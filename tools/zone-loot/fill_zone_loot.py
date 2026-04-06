"""
Zone Loot Table Generator — Fills specs with tier-appropriate drops.

Reads zone_tier_config.csv for tier assignments and npc_by_zone.csv for NPC
groupings, then generates eCompensation YAML specs with tier-matched crystal
boxes, runes, fusion structures, alkahest, infusion boxes, and gold.

All mob types (normal, elite, boss) use eCompensation since drops are class
agnostic — no class branching needed.

Usage:
    python tools/zone-loot/fill_zone_loot.py --patch 001
"""

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALKAHEST_ID = 21351

# Patch scope — only generate specs for zones in the active patch
PATCH_ZONES = {
    "001": {2, 3, 5, 6, 7, 15, 16, 17, 487, 488},
}

# Tier → feedstock item ID mapping (Item.rank correlation)
TIER_FEEDSTOCK = {
    2: 94101,   # Tier 1 Feedstock — Starter 0/1 gear (rank 1, Lv 1-30)
    3: 94102,   # Tier 2 Feedstock — Bastion gear (rank 2, Lv 31-50)
    4: 94103,   # Tier 3 Feedstock — (rank 3, Lv 51-60)
    5: 94104,   # Tier 4 Feedstock — (rank 4, Lv 61-64)
    6: 94104,   # Tier 4 Feedstock — endgame shares T4 feedstock
}

# Tier → drop item variable mapping
TIER_DROPS = {
    2: {
        "crystal_w": "WEAPON_CRYSTAL_BOX_CABOCHON",
        "crystal_a": "ARMOR_CRYSTAL_BOX_CABOCHON",
        "rune_shara": "PAVERUNE_OF_SHARA",
        "rune_arun": "PAVERUNE_OF_ARUN",
        "structure": "CABOCHON_STRUCTURE",
        "dyad_structure": "DYAD_CABOCHON_STRUCTURE",
        "smart_dyad_structure": "SMART_DYAD_CABOCHON_STRUCTURE",
        "gold_min": 5,
        "gold_max": 15,
    },
    3: {
        "crystal_w": "WEAPON_CRYSTAL_BOX_HEXAGE",
        "crystal_a": "ARMOR_CRYSTAL_BOX_HEXAGE",
        "rune_shara": "SILRUNE_OF_SHARA",
        "rune_arun": "SILRUNE_OF_ARUN",
        "structure": "HEXAGE_STRUCTURE",
        "dyad_structure": "DYAD_HEXAGE_STRUCTURE",
        "smart_dyad_structure": "SMART_DYAD_HEXAGE_STRUCTURE",
        "gold_min": 15,
        "gold_max": 40,
    },
    4: {
        "crystal_w": "WEAPON_CRYSTAL_BOX_PENTANT",
        "crystal_a": "ARMOR_CRYSTAL_BOX_PENTANT",
        "rune_shara": "QUOIRUNE_OF_SHARA",
        "rune_arun": "QUOIRUNE_OF_ARUN",
        "structure": "PENTANT_STRUCTURE",
        "dyad_structure": "DYAD_PENTANT_STRUCTURE",
        "smart_dyad_structure": "SMART_DYAD_PENTANT_STRUCTURE",
        "gold_min": 40,
        "gold_max": 100,
    },
    5: {
        "crystal_w": "WEAPON_CRYSTAL_BOX_CONCACH",
        "crystal_a": "ARMOR_CRYSTAL_BOX_CONCACH",
        "rune_shara": "ARCHRUNE_OF_SHARA",
        "rune_arun": "ARCHRUNE_OF_ARUN",
        "structure": "CONCACH_STRUCTURE",
        "dyad_structure": "DYAD_CONCACH_STRUCTURE",
        "smart_dyad_structure": "SMART_DYAD_CONCACH_STRUCTURE",
        "gold_min": 100,
        "gold_max": 250,
    },
    6: {
        "crystal_w": "WEAPON_CRYSTAL_BOX_CRUX",
        "crystal_a": "ARMOR_CRYSTAL_BOX_CRUX",
        "rune_shara": "KEYRUNE_OF_SHARA",
        "rune_arun": "KEYRUNE_OF_ARUN",
        "structure": "CRUX_STRUCTURE",
        "dyad_structure": "DYAD_CRUX_STRUCTURE",
        "smart_dyad_structure": "SMART_DYAD_CRUX_STRUCTURE",
        "gold_min": 250,
        "gold_max": 600,
    },
}

