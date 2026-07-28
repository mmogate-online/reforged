"""The graph integrity checks: references, hidden gates and client parity.

Positive oracles, all measured at the pinned baseline rather than quoted:

  references     13 sentinel-disabled quests carry 19 live inbound references
                 corpus-wide. Quest 59901 is referenced by five different
                 families at once, quest 244 by a dungeon event, and quest 201
                 by an in-progress gate that is invisible unless 진행퀘스트 is
                 read in the right encoding.
  hidden-gates   quests 1326 and 1330 gate on 진행퀘스트 = 1305,1 while granting
                 three set pieces each, so finishing 1305 first stranded them.
  client-parity  17 zone-13 rows disagreed with the client shard and one client
                 row had no server counterpart. Zone 213 has 10 rows on both
                 sides and no sync-config pair at all.

Negative oracles, equally measured:

  references     zone 13 is silent at BOTH snapshots even though the patch-002
                 wave disabled five more quests there. That is the check working
                 exactly as intended: the wave rewired 1324 off 1323 before
                 retiring it. The fire-then-quiet shape does not apply, because
                 the incident this check exists for was AVOIDED rather than
                 committed, so the 1323/1324 defect is pinned hermetically and
                 the real snapshots supply the before-and-after of the rewire.
  hidden-gates   34 quests carry an in-progress gate and grant no equipment.
                 They stay at medium at both snapshots: the gate alone is a
                 legitimate escort and timing idiom.
  client-parity  the same zone-13 comparison is completely clean on the working
                 tree, where the sync landed.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import audit_checks_graph as graph
from audit_checks_graph import (
    ACHIEVEMENT_ITEM_TEMPLATE,
    ACHIEVEMENT_QUEST_TEMPLATE,
    GLOBAL_HEAD,
    GLOBAL_LIST,
    PAIR,
    Edge,
    check_client_parity,
    check_hidden_gates,
    check_references,
    in_progress_gates,
    inbound_map,
    quest_ids,
    reference_edges,
    synced_zones,
)
from auditlib import Corpus, Scope
from dclib import SENTINEL_PREREQS, V92Baseline, load_item_model, parse_quest, strip_ns

# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

ITEMS = """<?xml version="1.0" encoding="utf-8"?>
<ItemData>
  <Item id="15021" name="mail17_feet" combatItemType="EQUIP_ARMOR_LEG" combatItemSubType="feetMail" linkLookInfoId="313007" requiredLevel="7" />
  <Item id="15024" name="leather17_feet" combatItemType="EQUIP_ARMOR_LEG" combatItemSubType="feetLeather" linkLookInfoId="213007" requiredLevel="7" />
  <Item id="88888" name="party_hat" combatItemType="EQUIP_COSTUME" combatItemSubType="costume" linkLookInfoId="0" />
