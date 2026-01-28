#!/usr/bin/env python3
"""
Generate YAML specs for the Gear Infusion System.

Reads gear_infusion_passivity.csv and generates:
- Passivities for all 3 tiers (Uncommon/Rare/Superior)
- Passivity strings for localization
- Infusion fodder items per equipment slot
- Item strings

Usage:
    python generate_infusion.py

Output:
    reforged/specs/gear-infusion-passivities.yaml
    reforged/specs/gear-infusion-items.yaml
"""

import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

INPUT_FILE = REFORGED_DIR / "data" / "gear_infusion_passivity.csv"
OUTPUT_PASSIVITIES = REFORGED_DIR / "specs" / "gear-infusion-passivities.yaml"
OUTPUT_ITEMS = REFORGED_DIR / "specs" / "gear-infusion-items.yaml"

# ID ranges as per GEAR_INFUSION_SYSTEM.md
PASSIVITY_ID_SEED = 9000000
PASSIVITY_CATEGORY_ID_SEED = 900000
ITEM_ID_SEED = 990000

# Grade configurations
GRADES = [
    {"id": 1, "name": "Uncommon", "color": "Green", "tier_field": "Uncommon"},
    {"id": 2, "name": "Rare", "color": "Blue", "tier_field": "Rare"},
    {"id": 3, "name": "Superior", "color": "Yellow", "tier_field": "Superior"},
]

# Slot configurations
SLOTS = {
    "EQUIP_WEAPON": {
        "prefix": "WPN",
        "display": "Weapon",
        "item_category": "enchant_material",
    },
    "EQUIP_ARMOR_BODY": {
        "prefix": "BDY",
        "display": "Chest",
        "item_category": "enchant_material",
    },
    "EQUIP_ARMOR_ARM": {
        "prefix": "ARM",
        "display": "Gloves",
        "item_category": "enchant_material",
    },
    "EQUIP_ARMOR_LEG": {
        "prefix": "LEG",
        "display": "Boots",
        "item_category": "enchant_material",
    },
}

