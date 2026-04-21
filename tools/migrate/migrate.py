"""Patch migration tool — applies all specs from a patch and syncs affected entities."""

import argparse
import json
import os
import re
import shutil
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
    "evolutionPaths": "EquipmentEvolutionData",
    "equipmentInheritance": "EquipmentInheritanceData",
    "itemProduceRecipes": "ItemProduceRecipeData",
    "materialEnchants": "MaterialEnchantData",
    "enchants": "EquipmentEnchantData",
    "enchantPassivityCategories": "EquipmentEnchantData",
    "itemStrings": "StrSheet_Item",
    "passivities": "Passivity",
    "passivityStrings": "StrSheet_Passivity",
    "cCompensations": None,
    "eCompensations": None,
    "fCompensations": None,
    "iCompensations": None,
    "gachaItems": "Gacha",
    "rawStoneItems": "RawStoneItems",
    "collections": "CollectionData",
    "abnormalities": "Abnormality",
    "customizingItems": "CustomizingItems",
    "customizingItemBags": None,
    "exchanges": None,          # ItemMedalExchange — server-only, client reads at runtime
    "npcStrings": "StrSheet_Npc",   # StrSheet_Npc — shop/NPC title strings
    "villagerMenuItems": None,  # VillagerMenuItem — server-only
    "buyMenuLists": "BuyMenuList",  # BuyMenuList — synced to client MenuList/
    "buyLists": None,           # BuyList — server-only
    "commonSkills": "SkillData",
    "userSkills": "SkillData",
    "npcSkills": "SkillData",
}

# Entity keys whose inline blocks imply additional sync entities
# Values can be a string (single entity) or list (multiple entities)
INLINE_STRING_SYNC = {
    "items": "StrSheet_Item",
    "enchantPassivityCategories": ["Passivity", "StrSheet_Passivity"],
    "gachaItems": ["ItemData", "StrSheet_Item"],
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


def manifest_slug(spec_path: Path, patch_dir: Path) -> str:
    """Derive a stable filename slug for a spec's manifest."""
    rel = spec_path.relative_to(patch_dir).with_suffix("")
    return rel.as_posix().replace("/", "_")


def scan_for_nul_files(server_datasheet: str) -> list[Path]:
    """Windows 'nul' is a reserved filename; its presence blocks robocopy."""
    hits: list[Path] = []
    for root, _, files in os.walk(server_datasheet):
        if "nul" in files:
            hits.append(Path(root) / "nul")
    return hits


def apply_spec(
    dsl_cli: str,
    spec_path: Path,
    server_datasheet: str,
    project_root: Path,
    dry_run: bool,
    verbose: bool,
    manifest_out: Path | None,
) -> tuple[bool, str]:
    rel_path = spec_path.relative_to(project_root)
    cmd = [dsl_cli, "apply", str(rel_path), "--path", server_datasheet]
    if dry_run:
        cmd.append("--dry-run")
    if manifest_out is not None:
        cmd.extend(["--manifest-out", str(manifest_out)])

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
    manifest_paths: list[Path] | None,
) -> tuple[bool, str]:
    config = project_root / "reforged" / "config" / "sync-config.yaml"
    cmd = [dsl_cli, "sync", "--config", str(config)]
    for e in entities:
        cmd.extend(["-e", e])
    if manifest_paths:
        for p in manifest_paths:
            cmd.extend(["--from-manifest", str(p)])
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


def load_manifest_modified_count(manifest_path: Path) -> int:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return len(data.get("modified_files", []))
    except (OSError, json.JSONDecodeError):
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply all specs from a patch and sync affected entities.")
    parser.add_argument("--patch", required=True, help="Patch folder name under reforged/specs/patches/")
    parser.add_argument("--dry-run", action="store_true", help="Pass --dry-run to dsl apply and dsl sync")
    parser.add_argument("--skip-sync", action="store_true", help="Apply specs only, skip client sync")
    parser.add_argument("--no-narrow", action="store_true", help="Run full sync instead of manifest-narrowed sync (escape hatch)")
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

    # Preflight: warn on Windows reserved 'nul' files in the server datasheet tree
    nul_files = scan_for_nul_files(server_datasheet)
    if nul_files:
        print(f"\u26a0 Warning: {len(nul_files)} 'nul' file(s) found in server datasheet (will block robocopy push):")
        for p in nul_files[:5]:
            print(f"    {p}")
        if len(nul_files) > 5:
            print(f"    ... and {len(nul_files) - 5} more")
        print("  Delete with: python -c \"import os; os.remove(r'\\\\\\\\?\\\\<full-path>')\"")
        print()

    # Manifest output directory — wiped per-run, gitignored via reforged/.gitignore
    manifests_dir = project_root / "reforged" / "tools" / "migrate" / ".manifests" / args.patch
    emit_manifests = not (args.dry_run or args.skip_sync)
    if emit_manifests:
        if manifests_dir.exists():
            shutil.rmtree(manifests_dir)
        manifests_dir.mkdir(parents=True, exist_ok=True)

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
    if args.no_narrow and emit_manifests:
        print("(--no-narrow: sync will skip manifest narrowing)")
    print()

    all_entity_keys: set[str] = set()
    applied = 0
    failed = 0
    failed_specs: list[str] = []
    successful_manifests: list[Path] = []

    for i, spec in enumerate(specs, 1):
        rel = spec.relative_to(patch_dir).as_posix()
        print(f"[{i}/{total}] {rel}")

        entities = detect_entities(spec)
        all_entity_keys.update(entities)

        manifest_path: Path | None = None
        if emit_manifests:
            manifest_path = manifests_dir / f"{manifest_slug(spec, patch_dir)}.json"

        ok, output = apply_spec(
            dsl_cli, spec, server_datasheet, project_root,
            args.dry_run, args.verbose, manifest_path,
        )

        if ok:
            applied += 1
            if manifest_path is not None and manifest_path.exists():
                successful_manifests.append(manifest_path)
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

    sync_set = {
        ENTITY_SYNC_MAP[k] for k in all_entity_keys
        if k in ENTITY_SYNC_MAP and ENTITY_SYNC_MAP[k] is not None
    }
    for k in all_entity_keys:
        if k in INLINE_STRING_SYNC:
            inline_entities = INLINE_STRING_SYNC[k]
            if isinstance(inline_entities, list):
                sync_set.update(inline_entities)
            else:
                sync_set.add(inline_entities)
    syncable_entities = sorted(sync_set)
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

    if applied == 0:
        print("\nAll specs failed — sync skipped")
        return 1

    # Manifest-narrowed sync decision
    manifest_paths: list[Path] | None = None
    if not args.no_narrow and emit_manifests:
        total_modified = sum(load_manifest_modified_count(m) for m in successful_manifests)
        if total_modified == 0:
            print("\nNo server-side file changes — sync skipped")
            return 0
        manifest_paths = successful_manifests
        print()
        print(f"\u2500\u2500 Client Sync \u2500\u2500")
        print(f"Syncing: {', '.join(syncable_entities)}")
        print(f"Narrowing: {len(manifest_paths)} manifest(s), {total_modified} modified file(s)")
    else:
        print()
        print(f"\u2500\u2500 Client Sync \u2500\u2500")
        print(f"Syncing: {', '.join(syncable_entities)}")
        if args.no_narrow:
            print("(--no-narrow: full sync, manifest narrowing disabled)")

    ok, output = run_sync(
        dsl_cli, syncable_entities, project_root,
        args.dry_run, args.verbose, manifest_paths,
    )
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
