# Island of Dawn — Quest Inventory

## Summary

| Metric | Count |
|--------|-------|
| Total unique quest IDs | 65 |
| Mission quests (미션) | 25 |
| Side quests (일반) | 40 (includes 16 prologue class variants + 1 zoneless) |
| Zones with active quests | 4 (64, 213, 415, 416) |
| Zones with no quests | 3 (13, 313, 364) |
| Story groups | 2 (group 1, 2) |
| Excluded | Story group 18 (Noctenium Arc, level 60 — out of scope) |

## Story Group 1 — Entry Arc (levels 1–6, 18 quests)

| Quest ID | Title | Category | Level | connectedTo | Zone |
|----------|-------|----------|-------|-------------|------|
| 1301 | Dawn's Twilight | 미션 | 1 | 1329 | 213 |
| 1304 | Making the Rounds | 미션 | 1 | 1329 | 213 |
| 1371 | Warrior Training | 미션 | 2 | terminal | 213 |
| 1372 | Lancer Training | 미션 | 2 | terminal | 213 |
| 1373 | Slayer Training | 미션 | 2 | terminal | 213 |
| 1374 | Berserker Training | 미션 | 2 | terminal | 213 |
| 1375 | Archer Training | 미션 | 2 | terminal | 213 |
| 1376 | Sorcerer Training | 미션 | 2 | terminal | 213 |
| 1377 | Priest Training | 미션 | 2 | terminal | 213 |
| 1378 | Mystic Training | 미션 | 2 | terminal | 213 |
| 1379 | Gunner Training | 미션 | 2 | terminal | 213 |
| 1329 | Going Above and Beyond | 미션 | 4 | terminal | 64 |
| 1384 | Getting to Know the Garrison | 미션 | 4 | terminal | 64 |
| 1303 | The Secret Life of Trees | 미션 | 4 | terminal | 64, 213 |
| 1331 | Climbing through the Ranks | 미션 | 5 | terminal | 64 |
| 1382 | Gathering Your Strength (A) | 미션 | 5 | terminal | 64 |
| 1383 | Gathering Your Strength (B) | 미션 | 5 | terminal | 64 |
| 1305 | A Clue in the Dark | 미션 | 6 | terminal | 64, 213 |

**Chain:** 1301/1304 → 1329 → terminal (chain ends)

## Story Group 2 — Mid Arc (levels 7–10, 7 quests)

| Quest ID | Title | Category | Level | connectedTo | Zone |
|----------|-------|----------|-------|-------------|------|
| 1311 | Redeployment | 미션 | 7 | terminal | 64 |
| 1350 | Strange Attractors | 미션 | 8 | terminal | 64 |
| 1309 | Acharak Attacks | 미션 | 8 | terminal | 64 |
| 1313 | Into the Gorge | 미션 | 8 | 1339 | 213, 64 |
| 1315 | Putting the Pieces Together | 미션 | 9 | terminal | 64 |
| 1316 | Dark Revelations | 미션 | 9 | terminal | 64 |
| 1317 | Ride Off into the Sunset | 미션 | 10 | terminal | 64 |

**Chain:** Multiple entry points → chain terminal. Quest 1313 → 1339 ("Sersine, She Seeks Shackles", zoneless side quest — included in migration).

## Story Group 18 — Noctenium Arc (level 60, 3 quests) — EXCLUDED

| Quest ID | Title | Category | Level | connectedTo | Zone |
|----------|-------|----------|-------|-------------|------|
| 15101 | Tell Me of Noctenium | 미션 | 60 | terminal | 213, 64 |
| 15102 | Noctenium Knowledge | 미션 | 60 | terminal | 213 |
| 15103 | Access and Allies | 미션 | 60 | terminal | (zone 151) |

**Excluded from migration scope.** High-level quests are not part of the IoD starting zone restoration. These transition to zone 151 (Noctenium Realm) and reference NPCs in zones 151 and 84.

## Side Quests — Zone 213 (7 quests)

| Quest ID | Title | Category | Level | connectedTo |
|----------|-------|----------|-------|-------------|
| 1302 | Another Fine Mess | 일반 | 1 | terminal |
| 1306 | Traces of Darkness | 일반 | 7 | terminal |
| 1307 | Live by the Sword | 일반 | 8 | terminal |
| 1308 | Essence of Foreboding | 일반 | 8 | terminal |
| 1385 | Always After Me Lucky Charms | 일반 | 3 | terminal |
| 1386 | Bombs Away | 일반 | 4 | terminal |
| 1389 | Emptying Pandora's Box | 일반 | 6 | terminal |

## Side Quests — Zone 64 (16 quests)

