"""The three report sections.

A report is not a check and the tests hold it to a different bar. There is no
positive-and-negative oracle pair here, because there is no defect to fire on:
the contract is that the numbers are right, that nothing is silently collapsed,
and that no severity ever leaks in. Severity is the whole distinction, so it is
asserted as a contract rather than assumed.

Assertions are structural. A golden output file for a table turns every column
tweak into a failure that teaches nothing, so the tests assert that a set with
three carriers yields three rows, that a chain is detected, that a multi-spawn
template lists every spawn, and only occasionally that one specific value shows
up in the rendered text.

Every corpus-tier constant here was measured against the datasheet at the pinned
baseline, never copied from a plan.
"""

from __future__ import annotations

import re

import pytest

import audit_reports as R
from audit_reports import (
    Carrier,
    NpcPlacement,
    Spawn,
    atlas,
    chain_links,
    effort_counts,
    effort_reward,
    giver_index,
    giver_load,
    hunt_quest_share,
    level_band,
    parse_area_sections,
    parse_pos,
    resolve_section,
    set_placements,
    turn_in_ref,
    verb_histogram,
)
from auditlib import CHECKS, REPORTS, Corpus, Finding, Scope
from dclib import V92Baseline

# Words a report must never print. Severity expresses confidence that something
# is a defect; a table of distances makes no such claim, and borrowing the
# vocabulary is how a descriptive section starts being argued with.
SEVERITY_WORDS = ("HIGH", "MEDIUM", "INFO", "SEVERITY", "WARNING", "WARN",
                  "ERROR", "CRITICAL", "PASS", "FAIL", "VIOLATION")


# ---------------------------------------------------------------------------
# Synthetic tree builders
# ---------------------------------------------------------------------------

def quest_xml(gid: int, hz: int, local: int, *, giver: str = "", min_level: str = "",
              tasks: str = "") -> str:
    trigger = f"<발생조건><NPC대화>{giver}</NPC대화></발생조건>" if giver else ""
    cond = f"<수행조건><최소레벨>{min_level}</최소레벨></수행조건>" if min_level else ""
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<Quest id="{gid}">\n'
            f"  <Header><Quest번호>{hz},{local}</Quest번호>{cond}{trigger}</Header>\n"
            f"  <Tasks>{tasks}</Tasks>\n</Quest>\n")


def task_xml(task_id: int, name: str, body: str) -> str:
    return (f'<Task id="{task_id}"><Header><이름>{name}</이름></Header>'
            f"<Body>{body}</Body></Task>")


def hunt_body(monster: str, kills: int, target_npc: str = "") -> str:
    npc = f"<대상NPC지정>{target_npc}</대상NPC지정>" if target_npc else ""
    return ("<몬스터지정><몬스터지정>"
            f"<몬스터Id>{monster}</몬스터Id><사냥마리수>{kills}</사냥마리수>"
            f"</몬스터지정></몬스터지정>{npc}")


def deliver_body(monster: str, qty: int, target_npc: str = "") -> str:
    npc = f"<대상NPC지정>{target_npc}</대상NPC지정>" if target_npc else ""
    return ("<아이템작성><아이템작성>"
            f"<전달수량>{qty}</전달수량>"
            f"<몬스터지정><몬스터지정><몬스터Id>{monster}</몬스터Id>"
            "<수여확률>100</수여확률></몬스터지정></몬스터지정>"
            f"</아이템작성></아이템작성>{npc}")


def collect_body(qty: int, target_npc: str = "") -> str:
    npc = f"<대상NPC지정>{target_npc}</대상NPC지정>" if target_npc else ""
    return ("<채집물지정><채집물지정><콜렉션Id>410</콜렉션Id></채집물지정></채집물지정>"
            "<전달아이템지정><전달아이템지정><아이템Id>9011</아이템Id>"
            f"<전달수량>{qty}</전달수량></전달아이템지정></전달아이템지정>{npc}")


def group_body(monster: str, kills: int, target_npc: str = "") -> str:
    npc = f"<대상NPC지정>{target_npc}</대상NPC지정>" if target_npc else ""
    return ("<몬스터그룹><몬스터그룹>"
            f"<그룹이름>pack</그룹이름><사냥마리수>{kills}</사냥마리수>"
            f"<몬스터지정><몬스터지정><몬스터Id>{monster}</몬스터Id></몬스터지정></몬스터지정>"
            f"</몬스터그룹></몬스터그룹>{npc}")


def visit_body(npc_ref: str) -> str:
    return f"<방문그룹><방문그룹><NPCId>{npc_ref}</NPCId></방문그룹></방문그룹>"


def comp_xml(rows) -> str:
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


def territory_xml(rows) -> str:
    """rows: (templateId, pos, desc)."""
    out = ['<?xml version="1.0" encoding="utf-8"?>', "<TerritoryData>",
           '  <TerritoryGroup id="1" desc="camp">', '    <Territory desc="camp east">']
    for tid, pos, desc in rows:
        out.append(f'      <Npc npcTemplateId="{tid}" pos="{pos}" desc="{desc}" spawnCount="1" />')
    out.extend(["    </Territory>", "  </TerritoryGroup>", "</TerritoryData>"])
    return "\n".join(out)


