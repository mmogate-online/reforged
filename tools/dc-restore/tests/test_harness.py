"""Self-tests for the test harness itself.

A suite that cannot fail is not a suite. These tests prove the machinery every
later phase leans on: fixture loading, the synthetic corpus factory, the byte
shape parsers actually meet on disk, and that a false assertion is reported as a
failure rather than swallowed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dclib import parse_quest, read_text


def test_committed_fixture_loads_and_parses(fixtures_dir: Path):
    """The hermetic tier can read a committed fixture and hand it to dclib."""
    path = fixtures_dir / "harness" / "minimal.quest"
    quest = parse_quest(read_text(path))

    assert quest is not None
    assert quest["gid"] == 1348
    assert (quest["hz"], quest["local"]) == (13, 48)
    assert quest["giver"] == "213,1147"
    assert quest["tasks"][1]["type"] == "사냥전달Task"
    # Grant rates ride on the monster entries, the delivered count on the bag.
    assert quest["tasks"][1]["monsters"] == [("13,302", "", "90"), ("13,303", "", "17")]


def test_hunt_deliver_bag_count_is_extracted(fixtures_dir: Path):
    """The delivered count of a 사냥전달Task lives at 아이템작성/아이템작성/전달수량.

    Before P1, _extract_task read only a 전달수량 that was a DIRECT Body child,
    which is the 찔러준아이템전달Task shape (204 tasks). The nested shape covers
    582 hunt-deliver, 317 repeat and 196 collect tasks, and the count was
    dropped for all of them, leaving the required side of the feasibility ratio
    unavailable. Kept here as the regression guard for that gap.
    """
    quest = parse_quest(read_text(fixtures_dir / "harness" / "minimal.quest"))

    assert [b["qty"] for b in quest["tasks"][1]["bags"]] == ["8"]


def test_corpus_factory_writes_the_real_byte_shape(corpus_dir):
    """Synthetic corpora carry a BOM and CRLF, like the server writes them."""
    root = corpus_dir({"QuestData/000001.quest": "<Quest id=\"1\">\n  <Header />\n</Quest>\n"})
    raw = (root / "QuestData" / "000001.quest").read_bytes()

    assert raw.startswith(b"\xef\xbb\xbf"), "fixture must reproduce the UTF-8 BOM"
    assert b"\r\n" in raw, "fixture must reproduce CRLF newlines"
    assert read_text(root / "QuestData" / "000001.quest").startswith("<Quest")


def test_corpus_factory_can_opt_out_of_bom_and_crlf(corpus_dir):
    """Some families ship LF and no BOM; the factory must be able to say so."""
    root = corpus_dir({"CompensationData/x.xml": "<a />\n"}, bom=False, crlf=False)
    raw = (root / "CompensationData" / "x.xml").read_bytes()

    assert raw == b"<a />\n"


@pytest.mark.xfail(strict=True, reason="harness self-test: a false assertion must FAIL")
def test_a_false_assertion_really_fails():
    """Strict xfail: if this ever passes, assertions are not being evaluated.

    `strict=True` turns an unexpected pass into a suite failure, so this guards
    against the whole tier degrading into vacuous green.
    """
    assert 1 == 2


def test_skip_reason_is_stated_not_silent(pytestconfig):
    """Corpus-tier skips must name the missing precondition.

    Enforced by construction in conftest._skip; asserted here so a future edit
    that drops the reason string is caught.
    """
    from conftest import _skip

    # pytest.skip raises Skipped, which derives from BaseException, not Exception.
    with pytest.raises(BaseException) as excinfo:
        _skip("server_datasheet path does not exist")

    assert "corpus tier unavailable" in str(excinfo.value)
    assert "server_datasheet" in str(excinfo.value)
