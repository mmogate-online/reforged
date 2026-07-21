# v31 Quest Server Data - Island of Dawn (Phase 2a)

Extracted from v31.04 server datasheets and diffed against the v17 client catalog (`v17-quests.json`, the north star). v31 is the server encoding; flags mark where v31 evolved past v17.

## Summary

- Catalog quests: **63**  |  present in v31: **63**
- **v31 has 40 of the 63 quests DISABLED** via the 99,99 prerequisite sentinel. v31 is the reworked "ATW_Death_P" Island of Dawn where the old content loop was soft-disabled; v17.11 (pre-rework) is where these quests are live, which is why v17 is the north star for this restoration.
- v31 13xx-band quests NOT in the v17 catalog (v31 additions): **[1379, 1383]**

Diff-flag counts across the 63 quests:

| Flag | Count |
| --- | --- |
| SENTINEL_DISABLED | 40 |
| TASKSEQ_DRIFT | 27 |
| RECEIVER_DRIFT | 20 |
| TASKCOUNT_DRIFT | 20 |
| PREREQ_DRIFT | 18 |
| STORYGROUP_DRIFT | 18 |
| TYPE_DRIFT | 17 |
| MINLEVEL_DRIFT | 13 |
| GIVER_DRIFT | 11 |
| ALIGNED | 1 |
| ACCEPT_DRIFT | 1 |

Flags: `ALIGNED` no header/structure divergence; `ACCEPT_DRIFT` accept mechanism differs (auto vs npc); `GIVER_DRIFT`/`RECEIVER_DRIFT` giver or turn-in NPC differs; `PREREQ_DRIFT` prerequisite chain differs; `TASKCOUNT_DRIFT`/`TASKSEQ_DRIFT` task structure differs; `MINLEVEL_DRIFT`/`STORYGROUP_DRIFT`/`TYPE_DRIFT`/`REPEAT_DRIFT` header field differs; `SENTINEL_DISABLED` v31 header carries the 99,99 disable sentinel.

## Per-quest alignment