</ItemData>
"""


def quest_xml(gid: int, hz: int, local: int, *, prereqs: tuple[str, ...] = (),
              link: str = "1,1", in_progress: tuple[str, ...] = (),
              visit_npcs: tuple[str, ...] = ()) -> str:
    prereq_block = ""
    if prereqs:
        rows = "".join(
            f"<선행퀘스트><퀘스트Id>{p}</퀘스트Id></선행퀘스트>" for p in prereqs)
        prereq_block = f"<선행퀘스트>{rows}</선행퀘스트>"
    gates = "".join(f"<진행퀘스트>{g}</진행퀘스트>" for g in in_progress)
    tasks = ""
    if visit_npcs:
        rows = "".join(f"<방문그룹><NPCId>{n}</NPCId></방문그룹>" for n in visit_npcs)
        tasks = ('<Task id="1"><Header><이름>방문Task</이름></Header>'
                 f"<Body><방문그룹>{rows}</방문그룹></Body></Task>")
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<Quest id="{gid}">\n'
        "  <Header>\n"
        f"    <Quest번호>{hz},{local}</Quest번호>\n"
        f"    <연결퀘스트>{link}</연결퀘스트>\n"
        f"    <수행조건><최소레벨>1</최소레벨>{prereq_block}{gates}</수행조건>\n"
        "  </Header>\n"
        f"  <Tasks>{tasks}</Tasks>\n"
        "</Quest>\n"
    )


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


DISABLED = quest_xml(5001, 50, 1, prereqs=("99,99",))


def build(corpus_dir, files: dict[str, str], zones=(50,), new=None) -> tuple[Corpus, Scope]:
    tree = {"ItemTemplate.xml": ITEMS}
    tree.update(files)
    root = corpus_dir(tree)
    corpus = Corpus(root, V92Baseline(root))
    return corpus, Scope(zones=set(zones) if zones else None, new_quests=new)


# ---------------------------------------------------------------------------
# The two id encodings
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,form,expected", [
    ("13,46", PAIR, {1346}),            # 선행퀘스트 and 연결퀘스트
    ("03,01", PAIR, {301}),             # zero padded halves are common
    ("1305,1", GLOBAL_HEAD, {1305}),    # 진행퀘스트: questId then taskId
    ("201,12", GLOBAL_HEAD, {201}),
    ("1346", GLOBAL_LIST, {1346}),      # every non-quest family
    ("41501,41502", GLOBAL_LIST, {41501, 41502}),
    ("", PAIR, set()),
    ("0", GLOBAL_LIST, {0}),
    ("abc", PAIR, set()),
    ("13,", PAIR, set()),
    ("1,2,3", PAIR, set()),             # a pair family cannot read a triple
])
def test_quest_id_encodings(value, form, expected):
    assert quest_ids(value, form) == expected


def test_the_same_text_means_two_different_quests_under_two_families():
    """This is the whole trap in one assertion.

    "1305,1" is the same shape as "13,46" and means something else entirely.
    Reading 진행퀘스트 as a pair resolves it to quest 130501, which does not
    exist, so the family silently contributes no edges at all and every gate it
    carries becomes invisible.
    """
    assert quest_ids("1305,1", PAIR) == {130501}
    assert quest_ids("1305,1", GLOBAL_HEAD) == {1305}


def test_a_comma_list_of_global_ids_is_not_a_pair():
    """NpcData_415 hides on eight quests in one attribute value.

    Read as a pair it yields one bogus id and loses all eight real ones.
    """
    value = "41501,41502,41503,41504,41505,41506,41507,41508"

    assert len(quest_ids(value, GLOBAL_LIST)) == 8
    assert quest_ids(value, PAIR) == set()


# ---------------------------------------------------------------------------
# references: one positive oracle per family
# ---------------------------------------------------------------------------

FAMILY_CASES = {
    "prereq": (
        {"QuestData/005002.quest": quest_xml(5002, 50, 2, prereqs=("50,1",))},
        "quest-5002",
    ),
    "link": (
        {"QuestData/005002.quest": quest_xml(5002, 50, 2, link="50,1")},
        "quest-5002",
    ),
    "inProgress": (
        {"QuestData/005002.quest": quest_xml(5002, 50, 2, in_progress=("5001,1",))},
        "quest-5002",
    ),
    "dungeonEvent": (
        {"DungeonData_9037.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                 '<DungeonData><Event questId="5001" taskId="1" /></DungeonData>'},
        "DungeonData_9037.xml",
    ),
    "dungeonEventTask": (
        {"DungeonData_9037.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                 '<DungeonData><EventTask type="updateQuest" questId="5001" '
                                 'taskId="3" /></DungeonData>'},
        "DungeonData_9037.xml",
    ),
    "dungeonProgressQuest": (
        {"DungeonData_9037.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                 '<DungeonData><Condition type="progressQuest" value="5001" '
                                 'taskId="5" /></DungeonData>'},
        "DungeonData_9037.xml",
    ),
    "dungeonCompleteQuest": (
        {"DungeonData_9037.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                 '<DungeonData><Condition type="completeQuest" value="5001" />'
                                 "</DungeonData>"},
        "DungeonData_9037.xml",
    ),
    "dungeonDaily": (
        {"DungeonData_9037.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                 '<DungeonData><Dungeon relatedDailyQuest="5001" /></DungeonData>'},
        "DungeonData_9037.xml",
    ),
    "dungeonScenario": (
        {"DungeonData_9037.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                 '<DungeonData><Dungeon scenarioQuestId="5001" /></DungeonData>'},
        "DungeonData_9037.xml",
    ),
    "workObject": (
        {"WorkObjectData.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                               '<WorkObjectData><WorkObject id="1" isForQuestId="5001" />'
                               "</WorkObjectData>"},
        "WorkObjectData.xml",
    ),
    "npcAppear": (
        {"NpcData_50.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                           '<NpcData><Template id="1" name="x" appearQuestId="5001" /></NpcData>'},
        "NpcData_50.xml",
    ),
    "npcHide": (
        {"NpcData_50.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                           '<NpcData><Template id="1" name="x" hideQuestId="5001" /></NpcData>'},
        "NpcData_50.xml",
    ),
    "areaRequire": (
        {"AreaData/AreaData_1_1.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                      '<AreaData><Section requireQuestId="5001" /></AreaData>'},
        "AreaData_1_1.xml",
    ),
    "achievement": (
        {"AchievementList.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                '<AchievementList><Achievement id="5991">'
                                '<Condition type="check" templateId="4012" value1="5001" />'
                                "</Achievement></AchievementList>"},
        "achievement-5991",
    ),
}


@pytest.mark.parametrize("family", sorted(FAMILY_CASES))
def test_every_reference_family_fires_on_a_disabled_target(corpus_dir, family):
    """A family missing from the sweep reports a clean trim that orphans content.

    That is the failure mode worth guarding: the tool says the retirement is
    safe and nothing about the output looks wrong.
    """
    files, expected_source = FAMILY_CASES[family]
    tree = {"QuestData/005001.quest": DISABLED}
    tree.update(files)
    corpus, scope = build(corpus_dir, tree)

    findings = check_references(corpus, scope)

    assert [f.severity for f in findings] == ["high"]
    assert findings[0].subject == "quest-5001"
    assert findings[0].evidence["family"] == family
    assert findings[0].evidence["source"] == expected_source
    assert findings[0].key == f"references:quest-5001:{family}:{expected_source}"


def test_the_1323_shape_fires_when_the_dependant_is_not_rewired(corpus_dir):
    """Retiring 1323 would have orphaned 1324.

    This is the incident the check exists for, pinned hermetically because it
    was AVOIDED in the real corpus: the wave rewired 1324 onto 1322 in the same
    change, so neither snapshot holds the broken state. The corpus tests below
    assert both halves of that rewire.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/001323.quest": quest_xml(1323, 13, 23, prereqs=("99,99",)),
        "QuestData/001324.quest": quest_xml(1324, 13, 24, prereqs=("13,23",)),
    }, zones=(13,))

    findings = check_references(corpus, scope)

    assert len(findings) == 1
    assert findings[0].evidence == {"quest": 1323, "family": "prereq", "source": "quest-1324"}


