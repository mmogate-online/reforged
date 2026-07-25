"""Class-gate coverage audit for restored quests (read-only).

Classic TERA offers some content as a PHYSICAL variant and a CASTER variant,
each gated by `<수행조건><클래스>`. A variant group covers exactly the classes that
existed when the content shipped, so a faithfully restored group leaves every
later class matching NO member: the content is offered to nobody, and anything
gated behind it is unreachable.

Born from the 2026-07-25 incident: a Ninja completed 1384 (Getting to Know the
Garrison) and the story spine dead-ended, because 1382 admits
Warrior/Lancer/Slayer/Berserker/Archer/Engineer and 1383 admits
Sorcerer/Priest/Elementalist, so Milene offered neither and 1331 never unlocked.
v31 carries the identical lists, so the restoration reproduced the hole
faithfully and NO diff-against-v31 gate could ever catch it. Only a coverage
check against the current class roster finds this.

Coverage is evaluated per VARIANT GROUP, not per quest: a caster-only quest is
not a gap when its physical sibling admits the class. Quests are grouped by
(zone, giver, story group), because the giver is the real-world grouping
mechanism: one NPC hands each player the variant matching their class.

    1351 / 1352                  Kiriya 64,1006   "Supply and Demand"
    1382 / 1383                  Milene 64,1049   "Gathering Your Strength"
    6302 / 6306                  63,1007          Collegium / Legion of Arms
    1371-1379 + 1380/1381/1387   Dulari 213,1017  per-class training quests

Caveat: if one NPC gives class-gated quests belonging to unrelated chains, the
group is over-merged and a real gap could hide inside the union. Each member's
prerequisites are printed so that is visible, and a group whose members disagree
on prerequisites is flagged MIXED for a human to check.

Verdicts per group:
  GAP       no member admits an audited class, and the group is offerable
  DISABLED  same, but every member is sentinel-disabled (prereq 99,99)
  SINGLE    one member, gated to exactly one class (per-class training quests)
  OK        the group's members together admit every audited class

Exit code 1 if any GAP is found.

Reaper (Soulless) is NOT audited by default: it starts in a different zone at a
higher level and never walks these chains (user decision 2026-07-25). Audit it
explicitly with --classes when working on its own content.

Usage:
  python reforged/tools/dc-restore/audit_class_gates.py --zones 13
  python reforged/tools/dc-restore/audit_class_gates.py --zones 13,64,213,313,364
  python reforged/tools/dc-restore/audit_class_gates.py --all-zones
  python reforged/tools/dc-restore/audit_class_gates.py --zones 63 --classes Assassin,Fighter,Glaiver,Soulless
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from dclib import iter_local, load_references, parse_root, read_text

REQ = "수행조건"
CLS = "클래스"
TRIG = "발생조건"
QUEST_NO = "Quest번호"
STORY_GROUP = "스토리그룹Id"
QUEST_TITLE = "Quest제목"
QUEST_ID = "퀘스트Id"
SENTINEL = "99,99"

# Full roster minus Soulless (Reaper), which is out of scope by decision.
DEFAULT_AUDIT = [
    "Warrior", "Lancer", "Slayer", "Berserker", "Archer", "Sorcerer",
    "Priest", "Elementalist", "Engineer", "Assassin", "Fighter", "Glaiver",
]
GAME_NAME = {
    "Assassin": "Ninja", "Fighter": "Brawler", "Glaiver": "Valkyrie",
    "Soulless": "Reaper", "Elementalist": "Mystic", "Engineer": "Gunner",
}


def label(internal: str) -> str:
    game = GAME_NAME.get(internal)
    return f"{internal}/{game}" if game else internal


def local_child(elem, name: str):
    for child in elem:
        if child.tag.rsplit("}", 1)[-1] == name:
            return child
    return None


def local_text(elem, name: str) -> str:
    child = local_child(elem, name)
    return (child.text or "").strip() if child is not None else ""


def collect(quest_dir: Path, zones: set[str] | None) -> list[dict]:
    rows = []
    for path in sorted(quest_dir.glob("*.quest")):
        try:
            root = parse_root(read_text(path))
        except Exception as exc:
            print(f"  ! {path.name}: parse failed ({exc})")
            continue
        header = local_child(root, "Header")
        if header is None:
            continue
        req = local_child(header, REQ)
        if req is None:
            continue
        gate = local_child(req, CLS)
        if gate is None or not len(gate):
            continue

        number = local_text(header, QUEST_NO)
        zone = number.split(",")[0].strip() if "," in number else "?"
        if zones is not None and zone not in zones:
            continue

        prereqs = tuple(sorted((q.text or "").strip() for q in iter_local(req, QUEST_ID)))
        trigger = local_child(header, TRIG)
        rows.append({
            "quest": path.stem,
            "zone": zone,
            "story_group": local_text(header, STORY_GROUP),
            "title": local_text(header, QUEST_TITLE),
            "classes": [c.tag.rsplit("}", 1)[-1] for c in gate],
            "prereqs": prereqs,
            "disabled": SENTINEL in prereqs,
            "giver": ", ".join(
                f"{c.tag.rsplit('}', 1)[-1]}={(c.text or '').strip()}" for c in trigger
            ) if trigger is not None else "",
        })
    return rows


def group_key(row: dict):
    """Variant group: the giver hands each class its matching variant."""
    return (row["zone"], row["giver"], row["story_group"])


def audit(quest_dir: Path, zones: set[str] | None, audited: list[str]) -> int:
    rows = collect(quest_dir, zones)
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[group_key(row)].append(row)

    gaps, disabled, single, ok = [], [], [], []
    for key, members in groups.items():
        covered = {c for m in members for c in m["classes"]}
        missing = [c for c in audited if c not in covered]
        entry = {"key": key, "members": members, "missing": missing}
        if not missing:
            ok.append(entry)
        elif all(m["disabled"] for m in members):
            disabled.append(entry)
        elif len(members) == 1 and len(members[0]["classes"]) == 1:
            single.append(entry)
        else:
            gaps.append(entry)

    print(f"Roster audited ({len(audited)}): {', '.join(label(c) for c in audited)}")
    print(f"Quest dir: {quest_dir}")
    zone_label = "all" if zones is None else ",".join(
        sorted(zones, key=lambda z: int(z) if z.isdigit() else 0))
    print(f"Zones: {zone_label}")
    print(f"Class-gated quests found: {len(rows)} in {len(groups)} variant group(s)\n")

    if gaps:
        print(f"GAP: {len(gaps)} offerable variant group(s) exclude an audited class\n")
        for entry in sorted(gaps, key=lambda e: min(m["quest"] for m in e["members"])):
            members = sorted(entry["members"], key=lambda m: m["quest"])
            mixed = len({m["prereqs"] for m in members}) > 1
            print(f"  group: zone {members[0]['zone']}  giver {members[0]['giver']}  "
                  f"storyGroup {members[0]['story_group'] or '-'}"
                  f"{'  [MIXED prereqs, check for over-merge]' if mixed else ''}")
            for m in members:
                print(f"      {m['quest']}  prereq {' '.join(m['prereqs']) or '-'}")
                print(f"          admits: {' '.join(m['classes'])}")
            print(f"      NOT OFFERED TO: {' '.join(label(c) for c in entry['missing'])}")
            print()
        print("  Add the missing classes to the variant whose content fits them")
        print("  (physical vs caster) so the group stays mutually exclusive: every")
        print("  class must match exactly one member.\n")

    if single:
        names = sorted(m["quest"] for e in single for m in e["members"])
        print(f"SINGLE (one quest per class, by design): {len(names)}")
        print("  " + " ".join(names) + "\n")
    if disabled:
        names = sorted(m["quest"] for e in disabled for m in e["members"])
        print(f"DISABLED (sentinel prereq {SENTINEL}, not offerable): {len(names)}")
        print("  " + " ".join(names) + "\n")

    print(f"OK (group covers the whole roster): {len(ok)}")
    print(f"\nRESULT: {'FAIL' if gaps else 'PASS'} ({len(gaps)} gap group(s))")
    return 1 if gaps else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--zones", help="Comma-separated zone ids from Quest번호 (e.g. 13,64,213)")
    group.add_argument("--all-zones", action="store_true", help="Audit every quest file")
    ap.add_argument("--classes", default=",".join(DEFAULT_AUDIT),
                    help="Comma-separated internal class names to require "
                         "(default: the full roster except Soulless)")
    ap.add_argument("--datasheet", help="Server datasheet path (default: server_datasheet from .references)")
    args = ap.parse_args()

    datasheet = Path(args.datasheet) if args.datasheet else Path(load_references()["server_datasheet"])
    quest_dir = datasheet / "QuestData"
    if not quest_dir.is_dir():
        print(f"Error: QuestData not found under {datasheet}")
        return 2

    zones = None if args.all_zones else {z.strip() for z in args.zones.split(",") if z.strip()}
    audited = [c.strip() for c in args.classes.split(",") if c.strip()]
    return audit(quest_dir, zones, audited)


if __name__ == "__main__":
    sys.exit(main())
