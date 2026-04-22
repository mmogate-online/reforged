# Island of Dawn — Progress Tracker

## Phase Status

| Phase | Description | Status | Notes |
|-------|-------------|--------|-------|
| Assessment | Zone mapping, file inventory, tooling gaps | Done | See assessment.md |
| Phase 0 | Revert pending v92 datasheet + client DC changes | Done | 49+45 files reverted |
| Phase 1 | Server zone-partitioned file copy (v31 → v92) | Done | 34 copied + 8 emptied (zones 13/64/213/313/364/416); zone 436: 8 files + 3 VillagerData conditions |
| Phase 2 | Server monolithic file merging | Done | 133 files modified; see data/phase2-log.md |
| Phase 3 | Client DC migration (direct v31 copy) | Done | 245 quest files copied; zone files reverted (schema incompatible); see data/client-dc-shards.md |
| Phase 4 | Validation | Done | MCP audit 2026-04-21: all zones, quests, reward items confirmed |

## Phase 0 — Revert Pending Changes

- [x] Git restore + clean v92 server datasheet repo (49 files)
- [x] Git restore + clean v92 client DC repo (45 files)
- [x] Verify both repos clean (only Windows `nul` artifacts remain)

## Phase 1 — Server Zone File Copy

- [x] Copy 34 v31 zone files -> v92 server
- [x] Copy CollectionTerritory_13_ATW_P.xml from v31 (missed in initial migration; restores Territory id=1 general gathering nodes + correct Territory id=5 quest nodes)
- [x] Patch CollectionTerritory_13_ATW_Death_P.xml (see note below)
- [x] Empty 8 v92-only files to skeleton XML (DynamicSpawn/FormationData for zones 64, 213, 313, 364)
- [x] Verify: zone 13 NPC count matches v31 (403 territories, 498 spawns, 31 NPCs)

> **CollectionData note:** The v92 server loads `CollectionTerritory_13_ATW_Death_P.xml` as the active gathering territory for zone 13 — NOT `CollectionTerritory_13_ATW_P.xml`. This was discovered during Phase 4 testing: players encountered level-60 endgame nodes (Pilka Plant, typeId=63) instead of v31 starter nodes. The `_ATW_P` file appears to be inactive or overridden by the `_ATW_Death_P` variant.
>
> Fix applied to `CollectionTerritory_13_ATW_Death_P.xml`:
> - Territory id=1 collection types downgraded from endgame (63/151/351) to v31 starter (1/101/301) — spawn positions preserved
> - Territory id=5 (quest nodes, including Mock Rock typeId=496 for quests 1382/1383) added from v31
>
> `CollectionTerritory_13_ATW_P.xml` was still replaced with the full v31 copy as a correctness measure.

### 1b — Zone 436 (Karascha's Lair) — scope added 2026-04-18

- [x] Copy 8 zone-partitioned files from v31 → v92 (AIData, ActiveMove, DungeonData_9036, DynamicSpawn, FormationData, NpcData, NpcSkillData, TerritoryData)
- [x] Copy 3 VillagerData conditions from v31 → v92 (01010, 01030, 01501)
- [x] Verify 3 v92-only VillagerData conditions intact (01502, 08001, 08002)
- [x] Verify VillagerDialog_436.xml intact (v92-only, keep)
- [x] DungeonData_9036.xml: confirmed `levelOver value="9"` and quest 1316 conditions after copy

> **DungeonData note:** v92 repurposed DungeonData_9036.xml for lv65 endgame content (`levelOver="65"`, `RestoreTargetQuest id="21306,21307"`). The v31 version has the correct IoD conditions (`levelOver="9"`, `progressQuest value="1316"`, `completeQuest value="1316"`). This is why players cannot enter "Dark Revelations" dungeon — direct file copy from v31 fixes it.

## Phase 2 — Server Monolithic File Merging

### 2a — Loot / Compensation
- [x] Extract compensationIds from IoD NPC templates in v31 — only zone 13 has loot
- [x] Copy CCompensation_0013.xml from v31 -> v92 (single file overwrite)
- [x] No conflicts — file already existed in v92

