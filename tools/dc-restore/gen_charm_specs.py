"""Generate patch 001 charm restoration specs (1:1 deterministic model).

Deterministic: re-running regenerates identical output from the inline design
table plus current server StrSheet_Item names.

Outputs:
  specs/patches/001/14-charm-abnormalities.yaml  (buff abnormalities + strings + icons)
  specs/patches/001/15-charm-items.yaml          (combatItemType flips + item tooltips)
  specs/patches/001/16-charm-skills.yaml         (buff injection + spike cleanup)
  docs/plans/charm-restoration/charm-design-map.md (authoritative mapping table)

Design (user-settled 2026-07-20, supersedes the shared-effect model):
- 1:1 buff per charm skill; buff name and icon match the granting item.
- Deterministic only: named charms = Major (classic tier-3) values, greater
  charms = classic tier-4 values.
- Onslaught/Ethereal/Sanguine I-IV are kind-scoped BUNDLES: every family of
  their kind in one buff at HALF the classic tier bonus (broad-but-weak vs the
  focused single-family charms; the 3-slot kind rule makes it a real tradeoff).
- Service charms (6/7/8, 31/32/33) share their line's tier-IV bundle skill.
- Trios (Balder's 81210, 98251, Talisman 201000+) fill all 3 slots: Balder's
  and Talisman keep their classic full tier-4 names/values; 98251 grants the
  three Major named buffs. Their items carry placeholder icons, so these buffs
  keep the classic charm-status icons instead.
"""

from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REFORGED = PROJECT_ROOT / "reforged"

BASE_ID = 488000010  # continues the Novos Abnormals custom band (IdSeed 488000002)

# Hand-made spike leftovers superseded by this restoration (server repo commits
# 0b66f0b6/66ad78fa/1660ed5f). 488000002 exists only inside an IdSeed comment,
# never as a row. 488000001 and 488000007-488000009 belong to other systems.
SPIKE_ABN_IDS = [488000003, 488000004, 488000005, 488000006]

# group: (abnormality kind, burn-burst appearEffectId, Rare_ icon index, classic paper prefix)
KIND_GROUPS = {
    "offense": (9814, 10045001, 1, "mysterypaper"),
    "defense": (9813, 500245, 2, "magicalpaper"),
    "auxiliary": (9812, 50171, 3, "abnormalpaper"),
}

# family order = item order 178-193 / 70019-70034 / named+greater skill bands
FAM_ORDER = ["power", "keen", "speed", "strength",
             "enduring", "unyielding", "rigid", "robust", "caduceus", "tenacity", "reverse",
             "relentless", "cunning", "vigorous", "infused", "swift"]

# family: (effect type, kind group, tickInterval, tooltip label, classic tier 1-4 multipliers)
FAMILIES = {
    "power":      (3,   "offense",   0, "Power",                   ["1.14", "1.16", "1.19", "1.27"]),
    "keen":       (6,   "offense",   0, "Critical hit chance",     ["1.16", "1.2", "1.24", "1.31"]),
    "speed":      (101, "offense",   0, "Attack speed",            ["1.04", "1.05", "1.06", "1.08"]),
    "strength":   (8,   "offense",   0, "Knockdown chance",        ["1.1", "1.126", "1.147", "1.211"]),
    "enduring":   (4,   "defense",   0, "Endurance",               ["1.1", "1.125", "1.15", "1.2"]),
    "unyielding": (7,   "defense",   0, "Critical hit resistance", ["1.2", "1.24", "1.28", "1.4"]),
    "rigid":      (9,   "defense",   0, "Knockdown resistance",    ["1.1", "1.12", "1.14", "1.2"]),
    "robust":     (14,  "defense",   0, "Weakening resistance",    ["1.1", "1.12", "1.14", "1.2"]),
    "caduceus":   (15,  "defense",   0, "Poison resistance",       ["1.1", "1.12", "1.14", "1.2"]),
    "tenacity":   (16,  "defense",   0, "Immobility resistance",   ["1.1", "1.12", "1.14", "1.2"]),
    "reverse":    (102, "defense",   0, "Damage reflection",       ["1.05", "1.06", "1.07", "1.1"]),
    "relentless": (1,   "auxiliary", 0, "Maximum HP",              ["1.075", "1.09", "1.1", "1.15"]),
    "cunning":    (2,   "auxiliary", 0, "Maximum MP",              ["1.05", "1.06", "1.07", "1.1"]),
    "vigorous":   (51,  "auxiliary", 5, "HP regeneration",         ["1.006", "1.008", "1.009", "1.013"]),
    "infused":    (52,  "auxiliary", 5, "MP regeneration",         ["1.0845", "1.1014", "1.1183", "1.169"]),
    "swift":      (5,   "auxiliary", 0, "Movement speed",          ["1.03", "1.05", "1.07", "1.1"]),
}