| gid | title | accept | tasks | prereq (v17->v31) | disabled | flags |
| --- | --- | --- | --- | --- | --- | --- |
| 1301 | Dawn's Early Light | npc | 1 | - | - | - |
| 1302 | Another Fine Mess | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1303 | The Secret Life of Trees | npc | 3->5 | -->[1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379] | - | RECEIVER_DRIFT, PREREQ_DRIFT, MINLEVEL_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1304 | Making the Rounds | npc | 4->2 | [1301] | - | RECEIVER_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1305 | Elleon's Fate | auto->npc | 4->7 | [1304]->[1331] | - | ACCEPT_DRIFT, GIVER_DRIFT, RECEIVER_DRIFT, PREREQ_DRIFT, MINLEVEL_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1306 | Traces of Darkness | npc | 6 | [9999] | yes | SENTINEL_DISABLED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1307 | Live by the Sword... | npc | 3 | [9999] | yes | SENTINEL_DISABLED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1308 | Essence of Foreboding | npc | 2 | [9999] | yes | SENTINEL_DISABLED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1309 | Acharak Attacks | npc | 2 | [1307]->[1311] | - | GIVER_DRIFT, RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT |
| 1310 | A Clue In the Dark | npc | 3 | [9999] | yes | SENTINEL_DISABLED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1311 | Clearing the Gorge | auto | 4->3 | [1310]->[1305] | - | RECEIVER_DRIFT, PREREQ_DRIFT, MINLEVEL_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1312 | The Dark Patrol | npc | 2 | [9999] | yes | SENTINEL_DISABLED, RECEIVER_DRIFT |
| 1313 | Into the Gorge | npc | 3->5 | [1311]->[1309] | - | GIVER_DRIFT, PREREQ_DRIFT, MINLEVEL_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1315 | Putting the Pieces Together | npc | 4->2 | [1350] | - | GIVER_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1316 | Dark Revelations | npc | 5->8 | [1343]->[1315] | - | PREREQ_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1317 | Ride Off Into the Sunset | npc | 5->4 | [1316] | - | TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1318 | Hunting the Beasts | npc | 1 | [9999] | yes | SENTINEL_DISABLED, GIVER_DRIFT, RECEIVER_DRIFT, MINLEVEL_DRIFT |
| 1319 | Dwellers of the Island | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1321 | A Bridge Pretty Near | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1322 | Unrest in the Forest | npc | 2 | [9999] | yes | SENTINEL_DISABLED |
| 1323 | Getting Some Answers | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1324 | Essence and Sensibility | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1325 | The Perfect Cut | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1326 | Mana out of Mudmen | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1327 | Garrison in Distress | npc | 3 | [9999] | yes | SENTINEL_DISABLED |
| 1328 | Academic Theft | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1329 | Going Above and Beyond | npc | 1->3 | [1304]->[1303] | - | GIVER_DRIFT, RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1330 | Horned Horrors | npc | 2 | [9999] | yes | SENTINEL_DISABLED, MINLEVEL_DRIFT |
| 1331 | I'll Take the High Road | npc | 2->5 | [1386]->[1382, 1383] | - | GIVER_DRIFT, RECEIVER_DRIFT, PREREQ_DRIFT, MINLEVEL_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1332 | They'll Eat Anything | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1333 | Twice the Bark, Twice the Bite | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1334 | Investigating the Relics <Repeatable> | npc | 1 | [9999] | yes | SENTINEL_DISABLED, TASKSEQ_DRIFT |
| 1335 | One of Our Couriers is Missing | npc | 2 | [9999] | yes | SENTINEL_DISABLED |
| 1336 | Chione's Missing Cargo | npc | 1 | [9999] | yes | SENTINEL_DISABLED, MINLEVEL_DRIFT, TASKSEQ_DRIFT |
| 1337 | Searching for the Stolen Stones | npc | 1 | [9999] | yes | SENTINEL_DISABLED, MINLEVEL_DRIFT |
| 1338 | Chione's Report | npc | 1 | [9999] | yes | SENTINEL_DISABLED, RECEIVER_DRIFT, MINLEVEL_DRIFT |
| 1339 | Sersine, She Seeks Shackles | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1340 | Painful Disc-overies | npc | 2 | [9999] | yes | SENTINEL_DISABLED |
| 1341 | Bequest of the Dead <Repeatable> | npc | 1 | [9999] | yes | SENTINEL_DISABLED, TASKSEQ_DRIFT |
| 1343 | Answers Lead to More Questions | npc | 3 | [9999] | yes | SENTINEL_DISABLED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1344 | Destroy All Destroyers! | npc | 4 | [9999] | yes | SENTINEL_DISABLED |
| 1345 | Desperately Seeking Sorscha | npc | 2 | [9999] | yes | SENTINEL_DISABLED |
| 1346 | Sorcha's Reckless Challenge | npc | 3 | [9999] | yes | SENTINEL_DISABLED, TASKSEQ_DRIFT |
| 1347 | It Was a Rock...Crawler! | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1348 | Ferocious Flowering Felons | npc | 1 | [9999] | yes | SENTINEL_DISABLED |
| 1349 | Gotta Kill 'em All | npc | 2 | [9999] | yes | SENTINEL_DISABLED |
| 1350 | Strange Attractors | npc | 1 | [1313] | - | GIVER_DRIFT, RECEIVER_DRIFT, MINLEVEL_DRIFT |
| 1351 | Supply and Demand | npc | 3 | [9999] | yes | SENTINEL_DISABLED |
| 1352 | Supply and Demand | npc | 3 | [9999] | yes | SENTINEL_DISABLED |
| 1371 | Initial Warrior Training | npc | 3->5 | -->[1304] | - | RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1372 | Initial Lancer Training | npc | 3->5 | -->[1304] | - | RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1373 | Initial Slayer Training | npc | 3->5 | -->[1304] | - | RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1374 | Initial Berserker Training | npc | 3->5 | -->[1304] | - | RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1375 | Initial Archer Training | npc | 3->5 | -->[1304] | - | RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1376 | Initial Sorcerer Training | npc | 3->5 | -->[1304] | - | RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1377 | Initial Priest Training | npc | 3->5 | -->[1304] | - | RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1378 | Initial Mystic Training | npc | 3->5 | -->[1304] | - | RECEIVER_DRIFT, PREREQ_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1382 | Introduction to Gathering | npc | 1->3 | -->[1384] | - | GIVER_DRIFT, PREREQ_DRIFT, MINLEVEL_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1384 | Recharge It | npc | 2->6 | -->[1329] | - | GIVER_DRIFT, PREREQ_DRIFT, MINLEVEL_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT, TASKCOUNT_DRIFT, TASKSEQ_DRIFT |
| 1385 | Always After Me Lucky Charms | npc | 2 | [9999] | yes | SENTINEL_DISABLED, TASKSEQ_DRIFT |
| 1386 | Bombs Away! | npc | 4 | [9999] | yes | SENTINEL_DISABLED |
| 1389 | 판도라 상자 사용 안내 | npc | 3 | [9999] | yes | SENTINEL_DISABLED, TASKSEQ_DRIFT |
| 1390 | Special Delivery | npc | 3 | [9999] | yes | SENTINEL_DISABLED, GIVER_DRIFT, RECEIVER_DRIFT, TASKSEQ_DRIFT |

