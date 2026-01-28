#!/usr/bin/env python3
"""
Enchant Materials Generator

Reads enchant.xlsx and generates:
1. reforged/specs/enchant-materials.yaml - MaterialEnchantData definitions
2. reforged/specs/enchant-item-links.yaml - Items updateWhere rules

Uses DSL expansion system ($repeat, $extends, $with) for compact output.

ID Scheme for materialEnchantId:
  Base: 20000
  Pattern: 20000 + (levelRangeIndex * 1000) + (slotGroupIndex * 100) + rank

  levelRangeIndex: 0=1-37, 1=38-49, 2=50-57, 3=58+
  slotGroupIndex: 0=WeC (Weapons & Chest), 1=GeB (Gloves & Boots)
"""

import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl not installed. Run: pip install openpyxl")
    sys.exit(1)


# Configuration
ALKAHEST_ID = 21351
FEEDSTOCK_BASE_ID = 94100  # Feedstock ID = 94100 + rank

LEVEL_RANGES = [
    (0, "1..37", 1, 37),
    (1, "38..49", 38, 49),
    (2, "50..57", 50, 57),
    (3, "58..65", 58, 65),  # 58+ represented as 58..65
]

SLOT_GROUPS = [
    (0, "WeC", ["EQUIP_WEAPON", "EQUIP_ARMOR_BODY"]),
    (1, "GeB", ["EQUIP_ARMOR_ARM", "EQUIP_ARMOR_LEG"]),
]

# Rank distribution per level range (from analysis)
RANKS_BY_LEVEL_RANGE = {
    0: [1, 2],           # Level 1-37
    1: [2],              # Level 38-49
    2: [2, 3],           # Level 50-57
    3: list(range(3, 23)),  # Level 58+: ranks 3-22
}

MAX_ENCHANT_COUNT = 15  # +0 to +14


@dataclass
class EnchantStep:
    step: int
    prob: float
    alkahest_amount: int
    feedstock_amount: int


@dataclass
class MaterialEnchantConfig:
    material_enchant_id: int
    level_range_idx: int
    level_range_str: str
    slot_group_idx: int
    slot_group_name: str
    combat_item_types: list
    rank: int
    steps: list  # List of EnchantStep


def calculate_material_enchant_id(level_range_idx: int, slot_group_idx: int, rank: int) -> int:
    """Calculate materialEnchantId using the defined scheme."""
    return 20000 + (level_range_idx * 1000) + (slot_group_idx * 100) + rank


def read_excel_sheet(wb, sheet_name: str) -> dict:
    """Read a sheet and return data as dict[enchant_step][level_range_col] = value."""
    ws = wb[sheet_name]

    # Column headers are in row 1: first col is enchant step, rest are level ranges
    col_headers = []
    for col in range(2, ws.max_column + 1):
        header = ws.cell(row=1, column=col).value
        if header:
            col_headers.append((col, str(header).strip()))

    data = {}
    for row in range(2, ws.max_row + 1):
        step_val = ws.cell(row=row, column=1).value
        if step_val is None:
            continue
        step = int(step_val)
        data[step] = {}
        for col, header in col_headers:
            val = ws.cell(row=row, column=col).value
            if val is not None:
                data[step][header] = float(val) if isinstance(val, (int, float)) else val

    return data


def map_level_range_to_col(level_range_idx: int) -> str:
    """Map level range index to Excel column header."""
    col_map = {
        0: "1 ~37",
        1: "38 ~49",
        2: "50 ~57",
        3: "58",
    }
    return col_map[level_range_idx]


