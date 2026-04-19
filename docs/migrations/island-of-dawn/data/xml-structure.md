# Island of Dawn — Monolithic XML File Structure

Source: First 50 lines of each file in v31 and v92

## Files That Need Merging

| File | Root Element | Child Element | Key Attr | v31 | v92 |
|------|-------------|---------------|----------|-----|-----|
| StrSheet_Quest.xml | `<StrSheet_Quest>` | `<String>` | `id` | Yes | Yes |
| QuestGroupList.xml | `<QuestGroupList>` | Nested sections | `id` | Yes | Yes |
| NpcBasicAction.xml | `<BasicActionData isNpc="1">` | `<BasicActions>` | `id` | Yes | Yes |
| NpcShape.xml | `<NpcShape>` | `<Shape>` | `id` | Yes | Yes |

## Files That Do NOT Need Merging

| File | Reason |
|------|--------|
| QuestCompensation.xml | Does not exist in either version |
| StrSheet_Npc.xml | v31 has no equivalent; v92 version is UI strings (Dialog/Quest/Shop labels), not NPC names |
| StrSheet_Creature.xml | v31 NPC names file; v92 uses client DC for NPC names, not server datasheet |
| NpcBasicAction.xml | All 11 IoD entries (3009xxx range) identical between v31/v92. v92 only adds schema attrs (`desc=""`, `id="1"`) |
| NpcShape.xml | All IoD shapes (300xxx) byte-for-byte identical. v92 only adds new non-IoD shapes (203xxx) |
| NpcSocialData.xml | All 34 IoD social entries identical. v92 only adds 1 non-IoD entry |
| NpcReactionData.xml | All 51 IoD reaction entries identical. v92 adds 373 new non-IoD entries |
| NpcAbnormalityBalance.xml | Global tuning table, no NPC-template-specific entries for IoD |
| NpcSeatData.xml | Battleground vehicle seats only, no IoD-specific entries |

## StrSheet_Quest.xml

- Flat list of `<String id="N" string="text" />` entries
- Quest string IDs follow pattern: `StringId = GlobalId * 1000 + StringIndex`
- IoD quest IDs: 1301-1390, 41501-41517 -> string IDs in ranges 1301000-1390999 and 41501000-41517999
- v31 and v92 may have different text for shared system strings (e.g., id=22 differs)

## QuestGroupList.xml

Two nested sections:
1. `<QuestHuntingZoneList>` -> `<HuntingZone id="N" name="..." step="..." kind="...">`
   - v31 attributes: id, name, step, kind
   - v92 has extra entries (ids 2000-2103) without step/kind at the top
   - Need to merge/overwrite IoD hunting zone entries (id=13 area)
2. `<StoryGroupList>` -> `<StoryGroup id="N" name="...">`
   - Merge story groups 1 and 2

## NpcBasicAction.xml

- Root: `<BasicActionData isNpc="1">`
- Entry: `<BasicActions id="N" name="Korean name">` with deeply nested children
- Key: `id` is NPC template ID (same as huntingZone:templateId but flattened to a global shape/model ID)
- v92 adds minor attributes: `id` on `<Run>`/`<Wait>`, `desc` on `<Cylinder>`
- IoD NPC IDs are in the low range — zone-local IDs (1-1153) are NOT in this file; only global template IDs (300xxx range and zone 13 specific monsters)

## NpcShape.xml

- Flat list of `<Shape id="N" name="..." ...many attrs... />`
- Self-closing elements, no children
- Key: `id` is the shape/model ID
- Need to identify which shape IDs are used by IoD NPCs