# Boss drop probabilities for Dyad structures by zone type
DYAD_PROBS = {
    "field":   {"dyad": 0.10, "smart_dyad": 0.01},
    "dungeon": {"dyad": 0.20, "smart_dyad": 0.02},
}

# Drop probabilities per mob type
NORMAL_PROBS = {"crystal": 0.03, "rune": 0.05, "structure": 0.01, "alkahest": 0.99}
ELITE_PROBS = {"crystal": 0.08, "rune": 0.12, "structure": 0.03, "alkahest": 0.97}

# Infusion gacha box IDs — same for all zone tiers (not tier-dependent)
# Each grade bag contains 4 items (weapon/chest/gloves/boots), equal probability
INFUSION_BOXES = {
    "uncommon": [602190, 602193, 602196, 602199],  # weapon, chest, gloves, boots
    "rare":     [602191, 602194, 602197, 602200],
    "superior": [602192, 602195, 602198, 602201],
}
INFUSION_PROBS_NORMAL = {"uncommon": 0.10, "rare": 0.01, "superior": 0.001}
INFUSION_PROBS_ELITE  = {"uncommon": 0.25, "rare": 0.05, "superior": 0.005}
INFUSION_PROBS_BOSS   = {"uncommon": 0.50, "rare": 0.10, "superior": 0.01}
INFUSION_GRADE_LABELS = {"uncommon": "Uncommon", "rare": "Rare", "superior": "Superior"}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Npc:
    template_id: int
    name: str
    title: str
    level: int
    elite: bool
    show_aggro_target: bool
    min_respawn: int
    has_party: bool

    @property
    def boss(self) -> bool:
        """Boss = showAggroTarget (reliable across field and dungeon zones)."""
        return self.show_aggro_target


@dataclass
class ZoneConfig:
    hunting_zone_id: int
    zone_name: str
    tier: int
    zone_type: str  # field, dungeon, hub, excluded


@dataclass
class ZoneNpcGroups:
    zone_id: int
    zone_name: str
    normals: list = field(default_factory=list)
    elites: list = field(default_factory=list)
    bosses: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# CSV readers
# ---------------------------------------------------------------------------

def read_zone_config(path: str) -> dict[int, ZoneConfig]:
    """Read zone_tier_config.csv → {huntingZoneId: ZoneConfig}."""
    configs = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            zid = int(row["huntingZoneId"])
            configs[zid] = ZoneConfig(
                hunting_zone_id=zid,
                zone_name=row["zoneName"],
                tier=int(row["tier"]),
                zone_type=row["type"],
            )
    return configs


def read_npcs(path: str) -> dict[int, list[Npc]]:
    """Read npc_by_zone.csv → {huntingZoneId: [Npc, ...]}."""
    npcs_by_zone: dict[int, list[Npc]] = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            zid = int(row["huntingZoneId"])
            npc = Npc(
                template_id=int(row["npcTemplateId"]),
                name=row.get("npcName", ""),
                title=row.get("npcTitle", ""),
                level=int(row["level"]),
                elite=row.get("elite", "False") == "True",
                show_aggro_target=row.get("showAggroTarget", "False") == "True",
                min_respawn=int(row.get("minRespawn", "0")),
                has_party=row.get("hasParty", "False") == "True",
            )
            npcs_by_zone.setdefault(zid, []).append(npc)
    return npcs_by_zone


# ---------------------------------------------------------------------------
# NPC grouping
# ---------------------------------------------------------------------------

def group_npcs(zone_id: int, zone_name: str, npcs: list[Npc]) -> ZoneNpcGroups:
    """Classify NPCs into normal/elite/boss groups."""
    groups = ZoneNpcGroups(zone_id=zone_id, zone_name=zone_name)
    for npc in npcs:
        if npc.boss:
            groups.bosses.append(npc)
        elif npc.elite:
            groups.elites.append(npc)
        else:
            groups.normals.append(npc)
    # Sort by template_id for deterministic output
    groups.normals.sort(key=lambda n: n.template_id)
    groups.elites.sort(key=lambda n: n.template_id)
    groups.bosses.sort(key=lambda n: n.template_id)
    return groups


