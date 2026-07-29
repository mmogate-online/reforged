# IoD Reward Vector Wave 1: token spine and feedstock flattening

_Planned 2026-07-28. Implementation plan for the first wave of `IOD-BACKLOG.md`, folded into the
OPEN patch 002. Nothing in this plan has been applied. The backlog holds the design rulings and the
work-item catalogue; this document holds the build order, the file-level change list, the gates and
the open dependencies._

Scope: backlog items **RV-01** (early-progression token item), **RV-03** (token threading, zone
quest leg), **RV-07** (zone quest XP pass), **RV-26** (loot correction, feedstock slice) and
**RV-28** (feedstock flattening).

## 0. Why this is one wave and not five

The six requested changes look independent and are not. The token cannot be threaded into zone
quests without the XP pass, because the framework's reward-parity rule (`03 §3b-i`) says the token
compensates for XP removed, so shipping the token alone is pure reward inflation. The feedstock
loot removal and the feedstock flattening touch the same generators and the same package
definition. And all of it lands in patch 002, whose working tree already holds the rows in
question.

**The timing argument for folding into patch 002 is load-bearing.** `ECompensation_13.xml` carries
4 feedstock rows at committed HEAD and 51 in the working tree; `MaterialEnchantData.xml` carries
846 at HEAD and 1,656 in the tree. The rows this wave removes exist only in the dirty tree, so
neutering the generator and replaying the patch simply never writes them. No delete op is needed
and no committed baseline has to be fought. If patch 002 closed first, the same outcome would
require explicit deletes against a baseline that contains them, and it is not established that
`eCompensations: upsert` can delete a single `ItemBag` at all (see PROBE-F2).

Accepted cost of folding: patch 002's revalidation surface now includes enchanting at a leveling
tier and at an endgame tier, not just the Island of Dawn quest wave, and Guardian Legion (patch
003) stays blocked longer.

## 1. Rulings this wave implements

Design rulings live in `IOD-BACKLOG.md` section 1. The ones added by this session govern the build
order below: fold into patch 002; family A keeps paying feedstock; surviving id is 94101 with tiers
94102 to 94112 retired but resident; migrate the mechanic families and delete the faucet families;
zone quest XP is capped against the **median** story quest of the same level bracket; the token is
`boundType: Loot` and untradable; a token paid into a `class` bag is authored as 12 duplicate rows.

## 2. Mechanism map

What the research wave established, so the build does not re-derive it. Full evidence in the
research reports referenced from the backlog.

**Three dismantle systems exist, and the one named in the original request is the least important.**

| Family | Keyed by | Rows | Role after this wave |
|---|---|---|---|
| A: `EnchantData` -> `EnchantDecompositionData` | `combatItemType` x `rank` x `rareGrade` | 304 | Gear dismantle refund. Identity collapses to 94101, the 4/8/24/48 grade ladder stays |
| B: `DecompositionData.xml` | per item, `ItemTemplate@decompositionId` | 8 ours | The sanctioned fodder faucet. Restructured to key on grade |
| C: `ItemDecompositionData.xml` (Hammer) | `combatItemType` x `rareGrade` | vanilla | Untouched, outputs no feedstock |

**The tier ladder is one expression.** `tools/enchant-materials/generate_enchant_materials.py` line
35 defines `FEEDSTOCK_BASE_ID = 94100` and line 304 computes `feedstock_id = FEEDSTOCK_BASE_ID +
config.rank`. The workbook `data/enchant.xlsx` carries only amounts, never item ids. Two further
generators carry their own tier mappings: `tools/zone-loot/fill_zone_loot.py` (gear tier to
feedstock id) and `tools/iod-loot/generate_iod_loot.py`.

**Selection chain, for reference:** `ItemTemplate@linkMaterialEnchantId` ->
`MaterialEnchantData/ItemEnchant@materialEnchantId` -> `MaterialItem/Material@id`. There is no
runtime lookup on level or grade; the material is baked into the link at authoring time.

**Corpus size:** 4,620 real references across 117 files, decomposing to 1,991 record-level ops.
`QuestCompensationData` contains **zero** feedstock and is out of scope. `LimitedDrop.xml` is
entirely commented out and is out of scope.

## 3. Build order

### Phase A: groundwork (no content change)

Nothing in later phases can sync to the client until this lands.

**Read this before touching the map. A mapped key with no descriptor is FAIL-CLOSED, not silent.**
An earlier draft of this plan said an unmatched key produces a silent zero-file plan "as `AreaData`
demonstrated". That is wrong on both halves. Verified against the shipped binary and source:
`SyncOrchestrator.Plan()` emits **E603** for an entity absent from `sync-config.yaml`, and although
it `continue`s past planning that one entity, `SyncPlan.IsValid` is `Errors.Count == 0`, so
`SyncCommand` prints the errors and returns `ExitCodes.ValidationError = 2` **before writing
anything**. One bad key therefore aborts the client leg for the ENTIRE patch. The `AreaData`
incident was a different bug: a descriptor existed, and its `source_mapping` omitted the
subdirectory prefix.

Two consequences. A key mapped to a descriptor that does not exist is far worse than an absent key.
And a key mapped to `None` is safe, because migrate never requests it for sync.

| Change | File | Note |
|---|---|---|
| Map keys that HAVE a descriptor | `tools/migrate/migrate.py` | `decompositions`, `itemMixes`, `eventMatchingEvents`, `achievements`. Each must land in the same change as its descriptor below, never before it |
| Map keys with NO client leg to `None` | `tools/migrate/migrate.py` | `stackAttendanceEvent` (server-only, the client folder has no `SampleEventList`), plus the other eight `eventMatching*` sections. `None` closes the `ENTITY_KEY_PATTERN` blind spot without arming E603 |
| Add entity descriptors | `config/sync-config.yaml` | `DecompositionData`, `ItemMixData`, `EventMatching`, `AchievementList`. These four carry the feedstock id on the client. Their strategies are NOT uniform: see the measured shapes below |
| Add token constant | `packages/iod-tokens/index.yml` | `IOD_PROGRESSION_TOKEN: 95217`, in `variables:` and `exports.variables:`. Package is already workspace-registered |

**Do NOT map `enchantDatas` or `itemConversions`.** An earlier draft said to map them anyway "to
remove the silent-skip hazard". With E603 fail-closed that advice would hard-stop the sync. Leave
them unmapped, or map to `None` if a spec in this patch uses those keys.

**`EventMatching` has nine DSL sections**, not one: `eventMatchingEvents`, `Rewards`,
`Achievements`, `Timeline`, `Settings`, `Filters`, `DefaultImages`, `ContentBanner`, `PlayGuide`.
All nine write the same file and client sync is file-scoped, so mapping one carries the whole file.
The blind spot bites only when a spec uses one of the other eight WITHOUT also using
`eventMatchingEvents`. C3 uses `eventMatchingEvents`, so this wave is covered; map the rest anyway.

