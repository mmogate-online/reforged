"""
Feedstock faucet removal, small-faucet leg (IoD reward-vector wave 1, phase C3).

Emits `specs/patches/002/38-feedstock-faucet-removal.yaml`, deleting every remaining
grant of feedstock (94101 to 94112) outside field-zone loot, which phases C1 and C2 own.

Framework: reforged-content-framework 04-power-systems.md 5e, "there is no direct
content drop of feedstock", restated as ruling R13. Fodder dismantling is the only
sanctioned faucet, plus the Kugai token shop, which `03 3b-i` sanctions explicitly and
which this tool must NOT touch.

Plan: docs/plans/reward-vectors/IOD-WAVE1-PLAN.md phase C3.

SEVEN FAMILIES, THREE OP STYLES:

  granular removal (DSL d06400c2, 2026-07-30)
    gachaItems      311 rows: FixedReward rows via removeFixedRewards; RandomReward
                    rows via updateRandomRewards plus removeRewards, then
                    `normalize: true` to rescale the survivors back to a total of 1
                    (needs DSL d04e4015 for the selector, 01e9dbb3 for normalize).
                    All affected groups are classless and each item holds exactly
                    one, so the group selector is a bare `expect: 1`
    itemConversions  80 rows: SeedItem/ResultItem via removeResultItems, and
                    ResultItemSet/ResultItem via updateResultItemSets
    achievements      3 rows: removeItemRewards, keyed on templateId

    eventMatchingEvents 164 rows: removeRewards, keyed on templateId (DSL 36de802c)

  restate the surviving rows (no granular support on these entities)
    buyLists              1 row out of list 2933
    stackAttendanceEvent  4 rows in the QA sample event

  delete the record outright
    exchanges             1 dead ItemMedalExchange row

SELECTOR RULE. Every granular selector states ONLY the item id plus `expect`. Two
reasons: every row it can match is feedstock by construction, so an over-match is
still correct, and the DSL matcher cannot match an attribute whose value is an
integral decimal (see the C2 generator and dsl-request section 3), which rules out
probability. `expect` is measured per container so drift fails the op.

TRAPS THIS TOOL ENCODES, all of which read as "nothing to do" when got wrong:
  * `EventMatching` reward rows are `Compensation@templateId`, NOT `@itemTemplateId`.
  * `Gacha` reward rows are `Reward@itemTemplateId`, NOT `Item@templateId`.
  * `BuyList`'s root is `ItemSellList` with `List@id` and `Item@itemId`.
  * `group: priority` maps to `isSpecialCompensation="true"`. The docs page had this
    backwards; `EventMatchingEventDataMapper.MapGroup` is the authority.
  * `ItemMedalExchange` holds TWO feedstock rows. Only the dead `94105 / 91966` one
    goes; `94101 / 95216` is the Kugai token shop and is sanctioned.

Usage:
    python reforged/tools/feedstock-faucet/gen_feedstock_faucet_removal.py \
        --out reforged/specs/patches/002/38-feedstock-faucet-removal.yaml
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dc-restore"))

from dclib import load_references  # noqa: E402

FEEDSTOCK_IDS = {str(i) for i in range(94101, 94113)}

# The one feedstock exchange that STAYS: the Kugai token shop row.
KUGAI_EXCHANGE = ("94101", "95216")
# The dead vanilla Feedstock Exchange Shop, which goes.
DEAD_EXCHANGE = ("94105", "91966")
DEAD_BUYLIST = "2933"


def q(value: str) -> str:
    """Quote a value unless it is a plain integer. Floats are never emitted by this
    tool as a SELECTOR value: the matcher cannot match an integral decimal, so no
    selector carries one. Rebalanced probabilities are emitted as literal payload
    values, which is a different thing and is safe."""
    if value is None:
        return '""'
    try:
        int(value)
        return value
    except ValueError:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


# `<RandomReward>` is a SUM-TO-1 BAG, and the DSL now enforces it.
#
# Measured over server HEAD: all 3,597 groups in Gacha*.xml total 1 within 1e-6, as do
# all 139 RandomOutput groups in DecompositionData.xml. Deleting a weighted row leaves
# the group short, and the world server REFUSES TO BOOT on it:
#     randomReward invalid probability prov [itemTemplateId=19321] [0.900000]
# (the id there is the BOX, not a reward row).
#
# This tool used to carry its own proportional rebalance and emit the rescaled survivor
# rows explicitly, roughly 700 of them across 81 groups, because `<Reward>` is a value
# collection with no `upsert*` able to edit a probability in place. DSL `01e9dbb3`
# (2026-07-30) shipped both halves of the request filed as
# docs/dsl-requests/2026-07-30-probability-bag-sum-not-validated.md: a run that leaves
# such a bag off 1 is now refused with E573 before anything is written, and
# `normalize: true` on the group selector rescales the survivors proportionally. So the
# arithmetic moved into the DSL and this generator just asks for it.
#
# `normalize` runs AFTER every add/remove on the group, scales every remaining row, and
# parks its rounding residual on the largest row with ties going to the earliest, which
# is what makes a re-apply a no-op instead of a slow drift.
#
# Note none of this applies to `ECompensation` ItemBags, which are NOT a sum-to-1 bag:
# their most common non-1 total is exactly 2, on 594 groups, in named per-dungeon rune
# families. That is a design, not authoring error, and it is why spec 002/41 can delete
# 1,785 whole bags without touching anything else.


def gacha_block(ds: Path) -> tuple[list[str], dict]:
    stats = Counter()
    records: list[str] = []
    for path in sorted(ds.glob("Gacha*.xml")):
        root = ET.parse(path).getroot()
        for gi in root.iter("GachaItem"):
            fixed: list[str] = []
            random_groups: list[str] = []

            for container in gi.findall("FixedReward"):
                rows = container.findall("Reward")
                hits = Counter(
                    r.get("itemTemplateId") for r in rows if r.get("itemTemplateId") in FEEDSTOCK_IDS
                )
                for item_id, _ in sorted(hits.items()):
                    matched = sum(1 for r in rows if r.get("itemTemplateId") == item_id)
                    fixed.append(f"          - itemTemplateId: {item_id}\n            expect: {matched}")
                    stats["fixed_rows"] += matched
                    stats["fixed_ops"] += 1

            groups = gi.findall("RandomReward")
            dead_groups = 0
            for index, group in enumerate(groups):
                rows = group.findall("Reward")
                hits = Counter(
                    r.get("itemTemplateId") for r in rows if r.get("itemTemplateId") in FEEDSTOCK_IDS
                )
                if not hits:
                    continue
                if sum(hits.values()) == len(rows):
                    # Every row goes, so the GROUP goes. The client XSD declares
                    # RandomReward/Reward without minOccurs="0", so an emptied group is
                    # XSD-invalid and the sync refuses the whole file with E650.
                    if len(groups) != 1:
                        raise SystemExit(
                            f"{path.name} gachaItem {gi.get('itemTemplateId')}: a fully "
                            f"feedstock RandomReward group among {len(groups)} groups. A bare "
                            f"`expect` selector would remove all of them; author this one by hand."
                        )
                    dead_groups += 1
                    stats["random_rows"] += sum(hits.values())
                    stats["dead_groups"] += 1
                    continue
                # PARTIAL removal. The group survives, so it must still total 1.
                cls = group.get("class")
                if cls is not None:
                    selector = f"          - class: {q(cls)}"
                elif len(groups) == 1:
                    # Classless group, and the item holds exactly one. A bare `expect`
                    # names it; `class: ""` would match nothing and `at` is refused.
                    selector = "          - expect: 1"
                else:
                    raise SystemExit(
                        f"{path.name} gachaItem {gi.get('itemTemplateId')}: classless "
                        f"RandomReward among {len(groups)} groups. No selector can name it; "
                        f"see dsl-requests/2026-07-30-gacha-randomreward-classless-group-unaddressable.md"
                    )
                lines = [selector, "            removeRewards:"]
                for item_id, _ in sorted(hits.items()):
                    matched = sum(1 for r in rows if r.get("itemTemplateId") == item_id)
                    lines.append(f"              - itemTemplateId: {item_id}")
                    lines.append(f"                expect: {matched}")
                    stats["random_rows"] += matched
                    stats["random_ops"] += 1
                # Rescale the survivors back to a total of 1. Without this the run is
                # refused with E573, and before the DSL had it the world server refused
                # to boot instead. See the note above `rebalance()`.
                lines.append("            normalize: true")
                stats["normalized_groups"] += 1
                random_groups.append("\n".join(lines))

            if not fixed and not random_groups and not dead_groups:
                continue
            body = [f"    - itemTemplateId: {gi.get('itemTemplateId')}", "      changes:"]
            if fixed:
                body.append("        removeFixedRewards:")
                body.extend(fixed)
            if dead_groups:
                body.append("        removeRandomRewardGroups:")
                body.append(f"          - expect: {len(groups)}")
            if random_groups:
                body.append("        updateRandomRewards:")
                body.extend(random_groups)
            records.append("\n".join(body))
            stats["records"] += 1
    return records, stats


def item_conversion_block(ds: Path) -> tuple[list[str], dict]:
    stats = Counter()
    records: list[str] = []
    for path in sorted(ds.glob("ItemConversion*.xml")):
        root = ET.parse(path).getroot()
        for seed in root.iter("SeedItem"):
            direct: list[str] = []
            rows = seed.findall("ResultItem")
            hits = Counter(r.get("templateId") for r in rows if r.get("templateId") in FEEDSTOCK_IDS)
            for item_id, _ in sorted(hits.items()):
                matched = sum(1 for r in rows if r.get("templateId") == item_id)
                direct.append(f"          - templateId: {item_id}\n            expect: {matched}")
                stats["direct_rows"] += matched
                stats["direct_ops"] += 1

            set_edits: list[str] = []
            dead_sets = 0
            sets = seed.findall("ResultItemSet")
            for index, rset in enumerate(sets):
                srows = rset.findall("ResultItem")
                shits = Counter(
                    r.get("templateId") for r in srows if r.get("templateId") in FEEDSTOCK_IDS
                )
                if not shits:
                    continue
                if sum(shits.values()) == len(srows):
                    # An emptied ResultItemSet is XSD-valid but semantically dead: the
                    # conversion would still roll that slot and grant nothing. Remove it.
                    if len(sets) != 1:
                        raise SystemExit(
                            f"{path.name} seed {seed.get('itemTemplateId')}: a fully feedstock "
                            f"ResultItemSet among {len(sets)} sets. A bare `expect` selector would "
                            f"remove all of them, and an `at` index would shift under the other "
                            f"edits on this seed; author this one by hand."
                        )
                    dead_sets += 1
                    stats["set_rows"] += sum(shits.values())
                    stats["dead_sets"] += 1
                    continue
                set_id = rset.get("id")
                if set_id is not None:
                    twins = sum(1 for s in sets if s.get("id") == set_id)
                    selector = [f"          - id: {set_id}", f"            expect: {twins}"]
                else:
                    # No id and probability is unmatchable, so name it by position.
                    selector = [f"          - at: {index}"]
                lines = selector + ["            removeResultItems:"]
                for item_id, _ in sorted(shits.items()):
                    matched = sum(1 for r in srows if r.get("templateId") == item_id)
                    lines.append(f"              - templateId: {item_id}")
                    lines.append(f"                expect: {matched}")
                    stats["set_rows"] += matched
                    stats["set_ops"] += 1
                set_edits.append("\n".join(lines))

            if not direct and not set_edits and not dead_sets:
                continue
            body = [f"    - itemTemplateId: {seed.get('itemTemplateId')}", "      changes:"]
            if direct:
                body.append("        removeResultItems:")
                body.extend(direct)
            if dead_sets:
                body.append("        removeResultItemSets:")
                body.append(f"          - expect: {len(sets)}")
            if set_edits:
                body.append("        updateResultItemSets:")
                body.extend(set_edits)
            records.append("\n".join(body))
            stats["records"] += 1
    return records, stats


def achievement_block(ds: Path) -> tuple[list[str], dict]:
    stats = Counter()
    records: list[str] = []
    for path in sorted(ds.glob("AchievementList*.xml")):
        root = ET.parse(path).getroot()
        for ach in root.iter("Achievement"):
            hits = sorted(
                {r.get("templateId") for r in ach.iter("ItemReward") if r.get("templateId") in FEEDSTOCK_IDS}
            )
            if not hits:
                continue
            body = [f"    - id: {ach.get('id')}", "      changes:", "        removeItemRewards:"]
            for item_id in hits:
                body.append(f"          - templateId: {item_id}")
                stats["rows"] += 1
            records.append("\n".join(body))
            stats["records"] += 1
    return records, stats


def event_matching_block(ds: Path) -> tuple[list[str], dict]:
    """Remove each affected event's feedstock reward row by key.

    Uses `removeRewards`, delivered as DSL 36de802c on 2026-07-30 in answer to
    docs/dsl-requests/2026-07-30-eventmatching-rewards-no-collection-membership.md.
    The collection is measured keyed on `templateId` (present on all 2,049 shipped rows,
    repeating in none of the 457 containers), so the key resolves to at most one row and
    the site takes no `expect`, no `at` and no `allowDuplicate`: stating one is a parse
    error, not a field that is quietly ignored.

    Before that landed this leg restated 934 surviving rows to delete 164, which was 73%
    of this spec. Nothing surviving is named any more.
    """
    stats = Counter()
    records: list[str] = []
    root = ET.parse(ds / "EventMatching.xml").getroot()
    for group in root.findall("EventGroup"):
        # MapGroup: "priority" => true, "secondary" => false. The docs page is inverted.
        name = "priority" if group.get("isSpecialCompensation") == "true" else "secondary"
        for event in group.findall("Event"):
            for comp_list in event.findall("CompensationList"):
                hits = sorted(
                    {r.get("templateId") for r in comp_list if r.get("templateId") in FEEDSTOCK_IDS}
                )
                if not hits:
                    continue
                body = [
                    f"    - eventId: {event.get('id')}",
                    f"      group: {name}",
                    "      changes:",
                    "        removeRewards:",
                ]
                for item_id in hits:
                    body.append(f"          - templateId: {item_id}")
                records.append("\n".join(body))
                stats["records"] += 1
                stats["rows"] += len(hits)
                stats[name] += len(hits)
    return records, stats


def buy_list_block(ds: Path) -> tuple[list[str], dict]:
    stats = Counter()
    root = ET.parse(ds / "BuyList.xml").getroot()
    for sell_list in root.iter("List"):
        if sell_list.get("id") != DEAD_BUYLIST:
            continue
        survivors = [i for i in sell_list.findall("Item") if i.get("itemId") not in FEEDSTOCK_IDS]
        removed = len(sell_list.findall("Item")) - len(survivors)
        if not removed:
            return [], stats
        body = [f"    - id: {DEAD_BUYLIST}", "      changes:", "        items:"]
        for item in survivors:
            body.append(f"          - itemId: {item.get('itemId')}")
            revision = item.get("priceRevision")
            if revision is not None:
                body.append(f"            priceRevision: {q(revision)}")
        stats["rows"] = removed
        stats["survivors"] = len(survivors)
        return ["\n".join(body)], stats
    return [], stats


def exchange_block(ds: Path) -> tuple[list[str], dict]:
    stats = Counter()
    root = ET.parse(ds / "ItemMedalExchange.xml").getroot()
    records: list[str] = []
    for exchange in root.iter("Exchange"):
        pair = (exchange.get("itemId"), exchange.get("medalItemId"))
        if pair[0] not in FEEDSTOCK_IDS:
            continue
        if pair == KUGAI_EXCHANGE:
            stats["kept"] += 1
            continue
        if pair != DEAD_EXCHANGE:
            raise SystemExit(
                f"ItemMedalExchange: unexpected feedstock row {pair}. Only the dead "
                f"{DEAD_EXCHANGE} row is in scope and {KUGAI_EXCHANGE} is sanctioned. "
                f"Rule on this row before regenerating."
            )
        records.append(f"    - itemId: {pair[0]}\n      medalItemId: {pair[1]}")
        stats["rows"] += 1
    return records, stats


def stack_attendance_block(ds: Path) -> tuple[list[str], dict]:
    stats = Counter()
    root = ET.parse(ds / "StackAttendanceEvent.xml").getroot()
    blocks: list[str] = []
    for sample in root.iter("SampleEvent"):
        rewards = sample.findall("Reward")
        survivors = [r for r in rewards if r.get("itemTemplateId") not in FEEDSTOCK_IDS]
        stats["rows"] += len(rewards) - len(survivors)
        body = []
        for key in ("conditionType", "resetHour", "startTime", "endTime"):
            value = sample.get(key)
            if value is not None:
                body.append(f"    - {key}: {q(value)}" if not body else f"      {key}: {q(value)}")
        body.append("      rewards:")
        for reward in survivors:
            first = True
            for key in ("day", "itemTemplateId", "itemAmount", "highlight"):
                value = reward.get(key)
                if value is None:
                    continue
                prefix = "        - " if first else "          "
                body.append(f"{prefix}{key}: {value if key == 'highlight' else q(value)}")
                first = False
        blocks.append("\n".join(body))
        stats["survivors"] += len(survivors)
    if not stats["rows"]:
        return [], stats
    return blocks, stats


HEADER = """spec:
  version: "1.0"
  schema: v92

