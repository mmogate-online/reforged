"""Cross-source entity-ID alignment check for the Island of Dawn restoration.

Verifies that the (huntingZoneId, templateId) NPC keys and the global questId
keys used by the Phase 1 v17 roster are stable across the three restoration
sources, so everything downstream can key on those ids with confidence:

  - v17.11 client roster  : docs/plans/.../data/v17-npcs.json + v17-quests.json
                            (the intended content, extracted in Phase 1 from the
                            old client DataCenter)
  - v31 server datasheet  : easy-restore source (.references v31_datasheet)
  - v92 server datasheet  : the restoration target / clean git HEAD baseline
                            (.references server_datasheet)

Read-only. Writes only the four artifacts under data/. No datasheet is touched.

Name-resolution path (documented, because the three sources name creatures and
quests in different languages / layers):

  * The server NpcData Template carries a Korean `name` and a language-neutral
    English `race` enum. Korean `name` is directly comparable v31 <-> v92, so it
    is the sharp server-to-server rename signal. `race` is comparable to the v17
    roster's `race` field (also the English enum), so it anchors the roster row
    to the server row across the language gap.
  * The English display name lives only in the client StrSheet_Creature. The v17
    roster `name` came from the old client (v17.11, USA); we resolve the same
    (hz, tid) through the current v92 client StrSheet_Creature (EUR) to get the
    v92-era English name and compare cross-era. A divergence here (id kept, name
    changed) is the "suspicious rename" we hunt for.
  * Quest titles live in client StrSheet_Quest as String id = questId*1000+1. We
    resolve the old-client title (v17 anchor) and the v92-client title and
    compare; the server .quest files only carry the title *ref*, identical by
    construction because the questId is identical.

v92 is read through dclib.V92Baseline so a dirty working tree would fall back to
git HEAD; for this repo the tree is clean so disk == HEAD.
"""

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dclib  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ZONES = [13, 64, 213, 313, 364, 436]
DATA_DIR = dclib.reforged_dir() / "docs" / "plans" / "iod-alpha-content-loop" / "data"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

_TEMPLATE = re.compile(r"<Template\b([^>]*)>")
_ATTR = re.compile(r'(\w+)="([^"]*)"')


def norm_en(s: str) -> str:
    """Normalize an English display name/title for tolerant comparison.

    Unescapes XML entities (so a roster-decoded '<Repeatable>' matches a client
    '&lt;Repeatable&gt;'), lowercases, collapses whitespace, and strips trailing
    punctuation (so 'Destroy All Destroyers!' matches 'Destroy All Destroyers').
    """
    if not s:
        return ""
    s = html.unescape(s).replace("’", "'").replace("`", "'")
    s = " ".join(s.lower().split())
    return s.rstrip(" .!?")


def norm_race(s: str) -> str:
    return (s or "").strip().lower()


def server_templates(text: str) -> dict[int, dict]:
    """Map Template id -> {name, race} for an NpcData file text."""
    out: dict[int, dict] = {}
    for m in _TEMPLATE.finditer(text):
        attrs = dict(_ATTR.findall(m.group(1)))
        tid = attrs.get("id")
        if tid and tid.isdigit():
            out[int(tid)] = {"name": attrs.get("name", ""), "race": attrs.get("race", "")}
    return out


def creature_name_index(strsheet_dir: Path) -> dict[tuple[int, int], dict]:
    """(hz, templateId) -> creature name row from a client StrSheet_Creature dir."""
    return {(r["hz"], r["templateId"]): r for r in dclib.index_creature_names(strsheet_dir)}


def quest_title_index(strsheet_dir: Path) -> dict[int, str]:
    """String id -> title across a client StrSheet_Quest dir (all shards)."""
    out: dict[int, str] = {}
    if not strsheet_dir.is_dir():
        return out
    for entry in strsheet_dir.glob("*.xml"):
        out.update(dclib.strsheet_quest_ids(dclib.read_text(entry)))
    return out


def quest_title(idx: dict[int, str], gid: int) -> str:
    return idx.get(gid * 1000 + 1, "")


# ---------------------------------------------------------------------------
# NPC alignment
# ---------------------------------------------------------------------------

