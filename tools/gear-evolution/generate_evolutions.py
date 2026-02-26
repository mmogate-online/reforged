#!/usr/bin/env python3
"""Generate per-gear-set evolution YAML specs from gear_progression.csv.

Reads the CSV, groups by EvolutionSet, and emits one YAML spec per set
into specs/patches/{patch}/evolutions/, referencing the evolution-base package.

Item template IDs are emitted as named variables (SCREAMING_SNAKE_CASE) so
content designers see gear names instead of raw numbers.
"""

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

INPUT_FILE = REFORGED_DIR / "data" / "gear_progression.csv"

# Map (material_id, amount) tuples -> definition name in evolution-base package
MATERIAL_TO_DEFINITION = {
    ((501, 2),): "PaveruneOfSharaPath",
    ((511, 2),): "PaveruneOfArunPath",
    ((502, 2),): "SilruneOfSharaPath",
    ((512, 2),): "SilruneOfArunPath",
    ((503, 2),): "QuoiruneOfSharaPath",
    ((513, 2),): "QuoiruneOfArunPath",
    ((504, 2),): "ArchruneOfSharaPath",
    ((514, 2),): "ArchruneOfArunPath",
    ((505, 2),): "KeyruneOfSharaPath",
    ((515, 2),): "KeyruneOfArunPath",
    ((505, 2), (520, 1)): "KeyruneOfSharaAeruPath",
    ((515, 1), (520, 1)): "KeyruneOfArunAeruPath",
}

# Variables each rune path definition depends on (from evolution-base package)
# All definitions also implicitly require EVOLUTION_COST and EVOLUTION_PROB
# via _EvolutionPathBase.
DEFINITION_VARIABLES = {
    "PaveruneOfSharaPath":    ["PAVERUNE_OF_SHARA"],
    "PaveruneOfArunPath":     ["PAVERUNE_OF_ARUN"],
    "SilruneOfSharaPath":     ["SILRUNE_OF_SHARA"],
    "SilruneOfArunPath":      ["SILRUNE_OF_ARUN"],
    "QuoiruneOfSharaPath":    ["QUOIRUNE_OF_SHARA"],
    "QuoiruneOfArunPath":     ["QUOIRUNE_OF_ARUN"],
    "ArchruneOfSharaPath":    ["ARCHRUNE_OF_SHARA"],
    "ArchruneOfArunPath":     ["ARCHRUNE_OF_ARUN"],
    "KeyruneOfSharaPath":     ["KEYRUNE_OF_SHARA"],
    "KeyruneOfArunPath":      ["KEYRUNE_OF_ARUN"],
    "KeyruneOfSharaAeruPath": ["KEYRUNE_OF_SHARA", "AERU_RUNE"],
    "KeyruneOfArunAeruPath":  ["KEYRUNE_OF_ARUN", "AERU_RUNE"],
}

# Base variables always needed (from _EvolutionPathBase)
BASE_VARIABLES = ["EVOLUTION_COST", "EVOLUTION_PROB"]

# Map material_id -> human-readable label for section comments
MATERIAL_LABELS = {
    501: "Paverune of Shara",
    502: "Silrune of Shara",
    503: "Quoirune of Shara",
    504: "Archrune of Shara",
    505: "Keyrune of Shara",
    511: "Paverune of Arun",
    512: "Silrune of Arun",
    513: "Quoirune of Arun",
    514: "Archrune of Arun",
    515: "Keyrune of Arun",
    520: "Aeru Rune",
}

# EvolutionSet -> (sequence, filename_suffix, dungeon_display_name, gear_set_name)
SET_METADATA = {
    "STARTER_0":    (0, "starter-0",    "Character Creation",  "Starter 0"),
    "STARTER_1":    (1, "starter-1",    "Quest Rewards",       "Starter 1"),
    "Bastion":      (2, "bastion",      "Bastion of Lok",      "Bastion"),
    "Demonia":      (3, "demonia",      "Sinestral Manor",     "Demonia"),
    "Covenant":     (4, "covenant",     "Cultists' Refuge",    "Covenant"),
    "Sepulchral":   (5, "sepulchral",   "Labyrinth of Terror", "Sepulchral"),
    "STARTER_6":    (6, "starter-6",    "Golden Labyrinth",    "Starter 6"),
    "Counterglow":  (7, "counterglow",  "Akasha's Hideout",    "Counterglow"),
    "THALNIM":      (8, "thalnim",      "Suryati's Peak",      "Thalnim"),
}


# Weapon gear categories (from CSV ItemName column)
WEAPON_CATEGORIES = {
    "dual", "lance", "twohand", "axe", "circle", "bow",
    "staff", "rod", "blaster", "shuriken", "glaive", "gauntlet", "chain",
}


