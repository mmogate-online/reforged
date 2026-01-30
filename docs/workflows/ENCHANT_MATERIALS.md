# Enchant Materials Workflow

## Overview

The enchant materials system controls enchantment probabilities, alkahest costs, and feedstock costs for equipment upgrades. Data is maintained in an Excel spreadsheet and converted into DSL specs that update server datasheets.

## Data File

**Location**: `reforged/data/enchant.xlsx`

### Sheets

| Sheet | Content |
|-------|---------|
| Chance | Success probability per enchant step and level range |
| Alkahest WeC | Alkahest cost for Weapons & Chest armor |
| Alkahest GeB | Alkahest cost for Gloves & Boots |
| Feedstock WeC | Feedstock cost for Weapons & Chest armor |
| Feedstock GeB | Feedstock cost for Gloves & Boots |

### Column Layout (all sheets)

- **Column A**: Enchant step (0–14, corresponding to +0 through +14)
- **Columns B+**: Level ranges: `1 ~37`, `38 ~49`, `50 ~57`, `58`

### Editing

- Open `reforged/data/enchant.xlsx` in Excel or LibreOffice Calc
- Edit values in any sheet — probabilities are decimals (e.g., `0.85` = 85%)
- Material amounts are integers
- Save and close the file before generating

## Entities Affected

| Entity | Server File | Description |
|--------|------------|-------------|
| MaterialEnchantData | `MaterialEnchantData.xml` | Enchant step definitions (probs, materials) |
| ItemData | `ItemTemplate*.xml` | Links items to their materialEnchantId |

## One-Click Deploy

Double-click `reforged/tools/enchant-materials/deploy.bat`

This runs the full pipeline:
1. Generates YAML specs from `enchant.xlsx`
2. Applies `enchant-materials.yaml` → MaterialEnchantData
3. Applies `enchant-item-links.yaml` → ItemData
4. Syncs MaterialEnchantData and ItemData to client DataCenter

After deploy, run `pack-client.bat` from the project root to pack the client.

## Manual Steps

```bash
# 1. Generate specs
cd reforged/tools/enchant-materials
python generate_enchant_materials.py

# 2. Apply to server (from project root)
dsl apply "reforged\specs\enchant-materials.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"
dsl apply "reforged\specs\enchant-item-links.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"

# 3. Sync affected entities to client
dsl sync --config reforged\config\sync-config.yaml -e MaterialEnchantData -e ItemData

# 4. Pack client
pack-client.bat
```

## Verifying Changes

- After apply, check `MaterialEnchantData.xml` in the server Datasheet folder for updated values
- After sync, check `MaterialEnchantData/MaterialEnchantData-00000.xml` in the client DataCenter folder
- Item links can be verified by searching for `linkMaterialEnchantId` in `ItemTemplate.xml`

## Generated Specs

| File | Content |
|------|---------|
| `reforged/specs/enchant-materials.yaml` | MaterialEnchantData upserts with probabilities and material costs |
| `reforged/specs/enchant-item-links.yaml` | ItemData updateWhere rules linking items to materialEnchantIds |
