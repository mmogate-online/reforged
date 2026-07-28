# Quest Reward Ledger: IDs 1318 to 1335

Source: datasheet-v92 (current server state). Range covers quest ids 1318 through 1335 inclusive (18 ids).

## 1. Quest Summary Table

| id | title | category | level | storyGroup | enabled | giver | prerequisites | exp | gold | reward item rows |
|---|---|---|---|---|---|---|---|---|---|---|
| 1318 | Hunting the Beasts | Normal | rec 2 (min 2) | none | live | Dulari (213,1017) | 1322 | 1500 | 150 | 0 |
| 1319 | Dwellers of the Island | Normal | rec 3 (min 2) | none | live | Clovis (213,1110) | none | 600 | 60 | 12 |
| 1320 | (not found) | | | | | | | | | |
| 1321 | A Bridge Pretty Near | Normal | rec 1 (min 1) | none | live | Barsabba (213,1106) | none | 800 | 80 | 0 |
| 1322 | Unrest in the Forest | Normal | rec 1 (min 1) | none | live | Kishale (213,1003) | none | 500 | 50 | 12 |
| 1323 | Getting Some Answers | Normal | rec 1 (min 1) | none | live | Kishale (213,1003) | 1322 | 800 | 80 | 12 |
| 1324 | Essence and Sensibility | Normal | rec 3 (min 2) | none | live | Dulari (213,1017) | 1323 | 900 | 90 | 0 |
| 1325 | The Perfect Cut | Normal | rec 3 (min 3) | none | live | Leolin (213,1121) | none | 500 | 50 | 12 |
| 1326 | Mana out of Mudmen | Normal | rec 5 (min 5) | none | live | Jirash (64,1023) | none (requires quest 1305 task 1 in progress) | 2000 | 200 | 12 |
| 1327 | Garrison in Distress | Normal | rec 4 (min 4) | none | live | Dulari (213,1017) | 1324 | 800 | 80 | 0 |
| 1328 | Academic Theft | Normal | rec 4 (min 4) | none | live | Adria (64,1001) | 1386 (outside range) | 1500 | 150 | 0 |
| 1329 | Going Above and Beyond | Mission | rec 4 (min 4) | 1 | live | Jorhon (64,1006) | 1303 (outside range) | 400 | 10 | 2 |
| 1330 | Horned Horrors | Normal | rec 5 (min 5) | none | live | Taras (64,1028) | none (requires quest 1305 task 1 in progress) | 1900 | 190 | 12 |
| 1331 | Climbing through the Ranks | Mission | rec 5 (min 5) | 1 | live | Lilni (64,1048) | 1382 OR 1383 (outside range) | 2300 | 230 | 12 |
| 1332 | They'll Eat Anything | Normal | rec 7 (min 6) | none | live | Kamarnu (213,1009) | none | 900 | 90 | 0 |
| 1333 | Twice the Bark, Twice the Bite | Normal | rec 7 (min 6) | none | live | Jehan (213,1130) | 1332 | 1700 | 170 | 0 |
| 1334 | Investigating the Relics (repeatable) | Normal | rec 7 (min 6, max 10) | none | live | Eria (213,1021) | none | 800 | 80 | 0 |
| 1335 | One of Our Couriers Is Missing | Normal | rec 8 (min 8) | none | live | Adria (64,1001) | 1309 (outside range) | 600 | 60 | 0 |

Notes on the table: "reward item rows" is the raw row count returned by lookup_quest_rewards (class variant rows counted individually, not deduplicated by templateId). Quests 1324, 1327, 1332, and 1333 report itemBag type "allpay" but returned zero item rows; see Section 4 anomaly note.

## 2. Per-Quest Detail

### 1318: Hunting the Beasts
Category Normal, recommended level 2, giver Dulari (213,1017), prerequisite quest 1322 (Unrest in the Forest).

Tasks (ordered):
1. HuntAndDeliver: monster 13,300921 (drop probability 100), deliver count 5, deliver to NPC 213,1004

Rewards: exp 1500, gold 150, no item rows.

### 1319: Dwellers of the Island
Category Normal, recommended level 3 (min 2), giver Clovis (213,1110), no prerequisite.

Tasks (ordered):
1. HuntAndDeliver: monster 13,300944 (probability 85) or monster 13,300941 (probability 12), deliver count 5, deliver to NPC 213,1110