## Divergences worth a precedence call (what taking v17 loses)

### 1302 - Another Fine Mess
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=1, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1302003

### 1303 - The Secret Life of Trees
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379]
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1303003

### 1305 - Elleon's Fate
- v31 has 7 tasks vs v17 4 (v17 drops 3 step(s))
- accept: v17=auto vs v31=npc (v31 giver 64,1001)
- prereq chain: v17=[1304] vs v31=[1331]
- v31 server-only header fields: rec_party_size=1, rec_level=6, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1305002

### 1306 - Traces of Darkness
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1306003

### 1307 - Live by the Sword...
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1307003

### 1308 - Essence of Foreboding
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1308003

### 1309 - Acharak Attacks
- prereq chain: v17=[1307] vs v31=[1311]
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1309003

### 1310 - A Clue In the Dark
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2

### 1311 - Clearing the Gorge
- prereq chain: v17=[1310] vs v31=[1305]
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2

### 1312 - The Dark Patrol
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1312003

### 1313 - Into the Gorge
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=[1311] vs v31=[1309]
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=불가능, summary_info=100, linked_quest=13,39, start_task=1, quest_dialog_count=2, end_popup=@quest:1313003

### 1316 - Dark Revelations
- v31 has 8 tasks vs v17 5 (v17 drops 3 step(s))
- prereq chain: v17=[1343] vs v31=[1315]
- v31 server-only header fields: rec_party_size=1, rec_level=9, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1316003

### 1318 - Hunting the Beasts
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1318003

### 1319 - Dwellers of the Island
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=3, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1319003

### 1321 - A Bridge Pretty Near
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=1, cancelable=가능, summary_info=100, linked_quest=13,22, start_task=1, quest_dialog_count=2, end_popup=@quest:1321003

### 1322 - Unrest in the Forest
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=1, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1322003

### 1323 - Getting Some Answers
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=1, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1323003

### 1324 - Essence and Sensibility
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=3, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1324003

### 1325 - The Perfect Cut
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=3, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1325003

### 1326 - Mana out of Mudmen
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=5, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1326003

### 1327 - Garrison in Distress
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1327003

### 1328 - Academic Theft
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1328003

### 1329 - Going Above and Beyond
- v31 has 3 tasks vs v17 1 (v17 drops 2 step(s))
- prereq chain: v17=[1304] vs v31=[1303]
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2

