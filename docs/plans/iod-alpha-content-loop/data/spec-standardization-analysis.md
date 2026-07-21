# IoD Patch 001 Spec Standardization Analysis

Statistical analysis of the patch 001 IoD specs to find redundancy that the DSL
definitions feature (`$extends` / `$with` / `$params`, cross-package exports) can
factor out. This is a proposal only. No spec, generator, or package was modified.

Method: each spec was parsed with PyYAML, every operation flattened to dotted
leaf keys, and per-attribute value histograms computed (distinct count, modal
value, modal share). Spawn entries were additionally clustered by attribute
fingerprint (all keys except pure per-row ids/positions/desc). Projected sizes
count emitted YAML leaf lines (one per scalar key; an inline flow list counts as
one line), which is the honest unit because `$extends` removes leaf lines, not
structural lines.

Scripts: `scratchpad/analyze.py`, `analyze2.py`, `analyze3.py` (session scratch).

---

## 1. Spec inventory

| Spec | Section(s) | Ops | File lines | Verdict |
|------|-----------|-----|-----------|---------|
| 00-iod-region-strings | regionStrings | 2 | 20 | skip (trivial) |
| 01-iod-area-sections | areaSections | 9 upsert (+1 nested, +1 delete) | 367 | **standardize (ClassicSection)** |
| 02-iod-spawn-restore | territoryGroups / territories / territorySpawns | 17 / 217 / 217 | 12543 | **standardize (dominant win)** |
| 03-iod-spawn-removals | territorySpawns / territoryGroups delete | 8 | 65 | skip (deletes, key-only) |
| 04-iod-shops | buyLists / buyMenuLists / villagerMenus | 22 | 342 | skip (literal item lists) |
| 05-iod-quest-rewards | questCompensations | 63 | 1124 | leave as-is (lists replace) |
| 08-legacy-strings-restore | strings | large | 4346 | skip (id -> string pairs) |
| 18-iod-item-string-fixes | strings | small | 18 | skip |

Spec 02 alone is 12543 of the ~18800 total spec lines. It is where essentially
all the redundancy lives, and where standardization pays off.

Context: patch 001 currently uses **zero** `$extends`. Patch 002 already uses
definitions and package imports throughout, so factoring via definitions is an
established project pattern, not a new mechanism being introduced here.

---

## 2. Spec 02 territorySpawns (217 entries, the dominant redundancy)

Each spawn entry carries **42 leaf keys**. Histogram result:

- **28 keys are byte-identical across all 217 entries** (modal share = 1.00).
- **14 keys vary**, and of those only 6 are genuinely per-row: `territoryId`,
  `npcInstanceId`, `pos`, `groupId`, `desc`, `npcTemplateId`. The rest cluster
  into a handful of values.

The 28 constant keys:

```
aggroIgnorePartyId=""          aggroReceiveOnlyInSight=false   aggroSendToTerritory=""
aggroShareGroupId=0            alertAngle=360                  alertRadius=250
cautionStateNoMoving=false     conditionalSpawn=false          delaySpawnTimeWhenWorldStart=0
escapeLocation=[0,0,0]         excludeAggroLimit=false         huntingZoneId=13
isReturnMyTerritory=false      moveInTerritory=false           msgInterval=0
msgProb=0                      offsetZ=0                       peaceStateNoMoving=false
popupMsg=""                    questPatrol=false               randomGroupId=0
randomPos=true                 respawnRandomTime=2000          respawnTime=20000
returnDistance=2000            viewAngle=360                   viewRadius=200
voidSpawn=false
```

The 14 varying keys and their value spread:

| Key | Distinct | Value distribution |
|-----|----------|--------------------|
| territoryId / npcInstanceId / pos | 217 | per-row (unavoidable) |
| npcTemplateId | 27 | per-row |
| groupId | 17 | per-row |
| desc | 25 | per-row (Korean mob names) |
| ai | 8 | {6:80, 11:37, 1:27, 29:24, 108:17, 31:16, ...} |
| spawnCount | 5 | {1:159, 6:37, 3:17, 12:2, 5:2} |
| aggroSendToPartyDistance | 3 | {2000:116, 500:91, 1000:10} |
| aggroSendToClanDistance | 2 | {0:207, 100:10} |
| isAggressiveMonster | 2 | {false:200, true:17} |
| isReturn | 2 | {false:200, true:17} (paired with isAggressiveMonster) |
| memberId | 3 | {0:178, ...} modal 0.82 |
| dir | 2 | {0:206, ...} modal 0.95 |

