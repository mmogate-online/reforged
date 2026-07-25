#!/usr/bin/env python3
"""
Generic DSL spec standardization analyzer.

Operationalizes the `spec-standardization` skill method as a reusable, spec-agnostic
tool. It READS a DSL spec YAML and reports where repeated blocks can be factored into
`$extends`/`$with` definitions. It never rewrites specs: the refactor happens in the
owning generator's render path and is proven separately by `dsl expand` deep-compare.

What it does (the skill method, steps 1-5):
  1. Walks the YAML tree and finds every list-of-mappings collection at any depth,
     aggregating nested collections across their parents (all itemBags across all mobs).
  2. Clusters each collection's blocks by STRUCTURAL SKELETON (keys + nested shape +
     list lengths; scalar leaf VALUES abstracted). Differing list lengths split
     skeletons, so a 1-item bag never clusters with a 4-item bag.
  3. Per skeleton group: per-leaf distinct-value count, modal value, modal share (tau),
     and a canonical partition (grouping) signature.
  4. Splits each group into sub-archetypes along the dominant correlated low-cardinality
     discriminator (the leaves that flip together, e.g. id+bagName+templateId+name).
     Within each sub-archetype: constant leaves -> definition body; varying leaves ->
     `$with` params; equal-leaf pairs (min==max) flagged as collapsible.
  5. Projects the leaf-line reduction and emits a GO / NO-GO verdict.

DSL merge semantics baked in (this is why "agnostic" is not "schema-blind"):
  maps deep-merge, LISTS REPLACE ENTIRELY. A block with a list child is only cleanly
  factorable when that list has CONSTANT LENGTH across the group (its elements can then
  ship in the definition body with scalar `$with` leaves). Variable-length list children
  are flagged NOT-FACTORABLE with a suggested sub-archetype-by-length split.

Usage:
    python analyze.py <spec.yaml> [--min-group N] [--tau 0.9] [--min-reduction 50]

Prints the analysis to stdout; writes no files.
"""

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml

from _walk import (DIRECTIVES, is_mapping, collection_paths, skeleton,
                   has_directive, leaves, list_children)


# ── Per-leaf statistics over an aligned group of blocks ──────────────────────
def leaf_matrix(blocks):
    """leaf path -> [value per block]. All blocks share a skeleton, so paths align."""
    rows = []
    for b in blocks:
        d = {}
        leaves(b, "", d)
        rows.append(d)
    paths = list(rows[0].keys())
    return {p: [r.get(p) for r in rows] for p in paths}


def canonical_partition(values):
    """Map values to first-seen integer ids: the grouping ignoring the labels."""
    seen, ids = {}, []
    for v in values:
        key = repr(v)
        if key not in seen:
            seen[key] = len(seen)
        ids.append(seen[key])
    return tuple(ids)


def analyze_group(blocks, tau):
    """Classify leaves of a single-skeleton group into constant / discriminator / param."""
    mat = leaf_matrix(blocks)
    n = len(blocks)
    stats = {}
    for path, vals in mat.items():
        c = Counter(repr(v) for v in vals)
        modal_key, modal_ct = c.most_common(1)[0]
        stats[path] = {
            "distinct": len(c),
            "modal_share": modal_ct / n,
            "partition": canonical_partition(vals),
            "values": vals,
        }

    constant = {p: mat[p][0] for p, s in stats.items() if s["distinct"] == 1}
    varying = {p: s for p, s in stats.items() if s["distinct"] > 1}

    # Discriminators: low-cardinality partitions whose correlated leaves flip together.
    # Generic identity guard: a real archetype axis must carry at least one STRING-valued
    # leaf (a label/name/id-like discriminator). A purely numeric partition (min/max,
    # probability) is a quantity PARAMETER axis, not an archetype split, and folding it
    # into sub-archetypes would produce buckets with identical identity. String-vs-numeric
    # is a structural property, so this stays domain-agnostic.
    part_groups = defaultdict(list)
    for p, s in varying.items():
        part_groups[s["partition"]].append(p)

    def has_string_leaf(plist):
        return any(any(isinstance(v, str) for v in mat[p]) for p in plist)

    discriminators = None
    for part, plist in part_groups.items():
        card = len(set(part))
        if 2 <= card <= 12 and has_string_leaf(plist):
            # Prefer fewer resulting sub-archetypes (smaller cardinality); break ties
            # toward the broadest correlated flip (more leaves).
            if discriminators is None:
                discriminators = (part, plist, card)
            else:
                _, cur_leaves, cur_card = discriminators
                if (card, -len(plist)) < (cur_card, -len(cur_leaves)):
                    discriminators = (part, plist, card)

    # Equal-leaf pairs (e.g. min==max in every block): collapsible to one param.
    equal_pairs = []
    vpaths = list(varying)
    for i in range(len(vpaths)):
        for j in range(i + 1, len(vpaths)):
            if mat[vpaths[i]] == mat[vpaths[j]]:
                equal_pairs.append((vpaths[i], vpaths[j]))

    return {
        "n": n, "stats": stats, "constant": constant,
        "varying": list(varying), "discriminators": discriminators,
        "equal_pairs": equal_pairs,
    }


