Full patch deploy pipeline: apply specs, sync client DataCenter, pack client, push to server share.

Patch numbers are passed as arguments (e.g. `/deploy-patch 000` or `/deploy-patch 000 001`). If no arguments are provided, ask the user for one or more patch numbers before proceeding.

Read `.references` at `reforged/.references`. Parse as `key=value` lines (skip comments and blanks). You need:

| Key | Purpose |
|-----|---------|
| `project_root` | Project root where `dsl.exe` lives |
| `server_datasheet` | Local server datasheet XML path |
| `client_pack_dir` | Client DataCenter pack directory |
| `server_share` | Live server share push target |

Execute these steps sequentially, stopping on any failure:

1. **Apply specs + sync client** — for each patch number in order, run from `<project_root>`:
   ```
   python reforged/tools/migrate/migrate.py --patch {patch}
   ```
   Run all patches before moving to the next step. If any patch fails, stop immediately.

2. **Pack client** — run once after all patches are applied. Use PowerShell:
   ```
   powershell -Command "Set-Location '<client_pack_dir>'; & '.\novadrop-dc_92.04\novadrop-dc' pack --encryption-key 7533835567F31B7C8BF9321CF7C67A07 --encryption-iv 1A2DE14F51A8AD426FEAEB4AC3CB705C DataCenter_Final_EUR DataCenter_Final_EUR.dat"
   ```
   The packed `DataCenter_Final_EUR.dat` is distributed to clients manually by the project lead. This step only produces the file — distribution is out of scope for this pipeline.

3. **Push to server share** — mirror every working-tree change in the server datasheet repo (modified, added, deleted, renamed, untracked) to the share, preserving subdirectory structure. This is a 1:1 push of whatever currently differs from HEAD, including any unrelated edits sitting in the working tree. Use PowerShell so UNC paths resolve:
   ```
   powershell -Command "python reforged/tools/migrate/push_changes.py --src '<server_datasheet>' --dst '<server_share>'"
   ```
   The script reads `git status` in `<server_datasheet>` — no patch numbers or manifests are consulted.

Replace `<project_root>`, `<server_datasheet>`, `<client_pack_dir>`, and `<server_share>` with values from `.references`.

Report each step's result. If any step fails, stop and report the error.
