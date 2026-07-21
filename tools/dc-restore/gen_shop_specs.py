#!/usr/bin/env python
"""Stage 3 IoD shop-restoration spec generator (patch 001).

Deterministic. Re-runs byte-identical (fixed iteration order, no timestamps;
the emitted YAML is derived only from static inputs, never from the live scan).

Emits one DSL spec:

  04-iod-shops.yaml   restore 4 drifted IoD stores to v31 content, wire Ashley's
                      merchant binding, remove Sandom + Ellonia + T-cat shop
                      wiring.

Source precedence (per team-lead brief and TRACKER settled decisions 5, 14, 15,
20, 21, 22):

  * Store item lists (itemId, priceRevision, tab assignment, order) :
        data/v31-shops.json (the v17-merchant-registry-scoped v31 shop dump;
        item ids + priceRevision verified byte-equal to the raw v31 BuyList.xml).
  * Menu / tab metadata (stringId, per-tab stringed) :
        captured from the raw v31 BuyMenuList.xml and pinned in MENU_META below
        (small, stable; keeps the generator self-contained and free of any Z:
        drive dependency at generation time).
  * Menu desc (Korean internal label) :
        data/v31-shops.json store `desc` (equals the v31 BuyMenuList Menu desc).
  * Removal / rewire targets :
        TRACKER decisions 14 (Sandom), 15/22 (Ellonia), 20 (T-cat), 21 (shared
        lists), 22 (Ashley).
  * Live enumeration + blast-radius report :
        live v92 BuyMenuList.xml / BuyList.xml / VillagerMenu.xml scan. Feeds the
        printed report and header enumeration ONLY; the operations themselves are
        fully determined by the static inputs above.

TRACKER Stage-3 decisions applied here:
  21. Shared general-goods lists 1601 / 1602 are NOT restored (shared by 30+
      non-IoD merchants). Rutgar's menu still lists them as tabs, but their
      content is left at live v92. Only his unique tab 16064 is restored. Store-
      250 tab 2501 (shared with 1 sibling menu, 252) IS restored (accepted).
  20. T-cat Exchanger (64,9000) is NOT gap-filled (deliberate divergence from the
      v17 registry; medal currency 213832 does not exist on this build). No menu
      315, no lists 3000/3001/3002 are created. Its existing villager binding is
      deleted. NpcData template stays dormant; world spawn is handled in 03.
  22. Ashley (313,1002) is wired to Merchant menu 250 (restores her merchant role;
      Ainah's binding already exists). Ellonia's full binding removal stands.

Run:  python gen_shop_specs.py
"""

import io
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Paths (absolute, per project rules).
# ---------------------------------------------------------------------------
PLAN_DIR = r"D:\dev\mmogate\github\reforged-server-content\reforged\docs\plans\iod-alpha-content-loop"
V31_SHOPS = os.path.join(PLAN_DIR, "data", "v31-shops.json")
V92_DATASHEET = r"D:\dev\mmogate\tera92\server\Datasheet"

OUT = r"D:\dev\mmogate\github\reforged-server-content\reforged\specs\patches\001\04-iod-shops.yaml"

# ---------------------------------------------------------------------------
# Restore set: store_id -> emission order + label + menu metadata.
# store_id equals the v31 BuyMenuList Menu id and the villager Merchant menu id.
# ---------------------------------------------------------------------------
RESTORE_ORDER = [100, 16064, 211, 250]

STORE_LABEL = {
    100:   "Viator (64/1004) Crystal Merchant",
    16064: "Rutgar (64/1005) Merchant",
    211:   "Ailesa (64/1052) Weapon Merchant",
    250:   "Ashley (313/1002) + Ainah (364/1001) shared Specialty Store",
}

# stringId + ordered (listId, stringed) tabs, from raw v31 BuyMenuList.xml.
MENU_META = {
    100:   {"stringId": 100,   "tabs": [(1001, 10001), (1002, 10002)]},
    16064: {"stringId": 16064, "tabs": [(1601, 1601), (1602, 1602), (16064, 1604)]},
    211:   {"stringId": 211,   "tabs": [(2111, 2111), (2112, 2112)]},
    250:   {"stringId": 250,   "tabs": [(2501, 2501), (2502, 2502), (2505, 2505)]},
}

# Shared general-goods lists: restore SKIPPED (rewrite 30+ non-IoD merchants).
# The owning menu still references them as tabs; their content stays live v92.
SKIP_UPSERT_LISTS = {1601, 1602}
# Shared but small blast radius; restore KEPT (accepted, decision 21). Flagged.
SHARED_KEPT_LISTS = {2501}

