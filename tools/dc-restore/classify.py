"""
classify.py - Phase 2b Island of Dawn restoration classifier.

Deterministic join/diff over the pre-digested Phase-2a artifacts plus the clean
v92 baseline tree. Produces per-key classification verdict tables that spec
authoring translates directly into DSL specs.

Verdict vocabulary (per key / per attribute):
  MATCH    - baseline already equals target; no spec op needed.
  RESTORE  - missing or wrong in baseline; upsert to target.
  REMOVE   - present in baseline, absent from target; delete.
  GAPFILL  - target content sourced from v31 keyed to a v17-rostered entity.
  DECISION - judgement call; both options recorded, recommendation given, not chosen here.

Provenance vocabulary: v17 | v31-gapfill | v92-keep | patch-000.

Re-runnable: reads only, writes only the classification-*.json/.md and decisions.md
outputs. No game data mutated, no git.

Usage:  python classify.py
"""

import json
import os
import xml.etree.ElementTree as ET
from collections import defaultdict, OrderedDict

DATA = r"D:\dev\mmogate\github\reforged-server-content\reforged\docs\plans\iod-alpha-content-loop\data"
BASE = r"D:\dev\mmogate\tera92\server\Datasheet"
OUT = DATA  # deliverable artifacts land alongside the inputs

SCOPE_ZONES = [13, 64, 213, 313, 364, 436]


# --------------------------------------------------------------------------- #
# loaders
# --------------------------------------------------------------------------- #
def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def strip_bom(path):
    with open(path, "r", encoding="utf-8-sig") as fh:
        return fh.read()


# --------------------------------------------------------------------------- #
# baseline XML readers (targeted; only extract what a diff needs)
# --------------------------------------------------------------------------- #
def base_territory_groups(hz):
    """group_id -> {desc, territory_ids:set, npc_templates:set, n_npcs:int}."""
    path = os.path.join(BASE, f"TerritoryData_{hz}.xml")
    if not os.path.exists(path):
        return {}
    root = ET.fromstring(strip_bom(path))
    out = OrderedDict()
    for grp in root.findall("TerritoryGroup"):
        gid = grp.get("id")
        terr_ids = set()
        tmpls = set()
        n_npcs = 0
        tl = grp.find("TerritoryList")
        if tl is not None:
            for terr in tl.findall("Territory"):
                terr_ids.add(terr.get("id"))
                for npc in terr.findall("Npc"):
                    tmpls.add(npc.get("npcTemplateId"))
                    n_npcs += 1
        out[gid] = {
            "desc": grp.get("desc", ""),
            "territory_ids": terr_ids,
            "npc_templates": tmpls,
            "n_npcs": n_npcs,
        }
    return out


def base_compensation_templates(hz):
    """Set of npcTemplateId strings that carry a loot bag in CCompensation_{hz}."""
    path = os.path.join(BASE, "CompensationData", f"CCompensation_{int(hz):04d}.xml")
    out = {}
    if not os.path.exists(path):
        return out
    root = ET.fromstring(strip_bom(path))
    for comp in root.findall("Compensation"):
        out[comp.get("npcTemplateId")] = len(comp.findall("ItemBag"))
    return out


def base_collection_territory(fname):
    """(territoryId, collectionsId) -> spawn count for a CollectionTerritory file."""
    path = os.path.join(BASE, "CollectionData", fname)
    out = {}
    if not os.path.exists(path):
        return None
    root = ET.fromstring(strip_bom(path))
    for terr in root.findall("Territory"):
        tid = terr.get("id")
        for col in terr.findall("Collections"):
            cid = col.get("id")
            out[(tid, cid)] = len(col.findall("Spawn"))
    return out


def base_bonfires(hz):
    path = os.path.join(BASE, f"BonfireData_{hz}.xml")
    if not os.path.exists(path):
        return []
    root = ET.fromstring(strip_bom(path))
    return [(b.get("id"), b.get("desc", ""), b.get("loc", "")) for b in root.findall("Bonfire")]


def base_buy_menus():
    """menu_id(str) -> [ItemList id str] from the v92 BuyMenuList.xml baseline."""
    path = os.path.join(BASE, "BuyMenuList.xml")
    out = {}
    if not os.path.exists(path):
        return out
    root = ET.fromstring(strip_bom(path))
    for menu in root.findall("Menu"):
        out[menu.get("id")] = [il.get("id") for il in menu.findall("ItemList")]
    return out


def base_buy_lists():
    """list_id(str) -> [itemId str] from the v92 BuyList.xml baseline."""
    path = os.path.join(BASE, "BuyList.xml")
    out = {}
    if not os.path.exists(path):
        return out
    root = ET.fromstring(strip_bom(path))
    for lst in root.findall("List"):
        out[lst.get("id")] = [it.get("itemId") for it in lst.findall("Item")]
    return out


