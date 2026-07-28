"""Quest parsing: count semantics, sentinels, and label-versus-body honesty.

Three hunt shapes put their required count in three different places, and a
check that reads the wrong one produces a confident, wrong feasibility verdict.
These tests pin each shape against the structure the corpus actually uses.
"""

from __future__ import annotations

import pytest

from dclib import SENTINEL_PREREQS, parse_quest, task_body_mismatch


def quest(header_extra: str = "", tasks: str = "") -> dict:
    return parse_quest(f"""<?xml version="1.0" encoding="utf-8"?>
<Quest id="1348">
  <Header>
    <Quest번호>13,48</Quest번호>
    <수행조건>{header_extra}</수행조건>
  </Header>
  <Tasks>{tasks}</Tasks>
</Quest>
""")


HUNT_DELIVER = """
    <Task id="1">
      <Header><이름>사냥전달Task</이름></Header>
      <Body>
        <아이템작성>
          <아이템작성>
            <Flag아이템이름>@quest:1348004</Flag아이템이름>
            <전달수량>8</전달수량>
            <몬스터지정>
              <몬스터지정><몬스터Id>13,302</몬스터Id><수여확률>90</수여확률></몬스터지정>
              <몬스터지정><몬스터Id>13,303</몬스터Id><수여확률>17</수여확률></몬스터지정>
            </몬스터지정>
          </아이템작성>
        </아이템작성>
      </Body>
    </Task>
"""

PLAIN_HUNT = """
    <Task id="1">
      <Header><이름>사냥Task</이름></Header>
      <Body>
        <몬스터지정>
          <몬스터지정><몬스터Id>13,302</몬스터Id><사냥마리수>10</사냥마리수></몬스터지정>
          <몬스터지정><몬스터Id>13,303</몬스터Id><사냥마리수>5</사냥마리수></몬스터지정>
        </몬스터지정>
      </Body>
    </Task>
"""

GROUP_HUNT = """
    <Task id="1">
      <Header><이름>그룹사냥Task</이름></Header>
      <Body>
        <몬스터그룹>
          <몬스터그룹>
            <그룹이름>@quest:301009</그룹이름>
            <사냥마리수>15</사냥마리수>
            <몬스터지정>
              <몬스터지정><몬스터Id>13,302</몬스터Id></몬스터지정>
              <몬스터지정><몬스터Id>13,303</몬스터Id></몬스터지정>
            </몬스터지정>
          </몬스터그룹>
        </몬스터그룹>
      </Body>
    </Task>
"""

COLLECT = """
    <Task id="1">
      <Header><이름>채집Task</이름></Header>
      <Body>
        <채집물지정><채집물지정><콜렉션Id>409</콜렉션Id></채집물지정></채집물지정>
        <전달아이템지정>
          <전달아이템지정><아이템Id>9106</아이템Id><전달수량>1</전달수량></전달아이템지정>
        </전달아이템지정>
      </Body>
    </Task>
"""


# ---------------------------------------------------------------------------
# Count semantics: three shapes, three locations
# ---------------------------------------------------------------------------

def test_hunt_deliver_count_is_on_the_bag_and_rates_are_per_entry():
    """The required count is stated once per bag, never per monster entry.

    Reading it off the entries yields either nothing or a double count, and the
    feasibility ratio is wrong in both directions.
    """
    task = quest(tasks=HUNT_DELIVER)["tasks"][1]

    assert len(task["bags"]) == 1
    bag = task["bags"][0]
    assert bag["qty"] == "8"
    assert bag["flag"] == "@quest:1348004"
    assert bag["monsters"] == [("13,302", "", "90"), ("13,303", "", "17")]


def test_plain_hunt_count_is_per_monster_entry_and_never_has_rates():
    task = quest(tasks=PLAIN_HUNT)["tasks"][1]

    assert task["bags"] == [], "a plain hunt has no bag"
    assert task["monsters"] == [("13,302", "10", ""), ("13,303", "5", "")]
    assert all(chance == "" for _, _, chance in task["monsters"])


def test_group_hunt_count_is_on_the_group_and_entries_carry_none():
    """15 kills across the group, not 15 per member."""
    task = quest(tasks=GROUP_HUNT)["tasks"][1]

    assert len(task["groups"]) == 1
    group = task["groups"][0]
    assert group["kills"] == "15"
    assert group["name"] == "@quest:301009"
    assert [m[0] for m in group["monsters"]] == ["13,302", "13,303"]
    assert all(kill == "" for _, kill, _ in group["monsters"])


def test_collect_bag_carries_the_item_and_count():
    task = quest(tasks=COLLECT)["tasks"][1]

    assert task["collections"] == ["409"]
    assert len(task["bags"]) == 1
    assert (task["bags"][0]["item"], task["bags"][0]["qty"]) == ("9106", "1")