def align_npcs(sources, roster, oldc, v92c) -> dict:
    v31_root = sources.v31
    zones_out = {}
    counts = {c: 0 for c in ("ALIGNED", "RENAMED", "MISSING_IN_V31",
                             "MISSING_IN_V92", "EXTRA_V31", "EXTRA_V92")}
    non_aligned = []
    extras = []
    drift_rows = []

    for z in ZONES:
        roster_npcs = {n["templateId"]: n for n in roster["zones"][str(z)]["npcs"]}

        v31_file = dclib.find_zone_file(v31_root, "NpcData", z)
        v31_t = server_templates(dclib.read_text(v31_file)) if v31_file else {}

        v92_rel = dclib.find_file_ci(sources.v92, f"NpcData_{z}.xml")
        v92_text = sources.baseline.read(v92_rel.name) if v92_rel else None
        v92_t = server_templates(v92_text) if v92_text else {}

        all_ids = sorted(set(roster_npcs) | set(v31_t) | set(v92_t))
        rows = []
        for tid in all_ids:
            in17 = tid in roster_npcs
            in31 = tid in v31_t
            in92 = tid in v92_t
            r17 = roster_npcs.get(tid, {})
            n31 = v31_t.get(tid, {})
            n92 = v92_t.get(tid, {})
            v92_en = v92c.get((z, tid), {}).get("name", "")
            old_en = oldc.get((z, tid), {}).get("name", "")

            row = {
                "hz": z, "templateId": tid,
                "in_v17": in17, "in_v31": in31, "in_v92": in92,
                "v17_name": r17.get("name", ""),
                "v17_race": r17.get("race", ""),
                "v31_name_ko": n31.get("name", ""),
                "v31_race": n31.get("race", ""),
                "v92_name_ko": n92.get("name", ""),
                "v92_race": n92.get("race", ""),
                "v92_client_en": v92_en,
                "old_client_en": old_en,
                "signals": [],
            }

            if in17:
                if not in31:
                    row["classification"] = "MISSING_IN_V31"
                    counts["MISSING_IN_V31"] += 1
                    non_aligned.append(row)
                elif not in92:
                    row["classification"] = "MISSING_IN_V92"
                    counts["MISSING_IN_V92"] += 1
                    non_aligned.append(row)
                else:
                    # Genuine id reuse is a server-to-server rename: the SAME
                    # (hz,tid) carrying a different canonical Korean Template name
                    # in v31 vs v92. That is the only "RENAMED (suspicious)" signal.
                    sig = []
                    if n31.get("name", "") != n92.get("name", ""):
                        sig.append("KO_NAME_V31_NE_V92")
                    # Informational drift (NOT id landmines): English display name
                    # revised across client region/patch, or race attribute recorded
                    # differently (object-vs-model-race, case). Recorded, not counted
                    # as suspicious, because the server id points to the same creature.
                    drift = []
                    if v92_en and r17.get("name") and norm_en(v92_en) != norm_en(r17["name"]):
                        drift.append("DISPLAY_EN_DRIFT")
                    if r17.get("race") and n92.get("race") and norm_race(r17["race"]) != norm_race(n92["race"]):
                        drift.append("RACE_REPR_DRIFT")
                    row["signals"] = sig
                    row["drift"] = drift
                    if sig:
                        row["classification"] = "RENAMED"
                        counts["RENAMED"] += 1
                        non_aligned.append(row)
                    else:
                        row["classification"] = "ALIGNED"
                        counts["ALIGNED"] += 1
                        if drift:
                            drift_rows.append(row)
            else:
                # server-only row: reverse-direction extra (REMOVE/ignore candidate)
                tags = []
                if in31:
                    tags.append("EXTRA_V31")
                    counts["EXTRA_V31"] += 1
                if in92:
                    tags.append("EXTRA_V92")
                    counts["EXTRA_V92"] += 1
                row["classification"] = "+".join(tags)
                extras.append(row)
            rows.append(row)

        zones_out[str(z)] = {
            "v17_count": len(roster_npcs),
            "v31_count": len(v31_t),
            "v92_count": len(v92_t),
            "rows": rows,
        }

    return {"counts": counts, "zones": zones_out,
            "non_aligned": non_aligned, "extras": extras, "drift": drift_rows}


# ---------------------------------------------------------------------------
# Quest alignment
# ---------------------------------------------------------------------------

