# Island of Dawn — File Manifest

## Zone-Partitioned Files

### Files to copy from v31 → v92 (35 files)

These files exist in both versions. The v31 version replaces the v92 version.

| File | Zone | Type |
|------|------|------|
| AIData_13.xml | 13 | AI behavior |
| AIData_213.xml | 213 | AI behavior |
| AIData_313.xml | 313 | AI behavior |
| AIData_364.xml | 364 | AI behavior |
| ActiveMove_13.xml | 13 | NPC movement paths |
| ActiveMove_416.xml | 416 | NPC movement paths |
| AiData_416.xml | 416 | AI behavior |
| AiData_64.xml | 64 | AI behavior |
| BonfireData_13.xml | 13 | Campfire locations |
| CollectionTerritory_13_ATW_P.xml | 13 | Gathering node spawn positions (v31 copy) |
| BonfireData_213.xml | 213 | Campfire locations |
| BonfireData_64.xml | 64 | Campfire locations |
| DynamicSpawn_13.xml | 13 | Dynamic spawn rules |
| DynamicSpawn_416.xml | 416 | Dynamic spawn rules |
| FormationData_13.xml | 13 | NPC formations |
| FormationData_416.xml | 416 | NPC formations |
| NpcData_13.xml | 13 | NPC spawn points |
| NpcData_213.xml | 213 | NPC spawn points |
| NpcData_313.xml | 313 | NPC spawn points |
| NpcData_364.xml | 364 | NPC spawn points |
| NpcData_416.xml | 416 | NPC spawn points |
| NpcData_64.xml | 64 | NPC spawn points |
| NpcSkillData_13.xml | 13 | NPC skill assignments |
| NpcSkillData_213.xml | 213 | NPC skill assignments |
| NpcSkillData_313.xml | 313 | NPC skill assignments |
| NpcSkillData_364.xml | 364 | NPC skill assignments |
| NpcSkillData_416.xml | 416 | NPC skill assignments |
| NpcSkillData_64.xml | 64 | NPC skill assignments |
| TerritoryData_13.xml | 13 | Zone territory definitions |
| TerritoryData_213.xml | 213 | Zone territory definitions |
| TerritoryData_313.xml | 313 | Zone territory definitions |
| TerritoryData_364.xml | 364 | Zone territory definitions |
| TerritoryData_416.xml | 416 | Zone territory definitions |
| TerritoryData_64.xml | 64 | Zone territory definitions |
| WorkObjectTerritory_13.xml | 13 | Work object placements |

### Files patched (not copied) — v92-only active variants

| File | Zone | Change |
|------|------|--------|
| CollectionTerritory_13_ATW_Death_P.xml | 13 | Territory id=1: downgraded collection types from endgame (63/151/351) to v31 starter (1/101/301); spawn positions kept. Territory id=5 added from v31 (quest nodes incl. Mock Rock typeId=496). |

> **Why:** The server loads `_ATW_Death_P` as the active gathering territory for zone 13, not `_ATW_P`. This file has no v31 equivalent — it was introduced in v92 as an endgame replacement using the same spawn positions. Direct copy from v31 is not possible; targeted patching was required.

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