Rewards: exp 600, gold 60, itemBag type class. Items (12 rows, one per class):
| templateId | name | qty | class |
|---|---|---|---|
| 12401 | Recycle & Reuse | 1 | warrior |
| 12402 | Repurposed Pronewood | 1 | lancer |
| 12403 | Self-propelled Mower | 1 | slayer |
| 12404 | Logsplitter | 1 | berserker |
| 12405 | Whirlwisp | 1 | sorcerer |
| 12407 | Burled Staff | 1 | priest |
| 12406 | Gnarled Messenger | 1 | archer |
| 12408 | Root of Evil | 1 | elementalist |
| 55305 | Graze Gun | 1 | engineer |
| 82006 | Knuckledusters | 1 | fighter |
| 58172 | Morning Glory | 1 | assassin |
| 59353 | Orcharn | 1 | glaiver |

### 1321: A Bridge Pretty Near
Category Normal, recommended level 1, giver Barsabba (213,1106), no prerequisite.

Tasks (ordered):
1. Visit: Kishale (213,1003)

Rewards: exp 800, gold 80, no item rows.

### 1322: Unrest in the Forest
Category Normal, recommended level 1, giver Kishale (213,1003), no prerequisite.

Tasks (ordered):
1. Hunt: monster 13,300931, kill count 5
2. Visit: Kishale (213,1003)

Rewards: exp 500, gold 50, itemBag type class. Items (12 rows, one per class):
| templateId | name | qty | class |
|---|---|---|---|
| 17703 | Tree Trimmer's Treads | 1 | lancer |
| 17703 | Tree Trimmer's Treads | 1 | berserker |
| 17706 | Tree Trimmer's Workboots | 1 | warrior |
| 17706 | Tree Trimmer's Workboots | 1 | slayer |
| 17706 | Tree Trimmer's Workboots | 1 | archer |
| 17706 | Tree Trimmer's Workboots | 1 | glaiver |
| 17709 | Tree Trimmer's Workshoes | 1 | sorcerer |
| 17709 | Tree Trimmer's Workshoes | 1 | priest |
| 17709 | Tree Trimmer's Workshoes | 1 | elementalist |
| 17709 | Tree Trimmer's Workshoes | 1 | assassin |
| 17703 | Tree Trimmer's Treads | 1 | engineer |
| 17703 | Tree Trimmer's Treads | 1 | fighter |

### 1323: Getting Some Answers
Category Normal, recommended level 1, giver Kishale (213,1003), prerequisite quest 1322 (Unrest in the Forest).

Tasks (ordered):
1. HuntAndDeliver: monster 13,300931 (probability 100), deliver count 5, deliver to NPC 213,1017

Rewards: exp 800, gold 80, itemBag type class. Items (12 rows, one per class):
| templateId | name | qty | class |
|---|---|---|---|
| 10009 | Rise & Shine | 1 | warrior |
| 10010 | Dawnbreaker | 1 | lancer |
| 10011 | Mourninglory | 1 | slayer |
| 10012 | Rude Awakening | 1 | berserker |
| 10013 | Parhelion | 1 | sorcerer |
| 10014 | Dayspring | 1 | archer |
| 10015 | Brightstaff | 1 | priest |
| 10016 | Sunbeam | 1 | elementalist |
| 55006 | Daybite | 1 | engineer |
| 82006 | Knuckledusters | 1 | fighter |
| 58172 | Morning Glory | 1 | assassin |
| 59054 | Sunstroke | 1 | glaiver |

### 1324: Essence and Sensibility
Category Normal, recommended level 3 (min 2), giver Dulari (213,1017), prerequisite quest 1323 (Getting Some Answers).

Tasks (ordered):
1. HuntAndDeliver: monster 13,300930 (probability 100) or monster 13,300933 (probability 85), deliver count 5, deliver to NPC 213,1017

Rewards: exp 900, gold 90, itemBag type allpay, 0 item rows returned.

### 1325: The Perfect Cut
Category Normal, recommended level 3, giver Leolin (213,1121), no prerequisite.

Tasks (ordered):
1. HuntAndDeliver: monster 13,1 (probability 30), deliver count 5, deliver to NPC 213,1121

