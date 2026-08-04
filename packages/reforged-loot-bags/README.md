# reforged-loot-bags

Parameterized `ItemBag` templates for the reforged drop economy that is merged into
every restored zone's loot table.

## Definitions

Each exports two `$with` parameters:

- `PROB`: bag-level drop probability (difficulty-weighted per mob)
- `QTY`: per-drop quantity (`min == max`; scales by mob difficulty)

| Definition | Bag id | Items | Notes |
|------------|--------|-------|-------|
| `AlkahestBag` | 101 | Masterwork Alkahest (21351) | item `probability: 1.0` |
| `FeedstockBag` | 109 | Tier 1 Feedstock (94101) | item `probability: 1.0` |
| `DyadStructureBag` | 103 | Dyad Rhomb Structure (96108) | item `probability: 1.0` |
| `SmartDyadStructureBag` | 104 | Smart Dyad Rhomb Structure (96114) | item `probability: 1.0` |
| `CrystalBoxesBag` | 102 | Weapon + Armor Crystal Box (602176/602177) | `equalProbability: true` |
| `InfusionBoxUncommonBag` | 105 | Infusion Weapon/Chest/Gloves/Boots Box (602190/93/96/99) | `equalProbability: true` |

Bag ids follow the generator's `REFORGED_BAG_ID_OFFSET` layout: v31 native ids stay
`<= 20`, reforged ids are offset by `+100` so the two economies never collide when
merged into one `eCompensations` entry.

## Usage

```yaml
imports:
  - from: reforged-loot-bags
    use:
      definitions:
        - AlkahestBag
        - CrystalBoxesBag

eCompensations:
  upsert:
    - huntingZoneId: 13
      npcTemplateId: 1
      itemBags:
        - $extends: AlkahestBag
          $with: { PROB: 0.05, QTY: 1 }
        - $extends: CrystalBoxesBag
          $with: { PROB: 0.02, QTY: 1 }
```

## Provenance

Curated, but derived: the six bag structures were identified by
`tools/spec-standardize/analyze.py` over `specs/patches/002/17-iod-loot.yaml`, where
they appeared structurally identical on all 47 IoD mobs (differing only in `PROB` and
`QTY`). The IoD-specific Kugai token bag (token 95216, ~8 mobs) is deliberately not
factored here; the generator emits it per-row.

Second consumer trigger: when another restored zone's loot generator merges the same
reforged bags, import from here rather than re-authoring. The item ids are global, so
these templates are zone-agnostic.