def npcdata_xml(rows) -> str:
    """rows: (templateId, name, spawnScriptId)."""
    out = ['<?xml version="1.0" encoding="utf-8"?>', "<NpcData>"]
    for tid, name, script in rows:
        out.append(f'  <Template id="{tid}" name="{name}" spawnScriptId="{script}" />')
    out.append("</NpcData>")
    return "\n".join(out)


ITEMS = """<?xml version="1.0" encoding="utf-8"?>
<ItemData>
  <Item id="17407" name="leather17_body" combatItemType="EQUIP_ARMOR_BODY" combatItemSubType="bodyLeather" linkLookInfoId="213005" requiredLevel="4" />
  <Item id="17408" name="leather17_hand" combatItemType="EQUIP_ARMOR_ARM" combatItemSubType="handLeather" linkLookInfoId="213005" requiredLevel="4" />
  <Item id="17409" name="leather17_feet" combatItemType="EQUIP_ARMOR_LEG" combatItemSubType="feetLeather" linkLookInfoId="213005" requiredLevel="4" />
  <Item id="10009" name="dual_01" combatItemType="EQUIP_WEAPON" combatItemSubType="dual" linkLookInfoId="0" requiredLevel="7" />
</ItemData>
"""


def build(corpus_dir, files: dict, zones=(13,)) -> tuple[Corpus, Scope]:
    tree = {"ItemTemplate.xml": ITEMS}
    tree.update(files)
    root = corpus_dir(tree, bom=False, crlf=False)
    corpus = Corpus(root, V92Baseline(root))
    return corpus, Scope(zones=set(zones) if zones else None, new_quests=None)


# ---------------------------------------------------------------------------
# Registration contract: a report is not a check
# ---------------------------------------------------------------------------

def test_the_three_sections_register_as_reports_not_checks():
    """--list-checks prints both, and the skill defers to that inventory."""
    assert {"set-placement", "giver-load", "effort-reward"} <= set(REPORTS)
    assert {"set-placement", "giver-load", "effort-reward"}.isdisjoint(CHECKS)
    assert {spec.group for spec in REPORTS.values()} == {"report"}


def test_every_report_summary_explains_what_the_table_shows():
    for spec in REPORTS.values():
        assert len(spec.summary) > 40, spec.id
        assert spec.fn.__doc__, f"{spec.id} must say why it exists"


# ---------------------------------------------------------------------------
# Geometry primitives
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("63756,-84169,-3806", (63756.0, -84169.0, -3806.0)),
    ("67089.37500000,-81620.63281250,-3255.37890625", (67089.375, -81620.6328125, -3255.37890625)),
    ("", None),
    ("1,2", None),
    ("a,b,c", None),
])
def test_position_parsing(raw, expected):
    assert parse_pos(raw) == expected


def test_distance_ignores_z():
    """Two kilometres of cliff between two points on the same path is relief,
    not travel, and folding it in makes neighbours look like strangers."""
    assert R.planar((0, 0, 0), (3, 4, 9999)) == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# AreaData section resolution
# ---------------------------------------------------------------------------

AREA = """<?xml version="1.0" encoding="utf-8"?>
<Area id="7" continentId="13">
  <Section id="4" desc="13001 the garden">
    <Fence pos="0,0,0" /><Fence pos="1000,0,0" />
    <Fence pos="1000,1000,0" /><Fence pos="0,1000,0" />
    <Section id="8" desc="13004 the rift">
      <Fence pos="100,100,0" /><Fence pos="300,100,0" />
      <Fence pos="300,300,0" /><Fence pos="100,300,0" />
    </Section>
  </Section>
  <!--<Section id="30" desc="64001 dormant camp">
    <Fence pos="500,500,0" /><Fence pos="900,500,0" />
    <Fence pos="900,900,0" /><Fence pos="500,900,0" />
  </Section>-->
</Area>
"""


def test_the_deepest_containing_section_wins():
    """Sections nest. The shallow answer names the island, which helps nobody."""
    sections = parse_area_sections(AREA)

    assert resolve_section((200, 200), sections) == "13004 the rift"
    assert resolve_section((800, 200), sections) == "13001 the garden"
    assert resolve_section((5000, 5000), sections) == ""


def test_a_commented_out_section_is_not_ground_anyone_stands_on():
    """Dormant content resolving a position would name a place the running
    server does not have."""
    sections = parse_area_sections(AREA)

    assert [s.desc for s in sections] == ["13001 the garden", "13004 the rift"]
    assert resolve_section((700, 700), sections) == "13001 the garden"


def test_section_depth_is_recorded_from_nesting():
    by_desc = {s.desc: s for s in parse_area_sections(AREA)}

    assert by_desc["13001 the garden"].depth == 0
    assert by_desc["13004 the rift"].depth == 1


# ---------------------------------------------------------------------------
# NPC placement: never a silent pick
# ---------------------------------------------------------------------------

def placement_corpus(corpus_dir, territory_rows, npc_rows) -> Corpus:
    corpus, _ = build(corpus_dir, {
        "QuestData/001301.quest": quest_xml(1301, 13, 1),
        f"TerritoryData_13.xml": territory_xml(territory_rows),
        f"NpcData_13.xml": npcdata_xml(npc_rows),
    })
    return corpus


