#!/usr/bin/env python3
"""
Shared YAML-walk primitives for the spec-standardize tools.

Both analyzers (structural block factoring and id-registry detection) read DSL spec
YAML the same way: skip preprocessor directives, descend maps and lists, enumerate
scalar leaves. Those primitives live here so neither script copy-pastes them.
"""

# DSL preprocessor directives that must never be treated as content leaves.
DIRECTIVES = {"$extends", "$with", "$params", "$remove"}


def is_mapping(x):
    return isinstance(x, dict)


def collection_paths(node, path, out):
    """Populate out[path] with the mapping-elements of every list-of-mappings.

    Nested collections aggregate across parents: every `itemBags` list across every
    mob lands under the single path `...itemBags`. Recurses through maps and lists.
    """
    if is_mapping(node):
        for k, v in node.items():
            if k in DIRECTIVES:
                continue
            child = f"{path}.{k}" if path else str(k)
            if isinstance(v, list) and v and all(is_mapping(e) for e in v):
                out.setdefault(child, []).extend(v)
            for e in (v if isinstance(v, list) else [v]):
                collection_paths(e, child, out)
    elif isinstance(node, list):
        for e in node:
            collection_paths(e, path, out)


def skeleton(node):
    """Structural signature: keys + nested shape + list lengths; scalar values erased."""
    if is_mapping(node):
        return ("map", tuple(sorted(
            (k, skeleton(v)) for k, v in node.items() if k not in DIRECTIVES
        )))
    if isinstance(node, list):
        return ("list", len(node), tuple(skeleton(e) for e in node))
    return "scalar"


def has_directive(node):
    if is_mapping(node):
        if any(k in DIRECTIVES for k in node):
            return True
        return any(has_directive(v) for v in node.values())
    if isinstance(node, list):
        return any(has_directive(e) for e in node)
    return False


def leaves(node, prefix, out):
    """out[dotted_path] = scalar value, for every scalar leaf (lists use [i])."""
    if is_mapping(node):
        for k, v in node.items():
            if k in DIRECTIVES:
                continue
            leaves(v, f"{prefix}.{k}" if prefix else str(k), out)
    elif isinstance(node, list):
        for i, e in enumerate(node):
            leaves(e, f"{prefix}[{i}]", out)
    else:
        out[prefix] = node


def list_children(block):
    """Return [(path, length)] for every list-valued child (any depth) of a block."""
    found = []

    def rec(node, prefix):
        if is_mapping(node):
            for k, v in node.items():
                if k in DIRECTIVES:
                    continue
                p = f"{prefix}.{k}" if prefix else str(k)
                if isinstance(v, list):
                    found.append((p, len(v)))
                rec(v, p)
        elif isinstance(node, list):
            for i, e in enumerate(node):
                rec(e, f"{prefix}[{i}]")

    rec(block, "")
    return found


def iter_scalar_occurrences(node, path, parent, key=None):
    """Yield (key, value, dotted_path, parent_mapping) for every scalar leaf.

    `key` is the mapping key the scalar sits under; a scalar inside a list is attributed
    to the LIST's key, not its numeric index (so `materials: [1001, 1002]` reports key
    `materials`, not `0`/`1`). `parent` is the nearest enclosing mapping, whose sibling
    leaves id-registry detection tests for a functionally-dependent label. Directives
    are skipped.
    """
    if is_mapping(node):
        for k, v in node.items():
            if k in DIRECTIVES:
                continue
            child = f"{path}.{k}" if path else str(k)
            if isinstance(v, (dict, list)):
                yield from iter_scalar_occurrences(v, child, node, k)
            else:
                yield (k, v, child, node)
    elif isinstance(node, list):
        for i, e in enumerate(node):
            child = f"{path}[{i}]"
            if isinstance(e, (dict, list)):
                yield from iter_scalar_occurrences(e, child, parent, key)
            else:
                yield (key, e, child, parent)
