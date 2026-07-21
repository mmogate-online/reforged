# Deploy Client

Takes an **already-synced** unpacked client DataCenter and ships it: repack the
`.dat`, install it into the local game client, and publish a new dev-channel
release to Cloudflare R2.

This is the client counterpart to `deploy-dev` (which pushes server datasheets
to the dev game server). It encodes the manual pipeline that was proven for the
IoD quest re-enable so it can be rerun without redriving each step by hand.

No hostnames, machine paths, or credentials are hardcoded; everything resolves
from `reforged/.references`. Credentials are read into the subprocess
environment only and are never printed.

## This tool does not sync

Populating the unpacked client DataCenter from the server datasheets is owned
entirely by `tools/migrate/migrate.py`, which syncs **every** entity declared in
`config/sync-config.yaml`, narrowed by the apply manifest to the files a patch
actually touched. Run it first:

```bash
python reforged/tools/migrate/migrate.py --patch 001
```

A `--sync` stage used to live here. It mapped exactly one family
(`QuestData/*.quest` to `Quest`) and reported every other dirty family as
`no sync mapping, server-only or handle manually`. That was true when it was
written for a quest-only deploy, but it went stale as `sync-config.yaml` gained
entities, so families that *were* syncable (`StrSheet_Item`, `StrSheet_Quest`,
`TerritoryData`, `AreaData`, `NewWorldMapData`, and others) got reported as
manual work. It was removed rather than repaired: two tools owning sync is the
defect, and the narrower one was always the wrong one to keep.

## .references keys

| Key | Purpose |
|-----|---------|
| `client_pack_dir` | Client pack directory (holds `novadrop-dc`, `enc_EUR.bat`, the `.dat`) |
| `game_client_install` | Local game client install (the patcher publish gameDir) |
| `patcher_origin` | Patcher origin unit (rporigin profile, vendored publish CLI, staged creds) |

Any key needed for a requested stage that is missing aborts with a clear
message before that stage runs.

## Usage

```bash
# Print every command without executing anything:
python deploy_client.py --all --dry-run

# Typical run: pack + install + publish DRY-RUN (no upload):
python deploy_client.py --all --note "IoD quest re-enable"

# After reviewing the dry-run delta, commit the upload:
python deploy_client.py --publish --note "IoD quest re-enable"
```

Running with no flags prints help. Individual stages can be run on their own:
`--pack`, `--install`, `--publish`. The pipeline stops at the first failed stage
with a non-zero exit.

## Stages

| Flag | Stage | What it does |
|------|-------|--------------|
| `--pack` | Pack | Repacks `DataCenter_Final_EUR` into `DataCenter_Final_EUR.dat` with `novadrop-dc`. Key and IV are parsed at runtime from `enc_EUR.bat` (never hardcoded). Takes ~1-3 min; progress is collapsed to occasional updates. |
| `--install` | Install | Copies the packed `.dat` into `<game_client_install>\S1Game\S1Data\`. Refuses if the target is locked (game running). Writes no backup or sidecar file: the patcher chunks the whole gameDir, so stray files would ship to players. |
| `--publish` | Publish | Stages `.rpignore`, builds, signs, dry-runs, and (only with `--publish`) uploads to R2, then records the release. |
| `--all` | All | `--pack` + `--install` and the publish stage in dry-run-only mode. Committing an upload always requires an explicit `--publish`. |

## Publish stage detail

All publish paths are relative to `patcher_origin` (the CLI runs with that as
its working directory); workspace, store, manifest, and gameDir come from the
`reforged.rporigin` profile.

1. **Stage ignore rules** - copy `build-source.rpignore` to
   `<game_client_install>\.rpignore` (overwrite).
2. **Read the profile** - `GameDirectory` must equal `game_client_install`
   (mismatch aborts). Reads `WorkspaceDirectory`, `ChunkAvgSize`, the S3
   target `Endpoint`/`Bucket`, and the last `Channel == "dev"` release to
   compute the next version `0.1.0-dev.{N+1}`.
3. **Credentials** - `RP_S3_ACCESS_KEY` / `RP_S3_SECRET_KEY` from
   `.tmp\r2-publish.env`, signing key `.tmp\priv.key`, public key
   `.tmp\pub.key`. Any missing input aborts with guidance to `sops`-decrypt
   per the patcher-origin README.
4. **Build** the manifest and parse the merkle root from the output.
5. **Sign** the manifest with the private key.
6. **Dry-run publish first, always** - prints the reused / to-upload summary.
   Then, only with an explicit `--publish`, the same command runs without
   `--dry-run` and success requires `committed=True` in the output.
7. **Record** - append the new release to `reforged.rporigin` `Releases[]`
   (text insertion that preserves 2-space indent and CRLF; `BuiltUtc` and
   `PublishedUtc` captured at build and publish time) and prepend a dated
   bullet to `deployment-log.md` after the H1 (version, chunk delta, and the
   `--note` content summary).

## Rules and rationale

- **No sidecar/backup files in the install tree.** The patcher chunks the whole
  install directory, so any stray file (a `.bak`, an old `.dat.original`) would
  ship to players. Install overwrites in place and writes no backup.
- **`.rpignore` staging.** The build must exclude launcher-managed runtime
  artifacts and per-client config; staging `build-source.rpignore` as the
  install's `.rpignore` before every build makes the chunk set reproducible
  regardless of what state the last play session left the folder in.
- **Locked chunk size.** `ChunkAvgSize` comes from the profile and is passed
  verbatim as `--avg`; do not change it. Re-chunking with a different average
  invalidates every reused chunk and forces a full re-upload.
- **rporigin / log auto-append.** The vendored CLI does not append to
  `Releases[]` itself (only the Publisher app does), so this tool writes both
  the profile entry and the deployment-log bullet after a committed publish.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success, dry-run, or read-only preview |
| 1 | Configuration error (missing `.references` key, GameDirectory mismatch, missing credentials) |
| 2 | A pipeline stage failed (pack/install/publish returned nonzero, or publish did not report `committed=True`) |
