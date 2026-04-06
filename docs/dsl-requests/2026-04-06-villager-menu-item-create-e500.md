# VillagerMenuItem: `create` operation fails with E500

**Date:** 2026-04-06

## Issue

`villagerMenuItems: create:` fails with E500 even when the entry does not exist yet. Switching to `upsert:` resolves the issue.

## Reproduction

**Spec:**

```yaml
spec:
  version: "1.0"
  schema: v92

villagerMenuItems:
  create:
    - id: 9999002
      itemTemplateId: 95214
      type: MedalStore
```

**Error:**

```
[E500] Command 'CreateVillagerMenuItemEntryCommand`1' could not be applied
```

## Workaround

Use `upsert:` instead of `create:`. The upsert correctly inserts the entry when it does not exist.

```yaml
villagerMenuItems:
  upsert:
    - id: 9999002
      itemTemplateId: 95214
      type: MedalStore
```

## Expected behavior

`create:` should insert the entry and succeed when no entry with the given ID exists, consistent with how `create` works for other entities like `buyMenuLists` and `buyLists`.

## Relevant doc reference

- `schemas/shop/villager-menu-item.mdx` — Operations listed: `create`, `update`, `delete`, `upsert`, `updateWhere`
