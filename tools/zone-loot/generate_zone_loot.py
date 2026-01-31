#!/usr/bin/env python3
"""
Generate per-zone loot scaffold YAML specs for content designers.

Reads:
- filtered_zones.csv: Zones selected for loot rework
- npc_by_zone.csv: NPC data per zone (templateId, elite, showAggroTarget, etc.)

Generates:
- One YAML spec per zone with cCompensations + eCompensations
- Definitions per NPC group (normal, elite, boss) using $extends

Usage:
    python generate_zone_loot.py --patch 001
"""

import argparse
import csv
import re
from pathlib import Path
from dataclasses import dataclass, field

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

# Input files
ZONES_FILE = REFORGED_DIR / "data" / "zone_loot" / "filtered_zones.csv"
NPC_FILE = REFORGED_DIR / "data" / "zone_loot" / "npc_by_zone.csv"

# Output directory
OUTPUT_DIR = REFORGED_DIR / "specs" / "loot"

# All available player classes
CLASSES = [
    "warrior", "lancer", "slayer", "berserker", "sorcerer", "archer",
    "priest", "mystic", "reaper", "gunner", "brawler", "ninja", "valkyrie",
]


@dataclass
class Npc:
    template_id: int
    name: str
    title: str
    level: int
    elite: bool
    show_aggro_target: bool
    size: str
    resource_type: str


@dataclass
class Zone:
    hunting_zone_id: int
    name: str
    npcs: list[Npc] = field(default_factory=list)