| Quest ID | Title | Category | Level | connectedTo |
|----------|-------|----------|-------|-------------|
| 1310 | A Clue in the Dark | 일반 | 8 | terminal |
| 1312 | The Dark Patrol | 일반 | 8 | terminal |
| 1321 | A Bridge Pretty Near | 일반 | 1 | 1322 |
| 1322 | Unrest in the Forest | 일반 | 1 | terminal |
| 1327 | Garrison in Distress | 일반 | 4 | terminal |
| 1330 | Horned Horrors | 일반 | 5 | terminal |
| 1335 | One of Our Couriers Is Missing | 일반 | 8 | terminal |
| 1338 | Chione's Report | 일반 | 7 | terminal |
| 1340 | Painful Disc-overies | 일반 | 8 | terminal |
| 1344 | Destroy All Destroyers | 일반 | 9 | terminal |
| 1345 | Desperately Seeking Sorcha | 일반 | 10 | 1346 |
| 1346 | Sorcha's Reckless Challenge | 일반 | 10 | terminal |
| 1349 | Gotta Kill 'Em All | 일반 | 8 | terminal |
| 1351 | Supply and Demand (A) | 일반 | 4 | terminal |
| 1352 | Supply and Demand (B) | 일반 | 4 | terminal |
| 1390 | Special Delivery | 일반 | 7 | terminal |

**Chains:** 1321 → 1322 → terminal; 1345 → 1346 → terminal. All others standalone.

## Side Quest — Zoneless (1 quest)

| Quest ID | Title | Category | Level | connectedTo | Dialog NPCs |
|----------|-------|----------|-------|-------------|-------------|
| 1339 | Sersine, She Seeks Shackles | 일반 | 8 | terminal | Lam (213), Barsabba (213), Nivek (213), Adria (64) |

No zone assignment in quest data. Successor to quest 1313 ("Into the Gorge"). Kill targets reference zone 13 monsters. All dialog NPCs are in IoD zones 213 and 64.

## Prologue Quests — Zone 415 (8 class-variant quests)

The prologue was an optional step where players tested their character at level 20 before starting at level 1 on IoD. The lore: a previous expedition arrived at the island and failed. After the prologue, the player starts fresh at level 1.

| Quest ID | Title | Category | Level | connectedTo |
|----------|-------|----------|-------|-------------|
| 41501 | Reach the Beach | 일반 | 20 | terminal |
| 41502 | Reach the Beach | 일반 | 20 | terminal |
| 41503 | Reach the Beach | 일반 | 20 | terminal |
| 41504 | Reach the Beach | 일반 | 20 | terminal |
| 41505 | Reach the Beach | 일반 | 20 | terminal |
| 41506 | Reach the Beach | 일반 | 20 | terminal |
| 41507 | Reach the Beach | 일반 | 20 | terminal |
| 41508 | Reach the Beach | 일반 | 20 | terminal |

One per class. Pure narrative escort — no combat. NPCs: Ahdun (415:1005), medics, Popomin (415:1007), Centurion (415:1053), Adjutant (415:1003). Post-shipwreck regrouping before pushing inland.

## Prologue Quests — Zone 416 (8 class-variant quests)

| Quest ID | Title | Category | Level | connectedTo |
|----------|-------|----------|-------|-------------|
| 41510 | The Prologue Ends | 일반 | 20 | terminal |
| 41511 | The Prologue Ends | 일반 | 20 | terminal |
| 41512 | The Prologue Ends | 일반 | 20 | terminal |
| 41513 | The Prologue Ends | 일반 | 20 | terminal |
| 41514 | The Prologue Ends | 일반 | 20 | terminal |
| 41515 | The Prologue Ends | 일반 | 20 | terminal |
| 41516 | The Prologue Ends | 일반 | 20 | terminal |
| 41517 | The Prologue Ends | 일반 | 20 | terminal |

One per class. Dialog NPCs reference zone 415 (IoD Coast), not 416.

## Cross-Zone Dependencies — Resolved

| Reference | Resolution |
|-----------|------------|
| `connectedTo 101` | **Not a real quest.** Value `101` is the quest chain terminal/null marker (raw XML: group 1, index 1). Means "chain ends here." No action needed. |
| `connectedTo 1339` | **Resolved.** Quest 1339 ("Sersine, She Seeks Shackles") exists in v31 as a zoneless level 8 side quest. All dialog NPCs in IoD zones 213/64. Included in migration scope. |
| Zone 415 (IoD Coast) | **No zone file migration needed.** Zone 415 is identical between v31 and v92 (44 territories, 107 spawns, all villager NPCs). But 8 "Reach the Beach" quests (41501–41508) added to quest scope. |
| Noctenium arc (15101–15103) | **Excluded.** High-level content not part of IoD starting zone restoration. |
| Zone 151 / Zone 84 NPCs | **N/A.** Only referenced by excluded noctenium arc. |

