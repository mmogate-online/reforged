# Island Quest Audit (Iteration 2)

Generated 2026-07-17 19:49:27 by tools/dc-restore/audit_quests.py

Sources compared per quest: CLIENT (design reference), V31 (easy-restore source), V92 (current truth, read from the working tree). Quest scope is the global-id band 1300-1399 unioned across sources; NPC-spawn checks scan the island TerritoryData for zones 13,64,213,313,364,436. V92 is the working tree, so authored spawns and restored comp/prereq are reflected as-is.

Old-client-vs-v92 numeric drift (kill counts, level bands) is expected from years of rebalancing; the high-signal items are reference-identity drift (collection/item/NPC ids), unspawned givers, empty comp on active quests, and the sentinel-disabled set. Severity reflects that.

## Summary

- Quests in scope: 65
- By severity: blocking 63, drift 1, info 0, clean 1

| Flag | Count |
|------|-------|
| SENTINEL_DISABLED | 37 |
| PREREQ_DRIFT | 18 |
| TASKREF_DRIFT | 48 |
| COMP_EMPTY | 62 |
| COMP_DRIFT | 55 |
| GIVER_UNSPAWNED | 6 |
| TARGET_UNSPAWNED | 10 |
| GROUPLIST_UNREGISTERED | 5 |
| STORYGROUP_DRIFT | 18 |
| LEVELBAND_DRIFT | 13 |
| TYPE_DRIFT | 17 |
| CLEAN | 1 |

## Reference-identity regressions (v31 + client agree, v92 diverges)

These are the clearest mechanical fixes: a gameplay reference where both the client and the v31 server hold one value and only v92 differs.

| Quest | EN title | task | field | client=v31 | v92 |
|-------|----------|------|-------|-----------|-----|
| 1336 | Chione's Missing Cargo | 1 | collections | ['409'] | ['403'] |

## Worklist

### Group A: Mechanically fixable now (sentinel/comp/taskref, giver spawned) (9)
- 1302 Another Fine Mess: SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT
- 1321 A Bridge Pretty Near: SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT
- 1325 The Perfect Cut: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT
- 1326 Mana out of Mudmen: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT
- 1330 Horned Horrors: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT
- 1336 Chione's Missing Cargo: TASKREF_DRIFT, LEVELBAND_DRIFT
- 1340 Painful Disc-overies: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT
- 1348 Ferocious Flowering Felons: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT
- 1390 Special Delivery: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT

### Group B: Needs spawn authoring (giver or task target not spawned in v92) (10)
- 1306 Traces of Darkness: SENTINEL_DISABLED, COMP_EMPTY, TARGET_UNSPAWNED, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT
- 1307 Live by the Sword...: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, TARGET_UNSPAWNED, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT
- 1310 A Clue In the Dark: SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT, TARGET_UNSPAWNED, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT
- 1319 Dwellers of the Island: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED
- 1332 They'll Eat Anything: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED
- 1333 Twice the Bark, Twice the Bite: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED
- 1346 Sorcha's Reckless Challenge: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, TARGET_UNSPAWNED
- 1347 It Was a Rock...Crawler!: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED
- 1349 Gotta Kill 'em All: SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED
- 1389 판도라 상자 사용 안내: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED

### Group C: Chain-entangled (prereq graph links the story spine) (19)
- 1308 Essence of Foreboding: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT  [pred [1306] / succ [1307]]
- 1312 The Dark Patrol: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT  [pred [1311] / succ -]
- 1318 Hunting the Beasts: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT  [pred [1322] / succ -]
- 1322 Unrest in the Forest: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT  [pred - / succ [1318, 1323]]
- 1323 Getting Some Answers: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT  [pred [1322] / succ [1324]]
- 1324 Essence and Sensibility: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT  [pred [1323] / succ [1327]]
- 1327 Garrison in Distress: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT  [pred [1324] / succ -]
- 1328 Academic Theft: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT  [pred [1386] / succ -]
- 1335 One of Our Couriers is Missing: SENTINEL_DISABLED, COMP_EMPTY  [pred [1310] / succ [1336, 1337]]
- 1337 Searching for the Stolen Stones: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT  [pred [1335] / succ [1338]]
- 1338 Chione's Report: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, LEVELBAND_DRIFT  [pred [1337] / succ -]
- 1339 Sersine, She Seeks Shackles: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT  [pred [1313] / succ -]
- 1343 Answers Lead to More Questions: SENTINEL_DISABLED, COMP_EMPTY, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT  [pred [1315] / succ [1316, 1344]]
- 1344 Destroy All Destroyers!: SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT  [pred [1343] / succ -]
- 1345 Desperately Seeking Sorscha: SENTINEL_DISABLED, COMP_EMPTY  [pred - / succ [1346]]
- 1351 Supply and Demand: SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT  [pred [1329] / succ -]
- 1352 Supply and Demand: SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT  [pred [1329] / succ -]
- 1385 Always After Me Lucky Charms: SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT  [pred [1384] / succ -]
- 1386 Bombs Away!: SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT  [pred [1329] / succ [1328, 1331]]

### Group D: Conflicts needing a human decision (comp/prereq disagreement) (25)
- 1301 Dawn's Early Light: COMP_EMPTY, COMP_DRIFT
- 1303 The Secret Life of Trees: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT
- 1304 Making the Rounds: TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT
- 1305 Elleon's Fate: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT
- 1309 Acharak Attacks: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT
- 1311 Clearing the Gorge: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT
- 1313 Into the Gorge: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT
- 1315 Putting the Pieces Together: TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT
- 1316 Dark Revelations: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT
- 1317 Ride Off Into the Sunset: TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT
- 1329 Going Above and Beyond: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1331 I'll Take the High Road: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, LEVELBAND_DRIFT, TYPE_DRIFT
- 1350 Strange Attractors: TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT
- 1371 Initial Warrior Training: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1372 Initial Lancer Training: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1373 Initial Slayer Training: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1374 Initial Berserker Training: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1375 Initial Archer Training: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1376 Initial Sorcerer Training: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1377 Initial Priest Training: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1378 Initial Mystic Training: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT
- 1379 : COMP_EMPTY, COMP_DRIFT
- 1382 Introduction to Gathering: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, LEVELBAND_DRIFT, TYPE_DRIFT
- 1383 : COMP_EMPTY, COMP_DRIFT
- 1384 Recharge It: PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, LEVELBAND_DRIFT, TYPE_DRIFT

## Per-quest flags

