# Dev Server Deploy

Deploys working-tree datasheet changes to the dev game server over SSH. This is
the inner loop for trial-and-error content work: apply a spec locally, push the
delta, restart the world server manually, test in game, iterate.

Replaces the discontinued server-share push. No hostnames, users, or paths are
hardcoded; everything resolves from `reforged/.references`:

| Key | Purpose |
|-----|---------|
| `server_datasheet` | Local datasheet repo (git working tree; the DSL apply target) |
| `dev_server_ssh` | SSH target or alias for the dev game server (key-based auth) |
| `dev_server_datasheet` | Remote datasheet path on the dev game server (forward slashes) |

## Usage

```bash
python reforged/tools/deploy-dev/deploy_dev.py [--dry-run] [--verify]
python reforged/tools/deploy-dev/deploy_dev.py --status
python reforged/tools/deploy-dev/deploy_dev.py --revert [--yes]
```

- **Default**: reads `git status` in the local datasheet repo (every modified,
  added, deleted, renamed, untracked file), mirrors the delta to the remote
  datasheet folder in one sftp batch session, and issues remote deletes for
  removed files. Prints a restart reminder; the world server loads datasheets
  at startup only.
- `--dry-run`: list the planned copies and deletes without transferring.
- `--verify`: after transfer, compare SHA256 hashes of every copied file
  against the remote copies.
- `--status`: show what is currently overlaid on the dev server versus the
  payload repo HEAD (the remote datasheet folder is a git working tree).
- `--revert`: restore the dev server datasheet to clean payload state
  (`git checkout -f` plus `git clean -fd`, scoped to the datasheet folder).
  Prompts for confirmation unless `--yes`. Requires a world server restart to
  take effect.

## Workflow

1. Author or fix a spec, then `dsl apply` it against `<server_datasheet>`.
2. `python reforged/tools/deploy-dev/deploy_dev.py` (add `--verify` when it matters).
3. Restart the dev world server manually (restart automation is deferred).
4. Test in game. Iterate from step 1; use `--revert` to throw away a bad overlay.
5. **Promotion**: once the patch validates end-to-end, commit the local
   datasheet repo and push it to the payload repo. Deployed overlays are
   working-tree state on the dev box; only the payload repo is durable (an
   infra payload redeploy resets the box to payload HEAD).

## Notes

- Transfers use an sftp batch (single connection, no remote shell in the data
  path), so the remote default shell never touches file content.
- Remote git calls fall back to the absolute git install path if `git` is not
  on the SSH session PATH.
- Files named `nul` (Windows reserved name) are skipped with a warning; delete
  them locally.
- Deletions propagate only for tracked files. Deleting a locally untracked
  file (one that was deployed but never committed) leaves an orphan on the dev
  server; remove it with `--revert` (full reset of the overlay) or manually
  over SSH.
- `/deploy-dev` runs this tool as a slash command. It covers the server leg
  only; the client leg (pack, install, publish) is `tools/deploy-client/`.
