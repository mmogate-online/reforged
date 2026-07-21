"""dc-restore extract_v31_spawns: v31 spawn + stat extraction and v17->v31 territory correlation.

Phase 2a of the Island of Dawn restoration. Read-only against the v31.04 server
datasheet; the only writes are the artifacts under
docs/plans/iod-alpha-content-loop/data/.

Three products, all scoped to the Island hunting zones (13, 64, 213, 313, 364, 436)
and filtered to the Phase 1 v17 roster (v17-npcs.json / v17-territories.json):

1. v31 spawn placement per HZ. Every TerritoryGroup/Territory (with its server
   ids and fence rings) and every <Npc> spawn entry (full attribute set: template,
   pos, count, respawn/delay, aggro). Spawn entries are kept only when their
   (hz, npcTemplateId) is in the v17 roster; v31-only templates are counted and
   listed, never silently dropped.

2. v31 NpcData stat block per v17-rostered (hz, templateId): the <Stat> attrs
   (maxHp, atk, def, level, exp, walk/run speed) plus the template flags
   (elite, size, race, aiid, ...), plus a presence map of the per-template and
   per-zone auxiliary files: NpcSkillData (skills keyed by templateId), AIData
   (Ai id referenced by the template's aiid), and the zone-level FormationData /
   ActiveMove / DynamicSpawn resources (present only for some zones).

3. Territory correlation. v17 client territories carry fence rings but no server
   id; v31 territories carry ids. Each v17 territory is matched to a v31 territory
   by fence-vertex geometry: exact rounded vertex-set match first, then a
   near-match by symmetric mean nearest-vertex distance, else unmatched. Unmatched
   territories on both sides are reported explicitly (the v17-only ones are the
   deleted-spawn losses; the v31-only ones are territories with no client polygon).

Geometry follows the prior art in spawn_restore.py (verts_of / centroid /
poly_mean_nn); the near-match threshold mirrors its MATCH_THRESHOLD.
"""

import json
import math
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from dclib import (
    Sources,
    find_zone_file,
    load_references,
    read_text,
    strip_ns,
)

# Force UTF-8 stdout on Windows (Korean/Cyrillic desc text).
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ISLAND_ZONES = [13, 64, 213, 313, 364, 436]

# Symmetric mean nearest-vertex distance below this = same polygon (fence drift).
# Above it = a distinct (deleted / added) territory. Mirrors spawn_restore.
NEAR_TOL = 400.0


# ---------------------------------------------------------------------------
# Geometry (2D fence-ring matching)
# ---------------------------------------------------------------------------

def verts_of(fences):
    """(x, y) vertex list from a list of 'x,y,z' Fence pos strings."""
    out = []
    for f in fences:
        parts = f.split(",")
        if len(parts) >= 2:
            try:
                out.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass
    return out


def centroid(verts):
    if not verts:
        return (0.0, 0.0)
    return (sum(x for x, _ in verts) / len(verts),
            sum(y for _, y in verts) / len(verts))


def mean_nn(a, b):
    """Mean nearest-neighbour vertex distance from polygon a to polygon b."""
    if not a or not b:
        return float("inf")
    tot = 0.0
    for xa, ya in a:
        tot += min(math.hypot(xa - xb, ya - yb) for xb, yb in b)
    return tot / len(a)


def sym_nn(a, b):
    """Symmetric (max-of-both-directions) mean nearest-vertex distance."""
    return max(mean_nn(a, b), mean_nn(b, a))


def vertex_key(verts):
    """Order-independent rounded (x, y) multiset key for exact matching.

    v17 fences carry 4 decimals, v31 carries 8; both round to the same integer
    grid, so an exact geometric match survives the precision difference.
    """
    return tuple(sorted((round(x), round(y)) for x, y in verts))


# ---------------------------------------------------------------------------
# v31 file parsing
# ---------------------------------------------------------------------------

def zone_file(v31_root, family, zone):
    """Case-insensitive per-zone file path (handles lowercase AiData_64)."""
    return find_zone_file(v31_root, family, zone)


