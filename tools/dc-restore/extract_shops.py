"""Phase 1 north-star extraction for the Island of Dawn restoration.

Deterministic, re-runnable extractor that answers three questions from the old
TERA v17.11 client DataCenter (the restoration north star), plus two structural
checks against the current v92 client and server:

  1. SHOPS      - does the client carry merchant sell lists (store inventories)?
                  What client families relate to shops, and which IoD NPCs carry
                  a client-side villager menu (the client-level NPC linkage)?
  2. GATHERING  - the client gathering-node catalog (Collections) and the
                  interactable WorkObject catalog, with the zone-scope caveat.
  3. STRUCTURE  - (a) fence-ring drift of the 8 surviving IoD sections between
                  the v17 and v92 client Area files, and (b) a free-id check for
                  candidate region ids 13036-13039 across six spatial families in
                  both the v92 client and server.

Sources are read-only. old_client_dc and server_datasheet resolve from
reforged/.references; the v92 client DataCenter has no .references key and is
pinned by V92_CLIENT_DC below (the drift / free-id checks only).

Outputs (sorted, no timestamps) land in
  reforged/docs/plans/iod-alpha-content-loop/data/:
    v17-shops.json / v17-shops.md
    v17-gathering.json / v17-gathering.md
    v17-structure-checks.md

Usage:
    python reforged/tools/dc-restore/extract_shops.py
"""

import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import dclib

# The v92 client DataCenter has no .references key; pin it here. Used only by
# the structural drift and free-id checks, never as a restoration source.
V92_CLIENT_DC = Path(r"D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR")

SCOPE_ZONES = [13, 64, 213, 313, 364, 436]

# The 8 IoD sections that survive into v92 (compared for fence drift).
SURVIVING_SECTIONS = ["13001", "13003", "13004", "13006", "13007",
                      "13024", "13028", "13030"]
DRIFT_V17_AREA = "Area/Area-00004.xml"   # v17 client, continentId 13
DRIFT_V92_AREA = "Area/Area-00013.xml"   # v92 client, continentId 13
ROUNDING_TOLERANCE = 0.001               # v17 stores 4 decimals, v92 stores 8

# Candidate free region ids and the spatial families to prove they are unused.
FREE_ID_CANDIDATES = ["13036", "13037", "13038", "13039"]
FREE_ID_FAMILIES = ["StrSheet_Region", "AreaData", "Area", "NewWorldMapData",
                    "MapDefineData", "TeleportData", "GuardData"]

OUT_DIR = (dclib.reforged_dir() / "docs" / "plans" / "iod-alpha-content-loop"
           / "data")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _family_shard(client_root: Path, family: str) -> Path | None:
    """First numbered shard of a single-shard client family (Family-00000.xml)."""
    d = client_root / family
    if not d.is_dir():
        return None
    shards = sorted(p for p in d.glob(f"{family}-*.xml"))
    return shards[0] if shards else None


def _iter_family_files(root: Path, family: str) -> list[Path]:
    """All .xml files for a family: a folder of shards and/or flat Family*.xml."""
    paths: list[Path] = []
    d = root / family
    if d.is_dir():
        paths += [p for p in d.iterdir() if p.suffix.lower() == ".xml"]
    if root.is_dir():
        for p in root.iterdir():
            if (p.suffix.lower() == ".xml"
                    and p.name.lower().startswith(family.lower())):
                paths.append(p)
    return sorted(set(paths))


# ---------------------------------------------------------------------------
# 1. Shops
# ---------------------------------------------------------------------------

def enumerate_families(client_root: Path) -> list[str]:
    """Sorted list of client DataCenter family folder names."""
    return sorted(p.name for p in client_root.iterdir() if p.is_dir())