# ---------------------------------------------------------------------------
# Slug helper (matches existing generator convention)
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    """Convert zone name to slug: lowercase, spaces→underscores, strip special chars."""
    s = name.lower()
    s = s.replace("'", "").replace("'", "")
    s = re.sub(r"[^a-z0-9_\s]", "", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


# ---------------------------------------------------------------------------
# YAML generation helpers
# ---------------------------------------------------------------------------

def npc_comment(npcs: list[Npc], group_label: str) -> str:
    """Build a comment showing NPC count, level range, and sample IDs."""
    if not npcs:
        return ""
    levels = sorted(set(n.level for n in npcs))
    lv_range = f"Lv{levels[0]}" if len(levels) == 1 else f"Lv{levels[0]}-{levels[-1]}"
    samples = []
    for n in npcs[:6]:
        label = n.name or str(n.template_id)
        if n.title:
            label = f"{n.name} ({n.title})"
        samples.append(f"{n.template_id}={label} {lv_range}")
    trailer = f", ... (+{len(npcs) - 6} more)" if len(npcs) > 6 else ""
    return f"# {group_label} ({len(npcs)} NPCs): {', '.join(samples)}{trailer}"


def collect_imports(tier: int, has_bosses: bool) -> tuple[list[str], list[str]]:
    """Return (crystal_vars, evo_vars) needed for imports."""
    drops = TIER_DROPS[tier]
    crystal_vars = [drops["crystal_w"], drops["crystal_a"], drops["structure"]]
    if has_bosses:
        crystal_vars.append(drops["dyad_structure"])
        crystal_vars.append(drops["smart_dyad_structure"])
    evo_vars = [drops["rune_shara"], drops["rune_arun"]]
    if tier == 6 and has_bosses:
        evo_vars.append("AERU_RUNE")
    return crystal_vars, evo_vars


def append_infusion_bags(lines: list[str], zone_name: str, mob_label: str,
                         probs: dict[str, float], bag_id: int) -> int:
    """Append 3 infusion box bags (uncommon/rare/superior) to lines.

    Returns the next available bag_id.
    """
    for grade, prob in probs.items():
        box_ids = INFUSION_BOXES[grade]
        label = INFUSION_GRADE_LABELS[grade]
        lines.append(f"      - id: {bag_id}")
        lines.append(f'        bagName: "{zone_name} {mob_label} Infusion ({label})"')
        lines.append(f"        probability: {prob}")
        lines.append("        equalProbability: true")
        lines.append("        items:")
        lines.append(f"          - templateId: {box_ids[0]}")
        lines.append(f'            name: "Infusion Weapon Box ({label})"')
        lines.append(f"          - templateId: {box_ids[1]}")
        lines.append(f'            name: "Infusion Chest Box ({label})"')
        lines.append(f"          - templateId: {box_ids[2]}")
        lines.append(f'            name: "Infusion Gloves Box ({label})"')
        lines.append(f"          - templateId: {box_ids[3]}")
        lines.append(f'            name: "Infusion Boots Box ({label})"')
        bag_id += 1
    return bag_id


# ---------------------------------------------------------------------------
# Definition generators (normal / elite / boss)
# ---------------------------------------------------------------------------

def generate_normal_definition(slug: str, zone_name: str, npcs: list[Npc], drops: dict, feedstock_id: int) -> tuple[list[str], int]:
    """Generate normal mob definition. Returns (lines, next_bag_id)."""
    lines = []
    levels = sorted(set(n.level for n in npcs))
    lv_str = f"Lv{levels[0]}" if len(levels) == 1 else f"Lv{levels[0]}-{levels[-1]}"
    lines.append(f"  # Normal mobs — {len(npcs)} NPCs, {lv_str}")
    lines.append(f"  {slug}_normal:")
    lines.append("    itemBags:")

    bag_id = 1

    # Bag: Crystal boxes
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Normal Crystal"')
    lines.append(f"        probability: {NORMAL_PROBS['crystal']}")
    lines.append("        equalProbability: true")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['crystal_w']}")
    lines.append(f'            name: "Weapon Crystal Box"')
    lines.append(f"          - templateId: ${drops['crystal_a']}")
    lines.append(f'            name: "Armor Crystal Box"')
    bag_id += 1

    # Bag: Runes
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Normal Rune"')
    lines.append(f"        probability: {NORMAL_PROBS['rune']}")
    lines.append("        equalProbability: true")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['rune_shara']}")
    lines.append(f'            name: "Weapon Evolution Rune"')
    lines.append(f"          - templateId: ${drops['rune_arun']}")
    lines.append(f'            name: "Armor Evolution Rune"')
    bag_id += 1

    # Bag: Alkahest + fusion structure
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Normal Alkahest"')
    lines.append("        probability: 1.0")
    lines.append("        items:")
    lines.append(f"          - templateId: {ALKAHEST_ID}")
    lines.append(f'            name: "Alkahest"')
    lines.append(f"            probability: {NORMAL_PROBS['alkahest']}")
    lines.append("            min: 1")
    lines.append("            max: 2")
    lines.append(f"          - templateId: ${drops['structure']}")
    lines.append(f'            name: "Fusion Structure"')
    lines.append(f"            probability: {NORMAL_PROBS['structure']}")
    bag_id += 1

    # Bag: Feedstock (2x alkahest ratio)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Normal Feedstock"')
    lines.append("        probability: 1.0")
    lines.append("        items:")
    lines.append(f"          - templateId: {feedstock_id}")
    lines.append(f'            name: "Feedstock"')
    lines.append(f"            probability: {NORMAL_PROBS['alkahest']}")
    lines.append("            min: 2")
    lines.append("            max: 4")
    bag_id += 1

    # Bags: Infusion boxes (3 grades, independent rolls)
    bag_id = append_infusion_bags(lines, zone_name, "Normal", INFUSION_PROBS_NORMAL, bag_id)

    return lines, bag_id