| Quest | EN title | v92 state | severity | flags |
|-------|----------|-----------|----------|-------|
| 1301 | Dawn's Early Light | active | blocking | COMP_EMPTY, COMP_DRIFT |
| 1302 | Another Fine Mess | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT |
| 1303 | The Secret Life of Trees | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT |
| 1304 | Making the Rounds | active | blocking | TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1305 | Elleon's Fate | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT |
| 1306 | Traces of Darkness | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, TARGET_UNSPAWNED, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1307 | Live by the Sword... | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, TARGET_UNSPAWNED, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1308 | Essence of Foreboding | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1309 | Acharak Attacks | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT |
| 1310 | A Clue In the Dark | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT, TARGET_UNSPAWNED, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1311 | Clearing the Gorge | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT |
| 1312 | The Dark Patrol | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1313 | Into the Gorge | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT |
| 1315 | Putting the Pieces Together | active | blocking | TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1316 | Dark Revelations | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1317 | Ride Off Into the Sunset | active | blocking | TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1318 | Hunting the Beasts | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT |
| 1319 | Dwellers of the Island | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED |
| 1321 | A Bridge Pretty Near | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT |
| 1322 | Unrest in the Forest | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1323 | Getting Some Answers | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1324 | Essence and Sensibility | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1325 | The Perfect Cut | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1326 | Mana out of Mudmen | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1327 | Garrison in Distress | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1328 | Academic Theft | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1329 | Going Above and Beyond | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1330 | Horned Horrors | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT |
| 1331 | I'll Take the High Road | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, LEVELBAND_DRIFT, TYPE_DRIFT |
| 1332 | They'll Eat Anything | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED |
| 1333 | Twice the Bark, Twice the Bite | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED |
| 1335 | One of Our Couriers is Missing | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY |
| 1336 | Chione's Missing Cargo | active | blocking | TASKREF_DRIFT, LEVELBAND_DRIFT |
| 1337 | Searching for the Stolen Stones | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT |
| 1338 | Chione's Report | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, LEVELBAND_DRIFT |
| 1339 | Sersine, She Seeks Shackles | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1340 | Painful Disc-overies | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1343 | Answers Lead to More Questions | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, GROUPLIST_UNREGISTERED, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1344 | Destroy All Destroyers! | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT |
| 1345 | Desperately Seeking Sorscha | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY |
| 1346 | Sorcha's Reckless Challenge | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, TARGET_UNSPAWNED |
| 1347 | It Was a Rock...Crawler! | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED |
| 1348 | Ferocious Flowering Felons | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1349 | Gotta Kill 'em All | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED |
| 1350 | Strange Attractors | active | blocking | TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, LEVELBAND_DRIFT |
| 1351 | Supply and Demand | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT |
| 1352 | Supply and Demand | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT |
| 1371 | Initial Warrior Training | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1372 | Initial Lancer Training | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1373 | Initial Slayer Training | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1374 | Initial Berserker Training | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1375 | Initial Archer Training | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1376 | Initial Sorcerer Training | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1377 | Initial Priest Training | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1378 | Initial Mystic Training | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, TYPE_DRIFT |
| 1379 |  | active | blocking | COMP_EMPTY, COMP_DRIFT |
| 1382 | Introduction to Gathering | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, LEVELBAND_DRIFT, TYPE_DRIFT |
| 1383 |  | active | blocking | COMP_EMPTY, COMP_DRIFT |
| 1384 | Recharge It | active | blocking | PREREQ_DRIFT, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, STORYGROUP_DRIFT, LEVELBAND_DRIFT, TYPE_DRIFT |
| 1385 | Always After Me Lucky Charms | DISABLED | blocking | SENTINEL_DISABLED, COMP_EMPTY, COMP_DRIFT |
| 1386 | Bombs Away! | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1389 | 판도라 상자 사용 안내 | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT, GIVER_UNSPAWNED, TARGET_UNSPAWNED |
| 1390 | Special Delivery | DISABLED | blocking | SENTINEL_DISABLED, TASKREF_DRIFT, COMP_EMPTY, COMP_DRIFT |
| 1341 | Bequest of the Dead &lt;Repeatable&gt; | active | drift | COMP_DRIFT |
| 1334 | Investigating the Relics &lt;Repeatable&gt; | active | clean | CLEAN |

## Blocking / drift detail

### 1301 Dawn's Early Light (blocking)
- COMP_EMPTY: v92 reward stub/absent; client=100xp 10g pp=0 v31=500xp 50g
- COMP_DRIFT: client 100xp 10g pp=0 vs v31 500xp 50g (no winner picked)

### 1302 Another Fine Mess (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=150xp 15g pp=0 v31=400xp 40g
- COMP_DRIFT: client 150xp 15g pp=0 vs v31 400xp 40g (no winner picked)

### 1303 The Secret Life of Trees (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,71', '13,72', '13,73', '13,74', '13,75', '13,76', '13,77', '13,78', '13,79'] | v92 ['13,71', '13,72', '13,73', '13,74', '13,75', '13,76', '13,77', '13,78', '13,79']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=1500xp 0g bag=class pp=0 items[17712x1/berserker,17712x1/lancer,17715x1/archer,17715x1/slayer,17715x1/warrior,17718x1/elementalist,17718x1/priest,17718x1/sorcerer] v31=2600xp 260g bag=class items[12129x1/warrior,12130x1/lancer,12131x1/slayer,12132x1/berserker,12133x1/sorcerer,12134x1/archer,12135x1/priest,12136x1/elementalist,17404x1/berserker,17404x1/engineer,17404x1/lancer,17407x1/archer,17407x1/slayer,17407x1/warrior,17410x1/elementalist,17410x1/priest,17410x1/sorcerer,55271x1/engineer]
- COMP_DRIFT: client 1500xp 0g bag=class pp=0 items[17712x1/berserker,17712x1/lancer,17715x1/archer,17715x1/slayer,17715x1/warrior,17718x1/elementalist,17718x1/priest,17718x1/sorcerer] vs v31 2600xp 260g bag=class items[12129x1/warrior,12130x1/lancer,12131x1/slayer,12132x1/berserker,12133x1/sorcerer,12134x1/archer,12135x1/priest,12136x1/elementalist,17404x1/berserker,17404x1/engineer,17404x1/lancer,17407x1/archer,17407x1/slayer,17407x1/warrior,17410x1/elementalist,17410x1/priest,17410x1/sorcerer,55271x1/engineer] (no winner picked)

