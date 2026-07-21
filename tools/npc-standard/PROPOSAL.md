# Statistical derivation of NPC-schema standards — research proposal

**Goal:** replace the n=1 (`Sandom`) archetype values in `npc-standard` with
defaults derived from the *entire* server-datasheet population, with explicit
outlier handling and a validation procedure that proves the derived standard
reproduces real data.

---

## 1. What the recon established (grounding facts)

Population (full, deduped, streamed via `iterparse`):

| Family | Files | Size | Primary entry | Count | Notes |
|---|---|---|---|---|---|
| NpcData | 424 | 47 MB | `Template` | **22,358** | ~50 root attrs + 11 near-universal nested blocks |
| AIData | 424 | 124 MB | `Ai` | **11,750** | id/name + `PeaceState`/`CautionState`/`CombatState` (all 100%) |
| NpcSkillData | 417 | **954 MB** | `Skill` | **179,580** | ~13 near-universal blocks; heaviest by far |
| TerritoryData | 425 | 133 MB | `TerritoryGroup` | 3,652 | spawn `Npc` records live at depth 3 (not yet profiled) |

Full structural sweep cost: ~10 s for the three small families, ~31 s for the
954 MB skill family. **Full-population analysis is feasible; no sampling needed.**

Three empirical facts that dictate the method:

1. **Presence% encodes optionality.** Nested blocks are near-universal
   (`Anger/Critical/Reaction/Stat/Abnormality/Aggro/CriticalAdjust` = 100%,
   `AbnormalityResistanceOverride` = 98.5%, `NamePlate` = only 59.8%), but root
   attributes range from 100% down to <10% presence. An attribute omitted by the
   game in 60% of entries is itself signal — it takes an engine default.
   *(My n=1 archetype both missed high-presence attrs like `elite`/`partyMember`/
   `balanceType` and wrongly excluded the 98.5%-present `AbnormalityResistanceOverride`.)*

2. **Global modes mix archetypes — clustering is mandatory.** Measured on NpcData:

   | attr | ALL modal (share) | villager=true cluster (share) |
   |---|---|---|
   | size | medium (77%) | medium (**94%**) |
   | invincible | true (66%) | true (**88%**) |
   | questVillager | false (71%) | false (**54%** ← looser) |

   Clustering tightens true defaults (size, invincible) and reveals sub-archetypes
   (`questVillager` loosening proves villagers split into merchant vs quest NPCs).
   A single global default would be wrong for ~30–45% of any given cluster.

3. **Cardinality separates defaults from identity.** Low-cardinality + high modal
   share (`size`: 4 values, `class`: 1 value @ 100%) = default candidate.
   High-cardinality (`id`, `shapeId`, `name`, `aiid`, `race`, `parentId`) =
   identity the spec must always supply. This is directly measurable per attribute.

---

## 2. Proposed methodology

### Phase A — Full-population extraction (generalize `recon.py`)
Stream every file in all four families, memory-bounded (`iterparse` + `clear()`,
capped value Counters). Emit a normalized aggregate keyed by
`(family, archetype?, element_path, attribute)` →
`{present, N, value_counts (capped), distinct, is_numeric}`.
Fix two recon gaps: profile TerritoryData **depth-3 `Npc` spawns**, and complete
the NpcSkillData value distributions (the count-only pass crashed in formatting).

### Phase B — Archetype segmentation
- **Primary: semantic clustering by declared flags** (interpretable, defensible).
  Candidate NPC cluster dimensions: `villager`, `questVillager`, `elite`,
  `isObjectNpc`, `huntingStyle`, `aggressive`, `unionElite`. Proposed initial
  taxonomy: `MerchantVillager`, `QuestVillager`, `NormalMonster`, `EliteMonster`,
  `BossMonster`, `ObjectNpc`. AI clusters keyed on `CombatState/@enable` +
  villager linkage; Skill clusters keyed on the owning NPC's cluster.
- **Cross-check: unsupervised clustering** (k-modes on the categorical attribute
  vectors, k-means/median on the numeric ones) used *only to validate* that the
  data's natural structure agrees with the semantic clusters — not as the primary
  definition. Disagreement flags a missing archetype dimension.

### Phase C — Per-cluster default derivation
For each `(cluster, attribute)`:
- **Categorical/enum attrs (the majority):** robust statistic = **mode + modal
  share + normalized entropy**. Accept as a default iff `modal_share ≥ τ` and
  `presence ≥ π`. (Precedent: the engine's existing EQUIP_* defaults use a
  ≥95% consistency bar — adopt τ≈0.90–0.95 as the starting point, tunable.)
- **Continuous numeric attrs (`scale`, `maxHp`, speeds, gauge sizes, coords):**
  use **median + MAD**, fence outliers with **1.5·IQR**; default = median of the
  fenced distribution. (Mean/σ are inappropriate — these are skewed/discrete.)
- Attributes failing the bar stay **required** (no default) and are documented as
  per-NPC. Multi-modal attributes (high entropy after clustering) flag a needed
  **sub-cluster**, not a default.

### Phase D — Outlier & conditional-default analysis
- **Outliers:** values below a frequency floor within a cluster are excluded from
  the standard and listed in an outlier register (auditable, not silently dropped).
- **Conditional defaults:** detect attributes whose value is a function of another
  (e.g. `gender`/`race`↔`shapeId`, `deathShapeId`↔`shapeId`, class-restricted
  fields) via pairwise conditional-entropy. These become *conditional* defaults
  (like the engine's `combatItemSubType`-derived item defaults), not static ones.

### Phase E — Codify into `npc-standard`
Translate accepted defaults into the layered `$extends` archetype chain, each
default annotated with provenance (`cluster`, `share%`, `N`) in a generated
companion table so reviewers can see *why* every value is what it is.

---

## 3. Validating the approach (proving the standard is right)

1. **Hold-out reconstruction (primary metric).** For every real NPC: take its
   cluster + identity fields, apply the derived archetype defaults, and diff the
   reconstruction against its actual XML. Report **per-attribute prediction
   accuracy** and **whole-entry exact-match rate** across the full population
   (leave-one-out / k-fold so an NPC never validates against a default it shaped).
2. **DSL round-trip at scale.** Author specs that recreate a stratified sample of
   real NPCs via the archetypes, `apply`, and structural-diff vs original — the
   original experiment's Phase-5 byte-equivalence test, now population-backed.
3. **Threshold sensitivity curve.** Sweep τ; plot (#attributes defaulted) vs
   (reconstruction error). Pick τ on the precision/coverage knee, don't assume it.
4. **Outlier audit.** Manually inspect a sample of flagged outliers to confirm
   they are genuinely special (not mis-clustered entries leaking in).

A standard is accepted when, per cluster, hold-out reconstruction reaches an
agreed accuracy bar (e.g. ≥95% per-attribute) with the outlier register reviewed.

---

## 4. Open decisions (need a call before Phase B)

- **Cluster granularity:** start with the 6-cluster NPC taxonomy above, or go
  finer (split MerchantVillager by service type, monsters by rank/level band)?
- **Default-acceptance threshold τ:** anchor at the engine's ≥95% precedent, or
  start looser (≈90%) and tighten via the sensitivity curve?
- **NpcSkillData scope:** include the 954 MB skill family in this pass (skills are
  tightly coupled to combat archetypes and 8× the data), or derive NPC+AI+Territory
  standards first and treat skills as a follow-up?
