"""The tuning checks: feasibility, level coherence and reward lane.

Positive oracle for feasibility: quest 1348 asked for 8 delivered items from a
zone holding 10 credit mobs at 90 and 17 percent grant rates. A full clear
yields 6.08. Every id resolved and every rate was a legal number, so
audit_quest_gates called it OK; testers called it the worst quest in the zone.
The corpus tier asserts the ARITHMETIC at the pinned baseline, not a verdict,
and asserts the same quest is silent on the working tree where the patch-002
wave raised the population to 22 and the yield to 12.50.

Negative oracles are always the same shape as their positive: quest 1319 is a
hunt-deliver task with two rated targets that is comfortably feasible, quest
1349 carries one starved and one healthy objective inside a single hunt task,
and quest 1316's group hunt has four times the population it needs.

Count semantics are the trap this file exists to nail down. The three hunt
shapes keep the required count in three different places, and reading the wrong
one is silent rather than loud: it produces a plausible number that is not the
requirement. One fixture per shape proves the check reads the right place by
planting a decoy in the wrong one.
"""

from __future__ import annotations

import pytest

from audit_checks_tuning import (
    DEFAULT_LEVEL_MARGIN,
    check_feasibility,
    check_lane,
    check_level_coherence,
    parse_territory_population,
    task_objectives,
)
from auditlib import Corpus, Scope
from dclib import V92Baseline, parse_quest

# ---------------------------------------------------------------------------
# Fixture builders: the real byte and element shapes, not tidied ones
# ---------------------------------------------------------------------------


def quest_xml(gid: int, hz: int, local: int, tasks: str = "", *, story: str = "",
              qtype: str = "일반", min_level: str = "", max_level: str = "",
              prereqs: tuple[str, ...] = ()) -> str:
    cond = []
    if min_level:
        cond.append(f"      <최소레벨>{min_level}</최소레벨>")
    if max_level:
        cond.append(f"      <최대레벨>{max_level}</최대레벨>")
    if prereqs:
        cond.append("      <선행퀘스트>")
        for ref in prereqs:
            cond.append(f"        <선행퀘스트><퀘스트Id>{ref}</퀘스트Id></선행퀘스트>")
        cond.append("      </선행퀘스트>")
    return (f'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n'
            f'<Quest id="{gid}">\n'
            f"  <Header>\n"
            f"    <Quest번호>{hz},{local}</Quest번호>\n"
            f"    <스토리그룹Id>{story}</스토리그룹Id>\n"
            f"    <퀘스트종류>{qtype}</퀘스트종류>\n"
            f"    <수행조건>\n" + "\n".join(cond) + "\n    </수행조건>\n"
            f"  </Header>\n"
            f"  <Tasks>\n{tasks}  </Tasks>\n</Quest>\n")


def _task(task_id: int, name: str, body: str) -> str:
    return (f'    <Task id="{task_id}">\n'
            f"      <Header><Id>{task_id}</Id><이름>{name}</이름></Header>\n"
            f"      <Body>\n{body}      </Body>\n"
            f"    </Task>\n")


def hunt_task(task_id: int, entries: list[tuple[str, int]]) -> str:
    """사냥Task: the count lives on each 몬스터지정 entry."""
    rows = "".join(
        f"          <몬스터지정><몬스터Id>{ref}</몬스터Id>"
        f"<사냥마리수>{kill}</사냥마리수></몬스터지정>\n"
        for ref, kill in entries)
    return _task(task_id, "사냥Task", f"        <몬스터지정>\n{rows}        </몬스터지정>\n")


def hunt_deliver_task(task_id: int, bags: list[tuple[int, list[tuple[str, int]]]],
                      decoy_kill: str = "") -> str:
    """사냥전달Task: the count lives on the BAG, the rates on the entries.

    decoy_kill plants a 사냥마리수 on the entries, which is where the count does
    NOT live. The corpus never writes one there; the fixture does, so that a
    check reading the wrong field gives a visibly different answer.
    """
    out = ["        <아이템작성>\n"]
    for qty, entries in bags:
        rows = "".join(
            f"              <몬스터지정><몬스터Id>{ref}</몬스터Id>"
            + (f"<사냥마리수>{decoy_kill}</사냥마리수>" if decoy_kill else "")
            + f"<수여확률>{rate}</수여확률></몬스터지정>\n"
            for ref, rate in entries)
        out.append("          <아이템작성>\n"
                   f"            <전달수량>{qty}</전달수량>\n"
                   f"            <몬스터지정>\n{rows}            </몬스터지정>\n"
                   "          </아이템작성>\n")
    out.append("        </아이템작성>\n")
    return _task(task_id, "사냥전달Task", "".join(out))


