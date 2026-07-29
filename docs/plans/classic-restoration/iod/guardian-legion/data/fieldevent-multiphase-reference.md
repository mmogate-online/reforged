# Field Event Multi-Phase Reference

Reverse-engineered from the shipped v92 corpus for the purpose of authoring a three-phase Guardian
Legion mission on continent 13 (Island of Dawn).

**Sources**

| Source | Path |
|---|---|
| Server field data (12 shipped files + our authored one) | `<server_datasheet>\FieldData_*.xml` |
| Global field event config | `<server_datasheet>\FieldEvent.xml` |
| Action scripts | `<server_datasheet>\S1ActionScripts_Field.xml` |
| Territory data | `<server_datasheet>\TerritoryData_{huntingZoneId}.xml` |
| Continent declaration | `<server_datasheet>\ContinentData.xml` |
| Client UI half | `<client_datacenter>\Field\` |
| Client cutins | `<client_datacenter>\EventDialog\` |
| Client strings | `<client_datacenter>\StrSheet_Field\` |

All counts in this document are over the **shipped** corpus: the 12 publisher files, 16 events,
733 `EventGroup` and 7,060 `EventTask` elements. Our own `FieldData_13.xml` is excluded from
every count so that it cannot contaminate the evidence.

Parsed with `lxml` with comments preserved. Comments matter: the publisher disables content by
commenting it out, and several schema definitions exist only inside comments.

---

## 1. Schema Reference

### 1.1 Element tree and cardinality

```
Field                                     (12, one per file, = one continent)
└── FieldEvent                            (16 total; 1 to 3 per file)
    ├── Condition                         (64 = 4 per event, always the same 4 types)
    ├── ClearCondition                    (16, exactly one per event)
    ├── Progress                          (16, exactly one per event)
    ├── SpawnAreaList                     (19)
    │   └── SpawnArea                     (26)
    ├── AutoUserBalance                   (1 live and empty; 7 more exist only inside comments)
    ├── AutoEventBalance                  (14)
    │   └── Balance                       (175)
    │       ├── BasicAbnormality          (156)   npc stat scaling
    │       └── Setting                   (34)    progress rate scaling  [UNDOCUMENTED]
    ├── ClearRewardPool                   (3)
    │   └── ClearReward                   (3)
    ├── EventPoint                        (16)
    │   └── Point                         (39)
    ├── Guide                             (15)
    │   └── Task                          (58)
    │       └── Marker                    (70)
    ├── FieldEventCloud                   (4)
    │   └── AeroList
    │       └── Aero                      (10)
    ├── AeroTerritory                     (4)
    └── EventGroup                        (733)
        └── Event                         (900)
            └── EventTaskGroup            (1454)
                └── EventTask             (7060)
```

Note the `Event` layer between `EventGroup` and `EventTaskGroup`. It carries no attributes anywhere
in the corpus but it is structurally required.

### 1.2 `Field`

| Attribute | n | Domain | Meaning |
|---|---|---|---|
| `continentId` | 12 | 2000, 7001, 7003, 7005, 7011, 7012, 7013, 7014, 7015, 7021, 7022, 7031 | The continent this file's events belong to. Must match the filename suffix. |

### 1.3 `FieldEvent`

| Attribute | n | Domain | Meaning |
|---|---|---|---|
| `id` | 16 | `1` x6, `2` x4, `90` to `95` | Event id, unique within the continent. Referenced by the rotation. |
| `startTerritoryId` | 16 | `continentId,territoryId` | Entry territory. Note the first half is a **hunting zone id**, not a continent id, despite the name (e.g. `627,62700001`). |
| `startPos` | 16 | `x,y,z` | Default entry position. One event uses the sentinel `999999,-999999,99999`. |
| `startDir` | 14 | `-25252` to `300` | Facing on entry. Not normalised to 0 to 360. |
| `revivePos` | 16 | `x,y,z` | Respawn point on death. |
| `reviveTownNameId` | 16 | `7777` (all 16) | String id for the revive location name. Effectively a constant. |
| `revivalRecoveryRate` | 16 | `1` (all 16) | HP/MP fraction restored on revive. Effectively a constant. |
| `nonPkSectionId` | 7 | `continentId,section,id` | Declares a non-PvP section inside the mission. |
| `type` | 3 | `0` x1, `1` x2 | Mission type. Undifferentiated in behaviour from the data alone. |
| `desc` | 1 | free text | Developer label. Only one shipped event carries it; the rest use an XML comment instead. |
| `execOnlyChannel` | 3 | `1`, `1,2,3` | Channel whitelist. |
| `cantTeleport` | 1 | `true` | Disables teleport while active. |
| `worldAnnounce` | 1 | `true` | Broadcasts a world announcement on start. |
| `rustleSoundOff` | 1 | `true` | Suppresses ambient rustle sound. |

### 1.4 `Condition`

Every one of the 16 events declares exactly the same four, so treat all four as mandatory in
practice even though the engine may not require them.

| `type` | `value` domain |
|---|---|
| `minLevel` | 1, 20, 30, 40, 50, 60, 65 |
| `maxLevel` | 70, 90, 99 |
| `maxMemberCount` | 15, 20, 30 |
| `teleportMemberCount` | 10, 20 |

### 1.5 `ClearCondition`

| Attribute | n | Domain | Meaning |
|---|---|---|---|
| `progressTime` | 16 | `330` x10, `440` x2, `660` x3, `1110` x1 | Mission duration in seconds. |
| `endWhenProgressFull` | 16 | `false` (all 16) | Never `true` anywhere in the corpus. Events always run out their clock; a full bar does not end them early. |
| `endIntervalTime` | 16 | `30` x15, `60` x1 | Seconds between end-of-event completion checks. |

`endWhenProgressFull="false"` being universal is worth internalising: filling the bar is the
*success* condition, not the *termination* condition. The event keeps running until
`progressTime` expires.

### 1.6 `Progress`

| Attribute | n | Domain | Meaning |
|---|---|---|---|
| `maxValue` | 16 | `100000` (all 16) | Raw units for a full bar. |
| `dividerPercent` | 15 | `100`, `20,100`, `10,25,100`, `15,30,100`, `25,50,100`, `30,70,100`, `30,80,100`, `50,80,100` | UI tick marks on the bar. **Cosmetic only, see 2.4.** |
| `isSharedChannel` | 16 | `false` (all 16) | Cross-channel progress sharing. Never enabled. |
| `syncNpcHpInterval` | 16 | `3` x12, `1` x4 | Seconds between npc HP syncs to clients. Use `1` when the bar is bound to boss HP. |
| `standardPlayerCount` | 16 | `30` (all 16) | Reference headcount for scaling. Effectively a constant. |

### 1.7 `SpawnAreaList` and `SpawnArea`

| Element | Attribute | Domain | Meaning |
|---|---|---|---|
| `SpawnAreaList` | `id` | 1 to 6 | Referenced by `changePos` tasks. |
| `SpawnArea` | `center` | `x,y,z` | Placement point. |
| `SpawnArea` | `dir` | -92 to 340 | Facing. |
| `SpawnArea` | `randomRange` | `0` (all 26) | Scatter radius. Always exact placement in shipped data. |

### 1.8 `AutoEventBalance` and its two children

`Balance` rows key on live participant count:

| Attribute | Domain |
|---|---|
| `userMin` | 0 to 55 |
| `userMax` | 1 to 60 |

Two distinct child elements hang off a `Balance` row, and they do completely different jobs.

**`BasicAbnormality`** (156 rows) scales the NPCs:

| Attribute | Domain | Meaning |
|---|---|---|
| `targetNpcId` | `0,0` x141, `627,1001` x15 | `0,0` means every event npc; otherwise `huntingZoneId,templateId`. |
| `abnormalityId` | `77770002` to `77770030`, even numbers | Stat modifier applied to those npcs at this headcount. |

The escort's per-npc row is instructive: `627,1001` is the wagon, and it is pinned to
`77770020` (the 1x tier) at **every** headcount, so the escorted object does not get harder to
protect as the crowd grows while the enemies do.
See `FieldData_7012.xml:29-90`.

**`Setting`** (34 rows, in 2 files) scales the *progress bar*, and is **absent from the domain
docs entirely**:

| Attribute | Domain | Meaning |
|---|---|---|
| `progressType` | `basic` (all 34) | Which progress mode this rate applies to. |
| `value` | `1` down to `0.018` | Multiplier applied to `basic` progress gains at this headcount. |

The full ladder, identical in `FieldData_7003.xml:420` and `FieldData_7021.xml:59`:

| Players | value | Players | value | Players | value |
|---|---|---|---|---|---|
| 0 to 1 | 1 | 8 to 9 | 0.125 | 30 to 34 | 0.033 |
| 2 | 0.5 | 10 to 14 | 0.1 | 35 to 39 | 0.029 |
| 3 | 0.333 | 15 to 19 | 0.067 | 40 to 44 | 0.025 |
| 4 | 0.25 | 20 to 24 | 0.05 | 45 to 49 | 0.022 |
| 5 | 0.2 | 25 to 29 | 0.04 | 50 to 54 | 0.02 |
| 6 to 7 | 0.167 | | | 55 to 60 | 0.018 |

The value tracks `1/N` closely. This is the mechanism that stops a kill-driven bar from being
filled in seconds by a large crowd. **Any event whose bar is filled by `progress action="plus"`
tasks needs this ladder, or its pacing is a function of how many people showed up.** The Korean
comment above the block at `FieldData_7003.xml:419` reads "progress balancing by player count",
distinguishing it from the plain "balancing by player count" comment on the `BasicAbnormality`
blocks.

### 1.9 `EventPoint` and `Point`

| Attribute | n | Domain | Meaning |
|---|---|---|---|
| `id` | 39 | 1 to 6 | Referenced by `point` tasks to toggle the rule mid-mission. |
| `type` | 39 | `dealing` x18, `healing` x11, `checkAbnormality` x7, `npcInteraction` x3 | Scoring metric. |
| `value` | 39 | `0.0` to `5.25` | Per-event coefficient. |
| `templateId` | 7 | `623004`, `623006`, `6270002` | For `checkAbnormality`, which abnormality is watched. |

`checkTerritory` is declared in the global file but **no shipped event uses it in a `Point` row**.

### 1.10 `Guide`, `Task`, `Marker`

| Element | Attribute | Domain | Meaning |
|---|---|---|---|
| `Guide` | `titleString` | `@field:NNNNNN` | Mission title string. |
| `Guide` | `description` | `@field:NNNNNN` | World map tooltip description. |
| `Guide` | `eventSize` | `small` x4, `medium` x2, `large` x1, `flying_medium` x2, `dragon_island` x6 | World map icon class. `flying_small` and `flying_large` are declared globally but unused. |
| `Task` | `id` | 0 to 9 | Objective id, referenced by `guide` tasks. |
| `Task` | `target` | `@creature:zone#templateId` or empty | Creature whose name is substituted into the string. |
| `Task` | `string` | `@field:NNNNNN` | Objective text. |
| `Task` | `iconId` | `1` x31, `2` x11, `3` x10 | Objective icon. |
| `Marker` | `markerType` | `MARKER_FIELD_EVENT_AREA_01` x29, `_02` x9, `_03` x14 | Map marker shape. |
| `Marker` | `markerPos` | `x,y,z` | Marker position. |
| `Marker` | `markerScaleX` / `Y` | 0.3 to 2.6 | Marker scale. |