# ---------------------------------------------------------------------------
# Villager rewire (restore Ashley's merchant role, decision 22).
# ---------------------------------------------------------------------------
# (hz, tid, menuType, menuId). v31/v17 Ashley carried no guideEffectId; omitted
# to match the restore source (Ainah, already present, uses 103 if parity wanted).
WIRE_VILLAGERS = [(313, 1002, "Merchant", 250)]

# ---------------------------------------------------------------------------
# Removals (shop wiring only; world-spawn removal is owned by 03-iod-spawn-
# removals.yaml, which does not touch VillagerMenu.xml -> no overlap).
# ---------------------------------------------------------------------------
# Sandom menu 16090 + its own teleport list 16090 (lists 1601/1602 are shared
# and kept). Ellonia medal menu 331 + its halloween-only lists 9149/9150/9151.
REMOVE_MENUS = [16090, 331]
REMOVE_LISTS = [16090, 9149, 9150, 9151]
# Villager bindings removed:
#   (213,1054) Sandom Merchant binding (decision 14).
#   (64,8000)  Ellonia binding (Teleport 608000 + BuyMenuMedal 1008 in live v92;
#              no longer carries MedalStore 331) removed with the NPC (dec 15/22).
#   (64,9000)  T-cat Exchanger binding (MedalStore 315) removed (decision 20).
REMOVE_VILLAGERS = [
    (213, 1054, "Sandom merchant binding"),
    (64, 8000, "Ellonia binding (Teleport 608000 + BuyMenuMedal 1008)"),
    (64, 9000, "T-cat Exchanger binding (MedalStore 315)"),
]


