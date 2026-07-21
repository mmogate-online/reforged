# Sorcha's Reckless Challenge (quest 1346 / dungeon 9037) - Full Investigation Report

> **CORRECTION BANNER (2026-07-21, same-day follow-up session).** The conclusion of this
> report (sections 8-9: "territory topology binding below the editable datasheet layer") is
> **REFUTED**. The actual root cause is that all 8 classic territory groups in the v92
> `TerritoryData_437.xml` are wrapped in a single XML comment (`<!--` ... `-->`) and are never
> loaded by the server. The "byte-identical v31/v92" verification in section 3 was a text-level
> comparison that did not notice the surrounding comment markers; grep/diff see commented
> content the XML loader skips. See **section 12** for the corrected evidence chain and fix.
> The section 11 "stop there" lesson is superseded and must not be followed.

Status: **RESOLVED, LIVE-VALIDATED 2026-07-21.** The dungeon was fully completed in-game after
the territory restore: Sorcha and escorts spawn on load, all wave stages spawn as designed, the
420s defense completes, and the quest turns in. Originally filed as BLOCKED; see the correction
banner above.

Date: 2026-07-21. Author: content-restoration session (IoD padding phase).

---

## 1. Goal

Make the v31 padding-phase quest **1346 "Sorcha's Reckless Challenge"** functional on v92. It is a
solo defense instance: the player enters dungeon continent **9037** (hunting zone **437**), talks
to **Sorcha** (`437,1001`, internal name "에리아/Eria", "견습 마녀/Apprentice Witch"), and defends
her against timed attack waves for 7 minutes (`제한시간 0,7` / 420s). Task 1 = 수호Task (Guardian),
task 2 = visit Sorcha inside, task 3 = turn in to `64,1006` at the IoD camp.

The quest was enabled during the earlier padding wave (spec 14/17). Spec **19-iod-sorcha-dungeon**
reclaimed continent 9037 from the modern level-65 "Garden of Dawn" line (quests 21301-21307) and
restored the classic DungeonData config.

---

## 2. Sources and references used

Resolved from `reforged/.references`:

| Source | `.references` key | Path | Role |
|--------|-------------------|------|------|
| v31 server datasheet | `v31_datasheet` | `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet` | Authoritative classic baseline |
| v92 server datasheet | `server_datasheet` | `D:\dev\mmogate\tera92\server\Datasheet` | Deploy target |
| v92 client DataCenter | `client_datacenter` | `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR` | Client wiring (portal, NpcLoc) |
| Dev game server | `dev_server_ssh` / `dev_server_datasheet` | `D:/tera/server/Datasheet` | Live test target |

Domain knowledge (`domain_docs` = `D:\dev\github-vperim\datasheet-domain\src\content\docs`):

- `entities/dungeon-system.md` - DungeonData structure, EventGroup/EventTask catalog, continent tenancy, continentId vs huntingZoneId.
- `reference/spawn-mechanics.md` - spawn taxonomy, territory activation, `voidSpawn`/`partySpawn`/`conditionalSpawn` flags.
- `entities/territory-system.md` - territory types and their activation flows, Party system, `bossInstanceId` semantics.
- `entities/zone-hierarchy-system.md` - Continent -> Area -> HZ -> Section hierarchy, dungeon = single-HZ-per-continent, `withAbnormalityId`.
- `server-setup/gm-commands.md` - the GM/QA commands used for live diagnostics.

Prior artifacts:

- `docs/plans/classic-restoration/iod/data/padding-sorcha-entrance.md` - earlier entrance analysis (its "guard-task auto-entry" verdict was REFUTED, see the correction banner on that file).
- `specs/patches/001/19-iod-sorcha-dungeon.yaml` - the reclaim spec.
- `docs/dsl-requests/2026-07-21-workobject-entity.md` - filed because DSL has no workObject entity.

Wiki cross-reference (user-provided): `https://tera.fandom.com/wiki/Quest:Plague_Hunt` - a working
analogous quest (defend a carriage against mob waves). Resolved to **quest 1507 / dungeon 9039**,
used as the primary working comparison.

---

## 3. Files analyzed

### Server (read and/or compared, both eras)

