# NPC Standard Library — initiative tracker & resume brief

Read this end-to-end before resuming in a new session. It captures the **goal**,
the **methodology**, the **current state**, and the **resume steps** for the
data-derived NPC authoring standard library.

---

## 1. Goal

Make the DSL a productivity tool for content creators by giving it a **standard
library** (like a programming language's stdlib) that eliminates the boilerplate
of authoring large schemas (`NpcData`, `AIData`, `TerritoryData`, later
`NpcSkillData`). A creator should declare only **identity + intent** and inherit
the rest from a reusable archetype via `$extends`.

**Strategic decision (locked):** the library lives **in DSL as packages**, not as
engine-baked defaults. Keeps the engine a minimal general language; keeps defaults
inspectable, overridable, and version-controlled. (The engine's existing `EQUIP_*`
auto-defaults are the counter-example we deliberately are *not* following.)

The deliverable package is [`packages/npc-standard`](../../packages/npc-standard/).

---

## 2. Methodology

Defaults are **not guessed from a sample** — they are mined from the full live
datasheet population and validated statistically.

1. **Extraction** (`recon.py`, `analyze_all.py`): stream every file
   (`iterparse`, memory-bounded), flatten each entry to `attr` / `Block.attr`
   vectors. Population: NpcData 22,358 · AIData 11,750 · TerritoryData 95,806 spawns.
2. **Segmentation** — 6 semantic clusters by declared flags:
   `MerchantVillager`, `QuestVillager`, `NormalMonster`, `EliteMonster`,
   `BossMonster`, `ObjectNpc`. AIs clustered by the owning NPC's `aiid`; spawns by
   `npcTemplateId`; skills by the owning NPC's `templateId`. Population also includes
   NpcSkillData (174,272 clustered skills, streamed two-pass to bound memory).
3. **Default derivation** — per `(cluster, attribute)`: a value is accepted as a
   default iff **presence ≥ π (0.50)** and **modal share ≥ τ (0.90)**. Numeric
   strings canonicalised so `1.000000`/`1` collapse. Continuous fields that vary
   stay below τ and remain **required** (correct outcome).
4. **τ chosen on evidence** — sensitivity curve (NpcData, weighted):
   0.85→94.2%acc/193defs · **0.90→96.0%/144** · 0.95→98.4%/92. τ=0.90 is the knee
   that clears the 95% accuracy bar while keeping the most defaults.
5. **Validation** — 5-fold cross-validated hold-out reconstruction: every entry
   rebuilt from cluster + identity and diffed vs its real XML.
   Per-attribute accuracy: **NpcData 95–99%, AIData 93–98%, TerritoryData 98–99%**.
6. **Codegen** (`codegen.py`) emits `packages/npc-standard/index.yml` with every
   value annotated `share`/`n`, vocab-guarded to DSL-supported fields.
7. **List-blocks** (`analyze_lists.py`): subtree-signature analysis for nested
   list blocks. Finding: `AbnormalityResistanceOverride` is a defaultable block
   (Merchant 95%); `CombatState` is **not** templatable (1–4% — per-NPC).

Full proposal: [`PROPOSAL.md`](./PROPOSAL.md).

---

## 3. Current state (2026-06-15)

| Item | State |
|---|---|
| Methodology proposed + validated | ✅ |
| NpcData + AIData + TerritoryData analyzed, CV ≥95% | ✅ |
| τ set via sensitivity curve (0.90) | ✅ |
| `npc-standard` regenerated from derived data (6×3 archetypes, provenance) | ✅ |
| DSL round-trip: `merchant-9001-derived.yaml` validates + applies (9 ops), faithful write, reverted clean | ✅ |
| Nested list-block analysis (`AbnormalityResistanceOverride`, socials, combat) | ✅ |
| **NpcSkillData analyzed (174,272 skills, CV 98.7–99.3%)** | ✅ |
| **`<Cluster>Skill` archetypes generated + all 6 validate** | ✅ |
| DSL coverage gaps filed (npc, territory, npcSkills) | ✅ `docs/dsl-requests/2026-06-15-*` |
| Ship `abnormalityResistanceOverride` (+ abnormalities list) / `objectNpcAiParam` / `balanceRef` / 13 territorySpawns fields | ✅ **unblocked + shipped** (DSL rebuilt `9f13a78c`; round-trip idempotent) |
| npcSkills `balanceRef` re-added | ✅ (global empty→null fix) |
| 17/18 npcSkills field gaps (`damageReduceValue`, `gaugeToMpRate`, …) | ✅ **resolved** (DSL `82e3424f`/`6e91acb0`, rebuilt → `6e91acb0`); re-added to `<Cluster>Skill`, round-trip idempotent |
| 4 additional npcSkills gaps (`damageApplyRate`, `parentId`, `returnAnimSet`, `ignoreDefenceRate`) | 🔄 follow-up request filed (`2026-06-15-npcskills-additional-high-prevalence-fields.md`) |
| ObjectNpc `RandomMove` socials (nested AI default) | ✅ investigated — **not shipped** (modal subtree has zero `<Social>` children; 74% < τ=0.90) |
| From-scratch territory authoring (`fences: [[x,y,z]]`) | ✅ confirmed working + idempotent (AOT fence fix `0b1ccf4c`); stale doc filed |
| **Combat-AI structural-skeleton classification (Phases A–E)** | ✅ **NO-GO** — see below |
| **AI split into own `ai-standard` package** | ✅ |
| **AI archetypes proven apply-idempotent (apply ×2, byte-identical)** | ✅ scalar-only → sidesteps the `ai-upsert` append bug |
| **AI library declared complete-to-ceiling + boundary documented** | ✅ `packages/ai-standard/README.md` |
| Skill `actions` / `targetingLists` list-blocks | ⏸ future extension |
| Population-scale DSL round-trip (stratified sample) | ⛔ not started |

---

## 3a. Combat-AI classification — NO-GO finding (2026-06-15)

We tested whether combat AI can be templated by a *finer, data-derived* axis than
the 6 flag-clusters: classify each AI by its **structural skeleton** (tree shape +
bool/string attrs, numeric leaves stripped to parameters), discover behavior
classes globally, parameterize within. Pipeline: `analyze_ai_behavior.py`.

**The concentration gate (Phase B) failed for combat AIs:**

| population | distinct skeletons | top-50 coverage | classes (≥30) cover |
|---|---|---|---|
| 6,767 combat AIs (Normal/Elite/Boss), coarsest level | 2,810 | 15% | **3%** |
| 10,960 all referenced AIs | 3,336 | 32% | 22% |

- Combat AI behavior is **irreducibly bespoke** — ~half the combat trees are
  structurally unique even after stripping numbers; ≥30-member classes cover only
  **3%** of combat AIs at any granularity.
- The 22% that *does* class up is almost entirely **MerchantVillager/ObjectNpc**
  AIs — already covered by the shipped flag-cluster archetypes — not monsters.
- AIs are **not shared** (`distinct_ais == class size`): each NPC's AI is
  separately authored. Recurrence exists only as structure, and only for villagers.

**Conclusion:** the flag-cluster granularity already in the package is the correct
(and only worthwhile) level for AI. There is no hidden set of combat behavior
templates to harvest. **Phase F (codegen) ships nothing** — no combat-AI archetypes.
Within-class param derivation does reach 99.5–99.8% CV (method is sound), so
`derived_ai_behavior.json` is retained should a future need arise, but it is not
integrated into `index.yml`.

---

## 4. Artifacts (this directory — durable copies)

| File | Role |
|---|---|
| `recon.py` | Structural recon (counts, presence%, cardinality) per family |
| `analyze_all.py` | NPC/AI/territory extraction + clustering + CV + τ-curve → `derived_standard_all.json` |
| `analyze_skills.py` | NpcSkillData streaming two-pass CV → `derived_skills.json` |
| `analyze_lists.py` | Nested list-block subtree analysis → `derived_list_blocks.json` |
| `analyze_ai_behavior.py` | Combat-AI structural-skeleton classification → `derived_ai_behavior.json` (NO-GO finding) |
| `codegen.py` | Generates `packages/npc-standard/index.yml` (npc/spawn) **and** `packages/ai-standard/index.yml` (ai) |
| `codegen_skills.py` | Injects `<Cluster>Skill` archetypes into `index.yml` (run AFTER `codegen.py`) |
| `derived_standard_all.json` | Per-cluster scalar defaults (npc/ai/territory) |
| `derived_skills.json` | Per-cluster skill defaults |
| `derived_list_blocks.json` | Per-cluster modal subtrees for list blocks |
| `PROPOSAL.md` | Methodology + validation design |

Original scratch copies are in `temp/npc-research/` (deletable).
Worked consuming spec: `temp/specs/merchant-9001-derived.yaml`.

---

## 5. How to regenerate (run from THIS directory)

```bash
cd reforged/tools/npc-standard
python analyze_all.py      # -> derived_standard_all.json (+ prints CV + tau curve)
python analyze_skills.py   # -> derived_skills.json (954MB stream, CV)
python analyze_lists.py    # -> derived_list_blocks.json (list-block findings)
python codegen.py          # -> npc-standard/index.yml (npc/spawn) + ai-standard/index.yml (ai)
python codegen_skills.py   # -> injects <Cluster>Skill archetypes into npc-standard (run AFTER codegen.py)
# validate the round-trip:
../../../dsl.exe validate ../../temp/specs/merchant-9001-derived.yaml --path <server_datasheet>
```

**Order matters:** `codegen_skills.py` splices into the file `codegen.py` produced;
always run `codegen.py` first (re-running `codegen_skills.py` alone double-injects).

`<server_datasheet>` = `server_datasheet` in `.references`. Paths inside the
scripts are absolute to the live datasheet; JSON is read/written cwd-relative, so
**run from this directory**.

Tuning knobs: `TAU`/`PI` in `analyze_all.py` (+ `codegen.py` re-reads the JSON);
cluster rules in `cluster_of()`; DSL-supported vocab allowlists in `codegen.py`.

---

## 6. Resume checklist (next session)

1. Re-read this file + `PROPOSAL.md`.
2. Check whether the filed DSL gaps were addressed (`docs/dsl-requests/2026-06-15-*`,
   `git -C D:/dev/github-vperim/datasheetlang log`). If `abnormalityResistanceOverride`
   nested-list + the territorySpawns fields are fixed, **extend `codegen.py`** to
   emit those (data already in `derived_list_blocks.json` / dropped-field report) and
   widen the vocab allowlists.
3. Rebuild `dsl.exe` if the DSL repo changed (PowerShell build, per project CLAUDE.md).
4. Re-run the pipeline (section 5); confirm CV still ≥95%.
5. **Skill blocks** done at scalar level; remaining skill work: ship `balanceRef`
   once the empty-string `ref*` crash is fixed, and extend to `actions` /
   `targetingLists` list-blocks (per-cluster modal sequences) via the
   `analyze_lists.py` subtree approach.
6. **Combat-AI sub-archetyping — CLOSED (NO-GO).** Structural-skeleton
   classification (`analyze_ai_behavior.py`) proved combat AI is irreducibly bespoke
   (≥30-member classes cover 3% of combat AIs). Do not retry unless the data changes;
   flag-cluster AI is the right granularity. See §3a.
7. **Population-scale round-trip** (proposal Phase 5): author a stratified sample of
   real NPCs (incl. skills) via the archetypes, apply, structural-diff vs original XML.
   This is now the main open creation task once the filed DSL blockers land.

---

## 7. Key facts / gotchas

- **Apply mutates the live datasheet** (`feature/iod`, git-tracked). Revert with
  `git checkout -- <files>`. Before reverting, confirm via `git diff -w` that the
  only semantic changes are your test IDs — the datasheet may carry committed patch
  content and DSL apply reformats whole files cosmetically.
- `scale` (npcs) and `respawnTime` (spawns) are **required but not defaultable**
  (genuinely per-NPC) — consuming specs must supply them.
- `index.yml` is **generated** — never hand-edit; re-run `codegen.py`.
- The combat AI tree and per-NPC socials are **not** defaultable — don't try.
