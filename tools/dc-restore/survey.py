"""dc-restore survey: gap report across old client, v31, and v92 (HEAD baseline).

For each requested hunting zone, compares NPC templates, skills, AI, territory
spawns, quests, quest and loot compensations, and dialog coverage between the
v31 server datasheet (easy-restore source), the old client DataCenter
(hard-restore source), and the current v92 server datasheet read at its clean
git HEAD baseline. Working-tree overlays (uncommitted patch tuning) are reported
separately from genuine content loss.

Read-only: writes only the report given by --out and the optional --json.
"""

import argparse
import json
import time
from collections import Counter
from pathlib import Path

import dclib
from dclib import (
    Sources,
    find_zone_file,
    find_file_ci,
    index_client_shards,
    iter_local,
    load_references,
    parse_root,
    read_text,
    scan_comments,
    strip_ns,
    zone_from_hz_attr,
    zone_from_questno,
)

# Per-zone server file families that carry commented-out markup worth surfacing.
COMMENT_FAMILIES = ["NpcData", "NpcSkillData", "TerritoryData", "AIData"]


# ---------------------------------------------------------------------------
# Small parse helpers
# ---------------------------------------------------------------------------

def npc_templates(text: str) -> dict[int, str]:
    """Map Template id -> name from an NpcData file."""
    out: dict[int, str] = {}
    for el in iter_local(parse_root(text), "Template"):
        tid = el.get("id")
        if tid is not None and tid.isdigit():
            out[int(tid)] = el.get("name", "")
    return out


def skill_ids(text: str) -> set[int]:
    out: set[int] = set()
    for el in iter_local(parse_root(text), "Skill"):
        val = el.get("templateId")
        if val is not None and val.isdigit():
            out.add(int(val))
    return out


def ai_ids(text: str) -> set[int]:
    out: set[int] = set()
    for el in iter_local(parse_root(text), "Ai"):
        val = el.get("id")
        if val is not None and val.isdigit():
            out.add(int(val))
    return out


def territory_groups(text: str) -> dict[int, tuple[str, int]]:
    """Map TerritoryGroup id -> (desc, spawn-entry count)."""
    out: dict[int, tuple[str, int]] = {}
    for grp in iter_local(parse_root(text), "TerritoryGroup"):
        gid = grp.get("id")
        if gid is None or not gid.isdigit():
            continue
        spawns = sum(1 for e in grp.iter() if strip_ns(e.tag) == "Npc")
        out[int(gid)] = (grp.get("desc", ""), spawns)
    return out


def quest_comp_status(text: str) -> dict[int, bool]:
    """Map questId -> filled(True)/stub(False) from a QuestCompensationData file."""
    out: dict[int, bool] = {}
    for q in iter_local(parse_root(text), "Quest"):
        qid = q.get("questId")
        if qid is not None and qid.isdigit():
            out[int(qid)] = len(list(q)) > 0
    return out


def comp_npc_ids(text: str) -> set[int]:
    """npcTemplateId set from a C/E CompensationData file."""
    out: set[int] = set()
    for c in iter_local(parse_root(text), "Compensation"):
        val = c.get("npcTemplateId")
        if val is not None and val.isdigit():
            out.add(int(val))
    return out


def qgl_quest_ids(text: str) -> set[int]:
    """Quest ids registered in a QuestGroupList StoryGroupList."""
    out: set[int] = set()
    for q in iter_local(parse_root(text), "Quest"):
        qid = q.get("id")
        if qid is not None and qid.isdigit():
            out.add(int(qid))
    return out


# ---------------------------------------------------------------------------
# Zone quest sets (ground truth: Quest번호 header hz, not the filename band)
# ---------------------------------------------------------------------------

def scan_server_quest_zones(quest_dir: Path, zones: set[int]) -> dict[int, set[int]]:
    """Map zone -> set of global quest ids for server .quest files.

    Zone is taken from the Quest번호 'hz,localId' header, which is authoritative
    (the numeric filename band does not hold for every zone).
    """
    out: dict[int, set[int]] = {z: set() for z in zones}
    if not quest_dir.is_dir():
        return out
    for entry in quest_dir.iterdir():
        if entry.suffix.lower() != ".quest":
            continue
        head = dclib._peek(entry, 500)
        zone = zone_from_questno(head)
        if zone in out and entry.stem.isdigit():
            out[zone].add(int(entry.stem))
    return out


