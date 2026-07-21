#!/usr/bin/env python
"""Extract the v17.11 Island of Dawn quest catalog from the old client DataCenter.

Deterministic and re-runnable: sorted output, no timestamps. Reuses dclib for
source resolution, the namespace-agnostic quest model parser, client title and
dialog helpers, and the compensation (reward) parser.

Island quest membership is the global-id band 1300-1399 whose Quest번호 header
keys hunting zone 13 (the island quest space). The physical island hunting zones
(13, 64, 213, 313, 364, 436) are the zones a quest's giver, task NPCs, target
regions and monsters actually touch; those are attributed per quest from the
data, never guessed from the id.

Outputs (paths are CLI flags):
  - a JSON catalog (one record per quest, plus catalog-level summary and the
    prerequisite chain graph), and
  - a Markdown catalog with a per-quest table, the story spine, and the
    prerequisite chains rendered as indented trees with AUTOGRANT_CHAIN flags.

Usage:
  python reforged/tools/dc-restore/extract_quests.py \
    --json reforged/docs/plans/iod-alpha-content-loop/data/v17-quests.json \
    --md   reforged/docs/plans/iod-alpha-content-loop/data/v17-quests.md
"""

import argparse
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TOOLDIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLDIR))
import dclib  # noqa: E402

ISLAND_ZONES = [13, 64, 213, 313, 364, 436]
BAND_LO, BAND_HI = 1300, 1399

# Extra header/task tags this catalog reads beyond dclib's model.
QT_MINLV = "최소레벨"
TK_TARGET_REGION = "목표지역"     # travel-task target region ("hz,hz*100000+N")
TRIGGER_AUTO = "즉시수주"          # auto-accept (immediate grant) trigger
REPEAT_YES = "반복"                # repeatable flag value
TYPE_MISSION = "미션"              # story-mission quest type

# Task-name (이름) Korean discriminator -> stable English label.
TASK_LABELS = {
    "방문Task": "visit",
    "사냥Task": "hunt",
    "사냥전달Task": "hunt-deliver",
    "찔러준아이템전달Task": "deliver-item",
    "채집Task": "gather",
    "수호Task": "guard",
    "조건Task": "condition",
    "동영상재생Task": "cinematic",
    "PC이동Task": "travel",
}


def strip(tag: str) -> str:
    return dclib.strip_ns(tag)


def _pair_zone(ref: str) -> int | None:
    """Physical hunting zone from an 'hz,local' ref (first component)."""
    p = dclib.parse_pair(ref)
    return p[0] if p else None


def _region_zone(ref: str) -> int | None:
    """Physical zone from a 목표지역 'hz,hz*100000+N' region ref."""
    p = dclib.parse_pair(ref)
    if not p:
        return None
    return p[0]


def load_island_client_quests(client_dc: Path):
    """Return {gid: (path, raw_text, model)} for the 13xx island band, hz=13."""
    quest_dir = client_dc / "Quest"
    by_id = dclib.index_quest_shards_by_id(quest_dir)
    out = {}
    for gid, path in by_id.items():
        if not (BAND_LO <= gid <= BAND_HI):
            continue
        raw = dclib.read_text(path)
        model = dclib.parse_quest(raw)
        if model is None or model.get("hz") != 13:
            continue
        out[gid] = (path, raw, model)
    return out


def extract_min_level(raw: str) -> str:
    root = ET.fromstring(raw.encode("utf-8"))
    for el in root.iter():
        if strip(el.tag) == QT_MINLV:
            return (el.text or "").strip()
    return ""


def extract_task_regions(raw: str) -> dict[str, list[str]]:
    """Map task id (str) -> list of 목표지역 region refs, in document order."""
    root = ET.fromstring(raw.encode("utf-8"))
    out: dict[str, list[str]] = {}
    tasks = None
    for c in root:
        if strip(c.tag) == "Tasks":
            tasks = c
    if tasks is None:
        return out
    for t in tasks:
        if strip(t.tag) != "Task":
            continue
        tid = t.get("id", "")
        regions = []
        for el in t.iter():
            if strip(el.tag) == TK_TARGET_REGION and (el.text or "").strip():
                regions.append((el.text or "").strip())
        if regions:
            out[tid] = regions
    return out


def classify_type(model: dict) -> str:
    if model["repeat"] == REPEAT_YES:
        return "repeatable"
    if model["story_group"]:
        return "story"
    return "zone"


