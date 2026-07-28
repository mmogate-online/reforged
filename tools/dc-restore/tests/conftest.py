"""Shared fixtures for the dc-restore test suite.

Two tiers, deliberately separated, because they answer different questions.

  hermetic  Synthetic XML, either committed under tests/fixtures/ or built into
            tmp_path by the `corpus_dir` factory. Needs no .references and no
            private repo, so it runs on any clone. This tier owns parser edge
            cases: sentinel encodings, malformed values, anomaly shapes.

  corpus    The real v92 server datasheet, read at the PINNED commit below.
            Marked `corpus` and skipped with a stated reason when the private
            repo is unavailable. This tier owns the anti-hallucination question:
            does the check actually fire on the real historical defect it was
            written for.

BASELINE_REF is pinned, never HEAD. The defects the audit checks were born from
live in the datasheet as it stood before the patch-002 trimming wave; HEAD moves
forward every time a patch closes, and an unpinned oracle would silently invert
from "fires on the defect" to "asserts nothing" on that day.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

# Server datasheet state before the patch-002 IoD trimming and redistribution
# wave (specs 002/27 through 002/33). Every corpus-tier defect assertion is
# measured here. Do not change this to HEAD or to a newer commit.
BASELINE_REF = "789fec28"

TESTS_DIR = Path(__file__).resolve().parent
TOOL_DIR = TESTS_DIR.parent
REFORGED_DIR = TOOL_DIR.parents[1]


def _read_references() -> dict[str, str]:
    """Parse reforged/.references, or return an empty map when it is absent."""
    ref_file = REFORGED_DIR / ".references"
    if not ref_file.exists():
        return {}
    refs: dict[str, str] = {}
    for line in ref_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if value:
            refs[key.strip()] = value.strip()
    return refs


@pytest.fixture(scope="session")
def references() -> dict[str, str]:
    return _read_references()


@pytest.fixture
def fixtures_dir() -> Path:
    """Root of the committed synthetic fixture corpora."""
    return TESTS_DIR / "fixtures"


@pytest.fixture
def corpus_dir(tmp_path: Path):
    """Factory building a synthetic datasheet tree from a {relpath: text} map.

    Writes UTF-8 with a BOM and CRLF newlines, matching how the server writes
    .quest and NpcData files, so parsers are exercised against the real byte
    shape rather than a tidied one.
    """

    def build(files: dict[str, str], *, bom: bool = True, crlf: bool = True) -> Path:
        root = tmp_path / "datasheet"
        for relpath, text in files.items():
            path = root / relpath
            path.parent.mkdir(parents=True, exist_ok=True)
            body = text.replace("\r\n", "\n")
            if crlf:
                body = body.replace("\n", "\r\n")
            data = body.encode("utf-8")
            path.write_bytes(b"\xef\xbb\xbf" + data if bom else data)
        return root

    return build


# ---------------------------------------------------------------------------
# Corpus tier: the real datasheet at the pinned baseline
# ---------------------------------------------------------------------------

def _skip(reason: str):
    pytest.skip(f"corpus tier unavailable: {reason}")


@pytest.fixture(scope="session")
def datasheet_dir(references: dict[str, str]) -> Path:
    """The v92 server datasheet directory, or a stated skip."""
    raw = references.get("server_datasheet")
    if not raw:
        _skip("reforged/.references has no server_datasheet key")
    path = Path(raw)
    if not path.exists():
        _skip(f"server_datasheet path does not exist: {path}")
    return path


@pytest.fixture(scope="session")
def baseline_ref(datasheet_dir: Path) -> str:
    """The pinned baseline commit, proven resolvable in the datasheet repo."""
    probe = subprocess.run(
        ["git", "-C", str(datasheet_dir), "cat-file", "-e", f"{BASELINE_REF}^{{commit}}"],
        capture_output=True,
    )
    if probe.returncode != 0:
        _skip(f"baseline commit {BASELINE_REF} is not present in the datasheet repo")
    return BASELINE_REF


@pytest.fixture(scope="session")
def baseline(datasheet_dir: Path, baseline_ref: str):
    """A V92Baseline pinned to the historical defect state."""
    from dclib import V92Baseline

    return V92Baseline(datasheet_dir, ref=baseline_ref)


@pytest.fixture(scope="session")
def worktree_baseline(datasheet_dir: Path):
    """A V92Baseline reading the current working tree (the post-wave state).

    Paired with `baseline` for the fire-then-quiet assertions: a high check must
    fire on the pinned defect state and stay quiet here.
    """
    from dclib import V92Baseline

    class _Worktree(V92Baseline):
        def read(self, relpath: str, baseline: bool = True) -> str | None:
            return super().read(relpath, baseline=False)

    return _Worktree(datasheet_dir)


def git_show(datasheet_dir: Path, ref: str, relpath: str) -> str | None:
    """Independent oracle: read a datasheet file straight from git.

    Used to verify V92Baseline against something other than itself.
    """
    root = subprocess.run(
        ["git", "-C", str(datasheet_dir), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if root.returncode != 0:
        return None
    repo_root = Path(root.stdout.strip())
    prefix = datasheet_dir.resolve().relative_to(repo_root).as_posix()
    r = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{prefix}/{relpath}"],
        capture_output=True,
    )
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8-sig", errors="replace")