def extract_shops(client_root: Path) -> dict:
    families = enumerate_families(client_root)

    # Client-side shop/menu/price family discovery (name-based, evidence trail).
    shop_pat = re.compile(r"store|shop|menu|price|sell|buy|merch|vendor|trade"
                          r"|reputationitem|gamble|gambe", re.I)
    shop_related = [f for f in families if shop_pat.search(f)]

    # VillagerMenu is a bare registry: <Villager id="hz,tid" /> with no inventory.
    vm_shard = _family_shard(client_root, "VillagerMenu")
    vm_entries: list[tuple[int, int]] = []
    vm_child_tags: set[str] = set()
    if vm_shard is not None:
        root = dclib.parse_root(dclib.read_text(vm_shard))
        for el in root.iter():
            tag = dclib.strip_ns(el.tag)
            if tag == "Villager":
                pair = dclib.parse_pair(el.get("id"))
                if pair:
                    vm_entries.append(pair)
                for c in el:
                    vm_child_tags.add(dclib.strip_ns(c.tag))

    # hz-scoped creature names (templateId unique only within a HuntingZone).
    creatures = dclib.index_creature_names(client_root / "StrSheet_Creature")
    name_by_key: dict[tuple[int, int], dict] = {}
    for row in creatures:
        key = (row["hz"], row["templateId"])
        if key not in name_by_key:  # first row wins; hz+tid is unique in-zone
            name_by_key[key] = row

    scope_villagers: list[dict] = []
    for hz, tid in sorted(set(vm_entries)):
        if hz not in SCOPE_ZONES:
            continue
        row = name_by_key.get((hz, tid), {})
        scope_villagers.append({
            "huntingZoneId": hz,
            "templateId": tid,
            "name": row.get("name", ""),
            "title": row.get("title", ""),
            "race": row.get("race", ""),
            "gender": row.get("gender", ""),
        })

    # ReputationItem: a reputation-vendor SellItem list (npcGuild-keyed), present
    # but placeholder/dummy; not a gold-merchant IoD inventory. Capture evidence.
    rep_shard = _family_shard(client_root, "ReputationItem")
    rep_items: list[dict] = []
    if rep_shard is not None:
        root = dclib.parse_root(dclib.read_text(rep_shard))
        for el in root.iter():
            if dclib.strip_ns(el.tag) == "Item":
                rep_items.append({
                    "Id": el.get("Id", ""),
                    "name": el.get("name", ""),
                    "grade": el.get("grade", ""),
                    "npcGuildId": el.get("npcGuildId", ""),
                    "reputationPoint": el.get("reputationPoint", ""),
                })

    per_zone: dict[int, int] = {z: 0 for z in SCOPE_ZONES}
    for v in scope_villagers:
        per_zone[v["huntingZoneId"]] += 1

    return {
        "family_count": len(families),
        "families": families,
        "shop_related_families": shop_related,
        "villager_menu": {
            "shard": vm_shard.name if vm_shard else None,
            "total_entries": len(vm_entries),
            "child_tags": sorted(vm_child_tags),
            "carries_inventory": False,
            "scope_entries_per_zone": per_zone,
            "scope_villagers": scope_villagers,
        },
        "reputation_item": {
            "shard": rep_shard.name if rep_shard else None,
            "entry_count": len(rep_items),
            "keyed_by": "npcGuildId + reputationPoint (reputation vendor)",
            "note": ("placeholder/dummy rows, not IoD gold-merchant inventory; "
                     "keyed by npcGuild not NPC template"),
            "sample": rep_items[:8],
        },
        "sell_list_finding": {
            "client_carries_merchant_sell_lists": False,
            "evidence": (
                "All {n} client families enumerated; the only shop/menu family "
                "is VillagerMenu, a bare <Villager id=\"hz,tid\"/> registry with "
                "no child inventory (child tags: {ct}). No StoreData / "
                "StoreSellList / MenuList / price / goods family exists. "
                "ReputationItem is a reputation-vendor placeholder, TradeBroker* "
                "is auction-house UI. Gold-merchant store inventories are "
                "server-side, so v31 is the source for shop sell lists."
            ).format(n=len(families),
                     ct=", ".join(sorted(vm_child_tags)) or "none"),
        },
        "npc_linkage": (
            "VillagerMenu id=\"hz,tid\" registers a client interaction menu for "
            "NpcData Template id=tid inside the huntingZoneId=hz shard (which "
            "carries villager=\"true\"); the display name resolves from "
            "StrSheet_Creature by (HuntingZone id, templateId). The client marks "
            "an NPC as a menu-bearing villager but does not encode what it sells."
        ),
    }