def parse_territory(v31_root, zone):
    """Full TerritoryData for a zone: [ {group_id, group_desc, territories:[...]} ].

    Each territory: {id, desc, type, fences:[pos...], npcs:[attrib dict...]}.
    """
    p = zone_file(v31_root, "TerritoryData", zone)
    if p is None:
        return None
    root = ET.fromstring(read_text(p).encode("utf-8"))
    groups = []
    for g in root.iter():
        if strip_ns(g.tag) != "TerritoryGroup":
            continue
        terrs = []
        for t in g.iter():
            if strip_ns(t.tag) != "Territory":
                continue
            fences, npcs = [], []
            for el in t.iter():
                tag = strip_ns(el.tag)
                if tag == "Fence":
                    fences.append(el.get("pos", ""))
                elif tag == "Npc":
                    npcs.append(dict(el.attrib))
            terrs.append({
                "id": t.get("id", ""),
                "desc": t.get("desc", ""),
                "type": t.get("type", ""),
                "fences": fences,
                "npcs": npcs,
            })
        groups.append({
            "group_id": g.get("id", ""),
            "group_desc": g.get("desc", ""),
            "territories": terrs,
        })
    return groups


def parse_npc_stats(v31_root, zone):
    """{templateId(int): {template attrs + stat dict}} for a zone NpcData file."""
    p = zone_file(v31_root, "NpcData", zone)
    if p is None:
        return None
    root = ET.fromstring(read_text(p).encode("utf-8"))
    out = {}
    for tmpl in root.iter():
        if strip_ns(tmpl.tag) != "Template":
            continue
        tid_raw = tmpl.get("id", "")
        if not tid_raw.isdigit():
            continue
        tid = int(tid_raw)
        stat = {}
        for el in tmpl.iter():
            if strip_ns(el.tag) == "Stat":
                stat = dict(el.attrib)
                break
        out[tid] = {
            "id": tid,
            "name": tmpl.get("name", ""),
            "race": tmpl.get("race", ""),
            "gender": tmpl.get("gender", ""),
            "size": tmpl.get("size", ""),
            "scale": tmpl.get("scale", ""),
            "elite": tmpl.get("elite", ""),
            "isFreeNamed": tmpl.get("isFreeNamed", ""),
            "aiid": tmpl.get("aiid", ""),
            "resourceType": tmpl.get("resourceType", ""),
            "partyMember": tmpl.get("partyMember", ""),
            "playStyle": tmpl.get("playStyle", ""),
            "balanceType": tmpl.get("balanceType", ""),
            "stat": stat,
        }
    return out


def parse_skill_counts(v31_root, zone):
    """{templateId(int): skill entry count} from NpcSkillData (root <SkillData>)."""
    p = zone_file(v31_root, "NpcSkillData", zone)
    if p is None:
        return None
    root = ET.fromstring(read_text(p).encode("utf-8"))
    out = {}
    for sk in root.iter():
        if strip_ns(sk.tag) != "Skill":
            continue
        tid = sk.get("templateId", "")
        if tid.isdigit():
            out[int(tid)] = out.get(int(tid), 0) + 1
    return out


def parse_ai_ids(v31_root, zone):
    """Set of Ai id strings defined in AIData for a zone (case-insensitive file)."""
    p = zone_file(v31_root, "AIData", zone)
    if p is None:
        return None
    root = ET.fromstring(read_text(p).encode("utf-8"))
    ids = set()
    for ai in root.iter():
        if strip_ns(ai.tag) == "Ai":
            ids.add(ai.get("id", ""))
    return ids


def count_root_children(v31_root, family, zone, child_tag):
    """(present, entry_count) for a zone-level resource file, or (False, 0)."""
    p = zone_file(v31_root, family, zone)
    if p is None:
        return False, 0
    root = ET.fromstring(read_text(p).encode("utf-8"))
    n = sum(1 for el in root.iter() if strip_ns(el.tag) == child_tag)
    return True, n


