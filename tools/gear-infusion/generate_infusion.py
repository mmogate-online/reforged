#!/usr/bin/env python3
"""
Generate YAML specs for the Gear Infusion System.

Reads gear_infusion_passivity.csv and generates a single combined file with:
- enchantPassivityCategories (with inline passivities + passivityStrings)
- Infusion items per equipment slot, replicated across decomposition tiers
- Equipment entries for each item

Usage:
    python generate_infusion.py
    python generate_infusion.py --patch 001

Output:
    reforged/specs/gear-infusion-items.yaml (or patches/{patch}/06-gear-infusion-items.yaml)
"""

import argparse
import csv
import math
from pathlib import Path
from dataclasses import dataclass

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

INPUT_FILE = REFORGED_DIR / "data" / "gear_infusion_passivity.csv"
OUTPUT_ITEMS = REFORGED_DIR / "specs" / "gear-infusion-items.yaml"

# ID ranges
PASSIVITY_ID_SEED = 9000000
PASSIVITY_CATEGORY_ID_SEED = 900000
ITEM_ID_SEED = 860000

# Passivities per category (1 = deterministic, no RNG on stat value)
ROLLS_PER_CATEGORY = 1

# Item grade configurations (the grade on the item template itself)
GRADES = [
    {"id": 1, "name": "Uncommon"},
    {"id": 2, "name": "Rare"},
    {"id": 3, "name": "Superior"},
]


# Total gradient steps = len(GRADES) * ROLLS_PER_CATEGORY = 3
GRADIENT_STEPS = len(GRADES) * ROLLS_PER_CATEGORY

# Decomposition tiers — each tier is a full replica of all items with a different decompositionId
# 2000-wide ID blocks per tier (server hard cap: item ID < 1000000)
DECOMP_TIERS = [
    {"tier": 1, "id_offset": 0, "numeral": "I"},
    {"tier": 2, "id_offset": 2000, "numeral": "II"},
    {"tier": 3, "id_offset": 4000, "numeral": "III"},
    {"tier": 4, "id_offset": 6000, "numeral": "IV"},
]

# Decomposition ID base (from DecompositionData.xml lines 3085-3128)
# Formula: DECOMP_ID_BASE + (tier-1)*2 + gear_group_offset
# gear_group_offset: 0 = weapon/body (48 feedstock), 1 = arm/leg (24 feedstock)
DECOMP_ID_BASE = 206861

# Gear groups for decomposition
WEAPON_BODY_SLOTS = {"EQUIP_WEAPON", "EQUIP_ARMOR_BODY"}
ARM_LEG_SLOTS = {"EQUIP_ARMOR_ARM", "EQUIP_ARMOR_LEG"}

# Slot configurations
SLOTS = {
    "EQUIP_WEAPON": {
        "prefix": "WPN",
        "display": "Weapon",
        "subtypes": [
            {"id": "dual", "display": "Twin Swords"},
            {"id": "lance", "display": "Lance"},
            {"id": "twohand", "display": "Greatsword"},
            {"id": "axe", "display": "Axe"},
            {"id": "circle", "display": "Disc"},
            {"id": "bow", "display": "Bow"},
            {"id": "staff", "display": "Staff"},
            {"id": "rod", "display": "Scepter"},
            {"id": "chain", "display": "Scythes"},
            {"id": "blaster", "display": "Arcannon"},
            {"id": "gauntlet", "display": "Powerfists"},
            {"id": "shuriken", "display": "Shuriken"},
            {"id": "glaive", "display": "Glaive"},
        ],
    },
    "EQUIP_ARMOR_BODY": {
        "prefix": "BDY",
        "display": "Chest",
        "subtypes": [
            {"id": "bodyMail", "display": "Mail Chest"},
            {"id": "bodyLeather", "display": "Leather Chest"},
            {"id": "bodyRobe", "display": "Robe Chest"},
        ],
    },
    "EQUIP_ARMOR_ARM": {
        "prefix": "ARM",
        "display": "Gloves",
        "subtypes": [
            {"id": "handMail", "display": "Mail Gloves"},
            {"id": "handLeather", "display": "Leather Gloves"},
            {"id": "handRobe", "display": "Robe Gloves"},
        ],
    },
    "EQUIP_ARMOR_LEG": {
        "prefix": "LEG",
        "display": "Boots",
        "subtypes": [
            {"id": "feetMail", "display": "Mail Boots"},
            {"id": "feetLeather", "display": "Leather Boots"},
            {"id": "feetRobe", "display": "Robe Boots"},
        ],
    },
}

