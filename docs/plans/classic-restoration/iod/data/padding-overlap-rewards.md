# IoD Padding: Overlap Map and Reward-Conflict Screen (Level 1, workstreams 3 and 4)

Analysis only. No specs written, no datasheet modified. Source: v31 QuestData/StrSheet_Quest/QuestCompensationData_13; live reward sheet from v92 QuestCompensationData_13; item metadata from datasheet-v92 MCP.

## Summary

- Live set: 25 quests (not sentinel-disabled). Candidate set: 40 quests (prereq sentinel 99,99).
- Overlap classification: CLEAN 6, OVERLAP-BENIGN 29, AWKWARD-DUPLICATE 5.
- AWKWARD-DUPLICATE (5): 1306, 1307, 1308, 1310, 1343.
- REWARD-FLAG (3): 1310, 1326, 1330. All other candidates REWARD-CLEAN.
- Missing reward item ids on v92: NONE (all 102 distinct reward templateIds resolve on v92).
- Every candidate is typed 일반 (general/side) in v31, not 미션 (story mission); the story-branch candidates still carry story dialog and so remain contradiction risks.

## Live quest set (25)

| gid | lvl | type | title |
|---|---|---|---|
| 1301 | 1 | story | Dawn's Twilight |
| 1303 | 3 | story | The Secret Life of Trees |
| 1304 | 1 | story | Making the Rounds |
| 1305 | 5 | story | A Clue in the Dark |
| 1309 | 7 | story | Acharak Attacks |
| 1311 | 7 | story | Redeployment |
| 1313 | 7 | story | Into the Gorge |
| 1315 | 9 | story | Putting the Pieces Together |
| 1316 | 9 | story | Dark Revelations |
| 1317 | 10 | story | Ride Off into the Sunset |
| 1329 | 4 | story | Going Above and Beyond |
| 1331 | 5 | story | Climbing through the Ranks |
| 1350 | 8 | story | Strange Attractors |
| 1371 | 2 | story | Warrior Training |
| 1372 | 2 | story | Lancer Training |
| 1373 | 2 | story | Slayer Training |
| 1374 | 2 | story | Berserker Training |
| 1375 | 2 | story | Archer Training |
| 1376 | 2 | story | Sorcerer Training |
| 1377 | 2 | story | Priest Training |
| 1378 | 2 | story | Mystic Training |
| 1379 | 2 | story | Gunner Training |
| 1382 | 5 | story | Gathering Your Strength |
| 1383 | 5 | story | Gathering Your Strength |
| 1384 | 4 | story | Getting to Know the Garrison |

## Overlap map (40 candidates)

Overlap class: CLEAN (no shared objective/NPC/story beat) / OVERLAP-BENIGN (shares mob, collect or hub NPC with a live quest but different framing, acceptable; some carry a GATE note) / AWKWARD-DUPLICATE (retells or contradicts a live story beat, needs gating or removal).

