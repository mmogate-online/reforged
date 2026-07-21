# Classification: Quest Rewards (axis 2)

Target: **v17 display data translated to server encoding**. Roster: 63 quests.

Verdict counts: MATCH=10, RESTORE=53

- v17 reward items checked against v92 Item: 74
- **BLOCKERS (missing from v92):** none

> v31 rewards are NOT the target (only 10/63 match); v31 rows used as encoding templates only.

| gid | title | verdict | note |
|-----|-------|---------|------|
| 1301 | Dawn's Early Light | RESTORE | EXP_GOLD_DRIFT: exp v17=100 v31=500; gold v17=10 v31=50 |
| 1302 | Another Fine Mess | RESTORE | EXP_GOLD_DRIFT: exp v17=150 v31=400; gold v17=15 v31=40 |
| 1303 | The Secret Life of Trees | RESTORE | ITEM_DRIFT: exp v17=1500 v31=2600; gold v17=0 v31=260; v31 missing [(' |
| 1304 | Making the Rounds | RESTORE | ITEM_DRIFT: exp v17=600 v31=800; gold v17=0 v31=80; v31 missing [('177 |
| 1305 | Elleon's Fate | RESTORE | ITEM_DRIFT: exp v17=800 v31=4900; gold v17=0 v31=490; v31 missing [('1 |
| 1306 | Traces of Darkness | MATCH | v31 rewards already equal v17 display data |
| 1307 | Live by the Sword... | MATCH | v31 rewards already equal v17 display data |
| 1308 | Essence of Foreboding | MATCH | v31 rewards already equal v17 display data |
| 1309 | Acharak Attacks | RESTORE | ITEM_DRIFT: exp v17=2000 v31=3200; gold v17=0 v31=320; itemBag v17='cl |
| 1310 | A Clue In the Dark | RESTORE | ITEM_DRIFT: itemBag v17='' v31='class'; v31 extra [('10017', '1', 'war |
| 1311 | Clearing the Gorge | RESTORE | EXP_GOLD_DRIFT: exp v17=1000 v31=3600; gold v17=100 v31=360 |
| 1312 | The Dark Patrol | RESTORE | ITEM_DRIFT: exp v17=1700 v31=2500; gold v17=170 v31=250; itemBag v17=' |
| 1313 | Into the Gorge | RESTORE | ITEM_DRIFT: exp v17=1000 v31=6840; gold v17=100 v31=470; itemBag v17=' |
| 1315 | Putting the Pieces Together | RESTORE | ITEM_DRIFT: exp v17=5200 v31=4500; gold v17=0 v31=450; v31 missing [(' |
| 1316 | Dark Revelations | RESTORE | ITEM_DRIFT: exp v17=6000 v31=14600; gold v17=0 v31=1460; v31 missing [ |
| 1317 | Ride Off Into the Sunset | RESTORE | ITEM_DRIFT: exp v17=1500 v31=2000; gold v17=0 v31=200; v31 extra [('15 |
| 1318 | Hunting the Beasts | RESTORE | ITEM_DRIFT: exp v17=900 v31=1500; gold v17=90 v31=150; itemBag v17='al |
| 1319 | Dwellers of the Island | RESTORE | ITEM_DRIFT: gold v17=0 v31=60; v31 extra [('55305', '1', 'engineer')] |
| 1321 | A Bridge Pretty Near | RESTORE | EXP_GOLD_DRIFT: exp v17=300 v31=800; gold v17=30 v31=80 |
| 1322 | Unrest in the Forest | RESTORE | ITEM_DRIFT: gold v17=0 v31=50; v31 extra [('17703', '1', 'engineer')] |
| 1323 | Getting Some Answers | RESTORE | ITEM_DRIFT: itemBag v17='allpay' v31='class'; v31 missing [('5132', '1 |
| 1324 | Essence and Sensibility | RESTORE | ITEM_DRIFT: v31 missing [('5132', '1', '')] |
| 1325 | The Perfect Cut | RESTORE | ITEM_DRIFT: gold v17=0 v31=50; v31 extra [('17702', '1', 'engineer')] |
| 1326 | Mana out of Mudmen | RESTORE | ITEM_DRIFT: itemBag v17='choice' v31='class'; v31 missing [('125', '10 |
| 1327 | Garrison in Distress | RESTORE | ITEM_DRIFT: v31 missing [('5132', '1', '')] |
| 1328 | Academic Theft | RESTORE | ITEM_DRIFT: exp v17=1100 v31=1500; gold v17=110 v31=150; itemBag v17=' |
| 1329 | Going Above and Beyond | RESTORE | ITEM_DRIFT: exp v17=100 v31=400; itemBag v17='class' v31='allpay'; v31 |
| 1330 | Horned Horrors | RESTORE | ITEM_DRIFT: itemBag v17='allpay' v31='class'; v31 missing [('5132', '1 |
| 1331 | I'll Take the High Road | RESTORE | ITEM_DRIFT: exp v17=800 v31=2300; gold v17=80 v31=230; itemBag v17='al |
| 1332 | They'll Eat Anything | RESTORE | ITEM_DRIFT: v31 missing [('5132', '1', '')] |
| 1333 | Twice the Bark, Twice the Bite | RESTORE | ITEM_DRIFT: v31 missing [('5132', '1', '')] |
| 1334 | Investigating the Relics <Repe | MATCH | v31 rewards already equal v17 display data |
| 1335 | One of Our Couriers is Missing | MATCH | v31 rewards already equal v17 display data |
| 1336 | Chione's Missing Cargo | MATCH | v31 rewards already equal v17 display data |
| 1337 | Searching for the Stolen Stone | RESTORE | ITEM_DRIFT: exp v17=1100 v31=1500; gold v17=0 v31=150; itemBag v17='cl |
| 1338 | Chione's Report | MATCH | v31 rewards already equal v17 display data |
| 1339 | Sersine, She Seeks Shackles | RESTORE | ITEM_DRIFT: exp v17=2900 v31=3200; gold v17=290 v31=320; itemBag v17=' |
| 1340 | Painful Disc-overies | RESTORE | ITEM_DRIFT: exp v17=2300 v31=3200; gold v17=230 v31=320; itemBag v17=' |
| 1341 | Bequest of the Dead <Repeatabl | RESTORE | ITEM_DRIFT: exp v17=1000 v31=1500; gold v17=100 v31=; itemBag v17='' v |
| 1343 | Answers Lead to More Questions | MATCH | v31 rewards already equal v17 display data |
| 1344 | Destroy All Destroyers! | RESTORE | ITEM_DRIFT: v31 missing [('5132', '1', '')] |
| 1345 | Desperately Seeking Sorscha | MATCH | v31 rewards already equal v17 display data |
| 1346 | Sorcha's Reckless Challenge | MATCH | v31 rewards already equal v17 display data |
| 1347 | It Was a Rock...Crawler! | RESTORE | ITEM_DRIFT: gold v17=0 v31=90; v31 extra [('17711', '1', 'engineer')] |
| 1348 | Ferocious Flowering Felons | RESTORE | ITEM_DRIFT: v31 missing [('5132', '1', '')] |
| 1349 | Gotta Kill 'em All | RESTORE | ITEM_DRIFT: v31 missing [('5132', '1', '')] |
| 1350 | Strange Attractors | RESTORE | EXP_GOLD_DRIFT: exp v17=1800 v31=8400; gold v17=180 v31=840 |
| 1351 | Supply and Demand | RESTORE | ITEM_DRIFT: v31 missing [('6048', '5', '')]; v31 extra [('6048', '3',  |
| 1352 | Supply and Demand | RESTORE | ITEM_DRIFT: v31 missing [('6048', '5', '')]; v31 extra [('6048', '3',  |
| 1371 | Initial Warrior Training | RESTORE | EXP_GOLD_DRIFT: exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1372 | Initial Lancer Training | RESTORE | EXP_GOLD_DRIFT: exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1373 | Initial Slayer Training | RESTORE | EXP_GOLD_DRIFT: exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1374 | Initial Berserker Training | RESTORE | EXP_GOLD_DRIFT: exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1375 | Initial Archer Training | RESTORE | EXP_GOLD_DRIFT: exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1376 | Initial Sorcerer Training | RESTORE | EXP_GOLD_DRIFT: exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1377 | Initial Priest Training | RESTORE | EXP_GOLD_DRIFT: exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1378 | Initial Mystic Training | RESTORE | EXP_GOLD_DRIFT: exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1382 | Introduction to Gathering | RESTORE | EXP_GOLD_DRIFT: gold v17=10 v31= |
| 1384 | Recharge It | RESTORE | ITEM_DRIFT: exp v17=50 v31=900; gold v17=5 v31=80; v31 extra [('6048', |
| 1385 | Always After Me Lucky Charms | RESTORE | EXP_GOLD_DRIFT: gold v17=5 v31= |
| 1386 | Bombs Away! | RESTORE | EXP_GOLD_DRIFT: gold v17=30 v31= |
| 1389 | 판도라 상자 사용 안내 | RESTORE | EXP_GOLD_DRIFT: gold v17=20 v31= |
| 1390 | Special Delivery | RESTORE | EXP_GOLD_DRIFT: gold v17=30 v31= |
