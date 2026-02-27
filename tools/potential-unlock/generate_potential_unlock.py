#!/usr/bin/env python3
"""Generate Potential Unlock system specs for gear progression items.

Reads gear_progression.csv (with UnlockTo column) and server XMLs to generate:
  - 11-potential-unlock-scroll.yaml    (scroll item + inheritance mappings)
  - 12-potential-unlock-gear.yaml      (unlocked items + equipment, stats match source)
  - 13-potential-unlock-evolution.yaml  (unlocked -> flawless evolution paths)
  - potential_unlock_progression.csv    (tracking data)

Usage:
    python generate_potential_unlock.py [--write] [--datasheet PATH]
"""

import argparse
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent

# ── Input / Output Paths ────────────────────────────────────────────────────
CSV_INPUT = REFORGED_DIR / "data" / "gear_progression.csv"
CSV_OUTPUT = REFORGED_DIR / "data" / "potential_unlock_progression.csv"
SCROLL_SPEC = REFORGED_DIR / "specs" / "patches" / "001" / "11-potential-unlock-scroll.yaml"
GEAR_SPEC = REFORGED_DIR / "specs" / "patches" / "001" / "12-potential-unlock-gear.yaml"
EVOLUTION_SPEC = REFORGED_DIR / "specs" / "patches" / "001" / "13-potential-unlock-evolution.yaml"

# ── ID Seeds ────────────────────────────────────────────────────────────────
UNLOCK_ID_SEED = 280000
UNLOCK_EQUIP_BASE = 900000000

# ── Scroll ID ───────────────────────────────────────────────────────────────
SCROLL_ID = 90

# ── Material ID → Evolution Path Definition ─────────────────────────────────
MATERIAL_TO_PATH = {
    502: "SilruneOfSharaPath",
    503: "QuoiruneOfSharaPath",
    504: "ArchruneOfSharaPath",
    512: "SilruneOfArunPath",
    513: "QuoiruneOfArunPath",
    514: "ArchruneOfArunPath",
    515: "KeyruneOfArunPath",
}

# ── Path Definition → Required Variables ────────────────────────────────────
# Each path def extends _EvolutionPathBase (needs EVOLUTION_COST, EVOLUTION_PROB)
# and references its own material variable.
PATH_TO_VARIABLES = {
    "SilruneOfSharaPath": ["SILRUNE_OF_SHARA"],
    "SilruneOfArunPath": ["SILRUNE_OF_ARUN"],
    "QuoiruneOfSharaPath": ["QUOIRUNE_OF_SHARA"],
    "QuoiruneOfArunPath": ["QUOIRUNE_OF_ARUN"],
    "ArchruneOfSharaPath": ["ARCHRUNE_OF_SHARA"],
    "ArchruneOfArunPath": ["ARCHRUNE_OF_ARUN"],
    "KeyruneOfArunPath": ["KEYRUNE_OF_ARUN"],
}
BASE_VARIABLES = ["EVOLUTION_COST", "EVOLUTION_PROB"]

# ── Filters ─────────────────────────────────────────────────────────────────
VALID_TYPES = {
    "EQUIP_WEAPON", "EQUIP_ARMOR_BODY", "EQUIP_ARMOR_ARM", "EQUIP_ARMOR_LEG",
}

# ── Attributes to copy from source item → unlocked item ────────────────────
COPY_ATTRS = [
    "name", "combatItemType", "combatItemSubType", "category", "rank",
    "rareGrade", "level", "requiredLevel", "enchantEnable",
    "linkEnchantId", "linkPassivityCategoryId", "linkPassivityId",
    "requiredClass", "boundType", "tradable", "searchable",
    "warehouseStorable", "guildWarehouseStorable", "destroyable",
    "dismantlable", "storeSellable", "obtainable", "relocatable",
    "artisanable", "dropType", "buyPrice", "sellPrice",
    "linkLookInfoId", "icon", "dropSilhouette", "dropSound", "equipSound",
    "defaultValue", "itemLevelId", "linkMaterialEnchantId",
    "linkCrestId", "linkCustomizingId", "linkSkillId",
    "linkPetAdultId", "linkPetOrbId", "changeColorEnable",
    "changeLook", "extractLook", "changeEnchantFxId", "requiredGuildMaster",
    "requiredEquipmentType", "conversion", "sortingNumber",
    "divide", "itemUseCount", "maxDropUnit", "maxStack",
    "extractRatio", "unidentifiedItemGrade", "dropIdentify",
    "masterpieceRate", "slotLimit", "coolTimeGroup", "coolTime",
    "useOnlyTerritory", "combineOptionValue",
]