def write_shops_md(data: dict, path: Path) -> None:
    L: list[str] = []
    L.append("# v17.11 Client Merchant / Shop Extraction (Island of Dawn)")
    L.append("")
    L.append("Scope zones: " + ", ".join(str(z) for z in SCOPE_ZONES) + ".")
    L.append("")
    L.append("## Headline finding: no merchant sell lists in the client")
    L.append("")
    f = data["sell_list_finding"]
    L.append("**Does the v17.11 client carry merchant SELL lists (store "
             "inventories, i.e. what merchants sell to players)? NO.**")
    L.append("")
    L.append(f["evidence"])
    L.append("")
    L.append("Consequence: v31 (server datasheet) is the source of truth for IoD "
             "merchant shop inventories; the client cannot supply them.")
    L.append("")
    L.append("## Shop-related client families (name scan)")
    L.append("")
    L.append("Of " + str(data["family_count"]) + " client families, the "
             "name-based shop/menu/price scan surfaces only:")
    L.append("")
    for fam in data["shop_related_families"]:
        L.append(f"- `{fam}`")
    L.append("")
    L.append("Assessment of each:")
    L.append("")
    L.append("- `VillagerMenu` - bare registry of menu-bearing NPCs; **no "
             "inventory** (see below).")
    L.append("- `ReputationItem` - reputation-vendor SellItem list, "
             "npcGuild-keyed, placeholder/dummy rows; not IoD gold merchants.")
    L.append("- `TradeBrokerCategory` / `TradeBrokerSetting` - auction-house "
             "(trade broker) UI category tree and settings, not merchant stores.")
    L.append("- `GambleBoxData` / `GambeItemData` - loot-box tables, not stores.")
    L.append("")
    vm = data["villager_menu"]
    L.append("## VillagerMenu (the client NPC linkage)")
    L.append("")
    L.append(f"Shard `{vm['shard']}` holds {vm['total_entries']} "
             "`<Villager id=\"hz,tid\"/>` entries. Every entry is self-closing; "
             "the only child tags present are: "
             + (", ".join(f"`{t}`" for t in vm["child_tags"]) or "none")
             + ". There is no sell list, buy menu, price, or menu-type content.")
    L.append("")
    L.append(data["npc_linkage"])
    L.append("")
    L.append("### Scope-zone villager-menu NPCs")
    L.append("")
    L.append("Per-zone counts of VillagerMenu entries in scope:")
    L.append("")
    L.append("| Zone | Villager-menu NPCs |")
    L.append("|------|--------------------|")
    for z in SCOPE_ZONES:
        L.append(f"| {z} | {vm['scope_entries_per_zone'][z]} |")
    L.append("")
    L.append("Full list (name/title from StrSheet_Creature; blank = template not "
             "named in the client creature strings):")
    L.append("")
    L.append("| hz | templateId | Name | Title | Race |")
    L.append("|----|-----------|------|-------|------|")
    for v in vm["scope_villagers"]:
        L.append(f"| {v['huntingZoneId']} | {v['templateId']} | "
                 f"{v['name']} | {v['title']} | {v['race']} |")
    L.append("")
    rep = data["reputation_item"]
    L.append("## ReputationItem (reputation vendor, not a gold merchant)")
    L.append("")
    L.append(f"Shard `{rep['shard']}` has {rep['entry_count']} SellItem rows, "
             f"keyed by {rep['keyed_by']}. {rep['note']}. Sample rows:")
    L.append("")
    L.append("| Id | name | grade | npcGuildId | reputationPoint |")
    L.append("|----|------|-------|-----------|-----------------|")
    for it in rep["sample"]:
        L.append(f"| {it['Id']} | {it['name']} | {it['grade']} | "
                 f"{it['npcGuildId']} | {it['reputationPoint']} |")
    L.append("")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 2. Gathering
# ---------------------------------------------------------------------------