# --------------------------------------------------------------------------- #
# axis 1+ : QUESTS
# --------------------------------------------------------------------------- #
# Map each v17-vs-v31 drift flag to the quest attribute it drives. Because
# id-alignment-quests confirms v92 and v31 carry an identical sentinel-disabled
# set (40 each) and identical story-group registration, v31 is used as a
# high-confidence proxy for the v92 baseline on quest structure. Attributes where
# v92 could theoretically differ from v31 carry a confidence note.
def classify_quests():
    v17 = load("v17-quests.json")
    v31 = load("v31-quests.json")
    iaq = load("id-alignment-quests.json")

    disabled = set(v31["summary"]["v31_sentinel_disabled"])
    v92_disabled_same = iaq["disabled_count_v92"] == iaq["disabled_count_v31"] == len(disabled)
    v31_by_gid = {q["gid"]: q for q in v31["quests"]}
    v17_by_id = {q["id"]: q for q in v17["quests"]}

    rows = []
    decisions = []
    counts = defaultdict(int)

    for q in v17["quests"]:
        gid = q["id"]
        vq = v31_by_gid.get(gid, {})
        flags = set(vq.get("flags", []))
        v17_accept = q["accept"]
        autogrant = q.get("autogrant_chain", False)

        attrs = OrderedDict()

        # --- enabled state ---
        if gid in disabled:
            attrs["enabled_state"] = ("RESTORE", "v17",
                "v31/v92 sentinel-disabled (99,99); v17 has it enabled -> re-enable",
                "high" if v92_disabled_same else "medium")
        else:
            attrs["enabled_state"] = ("MATCH", "v92-keep", "enabled in both v17 and baseline", "high")

        # --- prereq chain ---
        if "PREREQ_DRIFT" in flags:
            attrs["prereq_chain"] = ("RESTORE", "v17",
                "v17 prereq chain differs from v31/v92 rewiring -> v17 chain wins", "high")
        else:
            attrs["prereq_chain"] = ("MATCH", "v92-keep", "prereqs equal v17", "high")

        # --- accept mechanism ---
        if gid == 1311:
            attrs["accept_mechanism"] = ("DECISION", "v17",
                "v17 authority = auto-accept; prior session converted to NPC-accept as a trap fix", "n/a")
            decisions.append({
                "axis": "quests", "key": "1311.accept_mechanism",
                "title": q["title"],
                "options": [
                    "A) auto-accept (v17 authority) - matches classic behaviour",
                    "B) NPC-accept (prior-session trap fix) - avoids auto-grant stall for chars who "
                    "cleared prereq 1310 while it was disabled",
                ],
                "recommendation": "B (NPC-accept): the auto-grant-behind-prereq trap stalls any "
                "character who completed 1310 during the disabled window; NPC-accept lets them pick it up.",
                "provenance": "v17 vs patch-000",
            })
        elif gid == 1305 and autogrant:
            attrs["accept_mechanism"] = ("RESTORE", "v17",
                "v17 = auto-accept (AUTOGRANT_CHAIN behind 1304); same auto-grant stall risk as 1311 "
                "-> flag for spec review", "medium")
        elif "ACCEPT_DRIFT" in flags:
            attrs["accept_mechanism"] = ("RESTORE", "v17",
                f"v17 accept={v17_accept}; v31/v92 differs -> restore v17 mechanism", "high")
        else:
            attrs["accept_mechanism"] = ("MATCH", "v92-keep", f"accept={v17_accept} equal", "high")

        # --- giver ---
        if "GIVER_DRIFT" in flags:
            attrs["giver"] = ("RESTORE", "v17", f"v17 giver={q['giver']} differs from baseline", "high")
        else:
            attrs["giver"] = ("MATCH", "v92-keep", f"giver={q['giver']} equal", "high")

        # --- receiver ---
        if "RECEIVER_DRIFT" in flags:
            attrs["receiver"] = ("RESTORE", "v17", f"v17 receiver={q['receiver']} differs from baseline", "high")
        else:
            attrs["receiver"] = ("MATCH", "v92-keep", f"receiver={q['receiver']} equal", "high")

        # --- story-group registration ---
        if "STORYGROUP_DRIFT" in flags:
            sg = q.get("story_group")
            attrs["story_group"] = ("RESTORE", "v17",
                f"v17 story-group={sg}; baseline registration differs", "high")
        else:
            attrs["story_group"] = ("MATCH", "v92-keep", "story-group registration equal", "high")

        # --- task structure ---
        if "TASKSEQ_DRIFT" in flags:
            attrs["task_structure"] = ("DECISION", "v17",
                "task sequence drifted between v17 and v31/v92 -> restoration depth decision", "n/a")
            decisions.append({
                "axis": "quests", "key": f"{gid}.task_structure",
                "title": q["title"],
                "options": [
                    "A) shallow: re-enable with the v92 task structure as-is (fast, playable, not classic-faithful)",
                    "B) deep: reconstruct the v17 task sequence "
                    f"({' > '.join(q.get('task_types', []))}) (classic-faithful, more spec work)",
                ],
                "recommendation": "A (shallow) for zone/repeatable quests where task drift is cosmetic; "
                "B (deep) for the main-story spine quests where task order carries narrative.",
                "provenance": "v17 vs v92-keep",
            })
        elif "TASKCOUNT_DRIFT" in flags:
            attrs["task_structure"] = ("RESTORE", "v17",
                "task count differs; restore v17 task set", "medium")
        else:
            attrs["task_structure"] = ("MATCH", "v92-keep", "task structure equal", "high")

        # overall verdict = most severe among attributes
        verds = [a[0] for a in attrs.values()]
        if "DECISION" in verds:
            overall = "DECISION"
        elif "RESTORE" in verds:
            overall = "RESTORE"
        else:
            overall = "MATCH"
        counts[overall] += 1

        rows.append({
            "gid": gid, "title": q["title"], "type": q["type"],
            "overall": overall,
            "attributes": {k: {"verdict": v[0], "provenance": v[1], "note": v[2], "confidence": v[3]}
                           for k, v in attrs.items()},
            "v31_flags": sorted(flags),
        })

    # extras 1379 / 1383 -> DECISION (recommend v92-keep, Gunner playable on Reforged)
    for rc in iaq["remove_candidates"]:
        qid = rc["questId"]
        rows.append({
            "gid": qid, "title": rc["title"], "type": "extra-band",
            "overall": "DECISION",
            "attributes": {"membership": {"verdict": "DECISION", "provenance": "v92-keep",
                "note": "in v31+v92 band, absent from v17 roster", "confidence": "n/a"}},
            "v31_flags": [],
        })
        counts["DECISION"] += 1
        decisions.append({
            "axis": "quests", "key": f"{qid}.membership",
            "title": rc["title"],
            "options": [
                "A) v92-keep: leave enabled (Gunner is a playable class on Reforged)",
                "B) REMOVE: delete as out-of-roster to match strict v17 catalog",
            ],
            "recommendation": "A (v92-keep): Gunner is playable on Reforged, so the Gunner training "
            "quest belongs even though it post-dates the v17 catalog.",
            "provenance": "v92-keep",
        })

    meta = {
        "target": "v17 catalog",
        "roster_size": len(v17["quests"]),
        "sentinel_disabled_to_reenable": sorted(disabled),
        "sentinel_disabled_count": len(disabled),
        "v92_v31_disabled_set_identical": v92_disabled_same,
        "confidence_basis": "id-alignment-quests confirms v92==v31 on sentinel-disabled set (40) and "
        "story-group registration; v31 used as baseline proxy for giver/receiver/prereq/task drift.",
        "tasksseq_drift_decisions": v31["summary"]["flag_counts"].get("TASKSEQ_DRIFT", 0),
    }
    return {"meta": meta, "counts": dict(counts), "rows": rows}, decisions


