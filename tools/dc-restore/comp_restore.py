"""dc-restore comp_restore: restore quest compensation blocks from v31.

The v92 QuestCompensationData_<zone>.xml files carry empty self-closing quest
stubs (`<Quest questId="1334"/>`) where the reward payload was stripped. The v31
server datasheet still holds the original filled blocks (exp/gold, and for some
quests an itemBag with per-class <Item> children). This module splices each v31
block into the v92 file in place of its stub, re-indented to the v92 file's
indentation, with format-preserving text surgery: every other byte of the v92
file (including its LF newlines and BOM) is left untouched.

Rules:
  - Only an EMPTY v92 stub (self-closing or childless) is ever replaced.
  - A non-empty v92 entry is never overwritten (skipped with a warning).
  - A quest whose v31 entry is missing or itself empty has no source and is
    left as a stub (listed as no-v31-source).

Restored files are the canonical content baseline, committed on the baseline
lane separately from DSL patch overlays. Dry-run (unified diff) is the default;
--apply writes after validating that the edited file still parses.
"""

import argparse
import difflib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from dclib import (
    Sources,
    TextFile,
    find_file_ci,
    load_references,
    validate_xml,
)


def stub_ids_and_status(text: str) -> dict[int, bool]:
    """Map questId -> filled(True)/empty(False) for a QuestCompensationData file."""
    root = ET.fromstring(text.encode("utf-8"))
    out: dict[int, bool] = {}
    for q in root:
        if q.tag != "Quest":
            continue
        qid = q.get("questId")
        if qid and qid.isdigit():
            out[int(qid)] = len(list(q)) > 0
    return out


def find_v31_block(v31_text: str, qid: int) -> str | None:
    """The raw filled <Quest questId=qid>..</Quest> block from v31, or None."""
    m = re.search(r'([ \t]*)<Quest questId="' + str(qid) + r'"\s*>.*?</Quest>',
                  v31_text, re.S)
    if not m:
        return None
    block = m.group(0)
    if "<Compensation" not in block:
        return None  # present but empty; no reward payload to restore
    return block


def find_v92_stub(v92_text: str, qid: int):
    """Match an empty v92 stub for qid; return (match, indent) or (None, None)."""
    m = re.search(
        r'(?m)^([ \t]*)<Quest questId="' + str(qid) + r'"\s*(?:/>|>\s*</Quest>)[ \t]*$',
        v92_text)
    if not m:
        return None, None
    return m, m.group(1)


def reindent(block: str, from_base: int, to_base: int) -> str:
    """Shift every line of block by (to_base - from_base) leading spaces."""
    delta = to_base - from_base
    if delta == 0:
        return block
    out = []
    for line in block.split("\n"):
        if not line.strip():
            out.append(line)
            continue
        if delta > 0:
            out.append(" " * delta + line)
        else:
            drop = 0
            while drop < -delta and drop < len(line) and line[drop] == " ":
                drop += 1
            out.append(line[drop:])
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore quest compensation blocks from v31.")
    parser.add_argument("--zone", type=int, required=True, help="Hunting zone id, e.g. 13")
    parser.add_argument("--quests", default="", help="Comma-separated questIds to restore")
    parser.add_argument("--all-empty", action="store_true",
                        help="Restore every empty v92 stub that has a filled v31 source")
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run diff)")
    args = parser.parse_args()

    if not args.quests and not args.all_empty:
        print("Nothing requested: pass --quests and/or --all-empty.")
        return 2

    refs = load_references()
    sources = Sources(refs)
    problems = sources.validate()
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        return 1

    zone = args.zone
    fname = f"QuestCompensationData_{zone}.xml"
    v92_path = sources.v92 / "CompensationData" / fname
    v31_path = find_file_ci(sources.v31 / "CompensationData", fname)
    if not v92_path.exists():
        print(f"ERROR: v92 file not found: {v92_path}")
        return 1
    if v31_path is None:
        print(f"ERROR: v31 file not found: {sources.v31 / 'CompensationData' / fname}")
        return 1

    v92_tf = TextFile(v92_path)
    v92_before = v92_tf.text
    v31_text = TextFile(v31_path).text

    v92_status = stub_ids_and_status(v92_before)
    v31_status = stub_ids_and_status(v31_text)

    if args.all_empty:
        targets = sorted(q for q, filled in v92_status.items() if not filled)
    else:
        targets = [int(q) for q in args.quests.split(",") if q.strip()]

    restored: list[int] = []
    skipped_nonempty: list[int] = []
    no_source: list[int] = []
    not_in_v92: list[int] = []

    text = v92_before
    for qid in targets:
        if qid not in v92_status:
            not_in_v92.append(qid)
            continue
        if v92_status[qid]:
            skipped_nonempty.append(qid)
            continue
        v31_block = find_v31_block(v31_text, qid)
        if v31_block is None:
            no_source.append(qid)
            continue
        stub, indent = find_v92_stub(text, qid)
        if stub is None:
            # Should not happen for an empty stub; guard anyway.
            no_source.append(qid)
            continue
        from_base = len(v31_block) - len(v31_block.lstrip(" "))
        to_base = len(indent)
        new_block = reindent(v31_block, from_base, to_base)
        text = text[:stub.start()] + new_block + text[stub.end():]
        restored.append(qid)

    print("=" * 78)
    print(f"comp_restore zone {zone} " + ("(APPLY)" if args.apply else "(dry-run)"))
    print("=" * 78)
    print(f"  v92: {len(v92_status)} quests, {sum(v92_status.values())} filled, "
          f"{sum(1 for f in v92_status.values() if not f)} empty stubs")
    print(f"  v31: {len(v31_status)} quests, {sum(v31_status.values())} filled")
    print(f"  restored ({len(restored)}): {restored if len(restored) <= 30 else restored[:30] + ['...']}")
    print(f"  skipped non-empty ({len(skipped_nonempty)}): {skipped_nonempty}")
    print(f"  no v31 source ({len(no_source)}): {no_source}")
    if not_in_v92:
        print(f"  requested but absent in v92 ({len(not_in_v92)}): {not_in_v92}")
    print()

    if text == v92_before:
        print("No file changes produced.")
        return 0

    if len(restored) <= 6:
        diff = difflib.unified_diff(
            v92_before.splitlines(keepends=True),
            text.splitlines(keepends=True),
            fromfile=f"a/{fname}", tofile=f"b/{fname}",
        )
        print("".join(diff))
    else:
        print(f"[diff suppressed: {len(restored)} blocks restored; re-run with a "
              f"--quests subset to inspect specific diffs]")
        print()

    try:
        validate_xml(text)
    except Exception as exc:
        print(f"ERROR: edited {fname} does not parse: {exc}")
        return 1

    if args.apply:
        v92_tf.write(text)
        print(f"WROTE {fname}")
    else:
        print(f"[dry-run] {fname} would change ({len(restored)} blocks). Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