### Fingerprint clustering

Excluding only ids/pos/desc, the 217 entries collapse to **13 distinct
behavioral fingerprints** (largest cluster 74 entries, then 37, 27, 24, 17, and
a tail of small clusters). If the behavioral fields (`ai`, `spawnCount`,
aggro-distance, radii, return flags) are also excluded, they collapse to **3
fingerprints** (essentially the aggroSendToPartyDistance 2000/500/1000 split).
This confirms the entries are near-copies of a single template with a small set
of per-mob behavioral overrides, exactly the shape `$extends` addresses.

### Diff vs npc-standard spawn archetypes

Comparing the IoD constant set against `npc-standard.NormalMonsterSpawn`:

- **17 of the 28 IoD constants match the archetype exactly, with 0 conflicts.**
  (`aggroShareGroupId`, `delaySpawnTimeWhenWorldStart`, `aggroIgnorePartyId`,
  `questPatrol`, `aggroSendToTerritory`, `msgInterval`, `conditionalSpawn`,
  `voidSpawn`, `isReturnMyTerritory`, `popupMsg`, `msgProb`, `viewAngle`,
  `cautionStateNoMoving`, `excludeAggroLimit`, `aggroReceiveOnlyInSight`,
  `offsetZ`, `alertAngle`.)
- **11 IoD constants are not in the archetype at all**: `randomPos`(=true),
  `respawnTime`(=20000), `respawnRandomTime`(=2000), `viewRadius`(=200),
  `alertRadius`(=250), `returnDistance`(=2000), `moveInTerritory`,
  `peaceStateNoMoving`, `escapeLocation`, `randomGroupId`, `huntingZoneId`.
  These are restoration-fidelity values carried from the v17 fences and the v31
  modal donor, not global-population modals.
- The archetype carries **`msgBroadcastingChannel=false`**, which the IoD spec
  never emits.

Verdict on reuse: the 17/28 exact match validates that the IoD constants are
canonical (they agree with the full-population modal wherever both define a key),
but the IoD spawns are a distinct restoration template, not a generic normal
monster. **Do not blindly `$extends npc-standard.NormalMonsterSpawn`**: it would
(a) inject `msgBroadcastingChannel=false` into all 217 upserts, a silent output
divergence from the current generator, and (b) it still would not supply the 11
IoD-specific constants. Recommendation: a standalone restoration base
(`IoDSpawnBase`) that owns all 35 non-per-row constants directly. Chaining it off
the archetype saves only ~17 base-def lines while adding the injection risk, so
it is not worth it.

### Projection (spawns)

Design: `IoDSpawnBase` definition captures the modal value of all 35 non-per-row
keys. Each entry then emits `$extends` + the 6 per-row fields
(`groupId`, `territoryId`, `npcInstanceId`, `npcTemplateId`, `desc`, `pos`) plus
only the keys that deviate from base.

- Mean per-entry overrides beyond base: **1.79**.
- Override-count histogram: `{0 overrides: 74 entries, 1: 30, 2: 38, 3: 48, 5: 23, 6: 4}`.
- Current emitted leaf lines: **9114** (~42.0/entry).
- Projected: **~1949** (base def ~40 lines + ~8.8 lines/entry).
- **Reduction: 9114 -> ~1949, roughly 79% fewer leaf lines.**

Correctness: safe. All 14 varying keys are scalars, so deep-merge child-wins
applies cleanly. The only list fields are `pos` (always written per row) and
`escapeLocation` (constant `[0,0,0]`, lives in base, never overridden), so the
"lists replace entirely" rule is never triggered as a hazard here.

---

## 3. Spec 02 territories (217 entries)

11 leaf keys per entry. **7 are constant** across all 217:
`huntingZoneId=13`, `type=normal`, `addMaxZ=256.0`, `subtractMinZ=0.0`,
`eventId=0`, `randomPosMinDist=100.0`, `peaceMoveNpcCheckDist=100.0`.
Per-row: `groupId`, `territoryId`, `desc`, `fences`.