KIND_FAMILIES = {g: [f for f in FAM_ORDER if FAMILIES[f][1] == g] for g in KIND_GROUPS}

# bundle line: (kind group, item id base: tier N item = base + N - 1)
BUNDLE_LINES = {"onslaught": ("offense", 7100), "ethereal": ("defense", 7104), "sanguine": ("auxiliary", 7108)}

TRIO_FAMS = ["power", "enduring", "infused"]
BALDER_NAMES = {"power": "Balder's Power Charm", "enduring": "Balder's Enduring Charm",
                "infused": "Balder's Infused Charm"}
TRIO_NAMES = {"power": "Talisman Trio: Power", "enduring": "Talisman Trio: Enduring",
              "infused": "Talisman Trio: Infusion"}

NAMED_SKILLS = [60245100, 60245110, 60245120, 60245130,
                60245200, 60245210, 60245220, 60245230, 60245240, 60245250, 60245260,
                60245300, 60245310, 60245320, 60245330, 60245340]
GREATER_SKILLS = [60246100, 60246110, 60246120, 60246130,
                  60246200, 60246210, 60246220, 60246230, 60246240, 60246250, 60246260,
                  60246300, 60246310, 60246320, 60246330, 60246340]
BUNDLE_SKILLS = {"onslaught": [60240200, 60240300, 60240400, 60240500],
                 "ethereal": [60240600, 60240700, 60240800, 60240900],
                 "sanguine": [60241000, 60241100, 60241200, 60241300]}
SERVICE_SKILLS = {60241400: "onslaught", 60241500: "ethereal", 60241600: "sanguine"}

# item id -> (linkSkillId, flip) - flip=True means live v92 combatItemType is
# NO_COMBAT and must become DISPOSAL.
ITEMS = {
    6: (60241400, True), 7: (60241500, True), 8: (60241600, True),
    31: (60241400, True), 32: (60241500, True), 33: (60241600, True),
    **{178 + i: (NAMED_SKILLS[i], True) for i in range(16)},
    **{7100 + i: ([60240200, 60240300, 60240400, 60240500,
                   60240600, 60240700, 60240800, 60240900,
                   60241000, 60241100, 60241200, 60241300][i], True) for i in range(12)},
    **{70019 + i: (GREATER_SKILLS[i], False) for i in range(16)},
    81210: (63005522, True), 98251: (61015007, True),
    201000: (61100001, True), 201001: (61100001, True), 201002: (61100001, True),
    201003: (61100001, True), 201021: (61100001, True),
}

DEATH_NOTE = "Lasts 30 minutes and persists through death."


def dec(s: str) -> Decimal:
    return Decimal(s)


def fmt(d: Decimal) -> str:
    s = format(d.normalize(), "f")
    return s


def half_bonus(v: str) -> str:
    return fmt(Decimal(1) + (dec(v) - 1) / 2)


def pct(mult: str) -> str:
    p = (dec(mult) - 1) * 100
    s = format(p.normalize(), "f")
    return (s.rstrip("0").rstrip(".") if "." in s else s) + "%"


