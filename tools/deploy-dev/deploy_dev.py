"""Deploy working-tree datasheet changes to the dev game server over SSH.

Discovers every modified, added, deleted, renamed, or untracked file in the
local server datasheet repo (via git status, exactly what TortoiseGit's commit
dialog shows) and mirrors those changes to the dev game server's datasheet
folder over a single sftp batch session. The remote datasheet folder lives
inside a git clone of the payload repo, so the tool also offers remote status
(what is overlaid vs HEAD) and remote revert (restore clean payload state).

Connection and paths resolve from reforged/.references:
  server_datasheet      local datasheet repo (git working tree)
  dev_server_ssh        SSH target or alias (key-based auth)
  dev_server_datasheet  remote datasheet path, forward slashes

Datasheet changes load at world server startup only; restart the dev world
server manually after deploying (restart automation is deferred).
"""

import argparse
import hashlib
import posixpath
import subprocess
import sys
import tempfile
from pathlib import Path

REFERENCES = Path(__file__).resolve().parents[2] / ".references"
REMOTE_GIT_FALLBACK = "C:/Program Files/Git/cmd/git.exe"
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]


def read_references() -> dict[str, str]:
    if not REFERENCES.exists():
        sys.exit(f"Error: {REFERENCES} not found. Copy .references.example and fill in your paths.")
    refs: dict[str, str] = {}
    for line in REFERENCES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        refs[key.strip()] = value.strip()
    return refs


def require_keys(refs: dict[str, str], keys: list[str]) -> None:
    missing = [k for k in keys if not refs.get(k)]
    if missing:
        sys.exit(f"Error: missing .references key(s): {', '.join(missing)}")


def get_changes(root: Path) -> tuple[list[str], list[str]]:
    """Return (paths_to_copy, paths_to_delete) relative to root, forward slashes.

    root may be a subdirectory of the git repo (e.g. Datasheet/ inside the
    payload repo). git reports repo-root-relative paths, so entries are
    filtered to the subtree and the prefix is stripped; changes elsewhere in
    the repo are ignored.
    """
    prefix = subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=str(root),
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8").strip()

    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", "."],
        cwd=str(root),
        capture_output=True,
        check=True,
    )
    entries = result.stdout.decode("utf-8").split("\0")

    def in_scope(path: str) -> str | None:
        if not prefix:
            return path
        return path[len(prefix):] if path.startswith(prefix) else None

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
            new_rel = in_scope(path)
            old_rel = in_scope(old_path) if old_path else None
            if new_rel:
                copies.append(new_rel)
            if status[0] == "R" and old_rel:
                deletes.append(old_rel)
            i += 2
            continue

        rel = in_scope(path)
        if rel is None:
            i += 1
            continue
        if (root / rel).exists():
            copies.append(rel)
        else:
            deletes.append(rel)
        i += 1

    # 'nul' is a Windows reserved name; it cannot be read for transfer.
    blocked = [p for p in copies if posixpath.basename(p).lower() == "nul"]
    for p in blocked:
        print(f"Warning: skipping reserved-name file (delete it locally): {p}")
        copies.remove(p)

    return copies, deletes


def build_sftp_batch(local_root: Path, remote_root: str, copies: list[str], deletes: list[str]) -> str:
    # Windows OpenSSH sftp resolves "D:/..." relative to the home directory;
    # drive-letter paths must be written "/D:/..." to be absolute.
    if len(remote_root) > 1 and remote_root[1] == ":":
        remote_root = "/" + remote_root
    lines: list[str] = []

    dirs: set[str] = set()
    for rel in copies:
        d = posixpath.dirname(rel)
        while d:
            dirs.add(d)
            d = posixpath.dirname(d)
    # Parents before children; '-' prefix ignores already-exists errors.
    for d in sorted(dirs, key=lambda p: p.count("/")):
        lines.append(f'-mkdir "{remote_root}/{d}"')

    for rel in sorted(copies):
        local = (local_root / rel).as_posix()
        lines.append(f'put "{local}" "{remote_root}/{rel}"')

    for rel in sorted(deletes):
        lines.append(f'-rm "{remote_root}/{rel}"')

    return "\n".join(lines) + "\n"


def run_sftp(target: str, batch: str) -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".sftp", delete=False, encoding="utf-8") as f:
        f.write(batch)
        batch_path = f.name
    try:
        result = subprocess.run(["sftp", *SSH_OPTS, "-b", batch_path, target])
        return result.returncode
    finally:
        Path(batch_path).unlink(missing_ok=True)


def run_ssh(target: str, command: str) -> subprocess.CompletedProcess:
    return subprocess.run(["ssh", *SSH_OPTS, target, command], capture_output=True, text=True)


def remote_git(target: str, git_args: str) -> subprocess.CompletedProcess:
    result = run_ssh(target, f"git {git_args}")
    if "not recognized" in (result.stderr or "") or "not recognized" in (result.stdout or ""):
        result = run_ssh(target, f"& '{REMOTE_GIT_FALLBACK}' {git_args}")
    return result


