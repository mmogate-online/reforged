#!/usr/bin/env python3
"""
Gear Enchant Sync Tool

Generates a DSL spec that updates gear items from gear_progression.csv to use
the correct linkEnchantId values, using ID-based filters for precise targeting.

Usage:
    python generate_spec.py
    python generate_spec.py --patch 001

Output:
    reforged/specs/gear-enchant-sync.yaml (or patches/{patch}/04-gear-enchant-sync.yaml)
"""

import argparse
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent
DEFAULT_OUTPUT = REFORGED_DIR / "specs" / "gear-enchant-sync.yaml"

# Mapping from ID variable names to enchant variable names
SLOT_MAPPINGS = [
    # High Tier (Mythic)
    ("HIGH_TIER_HEALER_WEAPON_IDS", "ENCHANT_HIGH_TIER_WEAPON_HEALER", "Mythic Healer Weapons"),
    ("HIGH_TIER_DPS_WEAPON_IDS", "ENCHANT_HIGH_TIER_WEAPON_DPS_TANK", "Mythic DPS/Tank Weapons"),
    ("HIGH_TIER_BODY_IDS", "ENCHANT_HIGH_TIER_CHEST", "Mythic Body Armor"),
    ("HIGH_TIER_HAND_MAIL_IDS", "ENCHANT_HIGH_TIER_HAND_MAIL", "Mythic Hand Mail"),
    ("HIGH_TIER_HAND_LEATHER_IDS", "ENCHANT_HIGH_TIER_HAND_LEATHER", "Mythic Hand Leather"),
    ("HIGH_TIER_HAND_ROBE_IDS", "ENCHANT_HIGH_TIER_HAND_ROBE", "Mythic Hand Robe"),
    ("HIGH_TIER_FEET_IDS", "ENCHANT_HIGH_TIER_BOOTS", "Mythic Feet Armor"),
    # Mid Tier (Superior)
    ("MID_TIER_HEALER_WEAPON_IDS", "ENCHANT_MID_TIER_WEAPON_HEALER", "Superior Healer Weapons"),
    ("MID_TIER_DPS_WEAPON_IDS", "ENCHANT_MID_TIER_WEAPON_DPS_TANK", "Superior DPS/Tank Weapons"),
    ("MID_TIER_BODY_IDS", "ENCHANT_MID_TIER_CHEST", "Superior Body Armor"),
    ("MID_TIER_HAND_MAIL_IDS", "ENCHANT_MID_TIER_HAND_MAIL", "Superior Hand Mail"),
    ("MID_TIER_HAND_LEATHER_IDS", "ENCHANT_MID_TIER_HAND_LEATHER", "Superior Hand Leather"),
    ("MID_TIER_HAND_ROBE_IDS", "ENCHANT_MID_TIER_HAND_ROBE", "Superior Hand Robe"),
    ("MID_TIER_FEET_IDS", "ENCHANT_MID_TIER_BOOTS", "Superior Feet Armor"),
    # Low Tier (Uncommon/Rare)
    ("LOW_TIER_HEALER_WEAPON_IDS", "ENCHANT_LOW_TIER_WEAPON_HEALER", "Uncommon/Rare Healer Weapons"),
    ("LOW_TIER_DPS_WEAPON_IDS", "ENCHANT_LOW_TIER_WEAPON_DPS_TANK", "Uncommon/Rare DPS/Tank Weapons"),
    ("LOW_TIER_BODY_IDS", "ENCHANT_LOW_TIER_CHEST", "Uncommon/Rare Body Armor"),
    ("LOW_TIER_HAND_MAIL_IDS", "ENCHANT_LOW_TIER_HAND_MAIL", "Uncommon/Rare Hand Mail"),
    ("LOW_TIER_HAND_LEATHER_IDS", "ENCHANT_LOW_TIER_HAND_LEATHER", "Uncommon/Rare Hand Leather"),
    ("LOW_TIER_HAND_ROBE_IDS", "ENCHANT_LOW_TIER_HAND_ROBE", "Uncommon/Rare Hand Robe"),
    ("LOW_TIER_FEET_IDS", "ENCHANT_LOW_TIER_BOOTS", "Uncommon/Rare Feet Armor"),
]


