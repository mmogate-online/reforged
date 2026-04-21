# Island of Dawn — File Manifest

## Zone-Partitioned Files

### Files to copy from v31 → v92 (46 files)

These files exist in both versions. The v31 version replaces the v92 version.

| File | Zone | Type |
|------|------|------|
| AIData_13.xml | 13 | AI behavior |
| AIData_213.xml | 213 | AI behavior |
| AIData_313.xml | 313 | AI behavior |
| AIData_364.xml | 364 | AI behavior |
| AIData_436.xml | 436 | AI behavior |
| ActiveMove_13.xml | 13 | NPC movement paths |
| ActiveMove_416.xml | 416 | NPC movement paths |
| ActiveMove_436.xml | 436 | NPC movement paths |
| AiData_416.xml | 416 | AI behavior |
| AiData_64.xml | 64 | AI behavior |
| BonfireData_13.xml | 13 | Campfire locations |
| CollectionTerritory_13_ATW_P.xml | 13 | Gathering node spawn positions (v31 copy) |
| BonfireData_213.xml | 213 | Campfire locations |
| BonfireData_64.xml | 64 | Campfire locations |
| DungeonData_9036.xml | 436 (continent 9036) | Dungeon entry conditions — **CRITICAL: v92 has lv65 endgame conditions; v31 has lv9 IoD conditions** |
| DynamicSpawn_13.xml | 13 | Dynamic spawn rules |
| DynamicSpawn_416.xml | 416 | Dynamic spawn rules |
| DynamicSpawn_436.xml | 436 | Dynamic spawn rules |
| FormationData_13.xml | 13 | NPC formations |
| FormationData_416.xml | 416 | NPC formations |
| FormationData_436.xml | 436 | NPC formations |
| NpcData_13.xml | 13 | NPC spawn points |
| NpcData_213.xml | 213 | NPC spawn points |
| NpcData_313.xml | 313 | NPC spawn points |
| NpcData_364.xml | 364 | NPC spawn points |
| NpcData_416.xml | 416 | NPC spawn points |
| NpcData_436.xml | 436 | NPC spawn points |
| NpcData_64.xml | 64 | NPC spawn points |
| NpcSkillData_13.xml | 13 | NPC skill assignments |
| NpcSkillData_213.xml | 213 | NPC skill assignments |
| NpcSkillData_313.xml | 313 | NPC skill assignments |
| NpcSkillData_364.xml | 364 | NPC skill assignments |
| NpcSkillData_416.xml | 416 | NPC skill assignments |
| NpcSkillData_436.xml | 436 | NPC skill assignments |
| NpcSkillData_64.xml | 64 | NPC skill assignments |
| TerritoryData_13.xml | 13 | Zone territory definitions |
| TerritoryData_213.xml | 213 | Zone territory definitions |
| TerritoryData_313.xml | 313 | Zone territory definitions |
| TerritoryData_364.xml | 364 | Zone territory definitions |
| TerritoryData_416.xml | 416 | Zone territory definitions |
| TerritoryData_436.xml | 436 | Zone territory definitions |
| TerritoryData_64.xml | 64 | Zone territory definitions |
| VillagerData/04360000001010.condition | 436 | NPC 1010 dialog conditions |
| VillagerData/04360000001030.condition | 436 | NPC 1030 dialog conditions |
| VillagerData/04360000001501.condition | 436 | NPC 1501 dialog conditions |
| WorkObjectTerritory_13.xml | 13 | Work object placements |

### Files patched (not copied) — v92-only active variants

| File | Zone | Change |
|------|------|--------|
| CollectionTerritory_13_ATW_Death_P.xml | 13 | Territory id=1: downgraded collection types from endgame (63/151/351) to v31 starter (1/101/301); spawn positions kept. Territory id=5 added from v31 (quest nodes incl. Mock Rock typeId=496). |

> **Why:** The server loads `_ATW_Death_P` as the active gathering territory for zone 13, not `_ATW_P`. This file has no v31 equivalent — it was introduced in v92 as an endgame replacement using the same spawn positions. Direct copy from v31 is not possible; targeted patching was required.

### v92-only files to keep — Zone 436 additions