REPEAT_FLAT_BAG = """
    <Task id="1">
      <Header><이름>반복Task</이름></Header>
      <Body>
        <아이템작성>
          <Flag아이템이름>@quest:270002</Flag아이템이름>
          <전달수량>10</전달수량>
          <아이콘지정>119</아이콘지정>
        </아이템작성>
        <몬스터지정>
          <몬스터지정><몬스터Id>13,302</몬스터Id><수여확률>100</수여확률></몬스터지정>
        </몬스터지정>
      </Body>
    </Task>
"""


def test_repeat_task_states_its_bag_flat_without_a_doubled_wrapper():
    """317 repeat tasks put the bag fields straight on the container.

    Requiring the doubled <아이템작성><아이템작성> shape drops every one of them,
    and a dropped bag reads as a task with no requirement at all.
    """
    task = quest(tasks=REPEAT_FLAT_BAG)["tasks"][1]

    assert len(task["bags"]) == 1
    assert task["bags"][0]["qty"] == "10"
    assert task["bags"][0]["flag"] == "@quest:270002"


def test_bags_are_kept_separate_when_a_task_has_several():
    """A per-task total would hide which entries fill which requirement."""
    two_bags = HUNT_DELIVER.replace("</Body>", """
        <아이템작성>
          <아이템작성>
            <전달수량>3</전달수량>
            <몬스터지정><몬스터지정><몬스터Id>13,999</몬스터Id><수여확률>50</수여확률></몬스터지정></몬스터지정>
          </아이템작성>
        </아이템작성>
      </Body>""")
    task = quest(tasks=two_bags)["tasks"][1]

    assert [b["qty"] for b in task["bags"]] == ["8", "3"]
    assert [len(b["monsters"]) for b in task["bags"]] == [2, 1]


# ---------------------------------------------------------------------------
# Sentinels: two encodings
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["99,99", "99,9999"])
def test_both_sentinel_encodings_mark_a_quest_disabled(value):
    """60 quests use the first form and 17 the second.

    Recognizing only 99,99 reports those 17 as live, so a trim that references
    one of them reads as safe when it is not.
    """
    q = quest(header_extra=f"<선행퀘스트><선행퀘스트><퀘스트Id>{value}</퀘스트Id></선행퀘스트></선행퀘스트>")

    assert q["prereqs"] == [value]
    assert q["sentinel"] is True
    assert value in SENTINEL_PREREQS


def test_a_real_prerequisite_is_not_a_sentinel():
    q = quest(header_extra="<선행퀘스트><선행퀘스트><퀘스트Id>13,5</퀘스트Id></선행퀘스트></선행퀘스트>")

    assert q["sentinel"] is False


def test_a_sentinel_alongside_a_real_prerequisite_is_not_disabled():
    q = quest(header_extra=(
        "<선행퀘스트><선행퀘스트><퀘스트Id>99,99</퀘스트Id></선행퀘스트>"
        "<선행퀘스트><퀘스트Id>13,5</퀘스트Id></선행퀘스트></선행퀘스트>"
    ))

    assert len(q["prereqs"]) == 2
    assert q["sentinel"] is False, "disabling requires the sentinel to be the only gate"


def test_substring_matching_would_be_wrong():
    """A raw grep for 99,9999 hits 563 files where the structural answer is 17.

    546 of those are NPCId values that merely contain the digits. This test
    holds the shape that makes the difference concrete.
    """
    q = quest(tasks="""
    <Task id="1">
      <Header><이름>방문Task</이름></Header>
      <Body><방문그룹><방문그룹><NPCId>99,9999</NPCId></방문그룹></방문그룹></Body>
    </Task>
""")

    assert q["sentinel"] is False, "an NPCId is not a prerequisite"
    assert q["prereqs"] == []
    assert q["tasks"][1]["visits"] == ["99,9999"]


# ---------------------------------------------------------------------------
# Label versus body
# ---------------------------------------------------------------------------

def test_a_task_whose_body_matches_its_label_is_not_a_finding():
    for tasks in (HUNT_DELIVER, PLAIN_HUNT, GROUP_HUNT, COLLECT):
        task = quest(tasks=tasks)["tasks"][1]
        assert task_body_mismatch(task) is None, task["type"]


def test_a_label_without_its_body_container_is_a_finding():
    """Never guess from a label.

    A 사냥Task with no 몬스터지정 has no targets to count, and silently treating
    that as a hunt with zero targets buries a data error inside a feasibility
    verdict.
    """
    task = quest(tasks="""
    <Task id="1">
      <Header><이름>사냥Task</이름></Header>
      <Body><저널Text>x</저널Text></Body>
    </Task>
""")["tasks"][1]

    assert task_body_mismatch(task) == "몬스터지정"


