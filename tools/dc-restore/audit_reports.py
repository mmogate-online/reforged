"""Report sections: descriptive tables, no severities, offered as judgment input.

A check answers "is this a defect". These three answer "what does the zone
actually look like", which is a different question and one a program must not
pretend to settle. Labelling a judgment call with a severity is how a tool starts
being argued with instead of read, so nothing here carries one and nothing here
returns a Finding.

  set-placement   Where the pieces of a gear set are paid out, and what walking
                  the zone to collect them costs. Born from a level-7 weapon
                  parked on an NPC well outside the camp cluster that testers
                  simply skipped, and from the 1332 to 1333 pair, where one
                  quest's turn-in NPC is the next quest's giver: the ideal
                  placement, and the one shape worth naming explicitly.
  giver-load      Quests grouped by giver, task verb, target family and level
                  band, plus a zone-wide verb histogram. This is what turns
                  "the zone feels repetitive" into a number a designer can act
                  on.
  effort-reward   Kill, deliver and collect counts against exp, gold and item
                  payout, sorted raw. No outlier flags: a threshold is judgment,
                  a table is deterministic.

NPC positions are resolved by listing EVERY standing spawn of a template, never
by picking one. A template with spawns in two places has two answers and a tool
that silently reports the first is wrong half the time. Templates whose
spawnScriptId is set are called out for the same reason: the script decides
where the player actually meets them, so the standing position is a lower bound
on the truth, not the truth.

Everything this module needs beyond dclib (AreaData section geometry, the NPC
spawn atlas, turn-in derivation, planar distance) is implemented locally on
purpose: dclib is the shared model and a report's presentation helpers do not
belong in it.
"""

from __future__ import annotations

import math
import re
import weakref
from collections import Counter
from dataclasses import dataclass

from auditlib import Corpus, Scope, report
from dclib import npc_template_ids, territory_spawns

# ---------------------------------------------------------------------------
# Zone profile
# ---------------------------------------------------------------------------
#
# The hub is a per-zone parameter, never a constant: "how far is this from
# town" has no zone-independent answer. The Island of Dawn value is the v31
# recall point restored by spec 002/26, and the AreaData file is the continent
# that carries every island section (hunting zones 13, 64 and 213 all resolve
# into continent 13).


@dataclass(frozen=True)
class ZoneProfile:
    """Where a zone's players return to, and which AreaData names its ground."""

    hub: tuple[float, float]
    hub_name: str
    area_files: tuple[str, ...]


ZONE_PROFILES: dict[int, ZoneProfile] = {
    13: ZoneProfile(
        hub=(66600.8672, -79855.5234),
        hub_name="Island of Dawn recall point",
        area_files=("AreaData/AreaData_13_ATW_Death_P.xml",),
    ),
}

