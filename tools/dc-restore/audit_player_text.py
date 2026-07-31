"""Player-facing text gate (read-only).

DOCTRINE.md rule 10: player-facing text describes the world, never our build order.
Item tooltips, quest journals, dialogs and region strings state what is true in the
game. They never state what we have not built yet, what is coming in a later wave, or
which patch a thing belongs to.

WHY THIS IS A GATE AND NOT A CODE REVIEW ITEM. The failure mode is invisible to every
check this project already runs. `dsl validate` passes, `migrate` reports 0 warnings,
the client sync is clean, and the world server boots happily on a tooltip that tells
the player about our sprint. It is only caught by a human reading the string in game,
which is the most expensive place to catch anything.

THE INCIDENT. Item 95217 "Valkyon Commendation" (spec 002/39) shipped with a tooltip
ending "The quartermaster who accepts them has not yet set up." The spec's own header
explained why: the token deliberately ships before its vendor, and a currency with no
sink "reads as a bug", so the tooltip explained the gap. That reasoning is the trap,
and it will recur, because a restoration of this size ships incomplete systems on
purpose. The remedy is never prose; it is the plan folder and the backlog.

WHAT IS SCANNED. Spec YAML, not the datasheet. Two reasons. Authoring time is the
cheap place to fail, before any apply. And a datasheet scan cannot tell our text from
the publisher's 112,000 shipped strings, several of which legitimately say "no longer
usable" or name a discontinued event. This gate owns only what our specs write.

Comments are invisible to it by construction: the file is parsed as YAML, so `#` lines
never reach the scanner. Spec headers are free to discuss wave order in as much detail
as they like, which is exactly where that discussion belongs.

Usage:
  python audit_player_text.py                     # every spec under specs/patches/
  python audit_player_text.py --patch 002         # one patch
  python audit_player_text.py --specs <path> ...  # explicit files
"""

import argparse
import glob
import os
import re
import sys

import yaml

from dclib import reforged_dir

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# What counts as player-facing
# ---------------------------------------------------------------------------
# Two independent routes into the scan, because neither alone is sufficient.
#
# By ENTITY: everything under a string-table entity is by definition text the player
# reads. Measured over specs/patches/ on 2026-07-31; add new ones here as they appear.
STRING_ENTITIES = {
    "abnormalityStrings",
    "fieldStrings",
    "itemStrings",
    "npcLocStrings",
    "npcStrings",
    "questStrings",
    "regionStrings",
    "questDialogs",
}

# By FIELD NAME: `toolTip` is player-facing wherever it appears, including the inline
# `strings:` form nested inside an entity block that is not itself a string table.
PLAYER_FACING_KEYS = {"tooltip", "tooltipstring"}

# `name` is deliberately NOT in either set on its own. Under `items:` it is the internal
# datasheet name (`enchant_material_1`, `token`), which is not player-facing at all;
# under `itemStrings:` it is. The entity route already covers the second case, so adding
# `name` globally would fire on every internal name in the corpus.

# ---------------------------------------------------------------------------
# The banned phrase family
# ---------------------------------------------------------------------------
# Each entry is (compiled pattern, what it means). Word boundaries throughout, so
# "nothing" does not match "not yet" and "temporary" does not match a proper noun.
#
# DELIBERATELY NOT BANNED: "no longer usable", "formerly", "obsolete", "retired". Those
# describe a state of the world that is true and stable, which is the whole point of the
# rule. The publisher's own retirement convention uses them and so do specs 002/37 and
# 002/43.
BANNED = [
    (r"\bnot yet\b", "future tense about our own work"),
    (r"\bcoming soon\b", "future tense about our own work"),
    (r"\bwill be (added|available|implemented|enabled|introduced)\b",
     "future tense about our own work"),
    (r"\bfor now\b", "implies a state we intend to change"),
    (r"\bat this time\b", "implies a state we intend to change"),
    (r"\bcurrently (unavailable|unused|disabled|not)\b",
     "implies a state we intend to change"),
    (r"\bplaceholder\b", "internal authoring language"),
    (r"\bwork in progress\b", "internal authoring language"),
    (r"\bWIP\b", "internal authoring language"),
    (r"\bTBD\b", "internal authoring language"),
    (r"\bTODO\b", "internal authoring language"),
    (r"\btemporar(y|ily)\b", "internal authoring language"),
    (r"\bfor testing\b", "internal authoring language"),
    (r"\bwave \d+\b", "names our build order"),
    (r"\bpatch \d+\b", "names our build order"),
    (r"\bphase [A-Z0-9]\b", "names our build order"),
    (r"\bhas not (yet )?been (set up|added|implemented|built)\b",
     "states an internal gap to the player"),
    (r"\bhas not (yet )?set up\b", "states an internal gap to the player"),
    (r"\bis not (yet )?(implemented|available|in game)\b",
     "states an internal gap to the player"),
    (r"\bin a (future|later) (update|patch|version)\b",
     "states an internal gap to the player"),
]
COMPILED = [(re.compile(p, re.IGNORECASE), why) for p, why in BANNED]