def group_hunt_task(task_id: int, groups: list[tuple[int, list[str]]]) -> str:
    """그룹사냥Task: the count lives on the GROUP; entries carry none."""
    out = ["        <몬스터그룹>\n"]
    for i, (kills, refs) in enumerate(groups):
        rows = "".join(f"              <몬스터지정><몬스터Id>{ref}</몬스터Id></몬스터지정>\n"
                       for ref in refs)
        out.append("          <몬스터그룹>\n"
                   f"            <그룹이름>@quest:g{i}</그룹이름>\n"
                   f"            <사냥마리수>{kills}</사냥마리수>\n"
                   f"            <몬스터지정>\n{rows}            </몬스터지정>\n"
                   "          </몬스터그룹>\n")
    out.append("        </몬스터그룹>\n")
    return _task(task_id, "그룹사냥Task", "".join(out))


def repeat_task(task_id: int, qty: int, entries: list[tuple[str, int]]) -> str:
    """반복Task: a FLAT bag plus task-level entries carrying the rates."""
    rows = "".join(f"          <몬스터지정><몬스터Id>{ref}</몬스터Id>"
                   f"<수여확률>{rate}</수여확률></몬스터지정>\n" for ref, rate in entries)
    return _task(task_id, "반복Task",
                 f"        <아이템작성><전달수량>{qty}</전달수량></아이템작성>\n"
                 f"        <몬스터지정>\n{rows}        </몬스터지정>\n")


def collect_task(task_id: int, collection_id: int, qty: int) -> str:
    return _task(task_id, "채집Task",
                 f"        <채집물지정><채집물지정><콜렉션Id>{collection_id}</콜렉션Id>"
                 f"</채집물지정></채집물지정>\n"
                 f"        <전달아이템지정><전달아이템지정><아이템Id>9010</아이템Id>"
                 f"<전달수량>{qty}</전달수량></전달아이템지정></전달아이템지정>\n")


def territory_xml(hz: int, rows: list[tuple[int, int, str]],
                  positions: list[str] | None = None) -> str:
    """rows: (npcTemplateId, spawnCount, territory type). One Territory per row."""
    out = [f'<?xml version="1.0" encoding="utf-8"?>', f'<TerritoryData huntingZoneId="{hz}">',
           '  <TerritoryGroup id="1" desc="g">', "    <TerritoryList>"]
    for i, (template, count, kind) in enumerate(rows):
        pos = (positions or [])[i] if positions and i < len(positions) else "0,0,0"
        out.append(f'      <Territory id="{100 + i}" desc="t{i}" type="{kind}">')
        out.append(f'        <Npc npcTemplateId="{template}" spawnCount="{count}" pos="{pos}" />')
        out.append("      </Territory>")
    out += ["    </TerritoryList>", "  </TerritoryGroup>", "</TerritoryData>"]
    return "\n".join(out) + "\n"


def npc_xml(hz: int, templates: dict[int, str]) -> str:
    rows = "".join(f'  <Template id="{tid}" name="{name}" />\n'
                   for tid, name in sorted(templates.items()))
    return (f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<NpcData huntingZoneId="{hz}">\n{rows}</NpcData>\n')


def comp_xml(rows: list[tuple[int, str, str, list[int]]]) -> str:
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


def collection_territory_xml(hz: int, type_id: int, spawns: int) -> str:
    rows = "".join(f'      <Spawn pos="{i},0,0" dir="0"/>\n' for i in range(spawns))
    return (f'<?xml version="1.0" encoding="utf-8" ?>\n'
            f'<CollectionTerritory id="1" continentId="{hz}" areaName="X_P">\n'
            f'  <Territory id="1" desc="t">\n'
            f'    <Collections id="1" desc="c" typeId="{type_id}" spawnNum="{spawns}">\n'
            f"{rows}"
            f"    </Collections>\n  </Territory>\n</CollectionTerritory>\n")


ITEMS = """<?xml version="1.0" encoding="utf-8"?>
<ItemData>
  <Item id="15021" name="mail17_feet" requiredLevel="7" combatItemType="EQUIP_ARMOR_LEG" combatItemSubType="feetmail" linkLookInfoId="313007" />
  <Item id="10009" name="dual_01" requiredLevel="2" combatItemType="EQUIP_WEAPON" combatItemSubType="dual" linkLookInfoId="0" />
  <Item id="160" name="recall_scroll2" requiredLevel="1" combatItemType="DISPOSAL" combatItemSubType="magical" linkLookInfoId="0" />
  <Item id="9010" name="quest_material" combatItemType="ETC" combatItemSubType="etc" linkLookInfoId="0" />
</ItemData>
"""


def build(corpus_dir, files: dict[str, str], zones=(13,), new=None) -> tuple[Corpus, Scope]:
    tree = {"ItemTemplate.xml": ITEMS}
    tree.update(files)
    root = corpus_dir(tree)
    corpus = Corpus(root, V92Baseline(root))
    return corpus, Scope(zones=set(zones) if zones else None, new_quests=new)


# ---------------------------------------------------------------------------
# feasibility: count semantics, one fixture per hunt shape (mandatory)
# ---------------------------------------------------------------------------

def test_hunt_task_count_is_per_monster_entry(corpus_dir):
    """사냥Task keeps the count on EACH 몬스터지정, so entries are independent.

    The fixture asks for 3 of one target and 30 of another, both with a
    population of 10. Reading a single task-wide count, from the first entry or
    from a bag, would either report nothing at all or report the wrong target.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001349.quest": quest_xml(1349, 13, 49, hunt_task(1, [("13,101", 3), ("13,102", 30)])),
        "NpcData_13.xml": npc_xml(13, {101: "a", 102: "b"}),
        "TerritoryData_13.xml": territory_xml(13, [(101, 10, "normal"), (102, 10, "normal")]),
    })

    findings = [f for f in check_feasibility(corpus, scope) if f.severity == "medium"]

    assert [f.key for f in findings] == ["feasibility:quest-1349:t1:m13,102"]
    assert findings[0].evidence["required"] == 30
    assert findings[0].evidence["expected_yield"] == 10.0
    # The healthy entry sharing the task is the negative half of the proof.
    assert 10.0 >= 3


def test_hunt_deliver_count_is_per_bag_not_per_entry(corpus_dir):
    """사냥전달Task keeps the count on the BAG. Entries hold only the rates.

    The fixture plants a decoy 사냥마리수 of 2 on the entries, where the count
    does not live. A check reading that field would compare 2 against a 5.00
    yield and stay silent about a quest that cannot be finished.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001348.quest": quest_xml(
            1348, 13, 48, hunt_deliver_task(1, [(8, [("13,302", 100)])], decoy_kill="2")),
        "NpcData_13.xml": npc_xml(13, {302: "spirit"}),
        "TerritoryData_13.xml": territory_xml(13, [(302, 5, "normal")]),
    })
    model = parse_quest(corpus.read("QuestData/001348.quest"))
    decoy = {kill for _ref, kill, _rate in model["tasks"][1]["bags"][0]["monsters"]}

    findings = [f for f in check_feasibility(corpus, scope) if f.severity == "medium"]

    assert decoy == {"2"}, "the wrong source must be present for the proof to mean anything"
    assert len(findings) == 1
    assert findings[0].evidence["required"] == 8, "the bag, not the entry"
    assert findings[0].evidence["expected_yield"] == 5.0
    assert 5.0 >= 2, "reading the entry count would have reported nothing"


