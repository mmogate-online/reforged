---
name: create-package
description: Use when creating a new DSL package. Guides through directory setup, index.yml structure, sub-file exports, variable re-export pattern, and datasheetlang.yml registration.
disable-model-invocation: false
user-invocable: true
---

# Create a DSL Package

Follow these steps when creating a new DataSheetLang package. Do not skip any step.

## 1. Pre-flight

Read `datasheetlang.yml` and check existing packages under `workspace.packages`. Confirm the new package name does not collide with an existing one.

## 2. Create directory

```
packages/<package-name>/
└── index.yml
```

Package name must be **kebab-case** (e.g., `crystal-ids`, `evolution-base`).

## 3. Decide package type

| Type | When to use | index.yml contains |
|------|-------------|-------------------|
| Single-file | Small, cohesive set of variables and/or definitions | `variables:`, `definitions:`, `exports:` directly |
| Multi-file | Large packages or logical groupings | `imports:` from sub-files + `exports:` re-exporting |

## 4. Write index.yml

Every `index.yml` must start with:

```yaml
spec:
  version: "1.0"
```

### Single-file example

```yaml
spec:
  version: "1.0"

variables:
  MY_ITEM_ID: 50001

definitions:
  MyBase:
    combatItemType: EQUIP_WEAPON

exports:
  variables:
    - MY_ITEM_ID
  definitions:
    - MyBase
```

### Multi-file example

```yaml
spec:
  version: "1.0"

imports:
  - from: ./weapons.yml
    use:
      variables:
        - SWORD_ID
        - AXE_ID
  - from: ./armor.yml
    use:
      variables:
        - CHEST_ID

exports:
  variables:
    - SWORD_ID
    - AXE_ID
    - CHEST_ID
```

## 5. Write sub-files (multi-file only)

**Every sub-file MUST follow all of these rules:**

1. Start with `spec: version: "1.0"` — without this the DSL does not recognize it as a module
2. Declare variables in a `variables:` section and/or definitions in a `definitions:` section
3. List all exported names in an `exports:` section — variables in `exports.variables`, definitions in `exports.definitions`

```yaml
# packages/my-package/weapons.yml
spec:
  version: "1.0"

variables:
  SWORD_ID: 50001
  AXE_ID: 50002

exports:
  variables:
    - SWORD_ID
    - AXE_ID
```

### Critical: Variables vs definitions import behavior

| Export type | Auto-imports from sub-files? | Requires `use:` clause? |
|-------------|------------------------------|------------------------|
| Definitions | Yes | No — bare `- from: ./file.yml` is sufficient |
| Variables | **No** | **Yes** — must use `use: variables: [...]` in the import |

**This means:**
- index.yml importing definitions: `- from: ./bases.yml` (no `use:` needed)
- index.yml importing variables: requires explicit `use: variables:` listing every variable name
- index.yml can only re-export variables it explicitly imported via `use: variables:`
- Attempting to re-export a variable not in imported scope triggers **E535**

## 6. Register the package

Add the package to `datasheetlang.yml` under `workspace.packages`:

```yaml
workspace:
  packages:
    my-package: "./packages/my-package"
```

Without this, any spec importing from the package will fail with `Unknown package reference`.

## 7. Naming conventions

| Element | Convention | Examples |
|---------|-----------|----------|
| Package name | kebab-case | `crystal-ids`, `evolution-base` |
| File names | kebab-case.yml | `common-weapon.yml`, `grades.yml` |
| Variables | SCREAMING_SNAKE_CASE | `COMMON_POUNDING_RHOMB`, `BASE_HP` |
| Exported definitions | PascalCase | `WeaponBase`, `CommonGrade` |
| Internal definitions | _PascalCase | `_InternalHelper` (not exported) |

## 8. Consumer import pattern

Specs consuming the package must also use `use: variables:` for variables:

```yaml
imports:
  - from: my-package
    use:
      variables:
        - SWORD_ID

items:
  upsert:
    - id: $SWORD_ID
      level: 60
```

Definitions do not need `use:` — they are available automatically after `- from: my-package`.

## 9. Validate

Resolve the datasheet path from `.references` (`server_datasheet` key) and run:

```
dsl validate <spec-that-imports-package>.yaml --path "<server_datasheet>"
```

The package is correct when the consuming spec validates without E535 or E536 errors.
