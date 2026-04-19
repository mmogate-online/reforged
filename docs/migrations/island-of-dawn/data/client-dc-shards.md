# Client DC Shard Mapping — IoD Zones

IoD zones: 13, 64, 213, 313, 364, 416

## v31 Path

`Z:\tera pserver\v31.04\client-dc_v31\DataCenter_Final_EUR_v31\`

## v92 Path

`D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR\`

---

## Zone-Partitioned Files

### NpcData

| Zone | v31 Shard | v92 Shard |
|------|-----------|-----------|
| 13   | NpcData-00011.xml | NpcData-00011.xml |
| 64   | NpcData-00061.xml | NpcData-00061.xml |
| 213  | NpcData-00114.xml | NpcData-00112.xml |
| 313  | NpcData-00158.xml | NpcData-00156.xml |
| 364  | NpcData-00164.xml | NpcData-00162.xml |
| 416  | NpcData-00196.xml | NpcData-00194.xml |

### TerritoryData

| Zone | v31 Shard | v92 Shard |
|------|-----------|-----------|
| 13   | TerritoryData-00020.xml | TerritoryData-00018.xml |
| 64   | TerritoryData-00238.xml | TerritoryData-00318.xml |
| 213  | TerritoryData-00046.xml | TerritoryData-00066.xml |
| 313  | TerritoryData-00100.xml | TerritoryData-00145.xml |
| 364  | TerritoryData-00112.xml | TerritoryData-00158.xml |
| 416  | TerritoryData-00152.xml | TerritoryData-00198.xml |

### AIData

**v31 does NOT have AIData folder.** v92 has AIData parallel to NpcData (same shard indices).

| Zone | v31 Shard | v92 Shard |
|------|-----------|-----------|
| 13   | N/A | AIData-00011.xml |
| 64   | N/A | AIData-00061.xml |
| 213  | N/A | AIData-00112.xml |
| 313  | N/A | AIData-00156.xml |
| 364  | N/A | AIData-00162.xml |
| 416  | N/A | AIData-00194.xml |

### Dungeon

| Continent | v31 Shard | v92 Shard |
|-----------|-----------|-----------|
| 9016 (zone 416) | Dungeon-00012.xml | Dungeon-00041.xml |

Open-world IoD zones (continent 13) have no Dungeon shard.

### DynamicGeoData

Zone 416 dungeon (continent 9016) has geo data in both versions:
- v31: `DynamicGeoData-00012.xml` — 15 ATF_GDT doors + 4 elevator doors + 1 shuttle (original IoD dungeon)
- v92: `DynamicGeoData-00041.xml` — 6 AEN doors (different dungeon mapped to same continent ID)

Copy v31-00012 content → v92-00041 to restore original IoD dungeon geometry.

| Zone | v31 Shard | v92 Shard |
|------|-----------|-----------|
| 416 (continent 9016) | DynamicGeoData-00012.xml | DynamicGeoData-00041.xml |

Open-world IoD zones have no meaningful DynamicGeoData in either version.

---

## Quest Files

### Quest (one shard per quest)

| Quest Range | v31 Shards | v92 Shards |
|-------------|------------|------------|
| 1301–1390   | Quest-00388 to Quest-00452 | Quest-00325 to Quest-00389 |
| 41501–41517 | Quest-01854 to Quest-01869 | Quest-01633 to Quest-01648 |

### QuestDialog

| Scope | v31 Shards | v92 Shards |
|-------|------------|------------|
| Zone 13 (1301–1390) | QuestDialog-00430 to QuestDialog-00494 (65 shards) | QuestDialog-00325 to QuestDialog-00389 |
| Zone 416 (41501–41517) | None | QuestDialog-01623 to QuestDialog-01631 |

Note: v31 only has zone 13 dialog shards.

### QuestCompensationData

| Quest Range | v31 Shard | v92 Shard |
|-------------|-----------|-----------|
| 1301–1390   | QuestCompensationData-00010.xml | QuestCompensationData-00012.xml |
| 41501–41508 | QuestCompensationData-00048.xml | QuestCompensationData-00060.xml |

### StrSheet_Quest (one shard per quest)

| Quest Range | v31 Shards | v92 Shards |
|-------------|------------|------------|
| 1301–1390   | StrSheet_Quest-00431 to StrSheet_Quest-00495 | StrSheet_Quest-00326 to StrSheet_Quest-00390 |
| 41501–41517 | StrSheet_Quest-02079 to StrSheet_Quest-02094 | StrSheet_Quest-01741 to StrSheet_Quest-01756 |

---

## Monolithic / Global Files — Investigation Results

All monolithic files investigated; **none require merging**:

| File | v31 Shards | v92 Shards | Action | Reason |
|------|------------|------------|--------|--------|
| ContinentData | 00000 | 00000 | No action | IoD continents (13, 9016) identical; v92 only adds `channelMax` |
| NpcShape | 00000 | 00000 | No action | 150 IoD shapes functionally identical; v92 adds `name` attr + 776 new shapes |
| StrSheet_Npc | 00000 | 00000 | Deferred | v92 has 1,836 entries vs 630; investigate only if NPC names wrong in-game |
| StrSheet_ZoneName | 00000 | 00000 | No action | IoD zone names (13, 64, 416) identical |

---

## Key Findings

1. **Shard indices differ** between v31/v92 for the same zones — must map by content (huntingZoneId), not by index
2. **AIData absent in v31** — v92 AIData has no ID linkage to NPC templates; safe to leave as-is
3. **DynamicGeoData zone 416** — v31 has original IoD dungeon geometry; must copy v31-00012 → v92-00041
4. **QuestDialog zone 416 absent in v31** — v92 has dialog shards for 41501-41517 but v31 doesn't
5. **QuestCompensationData** — both shards are IoD-exclusive; safe to overwrite directly
6. **Dungeon shard** — v31's Dungeon-00012 is an empty skeleton; no action needed
