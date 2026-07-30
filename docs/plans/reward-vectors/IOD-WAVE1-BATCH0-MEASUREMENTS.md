# IoD Reward Vector Wave 1, Batch 0: measurements

_Measured 2026-07-29 against the WORKING-TREE server datasheet (`server_datasheet` from
`.references`), so specs `002/27` to `002/33` are already applied. Companion to
`IOD-WAVE1-PLAN.md`; this document holds the numbers, the plan holds the build order._

Batch 0 exists because two steps of the wave are numbers I did not have: the feedstock quantity
ladders (Phase B, "quantity ladders are balance work, not a find-and-replace") and the zone quest
XP targets (Phase E2 / RV-07). Both are pulled forward so no later batch stops to wait on a ruling.

Two decisions are requested, in section 5.

## 0. How to re-derive

| What | Source | Fields |
|---|---|---|
| Gear dismantle yield | `EnchantData.xml`, `.//EnchantDecomposition` | `combatItemType`, `rank`, `rareGrade`, `resultItemTemplateId`, `resultItemAmount` |
| Fodder dismantle yield | `DecompositionData.xml`, `Decomposition` 206861 to 206868 | `FixedOutput/Output@templateId`, `@amount` |
| Consumption per attempt | `MaterialEnchantData.xml`, `ItemEnchant` | `materialEnchantId`, `MaterialItem@enchantStep`, `@requiredMoney`, `Material@id`, `@amount` |
| Which items reach which record | all 20 `ItemTemplate*.xml` | `Item@linkMaterialEnchantId`, `@enchantEnable` |
| Quest headers | `QuestData/00NNNN.quest`, ids 1301 to 1399 | `퀘스트종류` (미션 = story / 일반 = zone), `스토리그룹Id`, `수행조건/최소레벨`, `적정수행레벨`, `반복퀘스트`, `수행조건/선행퀘스트` (sentinel `99,99` or `99,9999` = disabled) |
| Quest XP and bags | `CompensationData/QuestCompensationData_*.xml` | `CompensationType@exp`, `@gold`, `@itemBag`, `Item` rows |

Design authority read for this batch: framework `04-power-systems.md` §2c, §4d, §4e, §5e.

## 1. Yield: what a dismantle pays today

### 1a. Family A, gear dismantle (`EnchantData`, the 304 rows Phase B2 repoints)

| combatItemType | rows | ranks 1 to 7 (grade 0/1/2/3) | ranks 8 to 16 |
|---|---|---|---|
| `EQUIP_WEAPON` | 48 (ranks 1 to 12 only) | 4 / 8 / 24 / 48 | 0 / 0 / 0 / 0 |
| `ENCHANT_COMPONENT_WEAPON` | 64 | 4 / 8 / 24 / 48 | 0 / 0 / 0 / 0 |
| `EQUIP_ARMOR_BODY` | 64 | 3 / 6 / 18 / 36 | 0 / 0 / 0 / 0 |
| `EQUIP_ARMOR_ARM` | 64 | 2 / 4 / 12 / 24 | 0 / 0 / 0 / 0 |
| `EQUIP_ARMOR_LEG` | 64 | 2 / 4 / 12 / 24 | 0 / 0 / 0 / 0 |

Grade ratio 1 : 2 : 6 : 12, constant across every paying rank, and every rank 8 and above pays
zero. Current `resultItemTemplateId` spread: 94101 on 20 rows, 94102 to 94111 on 20 rows each,
94112 on 84 rows.

### 1b. Family B, fodder dismantle (`DecompositionData` 206861 to 206868)

Current state, all six of 206863 to 206868 dead (referenced by zero of 25,853 items):

| id | output | amount |
|---|---|---|
| 206861 weapon + body | 94101 | 48 |
| 206862 arm + leg | 94101 | 24 |
| 206863 / 206864 | 94102 | 48 / 24 |
| 206865 / 206866 | 94103 | 48 / 24 |
| 206867 / 206868 | 94104 | 48 / 24 |

The decided replacement (user ruling 2026-07-28, rare-anchored) needs no revisiting; it is
reproduced here only so the authoring step has one table to read:

| Decomposition group | uncommon | rare | superior |
|---|---|---|---|
| weapon + body | 16 | 48 | 96 |
| arm + leg | 8 | 24 | 48 |

## 2. Consumption: what an enchant attempt costs today

### 2a. Measured state, all 100 of our records

`enchantStep` N is the attempt from +N to +N+1, so steps 0 to 8 are the `+0 -> +9` climb, steps 9
to 11 are `+9 -> +12`, and steps 12 to 14 are the Mythic `+12 -> +15` steps.

| Slot group | steps 0-1 | 2-3 | 4-5 | 6-8 | 9-11 | 12-14 |
|---|---|---|---|---|---|---|
| WeC feedstock | 4 | 8 | 24 | 48 | 48 | 60 |
| WeC alkahest 21351 | 2 | 4 | 12 | 24 | 24 | 36 |
| GeB feedstock | 2 | 4 | 12 | 24 | 24 | 36 |
| GeB alkahest 21351 | 1 | 2 | 6 | 12 | 12 | 18 |

**The ladder is band-flat.** All four level ranges (`1..37`, `38..49`, `50..57`, `58..65`) carry
identical amounts, and the four columns of both feedstock sheets in `data/enchant.xlsx` are
identical. The level-range axis exists in the `materialEnchantId` scheme and carries no value.

**`requiredMoney` is `0` on all 1,350 of our `MaterialItem` rows.** The framework's per-attempt gold
cost is not implemented at all.

### 2b. What framework `04 §2c` actually asks for

Reading the table as written: **materials scale by enchant step, gold scales by gear level band.**
There is no per-level-band material scaling in it. The plan's phrase "consumption by band" reads as
gear band and that is not what the source says.

| Step band | MWA target | Feedstock target | Gold target | We ship (WeC) |
|---|---|---|---|---|
| `+0 -> +9`, L1-37 | 1 to 3 | 10 to 30 | under 100g | 2 to 24 MWA, 4 to 48 FS, 0g |
| `+0 -> +9`, L58-65 | 1 to 3 | 10 to 30 | about 500g | identical to the row above |
| `+9 -> +12`, L58-65 | 5 to 10 | 50 to 150 | about 5,000g | 24 MWA, 48 FS, 0g |
| `+12 -> +15` | flat per-step | flat per-step | about 5,000g | 36 MWA, 60 FS, 0g |

Three gaps, in descending size: **gold is absent everywhere**; **MWA is 3x to 8x over target** at
steps 4 and up; **feedstock is under target at steps 0 to 3 and over it at steps 6 to 8**, while
`+9 -> +12` sits just under its 50 floor at 48. Every number in the framework table is tagged
strawman ("numbers TBD").

### 2c. Recommendation: do not change consumption in wave 1

Flattening the item identity changes no amount, so nothing regresses if the ladder is left alone.
Re-deriving it now means:

- Changing demand across every gear band on the server in the same apply that changes IoD supply
  three ways (drop removal, fodder ladder, faucet deletion). Phase B's own argument for the
  rare-anchored fodder ladder was to keep the drop removal the single supply variable; a demand
  change in the same wave discards that.
- Guessing against a strawman. The `§2c` numbers are explicitly TBD, and the honest input is
  measured accumulation data, which wave 1 is what produces.
- Doing half a job. The largest gap is the missing gold cost, which is not in this plan at all and
  is a framework-wide change, not an IoD one.

So: Phase B2 keeps `resultItemAmount` untouched (as it already says), the workbook keeps its
amounts, and the ladder re-derivation plus the gold cost become their own backlog item with their
own review. That is a deviation from the Phase B note that says to re-derive inside this wave, so
it needs a ruling (section 5, decision 1).

Family A's amounts should also stay untouched, for a second reason: its 1 : 2 : 6 : 12 grade shape
is the reference the fodder ladder was just anchored against, so moving both at once removes the
only baseline the next tuning pass has.

## 3. Zone quest XP (RV-07)

### 3a. The live corpus

