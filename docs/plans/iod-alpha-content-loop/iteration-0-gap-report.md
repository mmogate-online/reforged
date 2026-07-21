# dc-restore Survey: Iteration 0 Gap Report

Generated 2026-07-17 16:15:42 by tools/dc-restore/survey.py

Baseline for v92 is the clean git HEAD content. Uncommitted working-tree
changes are patch-001 tuning overlays, annotated separately and never
counted as content loss. Sources: old client DataCenter (hard-restore),
v31 server datasheet (easy-restore), v92 server datasheet (current truth).

## Summary

| Zone | NPC miss | Skill miss | AI miss | Terr miss | Quests v31/v92/cli | v31-only Q | client-only Q | QComp lost | Loot overlay |
|------|----------|-----------|---------|-----------|--------------------|-----------|---------------|-----------|--------------|
| 13 | 0 | 0 | 0 | 0 | 65/65/63 | 0 | 0 | 75 | C:stripped |
| 64 | 0 | 0 | 0 | 0 | 0/0/0 | 0 | 0 | 0 | - |
| 213 | 0 | 0 | 0 | 0 | 0/9/0 | 0 | 0 | 0 | - |
| 313 | 0 | 0 | 0 | 0 | 0/0/0 | 0 | 0 | 0 | - |
| 364 | 0 | 0 | 0 | 0 | 0/0/0 | 0 | 0 | 0 | - |
| 436 | 0 | 0 | 0 | 0 | 0/0/0 | 0 | 0 | 0 | - |

## Recon cross-checks

Prior recon expected quests 1334, 1336, 1341, 1343 to be client-only (hard restore).
Actual per-source presence (zone 13, by Quest번호 hz header):

| Quest | v31 | v92 | client | classification |
|-------|-----|-----|--------|----------------|
| 1334 | Y | Y | Y | in-v92 (present, not a gap) |
| 1336 | Y | Y | Y | in-v92 (present, not a gap) |
| 1341 | Y | Y | Y | in-v92 (present, not a gap) |
| 1343 | Y | Y | Y | in-v92 (present, not a gap) |

Finding: all four are full quests present in v31, v92, and the client. The recon 'client-only' expectation does NOT hold against current on-disk data; they are not a restoration gap.

## Zone 13

### NPC templates (v92 file is a patch-001 overlay; compared against HEAD)
- v31: 57 | v92 HEAD: 57 | client shards: 1 (57 templates)
- present in both: 57
- MISSING in v92 HEAD: none

### NPC skills / AI
- Skills: v31 57 | v92 57 | missing 0
- AI: v31 45 | v92 45 | missing 0

### Territory / spawns
- Groups: v31 25 | v92 HEAD 25 | missing 0

### Quests
- Zone quest set (Quest번호 hz header): v31 65 | v92 65 | client 63
- Registered in QuestGroupList (of the union): v31 25 | v92 25 | client 16
- v31-only (easy restore): none
- client-only (hard restore): none

### Quest compensations
- v31 filled/total: 75/77 | v92 HEAD filled/total: 0/77
- Reward lost in v92 HEAD (75): 1301(stub), 1302(stub), 1303(stub), 1304(stub), 1305(stub), 1306(stub), 1307(stub), 1308(stub), 1309(stub), 1310(stub), 1311(stub), 1312(stub), 1313(stub), 1315(stub), 1316(stub), 1317(stub), 1318(stub), 1319(stub), 1321(stub), 1322(stub), 1323(stub), 1324(stub), 1325(stub), 1326(stub), 1327(stub), 1328(stub), 1329(stub), 1330(stub), 1331(stub), 1332(stub), 1333(stub), 1334(stub), 1335(stub), 1336(stub), 1337(stub), 1338(stub), 1339(stub), 1340(stub), 1341(stub), 1343(stub)

### Loot compensations
- CCompensation: v31 npcs 50 | v92 HEAD npcs 50 | worktree npcs 0
    - PATCH-001 OVERLAY: working tree stripped to 0 npcs (HEAD has 50); this is deliberate tuning, not content loss
