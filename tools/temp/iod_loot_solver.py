"""
IoD Loot Table Solver — difficulty-weighted drop rates
Score: sqrt(maxHp * atk) — geometric mean of time-to-kill and danger pressure.
Environmental mobs (playStyle=creature, HP<50) are floored at MIN_PROB.
"""

import sys, math
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
    (101,    "Giant Honeybee",        5.32,      900.00,    1,  True),   # creature
    (102,    "Docile Terron",         4.26,      900.00,    1,  True),   # creature
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
    (1011,   "Terron Saboteur",       8.26,      900.00,    9,  True),   # creature
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

BASE_PROB         = 0.20   # enchant mats
CRYSTAL_BASE_PROB = 0.10   # crystal boxes
DYAD_BASE_PROB       = 0.01    # dyad structure (rare)
SMART_DYAD_BASE_PROB = 0.001   # smart dyad structure (super rare)
INFUSION_BASE_PROB   = 0.01    # uncommon infusion box (1-2% range)
MIN_PROB             = 0.01
MIN_PROB_SMART_DYAD  = 0.001
MAX_PROB          = 0.80
ALKA_QTY  = 1
FEED_QTY  = 2

# ── Compute difficulty scores ─────────────────────────────────────────────────
def score(hp, atk):
    return math.sqrt(hp * atk)

combat = [(nid, name, hp, atk, lvl) for nid, name, hp, atk, lvl, env in NPCS if not env]
scores = [score(hp, atk) for _, _, hp, atk, _ in combat]
mean_score = sum(scores) / len(scores)

# Map id → scaled probabilities
prob_map = {}
crystal_prob_map = {}
dyad_prob_map = {}
smart_dyad_prob_map = {}
infusion_prob_map = {}
for nid, name, hp, atk, lvl, env in NPCS:
    if env:
        prob_map[nid] = MIN_PROB
        crystal_prob_map[nid] = MIN_PROB
        dyad_prob_map[nid] = MIN_PROB
        smart_dyad_prob_map[nid] = MIN_PROB_SMART_DYAD
        infusion_prob_map[nid] = MIN_PROB
    else:
        s = score(hp, atk) / mean_score
        prob_map[nid]          = round(min(MAX_PROB, max(MIN_PROB, BASE_PROB * s)), 2)
        crystal_prob_map[nid]  = round(min(MAX_PROB, max(MIN_PROB, CRYSTAL_BASE_PROB * s)), 2)
        dyad_prob_map[nid]     = round(min(MAX_PROB, max(MIN_PROB, DYAD_BASE_PROB * s)), 3)
        smart_dyad_prob_map[nid] = round(min(MAX_PROB, max(MIN_PROB_SMART_DYAD, SMART_DYAD_BASE_PROB * s)), 4)
        infusion_prob_map[nid] = round(min(MAX_PROB, max(MIN_PROB, INFUSION_BASE_PROB * s)), 3)

# ── Print difficulty ranking ──────────────────────────────────────────────────
print("=== IoD Mob Difficulty Ranking — sqrt(maxHp × atk) ===")
print(f"{'ID':>7}  {'Name':<25}  {'Lvl':>3}  {'maxHp':>9}  {'atk':>9}  {'Score':>9}  {'MatProb':>7}  {'CryProb':>7}  {'DyadProb':>8}  {'SmartProb':>9}  {'InfProb':>7}  {'Env':>4}")
ranked = sorted(NPCS, key=lambda r: score(r[2], r[3]) if not r[5] else 0)
for nid, name, hp, atk, lvl, env in ranked:
    s = score(hp, atk)
    p = prob_map[nid]
    cp = crystal_prob_map[nid]
    dp = dyad_prob_map[nid]
    sdp = smart_dyad_prob_map[nid]
    ip = infusion_prob_map[nid]
    flag = "ENV" if env else ""
    print(f"  {nid:>7}  {name:<25}  {lvl:>3}  {hp:>9.0f}  {atk:>9.0f}  {s:>9.0f}  {p:>7.2f}  {cp:>7.2f}  {dp:>8.3f}  {sdp:>9.4f}  {ip:>7.3f}  {flag:>4}")

