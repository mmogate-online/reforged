# v31 Quest Rewards Cross-Validation - Island of Dawn (Phase 2a)

v31 `QuestCompensationData_13.xml` reward rows cross-validated against the v17 client reward display (`v17-quests.json`). The v17 display is the north star; disagreements are the server encoding diverging from it.

## Verdict counts

| Verdict | Count |
| --- | --- |
| ITEM_DRIFT | 35 |
| EXP_GOLD_DRIFT | 18 |
| EXACT | 10 |

`EXACT` exp/gold/itemBag/items all agree; `CLASS_SUPERSET` v31 adds only the engineer 9th-class item(s) the v17 catalog predates, otherwise identical; `EXP_GOLD_DRIFT` exp/gold/itemBag differ (items agree); `ITEM_DRIFT` item sets differ beyond engineer; `V31_EMPTY` v31 comp is a stub while v17 has a reward; `V17_EMPTY` v31 has a reward v17 does not; `BOTH_EMPTY`.

## Per-quest rewards

| gid | title | verdict | v17 | v31 | detail |
| --- | --- | --- | --- | --- | --- |
| 1301 | Dawn's Early Light | EXP_GOLD_DRIFT | 100xp/10g | 500xp/50g | exp v17=100 v31=500; gold v17=10 v31=50 |
| 1302 | Another Fine Mess | EXP_GOLD_DRIFT | 150xp/15g | 400xp/40g | exp v17=150 v31=400; gold v17=15 v31=40 |
| 1303 | The Secret Life of Trees | ITEM_DRIFT | 1500xp/0g bag=class | 2600xp/260g bag=class | exp v17=1500 v31=2600; gold v17=0 v31=260; v31 missing [('17712', '1', 'berserker'), ('17712', '1', 'lancer'), ('17715', '1', 'archer'), ('17715', '1', 'slayer'), ('17715', '1', 'warrior'), ('17718', '1', 'elementalist'), ('17718', '1', 'priest'), ('17718', '1', 'sorcerer')]; v31 extra [('12129', '1', 'warrior'), ('12130', '1', 'lancer'), ('12131', '1', 'slayer'), ('12132', '1', 'berserker'), ('12133', '1', 'sorcerer'), ('12134', '1', 'archer'), ('12135', '1', 'priest'), ('12136', '1', 'elementalist'), ('17404', '1', 'berserker'), ('17404', '1', 'engineer'), ('17404', '1', 'lancer'), ('17407', '1', 'archer'), ('17407', '1', 'slayer'), ('17407', '1', 'warrior'), ('17410', '1', 'elementalist'), ('17410', '1', 'priest'), ('17410', '1', 'sorcerer'), ('55271', '1', 'engineer')] |
| 1304 | Making the Rounds | ITEM_DRIFT | 600xp/0g bag=class | 800xp/80g bag=class | exp v17=600 v31=800; gold v17=0 v31=80; v31 missing [('17701', '1', 'berserker'), ('17701', '1', 'lancer'), ('17704', '1', 'archer'), ('17704', '1', 'slayer'), ('17704', '1', 'warrior'), ('17707', '1', 'elementalist'), ('17707', '1', 'priest'), ('17707', '1', 'sorcerer')]; v31 extra [('10009', '1', 'warrior'), ('10010', '1', 'lancer'), ('10011', '1', 'slayer'), ('10012', '1', 'berserker'), ('10013', '1', 'sorcerer'), ('10014', '1', 'archer'), ('10015', '1', 'priest'), ('10016', '1', 'elementalist'), ('55006', '1', 'engineer')] |
| 1305 | Elleon's Fate | ITEM_DRIFT | 800xp/0g bag=class | 4900xp/490g bag=class | exp v17=800 v31=4900; gold v17=0 v31=490; v31 missing [('17710', '1', 'berserker'), ('17710', '1', 'lancer'), ('17713', '1', 'archer'), ('17713', '1', 'slayer'), ('17713', '1', 'warrior'), ('17716', '1', 'elementalist'), ('17716', '1', 'priest'), ('17716', '1', 'sorcerer')]; v31 extra [('10017', '1', 'warrior'), ('10018', '1', 'lancer'), ('10019', '1', 'slayer'), ('10020', '1', 'berserker'), ('10021', '1', 'sorcerer'), ('10022', '1', 'archer'), ('10023', '1', 'priest'), ('10024', '1', 'elementalist'), ('15019', '1', 'berserker'), ('15019', '1', 'engineer'), ('15019', '1', 'lancer'), ('15020', '1', 'berserker'), ('15020', '1', 'engineer'), ('15020', '1', 'lancer'), ('15021', '1', 'berserker'), ('15021', '1', 'engineer'), ('15021', '1', 'lancer'), ('15022', '1', 'archer'), ('15022', '1', 'slayer'), ('15022', '1', 'warrior'), ('15023', '1', 'archer'), ('15023', '1', 'slayer'), ('15023', '1', 'warrior'), ('15024', '1', 'archer'), ('15024', '1', 'slayer'), ('15024', '1', 'warrior'), ('15025', '1', 'elementalist'), ('15025', '1', 'priest'), ('15025', '1', 'sorcerer'), ('15026', '1', 'elementalist'), ('15026', '1', 'priest'), ('15026', '1', 'sorcerer'), ('15027', '1', 'elementalist'), ('15027', '1', 'priest'), ('15027', '1', 'sorcerer'), ('55007', '1', 'engineer')] |
| 1306 | Traces of Darkness | EXACT | 800xp/80g | 800xp/80g | - |
| 1307 | Live by the Sword... | EXACT | 1000xp/100g bag=allpay | 1000xp/100g bag=allpay | - |
| 1308 | Essence of Foreboding | EXACT | 1000xp/100g | 1000xp/100g | - |
| 1309 | Acharak Attacks | ITEM_DRIFT | 2000xp/0g bag=class | 3200xp/320g | exp v17=2000 v31=3200; gold v17=0 v31=320; itemBag v17='class' v31=''; v31 missing [('10537', '1', 'warrior'), ('10538', '1', 'lancer'), ('10539', '1', 'slayer'), ('10540', '1', 'berserker'), ('10541', '1', 'sorcerer'), ('10542', '1', 'archer'), ('10543', '1', 'priest'), ('10544', '1', 'elementalist')] |
| 1310 | A Clue In the Dark | ITEM_DRIFT | 1000xp/100g | 1000xp/100g bag=class | itemBag v17='' v31='class'; v31 extra [('10017', '1', 'warrior'), ('10018', '1', 'lancer'), ('10019', '1', 'slayer'), ('10020', '1', 'berserker'), ('10021', '1', 'sorcerer'), ('10022', '1', 'archer'), ('10023', '1', 'priest'), ('10024', '1', 'elementalist'), ('15019', '1', 'berserker'), ('15019', '1', 'lancer'), ('15022', '1', 'archer'), ('15022', '1', 'slayer'), ('15022', '1', 'warrior'), ('15025', '1', 'elementalist'), ('15025', '1', 'priest'), ('15025', '1', 'sorcerer'), ('55007', '1', 'engineer')] |
| 1311 | Clearing the Gorge | EXP_GOLD_DRIFT | 1000xp/100g | 3600xp/360g | exp v17=1000 v31=3600; gold v17=100 v31=360 |
| 1312 | The Dark Patrol | ITEM_DRIFT | 1700xp/170g bag=class | 2500xp/250g | exp v17=1700 v31=2500; gold v17=170 v31=250; itemBag v17='class' v31=''; v31 missing [('15606', '1', 'berserker'), ('15606', '1', 'lancer'), ('15609', '1', 'archer'), ('15609', '1', 'slayer'), ('15609', '1', 'warrior'), ('15612', '1', 'elementalist'), ('15612', '1', 'priest'), ('15612', '1', 'sorcerer')] |
| 1313 | Into the Gorge | ITEM_DRIFT | 1000xp/100g bag=allpay | 6840xp/470g | exp v17=1000 v31=6840; gold v17=100 v31=470; itemBag v17='allpay' v31=''; v31 extra [('7100', '1', ''), ('7104', '1', ''), ('7108', '1', '')] |
| 1315 | Putting the Pieces Together | ITEM_DRIFT | 5200xp/0g bag=class | 4500xp/450g bag=class | exp v17=5200 v31=4500; gold v17=0 v31=450; v31 missing [('15668', '1', 'berserker'), ('15668', '1', 'lancer'), ('15671', '1', 'archer'), ('15671', '1', 'slayer'), ('15671', '1', 'warrior'), ('15674', '1', 'elementalist'), ('15674', '1', 'priest'), ('15674', '1', 'sorcerer')]; v31 extra [('12137', '1', 'warrior'), ('12138', '1', 'lancer'), ('12139', '1', 'slayer'), ('12140', '1', 'berserker'), ('12141', '1', 'sorcerer'), ('12142', '1', 'archer'), ('12143', '1', 'priest'), ('12144', '1', 'elementalist'), ('17413', '1', 'berserker'), ('17413', '1', 'engineer'), ('17413', '1', 'lancer'), ('17416', '1', 'archer'), ('17416', '1', 'slayer'), ('17416', '1', 'warrior'), ('17419', '1', 'elementalist'), ('17419', '1', 'priest'), ('17419', '1', 'sorcerer'), ('55272', '1', 'engineer')] |
| 1316 | Dark Revelations | ITEM_DRIFT | 6000xp/0g bag=class | 14600xp/1460g bag=class | exp v17=6000 v31=14600; gold v17=0 v31=1460; v31 missing [('160', '2', 'archer'), ('160', '2', 'berserker'), ('160', '2', 'elementalist'), ('160', '2', 'lancer'), ('160', '2', 'priest'), ('160', '2', 'slayer'), ('160', '2', 'sorcerer'), ('160', '2', 'warrior')]; v31 extra [('55079', '1', 'engineer')] |
| 1317 | Ride Off Into the Sunset | ITEM_DRIFT | 1500xp/0g bag=class | 2000xp/200g bag=class | exp v17=1500 v31=2000; gold v17=0 v31=200; v31 extra [('15667', '1', 'engineer')] |
| 1318 | Hunting the Beasts | ITEM_DRIFT | 900xp/90g bag=allpay | 1500xp/150g | exp v17=900 v31=1500; gold v17=90 v31=150; itemBag v17='allpay' v31=''; v31 missing [('5132', '1', '')] |
| 1319 | Dwellers of the Island | ITEM_DRIFT | 600xp/0g bag=class | 600xp/60g bag=class | gold v17=0 v31=60; v31 extra [('55305', '1', 'engineer')] |
| 1321 | A Bridge Pretty Near | EXP_GOLD_DRIFT | 300xp/30g | 800xp/80g | exp v17=300 v31=800; gold v17=30 v31=80 |
| 1322 | Unrest in the Forest | ITEM_DRIFT | 500xp/0g bag=class | 500xp/50g bag=class | gold v17=0 v31=50; v31 extra [('17703', '1', 'engineer')] |
| 1323 | Getting Some Answers | ITEM_DRIFT | 800xp/80g bag=allpay | 800xp/80g bag=class | itemBag v17='allpay' v31='class'; v31 missing [('5132', '1', '')]; v31 extra [('10009', '1', 'warrior'), ('10010', '1', 'lancer'), ('10011', '1', 'slayer'), ('10012', '1', 'berserker'), ('10013', '1', 'sorcerer'), ('10014', '1', 'archer'), ('10015', '1', 'priest'), ('10016', '1', 'elementalist'), ('55006', '1', 'engineer')] |
| 1324 | Essence and Sensibility | ITEM_DRIFT | 900xp/90g bag=allpay | 900xp/90g bag=allpay | v31 missing [('5132', '1', '')] |
| 1325 | The Perfect Cut | ITEM_DRIFT | 500xp/0g bag=class | 500xp/50g bag=class | gold v17=0 v31=50; v31 extra [('17702', '1', 'engineer')] |
| 1326 | Mana out of Mudmen | ITEM_DRIFT | 2000xp/200g bag=choice | 2000xp/200g bag=class | itemBag v17='choice' v31='class'; v31 missing [('125', '10', ''), ('129', '1', ''), ('130', '1', '')]; v31 extra [('15021', '1', 'berserker'), ('15021', '1', 'engineer'), ('15021', '1', 'lancer'), ('15024', '1', 'archer'), ('15024', '1', 'slayer'), ('15024', '1', 'warrior'), ('15027', '1', 'elementalist'), ('15027', '1', 'priest'), ('15027', '1', 'sorcerer')] |
| 1327 | Garrison in Distress | ITEM_DRIFT | 800xp/80g bag=allpay | 800xp/80g bag=allpay | v31 missing [('5132', '1', '')] |
| 1328 | Academic Theft | ITEM_DRIFT | 1100xp/110g bag=allpay | 1500xp/150g | exp v17=1100 v31=1500; gold v17=110 v31=150; itemBag v17='allpay' v31=''; v31 missing [('5132', '1', '')] |
| 1329 | Going Above and Beyond | ITEM_DRIFT | 100xp/10g bag=class | 400xp/10g bag=allpay | exp v17=100 v31=400; itemBag v17='class' v31='allpay'; v31 missing [('12409', '1', 'warrior'), ('12410', '1', 'lancer'), ('12411', '1', 'slayer'), ('12412', '1', 'berserker'), ('12413', '1', 'sorcerer'), ('12414', '1', 'archer'), ('12415', '1', 'priest'), ('12416', '1', 'elementalist')]; v31 extra [('7200', '10', ''), ('8007', '3', '')] |
| 1330 | Horned Horrors | ITEM_DRIFT | 1900xp/190g bag=allpay | 1900xp/190g bag=class | itemBag v17='allpay' v31='class'; v31 missing [('5132', '1', '')]; v31 extra [('15020', '1', 'berserker'), ('15020', '1', 'engineer'), ('15020', '1', 'lancer'), ('15023', '1', 'archer'), ('15023', '1', 'slayer'), ('15023', '1', 'warrior'), ('15026', '1', 'elementalist'), ('15026', '1', 'priest'), ('15026', '1', 'sorcerer')] |
| 1331 | I'll Take the High Road | ITEM_DRIFT | 800xp/80g bag=allpay | 2300xp/230g bag=class | exp v17=800 v31=2300; gold v17=80 v31=230; itemBag v17='allpay' v31='class'; v31 missing [('8007', '2', '')]; v31 extra [('17710', '1', 'berserker'), ('17710', '1', 'engineer'), ('17710', '1', 'lancer'), ('17713', '1', 'archer'), ('17713', '1', 'slayer'), ('17713', '1', 'warrior'), ('17716', '1', 'elementalist'), ('17716', '1', 'priest'), ('17716', '1', 'sorcerer')] |
| 1332 | They'll Eat Anything | ITEM_DRIFT | 900xp/90g bag=allpay | 900xp/90g bag=allpay | v31 missing [('5132', '1', '')] |
| 1333 | Twice the Bark, Twice the Bite | ITEM_DRIFT | 1700xp/170g bag=allpay | 1700xp/170g bag=allpay | v31 missing [('5132', '1', '')] |
| 1334 | Investigating the Relics <Repeatable> | EXACT | 800xp/80g | 800xp/80g | - |
| 1335 | One of Our Couriers is Missing | EXACT | 600xp/60g | 600xp/60g | - |
| 1336 | Chione's Missing Cargo | EXACT | 600xp/60g | 600xp/60g | - |
| 1337 | Searching for the Stolen Stones | ITEM_DRIFT | 1100xp/0g bag=class | 1500xp/150g | exp v17=1100 v31=1500; gold v17=0 v31=150; itemBag v17='class' v31=''; v31 missing [('15605', '1', 'berserker'), ('15605', '1', 'lancer'), ('15608', '1', 'archer'), ('15608', '1', 'slayer'), ('15608', '1', 'warrior'), ('15611', '1', 'elementalist'), ('15611', '1', 'priest'), ('15611', '1', 'sorcerer')] |
| 1338 | Chione's Report | EXACT | 500xp/50g | 500xp/50g | - |
| 1339 | Sersine, She Seeks Shackles | ITEM_DRIFT | 2900xp/290g bag=allpay | 3200xp/320g | exp v17=2900 v31=3200; gold v17=290 v31=320; itemBag v17='allpay' v31=''; v31 missing [('5132', '1', '')] |
| 1340 | Painful Disc-overies | ITEM_DRIFT | 2300xp/230g bag=choice | 3200xp/320g | exp v17=2300 v31=3200; gold v17=230 v31=320; itemBag v17='choice' v31=''; v31 missing [('7100', '1', ''), ('7104', '1', ''), ('7108', '1', '')] |
| 1341 | Bequest of the Dead <Repeatable> | ITEM_DRIFT | 1000xp/100g | 1500xp/g bag=allpay | exp v17=1000 v31=1500; gold v17=100 v31=; itemBag v17='' v31='allpay'; v31 extra [('7100', '1', ''), ('7104', '1', ''), ('7108', '1', '')] |
| 1343 | Answers Lead to More Questions | EXACT | 800xp/80g | 800xp/80g | - |
| 1344 | Destroy All Destroyers! | ITEM_DRIFT | 3000xp/300g bag=allpay | 3000xp/300g bag=allpay | v31 missing [('5132', '1', '')] |
| 1345 | Desperately Seeking Sorscha | EXACT | 500xp/50g bag=allpay | 500xp/50g bag=allpay | - |
| 1346 | Sorcha's Reckless Challenge | EXACT | 6000xp/600g | 6000xp/600g | - |
| 1347 | It Was a Rock...Crawler! | ITEM_DRIFT | 900xp/0g bag=class | 900xp/90g bag=class | gold v17=0 v31=90; v31 extra [('17711', '1', 'engineer')] |
| 1348 | Ferocious Flowering Felons | ITEM_DRIFT | 900xp/90g bag=allpay | 900xp/90g bag=allpay | v31 missing [('5132', '1', '')] |
| 1349 | Gotta Kill 'em All | ITEM_DRIFT | 2300xp/230g bag=allpay | 2300xp/230g bag=allpay | v31 missing [('5132', '1', '')] |
| 1350 | Strange Attractors | EXP_GOLD_DRIFT | 1800xp/180g | 8400xp/840g | exp v17=1800 v31=8400; gold v17=180 v31=840 |
| 1351 | Supply and Demand | ITEM_DRIFT | 800xp/80g bag=allpay | 800xp/80g bag=allpay | v31 missing [('6048', '5', '')]; v31 extra [('6048', '3', '')] |
| 1352 | Supply and Demand | ITEM_DRIFT | 800xp/80g bag=allpay | 800xp/80g bag=allpay | v31 missing [('6048', '5', '')]; v31 extra [('6048', '3', '')] |
| 1371 | Initial Warrior Training | EXP_GOLD_DRIFT | 50xp/5g | 2100xp/150g | exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1372 | Initial Lancer Training | EXP_GOLD_DRIFT | 50xp/5g | 2100xp/150g | exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1373 | Initial Slayer Training | EXP_GOLD_DRIFT | 50xp/5g | 2100xp/150g | exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1374 | Initial Berserker Training | EXP_GOLD_DRIFT | 50xp/5g | 2100xp/150g | exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1375 | Initial Archer Training | EXP_GOLD_DRIFT | 50xp/5g | 2100xp/150g | exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1376 | Initial Sorcerer Training | EXP_GOLD_DRIFT | 50xp/5g | 2100xp/150g | exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1377 | Initial Priest Training | EXP_GOLD_DRIFT | 50xp/5g | 2100xp/150g | exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1378 | Initial Mystic Training | EXP_GOLD_DRIFT | 50xp/5g | 2100xp/150g | exp v17=50 v31=2100; gold v17=5 v31=150 |
| 1382 | Introduction to Gathering | EXP_GOLD_DRIFT | 100xp/10g | 100xp/g | gold v17=10 v31= |
| 1384 | Recharge It | ITEM_DRIFT | 50xp/5g bag=allpay | 900xp/80g bag=allpay | exp v17=50 v31=900; gold v17=5 v31=80; v31 extra [('6048', '3', '')] |
| 1385 | Always After Me Lucky Charms | EXP_GOLD_DRIFT | 50xp/5g | 50xp/g | gold v17=5 v31= |
| 1386 | Bombs Away! | EXP_GOLD_DRIFT | 300xp/30g bag=allpay | 300xp/g bag=allpay | gold v17=30 v31= |
| 1389 | 판도라 상자 사용 안내 | EXP_GOLD_DRIFT | 200xp/20g | 200xp/g | gold v17=20 v31= |
| 1390 | Special Delivery | EXP_GOLD_DRIFT | 300xp/30g bag=allpay | 300xp/g bag=allpay | gold v17=30 v31= |

