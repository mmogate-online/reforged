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
5. **Promotion, and it is TWO steps, not one**: once the patch validates
   end-to-end, commit the local datasheet repo and push it to the payload repo,
   **then pull that commit on the dev box**. Deployed overlays are working-tree
   state on the dev box; only the payload repo is durable (an infra payload
   redeploy resets the box to payload HEAD).

## The trap: this tool only ever pushes the DIRTY set

`git status` is the whole input. A file that is **committed** is not dirty, so it
is never pushed, and it reaches the dev box only through the box's own clone of
the payload repo.

That means closing a patch silently removes its content from every future deploy.
During development the files are dirty and get pushed; the moment they are
committed they drop out of the payload this tool sends, and the box keeps serving
them only until something resets it.

**This bit hard on 2026-07-30.** The dev box's clone sat at an April commit while
the local repo was 8 commits ahead, all of patch 001's restoration baseline. The
box had been reset at some point, which discarded the overlay that had been
carrying those files, and nothing detected it: `deploy_dev.py --verify` reported
184 of 184 files hash-verified every time, because all 184 were exactly the dirty
files it knew about. In game the symptom was quest givers with no quests, which
reads as a bad apply rather than a missing baseline. It cost hours.

**Check this first when deployed content does not appear in game:**

```bash
# what the box's clone is on, versus what your local repo has
ssh <dev_server_ssh> "& 'C:/Program Files/Git/cmd/git.exe' -C <repo> rev-parse --short HEAD"
git -C <server_datasheet> rev-parse --short HEAD
```

Different values mean the box is missing every committed change between them, and
no amount of redeploying will fix it. Fast-forward the box's clone, then redeploy
the overlay on top.

If the box cannot reach the git remote (no stored credentials in a non-interactive
SSH session is the usual cause), a `git bundle` moves the commits with no network
at all and leaves genuine history behind:

```bash
git -C <server_datasheet> bundle create iod.bundle <box-HEAD>..<branch>
scp iod.bundle <dev_server_ssh>:<remote path>
ssh <dev_server_ssh> "git -C <repo> fetch <bundle> <branch>:refs/remotes/origin/<branch>; git -C <repo> merge --ff-only origin/<branch>"
```

Line endings: the box's system gitconfig sets `core.autocrlf=true`, so files it
checks out are CRLF while this tool sftp's LF files byte-for-byte. A hash compare
between local and box will therefore differ on every checked-out file even when
the content is identical. Normalise line endings before concluding anything is
wrong.

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
