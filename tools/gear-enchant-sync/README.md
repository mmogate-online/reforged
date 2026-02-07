# Gear Enchant Sync Tool

Generates a DSL spec that bulk-updates all equipment items to use the correct `linkEnchantId` values using `updateWhere` filters and imported variables from the `enchant-standard` package.

## Purpose

Ensures all Grade 3 (Superior) and Grade 4 (Mythic) equipment items reference the correct enchant definitions for their tier and slot type.

## Usage

```bash
cd reforged/tools/gear-enchant-sync

# Default output (specs/gear-enchant-sync.yaml)
python generate_spec.py

# Patch-specific output (specs/patches/{patch}/04-gear-enchant-sync.yaml)
python generate_spec.py --patch 001
```

## How It Works

The generated spec uses `updateWhere` with filters by `enchantEnable`, `rareGrade`, and `category` instead of individual upserts. This ensures only enchantable gear is matched. The spec produces 14 concise rules that cover all combinations of:

- **Tiers**: Mythic (rareGrade=4), Superior (rareGrade=3)
- **Slots**: Weapons (healer vs DPS/Tank), Body, Hand (by armor type), Feet

The enchant IDs are imported as variables from `enchant-standard` package:

| Variable | Enchant ID | Usage |
|----------|------------|-------|
| `ENCHANT_HIGH_TIER_WEAPON_HEALER` | 12304 | Mythic staff, rod |
| `ENCHANT_HIGH_TIER_WEAPON_DPS_TANK` | 12302 | Mythic dual, lance, etc. |
| `ENCHANT_HIGH_TIER_CHEST` | 20336 | Mythic body armor |
| `ENCHANT_HIGH_TIER_HAND_MAIL` | 20500 | Mythic handMail |
| `ENCHANT_HIGH_TIER_HAND_LEATHER` | 20501 | Mythic handLeather |
| `ENCHANT_HIGH_TIER_HAND_ROBE` | 20502 | Mythic handRobe |
| `ENCHANT_HIGH_TIER_BOOTS` | 20339 | Mythic feet armor |
| `ENCHANT_MID_TIER_WEAPON_HEALER` | 12303 | Superior staff, rod |
| `ENCHANT_MID_TIER_WEAPON_DPS_TANK` | 12301 | Superior dual, lance, etc. |
| `ENCHANT_MID_TIER_CHEST` | 20328 | Superior body armor |
| `ENCHANT_MID_TIER_HAND_MAIL` | 20510 | Superior handMail |
| `ENCHANT_MID_TIER_HAND_LEATHER` | 20511 | Superior handLeather |
| `ENCHANT_MID_TIER_HAND_ROBE` | 20512 | Superior handRobe |
| `ENCHANT_MID_TIER_BOOTS` | 20331 | Superior feet armor |

## After Generation

1. Validate the spec:
   ```bash
   dsl validate <output_file> --path "<server_datasheet>"
   ```

2. Apply to server datasheets:
   ```bash
   dsl apply <output_file> --path "<server_datasheet>"
   ```

Replace `<server_datasheet>` with the path from `.references`.
