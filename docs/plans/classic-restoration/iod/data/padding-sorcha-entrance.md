# Sorcha's Reckless Challenge (quest 1346) - Dungeon Entrance Analysis

> CORRECTION 2026-07-21 (post-deploy live finding): the "guard-task auto-entry, no portal
> needed" verdict in this doc (section "Entry mechanism verdict") is REFUTED. The user could not
> enter after spec 19 deployed. A full survey showed a bare 수호Task never teleports the player
> in; 1346 is the ONLY quest whose dungeon-carrying task is the START task; every functioning
> instance is entered through a PHYSICAL PORTAL; and 1346 was 99,99-disabled in v31 so no working
> entrance exists in any source. Fix shipped: authored work object 134 (Black Rift portal) gated
> to quest 1346 task 1, placed in HZ 13 at 57908,-67648,-5097 (the v92 StrSheet_WorkObjectLoc
> position of the 21307 portal), teleport 642501 -> 9037. See spec 19 ENTRANCE PORTAL companion
> note, the divergence log, and docs/dsl-requests/2026-07-21-workobject-entity.md. The domain doc
> "Quest-task auto-entry" section was derived from this refuted analysis and needs the same fix.

Analysis and fix proposal only. No spec or datasheet changes made.

## Question

Quest 1346 is re-enabled on v92. Its guard task runs in solo instance dungeon 437
(continent 9037, "Tainted Gorge Bridge"). Players report there is no way to enter the
instance. How is dungeon entry expressed, what did the classic era have, what is v92
missing, and what is the exact fix (while keeping the existing Tainted Gorge quick-travel
teleports)?

## Quest 1346 shape (unchanged between v31 and v92)

`QuestData/001346.quest`:

- Giver 64,1050 (camp teleport master), min level 8, connects to next quest 1,1.
- Task 1 `수호Task` (Guardian): `던전Id 9037`, defend NPC `437,1001` (Sorcha), time limit
  0:07, aggro pulse 1 / 3s / 2000uu.
- Task 2 `방문Task`: talk to `437,1001` (Sorcha, inside the instance).
- Task 3 `방문Task`: talk to `64,1006` back in the IoD camp (reward turn-in).

The only difference in v92 is the prerequisite: v31 carries the soft-disable sentinel
`99,99`; v92 carries the real prerequisite `13,45`. So the padding phase already
re-enabled the quest. Sorcha herself (`NpcData_437` id 1001, "견습 마녀" / Apprentice
Witch, `playStyle="zarcoBoss"`, `villager="true"`) still exists in v92, and her wave
territories (`TerritoryData_437` ids 43700322 through 43700363) are fully intact.

## Entry mechanism verdict: guard-task auto-entry, NOT a teleport menu

The `던전Id` on the first quest task that carries one auto-teleports the player into that
instance; the player lands at the `DungeonData` `startPos` and is returned to `exitPos`.
Admission is gated by the `DungeonData` `<Condition>` elements. Evidence:

- Quest 1346 task 1 is the first task and carries `던전Id 9037`; there is no preceding
  MoveToPC/portal step. The dungeon defines `startPos`, `exitContinentId=13`, `exitPos`,
  and (in v31) a `questFail` EventGroup that teleports the player back to continent 13.
  This is an auto-in / auto-out solo instance, not a walk-in portal.
- Reference guard quest 401 (dungeon 9003): its guard task (task 9) is preceded by a
  `PC이동Task` (task 7) that carries the same `던전Id 9003`. The first task with a
  `던전Id` is what puts the player inside; later same-dungeon tasks just run objectives
  within it.
- Domain docs (`reference/quest-task-reference.md`, Guardian): DungeonId is required and
  the task is "always inside a dungeon."
- v31 `DungeonData_9037` gates entry with `Condition type="progressQuest" value="1346"
  taskId="1"` plus `levelOver 8` - a quest-progress admission gate, consistent with
  engine auto-entry, not with a manually-clicked portal.

Consequence: the fix needs NO teleport-menu or portal wiring. The camp teleport master
64,1050 (`VillagerMenu Menu type="CampTeleport" id="1"`, the open-world quick-travel the
user wants to keep) is unrelated to instance entry and must be left untouched. The
"teleportal only offers quick-travel, no instance entry" symptom is exactly what a blocked
auto-entry looks like: the level-8 player reaches task 1, the engine tries to auto-enter
9037, and the current `levelOver 65` entry condition rejects them, so nothing happens.

(There are two vestigial teleport rows into 9037: NPC `64,2501` -> `VillagerMenu Teleport
id=642501` -> `TeleportList 642501` -> continent 9037 at the v31 startPos, present in both
eras but 64,2501 is not placed in `TerritoryData_64` in either era; and the modern
`WorkObject templateId=125` -> `teleportId 4371001` -> 9037, which is `isForQuestId=21307`
only. Neither is the classic 1346 entrance.)

## What v92 is actually missing: continent 9037 was repurposed

`DungeonData_9037.xml` is the whole story. In v31 it is the live Sorcha guard dungeon. In
v92 the entire 1346 block is commented out (lines 3-81) and the continent has been
rebuilt for a different, non-classic quest 21307 ("여명의 정원" / Garden of Dawn, level 65):