**Gate A, restated so it is actually verifiable.** `migrate.py` prints only counts ("N entities
modified", "N server-only skipped") and never names entities, so "the log lists all six keys"
cannot be checked. The real gate is per family, on the client tree: after a REAL sync (never a
dry-run), confirm each of the four registered families has a changed client file, and diff it at
ATTRIBUTE level against the pre-sync snapshot. Expect a first-adoption rewrite: registering a
never-synced family can legitimately rewrite shipped client values, as `StrSheet_Creature` did when
it merged duplicate wrappers and lowercased two booleans. Then confirm a second sync writes 0 files.

**Boolean-case corruption was investigated and does NOT apply here.** `AchievementList` carries
5,278 uppercase `True` / `False` values on boolean-typed client attributes, 3,468 of them on
`use="required"` attributes, which looks exactly like the `ContinentData` incident. It is not:
`XmlFilterer.NormalizeBoolean` matches with `OrdinalIgnoreCase`, so `True` and `False` coerce
correctly, and the count of values genuinely outside the `xsd:boolean` lexical space, the only ones
W603 drops, is **zero**. Commit `3976613a` did both halves of its title, case-insensitive matching
AND W603 reporting. The real thing to watch on first adoption is smaller and different: `hasTitle`
(279 values) and `directApply` (1) are not declared in the client XSD at all, so they are W602
out-of-schema drops.

#### Descriptor shapes, measured 2026-07-29

Do not write these four from a template. Each was measured against the working-tree server datasheet
and the client DataCenter, and one of them is not the shape this plan originally implied.

| Family | Strategy | Files | First-sync expectation |
|---|---|---|---|
| `DecompositionData` | `Monolithic`, `merge: replace` | server `DecompositionData.xml`, one client shard | server 343 rows vs client 334, so 9 rows are ADDED to the client |
| `ItemMixData` | `Monolithic`, `merge: replace` | server `ItemMixData.xml`, one client shard | server 852 rows vs client 848, so 4 rows are ADDED. Both roots also carry a single `Common` element |
| `EventMatching` | `Monolithic`, **`merge: preserve-required-elements`** | server `EventMatching.xml`, one client shard | `replace` is REFUSED with E683, see below |
| `AchievementList` | **`SourceMapped`**, not `Monolithic` | 7 server regional files, 8 client shards | server-only rows added per shard |

**`EventMatching` cannot use `replace`, and this is now a hard error rather than silent corruption.**
The client shard `EventMatching/EventMatching-00000.xml` carries a `DailyCheckEvent` root child that
the server `EventMatching.xml` does not contain at all. A replace rebuilds the client file from the
server projection, drops the required element, and writes XSD-invalid output. DSL `f3be560c` added
**E683**, which refuses to plan that entity under `replace`, and added the `preserve-required-elements`
merge mode as the remedy: a replace in every other respect, except that an XSD-required root child
the projection does not supply is carried over from the existing client file and re-sorted into the
schema's declared order. It is idempotent and it grafts nothing when the client file does not exist.

**`AchievementList` is a shard family, not a monolith.** The client folder holds 8 shards and the
server ships 7 regional files. The mapping is deterministic, verified by row count and id range:

| Server file | Client shard | Rows |
|---|---|---|
| `AchievementList.xml` | `AchievementList-00001.xml` | 1734 |
| `AchievementList_CN.xml` | `AchievementList-00002.xml` | 0 |
| `AchievementList_JP.xml` | `AchievementList-00003.xml` | 48 |
| `AchievementList_KR.xml` | `AchievementList-00004.xml` | 2 |
| `AchievementList_NAEU.xml` | `AchievementList-00005.xml` | 135 |
| `AchievementList_RUS.xml` | `AchievementList-00006.xml` | 13 |
| `AchievementList_TW.xml` | `AchievementList-00007.xml` | 0 |

Shard `AchievementList-00000.xml` holds a single `CategoryInfo` element and no `Achievement` rows. It
has no counterpart inside `AchievementList.xml` and must be EXCLUDED from `source_mapping`, or the
sync will overwrite publisher-side category curation with achievement rows. This is the same
descriptor shape as the existing `StrSheet_Item` entry, so copy that one rather than the monolithic
entries.

The DSL entity behind it (`achievements`) is itself regional-aware, over the full 19-suffix set. All
three achievements C3 touches (9002, 9009, 9011) live in the base `AchievementList.xml`, so the three
deletes resolve without naming a region.

### Phase B: flatten the mechanic families (migrate to 94101)

| Step | Change | Ops |
|---|---|---|
| B1 | `generate_enchant_materials.py`: replace the `94100 + rank` arithmetic with the constant 94101 and delete `FEEDSTOCK_BASE_ID` so it cannot be reintroduced. Regenerate `specs/patches/002/04-enchant-materials.yaml` | 1,656 refs collapse; `05-enchant-item-links.yaml` regenerates byte-identical |
| B2 | New spec `002/34-feedstock-flatten-enchant-decomposition.yaml`, entity `enchantDatas`: all 304 `EnchantDecomposition` rows repointed to 94101, `resultItemAmount` untouched. `update` CAN target `decompositions` alone and leaves sibling collections untouched, and unlike create/upsert it does not require the three root attributes. **`decompositions` is upsert-by-key, NOT clear-and-replace**: restating all 304 rows works, but a row count after apply does not prove the repoint. Verify by asserting no row still carries a `resultItemTemplateId` outside 94101 | 1 op |
| B3 | New spec `002/35-feedstock-flatten-decomposition.yaml`, entity `decompositions`: bring rows 206861 to 206868 under spec control and rebuild them as the six-row grade-scaled ladder decided below | 6 ops |
| B4 | `tools/gear-infusion/generate_infusion.py`: emit one decomposition id per (slot group x rareGrade) instead of per slot, and set `decompositionId` per item from grade as well as slot. Regenerate `002/06-gear-infusion-items.yaml`. **HARD PREREQUISITE: B3.** See below | 900 items retargeted |

**B2: author `combatItemType` in UPPER_SNAKE. The value list this project has been reading was
fictional.** The `enchant-data.mdx` page listed PascalCase members (`EquipWeapon`, `EquipArmorBody`,
`EquipArmorHand`, `EquipArmorShoes`, ...) that the parser has never accepted. DSL `09192855` replaced
the list with the real enum member names. The four the 304 decomposition rows use are:

| Slot | Value |
|---|---|
| weapon | `EQUIP_WEAPON` |
| body | `EQUIP_ARMOR_BODY` |
| arm | `EQUIP_ARMOR_ARM` |
| leg | `EQUIP_ARMOR_LEG` |

Matching is case-insensitive but the underscores are required, and a value outside the list is
rejected with an invalid-enum error naming the collection it appeared in. There is no
`EQUIP_ARMOR_HAND` and no `EQUIP_ARMOR_SHOES`: those were inventions of the old doc. The same commit
confirmed the two semantics B2 depends on, so both statements above stand as written: `decompositions`
merges by `(combatItemType, rank, rareGrade)`, and `update` requires none of the three root
attributes. It also established that an empty list does not clear a collection, so `decompositions: []`
would be a silent no-op rather than a wipe.

B3 and B4 exist because **the current fodder yield contradicts R15**: it pays 48 (weapon and body)
or 24 (arm and leg) regardless of whether the piece is uncommon, rare or superior. R15 says grade
scales quantity. Rows 206863 to 206868 are dead today, referenced by nothing.

B3 also closes a reproducibility defect: rows 206861 to 206868 were committed directly into the
server datasheet by hand (`2c0477c7`) and are reproducible by no spec. That is the same failure
class as the `StrSheet_NpcLoc` loss on 2026-07-28.

#### B1 also repoints the Relic materials. RULED, not a note

The generator's rank domain is **1 to 22** (`RANKS_BY_LEVEL_RANGE` unions to that), so
`94100 + rank` emits **94101 to 94122**, not just the feedstock tiers. Replacing it with a constant
therefore moves more than feedstock:

| Currently pointing at | Spec rows moved | Distinct items affected |
|---|---|---|
| 94113 to 94118 (Relic Fragment and Shard) | 324 | **713** whole corpus, **575** in base `ItemTemplate.xml` |
| 94119 to 94122 (no `ItemTemplate` row exists) | 216 | 0, unreachable |

The 713 breaks down as weapon 354, body 205, arm 77, leg 77. An earlier figure of 559 in this
plan was the weapon-plus-chest subtotal and dropped gloves and boots. **559 was wrong; use 713.**

**RULED: let it collapse. All reachable enchanting consumes 94101.** Reasons, in order:

1. It is the framework position. Feedstock is one untiered commodity and consumption scales by
   band through AMOUNT (`04 §2c`), not through item identity.
2. The Relic usage is an artifact of `94100 + rank`, never a design. It currently makes 713
   endgame items enchant with a **bound** (`tradable=false`, `generalMaterial`) material, which
   sits badly with locked invariant 3, market is the catch-up.
3. It incidentally kills the 216 dangling references to items that do not exist.

**The "split economy" risk was investigated and does not exist.** 42 vanilla `ItemEnchant`
records (ids 21 to 62, 141 rows) do consume the Relic items and the generator does not touch them,
but **zero live `ItemTemplate` rows link to any of those 42 records**, checked per record across
every regional item file. Every one of the 713 items reaches the Relics through a SPEC record. What
survives is dormant data, not a second live economy. One residual the corpus cannot settle: whether
the server falls back to a vanilla record when `linkMaterialEnchantId` is unset. That is a code
question, not a data one.

**This is settled, not open.** Ruling R15 and R18 already fixed one flat feedstock as the design;
the only thing this section adds is the measured fact that the collapse also catches ranks 13 to 18,
which are all `level: 58..65` gear. Re-confirmed by the user on 2026-07-28 after external review
questioned it. Do not reopen it: any future chase-tier differentiation ships as a separate named
material per `04 §4e`, never by restoring the `94100 + rank` arithmetic.

**Quantity ladders are balance work, not a find-and-replace.** Every family carries tier-specific
amounts (`EnchantData` 4 to 48, `MaterialEnchantData` 4 and 12, `ItemConversion` 120). Flattening
the id makes those numbers mean something different, so re-derive them from framework `04 §2c`
(consumption by band) and `§4e` (yield by grade) rather than inheriting them by accident. Scope
this as its own reviewed step inside B, not as a side effect.

#### B3 and B4: the decided fodder dismantle yield

**Measured starting point.** The vanilla gear ladder (family A) is CONSTANT across every paying
rank, and ranks 8 to 16 pay nothing at all:

| Slot | common | uncommon | rare | superior |
|---|---|---|---|---|
| weapon | 4 | 8 | 24 | 48 |
| body | 3 | 6 | 18 | 36 |
| arm, leg | 2 | 4 | 12 | 24 |

Grade ratio 1 : 2 : 6 : 12. The infusion fodder today pays **48 and 24 flat with grade ignored**,
which is the vanilla SUPERIOR row applied to all grades, with body lumped in at the weapon rate (48
where vanilla body pays 36). All 900 fodder items sit at rank 16 in three grades, evenly split:
249 uncommon / 249 rare / 249 superior on `206861` (weapon and body) and 51 / 51 / 51 on `206862`
(arm and leg).

**DECIDED 2026-07-28 (user ruling): rare-anchored ladder, keeping the two existing slot groups.**

| Decomposition group | uncommon | rare | superior |
|---|---|---|---|
| weapon + body | 16 | 48 | 96 |
| arm + leg | 8 | 24 | 48 |

Six `Decomposition` rows replace the current two. Uses the vanilla 1 : 3 : 6 shape across the three
grades that exist, anchored so **rare** keeps today's value.

**Why rare-anchored and not superior-anchored.** Phase C already deletes roughly 2,086 direct
feedstock drop rows, which is a large supply contraction on its own. Anchoring on superior (8 / 24 /
48 and 4 / 12 / 24) would cut mean fodder output a further 44 percent on top of that, so if
enchanting then felt starved there would be no way to tell which change caused it. The rare anchor
holds mean fodder output roughly flat (up about 11 percent) while introducing the grade axis, which
leaves the drop removal as the SINGLE supply variable in this wave and keeps the next tuning pass
interpretable.

Sanity check against `04 §2c` (strawman: 10 to 30 feedstock per attempt at L1-37, 50 to 150 at the
+9 to +12 endgame step): one superior weapon fodder covers roughly three to nine leveling attempts,
or most of one endgame attempt.

**B4 generator change.** `tools/gear-infusion/generate_infusion.py:367` currently derives the id
from slot alone (`get_decomposition_id(combat_item_type)`, `DECOMP_ID_BASE = 206861` at `:54`). It
must derive from **slot group AND `rareGrade`**, emitting one of six ids per item. The move is
small: `:488` computes `decomposition_id` OUTSIDE the grade loop that starts at `:490`, so the fix
is to push the call inside the loop and pass `grade["id"]`. `GRADES` at `:42` is exactly
`[1 Uncommon, 2 Rare, 3 Superior]`.

Reuse the dead ids `206863` to `206868` for the four new combinations rather than allocating new
ones: they are already resident and referenced by nothing (zero of 25,853 items).

**B3 IS A HARD PREREQUISITE OF B4, and the ordering is not automatic.** Those six ids are not empty
today, they currently output the OLD tier items:

| id | current output |
|---|---|
| 206863, 206864 | 94102 |
| 206865, 206866 | 94103 |
| 206867, 206868 | 94104 |

B4 wires 900 fodder items to them at exactly the moment everything else collapses to 94101. Worse,
`002/06-gear-infusion-items.yaml` sorts BEFORE `002/35` in apply order, so within a single apply the
items are repointed before the rows are rewritten. Author B3's six rows and B4's item mapping in the
same change, and verify after apply that no fodder item points at a row still emitting 94102, 94103
or 94104.

**PROBE-F3 is resolved for fodder without running it.** Family A pays `resultItemAmount="0"` at
every rank 8 to 16, and all fodder is rank 16, so the two dismantle systems cannot collide on these
items. Precedence only becomes a live question if fodder is ever authored at rank 7 or below.

**The content-tier axis stays unused.** `04 §4e` permits content tier to scale yield as well
(higher tiers yield more, never a different kind), but all 900 fodder items are a single content
tier (rank 16, level 1), so there is nothing to scale against yet.

### Phase C: delete the faucet families

The framework position is unambiguous: `04 §5e` says there is no direct content drop of feedstock,
and R13 restates it. Migrating these rows to 94101 would preserve exactly the faucet the framework
forbids, only with one item instead of twelve.

**C1, our own zones (patch 002 surface).** Removes 299 rows across 11 zone files, written by nobody
rather than deleted. Roughly half of every standard Island of Dawn trash kill currently drops 5
feedstock; that stops.

An earlier draft said to "strip the tier mapping from `fill_zone_loot.py` and
`generate_iod_loot.py`". That instruction has no referent in the first tool and understates the
second. The executable change list:

| File | What is actually there | Change |
|---|---|---|
| `tools/iod-loot/generate_iod_loot.py` | **No tier mapping exists.** It emits `$extends: FeedstockBag` at `:325-326` with only `PROB` and `QTY`; the item id is hardcoded in the package | Drop `"FeedstockBag"` from `REFORGED_DEFS` at `:289` AND drop the two emit lines at `:325-326` |
| `packages/reforged-loot-bags/index.yml` | `FeedstockBag` declared at `:35-45` with `templateId: 94101` hardcoded at `:41`, exported at `:115` | Remove the definition and its export |
| `tools/zone-loot/fill_zone_loot.py` | `TIER_FEEDSTOCK` maps ZONE TIER, not item rank, and `feedstock_id` is a required positional threaded through 3 functions and 6 call sites | Deleting the dict alone breaks all six call sites. Remove the parameter through the whole chain |

Blast radius on the generated specs is small: 7 of the 10 zone loot specs already emit 94101, and
only 6 `templateId` rows emit 94102.

**C2, the remaining 85 zones (~1,790 rows, ~1,470 ops).** These arrived in a single 2025-02 operator
commit, "Incluido loot v71". Vanilla v92 had **zero** feedstock in field-zone loot tables, so
removing them moves the server toward its vanilla baseline rather than away from it.

**C2 DOES NOT SHIP IN WAVE 1. Decided 2026-07-28 by the gate condition below, no probe needed.**
The DSL docs settle it: bag collections are clear-and-replace, and "the DSL does not support
granular add/remove for bags or items". Removing one `ItemBag` means restating that
`Compensation` record's ENTIRE bag list, so C2 would make us the author of roughly 1,469 loot
records across 85 zone tables we have never touched, inside a patch that is meant to close.

C2 becomes its own work item with its own generator (read the current table, re-emit it minus the
feedstock bags). The removal is still right, it is just not wave 1 work.

**Precondition to carry into C2: `ItemMix 216862` breaks when its last 94105 source goes.** That
recipe consumes `94204 x200` + **`94105 x500`** + `98505 x50`. Item 94105's grant paths are
achievement 9009, `BuyList` 2933, the medal exchange on item 91966, npc drops in zones 711 and 750,
a `Gacha_Tool.xml` box (244757, grants 25) and two `ItemConversion` seeds. **C3 deletes four of
those and C2 deletes the zone drops**, which together leave the recipe uncompletable. Note the
attribution carefully: this is a C2-plus-C3 interaction, not a C2-only one, and the last two paths
were found by corpus sweep because `item_sources` does not scan `Gacha_Tool` or `ItemConversion`
grants. Decide the recipe's fate when C2 is scoped, not by accident.

**C3, the small faucets.** One spec, `002/38-feedstock-faucet-removal.yaml`:

| Family | Rows | Why delete |
|---|---|---|
| `EventMatching` (Vanguard) | 164 | **UNBLOCKED 2026-07-29, back in wave 1.** Both legs were fixed the same day the audit filed them. See below |
| `Gacha`, all **8** files | 307 on tiers 2 to 12 | Only 8 boxes are reachable. Migrating creates 307 new 94101 faucet rows for nothing. **The datasheet holds 8 Gacha files, not 7**: `Gacha.xml` plus `_JP`, `_KR`, `_NAEU`, `_RUS`, `_THA`, `_TW`, plus **`Gacha_Tool.xml`**, which grants 25x 94105 from box 244757 and would otherwise survive this step |
| `ItemConversion`, **all 6 files holding rows** | **80 of 80** | The entity was `SingleFile("ItemConversion.xml")` and is now `RegionalVariants` (DSL `36ceaa0a`), so `update` and `delete` search every variant and a row is addressed by `itemTemplateId` wherever it lives. Distribution re-measured 2026-07-29: base 40, `_JP` 2, `_KR` 1, `_NAEU` 27, `_RUS` 8, `_Tool` 2. Nothing is deferred |
| `AchievementList` 9002 / 9009 / 9011 | 3 | Large amounts (180 / 60 / 50), achievement-granted feedstock is a direct faucet |
| `BuyList` 2933 + `ItemMedalExchange` (vanilla Feedstock Exchange Shop) | 2 | Doubly dead: no NPC opens it and its currency 91966 has zero sources anywhere |
| `StackAttendanceEvent` | 4 | Now authorable, see below. Inert content, so this is hygiene rather than economy |

**Watch the collisions.** 10 containers hold two or more different tiers as separate weighted
entries (7 in `Gacha`, 3 in `ItemConversion`). Where a row is deleted rather than merged this does
not arise, but any container that keeps a 94101 row must have its probabilities **summed, not
dropped**. Note also that duplicate item ids inside a reward pool are already legal and deliberate
(47 `Gacha` containers do it), so no tooling in this wave may "dedup by item id".

**`EventMatching` was blocked on BOTH legs and BOTH are now fixed (verified 2026-07-29).** The
2026-07-28 capability audit filed the two defects below and the DSL team delivered both the same day.
The 164 live Vanguard feedstock rows are therefore in wave 1, and the "one item in this wave that does
not get resolved" caveat is withdrawn.

| Was | Fixed by | Now |
|---|---|---|
| **Authoring.** `EventCommandBase` resolved the target group by comparing `isSpecialCompensation` against the PascalCase literals `"True"` / `"False"` ordinally, while the shipped file writes them lowercase. No group ever matched, so every command reported **E500 "could not be applied"**. The entity had never been exercised against the shipped file: its own fixtures hardcoded the PascalCase form | `da47c4e9`, which also added a shipped-file test suite carrying the real 9,975-line `EventMatching.xml` | Commands resolve against the shipped file |
| **Sync.** The client XSD requires a `DailyCheckEvent` element the server file does not contain, so a monolithic replace would write XSD-invalid output | `f3be560c` | `merge: preserve-required-elements`, and `replace` on such an entity is now refused with E683 rather than silently corrupting. See Phase A |

**The `group` mapping was documented BACKWARDS, and this is the trap in the fix.** Authoring the
wrong group does not error in a way that names the mistake: the two pools mirror each other by
`categoryId`, so naming the wrong one either fails to find the event or edits the copy you did not
mean. The corrected mapping:

| DSL `group` | XML | Which pool |
|---|---|---|
| `priority` | `isSpecialCompensation="true"` | the RICHER reward set |
| `secondary` | `isSpecialCompensation="false"` | the reduced reward set |

An event is addressed by `eventId` AND `group` together and the two groups are searched
independently. The feedstock rows must be removed from BOTH copies of each affected category, not
one.

Two more semantics that shape the ops: `rewards` is **clear-and-replace**, so a feedstock row is
removed by restating the rest of that event's list without it, and `rewards: []` empties the list
entirely. `mailSender`, `mailTitle` and `mailBody` sit on the container rather than the rows and each
resolves independently, so restating an event's rewards does not rewrite its mail strings.

The other eight `eventMatching*` keys stay mapped to `None`. All nine sections write the same file and
client sync is file-scoped, so mapping `eventMatchingEvents` to the descriptor carries the whole file
and this wave is covered. Still no hand edit to the client shard: that is the anti-pattern that cost
this project the `StrSheet_NpcLoc` regeneration.

**`StackAttendanceEvent` is now in scope.** The dsl-request filed with this plan was delivered the
same day (DSL commit `ef6f3900`), so the family is authorable. Three things to know before writing
the op: the entity key is **`stackAttendanceEvent`** and it is a KEYLESS singleton, so it takes no
`create` / `update` / `upsert` wrapper and no `changes` block, exactly like `fieldEventConfig`;
`sampleEvents` is a LIST section, which means **restate the whole section** because entries are
matched positionally and none of `SampleEvent` or `Reward` carries an id; and the section is
server-only, since the client `StackAttendanceEvent` folder keeps UI chrome and has no
`SampleEventList` at all.

Keep the expectation honest: the sample event is QA scaffolding loadable only by `@load_saevent`
and its window closed on 2023-06-16, so removing its 4 feedstock rows changes nothing a player can
reach. It is included because it is cheap and it satisfies the corpus-wide ruling, not because it
affects the economy.

**C4, the classic carve-out.** R13 contradicts itself on 4 rows: it says remove direct feedstock
drops AND leave the classic v31 layer byte-untouched, but the v31 layer itself drops
`강화석 1단계` = 94101 on Vekas (13,1001) and Kugai (13,1004). **Ruling for this wave: the four
classic rows STAY**, as a named exception, because "the classic layer is untouched" is the older and
more load-bearing commitment and four rows on two named bosses is not an economy. Record it in the
divergence log as a policy carve-out rather than letting the contradiction sit unresolved.

### Phase D: retire the tier items (identity, not existence)

One spec, `002/37-feedstock-retire-tier-items.yaml`.

**Items 94102 to 94112 keep their `ItemTemplate` rows.** Deleting them would create roughly 4,000
dangling item references, and `WorldServer.exe` carries explicit id-validation strings for `Gacha`
and `LimitedGacha`. The shipping corpus maintains perfect referential integrity on item ids, the
only exception being the 4 ids our own spec introduced. The failure mode for getting this wrong is
the silent access violation during startup validation with no file named, which this project has
already lost days to. Tidiness is not worth that.

| Change | Entity | Ops |
|---|---|---|
| Rewrite 94101 name and tooltip: drop "Tier 1", drop the "right-click to combine 6" instruction, drop the level 1 to 30 band claim | `itemStrings` | **1**, base only. See the `Local` correction below |
| Rewrite 94102 to 94112 strings to say what they now are | `itemStrings` | **11**, base only |
| Delete the 10 `ItemMix` ladder records **and clear the 12 `itemMixId` back-pointers**, both now authorable | `itemMixes` delete, `items` update with `clear` | 10 + 12 = **22** |
| Rename the package constant `TIER_1_FEEDSTOCK_94101` to `FEEDSTOCK_94101` | `packages/item-ids/`, regenerated. **Read the warning below first** | n/a |
| Update the ~900 infusion fodder tooltips that name Feedstock | regenerate `002/06-gear-infusion-items.yaml` | with B4 |

**CORRECTION 2026-07-29: there is no `Local` leg. The string ops are base-file only.** An earlier
draft of this table doubled every `itemStrings` op to cover `StrSheet_ItemLocal.xml`. That file
cannot be written by `itemStrings` and should not be. Three reasons, all measured:

1. **It is not addressable.** The `itemStrings` entity resolves `StrSheet_Item.xml` plus suffixed
   variants (`_NAEU`, `_KR`, `_Tool`, ...). `StrSheet_ItemLocal.xml` carries no underscore and
   matches no suffix, so no operation reaches it.
2. **It is not in the sync map.** `config/sync-config.yaml`'s `StrSheet_Item` `source_mapping` lists
   the base file and eight regional variants. `StrSheet_ItemLocal.xml` is absent, so nothing in it
   reaches the client regardless.
3. **It is the wrong language.** Its 109,365 rows are Traditional Chinese. Id 94101 reads
   `強化石 1階段` there against `Tier 1 Feedstock` in the base file. Rewriting it would put English
   copy into a CJK sheet.

All 22 ids from 94101 to 94118 have a row in `StrSheet_Item.xml`, which is the sheet the English
server and client read. That is the only one this wave touches. This is a plan defect, not a DSL gap,
so no request is filed.

**The `ItemMixData` ladder must be DELETED, not migrated.** Its ten records read `94101 x6 -> 94102`
and so on. Flatten the ids and every rung becomes `94101 xN -> 94101`, a recipe that consumes N and
returns 1: a machine that destroys player items. Two of the back-pointers are already dangling
today, and the ladder is already severed at the tier 4 to 5 rung.

**The 12 back-pointer clears are now authorable. UNBLOCKED 2026-07-29, ship them with the deletes.**
The request filed with this plan was delivered as DSL `da5f2567`, which added a `clear` facility to
`items`:

```yaml
items:
  update:
    - id: 94101
      changes:
        clear: [itemMixId]
```

That removes the attribute from the `<Item>` element entirely, which is the canonical unset form:
111,569 of 112,392 shipped items carry no `itemMixId` at all and not one carries `itemMixId="0"`. The
original analysis stands and is what the fix was built on, so it is kept here as the reason `0` was
never shipped: `itemMixId: null` or an omitted key emits no command, and `0` would have been a
zero-corpus shape, the exact failure class behind the semicolon class lists and the `진행퀘스트`
`0,0` sentinel.

Four behaviours worth knowing before authoring the 12 ops: clearing an attribute that is already
absent is a **W500 no-op**, so the spec converges on re-apply; an attribute name the schema does not
declare is **refused**, so a typo fails the op instead of silently clearing nothing; setting and
clearing the same attribute in one `changes` block clears it; and `clear` works the same way under
`updateWhere`.

**Order the ops so the deletes and the clears land together.** Leaving the ladder live is worse than
a dangling pointer, since after the flattening a player could feed 6 feedstock into a rung and
receive one retired, useless tier item. Now that both halves are expressible there is no reason to
split them: author the 10 `itemMixes` deletes and the 12 `items` clears in the same spec.

**The acceptance checkpoint is restored to the strong form.** Wave 1 now proves BOTH that the tier-up
conversion no longer happens AND that the right-click affordance is gone. The earlier softening
("test the outcome, not the button") no longer applies.

**Two live recipes must not be broken:** `ItemMix 534` (`101374 x1 -> 94108 x5`) and `ItemMix
216862` (`94204 x200` + `94105 x500` + `98505 x50` -> `216872 x1`). The second hard-depends on tier
5 continuing to exist, which is another reason the item rows stay.

**"Regenerate `packages/item-ids/`" is a footgun as written.** `write_shards()` in
`tools/item-ids/gen_item_ids.py` UNLINKS every `*.yml` in the package before writing, and it names
only the ids passed via `--ids` or `--from-spec`. A naive regeneration would delete all seven
shards and every unrelated constant in them. The constant name is also derived from the server
`StrSheet_Item`, so the rename only materialises after the strings are applied. Correct order:

1. apply (the D-phase string rewrite lands),
2. regenerate `packages/item-ids/` with the full id set, never a partial one,
3. regenerate `002/17-iod-loot.yaml` so it imports the new constant name,
4. re-apply.

Blast radius of the rename itself is small and self-healing: one spec (`002/17`) and its two
references, which are the Vekas and Kugai carve-out rows from C4.

**Reverse conversion ladder: conditional, not planned.** If the planet database turns out to hold
player stock of 94102 to 94112, the cheapest migration is to rewrite the `ItemMix` ladder to convert
each tier INTO 94101, which needs no GM tooling and no DB surgery. That is a decision for after the
stock question is answered (section 7). Note the honest reverse rates are derivable only for tiers 2
to 4 (6, 36 and 216 respectively); the 4-to-5 break means tiers 5 to 12 have no derivable rate and
any number chosen there is a design call.

### Phase E: the token spine

| Step | Spec | Content |
|---|---|---|
| E1 | `002/39-iod-progression-token.yaml` | Item **95217**, the next slot in the project's own reserved token block 95214 to 95313. `boundType: Loot`, `tradable: false`, `NO_COMBAT`, high `maxStack`. Copy the `definitions:` plus `items: upsert:` shape from `002/14-dungeon-tokens.yaml`, NOT its MEDAL_USEABLE wiring, which R11 rejects |
| E2 | **AMEND `002/28`, `002/29`, `002/30`, plus one new spec `002/40`** | The XP pass and the token rows, together. NOT one new spec: see the ownership rule below |

**Author the strings in a TOP-LEVEL `itemStrings:` block, not the inline `strings:` form.**
`migrate.py` matches `ENTITY_KEY_PATTERN` anchored at column 0, so an indented inline block does not
register the `itemStrings` key. Patch 002 is covered today only by accident, because two unrelated
specs carry top-level blocks. A patch whose only string authoring was inline would ship a nameless
item to the client.

**E2, the XP pass (RV-07).** Cap each live zone quest at 25 percent of the **median** story quest XP
of its level bracket. Measured against that baseline, **29 of the 35 live zone quests are currently
over the cap**, so this is a zone-wide reduction, not a touch-up. Two measurement distortions to
correct for when computing the brackets: the 1-2 bracket median is inflated by the twelve
class-training missions at 2,100 XP each, of which a character completes exactly ONE; and the 5-6
bracket median is deflated by quests 1382 and 1383 at 100 XP, which are a paired gathering-intro
variant rather than a real story payout.

**Two caveats on the cap, both understated in an earlier draft of this plan.**

1. **The 25 percent RATIO is a strawman, not a settled ruling.** `IOD-BACKLOG.md` RV-07 tags it
   `_(strawman ratio; framework 99 #02 tuning entry)_`, an open framework question. Ruling D4
   settled the BASELINE (median rather than peak), which was genuinely ambiguous; it did not
   ratify the ratio. Since the ratio drives a cut on 29 of 35 quests, treat it as tuning and expect
   to revisit it, rather than as a fixed constraint the wave must satisfy.
2. **Compensation is the token, and only the token. RULED 2026-07-28.** RV-07's gate lists "gold up
   modestly, RV-01 tokens, small power items"; this wave pays the token alone, and the vendor that
   spends it lands in wave 2. That is deliberate scope control, not an accepted shortfall: the
   exchange is completed by wave 2, not abandoned. Do not quietly add gold or power items to E2 to
   "close" it, and do not describe reward parity as satisfied until the vendor ships.

**E2, the token rows (RV-03).** 35 live zone quests, of which 3 are repeatables that belong to
RV-08. Threading difficulty splits by bag mode:

| Bag mode | Quests | How |
|---|---|---|
| already `allpay` | 12 | one extra row |
| no `itemBag` | 15 | add `itemBag: "allpay"` plus one row |
| `class` (the 8 gear carriers) | 1319, 1322, 1324, 1325, 1326, 1330, 1332, 1333 | **12 duplicate rows, one per class** |

The 12-row form is not a workaround, it is the only idiom the corpus uses: there are zero
occurrences in v92 server, v92 client or v31 of a classless row inside a `class` bag, while 62 of
94 v92 class bags already pay a shared item by duplicating it per class. The in-file precedent is
quest **1310, in `QuestCompensationData_13.xml`**, which already runs 24 rows out of one class bag.
Adds 96 rows across 8 quests; 13 corpus bags already sit at exactly 24 rows and the ceiling is 104.

`questCompensations: upsert` is **replace-all**: every op must restate the complete compensation
block, including every exp, gold, itemBag value and every row that should survive.

#### E2 ownership rule: amend the owning spec, never layer a spec 40 over it

**This would have silently destroyed the trim wave.** `discover_specs` sorts on the relative path
string, so a spec numbered `40-` is the LAST writer for every quest it names, and
`questCompensations: upsert` is replace-all. Nine of the eleven gear-relevant quests are already
authored inside patch 002:

| Quest | Authoritative owner today | What a spec 40 would have overwritten |
|---|---|---|
| 1319, 1322, 1324, 1325 | `002/28-iod-reward-cadence.yaml` | the whole level-4 set and weapon |
| 1332, 1333 | `002/29-iod-expedition-set-distribution.yaml` | First Expedition body and weapon |
| 1347 | `002/30-iod-remove-mid-tier-gear.yaml` | the deliberate strip |
| 1348, 1349 | `002/29` | the deliberate strips |
| **1326, 1330** | **`001/04` only. Nothing in patch 002 touches their compensations** | see below |

The project's own precedent is explicit (`TRACKER.md`, Trim 5): amend the owning spec "so each
quest keeps one authoritative statement in the patch", which is legitimate while 002 is open
because specs replay wholesale from the committed baseline.

So E2 is authored as:

1. **Amend `002/28`** for 1319, 1322, 1324, 1325: add the token rows and the new exp values to the
   existing ops.
2. **Amend `002/29`** for 1332, 1333, 1348, 1349, and **`002/30`** for 1347, the same way.
3. **New spec `002/40`** for the remaining live zone quests that patch 002 does not already own.
4. **1326 and 1330 need special care.** Their rows exist only in the patch 001 baseline, so a
   patch-002 statement for them must reproduce their twelve class rows each from `001/04`, or the
   level-7 feet (15021 / 15024 / 15027) and hands (15020 / 15023 / 15026) are silently stripped.
   `002/29` says so in its own header at line 92.

**The failure mode is silent**: the apply succeeds, op counts look right, and only a parser-based
per-quest diff against committed HEAD catches it. That diff is mandatory for this step.

**Do not author from the stale ladder tables.** `TRACKER.md` line 397 and the header of
`002/30-iod-remove-mid-tier-gear.yaml` (two lines) still read "1348 body / 1349 weapon", superseded
by the 2026-07-27 move to 1332 and 1333. Corrected 2026-07-28; if you are reading an older copy,
the applied truth is 1326 feet, 1330 hands, **1332 body, 1333 weapon**.

### Phase F: NOT IN THIS WAVE. The existing token shops work as designed

Recorded here because a mid-planning claim that the three token shops were broken was **wrong** and
should not be rediscovered.

Menus 9999008 (Kugai), 9999004 (Bastion of Lok) and 9999006 (Sinestral Manor) have no NPC bound to
them, and that is correct: they are **item-opened `MEDAL_USEABLE` right-click shops**.
`VillagerMenuItem` binds the ITEM to the menu, not an NPC to the menu. Spec `002/20` sets
`combatItemType: MEDAL_USEABLE` and `itemUseCount: 1`, the item tooltip reads "[Right-click] to open
the Kugai Exchange", and `packages/dungeon-tokens/index.yml` documents the chain in its header. The
chain was established deliberately by commit `a57c65b`. A `reverse_lookup_shop_npcs` miss is the
EXPECTED result for this shop type, not evidence of a broken shop.

Converting them to physical NPC vendors is ruling R11 and belongs to **RV-05**. It is a design
change, not a defect, and folding it into this wave would enlarge patch 002 for no correctness
reason.

The framework does sanction a token shop selling feedstock (`03 §3b-i` spend catalogue, `03 §3c`
power-spend registry), so the Kugai shop's 94101 row stays regardless.

**RESOLVED 2026-07-28 (user ruling): the token ships as ACCUMULATING CURRENCY, with the vendor in
wave 2.** RV-01 mints the early-progression token and RV-03 pays it out; **RV-02, the vendor that
spends it, is deliberately not in this wave**, so for the duration of wave 1 the token has no sink.

This is intentional and it buys something concrete: the E2 XP pass is what determines token income,
so pricing a catalogue before that lands would mean guessing the income rate and then guessing
prices against the guess. Shipping the currency first produces measured accumulation data, and
wave 2 prices RV-02 against it.

Two consequences to hold:
- **Say it in the item tooltip.** The token's tooltip must tell the player it is saved for a vendor
  that is not open yet, or it reads as a bug. Author it in the same `itemStrings` block as the name.
- **The live-test checkpoint is accumulation, not spending.** Confirm the token is granted, stacks,
  cannot be traded, and survives relog. There is nothing to buy and that is the expected state.

### Phase G: apply, gate, validate, close

1. `python reforged/tools/migrate/migrate.py --patch 002`. Whole patch only. `--no-narrow` remains
   required for this patch because it adds new `Quest` and `QuestDialog` shards.
2. Both standing gates, exit 0 required: `dungeon_audit.py --dungeons 9037` and
   `audit_class_gates.py --zones 13,64,213,436`.
3. **REFERENTIAL INTEGRITY GATE, new and mandatory for this wave.** `check_references` over the
   families this wave rewrites, plus a targeted sweep proving every one of the repointed item
   references resolves to an existing `ItemTemplate` row. Neither standing gate proves this, and
   Phase D's entire argument for keeping the retired tier rows resident is the silent
   access-violation-at-startup failure mode that a dangling item id produces. A wave that repoints
   thousands of item references without a referential gate contradicts its own reasoning.
4. Advisory review: `audit_quest_design.py --zones 13,64,213,313,364 --since HEAD`.
5. Regression diffs, parser-based never regex: the compensation block contains self-closing
   children, so a lazy terminator truncates it. This project has already been burned by that.
   **Per-quest compensation diff against committed HEAD is mandatory**, because the E2 ownership
   hazard fails silently and shows correct op counts.
6. **Divergence log rows, before the wave is called done.** Doctrine rule 6 and RV-07's own gate
   both require them, and an earlier draft of this plan scheduled a row only for the C4 carve-out.
   Rows needed: the XP reduction on every changed zone quest (category policy, R10 and R20), the
   token threading (authored content), the token's `boundType: Loot` divergence from the three
   existing project tokens (R21), the fodder yield ladder change, and the feedstock faucet removals.
7. Deploy, then USER live validation. Server restart is manual.

## 4. Acceptance checkpoints for live validation

Derived from the change list, not from replaying content:

- Enchant a piece at a **leveling** tier and at an **endgame** tier: both consume 94101 and nothing
  else, at the expected amounts.
- Dismantle gear at two different `rareGrade` values: both return 94101, in different quantities.
- Dismantle infusion fodder at uncommon, rare and superior: yields are 16 / 48 / 96 on a weapon or
  body piece and 8 / 24 / 48 on an arm or leg piece (this is new
  behaviour; today they are identical).
- Kill Island of Dawn trash: **no** feedstock drops. Kill Vekas or Kugai: the classic drop still
  fires (the C4 carve-out).
- Complete one `allpay` zone quest and one `class`-bag zone quest: the token is paid in both, and
  the class-bag quest still pays the correct class gear.
- Check the quest log reward panel on a class-bag quest: the token appears alongside the gear.
- Right-click Kugai's Crest: the exchange still opens and its 94101 row still sells.
- Confirm the feedstock tier-up conversion is gone: the right-click affordance itself must no longer
  appear on 94101, and no rung of the ladder can be run. Both halves are testable now that the
  `itemMixId` clears ship with the `ItemMix` deletes (updated 2026-07-29).
- Run a Vanguard Request at level 11 or above: **no** tier feedstock in the payout, on both the
  `priority` and `secondary` reward sets of the affected categories (updated 2026-07-29; this was
  previously listed as a known unfixable exception).

## 5. Requests filed with this plan

| Request | File | Status |
|---|---|---|
| `StackAttendanceEvent` has no DSL entity | `docs/dsl-requests/2026-07-28-stackattendanceevent-entity-missing.md` | **DELIVERED** same day, DSL `ef6f3900`. Entity `stackAttendanceEvent` |
| Quest compensation doc states the wrong `maxOccurs` for `Compensation` | `docs/dsl-requests/2026-07-28-quest-compensation-doc-maxoccurs.md` | **DELIVERED** same day, DSL `e9e9e11e`. Also corrected fictional `type` values and reframed `[max N]` across all five compensation pages |
| `lookup` / `batch_lookup` return an opaque error for `entity: "Item"` | `docs/mcp-requests/2026-07-28-item-lookup-opaque-error.md` | open |

Binary in use is now **`1.0.0+98f98032`**, verified against `dsl.exe --version` on 2026-07-29. That
is the current HEAD of the `datasheetlang` repo.

### Capability gaps found by the 2026-07-28 audit: ALL FIVE DELIVERED, verified 2026-07-29

Every gap that changed wave 1 scope is closed. Re-verified by reading the commits and the shipped
docs, not by recall.

| Gap | File | Delivered by | Wave 1 effect |
|---|---|---|---|
| `items` cannot clear `itemMixId`, and `0` is a zero-corpus shape | `2026-07-28-items-itemmixid-clear.md` | `da5f2567` | Phase D ships the 12 clears with the 10 deletes. Acceptance checkpoint restored to the strong form |
| `eventMatchingEvents` group resolver compares casing ordinally, so every command E500s against the shipped file | `2026-07-28-eventmatching-group-casing.md` | `da47c4e9` | **All 164 EventMatching rows back in wave 1.** The fix also corrected a `group` mapping that was documented backwards |
| `itemConversions` is `SingleFile`, reaching 1 of the 6 files that hold rows | `2026-07-28-itemconversion-regional-files.md` | `36ceaa0a` | 80 of 80 rows, nothing deferred |
| `enchant-data.mdx` misstates `decompositions` as clear-and-replace | `2026-07-28-enchantdata-decompositions-doc-semantics.md` | `09192855` | Confirms PROBE-F1. Also exposed that the `combatItemType` value list was fictional, which changes how B2 is authored |
| Sync writes XSD-invalid output when the client XSD requires an element the server lacks | `2026-07-28-sync-required-element-loss.md` | `f3be560c` | `EventMatching` client leg unblocked via `merge: preserve-required-elements`. `replace` on such an entity is now refused with E683 |

The one request still open is the MCP-side `lookup` / `batch_lookup` opaque error above. It blocks no
wave 1 step.

**Everything else the plan needs is supported by the current binary**, confirmed against source
rather than docs: `decompositions` upsert and delete, `itemMixes` delete, `gachaItems`,
`achievements`, `stackAttendanceEvent`, `questCompensations` (including a 24-row class bag with two
templateIds per class, since the same-templateId collapse defect is fixed in the current source),
and `materialEnchants`.

Domain knowledge from the research wave goes to the `datasheet-domain` KB per doctrine rule 9
(three dismantle families, the enchant material selection chain, quest compensation semantics and
the wire format, regional variant loading, `LimitedDrop` and `ItemMixData` shapes).

### Regional file targeting changed under this patch, and the replay was checked (2026-07-29)

Two commits nobody asked for rewrote how operations reach regional variant files. They are in the
binary this wave will apply with, they change the behaviour of specs ALREADY in patch 002, and
neither is mentioned anywhere else in this plan. Read this before the first replay.

**What changed.**

| Change | Commit | Consequence |
|---|---|---|
| The standard regional suffix set went from 8 names to 19 (`_Console_Tool`, `_EU_Tool`, `_ctf`, `_Dummy`, `_cn`, the per-region `_Tool` builds) | `98f98032` | The eleven missing ones held 6,429 `ItemTemplate` rows and 6,451 `StrSheet_Item` rows that NO operation could reach. An update reported "not found", a delete reported success while doing nothing |
| `itemStrings` was `SingleFile` and is now `RegionalVariants` | `388baea0` | 68 percent of item string rows sat in files nothing ever opened. An upsert against one of them forked a SECOND row with the same id into the base file |
| `items` and `itemStrings` now enforce cross-file id uniqueness | `98f98032` | A `create` naming an id that lives in any variant fails with the new **E428** instead of minting a duplicate |

**`--region` is a CLI flag, not a spec key**, and it scopes the whole run. `create` writes to the
named variant; `update` and `delete` ignore it and search the entire file set; `upsert` searches
first and falls back to the region only when the record exists nowhere. Wave 1 needs no create
targeting a regional file, so **`migrate.py` needs no `--region` plumbing** and the batch apply is
unaffected.

**Two measurements prove the patch 002 replay is safe.** Both were run against the working-tree
server datasheet on 2026-07-29, and both must be re-run if this wave is rebased onto a different
baseline.

1. **Zero cross-file duplicate ids exist today**, so no past apply forked a row that E423 or E428
   would now trip over: `ItemTemplate` 112,392 distinct ids across 20 files, `StrSheet_Item` 111,617
   across 20, `Gacha` 5,052 across 8, `ItemConversion` 5,385 across 8. The first two figures match
   the DSL's own corpus measurement exactly.
2. **Every literal id our specs address lives in the base file**: all 2,190 `items` ids and all 1,232
   `itemStrings` ids under `specs/patches/**`. So promoting `itemStrings` to `RegionalVariants` is
   behaviourally neutral for the existing corpus.

**Caveat on measurement 2.** It matched literal `id:` lines only. Seven specs carry variable-valued
ids (`$HIGH_TIER_BODY_IDS` and siblings, concentrated in `002/01-armor-standardize.yaml`) and are not
covered by it. They are `updateWhere` filters over ids that resolve from `packages/item-ids`, which is
generated from the base `StrSheet_Item.xml`, so they are very unlikely to reach a variant. If a replay
ever reports an unexpected `E423` or a changed file outside the base set, that is the first place to
look.

## 6. Probes, all cheap, none blocking Phase A

| # | Question | Blocks |
|---|---|---|
| PROBE-F1 | ~~Does `enchantDatas` update replace all 304 rows?~~ **RESOLVED from source, and the earlier doc-based answer was WRONG.** `update` targets one collection and leaves siblings alone, but `decompositions` is upsert-by-key, not clear-and-replace. The doc line this was first resolved from is itself defective and is now filed. Verify by value, never by row count | nothing |
| PROBE-F2 | ~~Can `eCompensations` remove a single `ItemBag`?~~ **RESOLVED from the docs**: bag collections are clear-and-replace and "the DSL does not support granular add/remove for bags or items". This is what took C2 out of wave 1 | nothing |
| PROBE-F3 | ~~Precedence between dismantle family A and family B~~ **RESOLVED without a probe**: family A pays 0 at every rank 8 to 16 and all fodder is rank 16, so the two cannot collide on these items. Re-open only if fodder is ever authored at rank 7 or below | nothing |
| PROBE-F4 | Does the client render correctly after a first sync of the four newly registered families? Expect a first-adoption rewrite; verify with a real sync and an attribute-level diff | Gate A |

Only PROBE-F4 remains, and it runs as part of Gate A rather than as a separate experiment.

**Watch the `type` value when authoring compensation ops.** The DSL doc's examples used to show
`type: "basic"` and `type: "repeat"`; both were fictional. `normal` is the only value anywhere in
the v92 corpus. The doc was corrected in DSL commit `e9e9e11e`, but anything copied from it before
2026-07-28 carries the wrong value.

## 7. Owned elsewhere

- **Player stock of 94102 to 94112.** Not answerable from datasheets: character inventories, bank,
  broker listings and mail live in the planet database. This is a dev-server operator or Mystel
  Proxy question, and this repo has no DB access path and should not acquire one. The answer decides
  whether the reverse conversion ladder in Phase D is built. Expected answer, pre-release, is zero.
- **Vanguard per-event on/off state.** `spLoadEventMatchingOff` persists it in the planet database,
  so the datasheet cannot tell whether an operator already switched the system off. Does not block
  C3 (deleting the reward rows is correct either way).
- **Achievements 9002 / 9009 / 9011 completability** was not traced to trigger conditions. Does not
  block C3.

## 7b. RESOLVED: the wave ships all at once

**User ruling 2026-07-28: ship as scoped, option 1.** The concern below is recorded because it is
real and because it shapes how the wave is diagnosed afterwards, not because it is unresolved.

Practical consequence to carry into live validation: if levelling feels wrong after this wave, the
cause is not isolable from the seven trim specs it lands on. Diagnose from the acceptance
checkpoints in section 4 (which test each change independently) rather than from overall feel, and
expect the first tuning pass to work from a compound baseline.

The original analysis follows.

Phase B justifies the rare-anchored fodder ladder on the grounds that it "leaves the drop removal
as the SINGLE supply variable, which keeps the next tuning pass interpretable". That argument does
not survive at wave level. As scoped, wave 1 simultaneously ships: an XP cut on 29 of 35 zone
quests, removal of feedstock from roughly half of all Island of Dawn trash kills, a fodder yield
change, and a token with no sink until wave 2. It lands on top of seven trim specs (`002/27` to
`002/33`) that are still unvalidated live, in a zone whose mobs run x10 HP and x60 attack.

If levelling then feels bad, nothing in that list is isolable.

Three honest options:

1. **Ship as scoped**, and accept that the next tuning pass starts from a compound change.
2. **Live-validate the trim wave first**, then ship this wave against a known-good baseline. Costs
   one deploy and restart cycle, and it is the only option that keeps the seven trim specs
   interpretable.
3. **Split the wave**: feedstock work (B, C, D) in one apply, the zone-quest XP and token work (E)
   in a second, so the economy change and the progression change are separable.

**Option 1 adopted.** Options 2 and 3 are recorded only so a future session does not reopen the
question as if it were unexamined.

## 8. Deliberately out of scope

- `QuestCompensationData`: contains zero feedstock. The 3,053 references an earlier pass reported
  are all Relic Fragment and Relic Shard (94113 to 94118), a different item family.
  **Caveat added 2026-07-28:** "out of scope" holds for the QUEST REWARD side only. The B1 ruling
  above does repoint 324 enchant-material rows off those same Relic ids, so the Relic family is not
  untouched by this wave. The two statements are compatible, but do not read this bullet as a
  promise that nothing anywhere moves off 94113 to 94118.
- `LimitedDrop.xml`: the entire file body is commented out and it caps nothing. Worth remembering
  for the opposite reason: if a guaranteed-floor mechanic is ever wanted, this is a vanilla-proven
  one that is currently switched off.
- `ItemDecompositionData` (the Hammer): outputs no feedstock.
- Deleting the retired item rows. See Phase D.
- RV-02, RV-04, RV-05 catalogues and the remaining backlog waves.