# ---------------------------------------------------------------------------
# Extraction per zone
# ---------------------------------------------------------------------------

def extract_zone(v31_root, zone, roster_tids, v17_groups):
    """Return (spawns, stats, correlation) dicts for one hunting zone."""
    v31_groups = parse_territory(v31_root, zone)
    npc_stats = parse_npc_stats(v31_root, zone)
    skill_counts_raw = parse_skill_counts(v31_root, zone)
    skill_counts = skill_counts_raw or {}
    ai_ids_raw = parse_ai_ids(v31_root, zone)
    ai_ids = ai_ids_raw or set()
    form_present, form_n = count_root_children(v31_root, "FormationData", zone, "Formation")
    move_present, move_n = count_root_children(v31_root, "ActiveMove", zone, "ActiveMove")
    dyn_present, dyn_n = count_root_children(v31_root, "DynamicSpawn", zone, "DynamicSpawn")

    roster = set(roster_tids)

    # ---- 1. Spawn extraction (filter to roster) ----
    kept_groups = []
    n_kept = 0
    n_filtered = 0
    filtered_templates = {}  # tid -> count of dropped spawn entries
    for g in (v31_groups or []):
        out_terrs = []
        for t in g["territories"]:
            kept_npcs = []
            for npc in t["npcs"]:
                tid_raw = npc.get("npcTemplateId", "")
                tid = int(tid_raw) if tid_raw.isdigit() else None
                if tid in roster:
                    kept_npcs.append(npc)
                    n_kept += 1
                else:
                    n_filtered += 1
                    if tid is not None:
                        filtered_templates[tid] = filtered_templates.get(tid, 0) + 1
            out_terrs.append({
                "id": t["id"], "desc": t["desc"], "type": t["type"],
                "fences": t["fences"], "npcs": kept_npcs,
                "n_npcs_total": len(t["npcs"]), "n_npcs_kept": len(kept_npcs),
            })
        kept_groups.append({
            "group_id": g["group_id"], "group_desc": g["group_desc"],
            "territories": out_terrs,
        })

    spawns = {
        "hz": zone,
        "territory_data_present": v31_groups is not None,
        "n_groups": len(kept_groups),
        "n_territories": sum(len(g["territories"]) for g in kept_groups),
        "n_spawn_entries_kept": n_kept,
        "n_spawn_entries_filtered": n_filtered,
        "filtered_templates": [
            {"npcTemplateId": tid, "spawn_entries": c}
            for tid, c in sorted(filtered_templates.items())
        ],
        "groups": kept_groups,
    }

    # ---- 2. Stats extraction for roster templates ----
    stat_rows = []
    missing_stats = []
    for tid in sorted(roster):
        row = (npc_stats or {}).get(tid)
        present = row is not None
        if not present:
            missing_stats.append(tid)
        aiid = row["aiid"] if present else ""
        stat_rows.append({
            "hz": zone,
            "npcTemplateId": tid,
            "npc_data_present": present,
            "name": row["name"] if present else "",
            "race": row["race"] if present else "",
            "size": row["size"] if present else "",
            "scale": row["scale"] if present else "",
            "elite": row["elite"] if present else "",
            "isFreeNamed": row["isFreeNamed"] if present else "",
            "aiid": aiid,
            "stat": row["stat"] if present else {},
            "presence": {
                "npc_skill_count": skill_counts.get(tid, 0),
                "ai_present": (aiid in ai_ids) if aiid else False,
                "ai_id": aiid,
            },
        })

    stats = {
        "hz": zone,
        "npc_data_present": npc_stats is not None,
        "roster_size": len(roster),
        "n_with_stats": len(roster) - len(missing_stats),
        "missing_stats": missing_stats,
        "zone_resources": {
            "npc_skill_data_present": skill_counts_raw is not None,
            "ai_data_present": ai_ids_raw is not None,
            "formation_data": {"present": form_present, "entries": form_n},
            "active_move": {"present": move_present, "entries": move_n},
            "dynamic_spawn": {"present": dyn_present, "entries": dyn_n},
        },
        "templates": stat_rows,
    }

    # ---- 3. Territory correlation ----
    corr = correlate_territories(zone, v17_groups, v31_groups or [])

    return spawns, stats, corr


