"""Referential integrity gate for item ids (read-only).

Every item id referenced anywhere in the server datasheet must resolve to a row in
some `ItemTemplate*.xml`. The shipping corpus maintains that invariant perfectly, and
the failure mode for breaking it is the one this project has already lost days to: a
silent access violation during `WorldServer.exe` startup validation, naming no file.

Born from the IoD reward-vector wave 1 (2026-07-30), which repointed several thousand
item references at once when it flattened the feedstock tiers onto 94101. Phase D's
entire argument for keeping the retired tier rows 94102 to 94112 RESIDENT rather than
deleting them is that dangling references crash the loader; a wave that repoints
thousands of references without a gate proving they all still resolve contradicts its
own reasoning. Neither standing gate (`dungeon_audit.py`, `audit_class_gates.py`)
proves this.

Two independent checks:

  1. RESOLUTION. Every item id referenced by any of the audited families resolves to a
     real `ItemTemplate` row. This is the crash-prevention check.

  2. RETIRED-TIER SWEEP (`--retired`). No LIVE reference to a retired feedstock tier
     (94102 to 94112) survives outside the resident `ItemTemplate` rows themselves.
     This is the wave-1 completeness check, and it is the one with a known-good
     exception, below.

THE KNOWN-GOOD EXCEPTION, and why the gate must not flag it. Vanilla
`MaterialEnchantData` records 10401 and 10402 consume 94104 and are reached by 9 live
items, 163029 to 163037, level-60 superior armour in `ItemTemplate_NAEU.xml`. All 9
carry `enchantEnable="False"`, so the link is inert and no player can reach it. 63
vanilla records consume a retired tier and these two are the only ones any live item
points at, which is why phase B1's claim that all REACHABLE enchanting consumes 94101
still holds. Removing the exception is only correct if those 9 items ever become
enchantable.

Usage:
  python audit_item_references.py                 # resolution check only
  python audit_item_references.py --retired       # plus the retired-tier sweep
  python audit_item_references.py --datasheet <path>
"""

import argparse
import glob
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from decimal import Decimal

from dclib import load_references

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RETIRED = set(range(94102, 94113))
SURVIVING_FEEDSTOCK = 94101

# Records that legitimately keep a retired-tier reference. See the module docstring.
MATERIAL_ENCHANT_EXCEPTION = {10401, 10402}

# The project's own reserved token block, documented in packages/dungeon-tokens/index.yml.
# Every item in it is a currency and must satisfy the restated R21 policy, below.
TOKEN_BAND = (95214, 95313)

# Sum-to-1 bags are compared within this tolerance, never bit-exact. See the long note
# at the check itself: 12 shipped Gacha groups miss 1 by up to 1.47e-8 and the server
# boots on them, so exact equality would fail on untouched vanilla data.
PROB_TOLERANCE = Decimal('0.000001')

# ---------------------------------------------------------------------------
# PRE-EXISTING CORPUS DEBT, measured against server datasheet HEAD cdca4fb4 on
# 2026-07-30. These dangled BEFORE the reward-vector wave and are not its doing.
# ---------------------------------------------------------------------------
# A gate that fails on debt it cannot fix is not a gate, so these are baselined and
# anything NEW fails. Each was proved pre-existing by resolving the same reference
# set against HEAD's row set and diffing, not by assumption.
#
# This also corrects a claim the wave-1 plan leans on. Phase D says "the shipping
# corpus maintains perfect referential integrity on item ids, the only exception
# being the 4 ids our own spec introduced". On the ITEM axis that is nearly right:
# 207328 is one more exception it did not know about. On the STRUCTURAL axis it is
# wrong by 33. The Phase D conclusion still holds (do not delete the retired tier
# rows), because it rests on the crash risk, not on the corpus being spotless.
BASELINE_DANGLING_ITEMS = {
    # A medal currency referenced by BuyList@NeedMedalItemId (2) and
    # ItemMedalExchange@medalItemId (22) with no ItemTemplate row in any variant.
    # Nothing in patch 002 touches it.
    207328,
}
BASELINE_DANGLING_STRUCTURAL = {
    # Vanilla item rows pointing at Decomposition records that do not exist.
    "decompositionId": {7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                        19488, 19489, 19490, 19491, 19492, 19493, 19494, 19495,
                        19496, 19497, 19498, 19833},
    # Vanilla item rows pointing at ItemMix records that do not exist. NOTE none of
    # these is 94101-94112: the wave deleted that ladder AND cleared its twelve
    # back-pointers in the same spec (002/37), so it left nothing dangling.
    "itemMixId": {811, 118077, 118080, 118083, 118086, 160026, 170285, 170286, 206889},
    "linkMaterialEnchantId": set(),
}

