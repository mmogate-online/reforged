"""dc-restore quest_restore: restore quest header wiring from the client reference.

Four Island-of-Dawn quests were soft-disabled in the v92 server datasheet by a
sentinel prerequisite (`<퀘스트Id>99,99</퀘스트Id>`) and an emptied story-group
id. This module restores the original wiring recorded in the old client
DataCenter, touching ONLY the prerequisite and story-group fields with
format-preserving textual surgery: the .quest file is edited in place by regex
slice, never round-tripped through ElementTree, so tasks, dialogs and body stay
byte-identical.

Fields restored per quest (source of truth: the client Quest shard):
  - prerequisite: client has no prereq -> drop the 99,99 sentinel block to the
    canonical no-prereq form (no 선행퀘스트 element, mirroring active quests such
    as 001301.quest); client has a prereq -> replace 99,99 with the client value.
  - story group: client has a value and v92 is <스토리그룹Id /> -> restore it,
    and register the quest in QuestGroupList.xml under that StoryGroup.

--relink A=x,y sets quest A's existing single prerequisite to x,y (manual
override; refuses to act if A does not currently have exactly one prereq).

Restored files are the canonical content baseline. They are committed on the
baseline lane, separate from DSL patch overlays. Dry-run (unified diff) is the
default; --apply writes after validating that every edited file still parses.
"""

import argparse
import difflib
import sys
from pathlib import Path

import dclib
from dclib import (
    Sources,
    TextFile,
    index_quest_shards_by_id,
    load_references,
    validate_xml,
)

# Korean header tags, embedded as escapes so this source stays pure ASCII.
_SEONHAENG = "선행퀘스트"      # 선행퀘스트 (prerequisite)
_QUESTID = "퀘스트Id"                   # 퀘스트Id  (prereq quest id)
_STORY = "스토리그룹Id"         # 스토리그룹Id (story group id)

_S_OPEN, _S_CLOSE = "<" + _SEONHAENG + ">", "</" + _SEONHAENG + ">"
_Q_OPEN, _Q_CLOSE = "<" + _QUESTID + ">", "</" + _QUESTID + ">"

# The nested two-level prerequisite block (Korean/ASCII tags carry no regex
# metacharacters, so they are embedded literally).
import re

_BLOCK = (
    _S_OPEN + r"\s*" + _S_OPEN + r"\s*"
    + _Q_OPEN + r"([^<]*)" + _Q_CLOSE + r"\s*"
    + _S_CLOSE + r"\s*" + _S_CLOSE
)
_BLOCK_RE = re.compile(_BLOCK)
# For no-prereq conversion, also swallow the preceding newline and indent so no
# blank line is left behind.
_BLOCK_WITH_LEAD_RE = re.compile(r"\n[ \t]*" + _BLOCK)

_STORY_EMPTY_RE = re.compile("<" + _STORY + r"\s*/>")
_STORY_VALUE_RE = re.compile("<" + _STORY + r">([^<]*)</" + _STORY + ">")

_SENTINEL = "99,99"


# ---------------------------------------------------------------------------
# Client reference readers
# ---------------------------------------------------------------------------

def client_prereq(text: str) -> str | None:
    """The client quest's prerequisite value, or None when it has no prereq."""
    m = _BLOCK_RE.search(text)
    return m.group(1).strip() if m else None


def client_story_group(text: str) -> str | None:
    """The client quest's story-group id value, or None when empty/absent."""
    m = _STORY_VALUE_RE.search(text)
    if m and m.group(1).strip():
        return m.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# Surgical edits on the v92 .quest text (in-memory LF)
# ---------------------------------------------------------------------------

def v92_prereq(text: str) -> tuple[str, int] | None:
    """(value, count) of prerequisite entries in the header, or None if absent."""
    matches = _BLOCK_RE.findall(text)
    if not matches:
        return None
    return matches[0].strip(), len(matches)


def drop_prereq_block(text: str) -> str:
    """Remove the whole prerequisite block, yielding the no-prereq form."""
    return _BLOCK_WITH_LEAD_RE.sub("", text, count=1)


def set_prereq_value(text: str, new_value: str) -> str:
    """Replace the single prerequisite value in place, preserving whitespace."""
    m = _BLOCK_RE.search(text)
    if not m:
        raise ValueError("no prerequisite block to replace")
    block = m.group(0)
    old_inner = _Q_OPEN + m.group(1) + _Q_CLOSE
    new_inner = _Q_OPEN + new_value + _Q_CLOSE
    new_block = block.replace(old_inner, new_inner, 1)
    return text[:m.start()] + new_block + text[m.end():]


def set_story_group(text: str, value: str) -> str:
    """Fill an empty <스토리그룹Id /> with value."""
    return _STORY_EMPTY_RE.sub("<" + _STORY + ">" + value + "</" + _STORY + ">", text, count=1)


# ---------------------------------------------------------------------------
# QuestGroupList registration
# ---------------------------------------------------------------------------

