# Reforged Server Content - Project Structure

## Directory Layout

```
reforged-server-content/
├── dsl.exe                      # DataSheetLang CLI tool
├── pack-client.bat              # Pack client DataCenter
│
└── reforged/                    # Main content repository (git tracked)
    ├── .references              # Dev-specific local paths (gitignored)
    ├── .references.example      # Template for .references
    ├── CLAUDE.md                # AI assistant instructions
    │
    ├── config/                  # Configuration files
    │   └── sync-config.yaml     # Client sync configuration
    │
    ├── data/                    # Source data files (CSV, JSON, XLSX)
    │   ├── enchant.xlsx                   # Enchant probabilities & materials
    │   ├── gear_infusion_passivity.csv
    │   └── infusion_loot/
    │       ├── loot_tier_rates.csv      # Drop rates per content tier
    │       └── zone_loot_config.csv     # Zone-to-tier assignments
    │
    ├── docs/                    # Project documentation
    │   ├── PROJECT_STRUCTURE.md     # This file
    │   ├── INFUSION_LOOT_SYSTEM.md  # Loot distribution strategy
    │   ├── feature-requests/        # DSL feature requests
    │   └── workflows/               # Content workflow guides
    │       ├── GENERAL_WORKFLOW.md
    │       └── ENCHANT_MATERIALS.md
    │
    ├── specs/                   # YAML specification files
    │   ├── enchant-materials.yaml          # Generated
    │   ├── enchant-item-links.yaml         # Generated
    │   ├── gear-infusion-passivities.yaml  # Generated
    │   ├── gear-infusion-items.yaml        # Generated
    │   └── infusion-loot.yaml              # Generated
    │
    └── tools/                   # Generation scripts
        ├── enchant-materials/
        │   ├── generate_enchant_materials.py
        │   ├── generate.bat
        │   └── deploy.bat
        ├── gear-infusion/
        │   ├── generate_infusion.py
        │   └── README.md
        └── infusion-loot/
            ├── generate_infusion_loot.py
            └── README.md
```

## Data Flow

```
CSV Source Data
     │
     ▼
Python Generator Script
     │
     ├──► YAML Spec (passivities)
     │         │
     │         ▼
     │    dsl apply
     │         │
     │         ▼
     │    Server Datasheet XML
     │
     └──► YAML Spec (items)
               │
               ▼
          dsl apply
               │
               ▼
          Server Datasheet XML
               │
               ▼
          dsl sync
               │
               ▼
          Client DataCenter
```

## Content Systems

### Enchant Materials

**Status**: Implemented

| Component | Files |
|-----------|-------|
| Material Enchant Data | `specs/enchant-materials.yaml` |
| Item Links | `specs/enchant-item-links.yaml` |

**Workflow**: [ENCHANT_MATERIALS.md](workflows/ENCHANT_MATERIALS.md)

### Gear Infusion System

**Status**: Implemented

| Component | Files |
|-----------|-------|
| Passivities | `specs/gear-infusion-passivities.yaml` |
| Items | `specs/gear-infusion-items.yaml` |
| Loot Tables | `specs/infusion-loot.yaml` |

**Documentation**:
- Items & Passivities: [gear-infusion README](../tools/gear-infusion/README.md)
- Loot Distribution: [infusion-loot README](../tools/infusion-loot/README.md)
- Design Strategy: [INFUSION_LOOT_SYSTEM.md](INFUSION_LOOT_SYSTEM.md)

## External References

External paths are dev-specific. See `.references` (template: `.references.example`).

| Key | Purpose |
|-----|---------|
| `server_datasheet` | Server datasheet XMLs |
| `client_datacenter` | Client DataCenter folder |
| `client_pack_dir` | Client pack tool directory |
| `dsl_cli` | DSL CLI binary |
| `dsl_source` | DSL source code |
| `dsl_docs_enduser` | DSL end-user documentation |
| `dsl_docs_internal` | DSL internal documentation |

## Adding New Content Systems

1. Create data file in `reforged/data/`
2. Create generator script in `reforged/tools/<system-name>/`
3. Add README.md to tool folder
4. Output specs to `reforged/specs/`
5. Update this document