def structural_line_estimate(block):
    """Rough leaf-line count of a block's constant scaffold (keys + scalar leaves)."""
    d = {}
    leaves(block, "", d)
    return len(d)


def build_report(spec_path, min_group, tau, min_reduction):
    doc = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    collections = {}
    collection_paths(doc, "", collections)

    report = {"spec": str(spec_path), "params": {
        "min_group": min_group, "tau": tau, "min_reduction": min_reduction},
        "collections": []}
    total_reduction = 0

    for path, blocks in sorted(collections.items()):
        # Skip blocks that already carry directives (already factored).
        raw = [b for b in blocks if not has_directive(b)]
        if len(raw) < min_group:
            continue

        skels = defaultdict(list)
        for b in raw:
            skels[skeleton(b)].append(b)

        col = {"path": path, "block_count": len(raw), "skeletons": []}
        for sk, group in sorted(skels.items(), key=lambda kv: -len(kv[1])):
            if len(group) < min_group:
                continue
            a = analyze_group(group, tau)
            lc = list_children(group[0])
            # DSL guard: any list child must have constant length across the group.
            var_len = []
            for lp, _ in lc:
                lens = {len_of_list_at(b, lp) for b in group}
                if len(lens) > 1:
                    var_len.append((lp, sorted(lens)))

            const_leaf_lines = len(a["constant"])
            members = a["n"]

            # Sub-archetype split along the dominant discriminator.
            sub = []
            if a["discriminators"]:
                part, plist, card = a["discriminators"]
                buckets = defaultdict(list)
                for b, pid in zip(group, part):
                    buckets[pid].append(b)
                for pid, bl in sorted(buckets.items()):
                    sa = analyze_group(bl, tau)
                    sub.append({
                        "members": sa["n"],
                        "constant": {k: jsonable(v) for k, v in sa["constant"].items()},
                        "params": sorted(set(flatten_params(sa))),
                        "equal_pairs": sa["equal_pairs"],
                    })
                discriminator_paths = plist
            else:
                sa = a
                sub.append({
                    "members": members,
                    "constant": {k: jsonable(v) for k, v in a["constant"].items()},
                    "params": sorted(set(flatten_params(a))),
                    "equal_pairs": a["equal_pairs"],
                })
                discriminator_paths = []

            # Projection: constant scaffold emitted once per sub-archetype instead of
            # once per member. reduction ~= sum over sub of (members-1)*constant_lines.
            reduction = 0
            for s in sub:
                body = len(s["constant"]) + count_structural_keys(group[0])
                reduction += max(0, (s["members"] - 1) * body)

            factorable = not var_len and reduction >= 0
            verdict = "GO" if (factorable and reduction >= min_reduction) else "NO"
            if var_len:
                verdict = "NO (variable-length list child; lists replace on merge)"

            if verdict.startswith("GO"):
                total_reduction += reduction

            col["skeletons"].append({
                "size": len(group),
                "sample_keys": sorted(k for k in group[0] if k not in DIRECTIVES),
                "list_children": [{"path": lp, "length": ln} for lp, ln in lc],
                "variable_length_children": var_len,
                "constant_leaf_count": const_leaf_lines,
                "discriminator_paths": discriminator_paths,
                "sub_archetypes": sub,
                "projected_leaf_reduction": reduction,
                "verdict": verdict,
            })
        if col["skeletons"]:
            report["collections"].append(col)

    report["total_projected_reduction"] = total_reduction
    report["overall_verdict"] = "GO" if total_reduction >= min_reduction else "NO"
    return report


