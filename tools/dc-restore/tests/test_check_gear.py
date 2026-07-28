"""The four gear reward checks.

Each check owes its existence to a defect that reached a live server and was
found by a person playing the zone, not by a gate.

class-matrix
    Positive oracle: at the pinned baseline, zone 13 hands Brawler (FIGHTER) and
    Ninja (ASSASSIN) the same level-2 weapon from four separate quests and gives
    them no level-3, level-4, level-8 or level-11 weapon at all while nine peer
    classes climb every rung. Measured: 20 empty weapon cells, 0 on the working
    tree after the patch-002 wave. Negative oracle: the working tree still
    grants the identical level-7 weapon and body piece from two quests each, and
    the check reports exactly those 24 and nothing else. Fire-then-quiet holds
    for the empty-cell condition; the repeat condition is documented below as
    still firing, on a real and different pair.

set-completeness
    Positive oracle: the level-4 visual tier was granted body-only, leaving the
    six requiredLevel-4 hand and feet pieces granted by no quest in the corpus,
    and all three requiredLevel-3 body pieces likewise. Negative oracle: the
    same check must not call a set incomplete because the quest that finishes it
    lives outside the audited zone, which is why evidence is corpus-wide. The
    level-6 tier is completed by quest 59906, far from the island.

repeatable-rewards
    No corpus oracle exists in either direction, and the tests say so out loud
    rather than asserting nothing. See the corpus-tier docstrings.

reward-class-coverage
    Positive oracle: quest 1322 pays its leather boots to four classes while the
    item admits five. It does NOT go quiet after the wave, and it should not:
    the fifth class is Reaper, whose omission is a doctrine ruling, and the
    waiver file is where a ruling is recorded.
"""

from __future__ import annotations

from collections import Counter

import pytest

from audit_checks_gear import (
    DEFAULT_BAND_SIZE,
    DEFAULT_ROSTER,
    FULL_ROSTER,
    check_class_matrix,
    check_repeatable_rewards,
    check_reward_class_coverage,
    check_set_completeness,
    is_repeatable,
)
from auditlib import Corpus, Scope
from dclib import CLASS_ARMOUR, EQUIPMENT_TYPES, V92Baseline

REPEAT = "반복"


# ---------------------------------------------------------------------------
# Hermetic fixture builders
# ---------------------------------------------------------------------------

def quest_xml(gid: int, hz: int, local: int, *, repeat: str = "1회성",
              quest_type: str = "일반", min_level: str = "1",
              max_level: str = "") -> str:
    cond = [f"    <최소레벨>{min_level}</최소레벨>"]
    if max_level:
        cond.append(f"    <최대레벨>{max_level}</최대레벨>")
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<Quest id="{gid}">\n'
            "  <Header>\n"
            f"    <Quest번호>{hz},{local}</Quest번호>\n"
            f"    <퀘스트종류>{quest_type}</퀘스트종류>\n"
            f"    <반복퀘스트>{repeat}</반복퀘스트>\n"
            "    <수행조건>\n" + "\n".join(cond) + "\n    </수행조건>\n"
            "  </Header>\n  <Tasks />\n</Quest>\n")


def comp_xml(rows: list[tuple[int, list[tuple[int, str]]]]) -> str:
    """rows: (questId, [(item id, class or "")])."""
    out = ['<?xml version="1.0" encoding="utf-8"?>', "<CompensationData>"]
    for qid, items in rows:
        out.append(f'  <Quest questId="{qid}">')
        out.append('    <CompensationType type="all" exp="800" gold="80">')
        for item, cls in items:
            cls_attr = f' class="{cls}"' if cls else ""
            out.append(f'      <Item templateId="{item}" quantity="1"{cls_attr} />')
        out.append("    </CompensationType>")
        out.append("  </Quest>")
    out.append("</CompensationData>")
    return "\n".join(out)


def item(item_id: int, name: str, ctype: str, subtype: str, level: int,
         classes: str, look: str = "0") -> str:
    return (f'  <Item id="{item_id}" name="{name}" combatItemType="{ctype}" '
            f'combatItemSubType="{subtype}" requiredLevel="{level}" '
            f'requiredClass="{classes}" linkLookInfoId="{look}" />')


MAIL = "LANCER;BERSERKER;ENGINEER;FIGHTER"
LEATHER = "WARRIOR;SLAYER;ARCHER;GLAIVER;SOULLESS"
ROBE = "SORCERER;PRIEST;ELEMENTALIST;ASSASSIN"

