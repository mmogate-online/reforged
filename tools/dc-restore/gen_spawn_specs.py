#!/usr/bin/env python
"""Stage 2 IoD spawn-restoration spec generator (patch 001).

Deterministic. Re-runs byte-identical (fixed iteration order, no timestamps).

Emits two DSL specs:

  02-iod-spawn-restore.yaml    17 deleted v17-only territory groups restored in HZ 13
  03-iod-spawn-removals.yaml   v31-only group + Sandom cluster + Ellonia removals

Source precedence (per team-lead brief and TRACKER settled decisions 13-15):

  * Group roster + geometry + population mapping :
        batch-3-spawn-plan.json (prior session's in-game-validated reconstruction).
        Its per-group territory rings are the v17 client fences (verified equal to
        v17-territories.json), and its template-per-territory assignment and
        spawnCount sizing are treated as pre-seeded validated decisions.
  * Spawn-entry attributes (ai, respawn, aggro, view, alert, ...) :
        modal attribute set of the SAME npcTemplateId across surviving v31 zone-13
        spawns (v31-spawns.json). Templates absent from v31 fall back to a curated
        same-family donor (spawn_restore.py FAMILY_DONOR) and are FLAGGED.
  * Group / territory / instance ids :
        batch-3 allocation, each re-verified free against the live v92 file.
  * Spawn position :
        territory fence-ring centroid, point-in-polygon validated (clamp + warn).

Run:  python gen_spawn_specs.py
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
PLAN_DIR = r"D:\dev\mmogate\github\reforged-server-content\reforged\docs\plans\iod-alpha-content-loop"
BATCH3 = os.path.join(PLAN_DIR, "batch-3-spawn-plan.json")
V31_SPAWNS = os.path.join(PLAN_DIR, "data", "v31-spawns.json")
V92_DATASHEET = r"D:\dev\mmogate\tera92\server\Datasheet"

OUT_DIR = r"D:\dev\mmogate\github\reforged-server-content\reforged\specs\patches\001"
OUT_RESTORE = os.path.join(OUT_DIR, "02-iod-spawn-restore.yaml")
OUT_REMOVE = os.path.join(OUT_DIR, "03-iod-spawn-removals.yaml")

HZ = 13

# The 17 deleted v17-only groups, in emission order (classic historical ids).
CLASSIC_GROUP_IDS = [
    1300019, 1300020, 1300021, 1300022, 1300025, 1300028, 1300029, 1300030,
    1300031, 1300032, 1300033, 1300034, 1300036, 1300037, 1300038, 1300057,
    1300058,
]

# Same-family donor for templates with no v31 spawn anywhere in the zone.
# Curated in spawn_restore.py (prior art); every donor is v31-covered.
FAMILY_DONOR = {
    304: 300921, 300920: 300921, 300921: 300921,
    300910: 300910, 300911: 300910,
    300930: 300931, 300931: 300931, 300932: 300932, 300933: 300932,
    300941: 300942, 300942: 300942, 300943: 300942, 300944: 300942, 300945: 300942,
    302: 300942, 303: 300942,
    601: 300951, 300951: 300951, 300960: 300960,
    2: 2, 3: 2,
    4: 901, 5: 901, 901: 901, 902: 901, 1002: 901,
    102: 102, 301: 102, 1011: 1011,
    300541: 300921, 300542: 300921,
}

# --- removals (TRACKER settled decisions 13-15, 20) ---
REMOVE_GROUPS = [(13, 1300140), (13, 1300141), (213, 21300004)]
SANDOM_TEMPLATES = [1054, 1150, 1151, 1152, 1153, 1501]
ELLONIA_TEMPLATE = 8000
ELLONIA_ZONE = 64
# T-cat Exchanger: removed from IoD entirely (decision 20, deliberate divergence
# from the v17 registry; its medal currency does not exist on this build).
TCAT_TEMPLATE = 9000
TCAT_ZONE = 64

# ---------------------------------------------------------------------------
# Spawn attribute typing / emission order (DSL aliases == XML attr names).
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
SPAWN_STR = {"desc", "aggroSendToTerritory", "aggroIgnorePartyId", "popupMsg",
             "respawnRandomTime"}
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

# Per-spawn fields set from batch-3 / geometry, never from the v31 donor pattern.
OVERRIDE_FIELDS = {"npcInstanceId", "npcTemplateId", "memberId", "desc", "pos",
                   "spawnCount", "isAggressiveMonster"}

TERR_TYPE = "normal"

# ---------------------------------------------------------------------------
# Reusable archetypes (packages/spawn-restore-standard). A spawn/territory emits
# "$extends: <archetype>" plus only the fields that deviate from (or are absent
# in) the archetype, instead of a full attribute dump. The bases here MUST mirror
# the package definitions exactly; a field is suppressed only when its rendered
# value equals the archetype's, so the effective (post-merge) value is unchanged.
# ---------------------------------------------------------------------------
SPAWN_PKG = "spawn-restore-standard"

# RestoreSpawnBase: 31 fields at tau>=0.9 across the 217 restored spawns. Values
# are raw inputs rendered through render_spawn_value, identical to a spawn's own
# field rendering, so comparison is exact. isAggressiveMonster/isReturn hold the
# non-aggressive default; aggressive rows extend RestoreSpawnAggressive instead.
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

# ClassicTerritory: 6 fields constant across the 217 restored territories.
TERR_BASE = {
    "type": "normal", "addMaxZ": "256.000000", "subtractMinZ": "0.000000",
    "eventId": "0", "randomPosMinDist": "100.000000",
    "peaceMoveNpcCheckDist": "100.000000",
}
TERR_OPTIONAL = ("eventId", "randomPosMinDist", "peaceMoveNpcCheckDist")


def die(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def load_json(path):
    return json.load(io.open(path, encoding="utf-8"))


def read_text(path):
    return io.open(path, encoding="utf-8").read()


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
    """Ray-casting point-in-polygon on the (x, y) fence vertices."""
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


def fmt_num(v):
    """Compact fixed-point rendering (matches source vertex precision)."""
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


# ---------------------------------------------------------------------------
# batch-3 parsing.
# ---------------------------------------------------------------------------
def parse_attrs(tag_body):
    return dict(re.findall(r'(\w+)="([^"]*)"', tag_body))


def parse_batch3_group(xml):
    """Return a list of territory dicts from a batch-3 group xml.

    Each territory: {id, desc, addMaxZ, subtractMinZ, randomPosMinDist,
                     peaceMoveNpcCheckDist, eventId, ring([x,y,z]...), npc(attrs)}.
    """
    territories = []
    for tmatch in re.finditer(r"<Territory\b([^>]*)>(.*?)</Territory>", xml, re.DOTALL):
        tattrs = parse_attrs(tmatch.group(1))
        body = tmatch.group(2)
        ring = [parse_pos(p) for p in re.findall(r'<Fence pos="([^"]+)"', body)]
        npc_match = re.search(r"<Npc\b([^>]*?)/?>", body)
        npc = parse_attrs(npc_match.group(1)) if npc_match else {}
        territories.append({
            "id": int(tattrs["id"]),
            "desc": tattrs.get("desc", ""),
            "addMaxZ": tattrs.get("addMaxZ", "256.000000"),
            "subtractMinZ": tattrs.get("subtractMinZ", "0.000000"),
            "randomPosMinDist": tattrs.get("randomPosMinDist"),
            "peaceMoveNpcCheckDist": tattrs.get("peaceMoveNpcCheckDist"),
            "eventId": tattrs.get("eventId"),
            "ring": ring,
            "npc": npc,
        })
    return territories


# ---------------------------------------------------------------------------
# v31 modal attribute patterns.
# ---------------------------------------------------------------------------
def build_v31_patterns():
    """{templateId: {attr: modal_value}} over surviving v31 zone-13 spawns."""
    data = load_json(V31_SPAWNS)
    zone = next(z for z in data["zones"] if z["hz"] == HZ)
    by_tpl = {}
    for grp in zone["groups"]:
        for terr in grp["territories"]:
            for npc in terr["npcs"]:
                by_tpl.setdefault(int(npc["npcTemplateId"]), []).append(npc)
    patterns = {}
    for tpl, spawns in by_tpl.items():
        modal = {}
        keys = set()
        for s in spawns:
            keys.update(s.keys())
        for k in keys:
            counter = Counter(s.get(k, "") for s in spawns)
            # deterministic: highest count, then lexicographic value.
            best = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            modal[k] = best
        patterns[tpl] = modal
    return patterns


def resolve_pattern(tpl, patterns):
    """(pattern dict, donor_tpl, is_fallback) for a template."""
    if tpl in patterns:
        return patterns[tpl], tpl, False
    donor = FAMILY_DONOR.get(tpl)
    if donor is None or donor not in patterns:
        die("no v31 pattern and no covered donor for template %d" % tpl)
    return patterns[donor], donor, True


# ---------------------------------------------------------------------------
# Live v92 id scan.
# ---------------------------------------------------------------------------
def zone_path(zone):
    return os.path.join(V92_DATASHEET, "TerritoryData_%d.xml" % zone)


def live_ids(zone):
    t = read_text(zone_path(zone))
    return {
        "text": t,
        "groups": set(int(x) for x in re.findall(r'<TerritoryGroup id="(\d+)"', t)),
        "terrs": set(int(x) for x in re.findall(r'<Territory id="(\d+)"', t)),
        "npcs": set(int(x) for x in re.findall(r'<Npc instanceId="(\d+)"', t)),
    }


def scan_spawns(zone_text):
    """Yield (groupId, territoryId, instanceId, templateId, desc) with context."""
    cur_g = cur_t = None
    for m in re.finditer(
            r'<TerritoryGroup id="(\d+)"|<Territory id="(\d+)"|<Npc\b([^>]*?)/?>',
            zone_text):
        if m.group(1):
            cur_g = int(m.group(1))
        elif m.group(2):
            cur_t = int(m.group(2))
        elif m.group(3):
            a = parse_attrs(m.group(3))
            yield (cur_g, cur_t, int(a["instanceId"]),
                   int(a["npcTemplateId"]), a.get("desc", ""))


# ---------------------------------------------------------------------------
# YAML value rendering.
# ---------------------------------------------------------------------------
def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


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


# ---------------------------------------------------------------------------
# Archetype-diff emission (spawns / territories).
# ---------------------------------------------------------------------------
def _spawn_base_rendered():
    return {a: render_spawn_value(a, v) for a, v in SPAWN_BASE.items()}


def emit_spawn_body(values, base_rendered):
    """Emit ($extends def name, [override lines], [removed keys]) for a spawn.

    A field is inherited (suppressed) when its rendered value equals the
    archetype's. Aggressive spawns extend RestoreSpawnAggressive, whose only
    difference from the base is isAggressiveMonster=true. Base fields absent from
    `values` are listed for $remove so the merged result keeps exactly the
    original key set.
    """
    is_aggressive = (render_spawn_value("isAggressiveMonster",
                                        values.get("isAggressiveMonster", "false"))
                     == "true")
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


def emit_terr_body(terr):
    """Emit ([override lines], [removed keys]) for a territory against ClassicTerritory."""
    provided = {
        "type": TERR_TYPE,
        "addMaxZ": terr["addMaxZ"],
        "subtractMinZ": terr["subtractMinZ"],
    }
    if terr["eventId"] is not None:
        provided["eventId"] = str(int(terr["eventId"]))
    if terr["randomPosMinDist"] is not None:
        provided["randomPosMinDist"] = terr["randomPosMinDist"]
    if terr["peaceMoveNpcCheckDist"] is not None:
        provided["peaceMoveNpcCheckDist"] = terr["peaceMoveNpcCheckDist"]
    order = ["type", "addMaxZ", "subtractMinZ", "eventId", "randomPosMinDist",
             "peaceMoveNpcCheckDist"]
    override = []
    for alias in order:
        if alias not in provided:
            continue
        if provided[alias] == TERR_BASE[alias]:
            continue
        override.append("      %s: %s" % (alias, provided[alias]))
    removed = [a for a in TERR_OPTIONAL if a not in provided]
    return override, removed


# ---------------------------------------------------------------------------
# Build the restore spec.
# ---------------------------------------------------------------------------
def build_restore():
    batch = load_json(BATCH3)
    groups = {g["gid"]: g for g in batch["zone13_groups"]}
    patterns = build_v31_patterns()
    live = live_ids(HZ)
    spawn_base_rendered = _spawn_base_rendered()

    warnings = []
    fallbacks = {}          # template -> donor (flagged)
    clamps = []             # (groupId, territoryId, instanceId)
    group_upserts = []      # (gid, desc)
    terr_upserts = []       # list of line-blocks
    spawn_upserts = []      # list of line-blocks
    id_report = []          # (gid, n_terr, terr_min, terr_max, npc_min, npc_max)

    for gid in CLASSIC_GROUP_IDS:
        if gid in live["groups"]:
            die("classic group id %d is NOT free in live v92" % gid)
        g = groups[gid]
        tpl_names = g.get("template_names", {})
        territories = parse_batch3_group(g["xml"])
        tmin = tmax = nmin = nmax = None

        group_upserts.append((gid, g["desc"]))

        for terr in territories:
            tid = terr["id"]
            if tid in live["terrs"]:
                die("territory id %d (group %d) is NOT free in live v92" % (tid, gid))
            ring = terr["ring"]
            npc = terr["npc"]
            tpl = int(npc["npcTemplateId"])
            inst = int(npc["instanceId"])
            if inst in live["npcs"]:
                die("instance id %d (group %d) is NOT free in live v92" % (inst, gid))

            tmin = tid if tmin is None else min(tmin, tid)
            tmax = tid if tmax is None else max(tmax, tid)
            nmin = inst if nmin is None else min(nmin, inst)
            nmax = inst if nmax is None else max(nmax, inst)

            # --- territory block ($extends ClassicTerritory + deviations) ---
            terr_override, terr_removed = emit_terr_body(terr)
            tb = []
            tb.append("    - huntingZoneId: %d" % HZ)
            tb.append("      groupId: %d" % gid)
            tb.append("      territoryId: %d" % tid)
            tb.append("      $extends: %s.ClassicTerritory" % SPAWN_PKG)
            if terr_removed:
                tb.append("      $remove: [%s]" % ", ".join(terr_removed))
            tb.extend(terr_override)
            tb.append("      desc: %s" % q(terr["desc"]))
            tb.append("      fences:")
            for x, y, z in ring:
                tb.append("        - [%s, %s, %s]" % (fmt_num(x), fmt_num(y), fmt_num(z)))
            terr_upserts.append(tb)

            # --- spawn position (centroid, PIP-validated) ---
            cx, cy = centroid_xy(ring)
            cz = mean_z(ring)
            if not point_in_polygon(cx, cy, ring):
                clamps.append((gid, tid, inst))
                warnings.append(
                    "group %d terr %d inst %d: centroid (%.1f,%.1f) outside fence; "
                    "kept as clamped position." % (gid, tid, inst, cx, cy))
            pos = [cx, cy, cz]

            # --- spawn attributes: v31 modal pattern (+ flagged fallback) ---
            pattern, donor, is_fb = resolve_pattern(tpl, patterns)
            if is_fb:
                fallbacks[tpl] = donor

            values = {}
            for alias in SPAWN_ORDER:
                if alias in OVERRIDE_FIELDS:
                    continue
                src = "instanceId" if alias == "npcInstanceId" else alias
                if src in pattern:
                    values[alias] = pattern[src]
            # overrides
            values["npcInstanceId"] = inst
            values["npcTemplateId"] = tpl
            values["memberId"] = int(npc.get("memberId", 0))
            values["spawnCount"] = int(npc.get("spawnCount", 1))
            values["isAggressiveMonster"] = npc.get("isAggressiveMonster", "false")
            values["pos"] = pos
            values["desc"] = tpl_names.get(str(tpl), "복원 스폰 %d" % tpl)

            defname, override, removed = emit_spawn_body(values, spawn_base_rendered)
            sb = []
            sb.append("    - huntingZoneId: %d" % HZ)
            sb.append("      groupId: %d" % gid)
            sb.append("      territoryId: %d" % tid)
            sb.append("      $extends: %s.%s" % (SPAWN_PKG, defname))
            if removed:
                sb.append("      $remove: [%s]" % ", ".join(removed))
            sb.extend(override)
            spawn_upserts.append(sb)

        id_report.append((gid, len(territories), tmin, tmax, nmin, nmax))

    return {
        "group_upserts": group_upserts,
        "terr_upserts": terr_upserts,
        "spawn_upserts": spawn_upserts,
        "warnings": warnings,
        "fallbacks": fallbacks,
        "clamps": clamps,
        "id_report": id_report,
        "n_terr": sum(r[1] for r in id_report),
    }


# ---------------------------------------------------------------------------
# Build the removals spec.
# ---------------------------------------------------------------------------
def build_removals():
    live213 = live_ids(213)
    live13 = live_ids(HZ)
    live64 = live_ids(ELLONIA_ZONE)

    group_deletes = []          # (zone, gid, present)
    for zone, gid in REMOVE_GROUPS:
        present = gid in (live13 if zone == 13 else live213)["groups"]
        group_deletes.append((zone, gid, present))

    # Sandom spawns: enumerate exact composite keys from live 213.
    # A Sandom spawn whose parent group is itself being deleted is 'covered':
    # the group delete removes the whole subtree, so emitting a separate spawn
    # delete would target an element the group delete already removed (E500).
    remove_gids = {gid for _, gid in REMOVE_GROUPS}
    found = {}
    for g, t, inst, tpl, desc in scan_spawns(live213["text"]):
        if tpl in SANDOM_TEMPLATES:
            found.setdefault(tpl, []).append((g, t, inst, desc))
    sandom_rows = []            # (tpl, group, terr, inst, desc, covered_by_group_delete)
    sandom_present, sandom_absent = [], []
    for tpl in SANDOM_TEMPLATES:
        if tpl in found:
            for g, t, inst, desc in found[tpl]:
                sandom_rows.append((tpl, g, t, inst, desc, g in remove_gids))
            sandom_present.append(tpl)
        else:
            sandom_absent.append(tpl)

    # Ellonia spawn (zone 64 template 8000): present only if a spawn exists.
    ellonia_rows = []
    tcat_rows = []
    for g, t, inst, tpl, desc in scan_spawns(live64["text"]):
        if tpl == ELLONIA_TEMPLATE:
            ellonia_rows.append((g, t, inst, desc))
        if tpl == TCAT_TEMPLATE:
            tcat_rows.append((g, t, inst, desc))

    return {
        "group_deletes": group_deletes,
        "sandom_rows": sandom_rows,
        "sandom_present": sandom_present,
        "sandom_absent": sandom_absent,
        "ellonia_rows": ellonia_rows,
        "tcat_rows": tcat_rows,
    }


# ---------------------------------------------------------------------------
# Writers.
# ---------------------------------------------------------------------------
def write_lines(path, lines):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def write_restore(r):
    L = []
    L.append('spec:')
    L.append('  version: "1.0"')
    L.append('  schema: v92')
    L.append('')
    L.append('imports:')
    L.append('  - from: %s' % SPAWN_PKG)
    L.append('')
    L.append('# IoD patch 001 Stage 2: spawn restoration - 17 deleted v17-only groups (HZ 13).')
    L.append('#')
    L.append('# Sources:')
    L.append('#   roster/geometry/population : batch-3-spawn-plan.json (prior session,')
    L.append('#       in-game-validated). Territory rings are the v17 client fences')
    L.append('#       (verified equal to v17-territories.json); template-per-territory and')
    L.append('#       spawnCount sizing are pre-seeded validated decisions.')
    L.append('#   spawn attributes           : modal attribute set of the same npcTemplateId')
    L.append('#       across surviving v31 zone-13 spawns (v31-spawns.json). Templates absent')
    L.append('#       from v31 use a curated same-family donor (see FLAGGED fallbacks below).')
    L.append('#   ids                        : batch-3 allocation, re-verified free in live v92.')
    L.append('#   spawn position             : fence-ring centroid, point-in-polygon validated.')
    L.append('# Classifier verdicts         : classification-spawns.json (17 RESTORE rows, HZ 13).')
    L.append('#')
    L.append('# Group ids (all classic, verified free): %s'
             % ", ".join(str(g) for g in CLASSIC_GROUP_IDS))
    L.append('# Territory id block: 13014260..13016420   Instance id block: 13472950..13475110')
    L.append('#   (both allocated above the live max in the zone numbering convention).')
    if r["fallbacks"]:
        L.append('#')
        L.append('# FLAGGED attribute fallbacks (template has no v31 spawn; same-family donor used):')
        for tpl in sorted(r["fallbacks"]):
            L.append('#   template %d -> v31 donor %d' % (tpl, r["fallbacks"][tpl]))
    if r["clamps"]:
        L.append('#')
        L.append('# Position clamps (centroid fell outside fence): %d' % len(r["clamps"]))
    else:
        L.append('#')
        L.append('# Position sanity: every spawn centroid falls inside its territory fence (0 clamps).')
    L.append('#')
    L.append('# Territories and spawns extend the spawn-restore-standard archetypes')
    L.append('#   (ClassicTerritory / RestoreSpawnBase / RestoreSpawnAggressive); each entry')
    L.append('#   carries only the fields that deviate from its archetype.')
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

    L.append('territorySpawns:')
    L.append('  upsert:')
    for block in r["spawn_upserts"]:
        L.extend(block)

    write_lines(OUT_RESTORE, L)


def write_removals(m):
    L = []
    L.append('spec:')
    L.append('  version: "1.0"')
    L.append('  schema: v92')
    L.append('')
    L.append('# IoD patch 001 Stage 2: spawn removals (TRACKER settled decisions 13-15).')
    L.append('#')
    L.append('# 1. v31-only territory groups absent from the v17 roster: HZ 13 groups')
    L.append('#    1300140 / 1300141 and HZ 213 group 21300004 (Alliance Quest).')
    L.append('# 2. Sandom cluster (HZ 213): merchant + instructors + event teleportal.')
    L.append('#    Classic arrangement keeps shopping at Tower Base (64); the garden (213)')
    L.append('#    is services-only. Enumerated by exact composite key from the live file.')
    L.append('# 3. Ellonia medal store (HZ 64 template 8000): removed as a world spawn.')
    L.append('# 4. T-cat Exchanger (HZ 64 template 9000): removed as a world spawn')
    L.append('#    (decision 20, deliberate divergence from the v17 registry; its medal')
    L.append('#    currency does not exist on this build). Villager-menu wiring is handled')
    L.append('#    separately by the shops generator (04); this spec only removes the spawn.')
    L.append('#')
    L.append('# NpcData template rows for the removed NPCs are intentionally LEFT in place')
    L.append('# (dormant templates, retail-consistent). This spec only removes placements.')
    L.append('#')
    L.append('# Enumeration results (live v92 at generation time):')
    for zone, gid, present in m["group_deletes"]:
        L.append('#   group %d (HZ %d): %s' % (gid, zone, "present" if present else "ALREADY ABSENT"))
    for tpl in SANDOM_TEMPLATES:
        rows = [row for row in m["sandom_rows"] if row[0] == tpl]
        if rows:
            parts = []
            for tpl_, g, t, inst, desc, covered in rows:
                tag = " (removed by group %d delete)" % g if covered else ""
                parts.append("g%d/t%d/i%d%s" % (g, t, inst, tag))
            L.append('#   Sandom template %d: %s' % (tpl, ", ".join(parts)))
        else:
            L.append('#   Sandom template %d: ALREADY ABSENT' % tpl)
    if m["ellonia_rows"]:
        for g, t, inst, desc in m["ellonia_rows"]:
            L.append('#   Ellonia 8000: g%d/t%d/i%d' % (g, t, inst))
    else:
        L.append('#   Ellonia template %d (HZ %d): no world spawn (template-only, ALREADY ABSENT)'
                 % (ELLONIA_TEMPLATE, ELLONIA_ZONE))
    if m["tcat_rows"]:
        for g, t, inst, desc in m["tcat_rows"]:
            L.append('#   T-cat 9000: g%d/t%d/i%d' % (g, t, inst))
    else:
        L.append('#   T-cat template %d (HZ %d): no world spawn (template-only, ALREADY ABSENT)'
                 % (TCAT_TEMPLATE, TCAT_ZONE))
    L.append('')

    # territorySpawns deletes (Sandom not covered by a group delete + Ellonia + T-cat).
    spawn_delete_rows = [row for row in m["sandom_rows"] if not row[5]]
    ellonia_delete = [(ELLONIA_ZONE, ELLONIA_TEMPLATE) + row for row in m["ellonia_rows"]]
    tcat_delete = [(TCAT_ZONE, TCAT_TEMPLATE) + row for row in m["tcat_rows"]]
    if spawn_delete_rows or ellonia_delete or tcat_delete:
        L.append('territorySpawns:')
        L.append('  delete:')
        for tpl, g, t, inst, desc, covered in spawn_delete_rows:
            L.append('    - huntingZoneId: 213')
            L.append('      groupId: %d' % g)
            L.append('      territoryId: %d' % t)
            L.append('      npcInstanceId: %d  # Sandom template %d' % (inst, tpl))
        for zone, tpl, g, t, inst, desc in ellonia_delete + tcat_delete:
            label = "Ellonia" if tpl == ELLONIA_TEMPLATE else "T-cat Exchanger"
            L.append('    - huntingZoneId: %d' % zone)
            L.append('      groupId: %d' % g)
            L.append('      territoryId: %d' % t)
            L.append('      npcInstanceId: %d  # %s template %d' % (inst, label, tpl))
        L.append('')

    # territoryGroups deletes.
    L.append('territoryGroups:')
    L.append('  delete:')
    for zone, gid, present in m["group_deletes"]:
        L.append('    - huntingZoneId: %d' % zone)
        L.append('      groupId: %d' % gid)

    write_lines(OUT_REMOVE, L)


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    r = build_restore()
    write_restore(r)
    m = build_removals()
    write_removals(m)

    print("=== 02-iod-spawn-restore.yaml ===")
    print("groups restored : %d" % len(r["group_upserts"]))
    print("territories     : %d" % r["n_terr"])
    print("spawns          : %d" % len(r["spawn_upserts"]))
    print("")
    print("Per-group id allocation (gid: n_terr  terr[min..max]  inst[min..max]):")
    for gid, n, tmin, tmax, nmin, nmax in r["id_report"]:
        print("  %d: %2d  terr[%d..%d]  inst[%d..%d]" % (gid, n, tmin, tmax, nmin, nmax))
    print("")
    print("Attribute-pattern fallbacks (flagged in spec header):")
    if r["fallbacks"]:
        for tpl in sorted(r["fallbacks"]):
            print("  template %d -> v31 donor %d" % (tpl, r["fallbacks"][tpl]))
    else:
        print("  (none)")
    print("")
    print("Position clamps: %d" % len(r["clamps"]))
    for c in r["clamps"]:
        print("  group %d terr %d inst %d" % c)
    print("")
    print("=== 03-iod-spawn-removals.yaml ===")
    for zone, gid, present in m["group_deletes"]:
        print("  group %d (HZ %d): %s" % (gid, zone, "PRESENT" if present else "ABSENT"))
    print("  Sandom present: %s" % m["sandom_present"])
    print("  Sandom absent : %s" % m["sandom_absent"])
    explicit = [row for row in m["sandom_rows"] if not row[5]]
    covered = [row for row in m["sandom_rows"] if row[5]]
    print("  Sandom explicit spawn deletes: %d" % len(explicit))
    for tpl, g, t, inst, desc, cov in covered:
        print("  Sandom template %d (i%d) removed by group %d delete" % (tpl, inst, g))
    print("  Ellonia spawn deletes: %d %s" % (
        len(m["ellonia_rows"]), "" if m["ellonia_rows"] else "(template-only, absent)"))
    print("  T-cat spawn deletes: %d %s" % (
        len(m["tcat_rows"]), "" if m["tcat_rows"] else "(template-only, absent)"))
    for g, t, inst, desc in m["tcat_rows"]:
        print("    T-cat 9000: g%d/t%d/i%d" % (g, t, inst))
    print("")
    print("Wrote:")
    print("  " + OUT_RESTORE)
    print("  " + OUT_REMOVE)


if __name__ == "__main__":
    main()
