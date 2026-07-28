# Quest Reward Ledger: IDs 1301 to 1317

Source: datasheet-v92 (current server state), tools lookup_quest, lookup_quest_rewards, batch_lookup (entityType Item, entityType ItemString).

Scope: quest ids 1301 through 1317 inclusive (17 ids). Id 1314 does not exist and is listed under Missing ids.

## Section 1: Quest summary table

| id | title | category | level (rec/min) | storyGroup | enabled | giver | prerequisites | exp | gold | reward item count |
|---|---|---|---|---|---|---|---|---|---|---|
| 1301 | Dawn's Twilight | Mission | 1/1 | 1 | yes | Axelle (213,1105) | none | 500 | 50 | 0 |
| 1302 | Another Fine Mess | Normal | 1/1 | none | yes | Lam (213,1014) | none | 400 | 40 | 0 |
| 1303 | The Secret Life of Trees | Mission | 4/3 | 1 | yes | Nivek (213,1115) | 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1387 (OR logic) | 2600 | 260 | 24 |
| 1304 | Making the Rounds | Mission | 1/1 | 1 | yes | Lam (213,1014) | 1301 | 800 | 80 | 12 |
| 1305 | A Clue in the Dark | Mission | 6/5 | 1 | yes | Adria (64,1001) | 1331 | 4900 | 490 | 48 |
| 1306 | Traces of Darkness | Normal | 7/6 | none | no (sentinel prerequisite 9999) | Leander (213,1008) | 9999 (Unavailable Quest) | 800 | 80 | 0 |
| 1307 | Live by the Sword | Normal | 8/7 | none | no (sentinel prerequisite 9999) | Leander (213,1008) | 9999 (Unavailable Quest) | 1000 | 100 | 1 |
| 1308 | Essence of Foreboding | Normal | 8/7 | none | no (sentinel prerequisite 9999) | Eria (213,1021) | 9999 (Unavailable Quest) | 1000 | 100 | 0 |
| 1309 | Acharak Attacks | Mission | 8/7 | 2 | yes | Chione (213,1007) | 1311 | 3200 | 320 | 0 |
| 1310 | A Clue in the Dark | Normal | 8/7 | none | no (sentinel prerequisite 9999) | Leander (213,1008) | 9999 (Unavailable Quest) | 1000 | 100 | 24 |
| 1311 | Redeployment | Mission | 7/7 | 2 | yes | Teil (64,1009) | 1305 | 3600 | 360 | 0 |
| 1312 | The Dark Patrol | Normal | 8/8 | none | yes | Edan (213,1134) | 1311 | 2500 | 250 | 0 |
| 1313 | Into the Gorge | Mission | 8/7 | 2 | yes | Edan (213,1134) | 1309 | 6840 | 470 | 3 |
| 1314 | (missing) | | | | | | | | | |
| 1315 | Putting the Pieces Together | Mission | 9/9 | 2 | yes | Sersine (213,1025) | 1350 | 4500 | 450 | 24 |
| 1316 | Dark Revelations | Mission | 9/9 | 2 | yes | Sersine (213,1025) | 1315 | 14600 | 1460 | 12 |
| 1317 | Ride Off into the Sunset | Mission | 10/10 | 2 | yes | Adria (64,1001) | 1316 | 2000 | 200 | 12 |

Level column format: recommendedLevel / minLevel (from the quest Requirements block). No maxLevel attribute is present in the source data for any of these quests.

## Section 2: Per-quest detail

### 1301: Dawn's Twilight

Giver: Axelle (213,1105). Prerequisites: none.

Tasks (ordered):
1. Visit: Lam (213,1014), count 1 (reward task)

Rewards: exp 500, gold 50. No reward items.

### 1302: Another Fine Mess

Giver: Lam (213,1014). Prerequisites: none.

Tasks (ordered):
1. Visit: Barsabba (213,1106), count 1 (reward task)

Rewards: exp 400, gold 40. No reward items.

### 1303: The Secret Life of Trees

Giver: Nivek (213,1115). Prerequisites (OR logic): 1371 Warrior Training, 1372 Lancer Training, 1373 Slayer Training, 1374 Berserker Training, 1375 Archer Training, 1376 Sorcerer Training, 1377 Priest Training, 1378 Mystic Training, 1379 Gunner Training, 1380 Ninja Training, 1381 Brawler Training, 1387 Valkyrie Training.

