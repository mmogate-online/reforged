#!/usr/bin/env python
"""extract_v31_econ.py - Phase 2a v31 economy / dialog extraction (Island of Dawn).

Read-only extractor for the IoD alpha content loop. Pulls five server-side axes
from the v31.04 server datasheet, filtered to the v17.11 registry produced in
Phase 1, and writes a json + md pair per axis into the plan data directory:

  1. shops     - merchant sell lists per rostered menu NPC (VillagerMenu ->
                 BuyMenuList tabs -> BuyList items), names via StrSheet_Item.
  2. loot      - mob compensation drop/gold bags for the scope zones, filtered
                 to the v17 mob roster.
  3. gathering - per-zone gathering/collection placement, cross-checked against
                 the v17 node-type catalog.
  4. dialogs   - villager SpeechCondition presence + structure per rostered
                 villager (the .condition files keyed HHHH0000TTTTTT).
  5. furniture - BonfireData campfires and WorkObjectTerritory work-objects.

Discovered v31 file families (the DSL surface the restore will need):
  shops:     VillagerData/VillagerMenu.xml, BuyMenuList.xml, BuyList.xml,
             VillagerData/VillagerMenuItem.xml, StrSheet_Item.xml
  loot:      CompensationData/CCompensation_00<zone>.xml (item bags),
             CompensationData/ECompensation_<zone>.xml (gold bags)
  gathering: CollectionData/CollectionTerritory_<zone>_*_P.xml
  dialogs:   VillagerData/<HHHH0000TTTTTT>.condition (SpeechCondition)
  furniture: BonfireData_<zone>.xml, WorkObjectTerritory_<zone>.xml

Every read comes from the v31 source resolved from reforged/.references; nothing
is written outside the plan data directory. Python only, absolute paths.
"""

import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dclib  # noqa: E402  (UTF-8 stdout setup + shared helpers)

SCOPE_ZONES = [13, 64, 213, 313, 364, 436]
DATA_DIR = dclib.reforged_dir() / "docs" / "plans" / "iod-alpha-content-loop" / "data"


# ---------------------------------------------------------------------------
# Shared indexes
# ---------------------------------------------------------------------------

def load_item_names(v31: Path) -> dict[int, str]:
    """Map itemTemplateId -> English name from StrSheet_Item.xml."""
    path = dclib.find_file_ci(v31, "StrSheet_Item.xml")
    out: dict[int, str] = {}
    if path is None:
        return out
    text = dclib.read_text(path)
    for m in re.finditer(r'<String\b[^>]*\bid="(\d+)"[^>]*\bstring="([^"]*)"', text):
        out[int(m.group(1))] = m.group(2)
    return out


