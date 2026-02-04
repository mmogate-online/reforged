# Patch Migration Tool

Applies all specs from a patch in sequence and syncs affected entities to the client DataCenter.

## Overview

The migration tool automates the full apply+sync pipeline for a patch. It discovers all YAML specs under a patch folder, applies them sequentially via `dsl apply`, detects which entities were modified, and runs a single targeted `dsl sync` for all affected syncable entities.

Individual spec failures (expected for zones without XML) do not stop the pipeline. Sync failures are fatal.

## Quick Start

```bash
# Apply all specs from patch 001 and sync to client
python reforged/tools/migrate/migrate.py --patch 001

# Dry run — validate without writing files
python reforged/tools/migrate/migrate.py --patch 001 --dry-run

# Apply only, skip client sync
python reforged/tools/migrate/migrate.py --patch 001 --skip-sync

# Verbose output (full DSL output + failed spec list)
python reforged/tools/migrate/migrate.py --patch 001 --verbose
```

## Parameters

| Flag | Required | Description |
|------|----------|-------------|
| `--patch` | Yes | Patch folder name under `reforged/specs/patches/` |
| `--dry-run` | No | Pass `--dry-run` to `dsl apply` and `dsl sync`, no files written |
| `--skip-sync` | No | Apply specs only, skip client sync step |
| `--verbose` | No | Show detailed DSL output and list all failed specs in summary |

## Execution Order

1. **Discover** — recursively scans `reforged/specs/patches/{patch}/` for `*.yaml` files
2. **Sort** — `sorted()` on relative paths; numbered prefixes (`01-`, `02-`) control order; subdirectory files sort after root-level specs
3. **Apply** — runs `dsl apply <spec> --path <server_datasheet>` for each spec sequentially
4. **Detect entities** — parses each spec to extract top-level entity keys
5. **Sync** — runs a single `dsl sync -e Entity1 -e Entity2 ...` for all syncable entities

## Spec Ordering

Root-level specs must use numbered prefixes to control execution order:

```
reforged/specs/patches/001/
├── 01-reaper-weapons.yaml          # Applied first
├── 02-evolutions.yaml              # Applied second
├── 03-flawless-mythic-grade.yaml
├── ...
├── 08-infusion-loot.yaml           # Applied eighth
├── loot/c-compensation/zone-*.yaml # Applied after all root specs
└── loot/e-compensation/zone-*.yaml # Applied last
```

## Supported Entity Schemas

The tool detects top-level YAML keys and maps them to sync-config entities:

| YAML Key | Sync Entity | Synced to Client |
|----------|-------------|------------------|
| `items` | ItemData | Yes |
| `equipment` | EquipmentData | Yes |
| `evolutions` | EquipmentEvolutionData | Yes |
| `materialEnchants` | MaterialEnchantData | Yes |
| `enchants` | EquipmentEnchantData | Yes |
| `enchantPassivityCategories` | EquipmentEnchantData | Yes |
| `itemStrings` | StrSheet_Item | Yes |
| `passivities` | Passivity | Yes |
| `passivityStrings` | StrSheet_Passivity | Yes |
| `cCompensations` | — | No (server-only) |
| `eCompensations` | — | No (server-only) |
| `fCompensations` | — | No (server-only) |
| `iCompensations` | — | No (server-only) |

Server-only schemas are reported in the summary but excluded from client sync.

## Path Resolution

Paths are read from `reforged/.references`:

| Key | Used For |
|-----|----------|
| `dsl_cli` | DSL CLI binary path |
| `server_datasheet` | `--path` argument for `dsl apply` |

## Output Example

```
Patch 001 — 8 specs + 264 loot specs (272 total)

[1/272] 01-reaper-weapons.yaml
        ✓ Applied 12 operations (12 successful, 0 failed)
[2/272] 02-evolutions.yaml
        ✓ Applied 167 operations (167 successful, 0 failed)
...
[64/272] loot/c-compensation/zone-0058-balderon.yaml
        ✗ Failed — zone has no cCompensation XML
...

── Summary ──
Applied: 199 specs (73 failed)
Entities modified: EquipmentEvolutionData, ItemData, MaterialEnchantData
Server-only: cCompensations, eCompensations, passivities (no sync needed)

── Client Sync ──
Syncing: EquipmentEvolutionData, ItemData, MaterialEnchantData
✓ Sync complete
```

## Adding New Entity Schemas

When new entity types are added to specs and/or `sync-config.yaml`:

1. Add the YAML key and sync entity name to `ENTITY_SYNC_MAP` in `migrate.py`
2. Use `None` for server-only schemas that should not be synced
3. If an entity has inline nested entities (like `enchantPassivityCategories` with inline `passivities`), add it to `INLINE_STRING_SYNC` with a list of implied sync entities
