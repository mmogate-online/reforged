#!/usr/bin/env python3
"""
Island of Dawn (zone 13) loot table generator — difficulty-weighted drop rates.

Difficulty score: sqrt(maxHp * atk) per mob, scaled proportionally so the mean
combat mob maps to each base probability. Environmental mobs (creature playStyle,
HP < 50) are floored at their respective minimums.

Generates: specs/patches/{NNN}/17-iod-loot.yaml

Usage:
    python generate_iod_loot.py --patch 001
"""

import argparse
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import xml.etree.ElementTree as ET

# v31 server ECompensation source for the classic gold + item drops we merge in.
V31_ECOMP = Path(
    "Z:/tera pserver/v31.04/TERAServer/Executable/Bin/Datasheet/CompensationData/ECompensation_13.xml"
)
# Reforged item bags are renumbered into a disjoint id range so they never collide
# with the verbatim v31 ItemBag ids (all <= 20) when both are merged into one entry.
REFORGED_BAG_ID_OFFSET = 100


def _q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def load_v31_comps():
    """npcTemplateId -> Compensation element from the v31 ECompensation_13 table."""
    root = ET.parse(str(V31_ECOMP)).getroot()
    return {int(c.get("npcTemplateId")): c for c in root.findall("Compensation")}


def v31_gold_lines(comp):
    """YAML lines for the v31 GoldBags of a Compensation (verbatim), under goldBags:."""
    out = []
    for gb in comp.findall("GoldBag"):
        out.append(f"        - bagName: {_q(gb.get('bagName', ''))}")
        out.append(f"          probability: {gb.get('probability')}")
        if gb.get("wValue") is not None:
            out.append(f"          wValue: {gb.get('wValue')}")
        out.append(f"          min: {gb.get('min')}")
        out.append(f"          max: {gb.get('max')}")
        if gb.get("t"):
            out.append(f"          t: {_q(gb.get('t'))}")
    return out


def build_id_resolver():
    """item templateId -> (package, CONSTANT), preferring item-ids, never npc-ids.

    npc template ids and item template ids are separate id spaces, so an item drop must
    resolve to an ITEM constant even when npc-ids also names that number.
    """
    sys.path.insert(0, str(Path(__file__).parents[1] / "spec-standardize"))
    from analyze_ids import load_registry
    reg = load_registry(str(Path(__file__).parents[1].parent / "packages"))
    idmap = {}
    for val, lst in reg.items():
        cands = [(pkg, name) for (pkg, name, exp, kind) in lst
                 if exp and kind == "scalar" and pkg != "npc-ids"]
        if not cands:
            continue
        cands.sort(key=lambda pn: (0 if pn[0] == "item-ids" else 1, pn[0], pn[1]))
        idmap[val] = cands[0]
    return idmap


def _tid(raw, idmap, used):
    """Render a templateId value as a $CONSTANT when a package names it, else raw."""
    try:
        iid = int(raw)
    except (TypeError, ValueError):
        return str(raw)
    r = idmap.get(iid)
    if r:
        pkg, const = r
        used.setdefault(pkg, set()).add(const)
        return f"${const}"
    return str(iid)


def v31_item_lines(comp, idmap, used):
    """YAML lines for the v31 ItemBags of a Compensation (verbatim), under itemBags:.

    Item templateIds are emitted as $CONSTANT where an item package names them.
    """
    out = []
    for ib in comp.findall("ItemBag"):
        out.append(f"        - id: {ib.get('id')}")
        out.append(f"          bagName: {_q(ib.get('bagName', ''))}")
        out.append(f"          probability: {ib.get('probability')}")
        if ib.get("wValue") is not None:
            out.append(f"          wValue: {_q(ib.get('wValue'))}")
        if ib.get("t"):
            out.append(f"          t: {_q(ib.get('t'))}")
        out.append(f"          items:")
        for it in ib.findall("Item"):
            out.append(f"            - templateId: {_tid(it.get('templateId'), idmap, used)}")
            out.append(f"              name: {_q(it.get('name', ''))}")
            out.append(f"              min: {it.get('min', '1')}")
            out.append(f"              max: {it.get('max', '1')}")
            out.append(f"              probability: {it.get('probability')}")
    return out

