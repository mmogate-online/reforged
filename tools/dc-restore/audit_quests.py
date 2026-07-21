"""dc-restore audit_quests: deterministic quest-difference flagger for the Island.

Compares every Island-of-Dawn quest (global-id band 1300-1399, unioned across
sources) across CLIENT (design reference), V31 (easy-restore source) and V92
(current truth, read from the WORKING TREE so authored/tuned content is what is
judged). Each quest is reduced to a set of deterministic flags; nothing is
"fixed" or guessed. The report groups the actionable quests into a worklist and
the JSON mirrors every field for a future --from-audit consumer.

Quest attribution is the 1300-1399 band (all keyed Quest번호 hz=13). The --zones
set selects which per-zone TerritoryData files are scanned for NPC-spawn checks;
NPC references carry their own hz, so a giver "213,1021" is checked against
TerritoryData_213 specifically (npcTemplateId is unique only within a zone).

Read-only: writes only --out and --json; never touches a datasheet.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import dclib
from dclib import (
    ISLAND_ZONES,
    Sources,
    comp_reward_key,
    comp_summary,
    find_file_ci,
    find_zone_file,
    index_client_comp,
    index_client_quest_dialogs,
    index_comp_file,
    load_island_quests,
    load_references,
    npc_template_ids,
    parse_pair,
    qgl_ids_from_text,
    read_text,
    strsheet_quest_ids,
    territory_spawns,
    v31_dialog_exists,
    v92_dialog_exists,
)

# Severity tiers.
BLOCKING, DRIFT, INFO, CLEAN = "blocking", "drift", "info", "clean"
_RANK = {BLOCKING: 3, DRIFT: 2, INFO: 1, CLEAN: 0}

# Task gameplay fields compared for TASKREF_DRIFT, and their identity projection.
_TASK_FIELDS = ["monsters", "collections", "deliver_items", "deliver_direct",
                "visits", "target_npc", "dungeon"]


def _identity_proj(field: str, val):
    """Reference-identity projection of a task field (ignores counts/chances)."""
    if field in ("monsters", "deliver_items", "deliver_direct"):
        return sorted(x[0] for x in val)
    return val


class SpawnIndex:
    """npcTemplateId sets per (server, zone); loads zone files on demand."""

    def __init__(self, sources: Sources):
        self.s = sources
        self._cache: dict[tuple[str, int], set[int]] = {}

    def templates(self, which: str, zone: int) -> set[int]:
        key = (which, zone)
        if key not in self._cache:
            root = self.s.v92 if which == "v92" else self.s.v31
            f = find_zone_file(root, "TerritoryData", zone)
            ids = set()
            if f:
                for e in territory_spawns(read_text(f)):
                    if isinstance(e["npcTemplateId"], int):
                        ids.add(e["npcTemplateId"])
            self._cache[key] = ids
        return self._cache[key]

    def is_spawned(self, which: str, ref: str) -> bool:
        pair = parse_pair(ref)
        if not pair:
            return False
        hz, tid = pair
        return tid in self.templates(which, hz)


def _comp_index(sources: Sources, root, hz: int) -> dict[int, dict | None]:
    f = find_file_ci(root / "CompensationData", f"QuestCompensationData_{hz}.xml")
    return index_comp_file(read_text(f)) if f else {}


def audit_quest(gid: int, models: dict, comp: dict, spawn: SpawnIndex,
                qgl_v92: set[int], client_qd: set, sources: Sources,
                v92_title_ids: set[int], client_titles: dict[int, str]) -> dict:
    cli = models["client"].get(gid)
    v31 = models["v31"].get(gid)
    v92 = models["v92"].get(gid)
    anchor = v92 or v31 or cli
    hz, local = anchor["hz"], anchor["local"]

    disabled = bool(v92 and v92["sentinel"])
    active = bool(v92 and not v92["sentinel"])
    flags: list[str] = []
    detail: dict = {}

    def add(flag):
        if flag not in flags:
            flags.append(flag)

    # --- prerequisite / sentinel ---
    if disabled:
        add("SENTINEL_DISABLED")
    if cli and v92 and not v92["sentinel"]:
        if sorted(cli["prereqs"]) != sorted(v92["prereqs"]):
            add("PREREQ_DRIFT")
            v31_pre = sorted(v31["prereqs"]) if v31 else None
            detail["prereq"] = {
                "client": cli["prereqs"], "v31": v31_pre, "v92": v92["prereqs"],
                "v31_agrees_client": (v31_pre == sorted(cli["prereqs"])) if v31 else None,
            }

    # --- header drifts (client vs v92) ---
    if cli and v92:
        if cli["quest_type"] != v92["quest_type"]:
            add("TYPE_DRIFT"); detail["type"] = {"client": cli["quest_type"], "v92": v92["quest_type"]}
        if cli["repeat"] != v92["repeat"]:
            add("REPEAT_DRIFT"); detail["repeat"] = {"client": cli["repeat"], "v92": v92["repeat"]}
        if cli["story_group"] != v92["story_group"]:
            add("STORYGROUP_DRIFT")
            detail["story_group"] = {"client": cli["story_group"], "v92": v92["story_group"]}
        if cli["min_level"] != v92["min_level"] or cli["max_level"] != v92["max_level"]:
            add("LEVELBAND_DRIFT")
            detail["levelband"] = {
                "client": [cli["min_level"], cli["max_level"]],
                "v92": [v92["min_level"], v92["max_level"]],
            }

    # --- task references (client vs v92, structural per task id) ---
    # v31's value is recorded too: when v31 agrees with the client but v92
    # differs, the drift is a v92 regression with a clear fix (mechanical); when
    # v31 sides with v92 or all three differ, it needs a human call.
    if cli and v92:
        taskref = []
        v31_tasks = v31["tasks"] if v31 else {}
        all_tids = sorted(set(cli["tasks"]) | set(v92["tasks"]),
                          key=lambda x: (isinstance(x, str), x))
        for tid in all_tids:
            ct, t9 = cli["tasks"].get(tid), v92["tasks"].get(tid)
            if ct is None or t9 is None:
                taskref.append({"task": tid, "field": "task-presence", "kind": "ref",
                                "client": "present" if ct else "absent",
                                "v92": "present" if t9 else "absent",
                                "v31_agrees_client": None})
                continue
            t3 = v31_tasks.get(tid)
            for field in _TASK_FIELDS:
                cv, v9 = ct[field], t9[field]
                if cv == v9:
                    continue
                kind = "ref" if _identity_proj(field, cv) != _identity_proj(field, v9) else "count"
                v3 = t3[field] if t3 is not None else None
                if t3 is None:
                    agrees = None
                elif kind == "ref":
                    agrees = _identity_proj(field, v3) == _identity_proj(field, cv)
                else:
                    agrees = v3 == cv
                taskref.append({"task": tid, "field": field, "kind": kind,
                                "client": cv, "v31": v3, "v92": v9,
                                "v31_agrees_client": agrees})
        if taskref:
            add("TASKREF_DRIFT")
            detail["taskref"] = taskref

    # --- compensation ---
    ccomp = comp["client"].get(gid)
    v31c = comp["v31"].get(hz, {}).get(gid) if hz is not None else None
    v92c = comp["v92"].get(hz, {}).get(gid) if hz is not None else None
    detail["comp"] = {"client": comp_summary(ccomp), "v31": comp_summary(v31c),
                      "v92": comp_summary(v92c)}
    if v92c is None and (ccomp is not None or v31c is not None):
        add("COMP_EMPTY")
    if ccomp is not None and v31c is not None and comp_reward_key(ccomp) != comp_reward_key(v31c):
        add("COMP_DRIFT")

    # --- NPC spawns (v92 working tree; v31 agreement noted) ---
    giver = anchor.get("giver", "")
    if giver:
        if not spawn.is_spawned("v92", giver):
            add("GIVER_UNSPAWNED")
            detail["giver"] = {"ref": giver, "v92_spawned": False,
                               "v31_spawned": spawn.is_spawned("v31", giver)}
    targets = sorted(set((v92 or anchor).get("target_npcs", [])))
    unspawned = [r for r in targets if not spawn.is_spawned("v92", r)]
    if unspawned:
        add("TARGET_UNSPAWNED")
        detail["targets_unspawned"] = [
            {"ref": r, "v31_spawned": spawn.is_spawned("v31", r)} for r in unspawned]

    # --- story-group registration ---
    story = (v92 or {}).get("story_group") or (cli or {}).get("story_group") or ""
    if story and gid not in qgl_v92:
        add("GROUPLIST_UNREGISTERED")
        detail["story_group_id"] = story

    # --- dialog + strings (v92 lacks what client has) ---
    if cli and hz is not None and local is not None:
        if (hz, local) in client_qd and not v92_dialog_exists(sources.v92 / "QuestDialog", hz, local):
            add("DIALOG_MISSING")
        if (gid * 1000 + 1) in client_titles and (gid * 1000 + 1) not in v92_title_ids:
            add("STRINGS_MISSING")

    if not flags:
        flags = ["CLEAN"]

    # Reference-identity task drift split by whether it looks like a fixable v92
    # regression (v31 sides with the client) or a genuine conflict.
    id_taskref = [t for t in detail.get("taskref", []) if t["kind"] == "ref"]
    taskref_regression = any(t.get("v31_agrees_client") is True for t in id_taskref)
    taskref_conflict = any(t.get("v31_agrees_client") is not True for t in id_taskref)
    comp_needs_decision = "COMP_EMPTY" in flags and "COMP_DRIFT" in flags
    prereq_conflict = "PREREQ_DRIFT" in flags and not (
        detail.get("prereq", {}).get("v31_agrees_client") is True)

    # --- severity ---
    def flag_sev(f):
        if f == "TASKREF_DRIFT":
            return BLOCKING if id_taskref else INFO
        if f == "COMP_EMPTY":
            return BLOCKING if active else DRIFT
        return {
            "SENTINEL_DISABLED": BLOCKING, "GIVER_UNSPAWNED": BLOCKING, "TARGET_UNSPAWNED": BLOCKING,
            "PREREQ_DRIFT": DRIFT, "COMP_DRIFT": DRIFT,
            "GROUPLIST_UNREGISTERED": DRIFT, "DIALOG_MISSING": DRIFT, "STRINGS_MISSING": DRIFT,
            "STORYGROUP_DRIFT": INFO, "LEVELBAND_DRIFT": INFO, "TYPE_DRIFT": INFO, "REPEAT_DRIFT": INFO,
            "CLEAN": CLEAN,
        }.get(f, INFO)

    severity = max((flag_sev(f) for f in flags), key=lambda s: _RANK[s])
    return {
        "gid": gid, "hz": hz, "local": local,
        "title": client_titles.get(gid * 1000 + 1, ""),
        "present": {"client": cli is not None, "v31": v31 is not None, "v92": v92 is not None},
        "disabled": disabled, "active": active,
        "flags": flags, "severity": severity, "detail": detail,
        "signals": {
            "taskref_regression": taskref_regression,
            "taskref_conflict": taskref_conflict,
            "comp_needs_decision": comp_needs_decision,
            "prereq_conflict": prereq_conflict,
        },
    }


# ---------------------------------------------------------------------------
# Prereq chain graph (client-era) and worklist bucketing
# ---------------------------------------------------------------------------

def build_chain(models: dict, scope: list[int]) -> dict:
    """Client-era predecessor/successor edges among in-scope quests."""
    scope_set = set(scope)
    preds: dict[int, list[int]] = {g: [] for g in scope}
    succs: dict[int, list[int]] = {g: [] for g in scope}
    for gid in scope:
        cli = models["client"].get(gid) or models["v92"].get(gid)
        if not cli:
            continue
        for ref in cli["prereqs"]:
            pair = parse_pair(ref)
            if not pair:
                continue
            pg = pair[0] * 100 + pair[1]
            if pg in scope_set:
                preds[gid].append(pg)
                succs.setdefault(pg, []).append(gid)
    return {"preds": preds, "succs": succs}


def bucket_of(row: dict, chain: dict, spine: set[int]) -> str | None:
    """Primary worklist bucket A/B/C/D, or None for clean/info-only quests.

    Priority: spawn authoring (B) is the hardest gate; a disabled quest wired
    into the prereq chain re-enables as a chain (C); a disabled isolated quest
    or an active quest with only a deterministic fix is mechanical (A); an
    active quest whose remaining issue is a source disagreement needs a human
    decision (D). COMP_DRIFT is near-universal, so it tags quests everywhere
    rather than forcing them all into D; it only decides the bucket for an
    otherwise-active quest with no structural action.
    """
    flags = set(row["flags"])
    sig = row["signals"]
    gid = row["gid"]
    # COMP_DRIFT with a filled v92 comp and plain header drifts (level/type/story
    # group) are informational: recorded, but not on their own a unit of work.
    actionable = (flags & {
        "SENTINEL_DISABLED", "COMP_EMPTY", "GIVER_UNSPAWNED", "TARGET_UNSPAWNED",
        "PREREQ_DRIFT", "GROUPLIST_UNREGISTERED", "DIALOG_MISSING", "STRINGS_MISSING",
    }) or any(t["kind"] == "ref" for t in row["detail"].get("taskref", []))
    if not actionable:
        return None
    if flags & {"GIVER_UNSPAWNED", "TARGET_UNSPAWNED"}:
        return "B"
    linked = bool(chain["preds"].get(gid) or chain["succs"].get(gid))
    if row["disabled"]:
        return "C" if linked else "A"
    # Active quest: needs a human decision only when a source disagreement remains
    # (comp restore with divergent sources, prereq/taskref where v31 sides against
    # the client). A drift the v31 source resolves toward the client is mechanical.
    conflict = sig["comp_needs_decision"] or sig["prereq_conflict"] or sig["taskref_conflict"]
    return "D" if conflict else "A"


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

ALL_FLAGS = [
    "SENTINEL_DISABLED", "PREREQ_DRIFT", "TASKREF_DRIFT", "COMP_EMPTY", "COMP_DRIFT",
    "GIVER_UNSPAWNED", "TARGET_UNSPAWNED", "GROUPLIST_UNREGISTERED", "STORYGROUP_DRIFT",
    "DIALOG_MISSING", "STRINGS_MISSING", "LEVELBAND_DRIFT", "TYPE_DRIFT", "REPEAT_DRIFT", "CLEAN",
]
BUCKET_NAME = {
    "A": "Mechanically fixable now (sentinel/comp/taskref, giver spawned)",
    "B": "Needs spawn authoring (giver or task target not spawned in v92)",
    "C": "Chain-entangled (prereq graph links the story spine)",
    "D": "Conflicts needing a human decision (comp/prereq disagreement)",
}


def _short_flags(row: dict) -> str:
    order = {f: i for i, f in enumerate(ALL_FLAGS)}
    fl = sorted((f for f in row["flags"] if f != "CLEAN"), key=lambda f: order.get(f, 99))
    return ", ".join(fl) if fl else "CLEAN"


def render(rows: list[dict], buckets: dict, chain: dict, zones: list[int]) -> str:
    L: list[str] = []
    w = L.append
    from collections import Counter
    flag_counts = Counter(f for r in rows for f in r["flags"])
    sev_counts = Counter(r["severity"] for r in rows)

    w("# Island Quest Audit (Iteration 2)")
    w("")
    w(f"Generated {time.strftime('%Y-%m-%d %H:%M:%S')} by tools/dc-restore/audit_quests.py")
    w("")
    w("Sources compared per quest: CLIENT (design reference), V31 (easy-restore "
      "source), V92 (current truth, read from the working tree). Quest scope is the "
      "global-id band 1300-1399 unioned across sources; NPC-spawn checks scan the "
      f"island TerritoryData for zones {','.join(map(str, zones))}. V92 is the working "
      "tree, so authored spawns and restored comp/prereq are reflected as-is.")
    w("")
    w("Old-client-vs-v92 numeric drift (kill counts, level bands) is expected from "
      "years of rebalancing; the high-signal items are reference-identity drift "
      "(collection/item/NPC ids), unspawned givers, empty comp on active quests, and "
      "the sentinel-disabled set. Severity reflects that.")
    w("")

    w("## Summary")
    w("")
    w(f"- Quests in scope: {len(rows)}")
    w(f"- By severity: blocking {sev_counts[BLOCKING]}, drift {sev_counts[DRIFT]}, "
      f"info {sev_counts[INFO]}, clean {sev_counts[CLEAN]}")
    w("")
    w("| Flag | Count |")
    w("|------|-------|")
    for f in ALL_FLAGS:
        if flag_counts.get(f):
            w(f"| {f} | {flag_counts[f]} |")
    w("")

    # Highest-signal mechanical fixes: a task reference where v31 sides with the
    # client and v92 alone diverges (the 콜렉션Id-style bug class).
    regressions = []
    for r in rows:
        for t in r["detail"].get("taskref", []):
            if t["kind"] == "ref" and t.get("v31_agrees_client") is True:
                regressions.append((r["gid"], r["title"], t))
    w("## Reference-identity regressions (v31 + client agree, v92 diverges)")
    w("")
    if regressions:
        w("These are the clearest mechanical fixes: a gameplay reference where both "
          "the client and the v31 server hold one value and only v92 differs.")
        w("")
        w("| Quest | EN title | task | field | client=v31 | v92 |")
        w("|-------|----------|------|-------|-----------|-----|")
        for gid, title, t in regressions:
            w(f"| {gid} | {title} | {t['task']} | {t['field']} | {t['client']} | {t['v92']} |")
    else:
        w("None: no task reference has v31 agreeing with the client against v92.")
    w("")

    w("## Worklist")
    w("")
    for b in ("A", "B", "C", "D"):
        ids = buckets.get(b, [])
        w(f"### Group {b}: {BUCKET_NAME[b]} ({len(ids)})")
        if not ids:
            w("- (none)")
            w("")
            continue
        for gid in ids:
            r = next(x for x in rows if x["gid"] == gid)
            extra = ""
            if b == "C":
                preds = chain["preds"].get(gid, [])
                succs = chain["succs"].get(gid, [])
                extra = f"  [pred {preds or '-'} / succ {succs or '-'}]"
            w(f"- {gid} {r['title']}: {_short_flags(r)}{extra}")
        w("")

    w("## Per-quest flags")
    w("")
    w("| Quest | EN title | v92 state | severity | flags |")
    w("|-------|----------|-----------|----------|-------|")
    for r in sorted(rows, key=lambda x: (-_RANK[x["severity"]], x["gid"])):
        if not r["present"]["v92"]:
            state = "absent"
        elif r["disabled"]:
            state = "DISABLED"
        else:
            state = "active"
        w(f"| {r['gid']} | {r['title']} | {state} | {r['severity']} | {_short_flags(r)} |")
    w("")

    # Blocking detail dump (the actionable specifics).
    w("## Blocking / drift detail")
    w("")
    for r in sorted(rows, key=lambda x: (-_RANK[x["severity"]], x["gid"])):
        if r["severity"] in (INFO, CLEAN):
            continue
        w(f"### {r['gid']} {r['title']} ({r['severity']})")
        d = r["detail"]
        if "SENTINEL_DISABLED" in r["flags"]:
            w("- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.")
        if "PREREQ_DRIFT" in r["flags"]:
            pd = d["prereq"]
            agree = " (v31 agrees client: v92 regression)" if pd.get("v31_agrees_client") else ""
            w(f"- PREREQ_DRIFT: client {pd['client']} | v31 {pd['v31']} | v92 {pd['v92']}{agree}")
        if "TASKREF_DRIFT" in r["flags"]:
            for t in d.get("taskref", []):
                tag = ""
                if t["kind"] == "ref" and t.get("v31_agrees_client") is True:
                    tag = "  <-- v31 agrees client (v92 regression, mechanical fix)"
                v31part = f" | v31 {t['v31']}" if "v31" in t else ""
                w(f"- TASKREF_DRIFT[{t['kind']}] task {t['task']} {t['field']}: "
                  f"client {t['client']}{v31part} | v92 {t['v92']}{tag}")
        if "COMP_EMPTY" in r["flags"]:
            w(f"- COMP_EMPTY: v92 reward stub/absent; client={d['comp']['client']} "
              f"v31={d['comp']['v31']}")
        if "COMP_DRIFT" in r["flags"]:
            w(f"- COMP_DRIFT: client {d['comp']['client']} vs v31 {d['comp']['v31']} "
              "(no winner picked)")
        if "GIVER_UNSPAWNED" in r["flags"]:
            g = d["giver"]
            w(f"- GIVER_UNSPAWNED: giver {g['ref']} not spawned in v92 "
              f"(v31 spawned: {g['v31_spawned']})")
        if "TARGET_UNSPAWNED" in r["flags"]:
            for t in d["targets_unspawned"]:
                w(f"- TARGET_UNSPAWNED: {t['ref']} not spawned in v92 "
                  f"(v31 spawned: {t['v31_spawned']})")
        if "GROUPLIST_UNREGISTERED" in r["flags"]:
            w(f"- GROUPLIST_UNREGISTERED: story group {d['story_group_id']} but no "
              "v92 QuestGroupList entry.")
        if "STORYGROUP_DRIFT" in r["flags"]:
            w(f"- STORYGROUP_DRIFT: client {d['story_group']['client'] or '(none)'} vs "
              f"v92 {d['story_group']['v92'] or '(none)'}")
        if "DIALOG_MISSING" in r["flags"]:
            w("- DIALOG_MISSING: v92 lacks the QuestDialog file the client has.")
        if "STRINGS_MISSING" in r["flags"]:
            w("- STRINGS_MISSING: v92 StrSheet_Quest lacks the client title string.")
        w("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Island quest-difference audit.")
    parser.add_argument("--zones", default=",".join(map(str, ISLAND_ZONES)),
                        help="Comma-separated island zones for spawn scans")
    parser.add_argument("--out", required=True, help="Output markdown report path")
    parser.add_argument("--json", help="Output JSON path (mirrors every field)")
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
    print("Loading quest models and indices ...")
    models = load_island_quests(sources)
    scope = sorted(set(models["client"]) | set(models["v31"]) | set(models["v92"]))

    # Compensation indices.
    hzs = sorted({(models["v92"].get(g) or models["v31"].get(g) or models["client"][g])["hz"]
                  for g in scope})
    comp = {
        "client": index_client_comp(sources.old_client / "QuestCompensationData"),
        "v31": {hz: _comp_index(sources, sources.v31, hz) for hz in hzs if hz is not None},
        "v92": {hz: _comp_index(sources, sources.v92, hz) for hz in hzs if hz is not None},
    }

    spawn = SpawnIndex(sources)
    qgl_v92 = qgl_ids_from_text(read_text(find_file_ci(sources.v92, "QuestGroupList.xml")))
    client_qd = index_client_quest_dialogs(sources.old_client / "QuestDialog")

    # Title strings: aggregate client StrSheet_Quest shards; v92 single file.
    client_titles: dict[int, str] = {}
    cq_dir = sources.old_client / "StrSheet_Quest"
    if cq_dir.is_dir():
        for entry in cq_dir.glob("*.xml"):
            client_titles.update(strsheet_quest_ids(read_text(entry)))
    v92_title_ids = set(strsheet_quest_ids(read_text(sources.v92 / "StrSheet_Quest.xml")))

    rows = [audit_quest(gid, models, comp, spawn, qgl_v92, client_qd, sources,
                        v92_title_ids, client_titles) for gid in scope]

    # Chain graph + worklist buckets.
    spine = {g for g in scope if (models["v92"].get(g) or models["client"].get(g) or {}).get("story_group")}
    chain = build_chain(models, scope)
    buckets: dict[str, list[int]] = {"A": [], "B": [], "C": [], "D": []}
    for r in rows:
        b = bucket_of(r, chain, spine)
        if b:
            buckets[b].append(r["gid"])

    report = render(rows, buckets, chain, zones)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if args.json:
        Path(args.json).write_text(
            json.dumps({
                "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "zones": zones, "scope": scope,
                "rows": rows, "buckets": buckets,
                "chain": {"preds": chain["preds"], "succs": chain["succs"]},
            }, indent=2, ensure_ascii=False, default=list),
            encoding="utf-8",
        )

    dt = time.monotonic() - t0
    print(f"Done in {dt:.1f}s -> {out_path}")
    if args.json:
        print(f"JSON -> {args.json}")
    from collections import Counter
    fc = Counter(f for r in rows for f in r["flags"])
    print("Flag counts:", dict(fc))
    print("Bucket sizes:", {b: len(v) for b, v in buckets.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
