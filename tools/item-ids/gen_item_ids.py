#!/usr/bin/env python3
"""
Item-id registry generator: constant names + conflict-avoidance occupied set.

Reads ALL ItemTemplate*.xml (the full item universe, ids disjoint across files) and
all StrSheet_Item*.xml (display names), both streamed with iterparse for determinism
over 45MB+ files. Produces two things:

  occupied : the exact set of occupied item ids, as compact ranges, written to
             tools/item-ids/occupied_ids.json. Conflict-avoidance is a membership test
             against this set, never an id-range prediction.

  names    : demand-driven constant shards under packages/item-ids/. Names only the ids
             you ask for (via --from-spec or --ids), skipping any id already named in
             another package. Constant = SLUG(displayName)_<id> (id suffix guarantees
             uniqueness; no name source is unique on its own). Sharded by item class so
             a spec imports only what it needs.

  check    : report which of the given ids are free vs occupied (reads occupied_ids.json).

Determinism: sorted iteration, streaming parse, no timestamps.

Usage:
  python gen_item_ids.py occupied --datasheet <server_datasheet>
  python gen_item_ids.py names    --datasheet <server_datasheet> --from-spec <spec.yaml>
  python gen_item_ids.py names    --datasheet <server_datasheet> --ids 21351,94203,649
  python gen_item_ids.py check    --ids 700000,602176
"""

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]                      # reforged/
PKG_DIR = PROJECT / "packages" / "item-ids"
OCCUPIED_JSON = HERE / "occupied_ids.json"


# ── streaming loaders ─────────────────────────────────────────────────────────
def load_items(ds):
    """id -> (internal_name, combatItemType, category, suffix). Union of all files.

    `suffix` records the item's owning file variant ("" for base, "_KR", "_NAEU", ...)
    so its display name is looked up in the MATCHING StrSheet, not a clobbered merge.
    """
    items = {}
    for f in sorted(glob.glob(os.path.join(ds, "ItemTemplate*.xml"))):
        suf = os.path.basename(f)[len("ItemTemplate"):-len(".xml")]
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == "Item":
                iid = el.get("id")
                if iid is not None:
                    items[int(iid)] = (el.get("name", ""),
                                       el.get("combatItemType", ""),
                                       el.get("category", ""), suf)
                el.clear()
    return items


def load_strings(ds):
    """suffix -> {id: display}. Per-variant, because StrSheet ids are NOT disjoint across
    region files: a regional sheet re-lists base ids with localized strings, so a global
    merge would overwrite good base names."""
    per = defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(ds, "StrSheet_Item*.xml"))):
        suf = os.path.basename(f)[len("StrSheet_Item"):-len(".xml")]
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == "String":
                i = el.get("id")
                if i is not None:
                    per[suf][int(i)] = el.get("string", "") or ""
                el.clear()
    return per


def to_ranges(ids):
    """Compact a set of ids into sorted [start, end] inclusive ranges."""
    out = []
    for i in sorted(ids):
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return out


def occupied_from_ranges(ranges):
    return ranges  # kept as ranges; membership scans ranges (few thousand entries)


def id_taken(iid, ranges):
    lo, hi = 0, len(ranges) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        a, b = ranges[mid]
        if iid < a:
            hi = mid - 1
        elif iid > b:
            lo = mid + 1
        else:
            return True
    return False


# ── naming ────────────────────────────────────────────────────────────────────
def slug(display, internal, iid):
    for src in (display, internal):
        s = re.sub(r"\(.*?\)", "", src or "")          # drop parenthetical qualifiers
        s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").upper()
        if s:
            if s[0].isdigit():                         # DSL var names must start [A-Za-z_]
                s = "ITEM_" + s
            return f"{s}_{iid}"
    return f"ITEM_{iid}"


def shard_for(cit, cat):
    if cit in ("EQUIP_WEAPON", "EQUIP_STYLE_WEAPON"):
        return "gear-weapons"
    if cit in ("EQUIP_ARMOR_BODY", "EQUIP_ARMOR_ARM", "EQUIP_ARMOR_LEG",
               "EQUIP_UNDERWEAR", "EQUIP_STYLE_BODY"):
        return "gear-armor"
    if cit in ("EQUIP_ACCESSORY", "EQUIP_STYLE_ACCESSORY", "CREST"):
        return "gear-accessories"
    if cit == "RECIPE":
        return "recipes"
    if cit == "SKILLBOOK":
        return "skillbooks"
    if cit in ("GACHA", "MEDAL_USEABLE"):
        return "tokens-boxes"
    if (cat or "").lower().find("material") >= 0 or cat in ("generalMaterial", "fabrication"):
        return "materials"
    if cit in ("NO_COMBAT", "DISPOSAL"):
        return "consumables"
    return "misc"


def spec_template_ids(spec_path):
    import yaml
    doc = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    found = set()

    def walk(n):
        if isinstance(n, dict):
            for k, v in n.items():
                if k == "templateId" and isinstance(v, int) and not isinstance(v, bool):
                    found.add(v)
                walk(v)
        elif isinstance(n, list):
            for e in n:
                walk(e)

    walk(doc)
    return found


# npc template ids and item template ids are SEPARATE id spaces: the same integer is a
# different entity in each (1001 = npc Vekas AND item Coarse Fiber). So npc-ids naming an
# id must NOT block item-ids from naming the item that shares that number. item-ids also
# excludes itself so it never treats its own prior output as a reason to skip.
NON_ITEM_PACKAGES = {"npc-ids", "item-ids"}