These zone 436 files exist only in v92 and represent additions layered on top of the v31 dungeon. They are kept as-is.

| File | Zone | Notes |
|------|------|-------|
| VillagerData/04360000001502.condition | 436 | NPC 1502 "Dimensional Magic Stone" — teleportal inside dungeon added in v92 |
| VillagerData/04360000008001.condition | 436 | NPC 8001 "Joel" — story scene participant added in v92 |
| VillagerData/04360000008002.condition | 436 | NPC 8002 "Jowyn Rionas" — story scene participant added in v92 |
| VillagerDialog/VillagerDialog_436.xml | 436 | Dialog tree covering all zone 436 NPCs (both v31 story NPCs and v92 additions) |

### v92-only files to handle (8 files)

These exist in v92 but NOT in v31. They were added for the endgame rework and need to be emptied or removed.

| File | Zone | Type | Action |
|------|------|------|--------|
| DynamicSpawn_64.xml | 64 | Dynamic spawn rules | Empty/delete |
| DynamicSpawn_213.xml | 213 | Dynamic spawn rules | Empty/delete |
| DynamicSpawn_313.xml | 313 | Dynamic spawn rules | Empty/delete |
| DynamicSpawn_364.xml | 364 | Dynamic spawn rules | Empty/delete |
| FormationData_64.xml | 64 | NPC formations | Empty/delete |
| FormationData_213.xml | 213 | NPC formations | Empty/delete |
| FormationData_313.xml | 313 | NPC formations | Empty/delete |
| FormationData_364.xml | 364 | NPC formations | Empty/delete |

## Server Monolithic Files (Selective Merge Required)

These are server-wide files where IoD-related entries must be compared and potentially merged.

**Note:** NPC template definitions (stats, models, type) do NOT live in the server datasheet — they are client datacenter entities. The server only has NPC behavioral/support files.

### NPC Behavioral Files

Merge keyed on NPC template ID. 31 unique IDs in zone 13, plus sub-zone and prologue NPCs.

| File | Content | Complexity |
|------|---------|------------|
| NpcBasicAction.xml | Default NPC behaviors | Medium |
| NpcShape.xml | NPC visual models | Medium |
| NpcSocialData.xml | NPC social interactions | Low |
| NpcAbnormalityBalance.xml | NPC abnormality resistances | Low |
| NpcReactionData.xml | NPC reaction behaviors | Low |
| NpcSeatData.xml | NPC seating positions | Low |

### Quest Files

### Quest Files

53 IoD quests across zones 64, 213, 416. Three story groups + side quests + per-class prologue completion. See [quests.md](quests.md) for full inventory.

| File/Folder | Format | Strategy | Complexity |
|---|---|---|---|
| `QuestData/{id:D6}.quest` | XML per quest (Korean tags), one file per quest ID | Copy 65 matching files from v31 → v92 | Low |
| `QuestDialog/` | XML, zone-partitioned in v31 (`QuestDialog_<zone>_<n>.xml`), flat in v92 (`QuestDialog_<questId>.xml`) | Naming differs — needs transformation | Medium |
| `StrSheet_Quest.xml` | Monolithic XML | Selective merge by quest ID | Medium |
| `QuestGroupList.xml` | Monolithic XML | Merge storyGroup 1 and 2 entries | Low |
| `QuestCompensation.xml` | Monolithic XML | Selective merge by quest ID | Low |
| `QuestCompensationData/QuestCompensationData_xxx.xml` | Per-quest compensation files (156 in v92), keyed by quest GlobalId | Copy matching files from v31 for IoD quests | Low |

### Loot / Compensation Files

IoD loot is minimal — zone 13 drops only motes (items 8000, 8005), zone 416 has zero loot.

| File/Folder | Strategy | Complexity |
|---|---|---|
| `CompensationData/CCompensation_XXXX.xml` | Copy files matching IoD NPC compensationIds from v31 | Low |

### Other Monolithic Files

| File | Content | Strategy | Complexity |
|------|---------|----------|------------|
| ContinentData.xml | Continent properties | Compare continent 13 + 9016 entries | Medium |
| StrSheet_Npc.xml | NPC display names | Merge entries for IoD NPC template IDs | Medium |
| StrSheet_ZoneName.xml | Zone display names | Verify — likely unchanged | Low |