74 quests exist in group 13 on disk; 63 live, 11 sentinel-disabled. Of the live set, 28 are story
(`미션`) and **35 are zone (`일반`)**, which matches the plan's bag-mode split exactly:

| itemBag mode | count | quest ids |
|---|---|---|
| `allpay` | 12 | 1327, 1341, 1345, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1390 |
| none | 15 | 1302, 1312, 1321, 1328, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1346, 1347, 1348, 1349 |
| `class` | 8 | 1319, 1322, 1324, 1325, 1326, 1330, 1332, 1333 |

Repeatables in that set: **2**, not 3. Quests 1334 and 1341 carry `반복퀘스트` = `반복`; every other
live zone quest is `1회성`.

### 3b. The story baseline, raw and corrected

Bracket = minLevel rounded down to an odd number, so 1-2, 3-4, 5-6, 7-8, 9-10. Corrections applied
per the plan: the twelve class-training missions (1371 to 1381 and 1387, all 2,100 XP at minLevel 2)
count **once**, because a character completes exactly one; the paired gathering intros 1382 and 1383
(100 XP) are excluded as non-story payouts.

| Bracket | n raw | median raw | cap raw | n corrected | median corrected | **cap (25%)** | corrected values |
|---|---|---|---|---|---|---|---|
| 1-2 | 14 | 2,100 | 525 | 3 | 800 | **200** | 500, 800, 2100 |
| 3-4 | 3 | 900 | 225 | 3 | 900 | **225** | 400, 900, 2600 |
| 5-6 | 4 | 1,200 | 300 | 2 | 3,600 | **900** | 2300, 4900 |
| 7-8 | 4 | 5,220 | 1,305 | 4 | 5,220 | **1,305** | 3200, 3600, 6840, 8400 |
| 9-10 | 3 | 4,500 | 1,125 | 3 | 4,500 | **1,125** | 2000, 4500, 14600 |

Both corrections bite hard and in opposite directions: bracket 1-2 falls from 525 to 200, bracket
5-6 rises from 300 to 900.

Two properties worth knowing. The 9-10 cap (1,125) is **below** the 7-8 cap (1,305), because 1350
pays 8,400 at level 8 while the 9-10 bracket is dragged down by 1317 at 2,000; this is harmless
because no live zone quest sits above minLevel 8. And bracket 3-4's baseline rests on just three
story quests, two of which (1329 at 400, 1384 at 900) are small utility missions, so its 225 cap is
the least well-supported number in the table.

### 3c. Per-quest targets, clamped to the cap

**26 of 35 change**, not 29. (The plan's 29 predates the ruled median correction; the raw-median
count is 28 and the corrected count is 26.)

