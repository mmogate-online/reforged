# ai-standard

AI authoring **standard library** — data-derived `<Cluster>AI` archetypes for the
`ai` section. Split out from `npc-standard` so each schema has its own library.

## Data-derived & complete-to-ceiling

`index.yml` is **auto-generated** by `tools/npc-standard/codegen.py` from a full
-population analysis of AIData (11,750 AIs), segmented into 6 archetypes, accepting
a value as a default only at modal share **≥ τ (0.90)**. Every value is annotated
`share`/`n`. **Do not hand-edit** — re-run the pipeline.

The AI library is intentionally **thin**, and that is a proven data finding, not a
gap:

- **Templatable** (what these archetypes supply): the peace/caution idle "shell" —
  `peaceState`/`cautionState` scalars + `combatState.enable`.
- **Bespoke** (cannot be templated): the combat tree. Structural-skeleton
  classification proved combat AI is irreducibly unique — ≥30-member behavior
  classes cover only **3%** of combat AIs (see `tools/npc-standard/README.md` §3a).

So for **non-combat NPCs** (villagers, merchants, objects) an archetype + engine
defaults yields a complete working AI; for **combat NPCs** the archetype supplies
the shell and the combat tree is authored per-NPC (because it's unique).

## Exported definitions

`MerchantVillagerAI`, `QuestVillagerAI`, `NormalMonsterAI`, `EliteMonsterAI`,
`BossMonsterAI`, `ObjectNpcAI`. Cluster selectors match `npc-standard`.

## Usage

```yaml
imports:
  - from: npc-standard
  - from: ai-standard

ai:
  upsert:
    - $extends: MerchantVillagerAI
      huntingZoneId: 213
      id: 9001
      name: "my_merchant_ai"
```

Archetypes are **scalar-only** (no nested lists) — apply-idempotent, and they
sidestep the filed `ai-upsert` nested-list append bug.

## Enrichments

- **ObjectNpc `RandomMove` socials — investigated, not shipped.** The `ai-upsert`
  append bug is fixed (DSL `5f39a37f`), so nested AI lists are now authorable, but the
  data doesn't justify shipping it: ObjectNpc's modal `RandomMove` subtree is
  `(moveMaxDistance=300 moveMinDistance=100 moveRadius=1000 probMove=0 probSocial=0)`
  with **zero `<Social>` children**, and its 74% modal share is **below τ=0.90**.
  No cluster has a templatable social-motion sequence. Correct to leave it per-NPC.
- Natural types once `2026-05-20-ai-schema-type-mismatches` lands (still open).