Tasks (ordered):
1. PlayMovie: video 1
2. Hunt: monster 13,1001, count 1
3. Visit: Nivek (213,1115), count 1
4. Visit: Neziir (213,1004), count 1
5. Visit: Adria (64,1001), count 1 (reward task)

Rewards: exp 2600, gold 260, itemBag: class. 24 item rows:

| templateId | name | qty | class |
|---|---|---|---|
| 12129 | Thorn & Bloom | 1 | warrior |
| 12130 | Bole of Vekas | 1 | lancer |
| 12131 | Blade of Vekas | 1 | slayer |
| 12132 | Bane of Vekas | 1 | berserker |
| 12133 | Heart of Vekas | 1 | sorcerer |
| 12134 | Bough of Vekas | 1 | archer |
| 12135 | Branch of Vekas | 1 | priest |
| 12136 | Taproot of Vekas | 1 | elementalist |
| 55271 | Boomstick of Vekas | 1 | engineer |
| 17404 | Bark of Vekas | 1 | lancer |
| 17404 | Bark of Vekas | 1 | berserker |
| 17407 | Treejack's Jacket | 1 | warrior |
| 17407 | Treejack's Jacket | 1 | slayer |
| 17407 | Treejack's Jacket | 1 | archer |
| 17407 | Treejack's Jacket | 1 | glaiver |
| 17410 | Tannen-tint Robes | 1 | sorcerer |
| 17410 | Tannen-tint Robes | 1 | priest |
| 17410 | Tannen-tint Robes | 1 | elementalist |
| 17410 | Tannen-tint Robes | 1 | assassin |
| 17404 | Bark of Vekas | 1 | engineer |
| 17404 | Bark of Vekas | 1 | fighter |
| 82006 | Knuckledusters | 1 | fighter |
| 58172 | Morning Glory | 1 | assassin |
| 59353 | Orcharn | 1 | glaiver |

### 1304: Making the Rounds

Giver: Lam (213,1014). Prerequisites: 1301 Dawn's Twilight.

Tasks (ordered):
1. Visit: Kishale (213,1003), count 1
2. HuntAndDeliver: monster 13,300931, deliver count 5, turn in to NPC 213,1017 (reward task)

Rewards: exp 800, gold 80, itemBag: class. 12 item rows:

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

### 1305: A Clue in the Dark

Giver: Adria (64,1001). Prerequisites: 1331 Climbing through the Ranks.

Tasks (ordered):
1. Visit: Leander (213,1008), count 1
2. Visit: Taras (64,1028), count 1
3. Hunt: monster 13,300932, count 5
4. Visit: Tanli (213,1147), count 1
5. Hunt: monster 13,2, count 5
6. DeliverInjectedItem: to Leander (213,1008), count 1
7. Visit: Teil (64,1009), count 1 (reward task)

Rewards: exp 4900, gold 490, itemBag: class. 48 item rows:

| templateId | name | qty | class |
|---|---|---|---|
| 10017 | Twin Swords of the First Expedition | 1 | warrior |
| 10018 | Lance of the First Expedition | 1 | lancer |
| 10019 | Greatsword of the First Expedition | 1 | slayer |
| 10020 | Axe of the First Expedition | 1 | berserker |
| 10021 | Disc of the First Expedition | 1 | sorcerer |
| 10022 | Bow of the First Expedition | 1 | archer |
| 10023 | Staff of the First Expedition | 1 | priest |
| 10024 | Scepter of the First Expedition | 1 | elementalist |
| 55007 | Arcannon of the First Expedition | 1 | engineer |
| 15019 | Hauberk of the First Expedition | 1 | lancer |
| 15019 | Hauberk of the First Expedition | 1 | berserker |
| 15022 | Cuirass of the First Expedition | 1 | warrior |
| 15022 | Cuirass of the First Expedition | 1 | slayer |
| 15022 | Cuirass of the First Expedition | 1 | archer |
| 15022 | Cuirass of the First Expedition | 1 | glaiver |
| 15025 | Robe of the First Expedition | 1 | sorcerer |
| 15025 | Robe of the First Expedition | 1 | priest |
| 15025 | Robe of the First Expedition | 1 | elementalist |
| 15025 | Robe of the First Expedition | 1 | assassin |
| 15019 | Hauberk of the First Expedition | 1 | engineer |
| 15019 | Hauberk of the First Expedition | 1 | fighter |
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
| 82007 | Powerfists of the First Expedition | 1 | fighter |
| 58173 | Shuriken of the First Expedition | 1 | assassin |
| 59055 | Runeglaive of the First Expedition | 1 | glaiver |