print(f"\n  Mean combat score: {mean_score:.0f}  →  base_prob {BASE_PROB} maps to mean mob")

# ── Expected yield from quest kill budget ─────────────────────────────────────
KILL_BUDGET = 50
exp_alka = sum(prob_map[nid] * ALKA_QTY for nid, *_ in NPCS) / len(NPCS) * KILL_BUDGET
exp_feed = sum(prob_map[nid] * FEED_QTY for nid, *_ in NPCS) / len(NPCS) * KILL_BUDGET

print(f"\n=== Expected yield from {KILL_BUDGET} uniformly-sampled quest kills ===")
print(f"  ~{exp_alka:.0f} Masterwork Alkahest")
print(f"  ~{exp_feed:.0f} Tier 1 Feedstock")
a3, f3 = expected_cost_to(3)
print(f"  Cost to +3 on one piece: {a3:.0f} alka + {f3:.0f} feed")

# ── Generate YAML ─────────────────────────────────────────────────────────────
lines = [
    "# Island of Dawn (zone 13) — enchant material drops",
    "#",
    f"# Difficulty scoring: sqrt(maxHp * atk) per mob, scaled to base_prob={BASE_PROB} at mean.",
    f"# Environmental mobs (creature playStyle, HP<50): floored at {MIN_PROB}.",
    f"# Probability range: [{MIN_PROB}, {MAX_PROB}].",
    "#",
    "# Starting conservative — adjust BASE_PROB / CRYSTAL_BASE_PROB in iod_loot_solver.py after testing.",
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
    p   = prob_map[nid]
    cp  = crystal_prob_map[nid]
    dp  = dyad_prob_map[nid]
    sdp = smart_dyad_prob_map[nid]
    ip  = infusion_prob_map[nid]
    lines += [
        f"    - huntingZoneId: 13",
        f"      npcTemplateId: {nid}",
        f'      npcName: "{name}"',
        f"      itemBags:",
        f"        - id: 1",
        f'          bagName: "EnchantMaterials"',
        f"          probability: {p}",
        f"          items:",
        f"            - templateId: 21351",
        f'              name: "Masterwork Alkahest"',
        f"              min: {ALKA_QTY}",
        f"              max: {ALKA_QTY}",
        f"              probability: 1.0",
        f"            - templateId: 94101",
        f'              name: "Tier 1 Feedstock"',
        f"              min: {FEED_QTY}",
        f"              max: {FEED_QTY}",
        f"              probability: 1.0",
        f"        - id: 2",
        f'          bagName: "CrystalBoxes"',
        f"          probability: {cp}",
        f"          equalProbability: true",
        f"          items:",
        f"            - templateId: 602176",
        f'              name: "Weapon Crystal Box (Rhomb)"',
        f"            - templateId: 602177",
        f'              name: "Armor Crystal Box (Rhomb)"',
        f"        - id: 3",
        f'          bagName: "DyadStructure"',
        f"          probability: {dp}",
        f"          items:",
        f"            - templateId: 96108",
        f'              name: "Dyad Rhomb Structure"',
        f"              min: 1",
        f"              max: 1",
        f"              probability: 1.0",
        f"        - id: 4",
        f'          bagName: "SmartDyadStructure"',
        f"          probability: {sdp}",
        f"          items:",
        f"            - templateId: 96114",
        f'              name: "Smart Dyad Rhomb Structure"',
        f"              min: 1",
        f"              max: 1",
        f"              probability: 1.0",
        f"        - id: 5",
        f'          bagName: "InfusionBoxUncommon"',
        f"          probability: {ip}",
        f"          equalProbability: true",
        f"          items:",
        f"            - templateId: 602190",
        f'              name: "Infusion Weapon Box (Uncommon)"',
        f"            - templateId: 602193",
        f'              name: "Infusion Chest Box (Uncommon)"',
        f"            - templateId: 602196",
        f'              name: "Infusion Gloves Box (Uncommon)"',
        f"            - templateId: 602199",
        f'              name: "Infusion Boots Box (Uncommon)"',
    ]

OUT = r"D:\dev\mmogate\github\reforged-server-content\reforged\specs\patches\001\17-iod-loot.yaml"
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print(f"\nSpec written → {OUT}")
