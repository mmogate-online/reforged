# Reforged Server Content — Status

_Last updated: 2026-04-22_

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

## Patch 001 Content 🔄

Custom content layer applied on top of the IoD migration baseline.

| System | Status | Notes |
|--------|--------|-------|
| Gear progression pipeline | ✅ | Starter 0 → Frostfire → Flawless → potential unlock scroll |
| Enchant materials | ✅ | Probability tables + item links |
| Gear infusion | ✅ | Passivities, items, loot tables |
| Dyad crystal system | ✅ | 1182 crystals across 6 tiers, per-type passivity configs |
| Infusion loot | ✅ | Zone loot distribution strategy implemented |
| Zone loot overhaul | ✅ | All patch 001 open-world zones + dungeons |
| Dungeon tokens + shop chain | ✅ | MedalStore VillagerMenuItem→BuyMenuList→BuyList wiring |
| Full patch 001 validation | 🔄 | Pending — equivalent of IoD Phase 4 |

**In scope (patch 001 zones):** Fey Forest (2), Oblivion Woods (3), Tuwangi Mire (5), Valley of Titans (6), Celestial Hills (7), Cliffs of Insanity (15), Vale of the Fang (16), Paraanon Ravine (17), Crescentia (59), Lumbertown (60), Velika (63), Bastion of Lok (487), Sinestral Manor (488), Island of Dawn (13), Karascha's Lair (436).

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

**Open DSL requests:** ~27 filed in `docs/dsl-requests/`. Key pending items:
- ZoneBased and IdSorted sync support for Quest, QuestDialog, StrSheet_Quest (no server-side schema yet)
- DynamicGeoData, AIData, NpcShape, StrSheet_ZoneName sync support
- `collectionTerritories` cross-file ID uniqueness enforcement

### Datasheet MCP Server

- `datasheet-v31` — read-only reference (v31 original TERA data) ✅
- `datasheet-v92` — active server read access ✅

### Correlated Repositories

| Repo | Role | Current State |
|------|------|---------------|
| `reforged-server` (ATP) | Live v92 server datasheets + client DC | IoD restored, patch 000 fixes applied |
| `datasheetlang` | DSL CLI source | Manifest narrowing complete, all strategies operational |
| `datasheet-domain` | Game entity domain docs | Source of truth for entity schemas and ID ranges |
