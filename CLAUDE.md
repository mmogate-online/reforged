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

Packages are reusable modules located in `packages/`. Each package folder must contain an `index.yml` file. See `packages/README.md` for the full index of available packages, their types, and dependency relationships.

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
| Dev Server Deploy | `reforged/tools/deploy-dev/README.md` | `reforged/tools/deploy-dev/` |
| Content Restoration (old client / v31) | `reforged/tools/dc-restore/README.md` | `reforged/tools/dc-restore/` |
| Client Deploy (pack, install, CF publish) | `reforged/tools/deploy-client/README.md` | `reforged/tools/deploy-client/` |

## Domain Knowledge

The source of truth is the `datasheet-domain` Starlight project. `domain_docs` in `.references` resolves to its `src/content/docs/` root — raw markdown files readable directly, no HTTP needed.

**Navigation:** Start from the knowledge base index at `D:\dev\github-vperim\datasheet-domain\.claude\CLAUDE.md` — a curated flat table mapping every documented topic to its exact file path. Use it to find the right doc directly rather than globbing. Content is organized into two subdirectories:
- `entities/` — system docs (item, enchant, passivity, loot, NPC, evolution, quest, etc.)
- `reference/` — lookup tables (ID ranges, type codes, class data, grade tiers, etc.)


## Content Framework

The design source of truth for progression, economy, currencies, seasons, reward budgets, PvP, and monetization is the `reforged-content-framework` repo. Resolve its path from the `content_framework` key in `.references`.

It is a set of numbered design docs (00-overview through 10-social-architecture, plus 99-open-questions) with locked framework invariants listed in its CLAUDE.md (examples: seasonal power wipes, strict currency separation, cosmetic-only monetization).

Before authoring or changing any content that affects balance, rewards, currencies, drop economies, or progression pacing, consult the relevant framework doc and do not violate its locked invariants. If a requested change conflicts with an invariant, surface the conflict instead of proceeding.

Rule of thumb: the framework answers "why and how much" (design intent, budgets, pacing); the datasheet MCP and datasheet-domain docs answer "what exists and how it is encoded".

## Datasheet MCP Servers

Two read-only MCP servers provide access to datasheet XML files. Use them instead of writing Python XML-parsing scripts.

- `datasheet-v92`: current server state. Source of truth for what exists now, and the validation target after applying specs.
- `datasheet-v31`: original TERA v31 data. Read-only historical reference; never use v31 output as direct input to a DSL spec.

The `domain-research` skill documents which server to use for which question.

Agents are end users of the MCP servers. Do not attempt to fix MCP bugs. Log gaps, errors, and output-format problems in `docs/mcp-requests/` as `YYYY-MM-DD-<topic>.md` files (same convention as `docs/dsl-requests/`); the MCP dev team handles them separately.

## Dev Game Server

Content changes are tested against the dev game server deployment. Infrastructure, SSH access, and operations are documented in the private `reforged-deploy` repo; resolve its local path from the `deploy_repo` key in `.references`.