def _load_json(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. Shops
# ---------------------------------------------------------------------------

def parse_villager_menu(v31: Path) -> dict[tuple[int, int], list[tuple[str, str]]]:
    """Map (hz, tid) -> list of (menuType, menuId) from VillagerMenu.xml."""
    path = v31 / "VillagerData" / "VillagerMenu.xml"
    text = dclib.read_text(path)
    out: dict[tuple[int, int], list[tuple[str, str]]] = {}
    # Blocks with children.
    for m in re.finditer(r'<Villager id="(\d+),(\d+)">(.*?)</Villager>', text, re.S):
        key = (int(m.group(1)), int(m.group(2)))
        menus = re.findall(r'<Menu type="(\w+)" id="(\d+)"', m.group(3))
        out[key] = menus
    # Self-closing (no menus).
    for m in re.finditer(r'<Villager id="(\d+),(\d+)"\s*/>', text):
        out.setdefault((int(m.group(1)), int(m.group(2))), [])
    return out


def parse_buy_menus(v31: Path) -> dict[str, dict]:
    """Map menuId -> {desc, stringId, tabs:[ItemList id ...]} from BuyMenuList.xml."""
    path = dclib.find_file_ci(v31, "BuyMenuList.xml")
    text = dclib.read_text(path)
    out: dict[str, dict] = {}
    for m in re.finditer(r'<Menu\b([^>]*)>(.*?)</Menu>', text, re.S):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        mid = attrs.get("id")
        if mid is None:
            continue
        tabs = re.findall(r'<ItemList\b[^>]*\bid="(\d+)"', m.group(2))
        out[mid] = {"desc": attrs.get("desc", ""), "stringId": attrs.get("stringId", ""),
                    "tabs": tabs}
    return out


def parse_buy_lists(v31: Path) -> dict[str, list[tuple[str, str]]]:
    """Map listId -> [(itemId, priceRevision) ...] from BuyList.xml."""
    path = dclib.find_file_ci(v31, "BuyList.xml")
    text = dclib.read_text(path)
    out: dict[str, list[tuple[str, str]]] = {}
    for m in re.finditer(r'<List\b[^>]*\bid="(\d+)"[^>]*>(.*?)</List>', text, re.S):
        items = []
        for im in re.finditer(r'<Item\b([^>]*)/?>', m.group(2)):
            a = dict(re.findall(r'(\w+)="([^"]*)"', im.group(1)))
            if "itemId" in a:
                items.append((a["itemId"], a.get("priceRevision", "")))
        out[m.group(1)] = items
    return out


# Out-of-registry scope stores are auto-discovered below; these labels are
# cosmetic annotations so the extras block reads clearly (the NPC names are not
# recoverable from the v17 registry, which by definition excludes them).
EXTRA_STORE_LABELS: dict[tuple[int, int], dict[str, str]] = {
    (213, 1054): {"name": "Sandom", "title": "Merchant (out of v17 registry)"},
    (64, 8000): {"name": "Ellonia", "title": "Medal Store (out of v17 registry)"},
}


def _store_record(hz: int, tid: int, meta: dict, menu_type: str, store_id: str,
                  buymenus: dict, buylists: dict, item_names: dict[int, str]) -> dict:
    """Fully expand one store menu into a (hz, tid)-keyed record.

    store_id is the BuyMenuList menu id; tabs are its ItemList ids; items carry
    the resolved name, priceRevision, and the owning tab so a per-store inventory
    diff needs no re-join.
    """
    bm = buymenus[store_id]
    tabs: list[dict] = []
    items: list[dict] = []
    for tab_id in bm["tabs"]:
        rows = buylists.get(tab_id, [])
        tid_i = int(tab_id) if tab_id.isdigit() else tab_id
        tabs.append({"tab": tid_i, "n_items": len(rows)})
        for iid, rev in rows:
            iid_i = int(iid) if iid.isdigit() else iid
            items.append({"itemId": iid_i, "name": item_names.get(iid_i, ""),
                          "priceRevision": rev, "tab": tid_i})
    return {
        "hz": hz, "tid": tid,
        "name": meta.get("name", ""), "title": meta.get("title", ""),
        "race": meta.get("race", ""),
        "menu_type": menu_type,
        "store_id": int(store_id) if store_id.isdigit() else store_id,
        "desc": bm["desc"], "n_items": len(items),
        "tabs": tabs, "items": items,
    }


def extract_shops(v31: Path, item_names: dict[int, str]) -> dict:
    roster = _load_json("v17-shops.json")["villager_menu"]["scope_villagers"]
    roster_meta = {(v["huntingZoneId"], v["templateId"]): v for v in roster}
    vmenu = parse_villager_menu(v31)
    buymenus = parse_buy_menus(v31)
    buylists = parse_buy_lists(v31)

    stores: list[dict] = []
    service_npcs: list[dict] = []
    not_in_villagermenu: list[dict] = []

    # Every v17-registry menu-bearing NPC: a real store expands to one store
    # record per store menu; everything else is an explicitly marked service NPC.
    for v in roster:
        hz, tid = v["huntingZoneId"], v["templateId"]
        menus = vmenu.get((hz, tid))
        if menus is None:
            not_in_villagermenu.append({"hz": hz, "tid": tid, "name": v.get("name", ""),
                                        "title": v.get("title", "")})
            continue
        store_menus = [(mt, mid) for mt, mid in menus if mid in buymenus]
        if store_menus:
            for mtype, mid in store_menus:
                stores.append(_store_record(hz, tid, v, mtype, mid, buymenus, buylists, item_names))
        else:
            service_npcs.append({
                "hz": hz, "tid": tid, "name": v.get("name", ""),
                "title": v.get("title", ""), "race": v.get("race", ""),
                "menu_types": sorted({mt for mt, _ in menus}),
                "menus": [{"type": mt, "menuId": int(mid) if mid.isdigit() else mid}
                          for mt, mid in menus],
            })

    # Out-of-registry real stores in the scope zones: stores whose menu-bearing
    # NPC is absent from the v17 registry. Held separate so they never enter the
    # in-registry store diff.
    extras: list[dict] = []
    for (hz, tid), menus in sorted(vmenu.items()):
        if hz not in SCOPE_ZONES or (hz, tid) in roster_meta:
            continue
        for mtype, mid in menus:
            if mid not in buymenus:
                continue
            meta = dict(EXTRA_STORE_LABELS.get((hz, tid), {}))
            rec = _store_record(hz, tid, meta, mtype, mid, buymenus, buylists, item_names)
            rec["registry"] = False
            extras.append(rec)

    stores.sort(key=lambda r: (r["hz"], r["tid"], r["store_id"]))
    service_npcs.sort(key=lambda r: (r["hz"], r["tid"]))
    extras.sort(key=lambda r: (r["hz"], r["tid"], r["store_id"]))

    return {
        "scope_zones": SCOPE_ZONES,
        "source_families": ["VillagerData/VillagerMenu.xml", "BuyMenuList.xml",
                            "BuyList.xml", "StrSheet_Item.xml"],
        "price_note": ("BuyList items carry itemId + priceRevision only; the gold "
                       "price is the item base price selected by priceRevision "
                       "server-side and is not encoded in the store files."),
        "summary": {
            "registry_villagers": len(roster),
            "real_stores": len(stores),
            "service_only_npcs": len(service_npcs),
            "not_in_villagermenu": len(not_in_villagermenu),
            "extras_stores": len(extras),
        },
        "stores": stores,
        "service_npcs": service_npcs,
        "extras": {
            "note": ("Real v31 stores whose menu-bearing NPC is absent from the v17 "
                     "registry; kept out of the in-registry store set so they never "
                     "enter the registry store diff."),
            "stores": extras,
        },
        "gaps": {"not_in_villagermenu": not_in_villagermenu},
    }


# ---------------------------------------------------------------------------
# 2. Loot (mob compensation)
# ---------------------------------------------------------------------------

def parse_c_compensation(text: str, item_names: dict[int, str]) -> dict[int, dict]:
    """npcTemplateId -> {name, bags:[{probability, items:[...]}]} from a C file."""
    root = ET.fromstring(text.encode("utf-8"))
    out: dict[int, dict] = {}
    for comp in root.iter():
        if dclib.strip_ns(comp.tag) != "Compensation":
            continue
        tid = comp.get("npcTemplateId", "")
        if not tid.isdigit():
            continue
        bags = []
        for bag in comp:
            if dclib.strip_ns(bag.tag) != "ItemBag":
                continue
            items = []
            for it in bag:
                if dclib.strip_ns(it.tag) != "Item":
                    continue
                iid = it.get("templateId", "")
                iid_i = int(iid) if iid.isdigit() else iid
                items.append({
                    "templateId": iid_i,
                    "name": item_names.get(iid_i, ""),
                    "name_kr": it.get("name", ""),
                    "min": it.get("min", ""), "max": it.get("max", ""),
                    "probability": it.get("probability", ""),
                })
            bags.append({"probability": bag.get("probability", ""), "items": items})
        out[int(tid)] = {"npcName": comp.get("npcName", ""), "bags": bags}
    return out


def parse_e_compensation(text: str) -> dict[int, dict]:
    """npcTemplateId -> {name, gold:{...}} from an E (gold) compensation file."""
    root = ET.fromstring(text.encode("utf-8"))
    out: dict[int, dict] = {}
    for comp in root.iter():
        if dclib.strip_ns(comp.tag) != "Compensation":
            continue
        tid = comp.get("npcTemplateId", "")
        if not tid.isdigit():
            continue
        gold = None
        for bag in comp:
            if dclib.strip_ns(bag.tag) == "GoldBag":
                gold = {"probability": bag.get("probability", ""),
                        "min": bag.get("min", ""), "max": bag.get("max", ""),
                        "wValue": bag.get("wValue", "")}
                break
        out[int(tid)] = {"npcName": comp.get("npcName", ""), "gold": gold}
    return out


def extract_loot(v31: Path, item_names: dict[int, str]) -> dict:
    npcs = _load_json("v17-npcs.json")["zones"]
    comp_dir = v31 / "CompensationData"
    zones: dict[str, dict] = {}
    for z in SCOPE_ZONES:
        roster = {n["templateId"]: n for n in npcs.get(str(z), {}).get("npcs", [])}
        c_path = dclib.find_file_ci(comp_dir, f"CCompensation_{z:04d}.xml")
        e_path = dclib.find_file_ci(comp_dir, f"ECompensation_{z}.xml")
        if c_path is None and e_path is None:
            continue
        c_data = parse_c_compensation(dclib.read_text(c_path), item_names) if c_path else {}
        e_data = parse_e_compensation(dclib.read_text(e_path)) if e_path else {}
        all_tids = sorted(set(c_data) | set(e_data))
        mobs = []
        filtered_out = []
        for tid in all_tids:
            in_v17 = tid in roster
            rec = {
                "templateId": tid,
                "v17Name": roster.get(tid, {}).get("name", ""),
                "compName_kr": (c_data.get(tid) or e_data.get(tid) or {}).get("npcName", ""),
                "in_v17_roster": in_v17,
                "dropBags": c_data.get(tid, {}).get("bags", []),
                "goldBag": e_data.get(tid, {}).get("gold"),
            }
            if in_v17:
                mobs.append(rec)
            else:
                filtered_out.append({"templateId": tid, "compName_kr": rec["compName_kr"]})
        zones[str(z)] = {
            "c_file": c_path.name if c_path else None,
            "e_file": e_path.name if e_path else None,
            "v17_roster_size": len(roster),
            "mobs_with_loot_in_v17": len(mobs),
            "filtered_out_count": len(filtered_out),
            "mobs": mobs,
            "filtered_out": filtered_out,
        }
    return {"scope_zones": SCOPE_ZONES,
            "note": ("Only zone 13 carries mob compensation in scope; the other "
                     "scope zones are hub/outpost villages with no C/E/I "
                     "compensation files."),
            "zones": zones}


# ---------------------------------------------------------------------------
# 3. Gathering (collection placement)
# ---------------------------------------------------------------------------

def extract_gathering(v31: Path) -> dict:
    catalog = _load_json("v17-gathering.json")
    known_ids: set[int] = set()
    for row in catalog.get("collections", {}).get("catalog", []) if isinstance(
            catalog.get("collections"), dict) else []:
        pass  # replaced below once structure known
    # Robustly harvest every collectionId mentioned in the catalog json.
    known_ids = set(re.findall(r'"collectionId":\s*(\d+)', json.dumps(catalog)))
    known_ids = {int(x) for x in known_ids}

    coll_dir = v31 / "CollectionData"
    zones: dict[str, dict] = {}
    for z in SCOPE_ZONES:
        files = []
        if coll_dir.is_dir():
            for entry in coll_dir.iterdir():
                if re.match(rf'CollectionTerritory_{z}_.*\.xml$', entry.name, re.I):
                    files.append(entry)
        if not files:
            continue
        z_terrs = []
        z_flags = []
        for path in sorted(files):
            root = ET.fromstring(dclib.read_text(path).encode("utf-8"))
            cont = root.get("continentId", "")
            area = root.get("areaName", "")
            for terr in root.iter():
                if dclib.strip_ns(terr.tag) != "Territory":
                    continue
                colls = []
                for coll in terr:
                    if dclib.strip_ns(coll.tag) != "Collections":
                        continue
                    type_id = coll.get("typeId", "")
                    type_i = int(type_id) if type_id.isdigit() else None
                    spawns = sum(1 for c in coll if dclib.strip_ns(c.tag) == "Spawn")
                    in_cat = type_i in known_ids if type_i is not None else False
                    colls.append({
                        "collectionsId": coll.get("id", ""),
                        "typeId": type_i,
                        "in_v17_catalog": in_cat,
                        "giftNum": coll.get("giftNum", ""),
                        "spawnNum": coll.get("spawnNum", ""),
                        "respawnTime": coll.get("respawnTime", ""),
                        "placedSpawns": spawns,
                    })
                    if not in_cat:
                        z_flags.append({"file": path.name, "typeId": type_i,
                                        "collectionsId": coll.get("id", "")})
                z_terrs.append({
                    "file": path.name, "continentId": cont, "areaName": area,
                    "territoryId": terr.get("id", ""), "desc": terr.get("desc", ""),
                    "collections": colls,
                })
        zones[str(z)] = {
            "files": [p.name for p in sorted(files)],
            "territories": z_terrs,
            "typeIds_absent_from_v17_catalog": z_flags,
        }
    return {"scope_zones": SCOPE_ZONES,
            "note": ("Only zone 13 carries per-zone gathering placement in scope; "
                     "the other scope zones have no CollectionTerritory file."),
            "zones": zones}


# ---------------------------------------------------------------------------
# 4. Villager dialogs (SpeechCondition)
# ---------------------------------------------------------------------------

def parse_speech_condition(text: str) -> dict:
    root = ET.fromstring(text.encode("utf-8"))
    villager = None
    normal_texts = []
    popup_texts = []
    for el in root.iter():
        tag = dclib.strip_ns(el.tag)
        if tag == "Villager":
            villager = {"huntingZoneId": el.get("huntingZoneId", ""),
                        "id": el.get("id", ""), "note": el.get("note", "")}
    # Section-scoped text collection.
    for section in root:
        stag = dclib.strip_ns(section.tag)
        if stag not in ("Normal", "Popup"):
            continue
        rows = []
        for txt in section:
            if dclib.strip_ns(txt.tag) != "Text":
                continue
            params = [p.get("type", "") for p in txt if dclib.strip_ns(p.tag) == "Param"]
            rows.append({"id": txt.get("id", ""), "params": params})
        if stag == "Normal":
            normal_texts = rows
        else:
            popup_texts = rows
    return {"villager": villager, "normal_texts": normal_texts,
            "popup_texts": popup_texts}


def extract_dialogs(v31: Path) -> dict:
    npcs = _load_json("v17-npcs.json")["zones"]
    vd = v31 / "VillagerData"
    zones: dict[str, dict] = {}
    for z in SCOPE_ZONES:
        roster = [n for n in npcs.get(str(z), {}).get("npcs", [])
                  if n.get("villager")]
        present = []
        missing = []
        for n in roster:
            tid = n["templateId"]
            fname = f"{z:04d}0000{tid:06d}.condition"
            path = dclib.find_file_ci(vd, fname)
            if path is None:
                missing.append({"templateId": tid, "name": n.get("name", ""),
                                "title": n.get("title", "")})
                continue
            parsed = parse_speech_condition(dclib.read_text(path))
            present.append({
                "templateId": tid, "name": n.get("name", ""),
                "title": n.get("title", ""), "file": fname,
                "note": (parsed["villager"] or {}).get("note", ""),
                "normal_text_count": len(parsed["normal_texts"]),
                "popup_text_count": len(parsed["popup_texts"]),
                "detail": parsed,
            })
        zones[str(z)] = {
            "villager_roster_size": len(roster),
            "with_dialog": len(present),
            "without_dialog": len(missing),
            "present": present,
            "missing": missing,
        }
    return {"scope_zones": SCOPE_ZONES,
            "note": ("Villager dialogs are .condition SpeechCondition files keyed "
                     "HHHH0000TTTTTT (huntingZone + templateId). The condition file "
                     "defines which Normal/Popup text slots fire; the localized text "
                     "resolves from client string sheets, not the server file."),
            "zones": zones}


# ---------------------------------------------------------------------------
# 5. Furniture (bonfires + work objects)
# ---------------------------------------------------------------------------

def extract_furniture(v31: Path) -> dict:
    zones: dict[str, dict] = {}
    for z in SCOPE_ZONES:
        bonfires = []
        bf_path = dclib.find_file_ci(v31, f"BonfireData_{z}.xml")
        if bf_path is not None:
            root = ET.fromstring(dclib.read_text(bf_path).encode("utf-8"))
            for bf in root.iter():
                if dclib.strip_ns(bf.tag) != "Bonfire":
                    continue
                bonfires.append({"id": bf.get("id", ""), "desc": bf.get("desc", ""),
                                 "loc": bf.get("loc", "")})
        work_objects = []
        wo_path = dclib.find_file_ci(v31, f"WorkObjectTerritory_{z}.xml")
        wo_present = wo_path is not None
        if wo_path is not None:
            root = ET.fromstring(dclib.read_text(wo_path).encode("utf-8"))
            for wo in root.iter():
                tag = dclib.strip_ns(wo.tag)
                if tag in ("WorkObject", "Object", "Npc", "WorkObjectData"):
                    work_objects.append(dict(wo.attrib))
        if bf_path is None and wo_path is None:
            continue
        zones[str(z)] = {
            "bonfire_file": bf_path.name if bf_path else None,
            "bonfire_count": len(bonfires),
            "bonfires": bonfires,
            "workobject_file": wo_path.name if wo_present else None,
            "workobject_count": len(work_objects),
            "work_objects": work_objects,
        }
    return {"scope_zones": SCOPE_ZONES, "zones": zones}


# ---------------------------------------------------------------------------
# Markdown renderers
# ---------------------------------------------------------------------------

def _w(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def _md_store_block(L: list[str], s: dict) -> None:
    head = (f"### {s['name'] or '(unnamed)'}"
            + (f" ({s['title']})" if s['title'] else "")
            + f" - {s['hz']},{s['tid']}")
    L += [head, "",
          f"Store menu `{s['menu_type']}` store_id={s['store_id']} "
          f"({s['n_items']} items) - {s.get('desc','')}", "",
          "| Tab | Items |", "|-----|-------|"]
    for tab in s["tabs"]:
        names = ", ".join(f"{it['itemId']} {it['name']}".strip()
                          for it in s["items"] if it["tab"] == tab["tab"]) or "(empty)"
        L.append(f"| {tab['tab']} ({tab['n_items']}) | {names} |")
    L.append("")


def md_shops(d: dict) -> str:
    sm = d["summary"]
    L = ["# v31 Shop Inventories (Island of Dawn)", "",
         "Scope zones: " + ", ".join(map(str, d["scope_zones"])) + ".", "",
         "Source families: " + ", ".join(d["source_families"]) + ".", "",
         "Price note: " + d["price_note"], "",
         f"Registry villagers: {sm['registry_villagers']} "
         f"({sm['real_stores']} real stores, {sm['service_only_npcs']} service-only, "
         f"{sm['not_in_villagermenu']} not in VillagerMenu). "
         f"Out-of-registry extras: {sm['extras_stores']}.", "",
         "## Real stores (v17-registry NPCs)", ""]
    for s in d["stores"]:
        _md_store_block(L, s)

    L += ["## Service-only NPCs (registry, no gold inventory)", "",
          "| hz,tid | Name | Title | Menu types |", "|--------|------|-------|------------|"]
    for n in d["service_npcs"]:
        L.append(f"| {n['hz']},{n['tid']} | {n['name']} | {n['title']} | "
                 f"{', '.join(n['menu_types'])} |")
    L.append("")

    ex = d["extras"]
    L += ["## Out-of-registry stores (extras)", "", ex["note"], ""]
    for s in ex["stores"]:
        _md_store_block(L, s)

    g = d["gaps"]
    if g["not_in_villagermenu"]:
        L += ["## Registry NPCs absent from VillagerMenu", "",
              "| hz,tid | Name | Title |", "|--------|------|-------|"]
        for x in g["not_in_villagermenu"]:
            L.append(f"| {x['hz']},{x['tid']} | {x['name']} | {x['title']} |")
        L.append("")
    return _w(L)


def md_loot(d: dict) -> str:
    L = ["# v31 Mob Loot (Island of Dawn)", "",
         "Scope zones: " + ", ".join(map(str, d["scope_zones"])) + ".", "",
         d["note"], ""]
    for z, zd in d["zones"].items():
        L += [f"## Zone {z}", "",
              f"C file: {zd['c_file']} | E file: {zd['e_file']}",
              f"v17 roster: {zd['v17_roster_size']} | mobs with loot in v17: "
              f"{zd['mobs_with_loot_in_v17']} | filtered out (comp not in v17): "
              f"{zd['filtered_out_count']}", "",
              "| tid | v17 name | drop bags | gold bag |",
              "|-----|----------|-----------|----------|"]
        for m in zd["mobs"]:
            nbags = len(m["dropBags"])
            nitems = sum(len(b["items"]) for b in m["dropBags"])
            gold = "yes" if m["goldBag"] else "-"
            L.append(f"| {m['templateId']} | {m['v17Name'] or m['compName_kr']} | "
                     f"{nbags} bags / {nitems} items | {gold} |")
        L.append("")
        if zd["filtered_out"]:
            L += [f"Filtered-out compensation templates (in v31 comp, not in v17 roster): "
                  + ", ".join(str(x["templateId"]) for x in zd["filtered_out"]), ""]
    return _w(L)


def md_gathering(d: dict) -> str:
    L = ["# v31 Gathering Placement (Island of Dawn)", "",
         "Scope zones: " + ", ".join(map(str, d["scope_zones"])) + ".", "",
         d["note"], ""]
    for z, zd in d["zones"].items():
        L += [f"## Zone {z}", "", "Files: " + ", ".join(zd["files"]), "",
              "| Territory | typeId | in v17 catalog | spawnNum | placed spawns | respawn |",
              "|-----------|--------|----------------|----------|---------------|---------|"]
        for t in zd["territories"]:
            for c in t["collections"]:
                L.append(f"| {t['territoryId']} {t['desc']} | {c['typeId']} | "
                         f"{'yes' if c['in_v17_catalog'] else 'NO'} | {c['spawnNum']} | "
                         f"{c['placedSpawns']} | {c['respawnTime']} |")
        L.append("")
        flags = zd["typeIds_absent_from_v17_catalog"]
        L += [f"typeIds absent from v17 catalog: {len(flags)}"
              + ("" if not flags else " -> " + ", ".join(str(f["typeId"]) for f in flags)), ""]
    return _w(L)


def md_dialogs(d: dict) -> str:
    L = ["# v31 Villager Dialogs (Island of Dawn)", "",
         "Scope zones: " + ", ".join(map(str, d["scope_zones"])) + ".", "",
         d["note"], ""]
    for z, zd in d["zones"].items():
        L += [f"## Zone {z}", "",
              f"Villager roster: {zd['villager_roster_size']} | with dialog: "
              f"{zd['with_dialog']} | without dialog: {zd['without_dialog']}", "",
              "| tid | Name | Title | normal texts | popup texts | note |",
              "|-----|------|-------|--------------|-------------|------|"]
        for n in zd["present"]:
            note = n["note"].replace("|", "/")
            L.append(f"| {n['templateId']} | {n['name']} | {n['title']} | "
                     f"{n['normal_text_count']} | {n['popup_text_count']} | {note} |")
        L.append("")
        if zd["missing"]:
            L += ["Villagers with no .condition dialog file: "
                  + ", ".join(f"{m['templateId']} {m['name']}".strip() for m in zd["missing"]), ""]
    return _w(L)


def md_furniture(d: dict) -> str:
    L = ["# v31 Zone Furniture (Island of Dawn)", "",
         "Scope zones: " + ", ".join(map(str, d["scope_zones"])) + ".", ""]
    for z, zd in d["zones"].items():
        L += [f"## Zone {z}", "",
              f"Bonfire file: {zd['bonfire_file']} ({zd['bonfire_count']} campfires) | "
              f"WorkObject file: {zd['workobject_file']} ({zd['workobject_count']} objects)", ""]
        if zd["bonfires"]:
            L += ["| id | desc | loc |", "|----|------|-----|"]
            for b in zd["bonfires"]:
                L.append(f"| {b['id']} | {b['desc']} | {b['loc']} |")
            L.append("")
    return _w(L)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _dump(name: str, data: dict, md: str) -> None:
    (DATA_DIR / f"{name}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (DATA_DIR / f"{name}.md").write_text(md, encoding="utf-8")
    print(f"wrote {name}.json + {name}.md")


def main() -> int:
    refs = dclib.load_references()
    v31 = Path(refs["v31_datasheet"])
    if not v31.is_dir():
        print(f"v31 datasheet not found: {v31} (network drive unmounted?)", file=sys.stderr)
        return 1

    item_names = load_item_names(v31)
    print(f"loaded {len(item_names)} item names from StrSheet_Item")

    shops = extract_shops(v31, item_names)
    _dump("v31-shops", shops, md_shops(shops))

    loot = extract_loot(v31, item_names)
    _dump("v31-loot", loot, md_loot(loot))

    gathering = extract_gathering(v31)
    _dump("v31-gathering", gathering, md_gathering(gathering))

    dialogs = extract_dialogs(v31)
    _dump("v31-dialogs", dialogs, md_dialogs(dialogs))

    furniture = extract_furniture(v31)
    _dump("v31-furniture", furniture, md_furniture(furniture))

    # Console summary.
    print("\n=== SUMMARY ===")
    ss = shops["summary"]
    print(f"shops: {ss['real_stores']} real stores, {ss['service_only_npcs']} service-only, "
          f"{ss['extras_stores']} out-of-registry extras, "
          f"{ss['not_in_villagermenu']} not-in-villagermenu")
    for z, zd in loot["zones"].items():
        print(f"loot zone {z}: {zd['mobs_with_loot_in_v17']} mobs in v17, "
              f"{zd['filtered_out_count']} filtered out")
    for z, zd in gathering["zones"].items():
        nt = sum(len(t["collections"]) for t in zd["territories"])
        print(f"gathering zone {z}: {len(zd['territories'])} territories, {nt} collection groups, "
              f"{len(zd['typeIds_absent_from_v17_catalog'])} off-catalog")
    for z, zd in dialogs["zones"].items():
        print(f"dialogs zone {z}: {zd['with_dialog']}/{zd['villager_roster_size']} villagers have dialog")
    for z, zd in furniture["zones"].items():
        print(f"furniture zone {z}: {zd['bonfire_count']} campfires, {zd['workobject_count']} work objects")
    return 0


if __name__ == "__main__":
    sys.exit(main())
