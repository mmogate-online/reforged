"""Full NPC stat VALUE diff for the IoD restoration.

For every (huntingZone, templateId) in the v17-rostered NPC set, compares the
full server <Template> element between the v31 source (ground truth) and the
v92 baseline: the template-level attributes (elite, size, race, scale, aiid,
villager, isObjectNpc, ...) and every attribute on the <Stat> child (maxHp,
atk, def, level, exp, walk/run speeds, ...).

Alignment (roster membership + template presence) was proven separately; this
tool answers only "are the VALUES identical". Numeric comparison treats textual
float-formatting differences ("100.000000" vs "100", trailing spaces) as equal
and flags genuine value differences only.

Read-only. Emits stat-diff.json and stat-diff.md under the plan data dir.

Run: python stat_diff.py
"""

import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dclib  # noqa: E402

ISLAND_ZONES = [13, 64, 213, 313, 364, 436]

ROSTER_JSON = Path(
    r"D:\dev\mmogate\github\reforged-server-content\reforged"
    r"\docs\plans\iod-alpha-content-loop\data\v31-npc-stats.json"
)
OUT_JSON = ROSTER_JSON.parent / "stat-diff.json"
OUT_MD = ROSTER_JSON.parent / "stat-diff.md"


def load_roster() -> dict[int, list[int]]:
    """Map huntingZone -> sorted list of rostered templateIds."""
    data = json.loads(ROSTER_JSON.read_text(encoding="utf-8"))
    roster: dict[int, list[int]] = {}
    for zone in data["zones"]:
        hz = zone["hz"]
        ids = sorted(t["npcTemplateId"] for t in zone["templates"])
        roster[hz] = ids
    return roster


def index_templates(text: str) -> dict[int, ET.Element]:
    """Map templateId -> <Template> element for an NpcData file text."""
    root = ET.fromstring(text.encode("utf-8"))
    out: dict[int, ET.Element] = {}
    for el in root.iter():
        if dclib.strip_ns(el.tag) != "Template":
            continue
        tid = el.get("id")
        if tid is not None and tid.isdigit():
            out[int(tid)] = el
    return out


def stat_child(template: ET.Element) -> ET.Element | None:
    for el in template:
        if dclib.strip_ns(el.tag) == "Stat":
            return el
    return None


def values_equal(a: str | None, b: str | None) -> bool:
    """Compare two attribute values with numeric-formatting tolerance.

    None (attribute absent) and "" (present but empty) are treated as equal:
    both mean "no value". Numeric strings are compared as floats so
    "100.000000" == "100" and "1.100000 " == "1.1"; everything else is compared
    as whitespace-stripped text.
    """
    na = "" if a is None else a.strip()
    nb = "" if b is None else b.strip()
    if na == nb:
        return True
    fa = _as_float(na)
    fb = _as_float(nb)
    if fa is not None and fb is not None:
        return math.isclose(fa, fb, rel_tol=1e-9, abs_tol=1e-9)
    return False


_FLOAT_RE = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")


def _as_float(s: str) -> float | None:
    if s == "" or not _FLOAT_RE.match(s):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def diff_template(v31: ET.Element, v92: ET.Element) -> list[dict]:
    """Return attribute-level deltas between two <Template> elements.

    Compares template-level attributes and the <Stat> child's attributes.
    Each delta: {scope, name, v31, v92}. Empty list means IDENTICAL.
    """
    deltas: list[dict] = []

    # Template-level attributes.
    names = sorted(set(v31.attrib) | set(v92.attrib))
    for name in names:
        a = v31.get(name)
        b = v92.get(name)
        if not values_equal(a, b):
            deltas.append({"scope": "template", "name": name,
                           "v31": a, "v92": b})

    # Stat child.
    s31 = stat_child(v31)
    s92 = stat_child(v92)
    if (s31 is None) != (s92 is None):
        deltas.append({"scope": "stat", "name": "<Stat element>",
                       "v31": "present" if s31 is not None else "absent",
                       "v92": "present" if s92 is not None else "absent"})
    elif s31 is not None and s92 is not None:
        snames = sorted(set(s31.attrib) | set(s92.attrib))
        for name in snames:
            a = s31.get(name)
            b = s92.get(name)
            if not values_equal(a, b):
                deltas.append({"scope": "stat", "name": name,
                               "v31": a, "v92": b})
    return deltas


