# Guardian Legion: Backlog

The register of every unknown, test, failure and attempt in this wave. One row per item, with a
stable id so a later session can say `GL-P07` and mean something.

Seeded 2026-07-28 from the phase A research in `data/`. Nothing here is invented: every row cites
the artifact that raised it.

**Status values.** `OPEN`, `PASS`, `FAIL` (with cause), `FILED` (converted to a DSL or MCP
request), `DEFERRED` (with reason), `BLOCKED` (on another row).

**Rule: failures stay.** A row that failed and why is worth more than a row that passed. Never
delete a row, never overwrite a result. Amend with a dated note.

## Batch 0: no restart required

Answerable at the desk. Drain these before spending a boot. Phase 1 of `PLAN.md`.

| ID | Question or test | Method | Source | Status | Result |
|---|---|---|---|---|---|
| GL-P01 | Is a DSL-emitted `<Skill>` usable without `parentId`? | Was the wave's largest blocker: `parentId` sits on 98.0 percent of 179,580 corpus rows and could not be authored | `dsl-capability-audit.md` 2.2 | **RESOLVED UPSTREAM** 2026-07-28 | Moot. DSL `23ec700a` authors `parentId`, `returnAnimSet`, `ignoreDefenceRate` and `defence.damageApplyRate` on all skill facades, and `13c9fedd` keys NPC skill create/upsert/delete on the composite `(templateId, id)` identity. Verified present in `CommonSkillSchema.cs` and `Blocks/Skill/DefenceBlock.cs`. **The boss can have a bespoke skill set.** Still worth a scratch-datasheet emit-and-diff before committing to one, but it is no longer a design constraint |
| GL-P02 | Do `W604` / `W605` fire anywhere in our sync config? | Full `--all` sync dry-run, read the warning stream | `dsl-capability-audit.md` 3.2 | OPEN | |
| GL-P03 | Does the IdSorted `server_path` root fallback work? | Temporarily remove `server_path: "."` from the `Field` entity, `dsl sync -e Field --dry-run --verbose`, expect `12 sources -> 12 targets` | `dsl-capability-audit.md` 3.2 | OPEN | |
| GL-P04 | Can the `continentDatas` quarantine be lifted? | Lift the `None` in `ENTITY_SYNC_MAP`, full patch apply and sync, ATTRIBUTE-level diff. Pass condition: `isSpecificSpace` unchanged on all 249 continents (true 135, false 27, absent 87) and the only delta anywhere is continent 13's `channelType` | `dsl-capability-audit.md` 3.1 | OPEN | |
| GL-P05 | Do `spawnScriptId="248009998"` and `despawnScriptId="248009999"` resolve? | Check `S1ActionScripts` for both ids before copying them from donor `620,1005`. A dangling action script id is a boot risk | `orcan-npc-donor-survey.md` 3 | OPEN | |
| GL-P06 | Do the formation ids used by donor `87,2031` Cooperation works 3 and 4 exist in `FormationData_13`? | Resolve each referenced id against `FormationData_13.xml`; author them if absent | `orcan-npc-donor-survey.md` 3 | OPEN | |
| GL-P07 | What do `msg` ids `620013` and `703` resolve to? | They live in the client-only `StrSheet_MonsterBehavior`. `620013` is a zone 620 specific line and would put a Veritas District line on Island of Dawn. Decide: author new lines or blank the `msg` attributes | `orcan-npc-donor-survey.md` 3 | OPEN | |
| GL-P08 | MCP `find_free_ids` errors on `entityType: NpcTemplate` | Reproduce, then file in `docs/mcp-requests/` as `2026-07-28-find-free-ids-npctemplate.md`. Id allocation was proven by direct file scan instead, so this is not blocking | `orcan-npc-donor-survey.md` 5 | OPEN | |
| GL-P09 | `StrSheet_Creature` appears in NO sync-config entry | Register a `monolithic` descriptor. The family was already authorable via the `creatureStrings` entity, so only the sync leg was missing | `orcan-npc-donor-survey.md` 4 | **PASS** 2026-07-28 | Registered and synced. All 17,755 rows preserved. Two first-adoption changes, both understood: 3 duplicate `<HuntingZone id="183">` wrappers merged (428 blocks to 426, zero rows lost) and 2 `class="True"` normalized to `true` by the boolean fix in `3976613a`. Second sync writes 0 files, so idempotent. **New monster names now reach the client nameplate.** Blocker cleared |
| GL-P27 | `StrSheet_CollectionLoc` not synced | Register a `monolithic` descriptor; server file already existed because `gen_collectionloc.py` wrote both copies | 2026-07-28 adoption | **PASS** 2026-07-28 | Registered, synced, client byte-identical. Round trip clean on the first try |
| GL-P28 | `StrSheet_NpcLoc` cannot be imported | `dsl import` collapsed the family because it is keyed on the PAIR `(huntingZoneId, templateId)` and `composite_id_attributes` was silently ignored on `monolithic`. Dry-run reported 1018 records from 4101 rows, 3083 duplicates DISAGREEING on content, 75 percent data loss | 2026-07-28 adoption | **PASS** 2026-07-28 | Fixed upstream same day by `48fefbae`, which honors the key on every strategy AND refuses a mass-collapse import. Re-run imported 4101 of 4101, round-tripped byte-stable (sync wrote 0 files), committed as `cdca4fb4` and pushed |
| GL-P29 | No DSL entity for `StrSheet_NpcLoc` or `StrSheet_CollectionLoc` | Import is data-shape only, so an entity is still needed to author rows | 2026-07-28 adoption | **PASS** 2026-07-28 | Delivered by `530f0038`: entities `npcLocStrings` and `collectionLocStrings`, both with create/update/delete/upsert, NpcLoc addressed by the pair. `gen_npcloc.py` retargeted to emit a spec; patch 002 now carries `36-iod-npcloc-registry.yaml` (146 upserts) and the registry is reproducible by a patch apply for the first time |
| GL-P10 | `AIData` is absent from sync-config and mapped `ai: None` | The client DC has 426 `AIData` shards. Determine whether the client copy is load bearing or structural. There is no descriptor to enable, so this cannot be synced today even by hand | `dsl-capability-audit.md` 2.1, `orcan-npc-donor-survey.md` 4 | OPEN | |