### 1330 - Horned Horrors
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=5, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1330003

### 1331 - I'll Take the High Road
- v31 has 5 tasks vs v17 2 (v17 drops 3 step(s))
- prereq chain: v17=[1386] vs v31=[1382, 1383]
- v31 server-only header fields: rec_party_size=1, rec_level=5, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1331003

### 1332 - They'll Eat Anything
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1332003

### 1333 - Twice the Bark, Twice the Bite
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1333003

### 1334 - Investigating the Relics <Repeatable>
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1334003

### 1335 - One of Our Couriers is Missing
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1335003

### 1336 - Chione's Missing Cargo
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1336003

### 1337 - Searching for the Stolen Stones
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1337003

### 1338 - Chione's Report
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1338003

### 1339 - Sersine, She Seeks Shackles
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1339003

### 1340 - Painful Disc-overies
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1340003

### 1341 - Bequest of the Dead <Repeatable>
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1341003

### 1343 - Answers Lead to More Questions
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=11, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1343003

### 1344 - Destroy All Destroyers!
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=9, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1344003

### 1345 - Desperately Seeking Sorscha
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=10, cancelable=가능, summary_info=100, linked_quest=13,46, start_task=1, quest_dialog_count=2, end_popup=@quest:1345003

### 1346 - Sorcha's Reckless Challenge
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=10, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1346003

### 1347 - It Was a Rock...Crawler!
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=6, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1347003

### 1348 - Ferocious Flowering Felons
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1348003

### 1349 - Gotta Kill 'em All
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=8, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1349003

### 1351 - Supply and Demand
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1351003

### 1352 - Supply and Demand
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1352003

### 1371 - Initial Warrior Training
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1304]
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1371003

### 1372 - Initial Lancer Training
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1304]
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1372003

### 1373 - Initial Slayer Training
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1304]
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1373003

### 1374 - Initial Berserker Training
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1304]
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1374003

### 1375 - Initial Archer Training
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1304]
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1375003

### 1376 - Initial Sorcerer Training
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1304]
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1376003

### 1377 - Initial Priest Training
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1304]
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1377003

### 1378 - Initial Mystic Training
- v31 has 5 tasks vs v17 3 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1304]
- v31 server-only header fields: rec_party_size=1, rec_level=2, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1378003

### 1382 - Introduction to Gathering
- v31 has 3 tasks vs v17 1 (v17 drops 2 step(s))
- prereq chain: v17=none vs v31=[1384]
- v31 server-only header fields: rec_party_size=1, rec_level=5, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2

### 1384 - Recharge It
- v31 has 6 tasks vs v17 2 (v17 drops 4 step(s))
- prereq chain: v17=none vs v31=[1329]
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2

### 1385 - Always After Me Lucky Charms
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=3, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1385003

### 1386 - Bombs Away!
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=4, cancelable=가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1386003

### 1389 - 판도라 상자 사용 안내
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=6, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1389003

### 1390 - Special Delivery
- v31 has this quest DISABLED (99,99 sentinel); v17 is where it is live
- v31 server-only header fields: rec_party_size=1, rec_level=7, cancelable=불가능, summary_info=100, linked_quest=1,1, start_task=1, quest_dialog_count=2, end_popup=@quest:1390003

## Dialogs (v31 QuestDialog vs v17 client, structural)

| Flag | Count |
| --- | --- |
| DIALOG_ALIGNED | 38 |
| DIALOG_STRUCT_DRIFT | 25 |

Text-block counts shown client/v31.