def test_a_multi_spawn_template_lists_every_spawn(corpus_dir):
    """Two spawns is two answers. Reporting the first is wrong half the time."""
    corpus = placement_corpus(
        corpus_dir,
        [(500, "100,200,0", "north"), (500, "900,200,0", "south")],
        [(500, "Wanderer", "0")],
    )

    placement = atlas(corpus).placement("13,500")

    assert len(placement.spawns) == 2
    assert {s.pos[0] for s in placement.spawns} == {100.0, 900.0}
    assert placement.multi_spawn
    assert "2 spawns" in placement.caveat


def test_a_multi_spawn_template_yields_a_distance_span_not_a_number(corpus_dir):
    corpus = placement_corpus(
        corpus_dir,
        [(500, "0,0,0.5", "north"), (500, "300,400,0.5", "south"), (600, "0,0,1", "hub")],
        [(500, "Wanderer", "0"), (600, "Quartermaster", "0")],
    )
    npcs = atlas(corpus)

    span = R.distance_span(npcs.placement("13,600"), npcs.placement("13,500"))

    assert span == pytest.approx((0.0, 500.0))
    assert R.fmt_span(span) == "0..500"


def test_a_script_placed_npc_is_called_out(corpus_dir):
    """spawnScriptId means the script decides where the player meets them, so
    the standing position is a lower bound on the truth, not the truth."""
    corpus = placement_corpus(
        corpus_dir, [(700, "10,10,0", "dock")], [(700, "Ramun", "121310051")])

    placement = atlas(corpus).placement("13,700")

    assert placement.script_placed
    assert "spawnScriptId 121310051" in placement.caveat


@pytest.mark.parametrize("script,expected", [("", False), ("0", False), ("10023", True)])
def test_script_placement_detection(script, expected, corpus_dir):
    corpus = placement_corpus(corpus_dir, [(700, "1,1,0", "x")], [(700, "N", script)])

    assert atlas(corpus).placement("13,700").script_placed is expected


def test_an_origin_spawn_is_marked_unplaced_rather_than_used(corpus_dir):
    """0,0,0 means something other than this territory places the NPC. Treating
    it as a position puts every such NPC at the same fictional spot."""
    corpus = placement_corpus(
        corpus_dir, [(800, "0.00000000,0.00000000,0.00000000", "ghost")],
        [(800, "Unplaced", "0")])

    placement = atlas(corpus).placement("13,800")

    assert len(placement.spawns) == 1
    assert placement.placed_spawns == ()
    assert "no standing spawn" in placement.caveat
    assert R.hub_span((0.0, 0.0), placement) is None


def test_an_npc_with_no_spawn_entry_says_so(corpus_dir):
    corpus = placement_corpus(corpus_dir, [(900, "1,1,0", "x")], [(900, "Present", "0")])

    placement = atlas(corpus).placement("13,901")

    assert placement.known
    assert placement.spawns == ()
    assert "no spawn entry" in placement.caveat


@pytest.mark.parametrize("ref", ["", "nonsense", "13", "13,abc", "a,1"])
def test_an_unusable_reference_yields_an_unknown_placement(ref, corpus_dir):
    corpus = placement_corpus(corpus_dir, [(900, "1,1,0", "x")], [(900, "Present", "0")])

    assert atlas(corpus).placement(ref).known is False


def test_the_atlas_is_shared_per_corpus(corpus_dir):
    """Three sections read each zone file once, not three times."""
    corpus = placement_corpus(corpus_dir, [(900, "1,1,0", "x")], [(900, "Present", "0")])

    assert atlas(corpus) is atlas(corpus)


# ---------------------------------------------------------------------------
# Turn-in derivation
# ---------------------------------------------------------------------------

def test_turn_in_is_the_last_task_target_npc(corpus_dir):
    corpus, _ = build(corpus_dir, {"QuestData/001332.quest": quest_xml(
        1332, 13, 32, giver="213,1009",
        tasks=task_xml(1, "사냥전달Task", deliver_body("13,300920", 4, "213,1130")))})

    assert turn_in_ref(corpus.quests[1332]) == "213,1130"


def test_a_quest_that_ends_on_a_conversation_turns_in_at_that_npc(corpus_dir):
    """A visit task's target IS the NPC. Reading only 대상NPC지정 drops every
    quest that ends by talking to someone."""
    corpus, _ = build(corpus_dir, {"QuestData/001305.quest": quest_xml(
        1305, 13, 5, giver="64,1001",
        tasks=(task_xml(1, "사냥Task", hunt_body("13,301", 5, "64,1001"))
               + task_xml(2, "방문Task", visit_body("64,1009"))))})

    assert turn_in_ref(corpus.quests[1305]) == "64,1009"


def test_a_quest_with_no_target_has_no_turn_in(corpus_dir):
    corpus, _ = build(corpus_dir, {"QuestData/001321.quest": quest_xml(1321, 13, 21)})

    assert turn_in_ref(corpus.quests[1321]) == ""


# ---------------------------------------------------------------------------
# set-placement
# ---------------------------------------------------------------------------

