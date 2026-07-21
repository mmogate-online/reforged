"""Shared library for the dc-restore toolkit.

Reads three restoration sources (old client DataCenter, v31 server datasheet,
v92 server datasheet) and exposes helpers used by every dc-restore module.

The v92 datasheet lives inside a git repo whose working tree may hold
uncommitted patch overlays. Content comparisons must diff against the clean
git HEAD baseline, not the working tree, so V92Baseline reads dirty files from
HEAD while leaving clean files on disk. See README.md for the rationale.
"""

import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Force UTF-8 output on Windows (datasheets carry Korean/Cyrillic text).
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# References and source resolution
# ---------------------------------------------------------------------------

def reforged_dir() -> Path:
    """The reforged/ folder (this script sits at reforged/tools/dc-restore/)."""
    return Path(__file__).resolve().parents[2]


def load_references() -> dict[str, str]:
    """Parse reforged/.references (key=value lines, blanks and # skipped)."""
    refs: dict[str, str] = {}
    ref_file = reforged_dir() / ".references"
    for line in ref_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if value:
            refs[key.strip()] = value.strip()
    return refs


class Sources:
    """Resolved and validated restoration source roots."""

    def __init__(self, refs: dict[str, str]):
        self.old_client = Path(refs["old_client_dc"])
        self.v31 = Path(refs["v31_datasheet"])
        self.v92 = Path(refs["server_datasheet"])
        self.baseline = V92Baseline(self.v92)

    def validate(self) -> list[str]:
        """Return a list of human-readable problems (empty list means all good)."""
        problems: list[str] = []
        checks = [
            ("old_client_dc", self.old_client),
            ("v31_datasheet", self.v31),
            ("server_datasheet", self.v92),
        ]
        for key, path in checks:
            if not path.exists():
                hint = ""
                if str(path).startswith(("Z:", "z:", "//", "\\\\")):
                    hint = " (network drive unmounted?)"
                problems.append(f"{key} not found: {path}{hint}")
        return problems


# ---------------------------------------------------------------------------
# XML helpers (namespace-agnostic; client shards are namespaced, server is not)
# ---------------------------------------------------------------------------

def strip_ns(tag: str) -> str:
    """Local element name without any {namespace} prefix."""
    return tag.rsplit("}", 1)[-1]


def parse_root(text: str) -> ET.Element:
    """Parse XML text into a root element, tolerating a leading BOM."""
    text = text.lstrip("﻿ \t\r\n")
    return ET.fromstring(text)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def iter_local(root: ET.Element, name: str):
    """Yield descendant elements whose local tag equals name."""
    for el in root.iter():
        if strip_ns(el.tag) == name:
            yield el


def parse_pair(value: str | None) -> tuple[int, int] | None:
    """Parse a 'a,b' comma pair (e.g. Quest번호 'hz,localId') into ints."""
    if not value:
        return None
    m = re.match(r"\s*(\d+)\s*,\s*(\d+)", value)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


# ---------------------------------------------------------------------------
# Server file location (case-insensitive; AiData_64 breaks the AIData_ pattern)
# ---------------------------------------------------------------------------

_dir_cache: dict[str, dict[str, Path]] = {}


def _dir_index(directory: Path) -> dict[str, Path]:
    key = str(directory).lower()
    if key not in _dir_cache:
        index: dict[str, Path] = {}
        if directory.is_dir():
            for entry in directory.iterdir():
                index[entry.name.lower()] = entry
        _dir_cache[key] = index
    return _dir_cache[key]


def find_file_ci(directory: Path, filename: str) -> Path | None:
    """Case-insensitive lookup of filename inside directory."""
    return _dir_index(directory).get(filename.lower())


def find_zone_file(root: Path, family: str, zone: int) -> Path | None:
    """Locate a per-zone server file such as NpcData_13.xml, case-insensitively.

    Handles the zone-64 trap where the AI file is lowercase AiData_64.xml while
    every other zone uses AIData_<zone>.xml.
    """
    return find_file_ci(root, f"{family}_{zone}.xml")