| File | What was checked | Finding |
|------|------------------|---------|
| `DungeonData_9037.xml` | conditions, eventGroups, commented tenancy | Classic config restored 1:1 from v31; encounter logic intact |
| `TerritoryData_437.xml` | Sorcha spawn (terr 43700004), wave territories (43700322-43700363) | Sorcha = a `<Party partySpawn="true" bossInstanceId="43700996">`; byte-identical v31/v92 |
| `NpcData_437.xml` | template 1001 | Exists (shapeId 301040, aiid 102, race witch, elite) |
| `ContinentData.xml` | 9037 continent def | `channelType="dungeon"`, single `<HuntingZone id="437"/>`, matches working dungeons |
| `DungeonConstraint.xml` | 9037/437 registration | `isActive="true"` |
| `DungeonMatching.xml` | 9037 | not a matchmade dungeon (solo quest instance) |
| `TeleportData.xml` / `TeleportList.xml` / `TeleportMenuList.xml` | 9037 teleports | `642501` ("검은틈 입구", classic startPos) orphan in both eras; `4371001` (modern, WorkObject 125) |
| `WorkObjectData.xml` | template 125 (21307 portal), templates catalog | 125 = shape 531034 "Hedges", teleport to 9037 |
| `WorkObjectTerritory_13.xml` / `_437.xml` | portal placement | 13 was empty; 437 is v92-only |
| `AiData_437`, `DynamicSpawn_437`, `FormationData_437`, `ActiveMove_437`, `NpcSkillData_437`, `BonfireData_437`, `ShieldTerritory_9037_ATW_P` | file-set completeness | Present; file-set identical to working 9039/9091 |
| `QuestData/001346.quest` (v31+v92) | task structure, prereq | Identical except prereq (v31 `99,99` disabled; v92 `13,45`); guard task is the START task |

### Comparison dungeons (to find the working pattern)

| Dungeon | Quest | Guard target | Spawn structure | Works? |
|---------|-------|--------------|-----------------|--------|
| 9039 | 1507 **Plague Hunt** | `439,1001` (carriage) | direct standalone `<Npc memberId="0">` in a `type="normal"` territory | ✅ |
| 9091 | 2308 | `491,99` (Fiona) | `<Party partySpawn="true" bossInstanceId="0">` | ✅ |
| 9003 | 401 | `403,1103` | spawned via an `initialize` EventGroup (`type="quest"` territory) | ✅ |
| 9019 | 706 | `419,99` | party, `bossInstanceId=41900109` | (assumed) |
| **9037** | **1346** | **`437,1001` (Sorcha)** | `<Party partySpawn="true" bossInstanceId="43700996">` | **❌** |

Also read: `DungeonData_9003/9019/9064/9089/9090/9040`, `TerritoryData_491/403/439`,
`QuestData/021307.quest` (modern tenant), `QuestData/001507.quest`, `QuestData/005201.quest`.

### Client (v92 DataCenter)

| File | Change / check |
|------|----------------|
| `WorkObjectData` | added portal template 134 |
| `StrSheet_WorkObject` | id 134 "Black Rift Entrance" |
| `StrSheet_WorkObjectLoc` | tpl 134 loc `13#57908,-67648,-5097` |
| `WorkObjectShape` | shape 531034 = "A_Island_Bush", 200201 = "NPC_Trans" |
| `StrSheet_NpcLoc` | added `437,1001` -> `13#57908,-67648,-5097` (journal link); confirmed the modern 21307 NPCs (4000/8001/8003/8006/8008) had locs but Sorcha did not |
| `StrSheet_Quest` | resolved "Plague Hunt" = quest 1507 |
| `Abnormality` / `StrSheet_Abnormality` | 488000009 and 70449 exist |

---

## 4. Changes deployed during the investigation

Server (pushed via `deploy-dev`, world restart manual by user):

1. `DungeonData_9037.xml` - classic config restored (prior session); this session added then reverted an `initialize` EventGroup spawning terr 43700004.
2. `WorkObjectData.xml` - new portal template 134 (shape swapped bush 531034 -> NPC_Trans 200201; teleport 642501; gated `isForQuestId=1346 firstTaskId=1 lastTaskId=1`).
3. `WorkObjectTerritory_13.xml` - placed portal 134 at `57908,-67648,-5097`.
4. `TerritoryData_437.xml` - Sorcha party `bossInstanceId` `43700996` -> `0` (to match Fiona).

Client (published dev.28, dev.29 via `deploy-client`):

5. `WorkObjectData` / `StrSheet_WorkObject` / `StrSheet_WorkObjectLoc` - portal template + name + minimap loc.
6. `StrSheet_NpcLoc` - Sorcha journal location.

---

## 5. What we tried, in order, and why