| Bracket | Quest | min | bag | now | target | delta | Owning spec |
|---|---|---|---|---|---|---|---|
| 1-2 | 1302 | 1 | none | 400 | 200 | -200 | `002/40` |
| 1-2 | 1321 | 1 | none | 800 | 200 | -600 | `002/40` |
| 1-2 | 1322 | 1 | class | 500 | 200 | -300 | `002/28` |
| 1-2 | 1319 | 2 | class | 600 | 200 | -400 | `002/28` |
| 1-2 | 1324 | 2 | class | 900 | 200 | -700 | `002/28` |
| 3-4 | 1325 | 3 | class | 500 | 220 | -280 | `002/28` |
| 3-4 | 1353 | 3 | allpay | 2,300 | 220 | -2,080 | `002/40` |
| 3-4 | 1354 | 3 | allpay | 2,300 | 220 | -2,080 | `002/40` |
| 3-4 | 1327 | 4 | allpay | 800 | 220 | -580 | `002/40` |
| 3-4 | 1328 | 4 | none | 1,500 | 220 | -1,280 | `002/40` |
| 3-4 | 1351 | 4 | allpay | 800 | 220 | -580 | `002/40` |
| 3-4 | 1352 | 4 | allpay | 800 | 220 | -580 | `002/40` |
| 5-6 | 1326 | 5 | class | 2,000 | 900 | -1,100 | `002/40`, reproduce 12 class rows from `001/04` |
| 5-6 | 1330 | 5 | class | 1,900 | 900 | -1,000 | `002/40`, reproduce 12 class rows from `001/04` |
| 5-6 | 1348 | 5 | none | 900 | 900 | 0 | `002/29` |
| 5-6 | 1355 | 5 | allpay | 3,100 | 900 | -2,200 | `002/40` |
| 5-6 | 1356 | 5 | allpay | 3,100 | 900 | -2,200 | `002/40` |
| 5-6 | 1332 | 6 | class | 900 | 900 | 0 | `002/29` |
| 5-6 | 1333 | 6 | class | 1,700 | 900 | -800 | `002/29` |
| 5-6 | 1334 | 6 | none | 800 | 800 | 0 | `002/40`, REPEATABLE |
| 5-6 | 1347 | 6 | none | 900 | 900 | 0 | `002/30` |
| 5-6 | 1390 | 6 | allpay | 300 | 300 | 0 | `002/40` |
| 7-8 | 1336 | 7 | none | 600 | 600 | 0 | `002/40` |
| 7-8 | 1337 | 7 | none | 1,500 | 1,300 | -200 | `002/40` |
| 7-8 | 1338 | 7 | none | 500 | 500 | 0 | `002/40` |
| 7-8 | 1349 | 7 | none | 2,300 | 1,300 | -1,000 | `002/29` |
| 7-8 | 1357 | 7 | allpay | 4,000 | 1,300 | -2,700 | `002/40` |
| 7-8 | 1358 | 7 | allpay | 4,000 | 1,300 | -2,700 | `002/40` |
| 7-8 | 1312 | 8 | none | 2,500 | 1,300 | -1,200 | `002/40` |
| 7-8 | 1335 | 8 | none | 600 | 600 | 0 | `002/40` |
| 7-8 | 1339 | 8 | none | 3,200 | 1,300 | -1,900 | `002/40` |
| 7-8 | 1340 | 8 | none | 3,200 | 1,300 | -1,900 | `002/40` |
| 7-8 | 1341 | 8 | allpay | 1,500 | 1,300 | -200 | `002/40`, REPEATABLE |
| 7-8 | 1345 | 8 | allpay | 500 | 500 | 0 | `002/40` |
| 7-8 | 1346 | 8 | none | 6,000 | 1,300 | -4,700 | `002/40` |

Caps are rounded to the nearest 10, which is why the 3-4 target reads 220 and the 7-8 target 1,300.

### 3d. What the pass costs, in XP

| Measure | Before | After |
|---|---|---|
| Zone quest XP available on the island | 58,200 | 24,740 |
| Story XP available to one character (unchanged) | 57,740 | 57,740 |
| Zone share of all obtainable IoD XP | 50% | 30% |

**33,460 XP removed, 57% of the zone-quest pool.** The story spine is untouched and was
live-validated as self-sufficient to level 10, so the wave does not threaten the mandatory path; what
it removes is the surplus that let a completionist outrun the bracket.

**RULED 2026-07-29 (user): the XP loss is a non-issue and needs no mitigation.** The story spine
alone carries a player to level 10 without counting mob XP, so the reduction cannot strand anyone on
the mandatory path. The expected direction of travel is FURTHER reduction, not less: every zone quest
this project adds inflates the pool again, so the cap will likely tighten even after this pass lands.
Treat the 57% figure as progress toward the target rather than as a risk to manage, and do not size
compensation against it (the token is compensation by parity per `03 §3b-i`, not a refund of XP).

### 3e. Ops per owning spec

Every one of the 35 gets a token row, so every one needs a statement somewhere:

| Spec | Quests | Count |
|---|---|---|
| `002/28-iod-reward-cadence.yaml` (amend) | 1319, 1322, 1324, 1325 | 4 |
| `002/29-iod-expedition-set-distribution.yaml` (amend) | 1332, 1333, 1348, 1349 | 4 |
| `002/30-iod-remove-mid-tier-gear.yaml` (amend) | 1347 | 1 |
| `002/40` new, reproducing `001/04` class rows | 1326, 1330 | 2 |
| `002/40` new | the remaining 24 | 24 |

