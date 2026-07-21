---
name: spec-standardization
description: >
  Method for finding, validating, and implementing spec standardization through
  DSL definitions: statistical fingerprinting of repeated blocks, go/no-go
  criteria, package placement (rule of two), and the correctness gates for
  refactors. Also defines curation of the packages standard library. Use when a
  generated spec exceeds a few hundred lines of repeated blocks, after a patch's
  spec-authoring wave completes, when deciding whether a pattern belongs in a
  package, or during /learn curate sweeps of the package library.
disable-model-invocation: false
user-invocable: true
---

# Spec Standardization Method

Proven 2026-07-18 on patch 001: spec 02 went 12543 to 4992 lines with proven
semantic equivalence. Analysis artifact pattern:
`docs/plans/<plan>/data/spec-standardization-analysis.md`.

## When to run

- Any generated spec with more than ~300 lines of structurally repeated blocks.
- After each patch's spec-authoring wave, before the apply campaign (polish step).
- During `/learn curate`: sweep the package library per the curation rules below.

## The method (python, statistical)

1. Parse the spec YAML; group repeated blocks by family (spawn entries, sections,
   reward rows, list items).
2. Per attribute: distinct-value count, modal value, modal share.
3. Cluster blocks by full attribute fingerprint: the distinct-fingerprint count
   tells you how many archetypes the data actually wants; correlated flips form
   sub-archetypes (verify claimed correlations row by row; do not eyeball).
4. Candidate split: tau >= 0.9 constants into the archetype; clustered deviations
   into `$extends`-based sub-archetypes; the rest stays per-row.
5. Project the reduction (count factorable leaf lines, not file lines).

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