def test_the_1318_shape_stays_silent(corpus_dir):
    """Retiring 1318 was free: nothing in the corpus referenced it."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001318.quest": quest_xml(1318, 13, 18, prereqs=("99,99",)),
        "QuestData/001324.quest": quest_xml(1324, 13, 24, prereqs=("13,22",)),
    }, zones=(13,))

    assert check_references(corpus, scope) == []


def test_both_sentinel_encodings_disable_a_quest(corpus_dir):
    """Treating only 99,99 as a sentinel reports 17 disabled quests as live."""
    for sentinel in sorted(SENTINEL_PREREQS):
        corpus, scope = build(corpus_dir, {
            "QuestData/005001.quest": quest_xml(5001, 50, 1, prereqs=(sentinel,)),
            "QuestData/005002.quest": quest_xml(5002, 50, 2, prereqs=("50,1",)),
        })

        assert len(check_references(corpus, scope)) == 1, sentinel


# ---------------------------------------------------------------------------
# references: negative oracles
# ---------------------------------------------------------------------------

def test_a_reference_into_a_live_quest_is_not_a_finding(corpus_dir):
    corpus, scope = build(corpus_dir, {
        "QuestData/005001.quest": quest_xml(5001, 50, 1, prereqs=("50,3",)),
        "QuestData/005002.quest": quest_xml(5002, 50, 2, prereqs=("50,1",)),
        "QuestData/005003.quest": quest_xml(5003, 50, 3),
    })

    assert check_references(corpus, scope) == []


def test_an_npc_reference_that_merely_contains_the_sentinel_digits_is_not_one(corpus_dir):
    """The case study for parsing structurally.

    A raw substring search for 99,9999 matches 563 quest files at the baseline;
    17 are disabled. The rest carry it as an NPC reference, hunting zone 99
    template 9999, which is a different field meaning a different thing.
    """
    text = quest_xml(5002, 50, 2, prereqs=("50,1",), visit_npcs=("99,9999",))
    assert "99,9999" in text, "the fixture must contain the substring"

    corpus, scope = build(corpus_dir, {
        "QuestData/005001.quest": quest_xml(5001, 50, 1),
        "QuestData/005002.quest": text,
    })

    assert corpus.quests[5002]["sentinel"] is False
    assert check_references(corpus, scope) == []


def test_a_sentinel_prerequisite_is_not_itself_an_edge(corpus_dir):
    """99,99 points at no quest. Read as a pair it would name quest 9999."""
    corpus, scope = build(corpus_dir, {
        "QuestData/005001.quest": quest_xml(5001, 50, 1, prereqs=("99,99",)),
    })

    assert [e for e in reference_edges(corpus) if e.family == "prereq"] == []


def test_the_no_successor_idiom_is_not_an_edge(corpus_dir):
    """1,1 in 연결퀘스트 means no successor, not quest 101."""
    corpus, _ = build(corpus_dir, {"QuestData/005001.quest": quest_xml(5001, 50, 1, link="1,1")})

    assert [e for e in reference_edges(corpus) if e.family == "link"] == []


def test_a_commented_out_reference_is_inert(corpus_dir):
    """The server never loads it, so reporting it sends someone to fix nothing.

    This is the mirror of the dungeon 9037 incident, where grep saw content the
    server did not load.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/005001.quest": DISABLED,
        "DungeonData_9037.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                                "<DungeonData><!-- <Event questId=\"5001\" taskId=\"1\" /> -->"
                                "</DungeonData>",
    })

    assert check_references(corpus, scope) == []


def test_regional_shop_style_variants_are_not_counted_twice(corpus_dir):
    """Six regional AchievementList twins would sextuple every edge."""
    achievement = ('<?xml version="1.0" encoding="utf-8"?>\n'
                   '<AchievementList><Achievement id="5991">'
                   '<Condition type="check" templateId="4012" value1="5001" />'
                   "</Achievement></AchievementList>")
    corpus, scope = build(corpus_dir, {
        "QuestData/005001.quest": DISABLED,
        "AchievementList.xml": achievement,
        "AchievementList_NAEU.xml": achievement,
        "AchievementList_KR.xml": achievement,
    })

    assert len(check_references(corpus, scope)) == 1


def test_item_possession_conditions_are_not_quest_references(corpus_dir):
    """templateId 1020 is item possession. A previous analysis measured an
    achievement-safety claim against it and got an answer about nothing."""
    corpus, scope = build(corpus_dir, {
        "QuestData/005001.quest": DISABLED,
        "AchievementList.xml": '<?xml version="1.0" encoding="utf-8"?>\n'
                               '<AchievementList><Achievement id="1934">'
                               '<Condition type="count" templateId="1020" value1="1" value2="5001" />'
                               "</Achievement></AchievementList>",
    })

    assert check_references(corpus, scope) == []


