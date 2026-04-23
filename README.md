# Reforged Server Content

This repository contains the game content specifications for Reforged Server. Every stat, loot table, enchant chain, item progression, and merchant inventory applied to the server originates here as a versioned, reviewable change.

Content is authored in [DatasheetLang](https://dsl.mmogate.online), a domain-specific language built for declarative game datasheet management, and applied through an automated pipeline.

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

The `tools/` folder contains two kinds of scripts with very different roles.

**`migrate/`** is the primary workflow tool. It applies all specs in a patch to the server datasheet and syncs affected entities to the client DataCenter. This is what you run when deploying a patch.

**Spec generators** are development-time scripts that convert structured source data (CSV, XLSX) into DSL spec files. They are only needed when the underlying input data changes and specs need to be regenerated. Once the specs exist in `specs/patches/`, they are the deliverable — the generators are not part of the apply workflow.

| Tool | Input | Output |
|------|-------|--------|
| `enchant-materials` | `enchant.xlsx` | Enchant material and item link specs |
| `gear-enchant-sync` | `gear_progression.csv` | Gear enchant link spec; also regenerates `equipment-item-ids` package |
| `gear-evolution` | `gear_progression.csv` | Per-gear-set evolution path specs |
| `gear-infusion` | `gear_infusion_passivity.csv` | Infusion passivity and item specs |
| `infusion-loot` | `loot_tier_rates.csv`, `zone_loot_config.csv` | Zone infusion loot specs |
| `zone-loot` | Zone/NPC CSVs | Zone compensation loot scaffold specs |
| `potential-unlock` | `gear_progression.csv` + live server XML | Potential unlock scroll, gear, and evolution specs |

---

## How a Patch Works

The normal workflow starts with the specs that already exist in the repository:

```
Apply (DSL)  ->  Sync (DSL)  ->  Pack  ->  Deploy
```

```bash
# Apply all specs from patch 001 and sync to client
py tools/migrate/migrate.py --patch 001
```

The migrate tool applies every spec in `specs/patches/001/` in order, detects which server entities changed, and syncs only those to the client DataCenter.

**Regenerating specs from source data** is a separate, less frequent activity. It is only needed when the input CSV or XLSX changes:

```
Source data  ->  Generate (Python)  ->  specs/patches/{NNN}/
 (CSV / XLSX)                             (committed to repo)
```

Each generator in `tools/` has its own `README.md` with usage instructions.

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
| Gear infusion system | `tools/gear-infusion/README.md` |
| Infusion loot tables | `tools/infusion-loot/README.md` |
| Patch migration tooling | `tools/migrate/README.md` |
| Patch 001 scope | `docs/patch-001-scope.md` |