# ── small helpers ─────────────────────────────────────────────────────────────
def len_of_list_at(block, dotted):
    node = block
    for part in dotted.replace("]", "").split("."):
        if "[" in part:
            k, idx = part.split("[")
            node = node[k][int(idx)]
        else:
            node = node[part]
    return len(node) if isinstance(node, list) else 0


def count_structural_keys(block):
    """Count nesting scaffold lines that repeat per member (list keys, item dashes)."""
    n = 0

    def rec(node):
        nonlocal n
        if is_mapping(node):
            for k, v in node.items():
                if k in DIRECTIVES:
                    continue
                if isinstance(v, (list, dict)):
                    n += 1
                    rec(v)
        elif isinstance(node, list):
            for e in node:
                rec(e)

    rec(block)
    return n


def flatten_params(a):
    return list(a["varying"])


def jsonable(v):
    return v


# ── Markdown rendering ───────────────────────────────────────────────────────
def render_md(report):
    L = []
    L.append(f"# Spec standardization analysis: `{Path(report['spec']).name}`\n")
    L.append(f"Generated by `tools/spec-standardize/analyze.py` "
             f"(min-group={report['params']['min_group']}, tau={report['params']['tau']}, "
             f"min-reduction={report['params']['min_reduction']}).\n")
    L.append(f"**Overall verdict: {report['overall_verdict']}** "
             f"(projected leaf-line reduction ~{report['total_projected_reduction']}).\n")
    for col in report["collections"]:
        L.append(f"\n## Collection `{col['path']}` ({col['block_count']} blocks)\n")
        for i, sk in enumerate(col["skeletons"], 1):
            L.append(f"### Skeleton {i}: {sk['size']} blocks, verdict **{sk['verdict']}**")
            L.append(f"- keys: `{', '.join(sk['sample_keys'])}`")
            if sk["list_children"]:
                lc = ", ".join(f"{c['path']}(len {c['length']})" for c in sk["list_children"])
                L.append(f"- list children: {lc}")
            if sk["variable_length_children"]:
                L.append(f"- **variable-length list children (blocks factoring):** "
                         f"{sk['variable_length_children']}")
            L.append(f"- constant leaves: {sk['constant_leaf_count']}; "
                     f"projected reduction: ~{sk['projected_leaf_reduction']} lines")
            if sk["discriminator_paths"]:
                L.append(f"- sub-archetype discriminator leaves (flip together): "
                         f"`{', '.join(sk['discriminator_paths'])}`")
            L.append(f"- **{len(sk['sub_archetypes'])} proposed definition(s):**")
            for j, s in enumerate(sk["sub_archetypes"], 1):
                params = ", ".join(f"${p}" for p in s["params"]) or "(none)"
                L.append(f"  - def {j}: {s['members']} members; "
                         f"`$with` params: {params}")
                keyid = {k: v for k, v in s["constant"].items()
                         if k in ("id", "bagName") or k.endswith(".templateId") or k.endswith(".name")}
                if keyid:
                    L.append(f"    - identity constants: `{keyid}`")
                if s["equal_pairs"]:
                    L.append(f"    - collapsible equal leaves (share one param): "
                             f"{s['equal_pairs']}")
            L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Generic DSL spec standardization analyzer.")
    ap.add_argument("spec", help="Path to the DSL spec YAML to analyze")
    ap.add_argument("--min-group", type=int, default=4,
                    help="Minimum blocks in a skeleton group to consider (default 4)")
    ap.add_argument("--tau", type=float, default=0.9,
                    help="Modal-share threshold for 'constant enough' (default 0.9)")
    ap.add_argument("--min-reduction", type=int, default=50,
                    help="Minimum projected leaf-line reduction for a GO (default 50)")
    args = ap.parse_args()

    report = build_report(args.spec, args.min_group, args.tau, args.min_reduction)
    # Console-only by design: the report prints to stdout, the agent decides what to do
    # with it. The tool writes no artifact files.
    print(render_md(report))


if __name__ == "__main__":
    main()
