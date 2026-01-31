#!/usr/bin/env python3
"""Convert gear_progression.csv to equipment evolution YAML script.

Groups entries by material configuration and emits nested $loop directives
with object arrays for compact, readable specs.
"""

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

INPUT_FILE = REFORGED_DIR / "data" / "gear_progression.csv"

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
                "name": row.get(f"MaterialName_{i}", "").strip(),
            })
        except ValueError:
            continue

    return materials


def material_key(materials: list[dict]) -> tuple:
    """Create a hashable key from a materials list for grouping."""
    return tuple((m["id"], m["amount"]) for m in materials)


def format_material_label(materials: list[dict]) -> str:
    """Format a human-readable label for a materials configuration."""
    parts = []
    for mat in materials:
        name = mat.get("name") or str(mat["id"])
        parts.append(f"{name} ({mat['id']}) x{mat['amount']}")
    return " + ".join(parts)


def write_materials(f, materials: list[dict], indent: str):
    """Write materials list to file."""
    f.write(f"{indent}materials:\n")
    for mat in materials:
        f.write(f"{indent}  - id: {mat['id']}\n")
        f.write(f"{indent}    amount: {mat['amount']}\n")
        f.write(f"{indent}    type: item\n")


def write_group(f, group_label: str, materials: list[dict], entries: list[dict]):
    """Write a single material group as a sequence-element $loop block."""
    last_entry_idx = len(entries) - 1
    last_step_idx = len(ENCHANT_PATTERN) - 1

    f.write(f"    # ── {group_label} ──\n")
    f.write("    - $loop:\n")
    f.write(f"        range: 0..{last_entry_idx}\n")
    f.write("        as: i\n")
    f.write("      template:\n")
    f.write("        targetTemplateId: $entries[$i].target\n")
    f.write("        conditions:\n")
    f.write("          $loop:\n")
    f.write(f"            range: 0..{last_step_idx}\n")
    f.write("            as: j\n")
    f.write("          template:\n")
    f.write("            $extends: baseCondition\n")
    f.write("            targetEnchantStep: $steps[$j].target\n")
    f.write("            result:\n")
    f.write("              resultTemplateId: $entries[$i].result\n")
    f.write("              resultEnchantStep: $steps[$j].result\n")
    write_materials(f, materials, "            ")
    f.write("          $with:\n")
    f.write("            steps:\n")
    for target_step, result_step in ENCHANT_PATTERN:
        f.write(f"              - {{ target: {target_step}, result: {result_step} }}\n")
    f.write("      $with:\n")
    f.write("        entries:\n")
    for entry in entries:
        comment = f"  # {entry['itemString']}" if entry["itemString"] else ""
        f.write(f"          - {{ target: {entry['targetTemplateId']}, "
                f"result: {entry['resultTemplateId']} }}{comment}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate gear evolution YAML specs")
    parser.add_argument("--patch", help="Patch folder name (e.g. 001). Output goes to reforged/specs/patches/{patch}/")
    args = parser.parse_args()

    if args.patch:
        specs_dir = REFORGED_DIR / "specs" / "patches" / args.patch
    else:
        specs_dir = REFORGED_DIR / "specs"

    output_file = specs_dir / "02-evolutions.yaml"

    # Parse CSV and collect evolution entries
    evolutions = []

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            template_id = row.get("TemplateId", "").strip()
            upgrade_to = row.get("UpgradeTo", "").strip()
            item_string = row.get("ItemString", "").strip()
            dungeon = row.get("Dungeon", "").strip()

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
                "dungeon": dungeon,
                "materials": materials,
            })

    # Group by dungeon, then by material configuration
    dungeons: OrderedDict[str, OrderedDict[tuple, list[dict]]] = OrderedDict()
    for evo in evolutions:
        dungeon = evo["dungeon"]
        mat_key = material_key(evo["materials"])
        if dungeon not in dungeons:
            dungeons[dungeon] = OrderedDict()
        if mat_key not in dungeons[dungeon]:
            dungeons[dungeon][mat_key] = []
        dungeons[dungeon][mat_key].append(evo)

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)

    total_entries = 0
    total_groups = 0
    with open(output_file, "w", encoding="utf-8") as f:
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

        for dungeon, mat_groups in dungeons.items():
            f.write(f"    # ━━ {dungeon} ━━\n")
            for mat_key, entries in mat_groups.items():
                materials = entries[0]["materials"]
                mat_label = format_material_label(materials)
                write_group(f, mat_label, materials, entries)
                f.write("\n")
                total_entries += len(entries)
                total_groups += 1

    total_conditions = total_entries * len(ENCHANT_PATTERN)
    print(f"Generated {output_file}")
    print(f"  {len(dungeons)} dungeons, {total_groups} material groups")
    print(f"  {total_entries} evolution entries")
    print(f"  {total_conditions} total conditions")


if __name__ == "__main__":
    main()
