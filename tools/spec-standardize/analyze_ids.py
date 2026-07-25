#!/usr/bin/env python3
"""
Corpus-scope id-registry detection for DSL specs.

Complements analyze.py (structural block factoring). Where that tool factors repeated
STRUCTURE into `$extends` templates, this one finds repeated VALUES (ids) that should
be named constants in an ID-registry package, and it reconciles against the registries
that already exist so it can tell "hardcoded but already named elsewhere" from "not
named anywhere yet". Read-only: it advises, the refactor happens in the generator/spec.

Spec-agnostic by construction (see the design notes in README):
  - It never keys off a hardcoded field name like `templateId`. A value's "id-ness" is
    inferred from STRUCTURAL signals: large-int value profile, a functionally-dependent
    string sibling (the label, discovered by stable co-occurrence, not by key name),
    and multi-context cross-reference. Key-name morphology (`.*id$`) is a soft weight
    only, never a gate.
  - "Label" = a sibling scalar whose value is constant across every occurrence of the
    id value and is string-typed. The key it sits under is irrelevant.

Two finding classes:
  1. ALREADY NAMED  - the literal is already exported by a registry package; the spec
     could import that existing constant instead of hardcoding the magic number.
  2. UNREGISTERED   - a recurring id that no package names yet. The tool only FLAGS
     these (value, frequency, where used); it does NOT invent a constant name and does
     NOT surface the co-located label, so the observed string cannot be mistaken for a
     suggested name. Naming an unregistered id is a case-by-case decision resolved from
     the authoritative source (StrSheet / datasheet MCP), which this tool stays
     decoupled from. A stable label is still used INTERNALLY to decide id-ness (and to
     reject shared category labels), but it is never printed.

Prints the analysis to stdout; writes no files.

Usage:
    python analyze_ids.py [--specs-root specs/patches] [--packages-root packages]
                          [--min-id-value 1000] [--min-new-freq 2]
                          [--min-already-freq 2] [--top 40]
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml

from _walk import iter_scalar_occurrences

KEYNAME_ID = re.compile(r"(?i)(^id$|id$|ref$)")
LABEL_KEY_HINT = re.compile(r"(?i)(name|title|label|desc)")


# ── Registry side: what values already have named constants ──────────────────
def extract_int_vars(vars_block, pkg, exported, out):
    """Record value -> (package, varname, exported, kind) from a `variables:` block."""
    if not isinstance(vars_block, dict):
        return
    for name, val in vars_block.items():
        if isinstance(val, bool):
            continue
        if isinstance(val, int):
            out[val].append((pkg, name, name in exported, "scalar"))
        elif isinstance(val, list):
            for e in val:
                if isinstance(e, int) and not isinstance(e, bool):
                    out[e].append((pkg, name, name in exported, "member"))


def load_registry(packages_root):
    """value -> list of (package, varname, exported, kind) across every package file."""
    reg = defaultdict(list)
    for f in sorted(Path(packages_root).rglob("*.yml")):
        try:
            doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        pkg = f.relative_to(packages_root).parts[0]
        exp = doc.get("exports", {})
        exported = set((exp.get("variables") or []) if isinstance(exp, dict) else [])
        extract_int_vars(doc.get("variables"), pkg, exported, reg)
    return reg


# ── Spec side: where int literals are hardcoded ──────────────────────────────
def scan_specs(specs_root):
    """int value -> list of occurrence dicts {key, path, spec, siblings}."""
    occ = defaultdict(list)
    for f in sorted(Path(specs_root).rglob("*.yaml")):
        try:
            doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        rel = str(f)
        for key, val, path, parent in iter_scalar_occurrences(doc, "", None):
            if isinstance(val, bool) or not isinstance(val, int):
                continue
            if path.startswith("variables"):
                continue  # a spec's own variable defs, not hardcoded usages
            siblings = {k: v for k, v in parent.items()
                        if k != key and not isinstance(v, (dict, list))}
            occ[val].append({"key": key, "path": path, "spec": rel, "siblings": siblings})
    return occ


# ── Id-ness inference (structural, key-name-free) ────────────────────────────
def stable_label(records):
    """Best functionally-dependent string sibling of this value, or None.

    A sibling key qualifies when it is present in every occurrence and its value is a
    single constant STRING across all of them (the value determines it). The key name
    is never required to be `name`; it only breaks ties.
    """
    if not records:
        return None
    common = set(records[0]["siblings"])
    for r in records[1:]:
        common &= set(r["siblings"])
    candidates = []
    for k in common:
        vals = {r["siblings"][k] for r in records}
        if len(vals) == 1:
            (v,) = vals
            if isinstance(v, str) and v.strip():
                candidates.append((k, v))
    if not candidates:
        return None
    # Tie-break: prefer a label-shaped key name, then the shorter value.
    candidates.sort(key=lambda kv: (0 if LABEL_KEY_HINT.search(str(kv[0])) else 1,
                                    len(kv[1])))
    return candidates[0]  # (key, label)


def score(records, has_label, keyname_hit):
    distinct_keys = {str(r["key"]) for r in records}
    distinct_specs = {r["spec"] for r in records}
    multipath = len(distinct_keys) >= 2 or len(distinct_specs) >= 2
    s = len(records) + (3 if has_label else 0) + (2 if multipath else 0) + (1 if keyname_hit else 0)
    return s, multipath, sorted(distinct_keys), sorted(distinct_specs)


def load_occupied(path):
    """Load the item-universe occupied-id ranges (tools/item-ids/occupied_ids.json)."""
    import json
    return json.loads(Path(path).read_text(encoding="utf-8"))["ranges"]


def in_ranges(iid, ranges):
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


def build_report(specs_root, packages_root, min_id_value, min_new_freq, min_already_freq,
                 occupied_ranges=None):
    registry = load_registry(packages_root)
    occ = scan_specs(specs_root)

    # An IDENTITY label is near-unique to its value; a CATEGORY label (e.g. the gold-bag
    # name shared by every gold amount) maps to many distinct values. The label-only
    # fallback must reject category labels, otherwise quantities that merely sit next to
    # a shared name (gold min/max) get mistaken for ids. Fully generic: no key names.
    label_values = defaultdict(set)
    for value, all_records in occ.items():
        has_id_key = any(isinstance(r["key"], str) and KEYNAME_ID.search(r["key"])
                         for r in all_records)
        if not has_id_key:
            lab = stable_label(all_records)
            if lab:
                label_values[lab[1]].add(value)

    already, unregistered = [], []
    for value, all_records in occ.items():
        if value < min_id_value:
            continue
        # Restrict to id-CONTEXT occurrences: the same integer can be an id under
        # `templateId` and a stat under `minAtk`. Keep only occurrences whose key is
        # id-shaped; if none are but the value carries a stable, IDENTITY-specific label
        # everywhere, treat the whole set as id-like. This is the structural "is this
        # field an id" test, derived per-key rather than from a hardcoded field list.
        id_records = [r for r in all_records
                      if isinstance(r["key"], str) and KEYNAME_ID.search(r["key"])]
        if id_records:
            records = id_records
            keyname_hit = True
            lab = stable_label(records)
        else:
            lab = stable_label(all_records)
            if lab is None:
                continue  # neither an id-shaped key nor a stable label: not an id
            if len(label_values[lab[1]]) > 1:
                continue  # category label shared across values, not an identity: not an id
            records = all_records
            keyname_hit = False
        has_label = lab is not None
        sc, multipath, keys, specs = score(records, has_label, keyname_hit)

        entry = {
            "value": value, "frequency": len(records), "score": sc,
            "used_under_keys": keys, "used_in_specs": [Path(s).name for s in specs],
            "multipath": multipath,
            # None if no occupied set supplied; else True/False for "exists as an item".
            "in_item_universe": (in_ranges(value, occupied_ranges)
                                 if occupied_ranges is not None else None),
        }

        if value in registry:
            names = registry[value]
            exported = sorted({f"{p}.{n}" for (p, n, ex, kind) in names if ex and kind == "scalar"})
            any_name = sorted({f"{p}.{n}" for (p, n, ex, kind) in names})
            entry["registry_names"] = any_name
            entry["importable"] = exported
            # A value that resolves to more than one distinct constant is ambiguous:
            # ids collide across zones (1001 = IOD_VEKAS and KL_CULTIST_DEVASTATOR), so
            # the human must pick the context-correct one; flag rather than auto-pick.
            entry["ambiguous"] = len(exported) > 1
            if len(records) >= min_already_freq:
                already.append(entry)
        else:
            if len(records) >= min_new_freq:
                unregistered.append(entry)

    already.sort(key=lambda e: (-e["frequency"], e["value"]))
    unregistered.sort(key=lambda e: (-e["score"], -e["frequency"], e["value"]))
    return {
        "specs_root": str(specs_root), "packages_root": str(packages_root),
        "params": {"min_id_value": min_id_value, "min_new_freq": min_new_freq,
                   "min_already_freq": min_already_freq},
        "already_named": already, "unregistered": unregistered,
        "occupied_checked": occupied_ranges is not None,
        "summary": {"already_named": len(already), "unregistered": len(unregistered),
                    "already_ambiguous": sum(1 for e in already if e["ambiguous"]),
                    "unregistered_real_items": sum(1 for e in unregistered
                                                   if e["in_item_universe"]),
                    "unregistered_non_items": sum(1 for e in unregistered
                                                  if e["in_item_universe"] is False)},
    }


# ── Rendering ─────────────────────────────────────────────────────────────────
def render_md(rep, top):
    if top <= 0:  # 0 (or negative) means no row cap: print every finding
        top = max(len(rep["already_named"]), len(rep["unregistered"]))
    p = rep["params"]
    L = [f"# Id-registry analysis\n",
         f"specs: `{rep['specs_root']}`  ·  packages: `{rep['packages_root']}`  ·  "
         f"min-id-value={p['min_id_value']}, min-new-freq={p['min_new_freq']}, "
         f"min-already-freq={p['min_already_freq']}\n",
         f"**{rep['summary']['already_named']}** hardcoded literals already named in a "
         f"package ({rep['summary']['already_ambiguous']} ambiguous) · "
         f"**{rep['summary']['unregistered']}** recurring unregistered id candidates. "
         f"Tables show the top {top} by frequency/score (raise --top for more).\n"]

    L.append("\n## Already named in a package (import the constant, drop the magic number)\n")
    if not rep["already_named"]:
        L.append("_none_\n")
    else:
        L.append("| value | freq | importable constant(s) | ambiguous | used under keys |")
        L.append("|------:|-----:|------------------------|:---------:|-----------------|")
        for e in rep["already_named"][:top]:
            imp = ", ".join(f"`{x}`" for x in e["importable"]) or "_(defined, not exported)_"
            L.append(f"| {e['value']} | {e['frequency']} | {imp} | "
                     f"{'YES' if e['ambiguous'] else ''} | "
                     f"{', '.join('`'+k+'`' for k in e['used_under_keys'])} |")
        if len(rep["already_named"]) > top:
            L.append(f"\n_...{len(rep['already_named']) - top} more (raise --top to see them)._")

    L.append("\n## Unregistered id candidates (flagged for review, not named)\n")
    L.append("> Naming guidance: do NOT name these from intuition or from any string seen\n"
             "> next to the id in the spec. Resolve the canonical name from the\n"
             "> authoritative source (StrSheet / datasheet MCP) before adding a constant.\n")
    if rep["occupied_checked"]:
        s = rep["summary"]
        L.append(f"> Occupied check (fact, not a directive): {s['unregistered_real_items']} of "
                 f"these ids exist as items in ItemTemplate, {s['unregistered_non_items']} do "
                 f"not (definitely structural or dangling). `item?` is context-blind: an id "
                 f"used only under `huntingZoneId`/bag `id` is not an item reference even if "
                 f"its number also exists as an item, so read it with the keys column.\n")
    if not rep["unregistered"]:
        L.append("_none_\n")
    else:
        chk = rep["occupied_checked"]
        head = "| value | freq | used under keys | in specs |" + (" item? |" if chk else "")
        sep = "|------:|-----:|-----------------|----------|" + (":-----:|" if chk else "")
        L.append(head); L.append(sep)
        for e in rep["unregistered"][:top]:
            specs = ", ".join(e["used_in_specs"][:4]) + ("…" if len(e["used_in_specs"]) > 4 else "")
            row = (f"| {e['value']} | {e['frequency']} | "
                   f"{', '.join('`'+k+'`' for k in e['used_under_keys'])} | {specs} |")
            if chk:
                mark = "yes" if e["in_item_universe"] else ("no" if e["in_item_universe"] is False else "")
                row += f" {mark} |"
            L.append(row)
        if len(rep["unregistered"]) > top:
            L.append(f"\n_...{len(rep['unregistered']) - top} more (raise --top to see them)._")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Corpus-scope id-registry detection.")
    ap.add_argument("--specs-root", default="specs/patches")
    ap.add_argument("--packages-root", default="packages")
    ap.add_argument("--min-id-value", type=int, default=1000,
                    help="Ignore ints below this (filters counts, zones, bag ids)")
    ap.add_argument("--min-new-freq", type=int, default=2,
                    help="Min occurrences to propose a NEW registry entry (default 2)")
    ap.add_argument("--min-already-freq", type=int, default=2,
                    help="Min occurrences to report an already-named literal (default 2; "
                         "set 1 to flag every single-use magic number)")
    ap.add_argument("--top", type=int, default=40,
                    help="Max rows per table (default 40; 0 = no cap, print all)")
    ap.add_argument("--occupied", help="Path to occupied_ids.json; annotates unregistered "
                    "candidates with whether the id is a real item vs a structural/dangling id")
    args = ap.parse_args()

    ranges = load_occupied(args.occupied) if args.occupied else None
    rep = build_report(args.specs_root, args.packages_root, args.min_id_value,
                       args.min_new_freq, args.min_already_freq, ranges)
    # Console-only by design: prints to stdout, the agent decides what to do. No files.
    print(render_md(rep, args.top))


if __name__ == "__main__":
    main()
