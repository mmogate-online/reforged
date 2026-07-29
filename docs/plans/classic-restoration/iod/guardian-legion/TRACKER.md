# Guardian Legion: Tracker

Volatile. Rewritten every session. Narrative belongs in `BACKLOG.md`, not here.

Companion documents: `PLAN.md` (phases and gates, stable), `BACKLOG.md` (every test, failure and
decision), `data/` (frozen research, do not edit).

## You are here

| | |
|---|---|
| **Patch** | 003, scaffolded, zero specs authored |
| **Current phase** | 0, scaffold. Complete at session end 2026-07-28 |
| **Last gate passed** | Phase 0 |
| **Next action** | Phase 1, batch 0 of `BACKLOG.md`. `GL-P01` is now RESOLVED upstream, so start with `GL-P11`, the server-only NPC render probe, which is the one that still needs a restart |
| **Blocked on** | **Patch 002 must be closed first.** It is open, carries seven unvalidated trim specs (`002/27` to `002/33`), and patch 003 develops against its committed baseline |
| **Open decisions** | `GL-D01` to `GL-D06` in `BACKLOG.md`. None ruled |
| **Restarts spent this wave** | 2, both on the v0 lifecycle probe |

### Blockers cleared since the plan was written

All three NPC-authoring blockers are gone, all resolved upstream by the DSL team on 2026-07-28:

| Was | Now |
|---|---|
| `npcSkills:` could not author `parentId` (98.0 percent of 179,580 corpus rows) | Delivered by `23ec700a` plus `13c9fedd`. **The boss can have a bespoke skill set** |
| `StrSheet_Creature` had no sync descriptor, so authored names never reached the client nameplate | Registered and synced. `GL-P09` PASS |
| `npcs`/`ai` mapped `None` in `ENTITY_SYNC_MAP` | Still open as `GL-P11`, the render probe. This is the only NPC blocker left and it needs one restart |

## What is live today

**Nothing.** Guardian Legion content was REMOVED from the deployed environment on 2026-07-28 so
patch 002 could close on a clean baseline.

**Guardian Legion v0** was live-validated earlier the same day and the approach is proven:
deliberately not content, one npc spawns, the progress bar is bound to its HP, killing it
completes the mission. It proved the lifecycle end to end and nothing more.

Its two specs moved to patch 003 as `003/10-iod-field-event-continent.yaml` and
`003/11-iod-guardian-legion-v0.yaml`. `packages/fieldevent` (22 definitions) stays registered in
`datasheetlang.yml` and is untracked in the specs repo.

### The revert, done 2026-07-28

| Step | Result |
|---|---|
| GL specs moved out of patch 002 | 002 now ends at `33` |
| Dev overlay reverted (`deploy_dev.py --revert --yes`) | Required, not optional: the deploy tool mirrors only git-dirty files, so `FieldData_13.xml` would have stayed stale on the box after local removal |
| Both datasheet repos stashed with `-u` | `stash@{0}` on each, labelled `2026-07-28 pre-GL-move patch 002 + GL v0 working tree`. Recoverable, nothing hard deleted |
| Patch 002 replayed `--no-narrow` | 76 specs, 9195 ops, 0 failed, 0 warnings. Full sync because 002 adds new `Quest` and `QuestDialog` shards (1353-1358, 1380, 1381, 1387) |
| Verified | `FieldData_13.xml` absent, continent 13 back to `channelingZone`, client `Field` back to 12 shards |
| Redeployed | Server 78 files copied and hash-verified; client packed and installed, packed and installed `.dat` hash identical |

**Carried forward deliberately:** `StrSheet_Field.xml` (214 rows) and `EventDialog.xml` (159 rows)
remain COMMITTED in the server datasheet repo at `7b5e4092`. Both were added by that commit and
are absent at its parent, so they arrived during GL work. They are left in place because that
commit is what made patch 002 replayable at all, and reverting it would break patch 003
reproducibility later. They are inert for patch 002: no spec touches them, they are clean rather
than dirty, so `deploy_dev.py` does not push them and the dev box does not have them. The box is
therefore in its true pre-GL state.

## Proven facts, do not re-derive

| Fact | Established by |
|---|---|
| A field event will not run on a continent that is not `channelType="field"` | v0, cost 2 restarts |
| A dedicated mission hunting zone is NOT required. Ours runs in live world HZ 13 | v0, contradicts all 12 shipped events |
| Event territories must be `type="quest"`. A `normal` one spawns at world start and leaks into the live world permanently | v0 |
| The world server emits NO runtime field event logging. Log silence proves nothing | v0 |
| Adding a `FieldData` file inserts a shard into an IdSorted layout, and continent 13 sorts FIRST, shifting all 12 existing shards. That patch MUST sync `--no-narrow` or it fails E680 | v0 |
| There is no phase element. Phases are an emergent progress-ladder idiom | `data/fieldevent-multiphase-reference.md` |
| A global `EventPoint defaultRate="0.001"` multiplies every event, so `healing` scores literally nothing anywhere | same |
| Shipped GL missions have no kill loot at all. Zone 620 has no compensation file in existence | `data/orcan-npc-donor-survey.md` |
| GM kit: `/@startfe <cont> <ev>`, `/@gotofe <cont> <ev>` (both args required on both), `/@showfeinfo on`, `/@showfeprogress`, `/@setfeprogress`, `/@endfe`, `/@ferotation on off` | v0 |
| Run a SHIPPED event as a control before changing authored data | v0, isolated the blocker in one step |