def _story_group_block_span(qgl: str, gid: str):
    m = re.search(r'<StoryGroup\b[^>]*\bid="' + re.escape(gid) + r'"[^>]*>.*?</StoryGroup>', qgl, re.S)
    return m


def client_group_predecessor(client_qgl: str, gid: str, quest_id: str) -> str | None:
    """The quest id that immediately precedes quest_id in the client StoryGroup."""
    m = _story_group_block_span(client_qgl, gid)
    if not m:
        return None
    ids = re.findall(r'<Quest\b[^>]*\bid="(\d+)"', m.group(0))
    if quest_id not in ids:
        return None
    idx = ids.index(quest_id)
    return ids[idx - 1] if idx > 0 else None


def client_group_dec(client_qgl: str, gid: str, quest_id: str) -> str:
    """The dec text the client records for the quest (empty when absent)."""
    m = _story_group_block_span(client_qgl, gid)
    if not m:
        return ""
    entry = re.search(r'<Quest\b[^>]*\bid="' + re.escape(quest_id) + r'"[^>]*/?>', m.group(0))
    if not entry:
        return ""
    dec = re.search(r'\bdec="([^"]*)"', entry.group(0))
    return dec.group(1) if dec else ""


def register_in_qgl(qgl: str, gid: str, quest_id: str, dec: str, predecessor: str | None):
    """Insert <Quest id=.. dec=../> into StoryGroup gid; return (text, note)."""
    m = _story_group_block_span(qgl, gid)
    if not m:
        return qgl, f"StoryGroup {gid} not found in v92 QuestGroupList; skipped"
    block = m.group(0)
    if re.search(r'<Quest\b[^>]*\bid="' + re.escape(quest_id) + r'"', block):
        return qgl, f"quest {quest_id} already registered in StoryGroup {gid}; skipped"

    entry_lines = re.findall(r'\n([ \t]*)<Quest\b', block)
    indent = entry_lines[0] if entry_lines else "      "
    new_line = f"\n{indent}<Quest id=\"{quest_id}\" dec=\"{dec}\" />"

    note_pos = f"after predecessor {predecessor}"
    insert_at = None
    if predecessor is not None:
        pm = re.search(r'\n[ \t]*<Quest\b[^>]*\bid="' + re.escape(predecessor) + r'"[^>]*/?>', block)
        if pm:
            insert_at = pm.end()
    if insert_at is None:
        # Predecessor absent: append at end of the group (before </StoryGroup>).
        cm = re.search(r'\n[ \t]*</StoryGroup>', block)
        insert_at = cm.start()
        note_pos = "appended at end of group (predecessor absent)"

    new_block = block[:insert_at] + new_line + block[insert_at:]
    qgl = qgl[:m.start()] + new_block + qgl[m.end():]
    return qgl, f"registered quest {quest_id} in StoryGroup {gid} ({note_pos})"


# ---------------------------------------------------------------------------
# Per-quest processing
# ---------------------------------------------------------------------------

class Edit:
    def __init__(self, label: str, path: Path, before: str, after: str):
        self.label = label
        self.path = path
        self.before = before
        self.after = after


def process_quest(sources: Sources, qid: int, client_index: dict[int, Path],
                  qgl_state: dict, notes: list[str]) -> Edit | None:
    quest_path = sources.v92 / "QuestData" / f"{qid:06d}.quest"
    if not quest_path.exists():
        notes.append(f"[{qid}] v92 quest file not found: {quest_path}")
        return None
    client_path = client_index.get(qid)
    if client_path is None:
        notes.append(f"[{qid}] no client shard with root id {qid}; skipped")
        return None

    tf = TextFile(quest_path)
    original = tf.text
    text = original
    client_text = TextFile(client_path).text

    cli_prereq = client_prereq(client_text)
    cli_story = client_story_group(client_text)
    v92pr = v92_prereq(text)
    changed: list[str] = []

    # --- prerequisite ---
    if cli_prereq is None:
        if v92pr is not None and v92pr[0] == _SENTINEL:
            text = drop_prereq_block(text)
            changed.append("prereq: dropped 99,99 sentinel to no-prereq form")
        elif v92pr is not None:
            notes.append(f"[{qid}] client has no prereq but v92 has a non-sentinel "
                         f"prereq {v92pr[0]!r}; left untouched")
    else:
        if v92pr is None:
            notes.append(f"[{qid}] client prereq {cli_prereq!r} but v92 has no prereq "
                         f"block; cannot restore surgically, skipped")
        elif v92pr[0] == _SENTINEL:
            text = set_prereq_value(text, cli_prereq)
            changed.append(f"prereq: 99,99 -> {cli_prereq}")
        elif v92pr[0] == cli_prereq:
            pass  # already correct
        else:
            notes.append(f"[{qid}] DIVERGENCE: v92 prereq {v92pr[0]!r} vs client "
                         f"{cli_prereq!r}; non-sentinel, left untouched (use --relink)")

    # --- story group ---
    if cli_story is not None:
        if _STORY_EMPTY_RE.search(text):
            text = set_story_group(text, cli_story)
            changed.append(f"storyGroup: empty -> {cli_story}")
            # Register in QuestGroupList.
            pred = client_group_predecessor(qgl_state["client"], cli_story, str(qid))
            dec = client_group_dec(qgl_state["client"], cli_story, str(qid))
            qgl_state["text"], note = register_in_qgl(
                qgl_state["text"], cli_story, str(qid), dec, pred)
            notes.append(f"[{qid}] {note}")
        else:
            sm = _STORY_VALUE_RE.search(text)
            cur = sm.group(1).strip() if sm else "(absent)"
            if cur != cli_story:
                notes.append(f"[{qid}] v92 storyGroup {cur!r} vs client {cli_story!r}; "
                             f"v92 already non-empty, left untouched")

    if not changed:
        notes.append(f"[{qid}] nothing to do (no sentinel, no story-group gap)")
        return None
    notes.append(f"[{qid}] " + "; ".join(changed))
    return Edit(f"QuestData/{qid:06d}.quest", quest_path, original, text)


