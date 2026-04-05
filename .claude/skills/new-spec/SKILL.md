---
name: new-spec
description: Use when creating a new DSL spec file. Provides the correct YAML structure including schema version, imports with variable opt-in, definitions, and operation blocks.
disable-model-invocation: false
user-invocable: true
argument-hint: [spec-name]
---

# Create a New DSL Spec

Follow this structure when creating a new spec file.

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