def correlate_territories(zone, v17_groups, v31_groups):
    """Match every v17 territory fence ring to a v31 territory by geometry.

    A strict 1:1 assignment so no v31 territory is claimed by more than one v17
    territory (an earlier best-effort variant produced cross-group collisions
    where one v31 polygon absorbed up to five v17 polygons, hiding real losses):

      1. Exact pass: identical rounded vertex-set. When several v31 territories
         share the polygon, the same-group one is preferred.
      2. Same-group near pass: leftover v17 and v31 territories that share a group
         id, greedily paired by ascending symmetric mean nearest-vertex distance
         (<= NEAR_TOL), each v31 claimed once.
      3. Cross-group near pass: any remaining leftovers zone-wide, same greedy
         rule, scope recorded as "hz" so a cross-group match is visible.

    Whatever is still unpaired is a genuine loss (unmatched v17) or a v31-only /
    re-fenced territory (unmatched v31). v17 and v31 share group ids in this
    dataset, so a same-group match is the high-confidence signal.
    """
    # Flatten both sides with precomputed verts and an exact-match key.
    def flatten_v31():
        recs = []
        for g in v31_groups:
            for t in g["territories"]:
                v = verts_of(t["fences"])
                recs.append({"group_id": g["group_id"], "id": t["id"],
                             "desc": t["desc"], "verts": v, "key": vertex_key(v)})
        return recs

    v31_recs = flatten_v31()
    v17_recs = []
    for g in v17_groups:
        for terr in g["territories"]:
            v = verts_of(terr["fence"])
            v17_recs.append({"group_id": g["id"], "group_desc": g["desc"],
                             "index": terr["index"], "vertex_count": terr["vertex_count"],
                             "verts": v, "key": vertex_key(v)})

    # result[id(v17_rec)] = (v31_rec, dist, quality, scope)
    result = {}
    claimed = set()  # (group_id, id) of v31 territories already taken

    # ---- 1. Exact pass ----
    v31_by_key = {}
    for c in v31_recs:
        v31_by_key.setdefault(c["key"], []).append(c)
    for a in v17_recs:
        cands = [c for c in v31_by_key.get(a["key"], [])
                 if (c["group_id"], c["id"]) not in claimed]
        if not cands:
            continue
        same = [c for c in cands if c["group_id"] == a["group_id"]]
        pick = same[0] if same else cands[0]
        claimed.add((pick["group_id"], pick["id"]))
        scope = "group" if pick["group_id"] == a["group_id"] else "hz"
        result[id(a)] = (pick, 0.0, "exact", scope)

    # ---- greedy near helper: pair leftovers by ascending distance, 1:1 ----
    def greedy_near(pairs_scope):
        leftover_v17 = [a for a in v17_recs if id(a) not in result]
        leftover_v31 = [c for c in v31_recs if (c["group_id"], c["id"]) not in claimed]
        if not leftover_v17 or not leftover_v31:
            return
        cand = []
        for a in leftover_v17:
            same_group = pairs_scope == "group"
            for c in leftover_v31:
                if same_group and c["group_id"] != a["group_id"]:
                    continue
                d = sym_nn(a["verts"], c["verts"])
                if d <= NEAR_TOL:
                    cand.append((d, id(a), a, c))
        cand.sort(key=lambda x: x[0])
        for d, aid, a, c in cand:
            if aid in result:
                continue
            key = (c["group_id"], c["id"])
            if key in claimed:
                continue
            claimed.add(key)
            result[aid] = (c, d, "near", pairs_scope)

    greedy_near("group")  # ---- 2. Same-group near pass ----
    greedy_near("hz")     # ---- 3. Cross-group near pass ----

    # ---- Build rows ----
    rows = []
    for a in v17_recs:
        m = result.get(id(a))
        if m is None:
            rows.append({
                "hz": zone, "v17_group_id": a["group_id"],
                "v17_group_desc": a["group_desc"], "v17_territory_index": a["index"],
                "v17_vertex_count": a["vertex_count"], "match_quality": "unmatched",
                "match_scope": None, "v31_group_id": None, "v31_territory_id": None,
                "v31_territory_desc": "", "mean_nn_dist": None,
            })
        else:
            c, d, quality, scope = m
            rows.append({
                "hz": zone, "v17_group_id": a["group_id"],
                "v17_group_desc": a["group_desc"], "v17_territory_index": a["index"],
                "v17_vertex_count": a["vertex_count"], "match_quality": quality,
                "match_scope": scope, "v31_group_id": c["group_id"],
                "v31_territory_id": c["id"], "v31_territory_desc": c["desc"],
                "mean_nn_dist": round(d, 1),
            })

    v31_unmatched = [
        {"v31_group_id": c["group_id"], "v31_territory_id": c["id"],
         "v31_territory_desc": c["desc"], "vertex_count": len(c["verts"])}
        for c in v31_recs if (c["group_id"], c["id"]) not in claimed
    ]

    exact = sum(1 for r in rows if r["match_quality"] == "exact")
    near = sum(1 for r in rows if r["match_quality"] == "near")
    near_hz = sum(1 for r in rows if r["match_quality"] == "near" and r["match_scope"] == "hz")
    unm = sum(1 for r in rows if r["match_quality"] == "unmatched")

    return {
        "hz": zone,
        "v17_territory_count": len(rows),
        "v31_territory_count": len(v31_recs),
        "exact": exact, "near": near, "near_cross_group": near_hz,
        "unmatched_v17": unm,
        "unmatched_v31_count": len(v31_unmatched),
        "rows": rows,
        "unmatched_v31": v31_unmatched,
    }


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_spawns_md(all_spawns):
    L = ["# v31 Island Spawn Placement (filtered to v17 roster)", ""]
    L.append("Source: v31.04 server TerritoryData per hunting zone. Spawn entries are "
             "kept only when their (hz, npcTemplateId) is in the Phase 1 v17 roster; "
             "v31-only templates are reported per zone rather than dropped silently.")
    L.append("")
    L.append("| HZ | Groups | Territories | Spawns kept | Spawns filtered | v31-only templates |")
    L.append("|----|--------|-------------|-------------|-----------------|--------------------|")
    for s in all_spawns:
        L.append(f"| {s['hz']} | {s['n_groups']} | {s['n_territories']} | "
                 f"{s['n_spawn_entries_kept']} | {s['n_spawn_entries_filtered']} | "
                 f"{len(s['filtered_templates'])} |")
    L.append("")
    for s in all_spawns:
        L.append(f"## HZ {s['hz']}")
        L.append("")
        if not s["territory_data_present"]:
            L.append("- TerritoryData file absent in v31.")
            L.append("")
            continue
        L.append(f"- {s['n_groups']} groups, {s['n_territories']} territories, "
                 f"{s['n_spawn_entries_kept']} roster spawn entries kept, "
                 f"{s['n_spawn_entries_filtered']} filtered.")
        if s["filtered_templates"]:
            ft = ", ".join(f"{f['npcTemplateId']}(x{f['spawn_entries']})"
                           for f in s["filtered_templates"])
            L.append(f"- v31-only templates dropped (not in v17 roster): {ft}")
        L.append("")
        L.append("| Group | Desc | Territory | Terr desc | Spawns (kept/total) | Roster templates spawned |")
        L.append("|-------|------|-----------|-----------|---------------------|--------------------------|")
        for g in s["groups"]:
            for t in g["territories"]:
                tids = ",".join(sorted({n.get("npcTemplateId", "") for n in t["npcs"]}))
                L.append(f"| {g['group_id']} | {g['group_desc']} | {t['id']} | "
                         f"{t['desc']} | {t['n_npcs_kept']}/{t['n_npcs_total']} | {tids} |")
        L.append("")
    return "\n".join(L) + "\n"


