# DSL capability audit: authoring new NPCs, AI, NPC skills and loot

Audited 2026-07-28 against `dsl.exe` build `1.0.0+b56c21dd37706901c1c0aec407fae946db873245`
(previous verified build `1.0.0+12a24535`).

Method: the DSL YAML authoring surface was extracted from
`<dsl_repo>\src\DataSheetLang.Yaml.Contracts\Schemas\` (the
`[SchemaProperty("alias")]` and `[YamlMember(Alias = "alias")]` declarations, plus plain
C# properties on block classes) and compared name by name against the real server corpus
under `<server_datasheet>`. Corpus counts below are populated rows,
measured recursively under each entity element across the whole family, not a sample.

Two caveats on the method, stated up front:

- Matching is by NAME, flat across depth. A corpus attribute is called covered if the DSL
  declares that name anywhere in the family's schema tree. This can over-credit: a name
  modelled on one block but not on the block the corpus actually uses would read as
  covered. Every gap reported below was individually re-checked against the source; the
  positives were not exhaustively re-checked.
- Container element names (`<Item>`, `<Work>`, `<Info>`, `<Fence>`) legitimately have no
  alias of their own because the DSL exposes them as a plural list property. Those are
  excluded from the gap counts; the attribute-level numbers are the meaningful ones.

Nothing in this audit was proven by running an apply or a sync. Where a claim needs a live
proof, the required verification is stated.

---

## 1. Verdict table

| Family | DSL entity key | Operations | Field coverage | Sync status | Blocker |
|---|---|---|---|---|---|
| **NpcData** (`NpcData_<hz>.xml`, `<Template>`) | `npcs:` | create, update, delete, upsert, updateWhere | **FULL.** 294 of 297 corpus attribute names modelled. The 3 misses are corpus corruption, not fields (see 2.4) | Client family EXISTS (426 shards) and `sync-config.yaml` carries a working `NpcData` descriptor, but `ENTITY_SYNC_MAP` maps `npcs: None` | **YES** (pipeline, not schema) |
| **AiData** (`AIData_<hz>.xml`, `<Ai>`) | `ai:` | create, update, delete, upsert, updateWhere | **PARTIAL.** 118 of 122 corpus attribute names modelled. Missing: `motionId`, `patternShowTime`, `patternGuide`, `needTarget` | Client family EXISTS (426 shards). `AIData` is **not registered in `sync-config.yaml` at all**, and `ENTITY_SYNC_MAP` maps `ai: None` | **YES** (pipeline) |
| **NpcSkillData** (`NpcSkillData_<hz>.xml`, `<Skill>`) | `npcSkills:` | create, update, delete, upsert, updateWhere | **PARTIAL, worst of the set.** 183 of 400 corpus attribute names modelled; **217 missing**, including 25 on `<Skill>` itself (`parentId` at 98% prevalence, `returnAnimSet` at 65%, `ignoreDefenceRate` at 34%) | Synced as `SkillData` (538 client shards) | **YES** |
| **Loot** (`CompensationData\CCompensation_<hz>.xml`, `<Compensation>`) | `cCompensations:` | create, update, delete, upsert (**no** updateWhere) | **FULL.** All 9 corpus attribute names modelled, including `isPublic` and the `<ClassItemBag>` branch | `cCompensations: None`. Correct: no `CCompensation` family exists in the client DataCenter | NO |
| **TerritoryData** (`TerritoryData_<hz>.xml`) | `territories:`, `territorySpawns:`, `territoryGroups:`, `territoryParties:` | all four: create, update, delete, upsert. `territorySpawns:` additionally has updateWhere and **deleteWhere** | **FULL minus one.** 85 of 87 corpus attribute names modelled. `instanceId` is modelled under the alias `npcInstanceId`; only `invincibleVillager` (88 rows) is genuinely absent, and it is absent from `TerritoryData.xsd` too | Synced as `TerritoryData` (426 client shards) | NO |
| **Field / field events** (`FieldData_<continentId>.xml`, `<FieldEvent>`) | `fieldEvents:` | create, update, delete, upsert, updateWhere | **FULL.** 0 of 90 corpus attribute names missing | Synced as `Field` (14 client shards) | NO |
| **FieldEvent config** (`FieldEvent.xml`) | `fieldEventConfig:` | singleton config block, no create/update/delete/upsert verbs | **PARTIAL, trivially.** 36 of 37 modelled; `itemTemplateIdList` on `ShowRewardList` (3 rows) missing | Synced as `FieldEvent` (2 client shards) | NO |
| **StrSheet_Field** | `fieldStrings:` | create, update, upsert, delete | **FULL** (`id`, `string`) | Synced as `StrSheet_Field` (11 client shards) | NO |
| **EventDialog** | `eventDialogs:` | create, update, upsert, delete | **FULL.** All 7 corpus attributes modelled | Synced as `EventDialog` (2 client shards) | NO |
| **StrSheet_EventDialog** | `eventDialogStrings:` | create, update, upsert, delete | **FULL** | Synced as `StrSheet_EventDialog` (2 client shards) | NO |

Sources for the table: operations from
`src\DataSheetLang.Yaml\Deserialization\{Npcs,Ai,NpcSkills,CCompensations,TerritoryArea,TerritorySpawn,TerritoryGroup,TerritoryParty,FieldEvents,FieldStrings,EventDialogs,EventDialogStrings}Section.cs`;
top-level YAML keys from `src\DataSheetLang.Yaml\Deserialization\Spec.cs:112,133,139` and
`Spec.cs:344,368`; sync mapping from
`reforged\tools\migrate\migrate.py` `ENTITY_SYNC_MAP` and `reforged\config\sync-config.yaml`.

Note on the docs: `starlight\src\content\docs\reference\capabilities.mdx` and
`reference\entities.mdx` are both badly stale. `capabilities.mdx` claims only Items,
Equipment and ItemStrings are supported and that filter-based bulk updates are "not
supported yet"; `entities.mdx` omits NPCs, AI, NPC skills, territories and field events
entirely. Neither should be used to answer a capability question. The per-family pages
under `schemas\npcs\`, `schemas\territories\` and `schemas\events\` are the usable docs,
and the schema source is the actual authority.

---

## 2. Blocker list

### 2.1 BLOCKER: new NPC templates never reach the client

`ENTITY_SYNC_MAP` in `reforged\tools\migrate\migrate.py` contains:

```python
"npcs": None,               # NpcData - server-only
"ai": None,                 # AIData - server-only
```

Both comments are wrong as a statement of fact about the client.

- `<client_datacenter>\NpcData\` holds **426 shards**.
- `<client_datacenter>\AIData\` holds **426 shards**.

The client `NpcData` shard is not vestigial. `NpcData-00000.xml` `<Template id="1">`
carries `shapeId="300250"`, `basicActionId="3002500"`, `race="RedCap"`, `scale="0.8"`,
`size="small"`, `speciesId="5"`, `parentId="30025000"` and a `<NamePlate>` block, which is
the data the client needs to render the creature and draw its nameplate. A brand new
template written only to the server side will exist to the server and be unknown to the
client.

Severity split:

- `NpcData` is already registered in `reforged\config\sync-config.yaml` with a complete
  and plausible `ZoneBased` descriptor (`server_pattern: "NpcData_*.xml"`,
  `client_folder: "NpcData"`, `xsd_file: "NpcData/NpcData.xsd"`). Only the `None` in
  `ENTITY_SYNC_MAP` stops the patch pipeline from using it. This is a one-line pipeline
  decision plus a validation run, not missing capability.
- `AIData` is **not present in `sync-config.yaml` at all** (37 entities are registered;
  `AIData` is not among them). There is no descriptor to enable, so the AI client leg
  cannot be synced today even by hand. Whether it needs to be is a separate question: the
  client `AIData` shard is far thinner than the server file (mostly empty elements such as
  `<CounterFlee />`, `<PeaceState />`), so it may be structurally required rather than
  behaviourally load bearing.

Note this is not the E680 shard-insertion case. Guardian Legion targets hunting zones that
already exist (13, 64, 213, 313, 364, 436), so new templates land in existing shards and no
new shard has to be inserted into a sorted layout.

**Verification needed before authoring:** spawn one new template server-side only, deploy,
and observe in game whether the creature renders and nameplates correctly with no client
`NpcData` row. That single test decides whether 2.1 is a hard blocker or a cosmetic one. It
is cheap and should be run first, because it gates the whole authoring wave.

### 2.2 BLOCKER: NpcSkillData cannot express a complete skill

This is the largest genuine schema gap in the set and it is already on file, unresolved.

Measured across 417 `NpcSkillData_*.xml` files, 179,580 `<Skill>` rows: **217 of 400
distinct corpus attribute names have no YAML property**. Twenty five of those sit directly
on `<Skill>` itself:

| Attribute | Corpus rows | Prevalence |
|---|---|---|
| `parentId` | 176,027 | 98.0% |
| `returnAnimSet` | 117,615 | 65.5% |
| `ignoreDefenceRate` | 61,539 | 34.3% |
| `waistAngleIK` | 10,237 | 5.7% |
| `skillDamageType` | 4,878 | 2.7% |
| `breakInvincible` | 2,708 | 1.5% |
| `physicalFactor` / `magicalFactor` | 1,457 each | 0.8% |
| `abnormalityOnShot`, `abnormalityOnShotInvokeTime`, `abnormalityOnShotProb` | 434 each | 0.2% |
| `pvpAtkRate` | 394 | 0.2% |
| `ignoreAttackSpeed` | 322 | 0.2% |

`parentId` at 98% is the headline. Real NPC skills are near-universally derived from a
parent skill template, and the DSL cannot set that link. Proof it exists in real data:
`<server_datasheet>\NpcSkillData_13.xml`, first `<Skill>` element,
`parentId="30070000"`.

The remaining 192 unmodeled names sit in subtrees that ARE structurally modelled, so they
are per-field holes rather than missing structure:

| Subtree of `<Skill>` | Distinct unmodeled attributes |
|---|---|
| `TargetingList` (damage, areas, reactions, effects) | 144 |
| `Action` (stages, animation, camera) | 74 |
| `<Skill>` root | 25 |
| `Projectile` | 8 |
| `ShowTargetingList` | 8 |
| everything else | 31 |

The `Action` subtree is largely client-side presentation (`animRate`, `rootMotionXYRate`,
`readOnlyDuration`, the whole `CameraShake` set) and is a lower priority. The
`TargetingList` subtree is not: it holds hit reaction and damage application. Concrete
example, `Reaction`: the corpus writes `miniRate` (258,592 rows), `basicMotionId` (258,592
rows) and `miniMotionId` (258,592 rows), while
`src\DataSheetLang.Yaml.Contracts\Schemas\Blocks\Skill\ReactionBlock.cs` declares only
`adjForGrade`, `basicIncValue`, `ignoreWalkReachable`, `miniRateLarge`, `miniRateMedium`,
`miniRateSmall` and `direction`. The plain `miniRate` is absent.

This is already filed:

- `docs\dsl-requests\2026-06-15-npcskills-unmodeled-fields.md` plus
  `repro-npcskills-unmodeled-fields.yaml`. **Now FIXED.** Every field in that repro is
  present in the current build: `adjustHeight`
  (`NpcSkillSchema.cs:51`), `aggro.aggroWhenStart` (`Blocks\Skill\AggroBlock.cs`),
  `defence.damageReduceValue` and `defence.successAnimSet` (`DefenceBlock.cs`),
  `drainBack.gaugeToMpRate` (`DrainBackBlock.cs`), `precondition.modeChangeMethod`
  (`PreconditionBlock.cs`), `property.abnormalMultiHitAdjustId` (`PropertyBlock.cs`), and
  the whole `resistance` set (`ResistanceBlock.cs`).
- `docs\dsl-requests\2026-06-15-npcskills-additional-high-prevalence-fields.md` plus
  `repro-npcskills-additional-fields.yaml`. **STILL OPEN.** All four fields in that repro
  are still absent from the schema: `parentId`, `returnAnimSet`, `ignoreDefenceRate`,
  `defence.damageApplyRate`. Grepped across
  `Schemas\NpcSkillSchema.cs` and `Schemas\Blocks\Skill\`: no declaration of any of them.
- `docs\dsl-requests\2026-06-15-npcskills-balanceref-and-field-coverage.md` records its own
  section 1 as resolved and sections 2 and 3 as open. Section 3 is the same set as the
  first bullet above and is now delivered; section 2 (string-typing of bool/int fields) was
  not re-tested in this audit.

Naming note that is not a defect: `NpcData` `HitDropItem/Item/@lootPermession` is misspelled
in the corpus, and the DSL follows the corpus at the XML layer
(`src\DataSheetLang.Core\Data\Npc\NpcHitDropItemItemData.cs:13` `LootPermession`,
`schemas\NpcData.xsd:19`) while exposing the corrected spelling `lootPermission` as the
YAML alias. Correct behaviour, flagged only so it is not mistaken for a gap later.

**Verification needed:** author one throwaway `npcSkills: upsert` for a new skill id on a
scratch datasheet, apply it, and diff the emitted `<Skill>` element against a real
comparable skill. That shows exactly which attributes come out missing and whether the
result is loadable. Do this before committing to a custom skill set for the elite boss.

### 2.3 Minor gap: four AI attributes unauthorable

Measured across 424 `AIData_*.xml` files, 11,749 `<Ai>` rows. Four corpus attribute names
have no property anywhere in the AI YAML surface (`Schemas\AiSchema.cs`,
`Schemas\Blocks\Ai\*.cs`):

| Attribute | Corpus path | Rows |
|---|---|---|
| `motionId` | `/Ai/PeaceState/RandomMove/Social/@motionId` | 26,059 |
| `patternShowTime` | `/Ai/CombatState/Attack/WorkList/Work/@patternShowTime` | 680 |
| `patternGuide` | `/Ai/CombatState/Attack/WorkList/Work/@patternGuide` | 679 |
| `needTarget` | `/Ai/CombatState/Attack/WorkList/Work/@needTarget` | 168 |

All four are declared in `<dsl_repo>\schemas\AIData.xsd`, so the
XML layer knows them; only the YAML authoring layer does not. `patternShowTime` and
`patternGuide` do exist in the YAML layer, but on
`Schemas\Blocks\DungeonData\DungeonEventTaskBlock.cs`, a different entity, which is why a
naive grep makes them look present.

Practical read: `motionId` on `Social` is idle-flavour only. `patternShowTime`,
`patternGuide` and `needTarget` on combat `Work` entries matter for a telegraphed boss
pattern, which is exactly what an elite boss variant would want. Low volume, but on the
critical path for the boss specifically.

### 2.4 Not blockers, recorded so they are not rediscovered

- **NpcData corpus corruption, not schema gaps.** Three attribute names in the corpus have
  no DSL property: `hideQuestIdId` (12 rows, a doubled suffix of `hideQuestId`), `el06ite`
  (2 rows, a corrupted `elite`), and `lootPermession` (handled as described in 2.2). The
  first two are damaged data in the server tree, and modelling them would be wrong.
- **TerritoryData `invincibleVillager`.** Present on 88 `/Territory/**/Npc` rows, absent
  from both the DSL territory surface and `schemas\TerritoryData.xsd`. `NpcSchema.cs` has
  an alias of the same name, but that is the NPC template entity, not a territory spawn.
  Not needed for the described work.
- **`cCompensations:` has no `updateWhere`.** All four of create, update, delete and upsert
  exist, so authoring a loot table for a new monster is unaffected; only filter-based bulk
  retuning across a zone is not available.
- **Loot family placement.** The creature drop family is `CCompensation_<hz>.xml` under
  `CompensationData\`, entity `<Compensation npcTemplateId=... npcName=...>` with nested
  `<ItemBag probability>/<Item templateId min max probability>` and an optional
  `<ClassItemBag>` branch. The DSL models all of it:
  `Schemas\CCompensationSchema.cs` exposes `itemBags` and `classBranches`, and
  `CCompensationItemBlock` carries `TemplateId`, `Name`, `Min`, `Max`, `Probability` and
  `IsPublic`. There is no client `CCompensation` family, so `cCompensations: None` in
  `ENTITY_SYNC_MAP` is correct and is not a quarantine.
- **No precedent in this repo.** Zero specs under `reforged\specs\` currently use `npcs:`,
  `ai:` or `npcSkills:` (grep for `^npcs:`, `^ai:`, `^npcSkills:` returns nothing).
  `cCompensations:` appears in 10 specs, `territorySpawns:` in 7, `fieldEvents:` in 1.
  Everything in 2.1 through 2.3 would therefore be exercised for the first time by this
  authoring wave, with no working example to copy. That is a schedule risk independent of
  any single missing field.
- **No conformance gate outside Quest.** Commit `94f85043` added a corpus conformance gate
  (`schemas\Quest.conformance-contract.json`, 3,839 lines, plus
  `tests\...\Quest\Conformance\`) for the Quest entity only. NPC, AI, NpcSkill and
  FieldEvent have no equivalent, which is precisely why the gaps in 2.2 and 2.3 exist
  undetected. The DSL repo's own
  `.claude\skills\audit-entity-conformance\SKILL.md` (added in `35b4cb8a`) describes the
  method for extending it and names AI, NPC, Skill and FieldEvent as intended targets.

---

## 3. The two open requests

### 3.1 `2026-07-28-continentdata-sync-boolean-case.md`: **FIXED**

Commit `3976613a`, "Match client-sync boolean attributes case-insensitively and report
uncastable values as W603".

Code path, `src\DataSheetLang.Tools\ClientSync\Filtering\XmlFilterer.cs`. The old
conversion was:

```csharp
case XsdType.Boolean:
    return value switch
    {
        "True" or "true" or "1" => ("true", true),
        _ => ("false", true)
    };
