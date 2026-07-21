---
name: apply-spec
description: Use when validating or applying a DSL spec to server datasheets. Resolves paths from .references, runs validate-before-apply, and optionally syncs to client.
disable-model-invocation: false
user-invocable: true
argument-hint: [spec-path]
---

# Apply a DSL Spec

Follow these steps when validating or applying a spec. Do not skip validation.

**CRITICAL: never raw-apply a single patch spec.** When a `--source-ref` is
configured (this project pins it to the server repo baseline HEAD), `dsl apply`
REPLAYS the target files from that ref and applies only the specs given on the
command line. A single-spec apply therefore RESETS every file it touches to
baseline and silently wipes the changes every sibling spec made to those files
(2026-07-19 incident: applying `03-iod-spawn-removals.yaml` alone reset
`TerritoryData_13.xml` to HEAD and erased spec 02's 451 restored spawn ops; the
regressed file was deployed three times before detection). For any spec that
lives under `specs/patches/<patch>/`, apply THE WHOLE PATCH with the migrate
tool: `python reforged/tools/migrate/migrate.py --patch <patch> [--skip-sync]`.
Raw single-spec `dsl apply` is safe only for a spec whose target files no other
spec touches, or against a scratch path with no shared-file siblings.

## 1. Resolve paths

Read `.references` in the project root (`reforged/.references`). Parse as `key=value` lines. You need:

| Key | Purpose |
|-----|---------|
| `project_root` | Where `dsl.exe` lives |
| `server_datasheet` | Target datasheet XML directory |

The DSL binary is at `<project_root>/dsl.exe`. Always use the full absolute path — never `./dsl` or relative paths.

## 2. Determine the spec path

If the user provides a spec path, use it directly. If they mention a spec by name or number, find it under `specs/`. Spec files live in:

```
specs/patches/<patch>/          — patch-specific specs (numbered for execution order)
specs/patches/<patch>/loot/     — loot table specs (zone files)
specs/patches/<patch>/evolutions/ — evolution path specs
specs/backlog/                  — pending/future specs
```

## 3. Validate first

Always validate before applying:

```bash
"<project_root>/dsl.exe" validate <spec-path> --path "<server_datasheet>"
```

Run this from the `reforged/` directory. Check for:
- **Valid**: proceed to apply
- **Errors (E###)**: fix before applying, do not apply broken specs

## 4. Apply

Only after validation passes:

```bash
"<project_root>/dsl.exe" apply <spec-path> --path "<server_datasheet>"
```

Report the number of operations applied.

## 5. Sync to client (if requested)

If the user asks to sync or deploy, run the entity sync:

```bash
"<project_root>/dsl.exe" sync --config "reforged/config/sync-config.yaml" -e <Entity1> -e <Entity2>
```

Common entity names: `ItemData`, `EquipmentData`, `EnchantData`, `MaterialEnchantData`, `PassivityData`, `QuestData`.

Choose entities based on what the spec modifies. If unsure, ask the user which entities to sync.

## 6. Pack client (if requested)

Client packing requires PowerShell. Resolve `client_pack_dir` from `.references`:

```bash
powershell -Command "Set-Location '<client_pack_dir>'; & '.\novadrop-dc_92.04\novadrop-dc' pack --encryption-key 7533835567F31B7C8BF9321CF7C67A07 --encryption-iv 1A2DE14F51A8AD426FEAEB4AC3CB705C DataCenter_Final_EUR DataCenter_Final_EUR.dat"
```

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| E535 | Exported variable not found | Package sub-file missing `exports: variables:` or index.yml missing `use: variables:` |
| E536 | Imported variable not exported by source | Variable name not in source package's exports list |
| E520 | Unknown variable reference | `$VAR_NAME` used but not imported — add to `use: variables:` in imports |
| E103 | Invalid property | Check the DSL schema docs for the entity type (see note below) |
| E200 | Missing required field | Check required attributes in the entity schema (see note below) |

**Schema docs location:** resolve `dsl_docs_enduser` from `.references`, then read `schemas/<category>/<entity>.mdx` for the entity type.

## Lessons

### Semantic-diff a NEW sync entity's output against client HEAD before accepting it
- **Date/source:** 2026-07-19: `dsl sync -e NewWorldMapData` (entity newly added to sync-config for the Tower Base minimap fix); a Python semantic diff of the projection vs the client-dc git HEAD showed 37 curated client-only markers deleted game-wide (guild boards, dungeon entrances, brokers), on top of the intended addition.
- **Why:** monolithic sync is a full-file replace of the client file with the XSD-filtered server projection. "Server is source of truth" does not hold at file granularity for families where the publisher curated the client copy (extra markers, patched attributes); the sync silently deletes that curation. A single XSD-invalid server row also aborts the whole entity sync with E650 (server section 9034 lacked height/left/top; fixed by a spec backfill op using the client's own values).
- **Apply:** when adding a sync-config entity for a family never synced before, run the sync, then diff the written client file against git HEAD semantically (parse both, compare by id hierarchy), not just by eyeballing the textual diff. If client-only content would be deleted, set `merge: merge-by-id` (Monolithic strategy only) with `merge_key_attributes` on the entity: it preserves client-only siblings while server records win on match (delivered 2026-07-19; see tools/client-sync.mdx "Merge modes" in the end-user docs; NewWorldMapData is the live example in sync-config). Even with merge-by-id, review the "changed" entries of the semantic diff: server-wins overwrites can surface bad hand-edited server rows (e.g. section 9053 pointed at a MapDefine absent from the client; fixed by realigning the SERVER row to the client-proven values via a spec op, precedent in spec 13).
