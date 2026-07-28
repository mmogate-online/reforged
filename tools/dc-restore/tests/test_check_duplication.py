"""The duplication check.

Positive oracle: quests 1304 and 1323 granted the identical 12-row class weapon
bag at the identical 800 exp and 80 gold. Authentic v31 data, so no source diff
could have found it. It fires at the pinned baseline and is silent on the
working tree, where the patch-002 wave removed it.

Negative oracle: deliberate duplication is legitimate and must not reach high.
The class-variant pair 1351/1352 grants one item to a physical and a caster
variant of the same quest, and item 160 is a starter gift that the camp merchant
also stocks. Both are real, both are correct, and both live in the waiver file
rather than in check logic.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from audit_checks_duplication import check_duplication
from auditlib import Corpus, Scope
from dclib import ITEM_SOURCES, V92Baseline, is_regional_variant, scan_item_sources


def quest_xml(gid: int, hz: int, local: int) -> str:
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<Quest id="{gid}">\n'
            f"  <Header><Quest번호>{hz},{local}</Quest번호></Header>\n"
            f"  <Tasks />\n</Quest>\n")


def comp_xml(rows: list[tuple[int, str, str, list[int]]]) -> str:
    """rows: (questId, exp, gold, [item ids])."""
    out = ['<?xml version="1.0" encoding="utf-8"?>', "<CompensationData>"]
    for qid, exp, gold, items in rows:
        out.append(f'  <Quest questId="{qid}">')
        out.append(f'    <CompensationType type="all" exp="{exp}" gold="{gold}">')
        for item in items:
            out.append(f'      <Item templateId="{item}" quantity="1" />')
        out.append("    </CompensationType>")
        out.append("  </Quest>")
    out.append("</CompensationData>")
    return "\n".join(out)


ITEMS = """<?xml version="1.0" encoding="utf-8"?>
<ItemData>
  <Item id="10009" name="dual_01" combatItemType="EQUIP_WEAPON" combatItemSubType="dual" linkLookInfoId="0" />
  <Item id="12137" name="kugai_axe" combatItemType="EQUIP_WEAPON" combatItemSubType="axe" linkLookInfoId="0" />
  <Item id="160" name="recall_scroll2" combatItemType="DISPOSAL" combatItemSubType="magical" linkLookInfoId="0" />
</ItemData>
"""


def build(corpus_dir, files: dict[str, str], zones=(13,), new=None) -> tuple[Corpus, Scope]:
    tree = {"ItemTemplate.xml": ITEMS}
    tree.update(files)
    root = corpus_dir(tree, bom=False, crlf=False)
    corpus = Corpus(root, V92Baseline(root))
    return corpus, Scope(zones=set(zones) if zones else None, new_quests=new)


# ---------------------------------------------------------------------------
# Signature (a): identical item, exp and gold
# ---------------------------------------------------------------------------

def test_identical_item_exp_and_gold_across_two_quests_is_high(corpus_dir):
    """The 1304/1323 shape: a copy-paste, not a design choice."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001304.quest": quest_xml(1304, 13, 4),
        "QuestData/001323.quest": quest_xml(1323, 13, 23),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1304, "800", "80", [10009]),
            (1323, "800", "80", [10009]),
        ]),
    })

    findings = [f for f in check_duplication(corpus, scope) if f.severity == "high"]

    assert len(findings) == 1
    assert findings[0].key == "duplication:item-10009 (dual_01):1304+1323"
    assert "identical exp 800 and gold 80" in findings[0].message
    assert findings[0].evidence["quests"] == [1304, 1323]


def test_the_same_item_at_different_payouts_is_not_high(corpus_dir):
    """Two quests granting one item at different rewards is ordinary design.

    Only the identical-payout signature marked a real defect every time, so
    widening it here is how the check starts crying wolf.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001304.quest": quest_xml(1304, 13, 4),
        "QuestData/001323.quest": quest_xml(1323, 13, 23),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1304, "800", "80", [10009]),
            (1323, "1200", "120", [10009]),
        ]),
    })

    assert [f for f in check_duplication(corpus, scope) if f.severity == "high"] == []


def test_one_quest_granting_an_item_once_is_not_a_finding(corpus_dir):
    corpus, scope = build(corpus_dir, {
        "QuestData/001304.quest": quest_xml(1304, 13, 4),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1304, "800", "80", [10009])]),
    })

    assert check_duplication(corpus, scope) == []


# ---------------------------------------------------------------------------
# Signature (b): quest-granted and purchasable
# ---------------------------------------------------------------------------

KUGAI_BUYLIST = """<?xml version="1.0" encoding="utf-8"?>
<BuyList>
  <List id="9999009" desc="Kugai Weapons" NeedMedalItemId="95216">
    <Item itemId="12137" priceRevision="30" />
  </List>
</BuyList>
"""


def test_quest_granted_and_purchasable_is_high(corpus_dir):
    """The 1315 shape: a quest handing over a shop's whole tab for free.

    Only visible with shops in evidence scope. This exact overlap cannot be
    reproduced from either real snapshot (see the corpus test below), so the
    structure is pinned here instead.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001315.quest": quest_xml(1315, 13, 15),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1315, "4500", "450", [12137])]),
        "BuyList.xml": KUGAI_BUYLIST,
    })

    findings = [f for f in check_duplication(corpus, scope) if f.severity == "high"]

    assert len(findings) == 1
    assert findings[0].evidence["purchasable_from"] == ["BuyList"]
    assert "purchasable via BuyList" in findings[0].message


DROP = """<?xml version="1.0" encoding="utf-8"?>
<CompensationData><Compensation><Item templateId="12137" /></Compensation></CompensationData>
"""


