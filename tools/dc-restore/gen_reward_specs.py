#!/usr/bin/env python
"""Generate the IoD patch 001 quest-reward restoration spec (Stage 3).

Reward TARGET is the v17.11 client reward display data
(docs/plans/iod-alpha-content-loop/data/classification-rewards.json, field "v17").
v31 rewards are NOT the value source (only 10/63 match); they were used upstream
only as encoding templates. This generator reads the v17 blocks verbatim for
exp / gold / items / per-class bags, then extends every per-class bag with rows
for the post-classic classes engineer, fighter, assassin, glaiver (soulless /
Reaper is omitted per settled decision 12).

New-class row selection is data-driven and verified against live v92 ItemTemplate:
  - ARMOR bags: armor is shared by type. Each classic armor piece already lists
    the post-classic wearers in its v92 requiredClass (mail -> ENGINEER;FIGHTER,
    leather -> GLAIVER, robe -> ASSASSIN). The new class simply receives the SAME
    templateId as the matching classic class. No id guessing.
  - WEAPON bags: each class has its own weapon id. The new class receives the
    weapon of its own class line whose requiredLevel is NEAREST the classic
    weapon's requiredLevel (ties resolve to the lower level). Every chosen id is
    re-verified in v92 (requiredClass + requiredLevel); a mismatch hard-fails.

Output: specs/patches/001/05-iod-quest-rewards.yaml (upsert, idempotent).
QuestCompensationData is server-only (no client sync).
"""

import json
import re
import sys
from pathlib import Path

REPO = Path("D:/dev/mmogate/github/reforged-server-content/reforged")
V17_SRC = REPO / "docs/plans/iod-alpha-content-loop/data/classification-rewards.json"
ITEM_TEMPLATE = Path("D:/dev/mmogate/tera92/server/Datasheet/ItemTemplate.xml")
OUT = REPO / "specs/patches/001/05-iod-quest-rewards.yaml"

HUNTING_ZONE = 13

# Post-classic classes we extend into (v92 internal names). Reaper/SOULLESS omitted (decision 12).
NEW_CLASSES = ["engineer", "fighter", "assassin", "glaiver"]

# Weapon lines for the post-classic classes; candidate ids come from v92 and are
# re-verified below. Nearest-requiredLevel picks the tier for each bag.
NEW_WEAPON_CANDIDATES = {
    "engineer": [55005, 55006, 55007, 55008],
    "fighter": [82005, 82006, 82007, 82008],
    "assassin": [58171, 58172, 58173, 58174],
    "glaiver": [59054, 59353, 59354, 59055, 59056],
}


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
                "category": a.get("category", ""),
                "requiredClass": a.get("requiredClass", ""),
                "requiredLevel": int(a["requiredLevel"]) if a.get("requiredLevel", "").isdigit() else None,
            }
    return out


def is_weapon(item):
    return item["cit"] == "EQUIP_WEAPON"


def is_armor(item):
    return item["cit"].startswith("EQUIP_ARMOR")