# 사냥Task, 사냥전달Task, 그룹사냥Task: the three shapes that ask a player to kill.
HUNT_TASKS = ("사냥Task", "사냥전달Task", "그룹사냥Task")
UNPLACED = (0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def parse_pos(raw: str) -> tuple[float, float, float] | None:
    """A `pos` attribute as (x, y, z), or None when it is not three numbers."""
    parts = [p for p in (raw or "").replace(" ", "").split(",") if p]
    if len(parts) < 3:
        return None
    try:
        return (float(parts[0]), float(parts[1]), float(parts[2]))
    except ValueError:
        return None


def planar(a, b) -> float:
    """Distance in the XY plane.

    Z is deliberately ignored. The island's z spans two kilometres of cliff
    across a walk of a few hundred, so including it reports terrain relief as
    travel cost and makes two points on the same path look further apart than
    two points across the map.
    """
    return math.hypot(a[0] - b[0], a[1] - b[1])


def point_in_ring(point, ring) -> bool:
    """Even-odd containment of an XY point in a Fence polygon."""
    if len(ring) < 3:
        return False
    x, y = point[0], point[1]
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


_SECTION_OR_FENCE = re.compile(r"<(/?)(Section|Fence)\b([^>]*?)(/?)>")
_ATTR = re.compile(r'(\w+)="([^"]*)"')
_COMMENT = re.compile(r"<!--.*?-->", re.S)


@dataclass(frozen=True)
class AreaSection:
    """One named piece of ground, with its Fence ring and nesting depth."""

    id: str
    desc: str
    depth: int
    ring: tuple[tuple[float, float], ...]


def parse_area_sections(text: str) -> list[AreaSection]:
    """Live <Section> elements with their Fence rings, deepest nesting recorded.

    Comments are stripped first. A commented-out section is dormant content, not
    ground a player can stand on, and resolving a position into one would name a
    place that does not exist in the running server.
    """
    live = _COMMENT.sub("", text or "")
    out: list[AreaSection] = []
    rings: list[list[tuple[float, float]]] = []
    stack: list[int] = []
    for m in _SECTION_OR_FENCE.finditer(live):
        closing, tag, attrs, selfclose = m.groups()
        if tag == "Section":
            if closing:
                if stack:
                    stack.pop()
                continue
            a = dict(_ATTR.findall(attrs))
            out.append(AreaSection(a.get("id", ""), a.get("desc", ""), len(stack), ()))
            rings.append([])
            if not selfclose:
                stack.append(len(out) - 1)
        elif tag == "Fence" and stack:
            a = dict(_ATTR.findall(attrs))
            pos = parse_pos(a.get("pos", ""))
            if pos is not None:
                rings[stack[-1]].append((pos[0], pos[1]))
    return [
        AreaSection(s.id, s.desc, s.depth, tuple(ring))
        for s, ring in zip(out, rings)
    ]


def resolve_section(point, sections: list[AreaSection]) -> str:
    """Deepest section containing a point, or an empty string.

    Sections nest, so several can contain one point. The deepest is the specific
    answer ("the ruins"), the shallowest is the useless one ("the island").
    """
    hits = [s for s in sections if point_in_ring(point, s.ring)]
    if not hits:
        return ""
    return max(hits, key=lambda s: (s.depth, s.id)).desc


# ---------------------------------------------------------------------------
# NPC atlas
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Spawn:
    """One standing placement of an NPC template."""

    pos: tuple[float, float, float]
    desc: str
    territory: str
    group: str
    section: str = ""

    @property
    def placed(self) -> bool:
        """False for the 0,0,0 origin, which means "something else places me"."""
        return self.pos != UNPLACED


@dataclass(frozen=True)
class NpcPlacement:
    """Every standing spawn of one NPC reference, plus how it is placed.

    Absent spawns produce an empty placement rather than None, so callers never
    branch on a missing object to render a row.
    """

    ref: str = ""
    hz: int = 0
    template: int = 0
    name: str = ""
    spawn_script: str = ""
    spawns: tuple[Spawn, ...] = ()

    @property
    def known(self) -> bool:
        return bool(self.ref)

    @property
    def placed_spawns(self) -> tuple[Spawn, ...]:
        return tuple(s for s in self.spawns if s.placed)

    @property
    def multi_spawn(self) -> bool:
        return len({s.pos for s in self.placed_spawns}) > 1

    @property
    def script_placed(self) -> bool:
        """spawnScriptId set: the script, not the territory, has the last word."""
        return self.spawn_script not in ("", "0")

    @property
    def caveat(self) -> str:
        """Why this placement may not be the whole answer, in one phrase."""
        notes = []
        if not self.placed_spawns:
            notes.append("no standing spawn" if self.spawns else "no spawn entry")
        if self.multi_spawn:
            notes.append(f"{len(self.placed_spawns)} spawns")
        if self.script_placed:
            notes.append(f"spawnScriptId {self.spawn_script}")
        return ", ".join(notes)


class NpcAtlas:
    """Lazy per-zone index of NPC names, spawn positions and spawn scripts."""

    def __init__(self, corpus: Corpus):
        self.corpus = corpus
        self._zones: dict[int, tuple[dict, dict, dict]] = {}
        self._sections: dict[str, list[AreaSection]] = {}

    def _zone(self, hz: int):
        if hz not in self._zones:
            spawns: dict[int, list[Spawn]] = {}
            text = self.corpus.read(f"TerritoryData_{hz}.xml")
            if text:
                for row in territory_spawns(text):
                    pos = parse_pos(row.get("pos", ""))
                    if pos is None:
                        continue
                    tid = row.get("npcTemplateId")
                    if not isinstance(tid, int):
                        continue
                    spawns.setdefault(tid, []).append(Spawn(
                        pos=pos, desc=row.get("desc", ""),
                        territory=row.get("territory_desc", ""),
                        group=row.get("group_desc", ""),
                    ))
            names: dict[int, str] = {}
            scripts: dict[int, str] = {}
            npc_text = self.corpus.read(f"NpcData_{hz}.xml")
            if npc_text:
                names = npc_template_ids(npc_text)
                for m in re.finditer(
                        r'<Template\b[^>]*?\bid="(\d+)"[^>]*?\bspawnScriptId="([^"]*)"', npc_text):
                    scripts[int(m.group(1))] = m.group(2)
            self._zones[hz] = (names, spawns, scripts)
        return self._zones[hz]

    def sections(self, profile: ZoneProfile) -> list[AreaSection]:
        key = "|".join(profile.area_files)
        if key not in self._sections:
            found: list[AreaSection] = []
            for relpath in profile.area_files:
                text = self.corpus.read(relpath)
                if text:
                    found.extend(parse_area_sections(text))
            self._sections[key] = found
        return self._sections[key]

    def placement(self, ref: str, profile: ZoneProfile | None = None) -> NpcPlacement:
        """Resolve an "hz,templateId" reference to every spawn it has."""
        if not ref or "," not in ref:
            return NpcPlacement()
        head, _, tail = ref.partition(",")
        if not head.strip().isdigit() or not tail.strip().isdigit():
            return NpcPlacement()
        hz, tid = int(head), int(tail)
        names, spawns, scripts = self._zone(hz)
        sections = self.sections(profile) if profile else []
        located = tuple(
            Spawn(s.pos, s.desc, s.territory, s.group,
                  resolve_section(s.pos, sections) if s.placed else "")
            for s in spawns.get(tid, ())
        )
        return NpcPlacement(ref=ref, hz=hz, template=tid, name=names.get(tid, ""),
                            spawn_script=scripts.get(tid, ""), spawns=located)


_ATLASES: "weakref.WeakKeyDictionary[Corpus, NpcAtlas]" = weakref.WeakKeyDictionary()


def atlas(corpus: Corpus) -> NpcAtlas:
    """One atlas per corpus, so three report sections read each zone file once."""
    found = _ATLASES.get(corpus)
    if found is None:
        found = NpcAtlas(corpus)
        _ATLASES[corpus] = found
    return found


def distance_span(a: NpcPlacement, b: NpcPlacement) -> tuple[float, float] | None:
    """(shortest, longest) walk between two placements over all spawn pairs.

    A span rather than a number, because a template with two spawns has two
    answers and collapsing them to one is the silent pick this module refuses.
    """
    left, right = a.placed_spawns, b.placed_spawns
    if not left or not right:
        return None
    pairs = [planar(p.pos, q.pos) for p in left for q in right]
    return (min(pairs), max(pairs))


def hub_span(hub, placement: NpcPlacement) -> tuple[float, float] | None:
    spawns = placement.placed_spawns
    if not spawns:
        return None
    lengths = [planar(hub, s.pos) for s in spawns]
    return (min(lengths), max(lengths))


def fmt_span(span: tuple[float, float] | None) -> str:
    if span is None:
        return "n/a"
    low, hi = span
    if round(low) == round(hi):
        return f"{round(low):,}"
    return f"{round(low):,}..{round(hi):,}"


def round_trip(hub, giver: NpcPlacement, turn_in: NpcPlacement) -> tuple[float, float] | None:
    """hub to giver to turn-in and back, as a span over the spawn choices."""
    legs = (hub_span(hub, giver), distance_span(giver, turn_in), hub_span(hub, turn_in))
    if any(leg is None for leg in legs):
        return None
    return (sum(leg[0] for leg in legs), sum(leg[1] for leg in legs))


# ---------------------------------------------------------------------------
# Quest shape helpers
# ---------------------------------------------------------------------------

def turn_in_ref(quest: dict) -> str:
    """The NPC the last task hands back to.

    A hunt or deliver task names it in 대상NPC지정; a visit task's target IS the
    NPC, so its 방문그룹 entry is the same thing. Reading only the first drops
    every quest that ends on a conversation.
    """
    for task_id in sorted(quest.get("tasks", {}), key=lambda k: (k is None, k), reverse=True):
        task = quest["tasks"][task_id]
        if task.get("target_npc"):
            return task["target_npc"][0]
        if task.get("visits"):
            return task["visits"][0]
    return ""


def level_band(quest: dict, width: int = 5) -> str:
    raw = str(quest.get("min_level", "")).strip()
    if not raw.isdigit():
        return "?"
    level = int(raw)
    low = ((level - 1) // width) * width + 1
    return f"{low}-{low + width - 1}"


def task_targets(task: dict) -> list[str]:
    """Every monster reference a task names, across all three hunt shapes."""
    refs = [m[0] for m in task.get("monsters", ())]
    for bag in task.get("bags", ()):
        refs.extend(m[0] for m in bag.get("monsters", ()))
    for group in task.get("groups", ()):
        refs.extend(m[0] for m in group.get("monsters", ()))
    return [r for r in refs if r]


def target_family(task: dict, npcs: NpcAtlas) -> str:
    """The distinct target names of a task, or a dash when it hunts nothing."""
    names = []
    for ref in task_targets(task):
        placement = npcs.placement(ref)
        names.append(placement.name or ref)
    unique = sorted(set(names))
    if not unique:
        return "-"
    if len(unique) > 3:
        return f"{unique[0]} +{len(unique) - 1} more"
    return "+".join(unique)


def _count(raw) -> int:
    text = str(raw or "").strip()
    return int(text) if text.isdigit() else 0


def effort_counts(quest: dict) -> tuple[int, int, int]:
    """(kills, delivered items, collected items) required by a whole quest.

    The three hunt shapes hold their count in three different places: per
    monster entry for 사냥Task, per BAG for 사냥전달Task, and per GROUP for
    그룹사냥Task. Reading one place and calling it the count reports zero for
    two thirds of the corpus.
    """
    kills = delivered = collected = 0
    for task in quest.get("tasks", {}).values():
        for _ref, kill, _chance in task.get("monsters", ()):
            kills += _count(kill)
        for group in task.get("groups", ()):
            kills += _count(group.get("kills"))
        for bag in task.get("bags", ()):
            # The wrapper, not the task label, says what kind of bag this is:
            # 아이템작성 is filled by killing, 전달아이템지정 by gathering.
            if bag.get("kind") == "전달아이템지정":
                collected += _count(bag.get("qty"))
            else:
                delivered += _count(bag.get("qty"))
        for _flag, qty in task.get("deliver_direct", ()):
            delivered += _count(qty)
    return kills, delivered, collected


# ---------------------------------------------------------------------------
# set-placement
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Carrier:
    """One quest that pays out part of a gear set, and where it pays it."""

    quest: int
    items: tuple[int, ...]
    slots: tuple[str, ...]
    giver: NpcPlacement
    turn_in: NpcPlacement
    offerable: bool = True


@dataclass(frozen=True)
class SetPlacement:
    """A visual gear set and every subject quest that carries a piece of it."""

    family: str
    tier: str
    carriers: tuple[Carrier, ...]
    chains: tuple[tuple[int, int, str], ...] = ()
    profile: ZoneProfile | None = None


def giver_index(quests: dict[int, dict]) -> dict[str, list[int]]:
    """{npc ref: quests that NPC hands out}, over whatever pool is passed."""
    index: dict[str, list[int]] = {}
    for gid, quest in sorted(quests.items()):
        ref = quest.get("giver", "")
        if ref:
            index.setdefault(ref, []).append(gid)
    return index


def chain_links(carriers, index: dict[str, list[int]]) -> list[tuple[int, int, str]]:
    """(earlier, later, npc ref) where a carrier's turn-in NPC is a next giver.

    This is the placement that costs a player nothing: they hand in, and the
    next quest is already standing in front of them. The successor is looked up
    across the whole subject scope rather than inside the set, because the 1332
    to 1333 pair chains a set piece into a weapon and a set-only lookup cannot
    see it.
    """
    links: list[tuple[int, int, str]] = []
    for carrier in carriers:
        ref = carrier.turn_in.ref
        if not ref:
            continue
        for other in index.get(ref, ()):
            if other != carrier.quest:
                links.append((carrier.quest, other, ref))
    return sorted(set(links))


def set_placements(corpus: Corpus, scope: Scope) -> list[SetPlacement]:
    """Gear sets carried by subject quests, with every carrier's placement."""
    npcs = atlas(corpus)
    subject = scope.subject_quests(corpus)
    index = giver_index(subject)
    grouped: dict[tuple[str, str], dict[int, list]] = {}
    for gid in sorted(subject):
        payload = corpus.rewards.get(gid)
        if not payload:
            continue
        for template, _qty, _cls in payload["items"]:
            if not template.isdigit():
                continue
            info = corpus.items.get(int(template))
            if info is None or not info.is_equipment or info.set_key is None:
                continue
            grouped.setdefault(info.set_key, {}).setdefault(gid, []).append(
                (int(template), info.slot))

    out: list[SetPlacement] = []
    for (family, tier), per_quest in sorted(grouped.items()):
        profile = None
        carriers: list[Carrier] = []
        for gid, rows in sorted(per_quest.items()):
            quest = corpus.quests[gid]
            profile = profile or ZONE_PROFILES.get(quest.get("hz"))
            carriers.append(Carrier(
                quest=gid,
                items=tuple(sorted({r[0] for r in rows})),
                slots=tuple(sorted({r[1] for r in rows if r[1]})),
                giver=npcs.placement(quest.get("giver", ""), profile),
                turn_in=npcs.placement(turn_in_ref(quest), profile),
                offerable=not quest.get("sentinel", False),
            ))
        out.append(SetPlacement(family, tier, tuple(carriers),
                                tuple(chain_links(carriers, index)), profile))
    return out


def _npc_lines(label: str, placement: NpcPlacement) -> list[str]:
    """Every spawn of one NPC, one line each. Never a single silent pick."""
    if not placement.known:
        return [f"      {label:8} (none named)"]
    caveat = placement.caveat
    head = f"      {label:8} {placement.ref} {placement.name or '?'}"
    if caveat:
        head += f"  [{caveat}]"
    lines = [head]
    for spawn in placement.spawns:
        if not spawn.placed:
            lines.append("               origin 0,0,0 (placed elsewhere, not by this territory)")
            continue
        where = spawn.section or spawn.territory or spawn.group or spawn.desc
        lines.append(f"               {spawn.pos[0]:,.0f}, {spawn.pos[1]:,.0f}"
                     f"   {where}")
    return lines


@report("set-placement",
        "Per gear set: the carrier quests, every spawn of their giver and "
        "turn-in NPCs, pairwise distances, turn-in to giver chains, and round "
        "trips against the zone hub.")
def report_set_placement(corpus: Corpus, scope: Scope) -> list[str]:
    """Where a set is paid out decides whether anyone collects it.

    A level-7 weapon parked on an NPC far outside the camp cluster was simply
    skipped by testers, and the pair whose turn-in NPC is the next quest's giver
    cost them nothing extra. Both facts are geometry, and geometry is
    computable; whether a given distance is a flaw or the point of a migration
    quest is not, which is why this section carries no severities.
    """
    lines: list[str] = []
    for placement in set_placements(corpus, scope):
        profile = placement.profile
        hub = profile.hub if profile else None
        header = (f"  set {placement.family}/{placement.tier}: "
                  f"{len(placement.carriers)} carrier quest(s)")
        if profile:
            header += (f"; hub {profile.hub_name} at "
                       f"{profile.hub[0]:,.0f}, {profile.hub[1]:,.0f}")
        lines.append(header)
        for carrier in placement.carriers:
            slots = "+".join(carrier.slots) or "-"
            items = ", ".join(str(i) for i in carrier.items)
            state = "" if carrier.offerable else "  [sentinel prerequisite: not offerable]"
            lines.append(f"    quest {carrier.quest}  slots {slots}  items {items}{state}")
            lines.extend(_npc_lines("giver", carrier.giver))
            lines.extend(_npc_lines("turn-in", carrier.turn_in))
            walk = f"giver to turn-in {fmt_span(distance_span(carrier.giver, carrier.turn_in))}"
            if hub:
                walk += (f"; hub to giver {fmt_span(hub_span(hub, carrier.giver))}"
                         f"; round trip {fmt_span(round_trip(hub, carrier.giver, carrier.turn_in))}")
            lines.append(f"      {walk}")
        pairs = [
            (a.quest, b.quest, distance_span(a.giver, b.giver))
            for i, a in enumerate(placement.carriers)
            for b in placement.carriers[i + 1:]
        ]
        for left, right, span in pairs:
            lines.append(f"    giver {left} to giver {right}: {fmt_span(span)}")
        collapsed: dict[tuple[int, str], list[int]] = {}
        for earlier, later, ref in placement.chains:
            collapsed.setdefault((earlier, ref), []).append(later)
        for (earlier, ref), successors in sorted(collapsed.items()):
            names = ", ".join(str(s) for s in sorted(successors))
            lines.append(f"    chain: quest {earlier} turns in at {ref}, which gives {names}")
        if not placement.chains and len(placement.carriers) > 1:
            lines.append("    chain: none (no carrier's turn-in NPC gives another carrier)")
    return lines


# ---------------------------------------------------------------------------
# giver-load
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LoadRow:
    """Quests sharing a giver, a task verb, a target family and a level band."""

    giver: str
    giver_name: str
    task_type: str
    target: str
    band: str
    quests: tuple[int, ...] = ()


def giver_load(corpus: Corpus, scope: Scope) -> list[LoadRow]:
    npcs = atlas(corpus)
    buckets: dict[tuple[str, str, str, str, str], set[int]] = {}
    for gid, quest in sorted(scope.subject_quests(corpus).items()):
        giver = quest.get("giver", "")
        placement = npcs.placement(giver)
        band = level_band(quest)
        for task in quest.get("tasks", {}).values():
            key = (giver, placement.name, task.get("type", ""), target_family(task, npcs), band)
            buckets.setdefault(key, set()).add(gid)
    return [
        LoadRow(giver, name, task_type, target, band, tuple(sorted(quests)))
        for (giver, name, task_type, target, band), quests in sorted(buckets.items())
    ]


def verb_histogram(corpus: Corpus, scope: Scope) -> Counter:
    """How many tasks of each verb the subject zone asks a player to perform."""
    verbs: Counter = Counter()
    for quest in scope.subject_quests(corpus).values():
        for task in quest.get("tasks", {}).values():
            verbs[task.get("type", "") or "(unnamed)"] += 1
    return verbs


def hunt_quest_share(corpus: Corpus, scope: Scope) -> tuple[int, int]:
    """(quests carrying at least one hunt-family task, subject quests).

    The measurable form of "the zone is repetitive". Reported as a ratio and
    nothing else: whether a ratio is too high is exactly the judgment this
    section declines to make.
    """
    subject = scope.subject_quests(corpus)
    hunting = sum(
        1 for quest in subject.values()
        if any(task.get("type") in HUNT_TASKS for task in quest.get("tasks", {}).values())
    )
    return hunting, len(subject)


@report("giver-load",
        "Quests grouped by giver, task verb, target family and level band, "
        "plus the zone-wide task-verb histogram.")
def report_giver_load(corpus: Corpus, scope: Scope) -> list[str]:
    """Repetition is a feeling until it is counted.

    Testers reported the restored island as repetitive. The grouping makes the
    reason legible: one giver, one verb, one target family, one level band, over
    and over. The histogram gives the zone-wide shape, and the hunt share gives
    the one number the complaint was really about.
    """
    rows = giver_load(corpus, scope)
    lines: list[str] = []
    if rows:
        lines.append("  giver                 verb                target                          band    quests")
        for row in rows:
            giver = f"{row.giver} {row.giver_name}".strip() or "(no giver)"
            quests = ", ".join(str(q) for q in row.quests)
            lines.append(f"  {giver[:21]:21} {row.task_type[:19]:19} {row.target[:31]:31} "
                         f"{row.band:7} {quests}")
    verbs = verb_histogram(corpus, scope)
    if verbs:
        lines.append("  task-verb histogram (tasks, not quests):")
        for verb, count in sorted(verbs.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"    {verb:24} {count:4}  {'#' * min(count, 60)}")
    hunting, total = hunt_quest_share(corpus, scope)
    if total:
        lines.append(f"  quests carrying at least one hunt-family task: {hunting} of {total}")
    return lines


# ---------------------------------------------------------------------------
# effort-reward
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EffortRow:
    """What one quest asks for, and what it pays."""

    quest: int
    tasks: int
    kills: int
    delivered: int
    collected: int
    exp: int
    gold: int
    items: int


def effort_reward(corpus: Corpus, scope: Scope) -> list[EffortRow]:
    rows: list[EffortRow] = []
    for gid, quest in sorted(scope.subject_quests(corpus).items()):
        kills, delivered, collected = effort_counts(quest)
        payload = corpus.rewards.get(gid) or {}
        rows.append(EffortRow(
            quest=gid,
            tasks=len(quest.get("tasks", {})),
            kills=kills, delivered=delivered, collected=collected,
            exp=_count(payload.get("exp")), gold=_count(payload.get("gold")),
            items=len(payload.get("items", ())),
        ))
    return rows


@report("effort-reward",
        "Kill, deliver and collect counts and task counts against exp, gold "
        "and item payout, sorted raw and unflagged.")
def report_effort_reward(corpus: Corpus, scope: Scope) -> list[str]:
    """A table, not a verdict.

    Quest 1348 asked for 8 items from 10 credit mobs and testers called it the
    worst quest in the zone, but no threshold separates it from a quest that
    asks a lot and pays a lot. Flagging outliers here would encode one person's
    tuning taste as a rule; printing the numbers in quest order lets a designer
    apply their own.
    """
    rows = effort_reward(corpus, scope)
    if not rows:
        return []
    lines = ["  quest  tasks  kills  deliv  collect      exp     gold  items"]
    for row in rows:
        lines.append(f"  {row.quest:5}  {row.tasks:5}  {row.kills:5}  {row.delivered:5}  "
                     f"{row.collected:7}  {row.exp:7}  {row.gold:7}  {row.items:5}")
    return lines