def parse_filtered_zones() -> dict[int, str]:
    """Parse filtered zones CSV. Returns {huntingZoneId: zoneName}."""
    zones = {}
    with open(ZONES_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            zid = row.get("huntingZoneId", "").strip()
            zname = row.get("zoneName", "").strip()
            if zid:
                zones[int(zid)] = zname
    return zones


def parse_npcs(filtered_zone_ids: set[int]) -> dict[int, list[Npc]]:
    """Parse NPC CSV, returning only NPCs in filtered zones."""
    npcs_by_zone: dict[int, list[Npc]] = {}

    with open(NPC_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            zid_str = row.get("huntingZoneId", "").strip()
            if not zid_str:
                continue
            zid = int(zid_str)
            if zid not in filtered_zone_ids:
                continue

            elite_raw = row.get("elite", "").strip().lower()
            aggro_raw = row.get("showAggroTarget", "").strip().lower()
            level_raw = row.get("level", "0").strip()

            npc = Npc(
                template_id=int(row.get("templateId", "0").strip()),
                name=row.get("npcName", "").strip(),
                title=row.get("title", "").strip(),
                level=int(level_raw) if level_raw else 0,
                elite=elite_raw == "true",
                show_aggro_target=aggro_raw == "true",
                size=row.get("size", "").strip(),
                resource_type=row.get("resourceType", "").strip(),
            )

            npcs_by_zone.setdefault(zid, []).append(npc)

    return npcs_by_zone


def classify_npc(npc: Npc) -> str:
    """Classify NPC into a loot group: boss, elite, or normal."""
    if npc.show_aggro_target:
        return "boss"
    if npc.elite:
        return "elite"
    return "normal"


def slugify(name: str) -> str:
    """Convert zone name to a safe slug for definition names."""
    slug = name.lower().replace(" ", "_").replace("'", "")
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug


def format_npc_id_list(ids: list[int]) -> str:
    """Format a list of NPC IDs as a YAML inline array."""
    return "[" + ", ".join(str(i) for i in sorted(ids)) + "]"


def build_npc_comment(npcs: list[Npc]) -> str:
    """Build a comment string listing NPC names and levels."""
    entries = []
    for npc in sorted(npcs, key=lambda n: n.template_id):
        label = npc.name
        if npc.title:
            label += f" ({npc.title})"
        entries.append(f"{npc.template_id}={label} Lv{npc.level}")
    return ", ".join(entries)


def _level_range_str(npcs: list[Npc]) -> str:
    """Format level range string for a group of NPCs."""
    level_min = min(n.level for n in npcs)
    level_max = max(n.level for n in npcs)
    return f"Lv{level_min}-{level_max}" if level_min != level_max else f"Lv{level_min}"


def _yaml_header(zone: Zone, entity_label: str) -> list[str]:
    """Generate common YAML header lines."""
    return [
        f"# Zone Loot ({entity_label}) — {zone.name} (huntingZoneId: {zone.hunting_zone_id})",
        "# Auto-generated scaffold by generate_zone_loot.py",
        "# Content designers: fill in itemBags items for each group definition.",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
    ]


def generate_c_compensation_yaml(zone: Zone, groups: dict[str, list[Npc]]) -> str:
    """Generate cCompensation spec (normal + elite groups)."""
    slug = slugify(zone.name)
    c_groups = [g for g in ["normal", "elite"] if g in groups and groups[g]]

    lines = _yaml_header(zone, "cCompensation")

    # Definitions — cCompensation uses classBranches for per-class loot
    class_list = ", ".join(CLASSES)
    lines.append("definitions:")
    for group_name in c_groups:
        def_name = f"{slug}_{group_name}"
        group_npcs = groups[group_name]
        level_range = _level_range_str(group_npcs)

        lines.append(f"  # {group_name.capitalize()} mobs — {len(group_npcs)} NPCs, {level_range}")
        lines.append(f"  {def_name}:")
        lines.append("    classBranches:")
        lines.append(f"      - className: [{class_list}]")
        lines.append("        itemBags:")
        lines.append("          - probability: 1.0")
        lines.append("            distribution: auto")
        lines.append("            items:")
        lines.append("              - templateId: 21351")
        lines.append('                name: "Alkahest"')
        lines.append("                min: 1")
        lines.append("                max: 1")
        lines.append("                # <-- Designer: add more items here")
        lines.append("")

    # cCompensations entries
    lines.append("cCompensations:")
    lines.append("  upsert:")
    for group_name in c_groups:
        group_npcs = groups[group_name]
        def_name = f"{slug}_{group_name}"
        ids = [n.template_id for n in group_npcs]
        comment = build_npc_comment(group_npcs)

        lines.append(f"    # {group_name.capitalize()} ({len(group_npcs)} NPCs): {comment}")
        lines.append(f"    - huntingZoneId: {zone.hunting_zone_id}")
        lines.append(f"      npcTemplateId: {format_npc_id_list(ids)}")
        lines.append('      npcName: ""')
        lines.append(f"      $extends: {def_name}")
        lines.append("")

    return "\n".join(lines)


def generate_e_compensation_yaml(zone: Zone, boss_npcs: list[Npc]) -> str:
    """Generate eCompensation spec (boss group)."""
    slug = slugify(zone.name)
    lines = _yaml_header(zone, "eCompensation")

    # Definition — eCompensation ItemBag schema (id + bagName required)
    def_name = f"{slug}_boss"
    level_range = _level_range_str(boss_npcs)

    lines.append("definitions:")
    lines.append(f"  # Boss mobs — {len(boss_npcs)} NPCs, {level_range}")
    lines.append(f"  {def_name}:")
    lines.append("    itemBags:")
    lines.append("      - id: 1")
    lines.append(f'        bagName: "{zone.name} Boss Loot"')
    lines.append("        probability: 1.0")
    lines.append("        distribution: auto")
    lines.append("        items:")
    lines.append("          - templateId: 21351")
    lines.append('            name: "Alkahest"')
    lines.append("            min: 1")
    lines.append("            max: 1")
    lines.append("            # <-- Designer: add more items here")
    lines.append("")

    # eCompensations entries
    ids = [n.template_id for n in boss_npcs]
    comment = build_npc_comment(boss_npcs)

    lines.append("eCompensations:")
    lines.append("  upsert:")
    lines.append(f"    # Boss ({len(boss_npcs)} NPCs): {comment}")
    lines.append(f"    - huntingZoneId: {zone.hunting_zone_id}")
    lines.append(f"      npcTemplateId: {format_npc_id_list(ids)}")
    lines.append('      npcName: ""')
    lines.append(f"      $extends: {def_name}")
    lines.append("")

    return "\n".join(lines)


def zone_filename(zone: Zone, suffix: str = "") -> str:
    """Generate filename for a zone spec."""
    slug = slugify(zone.name)
    if suffix:
        return f"zone-{zone.hunting_zone_id:04d}-{slug}-{suffix}.yaml"
    return f"zone-{zone.hunting_zone_id:04d}-{slug}.yaml"


def main():
    parser = argparse.ArgumentParser(description="Generate per-zone loot scaffold YAML specs")
    parser.add_argument("--patch", required=True, help="Patch folder name (e.g. 001). Output goes to reforged/specs/patches/{patch}/loot/")
    args = parser.parse_args()

    output_dir = REFORGED_DIR / "specs" / "patches" / args.patch / "loot"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading filtered zones from {ZONES_FILE}")
    filtered_zones = parse_filtered_zones()
    print(f"  Found {len(filtered_zones)} zones")

    print(f"Reading NPC data from {NPC_FILE}")
    npcs_by_zone = parse_npcs(set(filtered_zones.keys()))
    total_npcs = sum(len(v) for v in npcs_by_zone.values())
    print(f"  Found {total_npcs} NPCs across {len(npcs_by_zone)} zones")

    c_output_dir = output_dir / "c-compensation"
    e_output_dir = output_dir / "e-compensation"
    c_output_dir.mkdir(parents=True, exist_ok=True)
    e_output_dir.mkdir(parents=True, exist_ok=True)

    total_normal = 0
    total_elite = 0
    total_boss = 0
    c_files = 0
    e_files = 0
    skipped_zones = []

    for zid, zname in sorted(filtered_zones.items()):
        npcs = npcs_by_zone.get(zid, [])
        if not npcs:
            skipped_zones.append((zid, zname))
            continue

        zone = Zone(hunting_zone_id=zid, name=zname, npcs=npcs)

        # Group NPCs
        groups: dict[str, list[Npc]] = {}
        for npc in npcs:
            group = classify_npc(npc)
            groups.setdefault(group, []).append(npc)

        total_normal += len(groups.get("normal", []))
        total_elite += len(groups.get("elite", []))
        total_boss += len(groups.get("boss", []))

        parts = []

        # cCompensation file (normal + elite)
        c_groups = [g for g in ["normal", "elite"] if g in groups and groups[g]]
        if c_groups:
            yaml_content = generate_c_compensation_yaml(zone, groups)
            filename = zone_filename(zone)
            filepath = c_output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(yaml_content)
            c_files += 1
            parts.append(", ".join(f"{g}: {len(groups[g])}" for g in c_groups))

        # eCompensation file (boss)
        if "boss" in groups and groups["boss"]:
            yaml_content = generate_e_compensation_yaml(zone, groups["boss"])
            filename = zone_filename(zone)
            filepath = e_output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(yaml_content)
            e_files += 1
            parts.append(f"boss: {len(groups['boss'])}")

        print(f"  zone-{zid:04d} {zname} — {', '.join(parts)}")

    print(f"\nGenerated specs in {output_dir}")
    print(f"  c-compensation/: {c_files} files (normal: {total_normal}, elite: {total_elite} NPCs)")
    print(f"  e-compensation/: {e_files} files (boss: {total_boss} NPCs)")
    print(f"  Total NPCs: {total_normal + total_elite + total_boss}")

    if skipped_zones:
        print(f"\nSkipped {len(skipped_zones)} zones (no NPC data):")
        for zid, zname in skipped_zones:
            print(f"  Zone {zid} — {zname}")


if __name__ == "__main__":
    main()
