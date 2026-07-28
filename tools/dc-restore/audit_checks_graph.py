"""Graph integrity: inbound references, hidden gates and client reward parity.

Three checks, each born from a defect the reward checks cannot see because the
defect is not in the reward, it is in what points at the quest.

  references    Retiring quest 1323 would have orphaned 1324, whose prerequisite
                pointed straight at it; retiring 1318 was free, because nothing
                in the entire corpus referenced it. Nothing short of a sweep of
                every reference family, in both id encodings, can tell those two
                cases apart, and the trimming wave had to answer it 5 times.
  hidden-gates  Quests 1326 and 1330 carried 진행퀘스트 = 1305,1 and granted two
                pieces of a four piece set. Finishing 1305 first closed the gate
                and stranded the set permanently. No MCP tool reports this
                field, so it was invisible until a player hit it.
  client-parity QuestCompensationData was not client-synced, so the quest log
                advertised stale rewards (17 zone-13 rows showed exp and gold
                but no items) while the payouts were correct. It recurs per
                zone by design: sync-config.yaml needs a pair per zone or the
                sync skips it silently.

Three encodings, all measured against the corpus rather than assumed, because
getting one wrong makes a whole family resolve to nothing and report clean:

  PAIR         "13,46" means quest 1346. Used by 선행퀘스트 (1097 of 1111 values
               resolve as a pair against the quest corpus, 123 as a global id)
               and by 연결퀘스트 (54 of 56 versus 2).
  GLOBAL_HEAD  "1305,1" means quest 1305, task 1. Used by 진행퀘스트, and it is
               the trap: it LOOKS like the pair form and is not. All 37 values
               resolve as a global id and none as a pair, and all 37 task
               halves name a task that exists on the global-read target.
  GLOBAL_LIST  every non-quest family carries plain global ids, and one value
               corpus-wide is a comma LIST of them (NpcData_415 hides on
               "41501,41502,...,41508"; all 8 tokens are real quests, so
               reading it as a pair loses 8 edges and invents a bogus one).

Sentinels have two encodings, both in dclib.SENTINEL_PREREQS. They must be found
STRUCTURALLY. A raw substring search for "99,9999" matches 563 quest files at the
pinned baseline; exactly 17 of them are disabled. The other 546 carry it as an
NPC reference ("hunting zone 99, template 9999") in an NPCId or 대상NPC지정
element, which is a different field meaning a different thing.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from auditlib import Corpus, Finding, Scope, check
from dclib import (
    SENTINEL_PREREQS,
    comp_reward_key,
    index_client_comp,
    index_comp_file,
    is_regional_variant,
    load_references,
    parse_root,
    reforged_dir,
    strip_ns,
)

# ---------------------------------------------------------------------------
# Id encodings
# ---------------------------------------------------------------------------

PAIR = "pair"                # "13,46"   -> 1346          (hz, local)
GLOBAL_HEAD = "global-head"  # "1305,1"  -> 1305          (questId, taskId)
GLOBAL_LIST = "global-list"  # "1346"    -> 1346, and "a,b,c" -> {a, b, c}


def quest_ids(value: str, form: str) -> set[int]:
    """Global quest ids a reference value denotes under one encoding.

    Never guess the encoding from the shape of the value: "1305,1" and "13,46"
    are the same shape and mean different quests. The family decides.
    """
    if not value:
        return set()
    parts = [p.strip() for p in value.strip().split(",")]
    if not parts or not all(p.isdigit() for p in parts):
        return set()
    if form == PAIR:
        if len(parts) != 2:
            return set()
        return {int(parts[0]) * 100 + int(parts[1])}
    if form == GLOBAL_HEAD:
        return {int(parts[0])}
    return {int(p) for p in parts}


# ---------------------------------------------------------------------------
# The reference families
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Edge:
    """One live reference into a quest."""

    target: int
    family: str
    source: str

    def __lt__(self, other: "Edge") -> bool:
        return (self.target, self.family, self.source) < (other.target, other.family, other.source)


@dataclass(frozen=True)
class AttrFamily:
    """A family that names its quest in an XML attribute."""

    family: str
    pattern: str
    attr: str
    form: str = GLOBAL_LIST


# Every non-quest family that can hold a quest live. Counts are the non-zero
# attribute occurrences measured at the pinned baseline 789fec28, recorded here
# as calibration only: the checks recount at runtime and the tests reprove them.
ATTR_FAMILIES: tuple[AttrFamily, ...] = (
    AttrFamily("workObject", "WorkObjectData*.xml", "isForQuestId"),        # 169
    AttrFamily("npcAppear", "NpcData_*.xml", "appearQuestId"),              # 934
    AttrFamily("npcHide", "NpcData_*.xml", "hideQuestId"),                  # 879
    AttrFamily("areaRequire", "AreaData/*.xml", "requireQuestId"),          # 10
    AttrFamily("dungeonDaily", "DungeonData_*.xml", "relatedDailyQuest"),   # 3
    AttrFamily("dungeonScenario", "DungeonData_*.xml", "scenarioQuestId"),  # 1
)

# DungeonData Condition types whose value is a quest. Both were missing from the
# first survey of this surface, as was the questId attribute below it.
DUNGEON_CONDITIONS = {"progressQuest": "dungeonProgressQuest",   # 51
                      "completeQuest": "dungeonCompleteQuest"}   # 46

# Quest completion in AchievementList. templateId 1020 is NOT this: it is item
# possession, proved by its own data (its 100 value2s are all item ids and none
# is a quest id, its value1 is the constant 1 and its type is "count", while
# 4012 carries type "check" and a lone value1 that resolves into the quest id
# space 244 times out of 286). A trimming-wave safety claim was once measured
# against 1020 and got an answer about nothing.
ACHIEVEMENT_QUEST_TEMPLATE = "4012"
ACHIEVEMENT_ITEM_TEMPLATE = "1020"

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_INPROGRESS_TAG = "진행퀘스트"
_QUESTID_EL = re.compile(r"<(\w+)\b[^>]*?\bquestId=\"([^\"]*)\"")
_CONDITION_EL = re.compile(r"<Condition\b([^>]*?)/?>")
_ATTRS = re.compile(r'(\w+)="([^"]*)"')

_EDGES_ATTR = "_graph_reference_edges"
_GATES_ATTR = "_graph_inprogress_gates"


def _live_text(corpus: Corpus, relpath: str) -> str | None:
    """File text with comment blocks removed.

    A reference inside an XML comment is inert: the server never loads it. The
    dungeon 9037 incident was the mirror image of this (content that grep saw
    and the server did not), and counting a commented-out reference as live
    would report a defect nobody can observe in game.
    """
    text = corpus.read(relpath)
    if text is None:
        return None
    return _COMMENT.sub("", text) if "<!--" in text else text


def _attr_values(text: str, attr: str) -> set[str]:
    return set(re.findall(rf'\b{attr}="([^"]*)"', text))


def _quest_relpaths(corpus: Corpus) -> list[str]:
    return corpus.glob("QuestData/*.quest")


def in_progress_gates(corpus: Corpus) -> dict[int, list[str]]:
    """{quest id: raw 진행퀘스트 values} for every quest carrying the gate.

    Parsed structurally. The substring prefilter only decides which files are
    worth an XML parse, never whether a gate exists.
    """
    cached = getattr(corpus, _GATES_ATTR, None)
    if cached is not None:
        return cached
    out: dict[int, list[str]] = {}
    for relpath in _quest_relpaths(corpus):
        text = corpus.read(relpath)
        if text is None or _INPROGRESS_TAG not in text:
            continue
        try:
            root = parse_root(text)
        except Exception:
            continue  # malformed source is a data finding, never a crash
        gid_raw = root.get("id")
        if not gid_raw or not gid_raw.isdigit():
            continue
        values = [(el.text or "").strip() for el in root.iter()
                  if strip_ns(el.tag) == _INPROGRESS_TAG and (el.text or "").strip()]
        if values:
            out[int(gid_raw)] = sorted(values)
    setattr(corpus, _GATES_ATTR, out)
    return out


def reference_edges(corpus: Corpus) -> list[Edge]:
    """Every live quest reference in the corpus, deduplicated and sorted.

    Evidence is corpus-wide on purpose. A zone-scoped read cannot prove that
    retiring a quest orphans nothing, which is the only question this check
    exists to answer.
    """
    cached = getattr(corpus, _EDGES_ATTR, None)
    if cached is not None:
        return cached

    edges: set[Edge] = set()

    # Quest to quest. Two encodings live side by side in one file.
    for gid, quest in corpus.quests.items():
        source = f"quest-{gid}"
        for raw in quest["prereqs"]:
            if raw in SENTINEL_PREREQS:
                continue  # a sentinel points at no quest; that is the point
            for target in quest_ids(raw, PAIR):
                edges.add(Edge(target, "prereq", source))
        link = quest.get("link", "")
        if link and link != "1,1":  # "1,1" is the no-successor idiom
            for target in quest_ids(link, PAIR):
                edges.add(Edge(target, "link", source))
    for gid, values in in_progress_gates(corpus).items():
        for raw in values:
            for target in quest_ids(raw, GLOBAL_HEAD):
                edges.add(Edge(target, "inProgress", f"quest-{gid}"))

    # Attribute families.
    for fam in ATTR_FAMILIES:
        for relpath in corpus.glob(fam.pattern):
            if is_regional_variant(relpath.rsplit("/", 1)[-1]):
                continue
            text = _live_text(corpus, relpath)
            if text is None:
                continue
            name = relpath.rsplit("/", 1)[-1]
            for value in _attr_values(text, fam.attr):
                for target in quest_ids(value, fam.form):
                    if target:
                        edges.add(Edge(target, fam.family, name))

    # DungeonData. The questId attribute is the largest surface here and it is
    # spread over more than one element, so the element name is read from the
    # match rather than enumerated: a new element carrying questId joins the
    # sweep automatically instead of being silently dropped.
    for relpath in corpus.glob("DungeonData_*.xml"):
        name = relpath.rsplit("/", 1)[-1]
        if is_regional_variant(name):
            continue
        text = _live_text(corpus, relpath)
        if text is None:
            continue
        for element, value in _QUESTID_EL.findall(text):
            for target in quest_ids(value, GLOBAL_LIST):
                if target:
                    edges.add(Edge(target, f"dungeon{element}", name))
        for raw in _CONDITION_EL.findall(text):
            attrs = dict(_ATTRS.findall(raw))
            family = DUNGEON_CONDITIONS.get(attrs.get("type", ""))
            if family is None:
                continue
            for target in quest_ids(attrs.get("value", ""), GLOBAL_LIST):
                if target:
                    edges.add(Edge(target, family, name))

    # Achievements. Base file only; the six regional twins add one non-quest
    # condition between them and would otherwise double-count every edge.
    for relpath in corpus.glob("AchievementList*.xml"):
        if is_regional_variant(relpath.rsplit("/", 1)[-1]):
            continue
        text = _live_text(corpus, relpath)
        if text is None:
            continue
        try:
            root = parse_root(text)
        except Exception:
            continue
        for ach in root.iter():
            if strip_ns(ach.tag) != "Achievement":
                continue
            aid = ach.get("id", "?")
            for cond in ach.iter():
                if strip_ns(cond.tag) != "Condition":
                    continue
                if cond.get("templateId") != ACHIEVEMENT_QUEST_TEMPLATE:
                    continue
                for target in quest_ids(cond.get("value1", ""), GLOBAL_LIST):
                    if target:
                        edges.add(Edge(target, "achievement", f"achievement-{aid}"))

    result = sorted(edges)
    setattr(corpus, _EDGES_ATTR, result)
    return result


def inbound_map(corpus: Corpus) -> dict[int, list[Edge]]:
    """{quest id: inbound edges}."""
    out: dict[int, list[Edge]] = {}
    for edge in reference_edges(corpus):
        out.setdefault(edge.target, []).append(edge)
    return out


# ---------------------------------------------------------------------------
# references
# ---------------------------------------------------------------------------

@check("references", "graph-integrity",
       "A live reference into a sentinel-disabled quest, over every reference "
       "family in both id encodings. This is the exact defect class that "
       "trimming introduces.")
def check_references(corpus: Corpus, scope: Scope) -> list[Finding]:
    """Disabling a quest is only safe when nothing points at it.

    The trimming wave had to answer this 5 times over. Retiring 1323 would have
    orphaned 1324, whose prerequisite named it directly; retiring 1318 was free
    because nothing anywhere referenced it. The two look identical in a quest
    file and differ only in the corpus-wide inbound edge map.

    One finding per edge, not per quest: the waiver key then names the exact
    file to fix, and a second reference appearing later is a new finding rather
    than a silent change to an already-waived one.
    """
    findings: list[Finding] = []
    inbound = inbound_map(corpus)
    for gid, quest in sorted(scope.subject_quests(corpus).items()):
        if not quest.get("sentinel"):
            continue
        for edge in inbound.get(gid, []):
            findings.append(Finding(
                severity="high",
                check="references",
                subject=f"quest-{gid}",
                detail=f"{edge.family}:{edge.source}",
                message=(f"disabled quest is still referenced by {edge.source} "
                         f"via {edge.family}"),
                evidence={"quest": gid, "family": edge.family, "source": edge.source},
            ))
    return findings


# ---------------------------------------------------------------------------
# hidden-gates
# ---------------------------------------------------------------------------

@check("hidden-gates", "graph-integrity",
       "A quest gated on another quest being IN PROGRESS (진행퀘스트). High when "
       "the gated quest also grants equipment: that is the permanently missable "
       "set case.")
def check_hidden_gates(corpus: Corpus, scope: Scope) -> list[Finding]:
    """An in-progress gate closes forever the moment the gating quest completes.

    Quests 1326 and 1330 each carried 진행퀘스트 = 1305,1 and granted a piece of
    the same four piece set. A player who finished 1305 before picking them up
    lost those pieces permanently, with no error and no way back. A prerequisite
    is a door you walk through; an in-progress gate is a door that locks behind
    you, and nothing in the quest log says so.

    The gate is legitimate for escort and timing quests, so the bare gate is
    medium. What makes it high is the conjunction with an equipment grant, since
    that is the case where the loss is permanent and irreplaceable.
    """
    findings: list[Finding] = []
    gates = in_progress_gates(corpus)
    subject = scope.subject_quests(corpus)
    for gid in sorted(gates):
        if gid not in subject:
            continue
        equipment = _granted_equipment(corpus, gid)
        for raw in gates[gid]:
            targets = sorted(quest_ids(raw, GLOBAL_HEAD))
            target = targets[0] if targets else 0
            if equipment:
                message = (f"gated on quest {target} being in progress while granting "
                           f"{len(equipment)} equipment item(s): finishing {target} first "
                           f"strands them permanently")
            else:
                message = f"gated on quest {target} being in progress ({raw})"
            findings.append(Finding(
                severity="high" if equipment else "medium",
                check="hidden-gates",
                subject=f"quest-{gid}",
                detail=str(target),
                message=message,
                evidence={"quest": gid, "gate": raw, "gates_on": target,
                          "equipment": equipment},
            ))
    return findings


def _granted_equipment(corpus: Corpus, gid: int) -> list[int]:
    """Distinct real equipment ids a quest grants.

    The allow-list in dclib matters here: combat_type.startswith("EQUIP") also
    matches roughly 4,100 cosmetic and underwear items, which would escalate
    every costume reward to high.
    """
    payload = corpus.rewards.get(gid)
    if not payload:
        return []
    out: set[int] = set()
    for template, _qty, _cls in payload["items"]:
        if not template.isdigit():
            continue
        info = corpus.items.get(int(template))
        if info is not None and info.is_equipment:
            out.add(int(template))
    return sorted(out)


# ---------------------------------------------------------------------------
# client-parity
# ---------------------------------------------------------------------------

def client_comp_dir() -> Path | None:
    """The client QuestCompensationData shard folder, or None when unavailable.

    Resolved from the client_datacenter key in reforged/.references, which is
    gitignored: a clean clone has no client at all, and this check must degrade
    rather than fail there.
    """
    try:
        refs = load_references()
    except Exception:
        return None
    raw = refs.get("client_datacenter")
    if not raw:
        return None
    path = Path(raw) / "QuestCompensationData"
    return path if path.is_dir() else None


def sync_config_path() -> Path:
    return reforged_dir() / "config" / "sync-config.yaml"


_MAPPED_ZONE = re.compile(r"QuestCompensationData_(\d+)\.xml")


def synced_zones(path: Path) -> set[int] | None:
    """Zones with a QuestCompensationData sync pair, or None when unreadable.

    None and the empty set mean different things: unreadable config cannot
    prove a zone is unmapped, while a readable config with no pairs proves
    every zone is.
    """
    if not path.exists():
        return None
    try:
        import yaml

        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    entity = ((raw.get("entities") or {}).get("QuestCompensationData") or {})
    mapping = entity.get("source_mapping") or {}
    if not isinstance(mapping, dict):
        return None
    return {int(m.group(1)) for key in mapping for m in [_MAPPED_ZONE.search(str(key))] if m}


@check("client-parity", "reward-integrity",
       "Server QuestCompensationData rows against the client shards, plus "
       "whether sync-config.yaml carries a pair for the zone at all.")
def check_client_parity(corpus: Corpus, scope: Scope) -> list[Finding]:
    """The quest log reads the client shards; the payout reads the server.

    They disagreed silently for as long as this family went unsynced: 17 zone-13
    rows advertised exp and gold with no items while the payouts were correct,
    because the class-filtered Item rows only ever existed server-side. It was
    the single most impactful defect of the session that produced this tool, and
    it recurs per zone by design, since sync-config.yaml needs an explicit pair
    per zone and skips the rest without a word.

    Degrades to one informational finding when the client is unavailable. A
    clean clone has no client DataCenter, and a check that cannot run must say
    so: returning nothing would read as a clean parity result.
    """
    comp_dir = client_comp_dir()
    if comp_dir is None:
        return [Finding(
            severity="info",
            check="client-parity",
            subject="client",
            message=("client DataCenter unavailable (client_datacenter in "
                     ".references is unset, or its QuestCompensationData folder "
                     "is missing), so server-to-client parity was NOT checked"),
            evidence={},
        )]

    client = index_client_comp(comp_dir)
    mapped = synced_zones(sync_config_path())

    findings: list[Finding] = []
    for hz in sorted(_subject_zones(corpus, scope)):
        text = corpus.read(f"CompensationData/QuestCompensationData_{hz}.xml")
        if text is None:
            continue  # a zone with no reward table has nothing to sync
        try:
            server = index_comp_file(text)
        except Exception:
            findings.append(Finding(
                severity="info", check="client-parity", subject=f"zone-{hz}",
                detail="unparsable",
                message=f"server QuestCompensationData_{hz}.xml could not be parsed",
                evidence={"zone": hz}))
            continue
        rows = {qid: v for qid, v in client.items() if qid // 100 == hz}

        for qid in sorted(set(server) - set(rows)):
            findings.append(Finding(
                severity="high", check="client-parity", subject=f"quest-{qid}",
                detail="server-only",
                message=("reward row exists on the server and in no client shard, so "
                         "the quest log shows nothing for it"),
                evidence={"quest": qid, "zone": hz, "kind": "server-only"}))

        for qid in sorted(set(rows) - set(server)):
            findings.append(Finding(
                severity="high", check="client-parity", subject=f"quest-{qid}",
                detail="client-stale",
                message=("client shard carries a reward row the server does not, so the "
                         "quest log advertises a reward that is never paid"),
                evidence={"quest": qid, "zone": hz, "kind": "client-orphan"}))

        for qid in sorted(set(server) & set(rows)):
            if comp_reward_key(server[qid]) == comp_reward_key(rows[qid]):
                continue
            findings.append(Finding(
                severity="high", check="client-parity", subject=f"quest-{qid}",
                detail="client-stale",
                message=("client shard disagrees with the server reward, so the quest log "
                         "advertises something other than the payout"),
                evidence={"quest": qid, "zone": hz, "kind": "stale"}))

        if mapped is None:
            findings.append(Finding(
                severity="info", check="client-parity", subject=f"zone-{hz}",
                detail="config-unreadable",
                message=("config/sync-config.yaml could not be read, so it is unknown "
                         "whether this zone is mapped for client sync"),
                evidence={"zone": hz}))
        elif hz not in mapped and server:
            # A zone with no rows yet has nothing to lose; the finding appears
            # the moment the first reward row is authored, which is when it
            # starts mattering.
            anchor = _anchor_quest(scope, server)
            findings.append(Finding(
                severity="high", check="client-parity", subject=f"zone-{hz}",
                detail="unmapped",
                message=(f"{len(server)} server reward row(s) but no QuestCompensationData "
                         f"pair in sync-config.yaml, so every edit here skips the client "
                         f"silently"),
                evidence={"quest": anchor, "zone": hz, "rows": len(server),
                          "kind": "unmapped"}))
    return findings


def _subject_zones(corpus: Corpus, scope: Scope) -> set[int]:
    """Zones to compare: the subject scope, or every zone with a reward file."""
    if scope.zones is not None:
        return set(scope.zones)
    zones: set[int] = set()
    for relpath in corpus.glob("CompensationData/QuestCompensationData_*.xml"):
        stem = relpath.rsplit("_", 1)[-1]
        if stem.endswith(".xml") and stem[:-4].isdigit():
            zones.add(int(stem[:-4]))
    return zones


def _anchor_quest(scope: Scope, server: dict) -> int | None:
    """A quest id to hang a zone-level finding on, for the NEW label only.

    A zone-level condition belongs to no single quest, but migrate's one-line
    summary counts only findings whose evidence names a quest the caller
    touched. Anchoring on a touched quest when there is one is what makes an
    unmapped zone visible at the moment someone edits it; with no findings
    scope every finding is new anyway, so the anchor changes nothing.
    """
    if scope.new_quests is None:
        return None
    touched = sorted(set(server) & scope.new_quests)
    return touched[0] if touched else None