### 1306: Traces of Darkness (disabled)

Giver: Leander (213,1008). Prerequisites: 9999 (Unavailable Quest, sentinel). State: disabled.

Tasks (ordered):
1. DeliverInjectedItem: to Eria (213,1021), count 1
2. Visit: Leander (213,1008), count 1
3. MoveToPC: target region 213,21300020
4. PlayMovie: video 2
5. Visit: Leander (213,1036), count 1
6. DeliverInjectedItem: to Eria (213,1021), count 1 (reward task)

Rewards: exp 800, gold 80. No reward items.

### 1307: Live by the Sword (disabled)

Giver: Leander (213,1008). Prerequisites: 9999 (Unavailable Quest, sentinel). State: disabled.

Tasks (ordered):
1. Visit: Kirash (213,1027), count 1
2. HuntAndDeliver: monster 13,601, deliver count 1, turn in to NPC 213,1027
3. Visit: Leander (213,1008), count 1 (reward task)

Rewards: exp 1000, gold 100, itemBag: allpay. 1 item row:

| templateId | name | qty | class |
|---|---|---|---|
| 8200 | Slaying Rhomb | 1 | (all classes) |

### 1308: Essence of Foreboding (disabled)

Giver: Eria (213,1021). Prerequisites: 9999 (Unavailable Quest, sentinel). State: disabled.

Tasks (ordered):
1. HuntAndDeliver: monster 13,3, deliver count 6, turn in to NPC 213,1021
2. Visit: Leander (213,1008), count 1 (reward task)

Rewards: exp 1000, gold 100. No reward items.

### 1309: Acharak Attacks

Giver: Chione (213,1007). Prerequisites: 1311 Redeployment.

Tasks (ordered):
1. Hunt: monster 13,1002, count 1 (task body includes encounter and death dialog references)
2. DeliverInjectedItem: to Edan (213,1134), count 1 (reward task)

Rewards: exp 3200, gold 320. No reward items.

### 1310: A Clue in the Dark (disabled)

Giver: Leander (213,1008). Prerequisites: 9999 (Unavailable Quest, sentinel). State: disabled. Note: same title as live quest 1305.

Tasks (ordered):
1. Visit: Jehan (213,1130), count 1
2. DeliverInjectedItem: to Adria (64,1001), count 1
3. Visit: Teil (64,1009), count 1 (reward task)

Rewards: exp 1000, gold 100, itemBag: class. 24 item rows:

| templateId | name | qty | class |
|---|---|---|---|
| 10017 | Twin Swords of the First Expedition | 1 | warrior |
| 10018 | Lance of the First Expedition | 1 | lancer |
| 10019 | Greatsword of the First Expedition | 1 | slayer |
| 10020 | Axe of the First Expedition | 1 | berserker |
| 10021 | Disc of the First Expedition | 1 | sorcerer |
| 10022 | Bow of the First Expedition | 1 | archer |
| 10023 | Staff of the First Expedition | 1 | priest |
| 10024 | Scepter of the First Expedition | 1 | elementalist |
| 55007 | Arcannon of the First Expedition | 1 | engineer |
| 15019 | Hauberk of the First Expedition | 1 | lancer |
| 15019 | Hauberk of the First Expedition | 1 | berserker |
| 15022 | Cuirass of the First Expedition | 1 | warrior |
| 15022 | Cuirass of the First Expedition | 1 | slayer |
| 15022 | Cuirass of the First Expedition | 1 | archer |
| 15022 | Cuirass of the First Expedition | 1 | glaiver |
| 15025 | Robe of the First Expedition | 1 | sorcerer |
| 15025 | Robe of the First Expedition | 1 | priest |
| 15025 | Robe of the First Expedition | 1 | elementalist |
| 15025 | Robe of the First Expedition | 1 | assassin |
| 15019 | Hauberk of the First Expedition | 1 | engineer |
| 15019 | Hauberk of the First Expedition | 1 | fighter |
| 82007 | Powerfists of the First Expedition | 1 | fighter |
| 58173 | Shuriken of the First Expedition | 1 | assassin |
| 59055 | Runeglaive of the First Expedition | 1 | glaiver |

