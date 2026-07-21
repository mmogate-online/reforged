"""dc-restore dcq: cross-source content query CLI for Island-of-Dawn content.

Answers focused lookups by reading the three content sources side by side:
the old client DataCenter (design reference), the v31 server datasheet
(easy-restore source), and the v92 server datasheet (current truth, read from
the WORKING TREE so authored/tuned content is what you see).

Subcommands:
  quest <gid>          header wiring + per-task gameplay fields + comp + title +
                       dialog presence, CLIENT | V31 | V92, DIFFs marked.
  npc <hz> <tid>       template name (v31/v92 + client), spawn entries across the
                       island TerritoryData of both servers, and island quests
                       that reference the NPC as giver or task target.
  name <substring>     case-insensitive search of client creature names/titles,
                       joined against island NpcData to show which hz layers hold
                       the template.
  collection <cid>     Collections.xml attrs, island CollectionTerritory spawn
                       counts, and island quests whose tasks reference the id.

Read-only: dcq never writes to any datasheet or source file.
"""

import argparse
import sys

import dclib
from dclib import (
    ISLAND_ZONES,
    Sources,
    comp_summary,
    collection_attrs,
    collection_territory_spawns,
    find_file_ci,
    find_zone_file,
    index_client_comp,
    index_comp_file,
    index_creature_names,
    index_quest_shards_by_id,
    island_quest_paths,
    load_island_quests,
    load_references,
    client_quest_title,
    npc_template_ids,
    parse_quest,
    read_text,
    territory_spawns,
    v31_dialog_exists,
    v92_dialog_exists,
)

DIFF = "  <<< DIFF"


class Ctx:
    """Lazily-built shared indices over the three sources."""

    def __init__(self, sources: Sources):
        self.s = sources
        self._client_quest_idx = None
        self._island_quests = None
        self._creature_rows = None
        self._client_comp = None
        self._terr_cache: dict[tuple[str, int], list[dict]] = {}

    @property
    def client_quest_idx(self) -> dict[int, "object"]:
        if self._client_quest_idx is None:
            self._client_quest_idx = index_quest_shards_by_id(self.s.old_client / "Quest")
        return self._client_quest_idx

    @property
    def island_quests(self) -> dict:
        if self._island_quests is None:
            self._island_quests = load_island_quests(self.s)
        return self._island_quests

    @property
    def creature_rows(self) -> list[dict]:
        if self._creature_rows is None:
            self._creature_rows = index_creature_names(self.s.old_client / "StrSheet_Creature")
        return self._creature_rows

    @property
    def client_comp(self) -> dict:
        if self._client_comp is None:
            self._client_comp = index_client_comp(self.s.old_client / "QuestCompensationData")
        return self._client_comp

    def territory(self, which: str, zone: int) -> list[dict]:
        """Spawn entries for a zone; which is 'v92' (working tree) or 'v31'."""
        key = (which, zone)
        if key not in self._terr_cache:
            root = self.s.v92 if which == "v92" else self.s.v31
            f = find_zone_file(root, "TerritoryData", zone)
            self._terr_cache[key] = territory_spawns(read_text(f)) if f else []
        return self._terr_cache[key]


# ---------------------------------------------------------------------------
# quest
# ---------------------------------------------------------------------------

def _load_quest_models(ctx: Ctx, gid: int) -> dict[str, dict | None]:
    s = ctx.s
    out: dict[str, dict | None] = {"client": None, "v31": None, "v92": None}
    cp = ctx.client_quest_idx.get(gid)
    if cp is not None:
        out["client"] = parse_quest(read_text(cp))
    for src, root in (("v31", s.v31), ("v92", s.v92)):
        p = root / "QuestData" / f"{gid:06d}.quest"
        if p.exists():
            out[src] = parse_quest(read_text(p))
    return out


def _row(label: str, cli, v31, v92) -> str:
    vals = [cli, v31, v92]
    diff = len({v for v in vals if v is not None}) > 1
    cell = lambda v: "-" if v in (None, "") else str(v)
    line = f"  {label:<14} {cell(cli):<22} {cell(v31):<22} {cell(v92):<22}"
    return line + (DIFF if diff else "")


