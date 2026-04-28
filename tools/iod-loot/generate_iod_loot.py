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
FEED_QTY             = 4      # baseline at mean mob; 1:2 enchant ratio with alka
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
    qty_alka, qty_feed, qty_unit = {}, {}, {}  # per-mob qty multipliers
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
            qty_feed[nid] = qty_scaled(FEED_QTY, s)
            qty_unit[nid] = qty_scaled(1, s)
        else:
            s = score(hp, atk) / mean
            prob[nid]  = round(min(MAX_PROB, max(MIN_PROB,            BASE_PROB * s)),            2)
            cry[nid]   = round(min(MAX_PROB, max(MIN_PROB,    CRYSTAL_BASE_PROB * s)),            2)
            dyad[nid]  = round(min(MAX_PROB, max(MIN_PROB,       DYAD_BASE_PROB * s)),            3)
            sdyad[nid] = round(min(MAX_PROB, max(MIN_PROB_SMART_DYAD, SMART_DYAD_BASE_PROB * s)), 4)
            inf[nid]   = round(min(MAX_PROB, max(MIN_PROB,   INFUSION_BASE_PROB * s)),            3)
            qty_alka[nid] = qty_scaled(ALKA_QTY, s)
            qty_feed[nid] = qty_scaled(FEED_QTY, s)
            qty_unit[nid] = qty_scaled(1, s)
    return mean, prob, cry, dyad, sdyad, inf, qty_alka, qty_feed, qty_unit


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


def print_yield(prob, qty_alka, qty_feed):
    exp_alka = sum(prob[nid] * qty_alka[nid] for nid, *_ in NPCS) / len(NPCS) * KILL_BUDGET
    exp_feed = sum(prob[nid] * qty_feed[nid] for nid, *_ in NPCS) / len(NPCS) * KILL_BUDGET
    print(f"\n=== Expected yield from {KILL_BUDGET} uniformly-sampled quest kills ===")
    print(f"  ~{exp_alka:.0f} Masterwork Alkahest")
    print(f"  ~{exp_feed:.0f} Tier 1 Feedstock")
    a3, f3 = expected_cost_to(3)
    print(f"  Cost to +3 on one piece: {a3:.0f} alka + {f3:.0f} feed")