def split_remote_root(remote_root: str) -> tuple[str, str]:
    """Return (repo_root, datasheet_subdir) from the remote datasheet path."""
    return posixpath.dirname(remote_root), posixpath.basename(remote_root)


def cmd_status(target: str, remote_root: str) -> int:
    repo, subdir = split_remote_root(remote_root)
    result = remote_git(target, f"-C {repo} status --short -- {subdir}")
    out = result.stdout.strip()
    print(out if out else "Dev server datasheet is clean (matches payload HEAD).")
    if result.returncode != 0:
        print(result.stderr.strip())
    return result.returncode


def cmd_revert(target: str, remote_root: str, assume_yes: bool) -> int:
    repo, subdir = split_remote_root(remote_root)
    if not assume_yes:
        answer = input(f"Revert {remote_root} on the dev server to clean payload state? [y/N] ")
        if answer.strip().lower() != "y":
            print("Aborted.")
            return 1
    checkout = remote_git(target, f"-C {repo} checkout -f -- {subdir}")
    clean = remote_git(target, f"-C {repo} clean -fd -- {subdir}")
    print(checkout.stdout.strip() or "checkout: done")
    print(clean.stdout.strip() or "clean: nothing to remove")
    if checkout.returncode or clean.returncode:
        print(checkout.stderr.strip(), clean.stderr.strip())
        return 1
    print("Dev server datasheet restored to payload HEAD. Restart the world server to load it.")
    return 0


def verify(target: str, local_root: Path, remote_root: str, copies: list[str]) -> int:
    mismatches = 0
    chunk_size = 40
    for start in range(0, len(copies), chunk_size):
        chunk = sorted(copies)[start : start + chunk_size]
        paths_ps = ",".join(f"'{remote_root}/{rel}'" for rel in chunk)
        command = (
            f"@({paths_ps}) | ForEach-Object {{ "
            f"(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLower() + '|' + $_ }}"
        )
        result = run_ssh(target, command)
        remote_hashes = {}
        for line in result.stdout.splitlines():
            if "|" in line:
                digest, _, path = line.partition("|")
                remote_hashes[path.strip()] = digest.strip()
        for rel in chunk:
            local_hash = hashlib.sha256((local_root / rel).read_bytes()).hexdigest()
            remote_hash = remote_hashes.get(f"{remote_root}/{rel}")
            if remote_hash != local_hash:
                print(f"  MISMATCH: {rel} (local {local_hash[:12]} vs remote {remote_hash or 'missing'})")
                mismatches += 1
    if mismatches:
        print(f"Verify FAILED: {mismatches} file(s) differ.")
        return 1
    print(f"Verify OK: {len(copies)} file(s) match.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deploy working-tree datasheet changes to the dev game server over SSH."
    )
    parser.add_argument("--dry-run", action="store_true", help="List planned actions without transferring")
    parser.add_argument("--verify", action="store_true", help="Compare SHA256 of transferred files after deploy")
    parser.add_argument("--status", action="store_true", help="Show what is overlaid on the dev server vs payload HEAD")
    parser.add_argument("--revert", action="store_true", help="Restore the dev server datasheet to clean payload state")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt for --revert")
    args = parser.parse_args()

    refs = read_references()
    require_keys(refs, ["server_datasheet", "dev_server_ssh", "dev_server_datasheet"])
    local_root = Path(refs["server_datasheet"])
    target = refs["dev_server_ssh"]
    remote_root = refs["dev_server_datasheet"].replace("\\", "/").rstrip("/")

    if args.status:
        return cmd_status(target, remote_root)
    if args.revert:
        return cmd_revert(target, remote_root, args.yes)

    try:
        copies, deletes = get_changes(local_root)
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
        sys.exit(f"Error: git failed in {local_root}: {err.strip()}")

    if not copies and not deletes:
        print("No working-tree changes; nothing to deploy.")
        return 0

    print(f"Deploying from {local_root} to {target}:{remote_root}")
    if copies:
        print(f"\n{len(copies)} file(s) to copy:")
        for f in sorted(copies):
            print(f"  + {f}")
    if deletes:
        print(f"\n{len(deletes)} file(s) to delete:")
        for f in sorted(deletes):
            print(f"  - {f}")

    if args.dry_run:
        print("\nDry run; nothing transferred.")
        return 0

    print()
    code = run_sftp(target, build_sftp_batch(local_root, remote_root, copies, deletes))
    if code != 0:
        print(f"Deploy FAILED: sftp exited with code {code}.")
        return code

    print(f"Done: {len(copies)} copied, {len(deletes)} delete(s) issued.")

    if args.verify and copies:
        code = verify(target, local_root, remote_root, copies)
        if code != 0:
            return code

    print("\nReminder: datasheet changes load at world server startup only.")
    print("Restart the dev world server manually to pick them up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