- ECompensation: v31 npcs 49 | v92 HEAD npcs 10 | worktree npcs 47
    - npcTemplateIds in v31 missing from v92 HEAD (49): 1, 2, 3, 4, 5, 6, 7, 8, 9, 102, 111, 301, 302, 303, 304, 555, 556, 557, 558, 601, 888, 901, 902, 999, 1001, 1002, 1003, 1004, 1011, 300541
    - gap after patch-001 overlay (v31 missing from working tree): 301, 888, 999 (3 remain)

### Dialogs
- QuestDialog: client shards 63 | v31 files 0 | v92 files 65
- VillagerDialog: client shards tagged to this zone 0 (villager dialogs are keyed globally, not by zone; true per-zone attribution needs the villager-NPC join done by a future villager-restore module). v31: absent by design.

## Zone 64

### NPC templates
- v31: 51 | v92 HEAD: 51 | client shards: 1 (50 templates)
- present in both: 51
- MISSING in v92 HEAD: none

### NPC skills / AI
- Skills: v31 3 | v92 3 | missing 0
- AI: v31 4 | v92 4 | missing 0

### Territory / spawns
- Groups: v31 2 | v92 HEAD 2 | missing 0

### Quests
- Zone quest set (Quest번호 hz header): v31 0 | v92 0 | client 0
- Registered in QuestGroupList (of the union): v31 0 | v92 0 | client 0
- v31-only (easy restore): none
- client-only (hard restore): none

### Quest compensations
- v31 filled/total: 0/0 | v92 HEAD filled/total: 0/0
- Reward lost in v92 HEAD: none

### Loot compensations
- CCompensation: absent in both v31 and v92 HEAD
- ECompensation: absent in both v31 and v92 HEAD

### Dialogs
- QuestDialog: client shards 0 | v31 files 0 | v92 files 0
- VillagerDialog: client shards tagged to this zone 45 (villager dialogs are keyed globally, not by zone; true per-zone attribution needs the villager-NPC join done by a future villager-restore module). v31: absent by design.

## Zone 213

### NPC templates
- v31: 93 | v92 HEAD: 93 | client shards: 1 (87 templates)
- present in both: 93
- MISSING in v92 HEAD: none

### NPC skills / AI
- Skills: v31 8 | v92 8 | missing 0
- AI: v31 3 | v92 3 | missing 0

### Territory / spawns (v92 file is a patch-001 overlay; compared against HEAD)
- Groups: v31 4 | v92 HEAD 4 | missing 0

### Quests
- Zone quest set (Quest번호 hz header): v31 0 | v92 9 | client 0
- Registered in QuestGroupList (of the union): v31 0 | v92 0 | client 0
- v31-only (easy restore): none
- client-only (hard restore): none

### Quest compensations
- v31 filled/total: 0/0 | v92 HEAD filled/total: 0/10
- Reward lost in v92 HEAD: none

### Loot compensations
- CCompensation: absent in both v31 and v92 HEAD
- ECompensation: absent in both v31 and v92 HEAD

### Dialogs
- QuestDialog: client shards 0 | v31 files 0 | v92 files 9
- VillagerDialog: client shards tagged to this zone 79 (villager dialogs are keyed globally, not by zone; true per-zone attribution needs the villager-NPC join done by a future villager-restore module). v31: absent by design.

## Zone 313

### NPC templates
- v31: 8 | v92 HEAD: 8 | client shards: 1 (8 templates)
- present in both: 8
- MISSING in v92 HEAD: none

### NPC skills / AI
- Skills: v31 2 | v92 2 | missing 0
- AI: v31 2 | v92 2 | missing 0

### Territory / spawns
- Groups: v31 1 | v92 HEAD 1 | missing 0

### Quests
- Zone quest set (Quest번호 hz header): v31 0 | v92 0 | client 0
- Registered in QuestGroupList (of the union): v31 0 | v92 0 | client 0
- v31-only (easy restore): none
- client-only (hard restore): none

