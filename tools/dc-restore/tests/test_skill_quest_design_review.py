"""The quest-design-review skill stays in sync with the tool.

A skill that restates the check list drifts from the tool the first time a check
is added, and nothing about the drift is visible: the skill still reads
plausibly. So the skill defers to --list-checks, and these tests hold that line.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from auditlib import CHECKS, REPORTS
from dclib import reforged_dir

SKILL_DIR = reforged_dir() / ".claude" / "skills" / "quest-design-review"
SKILL = SKILL_DIR / "SKILL.md"
CASE_STUDIES = SKILL_DIR / "reference" / "case-studies.md"

# Em dash, en dash, figure dash, horizontal bar. A PreToolUse hook blocks these
# on write; this catches anything that arrived another way.
DASHES = ("\u2014", "\u2013", "\u2012", "\u2015")


@pytest.fixture(scope="module")
def skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def case_text() -> str:
    return CASE_STUDIES.read_text(encoding="utf-8")


def test_the_skill_and_its_reference_exist():
    assert SKILL.is_file()
    assert CASE_STUDIES.is_file()


def test_frontmatter_matches_the_project_contract(skill_text: str):
    head = skill_text.split("---")[1]

    assert "name: quest-design-review" in head
    assert "disable-model-invocation: false" in head
    assert "user-invocable: true" in head
    assert "context: fork" not in skill_text, "project convention: skills are reference, not orchestration"


def test_the_description_names_situations_not_just_the_concept(skill_text: str):
    """Auto-invocation depends entirely on matching how real work is phrased."""
    # A folded YAML block wraps mid-phrase, so match against collapsed whitespace.
    head = " ".join(skill_text.split("---")[1].lower().split())

    assert "use when" in head
    for trigger in ("reward", "prerequisite", "level gate", "trimming or disabling",
                    "spawn density", "quest spec",
                    # Restoration vocabulary: a restore session says "restore" and
                    # "re-enable", never "authoring a quest", and without these it
                    # reaches the review only via the content-restoration skill.
                    "restoring classic quests", "re-enabling", "empty quest rewards"):
        assert trigger in head, f"missing trigger phrasing: {trigger}"
    description = head.split("description:", 1)[1].split("disable-model-invocation")[0]
    assert len(description) < 1024


def test_the_skill_does_not_restate_the_check_list(skill_text: str):
    """The drift guard.

    The tool's registry is the inventory. A prose copy is wrong the first time a
    check is added, and it fails silently because the stale list still reads fine.
    """
    # Match the CODE form, not the bare word: "duplication" and "references"
    # are ordinary English and appear in the prose about what the tool cannot
    # decide. An enumeration would write them as identifiers.
    named = [cid for cid in CHECKS if f"`{cid}`" in skill_text]

    assert named == [], f"the skill enumerates checks instead of deferring: {named}"
    assert "--list-checks" in skill_text, "it must point at the generated inventory instead"
    assert "Do not restate the check list" in skill_text, "and say why, for the next editor"


def test_every_check_and_report_has_a_case_study(case_text: str):
    """A check with no worked example is a rule nobody will believe."""
    missing = [cid for cid in list(CHECKS) + list(REPORTS) if f"`{cid}`" not in case_text]

    assert missing == [], f"no case study for: {missing}"


def test_the_skill_states_the_advisory_contract(skill_text: str):
    assert "exits 0" in skill_text
    assert "not approval" in skill_text
    assert "waiver" in skill_text.lower()


def test_the_skill_says_what_the_tool_cannot_decide(skill_text: str):
    """Without this the tool gets treated as the whole review."""
    assert "cannot decide" in skill_text.lower()


def test_paths_use_forward_slashes_and_no_machine_paths(skill_text: str, case_text: str):
    for text in (skill_text, case_text):
        assert "D:\\" not in text and "C:\\" not in text, "resolve paths via .references"


@pytest.mark.parametrize("path", [SKILL, CASE_STUDIES])
def test_no_em_dash_family_characters(path: Path):
    text = path.read_text(encoding="utf-8")
    found = [d for d in DASHES if d in text]

    assert found == [], f"{path.name} carries banned dash characters: {found}"


def test_the_skill_body_is_short(skill_text: str):
    assert len(skill_text.splitlines()) < 500