def build_buffs(names):
    """Return (buffs by key, ordered buff list, skill->buff-keys map)."""
    buffs = {}
    order = []

    def add(key, name, group, level, icon, fams_vals, internal):
        ktype, appear, _rare, _paper = KIND_GROUPS[group][0], KIND_GROUPS[group][1], None, None
        effects = []
        for fam, val in fams_vals:
            ftype, _g, tick, label, _tiers = FAMILIES[fam]
            effects.append({"type": ftype, "value": val, "tick": tick,
                            "label": label, "pct": pct(val)})
        if len(effects) == 1:
            tooltip = f"{effects[0]['label']} increased by {effects[0]['pct']}. {DEATH_NOTE}"
        else:
            tooltip = ", ".join(f"{e['label']} +{e['pct']}" for e in effects) + f". {DEATH_NOTE}"
        buffs[key] = {"key": key, "name": name, "kind": KIND_GROUPS[group][0], "appear": appear,
                      "level": level, "icon": icon, "effects": effects, "tooltip": tooltip,
                      "internal": internal}
        order.append(buffs[key])

    for i, fam in enumerate(FAM_ORDER):
        group = FAMILIES[fam][1]
        rare = KIND_GROUPS[group][2]
        add(f"named_{fam}", names[178 + i], group, 3, f"Icon_Items.Rare_Mysterypaper{rare}_Tex",
            [(fam, FAMILIES[fam][4][2])], f"Charm_Named_{fam.capitalize()}")
    for i, fam in enumerate(FAM_ORDER):
        group = FAMILIES[fam][1]
        rare = KIND_GROUPS[group][2]
        add(f"greater_{fam}", names[70019 + i], group, 4, f"Icon_Items.Rare_Mysterypaper{rare}_Tex",
            [(fam, FAMILIES[fam][4][3])], f"Charm_Greater_{fam.capitalize()}")
    for line, (group, item_base) in BUNDLE_LINES.items():
        paper = KIND_GROUPS[group][3]
        for tier in range(1, 5):
            fams_vals = [(f, half_bonus(FAMILIES[f][4][tier - 1])) for f in KIND_FAMILIES[group]]
            add(f"bundle_{line}_{tier}", names[item_base + tier - 1], group, tier,
                f"Icon_Items.{paper}{tier}_Tex", fams_vals,
                f"Charm_Bundle_{line.capitalize()}{tier}")
    for fam in TRIO_FAMS:
        group = FAMILIES[fam][1]
        paper = KIND_GROUPS[group][3]
        add(f"balder_{fam}", BALDER_NAMES[fam], group, 4, f"Icon_Items.{paper}4_Tex",
            [(fam, FAMILIES[fam][4][3])], f"Charm_Balder_{fam.capitalize()}")
    for fam in TRIO_FAMS:
        group = FAMILIES[fam][1]
        paper = KIND_GROUPS[group][3]
        add(f"trio_{fam}", TRIO_NAMES[fam], group, 4, f"Icon_Items.{paper}4_Tex",
            [(fam, FAMILIES[fam][4][3])], f"Charm_Trio_{fam.capitalize()}")

    for i, b in enumerate(order):
        b["abn_id"] = BASE_ID + i

    skill_buffs = {}
    for i, sid in enumerate(NAMED_SKILLS):
        skill_buffs[sid] = [f"named_{FAM_ORDER[i]}"]
    for i, sid in enumerate(GREATER_SKILLS):
        skill_buffs[sid] = [f"greater_{FAM_ORDER[i]}"]
    for line, sids in BUNDLE_SKILLS.items():
        for tier, sid in enumerate(sids, start=1):
            skill_buffs[sid] = [f"bundle_{line}_{tier}"]
    for sid, line in SERVICE_SKILLS.items():
        skill_buffs[sid] = [f"bundle_{line}_4"]
    skill_buffs[63005522] = [f"balder_{f}" for f in TRIO_FAMS]
    skill_buffs[61015007] = [f"named_{f}" for f in TRIO_FAMS]
    skill_buffs[61100001] = [f"trio_{f}" for f in TRIO_FAMS]
    return buffs, order, skill_buffs