def walk(node, path, in_string_entity, out):
    """Collect (path, key, value) for every player-facing string under `node`."""
    if isinstance(node, dict):
        for k, v in node.items():
            key = str(k)
            entity = in_string_entity or key in STRING_ENTITIES
            if isinstance(v, str):
                if entity or key.lower() in PLAYER_FACING_KEYS:
                    out.append((path, key, v))
            else:
                walk(v, f"{path}.{key}" if path else key, entity, out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, str):
                # A bare string in a list under a string entity (rare, but e.g. a
                # multi-line journal authored as a sequence).
                if in_string_entity:
                    out.append((path, f"[{i}]", v))
            else:
                walk(v, f"{path}[{i}]", in_string_entity, out)


def scan(path):
    """[(entity path, key, value, pattern, why)] for one spec file."""
    with open(path, encoding="utf-8") as fh:
        try:
            doc = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            return [("<unparseable>", "-", str(exc).splitlines()[0], "-",
                     "spec is not valid YAML; the gate cannot read it")]
    if not isinstance(doc, dict):
        return []

    strings = []
    walk(doc, "", False, strings)

    hits = []
    for where, key, value in strings:
        for pattern, why in COMPILED:
            m = pattern.search(value)
            if m:
                hits.append((where, key, value, m.group(0), why))
    return hits


def main():
    ap = argparse.ArgumentParser(
        description="Player-facing text gate (DOCTRINE.md rule 10).")
    ap.add_argument("--patch", help="patch number, e.g. 002 (default: all patches)")
    ap.add_argument("--specs", nargs="*", help="explicit spec files instead of a patch")
    args = ap.parse_args()

    root = reforged_dir()
    if args.specs:
        files = sorted(args.specs)
    else:
        sub = args.patch or "*"
        files = sorted(glob.glob(str(root / "specs" / "patches" / sub / "**" / "*.yaml"),
                                 recursive=True))

    print(f"Specs scanned: {len(files)}\n")
    if not files:
        print("RESULT: FAIL (no spec files matched)")
        return 1

    failures = []
    scanned_strings = 0
    for path in files:
        try:
            rel = os.path.relpath(path, root)
        except ValueError:
            # --specs may point at a different drive (probe files in the scratchpad).
            rel = path
        with open(path, encoding="utf-8") as fh:
            try:
                doc = yaml.safe_load(fh)
            except yaml.YAMLError:
                doc = None
        if isinstance(doc, dict):
            got = []
            walk(doc, "", False, got)
            scanned_strings += len(got)

        for where, key, value, matched, why in scan(path):
            snippet = value if len(value) <= 160 else value[:157] + "..."
            failures.append(
                f"{rel}\n      at {where or '<root>'} / {key}\n"
                f"      matched {matched!r}: {why}\n"
                f"      text: {snippet}")

    print(f"Player-facing strings checked: {scanned_strings}")
    print(f"Banned patterns: {len(COMPILED)}\n")

    if failures:
        print(f"RESULT: FAIL ({len(failures)} problem(s))")
        print("\nDOCTRINE.md rule 10: player-facing text describes the world, never our")
        print("build order. Record the gap in the plan folder and the backlog instead.\n")
        for f in failures:
            print("  " + f + "\n")
        return 1

    print("RESULT: PASS (0 player-facing strings describe our build order)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
