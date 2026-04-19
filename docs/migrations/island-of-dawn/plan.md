# Island of Dawn — Execution Plan

## Phase 0 — Revert Pending Changes

**Goal:** Clean v92 server datasheet and client DC back to committed state.

**Steps:**
1. Revert server datasheet (48 modified files + 1 untracked):
   ```bash
   git -C "D:/dev/mmogate/tera92/server" restore .
   git -C "D:/dev/mmogate/tera92/server" clean -fd
   ```
2. Revert client DC (42 modified files + 3 untracked):
   ```bash
   git -C "D:/dev/mmogate/tera92/client-dc" restore .
   git -C "D:/dev/mmogate/tera92/client-dc" clean -fd
   ```
3. Verify both repos are clean: `git -C <path> status`

**Risk:** None — these are uncommitted changes from the patch 001 migration run.

---

## Phase 1 — Zone-Partitioned File Copy (Server)

**Goal:** Replace v92 endgame IoD zone content with v31 original content.

### 1a — Copy v31 zone files → v92 server (34 files)

Source: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet\`
Target: `D:\dev\mmogate\tera92\server\Datasheet\`

Copy all files listed in file-manifest.md "Files to copy from v31 → v92" section. Direct overwrites — same filenames, same zone IDs.

### 1b — Empty v92-only zone files (8 files)

Files: `DynamicSpawn_{64,213,313,364}.xml`, `FormationData_{64,213,313,364}.xml`

Replace content with valid empty XML skeleton (root element only, no child entries). Read an existing v31 file of the same type to determine the root element structure.

### 1c — Verify

- Count zone files for IoD zones: expect 42 total (34 copied + 8 emptied)
- Spot-check a few files (e.g., `NpcData_13.xml`) — confirm content matches v31 source

---

## Phase 2 — Server Monolithic File Merging

**Goal:** Merge IoD-specific entries from v31 global server files into v92.

### 2a — Compensation / Loot Tables

IoD loot is minimal — zone 13 NPCs drop only healing motes (items 8000, 8005). Zone 416 has zero loot.

Loot tables live in `CompensationData/CCompensation_XXXX.xml` files, keyed by the NPC template's `compensationId`.

**Steps:**
1. Extract `compensationId` from each NPC template ID spawned in v31 IoD zones
2. Copy matching `CCompensation_XXXX.xml` files from v31 → v92 `CompensationData/`
3. Verify no conflicts with existing v92 compensation files

**Risk:** Low — IoD loot is trivial.

### 2b — Quest Data

65 IoD quests across zones 64, 213, 415, 416 in v31 (see [quests.md](quests.md) for full inventory):
- Story Group 1 — Entry Arc: 18 quests (levels 1–6)
- Story Group 2 — Mid Arc: 7 quests (levels 7–10)
- Side quests zone 213: 7 quests
- Side quests zone 64: 16 quests
- Zoneless side quest: 1 (quest 1339, successor to 1313)
- Prologue zone 415: 8 class-variant quests ("Reach the Beach")
- Prologue zone 416: 8 class-variant quests ("The Prologue Ends")
- **Excluded:** Story Group 18 — Noctenium Arc: 3 quests (level 60, out of scope)

Quest files are XML with Korean tags (`.quest` extension). DSL has full schema support for quests (`quests`, `questStrings`, `questDialogs`, `questCompensations` entities).

| Location | Format | Migration Strategy |
|---|---|---|
| `QuestData/{id:D6}.quest` | XML per quest (Korean tags) | Copy 65 matching files from v31 → v92 by quest ID |
| `QuestDialog/` | XML, zone-partitioned in v31 (`QuestDialog_<zone>_<n>.xml`), flat in v92 (`QuestDialog_<questId>.xml`) | Naming convention differs — needs transformation or v31-style copy |
| `StrSheet_Quest.xml` | Monolithic XML | Selective merge of IoD quest string entries |
| `QuestGroupList.xml` | Monolithic XML | Merge IoD quest group entries (storyGroup 1 and 2) |
| `QuestCompensation.xml` | Monolithic XML | Selective merge of IoD quest reward entries |
| `QuestCompensationData/QuestCompensationData_xxx.xml` | Per-quest compensation files (156 in v92) | Copy matching files from v31 for IoD quest GlobalIds |

**Steps:**
1. Full IoD quest ID list confirmed — 65 quests (see quests.md)
2. Copy 65 matching `.quest` files from v31 `QuestData/` → v92 `QuestData/`
3. Copy/transform v31 `QuestDialog` files for IoD zones (64, 213, 415, 416) into v92
4. Selective merge `StrSheet_Quest.xml` for IoD quest IDs
5. Selective merge `QuestGroupList.xml` for storyGroup 1 and 2
6. Selective merge `QuestCompensation.xml` for IoD quest IDs
7. Copy matching `QuestCompensationData_xxx.xml` files from v31 for IoD quests
8. Verify reward items exist in v92 (class weapon/armor bags, consumables — see quests.md reward items table)

**Cross-zone dependencies (all resolved):**
- `connectedTo 101` — not a real quest; it's the chain terminal/null marker. No action needed.
- Quest 1339 — "Sersine, She Seeks Shackles", zoneless side quest. All dialog NPCs in IoD zones. Included in scope.
- Zone 415 — identical between v31/v92 (no zone file migration needed). 8 "Reach the Beach" quests added to scope.
- Noctenium arc (15101–15103) — excluded (high-level, out of scope).

**Dangling chains:** IoD quests terminate at chain marker. Successor quests in other zones may not connect seamlessly in v92. Accept for now, smooth out post-migration with DSL.

**Risk:** Medium — QuestDialog naming convention differs between versions. Reward items (class weapon/armor bags) must be verified in v92.

### 2c — NPC Behavioral Files

31 unique NPC template IDs spawned in v31 IoD zone 13, plus NPCs in sub-zones and prologue.

| File | Action |
|---|---|
| NpcBasicAction.xml | Selective merge for IoD NPC template IDs |
| NpcShape.xml | Selective merge |
| NpcSocialData.xml | Selective merge |
| NpcAbnormalityBalance.xml | Selective merge |
| NpcReactionData.xml | Selective merge |
| NpcSeatData.xml | Selective merge |

**Steps:**
1. Compile full NPC template ID list across all IoD zones (13, 64, 213, 313, 364, 416) from v31 NpcData files
2. For each behavioral file: extract entries matching those template IDs from v31, replace/insert in v92
3. Python merge script keyed on template ID

**Risk:** Low — additive merges, IoD NPC IDs in low range unlikely to conflict with v92 additions.

### 2d — String Tables

| File | Strategy |
|---|---|
| StrSheet_Npc.xml | Merge NPC name entries for IoD template IDs from v31 → v92 |
| StrSheet_Quest.xml | Covered in 2b |
| StrSheet_ZoneName.xml | Verify IoD zone names match v31 — likely already correct |

---

## Phase 3 — Client DC Migration

**Goal:** Restore IoD content in v92 client datacenter using direct v31 client DC file copy.

### Design Decision

We use **direct v31 client DC file copy** instead of DSL sync for this migration because:
- We're restoring v31 content — the v31 client DC already has the exact data in the exact client format
- DSL sync filters through XSD, which could silently strip attributes needed for fidelity
- Multiple entity types have no sync config (quests, AIData, DynamicGeoData, NpcShape, StrSheet_ZoneName)
- Direct copy has zero dependencies on DSL team work

DSL sync will be adopted **after** migration for ongoing maintenance when we apply custom changes via specs.

### Source and Target

- **Source (v31):** `Z:\tera pserver\v31.04\client-dc_v31\DataCenter_Final_EUR_v31\`
- **Target (v92):** `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR\`

### 3a — Zone-Partitioned Client Files

For each entity type with client DC counterparts, identify the IoD zone shard files in v31 and copy to v92.

| Client DC Folder | Server Counterpart | Strategy |
|---|---|---|
| `NpcData/` | NpcData_*.xml | Map IoD zone IDs to v31 client shard numbers, copy matching shards |
| `TerritoryData/` | TerritoryData_*.xml | Same |
| `AIData/` | AIData_*.xml | Same (v92-only folder — may need new shards) |
| `DungeonData/` | DungeonData_*.xml | Same |
| `DynamicGeoData/` | DynamicGeoData_*.xml | Same |

**Steps:**
1. For each folder: extract the zone/huntingZoneId attribute from v31 client DC shard files to build a zoneId → shard mapping
2. Identify shards containing IoD zone IDs (13, 64, 213, 313, 364, 416)
3. Build the same mapping for v92 client DC
4. Copy v31 shards → v92, using the correct target shard number per zone

**Risk:** Low — zone-to-shard mapping is deterministic and extractable from both versions. Shards that contain only IoD data can be replaced wholesale; mixed shards need selective merge.

### 3b — Quest Client Files

| Client DC Folder | Strategy |
|---|---|
| `Quest/` | Map IoD quest IDs to v31 shard numbers, copy matching shards |
| `QuestDialog/` | Same |
| `QuestCompensationData/` | Same |
| `StrSheet_Quest/` | Same |

**Steps:**
1. Extract quest IDs from v31 client DC `Quest/` shard files
2. Identify shards containing IoD quest IDs (65 quests)
3. Build same mapping for v92
4. Copy/merge v31 shards → v92

**Risk:** Low — same deterministic shard mapping approach as 3a. IoD quests are in the low ID range and likely cluster in a small number of shards.

### 3c — Monolithic Client Files

| Client DC Folder | Strategy |
|---|---|
| `ContinentData/` | Copy v31 shard for continents 13, 9016 |
| `NpcShape/` | Copy v31 IoD NPC shape shards |
| `StrSheet_Npc/` | Copy v31 shards containing IoD NPC names |
| `StrSheet_ZoneName/` | Copy v31 shards containing IoD zone names |

### 3d — Verify

- Count client DC files modified per folder
- Spot-check: open a few copied shards, confirm IoD content present
- Cross-reference server NPC template IDs against client DC NpcData shards

---

## Phase 4 — Validation

**Goal:** Verify migrated content matches v31 reference and client-server consistency.

### 4a — Server-Side Validation (MCP v92)

| Check | Tool | Expected |
|---|---|---|
| Zone 13 NPC count | `audit_zone_spawns` | 57 NPCs (matching v31) |
| Zone 416 NPC count | `audit_zone_spawns` | 58 NPCs |
| Sub-zones (64, 213, 313, 364) | `audit_zone_spawns` | 51, 93, 8, 8 NPCs respectively |
| Zone 13 loot | `audit_zone_loot` | ~50 NPCs with mote drops |
| IoD quest chains | `trace_quest_sequence` | 65 quests across story groups 1, 2 + side quests + prologue |
| Quest dialogs | `lookup_quest_dialogs` | Spot-check key quests |
| NPC names | `search_text` | IoD NPC names present and correct |

### 4b — Client-Server Consistency

1. Compare NPC template IDs referenced in server NpcData vs templates present in client DC
2. Verify quest IDs in server QuestData have matching client DC Quest entries
3. Verify IoD zone/continent data consistent between server and client

### 4c — Functional Testing

- Create new character → lands in IoD prologue (zone 416) — *entry point config is manual, out of scope*
- Walk through story group 1 quest chain (zone 213 → zone 64)
- Walk through story group 2 quest chain
- Verify NPC dialog text displays correctly
- Verify loot drops from zone 13 mobs

---

## Execution Order and Dependencies

```
Phase 0 (git revert)
    ↓