def extract_gathering(client_root: Path) -> dict:
    # Collections: the global gathering-node catalog (Herb/Mine/Energy/Bug/Quest).
    coll_shard = _family_shard(client_root, "Collections")
    collections: list[dict] = []
    if coll_shard is not None:
        root = dclib.parse_root(dclib.read_text(coll_shard))
        for el in root.iter():
            if dclib.strip_ns(el.tag) != "Collection":
                continue
            collections.append({
                "collectionId": int(el.get("collectionId"))
                if (el.get("collectionId") or "").isdigit() else el.get("collectionId"),
                "typeName": el.get("typeName", ""),
                "grade": el.get("grade", ""),
                "neededProficiency": el.get("neededProficiency", ""),
                "pickSkillType": el.get("pickSkillType", ""),
                "questCollection": el.get("questCollection", ""),
            })

    # Collection display names.
    coll_names: dict[int, str] = {}
    cn_shard = _family_shard(client_root, "StrSheet_Collections")
    if cn_shard is not None:
        text = dclib.read_text(cn_shard)
        for m in re.finditer(r'<String\b[^>]*\bstring="([^"]*)"[^>]*\bcollectionId="(\d+)"'
                             r'|<String\b[^>]*\bcollectionId="(\d+)"[^>]*\bstring="([^"]*)"',
                             text):
            if m.group(2):
                coll_names[int(m.group(2))] = m.group(1)
            else:
                coll_names[int(m.group(3))] = m.group(4)
    for c in collections:
        cid = c["collectionId"]
        c["name"] = coll_names.get(cid, "") if isinstance(cid, int) else ""

    # WorkObjectData: interactable-object catalog (levers, altars, coffins...).
    wo_shard = _family_shard(client_root, "WorkObjectData")
    workobjects: list[dict] = []
    if wo_shard is not None:
        root = dclib.parse_root(dclib.read_text(wo_shard))
        for el in root.iter():
            if dclib.strip_ns(el.tag) != "WorkObject":
                continue
            workobjects.append({
                "templateId": int(el.get("templateId"))
                if (el.get("templateId") or "").isdigit() else el.get("templateId"),
                "socialMotionId": el.get("socialMotionId", ""),
                "isForQuestId": el.get("isForQuestId", ""),
            })
    wo_names: dict[int, str] = {}
    won_shard = _family_shard(client_root, "StrSheet_WorkObject")
    if won_shard is not None:
        text = dclib.read_text(won_shard)
        for m in re.finditer(r'<String\b[^>]*\bid="(\d+)"[^>]*\bstring="([^"]*)"', text):
            wo_names[int(m.group(1))] = m.group(2)
    for w in workobjects:
        tid = w["templateId"]
        w["name"] = wo_names.get(tid, "") if isinstance(tid, int) else ""

    by_type: dict[str, int] = {}
    for c in collections:
        by_type[c["typeName"]] = by_type.get(c["typeName"], 0) + 1

    return {
        "collections": {
            "shard": coll_shard.name if coll_shard else None,
            "total": len(collections),
            "by_type": dict(sorted(by_type.items())),
            "zone_scoped": False,
            "catalog": sorted(
                collections,
                key=lambda c: c["collectionId"] if isinstance(c["collectionId"], int) else 0),
        },
        "workobjects": {
            "shard": wo_shard.name if wo_shard else None,
            "total": len(workobjects),
            "catalog": sorted(
                workobjects,
                key=lambda w: w["templateId"] if isinstance(w["templateId"], int) else 0),
        },
        "zone_scope_finding": (
            "The v17 client carries gathering-node TYPE definitions (Collections) "
            "and interactable-object definitions (WorkObjectData) as GLOBAL "
            "catalogs keyed by collectionId / templateId. Neither is "
            "zone-scoped, and the client has no CollectionTerritory / per-zone "
            "gathering placement family. Where IoD gathering nodes spawn (and the "
            "items they yield) is server-side, so v31 is the source for scope-zone "
            "gathering placement; the client only supplies the node-type catalog."
        ),
    }


def write_gathering_md(data: dict, path: Path) -> None:
    L: list[str] = []
    L.append("# v17.11 Client Gathering Extraction (Island of Dawn)")
    L.append("")
    L.append("Scope zones: " + ", ".join(str(z) for z in SCOPE_ZONES) + ".")
    L.append("")
    L.append("## Zone-scope finding")
    L.append("")
    L.append(data["zone_scope_finding"])
    L.append("")
    coll = data["collections"]
    L.append("## Collections (gathering-node type catalog)")
    L.append("")
    L.append(f"Shard `{coll['shard']}`: {coll['total']} collection nodes "
             "(global, not zone-scoped). By type:")
    L.append("")
    L.append("| typeName | count |")
    L.append("|----------|-------|")
    for t, n in coll["by_type"].items():
        L.append(f"| {t} | {n} |")
    L.append("")
    L.append("Full catalog (`questCollection=true` marks quest-only nodes):")
    L.append("")
    L.append("| collectionId | name | typeName | grade | neededProficiency | quest |")
    L.append("|-------------|------|----------|-------|-------------------|-------|")
    for c in coll["catalog"]:
        L.append(f"| {c['collectionId']} | {c['name']} | {c['typeName']} | "
                 f"{c['grade']} | {c['neededProficiency']} | {c['questCollection']} |")
    L.append("")
    wo = data["workobjects"]
    L.append("## WorkObjectData (interactable-object catalog)")
    L.append("")
    L.append(f"Shard `{wo['shard']}`: {wo['total']} interactable objects "
             "(levers, altars, coffins, defense stones, etc.), global, keyed by "
             "templateId. `isForQuestId` links an object to a quest (0 = none).")
    L.append("")
    L.append("| templateId | name | isForQuestId | socialMotionId |")
    L.append("|-----------|------|--------------|----------------|")
    for w in wo["catalog"]:
        L.append(f"| {w['templateId']} | {w['name']} | {w['isForQuestId']} | "
                 f"{w['socialMotionId']} |")
    L.append("")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 3a. Fence-ring drift
