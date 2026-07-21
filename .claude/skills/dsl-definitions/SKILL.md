---
name: dsl-definitions
description: >
  Correct usage of the DSL definitions feature ($extends, $with, $params, $remove)
  and the project's archetype package conventions. Covers deep-merge semantics,
  the list-replace trap, package registration and cross-package resolution, and
  archetype design rules with the verification loop for refactors. Use when
  authoring or editing a spec or package that uses definitions or $extends, when
  creating or extending an archetype package (npc-standard, spawn-restore-standard,
  area-section-standard, equipment-item-standard), or when a refactor must prove
  semantic equivalence.
disable-model-invocation: false
user-invocable: true
---

# DSL Definitions Usage

Full semantics: DSL end-user docs `guides/definitions.mdx` (resolve `dsl_docs_enduser`
in `.references`). This skill records what the docs do not: the traps and the
project conventions.

## Semantics that bite

- Deep merge is child-wins on scalars, recursive on mappings, and **lists replace
  entirely**: there is no element-level merge. Never put a list in an archetype
  unless every consumer wants exactly that list.
- `$with` bindings are scalars or scalar lists only (E543), and substitution is
  whole-value only: `"prefix_$NAME"` stays literal.
- `$params` declares required bindings; missing ones fail at expansion (E544).
- `$remove` runs after merge, strips top-level keys only, and is processed before
  `$with` substitution (removed placeholders never trigger errors).
- YAML anchors/aliases/merge keys are forbidden (E506): use `$extends`.
- Max inheritance depth 10; circular extends is E502.
- Cross-package: export via `exports.definitions`, consume with qualified names
  (`pkg.Definition`). The package MUST be registered in `datasheetlang.yml` under
  `workspace.packages` or imports fail with Unknown package reference.
- Package-internal variables resolve at the exporting module's scope; consumers
  do not (and cannot) re-import them. `$with` at the call site shadows them.

## Archetype design rules (project convention)

- Constants enter an archetype at modal share tau >= 0.9 over the analyzed
  population; annotate every field `# share=NN% n=SAMPLE` (npc-standard style).
- Identity, geometry, positions, and descs are always per-row, never archetype.
- Below-tau fields stay per-row even when "mostly" constant.
- Generated archetype packages are DO NOT HAND-EDIT: regenerate from their tool
  (recorded in each package README) when the underlying population changes.
- Emitting generators carry a `$remove` guard for base keys absent from a row.

## The archetype-injection trap

Never `$extends` an existing archetype unless EVERY key it carries is wanted in
EVERY consumer row. A partially-matching archetype silently injects its extra
defaults into all rows: output diverges with no error.

## Verification loop for any definitions refactor

1. `dsl validate` per spec: operation counts must be unchanged.
2. Full patch batch dry-run: totals must be unchanged (applied/ops/warnings).
3. `dsl expand` the pre-refactor spec and the refactored spec; deep-compare the
   results (normalize mapping key order; strict on values and list order). Only
   a SEMANTICALLY IDENTICAL verdict proves equivalence.
4. Generators must stay byte-deterministic across re-runs.

## Lessons

### $params fires at every $extends site, not just entry call sites
- **Date/source:** 2026-07-20: charm skill spec (patch 001, 16-charm-skills)
- **Why:** a parameterized base definition (`_charmArea` with `$params: [ABN]`)
  extended by intermediate definitions (`_charmAllyArea`) raised E544 at
  `(root).definitions.<name>`: the intermediate `$extends` site provides no
  binding, and `$params` is validated at each site rather than deferred to the
  entry call site.
- **Apply:** declare `$params` only on the OUTERMOST entry-level definitions
  whose call sites always bind; leave inner parameterized definitions bare
  (their `$NAME` placeholders resolve later through nested `$with` scope
  inheritance, the docs' Outer/Inner pattern). Works proven: charm spec 16
  factored 2781 to 321 lines with dsl-expand-identical output.

### Smoke-test the data variant that carries the optional sibling elements
- **Date/source:** 2026-07-19: quest 1303 unofferable in live test after prereq clear
- **Why:** the prereq-clear smoke test used quest 1302, which has no
  선행퀘스트논리식 sibling; on 1303 (which has one) the DSL clear orphaned the
  operator (a corpus-unique shape) and the quest became permanently unofferable
  with no error anywhere. Validate and even scratch-apply looked green.
- **Apply:** before trusting a command class, enumerate the optional sibling
  elements of the target structure across the corpus and scratch-apply against
  a specimen CARRYING each optional sibling, not just the minimal case. A
  corpus-uniqueness scan (does the post-apply shape exist anywhere in vanilla?)
  is a cheap anomaly detector for lossy edits.

### Do not extend npc-standard archetypes for restoration spawns
- **Date/source:** 2026-07-18: spec-standardization analysis of 02-iod-spawn-restore
- **Why:** 17 of 28 restoration constants matched NormalMonsterSpawn exactly, but
  the archetype carried defaults absent from the restoration data and would have
  injected them into all 217 rows silently.
- **Apply:** restoration specs extend `spawn-restore-standard` archetypes that own
  their full constant set; partial overlap with another archetype is not reuse.

### List-valued reward bags cannot be factored
- **Date/source:** 2026-07-18: rewards axis analysis (05-iod-quest-rewards)
- **Why:** items lists replace wholesale on merge, and class-row ordering differed
  across bags (5 distinct orderings), so a shared list would change output.
- **Apply:** leave list-bodied blocks literal; factor only the scalar envelope,
  and only when it saves meaningful lines.
