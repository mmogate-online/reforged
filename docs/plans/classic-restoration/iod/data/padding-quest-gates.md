# IoD Padding: Per-Candidate Quest Enable Gates (workstreams 1, 2, 5)

Analysis only. Verdicts for the 40 sentinel-disabled quests in the 1300-1399 band, each adjudicated against the enable gates: (a) v31 server data intact, (b) every referenced NPC spawns in the ported baseline, (c) every hunt/collect target mob spawns in the baseline.

Source of truth: raw v31 datasheet XML at `Z:\tera pserver\v31.04\...\Datasheet`, parsed with python. Baseline equals v31 exactly (confirmed by the v31-vs-v92 quest diff), so v31 TerritoryData is authoritative for gates (b) and (c). Companion machine-readable file: `padding-quest-gates.json`.

## Summary

- Disabled candidates evaluated: **40** (prereq marker 99,99; identical set in v31 and v92).
- Live set untouched: 25 (story groups 1 and 2).
- **Gate (a) passes for all 40**: every candidate has its QuestDialog file, StrSheet_Quest rows, and a non-stub v31 QuestCompensationData_13 row. The differentiator is gate (b) NPC spawns and gate (c) mob habitats.

| Verdict | Count | Meaning |
|---------|-------|---------|
| RESTORE | 22 | Gates a+b+c pass as-is. Enable = replace prereq 99,99 + port v31 rewards. No world edits. |
| RESTORE+FIX | 2 | Gates pass, but a dormant internal inconsistency must be fixed on enable (doctrine rule 1) with a divergence-log entry. |
| ADAPT | 15 | Gate (a) passes; gate (b)/(c) fails but the fix is a bounded, named spawn/habitat addition (or a cross-axis collections dependency). |
| OUT | 1 | Superseded content; do not re-enable. |

## RESTORE (22)

| gid | title | giver (hz,tpl name) | lvl | v17 parent | gate a/b/c | action / justification |
|-----|-------|---------------------|-----|-----------|-----------|------------|
| 1302 | Another Fine Mess | 213,1014 (연락장교 램버트) | 1 | root | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent root), port v31 rewards. |
| 1312 | The Dark Patrol | 213,1134 (하사관 로드릭) | 8 | 1311 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1311), port v31 rewards. |
| 1318 | Hunting the Beasts | 213,1017 (연구원 카이몬) | 2 | 1322 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1322), port v31 rewards. |
| 1321 | A Bridge Pretty Near | 213,1106 (하사관 라브로스) | 1 | root | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent root), port v31 rewards. |
| 1323 | Getting Some Answers | 213,1003 (하사관 케이샤) | 1 | 1322 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1322), port v31 rewards. |
| 1325 | The Perfect Cut | 213,1121 (경비병 라이언) | 3 | root | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent root), port v31 rewards. |
| 1326 | Mana out of Mudmen | 64,1023 (경비병 미카엘) | 5 | root | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent root), port v31 rewards. |
| 1328 | Academic Theft | 64,1001 (파견장교 율리아) | 4 | 1386 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1386), port v31 rewards. |
| 1330 | Horned Horrors | 64,1028 (경비병 자키) | 5 | root | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent root), port v31 rewards. |
| 1335 | One of Our Couriers Is Missing | 64,1001 (파견장교 율리아) | 8 | 1310 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1310), port v31 rewards. |
| 1337 | The Last One | 213,1007 (연락선 조종사 키오네) | 7 | 1335 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1335), port v31 rewards. |
| 1338 | Chione's Report | 213,1007 (연락선 조종사 키오네) | 7 | 1337 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1337), port v31 rewards. |
| 1339 | Sersine, She Seeks Shackles | 213,1025 (마법사 키아나) | 8 | 1313 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1313), port v31 rewards. |
| 1340 | Painful Disc-overies | 213,1143 (기사  쥬콘) | 8 | root | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent root), port v31 rewards. |
| 1343 | Answers Lead to More Questions | 213,1025 (마법사 키아나) | 9 | 1315 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1315), port v31 rewards. |
| 1344 | Destroy All Destroyers | 213,1143 (기사  쥬콘) | 9 | 1343 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1343), port v31 rewards. |
| 1345 | Desperately Seeking Sorcha | 64,1006 (부관 이안) | 8 | root | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent root), port v31 rewards. |
| 1346 | Sorcha's Reckless Challenge | 64,1050 (사냥터 이동 관리인 하만) | 8 | 1345 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1345), port v31 rewards. |
| 1351 | Supply and Demand | 64,1006 (부관 이안) | 4 | 1329 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1329), port v31 rewards. |
| 1352 | Supply and Demand | 64,1006 (부관 이안) | 4 | 1329 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1329), port v31 rewards. |
| 1386 | Bombs Away | 64,1006 (부관 이안) | 4 | 1329 | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent 1329), port v31 rewards. |
| 1390 | Special Delivery | 213,1141 (정찰병 라사나) | 6 | root | a+ b+ c+ | gates a+b+c pass. Enable = replace prereq 99,99 (v17 parent root), port v31 rewards. |