def test_hunt_deliver_applies_the_grant_rate_per_entry(corpus_dir):
    """수여확률 is per entry and always present on this shape.

    Ignoring it turns 1348's 6.08 into 10 and the check into a no-op.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001348.quest": quest_xml(
            1348, 13, 48, hunt_deliver_task(1, [(8, [("13,302", 90), ("13,303", 17)])])),
        "NpcData_13.xml": npc_xml(13, {302: "a", 303: "b"}),
        "TerritoryData_13.xml": territory_xml(13, [(302, 6, "normal"), (303, 4, "normal")]),
    })

    findings = [f for f in check_feasibility(corpus, scope) if f.severity == "medium"]

    assert findings[0].evidence["expected_yield"] == 6.08
    assert findings[0].evidence["required"] == 8
    assert "at 90%" in findings[0].message and "at 17%" in findings[0].message


def test_group_hunt_count_is_per_group(corpus_dir):
    """그룹사냥Task keeps the count on the GROUP; entries are alternative credit.

    Both groups here have a population of 20. Only the group asking for 40 is
    short, and a reader taking a per-entry count would find none at all: the
    corpus writes no 사냥마리수 on a group entry anywhere.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001316.quest": quest_xml(1316, 13, 16, group_hunt_task(
            1, [(5, ["13,8", "13,9"]), (40, ["13,8", "13,9"])])),
        "NpcData_13.xml": npc_xml(13, {8: "a", 9: "b"}),
        "TerritoryData_13.xml": territory_xml(13, [(8, 12, "normal"), (9, 8, "normal")]),
    })
    model = parse_quest(corpus.read("QuestData/001316.quest"))
    entries = model["tasks"][1]["groups"][0]["monsters"]
    objectives = task_objectives(model["tasks"][1])

    findings = [f for f in check_feasibility(corpus, scope) if f.severity == "medium"]

    assert {kill for _ref, kill, _rate in entries} == {""}, "group entries carry no count"
    assert [o.required for o in objectives] == [5, 40]
    assert [f.key for f in findings] == ["feasibility:quest-1316:t1:g1"]
    assert findings[0].evidence["expected_yield"] == 20.0


def test_repeat_tasks_are_out_of_scope_for_the_verdict(corpus_dir):
    """A 반복Task is built to be run again, so one clear's worth is not the bar.

    313 of the corpus's 317 repeat tasks carry a flat bag plus rated entries,
    and firing on all of them would drown the check. They stay in scope for
    data errors, which the next test covers.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001334.quest": quest_xml(1334, 13, 34, repeat_task(1, 40, [("13,101", 50)])),
        "NpcData_13.xml": npc_xml(13, {101: "a"}),
        "TerritoryData_13.xml": territory_xml(13, [(101, 4, "normal")]),
    })

    assert check_feasibility(corpus, scope) == []


def test_a_dangling_target_is_a_data_error_not_a_crash(corpus_dir):
    """69 hunt-target references dangle corpus-wide, including all of NpcData_445.

    Treating an unresolvable target as a population of zero would report
    starvation for a quest whose real problem is a broken reference, and the
    remedy for the two is not the same.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001334.quest": quest_xml(1334, 13, 34, repeat_task(1, 5, [("13,7001", 50)])),
        "QuestData/001349.quest": quest_xml(1349, 13, 49, hunt_task(1, [("13,7001", 5)])),
        "NpcData_13.xml": npc_xml(13, {101: "a"}),
        "TerritoryData_13.xml": territory_xml(13, [(101, 4, "normal")]),
    })

    findings = check_feasibility(corpus, scope)

    assert sorted(f.key for f in findings) == [
        "feasibility:quest-1334:t1:target:13,7001",
        "feasibility:quest-1349:t1:target:13,7001",
    ]
    assert all(f.evidence["status"] == "dangling" for f in findings)


