# crystals Package

Exports item IDs for all crystals, fusion structures, dyad crystals, and crystal gacha boxes. Spread across 11 sub-files aggregated by `index.yml`.

## Sub-files

| File | Contents |
|------|---------|
| `common-weapon.yml` | Common weapon crystals — 7 tiers × 20 effects |
| `common-armor.yml` | Common armor crystals — 7 tiers × 11 effects |
| `fine-weapon.yml` | Fine weapon crystals — 7 tiers × 26 effects |
| `fine-armor.yml` | Fine armor crystals — 7 tiers × 16 effects |
| `common-accessory.yml` | Common accessory zyrkites — tier 6, 13 effects |
| `fine-accessory.yml` | Fine/Pristine accessory zyrkites — tier 6, 13 effects |
| `structures.yml` | Fusion structure IDs (standard + dyad + smart dyad variants) |
| `dyad-weapon.yml` | Dyad weapon crystal IDs by tier |
| `dyad-armor.yml` | Dyad armor crystal IDs by tier |
| `boxes.yml` | Crystal gacha box IDs per slot/tier |

---

## Naming Convention

### Individual crystals

```
{RARITY}_{EFFECT}_{TIER}
```

Examples: `COMMON_POUNDING_RHOMB`, `FINE_BRUTAL_HEXAGE`, `COMMON_HARDY_CABOCHON`

### Tier lists (all effects for one slot+tier)

```
{RARITY}_{SLOT}_{TIER}_IDS
```

Examples: `COMMON_WEAPON_RHOMB_IDS`, `FINE_ARMOR_HEXAGE_IDS`

### All-tier lists (all tiers for one slot)

```
{RARITY}_{SLOT}_ALL_IDS
```

Examples: `COMMON_WEAPON_ALL_IDS`, `FINE_ARMOR_ALL_IDS`

### Accessory crystals (zyrkites)

Accessories use a flat list — no per-tier naming, just effect name:

```
{RARITY}_{EFFECT}_ZYRK
```

Examples: `COMMON_POWERFUL_ZYRK`, `FINE_KEEN_ZYRK`. Aggregated as `COMMON_ACCESSORY_IDS` / `FINE_ACCESSORY_IDS`.

---

## Tiers (ascending quality)

| Tier name | Used in variable names |
|-----------|----------------------|
| Rhomb | `_RHOMB` |
| Cabochon | `_CABOCHON` |
| Hexage | `_HEXAGE` |
| Pentant | `_PENTANT` |
| Concach | `_CONCACH` |
| Crux | `_CRUX` |
| Niveot | `_NIVEOT` |

---

## Structures

Fusion structures are the consumable items used to slot crystals into gear. Three variants exist:

| Prefix | Description |
|--------|-------------|
| *(none)* | Standard fusion structure (e.g. `RHOMB_STRUCTURE`) |
| `DYAD_` | Dyad fusion structure (e.g. `DYAD_HEXAGE_STRUCTURE`) |
| `SMART_DYAD_` | Smart dyad structure (e.g. `SMART_DYAD_CONCACH_STRUCTURE`) |

All structure IDs are also available as `ALL_STRUCTURE_IDS`.

Note: `NIVEOT_STRUCTURE` exists in the standard set but not in the dyad set (dyad only goes up to Crux). `SMART_DYAD_NIVEOT_STRUCTURE` does exist.

---

## Gacha Boxes

Crystal box IDs follow a two-axis naming scheme:

```
{WEAPON|ARMOR}_CRYSTAL_BOX_{TIER}
```

Examples: `WEAPON_CRYSTAL_BOX_RHOMB`, `ARMOR_CRYSTAL_BOX_HEXAGE`. All 14 box IDs are also available as `ALL_CRYSTAL_BOX_IDS`.

---

## How to Import

Import only the specific variables you need. The full package exports hundreds of variables — importing all of them is wasteful and makes specs harder to read.

```yaml
imports:
  - from: crystals
    use:
      variables:
        - COMMON_WEAPON_HEXAGE_IDS   # all common weapon hexage crystals
        - FINE_ARMOR_ALL_IDS         # all fine armor crystals across all tiers
        - DYAD_HEXAGE_STRUCTURE      # dyad hexage structure item
        - ARMOR_CRYSTAL_BOX_HEXAGE   # armor hexage crystal box
```

Consumers in `patches/001/loot/e-compensation/` import a small targeted subset per zone (typically one or two tier-specific box IDs + a structure ID). The `10-crystal-boxes.yaml` spec imports a larger selection covering all Fine crystal IDs needed to populate gacha rewards.
