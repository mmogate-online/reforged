"""Push working-tree changes from the server datasheet repo to the server share.

Uses `git status` to discover every modified, added, deleted, renamed, or
untracked file in the server datasheet folder (exactly what TortoiseGit's
commit dialog shows) and mirrors those changes to the destination share,
preserving subdirectory structure.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def get_changes(repo: Path) -> tuple[list[str], list[str]]:
    """Return (paths_to_copy, paths_to_delete) as repo-relative forward-slash paths."""
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    data = result.stdout.decode("utf-8")
    entries = data.split("\0")

    copies: list[str] = []
    deletes: list[str] = []

    i = 0
    while i < len(entries):
        entry = entries[i]
        if not entry:
            i += 1
            continue

        status = entry[:2]
        path = entry[3:]

        # -z porcelain: renames/copies emit "XY new\0old"
        if status[0] in ("R", "C"):
            old_path = entries[i + 1] if i + 1 < len(entries) else ""
            copies.append(path)
            if status[0] == "R" and old_path:
                deletes.append(old_path)
            i += 2
            continue

        # Ignored files only appear with --ignored, so we won't see "!!" here.
        src = repo / path
        if src.exists():
            copies.append(path)
        else:
            deletes.append(path)
        i += 1

    return copies, deletes


def push(src: Path, dst: Path, copies: list[str], deletes: list[str]) -> tuple[int, int]:
    copied = 0
    for rel in sorted(copies):
        src_file = src / rel
        dst_file = dst / rel
        if not src_file.exists():
            print(f"Warning: source file not found: {src_file}")
            continue
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        copied += 1

    deleted = 0
    for rel in sorted(deletes):
        dst_file = dst / rel
        if dst_file.exists():
            dst_file.unlink()
            deleted += 1
        else:
            print(f"Note: delete target not present on share: {rel}")

    return copied, deleted


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mirror working-tree changes from the server datasheet to the server share."
    )
    parser.add_argument("--src", required=True, help="Source server datasheet path (must be a git repo)")
    parser.add_argument("--dst", required=True, help="Destination server share path")
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)

    if not (src / ".git").exists():
        print(f"Error: {src} is not a git repository")
        return 1

    try:
        copies, deletes = get_changes(src)
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
        print(f"Error: git status failed — {err.strip()}")
        return 1

    if not copies and not deletes:
        print("No working-tree changes — nothing to push.")
        return 0

    print(f"Pushing changes from {src} to {dst}")
    if copies:
        print(f"\n{len(copies)} file(s) to copy:")
        for f in sorted(copies):
            print(f"  + {f}")
    if deletes:
        print(f"\n{len(deletes)} file(s) to delete:")
        for f in sorted(deletes):
            print(f"  - {f}")

    print()
    copied, deleted = push(src, dst, copies, deletes)
    print(f"Done — {copied} copied, {deleted} deleted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