| Aspect | v31 (classic) | v92 (current) |
|--------|---------------|---------------|
| Active entry conditions | party, `levelOver 8`, `progressQuest 1346 taskId 1`, `completeQuest 1346`, `maxMemberCount 5` | `solo`, `levelOver 65`, `maxMemberCount 1` |
| Sorcha spawn scripting | active `talkNpc uniqueId="437,1001"` group (wave spawns + 420s timer) | commented out |
| Sorcha HP messages | active `npcHp uniqueId="437,1001"` group | commented out |
| Fail handler | active `questFail` -> message + teleport to continent 13 | commented out |
| Live content | none | quest 21307 Zik/Akatan story instance (RestoreTargetQuest 21307, initialize spawns, multi-phase cutscene) |
| startPos / exitPos | 58475,-67826,-5075 / 66615,-79814,-3003 | 59115,-67961,-5054 / 53169,-70241,-5663 |

So a level-8 player on quest 1346 cannot enter (blocked by `levelOver 65`), and even if
admitted would land in the 21307 Zik instance rather than a Sorcha defense. Quest 21307
does not exist in v31 at all (no `02130*.quest`), confirming the level-65 IoD revamp is a
post-classic overwrite of the classic Sorcha dungeon.

## The blocker is a live conflict, not dead content

The modern level-65 IoD line that owns 9037 is currently ENABLED in v92:
`021301.quest` prerequisite `63,66` (real), story group 26; `021306.quest` prerequisite
`213,05` (real, chained); `021307.quest` giver 436,8002, prerequisite `213,06`. Quest
21307 legitimately uses continent 9037 via `WorkObject 125` (isForQuestId=21307) and the
active level-65 DungeonData. It is registered active in `DungeonConstraint.xml`
(continentId 9037 / hz 437, "Tainted Gorge Bridge").

The continent's map is area `ATW_Death_P` (`AreaData_9037_ATW_Death_P.xml`). A brand-new
continent for the Sorcha dungeon is not feasible (client instance topology cannot be
cooked/duplicated - the known topology gap), so 1346 and 21307 must share the 9037 map or
one must yield it. Their entry conditions are mutually exclusive (level 8 vs level 65), so
a clean co-tenant of one DungeonData file is not achievable without brittle
condition-relaxing.

## Proposed fix

Recommended: reclaim continent 9037 for the classic Sorcha dungeon, and disable the
non-classic level-65 IoD line that currently occupies it. This is the v31-primary,
classic-authentic resolution.

DECISION POINT for the team lead before any spec is authored: confirm the modern level-65
"Garden of Dawn" IoD storyline (quests 213,1 through 213,7 = 21301-21307) is out of scope
for the classic baseline and may be disabled. It is currently enabled. If the reforged
design intends to keep that storyline, this reclaim cannot proceed as-is and quest 1346
would instead need a design decision on sharing the map.

Assuming the 213 line is out of scope, the fix is:

1. `DungeonData_9037.xml` - restore the classic Sorcha configuration (the v31 file is the
   reference):
   - Entry conditions: `solo`, `levelOver 8`, `maxMemberCount 1`,
     `progressQuest value="1346" taskId="1"`, and `completeQuest 1346` (the latter lets the
     player re-enter for task 2's in-instance visit). Use solo/maxMember 1 (matches quest
     `적정수행인원 1`) rather than v31's party/maxMember 5.
   - Un-comment/restore the 1346 EventGroups: `talkNpc uniqueId="437,1001"` (Sorcha spawn +
     attack waves over territories 43700322-43700363 + 420s timer), `npcHp
     uniqueId="437,1001"` (HP-threshold messages), and `questFail` (alert message +
     teleport back to continent 13).
   - Remove the modern 21307 content: `levelOver 65`, `RestoreTargetQuest 21307`, the
     `initialize` Zik spawn, and all questId=21307 EventGroups.
   - Set startPos/exitPos to land the player at Sorcha's arena and return them to the IoD
     camp (v31 values: startPos ~58475,-67826,-5075, exitPos 66615,-79814,-3003). Confirm
     by live test.

2. Disable the level-65 IoD line (21301-21307): apply the standard soft-disable sentinel
   (`선행퀘스트` = `99,99`) to quest 21301 (the entry point of story group 26), so the
   whole chain becomes unofferable, matching how the baseline disables other non-classic
   content. Removing `WorkObject 125` is not required once its quest is unofferable.

3. Leave 64,1050 `CampTeleport` (quick-travel) untouched - it is not the instance entrance.

4. Add dungeon 437 / continent 9037 ("Tainted Gorge Bridge", Sorcha's guard dungeon) to
   `patch-001-scope.md` "Associated Dungeon" table (currently only 436 is listed).

## Live-test checkpoints

- Confirm the guard task auto-teleports into 9037 on reaching task 1 with the restored
  conditions (progressQuest gate + level 8, no level-65 block). If auto-entry does NOT
  fire, fall back to wiring a quest-1346-gated entrance at the Tainted Gorge Bridge
  location (reuse `TeleportList 642501` -> 9037), but evidence strongly favors auto-entry.
- Confirm Sorcha (437,1001) spawns and the wave/timer defense runs for the 7-minute guard.
- Confirm task 2 (in-instance visit to Sorcha) and task 3 (turn-in to 64,1006 in camp)
  complete, and that failure teleports the player back to continent 13.
- Confirm disabling the 213 line does not orphan any in-progress-required references
  elsewhere.
