#!/usr/bin/env python
"""Stage 1 IoD section-restoration spec generator (patch 001).

Deterministic. Re-runs byte-identical (fixed iteration order, no timestamps).

Emits two DSL specs from three authoritative area sources:

  00-iod-region-strings.yaml   regionStrings upsert (Terron Run 13036, Leander's Outpost 13015)
  01-iod-area-sections.yaml    areaSections upsert/delete on continent 13 / ATW_Death_P

Source precedence (per team-lead brief and section-mapping.json):
  * Section ATTRIBUTES  : v31 classic server row (ATW_P) wins.
  * Fence GEOMETRY      : v31 ring by default; if v31 and v17 disagree beyond
                          decimal rounding (>0.01u on any vertex, or a differing
                          vertex count) the v17 client ring wins and a warning
                          is printed.
  * Section XML id      : reuse the v92 commented-out id for the Tower Base
                          cluster; otherwise prefer the v31 row id when it is
                          free in the live v92 file, else the lowest free id.

Run:  python gen_section_specs.py
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# Paths (absolute, per project rules).
# ---------------------------------------------------------------------------
V31_AREA = r"Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet\AreaData\AreaData_13_ATW_P.xml"
V17_AREA = r"D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA\Area\Area-00004.xml"
V92_AREA = r"D:\dev\mmogate\tera92\server\Datasheet\AreaData\AreaData_13_ATW_Death_P.xml"

OUT_DIR = r"D:\dev\mmogate\github\reforged-server-content\reforged\specs\patches\001"
OUT_REGION = os.path.join(OUT_DIR, "00-iod-region-strings.yaml")
OUT_SECTIONS = os.path.join(OUT_DIR, "01-iod-area-sections.yaml")

CONTINENT_ID = 13
AREA_NAME = "ATW_Death_P"
MAIN_SECTION_V92_ID = 4          # nameId 13001, live parent of every sub-section
FENCE_TOLERANCE = 0.01           # units; disagreement threshold for v31-vs-v17

# ---------------------------------------------------------------------------
# Restoration plan. Order here is the emission order (deterministic).
# ---------------------------------------------------------------------------
# Each entry: v31 nameId to pull the row from, the nameId to EMIT, placement,
# and an optional desc override.
RESTORE_PLAN = [
    {"v31_name": 13002, "emit_name": 13002, "parent": MAIN_SECTION_V92_ID},
    {"v31_name": 13005, "emit_name": 13005, "parent": MAIN_SECTION_V92_ID},
    {"v31_name": 13008, "emit_name": 13008, "parent": MAIN_SECTION_V92_ID},
    {"v31_name": 13015, "emit_name": 13015, "parent": MAIN_SECTION_V92_ID},
    {"v31_name": 13018, "emit_name": 13018, "parent": MAIN_SECTION_V92_ID},
    {"v31_name": 13022, "emit_name": 13022, "parent": MAIN_SECTION_V92_ID},
    {"v31_name": 13013, "emit_name": 13036, "parent": MAIN_SECTION_V92_ID,
     "desc": "13036 Terron Run (restored from v31 nameId 13013; reassigned to 13036 "
             "because v92 reuses 13013 for Airship Approach)"},
]

# Tower Base cluster: root-level 64001 with nested 64007. Ids reuse the v92
# commented-out template ids (evidence: id=30 / id=40).
TOWER_ROOT_NAME = 64001
TOWER_CHILD_NAME = 64007

# 13030 (Timeless Woods) survives; only its ring reverts to the classic ring.
RING_REPLACE_NAME = 13030

# 13035 (Ruined Temple) is a v92-only section to delete.
DELETE_NAME = 13035

# Region-string work.
REGION_UPSERTS = [
    (13015, "Leander's Outpost"),   # revert v92 "Abandoned Camp"
    (13036, "Terron Run"),          # new id, verified free in v92
]

# ---------------------------------------------------------------------------
# Attribute handling.
# ---------------------------------------------------------------------------
# Canonical emission order and YAML typing. Aliases equal the XML attr names
# (area-sections.mdx). `id` is handled separately (becomes sectionId).
INT_ATTRS = {
    "nameId", "worldMapSectionId", "huntingZoneId", "campId", "floor",
    "priority", "recallReviveContinentId", "recallScrollContinentId",
    "recallReviveContinentIdA", "recallReviveContinentIdB", "recallReviveContinentIdC",
    "recallScrollContinentIdA", "recallScrollContinentIdB", "recallScrollContinentIdC",
    "optimizeOption", "recallReviveDir", "recallScrollDir",
}
DOUBLE_ATTRS = {"addMaxZ", "subtractMinZ"}
BOOL_ATTRS = {
    "duel", "trade", "vender", "desTex", "protect", "guildWar", "ride",
    "pcMoveCylinder", "restBonus", "maze", "ignoreObstacleShortTel", "fishing",
    "holdAbnormalityRemainingTime",
}
# pk is a string (safe/true/false) emitted lowercase and quoted.
STRING_ATTRS = {
    "desc", "pk", "recallRevivePos", "recallScrollPos",
    "recallRevivePosA", "recallRevivePosB", "recallRevivePosC",
    "recallScrollPosA", "recallScrollPosB", "recallScrollPosC",
    "enableItemId", "disableItemId", "sellableItemId",
}

CANONICAL_ORDER = [
    "desc", "nameId", "worldMapSectionId", "huntingZoneId", "campId", "floor",
    "priority", "addMaxZ", "subtractMinZ",
    "duel", "trade", "vender", "desTex", "protect", "guildWar", "ride",
    "pcMoveCylinder", "restBonus", "maze", "ignoreObstacleShortTel", "fishing",
    "holdAbnormalityRemainingTime", "optimizeOption",
    "pk",
    "recallReviveContinentId", "recallRevivePos",
    "recallScrollContinentId", "recallScrollPos",
    "recallReviveContinentIdA", "recallRevivePosA",
    "recallReviveContinentIdB", "recallRevivePosB",
    "recallReviveContinentIdC", "recallRevivePosC",
    "recallScrollContinentIdA", "recallScrollPosA",
    "recallScrollContinentIdB", "recallScrollPosB",
    "recallScrollContinentIdC", "recallScrollPosC",
    "recallReviveDir", "recallScrollDir",
    "enableItemId", "disableItemId", "sellableItemId",
]

# ---------------------------------------------------------------------------
# Reusable archetype (packages/area-section-standard). A restored full section
# emits "$extends: area-section-standard.ClassicSection" plus only the fields
# that deviate. The base MUST mirror the package; a field is suppressed only when
# its rendered value equals the archetype's, so the effective value is unchanged.
# A base field absent from a section is listed under $remove so the merged result
# keeps exactly the original key set. Ring-only reverts do NOT extend the base.
# ---------------------------------------------------------------------------
SECTION_PKG = "area-section-standard"
SECTION_BASE = {
    "huntingZoneId": "-1", "floor": "1", "desTex": "false", "protect": "false",
    "guildWar": "true", "ride": "true", "trade": "true", "duel": "true",
    "vender": "false", "pcMoveCylinder": "false", "campId": "0",
    "worldMapSectionId": "0", "subtractMinZ": "4096.000000", "pk": "safe",
}


def die(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Parsing helpers.
# ---------------------------------------------------------------------------
def local(tag):
    return tag.rsplit("}", 1)[-1]


def iter_sections(elem):
    """Yield every <Section> element recursively, depth-first."""
    for child in elem:
        if local(child.tag) == "Section":
            yield child
            yield from iter_sections(child)


def section_fence_tokens(section):
    """Direct-child <Fence> pos tokens of a section: list of (x, y, z) strings."""
    ring = []
    for child in section:
        if local(child.tag) == "Fence":
            x, y, z = child.get("pos").split(",")
            ring.append((x.strip(), y.strip(), z.strip()))
    return ring


def parse_area(path):
    """Return {nameId(int): {'attrs': {...}, 'fences': [(x,y,z)str], 'id': str}}."""
    tree = ET.parse(path)
    root = tree.getroot()
    out = {}
    for sec in iter_sections(root):
        name = sec.get("nameId")
        if name is None:
            continue
        out[int(name)] = {
            "attrs": dict(sec.attrib),
            "fences": section_fence_tokens(sec),
            "id": sec.get("id"),
        }
    return out


def parse_v92_live_ids(path):
    """Live section ids in the v92 file (ET drops comments, so this is live-only)."""
    tree = ET.parse(path)
    ids = set()
    for sec in iter_sections(tree.getroot()):
        ids.add(int(sec.get("id")))
    return ids


def parse_v92_commented_tower(path):
    """Extract the commented-out Tower Base template from the raw v92 file.

    Returns {nameId: {'id': str, 'fences': [(x,y,z)str]}} for 64001 / 64007.
    """
    raw = open(path, "r", encoding="utf-8").read()
    result = {}
    for block in re.findall(r"<!--(.*?)-->", raw, re.DOTALL):
        if 'nameId="64001"' not in block:
            continue
        # Locate the nested child section start to split outer vs inner fences.
        child_ids = re.findall(r'<Section id="(\d+)"[^>]*nameId="(\d+)"', block)
        id_by_name = {int(n): sid for sid, n in child_ids}
        child_match = re.search(r'<Section id="\d+"[^>]*nameId="64007"', block)
        outer_text = block[:child_match.start()] if child_match else block
        inner_text = block[child_match.start():] if child_match else ""

        def fences(txt):
            ring = []
            for pos in re.findall(r'<Fence pos="([^"]+)"', txt):
                x, y, z = pos.split(",")
                ring.append((x.strip(), y.strip(), z.strip()))
            return ring

        result[64001] = {"id": id_by_name.get(64001), "fences": fences(outer_text)}
        result[64007] = {"id": id_by_name.get(64007), "fences": fences(inner_text)}
        break
    return result


# ---------------------------------------------------------------------------
# Fence cross-check (v31 default, v17 wins on disagreement).
# ---------------------------------------------------------------------------
def rings_agree(a, b):
    """True if two token rings agree within tolerance and vertex count."""
    if len(a) != len(b):
        return False
    for (ax, ay, az), (bx, by, bz) in zip(a, b):
        if (abs(float(ax) - float(bx)) > FENCE_TOLERANCE or
                abs(float(ay) - float(by)) > FENCE_TOLERANCE or
                abs(float(az) - float(bz)) > FENCE_TOLERANCE):
            return False
    return True


def choose_ring(name, v31_ring, v17_ring, warnings):
    """Return the ring tokens to emit. v31 default; v17 wins on disagreement."""
    if v17_ring is None:
        return v31_ring
    if rings_agree(v31_ring, v17_ring):
        return v31_ring
    warnings.append(
        "nameId %s fence disagreement: v31=%d vertices, v17=%d vertices; "
        "using v17 client geometry (precedence rule)."
        % (name, len(v31_ring), len(v17_ring)))
    return v17_ring


# ---------------------------------------------------------------------------
# Id allocation.
# ---------------------------------------------------------------------------
def allocate_id(preferred, taken):
    """preferred if free, else the lowest free positive id not in `taken`."""
    if preferred is not None and preferred not in taken:
        return preferred
    n = 1
    while n in taken:
        n += 1
    return n


# ---------------------------------------------------------------------------
# YAML emission helpers.
# ---------------------------------------------------------------------------
def yaml_scalar(alias, value):
    """Render one `alias: value` pair with schema-correct typing."""
    if alias in BOOL_ATTRS:
        return "%s: %s" % (alias, value.strip().lower())
    if alias in INT_ATTRS:
        return "%s: %s" % (alias, str(int(value)))
    if alias in DOUBLE_ATTRS:
        return "%s: %s" % (alias, value)
    # string family (incl. pk): quote, escaping backslash and double-quote.
    esc = value.replace("\\", "\\\\").replace('"', '\\"')
    if alias == "pk":
        esc = esc.strip().lower()
    return '%s: "%s"' % (alias, esc)


def emit_attrs(attrs, indent, desc_override=None, name_override=None, base=None):
    """Emit canonical-ordered non-empty attribute lines from a v31 attrib dict.

    When `base` (a {alias: rendered-line} archetype map) is given, a field whose
    rendered value equals the archetype's is suppressed (inherited). Returns
    (lines, removed) where `removed` lists archetype keys absent from this section
    so the caller can emit a $remove and keep the merged key set exact. When
    `base` is None the section is emitted literally and `removed` is empty.
    """
    lines = []
    present = set()
    for alias in CANONICAL_ORDER:
        if alias == "desc" and desc_override is not None:
            lines.append(indent + yaml_scalar("desc", desc_override))
            continue
        if alias == "nameId" and name_override is not None:
            lines.append(indent + ("nameId: %d" % name_override))
            continue
        if alias not in attrs:
            continue
        val = attrs[alias]
        if val == "":          # empty string means null -> omit
            continue
        rendered = yaml_scalar(alias, val)
        present.add(alias)
        if base is not None and alias in base and rendered == base[alias]:
            continue           # inherited from the archetype
        lines.append(indent + rendered)
    removed = ([a for a in CANONICAL_ORDER if a in base and a not in present]
               if base is not None else [])
    return lines, removed


def emit_fences(ring, indent):
    lines = [indent + "fences:"]
    for x, y, z in ring:
        lines.append(indent + "  - [%s, %s, %s]" % (x, y, z))
    return lines


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    v31 = parse_area(V31_AREA)
    v17 = parse_area(V17_AREA)
    live_ids = parse_v92_live_ids(V92_AREA)
    commented = parse_v92_commented_tower(V92_AREA)
    section_base_rendered = {a: yaml_scalar(a, v) for a, v in SECTION_BASE.items()}

    warnings = []
    id_map = {}          # emit_name -> chosen section id
    taken = set(live_ids)

    # --- resolve section ids (deterministic order) ---
    # Tower Base reuses commented template ids first so their ids are reserved.
    tower_root_id = int(commented[TOWER_ROOT_NAME]["id"])
    tower_child_id = int(commented[TOWER_CHILD_NAME]["id"])
    id_map[TOWER_ROOT_NAME] = tower_root_id
    id_map[TOWER_CHILD_NAME] = tower_child_id
    taken.update({tower_root_id, tower_child_id})

    for item in RESTORE_PLAN:
        v31row = v31.get(item["v31_name"])
        if v31row is None:
            die("v31 row nameId %s not found" % item["v31_name"])
        preferred = int(v31row["id"])
        chosen = allocate_id(preferred, taken)
        taken.add(chosen)
        id_map[item["emit_name"]] = chosen

    # --- Tower Base fence cross-checks (v31 vs v17 vs v92-comment) ---
    for tname in (TOWER_ROOT_NAME, TOWER_CHILD_NAME):
        v31_ring = v31[tname]["fences"]
        v17_ring = v17[tname]["fences"]
        cmt_ring = commented[tname]["fences"]
        # v92-comment note (do not auto-resolve; report only).
        cmt_vs_v31 = "matches v31" if rings_agree(cmt_ring, v31_ring) else \
            "differs from v31 (%d vs %d verts)" % (len(cmt_ring), len(v31_ring))
        cmt_vs_v17 = "matches v17" if rings_agree(cmt_ring, v17_ring) else \
            "differs from v17 (%d vs %d verts)" % (len(cmt_ring), len(v17_ring))
        warnings.append(
            "Tower Base nameId %s v92-comment ring: %s; %s."
            % (tname, cmt_vs_v31, cmt_vs_v17))

    # --- build section payloads in emission order ---
    section_blocks = []   # each is a list of text lines (an upsert list item)

    for item in RESTORE_PLAN:
        name = item["emit_name"]
        v31row = v31[item["v31_name"]]
        v17row = v17.get(item["v31_name"])
        ring = choose_ring(name, v31row["fences"],
                           v17row["fences"] if v17row else None, warnings)
        attr_lines, removed = emit_attrs(v31row["attrs"], "      ",
                                         desc_override=item.get("desc"),
                                         name_override=name,
                                         base=section_base_rendered)
        lines = []
        lines.append("    - continentId: %d" % CONTINENT_ID)
        lines.append('      areaName: "%s"' % AREA_NAME)
        lines.append("      parentSectionId: %d" % item["parent"])
        lines.append("      sectionId: %d" % id_map[name])
        lines.append("      $extends: %s.ClassicSection" % SECTION_PKG)
        if removed:
            lines.append("      $remove: [%s]" % ", ".join(removed))
        lines.extend(attr_lines)
        lines.extend(emit_fences(ring, "      "))
        section_blocks.append(lines)

    # Tower Base root (64001) with nested 64007 child; root has NO parentSectionId.
    root_row = v31[TOWER_ROOT_NAME]
    root_ring = choose_ring(TOWER_ROOT_NAME, root_row["fences"],
                            v17[TOWER_ROOT_NAME]["fences"], warnings)
    child_row = v31[TOWER_CHILD_NAME]
    child_ring = choose_ring(TOWER_CHILD_NAME, child_row["fences"],
                             v17[TOWER_CHILD_NAME]["fences"], warnings)
    root_attr_lines, root_removed = emit_attrs(root_row["attrs"], "      ",
                                               base=section_base_rendered)
    child_attr_lines, child_removed = emit_attrs(child_row["attrs"], "          ",
                                                 base=section_base_rendered)
    tblock = []
    tblock.append("    - continentId: %d" % CONTINENT_ID)
    tblock.append('      areaName: "%s"' % AREA_NAME)
    tblock.append("      sectionId: %d" % id_map[TOWER_ROOT_NAME])
    tblock.append("      $extends: %s.ClassicSection" % SECTION_PKG)
    if root_removed:
        tblock.append("      $remove: [%s]" % ", ".join(root_removed))
    tblock.extend(root_attr_lines)
    tblock.extend(emit_fences(root_ring, "      "))
    tblock.append("      sections:")
    tblock.append("        - sectionId: %d" % id_map[TOWER_CHILD_NAME])
    tblock.append("          $extends: %s.ClassicSection" % SECTION_PKG)
    if child_removed:
        tblock.append("          $remove: [%s]" % ", ".join(child_removed))
    tblock.extend(child_attr_lines)
    tblock.extend(emit_fences(child_ring, "          "))
    section_blocks.append(tblock)

    # 13030 ring-only revert (classic ring; v31 and v17 identical).
    ring_row = v31[RING_REPLACE_NAME]
    ring_ring = choose_ring(RING_REPLACE_NAME, ring_row["fences"],
                            v17[RING_REPLACE_NAME]["fences"], warnings)
    ring_live_id = delete_id_for_note(RING_REPLACE_NAME)   # existing v92 id of 13030
    rblock = []
    rblock.append("    - continentId: %d" % CONTINENT_ID)
    rblock.append('      areaName: "%s"' % AREA_NAME)
    rblock.append("      sectionId: %d" % ring_live_id)
    rblock.append("      nameId: %d" % RING_REPLACE_NAME)
    rblock.extend(emit_fences(ring_ring, "      "))
    section_blocks.append(rblock)

    # 13035 delete (v92-only section, live id).
    delete_id = delete_id_for_note(DELETE_NAME)

    # --- write region-strings spec ---
    region_lines = []
    region_lines.append('spec:')
    region_lines.append('  version: "1.0"')
    region_lines.append('  schema: v92')
    region_lines.append('')
    region_lines.append('# IoD patch 001 region strings (Stage 1 section restoration).')
    region_lines.append('# Source of truth: docs/plans/iod-alpha-content-loop/data/section-mapping.json')
    region_lines.append('#')
    region_lines.append('# 13036 "Terron Run": NEW region id (verified free in v92 client+server).')
    region_lines.append('#   Restores the classic place name for the section whose v31 nameId was')
    region_lines.append('#   13013; that id is kept as v92 "Airship Approach" (3 live minimap labels).')
    region_lines.append('# 13015 "Leander\'s Outpost": reverts v92\'s "Abandoned Camp" back to the')
    region_lines.append('#   classic string (zero inbound refs on the current v92 meaning).')
    region_lines.append('')
    region_lines.append('regionStrings:')
    region_lines.append('  upsert:')
    for rid, text in REGION_UPSERTS:
        esc = text.replace('\\', '\\\\').replace('"', '\\"')
        region_lines.append('    - id: %d' % rid)
        region_lines.append('      string: "%s"' % esc)
    write_lines(OUT_REGION, region_lines)

    # --- write area-sections spec ---
    sec_lines = []
    sec_lines.append('spec:')
    sec_lines.append('  version: "1.0"')
    sec_lines.append('  schema: v92')
    sec_lines.append('')
    sec_lines.append('imports:')
    sec_lines.append('  - from: %s' % SECTION_PKG)
    sec_lines.append('')
    sec_lines.append('# IoD patch 001 Stage 1: area-section restoration on continent 13 / ATW_Death_P.')
    sec_lines.append('#')
    sec_lines.append('# Sources:')
    sec_lines.append('#   attrs   : v31 classic server  AreaData_13_ATW_P.xml')
    sec_lines.append('#   geometry: v31 ring by default; v17 client Area-00004.xml wins on disagreement')
    sec_lines.append('#   ids     : v92 server AreaData_13_ATW_Death_P.xml (live + commented template)')
    sec_lines.append('# Disposition table: docs/plans/iod-alpha-content-loop/data/section-mapping.json')
    sec_lines.append('#')
    sec_lines.append('# Restored under original nameId (children of main section 13001, v92 id %d):' % MAIN_SECTION_V92_ID)
    sec_lines.append('#   13002 Pegasus Platform, 13005 Northern Checkpoint, 13008 Orcan Bivouac,')
    sec_lines.append('#   13015 Leander\'s Outpost, 13018 Northern Overwatch, 13022 Tainted Gorge Garrison.')
    sec_lines.append('# Restored under NEW nameId: 13036 Terron Run (v31 row carried nameId 13013).')
    sec_lines.append('# Tower Base cluster: 64001 (root-level) with 64007 nested; reuses the v92')
    sec_lines.append('#   commented-out template ids.')
    sec_lines.append('# 13030 Timeless Woods: ring-only revert to the classic ring (decision 16).')
    sec_lines.append('# 13035 Ruined Temple: deleted (v92-only section).')
    sec_lines.append('#')
    sec_lines.append('# Chosen section-id map (nameId -> XML id):')
    for name in sorted(id_map):
        sec_lines.append('#   %d -> %d' % (name, id_map[name]))
    sec_lines.append('#   %d (13030 existing) -> %d' % (RING_REPLACE_NAME, ring_live_id))
    sec_lines.append('#   %d (13035 delete)   -> %d' % (DELETE_NAME, delete_id))
    sec_lines.append('')
    sec_lines.append('areaSections:')
    sec_lines.append('  upsert:')
    for block in section_blocks:
        sec_lines.extend(block)
    sec_lines.append('  delete:')
    sec_lines.append('    - continentId: %d' % CONTINENT_ID)
    sec_lines.append('      areaName: "%s"' % AREA_NAME)
    sec_lines.append('      sectionId: %d' % delete_id)
    write_lines(OUT_SECTIONS, sec_lines)

    # --- report ---
    print("Section-id map (nameId -> XML id):")
    for name in sorted(id_map):
        print("  %6d -> %d" % (name, id_map[name]))
    print("  %6d -> %d  (13030 existing, ring-only)" % (RING_REPLACE_NAME, ring_live_id))
    print("  %6d -> %d  (13035 delete)" % (DELETE_NAME, delete_id))
    print("")
    print("Cross-check / notes:")
    for w in warnings:
        print("  - " + w)
    print("")
    print("Operation counts:")
    print("  region-strings : %d upsert, 0 delete" % len(REGION_UPSERTS))
    print("  area-sections  : %d upsert (top-level), 1 nested child, 1 delete"
          % len(section_blocks))
    print("")
    print("Wrote:")
    print("  " + OUT_REGION)
    print("  " + OUT_SECTIONS)


_V92_NAME_TO_ID = None


def delete_id_for_note(name):
    global _V92_NAME_TO_ID
    if _V92_NAME_TO_ID is None:
        _V92_NAME_TO_ID = {}
        for s in iter_sections(ET.parse(V92_AREA).getroot()):
            _V92_NAME_TO_ID[s.get("nameId")] = int(s.get("id"))
    return _V92_NAME_TO_ID[str(name)]


def write_lines(path, lines):
    text = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


if __name__ == "__main__":
    main()