def category_to_variable(category: str, direction: str) -> str:
    """Build a variable name from gear category and direction.

    Args:
        category:  CSV ItemName value (e.g. "dual", "bodyMail", "feetRobe")
        direction: "SOURCE" or "TARGET"

    Examples:
        ("dual", "SOURCE")       -> "SOURCE_WEAPON_DUAL"
        ("bodyMail", "TARGET")   -> "TARGET_BODYMAIL"
        ("feetLeather", "SOURCE") -> "SOURCE_FEETLEATHER"
    """
    cat_upper = category.upper()
    if category in WEAPON_CATEGORIES:
        return f"{direction}_WEAPON_{cat_upper}"
    return f"{direction}_{cat_upper}"


class ItemInfo:
    """Holds name and gear category for an item template."""
    __slots__ = ("name", "category")

    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category


def build_item_lookup(csv_path: Path) -> dict[int, ItemInfo]:
    """Build a complete template_id -> ItemInfo lookup from the CSV."""
    items: dict[int, ItemInfo] = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            tid = row.get("TemplateId", "").strip()
            name = row.get("ItemString", "").strip()
            category = row.get("ItemName", "").strip()
            if tid and name:
                try:
                    items[int(tid)] = ItemInfo(name, category)
                except ValueError:
                    pass
    return items


def parse_materials(row: dict) -> list[tuple[int, int]]:
    """Extract materials from row as (id, amount) tuples."""
    materials = []
    for i in range(1, 6):
        material_id = row.get(f"Material_{i}", "").strip()
        amount = row.get(f"Amount_{i}", "").strip()
        if not material_id or not amount:
            continue
        try:
            materials.append((int(material_id), int(amount)))
        except ValueError:
            continue
    return materials


def material_key(materials: list[tuple[int, int]]) -> tuple:
    """Create a hashable key from a materials list for grouping."""
    return tuple(materials)


def get_definition_name(materials: list[tuple[int, int]]) -> str:
    """Look up the evolution-base package definition name for a material config."""
    key = material_key(materials)
    if key in MATERIAL_TO_DEFINITION:
        return MATERIAL_TO_DEFINITION[key]
    raise ValueError(f"Unknown material configuration: {key}. "
                     "Add it to MATERIAL_TO_DEFINITION and evolution-base package.")


def format_material_label(materials: list[tuple[int, int]]) -> str:
    """Format a human-readable label for a materials configuration."""
    parts = []
    for mid, amt in materials:
        name = MATERIAL_LABELS.get(mid, str(mid))
        parts.append(f"{name} x{amt}")
    return " + ".join(parts)


def collect_variables(
    entries: list[dict],
    item_lookup: dict[int, ItemInfo],
) -> tuple[OrderedDict[str, int], OrderedDict[str, int], dict[int, str]]:
    """Collect item ID variables for a gear set, separated by role.

    Variable names are category-based (e.g. SOURCE_WEAPON_DUAL, TARGET_BODYMAIL).

    Returns:
        source_vars: OrderedDict of var_name -> template_id (source gear)
        target_vars: OrderedDict of var_name -> template_id (target/result gear)
        id_to_var:   dict of template_id -> var_name (combined reverse lookup)
    """
    id_to_var: dict[int, str] = {}

    source_vars: OrderedDict[str, int] = OrderedDict()
    target_vars: OrderedDict[str, int] = OrderedDict()

    for entry in entries:
        tid = entry["targetTemplateId"]
        rid = entry["resultTemplateId"]

        if tid not in id_to_var:
            info = item_lookup.get(tid)
            cat = info.category if info else "unknown"
            var_name = category_to_variable(cat, "SOURCE")
            id_to_var[tid] = var_name
            source_vars[var_name] = tid

        if rid not in id_to_var:
            info = item_lookup.get(rid)
            cat = info.category if info else "unknown"
            var_name = category_to_variable(cat, "TARGET")
            id_to_var[rid] = var_name
            target_vars[var_name] = rid

    return source_vars, target_vars, id_to_var


def write_variable_line(f, var_name: str, template_id: int,
                        item_lookup: dict[int, ItemInfo]):
    """Write a single variable line with category and name comment."""
    info = item_lookup.get(template_id)
    if info:
        f.write(f"  {var_name}: {template_id}  # {info.category} — {info.name}\n")
    else:
        f.write(f"  {var_name}: {template_id}\n")