# ---------------------------------------------------------------------------
# Client Novadrop shard indexing
# ---------------------------------------------------------------------------

_HZ_ATTR = re.compile(r'huntingZoneId="(\d+)"')
_QUESTNO = re.compile(r"<Quest번호>\s*(\d+)\s*,")


def _peek(path: Path, size: int = 800) -> str:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        return fh.read(size)


def zone_from_hz_attr(head: str) -> int | None:
    m = _HZ_ATTR.search(head)
    return int(m.group(1)) if m else None


def zone_from_questno(head: str) -> int | None:
    m = _QUESTNO.search(head)
    return int(m.group(1)) if m else None


def index_client_shards(family_dir: Path, zone_extractor, zones: set[int]) -> dict[int, list[Path]]:
    """Group client shard files under family_dir by zone.

    zone_extractor(head_text) returns the zone int for a shard (or None). Only
    the first bytes of each shard are read for speed. Returns zone -> shard paths
    restricted to the requested zones.
    """
    result: dict[int, list[Path]] = {z: [] for z in zones}
    if not family_dir.is_dir():
        return result
    for entry in family_dir.iterdir():
        if entry.suffix.lower() != ".xml":
            continue
        zone = zone_extractor(_peek(entry))
        if zone in result:
            result[zone].append(entry)
    return result


# ---------------------------------------------------------------------------
# v92 git HEAD baseline reader
# ---------------------------------------------------------------------------

