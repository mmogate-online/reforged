"""dc-restore spawn_restore: reconstruct deleted TerritoryData spawns.

Island-of-Dawn spawn losses predate v31, so "restore from v31" does not apply
here (v31 and v92 hold the same reduced spawn set). The old client DataCenter
TerritoryData shards are the only surviving record of the full spawn topology.
This module diffs the client shard against the v92 server TerritoryData and
produces a reviewable reconstruction plan:

  ZONE 13  -- 17 whole TerritoryGroups exist only in the client (the ruins /
    late-forest mob camps that feed the kill-quests). Each is rebuilt: group +
    territories (client fence polygons copied verbatim) + area-mob <Npc> entries
    whose npcTemplateId is resolved from the Korean group desc and whose combat
    attrs are cloned from a real same-zone v92 donor spawn.

  ZONE 213 -- no client-only groups; the deletion is at territory level inside
    the shared southern group 21300003 (client 9 territories vs v92 6). Deleted
    territories are found by fence-polygon similarity. The best recovered polygon
    beside the ruins is authored as Leander's Outpost, and the unspawned quest
    villagers (fixed idiom) are placed at their authentic camps. Eria (1021) is
    relocated from the vanguard camp to the outpost.

The two spawn idioms mirrored here (verified against the v92 files):
  area mob   -- randomPos="true" pos="0,0,0" spawnCount=N inside a fence
  villager   -- randomPos="false" explicit pos + dir, spawnCount=1

Template resolution is a curated table (authoritative, cross-checked against the
ruins-archaeology kill-target findings), never a blind guess; every group carries
a confidence tag and the exclusion rules (drop 페어런츠용 parent stubs and 환경
ambient templates unless the desc says 환경).

Read-only by default: writes only the plan markdown + JSON. An --apply path is
implemented (insert blocks, re-validate, write) but this shipment is plan-only.
"""

import argparse
import json
import math
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from dclib import (
    Sources,
    TextFile,
    find_zone_file,
    load_references,
    npc_template_ids,
    read_text,
    strip_ns,
    validate_xml,
)

# ---------------------------------------------------------------------------
# Client shard per zone (root huntingZoneId identifies the zone).
# ---------------------------------------------------------------------------
CLIENT_SHARD = {13: "TerritoryData-00005.xml", 213: "TerritoryData-00025.xml"}

# Id-numbering ceilings continue the zone's existing convention (verified from
# the v92 files): zone 13 steps territory/instance ids by 10; zone 213 by 1.
NUMBERING = {
    13:  {"territory": 13014250, "instance": 13472940, "step": 10},
    213: {"territory": 21300036, "instance": 21300069, "step": 1},
}

EXCLUDE_SUBSTR = ["페어런츠용"]      # parent-monster stubs (never world-spawned)
AMBIENT_PREFIX = "(환경몬스터)"       # ambient; include only when desc says 환경

# ---------------------------------------------------------------------------
# Curated zone-13 group -> template resolution (authoritative).
#
# Each entry: (templates, confidence, quests_fed, note). Cross-checked against
# the ruins-archaeology kill-target roster and the client kill tasks. quests_fed
# lists the kill-quests whose 몬스터Id targets this group supplies (empty = flavor
# or ambient, no kill task depends on it). Confidence: high / med.
# ---------------------------------------------------------------------------
GROUP_MOBS = {
    1300019: ([302, 303, 300941, 300944], "med", [1319],
              "mid-forest nature spirits; bare '자연의 정령' spans base 302/303 and "
              "Terron 300941/300944 (1319 targets 300941+300944)"),
    1300020: ([300930, 300931, 300932, 300933], "high", [1324],
              "Ghilliedhu family (1324 targets 300930+300933)"),
    1300021: ([300930, 300931, 300932, 300933], "med", [1324],
              "aggressive (선공) Ghilliedhu; same family, isAggressiveMonster set true"),
    1300022: ([302, 303, 300941, 300944], "med", [1319],
              "nature spirits near base; see 1300019"),
    1300025: ([304, 300920, 300921], "high", [1327, 1332],
              "Argas/Noruk near base (1327 targets 304, 1332 targets 300920)"),
    1300028: ([601], "high", [1307],
              "Dark Marauder near base (1307 targets 601)"),
    1300029: ([300942, 300943, 300945], "high", [1337],
              "corrupted Terron near base (1337 targets 300943+300945)"),
    1300030: ([2], "high", [],
              "polluted Earth Spirit (Black Rift side); 오염된 흙의 정령B = 2"),
    1300031: ([304, 300920, 300921], "high", [1327, 1332],
              "Argas/Noruk in ruins; see 1300025"),
    1300032: ([3], "high", [1308],
              "corrupted Earth Spirit 타락한 흙의 정령A=3 (1308 Ponderous Sporewalker)"),
    1300033: ([300541, 300542], "high", [1347],
              "Stone Crawler; 300540 parent excluded (1347 targets 300541+300542)"),
    1300034: ([300910, 300911], "high", [1333],
              "dying Cromos (1333 targets 300911)"),
    1300036: ([4, 5], "high", [1349],
              "Orcan minions outside camp: 미니 오칸=4, 오칸 습격자=5 (1349 targets 4x48,5x6)"),
    1300037: ([601], "high", [1307],
              "Dark Marauder inside camp; see 1300028"),
    1300038: ([901, 1002], "med", [],
              "Orcan patrol flavor (오칸 901/1002); not a kill-task target"),
    1300057: ([102], "high", [],
              "AMBIENT (환경) nature spirit; desc says 환경 so 환경몬스터 102 included"),
    1300058: ([301], "med", [],
              "AMBIENT Stonehead; sole 스톤헤드 template is 환경몬스터 301 (desc lacks 환경)"),
}

# Same-family donor: an npcTemplateId spawned in v92 zone 13 whose combat attrs
# are a sound clone source for a resolved template. Exact self-donor preferred;
# these fill in for templates absent from v92. A template with no listed donor
# falls back to a generic area-mob donor and is flagged in the uncertain list.
FAMILY_DONOR = {
    304: 300921, 300920: 300921, 300921: 300921,
    300910: 300910, 300911: 300910,
    300930: 300931, 300931: 300931, 300932: 300932, 300933: 300932,
    300941: 300942, 300942: 300942, 300943: 300942, 300944: 300942, 300945: 300942,
    302: 300942, 303: 300942,
    601: 300951, 300951: 300951, 300960: 300960,
    2: 2, 3: 2,
    4: 901, 5: 901, 901: 901, 902: 901, 1002: 901,
    102: 102, 301: 102, 1011: 1011,
    # Stone Crawler: no crawler spawned anywhere in v92 -> generic (flagged).
    300541: 300921, 300542: 300921,
}

