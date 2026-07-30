"""
Feedstock faucet removal, zone loot leg (IoD reward-vector wave 1, phase C2).

Emits a DSL spec of `eCompensations: update` records that delete every `<ItemBag>`
holding a feedstock item (94101 to 94112) from the field-zone loot tables of every
zone except 13, whose two surviving rows are the C4 classic carve-out.

Framework: reforged-content-framework 04-power-systems.md 5e, "there is no direct
content drop of feedstock", restated as ruling R13. Vanilla v92 shipped ZERO
feedstock in field-zone loot; these rows arrived in a single 2025-02 operator
commit, so removing them moves the server toward its vanilla baseline.

Plan: docs/plans/reward-vectors/IOD-WAVE1-PLAN.md phase C2.

WHY THIS IS A GENERATOR AND NOT A HAND-WRITTEN SPEC. The removal spans 95 zone
files and about 1,800 bags. The selector for each bag is derived from the bag's own
attributes and the `expect` count from its sibling set, so the spec is a pure
function of the datasheet and must be regenerated rather than maintained.

RUN THIS AGAINST A CLEAN SERVER DATASHEET TREE. `migrate` applies with
`--source-ref <server HEAD>`, so a spec is replayed against the COMMITTED baseline,
not the working tree. Generating from a tree that already holds an applied patch
produces `expect` counts for rows that the replay will still find, and silently
narrows the spec to whatever the last apply left behind. The tool refuses to run on
a dirty CompensationData rather than let that happen.

SELECTOR RULES (measured 2026-07-30, and the reason this tool exists):

  * `<ItemBag>` is an AMBIGUOUS collection. Neither `bagName` nor `id` is a key:
    523 of the target bags share a `bagName` with a sibling and 490 are identical
    to a sibling in every attribute.
  * So the tool emits ONE op per (bagName, id) group with `expect: <group size>`,
    never one op per bag. A per-bag spec would make the first op remove all N
    siblings and turn the rest into W500 no-ops.
  * Every bag matching one of these selectors is itself a feedstock bag: measured
    at 0 unsafe selectors over the whole target set. The tool ASSERTS this per
    group and refuses to write the spec if it is ever false, because an over-match
    that reached real loot would be silent.
  * Every feedstock item in these files sits ALONE in its own bag, which is why the
    op is `removeItemBags` and not a bag-content edit.

Requires DSL `d06400c2` or newer for `removeItemBags`.

Usage:
    python reforged/tools/feedstock-faucet/gen_feedstock_bag_removal.py \
        --out reforged/specs/patches/002/41-feedstock-faucet-removal-zones.yaml
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dc-restore"))

from dclib import load_references  # noqa: E402

# Feedstock item family. 94101 survives as the single untiered commodity (R15/R18);
# 94102 to 94112 are retired. Both are removed from zone loot: R13 forbids the faucet
# for the family, not for a tier.
FEEDSTOCK_IDS = {str(i) for i in range(94101, 94113)}

# Only zone 13 is excluded, and only because of the C4 carve-out: its two remaining
# feedstock rows are the classic v31 drops on Vekas (13,1001) and Kugai (13,1004), which
# a user ruling keeps. Everything else in zone 13 is generated and no longer emits
# feedstock at all.
#
# THE OTHER TEN PATCH-002 ZONES ARE IN SCOPE, corrected 2026-07-30 after the first apply.
# Phase C1 neutered the loot GENERATORS so they stop writing feedstock rows, and the plan
# assumed that was sufficient because "the rows this wave removes exist only in the dirty
# tree". That is true of the 299 rows the generators had added; it is FALSE of the 190
# vanilla rows that were already in the committed baseline for zones 2, 3, 5, 6, 7, 15, 16,
# 17, 487 and 488. Not generating a row does not delete a row. Verified by value after the
# first apply: 192 feedstock rows survived, in the eleven zones this patch owns, while all
# 1,595 rows in the 85 zones it does not own were gone. R13 was being enforced everywhere
# EXCEPT where the patch was working.
#
# Ordering note: the `loot/e-compensation/` specs sort after every numbered spec, so they
# run AFTER this one. That is safe because `eCompensations: upsert` merges bags rather than
# replacing a record's whole bag list (measured: the vanilla feedstock bags survived an
# apply of those very specs), so a bag removed here is not restored by them.
EXCLUDED_ZONES = {13}

# Selector attributes. Deliberately NOT the full attribute set.
#
# `bagName` alone was measured safe (zero selectors reach a non-feedstock bag), so any
# superset is safe too; `id` is added because it narrows most groups to a single bag.
#
# `probability` is deliberately EXCLUDED. The DSL matcher cannot match a bag whose
# probability is integral: `probability="1.0"` in the XML fails against `1.0`, `1` and
# `"1.0"` alike, and the failure surfaces as a bare E500. Zone 433 npc 81101 is the
# reproduction. Filed as section 3 of
# docs/dsl-requests/2026-07-30-gacha-randomreward-classless-group-unaddressable.md.
# Leaving it out costs nothing: the selector is already safe without it.
SELECTOR_ATTRS = ("bagName", "id")

HEADER = """spec:
  version: "1.0"
  schema: v92