## RESTORE+FIX (2)

| gid | title | giver (hz,tpl name) | lvl | v17 parent | gate a/b/c | action / justification |
|-----|-------|---------------------|-----|-----------|-----------|------------|
| 1322 | Unrest in the Forest | 213,1003 (하사관 케이샤) | 1 | root | a+ b+ c+ | dialog LinkCreature 13#300932 (Rotting Ghillie Dhu A) -> 13#300931 (task target, Dying Ghillie Dhu B, spawns 59x). Task side authoritative. Log divergence. |
| 1327 | Garrison in Distress | 213,1017 (연구원 카이몬) | 4 | 1324 | a+ b+ c+ | dialog LinkCreature 13#304 (Dying Argas, unspawned) -> 13#300921 (task target, Dying Argas B, spawns 48x). Task side authoritative. Separate cosmetic issue: English label 'sickly noruks' mismatches creature (no noruk template in zone 13); flag to string-fix owner. Log divergence. |

## ADAPT (15)

| gid | title | giver (hz,tpl name) | lvl | v17 parent | gate a/b/c | action / justification |
|-----|-------|---------------------|-----|-----------|-----------|------------|
| 1306 | Traces of Darkness | 213,1008 (리안 쿠벨) | 6 | 1305 | a+ b- c+ | add standing spawns: Eria Elin(213,1021) + Rian Kubel(213,1036) [gate b] |
| 1307 | Live by the Sword | 213,1008 (리안 쿠벨) | 7 | 1308 | a+ b- c- | add standing spawn Pelaeni(213,1027) [gate b] + habitat Dark Marauder(13,601) [gate c] |
| 1308 | Essence of Foreboding | 213,1021 (Eria Elin) | 7 | 1306 | a+ b- c- | add standing spawn Eria Elin(213,1021, giver) [gate b] + habitat Corrupted Earth Spirit A(13,3) [gate c] |
| 1310 | A Clue in the Dark | 213,1008 (리안 쿠벨) | 7 | 1309 | a+ b- c+ | add standing spawn Beres(213,1130) [gate b] |
| 1319 | Dwellers of the Island | 213,1110 (Muriel) | 2 | root | a+ b- c- | add standing spawn Muriel(213,1110, giver) [gate b] + habitat Nature Spirit Theron B/Chief(13,300941/300944) [gate c] |
| 1324 | Essence and Sensibility | 213,1017 (연구원 카이몬) | 2 | 1323 | a+ b+ c- | add habitat Dying Ghillie Dhu A / Rotting Ghillie Dhu B(13,300930/300933) [gate c] |
| 1332 | They'll Eat Anything | 213,1009 (Rabram) | 6 | root | a+ b- c- | add standing spawns Rabram(213,1009, giver) + Beres(213,1130) [gate b] + habitat Dying Argas A(13,300920) [gate c] |
| 1333 | Twice the Bark, Twice the Bite | 213,1130 (Beres) | 6 | 1332 | a+ b- c- | add standing spawn Beres(213,1130, giver) [gate b] + habitat Dying Chromos B(13,300911) [gate c] |
| 1334 | Investigating the Relics &lt;Repeatable&gt; | 213,1021 (Eria Elin) | 6 | root | a+ b- c+ | add standing spawn Eria Elin(213,1021, giver) [gate b]; ALSO collections-axis dep (collection 410) [cross-axis] |
| 1336 | Chione's Missing Cargo | 213,1007 (연락선 조종사 키오네) | 7 | 1335 | a+ b+ c+ | gates a/b/c pass; blocked on collections axis. 콜렉션Id 409 exists in v31 Collections.xml but must be ported to v92 before enable. Coordinate with collections-axis owner. |
| 1341 | Bequest of the Dead &lt;Repeatable&gt; | 213,1141 (정찰병 라사나) | 8 | root | a+ b+ c+ | gates a/b/c pass; blocked on collections axis. 콜렉션Id 411 exists in v31 Collections.xml but must be ported to v92 before enable. Coordinate with collections-axis owner. |
| 1347 | It Was a Rock...Crawler | 213,1128 (Mayer) | 6 | root | a+ b- c- | add standing spawn Mayer(213,1128, giver) [gate b] + habitat Stone Crawler B/Chief(13,300541/300542) [gate c] |
| 1348 | Ferocious Flowering Felons | 213,1147 (하사관 리야) | 5 | root | a+ b+ c- | add habitat Nature Spirit(13,302/303) [gate c] |
| 1349 | Gotta Kill 'Em All | 213,1126 (Eredos) | 7 | root | a+ b- c- | add standing spawn Eredos(213,1126, giver) [gate b] + habitat Okan Raider/Mini Okan(13,5/13,4) [gate c]. Mysterious Ruins (section 13003): the only quest of the ruins proper. |
| 1389 | Emptying Pandora's Box | 213,1020 (Theon) | 5 | root | a+ b- c+ | add standing spawn Theon(213,1020, giver) [gate b]. NOTE: '판도라 상자 사용 안내' = Pandora Box usage guide, a system/tutorial quest; flag to narrative-screen owner to confirm it belongs in classic IoD (candidate OUT on narrative grounds). |

