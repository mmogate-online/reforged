# Quest Reward Ledger: IDs 1336 to 1352

Scope: quest ids 1336 through 1352 inclusive (17 ids). Source: datasheet-v92 (current server state).

## Section 1: Quest Summary

| id | title | category | level | storyGroup | enabled | giver | prerequisites | exp | gold | reward item rows |
|---|---|---|---|---|---|---|---|---|---|---|
| 1336 | Chione's Missing Cargo | Normal | recommended 7, min 7 | none | live | Chione (213,1007) | 1335 (One of Our Couriers Is Missing) | 600 | 60 | 0 |
| 1337 | The Last One | Normal | recommended 7, min 7 | none | live | Chione (213,1007) | 1335 (One of Our Couriers Is Missing) | 1500 | 150 | 0 |
| 1338 | Chione's Report | Normal | recommended 7, min 7 | none | live | Chione (213,1007) | 1337 (The Last One) | 500 | 50 | 0 |
| 1339 | Sersine, She Seeks Shackles | Normal | recommended 8, min 8 | none | live | Sersine (213,1025) | 1313 (Into the Gorge) | 3200 | 320 | 0 |
| 1340 | Painful Disc-overies | Normal | recommended 8, min 8 | none | live | Perrin (213,1143) | none | 3200 | 320 | 0 |
| 1341 | Bequest of the Dead (Repeatable) | Normal | recommended 8, min 8, max 12 | none | live | Fili (213,1141) | none | 1500 | none | 3 |
| 1342 | (no quest data) | | | | | | | | | |
| 1343 | Answers Lead to More Questions | Normal | recommended 11, min 9 | none | live | Sersine (213,1025) | 1316 (Dark Revelations) | 800 | 80 | 0 |
| 1344 | Destroy All Destroyers | Normal | recommended 9, min 9 | none | live | Perrin (213,1143) | 1343 (Answers Lead to More Questions) | 3000 | 300 | 0 |
| 1345 | Desperately Seeking Sorcha | Normal | recommended 10, min 8 | none | live | Jorhon (64,1006) | none | 500 | 50 | 1 |
| 1346 | Sorcha's Reckless Challenge | Normal | recommended 10, min 8 | none | live | Tainted Gorge Teleportal (64,1050) | 1345 (Desperately Seeking Sorcha) | 6000 | 600 | 0 |
| 1347 | It Was a Rock...Crawler | Normal | recommended 6, min 6 | none | live | Lorin (213,1128) | none | 900 | 90 | 12 |
| 1348 | Ferocious Flowering Felons | Normal | recommended 4, min 5 | none | live | Tanli (213,1147) | none | 900 | 90 | 0 |
| 1349 | Gotta Kill 'Em All | Normal | recommended 8, min 7 | none | live | Ayrdoss (213,1126) | none | 2300 | 230 | 0 |
| 1350 | Strange Attractors | Mission | recommended 8, min 8 | 2 | live | Sersine (213,1025) | 1313 (Into the Gorge) | 8400 | 840 | 0 |
| 1351 | Supply and Demand | Normal | recommended 4, min 4 | none | live | Jorhon (64,1006) | 1329 (Going Above and Beyond) | 800 | 80 | 1 |
| 1352 | Supply and Demand | Normal | recommended 4, min 4 | none | live | Jorhon (64,1006) | 1329 (Going Above and Beyond) | 800 | 80 | 1 |

## Section 2: Per-Quest Detail

### 1336: Chione's Missing Cargo

Category: Normal. Not repeatable (1회성). Cancellable.

Tasks (ordered):
1. Collect, type Collect: collection id 409, deliver item 9010 x5 to Chione (213,1007). Required count: 5.

Rewards: exp 600, gold 60. No reward item rows.

### 1337: The Last One

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. HuntAndDeliver: monster 13,901 (95% drop chance per kill), deliver 5 items to Chione (213,1007). Required count: 5.