def main():
    data = json.load(open(V17_SRC, encoding="utf-8"))
    rows = data["rows"]

    # Collect every template id referenced by a v17 bag, plus weapon candidates.
    referenced = set()
    for r in rows:
        for tid, qty, cls in r["v17"]["items"]:
            referenced.add(int(tid))
    for ids in NEW_WEAPON_CANDIDATES.values():
        referenced.update(ids)

    items = load_items(referenced)

    # --- verify new-class weapon candidates against v92, index by requiredLevel ---
    weapon_pool = {}  # class -> {requiredLevel: id}
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
        """Nearest requiredLevel, ties resolve to the lower level."""
        pool = weapon_pool[cls]
        best = min(pool, key=lambda lv: (abs(lv - classic_level), lv))
        return pool[best], best

    op_created_style = 0  # counts as upsert rows emitted
    extended_quests = []
    weapon_select_log = {}   # quest -> {class: (id, chosen_level, classic_level)}
    glaiver_flag = []        # notes about missing exact glaiver level

    lines = []
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")
    lines.append("# IoD patch 001 quest rewards (Stage 3 restoration).")
    lines.append("# Reward TARGET (authoritative): v17.11 client reward display blocks in")
    lines.append("#   docs/plans/iod-alpha-content-loop/data/classification-rewards.json (field v17).")
    lines.append("# v31 rewards are NOT the value source (only 10/63 quests match); v31 was used")
    lines.append("#   upstream only as an encoding template. exp/gold/items/per-class bags below")
    lines.append("#   are the v17 values verbatim.")
    lines.append("#")
    lines.append("# Decision 6: v17.11 is the north star; v31 gap-fill only.")
    lines.append("# Decision 12: soulless (Reaper) is omitted from per-class reward bags.")
    lines.append("#")
    lines.append("# Post-classic extension: every v17 per-class bag is extended with rows for")
    lines.append("#   engineer, fighter, assassin, glaiver, verified against live v92 ItemTemplate:")
    lines.append("#   - Armor bags: armor is shared by type; the classic piece already lists the")
    lines.append("#     post-classic wearers in its v92 requiredClass (mail=engineer+fighter,")
    lines.append("#     leather=glaiver, robe=assassin), so the new class gets the SAME templateId.")
    lines.append("#   - Weapon bags: the new class gets its own class weapon whose requiredLevel is")
    lines.append("#     nearest the classic weapon's requiredLevel (ties -> lower).")
    lines.append("# Glaiver substitution: the Valkyrie glaive line has no requiredLevel-1 glaive")
    lines.append("#   (lowest is Sunstroke 59054 at requiredLevel 2); no weapon bag sits below")
    lines.append("#   requiredLevel 3, so glaiver takes exact/nearest glaives (59353/59354/59055/59056).")
    lines.append("#")
    lines.append("# QuestCompensationData is server-only (no client sync). Zone 13 (huntingZoneId=13).")
    lines.append("# Generated by tools/dc-restore/gen_reward_specs.py")
    lines.append("")
    lines.append("questCompensations:")
    lines.append("  upsert:")

    for r in rows:
        gid = r["gid"]
        v = r["v17"]
        exp = int(v["exp"]) if str(v["exp"]).strip() != "" else 0
        gold = int(v["gold"]) if str(v["gold"]).strip() != "" else 0
        item_bag = v["itemBag"]
        classic_items = [(int(t), int(q), c) for (t, q, c) in v["items"]]

        # Build the emitted item rows: classic rows verbatim, then new-class rows.
        emitted = list(classic_items)  # (templateId, qty, class)

        if item_bag == "class" and classic_items:
            # Classify the bag.
            weapon_ids = [t for (t, q, c) in classic_items if is_weapon(items.get(t, {"cit": ""}))]
            armor_ids = [(t, q, c) for (t, q, c) in classic_items if is_armor(items.get(t, {"cit": ""}))]

            new_rows = []
            if weapon_ids:
                # All classic weapons in a bag share one requiredLevel.
                levels = {items[t]["requiredLevel"] for t in weapon_ids}
                if len(levels) != 1:
                    sys.exit(f"HARD FAIL: quest {gid} weapon bag has mixed requiredLevels {levels}")
                classic_level = next(iter(levels))
                sel = {}
                for cls in NEW_CLASSES:
                    wid, chosen_level = pick_weapon(cls, classic_level)
                    new_rows.append((wid, 1, cls))
                    sel[cls] = (wid, chosen_level, classic_level)
                    if cls == "glaiver" and chosen_level != classic_level:
                        glaiver_flag.append(
                            f"quest {gid}: classic weapon rl{classic_level} -> glaiver {wid} rl{chosen_level} (nearest)"
                        )
                weapon_select_log[gid] = sel

            # Armor extension: armor is shared by type, so a piece appears once per
            # classic wearer. Extend per DISTINCT templateId (in first-seen order),
            # adding each post-classic class listed in that piece's v92 requiredClass.
            seen_armor = set()
            for (t, q, c) in armor_ids:
                if t in seen_armor:
                    continue
                seen_armor.add(t)
                rc = {x for x in items[t]["requiredClass"].split(";") if x}
                for cls in NEW_CLASSES:
                    if cls.upper() in rc:
                        new_rows.append((t, q, cls))

            if new_rows:
                emitted.extend(new_rows)
                extended_quests.append(gid)

        # --- emit YAML ---
        lines.append(f"    - questId: {gid}")
        lines.append(f"      huntingZoneId: {HUNTING_ZONE}")
        lines.append("      compensations:")
        lines.append("        - compensationId: 1")
        lines.append('          type: "normal"')
        lines.append(f"          exp: {exp}")
        lines.append(f"          gold: {gold}")
        if item_bag:
            lines.append(f'          itemBag: "{item_bag}"')
        if emitted:
            lines.append("          items:")
            for (t, q, c) in emitted:
                if c:
                    lines.append(f"            - templateId: {t}")
                    lines.append(f"              quantity: {q}")
                    lines.append(f'              class: "{c}"')
                else:
                    lines.append(f"            - templateId: {t}")
                    lines.append(f"              quantity: {q}")
        op_created_style += 1

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- report to stderr (not part of the spec) ---
    print(f"Wrote {OUT}", file=sys.stderr)
    print(f"Upsert rows (quests): {op_created_style}", file=sys.stderr)
    print(f"Extended (per-class bag) quests: {len(extended_quests)} -> {extended_quests}", file=sys.stderr)
    print("Weapon-bag new-class selection (id@requiredLevel, classic rl):", file=sys.stderr)
    for gid in sorted(weapon_select_log):
        sel = weapon_select_log[gid]
        parts = [f"{cls}={wid}@rl{lv}(classic rl{cl})" for cls, (wid, lv, cl) in sel.items()]
        print(f"  quest {gid}: " + ", ".join(parts), file=sys.stderr)
    if glaiver_flag:
        print("Glaiver non-exact substitutions:", file=sys.stderr)
        for g in glaiver_flag:
            print("  " + g, file=sys.stderr)


if __name__ == "__main__":
    main()