def generate_spec() -> str:
    """Generate the DSL spec YAML content using ID-based filters."""
    lines = [
        "# Gear Enchant Sync Spec",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "#",
        "# Updates gear items from gear_progression.csv to use the correct linkEnchantId",
        "# values from the enchant-standard package.",
        "#",
        "# Uses ID-based filters for precise targeting of items listed in the CSV.",
        "",
        "spec:",
        "  version: \"1.0\"",
        "  schema: v92",
        "",
        "imports:",
        "  - from: enchant-standard",
        "    use:",
        "      variables:",
        "        # High Tier (Mythic)",
        "        - ENCHANT_HIGH_TIER_WEAPON_DPS_TANK",
        "        - ENCHANT_HIGH_TIER_WEAPON_HEALER",
        "        - ENCHANT_HIGH_TIER_CHEST",
        "        - ENCHANT_HIGH_TIER_HAND_MAIL",
        "        - ENCHANT_HIGH_TIER_HAND_LEATHER",
        "        - ENCHANT_HIGH_TIER_HAND_ROBE",
        "        - ENCHANT_HIGH_TIER_BOOTS",
        "        # Mid Tier (Superior)",
        "        - ENCHANT_MID_TIER_WEAPON_DPS_TANK",
        "        - ENCHANT_MID_TIER_WEAPON_HEALER",
        "        - ENCHANT_MID_TIER_CHEST",
        "        - ENCHANT_MID_TIER_HAND_MAIL",
        "        - ENCHANT_MID_TIER_HAND_LEATHER",
        "        - ENCHANT_MID_TIER_HAND_ROBE",
        "        - ENCHANT_MID_TIER_BOOTS",
        "        # Low Tier (Uncommon/Rare)",
        "        - ENCHANT_LOW_TIER_WEAPON_DPS_TANK",
        "        - ENCHANT_LOW_TIER_WEAPON_HEALER",
        "        - ENCHANT_LOW_TIER_CHEST",
        "        - ENCHANT_LOW_TIER_HAND_MAIL",
        "        - ENCHANT_LOW_TIER_HAND_LEATHER",
        "        - ENCHANT_LOW_TIER_HAND_ROBE",
        "        - ENCHANT_LOW_TIER_BOOTS",
        "",
        "  - from: equipment-item-ids",
        "    use:",
        "      variables:",
        "        # High Tier (Mythic) Item IDs",
        "        - HIGH_TIER_HEALER_WEAPON_IDS",
        "        - HIGH_TIER_DPS_WEAPON_IDS",
        "        - HIGH_TIER_BODY_IDS",
        "        - HIGH_TIER_HAND_MAIL_IDS",
        "        - HIGH_TIER_HAND_LEATHER_IDS",
        "        - HIGH_TIER_HAND_ROBE_IDS",
        "        - HIGH_TIER_FEET_IDS",
        "        # Mid Tier (Superior) Item IDs",
        "        - MID_TIER_HEALER_WEAPON_IDS",
        "        - MID_TIER_DPS_WEAPON_IDS",
        "        - MID_TIER_BODY_IDS",
        "        - MID_TIER_HAND_MAIL_IDS",
        "        - MID_TIER_HAND_LEATHER_IDS",
        "        - MID_TIER_HAND_ROBE_IDS",
        "        - MID_TIER_FEET_IDS",
        "        # Low Tier (Uncommon/Rare) Item IDs",
        "        - LOW_TIER_HEALER_WEAPON_IDS",
        "        - LOW_TIER_DPS_WEAPON_IDS",
        "        - LOW_TIER_BODY_IDS",
        "        - LOW_TIER_HAND_MAIL_IDS",
        "        - LOW_TIER_HAND_LEATHER_IDS",
        "        - LOW_TIER_HAND_ROBE_IDS",
        "        - LOW_TIER_FEET_IDS",
        "",
        "items:",
        "  updateWhere:",
    ]

    current_tier = None
    for id_var, enchant_var, description in SLOT_MAPPINGS:
        if id_var.startswith("HIGH_"):
            tier = "HIGH TIER (Mythic)"
        elif id_var.startswith("MID_"):
            tier = "MID TIER (Superior)"
        else:
            tier = "LOW TIER (Uncommon/Rare)"

        if tier != current_tier:
            current_tier = tier
            lines.append("")
            lines.append(f"    # =========================================================================")
            lines.append(f"    # {tier}")
            lines.append(f"    # =========================================================================")

        lines.append("")
        lines.append(f"    # {description}")
        lines.append(f"    - filter:")
        lines.append(f"        id: ${id_var}")
        lines.append(f"      changes:")
        lines.append(f"        linkEnchantId: ${enchant_var}")

    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate gear enchant sync YAML spec")
    parser.add_argument("--patch", help="Patch folder name (e.g. 001). Output goes to reforged/specs/patches/{patch}/")
    args = parser.parse_args()

    if args.patch:
        specs_dir = REFORGED_DIR / "specs" / "patches" / args.patch
        specs_dir.mkdir(parents=True, exist_ok=True)
        output_path = specs_dir / "07-gear-enchant-sync.yaml"
    else:
        output_path = DEFAULT_OUTPUT

    print("Generating spec with ID-based filters...")
    spec_content = generate_spec()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print(f"Spec written to: {output_path}")

    # Count updateWhere rules
    rule_count = spec_content.count("- filter:")
    print(f"Generated {rule_count} updateWhere rules")


if __name__ == "__main__":
    main()