def parse_group_list(client_dc: Path):
    """QGL story groups -> {group_id: {name, order: [gid,...]}} restricted to island.

    Also returns gid -> (group_id, group_name, position, group_size) for island
    quests registered in a StoryGroup.
    """
    qgl_dir = client_dc / "QuestGroupList"
    text = None
    for entry in qgl_dir.iterdir():
        if entry.suffix.lower() == ".xml":
            text = dclib.read_text(entry)
            break
    groups: dict[str, dict] = {}
    membership: dict[int, dict] = {}
    if text is None:
        return groups, membership
    root = ET.fromstring(text.encode("utf-8"))
    sgl = None
    for c in root:
        if strip(c.tag) == "StoryGroupList":
            sgl = c
    if sgl is None:
        return groups, membership
    for sg in sgl:
        if strip(sg.tag) != "StoryGroup":
            continue
        gorder = [int(q.get("id")) for q in sg
                  if strip(q.tag) == "Quest" and q.get("id") and q.get("id").isdigit()]
        island = [g for g in gorder if BAND_LO <= g <= BAND_HI]
        if not island:
            continue
        gid_group = sg.get("id", "")
        gname = sg.get("name", "")
        groups[gid_group] = {"name": gname, "order": gorder, "island_order": island}
        for pos, g in enumerate(island, start=1):
            membership[g] = {
                "group_id": gid_group, "group_name": gname,
                "position": pos, "group_island_size": len(island),
            }
    return groups, membership


def build(client_dc: Path):
    quests = load_island_client_quests(client_dc)
    strsheet = client_dc / "StrSheet_Quest"
    comp_index = dclib.index_client_comp(client_dc / "QuestCompensationData")
    dialog_set = dclib.index_client_quest_dialogs(client_dc / "QuestDialog")
    groups, membership = parse_group_list(client_dc)

    # (hz,local) -> gid, to resolve prerequisite refs within the island band.
    key_to_gid: dict[tuple[int, int], int] = {}
    for gid, (_p, _r, model) in quests.items():
        if model["hz"] is not None and model["local"] is not None:
            key_to_gid[(model["hz"], model["local"])] = gid

    records = []
    for gid in sorted(quests):
        path, raw, model = quests[gid]
        title = dclib.client_quest_title(strsheet, gid)
        title = html.unescape(title) if title else None

        accept = "auto" if model["trigger_type"] == TRIGGER_AUTO else "npc"
        giver = model["giver"] or None

        regions_by_task = extract_task_regions(raw)

        # Ordered task summaries (parse_quest keeps document order in the dict).
        tasks_summary = []
        target_npcs: list[str] = []
        touched_zones: set[int] = set()
        if giver:
            z = _pair_zone(giver)
            if z is not None:
                touched_zones.add(z)
        for tid, td in model["tasks"].items():
            label = TASK_LABELS.get(td["type"], td["type"])
            regions = regions_by_task.get(str(tid), [])
            npc_refs = sorted(set(td["visits"]) | set(td["target_npc"]))
            monster_refs = [m[0] for m in td["monsters"]]
            for ref in npc_refs:
                target_npcs.append(ref)
                z = _pair_zone(ref)
                if z is not None:
                    touched_zones.add(z)
            for ref in regions:
                z = _region_zone(ref)
                if z is not None:
                    touched_zones.add(z)
            for ref in monster_refs:
                z = _pair_zone(ref)
                if z is not None:
                    touched_zones.add(z)
            tasks_summary.append({
                "id": tid,
                "type": label,
                "type_raw": td["type"],
                "npc_targets": npc_refs,
                "regions": regions,
                "monsters": [{"ref": m[0], "count": m[1]} for m in td["monsters"]],
                "collections": td["collections"],
                "deliver_items": [{"ref": d[0], "qty": d[1]} for d in td["deliver_items"]],
                "dungeon": td["dungeon"] or None,
            })

        receiver = target_npcs[-1] if target_npcs else None

        # Prerequisites resolved to island gids where possible.
        prereqs = []
        for pr in model["prereqs"]:
            pair = dclib.parse_pair(pr)
            resolved = key_to_gid.get(pair) if pair else None
            prereqs.append({"ref": pr, "gid": resolved})

        comp = comp_index.get(gid)
        reward = None
        if comp is not None:
            reward = {
                "exp": comp["exp"], "gold": comp["gold"],
                "itemBag": comp["itemBag"], "policyPoint": comp["policyPoint"],
                "type": comp["type"],
                "items": [{"templateId": t, "quantity": q, "class": c}
                          for t, q, c in comp["items"]],
                "summary": dclib.comp_summary(comp),
            }

        member = membership.get(gid)
        record = {
            "id": gid,
            "quest_no": f"{model['hz']},{model['local']}",
            "title": title,
            "type": classify_type(model),
            "quest_type_raw": model["quest_type"],
            "repeat": model["repeat"],
            "accept": accept,
            "giver": giver,
            "giver_zone": _pair_zone(giver) if giver else None,
            "receiver": receiver,
            "min_level": extract_min_level(raw),
            "max_level": model["max_level"] or None,
            "classes": model["classes"] or None,
            "prereqs": prereqs,
            "story_group": member["group_id"] if member else None,
            "story_group_name": member["group_name"] if member else None,
            "chain_position": member["position"] if member else None,
            "chain_group_size": member["group_island_size"] if member else None,
            "physical_zones": sorted(touched_zones),
            "tasks": tasks_summary,
            "task_types": [t["type"] for t in tasks_summary],
            "reward": reward,
            "dialog_present": (13, model["local"]) in dialog_set,
            "autogrant_chain": accept == "auto" and len(prereqs) > 0,
            "source_file": path.name,
        }
        records.append(record)

    summary = summarize(records, groups)
    graph = build_prereq_graph(records)
    return {"summary": summary, "story_groups": serialize_groups(groups),
            "quests": records, "prereq_graph": graph}


