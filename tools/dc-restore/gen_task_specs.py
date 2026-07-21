#!/usr/bin/env python
"""Reconstruct classic v17.11 quest task trees for the 27 task-drifted Island of
Dawn quests (patch 001, Stage 4A) and emit the DSL spec + reconstruction report.

Deterministic and re-runnable: sorted iteration, no timestamps, byte-stable
output. Reuses dclib for source resolution and the namespace-agnostic quest
parser. The v17.11 client Quest shards are the authoritative task source; live
v92 server .quest files are the fallback source and the update target.

Decision 9 (settled): DEEP v17 reconstruction for all 27 where possible; per-quest
fallback to the current v92 task structure ONLY where v17 reconstruction is
impossible or cannot be proven safe, each fallback documented.

The DSL task-authoring surface was extended (commits 2918a5c4 + 735abf92): task
`type` now writes the <이름> discriminator, `hasReward` writes <보상>, `removeTasks`
deletes tasks (with manual <다음Task> rewiring), `deliveryItems` authors the
CollectTask <전달아이템지정> objective, and an existing task is updated faithfully
and non-destructively (only the specified fields change; every unmodeled field and
the canonical element order are preserved). This lifts the old L1..L5 DSL capability
limits: type change, task delete, the reward flag, and the collect objective are all
now expressible.

What still bounds reconstruction is no longer the DSL but VERIFIABILITY. This
generator emits an op ONLY when the reconstruction is FABRICATED-BODY-FREE, i.e. it
is built entirely from:

  - clean tail removal (removeTasks) of v92 tasks the v17 flow never had,
  - <다음Task> rewiring and hasReward on the new completing (kept) task, and
  - in-place, non-destructive field upserts on EXISTING same-type tasks.

Such an op touches only fields whose before/after is fully determined, leaves every
other byte of every kept task intact, and can be proven correct by a structural
scratch-apply full-diff. It cannot crash the world server the way the earlier lossy
body rebuild did (quest 1390, 2026-07-18): there is no rebuilt body.

A reconstruction that must CREATE a task or RE-CREATE one under a new type builds a
fresh <Body> from YAML. The structural apply gate cannot prove that fabricated body
is server-load-safe (the loader rejects missing or mis-ordered elements: the L6
crash), and such reconstructions import v17-era monster / collection / NPC references
whose v92 spawn-state a structural diff cannot confirm. Those quests are therefore
held as FALLBACK pending a live-load validation pass (out of scope for the structural
gate), with the specific fabrication documented per quest. The classifier below is
written so that flipping the hold is a data change, not new code: once a
representative fabricated-body quest is live-validated, ALLOW_FABRICATED can be
enabled.

Usage:
  python reforged/tools/dc-restore/gen_task_specs.py
"""

import json
import sys
from pathlib import Path

TOOLDIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLDIR))
import dclib  # noqa: E402

REFORGED = dclib.reforged_dir()
DATA_DIR = REFORGED / "docs" / "plans" / "iod-alpha-content-loop" / "data"
SPEC_PATH = REFORGED / "specs" / "patches" / "001" / "06-iod-quest-tasks.yaml"
JSON_PATH = DATA_DIR / "task-reconstruction.json"
MD_PATH = DATA_DIR / "task-reconstruction.md"

# Hold fabricated-body (create / retype) reconstructions until a live-load pass
# validates a representative. Structural apply cannot prove a fabricated body is
# server-safe, so shipping one would risk the L6-class world-server crash.
ALLOW_FABRICATED = False

# The 27 task-drifted quests (decision 9 scope).
DRIFT_QUESTS = [
    1303, 1304, 1305, 1311, 1313, 1315, 1316, 1317, 1329, 1331, 1334, 1336,
    1341, 1346, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1382, 1384,
    1385, 1389, 1390,
]