## OUT (1)

| gid | title | giver (hz,tpl name) | lvl | v17 parent | gate a/b/c | action / justification |
|-----|-------|---------------------|-----|-----------|-----------|------------|
| 1385 | Always After Me Lucky Charms | 64,1049 (휴식 안내인 아르테미스) | 3 | 1384 | a+ b+ c+ | Superseded. patch-000 quest 1384 (Recharge It) already absorbs the charm flow (charm 70033). Prior ruling: do not re-enable. Gate data intact but policy = OUT. |

## Chain structure and partial-enable stranding

All 40 candidates carry prereq 99,99, so the intended chain wiring is recovered from the v17 prereq graph (pilot `v17-quests.json`). The **live v31/v92 spine deliberately re-parents around the disabled quests**: for example the story spine flows 1305 -> 1311 -> 1309 -> 1313 -> 1350 -> 1315 -> 1316 -> 1317, bypassing the disabled 1306/1307/1308/1310/1343 that sit on the original v17 line. Re-enabling a candidate therefore means giving it a real prereq; where its v17 parent is a live quest, anchor on that live quest, where the v17 parent is another disabled candidate, the two must enable together or the child strands with no way to start.

Key chains and stranding flags:

- **Story bridge 1306 -> 1308 -> 1307 (all ADAPT)**: the disabled link between live 1305 and live 1309. Enable as a unit anchored on live 1305; all three need Eria Elin/Pelaeni spawns plus mob habitats. 1307's v17 child 1309 is already live, so 1309 does not depend on 1307.
- **Courier branch 1309(live) -> 1310 -> 1335 -> 1337 -> 1338, plus 1335 -> 1336**: 1335, 1337, 1338 are gate-clean RESTORE but **cannot be enabled independently**: they sit behind 1310 (ADAPT, needs Beres 213,1130 spawn). Restore Beres's spawn (enable 1310) first, or the whole branch strands. 1336 (ADAPT-collections) also hangs off 1335.
- **Northern Checkpoint 1322(root) -> {1318, 1323 -> 1324 -> 1327}**: 1322 is RESTORE+FIX, 1318/1323 RESTORE. **1327 (RESTORE+FIX) sits behind 1324 (ADAPT, needs Ghillie Dhu 300930/300933 habitat)**: 1327 cannot enable until 1324's habitat exists. 1318 branches independently off 1322.
- **Gorge outpost 1315(live) -> 1343 -> 1344**: both RESTORE, anchor on live 1315. 1343 is a parallel branch (live 1316 is already parented on 1315), so **enabling 1343 collides with nothing and strands nothing** (no live or candidate quest lists 1343 as a prerequisite). Independent roots here: 1339 (anchor live 1313), 1340, 1341 (ADAPT-collections), 1390.
- **Tower supply 1329(live) -> {1351, 1352, 1386 -> 1328}**: all RESTORE, clean. Enable 1386 before 1328.
- **Sorcha 1345(root) -> 1346**: both RESTORE, clean unit (1346 turns in at dungeon HZ 437, npc 437,1001, which spawns).
- **Leander research 1332(root) -> 1333 (both ADAPT)**: enable as a unit (Rabram/Beres spawns + Argas A / Chromos B habitats).
- Independent single roots (no chain): 1302, 1321, 1325, 1326, 1330, 1312, 1319(ADAPT), 1334(ADAPT), 1347(ADAPT), 1348(ADAPT), 1349(ADAPT), 1389(ADAPT).

