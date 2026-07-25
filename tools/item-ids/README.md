# item-ids generator

Builds the `item-ids` naming registry and the conflict-avoidance occupied-id set from
the raw datasheet. Deterministic (sorted iteration, streaming `iterparse`, no timestamps)
because the source files are large (`ItemTemplate.xml` alone is 45MB).

## Sources

- **All** `ItemTemplate*.xml` (20 files, ~112k items, ids disjoint across files, zero
  cross-file conflicts). No file is excluded: regional and tool/dummy variants are all
  part of the id universe for conflict purposes.
- `StrSheet_Item*.xml` for display names. The base `StrSheet_Item.xml` is the English
  sheet and wins; a regional sheet is used only when base lacks the id; the internal
  `name` attribute is the last fallback.

## Modes

```bash
# 1. Occupied-id set (conflict-avoidance). Writes tools/item-ids/occupied_ids.json.
python gen_item_ids.py occupied --datasheet <server_datasheet>

# 2. Name the items a spec references (demand-driven). Writes packages/item-ids/*.
python gen_item_ids.py names --datasheet <server_datasheet> --from-spec <spec.yaml>
python gen_item_ids.py names --datasheet <server_datasheet> --ids 21351,94203,649

# 3. Check whether ids are free or taken (reads occupied_ids.json).
python gen_item_ids.py check --ids 700000,602176
```

`names` skips ids already named by another package and ids that are not items in
`ItemTemplate*`. It clears and rewrites the package shards each run, so the tree is a
pure function of the inputs.

## Naming

`SLUG(name)_<id>`: parentheticals dropped, non-alphanumerics to `_`, uppercased, id
appended. A digit-leading slug is prefixed `ITEM_` to stay a valid DSL variable name.
Korean-only items with no English string fall back to the internal name plus id.

## Design notes

- **No allocation ledger.** Item ids have no predictable range pattern (base ids scatter
  across 1..20M), so conflict-avoidance is a membership test against the exact occupied
  set, not a range prediction.
- **Resolve the display name from StrSheet, never from a spec's co-located string.** The
  generator reads the authoritative sheet; it does not trust whatever label sat next to
  an id in a spec.