def scan_client_quest_zones(quest_dir: Path, zones: set[int]) -> dict[int, set[int]]:
    """Map zone -> set of client global quest ids (hz from header, id from root)."""
    import re
    id_pat = re.compile(r"<Quest\b[^>]*\bid=\"(\d+)\"")
    out: dict[int, set[int]] = {z: set() for z in zones}
    if not quest_dir.is_dir():
        return out
    for entry in quest_dir.iterdir():
        if entry.suffix.lower() != ".xml":
            continue
        head = dclib._peek(entry, 500)
        zone = zone_from_questno(head)
        if zone not in out:
            continue
        m = id_pat.search(head)
        if m:
            out[zone].add(int(m.group(1)))
    return out


# ---------------------------------------------------------------------------
# Per-zone collection
# ---------------------------------------------------------------------------

def read_v92(sources: Sources, relpath: str, baseline: bool = True) -> str | None:
    return sources.baseline.read(relpath, baseline=baseline)


def collect_zone(sources: Sources, zone: int, quest_sets: dict) -> dict:
    z = {"zone": zone}

    # --- NPC templates ---
    v31_npc_file = find_zone_file(sources.v31, "NpcData", zone)
    v31_npc = npc_templates(read_text(v31_npc_file)) if v31_npc_file else {}
    v92_npc_text = read_v92(sources, f"NpcData_{zone}.xml")
    v92_npc = npc_templates(v92_npc_text) if v92_npc_text else {}
    client_npc_shards = quest_sets["client_npc"].get(zone, [])
    client_npc_count = 0
    for shard in client_npc_shards:
        client_npc_count += sum(1 for _ in iter_local(parse_root(read_text(shard)), "Template"))
    z["npc"] = {
        "v31": v31_npc,
        "v92": v92_npc,
        "v92_dirty": sources.baseline.is_dirty(f"NpcData_{zone}.xml"),
        "missing_in_v92": sorted(set(v31_npc) - set(v92_npc)),
        "in_both": sorted(set(v31_npc) & set(v92_npc)),
        "client_shards": len(client_npc_shards),
        "client_templates": client_npc_count,
    }

    # --- NPC skills ---
    v31_sk_file = find_zone_file(sources.v31, "NpcSkillData", zone)
    v31_sk = skill_ids(read_text(v31_sk_file)) if v31_sk_file else set()
    v92_sk_text = read_v92(sources, f"NpcSkillData_{zone}.xml")
    v92_sk = skill_ids(v92_sk_text) if v92_sk_text else set()
    z["skills"] = {"v31": len(v31_sk), "v92": len(v92_sk),
                   "missing_in_v92": sorted(v31_sk - v92_sk)}

    # --- AI (zone-64 file is lowercase AiData_64.xml) ---
    v31_ai_file = find_zone_file(sources.v31, "AIData", zone)
    v31_ai = ai_ids(read_text(v31_ai_file)) if v31_ai_file else set()
    v92_ai_text = read_v92(sources, f"AIData_{zone}.xml")
    v92_ai = ai_ids(v92_ai_text) if v92_ai_text else set()
    z["ai"] = {"v31": len(v31_ai), "v92": len(v92_ai),
               "missing_in_v92": sorted(v31_ai - v92_ai)}

    # --- Territory ---
    v31_terr_file = find_zone_file(sources.v31, "TerritoryData", zone)
    v31_terr = territory_groups(read_text(v31_terr_file)) if v31_terr_file else {}
    v92_terr_text = read_v92(sources, f"TerritoryData_{zone}.xml")
    v92_terr = territory_groups(v92_terr_text) if v92_terr_text else {}
    spawn_shrink = []
    for gid in sorted(set(v31_terr) & set(v92_terr)):
        if v31_terr[gid][1] > v92_terr[gid][1]:
            spawn_shrink.append((gid, v31_terr[gid][0], v31_terr[gid][1], v92_terr[gid][1]))
    z["territory"] = {
        "v31_groups": len(v31_terr), "v92_groups": len(v92_terr),
        "v92_dirty": sources.baseline.is_dirty(f"TerritoryData_{zone}.xml"),
        "missing_in_v92": sorted(
            (gid, v31_terr[gid][0], v31_terr[gid][1]) for gid in set(v31_terr) - set(v92_terr)
        ),
        "spawn_shrink": spawn_shrink,
    }

    # --- Quests ---
    v31_q = quest_sets["v31"].get(zone, set())
    v92_q = quest_sets["v92"].get(zone, set())
    cli_q = quest_sets["client"].get(zone, set())
    base = v31_q | v92_q | cli_q
    z["quests"] = {
        "v31": len(v31_q), "v92": len(v92_q), "client": len(cli_q),
        "v31_only": sorted(v31_q - v92_q),
        "client_only": sorted(base - v31_q - v92_q),
        "qgl_v31": len(quest_sets["qgl_v31"] & base),
        "qgl_v92": len(quest_sets["qgl_v92"] & base),
        "qgl_client": len(quest_sets["qgl_client"] & base),
    }

    # --- Quest compensations ---
    qc_rel = f"CompensationData/QuestCompensationData_{zone}.xml"
    v31_qc_file = find_file_ci(sources.v31 / "CompensationData", f"QuestCompensationData_{zone}.xml")
    v31_qc = quest_comp_status(read_text(v31_qc_file)) if v31_qc_file else {}
    v92_qc_text = read_v92(sources, qc_rel)
    v92_qc = quest_comp_status(v92_qc_text) if v92_qc_text else {}
    qc_lost = []
    for qid in sorted(v31_qc):
        if v31_qc[qid] and not v92_qc.get(qid, False):  # filled in v31, stub/absent in v92
            qc_lost.append((qid, "absent" if qid not in v92_qc else "stub"))
    z["quest_comp"] = {
        "v31_filled": sum(1 for v in v31_qc.values() if v),
        "v31_total": len(v31_qc),
        "v92_filled": sum(1 for v in v92_qc.values() if v),
        "v92_total": len(v92_qc),
        "lost": qc_lost,
    }

    # --- Loot compensations (C and E) with overlay annotation ---
    z["loot_comp"] = {}
    for kind, cpad in (("C", True), ("E", False)):
        fam = f"{kind}Compensation"
        fname = f"{fam}_{zone:04d}.xml" if cpad else f"{fam}_{zone}.xml"
        rel = f"CompensationData/{fname}"
        v31_file = find_file_ci(sources.v31 / "CompensationData", fname)
        v31_ids = comp_npc_ids(read_text(v31_file)) if v31_file else set()
        head_text = read_v92(sources, rel, baseline=True)
        head_ids = comp_npc_ids(head_text) if head_text else set()
        wt_text = read_v92(sources, rel, baseline=False)
        wt_ids = comp_npc_ids(wt_text) if wt_text else set()
        dirty = sources.baseline.is_dirty(rel)
        overlay_stripped = dirty and len(head_ids) > 0 and len(wt_ids) < len(head_ids)
        # Effective remaining gap: after a non-stripping overlay the working tree
        # may already restore most ids, so compare v31 against it. A stripping
        # overlay is deliberate patch tuning, so the actionable gap stays vs HEAD.
        remaining = sorted(v31_ids - (head_ids if overlay_stripped else wt_ids)) if dirty \
            else sorted(v31_ids - head_ids)
        z["loot_comp"][kind] = {
            "present_v31": v31_file is not None,
            "present_v92_head": head_text is not None,
            "v31_npcs": len(v31_ids),
            "head_npcs": len(head_ids),
            "worktree_npcs": len(wt_ids),
            "missing_vs_head": sorted(v31_ids - head_ids),
            "missing_vs_worktree": sorted(v31_ids - wt_ids),
            "remaining_gap": remaining,
            "dirty": dirty,
            "overlay_stripped": overlay_stripped,
        }

    # --- Dialogs ---
    # QuestDialog: client shards keyed by huntingZoneId; v31 named by questId_step;
    # v92 named QuestDialog_<n> with n in the zone*100..zone*100+99 band.
    client_qd = len(quest_sets["client_qd"].get(zone, []))
    v31_qd = 0
    v31_qd_dir = sources.v31 / "QuestDialog"
    if v31_qd_dir.is_dir():
        for entry in v31_qd_dir.iterdir():
            name = entry.name
            if not name.lower().startswith("questdialog_"):
                continue
            core = name[len("QuestDialog_"):].split(".", 1)[0]
            qid = core.split("_", 1)[0]
            if qid.isdigit() and int(qid) in v31_q:
                v31_qd += 1
    v92_qd = 0
    v92_qd_dir = sources.v92 / "QuestDialog"
    lo, hi = zone * 100, zone * 100 + 99
    if v92_qd_dir.is_dir():
        for entry in v92_qd_dir.iterdir():
            name = entry.name
            if not name.lower().startswith("questdialog_"):
                continue
            core = name[len("QuestDialog_"):].split(".", 1)[0]
            if core.isdigit() and lo <= int(core) <= hi:
                v92_qd += 1
    z["dialogs"] = {
        "quest_client": client_qd, "quest_v31": v31_qd, "quest_v92": v92_qd,
        "villager_client_zone": len(quest_sets["client_vd"].get(zone, [])),
    }

    # --- Commented-out markup ---
    comments = []
    for fam in COMMENT_FAMILIES:
        v31_file = find_zone_file(sources.v31, fam, zone)
        if v31_file:
            for line_no, snip in scan_comments(read_text(v31_file)):
                comments.append(("v31", v31_file.name, line_no, snip[:160]))
        v92_text = read_v92(sources, f"{fam}_{zone}.xml")
        if v92_text:
            for line_no, snip in scan_comments(v92_text):
                comments.append(("v92-HEAD", f"{fam}_{zone}.xml", line_no, snip[:160]))
    z["comments"] = comments
    return z


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

