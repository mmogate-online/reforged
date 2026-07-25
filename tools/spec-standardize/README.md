# spec-standardize

Two generic, spec-agnostic analyzers that operationalize the `spec-standardization`
skill method as reusable tools. Both **read** DSL spec YAML and **print** their report
to stdout; neither rewrites specs and neither writes artifact files (the agent decides
what to do with the output). They target two orthogonal axes of duplication:

| Script | Axis | Finds | DSL mechanism |
|--------|------|-------|---------------|
| `analyze.py` | **structural** | repeated block *shapes* | `$extends` / `$with` definitions |
| `analyze_ids.py` | **value / identity** | reused *ids* that should be named | ID-registry variables |

`_walk.py` holds the shared YAML-walk primitives both import.

## Why read-only advisors

Doctrine: you refactor the owning **generator's render path** (or the hand-authored
spec), never the generated output, and correctness is proven separately by
`dsl expand` deep-compare. Keeping these tools read-only makes them safe to run on any
generator's output.

## `analyze.py` (structural block factoring)

```bash
python tools/spec-standardize/analyze.py <spec.yaml> \
    [--min-group 4] [--tau 0.9] [--min-reduction 50]
```

Prints a per-collection, per-skeleton breakdown with, for each proposed definition,
its identity constants, its `$with` params, collapsible equal-leaf pairs, a projected
leaf-line reduction, and a GO / NO-GO verdict.

## `analyze_ids.py` (corpus-scope id-registry detection)

```bash
python tools/spec-standardize/analyze_ids.py \
    [--specs-root specs/patches] [--packages-root packages] \
    [--min-id-value 1000] [--min-new-freq 2] [--min-already-freq 2] [--top 40] \
    [--occupied tools/item-ids/occupied_ids.json]
```

With `--occupied`, each unregistered candidate gets an `item?` column: whether the id
exists as a real item in the ItemTemplate universe. It is context-blind (an id used only
under `huntingZoneId`/bag `id` is not an item reference even if the number also exists as
an item), so read it alongside the keys column. An id used under `templateId` that is
NOT in the universe is a dangling reference or a to-be-minted id.

Scans every spec for hardcoded integer literals, infers which are ids (see below), and
splits findings into two classes:

- **Already named**: the literal is exported by a registry package. The spec could
  import that existing constant instead of hardcoding the magic number. Values that
  resolve to more than one constant (ids collide across zones) are flagged `ambiguous`
  for a human to disambiguate.
- **Unregistered**: a recurring id that no package names yet. The tool only **flags** it
  (value, frequency, where it is used). It does **not** invent a constant name and does
  **not** print the co-located label, so no observed string can be read as a suggested
  name. Naming an unregistered id is a case-by-case decision resolved from the
  authoritative source (StrSheet / datasheet MCP), which this tool stays decoupled from.

### How "id-ness" stays spec-agnostic

It never keys off a hardcoded field name like `templateId`. A value is treated as an id
from **structural** signals: a large-integer value profile, occurrence under a key whose
*name shape* is id-like (`.*id$`, derived per-key, not a fixed list), a functionally
dependent **string label** (a sibling whose value is constant across every occurrence of
the id, discovered by co-occurrence not by being named `name`), and multi-context
cross-reference. The same integer used as a stat (`minAtk: 1001`) is excluded because
that occurrence's key is not id-shaped. Scope limit: the label must be a same-mapping
sibling; labels stored elsewhere are not resolved.

## Method (mirrors the skill, steps 1-5)

1. Walk the tree; find every list-of-mappings collection at any depth, aggregating
   nested collections across parents (all `itemBags` across all mobs land together).
2. Cluster blocks by **structural skeleton** (keys + nested shape + list lengths;
   scalar leaf values abstracted). Differing list lengths split skeletons, so a
   1-item bag never clusters with a 4-item bag.
3. Per group: per-leaf distinct count, modal share (tau), and a canonical partition.
4. Split each group into sub-archetypes along the dominant correlated **identity**
   discriminator (a partition carrying at least one string-valued leaf; purely
   numeric partitions such as `min`/`max` are quantity params, not archetype axes).
   Within each sub-archetype: constant leaves become the definition body, varying
   leaves become `$with` params, and equal-leaf pairs (e.g. `min == max`) are flagged
   as collapsible to a single param.
5. Project the leaf-line reduction and emit the verdict.

## The one DSL semantic it enforces

Maps deep-merge; **lists replace entirely**. A block with a list child is only cleanly
factorable when that list has **constant length** across the group (its elements can
then ship in the definition body with scalar `$with` leaves). Variable-length list
children are reported `NO (variable-length list child)` with a suggested
sub-archetype-by-length split. This is why an "agnostic" tool cannot be schema-blind.

## Pilot

First run: `specs/patches/002/17-iod-loot.yaml` (5640 lines). The tool identified the
6 core reforged bags as `PROB`/`QTY` templates; factoring them into the
`reforged-loot-bags` package cut the spec to 2928 lines (48%), `dsl expand`
deep-compare verified SEMANTICALLY IDENTICAL.