# Korean <이름> discriminator -> DSL task type name.
TYPE_BY_KO = {
    "방문Task": "VisitTask",
    "사냥Task": "HuntTask",
    "사냥전달Task": "HuntAndDeliverTask",
    "사냥수집Task": "HuntAndCollectTask",
    "그룹사냥Task": "GroupHuntTask",
    "채집Task": "CollectTask",
    "채집완료Task": "CollectionCompleteTask",
    "아이템전달Task": "DeliverItemTask",
    "찔러준아이템전달Task": "DeliverInjectedItemTask",
    "PC이동Task": "MoveToPcTask",
    "PC이동분기Task": "MoveToPcBranchTask",
    "텔레포트Task": "TeleportTask",
    "오브젝트동작Task": "ObjectActionTask",
    "아이템사용Task": "UseItemTask",
    "소셜Task": "SocialTask",
    "낚시성공Task": "FishingSuccessTask",
    "미니게임완료Task": "MinigameCompleteTask",
    "분기Task": "BranchTask",
    "조건Task": "ConditionTask",
    "반복Task": "RepeatTask",
    "동영상재생Task": "PlayMovieTask",
    "변신Task": "TransformTask",
    "던전이벤트Task": "DungeonEventTask",
    "수호Task": "GuardianTask",
    "호위Task": "EscortTask",
}


def _strip(tag):
    return dclib.strip_ns(tag)


def _text(el):
    return (el.text or "").strip() if el is not None else ""


def _entries(wrapper):
    """Inner same-name entries of a nested wrapper (e.g. 완료시삽입아이템)."""
    if wrapper is None:
        return []
    name = _strip(wrapper.tag)
    return [c for c in wrapper if _strip(c.tag) == name]


def _child(el, name):
    for c in el:
        if _strip(c.tag) == name:
            return c
    return None


def _item_list(wrapper, id_tag, qty_tag):
    """[(id, qty)] from a nested item wrapper; qty '' when absent."""
    out = []
    for entry in _entries(wrapper):
        iid = _text(_child(entry, id_tag))
        if not iid:
            continue
        out.append((iid, _text(_child(entry, qty_tag))))
    return sorted(out)


def parse_tasks(text):
    """Ordered task list. Each task: dict(id, ko, type, target fields...)."""
    root = dclib.parse_root(text)
    tasks_el = None
    for c in root:
        if _strip(c.tag) == "Tasks":
            tasks_el = c
    out = []
    if tasks_el is None:
        return out
    for t in tasks_el:
        if _strip(t.tag) != "Task":
            continue
        tid = t.get("id")
        ko = ""
        body = None
        for c in t:
            if _strip(c.tag) == "Header":
                nm = _child(c, "이름")
                ko = _text(nm)
            elif _strip(c.tag) == "Body":
                body = c
        rec = {
            "id": int(tid) if tid and tid.isdigit() else tid,
            "ko": ko,
            "type": TYPE_BY_KO.get(ko, ko),
            "npcs": [], "monsters": [], "colls": [], "delivery_items": [],
            "target_npc": "", "deliver_qty": "", "flag": "", "movie": "",
            "area": "", "cond": "", "reward": "0",
            "insert_items": [], "delete_items": [], "multi_group": False,
        }
        if body is not None:
            _fill_body(rec, body)
        out.append(rec)
    return out


def _fill_body(rec, body):
    for c in body:
        tag = _strip(c.tag)
        if tag == "방문그룹":
            for entry in _entries(c):
                nid = _text(_child(entry, "NPCId"))
                if nid:
                    rec["npcs"].append(nid)
        elif tag == "몬스터지정":  # direct HuntTask monster block
            for entry in _entries(c):
                mid = _text(_child(entry, "몬스터Id"))
                if mid:
                    rec["monsters"].append((mid, _text(_child(entry, "사냥마리수"))))
        elif tag == "채집물지정":
            for entry in _entries(c):
                cid = _text(_child(entry, "콜렉션Id"))
                if cid:
                    rec["colls"].append(cid)
        elif tag == "전달아이템지정":
            rec["delivery_items"] = _item_list(c, "아이템Id", "전달수량")
        elif tag == "대상NPC지정":
            rec["target_npc"] = _text(c)
        elif tag == "전달수량":  # direct child (찔러준 delivery qty)
            rec["deliver_qty"] = _text(c)
        elif tag == "Flag아이템이름":
            rec["flag"] = _text(c)
        elif tag == "동영상Id":
            rec["movie"] = _text(c)
        elif tag == "목표지역":
            rec["area"] = _text(c)
        elif tag == "완료조건":
            for sub in c:
                rec["cond"] = _strip(sub.tag)
                break
        elif tag == "보상":
            rec["reward"] = _text(c) or "0"
        elif tag == "완료시삽입아이템":
            rec["insert_items"] = _item_list(c, "아이템Id", "아이템갯수")
        elif tag == "완료시삭제아이템":
            rec["delete_items"] = _item_list(c, "아이템Id", "아이템갯수")
    rec["npcs"] = sorted(rec["npcs"])
    rec["monsters"] = sorted(rec["monsters"])
    rec["colls"] = sorted(rec["colls"])
    if len(rec["npcs"]) > 1:
        rec["multi_group"] = True


