"""Quest design review: deterministic checks over rewards, graph and tuning.

Born from the 2026-07-27 Island of Dawn trimming and redistribution wave (patch
002, specs 27 to 33), which surfaced a class of defect no existing gate catches:
quests that are individually valid but wrong as a system.

  Quests 1304 and 1323 granted the identical 12-row class weapon bag at the
  identical 800 exp and 80 gold. Authentic v31 data, so no source diff could
  ever have found it. Brawler and Ninja received the same level-2 weapon from
  all three weapon quests in the zone and never a mid-tier upgrade, because two
  reward generators each carried a private per-class weapon pool that skipped
  levels 3 to 6. No gear set below level 7 was completable: 6 of 9 level-4
  pieces and all 3 level-3 body pieces were granted by no quest anywhere in the
  corpus. Quest 1348 required 8 items from 10 credit mobs. Quests 1326 and 1330
  gated on 진행퀘스트 = 1305,1 while granting two pieces of a four-piece set, so
  finishing 1305 first stranded the set permanently.

Every one of those is individually valid and collectively wrong, and every one
is computable. This tool computes them.

ADVISORY BY DESIGN. It always exits 0 and never prints the word PASS. A clean
run is not approval; it means the deterministic checks found nothing, which is a
much smaller claim. Findings are promoted to blocking only after more regions
prove them out.

Three scopes, never conflated:

  subject   --zones, required. Which quests findings are REPORTED about.
  evidence  always corpus-wide. Set completeness must see every granting quest
            in the game, references must see inbound edges from anywhere. A
            zone-scoped evidence read calls every set that continues into the
            next region "partially granted" and cannot prove a trim orphans
            nothing.
  findings  --quests or --since, optional. Which findings count as NEW. Without
            it there is no way to review a change without also re-reporting
            every pre-existing condition in the zone.

Usage:
  python reforged/tools/dc-restore/audit_quest_design.py --zones 13,64,213
  python reforged/tools/dc-restore/audit_quest_design.py --zones 13 --quests 1323,1324
  python reforged/tools/dc-restore/audit_quest_design.py --zones 13 --since HEAD
  python reforged/tools/dc-restore/audit_quest_design.py --all-zones --check duplication
  python reforged/tools/dc-restore/audit_quest_design.py --zones 13 --report
  python reforged/tools/dc-restore/audit_quest_design.py --list-checks
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from auditlib import (  # noqa: F401  (re-exported for consumers and tests)
    CHECKS,
    DEFAULT_WAIVERS,
    REPORTS,
    SEVERITIES,
    CheckSpec,
    Corpus,
    Finding,
    Scope,
    Waivers,
    check,
    item_label,
    report,
)
from dclib import V92Baseline, load_references, reforged_dir

# Importing a check module is what registers its checks. Every group lives in
# its own file so adding one never edits a file another change is already in.
import audit_checks_duplication  # noqa: F401,E402
import audit_checks_gear  # noqa: F401,E402
import audit_checks_graph  # noqa: F401,E402
import audit_checks_tuning  # noqa: F401,E402
import audit_reports  # noqa: F401,E402


def quests_changed_since(baseline: V92Baseline, ref: str, datasheet: Path) -> set[int]:
    """Quest ids whose files differ between a git ref and the working tree."""
    probe = V92Baseline(datasheet, ref=ref)
    out: set[int] = set()
    for rel in probe.dirty_files():
        name = rel.rsplit("/", 1)[-1]
        if not name.endswith(".quest"):
            continue
        stem = name[: -len(".quest")]
        if stem.isdigit():
            out.add(int(stem))
    return out


def run_checks(corpus: Corpus, scope: Scope, selected: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for check_id in selected:
        findings.extend(CHECKS[check_id].fn(corpus, scope) or [])
    order = {s: i for i, s in enumerate(SEVERITIES)}
    findings.sort(key=lambda f: (order[f.severity], f.check, f.subject, f.detail))
    return findings


def render_text(findings: list[Finding], waivers: Waivers, scope: Scope) -> list[str]:
    lines: list[str] = []
    for f in findings:
        waived = f.key in waivers
        gid = f.evidence.get("quest")
        flag = "NEW " if (scope.is_new(gid) and not waived) else ""
        if waived:
            flag = "WAIVED "
        lines.append(f"{f.severity.upper():<7} {f.check:<22} {flag}{f.subject} | {f.message}")
    return lines


def summarize(findings: list[Finding], waivers: Waivers, scope: Scope) -> tuple[int, int, int]:
    waived = sum(1 for f in findings if f.key in waivers)
    new = sum(1 for f in findings
              if f.key not in waivers and scope.is_new(f.evidence.get("quest")))
    return len(findings), new, waived


def run_reports(corpus: Corpus, scope: Scope) -> list[str]:
    lines: list[str] = []
    for spec in REPORTS.values():
        rows = spec.fn(corpus, scope) or []
        if not rows:
            continue
        lines.append("")
        lines.append(f"== {spec.id}: {spec.summary}")
        lines.extend(rows)
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    scope_group = ap.add_mutually_exclusive_group()
    scope_group.add_argument("--zones", help="Subject scope: comma-separated zone ids from Quest번호")
    scope_group.add_argument("--all-zones", action="store_true", help="Subject scope: every zone")
    ap.add_argument("--quests", help="Findings scope: comma-separated quest ids to mark NEW")
    ap.add_argument("--since", help="Findings scope: derive --quests from the datasheet diff against a git ref")
    ap.add_argument("--check", help="Comma-separated check ids (default: all)")
    ap.add_argument("--report", action="store_true", help="Include descriptive report sections")
    ap.add_argument("--json", action="store_true", help="Emit findings as JSON")
    ap.add_argument("--waivers", default=None, help=f"Waiver file (default: reforged/{DEFAULT_WAIVERS})")
    ap.add_argument("--list-checks", action="store_true", help="Print the check inventory and exit")
    ap.add_argument("--datasheet", help="Server datasheet path (default: server_datasheet from .references)")
    ap.add_argument("--baseline-ref", default="HEAD",
                    help="Read the datasheet at this git ref instead of the working tree")
    ap.add_argument("--strict", action="store_true",
                    help="Reserved. Findings are advisory; this flag does not yet change the exit code")
    args = ap.parse_args(argv)

    if args.list_checks:
        print(json.dumps(
            [c.as_dict() for c in CHECKS.values()] + [r.as_dict() for r in REPORTS.values()],
            indent=2))
        return 0

    if not args.zones and not args.all_zones:
        ap.error("one of --zones or --all-zones is required")

    datasheet = Path(args.datasheet) if args.datasheet else Path(load_references()["server_datasheet"])
    if not (datasheet / "QuestData").is_dir():
        print(f"Error: QuestData not found under {datasheet}")
        return 2

    selected = [c.strip() for c in args.check.split(",")] if args.check else list(CHECKS)
    unknown = [c for c in selected if c not in CHECKS]
    if unknown:
        ap.error(f"unknown check(s): {', '.join(unknown)}")

    baseline = V92Baseline(datasheet, ref=args.baseline_ref)
    corpus = Corpus(datasheet, baseline, use_baseline=args.baseline_ref != "HEAD")

    zones = None if args.all_zones else {
        int(z.strip()) for z in args.zones.split(",") if z.strip().isdigit()
    }
    new_quests: set[int] | None = None
    if args.quests:
        new_quests = {int(q.strip()) for q in args.quests.split(",") if q.strip().isdigit()}
    elif args.since:
        new_quests = quests_changed_since(baseline, args.since, datasheet)
    scope = Scope(zones=zones, new_quests=new_quests)

    waiver_path = Path(args.waivers) if args.waivers else reforged_dir() / DEFAULT_WAIVERS
    waivers = Waivers.load(waiver_path)

    findings = run_checks(corpus, scope, selected)
    total, new, waived = summarize(findings, waivers, scope)

    if args.json:
        payload = {
            "findings": [
                {
                    "severity": f.severity, "check": f.check, "subject": f.subject,
                    "key": f.key, "new": scope.is_new(f.evidence.get("quest")) and f.key not in waivers,
                    "waived": f.key in waivers, "message": f.message, "evidence": f.evidence,
                }
                for f in findings
            ],
            "summary": {"total": total, "new": new, "waived": waived},
        }
        if args.report:
            payload["reports"] = run_reports(corpus, scope)
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        for line in render_text(findings, waivers, scope):
            print(line)
        if args.report:
            for line in run_reports(corpus, scope):
                print(line)

    # Always this line, always exit 0. The word PASS never appears: this project
    # runs two exit-0 gates whose agents are trained to read PASS as approval,
    # and an advisory tool that borrows that word will be read as one.
    print(f"ADVISORY: {total} findings ({new} new, {waived} waived)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
