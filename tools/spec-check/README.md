# Spec Check Tool

Validate or apply a single DSL spec against the datasheet repo's HEAD. Automatically
passes `--source-ref <HEAD>` to the DSL, so balance specs (and other non-idempotent
operations) read from a deterministic baseline regardless of working-tree state.

## When to use

- Quick validation of a spec you are authoring, without running the full migration
  pipeline
- Sanity-checking non-idempotent `balanceProfiles` specs — reading from HEAD means
  repeated runs produce the same result
- Checking that a spec still validates after upstream changes to the datasheet

## Quick Start

```bash
# Validate a spec against HEAD of the datasheet repo (default)
python reforged/tools/spec-check/check.py reforged/specs/patches/001/balance/zone-0013-island_of_dawn.yaml

# Apply it (writes to datasheet working tree)
python reforged/tools/spec-check/check.py reforged/specs/patches/001/balance/zone-0013-island_of_dawn.yaml --apply

# Use a specific ref instead of HEAD
python reforged/tools/spec-check/check.py <spec> --ref refs/tags/iod-migration-v1

# Read from working tree (disable --source-ref, escape hatch)
python reforged/tools/spec-check/check.py <spec> --no-source-ref
```

## Flags

| Flag | Description |
|------|-------------|
| `spec` | Path to the YAML spec (positional, required) |
| `--apply` | Execute `dsl apply` instead of `dsl validate`. Writes to the datasheet working tree. |
| `--ref <ref>` | Override the ref passed as `--source-ref`. Default: HEAD of the datasheet repo. |
| `--no-source-ref` | Disable `--source-ref` entirely; read from the working tree. Useful when debugging working-tree diffs. |
| `--verbose`, `-v` | Pass `--verbose` to the DSL command. |

## How It Resolves the Baseline

1. Reads the `server_datasheet` path from `reforged/.references`.
2. Runs `git rev-parse HEAD` in that directory to resolve the current commit.
3. Also runs `git rev-parse --abbrev-ref HEAD` to resolve the branch name for the
   startup banner.
4. Passes the resolved SHA as `--source-ref` to the DSL command.

If the datasheet path is not a git repo, the tool errors out with a hint to use
`--no-source-ref`.

## Relationship to `migrate.py`

`spec-check` is for single-spec sanity checks. `migrate.py` runs full patch pipelines
(many specs, manifest-narrowed client sync). Both tools can use `--source-ref`, but
with different trade-offs — see `tools/migrate/README.md`.