def render_stats_md(all_stats):
    L = ["# v31 NpcData Stat Blocks (v17-rostered templates)", ""]
    L.append("Source: v31.04 server NpcData per hunting zone. One row per v17-rostered "
             "(hz, templateId). Presence columns: skills = NpcSkillData entry count "
             "(templateId-keyed), ai = whether the template's aiid resolves to an AIData "
             "Ai entry. FormationData / ActiveMove / DynamicSpawn are zone-level "
             "resources (not template-keyed); their presence and entry counts are "
             "reported per zone below.")
    L.append("")
    L.append("| HZ | Roster | With stats | Missing stats | Formation | ActiveMove | DynamicSpawn |")
    L.append("|----|--------|------------|---------------|-----------|------------|--------------|")
    for s in all_stats:
        zr = s["zone_resources"]
        def rc(d):
            return f"{d['entries']}" if d["present"] else "-"
        L.append(f"| {s['hz']} | {s['roster_size']} | {s['n_with_stats']} | "
                 f"{len(s['missing_stats'])} | {rc(zr['formation_data'])} | "
                 f"{rc(zr['active_move'])} | {rc(zr['dynamic_spawn'])} |")
    L.append("")
    for s in all_stats:
        L.append(f"## HZ {s['hz']}")
        L.append("")
        if s["missing_stats"]:
            L.append(f"- Roster templates with NO v31 NpcData stat block: {s['missing_stats']}")
            L.append("")
        L.append("| Template | Name | Lvl | maxHp | atk | def | exp | elite | size | aiid | ai? | skills |")
        L.append("|----------|------|-----|-------|-----|-----|-----|-------|------|------|-----|--------|")
        for r in s["templates"]:
            if not r["npc_data_present"]:
                L.append(f"| {r['npcTemplateId']} | (missing) | - | - | - | - | - | - | - | - | - | - |")
                continue
            st = r["stat"]
            p = r["presence"]
            L.append(f"| {r['npcTemplateId']} | {r['name']} | {st.get('level','')} | "
                     f"{st.get('maxHp','')} | {st.get('atk','')} | {st.get('def','')} | "
                     f"{st.get('exp','')} | {r['elite']} | {r['size']} | {r['aiid']} | "
                     f"{'Y' if p['ai_present'] else 'n'} | {p['npc_skill_count']} |")
        L.append("")
    return "\n".join(L) + "\n"