SET_TREE = {
    "QuestData/001322.quest": quest_xml(
        1322, 13, 22, giver="13,1003", min_level="4",
        tasks=task_xml(1, "사냥전달Task", deliver_body("13,500", 5, "13,1017"))),
    "QuestData/001324.quest": quest_xml(
        1324, 13, 24, giver="13,1017", min_level="4",
        tasks=task_xml(1, "사냥전달Task", deliver_body("13,500", 5, "13,1017"))),
    "QuestData/001325.quest": quest_xml(
        1325, 13, 25, giver="13,1121", min_level="4",
        tasks=task_xml(1, "사냥전달Task", deliver_body("13,500", 5, "13,1121"))),
    "CompensationData/QuestCompensationData_13.xml": comp_xml([
        (1322, "500", "50", [17409]),
        (1324, "900", "90", [17407]),
        (1325, "500", "50", [17408]),
    ]),
    "TerritoryData_13.xml": territory_xml([
        (1003, "86917,-85129,0", "Keisha"),
        (1017, "80937,-81364,0", "Kaimon"),
        (1121, "73563,-83041,0", "Ryan"),
        (500, "70000,-80000,0", "Gilliduk"),
    ]),
    "NpcData_13.xml": npcdata_xml([
        (1003, "Keisha", "0"), (1017, "Kaimon", "0"),
        (1121, "Ryan", "0"), (500, "Gilliduk", "0"),
    ]),
}


def test_a_set_with_three_carriers_yields_three_rows(corpus_dir):
    corpus, scope = build(corpus_dir, SET_TREE)

    placements = set_placements(corpus, scope)

    assert len(placements) == 1
    assert (placements[0].family, placements[0].tier) == ("leather", "005")
    assert [c.quest for c in placements[0].carriers] == [1322, 1324, 1325]
    assert [c.slots for c in placements[0].carriers] == [("feet",), ("body",), ("hand",)]


def test_a_carrier_carries_its_giver_and_turn_in_placements(corpus_dir):
    corpus, scope = build(corpus_dir, SET_TREE)

    carrier = set_placements(corpus, scope)[0].carriers[0]

    assert carrier.giver.ref == "13,1003"
    assert carrier.giver.name == "Keisha"
    assert carrier.turn_in.ref == "13,1017"
    assert carrier.turn_in.name == "Kaimon"


def test_the_chain_relationship_is_detected(corpus_dir):
    """One quest's turn-in NPC is the next quest's giver: the placement that
    costs a player nothing, and the one shape worth naming."""
    corpus, scope = build(corpus_dir, SET_TREE)

    chains = set_placements(corpus, scope)[0].chains

    assert (1322, 1324, "13,1017") in chains


def test_a_chain_reaches_outside_the_set(corpus_dir):
    """1332 hands a set piece into 1333, which hands over a weapon. A lookup
    confined to the set's own carriers cannot see that pair at all."""
    tree = dict(SET_TREE)
    tree["QuestData/001333.quest"] = quest_xml(
        1333, 13, 33, giver="13,1121", min_level="6",
        tasks=task_xml(1, "사냥전달Task", deliver_body("13,500", 6, "13,1121")))
    tree["CompensationData/QuestCompensationData_13.xml"] = comp_xml([
        (1322, "500", "50", [17409]),
        (1324, "900", "90", [17407]),
        (1325, "500", "50", [17408]),
        (1333, "1700", "170", [10009]),     # a weapon: no set key at all
    ])
    corpus, scope = build(corpus_dir, tree)

    chains = set_placements(corpus, scope)[0].chains

    assert (1325, 1333, "13,1121") in chains


def test_no_chain_is_stated_explicitly_rather_than_left_blank(corpus_dir):
    tree = dict(SET_TREE)
    tree["QuestData/001324.quest"] = quest_xml(
        1324, 13, 24, giver="13,9999", min_level="4",
        tasks=task_xml(1, "사냥전달Task", deliver_body("13,500", 5, "13,9998")))
    corpus, scope = build(corpus_dir, tree)

    lines = R.report_set_placement(corpus, scope)

    assert any("chain: none" in line for line in lines)


def test_chain_links_never_link_a_quest_to_itself():
    """A quest whose giver is also its turn-in is the single most common shape
    in the zone, and it is not a chain."""
    giver = NpcPlacement(ref="13,1", hz=13, template=1, name="Self",
                         spawns=(Spawn((0, 0, 0), "", "", ""),))
    carrier = Carrier(quest=1326, items=(1,), slots=("feet",), giver=giver, turn_in=giver)

    assert chain_links([carrier], giver_index({1326: {"giver": "13,1"}})) == []