def core_target(task):
    """The gameplay-identifying signature of a task for drift comparison."""
    ty = task["type"]
    if ty == "VisitTask":
        return ("visit", tuple(task["npcs"]))
    if ty == "HuntTask":
        return ("hunt", tuple(task["monsters"]))
    if ty == "CollectTask":
        return ("collect", tuple(task["colls"]),
                tuple(task["delivery_items"]), task["target_npc"])
    if ty in ("DeliverInjectedItemTask", "DeliverItemTask"):
        return ("deliver", task["flag"], task["target_npc"], task["deliver_qty"])
    if ty == "PlayMovieTask":
        return ("movie",)  # movie id is left to v92
    if ty == "MoveToPcTask":
        return ("move", task["area"])
    if ty == "GuardianTask":
        return ("guard", task["target_npc"])
    if ty == "ConditionTask":
        # Compare the condition SUBTYPE only. A version-drifted skill id inside a
        # matching learnSkill condition is deliberately ignored (kept at v92).
        return ("cond", task["cond"])
    return (ty,)


# ---------------------------------------------------------------------------
# In-place body emitter for a drifted same-type slot. Emits ONLY the changed
# gameplay field(s); the non-destructive upsert preserves everything else.
# ---------------------------------------------------------------------------

def drift_body(v17, v92):
    """YAML body dict re-authoring the drifted target of a same-type slot.

    Returns (body, notes). Only fields whose v17 value differs from v92 are
    emitted, so the diff is minimal and every untouched field is preserved.
    """
    ty = v17["type"]
    body, notes = {}, []
    if ty == "VisitTask":
        if v17["npcs"] and v17["npcs"] != v92["npcs"]:
            body["npcId"] = v17["npcs"][0]
            notes.append(f"visit npc -> {v17['npcs'][0]} (v17)")
    elif ty == "HuntTask":
        if v17["monsters"] and v17["monsters"] != v92["monsters"]:
            mid, kill = v17["monsters"][0]
            body["targetId"] = int(mid.split(",")[-1]) if "," in mid else int(mid)
            if kill:
                body["targetCount"] = int(kill)
            notes.append(f"hunt target -> {mid} x{kill} (v17)")
    elif ty == "CollectTask":
        if v17["colls"] and v17["colls"] != v92["colls"]:
            body["itemId"] = int(v17["colls"][0])
            notes.append(f"collection node -> {v17['colls'][0]} (v17)")
        if v17["delivery_items"] and v17["delivery_items"] != v92["delivery_items"]:
            body["deliveryItems"] = [
                {"itemId": int(iid), "quantity": int(qty) if qty else 1}
                for iid, qty in v17["delivery_items"]
            ]
            notes.append("hand-in items -> " + ", ".join(
                f"{iid}x{qty}" for iid, qty in v17["delivery_items"]) + " (v17)")
    elif ty in ("DeliverInjectedItemTask", "DeliverItemTask"):
        if v17["target_npc"] and v17["target_npc"] != v92["target_npc"]:
            body["targetNpc"] = v17["target_npc"]
            notes.append(f"delivery npc -> {v17['target_npc']} (v17)")
        if v17["flag"] and v17["flag"] != v92["flag"]:
            body["flagItemName"] = v17["flag"]
        if v17["deliver_qty"] and v17["deliver_qty"] != v92["deliver_qty"]:
            body["deliveryQuantity"] = int(v17["deliver_qty"])
    return body, notes


