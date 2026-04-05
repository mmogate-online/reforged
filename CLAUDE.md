# DataSheetLang Content Project

YAML specs for TERA game content using DataSheetLang DSL.

## Prerequisites

- **Python 3.13+** — install via `winget install Python.Python.3.13` (restart terminal after install)
- **openpyxl** — install via `pip install openpyxl`

## Setup

Each developer must create a `.references` file in this folder with local paths. Copy `.references.example` and fill in your paths.

The `.references` file uses `key=value` format. Read it to resolve any path referenced in this document or workflow guides.

## Project Structure

- `reforged/` - Shared/public git repository (specs, packages, tools, configs)
- Root files - Local dev machine specific files

## Packages

Packages are reusable modules located in `packages/`. Each package folder must contain an `index.yml` file.

**Important:** New packages must be registered in `datasheetlang.yml` under `workspace.packages`:

```yaml
workspace:
  packages:
    my-new-package: "./packages/my-new-package"
```

Without registration, DSL will fail with `Unknown package reference` error when specs try to import from the package.

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

The DSL tool is documented in a Starlight project at `dsl_docs_enduser` in `.references` (`starlight/src/content/docs/`). Start from `index.mdx`; subdirs: `guides/` (quickstart, definitions, packages, recipes), `reference/` (CLI, syntax, operations, filters, etc.), `schemas/` (per-entity schemas), `tools/`.

Files are `.mdx` (MDX) — readable directly; ignore JSX component tags, focus on the markdown content.

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
| General Pipeline & Tool Development | `reforged/docs/workflows/GENERAL_WORKFLOW.md` | — |
| Enchant Materials | `reforged/docs/workflows/ENCHANT_MATERIALS.md` | `reforged/tools/enchant-materials/` |
| Gear Infusion | `reforged/tools/gear-infusion/README.md` | `reforged/tools/gear-infusion/` |
| Infusion Loot | `reforged/tools/infusion-loot/README.md` | `reforged/tools/infusion-loot/` |
| Patch Migration | `reforged/tools/migrate/README.md` | `reforged/tools/migrate/` |

## Domain Knowledge

The source of truth is the `datasheet-domain` Starlight project. `domain_docs` in `.references` resolves to its `src/content/docs/` root — raw markdown files readable directly, no HTTP needed.

**Navigation:** Start from `index.md` in that folder for an overview. Content is organized into two subdirectories:
- `entities/` — system docs (item, enchant, passivity, loot, NPC, evolution, quest, etc.)
- `reference/` — lookup tables (ID ranges, type codes, class data, grade tiers, etc.)

Glob the directory to discover available files rather than assuming specific filenames.


## Datasheet MCP Server

The `datasheet` MCP server provides read-only access to server datasheet XML files. Use these tools instead of writing Python XML-parsing scripts:

| Tool | Use When |
|------|----------|
| `lookup` | Get a single entity by ID |
| `search` | Find entities by attribute filters |
| `profile_item` | Full item profile (equipment, enchant chain, passivities, strings) |
| `find_similar_items` | Find items sharing attributes with a reference item |
| `compare` | Attribute diff between two entities |
| `find_free_ids` | Find unused ID ranges |
| `trace_enchant_chain` | Trace enchant → categories → passivities |
| `trace_evolution` | Find evolution paths for an item |
| `check_references` | Validate cross-entity links |
| `audit_zone_loot` | All NPCs + loot tables in a zone |
| `trace_item_dependencies` | Reverse lookup — what references this item |
| `describe_entity` | Discover entity XML structure and attribute distributions |
| `search_text` | Full-text search across string tables |
| `count` | Count entities with optional grouping |
| `scan_zones` | Search across all zone-partitioned files |
| `batch_lookup` | Multiple entities by ID with attribute projection |

## Skills

Project skills live in `.claude/skills/`. Each skill is a folder with a `SKILL.md` file. Skills are auto-loaded when relevant to the conversation and invocable via `/skill-name`.

**Before creating a new skill:** Check existing skills in `.claude/skills/` to avoid duplication.

**Conventions for this project:**
- `disable-model-invocation: false` — let Claude auto-invoke when relevant
- `user-invocable: true` — available in `/` menu
- No `context: fork` — skills are reference/guidance, not orchestration tasks
- Include `argument-hint` when the skill accepts parameters

**Official reference:** https://docs.anthropic.com/en/docs/claude-code/skills

## DSL Issues & Feature Requests

Agents in this project are end users of the DSL tool. Do not attempt to fix DSL bugs or implement missing features. Instead, log them in `docs/dsl-requests.md` with:
- Spec YAML or command that triggered the issue
- Expected vs actual behavior
- Relevant doc reference from the end-user starlight docs

The DSL dev team will handle requests from that file separately.