| gid | lvl | title | class | evidence |
|---|---|---|---|---|
| 1306 | 6 | Traces of Darkness | AWKWARD-DUPLICATE | Cut story subplot 'A Blade to Remember' (Leander/Eria investigation). Journal beats 'What does this all mean?' / 'Take gauges to Eria' / 'Return to Eria with the sword' extend a story thread the trimmed live chain drops. Shares story NPC 213,1008 (live 1305 giver). |
| 1307 | 7 | Live by the Sword | AWKWARD-DUPLICATE | Cut story subplot (Kirash / 'Clue to Orcan Plans'). Beats 'What are we not seeing?' / 'Kill a dark marauder and look for clues' reintroduce the Orcan-plot investigation absent from live. Shares story NPC 213,1008. |
| 1308 | 7 | Essence of Foreboding | AWKWARD-DUPLICATE | Cut story subplot: 'Obtain core essences from the ponderous sporewalkers' / 'Spirits are only a symptom of a larger problem here'. Retells the sporewalker clue that live 1305 already resolves (13,300932/sporewalker beat), and feeds Eria plot. |
| 1310 | 7 | A Clue in the Dark | AWKWARD-DUPLICATE | Identical displayed title to live story quest 1305 'A Clue in the Dark' -> duplicate quest name in the log. Different content (Jehan expedition report to Adria) but same title collides; also references Councilor Teil like 1305. Reward duplication too (see reward screen). |
| 1343 | 9 | Answers Lead to More Questions | AWKWARD-DUPLICATE | Pivotal reveal quest: 'It's nearly time for you to know the truth', Kugai's Codex, 'Karascha will pay!', Leander's Translation, Sersine. Names the antagonist (Karascha) and delivers a lore reveal the compressed live arc (1313->1350->1315->1316) never tells. Enabling it as an ungated side quest spoils/contradicts story pacing. Shares story NPCs 213,1025 (Sersine) and 213,1008. |
| 1312 | 8 | The Dark Patrol | OVERLAP-BENIGN | Gorge patrol: mob 13,300910 (cromos) shared with live 1313 'Into the Gorge'; directs to Sersine at Tainted Gorge Outpost (213,1025, live 1313/1315/1316/1350 receiver). Benign side-hunt framing. GATE behind 1313 so the player is not sent to the gorge before the story takes them. |
| 1318 | 2 | Hunting the Beasts | OVERLAP-BENIGN | Shares training mob 13,300921 with the 9 class-training quests (1371-1379) and deliver NPC 213,1004 with live 1303. Generic beast cull, different framing. |
| 1321 | 1 | A Bridge Pretty Near | OVERLAP-BENIGN | Visits 213,1003 (live 1304 giver). Simple bridge-visit errand, different framing. |
| 1322 | 1 | Unrest in the Forest | OVERLAP-BENIGN | Mob 13,300931 and NPC 213,1003 shared with live 1304 'Making the Rounds'. Side cull, different framing. |
| 1323 | 1 | Getting Some Answers | OVERLAP-BENIGN | Mob 13,300931 shared with live 1304; deliver 213,1017 shared with training quests. Side cull. (Reward starter weapon = expected v17 duplication.) |
| 1324 | 2 | Essence and Sensibility | OVERLAP-BENIGN | Deliver NPC 213,1017 shared with live 1304 and training quests. Distinct mobs (13,300930/300933). Side essence-fetch. |
| 1326 | 5 | Mana out of Mudmen | OVERLAP-BENIGN | Mob 13,2 shared with live 1305. Side hunt for mudmen mana. Different framing. (Reward flagged - see reward screen.) |
| 1327 | 4 | Garrison in Distress | OVERLAP-BENIGN | Mob 13,300921 shared with training quests; visit 213,1004 shared with live 1303. Garrison-rescue errand, different framing. |
| 1328 | 4 | Academic Theft | OVERLAP-BENIGN | Mobs 13,301191/301193/301194 shared with live 1331 'Climbing through the Ranks'. Side theft-recovery, different framing. |
| 1330 | 5 | Horned Horrors | OVERLAP-BENIGN | Mob 13,300932 AND NPC 64,1028 (Taras) both shared with live 1305 'A Clue in the Dark' (which also kills horned ghilliedhus west of Tower Base and talks to Taras). Strong objective overlap but framed as a rookie side-cull. GATE/verify it does not fire alongside 1305. (Reward flagged - see reward screen.) |
| 1332 | 6 | They'll Eat Anything | OVERLAP-BENIGN | Leander's Outpost errand (recover power gauges, deliver to Jehan). No live mob/collect overlap; world-flavor side quest. |
| 1333 | 6 | Twice the Bark, Twice the Bite | OVERLAP-BENIGN | Leander's Outpost errand (cromos power gauges to Jehan). Mob 13,300911 not in live. World-flavor side quest. |
| 1334 | 6 | Investigating the Relics <Repeatable> | OVERLAP-BENIGN | Repeatable relic-fragment collection (col 410) delivered to Eria. Distinct collection id from live; repeatable filler. |
| 1335 | 8 | One of Our Couriers Is Missing | OVERLAP-BENIGN | Visit 213,1007 shared with live 1311 'Redeployment'. Courier-search errand, different framing. |
| 1336 | 7 | Chione's Missing Cargo | OVERLAP-BENIGN | Collection 409 AND receiver 213,1007 both shared with live 1311 (which collects col 409). Same collect objective, different framing (Chione's cargo). Acceptable per doctrine but note the shared collect. |
| 1337 | 7 | The Last One | OVERLAP-BENIGN | Mob 13,901 shared with live 1311; receiver 213,1007. Side hunt, different framing. |
| 1338 | 7 | Chione's Report | OVERLAP-BENIGN | Visits 213,1134 (Acharak questgiver from live 1309). Report errand, different framing. |
| 1339 | 8 | Sersine, She Seeks Shackles | OVERLAP-BENIGN | Gorge mobs 13,300942/13,6 shared with live 1350 'Strange Attractors'; receiver Sersine 213,1025. Side hunt (shackles). GATE behind reaching Sersine (post-1313). |
| 1340 | 8 | Painful Disc-overies | OVERLAP-BENIGN | Gorge disc reapers; mob 13,7 shared with live 1350. Side hunt. GATE behind gorge access. |
| 1341 | 8 | Bequest of the Dead <Repeatable> | OVERLAP-BENIGN | Repeatable collection 411 shared with live 1313 (which collects col 411). Same collect, repeatable filler. Acceptable; note shared collect. |
| 1344 | 9 | Destroy All Destroyers | OVERLAP-BENIGN | Mob 13,9 (destroyers) shared with live 1316 'Dark Revelations' climax; visits 213,1028. Framed as open-ended 'kill as many as you can' side hunt. GATE behind 1316 so it does not pre-empt the climax mob. |
| 1345 | 8 | Desperately Seeking Sorcha | OVERLAP-BENIGN | Visit 64,1007 shared with live 1382. Find-Sorcha errand, different framing. |
| 1346 | 8 | Sorcha's Reckless Challenge | OVERLAP-BENIGN | Escort/guard into dungeon 9037; NPC 64,1006 shared with live 1331. Distinct escort content. |
| 1347 | 6 | It Was a Rock...Crawler | OVERLAP-BENIGN | Deliver 213,1128 not a live NPC, but rock-crawler mobs 13,300541/300542 are island fauna; no live quest uses them. (Borderline CLEAN; kept benign.) |
| 1348 | 5 | Ferocious Flowering Felons | OVERLAP-BENIGN | Deliver NPC 213,1147 shared with live 1305. Side cull (flowering felons), different framing. |
| 1351 | 4 | Supply and Demand | OVERLAP-BENIGN | Visit NPCs 64,1005/64,1007/64,1048 shared with live 1382/1383/1384 garrison cluster. Errand chain, different framing. (Duplicate-title with 1352.) |
| 1352 | 4 | Supply and Demand | OVERLAP-BENIGN | Visit NPCs 64,1005/64,1008/64,1048 shared with live 1382/1383/1384 garrison cluster. Class-split twin of 1351, same title. Errand, different framing. |
| 1385 | 3 | Always After Me Lucky Charms | OVERLAP-BENIGN | Visit 64,1049 shared with live 1384. Lucky-charm errand, different framing. |
| 1386 | 4 | Bombs Away | OVERLAP-BENIGN | Mob 13,888 AND NPC 64,1029 both shared with live 1329 'Going Above and Beyond'; NPC 64,1006 shared with 1331. Bomb side-mission, different framing. |
| 1302 | 1 | Another Fine Mess | CLEAN | Immediate tutorial follow-up to live 1301; visits 213,1106 (not a live objective). No shared mob/collect/story beat. |
| 1319 | 2 | Dwellers of the Island | CLEAN | Mobs 13,300941/300944 not used by any live quest. (Reward is a starter weapon also granted by 1303/1304 - expected v17 duplication, not a conflict.) |
| 1325 | 3 | The Perfect Cut | CLEAN | Mob 13,1 not used by any live quest; giver/deliver 213,1121 not a live NPC. |
| 1349 | 7 | Gotta Kill 'Em All | CLEAN | Mobs 13,4/13,5 not used by any live quest; giver 213,1126 not a live NPC. Pure side cull. |
| 1389 | 5 | Emptying Pandora's Box | CLEAN | Pandora's Box tutorial (giver 213,1020, 'Elleon's Outpost' is only a place name). No mob/collect/story overlap. NOTE: teaches a Pandora's Box consumable ('double your items') - content-fit / economy question for the framework, not an overlap issue. |
| 1390 | 6 | Special Delivery | CLEAN | Courier delivery via 64,1050; no live mob/collect/story-NPC overlap. |

### AWKWARD-DUPLICATE detail

- **1306 Traces of Darkness** (lvl 6): Cut story subplot 'A Blade to Remember' (Leander/Eria investigation). Journal beats 'What does this all mean?' / 'Take gauges to Eria' / 'Return to Eria with the sword' extend a story thread the trimmed live chain drops. Shares story NPC 213,1008 (live 1305 giver).
- **1307 Live by the Sword** (lvl 7): Cut story subplot (Kirash / 'Clue to Orcan Plans'). Beats 'What are we not seeing?' / 'Kill a dark marauder and look for clues' reintroduce the Orcan-plot investigation absent from live. Shares story NPC 213,1008.
- **1308 Essence of Foreboding** (lvl 7): Cut story subplot: 'Obtain core essences from the ponderous sporewalkers' / 'Spirits are only a symptom of a larger problem here'. Retells the sporewalker clue that live 1305 already resolves (13,300932/sporewalker beat), and feeds Eria plot.
- **1310 A Clue in the Dark** (lvl 7): Identical displayed title to live story quest 1305 'A Clue in the Dark' -> duplicate quest name in the log. Different content (Jehan expedition report to Adria) but same title collides; also references Councilor Teil like 1305. Reward duplication too (see reward screen).
- **1343 Answers Lead to More Questions** (lvl 9): Pivotal reveal quest: 'It's nearly time for you to know the truth', Kugai's Codex, 'Karascha will pay!', Leander's Translation, Sersine. Names the antagonist (Karascha) and delivers a lore reveal the compressed live arc (1313->1350->1315->1316) never tells. Enabling it as an ungated side quest spoils/contradicts story pacing. Shares story NPCs 213,1025 (Sersine) and 213,1008.

## Reward-conflict screen

Live reward sheet = v92 QuestCompensationData_13 (includes the reworked/new-class rows). Flag = conflict created by the v31->v92 evolution or the live rework, NOT plain v17 duplication (which is expected). No candidate references a reward item id absent from v92.

| gid | lvl | title | verdict | reason |
|---|---|---|---|---|
| 1310 | 7 | A Clue in the Dark | REWARD-FLAG | Gives body ilvl7 (17413/mail17 etc.) + weapon ilvl7 - duplicates pieces of the reworked live 1305 full ilvl7 set (body/feet/hand/weapon) handed at quest-level 5. A level-7 player already owns the set from same-named live 1305. |
| 1326 | 5 | Mana out of Mudmen | REWARD-FLAG | Gives feet ilvl7 (15021/15024/15027) - duplicate of the feet piece in live 1305's reworked full ilvl7 set (both around character level 5). |
| 1330 | 5 | Horned Horrors | REWARD-FLAG | Gives hand ilvl7 (15020/15023/15026) - duplicate of the hand piece in live 1305's reworked full ilvl7 set (both around character level 5). |
| 1302 | 1 | Another Fine Mess | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1306 | 6 | Traces of Darkness | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1307 | 7 | Live by the Sword | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1308 | 7 | Essence of Foreboding | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1312 | 8 | The Dark Patrol | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1318 | 2 | Hunting the Beasts | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1319 | 2 | Dwellers of the Island | REWARD-CLEAN | Gear reward is a starter piece matching v17 pacing (expected duplication) or an isolated slot/level with no live conflict. |
| 1321 | 1 | A Bridge Pretty Near | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1322 | 1 | Unrest in the Forest | REWARD-CLEAN | Gear reward is a starter piece matching v17 pacing (expected duplication) or an isolated slot/level with no live conflict. |
| 1323 | 1 | Getting Some Answers | REWARD-CLEAN | Gear reward is a starter piece matching v17 pacing (expected duplication) or an isolated slot/level with no live conflict. |
| 1324 | 2 | Essence and Sensibility | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1325 | 3 | The Perfect Cut | REWARD-CLEAN | Gear reward is a starter piece matching v17 pacing (expected duplication) or an isolated slot/level with no live conflict. |
| 1327 | 4 | Garrison in Distress | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1328 | 4 | Academic Theft | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1332 | 6 | They'll Eat Anything | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1333 | 6 | Twice the Bark, Twice the Bite | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1334 | 6 | Investigating the Relics <Repeatable> | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1335 | 8 | One of Our Couriers Is Missing | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1336 | 7 | Chione's Missing Cargo | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1337 | 7 | The Last One | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1338 | 7 | Chione's Report | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1339 | 8 | Sersine, She Seeks Shackles | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1340 | 8 | Painful Disc-overies | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1341 | 8 | Bequest of the Dead <Repeatable> | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1343 | 9 | Answers Lead to More Questions | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1344 | 9 | Destroy All Destroyers | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1345 | 8 | Desperately Seeking Sorcha | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1346 | 8 | Sorcha's Reckless Challenge | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1347 | 6 | It Was a Rock...Crawler | REWARD-CLEAN | Gear reward is a starter piece matching v17 pacing (expected duplication) or an isolated slot/level with no live conflict. |
| 1348 | 5 | Ferocious Flowering Felons | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1349 | 7 | Gotta Kill 'Em All | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1351 | 4 | Supply and Demand | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1352 | 4 | Supply and Demand | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1385 | 3 | Always After Me Lucky Charms | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1386 | 4 | Bombs Away | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1389 | 5 | Emptying Pandora's Box | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |
| 1390 | 6 | Special Delivery | REWARD-CLEAN | Exp/gold/consumable only; no gear conflict. |

### Live gear-bearing quests (reward sheet reference)

| gid | Qlvl | title | gear pieces (slot, itemLevel, rareGrade) |
|---|---|---|---|
| 1303 | 3 | The Secret Life of Trees | [['body', 4, 0], ['weapon', 2, 0], ['weapon', 3, 0], ['weapon', 4, 0]] |
| 1304 | 1 | Making the Rounds | [['weapon', 2, 0]] |
| 1305 | 5 | A Clue in the Dark | [['body', 7, 0], ['feet', 7, 0], ['hand', 7, 0], ['weapon', 7, 0]] |
| 1315 | 9 | Putting the Pieces Together | [['body', 8, 0], ['weapon', 7, 0], ['weapon', 8, 0]] |
| 1316 | 9 | Dark Revelations | [['weapon', 11, 1], ['weapon', 12, 0]] |
| 1317 | 10 | Ride Off into the Sunset | [['body', 11, 0]] |
| 1331 | 5 | Climbing through the Ranks | [['body', 5, 0]] |

### Expected-duplication notes (not flagged)

- 1319, 1323: hand a starter weapon that live 1303/1304 also grant at the same level band. This is the original v17 pacing (multiple level-1 to level-3 sources for the starter weapon) and is expected, not a conflict.
- 1322 (feet ilvl3), 1325 (hand ilvl3), 1347 (hand ilvl6): isolated single gear pieces with no live quest granting the same slot at that level band; no duplicate or obsolete conflict.
- 1389 Pandora's Box: economy/content-fit question (teaches a double-loot consumable) for the framework, independent of the reward-conflict screen.