# Ids, names, levels, classes and look ids are the real ones from the corpus, so
# a fixture that drifts from the data it stands in for fails loudly rather than
# passing against a shape that no longer exists.
ITEM_ROWS = [
    # Weapons: the class ladder, real ids.
    item(82006, "gauntlet_01", "EQUIP_WEAPON", "gauntlet", 2, "FIGHTER"),
    item(82271, "gauntlet_08", "EQUIP_WEAPON", "gauntlet", 4, "FIGHTER"),
    item(10009, "dual_01", "EQUIP_WEAPON", "dual", 2, "WARRIOR"),
    item(12129, "dual_08", "EQUIP_WEAPON", "dual", 4, "WARRIOR"),
    item(10010, "lance_01", "EQUIP_WEAPON", "lance", 2, "LANCER"),
    item(12130, "lance_08", "EQUIP_WEAPON", "lance", 4, "LANCER"),
    # The level-4 leather visual tier (family leather, tier 005).
    item(17407, "leather17_body", "EQUIP_ARMOR_BODY", "bodyLeather", 4, LEATHER, "211005"),
    item(17408, "leather17_hand", "EQUIP_ARMOR_ARM", "handLeather", 4, LEATHER, "212005"),
    item(17409, "leather17_feet", "EQUIP_ARMOR_LEG", "feetLeather", 4, LEATHER, "213005"),
    # The level-4 mail tier, used for the slot-grouping test.
    item(17404, "mail17_body", "EQUIP_ARMOR_BODY", "bodyMail", 4, MAIL, "311005"),
    item(17405, "mail17_hand", "EQUIP_ARMOR_ARM", "handMail", 4, MAIL, "312005"),
    item(17406, "mail17_feet", "EQUIP_ARMOR_LEG", "feetMail", 4, MAIL, "313005"),
    # A robe tier nobody grants, for the never-granted-set case.
    item(17410, "robe17_body", "EQUIP_ARMOR_BODY", "bodyRobe", 4, ROBE, "411005"),
    item(17411, "robe17_hand", "EQUIP_ARMOR_ARM", "handRobe", 4, ROBE, "412005"),
    item(17412, "robe17_feet", "EQUIP_ARMOR_LEG", "feetRobe", 4, ROBE, "413005"),
    # A costume. EQUIP_STYLE_BODY is the prefix trap: 55,739 items in the merged
    # model start with EQUIP and are not gear.
    item(70143, "body_item", "EQUIP_STYLE_BODY", "bodyLeather", 1, LEATHER, "211005"),
    # An unrestricted consumable, so a reward payload is not all equipment.
    item(160, "recall_scroll2", "DISPOSAL", "magical", 1, "", "0"),
]

ITEMS = ('<?xml version="1.0" encoding="utf-8"?>\n<ItemData>\n'
         + "\n".join(ITEM_ROWS) + "\n</ItemData>\n")


def build(corpus_dir, files: dict[str, str], zones=(13,), new=None) -> tuple[Corpus, Scope]:
    tree = {"ItemTemplate.xml": ITEMS}
    tree.update(files)
    root = corpus_dir(tree, bom=False, crlf=False)
    corpus = Corpus(root, V92Baseline(root))
    return corpus, Scope(zones=set(zones) if zones else None, new_quests=new)


# ---------------------------------------------------------------------------
# The roster constants
# ---------------------------------------------------------------------------

def test_full_roster_matches_the_dclib_armour_cross_tab():
    """The roster and dclib's class-to-armour map must never drift apart.

    A class present in one and absent from the other silently removes a whole
    column from the matrix, and an absent column reports no gaps at all.
    """
    from_dclib = {c for classes in CLASS_ARMOUR.values() for c in classes}

    assert set(FULL_ROSTER) == from_dclib
    assert len(FULL_ROSTER) == 13


def test_default_roster_omits_soulless_only():
    """Reaper has no low-level gear and is omitted from the island by doctrine.

    Auditing it against peers reports a gap in every single band, which is why
    the class-matrix default drops it. It stays a parameter because the omission
    is a per-region ruling, not a property of the data.
    """
    assert set(FULL_ROSTER) - set(DEFAULT_ROSTER) == {"SOULLESS"}
    assert DEFAULT_BAND_SIZE == 1


# ---------------------------------------------------------------------------
# class-matrix: condition 1, the same item twice in one band
# ---------------------------------------------------------------------------

def test_same_item_to_one_class_from_two_quests_is_high(corpus_dir):
    """The Brawler shape: two payouts, one weapon, no upgrade between them."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001304.quest": quest_xml(1304, 13, 4),
        "QuestData/001323.quest": quest_xml(1323, 13, 23),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1304, [(82006, "fighter")]),
            (1323, [(82006, "fighter")]),
        ]),
    })

    repeats = repeats_of(check_class_matrix(corpus, scope))

    assert len(repeats) == 1
    assert repeats[0].severity == "high"
    assert repeats[0].key == "class-matrix:item-82006 (gauntlet_01):FIGHTER:1304+1323"
    assert repeats[0].evidence["band"] == "lv2"
    assert repeats[0].evidence["slot"] == "weapon"


def test_a_real_upgrade_between_two_quests_is_not_a_finding(corpus_dir):
    """Two different weapons in two bands is the ladder working as intended."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001304.quest": quest_xml(1304, 13, 4),
        "QuestData/001323.quest": quest_xml(1323, 13, 23),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1304, [(82006, "fighter")]),
            (1323, [(82271, "fighter")]),
        ]),
    })

    assert check_class_matrix(corpus, scope, roster=("FIGHTER",)) == []


