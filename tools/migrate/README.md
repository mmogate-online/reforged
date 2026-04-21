# Patch Migration Tool

Applies all specs from a patch in sequence and syncs affected entities to the client DataCenter, using DSL apply manifests to narrow the sync to exactly the files each spec touched.

## Overview

The migration tool automates the full apply→sync pipeline for a patch. It discovers all YAML specs under a patch folder, applies them sequentially via `dsl apply --manifest-out`, and then runs a single `dsl sync --from-manifest …` that regenerates only the client shards whose server sources were actually modified.

Individual spec failures (expected for zones without XML) do not stop the pipeline. Sync failures are fatal.

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

# Verbose output (full DSL output + failed spec list)
python reforged/tools/migrate/migrate.py --patch 001 --verbose
```

## Parameters

| Flag | Required | Description |
|------|----------|-------------|
| `--patch` | Yes | Patch folder name under `reforged/specs/patches/` |
| `--dry-run` | No | Pass `--dry-run` to `dsl apply` and `dsl sync`; no files written, no manifests emitted |
| `--skip-sync` | No | Apply specs only, skip client sync; no manifests emitted |
| `--no-narrow` | No | Emit apply manifests for inspection but run broad sync without `--from-manifest` (escape hatch) |
| `--verbose` | No | Show detailed DSL output and list all failed specs in summary |

## Execution Order

1. **Preflight** — scan server datasheet tree for Windows-reserved `nul` files and warn (they block robocopy later)
2. **Prepare manifest dir** — wipe `reforged/tools/migrate/.manifests/<patch>/` (gitignored)
3. **Discover** — recursively scans `reforged/specs/patches/{patch}/` for `*.yaml` files
4. **Sort** — `sorted()` on relative paths; numbered prefixes (`01-`, `02-`) control order; subdirectory files sort after root-level specs
5. **Apply** — runs `dsl apply <spec> --path <server_datasheet> --manifest-out <path>` for each spec; collects the emitted manifest for successful specs
6. **Detect entities** — parses each spec to extract top-level entity keys for the sync `-e` arguments
7. **Sync** — runs `dsl sync -e Entity1 -e Entity2 ... --from-manifest m1.json --from-manifest m2.json ...` for the union of per-spec manifests

## Manifest Directory

Each run emits one manifest per successfully-applied spec at:

```
reforged/tools/migrate/.manifests/<patch>/<spec-slug>.json
```

The slug mirrors the spec's relative path under the patch folder, with `/` replaced by `_` and the `.yaml` extension dropped. Example:

```
specs/patches/001/loot/c-compensation/zone-0013-iod.yaml
 → .manifests/001/loot_c-compensation_zone-0013-iod.json
```

The directory is gitignored, wiped at the start of each run, and persisted until the next run so you can inspect what the tool saw when diagnosing a failure. Manifest JSON is emitted by the DSL (`dsl apply --manifest-out`) and contains the list of server files the apply actually wrote.

## Sync-Skip Conditions

The tool skips the sync phase in several cases. Each prints a clear message and returns the documented exit code:

| Condition | Exit | Message |
|-----------|------|---------|
| `--skip-sync` passed | 0 | `Sync skipped (--skip-sync)` |
| No specs declared a syncable entity | 0 | `No syncable entities — nothing to sync` |
| Every spec apply failed | 1 | `All specs failed — sync skipped` |
| Applies succeeded but wrote nothing (idempotent) | 0 | `No server-side file changes — sync skipped` |

The last case is common when re-running a patch against already-applied server state — the apply reports "N operations successful" but produces no file diffs. With manifest narrowing the tool detects this and skips sync entirely rather than spending time regenerating client shards that won't change. Use `--no-narrow` to force the broad sync anyway.

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
| `server_datasheet` | `--path` argument for `dsl apply` |

## Output Example

```
Patch 000 — 7 specs (7 total)

[1/7] 00-iod-training-bomb.yaml
        ✓ Applied 1 operations (1 successful, 0 failed)
[2/7] 01-iod-garrison-quest.yaml
        ✓ Applied 7 operations (7 successful, 0 failed)
[3/7] 02-iod-skill-quest-strings.yaml
        ✓ Applied 10 operations (10 successful, 0 failed)
...

── Summary ──
Applied: 7 specs
Entities modified: CollectionData, ItemData, SkillData, StrSheet_Item

── Client Sync ──
Syncing: CollectionData, ItemData, SkillData, StrSheet_Item
Narrowing: 7 manifest(s), 12 modified file(s)
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