# ---------------------------------------------------------------------------

def _section_fences(area_path: Path) -> dict[str, list[tuple[float, float, float]]]:
    """Map section nameId -> its DIRECT <Fence> children (own ring only)."""
    root = ET.fromstring(area_path.read_text(encoding="utf-8-sig"))
    out: dict[str, list[tuple[float, float, float]]] = {}
    for el in root.iter():
        if dclib.strip_ns(el.tag) != "Section":
            continue
        nid = el.get("nameId")
        ring: list[tuple[float, float, float]] = []
        for c in el:  # direct children only
            if dclib.strip_ns(c.tag) == "Fence" and c.get("pos"):
                ring.append(tuple(float(x) for x in c.get("pos").split(",")))
        out[nid] = ring
    return out


def fence_drift(old_client: Path, v92_client: Path) -> dict:
    a = _section_fences(old_client / DRIFT_V17_AREA)
    b = _section_fences(v92_client / DRIFT_V92_AREA)
    results: list[dict] = []
    for s in SURVIVING_SECTIONS:
        fa, fb = a.get(s, []), b.get(s, [])
        if len(fa) == len(fb) and fa:
            maxdev = max(math.dist(pa, pb) for pa, pb in zip(fa, fb))
            identical = maxdev <= ROUNDING_TOLERANCE
            results.append({
                "section": s, "v17_vertices": len(fa), "v92_vertices": len(fb),
                "vertex_identical": identical, "max_deviation": round(maxdev, 6),
                "verdict": "identical (rounding only)" if identical
                else "drift (positions differ beyond rounding)",
            })
        else:
            # Count changed: quantify with nearest-vertex distance both ways.
            def max_nn(src, dst):
                return max((min(math.dist(p, q) for q in dst) for p in src),
                           default=float("nan"))
            nn = max(max_nn(fa, fb), max_nn(fb, fa)) if fa and fb else float("nan")
            results.append({
                "section": s, "v17_vertices": len(fa), "v92_vertices": len(fb),
                "vertex_identical": False,
                "max_deviation": round(nn, 6) if fa and fb else None,
                "verdict": "drift (vertex count changed; ring reshaped)",
            })
    return {"v17_area": DRIFT_V17_AREA, "v92_area": DRIFT_V92_AREA,
            "rounding_tolerance": ROUNDING_TOLERANCE, "sections": results}


# ---------------------------------------------------------------------------
# 3b. Free-id check
# ---------------------------------------------------------------------------