## Design brief

Premise, pending `GL-D03`: the Orcans have been raiding the camp and the garrison moves to end it.
Three phases, each advancing the staging point toward the Orcan camp.

| Phase | Content | Position | Section |
|---|---|---|---|
| 1 | Swarm of Dwarf Orcans, minion type | `51930, -81192, -4534` | 13003 Mysterious Ruins |
| 2 | Orcan Raiders, many of them | `51290, -78824, -4733` | 13003 Mysterious Ruins |
| 3 | Orcan boss, elite variant | `50107, -77786, -4742` | 13008 **Orcan Bivouac** |

User constraints: new templates only, no reuse of existing Island of Dawn Orcans, because the
event mobs need their own loot and their own power tuning. The boss is an elite variant, visibly
bigger, donated from an existing NPC with richer AI. Not overly complex, but engaging: sequencing
and lore over mechanical depth. Validate each mob individually before wiring the event.

## Blockers carried into phase 1

| # | Blocker | Register row |
|---|---|---|
| 1 | `ENTITY_SYNC_MAP` maps `npcs: None` and `ai: None`, but the client DC holds 426 shards of each. A new template written server-only may be unknown to the client | `GL-P11` |
| 2 | `StrSheet_Creature` is in NO sync-config entry at all, so a new creature name lands server-only and the nameplate has nothing to draw | `GL-P09` |
| 3 | `npcSkills:` cannot express `parentId` (98.0 percent of 179,580 corpus rows), `returnAnimSet` (65.5), `ignoreDefenceRate` (34.3), or `Reaction/@miniRate`. Skill rows are keyed `(hz, templateId, id)`, so a zone 13 template must have its own rows and cannot point at zone 620's | `GL-P01` |

Filed and still open upstream: `docs/dsl-requests/2026-06-15-npcskills-additional-high-prevalence-fields.md`.
Its sibling request was delivered in build `b56c21dd`; this one was not.

Minor: four AI attributes unauthorable (`motionId`, `patternShowTime`, `patternGuide`,
`needTarget`). The last three are the telegraphed-boss-pattern fields, so they sit on the phase 3
critical path specifically.

Schedule risk independent of any field: **zero specs in this repo have ever used `npcs:`, `ai:` or
`npcSkills:`.** This wave exercises all three for the first time with no working example to copy.

## Session log

Keep to one short entry per session. Detail goes in `BACKLOG.md`.

### 2026-07-28, session 7

DSL binary moved to `1.0.0+b56c21dd` from `1.0.0+12a24535`. **Both open DSL requests confirmed
fixed**: ContinentData boolean case by `3976613a` (plus a new W603 that drops and reports rather
than coercing), IdSorted `server_path` by `b56c21dd` (which also added E682, W604 and W605).

Phase A research ran on four fronts and landed four reports in `data/`. Headline find: the boss
donor is `620,1005`, the publisher's own Guardian Legion mission Orcan, the only same-model
creature in the corpus that is `elite="True"`, `size="large"` and carrying a field event authored
skill (`1303`, the telegraphed alarm bomb), already wired as a GL objective in `FieldData_7015`.

Three new blockers found, all in the NPC authoring surface, none in the field event surface.

Decided to develop Guardian Legion as **patch 003** against a closed 002 baseline rather than
piling a first-of-its-kind authoring wave onto an open patch carrying seven unvalidated specs.
Scaffolded patch 003 and this plan folder.

The session then turned into a pipeline cleanup, because reverting patch 002 to move the GL specs
exposed a real defect: the replay silently dropped the `StrSheet_NpcLoc` registry while migrate
reported 0 failed and 0 warnings. Root cause was a tool writing the CLIENT DataCenter directly,
putting its output in the one tree a patch replay cannot reproduce.

Resolved end to end in this session:

- Patch 002 reverted (both repos stashed with `-u`, dev overlay reverted) and replayed clean, GL
  content removed. Specs moved to `003/10` and `003/11`.
- Three client-only families adopted: `StrSheet_Creature`, `StrSheet_CollectionLoc` and
  `StrSheet_NpcLoc` (the last imported with `dsl import`, 4101 of 4101 rows, round-tripped
  byte-stable, committed alone as `cdca4fb4` and pushed).
- `gen_npcloc.py` and `gen_collectionloc.py` retargeted to emit SPECS. Neither writes any
  datasheet now. Patch 002 carries `36-iod-npcloc-registry.yaml` (146 upserts) and the registry
  is reproducible by a patch apply for the first time.
- Loc waypoints authored in the typed `continent` + `markers` form, proven a pure no-op against
  the raw-string result (identical SHA256).
- Two DSL requests filed and both delivered the same day, plus the NpcSkillData request that had
  been open since 2026-06-15.

Next session: user validates and closes patch 002. Nothing in patch 003 has been applied.