def serialize_groups(groups: dict) -> list[dict]:
    out = []
    for gid in sorted(groups, key=lambda x: int(x) if x.isdigit() else 0):
        g = groups[gid]
        out.append({"group_id": gid, "name": g["name"],
                    "island_order": g["island_order"]})
    return out


def summarize(records: list[dict], groups: dict) -> dict:
    by_type: dict[str, int] = {}
    by_accept: dict[str, int] = {}
    per_zone: dict[int, int] = {z: 0 for z in ISLAND_ZONES}
    autogrant = []
    for r in records:
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
        by_accept[r["accept"]] = by_accept.get(r["accept"], 0) + 1
        for z in r["physical_zones"]:
            if z in per_zone:
                per_zone[z] += 1
        if r["autogrant_chain"]:
            autogrant.append(r["id"])
    giver_zone: dict[int, int] = {}
    for r in records:
        if r["giver_zone"] is not None:
            giver_zone[r["giver_zone"]] = giver_zone.get(r["giver_zone"], 0) + 1
    return {
        "total": len(records),
        "by_type": by_type,
        "by_accept": by_accept,
        "quests_touching_zone": per_zone,
        "giver_zone_counts": giver_zone,
        "autogrant_chain_quests": autogrant,
        "autogrant_chain_count": len(autogrant),
        "story_group_count": len(groups),
    }