def test_subject_scope_limits_reporting_but_not_evidence(corpus_dir):
    """A zone-scoped evidence read cannot prove a trim orphans nothing."""
    corpus, scope = build(corpus_dir, {
        "QuestData/005001.quest": quest_xml(5001, 50, 1, prereqs=("99,99",)),
        "QuestData/006401.quest": quest_xml(6401, 64, 1, prereqs=("50,1",)),
        "QuestData/006402.quest": quest_xml(6402, 64, 2, prereqs=("99,99",)),
    }, zones=(50,))

    findings = check_references(corpus, scope)

    assert [f.subject for f in findings] == ["quest-5001"], "zone 64 is not the subject"
    assert findings[0].evidence["source"] == "quest-6401", "evidence still reaches zone 64"


# ---------------------------------------------------------------------------
# hidden-gates
# ---------------------------------------------------------------------------

def test_a_bare_in_progress_gate_is_medium(corpus_dir):
    """The gate is a legitimate escort and timing idiom on its own."""
    corpus, scope = build(corpus_dir, {
        "QuestData/005002.quest": quest_xml(5002, 50, 2, in_progress=("5001,1",)),
        "QuestData/005001.quest": quest_xml(5001, 50, 1),
    })

    findings = check_hidden_gates(corpus, scope)

    assert [f.severity for f in findings] == ["medium"]
    assert findings[0].key == "hidden-gates:quest-5002:5001"
    assert findings[0].evidence["gates_on"] == 5001


def test_a_gate_on_a_quest_that_grants_equipment_is_high(corpus_dir):
    """The 1326/1330 shape: finishing the gating quest strands the set."""
    corpus, scope = build(corpus_dir, {
        "QuestData/005002.quest": quest_xml(5002, 50, 2, in_progress=("5001,1",)),
        "QuestData/005001.quest": quest_xml(5001, 50, 1),
        "CompensationData/QuestCompensationData_50.xml": comp_xml(
            [(5002, "1000", "100", [15021, 15024])]),
    })

    findings = check_hidden_gates(corpus, scope)

    assert [f.severity for f in findings] == ["high"]
    assert findings[0].evidence["equipment"] == [15021, 15024]
    assert "strands them permanently" in findings[0].message


def test_a_cosmetic_grant_does_not_escalate_a_gate(corpus_dir):
    """startswith("EQUIP") also matches roughly 4,100 costume items.

    Escalating on those makes every costume repeatable a high finding.
    """
    corpus, scope = build(corpus_dir, {
        "QuestData/005002.quest": quest_xml(5002, 50, 2, in_progress=("5001,1",)),
        "QuestData/005001.quest": quest_xml(5001, 50, 1),
        "CompensationData/QuestCompensationData_50.xml": comp_xml(
            [(5002, "1000", "100", [88888])]),
    })

    assert [f.severity for f in check_hidden_gates(corpus, scope)] == ["medium"]


def test_a_prerequisite_is_not_a_hidden_gate(corpus_dir):
    """A prerequisite is a door you walk through. This check is about the other
    kind, the one that locks behind you."""
    corpus, scope = build(corpus_dir, {
        "QuestData/005002.quest": quest_xml(5002, 50, 2, prereqs=("50,1",)),
        "QuestData/005001.quest": quest_xml(5001, 50, 1),
    })

    assert check_hidden_gates(corpus, scope) == []


def test_the_gate_target_is_read_as_a_global_id(corpus_dir):
    """1305,1 is quest 1305 task 1, never quest 130501."""
    corpus, scope = build(corpus_dir, {
        "QuestData/001326.quest": quest_xml(1326, 13, 26, in_progress=("1305,1",)),
    }, zones=(13,))

    assert check_hidden_gates(corpus, scope)[0].evidence["gates_on"] == 1305


# ---------------------------------------------------------------------------
# client-parity
# ---------------------------------------------------------------------------

SYNC_CONFIG = """version: 1
entities:
  QuestCompensationData:
    strategy: SourceMapped
    source_mapping:
      "CompensationData/QuestCompensationData_50.xml": "QuestCompensationData-00049.xml"
"""


@pytest.fixture
def client_side(tmp_path, monkeypatch):
    """Factory wiring a synthetic client folder and sync config into the check."""

    def wire(shards: dict[str, str] | None, config: str | None = SYNC_CONFIG) -> Path:
        comp_dir = tmp_path / "client" / "QuestCompensationData"
        if shards is not None:
            comp_dir.mkdir(parents=True)
            for name, text in shards.items():
                (comp_dir / name).write_text(text, encoding="utf-8")
        cfg = tmp_path / "sync-config.yaml"
        if config is not None:
            cfg.write_text(config, encoding="utf-8")
        monkeypatch.setattr(graph, "client_comp_dir",
                            lambda: comp_dir if comp_dir.is_dir() else None)
        monkeypatch.setattr(graph, "sync_config_path", lambda: cfg)
        return comp_dir

    return wire


def test_a_stale_client_row_is_high(client_side, corpus_dir):
    """The exact defect: the log advertised exp and gold with no items while the
    payout was correct, because the Item rows were server-side only."""
    client_side({"QuestCompensationData-00049.xml": comp_xml([(5001, "800", "80", [])])})
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_50.xml": comp_xml([(5001, "800", "80", [15021])]),
    })

    findings = check_client_parity(corpus, scope)

    assert [f.severity for f in findings] == ["high"]
    assert findings[0].key == "client-parity:quest-5001:client-stale"
    assert findings[0].evidence["kind"] == "stale"


def test_a_server_only_row_is_high(client_side, corpus_dir):
    client_side({"QuestCompensationData-00049.xml": comp_xml([(5001, "800", "80", [15021])])})
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_50.xml": comp_xml([
            (5001, "800", "80", [15021]),
            (5002, "900", "90", [15024]),
        ]),
    })

    findings = check_client_parity(corpus, scope)

    assert [f.evidence["kind"] for f in findings] == ["server-only"]
    assert findings[0].subject == "quest-5002"