def cmd_quest(ctx: Ctx, gid: int) -> int:
    m = _load_quest_models(ctx, gid)
    cli, v31, v92 = m["client"], m["v31"], m["v92"]
    present = [k for k in ("client", "v31", "v92") if m[k]]
    if not present:
        print(f"Quest {gid} not found in any source.")
        return 1

    anchor = v92 or v31 or cli
    hz, local = anchor["hz"], anchor["local"]
    title = client_quest_title(ctx.s.old_client / "StrSheet_Quest", gid)

    print("=" * 78)
    print(f"Quest {gid}  (hz {hz}, local {local})   EN: {title or '(no client title)'}")
    print("=" * 78)
    print(f"  {'field':<14} {'CLIENT':<22} {'V31':<22} {'V92 (worktree)':<22}")
    print("  " + "-" * 74)

    def g(src, key):
        return src[key] if src else None

    def prereq(src):
        if not src:
            return None
        if src["sentinel"]:
            return "99,99 (DISABLED)"
        return ",".join(src["prereqs"]) if src["prereqs"] else "(none)"

    print(_row("type", g(cli, "quest_type"), g(v31, "quest_type"), g(v92, "quest_type")))
    print(_row("repeat", g(cli, "repeat"), g(v31, "repeat"), g(v92, "repeat")))
    print(_row("storyGroup", g(cli, "story_group") or "(none)", g(v31, "story_group") or "(none)",
               g(v92, "story_group") or "(none)"))
    print(_row("prereq", prereq(cli), prereq(v31), prereq(v92)))
    print(_row("giver", g(cli, "giver"), g(v31, "giver"), g(v92, "giver")))
    print(_row("minLevel", g(cli, "min_level"), g(v31, "min_level"), g(v92, "min_level")))
    print(_row("maxLevel", g(cli, "max_level") or "(none)", g(v31, "max_level") or "(none)",
               g(v92, "max_level") or "(none)"))
    print(_row("class", g(cli, "classes") or "(any)", g(v31, "classes") or "(any)",
               g(v92, "classes") or "(any)"))

    # Tasks: union of task ids across sources.
    print()
    print("  Tasks (gameplay fields per task id):")
    all_tids = sorted({t for src in (cli, v31, v92) if src for t in src["tasks"]},
                      key=lambda x: (isinstance(x, str), x))
    for tid in all_tids:
        ct = cli["tasks"].get(tid) if cli else None
        t31 = v31["tasks"].get(tid) if v31 else None
        t92 = v92["tasks"].get(tid) if v92 else None
        ttype = (t92 or t31 or ct or {}).get("type", "?")
        print(f"    Task {tid} [{ttype}]")
        for field in ("monsters", "collections", "deliver_items", "deliver_direct",
                      "visits", "target_npc", "dungeon"):
            cv = ct.get(field) if ct else None
            v3 = t31.get(field) if t31 else None
            v9 = t92.get(field) if t92 else None
            if not any([cv, v3, v9]):
                continue
            fmt = lambda v: "-" if v in (None, "", []) else str(v)
            diff = len({str(x) for x in (cv, v3, v9) if x not in (None, "", [])}) > 1
            line = f"      {field:<14} {fmt(cv):<24} {fmt(v3):<24} {fmt(v9):<24}"
            print(line + (DIFF if diff else ""))

    # Compensation (hz-keyed server file; client sharded).
    print()
    print("  Compensation:")
    ccomp = ctx.client_comp.get(gid)
    v31_comp = v92_comp = None
    if hz is not None:
        v31f = find_file_ci(ctx.s.v31 / "CompensationData", f"QuestCompensationData_{hz}.xml")
        if v31f:
            v31_comp = index_comp_file(read_text(v31f)).get(gid)
        v92f = ctx.s.v92 / "CompensationData" / f"QuestCompensationData_{hz}.xml"
        if v92f.exists():
            v92_comp = index_comp_file(read_text(v92f)).get(gid)
    keys = {dclib.comp_reward_key(c) for c in (ccomp, v31_comp, v92_comp)}
    diff = DIFF if len(keys) > 1 else ""
    print(f"    CLIENT: {comp_summary(ccomp)}")
    print(f"    V31   : {comp_summary(v31_comp)}")
    print(f"    V92   : {comp_summary(v92_comp)}{diff}")

    # Dialog + title strings.
    print()
    print("  Dialog / strings:")
    if hz is not None and local is not None:
        cli_dlg = (hz, local) in dclib.index_client_quest_dialogs(ctx.s.old_client / "QuestDialog") \
            if cli else False
        v31_dlg = v31_dialog_exists(ctx.s.v31 / "QuestDialog", hz, local)
        v92_dlg = v92_dialog_exists(ctx.s.v92 / "QuestDialog", hz, local)
        print(_row("dialog file", "yes" if cli_dlg else "no", "yes" if v31_dlg else "no",
                   "yes" if v92_dlg else "no"))
    v92_title = dclib.strsheet_quest_ids(read_text(ctx.s.v92 / "StrSheet_Quest.xml")).get(gid * 1000 + 1)
    print(_row("EN title", title, None, v92_title))
    print()
    return 0


