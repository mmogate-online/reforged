---
name: prime-spec-standardization
description: >
  Session bootstrap for a DSL spec standardization pass. Loads the
  spec-standardization method, pre-reads the analyzer, item-ids, packages, and
  DSL definitions docs, and restates the session protocol: analyzers first,
  refactor the generator not the generated spec, gate with dsl expand
  deep-compare, keep item vs npc id spaces separate. Use when starting a pass to
  factor repeated blocks into $extends/$with or replace hardcoded ids with named
  package constants, when the user invokes /prime-spec-standardization, or before
  an analyzer sweep over a generated spec family.
argument-hint: "[optional target spec or family]"
disable-model-invocation: true
user-invocable: true
---

# Prime: Spec Standardization Session

Run this at the start of a standardization pass so the session opens with the
method, the reference set, and the correctness contract already in context. This
skill only primes and choreographs; the method itself lives in
[spec-standardization](../spec-standardization/SKILL.md).

## 1. Load the method
Invoke the `spec-standardization` skill and follow its method (analyzers,
go/no-go, rule of two, package curation).

## 2. Pre-read the reference set
Read all four before touching any spec:
- `tools/spec-standardize/README.md` (analyze.py + analyze_ids.py, the two axes)
- `tools/item-ids/README.md` (gen_item_ids.py, the occupied-id set)
- `packages/README.md` (package library, archetype vs data, rule of two)
- the DSL definitions guide: resolve `dsl_docs_enduser` from `.references`, then
  read `guides/definitions.mdx` ($extends / $with / $params / $remove semantics)

## 3. Hold the session protocol (non-negotiable)
- Run the analyzers FIRST. They are read-only advisors that print to stdout only:
  never persist their output as artifact files. For a full id audit run
  analyze_ids.py in exhaustive mode (--min-id-value 0 --min-new-freq 1
  --min-already-freq 1 --top 0) against a single-spec directory.
- Refactor the GENERATOR's render path, never hand-edit a generated spec. If the
  generator drifted (wrong output dir, create vs upsert), make it faithful first,
  then refactor.
- Gate every refactor with `dsl expand` deep-compare, verdict SEMANTICALLY
  IDENTICAL, plus unchanged op counts and a byte-deterministic re-run.
- Item template ids and npc template ids are separate id spaces that overlap
  numerically. Never resolve an item templateId to an npc-ids constant, and never
  swap a linkCustomizingId (or any non-item id) to an item constant.

## 4. Handshake before editing
Summarize your understanding of the above. Then:
- If a target spec or family was passed as an argument, run the analyzers on it
  and present a proposal (findings, structural + id axes, quantified reduction,
  the gates you will run). Do not edit until the user approves.
- If no target was passed, ask which spec to start with. Change nothing until the
  user names the target.
