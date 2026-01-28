# Gear Infusion System

Tool for generating YAML specs for the tiered gear infusion passive system.

## Overview

The infusion system allows players to bind passive effects to their equipment using infusion fodder items. Fodder gear drops from content (mobs, BAMs, dungeons) with a single passive attribute. Players can either dismantle fodder for feedstock or use it to infuse the passive into their own gear.

### Grade Tiers

| Grade | Color | Power Level |
|-------|-------|-------------|
| Uncommon | Green | ~25% of Superior |
| Rare | Blue | ~50% of Superior |
| Superior | Yellow | 100% (reference) |

### Equipment Slots

- Weapon (17 passives)
- Chest Armor (18 passives)
- Gloves (10 passives)
- Boots (7 passives)

Total: **50 unique passives × 3 tiers = 150 passivities and items**

## Quick Start

```bash
# 1. Edit CSV data (optional)
# Open: reforged/data/gear_infusion_passivity.csv

# 2. Generate YAML specs
python reforged/tools/gear-infusion/generate_infusion.py

# 3. Apply to server datasheet
dsl apply "reforged\specs\gear-infusion-passivities.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"
dsl apply "reforged\specs\gear-infusion-items.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"
```

## File Structure

```
reforged/
├── data/
│   └── gear_infusion_passivity.csv    # Source data (edit this)
├── specs/
│   ├── gear-infusion-passivities.yaml # Generated passivities + strings
│   └── gear-infusion-items.yaml       # Generated fodder items + strings
└── tools/
    └── gear-infusion/
        ├── generate_infusion.py       # Generator script
        └── README.md                  # This file
```

## CSV Format Reference

File: `reforged/data/gear_infusion_passivity.csv`

| Column | Description | Example |
|--------|-------------|---------|
| Order | Unique row number (1-50) | `1` |
| CombatItemType | Target slot | `EQUIP_WEAPON`, `EQUIP_ARMOR_BODY`, `EQUIP_ARMOR_ARM`, `EQUIP_ARMOR_LEG` |
| Role | Class restriction | `ANY`, `TANK`, `HEALER` |
| PassiveAttribute | Internal attribute name | `DamageVsEnraged`, `CritFactor` |
| Type | Engine passivity type | `152` (offense), `102` (defense), `6` (crit factor) |
| Uncommon | Tier 1 value | `0.008` (0.8%), `4` (flat) |
| Rare | Tier 2 value | `0.015` (1.5%), `8` (flat) |
| Superior | Tier 3 value | `0.03` (3%), `16` (flat) |
| Suffix | Item name suffix | `of Fury`, `of Precision` |
| Tooltip | Effect description with `$value` placeholder | `Increases damage by $value%.` |
| MobSize | Target filter (optional) | `all`, `any`, empty |
| Condition | Activation context (for reference) | `Enraged`, `Always` |

### Value Conventions

- **Percentages**: Stored as decimals (`0.03` = 3%)
- **Flat values**: Stored as-is (`16` = +16)
- **Reductions**: Same as percentages, script inverts internally

### Adding Comments

Lines starting with `#` in the Order column are treated as comments:
```csv
# Weapon Infusions (17)
1;EQUIP_WEAPON;ANY;DamageVsEnraged;...
```

## Passivity Engine Configuration

The script maps `PassiveAttribute` names to engine properties in `PASSIVITY_CONFIG`:

```python
"DamageVsEnraged": {
    "kind": 0,           # Always 0 for equipment passives
    "type": 152,         # 152 = offensive damage
    "method": 3,         # 3 = multiply (boost)
    "condition": 28,     # 28 = enraged trigger
    "conditionValue": 1,
    "is_percent": True,
    "value_offset": 1.0, # Boost: value becomes 1.0 + csv_value
},
```

### Common Type Codes

| Type | Purpose |
|------|---------|
| 152 | Offensive damage (% boost) |
| 102 | Defensive damage (% reduction) |
| 6 | Crit factor (flat) |
| 7 | Crit resist factor (flat) |
| 19 | Crit power (flat) |
| 25 | Attack speed (%) |
| 5 | Movement speed (%) |
| 1 | Max HP (flat or %) |
| 3 | Power (flat) |
| 4 | Endurance (flat) |
| 71 | Cooldown reduction (%) |
| 164 | Aggro generation (%) |
| 168 | Healing skill flat |
| 169 | Healing skill % |

