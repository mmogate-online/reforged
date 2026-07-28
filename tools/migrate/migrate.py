"""Patch migration tool — applies all specs from a patch and syncs affected entities."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
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
    "abnormalityIconData": "AbnormalityIconData",
    "abnormalityStrings": "StrSheet_Abnormality",
    "customizingItems": "CustomizingItems",
    "customizingItemBags": None,
    "exchanges": None,          # ItemMedalExchange — server-only, client reads at runtime
    "npcStrings": "StrSheet_Npc",
    "villagerMenuItems": None,  # VillagerMenuItem — server-only
    "buyMenuLists": "BuyMenuList",
    "buyLists": None,           # BuyList — server-only
    "commonSkills": "SkillData",
    "userSkills": "SkillData",
    "npcSkills": "SkillData",
    "npcs": None,               # NpcData — server-only
    "ai": None,                 # AIData — server-only
    "balanceProfiles": None,    # NpcData (+ SkillData when skills: present — see detect_entities)
    "quests": "Quest",
    "questDialogs": "QuestDialog",
    # StrSheet_Quest: 1 monolithic server file vs 2879 per-quest client shards.
    # Wired via `merge: shard-routed` (datasheetlang 8a3d89ab), which rewrites each
    # record in the shard that already owns it. See the entity note in sync-config.yaml.
    "questStrings": "StrSheet_Quest",
    # QuestCompensationData has a CLIENT leg (153 shards) that the quest log
    # reward panel reads; only C/E/F/ICompensation are truly server-only.
    # See docs/plans/questcomp-client-sync.md.
    "questCompensations": "QuestCompensationData",
    "territorySpawns": "TerritoryData",
    "territoryGroups": "TerritoryData",
    "territories": "TerritoryData",
    "territoryParties": "TerritoryData",
    "villagerDialogs": None,    # VillagerDialog: server-only
    "areaSections": "AreaData", # sync filtering fixed in DSL commit 735abf92, apply-verified 2026-07-19
    "regionStrings": "StrSheet_Region",
    "villagerMenus": "VillagerMenu",
    "speechConditions": None,   # VillagerData .condition files: server-only (client strings resolve elsewhere)
    "questStoryGroups": None,   # QuestGroupList.xml: client copy handling pending Stage 5 validation item 7
    "questHuntingZones": None,  # QuestGroupList.xml co-tenant: same as above
    "newWorldMap": "NewWorldMapData",  # monolithic merge-by-id sync (see sync-config entity note)
    "dungeonDatas": None,       # DungeonData: server-authoritative scripting, no client sync (spec 19 precedent)
    "workObjects": "WorkObjectData",  # client carries isForQuestId/task gating (spec 19 portal)
    "workObjectTerritories": None,    # WorkObjectTerritory_{hz}: server-only, no client family
}

# Entity keys whose inline blocks imply additional sync entities
# Values can be a string (single entity) or list (multiple entities)
INLINE_STRING_SYNC = {
    "items": "StrSheet_Item",
    "abnormalities": "StrSheet_Abnormality",  # inline abnormalityStrings blocks
    "enchantPassivityCategories": ["Passivity", "StrSheet_Passivity"],
    "gachaItems": ["ItemData", "StrSheet_Item"],
}

ENTITY_KEY_PATTERN = re.compile(r"^(" + "|".join(ENTITY_SYNC_MAP.keys()) + r"):")

# Detects a skills: section indented under a balanceProfiles block
BALANCE_SKILLS_HINT = re.compile(r"^\s+skills:\s*$")


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
    lines = spec_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        m = ENTITY_KEY_PATTERN.match(line)
        if m:
            entities.add(m.group(1))
    # A balanceProfiles block with a skills: section modifies NpcSkillData → SkillData sync needed
    if "balanceProfiles" in entities and any(BALANCE_SKILLS_HINT.match(l) for l in lines):
        entities.add("npcSkills")
    return entities


def scan_for_nul_files(server_datasheet: str) -> list[Path]:
    """Windows 'nul' is a reserved filename; its presence blocks robocopy."""
    hits: list[Path] = []
    for root, _, files in os.walk(server_datasheet):
        if "nul" in files:
            hits.append(Path(root) / "nul")
    return hits


def resolve_server_head(server_datasheet: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=server_datasheet,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def apply_specs_batch(
    dsl_cli: str,
    spec_paths: list[Path],
    server_datasheet: str,
    project_root: Path,
    dry_run: bool,
    verbose: bool,
    manifest_path: Path | None,
    source_ref: str | None,
) -> bool:
    """Apply all specs in one dsl apply call. DSL output streams to the terminal.

    Uses the shared in-memory cache — later specs see earlier specs' mutations
    without disk round-trips. On fail-fast failure DSL rolls back everything;
    nothing is committed to the working tree.
    """
    cmd = [dsl_cli, "apply"]
    cmd.extend(spec.relative_to(project_root).as_posix() for spec in spec_paths)
    cmd.extend(["--path", server_datasheet])
    if manifest_path is not None and not dry_run:
        cmd.extend(["--manifest-out", str(manifest_path)])
    if source_ref is not None:
        cmd.extend(["--source-ref", source_ref])
    if dry_run:
        cmd.append("--dry-run")
    if verbose:
        cmd.append("--verbose")
    result = subprocess.run(cmd, cwd=str(project_root))
    return result.returncode == 0


def run_sync(
    dsl_cli: str,
    entities: list[str],
    project_root: Path,
    dry_run: bool,
    verbose: bool,
    manifest_path: Path | None,
) -> tuple[bool, str]:
    config = project_root / "reforged" / "config" / "sync-config.yaml"
    cmd = [dsl_cli, "sync", "--config", str(config)]
    for e in entities:
        cmd.extend(["-e", e])
    if manifest_path is not None:
        cmd.extend(["--from-manifest", str(manifest_path)])
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(
        cmd,
        cwd=str(project_root / "reforged"),
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
    sub_count = 0
    for s in specs:
        rel = s.relative_to(patch_dir).as_posix()
        if "/" in rel:
            sub_count += 1
        else:
            root_count += 1
    return root_count, sub_count


def load_manifest_modified_count(manifest_path: Path) -> int:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return len(data.get("modified_files", []))
    except (OSError, json.JSONDecodeError):
        return 0


# Entity keys whose changes a quest design review has anything to say about.
QUEST_DESIGN_KEYS = {
    "quests", "questCompensations", "questDialogs", "questStrings",
    "questStoryGroups", "questHuntingZones",
}


def quest_design_advisory(project_root: Path, server_datasheet: str,
                          source_ref: str | None, entity_keys: set[str]) -> None:
    """Print ONE advisory line for the quests this patch touched.

    Never the full report: a patch apply is not the place to read 60 findings,
    and a wall of pre-existing conditions trains people to scroll past it. The
    number printed is NEW findings only, derived from the datasheet diff against
    the ref the apply already pinned reads to, which is what makes it meaningful.

    Advisory means advisory: this never changes migrate's exit code, and any
    failure inside it is reported and stepped over rather than failing a patch
    that applied correctly.
    """
    if not (entity_keys & QUEST_DESIGN_KEYS):
        return

    tool = project_root / "reforged" / "tools" / "dc-restore" / "audit_quest_design.py"
    if not tool.is_file():
        return

    cmd = [sys.executable, str(tool), "--all-zones", "--json",
           "--datasheet", server_datasheet]
    if source_ref:
        cmd += ["--since", source_ref]

    print()
    print("── Quest Design Review ──")
    try:
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=300, env=env)
        payload = json.loads(proc.stdout.rsplit("ADVISORY", 1)[0])
        summary = payload["summary"]
    except Exception as exc:
        print(f"  (advisory unavailable: {type(exc).__name__}: {exc})")
        return

    print(f"  ADVISORY: {summary['new']} new findings "
          f"({summary['total']} total, {summary['waived']} waived)")
    if summary["new"]:
        print(f"  Full report: python reforged/tools/dc-restore/audit_quest_design.py "
              f"--all-zones --since {source_ref or 'HEAD'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply all specs from a patch and sync affected entities.")
    parser.add_argument("--patch", required=True, help="Patch folder name under reforged/specs/patches/")
    parser.add_argument("--dry-run", action="store_true", help="Pass --dry-run to dsl apply and dsl sync")
    parser.add_argument("--skip-sync", action="store_true", help="Apply specs only, skip client sync")
    parser.add_argument("--no-narrow", action="store_true", help="Run full sync instead of manifest-narrowed sync (escape hatch)")
    parser.add_argument("--no-source-ref", action="store_true", help="Read datasheets from working tree instead of server repo HEAD")
    parser.add_argument("--verbose", action="store_true", help="Pass --verbose to dsl apply for diagnostic output")
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
        print(f"⚠ Warning: {len(nul_files)} 'nul' file(s) found in server datasheet (will block robocopy push):")
        for p in nul_files[:5]:
            print(f"    {p}")
        if len(nul_files) > 5:
            print(f"    ... and {len(nul_files) - 5} more")
        print("  Delete with: python -c \"import os; os.remove(r'\\\\\\\\?\\\\<full-path>')\"")
        print()

    # Source-ref: pin reads to server repo HEAD so multiply/add transforms are idempotent
    source_ref: str | None = None
    if not args.no_source_ref:
        source_ref = resolve_server_head(server_datasheet)
        if source_ref is None:
            print("⚠ Warning: server datasheet is not a git repo; reading from working tree")

    # Pre-scan all specs for entity keys before invoking DSL
    all_entity_keys: set[str] = set()
    for spec in specs:
        all_entity_keys.update(detect_entities(spec))

    # Manifest setup — run.json per patch run (wiped at start of each run)
    emit_manifests = not (args.dry_run or args.skip_sync)
    manifest_path: Path | None = None
    if emit_manifests:
        manifests_dir = project_root / "reforged" / "tools" / "migrate" / ".manifests" / args.patch
        if manifests_dir.exists():
            shutil.rmtree(manifests_dir)
        manifests_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifests_dir / "run.json"

    root_count, sub_count = count_by_category(specs, patch_dir)
    total = len(specs)

    header_parts = []
    if root_count:
        header_parts.append(f"{root_count} specs")
    if sub_count:
        header_parts.append(f"{sub_count} sub-specs")
    print(f"Patch {args.patch} — {' + '.join(header_parts)} ({total} total)")
    if args.dry_run:
        print("(dry-run mode)")
    if args.no_narrow and emit_manifests:
        print("(--no-narrow: sync will skip manifest narrowing)")
    print()

    sys.stdout.flush()

    t_apply = time.monotonic()
    run_ok = apply_specs_batch(
        dsl_cli, specs, server_datasheet, project_root,
        args.dry_run, args.verbose, manifest_path, source_ref,
    )
    apply_secs = time.monotonic() - t_apply

    if not run_ok:
        return 1

    if args.dry_run:
        print("\n(dry-run completed — no files written)")

    # Summary
    print()
    print("── Summary ──")

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

    summary_parts = []
    if syncable_entities:
        summary_parts.append(f"{len(syncable_entities)} entities modified")
    if server_only_keys:
        summary_parts.append(f"{len(server_only_keys)} server-only skipped")
    summary_parts.append(f"{apply_secs:.0f}s")
    print("  |  ".join(summary_parts))

    quest_design_advisory(project_root, server_datasheet, source_ref, all_entity_keys)

    # Client sync
    if args.skip_sync:
        print("\nSync skipped (--skip-sync)")
        return 0

    if not syncable_entities:
        print("\nNo syncable entities — nothing to sync")
        return 0

    # Manifest-narrowed sync decision
    use_manifest: Path | None = None
    if not args.no_narrow and emit_manifests and manifest_path is not None:
        total_modified = load_manifest_modified_count(manifest_path)
        if total_modified == 0:
            print("\nNo server-side file changes — sync skipped")
            return 0
        use_manifest = manifest_path
        print()
        print("── Client Sync ──")
        print(f"Syncing {len(syncable_entities)} entities  ·  {total_modified} file(s) via manifest")
    else:
        print()
        print("── Client Sync ──")
        print(f"Syncing {len(syncable_entities)} entities")
        if args.no_narrow:
            print("(--no-narrow: full sync, manifest narrowing disabled)")

    t_sync = time.monotonic()
    ok, output = run_sync(
        dsl_cli, syncable_entities, project_root,
        args.dry_run, args.verbose, use_manifest,
    )
    sync_secs = time.monotonic() - t_sync

    if ok:
        print(f"✓ Sync complete ({sync_secs:.0f}s)")
        if args.verbose and output:
            for line in output.splitlines():
                print(f"  {line}")
        return 0
    else:
        print(f"✗ Sync failed — {output}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
