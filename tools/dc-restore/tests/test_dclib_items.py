"""The dclib item model: levels, class gating, and gear-set identity.

Every rule here was derived by measuring the corpus, not by reading a schema.
The hermetic tests pin the derivation; the corpus tests prove the derivation
still describes the real data at the pinned baseline.
"""

from __future__ import annotations

import pytest

from dclib import (
    CLASS_ARMOUR,
    EQUIPMENT_TYPES,
    ItemInfo,
    ItemModel,
    item_template_files,
    load_item_model,
    parse_item_template,
)


def item(**attrs) -> ItemInfo:
    base = {"id": "1", "name": "x", "combatItemType": "EQUIP_ARMOR_BODY",
            "combatItemSubType": "bodyLeather", "linkLookInfoId": "211005"}
    base.update({k: str(v) for k, v in attrs.items()})
    return ItemInfo(base)


# ---------------------------------------------------------------------------
# Look-id decoding: three layouts, one tier
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("look,subtype,family,slot,tier", [
    # Layout A, the 6,489-item majority: armourType | slot | tier.
    ("213005", "feetLeather", "leather", "feet", "005"),
    ("311007", "bodyMail", "mail", "body", "007"),
    ("413116", "feetRobe", "robe", "feet", "116"),
    # Layout A with a leading digit (26 items). The tier is still the last three.
    ("9311043", "bodyMail", "mail", "body", "043"),
    ("9313043", "feetMail", "mail", "feet", "043"),
    # Layout B (31 leather items): slot 3/4/5, a literal 10, then the tier.
    # Reading digit 1 as the armour type would call this a mail body item.
    ("310106", "bodyLeather", "leather", "body", "106"),
    ("410106", "handLeather", "leather", "hand", "106"),
    ("510106", "feetLeather", "leather", "feet", "106"),
])
def test_family_and_slot_come_from_subtype_tier_from_look_id(look, subtype, family, slot, tier):
    it = item(linkLookInfoId=look, combatItemSubType=subtype)

    assert (it.family, it.slot, it.tier) == (family, slot, tier)


def test_a_set_is_family_plus_tier_across_slots():
    """The three slots of one visual set share a tier, in either layout."""
    a = item(id=1, combatItemSubType="bodyLeather", linkLookInfoId="211005")
    b = item(id=2, combatItemSubType="handLeather", linkLookInfoId="212005")
    c = item(id=3, combatItemSubType="feetLeather", linkLookInfoId="213005")
    odd = item(id=4, combatItemSubType="feetLeather", linkLookInfoId="510100")

    assert a.set_key == b.set_key == c.set_key == ("leather", "005")
    assert odd.set_key == ("leather", "100"), "a different tier is a different set"


def test_tier_is_not_level():
    """Never infer one from the other: the corpus disagrees at every tier."""
    low = item(linkLookInfoId="213005", combatItemSubType="feetLeather", requiredLevel=4)
    high = item(linkLookInfoId="413116", combatItemSubType="feetRobe", requiredLevel=58)

    assert low.tier == "005" and low.required_level == 4
    assert high.tier == "116" and high.required_level == 58
    assert int(high.tier) != high.required_level


def test_missing_or_zero_look_id_has_no_set():
    assert item(linkLookInfoId="0").set_key is None
    assert item(linkLookInfoId="").tier == ""
    assert item(combatItemSubType="potion", linkLookInfoId="211005").set_key is None


# ---------------------------------------------------------------------------
# Equipment allow-list and class gating
# ---------------------------------------------------------------------------

def test_equipment_is_an_allow_list_not_a_prefix():
    """startswith("EQUIP") sweeps in ~4,100 cosmetic and underwear items.

    repeatable-rewards fires on every costume repeatable in the game if this
    degrades to a prefix test.
    """
    assert item(combatItemType="EQUIP_ARMOR_BODY").is_equipment
    assert item(combatItemType="EQUIP_WEAPON").is_equipment
    assert not item(combatItemType="EQUIP_COSTUME").is_equipment
    assert not item(combatItemType="EQUIP_UNDERWEAR").is_equipment
    assert not item(combatItemType="DISPOSAL").is_equipment
    assert "EQUIP_COSTUME" not in EQUIPMENT_TYPES