def classify(gid, v17, v92):
    """Return a verdict record for one quest under the fabricated-body-free gate."""
    n, m = len(v17), len(v92)
    rec = {
        "id": gid,
        "verdict": None,
        "reason": "",
        "v17_types": [t["ko"] for t in v17],
        "v92_types": [t["ko"] for t in v92],
        "ops": [],           # in-place task upsert blocks
        "remove_tasks": [],  # v92 task ids to delete
        "notes": [],
    }

    if n == 0 or m == 0:
        rec["verdict"] = "FALLBACK"
        rec["reason"] = "missing v17 or v92 task tree; nothing to reconstruct."
        return rec

    aligned = min(n, m)
    prefix_ok = all(v17[i]["type"] == v92[i]["type"] for i in range(aligned))

    # ----- Fabricated-body reconstructions: held pending live-load validation.
    fabricated = (n > m) or (not prefix_ok)
    if fabricated and not ALLOW_FABRICATED:
        if n > m:
            what = (f"v17 has {n} tasks vs v92 {m}; reconstruction must CREATE "
                    f"{n - m} task(s) with a fabricated <Body>")
        else:
            diffs = [f"slot{i + 1} v17={v17[i]['ko']} vs v92={v92[i]['ko']}"
                     for i in range(aligned) if v17[i]["type"] != v92[i]["type"]]
            what = ("task types diverge at aligned slots, so reconstruction must "
                    "remove-and-recreate under the v17 type (fabricated <Body>): "
                    + "; ".join(diffs))
        rec["verdict"] = "FALLBACK"
        rec["reason"] = (
            what + ". The DSL now supports this (type write, task create, "
            "removeTasks), but a fabricated body cannot be proven server-load-safe "
            "by the structural apply gate (the loader rejects missing or mis-ordered "
            "elements: the 2026-07-18 quest-1390 crash) and would import v17-era "
            "monster / collection / NPC refs of unverified v92 spawn-state while "
            "discarding deliberate v92 content evolution. Held for a live-load pass."
        )
        return rec

    # ----- Empty-condition guard: an empty v17 조건Task against a real v92 one.
    for i in range(aligned):
        if (v17[i]["type"] == "ConditionTask" and not v17[i]["cond"]
                and v92[i]["cond"]):
            rec["verdict"] = "FALLBACK"
            rec["reason"] = (
                f"v17 slot{i + 1} 조건Task is an empty placeholder (<완료조건 />) "
                f"while v92 encodes a real {v92[i]['cond']} condition; restoring the "
                "empty condition has unverifiable runtime behaviour, keep v92."
            )
            return rec

    # ----- Multi-target visit/hunt group the DSL cannot address a single field of.
    for i in range(n):
        if v17[i]["multi_group"]:
            rec["verdict"] = "FALLBACK"
            rec["reason"] = (
                f"v17 slot{i + 1} is a multi-target group the in-place upsert "
                "cannot re-author field-by-field; keep v92."
            )
            return rec

    remove_tasks = [v92[j]["id"] for j in range(n, m)]

    # ----- Orphaned-item guard: trimming must not strand a completion item that a
    # kept task injects and only a removed task deletes. The kept tasks retain
    # their v92 completion items (the in-place upsert is non-destructive), so the
    # guard reasons over the v92 (post-apply) item flow, not the v17 target.
    kept_inserts = {iid for i in range(n) for iid, _ in v92[i]["insert_items"]}
    kept_deletes = {iid for i in range(n) for iid, _ in v92[i]["delete_items"]}
    removed_deletes = {iid for j in range(n, m) for iid, _ in v92[j]["delete_items"]}
    orphan = kept_inserts & removed_deletes - kept_deletes
    if orphan:
        rec["verdict"] = "FALLBACK"
        rec["reason"] = (
            "trimming the surplus tail would strand completion item(s) "
            f"{', '.join(sorted(orphan))}: a kept task injects them but only a "
            "removed task deleted them, leaving an orphaned quest item. Keep v92."
        )
        return rec

    # ----- Build fabricated-body-free ops.
    drift_idx = [i for i in range(n)
                 if core_target(v17[i]) != core_target(v92[i])]
    completing = n - 1
    task_ops = {}  # taskId -> {nextTaskId?, hasReward?, body?}

    for i in drift_idx:
        body, notes = drift_body(v17[i], v92[i])
        if body:
            task_ops.setdefault(v17[i]["id"], {})["body"] = body
            rec["notes"].extend(notes)

    # Completing task: terminate the chain and carry the reward flag.
    comp_id = v17[completing]["id"]
    if remove_tasks and v92[completing]["id"] == comp_id:
        # The kept completing task currently pointed into the removed tail.
        task_ops.setdefault(comp_id, {})["nextTaskId"] = 0
    if v92[completing]["reward"] != "1":
        task_ops.setdefault(comp_id, {})["hasReward"] = True

    if not task_ops and not remove_tasks:
        rec["verdict"] = "FALLBACK"
        rec["reason"] = (
            "v92 already matches the v17 task structure and targets (it differs "
            "only in v92-added task dialogue or a version-drifted condition skill id "
            "that v17 also intends); reconstructing would strip content with no "
            "faithful gain. Keep v92."
        )
        return rec

    # Emit ops in task-id order for determinism. Every task op carries its
    # `type` (required by the DSL); the value is the unchanged same-type slot
    # type, so writing it re-affirms the existing <이름> without a type change.
    types = {v17[i]["id"]: v17[i]["type"] for i in range(n)}
    for tid in sorted(task_ops):
        op = {"taskId": tid, "type": types[tid]}
        op.update(task_ops[tid])
        rec["ops"].append(op)
    rec["remove_tasks"] = remove_tasks
    rec["verdict"] = "DEEP_OK"
    if remove_tasks:
        rec["notes"].insert(0,
            f"trim v92-added tail tasks {remove_tasks}; task {comp_id} becomes the "
            "completing task (보상=1).")
    return rec