# ── Equipment attributes to copy (stats handled separately) ────────────────
EQUIP_COPY_ATTRS = [
    "level", "grade", "part", "type", "countOfSlot",
    "balance", "impactRate", "balanceRate",
]


# ═══════════════════════════════════════════════════════════════════════════
# XML Parsers
# ═══════════════════════════════════════════════════════════════════════════

def parse_items(datasheet: Path, ids: set[int]) -> dict[int, dict]:
    """Parse ItemTemplate.xml and return attributes for requested IDs."""
    items = {}
    tree = ET.parse(datasheet / "ItemTemplate.xml")
    for elem in tree.getroot():
        item_id = int(elem.get("id", "0"))
        if item_id in ids:
            items[item_id] = dict(elem.attrib)
    return items


def parse_equipment(datasheet: Path, ids: set[int]) -> dict[int, dict]:
    """Parse EquipmentTemplate.xml and return attributes for requested IDs."""
    equipment = {}
    tree = ET.parse(datasheet / "EquipmentTemplate.xml")
    for elem in tree.getroot():
        equip_id = int(elem.get("equipmentId", "0"))
        if equip_id in ids:
            equipment[equip_id] = dict(elem.attrib)
    return equipment


def parse_strings(datasheet: Path, ids: set[int]) -> dict[int, dict]:
    """Parse StrSheet_Item.xml and return string/toolTip for requested IDs."""
    strings = {}
    tree = ET.parse(datasheet / "StrSheet_Item.xml")
    for elem in tree.getroot():
        item_id = int(elem.get("id", "0"))
        if item_id in ids:
            strings[item_id] = {
                "name": elem.get("string", ""),
                "toolTip": elem.get("toolTip", ""),
            }
    return strings


# ═══════════════════════════════════════════════════════════════════════════
# CSV Reader
# ═══════════════════════════════════════════════════════════════════════════

