# Reforged Server Content

This repository contains the game content specifications for Reforged Server. Every stat, loot table, enchant chain, item progression, and merchant inventory applied to the server originates here as a versioned, reviewable change.

Content is authored in DatasheetLang, a domain-specific language built for declarative game datasheet management, and applied through an automated pipeline.

---

## How We Work

Content changes are expressed as spec files, validated before touching any datasheet, and applied through a repeatable pipeline. This makes patches reproducible across environments and keeps production from receiving anything untested.

Every change is a readable YAML file in version control, which means the history of the server is the history of this repository. The same pipeline that applies one spec applies a thousand, so adding new content systems is a matter of writing new specs.

### AI-Assisted Development

The project is built with AI-assisted workflows in mind. Two components keep agent output grounded:

- **MCP server** provides agents with live, queryable access to the actual server datasheet, so decisions are based on real data.
- **DSL validation** checks every spec against the schema before it can be applied, acting as a correctness barrier against malformed or incorrect output.

As the project grows, the domain knowledge in these tools and the validation rules covering game logic will expand. The long-term goal is to let the community participate more directly in content decisions, with tooling capable of catching mistakes automatically.

---

## Repository Structure

```
reforged/
├── packages/          # Reusable DSL modules (shared IDs, templates, definitions)
├── specs/
│   ├── patches/       # Versioned patch specs (000/, 001/, 002/, ...)
│   └── backlog/       # Drafts and deferred work
├── tools/             # Python generators that produce specs from source data
├── config/            # Gear formulas, sync config, tool-specific source data
├── docs/              # Design documents, migration guides, workflow references
└── datasheetlang.yml  # DSL workspace config (package registry, schema aliases)
```

### packages/

Reusable DSL modules imported by specs. Packages encapsulate shared definitions such as ID variables, stat templates, and enchant structures so specs stay concise and consistent. The available packages are listed in `datasheetlang.yml`.

### specs/patches/

Patches are numbered folders (`000`, `001`, `002`, ...) containing ordered YAML spec files. Specs within a patch are prefixed with a two-digit number to control application order.

```
specs/patches/001/
├── 01-reaper-weapons.yaml
├── 02-evolutions.yaml
├── 03-flawless-mythic-grade.yaml
├── ...
└── loot/
    ├── c-compensation/    # Per-zone compensation loot tables
    └── e-compensation/
```

### tools/

Python generator scripts that convert structured source data (CSV, XLSX) into DSL specs. Each tool lives in its own subfolder with a `README.md` and accepts a `--patch` argument so output lands in the correct patch folder.

| Tool | Purpose |
|------|---------|
| `enchant-materials` | Generate enchant material definitions |
| `gear-enchant-sync` | Bulk-link enchant IDs across all equipment items |
| `gear-evolution` | Generate evolution path specs for gear progression |
| `gear-infusion` | Generate infusion passivity and item specs |
| `gear-tiers` | Generate gear tier and item progression configuration |
| `infusion-loot` | Generate zone loot tables for infusion fodder |
| `zone-loot` | Extract NPC data and generate zone compensation tables |
| `potential-unlock` | Generate potential unlock passivity definitions |
| `migrate` | Apply all specs in a patch, detect changed entities, and sync to client |

---

## How a Patch Works

```
Source data  ->  Generate  ->  Apply  ->  Sync  ->  Pack  ->  Deploy
 (CSV / XLSX)    (Python)      (DSL)     (DSL)    (.bat)
```

1. Source data is edited (CSV, XLSX) in `config/<tool>/`
2. A generator script converts it into YAML specs under `specs/patches/<NNN>/`
3. `dsl apply` validates and writes each spec into the server datasheet
4. `dsl sync` propagates server-side changes to the client DataCenter
5. `pack-client.bat` packs the client DataCenter for distribution
6. Files are deployed to the running server

The `migrate` tool runs steps 3 and 4 for an entire patch in one command, detecting which entities changed and syncing only those.

---

## Getting Started

### Prerequisites

- Python 3.13+
- `pip install openpyxl`
- DatasheetLang CLI (distributed separately)

### Local Setup

Create a `.references` file in the repository root by copying `.references.example` and filling in your local paths:

```
project_root=D:\path\to\reforged-server-content
server_datasheet=D:\path\to\server\Datasheet
client_datacenter=D:\path\to\client-dc\DataCenter_Final_EUR
dsl_cli=D:\path\to\reforged-server-content\dsl.exe
...
```

This file is machine-specific and not committed to the repository.

---

## Documentation

| Topic | Location |
|-------|----------|
| DatasheetLang documentation | [dsl.mmogate.online](https://dsl.mmogate.online) |
| Gear infusion system | `tools/gear-infusion/README.md` |
| Infusion loot tables | `tools/infusion-loot/README.md` |
| Patch migration tooling | `tools/migrate/README.md` |
| Patch 001 scope | `docs/patch-001-scope.md` |
