# General Content Workflow

## Data Pipeline

Every content change follows the same pipeline:

```
Data File  →  Generate  →  Apply  →  Sync  →  Pack  →  Deploy
 (xlsx/csv)   (Python)     (DSL)    (DSL)   (bat)   (server)
```

| Step | What it does | Command |
|------|-------------|---------|
| **Data** | Edit source data (xlsx, csv) | Manual edit |
| **Generate** | Convert data into YAML specs | `python <generator>.py --patch {NNN}` |
| **Apply** | Write specs into server datasheets | `dsl apply <spec> --path <datasheet>` |
| **Sync** | Copy server changes to client DataCenter | `dsl sync --config reforged\config\sync-config.yaml -e <Entity>` |
| **Pack** | Pack client DataCenter for distribution | `pack-client.bat` (project root) |
| **Deploy** | Copy files to running server | Manual / server restart |

## Available Scripts

### Per-tool scripts (in `reforged/tools/<system>/`)

| Script | Purpose |
|--------|---------|
| `generate.bat` | Run only the generation step |
| `deploy.bat` | Run the full pipeline: generate → apply → sync |

### Root-level scripts

| Script | Purpose |
|--------|---------|
| `pack-client.bat` | Pack the client DataCenter after any sync |

## Typical Workflow

1. Edit your data file (xlsx or csv)
2. Double-click `deploy.bat` in the tool folder — this generates, applies, and syncs
3. Double-click `pack-client.bat` in the project root — this packs the client
4. Deploy to server

## Sync: Target Specific Entities

Always sync only the entities your workflow affects using `-e`:

```bash
dsl sync --config reforged\config\sync-config.yaml -e MaterialEnchantData -e ItemData
```

Using `--all` or omitting `-e` syncs every entity in the config, which touches datasheet files unrelated to your change — producing large diffs and unnecessary processing. Each `deploy.bat` already targets the correct entities.

## Patch Structure

Generated specs are organized into patch folders:

```
reforged/specs/patches/{NNN}/
```

Where `{NNN}` is the patch number (e.g., `001`, `002`). Each generator accepts `--patch {NNN}` to output specs into the corresponding patch folder. The `deploy.bat` and `generate.bat` scripts prompt for the patch number automatically.

Example:

```bash
python generate_enchant_materials.py --patch 001
# Output: reforged/specs/patches/001/enchant-materials.yaml
```

## Tool Development Standards

When creating new Python generator tools in `reforged/tools/`:

### Required Pattern

All tools MUST use `argparse` with a `--patch` argument:

```python
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFORGED_DIR = SCRIPT_DIR.parent.parent
DEFAULT_OUTPUT = REFORGED_DIR / "specs" / "my-spec.yaml"

def main():
    parser = argparse.ArgumentParser(description="Generate my spec")
    parser.add_argument("--patch", help="Patch folder name (e.g. 001). Output goes to reforged/specs/patches/{patch}/")
    args = parser.parse_args()

    if args.patch:
        specs_dir = REFORGED_DIR / "specs" / "patches" / args.patch
        specs_dir.mkdir(parents=True, exist_ok=True)
        output_path = specs_dir / "XX-my-spec.yaml"  # XX = ordering prefix
    else:
        output_path = DEFAULT_OUTPUT

    # ... generate and write spec ...
```

### Naming Conventions

- Tool directory: `reforged/tools/<system-name>/`
- Generator script: `generate_<name>.py` or `generate_spec.py`
- Default output: `reforged/specs/<spec-name>.yaml`
- Patch output: `reforged/specs/patches/{NNN}/XX-<spec-name>.yaml`
  - `XX` = two-digit ordering prefix (01, 02, 03...)

### Required Files

Each tool directory should contain:
- `generate_*.py` - The generator script
- `README.md` - Usage documentation

### Do NOT

- Hardcode output paths without `--patch` support
- Use global constants for patch-specific paths
- Skip the argparse pattern for "simple" tools

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `dsl apply` reports validation errors | YAML spec has invalid values | Re-check the data file and regenerate |
| `client-sync` skips entities | Entity not in sync-config.yaml | Add the entity to `reforged/config/sync-config.yaml` |
| Python script fails with import error | Missing dependency | Run `pip install openpyxl` (or the required package) |
| Pack fails | Client DC path incorrect | Verify path in `pack-client.bat` |
