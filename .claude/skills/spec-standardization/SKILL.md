---
name: spec-standardization
description: >
  Method and tools for standardizing DSL specs: factoring repeated blocks into
  $extends/$with definitions (analyze.py), and replacing hardcoded item/npc ids
  with named package constants (analyze_ids.py plus the item-ids registry and
  gen_item_ids.py). Covers go/no-go, package placement (rule of two), id
  conflict-avoidance via the occupied-id set, and the correctness gates for
  refactors, plus curation of the packages standard library. Use when a generated
  spec has repeated blocks or hardcoded ids/magic numbers, when deciding whether a
  pattern or id belongs in a package, after a spec-authoring wave, or during /learn
  curate sweeps.
disable-model-invocation: false
user-invocable: true
---

# Spec Standardization Method

Proven 2026-07-18 on patch 001: spec 02 went 12543 to 4992 lines with proven
semantic equivalence. The analyzers print to stdout only; do not persist their output
as artifact files (it accumulates junk). Capture what you act on in the commit/PR.

## When to run

- Any generated spec with more than ~300 lines of structurally repeated blocks.
- After each patch's spec-authoring wave, before the apply campaign (polish step).
- During `/learn curate`: sweep the package library per the curation rules below.

## Running the analyzers

**Run the analyzer first.** `tools/spec-standardize/analyze.py <spec.yaml>` executes
the structural-factoring steps below generically and prints its report to stdout (no
artifact files). Read
its verdict before hand-deriving anything; only fall back to manual analysis when the
spec shape defeats the tool (report the gap). For id reuse, `analyze_ids.py` flags
registry candidates (already-named vs unregistered); it never proposes a constant name.
Both tools are read-only: they advise, they never rewrite a spec.

**Id-registry audit: flag EVERY hardcoded id (mandatory invocation).** The default
`analyze_ids.py` thresholds favor signal over recall (they suppress small ids and
single-use magic numbers). When the task is to account for every hardcoded id in a
spec (an audit, or before a registry sweep), run it in exhaustive mode:

```
python tools/spec-standardize/analyze_ids.py --specs-root <dir-with-only-the-spec> \
    --packages-root packages --min-id-value 0 --min-new-freq 1 --min-already-freq 1 --top 0
```

This flags 100% of ids that sit under an id-shaped key (validated: 116/116 on
`17-iod-loot.yaml`, zero gaps). It does NOT drag in quantities that merely sit next to
a shared category label (gold min/max): the label-only fallback only fires on labels
near-unique to one value, so `--min-id-value 0` stays clean. Scope the run to one spec
by copying it into an otherwise-empty directory and pointing `--specs-root` at that dir
(the tool scans a directory tree, not a single file). Use `--top 0` to print the full
table with no row cap.

## Id registry: naming and conflict-avoidance

`analyze_ids.py` splits ids into already-named (import the existing constant, drop the
magic number) and unregistered. To ACT on the results:

- **Name unregistered ITEM ids** with the demand-driven generator (names only what a spec
  references, sourced from `ItemTemplate*.xml` + `StrSheet_Item*.xml`, sharded by class):
  `python tools/item-ids/gen_item_ids.py names --datasheet <server_datasheet> --from-spec <spec>`.
  Then migrate the spec's GENERATOR to emit `$CONSTANT` (it auto-adds the imports); gate
  the migration with `dsl expand` deep-compare (SEMANTICALLY IDENTICAL).
- **Conflict-avoidance** is a membership test against the exact occupied-id set, never a
  range prediction. Regenerate it with `gen_item_ids.py occupied`; query free/taken with
  `gen_item_ids.py check --ids ...`, or pass `--occupied tools/item-ids/occupied_ids.json`
  to `analyze_ids.py` to mark unregistered ids as real items vs structural/dangling.
- **Separate id spaces:** npc template ids and item template ids overlap numerically but
  are different entities (1001 = npc Vekas AND item Coarse Fiber). Never resolve an item
  `templateId` to an `npc-ids` constant; `item-ids` excludes `npc-ids` when reconciling.

## The method (structural factoring)

1. Parse the spec YAML; group repeated blocks by family (spawn entries, sections,
   reward rows, list items).
2. Per attribute: distinct-value count, modal value, modal share.
3. Cluster blocks by full attribute fingerprint: the distinct-fingerprint count
   tells you how many archetypes the data actually wants; correlated flips form
   sub-archetypes (verify claimed correlations row by row; do not eyeball).
4. Candidate split: tau >= 0.9 constants into the archetype; clustered deviations
   into `$extends`-based sub-archetypes; the rest stays per-row. A discriminator axis
   must carry a string-valued (identity) leaf; a purely numeric flip (min/max) is a
   `$with` param, not a sub-archetype.
5. Project the reduction (count factorable leaf lines, not file lines).

DSL guard the analyzer enforces (and you must too): maps deep-merge, **lists replace
entirely**. A list-valued child is factorable only at constant length across the group.

## Go / no-go

NO when: the bulk is list-valued (lists replace on merge); instance orderings are
inconsistent (a shared block would change output, not shrink it); fewer than ~50
factorable lines; the spec is hand-authored and small.
GO when: scalar-heavy repeated mappings, few fingerprints, a generator owns the
render path.

## Placement (rule of two)

- Patch-local `definitions:` block first when the pattern has one consumer.
- Promote to a package when a second consumer appears, OR immediately when the
  pattern is provably zone/patch-agnostic (restoration archetypes were).
- Never extend a partially-matching existing archetype (injection trap: see the
  dsl-definitions skill).

## Implementation rules

- Refactor the GENERATOR (render path), never hand-edit generated specs.
- Register new packages in `datasheetlang.yml` and index them in
  `packages/README.md` under the correct class (archetype vs data).
- Correctness gates, all mandatory: unchanged per-spec op counts; unchanged full
  patch batch totals; `dsl expand` deep-compare of pre-refactor vs refactored
  specs verdicts SEMANTICALLY IDENTICAL; byte-deterministic generator re-runs.

## Standard library curation

`packages/README.md` classifies packages:
- **Archetype packages** (statistically derived, regenerable, do not hand-edit):
  regenerate from their recorded tool when the source population changes; retire
  fields whose modal share drops below tau.
- **Data packages** (curated ids/values): hand-maintained, reviewed like content.
Curation sweep checklist: stale archetypes after baseline changes; patch-local
definitions with a second consumer (promote); exported definitions with zero
consumers (candidate retire, check history first).

## Generator conventions

Every `gen_*_specs.py`: byte-deterministic (sorted iteration, no timestamps);
emits `$extends` when a registered archetype matches fully; prints deviation
stats and id allocations; hard-fails on id collisions rather than reallocating
silently.