# --------------------------------------------------------------------------- #
# axis 2 : QUEST REWARDS
# --------------------------------------------------------------------------- #
def classify_quest_rewards(reward_items_present):
    r = load("v31-quest-rewards.json")
    rows = []
    counts = defaultdict(int)
    blockers = []
    for rw in r["rewards"]:
        v = rw["verdict"]
        if v == "EXACT":
            verdict, note = "MATCH", "v31 rewards already equal v17 display data"
        else:
            verdict, note = "RESTORE", f"{v}: {rw['detail']}"
        counts[verdict] += 1
        rows.append({
            "gid": rw["gid"], "title": rw["title"], "verdict": verdict,
            "provenance": "v17",
            "note": note,
            "v17": rw["v17"], "v31_template": rw["v31"],
        })
    # blockers: any v17 reward item missing from v92 ItemData
    for item_id, present in sorted(reward_items_present.items()):
        if not present:
            blockers.append(item_id)
    meta = {
        "target": "v17 display data translated to server encoding",
        "roster_size": len(r["rewards"]),
        "verdict_counts_source": r["summary"]["verdict_counts"],
        "v17_reward_items_checked": len(reward_items_present),
        "v17_reward_items_missing_from_v92": blockers,
        "note": "v31 rewards are NOT the target (only 10/63 match); v31 rows used as encoding templates only.",
    }
    return {"meta": meta, "counts": dict(counts), "rows": rows}, blockers


# --------------------------------------------------------------------------- #
# axis 3 : SPAWNS / TERRITORIES
# --------------------------------------------------------------------------- #
V31_ONLY_GROUPS_HZ13 = {"1300140", "1300141"}  # pre-seeded DECISION (default REMOVE by v17 authority)