# ---------------------------------------------------------------------------
# Zone-213 villager placements (fixed idiom). Curated from the ruins-archaeology
# roster + placement anchors. target_terr is the existing v92 Territory id to add
# the <Npc> to; OUTPOST means the newly recovered Leander's Outpost territory.
# Each: name, template, anchor (x,y), group, target_terr, rationale.
# ---------------------------------------------------------------------------
OUTPOST = "OUTPOST"
VILLAGERS = [
    ("Ayrdoss", 1126, (49912, -80844), "21300003", OUTPOST,
     "Leander's Outpost anchor NPC (breaks 1349); recovered polygon beside ruins"),
    ("Lorin", 1128, (49912, -80844), "21300003", OUTPOST,
     "Leander's Outpost (breaks 1347)"),
    ("Jehan", 1130, (49912, -80844), "21300003", OUTPOST,
     "Leander's Outpost (breaks 1310/1332/1333/1390)"),
    ("Kamarnu", 1009, (80900, -81300), "1300005", "1300467",
     "Kaimon's Camp (breaks 1305/1332); inside 카이몬의 야영지"),
    ("Riel", 1018, (69014, -79276), "1300005", "21300032",
     "Supply Base beside Leander 1008 (breaks 1311/1313); inside 보급기지_추가"),
    ("Kirash", 1027, (69014, -79276), "1300005", "21300032",
     "Supply Base (breaks 1307); inside 보급기지_추가"),
    ("Clovis", 1110, (74100, -82680), "1300005", "1300464",
     "Garrison North Camp (breaks 1319); inside 수비대 북부 캠프"),
    ("Milun", 1137, (65968, -70450), "1300005", "1300462",
     "Chione cluster (breaks 1338); inside 키오네 추락지점"),
]
# Eria relocation: move existing instance 21300069 to the outpost.
ERIA_INSTANCE = 21300069
ERIA_TEMPLATE = 1021
# NPCs deliberately NOT placed (cinematic / event; would clear a flag but must not).
NO_PLACE = {
    "213,1036": "Leander cinematic duplicate (1306 target)",
    "213,1020": "Priscus event guide (1389 giver/target)",
}

# Territory-match threshold: mean nearest-vertex distance below this = same
# polygon (fence drift). Above = a distinct (deleted) territory.
MATCH_THRESHOLD = 400.0


# ===========================================================================
# Geometry
# ===========================================================================

def verts_of(fences):
    """(x, y) vertex list from a list of 'x,y,z' Fence pos strings."""
    out = []
    for f in fences:
        parts = f.split(",")
        if len(parts) >= 2:
            out.append((float(parts[0]), float(parts[1])))
    return out


def centroid(verts):
    if not verts:
        return (0.0, 0.0)
    return (sum(x for x, _ in verts) / len(verts),
            sum(y for _, y in verts) / len(verts))


def mean_z(fences):
    zs = []
    for f in fences:
        parts = f.split(",")
        if len(parts) >= 3:
            try:
                zs.append(float(parts[2]))
            except ValueError:
                pass
    return sum(zs) / len(zs) if zs else 0.0


def poly_mean_nn(a, b):
    """Mean nearest-neighbour vertex distance from polygon a to polygon b."""
    if not a or not b:
        return float("inf")
    tot = 0.0
    for xa, ya in a:
        tot += min(math.hypot(xa - xb, ya - yb) for xb, yb in b)
    return tot / len(a)


def facing_dir(px, py, cx, cy):
    """Integer heading (degrees) from (px,py) toward (cx,cy), TERA convention."""
    return int(round(math.degrees(math.atan2(cy - py, cx - px))))


# ===========================================================================
# Territory readers
# ===========================================================================

class Territory:
    def __init__(self, tid, desc, fences):
        self.id = tid              # server id, or None for a client territory
        self.desc = desc
        self.fences = fences       # raw 'x,y,z' pos strings (verbatim)
        self.verts = verts_of(fences)

    def centroid(self):
        return centroid(self.verts)


def v92_territory_text(sources, zone):
    """v92 TerritoryData_<zone> read from the git HEAD baseline.

    The diff must be against the clean pre-apply baseline so the reconstruction is
    reproducible whether or not the working tree already holds applied spawns; the
    apply path then idempotently skips units already present in the working tree.
    Falls back to the working-tree file when the datasheet is not a dirty repo.
    """
    fname = find_zone_file(sources.v92, "TerritoryData", zone).name
    text = sources.baseline.read(fname, baseline=True)
    if text is None:  # not tracked / not in a repo: use the working tree
        text = read_text(find_zone_file(sources.v92, "TerritoryData", zone))
    return text


def _fences(terr_el):
    out = []
    for f in terr_el.iter():
        if strip_ns(f.tag) == "Fence":
            out.append(f.get("pos", ""))
    return out


def read_groups(text, client):
    """{gid: {'desc', 'territories': [Territory]}} for a TerritoryData document.

    client shards carry no Territory id; server territories do.
    """
    root = ET.fromstring(text.encode("utf-8"))
    out = {}
    for g in root.iter():
        if strip_ns(g.tag) != "TerritoryGroup":
            continue
        terrs = []
        for t in g.iter():
            if strip_ns(t.tag) != "Territory":
                continue
            terrs.append(Territory(None if client else t.get("id"),
                                   "" if client else t.get("desc", ""),
                                   _fences(t)))
        out[g.get("id")] = {"desc": g.get("desc", ""), "territories": terrs}
    return out


def npc_donors(text):
    """{npcTemplateId(int): ordered attr dict} of the first spawn per template."""
    root = ET.fromstring(text.encode("utf-8"))
    out = {}
    for npc in root.iter():
        if strip_ns(npc.tag) != "Npc":
            continue
        tid = npc.get("npcTemplateId", "")
        if tid.isdigit() and int(tid) not in out:
            out[int(tid)] = dict(npc.attrib)
    return out


# ===========================================================================
# Template resolution
# ===========================================================================

def resolve_group(gid, desc, tmap):
    """(templates, confidence, quests, note, unresolved_names).

    Uses the curated GROUP_MOBS table; every template is verified to exist in the
    zone NpcData map. Returns unresolved names honestly if a curated id is absent.
    """
    if gid not in GROUP_MOBS:
        return [], "none", [], f"no curated resolution for group {gid} ({desc})", [desc]
    templates, conf, quests, note = GROUP_MOBS[gid]
    present, missing = [], []
    for tid in templates:
        (present if tid in tmap else missing).append(tid)
    if missing:
        note += f"  [WARNING: {missing} absent from NpcData_{gid // 100000}]"
    return present, conf, quests, note, missing


# ===========================================================================
# Donor selection
# ===========================================================================

