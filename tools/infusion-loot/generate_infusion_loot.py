#!/usr/bin/env python3
"""
Generate YAML specs for infusion fodder loot distribution.

Reads:
- loot_tier_rates.csv: Drop rates per content tier
- zone_loot_config.csv: Zone assignments to tiers
- gear_infusion_passivity.csv: Item definitions (for IDs and names)

Generates:
- infusion-loot.yaml: CCompensation spec with definitions and zone entries

Usage:
    python generate_infusion_loot.py

Output:
    reforged/specs/infusion-loot.yaml
"""

import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

# Input files
RATES_FILE = REFORGED_DIR / "data" / "infusion_loot" / "loot_tier_rates.csv"
ZONES_FILE = REFORGED_DIR / "data" / "infusion_loot" / "zone_loot_config.csv"
ITEMS_FILE = REFORGED_DIR / "data" / "gear_infusion_passivity.csv"

# Output file
OUTPUT_FILE = REFORGED_DIR / "specs" / "infusion-loot.yaml"

# Item ID base (from gear infusion generator)
ITEM_ID_SEED = 990000

# Slot configurations
SLOTS = {
    "EQUIP_WEAPON": {
        "name": "Weapon",
        "order_start": 1,
        "order_end": 15,  # Orders 1-15 (15 passives)
    },
    "EQUIP_ARMOR_BODY": {
        "name": "Chest",
        "order_start": 16,
        "order_end": 33,  # Orders 16-33 (18 passives)
    },
    "EQUIP_ARMOR_ARM": {
        "name": "Gloves",
        "order_start": 34,
        "order_end": 43,  # Orders 34-43 (10 passives)
    },
    "EQUIP_ARMOR_LEG": {
        "name": "Boots",
        "order_start": 44,
        "order_end": 50,  # Orders 44-50 (7 passives)
    },
}

# Grade configurations
GRADES = [
    {"id": 0, "name": "Uncommon", "tier_field": "Uncommon"},
    {"id": 1, "name": "Rare", "tier_field": "Rare"},
    {"id": 2, "name": "Superior", "tier_field": "Superior"},
]


@dataclass
class TierRates:
    """Drop rates for a content tier."""
    name: str
    uncommon: float
    rare: float
    superior: float


@dataclass
class ZoneConfig:
    """Zone assignment to a content tier."""
    tier: str
    hunting_zone_id: int
    npc_template_ids: list[int]


@dataclass
class InfusionItem:
    """Infusion item definition."""
    order: int
    combat_item_type: str
    suffix: str
    slot_name: str