# ---------------------------------------------------------------------------
# npc
# ---------------------------------------------------------------------------

def cmd_npc(ctx: Ctx, hz: int, tid: int) -> int:
    s = ctx.s
    print("=" * 78)
    print(f"NPC template {tid} in hunting zone {hz}")
    print("=" * 78)

    # Template name in each server NpcData_<hz>.
    v92f = find_zone_file(s.v92, "NpcData", hz)
    v31f = find_zone_file(s.v31, "NpcData", hz)
    v92_name = npc_template_ids(read_text(v92f)).get(tid) if v92f else None
    v31_name = npc_template_ids(read_text(v31f)).get(tid) if v31f else None

    # Client names (StrSheet_Creature rows for this hz + tid).
    cli_rows = [r for r in ctx.creature_rows if r["templateId"] == tid and r["hz"] == hz]
    print("  Names:")
    print(f"    v92 NpcData_{hz}: {v92_name or '(absent)'}")
    print(f"    v31 NpcData_{hz}: {v31_name or '(absent)'}")
    if cli_rows:
        for r in cli_rows:
            title = f' "{r["title"]}"' if r["title"] else ""
            print(f"    client StrSheet_Creature: {r['name']}{title}  ({r['race']}/{r['gender']})")
    else:
        print("    client StrSheet_Creature: (absent)")

    # Spawn entries. npcTemplateId is unique only within a hunting zone, so the
    # definitive spawn for ref (hz,tid) is TerritoryData_<hz>. Same-numbered
    # templates in other island zones are distinct NPCs and are not conflated.
    print()
    print(f"  Spawns (TerritoryData_{hz}, the ref's own zone):")
    for which in ("v92", "v31"):
        hits = [e for e in ctx.territory(which, hz) if e["npcTemplateId"] == tid]
        label = "v92 (worktree)" if which == "v92" else "v31"
        if not hits:
            print(f"    {label}: NOT SPAWNED")
            continue
        print(f"    {label}: {len(hits)} entr{'y' if len(hits) == 1 else 'ies'}")
        for e in hits[:12]:
            print(f"      grp {e['group_id']} ({e['group_desc']}) terr={e['territory_desc']} "
                  f"npc={e['desc']} pos={e['pos']}")
    # Same local id in other island zones (distinct NPCs), reported for context only.
    others = []
    for zone in ISLAND_ZONES:
        if zone == hz:
            continue
        v92f = find_zone_file(s.v92, "NpcData", zone)
        if v92f and tid in npc_template_ids(read_text(v92f)):
            others.append(f"z{zone}={npc_template_ids(read_text(v92f))[tid]}")
    if others:
        print(f"    (note: local id {tid} is a DIFFERENT NPC in {', '.join(others)})")

    # Quests referencing this NPC (giver or task target) in the island band.
    print()
    print("  Referenced by island quests:")
    ref = f"{hz},{tid}"
    found = False
    for src in ("client", "v31", "v92"):
        givers, targets = [], []
        for gid, model in sorted(ctx.island_quests[src].items()):
            if model.get("giver") == ref:
                givers.append(gid)
            if ref in model.get("target_npcs", []):
                targets.append(gid)
        if givers or targets:
            found = True
            print(f"    {src}: giver of {givers or '-'} | target of {targets or '-'}")
    if not found:
        print("    (no island-band quest references this NPC)")
    print()
    return 0


