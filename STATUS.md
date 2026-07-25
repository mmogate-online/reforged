# Reforged Server Content — Status

_Last updated: 2026-07-25_

---

## Island of Dawn Migration ✅

Restores IoD as the new-character starting zone (replaces Stepstone Isle). Pre-requisite for all patch content.

| Phase | Status | Notes |
|-------|--------|-------|
| Assessment | ✅ | Zones, files, tooling gaps documented |
| Phase 0 — Revert | ✅ | 49 server + 45 client DC files reverted |
| Phase 1 — Server zone files | ✅ | 34 copied + 8 emptied; zone 436 added (8 files + 3 VillagerData) |
| Phase 2 — Server monolithic merges | ✅ | 65 quests, loot, NPC behavioral files, string tables |
| Phase 3 — Client DC migration | ✅ | Quest shards, zone NPC/TerritoryData via DSL sync |
| Phase 4 — Validation | ✅ | MCP audit: 65/65 quests, 72/72 reward items, all NPC templates match v31 |

**Patch 000 specs — all applied and in-game validated ✅**
- `00-iod-training-bomb.yaml` — item 5002 itemUseCount unlimited ✅
- `01-iod-garrison-quest.yaml` — quest 1384 task chain v92 compatible ✅
- `02-iod-skill-quest-strings.yaml` — skill name strings corrected (5 classes) ✅
- `03-iod-skill-quest-conditions.yaml` — skill ID conditions corrected (5 classes) ✅
- `04-iod-garrison-dialog.yaml` — garrison dialog revamped ✅
- `05-iod-gathering-nodes.yaml` — gathering nodes restored ✅
- `06-iod-teleport-scroll-coordinates.yaml` — teleport coordinates confirmed in-game ✅
- `07-iod-teleport-scroll-strings.yaml` — item 133 name/tooltip restored ✅

**Deferred (post-migration, not blocking launch):**
- Dangling IoD quest chain connections → smooth out via DSL
- DynamicGeoData zone 416 (dungeon doors/elevators — client-only data, server source missing)

---

## Patch 001: IoD v31 Baseline ✅ (redone under the v31-primary doctrine)

Baseline patch: Island of Dawn ported 1:1 from v31 per `docs/plans/classic-restoration/DOCTRINE.md` (v31-primary; v17.11 is a padding-phase research index only). Tracker: `docs/plans/classic-restoration/iod/TRACKER.md`. The earlier v17-north-star pilot (19 specs) was retired 2026-07-20; its salvageable specs carried over.

| Phase | Status | Notes |
|-------|--------|-------|
| 0-2 (Doctrine, salvage, three-surface revert) | ✅ | DOCTRINE.md adopted; salvage manifest (7 carry-over / 9 rework / 3 retire); server+client repos stashed clean, dev overlay reset |
| 3 (v31-vs-v92 diffs) | ✅ | Per-family artifacts with per-row dispositions in `docs/plans/classic-restoration/iod/data/`. Spawns: v92 IDENTICAL to v31 (no spec needed). Quests: spine/headers/story-groups MATCH; rewards 100% empty stubs (ported) |
| 4 (Spec authoring) | ✅ | 13 specs / 1573 ops: sections, region strings, worldmap, shops, rewards + carry-overs (legacy strings, stepstone disable, villager dialogs, charms x3, item strings) + T-cat removal. No spawn/enable/task/story-group specs needed |
| 5 (Apply + verify + deploy) | ✅ | Migrate batch, 8-check reconciliation gate PASS (caught + fixed a reward class-row collapse pre-deploy), NpcLoc regenerated (fence-centroid fix for pos-0,0,0 mobs), server push verified, client dev.23 |
| 6 (Live validation + baseline commit) | ✅ | Story spine validated end to end by user (level 1-10, pacing confirmed). Committed: server `c59c18ff`, client `43bedc3a` |
| Alpha boundary (spec 13) | ✅ | Quest 1317 ends at Leiyane with reward, task 4 removed, Pegasus menu deleted; committed server `4579d3f9` / client `32ed6274` |
| 7 (v17 padding phase, Levels 1-2) | ✅ | LEVEL 1 (specs 14-20): 34 quests enabled, 19 habitat groups (Mysterious Ruins ecology restored), 6 quest givers placed from v17 NpcLoc markers, Sorcha dungeon 437 reclaimed + 9037 live-completed (commit `b2ae08fa`; dungeon_audit.py gate), per-class reward rows fixed, v31 ECompensation drop table restored. LEVEL 2 (specs 21-22, Berlon crafting chain 1353-1358): 6 authored one-time quests (gather then craft via recipes 91213/91221/91282; material give-back so craft is pure crafting; reward returns 2 potions / 1 scroll), recipe designs 91213/91221/91282 + consumables 6000/6001/6016/6017/6197 restored to v31, gather-node map markers authored (`gen_collectionloc.py`). Live-validated end to end. PATCH 001 CLOSED: committed locally on server/client/specs repos (not pushed), client published dev.33; all DSL requests delivered and adopted natively (pipeline fixup-free) |

