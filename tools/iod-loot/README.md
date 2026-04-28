# IoD Loot Generator

Generates the `eCompensation` loot spec for all 47 mobs in Island of Dawn (hunting zone 13) using difficulty-weighted drop rates.

## Quick Start

```bash
# 1. Generate the spec
python reforged/tools/iod-loot/generate_iod_loot.py --patch 001

# 2. Apply to server
dsl apply "reforged\specs\patches\001\17-iod-loot.yaml" --path "<server_datasheet>"
```

Or use the batch files: `generate.bat` → `deploy.bat`.

## Difficulty Model

Each mob's drop probabilities scale proportionally to its difficulty score:

```
score = sqrt(maxHp × atk)
prob  = BASE_PROB × (score / mean_score)
```

`mean_score` is the average across all non-environmental combat mobs. A mob at exactly the mean therefore drops at `BASE_PROB`. Harder mobs drop more; easier mobs drop less.

**Environmental mobs** (creature playStyle, HP < 50 — Giant Honeybee, Docile Terron, Terron Saboteur env) are floored at their minimum and do not participate in the mean calculation.

All probabilities are clamped to `[MIN_PROB, MAX_PROB]`.

## Drop Table

Each mob has 5 independent item bags:

| Bag | Base Prob (at mean) | Range | Contents |
|-----|---------------------|-------|----------|
| EnchantMaterials | 20% | 1–54% | 1× Masterwork Alkahest + 2× Tier 1 Feedstock |
| CrystalBoxes | 10% | 1–27% | Weapon or Armor Crystal Box (Rhomb), equal chance |
| DyadStructure | 1% | 1–2.7% | Dyad Rhomb Structure |
| SmartDyadStructure | 0.1% | 0.1–0.27% | Smart Dyad Rhomb Structure |
| InfusionBoxUncommon | 1% | 1–2.7% | Weapon / Chest / Gloves / Boots Infusion Box (Uncommon), equal chance |

Bags roll independently — a single kill can yield multiple rewards.

## Configuration

All rates are constants at the top of `generate_iod_loot.py`:

```python
BASE_PROB            = 0.20   # enchant mats (at mean mob)
CRYSTAL_BASE_PROB    = 0.10   # rhomb crystal boxes
DYAD_BASE_PROB       = 0.01   # dyad rhomb structure
SMART_DYAD_BASE_PROB = 0.001  # smart dyad rhomb structure
INFUSION_BASE_PROB   = 0.01   # uncommon infusion box
MIN_PROB             = 0.01
MIN_PROB_SMART_DYAD  = 0.001
MAX_PROB             = 0.80
```

After editing, re-run `generate_iod_loot.py` and re-apply the spec. The spec is idempotent (`upsert`) — safe to re-apply at any time.

## Output

`specs/patches/{NNN}/17-iod-loot.yaml` — `eCompensations` upsert for all 47 mobs.

The generator also prints:
- Full difficulty ranking table with all bag probabilities per mob
- Expected enchant material yield for the 50-kill IoD quest budget
- Enchant cost reference (expected alka + feedstock to reach +3)

## Item IDs

| Item | ID | Source |
|------|----|--------|
| Masterwork Alkahest | 21351 | — |
| Tier 1 Feedstock | 94101 | — |
| Weapon Crystal Box (Rhomb) | 602176 | `packages/crystals/boxes.yml` |
| Armor Crystal Box (Rhomb) | 602177 | `packages/crystals/boxes.yml` |
| Dyad Rhomb Structure | 96108 | `packages/crystals/structures.yml` |
| Smart Dyad Rhomb Structure | 96114 | `packages/crystals/structures.yml` |
| Infusion Weapon Box (Uncommon) | 602190 | `packages/gear-infusion-boxes/index.yml` |
| Infusion Chest Box (Uncommon) | 602193 | `packages/gear-infusion-boxes/index.yml` |
| Infusion Gloves Box (Uncommon) | 602196 | `packages/gear-infusion-boxes/index.yml` |
| Infusion Boots Box (Uncommon) | 602199 | `packages/gear-infusion-boxes/index.yml` |