def _yaml_body(body, indent):
    L = []
    for k, v in body.items():
        if k == "deliveryItems":
            L.append(f"{indent}{k}:")
            for entry in v:
                L.append(f"{indent}  - itemId: {entry['itemId']}")
                L.append(f"{indent}    quantity: {entry['quantity']}")
        elif isinstance(v, bool):
            L.append(f"{indent}{k}: {'true' if v else 'false'}")
        elif isinstance(v, int):
            L.append(f"{indent}{k}: {v}")
        else:
            L.append(f'{indent}{k}: "{v}"')
    return L


def render_yaml(records):
    L = []
    L.append("spec:")
    L.append('  version: "1.0"')
    L.append("  schema: v92")
    L.append("")
    L.append("# IoD patch 001 quest task reconstruction (Stage 4A).")
    L.append("# Task TARGET (authoritative): v17.11 client Quest shards.")
    L.append("# Fallback source and update target: live v92 server .quest files.")
    L.append("#")
    L.append("# Decision 9: DEEP v17 reconstruction where it can be proven correct;")
    L.append("#   per-quest fallback to the current v92 task structure otherwise.")
    L.append("#   Fallback quests get NO op here and are documented in")
    L.append("#   docs/plans/iod-alpha-content-loop/data/task-reconstruction.md.")
    L.append("#")
    L.append("# The DSL task surface now supports type write, task delete")
    L.append("#   (removeTasks), the reward flag (hasReward), and the CollectTask")
    L.append("#   hand-in objective (deliveryItems); an existing task is updated")
    L.append("#   non-destructively (only named fields change, order preserved).")
    L.append("#")
    L.append("# This spec emits ONLY fabricated-body-free reconstructions: clean")
    L.append("#   tail removal, <다음Task> rewiring + hasReward on the new completing")
    L.append("#   task, and in-place field upserts on existing same-type tasks. Each")
    L.append("#   such change is fully determined and provable by a structural diff;")
    L.append("#   none rebuilds a <Body>, so none can repeat the L6 world crash.")
    L.append("#   Reconstructions that must CREATE or RE-TYPE a task (fabricated body)")
    L.append("#   are held FALLBACK pending a live-load validation pass.")
    L.append("#")
    L.append("# Client-sync entity: Quest (task trees). No questDialogs upsert is")
    L.append("#   required: no reconstructed task points at a dialog node absent from")
    L.append("#   live v92 (kept tasks retain their v92 dialogue refs; trimmed tail")
    L.append("#   tasks are removed whole).")
    L.append("#")
    L.append("# Zone 13 (huntingZoneId=13). Generated by tools/dc-restore/gen_task_specs.py")

    authored = [r for r in records if r["ops"] or r["remove_tasks"]]
    fallback = [r for r in records if not (r["ops"] or r["remove_tasks"])]

    L.append("")
    L.append("quests:")
    L.append("  update:")
    for r in authored:
        L.append(f"    # {r['id']}: {r['verdict']}. {r['reason'] or 'v17 task flow restored.'}")
        for note in r["notes"]:
            L.append(f"    #   note: {note}")
        L.append(f"    - id: {r['id']}")
        L.append("      changes:")
        if r["remove_tasks"]:
            L.append(f"        removeTasks: [{', '.join(str(x) for x in r['remove_tasks'])}]")
        if r["ops"]:
            L.append("        tasks:")
            for op in r["ops"]:
                L.append(f"          - taskId: {op['taskId']}")
                L.append(f"            type: {op['type']}")
                if "nextTaskId" in op:
                    L.append(f"            nextTaskId: {op['nextTaskId']}")
                if "hasReward" in op:
                    L.append(f"            hasReward: {'true' if op['hasReward'] else 'false'}")
                if "body" in op:
                    L.append("            body:")
                    L.extend(_yaml_body(op["body"], "              "))

    L.append("")
    L.append("# Fallback quests (no op; v92 task structure retained):")
    for r in fallback:
        L.append(f"#   {r['id']} [{r['verdict']}]: {r['reason']}")
    return "\n".join(L) + "\n"