def test_a_task_whose_body_contradicts_its_label_is_a_parse_finding(corpus_dir):
    """Never guess an objective from a label.

    A 사냥Task with no 몬스터지정 does not do what its name says. Reading it as
    a hunt with zero targets would bury the data error inside a tuning verdict.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001349.quest": quest_xml(
            1349, 13, 49, _task(1, "사냥Task", "        <저널Text>x</저널Text>\n")),
        "NpcData_13.xml": npc_xml(13, {101: "a"}),
        "TerritoryData_13.xml": territory_xml(13, [(101, 4, "normal")]),
    })

    findings = check_feasibility(corpus, scope)

    assert [f.key for f in findings] == ["feasibility:quest-1349:t1:body"]
    assert findings[0].evidence["missing"] == "몬스터지정"


# ---------------------------------------------------------------------------
# feasibility: the population model
# ---------------------------------------------------------------------------

def test_availability_sums_spawncount_never_row_count(corpus_dir):
    """A Territory row is one <Npc> element; spawnCount is how many it places.

    Counting rows is the failure mode dclib.territory_spawns invites: at the
    working tree, zone-13 templates 302 and 303 are 14 rows but 22 spawns, and
    a row count would report a famine that does not exist.
    """
    text = territory_xml(13, [(302, 6, "normal"), (302, 6, "normal"), (303, 10, "normal")])

    census = parse_territory_population(text)

    assert census[302] == {"normal": 12}, "two rows, twelve spawns"
    assert census[303] == {"normal": 10}


def test_nearby_groups_are_not_deduplicated_by_coordinate(corpus_dir):
    """Groups 1300022 and 1300060 sit about 11 units apart and both spawn.

    Collapsing near-identical positions would halve the real population, which
    is precisely the direction that manufactures a false starvation report.
    """
    text = territory_xml(
        13, [(302, 6, "normal"), (302, 6, "normal")],
        positions=["84726.36,-83623.64,-4694.40", "84730.11,-83633.02,-4694.40"])

    assert parse_territory_population(text)[302] == {"normal": 12}


def test_conditional_and_event_population_get_their_own_columns(corpus_dir):
    """quest and event territories are reported, never silently filtered.

    A quest-conditional territory is frequently the exactly-right population,
    because the condition is the audited quest itself. An event territory needs
    its FieldEvent live (zone 64's Christmas tree holds 24 spawns). Both are
    counted toward the verdict and both are named in the evidence, so a reader
    can see which half of the population is conditional.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001349.quest": quest_xml(1349, 13, 49, hunt_task(1, [("13,101", 8)])),
        "NpcData_13.xml": npc_xml(13, {101: "a"}),
        "TerritoryData_13.xml": territory_xml(
            13, [(101, 2, "normal"), (101, 5, "quest"), (101, 4, "event")]),
    })

    findings = check_feasibility(corpus, scope)

    assert [f.severity for f in findings] == ["info"]
    target = findings[0].evidence["targets"][0]
    assert (target["standing"], target["conditional"], target["event"]) == (2, 5, 4)
    assert findings[0].evidence["expected_yield"] == 11.0
    assert findings[0].evidence["expected_yield_standing"] == 2.0
    assert "conditional and event" in findings[0].message


def test_a_dungeon_continent_target_is_not_evaluable_rather_than_starved(corpus_dir):
    """Dungeon mobs come from event scripts, not from standing territories.

    Quests 48921 and 48923 point at zone 3003 and its census shows zero. That
    is what a dungeon looks like from the outside, not a broken quest.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/048921.quest": quest_xml(
            48921, 489, 21, hunt_deliver_task(1, [(8, [("3003,3603", 100)])])),
        "DungeonData_3003.xml": '<?xml version="1.0" encoding="utf-8"?>\n<DungeonData id="3003" />\n',
        "NpcData_3003.xml": npc_xml(3003, {3603: "boss"}),
        "TerritoryData_3003.xml": territory_xml(3003, []),
    }, zones=(489,))

    findings = check_feasibility(corpus, scope)

    assert [f.severity for f in findings] == ["info"]
    assert "dungeon continent" in findings[0].message


def test_a_healthy_hunt_deliver_task_stays_silent(corpus_dir):
    """The negative oracle for the headline shape.

    Quest 1319's real numbers at the baseline: 5 required, 10 mobs at 85 percent
    plus 7 at 12 percent, expected yield 9.34. A check that fires here fires on
    most of the game.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001319.quest": quest_xml(
            1319, 13, 19, hunt_deliver_task(1, [(5, [("13,300944", 85), ("13,300941", 12)])])),
        "NpcData_13.xml": npc_xml(13, {300944: "a", 300941: "b"}),
        "TerritoryData_13.xml": territory_xml(13, [(300944, 10, "normal"), (300941, 7, "normal")]),
    })

    assert check_feasibility(corpus, scope) == []


