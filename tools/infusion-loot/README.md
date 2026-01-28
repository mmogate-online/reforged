# Infusion Loot Generator

Generates CCompensation YAML specs for distributing infusion fodder items across hunting zones.

## Overview

This tool creates loot tables that distribute infusion fodder based on content tier (Leveling, EarlyEndgame, Endgame). Each tier has different drop rates for Uncommon/Rare/Superior grade items.

## Quick Start

```bash
# 1. Configure drop rates (optional)
# Edit: reforged/data/infusion_loot/loot_tier_rates.csv

# 2. Configure zones
# Edit: reforged/data/infusion_loot/zone_loot_config.csv

# 3. Generate YAML spec
python reforged/tools/infusion-loot/generate_infusion_loot.py

# 4. Apply to server
dsl apply "reforged\specs\infusion-loot.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"
```

## Input Files

### `loot_tier_rates.csv`

Drop rate profiles per content tier.

```csv
Tier;Uncommon;Rare;Superior
Leveling;0.1;0.01;0.001
EarlyEndgame;0.05;0.05;0.01
Endgame;0;0.02;0.05
```

| Column | Description |
|--------|-------------|
| Tier | Content tier name (used in definitions) |
| Uncommon | Base drop rate for Uncommon grade (0.1 = 10%) |
| Rare | Base drop rate for Rare grade |
| Superior | Base drop rate for Superior grade |

**Note:** Rates are divided by 4 (one per equipment slot) in the generated spec.

### `zone_loot_config.csv`

Zone assignments to content tiers.

```csv
Tier;HuntingZoneId;NpcTemplateIds
Leveling;2;3,4,5,6,7
EarlyEndgame;9001;3001,3002,3003
```

| Column | Description |
|--------|-------------|
| Tier | Must match a tier name from loot_tier_rates.csv |
| HuntingZoneId | The hunting zone ID |
| NpcTemplateIds | Comma-separated list of NPC template IDs |

**Note:** Lines starting with `#` after the header are treated as comments.

## Output Structure

The generator creates `infusion-loot.yaml` with:

### Definitions (per tier)

```yaml
definitions:
  loot_Leveling:
    itemBags:
      # 4 slots × N grades = up to 12 ItemBags
      - probability: 0.025  # 10% / 4 slots
        distribution: auto  # Equal probability for all items
        items:
          - templateId: 990000
            name: "Infusion Weapon of Fury"
          - templateId: 990003
            name: "Infusion Weapon of Dominance"
          # ... more items (auto-distributed)
```

**DSL Features Used:**
- `distribution: auto` - DSL auto-calculates item probabilities (1/n with remainder distribution)
- Default `min`/`max` - Omitted values default to 1

### CCompensations (per zone)

```yaml
cCompensations:
  upsert:
    - huntingZoneId: 2
      npcTemplateId: [3, 4, 5, 6, 7]  # ID list expansion
      npcName: ""
      $extends: loot_Leveling
```

## Loot Structure

Each tier definition contains ItemBags organized by slot and grade:

| Slot | Items | Grade | Bag Probability (Leveling) |
|------|-------|-------|----------------------------|
| Weapon | 15 | Uncommon | 2.5% (10%/4) |
| Weapon | 15 | Rare | 0.25% (1%/4) |
| Weapon | 15 | Superior | 0.025% (0.1%/4) |
| Chest | 18 | Uncommon | 2.5% |
| Chest | 18 | Rare | 0.25% |
| Chest | 18 | Superior | 0.025% |
| Gloves | 10 | Uncommon | 2.5% |
| Gloves | 10 | Rare | 0.25% |
| Gloves | 10 | Superior | 0.025% |
| Boots | 7 | Uncommon | 2.5% |
| Boots | 7 | Rare | 0.25% |
| Boots | 7 | Superior | 0.025% |

Item probabilities within bags are auto-distributed by DSL (sum exactly 1.0, first item gets remainder).

## DSL Features Used

- **Definitions**: Reusable loot table templates
- **$extends**: Inherit tier definitions in zone entries
- **ID List Expansion**: `npcTemplateId: [id1, id2, ...]` expands to multiple entries
- **Auto Distribution**: `distribution: auto` auto-calculates item probabilities
- **Default min/max**: Omitted `min`/`max` values default to 1

## Customization

### Adding new tiers

1. Add row to `loot_tier_rates.csv`
2. Reference the tier name in `zone_loot_config.csv`

### Adjusting slot weights

Currently all slots have equal weight (rate/4). To adjust, modify the `slot_rate` calculation in `generate_infusion_loot.py`.

### Adding new zones

Simply add rows to `zone_loot_config.csv` with the appropriate tier and NPC IDs.