def test_a_sentinel_disabled_carrier_is_marked_not_offerable(corpus_dir):
    """A quest behind a 99,99 prerequisite still holds its rewards in the data
    but cannot be taken, and a placement table that hides that is misleading."""
    tree = dict(SET_TREE)
    tree["QuestData/001324.quest"] = quest_xml(1324, 13, 24, giver="13,1017", min_level="4").replace(
        "<수행조건><최소레벨>4</최소레벨></수행조건>",
        "<수행조건><최소레벨>4</최소레벨><선행퀘스트><선행퀘스트>"
        "<퀘스트Id>99,99</퀘스트Id></선행퀘스트></선행퀘스트></수행조건>")
    corpus, scope = build(corpus_dir, tree)

    carriers = {c.quest: c for c in set_placements(corpus, scope)[0].carriers}

    assert carriers[1324].offerable is False
    assert carriers[1322].offerable is True
    assert any("not offerable" in line for line in R.report_set_placement(corpus, scope))


def test_round_trip_sums_the_three_legs(corpus_dir):
    corpus, scope = build(corpus_dir, SET_TREE)
    npcs = atlas(corpus)
    hub = (70000.0, -80000.0)
    giver = npcs.placement("13,1003")
    turn_in = npcs.placement("13,1017")

    legs = (R.hub_span(hub, giver)[0], R.distance_span(giver, turn_in)[0],
            R.hub_span(hub, turn_in)[0])

    assert R.round_trip(hub, giver, turn_in)[0] == pytest.approx(sum(legs))


def test_round_trip_is_unavailable_when_an_endpoint_has_no_spawn(corpus_dir):
    """An unplaced endpoint means the distance is unknown, and printing a number
    anyway is the failure this whole section exists to avoid."""
    corpus, scope = build(corpus_dir, SET_TREE)
    npcs = atlas(corpus)

    assert R.round_trip((0.0, 0.0), npcs.placement("13,1003"), npcs.placement("13,4242")) is None
    assert R.fmt_span(None) == "n/a"


def test_positions_resolve_into_area_section_names(corpus_dir, monkeypatch):
    """A coordinate pair tells a designer nothing; a section name tells them
    which camp they are standing in."""
    tree = dict(SET_TREE)
    tree["TerritoryData_13.xml"] = territory_xml([(1003, "200,200,0", "Keisha")])
    tree["AreaData/AreaData_13_ATW_Death_P.xml"] = AREA
    monkeypatch.setitem(R.ZONE_PROFILES, 13, R.ZoneProfile(
        hub=(0.0, 0.0), hub_name="test hub",
        area_files=("AreaData/AreaData_13_ATW_Death_P.xml",)))
    corpus, scope = build(corpus_dir, tree)

    carrier = set_placements(corpus, scope)[0].carriers[0]

    assert carrier.giver.spawns[0].section == "13004 the rift"


# ---------------------------------------------------------------------------
# giver-load
# ---------------------------------------------------------------------------

LOAD_TREE = {
    "QuestData/001371.quest": quest_xml(
        1371, 13, 71, giver="13,1017", min_level="4",
        tasks=task_xml(1, "사냥전달Task", deliver_body("13,500", 5, "13,1017"))),
    "QuestData/001372.quest": quest_xml(
        1372, 13, 72, giver="13,1017", min_level="4",
        tasks=task_xml(1, "사냥전달Task", deliver_body("13,500", 5, "13,1017"))),
    "QuestData/001373.quest": quest_xml(
        1373, 13, 73, giver="13,1017", min_level="9",
        tasks=task_xml(1, "사냥Task", hunt_body("13,501", 5, "13,1017"))),
    "TerritoryData_13.xml": territory_xml([
        (1017, "80937,-81364,0", "Kaimon"),
        (500, "70000,-80000,0", "Argas"),
        (501, "71000,-80000,0", "Okan"),
    ]),
    "NpcData_13.xml": npcdata_xml([
        (1017, "Kaimon", "0"), (500, "Argas", "0"), (501, "Okan", "0")]),
}


def test_quests_sharing_giver_verb_target_and_band_collapse_to_one_row(corpus_dir):
    """This is what "repetitive" looks like once it is counted: one giver, one
    verb, one target family, one band, listed together."""
    corpus, scope = build(corpus_dir, LOAD_TREE)

    rows = giver_load(corpus, scope)
    same = [r for r in rows if r.quests == (1371, 1372)]

    assert len(same) == 1
    assert same[0].giver == "13,1017"
    assert same[0].giver_name == "Kaimon"
    assert same[0].task_type == "사냥전달Task"
    assert same[0].target == "Argas"
    assert same[0].band == "1-5"


def test_a_different_band_or_target_splits_the_row(corpus_dir):
    corpus, scope = build(corpus_dir, LOAD_TREE)

    rows = giver_load(corpus, scope)

    assert {(r.band, r.target, r.quests) for r in rows} == {
        ("1-5", "Argas", (1371, 1372)),
        ("6-10", "Okan", (1373,)),
    }


@pytest.mark.parametrize("level,band", [("1", "1-5"), ("5", "1-5"), ("6", "6-10"),
                                        ("10", "6-10"), ("11", "11-15"), ("", "?")])
def test_level_bands(level, band):
    assert level_band({"min_level": level}) == band


def test_the_verb_histogram_counts_tasks_not_quests(corpus_dir):
    corpus, scope = build(corpus_dir, LOAD_TREE)

    assert verb_histogram(corpus, scope) == {"사냥전달Task": 2, "사냥Task": 1}


