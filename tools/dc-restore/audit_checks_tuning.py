"""Tuning checks: can the objective be met, and is the reward aimed at the right lane.

Three incidents, all individually valid and collectively wrong.

  feasibility      Quest 1348 asked for 8 delivered items and the whole zone held
                   10 credit mobs, at 90 and 17 percent grant rates: a full clear
                   yields 6.08 of the 8 required. audit_quest_gates called it OK
                   because every reference resolved; testers called it the worst
                   quest in the zone. Nothing was broken, the arithmetic was.

  level-coherence  Quests 1336 and 1337 gate at level 7 behind prerequisite 1335,
                   which gates at level 8, so the chain reads backwards. In the
                   same zone, items sat two and three levels above the quest that
                   granted them.

  lane             Story quest 1305 paid out the entire level-7 First Expedition
                   set in one go. Story quests own lore progression; zone quests
                   own power progression. Mixing them makes the zone quests
                   pointless and the story quest the only one anybody runs.

Every number in the output is measured at run time. The check reports the
arithmetic, not a verdict, because the remedy depends on which side is wrong:
widen the accept list (more credit mobs per objective) or change the spawns.

Two models live here rather than in dclib, because dclib does not carry them:

  * The spawn census. dclib.territory_spawns returns one row per <Npc> element
    and drops both `spawnCount` and the Territory `type` attribute, so summing
    its rows undercounts (zone 13 templates 302 and 303 are 14 rows but 22
    spawns) and cannot separate a standing population from a quest-conditional
    or event-gated one.
  * The third disable-sentinel encoding. dclib.SENTINEL_PREREQS lists 99,99 and
    99,9999; the corpus also uses 999,99 on 122 prerequisite references, which
    resolves to a real placeholder quest and therefore does NOT look dangling.
    Level coherence treats any prerequisite gated at level 99 or above as a
    sentinel, which covers all three encodings without enumerating them.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from auditlib import Corpus, Finding, Scope, check, item_label
from dclib import (
    collection_territory_spawns,
    npc_template_ids,
    parse_pair,
    strip_ns,
    task_body_mismatch,
)

# Territory@type, corpus-verified: normal / quest / event / policy / questStart,
# plus exactly one element with the attribute blank. Standing population is the
# only kind guaranteed to be on the map when the player arrives; the rest are
# reported in their own columns rather than filtered out, because a
# quest-conditional territory is frequently the exactly-right population when
# the condition IS the audited quest.
STANDING_TYPES = frozenset({"normal", "policy", ""})
CONDITIONAL_TYPES = frozenset({"quest", "questStart"})
EVENT_TYPES = frozenset({"event"})

# A prerequisite gated at or above this level can never be satisfied: it is a
# disable sentinel however it is spelled. Comparing level gates against one says
# nothing about design, so those edges are skipped.
UNREACHABLE_LEVEL = 99

# Island of Dawn deliberately grants items ahead of the quest's own gate: at the
# pinned baseline 42 of its equipment grants sit exactly 1 or 2 levels ahead. A
# margin below 2 therefore reports the zone's design as a defect. Configurable
# because the calibration is regional.
DEFAULT_LEVEL_MARGIN = 2

# Repeat tasks are OUT of scope for the feasibility verdict. A 반복Task is built
# to be run again, so needing more than one clear's worth of population is its
# design rather than a defect, and firing on all 317 of them would be pure
# noise. They stay IN scope for the data-error half: a dangling hunt target is
# broken whether or not the task repeats.
VERDICT_TASK_TYPES = frozenset({"사냥Task", "사냥전달Task", "그룹사냥Task", "채집Task"})
HUNT_TASK_TYPES = frozenset({"사냥Task", "사냥전달Task", "그룹사냥Task", "반복Task"})


# ---------------------------------------------------------------------------
# Population model
# ---------------------------------------------------------------------------

def _cache(corpus: Corpus, name: str) -> dict:
    """Per-corpus memo. Evidence is read once per run, never once per quest."""
    store = getattr(corpus, "_tuning_cache", None)
    if store is None:
        store = {}
        corpus._tuning_cache = store
    return store.setdefault(name, {})


def parse_territory_population(text: str) -> dict[int, dict[str, int]]:
    """{template id: {territory type: summed spawnCount}} for one TerritoryData file.

    Never deduplicated by coordinate. Groups 1300022 and 1300060 sit about 11
    units apart and both spawn, so collapsing near-identical positions halves a
    real population and turns a healthy zone into a reported famine.
    """
    out: dict[int, dict[str, int]] = {}
    root = ET.fromstring(text.encode("utf-8"))
    for territory in root.iter():
        if strip_ns(territory.tag) != "Territory":
            continue
        kind = territory.get("type", "")
        for npc in territory.iter():
            if strip_ns(npc.tag) != "Npc":
                continue
            raw = npc.get("npcTemplateId", "")
            if not raw.isdigit():
                continue
            count = npc.get("spawnCount", "")
            count = int(count) if count.isdigit() else 0
            bucket = out.setdefault(int(raw), {})
            bucket[kind] = bucket.get(kind, 0) + count
    return out


def zone_population(corpus: Corpus, hz: int) -> dict[int, dict[str, int]] | None:
    """Spawn census for a hunting zone, or None when it has no TerritoryData."""
    memo = _cache(corpus, "population")
    if hz not in memo:
        text = corpus.read(f"TerritoryData_{hz}.xml")
        try:
            memo[hz] = parse_territory_population(text) if text is not None else None
        except ET.ParseError:
            memo[hz] = None  # malformed source is a data finding, never a crash
    return memo[hz]


def zone_templates(corpus: Corpus, hz: int) -> dict[int, str] | None:
    """{template id: name} for a zone, or None when it has no NpcData."""
    memo = _cache(corpus, "templates")
    if hz not in memo:
        text = corpus.read(f"NpcData_{hz}.xml")
        memo[hz] = npc_template_ids(text) if text is not None else None
    return memo[hz]


def dungeon_zones(corpus: Corpus) -> set[int]:
    """Hunting zones that are dungeon continents.

    Their monsters are placed by dungeon event scripts rather than by standing
    territories, so a territory census understates them by design and a
    shortfall computed from one means nothing.
    """
    memo = _cache(corpus, "meta")
    if "dungeons" not in memo:
        found: set[int] = set()
        for relpath in corpus.glob("DungeonData_*.xml"):
            stem = relpath.rsplit("/", 1)[-1][len("DungeonData_"):-len(".xml")]
            if stem.isdigit():
                found.add(int(stem))
        memo["dungeons"] = found
    return memo["dungeons"]


@dataclass(frozen=True)
class Availability:
    """How many of one target the zone holds, split by territory kind."""

    ref: str
    status: str                 # ok / dangling / not-evaluable / unparsable
    standing: int = 0
    conditional: int = 0
    event: int = 0
    name: str = ""

    @property
    def total(self) -> int:
        return self.standing + self.conditional + self.event

    def as_dict(self) -> dict:
        return {"target": self.ref, "name": self.name, "status": self.status,
                "standing": self.standing, "conditional": self.conditional,
                "event": self.event, "total": self.total}


def availability(corpus: Corpus, ref: str) -> Availability:
    """Population of one hunt target, by the zone named in its own pair ref."""
    pair = parse_pair(ref)
    if not pair:
        return Availability(ref, "unparsable")
    hz, template = pair
    if hz in dungeon_zones(corpus):
        return Availability(ref, "not-evaluable")
    templates = zone_templates(corpus, hz)
    if templates is None or template not in templates:
        return Availability(ref, "dangling")
    census = (zone_population(corpus, hz) or {}).get(template, {})
    standing = sum(n for kind, n in census.items() if kind in STANDING_TYPES)
    conditional = sum(n for kind, n in census.items() if kind in CONDITIONAL_TYPES)
    event = sum(n for kind, n in census.items() if kind in EVENT_TYPES)
    other = sum(n for kind, n in census.items()
                if kind not in STANDING_TYPES | CONDITIONAL_TYPES | EVENT_TYPES)
    return Availability(ref, "ok", standing + other, conditional, event,
                        templates.get(template, ""))


# ---------------------------------------------------------------------------
# Objective model: where the count lives differs by task shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Objective:
    """One requirement inside a task: a count and the targets that satisfy it."""

    slot: str                              # stable within the task, for the key
    required: int | None
    targets: tuple[tuple[str, float], ...]  # (monster ref, grant rate 0..1)
    rated: bool                            # whether grant rates apply at all


def _rate(raw: str) -> float:
    """수여확률 as a fraction. Absent means every kill grants."""
    if not raw:
        return 1.0
    try:
        return float(raw) / 100.0
    except ValueError:
        return 1.0


def _count(raw: str) -> int | None:
    return int(raw) if raw.isdigit() else None


def _level(quest: dict, field: str) -> int | None:
    raw = quest.get(field, "")
    return int(raw) if raw.isdigit() else None


def task_objectives(task: dict) -> list[Objective]:
    """Requirements of a task, reading each count from where its shape keeps it.

    The three hunt shapes disagree, and reading the wrong one is silent:

      사냥Task      count is PER MONSTER ENTRY (사냥마리수). 1,079 tasks, no
                    grant rates anywhere in the corpus.
      사냥전달Task  count is PER BAG (전달수량), never per entry; the rates are
                    per entry inside the bag. All 990 bag entries carry one.
      그룹사냥Task  count is PER GROUP; the 1,527 group entries carry neither a
                    count nor a rate, so entries are alternative credit only.
    """
    kind = task.get("type", "")
    if kind == "사냥Task":
        return [
            Objective(f"m{ref}", _count(kill), ((ref, _rate(chance)),), False)
            for ref, kill, chance in task.get("monsters", [])
        ]
    if kind in ("사냥전달Task", "채집Task"):
        return [
            Objective(f"bag{i}", _count(bag["qty"]),
                      tuple((ref, _rate(chance)) for ref, _kill, chance in bag["monsters"]),
                      True)
            for i, bag in enumerate(task.get("bags", []))
        ]
    if kind == "그룹사냥Task":
        return [
            Objective(f"g{i}", _count(group["kills"]),
                      tuple((ref, 1.0) for ref, _kill, _chance in group["monsters"]),
                      False)
            for i, group in enumerate(task.get("groups", []))
        ]
    return []


def collection_continents(corpus: Corpus) -> set[int]:
    """Every continent id that ships a CollectionTerritory file."""
    memo = _cache(corpus, "meta")
    if "collection_continents" not in memo:
        found: set[int] = set()
        for relpath in corpus.glob("CollectionData/CollectionTerritory_*.xml"):
            stem = relpath.rsplit("/", 1)[-1][len("CollectionTerritory_"):]
            head = stem.split("_", 1)[0]
            if head.isdigit():
                found.add(int(head))
        memo["collection_continents"] = found
    return memo["collection_continents"]


def collect_availability(corpus: Corpus, collection_id: int, hz: int) -> tuple[int, list[dict]]:
    """Nodes available for a collection id in a zone, and the rows behind them.

    A zone ships several CollectionTerritory files for its map variants (zone 13
    has an ordinary and a "Death" phase holding the same 20 nodes). A player
    stands in one variant at a time, so availability is the MAXIMUM across
    files, not the sum, which would double every collect objective in the zone.

    The number is an UPPER BOUND. dclib.collection_territory_spawns counts
    <Spawn> candidate points, while the group's own spawnNum says how many of
    them are live at once (collection 409: 24 points, spawnNum 15). Over-reading
    availability makes the check silent where it should be loud, which is the
    safe direction for an advisory tool but is worth knowing when a collect
    objective looks fine and plays starved.
    """
    coll_dir = corpus.datasheet / "CollectionData"
    rows = collection_territory_spawns(coll_dir, collection_id, {hz})
    best = max((row["spawn_entries"] for row in rows), default=0)
    return best, rows


def collect_elsewhere(corpus: Corpus, collection_id: int, hz: int) -> list[dict]:
    """Rows for a collection id in every continent OTHER than the quest's own.

    A collect objective does not name the map it is farmed on, so the quest's
    zone is the only available assumption. It is sometimes wrong: quest 48922
    sits in zone 489 and collection 567 spawns only in 9123. Reporting that as
    starvation would be a lie about content that exists, so the corpus-wide read
    is what separates "nowhere" from "not here".
    """
    coll_dir = corpus.datasheet / "CollectionData"
    others = collection_continents(corpus) - {hz}
    return collection_territory_spawns(coll_dir, collection_id, others)


# ---------------------------------------------------------------------------
# feasibility
# ---------------------------------------------------------------------------

def _shortfall_finding(gid: int, task_id, obj: Objective, avail: list[Availability],
                       yield_total: float, yield_standing: float) -> Finding:
    parts = ", ".join(
        f"{a.ref}={a.total}" + (f" at {int(rate * 100)}%" if obj.rated else "")
        for a, (_ref, rate) in zip(avail, obj.targets)
    )
    return Finding(
        severity="medium",
        check="feasibility",
        subject=f"quest-{gid}",
        detail=f"t{task_id}:{obj.slot}",
        message=(f"needs {obj.required}, a full clear of the available population "
                 f"yields {yield_total:.2f} ({parts}); "
                 f"remedy: widen the accept list or raise the spawn count"),
        evidence={"quest": gid, "task": task_id, "slot": obj.slot,
                  "required": obj.required,
                  "expected_yield": round(yield_total, 2),
                  "expected_yield_standing": round(yield_standing, 2),
                  "targets": [a.as_dict() for a in avail]},
    )


@check("feasibility", "tuning",
       "Expected yield from a full clear of the available population against the "
       "required count, with the count read from where each task shape keeps it.")
def check_feasibility(corpus: Corpus, scope: Scope) -> list[Finding]:
    """Quest 1348 asked for 8 items from a population of 10 at 90 and 17 percent.

    That is 6.08 expected from a full clear of the zone, and no reference-level
    gate can see it: every id resolved, every rate was a legal number. The check
    exists to make the arithmetic visible, so it reports the numbers and both
    remedies rather than a verdict.

    Repeat tasks are excluded from the verdict and included in the data-error
    sweep; see VERDICT_TASK_TYPES for why.
    """
    findings: list[Finding] = []

    for gid, quest in sorted(scope.subject_quests(corpus).items()):
        # A quest gated at or above UNREACHABLE_LEVEL is disabled by its own
        # level requirement (10 of them at the baseline, all with zero spawns
        # left for their targets). Tuning a quest nobody can start is not a
        # defect, and severity here means confidence that it is one.
        gate = _level(quest, "min_level")
        if gate is not None and gate >= UNREACHABLE_LEVEL:
            continue
        for task_id, task in sorted(quest["tasks"].items(), key=lambda kv: str(kv[0])):
            kind = task.get("type", "")
            if kind not in HUNT_TASK_TYPES | VERDICT_TASK_TYPES:
                continue

            missing = task_body_mismatch(task)
            if missing:
                findings.append(Finding(
                    severity="medium", check="feasibility", subject=f"quest-{gid}",
                    detail=f"t{task_id}:body",
                    message=(f"{kind} has no {missing} container, so its objective "
                             f"cannot be read; treat as a data error, not as tuning"),
                    evidence={"quest": gid, "task": task_id, "task_type": kind,
                              "missing": missing},
                ))
                continue

            # Data errors first, across every hunt shape including repeats: a
            # dangling target is broken whether or not the task repeats.
            seen: set[str] = set()
            for ref, _kill, _chance in task.get("monsters", []):
                seen.add(ref)
            for group in task.get("groups", []):
                seen.update(ref for ref, _k, _c in group["monsters"])
            for bag in task.get("bags", []):
                seen.update(ref for ref, _k, _c in bag["monsters"])
            for ref in sorted(seen):
                info = availability(corpus, ref)
                if info.status in ("dangling", "unparsable"):
                    findings.append(Finding(
                        severity="medium", check="feasibility", subject=f"quest-{gid}",
                        detail=f"t{task_id}:target:{ref}",
                        message=(f"hunt target {ref} resolves to no NPC template, so "
                                 f"its population cannot be evaluated"),
                        evidence={"quest": gid, "task": task_id, "target": ref,
                                  "status": info.status},
                    ))

            if kind not in VERDICT_TASK_TYPES:
                continue

            if kind == "채집Task":
                findings.extend(_collect_findings(corpus, gid, quest, task_id, task))
                continue

            for obj in task_objectives(task):
                if obj.required is None or not obj.targets:
                    continue
                avail = [availability(corpus, ref) for ref, _rate in obj.targets]
                if any(a.status != "ok" for a in avail):
                    if any(a.status == "not-evaluable" for a in avail):
                        findings.append(Finding(
                            severity="info", check="feasibility", subject=f"quest-{gid}",
                            detail=f"t{task_id}:{obj.slot}",
                            message=("target lives in a dungeon continent, where mobs "
                                     "come from event scripts rather than standing "
                                     "territories: not evaluable, not starved"),
                            evidence={"quest": gid, "task": task_id, "slot": obj.slot,
                                      "required": obj.required,
                                      "targets": [a.as_dict() for a in avail]},
                        ))
                    continue

                yield_total = sum(a.total * rate for a, (_r, rate) in zip(avail, obj.targets))
                yield_standing = sum(
                    a.standing * rate for a, (_r, rate) in zip(avail, obj.targets))

                if yield_total < obj.required:
                    findings.append(_shortfall_finding(
                        gid, task_id, obj, avail, yield_total, yield_standing))
                elif yield_standing < obj.required:
                    kinds = sorted({k for a in avail for k in
                                    (["conditional"] if a.conditional else []) +
                                    (["event"] if a.event else [])})
                    findings.append(Finding(
                        severity="info", check="feasibility", subject=f"quest-{gid}",
                        detail=f"t{task_id}:{obj.slot}",
                        message=(f"needs {obj.required} and the standing population "
                                 f"yields only {yield_standing:.2f}; it reaches "
                                 f"{yield_total:.2f} on {' and '.join(kinds)} "
                                 f"territories, which hold only while their condition does"),
                        evidence={"quest": gid, "task": task_id, "slot": obj.slot,
                                  "required": obj.required,
                                  "expected_yield": round(yield_total, 2),
                                  "expected_yield_standing": round(yield_standing, 2),
                                  "targets": [a.as_dict() for a in avail]},
                    ))
    return findings


def _collect_findings(corpus: Corpus, gid: int, quest: dict, task_id,
                      task: dict) -> list[Finding]:
    """Collect tasks count nodes, not kills, and read from CollectionTerritory."""
    out: list[Finding] = []
    ids = [int(c) for c in task.get("collections", []) if c.isdigit()]
    if not ids:
        return out
    for obj in task_objectives(task):
        if obj.required is None:
            continue
        hz = quest["hz"] or 0
        nodes = 0
        rows: list[dict] = []
        for collection_id in ids:
            best, detail = collect_availability(corpus, collection_id, hz)
            nodes += best
            rows.extend(detail)
        if nodes < obj.required:
            elsewhere = [row for collection_id in ids
                         for row in collect_elsewhere(corpus, collection_id, hz)]
            if elsewhere:
                out.append(Finding(
                    severity="info", check="feasibility", subject=f"quest-{gid}",
                    detail=f"t{task_id}:{obj.slot}",
                    message=(f"collect task needs {obj.required} and zone {hz} spawns "
                             f"{nodes}; the collection spawns in "
                             f"{', '.join(str(r['continentId']) for r in elsewhere[:4])} "
                             f"instead, so the objective is farmed off-zone"),
                    evidence={"quest": gid, "task": task_id, "slot": obj.slot,
                              "required": obj.required, "nodes": nodes,
                              "collections": ids, "files": elsewhere},
                ))
                continue
            out.append(Finding(
                severity="medium", check="feasibility", subject=f"quest-{gid}",
                detail=f"t{task_id}:{obj.slot}",
                message=(f"collect task needs {obj.required} and the zone spawns "
                         f"{nodes} node(s) for collection(s) "
                         f"{', '.join(str(i) for i in ids)}; remedy: widen the accept "
                         f"list or raise the spawn count"),
                evidence={"quest": gid, "task": task_id, "slot": obj.slot,
                          "required": obj.required, "nodes": nodes,
                          "collections": ids, "files": rows},
            ))
    return out


# ---------------------------------------------------------------------------
# level-coherence
# ---------------------------------------------------------------------------

def resolve_prereq(corpus: Corpus, ref: str) -> int | None:
    """Global id of a live prerequisite, or None when the edge is a sentinel.

    Pair form hz,local becomes hz*100+local, the convention audit_quests.py
    build_chain uses. An edge is skipped when it does not resolve, or when the
    quest it resolves to gates at UNREACHABLE_LEVEL: that covers 99,99 and
    99,9999 (which dangle) and 999,99 (which resolves to a real placeholder
    quest at level 99 and would otherwise be read as a genuine level inversion
    on 122 quests).
    """
    pair = parse_pair(ref)
    if not pair:
        return None
    gid = pair[0] * 100 + pair[1]
    target = corpus.quests.get(gid)
    if target is None:
        return None
    level = _level(target, "min_level")
    if level is not None and level >= UNREACHABLE_LEVEL:
        return None
    return gid


def chain_max_min_level(corpus: Corpus, gid: int, seen: set[int] | None = None) -> int | None:
    """Highest 최소레벨 anywhere along a quest's prerequisite chain.

    Cycle-guarded: the corpus is not proven acyclic and a self-referencing
    prerequisite would otherwise recurse until the interpreter gives up.
    """
    seen = set() if seen is None else seen
    if gid in seen:
        return None
    seen.add(gid)
    quest = corpus.quests.get(gid)
    if quest is None:
        return None
    best = _level(quest, "min_level")
    for ref in quest["prereqs"]:
        parent = resolve_prereq(corpus, ref)
        if parent is None:
            continue
        upstream = chain_max_min_level(corpus, parent, seen)
        if upstream is not None and (best is None or upstream > best):
            best = upstream
    return best


@check("level-coherence", "tuning",
       "An item gated above the quest that grants it, a prerequisite gated above "
       "its dependent, or a 최대레벨 below the chain that leads to it.")
def check_level_coherence(corpus: Corpus, scope: Scope,
                          margin: int = DEFAULT_LEVEL_MARGIN) -> list[Finding]:
    """Three ways a level gate can contradict the content behind it.

    (a) Quest 1316 granted weapons at requiredLevel 12 from a 최소레벨 9 quest.
        Granting slightly ahead is deliberate on Island of Dawn (42 grants at
        the baseline sit 1 or 2 levels ahead), so the margin exists and defaults
        to 2; below that the check reports the zone's own design.
    (b) Quests 1336 and 1337 gate at 7 behind prerequisite 1335, which gates at
        8. The chain cannot be walked in the order it is written.
    (c) A 최대레벨 below the highest 최소레벨 on the way to the quest makes it
        unofferable: by the time you may start it, you are too high for it. No
        instance exists in either snapshot of this corpus, which is why the
        condition is pinned by a hermetic fixture rather than a corpus oracle.
    """
    findings: list[Finding] = []

    for gid, quest in sorted(scope.subject_quests(corpus).items()):
        quest_level = _level(quest, "min_level")

        # (a) item gated above the quest that grants it
        payload = corpus.rewards.get(gid)
        if payload and quest_level is not None:
            for template in sorted({t for t, _q, _c in payload["items"] if t.isdigit()}):
                info = corpus.items.get(int(template))
                if info is None or not info.is_equipment or info.required_level is None:
                    continue
                gap = info.required_level - quest_level
                if gap > margin:
                    findings.append(Finding(
                        severity="medium", check="level-coherence", subject=f"quest-{gid}",
                        detail=f"item:{template}",
                        message=(f"grants {item_label(corpus, int(template))} at "
                                 f"requiredLevel {info.required_level} from a quest gated "
                                 f"at 최소레벨 {quest_level} (gap {gap} > margin {margin})"),
                        evidence={"quest": gid, "item": int(template),
                                  "item_required_level": info.required_level,
                                  "quest_min_level": quest_level,
                                  "gap": gap, "margin": margin},
                    ))

        # (b) prerequisite gated above its dependent
        if quest_level is not None:
            for ref in quest["prereqs"]:
                parent_gid = resolve_prereq(corpus, ref)
                if parent_gid is None:
                    continue
                parent_level = _level(corpus.quests[parent_gid], "min_level")
                if parent_level is not None and parent_level > quest_level:
                    findings.append(Finding(
                        severity="medium", check="level-coherence", subject=f"quest-{gid}",
                        detail=f"prereq:{parent_gid}",
                        message=(f"gated at 최소레벨 {quest_level} behind prerequisite "
                                 f"{parent_gid}, which is gated at {parent_level}"),
                        evidence={"quest": gid, "prereq": parent_gid,
                                  "quest_min_level": quest_level,
                                  "prereq_min_level": parent_level},
                    ))

        # (c) 최대레벨 below the chain that leads here
        max_level = _level(quest, "max_level")
        if max_level is not None:
            chain_max = chain_max_min_level(corpus, gid)
            if chain_max is not None and chain_max > max_level:
                findings.append(Finding(
                    severity="medium", check="level-coherence", subject=f"quest-{gid}",
                    detail="max-level",
                    message=(f"caps at 최대레벨 {max_level} while its prerequisite chain "
                             f"requires 최소레벨 {chain_max}, so it can never be offered"),
                    evidence={"quest": gid, "max_level": max_level,
                              "chain_max_min_level": chain_max},
                ))
    return findings


# ---------------------------------------------------------------------------
# lane
# ---------------------------------------------------------------------------

@check("lane", "tuning",
       "A story quest granting allow-list equipment. Zone quests own power "
       "progression, story quests own lore progression.")
def check_lane(corpus: Corpus, scope: Scope) -> list[Finding]:
    """Story quest 1305 paid the entire level-7 First Expedition set at once.

    Story membership is a NON-EMPTY 스토리그룹Id, never 퀘스트종류 = 미션 on its
    own: that test misses every 중요미션 quest, 37 of the corpus's 327 story
    quests. Equipment is the dclib.EQUIPMENT_TYPES allow-list via
    ItemInfo.is_equipment, because combatItemType.startswith("EQUIP") also
    matches roughly 4,100 cosmetic and underwear items.

    ADVISORY, and more so than its siblings: lane separation is an Island of
    Dawn ruling. Other regions hand story quests real gear as a matter of
    course, and this check has no opinion about whether they should stop. A
    finding here is an invitation to confirm the region's intent, or to record
    it in the waiver file.
    """
    findings: list[Finding] = []
    for gid, quest in sorted(scope.subject_quests(corpus).items()):
        if not quest.get("story_group"):
            continue
        payload = corpus.rewards.get(gid)
        if not payload:
            continue
        for template in sorted({t for t, _q, _c in payload["items"] if t.isdigit()}):
            info = corpus.items.get(int(template))
            if info is None or not info.is_equipment:
                continue
            findings.append(Finding(
                severity="medium", check="lane", subject=f"quest-{gid}",
                detail=f"item:{template}",
                message=(f"story quest (스토리그룹Id {quest['story_group']}, "
                         f"퀘스트종류 {quest['quest_type'] or 'unset'}) grants "
                         f"{item_label(corpus, int(template))}, which is "
                         f"{info.combat_type}"),
                evidence={"quest": gid, "item": int(template),
                          "story_group": quest["story_group"],
                          "quest_type": quest["quest_type"],
                          "combat_type": info.combat_type},
            ))
    return findings