def build_prereq_graph(records: list[dict]) -> dict:
    """Adjacency + roots for the island prerequisite chains (gid space only)."""
    by_id = {r["id"]: r for r in records}
    children: dict[int, list[int]] = {r["id"]: [] for r in records}
    parents: dict[int, list[int]] = {r["id"]: [] for r in records}
    for r in records:
        for pr in r["prereqs"]:
            pg = pr["gid"]
            if pg in by_id:
                children[pg].append(r["id"])
                parents[r["id"]].append(pg)
    for k in children:
        children[k] = sorted(children[k])
    roots = sorted(r["id"] for r in records if not parents[r["id"]])
    return {"roots": roots, "children": children, "parents": parents}


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_md(data: dict) -> str:
    s = data["summary"]
    L = []
    L.append("# Island of Dawn Quest Catalog (v17.11 north star)")
    L.append("")
    L.append("Source: old client DataCenter (v17.11, `old_client_dc`). Generated by "
             "`tools/dc-restore/extract_quests.py`. Deterministic; re-run to refresh.")
    L.append("")
    L.append("Membership is the global-id band 1300-1399 keyed to Quest번호 hunting "
             "zone 13 (the island quest space). Physical zones are the island hunting "
             "zones a quest actually touches (giver, task NPCs, target regions, "
             "monsters).")
    L.append("")

    L.append("## Summary")
    L.append("")
    L.append(f"- Total island quests: **{s['total']}**")
    L.append(f"- By type: " + ", ".join(f"{k} {v}" for k, v in sorted(s["by_type"].items())))
    L.append(f"- By accept mechanism: " + ", ".join(f"{k} {v}" for k, v in sorted(s["by_accept"].items())))
    L.append(f"- Story groups on the island: {s['story_group_count']}")
    L.append(f"- AUTOGRANT_CHAIN flags (auto-accept behind a prerequisite): "
             f"**{s['autogrant_chain_count']}** "
             f"({', '.join(str(g) for g in s['autogrant_chain_quests']) or 'none'})")
    L.append("")
    L.append("### Quests touching each physical hunting zone")
    L.append("")
    L.append("A quest is counted once per zone its giver, task NPCs, target regions, "
             "or monster refs touch, so a quest may count in several zones. Monster "
             "refs on island quests are keyed to quest-space zone 13, which is why "
             "zone 13 is heavily represented.")
    L.append("")
    L.append("| Zone | Quests touching | Quests given here |")
    L.append("|------|-----------------|-------------------|")
    for z in ISLAND_ZONES:
        L.append(f"| {z} | {s['quests_touching_zone'].get(z, 0)} | "
                 f"{s['giver_zone_counts'].get(z, 0)} |")
    L.append("")

    # Story spine
    L.append("## Main story spine")
    L.append("")
    L.append("Story-group order from QuestGroupList (ordering is authored, not "
             "numeric). This is the intended main-quest progression.")
    L.append("")
    for g in data["story_groups"]:
        L.append(f"### StoryGroup {g['group_id']}: {g['name']}")
        L.append("")
        for pos, gid in enumerate(g["island_order"], start=1):
            rec = next((r for r in data["quests"] if r["id"] == gid), None)
            title = rec["title"] if rec else "(missing quest shard)"
            acc = f" [auto-accept]" if rec and rec["accept"] == "auto" else ""
            L.append(f"{pos}. `{gid}` {title}{acc}")
        L.append("")

    # Per-quest table
    L.append("## Quest table")
    L.append("")
    L.append("| id | title | type | accept | giver | receiver | lvl | prereqs | "
             "story grp/pos | zones | tasks | reward | dialog |")
    L.append("|----|-------|------|--------|-------|----------|-----|---------|"
             "---------------|-------|-------|--------|--------|")
    for r in data["quests"]:
        prereqs = ", ".join(
            (str(p["gid"]) if p["gid"] else p["ref"]) for p in r["prereqs"]) or "-"
        grp = (f"{r['story_group']}:{r['chain_position']}/{r['chain_group_size']}"
               if r["story_group"] else "-")
        zones = ",".join(str(z) for z in r["physical_zones"]) or "-"
        tasks = " > ".join(r["task_types"]) or "-"
        reward = r["reward"]["summary"] if r["reward"] else "-"
        title = (r["title"] or "").replace("|", "\\|")
        L.append(f"| {r['id']} | {title} | {r['type']} | {r['accept']} | "
                 f"{r['giver'] or '-'} | {r['receiver'] or '-'} | "
                 f"{r['min_level'] or '-'} | {prereqs} | {grp} | {zones} | "
                 f"{tasks} | {reward} | {'yes' if r['dialog_present'] else 'NO'} |")
    L.append("")

    # Prerequisite graph
    L.append("## Prerequisite chains")
    L.append("")
    L.append("Indented trees rooted at quests with no island prerequisite. "
             "`[AUTOGRANT_CHAIN]` marks an auto-accept quest sitting behind a "
             "prerequisite: if the predecessor is not active, the auto-grant never "
             "fires and the chain stalls.")
    L.append("")
    graph = data["prereq_graph"]
    by_id = {r["id"]: r for r in data["quests"]}

    def render_node(gid: int, depth: int, seen: set):
        rec = by_id.get(gid)
        title = rec["title"] if rec else "(unknown)"
        flag = ""
        if rec and rec["autogrant_chain"]:
            flag = "  [AUTOGRANT_CHAIN]"
        acc = " (auto)" if rec and rec["accept"] == "auto" else ""
        L.append("  " * depth + f"- `{gid}` {title}{acc}{flag}")
        if gid in seen:
            L.append("  " * (depth + 1) + "- (cycle)")
            return
        seen = seen | {gid}
        for child in graph["children"].get(gid, []):
            render_node(child, depth + 1, seen)

    # Only render roots that actually have descendants or are themselves island
    # story quests; list isolated no-prereq zone quests compactly afterwards.
    rooted = [g for g in graph["roots"] if graph["children"].get(g)]
    isolated = [g for g in graph["roots"] if not graph["children"].get(g)]
    for gid in rooted:
        render_node(gid, 0, set())
        L.append("")
    if isolated:
        L.append("### Standalone quests (no island prerequisite, no dependents)")
        L.append("")
        for gid in isolated:
            rec = by_id[gid]
            acc = " (auto-accept)" if rec["accept"] == "auto" else ""
            L.append(f"- `{gid}` {rec['title']}{acc}")
        L.append("")

    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Extract the v17.11 Island of Dawn quest catalog.")
    ap.add_argument("--json", required=True, help="Output JSON catalog path")
    ap.add_argument("--md", required=True, help="Output Markdown catalog path")
    args = ap.parse_args()

    refs = dclib.load_references()
    client_dc = Path(refs["old_client_dc"])
    if not client_dc.exists():
        sys.exit(f"old_client_dc not found: {client_dc}")

    data = build(client_dc)

    json_path = Path(args.json)
    md_path = Path(args.md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8")
    md_path.write_text(render_md(data), encoding="utf-8")

    s = data["summary"]
    print(f"wrote {json_path} and {md_path}")
    print(f"total={s['total']} by_type={s['by_type']} "
          f"autogrant_chain={s['autogrant_chain_count']}")


if __name__ == "__main__":
    main()