def test_the_hunt_share_is_a_ratio_and_nothing_else(corpus_dir):
    """Whether a ratio is too high is exactly the judgment this declines."""
    tree = dict(LOAD_TREE)
    tree["QuestData/001321.quest"] = quest_xml(
        1321, 13, 21, giver="13,1017", tasks=task_xml(1, "방문Task", visit_body("13,1017")))
    corpus, scope = build(corpus_dir, tree)

    assert hunt_quest_share(corpus, scope) == (3, 4)


def test_a_task_with_several_targets_names_them_all(corpus_dir):
    tree = dict(LOAD_TREE)
    tree["QuestData/001374.quest"] = quest_xml(
        1374, 13, 74, giver="13,1017", min_level="4",
        tasks=task_xml(1, "그룹사냥Task", group_body("13,500", 5).replace(
            "</몬스터지정></몬스터그룹>",
            "<몬스터지정><몬스터Id>13,501</몬스터Id></몬스터지정></몬스터지정></몬스터그룹>")))
    corpus, scope = build(corpus_dir, tree)

    rows = {r.quests: r for r in giver_load(corpus, scope) if r.task_type == "그룹사냥Task"}

    assert rows[(1374,)].target == "Argas+Okan"


def test_a_task_with_no_hunt_target_reads_as_a_dash(corpus_dir):
    corpus, scope = build(corpus_dir, {
        "QuestData/001321.quest": quest_xml(
            1321, 13, 21, giver="13,1017", tasks=task_xml(1, "방문Task", visit_body("13,1017"))),
    })

    assert giver_load(corpus, scope)[0].target == "-"


# ---------------------------------------------------------------------------
# effort-reward
# ---------------------------------------------------------------------------

def test_the_three_hunt_shapes_are_counted_from_three_different_places(corpus_dir):
    """사냥Task counts per monster entry, 사냥전달Task per BAG, 그룹사냥Task per
    GROUP. Reading one place and calling it the count reports zero for the other
    two thirds of the corpus."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001349.quest": quest_xml(1349, 13, 49, tasks=(
            task_xml(1, "사냥Task", hunt_body("13,500", 6))
            + task_xml(2, "사냥Task", hunt_body("13,501", 48))
            + task_xml(3, "그룹사냥Task", group_body("13,502", 5))
            + task_xml(4, "사냥전달Task", deliver_body("13,503", 8))
            + task_xml(5, "채집Task", collect_body(5)))),
    })

    kills, delivered, collected = effort_counts(corpus.quests[1349])

    assert (kills, delivered, collected) == (59, 8, 5)


def test_effort_rows_pair_the_ask_with_the_payout(corpus_dir):
    corpus, scope = build(corpus_dir, {
        "QuestData/001348.quest": quest_xml(
            1348, 13, 48, tasks=task_xml(1, "사냥전달Task", deliver_body("13,302", 8, "13,1147"))),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([
            (1348, "900", "90", [17409, 17408])]),
    })

    row = effort_reward(corpus, scope)[0]

    assert (row.quest, row.tasks, row.delivered) == (1348, 1, 8)
    assert (row.exp, row.gold, row.items) == (900, 90, 2)


def test_a_quest_with_no_reward_row_reads_as_zero_not_as_missing(corpus_dir):
    corpus, scope = build(corpus_dir, {
        "QuestData/001321.quest": quest_xml(1321, 13, 21)})

    row = effort_reward(corpus, scope)[0]

    assert (row.exp, row.gold, row.items) == (0, 0, 0)


def test_effort_rows_are_sorted_by_quest_and_carry_no_flags(corpus_dir):
    """Sorted raw, unflagged. A threshold is judgment; a table is deterministic."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001349.quest": quest_xml(
            1349, 13, 49, tasks=task_xml(1, "사냥Task", hunt_body("13,500", 54))),
        "QuestData/001321.quest": quest_xml(1321, 13, 21),
    })

    rows = effort_reward(corpus, scope)

    assert [r.quest for r in rows] == [1321, 1349]
    assert not any(hasattr(r, "flag") or hasattr(r, "severity") for r in rows)


# ---------------------------------------------------------------------------
# The contract that separates a report from a check
# ---------------------------------------------------------------------------

def all_report_lines(corpus, scope) -> list[str]:
    lines: list[str] = []
    for spec in REPORTS.values():
        lines.extend(spec.fn(corpus, scope) or [])
    return lines


def test_reports_return_plain_lines_and_never_findings(corpus_dir):
    corpus, scope = build(corpus_dir, SET_TREE)

    for spec in REPORTS.values():
        rows = spec.fn(corpus, scope) or []
        assert all(isinstance(row, str) for row in rows), spec.id
        assert not any(isinstance(row, Finding) for row in rows), spec.id


def test_no_report_line_carries_a_severity_word(corpus_dir):
    """Severity expresses confidence that something is a defect. A distance
    table makes no such claim, and borrowing the vocabulary invites an argument
    where a designer should just be reading."""
    corpus, scope = build(corpus_dir, SET_TREE)
    text = "\n".join(all_report_lines(corpus, scope)).upper()

    hits = [word for word in SEVERITY_WORDS if re.search(rf"\b{word}\b", text)]

    assert hits == []


