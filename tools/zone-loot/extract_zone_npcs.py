"""
Zone NPC Extraction — Joins TerritoryData + NpcData + StrSheet_Creature.

Reads zone_tier_config.csv for the zone list, then for each zone:
  1. Parses TerritoryData_{zoneId}.xml for spawn entries (territory filter)
  2. Parses NpcData_{zoneId}.xml for template attributes (NPC enrichment)
  3. Joins StrSheet_Creature.xml for display names

Outputs a clean npc_by_zone.csv with only territory-spawned NPCs enriched
with template data.

Usage:
    python tools/zone-loot/extract_zone_npcs.py
    python tools/zone-loot/extract_zone_npcs.py --aggressive-only --named-only
"""

import argparse
import csv
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SpawnEntry:
    hunting_zone_id: int
    npc_template_id: int
    territory_id: int
    territory_type: str
    instance_id: int
    spawn_count: int
    respawn_time: int
    aggressive: bool
    void_spawn: bool
    party_id: int  # 0 = solo
    member_id: int  # 0 = solo, 1 = leader, 2+ = member


@dataclass
class NpcTemplate:
    template_id: int
    level: int
    elite: bool
    show_aggro_target: bool
    size: str
    resource_type: str


@dataclass
class NpcString:
    name: str
    title: str


# ---------------------------------------------------------------------------
# Config reader
# ---------------------------------------------------------------------------

