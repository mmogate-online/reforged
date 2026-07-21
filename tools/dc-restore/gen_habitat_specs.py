#!/usr/bin/env python
"""IoD padding mob-habitat restoration spec generator (patch 001, Wave B).

Deterministic. Re-runs byte-identical (fixed iteration order, no timestamps).

Emits one DSL spec:

  specs/patches/001/15-iod-mob-habitats.yaml

Restores 17 deleted v17-only mob groups (217 territories) plus 2 bespoke
quest-target territories reconstructed from NpcLoc marker clusters, all in HZ 13.

Doctrine (v31-primary classic restoration):
  rule 4  : geometry (fences) recovered from the v17.11 client TerritoryData.
  rule 5  : mob habitat replication from v17; MOBS ONLY; every replicated
            territory is an approximation (v17 geometry + v31 donor attributes)
            and is divergence-logged.

Source precedence:
  * group roster + fence polygons :
        padding-habitat-gaps.json (v17 client fences + v17 group rosters).
  * population / respawn / flags :
        modal attribute set of the NAMED DONOR GROUP parsed live from the v31
        TerritoryData_13 (per-attribute mode over the donor's spawns).
  * bespoke quest-target fences + rosters :
        padding-npcloc-sweep.json marker clusters (convex hull + margin).
  * group / territory / instance ids :
        v17 group ids where free in BOTH eras; territory/instance ids allocated
        above the live max, each re-verified free in both v31 and v92.
  * spawn position :
        territory fence-ring centroid, point-in-polygon validated.

Adjudicated DECISION defaults (3 groups without a clean same-family v31 donor):
  * 1300033 (Rockcrawler)  : roster 300541/300542/300540; generic combat profile
                             (spawnCount 1, respawnTime 20000, randomPos true, ai 6).
  * 1300058 (Stone Head)   : roster 301; environment profile from donor 1300054.
  * 1300029 (corrupt Terron): FIGHTABLE roster 300942/300943/300945; density copied
                             from Black Rift group 1300041.
Bespoke quest territories use the same generic combat profile.

Emission uses the spawn-restore-standard archetypes (ClassicTerritory /
RestoreSpawnBase / RestoreSpawnAggressive): each row carries only the fields that
deviate from its archetype. This is the sanctioned restoration pattern
(dsl-definitions skill lesson: restoration spawns extend spawn-restore-standard).

Run:  python gen_habitat_specs.py
"""

import io
import json
import os
import re
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# Paths (absolute, per project rules).
# ---------------------------------------------------------------------------
DATA_DIR = r"D:\dev\mmogate\github\reforged-server-content\reforged\docs\plans\classic-restoration\iod\data"
HABITAT_JSON = os.path.join(DATA_DIR, "padding-habitat-gaps.json")
SWEEP_JSON = os.path.join(DATA_DIR, "padding-npcloc-sweep.json")

V92_DATASHEET = r"D:\dev\mmogate\tera92\server\Datasheet"
V31_DATASHEET = r"Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet"

OUT_DIR = r"D:\dev\mmogate\github\reforged-server-content\reforged\specs\patches\001"
OUT_SPEC = os.path.join(OUT_DIR, "15-iod-mob-habitats.yaml")

HZ = 13

# Territory / instance id allocation: above the live max (13014250 / 13472940 in
# both eras), stepped so provenance reads clearly. Every allocated id is asserted
# free in BOTH eras before use.
TERR_ID_START = 13014260
INST_ID_START = 13472950
ID_STEP = 10

# Bespoke quest-target groups: allocated adjacent to the v17 group id range so
# provenance reads naturally. Scanned upward from here for ids free in both eras.
BESPOKE_GROUP_SCAN_START = 1300059

SPAWN_PKG = "spawn-restore-standard"

# ---------------------------------------------------------------------------
# Spawn attribute typing / emission order (DSL aliases == XML attr names).
# Mirrors tools/dc-restore/gen_spawn_specs.py (proven to validate + apply).
# ---------------------------------------------------------------------------
SPAWN_INT = {
    "npcInstanceId", "npcTemplateId", "memberId", "ai", "spawnCount", "offsetZ",
    "respawnTime", "delaySpawnTimeWhenWorldStart", "viewRadius", "viewAngle",
    "alertRadius", "alertAngle", "aggroSendToClanDistance",
    "aggroSendToPartyDistance", "aggroShareGroupId", "returnDistance",
    "msgInterval", "randomGroupId",
}
SPAWN_BOOL = {
    "randomPos", "isAggressiveMonster", "aggroReceiveOnlyInSight", "isReturn",
    "isReturnMyTerritory", "conditionalSpawn", "questPatrol",
    "peaceStateNoMoving", "cautionStateNoMoving", "voidSpawn", "moveInTerritory",
    "msgBroadcastingChannel", "excludeAggroLimit",
}
SPAWN_DEC = {"dir", "msgProb"}
SPAWN_VEC = {"pos", "escapeLocation"}