def test_class_compare_is_case_insensitive_in_both_directions():
    """ItemTemplate is UPPERCASE, compensation class attrs are lowercase."""
    it = item(requiredClass="WARRIOR;SLAYER;ARCHER;GLAIVER;SOULLESS")

    assert it.admits("slayer") and it.admits("SLAYER")
    assert not it.admits("lancer")
    assert it.required_class == {"WARRIOR", "SLAYER", "ARCHER", "GLAIVER", "SOULLESS"}


def test_empty_required_class_admits_everyone():
    assert item(requiredClass="").admits("lancer")


def test_class_armour_map_is_a_partition_of_the_roster():
    """Every class wears exactly one family; no class is in two."""
    seen: set[str] = set()
    for family, classes in CLASS_ARMOUR.items():
        assert not (seen & classes), f"{family} overlaps an earlier family"
        seen |= classes

    assert len(seen) == 13, "the roster is 13 classes"
    assert "SOULLESS" in CLASS_ARMOUR["leather"]
    assert "FIGHTER" in CLASS_ARMOUR["mail"]


# ---------------------------------------------------------------------------
# Shard loading
# ---------------------------------------------------------------------------

SHARD_BASE = """<?xml version="1.0" encoding="utf-8"?>
<ItemData>
  <Item id="10" name="base_a" requiredLevel="4" combatItemType="EQUIP_ARMOR_LEG"
        combatItemSubType="feetLeather" linkLookInfoId="213005" requiredClass="WARRIOR" />
  <Item id="11" name="base_b" combatItemType="DISPOSAL" linkLookInfoId="0" />
</ItemData>
"""

SHARD_KR = """<?xml version="1.0" encoding="utf-8"?>
<ItemData>
  <Item id="900" name="kr_only" requiredLevel="7" combatItemType="EQUIP_WEAPON"
        combatItemSubType="sword" linkLookInfoId="0" requiredClass="WARRIOR;SLAYER" />
</ItemData>
"""


def test_shards_are_merged_because_their_id_spaces_are_disjoint(corpus_dir):
    """19% of quest-reward item ids exist only in a non-base shard.

    Applying the BuyList "base filenames only" rule here would leave a fifth of
    every reward table without level or class data, which every reward check
    then reports as unknown rather than as a finding.
    """
    root = corpus_dir({"ItemTemplate.xml": SHARD_BASE, "ItemTemplate_KR.xml": SHARD_KR},
                      bom=False, crlf=False)

    model = load_item_model(root)

    assert len(model) == 3
    assert 900 in model, "a shard-only id must resolve"
    assert model.get(900).source == "ItemTemplate_KR.xml"
    assert model.get(10).source == "ItemTemplate.xml"


def test_base_shard_is_read_first(corpus_dir):
    root = corpus_dir({"ItemTemplate.xml": SHARD_BASE, "ItemTemplate_KR.xml": SHARD_KR},
                      bom=False, crlf=False)

    assert item_template_files(root)[0] == "ItemTemplate.xml"


def test_load_accepts_an_injected_reader(corpus_dir):
    """Baseline reads route through V92Baseline.read, not the filesystem."""
    root = corpus_dir({"ItemTemplate.xml": SHARD_BASE}, bom=False, crlf=False)
    served = {"ItemTemplate.xml": SHARD_KR}  # deliberately different content

    model = load_item_model(root, read=served.get)

    assert 900 in model and 10 not in model, "the injected reader must win"


def test_sets_group_by_family_and_tier(corpus_dir):
    model = ItemModel(parse_item_template(SHARD_BASE))
    sets = model.sets()

    assert sets == {("leather", "005"): {"feet": [10]}}


# ---------------------------------------------------------------------------
# Corpus tier: the derivation still describes the real data
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def corpus_items(baseline, datasheet_dir):
    return load_item_model(datasheet_dir, read=baseline.read)