# ── Enchant data (MaterialEnchant 20001) ──────────────────────────────────────
STEPS = [
    (0,  1.00,  2,  4),
    (1,  1.00,  2,  4),
    (2,  1.00,  4,  8),
    (3,  1.00,  4,  8),
    (4,  1.00, 12, 24),
    (5,  1.00, 12, 24),
    (6,  1.00, 24, 48),
    (7,  1.00, 24, 48),
    (8,  0.95, 24, 48),
    (9,  0.95, 24, 48),
    (10, 0.87, 24, 48),
    (11, 0.87, 24, 48),
]

def expected_cost_to(lvl):
    a = f = 0.0
    for step, prob, alka, feed in STEPS[:lvl]:
        a += alka / prob
        f += feed / prob
    return a, f

# ── NPC stats (from mcp__datasheet-v92__lookup, zone 13) ─────────────────────
# (id, display_name, maxHp, atk, level, is_environmental)
NPCS = [
    (1,      "Pigling",               884.57,    1200.00,   3,  False),
    (2,      "Sporewalker",           8823.72,   11250.00,  6,  False),
    (3,      "Ponderous Sporewalker", 7448.88,   11250.00,  5,  False),
    (4,      "Dwarf Orcan",           669.27,    1140.00,   7,  False),
    (5,      "Orcan Raider",          5949.05,   11250.00,  7,  False),
    (6,      "Kariagon",              9236.53,   11250.00,  8,  False),
    (7,      "Disc Reaper",           9769.64,   11250.00,  8,  False),
    (8,      "Runekeeper",            9750.57,   11250.00,  9,  False),
    (9,      "Destroyer",             16250.95,  11250.00,  9,  False),
    (101,    "Giant Honeybee",        5.32,      900.00,    1,  True),
    (102,    "Docile Terron",         4.26,      900.00,    1,  True),
    (111,    "Gentle Pigling",        982.86,    1200.00,   3,  False),
    (302,    "Terron Ringleader",     6656.40,   11250.00,  3,  False),
    (303,    "Terron Thief",          936.06,    1200.00,   3,  False),
    (304,    "Sickly Noruk",          8748.17,   11250.00,  3,  False),
    (555,    "Scion Scout",           12410.48,  11250.00,  10, False),
    (556,    "Scion Scout",           12410.48,  11250.00,  10, False),
    (557,    "Scion Scout",           12410.48,  11250.00,  10, False),
    (558,    "Scion Scout",           12410.48,  11250.00,  10, False),
    (601,    "Dark Marauder",         10799.02,  11250.00,  7,  False),
    (901,    "Orcan Guardian",        8094.19,   11250.00,  7,  False),
    (902,    "Dwarf Guardian",        669.27,    1140.00,   7,  False),
    (1001,   "Vekas",                 9529.43,   25464.37,  4,  False),
    (1002,   "Acharak",               13277.51,  21220.31,  8,  False),
    (1003,   "Acharak's Soldier",     1239.79,   3875.43,   8,  False),
    (1004,   "Kugai",                 16412.86,  28293.75,  10, False),
    (1011,   "Terron Saboteur",       8.26,      900.00,    9,  True),
    (300541, "Rockcrawler",           1347.80,   1200.00,   5,  False),
    (300542, "Rockcrawler Cleaver",   9584.33,   11250.00,  5,  False),
    (300910, "Prowling Cromos",       9986.74,   11250.00,  8,  False),
    (300911, "Cromos",                12686.82,  11250.00,  7,  False),
    (300920, "Shaggy Noruk",          8931.52,   11250.00,  7,  False),
    (300921, "Noruk",                 8171.40,   11250.00,  2,  False),
    (300930, "Elder Ghilliedhu",      7231.33,   11250.00,  2,  False),
    (300931, "Ghilliedhu",            6652.80,   11250.00,  1,  False),
    (300932, "Horned Ghilliedhu",     9487.87,   11250.00,  6,  False),
    (300933, "Hardened Ghilliedhu",   7741.75,   11250.00,  3,  False),
    (300941, "Terron",                810.00,    1200.00,   1,  False),
    (300942, "Terron Thrall",         727.38,    960.00,    8,  False),
    (300943, "Terron Saboteur",       1353.75,   1200.00,   7,  False),
    (300944, "Terron Chief",          5760.00,   11250.00,  1,  False),
    (300945, "Terron Lama",           9626.65,   11250.00,  7,  False),
    (300951, "Dark Raider",           9236.53,   11250.00,  8,  False),
    (300960, "Devoted Ebon Imp",      727.38,    960.00,    8,  False),
    (301191, "Stonebeak Raider",      1058.20,   1200.00,   4,  False),
    (301193, "Stonebeak Brigand",     990.81,    1200.00,   3,  False),
    (301194, "Stonebeak Highcrest",   6487.08,   11250.00,  4,  False),
]

