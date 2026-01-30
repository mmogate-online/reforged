# DataSheetLang Content Project

YAML specs for TERA game content using DataSheetLang DSL.

## Setup

Each developer must create a `.references` file in this folder with local paths. Copy `.references.example` and fill in your paths.

The `.references` file uses `key=value` format. Read it to resolve any path referenced in this document or workflow guides.

## Project Structure

- `reforged/` - Shared/public git repository (specs, packages, tools, configs)
- Root files - Local dev machine specific files

## CLI Usage

```bash
# Apply spec to server datasheets
dsl apply <spec.yaml> --path "<server_datasheet>"

# Validate spec
dsl validate <spec.yaml> --path "<server_datasheet>"

# Client sync (after server apply)
dsl sync --config reforged\config\sync-config.yaml -e <Entity>
```

Replace `<server_datasheet>` with the `server_datasheet` value from `.references`.

## DataSheetLang Documentation

- **Online**: https://dsl.mmogate.online/guides/quickstart/
- **Local** (if available): see `dsl_docs_enduser` and `dsl_docs_internal` in `.references`

## Building DSL from Source

When the DSL tool needs to be rebuilt (e.g., after changes to datasheetlang project):

```powershell
cd <dsl_source>
dotnet publish -c Release -r win-x64 -o <project_root> /p:DebugType=None /p:DebugSymbols=false
```

Replace `<dsl_source>` with the `dsl_source` value and `<project_root>` with the `project_root` value from `.references`.

This builds with native AOT support for faster execution and excludes PDB files.

**IMPORTANT:** Claude Code must invoke PowerShell explicitly for this build (the `/p:` flag fails in the default shell):
```bash
powershell -Command "cd <dsl_source>; dotnet publish -c Release -r win-x64 -o <project_root> /p:DebugType=None /p:DebugSymbols=false"
```
Non-AOT builds are forbidden as they pollute the folder with DLLs and localization folders.

## Workflows

| System | Workflow Guide | Tool Path |
|--------|---------------|-----------|
| General Pipeline | `reforged/docs/workflows/GENERAL_WORKFLOW.md` | — |
| Enchant Materials | `reforged/docs/workflows/ENCHANT_MATERIALS.md` | `reforged/tools/enchant-materials/` |
| Gear Infusion | `reforged/tools/gear-infusion/README.md` | `reforged/tools/gear-infusion/` |
| Infusion Loot | `reforged/tools/infusion-loot/README.md` | `reforged/tools/infusion-loot/` |

## Error Reporting

When DSL behavior differs from documentation, file error report with:
- Spec YAML causing the issue
- Expected vs actual behavior
- Relevant doc reference from starlight docs
