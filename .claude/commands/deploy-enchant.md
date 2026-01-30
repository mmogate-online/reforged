Deploy enchant materials: generate specs from xlsx, apply to server datasheets, sync to client DataCenter, and pack client dat file.

Read the `.references` file at `.references` to resolve paths. Parse it as `key=value` lines (skip comments and blanks).

Execute these steps sequentially, stopping on any failure:

1. **Generate specs** — run `python generate_enchant_materials.py` from `tools/enchant-materials/`
2. **Apply enchant-materials** — from `<project_root>`, run: `./dsl.exe apply "reforged/specs/enchant-materials.yaml" --path "<server_datasheet>"`
3. **Apply enchant-item-links** — from `<project_root>`, run: `./dsl.exe apply "reforged/specs/enchant-item-links.yaml" --path "<server_datasheet>"`
4. **Sync to client** — from `<project_root>`, run: `./dsl.exe sync --config "reforged/config/sync-config.yaml" -e MaterialEnchantData -e ItemData`
5. **Pack client** — use PowerShell for this step: `powershell -Command "Set-Location '<client_pack_dir>'; & '.\novadrop-dc_92.04\novadrop-dc' pack --encryption-key 7533835567F31B7C8BF9321CF7C67A07 --encryption-iv 1A2DE14F51A8AD426FEAEB4AC3CB705C DataCenter_Final_EUR DataCenter_Final_EUR.dat"`

Replace `<project_root>`, `<server_datasheet>`, and `<client_pack_dir>` with values from the `.references` file. Use forward slashes in paths passed to `dsl.exe` arguments.

Report each step's result. If any step fails, stop and report the error.
