# Packages Index

Packages are reusable DSL modules shared across patches. They define the foundations — ID registries, system definitions, and parameterized templates — that keep specs consistent without duplicating logic.

All packages must be registered in `datasheetlang.yml` under `workspace.packages` to be importable by name.

---

## Package Types

**System packages** define the rules and structures for a game system. They are imported once per system and should not need to change between patches unless the system itself changes.

**ID registry packages** export named lists of item IDs. Specs import whichever lists they need to apply bulk operations. These grow over time as new gear sets, crystals, or items are added to the game.

**Template packages** export parameterized DSL definition templates. They allow specs to express repetitive structures (like evolution paths) as a single parameterized entry instead of duplicating the full definition for each item.

---

## All Packages

### Enchant System (dependency chain)

These four packages form a strict dependency chain. See `enchant-standard/README.md` for the full picture.

| Package | Type | Description | README |
|---------|------|-------------|--------|
| `enchant-passives` | System | Individual passivity stat definitions (38 definitions). Internal dependency only — never imported directly by specs. | — |
| `enchant-categories` | System | Groups passivities into roll pools per slot/role (19 category IDs + 19 category bundle definitions). Internal dependency of `enchant-standard`. | — |
| `enchant-standard` | System | Full enchant chain definitions: enchant IDs, stat rates, and tier/slot enchant records. The practical entry point for specs. | `enchant-standard/README.md` |
| `equipment-item-standard` | System | Item-level templates that bundle `enchantEnable`, `rareGrade`, and `linkEnchantId` per tier/slot. Built but not yet used by any spec — reserved for future use. | — |

### ID Registries

| Package | Type | Description | README |
|---------|------|-------------|--------|
| `equipment-item-ids` | ID Registry | All gear item IDs in the progression pipeline, grouped by tier (LOW/MID/HIGH) and slot. The source of truth for gear standardization. | `equipment-item-ids/README.md` |
| `flawless-gear-ids` | ID Registry | Flawless-grade item IDs (subset of HIGH_TIER): weapons, body, hands, feet, and a combined `FLAWLESS_ALL_IDS`. Used by the flawless standardization spec. | — |
| `chest-toproll-categories` | ID Registry | Per-class chest armor passivity category IDs (122001–122013) and their category definitions. Used by the chest top-roll system specs. | — |
| `crystals` | ID Registry | All crystal item IDs (Common/Fine weapon, armor, accessory), fusion structure IDs, dyad crystal IDs, and gacha box IDs. Split across 11 sub-files. | `crystals/README.md` |
| `dungeon-tokens` | ID Registry | Token, menu, and list item IDs for Bastion of Lok and Sinestral Manor. | — |
| `gear-infusion-boxes` | ID Registry | Infusion fodder gacha box IDs by slot and rarity (12 IDs total). | — |

### Templates

| Package | Type | Description | README |
|---------|------|-------------|--------|
| `evolution-base` | Template | Rune material IDs, evolution path definitions per rune tier, and the `EvolutionItem` parameterized template. Used by all gear evolution specs. | `evolution-base/README.md` |

---

## Adding a New Package

1. Create a folder under `packages/<name>/` with an `index.yml`
2. Register it in `datasheetlang.yml` under `workspace.packages`
3. Add an entry to this index

Without step 2, DSL will fail with `Unknown package reference` when specs try to import from it.
