#!/usr/bin/env python3
"""Convert gear_progression.csv to equipment evolution YAML script."""

import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

INPUT_FILE = REFORGED_DIR / "data" / "gear_progression.csv"
OUTPUT_FILE = REFORGED_DIR / "specs" / "evolutions.yaml"

# Enchant step pattern: targetEnchantStep -> resultEnchantStep
ENCHANT_PATTERN = [
    (9, 0),
    (10, 3),
    (11, 6),
    (12, 9),
]


def parse_materials(row: dict) -> list[dict]:
    """Extract materials from row, ignoring empty entries."""
    materials = []
    for i in range(1, 6):
        material_id = row.get(f"Material_{i}", "").strip()
        amount = row.get(f"Amount_{i}", "").strip()

        if not material_id or not amount:
            continue

        try:
            materials.append({
                "id": int(material_id),
                "amount": int(amount),
            })
        except ValueError:
            continue

    return materials


def write_materials(f, materials: list[dict], indent: str):
    """Write materials list to file."""
    f.write(f"{indent}materials:\n")
    for mat in materials:
        f.write(f"{indent}  - id: {mat['id']}\n")
        f.write(f"{indent}    amount: {mat['amount']}\n")
        f.write(f"{indent}    type: item\n")


def write_condition(f, target_step: int, result_step: int, result_id: int, materials: list[dict]):
    """Write a single condition block using $extends."""
    f.write("        - $extends: baseCondition\n")
    f.write(f"          targetEnchantStep: {target_step}\n")
    f.write("          result:\n")
    f.write(f"            resultTemplateId: {result_id}\n")
    f.write(f"            resultEnchantStep: {result_step}\n")
    write_materials(f, materials, "          ")


def main():
    evolutions = []

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            template_id = row.get("TemplateId", "").strip()
            upgrade_to = row.get("UpgradeTo", "").strip()
            item_string = row.get("ItemString", "").strip()

            if not template_id or not upgrade_to:
                continue

            try:
                target_id = int(template_id)
                result_id = int(upgrade_to)
            except ValueError:
                continue

            materials = parse_materials(row)
            if not materials:
                continue

            evolutions.append({
                "targetTemplateId": target_id,
                "resultTemplateId": result_id,
                "itemString": item_string,
                "materials": materials
            })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("spec:\n")
        f.write("  version: \"1.0\"\n")
        f.write("  schema: v92\n")
        f.write("\n")
        f.write("definitions:\n")
        f.write("  baseCondition:\n")
        f.write("    awaken: false\n")
        f.write("    masterpiece: false\n")
        f.write("    params:\n")
        f.write("      evolutionProb: 1.0\n")
        f.write("      requiredMoney: 10000\n")
        f.write("\n")
        f.write("evolutions:\n")
        f.write("  upsert:\n")

        for evo in evolutions:
            f.write(f"    # {evo['targetTemplateId']} - {evo['itemString']}\n")
            f.write(f"    - targetTemplateId: {evo['targetTemplateId']}\n")
            f.write("      conditions:\n")

            for target_step, result_step in ENCHANT_PATTERN:
                write_condition(
                    f,
                    target_step,
                    result_step,
                    evo["resultTemplateId"],
                    evo["materials"]
                )

    total_conditions = len(evolutions) * len(ENCHANT_PATTERN)
    print(f"Generated {OUTPUT_FILE}")
    print(f"  {len(evolutions)} evolution entries")
    print(f"  {total_conditions} total conditions")


if __name__ == "__main__":
    main()
