"""Patch migration tool — applies all specs from a patch and syncs affected entities."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# YAML entity key → sync-config entity name (None = server-only, skip sync)
ENTITY_SYNC_MAP = {
    "items": "ItemData",
    "equipment": "EquipmentData",
    "evolutions": "EquipmentEvolutionData",
    "materialEnchants": "MaterialEnchantData",
    "enchants": "EquipmentEnchantData",
    "itemStrings": "StrSheet_Item",
    "passivities": None,
    "cCompensations": None,
    "eCompensations": None,
    "fCompensations": None,
    "iCompensations": None,
}

ENTITY_KEY_PATTERN = re.compile(r"^(" + "|".join(ENTITY_SYNC_MAP.keys()) + r"):")


def load_references(project_root: Path) -> dict[str, str]:
    refs = {}
    ref_file = project_root / "reforged" / ".references"
    for line in ref_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if value:
            refs[key.strip()] = value.strip()
    return refs


def discover_specs(patch_dir: Path) -> list[Path]:
    specs = []
    for root, _, files in os.walk(patch_dir):
        for f in files:
            if f.endswith(".yaml"):
                specs.append(Path(root) / f)
    specs.sort(key=lambda p: p.relative_to(patch_dir).as_posix())
    return specs


def detect_entities(spec_path: Path) -> set[str]:
    entities = set()
    with open(spec_path, "r", encoding="utf-8") as f:
        for line in f:
            m = ENTITY_KEY_PATTERN.match(line)
            if m:
                entities.add(m.group(1))
    return entities


def apply_spec(
    dsl_cli: str,
    spec_path: Path,
    server_datasheet: str,
    project_root: Path,
    dry_run: bool,
    verbose: bool,
) -> tuple[bool, str]:
    rel_path = spec_path.relative_to(project_root)
    cmd = [dsl_cli, "apply", str(rel_path), "--path", server_datasheet]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(
        cmd,
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )

    output = result.stdout.strip()
    if result.returncode != 0:
        error = result.stderr.strip() or output or "Unknown error"
        return False, error

    return True, output


def run_sync(
    dsl_cli: str,
    entities: list[str],
    project_root: Path,
    dry_run: bool,
    verbose: bool,
) -> tuple[bool, str]:
    config = project_root / "reforged" / "config" / "sync-config.yaml"
    cmd = [dsl_cli, "sync", "--config", str(config)]
    for e in entities:
        cmd.extend(["-e", e])
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(
        cmd,
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )

    output = result.stdout.strip()
    if result.returncode != 0:
        error = result.stderr.strip() or output or "Unknown error"
        return False, error

    return True, output


def count_by_category(specs: list[Path], patch_dir: Path) -> tuple[int, int]:
    root_count = 0
    loot_count = 0
    for s in specs:
        rel = s.relative_to(patch_dir).as_posix()
        if "/" in rel:
            loot_count += 1
        else:
            root_count += 1
    return root_count, loot_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply all specs from a patch and sync affected entities.")
    parser.add_argument("--patch", required=True, help="Patch folder name under reforged/specs/patches/")
    parser.add_argument("--dry-run", action="store_true", help="Pass --dry-run to dsl apply and dsl sync")
    parser.add_argument("--skip-sync", action="store_true", help="Apply specs only, skip client sync")
    parser.add_argument("--verbose", action="store_true", help="Show detailed DSL output")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    refs = load_references(project_root)

    dsl_cli = refs.get("dsl_cli", str(project_root / "dsl.exe"))
    server_datasheet = refs["server_datasheet"]

    patch_dir = project_root / "reforged" / "specs" / "patches" / args.patch
    if not patch_dir.is_dir():
        print(f"Error: Patch directory not found: {patch_dir}")
        return 1

    specs = discover_specs(patch_dir)
    if not specs:
        print(f"Error: No .yaml specs found in {patch_dir}")
        return 1

    root_count, loot_count = count_by_category(specs, patch_dir)
    total = len(specs)

    header_parts = []
    if root_count:
        header_parts.append(f"{root_count} specs")
    if loot_count:
        header_parts.append(f"{loot_count} loot specs")
    print(f"Patch {args.patch} — {' + '.join(header_parts)} ({total} total)")
    if args.dry_run:
        print("(dry-run mode)")
    print()

    all_entity_keys: set[str] = set()
    applied = 0
    failed = 0
    failed_specs: list[str] = []

    for i, spec in enumerate(specs, 1):
        rel = spec.relative_to(patch_dir).as_posix()
        print(f"[{i}/{total}] {rel}")

        entities = detect_entities(spec)
        all_entity_keys.update(entities)

        ok, output = apply_spec(dsl_cli, spec, server_datasheet, project_root, args.dry_run, args.verbose)
        if ok:
            applied += 1
            if args.verbose and output:
                for line in output.splitlines():
                    print(f"        {line}")
            else:
                summary_line = ""
                for line in output.splitlines():
                    if "Applied" in line or "operations" in line.lower():
                        summary_line = line.strip()
                        break
                if summary_line:
                    print(f"        \u2713 {summary_line}")
                else:
                    print(f"        \u2713 Applied")
        else:
            failed += 1
            failed_specs.append(rel)
            error_brief = output.splitlines()[0] if output else "Unknown error"
            print(f"        \u2717 Failed \u2014 {error_brief}")
            if args.verbose and output:
                for line in output.splitlines()[1:]:
                    print(f"          {line}")

    # Summary
    print()
    print("\u2500\u2500 Summary \u2500\u2500")
    fail_note = f" ({failed} failed)" if failed else ""
    print(f"Applied: {applied} specs{fail_note}")

    if failed_specs and args.verbose:
        for fs in failed_specs:
            print(f"  \u2717 {fs}")

    syncable_entities = sorted({
        ENTITY_SYNC_MAP[k] for k in all_entity_keys
        if k in ENTITY_SYNC_MAP and ENTITY_SYNC_MAP[k] is not None
    })
    server_only_keys = sorted({
        k for k in all_entity_keys
        if k in ENTITY_SYNC_MAP and ENTITY_SYNC_MAP[k] is None
    })

    if syncable_entities:
        print(f"Entities modified: {', '.join(syncable_entities)}")
    if server_only_keys:
        print(f"Server-only: {', '.join(server_only_keys)} (no sync needed)")

    # Client sync
    if args.skip_sync:
        print("\nSync skipped (--skip-sync)")
        return 0

    if not syncable_entities:
        print("\nNo syncable entities — nothing to sync")
        return 0

    print()
    print("\u2500\u2500 Client Sync \u2500\u2500")
    print(f"Syncing: {', '.join(syncable_entities)}")

    ok, output = run_sync(dsl_cli, syncable_entities, project_root, args.dry_run, args.verbose)
    if ok:
        print("\u2713 Sync complete")
        if args.verbose and output:
            for line in output.splitlines():
                print(f"  {line}")
        return 0
    else:
        print(f"\u2717 Sync failed \u2014 {output}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