Phase 1 (server zone file copy)
    ↓
Phase 2a (loot)  ──┐
Phase 2b (quests) ──┼── can run in parallel
Phase 2c (NPC)   ──┤
Phase 2d (strings)──┘
    ↓
Phase 3a (client DC zone files) ──┐
Phase 3b (client DC quest files) ──┼── can run in parallel
Phase 3c (client DC monolithic)  ──┘
    ↓
Phase 3d (client DC verify)
    ↓
Phase 4 (validation)
```

## Tools Required

| Tool | Purpose | Exists? |
|---|---|---|
| Python file copy script | Phase 1 zone file copy + empty skeleton generation | Build |
| Python XML merge script | Phase 2 selective merges (keyed on template/quest ID) | Build |
| Python client DC shard mapper | Phase 3 shard ID extraction and mapping | Build |
| MCP v31 / v92 | All phases for audit and validation | Exists |

## Post-Migration: DSL Sync Adoption

After migration is complete and validated, adopt DSL sync configs for entities that have template support:
- NpcData, TerritoryData, DungeonData, ContinentData (from sync-config.template.yaml)
- This enables future spec-driven changes to sync deterministically

File DSL requests for missing sync entries as non-blocking enhancements:
- QuestData (IdSorted strategy — code exists, needs config)
- QuestDialog, QuestCompensation, StrSheet_Quest
- AIData, DynamicGeoData, NpcShape, StrSheet_ZoneName