def test_report_output_is_deterministic(corpus_dir):
    corpus, scope = build(corpus_dir, SET_TREE)

    assert all_report_lines(corpus, scope) == all_report_lines(corpus, scope)


def test_a_report_over_an_empty_scope_produces_nothing(corpus_dir):
    corpus, scope = build(corpus_dir, SET_TREE, zones=(999,))

    assert all_report_lines(corpus, scope) == []


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
def test_island_npc_positions_resolve_to_named_sections(at_baseline):
    """Measured at the pinned baseline: both endpoints of the 1332 to 1333 pair
    are single-spawn, standing, and land in named camps."""
    npcs = atlas(at_baseline)
    profile = R.ZONE_PROFILES[13]

    rabram = npcs.placement("213,1009", profile)
    beres = npcs.placement("213,1130", profile)

    assert (rabram.name, len(rabram.spawns)) == ("라브람", 1)
    assert rabram.spawns[0].pos == (63756.0, -84169.0, -3806.0)
    assert rabram.spawns[0].section == "13033 수비대 중부 캠프"
    assert beres.spawns[0].section == "13015 쿠벨 야영지"
    assert rabram.caveat == "" and beres.caveat == ""


@pytest.mark.corpus
def test_a_real_multi_spawn_template_lists_all_twelve(at_baseline):
    """The synthetic multi-spawn test proves the shape; this proves the reader
    meets it on real data rather than on a fixture built to suit it."""
    placement = atlas(at_baseline).placement("13,3")

    assert placement.name == "타락한 흙의 정령A"
    assert len(placement.spawns) == 12
    assert placement.multi_spawn
    assert len({s.pos for s in placement.spawns}) == 12


@pytest.mark.corpus
def test_a_real_script_placed_template_is_flagged(at_baseline):
    """Template 213,1005 carries spawnScriptId 121310051 at the baseline."""
    names, _spawns, scripts = atlas(at_baseline)._zone(213)

    assert scripts[1005] == "121310051"
    assert atlas(at_baseline).placement("213,1005").script_placed


@pytest.mark.corpus
def test_a_referenced_npc_with_no_spawn_is_reported_not_guessed(at_baseline):
    """213,1020 gives quest 1389 and has no territory entry at the baseline.
    Silently placing it at the origin would put it 103,981 units from the hub,
    which is further than the island is wide."""
    placement = atlas(at_baseline).placement("213,1020")

    assert placement.name == "테온"
    assert placement.spawns == ()
    assert placement.caveat == "no spawn entry"


@pytest.mark.corpus
def test_the_1332_to_1333_chain_holds_at_both_snapshots(at_baseline, at_worktree):
    """The chain itself predates the redistribution wave: 1332 turns in at
    Beres, and Beres is the giver of 1333, in both snapshots. What the wave
    changed is which rewards ride on it."""
    for corpus in (at_baseline, at_worktree):
        index = giver_index(ZONE_13.subject_quests(corpus))

        assert turn_in_ref(corpus.quests[1332]) == "213,1130"
        assert index["213,1130"] == [1333]


@pytest.mark.corpus
def test_the_chain_surfaces_inside_the_level_7_set_on_the_working_tree(at_worktree):
    """1332 became a tier-007 carrier in the wave, so the pair is now visible
    from inside the set. At the baseline 1332 carried nothing and the same chain
    existed unseen, which is exactly the blindness this section removes."""
    tier7 = [p for p in set_placements(at_worktree, ZONE_13)
             if (p.family, p.tier) == ("leather", "007")]

    assert len(tier7) == 1
    assert [c.quest for c in tier7[0].carriers] == [1310, 1326, 1330, 1332]
    assert (1332, 1333, "213,1130") in tier7[0].chains


@pytest.mark.corpus
def test_the_level_7_set_carriers_moved_between_the_snapshots(at_baseline, at_worktree):
    """Measured, not assumed: 1305 dropped out and 1332 came in."""
    def carriers(corpus):
        return {(p.family, p.tier): [c.quest for c in p.carriers]
                for p in set_placements(corpus, ZONE_13)}

    assert carriers(at_baseline)[("leather", "007")] == [1305, 1310, 1326, 1330]
    assert carriers(at_worktree)[("leather", "007")] == [1310, 1326, 1330, 1332]


@pytest.mark.corpus
def test_the_1332_geometry_reproduces_but_the_plan_figures_do_not(at_baseline):
    """What reproduced and what did not, recorded rather than asserted away.

    Measured at the pinned baseline, planar, single-spawn endpoints:

      hub to Rabram (giver of 1332)      5,167
      Rabram to Beres (turn-in of 1332)  8,082
      hub to Beres                      11,078
      round trip for 1332               24,327
      round trip for 1333               22,156  (Beres gives and receives it)

    The plan's "two-piece cost cut from 46,380 to 27,018 units" only half
    reproduces. Walking the two quests as separate hub round trips costs 46,483,
    which is within 0.3% of its 46,380. Walking them chained costs 24,327, not
    27,018, and no combination of these endpoints produces that figure. The
    46,380 half is treated as confirmed to the precision available; the 27,018
    half is not, and is deliberately not asserted anywhere.

    The plan's other geometry claim, a level-7 weapon on an NPC named Ayrdoss
    6,208 units past the camp cluster, does not reproduce at all: no NPC
    template in hunting zones 13, 64, 213, 313, 364 or 436 carries that name,
    and at this baseline the level-7 weapon sits on quest 1305, whose giver
    stands 2,686 units from the hub, inside the camp rather than past it.
    """
    npcs = atlas(at_baseline)
    hub = R.ZONE_PROFILES[13].hub
    giver = npcs.placement("213,1009")
    beres = npcs.placement("213,1130")

    assert round(R.hub_span(hub, giver)[0]) == 5167
    assert round(R.distance_span(giver, beres)[0]) == 8082
    assert round(R.hub_span(hub, beres)[0]) == 11078

    chained = round(R.round_trip(hub, giver, beres)[0])
    separate = chained + round(R.round_trip(hub, beres, beres)[0])

    assert chained == 24327
    assert separate == 46483