def render_md(records):
    counts = {"DEEP_OK": 0, "PARTIAL": 0, "FALLBACK": 0}
    for r in records:
        counts[r["verdict"]] += 1
    L = []
    L.append("# IoD Patch 001 Quest Task Reconstruction (Stage 4A)")
    L.append("")
    L.append("Authoritative task source: v17.11 client Quest shards "
             "(`old_client_dc/Quest`). Fallback source and update target: live v92 "
             "server `.quest` files. Generated by `tools/dc-restore/gen_task_specs.py`; "
             "deterministic, re-run to refresh.")
    L.append("")
    L.append("Decision 9: DEEP v17 reconstruction where it can be proven correct; "
             "per-quest fallback to the v92 task structure otherwise.")
    L.append("")
    L.append(f"Verdicts across {len(records)} quests: "
             f"**DEEP_OK {counts['DEEP_OK']}**, **PARTIAL {counts['PARTIAL']}**, "
             f"**FALLBACK {counts['FALLBACK']}**.")
    L.append("")
    L.append("## What the DSL now supports, and what still bounds reconstruction")
    L.append("")
    L.append("The task-authoring surface was extended (commits 2918a5c4 + 735abf92). "
             "The former L1..L5 capability limits are lifted:")
    L.append("")
    L.append("- **Type write.** A task `type` now writes the `<이름>` discriminator. A "
             "type change is a remove-and-recreate (`removeTasks` the old id, add a "
             "fresh entry with the new `type`).")
    L.append("- **Task delete.** `removeTasks` deletes tasks; the predecessor's "
             "`nextTaskId` is rewired in the same spec.")
    L.append("- **Reward flag.** `hasReward: true` writes `<보상>1`; set it on whichever "
             "task becomes the completing task.")
    L.append("- **Collect objective.** `deliveryItems` authors the CollectTask "
             "`<전달아이템지정>` hand-in objective.")
    L.append("- **Faithful update.** An existing task is updated non-destructively: only "
             "the named fields change; every unmodeled field and the canonical element "
             "order are preserved.")
    L.append("")
    L.append("What now bounds reconstruction is **verifiability**, not capability. This "
             "generator emits an op only when the reconstruction is "
             "**fabricated-body-free**: built entirely from clean tail removal, "
             "`nextTaskId`/`hasReward` on the kept completing task, and in-place field "
             "upserts on existing same-type tasks. Every such change is fully determined "
             "and provable by a structural scratch-apply full-diff, and none rebuilds a "
             "`<Body>`, so none can repeat the 2026-07-18 quest-1390 world crash.")
    L.append("")
    L.append("A reconstruction that must **create** a task or **re-type** one builds a "
             "fresh `<Body>` from YAML. The structural apply gate cannot prove that body "
             "is server-load-safe (the loader rejects missing or mis-ordered elements), "
             "and such a reconstruction imports v17-era monster / collection / NPC "
             "references whose v92 spawn-state a structural diff cannot confirm, while "
             "discarding deliberate v92 content evolution. Those quests are held "
             "**FALLBACK** pending a live-load validation pass (`ALLOW_FABRICATED` in the "
             "generator gates the flip).")
    L.append("")
    L.append("## Per-quest verdicts")
    L.append("")
    L.append("| gid | verdict | v17 types | v92 types | ops | reason / notes |")
    L.append("|-----|---------|-----------|-----------|-----|----------------|")
    for r in records:
        v17s = " > ".join(t.replace("Task", "") for t in r["v17_types"]) or "-"
        v92s = " > ".join(t.replace("Task", "") for t in r["v92_types"]) or "-"
        parts = []
        if r["remove_tasks"]:
            parts.append(f"del{r['remove_tasks']}")
        for o in r["ops"]:
            bits = []
            if "nextTaskId" in o:
                bits.append(f"next={o['nextTaskId']}")
            if "hasReward" in o:
                bits.append("reward=1")
            if "body" in o:
                bits.append("+".join(o["body"].keys()))
            parts.append(f"t{o['taskId']}:{'/'.join(bits)}")
        opsum = ", ".join(parts) or "-"
        note = r["reason"]
        if r["notes"]:
            note = (note + " " if note else "") + " ".join(r["notes"])
        note = note.replace("|", "\\|")
        L.append(f"| {r['id']} | {r['verdict']} | {v17s} | {v92s} | {opsum} | {note} |")
    L.append("")
    L.append("## Dialog linkage")
    L.append("")
    L.append("No `questDialogs` upserts are emitted. Reconstructed quests keep their "
             "existing v92 tasks (and dialogue refs) and only remove v92-added tail "
             "tasks or adjust a determined field, so no task references a dialog node "
             "absent from live v92.")
    L.append("")
    L.append("## Reconstruction detail")
    L.append("")
    for r in records:
        L.append(f"### {r['id']} [{r['verdict']}]")
        L.append("")
        L.append(f"- v17 tasks: {' > '.join(r['v17_types']) or '(none)'}")
        L.append(f"- v92 tasks: {' > '.join(r['v92_types']) or '(none)'}")
        if r["reason"]:
            L.append(f"- reason: {r['reason']}")
        if r["remove_tasks"]:
            L.append(f"- remove tasks: {r['remove_tasks']}")
        for note in r["notes"]:
            L.append(f"- note: {note}")
        if r["ops"]:
            L.append("- task upserts:")
            for o in r["ops"]:
                bits = []
                if "nextTaskId" in o:
                    bits.append(f"nextTaskId={o['nextTaskId']}")
                if "hasReward" in o:
                    bits.append("hasReward=true")
                if "body" in o:
                    bits.append("body(" + ", ".join(
                        f"{k}={v}" for k, v in o["body"].items()) + ")")
                L.append(f"  - task {o['taskId']}: {'; '.join(bits)}")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    refs = dclib.load_references()
    client_dc = Path(refs["old_client_dc"])
    v92_quest_dir = Path(refs["server_datasheet"]) / "QuestData"

    shards = dclib.index_quest_shards_by_id(client_dc / "Quest")

    records = []
    for gid in DRIFT_QUESTS:
        cpath = shards.get(gid)
        vpath = v92_quest_dir / f"{gid:06d}.quest"
        v17 = parse_tasks(dclib.read_text(cpath)) if cpath else []
        v92 = parse_tasks(dclib.read_text(vpath)) if vpath.exists() else []
        records.append(classify(gid, v17, v92))

    records.sort(key=lambda r: r["id"])

    has_ops = any(r["ops"] or r["remove_tasks"] for r in records)
    if has_ops:
        SPEC_PATH.write_text(render_yaml(records), encoding="utf-8")
    elif SPEC_PATH.exists():
        SPEC_PATH.unlink()
    JSON_PATH.write_text(
        json.dumps({"quests": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    MD_PATH.write_text(render_md(records), encoding="utf-8")

    counts = {"DEEP_OK": 0, "PARTIAL": 0, "FALLBACK": 0}
    op_count = 0
    for r in records:
        counts[r["verdict"]] += 1
        if r["ops"] or r["remove_tasks"]:
            op_count += 1
    print(f"wrote {SPEC_PATH.name if has_ops else '(no spec)'}, "
          f"{JSON_PATH.name}, {MD_PATH.name}")
    print(f"verdicts: {counts}; quests with ops: {op_count}")


if __name__ == "__main__":
    main()