A `Marker` with **no attributes at all** is legal and common (18 of 70); it is how an objective
declares "no map marker" while keeping the element present. See `FieldData_7012.xml:95`.

The shared strings are reusable and already localised in `StrSheet_Field-00000.xml`:

| String id | Text |
|---|---|
| `100000` | "Mission is not ready yet." |
| `100001` | "Defeat {target}." |
| `100003` | "Protect {target}." |
| `111111` | "Mission Complete" |

### 1.11 `EventGroup` (triggers)

| Attribute | n | Notes |
|---|---|---|
| `type` | 733 | See distribution below |
| `repeat` | 578 | `true` x487, `false` x91. Absent on 155 groups. |
| `name` | 138 | Flag name(s) for `flag` groups; label otherwise |
| `value` | 221 | Threshold, unit depends on type |
| `uniqueId` | 33 | `huntingZoneId,templateId` or `huntingZoneId,territoryId` |
| `checkFlag` | 377 | Gate flag; group only runs while it is set |
| `min` / `max` | 38 each | Inclusive range for `killCount` and `userCountInEvent` |
| `killCountName` | 4 | Named counter for `killCount` groups |
| `timerName` | 26 | Named timer for `timer` groups |
| `targetHuntingZoneId` | 321 | For `npcSpawn` / `npcDespawn` |
| `targetInstanceId` | 321 | For `npcSpawn` / `npcDespawn`. Instance id, not template id. |
| `targetNpcId` | 3 | **Only on `enterTerritory`**, all three `627,1001` |

Trigger type distribution:

| `type` | n | Fires when |
|---|---|---|
| `npcDespawn` | 171 | A specific npc instance despawns |
| `npcSpawn` | 150 | A specific npc instance spawns |
| `flag` | 112 | Every flag named in `name` is set (conjunction) |
| `progressTimer` | 80 | The mission countdown reaches `value` seconds **remaining** |
| `npcInteraction` | 54 | A player completes the interaction rule whose id equals `value` |
| `userCountInEvent` | 34 | Participant count is within `min`..`max` |
| `progress` | 33 | The bar reaches `value` **percent** |
| `timer` | 26 | The named timer reaches `value` |
| `userCountInTerritory` | 18 | Players in `uniqueId` territory reaches `value` |
| `initialize` | 16 | Mission instance is created |
| `beforeEndEvent` | 10 | Just before the event ends |
| `beforeDeleteEvent` | 10 | Just before the event is freed from memory |
| `npcHp` | 9 | Target npc HP crosses `value` percent (`0` = death) |
| `killCount` | 4 | The named counter is within `min`..`max` |
| `enterTerritory` | 4 | An entity enters `uniqueId` territory |
| `npcState` | 1 | Npc enters a state |
| `npcReset` | 1 | Npc leaves combat and resets |

`probability` never appears on `EventGroup`. All 740 occurrences are on `EventTaskGroup`.

### 1.12 `EventTaskGroup`

| Attribute | n | Domain |
|---|---|---|
| `probability` | 740 | `0.0` x163, `0.05` x180, `0.125` x48, `0.25` x8, `0.3` x161, `0.33`/`0.333`/`0.334` x8, `0.5` x10, `0.7` x161 |

When the parent trigger fires, each sibling task group is rolled independently. `0.0` groups
are dead branches left in the data. The escort's three-way wave picker uses `0.334 / 0.333 / 0.333`
(`FieldData_7012.xml:325-339`), which sums to 1.0 but is still three independent rolls, so it is
not a guaranteed-exactly-one selection.

### 1.13 `EventTask`

Task type distribution across all 7,060:

| `type` | n | `type` | n |
|---|---|---|---|
| `aiCombatWork` | 1928 | `timer` | 98 |
| `despawn` | 1181 | `empty` | 56 |
| `spawn` | 894 | `abnormality` | 55 |
| `dynamicSpawn` | 693 | `point` | 52 |
| `message` | 509 | `changePos` | 49 |
| `flag` | 426 | `progressType` | 21 |
| `changeHp` | 416 | `doActionScript` | 17 |
| `progress` | 356 | `aero` | 12 |
| `eventDialog` | 151 | `killCount` | 8 |
| `guide` | 130 | `workObjectSpawn` / `workObjectDespawn` | 4 / 4 |

