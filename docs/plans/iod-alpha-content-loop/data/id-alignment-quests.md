# Quest-ID alignment (Island of Dawn)

Cross-source check of the 63 v17 roster quests against v31 and v92 `QuestData`, with story-group membership and disable-state.

Title-resolution path: the server `.quest` files carry only a title *ref* (`@quest:<questId*1000+1>`), identical by construction because the questId is identical; the English title lives in client StrSheet_Quest. The v17 title (old client) is compared to the v92 client title for the same questId.

## Counts

| Classification | Count |
|---|---|
| ALIGNED | 63 |
| RENAMED | 0 |
| MISSING_IN_V31 | 0 |
| MISSING_IN_V92 | 0 |
| EXTRA_V31 | 2 |
| EXTRA_V92 | 2 |

- v17 roster quests: 63
- quest-zone-13 quests (Quest번호 hz=13): v31=65, v92=65
- story-group membership identical v31 vs v92: yes
- sentinel-disabled 13xx band quests: v31=40, v92=40

## RENAMED / MISSING / EXTRA rows (id landmines)

RENAMED here means genuine id reuse: the same questId pointing at a different title-ref (`title*1000+1`) or story group in v31 vs v92. `EXTRA_*` rows are server band quests absent from the v17 roster (see REMOVE candidates below).

| questId | class | signals | v17 title | v92 client title | v31 sg | v92 sg | v31 disabled | v92 disabled |
|---|---|---|---|---|---|---|---|---|
| 1379 | EXTRA_V31+EXTRA_V92 | - |  | Gunner Training | 1 | 1 | no | no |
| 1383 | EXTRA_V31+EXTRA_V92 | - |  | Gathering Your Strength | 1 | 1 | no | no |

## Informational drift (NOT id landmines)

These questIds are ALIGNED: the id and its title-ref are stable across v31 and v92. `TITLE_EN_DRIFT` is a client English title revised across region/patch (the questId still resolves the title from whichever client ships). `STORYGROUP_MEMBERSHIP_DRIFT` is a v17-roster-vs-server QuestGroupList registration difference (v31 and v92 agree with each other); it drives quest_restore story-group wiring, not id keying.

| questId | drift | v17 title | v92 client title | v17 sg | v31 sg | v92 sg |
|---|---|---|---|---|---|---|
| 1301 | TITLE_EN_DRIFT | Dawn's Early Light | Dawn's Twilight | 1 | 1 | 1 |
| 1305 | TITLE_EN_DRIFT | Elleon's Fate | A Clue in the Dark | 1 | 1 | 1 |
| 1306 | STORYGROUP_MEMBERSHIP_DRIFT | Traces of Darkness | Traces of Darkness | 1 | - | - |
| 1307 | STORYGROUP_MEMBERSHIP_DRIFT | Live by the Sword... | Live by the Sword | 1 | - | - |
| 1308 | STORYGROUP_MEMBERSHIP_DRIFT | Essence of Foreboding | Essence of Foreboding | 1 | - | - |
| 1309 | STORYGROUP_MEMBERSHIP_DRIFT | Acharak Attacks | Acharak Attacks | 1 | 2 | 2 |
| 1310 | STORYGROUP_MEMBERSHIP_DRIFT | A Clue In the Dark | A Clue in the Dark | 1 | - | - |
| 1311 | TITLE_EN_DRIFT | Clearing the Gorge | Redeployment | 2 | 2 | 2 |
| 1329 | STORYGROUP_MEMBERSHIP_DRIFT | Going Above and Beyond | Going Above and Beyond | - | 1 | 1 |
| 1331 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | I'll Take the High Road | Climbing through the Ranks | - | 1 | 1 |
| 1337 | TITLE_EN_DRIFT | Searching for the Stolen Stones | The Last One | - | - | - |
| 1343 | STORYGROUP_MEMBERSHIP_DRIFT | Answers Lead to More Questions | Answers Lead to More Questions | 2 | - | - |
| 1345 | TITLE_EN_DRIFT | Desperately Seeking Sorscha | Desperately Seeking Sorcha | - | - | - |
| 1371 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Initial Warrior Training | Warrior Training | - | 1 | 1 |
| 1372 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Initial Lancer Training | Lancer Training | - | 1 | 1 |
| 1373 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Initial Slayer Training | Slayer Training | - | 1 | 1 |
| 1374 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Initial Berserker Training | Berserker Training | - | 1 | 1 |
| 1375 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Initial Archer Training | Archer Training | - | 1 | 1 |
| 1376 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Initial Sorcerer Training | Sorcerer Training | - | 1 | 1 |
| 1377 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Initial Priest Training | Priest Training | - | 1 | 1 |
| 1378 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Initial Mystic Training | Mystic Training | - | 1 | 1 |
| 1382 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Introduction to Gathering | Gathering Your Strength | - | 1 | 1 |
| 1384 | TITLE_EN_DRIFT,STORYGROUP_MEMBERSHIP_DRIFT | Recharge It | Getting to Know the Garrison | - | 1 | 1 |
| 1389 | TITLE_EN_DRIFT | 판도라 상자 사용 안내 | Emptying Pandora's Box | - | - | - |

## REMOVE candidates: quest-zone-13 quests in v92 baseline absent from v17

Disable convention: a quest is soft-disabled by writing the single sentinel prerequisite `<퀘스트Id>99,99</퀘스트Id>` (quest 99,99 does not exist, so the requirement can never be met and the quest never offers). No other disable convention was found in the 13xx band: min/max level bands are all real (1-12), and both servers carry an identical disabled set.

| questId | quest-zone | local | v92 title | enabled | sentinel-disabled | v92 prereqs | in v31 |
|---|---|---|---|---|---|---|---|
| 1379 | 13 | 79 | Gunner Training | yes | no | 13,04 | yes |
| 1383 | 13 | 83 | Gathering Your Strength | yes | no | 13,84 | yes |