Rewards: exp 500, gold 50, itemBag type class. Items (12 rows, one per class):
| templateId | name | qty | class |
|---|---|---|---|
| 17702 | Swineherd's Gauntlets | 1 | lancer |
| 17702 | Swineherd's Gauntlets | 1 | berserker |
| 17705 | Swineherd's Gloves | 1 | warrior |
| 17705 | Swineherd's Gloves | 1 | slayer |
| 17705 | Swineherd's Gloves | 1 | archer |
| 17705 | Swineherd's Gloves | 1 | glaiver |
| 17708 | Swineherd's Wraps | 1 | sorcerer |
| 17708 | Swineherd's Wraps | 1 | priest |
| 17708 | Swineherd's Wraps | 1 | elementalist |
| 17708 | Swineherd's Wraps | 1 | assassin |
| 17702 | Swineherd's Gauntlets | 1 | engineer |
| 17702 | Swineherd's Gauntlets | 1 | fighter |

### 1326: Mana out of Mudmen
Category Normal, recommended level 5, giver Jirash (64,1023), no formal prerequisite quest (requires quest 1305 task 1 in progress).

Tasks (ordered):
1. HuntAndDeliver: monster 13,2 (probability 90), deliver count 5, deliver to NPC 64,1023

Rewards: exp 2000, gold 200, itemBag type class. Items (12 rows, one per class):
| templateId | name | qty | class |
|---|---|---|---|
| 15021 | Greaves of the First Expedition | 1 | lancer |
| 15021 | Greaves of the First Expedition | 1 | berserker |
| 15024 | Boots of the First Expedition | 1 | warrior |
| 15024 | Boots of the First Expedition | 1 | slayer |
| 15024 | Boots of the First Expedition | 1 | archer |
| 15024 | Boots of the First Expedition | 1 | glaiver |
| 15027 | Shoes of the First Expedition | 1 | sorcerer |
| 15027 | Shoes of the First Expedition | 1 | priest |
| 15027 | Shoes of the First Expedition | 1 | elementalist |
| 15027 | Shoes of the First Expedition | 1 | assassin |
| 15021 | Greaves of the First Expedition | 1 | engineer |
| 15021 | Greaves of the First Expedition | 1 | fighter |

### 1327: Garrison in Distress
Category Normal, recommended level 4, giver Dulari (213,1017), prerequisite quest 1324 (Essence and Sensibility).

Tasks (ordered):
1. Visit: Ramun (213,1038)
2. Visit: Neziir (213,1004)
3. HuntAndDeliver: monster 13,300921 (probability 100), deliver count 5, deliver to NPC 213,1119

Rewards: exp 800, gold 80, itemBag type allpay, 0 item rows returned.

### 1328: Academic Theft
Category Normal, recommended level 4, giver Adria (64,1001), prerequisite quest 1386 (Bombs Away, outside range).

Tasks (ordered):
1. HuntAndDeliver: monster 13,301194 (probability 90), monster 13,301191 (probability 12), or monster 13,301193 (probability 12), deliver count 5, deliver to NPC 64,1042

Rewards: exp 1500, gold 150, no item rows.

### 1329: Going Above and Beyond
Category Mission, storyGroup 1, recommended level 4, giver Jorhon (64,1006), prerequisite quest 1303 (The Secret Life of Trees, outside range), cancellable: no.

Tasks (ordered):
1. Visit: Kiriya (64,1029), grants item 5002 x1 on completion
2. Hunt: monster 13,888, kill count 3
3. Visit: Kiriya (64,1029), removes item 5002 x1 on completion

Rewards: exp 400, gold 10, itemBag type allpay. Items:
| templateId | name | qty | class |
|---|---|---|---|
| 8007 | Speed Potion | 3 | (none, all classes) |
| 7200 | Bomb I | 10 | (none, all classes) |

### 1330: Horned Horrors
Category Normal, recommended level 5, giver Taras (64,1028), no formal prerequisite quest (requires quest 1305 task 1 in progress).

Tasks (ordered):
1. Hunt: monster 13,300932, kill count 5
2. Visit: Taras (64,1028)