# ---------------------------------------------------------------------------
# name
# ---------------------------------------------------------------------------

def cmd_name(ctx: Ctx, needle: str) -> int:
    s = ctx.s
    low = needle.lower()
    rows = [r for r in ctx.creature_rows
            if low in r["name"].lower() or low in r["title"].lower()]
    print("=" * 78)
    print(f"Creature name search: '{needle}'  ({len(rows)} match{'' if len(rows) == 1 else 'es'})")
    print("=" * 78)
    if not rows:
        print("  No client StrSheet_Creature name/title matches.")
        return 0

    # Join each row against NpcData of its OWN hz (templateId is unique only
    # within a hz; the same number in another island zone is a different NPC).
    def templates(which, zone):
        root = s.v92 if which == "v92" else s.v31
        f = find_zone_file(root, "NpcData", zone)
        return npc_template_ids(read_text(f)) if f else {}

    for r in sorted(rows, key=lambda x: (x["hz"] if x["hz"] is not None else -1, x["templateId"] or 0)):
        title = f' "{r["title"]}"' if r["title"] else ""
        print(f"  {r['name']}{title}  templateId={r['templateId']} hz={r['hz']} ({r['race']}/{r['gender']})")
        if r["hz"] in ISLAND_ZONES:
            for which in ("v92", "v31"):
                name = templates(which, r["hz"]).get(r["templateId"])
                mark = f"defines it as '{name}'" if name else "does NOT define it"
                print(f"      {which} NpcData_{r['hz']}: {mark}")
    print()
    return 0


# ---------------------------------------------------------------------------
# collection
# ---------------------------------------------------------------------------

def cmd_collection(ctx: Ctx, cid: int) -> int:
    s = ctx.s
    print("=" * 78)
    print(f"Collection {cid}")
    print("=" * 78)
    col_file = s.v92 / "CollectionData" / "Collections.xml"
    attrs = collection_attrs(read_text(col_file), cid) if col_file.exists() else None
    if attrs:
        keys = ["collectionId", "grade", "typeName", "minUserLevel", "pickSkillType",
                "neededProficiency", "questCollection"]
        shown = {k: attrs[k] for k in keys if k in attrs}
        print("  Collections.xml:", shown)
    else:
        print("  Collections.xml: (collection id not found in v92)")

    print()
    print("  Island spawn territories (v92):")
    spawns = collection_territory_spawns(s.v92 / "CollectionData", cid, set(ISLAND_ZONES))
    if spawns:
        for row in spawns:
            print(f"    {row['file']} (continent {row['continentId']}): "
                  f"{row['groups']} group(s), {row['spawn_entries']} spawn points")
    else:
        print("    (no island CollectionTerritory spawns this collection)")

    print()
    print("  Referenced by island quests (task 콜렉션Id):")
    found = False
    for src in ("client", "v31", "v92"):
        hits = []
        for gid, model in sorted(ctx.island_quests[src].items()):
            for t in model["tasks"].values():
                if str(cid) in t["collections"]:
                    hits.append(gid)
                    break
        if hits:
            found = True
            print(f"    {src}: {hits}")
    if not found:
        print("    (no island-band quest references this collection)")
    print()
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-source Island content query.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("quest", help="quest header/tasks/comp/dialog, 3-source")
    q.add_argument("gid", type=int)
    n = sub.add_parser("npc", help="npc name/spawns/quest-refs")
    n.add_argument("hz", type=int)
    n.add_argument("tid", type=int)
    nm = sub.add_parser("name", help="creature name substring search")
    nm.add_argument("needle")
    c = sub.add_parser("collection", help="collection attrs/spawns/quest-refs")
    c.add_argument("cid", type=int)
    args = parser.parse_args()

    refs = load_references()
    sources = Sources(refs)
    problems = sources.validate()
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        return 1
    ctx = Ctx(sources)

    if args.cmd == "quest":
        return cmd_quest(ctx, args.gid)
    if args.cmd == "npc":
        return cmd_npc(ctx, args.hz, args.tid)
    if args.cmd == "name":
        return cmd_name(ctx, args.needle)
    if args.cmd == "collection":
        return cmd_collection(ctx, args.cid)
    return 2


if __name__ == "__main__":
    sys.exit(main())