| gid | file | v31 | client | text client/v31 | flags |
| --- | --- | --- | --- | --- | --- |
| 1301 | QuestDialog_13_1 | yes | yes | 4/4 | aligned |
| 1302 | QuestDialog_13_2 | yes | yes | 4/4 | aligned |
| 1303 | QuestDialog_13_3 | yes | yes | 4/6 | DIALOG_STRUCT_DRIFT |
| 1304 | QuestDialog_13_4 | yes | yes | 7/6 | DIALOG_STRUCT_DRIFT |
| 1305 | QuestDialog_13_5 | yes | yes | 7/8 | DIALOG_STRUCT_DRIFT |
| 1306 | QuestDialog_13_6 | yes | yes | 7/7 | aligned |
| 1307 | QuestDialog_13_7 | yes | yes | 7/7 | aligned |
| 1308 | QuestDialog_13_8 | yes | yes | 6/6 | aligned |
| 1309 | QuestDialog_13_9 | yes | yes | 4/4 | DIALOG_STRUCT_DRIFT |
| 1310 | QuestDialog_13_10 | yes | yes | 6/6 | aligned |
| 1311 | QuestDialog_13_11 | yes | yes | 7/6 | DIALOG_STRUCT_DRIFT |
| 1312 | QuestDialog_13_12 | yes | yes | 4/4 | DIALOG_STRUCT_DRIFT |
| 1313 | QuestDialog_13_13 | yes | yes | 5/6 | DIALOG_STRUCT_DRIFT |
| 1315 | QuestDialog_13_15 | yes | yes | 7/4 | DIALOG_STRUCT_DRIFT |
| 1316 | QuestDialog_13_16 | yes | yes | 6/6 | aligned |
| 1317 | QuestDialog_13_17 | yes | yes | 8/7 | DIALOG_STRUCT_DRIFT |
| 1318 | QuestDialog_13_18 | yes | yes | 5/5 | DIALOG_STRUCT_DRIFT |
| 1319 | QuestDialog_13_19 | yes | yes | 5/5 | aligned |
| 1321 | QuestDialog_13_21 | yes | yes | 4/4 | aligned |
| 1322 | QuestDialog_13_22 | yes | yes | 4/4 | aligned |
| 1323 | QuestDialog_13_23 | yes | yes | 5/5 | aligned |
| 1324 | QuestDialog_13_24 | yes | yes | 5/5 | aligned |
| 1325 | QuestDialog_13_25 | yes | yes | 5/5 | aligned |
| 1326 | QuestDialog_13_26 | yes | yes | 5/5 | aligned |
| 1327 | QuestDialog_13_27 | yes | yes | 7/7 | aligned |
| 1328 | QuestDialog_13_28 | yes | yes | 5/5 | aligned |
| 1329 | QuestDialog_13_29 | yes | yes | 4/5 | DIALOG_STRUCT_DRIFT |
| 1330 | QuestDialog_13_30 | yes | yes | 4/4 | aligned |
| 1331 | QuestDialog_13_31 | yes | yes | 6/7 | DIALOG_STRUCT_DRIFT |
| 1332 | QuestDialog_13_32 | yes | yes | 5/5 | aligned |
| 1333 | QuestDialog_13_33 | yes | yes | 5/5 | aligned |
| 1334 | QuestDialog_13_34 | yes | yes | 5/5 | aligned |
| 1335 | QuestDialog_13_35 | yes | yes | 5/5 | aligned |
| 1336 | QuestDialog_13_36 | yes | yes | 5/5 | aligned |
| 1337 | QuestDialog_13_37 | yes | yes | 5/5 | aligned |
| 1338 | QuestDialog_13_38 | yes | yes | 4/4 | DIALOG_STRUCT_DRIFT |
| 1339 | QuestDialog_13_39 | yes | yes | 5/5 | aligned |
| 1340 | QuestDialog_13_40 | yes | yes | 4/4 | aligned |
| 1341 | QuestDialog_13_41 | yes | yes | 5/5 | aligned |
| 1343 | QuestDialog_13_43 | yes | yes | 6/6 | aligned |
| 1344 | QuestDialog_13_44 | yes | yes | 6/6 | aligned |
| 1345 | QuestDialog_13_45 | yes | yes | 5/5 | aligned |
| 1346 | QuestDialog_13_46 | yes | yes | 5/5 | aligned |
| 1347 | QuestDialog_13_47 | yes | yes | 5/5 | aligned |
| 1348 | QuestDialog_13_48 | yes | yes | 5/5 | aligned |
| 1349 | QuestDialog_13_49 | yes | yes | 4/4 | aligned |
| 1350 | QuestDialog_13_50 | yes | yes | 5/5 | DIALOG_STRUCT_DRIFT |
| 1351 | QuestDialog_13_51 | yes | yes | 6/6 | aligned |
| 1352 | QuestDialog_13_52 | yes | yes | 6/6 | aligned |
| 1371 | QuestDialog_13_71 | yes | yes | 5/8 | DIALOG_STRUCT_DRIFT |
| 1372 | QuestDialog_13_72 | yes | yes | 5/8 | DIALOG_STRUCT_DRIFT |
| 1373 | QuestDialog_13_73 | yes | yes | 5/8 | DIALOG_STRUCT_DRIFT |
| 1374 | QuestDialog_13_74 | yes | yes | 5/8 | DIALOG_STRUCT_DRIFT |
| 1375 | QuestDialog_13_75 | yes | yes | 5/8 | DIALOG_STRUCT_DRIFT |
| 1376 | QuestDialog_13_76 | yes | yes | 5/8 | DIALOG_STRUCT_DRIFT |
| 1377 | QuestDialog_13_77 | yes | yes | 5/8 | DIALOG_STRUCT_DRIFT |
| 1378 | QuestDialog_13_78 | yes | yes | 5/8 | DIALOG_STRUCT_DRIFT |
| 1382 | QuestDialog_13_82 | yes | yes | 5/7 | DIALOG_STRUCT_DRIFT |
| 1384 | QuestDialog_13_84 | yes | yes | 4/7 | DIALOG_STRUCT_DRIFT |
| 1385 | QuestDialog_13_85 | yes | yes | 4/4 | aligned |
| 1386 | QuestDialog_13_86 | yes | yes | 6/6 | aligned |
| 1389 | QuestDialog_13_89 | yes | yes | 5/5 | aligned |
| 1390 | QuestDialog_13_90 | yes | yes | 5/5 | DIALOG_STRUCT_DRIFT |