### 2b — Quest Data (65 quests)
- [x] Get full IoD quest ID list from v31 MCP — 65 quests inventoried in quests.md
- [x] Resolve cross-zone dependencies — all resolved (see quests.md)
- [x] Copy 65 .quest XML files from v31 -> v92
- [x] Copy 65 QuestDialog files with v31->v92 rename (zone-partitioned -> flat per-quest)
- [x] Selective merge StrSheet_Quest.xml — 1,009 strings replaced (4 had content diffs)
- [x] Selective merge QuestGroupList.xml — StoryGroup 1, 2 + HuntingZone 13 replaced
- [x] QuestCompensation.xml — does not exist in either version; quest rewards in .quest files
- [x] QuestCompensationData — all IoD quests use ID 0 (null) or 1 (empty placeholder); no copy needed
- [x] Verify reward items exist in v92 — 72/72 items confirmed: weapon bags (10009–10016, 55006, 12129–12136, 55271, 10593–10600, 55079), armor/glove bags (17404–17716, 15019–15673), consumables (8007, 7200, 7100/7104/7108, 6048, 8200, 160)
- [ ] Post-migration: smooth out dangling chain connections to v92 questline via DSL

### 2c — NPC Behavioral Files
- [x] Compile full IoD NPC template ID list — 137 unique IDs (see data/npc-template-ids.md)
- [x] All 6 files investigated: IoD entries identical between v31/v92 — NO MERGE NEEDED
- [x] NpcBasicAction.xml — 11 IoD entries identical (v92 only adds cosmetic attrs)
- [x] NpcShape.xml — IoD shapes byte-for-byte identical
- [x] NpcSocialData.xml — 34 IoD entries identical
- [x] NpcReactionData.xml — 51 IoD entries identical
- [x] NpcAbnormalityBalance.xml — global tuning, no IoD-specific entries
- [x] NpcSeatData.xml — vehicle seats only, no IoD-specific entries