Attribute domains, restricted to what matters for a multi-phase authoring job:

| Attribute | n | Domain | Applies to |
|---|---|---|---|
| `next` | 7060 | `none` x3761, `time` x3299 | all tasks; inter-task delay, not a branch |
| `nextValue` | 3300 | `0` to `30`, floats | `next="time"` |
| `name` | 524 | 121 distinct | `flag`, `timer` |
| `value` | 887 | see below | `flag`, `progress`, `progressType`, `timer`, `killCount` |
| `action` | 462 | `plus` x354, `start` x86, `stop` x20, `change` x2 | `progress`, `timer`, `killCount` |
| `huntingZoneId` | 2823 | 24 distinct zones | `spawn`, `despawn`, `dynamicSpawn`, `abnormality`, `killCount` |
| `territoryId` | 2116 | 917 distinct | `spawn`, `despawn`, `abnormality` |
| `isEventNpc` | 495 | `false` (all 495) | `spawn` only; marks a world-restore spawn |
| `startAggro` | 24 | `10000` (all 24) | `spawn`; initial aggro toward `targetNpcId` |
| `targetNpcId` | 2020 | 56 distinct | many; `huntingZoneId,templateId` |
| `progressType` | 21 | `npcHp` x15, `basic` x6 | `progressType` |
| `progressValue` | 10 | `6666`, `6667` x2, `10000` x2, `25000` x2, `50000`, `80000` x2 | `progressType="npcHp"` only |
| `method` | 465 | `rate` x416, `start` x42, `revive` x7 | `changeHp` (`rate`), `changePos` (`start`/`revive`) |
| `id` | 252 | 147 distinct | `point`, `changePos`, `eventDialog` |
| `turn` | 107 | `on` x86, `off` x21 | `point`, `abnormality` |
| `guideId` | 130 | single ids and comma lists (`2,3`, `1,2,3,4,5,6,7,8`) | `guide` |
| `guideType` | 130 | `add` x56, `remove` x44, `complete` x30 | `guide` |
| `direction` | 97 | `forward` x89, `reverse` x8 | `timer` |
| `timerUiOff` | 98 | `true` (all 98) | `timer` |
| `killCountName` | 8 | 4 distinct | `killCount` |
| `targetType` | 6 | `specificNpc` (all 6) | `killCount` |
| `npcTemplateId` | 6 | `1002`, `1003`, `1003,1004`, `1007,1008` | `killCount`; accepts a comma list |
| `style` | 444 | `combat` x417, `speechbubble` x27 | `message`; absent on 65 |
| `string` | 509 | `@field:NNNNNN` | `message` |
| `abnormalityId` | 55 | 27 distinct | `abnormality` |
| `target` | 55 | `player` x46, `npc` x9 | `abnormality` |
| `aliveOnly` | 46 | `true` x30, `false` x16 | `abnormality` |
| `amount` | 416 | `-100.00` x161 and 32 others, all negative | `changeHp` |
| `workId` | 1928 | `101`, `109`, `102`, `110`, `301`, `358`, and 8 more | `aiCombatWork` |

`value` on `EventTask` splits cleanly by task type:

| Task type | `value` unit | Observed |
|---|---|---|
| `flag` | boolean | `0` x302 (partly), `1` x219 |
| `progress` | **raw units** | `375`, `500`, `1000`, `2000`, `2500`, `3000`, `5000`, `6000`, `7500`, `10000`, `30000`, `50000` |
| `progressType` (`basic`) | **raw units** | `15000` x2 |
| `timer` | seconds | `0`, `60` |
| `killCount` | starting count | `0` |

---

## 2. Phase Mechanism

There is **no phase element**. A phase is an emergent construct built from four primitives.
Understanding this is the whole job.

### 2.1 The four primitives

| Primitive | Element | What it gives you |
|---|---|---|
| **Named flags** | `EventTask type="flag"` sets them, `EventGroup type="flag"` waits on a conjunction of them | A general purpose state machine |
| **The progress bar** | `EventTask type="progress"` writes raw units, `EventGroup type="progress"` triggers on percent | An ordered, monotonic phase clock |
| **Territory occupancy** | `EventGroup type="enterTerritory"` / `userCountInTerritory` | Spatial gates, which is what makes an event *move* |
| **Named counters and timers** | `killCount` and `timer` task/group pairs | Bounded work quotas and wave pacing |

### 2.2 The dominant sequencing idiom: the progress ladder

The corpus overwhelmingly sequences phases through the **progress bar**, not through flags.
Flags are used for one-shot latches and difficulty variants; the *spine* is progress.

The pattern is:

1. A phase opens by declaring how the bar will be filled during it, with a `progressType` task.
2. Work during the phase adds raw units to the bar.
3. The bar crossing a percentage fires an `EventGroup type="progress"`, which tears down the
   current phase and opens the next one.

Because the bar is monotonic and shared, this gives a guaranteed ordering with no explicit
sequencing construct.

### 2.3 The two progress modes and their allocation attributes

| Mode | Task | Extra attribute | Semantics |
|---|---|---|---|
| `basic` | `progressType progressType="basic"` | `value` (raw units) | The bar is filled by explicit `progress action="plus"` tasks. `value` is the raw allocation for this segment. |
| `npcHp` | `progressType progressType="npcHp" targetNpcId="zone,template"` | `progressValue` (raw units) | The bar is driven by the inverse HP of that npc template. `progressValue` is the slice of the bar it owns. |

`value` appears only on `basic` tasks (2 uses, both in the escort). `progressValue` appears only
on `npcHp` tasks (10 uses). They are different attributes with the same job for different modes.

`npcHp` bindings **accumulate**: several can be active at once, each contributing its
`progressValue`. Two shipped events prove this arithmetically:

| Event | Bindings | Sum | Then |
|---|---|---|---|
| `FieldData_7005.xml:306-307` | `628,3000` at 10000 + `628,3001` at 10000 | 20000 = 20% | `progress` group at `20` fires, switches to `basic` then rebinds `628,1000` at 80000 = the remaining 80% |
| `FieldData_7015.xml:316-318` | `620,1001` at 6667 + `620,1004` at 6667 + `620,1005` at 6666 | 20000 = 20% | `progress` group at `20` fires, rebinds `620,1000` at 80000 |

Both events declare `dividerPercent="20,100"`, matching exactly.

Note the idiom at `FieldData_7003.xml:206-207` and `FieldData_7005.xml:360-361`: to rebind
`npcHp` to a new target, the data first issues `progressType="basic"` and *then* the new
`npcHp` task. Reading this as "clear the old binding, then install the new one" is the only
interpretation consistent with the fact that bindings otherwise accumulate.

### 2.4 `dividerPercent` is cosmetic, and this is provable

The natural assumption is that a `progress` group can only fire at a percentage declared in
`dividerPercent`. **This is false.**

`FieldData_7001.xml` event 2 has a `Progress` element with **no `dividerPercent` attribute at
all**, yet carries 13 `EventGroup type="progress"` triggers at values
2, 12, 22, 32, 33, 43, 53, 63, 64, 74, 84, 94 and 100. It is a shipped event, present in a live
rotation group (`FieldEvent.xml:44`), so those triggers demonstrably fire.

Correlating every event in the corpus:

| Event | `dividerPercent` | `progress` group values | Consistent |
|---|---|---|---|
| 7003 ev1 | `25,50,100` | 25, 50, 100 | yes |
| 7003 ev2 | `30,70,100` | 30, 70, 100 | yes |
| 7005 ev1 | `20,100` | 20, 100 | yes |
| 7011 ev1 | `10,25,100` | 10, 25, 100 | yes |
| 7012 ev1 | `15,30,100` | 15, 30, 100 | yes |
| 7015 ev1 | `20,100` | 20, 100 | yes |
| 7021 ev1 | `50,80,100` | 50, 80, 100 | yes |
| 7014 ev2 | `100` | 100 | yes |
| **7001 ev2** | **absent** | **13 values** | **no** |

Conclusion: `dividerPercent` draws the tick marks on the client's progress bar and nothing else.
Keeping it in sync with the trigger values is an authoring convention that 14 of 15 events follow
because the ticks should show players where the phases are. Author it in sync, but do not treat a
missing entry as the reason a trigger did not fire.

**Consequence for our pipeline:** `dividerPercent` is one of only two `Progress` attributes the
client half carries (`Field.xsd`, `Field_FieldEvent_Progress`). Changing the phase boundaries
requires a client sync or the ticks will not match the server's real phase gates.

### 2.5 Worked example, traced end to end

`FieldData_7012.xml`, "[Guardian Mission] Supply Wagon Escort". Continent 7012, hunting zone 627,
330 second clock, bar of 100000 split `15,30,100`.

| Step | Line | Trigger | Effect on the bar | Phase state |
|---|---|---|---|---|
| 1 | 133 | `initialize` | none | Flags zeroed, 9 event territories spawned, 29 world territories despawned, scoring rule 1 on, guide 7 shown |
| 2 | 194 | `userCountInTerritory 627,62700001 value=1` | none | Sets `기본버프` and `캠핑페널티`, which start two self-retriggering buff loops (203, 218) |
| 3 | 232 | `progressTimer value=320` | none | 10 seconds in: intro speech bubbles |
| 4 | 241 | `progressTimer value=310` | none | 20 seconds in: cutins, guide 7 to 8, sets `시작시간` and `예외처리1` |
| 5 | 254 | `enterTerritory 627,62700022` (no `targetNpcId`, so a **player**) | none | Sets `시작지점` |
| 6 | 261 | `flag 시작시간,시작지점,예외처리1` | none | Conjunction gate: time elapsed AND player at the wagon AND window open. Wagon and Karrak swap from static to patrolling placements. The convoy starts walking. |
| 7 | 281 | `enterTerritory 627,62700003 targetNpcId=627,1001` (the **wagon**) | opens a `basic` segment of 15000 | **Phase 1.** 16 mobs spawned pre-aggroed onto the wagon, kill counter `1지점킬` opened on templates 1003 and 1004, wave timer `1p` started, guide 2 and 3 shown, `changePos start`+`revive` moved to area 2 |
| 8 | 323 | `timer 1p value=15 repeat=true` | none | Every 15 seconds, one of three suicide-bomber territories spawns (probability 0.334 / 0.333 / 0.333) and the timer restarts. Pressure, not progress. |
| 9 | 343 | `killCount min=1 max=15 killCountName=1지점킬` | `plus 1000` per count | 15 kills x 1000 = **15000 raw = 15%** |
| 10 | 351 | `progress value=15` | none | **Phase 1 ends.** Timer stopped, counter stopped, 16 mob territories despawned, guides completed and swapped, convoy swapped back to patrolling placements and walks on |
| 11 | 397 | `enterTerritory 627,62700004 targetNpcId=627,1001` | opens a second `basic` segment of 15000 | **Phase 2.** Scoring rule 1 off, rule 2 on (higher coefficient). 6 tougher mobs, counter `2지점킬` on templates 1007 and 1008, wave timer `2p`, guide 4 and 5, `changePos` to area 3 |
| 12 | 453 | `killCount min=1 max=6 killCountName=2지점킬` | `plus 2500` per count | 6 kills x 2500 = **15000 raw**, bar now at **30%** |
| 13 | 461 | `progress value=30` | none | **Phase 2 ends.** Same teardown shape as step 10 |
| 14 | 497 | `enterTerritory 627,62700005 targetNpcId=627,1001` | rebinds to `npcHp` on `627,1013` | **Phase 3.** Scoring rule 2 off, rule 3 on (highest coefficient). Boss territory 62700021 spawned pre-aggroed onto the wagon. The boss's HP now owns the remaining 70% of the bar. `changePos` to area 4 |
| 15 | 664 | `progress value=100` | none | Sets `임무완료` |
| 16 | 671 | `flag 임무완료,일회성` | none | Success branch. Consumes the `일회성` one-shot latch so the failure branch cannot also run |
| 17 | 555 | `progressTimer value=0` | none | Sets `임무종료`. Two failure branches (564, 587) discriminate on whether the boss had appeared, each also consuming `일회성` |
| 18 | 695 | `beforeDeleteEvent` | none | 62 event territories despawned, then the 28 world territories respawned with `isEventNpc="false"` |

The three phase gates are `enterTerritory` on the escorted npc. The three phase *terminations*
are `progress` percentage triggers. The two mechanisms interlock: arriving somewhere opens a
phase, completing the work there closes it and releases the convoy toward the next arrival.

### 2.6 The one-shot latch

Steps 16 and 17 above are a race between a success branch and up to two failure branches. The
corpus solves this with a latch flag. `initialize` sets `일회성` to 1 (`FieldData_7012.xml:138`).
Every terminal branch requires it in its conjunction and clears it as its **first** task:

```
<EventGroup type="flag" name="임무완료,일회성" repeat="false">      <!-- success, L671 -->
    <EventTask type="flag" name="일회성" value="0" next="none" />
```

Whichever branch fires first removes the flag, so the others can never satisfy their conjunction.
Any multi-outcome ending needs this or it will run two endings.

### 2.7 Other real mechanisms, and one that is not

| Mechanism | Real | Notes |
|---|---|---|
| `initialize` | yes | 16 uses. Setup and world takeover. |
| `beforeDeleteEvent` | yes | 10 uses. Teardown and world restore. |
| `beforeEndEvent` | yes | 10 uses, but **9 of them are empty task groups**. Only meaningful in one file. Prefer `beforeDeleteEvent`. |
| `enterTerritory` | yes | 4 uses, **all four in the escort file**. See section 3. |
| `changePos` | yes | 49 uses. See 3.4. |
| `killCount` groups | yes | 4 uses in 2 files. See 2.8. |
| Flag gates | yes | 112 `flag` groups plus 377 `checkFlag` attributes. |
| Timers and waves | yes | 26 `timer` groups, 98 `timer` tasks. |
| `AutoEventBalance` | yes | 14 uses, two independent child mechanisms (1.8). |
| `ClearRewardPool` | yes but degenerate | 3 uses, each with exactly one entry at full weight. The weighting is never exercised. |
| `AutoUserBalance` | **no** | Zero live `Balance` rows corpus-wide. One live but empty element; 7 more exist only inside comments. Unproven. |

### 2.8 The `killCount` mechanism in detail

A counter is opened by a task and range-tested by a group.

Task (`FieldData_7012.xml:304`):
```
<EventTask type="killCount" action="start" value="0" killCountName="1지점킬"
           targetType="specificNpc" huntingZoneId="627" npcTemplateId="1003,1004" next="none" />
```

Group (`FieldData_7012.xml:343`):
```
<EventGroup type="killCount" min="1" max="15" killCountName="1지점킬" repeat="false">
    ... <EventTask type="progress" action="plus" value="1000" next="none"/>
```

The group fires **once per integer in the range**, not once for the whole range. This is forced by
the arithmetic, and it holds across all four shipped counters in two independent files:

