# evolution-base Package

Provides all shared materials, parameters, and definition templates for gear evolution specs. Every evolution spec in the project imports from this package.

## What It Provides

- **Rune material IDs** — item IDs for all 5 rune tiers × 2 continents (Shara/Arun), plus the Aeru Rune
- **Evolution parameters** — default cost and success probability
- **Path definitions** — one `*OfSharaPath` / `*OfArunPath` per rune tier, ready to `$extends`
- **`EvolutionItem` template** — parameterized definition that generates the full 4-step enchant progression for a single gear piece

---

## Rune Material IDs

Runes come in two continent variants. The convention is consistent across all tiers:

| Variable | ID | Use |
|----------|----|-----|
| `PAVERUNE_OF_SHARA` | 501 | Tier 1 — weapons |
| `PAVERUNE_OF_ARUN` | 511 | Tier 1 — armor |
| `SILRUNE_OF_SHARA` | 502 | Tier 2 — weapons |
| `SILRUNE_OF_ARUN` | 512 | Tier 2 — armor |
| `QUOIRUNE_OF_SHARA` | 503 | Tier 3 — weapons |
| `QUOIRUNE_OF_ARUN` | 513 | Tier 3 — armor |
| `ARCHRUNE_OF_SHARA` | 504 | Tier 4 — weapons |
| `ARCHRUNE_OF_ARUN` | 514 | Tier 4 — armor |
| `KEYRUNE_OF_SHARA` | 505 | Tier 5 — weapons |
| `KEYRUNE_OF_ARUN` | 515 | Tier 5 — armor |
| `AERU_RUNE` | 520 | Combined with Keyrune for Tier 5+ paths |

**Shara = weapons, Arun = armor.** This is the universal rule across all evolution specs.

---

## Path Definitions

Each rune tier has a pre-built path definition for each continent variant. All paths share the same base parameters:

- `evolutionProb`: `1.0` (100% success rate)
- `requiredMoney`: `10000` (10,000 gold)
- `awaken`: `false`
- `masterpiece`: `false`
- Amount: `2` runes per evolution step

| Definition | Rune | Use |
|-----------|------|-----|
| `PaveruneOfSharaPath` | Paverune of Shara ×2 | Tier 1 weapon evolutions |
| `PaveruneOfArunPath` | Paverune of Arun ×2 | Tier 1 armor evolutions |
| `SilruneOfSharaPath` | Silrune of Shara ×2 | Tier 2 weapon evolutions |
| `SilruneOfArunPath` | Silrune of Arun ×2 | Tier 2 armor evolutions |
| `QuoiruneOfSharaPath` | Quoirune of Shara ×2 | Tier 3 weapon evolutions |
| `QuoiruneOfArunPath` | Quoirune of Arun ×2 | Tier 3 armor evolutions |
| `ArchruneOfSharaPath` | Archrune of Shara ×2 | Tier 4 weapon evolutions |
| `ArchruneOfArunPath` | Archrune of Arun ×2 | Tier 4 armor evolutions |
| `KeyruneOfSharaPath` | Keyrune of Shara ×2 | Tier 5 weapon evolutions |
| `KeyruneOfArunPath` | Keyrune of Arun ×2 | Tier 5 armor evolutions |
| `KeyruneOfSharaAeruPath` | Keyrune of Shara ×2 + Aeru Rune ×1 | Tier 5+ weapon evolutions |
| `KeyruneOfArunAeruPath` | Keyrune of Arun ×1 + Aeru Rune ×1 | Tier 5+ armor evolutions |

---

## `EvolutionItem` Template

The central template. One `EvolutionItem` entry covers a single gear piece (one source item evolving into one target item) across **4 enchant steps**:

| Source enchant step | → Result enchant step |
|--------------------|-----------------------|
| +9 | → +0 |
| +10 | → +3 |
| +11 | → +6 |
| +12 | → +9 |

### Parameters

| Param | Description |
|-------|-------------|
| `SOURCE` | Item template ID of the gear being evolved (the current item) |
| `TARGET` | Item template ID of the resulting gear |
| `PATH_DEF` | Name of the path definition to use (`PaveruneOfSharaPath`, etc.) |

### Usage in a Spec

```yaml
imports:
  - from: evolution-base
    use:
      variables:
        - EVOLUTION_COST
        - EVOLUTION_PROB
        - PAVERUNE_OF_SHARA
        - PAVERUNE_OF_ARUN
      definitions:
        - EvolutionItem
        - PaveruneOfSharaPath
        - PaveruneOfArunPath

variables:
  SOURCE_WEAPON_DUAL: 12137
  TARGET_WEAPON_DUAL: 10593

evolutionPaths:
  upsert:
    - $extends: EvolutionItem
      $with: { SOURCE: $SOURCE_WEAPON_DUAL, TARGET: $TARGET_WEAPON_DUAL, PATH_DEF: PaveruneOfSharaPath }
```

**Always use `upsert`** — evolution specs are idempotent and safe to re-apply.

### Import note

Variables must be explicitly listed under `use.variables`. Definitions must be listed under `use.definitions`. Neither is auto-imported even when the package is imported — DSL requires explicit opt-in for both.

---

## Consumers

| Spec | Rune tier |
|------|-----------|
| `patches/001/evolutions/02-evo-00-pre-starter.yaml` | Paverune (Kugai's → Starter 0) |
| `patches/001/evolutions/02-evo-00-starter-0.yaml` | Paverune (Starter 0 → Starter 1) |
| `patches/001/evolutions/02-evo-01-starter-1.yaml` | Paverune (Starter 1 → Bastion) |
| `patches/001/evolutions/02-evo-02-bastion.yaml` through `02-evo-08-thalnim.yaml` | Silrune–Keyrune (MID tier chain) |
| `patches/001/13-potential-unlock-evolution.yaml` | Keyrune (potential unlock gear) |
| `patches/001/loot/e-compensation/*.yaml` | Rune ID variables only (as drop rewards) |