# GENERATED FILE. Do not hand edit.
#   Regenerate: python reforged/tools/feedstock-faucet/gen_feedstock_bag_removal.py \\
#       --out reforged/specs/patches/002/41-feedstock-faucet-removal-zones.yaml
#
# Remove the direct feedstock drop from field-zone loot outside the patch-002 zones.
#
# Framework: reforged-content-framework 04-power-systems.md 5e ("there is no direct
#   content drop of feedstock in this design, it is downstream of infusion fodder").
#   Ruling R13. Vanilla v92 shipped zero feedstock here; these rows came from a single
#   2025-02 operator import, so this returns the tables to their vanilla shape.
# Plan: docs/plans/reward-vectors/IOD-WAVE1-PLAN.md phase C2.
# Wave: IoD reward-vector wave 1, folded into the open patch 002.
#
# WHY THIS SHIPS NOW. C2 was cut from the wave on 2026-07-28 for one reason: the DSL
# could only replace a compensation's whole bag list, so deleting {rows} bags would
# have made this project the author of {records} complete loot tables it has never
# touched. DSL d06400c2 (2026-07-30) added per-row collection membership, so the spec
# below deletes bags and restates nothing. User ruled it back into the wave the same day.
#
# SCOPE CORRECTED 2026-07-30 after the first apply. This spec originally skipped all
# eleven patch-002 zones on the grounds that phase C1 owned them. C1 stops the loot
# GENERATORS from writing feedstock; it does not delete the rows already in the committed
# baseline, and 190 of those survived the first apply. Ten of the eleven zones are now in
# scope here. Zone 13 stays out: its two remaining rows are the C4 carve-out.
#
# WHAT IT TOUCHES: {records} Compensation records across {files} zone files,
# {rows} feedstock ItemBags, {ops} removal ops. Every feedstock item in these files sits
# alone in its own bag, so no surviving loot row is named anywhere in this spec.
#
# WHY THE OPS CARRY `expect`. ItemBag is an ambiguous collection: bagName is not a key
# and neither is id. {multi} of these selectors legitimately match several attribute-identical
# sibling bags, and every matched sibling was verified to be a feedstock bag before this
# file was written. `expect` states the measured count, so a datasheet that has drifted
# since generation fails the op instead of silently removing the wrong number of bags.
#
# NOT TOUCHED HERE: zone 13, whose surviving feedstock rows are the classic v31 drops on
# Vekas 13,1001 and Kugai 13,1004 (phase C4 carve-out, logged in the IoD divergence log).
#
# eCompensations is server-only in migrate's ENTITY_SYNC_MAP, so this spec has no client leg.

eCompensations:
  update:
"""


def zone_of(path: Path) -> int:
    return int(path.stem.replace("ECompensation_", ""))


def is_feedstock_bag(bag: ET.Element) -> bool:
    return any(i.get("templateId") in FEEDSTOCK_IDS for i in bag.findall("Item"))


def selector_of(bag: ET.Element) -> tuple:
    return tuple(bag.get(a) for a in SELECTOR_ATTRS)


def yaml_scalar(name: str, value: str) -> str:
    """Emit an attribute value with the type the datasheet carries.

    bagName is free text and is frequently Korean, so it is always quoted. id and
    probability are numeric in every shipped row; they are emitted bare so the spec
    reads as data rather than as strings, and a non-numeric value falls back to quoted
    rather than producing invalid YAML.
    """
    if name == "bagName":
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    try:
        float(value)
    except (TypeError, ValueError):
        return '"' + str(value).replace('"', '\\"') + '"'
    return value


def build(datasheet: Path) -> tuple[list[str], dict]:
    comp_dir = datasheet / "CompensationData"
    files = sorted(comp_dir.glob("ECompensation_*.xml"), key=zone_of)

    blocks: list[str] = []
    stats = {"files": 0, "records": 0, "rows": 0, "ops": 0, "multi": 0}

    for path in files:
        zone = zone_of(path)
        if zone in EXCLUDED_ZONES:
            continue
        root = ET.parse(path).getroot()
        file_blocks: list[str] = []

        for comp in root.iter("Compensation"):
            declared = comp.get("huntingZoneId")
            if declared is not None and int(declared) != zone:
                raise SystemExit(
                    f"{path.name}: Compensation declares huntingZoneId={declared} "
                    f"but the file is zone {zone}. The entity key would be wrong."
                )
            npc = comp.get("npcTemplateId")
            if npc is None:
                raise SystemExit(f"{path.name}: Compensation with no npcTemplateId")

            bags = comp.findall("ItemBag")
            groups: OrderedDict[tuple, list[ET.Element]] = OrderedDict()
            for bag in bags:
                if is_feedstock_bag(bag):
                    groups.setdefault(selector_of(bag), []).append(bag)
            if not groups:
                continue

            entries: list[str] = []
            for sel, members in groups.items():
                matched = [b for b in bags if selector_of(b) == sel]
                unsafe = [b for b in matched if not is_feedstock_bag(b)]
                if unsafe:
                    raise SystemExit(
                        f"{path.name} npc {npc}: selector {sel} would also remove "
                        f"{len(unsafe)} bag(s) that hold real loot. Refusing to write."
                    )
                lines = [f"          - {SELECTOR_ATTRS[0]}: {yaml_scalar(SELECTOR_ATTRS[0], sel[0])}"]
                for name, value in zip(SELECTOR_ATTRS[1:], sel[1:]):
                    lines.append(f"            {name}: {yaml_scalar(name, value)}")
                lines.append(f"            expect: {len(matched)}")
                entries.append("\n".join(lines))
                stats["ops"] += 1
                stats["rows"] += len(members)
                if len(matched) > 1:
                    stats["multi"] += 1

            file_blocks.append(
                f"    - huntingZoneId: {zone}\n"
                f"      npcTemplateId: {npc}\n"
                f"      changes:\n"
                f"        removeItemBags:\n" + "\n".join(entries)
            )
            stats["records"] += 1

        if file_blocks:
            stats["files"] += 1
            blocks.append(f"    # --- zone {zone} ({len(file_blocks)} records) ---")
            blocks.extend(file_blocks)

    return blocks, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="spec path to write")
    ap.add_argument("--datasheet", help="server datasheet root (default: .references)")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="skip the clean-baseline check (almost always wrong)")
    args = ap.parse_args()

    datasheet = Path(args.datasheet) if args.datasheet else Path(load_references()["server_datasheet"])

    if not args.allow_dirty:
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", "CompensationData"],
            cwd=datasheet, capture_output=True, text=True,
        )
        if dirty.returncode == 0 and dirty.stdout.strip():
            raise SystemExit(
                "CompensationData is dirty. Specs replay against the COMMITTED baseline, so a "
                "spec generated from an applied tree is wrong. Revert the datasheet tree "
                "(git checkout -- .) and re-run, or pass --allow-dirty if you know better. "
                f"{len(dirty.stdout.strip().splitlines())} dirty path(s)."
            )

    blocks, stats = build(datasheet)

    if not blocks:
        print("nothing to remove: no feedstock bags found outside the excluded zones")
        return 0

    out = Path(args.out)
    out.write_text(HEADER.format(**stats) + "\n".join(blocks) + "\n", encoding="utf-8")

    print(f"wrote {out}")
    print(f"  zone files      : {stats['files']}")
    print(f"  update records  : {stats['records']}")
    print(f"  removal ops     : {stats['ops']}")
    print(f"  feedstock bags  : {stats['rows']}")
    print(f"  multi-match ops : {stats['multi']} (each carries a measured expect > 1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