SPAWN_ORDER = [
    "npcInstanceId", "npcTemplateId", "memberId", "desc", "pos", "dir",
    "offsetZ", "randomPos", "escapeLocation", "spawnCount", "respawnTime",
    "respawnRandomTime", "delaySpawnTimeWhenWorldStart", "conditionalSpawn",
    "ai", "isAggressiveMonster", "isReturn", "isReturnMyTerritory",
    "returnDistance", "moveInTerritory", "questPatrol", "peaceStateNoMoving",
    "cautionStateNoMoving", "voidSpawn", "viewRadius", "viewAngle",
    "alertRadius", "alertAngle", "aggroShareGroupId", "aggroSendToPartyDistance",
    "aggroSendToClanDistance", "aggroSendToTerritory", "aggroIgnorePartyId",
    "aggroReceiveOnlyInSight", "excludeAggroLimit", "popupMsg", "msgProb",
    "msgInterval", "randomGroupId",
]

# Per-row identity fields (never taken from the donor modal pattern).
IDENTITY_FIELDS = {"npcInstanceId", "npcTemplateId", "desc", "pos"}

# XML attr name for a spawn field, where it differs from the DSL alias.
XML_ATTR = {"npcInstanceId": "instanceId"}

# ---------------------------------------------------------------------------
# Archetypes (packages/spawn-restore-standard). Values MUST mirror the package
# definitions exactly; a field is suppressed only when its rendered value equals
# the archetype's, so the merged result is unchanged.
# ---------------------------------------------------------------------------
SPAWN_BASE = {
    "dir": 0, "offsetZ": 0, "randomPos": "true", "escapeLocation": [0, 0, 0],
    "respawnTime": 20000, "respawnRandomTime": "2000",
    "delaySpawnTimeWhenWorldStart": 0, "conditionalSpawn": "false",
    "isAggressiveMonster": "false", "isReturn": "false",
    "isReturnMyTerritory": "false", "returnDistance": 2000,
    "moveInTerritory": "false", "questPatrol": "false",
    "peaceStateNoMoving": "false", "cautionStateNoMoving": "false",
    "voidSpawn": "false", "viewRadius": 200, "viewAngle": 360,
    "alertRadius": 250, "alertAngle": 360, "aggroShareGroupId": 0,
    "aggroSendToClanDistance": 0, "aggroSendToTerritory": "",
    "aggroIgnorePartyId": "", "aggroReceiveOnlyInSight": "false",
    "excludeAggroLimit": "false", "popupMsg": "", "msgProb": 0,
    "msgInterval": 0, "randomGroupId": 0,
}
TERR_BASE = {
    "type": "normal", "addMaxZ": "256.000000", "subtractMinZ": "0.000000",
    "eventId": "0", "randomPosMinDist": "100.000000",
    "peaceMoveNpcCheckDist": "100.000000",
}
TERR_OPTIONAL = ("eventId", "randomPosMinDist", "peaceMoveNpcCheckDist")

# ---------------------------------------------------------------------------
# Per-group generation plan. donor==None => DECISION default (see module docstring).
#   kind    : "v17"      17 replicated v17 groups (fences from habitat json)
#   profile : "donor"    modal attrs from `donor_gid` in v31
#             "combat"   generic combat: ref group 1300018 attrs + overrides
#             "env"      env: donor_gid modal attrs
# ---------------------------------------------------------------------------
GENERIC_COMBAT_REF = 1300018   # large Argas group; env-field envelope source
GENERIC_COMBAT_OVERRIDE = {"spawnCount": 1, "respawnTime": 20000,
                           "randomPos": "true", "ai": 6,
                           "isAggressiveMonster": "false"}

# Spawn-density fix (padding-density-fixes.md, 2026-07-21 adjudication).
# Quest-served v17 groups whose round-robin roster + spawnCount 1 left the credit
# template too sparse for its quest kill target. Applied in the v17-group loop:
#   force_roster : replace the round-robin roster so the credit template dominates.
#   spawnCount   : per-spawn override, merged like GENERIC_COMBAT_OVERRIDE.
QUEST_DENSITY = {
    1300036: {"force_roster": [4], "spawnCount": 5},  # Mini Orcan farm (quest 1349, 48-kill tpl 4)
    1300038: {"spawnCount": 2},                        # Orcan patrol (quest 1349, tpl 5); roster kept
}

# Bespoke quest-target groups (same 2026-07-21 fix). One small square territory per
# NpcLoc marker instead of a single convex hull per template, so every classic spawn
# point is represented. Templates are assigned by a weighted split over the shared
# marker cluster, weighting the high-drop credit template. Each entry:
#   (quest, marker_source_template, [(template, marker_count), ...] high-drop first)
# The weight counts must sum to the marker-source template's marker count.
BESPOKE_FENCE_MARGIN = 150.0
BESPOKE_DEFS = [
    ("1348", 302, [(302, 6), (303, 4)]),
    ("1319", 300941, [(300944, 10), (300941, 7)]),
]

