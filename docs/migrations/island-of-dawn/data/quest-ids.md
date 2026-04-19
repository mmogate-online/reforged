# Island of Dawn — Quest File Mapping (v31 vs v92)

Source: v31/v92 filesystem inspection + MCP quest data

## Quest File Existence

All 65 quest files exist in both v31 and v92. Filenames are 6-digit zero-padded with `.quest` extension.

| questId | filename | exists_v31 | exists_v92 | group |
|---------|----------|------------|------------|-------|
| 1301 | 001301.quest | yes | yes | story_1 |
| 1303 | 001303.quest | yes | yes | story_1 |
| 1304 | 001304.quest | yes | yes | story_1 |
| 1305 | 001305.quest | yes | yes | story_1 |
| 1329 | 001329.quest | yes | yes | story_1 |
| 1331 | 001331.quest | yes | yes | story_1 |
| 1371 | 001371.quest | yes | yes | story_1 |
| 1372 | 001372.quest | yes | yes | story_1 |
| 1373 | 001373.quest | yes | yes | story_1 |
| 1374 | 001374.quest | yes | yes | story_1 |
| 1375 | 001375.quest | yes | yes | story_1 |
| 1376 | 001376.quest | yes | yes | story_1 |
| 1377 | 001377.quest | yes | yes | story_1 |
| 1378 | 001378.quest | yes | yes | story_1 |
| 1379 | 001379.quest | yes | yes | story_1 |
| 1382 | 001382.quest | yes | yes | story_1 |
| 1383 | 001383.quest | yes | yes | story_1 |
| 1384 | 001384.quest | yes | yes | story_1 |
| 1309 | 001309.quest | yes | yes | story_2 |
| 1311 | 001311.quest | yes | yes | story_2 |
| 1313 | 001313.quest | yes | yes | story_2 |
| 1315 | 001315.quest | yes | yes | story_2 |
| 1316 | 001316.quest | yes | yes | story_2 |
| 1317 | 001317.quest | yes | yes | story_2 |
| 1350 | 001350.quest | yes | yes | story_2 |
| 1302 | 001302.quest | yes | yes | side_213 |
| 1306 | 001306.quest | yes | yes | side_213 |
| 1307 | 001307.quest | yes | yes | side_213 |
| 1308 | 001308.quest | yes | yes | side_213 |
| 1385 | 001385.quest | yes | yes | side_213 |
| 1386 | 001386.quest | yes | yes | side_213 |
| 1389 | 001389.quest | yes | yes | side_213 |
| 1310 | 001310.quest | yes | yes | side_64 |
| 1312 | 001312.quest | yes | yes | side_64 |
| 1321 | 001321.quest | yes | yes | side_64 |
| 1322 | 001322.quest | yes | yes | side_64 |
| 1327 | 001327.quest | yes | yes | side_64 |
| 1330 | 001330.quest | yes | yes | side_64 |
| 1335 | 001335.quest | yes | yes | side_64 |
| 1338 | 001338.quest | yes | yes | side_64 |
| 1340 | 001340.quest | yes | yes | side_64 |
| 1344 | 001344.quest | yes | yes | side_64 |
| 1345 | 001345.quest | yes | yes | side_64 |
| 1346 | 001346.quest | yes | yes | side_64 |
| 1349 | 001349.quest | yes | yes | side_64 |
| 1351 | 001351.quest | yes | yes | side_64 |
| 1352 | 001352.quest | yes | yes | side_64 |
| 1390 | 001390.quest | yes | yes | side_64 |
| 1339 | 001339.quest | yes | yes | zoneless |
| 41501 | 041501.quest | yes | yes | prologue_415 |
| 41502 | 041502.quest | yes | yes | prologue_415 |
| 41503 | 041503.quest | yes | yes | prologue_415 |
| 41504 | 041504.quest | yes | yes | prologue_415 |
| 41505 | 041505.quest | yes | yes | prologue_415 |
| 41506 | 041506.quest | yes | yes | prologue_415 |
| 41507 | 041507.quest | yes | yes | prologue_415 |
| 41508 | 041508.quest | yes | yes | prologue_415 |
| 41510 | 041510.quest | yes | yes | prologue_416 |
| 41511 | 041511.quest | yes | yes | prologue_416 |
| 41512 | 041512.quest | yes | yes | prologue_416 |
| 41513 | 041513.quest | yes | yes | prologue_416 |
| 41514 | 041514.quest | yes | yes | prologue_416 |
| 41515 | 041515.quest | yes | yes | prologue_416 |
| 41516 | 041516.quest | yes | yes | prologue_416 |
| 41517 | 041517.quest | yes | yes | prologue_416 |

**Result: All 65 quest files present in both v31 and v92. Zero missing.**

## QuestDialog File Mapping

v31 naming: `QuestDialog_{zone}_{local}.xml` (zone-partitioned)
v92 naming: `QuestDialog_{questId}.xml` (flat per-quest)

### IoD quests (49 files, zone 13 in v31)