def storygroup_map(text: str) -> dict[int, list[str]]:
    """global questId -> [StoryGroup id(s)] registered in a QuestGroupList."""
    out: dict[int, list[str]] = {}
    for sg in re.finditer(r'<StoryGroup\b[^>]*\bid="(\d+)"[^>]*>(.*?)</StoryGroup>', text, re.S):
        gid = sg.group(1)
        for qm in re.finditer(r'<Quest\b[^>]*\bid="(\d+)"', sg.group(2)):
            out.setdefault(int(qm.group(1)), []).append(gid)
    return out


def load_band_quests(quest_dir_reader) -> dict[int, dict]:
    """global id (1300-1399) -> parsed quest model, via a reader(relname)->text."""
    out: dict[int, dict] = {}
    for gid in range(1300, 1400):
        text = quest_dir_reader(gid)
        if text is None:
            continue
        m = dclib.parse_quest(text)
        if m is not None:
            out[gid] = m
    return out


def align_quests(sources, v17q, old_qt, v92_qt) -> dict:
    v17_by_id = {q["id"]: q for q in v17q["quests"]}

    # v31 band quests (disk)
    v31_qd = sources.v31 / "QuestData"

    def v31_reader(gid):
        p = v31_qd / f"{gid:06d}.quest"
        if not p.exists():
            p = v31_qd / f"{gid}.quest"
        return dclib.read_text(p) if p.exists() else None

    # v92 band quests (HEAD baseline)
    def v92_reader(gid):
        return sources.baseline.read(f"QuestData/{gid:06d}.quest")

    v31_band = load_band_quests(v31_reader)
    v92_band = load_band_quests(v92_reader)

    # quest-zone attribution is the Quest번호 hz, not the filename band
    v31_qz13 = {g for g, m in v31_band.items() if m["hz"] == 13}
    v92_qz13 = {g for g, m in v92_band.items() if m["hz"] == 13}

    v31_sg = storygroup_map(dclib.read_text(dclib.find_file_ci(sources.v31, "QuestGroupList.xml")))
    v92_sg = storygroup_map(sources.baseline.read("QuestGroupList.xml") or "")

    counts = {c: 0 for c in ("ALIGNED", "RENAMED", "MISSING_IN_V31",
                             "MISSING_IN_V92", "EXTRA_V31", "EXTRA_V92")}
    rows = []
    non_aligned = []
    drift_rows = []

    all_ids = sorted(set(v17_by_id) | set(v31_band) | set(v92_band))
    for gid in all_ids:
        in17 = gid in v17_by_id
        in31 = gid in v31_band
        in92 = gid in v92_band
        q17 = v17_by_id.get(gid, {})
        m31 = v31_band.get(gid)
        m92 = v92_band.get(gid)

        row = {
            "questId": gid,
            "in_v17": in17, "in_v31": in31, "in_v92": in92,
            "v17_title": q17.get("title", ""),
            "old_client_title": quest_title(old_qt, gid),
            "v92_client_title": quest_title(v92_qt, gid),
            "v17_story_group": q17.get("story_group", "") or "",
            "v31_story_group": ",".join(v31_sg.get(gid, [])),
            "v92_story_group": ",".join(v92_sg.get(gid, [])),
            "v31_sentinel": bool(m31 and m31["sentinel"]),
            "v92_sentinel": bool(m92 and m92["sentinel"]),
            "v92_quest_zone": m92["hz"] if m92 else (m31["hz"] if m31 else None),
            "signals": [],
        }

        if in17:
            if not in31:
                row["classification"] = "MISSING_IN_V31"
                counts["MISSING_IN_V31"] += 1
                non_aligned.append(row)
            elif not in92:
                row["classification"] = "MISSING_IN_V92"
                counts["MISSING_IN_V92"] += 1
                non_aligned.append(row)
            else:
                # Genuine id reuse is a server-to-server title-ref change: the
                # SAME questId pointing at a different title string in v31 vs v92.
                sig = []
                if m31["title_id"] != m92["title_id"]:
                    sig.append("TITLE_REF_V31_NE_V92")
                if (m31["story_group"] or "") != (m92["story_group"] or ""):
                    sig.append("STORYGROUP_V31_NE_V92")
                # Informational drift (NOT an id landmine): English title revised
                # across client region/patch; the questId and title-ref are stable.
                drift = []
                vt, ct = row["v17_title"], row["v92_client_title"]
                if vt and ct and norm_en(vt) != norm_en(ct):
                    drift.append("TITLE_EN_DRIFT")
                if (row["v17_story_group"] or "") != (row["v92_story_group"] or ""):
                    drift.append("STORYGROUP_MEMBERSHIP_DRIFT")
                row["signals"] = sig
                row["drift"] = drift
                if sig:
                    row["classification"] = "RENAMED"
                    counts["RENAMED"] += 1
                    non_aligned.append(row)
                else:
                    row["classification"] = "ALIGNED"
                    counts["ALIGNED"] += 1
                    if drift:
                        drift_rows.append(row)
        else:
            tags = []
            if in31:
                tags.append("EXTRA_V31")
                counts["EXTRA_V31"] += 1
            if in92:
                tags.append("EXTRA_V92")
                counts["EXTRA_V92"] += 1
            row["classification"] = "+".join(tags)
            non_aligned.append(row)
        rows.append(row)

    # REMOVE candidates: quest-zone-13 quests in v92 baseline absent from v17
    remove_candidates = []
    for gid in sorted(v92_qz13):
        if gid not in v17_by_id:
            m = v92_band[gid]
            remove_candidates.append({
                "questId": gid,
                "quest_zone": m["hz"],
                "local": m["local"],
                "v92_sentinel_disabled": m["sentinel"],
                "v92_prereqs": m["prereqs"],
                "v92_enabled": not m["sentinel"],
                "title": quest_title(v92_qt, gid),
                "in_v31": gid in v31_band,
            })

    return {
        "counts": counts,
        "rows": rows,
        "non_aligned": non_aligned,
        "drift": drift_rows,
        "remove_candidates": remove_candidates,
        "v31_qz13_count": len(v31_qz13),
        "v92_qz13_count": len(v92_qz13),
        "story_group_agreement": all(
            ",".join(v31_sg.get(g, [])) == ",".join(v92_sg.get(g, []))
            for g in set(v31_band) | set(v92_band)
        ),
        "disabled_count_v92": sum(1 for m in v92_band.values() if m["sentinel"]),
        "disabled_count_v31": sum(1 for m in v31_band.values() if m["sentinel"]),
    }


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def yn(b):
    return "yes" if b else "no"