| File | Counter | Range | Per-count grant | Product | Matches |
|---|---|---|---|---|---|
| 7012 | `1지점킬` | 1 to 15 | 1000 | 15000 | `progress` group at 15, `dividerPercent` 15 |
| 7012 | `2지점킬` | 1 to 6 | 2500 | 15000 | bar to 30000, `progress` group at 30 |
| 7011 | `새킬` | 1 to 10 | 1000 | 10000 | `dividerPercent` 10 |
| 7011 | `쿠차트킬` | 1 to 3 | 5000 | 15000 | bar to 25000, `progress` group at 25 |

Four for four. `repeat="false"` therefore means "do not re-fire for a count value already seen",
which is what makes the total exact.

`npcTemplateId` accepts a comma list, so one counter can span several mob types. `stop` rows may
either repeat the full binding (7011) or carry only `action` and `killCountName` (7012); both
spellings work.

---

## 3. The Escort Mission, Torn Down

`FieldData_7012.xml` is the only shipped event that physically relocates the objective across the
map, and it is the correct donor for a moving multi-phase design.

### 3.1 Cast

| Template (zone 627) | Role | Key territories |
|---|---|---|
| `1001` | The supply wagon. The thing that moves and that phases key on. | 62700022 static, 62700023/24/25/26 patrolling |
| `1011` | Karrak, the escorting npc | 62700039 static, 62700040/42/44 patrolling, 62700041/43/45 static-in-combat |
| `1003`, `1004` | Leg 1 enemies (cougar, kobold) | 62700007 to 62700014, 62700046 to 62700053 |
| `1007`, `1008` | Leg 2 enemies (wendigo warrior, wendigo shaman) | 62700015 to 62700020 |
| `1013` | The boss | 62700021 |
| `1010` | Suicide bombers, spawned by the wave timer | 62700027 to 62700032, 62700065 to 62700067 |
| `1012` | Reinforcements at the end | 62700056, a single territory holding **6** npcs |
| `9001`, `9002`, `9000` | Faction banners and a cinematic npc | 62700033 to 62700038, 62700068, 62700055 |

### 3.2 The checkpoint territories

`62700003`, `62700004`, `62700005` and `62700006` (`TerritoryData_627.xml:59,67,75,83`) are
`type="quest"` territories with a `Fence` polygon and **zero `Npc` children**. They are pure
geometry: invisible trip wires. `62700006` is a fourth checkpoint that no event group references,
so the band was cut one leg short of what was laid out.

### 3.3 How the objective actually moves

This is the single most important mechanical detail, and it is not in the field event file at all.
It is in the territory data.

An npc moves by being **despawned in one placement and respawned in another placement of the same
template**, where the two placements differ in their `PatrolList`.

| Territory | desc | `ai` | `isAggressiveMonster` | `Patrol` waypoints |
|---|---|---|---|---|
| `62700022` | wagon, pre-departure | 1001 | false | **0** |
| `62700023` | wagon, departing | 1001 | false | **3** |
| `62700024` | wagon, departing from point 1 | 1001 | false | **2** |
| `62700039` | Karrak, waiting | 9002 | false | **0** |
| `62700040` | Karrak, moving to point 1 | 9002 | false | **3** |
| `62700041` | Karrak, fighting at point 1 | **1011** | **true** | **0** |

The last waypoint of `62700040` is `-56348,-71416,48`; the fixed position of `62700041` is
`-56355,-71408,47`. Same spot to within a few units. So the sequence is:

1. Spawn the patrolling placement. The npc walks the waypoint chain.
2. It crosses the checkpoint fence, firing `enterTerritory ... targetNpcId`.
3. That group despawns the patrolling placement and spawns the static combat placement at the
   patrol's terminus, which also swaps the `ai` id and flips `isAggressiveMonster` to true.

The npc appears to arrive and turn to fight. Nothing in the field event file expresses movement;
the field event only switches between prepared placements. **AI is bound at placement, not on the
template**, which is what makes the same template behave as a walker and then as a fighter.

Compare `FieldData_7012.xml:273-276` (start walking) with `286-287` (arrive and fight):

```
<EventTask type="despawn" huntingZoneId="627" territoryId="62700039" next="none" />   <!-- Karrak waiting -->
<EventTask type="despawn" huntingZoneId="627" territoryId="62700022" next="none" />   <!-- wagon parked -->
<EventTask type="spawn"   huntingZoneId="627" territoryId="62700040" next="none" />   <!-- Karrak walking -->
<EventTask type="spawn"   huntingZoneId="627" territoryId="62700023" next="none" />   <!-- wagon rolling -->
```

### 3.4 `changePos`, leg by leg

`changePos` rewrites the event's entry point and its respawn point. It is always issued as a
**pair**, `start` then `revive`, pointing at the same `SpawnAreaList`:

| Line | Leg | Tasks | Area | `SpawnArea.center` |
|---|---|---|---|---|
| (implicit) | Start | `FieldEvent startPos` / `revivePos` | area 1 | `-59162,-71576,61` |
| 317, 318 | Phase 1 | `changePos method="start" id="2"` + `method="revive" id="2"` | area 2 | `-57340,-71815,-17` |
| 424, 425 | Phase 2 | `id="3"` pair | area 3 | `-54988,-73122,119` |
| 525, 526 | Phase 3 | `id="4"` pair | area 4 | `-53260,-74295,196` |

The four centres trace the convoy route. The effect is that a player who joins late, or who dies,
arrives at the *current* front rather than back at the start line. Without this, a moving event
strands everyone who was not there at the beginning.

The pairing is universal: all 7 `revive` uses in the corpus sit immediately next to a `start` use
with the same `id`, in `FieldData_7011.xml:414-415`, `7012:317-318, 424-425, 525-526` and
`7015:370-371`. The only exceptions are `7003:558-559` and `7021:195-196`, which set `start` and
`revive` to *different* areas once during `initialize`.

The other `changePos` idiom, in `FieldData_7003.xml:578-742` and `FieldData_7021.xml:217-381`, is
unrelated to phases: 15 `userCountInEvent` groups move the entry point as the crowd grows, so that
players 1 to 9 land at area 1, 10 to 14 at area 2, and so on. That is load spreading, not phasing.

### 3.5 The pre-aggro trick

Every combat spawn in the escort carries two extra attributes:

```
<EventTask type="spawn" huntingZoneId="627" territoryId="62700007"
           targetNpcId="627,1001" startAggro="10000" next="none" />
```

`targetNpcId` names the wagon and `startAggro="10000"` seeds the aggro table. The wave arrives
already committed to attacking the escorted object rather than idling until a player pulls it.
All 24 `startAggro` uses are `10000`, and all of them are in the escort file.

### 3.6 Wave composition: one mob per territory

The escort's phase 1 wave is **sixteen separate territories, each holding exactly one npc**
(`62700007` to `62700014` and `62700046` to `62700053`). Phase 2 is six such territories. The boss
is one territory with one npc (`62700021`).

The alternative shape exists too: `62700056` is one territory holding **six** npcs of template
`1012`, the end-of-mission reinforcements.

The distinction is operational, not stylistic:

| Shape | When to use |
|---|---|
| N territories x 1 npc | When the event must despawn or reference them individually, and when each needs its own hand-placed position. The escort despawns its entire leg-1 wave one territory at a time at `FieldData_7012.xml:362-377`. |
| 1 territory x N npcs | When the group is spawned and removed as a unit and individual placement does not matter. |

There is no count or density attribute on the `spawn` task. **The size of a wave is decided
entirely in the territory data.**

### 3.7 The wave timer

`FieldData_7012.xml:323` runs pressure independently of progress:

```
<EventGroup type="timer" name="1p" timerName="1p" value="15" repeat="true">
    <EventTaskGroup probability="0.334">
        <EventTask type="spawn" ... territoryId="62700027" next="none" />
        <EventTask type="timer" action="start" name="1p" direction="forward" value="0"
                   timerUiOff="true" next="time" nextValue="3.0" />
        <EventTask type="aiCombatWork" workId="301" targetNpcId="627,1010" next="none" />
```

The group restarts its own timer, so it is a self-perpetuating 15 second loop. The three
probability branches pick which of three bomber territories spawns. `timerUiOff="true"` hides it
from the player. The loop is killed by `timer action="stop"` in the phase-end group
(`FieldData_7012.xml:354`). Forgetting that stop would leak bombers into the next phase.

### 3.8 Scoring escalation

The escort rotates which scoring rule is live as phases advance, so later phases are worth more
per point of damage:

| Phase | Line | Rule on | Coefficient |
|---|---|---|---|
| Setup | 186 | rule 1 | `dealing` 0.60 |
| Phase 2 | 400, 401 | rule 1 off, rule 2 on | `dealing` 0.90 |
| Phase 3 | 500, 501 | rule 2 off, rule 3 on | `dealing` 1.6 |

Rule 5 (`checkAbnormality` on `6270002`, coefficient 0.0) is toggled off whenever the wagon is
stopped and on whenever it moves (313, 392, 427, 492, 521). Since its coefficient is 0.0 it scores
nothing; it is a disabled hook left in place.

---

## 4. Recipe for Our Three-Phase Event

Design target: phase 1 a swarm of weak minions near a camp, phase 2 a larger wave of stronger
raiders further out, phase 3 a boss at the enemy camp, with the staging point advancing each time.

Our event is `FieldData_13.xml`, continent 13, event id 1, in **live world hunting zone 13**.
Continent 13 already carries `channelType="field"` (`ContinentData.xml:119`) and already has a
rotation entry (`FieldEvent.xml:66-68`), so both prerequisites are satisfied.

### 4.1 Structural difference from the donor, and why it simplifies

The escort's phases are gated by an **npc** crossing a fence. Our design has no escorted object;
the **players** move. That is a strictly easier problem, and the shipped data already contains
the primitive:

- `EventGroup type="enterTerritory" uniqueId="13,TERR"` with **no** `targetNpcId` fires on a
  player. Proven at `FieldData_7012.xml:254`.
- `EventGroup type="userCountInTerritory" uniqueId="13,TERR" value="N"` fires when N players are
  inside. 18 shipped uses, including our own event's existing start gate.

Prefer `userCountInTerritory` with `value="1"` for our staging gates. It is the far better attested
of the two (18 uses versus 4), it is what our v0 already uses successfully, and requiring a
headcount is a natural fit for "the group has arrived".

We therefore do **not** need patrolling placements, the static/patrol placement pairs, `ai` swaps,
`startAggro`, or the `targetNpcId` form of `enterTerritory`. The whole of section 3.3 is donor
detail we can skip.

### 4.2 Territories to author in `TerritoryData_13.xml`

Extend group `1300062` (`TerritoryData_13.xml:7680`). The `13017xxx` band is ours and is free above
`13017020`; hunting zone 13 has 650 territories and none between `13017021` and `13017999`.

Every one of these must be `type="quest"`. A `normal` territory here would spawn at world start and
leak permanently into the live Island of Dawn population.

| Territory | Type | Npcs | Purpose |
|---|---|---|---|
| `13017000` | quest | 0 | Mission boundary (exists) |
| `13017010` | quest | 0 | Phase 1 staging pad, start gate (exists) |
| `13017020` | quest | 1 | Currently the v0 boss. **Repurpose as the phase 3 boss spawn.** |
| `13017030` | quest | 0 | Phase 2 staging pad, fence only |
| `13017040` | quest | 0 | Phase 3 staging pad, fence only |
| `13017101` to `13017112` | quest | 1 each | Phase 1 swarm, 12 weak minions near the camp |
| `13017201` to `13017210` | quest | 1 each | Phase 2 raider wave, 10 stronger raiders at the outer point |
| `13017301` to `13017303` | quest | 1 each | Optional phase 3 boss adds |

One npc per territory for the two waves, following the donor. It costs more territory rows but it
is what lets the phase-end group despawn the wave precisely, and it is how all four shipped waves
are built.

### 4.3 Progress budget

Bar is 100000. Allocate the three phases as `20 / 30 / 50`:

| Phase | Mode | Raw allocation | Filled by |
|---|---|---|---|
| 1, swarm | `basic`, `value="20000"` | 20000 (0 to 20%) | 12 kills x `progress plus 1667` (12 x 1667 = 20004, rounds over the gate, which is correct and harmless) |
| 2, raiders | `basic`, `value="30000"` | 30000 (20 to 50%) | 10 kills x `progress plus 3000` = 30000 exactly |
| 3, boss | `npcHp`, `targetNpcId="13,902"` | remaining 50000 | Boss HP |

Cleaner alternative for phase 1 that avoids the rounding: 10 minions x 2000. If we want 12 mobs on
the field but only 10 counted, that is fine, the counter range is what gates it.

Set `Progress dividerPercent="20,50,100"`, and mirror it in the client `Field` entry.

**Add the `AutoEventBalance/Balance/Setting` ladder** (section 1.8) verbatim from
`FieldData_7003.xml:420`. Without it, phase 1 and 2 complete in seconds if more than a handful of
players attend, because every kill grants its full raw allocation regardless of headcount. Our
current event has no `AutoEventBalance` element at all.

### 4.4 Element-by-element authoring list

**`FieldEvent` header** (`FieldData_13.xml:3`): keep as is. Optionally add `nonPkSectionId`.

**`Progress`** (line 9): change `dividerPercent` from `100` to `20,50,100`, change
`syncNpcHpInterval` from `3` to `1` for the boss phase.

**`AutoEventBalance`**: new. 17 `Balance` rows, each with one `Setting progressType="basic"`, plus
`BasicAbnormality targetNpcId="0,0"` rows if we want npc stat scaling too.

**`SpawnAreaList`**: new, three lists. Area 1 at the existing `startPos` `51959,-78919,-4631`,
area 2 at the phase 2 staging point, area 3 at the enemy camp.

**`Guide`**: extend from 2 tasks to 5 (one per phase objective, plus the existing complete line).
New `@field:` strings needed in `StrSheet_Field`.

**`EventPoint`**: see section 5, the coefficient must change.

**Trigger groups to author:**

| # | Group | Purpose |
|---|---|---|
| 1 | `initialize` | Set `oneshot=1`, despawn overlapping world territories, add guide 1 |
| 2 | `progressTimer value="320"` | Opening message (exists) |
| 3 | `userCountInTerritory uniqueId="13,13017010" value="1"` | Sets `phase1ready` (exists as `ready`) |
| 4 | `flag name="phase1ready" repeat="false"` | **Phase 1 opens.** `progressType basic value="20000"`, `point id=1 turn=on`, spawn the 12 swarm territories, `killCount action="start" killCountName="swarm" targetType="specificNpc" huntingZoneId="13" npcTemplateId="<minion>"`, guide 1 add |
| 5 | `killCount min="1" max="12" killCountName="swarm" repeat="false"` | `progress action="plus" value="1667"` |
| 6 | `progress value="20" repeat="false"` | **Phase 1 closes, phase 2 stages.** `killCount action="stop"`, despawn the 12 swarm territories, guide 1 complete then remove, guide 2 add, `changePos start id="2"` + `changePos revive id="2"`, message pointing at the outer point |
| 7 | `userCountInTerritory uniqueId="13,13017030" value="1"` | Sets `phase2ready` |
| 8 | `flag name="phase2ready" repeat="false"` | **Phase 2 opens.** `progressType basic value="30000"`, point rotate, spawn the 10 raider territories, `killCount start` on `raiders`, guide 2 remove, guide 3 add |
| 9 | `killCount min="1" max="10" killCountName="raiders" repeat="false"` | `progress action="plus" value="3000"` |
| 10 | `progress value="50" repeat="false"` | **Phase 2 closes, phase 3 stages.** counter stop, despawn the 10 raider territories, guide 3 complete then remove, guide 4 add, `changePos start id="3"` + `changePos revive id="3"` |
| 11 | `userCountInTerritory uniqueId="13,13017040" value="1"` | Sets `phase3ready` |
| 12 | `flag name="phase3ready" repeat="false"` | **Phase 3 opens.** `progressType progressType="npcHp" targetNpcId="13,902"`, point rotate to the highest coefficient, spawn `13017020` and any adds, guide 4 add |
| 13 | `progress value="100" repeat="false"` | Sets `success` |
| 14 | `flag name="success,oneshot" repeat="false"` | Success ending. Clears `oneshot` first. |
| 15 | `progressTimer value="30" / "20" / "10"` | Countdown warnings (exist) |
| 16 | `progressTimer value="0" repeat="false"` | Sets `timeup` |
| 17 | `flag name="timeup,oneshot" repeat="false"` | Failure ending. Clears `oneshot` first. |
| 18 | `beforeDeleteEvent` | Despawn all `13017xxx` event territories, then respawn the world territories from step 1 with `isEventNpc="false"` |