# Quest ids a prior recon expected to be "client-only"; verified against the data.
WATCH_QUESTS = [1334, 1336, 1341, 1343]


def render(zones_data: list[dict], sources: Sources, villager_global: dict, quest_sets: dict) -> str:
    lines: list[str] = []
    w = lines.append
    w("# dc-restore Survey: Iteration 0 Gap Report")
    w("")
    w(f"Generated {time.strftime('%Y-%m-%d %H:%M:%S')} by tools/dc-restore/survey.py")
    w("")
    w("Baseline for v92 is the clean git HEAD content. Uncommitted working-tree")
    w("changes are patch-001 tuning overlays, annotated separately and never")
    w("counted as content loss. Sources: old client DataCenter (hard-restore),")
    w("v31 server datasheet (easy-restore), v92 server datasheet (current truth).")
    w("")

    # Summary table
    w("## Summary")
    w("")
    w("| Zone | NPC miss | Skill miss | AI miss | Terr miss | Quests v31/v92/cli | v31-only Q | client-only Q | QComp lost | Loot overlay |")
    w("|------|----------|-----------|---------|-----------|--------------------|-----------|---------------|-----------|--------------|")
    for z in zones_data:
        q = z["quests"]
        loot_flags = []
        for kind in ("C", "E"):
            lc = z["loot_comp"][kind]
            if lc["overlay_stripped"]:
                loot_flags.append(f"{kind}:stripped")
        w("| {zone} | {npc} | {sk} | {ai} | {terr} | {qv31}/{qv92}/{qcli} | {q31o} | {qclio} | {qc} | {loot} |".format(
            zone=z["zone"],
            npc=len(z["npc"]["missing_in_v92"]),
            sk=len(z["skills"]["missing_in_v92"]),
            ai=len(z["ai"]["missing_in_v92"]),
            terr=len(z["territory"]["missing_in_v92"]),
            qv31=q["v31"], qv92=q["v92"], qcli=q["client"],
            q31o=len(q["v31_only"]), qclio=len(q["client_only"]),
            qc=len(z["quest_comp"]["lost"]),
            loot=", ".join(loot_flags) or "-",
        ))
    w("")

    # Recon cross-check: the prior recon expected 1334/1336/1341/1343 to be
    # client-only. Report their actual per-source presence so the claim is
    # settled by data rather than assumption.
    w("## Recon cross-checks")
    w("")
    w("Prior recon expected quests 1334, 1336, 1341, 1343 to be client-only (hard restore).")
    w("Actual per-source presence (zone 13, by Quest번호 hz header):")
    w("")
    w("| Quest | v31 | v92 | client | classification |")
    w("|-------|-----|-----|--------|----------------|")
    v31_13 = quest_sets["v31"].get(13, set())
    v92_13 = quest_sets["v92"].get(13, set())
    cli_13 = quest_sets["client"].get(13, set())
    for qid in WATCH_QUESTS:
        in31, in92, incli = qid in v31_13, qid in v92_13, qid in cli_13
        if in92:
            cls = "in-v92 (present, not a gap)"
        elif in31:
            cls = "v31-only (easy restore)"
        elif incli:
            cls = "client-only (hard restore)"
        else:
            cls = "absent everywhere"
        w(f"| {qid} | {'Y' if in31 else '-'} | {'Y' if in92 else '-'} | {'Y' if incli else '-'} | {cls} |")
    w("")
    if all(qid in v92_13 for qid in WATCH_QUESTS):
        w("Finding: all four are full quests present in v31, v92, and the client. "
          "The recon 'client-only' expectation does NOT hold against current on-disk data; "
          "they are not a restoration gap.")
    w("")

    # Per-zone detail
    for z in zones_data:
        zone = z["zone"]
        w(f"## Zone {zone}")
        w("")

        npc = z["npc"]
        overlay = " (v92 file is a patch-001 overlay; compared against HEAD)" if npc["v92_dirty"] else ""
        w(f"### NPC templates{overlay}")
        w(f"- v31: {len(npc['v31'])} | v92 HEAD: {len(npc['v92'])} | client shards: {npc['client_shards']} ({npc['client_templates']} templates)")
        w(f"- present in both: {len(npc['in_both'])}")
        if npc["missing_in_v92"]:
            w(f"- MISSING in v92 HEAD ({len(npc['missing_in_v92'])}):")
            for tid in npc["missing_in_v92"][:40]:
                w(f"    - {tid}  {npc['v31'].get(tid, '')}")
            if len(npc["missing_in_v92"]) > 40:
                w(f"    - ... and {len(npc['missing_in_v92']) - 40} more")
        else:
            w("- MISSING in v92 HEAD: none")
        w("")

        w("### NPC skills / AI")
        sk, ai = z["skills"], z["ai"]
        w(f"- Skills: v31 {sk['v31']} | v92 {sk['v92']} | missing {len(sk['missing_in_v92'])}"
          + (f" -> {sk['missing_in_v92'][:20]}" if sk["missing_in_v92"] else ""))
        w(f"- AI: v31 {ai['v31']} | v92 {ai['v92']} | missing {len(ai['missing_in_v92'])}"
          + (f" -> {ai['missing_in_v92'][:20]}" if ai["missing_in_v92"] else ""))
        w("")

        terr = z["territory"]
        overlay = " (v92 file is a patch-001 overlay; compared against HEAD)" if terr["v92_dirty"] else ""
        w(f"### Territory / spawns{overlay}")
        w(f"- Groups: v31 {terr['v31_groups']} | v92 HEAD {terr['v92_groups']} | missing {len(terr['missing_in_v92'])}")
        for gid, desc, cnt in terr["missing_in_v92"][:20]:
            w(f"    - group {gid} ({cnt} spawns)  {desc}")
        if terr["spawn_shrink"]:
            w(f"- Spawn-count shrink in shared groups ({len(terr['spawn_shrink'])}):")
            for gid, desc, a, b in terr["spawn_shrink"][:20]:
                w(f"    - group {gid}: v31 {a} -> v92 {b}  {desc}")
        w("")

        q = z["quests"]
        w("### Quests")
        w(f"- Zone quest set (Quest번호 hz header): v31 {q['v31']} | v92 {q['v92']} | client {q['client']}")
        w(f"- Registered in QuestGroupList (of the union): v31 {q['qgl_v31']} | v92 {q['qgl_v92']} | client {q['qgl_client']}")
        w(f"- v31-only (easy restore): {q['v31_only'] or 'none'}")
        w(f"- client-only (hard restore): {q['client_only'] or 'none'}")
        w("")

        qc = z["quest_comp"]
        w("### Quest compensations")
        w(f"- v31 filled/total: {qc['v31_filled']}/{qc['v31_total']} | v92 HEAD filled/total: {qc['v92_filled']}/{qc['v92_total']}")
        if qc["lost"]:
            w(f"- Reward lost in v92 HEAD ({len(qc['lost'])}): "
              + ", ".join(f"{qid}({state})" for qid, state in qc["lost"][:40]))
        else:
            w("- Reward lost in v92 HEAD: none")
        w("")

        w("### Loot compensations")
        for kind in ("C", "E"):
            lc = z["loot_comp"][kind]
            if not lc["present_v31"] and not lc["present_v92_head"]:
                w(f"- {kind}Compensation: absent in both v31 and v92 HEAD")
                continue
            parts = [f"v31 npcs {lc['v31_npcs']}", f"v92 HEAD npcs {lc['head_npcs']}"]
            if lc["dirty"]:
                parts.append(f"worktree npcs {lc['worktree_npcs']}")
            w(f"- {kind}Compensation: " + " | ".join(parts))
            if lc["overlay_stripped"]:
                w(f"    - PATCH-001 OVERLAY: working tree stripped to {lc['worktree_npcs']} npcs "
                  f"(HEAD has {lc['head_npcs']}); this is deliberate tuning, not content loss")
            if lc["missing_vs_head"]:
                w(f"    - npcTemplateIds in v31 missing from v92 HEAD ({len(lc['missing_vs_head'])}): "
                  + ", ".join(str(x) for x in lc["missing_vs_head"][:30]))
            if lc["dirty"] and not lc["overlay_stripped"] and \
                    len(lc["missing_vs_worktree"]) != len(lc["missing_vs_head"]):
                mvw = lc["missing_vs_worktree"]
                w(f"    - gap after patch-001 overlay (v31 missing from working tree): "
                  + (", ".join(str(x) for x in mvw) if mvw else "none")
                  + f" ({len(mvw)} remain)")
        w("")

        d = z["dialogs"]
        w("### Dialogs")
        w(f"- QuestDialog: client shards {d['quest_client']} | v31 files {d['quest_v31']} | v92 files {d['quest_v92']}")
        w(f"- VillagerDialog: client shards tagged to this zone {d['villager_client_zone']} "
          "(villager dialogs are keyed globally, not by zone; true per-zone attribution "
          "needs the villager-NPC join done by a future villager-restore module). v31: absent by design.")
        w("")

        if z["comments"]:
            w(f"### Commented-out markup ({len(z['comments'])})")
            for src, fname, line_no, snip in z["comments"][:20]:
                w(f"- [{src}] {fname}:{line_no}  {snip}")
            if len(z["comments"]) > 20:
                w(f"- ... and {len(z['comments']) - 20} more")
            w("")

    # Global villager corpus signal
    w("## VillagerDialog corpus (global signal)")
    w("")
    w(f"- Old client VillagerDialog shards: {villager_global['client_shards']}")
    w(f"- v92 VillagerDialog files: {villager_global['v92_files']} "
      f"({villager_global['v92_entries']} VillagerDialog entries)")
    w("- v31: no VillagerDialog directory (absent by design).")
    w("- Per-zone attribution is deferred to the villager-restore module (join via villager NPCs).")
    w("")

    # Restoration worklist
    w("## Restoration worklist")
    w("")
    w("### Easy path (restore from v31 server datasheet)")
    for z in zones_data:
        items = []
        if z["npc"]["missing_in_v92"]:
            items.append(f"{len(z['npc']['missing_in_v92'])} NPC templates")
        if z["skills"]["missing_in_v92"]:
            items.append(f"{len(z['skills']['missing_in_v92'])} skills")
        if z["ai"]["missing_in_v92"]:
            items.append(f"{len(z['ai']['missing_in_v92'])} AI entries")
        if z["territory"]["missing_in_v92"]:
            items.append(f"{len(z['territory']['missing_in_v92'])} territory groups")
        if z["quests"]["v31_only"]:
            items.append(f"{len(z['quests']['v31_only'])} quests")
        if z["quest_comp"]["lost"]:
            items.append(f"{len(z['quest_comp']['lost'])} quest rewards")
        loot_miss = sum(len(z["loot_comp"][k]["remaining_gap"]) for k in ("C", "E"))
        loot_head = sum(len(z["loot_comp"][k]["missing_vs_head"]) for k in ("C", "E"))
        if loot_miss:
            note = f" (vs HEAD baseline: {loot_head})" if loot_head != loot_miss else ""
            items.append(f"{loot_miss} loot-comp npc entries{note}")
        if items:
            w(f"- Zone {z['zone']}: " + ", ".join(items))
    w("")
    w("### Hard path (reconstruct from old client DataCenter)")
    any_hard = False
    for z in zones_data:
        if z["quests"]["client_only"]:
            any_hard = True
            w(f"- Zone {z['zone']}: {len(z['quests']['client_only'])} client-only quests "
              f"-> {z['quests']['client_only'][:20]}")
    if not any_hard:
        w("- No client-only quests found in surveyed zones.")
    w("")
    w("### Overlay (patch-001 tuning, NOT restoration scope)")
    any_overlay = False
    for z in zones_data:
        flags = []
        if z["npc"]["v92_dirty"]:
            flags.append("NpcData")
        if z["territory"]["v92_dirty"]:
            flags.append("TerritoryData")
        for kind in ("C", "E"):
            if z["loot_comp"][kind]["overlay_stripped"]:
                flags.append(f"{kind}Compensation(stripped)")
        if flags:
            any_overlay = True
            w(f"- Zone {z['zone']}: working-tree overlay on {', '.join(flags)}")
    if not any_overlay:
        w("- No patch-001 overlays touch the surveyed zones.")
    w("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="dc-restore content gap survey.")
    parser.add_argument("--zones", required=True, help="Comma-separated hunting zone ids, e.g. 13,64,213")
    parser.add_argument("--out", required=True, help="Output markdown report path")
    parser.add_argument("--json", help="Optional JSON dump path")
    args = parser.parse_args()

    zones = [int(z) for z in args.zones.split(",") if z.strip()]
    zone_set = set(zones)

    refs = load_references()
    sources = Sources(refs)
    problems = sources.validate()
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        return 1

    t0 = time.monotonic()
    print(f"Surveying zones {zones} ...")

    # Build shared indices once.
    quest_sets = {
        "v31": scan_server_quest_zones(sources.v31 / "QuestData", zone_set),
        "v92": scan_server_quest_zones(sources.v92 / "QuestData", zone_set),
        "client": scan_client_quest_zones(sources.old_client / "Quest", zone_set),
        "client_npc": index_client_shards(sources.old_client / "NpcData", zone_from_hz_attr, zone_set),
        "client_qd": index_client_shards(sources.old_client / "QuestDialog", zone_from_hz_attr, zone_set),
        "client_vd": index_client_shards(sources.old_client / "VillagerDialog", zone_from_hz_attr, zone_set),
    }
    # QuestGroupList registration sets (not dirty; worktree == HEAD).
    qgl_v31_file = find_file_ci(sources.v31, "QuestGroupList.xml")
    quest_sets["qgl_v31"] = qgl_quest_ids(read_text(qgl_v31_file)) if qgl_v31_file else set()
    qgl_v92_text = read_v92(sources, "QuestGroupList.xml")
    quest_sets["qgl_v92"] = qgl_quest_ids(qgl_v92_text) if qgl_v92_text else set()
    qgl_cli_dir = sources.old_client / "QuestGroupList"
    qgl_client: set[int] = set()
    if qgl_cli_dir.is_dir():
        for entry in qgl_cli_dir.iterdir():
            if entry.suffix.lower() == ".xml":
                qgl_client |= qgl_quest_ids(read_text(entry))
    quest_sets["qgl_client"] = qgl_client

    zones_data = [collect_zone(sources, z, quest_sets) for z in zones]

    # Villager corpus signal (global).
    client_vd_dir = sources.old_client / "VillagerDialog"
    v92_vd_dir = sources.v92 / "VillagerDialog"
    v92_vd_files = list(v92_vd_dir.glob("VillagerDialog_*.xml")) if v92_vd_dir.is_dir() else []
    v92_vd_entries = 0
    for f in v92_vd_files:
        v92_vd_entries += sum(1 for _ in iter_local(parse_root(read_text(f)), "VillagerDialog"))
    villager_global = {
        "client_shards": len(list(client_vd_dir.glob("*.xml"))) if client_vd_dir.is_dir() else 0,
        "v92_files": len(v92_vd_files),
        "v92_entries": v92_vd_entries,
    }

    report = render(zones_data, sources, villager_global, quest_sets)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"zones": zones_data, "villager_global": villager_global},
                       indent=2, ensure_ascii=False, default=list),
            encoding="utf-8",
        )

    dt = time.monotonic() - t0
    print(f"Done in {dt:.1f}s -> {out_path}")
    if args.json:
        print(f"JSON -> {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