# (glob, element tag, attribute) triples. Every one of these attributes holds an
# ItemTemplate id. Chosen as the families the reward-vector wave rewrites, plus the
# item-side back-pointers it clears.
ITEM_REF_SOURCES = [
    ("EnchantData.xml", "EnchantDecomposition", "resultItemTemplateId"),
    ("DecompositionData.xml", "Output", "templateId"),
    ("ItemMixData.xml", "Material", "itemId"),
    ("ItemMixData.xml", "Result", "successItemId"),
    ("ItemMixData.xml", "Result", "failedItemId"),
    ("MaterialEnchantData.xml", "Material", "id"),
    ("CompensationData/ECompensation_*.xml", "Item", "templateId"),
    ("CompensationData/QuestCompensationData_*.xml", "Item", "templateId"),
    ("CompensationData/CCompensation_*.xml", "Item", "templateId"),
    ("Gacha*.xml", "Reward", "itemTemplateId"),
    ("ItemConversion*.xml", "ResultItem", "itemTemplateId"),
    ("ItemConversion*.xml", "SeedItem", "itemTemplateId"),
    ("AchievementList*.xml", "ItemReward", "templateId"),
    ("EventMatching.xml", "Compensation", "templateId"),
    ("BuyList.xml", "Item", "itemId"),
    ("BuyList.xml", "List", "NeedMedalItemId"),
    ("ItemMedalExchange.xml", "Exchange", "itemId"),
    ("ItemMedalExchange.xml", "Exchange", "medalItemId"),
    ("StackAttendanceEvent.xml", "Reward", "itemTemplateId"),
]

# Non-item cross-references the wave also repointed. Each is (glob, tag, attr) on the
# referencing side and (glob, tag, attr) on the defining side.
STRUCTURAL_REFS = [
    ("linkMaterialEnchantId",
     ("ItemTemplate*.xml", "Item", "linkMaterialEnchantId"),
     ("MaterialEnchantData.xml", "ItemEnchant", "materialEnchantId")),
    ("decompositionId",
     ("ItemTemplate*.xml", "Item", "decompositionId"),
     ("DecompositionData.xml", "Decomposition", "id")),
    ("itemMixId",
     ("ItemTemplate*.xml", "Item", "itemMixId"),
     ("ItemMixData.xml", "ItemMix", "itemMixId")),
]


OWNER_ATTRS = ("materialEnchantId", "itemMixId", "questId", "id")


def collect(ds, pattern, tag, attr):
    """[(value, file, owner)] for every <tag attr=...> under the glob.

    `owner` is the id of the nearest ENCLOSING record, never the matched element's
    own id. Getting that backwards makes `MaterialEnchantData` report each material
    as its own owner instead of the `ItemEnchant@materialEnchantId` that contains it,
    which is exactly what the 10401/10402 exception needs to match on.
    """
    out = []
    for path in sorted(glob.glob(os.path.join(ds, pattern))):
        name = os.path.relpath(path, ds)
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            print(f"  ! unparseable: {name}: {exc}")
            continue

        def walk(el, owner):
            if el.tag == tag:
                v = el.get(attr)
                if v not in (None, "", "0"):
                    try:
                        out.append((int(v), name, owner))
                    except ValueError:
                        pass
            child_owner = owner
            for a in OWNER_ATTRS:
                if el.get(a) is not None:
                    child_owner = el.get(a)
                    break
            for c in el:
                walk(c, child_owner)

        walk(root, None)
    return out


def load_item_ids(ds):
    ids = set()
    for path in sorted(glob.glob(os.path.join(ds, "ItemTemplate*.xml"))):
        for _, el in ET.iterparse(path, events=("end",)):
            if el.tag == "Item":
                v = el.get("id")
                if v is not None:
                    ids.add(int(v))
            el.clear()
    return ids


def load_enchant_enable(ds):
    """item id -> enchantEnable, for judging whether a retired-tier link is reachable."""
    out = {}
    for path in sorted(glob.glob(os.path.join(ds, "ItemTemplate*.xml"))):
        for _, el in ET.iterparse(path, events=("end",)):
            if el.tag == "Item":
                v = el.get("id")
                if v is not None:
                    out[int(v)] = (el.get("enchantEnable", "") or "").lower() == "true"
            el.clear()
    return out