@pytest.mark.corpus
def test_base_shard_item_count_at_the_baseline(baseline):
    """ItemTemplate.xml is itself dirty in a patch working tree.

    The tree carries 36,528 items while the baseline carries 34,276, which is
    why every count here is read through the pinned baseline rather than off
    disk. A disk read would drift by 2,252 items the moment a patch adds gear.
    """
    base = parse_item_template(baseline.read("ItemTemplate.xml"))

    assert len(base) == 34276


@pytest.mark.corpus
def test_shard_id_spaces_do_not_overlap(baseline, corpus_items):
    """The premise of merging: no shard redefines a base id."""
    base = set(parse_item_template(baseline.read("ItemTemplate.xml")))
    merged = set(corpus_items.items)

    shard_only = merged - base
    assert len(shard_only) == 75864, "shards add ids, they never override them"
    assert len(merged) == len(base) + len(shard_only)


@pytest.mark.corpus
def test_every_quest_reward_item_resolves_in_the_merged_model(baseline, corpus_items):
    """The measurement that forced the merge: base-only leaves 171 unresolved."""
    import re
    from pathlib import Path

    refs: set[int] = set()
    comp_dir = Path(baseline.datasheet_dir) / "CompensationData"
    for path in sorted(comp_dir.glob("QuestCompensationData*.xml")):
        text = baseline.read(f"CompensationData/{path.name}")
        if text is None:
            continue
        refs |= {int(m) for m in re.findall(r'templateId="(\d+)"', text)}

    base = parse_item_template(baseline.read("ItemTemplate.xml"))
    unresolved_base = {r for r in refs if r not in base}
    unresolved_merged = {r for r in refs if r not in corpus_items}

    assert len(refs) == 925
    assert len(unresolved_base) == 171, "base-only loses 19% of reward items"
    assert unresolved_merged == set(), "the merged model resolves every reward item"


@pytest.mark.corpus
def test_armour_look_ids_decode_for_every_armour_item(corpus_items):
    """No armour item falls outside the two layouts."""
    armour = [it for it in corpus_items.items.values()
              if it.combat_type.startswith("EQUIP_ARMOR") and it.look_id not in ("", "0")]
    undecodable = [it for it in armour if not it.set_key]

    assert undecodable == [], "every armour item with a look id must have a set key"
    assert all(it.slot in ("body", "hand", "feet") for it in armour)
    assert all(it.family in ("leather", "mail", "robe") for it in armour)


@pytest.mark.corpus
def test_the_31_alternate_layout_items_group_with_their_own_family(corpus_items):
    """Layout B: reading digit 1 as armour type would scatter these into mail,
    robe and a nonexistent family 5, splitting one set into three."""
    odd = [it for it in corpus_items.items.values()
           if len(it.look_id) == 6 and it.look_id[1:3] == "10"
           and it.combat_type.startswith("EQUIP_ARMOR")]

    assert len(odd) == 37, "31 in the base shard, 6 more across the regional shards"
    assert {it.family for it in odd} == {"leather"}
    assert {it.look_id[0] for it in odd} == {"3", "4", "5"}, "leading digit is the slot here"
    # Grouped correctly, the three slots of one tier form one set rather than
    # scattering across mail, robe and a nonexistent family 5.
    by_set: dict[tuple[str, str], set[str]] = {}
    for it in odd:
        by_set.setdefault(it.set_key, set()).add(it.slot)
    assert any(slots == {"body", "hand", "feet"} for slots in by_set.values())


@pytest.mark.corpus
def test_known_items_carry_the_expected_gating(corpus_items):
    """Spot anchors from the defects the checks were written for."""
    feet = corpus_items.get(17409)
    assert feet.required_level == 4
    assert feet.set_key == ("leather", "005")
    assert feet.required_class == {"WARRIOR", "SLAYER", "ARCHER", "GLAIVER", "SOULLESS"}

    scroll = corpus_items.get(160)
    assert not scroll.is_equipment, "the deliberate gift item is not gear"