# Passivity type configurations
PASSIVITY_CONFIG = {
    "DamageVsEnraged": {
        "kind": 0, "type": 152, "method": 3, "condition": 28, "conditionValue": 1,
        "is_percent": True, "value_offset": 1.0,
    },
    "DamageWithMaxAggro": {
        "kind": 0, "type": 152, "method": 3, "condition": 32, "conditionValue": 1,
        "is_percent": True, "value_offset": 1.0,
    },
    "DamageVsProne": {
        "kind": 0, "type": 152, "method": 3, "condition": 26, "conditionValue": 1,
        "is_percent": True, "value_offset": 1.0, "mobSize": "all",
    },
    "DamageFromRear": {
        "kind": 0, "type": 152, "method": 3, "condition": 24, "conditionValue": 2,
        "is_percent": True, "value_offset": 1.0, "mobSize": "all",
    },
    "DamageVsMonsters": {
        "kind": 0, "type": 152, "method": 3, "condition": 25, "conditionValue": 3,
        "is_percent": True, "value_offset": 1.0,
    },
    "AttackSpeed": {
        "kind": 0, "type": 25, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
    },
    "CooldownReduction": {
        "kind": 0, "type": 71, "method": 2, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 0.0, "value_invert": True,
    },
    "CritFactor": {
        "kind": 0, "type": 6, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "CritPower": {
        "kind": 0, "type": 19, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "MpReplenishment": {
        "kind": 0, "type": 21, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "MpOnSkillUse": {
        "kind": 0, "type": 232, "method": 2, "condition": 0, "conditionValue": 0,
        "is_percent": True, "value_offset": 0.0,
    },
    "AggroGeneration": {
        "kind": 0, "type": 164, "method": 3, "condition": 25, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
    },
    "HealingSkillFlat": {
        "kind": 0, "type": 168, "method": 2, "condition": 25, "conditionValue": 0,
        "is_percent": False,
        "mobSize": "all",
    },
    "HealingSkillPercent": {
        "kind": 0, "type": 169, "method": 3, "condition": 25, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
        "mobSize": "all",
    },
    "PvpAttack": {
        "kind": 0, "type": 176, "method": 2, "condition": 25, "conditionValue": 3,
        "is_percent": False,
        "mobSize": "player",
    },
    "DamageFromEnraged": {
        "kind": 0, "type": 102, "method": 3, "condition": 9, "conditionValue": 4,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
        "mobSize": "all",
    },
    "DamageWhileProne": {
        "kind": 0, "type": 102, "method": 3, "condition": 11, "conditionValue": 2,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
        "mobSize": "all",
    },
    "FrontalDamageTaken": {
        "kind": 0, "type": 102, "method": 2, "condition": 18, "conditionValue": 1,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
    },
    "DamageTaken": {
        "kind": 0, "type": 102, "method": 3, "condition": 15, "conditionValue": 3,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
        "mobSize": "all",
    },
    "DamageFromMonsters": {
        "kind": 0, "type": 102, "method": 3, "condition": 15, "conditionValue": 3,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
        "mobSize": "all",
    },
    "CritResistFactor": {
        "kind": 0, "type": 7, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "CritResistChance": {
        "kind": 0, "type": 105, "method": 2, "condition": 15, "conditionValue": 0,
        "is_percent": False, "value_invert": True,
        "mobSize": "all",
    },
    "Power": {
        "kind": 0, "type": 3, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "Endurance": {
        "kind": 0, "type": 4, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "MaxHpPercent": {
        "kind": 0, "type": 1, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
    },
    "MaxHpFlat": {
        "kind": 0, "type": 1, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "MaxMp": {
        "kind": 0, "type": 2, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "MpPer5Sec": {
        "kind": 0, "type": 52, "method": 2, "condition": 0, "conditionValue": 0,
        "is_percent": False,
        "mobSize": "all",
        "tickInterval": 5,
    },
    "HealingReceived": {
        "kind": 0, "type": 110, "method": 3, "condition": 15, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
        "mobSize": "all",
    },
    "HpLeech": {
        "kind": 0, "type": 226, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 0.0,
    },
    "DamageReflect": {
        "kind": 0, "type": 203, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 0.0,
    },
    "PvpDefense": {
        "kind": 0, "type": 113, "method": 2, "condition": 15, "conditionValue": 3,
        "is_percent": False,
        "mobSize": "player",
    },
    "CritDamageReduction": {
        "kind": 0, "type": 111, "method": 2, "condition": 15, "conditionValue": 3,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
        "mobSize": "all",
    },
    "MovementSpeed": {
        "kind": 0, "type": 5, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
    },
}


@dataclass
class PassiveDefinition:
    """Parsed passive definition from CSV."""
    order: int
    combat_item_type: str
    role: str
    passive_attribute: str
    passivity_type: int
    min_value: float
    max_value: float
    suffix: str
    tooltip: str
    mob_size: str
    condition: str


def parse_csv() -> list[PassiveDefinition]:
    """Parse the CSV file and return passive definitions."""
    definitions = []

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            order_str = row.get("Order", "").strip()

            if not order_str or order_str.startswith("#"):
                continue

            try:
                order = int(order_str)
            except ValueError:
                continue

            definitions.append(PassiveDefinition(
                order=order,
                combat_item_type=row.get("CombatItemType", "").strip(),
                role=row.get("Role", "").strip(),
                passive_attribute=row.get("PassiveAttribute", "").strip(),
                passivity_type=int(row.get("Type", "0").strip()),
                min_value=float(row.get("Min", "0").strip().replace(",", ".")),
                max_value=float(row.get("Max", "0").strip().replace(",", ".")),
                suffix=row.get("Suffix", "").strip(),
                tooltip=row.get("Tooltip", "").strip(),
                mob_size=row.get("MobSize", "").strip(),
                condition=row.get("Condition", "").strip(),
            ))

    return definitions


def compute_gradient(min_val: float, max_val: float, is_integer: bool) -> list[float]:
    """Compute GRADIENT_STEPS evenly spaced values from min to max.

    Returns a list of 3 values: [0] Uncommon (min), [1] Rare (mid), [2] Superior (max).
    Integer stats are rounded to nearest int.
    """
    values = []
    for i in range(GRADIENT_STEPS):
        raw = min_val + (max_val - min_val) * (i / (GRADIENT_STEPS - 1))
        if is_integer:
            raw = round(raw)
        values.append(raw)
    return values


def is_integer_stat(min_val: float, max_val: float) -> bool:
    """Determine if a stat uses integer values based on the actual CSV data."""
    return min_val == int(min_val) and max_val == int(max_val)


def get_passivity_value(raw_value: float, config: dict) -> float:
    """Convert raw CSV value to passivity value based on config."""
    if config.get("value_invert"):
        if config.get("value_offset", 0) == 1.0:
            return 1.0 - raw_value
        return -raw_value

    if config.get("value_offset", 0) == 1.0:
        return 1.0 + raw_value

    return raw_value


def format_tooltip_value(raw_value: float, config: dict) -> str:
    """Format value for tooltip display."""
    if config.get("is_percent"):
        percent = raw_value * 100
        if percent == int(percent):
            return str(int(percent))
        return f"{percent:.1f}".rstrip("0").rstrip(".")
    else:
        if raw_value == int(raw_value):
            return str(int(raw_value))
        return f"{raw_value:.2f}".rstrip("0").rstrip(".")


def generate_passivity_name(definition: PassiveDefinition, grade: dict, roll: int) -> str:
    """Generate internal passivity name with roll suffix."""
    slot_config = SLOTS.get(definition.combat_item_type, {})
    prefix = slot_config.get("prefix", "UNK")
    return f"TIER{grade['id']}_{prefix}_{definition.passive_attribute}_R{roll}"


def get_decomposition_id(combat_item_type: str, decomp_tier: int) -> int:
    """Calculate decompositionId from slot type and decomposition tier."""
    gear_group_offset = 0 if combat_item_type in WEAPON_BODY_SLOTS else 1
    return DECOMP_ID_BASE + (decomp_tier - 1) * 2 + gear_group_offset


def generate_categories_yaml(definitions: list[PassiveDefinition]) -> tuple[list[str], list[dict]]:
    """Generate enchantPassivityCategories YAML with inline passivities and passivityStrings.

    Each category gets ROLLS_PER_CATEGORY passivities from the gradient.
    """
    lines = [
        "enchantPassivityCategories:",
        "  upsert:",
    ]

    passivity_id = PASSIVITY_ID_SEED
    category_id = PASSIVITY_CATEGORY_ID_SEED
    passivity_data = []

    for definition in definitions:
        config = PASSIVITY_CONFIG.get(definition.passive_attribute)
        if not config:
            print(f"Warning: No config for {definition.passive_attribute}")
            continue

        int_stat = is_integer_stat(definition.min_value, definition.max_value)
        gradient = compute_gradient(definition.min_value, definition.max_value, int_stat)

        for grade_idx, grade in enumerate(GRADES):
            # Slice 3 values for this grade from the 9-step gradient
            start = grade_idx * ROLLS_PER_CATEGORY
            grade_values = gradient[start:start + ROLLS_PER_CATEGORY]

            slot_display = SLOTS[definition.combat_item_type]["display"]
            lines.append(f"    # {grade['name']} {slot_display} - {definition.passive_attribute}")
            lines.append(f"    - enchantPassivityCategoryId: {category_id}")
            lines.append(f"      unchangeable: false")
            lines.append(f"      passivities:")
            lines.append(f"        upsert:")

            for roll_idx, raw_value in enumerate(grade_values):
                roll = roll_idx + 1
                value = get_passivity_value(raw_value, config)
                name = generate_passivity_name(definition, grade, roll)
                tooltip_value = format_tooltip_value(raw_value, config)
                tooltip_text = definition.tooltip.replace("$value", tooltip_value)
                tooltip_escaped = tooltip_text.replace('"', '\\"')

                lines.append(f"          - $extends: passivityBase")
                lines.append(f"            id: {passivity_id}")
                lines.append(f'            name: "{name}"')
                lines.append(f"            type: {config['type']}")
                lines.append(f"            method: {config['method']}")
                lines.append(f"            condition: {config['condition']}")
                lines.append(f"            conditionValue: {config['conditionValue']}")
                lines.append(f"            value: {value}")

                mob_size = config.get("mobSize") or definition.mob_size
                if mob_size:
                    lines.append(f'            mobSize: "{mob_size}"')

                tick_interval = config.get("tickInterval")
                if tick_interval is not None and tick_interval != 0:
                    lines.append(f"            tickInterval: {tick_interval}")

                lines.append(f"            passivityStrings:")
                lines.append(f'              name: "{name}"')
                lines.append(f'              tooltip: "{tooltip_escaped}"')

                passivity_id += 1

            lines.append("")

            passivity_data.append({
                "category_id": category_id,
                "definition": definition,
                "grade": grade,
            })

            category_id += 1

    return lines, passivity_data


def generate_items_yaml(definitions: list[PassiveDefinition], passivity_data: list[dict]) -> list[str]:
    """Generate YAML for infusion items, expanded across subtypes and decomposition tiers."""
    lines = [
        "items:",
        "  upsert:",
    ]

    # Index passivity data by (definition.order, grade_id)
    data_by_key = {}
    for data in passivity_data:
        key = (data["definition"].order, data["grade"]["id"])
        data_by_key[key] = data

    for decomp in DECOMP_TIERS:
        item_id = ITEM_ID_SEED + decomp["id_offset"]
        numeral = decomp["numeral"]
        tier = decomp["tier"]

        lines.append(f"    # === Decomposition Tier {tier} ({numeral}) ===")

        for definition in definitions:
            slot_config = SLOTS.get(definition.combat_item_type, {})
            subtypes = slot_config.get("subtypes", [])
            decomposition_id = get_decomposition_id(definition.combat_item_type, tier)

            for grade in GRADES:
                key = (definition.order, grade["id"])
                data = data_by_key.get(key)
                if not data:
                    continue

                category_id = data["category_id"]
                grade_template = f"infusionItem{grade['name']}"

                for subtype in subtypes:
                    item_name = f"Infusion {subtype['display']} {definition.suffix} {numeral}"
                    internal_name = f"infusion_{subtype['id']}_{definition.passive_attribute.lower()}_t{grade['id']}_d{tier}"
                    link_equipment_id = 900000000 + item_id

                    lines.append(f"    # {item_name} ({grade['name']})")
                    lines.append(f"    - $extends: {grade_template}")
                    lines.append(f"      id: {item_id}")
                    lines.append(f'      name: "{internal_name}"')
                    lines.append(f"      combatItemType: {definition.combat_item_type}")
                    lines.append(f"      combatItemSubType: {subtype['id']}")
                    lines.append(f'      category: "{subtype["id"]}"')
                    lines.append(f"      linkEquipmentId: {link_equipment_id}")
                    lines.append(f"      decompositionId: {decomposition_id}")
                    lines.append(f"      linkPassivityCategoryId:")
                    lines.append(f"        - {category_id}")

                    if definition.role != "ANY":
                        lines.append(f"      # Role restriction: {definition.role}")

                    item_tooltip = f"Infusable Fodder.$BRCan be used to infuse effect on compatible gear, can be upgraded with <font color = '#00A0FF'>Enigmatic Scrolls</font> or can be dismantled for <font color = '#ffbb00'>Tier {tier} Feedstock</font>."
                    lines.append(f"      strings:")
                    lines.append(f'        name: "{item_name}"')
                    lines.append(f'        toolTip: "{item_tooltip}"')
                    lines.append("")

                    item_id += 1

    return lines


def generate_equipment_yaml(definitions: list[PassiveDefinition], passivity_data: list[dict]) -> list[str]:
    """Generate YAML for equipment entries, replicated across decomposition tiers."""
    lines = [
        "equipment:",
        "  upsert:",
    ]

    data_by_key = {}
    for data in passivity_data:
        key = (data["definition"].order, data["grade"]["id"])
        data_by_key[key] = data

    for decomp in DECOMP_TIERS:
        item_id = ITEM_ID_SEED + decomp["id_offset"]

        for definition in definitions:
            slot_config = SLOTS.get(definition.combat_item_type, {})
            subtypes = slot_config.get("subtypes", [])

            for grade in GRADES:
                key = (definition.order, grade["id"])
                data = data_by_key.get(key)
                if not data:
                    continue

                for subtype in subtypes:
                    equipment_id = 900000000 + item_id

                    if definition.combat_item_type == "EQUIP_WEAPON":
                        part = "Weapon"
                        equipment_type = subtype['id'].upper()
                    elif definition.combat_item_type == "EQUIP_ARMOR_BODY":
                        part = "BODY"
                        if subtype['id'] == "bodyMail":
                            equipment_type = "MAIL"
                        elif subtype['id'] == "bodyLeather":
                            equipment_type = "LEATHER"
                        else:
                            equipment_type = "ROBE"
                    elif definition.combat_item_type == "EQUIP_ARMOR_ARM":
                        part = "HAND"
                        if subtype['id'] == "handMail":
                            equipment_type = "MAIL"
                        elif subtype['id'] == "handLeather":
                            equipment_type = "LEATHER"
                        else:
                            equipment_type = "ROBE"
                    else:
                        part = "FEET"
                        if subtype['id'] == "feetMail":
                            equipment_type = "MAIL"
                        elif subtype['id'] == "feetLeather":
                            equipment_type = "LEATHER"
                        else:
                            equipment_type = "ROBE"

                    lines.append(f"    - equipmentId: {equipment_id}")
                    lines.append(f"      level: 1")
                    lines.append(f"      grade: {grade['name']}")
                    lines.append(f"      part: {part}")
                    lines.append(f"      type: {equipment_type}")
                    lines.append(f"      countOfSlot: 0")
                    lines.append(f"      minAtk: 1")
                    lines.append(f"      maxAtk: 1")
                    lines.append(f"      impact: 1")
                    lines.append(f"      balance: 0")
                    lines.append(f"      def: 1")
                    lines.append(f"      atkRate: 1")
                    lines.append(f"      impactRate: 1")
                    lines.append(f"      balanceRate: 1")
                    lines.append(f"      defRate: 1")
                    lines.append("")

                    item_id += 1

    return lines



def generate_combined_yaml(definitions: list[PassiveDefinition]) -> str:
    """Generate the combined YAML file with categories, items, and equipment."""
    lines = [
        "# Gear Infusion System - Categories & Items",
        "# Auto-generated by generate_infusion.py",
        "# DO NOT EDIT MANUALLY",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "definitions:",
        "  # Base infusion item template",
        "  infusionItemBase:",
        "    maxStack: 1",
        "    rank: 16",
        "    tradable: false",
        "    tradeBrokerTradable: false",
        "    boundType: None",
        "    enchantEnable: false",
        "    dismantlable: true",
        "    storeSellable: true",
        "    warehouseStorable: true",
        "    guildWarehouseStorable: false",
        "    destroyable: true",
        "    requiredLevel: 1",
        "    level: 1",
        "    dropIdentify: true",
        "    unidentifiedItemGrade: 1",
        "    masterpieceRate: 0",
        "    isMaterialEquip: true",
        "    searchable: true",
        "    obtainable: true",
        "    relocatable: true",
        "    artisanable: false",
        "    strings:",
        '      toolTip: ""',
        "",
        "  # Grade-specific templates",
        "  infusionItemUncommon:",
        "    $extends: infusionItemBase",
        "    rareGrade: Uncommon",
        "    buyPrice: 1000",
        "    sellPrice: 100",
        "",
        "  infusionItemRare:",
        "    $extends: infusionItemBase",
        "    rareGrade: Rare",
        "    buyPrice: 5000",
        "    sellPrice: 500",
        "",
        "  infusionItemSuperior:",
        "    $extends: infusionItemBase",
        "    rareGrade: Superior",
        "    buyPrice: 25000",
        "    sellPrice: 2500",
        "",
        "  # Base passivity template (common fields)",
        "  passivityBase:",
        "    category: Equipment",
        "    kind: 0",
        "    prob: 1.0",
        "    tickInterval: 0",
        "    balancedByTargetCount: false",
        "    judgmentOnce: false",
        "    conditionCategory: 0",
        "    abnormalityKind: 0",
        "    abnormalityCategory: 0",
        "    mobSize: all",
        "",
    ]

    categories_lines, passivity_data = generate_categories_yaml(definitions)
    lines.extend(categories_lines)

    items_lines = generate_items_yaml(definitions, passivity_data)
    lines.extend(items_lines)

    equipment_lines = generate_equipment_yaml(definitions, passivity_data)
    lines.extend(equipment_lines)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate gear infusion YAML specs")
    parser.add_argument("--patch", help="Patch folder name (e.g. 001). Output goes to reforged/specs/patches/{patch}/")
    args = parser.parse_args()

    if args.patch:
        specs_dir = REFORGED_DIR / "specs" / "patches" / args.patch
        specs_dir.mkdir(parents=True, exist_ok=True)
        output_items = specs_dir / "06-gear-infusion-items.yaml"
    else:
        output_items = OUTPUT_ITEMS

    print(f"Reading definitions from {INPUT_FILE}")
    definitions = parse_csv()
    print(f"Parsed {len(definitions)} passive definitions")

    print("Generating combined YAML...")
    combined_yaml = generate_combined_yaml(definitions)

    print(f"Writing {output_items}")
    with open(output_items, "w", encoding="utf-8") as f:
        f.write(combined_yaml)

    num_categories = len(definitions) * len(GRADES)
    num_passivities = num_categories * ROLLS_PER_CATEGORY
    items_per_tier = sum(
        len(SLOTS[d.combat_item_type]["subtypes"])
        for d in definitions
        for _ in GRADES
    )
    num_tiers = len(DECOMP_TIERS)
    total_items = items_per_tier * num_tiers
    total_equipment = total_items

    print(f"\nGenerated:")
    print(f"  - {num_categories} passivity categories (IDs {PASSIVITY_CATEGORY_ID_SEED} - {PASSIVITY_CATEGORY_ID_SEED + num_categories - 1})")
    print(f"  - {num_passivities} passivities (IDs {PASSIVITY_ID_SEED} - {PASSIVITY_ID_SEED + num_passivities - 1})")
    print(f"  - {total_items} items ({items_per_tier}/tier x {num_tiers} tiers)")
    print(f"  - {total_equipment} equipment entries")
    for decomp in DECOMP_TIERS:
        base = ITEM_ID_SEED + decomp["id_offset"]
        print(f"    Tier {decomp['tier']} ({decomp['numeral']}): IDs {base} - {base + items_per_tier - 1}")
    print(f"\nTo apply:")
    print(f'  dsl apply "{output_items}" --path "D:\\dev\\mmogate\\tera92\\server\\Datasheet"')


if __name__ == "__main__":
    main()