def test_collect_tasks_count_nodes_from_collectionterritory(corpus_dir):
    """채집Task counts gather nodes, and its count lives on the deliver bag.

    Availability is the MAXIMUM across a zone's CollectionTerritory files, not
    the sum: zone 13 ships an ordinary and a "Death" phase holding the same 20
    nodes, and a player stands in one at a time.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001336.quest": quest_xml(1336, 13, 36, collect_task(1, 409, 30)),
        "CollectionData/CollectionTerritory_13_ATW_P.xml": collection_territory_xml(13, 409, 24),
        "CollectionData/CollectionTerritory_13_ATW_Death_P.xml": collection_territory_xml(13, 409, 24),
    })

    findings = check_feasibility(corpus, scope)

    assert [f.severity for f in findings] == ["medium"]
    assert findings[0].evidence["nodes"] == 24, "the max across phases, not 48"
    assert findings[0].evidence["required"] == 30


def test_a_collection_that_spawns_off_zone_is_not_starvation(corpus_dir):
    """Quest 48922 sits in zone 489 and collection 567 spawns only in 9123.

    A collect objective never names the map it is farmed on, so the quest's own
    zone is the only assumption available, and it is sometimes wrong. Calling
    that starvation would be a lie about content that exists.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/048922.quest": quest_xml(48922, 489, 22, collect_task(1, 567, 3)),
        "CollectionData/CollectionTerritory_9123_EX_P.xml": collection_territory_xml(9123, 567, 12),
    }, zones=(489,))

    findings = check_feasibility(corpus, scope)

    assert [f.severity for f in findings] == ["info"]
    assert "farmed off-zone" in findings[0].message
    assert findings[0].evidence["files"][0]["continentId"] == 9123


def test_subject_scope_limits_reporting_but_not_evidence(corpus_dir):
    """Spawns for a zone-13 target are read even when zone 13 is not the subject."""
    corpus, scope = build(corpus_dir, {
        "QuestData/006401.quest": quest_xml(6401, 64, 1, hunt_task(1, [("13,101", 40)])),
        "QuestData/001349.quest": quest_xml(1349, 13, 49, hunt_task(1, [("13,101", 40)])),
        "NpcData_13.xml": npc_xml(13, {101: "a"}),
        "TerritoryData_13.xml": territory_xml(13, [(101, 10, "normal")]),
    }, zones=(64,))

    findings = check_feasibility(corpus, scope)

    assert [f.evidence["quest"] for f in findings] == [6401]
    assert findings[0].evidence["expected_yield"] == 10.0, "evidence still reached zone 13"


# ---------------------------------------------------------------------------
# level-coherence
# ---------------------------------------------------------------------------

def test_an_item_gated_far_above_its_quest_fires(corpus_dir):
    """Condition (a): item 15021 needs level 7 and quest 1326 gates at 5.

    Island of Dawn grants ahead on purpose, so the margin exists; the fixture
    uses a gap of 6 to sit well clear of it.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001326.quest": quest_xml(1326, 13, 26, min_level="1"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1326, "800", "80", [15021])]),
    })

    findings = check_level_coherence(corpus, scope)

    assert [f.key for f in findings] == ["level-coherence:quest-1326:item:15021"]
    assert findings[0].evidence["gap"] == 6
    assert findings[0].evidence["margin"] == DEFAULT_LEVEL_MARGIN


def test_granting_within_the_margin_is_deliberate_design(corpus_dir):
    """Negative oracle for (a): 42 of the baseline's grants sit 1 or 2 ahead.

    Quest 1305 hands out level-7 gear at a level-5 gate. A margin below 2 turns
    the zone's own design into a wall of findings.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001305.quest": quest_xml(1305, 13, 5, min_level="5"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1305, "800", "80", [15021])]),
    })

    assert check_level_coherence(corpus, scope) == []


def test_a_non_equipment_reward_is_never_a_level_finding(corpus_dir):
    """combatItemType.startswith("EQUIP") also matches ~4,100 cosmetics.

    Only the allow-list counts, so a consumable with no requiredLevel of its own
    cannot produce a gap.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001326.quest": quest_xml(1326, 13, 26, min_level="1"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1326, "800", "80", [160])]),
    })

    assert check_level_coherence(corpus, scope) == []


def test_a_prerequisite_gated_above_its_dependent_fires(corpus_dir):
    """Condition (b), the Chione case: 1336 gates at 7 behind 1335, which gates at 8."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001335.quest": quest_xml(1335, 13, 35, min_level="8"),
        "QuestData/001336.quest": quest_xml(1336, 13, 36, min_level="7", prereqs=("13,35",)),
    })

    findings = check_level_coherence(corpus, scope)

    assert [f.key for f in findings] == ["level-coherence:quest-1336:prereq:1335"]
    assert findings[0].evidence["prereq_min_level"] == 8


