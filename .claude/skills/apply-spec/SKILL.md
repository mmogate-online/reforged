---
name: apply-spec
description: Use when validating or applying a DSL spec to server datasheets. Resolves paths from .references, runs validate-before-apply, and optionally syncs to client.
disable-model-invocation: false
user-invocable: true
argument-hint: [spec-path]
---

# Apply a DSL Spec

Follow these steps when validating or applying a spec. Do not skip validation.

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
| E103 | Invalid property | Check the DSL schema docs for the entity type |
| E200 | Missing required field | Check required attributes in the entity schema |
