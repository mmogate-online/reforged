"""Push only the files modified by a patch run to the server share.

Reads manifests from .manifests/<patch>/ and copies only the listed
modified_files from src to dst, preserving directory structure.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def collect_files(manifests_base: Path, patches: list[str]) -> set[str]:
    files: set[str] = set()
    for patch in patches:
        patch_dir = manifests_base / patch
        if not patch_dir.is_dir():
            print(f"Warning: no manifests found for patch {patch} at {patch_dir}")
            continue
        for f in patch_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            files.update(data.get("modified_files", []))
    return files


def push(src: Path, dst: Path, files: set[str]) -> int:
    copied = 0
    for rel in sorted(files):
        rel_path = Path(rel)
        src_file = src / rel_path
        dst_file = dst / rel_path
        if not src_file.exists():
            print(f"Warning: source file not found: {src_file}")
            continue
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        copied += 1
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="Push manifest-listed files to server share.")
    parser.add_argument("--patches", nargs="+", required=True, help="Patch folder names (e.g. 001 002)")
    parser.add_argument("--src", required=True, help="Source server datasheet path")
    parser.add_argument("--dst", required=True, help="Destination server share path")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    manifests_base = project_root / "reforged" / "tools" / "migrate" / ".manifests"

    files = collect_files(manifests_base, args.patches)
    if not files:
        print("No modified files found in manifests — nothing to push.")
        return 0

    print(f"Pushing {len(files)} file(s) to {args.dst} ...")
    for f in sorted(files):
        print(f"  {f}")

    copied = push(Path(args.src), Path(args.dst), files)
    print(f"Done — {copied} file(s) pushed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