def test_one_quest_paying_one_item_per_class_is_not_a_self_duplicate(corpus_dir):
    """A single payout with one row per class is the normal shape, not a repeat."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001304.quest": quest_xml(1304, 13, 4),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1304, [(82006, "fighter"), (10009, "warrior"), (10010, "lancer")]),
        ]),
    })

    repeats = [f for f in check_class_matrix(corpus, scope) if "item" in f.evidence]

    assert repeats == []


# ---------------------------------------------------------------------------
# class-matrix: condition 2, an empty cell with filled peers
# ---------------------------------------------------------------------------

def test_a_class_left_out_of_a_band_its_peers_reached_is_high(corpus_dir):
    """Brawler stayed on its level-2 weapon while peers took a level-4 one.

    A misaligned ladder is reported from both sides, and deliberately so: the
    level-2 band is now filled for Brawler alone, which is the same defect said
    the other way round. The corpus shows the identical mirror at level 12,
    where three classes hold a weapon the other nine never receive.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001303.quest": quest_xml(1303, 13, 3),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1303, [(12129, "warrior"), (12130, "lancer"), (82006, "fighter")]),
        ]),
    })

    gaps = gaps_of(check_class_matrix(corpus, scope, roster=("WARRIOR", "LANCER", "FIGHTER")))
    by_key = {f.key: f for f in gaps}

    assert set(by_key) == {
        "class-matrix:FIGHTER:weapon:lv4",
        "class-matrix:WARRIOR:weapon:lv2",
        "class-matrix:LANCER:weapon:lv2",
    }
    assert by_key["class-matrix:FIGHTER:weapon:lv4"].evidence["filled"] == ["WARRIOR", "LANCER"]
    # A gap belongs to the payout that covered everyone else, so a --quests run
    # reviewing 1303 sees it as new.
    assert by_key["class-matrix:FIGHTER:weapon:lv4"].evidence["quest"] == 1303


def test_the_band_comes_from_the_item_level_not_the_quest_gate(corpus_dir):
    """Island of Dawn grants level-4 items from level-1 quests, on purpose.

    Ordering by 최소레벨 puts those grants in the level-1 band and invents a
    plateau for every class that got its level-4 item from a level-3 quest.
    Here two quests with different gates grant the same-level items, and there
    is nothing wrong with that.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001303.quest": quest_xml(1303, 13, 3, min_level="1"),
        "QuestData/001319.quest": quest_xml(1319, 13, 19, min_level="7"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1303, [(12129, "warrior")]),
            (1319, [(12130, "lancer")]),
        ]),
    })

    findings = check_class_matrix(corpus, scope, roster=("WARRIOR", "LANCER"))

    assert findings == [], "both items are requiredLevel 4; the quest gates are irrelevant"


def test_armour_in_the_band_does_not_fill_a_missing_weapon(corpus_dir):
    """Slot grouping is what makes the weapon stall visible.

    Brawler's level-4 cell is not empty if a level-4 chest piece counts. It got
    a chest piece and no weapon, and a matrix that mixes the two reports a
    healthy ladder.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001303.quest": quest_xml(1303, 13, 3),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1303, [(12129, "warrior"), (82006, "fighter"),
                    (17404, "fighter"), (17407, "warrior")]),
        ]),
    })

    keys = {f.key for f in gaps_of(check_class_matrix(corpus, scope, roster=("WARRIOR", "FIGHTER")))}

    assert "class-matrix:FIGHTER:weapon:lv4" in keys, "the weapon that never arrived"
    assert "class-matrix:FIGHTER:body:lv4" not in keys, "the chest piece did arrive"
    assert "class-matrix:WARRIOR:weapon:lv2" in keys, "the mirror, same band grouping"