### 2d — String Tables
- [x] StrSheet_Npc.xml — no merge needed (v31 doesn't have it; v92 version is UI strings, not NPC names)
- [x] StrSheet_ZoneName.xml — IoD zone names (13, 64, 416) identical between v31/v92

## Phase 3 — Client DC Migration (Direct v31 Copy)

### 3a — Shard Mapping (Assessment)
- [x] Build zoneId → shard mapping for v31 and v92 client DC (see data/client-dc-shards.md)
- [x] Build questId → shard mapping for v31 and v92 client DC (see data/client-dc-shards.md)
- [x] Investigate QuestCompensationData — both shards IoD-exclusive, safe to overwrite
- [x] Investigate NpcShape — 150 IoD shapes functionally identical, no merge needed
- [x] Investigate StrSheet_ZoneName — IoD zone entries identical, no merge needed
- [x] Investigate ContinentData — IoD continents identical (v92 adds channelMax only), no merge needed
- [x] Investigate StrSheet_Npc — v92 has 1,836 entries vs v31's 630; skip (investigate if NPC names wrong in-game)
- [x] Investigate DynamicGeoData — zone 416 dungeon HAS geo data in v31 (15 doors + 4 elevators + 1 shuttle), must copy
- [x] Investigate AIData — v31 has no AIData; v92 AIData has no ID linkage to NPC templates, safe to leave as-is
- [x] Investigate Dungeon — v31 shard is empty skeleton for continent 9016, no action needed

### 3b — Zone-Partitioned Client Files (DSL Sync)

v31 direct copy failed for zone files due to schema incompatibility (v31 XML missing attributes required by v92 XSD). Solution: use DSL sync tool to generate client DC files from v92 server datasheets.

```bash
dsl sync -c reforged/config/sync-config.yaml -e NpcData -e TerritoryData --zones 13,64,213,313,364,416
```

- [x] NpcData — synced via DSL (6 zones, numeric sorting); server-to-client XSD filtering handles attribute subset
- [x] TerritoryData — synced via DSL (6 zones, alphabetical sorting); server-to-client XSD filtering handles attribute subset
- [x] DynamicGeoData — SKIPPED; client file deleted. Neither v31 nor v92 server has DynamicGeo_9016.xml (prologue dungeon geometry is client-only data). Client DC file is a subset of server format (missing desc, auto, closedMSec, openMSec, bottomLeftPos, bottomRightPos, height). Creating a server file from client data requires sourcing missing physics/collision attributes. Deferred to post-migration.
- [x] AIData — no v31 source, v92 left as-is
- [x] Dungeon — v31 shard empty, no action needed

### 3c — Quest Client Files
- [x] Copy v31 → v92 Quest shards (81 quests)
- [x] Copy v31 → v92 QuestDialog shards (81 dialogs)
- [x] Copy v31 → v92 QuestCompensationData shards (2 shards, IoD-exclusive)
- [x] Copy v31 → v92 StrSheet_Quest shards (81 shards)

### 3d — Monolithic / Other Client Files
- [x] ContinentData — no merge needed (IoD entries identical, v92 only adds channelMax)
- [x] NpcShape — no merge needed (150 IoD shapes functionally identical)
- [x] StrSheet_Npc — deferred (investigate only if NPC names wrong in-game)
- [x] StrSheet_ZoneName — no merge needed (IoD zone names identical)

### 3f — Zone 436 Client DC — scope added 2026-04-18

- [x] NpcData zone 436 — generated via DSL sync from server NpcData_436.xml (v31); NpcData-00212.xml written with 8 NPC entries in v92-compliant format
- [x] TerritoryData zone 436 — generated via DSL sync from server TerritoryData_436.xml (v31); TerritoryData-00218.xml written with 4 territory groups (43600003/4/8/9) in v92-compliant format
- [x] VillagerDialog — no action needed; v92 shards 06090/06091 already identical to v31; stubs match

### 3e — Verify
- [x] Count client DC files modified per folder
- [x] Spot-check copied shards for IoD content
- [x] Cross-reference server NPC template IDs against client DC NpcData shards

## Phase 4 — Validation

### 4a — Server-Side (MCP v92)
- [x] Zone 13 NPC population matches v31 — 57 NPCs confirmed via audit_zone_loot; NPC template IDs zero-diff vs v31
- [x] Zone 416 prologue NPCs intact — 8/8 prologue quests (41510–41517) confirmed via MCP
- [x] Sub-zones correct — all 6 zones (13, 64, 213, 313, 364, 416) NPC templates match v31 exactly; only cosmetic name diff on template 1050
- [x] Zone 13 loot audit — 50 NPCs with mote drops (items 8000, 8005); 7 NPCs with no loot (vendors/quest NPCs); matches v31
- [x] Zone 436 loot audit — 8 NPCs, 0 regular drops (correct: boss uses ECompensation, not CCompensation)
- [x] IoD quest chains complete — story group 1: 18/18; story group 2: 7/7 IoD quests (4 extra level-65 v92 quests in group are non-migration); side quests zone 64: 16/16; side quests zone 213: 7/7; zoneless 1339: present; prologue 415: 8/8; prologue 416: 8/8 — total 65/65
- [x] Quest 1316 (Dark Revelations) task chain confirmed — zone 436 boss kill (templateId 1002) + dialog chain intact
- [x] Quest dialogs spot-check — quest 1339 prerequisites identical to v31 (Quest 9999 is original design)

### 4b — Client-Server Consistency
- [x] Teleport scroll (skill 60130101) — server UserSkillData_Common.xml and client SkillData-00023.xml both have recallContinent=13, recallPos=66600.8672,-79855.5234,-2993.1643
- [x] Full NPC template IDs: server NpcData refs all present in client DC — validated via MCP audit
- [x] Quest IDs: server QuestData all present in client DC Quest shards — 65/65 confirmed
- [x] Zone/continent data consistent between server and client

### 4c — Functional Testing
- [ ] New character lands in IoD prologue (zone 416) — *entry point manual, out of scope*
- [x] Gathering nodes present in zone 13 (verified: Mock Rock nodes spawn, Primer Ore gatherable, quests 1382/1383 completable)
- [x] Story group 1 quest chain walkthrough — in-game validated 2026-04-22
- [x] Story group 2 quest chain walkthrough — in-game validated 2026-04-22
- [x] NPC dialog text displays correctly — in-game validated 2026-04-22
- [x] Loot drops from zone 13 mobs — in-game validated 2026-04-22

## Post-Migration

- [ ] Adopt DSL sync configs for NpcData, TerritoryData, DungeonData, ContinentData
- [ ] File DSL requests for missing sync entries (QuestData, QuestDialog, QuestCompensation, StrSheet_Quest, AIData, DynamicGeoData, NpcShape, StrSheet_ZoneName)
- [ ] Smooth out dangling IoD quest chain connections to v92 questline via DSL
- [ ] DynamicGeoData zone 416 (dungeon doors/elevators — client-only data, server source missing)
