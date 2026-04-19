# Island of Dawn — Phase 2 Execution Log

## Phase 2a — Compensation / Loot Tables

**Action:** Copied `CCompensation_0013.xml` from v31 to v92.

Only zone 13 has loot (50 NPCs dropping healing motes: items 8000, 8005). All other IoD zones have zero loot. Single file overwrite.

## Phase 2b — Quest Data (65 quests)

### Step 1: Copy .quest files
- Copied 65/65 `.quest` files from v31 `QuestData/` to v92 `QuestData/`
- All files already existed in v92 — pure overwrite

### Step 2: Copy QuestDialog files (with rename)
- Copied 65/65 QuestDialog files from v31 to v92
- v31 naming: `QuestDialog_{zone}_{local}.xml` (zone 13 for main quests, zone 415 for prologue)
- v92 naming: `QuestDialog_{questId}.xml` (flat per-quest)
- All prologue quests (41501-41517) use zone 415 in v31 — no zone 416 dialog files exist in v31

### Step 3: Merge StrSheet_Quest.xml
- Replaced 1,009 IoD quest strings (id ranges 1301000-1390999, 41501000-41517999)
- 0 strings added (identical count between versions)
- 4 strings had content differences (minor text edits); overwritten with v31 versions:
  - 1331015: Featherlight Potion text
  - 1382003: Quest objective text
  - 1382004: Gurney reference text
  - 1383003: Lilni dialog text

### Step 4: Merge QuestGroupList.xml
- Replaced StoryGroup 1 and 2 entries with v31 versions
- Replaced HuntingZone id=13 entry with v31 version
- v92 extra entries (ids 2000-2103) left untouched

### QuestCompensationData
- Does not need migration: all IoD quests reference compensation ID 0 (null) or 1 (empty placeholder)
- `QuestCompensationData_1.xml` exists in both versions, identical

## Phase 2c — NPC Behavioral Files

**No merge required.** Investigation found all IoD NPC entries identical between v31 and v92:

| File | IoD Entries | Identical? |
|------|------------|------------|
| NpcBasicAction.xml | 11 entries (3009xxx range) | Yes (v92 only adds cosmetic attrs) |
| NpcShape.xml | 300xxx shapes | Yes (byte-for-byte) |
| NpcSocialData.xml | 34 entries | Yes |
| NpcReactionData.xml | 51 entries | Yes |
| NpcAbnormalityBalance.xml | N/A (global tuning) | N/A |
| NpcSeatData.xml | N/A (vehicle seats) | N/A |

## Phase 2d — String Tables

### StrSheet_Npc.xml
- **No merge needed.** v31 does not have `StrSheet_Npc.xml` (uses `StrSheet_Creature.xml` instead). v92's version is UI strings (Dialog/Quest/Shop labels), not NPC names. NPC display names come from client DC.

### StrSheet_ZoneName.xml
- **No merge needed.** IoD zone names (13, 64, 416) are identical between v31 and v92.

## Summary

| Sub-phase | Files Modified | Action |
|-----------|---------------|--------|
| 2a — Loot | 1 | CCompensation_0013.xml overwritten |
| 2b — Quests | 132 | 65 .quest + 65 QuestDialog + StrSheet_Quest + QuestGroupList |
| 2c — NPC Behavioral | 0 | All IoD entries identical — no merge needed |
| 2d — Strings | 0 | StrSheet_Npc N/A, StrSheet_ZoneName identical |
| **Total** | **133** | |
