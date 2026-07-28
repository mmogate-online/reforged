"""The audit tool's output contracts.

These are the promises every consumer depends on: migrate.py reads the summary
line, the skill reads --list-checks and --json, and the waiver file keys off the
finding key. A check can be rewritten freely; these must not move underneath it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import audit_quest_design as aqd
from audit_quest_design import main
from auditlib import CHECKS, Finding, Scope, Waivers, check


@pytest.fixture
def isolated_registry():
    """Swap the global check registry so a test can register its own."""
    saved = dict(CHECKS)
    CHECKS.clear()
    try:
        yield CHECKS
    finally:
        CHECKS.clear()
        CHECKS.update(saved)


@pytest.fixture
def tiny_datasheet(corpus_dir) -> Path:
    """Enough of a tree that the tool starts: QuestData must exist."""
    return corpus_dir({"QuestData/000001.quest": "<Quest id=\"1\"><Header /></Quest>"})


def run(capsys, *argv) -> tuple[int, str]:
    code = main(list(argv))
    return code, capsys.readouterr().out


# ---------------------------------------------------------------------------
# Finding keys
# ---------------------------------------------------------------------------

def test_key_is_check_subject_detail():
    f = Finding("high", "duplication", "item-17409", "granted twice", detail="1322+1325")

    assert f.key == "duplication:item-17409:1322+1325"


def test_key_omits_an_empty_detail():
    assert Finding("info", "lane", "quest-1305", "x").key == "lane:quest-1305"


def test_key_is_stable_across_evidence_changes():
    """A waiver written today must still match after unrelated content changes.

    Evidence carries the counts and positions; the key must not, or every waiver
    silently lapses the next time a neighbouring quest moves.
    """
    a = Finding("high", "duplication", "item-160", "m", detail="d", evidence={"sources": 2})
    b = Finding("high", "duplication", "item-160", "different message",
                detail="d", evidence={"sources": 9, "quest": 1301})

    assert a.key == b.key


def test_an_unknown_severity_is_rejected():
    with pytest.raises(ValueError):
        Finding("critical", "x", "y", "z")


# ---------------------------------------------------------------------------
# Waivers
# ---------------------------------------------------------------------------

def test_waiver_matches_by_key_and_carries_its_reason(tmp_path: Path):
    path = tmp_path / "w.yaml"
    path.write_text(
        "waivers:\n"
        "  - key: duplication:item-160:1301+buylist\n"
        "    reason: deliberate starter gift, also stocked by the camp merchant\n"
        "    date: 2026-07-20\n",
        encoding="utf-8",
    )

    w = Waivers.load(path)

    assert "duplication:item-160:1301+buylist" in w
    assert "camp merchant" in w.reason("duplication:item-160:1301+buylist")
    assert "duplication:item-160:other" not in w


def test_a_waiver_without_a_reason_does_not_waive(tmp_path: Path):
    """A reasonless waiver is indistinguishable from nobody having looked."""
    path = tmp_path / "w.yaml"
    path.write_text("waivers:\n  - key: lane:quest-1305\n", encoding="utf-8")

    assert "lane:quest-1305" not in Waivers.load(path)


def test_a_missing_waiver_file_is_not_an_error(tmp_path: Path):
    assert Waivers.load(tmp_path / "absent.yaml").entries == {}


def test_the_checked_in_waiver_file_parses():
    from dclib import reforged_dir

    Waivers.load(reforged_dir() / aqd.DEFAULT_WAIVERS)


def test_every_checked_in_waiver_carries_a_reason_and_a_date():
    """The file is the durable record of deliberate design decisions.

    An entry that survives without a reason has already failed at its job, and
    the loader drops it silently, so the finding quietly comes back.
    """
    import yaml
    from dclib import reforged_dir

    raw = yaml.safe_load((reforged_dir() / aqd.DEFAULT_WAIVERS).read_text(encoding="utf-8"))
    entries = raw.get("waivers") or []

    for entry in entries:
        assert entry.get("key"), f"waiver with no key: {entry}"
        assert entry.get("reason"), f"waiver with no reason: {entry['key']}"
        assert entry.get("date"), f"waiver with no date: {entry['key']}"
        assert len(str(entry["reason"]).split()) >= 8, \
            f"waiver reason too thin to be useful in a year: {entry['key']}"


# ---------------------------------------------------------------------------
# Scope model
# ---------------------------------------------------------------------------

def test_subject_scope_filters_by_zone():
    scope = Scope(zones={13, 64}, new_quests=None)

    assert scope.in_subject({"hz": 13})
    assert not scope.in_subject({"hz": 213})


def test_all_zones_admits_everything():
    assert Scope(zones=None, new_quests=None).in_subject({"hz": 999})


def test_findings_scope_marks_only_the_named_quests_new():
    """Without this there is no way to review a change without also
    re-reporting every pre-existing condition in the zone."""
    scope = Scope(zones={13}, new_quests={1323, 1324})

    assert scope.is_new(1323)
    assert not scope.is_new(1305)
    assert not scope.is_new(None)


def test_no_findings_scope_means_everything_is_new():
    assert Scope(zones={13}, new_quests=None).is_new(1305)


# ---------------------------------------------------------------------------
# CLI contracts
# ---------------------------------------------------------------------------

def test_list_checks_is_machine_readable(capsys):
    """The skill defers to this instead of restating the check list."""
    code, out = run(capsys, "--list-checks")
    parsed = json.loads(out)

    from auditlib import REPORTS

    assert code == 0
    assert isinstance(parsed, list)
    assert all({"id", "group", "summary"} <= set(c) for c in parsed)
    assert {c["id"] for c in parsed} == set(CHECKS) | set(REPORTS), \
        "the inventory must cover checks AND report sections"
    assert all(c["summary"].strip() for c in parsed), "every entry needs a summary"


def test_zones_or_all_zones_is_required(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])

    assert exc.value.code == 2


def test_an_unknown_check_is_rejected(tiny_datasheet):
    with pytest.raises(SystemExit) as exc:
        main(["--zones", "13", "--check", "nosuchcheck", "--datasheet", str(tiny_datasheet)])

    assert exc.value.code == 2


def test_exit_is_zero_even_with_high_findings(capsys, isolated_registry, tiny_datasheet):
    """Advisory means advisory. A promotion to blocking is a separate decision."""

    @check("noisy", "test", "always fires")
    def _noisy(corpus, scope):
        return [Finding("high", "noisy", "quest-1", "a real problem")]

    code, out = run(capsys, "--zones", "13", "--datasheet", str(tiny_datasheet))

    assert code == 0
    assert "HIGH" in out


def test_strict_is_reserved_and_does_not_change_the_exit_code(capsys, isolated_registry, tiny_datasheet):
    @check("noisy", "test", "always fires")
    def _noisy(corpus, scope):
        return [Finding("high", "noisy", "quest-1", "a real problem")]

    code, _ = run(capsys, "--zones", "13", "--strict", "--datasheet", str(tiny_datasheet))

    assert code == 0


def test_the_word_pass_never_appears(capsys, isolated_registry, tiny_datasheet):
    """This project runs two exit-0 gates whose readers treat PASS as approval.

    An advisory tool that borrows the word gets read as one of them.
    """

    @check("quiet", "test", "never fires")
    def _quiet(corpus, scope):
        return []

    _, out = run(capsys, "--zones", "13", "--datasheet", str(tiny_datasheet))

    assert "PASS" not in out.upper().replace("ADVISORY", "")
    assert out.strip().endswith("ADVISORY: 0 findings (0 new, 0 waived)")


def test_summary_line_counts_new_and_waived_separately(capsys, isolated_registry, tiny_datasheet, tmp_path):
    @check("dup", "test", "fires twice")
    def _dup(corpus, scope):
        return [
            Finding("high", "dup", "item-1", "m", evidence={"quest": 1323}),
            Finding("high", "dup", "item-2", "m", evidence={"quest": 1305}),
            Finding("info", "dup", "item-3", "m", evidence={"quest": 1323}),
        ]

    waivers = tmp_path / "w.yaml"
    waivers.write_text("waivers:\n  - key: dup:item-3\n    reason: deliberate\n", encoding="utf-8")

    _, out = run(capsys, "--zones", "13", "--quests", "1323",
                 "--waivers", str(waivers), "--datasheet", str(tiny_datasheet))

    assert out.strip().endswith("ADVISORY: 3 findings (1 new, 1 waived)")
    assert "NEW item-1" in out
    assert "WAIVED item-3" in out


def test_json_shape_is_stable_and_deterministic(capsys, isolated_registry, tiny_datasheet):
    @check("dup", "test", "fires")
    def _dup(corpus, scope):
        return [Finding("medium", "dup", "item-1", "m", detail="d", evidence={"quest": 1323, "n": 2})]

    _, first = run(capsys, "--zones", "13", "--json", "--datasheet", str(tiny_datasheet))
    _, second = run(capsys, "--zones", "13", "--json", "--datasheet", str(tiny_datasheet))

    assert first == second, "identical input must produce byte-identical output"
    payload = json.loads(first.rsplit("ADVISORY", 1)[0])
    row = payload["findings"][0]
    assert set(row) == {"severity", "check", "subject", "key", "new", "waived", "message", "evidence"}
    assert row["key"] == "dup:item-1:d"
    assert row["evidence"] == {"quest": 1323, "n": 2}
    assert payload["summary"] == {"total": 1, "new": 1, "waived": 0}


def test_findings_sort_by_severity_then_identity(capsys, isolated_registry, tiny_datasheet):
    @check("z", "test", "fires")
    def _z(corpus, scope):
        return [
            Finding("info", "z", "c", "m"),
            Finding("high", "z", "b", "m"),
            Finding("medium", "z", "a", "m"),
        ]

    _, out = run(capsys, "--zones", "13", "--datasheet", str(tiny_datasheet))
    severities = [line.split()[0] for line in out.splitlines() if not line.startswith("ADVISORY")]

    assert severities == ["HIGH", "MEDIUM", "INFO"]


def test_registering_a_duplicate_check_id_is_rejected(isolated_registry):
    @check("only", "test", "x")
    def _a(corpus, scope):
        return []

    with pytest.raises(ValueError):
        @check("only", "test", "x")
        def _b(corpus, scope):
            return []


def test_a_malformed_datasheet_path_reports_instead_of_crashing(capsys, tmp_path):
    code, out = run(capsys, "--zones", "13", "--datasheet", str(tmp_path / "nope"))

    assert code == 2
    assert "QuestData not found" in out