```

which is exactly the reported defect: an uppercase `TRUE` falls to the `_` arm and becomes
`false`. It is replaced by a call to a new `NormalizeBoolean(string)` helper that trims,
maps `"1"` and any case-insensitive `"true"` to `"true"`, maps `"0"` and any
case-insensitive `"false"` to `"false"`, returns `("false", true)` for an empty value, and
returns `(value, false)` for anything else so it is rejected rather than defaulted.

Both parts of the request are delivered. Part 1 (case-insensitive parse emitting the
XSD-legal lowercase form) is the helper above. Part 2 (fail loudly rather than default) is
the new `W603` diagnostic, `SyncErrorCodes.FilteredValueTypeMismatch`
(`ClientSync\Core\SyncErrorCodes.cs`), raised through a new `RecordTypeMismatchDrop` path
in `XmlFilterer.cs` that reports the drop under its own code instead of folding it into
`W602`'s stale-schema meaning. The commit's own doc comment names this project's measured
symptom verbatim: 135 continents losing their instanced-space flag, with uppercase `FALSE`
masking the fault. Test coverage added:
`tests\DataSheetLang.Tools.UnitTests\ClientSync\BooleanNormalizationSyncTests.cs` (211
lines) and additions to `XmlFiltererTests.cs` and `XmlFiltererDropDiagnosticTests.cs`.

Behaviour change worth knowing before enabling the sync: an uncastable value is now
**dropped and reported**, not coerced. An attribute that previously came out as a wrong
`false` will now be absent from the client shard. Empty is the deliberate exception and
still maps to `false`.

**Verification we must run.** Per the tracker, an ATTRIBUTE-level diff proving only
continent 13 changed. Concretely:

1. Flip `"continentDatas"` from `None` to `"ContinentData"` in `ENTITY_SYNC_MAP`
   (`reforged\tools\migrate\migrate.py`), which is currently the quarantine.
2. Snapshot the client `ContinentData` shard before the sync.
3. Run the full patch apply and sync as a whole (`python reforged\tools\migrate\migrate.py
   --patch 002`), per the patch application discipline. Do not sync this entity alone.
4. Diff the new shard against the snapshot at attribute granularity, not by line or file
   count. The pass condition is: `isSpecificSpace` unchanged on all 249 continents
   (`true` 135, `false` 27, absent 87, matching the pre-sync client exactly), and the only
   attribute delta anywhere in the family is continent 13's `channelType`.
5. Confirm the run emits no `W603`. A `W603` here would mean some continent carries a
   boolean literal outside `true|false|1|0`, which the old build would have silently turned
   into `false`.
6. Watch for the documented secondary effect, which is **not** fixed and was not claimed to
   be: the sync projects server truth over client drift, so `channelMax` on continents 1,
   2, 3 and 4 will still be rewritten (`10` to `3`, and `10` to `2` on continent 4). Decide
   whether that is acceptable before the run rather than treating it as a regression after.

Only after that diff passes should the `None` quarantine and its comment block in
`migrate.py` be removed.

### 3.2 `2026-07-27-idsorted-server-path-required.md`: **FIXED**, and more than was asked

Commit `b56c21dd`, "Fall back to the server root for IdSorted server_path and refuse
zero-source sync plans".

All three requested changes are delivered, in the requested preference order.

**Preference 1, the documented root fallback.** `SyncOrchestrator.GetIdSortedSources`
(`src\DataSheetLang.Tools\ClientSync\SyncOrchestrator.cs`) previously bailed out with an
empty list whenever `ServerPath` was null or empty:

```csharp
if (string.IsNullOrEmpty(config.ServerPath) || string.IsNullOrEmpty(config.ServerPattern))
    return [];