@pytest.mark.parametrize("sentinel", ["99,99", "99,9999", "999,99"])
def test_disable_sentinels_are_not_level_inversions(sentinel, corpus_dir):
    """THREE encodings, not the two dclib.SENTINEL_PREREQS lists.

    99,99 and 99,9999 dangle, but 999,99 resolves to a real placeholder quest
    gated at level 99, so a name-based skip misses it and reports a level
    inversion on all 122 quests that use it. The rule here is the level itself:
    a prerequisite you can never reach is a sentinel however it is spelled.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/009999.quest": quest_xml(9999, 99, 99, min_level="99", max_level="99"),
        "QuestData/099999.quest": quest_xml(99999, 999, 99, min_level="99", max_level="99"),
        "QuestData/001318.quest": quest_xml(1318, 13, 18, min_level="2", prereqs=(sentinel,)),
    })

    assert check_level_coherence(corpus, scope) == []


def test_a_max_level_below_its_prerequisite_chain_fires(corpus_dir):
    """Condition (c). No instance exists in EITHER real snapshot.

    Measured at the pinned baseline and on the working tree: zero quests
    corpus-wide have a 최대레벨 below the highest 최소레벨 on the way to them,
    once the disable sentinels are excluded. The condition is real and cheap to
    compute, so it is pinned here structurally rather than dropped.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001301.quest": quest_xml(1301, 13, 1, min_level="12"),
        "QuestData/001302.quest": quest_xml(1302, 13, 2, min_level="5", prereqs=("13,1",)),
        "QuestData/001303.quest": quest_xml(1303, 13, 3, min_level="5", max_level="9",
                                            prereqs=("13,2",)),
    })

    findings = [f for f in check_level_coherence(corpus, scope) if f.detail == "max-level"]

    assert [f.key for f in findings] == ["level-coherence:quest-1303:max-level"]
    assert findings[0].evidence["chain_max_min_level"] == 12, "reached through 1302"


def test_a_prerequisite_cycle_does_not_recurse_forever(corpus_dir):
    """The corpus is not proven acyclic and a chain walk must survive one."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001301.quest": quest_xml(1301, 13, 1, min_level="5", max_level="9",
                                            prereqs=("13,2",)),
        "QuestData/001302.quest": quest_xml(1302, 13, 2, min_level="5", prereqs=("13,1",)),
    })

    assert check_level_coherence(corpus, scope) == []


# ---------------------------------------------------------------------------
# lane
# ---------------------------------------------------------------------------

def test_a_story_quest_granting_equipment_fires(corpus_dir):
    """Story quest 1305 paid out the whole level-7 First Expedition set."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001305.quest": quest_xml(1305, 13, 5, story="1", qtype="미션"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1305, "800", "80", [15021])]),
    })

    findings = check_lane(corpus, scope)

    assert [f.key for f in findings] == ["lane:quest-1305:item:15021"]
    assert findings[0].evidence["combat_type"] == "EQUIP_ARMOR_LEG"


def test_story_membership_is_the_group_id_not_the_quest_type(corpus_dir):
    """중요미션 is a story type too: 37 of the corpus's 327 story quests.

    Testing 퀘스트종류 = 미션 alone misses every one of them, which is why the
    test is a non-empty 스토리그룹Id.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001316.quest": quest_xml(1316, 13, 16, story="2", qtype="중요미션"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1316, "800", "80", [10009])]),
    })

    findings = check_lane(corpus, scope)

    assert [f.key for f in findings] == ["lane:quest-1316:item:10009"]
    assert findings[0].evidence["quest_type"] == "중요미션"


def test_a_zone_quest_granting_equipment_is_the_intended_lane(corpus_dir):
    """The negative oracle: an empty 스토리그룹Id is where gear belongs."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001323.quest": quest_xml(1323, 13, 23, story="", qtype="일반"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1323, "800", "80", [10009])]),
    })

    assert check_lane(corpus, scope) == []