## CollectionTerritory verdict (Task 4)

**The v92 server loads `CollectionTerritory_13_ATW_Death_P.xml`. `CollectionTerritory_13_ATW_P.xml` is an inert legacy leftover (byte-identical to v31) that no live area references.**

Evidence:

- v92 `CollectionData/` carries **both** files: `ATW_Death_P` (present) and `ATW_P` (present).
- v31 `CollectionData/` carries **only** the legacy `ATW_P` (present); no `ATW_Death_P` exists there.
- The zone-13 area in v92 is `AreaData_13_ATW_Death_P.xml`, whose `<Area>` `areaName="ATW_Death_P"`. There is **no** `AreaData_13_ATW_P` in v92 (absent), so the `ATW_P` area name no longer exists.
- Each `CollectionTerritory` file tags its own `areaName`: `ATW_Death_P` file -> `ATW_Death_P`, `ATW_P` file -> `ATW_P`. The loader binds a CollectionTerritory to the Area of the same `continentId` + `areaName`; only `ATW_Death_P` matches a live Area.
- Spawn geometry is the same in both: `ATW_Death_P` 8 groups / 237 spawns, `ATW_P` 8 groups / 237 spawns (identical positions). The `ATW_Death_P` file is a reformatted re-author (2-space indent, updated Korean territory descriptions); content-equivalent spawns, so nothing is lost by the legacy file being dead.
- v92 `ATW_P` is **byte-identical** to v31's `ATW_P`, confirming it is the untouched v31-era artifact rather than a maintained file.

Recommendation: the legacy `CollectionTerritory_13_ATW_P.xml` can be removed from v92 (inert; safe), but it causes no live effect while present.