def pick_donor(tid, tname, donors):
    """(donor_attrs, source_note, exact) for a resolved template id.

    Prefer the template's own v92 spawn; else a curated same-family donor; else a
    generic area-mob donor (flagged not-exact).
    """
    if tid in donors:
        return donors[tid], f"self (tpl {tid} spawned in v92)", True
    fam = FAMILY_DONOR.get(tid)
    if fam and fam in donors:
        exact = fam in FAMILY_DONOR and FAMILY_DONOR.get(tid) == tid
        return donors[fam], f"same-family donor tpl {fam}", exact
    # Generic fallback: any randomPos=true area mob.
    for dtid, attrs in donors.items():
        if attrs.get("randomPos") == "true":
            return attrs, f"GENERIC area-mob donor tpl {dtid} (no same-family source)", False
    # Last resort: any donor.
    dtid, attrs = next(iter(donors.items()))
    return attrs, f"GENERIC donor tpl {dtid}", False


# ===========================================================================
# XML emission (server schema, tab-indented)
# ===========================================================================

# Attribute order for a fresh area-mob Npc, taken from a real v92 entry so the
# emitted element is byte-comparable to hand-authored spawns.
def _npc_element(indent, attrs):
    """Serialize one <Npc> (with default PatrolList/SocialSet) at tab depth."""
    a = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    return (f'{indent}<Npc {a}>\n'
            f'{indent}\t<PatrolList type="default" socialDuration="0" randomSocial="false" />\n'
            f'{indent}\t<SocialSet checkInterval="0" probSocial="0.000000" />\n'
            f'{indent}</Npc>')


def area_npc_attrs(donor, instance_id, tid, desc, spawn_count, aggressive):
    """Clone donor attrs into an area-mob spawn (randomPos true, pos 0,0,0)."""
    a = dict(donor)
    a["instanceId"] = str(instance_id)
    a["desc"] = desc
    a["npcTemplateId"] = str(tid)
    a["randomPos"] = "true"
    a["spawnCount"] = str(spawn_count)
    a["pos"] = "0.00000000,0.00000000,0.00000000"
    if aggressive:
        a["isAggressiveMonster"] = "true"
    return a


def villager_npc_attrs(donor, instance_id, tid, desc, pos, dir_deg):
    """Clone donor attrs into a fixed villager spawn (randomPos false)."""
    a = dict(donor)
    a["instanceId"] = str(instance_id)
    a["desc"] = desc
    a["npcTemplateId"] = str(tid)
    a["randomPos"] = "false"
    a["spawnCount"] = "1"
    a["pos"] = pos
    a["dir"] = str(dir_deg)
    return a


def territory_block(indent, tid, desc, fences, npc_attr_list):
    """Serialize one <Territory> with verbatim fences and the given npc entries."""
    L = [f'{indent}<Territory id="{tid}" desc="{desc}" type="normal" '
         'addMaxZ="256.000000" subtractMinZ="0.000000" randomPosMinDist="100.000000" '
         'peaceMoveNpcCheckDist="100.000000" eventId="0">']
    for f in fences:
        L.append(f'{indent}\t<Fence pos="{f}" />')
    for attrs in npc_attr_list:
        L.append(_npc_element(indent + "\t", attrs))
    L.append(f'{indent}\t<Attribute achieveConditionId="0" abnormality="0" />')
    L.append(f'{indent}</Territory>')
    return "\n".join(L)


def group_block(gid, desc, territory_blocks):
    """Serialize a whole <TerritoryGroup> with the standard AI trailer."""
    inner = "\n".join(territory_blocks)
    return (f'\t<TerritoryGroup id="{gid}" desc="{desc}">\n'
            f'\t\t<TerritoryList>\n{inner}\n\t\t</TerritoryList>\n'
            '\t\t<BerserkAi working="false" duration="0" berserkRate="0.000000" '
            'combatRatioDiffToBerserk="0.000000" />\n'
            '\t\t<BlastRegenAi working="false" checkType="time" intervalToBlastRegen="0" '
            'spawnedRatioToBlastRegen="0.000000" />\n'
            '\t\t<DoorAiList />\n'
            '\t\t<RespawnTimeAi working="false" combatRateToReduceRespawnTime="0.000000" '
            'respawnReduceTime="0.000000" duration="0" />\n'
            '\t\t<SpawnNewNpcAi working="false" npcDeadCount="0" duration="0" />\n'
            '\t</TerritoryGroup>')


# ===========================================================================
# Spawn-count sizing
# ===========================================================================

def size_group(templates, n_terr, kill_reqs, donors):
    """Assign templates to territories and size spawnCount per template.

    Returns {tid: (n_assigned_terr, per_terr_count, total_supply)} and a list of
    sizing notes. Base density is the donor's spawnCount; when a group feeds an
    explicit kill count and base supply is short of 1.5x, per-territory count is
    raised (capped at 12, flagged if still short).
    """
    CAP = 12
    plan = {}
    notes = []
    n_t = len(templates)
    if n_t == 0 or n_terr == 0:
        return plan, notes
    # Round-robin territory assignment.
    assigned = {t: 0 for t in templates}
    for i in range(n_terr):
        assigned[templates[i % n_t]] += 1
    for tid in templates:
        donor, _, _ = pick_donor(tid, "", donors)
        base = int(donor.get("spawnCount", "1")) if donor.get("spawnCount", "1").isdigit() else 1
        base = max(1, base)
        na = assigned[tid]
        per = base
        need = kill_reqs.get(tid)
        if need is not None:
            target = math.ceil(1.5 * need)
            if base * na < target:
                per = min(CAP, math.ceil(target / na)) if na else base
                if per * na < target:
                    notes.append(f"tpl {tid}: SHORT -- {per}x{na}={per*na} < 1.5x{need}"
                                 f"={target} (density-capped at {CAP}; supplement elsewhere)")
        plan[tid] = (na, per, per * na)
    return plan, notes


# ===========================================================================
# Zone-13 reconstruction
# ===========================================================================