Optional, following the donor: a `timer` group looping every 15 to 20 seconds during phases 1 and 2
that spawns a single extra mob, to keep pressure on. Remember the matching `timer action="stop"` in
the phase-close group.

### 4.5 World takeover, exact ops and ordering

Our v0 skips this. It runs its territories in a live world zone alongside ambient mobs, and the
domain doc records the live-measured consequence: players cannot tell what belongs to the event.

The shipped pattern, distribution across the corpus (509 despawns and 506 spawns resolving to
`normal` territories):

| Phase | Group type | Task | Despawns | Spawns |
|---|---|---|---|---|
| Takeover at start | `initialize` | `despawn` | 74 | 0 |
| Swap per phase | `flag` | `despawn` then `spawn` | 434 | 433 |
| Restore at teardown | `beforeDeleteEvent` | `spawn isEventNpc="false"` | 1 | 73 |

The escort is the clean minimal example:

- `initialize` (`FieldData_7012.xml:156-184`): 29 `despawn` tasks, all against hunting zone **34**,
  which is the *world* zone underneath, not the event's zone 627. All `next="none"`, all in one
  task group, executed in file order.
- `beforeDeleteEvent` (`FieldData_7012.xml:698-789`): first 62 `despawn` tasks against the event's
  own zone 627, **then** 28 `spawn isEventNpc="false"` tasks against zone 34. Event content is
  removed before the world is put back. One world territory (`3400808`, despawned at line 162) is
  never restored, which is a shipped bug worth not copying.

For us the world zone and the event zone are **the same zone, 13**. So the ordering discipline is
what keeps it straight: despawn the specific ambient `type="normal"` territories that overlap our
mission footprint on `initialize`, and respawn exactly that list with `isEventNpc="false"` at
`beforeDeleteEvent`, after despawning our own `13017xxx` territories.

`isEventNpc="false"` appears 495 times and is **always** `false`. It exists solely to mark a spawn
as "putting the world back" rather than "spawning event content". There is no `true`.

### 4.6 Client half

`Field.xsd` (`client-dc\DataCenter_Final_EUR\Field\Field.xsd`) shows the client carries only:

```
Field/FieldEvent  @id @startPos @reviveTownNameId [@type @cantTeleport @rustleSoundOff]
  ├── FieldEventCloud   (optional)
  ├── Guide             (optional)   @titleString @eventSize @description, Task+, Marker*
  └── Progress          (required)   @dividerPercent
```

No `EventGroup`, no `Condition`, no `EventPoint`. So the client sync is needed exactly when
`Guide`, `dividerPercent`, `startPos` or `reviveTownNameId` change. Our phase work changes
`dividerPercent` and `Guide`, so a sync is mandatory.

Current client entry: `client-dc\DataCenter_Final_EUR\Field\Field-00000.xml`.

**Strings** go in `StrSheet_Field`. Ours already occupy `1301`, `13010`, `1301001` to `1301003`,
`1301910`, `1301920`, `1301930` (`StrSheet_Field-00000.xml:50-57`). Extend the `1301xxx` band for
the new per-phase objective and transition text. The generic strings `100001` ("Defeat {target}."),
`100003` ("Protect {target}.") and `111111` ("Mission Complete") are reusable as is.

**Cutins** (`eventDialog` tasks) are **client-only** and need a `Dialog` row in
`client-dc\DataCenter_Final_EUR\EventDialog\EventDialog-00000.xml`. `EventDialog.xsd` requires
all seven attributes: `id`, `continentId`, `dialogStrId`, `duration`, `imgPath`, `pingLoc`,
`titleStrId`. The string comes from `StrSheet_EventDialog`, not `StrSheet_Field`.

### 4.7 What our design needs that the data cannot express

| Need | Status | Detail |
|---|---|---|
| Wave size as a parameter | **Cannot express.** | There is no count or density attribute on `spawn`. Wave size is fixed in territory data. Changing "12 minions" to "20 minions" is a territory edit, not an event edit. |
| Scaling wave size to headcount | **Cannot express.** | `AutoEventBalance` scales npc *stats* and progress *rate*. It cannot add npcs. The shipped workaround is `dynamicSpawn` (693 uses in 7021 and 7003), which spawns from a `DynamicSpawn` template without a pre-defined territory, but the shipped uses are driven by timers and probability branches, not by headcount. |
| Respawning a wave as it is cleared | **Only via re-spawning the whole territory.** | The `timer` loop idiom (3.7) is the shipped answer, and it spawns a *different* territory each tick rather than refilling one. |
| Moving the boss between phases | **Cannot express directly.** | Requires the donor's despawn-and-respawn-a-different-placement trick, with patrol waypoints authored in territory data. Our design places the boss statically at the camp, so this does not bite. |
| Ending the event when the bar fills | **Not supported as configured.** | `endWhenProgressFull` is `false` in all 16 shipped events, so its `true` behaviour is unproven. The event will run out its 330 seconds after the boss dies. Budget the clock so phase 3 can finish comfortably inside it. |
| Removing an abnormality mid-event | **Unproven.** | All 55 `abnormality` tasks are `turn="on"`. `turn="off"` has zero uses. |
| Absolute npc HP changes | **Unproven.** | All 416 `changeHp` tasks are `method="rate"`. |
| Level-appropriate reward scaling | **Absent from the whole chain.** | See section 5. There is no automatic level normalisation anywhere. |
| Per-phase reward grants | **Cannot express.** | Rewards are computed once, globally, from the point total. There is no per-phase reward task. |

---

## 5. Reward Calibration Data

### 5.1 The two-stage multiplier, which is the thing that breaks low-level events

Contribution points are **not** the per-event coefficient alone. There is a global per-type rate in
`FieldEvent.xml:70-84` that multiplies it:

```
points = raw_metric x Point.value x EventPoint.defaultRate
```

| Global `EventPoint` | `defaultRate` | Class overrides |
|---|---|---|
| `dealing` | **0.001** | priest 0.00115, lancer 0.0018, fighter 0.00117, engineer 0.00105 |
| `healing` | **0.0** | `class="priest,elementalist"` also 0.0 |
| `checkAbnormality` | 1.0 | none |
| `checkTerritory` | 1.0 | none |
| `npcInteraction` | 1.0 | none |

The comment above the `dealing` block (`FieldEvent.xml:71`) states the coefficient was cut to
1/1000 for the flying non-combat content rework. That global 1/1000 applies to **every** event.

