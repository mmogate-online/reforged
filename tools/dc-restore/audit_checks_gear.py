"""Gear reward checks: the class ladder, visual sets, repeatables, class rows.

Four checks, each born from a defect that survived every existing gate on the
Island of Dawn and had to be found by a human playing the zone.

  class-matrix           Brawler (FIGHTER) and Ninja (ASSASSIN) were handed the
                         same level-2 weapon by four separate zone-13 quests and
                         never got a level-3, level-4, level-8 or level-11
                         upgrade at all, while nine other classes did. Two
                         reward generators each carried a private per-class
                         weapon pool, and neither pool agreed with the other.
  set-completeness       No gear set below level 7 was completable. The level-4
                         visual tier was granted body-only, so six of its nine
                         pieces came from no quest in the entire game, and all
                         three level-3 body pieces likewise.
  repeatable-rewards     A repeatable quest that hands out real gear is a farm.
                         The redistribution wave had to exclude set carriers by
                         hand because nothing checked for it.
  reward-class-coverage  Quest 1322's leather rows list four classes while the
                         item's own requiredClass admits five.

Two rules that the earlier attempts at this got wrong, and that the tests pin:

  Order by the ITEM's requiredLevel, never the quest's 최소레벨 gate. Island of
  Dawn deliberately grants level-4 items from level-1 quests, so quest-gate
  ordering invents plateaus that do not exist.

  Equipment means dclib.EQUIPMENT_TYPES, never combat_type.startswith("EQUIP").
  The prefix also matches 55,739 cosmetic, underwear and inheritance items in
  the merged item model, which would make repeatable-rewards fire on every
  costume repeatable in the game.
"""

from __future__ import annotations

from auditlib import Corpus, Finding, Scope, check, item_label

# The playable roster, in a fixed order so output is stable. It must stay the
# same thirteen classes dclib.CLASS_ARMOUR maps to armour families;
# test_check_gear.py asserts the two never drift apart.
FULL_ROSTER: tuple[str, ...] = (
    "LANCER", "BERSERKER", "ENGINEER", "FIGHTER",
    "WARRIOR", "SLAYER", "ARCHER", "GLAIVER", "SOULLESS",
    "SORCERER", "PRIEST", "ELEMENTALIST", "ASSASSIN",
)

# Reaper (SOULLESS) has no low-level gear and is omitted from Island of Dawn by
# doctrine, so auditing it against a peer roster reports a gap in every band. It
# stays a parameter rather than a constant because the omission is a per-region
# ruling, not a property of the data.
DEFAULT_ROSTER: tuple[str, ...] = tuple(c for c in FULL_ROSTER if c != "SOULLESS")

# One band per distinct item requiredLevel. Measured at the pinned baseline:
# widening the band to 4 drops the zone-13 weapon plateau from 20 empty cells to
# 0, because Brawler's level-2 weapon and everyone else's level-4 weapon land in
# the same bucket and the cell stops looking empty. A band wider than the gap it
# is meant to expose cannot expose it.
DEFAULT_BAND_SIZE = 1

REPEAT_VALUE = "반복"

# Where a piece of equipment is worn. Armour reports body / hand / feet from
# combatItemSubType; weapons and accessories have no subtype slot, so the
# combatItemType supplies the group. Grouping matters: a class whose weapon
# ladder stalls still has armour in the same band, and a matrix that mixes the
# two shows a filled cell for a class holding nothing but a level-2 sword.
WEAPON_GROUP = "weapon"
ACCESSORY_GROUP = "accessory"


def _slot_group(info) -> str:
    if info.combat_type == "EQUIP_WEAPON":
        return WEAPON_GROUP
    if info.combat_type == "EQUIP_ACCESSORY":
        return ACCESSORY_GROUP
    return info.slot or info.combat_type.lower()