- Current emitted leaf lines: **2387**.
- Projected with a `ClassicTerritory` base (7 const keys) + per-row
  (`$extends`, groupId, territoryId, desc, fences): **~1092**.
- **Reduction: ~54% fewer.**

Correctness: safe. `fences` is the only list and is always a per-row literal;
"lists replace" is not a hazard.

## Spec 02 territoryGroups (17 entries)

Only 3 keys (`huntingZoneId`, `groupId`, `desc`), all per-row except the
constant `huntingZoneId`. Not worth a definition. Skip.

Spec 02 whole-file impact: content leaf lines ~11500 -> ~3100, and the 12543-line
file projects to roughly 3500 to 4000 lines.

---

## 4. Spec 01 areaSections (ClassicSection)

10 section rows (9 full restored sections + 1 partial ring-only revert row for
13030). 30 distinct attribute keys. No key is constant across all 10 rows only
because the partial row omits most fields; across the **9 full rows**:

- ~12 keys are effectively constant (share 1.00, present 9/9): `areaName`,
  `continentId`, `desTex`, `floor`, `guildWar`, `huntingZoneId=-1`, `protect`,
  `recallReviveContinentId`, `recallScrollContinentId`, `recallScrollPos`,
  `ride`, `trade`.
- Several more are high-modal and make good base defaults with occasional
  per-row overrides: `duel`(0.89), `campId`(0.89), `subtractMinZ`(0.89),
  `recallRevivePos`(0.89), `worldMapSectionId`(0.89), `pcMoveCylinder`(0.78),
  `pk`(0.78), `restBonus`(0.75), `vender`(0.67).
- Genuinely per-row: `sectionId`, `nameId`, `desc`, `priority`, `addMaxZ`,
  `fences`, plus the rare `enableItemId` / `disableItemId`.

Design: a `ClassicSection` base (12 constants + high-modal defaults). Each row
then emits `$extends` + sectionId/nameId/desc/priority/addMaxZ/fences + a couple
of flag overrides.

- Current emitted leaf lines: **255**.
- Projected: **~140** (base ~22 lines once + ~9 to 12 lines per row).
- **Reduction: ~45% fewer.**

Absolute savings are modest (the spec is small), but a `ClassicSection`
archetype has strong reuse value: patch scope covers five IoD layers plus hub
cities and dungeons, and future area/section restoration work will reproduce the
same attribute envelope. Worth doing for consistency and reuse, not for the
line count on this one spec.

Correctness: safe (scalars); `fences` is a per-row list, no replace hazard. One
caution: the partial 13030 row must still `$extends` and then `$remove` any base
keys a ring-only revert should not carry, or simply not extend the base. Keep it
literal to avoid injecting section attributes into a geometry-only revert.

---

## 5. Spec 05 quest rewards (definitions do NOT help)

63 questCompensations ops: 14 carry per-class item bags, 49 are plain exp/gold.

Bag structure (questId, item count, distinct templateIds):

```
armor bags  (3 distinct templateIds shared across 12 classes):
    1303,1304,1305,1312,1315,1317,1322,1325,1337,1347   (12 items each)
weapon bags (12 distinct templateIds, unique per class):
    1309,1319,1329                                       (12 items each)
mixed 20-item bag: 1316 (13 distinct templateIds)
```

Two blockers make definitions ineffective here:

1. **Lists replace entirely on merge.** The `items` list is the entire bulk of
   each bag and cannot be factored by `$extends`; every bag must spell out its
   list literally regardless.
2. **Class ordering is not even consistent.** There are **5 distinct class
   orderings** across the bags (one starts `berserker,lancer,archer,slayer,...`,
   another `warrior,lancer,slayer,berserker,...`), so a shared ordered class
   list would not apply uniformly.

The only factorable part is the compensation envelope (`compensationId: 1`,
`type: "normal"`, `itemBag: "class"`), which is ~3 lines times 14 bags, roughly
40 lines out of 1124. Not worth the indirection. **Recommendation: leave 05
as-is.** This is the honest answer the histograms confirm.

---

## 6. Specs 04 / 00 / 08 / 18 (skip)

- **04 shops**: `buyLists` are literal `itemId` + `priceRevision` list elements;
  lists replace, so the per-item rows cannot be factored. `buyMenuLists` and
  `villagerMenus` are small and structurally varied. The only repetition is
  `priceRevision: 1`, which lives inside list elements and is unreachable by
  `$extends`. Skip.
