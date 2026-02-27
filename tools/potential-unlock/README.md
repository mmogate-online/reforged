# Potential Unlock System

Tool for generating YAML specs that enable Flawless gear access through a branching upgrade path.

## Problem

TERA's evolution system only supports 1:1 paths — each item evolves to exactly one successor. Flawless (Mythic) gear variants exist in the data but are unreachable because evolution slots are already occupied by the normal next-tier progression.

## Solution

The **Potential Unlock Scroll** introduces a branching choice at eligible tiers:

```
                           ┌──── Normal Evolution ────► Next Tier
Eligible Gear (+9) ────────┤
                           └──── Unlock Scroll ──────► Unlocked Gear (+9) ──── Evolution ────► Flawless Gear
                                  (10% chance)            (same stats)           (+9 → +9)
```

### Trade-off

Players choose between:
- **Normal path**: evolve to the next tier as usual (guaranteed, standard progression)
- **Unlock path**: use the scroll to create a bridge item ("Unlocked") that can then evolve into the Flawless version (10% success chance, irreversible once unlocked)

The unlocked item has identical stats to the source and serves as the evolution source for the Flawless target. It cannot evolve to the normal next tier.

## Eligible Tiers

63 items across 6 gear sets (Level ≤ 57, excluding Frostfire):

| Tier | Level | Slots | Evolution Material |
|------|-------|-------|--------------------|
| Bastion | 22 | 12 weapons + 3 feet | Silrune of Shara / Arun |
| Demonia | 27 | 3 body + 3 hands | Silrune of Arun |
| Covenant | 38 | 12 weapons + 3 feet | Quoirune of Shara / Arun |
| Sepulchral | 44 | 3 body + 3 hands | Archrune of Arun |
| Starter 6 | 50 | 12 weapons + 3 feet | Archrune of Shara / Arun |
| Counterglow | 55 | 3 body + 3 hands | Keyrune of Arun |

Eligibility is driven by the `UnlockTo` column in `gear_progression.csv`. To add new tiers, populate that column with the target Flawless TemplateId.

## Mechanics

- **Inheritance system**: same mechanism as Frostfire tokens (item 90 acts as EQUIP_INHERITANCE)
- **10% success chance**: on failure, the scroll is consumed and the item remains unchanged
- **Enchant preserved**: on success, the source item's enchantment transfers to the unlocked item
- **Evolution unlock**: once unlocked, the item gains a 4-step evolution path to its Flawless version with 1:1 enchant carry (+9→+9, +10→+10, +11→+11, +12→+12)

## Quick Start

```bash
# 1. Generate YAML specs + tracking CSV
python reforged/tools/potential-unlock/generate_potential_unlock.py --write

# 2. Apply all patch specs and sync via the migration tool
python reforged/tools/migrate/migrate.py --patch 001
```

The generator must run against **post-patch** server XMLs (after specs 00–09 are applied), because earlier specs modify `linkEnchantId` and `linkPassivityCategoryId` on source items. Reading vanilla XMLs would bake in stale values and cause server validation failures.

Recommended workflow when regenerating:
1. Ensure server XMLs already have specs 00–09 applied (or run a full migration first)
2. Run the generator with `--write`
3. Revert server + client datasheets to vanilla
4. Run the migration tool to apply all specs cleanly

## Data Flow

```
gear_progression.csv   ──┐
ItemTemplate.xml       ──┼──► generate_potential_unlock.py
EquipmentTemplate.xml  ──┤    ├──► 11-potential-unlock-scroll.yaml    (scroll + inheritance)
StrSheet_Item.xml      ──┘    ├──► 12-potential-unlock-gear.yaml      (63 items + equipment)
                              ├──► 13-potential-unlock-evolution.yaml  (63 evolution paths)
                              └──► potential_unlock_progression.csv    (tracking)
```

## File Structure

```
reforged/
├── data/
│   ├── gear_progression.csv              # Source data (UnlockTo column)
│   └── potential_unlock_progression.csv  # Generated tracking CSV
├── packages/
│   └── evolution-base/                   # Shared evolution path definitions
├── specs/
│   └── patches/001/
│       ├── 11-potential-unlock-scroll.yaml
│       ├── 12-potential-unlock-gear.yaml
│       └── 13-potential-unlock-evolution.yaml
└── tools/
    └── potential-unlock/
        ├── generate_potential_unlock.py
        └── README.md
```

## Generated Output

### Spec 11 — Scroll Item + Inheritance

Defines the Potential Unlock Scroll (ID 90), appends `[Potential Unlock]` tooltip hints to all 63 source items via `itemStrings: update:`, and a single `equipmentInheritance` entry with all 63 source→unlocked mappings.

### Spec 12 — Unlocked Gear

63 items (IDs 280000+) cloned from source with:
- Stats matching source 1:1 (no boost)
- `linkEnchantId` and `linkPassivityCategoryId` matching source (critical for server stability)
- "Unlocked" name prefix
- Dedicated equipment entries (IDs 900280000+)

### Spec 13 — Evolution Paths

63 evolution paths with 1:1 enchant carry (+9→+9, +10→+10, +11→+11, +12→+12). Each path extends the appropriate material path definition from `evolution-base` (e.g. `SilruneOfSharaPath`) with rune material x2.

## ID Ranges

| Entity | ID Range |
|--------|----------|
| Scroll | 90 |
| Unlocked Items | 280000 – 280062 |
| Unlocked Equipment | 900280000 – 900280062 |

## Key Constraints

- `linkEnchantId` and `linkPassivityCategoryId` **must** match between source and unlocked item (server crash otherwise)
- `requiredClass` must be a YAML array for multi-class items
- Inline `strings:` block on `items: upsert:` entries (not standalone `itemStrings:`)
- Evolution paths use per-material `$extends` (e.g. `SilruneOfSharaPath`) from `evolution-base` package with required variable imports
- All evolution materials are single-material x2

## Extending the System

### Adding New Tiers

1. Populate the `UnlockTo` column in `gear_progression.csv` for the new source items (value = Flawless TemplateId)
2. Ensure the source item's `Material_1` maps to a known path in `MATERIAL_TO_PATH` (add new entries if needed)
3. Re-run the generator with `--write`
4. Apply and sync

### Adjusting Success Rate

Edit the `probability` value in `generate_scroll_spec()` (currently `0.10` = 10%).

## Idempotency

The generator reads tooltips from the live server XML. To avoid stacking hints on repeated runs, `strip_appended_hints()` detects and removes any previously appended `[Potential Unlock]` or unlocked gear markers before re-appending them. This makes regeneration safe regardless of server XML state.