def test_a_client_row_the_server_does_not_have_is_high(client_side, corpus_dir):
    client_side({"QuestCompensationData-00049.xml": comp_xml([
        (5001, "800", "80", [15021]),
        (5002, "900", "90", [15024]),
    ])})
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_50.xml": comp_xml([(5001, "800", "80", [15021])]),
    })

    findings = check_client_parity(corpus, scope)

    assert [f.evidence["kind"] for f in findings] == ["client-orphan"]


def test_matching_rows_in_a_mapped_zone_are_silent(client_side, corpus_dir):
    client_side({"QuestCompensationData-00049.xml": comp_xml([(5001, "800", "80", [15021])])})
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_50.xml": comp_xml([(5001, "800", "80", [15021])]),
    })

    assert check_client_parity(corpus, scope) == []


def test_an_unmapped_zone_is_flagged_even_when_the_rows_agree(client_side, corpus_dir):
    """The rows agree today. The next edit to them skips the client silently."""
    client_side({"QuestCompensationData-00212.xml": comp_xml([(21301, "800", "80", [15021])])})
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_213.xml": comp_xml([(21301, "800", "80", [15021])]),
    }, zones=(213,))

    findings = check_client_parity(corpus, scope)

    assert [f.key for f in findings] == ["client-parity:zone-213:unmapped"]
    assert findings[0].severity == "high"
    assert findings[0].evidence["rows"] == 1


def test_an_unmapped_zone_with_no_rows_is_not_flagged(client_side, corpus_dir):
    """A zone with nothing to sync has nothing to lose yet.

    The finding appears the moment the first reward row is authored, which is
    exactly when it starts mattering.
    """
    client_side({})
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_213.xml": comp_xml([]),
    }, zones=(213,))

    assert check_client_parity(corpus, scope) == []


def test_an_unmapped_zone_anchors_on_a_touched_quest(client_side, corpus_dir):
    """migrate counts only findings whose evidence names a quest the caller
    touched, so a zone-level finding has to name one or it is never NEW."""
    rows = comp_xml([(21301, "800", "80", []), (21302, "900", "90", [])])
    client_side({"QuestCompensationData-00212.xml": rows})
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_213.xml": rows,
    }, zones=(213,), new={21302})

    findings = check_client_parity(corpus, scope)

    assert [f.detail for f in findings] == ["unmapped"]
    assert findings[0].evidence["quest"] == 21302
    assert scope.is_new(findings[0].evidence["quest"])


def test_a_missing_client_degrades_to_one_informational_finding(client_side, corpus_dir):
    """A clean clone has no client DataCenter.

    Returning nothing would read as a clean parity result, which is the one
    outcome this check must never produce without having looked.
    """
    client_side(None)
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_50.xml": comp_xml([(5001, "800", "80", [15021])]),
    })

    findings = check_client_parity(corpus, scope)

    assert [f.severity for f in findings] == ["info"]
    assert "NOT checked" in findings[0].message


def test_an_unreadable_sync_config_does_not_claim_a_zone_is_unmapped(client_side, corpus_dir):
    """Unreadable config cannot prove anything about mapping either way."""
    client_side({"QuestCompensationData-00049.xml": comp_xml([(5001, "800", "80", [15021])])},
                config=None)
    corpus, scope = build(corpus_dir, {
        "CompensationData/QuestCompensationData_50.xml": comp_xml([(5001, "800", "80", [15021])]),
    })

    findings = check_client_parity(corpus, scope)

    assert [f.detail for f in findings] == ["config-unreadable"]
    assert [f.severity for f in findings] == ["info"]


def test_a_zone_with_no_server_file_is_skipped(client_side, corpus_dir):
    client_side({})
    corpus, scope = build(corpus_dir, {"QuestData/005001.quest": quest_xml(5001, 50, 1)})

    assert check_client_parity(corpus, scope) == []


def test_synced_zones_reads_the_real_project_config():
    """The checked-in config must stay parseable by this check."""
    zones = synced_zones(graph.sync_config_path())

    assert zones is not None, "config/sync-config.yaml did not parse"
    assert 13 in zones, "zone 13 is the one mapped reward table"


# ---------------------------------------------------------------------------
# Corpus tier
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def at_baseline(datasheet_dir, baseline):
    return Corpus(datasheet_dir, baseline, use_baseline=True)


@pytest.fixture(scope="session")
def at_worktree(datasheet_dir):
    return Corpus(datasheet_dir, V92Baseline(datasheet_dir), use_baseline=False)


ALL_ZONES = Scope(zones=None, new_quests=None)
ZONE_13 = Scope(zones={13}, new_quests=None)


# --- sentinels: grep versus structural ---------------------------------------