# GENERATED FILE. Do not hand edit.
#   Regenerate: python reforged/tools/feedstock-faucet/gen_feedstock_faucet_removal.py \\
#       --out reforged/specs/patches/002/38-feedstock-faucet-removal.yaml
#
# Delete every remaining feedstock faucet outside field-zone loot.
#
# Framework: reforged-content-framework 04-power-systems.md 5e ("there is no direct
#   content drop of feedstock in this design"). Ruling R13. Fodder dismantling is the
#   only sanctioned source.
# Plan: docs/plans/reward-vectors/IOD-WAVE1-PLAN.md phase C3.
# Wave: IoD reward-vector wave 1, folded into the open patch 002.
#
# WHAT IT REMOVES
#   gachaItems            {gacha_rows} reward rows across {gacha_records} gacha items
#                         ({gacha_fixed} fixed, {gacha_random} random)
#   itemConversions       {conv_rows} result rows across {conv_records} seed items
#   achievements          {ach_rows} item rewards on {ach_records} achievements
#   eventMatchingEvents   {em_rows} Vanguard rows across {em_records} (event, group) pairs,
#                         split {em_priority} priority and {em_secondary} secondary
#   buyLists              {buy_rows} row from the dead Feedstock Exchange list {buylist}
#   exchanges             {exch_rows} dead ItemMedalExchange row
#   stackAttendanceEvent  {sae_rows} rows from the QA sample event
#
# WHAT IT DELIBERATELY KEEPS
#   The Kugai token shop exchange 94101 / 95216. Framework 03 3b-i sanctions a token
#   shop selling feedstock, so a family-wide sweep here would have been wrong.
#   BuyList {buylist}'s sibling item 138294.
#
# TWO FAMILIES ARE RESTATED, NOT EDITED IN PLACE. `buyLists.items` and
# `stackAttendanceEvent.sampleEvents` are clear-and-replace and have no membership keys,
# so every surviving row in those two is restated below and must be diffed against
# committed HEAD after apply. Between them that is {buy_survivors} BuyList item and
# {sae_survivors} attendance rewards, which is small enough to read.
#
# `eventMatchingEvents` USED to be the third and by far the largest: it restated 934
# surviving rows to delete 164, 73% of this file. DSL 36de802c (2026-07-30) added
# `removeRewards` keyed on templateId, so that leg now names only what it deletes. The
# mail strings on each CompensationList were never at risk either way: they live on the
# container and resolve independently.
#
# GROUP MAPPING: `priority` is isSpecialCompensation="true". The DSL docs page states
# this backwards; EventMatchingEventDataMapper.MapGroup is the authority.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--datasheet")
    args = ap.parse_args()

    ds = Path(args.datasheet) if args.datasheet else Path(load_references()["server_datasheet"])

    gacha, gs = gacha_block(ds)
    conv, cs = item_conversion_block(ds)
    ach, as_ = achievement_block(ds)
    em, es = event_matching_block(ds)
    buy, bs = buy_list_block(ds)
    exch, xs = exchange_block(ds)
    sae, ss = stack_attendance_block(ds)

    fields = {
        "gacha_rows": gs["fixed_rows"] + gs["random_rows"],
        "gacha_records": gs["records"],
        "gacha_fixed": gs["fixed_rows"],
        "gacha_random": gs["random_rows"],
        "conv_rows": cs["direct_rows"] + cs["set_rows"],
        "conv_records": cs["records"],
        "ach_rows": as_["rows"],
        "ach_records": as_["records"],
        "em_rows": es["rows"],
        "em_records": es["records"],
        "em_priority": es["priority"],
        "em_secondary": es["secondary"],
        "buy_rows": bs["rows"],
        "exch_rows": xs["rows"],
        "sae_rows": ss["rows"],
        "buylist": DEAD_BUYLIST,
        "buy_survivors": bs["survivors"],
        "sae_survivors": ss["survivors"],
    }

    parts = [HEADER.format(**fields)]
    if gacha:
        parts.append("\ngachaItems:\n  update:\n" + "\n".join(gacha))
    if conv:
        parts.append("\nitemConversions:\n  update:\n" + "\n".join(conv))
    if ach:
        parts.append("\nachievements:\n  update:\n" + "\n".join(ach))
    if em:
        parts.append("\neventMatchingEvents:\n  update:\n" + "\n".join(em))
    if buy:
        parts.append("\nbuyLists:\n  update:\n" + "\n".join(buy))
    if exch:
        parts.append("\nexchanges:\n  delete:\n" + "\n".join(exch))
    if sae:
        parts.append("\nstackAttendanceEvent:\n  sampleEvents:\n" + "\n".join(sae))

    Path(args.out).write_text("\n".join(parts) + "\n", encoding="utf-8")

    print(f"wrote {args.out}")
    for key, value in fields.items():
        print(f"  {key:16s}: {value}")
    print(f"  exchanges kept  : {xs['kept']} (the Kugai token shop row)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