Rewards: exp 1900, gold 190, itemBag type class. Items (12 rows, one per class):
| templateId | name | qty | class |
|---|---|---|---|
| 15020 | Gauntlets of the First Expedition | 1 | lancer |
| 15020 | Gauntlets of the First Expedition | 1 | berserker |
| 15023 | Gloves of the First Expedition | 1 | warrior |
| 15023 | Gloves of the First Expedition | 1 | slayer |
| 15023 | Gloves of the First Expedition | 1 | archer |
| 15023 | Gloves of the First Expedition | 1 | glaiver |
| 15026 | Sleeves of the First Expedition | 1 | sorcerer |
| 15026 | Sleeves of the First Expedition | 1 | priest |
| 15026 | Sleeves of the First Expedition | 1 | elementalist |
| 15026 | Sleeves of the First Expedition | 1 | assassin |
| 15020 | Gauntlets of the First Expedition | 1 | engineer |
| 15020 | Gauntlets of the First Expedition | 1 | fighter |

### 1331: Climbing through the Ranks
Category Mission, storyGroup 1, recommended level 5, giver Lilni (64,1048), prerequisite quest 1382 OR 1383 (both titled Gathering Your Strength, outside range, prerequisiteLogic OR), cancellable: no.

Tasks (ordered):
1. Visit: Gyebrik (64,1024), grants item 200001 x3 on completion
2. HuntAndDeliver: monster 13,301194 (probability 90), monster 13,301191 (probability 12), or monster 13,301193 (probability 12), deliver count 5, deliver to NPC 213,1053
3. MoveToPC: target region 213,21300007
4. CollectionComplete: collection id 492, target item 9095 x1
5. Visit: Jorhon (64,1006), removes item 9095 x1 on completion

Rewards: exp 2300, gold 230, itemBag type class. Items (12 rows, one per class):
| templateId | name | qty | class |
|---|---|---|---|
| 17710 | Hauberk of Family Ties | 1 | lancer |
| 17710 | Hauberk of Family Ties | 1 | berserker |
| 17713 | Cuirass of Family Ties | 1 | warrior |
| 17713 | Cuirass of Family Ties | 1 | slayer |
| 17713 | Cuirass of Family Ties | 1 | archer |
| 17713 | Cuirass of Family Ties | 1 | glaiver |
| 17716 | Robes of Family Ties | 1 | sorcerer |
| 17716 | Robes of Family Ties | 1 | priest |
| 17716 | Robes of Family Ties | 1 | elementalist |
| 17716 | Robes of Family Ties | 1 | assassin |
| 17710 | Hauberk of Family Ties | 1 | engineer |
| 17710 | Hauberk of Family Ties | 1 | fighter |

### 1332: They'll Eat Anything
Category Normal, recommended level 7 (min 6), giver Kamarnu (213,1009), no prerequisite.

Tasks (ordered):
1. HuntAndDeliver: monster 13,300920 (probability 100), deliver count 4, deliver to NPC 213,1130

Rewards: exp 900, gold 90, itemBag type allpay, 0 item rows returned.