### 1311: Redeployment

Giver: Teil (64,1009), immediate trigger on NPC dialog. Prerequisites: 1305 A Clue in the Dark.

Tasks (ordered):
1. Visit: Bipi (64,1033), count 1
2. Hunt: monster 13,901, count 5
3. Collect: collection 409, item 9010, deliver count 5, turn in to Chione (213,1007) (reward task)

Rewards: exp 3600, gold 360. No reward items.

### 1312: The Dark Patrol

Giver: Edan (213,1134). Prerequisites: 1311 Redeployment.

Tasks (ordered):
1. Hunt: monster 13,300910, count 5
2. Visit: Sersine (213,1025), count 1 (reward task)

Rewards: exp 2500, gold 250. No reward items.

### 1313: Into the Gorge

Giver: Edan (213,1134). Prerequisites: 1309 Acharak Attacks.

Tasks (ordered):
1. Hunt: monster 13,300910, count 5
2. MoveToPC: target region 213,21300011
3. Visit: Phaedra (213,1005), count 1
4. GroupHunt: monster 13,300951 or monster 13,300960, count 5 (public quest flag false)
5. Collect: collection 411, item 9012, deliver count 5, turn in to Sersine (213,1025) (reward task)

Rewards: exp 6840, gold 470, itemBag: not specified (class column empty on all rows). 3 item rows:

| templateId | name | qty | class |
|---|---|---|---|
| 7100 | Onslaught Charm I | 1 | (none) |
| 7104 | Ethereal Charm I | 1 | (none) |
| 7108 | Sanguine Charm I | 1 | (none) |

### 1314: missing

No quest exists at this id. See Section 4.

### 1315: Putting the Pieces Together

Giver: Sersine (213,1025). Prerequisites: 1350 Strange Attractors.

Tasks (ordered):
1. Hunt: monster 13,1004, count 1
2. DeliverInjectedItem: to Sersine (213,1025), count 1 (reward task)

Rewards: exp 4500, gold 450, itemBag: class. 24 item rows:

| templateId | name | qty | class |
|---|---|---|---|
| 12137 | Kugai's Left & Right | 1 | warrior |
| 12138 | Resistance of the Mighty | 1 | lancer |
| 12139 | Kugai's Greatsword | 1 | slayer |
| 12140 | Kugai's Axe | 1 | berserker |
| 12141 | Kugai's Disc | 1 | sorcerer |
| 12142 | Kugai's Bow | 1 | archer |
| 12143 | Kugai's Staff | 1 | priest |
| 12144 | Kugai's Scepter | 1 | elementalist |
| 55272 | Kugai's Arcannon | 1 | engineer |
| 17413 | Second-in-Command's Breastplate | 1 | lancer |
| 17413 | Second-in-Command's Breastplate | 1 | berserker |
| 17416 | Corruption-Covered Cuirass | 1 | warrior |
| 17416 | Corruption-Covered Cuirass | 1 | slayer |
| 17416 | Corruption-Covered Cuirass | 1 | archer |
| 17416 | Corruption-Covered Cuirass | 1 | glaiver |
| 17419 | Robes of Unnatural Order | 1 | sorcerer |
| 17419 | Robes of Unnatural Order | 1 | priest |
| 17419 | Robes of Unnatural Order | 1 | elementalist |
| 17419 | Robes of Unnatural Order | 1 | assassin |
| 17413 | Second-in-Command's Breastplate | 1 | engineer |
| 17413 | Second-in-Command's Breastplate | 1 | fighter |
| 82007 | Powerfists of the First Expedition | 1 | fighter |
| 58173 | Shuriken of the First Expedition | 1 | assassin |
| 59055 | Runeglaive of the First Expedition | 1 | glaiver |

### 1316: Dark Revelations

Giver: Sersine (213,1025). Prerequisites: 1315 Putting the Pieces Together.

