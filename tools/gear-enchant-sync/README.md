# Gear Enchant Sync Tool — DEPRECATED / DISABLED

**Status: disabled as of the equipment-item-standard package-owned migration.**

## Why Disabled

This tool previously generated `07-gear-enchant-sync.yaml`, a bulk `updateWhere`
spec that set `linkEnchantId` on every tier × slot item pool using variables
from the `enchant-standard` package.

After the migration that made `equipment-item-standard` the authoritative
baseline for equipment gear, the refactored `01-armor-standardize.yaml` and
`01-weapon-standardize.yaml` already set `linkEnchantId` via `$extends` into
package definitions (`HighTierChestItem`, `HighTierWeaponDPSTankItem`, …). The
per-tier × slot linkEnchantId assignment is now a natural side effect of
applying the tier baseline — duplicating it in a standalone spec is redundant
and risked divergence (e.g., Low Tier enchant references).

The generated spec `07-gear-enchant-sync.yaml` has been deleted. The generator
scripts (`generate_spec.py`, `generate_id_lists.py`) are preserved here for
historical reference but **must not be re-run** — regeneration would resurrect
a spec whose authority is now held by the armor/weapon standardize sweeps.

## If you need to add a new tier/slot enchant binding

Edit the `equipment-item-standard` package definition for the target tier/slot
(e.g., add `linkEnchantId: $ENCHANT_NEW_TIER_NEW_SLOT` on `NewTierNewSlotItem`).
The next apply of `01-armor-standardize.yaml` / `01-weapon-standardize.yaml`
will propagate the change to every item in the corresponding pool.

## Historical Notes

The tool produced 14+ `updateWhere` rules covering Mythic, Superior, and Rare
tiers across weapons (healer vs DPS/Tank) and armor (body, hand by material,
feet). Filter strategy evolved from `category`-based to ID-based before the
tool was deprecated.

Preserved files:

- `generate_spec.py` — generated the now-deleted `07-gear-enchant-sync.yaml`
- `generate_id_lists.py` — generated per-tier ID lists from
  `gear_progression.csv`