def test_quest_granted_and_droppable_is_info_not_high(corpus_dir):
    """A quest reward that also drops is normal. Severity is confidence."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001315.quest": quest_xml(1315, 13, 15),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1315, "4500", "450", [12137])]),
        "CompensationData/ECompensation_13.xml": DROP,
    })

    findings = check_duplication(corpus, scope)

    assert [f.severity for f in findings] == ["info"]
    assert findings[0].evidence["sources"] == ["ECompensation"]


def test_regional_shop_variants_are_not_counted_twice(corpus_dir):
    """Regional shops duplicate their base list.

    Counting all eight reports every stocked item as sold in eight places. This
    is the opposite of the ItemTemplate rule, where the shards are disjoint.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001315.quest": quest_xml(1315, 13, 15),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1315, "4500", "450", [12137])]),
        "BuyList.xml": KUGAI_BUYLIST,
        "BuyList_NAEU.xml": KUGAI_BUYLIST,
    })

    findings = [f for f in check_duplication(corpus, scope) if f.severity == "high"]

    assert findings[0].evidence["purchasable_from"] == ["BuyList"]


@pytest.mark.parametrize("name,regional", [
    ("BuyList.xml", False), ("BuyList_NAEU.xml", True), ("BuyList_KR.xml", True),
    ("Gacha_Tool.xml", True), ("ItemTemplate.xml", False), ("TokenExchange.xml", False),
])
def test_regional_variant_detection(name, regional):
    assert is_regional_variant(name) is regional


# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------

def test_subject_scope_limits_reporting_but_not_evidence(corpus_dir):
    """A zone-scoped evidence read cannot see the other half of a duplication."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001304.quest": quest_xml(1304, 13, 4),
        "QuestData/006401.quest": quest_xml(6401, 64, 1),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1304, "800", "80", [12137])]),
        "CompensationData/QuestCompensationData_64.xml": comp_xml([(6401, "800", "80", [12137])]),
        "BuyList.xml": KUGAI_BUYLIST,
    }, zones=(13,))

    findings = check_duplication(corpus, scope)
    subjects = [f.evidence["quests"] for f in findings]

    assert all(6401 not in q for q in subjects), "zone 64 is not the subject"
    assert any(f.evidence.get("purchasable_from") for f in findings), \
        "evidence still reaches the corpus-wide shop"


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


@pytest.mark.corpus
def test_the_1304_1323_weapon_bag_fires_at_the_baseline(at_baseline):
    """12 class weapons, one bag, two quests, identical 800 exp and 80 gold."""
    findings = [f for f in check_duplication(at_baseline, ZONE_13)
                if f.severity == "high" and f.evidence.get("quests") == [1304, 1323]]

    assert len(findings) == 12, "the whole class weapon bag"
    assert {f.evidence["exp"] for f in findings} == {"800"}
    assert {f.evidence["gold"] for f in findings} == {"80"}
    assert 10009 in {f.evidence["item"] for f in findings}


@pytest.mark.corpus
def test_the_1304_1323_weapon_bag_is_silent_on_the_working_tree(at_worktree):
    """The patch-002 wave fixed it. Fire-then-quiet is the whole assertion."""
    findings = [f for f in check_duplication(at_worktree, ZONE_13)
                if f.evidence.get("quests") == [1304, 1323]]

    assert findings == []


@pytest.mark.corpus
def test_item_160_is_the_single_purchasable_overlap_in_zone_13(at_worktree):
    """Measured calibration: zone-13 rewards intersect the shops on exactly one
    item, the deliberate recall-scroll gift. Shops in scope are cheap."""
    purchasable = [f for f in check_duplication(at_worktree, ZONE_13)
                   if f.evidence.get("purchasable_from")]

    assert [f.evidence["item"] for f in purchasable] == [160]
    assert purchasable[0].evidence["purchasable_from"] == ["BuyList"]


@pytest.mark.corpus
def test_the_kugai_overlap_does_not_coexist_in_either_snapshot(at_baseline, at_worktree):
    """Documented, not silently skipped.

    Quest 1315 granted 24 items at the baseline and the Kugai Weapons list did
    not exist yet; the working tree has the shop and 1315 grants nothing. The
    defect was real in a transient state during the session that produced it,
    and neither snapshot can serve as its oracle, so the structure is pinned by
    the hermetic test above instead.
    """
    at_base = at_baseline.rewards.get(1315)
    now = at_worktree.rewards.get(1315)

    assert at_base is not None and len(at_base["items"]) == 24
    assert now is not None and now["items"] == []
    assert 12137 not in at_baseline.item_sources or \
        "BuyList" not in at_baseline.item_sources[12137]
    assert "BuyList" in at_worktree.item_sources[12137]


@pytest.mark.corpus
def test_every_declared_source_family_actually_yields_item_ids(datasheet_dir, baseline):
    """A family silently absent from the reader is the failure mode here.

    The check reports "granted by exactly one source" for an item that three
    other families also hand out, and nothing about the output looks wrong.
    """
    empty = []
    for source in ITEM_SOURCES:
        found = scan_item_sources(datasheet_dir, read=baseline.read, families={source.family})
        if not found:
            empty.append(source.family)

    assert empty == [], f"declared but yielding nothing: {empty}"


@pytest.mark.corpus
def test_the_source_universe_covers_the_expected_families(datasheet_dir, baseline):
    families = set()
    for item_families in scan_item_sources(datasheet_dir, read=baseline.read).values():
        families |= item_families

    assert {"QuestCompensation", "ECompensation", "CCompensation", "ICompensation",
            "FCompensation", "WorldDrop", "BuyList", "ItemMedalExchange",
            "TokenExchange", "Gacha"} <= families