class V92Baseline:
    """Reads v92 datasheet content from git HEAD for dirty files.

    Uncommitted working-tree edits are patch overlays (deliberate tuning), not
    lost content. Baseline reads must therefore come from HEAD for any file that
    is dirty per `git status --porcelain`; clean files are read from disk.
    """

    def __init__(self, datasheet_dir: Path):
        self.datasheet_dir = datasheet_dir
        self.repo_root = self._repo_root(datasheet_dir)
        if self.repo_root is not None:
            self.prefix = datasheet_dir.resolve().relative_to(self.repo_root).as_posix()
            self._dirty = self._porcelain()
        else:
            self.prefix = ""
            self._dirty = set()

    @staticmethod
    def _repo_root(path: Path) -> Path | None:
        r = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            return None
        return Path(r.stdout.strip())

    def _porcelain(self) -> set[str]:
        """Datasheet-relative paths of files that differ from HEAD."""
        r = subprocess.run(
            ["git", "-C", str(self.repo_root), "status", "--porcelain", "--", self.prefix],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        dirty: set[str] = set()
        marker = self.prefix + "/"
        for line in r.stdout.splitlines():
            if len(line) < 4:
                continue
            path = line[3:].strip().strip('"')
            if " -> " in path:  # rename
                path = path.split(" -> ", 1)[1]
            if path.startswith(marker):
                dirty.add(path[len(marker):])
        return dirty

    def dirty_files(self) -> set[str]:
        return set(self._dirty)

    def is_dirty(self, relpath: str) -> bool:
        return relpath.replace("\\", "/") in self._dirty

    def worktree_exists(self, relpath: str) -> bool:
        return (self.datasheet_dir / relpath).exists()

    def head_exists(self, relpath: str) -> bool:
        rel = relpath.replace("\\", "/")
        r = subprocess.run(
            ["git", "-C", str(self.repo_root), "cat-file", "-e", f"HEAD:{self.prefix}/{rel}"],
            capture_output=True,
        )
        return r.returncode == 0

    def read(self, relpath: str, baseline: bool = True) -> str | None:
        """Return file text. When baseline and the file is dirty, read from HEAD.

        Returns None when the file is absent from the chosen source (missing in
        HEAD, or missing in the working tree for a clean read).
        """
        rel = relpath.replace("\\", "/")
        if baseline and self.repo_root is not None and rel in self._dirty:
            r = subprocess.run(
                ["git", "-C", str(self.repo_root), "show", f"HEAD:{self.prefix}/{rel}"],
                capture_output=True,
            )
            if r.returncode != 0:
                return None
            return r.stdout.decode("utf-8-sig", errors="replace")
        path = self.datasheet_dir / relpath
        if not path.exists():
            return None
        return read_text(path)


# ---------------------------------------------------------------------------
# Format-preserving textual surgery
# ---------------------------------------------------------------------------

class TextFile:
    """A file read for format-preserving, byte-identical textual surgery.

    Server and client XML carry a UTF-8 BOM and a consistent newline style
    (CRLF for .quest / QuestGroupList, LF for QuestCompensationData). Editing a
    few fields must leave every other byte untouched, so this reader:

      - reads raw bytes and records whether a BOM is present,
      - records the dominant newline (CRLF if any CRLF is present, else LF),
      - normalizes the in-memory text to LF so regex surgery never has to
        reason about \\r, and
      - on encode restores the original newline and BOM.

    Round-tripping an unedited TextFile reproduces the source bytes exactly for
    any file with a single consistent newline style.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        raw = self.path.read_bytes()
        self.bom = raw[:3] == b"\xef\xbb\xbf"
        body = raw[3:] if self.bom else raw
        text = body.decode("utf-8")
        self.newline = "\r\n" if "\r\n" in text else "\n"
        self.text = text.replace("\r\n", "\n")

    def encode(self, text: str) -> bytes:
        out = text.replace("\n", "\r\n") if self.newline == "\r\n" else text
        data = out.encode("utf-8")
        return b"\xef\xbb\xbf" + data if self.bom else data

    def write(self, text: str) -> None:
        self.path.write_bytes(self.encode(text))


def validate_xml(text: str) -> None:
    """Raise if text is not well-formed XML (encoding-declaration safe)."""
    ET.fromstring(text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Client quest shard index (by root quest id)
# ---------------------------------------------------------------------------

_QUEST_ROOT_ID = re.compile(r'<Quest\b[^>]*\bid="(\d+)"')


def index_quest_shards_by_id(quest_dir: Path) -> dict[int, Path]:
    """Map global quest id -> client Quest shard path.

    The client Quest folder holds sequential shards (Quest-NNNNN.xml) whose
    numeric index is not the quest id; the id lives on the shard's root
    element. Only the first bytes of each shard are read for speed.
    """
    out: dict[int, Path] = {}
    if not quest_dir.is_dir():
        return out
    for entry in quest_dir.iterdir():
        if entry.suffix.lower() != ".xml":
            continue
        m = _QUEST_ROOT_ID.search(_peek(entry, 500))
        if m:
            out[int(m.group(1))] = entry
    return out


# ---------------------------------------------------------------------------
# Commented-out markup scanner
# ---------------------------------------------------------------------------

_COMMENT = re.compile(r"<!--(.*?)-->", re.S)


def scan_comments(text: str, min_len: int = 1):
    """Yield (line_no, snippet) for comment blocks that contain '<' markup."""
    for m in _COMMENT.finditer(text):
        body = m.group(1)
        if "<" not in body:
            continue
        snippet = " ".join(body.split())
        if len(snippet) < min_len:
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        yield line_no, snippet


# ===========================================================================
# Quest model parsing (shared by dcq.py and audit_quests.py)
#
# Server .quest files and client Quest shards use the same Korean tag set, so
# one namespace-agnostic parser reads both. The client is "minified": it drops
# empty/default elements and reorders Header/Body, so a structural comparison
# must extract named gameplay fields and treat an absent field as its default
# rather than diffing raw text.
# ===========================================================================

# Header tags.
QT_NO = "Quest번호"           # "hz,local" zone key
QT_TITLE = "Quest제목"        # @quest:<gid*1000+1> title ref
QT_STORY = "스토리그룹Id"      # story group id ("" when empty)
QT_TYPE = "퀘스트종류"         # quest type (일반 / 미션 / ...)
QT_REPEAT = "반복퀘스트"       # repeat flag (반복 / 1회성 / ...)
QT_COND = "수행조건"           # pursue-condition wrapper
QT_MINLV = "최소레벨"          # min level
QT_MAXLV = "최대레벨"          # max level
QT_CLASS = "클래스"            # class restriction
QT_PREREQ = "선행퀘스트"       # prerequisite wrapper (nested one level)
QT_QUESTID = "퀘스트Id"        # prereq quest id leaf ("hz,local")
QT_TRIGGER = "발생조건"        # trigger wrapper
QT_NPCTALK = "NPC대화"         # giver NPC ref ("hz,tid")
QT_LINK = "연결퀘스트"         # linked quest

# Task tags.
TK_NAME = "이름"               # task-type discriminator (사냥Task, 방문Task, ...)
TK_MONSTER_ID = "몬스터Id"     # kill-target monster ref ("hz,tid")
TK_KILL = "사냥마리수"         # kill count
TK_CHANCE = "수여확률"         # award/drop chance
TK_COLLECTION = "콜렉션Id"     # collection (gather) id
TK_ITEM_ID = "아이템Id"        # deliver item template id
TK_DELIVER_QTY = "전달수량"    # deliver quantity
TK_TARGET_NPC = "대상NPC지정"  # target NPC ref ("hz,tid")
TK_VISIT_NPC = "NPCId"         # visit-group NPC ref ("hz,tid")
TK_DUNGEON = "던전Id"          # dungeon id
TK_FLAG_ITEM = "Flag아이템이름"  # given-item display ref (@quest:...)

_SENTINEL_PREREQ = "99,99"


def _text(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def _find_local(parent, name):
    """First direct-or-descendant child with local tag name (namespace-agnostic)."""
    for el in parent.iter():
        if el is parent:
            continue
        if strip_ns(el.tag) == name:
            return el
    return None


def _parent_map(root):
    return {c: p for p in root.iter() for c in p}


def _extract_task(task_el) -> dict:
    """Normalize one <Task> into named gameplay fields (absent -> default)."""
    tid_raw = task_el.get("id")
    out = {
        "id": int(tid_raw) if tid_raw and tid_raw.isdigit() else tid_raw,
        "type": "",
        "monsters": [], "collections": [], "deliver_items": [],
        "deliver_direct": [], "visits": [], "target_npc": [], "dungeon": "",
    }
    body = None
    for child in task_el:
        tag = strip_ns(child.tag)
        if tag == "Header":
            nm = _find_local(child, TK_NAME)
            out["type"] = _text(nm)
        elif tag == "Body":
            body = child
    if body is None:
        return out

    pm = _parent_map(body)
    for el in body.iter():
        tag = strip_ns(el.tag)
        if tag == TK_MONSTER_ID:
            wrap = pm.get(el)
            kill = chance = ""
            if wrap is not None:
                for sib in wrap:
                    st = strip_ns(sib.tag)
                    if st == TK_KILL:
                        kill = _text(sib)
                    elif st == TK_CHANCE:
                        chance = _text(sib)
            out["monsters"].append((_text(el), kill, chance))
        elif tag == TK_COLLECTION and _text(el):
            out["collections"].append(_text(el))
        elif tag == TK_ITEM_ID:
            wrap = pm.get(el)
            qty = chance = ""
            if wrap is not None:
                for sib in wrap:
                    st = strip_ns(sib.tag)
                    if st == TK_DELIVER_QTY:
                        qty = _text(sib)
                    elif st == TK_CHANCE:
                        chance = _text(sib)
            out["deliver_items"].append((_text(el), qty, chance))
        elif tag == TK_VISIT_NPC and _text(el):
            out["visits"].append(_text(el))
        elif tag == TK_TARGET_NPC and _text(el):
            out["target_npc"].append(_text(el))
        elif tag == TK_DUNGEON and _text(el):
            out["dungeon"] = _text(el)

    # Direct deliver quantity (찔러준/사냥전달 tasks: a 전달수량 that is a direct
    # Body child, not inside a 전달아이템지정 wrapper with an 아이템Id).
    for child in body:
        if strip_ns(child.tag) == TK_DELIVER_QTY and _text(child):
            flag = ""
            for sib in body:
                if strip_ns(sib.tag) == TK_FLAG_ITEM:
                    flag = _text(sib)
            out["deliver_direct"].append((flag, _text(child)))

    for k in ("monsters", "collections", "deliver_items", "deliver_direct",
              "visits", "target_npc"):
        out[k] = sorted(out[k])
    return out


def parse_quest(text: str) -> dict | None:
    """Parse a server .quest or client Quest shard into a normalized model.

    Returns None when the text is not a <Quest> document.
    """
    root = ET.fromstring(text.encode("utf-8"))
    if strip_ns(root.tag) != "Quest":
        return None
    gid_raw = root.get("id")
    gid = int(gid_raw) if gid_raw and gid_raw.isdigit() else None

    header = None
    tasks_el = None
    for child in root:
        tag = strip_ns(child.tag)
        if tag == "Header":
            header = child
        elif tag == "Tasks":
            tasks_el = child

    m = {
        "gid": gid,
        "hz": None, "local": None,
        "title_ref": "", "title_id": (gid * 1000 + 1) if gid is not None else None,
        "story_group": "", "quest_type": "", "repeat": "",
        "min_level": "", "max_level": "", "classes": "",
        "prereqs": [], "sentinel": False,
        "trigger_type": "", "giver": "", "link": "",
        "tasks": {}, "target_npcs": [],
    }
    if header is not None:
        no = _find_local(header, QT_NO)
        pair = parse_pair(_text(no)) if no is not None else None
        if pair:
            m["hz"], m["local"] = pair
        m["title_ref"] = _text(_find_local(header, QT_TITLE))
        sg = _find_local(header, QT_STORY)
        m["story_group"] = _text(sg)
        m["quest_type"] = _text(_find_local(header, QT_TYPE))
        m["repeat"] = _text(_find_local(header, QT_REPEAT))
        m["link"] = _text(_find_local(header, QT_LINK))

        cond = _find_local(header, QT_COND)
        if cond is not None:
            for c in cond:
                tag = strip_ns(c.tag)
                if tag == QT_MINLV:
                    m["min_level"] = _text(c)
                elif tag == QT_MAXLV:
                    m["max_level"] = _text(c)
                elif tag == QT_CLASS:
                    m["classes"] = _text(c)
            prereq_wrap = _find_local(cond, QT_PREREQ)
            if prereq_wrap is not None:
                for q in prereq_wrap.iter():
                    if strip_ns(q.tag) == QT_QUESTID and _text(q):
                        m["prereqs"].append(_text(q))
        m["sentinel"] = (len(m["prereqs"]) == 1 and m["prereqs"][0] == _SENTINEL_PREREQ)

        trig = _find_local(header, QT_TRIGGER)
        if trig is not None:
            for c in trig:
                m["trigger_type"] = strip_ns(c.tag)
                if strip_ns(c.tag) == QT_NPCTALK:
                    m["giver"] = _text(c)
                break

    targets: list[str] = []
    if tasks_el is not None:
        for t in tasks_el:
            if strip_ns(t.tag) != "Task":
                continue
            td = _extract_task(t)
            m["tasks"][td["id"]] = td
            targets.extend(td["target_npc"])
            targets.extend(td["visits"])
    m["target_npcs"] = sorted(set(targets))
    return m


# ---------------------------------------------------------------------------
# Quest compensation parsing (server QuestCompensationData + client shards)
# ---------------------------------------------------------------------------

def parse_comp_quest(quest_el) -> dict | None:
    """Reward payload of a <Quest questId=..> comp element, or None when empty."""
    ct = _find_local(quest_el, "CompensationType")
    if ct is None:
        return None
    items = []
    for it in quest_el.iter():
        if strip_ns(it.tag) == "Item":
            items.append((it.get("templateId", ""), it.get("quantity", ""),
                          it.get("class", "")))
    return {
        "exp": ct.get("exp", ""), "gold": ct.get("gold", ""),
        "itemBag": ct.get("itemBag", ""), "policyPoint": ct.get("policyPoint", ""),
        "type": ct.get("type", ""), "items": sorted(items),
    }


def index_comp_file(text: str) -> dict[int, dict | None]:
    """Map questId -> reward dict (or None for an empty stub) for a comp file."""
    out: dict[int, dict | None] = {}
    root = ET.fromstring(text.encode("utf-8"))
    for q in root.iter():
        if strip_ns(q.tag) != "Quest":
            continue
        qid = q.get("questId")
        if qid and qid.isdigit():
            out[int(qid)] = parse_comp_quest(q)
    return out


def index_client_comp(comp_dir: Path) -> dict[int, dict | None]:
    """Map questId -> reward dict across all client QuestCompensationData shards."""
    out: dict[int, dict | None] = {}
    if not comp_dir.is_dir():
        return out
    for entry in comp_dir.iterdir():
        if entry.suffix.lower() != ".xml":
            continue
        out.update(index_comp_file(read_text(entry)))
    return out


def comp_summary(comp: dict | None) -> str:
    """One-line human summary of a reward dict."""
    if comp is None:
        return "(empty stub)"
    parts = []
    if comp["exp"]:
        parts.append(f"{comp['exp']}xp")
    if comp["gold"]:
        parts.append(f"{comp['gold']}g")
    if comp["itemBag"]:
        parts.append(f"bag={comp['itemBag']}")
    if comp["policyPoint"]:
        parts.append(f"pp={comp['policyPoint']}")
    if comp["items"]:
        its = ",".join(f"{t}x{q}" + (f"/{c}" if c else "") for t, q, c in comp["items"])
        parts.append(f"items[{its}]")
    return " ".join(parts) if parts else "(no reward)"


def comp_reward_key(comp: dict | None):
    """Comparable reward identity (exp/gold/itemBag/items) ignoring memo/policy."""
    if comp is None:
        return None
    return (comp["exp"], comp["gold"], comp["itemBag"], tuple(comp["items"]))


# ---------------------------------------------------------------------------
# StrSheet indexing (client English + server strings)
# ---------------------------------------------------------------------------

def qgl_ids_from_text(text: str) -> set[int]:
    """Global quest ids registered anywhere in a QuestGroupList StoryGroupList."""
    return {int(m) for m in re.findall(r'<Quest\b[^>]*\bid="(\d+)"', text)}


def strsheet_quest_ids(text: str) -> dict[int, str]:
    """Map String id -> string for a StrSheet_Quest file."""
    out: dict[int, str] = {}
    for m in re.finditer(r'<String\b[^>]*\bid="(\d+)"[^>]*\bstring="([^"]*)"', text):
        out[int(m.group(1))] = m.group(2)
    return out


def client_quest_title(strsheet_dir: Path, gid: int) -> str | None:
    """English title for a global quest id (String id = gid*1000+1)."""
    want = gid * 1000 + 1
    if not strsheet_dir.is_dir():
        return None
    pat = re.compile(r'<String\b[^>]*\bid="' + str(want) + r'"[^>]*\bstring="([^"]*)"')
    for entry in strsheet_dir.glob("*.xml"):
        m = pat.search(read_text(entry))
        if m:
            return m.group(1)
    return None


# StrSheet_Creature: <HuntingZone id=..> groups <String name= templateId= title=
# gender= race= class= />. templateId is unique only within a HuntingZone.
def index_creature_names(strsheet_dir: Path) -> list[dict]:
    """All creature name rows across client StrSheet_Creature shards.

    Each row: {hz, templateId, name, title, gender, race, class}.
    """
    rows: list[dict] = []
    if not strsheet_dir.is_dir():
        return rows
    hz_re = re.compile(r'<HuntingZone\b[^>]*\bid="(\d+)"')
    str_re = re.compile(r'<String\b([^>]*)/?>')
    attr_re = re.compile(r'(\w+)="([^"]*)"')
    for entry in strsheet_dir.glob("*.xml"):
        text = read_text(entry)
        hz = None
        pos = 0
        for m in re.finditer(r'<HuntingZone\b[^>]*\bid="(\d+)"|<String\b([^>]*)>', text):
            if m.group(1) is not None:
                hz = int(m.group(1))
                continue
            attrs = dict(attr_re.findall(m.group(2) or ""))
            if "templateId" not in attrs:
                continue
            rows.append({
                "hz": hz,
                "templateId": int(attrs["templateId"]) if attrs["templateId"].isdigit() else None,
                "name": attrs.get("name", ""),
                "title": attrs.get("title", ""),
                "gender": attrs.get("gender", ""),
                "race": attrs.get("race", ""),
                "class": attrs.get("class", ""),
            })
    return rows


# ---------------------------------------------------------------------------
# NPC templates and territory spawns (server per-zone files)
# ---------------------------------------------------------------------------

def npc_template_name(text: str, tid: int) -> str | None:
    """Template name attr for a template id in an NpcData file text."""
    m = re.search(r'<Template\b[^>]*\bid="' + str(tid) + r'"[^>]*\bname="([^"]*)"', text)
    return m.group(1) if m else None


def npc_template_ids(text: str) -> dict[int, str]:
    """Map Template id -> name for an NpcData file text."""
    out: dict[int, str] = {}
    for m in re.finditer(r'<Template\b[^>]*\bid="(\d+)"[^>]*\bname="([^"]*)"', text):
        out[int(m.group(1))] = m.group(2)
    return out


def territory_spawns(text: str) -> list[dict]:
    """All <Npc> spawn entries in a TerritoryData file, with group/territory desc.

    Each entry: {npcTemplateId, desc, pos, group_id, group_desc, territory_desc}.
    """
    root = ET.fromstring(text.encode("utf-8"))
    entries: list[dict] = []
    for grp in root.iter():
        if strip_ns(grp.tag) != "TerritoryGroup":
            continue
        gid = grp.get("id", "")
        gdesc = grp.get("desc", "")
        for terr in grp.iter():
            if strip_ns(terr.tag) != "Territory":
                continue
            tdesc = terr.get("desc", "")
            for npc in terr.iter():
                if strip_ns(npc.tag) != "Npc":
                    continue
                tid = npc.get("npcTemplateId", "")
                entries.append({
                    "npcTemplateId": int(tid) if tid.isdigit() else tid,
                    "desc": npc.get("desc", ""),
                    "pos": npc.get("pos", ""),
                    "group_id": gid, "group_desc": gdesc, "territory_desc": tdesc,
                })
    return entries


# ---------------------------------------------------------------------------
# Collections (server CollectionData)
# ---------------------------------------------------------------------------

def collection_attrs(text: str, cid: int) -> dict | None:
    """Attributes of a self-closing <Collection collectionId=cid .../> element."""
    m = re.search(r'<Collection\b([^>]*\bcollectionId="' + str(cid) + r'"[^>]*)/?>', text)
    if not m:
        return None
    return dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))


def collection_territory_spawns(coll_dir: Path, cid: int, zones: set[int]) -> list[dict]:
    """Per-file spawn summary for a collection id in island CollectionTerritory files.

    A collection is spawned via <Collections typeId=cid ..> groups; each group has
    a spawnNum and <Spawn> children. Returns one row per file that spawns cid:
    {file, continentId, groups, spawn_entries}.
    """
    out: list[dict] = []
    if not coll_dir.is_dir():
        return out
    for entry in coll_dir.iterdir():
        fm = re.match(r'CollectionTerritory_(\d+)_', entry.name)
        if not fm or int(fm.group(1)) not in zones:
            continue
        text = read_text(entry)
        groups = 0
        spawns = 0
        for gm in re.finditer(r'<Collections\b([^>]*)>(.*?)</Collections>', text, re.S):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', gm.group(1)))
            if attrs.get("typeId") == str(cid):
                groups += 1
                spawns += len(re.findall(r'<Spawn\b', gm.group(2)))
        if groups:
            cont = re.search(r'continentId="(\d+)"', text)
            out.append({"file": entry.name,
                        "continentId": int(cont.group(1)) if cont else None,
                        "groups": groups, "spawn_entries": spawns})
    return out


# ---------------------------------------------------------------------------
# Quest dialog presence (three naming schemes)
# ---------------------------------------------------------------------------

def index_client_quest_dialogs(qd_dir: Path) -> set[tuple[int, int]]:
    """Set of (huntingZoneId, id) for client QuestDialog shards (dialog presence)."""
    out: set[tuple[int, int]] = set()
    if not qd_dir.is_dir():
        return out
    head_re = re.compile(r'<QuestDialog\b[^>]*\bid="(\d+)"[^>]*\bhuntingZoneId="(\d+)"')
    for entry in qd_dir.iterdir():
        if entry.suffix.lower() != ".xml":
            continue
        m = head_re.search(_peek(entry, 300))
        if m:
            out.add((int(m.group(2)), int(m.group(1))))
    return out


def v92_dialog_exists(qd_dir: Path, hz: int, local: int) -> bool:
    """v92 dialog file QuestDialog_<hz*100+local>.xml presence (case-insensitive)."""
    return find_file_ci(qd_dir, f"QuestDialog_{hz * 100 + local}.xml") is not None


def v31_dialog_exists(qd_dir: Path, hz: int, local: int) -> bool:
    """v31 dialog file QuestDialog_<hz>_<local>.xml presence (case-insensitive)."""
    return find_file_ci(qd_dir, f"QuestDialog_{hz}_{local}.xml") is not None


# ---------------------------------------------------------------------------
# Island quest scope (shared by dcq.py and audit_quests.py)
#
# Quest attribution is the global-id band 1300-1399 (all keyed Quest번호 hz=13),
# unioned across the three sources so a quest present in only one still appears.
# The --zones set drives per-zone spawn scans, not quest membership.
# ---------------------------------------------------------------------------

ISLAND_ZONES = [13, 64, 213, 313, 364, 436]
_BAND_LO, _BAND_HI = 1300, 1399


def _server_band_paths(quest_dir: Path) -> dict[int, Path]:
    out: dict[int, Path] = {}
    if not quest_dir.is_dir():
        return out
    for entry in quest_dir.iterdir():
        if entry.suffix.lower() == ".quest" and entry.stem.isdigit():
            gid = int(entry.stem)
            if _BAND_LO <= gid <= _BAND_HI:
                out[gid] = entry
    return out


def island_quest_paths(sources) -> dict[str, dict[int, Path]]:
    """{'v92','v31','client'} -> {gid: quest-file path} for the 13xx band."""
    client_all = index_quest_shards_by_id(sources.old_client / "Quest")
    client = {g: p for g, p in client_all.items() if _BAND_LO <= g <= _BAND_HI}
    return {
        "v92": _server_band_paths(sources.v92 / "QuestData"),
        "v31": _server_band_paths(sources.v31 / "QuestData"),
        "client": client,
    }


def load_island_quests(sources) -> dict[str, dict[int, dict]]:
    """{'v92','v31','client'} -> {gid: parsed quest model} for the 13xx band."""
    paths = island_quest_paths(sources)
    out: dict[str, dict[int, dict]] = {}
    for src, gmap in paths.items():
        models: dict[int, dict] = {}
        for gid, path in gmap.items():
            model = parse_quest(read_text(path))
            if model is not None:
                models[gid] = model
        out[src] = models
    return out