### Quest compensations
- v31 filled/total: 0/0 | v92 HEAD filled/total: 0/0
- Reward lost in v92 HEAD: none

### Loot compensations
- CCompensation: absent in both v31 and v92 HEAD
- ECompensation: absent in both v31 and v92 HEAD

### Dialogs
- QuestDialog: client shards 0 | v31 files 0 | v92 files 0
- VillagerDialog: client shards tagged to this zone 8 (villager dialogs are keyed globally, not by zone; true per-zone attribution needs the villager-NPC join done by a future villager-restore module). v31: absent by design.

## Zone 364

### NPC templates
- v31: 8 | v92 HEAD: 8 | client shards: 1 (8 templates)
- present in both: 8
- MISSING in v92 HEAD: none

### NPC skills / AI
- Skills: v31 2 | v92 2 | missing 0
- AI: v31 3 | v92 3 | missing 0

### Territory / spawns
- Groups: v31 1 | v92 HEAD 1 | missing 0

### Quests
- Zone quest set (Quest번호 hz header): v31 0 | v92 0 | client 0
- Registered in QuestGroupList (of the union): v31 0 | v92 0 | client 0
- v31-only (easy restore): none
- client-only (hard restore): none

### Quest compensations
- v31 filled/total: 0/0 | v92 HEAD filled/total: 0/0
- Reward lost in v92 HEAD: none

### Loot compensations
- CCompensation: absent in both v31 and v92 HEAD
- ECompensation: absent in both v31 and v92 HEAD

### Dialogs
- QuestDialog: client shards 0 | v31 files 0 | v92 files 0
- VillagerDialog: client shards tagged to this zone 8 (villager dialogs are keyed globally, not by zone; true per-zone attribution needs the villager-NPC join done by a future villager-restore module). v31: absent by design.

## Zone 436

### NPC templates (v92 file is a patch-001 overlay; compared against HEAD)
- v31: 8 | v92 HEAD: 8 | client shards: 1 (8 templates)
- present in both: 8
- MISSING in v92 HEAD: none

### NPC skills / AI
- Skills: v31 5 | v92 5 | missing 0
- AI: v31 6 | v92 6 | missing 0

### Territory / spawns
- Groups: v31 4 | v92 HEAD 4 | missing 0

### Quests
- Zone quest set (Quest번호 hz header): v31 0 | v92 0 | client 0
- Registered in QuestGroupList (of the union): v31 0 | v92 0 | client 0
- v31-only (easy restore): none
- client-only (hard restore): none

### Quest compensations
- v31 filled/total: 0/0 | v92 HEAD filled/total: 0/0
- Reward lost in v92 HEAD: none

### Loot compensations
- CCompensation: absent in both v31 and v92 HEAD
- ECompensation: absent in both v31 and v92 HEAD

### Dialogs
- QuestDialog: client shards 0 | v31 files 0 | v92 files 0
- VillagerDialog: client shards tagged to this zone 3 (villager dialogs are keyed globally, not by zone; true per-zone attribution needs the villager-NPC join done by a future villager-restore module). v31: absent by design.

## VillagerDialog corpus (global signal)

- Old client VillagerDialog shards: 4468
- v92 VillagerDialog files: 395 (7922 VillagerDialog entries)
- v31: no VillagerDialog directory (absent by design).
- Per-zone attribution is deferred to the villager-restore module (join via villager NPCs).

## Restoration worklist

### Easy path (restore from v31 server datasheet)
- Zone 13: 75 quest rewards, 3 loot-comp npc entries (vs HEAD baseline: 49)

### Hard path (reconstruct from old client DataCenter)
- No client-only quests found in surveyed zones.

### Overlay (patch-001 tuning, NOT restoration scope)
- Zone 13: working-tree overlay on NpcData, CCompensation(stripped)
- Zone 213: working-tree overlay on TerritoryData
- Zone 436: working-tree overlay on NpcData