def reconstruct_zone13(sources, tmap, donors, kill_by_template):
    client = read_groups(read_text(sources.old_client / "TerritoryData" / CLIENT_SHARD[13]), True)
    v92 = read_groups(v92_territory_text(sources, 13), False)
    client_only = sorted((set(client) - set(v92)), key=int)

    num = dict(NUMBERING[13])
    t_next = num["territory"] + num["step"]
    i_next = num["instance"] + num["step"]
    step = num["step"]

    groups = []
    for gid_s in client_only:
        gid = int(gid_s)
        cg = client[gid_s]
        desc = cg["desc"].strip()
        terrs = cg["territories"]
        templates, conf, quests, note, missing = resolve_group(gid, desc, tmap)
        aggressive = "선공" in desc
        kill_reqs = {t: kill_by_template[t] for t in templates if t in kill_by_template}
        sizing, size_notes = size_group(templates, len(terrs), kill_reqs, donors)

        # Assign templates round-robin, emit a territory block per client polygon.
        blocks = []
        rendered_terr = []
        npc_total = 0
        for idx, terr in enumerate(terrs):
            tid_num = t_next
            t_next += step
            tpl = templates[idx % len(templates)] if templates else None
            npc_attrs = []
            if tpl is not None:
                donor, dsrc, exact = pick_donor(tpl, "", donors)
                per = sizing.get(tpl, (0, 1, 0))[1]
                tname = tmap.get(tpl, str(tpl))
                attrs = area_npc_attrs(donor, i_next, tpl,
                                       f"{tname} (Client Only)", per, aggressive)
                i_next += step
                npc_attrs.append(attrs)
                npc_total += 1
            blocks.append(territory_block("\t\t\t\t", tid_num,
                          f"복원 테리토리({tid_num})", terr.fences, npc_attrs))
            cx, cy = terr.centroid()
            rendered_terr.append({"id": tid_num, "template": tpl,
                                  "centroid": [round(cx), round(cy)],
                                  "n_fences": len(terr.fences)})
        gc = centroid([v for terr in terrs for v in terr.verts])
        groups.append({
            "gid": gid, "desc": desc, "confidence": conf, "quests_fed": quests,
            "note": note, "missing_templates": missing, "aggressive": aggressive,
            "templates": templates,
            "template_names": {t: tmap.get(t, "?") for t in templates},
            "n_territories": len(terrs), "n_npc": npc_total,
            "group_centroid": [round(gc[0]), round(gc[1])],
            "sizing": {t: {"terr": v[0], "per_terr": v[1], "supply": v[2]}
                       for t, v in sizing.items()},
            "sizing_notes": size_notes,
            "donors": {t: pick_donor(t, "", donors)[1] for t in templates},
            "territories": rendered_terr,
            "xml": group_block(gid, desc, blocks),
        })
    return groups, client, v92


# ===========================================================================
# Zone-213 reconstruction (territory recovery + villagers + Eria)
# ===========================================================================

def match_territories(client_terrs, server_terrs):
    """For each client territory, (best server id, mean_nn, matched?)."""
    out = []
    for c in client_terrs:
        best, bd = None, float("inf")
        for s in server_terrs:
            d = poly_mean_nn(c.verts, s.verts)
            if d < bd:
                bd, best = d, s
        out.append((c, best, bd, bd <= MATCH_THRESHOLD))
    return out


