"""Client-side deploy pipeline: pack, install, publish.

Takes an ALREADY-SYNCED unpacked client DataCenter and ships it:

  1. pack    Repack the client DataCenter into DataCenter_Final_EUR.dat.
  2. install Copy the .dat into the local game client (no sidecar/backup files).
  3. publish Build, sign, dry-run gate, and (only with --publish) upload a new
             dev-channel release to Cloudflare R2, then record it.

THIS TOOL DOES NOT SYNC. Populating the unpacked client DC from the server
datasheets is owned entirely by tools/migrate/migrate.py, which syncs every
entity declared in config/sync-config.yaml, narrowed by the apply manifest to
the files a patch actually touched. Run migrate first, then this tool.

A --sync stage used to live here. It only ever mapped ONE family
(QuestData/*.quest -> Quest) and reported every other dirty family as
"no sync mapping, server-only or handle manually" -- which silently went stale
as sync-config gained entities, so families that WERE syncable got flagged as
manual work. Removed rather than fixed: two tools syncing is the actual defect.

Everything resolves from reforged/.references; no machine paths, hostnames, or
credentials are hardcoded. Credentials are read into the subprocess env only and
never printed.

Stages are independent flags. --all runs pack+install and the publish stage in
dry-run-only mode; committing a publish upload always requires an explicit
--publish. --dry-run prints every command without executing anything. No flags
prints help.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REFERENCES = Path(__file__).resolve().parents[2] / ".references"

EXIT_OK = 0
EXIT_CONFIG = 1   # missing key, path mismatch, missing credentials
EXIT_STAGE = 2    # a pipeline stage failed


# --------------------------------------------------------------------------- #
# .references + small helpers
# --------------------------------------------------------------------------- #

def read_references() -> dict:
    if not REFERENCES.exists():
        sys.exit(f"Error: {REFERENCES} not found. Copy .references.example and fill in your paths.")
    refs: dict = {}
    for line in REFERENCES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        refs[key.strip()] = value.strip()
    return refs


def require_keys(refs: dict, keys: list, stage: str) -> None:
    missing = [k for k in keys if not refs.get(k)]
    if missing:
        sys.exit(f"Error ({stage}): missing .references key(s): {', '.join(missing)}")


def utcnow_dotnet() -> str:
    """UTC ISO timestamp matching the .NET style used in reforged.rporigin."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f0Z")


def run_streamed(cmd: list, cwd=None, env=None, throttle: float = 2.0) -> int:
    """Run a command, collapsing chatty progress output to occasional updates.

    novadrop-dc / the patcher CLI emit many progress lines; print at most one
    line every `throttle` seconds, and always print the final line.
    """
    proc = subprocess.Popen(
        cmd, cwd=cwd if cwd is None else str(cwd), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
    )
    last_print = 0.0
    last_line = ""
    captured: list = []
    assert proc.stdout is not None
    for raw in proc.stdout:
        line = raw.rstrip()
        if not line:
            continue
        captured.append(line)
        last_line = line
        now = time.monotonic()
        if now - last_print >= throttle:
            print(f"  {line}")
            last_print = now
    proc.wait()
    if last_line:
        print(f"  {last_line}")
    return proc.returncode


# --------------------------------------------------------------------------- #
# Stage: pack
# --------------------------------------------------------------------------- #

def parse_enc_keys(bat_path: Path):
    if not bat_path.exists():
        sys.exit(f"Error (pack): {bat_path} not found (needed for encryption key/iv).")
    text = bat_path.read_text(encoding="utf-8", errors="replace")
    k = re.search(r"--encryption-key\s+(\S+)", text)
    iv = re.search(r"--encryption-iv\s+(\S+)", text)
    if not k or not iv:
        sys.exit(f"Error (pack): could not parse --encryption-key/--encryption-iv from {bat_path}.")
    return k.group(1), iv.group(1)


def stage_pack(refs: dict, args) -> int:
    require_keys(refs, ["client_pack_dir"], "pack")
    pack_dir = Path(refs["client_pack_dir"])
    exe = pack_dir / "novadrop-dc_92.04" / "novadrop-dc.exe"
    key, iv = parse_enc_keys(pack_dir / "enc_EUR.bat")

    cmd = [str(exe), "pack", "--encryption-key", key, "--encryption-iv", iv,
           "DataCenter_Final_EUR", "DataCenter_Final_EUR.dat"]

    print("Pack: repacking client DataCenter into DataCenter_Final_EUR.dat (this takes ~1-3 min).")
    if args.dry_run:
        # Do not print the actual key/iv in dry-run.
        preview = [str(exe), "pack", "--encryption-key", "<KEY>", "--encryption-iv", "<IV>",
                   "DataCenter_Final_EUR", "DataCenter_Final_EUR.dat"]
        print(f"  [dry-run] would run: {' '.join(preview)}  (cwd={pack_dir})")
        return EXIT_OK

    if not exe.exists():
        print(f"Pack FAILED: novadrop-dc.exe not found at {exe}")
        return EXIT_STAGE

    code = run_streamed(cmd, cwd=pack_dir)
    if code != 0:
        print(f"Pack FAILED: novadrop-dc exited with code {code}.")
        return EXIT_STAGE
    print("Pack OK.")
    return EXIT_OK