@pytest.mark.corpus
def test_the_task_verb_distribution_at_the_baseline(at_baseline):
    """The measured shape of the complaint. Visits dominate the task count and
    hunt-deliver is the most common thing a player is actually asked to do."""
    verbs = verb_histogram(at_baseline, ZONE_13)

    assert verbs["방문Task"] == 92
    assert verbs["사냥전달Task"] == 28
    assert verbs["사냥Task"] == 16
    assert verbs["그룹사냥Task"] == 2
    assert sum(verbs.values()) == 188


@pytest.mark.corpus
def test_the_hunt_concentration_claim_measured_at_both_snapshots(at_baseline, at_worktree):
    """The plan's "20 of the 34 restored zone quests are a single Hunt or
    HuntAndDeliver task" does not hold as one measurement.

    Measured over the live, non-story quests in the restored band 1301 to 1358,
    which is the only scope that yields either number:

      baseline   38 quests, 20 carrying a hunt-family task
      worktree   34 quests, 17 carrying a hunt-family task

    So the 20 is a baseline count and the 34 is a working-tree count, and the
    two halves of the sentence come from different snapshots. The stricter
    reading, quests whose ONLY task is a hunt, is 13 and 11 respectively, never
    20. The report prints the ratio for whatever scope it is given and makes no
    claim beyond it.
    """
    def pool(corpus):
        return {gid: q for gid, q in ZONE_13.subject_quests(corpus).items()
                if not q["sentinel"] and not q["story_group"] and 1301 <= gid <= 1358}

    def hunting(corpus):
        return sum(1 for q in pool(corpus).values()
                   if any(t.get("type") in R.HUNT_TASKS for t in q["tasks"].values()))

    assert (len(pool(at_baseline)), hunting(at_baseline)) == (38, 20)
    assert (len(pool(at_worktree)), hunting(at_worktree)) == (34, 17)
    assert hunt_quest_share(at_baseline, ZONE_13) == (43, 71)
    assert hunt_quest_share(at_worktree, ZONE_13) == (46, 74)


@pytest.mark.corpus
def test_the_worst_quest_in_the_zone_is_just_a_row(at_baseline):
    """Quest 1348 asks for 8 items and 1349 asks for 54 kills. Both are printed
    plainly: no threshold separates a demanding quest from a badly tuned one
    without knowing the drop rate and the population, and that is a judgment."""
    rows = {r.quest: r for r in effort_reward(at_baseline, ZONE_13)}

    assert (rows[1348].delivered, rows[1348].tasks) == (8, 1)
    assert (rows[1348].exp, rows[1348].gold) == (900, 90)
    assert (rows[1349].kills, rows[1349].tasks) == (54, 2)


@pytest.mark.corpus
def test_the_redistribution_wave_shows_up_in_the_effort_table(at_baseline, at_worktree):
    """1332 asked for 4 deliveries and paid no items at the baseline; the same
    ask now carries a twelve-row class bag. The effort column did not move."""
    before = {r.quest: r for r in effort_reward(at_baseline, ZONE_13)}[1332]
    after = {r.quest: r for r in effort_reward(at_worktree, ZONE_13)}[1332]

    assert (before.delivered, before.items) == (4, 0)
    assert (after.delivered, after.items) == (4, 12)


@pytest.mark.corpus
def test_the_giver_load_table_shows_one_npc_carrying_the_repeatable_band(at_baseline):
    """Kaimon hands out eleven quests with the same verb, the same target and
    the same level band. That is the repetition, in one row."""
    rows = [r for r in giver_load(at_baseline, ZONE_13)
            if r.giver == "213,1017" and r.task_type == "사냥전달Task"
            and r.target == "죽어가는 아르가스B"]

    assert len(rows) == 1
    assert rows[0].band == "1-5"
    assert len(rows[0].quests) == 11
    assert 1327 in rows[0].quests


@pytest.mark.corpus
def test_no_severity_word_survives_a_real_zone_run(at_worktree):
    """The hermetic contract test runs on four quests. This runs on all 74, with
    Korean section and NPC names in every line."""
    text = "\n".join(all_report_lines(at_worktree, ZONE_13)).upper()

    hits = [word for word in SEVERITY_WORDS if re.search(rf"\b{word}\b", text)]

    assert hits == []