def generate_elite_definition(slug: str, zone_name: str, npcs: list[Npc], drops: dict, feedstock_id: int) -> tuple[list[str], int]:
    """Generate elite mob definition. Returns (lines, next_bag_id)."""
    lines = []
    levels = sorted(set(n.level for n in npcs))
    lv_str = f"Lv{levels[0]}" if len(levels) == 1 else f"Lv{levels[0]}-{levels[-1]}"
    lines.append(f"  # Elite mobs — {len(npcs)} NPCs, {lv_str}")
    lines.append(f"  {slug}_elite:")
    lines.append("    itemBags:")

    bag_id = 1

    # Bag: Crystal boxes
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Elite Crystal"')
    lines.append(f"        probability: {ELITE_PROBS['crystal']}")
    lines.append("        equalProbability: true")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['crystal_w']}")
    lines.append(f'            name: "Weapon Crystal Box"')
    lines.append(f"          - templateId: ${drops['crystal_a']}")
    lines.append(f'            name: "Armor Crystal Box"')
    bag_id += 1

    # Bag: Runes
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Elite Rune"')
    lines.append(f"        probability: {ELITE_PROBS['rune']}")
    lines.append("        equalProbability: true")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['rune_shara']}")
    lines.append(f'            name: "Weapon Evolution Rune"')
    lines.append("            min: 1")
    lines.append("            max: 2")
    lines.append(f"          - templateId: ${drops['rune_arun']}")
    lines.append(f'            name: "Armor Evolution Rune"')
    lines.append("            min: 1")
    lines.append("            max: 2")
    bag_id += 1

    # Bag: Alkahest + fusion structure
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Elite Alkahest"')
    lines.append("        probability: 1.0")
    lines.append("        items:")
    lines.append(f"          - templateId: {ALKAHEST_ID}")
    lines.append(f'            name: "Alkahest"')
    lines.append(f"            probability: {ELITE_PROBS['alkahest']}")
    lines.append("            min: 2")
    lines.append("            max: 4")
    lines.append(f"          - templateId: ${drops['structure']}")
    lines.append(f'            name: "Fusion Structure"')
    lines.append(f"            probability: {ELITE_PROBS['structure']}")
    bag_id += 1

    # Bag: Feedstock (2x alkahest ratio)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Elite Feedstock"')
    lines.append("        probability: 1.0")
    lines.append("        items:")
    lines.append(f"          - templateId: {feedstock_id}")
    lines.append(f'            name: "Feedstock"')
    lines.append(f"            probability: {ELITE_PROBS['alkahest']}")
    lines.append("            min: 4")
    lines.append("            max: 8")
    bag_id += 1

    # Bags: Infusion boxes (3 grades, independent rolls)
    bag_id = append_infusion_bags(lines, zone_name, "Elite", INFUSION_PROBS_ELITE, bag_id)

    return lines, bag_id