- Connection details resolve from `.references`: `dev_server_ssh` (an SSH alias defined in the developer's ssh config) and `dev_server_datasheet` (remote datasheet path on the dev game server).
- The game server loads datasheets at process startup only; after deploying datasheet changes, the world server must be restarted. There is no hot reload.
- Deploy working-tree datasheet changes with `python reforged/tools/deploy-dev/deploy_dev.py` (or `/deploy-dev`); see `reforged/tools/deploy-dev/README.md`. Overlays become durable only when the local datasheet repo is committed and pushed to the payload repo (the promotion step).
- The legacy server-share push (`server_share` key, UNC share targets) is discontinued. Do not add share-based deploy steps to any doc, tool, or command.

**Public repo rule:** this repository is public on GitHub. Never commit hostnames, IPs, usernames, key paths, ports, or credentials. Environment specifics live only in `.references` (gitignored) and in the private `reforged-deploy` repo. Docs, tools, and commands reference `.references` keys, never literal values.

## Skills

Project skills live in `.claude/skills/`. Each skill is a folder with a `SKILL.md` file. Skills are auto-loaded when relevant to the conversation and invocable via `/skill-name`.

**Before creating a new skill:** Check existing skills in `.claude/skills/` to avoid duplication, then follow the binding authoring standard in `.claude/skills/skill-authoring/SKILL.md`.

**Lessons learned:** When a session resolves a trap, quirk, or repeated correction that future agents must not rediscover, invoke `/learn` to capture it into the owning skill (or route it to domain docs / dsl-requests). Invoke `/learn curate` periodically to merge, promote, or retire accumulated lessons.

**Conventions for this project:**
- `disable-model-invocation: false` — let Claude auto-invoke when relevant
- `user-invocable: true` — available in `/` menu
- No `context: fork` — skills are reference/guidance, not orchestration tasks
- Include `argument-hint` when the skill accepts parameters

**Official reference:** https://docs.anthropic.com/en/docs/claude-code/skills

## Patch Zone Scope

Patch 001 (classic-restoration baseline): scope is defined in `reforged/docs/patch-001-scope.md`. Island of Dawn is five layered hunting zones (13, 64, 213, 313, 364) plus dungeon 436; always enumerate all layers, never just combat HZ 13.

Patch 002 (Reforged customizations): scope is defined in `reforged/docs/patch-002-scope.md`.

When doing any research, loot work, merchant audits, or NPC queries scoped to patch 002, always include **all zones in its scope doc** (hunting zones, hub cities, and dungeons). Do not query hunting zones in isolation; hub cities are part of the content scope.

## Client DC Migration — Schema Error Handling

When migrating client DC files and a schema error or incompatibility is encountered (packer rejects a file, XSD validation fails, required attributes missing):

1. **Never revert the migrated file and move on.** Reverting a change without resolving the underlying content problem is silent data loss — the task is not done.
2. **Investigate first.** Compare the server file counterpart to understand whether the content difference is real or just a schema format issue. A DSL sync from the server file is often the correct fix (server is source of truth; XSD filtering produces compliant output).
3. **If DSL sync was already used and the error persists**, consider whether it is a DSL bug and log it in `docs/dsl-requests/`.
4. **If the issue cannot be resolved**, stop and report it explicitly. Do not mark the task complete.

## Spec Authoring Rules

**Specs must be idempotent by default.** Always use `upsert` for create-style operations. Never use `create` unless explicitly instructed — `create` fails on re-runs, breaks manifest generation for the affected spec, and causes files to be silently omitted from server pushes.

## Patch Application Discipline (binding)

These rules keep the pipeline simple and make every apply a full-patch regression check.

1. **Apply and sync a patch only as a whole.** Always run `python reforged/tools/migrate/migrate.py --patch NNN` (full apply plus full sync). Never hand-pick a subset of specs or entities to apply/sync. A patch that adds new quests (or any new `IdSorted` client entity: `Quest`, `QuestDialog`) must sync with `--no-narrow`, because the default manifest-narrowed sync cannot insert a new shard into the sorted layout (E680); the broad sync renumbers the downstream shards correctly. `gen_npcloc.py --prune` remains a separate post-apply step whenever spawns change.
2. **Never commit the server or client datasheet repos (`server_datasheet`, `client_datacenter`) mid-patch.** The working tree holds the in-progress patch. Land exactly one "close patch NNN" commit per repo, only when the patch is fully applied, synced, and live-validated. That commit becomes the source-ref baseline the next patch develops against. Committing mid-patch shifts the baseline, defeats the from-baseline regression check, and forces error-prone segmented applies.
3. **Each new patch develops against the previous patch's closed (committed) baseline.** Patch specs are the reproducible source of truth; the committed repo state is the baseline they layer on.

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