def read_item_names(server_datasheet: Path):
    names = {}
    tree = ET.parse(server_datasheet / "StrSheet_Item.xml")
    wanted = set(ITEMS)
    for s in tree.getroot().iter("String"):
        i = int(s.get("id"))
        if i in wanted:
            names[i] = s.get("string")
    missing = wanted - set(names)
    if missing:
        raise SystemExit(f"StrSheet_Item is missing charm item ids: {sorted(missing)}")
    return names


def resolve_server_datasheet() -> Path:
    refs = {}
    for line in (REFORGED / ".references").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            refs[k.strip()] = v.strip()
    return Path(refs["server_datasheet"])


def emit_abnormality_spec(order):
    L = []
    L.append("# Charm Buff Abnormalities - Patch 001")
    L.append("# 1:1 deterministic charm buffs (see charm-design-map.md). Named = classic tier-3")
    L.append("# values, greater = classic tier-4, Onslaught/Ethereal/Sanguine = kind-scoped")
    L.append("# bundles at half the classic tier bonus. method=3 multipliers, 30 min, persist")
    L.append("# through death. Burn visuals: classic per-kind targetEffectId as appearEffectId.")
    L.append("# Buff icons match the granting item's icon (trio items excepted: placeholder art).")
    L.append("# Generated by tools/dc-restore/gen_charm_specs.py")
    L.append("")
    L.append("spec:")
    L.append('  version: "1.0"')
    L.append("  schema: v92")
    L.append("")
    L.append("definitions:")
    L.append("  charmBuffBase:")
    L.append("    property: 4")
    L.append('    category: "4"')
    L.append("    time: 1800000")
    L.append("    isBuff: true")
    L.append('    isShow: "True"')
    L.append('    mobSize: "all"')
    L.append("    priority: 7")
    L.append("    maxStackCount: 1")
    L.append("    levelOver: 1")
    L.append("    levelUnder: 127")
    L.append("    notCareDeath: true")
    L.append("    notCareBattleField: true")
    L.append('    group: "doping"')
    L.append("")
    L.append("abnormalities:")
    L.append("  upsert:")
    for b in order:
        L.append(f"    # {b['name']}")
        L.append(f"    - id: {b['abn_id']}")
        L.append("      $extends: charmBuffBase")
        L.append(f"      name: \"{b['internal']}\"")
        L.append(f"      kind: {b['kind']}")
        L.append(f"      level: {b['level']}")
        L.append("      effects:")
        for i, e in enumerate(b["effects"]):
            L.append(f"        - type: {e['type']}")
            L.append("          method: 3")
            L.append(f"          value: \"{e['value']}\"")
            L.append(f"          tickInterval: {e['tick']}")
            if i == 0:
                L.append(f"          appearEffectId: {b['appear']}")
                L.append('          effectPart: "FXBottom"')
        L.append("      abnormalityStrings:")
        L.append(f"        name: \"{b['name']}\"")
        L.append(f"        tooltip: \"{b['tooltip']}\"")
    L.append("")
    L.append("abnormalityIconData:")
    L.append("  upsert:")
    for b in order:
        L.append(f"    - abnormalityId: {b['abn_id']}")
        L.append(f"      iconName: \"{b['icon']}\"")
    L.append("")
    return "\n".join(L)


