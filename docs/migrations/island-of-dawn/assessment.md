# Island of Dawn — Technical Assessment

## Overview

The Island of Dawn exists in both v31 and v92 with identical zone IDs and continent structure. v92 didn't delete the zones — it repurposed them as an endgame BAM hunting ground (Dawnfall patch, March 2016). The original skeleton is preserved; only the content within changed.

Stepstone Isle (zone 827) was added in v92 as a dungeon-type replacement starting zone. It has no v31 equivalent.

## Version Comparison

### Zone Structure

Zone IDs 13, 64, 213, 313, 364, 416 exist in both versions on the same continents (13 and 9016). The structure is 1:1 — no zone ID remapping needed.

The major content difference is zone 13 (main hub): 57 NPCs in v31 vs 186 NPCs in v92. The jump reflects the endgame BAM population added by Dawnfall. Sub-zones (64, 213, 313, 364) and the prologue (416) have identical NPC counts.

### File Structure

- **v31:** 34 zone-partitioned files across 10 file types
- **v92:** 42 zone-partitioned files across 10 file types (same types)
- **Delta:** v92 has 8 extra files — `DynamicSpawn` and `FormationData` for sub-zones 64, 213, 313, 364 (endgame spawn patterns that v31 didn't need)

All 14 zone-partitioned file types that exist in v31 also exist in v92. No v31-only types. v92 adds 5 new zone-partitioned types globally (`ActiveRotate`, `FieldData`, `FishingTerritory`, `NpcPartData`, `PegasusPath`) but none of these appear for IoD zones.

## Server vs Client Data Split

**Important:** NPC template definitions (stats, models, type, skills) do NOT exist in the server datasheet. The server only has:
- **Zone-partitioned files** (`NpcData_*.xml`) — spawn points referencing template IDs by number
- **Monolithic support files** — behavioral data (`NpcBasicAction.xml`, `NpcShape.xml`, `NpcSocialData.xml`, `NpcAbnormalityBalance.xml`, etc.)

The NPC template data (what an NPC *is*) lives in the **client datacenter**. The MCP tools surface it as `NpcTemplate` entities, but that's read from the client DC, not the server datasheet.

This means the server-side migration is primarily zone-partitioned file copies + behavioral support files. The heavier NPC template work is a client-side concern.

### Server-side monolithic NPC files

| File | v31 | v92 | Content |
|------|-----|-----|---------|
| NpcBasicAction.xml | Yes | Yes | Default NPC behaviors |
| NpcShape.xml | Yes | Yes | NPC visual models/shapes |
| NpcSocialData.xml | Yes | Yes | NPC social interactions |
| NpcAbnormalityBalance.xml | Yes | Yes | NPC abnormality resistances |
| NpcSeatData.xml | Yes | Yes | NPC seating positions |
| NpcReactionData.xml | Yes | Yes | NPC reaction behaviors |
| NpcArena.xml | Yes | Yes | NPC arena configurations |
| DarkRiftNpcData.xml | Yes | Yes | Dark rift NPC data |
| NpcInteractionData.xml | No | Yes | v92-only |
| NpcSpawnEvent.xml | No | Yes | v92-only |
| StrSheet_Npc.xml | No | Yes | v92-only (server copy) |

## Tooling Assessment

### What DSL CAN do

- Apply loot table specs (CCompensation, ECompensation) — server-only, no client sync
- Sync string tables (StrSheet_Npc, StrSheet_Item) to client
- Sync item/equipment data to client
- Fine-tune individual entities post-migration

### What DSL CANNOT do

- Copy or manipulate zone-partitioned files (NpcData, AIData, TerritoryData, etc.) — the migration itself is file operations
- Merge entries in monolithic server files (NPC behavioral data, quest data)
- Handle the 8 v92-only files that need emptying

### Client DC Migration Strategy

**Decision: Direct v31 client DC file copy, not DSL sync.**

Rationale:
- We're restoring v31 content — the v31 client DC already has the exact data in the correct client format
- DSL sync filters through XSD, which could silently strip attributes needed for v31 fidelity
- Multiple entity types have no sync config (quests, AIData, DynamicGeoData, NpcShape, StrSheet_ZoneName)
- Direct copy has zero dependencies on DSL team work
- DSL sync will be adopted post-migration for ongoing maintenance of custom changes

### DSL Quest Support (Reference)

The DSL has full quest entity support — `.quest` files are XML with Korean tags, fully mapped:

| Entity Key | Server File(s) | Operations |
|---|---|---|
| `quests` | `QuestData/{id:D6}.quest` | create, update, delete, upsert |
| `questStrings` | `StrSheet_Quest.xml` | create, update, delete, upsert |
| `questDialogs` | `QuestDialog_{zone}.xml` | upsert, update |
| `questCompensations` | `QuestCompensation.xml` | keyed by questId |
| `dailyQuests` | `DailyQuest.xml` | create, update, delete, upsert, config |

This will be useful for post-migration fine-tuning via DSL specs.

### DSL Sync Template Coverage (Reference for Post-Migration)

| Entity | In Template? | Strategy | Post-Migration Use |
|--------|-------------|----------|---|
| NpcData | Yes | ZoneBased (numeric) | Adopt for future sync |
| TerritoryData | Yes | ZoneBased (numeric) | Adopt for future sync |
| DungeonData | Yes | ZoneBased (by continentId) | Adopt for future sync |
| ContinentData | Yes | monolithic | Adopt for future sync |
| QuestData | No (code exists, IdSorted) | IdSorted | File DSL request |
| QuestDialog | No | — | File DSL request |
| QuestCompensation | No | — | File DSL request |
| StrSheet_Quest | No | — | File DSL request |
| AIData | No | — | File DSL request |
| DynamicGeoData | No | — | File DSL request |
| NpcShape | No | — | File DSL request |
| StrSheet_ZoneName | No | — | File DSL request |

### Tooling Gaps

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No DSL schema for zone infrastructure files | Cannot use DSL for server-side migration | Direct file copy (trivial for zone-partitioned files) |
| No selective merge tool for monolithic XML | Server behavioral files and quest files need surgical edits | Build a Python merge script keyed on NPC template/quest IDs |
| Client DC shard mapping needed | Must map entity IDs to shard file numbers in both versions | Build a Python shard mapper script |

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking v92 content outside IoD during monolithic merges | High | Merge by NPC template ID / zone reference only; validate with MCP after |
| Missing NPC template dependencies (skills, passivities, abnormalities) | High | Trace full dependency chain from NPC templates before merging |
| Character creation entry point misconfigured | Medium | Test with new character after migration |
| Client-server mismatch after migration | Medium | Validate client DC against server state using MCP tools |
| Quest chain references to NPCs/items that don't exist in v92 | Medium | Full quest dependency audit needed before quest migration |

## Recommended Approach

### Phase 0 — Revert Pending Changes
Git checkout the pending changes in v92 server datasheet and client DC directories. These are from the patch 001 migration run.

### Phase 1 — Zone File Copy
Direct copy of 34 v31 zone-partitioned files → v92. Empty 8 v92-only extras to skeleton XML. Pure file operations.

### Phase 2 — Server Monolithic File Merging
Selective merge of IoD-related entries from v31 monolithic server files into v92. Includes NPC behavioral files, quest files, string tables, and loot tables. Use MCP tools to audit quest chains and NPC dependencies before merging.

### Phase 3 — Client DC Sync
Adopt sync config from DSL template for NpcData, TerritoryData, DungeonData, ContinentData (already mapped). Run `dsl sync` for all supported entities. For unsupported entities (AIData, DynamicGeoData, NpcShape, StrSheet_ZoneName), either request DSL template additions or perform manual client DC file copy from v31 client DC as fallback.

**v31 client DC available at:** `Z:\tera pserver\v31.04\client-dc_v31\DataCenter_Final_EUR_v31\`

### Phase 4 — Validation
Audit migrated zones using MCP v92 tools. Compare NPC populations, quest chains, loot tables against v31 reference data. Verify client-server consistency.

**Note:** Character creation entry point redirect (zone 827 → 416) is out of scope — handled manually by project lead.
