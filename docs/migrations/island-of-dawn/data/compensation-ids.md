# Island of Dawn — Compensation Data (v31)

Source: v31 MCP `audit_zone_loot` for zones 13, 64, 213, 313, 364, 416

## Per-Zone Loot Summary

| Zone | NPCs with Loot | Compensation File |
|------|---------------|-------------------|
| 13 | 50 | CCompensation_0013.xml |
| 64 | 0 | none |
| 213 | 0 | none |
| 313 | 0 | none |
| 364 | 0 | none |
| 416 | 0 | none |

Only zone 13 has CCompensation data. All other zones are quest/hub zones with no loot.

## Zone 13 — NPCs with Compensation (50 entries)

| npcTemplateId | Korean Name |
|---------------|-------------|
| 1 | Pigling |
| 2 | Sporewalker |
| 3 | (no English name) |
| 4 | (no English name) |
| 5 | (no English name) |
| 6 | Kariagon |
| 7 | Disc Reaper |
| 8 | Runekeeper |
| 9 | Destroyer |
| 101 | (no name) |
| 102 | Docile Terron |
| 111 | Gentle Pigling |
| 301 | (no English name) |
| 302 | (no English name) |
| 303 | (no English name) |
| 304 | (no English name) |
| 555 | Scion Scout |
| 556 | Scion Scout |
| 557 | Scion Scout |
| 558 | Scion Scout |
| 601 | (no English name) |
| 888 | Training Dummy |
| 901 | Orcan Guardian |
| 902 | (no English name) |
| 999 | (no name) |
| 1001 | Vekas |
| 1002 | Acharak |
| 1003 | Acharak's Soldier |
| 1004 | Kugai |
| 1011 | Terron Saboteur |
| 300910 | Prowling Cromos |
| 300911 | (variant) |
| 300920 | (variant) |
| 300921 | Noruk |
| 300930 | (variant) |
| 300931 | Ghilliedhu |
| 300932 | Horned Ghilliedhu |
| 300933 | (variant) |
| 300941 | (variant) |
| 300942 | Terron Thrall |
| 300943 | (variant) |
| 300944 | (variant) |
| 300945 | (variant) |
| 300951 | Dark Raider |
| 300960 | Devoted Ebon Imp |
| 301191 | Stonebeak Raider |
| 301193 | Stonebeak Brigand |
| 301194 | Stonebeak Highcrest |
| 300541 | (variant) |
| 300542 | (variant) |

Items dropped: exclusively healing motes (item 8000 — Rejuvenation Mote, item 8005 — Healing Mote).

## Files to Copy

| File | In v31 | In v92 | Action |
|------|--------|--------|--------|
| CCompensation_0013.xml | Yes | Yes | **Overwrite** v92 with v31 version |

Only one CCompensation file is needed. It already exists in v92 (with endgame loot tables) and must be overwritten with the v31 original content.

## Quest Compensation (QuestCompensationData)

All 65 IoD quests reference only two compensation IDs:
- **ID 0**: Null sentinel (file does not exist in either version). Means "no reward" for intermediate steps.
- **ID 1**: `QuestCompensationData_1.xml` — empty placeholder file, exists in both versions.

**No QuestCompensationData files need to be copied.** The actual quest rewards are embedded in the `.quest` files themselves, not in QuestCompensationData.