# --------------------------------------------------------------------------- #
# Stage: install
# --------------------------------------------------------------------------- #

def stage_install(refs: dict, args) -> int:
    require_keys(refs, ["client_pack_dir", "game_client_install"], "install")
    src = Path(refs["client_pack_dir"]) / "DataCenter_Final_EUR.dat"
    dst = Path(refs["game_client_install"]) / "S1Game" / "S1Data" / "DataCenter_Final_EUR.dat"

    print(f"Install: {src} -> {dst}")
    if args.dry_run:
        print("  [dry-run] would copy the packed .dat into the game install (no backup file).")
        return EXIT_OK

    if not src.exists():
        print(f"Install FAILED: packed file not found: {src} (run pack first).")
        return EXIT_STAGE

    # Refuse if the target is locked (game running) rather than copy over a live file.
    if dst.exists():
        try:
            with open(dst, "r+b"):
                pass
        except PermissionError:
            print(f"Install FAILED: target is locked: {dst}. Close the game client and retry.")
            return EXIT_STAGE

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    # Hard rule: no sidecar/backup files in the install tree (the patcher chunks
    # the whole directory and would ship strays to players). We create none.
    print("Install OK (no backup/sidecar file written).")
    return EXIT_OK


# --------------------------------------------------------------------------- #
# Stage: publish
# --------------------------------------------------------------------------- #