### 1304 Making the Rounds (blocking)
- TASKREF_DRIFT[ref] task 2 monsters: client [] | v31 [('13,300931', '', '100')] | v92 [('13,300931', '', '100')]
- TASKREF_DRIFT[ref] task 2 visits: client ['213,1017'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 2 target_npc: client [] | v31 ['213,1017'] | v92 ['213,1017']
- TASKREF_DRIFT[ref] task 3 task-presence: client present | v92 absent
- TASKREF_DRIFT[ref] task 4 task-presence: client present | v92 absent
- COMP_EMPTY: v92 reward stub/absent; client=600xp 0g bag=class pp=0 items[17701x1/berserker,17701x1/lancer,17704x1/archer,17704x1/slayer,17704x1/warrior,17707x1/elementalist,17707x1/priest,17707x1/sorcerer] v31=800xp 80g bag=class items[10009x1/warrior,10010x1/lancer,10011x1/slayer,10012x1/berserker,10013x1/sorcerer,10014x1/archer,10015x1/priest,10016x1/elementalist,55006x1/engineer]
- COMP_DRIFT: client 600xp 0g bag=class pp=0 items[17701x1/berserker,17701x1/lancer,17704x1/archer,17704x1/slayer,17704x1/warrior,17707x1/elementalist,17707x1/priest,17707x1/sorcerer] vs v31 800xp 80g bag=class items[10009x1/warrior,10010x1/lancer,10011x1/slayer,10012x1/berserker,10013x1/sorcerer,10014x1/archer,10015x1/priest,10016x1/elementalist,55006x1/engineer] (no winner picked)

### 1305 Elleon's Fate (blocking)
- PREREQ_DRIFT: client ['13,04'] | v31 ['13,31'] | v92 ['13,31']
- TASKREF_DRIFT[ref] task 1 visits: client ['64,1001'] | v31 ['213,1008'] | v92 ['213,1008']
- TASKREF_DRIFT[ref] task 3 monsters: client [] | v31 [('13,300932', '5', '')] | v92 [('13,300932', '5', '')]
- TASKREF_DRIFT[ref] task 3 visits: client ['213,1009'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 4 visits: client ['213,1008'] | v31 ['213,1147'] | v92 ['213,1147']
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 6 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 7 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=800xp 0g bag=class pp=0 items[17710x1/berserker,17710x1/lancer,17713x1/archer,17713x1/slayer,17713x1/warrior,17716x1/elementalist,17716x1/priest,17716x1/sorcerer] v31=4900xp 490g bag=class items[10017x1/warrior,10018x1/lancer,10019x1/slayer,10020x1/berserker,10021x1/sorcerer,10022x1/archer,10023x1/priest,10024x1/elementalist,15019x1/berserker,15019x1/engineer,15019x1/lancer,15020x1/berserker,15020x1/engineer,15020x1/lancer,15021x1/berserker,15021x1/engineer,15021x1/lancer,15022x1/archer,15022x1/slayer,15022x1/warrior,15023x1/archer,15023x1/slayer,15023x1/warrior,15024x1/archer,15024x1/slayer,15024x1/warrior,15025x1/elementalist,15025x1/priest,15025x1/sorcerer,15026x1/elementalist,15026x1/priest,15026x1/sorcerer,15027x1/elementalist,15027x1/priest,15027x1/sorcerer,55007x1/engineer]
- COMP_DRIFT: client 800xp 0g bag=class pp=0 items[17710x1/berserker,17710x1/lancer,17713x1/archer,17713x1/slayer,17713x1/warrior,17716x1/elementalist,17716x1/priest,17716x1/sorcerer] vs v31 4900xp 490g bag=class items[10017x1/warrior,10018x1/lancer,10019x1/slayer,10020x1/berserker,10021x1/sorcerer,10022x1/archer,10023x1/priest,10024x1/elementalist,15019x1/berserker,15019x1/engineer,15019x1/lancer,15020x1/berserker,15020x1/engineer,15020x1/lancer,15021x1/berserker,15021x1/engineer,15021x1/lancer,15022x1/archer,15022x1/slayer,15022x1/warrior,15023x1/archer,15023x1/slayer,15023x1/warrior,15024x1/archer,15024x1/slayer,15024x1/warrior,15025x1/elementalist,15025x1/priest,15025x1/sorcerer,15026x1/elementalist,15026x1/priest,15026x1/sorcerer,15027x1/elementalist,15027x1/priest,15027x1/sorcerer,55007x1/engineer] (no winner picked)

### 1306 Traces of Darkness (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=800xp 80g pp=0 v31=800xp 80g
- TARGET_UNSPAWNED: 213,1036 not spawned in v92 (v31 spawned: False)
- GROUPLIST_UNREGISTERED: story group 1 but no v92 QuestGroupList entry.
- STORYGROUP_DRIFT: client 1 vs v92 (none)

### 1307 Live by the Sword... (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 2 monsters: client [('13,601', '', '')] | v31 [('13,601', '', '100')] | v92 [('13,601', '', '100')]
- COMP_EMPTY: v92 reward stub/absent; client=1000xp 100g bag=allpay pp=0 items[8200x1] v31=1000xp 100g bag=allpay items[8200x1]
- TARGET_UNSPAWNED: 213,1027 not spawned in v92 (v31 spawned: False)
- GROUPLIST_UNREGISTERED: story group 1 but no v92 QuestGroupList entry.
- STORYGROUP_DRIFT: client 1 vs v92 (none)

### 1308 Essence of Foreboding (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,3', '', '')] | v31 [('13,3', '', '100')] | v92 [('13,3', '', '100')]
- COMP_EMPTY: v92 reward stub/absent; client=1000xp 100g pp=0 v31=1000xp 100g
- GROUPLIST_UNREGISTERED: story group 1 but no v92 QuestGroupList entry.
- STORYGROUP_DRIFT: client 1 vs v92 (none)

### 1309 Acharak Attacks (blocking)
- PREREQ_DRIFT: client ['13,07'] | v31 ['13,11'] | v92 ['13,11']
- TASKREF_DRIFT[ref] task 1 monsters: client [('13,1002', '1', ''), ('13,1003', '5', '')] | v31 [('13,1002', '1', '')] | v92 [('13,1002', '1', '')]
- TASKREF_DRIFT[ref] task 2 target_npc: client ['213,1008'] | v31 ['213,1134'] | v92 ['213,1134']
- COMP_EMPTY: v92 reward stub/absent; client=2000xp 0g bag=class pp=0 items[10537x1/warrior,10538x1/lancer,10539x1/slayer,10540x1/berserker,10541x1/sorcerer,10542x1/archer,10543x1/priest,10544x1/elementalist] v31=3200xp 320g
- COMP_DRIFT: client 2000xp 0g bag=class pp=0 items[10537x1/warrior,10538x1/lancer,10539x1/slayer,10540x1/berserker,10541x1/sorcerer,10542x1/archer,10543x1/priest,10544x1/elementalist] vs v31 3200xp 320g (no winner picked)
- STORYGROUP_DRIFT: client 1 vs v92 2

### 1310 A Clue In the Dark (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=1000xp 100g pp=0 v31=1000xp 100g bag=class items[10017x1/warrior,10018x1/lancer,10019x1/slayer,10020x1/berserker,10021x1/sorcerer,10022x1/archer,10023x1/priest,10024x1/elementalist,15019x1/berserker,15019x1/lancer,15022x1/archer,15022x1/slayer,15022x1/warrior,15025x1/elementalist,15025x1/priest,15025x1/sorcerer,55007x1/engineer]
- COMP_DRIFT: client 1000xp 100g pp=0 vs v31 1000xp 100g bag=class items[10017x1/warrior,10018x1/lancer,10019x1/slayer,10020x1/berserker,10021x1/sorcerer,10022x1/archer,10023x1/priest,10024x1/elementalist,15019x1/berserker,15019x1/lancer,15022x1/archer,15022x1/slayer,15022x1/warrior,15025x1/elementalist,15025x1/priest,15025x1/sorcerer,55007x1/engineer] (no winner picked)
- TARGET_UNSPAWNED: 213,1130 not spawned in v92 (v31 spawned: False)
- GROUPLIST_UNREGISTERED: story group 1 but no v92 QuestGroupList entry.
- STORYGROUP_DRIFT: client 1 vs v92 (none)

### 1311 Clearing the Gorge (blocking)
- PREREQ_DRIFT: client ['13,10'] | v31 ['13,05'] | v92 ['13,05']
- TASKREF_DRIFT[ref] task 1 visits: client ['64,1001'] | v31 ['64,1033'] | v92 ['64,1033']
- TASKREF_DRIFT[ref] task 2 monsters: client [] | v31 [('13,901', '5', '')] | v92 [('13,901', '5', '')]
- TASKREF_DRIFT[ref] task 2 visits: client ['64,1033'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 3 collections: client [] | v31 ['409'] | v92 ['409']
- TASKREF_DRIFT[ref] task 3 deliver_items: client [] | v31 [('9010', '5', '')] | v92 [('9010', '5', '')]
- TASKREF_DRIFT[ref] task 3 visits: client ['213,1007'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 3 target_npc: client [] | v31 ['213,1007'] | v92 ['213,1007']
- TASKREF_DRIFT[ref] task 4 task-presence: client present | v92 absent
- COMP_EMPTY: v92 reward stub/absent; client=1000xp 100g pp=0 v31=3600xp 360g
- COMP_DRIFT: client 1000xp 100g pp=0 vs v31 3600xp 360g (no winner picked)

### 1312 The Dark Patrol (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300910', '6', '')] | v31 [('13,300910', '5', '')] | v92 [('13,300910', '5', '')]
- TASKREF_DRIFT[ref] task 2 visits: client ['213,1134'] | v31 ['213,1025'] | v92 ['213,1025']
- COMP_EMPTY: v92 reward stub/absent; client=1700xp 170g bag=class pp=0 items[15606x1/berserker,15606x1/lancer,15609x1/archer,15609x1/slayer,15609x1/warrior,15612x1/elementalist,15612x1/priest,15612x1/sorcerer] v31=2500xp 250g
- COMP_DRIFT: client 1700xp 170g bag=class pp=0 items[15606x1/berserker,15606x1/lancer,15609x1/archer,15609x1/slayer,15609x1/warrior,15612x1/elementalist,15612x1/priest,15612x1/sorcerer] vs v31 2500xp 250g (no winner picked)

### 1313 Into the Gorge (blocking)
- PREREQ_DRIFT: client ['13,11'] | v31 ['13,09'] | v92 ['13,09']
- TASKREF_DRIFT[ref] task 1 monsters: client [] | v31 [('13,300910', '5', '')] | v92 [('13,300910', '5', '')]
- TASKREF_DRIFT[ref] task 2 visits: client ['213,1005'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 3 visits: client ['213,1025'] | v31 ['213,1005'] | v92 ['213,1005']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=1000xp 100g bag=allpay pp=0 v31=6840xp 470g items[7100x1,7104x1,7108x1]
- COMP_DRIFT: client 1000xp 100g bag=allpay pp=0 vs v31 6840xp 470g items[7100x1,7104x1,7108x1] (no winner picked)

### 1315 Putting the Pieces Together (blocking)
- TASKREF_DRIFT[ref] task 1 monsters: client [('13,8', '', '')] | v31 [('13,1004', '1', '')] | v92 [('13,1004', '1', '')]
- TASKREF_DRIFT[ref] task 1 target_npc: client ['213,1026'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 2 deliver_direct: client [('@quest:1315009', '10')] | v31 [('@quest:1315004', '1')] | v92 [('@quest:1315004', '1')]
- TASKREF_DRIFT[ref] task 3 task-presence: client present | v92 absent
- TASKREF_DRIFT[ref] task 4 task-presence: client present | v92 absent
- COMP_EMPTY: v92 reward stub/absent; client=5200xp 0g bag=class pp=0 items[15668x1/berserker,15668x1/lancer,15671x1/archer,15671x1/slayer,15671x1/warrior,15674x1/elementalist,15674x1/priest,15674x1/sorcerer] v31=4500xp 450g bag=class items[12137x1/warrior,12138x1/lancer,12139x1/slayer,12140x1/berserker,12141x1/sorcerer,12142x1/archer,12143x1/priest,12144x1/elementalist,17413x1/berserker,17413x1/engineer,17413x1/lancer,17416x1/archer,17416x1/slayer,17416x1/warrior,17419x1/elementalist,17419x1/priest,17419x1/sorcerer,55272x1/engineer]
- COMP_DRIFT: client 5200xp 0g bag=class pp=0 items[15668x1/berserker,15668x1/lancer,15671x1/archer,15671x1/slayer,15671x1/warrior,15674x1/elementalist,15674x1/priest,15674x1/sorcerer] vs v31 4500xp 450g bag=class items[12137x1/warrior,12138x1/lancer,12139x1/slayer,12140x1/berserker,12141x1/sorcerer,12142x1/archer,12143x1/priest,12144x1/elementalist,17413x1/berserker,17413x1/engineer,17413x1/lancer,17416x1/archer,17416x1/slayer,17416x1/warrior,17419x1/elementalist,17419x1/priest,17419x1/sorcerer,55272x1/engineer] (no winner picked)

### 1316 Dark Revelations (blocking)
- PREREQ_DRIFT: client ['13,43'] | v31 ['13,15'] | v92 ['13,15']
- TASKREF_DRIFT[ref] task 1 monsters: client [('436,1002', '1', '')] | v31 [('13,8', '', ''), ('13,9', '', '')] | v92 [('13,8', '', ''), ('13,9', '', '')]
- TASKREF_DRIFT[ref] task 3 deliver_direct: client [('@quest:1316006', '1')] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 3 target_npc: client ['213,1025'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 4 monsters: client [] | v31 [('436,1002', '1', '')] | v92 [('436,1002', '1', '')]
- TASKREF_DRIFT[ref] task 4 deliver_direct: client [('@quest:1316010', '1')] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 4 target_npc: client ['213,1037'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 5 deliver_direct: client [('@quest:1316014', '1')] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 5 target_npc: client ['64,1001'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 6 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 7 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 8 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=6000xp 0g bag=class pp=0 items[10593x1/warrior,10594x1/lancer,10595x1/slayer,10596x1/berserker,10597x1/sorcerer,10598x1/archer,10599x1/priest,10600x1/elementalist,160x2/archer,160x2/berserker,160x2/elementalist,160x2/lancer,160x2/priest,160x2/slayer,160x2/sorcerer,160x2/warrior] v31=14600xp 1460g bag=class items[10593x1/warrior,10594x1/lancer,10595x1/slayer,10596x1/berserker,10597x1/sorcerer,10598x1/archer,10599x1/priest,10600x1/elementalist,55079x1/engineer]
- COMP_DRIFT: client 6000xp 0g bag=class pp=0 items[10593x1/warrior,10594x1/lancer,10595x1/slayer,10596x1/berserker,10597x1/sorcerer,10598x1/archer,10599x1/priest,10600x1/elementalist,160x2/archer,160x2/berserker,160x2/elementalist,160x2/lancer,160x2/priest,160x2/slayer,160x2/sorcerer,160x2/warrior] vs v31 14600xp 1460g bag=class items[10593x1/warrior,10594x1/lancer,10595x1/slayer,10596x1/berserker,10597x1/sorcerer,10598x1/archer,10599x1/priest,10600x1/elementalist,55079x1/engineer] (no winner picked)

### 1317 Ride Off Into the Sunset (blocking)
- TASKREF_DRIFT[ref] task 4 visits: client ['63,1097'] | v31 ['63,1107'] | v92 ['63,1107']
- TASKREF_DRIFT[ref] task 5 task-presence: client present | v92 absent
- COMP_EMPTY: v92 reward stub/absent; client=1500xp 0g bag=class pp=0 items[15667x1/berserker,15667x1/lancer,15670x1/archer,15670x1/slayer,15670x1/warrior,15673x1/elementalist,15673x1/priest,15673x1/sorcerer] v31=2000xp 200g bag=class items[15667x1/berserker,15667x1/engineer,15667x1/lancer,15670x1/archer,15670x1/slayer,15670x1/warrior,15673x1/elementalist,15673x1/priest,15673x1/sorcerer]
- COMP_DRIFT: client 1500xp 0g bag=class pp=0 items[15667x1/berserker,15667x1/lancer,15670x1/archer,15670x1/slayer,15670x1/warrior,15673x1/elementalist,15673x1/priest,15673x1/sorcerer] vs v31 2000xp 200g bag=class items[15667x1/berserker,15667x1/engineer,15667x1/lancer,15670x1/archer,15670x1/slayer,15670x1/warrior,15673x1/elementalist,15673x1/priest,15673x1/sorcerer] (no winner picked)

### 1318 Hunting the Beasts (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300921', '', '')] | v31 [('13,300921', '', '100')] | v92 [('13,300921', '', '100')]
- TASKREF_DRIFT[ref] task 1 target_npc: client ['213,1114'] | v31 ['213,1004'] | v92 ['213,1004']
- COMP_EMPTY: v92 reward stub/absent; client=900xp 90g bag=allpay pp=0 items[5132x1] v31=1500xp 150g
- COMP_DRIFT: client 900xp 90g bag=allpay pp=0 items[5132x1] vs v31 1500xp 150g (no winner picked)

### 1319 Dwellers of the Island (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300941', '', ''), ('13,300944', '', '')] | v31 [('13,300941', '', '12'), ('13,300944', '', '85')] | v92 [('13,300941', '', '12'), ('13,300944', '', '85')]
- COMP_EMPTY: v92 reward stub/absent; client=600xp 0g bag=class pp=0 items[12401x1/warrior,12402x1/lancer,12403x1/slayer,12404x1/berserker,12405x1/sorcerer,12406x1/archer,12407x1/priest,12408x1/elementalist] v31=600xp 60g bag=class items[12401x1/warrior,12402x1/lancer,12403x1/slayer,12404x1/berserker,12405x1/sorcerer,12406x1/archer,12407x1/priest,12408x1/elementalist,55305x1/engineer]
- COMP_DRIFT: client 600xp 0g bag=class pp=0 items[12401x1/warrior,12402x1/lancer,12403x1/slayer,12404x1/berserker,12405x1/sorcerer,12406x1/archer,12407x1/priest,12408x1/elementalist] vs v31 600xp 60g bag=class items[12401x1/warrior,12402x1/lancer,12403x1/slayer,12404x1/berserker,12405x1/sorcerer,12406x1/archer,12407x1/priest,12408x1/elementalist,55305x1/engineer] (no winner picked)
- GIVER_UNSPAWNED: giver 213,1110 not spawned in v92 (v31 spawned: False)
- TARGET_UNSPAWNED: 213,1110 not spawned in v92 (v31 spawned: False)

### 1321 A Bridge Pretty Near (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=300xp 30g pp=0 v31=800xp 80g
- COMP_DRIFT: client 300xp 30g pp=0 vs v31 800xp 80g (no winner picked)

### 1322 Unrest in the Forest (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300931', '4', '')] | v31 [('13,300931', '5', '')] | v92 [('13,300931', '5', '')]
- COMP_EMPTY: v92 reward stub/absent; client=500xp 0g bag=class pp=0 items[17703x1/berserker,17703x1/lancer,17706x1/archer,17706x1/slayer,17706x1/warrior,17709x1/elementalist,17709x1/priest,17709x1/sorcerer] v31=500xp 50g bag=class items[17703x1/berserker,17703x1/engineer,17703x1/lancer,17706x1/archer,17706x1/slayer,17706x1/warrior,17709x1/elementalist,17709x1/priest,17709x1/sorcerer]
- COMP_DRIFT: client 500xp 0g bag=class pp=0 items[17703x1/berserker,17703x1/lancer,17706x1/archer,17706x1/slayer,17706x1/warrior,17709x1/elementalist,17709x1/priest,17709x1/sorcerer] vs v31 500xp 50g bag=class items[17703x1/berserker,17703x1/engineer,17703x1/lancer,17706x1/archer,17706x1/slayer,17706x1/warrior,17709x1/elementalist,17709x1/priest,17709x1/sorcerer] (no winner picked)

### 1323 Getting Some Answers (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300931', '', '')] | v31 [('13,300931', '', '100')] | v92 [('13,300931', '', '100')]
- COMP_EMPTY: v92 reward stub/absent; client=800xp 80g bag=allpay pp=0 items[5132x1] v31=800xp 80g bag=class items[10009x1/warrior,10010x1/lancer,10011x1/slayer,10012x1/berserker,10013x1/sorcerer,10014x1/archer,10015x1/priest,10016x1/elementalist,55006x1/engineer]
- COMP_DRIFT: client 800xp 80g bag=allpay pp=0 items[5132x1] vs v31 800xp 80g bag=class items[10009x1/warrior,10010x1/lancer,10011x1/slayer,10012x1/berserker,10013x1/sorcerer,10014x1/archer,10015x1/priest,10016x1/elementalist,55006x1/engineer] (no winner picked)

### 1324 Essence and Sensibility (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300930', '', ''), ('13,300933', '', '')] | v31 [('13,300930', '', '100'), ('13,300933', '', '85')] | v92 [('13,300930', '', '100'), ('13,300933', '', '85')]
- COMP_EMPTY: v92 reward stub/absent; client=900xp 90g bag=allpay pp=0 items[5132x1] v31=900xp 90g bag=allpay
- COMP_DRIFT: client 900xp 90g bag=allpay pp=0 items[5132x1] vs v31 900xp 90g bag=allpay (no winner picked)

### 1325 The Perfect Cut (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,1', '', '')] | v31 [('13,1', '', '30')] | v92 [('13,1', '', '30')]
- COMP_EMPTY: v92 reward stub/absent; client=500xp 0g bag=class pp=0 items[17702x1/berserker,17702x1/lancer,17705x1/archer,17705x1/slayer,17705x1/warrior,17708x1/elementalist,17708x1/priest,17708x1/sorcerer] v31=500xp 50g bag=class items[17702x1/berserker,17702x1/engineer,17702x1/lancer,17705x1/archer,17705x1/slayer,17705x1/warrior,17708x1/elementalist,17708x1/priest,17708x1/sorcerer]
- COMP_DRIFT: client 500xp 0g bag=class pp=0 items[17702x1/berserker,17702x1/lancer,17705x1/archer,17705x1/slayer,17705x1/warrior,17708x1/elementalist,17708x1/priest,17708x1/sorcerer] vs v31 500xp 50g bag=class items[17702x1/berserker,17702x1/engineer,17702x1/lancer,17705x1/archer,17705x1/slayer,17705x1/warrior,17708x1/elementalist,17708x1/priest,17708x1/sorcerer] (no winner picked)

### 1326 Mana out of Mudmen (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,2', '', '')] | v31 [('13,2', '', '90')] | v92 [('13,2', '', '90')]
- COMP_EMPTY: v92 reward stub/absent; client=2000xp 200g bag=choice pp=0 items[125x10,129x1,130x1] v31=2000xp 200g bag=class items[15021x1/berserker,15021x1/engineer,15021x1/lancer,15024x1/archer,15024x1/slayer,15024x1/warrior,15027x1/elementalist,15027x1/priest,15027x1/sorcerer]
- COMP_DRIFT: client 2000xp 200g bag=choice pp=0 items[125x10,129x1,130x1] vs v31 2000xp 200g bag=class items[15021x1/berserker,15021x1/engineer,15021x1/lancer,15024x1/archer,15024x1/slayer,15024x1/warrior,15027x1/elementalist,15027x1/priest,15027x1/sorcerer] (no winner picked)

### 1327 Garrison in Distress (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[ref] task 3 monsters: client [('13,304', '', '')] | v31 [('13,300921', '', '100')] | v92 [('13,300921', '', '100')]
- COMP_EMPTY: v92 reward stub/absent; client=800xp 80g bag=allpay pp=0 items[5132x1] v31=800xp 80g bag=allpay
- COMP_DRIFT: client 800xp 80g bag=allpay pp=0 items[5132x1] vs v31 800xp 80g bag=allpay (no winner picked)

### 1328 Academic Theft (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,301191', '', ''), ('13,301193', '', ''), ('13,301194', '', '')] | v31 [('13,301191', '', '12'), ('13,301193', '', '12'), ('13,301194', '', '90')] | v92 [('13,301191', '', '12'), ('13,301193', '', '12'), ('13,301194', '', '90')]
- COMP_EMPTY: v92 reward stub/absent; client=1100xp 110g bag=allpay pp=0 items[5132x1] v31=1500xp 150g
- COMP_DRIFT: client 1100xp 110g bag=allpay pp=0 items[5132x1] vs v31 1500xp 150g (no winner picked)

### 1329 Going Above and Beyond (blocking)
- PREREQ_DRIFT: client ['13,04'] | v31 ['13,03'] | v92 ['13,03']
- TASKREF_DRIFT[ref] task 1 deliver_items: client [] | v31 [('5002', '', '')] | v92 [('5002', '', '')]
- TASKREF_DRIFT[ref] task 1 visits: client ['64,1006'] | v31 ['64,1029'] | v92 ['64,1029']
- TASKREF_DRIFT[ref] task 2 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 3 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=100xp 10g bag=class pp=0 items[12409x1/warrior,12410x1/lancer,12411x1/slayer,12412x1/berserker,12413x1/sorcerer,12414x1/archer,12415x1/priest,12416x1/elementalist] v31=400xp 10g bag=allpay items[7200x10,8007x3]
- COMP_DRIFT: client 100xp 10g bag=class pp=0 items[12409x1/warrior,12410x1/lancer,12411x1/slayer,12412x1/berserker,12413x1/sorcerer,12414x1/archer,12415x1/priest,12416x1/elementalist] vs v31 400xp 10g bag=allpay items[7200x10,8007x3] (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1330 Horned Horrors (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300932', '4', '')] | v31 [('13,300932', '5', '')] | v92 [('13,300932', '5', '')]
- COMP_EMPTY: v92 reward stub/absent; client=1900xp 190g bag=allpay pp=0 items[5132x1] v31=1900xp 190g bag=class items[15020x1/berserker,15020x1/engineer,15020x1/lancer,15023x1/archer,15023x1/slayer,15023x1/warrior,15026x1/elementalist,15026x1/priest,15026x1/sorcerer]
- COMP_DRIFT: client 1900xp 190g bag=allpay pp=0 items[5132x1] vs v31 1900xp 190g bag=class items[15020x1/berserker,15020x1/engineer,15020x1/lancer,15023x1/archer,15023x1/slayer,15023x1/warrior,15026x1/elementalist,15026x1/priest,15026x1/sorcerer] (no winner picked)

### 1331 I'll Take the High Road (blocking)
- PREREQ_DRIFT: client ['13,86'] | v31 ['13,82', '13,83'] | v92 ['13,82', '13,83']
- TASKREF_DRIFT[ref] task 1 deliver_items: client [] | v31 [('200001', '', '')] | v92 [('200001', '', '')]
- TASKREF_DRIFT[ref] task 1 visits: client ['213,1053'] | v31 ['64,1024'] | v92 ['64,1024']
- TASKREF_DRIFT[ref] task 2 monsters: client [] | v31 [('13,301191', '', '12'), ('13,301193', '', '12'), ('13,301194', '', '90')] | v92 [('13,301191', '', '12'), ('13,301193', '', '12'), ('13,301194', '', '90')]
- TASKREF_DRIFT[ref] task 2 collections: client ['492'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 2 deliver_items: client [('9095', '1', '')] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 2 target_npc: client ['64,1001'] | v31 ['213,1053'] | v92 ['213,1053']
- TASKREF_DRIFT[ref] task 3 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=800xp 80g bag=allpay pp=0 items[8007x2] v31=2300xp 230g bag=class items[17710x1/berserker,17710x1/engineer,17710x1/lancer,17713x1/archer,17713x1/slayer,17713x1/warrior,17716x1/elementalist,17716x1/priest,17716x1/sorcerer]
- COMP_DRIFT: client 800xp 80g bag=allpay pp=0 items[8007x2] vs v31 2300xp 230g bag=class items[17710x1/berserker,17710x1/engineer,17710x1/lancer,17713x1/archer,17713x1/slayer,17713x1/warrior,17716x1/elementalist,17716x1/priest,17716x1/sorcerer] (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1332 They'll Eat Anything (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300920', '', '')] | v31 [('13,300920', '', '100')] | v92 [('13,300920', '', '100')]
- COMP_EMPTY: v92 reward stub/absent; client=900xp 90g bag=allpay pp=0 items[5132x1] v31=900xp 90g bag=allpay
- COMP_DRIFT: client 900xp 90g bag=allpay pp=0 items[5132x1] vs v31 900xp 90g bag=allpay (no winner picked)
- GIVER_UNSPAWNED: giver 213,1009 not spawned in v92 (v31 spawned: False)
- TARGET_UNSPAWNED: 213,1130 not spawned in v92 (v31 spawned: False)

### 1333 Twice the Bark, Twice the Bite (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300911', '', '')] | v31 [('13,300911', '', '90')] | v92 [('13,300911', '', '90')]
- COMP_EMPTY: v92 reward stub/absent; client=1700xp 170g bag=allpay pp=0 items[5132x1] v31=1700xp 170g bag=allpay
- COMP_DRIFT: client 1700xp 170g bag=allpay pp=0 items[5132x1] vs v31 1700xp 170g bag=allpay (no winner picked)
- GIVER_UNSPAWNED: giver 213,1130 not spawned in v92 (v31 spawned: False)
- TARGET_UNSPAWNED: 213,1130 not spawned in v92 (v31 spawned: False)

### 1335 One of Our Couriers is Missing (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=600xp 60g pp=0 v31=600xp 60g

### 1336 Chione's Missing Cargo (blocking)
- TASKREF_DRIFT[ref] task 1 collections: client ['409'] | v31 ['409'] | v92 ['403']  <-- v31 agrees client (v92 regression, mechanical fix)
- TASKREF_DRIFT[count] task 1 deliver_items: client [('9010', '4', '')] | v31 [('9010', '5', '')] | v92 [('9010', '5', '')]

### 1337 Searching for the Stolen Stones (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[ref] task 1 monsters: client [('13,300943', '', ''), ('13,300945', '', '')] | v31 [('13,901', '', '95')] | v92 [('13,901', '', '95')]
- COMP_EMPTY: v92 reward stub/absent; client=1100xp 0g bag=class pp=0 items[15605x1/berserker,15605x1/lancer,15608x1/archer,15608x1/slayer,15608x1/warrior,15611x1/elementalist,15611x1/priest,15611x1/sorcerer] v31=1500xp 150g
- COMP_DRIFT: client 1100xp 0g bag=class pp=0 items[15605x1/berserker,15605x1/lancer,15608x1/archer,15608x1/slayer,15608x1/warrior,15611x1/elementalist,15611x1/priest,15611x1/sorcerer] vs v31 1500xp 150g (no winner picked)

### 1338 Chione's Report (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[ref] task 1 visits: client ['213,1137'] | v31 ['213,1134'] | v92 ['213,1134']
- COMP_EMPTY: v92 reward stub/absent; client=500xp 50g pp=0 v31=500xp 50g

### 1339 Sersine, She Seeks Shackles (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300942', '', ''), ('13,6', '', '')] | v31 [('13,300942', '', '5'), ('13,6', '', '95')] | v92 [('13,300942', '', '5'), ('13,6', '', '95')]
- COMP_EMPTY: v92 reward stub/absent; client=2900xp 290g bag=allpay pp=0 items[5132x1] v31=3200xp 320g
- COMP_DRIFT: client 2900xp 290g bag=allpay pp=0 items[5132x1] vs v31 3200xp 320g (no winner picked)

### 1340 Painful Disc-overies (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,7', '8', '')] | v31 [('13,7', '5', '')] | v92 [('13,7', '5', '')]
- COMP_EMPTY: v92 reward stub/absent; client=2300xp 230g bag=choice pp=0 items[7100x1,7104x1,7108x1] v31=3200xp 320g
- COMP_DRIFT: client 2300xp 230g bag=choice pp=0 items[7100x1,7104x1,7108x1] vs v31 3200xp 320g (no winner picked)

### 1343 Answers Lead to More Questions (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=800xp 80g pp=0 v31=800xp 80g
- GROUPLIST_UNREGISTERED: story group 2 but no v92 QuestGroupList entry.
- STORYGROUP_DRIFT: client 2 vs v92 (none)

### 1344 Destroy All Destroyers! (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=3000xp 300g bag=allpay pp=0 items[5132x1] v31=3000xp 300g bag=allpay
- COMP_DRIFT: client 3000xp 300g bag=allpay pp=0 items[5132x1] vs v31 3000xp 300g bag=allpay (no winner picked)

### 1345 Desperately Seeking Sorscha (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=500xp 50g bag=allpay pp=0 items[8007x1] v31=500xp 50g bag=allpay items[8007x1]

### 1346 Sorcha's Reckless Challenge (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[ref] task 1 dungeon: client  | v31 9037 | v92 9037
- COMP_EMPTY: v92 reward stub/absent; client=6000xp 600g pp=0 v31=6000xp 600g
- TARGET_UNSPAWNED: 437,1001 not spawned in v92 (v31 spawned: True)

### 1347 It Was a Rock...Crawler! (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,300541', '', ''), ('13,300542', '', '')] | v31 [('13,300541', '', '17'), ('13,300542', '', '100')] | v92 [('13,300541', '', '17'), ('13,300542', '', '100')]
- COMP_EMPTY: v92 reward stub/absent; client=900xp 0g bag=class pp=0 items[17711x1/berserker,17711x1/lancer,17714x1/archer,17714x1/slayer,17714x1/warrior,17717x1/elementalist,17717x1/priest,17717x1/sorcerer] v31=900xp 90g bag=class items[17711x1/berserker,17711x1/engineer,17711x1/lancer,17714x1/archer,17714x1/slayer,17714x1/warrior,17717x1/elementalist,17717x1/priest,17717x1/sorcerer]
- COMP_DRIFT: client 900xp 0g bag=class pp=0 items[17711x1/berserker,17711x1/lancer,17714x1/archer,17714x1/slayer,17714x1/warrior,17717x1/elementalist,17717x1/priest,17717x1/sorcerer] vs v31 900xp 90g bag=class items[17711x1/berserker,17711x1/engineer,17711x1/lancer,17714x1/archer,17714x1/slayer,17714x1/warrior,17717x1/elementalist,17717x1/priest,17717x1/sorcerer] (no winner picked)
- GIVER_UNSPAWNED: giver 213,1128 not spawned in v92 (v31 spawned: False)
- TARGET_UNSPAWNED: 213,1128 not spawned in v92 (v31 spawned: False)

### 1348 Ferocious Flowering Felons (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[count] task 1 monsters: client [('13,302', '', ''), ('13,303', '', '')] | v31 [('13,302', '', '90'), ('13,303', '', '17')] | v92 [('13,302', '', '90'), ('13,303', '', '17')]
- COMP_EMPTY: v92 reward stub/absent; client=900xp 90g bag=allpay pp=0 items[5132x1] v31=900xp 90g bag=allpay
- COMP_DRIFT: client 900xp 90g bag=allpay pp=0 items[5132x1] vs v31 900xp 90g bag=allpay (no winner picked)

### 1349 Gotta Kill 'em All (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=2300xp 230g bag=allpay pp=0 items[5132x1] v31=2300xp 230g bag=allpay
- COMP_DRIFT: client 2300xp 230g bag=allpay pp=0 items[5132x1] vs v31 2300xp 230g bag=allpay (no winner picked)
- GIVER_UNSPAWNED: giver 213,1126 not spawned in v92 (v31 spawned: False)
- TARGET_UNSPAWNED: 213,1126 not spawned in v92 (v31 spawned: False)

### 1350 Strange Attractors (blocking)
- TASKREF_DRIFT[ref] task 1 monsters: client [('13,300951', '', ''), ('13,300960', '', '')] | v31 [('13,300942', '', '5'), ('13,6', '', '95'), ('13,7', '', '100')] | v92 [('13,300942', '', '5'), ('13,6', '', '95'), ('13,7', '', '100')]
- TASKREF_DRIFT[ref] task 1 target_npc: client ['213,1026'] | v31 ['213,1025'] | v92 ['213,1025']
- COMP_EMPTY: v92 reward stub/absent; client=1800xp 180g pp=0 v31=8400xp 840g
- COMP_DRIFT: client 1800xp 180g pp=0 vs v31 8400xp 840g (no winner picked)

### 1351 Supply and Demand (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=800xp 80g bag=allpay pp=0 items[6048x5] v31=800xp 80g bag=allpay items[6048x3]
- COMP_DRIFT: client 800xp 80g bag=allpay pp=0 items[6048x5] vs v31 800xp 80g bag=allpay items[6048x3] (no winner picked)

### 1352 Supply and Demand (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=800xp 80g bag=allpay pp=0 items[6048x5] v31=800xp 80g bag=allpay items[6048x3]
- COMP_DRIFT: client 800xp 80g bag=allpay pp=0 items[6048x5] vs v31 800xp 80g bag=allpay items[6048x3] (no winner picked)

### 1371 Initial Warrior Training (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,04'] | v92 ['13,04']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 2100xp 150g (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1372 Initial Lancer Training (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,04'] | v92 ['13,04']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 2100xp 150g (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1373 Initial Slayer Training (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,04'] | v92 ['13,04']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 2100xp 150g (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1374 Initial Berserker Training (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,04'] | v92 ['13,04']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 2100xp 150g (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1375 Initial Archer Training (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,04'] | v92 ['13,04']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 2100xp 150g (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1376 Initial Sorcerer Training (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,04'] | v92 ['13,04']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 2100xp 150g (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1377 Initial Priest Training (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,04'] | v92 ['13,04']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 2100xp 150g (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1378 Initial Mystic Training (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,04'] | v92 ['13,04']
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 2100xp 150g (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1379  (blocking)
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g v31=2100xp 150g
- COMP_DRIFT: client 50xp 5g vs v31 2100xp 150g (no winner picked)

### 1382 Introduction to Gathering (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,84'] | v92 ['13,84']
- TASKREF_DRIFT[ref] task 1 collections: client ['496'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 1 deliver_items: client [('9100', '2', '')] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 1 visits: client [] | v31 ['64,1007'] | v92 ['64,1007']
- TASKREF_DRIFT[ref] task 1 target_npc: client ['64,1048'] | v31 [] | v92 []
- TASKREF_DRIFT[ref] task 2 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 3 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=100xp 10g pp=0 v31=100xp
- COMP_DRIFT: client 100xp 10g pp=0 vs v31 100xp (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1383  (blocking)
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g v31=100xp
- COMP_DRIFT: client 50xp 5g vs v31 100xp (no winner picked)

### 1384 Recharge It (blocking)
- PREREQ_DRIFT: client [] | v31 ['13,29'] | v92 ['13,29']
- TASKREF_DRIFT[ref] task 1 visits: client [] | v31 ['64,1005'] | v92 ['64,1005']
- TASKREF_DRIFT[ref] task 2 deliver_items: client [] | v31 [('98', '', '')] | v92 [('70033', '', ''), ('98', '', '')]
- TASKREF_DRIFT[ref] task 3 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 4 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 5 task-presence: client absent | v92 present
- TASKREF_DRIFT[ref] task 6 task-presence: client absent | v92 present
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g bag=allpay pp=0 items[7100x2] v31=900xp 80g bag=allpay items[6048x3,7100x2]
- COMP_DRIFT: client 50xp 5g bag=allpay pp=0 items[7100x2] vs v31 900xp 80g bag=allpay items[6048x3,7100x2] (no winner picked)
- STORYGROUP_DRIFT: client (none) vs v92 1

### 1385 Always After Me Lucky Charms (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- COMP_EMPTY: v92 reward stub/absent; client=50xp 5g pp=0 v31=50xp
- COMP_DRIFT: client 50xp 5g pp=0 vs v31 50xp (no winner picked)

### 1386 Bombs Away! (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[ref] task 1 deliver_items: client [] | v31 [('5002', '', '')] | v92 [('5002', '', '')]
- TASKREF_DRIFT[count] task 2 monsters: client [('13,888', '5', '')] | v31 [('13,888', '3', '')] | v92 [('13,888', '3', '')]
- TASKREF_DRIFT[ref] task 3 deliver_items: client [] | v31 [('5002', '', '')] | v92 [('5002', '', '')]
- COMP_EMPTY: v92 reward stub/absent; client=300xp 30g bag=allpay pp=0 items[7200x10] v31=300xp bag=allpay items[7200x10]
- COMP_DRIFT: client 300xp 30g bag=allpay pp=0 items[7200x10] vs v31 300xp bag=allpay items[7200x10] (no winner picked)

### 1389 판도라 상자 사용 안내 (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[ref] task 1 deliver_items: client [] | v31 [('1002', '', '')] | v92 [('1002', '', '')]
- COMP_EMPTY: v92 reward stub/absent; client=200xp 20g pp=0 v31=200xp
- COMP_DRIFT: client 200xp 20g pp=0 vs v31 200xp (no winner picked)
- GIVER_UNSPAWNED: giver 213,1020 not spawned in v92 (v31 spawned: False)
- TARGET_UNSPAWNED: 213,1020 not spawned in v92 (v31 spawned: False)

### 1390 Special Delivery (blocking)
- SENTINEL_DISABLED: v92 prereq is the 99,99 disable sentinel.
- TASKREF_DRIFT[ref] task 3 target_npc: client ['213,1130'] | v31 ['213,1141'] | v92 ['213,1141']
- COMP_EMPTY: v92 reward stub/absent; client=300xp 30g bag=allpay pp=0 items[160x2] v31=300xp bag=allpay items[160x2]
- COMP_DRIFT: client 300xp 30g bag=allpay pp=0 items[160x2] vs v31 300xp bag=allpay items[160x2] (no winner picked)

### 1341 Bequest of the Dead &lt;Repeatable&gt; (drift)
- COMP_DRIFT: client 1000xp 100g pp=0 vs v31 1500xp bag=allpay items[7100x1,7104x1,7108x1] (no winner picked)