var dir = Path.Combine(serverRoot, config.ServerPath);
```

It now guards only on `ServerPattern` and falls back to the server root:

```csharp
var dir = string.IsNullOrEmpty(config.ServerPath) ? serverRoot : Path.Combine(serverRoot, config.ServerPath);
```

The commit comment names this project's exact case: the field event
`Field/FieldData_*.xml` set sitting at the datasheet root, planning zero sources and
exiting 0 unless the config spelled out `server_path: "."`.

**Preference 3, the zero-file guard, which the request called the most valuable part.** Two
new mechanisms in `SyncOrchestrator`:

- `GuardEmptySourceSet(...)` runs on the unnarrowed source set and splits on severity. An
  entity named explicitly via `--entities` that resolves zero sources now **throws**
  `SyncConfigException` with the new `E682` (`SyncErrorCodes.SourceSetEmpty`), so the run
  fails instead of reporting success. An entity swept up by `--all` reports the new `W604`
  (`SourceSetEmptyUnderAll`) and the sweep continues. The same guard is applied a second
  time on the segmented path, deliberately measured on the unfiltered corpus so that
  `--segment` / `--filter` / `--from-manifest` narrowing to nothing stays legitimate.
- `WarnOnMissingDeclaredSources(...)` adds `W605` (`DeclaredSourceMissing`) for
  `Bucket` `server_files` entries and `SourceMapped` `source_mapping` keys that name a file
  which does not exist under the server root. This is the second, subtler failure the
  request called out, where a partial miss keeps the plan non-empty so the zero-file guard
  cannot see it, and it should catch this project's `AreaData` `source_mapping` key that
  has been silently missing its subdirectory prefix.

Test coverage: `tests\DataSheetLang.Tools.UnitTests\ClientSync\EmptySourceSetTests.cs`
(221 lines), plus updates to `ZoneBasedPositionGuardTests.cs`.

**Verification we must run.** Two checks, both cheap and both dry-run only:

1. Temporarily remove `server_path: "."` from the `Field` entity in
   `reforged\config\sync-config.yaml` and run
   `dsl sync --config reforged\config\sync-config.yaml -e Field --dry-run --verbose`. It
   must report `Field: 12 sources -> 12 targets`, matching what variant A produced in the
   original repro. Then restore the key or delete it deliberately, and update the comment
   there that records the measurement so a future reader is not misled into thinking the
   workaround is still load bearing.
2. Run a full `--all` dry-run sync and read the warning stream. This is the more valuable
   half: it is the first opportunity to see `W604` and `W605` fire across the whole
   config, and it is the check that should surface the `AreaData` `source_mapping`
   misconfiguration the request predicted. Any `W604` or `W605` in that output is a real
   config fault to fix before the next patch apply, not noise.

Note that `E682` makes a previously silent no-op into a hard failure for any entity named
with `--entities`. That is the intended behaviour, but it means a config that was quietly
broken will now stop a run. Doing check 2 before the next patch apply avoids discovering
that mid-patch.

---

## 4. Other requests possibly resolved by this build

The six commits between `12a24535` and `b56c21dd` are:

| Commit | Subject |
|---|---|
| `b56c21dd` | Fall back to the server root for IdSorted server_path and refuse zero-source sync plans |
| `3976613a` | Match client-sync boolean attributes case-insensitively and report uncastable values as W603 |
| `2a41fa95` | Author hunt task monster lists with per-entry grant rate and kill count |
| `35b4cb8a` | Stop fishing tasks writing elements the corpus never contains |
| `94f85043` | Gate the quest authoring surface against the production corpus |
| `5e35d832` | Link quest error codes and correct the abnormal-state task description |

Cross-referencing every file in `docs\dsl-requests\`:

- **`2026-07-27-hunt-task-multi-target-and-grant-rate.md`: FIXED** by `2a41fa95`. Both
  reported problems are addressed. A new `targets:` list property on
  `Schemas\Blocks\Quest\QuestTaskBodyBlock.cs` takes a
  `List<QuestMonsterTargetBlock>`, and a non-empty list REPLACES the `<몬스터지정>`
  container, so adding and removing entries both work and re-application is idempotent.
  The new `Schemas\Blocks\Quest\QuestMonsterTargetBlock.cs` carries `templateId` (accepting
  either `"huntingZone,template"` or a bare id inheriting the body-level `huntingZoneId`),
  `grantRate` for `수여확률`, and `killCount` for `사냥마리수`. The block's own doc comment
  records that the two are an exact complement by task type, which is why they are separate
  fields. A task type other than HuntTask or HuntAndDeliverTask that is given `targets:`
  is refused with `E212` rather than having it silently dropped. This unblocks the Island
  of Dawn quest-objective tuning for quests 1319 and 1348 that the request said it was
  blocking.
- **`2026-07-19-huntdeliver-monster-target-inplace-update.md`: LIKELY FIXED for the main
  complaint, NOT VERIFIED for the rest.** The reported loss of `<수여확률>` on a
  monster-target update is resolved, because `grantRate` is now authorable on each entry
  rather than depending on preservation. The request also reported that the decompose path
  drops the `<조우시대사>` / `<사망시대사>` / `<이상상태조건>` sub-elements, and nothing in
  the diff of `2a41fa95` visibly addresses those. Since `targets:` REPLACES the container,
  the sub-element question may in fact be sharper now, not softer. **Do not close this
  request without an apply-and-diff on a task that actually carries those sub-elements.**
- **`2026-04-14-sync-xsd-filter-stripping-required-attrs.md`: possibly affected, not
  resolved.** It concerns the XSD filter dropping attributes, and `3976613a` changed how
  `XmlFilterer` classifies and reports drops (splitting `W603` out of `W602`). That is a
  diagnostics improvement, not a fix to what gets stripped. It does mean a re-run will now
  distinguish "client schema does not declare it" from "value is outside the declared
  type's lexical space", which should make the original report easier to re-diagnose.
- **`2026-07-26-zonebased-server-path.md`: already recorded as delivered** in its own
  resolution log dated 2026-07-27, pending a release build. This build is that release
  build, so it can now be verified and closed. `b56c21dd` is the sibling change that
  extends the same `server_path` handling to IdSorted.
- **No fishing-task request exists in `docs\dsl-requests\`.** `35b4cb8a` (the
  `FishingSuccessTask` writing a `<낚시등급>` element the corpus never contains) was found
  by the DSL team's own conformance sweep, not by us. No action needed on our side.
- **`94f85043` and `5e35d832`** are internal quality and documentation work with no
  corresponding request from this project. `94f85043` is worth knowing about anyway: it is
  the conformance gate that will catch this class of defect on Quest going forward, and the
  reason no equivalent protection exists on NPC, AI, NpcSkill or FieldEvent (see 2.4).

Every other file in `docs\dsl-requests\` was checked against the six commit subjects and
none of them are touched by this build.

---

## 5. Recommended order of work

1. Run the 2.1 client-render test first. It is one spawn and one restart, and it decides
   whether the NPC authoring wave needs a pipeline change before it can start at all.
2. Run the two `2026-07-27-idsorted-server-path-required.md` verifications (3.2). Both are
   dry-runs, and the `--all` one may surface pre-existing config faults that would
   otherwise bite mid-patch now that `E682` fails hard.
3. Run the 3.1 ContinentData attribute-level diff and lift the quarantine if it passes.
4. Probe `npcSkills: upsert` on a scratch datasheet (2.2) before committing to a custom
   skill set. If the emitted skill is unusable without `parentId`, the elite boss should
   reuse or clone an existing skill set rather than define a new one, and
   `2026-06-15-npcskills-additional-high-prevalence-fields.md` should be escalated with
   this audit's prevalence numbers attached.
5. NpcData, loot, territory spawns and the field event families are all clear to author
   now. None of them carry a schema blocker.