def generate_boss_definition(slug: str, zone_name: str, npcs: list[Npc], drops: dict, tier: int, feedstock_id: int, zone_type: str) -> list[str]:
    """Generate boss mob definition. Returns lines."""
    lines = []
    levels = sorted(set(n.level for n in npcs))
    lv_str = f"Lv{levels[0]}" if len(levels) == 1 else f"Lv{levels[0]}-{levels[-1]}"
    lines.append(f"  # Boss mobs — {len(npcs)} NPCs, {lv_str}")
    lines.append(f"  {slug}_boss:")
    lines.append("    itemBags:")

    bag_id = 1

    # Bag: Weapon crystal box (50%)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Weapon Crystal"')
    lines.append("        probability: 0.5")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['crystal_w']}")
    lines.append(f'            name: "Weapon Crystal Box"')
    lines.append("            probability: 1.0")
    bag_id += 1

    # Bag: Armor crystal box (50%)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Armor Crystal"')
    lines.append("        probability: 0.5")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['crystal_a']}")
    lines.append(f'            name: "Armor Crystal Box"')
    lines.append("            probability: 1.0")
    bag_id += 1

    # Bag: Weapon rune (guaranteed)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Weapon Rune"')
    lines.append("        probability: 1.0")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['rune_shara']}")
    lines.append(f'            name: "Weapon Evolution Rune"')
    lines.append("            probability: 1.0")
    bag_id += 1

    # Bag: Armor rune (guaranteed)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Armor Rune"')
    lines.append("        probability: 1.0")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['rune_arun']}")
    lines.append(f'            name: "Armor Evolution Rune"')
    lines.append("            probability: 1.0")
    bag_id += 1

    # Bag: Fusion structure (15%)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Fusion Structure"')
    lines.append("        probability: 0.15")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['structure']}")
    lines.append(f'            name: "Fusion Structure"')
    lines.append("            probability: 1.0")
    lines.append("            min: 1")
    lines.append("            max: 2")
    bag_id += 1

    # Bag: Dyad Structure
    dyad_probs = DYAD_PROBS[zone_type]
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Dyad Structure"')
    lines.append(f"        probability: {dyad_probs['dyad']}")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['dyad_structure']}")
    lines.append(f'            name: "Dyad Structure"')
    lines.append("            probability: 1.0")
    bag_id += 1

    # Bag: Smart Dyad Structure
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Smart Dyad Structure"')
    lines.append(f"        probability: {dyad_probs['smart_dyad']}")
    lines.append("        items:")
    lines.append(f"          - templateId: ${drops['smart_dyad_structure']}")
    lines.append(f'            name: "Smart Dyad Structure"')
    lines.append("            probability: 1.0")
    bag_id += 1

    # Bag: Alkahest (guaranteed)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Alkahest"')
    lines.append("        probability: 1.0")
    lines.append("        items:")
    lines.append(f"          - templateId: {ALKAHEST_ID}")
    lines.append(f'            name: "Alkahest"')
    lines.append("            probability: 1.0")
    lines.append("            min: 3")
    lines.append("            max: 6")
    bag_id += 1

    # Bag: Feedstock (guaranteed, 2x alkahest ratio)
    lines.append(f"      - id: {bag_id}")
    lines.append(f'        bagName: "{zone_name} Feedstock"')
    lines.append("        probability: 1.0")
    lines.append("        items:")
    lines.append(f"          - templateId: {feedstock_id}")
    lines.append(f'            name: "Feedstock"')
    lines.append("            probability: 1.0")
    lines.append("            min: 6")
    lines.append("            max: 12")
    bag_id += 1

    # Bags: Infusion boxes (3 grades, independent rolls)
    bag_id = append_infusion_bags(lines, zone_name, "Boss", INFUSION_PROBS_BOSS, bag_id)

    # T6 bonus: Aeru Rune (50%)
    if tier == 6:
        lines.append(f"      - id: {bag_id}")
        lines.append(f'        bagName: "{zone_name} Aeru Rune"')
        lines.append("        probability: 0.5")
        lines.append("        items:")
        lines.append("          - templateId: $AERU_RUNE")
        lines.append('            name: "Aeru Rune"')
        lines.append("            probability: 1.0")
        bag_id += 1

    # GoldBags (boss only)
    lines.append("    goldBags:")
    lines.append(f'      - bagName: "{zone_name} Gold"')
    lines.append("        probability: 1.0")
    lines.append(f"        min: {drops['gold_min']}")
    lines.append(f"        max: {drops['gold_max']}")

    return lines


