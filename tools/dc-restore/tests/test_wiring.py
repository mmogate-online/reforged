"""The wiring that keeps the review from depending on anyone remembering it.

A tool nobody runs is a tool that does not exist. These tests hold the hooks:
migrate prints an advisory after a patch touches quests, the two skills point at
it, the playbook names it, and the README registers it everywhere it registers a
tool.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from dclib import reforged_dir

ROOT = reforged_dir()
MIGRATE = ROOT / "tools" / "migrate" / "migrate.py"
README = ROOT / "tools" / "dc-restore" / "README.md"
PLAYBOOK = ROOT / "docs" / "plans" / "classic-restoration" / "ZONE-PORT-PLAYBOOK.md"
NEW_SPEC = ROOT / ".claude" / "skills" / "new-spec" / "SKILL.md"
RESTORATION = ROOT / ".claude" / "skills" / "content-restoration" / "SKILL.md"

TOOL = "audit_quest_design.py"


@pytest.fixture(scope="module")
def migrate():
    spec = importlib.util.spec_from_file_location("migrate_under_test", MIGRATE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["migrate_under_test"] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# migrate.py
# ---------------------------------------------------------------------------

def test_the_advisory_is_skipped_when_a_patch_touches_no_quests(migrate, capsys):
    """An item-only patch has nothing to review, and a section printed for every
    patch is a section people learn to scroll past."""
    migrate.quest_design_advisory(ROOT.parent, "ignored", "HEAD", {"items", "enchants"})

    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("key", ["quests", "questCompensations", "questDialogs"])
def test_quest_entity_keys_trigger_the_advisory(migrate, key):
    assert key in migrate.QUEST_DESIGN_KEYS


def test_the_advisory_prints_one_line_and_no_report_body(migrate, capsys, monkeypatch):
    """D4: never the full report inline.

    A patch apply is not the place to read 60 findings, and a wall of
    pre-existing conditions trains people to scroll past the one that matters.
    """
    class FakeProc:
        stdout = ('{"findings": [{"severity": "high", "check": "duplication", '
                  '"subject": "item-1", "key": "k", "new": true, "waived": false, '
                  '"message": "m", "evidence": {}}], '
                  '"summary": {"total": 47, "new": 2, "waived": 1}}\n'
                  "ADVISORY: 47 findings (2 new, 1 waived)\n")

    monkeypatch.setattr(migrate.subprocess, "run", lambda *a, **k: FakeProc())

    migrate.quest_design_advisory(ROOT.parent, "ignored", "abc123", {"quests"})
    out = capsys.readouterr().out

    assert "ADVISORY: 2 new findings (47 total, 1 waived)" in out
    assert "item-1" not in out, "the finding body must not be printed inline"
    assert "duplication" not in out
    body = [ln for ln in out.splitlines() if ln.strip()]
    assert len(body) == 3, f"header, advisory, pointer only; got {body}"
    assert "Full report:" in out


def test_a_clean_advisory_prints_no_pointer(migrate, capsys, monkeypatch):
    class FakeProc:
        stdout = '{"findings": [], "summary": {"total": 0, "new": 0, "waived": 0}}\nADVISORY: 0 findings\n'

    monkeypatch.setattr(migrate.subprocess, "run", lambda *a, **k: FakeProc())

    migrate.quest_design_advisory(ROOT.parent, "ignored", "abc123", {"quests"})
    out = capsys.readouterr().out

    assert "ADVISORY: 0 new findings" in out
    assert "Full report:" not in out


def test_an_advisory_failure_never_fails_the_patch(migrate, capsys, monkeypatch):
    """Advisory means advisory. A patch that applied correctly must not be
    reported as broken because a read-only reviewer fell over."""
    def boom(*a, **k):
        raise OSError("no python here")

    monkeypatch.setattr(migrate.subprocess, "run", boom)

    result = migrate.quest_design_advisory(ROOT.parent, "ignored", "abc", {"quests"})
    out = capsys.readouterr().out

    assert result is None
    assert "advisory unavailable" in out


def test_the_advisory_runs_after_the_apply(migrate):
    """It reviews applied state, so it cannot run before the apply."""
    source = MIGRATE.read_text(encoding="utf-8")
    apply_at = source.index("run_ok = apply_specs_batch")
    # The CALL, not the def: both start with the same name, and the def sits
    # above the apply, so a loose match asserts the opposite of the intent.
    call_at = source.index("quest_design_advisory(project_root, server_datasheet")

    assert apply_at < call_at


# ---------------------------------------------------------------------------
# Docs and skills
# ---------------------------------------------------------------------------

def test_the_readme_registers_the_tool_in_all_four_places():
    """The README registers a tool four times, and three out of four is how a
    tool becomes undiscoverable."""
    text = README.read_text(encoding="utf-8")

    overview = text.split("### Read-only vs restore modules")[0]
    assert TOOL in overview, "missing from the prose overview"
    assert f"## {TOOL}" in text, "missing its own section"
    assert f"| `{TOOL}` |" in text, "missing from the Files table"
    assert f"- **{TOOL}**" in text, "missing from the Shipped list"


def test_the_readme_documents_the_advisory_contract():
    text = README.read_text(encoding="utf-8")

    assert "always exits 0" in text.lower()
    assert "waiver" in text.lower()


def test_the_playbook_names_the_review_in_the_authoring_rules():
    text = PLAYBOOK.read_text(encoding="utf-8")
    phase4 = text.split("## Phase 4: authoring rules")[1].split("## Phase 5")[0]

    assert TOOL in phase4


def test_the_playbook_no_longer_claims_the_reward_flag_is_an_invariant():
    """Measured at 789fec28 over 2,707 quests: 1,969 carry the flag on exactly
    the last task, 729 on several, and 9 on one that is not the last."""
    text = PLAYBOOK.read_text(encoding="utf-8")

    assert "reward flag on final task" not in text
    assert "NOT an invariant" in text


def test_new_spec_routes_quest_specs_through_the_review():
    text = NEW_SPEC.read_text(encoding="utf-8")

    assert "quest-design-review" in text
    assert "questCompensations" in text


def test_content_restoration_lists_the_review_as_an_advisory_step():
    text = RESTORATION.read_text(encoding="utf-8")

    assert TOOL in text
    assert "ADVISORY" in text.upper()