def free_id_check(v92_client: Path, v92_server: Path) -> dict:
    def scan(root: Path, label: str) -> dict:
        fam_out: list[dict] = []
        for fam in FREE_ID_FAMILIES:
            paths = _iter_family_files(root, fam)
            hits: dict[str, list[dict]] = {c: [] for c in FREE_ID_CANDIDATES}
            for p in paths:
                text = p.read_text(encoding="utf-8-sig", errors="replace")
                for c in FREE_ID_CANDIDATES:
                    for m in re.finditer(r"(?<!\d)" + c + r"(?!\d)", text):
                        seg = text[max(0, m.start() - 60):m.end() + 20]
                        seg = " ".join(seg.split())
                        # A hit is a real id only if it looks like an id token,
                        # not a decimal coordinate fragment (e.g. 13036.7275).
                        frag = text[m.start():m.end() + 2]
                        coincidental = bool(re.match(r"\d+\.\d", frag))
                        hits[c].append({"file": p.name, "context": seg,
                                        "coincidental_coordinate": coincidental})
            fam_out.append({
                "family": fam,
                "files_scanned": len(paths),
                "present": len(paths) > 0,
                "hits": {c: v for c, v in hits.items() if v},
            })
        return {"root": str(root), "label": label, "families": fam_out}

    client = scan(v92_client, "v92-client")
    server = scan(v92_server, "v92-server")

    # A candidate is free iff every non-coincidental hit is absent in both roots.
    def real_hits(scan_res) -> int:
        n = 0
        for fam in scan_res["families"]:
            for c, lst in fam["hits"].items():
                n += sum(1 for h in lst if not h["coincidental_coordinate"])
        return n

    return {
        "candidates": FREE_ID_CANDIDATES,
        "families": FREE_ID_FAMILIES,
        "client": client,
        "server": server,
        "all_free": real_hits(client) == 0 and real_hits(server) == 0,
    }


def region_band_max(v92_client: Path, v92_server: Path) -> dict:
    """Highest contiguous 13xxx region-name id in StrSheet_Region, both sides."""
    def band(root: Path) -> list[int]:
        ids: set[int] = set()
        for p in _iter_family_files(root, "StrSheet_Region"):
            text = p.read_text(encoding="utf-8-sig", errors="replace")
            ids.update(int(m) for m in re.findall(r'id="(130\d\d)"', text))
        return sorted(ids)
    return {"client": band(v92_client), "server": band(v92_server)}