def emit_item_spec(buffs, skill_buffs, names):
    L = []
    L.append("# Charm Items Re-enable - Patch 001")
    L.append("# Flips retired charm items back to usable (combatItemType DISPOSAL) and replaces the")
    L.append('# "This item is no longer usable." tooltips with the restored effect description.')
    L.append("# Generated by tools/dc-restore/gen_charm_specs.py")
    L.append("")
    L.append("spec:")
    L.append('  version: "1.0"')
    L.append("  schema: v92")
    L.append("")
    flips = [i for i, (_s, flip) in sorted(ITEMS.items()) if flip]
    L.append("items:")
    L.append("  update:")
    for i in flips:
        L.append(f"    - id: {i}  # {names[i]}")
        L.append("      changes:")
        L.append("        combatItemType: DISPOSAL")
    L.append("")
    L.append("itemStrings:")
    L.append("  upsert:")
    for i, (skill_id, _flip) in sorted(ITEMS.items()):
        recs = [buffs[k] for k in skill_buffs[skill_id]]
        if len(recs) == 1:
            r = recs[0]
            tip = f"Grants {r['name']}: {r['tooltip']}"
        else:
            bn = ", ".join(r["name"] for r in recs[:-1]) + f" and {recs[-1]['name']}"
            tip = f"Grants {bn}. {DEATH_NOTE}"
        L.append(f"    - id: {i}")
        L.append(f"      name: \"{names[i]}\"")
        L.append(f"      toolTip: \"{tip}\"")
    L.append("")
    return "\n".join(L)


