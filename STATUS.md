# Reforged Server Content — Status

_Last updated: 2026-07-21_

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
| 7 (v17 padding phase, Level 1) | 🔄 | APPLIED + DEPLOYED (specs 14-20, batch 21 specs / 2148 ops; client dev.27): 34 quests enabled, 19 habitat groups (Mysterious Ruins ecology restored), 6 quest givers placed from v17 NpcLoc markers, Sorcha dungeon 437 reclaimed (level-65 line 21301-21307 disabled), per-class reward rows fixed (First Expedition armor pays), v31 ECompensation drop table restored (300945). Sorcha dungeon 9037 fully working and live-completed (comment-disabled territory groups restored, commit `b2ae08fa`; dungeon_audit.py gate added). First live test done (density/Ramun/dupes fixes applied from it); remaining live checklist in the tracker phase 7 row. Level 2 (Berlon chain) not started |

**Divergence log:** `docs/plans/classic-restoration/iod/divergence-log.md` (adaptations, policy divergences incl. game-wide shared-store port and T-cat removal). **Open DSL requests from the redo:** newWorldMap section-level delete; VillagerDialog client sync (both low priority, hand-managed meanwhile). Client-only families stay tool-managed: StrSheet_NpcLoc (`gen_npcloc.py --prune`), MapDefineData.

---

## Patch 002 Content 🔄 (formerly patch 001)

Custom content layer; specs moved to `specs/patches/002/`. Applies on top of the patch 001 restoration baseline once committed. Rebase required before apply: `17-iod-loot`, the `19/21` strips, and the `balance/` specs were authored against vanilla v92 IoD tables.

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
| IoD restoration tooling | ✅ | `tools/dc-restore/` (survey, dcq, audit_quests, quest_restore, comp_restore, spawn_restore) + `tools/deploy-client/` (pack/install/CF-publish; syncing is migrate's job); `content-restoration` skill documents the workflow, `quest-live-test` skill documents live quest verification |

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
| Package-internal variable scope at export | ✅ Variables resolved at export time — consumers no longer re-import package-internal vars |

**Open DSL requests:** ~28 filed in `docs/dsl-requests/`. Key pending items:
- ~~Multi-spec in-memory cache E422~~ — resolved in DSL commit `2278066c`; `migrate.py` switched to batch apply
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