def load_rporigin(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def next_dev_version(origin: dict):
    dev = [r for r in origin.get("Releases", []) if r.get("Channel") == "dev"]
    if not dev:
        sys.exit("Error (publish): no existing dev release in reforged.rporigin Releases[].")
    last = dev[-1]["Version"]
    m = re.match(r"(\d+\.\d+\.\d+)-dev\.(\d+)$", last)
    if not m:
        sys.exit(f"Error (publish): cannot parse dev version '{last}'.")
    return f"{m.group(1)}-dev.{int(m.group(2)) + 1}", last


def read_env_file(path: Path) -> dict:
    out: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip()
    return out


def append_release(origin_path: Path, entry: dict) -> None:
    """Insert a new Releases[] object as text, preserving indent and CRLF."""
    # read_bytes (not read_text) so CRLF is not translated to LF on read.
    text = origin_path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    close_idx = text.rfind(nl + "  ]")
    if close_idx < 0:
        raise ValueError("could not locate Releases array close in reforged.rporigin")
    brace_idx = text.rfind("}", 0, close_idx)
    if brace_idx < 0:
        raise ValueError("could not locate last Releases entry in reforged.rporigin")

    fi = "      "  # field indent (6 spaces)
    ei = "    "     # entry indent (4 spaces)
    # json.dumps each value so backslashes/quotes are escaped like the existing entries.
    fields = ["Version", "ManifestPath", "MerkleRoot", "Channel", "BuiltUtc", "PublishedUtc"]
    lines = [ei + "{"]
    for i, name in enumerate(fields):
        sep = "," if i < len(fields) - 1 else ""
        lines.append(fi + f'"{name}": {json.dumps(entry[name])}{sep}')
    lines.append(ei + "}")
    block = nl.join(lines)
    new_text = text[:brace_idx + 1] + "," + nl + block + text[brace_idx + 1:]
    origin_path.write_text(new_text, encoding="utf-8", newline="")


def prepend_log(log_path: Path, version: str, delta: str, note: str) -> None:
    text = log_path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title = f"## {date}: {version} published: {note}"
    bullet = (f"- Published `{version}` to the dev channel (build, sign, dry-run gate, "
              f"publish). {delta}")
    section = nl + nl + title + nl + nl + bullet
    first_nl = text.find(nl)
    if first_nl < 0:  # single-line file; just append
        new_text = text + section
    else:
        new_text = text[:first_nl] + section + text[first_nl:]
    log_path.write_text(new_text, encoding="utf-8", newline="")


def summarize_delta(output: str) -> str:
    """Best-effort chunk delta summary from patcher publish output."""
    hits = []
    for line in output.splitlines():
        low = line.lower()
        if any(t in low for t in ("upload", "reused", "chunk", "mib", "committed")):
            hits.append(line.strip())
    return "; ".join(hits[:4]) if hits else "chunk delta unavailable"


def stage_publish(refs: dict, args) -> int:
    require_keys(refs, ["patcher_origin", "game_client_install"], "publish")
    origin_dir = Path(refs["patcher_origin"])
    game_install = Path(refs["game_client_install"])

    publish_exe = origin_dir / "tools" / "ReforgedPatcher.Publish.exe"
    rpignore_src = origin_dir / "build-source.rpignore"
    rporigin_path = origin_dir / "reforged.rporigin"
    env_path = origin_dir / ".tmp" / "r2-publish.env"
    priv_key = origin_dir / ".tmp" / "priv.key"
    pub_key = origin_dir / ".tmp" / "pub.key"
    log_path = origin_dir / "deployment-log.md"
    rpignore_dst = game_install / ".rpignore"

    commit = args.publish and not args.dry_run  # --all alone -> dry-run gate only

    # 2. Read origin profile.
    origin = load_rporigin(rporigin_path)
    game_dir_cfg = origin.get("GameDirectory", "")
    if os.path.normcase(os.path.normpath(game_dir_cfg)) != \
       os.path.normcase(os.path.normpath(str(game_install))):
        print(f"Publish FAILED: reforged.rporigin GameDirectory ({game_dir_cfg}) "
              f"does not match game_client_install ({game_install}).")
        return EXIT_CONFIG

    workspace = origin["WorkspaceDirectory"]
    avg = str(origin["ChunkAvgSize"])
    target = origin["Targets"][0]
    endpoint = target["Endpoint"]
    bucket = target["Bucket"]
    version, prev = next_dev_version(origin)
    store = os.path.join(workspace, "store")
    manifest = os.path.join(workspace, f"{version}.rpm")

    print(f"Publish: {prev} -> {version} (channel dev)")

    if args.dry_run:
        print("  [dry-run] would stage build-source.rpignore, build, sign, and publish --dry-run:")
        print(f"    copy {rpignore_src} -> {rpignore_dst}")
        print(f"    {publish_exe} build {game_dir_cfg} {store} {manifest} --version {version} --avg {avg}")
        print(f"    {publish_exe} sign {manifest} .tmp/priv.key")
        print(f"    {publish_exe} publish {store} {manifest} --target s3 --endpoint {endpoint} "
              f"--bucket {bucket} --region auto --channel dev --pubkey .tmp/pub.key "
              f"--concurrency 64 --dry-run")
        print("  [dry-run] commit publish + rporigin/log append only with explicit --publish.")
        return EXIT_OK

    # 3. Credentials.
    for p, what in ((env_path, "R2 credentials env"), (priv_key, "signing key"), (pub_key, "public key")):
        if not p.exists():
            print(f"Publish FAILED: missing {what}: {p}. Decrypt with sops per the "
                  f"patcher-origin README before publishing.")
            return EXIT_CONFIG
    creds = read_env_file(env_path)
    if not creds.get("RP_S3_ACCESS_KEY") or not creds.get("RP_S3_SECRET_KEY"):
        print(f"Publish FAILED: RP_S3_ACCESS_KEY / RP_S3_SECRET_KEY not set in {env_path}.")
        return EXIT_CONFIG
    env = dict(os.environ)
    env.update(creds)

    # 1. Stage ignore rules into the game install (overwrite).
    shutil.copyfile(rpignore_src, rpignore_dst)
    print(f"  Staged {rpignore_src.name} -> {rpignore_dst}")

    # 4. Build.
    built_utc = utcnow_dotnet()
    build_cmd = [str(publish_exe), "build", game_dir_cfg, store, manifest,
                 "--version", version, "--avg", avg]
    print(f"  Building {version} ...")
    bproc = subprocess.run(build_cmd, cwd=str(origin_dir), env=env,
                           capture_output=True, text=True)
    print_indented(bproc.stdout)
    if bproc.returncode != 0:
        print(f"Publish FAILED: build exited {bproc.returncode}: {bproc.stderr.strip()}")
        return EXIT_STAGE
    mm = re.search(r"merkle root[:\s]+([0-9a-fA-F]{64})", bproc.stdout, re.I)
    if not mm:
        print("Publish FAILED: could not parse merkle root from build output.")
        return EXIT_STAGE
    merkle = mm.group(1)
    print(f"  Merkle root: {merkle}")

    # 5. Sign.
    sign_cmd = [str(publish_exe), "sign", manifest, ".tmp/priv.key"]
    sproc = subprocess.run(sign_cmd, cwd=str(origin_dir), env=env,
                           capture_output=True, text=True)
    print_indented(sproc.stdout)
    if sproc.returncode != 0:
        print(f"Publish FAILED: sign exited {sproc.returncode}: {sproc.stderr.strip()}")
        return EXIT_STAGE
    print("  Signed manifest.")

    # 6. Dry-run publish (always).
    base_pub = [str(publish_exe), "publish", store, manifest, "--target", "s3",
                "--endpoint", endpoint, "--bucket", bucket, "--region", "auto",
                "--channel", "dev", "--pubkey", ".tmp/pub.key", "--concurrency", "64"]
    dry = base_pub + ["--dry-run"]
    print("  Publish dry-run (reused / to-upload summary):")
    dproc = subprocess.run(dry, cwd=str(origin_dir), env=env, capture_output=True, text=True)
    print_indented(dproc.stdout)
    if dproc.returncode != 0:
        print(f"Publish FAILED: dry-run exited {dproc.returncode}: {dproc.stderr.strip()}")
        return EXIT_STAGE
    delta = summarize_delta(dproc.stdout)

    if not commit:
        print("  Publish dry-run only (no upload). Rerun with --publish to commit.")
        return EXIT_OK

    # Commit publish; require committed=True.
    print("  Committing publish (uploading to R2) ...")
    pproc = subprocess.run(base_pub, cwd=str(origin_dir), env=env, capture_output=True, text=True)
    print_indented(pproc.stdout)
    if pproc.returncode != 0 or "committed=True" not in pproc.stdout:
        print(f"Publish FAILED: commit did not report committed=True "
              f"(exit {pproc.returncode}). {pproc.stderr.strip()}")
        return EXIT_STAGE
    published_utc = utcnow_dotnet()
    delta = summarize_delta(pproc.stdout) or delta

    # 7. Record the release.
    note = args.note or "(no note provided)"
    append_release(rporigin_path, {
        "Version": version,
        "ManifestPath": manifest,
        "MerkleRoot": merkle,
        "Channel": "dev",
        "BuiltUtc": built_utc,
        "PublishedUtc": published_utc,
    })
    prepend_log(log_path, version, f"{delta}. {note}. Merkle root `{merkle}`.", note)
    print(f"Publish OK: {version} committed; reforged.rporigin and deployment-log.md updated.")
    return EXIT_OK


def print_indented(text: str) -> None:
    for line in (text or "").splitlines():
        if line.strip():
            print(f"  {line}")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Client-side deploy pipeline: pack, install, publish. "
                    "Syncing is owned by tools/migrate/migrate.py; run it first.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Syncing the unpacked client DC is NOT done here. Run\n"
            "  python reforged/tools/migrate/migrate.py --patch <id>\n"
            "first; it applies the patch and syncs every entity in sync-config.yaml,\n"
            "narrowed by the apply manifest. Then ship the result with this tool.\n"
            "\n"
            "Examples:\n"
            "  python deploy_client.py --all --dry-run      print every command, run nothing\n"
            "  python deploy_client.py --all --note \"...\"    pack+install+publish dry-run\n"
            "  python deploy_client.py --publish --note \"...\"  commit the reviewed publish\n"
        ),
    )
    parser.add_argument("--pack", action="store_true", help="Repack the client DataCenter .dat")
    parser.add_argument("--install", action="store_true", help="Copy the packed .dat into the game install")
    parser.add_argument("--publish", action="store_true", help="Publish stage; commits the R2 upload")
    parser.add_argument("--all", action="store_true",
                        help="pack+install and publish in dry-run-only mode")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print every command without executing")
    parser.add_argument("--note", metavar="TEXT", help="Content summary for the deployment-log entry")
    args = parser.parse_args()

    refs = read_references()

    run_pack = args.pack or args.all
    run_install = args.install or args.all
    run_publish = args.publish or args.all

    if not (run_pack or run_install or run_publish):
        parser.print_help()
        return EXIT_OK

    stages = []
    if run_pack:
        stages.append(("pack", lambda: stage_pack(refs, args)))
    if run_install:
        stages.append(("install", lambda: stage_install(refs, args)))
    if run_publish:
        stages.append(("publish", lambda: stage_publish(refs, args)))

    for name, fn in stages:
        print(f"== Stage: {name} ==")
        code = fn()
        print()
        if code != EXIT_OK:
            print(f"Pipeline stopped at stage '{name}' (exit {code}).")
            return code

    print("Pipeline complete.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