def emit_skill_spec(buffs, skill_buffs):
    L = []
    L.append("# Charm Skill Buff Injection - Patch 001")
    L.append("# Injects a TargetingList into every charm-linked skill so using the item applies the")
    L.append("# matching buff abnormality from 14-charm-abnormalities to the user AND nearby allies")
    L.append("# (allyExceptMe r500 maxCount 19 + me r30: the BHS party food-buff pattern, e.g.")
    L.append("# Traditional Bleakfields BBQ skill 60950532, matching classic charm behavior). Replaces the")
    L.append("# hand-made spike TargetingLists on skills 60246100/60246200/60246330 and deletes the")
    L.append("# superseded spike abnormalities 488000003-488000006 with their icon and string rows.")
    L.append("# Requires DSL >= a7cf8d11 (Area type/maxCount/rangeAngle authoring).")
    L.append("# Generated by tools/dc-restore/gen_charm_specs.py")
    L.append("")
    L.append("spec:")
    L.append('  version: "1.0"')
    L.append("  schema: v92")
    L.append("")
    L.append("definitions:")
    L.append("  # BHS party food-buff area pair (Bleakfields BBQ skill 60950532)")
    L.append("  # $ABN binds at the _charmCast/_charmCastTriple call sites (scope inheritance)")
    L.append("  _charmArea:")
    L.append("    minRadius: 0.0")
    L.append("    maxHeight: 60.0")
    L.append("    minHeight: 0.0")
    L.append("    rangeAngle: 360.0")
    L.append("    offsetDistance: 0.0")
    L.append("    offsetAngle: 0.0")
    L.append("    rotateAngle: 0.0")
    L.append("    effect:")
    L.append("      atk: 0.0")
    L.append("      abnormalityOnCommon:")
    L.append("        id: $ABN")
    L.append("        abnormalityRate: 1.0")
    L.append("")
    L.append("  _charmAllyArea:")
    L.append("    $extends: _charmArea")
    L.append("    type: allyExceptMe")
    L.append("    maxCount: 19")
    L.append("    maxRadius: 500.0")
    L.append("    selectMethod: dir")
    L.append("")
    L.append("  _charmSelfArea:")
    L.append("    $extends: _charmArea")
    L.append("    type: me")
    L.append("    maxCount: 1")
    L.append("    maxRadius: 30.0")
    L.append("    selectMethod: dist")
    L.append("")
    L.append("  _charmTargetingBase:")
    L.append("    method: normal")
    L.append("    id: -1")
    L.append("    time: 0")
    L.append("    interval: 0")
    L.append("    until: 0")
    L.append("    mpBonusTypeB: 0")
    L.append("    combinedArea: false")
    L.append("    cost:")
    L.append("      hp: 0")
    L.append("      mp: 0")
    L.append("      anger: 0")
    L.append("")
    L.append("  # Single-buff charm skill: buffs the user and nearby allies")
    L.append("  _charmCast:")
    L.append("    $params: [ABN]")
    L.append("    category: Common")
    L.append("    changes:")
    L.append("      targetingLists:")
    L.append("        - targetingIndex: 0")
    L.append("          targetings:")
    L.append("            - $extends: _charmTargetingBase")
    L.append("              areas:")
    L.append("                - $extends: _charmAllyArea")
    L.append("                  $with: { ABN: $ABN }")
    L.append("                - $extends: _charmSelfArea")
    L.append("                  $with: { ABN: $ABN }")
    L.append("")
    L.append("  # Triple charm skill (trios): one buff per kind")
    L.append("  _charmCastTriple:")
    L.append("    $params: [ABN1, ABN2, ABN3]")
    L.append("    category: Common")
    L.append("    changes:")
    L.append("      targetingLists:")
    L.append("        - targetingIndex: 0")
    L.append("          targetings:")
    L.append("            - $extends: _charmTargetingBase")
    L.append("              areas:")
    L.append("                - $extends: _charmAllyArea")
    L.append("                  $with: { ABN: $ABN1 }")
    L.append("                - $extends: _charmSelfArea")
    L.append("                  $with: { ABN: $ABN1 }")
    L.append("                - $extends: _charmAllyArea")
    L.append("                  $with: { ABN: $ABN2 }")
    L.append("                - $extends: _charmSelfArea")
    L.append("                  $with: { ABN: $ABN2 }")
    L.append("                - $extends: _charmAllyArea")
    L.append("                  $with: { ABN: $ABN3 }")
    L.append("                - $extends: _charmSelfArea")
    L.append("                  $with: { ABN: $ABN3 }")
    L.append("")
    L.append("commonSkills:")
    L.append("  update:")
    for skill_id in sorted(skill_buffs):
        recs = [buffs[k] for k in skill_buffs[skill_id]]
        L.append(f"    # {' + '.join(r['name'] for r in recs)}")
        L.append(f"    - id: {skill_id}")
        if len(recs) == 1:
            L.append("      $extends: _charmCast")
            L.append(f"      $with: {{ ABN: {recs[0]['abn_id']} }}")
        else:
            L.append("      $extends: _charmCastTriple")
            L.append(f"      $with: {{ ABN1: {recs[0]['abn_id']}, ABN2: {recs[1]['abn_id']}, ABN3: {recs[2]['abn_id']} }}")
    L.append("")
    L.append("# Spike cleanup: superseded by the roster above.")
    L.append("abnormalities:")
    L.append("  delete:")
    for i in SPIKE_ABN_IDS:
        L.append(f"    - {i}")
    L.append("")
    L.append("abnormalityIconData:")
    L.append("  delete:")
    for i in SPIKE_ABN_IDS:
        L.append(f"    - {i}")
    L.append("")
    L.append("abnormalityStrings:")
    L.append("  delete:")
    for i in SPIKE_ABN_IDS:
        L.append(f"    - {i}")
    L.append("")
    return "\n".join(L)


