#!/usr/bin/env python3
"""
Generate ID Lists for Equipment Item IDs Package

Reads gear_progression.csv and generates YAML variable definitions for
item ID lists, organized by tier/slot with set grouping and annotations.

Only includes items at level 60 or below (filters out level 65/69 endgame gear).

Usage:
    python generate_id_lists.py          # Print to stdout
    python generate_id_lists.py --write  # Write to equipment-item-ids package

Output:
    YAML content for equipment-item-ids/index.yml variables section
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent
CSV_PATH = REFORGED_DIR / "data" / "gear_progression.csv"
PACKAGE_PATH = REFORGED_DIR / "packages" / "equipment-item-ids" / "index.yml"

# Slot classification
HEALER_WEAPONS = ["staff", "rod"]
DPS_TANK_WEAPONS = ["dual", "lance", "twohand", "axe", "circle", "bow", "blaster", "shuriken", "glaive", "gauntlet", "chain"]
BODY_ARMOR = ["bodyMail", "bodyLeather", "bodyRobe"]
HAND_MAIL = ["handMail"]
HAND_LEATHER = ["handLeather"]
HAND_ROBE = ["handRobe"]
FEET_ARMOR = ["feetMail", "feetLeather", "feetRobe"]


def load_csv() -> list[dict]:
    """Load and parse the gear progression CSV."""
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        return list(reader)


def build_id_lists(rows: list[dict], max_level: int = 60) -> dict:
    """
    Build ID lists organized by:
    - Grade (Mythic/Superior)
    - Slot category
    - Gear set (sorted by PowerTier desc)

    Args:
        rows: CSV rows from gear_progression.csv
        max_level: Maximum item level to include (default: 60)
    """
    organized = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for row in rows:
        # Filter by level
        level = int(row.get("Level", "0") or "0")
        if level > max_level:
            continue

        grade = row.get("RareGrade", "")
        if grade not in ["1", "2", "3", "4"]:
            continue

        if grade == "4":
            grade_name = "HIGH"
        elif grade == "3":
            grade_name = "MID"
        else:  # grade 1 or 2
            grade_name = "LOW"

        category = row.get("ItemName", "")  # Category column
        item_name = row.get("ItemString", "")  # Actual item name
        combat_type = row.get("CombatItemType", "")

        # Classify the item
        if combat_type == "EQUIP_WEAPON":
            if category in HEALER_WEAPONS:
                slot = "HEALER_WEAPON"
            elif category in DPS_TANK_WEAPONS:
                slot = "DPS_WEAPON"
            else:
                continue
        elif combat_type == "EQUIP_ARMOR_BODY":
            slot = "BODY"
        elif combat_type == "EQUIP_ARMOR_ARM":
            if category in HAND_MAIL:
                slot = "HAND_MAIL"
            elif category in HAND_LEATHER:
                slot = "HAND_LEATHER"
            elif category in HAND_ROBE:
                slot = "HAND_ROBE"
            else:
                continue
        elif combat_type == "EQUIP_ARMOR_LEG":
            slot = "FEET"
        else:
            continue

        gear_set = row.get("Gear", "Unknown")
        power_tier = int(row.get("PowerTier", "0") or "0")
        template_id = int(row.get("TemplateId", "0"))

        organized[grade_name][slot][(gear_set, power_tier)].append({
            "id": template_id,
            "category": category,
            "name": item_name,
        })

    return organized


def generate_yaml(organized: dict) -> str:
    """Generate YAML file content with variable definitions."""
    lines = []
    lines.append("# Equipment Item ID Lists")
    lines.append("# Generated from gear_progression.csv")
    lines.append("#")
    lines.append("# Organized by tier/slot with set grouping for content designer readability.")
    lines.append("# Each ID is annotated with category and item name.")
    lines.append("")
    lines.append("variables:")

    slot_order = ["HEALER_WEAPON", "DPS_WEAPON", "BODY", "HAND_MAIL", "HAND_LEATHER", "HAND_ROBE", "FEET"]
    grade_order = ["HIGH", "MID", "LOW"]

    for grade in grade_order:
        if grade == "HIGH":
            grade_label = "High Tier (Mythic)"
        elif grade == "MID":
            grade_label = "Mid Tier (Superior)"
        else:
            grade_label = "Low Tier (Uncommon/Rare)"

        for slot in slot_order:
            if slot not in organized.get(grade, {}):
                continue

            slot_data = organized[grade][slot]
            var_name = f"{grade}_TIER_{slot}_IDS"

            sorted_sets = sorted(slot_data.items(), key=lambda x: -x[0][1])
            total_items = sum(len(items) for items in slot_data.values())

            lines.append("")
            lines.append(f"  # {grade_label} - {slot.replace('_', ' ').title()} ({total_items} items)")
            lines.append(f"  {var_name}:")

            for (gear_set, power_tier), items in sorted_sets:
                items_sorted = sorted(items, key=lambda x: x["id"])

                lines.append(f"    # --- {gear_set} (PowerTier {power_tier}) ---")
                for item in items_sorted:
                    lines.append(f"    - {item['id']}  # {item['category']} - {item['name']}")

    lines.append("")

    # Generate exports section
    lines.append("exports:")
    lines.append("  variables:")

    for grade in grade_order:
        for slot in slot_order:
            if slot in organized.get(grade, {}):
                var_name = f"{grade}_TIER_{slot}_IDS"
                lines.append(f"    - {var_name}")

    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate item ID lists from gear_progression.csv")
    parser.add_argument("--write", action="store_true", help="Write to equipment-item-standard package")
    args = parser.parse_args()

    print("Loading gear_progression.csv...")
    rows = load_csv()
    print(f"Loaded {len(rows)} rows")

    print("Building ID lists...")
    organized = build_id_lists(rows)

    total = 0
    for grade in organized:
        for slot in organized[grade]:
            count = sum(len(items) for items in organized[grade][slot].values())
            print(f"  {grade}_TIER_{slot}_IDS: {count} items")
            total += count

    print(f"Total: {total} items")

    print("\nGenerating YAML...")
    yaml_content = generate_yaml(organized)

    if args.write:
        PACKAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PACKAGE_PATH, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        print(f"\nWritten to: {PACKAGE_PATH}")
    else:
        print("\n" + "=" * 60)
        print("YAML OUTPUT (use --write to save to package):")
        print("=" * 60 + "\n")
        print(yaml_content)


if __name__ == "__main__":
    main()