def _band(level: int | None, band_size: int) -> str:
    """Label for the band an item requiredLevel falls in.

    Items with no requiredLevel get their own label and are excluded from the
    empty-cell condition: an unordered item cannot prove a hole in an ordering.
    """
    if level is None:
        return "lv?"
    if band_size <= 1:
        return f"lv{level}"
    start = ((level - 1) // band_size) * band_size + 1
    return f"lv{start}-{start + band_size - 1}"


def _band_sort_key(label: str) -> tuple:
    body = label[2:]
    if not body or not body[0].isdigit():
        return (1, 0, label)
    return (0, int(body.split("-")[0]), label)


def equipment_grants(corpus: Corpus, quest_ids) -> list[tuple[int, int, str]]:
    """(quest id, item id, row class) for every equipment grant in quest_ids.

    Row class is the lowercase compensation `class` attribute, uppercased, or ""
    when the row is untagged and the grant applies to whoever the item admits.
    """
    out: list[tuple[int, int, str]] = []
    for gid in quest_ids:
        payload = corpus.rewards.get(gid)
        if not payload:
            continue
        for template, _qty, cls in payload["items"]:
            if not template.isdigit():
                continue
            info = corpus.items.get(int(template))
            if info is None or not info.is_equipment:
                continue
            out.append((gid, int(template), cls.strip().upper()))
    return out


def _classes_for(info, row_class: str, roster: tuple[str, ...]) -> list[str]:
    """Roster classes a grant row actually reaches."""
    if row_class:
        return [row_class] if row_class in roster else []
    return [c for c in roster if info.admits(c)]


# ---------------------------------------------------------------------------
# class-matrix
# ---------------------------------------------------------------------------

@check("class-matrix", "reward-integrity",
       "Class by level-band matrix of granted equipment. Flags the same item "
       "granted twice to one class inside a band, and a class/band cell left "
       "empty while peer classes' cells are filled.")
def check_class_matrix(corpus: Corpus, scope: Scope,
                       roster: tuple[str, ...] = DEFAULT_ROSTER,
                       band_size: int = DEFAULT_BAND_SIZE) -> list[Finding]:
    """Every class should get a real ladder, and never the same rung twice.

    Brawler and Ninja were stuck on their level-2 weapon across four zone-13
    quests while nine other classes climbed levels 2, 3, 4, 8 and 11. Each
    individual grant was valid; only the matrix makes the stall visible, and
    only when it is ordered by the item's requiredLevel. Ordering by the quest's
    최소레벨 gate reports plateaus that are not there, because Island of Dawn
    deliberately hands level-4 items out of level-1 quests.

    The matrix is built per equipment slot group. Mixing weapons and armour
    fills Brawler's level-4 cell with a chest piece and hides the weapon that
    never arrived.
    """
    findings: list[Finding] = []
    subject_quests = scope.subject_quests(corpus)

    # (slot group, band) -> class -> item id -> granting quest ids
    cells: dict[tuple[str, str], dict[str, dict[int, set[int]]]] = {}
    for gid, item_id, row_class in equipment_grants(corpus, sorted(subject_quests)):
        info = corpus.items.get(item_id)
        cell = (_slot_group(info), _band(info.required_level, band_size))
        for cls in _classes_for(info, row_class, roster):
            cells.setdefault(cell, {}).setdefault(cls, {}).setdefault(item_id, set()).add(gid)

    # Condition 1: the same item handed to one class more than once in a band.
    for (group, band), by_class in sorted(cells.items(), key=lambda kv: (kv[0][0], _band_sort_key(kv[0][1]))):
        for cls in roster:
            for item_id, quests in sorted(by_class.get(cls, {}).items()):
                if len(quests) < 2:
                    continue
                quest_list = sorted(quests)
                findings.append(Finding(
                    severity="high",
                    check="class-matrix",
                    subject=item_label(corpus, item_id),
                    detail=f"{cls}:{'+'.join(str(q) for q in quest_list)}",
                    message=(f"{cls} is granted the same {group} {band} item by quests "
                             f"{', '.join(str(q) for q in quest_list)}: no upgrade between them"),
                    evidence={"quest": quest_list[0], "quests": quest_list, "item": item_id,
                              "class": cls, "slot": group, "band": band},
                ))

    # Condition 2: an empty cell with filled peers. "lv?" is excluded because an
    # item with no requiredLevel has no place in the ordering to be missing from.
    for (group, band), by_class in sorted(cells.items(), key=lambda kv: (kv[0][0], _band_sort_key(kv[0][1]))):
        if band == "lv?":
            continue
        filled = [c for c in roster if by_class.get(c)]
        empty = [c for c in roster if not by_class.get(c)]
        if not filled or not empty:
            continue
        peer_quests = sorted({q for items in by_class.values()
                              for quests in items.values() for q in quests})
        for cls in empty:
            findings.append(Finding(
                severity="high",
                check="class-matrix",
                subject=cls,
                detail=f"{group}:{band}",
                message=(f"no {group} at {band} while {len(filled)} peer classes have one "
                         f"(from quests {', '.join(str(q) for q in peer_quests)})"),
                # A gap belongs to the quests that filled the band for everyone
                # else: those are the payouts that should have covered this
                # class, and the ones a --quests run is reviewing.
                evidence={"quest": peer_quests[0] if peer_quests else None,
                          "quests": peer_quests, "class": cls, "slot": group,
                          "band": band, "filled": filled},
            ))

    return findings


# ---------------------------------------------------------------------------
# set-completeness
# ---------------------------------------------------------------------------

@check("set-completeness", "reward-integrity",
       "A visual gear set (family, tier) whose slots are only partly granted by "
       "quests. Evidence is corpus-wide; findings are reported per subject zone.")
def check_set_completeness(corpus: Corpus, scope: Scope) -> list[Finding]:
    """A set nobody can finish is worse than a set nobody is offered.

    The level-4 visual tier was granted body-only, so six of its nine pieces
    came from no quest anywhere in the game, and the three level-3 body pieces
    likewise. A player saw two thirds of a set and could never complete it.

    Evidence has to be corpus-wide or this is worse than useless: a zone-scoped
    read calls every set that continues into the next region incomplete, and
    misses the out-of-zone quest that already grants the missing slot. The
    level-6 tier really is completed by quest 59906, well outside the island.

    A set granted by nobody at all is not reported. It is not a broken reward,
    it is content that was never handed out, and it belongs to no zone.
    """
    findings: list[Finding] = []
    subject_quests = scope.subject_quests(corpus)

    # Corpus-wide: which quests grant which item.
    granting: dict[int, set[int]] = {}
    for gid, item_id, _cls in equipment_grants(corpus, sorted(corpus.quests)):
        granting.setdefault(item_id, set()).add(gid)

    for set_key, slots in sorted(corpus.items.sets().items()):
        family, tier = set_key
        granted: dict[str, list[int]] = {}
        missing_items: dict[str, list[int]] = {}
        for slot, item_ids in slots.items():
            quests = sorted({q for i in item_ids for q in granting.get(i, ())})
            if quests:
                granted[slot] = quests
            else:
                missing_items[slot] = sorted(item_ids)
        if not granted or not missing_items:
            continue  # fully granted, or never granted at all

        all_quests = sorted({q for quests in granted.values() for q in quests})
        in_subject = sorted(q for q in all_quests if q in subject_quests)
        if not in_subject:
            continue

        missing = sorted(missing_items)
        by_slot = {slot: granted[slot] for slot in sorted(granted)}
        findings.append(Finding(
            severity="high",
            check="set-completeness",
            subject=f"set {family}/{tier}",
            detail="+".join(missing),
            message=(f"slot(s) {', '.join(missing)} granted by no quest in the corpus; "
                     + "; ".join(f"{slot} from {', '.join(str(q) for q in quests)}"
                                 for slot, quests in by_slot.items())),
            evidence={"quest": in_subject[0], "quests": all_quests,
                      "subject_quests": in_subject, "family": family, "tier": tier,
                      "granted": by_slot, "missing_slots": missing,
                      "missing_items": {s: missing_items[s] for s in missing},
                      "zones": sorted({corpus.quests[q]["hz"] for q in in_subject
                                       if corpus.quests[q].get("hz") is not None})},
        ))

    return findings


# ---------------------------------------------------------------------------
# repeatable-rewards
# ---------------------------------------------------------------------------

def is_repeatable(quest: dict) -> bool:
    """반복퀘스트 = 반복 or 퀘스트종류 = 반복. Both encodings exist in the corpus.

    At the pinned baseline 36 quests carry the first and 11 the second, and the
    two sets do not overlap, so testing only one misses a quarter of them.
    """
    return quest.get("repeat", "") == REPEAT_VALUE or quest.get("quest_type", "") == REPEAT_VALUE


@check("repeatable-rewards", "reward-integrity",
       "A repeatable quest granting real equipment. Equipment is the "
       "EQUIPMENT_TYPES allow-list, not the EQUIP prefix, which also matches "
       "cosmetics and underwear.")
def check_repeatable_rewards(corpus: Corpus, scope: Scope) -> list[Finding]:
    """A repeatable quest that grants gear is a farm, not a reward.

    The redistribution wave had to exclude set carriers from the repeatable
    quests by hand, because nothing checked for it and a repeatable holding one
    piece of a unique set can be run until the piece is worthless.

    Two traps this check exists to avoid. The first is combat_type.startswith
    ("EQUIP"), which matches 55,739 cosmetic, underwear and inheritance items in
    the merged model and would fire on every costume repeatable in the game.
    The second is 최대레벨: a level cap is not a trigger, 777 quests carry one,
    and only the conjunction of repeatable and an equipment grant is a defect.
    """
    findings: list[Finding] = []
    for gid, quest in sorted(scope.subject_quests(corpus).items()):
        if not is_repeatable(quest):
            continue
        by_item: dict[int, set[str]] = {}
        for _gid, item_id, row_class in equipment_grants(corpus, [gid]):
            by_item.setdefault(item_id, set()).add(row_class)
        for item_id, classes in sorted(by_item.items()):
            info = corpus.items.get(item_id)
            findings.append(Finding(
                severity="high",
                check="repeatable-rewards",
                subject=f"quest-{gid}",
                detail=str(item_id),
                message=(f"repeatable quest grants equipment {item_label(corpus, item_id)} "
                         f"({info.combat_type}, requiredLevel {info.required_level}): farmable"),
                evidence={"quest": gid, "item": item_id, "combat_type": info.combat_type,
                          "required_level": info.required_level,
                          "classes": sorted(c for c in classes if c),
                          "max_level": quest.get("max_level", "")},
            ))
    return findings


# ---------------------------------------------------------------------------
# reward-class-coverage
# ---------------------------------------------------------------------------

@check("reward-class-coverage", "reward-integrity",
       "A class-gated equipment grant whose compensation rows disagree with the "
       "item's own requiredClass, in either direction.")
def check_reward_class_coverage(corpus: Corpus, scope: Scope,
                                roster: tuple[str, ...] = FULL_ROSTER) -> list[Finding]:
    """The rows and the item must agree on who the gear is for.

    Quest 1322 lists four classes on its leather boots while the item admits
    five. Missing a class means that class walks away from a payout with
    nothing; listing a class the item rejects means a row that can never pay.

    The roster defaults to the FULL thirteen here, unlike class-matrix. The
    fifth leather class is Reaper, whose omission on Island of Dawn is a
    doctrine ruling, and a ruling recorded in the waiver file is auditable while
    the same ruling hardcoded into a roster constant is invisible. That is also
    the only reason this check has a positive oracle at all: with Reaper dropped
    from the roster the corpus produces zero coverage findings.

    ItemTemplate spells classes UPPERCASE and compensation rows lowercase.
    ItemInfo normalizes both, so nothing here compares raw strings.
    """
    findings: list[Finding] = []
    subject_quests = scope.subject_quests(corpus)

    rows: dict[tuple[int, int], set[str]] = {}
    for gid, item_id, row_class in equipment_grants(corpus, sorted(subject_quests)):
        rows.setdefault((gid, item_id), set()).add(row_class)

    for (gid, item_id), classes in sorted(rows.items()):
        info = corpus.items.get(item_id)
        if not info.required_class:
            continue  # unrestricted gear has no coverage obligation
        tagged = {c for c in classes if c}
        if not tagged:
            continue  # an untagged grant reaches everyone the item admits
        uncovered = [c for c in roster if info.admits(c) and c not in tagged]
        wrong = sorted(c for c in tagged if not info.admits(c))

        if uncovered:
            findings.append(Finding(
                severity="medium",
                check="reward-class-coverage",
                subject=item_label(corpus, item_id),
                detail=f"{gid}:uncovered:{'+'.join(uncovered)}",
                message=(f"quest {gid} covers {', '.join(sorted(tagged))} but the item admits "
                         f"{', '.join(uncovered)} as well: those classes are paid nothing"),
                evidence={"quest": gid, "item": item_id, "rows": sorted(tagged),
                          "admits": sorted(info.required_class), "uncovered": uncovered},
            ))
        if wrong:
            findings.append(Finding(
                severity="medium",
                check="reward-class-coverage",
                subject=item_label(corpus, item_id),
                detail=f"{gid}:wrong-class:{'+'.join(wrong)}",
                message=(f"quest {gid} pays {', '.join(wrong)} an item requiring "
                         f"{', '.join(sorted(info.required_class))}: the row can never pay"),
                evidence={"quest": gid, "item": item_id, "rows": sorted(tagged),
                          "admits": sorted(info.required_class), "wrong_class": wrong},
            ))

    return findings