def classify_spawns():
    corr = load("territory-correlation.json")
    spawns = load("v31-spawns.json")
    spawn_by_hz = {z["hz"]: z for z in spawns["zones"]}

    rows = []
    decisions = []
    counts = defaultdict(int)
    hz_summary = []

    for zc in corr["zones"]:
        hz = zc["hz"]
        base_groups = base_territory_groups(hz)
        base_gids = set(base_groups.keys())
        sp = spawn_by_hz.get(hz, {})
        v31_groups_present = {g["group_id"] for g in sp.get("groups", [])}

        # v17 groups that have at least one same-group (identity) v31 match
        v17_groups = defaultdict(lambda: {"desc": "", "has_group_match": False, "n_terr": 0})
        for row in zc["rows"]:
            g = row["v17_group_id"]
            v17_groups[g]["desc"] = row["v17_group_desc"]
            v17_groups[g]["n_terr"] += 1
            if row["match_scope"] == "group" and row["match_quality"] in ("exact", "near"):
                v17_groups[g]["has_group_match"] = True

        deleted_v17_only = [g for g, v in v17_groups.items()
                            if not v["has_group_match"] and g not in base_gids]
        v31_only = [g for g in v31_groups_present if g not in v17_groups]

        # --- RESTORE rows: deleted v17-only groups (geometry from v17 fences,
        #     population from correlation cross-group losses) ---
        for g in sorted(deleted_v17_only):
            rows.append({
                "hz": hz, "group_id": g, "group_desc": v17_groups[g]["desc"],
                "verdict": "RESTORE", "provenance": "v17",
                "reconstruction_source": "geometry from v17 territory fences; population from "
                "correlation cross-group near losses (v17-only mob-camp group deleted in v31/v92)",
                "confidence": "medium",
            })
            counts["RESTORE"] += 1

        # --- v31 groups present in baseline: MATCH (baseline == v31 port) ---
        matched_groups = sorted(g for g in v31_groups_present
                                if g in base_gids and g not in V31_ONLY_GROUPS_HZ13)
        for g in matched_groups:
            counts["MATCH"] += 1  # summarised, not per-row emitted to keep table readable

        # --- v31-only groups: DECISION (default REMOVE by v17 authority) ---
        for g in sorted(set(v31_only) | (V31_ONLY_GROUPS_HZ13 if hz == 13 else set())):
            if g not in base_gids and g not in v31_groups_present:
                continue
            note = "v31-only territory group, absent from v17 roster"
            rows.append({
                "hz": hz, "group_id": g,
                "group_desc": base_groups.get(g, {}).get("desc", ""),
                "verdict": "DECISION", "provenance": "v31-gapfill",
                "note": note, "confidence": "n/a",
            })
            counts["DECISION"] += 1
            decisions.append({
                "axis": "spawns", "key": f"hz{hz}.group.{g}",
                "title": base_groups.get(g, {}).get("desc", g),
                "options": ["A) REMOVE (v17 authority: not in classic roster)",
                            "B) keep (popular-lore content)"],
                "recommendation": "A (REMOVE) by v17 authority" +
                (" - but note the Sandom cluster is popular-lore content worth a keep review"
                 if hz == 213 else ""),
                "provenance": "v31-gapfill",
            })

        hz_summary.append({
            "hz": hz,
            "v17_groups": len(v17_groups),
            "v31_groups_present": len(v31_groups_present),
            "baseline_groups": len(base_gids),
            "deleted_v17_only_RESTORE": len(deleted_v17_only),
            "matched_MATCH": len(matched_groups),
            "v31_only_DECISION": sum(1 for g in set(v31_only) |
                                     (V31_ONLY_GROUPS_HZ13 if hz == 13 else set())
                                     if g in base_gids or g in v31_groups_present),
            "exact_terr": zc["exact"], "near_terr": zc["near"],
            "near_cross_group_terr": zc["near_cross_group"],
        })

    # pre-seeded DECISION: 5 v31-only 213 spawn templates (default REMOVE by v17 authority)
    decisions.append({
        "axis": "spawns", "key": "hz213.v31_only_templates",
        "title": "5 v31-only NPC templates spawned in HZ 213 (not in v17 roster)",
        "options": ["A) REMOVE all 5 (v17 authority)",
                    "B) keep (Sandom cluster / lore NPCs)"],
        "recommendation": "A (REMOVE) by default v17 authority; Sandom (213/1054) is popular-lore "
        "content and may warrant a keep on review.",
        "provenance": "v31-gapfill",
    })

    meta = {
        "target": "v31 spawn entries mapped through identity (exact + near-group) territory matches",
        "hz_summary": hz_summary,
        "note": "Cross-group near matches are spatial coincidences (losses), not restorable "
        "correspondences. MATCH groups (baseline == v31 port) are summarised in hz_summary, "
        "not emitted per-row.",
    }
    return {"meta": meta, "counts": dict(counts), "rows": rows}, decisions


# --------------------------------------------------------------------------- #
# axis 4 : NPC STATS / BEHAVIOUR
# --------------------------------------------------------------------------- #
def classify_npcs():
    ns = load("v31-npc-stats.json")
    ian = load("id-alignment-npcs.json")

    rows = []
    counts = defaultdict(int)
    align_by = {}
    zz = ian["zones"]
    zone_iter = zz.values() if isinstance(zz, dict) else zz
    for z in zone_iter:
        for r in z["rows"]:
            align_by[(r["hz"], r["templateId"])] = r["classification"]

    for z in ns["zones"]:
        hz = z["hz"]
        for t in z["templates"]:
            tid = t["npcTemplateId"]
            cls = align_by.get((hz, tid), "ALIGNED")
            # Baseline came from the same v31 port; target = v31 stat block.
            # Aligned + stats present => MATCH.
            if cls == "ALIGNED" and t.get("npc_data_present"):
                verdict, prov, note, conf = ("MATCH", "v31-gapfill",
                    "aligned template, v31 stat block present; baseline from same v31 port", "medium")
            else:
                verdict, prov, note, conf = ("RESTORE", "v31-gapfill",
                    f"alignment={cls} or stats absent -> restore v31 stat block", "medium")
            counts[verdict] += 1
            rows.append({
                "hz": hz, "npcTemplateId": tid, "name": t.get("name", ""),
                "verdict": verdict, "provenance": "v31-gapfill",
                "note": note, "confidence": conf,
                "level": t.get("stat", {}).get("level"),
                "maxHp": t.get("stat", {}).get("maxHp"),
            })

    # out-of-roster extras (present in v31+v92, absent from v17) - informational
    extras = []
    for e in ian["extras"]:
        extras.append({"hz": e["hz"], "templateId": e["templateId"],
                       "name": e.get("v92_client_en") or e.get("v31_name_ko", ""),
                       "classification": e["classification"]})

    meta = {
        "target": "v31 stat blocks for all 218 v17-rostered templates",
        "roster_total": sum(z["roster_size"] for z in ns["zones"]),
        "out_of_roster_extras": extras,
        "confidence_note": "Baseline stat VALUES were not byte-diffed against v31 for all 218; baseline "
        "is a v31 port so MATCH is expected. Spot-check via datasheet-v92 NpcTemplate confirmed an EXACT "
        "match on sampled templates (hz13/1 Pigling: maxHp 88.4572514565471, level 3, atk 20, def 46.656 "
        "identical in baseline and v31 artifact). Recommend a full per-template stat diff during spec "
        "authoring; any drift found (patch-000 or manual fixes) should be re-flagged RESTORE.",
    }
    return {"meta": meta, "counts": dict(counts), "rows": rows}, extras