def test_an_untagged_row_reaches_every_class_the_item_admits(corpus_dir):
    """A grant with no class attribute is not a grant to nobody."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001324.quest": quest_xml(1324, 13, 24),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1324, [(17407, "")]),
        ]),
    })

    findings = check_class_matrix(corpus, scope, roster=("WARRIOR", "SLAYER", "ARCHER"))

    assert findings == [], "one untagged leather body piece covers all three"


def test_soulless_is_not_a_gap_under_the_default_roster(corpus_dir):
    """The doctrine omission must not become a finding in every single band."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001324.quest": quest_xml(1324, 13, 24),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1324, [(17407, "warrior"), (17407, "slayer"),
                    (17407, "archer"), (17407, "glaiver")]),
        ]),
    })

    default = [f for f in check_class_matrix(corpus, scope) if f.subject == "SOULLESS"]
    full = [f for f in check_class_matrix(corpus, scope, roster=FULL_ROSTER)
            if f.subject == "SOULLESS"]

    assert default == []
    assert [f.key for f in full] == ["class-matrix:SOULLESS:body:lv4"]


# ---------------------------------------------------------------------------
# set-completeness
# ---------------------------------------------------------------------------

def test_a_set_granted_body_only_is_high(corpus_dir):
    """The level-4 tier shape: two thirds of a set a player can never finish."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001303.quest": quest_xml(1303, 13, 3),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1303, [(17407, "warrior")]),
        ]),
    })

    findings = check_set_completeness(corpus, scope)

    assert len(findings) == 1
    assert findings[0].severity == "high"
    assert findings[0].key == "set-completeness:set leather/005:feet+hand"
    assert findings[0].evidence["missing_items"] == {"feet": [17409], "hand": [17408]}
    assert findings[0].evidence["granted"] == {"body": [1303]}


def test_a_fully_granted_set_is_silent(corpus_dir):
    corpus, scope = build(corpus_dir, {
        "QuestData/001322.quest": quest_xml(1322, 13, 22),
        "QuestData/001324.quest": quest_xml(1324, 13, 24),
        "QuestData/001325.quest": quest_xml(1325, 13, 25),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1324, [(17407, "warrior")]),
            (1325, [(17408, "warrior")]),
            (1322, [(17409, "warrior")]),
        ]),
    })

    assert [f for f in check_set_completeness(corpus, scope)
            if f.evidence["family"] == "leather"] == []


def test_a_set_nobody_grants_is_not_reported(corpus_dir):
    """Content that was never handed out is not a broken reward.

    It also belongs to no zone, so reporting it would attach a finding to
    whichever zone happened to be audited.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001303.quest": quest_xml(1303, 13, 3),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1303, [(17407, "warrior")]),
        ]),
    })

    families = {f.evidence["family"] for f in check_set_completeness(corpus, scope)}

    assert "robe" not in families, "the robe tier is granted by nobody at all"


def test_evidence_is_corpus_wide_so_an_out_of_zone_quest_completes_a_set(corpus_dir):
    """A zone-scoped evidence read calls every cross-region set incomplete.

    The level-6 tier really is completed by quest 59906, nowhere near the
    island, and reporting it as broken is the failure mode this guards.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001303.quest": quest_xml(1303, 13, 3),
        "QuestData/599061.quest": quest_xml(599061, 599, 61),
        "QuestData/599062.quest": quest_xml(599062, 599, 62),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1303, [(17407, "warrior")]),
        ]),
        "CompensationData/QuestCompensationData_599.xml": comp_xml([
            (599061, [(17408, "warrior")]),
            (599062, [(17409, "warrior")]),
        ]),
    }, zones=(13,))

    assert [f for f in check_set_completeness(corpus, scope)
            if f.evidence["family"] == "leather"] == []


def test_a_set_no_subject_quest_touches_is_not_reported(corpus_dir):
    """Subject scope limits reporting; it never limits evidence."""
    corpus, scope = build(corpus_dir, {
        "QuestData/006401.quest": quest_xml(6401, 64, 1),
        "CompensationData/QuestCompensationData_64.xml": comp_xml([
            (6401, [(17407, "warrior")]),
        ]),
    }, zones=(13,))

    assert check_set_completeness(corpus, scope) == []


# ---------------------------------------------------------------------------
# repeatable-rewards
# ---------------------------------------------------------------------------

def test_a_repeatable_granting_equipment_is_high(corpus_dir):
    """A repeatable holding a unique set piece can be farmed until it is worthless."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001334.quest": quest_xml(1334, 13, 34, repeat=REPEAT, max_level="10"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1334, [(17407, "warrior")]),
        ]),
    })

    findings = check_repeatable_rewards(corpus, scope)

    assert len(findings) == 1
    assert findings[0].severity == "high"
    assert findings[0].key == "repeatable-rewards:quest-1334:17407"
    assert findings[0].evidence["combat_type"] == "EQUIP_ARMOR_BODY"