## Missing-entity roster (why gates b/c fail)

These v31 templates exist in NpcData but have **no standing spawn** in v31 TerritoryData, so the ported baseline lacks them. Re-adding them (placement referenced from v17) is the ADAPT work. None require inventing a template, only a spawn/habitat entry.

NPCs never spawned in v31 (hz 213):

| tpl | name | blocks quests |
|-----|------|---------------|
| 213,1009 | Rabram | 1332 |
| 213,1020 | Theon | 1389 |
| 213,1021 | Eria Elin | 1306, 1308, 1334 |
| 213,1027 | Pelaeni | 1307 |
| 213,1036 | Rian Kubel | 1306 |
| 213,1110 | Muriel | 1319 |
| 213,1126 | Eredos | 1349 |
| 213,1128 | Mayer | 1347 |
| 213,1130 | Beres | 1310, 1332, 1333 |

Mobs never spawned in v31 (hz 13):

| tpl | name | blocks quests |
|-----|------|---------------|
| 13,3 | Corrupted Earth Spirit A | 1308 |
| 13,4 | Mini Okan | 1349 |
| 13,5 | Okan Raider | 1349 |
| 13,302 | Nature Spirit | 1348 |
| 13,303 | Nature Spirit | 1348 |
| 13,601 | Dark Marauder | 1307 |
| 13,300541 | Stone Crawler B | 1347 |
| 13,300542 | Stone Crawler Chief | 1347 |
| 13,300911 | Dying Chromos B | 1333 |
| 13,300920 | Dying Argas A | 1332 |
| 13,300930 | Dying Ghillie Dhu A | 1324 |
| 13,300933 | Rotting Ghillie Dhu B | 1324 |
| 13,300941 | Nature Spirit Theron B | 1319 |
| 13,300944 | Nature Spirit Theron Chief | 1319 |

## Verified findings (from the brief)

- **1343 (Answers Lead to More Questions)**: giver Kiana (213,1025) spawns; data intact; gates a+b+c pass = RESTORE. No live or candidate quest lists 1343 as a prerequisite, and the live spine reparents 1316 onto 1315 directly, so 1343 slots back in as an optional branch off live 1315 (its v17 parent) with zero collision.
- **1322 / 1327 internal inconsistency (RESTORE+FIX)**. 1322: task hunts 13,300931 (Dying Ghillie Dhu B, spawns 59x); dialog LinkCreature points at 13,300932 (Rotting Ghillie Dhu A). Task side is authoritative; fix dialog to 300931. 1327: task hunts 13,300921 (Dying Argas B, spawns 48x); dialog LinkCreature 13#304 points at template 304 (Dying Argas, base, unspawned). Task side authoritative; fix dialog to 300921. The dialog's English label 'sickly noruks' is a separate cosmetic mislabel (no noruk template exists in zone 13).
- **1334 / 1336 / 1341 collections**: collection IDs 410 / 409 / 411 exist in v31 `Collections.xml`. 1336 and 1341 pass NPC/mob gates and are blocked only on porting these collections to v92 (collections axis, out of scope here) = ADAPT. 1334 additionally fails gate (b) on Eria Elin's spawn = ADAPT (spawn + collection).
- **1385 (Always After Me Lucky Charms) = OUT**. Confirmed superseded: patch-000 quest 1384 already carries the charm flow (charm item 70033). Do not re-enable.
- **v17-only quests: none.** Every v17 band quest (63) exists in v31 (65). v31 is a superset, adding 1379 (Gunner Training) and 1383 (Gathering Your Strength), both already live. The brief's suspected v17-only ids 1379/1389/1390 are all present in v31 (1379 live; 1389/1390 disabled-but-present). Doctrine rule 3 (no v17 story-quest porting) is moot.