# ---------------------------------------------------------------------------
# eCompensation YAML generator (all mob types)
# ---------------------------------------------------------------------------

def generate_e_compensation(zone: ZoneConfig, groups: ZoneNpcGroups,
                            vanilla_ccomp_ids: list[int] | None = None) -> str | None:
    """Generate eCompensation YAML for a zone with all mob types.

    If vanilla_ccomp_ids is provided, emits cCompensation delete entries
    to clear pre-existing vanilla loot (which lives in cCompensation).
    """
    if not groups.normals and not groups.elites and not groups.bosses:
        return None

    tier = zone.tier
    drops = TIER_DROPS[tier]
    feedstock_id = TIER_FEEDSTOCK[tier]
    slug = slugify(zone.zone_name)
    crystal_vars, evo_vars = collect_imports(tier, bool(groups.bosses))

    lines = []
    lines.append(f"# {zone.zone_name} (Zone {zone.hunting_zone_id}) — Tier {tier} eCompensation")
    lines.append(f"# All mob drops: crystal boxes, runes, fusion structures, alkahest, feedstock, infusion boxes, gold")
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
    for v in crystal_vars:
        lines.append(f"        - {v}")
    lines.append("  - from: evolution-base")
    lines.append("    use:")
    lines.append("      variables:")
    for v in evo_vars:
        lines.append(f"        - {v}")
    lines.append("")

    # Definitions
    lines.append("definitions:")

    if groups.normals:
        normal_lines, _ = generate_normal_definition(slug, zone.zone_name, groups.normals, drops, feedstock_id)
        lines.extend(normal_lines)
        lines.append("")

    if groups.elites:
        elite_lines, _ = generate_elite_definition(slug, zone.zone_name, groups.elites, drops, feedstock_id)
        lines.extend(elite_lines)
        lines.append("")

    if groups.bosses:
        boss_lines = generate_boss_definition(slug, zone.zone_name, groups.bosses, drops, tier, feedstock_id, zone.zone_type)
        lines.extend(boss_lines)
        lines.append("")

    # Upsert entries
    lines.append("eCompensations:")
    lines.append("  upsert:")

    if groups.normals:
        lines.append(f"    {npc_comment(groups.normals, 'Normal')}")
        ids = [n.template_id for n in groups.normals]
        lines.append(f"    - huntingZoneId: {zone.hunting_zone_id}")
        lines.append(f"      npcTemplateId: [{', '.join(str(i) for i in ids)}]")
        lines.append(f'      npcName: ""')
        lines.append(f"      $extends: {slug}_normal")

    if groups.elites:
        lines.append(f"    {npc_comment(groups.elites, 'Elite')}")
        ids = [n.template_id for n in groups.elites]
        lines.append(f"    - huntingZoneId: {zone.hunting_zone_id}")
        lines.append(f"      npcTemplateId: [{', '.join(str(i) for i in ids)}]")
        lines.append(f'      npcName: ""')
        lines.append(f"      $extends: {slug}_elite")

    if groups.bosses:
        lines.append(f"    {npc_comment(groups.bosses, 'Boss')}")
        ids = [n.template_id for n in groups.bosses]
        lines.append(f"    - huntingZoneId: {zone.hunting_zone_id}")
        lines.append(f"      npcTemplateId: [{', '.join(str(i) for i in ids)}]")
        lines.append(f'      npcName: ""')
        lines.append(f"      $extends: {slug}_boss")

    # Delete all vanilla cCompensation entries (vanilla loot lives in cComp)
    if vanilla_ccomp_ids:
        lines.append("")
        lines.append(f"cCompensations:")
        lines.append(f"  # Delete {len(vanilla_ccomp_ids)} vanilla cCompensation entries")
        lines.append("  delete:")
        for nid in sorted(vanilla_ccomp_ids):
            lines.append(f"    - huntingZoneId: {zone.hunting_zone_id}")
            lines.append(f"      npcTemplateId: {nid}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_vanilla_ccomp_ids(path: str) -> dict[int, list[int]]:
    """Load vanilla eCompensation NPC IDs from JSON file."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


def main():
    parser = argparse.ArgumentParser(description="Fill zone loot specs with tier-appropriate drops")
    parser.add_argument("--patch", default="001", help="Patch number (default: 001)")
    parser.add_argument("--zones", default=None, help="Comma-separated zone IDs to generate (default: all)")
    parser.add_argument("--vanilla-ids", default=None, help="Path to vanilla cComp NPC IDs JSON for delete entries")
    parser.add_argument("--dry-run", action="store_true", help="Print stats without writing files")
    args = parser.parse_args()

    # Resolve paths relative to reforged/ root
    script_dir = Path(__file__).resolve().parent
    reforged_root = script_dir.parent.parent
    data_dir = reforged_root / "data" / "zone_loot"
    specs_dir = reforged_root / "specs" / "patches" / args.patch / "loot"
    e_comp_dir = specs_dir / "e-compensation"

    # Read inputs
    zone_configs = read_zone_config(str(data_dir / "zone_tier_config.csv"))
    npcs_by_zone = read_npcs(str(data_dir / "npc_by_zone.csv"))

    # Optional zone filter
    zone_filter = None
    if args.zones:
        zone_filter = set(int(z.strip()) for z in args.zones.split(","))

    # Optional vanilla cComp IDs for delete entries
    vanilla_ids = {}
    if args.vanilla_ids:
        vanilla_ids = load_vanilla_ccomp_ids(args.vanilla_ids)

    # Stats
    stats = {"e_written": 0, "skipped_no_tier": 0, "skipped_no_npcs": 0, "skipped_filtered": 0}

    # Resolve patch scope
    patch_scope = PATCH_ZONES.get(args.patch)

    for zid, config in sorted(zone_configs.items()):
        # Skip non-combat zones and tier 0
        if config.tier == 0 or config.zone_type in ("hub", "excluded"):
            continue

        # Apply patch scope filter (unless --zones override is active)
        if not zone_filter and patch_scope and zid not in patch_scope:
            stats["skipped_filtered"] += 1
            continue

        # Apply manual zone filter
        if zone_filter and zid not in zone_filter:
            stats["skipped_filtered"] += 1
            continue

        # Skip tiers without drop definitions (T1 has no field zones)
        if config.tier not in TIER_DROPS:
            stats["skipped_no_tier"] += 1
            continue

        # Get NPCs for this zone
        npcs = npcs_by_zone.get(zid, [])
        if not npcs:
            stats["skipped_no_npcs"] += 1
            continue

        # Group NPCs
        groups = group_npcs(zid, config.zone_name, npcs)
        slug = slugify(config.zone_name)
        filename = f"zone-{zid:04d}-{slug}.yaml"

        # Generate eCompensation (all mob types)
        zone_ccomp_ids = vanilla_ids.get(zid)
        e_yaml = generate_e_compensation(config, groups, zone_ccomp_ids)
        if e_yaml:
            e_path = e_comp_dir / filename
            if args.dry_run:
                n_count = len(groups.normals)
                e_count = len(groups.elites)
                b_count = len(groups.bosses)
                print(f"  [e-comp] {filename} — T{config.tier} — {n_count} normal, {e_count} elite, {b_count} boss")
            else:
                os.makedirs(e_comp_dir, exist_ok=True)
                with open(str(e_path), "w", encoding="utf-8", newline="\n") as f:
                    f.write(e_yaml)
            stats["e_written"] += 1

    # Summary
    print(f"\nZone Loot Generator — Patch {args.patch}")
    print(f"  eCompensation files: {stats['e_written']}")
    if zone_filter:
        print(f"  Skipped (filtered out): {stats['skipped_filtered']}")
    print(f"  Skipped (no tier drops): {stats['skipped_no_tier']}")
    print(f"  Skipped (no NPCs): {stats['skipped_no_npcs']}")
    if args.dry_run:
        print("  (dry-run mode — no files written)")


if __name__ == "__main__":
    main()
