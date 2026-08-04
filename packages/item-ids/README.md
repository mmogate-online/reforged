# item-ids

Per-item constant names for item template ids. Generated, demand-driven, and sharded.

## What it is

- **Constant per referenced item**, named `SLUG(displayName)_<id>` (e.g.
  `CUIRASS_OF_THE_FIRST_EXPEDITION_15022`, `SPEED_MOTE_649`, `TIER_3_ALKAHEST_94203`).
  The `_<id>` suffix guarantees uniqueness: no name source in the game data is unique on
  its own, so the id is the only safe key.
- **Demand-driven, not exhaustive.** Only ids that specs reference are named. The full
  item table is 112k+ items; naming all of it would tax every importing spec for
  constants nobody uses.
- **Sharded by item class** (`gear-weapons`, `gear-armor`, `gear-accessories`,
  `materials`, `consumables`, `recipes`, `skillbooks`, `tokens-boxes`, `misc`) so a spec
  imports only the shard it needs.
- Ids already named by another package (`crystals`, `gear-infusion-boxes`, `npc-ids`,
  `iod-tokens`, `evolution-base`, ...) are **not** duplicated here.

## Generated, do not hand-edit

Produced by `tools/item-ids/gen_item_ids.py` from all `ItemTemplate*.xml` (the full item
universe) and `StrSheet_Item*.xml` (English names from the base sheet, regional/internal
fallback). Regenerate to add newly referenced items; see that tool's README.

## Usage

```yaml
imports:
  - from: item-ids
    use:
      variables:
        - SPEED_MOTE_649
        - TIER_3_ALKAHEST_94203

eCompensations:
  upsert:
    - huntingZoneId: 13
      npcTemplateId: 1
      itemBags:
        - id: 2
          items:
            - templateId: $SPEED_MOTE_649
              min: 1
              max: 1
```

## Conflict-avoidance is separate

This package is about names. The occupied-id set (for checking whether a new id is free)
is `tools/item-ids/occupied_ids.json`, queried with `gen_item_ids.py check`. It is not a
package and specs never import it.