## Client Datacenter Migration (Direct v31 Copy)

**Strategy:** Direct file copy from v31 client DC, not DSL sync. We're restoring v31 content — the v31 client DC already has the exact data in the exact format the client expects. DSL sync will be adopted post-migration for ongoing maintenance.

**Source:** `Z:\tera pserver\v31.04\client-dc_v31\DataCenter_Final_EUR_v31\`
**Target:** `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR\`

### Zone-Partitioned Client Files (shard copy by zone ID)

| Client DC Folder | Server Counterpart | Has Client DC? | Migration Action |
|---|---|---|---|
| NpcData | NpcData_*.xml | Yes (both versions) | Map zoneId → shard, copy IoD shards |
| TerritoryData | TerritoryData_*.xml | Yes (both versions) | Map zoneId → shard, copy IoD shards |
| AIData | AIData_*.xml | Yes (v92 only) | v92-only folder — may not exist in v31 client DC |
| DungeonData | DungeonData_*.xml | Yes (both versions) | Map zoneId → shard, copy IoD shards |
| DynamicGeoData | DynamicGeoData_*.xml | Yes (both versions) | Map zoneId → shard, copy IoD shards |

#### Zone 436 — Shard Mapping

| Client DC Folder | v31 Shard | v92 Shard | Action |
|---|---|---|---|
| NpcData | NpcData-00209.xml | NpcData-00212.xml | Copy v31 shard to v92 target |
| TerritoryData | TerritoryData-00167.xml | TerritoryData-00218.xml | Copy v31 shard to v92 target |
| DungeonData | Not present (server-only) | Not present | No action |
| AIData | Not in v31 client DC | v92 only | No action (v92 left as-is) |
| VillagerDialog | Shards 05218, 05219, 05220 (zone 436 dialogs) | Shards 06090–06095 | Merge v31 zone 436 entries into v92 shards |

### Quest Client Files (shard copy by quest ID)

| Client DC Folder | Content | Migration Action |
|---|---|---|
| Quest | Quest definitions (sharded by ID) | Map IoD quest IDs → shards, copy/merge |
| QuestDialog | Quest dialog text (sharded) | Map IoD quest IDs → shards, copy/merge |
| QuestCompensationData | Quest rewards (sharded) | Map IoD quest IDs → shards, copy/merge |
| StrSheet_Quest | Quest display strings | Map IoD quest IDs → shards, copy/merge |

### Monolithic / Other Client Files

| Client DC Folder | Content | Migration Action |
|---|---|---|
| ContinentData | World topology | Copy shards for continents 13, 9016 |
| NpcShape | NPC visual models | Copy shards for IoD NPC template IDs |
| StrSheet_Npc | NPC display names | Copy shards for IoD NPC template IDs |
| StrSheet_ZoneName | Zone display names | Copy shards for IoD zone IDs |

### Server-Only Files (No Client Counterpart)

| Server File Type | Notes |
|---|---|
| DynamicSpawn | Server-only, no client sync needed |
| FormationData | Server-only |
| ActiveMove | Server-only |
| NpcSkillData | Synced via SkillData (Merged strategy) — handled separately if needed |
| BonfireData | Server-only |
| WorkObjectTerritory | v92 dropped client-side support |

### Post-Migration: DSL Sync Adoption

After migration, adopt DSL sync configs for future spec-driven changes:
- NpcData, TerritoryData, DungeonData, ContinentData (from sync-config.template.yaml)
- File DSL requests for missing sync entries: QuestData (IdSorted), QuestDialog, QuestCompensation, StrSheet_Quest, AIData, DynamicGeoData, NpcShape, StrSheet_ZoneName

## Files NOT in Scope

| File | Reason |
|------|--------|
| Stepstone Isle zone files (*_827.xml) | Left in place, just unreferenced |
| IoD Coast zone files (*_415.xml) | v92-only, decision deferred |
| v92-only file types (FieldData, FishingTerritory, etc.) | Not present for IoD zones in either version |
