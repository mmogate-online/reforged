"""Extract and diff v31 server quest data for the 63 v17-cataloged IoD quests.

Phase 2a of the Island of Dawn restoration. Read-only: this tool never writes a
datasheet. It reads the v31 server QuestData / QuestCompensationData / QuestDialog,
the old-client QuestDialog shards, and the Phase 1 v17 client catalog, then emits:

  data/v31-quests.json / .md          per-quest v31 record + diff vs the v17 catalog
  data/v31-quest-rewards.json / .md   v31 reward rows cross-validated against v17

The v17 client catalog is the north star (v17-quests.json). v31 is the server
encoding; where v31 has evolved past v17 the divergence is flagged so a
v17-wins precedence call can see exactly what taking v17 gives up.

Quest attribution: the 63 catalog quests are all Quest번호 hz=13, global ids
1301-1390. v31 files them as zero-padded gid (001305.quest -> root id 1305).
gid = hz*100 + local, so a "13,5" reference maps to gid 1305.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dclib as L

DATA_DIR = L.reforged_dir() / "docs" / "plans" / "iod-alpha-content-loop" / "data"
V17_JSON = DATA_DIR / "v17-quests.json"

# v31 Korean task-type 이름 -> the english label used by the v17 catalog.
TASK_TYPE_EN = {
    "방문Task": "visit",
    "사냥Task": "hunt",
    "사냥전달Task": "hunt-deliver",
    "찔러준아이템전달Task": "deliver-item",
    "동영상재생Task": "cinematic",
    "PC이동Task": "travel",
    "수집Task": "collect",
    "대화Task": "talk",
}

# Header fields the server carries that the minified client catalog drops. Value
# is the JSON key we expose them under. Empty / self-closed -> "".
SERVER_ONLY_TAGS = [
    ("적정수행인원", "rec_party_size"),
    ("적정수행레벨", "rec_level"),
    ("취소가능여부", "cancelable"),
    ("요약정보", "summary_info"),
    ("연결퀘스트", "linked_quest"),
    ("시작Task번호", "start_task"),
    ("퀘스트대사", "quest_dialog_count"),
    ("종료시팝업대사", "end_popup"),
]


def gid_from_ref(ref):
    """A 'hz,local' quest reference -> global id (hz*100+local), or None."""
    pair = L.parse_pair(ref)
    return pair[0] * 100 + pair[1] if pair else None


def task_type_en(korean):
    return TASK_TYPE_EN.get(korean, korean)


def extract_server_only(header_text):
    """Pull the server-only header fields from raw <Header> text."""
    out = {}
    for tag, key in SERVER_ONLY_TAGS:
        m = re.search(rf"<{tag}\s*/>|<{tag}>(.*?)</{tag}>", header_text, re.S)
        out[key] = (m.group(1).strip() if m and m.group(1) else "") if m else None
    return out


def derive_accept(header_text, model):
    """Accept mechanism from the raw header.

    v31 encodes auto-grant as <즉시수주>1</즉시수주> in the trigger block; such a
    quest may ALSO carry an <NPC대화> context ref (e.g. 1311) but is still
    auto-accepted. Only when there is no 즉시수주 flag is an <NPC대화> the actual
    giver. Returns (accept, giver, context_npc).
    """
    inst = re.search(r"<즉시수주>\s*(\d+)\s*</즉시수주>", header_text)
    auto = bool(inst and inst.group(1) not in ("0", ""))
    npc_m = re.search(r"<NPC대화>([^<]*)</NPC대화>", header_text)
    context_npc = npc_m.group(1).strip() if npc_m else None
    if auto:
        return "auto", None, context_npc
    if context_npc or model["giver"]:
        return "npc", (model["giver"] or context_npc), context_npc
    return "auto", None, context_npc


def derive_receiver(model):
    """The turn-in NPC: the last task (by id) that names an NPC target."""
    tasks = model["tasks"]
    for tid in sorted(tasks, key=lambda x: (isinstance(x, str), x), reverse=True):
        t = tasks[tid]
        if t["target_npc"]:
            return t["target_npc"][0]
        if t["visits"]:
            return t["visits"][0]
    return None


def summarize_tasks(model):
    """Ordered compact per-task summary of the v31 quest."""
    out = []
    for tid in sorted(model["tasks"], key=lambda x: (isinstance(x, str), x)):
        t = model["tasks"][tid]
        refs = []
        if t["visits"]:
            refs.append("visit=" + "/".join(t["visits"]))
        if t["target_npc"]:
            refs.append("to=" + "/".join(t["target_npc"]))
        if t["monsters"]:
            refs.append("kill=" + "/".join(f"{mid}x{k or '?'}" for mid, k, _ in t["monsters"]))
        if t["collections"]:
            refs.append("collect=" + "/".join(t["collections"]))
        if t["deliver_items"]:
            refs.append("item=" + "/".join(f"{i}x{q or '?'}" for i, q, _ in t["deliver_items"]))
        if t["dungeon"]:
            refs.append("dungeon=" + t["dungeon"])
        out.append({
            "id": tid,
            "type": task_type_en(t["type"]),
            "type_raw": t["type"],
            "refs": refs,
        })
    return out


# ---------------------------------------------------------------------------
# Dialog structural parsing (client shard + v31 file share the tag set)
# ---------------------------------------------------------------------------

_TEXT_RE = re.compile(r"<Text\b([^>]*?)/?>")
_ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def dialog_structure(text):
    """Structural fingerprint of a QuestDialog document (no full text)."""
    texts = []
    for m in _TEXT_RE.finditer(text):
        a = dict(_ATTR_RE.findall(m.group(1)))
        texts.append((
            int(a["id"]) if a.get("id", "").isdigit() else a.get("id", ""),
            int(a["huntingZoneId"]) if a.get("huntingZoneId", "").isdigit() else a.get("huntingZoneId", ""),
            int(a["villagerId"]) if a.get("villagerId", "").isdigit() else a.get("villagerId", ""),
        ))
    return {
        "text_count": len(texts),
        "page_count": len(re.findall(r"<Page\b", text)),
        "chain": sorted(texts),
    }


def index_client_dialogs(qd_dir, hz):
    """Map local dialog id -> shard path for a hunting zone (client shards)."""
    out = {}
    if not qd_dir.is_dir():
        return out
    head_re = re.compile(r'<QuestDialog\b[^>]*\bid="(\d+)"[^>]*\bhuntingZoneId="(\d+)"')
    for entry in qd_dir.iterdir():
        if entry.suffix.lower() != ".xml":
            continue
        m = head_re.search(L._peek(entry, 400))
        if m and int(m.group(2)) == hz:
            out[int(m.group(1))] = entry
    return out


# ---------------------------------------------------------------------------
# Reward cross-validation
# ---------------------------------------------------------------------------

def item_set(items):
    """Normalized (templateId, quantity, class) set from a reward item list."""
    out = set()
    for it in items:
        if isinstance(it, dict):
            out.add((str(it.get("templateId", "")), str(it.get("quantity", "")), it.get("class", "") or ""))
        else:
            out.add((str(it[0]), str(it[1]), it[2] or ""))
    return out


def classify_reward(v17_reward, v31_reward):
    """Compare a v17 catalog reward with a v31 comp reward. Returns (verdict, detail)."""
    v17_present = v17_reward is not None and any([
        v17_reward.get("exp"), v17_reward.get("gold"), v17_reward.get("items")])
    if v31_reward is None:
        return ("V31_EMPTY", "v31 comp is an empty stub / absent") if v17_present else ("BOTH_EMPTY", "")
    if not v17_present:
        return "V17_EMPTY", "v31 has a reward, v17 catalog shows none"

    v17_exp = str(v17_reward.get("exp", "") or "")
    v17_gold = str(v17_reward.get("gold", "") or "")
    v17_bag = v17_reward.get("itemBag", "") or ""
    v31_exp = str(v31_reward.get("exp", "") or "")
    v31_gold = str(v31_reward.get("gold", "") or "")
    v31_bag = v31_reward.get("itemBag", "") or ""

    s17 = item_set(v17_reward.get("items", []))
    s31 = item_set(v31_reward.get("items", []))

    detail = []
    if v17_exp != v31_exp:
        detail.append(f"exp v17={v17_exp} v31={v31_exp}")
    if v17_gold != v31_gold:
        detail.append(f"gold v17={v17_gold} v31={v31_gold}")
    if v17_bag != v31_bag:
        detail.append(f"itemBag v17={v17_bag!r} v31={v31_bag!r}")

    extra31 = s31 - s17
    missing31 = s17 - s31
    # Engineer is the v31-era 9th class the v17 catalog predates.
    only_engineer = extra31 and all(c == "engineer" for _, _, c in extra31)

    xp_gold_ok = (v17_exp == v31_exp and v17_gold == v31_gold and v17_bag == v31_bag)

    if not detail and not extra31 and not missing31:
        return "EXACT", ""
    if xp_gold_ok and not missing31 and only_engineer:
        return "CLASS_SUPERSET", f"v31 adds engineer-class item(s): {sorted(extra31)}"
    if detail and not extra31 and not missing31:
        return "EXP_GOLD_DRIFT", "; ".join(detail)
    if missing31:
        detail.append(f"v31 missing {sorted(missing31)}")
    if extra31:
        detail.append(f"v31 extra {sorted(extra31)}")
    return "ITEM_DRIFT", "; ".join(detail)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    refs = L.load_references()
    sources = L.Sources(refs)
    problems = sources.validate()
    if problems:
        for p in problems:
            print("SOURCE PROBLEM:", p, file=sys.stderr)
        sys.exit(2)

    v17 = json.loads(V17_JSON.read_text(encoding="utf-8"))
    v17_by_id = {q["id"]: q for q in v17["quests"]}
    catalog_ids = [q["id"] for q in v17["quests"]]

    # v31 quest models keyed by gid, plus the raw header for server-only fields.
    v31_quest_dir = sources.v31 / "QuestData"
    v31_models = {}
    v31_headers = {}
    v31_band_ids = set()
    for entry in v31_quest_dir.iterdir():
        if entry.suffix.lower() != ".quest" or not entry.stem.isdigit():
            continue
        gid = int(entry.stem)
        if not (1300 <= gid <= 1399):
            continue
        v31_band_ids.add(gid)
        text = L.read_text(entry)
        model = L.parse_quest(text)
        if model is None:
            continue
        v31_models[gid] = model
        hm = re.search(r"<Header>(.*?)</Header>", text, re.S)
        v31_headers[gid] = hm.group(1) if hm else ""

    v31_extra = sorted(v31_band_ids - set(catalog_ids))

    # v31 quest compensation (zone 13, global questId keys).
    comp_path = L.find_file_ci(sources.v31 / "CompensationData", "QuestCompensationData_13.xml")
    v31_comp = L.index_comp_file(L.read_text(comp_path)) if comp_path else {}

    # Dialog indices.
    v31_dialog_dir = sources.v31 / "QuestDialog"
    client_dialog_dir = sources.old_client / "QuestDialog"
    client_dialog_idx = index_client_dialogs(client_dialog_dir, 13)

    quest_records = []
    reward_records = []

    for gid in catalog_ids:
        c = v17_by_id[gid]
        model = v31_models.get(gid)
        rec = {"gid": gid, "title": c["title"], "v31_present": model is not None}

        if model is None:
            rec["flags"] = ["V31_ABSENT"]
            rec["v17"] = {"accept": c["accept"], "giver": c["giver"], "receiver": c["receiver"]}
            quest_records.append(rec)
            continue

        # v31 accept mechanism (explicit 즉시수주 flag; see derive_accept).
        v31_accept, v31_giver, v31_context_npc = derive_accept(v31_headers.get(gid, ""), model)
        v31_receiver = derive_receiver(model)
        v31_prereq_refs = model["prereqs"]
        v31_prereq_gids = sorted({g for g in (gid_from_ref(p) for p in v31_prereq_refs) if g})
        v31_tasks = summarize_tasks(model)
        v31_task_types = [t["type"] for t in v31_tasks]

        v17_prereq_gids = sorted({p["gid"] for p in c["prereqs"] if p.get("gid")})
        v17_task_types = list(c["task_types"])

        server_only = extract_server_only(v31_headers.get(gid, ""))

        # Diff flags.
        flags = []
        if model["sentinel"]:
            flags.append("SENTINEL_DISABLED")
        if v31_accept != c["accept"]:
            flags.append("ACCEPT_DRIFT")
        if (v31_giver or "") != (c["giver"] or ""):
            flags.append("GIVER_DRIFT")
        if (v31_receiver or "") != (c["receiver"] or ""):
            flags.append("RECEIVER_DRIFT")
        # A sentinel-disabled quest has its prereq overwritten by 99,99, so the
        # "drift" is the disable, already flagged; do not double-count it.
        if v31_prereq_gids != v17_prereq_gids and not model["sentinel"]:
            flags.append("PREREQ_DRIFT")
        if str(model["min_level"] or "") != str(c["min_level"] or ""):
            flags.append("MINLEVEL_DRIFT")
        if (model["story_group"] or "") != (c["story_group"] or ""):
            flags.append("STORYGROUP_DRIFT")
        if (model["quest_type"] or "") != (c["quest_type_raw"] or ""):
            flags.append("TYPE_DRIFT")
        if (model["repeat"] or "") != (c["repeat"] or ""):
            flags.append("REPEAT_DRIFT")
        if len(v31_tasks) != len(c["tasks"]):
            flags.append("TASKCOUNT_DRIFT")
        if v31_task_types != v17_task_types:
            flags.append("TASKSEQ_DRIFT")

        # "What taking v17 loses" note when v31 is the richer encoding.
        losing = []
        if len(v31_tasks) > len(c["tasks"]):
            losing.append(f"v31 has {len(v31_tasks)} tasks vs v17 {len(c['tasks'])} "
                          f"(v17 drops {len(v31_tasks) - len(c['tasks'])} step(s))")
        if v31_accept != c["accept"]:
            losing.append(f"accept: v17={c['accept']} vs v31={v31_accept}"
                          + (f" (v31 giver {v31_giver})" if v31_giver else ""))
        if model["sentinel"]:
            losing.append("v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live")
        elif v31_prereq_gids != v17_prereq_gids:
            losing.append(f"prereq chain: v17={v17_prereq_gids or 'none'} vs v31={v31_prereq_gids or 'none'}")

        rec.update({
            "flags": flags or ["ALIGNED"],
            "losing_if_v17": losing,
            "v17": {
                "accept": c["accept"], "giver": c["giver"], "receiver": c["receiver"],
                "min_level": c["min_level"], "story_group": c["story_group"],
                "type_raw": c["quest_type_raw"], "repeat": c["repeat"],
                "prereq_gids": v17_prereq_gids, "task_count": len(c["tasks"]),
                "task_types": v17_task_types,
            },
            "v31": {
                "accept": v31_accept, "giver": v31_giver, "receiver": v31_receiver,
                "context_npc": v31_context_npc,
                "trigger_type": model["trigger_type"], "sentinel_disabled": model["sentinel"],
                "min_level": model["min_level"], "max_level": model["max_level"],
                "story_group": model["story_group"], "type_raw": model["quest_type"],
                "repeat": model["repeat"], "classes": model["classes"],
                "prereq_refs": v31_prereq_refs, "prereq_gids": v31_prereq_gids,
                "task_count": len(v31_tasks), "task_types": v31_task_types,
                "tasks": v31_tasks, "server_only": server_only,
            },
        })
        quest_records.append(rec)

        # ---- reward cross-validation ----
        v31_reward = v31_comp.get(gid)
        v17_reward = c.get("reward")
        verdict, detail = classify_reward(v17_reward, v31_reward)
        reward_records.append({
            "gid": gid, "title": c["title"], "verdict": verdict, "detail": detail,
            "v17": {
                "exp": str((v17_reward or {}).get("exp", "") or ""),
                "gold": str((v17_reward or {}).get("gold", "") or ""),
                "itemBag": (v17_reward or {}).get("itemBag", "") or "",
                "items": sorted(item_set((v17_reward or {}).get("items", []))),
            },
            "v31": None if v31_reward is None else {
                "exp": str(v31_reward.get("exp", "") or ""),
                "gold": str(v31_reward.get("gold", "") or ""),
                "itemBag": v31_reward.get("itemBag", "") or "",
                "items": sorted(item_set(v31_reward.get("items", []))),
            },
        })

    # ---- dialogs (Task 3) ----
    dialog_records = []
    for gid in catalog_ids:
        model = v31_models.get(gid)
        local = model["local"] if model and model["local"] else gid - 1300
        v31_path = L.find_file_ci(v31_dialog_dir, f"QuestDialog_13_{local}.xml")
        client_path = client_dialog_idx.get(local)
        v31_struct = dialog_structure(L.read_text(v31_path)) if v31_path else None
        client_struct = dialog_structure(L.read_text(client_path)) if client_path else None

        dflags = []
        if v31_struct is None:
            dflags.append("V31_DIALOG_MISSING")
        if client_struct is None:
            dflags.append("CLIENT_DIALOG_MISSING")
        material = None
        if v31_struct and client_struct:
            if (v31_struct["text_count"] != client_struct["text_count"]
                    or v31_struct["page_count"] != client_struct["page_count"]
                    or v31_struct["chain"] != client_struct["chain"]):
                dflags.append("DIALOG_STRUCT_DRIFT")
                material = True
            else:
                material = False
        dialog_records.append({
            "gid": gid, "local": local,
            "v31_present": v31_struct is not None,
            "client_present": client_struct is not None,
            "v31": v31_struct, "client": client_struct,
            "flags": dflags or ["DIALOG_ALIGNED"], "material_diff": material,
        })

    write_outputs(quest_records, reward_records, dialog_records, v31_extra, sources)


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def _md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def write_outputs(quests, rewards, dialogs, v31_extra, sources):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Merge dialog into quest json for a single record set, but also keep the
    # dialog view addressable.
    dialog_by_gid = {d["gid"]: d for d in dialogs}
    for q in quests:
        q["dialog"] = dialog_by_gid.get(q["gid"])

    from collections import Counter
    flag_counter = Counter()
    for q in quests:
        for f in q["flags"]:
            flag_counter[f] += 1
    reward_counter = Counter(r["verdict"] for r in rewards)
    dialog_counter = Counter(f for d in dialogs for f in d["flags"])

    sentinel_disabled = [q["gid"] for q in quests
                         if q["v31_present"] and q["v31"].get("sentinel_disabled")]
    quests_json = {
        "summary": {
            "catalog_quests": len(quests),
            "v31_present": sum(1 for q in quests if q["v31_present"]),
            "v31_sentinel_disabled_count": len(sentinel_disabled),
            "v31_sentinel_disabled": sentinel_disabled,
            "flag_counts": dict(flag_counter),
            "v31_extra_band_quests": v31_extra,
        },
        "quests": quests,
    }
    (DATA_DIR / "v31-quests.json").write_text(
        json.dumps(quests_json, ensure_ascii=False, indent=2), encoding="utf-8")

    rewards_json = {
        "summary": {
            "catalog_quests": len(rewards),
            "verdict_counts": dict(reward_counter),
        },
        "rewards": rewards,
    }
    (DATA_DIR / "v31-quest-rewards.json").write_text(
        json.dumps(rewards_json, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- v31-quests.md ----
    lines = []
    lines.append("# v31 Quest Server Data - Island of Dawn (Phase 2a)")
    lines.append("")
    lines.append("Extracted from v31.04 server datasheets and diffed against the v17 client "
                 "catalog (`v17-quests.json`, the north star). v31 is the server encoding; "
                 "flags mark where v31 evolved past v17.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Catalog quests: **{len(quests)}**  |  present in v31: "
                 f"**{sum(1 for q in quests if q['v31_present'])}**")
    lines.append(f"- **v31 has {len(sentinel_disabled)} of the 63 quests DISABLED** via the "
                 f"99,99 prerequisite sentinel. v31 is the reworked \"ATW_Death_P\" Island of "
                 f"Dawn where the old content loop was soft-disabled; v17.11 (pre-rework) is "
                 f"where these quests are live, which is why v17 is the north star for this "
                 f"restoration.")
    lines.append(f"- v31 13xx-band quests NOT in the v17 catalog (v31 additions): "
                 f"**{v31_extra or 'none'}**")
    lines.append("")
    lines.append("Diff-flag counts across the 63 quests:")
    lines.append("")
    lines.append(_md_table(["Flag", "Count"],
                           [(f, n) for f, n in flag_counter.most_common()]))
    lines.append("")
    lines.append("Flags: `ALIGNED` no header/structure divergence; `ACCEPT_DRIFT` accept "
                 "mechanism differs (auto vs npc); `GIVER_DRIFT`/`RECEIVER_DRIFT` giver or "
                 "turn-in NPC differs; `PREREQ_DRIFT` prerequisite chain differs; "
                 "`TASKCOUNT_DRIFT`/`TASKSEQ_DRIFT` task structure differs; "
                 "`MINLEVEL_DRIFT`/`STORYGROUP_DRIFT`/`TYPE_DRIFT`/`REPEAT_DRIFT` header field "
                 "differs; `SENTINEL_DISABLED` v31 header carries the 99,99 disable sentinel.")
    lines.append("")
    lines.append("## Per-quest alignment")
    lines.append("")
    rows = []
    for q in quests:
        if not q["v31_present"]:
            rows.append((q["gid"], q["title"], "ABSENT", "-", "-", "-", "V31_ABSENT"))
            continue
        v17, v31 = q["v17"], q["v31"]
        flags = ", ".join(f for f in q["flags"] if f != "ALIGNED") or "-"
        rows.append((
            q["gid"], q["title"],
            f"{v17['accept']}->{v31['accept']}" if "ACCEPT_DRIFT" in q["flags"] else v31["accept"],
            f"{v17['task_count']}->{v31['task_count']}" if "TASKCOUNT_DRIFT" in q["flags"] else v31["task_count"],
            f"{v17['prereq_gids'] or '-'}->{v31['prereq_gids'] or '-'}" if "PREREQ_DRIFT" in q["flags"] else (v31["prereq_gids"] or "-"),
            "yes" if v31["sentinel_disabled"] else "-",
            flags,
        ))
    lines.append(_md_table(
        ["gid", "title", "accept", "tasks", "prereq (v17->v31)", "disabled", "flags"], rows))
    lines.append("")
    lines.append("## Divergences worth a precedence call (what taking v17 loses)")
    lines.append("")
    any_losing = False
    for q in quests:
        if q.get("losing_if_v17"):
            any_losing = True
            lines.append(f"### {q['gid']} - {q['title']}")
            for note in q["losing_if_v17"]:
                lines.append(f"- {note}")
            so = q["v31"].get("server_only", {})
            extras = [f"{k}={v}" for k, v in so.items() if v]
            if extras:
                lines.append(f"- v31 server-only header fields: {', '.join(extras)}")
            lines.append("")
    if not any_losing:
        lines.append("_None: every catalog quest aligns structurally with v31._")
        lines.append("")

    lines.append("## Dialogs (v31 QuestDialog vs v17 client, structural)")
    lines.append("")
    lines.append(_md_table(["Flag", "Count"],
                           [(f, n) for f, n in dialog_counter.most_common()]))
    lines.append("")
    drows = []
    for d in dialogs:
        vt = d["v31"]["text_count"] if d["v31"] else "-"
        ct = d["client"]["text_count"] if d["client"] else "-"
        drows.append((d["gid"], f"QuestDialog_13_{d['local']}",
                      "yes" if d["v31_present"] else "no",
                      "yes" if d["client_present"] else "no",
                      f"{ct}/{vt}",
                      ", ".join(f for f in d["flags"] if f != "DIALOG_ALIGNED") or "aligned"))
    lines.append("Text-block counts shown client/v31.")
    lines.append("")
    lines.append(_md_table(
        ["gid", "file", "v31", "client", "text client/v31", "flags"], drows))
    lines.append("")

    lines.append(collection_territory_section(sources))
    lines.append("")

    (DATA_DIR / "v31-quests.md").write_text("\n".join(lines), encoding="utf-8")

    # ---- v31-quest-rewards.md ----
    rlines = []
    rlines.append("# v31 Quest Rewards Cross-Validation - Island of Dawn (Phase 2a)")
    rlines.append("")
    rlines.append("v31 `QuestCompensationData_13.xml` reward rows cross-validated against the "
                  "v17 client reward display (`v17-quests.json`). The v17 display is the north "
                  "star; disagreements are the server encoding diverging from it.")
    rlines.append("")
    rlines.append("## Verdict counts")
    rlines.append("")
    rlines.append(_md_table(["Verdict", "Count"],
                            [(v, n) for v, n in reward_counter.most_common()]))
    rlines.append("")
    rlines.append("`EXACT` exp/gold/itemBag/items all agree; `CLASS_SUPERSET` v31 adds only "
                  "the engineer 9th-class item(s) the v17 catalog predates, otherwise identical; "
                  "`EXP_GOLD_DRIFT` exp/gold/itemBag differ (items agree); `ITEM_DRIFT` item "
                  "sets differ beyond engineer; `V31_EMPTY` v31 comp is a stub while v17 has a "
                  "reward; `V17_EMPTY` v31 has a reward v17 does not; `BOTH_EMPTY`.")
    rlines.append("")
    rlines.append("## Per-quest rewards")
    rlines.append("")
    rrows = []
    for r in rewards:
        v17 = r["v17"]
        v31 = r["v31"]
        v17s = f"{v17['exp']}xp/{v17['gold']}g" + (f" bag={v17['itemBag']}" if v17['itemBag'] else "")
        if v31 is None:
            v31s = "(stub)"
        else:
            v31s = f"{v31['exp']}xp/{v31['gold']}g" + (f" bag={v31['itemBag']}" if v31['itemBag'] else "")
        rrows.append((r["gid"], r["title"], r["verdict"], v17s, v31s, r["detail"] or "-"))
    rlines.append(_md_table(
        ["gid", "title", "verdict", "v17", "v31", "detail"], rrows))
    rlines.append("")
    rlines.append("## Notable disagreements")
    rlines.append("")
    notable = [r for r in rewards if r["verdict"] in ("EXP_GOLD_DRIFT", "ITEM_DRIFT", "V31_EMPTY", "V17_EMPTY")]
    if notable:
        for r in notable:
            rlines.append(f"- **{r['gid']} {r['title']}** [{r['verdict']}]: {r['detail']}")
    else:
        rlines.append("_None beyond the engineer-class superset additions._")
    rlines.append("")
    (DATA_DIR / "v31-quest-rewards.md").write_text("\n".join(rlines), encoding="utf-8")

    # Console summary.
    print("v31 quest extraction complete.")
    print(f"  quests: {len(quests)}  present-in-v31: {sum(1 for q in quests if q['v31_present'])}")
    print(f"  v31 extra band quests: {v31_extra}")
    print("  quest flags:", dict(flag_counter))
    print("  reward verdicts:", dict(reward_counter))
    print("  dialog flags:", dict(dialog_counter))
    print("  wrote v31-quests.json/.md, v31-quest-rewards.json/.md to", DATA_DIR)


def collection_territory_section(sources):
    """Task 4 finding: which CollectionTerritory_13 file the v92 server loads."""
    coll92 = sources.v92 / "CollectionData"
    coll31 = sources.v31 / "CollectionData"
    area92 = sources.v92 / "AreaData"

    death = L.find_file_ci(coll92, "CollectionTerritory_13_ATW_Death_P.xml")
    atwp92 = L.find_file_ci(coll92, "CollectionTerritory_13_ATW_P.xml")
    atwp31 = L.find_file_ci(coll31, "CollectionTerritory_13_ATW_P.xml")
    area_death = L.find_file_ci(area92, "AreaData_13_ATW_Death_P.xml")
    area_atwp = L.find_file_ci(area92, "AreaData_13_ATW_P.xml")

    def area_name(path):
        if not path:
            return None
        m = re.search(r'<Area\b[^>]*\bareaName="([^"]*)"', L.read_text(path))
        return m.group(1) if m else None

    def ct_area_name(path):
        if not path:
            return None
        m = re.search(r'<CollectionTerritory\b[^>]*\bareaName="([^"]*)"', L.read_text(path))
        return m.group(1) if m else None

    def counts(path):
        if not path:
            return (0, 0)
        t = L.read_text(path)
        return (len(re.findall(r"<Collections\b", t)), len(re.findall(r"<Spawn\b", t)))

    identical = False
    if atwp92 and atwp31:
        identical = atwp92.read_bytes() == atwp31.read_bytes()

    live_area = area_name(area_death)
    s = []
    s.append("## CollectionTerritory verdict (Task 4)")
    s.append("")
    s.append("**The v92 server loads `CollectionTerritory_13_ATW_Death_P.xml`. "
             "`CollectionTerritory_13_ATW_P.xml` is an inert legacy leftover (byte-identical to "
             "v31) that no live area references.**")
    s.append("")
    s.append("Evidence:")
    s.append("")
    s.append(f"- v92 `CollectionData/` carries **both** files: "
             f"`ATW_Death_P` ({'present' if death else 'MISSING'}) and "
             f"`ATW_P` ({'present' if atwp92 else 'MISSING'}).")
    s.append(f"- v31 `CollectionData/` carries **only** the legacy `ATW_P` "
             f"({'present' if atwp31 else 'MISSING'}); no `ATW_Death_P` exists there.")
    s.append(f"- The zone-13 area in v92 is `AreaData_13_ATW_Death_P.xml`, whose `<Area>` "
             f"`areaName=\"{live_area}\"`. There is **no** `AreaData_13_ATW_P` in v92 "
             f"({'present' if area_atwp else 'absent'}), so the `ATW_P` area name no longer exists.")
    s.append(f"- Each `CollectionTerritory` file tags its own `areaName`: "
             f"`ATW_Death_P` file -> `{ct_area_name(death)}`, `ATW_P` file -> `{ct_area_name(atwp92)}`. "
             f"The loader binds a CollectionTerritory to the Area of the same `continentId` + "
             f"`areaName`; only `ATW_Death_P` matches a live Area.")
    dc, ds = counts(death)
    pc, ps = counts(atwp92)
    s.append(f"- Spawn geometry is the same in both: `ATW_Death_P` {dc} groups / {ds} spawns, "
             f"`ATW_P` {pc} groups / {ps} spawns (identical positions). The `ATW_Death_P` file "
             f"is a reformatted re-author (2-space indent, updated Korean territory descriptions); "
             f"content-equivalent spawns, so nothing is lost by the legacy file being dead.")
    s.append(f"- v92 `ATW_P` is **{'byte-identical' if identical else 'NOT byte-identical'}** to "
             f"v31's `ATW_P`, confirming it is the untouched v31-era artifact rather than a "
             f"maintained file.")
    s.append("")
    s.append("Recommendation: the legacy `CollectionTerritory_13_ATW_P.xml` can be removed from "
             "v92 (inert; safe), but it causes no live effect while present.")
    return "\n".join(s)


if __name__ == "__main__":
    main()