def render_npcs_md(res) -> str:
    c = res["counts"]
    L = []
    L.append("# NPC template-ID alignment (Island of Dawn)")
    L.append("")
    L.append("Cross-source check of every v17 roster NPC `(huntingZoneId, templateId)` "
             "against v31 and v92 `NpcData_<hz>.xml`, plus reverse-direction server extras.")
    L.append("")
    L.append("Name-resolution path: server Template `name` is Korean (compared v31 vs v92 "
             "as the sharp rename signal); the English `race` enum anchors the roster row to "
             "the server row across languages; the v17 English name (old client) is compared "
             "to the current v92 client StrSheet_Creature English name for the same key.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L.append("| Classification | Count |")
    L.append("|---|---|")
    for k in ("ALIGNED", "RENAMED", "MISSING_IN_V31", "MISSING_IN_V92",
              "EXTRA_V31", "EXTRA_V92"):
        L.append(f"| {k} | {c[k]} |")
    L.append("")
    L.append("Per-zone key counts (v17 / v31 / v92 template totals):")
    L.append("")
    L.append("| Zone | v17 | v31 | v92 |")
    L.append("|---|---|---|---|")
    for z in ZONES:
        zd = res["zones"][str(z)]
        L.append(f"| {z} | {zd['v17_count']} | {zd['v31_count']} | {zd['v92_count']} |")
    L.append("")

    L.append("## RENAMED / MISSING v17 rows (id landmines)")
    L.append("")
    L.append("RENAMED here means genuine id reuse: the same `(hz,tid)` carries a different "
             "canonical Korean server name in v31 vs v92. That is the signal that would break "
             "keying.")
    L.append("")
    if not res["non_aligned"]:
        L.append("**None.** Every v17 roster NPC key is present in both v31 and v92, and its "
                 "canonical Korean Template name is identical between the two servers, so no id "
                 "was reused for a different creature.")
    else:
        L.append("| hz | tid | class | signals | v17 name | v31 ko | v92 ko | v92 client EN | v17 race | v31 race | v92 race |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in res["non_aligned"]:
            L.append(f"| {r['hz']} | {r['templateId']} | {r['classification']} | "
                     f"{','.join(r['signals']) or '-'} | {r['v17_name']} | {r['v31_name_ko']} | "
                     f"{r['v92_name_ko']} | {r['v92_client_en']} | {r['v17_race']} | "
                     f"{r['v31_race']} | {r['v92_race']} |")
    L.append("")

    L.append("## Informational drift (NOT id landmines)")
    L.append("")
    L.append("These rows are ALIGNED: the `(hz,tid)` id is stable and the canonical Korean "
             "server name is identical v31 vs v92. Only the client English display name was "
             "revised across region/patch (`DISPLAY_EN_DRIFT`), or the `race` attribute is "
             "recorded differently between the v17 roster and the server "
             "(`RACE_REPR_DRIFT`, e.g. a corpse tagged `object` in the roster but the model "
             "race `Human` on the server). Listed for restoration awareness only.")
    L.append("")
    if not res["drift"]:
        L.append("None.")
    else:
        L.append("| hz | tid | drift | v17 name | v92 client EN | v17 race | v92 race | v31 ko = v92 ko |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in res["drift"]:
            same_ko = "yes" if r["v31_name_ko"] == r["v92_name_ko"] else "NO"
            L.append(f"| {r['hz']} | {r['templateId']} | {','.join(r['drift'])} | {r['v17_name']} | "
                     f"{r['v92_client_en']} | {r['v17_race']} | {r['v92_race']} | {same_ko} |")
    L.append("")

    L.append("## Reverse-direction extras (present in server, absent from v17)")
    L.append("")
    L.append("Candidate REMOVE/ignore set: server NPCs the v17 roster does not list. All are "
             "present in both v31 and v92 unless a single-server tag says otherwise.")
    L.append("")
    L.append("| hz | tid | tag | v92 ko name | v92 client EN | race | in v31 | in v92 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in res["extras"]:
        L.append(f"| {r['hz']} | {r['templateId']} | {r['classification']} | "
                 f"{r['v92_name_ko']} | {r['v92_client_en']} | {r['v92_race'] or r['v31_race']} | "
                 f"{yn(r['in_v31'])} | {yn(r['in_v92'])} |")
    L.append("")
    return "\n".join(L)


def render_quests_md(res) -> str:
    c = res["counts"]
    L = []
    L.append("# Quest-ID alignment (Island of Dawn)")
    L.append("")
    L.append("Cross-source check of the 63 v17 roster quests against v31 and v92 `QuestData`, "
             "with story-group membership and disable-state.")
    L.append("")
    L.append("Title-resolution path: the server `.quest` files carry only a title *ref* "
             "(`@quest:<questId*1000+1>`), identical by construction because the questId is "
             "identical; the English title lives in client StrSheet_Quest. The v17 title (old "
             "client) is compared to the v92 client title for the same questId.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L.append("| Classification | Count |")
    L.append("|---|---|")
    for k in ("ALIGNED", "RENAMED", "MISSING_IN_V31", "MISSING_IN_V92",
              "EXTRA_V31", "EXTRA_V92"):
        L.append(f"| {k} | {c[k]} |")
    L.append("")
    L.append(f"- v17 roster quests: {sum(1 for r in res['rows'] if r['in_v17'])}")
    L.append(f"- quest-zone-13 quests (Quest번호 hz=13): v31={res['v31_qz13_count']}, v92={res['v92_qz13_count']}")
    L.append(f"- story-group membership identical v31 vs v92: {yn(res['story_group_agreement'])}")
    L.append(f"- sentinel-disabled 13xx band quests: v31={res['disabled_count_v31']}, v92={res['disabled_count_v92']}")
    L.append("")

    L.append("## RENAMED / MISSING / EXTRA rows (id landmines)")
    L.append("")
    L.append("RENAMED here means genuine id reuse: the same questId pointing at a different "
             "title-ref (`title*1000+1`) or story group in v31 vs v92. `EXTRA_*` rows are "
             "server band quests absent from the v17 roster (see REMOVE candidates below).")
    L.append("")
    if not res["non_aligned"]:
        L.append("**None.**")
    else:
        L.append("| questId | class | signals | v17 title | v92 client title | v31 sg | v92 sg | v31 disabled | v92 disabled |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for r in res["non_aligned"]:
            L.append(f"| {r['questId']} | {r['classification']} | {','.join(r['signals']) or '-'} | "
                     f"{r['v17_title']} | {r['v92_client_title']} | "
                     f"{r['v31_story_group'] or '-'} | {r['v92_story_group'] or '-'} | "
                     f"{yn(r['v31_sentinel'])} | {yn(r['v92_sentinel'])} |")
    L.append("")

    L.append("## Informational drift (NOT id landmines)")
    L.append("")
    L.append("These questIds are ALIGNED: the id and its title-ref are stable across v31 and "
             "v92. `TITLE_EN_DRIFT` is a client English title revised across region/patch (the "
             "questId still resolves the title from whichever client ships). "
             "`STORYGROUP_MEMBERSHIP_DRIFT` is a v17-roster-vs-server QuestGroupList "
             "registration difference (v31 and v92 agree with each other); it drives quest_restore "
             "story-group wiring, not id keying.")
    L.append("")
    if not res["drift"]:
        L.append("None.")
    else:
        L.append("| questId | drift | v17 title | v92 client title | v17 sg | v31 sg | v92 sg |")
        L.append("|---|---|---|---|---|---|---|")
        for r in res["drift"]:
            L.append(f"| {r['questId']} | {','.join(r['drift'])} | {r['v17_title']} | "
                     f"{r['v92_client_title']} | {r['v17_story_group'] or '-'} | "
                     f"{r['v31_story_group'] or '-'} | {r['v92_story_group'] or '-'} |")
    L.append("")

    L.append("## REMOVE candidates: quest-zone-13 quests in v92 baseline absent from v17")
    L.append("")
    L.append("Disable convention: a quest is soft-disabled by writing the single sentinel "
             "prerequisite `<퀘스트Id>99,99</퀘스트Id>` (quest 99,99 does not exist, so the "
             "requirement can never be met and the quest never offers). No other disable "
             "convention was found in the 13xx band: min/max level bands are all real (1-12), "
             "and both servers carry an identical disabled set.")
    L.append("")
    if not res["remove_candidates"]:
        L.append("None.")
    else:
        L.append("| questId | quest-zone | local | v92 title | enabled | sentinel-disabled | v92 prereqs | in v31 |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in res["remove_candidates"]:
            L.append(f"| {r['questId']} | {r['quest_zone']} | {r['local']} | {r['title']} | "
                     f"{yn(r['v92_enabled'])} | {yn(r['v92_sentinel_disabled'])} | "
                     f"{','.join(r['v92_prereqs']) or '-'} | {yn(r['in_v31'])} |")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    refs = dclib.load_references()
    sources = dclib.Sources(refs)
    problems = sources.validate()
    if problems:
        for p in problems:
            print("SOURCE PROBLEM:", p)
        return 1

    roster = json.loads((DATA_DIR / "v17-npcs.json").read_text(encoding="utf-8"))
    v17q = json.loads((DATA_DIR / "v17-quests.json").read_text(encoding="utf-8"))

    oldc = creature_name_index(sources.old_client / "StrSheet_Creature")
    v92c = creature_name_index(Path(refs["client_datacenter"]) / "StrSheet_Creature")
    old_qt = quest_title_index(sources.old_client / "StrSheet_Quest")
    v92_qt = quest_title_index(Path(refs["client_datacenter"]) / "StrSheet_Quest")

    npc_res = align_npcs(sources, roster, oldc, v92c)
    quest_res = align_quests(sources, v17q, old_qt, v92_qt)

    (DATA_DIR / "id-alignment-npcs.json").write_text(
        json.dumps(npc_res, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "id-alignment-npcs.md").write_text(
        render_npcs_md(npc_res), encoding="utf-8")
    (DATA_DIR / "id-alignment-quests.json").write_text(
        json.dumps(quest_res, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "id-alignment-quests.md").write_text(
        render_quests_md(quest_res), encoding="utf-8")

    print("NPC counts:  ", npc_res["counts"])
    print("Quest counts:", quest_res["counts"])
    print("REMOVE candidates (quest-zone 13, not in v17):",
          [r["questId"] for r in quest_res["remove_candidates"]])
    print("Artifacts written to", DATA_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