Tasks (ordered):
1. GroupHunt: monster 13,9 or monster 13,8, count 8 (public quest flag false)
2. MoveToPC: target region 213,21300034
3. MoveToPC: target region 436,43600026
4. Hunt: monster 436,1002, count 1
5. PlayMovie: video 6
6. DeliverInjectedItem: to Sersine (213,1025), count 1
7. DeliverInjectedItem: to Leander (213,1037), count 1 (task also grants item 133 x1 on completion, outside the quest reward bag)
8. DeliverInjectedItem: to Adria (64,1001), count 1 (reward task)

Rewards: exp 14600, gold 1460, itemBag: class. 12 item rows:

| templateId | name | qty | class |
|---|---|---|---|
| 10593 | Disclose & Divulge | 1 | warrior |
| 10594 | Revelation Tree | 1 | lancer |
| 10595 | Incisive Greatsword | 1 | slayer |
| 10596 | Axe of Manifesto | 1 | berserker |
| 10597 | Darkseeing Lens | 1 | sorcerer |
| 10598 | Revealing Arc | 1 | archer |
| 10599 | Praesto Staff | 1 | priest |
| 10600 | Rod of Revelation | 1 | elementalist |
| 55079 | See Shooter | 1 | engineer |
| 82008 | Feyfists | 1 | fighter |
| 58174 | Copsebloom | 1 | assassin |
| 59056 | Gladeglaive | 1 | glaiver |

### 1317: Ride Off into the Sunset

Giver: Adria (64,1001). Prerequisites: 1316 Dark Revelations.

Tasks (ordered):
1. Visit: Teil (64,1009), count 1
2. Visit: Taleb (213,1001), count 1
3. Visit: Leiyane (213,1016), count 1 (reward task)

Rewards: exp 2000, gold 200, itemBag: class. 12 item rows:

| templateId | name | qty | class |
|---|---|---|---|
| 15667 | Outrider's Chestpiece | 1 | lancer |
| 15667 | Outrider's Chestpiece | 1 | berserker |
| 15670 | Sentry's Jerkin | 1 | warrior |
| 15670 | Sentry's Jerkin | 1 | slayer |
| 15670 | Sentry's Jerkin | 1 | archer |
| 15670 | Sentry's Jerkin | 1 | glaiver |
| 15673 | Outrider's Robes | 1 | sorcerer |
| 15673 | Outrider's Robes | 1 | priest |
| 15673 | Outrider's Robes | 1 | elementalist |
| 15673 | Outrider's Robes | 1 | assassin |
| 15667 | Outrider's Chestpiece | 1 | engineer |
| 15667 | Outrider's Chestpiece | 1 | fighter |

## Section 3: Item name lookup table

All distinct reward templateIds observed across quests 1301 through 1317, resolved via batch_lookup (entityType Item for level/rareGrade/category, entityType ItemString for the display name). rareGrade is the raw numeric value from the datasheet (values seen: 0, 1, 2); no rarity name mapping is stored in this entity.

