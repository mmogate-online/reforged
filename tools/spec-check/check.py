"""Validate or apply a single DSL spec against the datasheet repo's HEAD.

Designed for quick sanity checks — especially non-idempotent specs
(balanceProfiles with multiply/add) that need a stable read baseline to
produce deterministic output.

By default runs `dsl validate` against HEAD of the datasheet repo. Pass
--apply to actually write (still reading from HEAD unless --no-source-ref).
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def load_references(project_root: Path) -> dict[str, str]:
    refs: dict[str, str] = {}
    ref_file = project_root / "reforged" / ".references"
    for line in ref_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if value:
            refs[key.strip()] = value.strip()
    return refs


def resolve_head(datasheet_dir: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=datasheet_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def resolve_branch(datasheet_dir: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=datasheet_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate or apply a single DSL spec. Reads datasheets from the "
            "datasheet repo's current HEAD for a deterministic baseline."
        )
    )
    parser.add_argument("spec", help="Path to YAML spec file")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually apply the spec (writes to datasheet working tree). Default is validate-only.",
    )
    parser.add_argument(
        "--ref",
        help="Override the git ref to read from (default: HEAD of the datasheet repo).",
    )
    parser.add_argument(
        "--no-source-ref",
        action="store_true",
        help="Disable --source-ref and read from the working tree directly (escape hatch).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Pass --verbose to the DSL command.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    refs = load_references(project_root)
    dsl_cli = refs.get("dsl_cli", str(project_root / "dsl.exe"))
    datasheet = refs["server_datasheet"]

    spec_path = Path(args.spec).resolve()
    if not spec_path.is_file():
        print(f"Error: Spec not found: {spec_path}")
        return 1

    source_ref: str | None = None
    if not args.no_source_ref:
        source_ref = args.ref or resolve_head(datasheet)
        if source_ref is None:
            print(
                f"Error: Could not resolve git HEAD in {datasheet}. "
                f"Is it a git repo? Use --no-source-ref to bypass."
            )
            return 1
        branch = resolve_branch(datasheet) if not args.ref else None
        source_label = args.ref or (f"HEAD ({branch})" if branch else "HEAD")
        print(f"Baseline: {source_label} → {source_ref[:12]}")
    else:
        print("Baseline: working tree (--no-source-ref)")

    subcommand = "apply" if args.apply else "validate"
    cmd = [dsl_cli, subcommand, str(spec_path), "--path", datasheet]
    if source_ref is not None:
        cmd.extend(["--source-ref", source_ref])
    if args.verbose:
        cmd.append("--verbose")

    print(f"Running: {subcommand} {spec_path.name}")
    print()
    sys.stdout.flush()
    result = subprocess.run(cmd, cwd=str(project_root))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