def test_an_unknown_task_type_is_unconstrained():
    task = quest(tasks="""
    <Task id="1">
      <Header><이름>미지Task</이름></Header>
      <Body><저널Text>x</저널Text></Body>
    </Task>
""")["tasks"][1]

    assert task_body_mismatch(task) is None


# ---------------------------------------------------------------------------
# Corpus tier: the parser describes the real quest corpus at the baseline
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def corpus_quests(baseline, datasheet_dir):
    """Every quest that exists at the pinned baseline, parsed."""
    names = sorted(p.name for p in (datasheet_dir / "QuestData").glob("*.quest"))
    out = {}
    for name in names:
        text = baseline.read(f"QuestData/{name}")
        if text is None:
            continue  # added after the baseline
        model = parse_quest(text)
        if model is not None:
            out[name] = model
    return out


@pytest.mark.corpus
def test_the_baseline_holds_2707_of_the_2710_quest_files(corpus_quests, datasheet_dir):
    """The three missing ones are patch-002 additions, absent at the baseline."""
    on_disk = list((datasheet_dir / "QuestData").glob("*.quest"))

    assert len(on_disk) == 2710
    assert len(corpus_quests) == 2707


@pytest.mark.corpus
def test_both_sentinel_encodings_are_in_live_use(corpus_quests):
    import collections

    counts = collections.Counter(
        p for q in corpus_quests.values() for p in q["prereqs"] if p in SENTINEL_PREREQS
    )
    disabled = sum(1 for q in corpus_quests.values() if q["sentinel"])

    assert counts["99,99"] == 55
    assert counts["99,9999"] == 17, "the encoding a single-sentinel check would miss"
    assert disabled == 72


@pytest.mark.corpus
def test_every_hunt_family_task_yields_its_count(corpus_quests):
    """No hunt-shaped task loses its requirement to a wrapper-shape assumption."""
    bags = groups = plain = 0
    for q in corpus_quests.values():
        for task in q["tasks"].values():
            if task["bags"]:
                bags += 1
            if task["groups"]:
                groups += 1
            if task["type"] == "사냥Task" and task["monsters"]:
                plain += 1

    assert bags == 1095, "582 hunt-deliver + 317 repeat + 196 collect"
    assert groups == 189
    assert plain == 1079, "every 사냥Task at the baseline carries monster entries"


@pytest.mark.corpus
def test_group_hunt_counts_live_on_the_group_not_the_entries(corpus_quests):
    groups = [g for q in corpus_quests.values()
              for t in q["tasks"].values() for g in t["groups"]]

    assert all(kill == "" for g in groups for _, kill, _ in g["monsters"]), \
        "no group entry carries its own kill count"
    assert sum(1 for g in groups if g["kills"]) == len(groups), \
        "every group states its count"


@pytest.mark.corpus
def test_the_corpus_carries_exactly_six_label_body_mismatches(corpus_quests):
    """Real data errors, not parser noise.

    Two 찔러준아이템전달 tasks state no 전달수량 and four 아이템전달 tasks state no
    아이템지정. A check that trusted the label would report each as a delivery of
    zero items rather than as broken data.
    """
    found = sorted(
        (name, task["id"], task["type"], task_body_mismatch(task))
        for name, q in corpus_quests.items()
        for task in q["tasks"].values()
        if task_body_mismatch(task)
    )

    assert found == [
        ("003837.quest", 4, "찔러준아이템전달Task", "전달수량"),
        ("005034.quest", 3, "찔러준아이템전달Task", "전달수량"),
        ("017217.quest", 4, "아이템전달Task", "아이템지정"),
        ("018208.quest", 6, "아이템전달Task", "아이템지정"),
        ("050501.quest", 6, "아이템전달Task", "아이템지정"),
        ("061502.quest", 5, "아이템전달Task", "아이템지정"),
    ]


@pytest.mark.corpus
def test_task_verb_distribution_at_the_baseline(corpus_quests):
    """The measurable form of "the zone feels repetitive"."""
    import collections

    verbs = collections.Counter(
        task["type"] for q in corpus_quests.values() for task in q["tasks"].values()
    )

    assert verbs.most_common(9) == [
        ("방문Task", 3335), ("사냥Task", 1079), ("사냥전달Task", 582),
        ("PC이동Task", 489), ("반복Task", 317), ("아이템전달Task", 294),
        ("찔러준아이템전달Task", 204), ("채집Task", 196), ("그룹사냥Task", 189),
    ]
