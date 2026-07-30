# IoD Reward Vector Wave 1: token spine and feedstock flattening

_Planned 2026-07-28. Implementation plan for the first wave of `IOD-BACKLOG.md`, folded into the
OPEN patch 002. Nothing in this plan has been applied. The backlog holds the design rulings and the
work-item catalogue; this document holds the build order, the file-level change list, the gates and
the open dependencies._

Scope: backlog items **RV-01** (early-progression token item), **RV-03** (token threading, zone
quest leg), **RV-07** (zone quest XP pass), **RV-26** (loot correction, feedstock slice) and
**RV-28** (feedstock flattening).

## 0a. Execution status and batching (opened 2026-07-29)

Execution runs in four batches, agreed with the user 2026-07-29. Each batch ends in one full
`migrate --patch 002` apply and its verification; **only batch 3 deploys**, so the wave still
reaches live validation as one compound change exactly as section 7b ruled. Intermediate applies
are not shipping.

| Batch | Contents | Applies | State |
|---|---|---|---|
| 0 | Measure the two balance decisions the plan defers: the feedstock quantity ladders and the zone quest XP targets | none | **DONE 2026-07-29.** Results in `IOD-WAVE1-BATCH0-MEASUREMENTS.md`. Both decisions RULED: the consumption ladder is DEFERRED out of this wave, and the XP pass CLAMPS to the corrected caps |
| 1 | Phase A alone (descriptors, `ENTITY_SYNC_MAP`, token constant) | direct `dsl sync`, no apply, no deploy | **DONE 2026-07-29, Gate A met.** Outcome in the Phase A section below |
| 2 | Phases B, C1, **C2**, C3, C4, D: the whole feedstock economy | 2 (Phase D's `packages/item-ids/` rename forces the second) | **DONE AND VERIFIED 2026-07-30.** Apply 1: 82 specs, 11,069 ops, 0 failed, 0 warnings. Apply 2 (the `item-ids` rename): 82 specs, 11,069 ops, 0 failed, 0 warnings. The regeneration diff was exactly the rename and nothing else, in `packages/item-ids/{index,materials}.yml` and the two `002/17` carve-out rows |
| 3 | Phase E, the divergence rows, all gates, deploy, user live validation | 1 | **DEPLOYED AND BOOTING 2026-07-30.** 84 specs, 11,097 ops, 0 failed, 0 warnings, client sync clean. All gates PASS. Deployed to dev, 184 files, verify OK. The world server REJECTED the datasheet TWICE before it booted, both times on invariants `dsl validate` does not check; both are fixed and both are now gated locally, see the boot-failure section below. **Only user live validation remains** |

### Pick up here: THE WAVE IS BUILT AND THE SERVER BOOTS. Only live validation remains (2026-07-30)

Everything in this plan is authored, applied, gated and deployed to dev. **Nothing is committed**:
patch 002 is still open, so the spec repo and both datasheet trees are deliberately dirty, exactly
as patch discipline requires.

**The one remaining step is the user's live validation pass**, from the acceptance checkpoints in
section 4. The dev world server loads datasheets at process startup only and its restart is manual,
so it must be restarted before testing.

Final apply: **84 specs, 11,097 operations, 0 failed, 0 warnings**, client sync clean, 184 files
deployed and SHA-verified.

| Phase | Delivered | Evidence |
|---|---|---|
| B | Feedstock identity flattened to 94101 | All 304 `EnchantDecomposition` rows on 94101 across all five `combatItemType` values; 1,413 `MaterialEnchantData` rows consume 94101 |
| B3/B4 | Grade-scaled fodder ladder | Six live decomposition ids carrying 16/48/96 and 8/24/48; all 900 fodder items mapped by (slot group x grade) |
| C | Every faucet removed but the sanctioned ones | 2 feedstock rows left in ALL zone loot, and both are the C4 carve-out bosses; 0 left in `Gacha`, `ItemConversion`, `AchievementList`, `EventMatching`, `StackAttendanceEvent`; `ItemMedalExchange` down to the Kugai `94101/95216` row |
| D | Tiers retired, ladder deleted | 0 ladder `ItemMix` records, 0 `itemMixId` back-pointers, 0 live `ItemMixData` references to a retired tier, 94101 reads "Feedstock" |
| E1 | Token item 95217 "Dawn Seal" | `NO_COMBAT`, `tradable: false`, `guildWarehouseStorable: false`, `boundType: None`, `maxStack` 10,000, `itemUseCount` 0, in base `ItemTemplate.xml` and `StrSheet_Item.xml`. R21 asked for `boundType: Loot`; it is OVERTURNED on both design and engine grounds, see the correction below |
| E2 | XP clamp + token threading | 35 zone quests stated across four specs, 26 changed, pool 58,200 to 24,740 (33,460 removed, 57.5 percent), **123 token rows**, all reproducing the batch 0 prediction exactly |

**The E2 ownership hazard did NOT fire, and it was checked rather than assumed.** A parser-based
per-quest diff of `QuestCompensationData_13.xml` against committed server HEAD confirms 1326 and
1330 still carry their full twelve level-7 gear rows (15021/15024/15027 and 15020/15023/15026),
every quest's gold is byte-identical to baseline, and no quest outside the wave's own list moved.

Gates, all run after the final apply:

| Gate | Result |
|---|---|
| `dungeon_audit.py --dungeons 9037` | PASS, 0 failures, exit 0 |
| `audit_class_gates.py --zones 13,64,213,436` | PASS, 0 gap groups, exit 0 |
| **`audit_item_references.py --retired`** (new, see below) | PASS. 358,398 item references checked, 0 dangling; 0 REACHABLE references to a retired tier |
| `audit_quest_design.py` (advisory) | 13 new findings, all MEDIUM or INFO, none a defect. See below |
| Per-quest compensation diff vs committed HEAD | ALL CLEAR |
| Consolidated value verification | ALL CLEAR, 25 checks |

**The referential integrity gate is now a repo tool**: `tools/dc-restore/audit_item_references.py`,
alongside the other `audit_*` gates. Re-run it after any wave that repoints item references. Three
things it established that this plan got wrong or did not know:

1. **The plan's claim that "the shipping corpus maintains perfect referential integrity on item ids"
   is not true.** Item **207328** is referenced by `BuyList@NeedMedalItemId` (2) and
   `ItemMedalExchange@medalItemId` (22) and has no `ItemTemplate` row in any variant. There are also
   24 dangling `decompositionId` and 9 dangling `itemMixId` references. ALL of them were proved
   pre-existing by resolving the same reference set against HEAD's row set and diffing, so this wave
   introduced **zero** new dangling references. They are baselined in the tool, and anything new
   fails. Phase D's conclusion is unaffected: it rests on the crash risk, not on a spotless corpus.
2. **The retired-tier exception is bigger than the plan's note, and the note is still right.** 783
   `MaterialEnchantData` rows still name a retired tier. 759 sit in records that NO live item links
   to, so they are unreachable dormant data; the other 24 sit in records 10401 and 10402, which are
   the plan's documented exception, and their 9 live items all still carry `enchantEnable="False"`.
   The gate tests REACHABILITY, not presence, which is the only formulation under which phase B1's
   claim is checkable. It also fails if any of items 163029 to 163037 ever becomes enchantable.
3. Advisory findings: all 13 new ones are consequences of quests 1324, 1326, 1330, 1351 and 1352
   now being STATED by patch 002 rather than only by the patch 001 baseline. The rows are unchanged.
   Three are the standing Reaper/Soulless omission (doctrine), which the non-new siblings already
   carry. Zero new findings at HIGH or CRITICAL.

**One decision was made during execution that the plan did not rule: the token quantity.** Nothing
in this plan, `IOD-BACKLOG.md` or the measurements document set a rate. Shipped as **one Dawn Seal
per zone quest, flat, on every one of the 35**, because framework `03 §3b-i` rules the earn rate is
"the same rate for all players in the content ... no level-band rate scaling", so any per-bracket
ladder would contradict it; and because a flat rate makes wave-1 income trivially readable (seals
earned = zone quests done), which is exactly the measured accumulation data RV-02 prices against.
If wave 2 wants differentiation, it belongs in the PRICES, not the earn rate. Reopen only with that
framework line in hand.

Specs added this session: `002/39-iod-progression-token.yaml` (2 ops) and
`002/40-iod-zone-quest-xp-and-token.yaml` (26 ops). Amended: `002/28`, `002/29`, `002/30`.
Divergence log: five rows appended, covering the XP reduction, the token threading, the
bind-behaviour row (R21, OVERTURNED; the row now records the overturn rather than a departure), the fodder yield ladder and the faucet removals.

#### The two boot failures, and what they cost

Recorded because both are generalisable and neither was catchable by anything this project ran
before. In both cases `dsl validate` passed, `migrate` reported 0 failed and 0 warnings, the client
sync was clean, and every standing gate was green. **A clean apply is not evidence that the server
will load the result.**

| # | Loader message | Cause | Fix |
|---|---|---|---|
| 1 | `stackable item cannot specify boundType [ItemTID=95217][boundType=1]` | Item 95217 was authored `maxStack: 10000` + `boundType: Loot` per the original ruling R21. The loader treats those as mutually exclusive | R21 overturned; the token is restricted by `tradable` and the guild bank instead. See the correction below |
| 2 | `randomReward invalid probability prov [itemTemplateId=19321] [0.900000]` | Phase C3 deleted weighted `<Reward>` rows from `<RandomReward>` groups without redistributing their probability. `RandomReward` is a SUM-TO-1 bag, so 81 groups across 6 `Gacha*.xml` files were left short. The id in the message is the BOX, not a reward row, and the loader names only the first 8 then stops | The C3 generator now rebalances survivors PROPORTIONALLY (user-approved 2026-07-30): each keeps its relative odds and absorbs a share of the freed mass. Verified: box 19321 goes 0.826 to 0.9177779 while the 82.6x ratio against its 0.01 sibling is preserved exactly, and the group totals 1 |

Failure 2 forced a spec shape change worth knowing about. `<Reward>` is a VALUE collection, so it has
no `upsert*` that could edit a probability in place, and mixing the whole-list and incremental forms
for one collection is `E570`. The 81 rebalanced groups therefore moved from incremental
`updateRandomRewards` to the whole-list `randomRewards` form, which restates every surviving row with
its `min`, `max`, `name` and `notifyLevel`. Every affected box carries exactly one classless group
(measured over HEAD: 92 boxes, all single-group, all classless), so restating the collection restates
only the group that was edited; the generator hard-fails if that ever stops being true.

**Which collections this applies to, because the obvious generalisation is wrong.** Measured over
server HEAD, sums within 1e-6:

| Collection | Groups | Sum to 1 | Reading |
|---|---|---|---|
| `Gacha` / `RandomReward` / `Reward` | 3,597 | 3,597 | sum-to-1 bag |
| `DecompositionData` / `RandomOutput` / `Output` | 139 | 139 | sum-to-1 bag |
| `ECompensation` / `Compensation` / `ItemBag` | 704 | 30 | independent per-bag roll |
| `ECompensation` / `ItemBag` / `Item` | 3,363 | 3,337 | independent, NOT a bag |

That last row is the trap: 99.2 percent is not an invariant. It is also why spec `002/41` can delete
1,785 whole `ItemBag`s without touching anything else, which had looked like luck and was not.
Separately, "sums to 1" means within 1e-6 and not bit-exact: 12 shipped `Gacha` groups miss by up to
1.47e-8 because the authors' own decimals do not add up, and the server boots on them, so an
exact-equality check would fail on untouched vanilla data.

**Both failures are now gated locally** in `tools/dc-restore/audit_item_references.py`, which has
caught three distinct classes in this wave: dangling item references, the stackable/`boundType`
loader rule, and sum-to-1 bags.

**THE DEFINITIVE FIX FOR FAILURE 2 SHIPPED THE SAME DAY, DSL `01e9dbb3`.** A run that would leave a
sum-to-1 bag off 1 is refused with **`E573`** before anything is written, and **`normalize: true`**
on the `updateRandomRewards` selector rescales the survivors proportionally. `002/38` is regenerated
on it: the generator's own rebalance arithmetic is deleted, the ~700 explicitly restated survivor
rows collapsed to **81 `normalize: true` lines**, and the spec shed about 600 lines. Verified by
probe that `E573` fires when `normalize` is removed, so the safety net is real and not merely
assumed. Re-applied, re-gated, redeployed.

The DSL team also settled the scoping question this plan could not. `ItemBag/Item` is genuinely NOT
a bag: its non-1 sums are most commonly **exactly 2, on 594 groups**, in named per-dungeon rune
families. 594 identical instances of one value is a design, so spec `002/41`'s 1,785 bag deletions
were safe for a reason rather than by luck. They also adopted the 1e-6 tolerance, and parked five
further 100%-uniform collections rather than enabling them, on the grounds that corpus uniformity is
evidence and not proof of a server-enforced invariant.

**CORRECTION 2026-07-30, after the first dev boot: RULING R21 IS OVERTURNED.** It was wrong on
design and impossible on the engine, in that order.

**The design correction (user ruling, and this is the one that governs).** `boundType` is for
EQUIPMENT the character wears, not for consumables or currency. A token is neither worn nor bound;
its only real requirement is that it must not move between PLAYERS. The two flags that gate that are:

| Flag | Blocks | Value |
|---|---|---|
| `tradable` | direct trade and the broker | `false` |
| `guildWarehouseStorable` | the guild bank, the other cross-player route | `false` |
| `warehouseStorable` | nothing between players: the personal bank is same-ACCOUNT only | `true`, kept |

Verified across the whole reserved token band 95214-95313: all four tokens (Bastion of Lok,
Sinestral Manor, Kugai's Crest, Dawn Seal) already carried `tradable: false` and
`guildWarehouseStorable: false`, so **no data change was needed** and the Dawn Seal was already in
the correct shape once `boundType` came off. R21 is restated in `IOD-BACKLOG.md` and now applies to
the whole band. Consequence to carry into RV-02: seals pool per ACCOUNT through the personal bank,
so price against per-account income, not per-character.

**The engine correction, which independently forced the same outcome.** The token was first authored
`boundType: Loot` per the original R21 and `WorldServer.exe` REFUSED THE DATASHEET at startup:

```
last read[.\Datasheet\\.\ItemTemplate.xml]
stackable item cannot specify boundType [ItemTID=95217][boundType=1]
[ItemTemplate] Loading Error!
```

The loader treats `maxStack > 1` and a non-None `boundType` as mutually exclusive, and the corpus
states the rule without exception: of 112,393 item rows, all 3,803 carrying `boundType: Loot` are
`maxStack: 1`, and all 25,073 stackable rows are `boundType: None`. The pairing had **zero** corpus
occurrences before this spec invented it, the same failure class as the `itemMixId="0"` and
`진행퀘스트 0,0` shapes this project has already been bitten by. A currency has to stack, so
`boundType` was never available here regardless of intent.

**Three checks now live in `audit_item_references.py` so none of this can regress:** the loader
invariant (no `boundType` on a stackable item), the token policy (`tradable` and
`guildWarehouseStorable` both `false` across the reserved band), and the referential sweep. The
generalisable lesson from the authoring mistake: **check `maxStack` alongside `boundType`, not
`boundType` alone.** The first draft justified `Loot` from items 45375 and 45376, which do carry
`NO_COMBAT` + `Loot` + `itemUseCount` 0, but both are `maxStack: 1`, so that evidence never tested
the case the loader actually rejects.

Both feedstock generators refuse to run against a dirty datasheet tree, by design. Before
regenerating either spec, `git checkout -- .` in the server datasheet repo, because `migrate`
replays from the COMMITTED baseline and a spec generated from an applied tree is wrong.

**All five DSL defects filed this session are resolved and verified.** Nothing is blocked.

**C2 JOINED THE WAVE 2026-07-30 (user ruling).** It was deferred for one reason only, a DSL capability
that did not exist, and the DSL team shipped it. The user ruled: "C2 original decision for not shipping
in wave 1 was a lack of DSL capability which is already solved, so you may proceed." The C2 section
below is rewritten accordingly and its old justification is preserved there as superseded text.

Why batch 1 stays separate from batch 2: registering a never-synced family can legitimately rewrite
shipped client values, and batch 2 then rewrites rows in those same four families. Isolating Phase A
keeps Gate A's attribute-level client diff attributable to one cause.

**Batch 0 corrected nine statements in this plan.** The corrections are folded into the sections
below and catalogued in section 4 of the measurements document. The one that changes authoring is
C1: the 304 decomposition rows carry **five** `combatItemType` values, not four.

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
restricted by `tradable: false` **and** `guildWarehouseStorable: false` (R21 as RESTATED 2026-07-30;
it originally said `boundType: Loot` and untradable, which was overturned on both design and engine
grounds, see section 0a); a token paid into a `class` bag is authored as 12 duplicate rows.

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

### Phase A outcome, executed 2026-07-29 (batch 1). Gate A MET

**Gate A cannot run inside a `migrate` replay, and that is now proven, not assumed.** `migrate.py`
builds its `sync_set` from the entity keys found in the patch's specs, so a family no spec touches is
never synced no matter what flags are passed, `--no-narrow` included. The first sync of these four was
therefore run directly: `dsl sync -c config/sync-config.yaml -e DecompositionData -e ItemMixData -e
EventMatching -e AchievementList`. That is a deliberate, documented use of a direct sync; the
never-use-`dsl apply`-directly rule is about APPLY replaying source-ref, and does not extend to
propagating existing server state to the client.

Result: dry-run planned 4 entities and 10 targets with no E603 and no E683, then the real sync exited
0 with 8 files written, 2 unchanged, 10 validated. A second run wrote **0 files**, so the family set
is idempotent. Attribute-level diff against a pre-sync snapshot:

| Family | Change | Verdict |
|---|---|---|
| `DecompositionData` | 334 to 343 rows, adding 99972 to 99974 and 202092 to 202097 | As predicted. Feedstock id census unchanged at 59 references |
| `ItemMixData` | 848 to 852 rows, adding 300041 to 300044 | As predicted. Census unchanged at 32 references |
| `EventMatching` | +26 `Compensation` rows; every other element count identical; all 12 root children present in the same order, `DailyCheckEvent` INCLUDED | `preserve-required-elements` works as documented. Census unchanged at 164 references |
| `AchievementList` | See the narrowing below | Descriptor narrowed to the base file |

**`AchievementList` was narrowed to the base file because the full mapping propagated unrelated
divergence.** With all 7 regional files mapped, the first sync deactivated **112** NAEU achievements
(server `AchievementList_NAEU.xml` carries `active="False"` on all 135 rows; client shard 00005
shipped 112 as `true`), hid 30 more, moved one grade, and flipped 10 rows across the JP, KR and RUS
shards. That is player-visible and has nothing to do with feedstock. The four regional shards were
restored from client-repo HEAD and the descriptor now maps only `AchievementList.xml`, which is where
all three feedstock achievements (9002, 9009, 9011) live. Do not widen it without first settling
which side is authoritative; the v92 server's regional files may simply be stale against the NA/EU
publisher client.

What the base shard did legitimately change, and is kept: 6 rows, achievements 455 and 580 to 584 in
categories 602 and 603, going from hidden and inactive to active and visible with 10/10/10/20/30
points. The server is the source of truth for the file it reads, and the direction is enabling.

**Two findings worth carrying forward.** First, the client shard ALREADY contained our fodder rows
206861 to 206868 before any sync, even though the family had never been registered, so they reached
the client by hand at some point: the same unreproducible-client-tree failure class as the
`StrSheet_NpcLoc` loss. Registering the family plus B3 brings both sides under spec control. Second,
W602 out-of-schema drops on this family set are extensive and expected: the client
`DecompositionData.xsd` declares no `probability`, `min` or `max` on `RandomOutput/Output` (427
records) and no `desc` (28), so the client carries dismantle OUTPUT IDENTITY but not its odds or
quantities. That is another reason B3's yield ladder is server-only.

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
| B3 | New spec `002/35-feedstock-flatten-decomposition.yaml`, entity `decompositions`: bring rows 206861 to 206868 under spec control and rebuild them as the six-row grade-scaled ladder decided below. Wire shape measured 2026-07-29: `FixedOutput` holding one `Output templateId amount`, NOT `RandomOutput` with min/max/probability | 6 ops |
| B4 | `tools/gear-infusion/generate_infusion.py`: emit one decomposition id per (slot group x rareGrade) instead of per slot, and set `decompositionId` per item from grade as well as slot. Regenerate `002/06-gear-infusion-items.yaml`. **HARD PREREQUISITE: B3.** See below | 900 items retargeted |

**B2: author `combatItemType` in UPPER_SNAKE. The value list this project has been reading was
fictional.** The `enchant-data.mdx` page listed PascalCase members (`EquipWeapon`, `EquipArmorBody`,
`EquipArmorHand`, `EquipArmorShoes`, ...) that the parser has never accepted. DSL `09192855` replaced
the list with the real enum member names.

**CORRECTED 2026-07-29 (batch 0): there are FIVE values, not four, and the rank coverage is not
uniform.** Measured over the 304 rows in the working-tree `EnchantData.xml`:

| Slot | Value | Rows | Ranks |
|---|---|---|---|
| weapon | `EQUIP_WEAPON` | 48 | 1 to 12 |
| weapon component | `ENCHANT_COMPONENT_WEAPON` | 64 | 1 to 16 |
| body | `EQUIP_ARMOR_BODY` | 64 | 1 to 16 |
| arm | `EQUIP_ARMOR_ARM` | 64 | 1 to 16 |
| leg | `EQUIP_ARMOR_LEG` | 64 | 1 to 16 |

An earlier draft of this table named only the four `EQUIP_*` slots. Authoring from it would leave
**64 of the 304 rows still pointing at a retired tier**, and the row-count check B2 already warns
about would not catch it. `ENCHANT_COMPONENT_WEAPON` is a declared enum member (DSL docs
`schemas/enchants/enchant-data.mdx`), so all five are authorable.

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

Re-verified 2026-07-29 (batch 0), independently and exactly: 713 item rows carry a
`linkMaterialEnchantId` pointing at one of the 82 Relic-consuming records, 713 distinct ids, 575 of
them in base `ItemTemplate.xml` and the rest in `_KR` (92), `_RUS` (32) and `_JP` (14).

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
amounts (`EnchantData` 4 to 48, `MaterialEnchantData` 4 to 60, `ItemConversion` 120). Flattening
the id makes those numbers mean something different, so re-derive them from framework `04 §2c`
(consumption per attempt) and `§4e` (yield by grade) rather than inheriting them by accident. Scope
this as its own reviewed step inside B, not as a side effect.

**MEASURED 2026-07-29 (batch 0), and the recommendation is to DEFER this step out of wave 1.** Full
tables in `IOD-WAVE1-BATCH0-MEASUREMENTS.md` section 2. Three corrections to the framing above:

1. `MaterialEnchantData` does not carry "4 and 12". Our 100 records run 4 / 8 / 24 / 48 / 60
   feedstock by enchant step on weapon and body, half that on arm and leg.
2. `§2c` scales **materials by enchant step** and **gold by gear level band**, not materials by
   gear band. Our ladder is band-flat across all four level ranges, which is compliant on the
   material axis. That removes most of the re-derivation case.
3. The largest actual gap is not a quantity at all: `requiredMoney` is `0` on all 1,350 of our
   `MaterialItem` rows, so `§2c`'s per-attempt gold sink is unimplemented server-wide. That is a
   framework-wide change, not an IoD one, and it is not in this plan.

Deferring costs nothing, because flattening the identity changes no amount. Shipping the
re-derivation here would change enchanting demand on every gear band inside the same apply that
changes IoD supply three ways, which discards Phase B's own reason for anchoring the fodder ladder
on rare. **RULED 2026-07-29 (user): deferred.** B2 keeps `resultItemAmount` untouched, the workbook
keeps its amounts, and the `§2c` re-derivation plus the gold cost become their own backlog item.

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

**C2 SHIPS IN WAVE 1. Reversed 2026-07-30 by user ruling, after the blocking capability landed.**

The 2026-07-28 deferral read: "The DSL docs settle it: bag collections are clear-and-replace, and
'the DSL does not support granular add/remove for bags or items'. Removing one `ItemBag` means
restating that `Compensation` record's ENTIRE bag list, so C2 would make us the author of roughly
1,469 loot records across 85 zone tables we have never touched." That was true when written and is
now false. DSL `d06400c2` (2026-07-30) added per-row collection membership to `eCompensations`,
`gachaItems`, `itemConversions` and `achievements`, and `d04e4015` corrected the gacha key
measurement the same day. The removal was never in doubt; only its cost was.

**Measured surface, 2026-07-30, against the working-tree server datasheet** (the 11 patch-002 zones
excluded, since C1 owns those):

| Measure | Value |
|---|---|
| Feedstock `Item` rows | **1,595** (the earlier ~1,790 estimate was high) |
| `ECompensation_*.xml` files | 85 |
| `Compensation` records touched | 1,159 |
| Feedstock items sharing a bag with other loot | **0 of 1,595.** Every one sits alone in its own `<ItemBag>` |
| Compensations left with no bags after removal | **0** |

So the op is `removeItemBags`, not a bag-content edit, and nothing surviving is restated. Blast
radius drops from "we now own 1,469 complete loot tables" to "1,595 bags deleted, nothing else
touched".

**Selector rules the generator must follow.** `ItemBag` is an AMBIGUOUS collection: `bagName` is not
a key and neither is `id`. Measured over the 1,595 target bags: 1,105 pin to exactly one row with a
full-attribute selector, and the other 490 sit in groups of 3, 5, 7 or 10 attribute-identical
siblings. **Every sibling in every one of those groups is itself a feedstock bag**, and zero
selectors would reach a non-feedstock bag, so removing a whole group is correct. Therefore:

- Emit ONE op per attribute-identical group with `expect: <group size>`, never one op per row. A
  per-row spec makes the first op remove all N siblings and turns the rest into `W500` no-ops.
- State the bag's FULL attribute set in the selector. A partial selector over-matches.

**`eCompensations` is `None` in `ENTITY_SYNC_MAP`, so C2 is server-only and has no client leg.**

**DONE 2026-07-30.** Generator `tools/feedstock-faucet/gen_feedstock_bag_removal.py`, spec
`002/41-feedstock-faucet-removal-zones.yaml`. Numbered 41 because 37 to 40 are already claimed by
phases D, C3 and E; the file ordering does not matter here because no other spec in the patch writes
these 85 zone files. Generated output matches the measurement exactly: 85 files, 1,159 update
records, 1,188 removal ops, 1,595 bags, 83 ops carrying `expect > 1`. **`dsl validate`: 1,159
operations valid, zero warnings.**

**A second DSL defect was found generating it, and it changed the selector.** The first attempt used
`(bagName, id, probability)` and 3 ops failed with a bare `E500`. Cause: the matcher cannot match an
attribute whose value is an integral decimal. `probability="1.0"` fails against `1.0`, `1` and
`"1.0"` alike, while `0.1`, `0.5` and `0.0416` all match correctly. The selector is now
`(bagName, id)`, which is sound because `bagName` alone was already measured to reach zero
non-feedstock bags. Filed as section 3 of
`docs/dsl-requests/2026-07-30-gacha-randomreward-classless-group-unaddressable.md`. **Do not add a
numeric attribute to a generated selector in this wave without probing it first.**

**Carried over from the deferral, still true: `ItemMix 216862` breaks when its last 94105 source
goes.** See the precondition note below, which was written for a C2-plus-C3 interaction and now
applies inside a single wave rather than across two.

**Precondition, now due: `ItemMix 216862` breaks when its last 94105 source goes.** That
recipe consumes `94204 x200` + **`94105 x500`** + `98505 x50`. Item 94105's grant paths are
achievement 9009, `BuyList` 2933, the medal exchange on item 91966, npc drops in zones 711 and 750,
a `Gacha_Tool.xml` box (244757, grants 25) and two `ItemConversion` seeds. **C3 deletes four of
those and C2 deletes the zone drops**, which together leave the recipe uncompletable. The last two
paths were found by corpus sweep because `item_sources` does not scan `Gacha_Tool` or
`ItemConversion` grants.

The plan said "decide the recipe's fate when C2 is scoped, not by accident". C2 is now scoped, so:

**RULING C2-a. APPROVED by the user 2026-07-30.** The two live non-ladder `ItemMix` records that
reference retired tiers are REPOINTED to 94101 at unchanged amounts, rather than deleted or left to
rot:

| Record | Today | After | Why |
|---|---|---|---|
| `216862` | consumes `94105 x500` | consumes `94101 x500` | Keeps the recipe completable, which C2+C3 would otherwise silently end. A recipe that CONSUMES feedstock is a sink, not a faucet, so R13 does not touch it, and R15 puts the surviving identity on 94101 |
| `534` | produces `94108 x5` | produces `94101 x5` | Phase D's "must not be broken" list protects it, but minting a RETIRED tier contradicts R18. Repointing preserves the recipe and stops the last live grant of a retired id |

This is the minimum change that satisfies both rulings the plan already carries. It also removes the
last two live references to 94102-94112 outside the resident `ItemTemplate` rows, which makes the
Phase G referential gate a cleaner statement. Amounts are deliberately untouched: the consumption
ladder is DEFERRED out of this wave (batch 0), so re-pricing 500 or 5 here would be exactly the
out-of-scope tuning that ruling excluded.

**C3, the small faucets.** One spec, `002/38-feedstock-faucet-removal.yaml`:

| Family | Rows | Why delete |
|---|---|---|
| `EventMatching` (Vanguard) | 164 | **UNBLOCKED 2026-07-29, back in wave 1.** Both legs were fixed the same day the audit filed them. See below |
| `Gacha`, all **8** files | 307 on tiers 2 to 12 | Only 8 boxes are reachable. Migrating creates 307 new 94101 faucet rows for nothing. **The datasheet holds 8 Gacha files, not 7**: `Gacha.xml` plus `_JP`, `_KR`, `_NAEU`, `_RUS`, `_THA`, `_TW`, plus **`Gacha_Tool.xml`**, which grants 25x 94105 from box 244757 and would otherwise survive this step |
| `ItemConversion`, **all 6 files holding rows** | **80 of 80** | The entity was `SingleFile("ItemConversion.xml")` and is now `RegionalVariants` (DSL `36ceaa0a`), so `update` and `delete` search every variant and a row is addressed by `itemTemplateId` wherever it lives. Distribution re-measured 2026-07-29: base 40, `_JP` 2, `_KR` 1, `_NAEU` 27, `_RUS` 8, `_Tool` 2. Nothing is deferred |
| `AchievementList` 9002 / 9009 / 9011 | 3 | Large amounts (180 / 60 / 50), achievement-granted feedstock is a direct faucet |
| `BuyList` 2933 + `ItemMedalExchange` (vanilla Feedstock Exchange Shop) | 2 | Doubly dead: no NPC opens it and its currency 91966 has zero sources anywhere |
| `StackAttendanceEvent` | 4 | Now authorable, see below. Inert content, so this is hygiene rather than economy |

#### C3 op shapes, settled 2026-07-30 against the new binary

Every shape below was probe-validated with `dsl validate` against the live server datasheet before
authoring. Nothing was applied.

| Family | Rows | Op shape |
|---|---|---|
| `Gacha` `<FixedReward>` | 31 | `removeFixedRewards` with the row's full attributes plus `expect: 1` |
| `Gacha` `<RandomReward>` | 280 in 92 groups | `updateRandomRewards` with a bare `expect: 1` group selector, then `removeRewards` with full attributes. **All 92 groups are classless and each affected item holds exactly one group**, so `expect: 1` is right in every case |
| `ItemConversion` | 80 | 43 at `SeedItem/ResultItem` via `removeResultItems`; 37 at `ResultItemSet/ResultItem` via `updateResultItemSets` (selector matches exactly 1 in all 37) plus `removeResultItems` |
| `AchievementList` | 3 | `removeItemRewards`, keyed on `templateId`. Cleanest of the four |
| `EventMatching` | 164 | `removeRewards`, keyed on `templateId`. **Was the expensive leg and no longer is.** It originally restated 934 surviving rows to delete 164, 73% of the spec, because `rewards` was clear-and-replace. Filed as `docs/dsl-requests/2026-07-30-eventmatching-rewards-no-collection-membership.md` with the corpus measurement showing the collection qualifies as keyed (`templateId` on all 2,049 rows, zero repeats in any of the 457 containers), and DSL `36de802c` delivered it the same day. Spec went 4,715 lines to 2,081 |
| `BuyList` 2933, `ItemMedalExchange` | 2 | UNCHANGED |
| `StackAttendanceEvent` | 4 | UNCHANGED. Keyless singleton, restate `sampleEvents` whole |

Row counts re-measured 2026-07-30: `Gacha` holds **311** feedstock reward rows, which is the plan's
307 on tiers 2 to 12 plus 4 on 94101 itself.

**DONE 2026-07-30.** Generator `tools/feedstock-faucet/gen_feedstock_faucet_removal.py`, spec
`002/38-feedstock-faucet-removal.yaml`. **`dsl validate`: 334 operations valid, zero warnings.**
Every count came out exactly as this section predicted: 311 gacha rows over 114 items (31 fixed, 280
random), 80 itemConversion rows over 50 seeds, 3 achievement rows, 164 EventMatching rows over 164
(event, group) pairs split 82 priority and 82 secondary, 1 BuyList row, 1 exchange, 4
StackAttendanceEvent rows. The Kugai 94101 / 95216 exchange is kept, and the generator REFUSES to run
if it ever meets a feedstock exchange row that is neither the Kugai row nor the dead one.

**A fourth naming trap, not in the 2026-07-29 correction list.** `EventMatching` reward rows are
`Compensation@templateId`, **not** `@itemTemplateId`. Scanning for the latter reports zero rows and
reads as "nothing to do", which is exactly how the first traversal written for this leg failed. The
2026-07-29 correction covered `Gacha`, `BuyList` and `ItemMedalExchange` naming but not this one.

**Selector rule used throughout C3: the item id and `expect`, nothing else.** Every row a selector
can match is feedstock by construction, so an over-match is still correct, and no numeric attribute
is stated, which sidesteps the integral-decimal matcher defect that bit C2.

#### C3 measured 2026-07-29 (batch 2), with three corrections

Row counts confirmed exactly where the plan gave them: **164** EventMatching reward rows, **307**
Gacha rows on tiers 2 to 12, **80** ItemConversion rows split base 40 / `_JP` 2 / `_KR` 1 / `_NAEU`
27 / `_RUS` 8 / `_Tool` 2, **3** achievement rows (9002 pays 94104 x180, 9009 pays 94105 x60, 9011
pays 94106 x50, and all three sit at `active="False"`), and **4** `StackAttendanceEvent` rows
(94111 x50 on days 1, 6, 11 and 16).

**1. DO NOT strip feedstock from `ItemMedalExchange` wholesale. It holds the Kugai shop row.** The
file carries exactly two feedstock exchanges: `itemId="94105" medalItemId="91966"` (the dead
vanilla Feedstock Exchange Shop, which C3 removes) and `itemId="94101" medalItemId="95216"`, which
is the **Kugai token shop** row that phase F says stays regardless, because the framework sanctions
a token shop selling feedstock (`03 §3b-i`). A family-wide sweep would have deleted it silently.

**2. Element and attribute names, since the obvious guesses are all wrong.** `Gacha` rows are
`GachaItem` / `FixedReward` or `RandomReward` / `Reward@itemTemplateId`, NOT `Item@templateId`;
scanning for the latter reports zero rows and reads as "nothing to do". `BuyList.xml`'s root is
`ItemSellList` with `List@id` and `Item@itemId`, so the target is the `94105` item inside
`List id="2933" NeedMedalItemId="91966"` (its sibling item 138294 stays).
`ItemMedalExchange` is `ExchangeList` / `Exchange@itemId` with `@medalItemId`.

**3. `fill_zone_loot.py` needs `--vanilla-ids`, or regeneration silently drops content.** The C1
regeneration was run first without it and the ten zone specs came back missing their whole
`cCompensations: delete` sections (868 deletions instead of 219), because that block is only emitted
when the flag is present. Correct invocation:
`python tools/zone-loot/fill_zone_loot.py --patch 002 --zones 2,3,5,6,7,15,16,17,487,488
--vanilla-ids data/zone_loot/vanilla_ccomp_ids.json`. Note also that `PATCH_ZONES` has no `002`
entry, so omitting `--zones` filters nothing and would generate specs for all 123 tiered zones,
silently widening the patch.

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

**RE-VERIFIED FROM SOURCE 2026-07-29, and the docs page is STILL inverted.** `event-matching.mdx`
under "Common pitfalls" continues to read "`group: priority` (false) and `group: secondary` (true)",
which is wrong. `DataSheetLang.Yaml/Mapping/EventMatchingEventDataMapper.cs`, `MapGroup`, is the
authority: `"priority" => true`, `"secondary" => false`. The table below stands. Whatever landed in
`da47c4e9`, the page did not get fixed, so filed again as
`docs/dsl-requests/2026-07-29-eventmatching-group-doc-backwards-and-granular-removal.md`. Do not
author this leg from the docs page.

Measured group split of the 164 feedstock rows, so both legs are sized: **82 in the `true`
(`priority`) group and 82 in the `false` (`secondary`) group**, across 232 and 225 events
respectively.

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

**C4 DONE 2026-07-30.** Row written to `docs/plans/classic-restoration/iod/divergence-log.md`, with
its live-test checkpoint. Ruling C2-a got a row in the same file.

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
| E1 | `002/39-iod-progression-token.yaml` | Item **95217**, the next slot in the project's own reserved token block 95214 to 95313. `NO_COMBAT`, high `maxStack`, and restricted by **`tradable: false` plus `guildWarehouseStorable: false`, NOT by the `boundType: Loot` R21 asks for**: binding is the wrong instrument for a currency and the loader refuses any `boundType` on a stackable item anyway (correction in section 0a). Copy the `definitions:` plus `items: upsert:` shape from `002/14-dungeon-tokens.yaml`, NOT its MEDAL_USEABLE wiring, which R11 rejects |
| E2 | **AMEND `002/28`, `002/29`, `002/30`, plus one new spec `002/40`** | The XP pass and the token rows, together. NOT one new spec: see the ownership rule below |

**Author the strings in a TOP-LEVEL `itemStrings:` block, not the inline `strings:` form.**
`migrate.py` matches `ENTITY_KEY_PATTERN` anchored at column 0, so an indented inline block does not
register the `itemStrings` key. Patch 002 is covered today only by accident, because two unrelated
specs carry top-level blocks. A patch whose only string authoring was inline would ship a nameless
item to the client.

**E2, the XP pass (RV-07).** Cap each live zone quest at 25 percent of the **median** story quest XP
of its level bracket. Two measurement distortions to correct for when computing the brackets: the 1-2
bracket median is inflated by the twelve class-training missions at 2,100 XP each, of which a
character completes exactly ONE; and the 5-6 bracket median is deflated by quests 1382 and 1383 at
100 XP, which are a paired gathering-intro variant rather than a real story payout.

**MEASURED 2026-07-29 (batch 0). Author from `IOD-WAVE1-BATCH0-MEASUREMENTS.md` section 3, not from
this paragraph.** The corrected caps are 200 (bracket 1-2), 225 (3-4), 900 (5-6), 1,305 (7-8) and
1,125 (9-10, no live zone quest sits there). Both corrections bite hard and in OPPOSITE directions:
bracket 1-2 falls from 525 to 200, bracket 5-6 rises from 300 to 900.

Three figures in the earlier draft are superseded. **26 of the 35** quests change, not 29 (the raw
uncorrected count is 28). The pass removes **33,460 XP, 57 percent of the zone-quest pool**, taking
the zone share of all obtainable island XP from 50 to 30 percent while the story spine stays at
57,740 and untouched. And bracket 3-4's cap rests on only three story quests, two of them small
utility missions, so 225 is the least well-supported number in the table.

**Shaping rule RULED 2026-07-29 (user): clamp.** A zone quest above its bracket cap drops to the cap;
one already under it is untouched. The resulting flatness (seven quests at 220 in bracket 3-4, eight
at 1,300 in 7-8) is accepted. The XP reduction itself is explicitly NOT a risk to manage: the story
spine reaches level 10 without mob XP, and the cap is expected to tighten further as more zone quests
are added. See the ruling in the measurements document section 3d.

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

**E2, the token rows (RV-03).** 35 live zone quests, of which **2** are repeatables that belong to
RV-08 (measured 2026-07-29: 1334 and 1341, both `반복`; the earlier count of 3 was wrong). Both stay
in this wave, because 1334 is already under its cap and 1341 needs only -200; repeat-specific
economics stay RV-08. The bag-mode split below was confirmed exactly by the batch 0 census.
Threading difficulty splits by bag mode:

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
   **One known-good exception the gate must not flag** (measured 2026-07-29): vanilla
   `MaterialEnchantData` records 10401 and 10402 consume 94104 and are referenced by 9 live items,
   163029 to 163037, level-60 superior armor in `ItemTemplate_NAEU.xml`. All 9 carry
   `enchantEnable="False"`, so the link is inert and no player can reach it. This is why B1's claim
   that all REACHABLE enchanting consumes 94101 still holds; 63 vanilla records consume a retired
   tier and these two are the only ones any live item points at.
4. Advisory review: `audit_quest_design.py --zones 13,64,213,313,364 --since HEAD`.
5. Regression diffs, parser-based never regex: the compensation block contains self-closing
   children, so a lazy terminator truncates it. This project has already been burned by that.
   **Per-quest compensation diff against committed HEAD is mandatory**, because the E2 ownership
   hazard fails silently and shows correct op counts.
6. **Divergence log rows, before the wave is called done.** Doctrine rule 6 and RV-07's own gate
   both require them, and an earlier draft of this plan scheduled a row only for the C4 carve-out.
   Rows needed: the XP reduction on every changed zone quest (category policy, R10 and R20), the
   token threading (authored content), the token's restriction policy against R21 and the three
   existing project tokens (R21), the fodder yield ladder change, and the feedstock faucet removals.
7. Deploy, then USER live validation. Server restart is manual.

## 3b. Batch 2 apply 1: what the first real apply taught us (2026-07-30)

The specs all validated clean and the apply still failed twice before it was right. Every failure
was invisible to `dsl validate`, which is the point worth carrying.

**1. An emptied collection can be XSD-invalid on the client even when the server accepts it.**
First apply died at the client sync with `E650`: `RandomReward has incomplete content`. C3 had
removed every `Reward` row from 11 gacha groups, and the client `Gacha.xsd` declares
`RandomReward/Reward` WITHOUT `minOccurs="0"`, so an emptied group fails validation and the sync
refuses the whole file. Fixed by removing the whole group with `removeRandomRewardGroups` when it
would be emptied. Checked the same question across every collection this wave touches:

| Collection | Emptied by this wave | Client XSD | Action |
|---|---|---|---|
| `Gacha` `RandomReward` | 11 groups | `Reward` required | Remove the group |
| `ItemConversion` `ResultItemSet` | 5 sets | `minOccurs="0"`, so valid | Remove anyway: an empty set is a dead roll slot |
| `Gacha` `FixedReward` | 13 containers | `minOccurs="0"`, so valid | Leave. There is no op to remove the container and an empty one is inert |
| `EventMatching` `CompensationList` | 0 | n/a | Nothing to do |

**2. Not generating a row does not delete a row, and C1 rested on that confusion.** Phase C1
neutered the loot generators and the plan reasoned that the rows "exist only in the dirty tree", so
a replay would simply never write them. That is true of the 299 rows the generators had added. It is
false of the **190 vanilla rows already in the committed baseline** for zones 2, 3, 5, 6, 7, 15, 16,
17, 487 and 488. Caught only by verifying by VALUE after the apply: 192 feedstock rows survived, all
of them inside the eleven zones this patch owns, while all 1,595 rows in the 85 zones it does not
own were gone. R13 was being enforced everywhere except where we were working. C2's scope now covers
95 zone files, 1,349 records, 1,378 ops, 1,785 bags; only zone 13 is excluded, for the C4 carve-out.

**3. Generate against the COMMITTED baseline, never the working tree.** `migrate` applies with
`--source-ref <server HEAD>`, so a spec replays against the baseline. Regenerating C2 from a tree
that already held an applied patch produced a spec covering only the 190 rows the last apply had
left behind. The generator now refuses to run on a dirty `CompensationData` unless `--allow-dirty`
is passed.

**4. `itemMixes` could not change a material, and then it could.** Half of ruling C2-a was dropped
mid-execution: `materials` APPENDED instead of replacing (216862 came out with six materials, still
demanding the 94105 the ruling exists to remove, with `count` lost from the first appended entry),
`upsert` appended too, and `delete` plus `create` failed on the create. Filed as section 4 of
`docs/dsl-requests/2026-07-30-gacha-randomreward-classless-group-unaddressable.md` and fixed the
same day by DSL `d53dbfad`. The op is restored and applied. Two things from the fix worth carrying:

- **`SpecMapper` emits operations grouped by kind in the fixed order create, update, delete,
  upsert**, whatever order the YAML keys are written in. So delete-then-create can never work
  within one spec: the create is always attempted while the id is still taken. Use `upsert` for a
  whole-record rewrite. The bare `E500` on that path is now `E429`, naming the id, the file and the
  ordering rule.
- **`materials` is clear-and-replace on both `update.changes` and `upsert`.** A material left out is
  deleted, so restate every row you intend to keep.

**5. The EventMatching leg was rebuilt after the fact, and the diff obligation went away with it.**
DSL `36de802c` (2026-07-30) added `removeRewards` keyed on `templateId` to `eventMatchingEvents`,
which was the one family in this wave with no membership support. The C3 generator now names only
the 164 rows it deletes instead of the 934 it wanted to keep. Re-applied and verified with a
per-event diff against committed HEAD: all 457 `CompensationList` containers present, exactly 164
rows removed, every surviving row byte-identical to baseline-minus-feedstock, zero mail strings
touched. The two families still restated are `buyLists` (1 surviving item) and
`stackAttendanceEvent` (16 surviving rewards), both small enough to read.

### Final verification, apply 1

`82 applied, 0 failed, 11,069 operations, 0 warnings`, client sync clean. Value checks, all pass:
zone loot down to exactly the 2 carve-out rows on Vekas and Kugai; 0 feedstock rows left in `Gacha`,
`ItemConversion`, `AchievementList`, `EventMatching`, `StackAttendanceEvent`; 0 emptied
`RandomReward` groups or `ResultItemSet`s; `BuyList` down to the sanctioned Kugai list 9999011;
`ItemMedalExchange` down to the sanctioned 94101/95216 row; all 10 ladder `ItemMix` records gone;
`534` repointed to `94101 x5` with its single material intact; `216862` at exactly 3 materials with
`94101 x500` replacing `94105 x500` and counts 200/500/50 intact; **zero live references to a
retired tier 94102-94112 anywhere in `ItemMixData`**; 0 `itemMixId` back-pointers left; 94101 reads
"Feedstock" and 94112 "Obsolete Feedstock (Tier 12)".

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
| Sync reports no value-change summary, so a first adoption that rewrites behaviour-bearing attributes reads as a clean success. Plus: W602's "regenerate or extend the schema" advice is wrong for a Novadrop client DC | `docs/dsl-requests/2026-07-29-sync-first-adoption-change-visibility.md` | open, filed from batch 1. Blocks nothing: Gate A was met with an external snapshot-and-diff script |
| `lookup` / `batch_lookup` return an opaque error for `entity: "Item"` | `docs/mcp-requests/2026-07-28-item-lookup-opaque-error.md` | open |

Binary in use is now the **`a70475f5` build** (2026-07-30 17:52). **The version string is stale
AGAIN and by a different amount each time**, so it is not a usable identifier: this build prints
`1.0.0+01e9dbb3`, one commit behind, exactly as the `d04e4015` build printed `1.0.0+e89cc53c`.
Identify a binary by file mtime and by BEHAVIOUR. Confirmed behaviourally here by probing an emptied
`<RandomReward>` group on a scratch datasheet and getting the `E573` wording only `a70475f5` emits
("holds no `<Reward>` row, so its probabilities total 0, not 1").

**`a70475f5` needed NO spec change, and the reason is worth keeping.** It refuses an emptied
probability bag and points at the remedy each collection actually has. Checked against every spec in
the patch, then proved by a full re-apply that left both trees byte-identical:

| What it added | Our exposure | Why nothing moved |
|---|---|---|
| `E573` on an EMPTIED bag, not just one off 1 | `002/38` empties 11 fully-feedstock groups | It already removes the GROUP with `removeRandomRewardGroups` rather than emptying it, which is precisely the remedy the new error names. That shape was forced back in apply 1 by the client XSD (`E650`, `RandomReward/Reward` has no `minOccurs="0"`), so the client constraint had already driven us to the server-correct answer |
| `DecompositionData/RandomOutput` added as a checked bag | `002/35` rewrites `Decomposition` rows 206861-206868 | It uses `fixedOutputs` only. **Caveat for any future spec: `randomOutputs` has NO `normalize`.** It is replace-all, so the author must state probabilities totalling 1, or set `equalProbability: true` |
| `upsertRandomRewardGroups` stating only a key is refused, since it would create an empty group | none | No spec in the patch uses that op |

The three specs that fail a STANDALONE `dsl validate` (`002/02-brawler-weapons`, `002/02-reaper-weapons`,
`002/05-chest-missing-items`) are unrelated to any of this: they emit `E403 has compute block but
stat-formulas.yaml is missing`, because `migrate` passes a `--formulas` path that a bare `validate`
does not. Not a regression and not new.

### Collection membership landed 2026-07-30, and it reopened C2

| Commit | What it gives this wave |
|---|---|
| `d06400c2` | Per-row add/remove/upsert inside nested collections on `eCompensations`, `gachaItems`, `itemConversions` and `achievements`. Whole-list keys still mean replace-all; mixing the two forms for one collection is `E570` |
| `eb09d8ee` | Gates the feature on corpus-measured identity kinds |
| `d04e4015` | Measures key PRESENCE, not just uniqueness. Reclassifies `RandomReward` from keyed to value, so a classless group is selected by a bare `expect: <count>` |

Filed by this project and resolved the same day:
`docs/dsl-requests/2026-07-30-gacha-randomreward-classless-group-unaddressable.md`. That file's own
diagnosis was wrong in an instructive way: it assumed `class` needed a null-meaning selector value,
when the real fault was that `class` is not a key at all and the corpus measurement said it was.

**Two things to hold while authoring against this feature.**

1. **An `expect` mismatch reports a bare `E500`, not the documented `E571` with counts.** Reproduced
   on both `gachaItems` and `eCompensations`. Filed as section 2 of the request above. It matters
   because C2 and C3 emit roughly 1,200 generator-derived `expect` values, and any drift between our
   parse and the DSL matcher lands as an error naming neither the collection nor the counts.
2. **`class: ""` is not how you name a group that has no `class`.** Per datasheet convention an empty
   value means present-and-empty, so it matches nothing. Use the bare `expect` form.

What the feature does NOT cover, so these legs are unchanged: `EventMatching` rewards (still
clear-and-replace restate), `StackAttendanceEvent`, `BuyList`, `ItemMedalExchange`, and Phase E's
`questCompensations`, which remains replace-all with the ownership hazard that implies.

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
| PROBE-F2 | ~~Can `eCompensations` remove a single `ItemBag`?~~ **ANSWER CHANGED 2026-07-30: YES.** The 2026-07-28 answer ("clear-and-replace, no granular add/remove") was correct against that binary and is now obsolete. DSL `d06400c2` added `removeItemBags`. Probed with `dsl validate` against `ECompensation_457` npc 1001: a full-attribute selector with `expect: 10` validates, and an off-by-one `expect` refuses. This is what put C2 BACK into wave 1 | nothing |
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
