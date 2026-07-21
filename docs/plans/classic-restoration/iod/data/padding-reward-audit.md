# IoD Padding: Side-Quest Reward Audit (34 enabled quests)

Audit only. No datasheet modified. Question answered: do the enabled IoD side quests reward any gear, and what does each pay out on the live server now, versus v31 and v17?

Sources:
- LIVE (what the server pays now): `D:\dev\mmogate\tera92\server\Datasheet\CompensationData\QuestCompensationData_13.xml`
- v31: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet\CompensationData\QuestCompensationData_13.xml`
- v17 index: `reforged\docs\plans\iod-alpha-content-loop\data\v17-quests.json`
- Item metadata: datasheet-v92 MCP (`batch_lookup` on all 54 distinct reward item ids)

## Headline answer

- **7 of 34** side quests grant gear on LIVE: 1319, 1322, 1323, 1325, 1326, 1330, 1347. Live matches v31 exactly (same 7, same items).
- **25 of 34** carry ZERO gear in BOTH v31 and v17 (and therefore on live): 1302, 1318, 1321, 1324, 1327, 1328, 1332, 1333, 1334, 1335, 1336, 1338, 1339, 1340, 1341, 1343, 1344, 1345, 1346, 1348, 1349, 1351, 1352, 1386, 1390. These pay exp + gold only, sometimes plus a consumable (potion, charm, scroll, event item). No gear anywhere, in any source.
- The v17 index and v31 disagree on which side quests carry gear. v17 lists gear on **6** (1312, 1319, 1322, 1325, 1337, 1347); v31/live list gear on **7** (1319, 1322, 1323, 1325, 1326, 1330, 1347). Only 4 quests carry gear in BOTH v17 and v31: 1319, 1322, 1325, 1347.
- Two quests (1312 feet i9, 1337 hand i9) have gear in the v17 index but NOT in v31 and NOT on live. Three quests (1323, 1326, 1330) have gear in v31/live but the v17 index gives them consumables instead.
- All gear that exists on side quests sits in levels 1 to 6. The entire level 7 to 9 side-quest band grants no gear on live.

## Per-quest table (34 rows)

Gear notation: slot + item-level (e.g. `feet i7`). "consumable" = potion/charm/scroll/event item only. Levels are the quest min level.

| qid | lvl | title | LIVE reward | v31 reward | v17 reward | verdict |
|---|---|---|---|---|---|---|
| 1302 | 1 | Another Fine Mess | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1312 | 8 | The Dark Patrol | exp/gold | exp/gold | feet i9 (8 classic) | NO-GEAR live/v31; v17-only gear |
| 1318 | 1 | Hunting the Beasts | exp/gold + consumable | exp/gold | exp/gold + consumable | NO-GEAR |
| 1319 | 2 | Dwellers of the Island | weapon i2/i3 (12 cls) | weapon i3 (9 cls) | weapon i3 (8 cls) | GEAR (weapon) |
| 1321 | 1 | A Bridge Pretty Near | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1322 | 1 | Unrest in the Forest | feet i3 (12 cls) | feet i3 (9 cls) | feet i3 (8 cls) | GEAR (feet) |
| 1323 | 1 | Getting Some Answers | weapon i2 (12 cls) | weapon i2 (9 cls) | event item (no gear) | GEAR live/v31 (weapon); none v17 |
| 1324 | 2 | Essence and Sensibility | exp/gold + consumable | exp/gold | exp/gold + consumable | NO-GEAR |
| 1325 | 3 | The Perfect Cut | hand i3 (12 cls) | hand i3 (9 cls) | hand i3 (8 cls) | GEAR (hand) |
| 1326 | 5 | Mana out of Mudmen | feet i7 (12 cls) | feet i7 (9 cls) | consumables (no gear) | GEAR live/v31 (feet); none v17 |
| 1327 | 4 | Garrison in Distress | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1328 | 4 | Academic Theft | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1330 | 4 | Horned Horrors | hand i7 (12 cls) | hand i7 (9 cls) | event item (no gear) | GEAR live/v31 (hand); none v17 |
| 1332 | 6 | They'll Eat Anything | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1333 | 6 | Twice the Bark, Twice the Bite | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1334 | 6 | Investigating the Relics (Repeatable) | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1335 | 8 | One of Our Couriers is Missing | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1336 | 8 | Chione's Missing Cargo | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1337 | 8 | Searching for the Stolen Stones | exp/gold | exp/gold | hand i9 (8 classic) | NO-GEAR live/v31; v17-only gear |
| 1338 | 8 | Chione's Report | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1339 | 8 | Sersine, She Seeks Shackles | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1340 | 8 | Painful Disc-overies | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1341 | 8 | Bequest of the Dead (Repeatable) | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1343 | 9 | Answers Lead to More Questions | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1344 | 9 | Destroy All Destroyers | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1345 | 8 | Desperately Seeking Sorscha | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1346 | 8 | Sorcha's Reckless Challenge | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1347 | 6 | It Was a Rock...Crawler | hand i6 (12 cls) | hand i6 (9 cls) | hand i6 (8 cls) | GEAR (hand) |
| 1348 | 5 | Ferocious Flowering Felons | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1349 | 7 | Gotta Kill 'em All | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1351 | 4 | Supply and Demand | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1352 | 4 | Supply and Demand | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1386 | 4 | Bombs Away | exp/gold | exp/gold | exp/gold | NO-GEAR |
| 1390 | 6 | Special Delivery | exp/gold | exp/gold | exp/gold | NO-GEAR |

Notes on the gear pieces (all rareGrade 0, common):
- The armor is the ilvl17 progression set: `mail17`/`leather17`/`robe17` in hand and feet cuts. Hand at i3 (1325), i6 (1347), i7 (1330). Feet at i3 (1322), i7 (1326).
- The weapons are the `*_01` starter weapons at i2/i3 (1319, 1323), the same starter weapons the story quests 1304 and 1303 also hand out.
- No side quest grants a BODY (chest) piece in any source. No side quest grants a helmet, gloves proper, or accessory.

## Class-gating finding (question 3: did the side quests get the new-class rows?)

YES. Spec 04 appended the new-class rows to the SIDE quests, not only the story quests.

- Individual-weapon quests (1319, 1323): v31 had 8 classic classes plus engineer (9 rows). Live adds fighter (82006), assassin (58172), glaiver (59054/59353) to reach 12 rows.
- Armor quests (1322, 1326, 1330, 1347): v31 stored one row per class. Live consolidated them into three semicolon-grouped rows that already include the new classes, e.g. `class="lancer;berserker;engineer;fighter"`, `"warrior;slayer;archer;glaiver"`, `"sorcerer;priest;elementalist;assassin"`.

Coverage on the 7 live gear quests is the 12 classes: warrior, lancer, slayer, berserker, sorcerer, archer, priest, elementalist, engineer, fighter, assassin, glaiver.

NOT covered by any side-quest gear bag: **reaper (soulless)** and **gunner**. Neither appears in any reward row on the 7 gear quests, so a reaper or gunner character receives NO gear item from these quests (the `itemBag="class"` bag has no matching row for them, so it yields nothing). Reaper having no low-level gear is a known design fact; gunner is simply absent from these rows. The same reaper/gunner absence exists on the story quests (they carry no soulless/gunner weapon rows either), so this is not unique to side quests.

## Played-path effect

- A player on any of the 12 covered classes sees gear from up to 7 side quests, all at character level 1 to 6, and all in the hand/feet/weapon slots.
- A player on reaper or gunner sees zero gear from any of the 34 side quests.
- Regardless of class, no side quest grants gear above character level 6, and no side quest grants a body piece.

## Gap analysis for the design goal (visual set progression via side quests)

Where the data already supports it (live side-quest gear that exists to build on):

| band | slots side quests grant on live | quests |
|---|---|---|
| lvl 1-3 | weapon, feet, hand | 1319, 1323 (weapon); 1322 (feet); 1325 (hand) |
| lvl 4-6 | feet, hand | 1326 (feet i7); 1330, 1347 (hand) |
| lvl 7-9 | none | (all 7-9 side quests are exp/gold only) |

Where it does not (gaps against the story spine, which is the comparison for a full set look):

- **BODY (chest) slot: never granted by any side quest, in any band, in any source.** Body is story-only on live: 1303 (body i4, lvl 3), 1331 (body i5, lvl 5), 1305 (body i7, lvl 5), 1315 (body i8, lvl 9), 1317 (body i11, lvl 10). For a visual set, the chest is the most prominent slot and there is no side-quest source for it.
- **The entire level 7-9 band grants no side-quest gear on live.** Story covers that band (1305 full ilvl7 set at quest-level 5, 1315, 1316, 1317). Side quests in this band (1312, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1343, 1344, 1345, 1346, plus 1349 at lvl 7) all pay exp/gold only.
- **Weapon: side quests only grant it in band 1-3**, and it duplicates the starter weapon the story quests 1303/1304 already hand out. No side-quest weapon at level 4 or above.
- **Feet and hand appear only in bands 1-3 and 4-6.** No feet or hand side-quest reward at level 7 or above.

Story-spine baseline for reference (live gear-bearing story/training quests in HZ 13):

| qid | lvl | gear granted |
|---|---|---|
| 1303 | 3 | body i4, weapon i2/i3/i4 |
| 1304 | 1 | weapon i2 |
| 1305 | 5 | full set: body i7, feet i7, hand i7, weapon i7 |
| 1315 | 9 | body i8, weapon i7/i8 |
| 1316 | 9 | weapon i11/i12 |
| 1317 | 10 | body i11 |
| 1331 | 5 | body i5 |

## Factual summary for the ruling

- 7 of 34 side quests grant gear on the live server today (1319, 1322, 1323, 1325, 1326, 1330, 1347), all at character level 1 to 6, all hand/feet/weapon, all common grade. Live is identical to v31.
- 25 of 34 carry zero gear in v17, v31, and live. They pay exp/gold, some with a consumable.
- The v17 index differs from v31: it puts gear on 1312 and 1337 (never restored to live) and gives 1323/1326/1330 consumables instead of gear. Only 1319, 1322, 1325, 1347 carry gear in both classic sources.
- The new-class rows (fighter, assassin, glaiver, engineer) are present on the side quests, not only the story quests. Reaper and gunner get no gear from any of these quests.
- The design goal (visual set progression via side quests) is unsupported by the current data in two structural ways: no side quest grants a body/chest piece at any level, and the entire level 7 to 9 side-quest band grants no gear at all. Feet/hand exist only up to level 6 and weapon only up to level 3.