## Notes on Dangling Quest Chains

IoD quest chains terminate with `connectedTo: 101` (chain terminal). In the original game, subsequent quests in other zones would pick up via `prerequisite` fields referencing IoD quest IDs. Some of these successor quests may not exist or may have different prerequisites in v92.

**Strategy:** Accept dangling chains for initial migration. Smooth out connections to v92 questline post-migration using DSL tool.

## Quest Dependency Chain

Based on domain documentation, each quest touches multiple file systems:

| System | Files | Migration Impact |
|--------|-------|-----------------|
| Quest definitions | `QuestData/{id:D6}.quest` | Copy per-quest files |
| Quest dialogs | `QuestDialog/QuestDialog_*.xml` | Zone-scoped, naming differs between versions |
| Quest strings | `StrSheet_Quest.xml` | Selective merge by quest StringId |
| Quest compensation | `QuestCompensationData_xxx.xml` (156 files in v92) | Separate from NPC CCompensation — keyed by quest GlobalId |
| Quest group list | `QuestGroupList.xml` | Merge story groups 1 and 2 |
| NPC visibility | `NpcData_*.xml` (appearQuestId/hideQuestId) | Already handled by zone file copy in Phase 1 |
| Territory triggers | `TerritoryData_*.xml` (quest territory entries) | Already handled by zone file copy in Phase 1 |
| Reward items | Various item files | Class weapon/armor bags must exist in v92 |
| Daily quest pools | `DailyQuest.xml` | Check if IoD has daily quest entries |
| Vanguard activities | `DailyPlayGuideQuest.xml` | Check if IoD has vanguard entries |

**Key insight:** NPC visibility gating (`appearQuestId`/`hideQuestId` in NpcData) and territory spawn controls (`voidSpawn`, `conditionalSpawn` in TerritoryData) are already preserved by the Phase 1 zone file copy. The quest-NPC linkage is embedded in the zone files themselves.

## Reward Items Referenced

Quest rewards reference class weapon/armor bags and consumables. These items must exist in v92 for rewards to function.

| Item IDs | Context | Type |
|----------|---------|------|
| 10009–10016, 55006 | Class weapon bags (quest 1304) | Equipment bags |
| 12129–12136, 55271 | Class weapon bags (quest 1303) | Equipment bags |
| 12137–12144, 55272 | Class weapon bags (quest 1315) | Equipment bags |
| 10593–10600, 55079 | Class weapon bags (quest 1316) | Equipment bags |
| 17404–17410 | Class glove bags (quest 1303) | Equipment bags |
| 17710–17716 | Class chest/glove bags (quest 1331) | Equipment bags |
| 15019–15027 | Class armor bags (quest 1305) | Equipment bags |
| 15667–15673 | Class armor bags (quest 1317) | Equipment bags |
| 17703–17709 | Class armor bags (quest 1322) | Equipment bags |
| 15020–15026 | Class gear bags (quest 1330) | Equipment bags |
| 8007 | Consumable (quest 1329, 1345) | Item |
| 7200 | Consumable (quest 1329, 1386) | Item |
| 7100, 7104, 7108 | Token items (quest 1313) | Token |
| 6048 | Consumable (quest 1384, 1351/1352) | Item |
| 8200 | Consumable (quest 1307) | Item |
| 160 | Consumable (quest 1390) | Item |
| ~~143, 151, 159~~ | ~~Noctenium items (quest 15102)~~ | ~~Excluded~~ |
| ~~1301, 1207, 1208~~ | ~~Noctenium materials (quest 15102)~~ | ~~Excluded~~ |

## QuestDialog File Mapping

v31 uses zone-partitioned naming: `QuestDialog_<zone>_<n>.xml`
v92 uses flat per-quest naming: `QuestDialog_<questId>.xml`

Key dialog NPCs and their zones:

| NPC | Zone | Role |
|-----|------|------|
| Lam | 213, templateId 1014 | Primary quest giver (story groups 1 & 2) |
| Barsabba | 213, templateId 1106 | Training/combat readiness |
| Adria | 64, templateId 1001 | Tower Base commander |
| Teil | 64, templateId 1009 | Conspiracy investigator |
| Leander | 213, templateId 1008 | Lore NPC — search for Elleon |
| Ahdun | 415, templateId 1005 | Prologue beach commander |
| Todoro | 213, templateId 1150 | Noctenium arc guide — excluded from migration |