# Passivity type configurations
# Maps PassiveAttribute to the passivity properties
PASSIVITY_CONFIG = {
    # Damage bonuses (type 152)
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
        "kind": 0, "type": 152, "method": 3, "condition": 17, "conditionValue": 1,
        "is_percent": True, "value_offset": 1.0, "mobSize": "all",
    },
    "DamageVsMonsters": {
        "kind": 0, "type": 152, "method": 3, "condition": 25, "conditionValue": 3,
        "is_percent": True, "value_offset": 1.0,
    },
    # Stat increases
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
        "kind": 0, "type": 232, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 0.0,
    },
    # Tank/Healer exclusives
    "AggroGeneration": {
        "kind": 0, "type": 164, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
    },
    "HealingSkillFlat": {
        "kind": 0, "type": 168, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "HealingSkillPercent": {
        "kind": 0, "type": 169, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
    },
    "PvpAttack": {
        "kind": 0, "type": 176, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    # Defensive (type 102) - damage reduction
    "DamageFromEnraged": {
        "kind": 0, "type": 102, "method": 2, "condition": 28, "conditionValue": 1,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
    },
    "DamageWhileProne": {
        "kind": 0, "type": 102, "method": 2, "condition": 26, "conditionValue": 1,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
    },
    "FrontalDamageTaken": {
        "kind": 0, "type": 102, "method": 2, "condition": 18, "conditionValue": 1,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
    },
    "DamageTaken": {
        "kind": 0, "type": 102, "method": 2, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
    },
    "DamageFromMonsters": {
        "kind": 0, "type": 102, "method": 2, "condition": 25, "conditionValue": 3,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
    },
    # Defensive stats
    "CritResistFactor": {
        "kind": 0, "type": 7, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "CritResistChance": {
        "kind": 0, "type": 105, "method": 2, "condition": 1, "conditionValue": 0,
        "is_percent": False, "value_invert": True,
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
        "kind": 0, "type": 52, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    "HealingReceived": {
        "kind": 0, "type": 110, "method": 3, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0,
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
        "kind": 0, "type": 113, "method": 1, "condition": 1, "conditionValue": 0,
        "is_percent": False,
    },
    # Gloves specific
    "CritDamageReduction": {
        "kind": 0, "type": 111, "method": 2, "condition": 1, "conditionValue": 0,
        "is_percent": True, "value_offset": 1.0, "value_invert": True,
    },
    # Boots specific
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
    uncommon: float
    rare: float
    superior: float
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

            # Skip comment lines
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
                uncommon=float(row.get("Uncommon", "0").strip()),
                rare=float(row.get("Rare", "0").strip()),
                superior=float(row.get("Superior", "0").strip()),
                suffix=row.get("Suffix", "").strip(),
                tooltip=row.get("Tooltip", "").strip(),
                mob_size=row.get("MobSize", "").strip(),
                condition=row.get("Condition", "").strip(),
            ))

    return definitions


def get_passivity_value(raw_value: float, config: dict) -> float:
    """Convert raw CSV value to passivity value based on config."""
    if config.get("value_invert"):
        # For reductions: 0.03 (3% reduction) -> 0.97 (multiply by this)
        if config.get("value_offset", 0) == 1.0:
            return 1.0 - raw_value
        return -raw_value

    if config.get("value_offset", 0) == 1.0:
        # For multipliers: 0.03 (3% increase) -> 1.03
        return 1.0 + raw_value

    return raw_value


def format_tooltip_value(raw_value: float, config: dict) -> str:
    """Format value for tooltip display."""
    if config.get("is_percent"):
        # Convert decimal to percentage
        percent = raw_value * 100
        if percent == int(percent):
            return str(int(percent))
        return f"{percent:.1f}".rstrip("0").rstrip(".")
    else:
        # Flat values
        if raw_value == int(raw_value):
            return str(int(raw_value))
        return f"{raw_value:.2f}".rstrip("0").rstrip(".")


def generate_passivity_name(definition: PassiveDefinition, grade: dict) -> str:
    """Generate internal passivity name."""
    slot_config = SLOTS.get(definition.combat_item_type, {})
    prefix = slot_config.get("prefix", "UNK")
    return f"TIER{grade['id']}_{prefix}_{definition.passive_attribute}"


def generate_passivities_yaml(definitions: list[PassiveDefinition]) -> str:
    """Generate YAML for passivities and passivity strings."""
    lines = [
        "# Gear Infusion System - Passivities",
        "# Auto-generated by generate_infusion.py",
        "# DO NOT EDIT MANUALLY",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "passivities:",
        "  upsert:",
    ]

    passivity_id = PASSIVITY_ID_SEED
    passivity_data = []  # Store for strings generation

    for definition in definitions:
        config = PASSIVITY_CONFIG.get(definition.passive_attribute)
        if not config:
            print(f"Warning: No config for {definition.passive_attribute}")
            continue

        for grade in GRADES:
            tier_value = getattr(definition, grade["tier_field"].lower())
            value = get_passivity_value(tier_value, config)
            name = generate_passivity_name(definition, grade)
            tooltip_value = format_tooltip_value(tier_value, config)
            tooltip = definition.tooltip.replace("$value", tooltip_value)

            lines.append(f"    # {grade['name']} {SLOTS[definition.combat_item_type]['display']} - {definition.passive_attribute}")
            lines.append(f"    - category: Equipment")
            lines.append(f"      id: {passivity_id}")
            lines.append(f'      name: "{name}"')
            lines.append(f"      kind: {config['kind']}")
            lines.append(f"      type: {config['type']}")
            lines.append(f"      method: {config['method']}")
            lines.append(f"      condition: {config['condition']}")
            lines.append(f"      conditionValue: {config['conditionValue']}")
            lines.append(f"      value: {value}")
            lines.append(f"      prob: 1.0")
            lines.append(f"      tickInterval: 0")
            lines.append(f"      balancedByTargetCount: false")
            lines.append(f"      judgmentOnce: false")

            # Add mobSize if specified
            mob_size = config.get("mobSize") or definition.mob_size
            if mob_size:
                lines.append(f'      mobSize: "{mob_size}"')

            lines.append("")

            passivity_data.append({
                "id": passivity_id,
                "name": name,
                "tooltip": tooltip,
                "definition": definition,
                "grade": grade,
            })

            passivity_id += 1

    # Generate passivity strings
    lines.append("passivityStrings:")
    lines.append("  upsert:")

    for data in passivity_data:
        lines.append(f"    - id: {data['id']}")
        lines.append(f'      name: "{data["name"]}"')
        # Escape quotes in tooltip
        tooltip_escaped = data["tooltip"].replace('"', '\\"')
        lines.append(f'      tooltip: "{tooltip_escaped}"')
        lines.append("")

    return "\n".join(lines), passivity_data


def generate_items_yaml(definitions: list[PassiveDefinition], passivity_data: list) -> str:
    """Generate YAML for infusion fodder items."""
    lines = [
        "# Gear Infusion System - Items",
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
        "    tradable: false",
        "    boundType: Loot",
        "    dismantlable: true",
        "    storeSellable: false",
        "    warehouseStorable: true",
        "    guildWarehouseStorable: false",
        "    destroyable: true",
        "    requiredLevel: 1",
        "",
        "  # Grade-specific templates",
        "  infusionItemUncommon:",
        "    $extends: infusionItemBase",
        "    rareGrade: Uncommon",
        "    buyPrice: 1000",
        "    sellPrice: 100",
        "    icon: 'Icon_Items.Item_InfusionCore_Green_Tex'",
        "",
        "  infusionItemRare:",
        "    $extends: infusionItemBase",
        "    rareGrade: Rare",
        "    buyPrice: 5000",
        "    sellPrice: 500",
        "    icon: 'Icon_Items.Item_InfusionCore_Blue_Tex'",
        "",
        "  infusionItemSuperior:",
        "    $extends: infusionItemBase",
        "    rareGrade: Superior",
        "    buyPrice: 25000",
        "    sellPrice: 2500",
        "    icon: 'Icon_Items.Item_InfusionCore_Yellow_Tex'",
        "",
        "items:",
        "  upsert:",
    ]

    item_id = ITEM_ID_SEED
    category_id = PASSIVITY_CATEGORY_ID_SEED

    # Group passivity data by definition order for easier processing
    passivity_by_order_grade = {}
    for data in passivity_data:
        key = (data["definition"].order, data["grade"]["id"])
        passivity_by_order_grade[key] = data

    for definition in definitions:
        slot_config = SLOTS.get(definition.combat_item_type, {})
        slot_display = slot_config.get("display", "Unknown")

        for grade in GRADES:
            key = (definition.order, grade["id"])
            data = passivity_by_order_grade.get(key)
            if not data:
                continue

            passivity_id = data["id"]

            # Generate item name using suffix format: "Infusion [Slot] [Suffix]"
            # Example: "Infusion Weapon of Wrath"
            item_name = f"Infusion {slot_display} {definition.suffix}"
            internal_name = f"infusion_{slot_config['prefix'].lower()}_{definition.passive_attribute.lower()}_t{grade['id']}"

            # Determine template based on grade
            grade_template = f"infusionItem{grade['name']}"

            lines.append(f"    # {item_name} ({grade['name']})")
            lines.append(f"    - $extends: {grade_template}")
            lines.append(f"      id: {item_id}")
            lines.append(f'      name: "{internal_name}"')
            lines.append(f"      combatItemType: ENCHANT_MATERIAL")
            lines.append(f"      combatItemSubType: enchant_material")
            lines.append(f'      category: "{slot_config["item_category"]}"')
            lines.append(f"      # Target slot: {definition.combat_item_type}")
            lines.append(f"      linkPassivityId:")
            lines.append(f'        - "{passivity_id}"')

            # Add role restriction comment if not ANY
            if definition.role != "ANY":
                lines.append(f"      # Role restriction: {definition.role}")

            # Inline strings block
            config = PASSIVITY_CONFIG.get(definition.passive_attribute, {})
            tier_value = getattr(definition, grade["tier_field"].lower())
            tooltip_value = format_tooltip_value(tier_value, config)
            tooltip = definition.tooltip.replace("$value", tooltip_value)

            lines.append(f"      strings:")
            lines.append(f'        name: "{item_name}"')
            tooltip_escaped = tooltip.replace('"', '\\"')
            lines.append(f'        toolTip: "Infusion Core. {tooltip_escaped} Use on {slot_display.lower()} to apply this effect."')
            lines.append("")

            item_id += 1

    return "\n".join(lines)


def main():
    print(f"Reading definitions from {INPUT_FILE}")
    definitions = parse_csv()
    print(f"Parsed {len(definitions)} passive definitions")

    print("Generating passivities YAML...")
    passivities_yaml, passivity_data = generate_passivities_yaml(definitions)

    print("Generating items YAML...")
    items_yaml = generate_items_yaml(definitions, passivity_data)

    print(f"Writing {OUTPUT_PASSIVITIES}")
    with open(OUTPUT_PASSIVITIES, "w", encoding="utf-8") as f:
        f.write(passivities_yaml)

    print(f"Writing {OUTPUT_ITEMS}")
    with open(OUTPUT_ITEMS, "w", encoding="utf-8") as f:
        f.write(items_yaml)

    total_passivities = len(definitions) * len(GRADES)
    total_items = len(definitions) * len(GRADES)

    print(f"\nGenerated:")
    print(f"  - {total_passivities} passivities (IDs {PASSIVITY_ID_SEED} - {PASSIVITY_ID_SEED + total_passivities - 1})")
    print(f"  - {total_items} items (IDs {ITEM_ID_SEED} - {ITEM_ID_SEED + total_items - 1})")
    print(f"\nTo apply:")
    print(f'  dsl apply "{OUTPUT_PASSIVITIES}" --path "D:\\dev\\mmogate\\tera92\\server\\Datasheet"')
    print(f'  dsl apply "{OUTPUT_ITEMS}" --path "D:\\dev\\mmogate\\tera92\\server\\Datasheet"')


if __name__ == "__main__":
    main()