def main() -> int:
    refs = dclib.load_references()
    sources = dclib.Sources(refs)
    problems = sources.validate()
    if problems:
        for p in problems:
            print("ERROR:", p, file=sys.stderr)
        return 1

    roster = load_roster()

    zone_reports: list[dict] = []
    total_identical = 0
    total_drift = 0
    total_missing = 0

    for hz in ISLAND_ZONES:
        ids = roster.get(hz, [])

        v31_path = dclib.find_zone_file(sources.v31, "NpcData", hz)
        v31_text = dclib.read_text(v31_path) if v31_path else None
        v92_text = sources.baseline.read(f"NpcData_{hz}.xml", baseline=True)

        v31_idx = index_templates(v31_text) if v31_text else {}
        v92_idx = index_templates(v92_text) if v92_text else {}

        templates: list[dict] = []
        z_identical = z_drift = z_missing = 0
        for tid in ids:
            t31 = v31_idx.get(tid)
            t92 = v92_idx.get(tid)
            if t31 is None or t92 is None:
                z_missing += 1
                templates.append({
                    "templateId": tid,
                    "verdict": "MISSING",
                    "v31_present": t31 is not None,
                    "v92_present": t92 is not None,
                    "deltas": [],
                })
                continue
            deltas = diff_template(t31, t92)
            if deltas:
                z_drift += 1
                templates.append({
                    "templateId": tid,
                    "verdict": "DRIFT",
                    "v31_present": True,
                    "v92_present": True,
                    "deltas": deltas,
                })
            else:
                z_identical += 1
                templates.append({
                    "templateId": tid,
                    "verdict": "IDENTICAL",
                    "v31_present": True,
                    "v92_present": True,
                    "deltas": [],
                })

        total_identical += z_identical
        total_drift += z_drift
        total_missing += z_missing
        zone_reports.append({
            "hz": hz,
            "roster_size": len(ids),
            "identical": z_identical,
            "drift": z_drift,
            "missing": z_missing,
            "templates": templates,
        })

    all_match = (total_drift == 0 and total_missing == 0)
    report = {
        "source_v31": str(sources.v31),
        "source_v92": str(sources.v92),
        "v92_read_from": "git HEAD baseline (dirty files) / disk (clean files)",
        "totals": {
            "roster": total_identical + total_drift + total_missing,
            "identical": total_identical,
            "drift": total_drift,
            "missing": total_missing,
        },
        "verdict": "ALL-MATCH" if all_match else "DRIFT-PRESENT",
        "zones": zone_reports,
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    write_markdown(report)

    print(f"IDENTICAL={total_identical} DRIFT={total_drift} "
          f"MISSING={total_missing} verdict={report['verdict']}")
    return 0


def write_markdown(report: dict) -> None:
    lines: list[str] = []
    lines.append("# IoD NPC Stat VALUE Diff (v31 source vs v92 baseline)")
    lines.append("")
    lines.append("Full-Template value comparison for every v17-rostered NPC "
                 "template: all template-level attributes plus every attribute "
                 "on the <Stat> child. Numeric formatting differences "
                 "(\"100.000000\" vs \"100\", trailing spaces) are treated as "
                 "equal; only genuine value differences are flagged.")
    lines.append("")
    t = report["totals"]
    lines.append(f"- v31 source: `{report['source_v31']}`")
    lines.append(f"- v92 baseline: `{report['source_v92']}` "
                 f"({report['v92_read_from']})")
    lines.append(f"- Roster: {t['roster']} templates "
                 f"(IDENTICAL={t['identical']}, "
                 f"DRIFT={t['drift']}, MISSING={t['missing']})")
    lines.append(f"- **Verdict: {report['verdict']}**")
    lines.append("")
    lines.append("## Per-zone summary")
    lines.append("")
    lines.append("| HZ | Roster | IDENTICAL | DRIFT | MISSING |")
    lines.append("|----|-------:|----------:|------:|--------:|")
    for z in report["zones"]:
        lines.append(f"| {z['hz']} | {z['roster_size']} | {z['identical']} | "
                     f"{z['drift']} | {z['missing']} |")
    lines.append("")

    drift_zones = [z for z in report["zones"]
                   if z["drift"] or z["missing"]]
    lines.append("## Drift detail")
    lines.append("")
    if not drift_zones:
        lines.append("No drift and no missing templates. Every rostered "
                     "template carries an identical stat block in v92 versus "
                     "v31. No restore spec is needed on the NPC-stats axis.")
    else:
        for z in drift_zones:
            lines.append(f"### HZ {z['hz']}")
            lines.append("")
            for tpl in z["templates"]:
                if tpl["verdict"] == "IDENTICAL":
                    continue
                if tpl["verdict"] == "MISSING":
                    lines.append(f"- Template `{tpl['templateId']}` "
                                 f"**MISSING** (v31_present="
                                 f"{tpl['v31_present']}, v92_present="
                                 f"{tpl['v92_present']})")
                    continue
                lines.append(f"- Template `{tpl['templateId']}` **DRIFT**:")
                for d in tpl["deltas"]:
                    lines.append(f"  - `{d['scope']}.{d['name']}`: "
                                 f"v31=`{d['v31']}` v92=`{d['v92']}`")
            lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