### 1333: Twice the Bark, Twice the Bite
Category Normal, recommended level 7 (min 6), giver Jehan (213,1130), prerequisite quest 1332 (They'll Eat Anything).

Tasks (ordered):
1. HuntAndDeliver: monster 13,300911 (probability 90), deliver count 6, deliver to NPC 213,1130

Rewards: exp 1700, gold 170, itemBag type allpay, 0 item rows returned.

### 1334: Investigating the Relics (repeatable)
Category Normal, recommended level 7 (min 6, max 10), giver Eria (213,1021), no prerequisite. Requirements include maxLevel 10.

Tasks (ordered):
1. Collect: collection id 410, deliver item 9011 x5, deliver to NPC 213,1021

Rewards: exp 800, gold 80, no item rows.

### 1335: One of Our Couriers Is Missing
Category Normal, recommended level 8, giver Adria (64,1001), prerequisite quest 1309 (Acharak Attacks, outside range).

Tasks (ordered):
1. Visit: Kerson (64,1003)
2. Visit: Chione (213,1007)

Rewards: exp 600, gold 60, no item rows.

## 3. Item Name Lookup Table

Every distinct reward templateId encountered above, resolved via batch_lookup (entityType Item). Name is the item's displayName field; level and grade/rarity are the level and rareGrade attributes; type is combatItemType/combatItemSubType.

| templateId | name | level | grade/rarity | type |
|---|---|---|---|---|
| 12401 | Recycle & Reuse | 3 | 0 | EQUIP_WEAPON, dual |
| 12402 | Repurposed Pronewood | 3 | 0 | EQUIP_WEAPON, lance |
| 12403 | Self-propelled Mower | 3 | 0 | EQUIP_WEAPON, twohand |
| 12404 | Logsplitter | 3 | 0 | EQUIP_WEAPON, axe |
| 12405 | Whirlwisp | 3 | 0 | EQUIP_WEAPON, circle |
| 12406 | Gnarled Messenger | 3 | 0 | EQUIP_WEAPON, bow |
| 12407 | Burled Staff | 3 | 0 | EQUIP_WEAPON, staff |
| 12408 | Root of Evil | 3 | 0 | EQUIP_WEAPON, rod |
| 55305 | Graze Gun | 3 | 0 | EQUIP_WEAPON, blaster |
| 82006 | Knuckledusters | 2 | 0 | EQUIP_WEAPON, gauntlet |
| 58172 | Morning Glory | 2 | 0 | EQUIP_WEAPON, shuriken |
| 59353 | Orcharn | 3 | 0 | EQUIP_WEAPON, glaive |
| 17703 | Tree Trimmer's Treads | 3 | 0 | EQUIP_ARMOR_LEG, feetMail |
| 17706 | Tree Trimmer's Workboots | 3 | 0 | EQUIP_ARMOR_LEG, feetLeather |
| 17709 | Tree Trimmer's Workshoes | 3 | 0 | EQUIP_ARMOR_LEG, feetRobe |
| 10009 | Rise & Shine | 2 | 0 | EQUIP_WEAPON, dual |
| 10010 | Dawnbreaker | 2 | 0 | EQUIP_WEAPON, lance |
| 10011 | Mourninglory | 2 | 0 | EQUIP_WEAPON, twohand |
| 10012 | Rude Awakening | 2 | 0 | EQUIP_WEAPON, axe |
| 10013 | Parhelion | 2 | 0 | EQUIP_WEAPON, circle |
| 10014 | Dayspring | 2 | 0 | EQUIP_WEAPON, bow |
| 10015 | Brightstaff | 2 | 0 | EQUIP_WEAPON, staff |
| 10016 | Sunbeam | 2 | 0 | EQUIP_WEAPON, rod |
| 55006 | Daybite | 2 | 0 | EQUIP_WEAPON, blaster |
| 17702 | Swineherd's Gauntlets | 3 | 0 | EQUIP_ARMOR_ARM, handMail |
| 17705 | Swineherd's Gloves | 3 | 0 | EQUIP_ARMOR_ARM, handLeather |
| 17708 | Swineherd's Wraps | 3 | 0 | EQUIP_ARMOR_ARM, handRobe |
| 15021 | Greaves of the First Expedition | 7 | 0 | EQUIP_ARMOR_LEG, feetMail |
| 15024 | Boots of the First Expedition | 7 | 0 | EQUIP_ARMOR_LEG, feetLeather |
| 15027 | Shoes of the First Expedition | 7 | 0 | EQUIP_ARMOR_LEG, feetRobe |
| 8007 | Speed Potion | 1 | 1 | DISPOSAL, combat |
| 7200 | Bomb I | 1 | 0 | DISPOSAL, combat |
| 15020 | Gauntlets of the First Expedition | 7 | 0 | EQUIP_ARMOR_ARM, handMail |
| 15023 | Gloves of the First Expedition | 7 | 0 | EQUIP_ARMOR_ARM, handLeather |
| 15026 | Sleeves of the First Expedition | 7 | 0 | EQUIP_ARMOR_ARM, handRobe |
| 17710 | Hauberk of Family Ties | 5 | 0 | EQUIP_ARMOR_BODY, bodyMail |
| 17713 | Cuirass of Family Ties | 5 | 0 | EQUIP_ARMOR_BODY, bodyLeather |
| 17716 | Robes of Family Ties | 5 | 0 | EQUIP_ARMOR_BODY, bodyRobe |
| 59054 | Sunstroke | 2 | 0 | EQUIP_WEAPON, glaive |

## 4. Missing IDs

| id | status |
|---|---|
| 1320 | not found (no quest record at this id) |

Anomaly note: quests 1324, 1327, 1332, and 1333 report itemBag type "allpay" in lookup_quest_rewards but returned zero item rows. This pattern (bag type set, no item rows) recurs across four ids in this range and is recorded here as observed, without further interpretation.
