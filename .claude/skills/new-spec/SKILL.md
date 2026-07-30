---
name: new-spec
description: >
  Author a new DSL spec file: correct YAML structure, schema version, imports with variable
  opt-in, definitions, and operation blocks. Also covers reading an entity's capabilities
  before choosing an operation, since which operations exist, which fields accept transforms,
  and which collections are list-replace routinely change what you should build. Use when
  creating a spec, when deciding which operation or entity block fits a change, when checking
  whether the DSL can express something at all, or when an operation validates green but
  appears to do nothing.
disable-model-invocation: false
user-invocable: true
argument-hint: [spec-name]
---

# Create a New DSL Spec

Follow this structure when creating a new spec file.

## Before authoring

- Use `mcp__datasheet-v92__find_free_ids` to pick IDs for new entities.
- Use `mcp__datasheet-v92__describe_entity` or `mcp__datasheet-v92__profile_item` to inspect existing entities before writing operations.
- **Reference existing items by a package constant, not a raw id.** Import the `item-ids` constant (e.g. `$SPEED_MOTE_649`) instead of hardcoding a templateId. If an item you reference is not named yet, generate it demand-driven: `python tools/item-ids/gen_item_ids.py names --datasheet "<server_datasheet>" --from-spec <spec>` (see the `spec-standardization` skill). Before minting a NEW id, confirm it is free: `gen_item_ids.py check --ids <id>`.
- For attributes not covered by the tables in this skill, consult the schema docs at the `dsl_docs_enduser` path from `.references`, under `schemas/`.
- For content affecting balance, rewards, or currencies, check the content framework docs (`content_framework` in `.references`) first.
- **If the spec touches `quests` or `questCompensations`, invoke `quest-design-review` first.** Quests fail review as a system, not one at a time: duplicate rewards, gear sets nothing completes, objectives the zone cannot supply, and references into disabled quests are all invisible in a spec diff and none are caught by `dsl validate`.

### Read the entity's capabilities before choosing the operation

Open `schemas/<category>/<entity>.mdx` and read three things before deciding on an approach:
the **`Operations:`** line, the **key attributes**, and any **field-level restriction table**
(which fields accept transforms, which are list-replace, which are create-only).

Do this even when you are confident the operation exists. The capability set is a design
input, not a feasibility check: it routinely changes what you should build, and the failure
mode when you skip it is silent. Evidence from one session (2026-07-25):

- `stat.def` is not transform-capable (only `stat.maxHp`, `stat.atk`, `stat.level` and
  `critical.res`, plus two `npcSkills` fields). A proposed NPC balance pass that scaled
  defense was cut before any numbers were written, because expressing it would have meant
  hardcoding absolutes per template.
- `balanceProfiles` entries compound in declaration order when their cohorts overlap, which
  forced three cohorts to be made provably disjoint rather than layered.
- `dungeonDatas.update` accepts a nested collection under `changes` and decomposes to ZERO
  commands. It reports `Valid: 1 operation(s)` with only a `W503` warning, so the spec would
  have shipped as a no-op that passes an op-count reconciliation.

When the doc leaves a semantic ambiguous and the blast radius is real, probe it rather than
guess: see the scratch-datasheet technique in `apply-spec`.

## 1. Choose location

Specs are organized by patch and concern:

```
specs/patches/<patch>/              : main specs (numbered for execution order)
specs/patches/<patch>/evolutions/   : evolution path specs
specs/patches/<patch>/loot/         : loot table specs
  loot/c-compensation/              : class-branched drops (CCompensation)
  loot/e-compensation/              : environment/PvE drops (ECompensation)
specs/backlog/                      : future/pending specs
```

**Naming convention:** `<NN>-<descriptive-name>.yaml` where NN is a two-digit execution order number. Zone loot files use `zone-<id>-<name>.yaml`.

## 2. File header

Every spec starts with a descriptive comment and the spec block:

```yaml
# <Title>: Patch <NNN>
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

Definitions are available immediately: no `use:` clause needed.

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
| `upsert` | Create or update: safe default for most cases |
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

For a generated spec, also run the standardization analyzers before shipping: `analyze.py` for repeated blocks and `analyze_ids.py` for hardcoded ids that should be package constants. See the `spec-standardization` skill.

## Complete example

```yaml
# Starter Weapons: Patch 001
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

### Operations run grouped by KIND in a fixed order, so delete-then-create in one spec can never work
- **Date/source:** 2026-07-30: a spec listed `itemMixes: delete` for id 216862 and `itemMixes: create` for the corrected record, in that order in the file. The create failed. DSL `d53dbfad` then made the reason explicit as a new `E429` naming the id, the file and the ordering rule.
- **Why:** `SpecMapper` emits operations grouped by kind in the order create, update, delete, upsert, regardless of the order the keys appear in the YAML. The create is therefore always attempted while the id is still taken. Key position in the file buys no sequencing at all.
- **Apply:** to rewrite a whole record, use `upsert`, never delete plus create. Never rely on YAML key order for sequencing inside one spec. When ordering genuinely matters, split across two specs: `discover_specs` sorts on the relative path string, so the later-sorting file is the last writer (note that a subdirectory like `loot/` sorts after every numbered file at the same level).

### Clone a donor record the server already loads; never synthesize a new one from the schema
- **Date/source:** 2026-07-24: three DSL-created quests (1380/1381/1387, spec 002/18) crashed the world server during datasheet validation with a bare `access violation ... Write to 0x0` and no file name; the symbolized crash stack named `QuestTemplate::Validate`. Six deploy/restart cycles. The DSL side is fixed as of the 2026-07-25 binary (`1.0.0+5f90181c`): quest entry children are now scaffolded from a mechanically derived structure contract, so this exact trap is closed for Quest. The lesson stands for every other entity the server validates, and the request that documented it was closed and deleted.
- **Why:** DSL emits only what the spec author supplied, but the server dereferences nodes that appear in 100% of the corpus for that task type without null-checking them. The missing nodes sat at several nesting depths (`보상` and `진행조건` at body level; `연출Id` inside `방문그룹/방문그룹`; `조우시대사`/`사망시대사`/`이상상태조건` inside `몬스터지정/몬스터지정`), so auditing corpus statistics one level at a time surfaced exactly one layer per boot and each "fix" looked complete until the next crash. `dsl validate` passes throughout, and the client packs fine, because only the server loader is strict.
- **Apply:** when a spec CREATES a record for an entity the server validates (quests above all), pick a donor of the same shape that the live server already loads, and make the new record structurally identical to it: same elements, same nesting, same order, substituting values only. For quests the donors used were 001371 (quest `Header` plus `방문Task` bodies) and 001303 (`사냥Task` body). Verify with a RECURSIVE conformance check (every container path, not just top-level children) against the stock corpus of both eras, and match corpus element ORDER: the loader reads sequentially, so a value written before its container can be applied to a null pointer. Terminate task chains with an empty `<다음Task />` (5522 corpus instances) rather than `0` (7, all DSL-authored). If the server still crashes after two isolating boots, stop hypothesizing and clone; see the `server-load-diagnosis` skill for the crash-artifact forensics.

### Never invent an XML encoding; verify format precedent in the stock corpus first
- **Date/source:** 2026-07-21: live run paid single-class reward rows but none of the semicolon-merged `class="warrior;slayer;..."` rows spec 04's generator emitted; `class="...;..."` had ZERO occurrences in stock v92 and v31 CompensationData (filed as `docs/dsl-requests/2026-07-21-compensation-class-row-collapse.md`, fixed in datasheetlang d79aca90 with an E207 guard).
- **Why:** `dsl validate` checks spec-vs-schema, not engine parseability; a workaround encoding can validate green, apply cleanly, survive a value-level reconciliation gate, and still be dead data the engine silently ignores.
- **Apply:** before shipping any encoding not copied verbatim from a source datasheet, grep the STOCK corpus (all zones of the same family, both eras) for the exact pattern; zero occurrences means the engine almost certainly does not parse it. File the underlying DSL limitation instead of inventing a format, and treat "validation green" as necessary, never sufficient.