def test_the_quest_type_encoding_of_repeatable_is_detected_too(corpus_dir):
    """Both encodings exist. Testing only 반복퀘스트 misses 11 of the 47."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001334.quest": quest_xml(1334, 13, 34, repeat="1회성", quest_type=REPEAT),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1334, [(17407, "warrior")]),
        ]),
    })

    assert len(check_repeatable_rewards(corpus, scope)) == 1


def test_a_costume_repeatable_does_not_fire(corpus_dir):
    """The mandatory negative oracle.

    combat_type.startswith("EQUIP") also matches EQUIP_STYLE_*, EQUIP_UNDERWEAR
    and EQUIP_INHERITANCE: 55,739 items in the merged model at the baseline. A
    check built on the prefix reports every costume repeatable in the game and
    is switched off within a week. Item 70143 is a real EQUIP_STYLE_BODY.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001341.quest": quest_xml(1341, 13, 41, repeat=REPEAT),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1341, [(70143, "warrior"), (160, "")]),
        ]),
    })

    assert check_repeatable_rewards(corpus, scope) == []


def test_a_max_level_cap_alone_is_not_a_trigger(corpus_dir):
    """777 quests carry 최대레벨. Only the conjunction is a defect.

    Quest 1390 is exactly this shape: a level cap of 12, a one-shot flag, and a
    consumable payout. The plan called it a repeatable; it is not.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001390.quest": quest_xml(1390, 13, 90, repeat="1회성", max_level="12"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1390, [(17407, "warrior")]),
        ]),
    })

    assert check_repeatable_rewards(corpus, scope) == []


def test_a_repeatable_paying_consumables_is_silent(corpus_dir):
    corpus, scope = build(corpus_dir, {
        "QuestData/001341.quest": quest_xml(1341, 13, 41, repeat=REPEAT),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1341, [(160, "")])]),
    })

    assert check_repeatable_rewards(corpus, scope) == []


def test_is_repeatable_tolerates_the_garbage_values(corpus_dir):
    """4 quests carry a backtick and 27 an empty string in 반복퀘스트."""
    assert is_repeatable({"repeat": REPEAT, "quest_type": "일반"}) is True
    assert is_repeatable({"repeat": "1회성", "quest_type": REPEAT}) is True
    assert is_repeatable({"repeat": "`", "quest_type": "일반"}) is False
    assert is_repeatable({"repeat": "", "quest_type": ""}) is False
    assert is_repeatable({}) is False


# ---------------------------------------------------------------------------
# reward-class-coverage
# ---------------------------------------------------------------------------

def test_a_class_the_item_admits_and_no_row_covers_is_medium(corpus_dir):
    """The 1322 shape: four leather rows against an item admitting five."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001322.quest": quest_xml(1322, 13, 22),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1322, [(17409, "warrior"), (17409, "slayer"),
                    (17409, "archer"), (17409, "glaiver")]),
        ]),
    })

    findings = check_reward_class_coverage(corpus, scope)

    assert len(findings) == 1
    assert findings[0].severity == "medium"
    assert findings[0].key == "reward-class-coverage:item-17409 (leather17_feet):1322:uncovered:SOULLESS"
    assert findings[0].evidence["uncovered"] == ["SOULLESS"]


def test_the_omission_disappears_under_a_roster_that_drops_the_class(corpus_dir):
    """Why the default here is the FULL thirteen, unlike class-matrix.

    With Reaper dropped from the roster the corpus produces zero coverage
    findings and the check has no positive oracle at all. The doctrine ruling
    belongs in the waiver file, where it is auditable, not in a constant.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001322.quest": quest_xml(1322, 13, 22),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1322, [(17409, "warrior"), (17409, "slayer"),
                    (17409, "archer"), (17409, "glaiver")]),
        ]),
    })

    assert check_reward_class_coverage(corpus, scope, roster=DEFAULT_ROSTER) == []


def test_a_row_the_item_rejects_is_medium(corpus_dir):
    """The other direction: a row that can never pay.

    No instance of this exists anywhere in the corpus at either snapshot (see
    the corpus test below), so the structure is pinned here.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001322.quest": quest_xml(1322, 13, 22),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1322, [(17409, "priest")]),
        ]),
    })

    wrong = [f for f in check_reward_class_coverage(corpus, scope)
             if "wrong_class" in f.evidence]

    assert len(wrong) == 1
    assert wrong[0].evidence["wrong_class"] == ["PRIEST"]
    assert "can never pay" in wrong[0].message


def test_the_compare_is_case_insensitive(corpus_dir):
    """ItemTemplate is UPPERCASE, compensation rows lowercase.

    A raw string compare reports every single class-gated grant in the game as
    both uncovered and wrong-class at once.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001324.quest": quest_xml(1324, 13, 24),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1324, [(17404, "lancer"), (17404, "berserker"),
                    (17404, "engineer"), (17404, "fighter")]),
        ]),
    })

    assert check_reward_class_coverage(corpus, scope) == []


def test_an_untagged_grant_has_no_coverage_obligation(corpus_dir):
    """An untagged row already reaches everyone the item admits."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001324.quest": quest_xml(1324, 13, 24),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1324, [(17407, "")])]),
    })

    assert check_reward_class_coverage(corpus, scope) == []


