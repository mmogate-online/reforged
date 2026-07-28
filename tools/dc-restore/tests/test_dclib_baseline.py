"""V92Baseline pinning semantics.

The regression oracle for every audit check is the datasheet as it stood at a
specific commit. Before this suite, V92Baseline could only read HEAD, and HEAD
advances every time a patch closes: an assertion written as "fires at HEAD"
quietly becomes "fires at the post-fix state", which is no assertion at all.

The hermetic tests build a throwaway git repo so the pinning behaviour is proven
from drift the test creates itself, rather than from whatever the real repo
happens to look like today (right now the real HEAD IS the pinned baseline, so
the real repo cannot distinguish the two code paths at all).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from conftest import git_show

from dclib import V92Baseline

V1 = "<Quest id=\"1\">v1 baseline</Quest>\n"
V2 = "<Quest id=\"1\">v2 committed after the baseline</Quest>\n"
V3 = "<Quest id=\"1\">v3 uncommitted overlay</Quest>\n"


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr}"
    return r.stdout.strip()


@pytest.fixture
def drifted_repo(tmp_path: Path) -> tuple[Path, str]:
    """A repo whose datasheet drifted twice past the pinned commit.

    Layout mirrors the real one: the datasheet is a subdirectory of the repo,
    not the repo root, because V92Baseline computes a prefix from that.

      commit 1 (pinned)  clean.quest = V1   dirty.quest = V1
      commit 2 (HEAD)    clean.quest = V1   dirty.quest = V2
      working tree       clean.quest = V1   dirty.quest = V3
    """
    repo = tmp_path / "repo"
    sheet = repo / "Datasheet" / "QuestData"
    sheet.mkdir(parents=True)
    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "harness@example.invalid")
    _git(repo, "config", "user.name", "harness")

    (sheet / "clean.quest").write_text(V1, encoding="utf-8")
    (sheet / "dirty.quest").write_text(V1, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "baseline")
    pinned = _git(repo, "rev-parse", "HEAD")

    (sheet / "dirty.quest").write_text(V2, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "post-baseline patch")

    (sheet / "dirty.quest").write_text(V3, encoding="utf-8")
    return repo / "Datasheet", pinned


def test_head_default_reads_worktree_for_clean_and_head_for_dirty(drifted_repo):
    """Unpinned behaviour is unchanged: HEAD for dirty files, disk for clean."""
    sheet, _ = drifted_repo
    b = V92Baseline(sheet)

    assert b.pinned is False
    assert b.read("QuestData/dirty.quest") == V2, "dirty file must come from HEAD"
    assert b.read("QuestData/clean.quest") == V1
    assert b.read("QuestData/dirty.quest", baseline=False) == V3, "opt out reads the overlay"


def test_pinned_ref_reads_the_baseline_not_head_or_worktree(drifted_repo):
    """The whole point: a pinned read returns the historical content."""
    sheet, pinned = drifted_repo
    b = V92Baseline(sheet, ref=pinned)

    assert b.pinned is True
    assert b.read("QuestData/dirty.quest") == V1, "must be the pinned content, not HEAD's V2"


def test_pinned_ref_does_not_fall_back_to_disk_for_clean_files(drifted_repo):
    """A file clean against HEAD can still differ from the pinned commit.

    This is the failure mode the pinning was written for: reading such a file
    off disk returns post-baseline content while the test believes it holds the
    historical state. Proven by making the file clean vs HEAD but different at
    the pinned commit.
    """
    sheet, _ = drifted_repo
    repo = sheet.parent
    (sheet / "QuestData" / "dirty.quest").write_text(V2, encoding="utf-8")  # now clean vs HEAD
    pinned = _git(repo, "rev-parse", "HEAD~1")

    b = V92Baseline(sheet, ref=pinned)

    assert b.is_dirty("QuestData/dirty.quest"), "differs from the pinned ref, so it is drift"
    assert b.read("QuestData/dirty.quest") == V1
    assert b.read("QuestData/dirty.quest", baseline=False) == V2


def test_pinned_drift_set_spans_commits_and_uncommitted_edits(drifted_repo):
    """dirty_files() against a pinned ref means differs-from-ref, both sources."""
    sheet, pinned = drifted_repo
    b = V92Baseline(sheet, ref=pinned)

    assert b.dirty_files() == {"QuestData/dirty.quest"}
    assert b.is_dirty("QuestData/dirty.quest")
    assert not b.is_dirty("QuestData/clean.quest")


def test_untracked_files_are_not_part_of_the_baseline(drifted_repo):
    """A patch that adds files leaves them untracked, and git diff cannot see them.

    Omitting them from the drift set makes a baseline read fall through to disk
    and count content that does not exist at the baseline at all. Measured on
    the real corpus: three patch-002 quest files leaked in that way, turning
    2,707 baseline quests into 2,710.
    """
    sheet, pinned = drifted_repo
    (sheet / "QuestData" / "added_by_patch.quest").write_text(V3, encoding="utf-8")

    b = V92Baseline(sheet, ref=pinned)

    assert b.is_dirty("QuestData/added_by_patch.quest")
    assert b.read("QuestData/added_by_patch.quest") is None, "absent at the baseline"
    assert b.read("QuestData/added_by_patch.quest", baseline=False) == V3


def test_absent_file_at_ref_returns_none(drifted_repo):
    sheet, pinned = drifted_repo
    b = V92Baseline(sheet, ref=pinned)

    assert b.read("QuestData/never-existed.quest") is None
    assert b.head_exists("QuestData/never-existed.quest") is False
    assert b.head_exists("QuestData/clean.quest") is True


# ---------------------------------------------------------------------------
# Corpus tier
# ---------------------------------------------------------------------------

@pytest.mark.corpus
def test_pinned_baseline_resolves_in_the_real_repo(baseline, baseline_ref):
    """The pinned defect state is reachable, and reads route through git."""
    assert baseline.pinned is True
    assert baseline.ref == baseline_ref
    assert baseline.repo_root is not None


@pytest.mark.corpus
def test_pinned_read_matches_an_independent_git_show(baseline, datasheet_dir, baseline_ref):
    """Verify V92Baseline against something other than itself."""
    rel = "QuestData/001348.quest"
    assert baseline.head_exists(rel), f"{rel} missing at {baseline_ref}"

    via_lib = baseline.read(rel)
    via_git = git_show(datasheet_dir, baseline_ref, rel)

    assert via_lib is not None and via_git is not None
    assert via_lib == via_git
    assert via_lib.lstrip().startswith("<?xml"), "BOM must be stripped by the reader"


@pytest.mark.corpus
def test_worktree_baseline_reads_the_overlay(worktree_baseline, baseline):
    """The paired fixture used by fire-then-quiet assertions reads current state."""
    rel = "QuestData/001348.quest"
    from_worktree = worktree_baseline.read(rel)

    assert from_worktree is not None
    assert from_worktree == (baseline.datasheet_dir / rel).read_text(encoding="utf-8-sig")