| # | Hypothesis | Change | Result |
|---|-----------|--------|--------|
| 1 | No entrance exists (guard task is the START task, so quest-task auto-entry never fires; classic teleport 642501 is an orphan; quest was `99,99`-disabled in v31 so never wired) | Authored physical WorkObject portal 134 -> teleport 642501 -> 9037 | Player **can enter**, but the instance is empty |
| 2 | Portal looks wrong (bush) | shape 531034 -> 200201 (NPC_Trans pad) | cosmetic only |
| 3 | Journal "Sorcha" link dead (no NpcLoc for 437,1001) | added StrSheet_NpcLoc -> entrance | link/indicator wiring |
| 4 | Sorcha never spawns because the classic config lacked an `initialize` (9003 pattern: "던전 생성 되자마자 수호대상 스폰") | added `initialize` EventGroup spawning terr 43700004 | **Sorcha still absent** |
| 5 | Sorcha's party is boss-flagged (`bossInstanceId=43700996`) so it waits for a trigger; working Fiona uses `bossInstanceId=0` | `bossInstanceId` -> 0, reverted the dead initialize | **Sorcha still absent** |

Each fix targeted a plausible, precedent-backed cause. Each was disproven by live test.

---

## 6. In-game tests (run live by the user)

| Command / action | Purpose | Result |
|------------------|---------|--------|
| Enter via portal on quest 1346 task 1 | Confirm entry | Enters continent 9037, empty |
| `/@jump_task 1346 1` | Sit on task 1 (portal gate + dungeon condition) | OK |
| `/@jumpto 437 1001` | Teleport to Sorcha if she exists | **"not found"** = zero Sorcha spawned |
| `/@enter_dungeon 9037 0` | Create + enter a **proper** instance (rules out flat-teleport theory) | Enters a proper instance, **still no Sorcha** |
| `/@enter_dungeonwork 9037 0 1` | Solo quest-dungeon entry variant | nothing |
| `/@spawnnpc 437 1001 1` | Force-spawn Sorcha directly (bypass territories) | **Sorcha appears** with quest marker |
| Talk -> "Activate the magical device" -> "Protect Sorcha" | Trigger the encounter on the force-spawned Sorcha | **"challenge has begun", timer starts ticking, but NO wave mobs spawn** |

The last two rows are the decisive evidence (see section 8).

---

## 7. Domain knowledge established (verified against docs + data)

- **Quest-task auto-entry** (`entities/dungeon-system.md`): the engine auto-teleports a player into a solo instance when the quest reaches the first task carrying a `던전Id`. REFUTED for 1346: a bare 수호Task as the START task does not fire it, and 1346 is the only quest in the whole dataset with a dungeon-carrying task at position 1. All functioning instances are entered via a physical portal.
- **Territory types** (`entities/territory-system.md`): `type="normal"` spawns immediately on world/instance load; `type="quest"` is dormant and spawned by a DungeonData `EventTask type="spawn"`. Sorcha's territory 43700004 is `normal`; the wave territories are `quest`.
- **Party / bossInstanceId** (`entities/territory-system.md`): `bossInstanceId` is meant to point to the leader NPC's `instanceId` (so Sorcha's original `43700996`, her own instanceId, was correct; Fiona's `0` is the anomaly, not the rule). `partySpawn="true"` = all members spawn together on territory activation.
- **Dungeon = single-HZ continent** (`entities/zone-hierarchy-system.md`): continent 9037 carries exactly one `<HuntingZone id="437"/>`. Confirmed; and force-spawn in HZ 437 works, so the HZ binding is live.
- **Guard-target spawn patterns**: working defense dungeons spawn the defended NPC either as a direct standalone Npc (9039 Plague Hunt carriage, 9003, 9064, 9089) or a `bossInstanceId=0` party (9091 Fiona). Sorcha is the lone boss-flagged party.

---

## 8. Evidence chain to the conclusion

What is **proven working**:

1. Encounter **logic** is correct: force-spawned Sorcha shows the quest marker, the dialog chain runs, "Protect Sorcha" fires the `talkNpc` EventGroup (the 420s `timerUi` task starts). The DungeonData script matches v31 1:1.
2. **Direct** NPC spawning works in the instance (`/@spawnnpc 437 1001 1`), so the HZ, template, AI, and instance are all valid.
3. Entry conditions work (gated to quest 1346 task 1).

What is **proven broken**:

4. **Territory-based spawning fails through every mechanism**:
   - `type="normal"` load-spawn: Sorcha's terr 43700004 never auto-appears on instance creation.
   - `type="quest"` event-spawn: the `talkNpc` wave tasks fire (timer proves the event ran) but produce **no mobs**.
   - explicit `initialize` event-spawn of terr 43700004: also produced nothing.

What is **ruled out** (each verified, not assumed):

- Dungeon scripting / conditions / eventGroups - correct, match v31, logic fires.
- Missing NPC template - 1001 exists; all 38 wave/spawn templates exist in NpcData_437.
- Wrong HZ / continent mapping - 9037 -> 437 correct; force-spawn in 437 works.
- Missing file type / AreaData - file-set identical to working 9039/9091; no dungeon here uses AreaData.
- ContinentData difference - `withAbnormalityId="488000009"` is present on the working 9039 and 9091 too, so it is a harmless global v92 addition, not the cause. 9037's continent shape matches the working dungeons.
- Entry mechanism (flat teleport vs real instance) - `/@enter_dungeon 9037 0` creates a proper instance and Sorcha still does not spawn, so the WorkObject portal is not the problem.
- Sorcha's party structure (`bossInstanceId`) - changed to match working Fiona; no effect.

**Conclusion:** every editable datasheet (ContinentData, HZ map, NpcData, TerritoryData structure,
DungeonData scripting, whole file set) matches the working Plague Hunt / Fiona dungeons, and the
encounter logic itself works, yet **territory spawning does not function in the reclaimed 9037
instance**. The fault is below the datasheet layer we can edit: the 9037 instance topology was
rebuilt for the modern level-65 "Garden of Dawn" (21307) revamp, and the classic HZ-437 territories
do not bind to it. This is the documented "client instance topology cannot be cooked/duplicated"
gap. No DungeonData or TerritoryData edit can change it, because the data is already correct; the
instance will not honor it.

---

## 9. Why this is not fixable within scope

- The data is not the problem, so there is nothing left to correct in DungeonData/TerritoryData.
- The territory topology binding is part of the compiled/cooked instance definition for continent 9037, which was reconstructed for 21307. Rebuilding it means reverse-engineering and re-cooking client level geometry, which is out of scope (the known topology gap).
- 1346 is a single optional side-dungeon on the tutorial island that was **never finished in v31** (its DungeonData carries the dev note `원안 3인 퀘스트, 임시 입력` = "original 3-person quest, temporary input", and the quest was `99,99`-disabled there). There is no complete, proven-working source to port.

---

## 10. Recommendation and proposed disposition

**Shelve quest 1346 as deferred / unfinished padding.**

1. Re-disable quest 1346 (sentinel prerequisite) so players are not handed a broken quest. Reverts only this one padding enable.
2. Revert the speculative spawn edit: `TerritoryData_437` `bossInstanceId` `0` -> `43700996` (the correct leader value); the dead `initialize` is already removed from `DungeonData_9037`.
3. Portal (WorkObject 134) + journal loc become inert automatically once 1346 is unofferable (gated `isForQuestId=1346`). Leave harmlessly, or remove for cleanliness (open decision).
4. Log in the IoD divergence log as deferred padding; keep this report as the record so no future session re-attempts it.

The 21307 line stays disabled (separate policy decision, unaffected). Continent 9037 keeps the inert
classic config, which is acceptable dormant content per doctrine.

---

## 11. Reusable lesson (SUPERSEDED, see section 12)

~~When restoring an instance dungeon onto a continent that a later game version repurposed, the
datasheets can be perfectly correct and the encounter still fail, because the instance's territory
topology binding is not in the editable datasheet layer.~~ **Wrong.** The corrected lesson: the
`/@spawnnpc`-works-but-no-territory-spawn-works signature means the territory data is **not being
loaded**, and the first thing to check is XML comment markers around the territory groups.
Grep and text diff both "see" commented-out content; only a real XML parse tells you what the
server loads. This session even edited `bossInstanceId` inside the commented block without
noticing.

## 12. Correction (2026-07-21 follow-up): actual root cause and fix

### Root cause

`TerritoryData_437.xml` (v92) lines 3-591 were one XML comment. It contained **all 8 classic
territory groups (63 territories)**: `43700001 빌리저 배치` (Sorcha's villager group, terr
43700004), `43700009-43700011 1/2/3단계` (wave stages), `43700012-43700014 후방` (rear-guard
stages), `43700015 막판 연출용` (finale staging). Only the modern Garden of Dawn groups
(`43700016 미션퀘스트01`, `43700017 연출`, territories 43700384-43700398) were live. The
commented set is territory-id-identical to v31 (verified id-by-id, both directions). BHS
disabled the classic encounter by commenting it out when 9037 was repurposed for the 21307 line.