def load_enchant_data(xlsx_path: str) -> tuple:
    """Load all enchant data from Excel file."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)

    chance_data = read_excel_sheet(wb, "Chance")
    alkahest_wec = read_excel_sheet(wb, "Alkahest WeC")
    alkahest_geb = read_excel_sheet(wb, "Alkahest GeB")
    feedstock_wec = read_excel_sheet(wb, "Feedstock WeC")
    feedstock_geb = read_excel_sheet(wb, "Feedstock GeB")

    wb.close()

    return chance_data, alkahest_wec, alkahest_geb, feedstock_wec, feedstock_geb


def build_material_enchant_configs(
    chance_data: dict,
    alkahest_wec: dict,
    alkahest_geb: dict,
    feedstock_wec: dict,
    feedstock_geb: dict,
) -> list:
    """Build all MaterialEnchantConfig objects."""
    configs = []

    for level_range_idx, level_range_str, level_min, level_max in LEVEL_RANGES:
        col_name = map_level_range_to_col(level_range_idx)
        ranks = RANKS_BY_LEVEL_RANGE[level_range_idx]

        for slot_group_idx, slot_group_name, combat_types in SLOT_GROUPS:
            # Select alkahest/feedstock data based on slot group
            alkahest_data = alkahest_wec if slot_group_idx == 0 else alkahest_geb
            feedstock_data = feedstock_wec if slot_group_idx == 0 else feedstock_geb

            for rank in ranks:
                material_enchant_id = calculate_material_enchant_id(
                    level_range_idx, slot_group_idx, rank
                )

                steps = []
                for step in range(MAX_ENCHANT_COUNT):
                    prob = chance_data.get(step, {}).get(col_name, 1.0)
                    alkahest_amount = int(alkahest_data.get(step, {}).get(col_name, 0))
                    feedstock_amount = int(feedstock_data.get(step, {}).get(col_name, 0))

                    steps.append(EnchantStep(
                        step=step,
                        prob=prob,
                        alkahest_amount=alkahest_amount,
                        feedstock_amount=feedstock_amount,
                    ))

                configs.append(MaterialEnchantConfig(
                    material_enchant_id=material_enchant_id,
                    level_range_idx=level_range_idx,
                    level_range_str=level_range_str,
                    slot_group_idx=slot_group_idx,
                    slot_group_name=slot_group_name,
                    combat_item_types=combat_types,
                    rank=rank,
                    steps=steps,
                ))

    return configs


def format_array(values: list, formatter=str) -> str:
    """Format a list as YAML inline array."""
    formatted = [formatter(v) for v in values]
    return "[" + ", ".join(formatted) + "]"


def format_prob(p: float) -> str:
    """Format probability value."""
    if p == 1.0:
        return "1.0"
    elif p == 0.0:
        return "0.0"
    else:
        return f"{p:.2f}".rstrip('0').rstrip('.')


def generate_material_enchants_yaml(configs: list) -> str:
    """Generate the materialEnchants YAML spec using DSL expansion system."""
    lines = [
        "# Enchant Materials System - MaterialEnchantData",
        "# Auto-generated by generate_enchant_materials.py",
        "# Uses DSL expansion system ($repeat, $extends, $with)",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "definitions:",
        "  # Reusable template for 15 enchant steps (0..14)",
        "  enchantProgression:",
        "    $repeat:",
        "      range: 0..14",
        "      as: step",
        "    template:",
        "      enchantStep: $step",
        "      enchantProb: $probs[$step]",
        "      requiredMoney: 0",
        "      materials:",
        f"        - id: {ALKAHEST_ID}",
        "          type: Item",
        "          amount: $alkahest[$step]",
        "        - id: $feedstockId",
        "          type: Item",
        "          amount: $feedstock[$step]",
        "",
        "materialEnchants:",
        "  upsert:",
    ]

    for config in configs:
        feedstock_id = FEEDSTOCK_BASE_ID + config.rank

        # Extract arrays from steps
        probs = [format_prob(s.prob) for s in config.steps]
        alkahest = [s.alkahest_amount for s in config.steps]
        feedstock = [s.feedstock_amount for s in config.steps]

        lines.append(f"    # {config.slot_group_name}, Level {config.level_range_str}, Rank {config.rank}")
        lines.append(f"    - materialEnchantId: {config.material_enchant_id}")
        lines.append(f"      maxEnchantCount: {MAX_ENCHANT_COUNT}")
        lines.append("      materialItems:")
        lines.append("        $extends: enchantProgression")
        lines.append("        $with:")
        lines.append(f"          probs: {format_array(probs)}")
        lines.append(f"          alkahest: {format_array(alkahest)}")
        lines.append(f"          feedstock: {format_array(feedstock)}")
        lines.append(f"          feedstockId: {feedstock_id}")
        lines.append("")

    return "\n".join(lines)


def generate_item_links_yaml(configs: list) -> str:
    """Generate the items updateWhere YAML spec."""
    lines = [
        "# Enchant Materials System - Item Links",
        "# Auto-generated by generate_enchant_materials.py",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "items:",
        "  updateWhere:",
    ]

    for config in configs:
        combat_types_yaml = "[" + ", ".join(config.combat_item_types) + "]"

        lines.append(f"    # {config.slot_group_name}, Level {config.level_range_str}, Rank {config.rank}")
        lines.append("    - filter:")
        lines.append("        enchantEnable: true")
        lines.append(f"        combatItemType: {combat_types_yaml}")
        lines.append(f"        level: {config.level_range_str}")
        lines.append(f"        rank: {config.rank}")
        lines.append("      changes:")
        lines.append(f"        linkMaterialEnchantId: {config.material_enchant_id}")
        lines.append("")

    return "\n".join(lines)


def main():
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent  # reforged-server-content
    xlsx_path = project_root / "enchant.xlsx"
    specs_dir = project_root / "reforged" / "specs"

    if not xlsx_path.exists():
        print(f"Error: {xlsx_path} not found")
        sys.exit(1)

    print(f"Reading {xlsx_path}...")
    chance_data, alkahest_wec, alkahest_geb, feedstock_wec, feedstock_geb = load_enchant_data(str(xlsx_path))

    print("Building material enchant configurations...")
    configs = build_material_enchant_configs(
        chance_data, alkahest_wec, alkahest_geb, feedstock_wec, feedstock_geb
    )
    print(f"Generated {len(configs)} configurations")

    # Generate YAML specs
    materials_yaml = generate_material_enchants_yaml(configs)
    item_links_yaml = generate_item_links_yaml(configs)

    # Write output files
    materials_path = specs_dir / "enchant-materials.yaml"
    item_links_path = specs_dir / "enchant-item-links.yaml"

    print(f"Writing {materials_path}...")
    with open(materials_path, "w", encoding="utf-8") as f:
        f.write(materials_yaml)

    print(f"Writing {item_links_path}...")
    with open(item_links_path, "w", encoding="utf-8") as f:
        f.write(item_links_yaml)

    # Count lines for comparison
    old_line_estimate = len(configs) * 150  # ~150 lines per entry in old format
    new_lines = len(materials_yaml.split('\n'))

    print(f"\nDone!")
    print(f"  Old format estimate: ~{old_line_estimate} lines")
    print(f"  New format: {new_lines} lines")
    print(f"  Reduction: ~{100 - (new_lines * 100 // old_line_estimate)}%")
    print(f"\nNext steps:")
    print(f"  dsl validate \"{materials_path.relative_to(project_root)}\" --path \"D:\\dev\\mmogate\\tera92\\server\\Datasheet\"")
    print(f"  dsl apply \"{materials_path.relative_to(project_root)}\" --path \"D:\\dev\\mmogate\\tera92\\server\\Datasheet\"")


if __name__ == "__main__":
    main()