## Notable disagreements

- **1301 Dawn's Early Light** [EXP_GOLD_DRIFT]: exp v17=100 v31=500; gold v17=10 v31=50
- **1302 Another Fine Mess** [EXP_GOLD_DRIFT]: exp v17=150 v31=400; gold v17=15 v31=40
- **1303 The Secret Life of Trees** [ITEM_DRIFT]: exp v17=1500 v31=2600; gold v17=0 v31=260; v31 missing [('17712', '1', 'berserker'), ('17712', '1', 'lancer'), ('17715', '1', 'archer'), ('17715', '1', 'slayer'), ('17715', '1', 'warrior'), ('17718', '1', 'elementalist'), ('17718', '1', 'priest'), ('17718', '1', 'sorcerer')]; v31 extra [('12129', '1', 'warrior'), ('12130', '1', 'lancer'), ('12131', '1', 'slayer'), ('12132', '1', 'berserker'), ('12133', '1', 'sorcerer'), ('12134', '1', 'archer'), ('12135', '1', 'priest'), ('12136', '1', 'elementalist'), ('17404', '1', 'berserker'), ('17404', '1', 'engineer'), ('17404', '1', 'lancer'), ('17407', '1', 'archer'), ('17407', '1', 'slayer'), ('17407', '1', 'warrior'), ('17410', '1', 'elementalist'), ('17410', '1', 'priest'), ('17410', '1', 'sorcerer'), ('55271', '1', 'engineer')]
- **1304 Making the Rounds** [ITEM_DRIFT]: exp v17=600 v31=800; gold v17=0 v31=80; v31 missing [('17701', '1', 'berserker'), ('17701', '1', 'lancer'), ('17704', '1', 'archer'), ('17704', '1', 'slayer'), ('17704', '1', 'warrior'), ('17707', '1', 'elementalist'), ('17707', '1', 'priest'), ('17707', '1', 'sorcerer')]; v31 extra [('10009', '1', 'warrior'), ('10010', '1', 'lancer'), ('10011', '1', 'slayer'), ('10012', '1', 'berserker'), ('10013', '1', 'sorcerer'), ('10014', '1', 'archer'), ('10015', '1', 'priest'), ('10016', '1', 'elementalist'), ('55006', '1', 'engineer')]
- **1305 Elleon's Fate** [ITEM_DRIFT]: exp v17=800 v31=4900; gold v17=0 v31=490; v31 missing [('17710', '1', 'berserker'), ('17710', '1', 'lancer'), ('17713', '1', 'archer'), ('17713', '1', 'slayer'), ('17713', '1', 'warrior'), ('17716', '1', 'elementalist'), ('17716', '1', 'priest'), ('17716', '1', 'sorcerer')]; v31 extra [('10017', '1', 'warrior'), ('10018', '1', 'lancer'), ('10019', '1', 'slayer'), ('10020', '1', 'berserker'), ('10021', '1', 'sorcerer'), ('10022', '1', 'archer'), ('10023', '1', 'priest'), ('10024', '1', 'elementalist'), ('15019', '1', 'berserker'), ('15019', '1', 'engineer'), ('15019', '1', 'lancer'), ('15020', '1', 'berserker'), ('15020', '1', 'engineer'), ('15020', '1', 'lancer'), ('15021', '1', 'berserker'), ('15021', '1', 'engineer'), ('15021', '1', 'lancer'), ('15022', '1', 'archer'), ('15022', '1', 'slayer'), ('15022', '1', 'warrior'), ('15023', '1', 'archer'), ('15023', '1', 'slayer'), ('15023', '1', 'warrior'), ('15024', '1', 'archer'), ('15024', '1', 'slayer'), ('15024', '1', 'warrior'), ('15025', '1', 'elementalist'), ('15025', '1', 'priest'), ('15025', '1', 'sorcerer'), ('15026', '1', 'elementalist'), ('15026', '1', 'priest'), ('15026', '1', 'sorcerer'), ('15027', '1', 'elementalist'), ('15027', '1', 'priest'), ('15027', '1', 'sorcerer'), ('55007', '1', 'engineer')]
- **1309 Acharak Attacks** [ITEM_DRIFT]: exp v17=2000 v31=3200; gold v17=0 v31=320; itemBag v17='class' v31=''; v31 missing [('10537', '1', 'warrior'), ('10538', '1', 'lancer'), ('10539', '1', 'slayer'), ('10540', '1', 'berserker'), ('10541', '1', 'sorcerer'), ('10542', '1', 'archer'), ('10543', '1', 'priest'), ('10544', '1', 'elementalist')]
- **1310 A Clue In the Dark** [ITEM_DRIFT]: itemBag v17='' v31='class'; v31 extra [('10017', '1', 'warrior'), ('10018', '1', 'lancer'), ('10019', '1', 'slayer'), ('10020', '1', 'berserker'), ('10021', '1', 'sorcerer'), ('10022', '1', 'archer'), ('10023', '1', 'priest'), ('10024', '1', 'elementalist'), ('15019', '1', 'berserker'), ('15019', '1', 'lancer'), ('15022', '1', 'archer'), ('15022', '1', 'slayer'), ('15022', '1', 'warrior'), ('15025', '1', 'elementalist'), ('15025', '1', 'priest'), ('15025', '1', 'sorcerer'), ('55007', '1', 'engineer')]
- **1311 Clearing the Gorge** [EXP_GOLD_DRIFT]: exp v17=1000 v31=3600; gold v17=100 v31=360
- **1312 The Dark Patrol** [ITEM_DRIFT]: exp v17=1700 v31=2500; gold v17=170 v31=250; itemBag v17='class' v31=''; v31 missing [('15606', '1', 'berserker'), ('15606', '1', 'lancer'), ('15609', '1', 'archer'), ('15609', '1', 'slayer'), ('15609', '1', 'warrior'), ('15612', '1', 'elementalist'), ('15612', '1', 'priest'), ('15612', '1', 'sorcerer')]
- **1313 Into the Gorge** [ITEM_DRIFT]: exp v17=1000 v31=6840; gold v17=100 v31=470; itemBag v17='allpay' v31=''; v31 extra [('7100', '1', ''), ('7104', '1', ''), ('7108', '1', '')]
- **1315 Putting the Pieces Together** [ITEM_DRIFT]: exp v17=5200 v31=4500; gold v17=0 v31=450; v31 missing [('15668', '1', 'berserker'), ('15668', '1', 'lancer'), ('15671', '1', 'archer'), ('15671', '1', 'slayer'), ('15671', '1', 'warrior'), ('15674', '1', 'elementalist'), ('15674', '1', 'priest'), ('15674', '1', 'sorcerer')]; v31 extra [('12137', '1', 'warrior'), ('12138', '1', 'lancer'), ('12139', '1', 'slayer'), ('12140', '1', 'berserker'), ('12141', '1', 'sorcerer'), ('12142', '1', 'archer'), ('12143', '1', 'priest'), ('12144', '1', 'elementalist'), ('17413', '1', 'berserker'), ('17413', '1', 'engineer'), ('17413', '1', 'lancer'), ('17416', '1', 'archer'), ('17416', '1', 'slayer'), ('17416', '1', 'warrior'), ('17419', '1', 'elementalist'), ('17419', '1', 'priest'), ('17419', '1', 'sorcerer'), ('55272', '1', 'engineer')]
- **1316 Dark Revelations** [ITEM_DRIFT]: exp v17=6000 v31=14600; gold v17=0 v31=1460; v31 missing [('160', '2', 'archer'), ('160', '2', 'berserker'), ('160', '2', 'elementalist'), ('160', '2', 'lancer'), ('160', '2', 'priest'), ('160', '2', 'slayer'), ('160', '2', 'sorcerer'), ('160', '2', 'warrior')]; v31 extra [('55079', '1', 'engineer')]
- **1317 Ride Off Into the Sunset** [ITEM_DRIFT]: exp v17=1500 v31=2000; gold v17=0 v31=200; v31 extra [('15667', '1', 'engineer')]
- **1318 Hunting the Beasts** [ITEM_DRIFT]: exp v17=900 v31=1500; gold v17=90 v31=150; itemBag v17='allpay' v31=''; v31 missing [('5132', '1', '')]
- **1319 Dwellers of the Island** [ITEM_DRIFT]: gold v17=0 v31=60; v31 extra [('55305', '1', 'engineer')]
- **1321 A Bridge Pretty Near** [EXP_GOLD_DRIFT]: exp v17=300 v31=800; gold v17=30 v31=80
- **1322 Unrest in the Forest** [ITEM_DRIFT]: gold v17=0 v31=50; v31 extra [('17703', '1', 'engineer')]
- **1323 Getting Some Answers** [ITEM_DRIFT]: itemBag v17='allpay' v31='class'; v31 missing [('5132', '1', '')]; v31 extra [('10009', '1', 'warrior'), ('10010', '1', 'lancer'), ('10011', '1', 'slayer'), ('10012', '1', 'berserker'), ('10013', '1', 'sorcerer'), ('10014', '1', 'archer'), ('10015', '1', 'priest'), ('10016', '1', 'elementalist'), ('55006', '1', 'engineer')]
- **1324 Essence and Sensibility** [ITEM_DRIFT]: v31 missing [('5132', '1', '')]
- **1325 The Perfect Cut** [ITEM_DRIFT]: gold v17=0 v31=50; v31 extra [('17702', '1', 'engineer')]
- **1326 Mana out of Mudmen** [ITEM_DRIFT]: itemBag v17='choice' v31='class'; v31 missing [('125', '10', ''), ('129', '1', ''), ('130', '1', '')]; v31 extra [('15021', '1', 'berserker'), ('15021', '1', 'engineer'), ('15021', '1', 'lancer'), ('15024', '1', 'archer'), ('15024', '1', 'slayer'), ('15024', '1', 'warrior'), ('15027', '1', 'elementalist'), ('15027', '1', 'priest'), ('15027', '1', 'sorcerer')]
- **1327 Garrison in Distress** [ITEM_DRIFT]: v31 missing [('5132', '1', '')]
- **1328 Academic Theft** [ITEM_DRIFT]: exp v17=1100 v31=1500; gold v17=110 v31=150; itemBag v17='allpay' v31=''; v31 missing [('5132', '1', '')]
- **1329 Going Above and Beyond** [ITEM_DRIFT]: exp v17=100 v31=400; itemBag v17='class' v31='allpay'; v31 missing [('12409', '1', 'warrior'), ('12410', '1', 'lancer'), ('12411', '1', 'slayer'), ('12412', '1', 'berserker'), ('12413', '1', 'sorcerer'), ('12414', '1', 'archer'), ('12415', '1', 'priest'), ('12416', '1', 'elementalist')]; v31 extra [('7200', '10', ''), ('8007', '3', '')]
- **1330 Horned Horrors** [ITEM_DRIFT]: itemBag v17='allpay' v31='class'; v31 missing [('5132', '1', '')]; v31 extra [('15020', '1', 'berserker'), ('15020', '1', 'engineer'), ('15020', '1', 'lancer'), ('15023', '1', 'archer'), ('15023', '1', 'slayer'), ('15023', '1', 'warrior'), ('15026', '1', 'elementalist'), ('15026', '1', 'priest'), ('15026', '1', 'sorcerer')]
- **1331 I'll Take the High Road** [ITEM_DRIFT]: exp v17=800 v31=2300; gold v17=80 v31=230; itemBag v17='allpay' v31='class'; v31 missing [('8007', '2', '')]; v31 extra [('17710', '1', 'berserker'), ('17710', '1', 'engineer'), ('17710', '1', 'lancer'), ('17713', '1', 'archer'), ('17713', '1', 'slayer'), ('17713', '1', 'warrior'), ('17716', '1', 'elementalist'), ('17716', '1', 'priest'), ('17716', '1', 'sorcerer')]
- **1332 They'll Eat Anything** [ITEM_DRIFT]: v31 missing [('5132', '1', '')]
- **1333 Twice the Bark, Twice the Bite** [ITEM_DRIFT]: v31 missing [('5132', '1', '')]
- **1337 Searching for the Stolen Stones** [ITEM_DRIFT]: exp v17=1100 v31=1500; gold v17=0 v31=150; itemBag v17='class' v31=''; v31 missing [('15605', '1', 'berserker'), ('15605', '1', 'lancer'), ('15608', '1', 'archer'), ('15608', '1', 'slayer'), ('15608', '1', 'warrior'), ('15611', '1', 'elementalist'), ('15611', '1', 'priest'), ('15611', '1', 'sorcerer')]
- **1339 Sersine, She Seeks Shackles** [ITEM_DRIFT]: exp v17=2900 v31=3200; gold v17=290 v31=320; itemBag v17='allpay' v31=''; v31 missing [('5132', '1', '')]
- **1340 Painful Disc-overies** [ITEM_DRIFT]: exp v17=2300 v31=3200; gold v17=230 v31=320; itemBag v17='choice' v31=''; v31 missing [('7100', '1', ''), ('7104', '1', ''), ('7108', '1', '')]
- **1341 Bequest of the Dead <Repeatable>** [ITEM_DRIFT]: exp v17=1000 v31=1500; gold v17=100 v31=; itemBag v17='' v31='allpay'; v31 extra [('7100', '1', ''), ('7104', '1', ''), ('7108', '1', '')]
- **1344 Destroy All Destroyers!** [ITEM_DRIFT]: v31 missing [('5132', '1', '')]
- **1347 It Was a Rock...Crawler!** [ITEM_DRIFT]: gold v17=0 v31=90; v31 extra [('17711', '1', 'engineer')]
- **1348 Ferocious Flowering Felons** [ITEM_DRIFT]: v31 missing [('5132', '1', '')]
- **1349 Gotta Kill 'em All** [ITEM_DRIFT]: v31 missing [('5132', '1', '')]
- **1350 Strange Attractors** [EXP_GOLD_DRIFT]: exp v17=1800 v31=8400; gold v17=180 v31=840
- **1351 Supply and Demand** [ITEM_DRIFT]: v31 missing [('6048', '5', '')]; v31 extra [('6048', '3', '')]
- **1352 Supply and Demand** [ITEM_DRIFT]: v31 missing [('6048', '5', '')]; v31 extra [('6048', '3', '')]
- **1371 Initial Warrior Training** [EXP_GOLD_DRIFT]: exp v17=50 v31=2100; gold v17=5 v31=150
- **1372 Initial Lancer Training** [EXP_GOLD_DRIFT]: exp v17=50 v31=2100; gold v17=5 v31=150
- **1373 Initial Slayer Training** [EXP_GOLD_DRIFT]: exp v17=50 v31=2100; gold v17=5 v31=150
- **1374 Initial Berserker Training** [EXP_GOLD_DRIFT]: exp v17=50 v31=2100; gold v17=5 v31=150
- **1375 Initial Archer Training** [EXP_GOLD_DRIFT]: exp v17=50 v31=2100; gold v17=5 v31=150
- **1376 Initial Sorcerer Training** [EXP_GOLD_DRIFT]: exp v17=50 v31=2100; gold v17=5 v31=150
- **1377 Initial Priest Training** [EXP_GOLD_DRIFT]: exp v17=50 v31=2100; gold v17=5 v31=150
- **1378 Initial Mystic Training** [EXP_GOLD_DRIFT]: exp v17=50 v31=2100; gold v17=5 v31=150
- **1382 Introduction to Gathering** [EXP_GOLD_DRIFT]: gold v17=10 v31=
- **1384 Recharge It** [ITEM_DRIFT]: exp v17=50 v31=900; gold v17=5 v31=80; v31 extra [('6048', '3', '')]
- **1385 Always After Me Lucky Charms** [EXP_GOLD_DRIFT]: gold v17=5 v31=
- **1386 Bombs Away!** [EXP_GOLD_DRIFT]: gold v17=30 v31=
- **1389 판도라 상자 사용 안내** [EXP_GOLD_DRIFT]: gold v17=20 v31=
- **1390 Special Delivery** [EXP_GOLD_DRIFT]: gold v17=30 v31=
