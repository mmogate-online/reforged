---
name: new-spec
description: Use when creating a new DSL spec file. Provides the correct YAML structure including schema version, imports with variable opt-in, definitions, and operation blocks.
disable-model-invocation: false
user-invocable: true
argument-hint: [spec-name]
---

# Create a New DSL Spec

Follow this structure when creating a new spec file.

## Before authoring

- Use `mcp__datasheet-v92__find_free_ids` to pick IDs for new entities.
- Use `mcp__datasheet-v92__describe_entity` or `mcp__datasheet-v92__profile_item` to inspect existing entities before writing operations.
- For attributes not covered by the tables in this skill, consult the schema docs at the `dsl_docs_enduser` path from `.references`, under `schemas/`.
- For content affecting balance, rewards, or currencies, check the content framework docs (`content_framework` in `.references`) first.

## 1. Choose location

Specs are organized by patch and concern:

```
specs/patches/<patch>/               — main specs (numbered for execution order)
specs/patches/<patch>/evolutions/    — evolution path specs
specs/patches/<patch>/loot/          — loot table specs
  loot/c-compensation/               — class-branched drops (CCompensation)
  loot/e-compensation/               — environment/PvE drops (ECompensation)
specs/backlog/                       — future/pending specs
```

**Naming convention:** `<NN>-<descriptive-name>.yaml` where NN is a two-digit execution order number. Zone loot files use `zone-<id>-<name>.yaml`.

## 2. File header

Every spec starts with a descriptive comment and the spec block:

```yaml
# <Title> — Patch <NNN>
# <One-line description of what this spec does>

spec:
  version: "1.0"
  schema: v92
```

## 3. Imports

### Importing definitions only (auto-import)

```yaml
imports:
  - from: weapons
```

Definitions are available immediately — no `use:` clause needed.

### Importing variables (explicit opt-in required)

```yaml
imports:
  - from: crystals
    use:
      variables:
        - COMMON_POUNDING_RHOMB
        - WEAPON_CRYSTAL_BOX_RHOMB
```

**Variables require `use: variables:` listing every variable by name.** An import without `use: variables:` imports zero variables, even if the package exports them.

### Mixed imports

```yaml
imports:
  - from: evolution-base
    use:
      variables:
        - PAVERUNE_OF_SHARA
  - from: weapons
```

## 4. Definitions (optional)

Use definitions to reduce duplication within the spec:

```yaml
definitions:
  myBase:
    combatItemType: EQUIP_WEAPON
    maxStack: 1
    tradable: true

  myVariant:
    $extends: myBase
    category: axe
```

Reference with `$extends: myBase` in operation entries. Prefix internal-only definitions with `_` by convention.

## 5. Operation blocks

Use the appropriate top-level entity block with an operation:

| Operation | When to use |
|-----------|-------------|
| `create` | New entities that must not already exist |
| `upsert` | Create or update — safe default for most cases |
| `update` | Modify existing entities only |
| `updateWhere` | Bulk update matching a filter |
| `delete` | Remove entities |

```yaml
items:
  upsert:
    - id: $MY_ITEM_ID
      $extends: myBase
      level: 60
      strings:
        name: "My Item"
        toolTip: "Description here"
```

### Common entity blocks

| Block | Entity | Key field |
|-------|--------|-----------|
| `items` | ItemTemplate | `id` |
| `equipments` | Equipment | `equipmentId` |
| `enchants` | EquipmentEnchantData | `enchantId` |
| `passivities` | Passivity | `passivityId` |
| `cCompensations` | CCompensation | `huntingZoneId` + `npcTemplateId` |
| `eCompensations` | ECompensation | `huntingZoneId` + `npcTemplateId` |
| `gachaItems` | GachaItem | `itemTemplateId` |
| `rawStoneItems` | RawStoneItem | `rawStoneItemId` |
| `itemProduceRecipes` | ItemProduceRecipe | `id` |
| `equipmentEvolutions` | EquipmentEvolution | `evolutionId` |

## 6. Validate

After writing the spec, validate it immediately:

```bash
"<project_root>/dsl.exe" validate <spec-path> --path "<server_datasheet>"
```

Resolve paths from `.references` (keys: `project_root`, `server_datasheet`).

## Complete example

```yaml
# Starter Weapons — Patch 001
# Creates level 1 training weapons for new characters.

spec:
  version: "1.0"
  schema: v92

imports:
  - from: weapons
  - from: equipment-item-ids
    use:
      variables:
        - STARTER_SWORD_ID
        - STARTER_AXE_ID

definitions:
  starterBase:
    $extends: weaponBase
    level: 1
    rareGrade: 0
    tradable: false
    buyPrice: 0
    sellPrice: 0

items:
  upsert:
    - id: $STARTER_SWORD_ID
      $extends: starterBase
      combatItemSubType: dualSword
      strings:
        name: "Training Sword"
    - id: $STARTER_AXE_ID
      $extends: starterBase
      combatItemSubType: axe
      strings:
        name: "Training Axe"
```


## Lessons

### Never invent an XML encoding; verify format precedent in the stock corpus first
- **Date/source:** 2026-07-21: live run paid single-class reward rows but none of the semicolon-merged `class="warrior;slayer;..."` rows spec 04's generator emitted; `class="...;..."` had ZERO occurrences in stock v92 and v31 CompensationData (filed as `docs/dsl-requests/2026-07-21-compensation-class-row-collapse.md`, fixed in datasheetlang d79aca90 with an E207 guard).
- **Why:** `dsl validate` checks spec-vs-schema, not engine parseability; a workaround encoding can validate green, apply cleanly, survive a value-level reconciliation gate, and still be dead data the engine silently ignores.
- **Apply:** before shipping any encoding not copied verbatim from a source datasheet, grep the STOCK corpus (all zones of the same family, both eras) for the exact pattern; zero occurrences means the engine almost certainly does not parse it. File the underlying DSL limitation instead of inventing a format, and treat "validation green" as necessary, never sufficient.