# ── Kugai token drops ────────────────────────────────────────────────────────
KUGAI_NPC_ID    = 1004
KUGAI_TOKEN_ID  = 95216
KUGAI_TOKEN_BAGS = [(6, 2), (7, 3), (8, 5)]  # (bag_id, qty) — 10 tokens/kill

# Bottleneck relief: nearby elites also drop Kugai tokens (always, single bag).
# Scaled below Kugai so he stays the per-kill king while area farming smooths
# throughput on contested servers.
ELITE_TOKEN_DROPS = {
    9:      3,  # Destroyer       (lv9, 2 spawns,  63% of Kugai score)
    8:      2,  # Runekeeper      (lv9, 2 spawns,  49%)
    300951: 2,  # Dark Raider     (lv8, 1 spawn,   47%)
    6:      2,  # Kariagon        (lv8, 1 spawn,   47%)
    901:    1,  # Orcan Guardian  (lv7, 10 spawns, 44%)
}

# ── Drop rate configuration ───────────────────────────────────────────────────
BASE_PROB            = 0.40   # enchant mats (at mean mob)
CRYSTAL_BASE_PROB    = 0.15   # rhomb crystal boxes
DYAD_BASE_PROB       = 0.01   # dyad rhomb structure (rare)
SMART_DYAD_BASE_PROB = 0.001  # smart dyad rhomb structure (super rare)
INFUSION_BASE_PROB   = 0.01   # uncommon infusion box
MIN_PROB             = 0.01
MIN_PROB_SMART_DYAD  = 0.001
MAX_PROB             = 0.80
ALKA_QTY             = 2      # baseline at mean mob; scales by sqrt(score_ratio)
KILL_BUDGET          = 50


def score(hp, atk):
    return math.sqrt(hp * atk)


def qty_scaled(base_qty, score_ratio):
    """Scale per-trigger drop quantity by sqrt(score_ratio), ceiling.

    sqrt curve keeps trash mobs at base qty while letting bosses ~2x the base.
    Ceiling guarantees every drop yields at least 1 unit.
    """
    return max(1, math.ceil(base_qty * math.sqrt(score_ratio)))


def build_prob_maps():
    combat = [r for r in NPCS if not r[5]]
    scores = [score(r[2], r[3]) for r in combat]
    mean = sum(scores) / len(scores)

    prob, cry, dyad, sdyad, inf = {}, {}, {}, {}, {}
    qty_alka, qty_unit = {}, {}  # per-mob qty multipliers
    for nid, _, hp, atk, _, env in NPCS:
        if env:
            prob[nid]  = MIN_PROB
            cry[nid]   = MIN_PROB
            dyad[nid]  = MIN_PROB
            sdyad[nid] = MIN_PROB_SMART_DYAD
            inf[nid]   = MIN_PROB
            # Env mobs: tiny score ratio → qty floors at 1
            s = score(hp, atk) / mean
            qty_alka[nid] = qty_scaled(ALKA_QTY, s)
            qty_unit[nid] = qty_scaled(1, s)
        else:
            s = score(hp, atk) / mean
            prob[nid]  = round(min(MAX_PROB, max(MIN_PROB,            BASE_PROB * s)),            2)
            cry[nid]   = round(min(MAX_PROB, max(MIN_PROB,    CRYSTAL_BASE_PROB * s)),            2)
            dyad[nid]  = round(min(MAX_PROB, max(MIN_PROB,       DYAD_BASE_PROB * s)),            3)
            sdyad[nid] = round(min(MAX_PROB, max(MIN_PROB_SMART_DYAD, SMART_DYAD_BASE_PROB * s)), 4)
            inf[nid]   = round(min(MAX_PROB, max(MIN_PROB,   INFUSION_BASE_PROB * s)),            3)
            qty_alka[nid] = qty_scaled(ALKA_QTY, s)
            qty_unit[nid] = qty_scaled(1, s)
    return mean, prob, cry, dyad, sdyad, inf, qty_alka, qty_unit