def process_relink(sources: Sources, qid: int, value: str, notes: list[str]) -> Edit | None:
    quest_path = sources.v92 / "QuestData" / f"{qid:06d}.quest"
    if not quest_path.exists():
        notes.append(f"[relink {qid}] v92 quest file not found: {quest_path}")
        return None
    tf = TextFile(quest_path)
    original = tf.text
    v92pr = v92_prereq(original)
    if v92pr is None:
        notes.append(f"[relink {qid}] no prerequisite block present; cannot relink")
        return None
    if v92pr[1] != 1:
        notes.append(f"[relink {qid}] expected a single prerequisite, found {v92pr[1]}; "
                     f"refusing to relink")
        return None
    if v92pr[0] == value:
        notes.append(f"[relink {qid}] prerequisite already {value}; nothing to do")
        return None
    text = set_prereq_value(original, value)
    notes.append(f"[relink {qid}] prereq {v92pr[0]} -> {value}")
    return Edit(f"QuestData/{qid:06d}.quest", quest_path, original, text)


# ---------------------------------------------------------------------------
# Diff and main
# ---------------------------------------------------------------------------

def unified(edit: Edit) -> str:
    diff = difflib.unified_diff(
        edit.before.splitlines(keepends=True),
        edit.after.splitlines(keepends=True),
        fromfile=f"a/{edit.label}", tofile=f"b/{edit.label}",
    )
    return "".join(diff)


def parse_relink(spec: str) -> tuple[int, str]:
    left, _, right = spec.partition("=")
    return int(left.strip()), right.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore quest header wiring from the client reference.")
    parser.add_argument("--quests", default="", help="Comma-separated global quest ids to restore")
    parser.add_argument("--relink", action="append", default=[],
                        help="A=x,y : set quest A's single prerequisite to x,y (repeatable)")
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run diff)")
    args = parser.parse_args()

    quests = [int(q) for q in args.quests.split(",") if q.strip()]
    relinks = [parse_relink(s) for s in args.relink]
    if not quests and not relinks:
        print("Nothing requested: pass --quests and/or --relink.")
        return 2

    refs = load_references()
    sources = Sources(refs)
    problems = sources.validate()
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        return 1

    client_index = index_quest_shards_by_id(sources.old_client / "Quest")

    qgl_path = sources.v92 / "QuestGroupList.xml"
    qgl_tf = TextFile(qgl_path)
    client_qgl_dir = sources.old_client / "QuestGroupList"
    client_qgl = ""
    if client_qgl_dir.is_dir():
        for entry in sorted(client_qgl_dir.glob("*.xml")):
            client_qgl += TextFile(entry).text + "\n"
    qgl_state = {"text": qgl_tf.text, "client": client_qgl}
    qgl_before = qgl_tf.text

    notes: list[str] = []
    edits: list[Edit] = []

    for qid in quests:
        e = process_quest(sources, qid, client_index, qgl_state, notes)
        if e:
            edits.append(e)
    for qid, value in relinks:
        e = process_relink(sources, qid, value, notes)
        if e:
            edits.append(e)

    if qgl_state["text"] != qgl_before:
        edits.append(Edit("QuestGroupList.xml", qgl_path, qgl_before, qgl_state["text"]))

    print("=" * 78)
    print("quest_restore " + ("(APPLY)" if args.apply else "(dry-run)"))
    print("=" * 78)
    for n in notes:
        print("  " + n)
    print()

    if not edits:
        print("No file changes produced.")
        return 0

    for e in edits:
        print(unified(e))

    # Validate every edited file parses.
    for e in edits:
        try:
            validate_xml(e.after)
        except Exception as exc:
            print(f"ERROR: edited {e.label} does not parse: {exc}")
            return 1

    if args.apply:
        for e in edits:
            if e.label == "QuestGroupList.xml":
                qgl_tf.write(e.after)
            else:
                TextFile(e.path).write(e.after)
            print(f"WROTE {e.label}")
    else:
        print(f"[dry-run] {len(edits)} file(s) would change. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