def read_references(reforged_root: Path) -> dict[str, str]:
    """Read .references file from project root (parent of reforged/)."""
    ref_path = reforged_root.parent / ".references"
    if not ref_path.exists():
        ref_path = reforged_root / ".references"
    refs = {}
    with open(ref_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                refs[key.strip()] = value.strip()
    return refs


def read_zone_config(path: str) -> list[int]:
    """Read zone_tier_config.csv → list of huntingZoneIds with tier > 0."""
    zone_ids = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            tier = int(row["tier"])
            zone_type = row["type"]
            if tier > 0 and zone_type not in ("hub", "excluded"):
                zone_ids.append(int(row["huntingZoneId"]))
    return sorted(zone_ids)


# ---------------------------------------------------------------------------
# XML parsers
# ---------------------------------------------------------------------------

def parse_territory_data(xml_path: str, zone_id: int) -> list[SpawnEntry]:
    """Parse TerritoryData_{zoneId}.xml → list of SpawnEntry."""
    if not os.path.exists(xml_path):
        return []

    entries = []
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for tgroup in root.iter("TerritoryGroup"):
        for territory in tgroup.iter("Territory"):
            t_id = int(territory.get("id", "0"))
            t_type = territory.get("type", "normal")

            # Solo NPCs (direct children of Territory)
            for npc in territory.findall("Npc"):
                entries.append(_parse_npc_element(
                    npc, zone_id, t_id, t_type, party_id=0
                ))

            # Party NPCs
            for party in territory.iter("Party"):
                p_id = int(party.get("id", "0"))
                for npc in party.findall("Npc"):
                    entries.append(_parse_npc_element(
                        npc, zone_id, t_id, t_type, party_id=p_id
                    ))

    return entries


def _parse_npc_element(
    npc: ET.Element, zone_id: int, territory_id: int,
    territory_type: str, party_id: int
) -> SpawnEntry:
    """Parse a single <Npc> element into a SpawnEntry."""
    return SpawnEntry(
        hunting_zone_id=zone_id,
        npc_template_id=int(npc.get("npcTemplateId", "0")),
        territory_id=territory_id,
        territory_type=territory_type,
        instance_id=int(npc.get("instanceId", "0")),
        spawn_count=int(npc.get("spawnCount", "1")),
        respawn_time=int(npc.get("respawnTime", "0")),
        aggressive=npc.get("isAggressiveMonster", "false").lower() == "true",
        void_spawn=npc.get("voidSpawn", "false").lower() == "true",
        party_id=party_id,
        member_id=int(npc.get("memberId", "0")),
    )


def parse_npc_data(xml_path: str) -> dict[int, NpcTemplate]:
    """Parse NpcData_{zoneId}.xml → {templateId: NpcTemplate}."""
    if not os.path.exists(xml_path):
        return {}

    templates = {}
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for tmpl in root.iter("Template"):
        tid = int(tmpl.get("id", "0"))
        stat = tmpl.find("Stat")
        level = int(stat.get("level", "0")) if stat is not None else 0
        templates[tid] = NpcTemplate(
            template_id=tid,
            level=level,
            elite=tmpl.get("elite", "False").lower() == "true",
            show_aggro_target=tmpl.get("showAggroTarget", "False").lower() == "true",
            size=tmpl.get("size", ""),
            resource_type=tmpl.get("resourceType", ""),
        )
    return templates


def parse_creature_strings(xml_path: str) -> dict[tuple[int, int], NpcString]:
    """Parse StrSheet_Creature.xml → {(huntingZoneId, templateId): NpcString}."""
    strings = {}
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for hz in root.iter("HuntingZone"):
        zone_id = int(hz.get("id", "0"))
        for s in hz.iter("String"):
            tid = int(s.get("templateId", "0"))
            strings[(zone_id, tid)] = NpcString(
                name=s.get("name", ""),
                title=s.get("title", ""),
            )
    return strings


# ---------------------------------------------------------------------------
# Deduplication — collapse spawn entries to unique NPCs per zone
# ---------------------------------------------------------------------------

@dataclass
class NpcRow:
    hunting_zone_id: int
    npc_template_id: int
    npc_name: str
    npc_title: str
    territory_type: str
    total_spawns: int
    min_respawn: int
    max_respawn: int
    aggressive: bool
    has_name: bool
    has_party: bool
    level: int
    elite: bool
    show_aggro_target: bool
    size: str
    resource_type: str


def find_script_spawned_bosses(
    zone_id: int,
    territory_npc_ids: set[int],
    npc_templates: dict[int, NpcTemplate],
    creature_strings: dict[tuple[int, int], NpcString],
) -> list[NpcRow]:
    """Find NPCs with showAggroTarget=True that aren't in territory data.

    These are script-spawned dungeon bosses that the territory XML doesn't
    reference. They exist in NpcData but are spawned by encounter scripts.
    """
    rows = []
    for tid, tmpl in sorted(npc_templates.items()):
        if tid in territory_npc_ids:
            continue
        if not tmpl.show_aggro_target:
            continue

        npc_str = creature_strings.get((zone_id, tid), NpcString("", ""))
        rows.append(NpcRow(
            hunting_zone_id=zone_id,
            npc_template_id=tid,
            npc_name=npc_str.name,
            npc_title=npc_str.title,
            territory_type="script",
            total_spawns=1,
            min_respawn=0,
            max_respawn=0,
            aggressive=True,
            has_name=bool(npc_str.name),
            has_party=True,
            level=tmpl.level,
            elite=tmpl.elite,
            show_aggro_target=True,
            size=tmpl.size,
            resource_type=tmpl.resource_type,
        ))
    return rows


def aggregate_spawns(
    spawns: list[SpawnEntry],
    npc_templates: dict[int, NpcTemplate],
    creature_strings: dict[tuple[int, int], NpcString],
    territory_type_filter: str | None,
    exclude_void_spawn: bool,
    aggressive_only: bool,
    named_only: bool,
) -> list[NpcRow]:
    """Aggregate spawn entries into unique NPC rows per zone."""

    # Group by (zone_id, npc_template_id)
    groups: dict[tuple[int, int], list[SpawnEntry]] = {}
    for s in spawns:
        if exclude_void_spawn and s.void_spawn:
            continue
        if territory_type_filter and s.territory_type != territory_type_filter:
            continue
        key = (s.hunting_zone_id, s.npc_template_id)
        groups.setdefault(key, []).append(s)

    rows = []
    for (zone_id, npc_id), entries in sorted(groups.items()):
        # NPC string lookup
        npc_str = creature_strings.get((zone_id, npc_id), NpcString("", ""))
        has_name = bool(npc_str.name)

        # Apply filters
        any_aggressive = any(e.aggressive for e in entries)
        if aggressive_only and not any_aggressive:
            continue
        if named_only and not has_name:
            continue

        # NPC template enrichment
        tmpl = npc_templates.get(npc_id)

        # Aggregate spawn stats
        total_spawns = sum(e.spawn_count for e in entries)
        respawn_times = [e.respawn_time for e in entries if e.respawn_time > 0]
        has_party = any(e.party_id > 0 for e in entries)

        rows.append(NpcRow(
            hunting_zone_id=zone_id,
            npc_template_id=npc_id,
            npc_name=npc_str.name,
            npc_title=npc_str.title,
            territory_type="normal",
            total_spawns=total_spawns,
            min_respawn=min(respawn_times) if respawn_times else 0,
            max_respawn=max(respawn_times) if respawn_times else 0,
            aggressive=any_aggressive,
            has_name=has_name,
            has_party=has_party,
            level=tmpl.level if tmpl else 0,
            elite=tmpl.elite if tmpl else False,
            show_aggro_target=tmpl.show_aggro_target if tmpl else False,
            size=tmpl.size if tmpl else "",
            resource_type=tmpl.resource_type if tmpl else "",
        ))

    return rows


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

CSV_COLUMNS = [
    "huntingZoneId", "npcTemplateId", "npcName", "npcTitle",
    "territoryType", "totalSpawns", "minRespawn", "maxRespawn",
    "aggressive", "hasName", "hasParty",
    "level", "elite", "showAggroTarget", "size", "resourceType",
]


def write_csv(rows: list[NpcRow], output_path: str):
    """Write NPC rows to CSV."""
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(CSV_COLUMNS)
        for r in rows:
            writer.writerow([
                r.hunting_zone_id, r.npc_template_id,
                r.npc_name, r.npc_title,
                r.territory_type, r.total_spawns,
                r.min_respawn, r.max_respawn,
                r.aggressive, r.has_name, r.has_party,
                r.level, r.elite, r.show_aggro_target,
                r.size, r.resource_type,
            ])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract zone NPCs from TerritoryData + NpcData + StrSheet_Creature"
    )
    parser.add_argument(
        "--territory-type", default="normal",
        help="Filter to this territory type (default: normal). Use 'all' for no filter."
    )
    parser.add_argument(
        "--include-void-spawn", action="store_true",
        help="Include voidSpawn NPCs (default: excluded)"
    )
    parser.add_argument(
        "--aggressive-only", action="store_true",
        help="Only include aggressive NPCs"
    )
    parser.add_argument(
        "--named-only", action="store_true",
        help="Only include NPCs with display names"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output CSV path (default: data/zone_loot/npc_by_zone.csv)"
    )
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    reforged_root = script_dir.parent.parent
    refs = read_references(reforged_root)
    datasheet_path = Path(refs["server_datasheet"])
    data_dir = reforged_root / "data" / "zone_loot"

    zone_config_path = str(data_dir / "zone_tier_config.csv")
    creature_str_path = str(datasheet_path / "StrSheet_Creature.xml")
    output_path = args.output or str(data_dir / "npc_by_zone.csv")

    territory_type_filter = None if args.territory_type == "all" else args.territory_type

    # Read zone list
    zone_ids = read_zone_config(zone_config_path)
    print(f"Processing {len(zone_ids)} zones...")

    # Parse creature strings (single file, all zones)
    print("Parsing StrSheet_Creature.xml...")
    creature_strings = parse_creature_strings(creature_str_path)

    # Process each zone
    all_rows = []
    for zone_id in zone_ids:
        territory_file = str(datasheet_path / f"TerritoryData_{zone_id}.xml")
        npc_file = str(datasheet_path / f"NpcData_{zone_id}.xml")

        spawns = parse_territory_data(territory_file, zone_id)
        npc_templates = parse_npc_data(npc_file)

        rows = aggregate_spawns(
            spawns, npc_templates, creature_strings,
            territory_type_filter=territory_type_filter,
            exclude_void_spawn=not args.include_void_spawn,
            aggressive_only=args.aggressive_only,
            named_only=args.named_only,
        )

        # Find script-spawned bosses missing from territory data
        territory_npc_ids = {r.npc_template_id for r in rows}
        script_bosses = find_script_spawned_bosses(
            zone_id, territory_npc_ids, npc_templates, creature_strings,
        )
        rows.extend(script_bosses)

        all_rows.extend(rows)

        if rows:
            agg_count = sum(1 for r in rows if r.aggressive)
            script_count = len(script_bosses)
            extra = f", {script_count} script-spawned" if script_count else ""
            print(f"  Zone {zone_id:5d}: {len(rows):4d} NPCs ({agg_count} aggressive{extra})")
        else:
            print(f"  Zone {zone_id:5d}: no territory data")

    # Write output
    write_csv(all_rows, output_path)

    # Summary
    total_aggressive = sum(1 for r in all_rows if r.aggressive)
    total_named = sum(1 for r in all_rows if r.has_name)
    total_combat = sum(1 for r in all_rows if r.aggressive and r.has_name)
    print(f"\nExtraction complete:")
    print(f"  Total unique NPCs: {len(all_rows)}")
    print(f"  Aggressive: {total_aggressive}")
    print(f"  Named: {total_named}")
    print(f"  Aggressive + Named (combat): {total_combat}")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    main()
