# Patch Migration Tool

Applies all specs from a patch in a single batch and syncs affected entities to the client DataCenter, using DSL apply manifests to narrow the sync to exactly the files touched.

## Overview

The migration tool automates the full apply→sync pipeline for a patch. It discovers all YAML specs under a patch folder, applies them in **one batch call** (specs share an in-memory cache — later specs see earlier specs' mutations without disk round-trips), and then runs `dsl sync --from-manifest` that regenerates only the client shards whose server sources were actually modified.

Reads are pinned to the server datasheet repo's HEAD commit via `--source-ref`. This ensures `multiply`/`add` transforms in balance specs are idempotent — re-applying the same patch against the same HEAD produces the same result.

Any spec failure stops the run (fail-fast); **nothing is committed** — DSL rolls back the whole batch transaction. Sync failures are also fatal.

## Quick Start

```bash
# Apply all specs from patch 001 and sync to client (manifest-narrowed)
python reforged/tools/migrate/migrate.py --patch 001

# Dry run — validate without writing files
python reforged/tools/migrate/migrate.py --patch 001 --dry-run

# Apply only, skip client sync
python reforged/tools/migrate/migrate.py --patch 001 --skip-sync

# Full sync (escape hatch: disable manifest narrowing)
python reforged/tools/migrate/migrate.py --patch 001 --no-narrow

# Read from working tree instead of HEAD (bypass source-ref)
python reforged/tools/migrate/migrate.py --patch 001 --no-source-ref

# Verbose DSL diagnostic output
python reforged/tools/migrate/migrate.py --patch 001 --verbose
```

## Parameters

| Flag | Required | Description |
|------|----------|-------------|
| `--patch` | Yes | Patch folder name under `reforged/specs/patches/` |
| `--dry-run` | No | Pass `--dry-run` to `dsl apply` and `dsl sync`; no files written, no manifests emitted |
| `--skip-sync` | No | Apply specs only, skip client sync; no manifests emitted |
| `--no-narrow` | No | Emit apply manifest for inspection but run broad sync without `--from-manifest` (escape hatch) |
| `--no-source-ref` | No | Read datasheets from working tree instead of server repo HEAD (disables idempotency guarantee for balance specs) |
| `--verbose` | No | Pass `--verbose` to `dsl apply` for diagnostic output |

## Execution Order

1. **Preflight** — scan server datasheet tree for Windows-reserved `nul` files and warn (they block robocopy later)
2. **Source-ref** — resolve `git rev-parse HEAD` in `server_datasheet`; passed as `--source-ref` to `dsl apply`
3. **Detect entities** — pre-scans all spec YAML files for top-level entity keys (determines sync targets before any apply runs)
4. **Prepare manifest dir** — wipe `reforged/tools/migrate/.manifests/<patch>/` (gitignored)
5. **Discover** — recursively scans `reforged/specs/patches/{patch}/` for `*.yaml` files
6. **Sort** — `sorted()` on relative paths; numbered prefixes (`01-`, `02-`) control order; subdirectory files sort after root-level specs
7. **Apply** — runs `dsl apply spec1 spec2 … --path <server_datasheet> --source-ref <HEAD> --manifest-out run.json`; specs share an in-memory cache; first failure stops the run and rolls back everything (nothing written to disk)
8. **Sync** — runs `dsl sync -e Entity1 -e Entity2 … --from-manifest run.json` against the manifest

## Manifest Directory

Each run emits a single merged manifest:

```
reforged/tools/migrate/.manifests/<patch>/
  run.json    ← manifest from dsl apply (all specs, union of modified files)
```

`run.json` follows DSL manifest v2 format. The tool passes it to `dsl sync --from-manifest` to narrow the sync.

The directory is gitignored, wiped at the start of each run, and persisted until the next run for post-run diagnostics. No manifests are emitted on `--dry-run` or `--skip-sync`.

## Sync-Skip Conditions

The tool skips the sync phase in several cases. Each prints a clear message and returns the documented exit code:

| Condition | Exit | Message |
|-----------|------|---------|
| Any spec fails | 1 | DSL prints per-spec FAILED output; no files written |
| `--skip-sync` passed | 0 | `Sync skipped (--skip-sync)` |
| No specs declared a syncable entity | 0 | `No syncable entities — nothing to sync` |
| Applies succeeded but wrote nothing (idempotent) | 0 | `No server-side file changes — sync skipped` |

The last case is common when re-running a patch against already-applied server state — specs find all items/entities already in the correct state, write nothing, and the manifest has an empty `modified_files` list. Use `--no-narrow` to force the broad sync anyway.

On failure, the batch transaction rolls back automatically — the working tree is left unchanged. Use `git checkout .` in the server datasheet repo only if you made manual edits that need reverting.

## Spec Ordering

Root-level specs must use numbered prefixes to control execution order:

```
reforged/specs/patches/001/
├── 01-armor-standardize.yaml       # Applied first
├── 02-reaper-weapons.yaml          # Applied second
├── 02-brawler-weapons.yaml         # Applied third (same prefix → alphabetical)
├── ...
├── 15-infusion-boxes.yaml          # Applied last root-level
├── balance/zone-0013-island_of_dawn.yaml  # After all root specs
└── loot/c-compensation/zone-*.yaml # Applied after all root specs
```

## Source-Ref and Balance Specs

Balance specs (`balanceProfiles` with `multiply`/`add`) are non-idempotent when reading from the working tree — re-applying compounds the multipliers. The tool avoids this by passing `--source-ref HEAD` (the server repo's last committed state) to every apply run. Reads go through the git object database at that commit; writes still land on the working tree.

**Re-migration after spec changes:** If you need to re-apply a patch after fixing a spec, you need a clean working tree first so HEAD is still the correct baseline:

```bash
git -C <server_datasheet> checkout .
python reforged/tools/migrate/migrate.py --patch 001
```

## Supported Entity Schemas

The tool detects top-level YAML keys and maps them to sync-config entities:

| YAML Key | Sync Entity | Synced to Client |
|----------|-------------|------------------|
| `items` | ItemData | Yes |
| `equipment` | EquipmentData | Yes |
| `evolutions` | EquipmentEvolutionData | Yes |
| `evolutionPaths` | EquipmentEvolutionData | Yes |
| `equipmentInheritance` | EquipmentInheritanceData | Yes |
| `itemProduceRecipes` | ItemProduceRecipeData | Yes |
| `materialEnchants` | MaterialEnchantData | Yes |
| `enchants` | EquipmentEnchantData | Yes |
| `enchantPassivityCategories` | EquipmentEnchantData | Yes |
| `itemStrings` | StrSheet_Item | Yes |
| `passivities` | Passivity | Yes |
| `passivityStrings` | StrSheet_Passivity | Yes |
| `gachaItems` | Gacha | Yes |
| `rawStoneItems` | RawStoneItems | Yes |
| `collections` | CollectionData | Yes |
| `abnormalities` | Abnormality | Yes |
| `customizingItems` | CustomizingItems | Yes |
| `npcStrings` | StrSheet_Npc | Yes |
| `buyMenuLists` | BuyMenuList | Yes |
| `commonSkills` | SkillData | Yes |
| `userSkills` | SkillData | Yes |
| `npcSkills` | SkillData | Yes |
| `npcs` | — | No (server-only) |
| `ai` | — | No (server-only) |
| `balanceProfiles` | — | No (server-only NpcData; SkillData added automatically when `skills:` section present) |
| `cCompensations` | — | No (server-only) |
| `eCompensations` | — | No (server-only) |
| `fCompensations` | — | No (server-only) |
| `iCompensations` | — | No (server-only) |
| `customizingItemBags` | — | No (server-only) |
| `exchanges` | — | No (server-only) |
| `villagerMenuItems` | — | No (server-only) |
| `buyLists` | — | No (server-only) |

Server-only schemas are reported in the summary but excluded from client sync.

## Path Resolution

Paths are read from `reforged/.references`:

| Key | Used For |
|-----|----------|
| `dsl_cli` | DSL CLI binary path |
| `server_datasheet` | `--path` argument for `dsl apply`; also the git repo used for HEAD resolution |

## Output Example

```
Patch 001 — 38 specs + 19 sub-specs (57 total)
Baseline: HEAD → a1b2c3d4e5f6

[1/57] 00-enchant-system.yaml  →  applied (43 operations)
[2/57] 01-armor-standardize.yaml  →  applied (61 operations)
[3/57] 01-weapon-standardize.yaml  →  applied (23 operations)
...

Run complete: 57 applied, 0 failed, 1842 operation(s), 0 warning(s).
Manifest: 47 modified, 0 deleted -> .manifests/001/run.json

── Summary ──
Entities modified: CollectionData, EquipmentData, ItemData, ...
Server-only: balanceProfiles, npcs (no sync needed)

── Client Sync ──
Syncing: CollectionData, EquipmentData, ItemData, ...
Narrowing: 1 manifest, 47 modified file(s)
✓ Sync complete
```

## Preflight `nul` Check

Before applying any spec the tool walks the server datasheet tree and warns if any `nul` files are present:

```
⚠ Warning: 1 'nul' file(s) found in server datasheet (will block robocopy push):
    D:\dev\mmogate\tera92\server\Datasheet\nul
  Delete with: python -c "import os; os.remove(r'\\\\?\\<full-path>')"
```

`nul` is a Windows reserved filename; it can be created by accidental shell redirections on Windows (e.g., `> nul` without the right quoting). Robocopy's retry loop on this file can hang the deploy step for minutes without surfacing the cause. The preflight warning is informational — the tool does not auto-delete these files since they may be intentional. Use the `\\?\` extended-path trick in the suggested command to delete them safely.

## Full Deploy Pipeline

After running the migration tool, two additional steps push changes to the live server:

**Pack client DataCenter:**
```bash
# Run enc_EUR.bat from client_pack_dir (from .references)
D:\dev\mmogate\tera92\client-dc\enc_EUR.bat
```

Or using novadrop-dc directly (PowerShell):
```powershell
Set-Location '<client_pack_dir>'
.\novadrop-dc_92.04\novadrop-dc pack `
  --encryption-key 7533835567F31B7C8BF9321CF7C67A07 `
  --encryption-iv 1A2DE14F51A8AD426FEAEB4AC3CB705C `
  DataCenter_Final_EUR DataCenter_Final_EUR.dat
```

**Push to server share:**
```bash
robocopy "<server_datasheet>" "\\tera-dev.mmogate.local\Datasheet" /MIR /IS /NFL /NDL
```

Replace `<server_datasheet>` and `<client_pack_dir>` with values from `.references`.

Use `/deploy-patch` to run the full pipeline as a slash command.

## Clean Re-migration

When specs change and you need to re-apply a patch from scratch (e.g., after fixing a spec bug), use this workflow to revert both server and client to vanilla state, re-run the migration, and repack the client.

**Prerequisites:** Both `server_datasheet` and `client_datacenter` paths (from `.references`) must be git repositories with a clean baseline commit.

```bash
# 1. Revert server datasheets to vanilla
cd <server_datasheet>
git checkout .

# 2. Revert client DataCenter to vanilla
cd <client_datacenter>/..
git checkout .

# 3. Re-run migration (from project root)
python reforged/tools/migrate/migrate.py --patch 001

# 4. Pack client DataCenter
cd <client_pack_dir>
novadrop-dc_92.04/novadrop-dc pack \
  --encryption-key 7533835567F31B7C8BF9321CF7C67A07 \
  --encryption-iv 1A2DE14F51A8AD426FEAEB4AC3CB705C \
  DataCenter_Final_EUR DataCenter_Final_EUR.dat
```

Replace `<server_datasheet>`, `<client_datacenter>`, and `<client_pack_dir>` with the values from `.references`.

Alternatively, run `enc_EUR.bat` in the `client_pack_dir` for step 4.

## Adding New Entity Schemas

When new entity types are added to specs and/or `sync-config.yaml`:

1. Add the YAML key and sync entity name to `ENTITY_SYNC_MAP` in `migrate.py`
2. Use `None` for server-only schemas that should not be synced
3. If an entity has inline nested entities (like `enchantPassivityCategories` with inline `passivities`), add it to `INLINE_STRING_SYNC` with a list of implied sync entities