- **00 / 08 / 18 strings**: pure `id -> string` pairs with no attribute
  structure to factor. 08 is large (4346 lines) but it is 4346 flat pairs; there
  is no archetype to extract. Skip.

---

## 7. Ranked proposals

Each proposal is a **generator change**, not a hand-spec edit: 02 is emitted by
`gen_spawn_specs.py`, 01 by `gen_section_specs.py`, 05 by `gen_reward_specs.py`.
`gen_spawn_specs.py` already computes the per-template modal attribute set
(`build_v31_patterns`), so teaching it to emit `$extends IoDSpawnBase` + residual
instead of the full attribute dump is a change to the render path, not new
analysis.

| Rank | Proposal | Where it lives | Current -> projected (leaf lines) | Reduction | Risk |
|------|----------|----------------|-----------------------------------|-----------|------|
| 1 | `IoDSpawnBase` for 02 territorySpawns | new package `spawn-restore-standard` (reused by future zone restorations) or patch-local `definitions:` block | 9114 -> ~1949 | ~79% | Low |
| 2 | `ClassicTerritory` for 02 territories | same package as #1 | 2387 -> ~1092 | ~54% | Low |
| 3 | `ClassicSection` for 01 areaSections | new package `area-section-standard` or patch-local block | 255 -> ~140 | ~45% | Low |
| 4 | reward envelope for 05 | n/a | 1124 -> ~1084 | ~4% | not worth it |
| 5 | shops / strings | n/a | no benefit | 0 | skip |

### Placement reasoning

- **Spawns and territories (#1, #2)**: the restoration-fidelity constants
  (`respawnTime=20000`, `randomPos=true`, `viewRadius=200`, ring/return values)
  are shared by any future classic zone restoration, not just IoD zone 13. Patch
  scope enumerates five IoD layers (13, 64, 213, 313, 364) plus dungeon 436, and
  the content-restoration workflow is explicitly reused per zone. That recurrence
  argues for a small **package** (`spawn-restore-standard`) exporting
  `IoDSpawnBase` (better named `RestoreSpawnBase`) and `ClassicTerritory`, rather
  than a patch-local block. If the team prefers to keep patch 001 self-contained
  until a second zone actually needs it, a patch-local `definitions:` block in 02
  captures the same 79% reduction now and can be promoted to a package later. Do
  not extend `npc-standard.NormalMonsterSpawn` (section 2: injection + semantic
  mismatch).
- **Sections (#3)**: same recurrence logic (hub cities and other areas). A
  `ClassicSection` archetype in an `area-section-standard` package is the durable
  home; patch-local is acceptable as a first step.
- **Rewards (#4)**: no package, no definition. The lists-replace rule makes it a
  poor fit.

### What cannot be factored (kept literal in every design)

- Spawns: `territoryId`, `npcInstanceId`, `npcTemplateId`, `groupId`, `desc`,
  `pos`, and the per-mob behavioral overrides (`ai`, `spawnCount`, aggro
  distances, `isAggressiveMonster`/`isReturn` pair).
- Territories: `groupId`, `territoryId`, `desc`, `fences`.
- Sections: `sectionId`, `nameId`, `desc`, `priority`, `addMaxZ`, `fences`.
- Rewards: the entire `items` list (lists replace).

---

## 8. Surprises from the histograms

- **Spawns are 28/42 constant.** Two thirds of every spawn entry is dead-copy
  boilerplate; only 6 keys are truly per-row. The 42-line entries carry ~8 lines
  of real information.
- **Behavioral variety is tiny.** 217 entries reduce to 13 fingerprints, and
  the whole varying surface is 6 low-cardinality fields. The restoration is one
  template with light per-mob tuning.
- **`isAggressiveMonster` and `isReturn` move together** (both true on exactly
  the same 17 entries), suggesting a single "aggressive" sub-archetype rather
  than two independent flags.
- **The IoD constants agree with the global npc-standard modal on all 17 shared
  keys with zero conflicts**, which is a good independent sanity check that the
  v31-modal donor pipeline produced canonical values.
- **Reward class ordering is inconsistent (5 orderings)**, which is the concrete
  reason a class-list definition would be wrong, not just unhelpful.