def render_correlation_md(all_corr):
    L = ["# v17 -> v31 Territory Correlation", ""]
    L.append("Each v17 client territory (fence ring, no server id) is matched 1:1 to a "
             "v31 server territory by fence-vertex geometry: exact rounded vertex-set "
             "match first, then a near-match by symmetric mean nearest-vertex distance "
             f"(<= {int(NEAR_TOL)}), each v31 territory claimed at most once.")
    L.append("")
    L.append("**Read the scope column.** v17 and v31 share group ids in this dataset, so "
             "a same-group match (scope `group`: all exacts plus near-group) is an "
             "identity correspondence and is high confidence. A cross-group near match "
             "(scope `hz`) is a spatial coincidence: the v17 territory sits within the "
             "tolerance of a surviving v31 territory that belongs to a *different* group, "
             "so it is NOT the same territory. Cross-group near matches come almost "
             "entirely from the v17-only (deleted) mob-camp groups and should be read as "
             "losses that happen to overlap a surviving neighbour, not restorable "
             "correspondences. The `Near (cross-group)` column isolates them.")
    L.append("")
    L.append("| HZ | v17 terr | v31 terr | Exact | Near | Near (cross-group) | Unmatched v17 | Unmatched v31 |")
    L.append("|----|----------|----------|-------|------|--------------------|---------------|---------------|")
    for c in all_corr:
        L.append(f"| {c['hz']} | {c['v17_territory_count']} | {c['v31_territory_count']} | "
                 f"{c['exact']} | {c['near']} | {c['near_cross_group']} | "
                 f"{c['unmatched_v17']} | {c['unmatched_v31_count']} |")
    L.append("")
    for c in all_corr:
        L.append(f"## HZ {c['hz']}")
        L.append("")
        L.append(f"- exact {c['exact']}, near {c['near']} (of which {c['near_cross_group']} "
                 f"cross-group), unmatched v17 {c['unmatched_v17']}, "
                 f"unmatched v31 {c['unmatched_v31_count']}.")
        L.append("")
        L.append("| v17 group | v17 desc | v17 terr idx | Quality | Scope | v31 group | v31 terr id | Mean NN |")
        L.append("|-----------|----------|--------------|---------|-------|-----------|-------------|---------|")
        for r in c["rows"]:
            L.append(f"| {r['v17_group_id']} | {r['v17_group_desc']} | "
                     f"{r['v17_territory_index']} | {r['match_quality']} | "
                     f"{r['match_scope'] or '-'} | {r['v31_group_id'] or '-'} | "
                     f"{r['v31_territory_id'] or '-'} | "
                     f"{r['mean_nn_dist'] if r['mean_nn_dist'] is not None else '-'} |")
        L.append("")
        if c["unmatched_v31"]:
            L.append("### v31 territories with no v17 match")
            L.append("")
            L.append("| v31 group | v31 terr id | Desc | Vertices |")
            L.append("|-----------|-------------|------|----------|")
            for u in c["unmatched_v31"]:
                L.append(f"| {u['v31_group_id']} | {u['v31_territory_id']} | "
                         f"{u['v31_territory_desc']} | {u['vertex_count']} |")
            L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    refs = load_references()
    sources = Sources(refs)
    v31_root = sources.v31
    if not v31_root.exists():
        print(f"ERROR: v31 datasheet not found: {v31_root} (network drive unmounted?)")
        return 1

    data_dir = Path(__file__).resolve().parents[2] / "docs" / "plans" / \
        "iod-alpha-content-loop" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    npcs = json.loads((data_dir / "v17-npcs.json").read_text(encoding="utf-8"))["zones"]
    terr = json.loads((data_dir / "v17-territories.json").read_text(encoding="utf-8"))["zones"]

    all_spawns, all_stats, all_corr = [], [], []
    for zone in ISLAND_ZONES:
        zk = str(zone)
        roster_tids = sorted({n["templateId"] for n in npcs[zk]["npcs"]})
        v17_groups = terr[zk]["groups"]
        spawns, stats, corr = extract_zone(v31_root, zone, roster_tids, v17_groups)
        all_spawns.append(spawns)
        all_stats.append(stats)
        all_corr.append(corr)
        print(f"HZ {zone}: spawns kept {spawns['n_spawn_entries_kept']} / "
              f"filtered {spawns['n_spawn_entries_filtered']}; "
              f"stats {stats['n_with_stats']}/{stats['roster_size']} "
              f"(missing {len(stats['missing_stats'])}); "
              f"corr exact {corr['exact']} near {corr['near']} "
              f"unm-v17 {corr['unmatched_v17']} unm-v31 {corr['unmatched_v31_count']}")

    # Write JSON + MD artifacts.
    (data_dir / "v31-spawns.json").write_text(
        json.dumps({"zones": all_spawns}, indent=2, ensure_ascii=False), encoding="utf-8")
    (data_dir / "v31-npc-stats.json").write_text(
        json.dumps({"zones": all_stats}, indent=2, ensure_ascii=False), encoding="utf-8")
    (data_dir / "territory-correlation.json").write_text(
        json.dumps({"zones": all_corr}, indent=2, ensure_ascii=False), encoding="utf-8")

    (data_dir / "v31-spawns.md").write_text(render_spawns_md(all_spawns), encoding="utf-8")
    (data_dir / "v31-npc-stats.md").write_text(render_stats_md(all_stats), encoding="utf-8")
    (data_dir / "territory-correlation.md").write_text(
        render_correlation_md(all_corr), encoding="utf-8")

    print(f"\nArtifacts written to {data_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