def print_ranking(mean, prob, cry, dyad, sdyad, inf):
    print("=== IoD Mob Difficulty Ranking — sqrt(maxHp × atk) ===")
    print(f"{'ID':>7}  {'Name':<25}  {'Lvl':>3}  {'maxHp':>9}  {'atk':>9}  {'Score':>9}"
          f"  {'MatProb':>7}  {'CryProb':>7}  {'DyadProb':>8}  {'SmartProb':>9}  {'InfProb':>7}  {'Env':>4}")
    ranked = sorted(NPCS, key=lambda r: score(r[2], r[3]) if not r[5] else 0)
    for nid, name, hp, atk, lvl, env in ranked:
        s = score(hp, atk)
        flag = "ENV" if env else ""
        print(f"  {nid:>7}  {name:<25}  {lvl:>3}  {hp:>9.0f}  {atk:>9.0f}  {s:>9.0f}"
              f"  {prob[nid]:>7.2f}  {cry[nid]:>7.2f}  {dyad[nid]:>8.3f}"
              f"  {sdyad[nid]:>9.4f}  {inf[nid]:>7.3f}  {flag:>4}")
    print(f"\n  Mean combat score: {mean:.0f}  →  base_prob {BASE_PROB} maps to mean mob")


def print_yield(prob, qty_alka):
    exp_alka = sum(prob[nid] * qty_alka[nid] for nid, *_ in NPCS) / len(NPCS) * KILL_BUDGET
    print(f"\n=== Expected yield from {KILL_BUDGET} uniformly-sampled quest kills ===")
    print(f"  ~{exp_alka:.0f} Masterwork Alkahest")
    a3, f3 = expected_cost_to(3)
    print(f"  Cost to +3 on one piece: {a3:.0f} alka + {f3:.0f} feed")


# FeedstockBag is deliberately absent. Framework 04 §5e: "There is no direct content drop
# of feedstock in this design, it is downstream of infusion fodder", restated as ruling R13.
# Fodder dismantling (DecompositionData, see specs/patches/002/35) is the sole faucet, so the
# bag definition was removed from packages/reforged-loot-bags as well.
REFORGED_DEFS = ["AlkahestBag", "DyadStructureBag",
                 "SmartDyadStructureBag", "CrystalBoxesBag", "InfusionBoxUncommonBag"]