def parse_tier_rates() -> dict[str, TierRates]:
    """Parse loot tier rates CSV."""
    rates = {}

    with open(RATES_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            tier = row.get("Tier", "").strip()
            if not tier or tier.startswith("#"):
                continue

            rates[tier] = TierRates(
                name=tier,
                uncommon=float(row.get("Uncommon", "0").strip()),
                rare=float(row.get("Rare", "0").strip()),
                superior=float(row.get("Superior", "0").strip()),
            )

    return rates


def parse_zone_configs() -> list[ZoneConfig]:
    """Parse zone loot configuration CSV."""
    configs = []

    with open(ZONES_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            tier = row.get("Tier", "").strip()
            if not tier or tier.startswith("#"):
                continue

            zone_id_str = row.get("HuntingZoneId", "").strip()
            if not zone_id_str:
                continue

            npc_ids_str = row.get("NpcTemplateIds", "").strip()
            if not npc_ids_str:
                continue

            npc_ids = [int(x.strip()) for x in npc_ids_str.split(",") if x.strip()]

            configs.append(ZoneConfig(
                tier=tier,
                hunting_zone_id=int(zone_id_str),
                npc_template_ids=npc_ids,
            ))

    return configs


def parse_infusion_items() -> list[InfusionItem]:
    """Parse infusion items from gear_infusion_passivity.csv."""
    items = []

    with open(ITEMS_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            order_str = row.get("Order", "").strip()
            if not order_str or order_str.startswith("#"):
                continue

            try:
                order = int(order_str)
            except ValueError:
                continue

            combat_item_type = row.get("CombatItemType", "").strip()
            suffix = row.get("Suffix", "").strip()

            # Get slot name
            slot_config = SLOTS.get(combat_item_type, {})
            slot_name = slot_config.get("name", "Unknown")

            items.append(InfusionItem(
                order=order,
                combat_item_type=combat_item_type,
                suffix=suffix,
                slot_name=slot_name,
            ))

    return items


def get_item_id(order: int, grade_id: int) -> int:
    """Calculate item ID from order and grade."""
    # Each order generates 3 items (uncommon, rare, superior)
    # Item ID = base + (order - 1) * 3 + grade_id
    return ITEM_ID_SEED + (order - 1) * 3 + grade_id


def get_item_name(slot_name: str, suffix: str) -> str:
    """Generate item display name."""
    return f"Infusion {slot_name} {suffix}"


def get_items_by_slot_and_grade(items: list[InfusionItem]) -> dict:
    """Group items by slot and grade."""
    result = {}

    for slot_type, slot_config in SLOTS.items():
        slot_name = slot_config["name"]
        result[slot_name] = {grade["name"]: [] for grade in GRADES}

        # Get items for this slot
        slot_items = [i for i in items if i.combat_item_type == slot_type]

        for item in slot_items:
            for grade in GRADES:
                item_id = get_item_id(item.order, grade["id"])
                item_name = get_item_name(item.slot_name, item.suffix)

                result[slot_name][grade["name"]].append({
                    "id": item_id,
                    "name": item_name,
                })

    return result


def generate_yaml(
    tier_rates: dict[str, TierRates],
    zone_configs: list[ZoneConfig],
    items_by_slot_grade: dict,
) -> str:
    """Generate the YAML spec."""
    lines = [
        "# Infusion Fodder Loot Distribution",
        "# Auto-generated by generate_infusion_loot.py",
        "# DO NOT EDIT MANUALLY",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "definitions:",
    ]

    # Generate definitions for each tier
    for tier_name, rates in tier_rates.items():
        lines.append(f"  # {tier_name} content tier")
        lines.append(f"  loot_{tier_name}:")
        lines.append("    itemBags:")

        # For each grade
        for grade in GRADES:
            grade_name = grade["name"]
            rate_field = grade["tier_field"].lower()
            base_rate = getattr(rates, rate_field)

            if base_rate <= 0:
                continue

            # Rate per slot = base_rate / 4 slots
            slot_rate = base_rate / 4

            # For each slot
            for slot_name, slot_items in items_by_slot_grade.items():
                grade_items = slot_items[grade_name]

                if not grade_items:
                    continue

                item_count = len(grade_items)

                lines.append(f"      # {grade_name} {slot_name} ({item_count} items)")
                lines.append(f"      - probability: {slot_rate}")
                lines.append("        distribution: auto")
                lines.append("        items:")

                for item in grade_items:
                    lines.append(f"          - templateId: {item['id']}")
                    lines.append(f'            name: "{item["name"]}"')

        lines.append("")

    # Generate cCompensations
    lines.append("cCompensations:")
    lines.append("  upsert:")

    # Group zones by hunting zone ID for cleaner output
    for config in zone_configs:
        npc_ids_str = ", ".join(str(x) for x in config.npc_template_ids)

        lines.append(f"    # Zone {config.hunting_zone_id} - {config.tier}")
        lines.append(f"    - huntingZoneId: {config.hunting_zone_id}")
        lines.append(f"      npcTemplateId: [{npc_ids_str}]")
        lines.append('      npcName: ""')
        lines.append(f"      $extends: loot_{config.tier}")
        lines.append("")

    return "\n".join(lines)


def main():
    print(f"Reading tier rates from {RATES_FILE}")
    tier_rates = parse_tier_rates()
    print(f"  Found {len(tier_rates)} tiers: {', '.join(tier_rates.keys())}")

    print(f"Reading zone configs from {ZONES_FILE}")
    zone_configs = parse_zone_configs()
    print(f"  Found {len(zone_configs)} zone configurations")

    print(f"Reading infusion items from {ITEMS_FILE}")
    items = parse_infusion_items()
    print(f"  Found {len(items)} infusion items")

    print("Grouping items by slot and grade...")
    items_by_slot_grade = get_items_by_slot_and_grade(items)

    for slot_name, grades in items_by_slot_grade.items():
        counts = [f"{g}: {len(grades[g])}" for g in ["Uncommon", "Rare", "Superior"]]
        print(f"  {slot_name}: {', '.join(counts)}")

    print("Generating YAML...")
    yaml_content = generate_yaml(tier_rates, zone_configs, items_by_slot_grade)

    print(f"Writing {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    # Summary
    total_bags = sum(
        1 for rates in tier_rates.values()
        for grade in GRADES
        if getattr(rates, grade["tier_field"].lower()) > 0
    ) * 4  # 4 slots

    print(f"\nGenerated:")
    print(f"  - {len(tier_rates)} tier definitions")
    print(f"  - {total_bags} item bags total")
    print(f"  - {len(zone_configs)} zone entries")
    print(f"\nTo apply:")
    print(f'  dsl apply "{OUTPUT_FILE}" --path "D:\\dev\\mmogate\\tera92\\server\\Datasheet"')


if __name__ == "__main__":
    main()