## 4. Plan corrections this batch produced

| # | Plan said | Measured | Consequence |
|---|---|---|---|
| C1 | The 304 decomposition rows use **four** `combatItemType` values | **Five.** `ENCHANT_COMPONENT_WEAPON` carries 64 of the 304 rows. `EQUIP_WEAPON` covers ranks 1 to 12 (48 rows); the other four cover 1 to 16 (64 each) | B2 must enumerate five types or **64 of 304 rows keep pointing at a retired tier**. `ENCHANT_COMPONENT_WEAPON` is a real enum member (DSL docs `schemas/enchants/enchant-data.mdx`), so this is authorable |
| C2 | `MaterialEnchantData` carries "4 and 12" | 4 / 8 / 24 / 48 / 60 (WeC) and 2 / 4 / 12 / 24 / 36 (GeB), by step | The mechanism map understates the ladder; see section 2a |
| C3 | "consumption scales by band (§2c)" | `§2c` scales **materials by enchant step** and **gold by gear band**. Our ladder is band-flat, which is compliant on the material axis | Removes most of the re-derivation case; see section 2c |
| C4 | (not mentioned) | `requiredMoney` is 0 on all 1,350 of our `MaterialItem` rows | The `§2c` gold sink is entirely unimplemented. Out of wave scope, parked |
| C5 | "all reachable enchanting consumes 94101" after B1 | Holds, with a documented exception: vanilla records 10401 and 10402 consume 94104 and are referenced by 9 live items (163029 to 163037, level-60 superior armor in `ItemTemplate_NAEU.xml`), **all 9 carrying `enchantEnable="False"`** | No op needed. Phase G's referential gate will see these links and must not read them as a break |
| C6 | 713 items affected by the Relic collapse, 575 in base | **Confirmed exactly**: 713 rows, 713 distinct ids, 575 in `ItemTemplate.xml`, the rest in `_KR` (92), `_RUS` (32), `_JP` (14) | The plan's figure stands; the earlier 559 was indeed wrong |
| C7 | 29 of 35 zone quests over the cap | **26** on the ruled corrected-median baseline (28 on raw medians) | Section 3c is the authoritative table |
| C8 | 3 of the 35 are repeatables | **2**: 1334 and 1341 | 1334 is already under its cap; 1341 needs -200. Repeat-specific tuning stays RV-08 |
| C9 | (not mentioned) | Fodder rows use `FixedOutput/Output@templateId,@amount`, not `RandomOutput` with min/max/probability | B3 authoring shape |

## 5. Decisions: BOTH RULED 2026-07-29

**Decision 1 RULED: defer.** `MaterialEnchantData` amounts and `EnchantData` `resultItemAmount` stay
untouched in wave 1. The `§2c` re-derivation and the missing per-attempt gold cost become their own
backlog item.

**Decision 2 RULED: clamp**, per the table in section 3c. The flatness is accepted; see the XP ruling
in section 3d, which also removes XP loss as a concern to manage.

The original write-ups follow, kept as the reasoning behind both rulings.

**Decision 1: the consumption ladder.** Recommendation is to leave `MaterialEnchantData` amounts and
`EnchantData` `resultItemAmount` untouched in wave 1, and split the `§2c` re-derivation (plus the
missing per-attempt gold cost) into its own backlog item. Reasoning in section 2c. The alternative is
to re-derive now, which changes server-wide enchanting demand inside a wave that already changes IoD
supply three ways.

**Decision 2: the XP shaping rule.** Recommendation is the clamp in section 3c: any zone quest above
its bracket cap drops to the cap, anything already under it is untouched. It matches RV-07's wording
("reduce any above the cap") and it never lowers a quest that is already compliant. The cost is
flatness: seven quests in bracket 3-4 all land on 220 and eight in 7-8 all land on 1,300, so a long
chain pays what a one-step fetch pays. The dial, if that flatness is not acceptable, is to spread the
over-cap quests across a band (for example 60% of cap up to cap) so their relative ordering survives;
that is more numbers to review and it still never raises anything.