## Batch 1: restart 1, monster authoring

Phase 2 and 3 of `PLAN.md`. `GL-P11` is the gate for the entire authoring wave and should be first
on the boot.

| ID | Question or test | Method | Source | Status | Result |
|---|---|---|---|---|---|
| GL-P11 | Does a server-only NPC template render on the client? | Author one throwaway template plus its `StrSheet_Creature` name, deploy with NO client `NpcData` row, restart, spawn it, observe. This single test decides whether the `npcs: None` / `ai: None` mapping is a hard blocker or cosmetic | `dsl-capability-audit.md` 2.1 | OPEN | |
| GL-P12 | Does an authored template fight and use its own skills? | `/@spawnnpc 13 <tpl> 1`, engage, observe at least one skill from its own `NpcSkillData_13` rows | `PLAN.md` phase 2 gate | OPEN | |
| GL-P13 | Does `scale="0.41"` read as elite, and what `nameplateHeight` does it need? | No zone 620 template carries `nameplateHeight`, so it must be derived. Zone 13 Orcans are 18 at scale 0.17; `1022,203` is 30 at scale 0.30, roughly 100 units per unit of scale, so 0.41 wants 41 to 45. Confirm in game | `orcan-npc-donor-survey.md` 6 | OPEN | |
| GL-P14 | Does an authored template drop its own loot? | Author a `cCompensations` / `eCompensations` entry keyed on the new `npcTemplateId`, kill it, confirm the drop | `orcan-npc-donor-survey.md` 7 | OPEN | |

## Batch 2: restart 2, field event mechanics

Phase 4 of `PLAN.md`. A disposable probe event answers most of these in one boot. All twelve come
from `fieldevent-multiphase-reference.md` section 6, where each carries a suggested probe.

| ID | Question or test | Why the data cannot answer it | Status | Result |
|---|---|---|---|---|
| GL-P15 | Is `value` on `progressType="basic"` a segment budget, a cap, or an absolute set of the bar? | Only 2 uses corpus-wide, both in the escort, both at points where budget and absolute-set give the same number. The readings are indistinguishable | OPEN | |
| GL-P16 | Is there an upper bound on `Point value`? | Shipped domain is 0.24 to 1.6. Calibration needs roughly 2900, three orders outside anything attested. No evidence of a cap, none against one | OPEN | |
| GL-P17 | What is the tick period of `checkTerritory` scoring? | Declared globally with `defaultRate="1.0"` but used by zero shipped events | OPEN | |
| GL-P18 | Does `endWhenProgressFull="true"` work? | All 16 shipped events set it `false` | OPEN | |
| GL-P19 | Does a `killCount` group fire once per integer in `min`..`max`? | Inferred from arithmetic across four counters in two files, four for four. Strong but indirect, and the whole progress ladder rests on it | OPEN | |
| GL-P20 | Does `killCount` count any player's kill, or only the killer's party? | No attribute distinguishes them, no comment addresses it | OPEN | |
| GL-P21 | Does `userCountInTerritory` re-fire when the count drops and rises again? | `repeat` is absent on all 18 shipped uses, so the default is unobserved. Our staging gates depend on it | OPEN | |
| GL-P22 | Do `changePos method="start"` and `revive` affect players already inside the event? | Never stated. The escort's design implies "everyone from now on", but joiners and corpses are different cases | OPEN | |
| GL-P23 | Is `dividerPercent` genuinely cosmetic at runtime? | Evidence is strong (event 7001 has 13 progress triggers and no `dividerPercent` at all) but it is one event | OPEN | |
| GL-P24 | Does `abnormality turn="off"` work? | Zero uses corpus-wide; all 55 are `turn="on"` | OPEN | |
| GL-P25 | What distinguishes `FieldEvent type="0"` from `type="1"`? | 3 uses, no behavioural correlate visible. Low priority | OPEN | |
| GL-P26 | Does `changeHp` support anything other than `method="rate"`? | All 416 uses are `rate` | DEFERRED | Not needed for the three-phase design |