Rewards: exp 1500, gold 150. No reward item rows.

### 1338: Chione's Report

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. Visit: Edan (213,1134). No count (visit only).

Rewards: exp 500, gold 50. No reward item rows.

### 1339: Sersine, She Seeks Shackles

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. HuntAndDeliver: monster 13,6 (95% drop chance) and monster 13,300942 (5% drop chance), deliver 5 items total to Sersine (213,1025). Required count: 5.

Rewards: exp 3200, gold 320. No reward item rows.

### 1340: Painful Disc-overies

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. Hunt: 5x monster 13,7. Required count: 5.
2. Visit: Perrin (213,1143). No count.

Rewards: exp 3200, gold 320. No reward item rows.

### 1341: Bequest of the Dead (Repeatable)

Category: Normal. Repeatable (반복). Cancellable. Level condition: minLevel 8, maxLevel 12 (level-capped quest).

Tasks (ordered):
1. Collect: collection id 411, deliver item 9012 x5 to Fili (213,1141). Required count: 5.

Rewards: exp 1500. No gold value present (only quest in range without a gold reward). itemBag: allpay.

Reward item rows:

| templateId | qty | class |
|---|---|---|
| 7100 | 1 | (any) |
| 7104 | 1 | (any) |
| 7108 | 1 | (any) |

### 1342: (no quest found)

`lookup_quest(1342)` returned not found. `lookup_quest_rewards(1342)` reported: "Quest is registered but defines no compensation (empty reward stub)." The reward-side registry has a stub entry for this id, but the quest body itself does not exist. See Section 4.

### 1343: Answers Lead to More Questions

Category: Normal. Not repeatable. Not cancellable (불가능).

Tasks (ordered):
1. DeliverInjectedItem: deliver 1 injected item to Gregor (213,1028). Required count: 1.
2. DeliverInjectedItem: deliver 1 injected item to Leander (213,1008). Required count: 1.
3. DeliverInjectedItem: deliver 1 injected item to Sersine (213,1025). Required count: 1.

Rewards: exp 800, gold 80. No reward item rows.

### 1344: Destroy All Destroyers

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. Visit: Gregor (213,1028). No count.
2. Hunt: 5x monster 13,9. Required count: 5.
3. Visit: Gregor (213,1028). No count.
4. Visit: Perrin (213,1143). No count.

Rewards: exp 3000, gold 300, itemBag: allpay. No reward item rows returned despite the allpay bag declaration.

### 1345: Desperately Seeking Sorcha

Category: Normal. Not repeatable. Cancellable. connectedQuest links to 1346.

Tasks (ordered):
1. Visit: Gurney (64,1007). No count.
2. Visit: Tainted Gorge Teleportal (64,1050). No count.

Rewards: exp 500, gold 50, itemBag: allpay.

Reward item rows:

| templateId | qty | class |
|---|---|---|
| 8007 | 1 | (any) |

### 1346: Sorcha's Reckless Challenge

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. Guardian: dungeon id 9037, target NPC Sorcha (437,1001), aggro injection interval 3s, aggro injection value 1, aggro propagation range 2000uu, time limit 0h7m.
2. Visit: Sorcha (437,1001). No count.
3. Visit: Jorhon (64,1006). No count.

Rewards: exp 6000, gold 600. No reward item rows.

### 1347: It Was a Rock...Crawler

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. HuntAndDeliver: monster 13,300542 (100% drop chance) and monster 13,300541 (17% drop chance), deliver 8 items total to Lorin (213,1128). Required count: 8.

Rewards: exp 900, gold 90, itemBag: class.

Reward item rows:

| templateId | qty | class |
|---|---|---|
| 17711 | 1 | lancer |
| 17711 | 1 | berserker |
| 17714 | 1 | warrior |
| 17714 | 1 | slayer |
| 17714 | 1 | archer |
| 17714 | 1 | glaiver |
| 17717 | 1 | sorcerer |
| 17717 | 1 | priest |
| 17717 | 1 | elementalist |
| 17717 | 1 | assassin |
| 17711 | 1 | engineer |
| 17711 | 1 | fighter |

