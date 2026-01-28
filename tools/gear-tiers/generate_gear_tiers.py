#!/usr/bin/env python3
"""Convert gear_progression.csv to gear-tiers.yaml"""

import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

INPUT_FILE = REFORGED_DIR / "data" / "gear_progression.csv"
OUTPUT_FILE = REFORGED_DIR / "config" / "gear-tiers.yaml"


def main():
    items = []

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            template_id = row.get("TemplateId", "").strip()
            item_string = row.get("ItemString", "").strip()
            power_tier = row.get("PowerTier", "").strip()

            if not template_id or not power_tier:
                continue

            try:
                tier_value = int(power_tier)
            except ValueError:
                continue

            if tier_value == 0:
                continue

            items.append((int(template_id), item_string, tier_value))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("tiers:\n")
        for template_id, item_string, tier_value in items:
            f.write(f"  # {item_string}\n")
            f.write(f"  {template_id}: {tier_value}\n")

    print(f"Generated {OUTPUT_FILE} with {len(items)} items")


if __name__ == "__main__":
    main()