def main():
    ap = argparse.ArgumentParser(description="Item-id referential integrity gate.")
    ap.add_argument("--datasheet", help="server datasheet root (default: from .references)")
    ap.add_argument("--retired", action="store_true",
                    help="also sweep for live references to retired feedstock tiers")
    args = ap.parse_args()

    ds = args.datasheet or load_references()["server_datasheet"]

    print(f"Datasheet: {ds}\n")
    item_ids = load_item_ids(ds)
    print(f"ItemTemplate rows: {len(item_ids)}\n")

    failures = []

    # ---- check 1: every referenced item id resolves -------------------------------
    print("== Resolution ==")
    total_refs = 0
    for pattern, tag, attr in ITEM_REF_SOURCES:
        refs = collect(ds, pattern, tag, attr)
        if not refs:
            print(f"  {pattern:<45} {tag}@{attr:<20} 0 refs  (family absent or empty)")
            continue
        total_refs += len(refs)
        dangling, baselined = defaultdict(list), 0
        for val, fname, owner in refs:
            if val in item_ids:
                continue
            if val in BASELINE_DANGLING_ITEMS:
                baselined += 1
                continue
            dangling[val].append((fname, owner))
        mark = "OK" if not dangling else f"DANGLING {len(dangling)}"
        if baselined:
            mark += f", {baselined} baselined"
        print(f"  {pattern:<45} {tag}@{attr:<20} {len(refs):>6} refs  [{mark}]")
        for val, where in sorted(dangling.items()):
            sample = ", ".join(f"{f}:{o}" for f, o in where[:3])
            failures.append(f"item {val} referenced by {tag}@{attr} but has no "
                            f"ItemTemplate row ({len(where)} refs, e.g. {sample})")
    print(f"\n  {total_refs} item references checked\n")

    # ---- check 1b: structural cross-references resolve ----------------------------
    print("== Structural cross-references ==")
    for label, (rp, rt, ra), (dp, dt, da) in STRUCTURAL_REFS:
        defined = {v for v, _, _ in collect(ds, dp, dt, da)}
        used = collect(ds, rp, rt, ra)
        base = BASELINE_DANGLING_STRUCTURAL.get(label, set())
        allbad = {v for v, _, _ in used if v not in defined}
        bad = sorted(allbad - base)
        healed = sorted(base - allbad)
        mark = "OK" if not bad else f"NEW DANGLING {len(bad)}"
        if allbad & base:
            mark += f", {len(allbad & base)} baselined"
        print(f"  {label:<22} {len(used):>6} refs -> {len(defined):>5} definitions  [{mark}]")
        for v in bad[:10]:
            failures.append(f"{label} {v} referenced but no matching {dt}@{da} record "
                            f"(NOT in the pre-existing baseline: this is new breakage)")
        if len(bad) > 10:
            failures.append(f"{label}: {len(bad) - 10} further NEW dangling ids not listed")
        if healed:
            print(f"    note: {len(healed)} baselined id(s) now resolve: {healed}. "
                  f"Trim them from BASELINE_DANGLING_STRUCTURAL.")
    print()

    # ---- check 1c: loader invariants on ItemTemplate --------------------------------
    # Not a reference check, but the same failure class the rest of this gate exists to
    # prevent: WorldServer.exe refusing the datasheet at startup. Added 2026-07-30 after
    # the reward-vector wave shipped item 95217 as maxStack 10000 + boundType Loot and
    # the dev server rejected ItemTemplate.xml outright with
    #   "stackable item cannot specify boundType [ItemTID=95217][boundType=1]"
    # This one is LOUD (the loader names the item), unlike the dangling-reference case,
    # but it still costs a deploy and a restart cycle to find. The corpus states the
    # rule unambiguously: all 3,803 boundType:Loot rows are maxStack 1, and all 25,073
    # stackable rows are boundType:None.
    print("== ItemTemplate loader invariants ==")
    stackable_bound = []
    for path in sorted(glob.glob(os.path.join(ds, "ItemTemplate*.xml"))):
        rel = os.path.relpath(path, ds)
        for _, el in ET.iterparse(path, events=("end",)):
            if el.tag == "Item":
                try:
                    stack = int(el.get("maxStack") or 1)
                except ValueError:
                    stack = 1
                bound = (el.get("boundType") or "None").lower()
                if stack > 1 and bound != "none":
                    stackable_bound.append((el.get("id"), stack, el.get("boundType"), rel))
            el.clear()
    mark = "OK" if not stackable_bound else f"REJECTED BY LOADER {len(stackable_bound)}"
    print(f"  stackable items carrying a boundType (must be 0)  [{mark}]")
    for iid, stack, bound, rel in stackable_bound:
        failures.append(f"item {iid} in {rel} has maxStack={stack} AND boundType={bound}; "
                        f"the world server refuses ItemTemplate with 'stackable item "
                        f"cannot specify boundType'. Drop boundType, or set maxStack 1")
    print()

    # ---- check 1e: sum-to-1 probability bags ---------------------------------------
    # Added 2026-07-30 after the world server refused to boot on
    #   randomReward invalid probability prov [itemTemplateId=19321] [0.900000]
    # (the id is the BOX, not a reward row). Phase C3 deleted weighted rows from
    # <RandomReward> groups; `dsl validate` passed, every gate passed, and 81 groups
    # across 6 Gacha files no longer summed to 1. Filed as
    # docs/dsl-requests/2026-07-30-probability-bag-sum-not-validated.md.
    #
    # ONLY these two collections are checked, and the restraint is the point. Measured
    # over server HEAD:
    #   Gacha/RandomReward/Reward          3,597 groups, 3,597 sum to 1   sum-to-1 bag
    #   DecompositionData/RandomOutput     139 groups,   139 sum to 1     sum-to-1 bag
    #   ECompensation/Compensation/ItemBag 704 groups,    30 sum to 1     independent
    #   ECompensation/ItemBag/Item       3,363 groups, 3,337 sum to 1     independent
    # That last row is the trap: 99.2 percent is NOT an invariant, and treating it as
    # one would reject valid specs. It is why 002/41 can delete 1,785 whole ItemBags.
    #
    # THE COMPARISON IS TOLERANT, AND IT HAS TO BE. "Sums to 1" above means within
    # 1e-6, not bit-exact. 12 shipped Gacha groups miss exactly 1 by up to 1.47e-8
    # because the author's own decimals do not add up (e.g. Gacha_KR 148329, 498 rows,
    # 0.999999999999999743). All 12 pre-date this wave and the server boots on them
    # happily, so exact equality would fail the gate on untouched vanilla data. The
    # server rejected a 0.1 deviation and accepts 1.5e-8; the true threshold is
    # somewhere between and is not knowable from the data, so this sits two orders of
    # magnitude above the observed corpus noise and far below anything meaningful.
    print("== Sum-to-1 probability bags ==")
    for label, pattern, group_tag, row_tag in [
            ("Gacha / RandomReward", "Gacha*.xml", "RandomReward", "Reward"),
            ("DecompositionData / RandomOutput", "DecompositionData.xml",
             "RandomOutput", "Output")]:
        checked, broken, noise, worst = 0, [], 0, Decimal(0)
        for path in sorted(glob.glob(os.path.join(ds, pattern))):
            rel = os.path.relpath(path, ds)
            root = ET.parse(path).getroot()
            for owner in root:
                oid = owner.get("itemTemplateId") or owner.get("id")
                for grp in owner:
                    if grp.tag != group_tag:
                        continue
                    probs = [Decimal(r.get("probability") or "0")
                             for r in grp if r.tag == row_tag]
                    if not probs:
                        continue
                    checked += 1
                    dev = abs(sum(probs) - Decimal(1))
                    worst = max(worst, dev)
                    if dev > PROB_TOLERANCE:
                        broken.append((rel, oid, grp.get("class"), sum(probs), len(probs)))
                    elif dev:
                        noise += 1
        mark = "OK" if not broken else f"INVALID {len(broken)}"
        print(f"  {label:<36} {checked:>6} groups  [{mark}]"
              f"   worst deviation {worst:.3e}, {noise} within tolerance")
        for rel, oid, cls, total, n in broken[:10]:
            failures.append(f"{label} in {rel}: owner {oid} class={cls!r} has {n} rows "
                            f"summing to {total}, not 1. The world server refuses this "
                            f"with 'invalid probability prov'. Rebalance the survivors")
        if len(broken) > 10:
            failures.append(f"{label}: {len(broken) - 10} further invalid groups not listed")
    print()

    # ---- check 1d: token restriction policy ---------------------------------------
    # USER RULING 2026-07-30, which restates backlog R21. Tokens are restricted by
    # `tradable: false` AND `guildWarehouseStorable: false`, never by `boundType`:
    # boundType is for EQUIPMENT the character wears, while a token is a consumable
    # currency whose only real requirement is that it not move between PLAYERS, and
    # those two flags are exactly what gate that. `warehouseStorable` is deliberately
    # NOT checked: the personal bank is same-account only, so it moves nothing between
    # players and blocking it would only inconvenience the owner.
    print("== Token restriction policy (reserved band "
          f"{TOKEN_BAND[0]}-{TOKEN_BAND[1]}) ==")
    tokens, offenders = [], []
    for path in sorted(glob.glob(os.path.join(ds, "ItemTemplate*.xml"))):
        rel = os.path.relpath(path, ds)
        for _, el in ET.iterparse(path, events=("end",)):
            if el.tag == "Item":
                iid = int(el.get("id"))
                if TOKEN_BAND[0] <= iid <= TOKEN_BAND[1]:
                    tr = (el.get("tradable") or "").lower()
                    gw = (el.get("guildWarehouseStorable") or "").lower()
                    tokens.append((iid, tr, gw))
                    if tr != "false" or gw != "false":
                        offenders.append((iid, tr, gw, rel))
            el.clear()
    print(f"  tokens found: {sorted(t[0] for t in tokens)}")
    mark = "OK" if not offenders else f"POLICY VIOLATION {len(offenders)}"
    print(f"  all carry tradable=false and guildWarehouseStorable=false  [{mark}]")
    for iid, tr, gw, rel in offenders:
        failures.append(f"token {iid} in {rel} has tradable={tr or '<unset>'} "
                        f"guildWarehouseStorable={gw or '<unset>'}; both must be false "
                        f"(restated R21). Do NOT reach for boundType instead")
    print()

    # ---- check 2: retired-tier sweep ----------------------------------------------
    if args.retired:
        print("== Retired feedstock tiers 94102-94112 ==")
        enchantable = load_enchant_enable(ds)
        resident = sorted(t for t in RETIRED if t in item_ids)
        print(f"  resident ItemTemplate rows (expected, phase D): {resident}")

        # REACHABILITY is the test, not mere presence. Phase B1's claim is that all
        # REACHABLE enchanting consumes 94101; the corpus also carries dormant vanilla
        # records that consume a retired tier and that NO live item links to. Those are
        # not a wave defect, they are data nobody can get to. So a MaterialEnchantData
        # record only counts against the sweep when some live ItemTemplate row points
        # at it via linkMaterialEnchantId.
        linked = {v for v, _, _ in collect(ds, "ItemTemplate*.xml", "Item",
                                           "linkMaterialEnchantId")}

        live, dormant, excused = defaultdict(list), 0, 0
        for pattern, tag, attr in ITEM_REF_SOURCES:
            for val, fname, owner in collect(ds, pattern, tag, attr):
                if val not in RETIRED:
                    continue
                if fname.startswith("MaterialEnchantData"):
                    rec = int(owner) if owner and owner.isdigit() else None
                    if rec is not None and rec not in linked:
                        dormant += 1
                        continue
                    if rec in MATERIAL_ENCHANT_EXCEPTION:
                        excused += 1
                        continue
                live[val].append((fname, tag, attr, owner))

        print(f"  dormant MaterialEnchantData refs (record reached by no live item): "
              f"{dormant}")
        print(f"  excused by the known-good exception (records "
              f"{sorted(MATERIAL_ENCHANT_EXCEPTION)}): {excused} ref(s)")
        if live:
            for val, where in sorted(live.items()):
                sample = ", ".join(f"{f} {t}@{a} in {o}" for f, t, a, o in where[:3])
                failures.append(f"retired tier {val} still REACHABLE, {len(where)} "
                                f"reference(s): {sample}")
            print(f"  UNEXPECTED reachable references: "
                  f"{sum(len(v) for v in live.values())}")
        else:
            print("  UNEXPECTED reachable references: 0  [OK]")

        # The exception is only inert while those 9 items stay unenchantable.
        hot = sorted(i for i in range(163029, 163038) if enchantable.get(i))
        if hot:
            failures.append(f"items {hot} now carry enchantEnable=true, so the "
                            f"MaterialEnchantData {sorted(MATERIAL_ENCHANT_EXCEPTION)} "
                            f"exception is no longer inert and must be re-examined")
        else:
            print("  exception still inert: all of 163029-163037 carry "
                  "enchantEnable=False  [OK]")

        mats = collect(ds, "MaterialEnchantData.xml", "Material", "id")
        n94101 = sum(1 for v, _, _ in mats if v == SURVIVING_FEEDSTOCK)
        print(f"  MaterialEnchantData rows consuming {SURVIVING_FEEDSTOCK}: "
              f"{n94101} of {len(mats)}")
        print()

    if failures:
        print(f"RESULT: FAIL ({len(failures)} problem(s))")
        for f in failures:
            print("  " + f)
        return 1
    print("RESULT: PASS (0 dangling item references)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