@pytest.mark.corpus
def test_grep_finds_thirty_three_times_as_many_sentinels_as_exist(datasheet_dir, baseline):
    """The case study for parsing structurally instead of grepping.

    Both numbers are measured here rather than quoted, because the whole lesson
    is that the cheap number is the wrong one.
    """
    grep_hits, structural, tags = 0, 0, {}
    for path in sorted((datasheet_dir / "QuestData").glob("*.quest")):
        text = baseline.read(f"QuestData/{path.name}", baseline=True)
        if text is None or "99,9999" not in text:
            continue
        grep_hits += 1
        root = ET.fromstring(text.encode("utf-8"))
        for el in root.iter():
            if "99,9999" in (el.text or ""):
                tags[strip_ns(el.tag)] = tags.get(strip_ns(el.tag), 0) + 1
        model = parse_quest(text)
        if model and model["sentinel"] and model["prereqs"][0] == "99,9999":
            structural += 1

    assert grep_hits == 563, "the substring search"
    assert structural == 17, "the structural answer"
    assert tags == {"퀘스트Id": 17, "NPCId": 512, "대상NPC지정": 80}, \
        "the 546 extra files carry it as an NPC reference: hunting zone 99, template 9999"


@pytest.mark.corpus
def test_both_sentinel_encodings_are_in_use_at_the_baseline(at_baseline):
    """Treating only 99,99 as a sentinel reports 17 disabled quests as live."""
    counts = {"99,99": 0, "99,9999": 0}
    for quest in at_baseline.quests.values():
        if quest["sentinel"]:
            counts[quest["prereqs"][0]] += 1

    assert counts == {"99,99": 55, "99,9999": 17}
    assert sum(counts.values()) == 72


# --- the reference sweep ------------------------------------------------------

@pytest.mark.corpus
def test_the_edge_map_covers_every_declared_family(at_baseline):
    """A family silently yielding nothing is the failure mode here.

    The check then reports a clean retirement for a quest three other families
    still point at, and nothing about the output looks wrong.
    """
    families = {e.family for e in reference_edges(at_baseline)}

    assert families == {
        "prereq", "link", "inProgress",
        "dungeonEvent", "dungeonEventTask", "dungeonProgressQuest", "dungeonCompleteQuest",
        "dungeonDaily", "dungeonScenario",
        "workObject", "npcAppear", "npcHide", "areaRequire", "achievement",
    }


@pytest.mark.corpus
def test_the_dungeon_quest_id_surface_lives_on_exactly_two_elements(at_baseline):
    """Read the element name from the match rather than enumerating it.

    Both prior surveys of this surface listed Event and missed EventTask, which
    is 14 live references. Deriving the name means a third element carrying
    questId joins the sweep instead of vanishing from it.
    """
    counts = {}
    for edge in reference_edges(at_baseline):
        if edge.family.startswith("dungeon") and "Quest" not in edge.family:
            counts[edge.family] = counts.get(edge.family, 0) + 1

    assert set(counts) == {"dungeonEvent", "dungeonEventTask", "dungeonDaily", "dungeonScenario"}
    assert counts["dungeonEvent"] == 77
    assert counts["dungeonEventTask"] == 7


@pytest.mark.corpus
def test_dungeon_9037_is_wired_to_quest_1346(at_baseline):
    """The Sorcha encounter. Missing the Event questId surface loses this."""
    families = {e.family for e in inbound_map(at_baseline)[1346]}

    assert "dungeonEvent" in families
    assert families == {"dungeonEvent", "dungeonProgressQuest", "dungeonCompleteQuest",
                        "link", "workObject"}
    assert all(e.source == "DungeonData_9037.xml"
               for e in inbound_map(at_baseline)[1346] if e.family.startswith("dungeon"))


@pytest.mark.corpus
def test_the_reference_check_finds_the_real_corpus_defects(at_baseline):
    """13 disabled quests still carry 19 live inbound references."""
    findings = check_references(at_baseline, ALL_ZONES)

    assert len(findings) == 19
    assert {f.severity for f in findings} == {"high"}
    assert len({f.subject for f in findings}) == 13
    assert "references:quest-244:dungeonEvent:DungeonData_9090.xml" in {f.key for f in findings}


@pytest.mark.corpus
def test_quest_59901_is_referenced_by_five_families_at_once(at_baseline):
    """One subject exercising five of the fourteen families in real data."""
    families = {f.evidence["family"] for f in check_references(at_baseline, ALL_ZONES)
                if f.subject == "quest-59901"}

    assert families == {"prereq", "achievement", "npcAppear", "npcHide", "workObject"}


@pytest.mark.corpus
def test_the_in_progress_encoding_is_the_difference_between_finding_a_defect_and_not(at_baseline):
    """Quest 201 is disabled and quest 221 still gates on it being in progress.

    Read as a pair, "201,12" resolves to quest 20112, which does not exist, and
    this defect disappears without a trace. It is the only one of the 19 that
    the wrong encoding hides.
    """
    edges = [e for e in inbound_map(at_baseline)[201] if e.family == "inProgress"]

    assert at_baseline.quests[201]["sentinel"] is True
    assert edges == [Edge(201, "inProgress", "quest-221")]
    assert quest_ids("201,12", PAIR) == {20112}
    assert 20112 not in at_baseline.quests


@pytest.mark.corpus
def test_the_in_progress_family_resolves_only_as_a_global_id(at_baseline, baseline, datasheet_dir):
    """Measured over every value in the corpus, both readings scored.

    37 of 37 resolve as a global id; 0 of 37 as a pair. The task half names a
    real task on the global-read target every time, which is the second,
    independent confirmation.
    """
    values = [v for vs in in_progress_gates(at_baseline).values() for v in vs]
    as_pair = sum(1 for v in values for t in quest_ids(v, PAIR) if t in at_baseline.quests)
    as_global = sum(1 for v in values for t in quest_ids(v, GLOBAL_HEAD) if t in at_baseline.quests)
    tasks_exist = sum(
        1 for v in values
        if (lambda q, t: q is not None and t in q["tasks"])(
            at_baseline.quests.get(int(v.split(",")[0])), int(v.split(",")[1]))
    )

    assert len(values) == 37
    assert (as_pair, as_global) == (0, 37)
    assert tasks_exist == 37