| questId | v31 file | v92 file |
|---------|----------|----------|
| 1301 | QuestDialog_13_1.xml | QuestDialog_1301.xml |
| 1302 | QuestDialog_13_2.xml | QuestDialog_1302.xml |
| 1303 | QuestDialog_13_3.xml | QuestDialog_1303.xml |
| 1304 | QuestDialog_13_4.xml | QuestDialog_1304.xml |
| 1305 | QuestDialog_13_5.xml | QuestDialog_1305.xml |
| 1306 | QuestDialog_13_6.xml | QuestDialog_1306.xml |
| 1307 | QuestDialog_13_7.xml | QuestDialog_1307.xml |
| 1308 | QuestDialog_13_8.xml | QuestDialog_1308.xml |
| 1309 | QuestDialog_13_9.xml | QuestDialog_1309.xml |
| 1310 | QuestDialog_13_10.xml | QuestDialog_1310.xml |
| 1311 | QuestDialog_13_11.xml | QuestDialog_1311.xml |
| 1312 | QuestDialog_13_12.xml | QuestDialog_1312.xml |
| 1313 | QuestDialog_13_13.xml | QuestDialog_1313.xml |
| 1315 | QuestDialog_13_15.xml | QuestDialog_1315.xml |
| 1316 | QuestDialog_13_16.xml | QuestDialog_1316.xml |
| 1317 | QuestDialog_13_17.xml | QuestDialog_1317.xml |
| 1321 | QuestDialog_13_21.xml | QuestDialog_1321.xml |
| 1322 | QuestDialog_13_22.xml | QuestDialog_1322.xml |
| 1327 | QuestDialog_13_27.xml | QuestDialog_1327.xml |
| 1329 | QuestDialog_13_29.xml | QuestDialog_1329.xml |
| 1330 | QuestDialog_13_30.xml | QuestDialog_1330.xml |
| 1331 | QuestDialog_13_31.xml | QuestDialog_1331.xml |
| 1335 | QuestDialog_13_35.xml | QuestDialog_1335.xml |
| 1338 | QuestDialog_13_38.xml | QuestDialog_1338.xml |
| 1339 | QuestDialog_13_39.xml | QuestDialog_1339.xml |
| 1340 | QuestDialog_13_40.xml | QuestDialog_1340.xml |
| 1344 | QuestDialog_13_44.xml | QuestDialog_1344.xml |
| 1345 | QuestDialog_13_45.xml | QuestDialog_1345.xml |
| 1346 | QuestDialog_13_46.xml | QuestDialog_1346.xml |
| 1349 | QuestDialog_13_49.xml | QuestDialog_1349.xml |
| 1350 | QuestDialog_13_50.xml | QuestDialog_1350.xml |
| 1351 | QuestDialog_13_51.xml | QuestDialog_1351.xml |
| 1352 | QuestDialog_13_52.xml | QuestDialog_1352.xml |
| 1371 | QuestDialog_13_71.xml | QuestDialog_1371.xml |
| 1372 | QuestDialog_13_72.xml | QuestDialog_1372.xml |
| 1373 | QuestDialog_13_73.xml | QuestDialog_1373.xml |
| 1374 | QuestDialog_13_74.xml | QuestDialog_1374.xml |
| 1375 | QuestDialog_13_75.xml | QuestDialog_1375.xml |
| 1376 | QuestDialog_13_76.xml | QuestDialog_1376.xml |
| 1377 | QuestDialog_13_77.xml | QuestDialog_1377.xml |
| 1378 | QuestDialog_13_78.xml | QuestDialog_1378.xml |
| 1379 | QuestDialog_13_79.xml | QuestDialog_1379.xml |
| 1382 | QuestDialog_13_82.xml | QuestDialog_1382.xml |
| 1383 | QuestDialog_13_83.xml | QuestDialog_1383.xml |
| 1384 | QuestDialog_13_84.xml | QuestDialog_1384.xml |
| 1385 | QuestDialog_13_85.xml | QuestDialog_1385.xml |
| 1386 | QuestDialog_13_86.xml | QuestDialog_1386.xml |
| 1389 | QuestDialog_13_89.xml | QuestDialog_1389.xml |
| 1390 | QuestDialog_13_90.xml | QuestDialog_1390.xml |

### Prologue quests (16 files, zone 415 in v31)

All prologue quests (both 415xx and 416xx) use zone 415 in v31 internal representation.

| questId | v31 file | v92 file |
|---------|----------|----------|
| 41501 | QuestDialog_415_1.xml | QuestDialog_41501.xml |
| 41502 | QuestDialog_415_2.xml | QuestDialog_41502.xml |
| 41503 | QuestDialog_415_3.xml | QuestDialog_41503.xml |
| 41504 | QuestDialog_415_4.xml | QuestDialog_41504.xml |
| 41505 | QuestDialog_415_5.xml | QuestDialog_41505.xml |
| 41506 | QuestDialog_415_6.xml | QuestDialog_41506.xml |
| 41507 | QuestDialog_415_7.xml | QuestDialog_41507.xml |
| 41508 | QuestDialog_415_8.xml | QuestDialog_41508.xml |
| 41510 | QuestDialog_415_10.xml | QuestDialog_41510.xml |
| 41511 | QuestDialog_415_11.xml | QuestDialog_41511.xml |
| 41512 | QuestDialog_415_12.xml | QuestDialog_41512.xml |
| 41513 | QuestDialog_415_13.xml | QuestDialog_41513.xml |
| 41514 | QuestDialog_415_14.xml | QuestDialog_41514.xml |
| 41515 | QuestDialog_415_15.xml | QuestDialog_41515.xml |
| 41516 | QuestDialog_415_16.xml | QuestDialog_41516.xml |
| 41517 | QuestDialog_415_17.xml | QuestDialog_41517.xml |

**Result: All 65 QuestDialog files present in both versions. Zero missing.**

## QuestCompensationData

All 65 IoD quests reference only two compensation IDs:
- **ID 0**: Null sentinel (file does not exist). Means "no reward" for intermediate steps.
- **ID 1**: `QuestCompensationData_1.xml` — empty placeholder, exists in both versions.

**No QuestCompensationData files need to be copied.**

## Key Observations

- All 65 quest files exist in both versions — this is a pure overwrite operation
- QuestDialog naming differs (v31 zone-partitioned vs v92 flat) — copy from v31, rename to v92 convention
- No QuestCompensationData files need migration — quest rewards are in the .quest files
- v31 has no `QuestDialog_416_*.xml` files — all prologue dialogs are under zone 415