def test_unrestricted_equipment_is_not_class_gated(corpus_dir):
    """An empty requiredClass admits everyone; there is nothing to cover."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001324.quest": quest_xml(1324, 13, 24),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1324, [(160, "warrior")])]),
    })

    assert check_reward_class_coverage(corpus, scope) == []


# ---------------------------------------------------------------------------
# Corpus tier
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def at_baseline(datasheet_dir, baseline):
    return Corpus(datasheet_dir, baseline, use_baseline=True)


@pytest.fixture(scope="session")
def at_worktree(datasheet_dir):
    return Corpus(datasheet_dir, V92Baseline(datasheet_dir), use_baseline=False)


ZONE_13 = Scope(zones={13}, new_quests=None)
CORPUS_WIDE = Scope(zones=None, new_quests=None)


def gaps_of(findings):
    return [f for f in findings if "filled" in f.evidence]


def repeats_of(findings):
    return [f for f in findings if "filled" not in f.evidence]


# --- class-matrix ---------------------------------------------------------

@pytest.mark.corpus
def test_the_brawler_and_ninja_weapon_plateau_fires_at_the_baseline(at_baseline):
    """Both classes were handed the same level-2 weapon by four quests.

    The plan recorded three weapon quests. Measured at the pinned baseline it is
    four: 1303, 1304, 1319 and 1323, because 1303 and 1319 pay every other class
    a level-4 and a level-3 weapon respectively while paying these two the same
    level-2 one they already had.
    """
    repeats = repeats_of(check_class_matrix(at_baseline, ZONE_13))
    stuck = {f.evidence["class"]: f for f in repeats
             if f.evidence["item"] in (82006, 58172)}

    assert set(stuck) == {"FIGHTER", "ASSASSIN"}
    assert stuck["FIGHTER"].evidence["quests"] == [1303, 1304, 1319, 1323]
    assert stuck["ASSASSIN"].evidence["quests"] == [1303, 1304, 1319, 1323]
    assert stuck["FIGHTER"].evidence["band"] == "lv2"


@pytest.mark.corpus
def test_the_missing_mid_tier_upgrades_fire_at_the_baseline(at_baseline):
    """20 empty weapon cells, and every one of them is a weapon.

    Brawler and Ninja have no level-3, level-4, level-8 or level-11 weapon at
    all. Glaiver joins them from level 4 up. The level-12 rows are the same
    defect seen from the other side: the three classes that DID get a level-12
    weapon are the ones the other nine never reach.
    """
    gaps = gaps_of(check_class_matrix(at_baseline, ZONE_13))

    assert len(gaps) == 20
    assert {f.evidence["slot"] for f in gaps} == {"weapon"}
    by_class = {(f.subject, f.evidence["band"]) for f in gaps}
    for band in ("lv3", "lv4", "lv8", "lv11"):
        assert ("FIGHTER", band) in by_class
        assert ("ASSASSIN", band) in by_class
    assert Counter(f.evidence["band"] for f in gaps) == {
        "lv12": 9, "lv4": 3, "lv8": 3, "lv11": 3, "lv3": 2}


@pytest.mark.corpus
def test_the_weapon_plateau_is_silent_on_the_working_tree(at_worktree):
    """Fire-then-quiet. The patch-002 wave gave every class a real ladder."""
    gaps = gaps_of(check_class_matrix(at_worktree, ZONE_13))

    assert gaps == []


@pytest.mark.corpus
def test_the_repeat_condition_still_fires_on_the_working_tree(at_worktree):
    """Documented, not dropped.

    The empty-cell condition goes quiet after the wave; the repeat condition
    does not, and it is right not to. Quests 1310 and 1333 both pay the level-7
    weapon set, and 1310 and 1332 both pay the level-7 body piece: 12 classes by
    2 conditions. That is a different pair from the 1304/1323 one the wave
    removed, and it is a real standing finding for the waiver file, not a
    regression in the check.
    """
    repeats = repeats_of(check_class_matrix(at_worktree, ZONE_13))

    assert len(repeats) == 24
    assert Counter(tuple(f.evidence["quests"]) for f in repeats) == {
        (1310, 1332): 12, (1310, 1333): 12}
    assert {f.evidence["band"] for f in repeats} == {"lv7"}


@pytest.mark.corpus
def test_a_wider_band_hides_the_plateau(at_baseline):
    """Why DEFAULT_BAND_SIZE is 1, measured rather than assumed.

    At width 4 the level-2 weapon Brawler was stuck on and the level-4 weapon
    everyone else received fall in the same bucket, the cell stops looking
    empty, and all 20 findings vanish.
    """
    assert len(gaps_of(check_class_matrix(at_baseline, ZONE_13, band_size=1))) == 20
    assert len(gaps_of(check_class_matrix(at_baseline, ZONE_13, band_size=2))) == 2
    assert len(gaps_of(check_class_matrix(at_baseline, ZONE_13, band_size=4))) == 0


# --- set-completeness -----------------------------------------------------

@pytest.mark.corpus
def test_no_gear_set_below_level_seven_was_completable_at_the_baseline(at_baseline):
    """15 partly granted sets in zone 13, and the two that stranded players.

    The level-4 tier (005) was granted body-only in all three families, so its
    six requiredLevel-4 hand and feet pieces came from no quest in the corpus.
    The level-3 tier (003) was granted hand and feet only, so its body pieces
    did.

    Plan correction: the level-3 body count is six, not three. Each 1770x piece
    has a 300xx twin at the same requiredLevel in the same visual tier, and the
    plan counted only the first family. The level-4 figure of "6 of 9" does
    hold, because that tier's twins sit at requiredLevel 5.
    """
    findings = check_set_completeness(at_baseline, ZONE_13)
    by_key = {(f.evidence["family"], f.evidence["tier"]): f for f in findings}

    assert len(findings) == 15

    level4 = []
    for family in ("mail", "leather", "robe"):
        f = by_key[(family, "005")]
        assert f.evidence["missing_slots"] == ["feet", "hand"]
        assert f.evidence["granted"] == {"body": [1303]}
        level4 += [i for items in f.evidence["missing_items"].values() for i in items
                   if at_baseline.items.get(i).required_level == 4]
    assert sorted(level4) == [17405, 17406, 17408, 17409, 17411, 17412], "6 of 9"

    level3 = []
    for family in ("mail", "leather", "robe"):
        f = by_key[(family, "003")]
        assert f.evidence["missing_slots"] == ["body"]
        assert f.evidence["granted"] == {"feet": [1322], "hand": [1325]}
        level3 += [i for i in f.evidence["missing_items"]["body"]
                   if at_baseline.items.get(i).required_level == 3]
    assert sorted(level3) == [17701, 17704, 17707, 30043, 30046, 30049]


@pytest.mark.corpus
def test_the_sub_level_seven_sets_are_silent_on_the_working_tree(at_worktree):
    """Fire-then-quiet: specs 002/27 to 002/33 completed both tiers.

    What remains is the level-11 tier (031), still body-only, and that is a real
    standing finding rather than a regression. The level-3 tier is now granted
    by nobody at all, which is content nobody is offered, not a broken set.
    """
    findings = check_set_completeness(at_worktree, ZONE_13)
    tiers = {(f.evidence["family"], f.evidence["tier"]) for f in findings}

    assert tiers == {("mail", "031"), ("leather", "031"), ("robe", "031")}
    assert len(findings) == 3


@pytest.mark.corpus
def test_set_evidence_reaches_outside_the_audited_zone(at_baseline):
    """Quest 59906 completes the level-6 body slot from far off the island.

    A zone-scoped evidence read would report that slot as granted by nobody, and
    the finding would be wrong in the direction that costs the most: it invents
    a problem and sends someone to fix data that is already correct.
    """
    findings = {(f.evidence["family"], f.evidence["tier"]): f
                for f in check_set_completeness(at_baseline, ZONE_13)}
    leather6 = findings[("leather", "006")]

    assert 59906 in leather6.evidence["granted"]["body"]
    assert leather6.evidence["subject_quests"] == [1331, 1347]
    assert leather6.evidence["zones"] == [13]


# --- repeatable-rewards ---------------------------------------------------

@pytest.mark.corpus
def test_no_repeatable_in_the_corpus_grants_equipment(at_baseline, at_worktree):
    """This check has NO corpus oracle, in either direction. Stated, not hidden.

    Measured at the pinned baseline and on the working tree: 47 repeatable
    quests, 20 of them with a reward payload, and not one grants an item in
    EQUIPMENT_TYPES. The plan named quests 1334 and 1390 as repeatable set
    carriers. Only 1334 is repeatable, and it grants nothing at either snapshot;
    1390 is 반복퀘스트 = 1회성, a one-shot with a 최대레벨 of 12 that pays two
    recall scrolls. So the positive oracle is the hermetic test above, and this
    test pins the corpus fact that makes it necessary.
    """
    for corpus in (at_baseline, at_worktree):
        repeatables = [gid for gid, q in corpus.quests.items() if is_repeatable(q)]
        with_payout = [g for g in repeatables if (corpus.rewards.get(g) or {}).get("items")]

        assert len(repeatables) == 47
        assert len(with_payout) == 20
        assert check_repeatable_rewards(corpus, CORPUS_WIDE) == []

    assert is_repeatable(at_worktree.quests[1334]) is True
    assert (at_worktree.rewards.get(1334) or {"items": []})["items"] == []
    assert is_repeatable(at_worktree.quests[1390]) is False
    assert at_worktree.quests[1390]["max_level"] == "12"


@pytest.mark.corpus
def test_the_corpus_holds_no_costume_repeatable_either(at_worktree):
    """Which is why the costume negative oracle has to be hermetic.

    Nothing repeatable pays an EQUIP-prefixed item at all, so the corpus cannot
    distinguish the allow-list from the prefix. The gap it would leave is large:
    55,739 items in the merged model start with EQUIP and are not gear.
    """
    prefixed = 0
    for gid, quest in at_worktree.quests.items():
        if not is_repeatable(quest):
            continue
        for template, _q, _c in (at_worktree.rewards.get(gid) or {"items": []})["items"]:
            if not template.isdigit():
                continue
            info = at_worktree.items.get(int(template))
            if info is not None and info.combat_type.startswith("EQUIP"):
                prefixed += 1

    assert prefixed == 0

    not_gear = sum(1 for i in at_worktree.items.items.values()
                   if i.combat_type.startswith("EQUIP") and i.combat_type not in EQUIPMENT_TYPES)
    assert not_gear > 50_000, "the prefix trap is not a rounding error"


@pytest.mark.corpus
def test_a_level_cap_alone_never_reaches_the_check(at_worktree):
    """777 quests carry 최대레벨 and none of them is a finding."""
    capped = [gid for gid, q in at_worktree.quests.items() if q.get("max_level")]

    assert len(capped) == 777
    assert check_repeatable_rewards(at_worktree, CORPUS_WIDE) == []


# --- reward-class-coverage ------------------------------------------------

@pytest.mark.corpus
def test_the_1322_leather_rows_fire_at_both_snapshots(at_baseline, at_worktree):
    """The one finding that must NOT go quiet after the wave.

    Quest 1322 pays its leather boots to four classes while the item admits
    five. The fifth is Reaper, and its omission is a doctrine ruling, so the
    right resolution is a waiver entry recording the ruling, not a fix and not a
    hardcoded roster. The item id changed with the wave: 17706 at the baseline,
    17409 on the working tree. The plan quoted 17409, which is the working-tree
    id, not the one in the state it said it measured.
    """
    at_base = {(f.evidence["quest"], f.evidence["item"]): f
               for f in check_reward_class_coverage(at_baseline, ZONE_13)}
    now = {(f.evidence["quest"], f.evidence["item"]): f
           for f in check_reward_class_coverage(at_worktree, ZONE_13)}

    assert (1322, 17706) in at_base
    assert (1322, 17409) in now
    assert now[(1322, 17409)].evidence["rows"] == ["ARCHER", "GLAIVER", "SLAYER", "WARRIOR"]
    assert now[(1322, 17409)].evidence["uncovered"] == ["SOULLESS"]


@pytest.mark.corpus
def test_every_coverage_finding_in_zone_13_is_the_same_doctrine_omission(at_baseline, at_worktree):
    """13 findings at the baseline, 8 on the working tree, all one ruling.

    A check whose entire output is a single known ruling is exactly what the
    waiver file exists for, and it stays medium because it is a coverage
    question, not proof of a defect.
    """
    for corpus, expected in ((at_baseline, 13), (at_worktree, 8)):
        findings = check_reward_class_coverage(corpus, ZONE_13)

        assert len(findings) == expected
        assert {tuple(f.evidence["uncovered"]) for f in findings} == {("SOULLESS",)}
        assert {f.severity for f in findings} == {"medium"}


@pytest.mark.corpus
def test_dropping_soulless_from_the_roster_leaves_no_oracle(at_baseline, at_worktree):
    """Measured justification for the FULL default on this check alone."""
    for corpus in (at_baseline, at_worktree):
        assert check_reward_class_coverage(corpus, ZONE_13, roster=DEFAULT_ROSTER) == []


@pytest.mark.corpus
def test_the_wrong_class_direction_has_no_corpus_instance(at_baseline, at_worktree):
    """Stated rather than silently untested.

    No compensation row anywhere in the corpus pays a class the item rejects, at
    either snapshot. The direction is real and cheap to compute, so it ships,
    with the hermetic test above as its only oracle.
    """
    for corpus in (at_baseline, at_worktree):
        wrong = 0
        for gid, payload in corpus.rewards.items():
            for template, _q, cls in payload["items"]:
                if not template.isdigit() or not cls:
                    continue
                info = corpus.items.get(int(template))
                if info is None or not info.is_equipment or not info.required_class:
                    continue
                if not info.admits(cls):
                    wrong += 1

        assert wrong == 0