# --------------------------------------------------------------------------- #
# axis 5-8 : ECONOMY (shops + loot + gathering + dialogs + furniture)
# --------------------------------------------------------------------------- #
def classify_economy():
    result = {}
    decisions = []
    counts = defaultdict(int)

    # ---- SHOPS ----
    # Per-store diff of each v31 store (store_id -> BuyMenuList tabs -> BuyList
    # items) against the v92 baseline BuyMenuList/BuyList wiring.
    #   GAPFILL - store menu absent from the v92 baseline entirely.
    #   RESTORE - menu present but tab set or per-tab item lists differ from v31.
    #   MATCH   - baseline BuyMenuList/BuyList already equals the v31 store.
    sh = load("v31-shops.json")
    base_menus = base_buy_menus()
    base_lists = base_buy_lists()

    def diff_store(store):
        sid = str(store["store_id"])
        v31_tabs = [str(t["tab"]) for t in store["tabs"]]
        if sid not in base_menus:
            return "GAPFILL", (f"store menu {sid} absent from v92 BuyMenuList; "
                               f"wire {store['n_items']} v31 items across {len(v31_tabs)} tab(s)")
        diffs = []
        v92_tabs = base_menus[sid]
        if v31_tabs != v92_tabs:
            diffs.append(f"tab set v31={v31_tabs} vs v92={v92_tabs}")
        for t in v31_tabs:
            i31 = [str(it["itemId"]) for it in store["items"] if str(it["tab"]) == t]
            i92 = base_lists.get(t, [])
            if i31 != i92:
                diffs.append(f"list {t}: v31 {len(i31)} items vs v92 {len(i92)}")
        if not diffs:
            return "MATCH", f"v92 BuyMenuList/BuyList already equals v31 store {sid}"
        return "RESTORE", "; ".join(diffs)

    shop_rows = []
    for store in sh.get("stores", []):
        verdict, note = diff_store(store)
        counts[verdict] += 1
        shop_rows.append({
            "store": f"{store['hz']}/{store['tid']}", "store_id": store["store_id"],
            "npc": store.get("name", ""), "menu_type": store.get("menu_type", ""),
            "n_items": store["n_items"], "verdict": verdict,
            "provenance": "v31-gapfill", "note": note,
        })

    # out-of-registry extras (pre-seeded DECISION); now carry real store detail.
    extra_by_key = {f"{e['hz']}/{e['tid']}": e for e in sh.get("extras", {}).get("stores", [])}
    for key, title in [("213/1054", "Sandom (merchant, out of v17 registry)"),
                       ("64/8000", "Ellonia medal store (out of v17 registry)")]:
        e = extra_by_key.get(key, {})
        detail = (f"store_id={e['store_id']}, {e['n_items']} items" if e
                  else "store detail unavailable")
        shop_rows.append({"store": key, "store_id": e.get("store_id"),
                          "npc": e.get("name", ""), "menu_type": e.get("menu_type", ""),
                          "n_items": e.get("n_items"),
                          "verdict": "DECISION", "provenance": "v31-gapfill",
                          "note": f"{title}: real store but NPC absent from v17 registry ({detail})"})
        counts["DECISION"] += 1
        decisions.append({
            "axis": "economy/shops", "key": f"shop.{key}",
            "title": title,
            "options": ["A) REMOVE store (strict v17 registry)",
                        "B) keep store (real v31 content, playable)"],
            "recommendation": "B (keep) for 64/8000 Ellonia medal store if the medal economy is live; "
            "A (REMOVE) for 213/1054 Sandom unless the Sandom cluster is retained on the spawn axis.",
            "provenance": "v31-gapfill",
        })
    shop_meta = {
        "target": "7 real v31 stores for v17-registry NPCs, diffed per store against the v92 "
        "baseline BuyMenuList/BuyList; 2 out-of-registry stores held as DECISION extras",
        "registry_stores": len(sh.get("stores", [])),
        "extras_stores": len(sh.get("extras", {}).get("stores", [])),
        "service_only_npcs": sh.get("summary", {}).get("service_only_npcs"),
        "gaps": sh.get("gaps", {}),
    }
    result["shops"] = {"meta": shop_meta, "rows": shop_rows}

    # ---- LOOT ----
    loot = load("v31-loot.json")
    z13 = loot["zones"]["13"]
    base_c = base_compensation_templates(13)
    loot_rows = []
    for m in z13["mobs"]:
        tid = str(m["templateId"])
        if not m.get("in_v17_roster", True):
            continue
        if tid in base_c:
            verdict, note = "MATCH", f"baseline CCompensation has loot for {tid} ({base_c[tid]} bags); v31 port"
        else:
            verdict, note = "RESTORE", f"baseline CCompensation missing loot for {tid}; restore v31 drop table"
        counts[verdict] += 1
        loot_rows.append({"templateId": m["templateId"], "name": m.get("v17Name", ""),
                          "verdict": verdict, "provenance": "v31-gapfill", "note": note,
                          "n_dropbags_v31": len(m.get("dropBags", []))})
    loot_meta = {
        "target": "v31 zone-13 loot filtered to v17 roster (50 mobs)",
        "baseline_ccompensation_templates": len(base_c),
        "v31_mobs_with_loot": z13["mobs_with_loot_in_v17"],
    }
    result["loot"] = {"meta": loot_meta, "rows": loot_rows}

    # ---- GATHERING ----
    gath = load("v31-gathering.json")
    gz = gath["zones"]["13"]
    live = base_collection_territory("CollectionTerritory_13_ATW_Death_P.xml")
    inert = base_collection_territory("CollectionTerritory_13_ATW_P.xml")
    gath_rows = []
    # target = v31 placement (in v31's _ATW_P) landed into the LIVE _ATW_Death_P file
    for terr in gz.get("territories", []):
        tid = terr["territoryId"]
        for col in terr.get("collections", []):
            cid = col["collectionsId"]
            target_spawns = col.get("placedSpawns")
            base_n = (live or {}).get((tid, cid))
            if base_n is None:
                verdict, note = "RESTORE", (f"collection ({tid},{cid}) absent from LIVE "
                    f"_ATW_Death_P; place {target_spawns} v31 spawns")
            elif base_n == target_spawns:
                verdict, note = "MATCH", f"LIVE _ATW_Death_P already has {base_n} spawns for ({tid},{cid})"
            else:
                verdict, note = "RESTORE", (f"spawn count drift for ({tid},{cid}): "
                    f"LIVE={base_n} target(v31)={target_spawns}")
            counts[verdict] += 1
            gath_rows.append({"territoryId": tid, "collectionsId": cid, "typeId": col.get("typeId"),
                              "verdict": verdict, "provenance": "v31-gapfill", "note": note,
                              "target_spawns": target_spawns, "live_spawns": base_n})
    # inert _ATW_P baseline file -> REMOVE
    if inert is not None:
        gath_rows.append({"territoryId": "*", "collectionsId": "*", "typeId": None,
                          "verdict": "REMOVE", "provenance": "v92-keep",
                          "note": "inert baseline file CollectionTerritory_13_ATW_P.xml "
                          f"({len(inert)} collections) is superseded by _ATW_Death_P -> delete",
                          "target_spawns": None, "live_spawns": None})
        counts["REMOVE"] += 1
    gath_meta = {
        "target": "v31 gathering placement landed in LIVE CollectionTerritory_13_ATW_Death_P.xml",
        "inert_file_removed": "CollectionTerritory_13_ATW_P.xml",
        "patch000_note": "Account for patch-000 gathering fixes in the LIVE file; do not remove them "
        "blindly. Any LIVE spawn count exceeding the v31 target may be a patch-000 fix -> flag, don't overwrite.",
    }
    result["gathering"] = {"meta": gath_meta, "rows": gath_rows}

    # ---- DIALOGS ----
    dlg = load("v31-dialogs.json")
    dlg_rows = []
    dlg_gaps = []
    for zk, zv in dlg["zones"].items():
        for p in zv.get("present", []):
            counts["GATHER_DIALOG_PRESENT"] += 0  # not a verdict bucket
        present_n = len(zv.get("present", []))
        missing = zv.get("missing", [])
        for m in missing:
            dlg_gaps.append({"hz": int(zk), "templateId": m["templateId"],
                             "name": m.get("name", ""), "title": m.get("title", "")})
        if present_n:
            dlg_rows.append({"hz": int(zk), "villagers_with_dialog": present_n,
                             "villagers_missing_dialog": len(missing),
                             "verdict": "GAPFILL", "provenance": "v31-gapfill",
                             "note": f"restore v31 .condition dialogs for {present_n} rostered villagers; "
                             f"{len(missing)} coverage gaps (GAPFILL-missing)"})
            counts["GAPFILL"] += present_n
    dlg_meta = {
        "target": "v31 .condition dialogs for rostered villagers; coverage gaps = GAPFILL-missing",
        "coverage_gaps": dlg_gaps,
        "coverage_gap_count": len(dlg_gaps),
    }
    result["dialogs"] = {"meta": dlg_meta, "rows": dlg_rows}

    # ---- FURNITURE ----
    furn = load("v31-furniture.json")
    fz = furn["zones"].get("13", {})
    base_bf = base_bonfires(13)
    base_locs = {b[2] for b in base_bf}
    furn_rows = []
    for b in fz.get("bonfires", []):
        loc = b.get("loc", "")
        # baseline loc strings may differ in float precision; compare rounded
        def rnd(s):
            try:
                return tuple(round(float(x)) for x in s.split(","))
            except Exception:
                return s
        base_rnd = {rnd(x) for x in base_locs}
        if rnd(loc) in base_rnd:
            verdict, note = "MATCH", f"campfire at {loc} already in baseline BonfireData_13"
        else:
            verdict, note = "RESTORE", f"campfire at {loc} missing from baseline -> restore"
        counts[verdict] += 1
        furn_rows.append({"id": b.get("id"), "desc": b.get("desc", ""), "loc": loc,
                          "verdict": verdict, "provenance": "v31-gapfill", "note": note})
    furn_meta = {
        "target": "3 zone-13 campfires (v31 BonfireData)",
        "baseline_bonfire_count": len(base_bf),
        "v31_bonfire_count": fz.get("bonfire_count", 0),
    }
    result["furniture"] = {"meta": furn_meta, "rows": furn_rows}

    result["_counts"] = {k: v for k, v in counts.items() if not k.startswith("GATHER_")}
    return result, decisions