def generate_yaml(prob, cry, dyad, sdyad, inf, qty_alka, qty_feed, qty_unit):
    lines = [
        "# Island of Dawn (zone 13) — difficulty-weighted loot table",
        "#",
        f"# Difficulty scoring: sqrt(maxHp * atk) per mob, scaled to base_prob={BASE_PROB} at mean.",
        f"# Environmental mobs (creature playStyle, HP<50): floored at {MIN_PROB}.",
        f"# Probability range: [{MIN_PROB}, {MAX_PROB}].",
        f"# Drop qty also scales by ceil(base_qty * sqrt(score_ratio)) — bosses drop more per trigger.",
        "#",
        "# To adjust rates edit the constants in generate_iod_loot.py and re-run.",
        "# Idempotency: upsert — safe to re-apply against any baseline.",
        "",
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "eCompensations:",
        "  upsert:",
    ]

    for nid, name, hp, atk, lvl, env in NPCS:
        p, cp, dp, sdp, ip = prob[nid], cry[nid], dyad[nid], sdyad[nid], inf[nid]
        qa, qf, qu = qty_alka[nid], qty_feed[nid], qty_unit[nid]
        lines += [
            f"    - huntingZoneId: 13",
            f"      npcTemplateId: {nid}",
            f'      npcName: "{name}"',
            f"      itemBags:",
            f"        - id: 1",
            f'          bagName: "Alkahest"',
            f"          probability: {p}",
            f"          items:",
            f"            - templateId: 21351",
            f'              name: "Masterwork Alkahest"',
            f"              min: {qa}",
            f"              max: {qa}",
            f"              probability: 1.0",
            f"        - id: 9",
            f'          bagName: "Feedstock"',
            f"          probability: {p}",
            f"          items:",
            f"            - templateId: 94101",
            f'              name: "Tier 1 Feedstock"',
            f"              min: {qf}",
            f"              max: {qf}",
            f"              probability: 1.0",
            f"        - id: 2",
            f'          bagName: "CrystalBoxes"',
            f"          probability: {cp}",
            f"          equalProbability: true",
            f"          items:",
            f"            - templateId: 602176",
            f'              name: "Weapon Crystal Box (Rhomb)"',
            f"              min: {qu}",
            f"              max: {qu}",
            f"            - templateId: 602177",
            f'              name: "Armor Crystal Box (Rhomb)"',
            f"              min: {qu}",
            f"              max: {qu}",
            f"        - id: 3",
            f'          bagName: "DyadStructure"',
            f"          probability: {dp}",
            f"          items:",
            f"            - templateId: 96108",
            f'              name: "Dyad Rhomb Structure"',
            f"              min: {qu}",
            f"              max: {qu}",
            f"              probability: 1.0",
            f"        - id: 4",
            f'          bagName: "SmartDyadStructure"',
            f"          probability: {sdp}",
            f"          items:",
            f"            - templateId: 96114",
            f'              name: "Smart Dyad Rhomb Structure"',
            f"              min: {qu}",
            f"              max: {qu}",
            f"              probability: 1.0",
            f"        - id: 5",
            f'          bagName: "InfusionBoxUncommon"',
            f"          probability: {ip}",
            f"          equalProbability: true",
            f"          items:",
            f"            - templateId: 602190",
            f'              name: "Infusion Weapon Box (Uncommon)"',
            f"              min: {qu}",
            f"              max: {qu}",
            f"            - templateId: 602193",
            f'              name: "Infusion Chest Box (Uncommon)"',
            f"              min: {qu}",
            f"              max: {qu}",
            f"            - templateId: 602196",
            f'              name: "Infusion Gloves Box (Uncommon)"',
            f"              min: {qu}",
            f"              max: {qu}",
            f"            - templateId: 602199",
            f'              name: "Infusion Boots Box (Uncommon)"',
            f"              min: {qu}",
            f"              max: {qu}",
        ]

        if nid == KUGAI_NPC_ID:
            for bag_id, qty in KUGAI_TOKEN_BAGS:
                lines += [
                    f"        - id: {bag_id}",
                    f'          bagName: "KugaiToken_{qty}"',
                    f"          probability: 1.0",
                    f"          items:",
                    f"            - templateId: {KUGAI_TOKEN_ID}",
                    f'              name: "Kugai\'s Crest"',
                    f"              min: {qty}",
                    f"              max: {qty}",
                    f"              probability: 1.0",
                ]
        elif nid in ELITE_TOKEN_DROPS:
            qty = ELITE_TOKEN_DROPS[nid]
            lines += [
                f"        - id: 6",
                f'          bagName: "KugaiToken_{qty}"',
                f"          probability: 1.0",
                f"          items:",
                f"            - templateId: {KUGAI_TOKEN_ID}",
                f'              name: "Kugai\'s Crest"',
                f"              min: {qty}",
                f"              max: {qty}",
                f"              probability: 1.0",
            ]

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate IoD loot spec.")
    parser.add_argument("--patch", required=True, help="Patch number, e.g. 001")
    args = parser.parse_args()

    mean, prob, cry, dyad, sdyad, inf, qty_alka, qty_feed, qty_unit = build_prob_maps()
    print_ranking(mean, prob, cry, dyad, sdyad, inf)
    print_yield(prob, qty_alka, qty_feed)

    out = Path(__file__).parents[2] / "specs" / "patches" / args.patch / "17-iod-loot.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(generate_yaml(prob, cry, dyad, sdyad, inf, qty_alka, qty_feed, qty_unit), encoding="utf-8")
    print(f"\nSpec written → {out}")


if __name__ == "__main__":
    main()