def generate_yaml(prob, cry, dyad, sdyad, inf, qty_alka, qty_unit, v31, idmap):
    off = REFORGED_BAG_ID_OFFSET
    used = {}   # package -> set of item-id constants referenced by this spec

    body = []
    for nid, name, hp, atk, lvl, env in NPCS:
        p, cp, dp, sdp, ip = prob[nid], cry[nid], dyad[nid], sdyad[nid], inf[nid]
        qa, qu = qty_alka[nid], qty_unit[nid]
        comp = v31.get(nid)

        body += [
            f"    - huntingZoneId: 13",
            f"      npcTemplateId: {nid}",
            f'      npcName: "{name}"',
        ]

        # 1. v31 gold (priority) + v31 item bags, verbatim (item ids -> $CONSTANT)
        gold = v31_gold_lines(comp) if comp is not None else []
        if gold:
            body.append("      goldBags:")
            body += gold
        body.append("      itemBags:")
        if comp is not None:
            body += v31_item_lines(comp, idmap, used)

        # 2. reforged item bags via the reforged-loot-bags package templates.
        # Emission order (Alkahest, Crystal, Dyad, SmartDyad, Infusion) is preserved so the
        # expanded itemBags list matches the pre-refactor spec. The Feedstock bag that used
        # to sit second is GONE: no direct content drop of feedstock (framework 04 §5e, R13).
        body += [
            f"        - $extends: AlkahestBag",
            f"          $with: {{ PROB: {p}, QTY: {qa} }}",
            f"        - $extends: CrystalBoxesBag",
            f"          $with: {{ PROB: {cp}, QTY: {qu} }}",
            f"        - $extends: DyadStructureBag",
            f"          $with: {{ PROB: {dp}, QTY: {qu} }}",
            f"        - $extends: SmartDyadStructureBag",
            f"          $with: {{ PROB: {sdp}, QTY: {qu} }}",
            f"        - $extends: InfusionBoxUncommonBag",
            f"          $with: {{ PROB: {ip}, QTY: {qu} }}",
        ]

        token_bags = (KUGAI_TOKEN_BAGS if nid == KUGAI_NPC_ID
                      else [(6, ELITE_TOKEN_DROPS[nid])] if nid in ELITE_TOKEN_DROPS else [])
        for bag_id, qty in token_bags:
            body += [
                f"        - id: {bag_id + off}",
                f'          bagName: "KugaiToken_{qty}"',
                f"          probability: 1.0",
                f"          items:",
                f"            - templateId: {_tid(KUGAI_TOKEN_ID, idmap, used)}",
                f'              name: "Kugai\'s Crest"',
                f"              min: {qty}",
                f"              max: {qty}",
                f"              probability: 1.0",
            ]

    header = [
        "# Island of Dawn (zone 13) - merged loot table (v31 restore + reforged economy)",
        "#",
        "# Generated by tools/iod-loot/generate_iod_loot.py (do not hand-edit).",
        "#",
        "# Each mob entry is the UNION of two sources:",
        "#   1. v31 GoldBags + v31 ItemBags, ported verbatim from the v31 server",
        "#      ECompensation_13.xml. Item ids are emitted as item-ids package constants.",
        f"#   2. Reforged ItemBags via the reforged-loot-bags package, difficulty-weighted by",
        f"#      sqrt(maxHp*atk); bag ids offset by +{off} so they never collide with v31 ids.",
        "#",
        f"# Difficulty scoring: sqrt(maxHp * atk) per mob, scaled to base_prob={BASE_PROB} at mean.",
        f"# Environmental mobs (creature playStyle, HP<50): floored at {MIN_PROB}.",
        "# Idempotency: upsert - safe to re-apply against any baseline.",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "imports:",
        "  - from: reforged-loot-bags",
        "    use:",
        "      definitions:",
    ]
    header += [f"        - {d}" for d in REFORGED_DEFS]
    for pkg in sorted(used):
        header += [f"  - from: {pkg}", "    use:", "      variables:"]
        header += [f"        - {c}" for c in sorted(used[pkg])]
    header += ["", "eCompensations:", "  upsert:"]

    return "\n".join(header + body) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate IoD loot spec.")
    parser.add_argument("--patch", required=True, help="Patch number, e.g. 001")
    args = parser.parse_args()

    mean, prob, cry, dyad, sdyad, inf, qty_alka, qty_unit = build_prob_maps()
    print_ranking(mean, prob, cry, dyad, sdyad, inf)
    print_yield(prob, qty_alka)

    v31 = load_v31_comps()
    idmap = build_id_resolver()
    out = Path(__file__).parents[2] / "specs" / "patches" / args.patch / "17-iod-loot.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(generate_yaml(prob, cry, dyad, sdyad, inf, qty_alka, qty_unit, v31, idmap),
                   encoding="utf-8")
    print(f"\nSpec written → {out}")


if __name__ == "__main__":
    main()