| templateId | name | level | rareGrade | type (category) |
|---|---|---|---|---|
| 7100 | Onslaught Charm I | 1 | 0 | charm |
| 7104 | Ethereal Charm I | 1 | 0 | charm |
| 7108 | Sanguine Charm I | 1 | 0 | charm |
| 8200 | Slaying Rhomb | 1 | 0 | customize_weapon |
| 10009 | Rise & Shine | 2 | 0 | dual |
| 10010 | Dawnbreaker | 2 | 0 | lance |
| 10011 | Mourninglory | 2 | 0 | twohand |
| 10012 | Rude Awakening | 2 | 0 | axe |
| 10013 | Parhelion | 2 | 0 | circle |
| 10014 | Dayspring | 2 | 0 | bow |
| 10015 | Brightstaff | 2 | 0 | staff |
| 10016 | Sunbeam | 2 | 0 | rod |
| 10017 | Twin Swords of the First Expedition | 7 | 0 | dual |
| 10018 | Lance of the First Expedition | 7 | 0 | lance |
| 10019 | Greatsword of the First Expedition | 7 | 0 | twohand |
| 10020 | Axe of the First Expedition | 7 | 0 | axe |
| 10021 | Disc of the First Expedition | 7 | 0 | circle |
| 10022 | Bow of the First Expedition | 7 | 0 | bow |
| 10023 | Staff of the First Expedition | 7 | 0 | staff |
| 10024 | Scepter of the First Expedition | 7 | 0 | rod |
| 10593 | Disclose & Divulge | 11 | 2 | dual |
| 10594 | Revelation Tree | 11 | 2 | lance |
| 10595 | Incisive Greatsword | 11 | 2 | twohand |
| 10596 | Axe of Manifesto | 11 | 2 | axe |
| 10597 | Darkseeing Lens | 11 | 2 | circle |
| 10598 | Revealing Arc | 11 | 2 | bow |
| 10599 | Praesto Staff | 11 | 2 | staff |
| 10600 | Rod of Revelation | 11 | 2 | rod |
| 12129 | Thorn & Bloom | 4 | 0 | dual |
| 12130 | Bole of Vekas | 4 | 0 | lance |
| 12131 | Blade of Vekas | 4 | 0 | twohand |
| 12132 | Bane of Vekas | 4 | 0 | axe |
| 12133 | Heart of Vekas | 4 | 0 | circle |
| 12134 | Bough of Vekas | 4 | 0 | bow |
| 12135 | Branch of Vekas | 4 | 0 | staff |
| 12136 | Taproot of Vekas | 4 | 0 | rod |
| 12137 | Kugai's Left & Right | 8 | 2 | dual |
| 12138 | Resistance of the Mighty | 8 | 2 | lance |
| 12139 | Kugai's Greatsword | 8 | 2 | twohand |
| 12140 | Kugai's Axe | 8 | 2 | axe |
| 12141 | Kugai's Disc | 8 | 2 | circle |
| 12142 | Kugai's Bow | 8 | 2 | bow |
| 12143 | Kugai's Staff | 8 | 2 | staff |
| 12144 | Kugai's Scepter | 8 | 2 | rod |
| 15019 | Hauberk of the First Expedition | 7 | 0 | bodyMail |
| 15020 | Gauntlets of the First Expedition | 7 | 0 | handMail |
| 15021 | Greaves of the First Expedition | 7 | 0 | feetMail |
| 15022 | Cuirass of the First Expedition | 7 | 0 | bodyLeather |
| 15023 | Gloves of the First Expedition | 7 | 0 | handLeather |
| 15024 | Boots of the First Expedition | 7 | 0 | feetLeather |
| 15025 | Robe of the First Expedition | 7 | 0 | bodyRobe |
| 15026 | Sleeves of the First Expedition | 7 | 0 | handRobe |
| 15027 | Shoes of the First Expedition | 7 | 0 | feetRobe |
| 15667 | Outrider's Chestpiece | 11 | 1 | bodyMail |
| 15670 | Sentry's Jerkin | 11 | 1 | bodyLeather |
| 15673 | Outrider's Robes | 11 | 1 | bodyRobe |
| 17404 | Bark of Vekas | 4 | 0 | bodyMail |
| 17407 | Treejack's Jacket | 4 | 0 | bodyLeather |
| 17410 | Tannen-tint Robes | 4 | 0 | bodyRobe |
| 17413 | Second-in-Command's Breastplate | 8 | 2 | bodyMail |
| 17416 | Corruption-Covered Cuirass | 8 | 2 | bodyLeather |
| 17419 | Robes of Unnatural Order | 8 | 2 | bodyRobe |
| 55006 | Daybite | 2 | 0 | blaster |
| 55007 | Arcannon of the First Expedition | 7 | 0 | blaster |
| 55079 | See Shooter | 11 | 2 | blaster |
| 55271 | Boomstick of Vekas | 4 | 0 | blaster |
| 55272 | Kugai's Arcannon | 8 | 2 | blaster |
| 58172 | Morning Glory | 2 | 0 | shuriken |
| 58173 | Shuriken of the First Expedition | 7 | 0 | shuriken |
| 58174 | Copsebloom | 12 | 0 | shuriken |
| 59054 | Sunstroke | 2 | 0 | glaive |
| 59055 | Runeglaive of the First Expedition | 7 | 0 | glaive |
| 59056 | Gladeglaive | 12 | 0 | glaive |
| 59353 | Orcharn | 3 | 0 | glaive |
| 82006 | Knuckledusters | 2 | 0 | gauntlet |
| 82007 | Powerfists of the First Expedition | 7 | 0 | gauntlet |
| 82008 | Feyfists | 12 | 0 | gauntlet |

## Section 4: Missing ids

- 1314: no quest exists at this id (lookup_quest returned not found).

All other ids in the 1301 to 1317 range exist.