def write_spec(output_dir: Path, evo_set: str, entries: list[dict],
               item_lookup: dict[int, ItemInfo]):
    """Write a single gear-set evolution spec file."""
    meta = SET_METADATA[evo_set]
    seq = meta[0]
    filename = f"02-evo-{seq:02d}-{meta[1]}.yaml"
    dungeon = meta[2]
    gear_name = meta[3]
    output_path = output_dir / filename

    # Build variable lookups for this spec
    source_vars, target_vars, id_to_var = collect_variables(entries, item_lookup)

    # Group entries by material configuration
    groups: OrderedDict[tuple, list[dict]] = OrderedDict()
    for entry in entries:
        key = material_key(entry["materials"])
        if key not in groups:
            groups[key] = []
        groups[key].append(entry)

    # Collect needed rune path definitions and their variable dependencies
    needed_rune_defs = sorted({get_definition_name(e["materials"]) for e in entries})
    needed_vars: set[str] = set(BASE_VARIABLES)
    for d in needed_rune_defs:
        needed_vars.update(DEFINITION_VARIABLES.get(d, []))
    needed_vars_sorted = sorted(needed_vars)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("spec:\n")
        f.write('  version: "1.0"\n')
        f.write("  schema: v92\n")
        f.write("\n")
        f.write("imports:\n")
        f.write("  - from: evolution-base\n")
        f.write("    use:\n")
        f.write("      variables:\n")
        for v in needed_vars_sorted:
            f.write(f"        - {v}\n")
        f.write("      definitions:\n")
        f.write("        - EvolutionItem\n")
        for d in needed_rune_defs:
            f.write(f"        - {d}\n")
        f.write("\n")

        # Write variables section — separated by role
        f.write("variables:\n")
        f.write("  # ── Source Gear ──\n")
        for var_name, template_id in source_vars.items():
            write_variable_line(f, var_name, template_id, item_lookup)
        f.write("\n")
        f.write("  # ── Result Gear ──\n")
        for var_name, template_id in target_vars.items():
            write_variable_line(f, var_name, template_id, item_lookup)
        f.write("\n")

        f.write(f"# {'=' * 75}\n")
        f.write(f"# {gear_name} Gear Set \u2014 {dungeon}\n")
        f.write(f"# {'=' * 75}\n")
        f.write("\n")
        f.write("evolutionPaths:\n")
        f.write("  upsert:\n")

        for mat_key, group_entries in groups.items():
            mat_label = format_material_label(list(mat_key))
            def_name = get_definition_name(list(mat_key))

            # Determine section type from first entry's combat type
            combat_type = group_entries[0].get("combatItemType", "")
            if "WEAPON" in combat_type:
                section = "Weapons"
            elif "ARMOR" in combat_type:
                section = "Armor"
            else:
                section = "Equipment"

            f.write(f"    # \u2500\u2500 {section}: {mat_label} \u2500\u2500\n")

            for entry in group_entries:
                source_var = id_to_var[entry["targetTemplateId"]]
                target_var = id_to_var[entry["resultTemplateId"]]

                f.write(f"    - $extends: EvolutionItem\n")
                f.write(f"      $with: {{ SOURCE: ${source_var}, TARGET: ${target_var}, PATH_DEF: {def_name} }}\n")

        f.write("\n")

    return filename, len(entries)


def main():
    parser = argparse.ArgumentParser(
        description="Generate per-gear-set evolution YAML specs referencing evolution-base package"
    )
    parser.add_argument(
        "--patch",
        help="Patch folder name (e.g. 001). Output goes to reforged/specs/patches/{patch}/evolutions/"
    )
    args = parser.parse_args()

    if args.patch:
        output_dir = REFORGED_DIR / "specs" / "patches" / args.patch / "evolutions"
    else:
        output_dir = REFORGED_DIR / "specs" / "evolutions"

    # Build complete item name lookup from CSV
    item_lookup = build_item_lookup(INPUT_FILE)

    # Parse CSV and collect evolution entries grouped by EvolutionSet
    evolutions: dict[str, list[dict]] = {}

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            evo_set = row.get("EvolutionSet", "").strip()
            template_id = row.get("TemplateId", "").strip()
            upgrade_to = row.get("UpgradeTo", "").strip()

            if not evo_set or not template_id or not upgrade_to:
                continue

            materials = parse_materials(row)
            if not materials:
                continue

            if evo_set not in SET_METADATA:
                continue

            try:
                entry = {
                    "targetTemplateId": int(template_id),
                    "resultTemplateId": int(upgrade_to),
                    "itemString": row.get("ItemString", "").strip(),
                    "combatItemType": row.get("CombatItemType", "").strip(),
                    "materials": materials,
                }
            except ValueError:
                continue

            if evo_set not in evolutions:
                evolutions[evo_set] = []
            evolutions[evo_set].append(entry)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(evolutions)} evolution spec files in {output_dir}:")
    total = 0
    for evo_set in SET_METADATA:
        if evo_set in evolutions:
            filename, count = write_spec(output_dir, evo_set, evolutions[evo_set],
                                         item_lookup)
            print(f"  {filename}: {count} entries")
            total += count

    print(f"\nTotal: {total} evolution entries across {len(evolutions)} gear sets")


if __name__ == "__main__":
    main()
