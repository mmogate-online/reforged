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

The `datasheet` MCP server provides read-only access to server datasheet XML files. Use it instead of writing Python XML-parsing scripts. Available tools are listed in the system-reminder at conversation start.

## Skills

Project skills live in `.claude/skills/`. Each skill is a folder with a `SKILL.md` file. Skills are auto-loaded when relevant to the conversation and invocable via `/skill-name`.

**Before creating a new skill:** Check existing skills in `.claude/skills/` to avoid duplication.

**Conventions for this project:**
- `disable-model-invocation: false` — let Claude auto-invoke when relevant
- `user-invocable: true` — available in `/` menu
- No `context: fork` — skills are reference/guidance, not orchestration tasks
- Include `argument-hint` when the skill accepts parameters

**Official reference:** https://docs.anthropic.com/en/docs/claude-code/skills

## Patch 001 Zone Scope

When doing any research, loot work, merchant audits, or NPC queries scoped to patch 001, always include **all zones defined in `reforged/docs/patch-001-scope.md`** — hunting zones, hub cities, and dungeons. Do not query hunting zones in isolation; hub cities are part of the content scope.

## Client DC Migration — Schema Error Handling

When migrating client DC files and a schema error or incompatibility is encountered (packer rejects a file, XSD validation fails, required attributes missing):

1. **Never revert the migrated file and move on.** Reverting a change without resolving the underlying content problem is silent data loss — the task is not done.
2. **Investigate first.** Compare the server file counterpart to understand whether the content difference is real or just a schema format issue. A DSL sync from the server file is often the correct fix (server is source of truth; XSD filtering produces compliant output).
3. **If DSL sync was already used and the error persists**, consider whether it is a DSL bug and log it in `docs/dsl-requests/`.
4. **If the issue cannot be resolved**, stop and report it explicitly. Do not mark the task complete.

## DSL Issues & Feature Requests

Agents in this project are end users of the DSL tool. Do not attempt to fix DSL bugs or implement missing features. Instead, log them in `docs/dsl-requests/` as individual files named `YYYY-MM-DD-<topic>.md`. Multiple issues discovered during the same task can share a single file. Each entry should include:
- Spec YAML or command that triggered the issue
- Expected vs actual behavior
- Relevant doc reference from the end-user starlight docs

The DSL dev team will handle requests from that directory separately.

## Progress Tracking

Two files track project state across all patches and correlated projects:
- `reforged/CHANGELOG.md` — append-only historical record (newest first)
- `reforged/STATUS.md` — living current-state dashboard (updated in place)

**Invoke `/log-progress` immediately when:**
- A migration phase entry in any `docs/migrations/*/progress.md` transitions to Done
- A batch of patch specs is applied **and** validated end-to-end
- Phase 4 (validation) confirms a migration is correct

**Proactively ask the user "Should I log this progress?" when:**
- The session is wrapping up and meaningful work was done without a clear phase boundary
- A DSL fix or MCP capability is noted that unblocked content work
- Work spans multiple areas and it's unclear if the threshold has been crossed

**Never log** exploratory research, specs written but not yet applied, or bugs discovered but not resolved.
