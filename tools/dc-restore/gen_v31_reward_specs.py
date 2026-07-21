#!/usr/bin/env python
"""Generate the IoD patch 001 quest-reward restoration spec (v31-primary doctrine).

Source of truth is the v31 server QuestCompensationData_13.xml, ported 1:1: every
band reward row (exp / gold / itemBag / per-class item grants) is emitted verbatim.
v92's QuestCompensationData_13 is entirely empty self-closed stubs, so the whole
band reward sheet is restored from v31.

Scope: exactly the 65 IoD band quest files that exist in both v31 and v92
(quests-diff.json). v31 comp rows outside that set (1361-1368, 1380, 1381, 1388,
1342, ...) are NOT ported here.

New-class adaptation (adaptation whitelist item 2, tracker ruling 4): for the 15
class-scoped reward quests, every per-class bag is extended with rows for the
post-classic INTERNAL classes fighter, assassin, glaiver. engineer already has v31
rows; soulless (Reaper) is omitted (no base low-level gear; patch 002). Selection
is data-driven and verified against live v92 ItemTemplate:
  - Armor bags: armor is shared by type; the v31 piece already lists the
    post-classic wearer in its v92 requiredClass (mail -> FIGHTER, leather ->
    GLAIVER, robe -> ASSASSIN), so the new class receives the SAME templateId.
  - Weapon bags: the new class receives its own class weapon whose requiredLevel is
    nearest the classic weapon tier (ties resolve to the lower level). Every chosen
    id is re-verified in v92 (requiredClass + requiredLevel + EQUIP_WEAPON).

Doctrine rule 1 repair: v31 quest 1310's armor block is corrupted (its engineer
row is a stray '15019' text token instead of an <Item/>). It is restored to the
15019 body/arm/leg block's engineer row (mirroring quest 1305's identical block).

QuestCompensationData is server-only (no client sync). Zone 13 (huntingZoneId=13).
Output: specs/patches/001/04-iod-quest-rewards.yaml (idempotent upsert).
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path("D:/dev/mmogate/github/reforged-server-content/reforged")
V31_SRC = Path(
    "Z:/tera pserver/v31.04/TERAServer/Executable/Bin/Datasheet/CompensationData/QuestCompensationData_13.xml"
)
ITEM_TEMPLATE = Path("D:/dev/mmogate/tera92/server/Datasheet/ItemTemplate.xml")
OUT = REPO / "specs/patches/001/04-iod-quest-rewards.yaml"

HUNTING_ZONE = 13

# The 65 IoD band quest files present in both v31 and v92 (quests-diff.json).
BAND_QUESTS = [
    1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310,
    1311, 1312, 1313, 1315, 1316, 1317, 1318, 1319, 1321, 1322,
    1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332,
    1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1343,
    1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1371,
    1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1382, 1383,
    1384, 1385, 1386, 1389, 1390,
]

# 15 class-scoped reward quests to extend with post-classic rows (tracker ruling 4).
CLASS_SCOPED = {
    1303, 1304, 1305, 1310, 1315, 1316, 1317, 1319,
    1322, 1323, 1325, 1326, 1330, 1331, 1347,
}

# Post-classic INTERNAL classes we extend into. engineer already has v31 rows;
# soulless (Reaper) omitted.
NEW_CLASSES = ["fighter", "assassin", "glaiver"]

# Candidate weapon lines per post-classic class; re-verified against v92 below.
NEW_WEAPON_CANDIDATES = {
    "fighter": [82005, 82006, 82007, 82008],
    "assassin": [58171, 58172, 58173, 58174],
    "glaiver": [59054, 59353, 59354, 59055, 59056],
}

# Doctrine rule 1 repair for the corrupted v31 1310 engineer armor row.
REPAIRS = {1310: [(15019, 1, "engineer")]}


def load_items(needed):
    """Parse v92 ItemTemplate for the needed ids -> attribute dicts."""
    out = {}
    needed = {str(i) for i in needed}
    with open(ITEM_TEMPLATE, encoding="utf-8") as f:
        for line in f:
            m = re.match(r'\s*<Item id="(\d+)"', line)
            if not m or m.group(1) not in needed:
                continue
            a = dict(re.findall(r'(\w+)="([^"]*)"', line))
            out[int(m.group(1))] = {
                "name": a.get("name", ""),
                "cit": a.get("combatItemType", ""),
                "requiredClass": a.get("requiredClass", ""),
                "requiredLevel": int(a["requiredLevel"]) if a.get("requiredLevel", "").isdigit() else None,
            }
    return out


def is_weapon(item):
    return item.get("cit", "") == "EQUIP_WEAPON"


def is_armor(item):
    return item.get("cit", "").startswith("EQUIP_ARMOR")


def parse_v31():
    """Parse the v31 comp file into {questId: {attrs, items:[(tid,qty,class)]}}."""
    root = ET.parse(V31_SRC).getroot()
    quests = {}
    for q in root.findall("Quest"):
        qid = int(q.get("questId"))
        comp = q.find("Compensation")
        if comp is None:
            quests[qid] = None
            continue
        ct = comp.find("CompensationType")
        if ct is None:
            quests[qid] = None
            continue
        items = []
        for it in ct.findall("Item"):
            tid = int(it.get("templateId"))
            qty = int(it.get("quantity", "1"))
            cls = it.get("class")
            items.append((tid, qty, cls))
        quests[qid] = {
            "type": ct.get("type", "normal"),
            "exp": ct.get("exp"),
            "gold": ct.get("gold"),
            "itemBag": ct.get("itemBag"),
            "items": items,
        }
    return quests


def main():
    v31 = parse_v31()

    # Every band quest must be present in v31.
    missing_quests = [q for q in BAND_QUESTS if q not in v31 or v31[q] is None]
    if missing_quests:
        sys.exit(f"HARD FAIL: band quests absent/empty in v31 comp file: {missing_quests}")

    # Apply the doctrine-rule-1 repair rows before analysis.
    for qid, rows in REPAIRS.items():
        if qid in v31 and v31[qid] is not None:
            v31[qid]["items"].extend(rows)

    # Collect referenced ids (ported rows) + weapon candidates for v92 verification.
    referenced = set()
    for q in BAND_QUESTS:
        for (tid, qty, cls) in v31[q]["items"]:
            referenced.add(tid)
    for ids in NEW_WEAPON_CANDIDATES.values():
        referenced.update(ids)

    items = load_items(referenced)

    # Report ported ids missing from v92 (broken grants; kept per v31 1:1 doctrine).
    ported_ids = set()
    for q in BAND_QUESTS:
        for (tid, qty, cls) in v31[q]["items"]:
            ported_ids.add(tid)
    missing_ported = sorted(t for t in ported_ids if t not in items)

    # --- verify new-class weapon candidates against v92, index by requiredLevel ---
    weapon_pool = {}
    for cls, ids in NEW_WEAPON_CANDIDATES.items():
        pool = {}
        expected_rc = cls.upper()
        for tid in ids:
            it = items.get(tid)
            if it is None:
                sys.exit(f"HARD FAIL: weapon candidate {tid} ({cls}) not found in v92 ItemTemplate")
            if it["requiredClass"] != expected_rc:
                sys.exit(f"HARD FAIL: weapon {tid} requiredClass={it['requiredClass']!r} expected {expected_rc}")
            if it["requiredLevel"] is None:
                sys.exit(f"HARD FAIL: weapon {tid} ({cls}) has no requiredLevel in v92")
            if not is_weapon(it):
                sys.exit(f"HARD FAIL: candidate {tid} ({cls}) is not EQUIP_WEAPON (cit={it['cit']})")
            pool[it["requiredLevel"]] = tid
        weapon_pool[cls] = pool

    def pick_weapon(cls, classic_level):
        pool = weapon_pool[cls]
        best = min(pool, key=lambda lv: (abs(lv - classic_level), lv))
        return pool[best], best

    extended_quests = []
    weapon_select_log = {}
    armor_extend_log = {}

    lines = []
    lines.append("# IoD Quest Rewards - Patch 001 (v31-primary restoration)")
    lines.append("# Restores the Island of Dawn band (quest ids 1300-1399, hz 13) quest rewards.")
    lines.append("#")
    lines.append("# Provenance:")
    lines.append("#   Doctrine: docs/plans/classic-restoration/DOCTRINE.md (v31-primary; v31 ported 1:1).")
    lines.append("#   Source:   v31 server CompensationData/QuestCompensationData_13.xml")
    lines.append("#             (Z:\\tera pserver\\v31.04\\...\\Datasheet). v92's band comp rows are all")
    lines.append("#             empty self-closed stubs, so the whole band reward sheet is restored from v31.")
    lines.append("#   Diff:     docs/plans/classic-restoration/iod/data/quests-diff.md/.json (Rewards: PORT ALL 65).")
    lines.append("#   Rulings:  iod/TRACKER.md quests-diff rulings 4 (new-class rows) and 5 (class-gate deferred).")
    lines.append("#   Generator: tools/dc-restore/gen_v31_reward_specs.py (re-run to regenerate).")
    lines.append("#")
    lines.append("# Scope: exactly the 65 band quest files present in both v31 and v92. v31 comp rows")
    lines.append("#   outside that set are not ported here.")
    lines.append("#")
    lines.append("# New-class adaptation rows appended to the 15 class-scoped quests")
    lines.append("#   (1303 1304 1305 1310 1315 1316 1317 1319 1322 1323 1325 1326 1330 1331 1347),")
    lines.append("#   INTERNAL names fighter/assassin/glaiver (server QuestCompensationData namespace;")
    lines.append("#   never client CCompensation names). engineer already has v31 rows; soulless omitted.")
    lines.append("#   - Armor: same templateId as the classic piece (v92 requiredClass lists the new")
    lines.append("#     wearer: mail->FIGHTER, leather->GLAIVER, robe->ASSASSIN).")
    lines.append("#   - Weapon: own class weapon at requiredLevel nearest the classic tier (ties->lower).")
    lines.append("#")
    lines.append("# Doctrine rule 1 fix: v31 quest 1310's armor block is corrupted (engineer row is a")
    lines.append("#   stray '15019' text token); restored to the 15019 block engineer row (per quest 1305).")
    lines.append("#")
    lines.append("# Class-list encoding: v31 emits one <Item> per class, and the DSL keys comp Item")
    lines.append("#   rows by templateId+class+race (fix d79aca90, adopted 2026-07-21), so per-class")
    lines.append("#   duplicate-templateId rows survive apply. This spec mirrors the v31 source rows")
    lines.append("#   verbatim: one row per (templateId, class). Shared-by-type armor (e.g. 17703 ->")
    lines.append("#   lancer + berserker + engineer) is three rows, and each new-class append is its")
    lines.append("#   own row. Semicolon-joined class lists are no longer emitted (the previous")
    lines.append("#   workaround for the old collapse defect is removed; the writer now rejects them")
    lines.append("#   with E207).")
    lines.append("#")
    lines.append("# QuestCompensationData is server-only (no client sync).")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")
    lines.append("questCompensations:")
    lines.append("  upsert:")

    for gid in BAND_QUESTS:
        rec = v31[gid]
        emitted = list(rec["items"])  # (tid, qty, class)

        if gid in CLASS_SCOPED and rec["items"]:
            weapon_items = [(t, q, c) for (t, q, c) in rec["items"] if is_weapon(items.get(t, {}))]
            armor_items = [(t, q, c) for (t, q, c) in rec["items"] if is_armor(items.get(t, {}))]
            weapon_new = []   # (tid, qty, cls) distinct new weapon lines, appended at end
            armor_new = []    # (tid, qty, cls) same-id rows, inserted beside their piece

            # Weapon extension: one new-class weapon per new class, nearest tier.
            if weapon_items:
                levels = [items[t]["requiredLevel"] for (t, q, c) in weapon_items if items[t]["requiredLevel"] is not None]
                classic_level = max(set(levels), key=levels.count)  # mode; ties -> higher (deterministic)
                sel = {}
                for cls in NEW_CLASSES:
                    wid, chosen = pick_weapon(cls, classic_level)
                    weapon_new.append((wid, 1, cls))
                    sel[cls] = (wid, chosen, classic_level)
                weapon_select_log[gid] = sel

            # Armor extension: per distinct armor id, add new classes in its v92 requiredClass.
            seen = set()
            arows = []
            for (t, q, c) in armor_items:
                if t in seen:
                    continue
                seen.add(t)
                rc = {x for x in items[t]["requiredClass"].split(";") if x}
                for cls in NEW_CLASSES:
                    if cls.upper() in rc:
                        armor_new.append((t, q, cls))
                        arows.append((t, cls))
            if arows:
                armor_extend_log[gid] = arows

            if armor_new or weapon_new:
                extended_quests.append(gid)

            # Insert each armor new-class row immediately after the last v31 row that
            # shares its templateId, so the piece's classes stay grouped (mirroring the
            # v31 block order). Weapons are distinct new templateIds, appended last.
            for (t, q, cls) in armor_new:
                last = max(i for i, (tt, qq, cc) in enumerate(emitted) if tt == t)
                emitted.insert(last + 1, (t, q, cls))
            emitted.extend(weapon_new)

        # --- emit YAML ---
        lines.append(f"    - questId: {gid}")
        lines.append(f"      huntingZoneId: {HUNTING_ZONE}")
        lines.append("      compensations:")
        lines.append("        - compensationId: 1")
        lines.append(f'          type: "{rec["type"]}"')
        if rec["exp"] not in (None, ""):
            lines.append(f"          exp: {int(rec['exp'])}")
        if rec["gold"] not in (None, ""):
            lines.append(f"          gold: {int(rec['gold'])}")
        if rec["itemBag"] not in (None, ""):
            lines.append(f'          itemBag: "{rec["itemBag"]}"')
        # Emit one row per (templateId, class), verbatim in source/insertion order.
        # The DSL keys comp Item rows by templateId+class+race (fix d79aca90), so shared
        # template ids stay as separate per-class rows instead of a semicolon list.
        # Invariants: a templateId carries one quantity and is either classless or
        # class-filtered (never both).
        qty_by_tid = {}
        classed_tids = set()
        classless_tids = set()
        for (t, q, c) in emitted:
            if t in qty_by_tid and qty_by_tid[t] != q:
                sys.exit(f"HARD FAIL: quest {gid} templateId {t} has mixed quantities {qty_by_tid[t]} vs {q}")
            qty_by_tid[t] = q
            (classed_tids if c else classless_tids).add(t)
        both = classed_tids & classless_tids
        if both:
            sys.exit(f"HARD FAIL: quest {gid} templateIds mix classless and class rows: {sorted(both)}")

        if emitted:
            lines.append("          items:")
            for (t, q, c) in emitted:
                lines.append(f"            - templateId: {t}")
                lines.append(f"              quantity: {q}")
                if c:
                    lines.append(f'              class: "{c}"')

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- report to stderr ---
    print(f"Wrote {OUT}", file=sys.stderr)
    print(f"Band quests emitted (upsert rows): {len(BAND_QUESTS)}", file=sys.stderr)
    print(f"Extended (class-scoped) quests: {len(extended_quests)} -> {extended_quests}", file=sys.stderr)
    print("Weapon-bag new-class selection (id@rl, classic tier rl):", file=sys.stderr)
    for gid in sorted(weapon_select_log):
        sel = weapon_select_log[gid]
        parts = [f"{cls}={wid}@rl{lv}(classic rl{cl})" for cls, (wid, lv, cl) in sel.items()]
        print(f"  quest {gid}: " + ", ".join(parts), file=sys.stderr)
    print("Armor-bag new-class rows (templateId->class):", file=sys.stderr)
    for gid in sorted(armor_extend_log):
        parts = [f"{t}->{c}" for (t, c) in armor_extend_log[gid]]
        print(f"  quest {gid}: " + ", ".join(parts), file=sys.stderr)
    if missing_ported:
        print("WARNING: ported v31 item ids NOT found in v92 ItemTemplate (kept per v31 1:1; review):", file=sys.stderr)
        print(f"  {missing_ported}", file=sys.stderr)
    else:
        print("All ported v31 item ids exist in v92 ItemTemplate.", file=sys.stderr)


if __name__ == "__main__":
    main()