### Common Method Codes

| Method | Purpose |
|--------|---------|
| 1 | Add (flat values) |
| 2 | Multiply reduction (1 - value) |
| 3 | Multiply boost (1 + value) |

### Common Condition Codes

| Condition | Trigger |
|-----------|---------|
| 1 | Always active |
| 17 | Rear attack (positional) |
| 18 | Frontal attack |
| 25 | Generic monster (on attack) |
| 26 | Target knockdown |
| 28 | Enraged status |
| 32 | Max aggro holder |

## ID Ranges

| Entity | ID Range |
|--------|----------|
| Passivities | 9000000 - 9000149 |
| Items | 990000 - 990149 |

IDs are assigned sequentially: each CSV row generates 3 IDs (one per tier).

## Generated Output

### Passivities YAML

```yaml
passivities:
  upsert:
    - category: Equipment
      id: 9000000
      name: "TIER1_WPN_DamageVsEnraged"
      kind: 0
      type: 152
      method: 3
      condition: 28
      conditionValue: 1
      value: 1.008    # 1.0 + 0.008 = 0.8% boost
      prob: 1.0
      mobSize: "all"

passivityStrings:
  upsert:
    - id: 9000000
      name: "TIER1_WPN_DamageVsEnraged"
      tooltip: "Increases damage against enraged enemies by 0.8%."
```

### Items YAML

```yaml
definitions:
  infusionItemBase:
    maxStack: 1
    tradable: false
    boundType: Loot
    # ... common properties

  infusionItemUncommon:
    $extends: infusionItemBase
    rareGrade: Uncommon
    icon: 'Icon_Items.Item_InfusionCore_Green_Tex'

items:
  upsert:
    - $extends: infusionItemUncommon
      id: 990000
      name: "infusion_wpn_damagevsenraged_t1"
      combatItemType: ENCHANT_MATERIAL
      linkPassivityId:
        - "9000000"
      strings:
        name: "Infusion Weapon of Fury"
        toolTip: "Infusion Core. Increases damage against enraged enemies by 0.8%. Use on weapon to apply this effect."
```

## Workflow: Updating Passives

### 1. Modify Values

Edit `reforged/data/gear_infusion_passivity.csv` in Excel or text editor.

Example: Increase Superior tier damage for enraged enemies from 3% to 3.5%:
```csv
1;EQUIP_WEAPON;ANY;DamageVsEnraged;152;0.008;0.015;0.035;of Fury;...
```

### 2. Add New Passive

Add a new row with the next Order number:
```csv
51;EQUIP_WEAPON;ANY;NewAttribute;TYPE;0.01;0.02;0.04;of Newness;Description with $value%.;;Always
```

If the attribute is new, also add its configuration to `PASSIVITY_CONFIG` in the Python script.

### 3. Regenerate Specs

```bash
python reforged/tools/gear-infusion/generate_infusion.py
```

### 4. Apply to Server

```bash
dsl apply "reforged\specs\gear-infusion-passivities.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"
dsl apply "reforged\specs\gear-infusion-items.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"
```

### 5. Sync to Client (if needed)

```bash
dsl client-sync --config reforged\config\sync-config.yaml
```

## Design Documentation

For detailed design rationale, scaling formulas, and passivity tables see:
- `D:\dev\mmogate\github\server-director\docs\workflows\GEAR_INFUSION_SYSTEM.md`

## Legacy Reference

The original C# implementation in `huntingzone-editor` used:
- `PassivityGenerator.cs` - Main generator logic
- `PassiveFactory.cs` - Factory pattern for passivity creation
- `ItemDataFactory.cs` - Item object creation

Key differences from DSL approach:
1. Generated XML directly vs YAML specs
2. Created per-class weapon items (13 items per passive) vs slot-generic items
3. Manual XML manipulation vs declarative DSL transforms
4. Hardcoded ID seeds vs configurable ranges
