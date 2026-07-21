Fast dev deploy loop: push local working-tree datasheet changes to the dev game server over SSH.

Arguments are optional and pass straight through to the tool: `--dry-run`, `--verify`, `--status`, `--revert`.

Read `.references` at `reforged/.references` only to resolve `<project_root>`; the tool resolves its own keys (`server_datasheet`, `dev_server_ssh`, `dev_server_datasheet`).

Run from `<project_root>`:

```
python reforged/tools/deploy-dev/deploy_dev.py {arguments}
```

Rules:

- With no arguments, run a plain deploy. If more than 200 files would transfer, stop and show the list summary to the user first; a working tree that dirty usually means unrelated edits are about to ship.
- After a successful deploy, remind the user: the world server loads datasheets at startup only and must be restarted manually (restart automation is deferred).
- `--revert` is destructive on the dev server (restores clean payload state). Never pass `--yes` on the user's behalf; let the tool prompt, or confirm with the user explicitly first.
- On failure, report the tool output verbatim and stop; do not fall back to manual copies or share paths.
- This tool deploys working-tree overlays only. When the user declares a patch validated, remind them of the promotion step: commit the local datasheet repo and push to the payload repo (see `reforged/tools/deploy-dev/README.md`).