def test_a_story_quest_granting_a_consumable_stays_silent(corpus_dir):
    """Story quests may pay exp, gold and consumables. Only gear crosses lanes."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001301.quest": quest_xml(1301, 13, 1, story="1", qtype="미션"),
        "CompensationData/QuestCompensationData_13.xml": comp_xml([(1301, "800", "80", [160])]),
    })

    assert check_lane(corpus, scope) == []


# ---------------------------------------------------------------------------
# Corpus tier: the real defects at the pinned baseline
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def at_baseline(datasheet_dir, baseline):
    return Corpus(datasheet_dir, baseline, use_baseline=True)


@pytest.fixture(scope="session")
def at_worktree(datasheet_dir):
    return Corpus(datasheet_dir, V92Baseline(datasheet_dir), use_baseline=False)


ZONE_13 = Scope(zones={13}, new_quests=None)
CORPUS_WIDE = Scope(zones=None, new_quests=None)


@pytest.mark.corpus
def test_quest_1348_arithmetic_at_the_baseline(at_baseline):
    """The headline oracle, asserted as arithmetic rather than as a verdict.

    Measured at 789fec28: the bag requires 8; targets 13,302 and 13,303 carry
    grant rates of 90 and 17 percent; TerritoryData_13 places 6 and 4 of them,
    all on standing territories. 6*0.90 + 4*0.17 = 6.08 against a required 8.

    The plan that commissioned this check quoted 302+303 = 22, which is the
    POST-fix working-tree figure, not the baseline one.
    """
    findings = [f for f in check_feasibility(at_baseline, ZONE_13)
                if f.evidence.get("quest") == 1348]

    assert [f.key for f in findings] == ["feasibility:quest-1348:t1:bag0"]
    finding = findings[0]
    assert finding.severity == "medium"
    assert finding.evidence["required"] == 8
    assert finding.evidence["expected_yield"] == 6.08
    assert finding.evidence["expected_yield_standing"] == 6.08
    assert [(t["target"], t["standing"], t["total"]) for t in finding.evidence["targets"]] == [
        ("13,302", 6, 6), ("13,303", 4, 4),
    ]
    assert "widen the accept list or raise the spawn count" in finding.message


@pytest.mark.corpus
def test_quest_1348_is_silent_on_the_working_tree(at_worktree):
    """The patch-002 wave raised 302+303 from 10 to 22, so the yield is 12.50.

    Fire-then-quiet is the whole assertion: a check that only fires proves
    nothing about whether it can be satisfied.
    """
    findings = [f for f in check_feasibility(at_worktree, ZONE_13)
                if f.evidence.get("quest") == 1348]

    assert findings == []


@pytest.mark.corpus
def test_the_healthy_hunt_deliver_quests_of_zone_13_stay_silent(at_baseline):
    """Negative oracle of the same shape, from the same zone and snapshot.

    1319 (5 required, yield 9.34) and 1325 (5 required, yield 23.40) are
    hunt-deliver tasks with rated targets that are comfortably feasible.
    """
    reported = {f.evidence.get("quest") for f in check_feasibility(at_baseline, ZONE_13)}

    assert 1319 not in reported
    assert 1325 not in reported


@pytest.mark.corpus
def test_quest_1349_is_starved_and_healthy_in_the_same_hunt_task(at_baseline):
    """The per-entry count semantics, proven on real data.

    Task 1 asks for 48 of template 13,4 (20 spawned) and 6 of 13,5 (8 spawned).
    A shared count would report both entries or neither.
    """
    findings = [f for f in check_feasibility(at_baseline, ZONE_13)
                if f.evidence.get("quest") == 1349]

    assert [f.key for f in findings] == ["feasibility:quest-1349:t1:m13,4"]
    assert findings[0].evidence["required"] == 48
    assert findings[0].evidence["expected_yield"] == 20.0


@pytest.mark.corpus
def test_the_zone_13_group_hunt_is_not_reported(at_baseline):
    """Negative oracle for the group shape: 1316 needs 8 and the zone holds 31."""
    findings = [f for f in check_feasibility(at_baseline, ZONE_13)
                if f.evidence.get("quest") == 1316]

    assert findings == []


@pytest.mark.corpus
def test_a_real_group_hunt_shortfall_is_reported(at_baseline):
    """Positive oracle for the group shape, from outside Island of Dawn.

    Quest 999611 asks for 100 kills across three templates in zone 27 that are
    spawned 21 + 12 + 13 = 46 times.
    """
    findings = [f for f in check_feasibility(at_baseline, Scope(zones={9996}, new_quests=None))
                if f.evidence.get("quest") == 999611]

    assert [f.key for f in findings] == ["feasibility:quest-999611:t1:g0"]
    assert findings[0].evidence["required"] == 100
    assert findings[0].evidence["expected_yield"] == 46.0


@pytest.mark.corpus
def test_every_dangling_hunt_target_degrades_instead_of_crashing(at_baseline):
    """69 hunt-target references dangle corpus-wide at the pinned baseline.

    The count is a legitimate assertion because the ref is pinned. What matters
    is that the sweep completes: a dangling target must never reach the
    arithmetic, where it would read as a population of zero.
    """
    findings = [f for f in check_feasibility(at_baseline, CORPUS_WIDE)
                if f.evidence.get("status") == "dangling"]

    assert len(findings) == 69
    assert {"13,7001", "445,200"} <= {f.evidence["target"] for f in findings}


@pytest.mark.corpus
def test_dungeon_continent_targets_are_annotated_not_starved(at_baseline):
    """Quests 48921 and 48923 point into zone 3003, whose census reads zero."""
    findings = [f for f in check_feasibility(at_baseline, Scope(zones={489}, new_quests=None))
                if f.evidence.get("quest") in (48921, 48923)]

    assert {f.severity for f in findings} == {"info"}
    assert all("dungeon continent" in f.message for f in findings)


@pytest.mark.corpus
def test_event_territory_population_is_reported_in_its_own_column(at_baseline):
    """Event territories need their FieldEvent live, so they are flagged.

    Quest 50512 task 21 has no standing population for target 833,1240 at all:
    its single spawn sits on an event territory.
    """
    findings = [f for f in check_feasibility(at_baseline, Scope(zones={505}, new_quests=None))
                if f.evidence.get("quest") == 50512
                and any(t.get("event") for t in f.evidence.get("targets", []))]

    assert [f.severity for f in findings] == ["info"]
    assert findings[0].evidence["expected_yield_standing"] == 0.0
    assert findings[0].evidence["expected_yield"] == 1.0


@pytest.mark.corpus
def test_the_chione_level_inversion_fires_at_the_baseline(at_baseline):
    """1336 and 1337 gate at 7 behind 1335, which gates at 8.

    Still true on the working tree: the trimming wave did not touch it, so this
    check has no fire-then-quiet half and says so rather than faking one.
    """
    findings = [f for f in check_level_coherence(at_baseline, ZONE_13)
                if f.detail.startswith("prereq:")]

    assert sorted(f.key for f in findings) == [
        "level-coherence:quest-1336:prereq:1335",
        "level-coherence:quest-1337:prereq:1335",
    ]
    assert {f.evidence["prereq_min_level"] for f in findings} == {8}
    assert {f.evidence["quest_min_level"] for f in findings} == {7}


@pytest.mark.corpus
def test_the_third_disable_sentinel_does_not_manufacture_inversions(at_baseline):
    """999,99 resolves to placeholder quest 99999, gated at level 99.

    122 prerequisite references use it. Skipping only the two encodings
    dclib.SENTINEL_PREREQS lists leaves 8 real inversions buried under 114
    fabricated ones, so the corpus-wide count is the assertion.
    """
    findings = [f for f in check_level_coherence(at_baseline, CORPUS_WIDE)
                if f.detail.startswith("prereq:")]

    assert len(findings) == 8
    assert all(f.evidence["prereq_min_level"] < 99 for f in findings)


@pytest.mark.corpus
def test_no_quest_in_the_corpus_has_a_max_level_below_its_chain(at_baseline):
    """Condition (c) has no oracle in either snapshot, and this records why.

    Zero instances corpus-wide at the pinned baseline once the disable sentinels
    are excluded. The hermetic fixture above pins the structure instead. If this
    ever fails, a real instance has appeared and it should become the oracle.
    """
    findings = [f for f in check_level_coherence(at_baseline, CORPUS_WIDE)
                if f.detail == "max-level"]

    assert findings == []


@pytest.mark.corpus
def test_the_level_margin_keeps_deliberate_grant_ahead_quiet(at_baseline):
    """Island of Dawn grants 1 and 2 levels ahead on purpose, 42 times.

    At the default margin only the three level-12 weapons of quest 1316 clear
    it, from a quest gated at 9. Dropping the margin to 1 reports 42 grants and
    the check stops being readable.
    """
    at_default = [f for f in check_level_coherence(at_baseline, ZONE_13)
                  if f.detail.startswith("item:")]
    at_one = [f for f in check_level_coherence(at_baseline, ZONE_13, margin=1)
              if f.detail.startswith("item:")]

    assert {f.evidence["quest"] for f in at_default} == {1316}
    assert {f.evidence["gap"] for f in at_default} == {3}
    assert len(at_one) == 42


@pytest.mark.corpus
def test_the_story_lane_leak_fires_at_the_baseline(at_baseline):
    """Story quest 1305 granted the entire level-7 First Expedition set.

    21 equipment rows in one payout, alongside six other story quests in the
    zone that also carried gear.
    """
    findings = [f for f in check_lane(at_baseline, ZONE_13)]
    per_quest = {}
    for f in findings:
        per_quest.setdefault(f.evidence["quest"], []).append(f)

    assert len(per_quest[1305]) == 21
    assert sorted(per_quest) == [1303, 1304, 1305, 1315, 1316, 1317, 1331]


@pytest.mark.corpus
def test_the_story_lane_is_almost_clean_on_the_working_tree(at_worktree):
    """The wave moved gear off the story quests it could move it off.

    1316 and 1317 still carry it by design (the zone's final story beats), and
    that is what the waiver file is for; 1303, 1304, 1305, 1315 and 1331 went
    quiet, which is the fire-then-quiet half.
    """
    reported = {f.evidence["quest"] for f in check_lane(at_worktree, ZONE_13)}

    assert reported == {1316, 1317}


@pytest.mark.corpus
def test_a_full_corpus_sweep_completes_without_raising(at_baseline):
    """2,707 quests, 194 referenced zones, every malformed shape the corpus has.

    The check runs after every patch apply, so a crash on one bad file would
    take the whole gate down.
    """
    findings = check_feasibility(at_baseline, CORPUS_WIDE)

    assert all(f.severity in ("medium", "info") for f in findings)
    assert any(f.evidence.get("quest") == 1348 for f in findings)