def load_registry_values(packages_root):
    """Set of ints already named by some other ITEM-domain package."""
    sys.path.insert(0, str(HERE.parent / "spec-standardize"))
    from analyze_ids import load_registry  # reuse the reconciler
    reg = load_registry(str(packages_root))
    return {v for v, lst in reg.items()
            if any(pkg not in NON_ITEM_PACKAGES for (pkg, _n, _e, _k) in lst)}


# ── writers ───────────────────────────────────────────────────────────────────
def q(s):
    return s


def write_shards(shards):
    """shards: name -> list of (const, id). Writes shard files + index.yml."""
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    for old in PKG_DIR.glob("*.yml"):   # clear stale shards for a deterministic tree
        old.unlink()
    for name, entries in sorted(shards.items()):
        entries = sorted(entries, key=lambda e: e[1])
        lines = [
            f"# item-ids : {name}",
            f"# Generated by tools/item-ids/gen_item_ids.py (do not hand-edit).",
            f"# Constant = SLUG(display name)_<id>; the id suffix guarantees uniqueness.",
            "",
            "spec:",
            '  version: "1.0"',
            "",
            "variables:",
        ]
        for const, iid in entries:
            lines.append(f"  {const}: {iid}")
        lines += ["", "exports:", "  variables:"]
        for const, _ in entries:
            lines.append(f"    - {const}")
        (PKG_DIR / f"{name}.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # index.yml imports every shard and re-exports its variables (crystals convention).
    idx = [
        "# Item ID registry (demand-driven constant names).",
        "# Generated by tools/item-ids/gen_item_ids.py (do not hand-edit).",
        "#",
        "# Sharded by item class so a spec imports only the shard it needs. Each constant",
        "# is SLUG(display name)_<id>. Names cover only ids that specs reference; the id",
        "# universe (conflict-avoidance) lives in tools/item-ids/occupied_ids.json.",
        "",
        "spec:",
        '  version: "1.0"',
        "",
        "imports:",
    ]
    for name, entries in sorted(shards.items()):
        idx.append(f"  - from: ./{name}.yml")
        idx.append("    use:")
        idx.append("      variables:")
        for const, _ in sorted(entries, key=lambda e: e[1]):
            idx.append(f"        - {const}")
    idx += ["", "exports:", "  variables:"]
    for name, entries in sorted(shards.items()):
        for const, _ in sorted(entries, key=lambda e: e[1]):
            idx.append(f"    - {const}")
    (PKG_DIR / "index.yml").write_text("\n".join(idx) + "\n", encoding="utf-8")


# ── modes ─────────────────────────────────────────────────────────────────────
def do_occupied(args):
    items = load_items(args.datasheet)
    ranges = to_ranges(items.keys())
    OCCUPIED_JSON.write_text(json.dumps({"count": len(items), "ranges": ranges},
                                        ensure_ascii=False), encoding="utf-8")
    print(f"occupied ids: {len(items)} across {len(ranges)} ranges -> {OCCUPIED_JSON}")


def do_names(args):
    items = load_items(args.datasheet)
    disp = load_strings(args.datasheet)
    named = load_registry_values(PROJECT / "packages")

    if args.from_spec:
        targets = spec_template_ids(args.from_spec)
    else:
        targets = {int(x) for x in args.ids.split(",") if x.strip()}

    shards = defaultdict(list)
    skipped_registered, skipped_absent = [], []
    for iid in sorted(targets):
        if iid not in items:
            skipped_absent.append(iid)
            continue
        if iid in named:
            skipped_registered.append(iid)
            continue
        internal, cit, cat, suf = items[iid]
        # Base StrSheet_Item.xml is the English sheet; prefer it. Fall back to the item's
        # own regional sheet only when base lacks the id, then to the internal name.
        name = disp.get("", {}).get(iid) or disp.get(suf, {}).get(iid) or ""
        const = slug(name, internal, iid)
        shards[shard_for(cit, cat)].append((const, iid))

    write_shards(shards)
    total = sum(len(v) for v in shards.values())
    print(f"named {total} items into {len(shards)} shard(s): "
          f"{', '.join(sorted(shards))}")
    print(f"  skipped {len(skipped_registered)} already named elsewhere: {skipped_registered}")
    print(f"  skipped {len(skipped_absent)} not items in ItemTemplate*: {skipped_absent}")


def do_check(args):
    data = json.loads(OCCUPIED_JSON.read_text(encoding="utf-8"))
    ranges = data["ranges"]
    for x in args.ids.split(","):
        x = x.strip()
        if not x:
            continue
        iid = int(x)
        print(f"  {iid}: {'TAKEN' if id_taken(iid, ranges) else 'FREE'}")


def main():
    ap = argparse.ArgumentParser(description="Item-id registry generator.")
    sub = ap.add_subparsers(dest="mode", required=True)

    o = sub.add_parser("occupied"); o.add_argument("--datasheet", required=True)
    o.set_defaults(func=do_occupied)

    n = sub.add_parser("names")
    n.add_argument("--datasheet", required=True)
    g = n.add_mutually_exclusive_group(required=True)
    g.add_argument("--from-spec")
    g.add_argument("--ids")
    n.set_defaults(func=do_names)

    c = sub.add_parser("check"); c.add_argument("--ids", required=True)
    c.set_defaults(func=do_check)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