### 1348: Ferocious Flowering Felons

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. HuntAndDeliver: monster 13,302 (90% drop chance) and monster 13,303 (17% drop chance), deliver 8 items total to Tanli (213,1147). Required count: 8.

Rewards: exp 900, gold 90, itemBag: allpay. No reward item rows returned despite the allpay bag declaration.

### 1349: Gotta Kill 'Em All

Category: Normal. Not repeatable. Cancellable.

Tasks (ordered):
1. Hunt: 6x monster 13,5 and 48x monster 13,4. Required counts: 6 and 48.
2. Visit: Ayrdoss (213,1126). No count.

Rewards: exp 2300, gold 230, itemBag: allpay. No reward item rows returned despite the allpay bag declaration.

### 1350: Strange Attractors

Category: Mission. storyGroupId 2. Not repeatable. Not cancellable (불가능).

Tasks (ordered):
1. HuntAndDeliver: monster 13,6 (95% drop chance), monster 13,300942 (5% drop chance), monster 13,7 (100% drop chance), deliver 5 items total to Sersine (213,1025). Required count: 5.

Rewards: exp 8400, gold 840. No reward item rows.

### 1351: Supply and Demand

Category: Normal. Not repeatable. Cancellable. Requirements line carries a class filter value (raw field: class=적용적용적용적용적용적용적용적용적용, 9 repeated units).

Tasks (ordered):
1. Visit: Rutgar (64,1005). No count.
2. Visit: Gurney (64,1007). No count.
3. Visit: Lilni (64,1048). No count.

Rewards: exp 800, gold 80, itemBag: allpay.

Reward item rows:

| templateId | qty | class |
|---|---|---|
| 6048 | 3 | (any) |

### 1352: Supply and Demand

Category: Normal. Not repeatable. Cancellable. Requirements line carries a class filter value (raw field: class=적용적용적용, 3 repeated units), same title and same prerequisite as 1351 but a different class filter count and a different task 2 target (Charise instead of Gurney).

Tasks (ordered):
1. Visit: Rutgar (64,1005). No count.
2. Visit: Charise (64,1008). No count.
3. Visit: Lilni (64,1048). No count.

Rewards: exp 800, gold 80, itemBag: allpay.

Reward item rows:

| templateId | qty | class |
|---|---|---|
| 6048 | 3 | (any) |

## Section 3: Item Name Lookup

| templateId | name | level | rareGrade | type |
|---|---|---|---|---|
| 6048 | Healing Elixir I | 1 | 0 | combat (DISPOSAL) |
| 7100 | Onslaught Charm I | 1 | 0 | charm (DISPOSAL) |
| 7104 | Ethereal Charm I | 1 | 0 | charm (DISPOSAL) |
| 7108 | Sanguine Charm I | 1 | 0 | charm (DISPOSAL) |
| 8007 | Speed Potion | 1 | 1 | combat (DISPOSAL) |
| 17711 | Rockhound Gauntlets | 6 | 0 | handMail (EQUIP_ARMOR_ARM); requiredClass LANCER;BERSERKER;ENGINEER;FIGHTER |
| 17714 | Rockhound Gloves | 6 | 0 | handLeather (EQUIP_ARMOR_ARM); requiredClass WARRIOR;SLAYER;ARCHER;GLAIVER;SOULLESS |
| 17717 | Rockhound Handwraps | 6 | 0 | handRobe (EQUIP_ARMOR_ARM); requiredClass SORCERER;PRIEST;ELEMENTALIST;ASSASSIN |

## Section 4: Missing IDs

- 1342: no quest body exists at this id. `lookup_quest` returns not found. `lookup_quest_rewards` returns a message that the id is registered in the reward/compensation table but defines no compensation (empty reward stub). This is the only missing id in the 1336 through 1352 range.