@pytest.mark.corpus
def test_the_prerequisite_family_resolves_only_as_a_pair(at_baseline):
    """The mirror measurement, so neither encoding is assumed anywhere."""
    values = [p for q in at_baseline.quests.values() for p in q["prereqs"]
              if p not in SENTINEL_PREREQS]
    as_pair = sum(1 for v in values for t in quest_ids(v, PAIR) if t in at_baseline.quests)
    as_global = sum(1 for v in values for t in quest_ids(v, GLOBAL_HEAD) if t in at_baseline.quests)

    assert len(values) == 1111
    assert (as_pair, as_global) == (1097, 123)


@pytest.mark.corpus
def test_the_hide_quest_comma_value_is_a_list_of_eight_real_quests(at_baseline):
    """The one corpus value that is a comma LIST rather than a single id.

    Reading it as a pair loses eight edges and invents a bogus one, which is why
    every family declares its encoding instead of sniffing the value.
    """
    value = "41501,41502,41503,41504,41505,41506,41507,41508"
    targets = quest_ids(value, GLOBAL_LIST)

    assert len(targets) == 8
    assert targets <= set(at_baseline.quests), "all eight are real quests"
    edges = {e.target for e in reference_edges(at_baseline)
             if e.family == "npcHide" and e.source == "NpcData_415.xml"}
    assert targets <= edges


# --- the 1323 / 1318 incident, before and after ------------------------------

@pytest.mark.corpus
def test_1323_had_one_inbound_edge_and_1318_had_none(at_baseline):
    """The question the trimming wave had to answer 5 times.

    Both quests look identical in their own file: same zone, same prerequisite,
    same shape. They differ only in the corpus-wide inbound edge map.
    """
    inbound = inbound_map(at_baseline)

    assert inbound[1323] == [Edge(1323, "prereq", "quest-1324")]
    assert 1318 not in inbound
    assert at_baseline.quests[1323]["sentinel"] is False, "still live at the baseline"


@pytest.mark.corpus
def test_the_wave_disabled_1323_and_rewired_1324_in_the_same_change(at_worktree, at_baseline):
    """Why zone 13 is silent on the working tree, spelled out.

    1324's prerequisite moved from 1323 to 1322 as 1323 was retired. Had it not,
    the hermetic 1323 test above is exactly what would have fired.
    """
    assert at_baseline.quests[1324]["prereqs"] == ["13,23"]
    assert at_worktree.quests[1324]["prereqs"] == ["13,22"]
    assert at_worktree.quests[1323]["sentinel"] is True
    assert 1323 not in inbound_map(at_worktree)


@pytest.mark.corpus
def test_zone_13_is_silent_at_both_snapshots(at_baseline, at_worktree):
    """The negative oracle, and the point of the whole check.

    The wave disabled five more Island of Dawn quests (1318, 1323, 1343, 1344,
    1386) and introduced zero dangling references, because it rewired the one
    dependant first. A check that fired here would be reporting the successful
    case as a defect.
    """
    before = {g for g, q in at_baseline.quests.items() if q["sentinel"] and 1300 <= g <= 1399}
    after = {g for g, q in at_worktree.quests.items() if q["sentinel"] and 1300 <= g <= 1399}

    assert after - before == {1318, 1323, 1343, 1344, 1386}
    assert check_references(at_baseline, ZONE_13) == []
    assert check_references(at_worktree, ZONE_13) == []


# --- achievement condition semantics -----------------------------------------

def _achievement_conditions(corpus, template_id: str) -> list[dict]:
    text = corpus.read("AchievementList.xml")
    out = []
    for raw in re.findall(r"<Condition\b([^>]*?)/?>", text):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', raw))
        if attrs.get("templateId") == template_id:
            out.append(attrs)
    return out


@pytest.mark.corpus
def test_4012_is_quest_completion_and_1020_is_item_possession(at_baseline, datasheet_dir, baseline):
    """Proved from the data, never asserted from a name.

    A trimming-wave safety claim was once measured against 1020 and produced a
    meaningless answer, which is why this is a test and not a comment. Three
    independent signals agree:

      value space  1020's value2 lands in the item id space 100 times out of 100
                   and in the quest id space 0 times. 4012's value1 lands in the
                   quest id space 244 times out of 286.
      arity        1020 carries value1 AND value2; 4012 carries value1 alone.
      shape        1020's value1 is the constant 1 (a quantity) and its type is
                   "count"; 4012's type is "check".
    """
    items = load_item_model(datasheet_dir, read=lambda rel: baseline.read(rel, baseline=True))
    quests = set(at_baseline.quests)
    poss = _achievement_conditions(at_baseline, ACHIEVEMENT_ITEM_TEMPLATE)
    done = _achievement_conditions(at_baseline, ACHIEVEMENT_QUEST_TEMPLATE)

    assert (len(poss), len(done)) == (100, 286)

    poss_v2 = [int(a["value2"]) for a in poss]
    assert sum(1 for v in poss_v2 if v in items) == 100
    assert sum(1 for v in poss_v2 if v in quests) == 0
    assert {a["value1"] for a in poss} == {"1"}
    assert {a["type"] for a in poss} == {"count"}

    done_v1 = [int(a["value1"]) for a in done]
    assert sum(1 for v in done_v1 if v in quests) == 244
    assert all("value2" not in a for a in done)
    assert {a["type"] for a in done} == {"check"}


