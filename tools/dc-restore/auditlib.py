"""Shared model for audit_quest_design.py: findings, scopes, waivers, corpus.

Split from the CLI so each check group can live in its own module and register
itself, rather than one file growing a section per check.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from dclib import (
    V92Baseline,
    index_comp_file,
    load_item_model,
    parse_quest,
    scan_item_sources,
)

DEFAULT_WAIVERS = "config/quest-design-waivers.yaml"

# Severity is CONFIDENCE that the finding is a defect, not importance. A high
# finding is one whose signature marked a real defect every time it fired; an
# info finding is a fact worth seeing that is legitimate about as often as not.
SEVERITIES = ("high", "medium", "info")


@dataclass(frozen=True)
class Finding:
    """One deterministic observation about one subject."""

    severity: str
    check: str
    subject: str
    message: str
    detail: str = ""
    evidence: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.severity not in SEVERITIES:
            raise ValueError(f"unknown severity {self.severity!r}")

    @property
    def key(self) -> str:
        """Stable waiver key: check:subject[:detail].

        Stability is the whole contract. A waiver written today must still match
        the same finding after unrelated content changes, so the key never
        contains counts, positions, or anything derived from other quests.
        """
        return f"{self.check}:{self.subject}" + (f":{self.detail}" if self.detail else "")


@dataclass(frozen=True)
class CheckSpec:
    """Registration record for one check."""

    id: str
    group: str
    summary: str
    fn: object

    def as_dict(self) -> dict:
        return {"id": self.id, "group": self.group, "summary": self.summary}


CHECKS: dict[str, CheckSpec] = {}
REPORTS: dict[str, CheckSpec] = {}


def check(check_id: str, group: str, summary: str):
    """Register a check. The registry IS the inventory --list-checks prints.

    The skill defers to that output rather than restating the list, so adding a
    check here is the only edit needed to make it visible to every consumer.
    """

    def wrap(fn):
        if check_id in CHECKS:
            raise ValueError(f"duplicate check id {check_id!r}")
        CHECKS[check_id] = CheckSpec(check_id, group, summary, fn)
        return fn

    return wrap


def report(report_id: str, summary: str):
    """Register a report section.

    Reports carry NO severities. They are descriptive tables offered as input to
    a judgment call, and labelling a judgment call with a severity is how a tool
    starts being argued with instead of read.
    """

    def wrap(fn):
        if report_id in REPORTS:
            raise ValueError(f"duplicate report id {report_id!r}")
        REPORTS[report_id] = CheckSpec(report_id, "report", summary, fn)
        return fn

    return wrap


class Waivers:
    """Accepted findings, keyed by the stable finding key.

    The file doubles as the durable record of deliberate design decisions. A
    finding that is waived without a reason is indistinguishable from a finding
    nobody looked at, so a reason is required.
    """

    def __init__(self, entries: dict[str, dict]):
        self.entries = entries

    @classmethod
    def load(cls, path: Path) -> "Waivers":
        if not path.exists():
            return cls({})
        import yaml

        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        items = raw.get("waivers") or []
        entries: dict[str, dict] = {}
        for item in items:
            if not isinstance(item, dict) or not item.get("key"):
                continue
            if not item.get("reason"):
                continue  # a waiver without a reason records nothing
            entries[str(item["key"])] = item
        return cls(entries)

    def __contains__(self, key: str) -> bool:
        return key in self.entries

    def reason(self, key: str) -> str:
        return str(self.entries.get(key, {}).get("reason", ""))


class Corpus:
    """Corpus-wide evidence, loaded once and lazily.

    Evidence is never scoped to the subject zones. Reading only the audited
    zones makes set completeness, references and duplication silently wrong, in
    the direction of reporting problems that do not exist and missing the ones
    that do.
    """

    def __init__(self, datasheet: Path, baseline: V92Baseline, use_baseline: bool = False):
        self.datasheet = Path(datasheet)
        self.baseline = baseline
        # The subject of a design review is the content you just changed, so the
        # default read is the WORKING TREE. V92Baseline serves HEAD for dirty
        # files, which is the right default for a restoration diff and exactly
        # the wrong one here: it would review the state before your edit and
        # report a clean run for a defect you just introduced. Historical runs
        # (the regression fixtures) opt in with --baseline-ref.
        self.use_baseline = use_baseline
        self._quests: dict[int, dict] | None = None
        self._items = None
        self._rewards: dict[int, dict] | None = None
        self._item_sources: dict[int, set[str]] | None = None
        self._text_cache: dict[str, str | None] = {}

    def read(self, relpath: str) -> str | None:
        if relpath not in self._text_cache:
            self._text_cache[relpath] = self.baseline.read(relpath, baseline=self.use_baseline)
        return self._text_cache[relpath]

    def glob(self, pattern: str) -> list[str]:
        """Datasheet-relative paths matching a glob, in sorted order."""
        return sorted(
            p.relative_to(self.datasheet).as_posix()
            for p in self.datasheet.glob(pattern)
        )

    @property
    def quests(self) -> dict[int, dict]:
        """{global id: parsed quest} for every quest in the corpus."""
        if self._quests is None:
            out: dict[int, dict] = {}
            for relpath in self.glob("QuestData/*.quest"):
                text = self.read(relpath)
                if text is None:
                    continue
                try:
                    model = parse_quest(text)
                except Exception:
                    continue  # malformed source is a data finding, never a crash
                if model is not None and model["gid"] is not None:
                    out[model["gid"]] = model
            self._quests = out
        return self._quests

    @property
    def items(self):
        if self._items is None:
            self._items = load_item_model(self.datasheet, read=self.read)
        return self._items

    @property
    def rewards(self) -> dict[int, dict]:
        """{quest id: reward payload} across every server compensation shard."""
        if self._rewards is None:
            out: dict[int, dict] = {}
            for relpath in self.glob("CompensationData/QuestCompensationData_*.xml"):
                text = self.read(relpath)
                if text is None:
                    continue
                try:
                    shard = index_comp_file(text)
                except Exception:
                    continue
                for qid, payload in shard.items():
                    if payload is not None:
                        out[qid] = payload
            self._rewards = out
        return self._rewards

    @property
    def item_sources(self) -> dict[int, set[str]]:
        """{item id: families that can grant it} across the source universe."""
        if self._item_sources is None:
            self._item_sources = scan_item_sources(self.datasheet, read=self.read)
        return self._item_sources


@dataclass
class Scope:
    """The three scopes, resolved."""

    zones: set[int] | None          # None means every zone
    new_quests: set[int] | None     # None means every finding counts as new

    def in_subject(self, quest: dict) -> bool:
        return self.zones is None or quest.get("hz") in self.zones

    def is_new(self, gid: int | None) -> bool:
        return self.new_quests is None or (gid is not None and gid in self.new_quests)

    def subject_quests(self, corpus: Corpus) -> dict[int, dict]:
        """The quests findings are reported about. Evidence stays corpus-wide."""
        return {gid: q for gid, q in corpus.quests.items() if self.in_subject(q)}


def item_label(corpus: Corpus, item_id: int) -> str:
    info = corpus.items.get(item_id)
    return f"item-{item_id}" + (f" ({info.name})" if info and info.name else "")