def emit_design_map(buffs, order, skill_buffs, names):
    L = []
    L.append("# Charm Design Map (generated)")
    L.append("")
    L.append("Authoritative mapping for the charm restoration. Generated by")
    L.append("`tools/dc-restore/gen_charm_specs.py`; edit the generator, not this file.")
    L.append("")
    L.append("Design decisions (user-settled 2026-07-20, 1:1 deterministic model):")
    L.append("")
    L.append("- One buff per charm skill (1:1); buff name and icon match the granting item")
    L.append("  (trio items excepted: their placeholder art is replaced by classic charm icons).")
    L.append("- Deterministic only. Named charms = classic tier-3 (Major) values; greater")
    L.append("  charms = classic tier-4 values; `method=3` multipliers (verified on dev).")
    L.append("- Onslaught/Ethereal/Sanguine I-IV are kind-scoped bundles: every family of the")
    L.append("  kind in one buff at HALF the classic tier bonus. Broad-but-weak vs the focused")
    L.append("  single-family charms; the one-buff-per-kind slot rule makes it a tradeoff.")
    L.append("- Service charms (6/7/8, 31/32/33) share their line's tier-IV bundle skill.")
    L.append("- Trios fill all 3 kind slots: Balder's (81210) and Talisman (201000+) keep")
    L.append("  classic full tier-4 values (scarcity-gated); 98251 grants the 3 Major named")
    L.append("  buffs. Open balance knob: availability, not values.")
    L.append("- Duration 30 minutes; buffs persist through death (`notCareDeath`).")
    L.append("- Kinds: offense 9814, defense 9813, auxiliary 9812; level = tier (equal-or-")
    L.append("  higher replaces, lower does not override).")
    L.append("- Burn burst visuals: classic per-kind `targetEffectId` as `appearEffectId` on")
    L.append("  `FXBottom` (offense 10045001, defense 500245, auxiliary 50171).")
    L.append("- Spike abnormalities 488000003-488000006 deleted in 16-charm-skills, which also")
    L.append("  rewrites the 3 hand-edited spike skills to the clean pattern.")
    L.append("- Skill targeting: user + nearby allies (`allyExceptMe` r500 maxCount 19 + `me`")
    L.append("  r30), the BHS party food-buff pattern (Bleakfields BBQ skill 60950532).")
    L.append("")
    L.append("## Buffs (spec 14)")
    L.append("")
    L.append("| abn id | buff | kind | lvl | effects (type x value) | icon |")
    L.append("|--------|------|------|-----|------------------------|------|")
    for b in order:
        eff = "; ".join(f"t{e['type']} x{e['value']}" for e in b["effects"])
        L.append(f"| {b['abn_id']} | {b['name']} | {b['kind']} | {b['level']} | {eff} | {b['icon'].split('.')[1]} |")
    L.append("")
    L.append("## Items and skills (specs 15 + 16)")
    L.append("")
    L.append("| item | name | flip | skill | buff(s) | abn id(s) |")
    L.append("|------|------|------|-------|---------|-----------|")
    for i, (skill_id, flip) in sorted(ITEMS.items()):
        recs = [buffs[k] for k in skill_buffs[skill_id]]
        L.append(f"| {i} | {names[i]} | {'yes' if flip else 'already DISPOSAL'} | {skill_id} | "
                 + ", ".join(r["name"] for r in recs) + " | "
                 + ", ".join(str(r["abn_id"]) for r in recs) + " |")
    L.append("")
    return "\n".join(L)


def main():
    server_datasheet = resolve_server_datasheet()
    names = read_item_names(server_datasheet)
    buffs, order, skill_buffs = build_buffs(names)
    spec_dir = REFORGED / "specs" / "patches" / "001"
    (spec_dir / "14-charm-abnormalities.yaml").write_text(
        emit_abnormality_spec(order) + "\n", encoding="utf-8", newline="\n")
    (spec_dir / "15-charm-items.yaml").write_text(
        emit_item_spec(buffs, skill_buffs, names) + "\n", encoding="utf-8", newline="\n")
    (spec_dir / "16-charm-skills.yaml").write_text(
        emit_skill_spec(buffs, skill_buffs) + "\n", encoding="utf-8", newline="\n")
    out_doc = REFORGED / "docs" / "plans" / "charm-restoration" / "charm-design-map.md"
    out_doc.write_text(emit_design_map(buffs, order, skill_buffs, names) + "\n", encoding="utf-8", newline="\n")
    print(f"buffs: {len(order)} (ids {order[0]['abn_id']}..{order[-1]['abn_id']})")
    print(f"items: {len(ITEMS)} ({sum(1 for _s, f in ITEMS.values() if f)} flips), skills: {len(skill_buffs)}")
    print("wrote 14-charm-abnormalities.yaml, 15-charm-items.yaml, 16-charm-skills.yaml, charm-design-map.md")


if __name__ == "__main__":
    main()