@pytest.mark.corpus
def test_six_island_quests_are_achievement_referenced(at_baseline):
    """The correctly measured answer to the trimming-wave safety question.

    None of the five quests the wave retired is in this set, so the trims were
    safe. Measured against 1020 the same question returns an empty set, which is
    how it came to be answered by luck rather than by check.
    """
    done = {int(a["value1"]) for a in _achievement_conditions(at_baseline, "4012")
            if a["value1"].isdigit()}
    poss = {int(a["value2"]) for a in _achievement_conditions(at_baseline, "1020")
            if a.get("value2", "").isdigit()}
    island = {q for q in done if 1300 <= q <= 1399}

    assert island == {1301, 1303, 1309, 1316, 1317, 1329}
    assert {q for q in poss if 1300 <= q <= 1399} == set(), "the meaningless answer"
    assert island & {1318, 1323, 1343, 1344, 1386} == set(), "none of the trims was referenced"


# --- hidden gates -------------------------------------------------------------

@pytest.mark.corpus
def test_1326_and_1330_fire_at_high_on_the_baseline(at_baseline):
    """Both gate on 1305 being in progress and both grant set pieces."""
    findings = check_hidden_gates(at_baseline, ZONE_13)

    assert {f.subject for f in findings} == {"quest-1326", "quest-1330"}
    assert {f.severity for f in findings} == {"high"}
    assert {f.evidence["gates_on"] for f in findings} == {1305}
    assert {tuple(f.evidence["equipment"]) for f in findings} == {
        (15021, 15024, 15027), (15020, 15023, 15026)}


@pytest.mark.corpus
def test_the_island_gates_are_gone_from_the_working_tree(at_worktree, at_baseline):
    """Fire then quiet: spec 002/29 cleared both gates."""
    assert len(in_progress_gates(at_baseline)) == 37
    assert len(in_progress_gates(at_worktree)) == 35
    assert check_hidden_gates(at_worktree, ZONE_13) == []


@pytest.mark.corpus
def test_the_bare_gate_stays_at_medium_across_the_corpus(at_baseline):
    """34 of the 37 gates grant no equipment and must not be escalated.

    An escort quest gated on its escort being under way is the idiom working as
    designed, and a check that called all 37 high would be ignored by the second
    time someone read it.
    """
    findings = check_hidden_gates(at_baseline, ALL_ZONES)
    high = [f for f in findings if f.severity == "high"]

    assert len(findings) == 37
    assert sum(1 for f in findings if f.severity == "medium") == 34
    assert {f.subject for f in high} == {"quest-1326", "quest-1330", "quest-70203"}


# --- client parity ------------------------------------------------------------

@pytest.mark.corpus
def test_seventeen_zone_13_rows_were_stale_at_the_baseline(at_baseline):
    """The single most impactful defect of the session that produced this tool.

    Skipped rather than failed when the client DataCenter is unavailable, since
    it is gitignored and absent from a clean clone.
    """
    findings = check_client_parity(at_baseline, ZONE_13)
    if any(f.subject == "client" for f in findings):
        pytest.skip("client DataCenter unavailable")

    kinds = [f.evidence.get("kind") for f in findings]

    assert kinds.count("stale") == 17
    assert kinds.count("client-orphan") == 1
    assert {f.severity for f in findings} == {"high"}
    assert "client-parity:quest-1387:client-stale" in {f.key for f in findings}


@pytest.mark.corpus
def test_zone_13_parity_is_clean_on_the_working_tree(at_worktree):
    """Fire then quiet: the sync landed."""
    findings = check_client_parity(at_worktree, ZONE_13)
    if any(f.subject == "client" for f in findings):
        pytest.skip("client DataCenter unavailable")

    assert findings == []


@pytest.mark.corpus
def test_zone_213_is_unmapped_in_the_real_sync_config(at_worktree):
    """Ten rows on each side and no pair, so the next edit there skips silently.

    Zone 13 is the only mapped reward table, deliberately, and this is what that
    decision costs everywhere else.
    """
    findings = check_client_parity(at_worktree, Scope(zones={213}, new_quests=None))
    if any(f.subject == "client" for f in findings):
        pytest.skip("client DataCenter unavailable")

    assert [f.key for f in findings] == ["client-parity:zone-213:unmapped"]
    assert findings[0].evidence["rows"] == 10


# --- cost ---------------------------------------------------------------------

@pytest.mark.corpus
def test_the_sweep_reads_the_corpus_without_a_subprocess_per_file(at_worktree):
    """This runs after every patch apply.

    The whole sweep touches roughly 3,600 files and 76 MB. Reading each one
    through git would take minutes instead of seconds, which is well past the
    point anyone leaves a post-apply hook enabled.
    """
    import time

    start = time.time()
    edges = reference_edges(at_worktree)
    first = time.time() - start

    start = time.time()
    reference_edges(at_worktree)
    cached = time.time() - start

    assert len(edges) > 2000
    assert first < 60, "the cold sweep"
    assert cached < 0.05, "the second call must come from the corpus cache"
