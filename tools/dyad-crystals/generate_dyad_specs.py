"""
Dyad Crystal System Generator
Generates all YAML spec files, package files, and config updates for the
Dyad crystal system across tiers 1-6 (Rhomb through Crux).

Usage:
    python tmp/generate_dyad_specs.py
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Output directories
# ---------------------------------------------------------------------------
REFORGED = Path(__file__).resolve().parent.parent.parent
SPECS_DIR = REFORGED / "specs" / "patches" / "002"
PKG_DIR = REFORGED / "packages" / "crystals"
DYAD_ITEMS_PKG_DIR = REFORGED / "packages" / "dyad-crystal-items"

# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------
TIERS = [
    {"num": 1, "name": "Rhomb",    "level": 1,  "reqLevel": 1,  "buy": 262,    "sell": 26,    "grade": 1, "icon_suffix": "A"},
    {"num": 2, "name": "Cabochon", "level": 11, "reqLevel": 11, "buy": 830,    "sell": 83,    "grade": 2, "icon_suffix": "B"},
    {"num": 3, "name": "Hexage",   "level": 20, "reqLevel": 20, "buy": 5372,   "sell": 537,   "grade": 3, "icon_suffix": "C"},
    {"num": 4, "name": "Pentant",  "level": 32, "reqLevel": 32, "buy": 16554,  "sell": 1655,  "grade": 4, "icon_suffix": "D"},
    {"num": 5, "name": "Concach",  "level": 44, "reqLevel": 44, "buy": 60160,  "sell": 6016,  "grade": 5, "icon_suffix": "E"},
    {"num": 6, "name": "Crux",     "level": 55, "reqLevel": 55, "buy": 108919, "sell": 10891, "grade": 6, "icon_suffix": "F"},
]
TIER_NAMES = [t["name"] for t in TIERS]

# ---------------------------------------------------------------------------
# Item ID allocation (plan section 4.1)
# ---------------------------------------------------------------------------
WEAPON_ITEM_BASES = {1: 83416, 2: 83613, 3: 83810, 4: 84007, 5: 84600, 6: 84797}
ARMOR_ITEM_BASES  = {1: 83536, 2: 83733, 3: 83930, 4: 84127, 5: 84720, 6: 84917}

# Customizing ID allocation (plan section 4.3)
WEAPON_CUST_BASES = {1: 82400, 2: 82600, 3: 82800, 4: 83000, 5: 83200, 6: 83400}
ARMOR_CUST_BASES  = {1: 82520, 2: 82720, 3: 82920, 4: 83120, 5: 83320, 6: 83520}

# Structure IDs (plan section 4.2)
DYAD_STRUCTURE_IDS       = {1: 96108, 2: 96109, 3: 96110, 4: 96111, 5: 96112, 6: 96113}
SMART_DYAD_STRUCTURE_IDS = {1: 96114, 2: 96115, 3: 96116, 4: 96117, 5: 96118, 6: 96119}
RHOMB_STRUCTURE_ID = 96120

# Primary passivity IDs: 80400-80585, 31 per tier (20 weapon + 11 armor)
PRIMARY_PASS_BASE = 80400
# Secondary passivity IDs: 81014-81067, 9 per tier
SECONDARY_PASS_BASE = 81014
# Abnormality IDs: 12291-12350, 10 per tier (6 weapon + 4 armor proc families)
ABNORM_BASE = 12291

# ---------------------------------------------------------------------------
# Weapon families (20) — Dyad-eligible
# ---------------------------------------------------------------------------
WEAPON_FAMILIES = [
    # Non-proc families — per-type field configs from vanilla references
    {"name": "Pounding",    "conv": 91,  "type": 152, "proc": False, "kind": 0, "cond": 25, "condVal": 0, "mob": "any", "method": 3,
     "icon": "RedCustomize23A_Tex", "tooltip": "Increases damage to monsters by $value.",
     "values": [1.041, 1.049, 1.057, 1.065, 1.073, 1.082]},
    {"name": "Bitter",      "conv": 93,  "type": 167, "proc": False, "kind": 53, "cond": 24, "condVal": 2, "mob": "any", "method": 2,
     "icon": "RedCustomize24A_Tex", "tooltip": "Increases Crit Power by $value when attacking from behind.",
     "values": [1.37, 1.44, 1.51, 1.59, 1.66, 1.73]},
    {"name": "Slaying",     "conv": 2,   "type": 167, "proc": False, "kind": 50, "cond": 28, "condVal": 0.5, "mob": "any", "method": 2,
     "icon": "RedCustomize21A_Tex", "tooltip": "Increases Crit Power by $value when below 50% HP.",
     "values": [1.44, 1.52, 1.59, 1.67, 1.76, 1.84]},
    {"name": "Furious",     "conv": 4,   "type": 152, "proc": False, "kind": 0, "cond": 28, "condVal": 0.5, "mob": "all", "method": 3,
     "icon": "RedCustomize22A_Tex", "tooltip": "Increases damage by $value when below 50% HP.",
     "values": [1.051, 1.060, 1.071, 1.081, 1.091, 1.101]},
    {"name": "Focused",     "conv": 9,   "type": 167, "proc": False, "kind": 52, "cond": 26, "condVal": 4, "mob": "all", "method": 2,
     "icon": "RedCustomize04A_Tex", "tooltip": "Increases Crit Power by $value when attacking from the front.",
     "values": [1.47, 1.55, 1.64, 1.72, 1.82, 1.90]},
    # Proc: Virulent (DOT)
    {"name": "Virulent",    "conv": 11,  "type": 225, "proc": True,  "kind": 5, "cond": 1, "condVal": 2, "mob": "all", "method": 4,
     "icon": "RedCustomize19A_Tex",
     "abnorm_template": "virulent",
     "values": None},  # abnormality values used instead
    {"name": "Brutal",      "conv": 13,  "type": 152, "proc": False, "kind": 0, "cond": 21, "condVal": 2, "mob": "all", "method": 3,
     "icon": "RedCustomize11A_Tex", "tooltip": "Increases damage to knocked-down opponents by $value.",
     "values": [1.049, 1.060, 1.069, 1.079, 1.088, 1.099]},
    # Proc: Cruel (crit power buff)
    {"name": "Cruel",       "conv": 15,  "type": 208, "proc": True,  "kind": 6, "cond": 1, "condVal": 2, "mob": "all", "method": 4,
     "icon": "RedCustomize05A_Tex",
     "abnorm_template": "cruel",
     "values": None},
    # Proc: Forceful (power buff)
    {"name": "Forceful",    "conv": 17,  "type": 224, "proc": True,  "kind": 7, "cond": 1, "condVal": 2, "mob": "all", "method": 4,
     "icon": "RedCustomize12A_Tex",
     "abnorm_template": "forceful",
     "values": None},
    {"name": "Savage",      "conv": 21,  "type": 167, "proc": False, "kind": 55, "cond": 24, "condVal": 2, "mob": "all", "method": 2,
     "icon": "RedCustomize06A_Tex", "tooltip": "Increases Crit Power by $value when attacking from behind.",
     "values": [1.32, 1.39, 1.45, 1.51, 1.57, 1.63]},
    {"name": "Cunning",     "conv": 24,  "type": 2,   "proc": False, "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2,
     "judgmentOnce": False,
     "icon": "RedCustomize16A_Tex", "tooltip": "Increases maximum MP by $value.",
     "values": [134, 161, 187, 215, 241, 267]},
    # Proc: Infused (MP regen)
    {"name": "Infused",     "conv": 26,  "type": 201, "proc": True,  "kind": 8, "cond": 1, "condVal": 2, "mob": "all", "method": 2,
     "icon": "RedCustomize14A_Tex",
     "abnorm_template": "infused_w",
     "values": None},
    # Proc: Glistening (MP regen)
    {"name": "Glistening",  "conv": 28,  "type": 224, "proc": True,  "kind": 9, "cond": 1, "condVal": 2, "mob": "all", "method": 4,
     "icon": "RedCustomize13A_Tex",
     "abnorm_template": "glistening_w",
     "values": None},
    {"name": "Swift",       "conv": 30,  "type": 17,  "proc": False, "kind": 3, "cond": 0, "condVal": 0, "mob": "all", "method": 2,
     "judgmentOnce": False,
     "icon": "RedCustomize20A_Tex", "tooltip": "Increases Movement Speed by $value while in combat.",
     "values": [8, 10, 11, 14, 15, 17]},
    {"name": "Brilliant",   "conv": 32,  "type": 52,  "proc": False, "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2,
     "tickInterval": 5, "judgmentOnce": False,
     "icon": "RedCustomize15A_Tex", "tooltip": "Replenishes $value MP per $tickInterval.",
     "values": [25, 28, 32, 38, 40, 42]},
    {"name": "Carving",     "conv": 57,  "type": 155, "proc": False, "kind": 15, "cond": 25, "condVal": 0, "mob": "all", "method": 2,
     "judgmentOnce": False,
     "icon": "RedCustomize07A_Tex", "tooltip": "Increases the chance to crit by $value.",
     "values": [0.015, 0.019, 0.022, 0.025, 0.028, 0.031]},
    # Proc: Salivating (MP instant)
    {"name": "Salivating",  "conv": 59,  "type": 157, "proc": True,  "kind": 56, "cond": 25, "condVal": 3, "mob": "player", "method": 4,
     "icon": "RedCustomize17A_Tex",
     "abnorm_template": "salivating_w",
     "values": None},
    {"name": "Threatening",  "conv": 63, "type": 164, "proc": False, "kind": 61, "cond": 25, "condVal": 0, "mob": "all", "method": 3,
     "judgmentOnce": False,
     "icon": "RedCustomize18A_Tex", "tooltip": "Increases aggro by $value.",
     "values": [1.413, 1.454, 1.495, 1.537, 1.578, 1.619]},
    {"name": "Wrathful",    "conv": 100, "type": 167, "proc": False, "kind": 53, "cond": 24, "condVal": 1, "mob": "any", "method": 2,
     "icon": "RedCustomize25A_Tex", "tooltip": "Increases Crit Power by $value when attacking from the front.",
     "values": [1.40, 1.48, 1.55, 1.64, 1.72, 1.79]},
    {"name": "Spiteful",    "conv": 101, "type": 167, "proc": False, "kind": 53, "cond": 24, "condVal": 10, "mob": "any", "method": 2,
     "icon": "RedCustomize26A_Tex", "tooltip": "Increases Crit Power by $value when attacking from behind.",
     "values": [1.37, 1.44, 1.51, 1.59, 1.66, 1.73]},
]

# ---------------------------------------------------------------------------
# Armor families (11)
# ---------------------------------------------------------------------------
ARMOR_FAMILIES = [
    {"name": "Hardy",       "conv": 95,  "type": 102, "proc": False, "kind": 0, "cond": 15, "condVal": 0, "mob": "any", "method": 3,
     "icon": "BlueCustomize16A_Tex", "tooltip": "Reduces damage from monsters by $value.",
     "values": [0.959, 0.952, 0.943, 0.935, 0.927, 0.919]},
    {"name": "Protective",  "conv": 34,  "type": 105, "proc": False, "kind": 0, "cond": 17, "condVal": 0.6, "mob": "all", "method": 3,
     "icon": "BlueCustomize08A_Tex", "tooltip": "Increases the chance to resist crits by $value when below 50% HP.",
     "values": [0.951, 0.940, 0.931, 0.920, 0.911, 0.900]},
    {"name": "Resolute",    "conv": 36,  "type": 102, "proc": False, "kind": 59, "cond": 17, "condVal": 0.5, "mob": "all", "method": 3,
     "icon": "BlueCustomize09A_Tex", "tooltip": "Reduces damage taken by $value when below 50% HP.",
     "values": [0.951, 0.940, 0.931, 0.920, 0.911, 0.900]},
    {"name": "Poised",      "conv": 41,  "type": 102, "proc": False, "kind": 62, "cond": 9, "condVal": 4, "mob": "all", "method": 3,
     "icon": "BlueCustomize04A_Tex", "tooltip": "Reduces damage from enraged monsters by $value.",
     "values": [0.956, 0.946, 0.938, 0.928, 0.920, 0.910]},
    # Proc: Empyrean (shield)
    {"name": "Empyrean",    "conv": 43,  "type": 201, "proc": True,  "kind": 11, "cond": 9, "condVal": 9, "mob": "all", "method": 4,
     "icon": "BlueCustomize11A_Tex",
     "abnorm_template": "empyrean",
     "values": None},
    # Proc: Warding (shield) — prob=0.5 from vanilla
    {"name": "Warding",     "conv": 45,  "type": 201, "proc": True,  "kind": 12, "cond": 1, "condVal": 2, "mob": "all", "method": 4,
     "prob": 0.5,
     "icon": "BlueCustomize05A_Tex",
     "abnorm_template": "warding",
     "values": None},
    # Proc: Inspiring (HP regen) — prob=0.5 from vanilla
    {"name": "Inspiring",   "conv": 47,  "type": 201, "proc": True,  "kind": 13, "cond": 1, "condVal": 2, "mob": "all", "method": 4,
     "prob": 0.5,
     "icon": "BlueCustomize06A_Tex",
     "abnorm_template": "inspiring",
     "values": None},
    {"name": "Relentless",  "conv": 51,  "type": 1,   "proc": False, "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2,
     "judgmentOnce": False,
     "icon": "BlueCustomize12A_Tex", "tooltip": "Increase maximum HP by $value.",
     "values": [227, 394, 758, 1447, 2913, 5638]},
    {"name": "Fleetfoot",   "conv": 53,  "type": 18,  "proc": False, "kind": 4, "cond": 0, "condVal": 0, "mob": "all", "method": 2,
     "judgmentOnce": False,
     "icon": "BlueCustomize15A_Tex", "tooltip": "Increases Movement Speed by $value while out of combat.",
     "values": [16, 19, 22, 26, 29, 32]},
    {"name": "Vigorous",    "conv": 55,  "type": 51,  "proc": False, "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2,
     "tickInterval": 5, "judgmentOnce": False,
     "icon": "BlueCustomize13A_Tex", "tooltip": "Recovers $value HP per $tickInterval.",
     "values": [15, 26, 50, 96, 194, 376]},
    # Proc: Grieving (MP instant)
    {"name": "Grieving",    "conv": 61,  "type": 106, "proc": True,  "kind": 57, "cond": 15, "condVal": 3, "mob": "player", "method": 4,
     "icon": "BlueCustomize14A_Tex",
     "abnorm_template": "grieving_a",
     "values": None},
]

# ---------------------------------------------------------------------------
# Secondary passivities (Niveot baseline IDs)
# Weapon secondaries (from armor): 6 effects
# Armor secondaries (from weapon): 7 effects
# ---------------------------------------------------------------------------
WEAPON_SECONDARIES = [
    # Weapon secondaries use uniform config (cond=9, condVal=4, method=3, kind=0) — matches vanilla 81014-81022
    {"adverb": "Poisedly",      "name": "Poised",      "niveotId": 81008, "type": 102, "values": [0.989, 0.987, 0.985, 0.983, 0.981, 0.979], "proc": False,
     "kind": 0, "cond": 9, "condVal": 4, "mob": "all", "method": 3,
     "tooltip": "Reduces damage from enraged monsters by $value."},
    {"adverb": "Resolutely",    "name": "Resolute",     "niveotId": 81009, "type": 102, "values": [0.988, 0.986, 0.983, 0.981, 0.978, 0.976], "proc": False,
     "kind": 0, "cond": 17, "condVal": 0.5, "mob": "all", "method": 3, "judgmentOnce": False,
     "tooltip": "Reduces damage taken by $value when below 50% HP."},
    {"adverb": "Grievingly",    "name": "Grieving",     "niveotId": 81010, "type": 106, "values": None, "proc": True,
     "kind": 0, "cond": 15, "condVal": 3, "mob": "player", "method": 4},
    {"adverb": "Protectively",  "name": "Protective",   "niveotId": 81011, "type": 105, "values": [0.988, 0.986, 0.983, 0.981, 0.978, 0.976], "proc": False,
     "kind": 0, "cond": 17, "condVal": 0.6, "mob": "all", "method": 3, "judgmentOnce": False,
     "tooltip": "Increases the chance to resist crits by $value when below 50% HP."},
    {"adverb": "Relentlessly",  "name": "Relentless",   "niveotId": 81012, "type": 1,   "values": [654, 788, 906, 1040, 1174, 1308], "proc": False,
     "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2, "judgmentOnce": False,
     "tooltip": "Increase maximum HP by $value."},
    {"adverb": "Vigorously",    "name": "Vigorous",     "niveotId": 81013, "type": 51,  "values": [44, 53, 61, 70, 79, 88], "proc": False,
     "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2, "tickInterval": 5, "judgmentOnce": False,
     "tooltip": "Recovers $value HP per $tickInterval."},
]

ARMOR_SECONDARIES = [
    # Armor secondaries use type-specific configs with kind=0 — matches vanilla 81001-81013
    {"adverb": "Glisteningly",  "name": "Glistening",   "niveotId": 81001, "type": 224, "values": None, "proc": True,
     "kind": 0, "cond": 1, "condVal": 2, "mob": "all", "method": 4},
    {"adverb": "Cunningly",     "name": "Cunning",      "niveotId": 81002, "type": 2,   "values": [32, 38, 44, 50, 57, 64], "proc": False,
     "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2, "judgmentOnce": False,
     "tooltip": "Increases maximum MP by $value."},
    {"adverb": "Infusedly",     "name": "Infused",      "niveotId": 81003, "type": 201, "values": None, "proc": True,
     "kind": 0, "cond": 1, "condVal": 2, "mob": "all", "method": 2},
    {"adverb": "Salivatingly",  "name": "Salivating",   "niveotId": 81004, "type": 157, "values": None, "proc": True,
     "kind": 0, "cond": 25, "condVal": 3, "mob": "player", "method": 4},
    {"adverb": "Brutally",      "name": "Brutal",       "niveotId": 81005, "type": 152, "values": [1.012, 1.014, 1.016, 1.018, 1.021, 1.023], "proc": False,
     "kind": 0, "cond": 21, "condVal": 2, "mob": "all", "method": 3,
     "tooltip": "Increases damage to knocked-down opponents by $value."},
    {"adverb": "Brilliantly",   "name": "Brilliant",    "niveotId": 81006, "type": 52,  "values": [5, 6, 7, 8, 10, 11], "proc": False,
     "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2, "tickInterval": 5, "judgmentOnce": False,
     "tooltip": "Replenishes $value MP per $tickInterval."},
    {"adverb": "Swiftly",       "name": "Swift",        "niveotId": 81007, "type": 17,  "values": [1, 1, 1, 2, 2, 2], "proc": False,
     "kind": 0, "cond": 0, "condVal": 0, "mob": "all", "method": 2, "judgmentOnce": False,
     "tooltip": "Increases Movement Speed by $value while in combat."},
]

# ---------------------------------------------------------------------------
# Abnormality templates for proc-based families
# Each template defines the abnormality pattern + per-tier Dyad effect values
# ---------------------------------------------------------------------------
ABNORM_TEMPLATES = {
    # Weapon proc families
    "virulent": {
        "base_kind": 38401, "level": 21, "property": 2, "category": "2,13,902",
        "isBuff": False, "isShow": True, "priority": 2, "cancelCondition": 0,
        "effect_type": 51, "effect_method": 2, "tickInterval": 1,
        "time": 5000, "group": None,
        "values": [-15, -30, -75, -187, -445, -996],  # Dyad HP/tick per tier
        "min_mult": 6,  # min = value * 6 (5s/1s = 5 ticks, but value * duration/tick)
        "string_name": "Virulence", "string_tooltip": "Reduces HP by $H_W_BAD$value$COLOR_END every $H_W_BAD$tickInterval$COLOR_END.",
        "passivity_tooltip": "Crits to knocked-down opponents apply $H_W_GOODPoison {roman}$COLOR_END.",
    },
    "cruel": {
        "base_kind": 16001, "level": 21, "property": 4, "category": "4",
        "isBuff": True, "isShow": True, "priority": 2, "cancelCondition": 0,
        "effect_type": 19, "effect_method": 3, "tickInterval": 0,
        "time": 7000, "group": "skill",
        "values": [1.12, 1.14, 1.16, 1.19, 1.21, 1.23],
        "min_mult": 0,
        "string_name": "Cruelty", "string_tooltip": "Increases Crit Power.",
        "passivity_tooltip": "Increases Crit Power after knocking down an opponent. Applies $H_W_GOODCruelty {roman}$COLOR_END.",
    },
    "forceful": {
        "base_kind": 16002, "level": 21, "property": 4, "category": "4",
        "isBuff": True, "isShow": True, "priority": 1, "cancelCondition": 0,
        "effect_type": 3, "effect_method": 2, "tickInterval": 0,
        "time": 10000, "group": "skill",
        "values": [9, 12, 14, 16, 18, 20],
        "min_mult": 0,
        "string_name": "Forcefulness", "string_tooltip": "Increases Power by $H_W_GOOD$value$COLOR_END.",
        "passivity_tooltip": "Crits increase Power when attacking from behind. Applies $H_W_GOODForcefulness {roman}$COLOR_END.",
    },
    "infused_w": {
        "base_kind": 16004, "level": 21, "property": 4, "category": "4",
        "isBuff": True, "isShow": True, "priority": 1, "cancelCondition": 0,
        "effect_type": 52, "effect_method": 2, "tickInterval": 1,
        "time": 3000, "group": "skill",
        "values": [51, 56, 65, 78, 81, 83],
        "min_mult": 6,
        "string_name": "Infusion", "string_tooltip": "Replenishes $H_W_GOOD$value$COLOR_END MP every $H_W_GOOD$tickInterval$COLOR_END.",
        "passivity_tooltip": "Replenishes {total} MP when knocked down.",
    },
    "glistening_w": {
        "base_kind": 16004, "level": 21, "property": 4, "category": "4",
        "isBuff": True, "isShow": True, "priority": 1, "cancelCondition": 0,
        "effect_type": 52, "effect_method": 2, "tickInterval": 1,
        "time": 3000, "group": "skill",
        "values": [47, 51, 60, 71, 74, 81],
        "min_mult": 6,
        "string_name": "Infusion", "string_tooltip": "Replenishes $H_W_GOOD$value$COLOR_END MP every $H_W_GOOD$tickInterval$COLOR_END.",
        "passivity_tooltip": "Crits replenish {total} MP when attacking from behind.",
    },
    "salivating_w": {
        "base_kind": 16005, "level": 21, "property": 4, "category": "4",
        "isBuff": True, "isShow": False, "priority": 1, "cancelCondition": 0,
        "effect_type": 52, "effect_method": 2, "tickInterval": 1,
        "time": 1000, "group": "skill",
        "values": [43, 52, 60, 69, 77, 86],
        "min_mult": 2,
        "string_name": "Instant MP Replenishment [Crystal]", "string_tooltip": "Restores MP.",
        "passivity_tooltip": "Replenishes {total} MP when attacking a player.",
    },
    # Armor proc families
    "empyrean": {
        "base_kind": 9624, "level": 7, "property": 4, "category": "4",
        "isBuff": True, "isShow": True, "priority": 3, "cancelCondition": 9,
        "effect_type": 227, "effect_method": 0, "tickInterval": 0,
        "time": 10000, "group": "skill",
        "values": [246, 428, 821, 1568, 3156, 6108],
        "min_mult": 0,
        "string_name": "Warding", "string_tooltip": "Absorbs up to $H_W_GOOD$value$COLOR_END damage.",
        "passivity_tooltip": "Applies $H_W_GOODWarding {roman}$COLOR_END when knocked down by enraged monsters.",
    },
    "warding": {
        "base_kind": 9624, "level": 7, "property": 4, "category": "4",
        "isBuff": True, "isShow": True, "priority": 3, "cancelCondition": 9,
        "effect_type": 227, "effect_method": 0, "tickInterval": 0,
        "time": 7000, "group": "skill",
        "values": [202, 351, 673, 1287, 2590, 5012],
        "min_mult": 0,
        "string_name": "Warding", "string_tooltip": "Absorbs up to $H_W_GOOD$value$COLOR_END damage.",
        "passivity_tooltip": "Applies $H_W_GOODWarding {roman}$COLOR_END when knocked down ($prob chance).",
    },
    "inspiring": {
        "base_kind": 16003, "level": 21, "property": 4, "category": "4",
        "isBuff": True, "isShow": True, "priority": 1, "cancelCondition": 0,
        "effect_type": 51, "effect_method": 2, "tickInterval": 2,
        "time": 10000, "group": "skill",
        "values": [27, 47, 90, 171, 345, 668],
        "min_mult": 6,
        "string_name": "Restoration", "string_tooltip": "Recovers $H_W_GOOD$value$COLOR_END HP every $H_W_GOOD$tickInterval$COLOR_END.",
        "passivity_tooltip": "Applies $H_W_GOODHP Recovery {roman}$COLOR_END when knocked down ($prob chance).",
    },
    "grieving_a": {
        "base_kind": 16006, "level": 21, "property": 4, "category": "4",
        "isBuff": True, "isShow": False, "priority": 1, "cancelCondition": 0,
        "effect_type": 52, "effect_method": 2, "tickInterval": 1,
        "time": 1000, "group": "skill",
        "values": [56, 68, 79, 90, 101, 113],
        "min_mult": 2,
        "string_name": "Instant MP Replenishment [Crystal]", "string_tooltip": "Restores MP.",
        "passivity_tooltip": "Replenishes {total} MP when attacked by a player.",
    },
}

# Proc family ordering for abnormality ID allocation (6 weapon + 4 armor = 10)
PROC_FAMILIES_ORDER = [
    "virulent", "cruel", "forceful", "infused_w", "glistening_w", "salivating_w",
    "empyrean", "warding", "inspiring", "grieving_a",
]

# ---------------------------------------------------------------------------
# Helper: format a numeric value for YAML (avoid trailing zeros for floats)
# ---------------------------------------------------------------------------
def fmt(v):
    if isinstance(v, float):
        s = f"{v:.6f}".rstrip("0").rstrip(".")
        # Ensure at least one decimal for floats that are whole numbers
        if "." not in s:
            s += ".0"
        return s
    return str(v)


# ---------------------------------------------------------------------------
# Compute all IDs
# ---------------------------------------------------------------------------
def compute_ids():
    """Compute all ID allocations and return lookup dictionaries."""
    data = {}

    # Primary passivities: 31 per tier (20 weapon + 11 armor)
    data["primary_pass"] = {}
    for ti, t in enumerate(TIERS):
        tier_base = PRIMARY_PASS_BASE + ti * 31
        wp = {}
        for fi, fam in enumerate(WEAPON_FAMILIES):
            wp[fam["name"]] = tier_base + fi
        ap = {}
        for fi, fam in enumerate(ARMOR_FAMILIES):
            ap[fam["name"]] = tier_base + 20 + fi
        data["primary_pass"][t["num"]] = {"weapon": wp, "armor": ap}

    # Secondary passivities: 9 non-proc per tier
    data["secondary_pass"] = {}
    non_proc_weapon_secs = [s for s in WEAPON_SECONDARIES if not s["proc"]]
    non_proc_armor_secs = [s for s in ARMOR_SECONDARIES if not s["proc"]]
    all_non_proc = non_proc_weapon_secs + non_proc_armor_secs  # 5 + 4 = 9
    for ti, t in enumerate(TIERS):
        tier_base = SECONDARY_PASS_BASE + ti * 9
        sp = {}
        for si, sec in enumerate(all_non_proc):
            sp[sec["name"]] = tier_base + si
        data["secondary_pass"][t["num"]] = sp

    # Abnormalities: 10 per tier
    data["abnorm"] = {}
    for ti, t in enumerate(TIERS):
        tier_base = ABNORM_BASE + ti * 10
        ab = {}
        for pi, pf in enumerate(PROC_FAMILIES_ORDER):
            ab[pf] = tier_base + pi
        data["abnorm"][t["num"]] = ab

    return data


def get_secondary_pass_id(tier_num, sec_name, ids_data):
    """Get secondary passivity ID for a given tier and secondary name.
    Proc-based secondaries use Niveot IDs at all tiers."""
    # Check weapon secondaries
    for s in WEAPON_SECONDARIES:
        if s["name"] == sec_name:
            if s["proc"]:
                return s["niveotId"]
            return ids_data["secondary_pass"][tier_num].get(sec_name)
    # Check armor secondaries
    for s in ARMOR_SECONDARIES:
        if s["name"] == sec_name:
            if s["proc"]:
                return s["niveotId"]
            return ids_data["secondary_pass"][tier_num].get(sec_name)
    raise ValueError(f"Unknown secondary: {sec_name}")


# ---------------------------------------------------------------------------
# Generator: Dyad Structure Items + RawStoneItem entries
# ---------------------------------------------------------------------------
def gen_structures():
    lines = []
    lines.append("# Dyad Crystal Structures — Patch 001")
    lines.append("# Dyad/Smart Dyad structures (UPGRADE) + Rhomb Structure (TIERUP)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")

    # Imports
    lines.append("imports:")
    lines.append("  - from: crystals")
    lines.append("    use:")
    lines.append("      variables:")
    for t in TIERS:
        tn = t["name"].upper()
        lines.append(f"        - DYAD_{tn}_STRUCTURE")
        lines.append(f"        - SMART_DYAD_{tn}_STRUCTURE")
    lines.append("        - RHOMB_STRUCTURE")
    lines.append("")

    # Definitions
    lines.append("definitions:")
    lines.append("  dyadStructureBase:")
    lines.append("    name: RawStone")
    lines.append("    combatItemType: RAWSTONE")
    lines.append("    combatItemSubType: generalMaterial")
    lines.append("    category: generalMaterial")
    lines.append("    rank: 0")
    lines.append("    sortingNumber: 1")
    lines.append("    maxStack: 100")
    lines.append("    maxDropUnit: 100")
    lines.append("    slotLimit: 0")
    lines.append("    coolTimeGroup: 0")
    lines.append("    tradable: false")
    lines.append("    warehouseStorable: true")
    lines.append("    guildWarehouseStorable: false")
    lines.append("    boundType: None")
    lines.append("    destroyable: true")
    lines.append("    storeSellable: true")
    lines.append("    searchable: true")
    lines.append("    obtainable: true")
    lines.append("    relocatable: true")
    lines.append("    enchantEnable: false")
    lines.append("    dismantlable: false")
    lines.append("    artisanable: false")
    lines.append("    requiredEquipmentType: NO_COMBAT")
    lines.append("    requiredLevel: 1")
    lines.append("    dropSilhouette: DropItem.SM.Item_Drop_Chest_SM")
    lines.append("    dropSound: InterfaceSound.Drop_ItemCUE.Drop_ChestBoxCue")
    lines.append("    equipSound: InterfaceSound.Equip_ItemCUE.Equip_CustomizeStoneCue")
    lines.append("")

    # Items
    lines.append("items:")
    lines.append("  upsert:")

    for t in TIERS:
        tn = t["name"].upper()
        tname = t["name"]
        icon = f"Icon_Items.RawCrystal01{t['icon_suffix']}_Tex"

        # Dyad Structure
        lines.append(f"    - id: $DYAD_{tn}_STRUCTURE")
        lines.append("      $extends: dyadStructureBase")
        lines.append("      rareGrade: 2")
        lines.append(f"      level: {t['level']}")
        lines.append(f"      buyPrice: {t['buy']}")
        lines.append(f"      sellPrice: {t['sell']}")
        lines.append(f"      defaultValue: {t['buy']}")
        lines.append(f"      linkRawStoneId: $DYAD_{tn}_STRUCTURE")
        lines.append(f"      icon: {icon}")
        lines.append("      strings:")
        lines.append(f'        name: "Dyad {tname} Structure"')
        lines.append(f'        toolTip: "Fuse 3 fine {tname.lower()} crystals to produce a random dyad {tname.lower()}.\\nSuccess Rate: 100%"')

        # Smart Dyad Structure
        lines.append(f"    - id: $SMART_DYAD_{tn}_STRUCTURE")
        lines.append("      $extends: dyadStructureBase")
        lines.append("      rareGrade: 3")
        lines.append(f"      level: {t['level']}")
        lines.append(f"      buyPrice: {t['buy'] * 3}")
        lines.append(f"      sellPrice: {t['sell'] * 3}")
        lines.append(f"      defaultValue: {t['buy'] * 3}")
        lines.append(f"      linkRawStoneId: $SMART_DYAD_{tn}_STRUCTURE")
        lines.append(f"      icon: {icon}")
        lines.append("      strings:")
        lines.append(f'        name: "Smart Dyad {tname} Structure"')
        lines.append(f'        toolTip: "Fuse 3 fine {tname.lower()} crystals of the same type to produce a dyad {tname.lower()} preserving the primary effect.\\nSuccess Rate: 100%"')

    # Rhomb Structure (TIERUP)
    lines.append("    - id: $RHOMB_STRUCTURE")
    lines.append("      $extends: dyadStructureBase")
    lines.append("      rareGrade: 1")
    lines.append("      tradable: true")
    lines.append("      guildWarehouseStorable: true")
    lines.append("      level: 1")
    lines.append("      buyPrice: 200")
    lines.append("      sellPrice: 20")
    lines.append("      defaultValue: 200")
    lines.append("      linkRawStoneId: $RHOMB_STRUCTURE")
    lines.append("      icon: Icon_Items.RawCrystal01A_Tex")
    lines.append("      strings:")
    lines.append('        name: "Rhomb Structure"')
    lines.append('        toolTip: "Fuse 3 fine rhomb crystals to produce a random fine cabochon.\\nSuccess Rate: 100%"')
    lines.append("")

    # RawStoneItem entries
    lines.append("rawStoneItems:")
    lines.append("  upsert:")

    for t in TIERS:
        tn = t["name"].upper()
        grade = t["grade"]

        # Dyad Structure (random output)
        lines.append(f"    # Dyad {t['name']} — 3x Fine {t['name']} (rareGrade 1) → Random Dyad {t['name']}")
        lines.append(f"    - rawStoneItemId: $DYAD_{tn}_STRUCTURE")
        lines.append("      type: UPGRADE")
        lines.append("      useGambleItemGrade:")
        lines.append(f"        - {grade}")
        lines.append("      useRareGrade: 1")
        lines.append("      useEquipmentType:")
        lines.append("        - EQUIP_WEAPON")
        lines.append("        - EQUIP_ARMOR_BODY")
        lines.append("      rate: 1.0")
        lines.append("      succeedRate: 0")
        lines.append("      needSameMaterial: false")

        # Smart Dyad Structure (same-type output)
        lines.append(f"    # Smart Dyad {t['name']} — 3x Same Fine {t['name']} (rareGrade 1) → Same-type Dyad {t['name']}")
        lines.append(f"    - rawStoneItemId: $SMART_DYAD_{tn}_STRUCTURE")
        lines.append("      type: UPGRADE")
        lines.append("      useGambleItemGrade:")
        lines.append(f"        - {grade}")
        lines.append("      useRareGrade: 1")
        lines.append("      useEquipmentType:")
        lines.append("        - EQUIP_WEAPON")
        lines.append("        - EQUIP_ARMOR_BODY")
        lines.append("      rate: 1.0")
        lines.append("      succeedRate: 1")
        lines.append("      needSameMaterial: true")

    # Rhomb Structure TIERUP
    lines.append("    # Rhomb Structure (TIERUP) — 3x Fine Rhomb → Fine Cabochon")
    lines.append("    - rawStoneItemId: $RHOMB_STRUCTURE")
    lines.append("      type: TIERUP")
    lines.append("      useGambleItemGrade:")
    lines.append("        - 1")
    lines.append("      useRareGrade: 1")
    lines.append("      useEquipmentType:")
    lines.append("        - EQUIP_WEAPON")
    lines.append("        - EQUIP_ARMOR_BODY")
    lines.append("      rate: 1.0")
    lines.append("      succeedRate: 0")
    lines.append("      needSameMaterial: false")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Helper: compute proc passivity tooltip from abnormality template
# ---------------------------------------------------------------------------
def proc_tooltip(tmpl_key, ti, tier_roman):
    """Build tooltip for a proc passivity from its abnormality template."""
    tmpl = ABNORM_TEMPLATES[tmpl_key]
    tooltip_fmt = tmpl["passivity_tooltip"]
    if "{total}" in tooltip_fmt:
        tick_s = tmpl["tickInterval"]
        ticks = (tmpl["time"] / 1000) / tick_s if tick_s > 0 else 1
        total = int(abs(tmpl["values"][ti]) * ticks)
        return tooltip_fmt.format(total=total)
    return tooltip_fmt.format(roman=tier_roman)


# ---------------------------------------------------------------------------
# Generator: Primary + Secondary Passivities
# ---------------------------------------------------------------------------
def gen_passivities(ids_data):
    lines = []
    lines.append("# Dyad Crystal Passivities — Patch 001")
    lines.append("# Primary passivities (186) + Secondary passivities (54)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")
    lines.append("passivities:")
    lines.append("  upsert:")

    # Primary passivities
    lines.append("    # ========== PRIMARY PASSIVITIES ==========")

    for ti, t in enumerate(TIERS):
        tier_num = t["num"]
        tier_name = t["name"]
        tier_roman = ["I", "II", "III", "IV", "V", "VI"][ti]
        lines.append(f"    # --- Tier {tier_num} ({tier_name}) ---")

        # Weapon primaries
        for fi, fam in enumerate(WEAPON_FAMILIES):
            pid = ids_data["primary_pass"][tier_num]["weapon"][fam["name"]]
            lines.append(f"    - id: {pid}")
            lines.append(f'      name: "Dyad_{fam["name"]}_{tier_name}"')
            lines.append("      category: Equipment")

            if fam["proc"]:
                tmpl = fam["abnorm_template"]
                abnorm_id = ids_data["abnorm"][tier_num][tmpl]
                lines.append(f"      kind: {fam['kind']}")
                lines.append(f"      judgmentOnce: {str(fam.get('judgmentOnce', True)).lower()}")
                lines.append("      balancedByTargetCount: false")

                lines.append(f"      type: {fam['type']}")
                lines.append(f"      value: {abnorm_id}")
                lines.append(f"      tickInterval: {fam.get('tickInterval', 0)}")
                lines.append(f"      method: {fam['method']}")
                lines.append(f"      prob: {fam.get('prob', 1)}")
                lines.append(f'      mobSize: {fam["mob"]}')
                lines.append(f"      condition: {fam['cond']}")
                lines.append(f"      conditionValue: {fam['condVal']}")
                lines.append("      conditionCategory: 0")
                lines.append("      abnormalityKind: 0")
                lines.append("      abnormalityCategory: 0")
            else:
                val = fam["values"][ti]
                lines.append(f"      kind: {fam['kind']}")
                lines.append(f"      judgmentOnce: {str(fam.get('judgmentOnce', True)).lower()}")
                lines.append("      balancedByTargetCount: false")

                lines.append(f"      type: {fam['type']}")
                lines.append(f"      value: {fmt(val)}")
                lines.append(f"      tickInterval: {fam.get('tickInterval', 0)}")
                lines.append(f"      method: {fam['method']}")
                lines.append(f"      prob: {fam.get('prob', 1)}")
                lines.append(f'      mobSize: {fam["mob"]}')
                lines.append(f"      condition: {fam['cond']}")
                lines.append(f"      conditionValue: {fam['condVal']}")
                lines.append("      conditionCategory: 0")
                lines.append("      abnormalityKind: 0")
                lines.append("      abnormalityCategory: 0")

            lines.append("      passivityStrings:")
            lines.append(f'        name: "First Effect - {fam["name"]} {tier_roman}"')
            if fam["proc"]:
                tt = proc_tooltip(fam["abnorm_template"], ti, tier_roman)
            else:
                tt = fam["tooltip"]
            lines.append(f'        tooltip: "{tt}"')

        # Armor primaries
        for fi, fam in enumerate(ARMOR_FAMILIES):
            pid = ids_data["primary_pass"][tier_num]["armor"][fam["name"]]
            lines.append(f"    - id: {pid}")
            lines.append(f'      name: "Dyad_{fam["name"]}_{tier_name}"')
            lines.append("      category: Equipment")

            if fam["proc"]:
                tmpl = fam["abnorm_template"]
                abnorm_id = ids_data["abnorm"][tier_num][tmpl]
                lines.append(f"      kind: {fam['kind']}")
                lines.append(f"      judgmentOnce: {str(fam.get('judgmentOnce', True)).lower()}")
                lines.append("      balancedByTargetCount: false")

                lines.append(f"      type: {fam['type']}")
                lines.append(f"      value: {abnorm_id}")
                lines.append(f"      tickInterval: {fam.get('tickInterval', 0)}")
                lines.append(f"      method: {fam['method']}")
                lines.append(f"      prob: {fam.get('prob', 1)}")
                lines.append(f'      mobSize: {fam["mob"]}')
                lines.append(f"      condition: {fam['cond']}")
                lines.append(f"      conditionValue: {fam['condVal']}")
                lines.append("      conditionCategory: 0")
                lines.append("      abnormalityKind: 0")
                lines.append("      abnormalityCategory: 0")
            else:
                val = fam["values"][ti]
                lines.append(f"      kind: {fam['kind']}")
                lines.append(f"      judgmentOnce: {str(fam.get('judgmentOnce', True)).lower()}")
                lines.append("      balancedByTargetCount: false")

                lines.append(f"      type: {fam['type']}")
                lines.append(f"      value: {fmt(val)}")
                lines.append(f"      tickInterval: {fam.get('tickInterval', 0)}")
                lines.append(f"      method: {fam['method']}")
                lines.append(f"      prob: {fam.get('prob', 1)}")
                lines.append(f'      mobSize: {fam["mob"]}')
                lines.append(f"      condition: {fam['cond']}")
                lines.append(f"      conditionValue: {fam['condVal']}")
                lines.append("      conditionCategory: 0")
                lines.append("      abnormalityKind: 0")
                lines.append("      abnormalityCategory: 0")

            lines.append("      passivityStrings:")
            lines.append(f'        name: "First Effect - {fam["name"]} {tier_roman}"')
            if fam["proc"]:
                tt = proc_tooltip(fam["abnorm_template"], ti, tier_roman)
            else:
                tt = fam["tooltip"]
            lines.append(f'        tooltip: "{tt}"')

    # Secondary passivities (non-proc only)
    lines.append("    # ========== SECONDARY PASSIVITIES ==========")

    non_proc_weapon_secs = [s for s in WEAPON_SECONDARIES if not s["proc"]]
    non_proc_armor_secs = [s for s in ARMOR_SECONDARIES if not s["proc"]]
    all_non_proc = non_proc_weapon_secs + non_proc_armor_secs

    for ti, t in enumerate(TIERS):
        tier_num = t["num"]
        tier_name = t["name"]
        tier_roman = ["I", "II", "III", "IV", "V", "VI"][ti]
        lines.append(f"    # --- Secondary Tier {tier_num} ({tier_name}) ---")

        for si, sec in enumerate(all_non_proc):
            pid = ids_data["secondary_pass"][tier_num][sec["name"]]
            val = sec["values"][ti]
            lines.append(f"    - id: {pid}")
            lines.append(f'      name: "DyadSec_{sec["name"]}_{tier_name}"')
            lines.append("      category: Equipment")
            lines.append(f"      kind: {sec['kind']}")
            lines.append(f"      judgmentOnce: {str(sec.get('judgmentOnce', True)).lower()}")
            lines.append("      balancedByTargetCount: false")
            lines.append(f"      type: {sec['type']}")
            lines.append(f"      value: {fmt(val)}")
            lines.append(f"      tickInterval: {sec.get('tickInterval', 0)}")
            lines.append(f"      method: {sec['method']}")
            lines.append(f"      prob: {sec.get('prob', 1)}")
            lines.append(f'      mobSize: {sec["mob"]}')
            lines.append(f"      condition: {sec['cond']}")
            lines.append(f"      conditionValue: {sec['condVal']}")
            lines.append("      conditionCategory: 0")
            lines.append("      abnormalityKind: 0")
            lines.append("      abnormalityCategory: 0")
            lines.append("      passivityStrings:")
            lines.append(f'        name: "Second Effect - {sec["name"]} {tier_roman}"')
            lines.append(f'        tooltip: "{sec["tooltip"]}"')

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generator: Abnormalities for proc-based families
# ---------------------------------------------------------------------------
def gen_abnormalities(ids_data):
    lines = []
    lines.append("# Dyad Crystal Abnormalities — Patch 001")
    lines.append("# Proc-based primary effects (60 total: 10 families x 6 tiers)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")
    lines.append("abnormalities:")
    lines.append("  upsert:")

    for ti, t in enumerate(TIERS):
        tier_num = t["num"]
        tier_name = t["name"]
        tier_roman = ["I", "II", "III", "IV", "V", "VI"][ti]
        lines.append(f"    # --- Tier {tier_num} ({tier_name}) ---")

        for pf_key in PROC_FAMILIES_ORDER:
            tmpl = ABNORM_TEMPLATES[pf_key]
            aid = ids_data["abnorm"][tier_num][pf_key]
            val = tmpl["values"][ti]

            lines.append(f"    - id: {aid}")
            lines.append(f'      name: "Dyad_{pf_key}_{tier_name}"')
            lines.append(f"      kind: {tmpl['base_kind']}")
            lines.append(f"      level: {tmpl['level']}")
            lines.append(f"      property: {tmpl['property']}")
            lines.append(f'      category: "{tmpl["category"]}"')
            lines.append(f"      time: {tmpl['time']}")
            lines.append("      cancelCondition: " + str(tmpl["cancelCondition"]))
            lines.append("      cancelConditionValue: 0")
            lines.append("      cancelConditionProb: 1")
            lines.append("      mobSize: all")
            lines.append("      bySkillCategory: 0")
            lines.append(f"      priority: {tmpl['priority']}")
            lines.append("      maxStackCount: 1")
            lines.append("      isBuff: " + str(tmpl["isBuff"]).lower())
            lines.append('      isShow: "' + str(tmpl["isShow"]) + '"')
            lines.append("      notCareBattleField: true")
            if tmpl["group"]:
                lines.append(f"      group: {tmpl['group']}")

            # Effect
            eff_min = 0
            eff_max = 0
            if tmpl["min_mult"] > 0:
                eff_min = val * tmpl["min_mult"] if val < 0 else 0
                eff_max = 0 if val < 0 else val * tmpl["min_mult"]

            lines.append("      effects:")
            lines.append(f"        - type: {tmpl['effect_type']}")
            lines.append(f"          method: {tmpl['effect_method']}")
            lines.append(f'          value: "{fmt(val)}"')
            lines.append(f"          tickInterval: {tmpl['tickInterval']}")
            lines.append("          variation: 0")
            lines.append(f"          min: {fmt(eff_min)}")
            lines.append(f"          max: {fmt(eff_max)}")

            lines.append("      abnormalityStrings:")
            lines.append(f'        name: "{tmpl["string_name"]} {tier_roman}"')
            lines.append(f'        tooltip: "{tmpl["string_tooltip"]}"')

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generator: CustomizingItem entries
# ---------------------------------------------------------------------------
def gen_customizing_items(ids_data):
    lines = []
    lines.append("# Dyad Crystal CustomizingItem Entries — Patch 001")
    lines.append("# 1,182 entries (6 tiers x (120 weapon + 77 armor))")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")
    lines.append("customizingItems:")
    lines.append("  upsert:")

    for ti, t in enumerate(TIERS):
        tier_num = t["num"]
        tier_name = t["name"]
        lines.append(f"    # === Tier {tier_num} ({tier_name}) Weapon ===")

        for fi, fam in enumerate(WEAPON_FAMILIES):
            primary_pid = ids_data["primary_pass"][tier_num]["weapon"][fam["name"]]
            for si, sec in enumerate(WEAPON_SECONDARIES):
                cust_id = WEAPON_CUST_BASES[tier_num] + fi * 6 + si
                sec_pid = get_secondary_pass_id(tier_num, sec["name"], ids_data)
                lines.append(f"    - id: {cust_id}")
                lines.append("      destroyProbOnDead: 0.0")
                lines.append("      destroyProbOnDetach: 0")
                lines.append("      takeSlot: 1")
                lines.append("      isArtifact: 1")
                lines.append(f'      passivityLink: "{primary_pid};{sec_pid}"')

        lines.append(f"    # === Tier {tier_num} ({tier_name}) Armor ===")

        for fi, fam in enumerate(ARMOR_FAMILIES):
            primary_pid = ids_data["primary_pass"][tier_num]["armor"][fam["name"]]
            for si, sec in enumerate(ARMOR_SECONDARIES):
                cust_id = ARMOR_CUST_BASES[tier_num] + fi * 7 + si
                sec_pid = get_secondary_pass_id(tier_num, sec["name"], ids_data)
                lines.append(f"    - id: {cust_id}")
                lines.append("      destroyProbOnDead: 0.0")
                lines.append("      destroyProbOnDetach: 0")
                lines.append("      takeSlot: 1")
                lines.append("      isArtifact: 1")
                lines.append(f'      passivityLink: "{primary_pid};{sec_pid}"')

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generator: CustomizingItemBag entries
# ---------------------------------------------------------------------------
def gen_customizing_bags(ids_data):
    lines = []
    lines.append("# Dyad Crystal CustomizingItemBag Entries — Patch 001")
    lines.append("# 12 bags (6 tiers x 2 equipment types)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")
    lines.append("customizingItemBags:")
    lines.append("  upsert:")

    for ti, t in enumerate(TIERS):
        tier_num = t["num"]
        tier_name = t["name"]
        grade = t["grade"]

        # Weapon bag
        lines.append(f"    # --- Tier {tier_num} ({tier_name}) Weapon ---")
        lines.append("    - requiredEquipmentType: EQUIP_WEAPON")
        lines.append(f"      gambleItemGrade: {grade}")
        lines.append("      rareGrade: 2")
        lines.append("      bagItems:")

        for fi, fam in enumerate(WEAPON_FAMILIES):
            # Collect all 6 variant item IDs for this family
            item_ids = []
            for si in range(6):
                item_ids.append(str(WEAPON_ITEM_BASES[tier_num] + fi * 6 + si))
            template_str = ";".join(item_ids)
            lines.append(f"        - conversionSmallGroup: {fam['conv']}")
            lines.append(f'          templateId: "{template_str}"')
            lines.append(f'          name: "{fam["name"]}"')

        # Armor bag
        lines.append(f"    # --- Tier {tier_num} ({tier_name}) Armor ---")
        lines.append("    - requiredEquipmentType: EQUIP_ARMOR_BODY")
        lines.append(f"      gambleItemGrade: {grade}")
        lines.append("      rareGrade: 2")
        lines.append("      bagItems:")

        for fi, fam in enumerate(ARMOR_FAMILIES):
            item_ids = []
            for si in range(7):
                item_ids.append(str(ARMOR_ITEM_BASES[tier_num] + fi * 7 + si))
            template_str = ";".join(item_ids)
            lines.append(f"        - conversionSmallGroup: {fam['conv']}")
            lines.append(f'          templateId: "{template_str}"')
            lines.append(f'          name: "{fam["name"]}"')

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generator: Dyad Crystal Items (weapon, per tier)
# ---------------------------------------------------------------------------
def gen_crystal_items_weapon(tier_idx, ids_data):
    t = TIERS[tier_idx]
    tier_num = t["num"]
    tier_name = t["name"]

    lines = []
    lines.append(f"# Dyad Weapon Crystals — Tier {tier_num} ({tier_name})")
    lines.append(f"# 120 items (20 families x 6 secondary variants)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")

    # Item base envelope lives in the dyad-crystal-items package.
    lines.append("imports:")
    lines.append("  - from: dyad-crystal-items")
    lines.append("")

    lines.append("items:")
    lines.append("  upsert:")

    for fi, fam in enumerate(WEAPON_FAMILIES):
        for si, sec in enumerate(WEAPON_SECONDARIES):
            item_id = WEAPON_ITEM_BASES[tier_num] + fi * 6 + si
            cust_id = WEAPON_CUST_BASES[tier_num] + fi * 6 + si
            crystal_name = f"{sec['adverb']} {fam['name']} {tier_name}"
            internal_name = f"Artifact_T{tier_num}_{fam['name']}_{sec['name']}"

            tier_icon = fam['icon'].replace('A_Tex', f'{t["icon_suffix"]}_Tex')
            lines.append(f"    - id: {item_id}")
            lines.append(f"      $extends: DyadWeapon{tier_name}Base")
            lines.append(f"      name: {internal_name}")
            lines.append(f"      linkCustomizingId: {cust_id}")
            lines.append(f"      conversionSmallGroup: {fam['conv']}")
            lines.append(f"      icon: Icon_Items.{tier_icon}")
            lines.append("      strings:")
            lines.append(f'        name: "{crystal_name}"')

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generator: Dyad Crystal Items (armor, per tier)
# ---------------------------------------------------------------------------
def gen_crystal_items_armor(tier_idx, ids_data):
    t = TIERS[tier_idx]
    tier_num = t["num"]
    tier_name = t["name"]

    lines = []
    lines.append(f"# Dyad Armor Crystals — Tier {tier_num} ({tier_name})")
    lines.append(f"# 77 items (11 families x 7 secondary variants)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")

    # Item base envelope lives in the dyad-crystal-items package.
    lines.append("imports:")
    lines.append("  - from: dyad-crystal-items")
    lines.append("")

    lines.append("items:")
    lines.append("  upsert:")

    for fi, fam in enumerate(ARMOR_FAMILIES):
        for si, sec in enumerate(ARMOR_SECONDARIES):
            item_id = ARMOR_ITEM_BASES[tier_num] + fi * 7 + si
            cust_id = ARMOR_CUST_BASES[tier_num] + fi * 7 + si
            crystal_name = f"{sec['adverb']} {fam['name']} {tier_name}"
            internal_name = f"Artifact_T{tier_num}_{fam['name']}_{sec['name']}"

            tier_icon = fam['icon'].replace('A_Tex', f'{t["icon_suffix"]}_Tex')
            lines.append(f"    - id: {item_id}")
            lines.append(f"      $extends: DyadArmor{tier_name}Base")
            lines.append(f"      name: {internal_name}")
            lines.append(f"      linkCustomizingId: {cust_id}")
            lines.append(f"      conversionSmallGroup: {fam['conv']}")
            lines.append(f"      icon: Icon_Items.{tier_icon}")
            lines.append("      strings:")
            lines.append(f'        name: "{crystal_name}"')

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generator: Package files
# ---------------------------------------------------------------------------
def gen_pkg_structures():
    lines = []
    lines.append("# Crystal Structure IDs")
    lines.append("# Vanilla fusion structures + Dyad structures + Rhomb Structure")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("")
    lines.append("variables:")
    lines.append("  # --- Vanilla Fusion Structures (TIERUP: 3x Fine tier N → Fine tier N+1) ---")
    lines.append("  EMPTY_RHOMB_STRUCTURE: 96100")
    lines.append("  CABOCHON_STRUCTURE: 96102")
    lines.append("  HEXAGE_STRUCTURE: 96103")
    lines.append("  PENTANT_STRUCTURE: 96104")
    lines.append("  CONCACH_STRUCTURE: 96105")
    lines.append("  CRUX_STRUCTURE: 96106")
    lines.append("  NIVEOT_STRUCTURE: 96107")
    lines.append("  SMART_DYAD_NIVEOT_STRUCTURE: 96206")
    lines.append("  DYAD_NIVEOT_STRUCTURE: 96207")
    lines.append("")
    lines.append("  # --- Dyad Structures (UPGRADE: 3x Fine tier N → Random Dyad tier N) ---")
    for t in TIERS:
        tn = t["name"].upper()
        lines.append(f"  DYAD_{tn}_STRUCTURE: {DYAD_STRUCTURE_IDS[t['num']]}")
    lines.append("")
    lines.append("  # --- Smart Dyad Structures (UPGRADE: 3x Same Fine tier N → Same Dyad tier N) ---")
    for t in TIERS:
        tn = t["name"].upper()
        lines.append(f"  SMART_DYAD_{tn}_STRUCTURE: {SMART_DYAD_STRUCTURE_IDS[t['num']]}")
    lines.append("")
    lines.append("  # --- Rhomb Structure (TIERUP: 3x Fine Rhomb → Fine Cabochon) ---")
    lines.append(f"  RHOMB_STRUCTURE: {RHOMB_STRUCTURE_ID}")
    lines.append("")

    # ALL_STRUCTURE_IDS
    all_ids = [96100, 96102, 96103, 96104, 96105, 96106, 96107, 96206, 96207]
    for t in TIERS:
        all_ids.append(DYAD_STRUCTURE_IDS[t["num"]])
    for t in TIERS:
        all_ids.append(SMART_DYAD_STRUCTURE_IDS[t["num"]])
    all_ids.append(RHOMB_STRUCTURE_ID)

    lines.append("  ALL_STRUCTURE_IDS:")
    for sid in all_ids:
        lines.append(f"    - {sid}")
    lines.append("")

    # Exports
    lines.append("exports:")
    lines.append("  variables:")
    lines.append("    - EMPTY_RHOMB_STRUCTURE")
    lines.append("    - CABOCHON_STRUCTURE")
    lines.append("    - HEXAGE_STRUCTURE")
    lines.append("    - PENTANT_STRUCTURE")
    lines.append("    - CONCACH_STRUCTURE")
    lines.append("    - CRUX_STRUCTURE")
    lines.append("    - NIVEOT_STRUCTURE")
    lines.append("    - SMART_DYAD_NIVEOT_STRUCTURE")
    lines.append("    - DYAD_NIVEOT_STRUCTURE")
    for t in TIERS:
        tn = t["name"].upper()
        lines.append(f"    - DYAD_{tn}_STRUCTURE")
    for t in TIERS:
        tn = t["name"].upper()
        lines.append(f"    - SMART_DYAD_{tn}_STRUCTURE")
    lines.append("    - RHOMB_STRUCTURE")
    lines.append("    - ALL_STRUCTURE_IDS")

    return "\n".join(lines) + "\n"


def gen_pkg_dyad_weapon():
    """Generate dyad-weapon.yml package file with all Dyad weapon crystal IDs."""
    lines = []
    lines.append("# Dyad Weapon Crystal IDs")
    lines.append("# 720 items (6 tiers x 20 families x 6 variants)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("")
    lines.append("variables:")

    for t in TIERS:
        tier_num = t["num"]
        tier_name = t["name"]
        tn = tier_name.upper()
        lines.append(f"  # --- Tier {tier_num} ({tier_name}) ---")

        tier_ids = []
        for fi, fam in enumerate(WEAPON_FAMILIES):
            fn = fam["name"].upper()
            for si, sec in enumerate(WEAPON_SECONDARIES):
                item_id = WEAPON_ITEM_BASES[tier_num] + fi * 6 + si
                sn = sec["name"].upper()
                var_name = f"DYAD_{fn}_{sn}_{tn}"
                lines.append(f"  {var_name}: {item_id}")
                tier_ids.append(item_id)

        # Tier list variable
        lines.append(f"  DYAD_WEAPON_{tn}_IDS:")
        for iid in tier_ids:
            lines.append(f"    - {iid}")
        lines.append("")

    # All weapon IDs
    lines.append("  DYAD_WEAPON_ALL_IDS:")
    for t in TIERS:
        tier_num = t["num"]
        for fi in range(len(WEAPON_FAMILIES)):
            for si in range(6):
                item_id = WEAPON_ITEM_BASES[tier_num] + fi * 6 + si
                lines.append(f"    - {item_id}")
    lines.append("")

    # Exports
    lines.append("exports:")
    lines.append("  variables:")
    for t in TIERS:
        tier_num = t["num"]
        tn = t["name"].upper()
        for fi, fam in enumerate(WEAPON_FAMILIES):
            fn = fam["name"].upper()
            for si, sec in enumerate(WEAPON_SECONDARIES):
                sn = sec["name"].upper()
                lines.append(f"    - DYAD_{fn}_{sn}_{tn}")
        lines.append(f"    - DYAD_WEAPON_{tn}_IDS")
    lines.append("    - DYAD_WEAPON_ALL_IDS")

    return "\n".join(lines) + "\n"


def gen_pkg_dyad_armor():
    """Generate dyad-armor.yml package file."""
    lines = []
    lines.append("# Dyad Armor Crystal IDs")
    lines.append("# 462 items (6 tiers x 11 families x 7 variants)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("")
    lines.append("variables:")

    for t in TIERS:
        tier_num = t["num"]
        tier_name = t["name"]
        tn = tier_name.upper()
        lines.append(f"  # --- Tier {tier_num} ({tier_name}) ---")

        tier_ids = []
        for fi, fam in enumerate(ARMOR_FAMILIES):
            fn = fam["name"].upper()
            for si, sec in enumerate(ARMOR_SECONDARIES):
                item_id = ARMOR_ITEM_BASES[tier_num] + fi * 7 + si
                sn = sec["name"].upper()
                var_name = f"DYAD_{fn}_{sn}_{tn}"
                lines.append(f"  {var_name}: {item_id}")
                tier_ids.append(item_id)

        lines.append(f"  DYAD_ARMOR_{tn}_IDS:")
        for iid in tier_ids:
            lines.append(f"    - {iid}")
        lines.append("")

    lines.append("  DYAD_ARMOR_ALL_IDS:")
    for t in TIERS:
        tier_num = t["num"]
        for fi in range(len(ARMOR_FAMILIES)):
            for si in range(7):
                item_id = ARMOR_ITEM_BASES[tier_num] + fi * 7 + si
                lines.append(f"    - {item_id}")
    lines.append("")

    lines.append("exports:")
    lines.append("  variables:")
    for t in TIERS:
        tier_num = t["num"]
        tn = t["name"].upper()
        for fi, fam in enumerate(ARMOR_FAMILIES):
            fn = fam["name"].upper()
            for si, sec in enumerate(ARMOR_SECONDARIES):
                sn = sec["name"].upper()
                lines.append(f"    - DYAD_{fn}_{sn}_{tn}")
        lines.append(f"    - DYAD_ARMOR_{tn}_IDS")
    lines.append("    - DYAD_ARMOR_ALL_IDS")

    return "\n".join(lines) + "\n"


def gen_pkg_dyad_items():
    """Generate the dyad-crystal-items package: shared item envelope archetypes.

    A slot/tier-agnostic common base plus per-slot commons (category, equipment
    type, constant tooltip) plus 12 per-tier bases that bake tier economics.
    Consumer crystal specs $extends the matching Dyad{Slot}{Tier}Base.
    """
    weapon_tooltip = (
        "<font color = '#2478FF'>[Recommended Classes: warrior, lancer, slayer, "
        "berserker, sorcerer, archer, reaper, gunner, brawler, ninja, valkyrie]"
        "</font> Dyad crystals are not destroyed upon death."
    )
    armor_tooltip = "Dyad crystals are not destroyed upon death."

    lines = []
    lines.append("# Dyad Crystal Item Base Definitions")
    lines.append("# Shared item envelope for all Dyad crystal items (weapon + armor, tiers 1-6).")
    lines.append("# Generated by tools/dyad-crystals/generate_dyad_specs.py. Do not hand-edit.")
    lines.append("#")
    lines.append("# Per-tier bases bake tier economics via $extends over the slot-common base,")
    lines.append("# which carries the constant category, equipment type and tooltip. Consumer")
    lines.append("# crystal specs $extends the matching Dyad{Slot}{Tier}Base.")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("")
    lines.append("definitions:")

    # Slot/tier-agnostic envelope (constant across every dyad crystal item)
    lines.append("  DyadCrystalCommon:")
    lines.append("    combatItemType: CUSTOM")
    lines.append("    combatItemSubType: custormaize")
    lines.append("    rareGrade: 2")
    lines.append("    boundType: EquipToItem")
    lines.append("    tradable: false")
    lines.append("    maxStack: 1")
    lines.append("    maxDropUnit: 1")
    lines.append("    guildWarehouseStorable: false")
    lines.append("    warehouseStorable: true")
    lines.append("    destroyable: true")
    lines.append("    dismantlable: false")
    lines.append("    storeSellable: true")
    lines.append("    obtainable: true")
    lines.append("    relocatable: true")
    lines.append("    artisanable: false")
    lines.append("    enchantEnable: false")
    lines.append("    searchable: true")
    lines.append("    rank: 0")
    lines.append("    sortingNumber: 1")
    lines.append('    gambleItemType: "1;2;4"')
    lines.append("    conversionBigGroup: 4")
    lines.append("    coolTimeGroup: 0")
    lines.append("    slotLimit: 0")
    lines.append("    dropSilhouette: DropItem.SM.Item_Drop_Chest_SM")
    lines.append("    dropSound: InterfaceSound.Drop_ItemCUE.Drop_ChestBoxCue")
    lines.append("    equipSound: InterfaceSound.Equip_ItemCUE.Equip_CustomizeStoneCue")
    lines.append("")

    # Per-slot commons: category, equipment type, constant tooltip
    lines.append("  DyadWeaponCommon:")
    lines.append("    $extends: DyadCrystalCommon")
    lines.append("    category: customize_weapon")
    lines.append("    requiredEquipmentType: EQUIP_WEAPON")
    lines.append("    strings:")
    lines.append(f'      toolTip: "{weapon_tooltip}"')
    lines.append("")
    lines.append("  DyadArmorCommon:")
    lines.append("    $extends: DyadCrystalCommon")
    lines.append("    category: customize_armor")
    lines.append("    requiredEquipmentType: EQUIP_ARMOR_BODY")
    lines.append("    strings:")
    lines.append(f'      toolTip: "{armor_tooltip}"')
    lines.append("")

    # Per-tier bases: bake tier economics (grade/level/price) onto the slot common
    for slot, common in (("Weapon", "DyadWeaponCommon"), ("Armor", "DyadArmorCommon")):
        for t in TIERS:
            tn = t["name"]
            lines.append(f"  Dyad{slot}{tn}Base:")
            lines.append(f"    $extends: {common}")
            lines.append(f"    name: Dyad{slot}{tn}")
            lines.append(f"    gambleItemGrade: {t['grade']}")
            lines.append(f"    level: {t['level']}")
            lines.append(f"    requiredLevel: {t['reqLevel']}")
            lines.append(f"    buyPrice: {t['buy']}")
            lines.append(f"    sellPrice: {t['sell']}")
            lines.append(f"    defaultValue: {t['buy']}")
            lines.append("")

    lines.append("exports:")
    lines.append("  definitions:")
    for slot in ("Weapon", "Armor"):
        for t in TIERS:
            lines.append(f"    - Dyad{slot}{t['name']}Base")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generator: Updated crystal box spec (Common → Fine)
# ---------------------------------------------------------------------------
def gen_crystal_boxes():
    """Generate updated 10-crystal-boxes.yaml using Fine crystals instead of Common."""

    # Dyad-eligible weapon families (20)
    weapon_families = [f["name"].upper() for f in WEAPON_FAMILIES]
    # Dyad-eligible armor families (11)
    armor_families = [f["name"].upper() for f in ARMOR_FAMILIES]
    tier_names = ["RHOMB", "CABOCHON", "HEXAGE", "PENTANT", "CONCACH", "CRUX", "NIVEOT"]

    lines = []
    lines.append("# Crystal Gacha Boxes — Patch 001")
    lines.append("# Fine-grade crystal boxes dropped from mob loot tables.")
    lines.append("# 14 boxes: 7 tiers x 2 categories (weapon/armor)")
    lines.append("")
    lines.append("spec:")
    lines.append('  version: "1.0"')
    lines.append("  schema: v92")
    lines.append("")

    # Imports
    lines.append("imports:")
    lines.append("  - from: crystals")
    lines.append("    use:")
    lines.append("      variables:")

    for tn in tier_names:
        lines.append(f"        - WEAPON_CRYSTAL_BOX_{tn}")
        lines.append(f"        - ARMOR_CRYSTAL_BOX_{tn}")
        for wf in weapon_families:
            lines.append(f"        - FINE_{wf}_{tn}")
        for af in armor_families:
            lines.append(f"        - FINE_{af}_{tn}")

    lines.append("")
    lines.append("definitions:")
    lines.append("  crystalBoxBase:")
    lines.append("    maxStack: 100")
    lines.append("    tradable: true")
    lines.append("    warehouseStorable: true")
    lines.append("    boundType: None")
    lines.append("")
    lines.append("gachaItems:")
    lines.append("  upsert:")

    tier_display = ["Rhomb", "Cabochon", "Hexage", "Pentant", "Concach", "Crux", "Niveot"]

    for ti, tn in enumerate(tier_names):
        td = tier_display[ti]
        tier_num = ti + 1

        # Weapon box
        lines.append(f"    # Weapon Crystal Box — Tier {tier_num} ({td}) — 20 crystals")
        lines.append(f"    - itemTemplateId: $WEAPON_CRYSTAL_BOX_{tn}")
        lines.append(f'      title: "Weapon Crystal Box ({td})"')
        lines.append('      sender: "Crystal System"')
        lines.append(f'      memo: "Fine weapon crystals tier {tier_num}"')
        lines.append("      item:")
        lines.append("        $extends: crystalBoxBase")
        lines.append("        icon: Icon_Items.Cash_Material_box_3_Tex")
        lines.append("        rareGrade: 1")
        lines.append("      randomRewards:")
        lines.append("        - equalProbability: true")
        lines.append("          rewards:")
        for wf in weapon_families:
            lines.append(f"            - itemTemplateId: $FINE_{wf}_{tn}")

        # Armor box
        lines.append(f"    # Armor Crystal Box — Tier {tier_num} ({td}) — 11 crystals")
        lines.append(f"    - itemTemplateId: $ARMOR_CRYSTAL_BOX_{tn}")
        lines.append(f'      title: "Armor Crystal Box ({td})"')
        lines.append('      sender: "Crystal System"')
        lines.append(f'      memo: "Fine armor crystals tier {tier_num}"')
        lines.append("      item:")
        lines.append("        $extends: crystalBoxBase")
        lines.append("        icon: Icon_Items.Cash_Material_box_3_Tex")
        lines.append("        rareGrade: 1")
        lines.append("      randomRewards:")
        lines.append("        - equalProbability: true")
        lines.append("          rewards:")
        for af in armor_families:
            lines.append(f"            - itemTemplateId: $FINE_{af}_{tn}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ids_data = compute_ids()

    # Ensure output dirs exist
    os.makedirs(SPECS_DIR, exist_ok=True)
    os.makedirs(PKG_DIR, exist_ok=True)

    # Generate spec files
    specs = {
        "11-dyad-structures.yaml": gen_structures(),
        "11-dyad-passivities.yaml": gen_passivities(ids_data),
        "11-dyad-abnormalities.yaml": gen_abnormalities(ids_data),
        "11-dyad-customizing.yaml": gen_customizing_items(ids_data),
        "11-dyad-customizing-bags.yaml": gen_customizing_bags(ids_data),
        "10-crystal-boxes.yaml": gen_crystal_boxes(),
    }

    for ti in range(6):
        t = TIERS[ti]
        specs[f"11-dyad-crystals-weapon-t{t['num']}.yaml"] = gen_crystal_items_weapon(ti, ids_data)
        specs[f"11-dyad-crystals-armor-t{t['num']}.yaml"] = gen_crystal_items_armor(ti, ids_data)

    for fname, content in specs.items():
        path = SPECS_DIR / fname
        path.write_text(content, encoding="utf-8")
        print(f"  Wrote {path.relative_to(REFORGED)}")

    # Generate package files
    pkg_files = {
        "structures.yml": gen_pkg_structures(),
        "dyad-weapon.yml": gen_pkg_dyad_weapon(),
        "dyad-armor.yml": gen_pkg_dyad_armor(),
    }

    for fname, content in pkg_files.items():
        path = PKG_DIR / fname
        path.write_text(content, encoding="utf-8")
        print(f"  Wrote {path.relative_to(REFORGED)}")

    # Generate the dyad-crystal-items package (shared item base archetypes)
    os.makedirs(DYAD_ITEMS_PKG_DIR, exist_ok=True)
    dyad_items_path = DYAD_ITEMS_PKG_DIR / "index.yml"
    dyad_items_path.write_text(gen_pkg_dyad_items(), encoding="utf-8")
    print(f"  Wrote {dyad_items_path.relative_to(REFORGED)}")

    # Summary
    print("\n--- Generation Summary ---")
    print(f"Spec files: {len(specs)}")
    print(f"Package files: {len(pkg_files)}")

    # Count entities
    w_items = 6 * 120
    a_items = 6 * 77
    print(f"Dyad weapon crystals: {w_items}")
    print(f"Dyad armor crystals: {a_items}")
    print(f"Total Dyad crystals: {w_items + a_items}")
    print(f"Structure items: 13 (6 Dyad + 6 Smart Dyad + 1 Rhomb)")
    print(f"RawStoneItem entries: 13")
    print(f"CustomizingItem entries: {w_items + a_items}")
    print(f"CustomizingItemBag entries: 12")
    print(f"Primary passivities: {6 * 31}")
    print(f"Secondary passivities: {6 * 9}")
    print(f"Abnormalities: {6 * 10}")

    print("\nDone! Remember to:")
    print("  1. Delete 11-crystal-upgrade.yaml")
    print("  2. Update index.yml imports/exports")
    print("  3. Update sync-config.yaml (add CustomizingItems, extend passivity bucket)")
    print("  4. Update migrate.py (add customizingItems/customizingItemBags)")
    print("  5. Update zone loot tool (Dyad/Smart Dyad structure drops)")


if __name__ == "__main__":
    main()
