# IoD First Expedition Set: Acquisition Audit

Research only. No datasheet modified. Answers the user's claim that some Island of Dawn quests rewarded a complete "First Expedition" gear set (leather chest "Cuirass of the First Expedition", item 15022), which the earlier reward audit reported missing.

Sources:
- v92 (live): `D:\dev\mmogate\tera92\server\Datasheet` (StrSheet_Item, CompensationData, QuestData, QuestCompensationData_13.xml, _599.xml)
- v31: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet` (same)
- v17 index: `reforged\docs\plans\iod-alpha-content-loop\data\v17-quests.json`

## Verdict on the user's claim: CONFIRMED

The First Expedition set IS quest-granted on Island of Dawn, in BOTH v31 and live v92, identically. The Cuirass of the First Expedition (15022, leather body) and every other piece are handed out by two STORY quests in hunting zone 13:

- **Quest 1305 "A Clue in the Dark" (min level 5)** grants the COMPLETE set: all 12 class weapons + all 3 body + all 3 hand + all 3 feet pieces (compensation, itemBag=class). This is the full-set quest.
- **Quest 1310 "A Clue in the Dark" (min level 7)** grants the 12 class weapons + the 3 body pieces (15019/15022/15025) only.

Both are present and active on live (`QuestCompensationData_13.xml`, quests 1305 lines 235-261 and 1310 lines 306-326; v31 lines 284-325 and 370-393). v31 and v92 payloads are byte-equivalent in content (v92 just consolidated per-class rows into semicolon groups and added the fighter/assassin/glaiver rows).

## Why the earlier reward audit missed the body pieces

The reward audit (`padding-reward-audit.md`) scanned only the **34 enabled SIDE quests** and their `QuestCompensationData_13` rows. Quests 1305 and 1310 are **story-spine quests**, not side quests, so they fell outside that audit's set. The audit's own story-baseline table did list "1305 | full set: body i7, feet i7, hand i7, weapon i7" but did not name it "First Expedition" and did not list 1310 at all. So the audit's statement "no SIDE quest grants a body piece" is literally true, but the derived impression that the First Expedition body is unobtainable from IoD quests is false. The live server is NOT missing the body pieces; they are on the story quest.

## Set roster (ids, all rareGrade 0 common, level 7 / requiredLevel 7)

Internal names confirm this is the single ilvl17 tier (`mail17`/`leather17`/`robe17`, `*_01` weapons), not a mix of item-levels.

Armor (9 pieces, 3 armor classes x 3 slots):

| id | display name | internal | slot | armor class | classes (v92 bag) |
|---|---|---|---|---|---|
| 15019 | Hauberk of the First Expedition | mail17_body | body | mail | lancer;berserker;engineer;fighter |
| 15020 | Gauntlets of the First Expedition | mail17_hand | hand | mail | lancer;berserker;engineer;fighter |
| 15021 | Greaves of the First Expedition | mail17_feet | feet | mail | lancer;berserker;engineer;fighter |
| 15022 | Cuirass of the First Expedition | leather17_body | body | leather | warrior;slayer;archer;glaiver |
| 15023 | Gloves of the First Expedition | leather17_hand | hand | leather | warrior;slayer;archer;glaiver |
| 15024 | Boots of the First Expedition | leather17_feet | feet | leather | warrior;slayer;archer;glaiver |
| 15025 | Robe of the First Expedition | robe17_body | body | robe | sorcerer;priest;elementalist;assassin |
| 15026 | Sleeves of the First Expedition | robe17_hand | hand | robe | sorcerer;priest;elementalist;assassin |
| 15027 | Shoes of the First Expedition | robe17_feet | feet | robe | sorcerer;priest;elementalist;assassin |

Weapons (12, one per class; `*_01` starter weapons):

| id | display name | class | id | display name | class |
|---|---|---|---|---|---|
| 10017 | Twin Swords | warrior | 10023 | Staff | priest |
| 10018 | Lance | lancer | 10024 | Scepter | elementalist |
| 10019 | Greatsword | slayer | 55007 | Arcannon | engineer (gunner) |
| 10020 | Axe | berserker | 58173 | Shuriken | assassin (ninja) |
| 10021 | Disc | sorcerer | 59055 | Runeglaive | glaiver (valkyrie) |
| 10022 | Bow | archer | 82007 | Powerfists | fighter (brawler) |

Reaper (soulless) and gunner-proper have no First Expedition armor bag row; reaper has no weapon either (known "Reaper has no low-level gear" fact). v92 also carries costume/skin clones (200531/200552/200573 and 200594+ weapon skins) that are cosmetics, not quest gear.

## Per-piece per-era acquisition table

| piece(s) | v31 | v92 (live) | v17.11 | mechanism |
|---|---|---|---|---|
| full set (wep+body+hand+feet) | quest 1305 | quest 1305 | NOT on 1305 (see note) | QuestCompensationData_13, itemBag=class |
| weapons + 3 body (15019/22/25) | quest 1310 | quest 1310 | NOT on 1310 (empty reward) | QuestCompensationData_13, itemBag=class |
| 3 feet (15021/24/27) | quest 1326 | quest 1326 | consumables (no gear) | side quest, feet only |
| 3 hand (15020/23/26) | quest 1330 | quest 1330 | event item (no gear) | side quest, hand only |
| all 9 armor | ECompensation_13 drop (prob 1/3 each) | NOT present (v92 dropped it) | n/a | v31 random drop/box in zone 13 |
| full set (level-60 relaunch) | n/a | quests in zone 599/605 (`QuestCompensationData_599`, level-60 IoD) | n/a | out of scope for classic 1-11 restoration |

Evidence lines:
- v92 1305: `QuestCompensationData_13.xml:237-258` (exp 4900, itemBag=class, weapons + 15019-15027 + 82007/58173/59055).
- v92 1310: `QuestCompensationData_13.xml:308-323` (exp 1000, weapons + 15019/15022/15025).
- v31 1305: `QuestCompensationData_13.xml:286-322`. v31 1310: `370-389` (per-class rows, same items).
- v31 non-quest drop: `ECompensation_13.xml:173-185` grants all 9 armor pieces at probability 0.333 each (Korean names "쿠벨 탐험대의..." = Kubel Expedition). v92 has no matching ECompensation armor rows.

Note on v17: the v17 index quest numbering diverges from v31/v92. v17 1305 is titled "Elleon's Fate" with 17710/17713-family armor rewards; v17 1310 "A Clue In the Dark" pays exp/gold only. So the v17.11 client did NOT grant the First Expedition set through these ids. This is expected: the v17 client reorganized IoD. Per the v31-primary doctrine, v31 is the authoritative classic source and it grants the set on 1305/1310.

## Relation to the 7-9 band gap and padding

The earlier gap analysis (no side quest grants body, no side-quest gear in the level 7-9 band) stands as written FOR SIDE QUESTS. But the body slot and the 7-9 band are already covered by the STORY spine:
- 1305 (level 5) = full First Expedition set including leather/mail/robe body.
- 1310 (level 7) = weapons + 3 body pieces, squarely in the 7-9 band.
- 1315 (level 9) continues with body i8.

So on a played story path a character already receives a First Expedition body at level 5 and again at level 7. There is no missing body-slot source on live.

## Faithful-restoration options

1. **No action needed for authenticity (recommended).** The First Expedition set is already granted era-faithfully by story quests 1305 and 1310, identical to v31. Nothing was stripped. The user's memory is correct and the live data already honors it.
2. **If the padding goal is "collect the set through SIDE quests":** that is a NEW design, not a restoration. In v31 the set was concentrated on the story spine (1305/1310) plus a random zone-13 drop (ECompensation_13), never spread across the side quests. Spreading body pieces onto side quests belongs in patch 002 (customization), not classic restoration.
3. **Optional era-faithful extra:** v31 also dropped the 9 armor pieces via `ECompensation_13` (1/3 probability each) in zone 13; v92 dropped that table. Restoring that drop would re-add a non-quest acquisition path that existed in v31, if a broader drop-economy restoration is wanted. Keep separate from the quest work.

Action item to verify before relying on this in-game: confirm quests 1305 and 1310 are reachable/enabled on the current live server (both have quest files `001305.quest` min level 5 and `001310.quest` min level 7, and live compensation rows, so they are wired; a live QA run would confirm the story chain is not gated off).