This explains every symptom in section 8 with no residue: normal-type load spawn, event wave
spawn, and `initialize` spawn all target territories that were never parsed into existence;
`/@spawnnpc` bypasses territories; DungeonData (a separate, uncommented file) fires its logic
against nothing.

### Refuted claims from this report

- "Territory topology binding is not editable / cooked": false. 9037 shares `ATW_Death_P`
  (same `AreaList.xml` origin 43,58, same `.geo`/`.nod` tiles) with continent 13, where
  territory spawning demonstrably works. Topology was never the blocker.
- "TerritoryData byte-identical v31/v92": text-identical **inside a comment**. Not loaded.
- The `bossInstanceId` 43700996 value was correct all along (leader's instanceId); the `0`
  edit was made inside the comment block and could never have had an effect. Reverted.

### Additional findings

- Era rebinding: v31 bound continent 9037 to area `ATW_P` (original island map,
  `AreaData_9037_ATW_P.xml`); v92 binds it to `ATW_Death_P` (`AreaData_9037_ATW_Death_P.xml`).
  Classic coordinates sit in a preserved part of the island (live walking + force-spawn
  confirmed terrain validity).
- The v92 AreaData section polygon for 9037 ("검은 틈 입구", section 57) **shrank** vs v31:
  vertices C/D pulled inward. Point-in-polygon over all 63 classic territories: Sorcha's group
  and staging territories are inside both eras' polygons, but **42 wave territories at the
  entrance strip (~X 57.5-57.8k) are outside the v92 polygon** (inside v31's). Whether section
  containment gates territory spawning is unproven (modern active terr 43700397 also sits
  outside). If waves fail after the restore, the next editable fix is restoring the two v31
  fence vertices in `AreaData_9037_ATW_Death_P.xml`:
  v31 C = `56593.3984,-66792.6953,-5185.8867`, D = `57665.0859,-72032.6563,-5945.4482`
  (v92 has C = `57952.33...,-67640.55...`, D = `58746.00...,-70831.11...`).
- Disable-by-comment is a BHS pattern, not a one-off: a sweep found 14 v92 TerritoryData files
  with comment-disabled spawn content (HZ 26: 76 territories; HZ 437: 63; also 473, 358, 243,
  871/872, 767, 980, 2050/2052/2054, 236, 58). Relevant to every future restoration audit.

### Fix applied (baseline lane, deployed to dev, awaiting restart + live test)

1. Removed the `<!--`/`-->` markers in `TerritoryData_437.xml`; re-added the final
   `</TerritoryGroup>` the comment had swallowed (8 opens / 7 closes inside the block).
2. Reverted the speculative `bossInstanceId` edit back to `43700996`.
3. Validated: file parses, 10 groups / 74 territories live; the 8 classic groups are
   attribute-identical to v31 except the v92 schema addition `autoRespawn="false"` on the
   Party element (pre-existing, harmless).
4. Deployed via `deploy_dev.py --verify` (47 working-tree files, verify OK).

### Live-test result (2026-07-21)

All checkpoints below **passed** on the first post-restore run: territory spawns appeared without
any GM force-spawn, the full wave encounter ran as designed, and the quest was completed end to
end. Bonus finding: the 42 wave territories outside the v92 AreaData section polygon spawned
normally, proving AreaData section containment does NOT gate territory spawning (the conditional
AreaData fix below is therefore unnecessary and must not be applied).

### Live-test checkpoints (after manual world restart)

1. `/@jump_task 1346 1`, enter via portal (or `/@enter_dungeon 9037 0`): Sorcha `437,1001`
   (plus 2 enchanted dolls 1003 and Rian Kubel 1002) should now stand at ~`59347,-68002,-5063`
   **without** `/@spawnnpc`.
2. `/@jumpto 437 1001` must resolve.
3. Dialog, then "Protect Sorcha": timer starts **and stage-1 wave mobs spawn** (piglings etc.;
   waves come from the entrance strip). If Sorcha spawns but waves do not, apply the AreaData
   section-polygon restore above and retest. That outcome would also prove section containment
   gates territory spawning (valuable domain knowledge either way).
4. Survive 420s, task completes, turn in at `64,1006`.