def read_progression() -> list[dict]:
    """Read gear_progression.csv, filter by non-empty UnlockTo, sort by TemplateId."""
    rows = []
    with open(CSV_INPUT, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row.get("UnlockTo", "").strip():
                rows.append(row)
    rows.sort(key=lambda r: int(r["TemplateId"]))
    return rows


# ═══════════════════════════════════════════════════════════════════════════
# References Resolver
# ═══════════════════════════════════════════════════════════════════════════

def resolve_references() -> Path | None:
    """Try to resolve datasheet path from .references file."""
    ref_file = REFORGED_DIR / ".references"
    if not ref_file.exists():
        return None
    for line in ref_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        if key.strip() == "server_datasheet":
            return Path(val.strip())
    return None


# ═══════════════════════════════════════════════════════════════════════════
# YAML Formatting
# ═══════════════════════════════════════════════════════════════════════════

HINT_MARKER = "<font color = '#41FF3A'>[Potential Unlock]</font>"
UNLOCK_MARKER = "This gear's full potential has been unlocked"


def strip_appended_hints(tooltip: str) -> str:
    """Remove previously appended [Potential Unlock] / unlocked hints from tooltip."""
    for marker in (HINT_MARKER, UNLOCK_MARKER):
        idx = tooltip.find(marker)
        if idx != -1:
            # Walk back to strip leading $BR separators
            cut = idx
            while cut > 0 and tooltip[cut - 1 : cut] in ("R", "B", "$"):
                cut -= 1
            tooltip = tooltip[:cut]
    return tooltip


def format_attr_value(val: str) -> str:
    """Format a single XML attribute value for YAML output."""
    # Semicolon-delimited → YAML flow array
    if ";" in val:
        parts = [p.strip() for p in val.split(";") if p.strip()]
        return f"[{', '.join(parts)}]"
    # Boolean normalization
    if val in ("True", "true"):
        return "true"
    if val in ("False", "false"):
        return "false"
    # Numeric passthrough
    try:
        if "." in val:
            float(val)
        else:
            int(val)
        return val
    except ValueError:
        return val


# ═══════════════════════════════════════════════════════════════════════════
# Generators
# ═══════════════════════════════════════════════════════════════════════════

def generate_scroll_spec(
    entries: list[dict],
    strings_data: dict[int, dict],
) -> str:
    """Generate 11-potential-unlock-scroll.yaml content."""
    lines = [
        "# " + "=" * 75,
        "# Potential Unlock Scroll",
        "# " + "=" * 75,
        "#",
        "# TERA's evolution system only supports 1:1 paths — each item evolves to",
        "# exactly one successor. Flawless (Mythic) gear variants exist in the data",
        "# but are unreachable because evolution slots are already occupied by the",
        "# normal next-tier progression.",
        "#",
        "# The Potential Unlock Scroll introduces a branching choice:",
        "#   - Normal path: evolve to the next tier as usual",
        "#   - Unlock path: use this scroll to create a bridge item (\"Unlocked\")",
        "#     that can then evolve into the Flawless version",
        "#",
        "# Trade-off: unlocking consumes the scroll and the player forgoes the",
        "# normal next-tier evolution. The unlocked item keeps the same stats and",
        "# serves as the evolution source for the Flawless target.",
        "#",
        "# Mechanics:",
        "#   - Inheritance system (same as Frostfire tokens)",
        "#   - 10% success chance per attempt",
        "#   - Enchantment level is preserved on success",
        "#   - Evolution carries enchant step 1:1 (e.g. +9 -> +9)",
        "#   - Designed for reuse with future gear systems beyond Flawless",
        "#",
        "# Auto-generated by generate_potential_unlock.py — DO NOT EDIT MANUALLY",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "# " + "=" * 75,
        "# Scroll Item Definition",
        "# " + "=" * 75,
        "",
        "items:",
        "  upsert:",
        f"    - id: {SCROLL_ID}",
        "      name: generalMaterial",
        "      combatItemType: EQUIP_INHERITANCE",
        "      combatItemSubType: etc",
        "      category: etc",
        "      rank: 0",
        "      rareGrade: 3",
        "      level: 1",
        "      requiredLevel: 1",
        "      searchable: true",
        "      conversion: false",
        "      sortingNumber: 0",
        "      dropType: 2",
        "      buyPrice: 100000",
        "      sellPrice: 10000",
        "      divide: 0",
        "      maxStack: 10000",
        "      itemUseCount: 1",
        "      maxDropUnit: 9999",
        "      enchantEnable: false",
        "      tradable: false",
        "      boundType: None",
        "      destroyable: true",
        "      dismantlable: false",
        "      warehouseStorable: true",
        "      guildWarehouseStorable: false",
        "      storeSellable: true",
        "      obtainable: true",
        "      relocatable: true",
        "      artisanable: false",
        "      unidentifiedItemGrade: 0",
        "      masterpieceRate: 0",
        "      linkEquipmentId: 0",
        "      linkLookInfoId: 0",
        "      changeLook: false",
        "      extractLook: false",
        "      changeColorEnable: false",
        "      requiredGuildMaster: false",
        "      requiredEquipmentType: NO_COMBAT",
        "      linkCrestId: 0",
        "      linkCustomizingId: 0",
        "      linkSkillId: 0",
        "      linkPetAdultId: 0",
        "      linkPetOrbId: 0",
        "      icon: Icon_Items.q_scrollseal_Tex",
        # Visual/sound attributes copied from item 71 (Master Enigmatic Scroll)
        "      dropSilhouette: DropItem.SM.Item_Drop_Chest_SM",
        "      dropSound: InterfaceSound.Drop_ItemCUE.Drop_ChestBoxCue",
        "      usedSound: InterfaceSound.UseItem.UseItemCue",
        "      equipSound: InterfaceSound.Equip_ItemCUE.Equip_ScrollCue",
        "      defaultValue: 100000",
        "      strings:",
        '        name: "Potential Unlock Scroll"',
        "        toolTip: \"Use on eligible equipment to unlock its full potential."
        "$BR$BR<font color = '#41FF3A'>10% success chance.</font>"
        "$BRUnlocked gear gains access to an alternate upgrade path.\"",
        "",
        "# " + "=" * 75,
        "# Source Gear Hints",
        "# " + "=" * 75,
        "",
        "itemStrings:",
        "  update:",
    ]

    for entry in entries:
        source_id = entry["source_id"]
        s = strings_data.get(source_id, {})
        source_tooltip = strip_appended_hints(s.get("toolTip", ""))
        safe_tooltip = source_tooltip.replace('"', '\\"')
        hint = (
            f"{safe_tooltip}"
            "$BR"
            "<font color = '#41FF3A'>[Potential Unlock]</font>"
            "$BR"
            "Use a Potential Unlock Scroll to unlock this gear's full potential."
        )
        lines.append(f"    - id: {source_id}")
        lines.append("      changes:")
        lines.append(f'        toolTip: "{hint}"')

    lines.append("")
    lines.append("# " + "=" * 75)
    lines.append("# Inheritance Entry")
    lines.append("# " + "=" * 75)
    lines.append("")
    lines.append("equipmentInheritance:")
    lines.append("  upsert:")
    lines.append(f"    - templateId: {SCROLL_ID}")
    lines.append("      masterpiece: true")
    lines.append("      awaken: false")
    lines.append("      enchant: true")
    lines.append("      scroll: true")
    lines.append("      artifact: true")
    lines.append("      probability: 0.10")
    lines.append("      bound: true")
    lines.append("      inheritInfos:")

    for entry in entries:
        source_id = entry["source_id"]
        unlock_id = entry["unlock_id"]
        item_name = entry["item_name"]
        lines.append(
            f"        - {{ targetTemplateId: {source_id},"
            f" resultTemplateId: {unlock_id} }}"
            f"   # {item_name}"
        )

    lines.append("")
    return "\n".join(lines) + "\n"


def generate_gear_spec(
    entries: list[dict],
    items_data: dict[int, dict],
    equip_data: dict[int, dict],
    strings_data: dict[int, dict],
) -> str:
    """Generate 12-potential-unlock-gear.yaml content."""
    lines = [
        "# Potential Unlock Gear",
        "# Auto-generated by generate_potential_unlock.py",
        "# DO NOT EDIT MANUALLY",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "# " + "=" * 75,
        "# Unlocked Items (stats match source)",
        "# " + "=" * 75,
        "",
        "items:",
        "  upsert:",
    ]

    for entry in entries:
        source_id = entry["source_id"]
        unlock_id = entry["unlock_id"]
        unlock_equip_id = entry["unlock_equip_id"]
        item = items_data[source_id]
        s = strings_data.get(source_id, {})
        display_name = s.get("name", "")
        category = item.get("category", "")

        lines.append(f"    # --- Unlocked {display_name} ({category}) ---")
        lines.append(f"    - id: {unlock_id}")

        for attr in COPY_ATTRS:
            val = item.get(attr)
            if val is not None and val != "":
                lines.append(f"      {attr}: {format_attr_value(val)}")

        # Override linkEquipmentId → new boosted equipment
        lines.append(f"      linkEquipmentId: {unlock_equip_id}")

        # Inline strings — keep source set name, add unlock text
        unlocked_name = f"Unlocked {display_name}"
        source_tooltip = strip_appended_hints(s.get("toolTip", ""))
        safe_source_tooltip = source_tooltip.replace('"', '\\"')
        tooltip = (
            f"{safe_source_tooltip}"
            "$BR"
            "This gear's full potential has been unlocked, "
            "you can upgrade it after reaching +9 refinement."
        )
        lines.append("      strings:")
        lines.append(f'        name: "{unlocked_name}"')
        lines.append(f'        toolTip: "{tooltip}"')
        lines.append("")

    # ── Equipment section ────────────────────────────────────────────────
    lines.append("# " + "=" * 75)
    lines.append("# Unlocked Equipment (stats match source)")
    lines.append("# " + "=" * 75)
    lines.append("")
    lines.append("equipment:")
    lines.append("  upsert:")

    for entry in entries:
        source_id = entry["source_id"]
        unlock_equip_id = entry["unlock_equip_id"]
        item = items_data[source_id]
        base_equip_id = int(item["linkEquipmentId"])
        equip = equip_data[base_equip_id]
        s = strings_data.get(source_id, {})
        display_name = s.get("name", "")

        lines.append(f"    # Unlocked {display_name}")
        lines.append(f"    - equipmentId: {unlock_equip_id}")

        for attr in EQUIP_COPY_ATTRS:
            val = equip.get(attr, "")
            if val:
                lines.append(f"      {attr}: {val}")

        # Stats copied 1:1 from source
        min_atk = int(equip.get("minAtk", "0"))
        max_atk = int(equip.get("maxAtk", "0"))
        impact = int(equip.get("impact", "0"))
        defense = int(equip.get("def", "0"))

        lines.append(f"      minAtk: {min_atk}")
        lines.append(f"      maxAtk: {max_atk}")
        lines.append(f"      impact: {impact}")
        lines.append(f"      def: {defense}")
        lines.append("      atkRate: 1")
        lines.append("      defRate: 1")
        lines.append("")

    return "\n".join(lines) + "\n"


def generate_evolution_spec(entries: list[dict]) -> str:
    """Generate 13-potential-unlock-evolution.yaml content."""
    # Collect unique path definitions needed
    paths_needed = sorted({e["path_def"] for e in entries})

    # Collect required variables from path definitions
    vars_needed = set(BASE_VARIABLES)
    for path in paths_needed:
        vars_needed.update(PATH_TO_VARIABLES.get(path, []))
    sorted_vars = sorted(vars_needed)

    # 1:1 enchant step mapping (source step = result step)
    enchant_steps = [9, 10, 11, 12]

    lines = [
        "# Potential Unlock Evolution Paths",
        "# Auto-generated by generate_potential_unlock.py",
        "# DO NOT EDIT MANUALLY",
        "#",
        "# Evolves Unlocked gear -> Flawless gear with 1:1 enchant carry",
        "# (e.g. +9 -> +9, +10 -> +10, +11 -> +11, +12 -> +12).",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "imports:",
        "  - from: evolution-base",
        "    use:",
        "      variables:",
    ]

    for var in sorted_vars:
        lines.append(f"        - {var}")

    lines.append("      definitions:")

    for path in paths_needed:
        lines.append(f"        - {path}")

    lines.append("")
    lines.append("# " + "=" * 75)
    lines.append("# Unlocked -> Flawless Evolution Paths (1:1 enchant carry)")
    lines.append("# " + "=" * 75)
    lines.append("")
    lines.append("evolutionPaths:")
    lines.append("  upsert:")

    for entry in entries:
        unlock_id = entry["unlock_id"]
        flawless_id = entry["flawless_id"]
        path_def = entry["path_def"]
        item_name = entry["item_name"]
        lines.append(f"    - targetTemplateId: {unlock_id}   # {item_name}")
        lines.append("      paths:")
        for step in enchant_steps:
            lines.append(f"        - $extends: {path_def}")
            lines.append(f"          targetEnchantStep: {step}")
            lines.append(f"          resultTemplateId: {flawless_id}")
            lines.append(f"          resultEnchantStep: {step}")

    lines.append("")
    return "\n".join(lines) + "\n"


def generate_tracking_csv(entries: list[dict]) -> str:
    """Generate potential_unlock_progression.csv content."""
    header = (
        "SourceId;UnlockedId;FlawlessId;ItemName;ItemString;"
        "Level;CombatItemType;Gear;Material;Amount"
    )
    lines = [header]

    for entry in entries:
        lines.append(
            f"{entry['source_id']};{entry['unlock_id']};{entry['flawless_id']};"
            f"{entry['item_name']};{entry['item_string']};{entry['level']};"
            f"{entry['combat_type']};{entry['gear']};{entry['material']};"
            f"{entry['amount']}"
        )

    return "\n".join(lines) + "\n"


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Generate potential unlock system specs"
    )
    parser.add_argument(
        "--datasheet",
        help="Path to server Datasheet directory (default: from .references)",
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Write output files to disk (default: dry-run with summary)",
    )
    args = parser.parse_args()

    # Resolve datasheet path
    if args.datasheet:
        datasheet = Path(args.datasheet)
    else:
        datasheet = resolve_references()
        if not datasheet:
            parser.error("No --datasheet provided and .references not found")

    if not datasheet.exists():
        parser.error(f"Datasheet directory not found: {datasheet}")

    # ── Step 1: Read CSV ─────────────────────────────────────────────────
    print("Reading gear progression (UnlockTo column)...")
    progression = read_progression()
    print(f"  Found {len(progression)} items with UnlockTo mapping")

    # ── Step 2: Parse XMLs ───────────────────────────────────────────────
    print(f"Parsing datasheets from: {datasheet}")
    source_ids = {int(r["TemplateId"]) for r in progression}

    items_data = parse_items(datasheet, source_ids)
    strings_data = parse_strings(datasheet, source_ids)

    # Filter to items found in both XML sources
    found_ids = set(items_data.keys()) & set(strings_data.keys())
    skipped = source_ids - found_ids
    if skipped:
        print(
            f"  WARNING: Skipped {len(skipped)} items not found in XMLs: "
            f"{sorted(skipped)[:10]}"
        )
        progression = [
            r for r in progression if int(r["TemplateId"]) in found_ids
        ]

    # Collect equipment IDs from found items
    equip_ids = set()
    for row in progression:
        sid = int(row["TemplateId"])
        equip_ids.add(int(items_data[sid]["linkEquipmentId"]))
    equip_data = parse_equipment(datasheet, equip_ids)

    print(
        f"  Items: {len(items_data)}, Equipment: {len(equip_data)}, "
        f"Strings: {len(strings_data)}"
    )

    # ── Step 3: Build entries ────────────────────────────────────────────
    entries = []
    for idx, row in enumerate(progression):
        source_id = int(row["TemplateId"])
        unlock_id = UNLOCK_ID_SEED + idx
        flawless_id = int(row["UnlockTo"])
        material = int(row["Material_1"])
        amount = int(row["Amount_1"])
        path_def = MATERIAL_TO_PATH.get(material)

        if not path_def:
            print(
                f"  WARNING: Unknown material {material} for item {source_id},"
                f" skipping"
            )
            continue

        entries.append({
            "source_id": source_id,
            "unlock_id": unlock_id,
            "unlock_equip_id": UNLOCK_EQUIP_BASE + unlock_id,
            "flawless_id": flawless_id,
            "item_name": row["ItemName"],
            "item_string": row["ItemString"],
            "level": row["Level"],
            "combat_type": row["CombatItemType"],
            "gear": row["Gear"],
            "material": material,
            "amount": amount,
            "path_def": path_def,
        })

    # ── Step 4: Generate outputs ─────────────────────────────────────────
    scroll_yaml = generate_scroll_spec(entries, strings_data)
    gear_yaml = generate_gear_spec(entries, items_data, equip_data, strings_data)
    evolution_yaml = generate_evolution_spec(entries)
    tracking_csv = generate_tracking_csv(entries)

    if args.write:
        SCROLL_SPEC.parent.mkdir(parents=True, exist_ok=True)
        CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

        for path, content in [
            (SCROLL_SPEC, scroll_yaml),
            (GEAR_SPEC, gear_yaml),
            (EVOLUTION_SPEC, evolution_yaml),
            (CSV_OUTPUT, tracking_csv),
        ]:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"\nWritten: {path}")
    else:
        print("\nDry run — use --write to save files")

    # ── Summary ──────────────────────────────────────────────────────────
    unlock_last = UNLOCK_ID_SEED + len(entries) - 1
    print(f"\nSummary:")
    print(f"  Items:     {len(entries)} (IDs {UNLOCK_ID_SEED} – {unlock_last})")
    print(
        f"  Equipment: {len(entries)} (IDs {UNLOCK_EQUIP_BASE + UNLOCK_ID_SEED}"
        f" – {UNLOCK_EQUIP_BASE + unlock_last})"
    )
    print(f"  Evolution: {len(entries)} paths")
    print(f"  Scroll:    ID {SCROLL_ID} with {len(entries)} inheritance mappings")

    paths = sorted({e["path_def"] for e in entries})
    print(f"  Paths:     {', '.join(paths)}")


if __name__ == "__main__":
    main()
