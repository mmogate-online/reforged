# IoD Dormant Systems Research (Padding Phase, Level 1 / WS7)

Analysis only. Inventories non-standard-quest content (repeatable, challenge, guide, event, dungeon-extra) that existed in the v17.11-era Island of Dawn and is dormant or absent in v31/v92, and answers triage question 1 for each lead: is it expressible in datasheets, and via which mechanism.

Sources: v17.11 client DataCenter (`D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA`), v31 server datasheet (`Z:\tera pserver\v31.04\...\Datasheet`), v92 live server datasheet (`D:\dev\mmogate\tera92\server\Datasheet`), domain quest-system and event-matching docs, pilot v17-quests catalog.

## Headline

All five named leads (plus 1345, the prerequisite of 1346) are present in BOTH v31 and v92, byte-similar and fully intact, soft-disabled by a single `99,99` sentinel prerequisite. Task bodies, repeatable flags, and reward compensation are all preserved (rewards are NOT reduced to empty stubs here, contrary to the general soft-disable pattern documented for the zone-13 story set). Every mechanism they use is expressible and has living, non-sentinel examples elsewhere in v92. Restoration for the simple cases is one operation: remove the sentinel prerequisite.

No dormant daily/reputation/guild/event system exists for the island: IoD sits below the level band where EventMatching (Vanguard), reputation dailies, and guild quests operate. Dungeon 436 (Karascha's Lair) has exactly one island quest touching it (1316, the story climax) in both v31 and v92, so it carries no dormant extra quest content.

## Mechanism Inventory

| Mechanism | Datasheet expression | Honored by v92? | Living v92 example (non-sentinel) |
|-----------|----------------------|-----------------|-----------------------------------|
| Repeatable quest | Header `<반복퀘스트>반복</반복퀘스트>` (category stays `일반`) | Yes | 22 active: 1540-1545 (zone 15), 6354 (zone 63), 102301-102306 (zone 1023), 469,1, 482,21 |
| Collect / gather task | Task `채집Task` with `<채집물지정><콜렉션Id>N</콜렉션Id>` + `<전달아이템지정>` quest item | Yes (task type documented, 2.6% of tasks) | Living repeatable collect quests in zone 1023 band |
| Guard / defend task | Task `수호Task` with `<던전Id>` (solo instance), `어그로주입간격초/수치`, `어그로전파범위uu`, `<제한시간>` | Yes (Guardian task type, 8 quests corpus-wide) | Guardian-task quests elsewhere; instance 437/9037 files exist in v92 |
| Condition task | Task `조건Task` with `<완료조건>` (item-use trigger) or empty (system-event) | Yes (2.1% of tasks) | Broadly used across zones |
| DeliverInjected task | Task `찔러준아이템전달Task` (server-injected virtual item turn-in) | Yes (2.7% of tasks) | Broadly used |
| Soft-disable / re-enable | Prerequisite `99,99` sentinel toggles offerability; removing it re-enables | Yes (publisher retirement mechanism, 84 files corpus-wide) | Any active quest lacking the sentinel |

Mechanisms that are NOT present for IoD (so nothing dormant to restore, not a gap):

- EventMatching / Vanguard daily-weekly wrapping: no `Event` entry references any 13xx quest (IoD is sub-level-20; the system begins around level 20+).
- Reputation dailies (`DailyQuest.xml`) and guild quests: no island wiring; the island predates faction and guild content.
- Timed field events / Dark Rift on the island: none in the v17 island band.

## Per-Lead Findings

Server state confirmed identical between v31 and v92 for every row unless noted. "Rewards" = `QuestCompensationData_13.xml` entry, confirmed populated (not stubbed).

| Quest | Title | v17 type / tasks | Server body (v31 & v92) | Dependencies for a live restore | Verdict |
|-------|-------|------------------|-------------------------|--------------------------------|---------|
| 1334 | Investigating the Relics `<Repeatable>` | Repeatable, Collect (콜렉션 404, deliver item 9011x5) to Eria 213,1021, lvl 6-10 | `반복퀘스트=반복`, sentinel `99,99`, rewards 800xp/80g | Collection node 404 must spawn in-world (not currently placed in zone 13/213 territory); giver 213,1021 defined but not seen in TerritoryData_213 | EXPRESSIBLE |
| 1341 | Bequest of the Dead `<Repeatable>` | Repeatable, Collect (콜렉션 411, deliver item 9012x5) to Fili 213,1141, lvl 8-12 | `반복퀘스트=반복`, sentinel `99,99`, rewards 1500xp + charms 7100/7104/7108 | Collection node 411 must spawn; giver 213,1141 defined AND spawned in TerritoryData_213 | EXPRESSIBLE |
| 1345 | Desperately Seeking Sorscha | One-time, Visit > Visit, giver 64,1006, lvl 8 | `1회성`, sentinel `99,99`, rewards 500xp/50g + Speed Potion 8007 | Giver 64,1006 defined AND spawned; target 64,1050 defined AND spawned | EXPRESSIBLE (prereq of 1346) |
| 1346 | Sorcha's Reckless Challenge | One-time challenge, Guard(437,1001 in solo instance) > Visit > Visit, giver 64,1050, prereq 13,45, lvl 8+ | `1회성`, sentinel `99,99`, `던전Id=9037`, aggro 1/3s/2000uu, time limit `0,7`, rewards 6000xp/600g | Solo instance 437/9037 must be reachable (NpcData_437, TerritoryData_437, DynamicSpawn_437 all exist; entry/teleport wiring must be verified live); guard NPC 437,1001 defined AND spawned | EXPRESSIBLE, higher effort (instanced defend) |
| 1389 | Pandora box use guide (판도라 상자 사용 안내) | One-time guide, Visit > Condition(empty=system event) > Visit, giver 213,1020, lvl 5 | `1회성`, sentinel `99,99`, rewards 200xp | Title/journal strings are Korean in the client (localization status to verify); box mechanic the guide teaches must exist; giver 213,1020 defined but not seen in TerritoryData_213 | EXPRESSIBLE, low value (untranslated tutorial) |
| 1390 | Special Delivery | One-time, Condition(use item 160 x1) > Visit(64,1050) > DeliverInjected(213,1141 / 213,1130), lvl 6-12 | `1회성`, sentinel `99,99`, rewards 300xp + 2x item 160 | Item 160 = Safe Haven Teleport Scroll (exists, obtainable); giver 213,1130 defined but not seen in TerritoryData_213 | EXPRESSIBLE |

Notes:
- Item existence confirmed in v92: 160 (Safe Haven Teleport Scroll), 9011 (Inscribed Fragment / quest_collection_10), 9012 (Expedition Amulet / quest_collection_11), 7100/7104/7108 (charms), 8007 (Speed Potion).
- "Not seen in TerritoryData" givers may still spawn via another mechanism (DynamicSpawn, WorldSpawn, or quest appear-gating); giver spawn presence overlaps the spawn/habitat workstream and is not a quest-file concern. Every giver template is DEFINED in v92 NpcData, so no quest points at a missing NPC.
- The collection-node placement for 1334/1341 (콜렉션 404/411) is the one genuine content dependency outside the quest file: it is a gathering-spawn concern and should be handed to the spawn/habitat workstream.

## Dungeon 436 (Karascha's Lair)

Only quest 1316 (Dark Revelations, the island story climax) references zone 436/9036, and this holds in both v31 and v92. There is no additional dormant island quest tied to the dungeon, and no repeatable/challenge/event content around it. Nothing to restore beyond the story quest already in the baseline plan.

## Other Dormant Island Systems (bounded scan)

- Guild quests: none on the island.
- Gathering dailies / reputation dailies: none wired for IoD.
- Achievements / exploration triggers tied to IoD sections: not surfaced in the quest or event data; out of the level band. Not pursued further (leads take priority per task scope).

## Recommendations (ordered by value / effort)

1. Re-enable the repeatable pair 1334 + 1341 (remove `99,99` sentinel each). Highest value: adds the only repeatable content loop the classic island had, and rewards are already intact. Blocking dependency: place collection nodes 404 and 411 in the correct island sections (route to the spawn/habitat workstream). Do not re-enable before the nodes exist, or the quests are un-completable.
2. Re-enable the 1345 -> 1346 challenge chain (remove sentinel on both). Medium value (a signature timed defend challenge). 1345 is trivial (deps met). 1346 needs a live check that solo instance 9037/437 is reachable and its defend encounter spawns; treat as medium/high effort and verify in-game before shipping.
3. Re-enable 1390 Special Delivery (remove sentinel). Low/medium value, low effort: all item and NPC dependencies exist; confirm giver 213,1130 spawns.
4. Defer 1389 Pandora box guide. Lowest value (a tutorial popup) and its strings are Korean in the client; verify localization and that the box mechanic it teaches still exists before spending effort. Restore last, if at all.