Two immediate consequences:

- `healing` scores **nothing anywhere**, globally, despite 11 shipped `Point type="healing"` rows.
  Do not author a healing rule expecting it to pay.
- `dealing` is a thousand times weaker than the per-event coefficient suggests.

### 5.2 Why our event's reward is unreachable, quantified

| Quantity | Value | Source |
|---|---|---|
| Our `Point type="dealing" value` | 1.45 | `FieldData_13.xml:11` |
| Global `dealing` `defaultRate` | 0.001 | `FieldEvent.xml:72` |
| Effective points per point of damage | **0.00145** | product |
| Participation bag `requiredPoint` | 100000 | `FieldEvent.xml:87` |
| Damage needed for one bag | **69.0 million** | 100000 / 0.00145 |
| Measured yield at level 8 | about 1 point per 2 kills | live measurement 2026-07-28 |
| Implied kills for one bag | **about 200,000** | from the measurement |

The measurement and the arithmetic agree: 1 point per 2 kills implies about 690 damage per point,
which is exactly 1/0.00145. A level 8 mob is worth roughly 690 damage. The reward is unreachable by
about four orders of magnitude.

### 5.3 Shipped coefficients, for reference

| Value | Type | Where |
|---|---|---|
| 0.24, 0.35, 0.60, 0.63, 0.90, 0.96, 1.2, 1.45, 1.6 | `dealing` | across the corpus, all paired with level 65 to 70 content |
| 1.0, 1.05 | `healing` | scores zero because of the global rate |
| 0.0, 1.75, 3.5, 5.25 | `checkAbnormality` | 7 rows |
| 1.0 | `npcInteraction` | 3 rows |

Every shipped `dealing` coefficient assumes a max-level character hitting max-level content.
Reusing one at level 8 does not scale down, it collapses.

### 5.4 Calibration levers, ranked

**Do not touch `FieldEvent.xml` `defaultRate`.** It is global and would rebalance all 16 shipped
events.

**Lever 1, raise the per-event `dealing` coefficient.** This is the correct knob: it is per-event
and it is exactly what the shipped data varies.

Working from the live measurement (about 690 effective damage per level 8 kill), for a target of
one full participation bag per completed run:

| Target kills per bag | Total damage | Required `Point value` |
|---|---|---|
| 22 (our phase budget: 12 + 10) | 15,180 | **6,600** |
| 50 | 34,500 | **2,900** |
| 100 | 69,000 | **1,450** |

So a `Point type="dealing" value` in the low thousands is the right order of magnitude for a level
7 to 15 event. Recommend starting at **2900** (about 50 kills for a bag, roughly two full runs of
the three phases) and confirming with `/@showfeprogress` on a live run.

Caveat: the shipped domain is 0.24 to 1.6, so a value of 2900 is three orders of magnitude outside
anything shipped. There is no evidence of a cap, but there is also no evidence there is not one.
This needs a live probe before it is trusted.

**Lever 2, `npcInteraction`.** `defaultRate` is 1.0, so `Point type="npcInteraction" value="50000"`
would grant 50000 points per interaction and two interactions would fill a bag. Clean and
predictable, but it requires an `InteractionRule` with `inFieldEvent="true"` and an
`interactionRuleId` on the territory placement. This is the only case in the whole system where
data outside the event definition has to know the event exists.

**Lever 3, `checkTerritory`.** `defaultRate` is 1.0 and it is the natural "participation" metric,
but **no shipped event uses it in a `Point` row**, so its tick period is entirely unknown. Do not
rely on it without a probe.

### 5.5 The reward tables themselves need no change

`FieldEvent.xml:86-96`:

```
FieldEventReward
└── RewardBag requiredPoint="100000" repeat="40"
    ├── Level minLevel="1"  maxLevel="64"   → Reward item 98582 x1
    └── Level minLevel="65" maxLevel="70"   → Reward item 98582 x1 + reputationPoint guild 611 x250
```

The `1` to `64` band already covers our level 7 to 15 event and already grants an item. `repeat="40"`
means the bag can be earned up to 40 times in one event, so calibrating one bag per run leaves
plenty of headroom.

`FieldEventClearReward` holds three live `ClearReward` entries (`70030201`, `70210101`, `70050101`),
all `rule="point"` with `ruleValue` thresholds of 60000 to 175000. Our event carries no
`ClearRewardPool`, so it grants no clear reward. Adding one means authoring a new `ClearReward` in
the global file plus a `ClearRewardPool` in ours. Not required for the three-phase work.

### 5.6 Headcount scaling of the bar

Repeated from 1.8 because it is a calibration input, not a schema detail: the
`AutoEventBalance/Balance/Setting` ladder multiplies `basic` progress gains by roughly `1/N`.
With the ladder, 12 kills fill phase 1 whether 1 player or 30 players attend. Without it, 30
players fill it in one volley. Our event currently has no `AutoEventBalance` element.

---

## 6. Open Questions

These are not answerable from the shipped data and need a live probe.

| # | Question | Why the data cannot answer it | Suggested probe |
|---|---|---|---|
| 1 | Is `value` on `progressType progressType="basic"` a segment budget, a cap, or an absolute set of the bar? | Only 2 uses, both in the escort, both at points where budget and absolute-set readings give the same number (leg 1 starts at 0 with budget 15000; leg 2 starts at 15000 with budget 15000). The two readings are indistinguishable. | Author a `basic` segment with `value` deliberately different from the segment's start value, then `/@showfeprogress` after the first kill. |
| 2 | Is there an upper bound on `Point value`? | Shipped domain is 0.24 to 1.6. A value of 2900 is far outside it. | Set 2900, run, `/@showfeprogress` after a known number of kills, compare against the predicted 0.29 points per damage. |
| 3 | What is the tick period of `checkTerritory` scoring? | Declared globally with `defaultRate="1.0"` but used by zero shipped events. | Add a `Point type="checkTerritory" value="1"`, stand in the territory for 60 seconds, read the point total. |
| 4 | Does `endWhenProgressFull="true"` work? | All 16 shipped events set it `false`. | Set `true` on our event, fill the bar with `/@setfeprogress`, see whether the event ends before the clock. |
| 5 | Does a `killCount` group really fire once per integer in `min`..`max`? | Inferred from arithmetic across four counters in two files. Strong, but indirect. | Set `min="1" max="3"` with `progress plus 10000`, kill 3, confirm the bar reads 30%. |
| 6 | Does `killCount` count kills by any player, or only by the killer's party? | No attribute distinguishes them and no comment addresses it. | Two characters, one kills, the other watches the bar. |
| 7 | Does `userCountInTerritory` re-fire when the count drops and rises again? | `repeat` is absent on all 18 shipped uses, so the default is unobserved. | Enter, leave, re-enter the staging pad and watch for a duplicate phase open. |
| 8 | Do `changePos method="start"` and `revive` affect players already inside the event, or only those who arrive after? | Never stated. The escort's design implies "everyone from now on", but joiners and corpses are different cases. | Die during phase 2 and check the respawn point. |
| 9 | Does `abnormality turn="off"` work? | Zero uses in the corpus. | Apply then remove one, watch the buff bar. |
| 10 | Does `changeHp` support anything other than `method="rate"`? | All 416 uses are `rate`. | Not needed for our design. |
| 11 | What distinguishes `FieldEvent type="0"` from `type="1"`? | 3 uses, no behavioural correlate visible in the data. | Low priority. |
| 12 | Is `dividerPercent` genuinely cosmetic at runtime, as the 7001 evidence implies? | The evidence is strong (a live event with 13 triggers and no dividers) but it is one event. | Set `dividerPercent="100"` while running a `progress` group at 50, and see whether the phase still advances. |