# --------------------------------------------------------------------------- #
# markdown rendering
# --------------------------------------------------------------------------- #
def w(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def md_quests(q):
    m = q["meta"]
    L = ["# Classification: Quests (axis 1)", "",
         f"Target: **{m['target']}**. Roster: {m['roster_size']} quests.", "",
         "Verdict counts (overall per quest): " +
         ", ".join(f"{k}={v}" for k, v in sorted(q["counts"].items())), "",
         f"- sentinel-disabled to re-enable: {m['sentinel_disabled_count']}",
         f"- v92==v31 disabled set identical: {m['v92_v31_disabled_set_identical']}",
         f"- TASKSEQ_DRIFT restoration-depth decisions: {m['tasksseq_drift_decisions']}", "",
         f"> Confidence basis: {m['confidence_basis']}", "",
         "## Per-quest attribute verdicts", "",
         "| gid | title | overall | enabled | prereq | accept | giver | receiver | story_grp | tasks |",
         "|-----|-------|---------|---------|--------|--------|-------|----------|-----------|-------|"]
    for r in q["rows"]:
        a = r["attributes"]
        def cell(k):
            return a[k]["verdict"] if k in a else "-"
        L.append(f"| {r['gid']} | {r['title'][:28]} | {r['overall']} | {cell('enabled_state')} | "
                 f"{cell('prereq_chain')} | {cell('accept_mechanism')} | {cell('giver')} | "
                 f"{cell('receiver')} | {cell('story_group')} | {cell('task_structure')} |")
    return "\n".join(L) + "\n"


def md_rewards(q):
    m = q["meta"]
    L = ["# Classification: Quest Rewards (axis 2)", "",
         f"Target: **{m['target']}**. Roster: {m['roster_size']} quests.", "",
         "Verdict counts: " + ", ".join(f"{k}={v}" for k, v in sorted(q["counts"].items())), "",
         f"- v17 reward items checked against v92 Item: {m['v17_reward_items_checked']}",
         f"- **BLOCKERS (missing from v92):** {m['v17_reward_items_missing_from_v92'] or 'none'}", "",
         f"> {m['note']}", "",
         "| gid | title | verdict | note |", "|-----|-------|---------|------|"]
    for r in q["rows"]:
        L.append(f"| {r['gid']} | {r['title'][:30]} | {r['verdict']} | {r['note'][:70]} |")
    return "\n".join(L) + "\n"


def md_spawns(q):
    m = q["meta"]
    L = ["# Classification: Spawns / Territories (axis 3)", "",
         f"Target: **{m['target']}**", "",
         "Verdict counts: " + ", ".join(f"{k}={v}" for k, v in sorted(q["counts"].items())), "",
         f"> {m['note']}", "",
         "## Per-HZ summary", "",
         "| hz | v17 grps | v31 grps | base grps | deleted-v17-only (RESTORE) | matched (MATCH) | v31-only (DECISION) | exact terr | near terr | near x-grp |",
         "|----|----------|----------|-----------|----------------------------|-----------------|---------------------|------------|-----------|-----------|"]
    for s in m["hz_summary"]:
        L.append(f"| {s['hz']} | {s['v17_groups']} | {s['v31_groups_present']} | {s['baseline_groups']} | "
                 f"{s['deleted_v17_only_RESTORE']} | {s['matched_MATCH']} | {s['v31_only_DECISION']} | "
                 f"{s['exact_terr']} | {s['near_terr']} | {s['near_cross_group_terr']} |")
    L += ["", "## Actionable rows (RESTORE / DECISION)", "",
          "| hz | group_id | desc | verdict | provenance | note |",
          "|----|----------|------|---------|------------|------|"]
    for r in q["rows"]:
        note = r.get("reconstruction_source") or r.get("note", "")
        L.append(f"| {r['hz']} | {r['group_id']} | {r['group_desc'][:24]} | {r['verdict']} | "
                 f"{r['provenance']} | {note[:60]} |")
    return "\n".join(L) + "\n"


def md_npcs(q):
    m = q["meta"]
    L = ["# Classification: NPC Stats / Behaviour (axis 4)", "",
         f"Target: **{m['target']}**. Roster total: {m['roster_total']}.", "",
         "Verdict counts: " + ", ".join(f"{k}={v}" for k, v in sorted(q["counts"].items())), "",
         f"> {m['confidence_note']}", "",
         "## Out-of-roster extras (informational; present v31+v92, absent v17)", "",
         "| hz | templateId | name | classification |", "|----|-----------|------|----------------|"]
    for e in m["out_of_roster_extras"]:
        L.append(f"| {e['hz']} | {e['templateId']} | {e['name']} | {e['classification']} |")
    L += ["", "## Per-template verdicts (RESTORE rows only; MATCH summarised in counts)", ""]
    restore = [r for r in q["rows"] if r["verdict"] != "MATCH"]
    if restore:
        L += ["| hz | templateId | name | verdict | note |", "|----|-----------|------|---------|------|"]
        for r in restore:
            L.append(f"| {r['hz']} | {r['npcTemplateId']} | {r['name']} | {r['verdict']} | {r['note'][:50]} |")
    else:
        L.append("_All 218 rostered templates classified MATCH (v31 port). No RESTORE rows._")
    return "\n".join(L) + "\n"


def md_economy(e):
    L = ["# Classification: Economy (axes 5-8: shops, loot, gathering, dialogs, furniture)", "",
         "Combined verdict counts: " + ", ".join(f"{k}={v}" for k, v in sorted(e["_counts"].items())), ""]
    # shops
    s = e["shops"]
    L += ["## Shops (axis 5)", "", f"Target: {s['meta']['target']}", "",
          f"Registry stores: {s['meta']['registry_stores']}, out-of-registry extras: "
          f"{s['meta']['extras_stores']}, service-only NPCs: {s['meta']['service_only_npcs']}", "",
          "| store | store_id | npc | menu | n_items | verdict | note |",
          "|-------|----------|-----|------|---------|---------|------|"]
    for r in s["rows"]:
        L.append(f"| {r['store']} | {r.get('store_id')} | {r.get('npc', '')} | "
                 f"{r.get('menu_type', '')} | {r.get('n_items')} | {r['verdict']} | {r['note'][:55]} |")
    # loot
    lo = e["loot"]
    L += ["", "## Loot (axis 6)", "", f"Target: {lo['meta']['target']}",
          f"baseline CCompensation templates: {lo['meta']['baseline_ccompensation_templates']}", "",
          "| templateId | name | verdict | note |", "|-----------|------|---------|------|"]
    for r in lo["rows"]:
        L.append(f"| {r['templateId']} | {r['name'][:20]} | {r['verdict']} | {r['note'][:55]} |")
    # gathering
    g = e["gathering"]
    L += ["", "## Gathering (axis 7)", "", f"Target: {g['meta']['target']}",
          f"> {g['meta']['patch000_note']}", "",
          "| territory | collection | typeId | verdict | target_spawns | live_spawns | note |",
          "|-----------|-----------|--------|---------|---------------|-------------|------|"]
    for r in g["rows"]:
        L.append(f"| {r['territoryId']} | {r['collectionsId']} | {r['typeId']} | {r['verdict']} | "
                 f"{r['target_spawns']} | {r['live_spawns']} | {r['note'][:45]} |")
    # dialogs
    d = e["dialogs"]
    L += ["", "## Dialogs (axis 8a)", "", f"Target: {d['meta']['target']}",
          f"coverage gaps (GAPFILL-missing): {d['meta']['coverage_gap_count']}", "",
          "| hz | with_dialog | missing | verdict | note |", "|----|-------------|---------|---------|------|"]
    for r in d["rows"]:
        L.append(f"| {r['hz']} | {r['villagers_with_dialog']} | {r['villagers_missing_dialog']} | "
                 f"{r['verdict']} | {r['note'][:45]} |")
    # furniture
    f = e["furniture"]
    L += ["", "## Furniture (axis 8b)", "", f"Target: {f['meta']['target']}",
          f"baseline bonfires: {f['meta']['baseline_bonfire_count']}, v31: {f['meta']['v31_bonfire_count']}", "",
          "| id | desc | verdict | note |", "|----|------|---------|------|"]
    for r in f["rows"]:
        L.append(f"| {r['id']} | {r['desc'][:24]} | {r['verdict']} | {r['note'][:50]} |")
    return "\n".join(L) + "\n"


def md_decisions(all_decisions):
    L = ["# DECISION rows (all axes)", "",
         f"Total decision rows: {len(all_decisions)}", "",
         "Each row records both options and a recommendation. None are chosen here; "
         "spec authoring resolves them.", ""]
    by_axis = defaultdict(list)
    for d in all_decisions:
        by_axis[d["axis"]].append(d)
    for axis in sorted(by_axis):
        L += [f"## {axis}", ""]
        for d in by_axis[axis]:
            L += [f"### {d['key']} - {d['title']}",
                  f"- Provenance: {d['provenance']}"]
            for opt in d["options"]:
                L.append(f"- {opt}")
            L += [f"- **Recommendation:** {d['recommendation']}", ""]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    # reward item existence: verified via datasheet-v92 MCP batch_lookup (74/74 found).
    reward_items_present = {str(i): True for i in [
        125,129,130,160,5132,6048,7100,7104,7108,7200,8007,8200,
        10537,10538,10539,10540,10541,10542,10543,10544,
        10593,10594,10595,10596,10597,10598,10599,10600,
        12401,12402,12403,12404,12405,12406,12407,12408,
        12409,12410,12411,12412,12413,12414,12415,12416,
        15605,15606,15608,15609,15611,15612,15667,15668,15670,15671,15673,15674,
        17701,17702,17703,17704,17705,17706,17707,17708,17709,17710,
        17711,17712,17713,17714,17715,17716,17717,17718]}

    all_decisions = []

    quests, qdec = classify_quests()
    all_decisions += qdec
    rewards, blockers = classify_quest_rewards(reward_items_present)
    spawns, sdec = classify_spawns()
    all_decisions += sdec
    npcs, extras = classify_npcs()
    economy, edec = classify_economy()
    all_decisions += edec

    # write json
    w(os.path.join(OUT, "classification-quests.json"), json.dumps(quests, ensure_ascii=False, indent=1))
    w(os.path.join(OUT, "classification-rewards.json"), json.dumps(rewards, ensure_ascii=False, indent=1))
    w(os.path.join(OUT, "classification-spawns.json"), json.dumps(spawns, ensure_ascii=False, indent=1))
    w(os.path.join(OUT, "classification-npcs.json"), json.dumps(npcs, ensure_ascii=False, indent=1))
    w(os.path.join(OUT, "classification-economy.json"), json.dumps(economy, ensure_ascii=False, indent=1))

    # write md
    w(os.path.join(OUT, "classification-quests.md"), md_quests(quests))
    w(os.path.join(OUT, "classification-rewards.md"), md_rewards(rewards))
    w(os.path.join(OUT, "classification-spawns.md"), md_spawns(spawns))
    w(os.path.join(OUT, "classification-npcs.md"), md_npcs(npcs))
    w(os.path.join(OUT, "classification-economy.md"), md_economy(economy))
    w(os.path.join(OUT, "decisions.md"), md_decisions(all_decisions))

    # console summary
    print("QUESTS   counts:", quests["counts"])
    print("REWARDS  counts:", rewards["counts"], "blockers:", blockers)
    print("SPAWNS   counts:", spawns["counts"])
    print("NPCS     counts:", npcs["counts"])
    print("ECONOMY  counts:", economy["_counts"])
    print("DECISIONS total:", len(all_decisions))
    print("dialog coverage gaps:", economy["dialogs"]["meta"]["coverage_gap_count"])


if __name__ == "__main__":
    main()