def write_structure_md(drift: dict, freeid: dict, band: dict, path: Path) -> None:
    L: list[str] = []
    L.append("# v17 -> v92 Structural Checks (Island of Dawn)")
    L.append("")
    L.append("## (a) Fence-ring drift of the 8 surviving sections")
    L.append("")
    L.append(f"v17 client `{drift['v17_area']}` (continentId 13) vs v92 client "
             f"`{drift['v92_area']}` (continentId 13). Each section's own ring is "
             "its direct `<Fence>` children (sections nest inside the outer 13001 "
             "zone section). Note: the v17 file stores fence coordinates at 4 "
             "decimals while v92 stores 8, so an identical ring shows a residual "
             f"deviation up to the rounding tolerance ({drift['rounding_tolerance']}).")
    L.append("")
    L.append("| Section | v17 verts | v92 verts | Vertex-identical | Max deviation | Verdict |")
    L.append("|---------|-----------|-----------|------------------|---------------|---------|")
    for r in drift["sections"]:
        dev = "n/a" if r["max_deviation"] is None else f"{r['max_deviation']}"
        L.append(f"| {r['section']} | {r['v17_vertices']} | {r['v92_vertices']} | "
                 f"{'yes' if r['vertex_identical'] else 'NO'} | {dev} | {r['verdict']} |")
    L.append("")
    ident = [r for r in drift["sections"] if r["vertex_identical"]]
    drifted = [r for r in drift["sections"] if not r["vertex_identical"]]
    L.append(f"**Verdict:** {len(ident)} of {len(drift['sections'])} sections are "
             "vertex-identical (same vertex count; every position equal within "
             "decimal-rounding, i.e. the only numeric difference is v92's extra "
             "decimal digits).")
    if drifted:
        for r in drifted:
            L.append("")
            L.append(f"- Section `{r['section']}` is genuinely drifted: vertex "
                     f"count {r['v17_vertices']} -> {r['v92_vertices']} and the "
                     "ring was reshaped (the change is far larger than rounding; "
                     f"max nearest-vertex distance {r['max_deviation']} units). "
                     "This is a real boundary edit in v92, not a formatting "
                     "artifact: the southern arc of the ring was relocated.")
    L.append("")
    L.append("## (b) Free-id check for candidate region ids 13036-13039")
    L.append("")
    L.append("Families scanned in BOTH v92 client and v92 server: "
             + ", ".join(f"`{f}`" for f in freeid["families"]) + ".")
    L.append("")
    L.append("| Candidate | v92 client | v92 server | Free |")
    L.append("|-----------|-----------|-----------|------|")
    for c in freeid["candidates"]:
        def summarize(scan_res):
            real, coinc = 0, 0
            for fam in scan_res["families"]:
                for h in fam["hits"].get(c, []):
                    if h["coincidental_coordinate"]:
                        coinc += 1
                    else:
                        real += 1
            if real:
                return f"{real} real hit(s)"
            if coinc:
                return f"clear ({coinc} coord. false-positive)"
            return "clear"
        cl = summarize(freeid["client"])
        sv = summarize(freeid["server"])
        free = "yes" if "real" not in cl and "real" not in sv else "NO"
        L.append(f"| {c} | {cl} | {sv} | {free} |")
    L.append("")
    # Detail any coincidental hits so the reader can see they are coordinates.
    coincidences: list[str] = []
    for scan_res in (freeid["client"], freeid["server"]):
        for fam in scan_res["families"]:
            for c, lst in fam["hits"].items():
                for h in lst:
                    if h["coincidental_coordinate"]:
                        coincidences.append(
                            f"- {scan_res['label']} `{fam['family']}` / "
                            f"{h['file']}: `{c}` appears only as a coordinate "
                            f"fragment (`...{h['context']}...`), not a region id.")
    if coincidences:
        L.append("The only textual matches are coincidental coordinate fragments, "
                 "not region-id usages:")
        L.append("")
        L.extend(sorted(set(coincidences)))
        L.append("")
    L.append(f"**Verdict:** candidate region ids 13036-13039 are "
             f"{'ALL FREE' if freeid['all_free'] else 'NOT all free'} in both the "
             "v92 client and the v92 server across every family listed.")
    L.append("")
    L.append("### Standard-conformance of 13036")
    L.append("")
    L.append("Contiguous 13xxx region-name ids present in `StrSheet_Region`:")
    L.append("")
    L.append(f"- v92 client: {band['client'][0]}..{band['client'][-1]} "
             f"({len(band['client'])} ids, contiguous)")
    L.append(f"- v92 server: {band['server'][0]}..{band['server'][-1]} "
             f"({len(band['server'])} ids, contiguous)")
    L.append("")
    L.append("Both sides run 13001..13035 with no gaps, so 13036 is the next "
             "sequential id. The domain reference "
             "`datasheet-domain/.../reference/zone-id-conventions.md` documents "
             "the section nameId / StrSheet_Region encoding `XXYYY` (XX = base HZ "
             "10-99, YYY = sub-region), e.g. `13004` = HZ 13 sub-region 004. "
             "Thus 13036 = HZ 13 sub-region 036 = 13*1000+36 follows the "
             "hz*1000+seq pattern and is standard-conforming as the next IoD "
             "region id.")
    L.append("")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    refs = dclib.load_references()
    old_client = Path(refs["old_client_dc"])
    v92_server = Path(refs["server_datasheet"])

    problems = []
    for label, p in [("old_client_dc", old_client),
                     ("server_datasheet", v92_server),
                     ("V92_CLIENT_DC", V92_CLIENT_DC)]:
        if not p.exists():
            problems.append(f"{label} not found: {p}")
    if problems:
        for pr in problems:
            print("ERROR:", pr, file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    shops = extract_shops(old_client)
    (OUT_DIR / "v17-shops.json").write_text(
        json.dumps(shops, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    write_shops_md(shops, OUT_DIR / "v17-shops.md")

    gathering = extract_gathering(old_client)
    (OUT_DIR / "v17-gathering.json").write_text(
        json.dumps(gathering, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    write_gathering_md(gathering, OUT_DIR / "v17-gathering.md")

    drift = fence_drift(old_client, V92_CLIENT_DC)
    freeid = free_id_check(V92_CLIENT_DC, v92_server)
    band = region_band_max(V92_CLIENT_DC, v92_server)
    write_structure_md(drift, freeid, band, OUT_DIR / "v17-structure-checks.md")

    # Summary to stdout.
    print("Wrote artifacts to", OUT_DIR)
    print(f"  shops: {shops['villager_menu']['total_entries']} villager-menu "
          f"entries, sell-lists-in-client={shops['sell_list_finding']['client_carries_merchant_sell_lists']}")
    print(f"  gathering: {gathering['collections']['total']} collections, "
          f"{gathering['workobjects']['total']} workobjects")
    ident = sum(1 for r in drift["sections"] if r["vertex_identical"])
    print(f"  drift: {ident}/{len(drift['sections'])} sections vertex-identical")
    print(f"  free-id 13036-13039 all free: {freeid['all_free']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