def reconstruct_zone213(sources, donors_213):
    client = read_groups(read_text(sources.old_client / "TerritoryData" / CLIENT_SHARD[213]), True)
    v92 = read_groups(v92_territory_text(sources, 213), False)

    num = dict(NUMBERING[213])
    t_next = num["territory"] + num["step"]
    i_next = num["instance"] + num["step"]

    # Territory diff inside shared groups (report deleted client territories).
    territory_diffs = {}
    deleted = {}
    for gid in sorted(set(client) & set(v92), key=int):
        cterrs = client[gid]["territories"]
        vterrs = v92[gid]["territories"]
        if len(cterrs) == len(vterrs):
            continue
        rows = match_territories(cterrs, vterrs)
        unm = []
        for c, best, d, matched in rows:
            if not matched:
                cx, cy = c.centroid()
                unm.append({"centroid": [round(cx), round(cy)], "n_fences": len(c.fences),
                            "nearest": best.id if best else None,
                            "nearest_desc": best.desc if best else "",
                            "mean_nn": round(d), "fences": c.fences})
        # A client territory can only be a genuine deletion when the group lost
        # territories overall (v92 < client). Where v92 has as many or more, an
        # unmatched polygon is fence drift, not a deletion.
        is_deletion = len(vterrs) < len(cterrs)
        territory_diffs[gid] = {"client": len(cterrs), "v92": len(vterrs),
                                "unmatched": unm, "is_deletion_group": is_deletion,
                                "net_deleted": max(0, len(cterrs) - len(vterrs))}
        if unm and is_deletion:
            deleted[gid] = unm

    # Leander's Outpost: the unmatched polygon nearest the ruins centroid.
    RUINS = (50700, -78500)
    outpost = None
    if "21300003" in deleted:
        cand = min(deleted["21300003"],
                   key=lambda u: math.hypot(u["centroid"][0] - RUINS[0],
                                            u["centroid"][1] - RUINS[1]))
        outpost = cand
    outpost_terr_id = t_next
    t_next += num["step"]
    outpost_z = mean_z(outpost["fences"]) if outpost else -3500.0
    outpost_cx, outpost_cy = (outpost["centroid"] if outpost else [49912, -80844])

    # Villager placements.
    donor = donors_213  # a real fixed-villager attr dict
    placements = []
    offset_i = 0
    for name, tpl, (ax, ay), gid, target, why in VILLAGERS:
        # Small deterministic spread so co-located NPCs do not stack exactly.
        ox = (offset_i % 3) * 60 - 60
        oy = (offset_i // 3) * 60 - 30
        offset_i += 1
        if target == OUTPOST:
            px, py, pz = outpost_cx + ox, outpost_cy + oy, outpost_z
            cx, cy = outpost_cx, outpost_cy
            terr_id = outpost_terr_id
        else:
            px, py = ax + ox, ay + oy
            # z + facing centroid from the target territory's existing donor NPC.
            tv = _territory_by_id(v92, gid, target)
            pz = _territory_z(tv, donor)
            cx, cy = (tv.centroid() if tv else (ax, ay))
            terr_id = target
        pos = f"{px:.8f},{py:.8f},{pz:.8f}"
        dir_deg = facing_dir(px, py, cx, cy)
        attrs = villager_npc_attrs(donor, i_next, tpl, f"{name} (Client Only)", pos, dir_deg)
        placements.append({
            "name": name, "template": tpl, "instance": i_next, "group": gid,
            "target_terr_id": outpost_terr_id if target == OUTPOST else target,
            "is_outpost": target == OUTPOST,
            "territory": ("OUTPOST " + str(outpost_terr_id)) if target == OUTPOST else target,
            "pos": [round(px), round(py), round(pz)], "dir": dir_deg,
            "rationale": why, "npc_attrs": attrs,
            "xml": _npc_element("\t\t\t\t", attrs),  # server depth: Npc = 4 tabs
        })
        i_next += num["step"]

    # Eria relocation: replace instance 21300069 pos with an outpost pos.
    eria_px, eria_py = outpost_cx + 30, outpost_cy - 30
    eria = {
        "instance": ERIA_INSTANCE, "template": ERIA_TEMPLATE,
        "from_pos": [53330, -69640], "from_territory": "21300023 (Black Rift vanguard camp)",
        "to_pos": [round(eria_px), round(eria_py), round(outpost_z)],
        "to_territory": f"OUTPOST {outpost_terr_id} (Leander's Outpost)",
        "new_pos_attr": f"{eria_px:.8f},{eria_py:.8f},{outpost_z:.8f}",
    }

    # Outpost territory metadata (the full block is rendered in the plan from the
    # recovered fence plus the placements whose territory is this outpost).
    outpost_block = None
    if outpost:
        outpost_block = {"territory_id": outpost_terr_id,
                         "centroid": outpost["centroid"],
                         "fences": outpost["fences"], "z": round(outpost_z)}

    return {
        "client_groups": len(client), "v92_groups": len(v92),
        "territory_diffs": territory_diffs, "deleted": deleted,
        "outpost": outpost, "outpost_terr_id": outpost_terr_id,
        "placements": placements, "eria": eria, "outpost_block": outpost_block,
    }, client, v92


def _territory_by_id(groups, gid, tid):
    grp = groups.get(gid)
    if not grp:
        return None
    for t in grp["territories"]:
        if t.id == tid:
            return t
    return None


def _territory_z(terr, donor):
    if terr and terr.fences:
        return mean_z(terr.fences)
    return -3500.0


# ===========================================================================
# Closure against the audit flags
# ===========================================================================

def closure(audit_json, placements, eria):
    """Which GIVER_UNSPAWNED / TARGET_UNSPAWNED flags clear vs remain."""
    data = json.loads(Path(audit_json).read_text(encoding="utf-8"))
    placed = {f"213,{p['template']}" for p in placements}
    placed.add(f"213,{eria['template']}")  # Eria relocation keeps 1021 spawned
    clears, remains = [], []
    for r in data["rows"]:
        gid, title = r["gid"], r["title"]
        for flag in ("GIVER_UNSPAWNED", "TARGET_UNSPAWNED"):
            if flag not in r["flags"]:
                continue
            refs = []
            if flag == "GIVER_UNSPAWNED":
                g = r["detail"].get("giver", {})
                if g.get("ref"):
                    refs.append(g["ref"])
            else:
                refs = [t["ref"] for t in r["detail"].get("targets_unspawned", [])]
            for ref in refs:
                if ref in placed:
                    clears.append((gid, title, flag, ref, "placed"))
                elif ref in NO_PLACE:
                    remains.append((gid, title, flag, ref, "not placed: " + NO_PLACE[ref]))
                elif not ref.startswith("213,"):
                    remains.append((gid, title, flag, ref, "out of zone-13/213 scope"))
                else:
                    remains.append((gid, title, flag, ref, "not in placement roster"))
    return clears, remains


# ===========================================================================
# Plan rendering
# ===========================================================================

def render_plan(z13, z213, clears, remains, kill_by_template, tmap):
    L = []
    w = L.append
    w("# Island of Dawn -- Batch 3 Spawn Reconstruction Plan")
    w("")
    w(f"Generated {time.strftime('%Y-%m-%d %H:%M:%S')} by tools/dc-restore/spawn_restore.py")
    w("")
    w("DRY-RUN reconstruction plan. Nothing here is applied. The client "
      "DataCenter TerritoryData shards are the only surviving record of the "
      "pre-v31 Island spawn topology; this plan diffs them against the v92 server "
      "TerritoryData and proposes the server XML that `--apply` would insert.")
    w("")

    n_groups = len(z13["groups"])
    n_npc13 = sum(g["n_npc"] for g in z13["groups"])
    n_terr13 = sum(g["n_territories"] for g in z13["groups"])
    n_recovered = sum(len(v) for v in z213["deleted"].values())
    w("## Headline")
    w("")
    w(f"- Zone 13: **{n_groups} deleted mob groups** reconstructed, "
      f"**{n_terr13} territories**, **{n_npc13} area-mob Npc entries**.")
    w(f"- Zone 213: **{n_recovered} deleted territories** recovered inside shared "
      f"groups; **{len(z213['placements'])} villager Npc entries** placed + "
      f"**1 Eria relocation**.")
    w(f"- Audit spawn flags: **{len(clears)} clear**, **{len(remains)} remain**.")
    w("")

    # ---- Zone 13 group table ----
    w("## Zone 13 -- reconstructed mob groups")
    w("")
    w("Each group is a client-only TerritoryGroup (present in the 2011 client, "
      "absent from v92/v31). Templates are resolved from the Korean group desc via "
      "the curated table (parent 페어런츠용 stubs and 환경 ambient templates excluded "
      "unless the desc says 환경), cross-checked against the ruins-archaeology "
      "kill-target roster. Fences are copied verbatim from the client polygons.")
    w("")
    w("| Group | Desc | Templates (resolved) | Conf | Territories | Npc | Feeds quests | Group centroid |")
    w("|-------|------|----------------------|------|-------------|-----|--------------|----------------|")
    for g in z13["groups"]:
        tstr = ", ".join(f"{t}={g['template_names'][t]}" for t in g["templates"])
        qstr = ", ".join(map(str, g["quests_fed"])) or "-"
        w(f"| {g['gid']} | {g['desc']} | {tstr} | {g['confidence']} | "
          f"{g['n_territories']} | {g['n_npc']} | {qstr} | "
          f"{g['group_centroid'][0]},{g['group_centroid'][1]} |")
    w("")

    # ---- spawnCount sizing ----
    w("### Spawn-count sizing (quest-critical mobs)")
    w("")
    w("Base density = the donor spawn's spawnCount (one Npc per client fence "
      "polygon). Where a group feeds an explicit kill count, per-territory count "
      "is raised toward 1.5x that requirement (capped at 12/territory).")
    w("")
    w("| Group | Template | Name | Terr assigned | Per-terr count | Total supply | Quest need (1.5x) |")
    w("|-------|----------|------|---------------|----------------|--------------|-------------------|")
    for g in z13["groups"]:
        for t in g["templates"]:
            s = g["sizing"].get(t)
            if not s:
                continue
            need = kill_by_template.get(t)
            needstr = f"{math.ceil(1.5*need)} (kill {need})" if need is not None else "-"
            w(f"| {g['gid']} | {t} | {g['template_names'][t]} | {s['terr']} | "
              f"{s['per_terr']} | {s['supply']} | {needstr} |")
    w("")
    short = [(g["gid"], n) for g in z13["groups"] for n in g["sizing_notes"]]
    if short:
        w("Sizing warnings:")
        for gid, n in short:
            w(f"- group {gid}: {n}")
        w("")

    # ---- donors ----
    w("### Donor spawns cloned (zone 13)")
    w("")
    w("| Group | Template | Donor source |")
    w("|-------|----------|--------------|")
    for g in z13["groups"]:
        for t in g["templates"]:
            w(f"| {g['gid']} | {t} | {g['donors'][t]} |")
    w("")

    # ---- Zone 213 territory recovery ----
    w("## Zone 213 -- recovered territories (deleted inside shared groups)")
    w("")
    w("No client-only groups exist in zone 213; deleted southern villager "
      "territories hide inside shared groups, found by fence-polygon similarity "
      f"(mean nearest-vertex distance > {int(MATCH_THRESHOLD)} = distinct/deleted).")
    w("")
    for gid, diff in z213["territory_diffs"].items():
        w(f"### Group {gid}: client {diff['client']} territories vs v92 {diff['v92']}")
        if not diff["is_deletion_group"]:
            w(f"- v92 has as many or more territories (net {diff['net_deleted']} lost); "
              f"{len(diff['unmatched'])} unmatched client polygon(s) are fence drift, "
              "not deletions -- nothing authored here.")
            w("")
            continue
        w(f"- net {diff['net_deleted']} territories deleted; "
          f"{len(diff['unmatched'])} client polygons have no close v92 counterpart:")
        w("")
        w("| Client centroid | Fences | Nearest v92 | Nearest desc | Mean NN dist | Verdict |")
        w("|-----------------|--------|-------------|--------------|--------------|---------|")
        for u in diff["unmatched"]:
            verdict = "DELETED" if u["mean_nn"] > 2000 else "deleted/heavily-drifted"
            w(f"| {u['centroid'][0]},{u['centroid'][1]} | {u['n_fences']} | "
              f"{u['nearest']} | {u['nearest_desc']} | {u['mean_nn']} | {verdict} |")
        w("")

    if z213["outpost"]:
        o = z213["outpost"]
        w(f"**Leander's Outpost** authored from the recovered polygon nearest the "
          f"ruins: centroid {o['centroid'][0]},{o['centroid'][1]}, new Territory id "
          f"{z213['outpost_terr_id']} in group 21300003.")
        w("")

    # ---- villager placement table ----
    if z213["placements"]:
        w("## Zone 213 -- villager placements (fixed idiom)")
        w("")
        w("| NPC | Template | Pos (x,y,z) | Dir | Group / Territory | Anchor rationale |")
        w("|-----|----------|-------------|-----|-------------------|------------------|")
        for p in z213["placements"]:
            px, py, pz = p["pos"]
            w(f"| {p['name']} | 213,{p['template']} | {px},{py},{pz} | {p['dir']} | "
              f"{p['group']} / {p['territory']} | {p['rationale']} |")
        e = z213["eria"]
        w(f"| Eria (RELOCATE) | 213,{e['template']} | {e['to_pos'][0]},{e['to_pos'][1]},"
          f"{e['to_pos'][2]} | - | {e['to_territory']} | from {e['from_pos'][0]},"
          f"{e['from_pos'][1]} ({e['from_territory']}) |")
        w("")

        w("### Eria relocation detail")
        w("")
        w(f"- Instance `{e['instance']}` (template {e['template']}) currently at "
          f"{e['from_pos'][0]},{e['from_pos'][1]} in {e['from_territory']}.")
        w(f"- `--apply` replaces its `pos` attribute with `{e['new_pos_attr']}` (inside "
          f"{e['to_territory']}). Fixed NPCs use randomPos=\"false\", so pos is "
          "authoritative; no fence move is required.")
        w("")

    # ---- closure ----
    w("## Audit closure (GIVER_UNSPAWNED / TARGET_UNSPAWNED)")
    w("")
    w("Zone-13 group restoration supplies kill-target mobs (`몬스터Id`), which the "
      "audit does NOT spawn-check, so it clears the ruins-archaeology kill-target "
      "gap, not audit flags. The audit's spawn flags are all hz-213 villager NPCs; "
      "these clear only via the villager placements below.")
    w("")
    w("### Flags that CLEAR")
    w("")
    if clears:
        w("| Quest | Title | Flag | Ref | How |")
        w("|-------|-------|------|-----|-----|")
        for gid, title, flag, ref, how in clears:
            w(f"| {gid} | {title} | {flag} | {ref} | {how} |")
    else:
        w("- (none)")
    w("")
    w("### Flags that REMAIN")
    w("")
    if remains:
        w("| Quest | Title | Flag | Ref | Why |")
        w("|-------|-------|------|-----|-----|")
        for gid, title, flag, ref, why in remains:
            w(f"| {gid} | {title} | {flag} | {ref} | {why} |")
    else:
        w("- (none)")
    w("")

    # ---- kill-target closure (ruins-archaeology, not audit) ----
    w("### Kill-target availability restored (ruins-archaeology gap, not audit flags)")
    w("")
    fed = {}
    for g in z13["groups"]:
        for q in g["quests_fed"]:
            fed.setdefault(q, set()).update(g["templates"])
    if fed:
        w("| Quest | Kill-target templates now spawned |")
        w("|-------|-----------------------------------|")
        for q in sorted(fed):
            w(f"| {q} | {', '.join(map(str, sorted(fed[q])))} |")
    w("")

    # ---- unresolved / uncertain ----
    w("## Unresolved / uncertain")
    w("")
    uncertain = []
    for g in z13["groups"]:
        if g["confidence"] != "high":
            uncertain.append(f"group {g['gid']} ({g['desc']}): confidence "
                             f"{g['confidence']} -- {g['note']}")
        if g["missing_templates"]:
            uncertain.append(f"group {g['gid']}: templates {g['missing_templates']} "
                             "absent from NpcData (dropped from plan)")
        for t in g["templates"]:
            if "GENERIC" in g["donors"][t]:
                uncertain.append(f"group {g['gid']} tpl {t} ({g['template_names'][t]}): "
                                 f"{g['donors'][t]} -- verify ai/combat attrs vs NpcData")
    if uncertain:
        for u in uncertain:
            w(f"- {u}")
    else:
        w("- (none)")
    w("")
    w("NPCs deliberately NOT placed (would clear a flag but must not):")
    for ref, why in NO_PLACE.items():
        w(f"- {ref}: {why}")
    w("")

    # ---- full XML appendix ----
    w("## Appendix: full proposed XML (`--apply` insert payload)")
    w("")
    w("### Zone 213: Leander's Outpost territory + villagers + relocated Eria")
    w("")
    if z213["outpost"]:
        w("```xml")
        w("<!-- insert into TerritoryData_213.xml, group 21300003 TerritoryList -->")
        w(build_outpost_territory(z213))
        w("```")
        w("")
    w("Villagers placed into existing territories (one `<Npc>` appended per target):")
    w("")
    w("```xml")
    for p in z213["placements"]:
        if "OUTPOST" in p["territory"]:
            continue
        w(f"<!-- into TerritoryData_213.xml group {p['group']} territory {p['territory']} -->")
        w(p["xml"])
    w("```")
    w("")
    w("### Zone 13: reconstructed groups")
    w("")
    w("Full per-group XML for all reconstructed groups follows (insert each before "
      "the closing `</TerritoryData>` of TerritoryData_13.xml).")
    w("")
    for g in z13["groups"]:
        w(f"#### Group {g['gid']} -- {g['desc']}")
        w("")
        w("```xml")
        w(g["xml"])
        w("```")
        w("")
    return "\n".join(L) + "\n"


# ===========================================================================
# --apply: format-preserving insertion, idempotent, with loud verification
# ===========================================================================

def _group_span(text, gid):
    """(start, end) of <TerritoryGroup id="gid"> .. </TerritoryGroup>, or None.

    The closing quote already delimits the id (no \\b, which would fail between the
    quote and a following space, both non-word chars).
    """
    m = re.search(r'<TerritoryGroup id="' + re.escape(str(gid)) + r'".*?</TerritoryGroup>',
                  text, re.S)
    return (m.start(), m.end()) if m else None


def _territory_span(text, tid):
    """(start, end) of <Territory id="tid" ..> .. </Territory>, or None."""
    m = re.search(r'<Territory id="' + re.escape(str(tid)) + r'".*?</Territory>',
                  text, re.S)
    return (m.start(), m.end()) if m else None


def _has_attr(text, attr, value):
    """True if attr="value" appears (exact attr name, avoids id/instanceId overlap)."""
    return re.search(r'\b' + re.escape(attr) + r'="' + re.escape(str(value)) + r'"', text) is not None


def _eria_pos(text, instance):
    m = re.search(r'<Npc instanceId="' + str(instance) + r'"[^>]*?\bpos="([^"]*)"', text)
    return m.group(1) if m else None


def insert_territory_in_group(text, gid, territory_block):
    """Insert territory_block before the group's </TerritoryList>."""
    span = _group_span(text, gid)
    if not span:
        raise ValueError(f"group {gid} not found in file")
    gs, ge = span
    block = text[gs:ge]
    m = re.search(r'[ \t]*</TerritoryList>', block)
    if not m:
        raise ValueError(f"group {gid} has no </TerritoryList>")
    at = gs + m.start()
    return text[:at] + territory_block + "\n" + text[at:]


def insert_npc_in_territory(text, tid, npc_block):
    """Insert npc_block before the territory's <Attribute ..> line."""
    span = _territory_span(text, tid)
    if not span:
        raise ValueError(f"territory {tid} not found in file")
    ts, te = span
    block = text[ts:te]
    m = re.search(r'[ \t]*<Attribute\b', block)
    if not m:
        raise ValueError(f"territory {tid} has no <Attribute>")
    at = ts + m.start()
    return text[:at] + npc_block + "\n" + text[at:]


def build_outpost_territory(z213):
    """Full <Territory> block for Leander's Outpost (fences + outpost villagers)."""
    ob = z213["outpost_block"]
    tid = ob["territory_id"]
    L = [f'\t\t\t<Territory id="{tid}" desc="레안더의 전초기지 (Leander\'s Outpost)" '
         'type="normal" addMaxZ="256.000000" subtractMinZ="0.000000" '
         'randomPosMinDist="100.000000" peaceMoveNpcCheckDist="100.000000" eventId="0">']
    for f in ob["fences"]:
        L.append(f'\t\t\t\t<Fence pos="{f}" />')
    for p in z213["placements"]:
        if p["is_outpost"]:
            L.append(_npc_element("\t\t\t\t", p["npc_attrs"]))
    L.append('\t\t\t\t<Attribute achieveConditionId="0" abnormality="0" />')
    L.append('\t\t\t</Territory>')
    return "\n".join(L)


def apply_plan(sources, z13, z213):
    """Insert the reconstruction into the server files. Idempotent and validated.

    Every unit (zone-13 group, the outpost territory, each villager, the Eria pos)
    is inserted only when not already present; an already-applied unit is reported
    as skipped, never duplicated. Each edited file is re-validated (ET parse)
    before it is written. Returns (written_paths, report).
    """
    written = []
    rep = {"z13_inserted": [], "z13_skipped": [], "z213_inserted": [], "z213_skipped": []}

    # ---- Zone 13: reconstructed groups (skip already-present) ----
    if z13["groups"]:
        p13 = find_zone_file(sources.v92, "TerritoryData", 13)
        tf13 = TextFile(p13)
        text = tf13.text
        new_blocks = []
        for g in z13["groups"]:
            if _group_span(text, g["gid"]):
                rep["z13_skipped"].append(g["gid"])
            else:
                new_blocks.append(g["xml"])
                rep["z13_inserted"].append(g["gid"])
        if new_blocks:
            idx = text.rfind("</TerritoryData>")
            if idx == -1:
                raise ValueError("TerritoryData_13.xml has no root close")
            text = text[:idx] + "\n".join(new_blocks) + "\n" + text[idx:]
            validate_xml(text)
            tf13.write(text)
            written.append(str(p13))

    # ---- Zone 213: outpost territory + villagers + Eria (all idempotent) ----
    if z213.get("placements"):
        p213 = find_zone_file(sources.v92, "TerritoryData", 213)
        tf213 = TextFile(p213)
        t2 = tf213.text
        changed = False

        if z213["outpost_block"]:
            otid = z213["outpost_block"]["territory_id"]
            if _territory_span(t2, otid):
                rep["z213_skipped"].append(f"territory {otid}")
            else:
                t2 = insert_territory_in_group(t2, "21300003", build_outpost_territory(z213))
                rep["z213_inserted"].append(f"territory {otid} (+ outpost villagers)")
                changed = True

        for p in z213["placements"]:
            if p["is_outpost"]:
                continue  # placed inside the outpost territory block above
            if _has_attr(t2, "instanceId", p["instance"]):
                rep["z213_skipped"].append(f"{p['name']} {p['instance']}")
                continue
            npc = _npc_element("\t\t\t\t", p["npc_attrs"])
            t2 = insert_npc_in_territory(t2, p["target_terr_id"], npc)
            rep["z213_inserted"].append(f"{p['name']} {p['instance']} -> terr {p['target_terr_id']}")
            changed = True

        e = z213["eria"]
        if _eria_pos(t2, e["instance"]) == e["new_pos_attr"]:
            rep["z213_skipped"].append(f"Eria pos {e['instance']} (already relocated)")
        else:
            t2 = re.sub(r'(<Npc instanceId="' + str(e["instance"]) + r'"[^>]*?\bpos=")[^"]*(")',
                        r'\g<1>' + e["new_pos_attr"] + r'\g<2>', t2, count=1)
            rep["z213_inserted"].append(f"Eria pos {e['instance']} relocated")
            changed = True

        if changed:
            validate_xml(t2)
            tf213.write(t2)
            written.append(str(p213))

    return written, rep


def verify_apply(sources, z13, z213):
    """Re-read the written files; return a list of problems (empty = all good).

    Confirms every id the plan claims to add is present and every file still has
    unique instanceIds. A non-empty return must make --apply fail loudly.
    """
    problems = []

    def dup_instances(text, zid):
        ids = re.findall(r'instanceId="(\d+)"', text)
        dups = sorted({x for x in ids if ids.count(x) > 1})
        if dups:
            problems.append(f"zone{zid}: duplicate instanceIds {dups}")

    t13 = read_text(find_zone_file(sources.v92, "TerritoryData", 13))
    for g in z13["groups"]:
        if not _group_span(t13, g["gid"]):
            problems.append(f"zone13: group {g['gid']} missing after apply")
    dup_instances(t13, 13)

    if z213.get("placements"):
        t213 = read_text(find_zone_file(sources.v92, "TerritoryData", 213))
        if z213["outpost_block"]:
            otid = z213["outpost_block"]["territory_id"]
            if not _territory_span(t213, otid):
                problems.append(f"zone213: outpost territory {otid} missing after apply")
        for p in z213["placements"]:
            if not _has_attr(t213, "instanceId", p["instance"]):
                problems.append(f"zone213: {p['name']} instanceId {p['instance']} missing")
            if not _has_attr(t213, "npcTemplateId", p["template"]):
                problems.append(f"zone213: {p['name']} template {p['template']} missing")
        e = z213["eria"]
        if _eria_pos(t213, e["instance"]) != e["new_pos_attr"]:
            problems.append(f"zone213: Eria pos {e['instance']} not at target")
        dup_instances(t213, 213)
    return problems


# ===========================================================================
# Main
# ===========================================================================

def build_kill_by_template(sources):
    """{templateId: kill count} from client kill tasks of the fed quests."""
    from dclib import index_quest_shards_by_id, parse_quest, parse_pair
    cidx = index_quest_shards_by_id(sources.old_client / "Quest")
    fed = {q for _, (_, _, quests, _) in [(g, GROUP_MOBS[g]) for g in GROUP_MOBS]
           for q in quests}
    out = {}
    for gid in fed:
        p = cidx.get(gid)
        if not p:
            continue
        m = parse_quest(read_text(p))
        for t in m["tasks"].values():
            for mon, kc, _ in t["monsters"]:
                pair = parse_pair(mon)
                if pair and kc and kc.isdigit():
                    out[pair[1]] = max(out.get(pair[1], 0), int(kc))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconstruct deleted TerritoryData spawns.")
    parser.add_argument("--zones", default="13,213", help="Comma-separated zones (13,213)")
    parser.add_argument("--plan-out",
                        default=str(Path(__file__).resolve().parents[2] / "docs" / "plans"
                                    / "iod-alpha-content-loop" / "batch-3-spawn-plan.md"),
                        help="Output plan markdown path")
    parser.add_argument("--json", help="Output JSON path (defaults beside --plan-out)")
    parser.add_argument("--audit",
                        default=str(Path(__file__).resolve().parents[2] / "docs" / "plans"
                                    / "iod-alpha-content-loop" / "iteration-2-quest-audit.json"),
                        help="Audit JSON for closure join")
    parser.add_argument("--apply", action="store_true",
                        help="Write server files (default: dry-run plan only)")
    args = parser.parse_args()

    zones = [int(z) for z in args.zones.split(",") if z.strip()]
    refs = load_references()
    sources = Sources(refs)
    problems = sources.validate()
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        return 1

    t0 = time.monotonic()
    tmap13 = npc_template_ids(read_text(find_zone_file(sources.v92, "NpcData", 13)))
    # Donors from the git HEAD baseline so already-applied reconstructions do not
    # pollute the donor pool (keeps donor selection and the plan reproducible).
    donors13 = npc_donors(v92_territory_text(sources, 13))
    donors213 = npc_donors(v92_territory_text(sources, 213))
    # A clean fixed-villager donor: instance 21300032 (정찰병 라사나, tpl 1141).
    villager_donor = donors213.get(1141) or donors213.get(1017)
    kill_by_template = build_kill_by_template(sources)

    groups13, cli13, v9213 = ([], {}, {})
    z13 = {"groups": []}
    if 13 in zones:
        groups13, cli13, v9213 = reconstruct_zone13(sources, tmap13, donors13, kill_by_template)
        z13 = {"groups": groups13}

    z213 = {"groups": [], "territory_diffs": {}, "deleted": {}, "placements": [],
            "eria": {}, "outpost": None, "outpost_terr_id": None, "outpost_block": None}
    if 213 in zones:
        z213, _, _ = reconstruct_zone213(sources, villager_donor)

    clears, remains = closure(args.audit, z213["placements"], z213["eria"]) if z213["placements"] else ([], [])

    report = render_plan(z13, z213, clears, remains, kill_by_template, tmap13)
    out_path = Path(args.plan_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    json_path = Path(args.json) if args.json else out_path.with_suffix(".json")
    payload = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"), "zones": zones,
        "zone13_groups": [{k: v for k, v in g.items()} for g in z13["groups"]],
        "zone213": {k: v for k, v in z213.items() if k != "outpost_block"},
        "closure": {"clears": clears, "remains": remains},
        "kill_by_template": kill_by_template,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str),
                         encoding="utf-8")

    print("=" * 78)
    print("spawn_restore " + ("(APPLY)" if args.apply else "(dry-run plan)"))
    print("=" * 78)
    print(f"  zone 13: {len(z13['groups'])} groups, "
          f"{sum(g['n_territories'] for g in z13['groups'])} territories, "
          f"{sum(g['n_npc'] for g in z13['groups'])} npc entries")
    print(f"  zone 213: {sum(len(v) for v in z213['deleted'].values())} recovered territories, "
          f"{len(z213['placements'])} villagers, "
          f"{'1 Eria relocation' if z213['eria'] else 'no eria'}")
    print(f"  closure: {len(clears)} flags clear, {len(remains)} remain")
    print(f"  plan -> {out_path}")
    print(f"  json -> {json_path}")

    if args.apply:
        written, rep = apply_plan(sources, z13, z213)
        print(f"  zone 13: inserted {len(rep['z13_inserted'])} groups, "
              f"skipped {len(rep['z13_skipped'])} already-present")
        print(f"  zone 213 inserted ({len(rep['z213_inserted'])}): {rep['z213_inserted']}")
        print(f"  zone 213 skipped ({len(rep['z213_skipped'])}): {rep['z213_skipped']}")
        for wp in written:
            print(f"  WROTE {wp}")
        if not written:
            print("  (no changes: everything already applied)")
        problems = verify_apply(sources, z13, z213)
        if problems:
            print("  APPLY VERIFICATION FAILED -- the following are missing/broken:")
            for pr in problems:
                print(f"    - {pr}")
            return 1
        print("  APPLY VERIFIED: every planned id present; instanceIds unique in both files.")
    else:
        print(f"  [dry-run] no datasheet written. Done in {time.monotonic()-t0:.1f}s.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