def die(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def load_json(path):
    return json.load(io.open(path, encoding="utf-8"))


def read_text(path):
    for enc in ("utf-8-sig", "utf-16", "utf-8", "cp949"):
        try:
            return io.open(path, encoding=enc).read()
        except (UnicodeError, UnicodeDecodeError):
            continue
    return io.open(path, encoding="utf-8", errors="replace").read()


# ---------------------------------------------------------------------------
# Static content model from v31-shops.json (dedup shared store_id 250).
# ---------------------------------------------------------------------------
def build_stores():
    data = load_json(V31_SHOPS)
    stores = {}
    for s in data["stores"]:
        sid = s["store_id"]
        if sid not in RESTORE_ORDER:
            continue  # Mahadam (MATCH), T-cat (removed), and anything else.
        tabs = {}
        for it in s["items"]:
            tabs.setdefault(it["tab"], []).append(
                (int(it["itemId"]), int(it["priceRevision"])))
        rec = {"desc": s["desc"], "tabs": tabs}
        if sid in stores and stores[sid] != rec:
            die("store_id %d has conflicting content across NPCs" % sid)
        stores[sid] = rec
    for sid in RESTORE_ORDER:
        if sid not in stores:
            die("restore store_id %d missing from v31-shops.json" % sid)
        meta_tabs = [t for t, _ in MENU_META[sid]["tabs"]]
        if sorted(stores[sid]["tabs"]) != sorted(meta_tabs):
            die("store %d tab mismatch: json=%s meta=%s"
                % (sid, sorted(stores[sid]["tabs"]), sorted(meta_tabs)))
    return stores


# ---------------------------------------------------------------------------
# Live v92 scan (report + header enumeration only; never feeds the operations).
# ---------------------------------------------------------------------------
def scan_live():
    bml = read_text(os.path.join(V92_DATASHEET, "BuyMenuList.xml"))
    bl = read_text(os.path.join(V92_DATASHEET, "BuyList.xml"))
    vm = read_text(os.path.join(V92_DATASHEET, "VillagerData", "VillagerMenu.xml"))

    menus = re.findall(r'<Menu\b[^>]*\bid="(\d+)"[^>]*>(.*?)</Menu>', bml, re.S)
    menu_ids = set(int(m) for m, _ in menus)

    def list_item_count(lid):
        m = re.search(r'<List\b[^>]*\bid="%d"[^>]*>(.*?)</List>' % lid, bl, re.S)
        if not m:
            if re.search(r'<List\b[^>]*\bid="%d"[^>]*/>' % lid, bl):
                return 0
            return None
        return len(re.findall(r'<Item\b', m.group(1)))

    def menu_refs(lid):
        return [int(mid) for mid, body in menus
                if re.search(r'<ItemList\b[^>]*\bid="%d"' % lid, body)]

    def villager(hz, tid):
        key = '"%d,%d"' % (hz, tid)
        m = re.search(r'<Villager\b[^>]*\bid=%s.*?</Villager>' % re.escape(key),
                      vm, re.S)
        if not m:
            m = re.search(r'<Villager\b[^>]*\bid=%s[^>]*/>' % re.escape(key), vm)
        if not m:
            return None
        return re.findall(r'<Menu\b[^>]*/>', m.group(0))

    return {
        "menu_ids": menu_ids,
        "list_item_count": list_item_count,
        "menu_refs": menu_refs,
        "villager": villager,
    }


# ---------------------------------------------------------------------------
# YAML rendering.
# ---------------------------------------------------------------------------
def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def emit(stores, live):
    L = []
    L.append('spec:')
    L.append('  version: "1.0"')
    L.append('  schema: v92')
    L.append('')
    L.append('# IoD patch 001 Stage 3: shop restoration (classification-economy.json,')
    L.append('# shops section) with TRACKER Stage-3 decisions 20/21/22 folded in.')
    L.append('#')
    L.append('# Sources:')
    L.append('#   item lists (itemId, priceRevision, tab, order) : data/v31-shops.json')
    L.append('#       (v17-registry-scoped v31 dump; verified byte-equal to raw v31 BuyList).')
    L.append('#   menu/tab metadata (stringId, stringed) : raw v31 BuyMenuList.xml (MENU_META).')
    L.append('#   removals/rewire : TRACKER decisions 14/15/20/21/22.')
    L.append('#')
    L.append('# Live file placement (v92 at generation time):')
    L.append('#   All IoD merchant menus (100/210/211/250) and the removal menus')
    L.append('#   (331/16090) live in the BASE BuyMenuList.xml, not a regional variant.')
    L.append('#   All ops target the base files (BuyMenuList.xml / BuyList.xml /')
    L.append('#   VillagerData/VillagerMenu.xml); no regional-variant targeting needed.')
    L.append('#')
    L.append('# Restore stores (store_id = BuyMenuList Menu id = villager Merchant menu id):')
    for sid in RESTORE_ORDER:
        emitted = [l for l, _ in MENU_META[sid]["tabs"] if l not in SKIP_UPSERT_LISTS]
        n = sum(len(stores[sid]["tabs"][l]) for l in emitted)
        L.append('#   %-6d %s' % (sid, STORE_LABEL[sid]))
        L.append('#          restored lists %s (%d items); menu lists all %d tabs'
                 % (emitted, n, len(MENU_META[sid]["tabs"])))
    L.append('#   210    Mahadam (64/1053) Armor Merchant : MATCH, intentionally untouched.')
    L.append('#')
    L.append('# Decision 21 - shared general-goods lists NOT restored:')
    for lid in sorted(SKIP_UPSERT_LISTS):
        refs = live["menu_refs"](lid)
        others = [m for m in refs if m not in RESTORE_ORDER]
        L.append('#   list %-5d shared by %d menus (%d outside IoD); content left at live v92,'
                 % (lid, len(refs), len(others)))
        L.append('#             Rutgar menu 16064 still references it as a tab.')
    for lid in sorted(SHARED_KEPT_LISTS):
        refs = live["menu_refs"](lid)
        others = [m for m in refs if m not in RESTORE_ORDER]
        L.append('#   list %-5d shared by %d menus (%d outside IoD); restore KEPT (accepted).'
                 % (lid, len(refs), len(others)))
    L.append('#')
    L.append('# Decision 20 - T-cat Exchanger (64,9000) is NOT gap-filled (deliberate')
    L.append('#   divergence from the v17 registry; medal currency 213832 absent on build).')
    L.append('#   No menu 315 / lists 3000-3002 created; its villager binding is deleted.')
    L.append('# Decision 22 - Ashley (313,1002) wired to Merchant menu 250.')
    L.append('#')
    L.append('# Removal enumeration (live v92 at generation time):')
    for mid in REMOVE_MENUS:
        L.append('#   buy menu %d : %s'
                 % (mid, "present" if mid in live["menu_ids"] else "ALREADY ABSENT"))
    for lid in REMOVE_LISTS:
        c = live["list_item_count"](lid)
        L.append('#   buy list %-5d : %s'
                 % (lid, "ALREADY ABSENT" if c is None else "present (%d items)" % c))
    for hz, tid, note in REMOVE_VILLAGERS:
        vmenus = live["villager"](hz, tid)
        L.append('#   villager (%d,%d) : %s'
                 % (hz, tid, "ALREADY ABSENT" if vmenus is None
                    else "present " + " ".join(vmenus)))
    L.append('')

    # -- buyLists --
    L.append('buyLists:')
    L.append('  upsert:')
    for sid in RESTORE_ORDER:
        L.append('    # %s' % STORE_LABEL[sid])
        any_emitted = False
        for lid, _stringed in MENU_META[sid]["tabs"]:
            if lid in SKIP_UPSERT_LISTS:
                L.append('    # list %d NOT restored (shared general-goods; left at live v92)'
                         % lid)
                continue
            any_emitted = True
            items = stores[sid]["tabs"][lid]
            tag = "   # SHARED with 1 sibling menu (restore accepted)" \
                if lid in SHARED_KEPT_LISTS else ""
            L.append('    - id: %d%s' % (lid, tag))
            L.append('      items:')
            for item_id, rev in items:
                L.append('        - itemId: %d' % item_id)
                L.append('          priceRevision: %d' % rev)
        if not any_emitted:
            L.append('    # (no unique lists to restore for this store)')
    L.append('  delete:')
    L.append('    - 16090   # Sandom teleport list (Sandom-only ref)')
    L.append('    - 9149    # Ellonia halloween accessories')
    L.append('    - 9150    # Ellonia halloween skill book')
    L.append('    - 9151    # Ellonia halloween boxes')
    L.append('')

    # -- buyMenuLists --
    L.append('buyMenuLists:')
    L.append('  upsert:')
    for sid in RESTORE_ORDER:
        meta = MENU_META[sid]
        L.append('    - id: %d' % sid)
        L.append('      stringId: %d' % meta["stringId"])
        L.append('      desc: %s' % q(stores[sid]["desc"]))
        L.append('      itemLists:')
        for lid, stringed in meta["tabs"]:
            L.append('        - id: %d' % lid)
            L.append('          stringed: %d' % stringed)
    L.append('  delete:')
    L.append('    - 16090   # Sandom store')
    L.append('    - 331     # Ellonia medal store')
    L.append('')

    # -- villagerMenus (rewire Ashley; remove Sandom / Ellonia / T-cat) --
    L.append('villagerMenus:')
    L.append('  upsert:')
    for hz, tid, mtype, mid in WIRE_VILLAGERS:
        L.append('    - huntingZoneId: %d' % hz)
        L.append('      npcTemplateId: %d   # Ashley: restore merchant role' % tid)
        L.append('      menus:')
        L.append('        - type: %s' % mtype)
        L.append('          id: %d' % mid)
    L.append('  delete:')
    for hz, tid, note in REMOVE_VILLAGERS:
        L.append('    - huntingZoneId: %d' % hz)
        L.append('      npcTemplateId: %d   # %s' % (tid, note))

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")


# ---------------------------------------------------------------------------
# Main + report.
# ---------------------------------------------------------------------------
def main():
    stores = build_stores()
    live = scan_live()
    emit(stores, live)

    print("=== 04-iod-shops.yaml ===")
    print("Wrote: " + OUT)
    print("")
    print("Restore stores (upsert menu + unique-tab lists):")
    for sid in RESTORE_ORDER:
        emitted = [l for l, _ in MENU_META[sid]["tabs"] if l not in SKIP_UPSERT_LISTS]
        skipped = [l for l, _ in MENU_META[sid]["tabs"] if l in SKIP_UPSERT_LISTS]
        n = sum(len(stores[sid]["tabs"][l]) for l in emitted)
        print("  %-6d %-55s lists_restored=%s items=%d skipped_shared=%s"
              % (sid, STORE_LABEL[sid], emitted, n, skipped or "none"))
    print("  210    Mahadam (64/1053) : MATCH, untouched (no op).")
    print("")
    print("Villager rewire (upsert):")
    for hz, tid, mtype, mid in WIRE_VILLAGERS:
        print("  (%d,%d) -> %s %d" % (hz, tid, mtype, mid))
    print("")
    print("Removal enumeration (live v92):")
    for mid in REMOVE_MENUS:
        print("  buy menu %-6d : %s"
              % (mid, "present" if mid in live["menu_ids"] else "ABSENT"))
    for lid in REMOVE_LISTS:
        c = live["list_item_count"](lid)
        print("  buy list %-6d : %s"
              % (lid, "ABSENT" if c is None else "present (%d items)" % c))
    for hz, tid, note in REMOVE_VILLAGERS:
        vmenus = live["villager"](hz, tid)
        print("  villager (%d,%d) : %s"
              % (hz, tid, "ABSENT" if vmenus is None else "present " + " ".join(vmenus)))


if __name__ == "__main__":
    main()