**Divergence log:** `docs/plans/classic-restoration/iod/divergence-log.md` (adaptations, policy divergences, Level 2 authored quests + restoration entries). **Open DSL requests from the redo:** newWorldMap section-level delete; VillagerDialog client sync (both low priority, hand-managed meanwhile). Client-only families stay tool-managed: StrSheet_NpcLoc (`gen_npcloc.py --prune`), StrSheet_CollectionLoc (`gen_collectionloc.py`), MapDefineData. **Next (LEVEL2-ROADMAP.md):** bump patch 002 to 003, open patch 002 for follow-up Level 2 contextual additions, pacing review of the new XP sources.

---

## Patch 002 Content 🔄 (formerly patch 001)

Custom content layer; specs in `specs/patches/002/`. Applies on top of the committed patch-001 restoration baseline. **IoD loot rebased 2026-07-22:** `17-iod-loot` now merges v31 gold + classic drops with the reforged drops (specs `19`/`21`/`22` deleted); the full patch 002 was applied + deployed to dev for a pending live test (uncommitted test state). See the session handoff in `docs/plans/classic-restoration/iod/TRACKER.md`.

| System | Status | Notes |
|--------|--------|-------|
| Gear progression pipeline | ✅ | Starter 0 → Frostfire → Flawless → potential unlock scroll |
| Enchant materials | ✅ | Probability tables + item links |
| Gear infusion | ✅ | Passivities, items, loot tables |
| Dyad crystal system | ✅ | 1182 crystals across 6 tiers, per-type passivity configs |
| Infusion loot | ✅ | Zone loot distribution strategy implemented |
| Zone loot overhaul | ✅ | All patch 001 open-world zones + dungeons |
| Dungeon tokens + shop chain | ✅ | MedalStore VillagerMenuItem→BuyMenuList→BuyList wiring |
| Equipment standardization via `equipment-item-standard` | ✅ | Package is authoritative baseline for all gear (HIGH/MID/LOW × weapon/chest/hand/boot + class-specific chest & class-restricted weapons); `01-armor-standardize.yaml` and `01-weapon-standardize.yaml` sweep via `$extends` into package definitions; redundant specs retired (`03-flawless-standardize`, `03-chest-toproll-items`, `07-gear-enchant-sync`) |
| Potential unlock generator on package | ✅ | `tools/potential-unlock/generate_potential_unlock.py` emits `$extends`-based specs referencing `equipment-item-standard`; `12-potential-unlock-gear.yaml` reduced 5333→2788 lines |
| EquipmentInheritance compatibility | ✅ | 0 mismatches across all 582 pairs / 53 tokens — server loads with all changes applied |
| IoD NPC balance | ✅ | Normal monsters: maxHp ×10, atk ×60 (retuned above gear-formula neutral for dodge-teaching difficulty); spec applied via migrate |
| Full patch 001 validation | 🔄 | Fresh re-apply deployed to dev server 2026-07-17 (52 files verified, loaded live); in-game validation in progress |
| IoD alpha content loop | ✅ | Superseded by the v31-primary baseline (see Patch 001 section above; baseline committed `c59c18ff`). Patch 002 rebase onto the new baseline still pending. New tracker: `docs/plans/classic-restoration/iod/TRACKER.md` |
| IoD restoration tooling | ✅ | `tools/dc-restore/` (survey, dcq, audit_quests, quest_restore, comp_restore, spawn_restore, dungeon_audit, audit_class_gates) + `tools/deploy-client/` (pack/install/CF-publish; syncing is migrate's job); `content-restoration` skill documents the workflow, `quest-live-test` skill documents live quest verification, `server-load-diagnosis` skill documents world-server load-failure forensics. Two pre-deploy gates are binding: `dungeon_audit.py --dungeons` for dungeon restores and `audit_class_gates.py --zones` for any restored quests |
| Sorcha dungeon 9037 as a party encounter (specs 22-25 + balance) | 🔄 | **Applied and deployed 2026-07-25; live-tuned over three passes, final tuning awaiting confirmation.** Opened to a party of five by restoring v31's `party=1` + `maxMemberCount=5` (spec 22, retiring a patch-001 divergence) and clearing `partyCantWork="true"` from entrance WorkObject 134 (spec 23), which had been inherited from cloning the level-65 donor and blocked grouped players with no server-side counterpart in the client. Encounter rebuilt: waves at v31 x100 HP / x600 atk, effective population 314 → 834 across 50 spawn tasks, Sorcha 1,082,344 hp. 23 dormant wave territories wired (both stage-rear groups plus all of stage 3, 10 → 25 stage-3 spawn points), every insert splitting an existing delay so the chain still fits the 420s guard. New generator `gen_sorcha_wave_density.py` (per-stage factors, baselines from git HEAD) and package `npc-ids/zone-437-tainted-gorge-bridge.yml`. **Open caveat:** tuned for geared test characters, so a level 8-10 player on quest 1346 cannot clear it; needs a difficulty mode or level scaling before launch |
| IoD spawn clarity (spec 21) | ✅ | **Applied, deployed and live-validated 2026-07-25.** Quest 1309 "Acharak Attacks" is a kill-one on named boss 13,1002, but the patch-001 padding wave drew that template from the v17 roster `[5, 901, 1002]` into habitat group 1300038, spawning 8 mobs that display as "Acharak" in the Mysterious Ruins, ~19,400 units from the Tainted Gorge Garrison the quest names. Spec `21-iod-acharak-ruins-cleanup.yaml` retargets those 4 spawns to generic template 901 (same shapeId/basicActionId/aiid, so density and appearance are preserved), restoring the v31 footprint; `gen_npcloc.py --prune` returned the 13/1002 map marker to 2 garrison waypoints. Client published `0.1.0-dev.36`. Side effect accepted: the first full `TerritoryData` client sync rewrote 409 shards (368 reorder-only, 41 with content), closing standing server-to-client gaps including dungeon 437's 63 territories |
| New-class story spine (specs 18 + 19) | ✅ | **Fully generated from specs, deployed, and Ninja live-validated end to end 2026-07-25.** Spec 18 (training quests) regenerated by the fixed DSL: acceptance diff vs the hand-repaired oracle passed at 14 missing / 0 extra on all three quests, all four loader-dereferenced entry children present, empty `<다음Task />` terminator. Spec 19 then closed a second soft-lock one chain later: the class-split pair 1382/1383 admitted only the classic nine, so a Ninja cleared 1384 and stalled before 1331; the physical variant of each affected group (1382, 1351, Velika 6306) now admits Ninja/Brawler/Valkyrie plus Gunner. Client published `0.1.0-dev.35`. Brawler, Valkyrie, and the wrong-class negative case remain unwalked (structurally identical files) |

**In scope (patch 002 zones, see `docs/patch-002-scope.md`):** Fey Forest (2), Oblivion Woods (3), Tuwangi Mire (5), Valley of Titans (6), Celestial Hills (7), Cliffs of Insanity (15), Vale of the Fang (16), Paraanon Ravine (17), Crescentia (59), Lumbertown (60), Velika (63), Bastion of Lok (487), Sinestral Manor (488), Island of Dawn (13), Karascha's Lair (436).

---

## Infrastructure

### DataSheetLang (DSL CLI)

| Capability | Status |
|-----------|--------|
| Manifest-narrowed apply→sync (`--manifest-out` / `--from-manifest`) | ✅ All strategies fixed (Monolithic, SourceMapped, ZoneBased, IdSorted, Bucket, Segmented) |
| SkillData segmented sync | ✅ XSD-driven class filter, orphan deletion gating |
| `commonSkills` Effect-level Teleport (`recallPos`, `recallContinent`) | ✅ |
| `Create*EntryCommand` idempotency (no empty placeholder appends) | ✅ |
| CollectionTerritories nested collection update/delete | ✅ |
| Quest system partial updates (tasks, dialogs, conditions) | ✅ (multiple fixes across Apr 14–21) |
| `dsl apply` CRLF line endings fix (e86a42d) | ✅ Validated |
| `dsl apply` indentation preservation (e86a42d) | ✅ Validated |
| SkillData sync float normalization (8db859c) | ✅ Validated — `100.000000` → `100` |
| SkillData sync user shard idempotency (8db859c) | ✅ Validated — shards 000–118 stable |
| SkillData sync NPC shard idempotency (29137ed) | ✅ Validated — 536/536 unchanged on second sync |
| `dsl apply` UTF-8 BOM preservation (5427ba1) | ✅ Validated |
| SkillData sync attribute ordering | ✅ XSD attribute-order feature reverted upstream (ab41f20); source-order pass-through restored; one-time reformat diff expected on first sync per entity |
| Float precision in `dsl apply` | ✅ Capped to 8 decimal places (92fa465) |
| Monolithic sync `merge: merge-by-id` (client-only record preservation) | ✅ Validated (4b1c61b7): NewWorldMapData entity live with `merge_key_attributes: [id, nameId]`, lossless + idempotent |
| SourceMapped sync `merge: shard-routed` (monolithic server file -> per-record client shards) | ✅ Validated (8a3d89ab): StrSheet_Quest entity live; 8 strings routed to 2 of 2879 shards, multi-owner records updated in every owner, idempotent |
| Quest header elements (`startItems` + 9 others previously unconsumed) | ✅ Validated (84d5ded8): `header.startItems` list-replace, `[]` clears, XSD cap 6; residual `추가보상` ExtraReward still unwired (no content case) |
| Quest class gate (`requirements.classes`) | ✅ Validated (1c31ff16): writes the `<클래스>` block under 수행조건; client sync additionally needs the client Quest.xsd widened to 13 classes (done, client `09ea033f`) |
| Quest creation structural completeness | ✅ Verified against released binary `1.0.0+5f90181c` (2026-07-25): entry children scaffolded on all 22 repeated-entry containers from a mechanically derived contract (`a59caf4e`), quest/task header skeletons, VisitTask completion-item bags, empty `<다음Task />` terminator, in-place visit-target update, E427 apply-time element-name check. Residual: create-path element order at 3 sites (`2026-07-25-created-quest-element-order.md`) |
| Package-internal variable scope at export | ✅ Variables resolved at export time — consumers no longer re-import package-internal vars |

**Open DSL requests:** ~28 filed in `docs/dsl-requests/`. Key pending items:
- ~~Multi-spec in-memory cache E422~~ — resolved in DSL commit `2278066c`; `migrate.py` switched to batch apply
- ~~Quest creation structural completeness (was BLOCKER for patch 002 re-apply)~~: delivered and verified 2026-07-25; 7 quest requests closed and deleted. Residual: `2026-07-25-created-quest-element-order.md` (create-path child order at 3 sites, unproven fatal)
- ZoneBased and IdSorted sync support for Quest, QuestDialog, StrSheet_Quest (no server-side schema yet)
- DynamicGeoData, AIData, NpcShape, StrSheet_ZoneName sync support
- `collectionTerritories` cross-file ID uniqueness enforcement

### Datasheet MCP Server

- `datasheet-v31` — read-only reference (v31 original TERA data) ✅
- `datasheet-v92` — active server read access ✅
- Improvement backlog: 20 issues filed and triaged same day (11 fixed, 2 already-working, 7 deferred); rebuilt exe validated 15/15 via stdio harness; deployment to `.mcp/` pending session restart ✅

### Dev Deployment

- `tools/deploy-dev/` SSH delta deploy to dev game server (verified end-to-end) ✅
- Server-share push discontinued; world server restart remains manual (automation deferred)

### Correlated Repositories

| Repo | Role | Current State |
|------|------|---------------|
| `reforged-server` (ATP) | Live v92 server datasheets + client DC | IoD restored, patch 000 applied; patch 001 all 57 specs applied (sync narrowed to 47 files) |
| `datasheetlang` | DSL CLI source | Manifest narrowing complete, all strategies operational |
| `datasheet-domain` | Game entity domain docs | Source of truth for entity schemas and ID ranges |
| `datasheet-mcp` | MCP server source | 20-item improvement backlog in progress |
| `reforged-content-framework` | Design source of truth (progression, economy, seasons) | Routed via `content_framework` key; locked invariants binding |
| `reforged-deploy` | Deployment infra docs (private) | Dev game server SSH access operational |