## Decisions

Design rulings, with the reason. A ruling recorded here that changes shipped content also needs an
AUTHORED row in `../divergence-log.md`.

| ID | Decision | Options | Ruled | Date |
|---|---|---|---|---|
| GL-D01 | Do the event mobs carry kill loot? | Shipped GL missions pay ONLY through the event reward system; zone 620 has no compensation file at all. Giving our mobs loot tables is a deliberate divergence from how the publisher built this content type | OPEN | |
| GL-D02 | Reward coefficient target | How many kills should one participation bag cost? Drives the `Point value`: about 2900 for 50 kills, 1450 for 100 | OPEN | |
| GL-D03 | Lore framing | (a) Ayrdoss's "continuously reinforcing from somewhere", canon's largest deliberately open hook, which justifies a RECURRING event with zero invention. (b) The plainer "raiding the camp" premise, which is a one-off | OPEN | |
| GL-D04 | Boss identity | Canon never says who leads the Black Claw after Acharak dies. Clean authoring space. Note no Orcan speaks a single line in any era on any continent, so giving him dialogue invents the species' voice | OPEN | |
| GL-D05 | Boss scale | `0.41` is the largest the publisher shipped on an elite GL Orcan, 2.41x the Orcans beside it. `0.6` is the only larger attested value for the shape and is the ceiling | OPEN | |
| GL-D06 | Tribe name in English | Korean is 검은 발톱 in both places. English localisation says "Dark Claw" on the island and "Black Claw" on the mainland. Pick one and say why | OPEN | |

## Attempt log

Dated narrative of what was tried and what happened, including dead ends. This is the part that
stops a future session repeating a failure.

### 2026-07-28: v0 lifecycle probe (pre-dates this register)

Carried over from `../TRACKER.md` because it is the wave's first entry. The v0 event was
structurally perfect and did nothing for two restarts. Cause: a field event will not run on a
continent that is not `channelType="field"`, and continent 13 was `channelingZone`.

It was documented in two places we already had and both reads went around it. The
`ContinentData.xml` header comment defines the attribute, missed because every inspection used
Python ElementTree, which discards comments and the file has 162 of them. The domain KB's own
`field-event-system.md` listed it under "What Starts an Event", missed because the search covered
adjacent docs instead of the system's primary doc.

What isolated it in one step was a **control test**: running a shipped event (`/@startfe 7014 2`)
in the same session with the same commands. It started and teleported correctly while `13/1` did
nothing, which localised the fault to our continent immediately.

Both lessons are now in the skills. The standing instruction: run the nearest shipped example as a
control BEFORE changing any data or spending a restart.

### 2026-07-28: phase A research

Four parallel agents produced `data/dsl-capability-audit.md`, `data/orcan-lore.md`,
`data/fieldevent-multiphase-reference.md` and `data/orcan-npc-donor-survey.md`. No failures. The
register above is the seeded output.

One incidental fix during scaffolding: the four reports were written with 36 machine-absolute
paths, including a `Z:` network drive. This repo is public and CLAUDE.md forbids literal
environment paths in tracked docs, so they were rewritten to `.references` key tokens. Verified 0
remaining.

### 2026-07-28: the client-write defect, found by accident and fixed end to end

Moving the GL specs out of patch 002 required a full revert and replay. The replay reported 76
applied, 0 failed, 0 warnings, and had **silently dropped the `StrSheet_NpcLoc` registry**. Found
only by diffing the stash against the working tree afterward: 16 files were dirty before and clean
after, 15 of them correct GL removals and one that was not.

Root cause: `gen_npcloc.py` wrote the CLIENT DataCenter directly. A patch replay regenerates the
server tree and syncs it; it cannot regenerate something that was never server-side, and a stash
of the client tree discards it with nothing reporting the loss.

Two false starts worth recording, both my own measurement errors, both caught before they misled a
decision:

1. A stash-vs-working-tree comparison reported "4971 files lost" because `git stash show` lists
   repo-root-relative paths while `git status` from a subdirectory lists cwd-relative ones, so
   nothing matched. The real answer was 16.
2. A `git show HEAD:StrSheet_CollectionLoc.xml` returned 200 bytes against a 94,598 byte working
   file that git called CLEAN, which is impossible. Same class of error: `git show HEAD:<path>` is
   always repo-root-relative, and the file lives under `Datasheet/`. Corrected, it showed all 8
   continent-13 collections already present at HEAD.

**Lesson: when a git path comparison produces an impossible number, suspect the path convention
before believing the result.** Both mistakes produced plausible-looking output.

The fix chain: import the family to the server, register the sync descriptor, map the key in
`ENTITY_SYNC_MAP` (which is silently skipped otherwise), retarget the generator to emit a spec,
and commit the canonical baseline so `--source-ref` can see it. All four steps are required; any
one omitted leaves the family broken in a different way.