# Previously-applied bespoke layout (spec 15 as generated/applied 2026-07-20, before
# the density fix: one hull-derived territory per template). The per-marker
# regeneration reuses the group-1300060 ids but reallocates the group-1300061 ids,
# so any prior (groupId, territoryId) NOT reproduced by the new emission is stranded
# under upsert-only replay. These are emitted as explicit territory deletes (cascade
# to their child spawn). Absent-delete warnings on re-replay are the accepted pattern.
PRIOR_BESPOKE = {
    1300060: [(13016430, 13475120, 302), (13016440, 13475130, 303)],
    1300061: [(13016450, 13475140, 300941), (13016460, 13475150, 300944)],
}

# Roster templates excluded from the ambient round-robin because they are NAMED
# uniques already live in the v92 baseline; re-spawning them from an ambient
# habitat would duplicate the unique and collide same-family with its live group.
ROSTER_EXCLUDE = {
    1001: ("named unique (Vekas / Resisting Ghilliedhu) already live in baseline "
           "named-boss group 1300047; ambient restore must not duplicate it"),
}


def die(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def load_json(path):
    return json.load(io.open(path, encoding="utf-8"))


def read_text(path):
    return io.open(path, encoding="utf-8-sig").read()


# ---------------------------------------------------------------------------
# Geometry helpers.
# ---------------------------------------------------------------------------
def parse_pos(token):
    return [float(x) for x in token.split(",")]


def centroid_xy(ring):
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def mean_z(ring):
    return sum(p[2] for p in ring) / len(ring)


def point_in_polygon(x, y, ring):
    n = len(ring)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > y) != (yj > y)) and \
           (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _seg_intersect(p1, p2, p3, p4):
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if v > 1e-9:
            return 1
        if v < -1e-9:
            return -1
        return 0

    def on_seg(a, b, c):
        return (min(a[0], b[0]) - 1e-6 <= c[0] <= max(a[0], b[0]) + 1e-6 and
                min(a[1], b[1]) - 1e-6 <= c[1] <= max(a[1], b[1]) + 1e-6)

    o1 = orient(p1, p2, p3)
    o2 = orient(p1, p2, p4)
    o3 = orient(p3, p4, p1)
    o4 = orient(p3, p4, p2)
    if o1 != o2 and o3 != o4:
        return True
    if o1 == 0 and on_seg(p1, p2, p3):
        return True
    if o2 == 0 and on_seg(p1, p2, p4):
        return True
    if o3 == 0 and on_seg(p3, p4, p1):
        return True
    if o4 == 0 and on_seg(p3, p4, p2):
        return True
    return False


def polygons_overlap(a, b):
    """True if 2D rings a, b intersect (edge crossing or containment)."""
    na, nb = len(a), len(b)
    for i in range(na):
        for j in range(nb):
            if _seg_intersect(a[i], a[(i + 1) % na], b[j], b[(j + 1) % nb]):
                return True
    if point_in_polygon(a[0][0], a[0][1], b):
        return True
    if point_in_polygon(b[0][0], b[0][1], a):
        return True
    return False


def convex_hull(points):
    """Andrew's monotone chain. points: list of (x, y). Returns CCW ring."""
    pts = sorted(set((round(p[0], 4), round(p[1], 4)) for p in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def expand_hull(ring, margin):
    """Push each hull vertex outward from the centroid by `margin` units."""
    cx, cy = centroid_xy([(x, y) for x, y in ring])
    out = []
    for x, y in ring:
        dx, dy = x - cx, y - cy
        d = (dx * dx + dy * dy) ** 0.5
        if d < 1e-6:
            out.append((x, y))
        else:
            out.append((x + dx / d * margin, y + dy / d * margin))
    return out


def fmt_num(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


# ---------------------------------------------------------------------------
# v31 / v92 TerritoryData parsing.
# ---------------------------------------------------------------------------
def parse_attrs(tag_body):
    return dict(re.findall(r'(\w+)="([^"]*)"', tag_body))


def zone_path(root, zone):
    return os.path.join(root, "TerritoryData_%d.xml" % zone)


def live_ids(root, zone):
    t = read_text(zone_path(root, zone))
    return {
        "groups": set(int(x) for x in re.findall(r'<TerritoryGroup id="(\d+)"', t)),
        "terrs": set(int(x) for x in re.findall(r'<Territory id="(\d+)"', t)),
        "npcs": set(int(x) for x in re.findall(r'<Npc instanceId="(\d+)"', t)),
    }


def parse_group_spawns(text, gid):
    """Return list of Npc attr dicts for TerritoryGroup `gid`, or None."""
    m = re.search(r'<TerritoryGroup id="%d"[^>]*>.*?</TerritoryGroup>' % gid,
                  text, re.DOTALL)
    if not m:
        return None
    return [parse_attrs(b) for b in re.findall(r'<Npc\b([^>]*?)/?>', m.group(0))]


def parse_baseline_territories(text):
    """Yield (groupId, territoryId, ring[(x,y)...], templateId) per baseline
    territory that carries a spawn, in file order."""
    out = []
    for gm in re.finditer(r'<TerritoryGroup id="(\d+)"[^>]*>(.*?)</TerritoryGroup>',
                          text, re.DOTALL):
        gid = int(gm.group(1))
        for tm in re.finditer(r'<Territory id="(\d+)"[^>]*>(.*?)</Territory>',
                             gm.group(2), re.DOTALL):
            tid = int(tm.group(1))
            body = tm.group(2)
            ring = [tuple(parse_pos(p)[:2])
                    for p in re.findall(r'<Fence pos="([^"]+)"', body)]
            npc = re.search(r'<Npc\b([^>]*?)/?>', body)
            if not ring or not npc:
                continue
            tpl = int(parse_attrs(npc.group(1))["npcTemplateId"])
            out.append((gid, tid, ring, tpl))
    return out


def modal_profile(spawns):
    """{attr: most-common-value} over a donor group's spawns (lexicographic tie
    break, matching gen_spawn_specs)."""
    keys = set()
    for s in spawns:
        keys.update(s.keys())
    prof = {}
    for k in keys:
        c = Counter(s.get(k, "") for s in spawns)
        prof[k] = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return prof


# ---------------------------------------------------------------------------
# NpcData_13: template -> race (family) and template -> KR name.
# ---------------------------------------------------------------------------
def load_npcdata():
    nd = read_text(os.path.join(V92_DATASHEET, "NpcData_13.xml"))
    race, name = {}, {}
    for m in re.finditer(r'<Template\b([^>]*)>', nd):
        a = parse_attrs(m.group(1))
        if "id" in a:
            tid = int(a["id"])
            race[tid] = a.get("race", "")
            name[tid] = a.get("name", "")
    return race, name


# ---------------------------------------------------------------------------
# YAML value rendering + archetype-diff emission.
# ---------------------------------------------------------------------------
def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_spawn_value(alias, value):
    if alias in SPAWN_VEC:
        parts = value if isinstance(value, (list, tuple)) else parse_pos(value)
        return "[%s]" % ", ".join(fmt_num(float(p)) for p in parts)
    if alias in SPAWN_BOOL:
        return str(value).strip().lower()
    if alias in SPAWN_INT:
        return str(int(round(float(value))))
    if alias in SPAWN_DEC:
        return fmt_num(float(value))
    return q(str(value))


def spawn_base_rendered():
    return {a: render_spawn_value(a, v) for a, v in SPAWN_BASE.items()}


def emit_spawn_body(values, base_rendered):
    is_aggressive = (render_spawn_value(
        "isAggressiveMonster", values.get("isAggressiveMonster", "false")) == "true")
    effective = dict(base_rendered)
    if is_aggressive:
        defname = "RestoreSpawnAggressive"
        effective["isAggressiveMonster"] = render_spawn_value("isAggressiveMonster", "true")
    else:
        defname = "RestoreSpawnBase"
    override = []
    for alias in SPAWN_ORDER:
        if alias not in values:
            continue
        rendered = render_spawn_value(alias, values[alias])
        if alias in effective and rendered == effective[alias]:
            continue
        override.append("      %s: %s" % (alias, rendered))
    removed = [a for a in SPAWN_ORDER if a in effective and a not in values]
    return defname, override, removed


def emit_terr_body():
    """Restored territories take the ClassicTerritory constants exactly; no
    deviations, no removals."""
    return [], []


# ---------------------------------------------------------------------------
# Spawn value assembly.
# ---------------------------------------------------------------------------
def build_values(profile, inst, tpl, desc, pos):
    """profile: donor modal dict keyed by XML attr name. Returns a `values` dict
    keyed by DSL alias over SPAWN_ORDER (identity fields overridden per row)."""
    values = {}
    for alias in SPAWN_ORDER:
        if alias in IDENTITY_FIELDS:
            continue
        src = XML_ATTR.get(alias, alias)
        if src in profile:
            values[alias] = profile[src]
    values["npcInstanceId"] = inst
    values["npcTemplateId"] = tpl
    values["desc"] = desc
    values["pos"] = pos
    return values


# ---------------------------------------------------------------------------
# Main build.
# ---------------------------------------------------------------------------
def build():
    habitat = load_json(HABITAT_JSON)
    sweep = load_json(SWEEP_JSON)
    race_map, name_map = load_npcdata()

    v92 = read_text(zone_path(V92_DATASHEET, HZ))
    v31 = read_text(zone_path(V31_DATASHEET, HZ))
    ids92 = live_ids(V92_DATASHEET, HZ)
    ids31 = live_ids(V31_DATASHEET, HZ)

    # Re-runnability against an already-applied server tree. Once this spec is
    # applied, its own groups/territories/instances live in the v92 baseline, which
    # would fail the "free in both eras" checks and shift id allocation. Subtract the
    # spec's OWN footprint so the pristine id space is reconstructed deterministically:
    #   - managed groups: the 17 v17 group ids + the 2 fixed bespoke group ids.
    #   - territory/instance ids: everything at/above the allocation start (chosen
    #     above the pristine live max, so anything there is necessarily self-created).
    # ids31 needs no adjustment (these ids never existed in v31 by construction).
    managed_groups = {int(g["group_id"]) for g in habitat["gaps"]} | set(PRIOR_BESPOKE)
    ids92["groups"] = {g for g in ids92["groups"] if g not in managed_groups}
    ids92["terrs"] = {t for t in ids92["terrs"] if t < TERR_ID_START}
    ids92["npcs"] = {n for n in ids92["npcs"] if n < INST_ID_START}

    # Overlap check compares against GENUINE baseline mobs only; exclude this spec's
    # own already-applied groups to avoid self-overlap false positives.
    base_terrs = [bt for bt in parse_baseline_territories(v92)
                  if bt[0] not in managed_groups]

    base_rendered = spawn_base_rendered()

    # Donor profile cache (parsed live from v31).
    donor_cache = {}

    def donor_profile(gid):
        if gid not in donor_cache:
            sp = parse_group_spawns(v31, gid)
            if not sp:
                die("donor group %d not found in v31 TerritoryData_13" % gid)
            donor_cache[gid] = modal_profile(sp)
        return donor_cache[gid]

    # id allocators (assert free in BOTH eras).
    state = {"terr": TERR_ID_START, "inst": INST_ID_START}

    def alloc_terr():
        while True:
            tid = state["terr"]
            state["terr"] += ID_STEP
            if tid not in ids92["terrs"] and tid not in ids31["terrs"]:
                return tid

    def alloc_inst():
        while True:
            iid = state["inst"]
            state["inst"] += ID_STEP
            if iid not in ids92["npcs"] and iid not in ids31["npcs"]:
                return iid

    group_upserts = []      # (gid, desc)
    terr_upserts = []       # list of line-blocks
    spawn_upserts = []      # list of line-blocks
    emitted_terr_keys = set()  # (gid, tid) upserted, for stale-delete computation
    emitted_fences = []     # (gid, tid, ring2d, race) for overlap check
    id_report = []          # (gid, kind, n_terr, n_spawn, terr[min..max], inst[min..max])
    id_collisions = []
    clamps = []
    donor_used = {}         # gid -> (profile_kind, donor_gid or note)

    def emit_group(gid, desc, kind):
        group_upserts.append((gid, desc))
        return {"tmin": None, "tmax": None, "imin": None, "imax": None, "nt": 0, "ns": 0}

    def note_ids(rep, tid, iid):
        rep["tmin"] = tid if rep["tmin"] is None else min(rep["tmin"], tid)
        rep["tmax"] = tid if rep["tmax"] is None else max(rep["tmax"], tid)
        rep["imin"] = iid if rep["imin"] is None else min(rep["imin"], iid)
        rep["imax"] = iid if rep["imax"] is None else max(rep["imax"], iid)

    def emit_territory(gid, tid, desc, ring3d):
        emitted_terr_keys.add((gid, tid))
        override, removed = emit_terr_body()
        tb = ["    - huntingZoneId: %d" % HZ,
              "      groupId: %d" % gid,
              "      territoryId: %d" % tid,
              "      $extends: %s.ClassicTerritory" % SPAWN_PKG]
        if removed:
            tb.append("      $remove: [%s]" % ", ".join(removed))
        tb.extend(override)
        tb.append("      desc: %s" % q(desc))
        tb.append("      fences:")
        for x, y, z in ring3d:
            tb.append("        - [%s, %s, %s]" % (fmt_num(x), fmt_num(y), fmt_num(z)))
        terr_upserts.append(tb)

    def emit_spawn(gid, tid, profile, inst, tpl, desc, pos, overrides):
        values = build_values(profile, inst, tpl, desc, pos)
        for k, v in overrides.items():
            values[k] = v
        defname, override, removed = emit_spawn_body(values, base_rendered)
        sb = ["    - huntingZoneId: %d" % HZ,
              "      groupId: %d" % gid,
              "      territoryId: %d" % tid,
              "      $extends: %s.%s" % (SPAWN_PKG, defname)]
        if removed:
            sb.append("      $remove: [%s]" % ", ".join(removed))
        sb.extend(override)
        spawn_upserts.append(sb)

    # ---- 17 replicated v17 groups ------------------------------------------
    for grp in habitat["gaps"]:
        gid = int(grp["group_id"])
        desc = grp["group_desc_ko"]
        roster = [int(r["npcTemplateId"]) for r in grp["roster"]
                  if int(r["npcTemplateId"]) not in ROSTER_EXCLUDE]
        names = {int(r["npcTemplateId"]): r["name"] for r in grp["roster"]}
        fences = grp["v17_fences"]
        if len(fences) != grp["v17_territory_count"]:
            die("group %d: %d fences vs v17_territory_count %d"
                % (gid, len(fences), grp["v17_territory_count"]))
        if gid in ids92["groups"] or gid in ids31["groups"]:
            id_collisions.append(("group", gid))
            die("v17 group id %d is NOT free in both eras" % gid)

        # Resolve profile + roster + overrides per DECISION.
        overrides = {}
        if gid == 1300033:                         # DECISION: generic combat
            profile = dict(donor_profile(GENERIC_COMBAT_REF))
            overrides = dict(GENERIC_COMBAT_OVERRIDE)
            donor_used[gid] = ("combat", "DECISION generic combat (ref 1300018)")
        elif gid == 1300058:                       # DECISION: env from 1300054
            profile = donor_profile(1300054)
            donor_used[gid] = ("env", "DECISION env donor 1300054")
        elif gid == 1300029:                       # DECISION: fightable Terron
            profile = donor_profile(1300041)
            roster = [300942, 300943, 300945]
            names = {300942: "타락한 자연의 정령 테론A",
                     300943: "타락한 자연의 정령 테론B",
                     300945: "타락한 자연의 정령 테론 대장"}
            donor_used[gid] = ("donor", "DECISION Black Rift donor 1300041 (fightable roster)")
        else:
            dg = int(grp["donor"]["group_id"])
            profile = donor_profile(dg)
            donor_used[gid] = ("donor", "donor %d" % dg)

        # Density fix (2026-07-21): dominate the roster with the credit template and
        # raise spawnCount for the two under-dense quest-served groups.
        qd = QUEST_DENSITY.get(gid)
        if qd:
            if "force_roster" in qd:
                roster = list(qd["force_roster"])
            if "spawnCount" in qd:
                overrides = dict(overrides)
                overrides["spawnCount"] = qd["spawnCount"]
            donor_used[gid] = (donor_used[gid][0],
                               donor_used[gid][1] + " + density-fix %s" % qd)

        rep = emit_group(gid, desc, "v17")
        for i, fence in enumerate(fences):
            ring3d = [parse_pos(v) for v in fence]
            tid = alloc_terr()
            iid = alloc_inst()
            note_ids(rep, tid, iid)
            emit_territory(gid, tid, desc, ring3d)
            cx, cy = centroid_xy([(p[0], p[1]) for p in ring3d])
            cz = mean_z(ring3d)
            if not point_in_polygon(cx, cy, [(p[0], p[1]) for p in ring3d]):
                clamps.append((gid, tid, iid))
            tpl = roster[i % len(roster)]
            emit_spawn(gid, tid, profile, iid, tpl, names[tpl], [cx, cy, cz], overrides)
            emitted_fences.append((gid, tid, [(p[0], p[1]) for p in ring3d],
                                   race_map.get(tpl, "")))
            rep["nt"] += 1
            rep["ns"] += 1
        id_report.append((gid, "v17", rep["nt"], rep["ns"],
                          rep["tmin"], rep["tmax"], rep["imin"], rep["imax"]))

    # ---- 2 bespoke quest-target groups (per-marker; density fix 2026-07-21) -
    sweep_rec = {int(r["templateId"]): r for r in sweep["records"]
                 if r["hz"] == "13"}
    bespoke_group_ids = []
    scan = BESPOKE_GROUP_SCAN_START
    for _ in BESPOKE_DEFS:
        while scan in ids92["groups"] or scan in ids31["groups"]:
            id_collisions.append(("bespoke-group", scan))
            scan += 1
        bespoke_group_ids.append(scan)
        scan += 1

    for (quest, msrc, weights), gid in zip(BESPOKE_DEFS, bespoke_group_ids):
        markers = sweep_rec[msrc]["markers"]
        # Weighted per-marker template assignment (high-drop template dominates).
        assign = []
        for tpl, cnt in weights:
            assign.extend([tpl] * cnt)
        if len(assign) != len(markers):
            die("bespoke %s: weight sum %d != %d markers (source tpl %d)"
                % (quest, len(assign), len(markers), msrc))
        roster_ids = [t for t, _ in weights]
        desc = "IoD quest %s target habitat (%s)" % (
            quest, "/".join(str(t) for t in roster_ids))
        rep = emit_group(gid, desc, "bespoke")
        profile = dict(donor_profile(GENERIC_COMBAT_REF))
        overrides = dict(GENERIC_COMBAT_OVERRIDE)   # spawnCount 1 per marker
        donor_used[gid] = ("combat",
                           "DECISION generic combat, per-marker (bespoke quest %s)" % quest)
        for i, mk in enumerate(markers):
            tpl = assign[i]
            mx, my, mz = mk[0], mk[1], mk[2]
            m = BESPOKE_FENCE_MARGIN
            ring3d = [(mx - m, my - m, mz), (mx + m, my - m, mz),
                      (mx + m, my + m, mz), (mx - m, my + m, mz)]
            tid = alloc_terr()
            iid = alloc_inst()
            note_ids(rep, tid, iid)
            emit_territory(gid, tid, desc, ring3d)
            pos = [mx, my, mz]   # marker is the fence centre; always inside, no clamp
            tname = sweep_rec[tpl].get("v92_korean_npcdata") or name_map.get(tpl, str(tpl))
            emit_spawn(gid, tid, profile, iid, tpl, tname, pos, overrides)
            emitted_fences.append((gid, tid, [(p[0], p[1]) for p in ring3d],
                                   race_map.get(tpl, "")))
            rep["nt"] += 1
            rep["ns"] += 1
        id_report.append((gid, "bespoke", rep["nt"], rep["ns"],
                          rep["tmin"], rep["tmax"], rep["imin"], rep["imax"]))

    # ---- stale-territory cleanup (superseded prior bespoke layout) ----------
    # Prior (groupId, territoryId) not reproduced by this regeneration would be
    # left behind by upsert-only replay; delete them (cascade to child spawn).
    terr_deletes = []   # (gid, tid, iid, tpl)
    for gid, rows in sorted(PRIOR_BESPOKE.items()):
        for tid, iid, tpl in rows:
            if (gid, tid) not in emitted_terr_keys:
                terr_deletes.append((gid, tid, iid, tpl))

    # ---- geometric overlap check vs baseline -------------------------------
    overlap_warn = []
    overlap_err = []
    for gid, tid, ring, race in emitted_fences:
        for bgid, btid, bring, btpl in base_terrs:
            if len(bring) < 3 or len(ring) < 3:
                continue
            if polygons_overlap(ring, bring):
                brace = race_map.get(btpl, "")
                rec = (gid, tid, bgid, btid, btpl, race, brace)
                if race and brace and race == brace:
                    overlap_err.append(rec)
                else:
                    overlap_warn.append(rec)

    return {
        "group_upserts": group_upserts,
        "terr_upserts": terr_upserts,
        "spawn_upserts": spawn_upserts,
        "terr_deletes": terr_deletes,
        "id_report": id_report,
        "id_collisions": id_collisions,
        "clamps": clamps,
        "donor_used": donor_used,
        "bespoke_group_ids": bespoke_group_ids,
        "overlap_warn": overlap_warn,
        "overlap_err": overlap_err,
        "n_terr": len(terr_upserts),
        "n_spawn": len(spawn_upserts),
        "n_group": len(group_upserts),
    }


# ---------------------------------------------------------------------------
# Writer.
# ---------------------------------------------------------------------------
def write_lines(path, lines):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def write_spec(r):
    L = []
    L.append('spec:')
    L.append('  version: "1.0"')
    L.append('  schema: v92')
    L.append('')
    L.append('imports:')
    L.append('  - from: %s' % SPAWN_PKG)
    L.append('')
    L.append('# IoD padding Wave B: mob-habitat restoration (patch 001, classic-restoration).')
    L.append('#')
    L.append('# Doctrine:')
    L.append('#   rule 4 : fence geometry recovered from the v17.11 client TerritoryData.')
    L.append('#   rule 5 : mob habitat replication from v17; MOBS ONLY. Every group is an')
    L.append('#            APPROXIMATION (v17 geometry + v31 same-family donor attributes) and')
    L.append('#            is divergence-logged; no v17 group carried per-territory spawn points,')
    L.append('#            so template-per-territory placement is round-robin over the v17 roster.')
    L.append('#')
    L.append('# Generator : reforged/tools/dc-restore/gen_habitat_specs.py (deterministic).')
    L.append('# Inputs    : docs/plans/classic-restoration/iod/data/padding-habitat-gaps.json')
    L.append('#             docs/plans/classic-restoration/iod/data/padding-npcloc-sweep.json')
    L.append('#             v31 TerritoryData_13 (donor populations), v92 NpcData_13 (family/name).')
    L.append('#')
    L.append('# Spawn-density fix (padding-density-fixes.md adjudication, 2026-07-21):')
    L.append('#   Quest-served groups were too sparse for their quest kill targets. Two levers:')
    L.append('#   1300036 (quest 1349 Mini Orcan, 48-kill tpl 4): roster forced to [4] on all 4')
    L.append('#           territories, spawnCount 5  -> 20 concurrent tpl 4 (was 2).')
    L.append('#   1300038 (quest 1349 tpl 5): roster kept, spawnCount 2 -> 8 concurrent tpl 5.')
    L.append('#   Bespoke groups 1300060/1300061 now emit ONE small square territory (+/-%d u)'
             % int(BESPOKE_FENCE_MARGIN))
    L.append('#           per NpcLoc marker instead of one convex hull per template, using every')
    L.append('#           marker; templates split by drop weight (302:303 = 6:4 over 10 markers;')
    L.append('#           300944:300941 = 10:7 over 17 markers). spawnCount stays 1 per marker.')
    L.append('#   Superseded prior bespoke territories are removed (see territories.delete below).')
    L.append('#')
    L.append('# Scope: 17 replicated v17 mob groups + 2 bespoke quest-target groups (one territory')
    L.append('#   per NpcLoc marker), all HZ 13; %d territories, %d spawns total. Territories/'
             % (r["n_terr"], r["n_spawn"]))
    L.append('#   spawns extend the spawn-restore-standard archetypes; each row carries only its')
    L.append('#   deviations.')
    L.append('#')
    L.append('# Adjudicated DECISION defaults (no clean same-family v31 donor):')
    L.append('#   1300033 Rockcrawler   : roster 300541/300542/300540; generic combat profile')
    L.append('#                           (spawnCount 1, respawnTime 20000, randomPos true, ai 6).')
    L.append('#   1300058 Stone Head    : roster 301; environment profile from donor 1300054.')
    L.append('#   1300029 corrupt Terron: FIGHTABLE roster 300942/300943/300945; density copied')
    L.append('#                           from Black Rift group 1300041.')
    L.append('#   bespoke 1348 (302/303) and 1319 (300941/300944): generic combat profile,')
    L.append('#                           per-marker territories (density fix).')
    L.append('#')
    L.append('# Group ids (v17 originals, verified free in both eras): %s'
             % ", ".join(str(g) for g, _ in r["group_upserts"]
                         if g not in r["bespoke_group_ids"]))
    L.append('# Bespoke group ids (adjacent-free, both eras): %s'
             % ", ".join(str(g) for g in r["bespoke_group_ids"]))
    L.append('# Territory ids from %d; instance ids from %d (both above the live max in both eras).'
             % (TERR_ID_START, INST_ID_START))
    if r["clamps"]:
        L.append('# Position clamps (centroid outside fence): %d' % len(r["clamps"]))
    else:
        L.append('# Position sanity: every spawn position falls inside its fence (0 clamps).')
    if r["overlap_err"]:
        L.append('# WARNING: %d same-family baseline overlaps (see generator output).'
                 % len(r["overlap_err"]))
    L.append('')

    L.append('territoryGroups:')
    L.append('  upsert:')
    for gid, desc in r["group_upserts"]:
        L.append('    - huntingZoneId: %d' % HZ)
        L.append('      groupId: %d' % gid)
        L.append('      desc: %s' % q(desc))
    L.append('')

    L.append('territories:')
    L.append('  upsert:')
    for block in r["terr_upserts"]:
        L.extend(block)
    L.append('')
    if r["terr_deletes"]:
        L.append('  # Density fix (2026-07-21): remove prior bespoke territories the per-marker')
        L.append('  # regeneration supersedes (composite key not reproduced above). Cascade to')
        L.append('  # their child spawn. Absent-delete warnings on re-replay are expected.')
        L.append('  delete:')
        for gid, tid, iid, tpl in r["terr_deletes"]:
            L.append('    - huntingZoneId: %d' % HZ)
            L.append('      groupId: %d' % gid)
            L.append('      territoryId: %d     # prior tpl %d spawn %d, cascades'
                     % (tid, tpl, iid))
        L.append('')

    L.append('territorySpawns:')
    L.append('  upsert:')
    for block in r["spawn_upserts"]:
        L.extend(block)

    write_lines(OUT_SPEC, L)


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    r = build()
    write_spec(r)

    print("=== 15-iod-mob-habitats.yaml ===")
    print("groups      : %d (17 v17 + %d bespoke)"
          % (r["n_group"], len(r["bespoke_group_ids"])))
    print("territories : %d" % r["n_terr"])
    print("spawns      : %d" % r["n_spawn"])
    print("bespoke gids: %s" % r["bespoke_group_ids"])
    print("")
    print("Per-group (gid  kind  n_terr  n_spawn  terr[min..max]  inst[min..max]  profile):")
    for gid, kind, nt, ns, tmin, tmax, imin, imax in r["id_report"]:
        print("  %d  %-7s %2d  %2d  terr[%d..%d]  inst[%d..%d]  %s"
              % (gid, kind, nt, ns, tmin, tmax, imin, imax, r["donor_used"][gid][1]))
    print("")
    print("id collisions resolved: %s" % (r["id_collisions"] or "(none)"))
    print("position clamps: %d %s" % (len(r["clamps"]), r["clamps"] or ""))
    print("")
    print("stale-territory deletes (superseded prior bespoke): %d" % len(r["terr_deletes"]))
    for gid, tid, iid, tpl in r["terr_deletes"]:
        print("  delete territory %d/%d (prior tpl %d spawn %d, cascades)"
              % (gid, tid, tpl, iid))
    print("")
    print("OVERLAP CHECK vs baseline TerritoryData_13:")
    print("  same-family (HARD ERROR): %d" % len(r["overlap_err"]))
    for gid, tid, bgid, btid, btpl, race, brace in r["overlap_err"]:
        print("    emit g%d/t%d (%s) overlaps baseline g%d/t%d tpl%d (%s)"
              % (gid, tid, race, bgid, btid, btpl, brace))
    print("  different-family / prop (warning): %d" % len(r["overlap_warn"]))
    for gid, tid, bgid, btid, btpl, race, brace in r["overlap_warn"]:
        print("    emit g%d/t%d (%s) overlaps baseline g%d/t%d tpl%d (%s)"
              % (gid, tid, race, bgid, btid, btpl, brace))
    print("")
    print("")
    print("Roster exclusions (named uniques already live in baseline):")
    for tpl, reason in sorted(ROSTER_EXCLUDE.items()):
        print("  tpl %d: %s" % (tpl, reason))
    print("")
    print("Wrote: " + OUT_SPEC)

    if r["overlap_err"]:
        print("", file=sys.stderr)
        print("HARD ERROR: %d same-family baseline overlap(s) remain; review required."
              % len(r["overlap_err"]), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
