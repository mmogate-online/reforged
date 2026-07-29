# Orcan NPC and AI donor survey

Survey for three brand new authored Orcan monsters (minion swarm, raider, elite boss) for the
Island of Dawn Guardian Legion field event.

Read only survey. No datasheet was modified.

Sources:

- v92 server datasheet `<server_datasheet>`
- v31 server datasheet `<v31_datasheet>`
- v92 client DataCenter `<client_datacenter>`
- v31 client DataCenter `<client_dc_v31>`
- v17.11 client DataCenter `<old_client_dc>`
- Domain KB `<domain_docs>\entities\npc-system.md`,
  `...\entities\loot-system.md`

Parsing note: every scan below was run with `lxml` with `remove_comments=False` plus a raw text
regex pass, so commented out content is visible. Findings from comments are called out in
section 8.

---

## 1. Island of Dawn Orcan census

Two Orcan models exist, not one. They are separate meshes with separate races and separate
animation sets, so the minion tier and the raider tier do not share a model.

| shapeId | race | basicActionId | client animSet | reads as |
|---|---|---|---|---|
| 300650 | `OrcanPirate` (zone 13) / `Orcan` (zone 620) | 3006500 | `Orcan_ANI.Anim.Orcan_Anim` | full size Orcan warrior |
| 300710 | `OrcanMinimi` | 3007100 | `OrcanMinimi_ANI.Anim.OrcanMinimi_Anim` | small dwarf Orcan |

All Island of Dawn Orcan templates, from `<server_datasheet>\NpcData_13.xml`:

| tpl | line | display name (StrSheet_Creature) | internal name | shapeId | basicActionId | parentId | aiid | playStyle | size | scale | level | maxHp | atk | AI works | own skills | HZ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 494 | Dwarf Orcan | 미니 오칸 | 300710 | 3007100 | none | 32 | zarco | small | 0.5 | 7 | 669.27 | 1140 | 12 | 7 | 13 |
| 5 | 515 | Orcan Raider | 오칸 습격자 | 300650 | 3006500 | none | 31 | zarcoBoss | medium | 0.17 | 7 | 5949.05 | 11250 | 17 | 16 | 13 |
| 901 | 951 | Orcan Guardian | 오칸 | 300650 | 3006500 | 30065000 | 31 | basic | medium | 0.17 | 7 | 8094.19 | 11250 | 17 | 16 | 13 |
| 902 | 972 | Dwarf Guardian | 오칸미니미 | 300710 | 3007100 | 30071001 | 32 | zarco | small | 0.5 | 7 | 669.27 | 1140 | 12 | 7 | 13 |
| 1002 | 641 | Acharak | 오칸 | 300650 | 3006500 | none | 31 | zarcoBoss | medium | 0.17 | 8 | 13277.51 | 21220.31 | 17 | 16 | 13 |
| 1003 | 662 | Acharak's Soldier | 오칸미니미 | 300710 | 3007100 | none | 32 | zarco | small | 0.5 | 8 | 1239.79 | 3875.43 | 12 | 7 | 13 |

Column notes:

- `scale` is on the `Template` element. `size` is the small/medium/large category, a separate
  attribute; both are listed because the two are not derived from each other (`13,5` is
  `size="medium" scale="0.17"`, `453,20` is `size="small" scale="0.21"`, same model).
- "AI works" is the count of `Work` elements under the referenced `Ai` in
  `<server_datasheet>\AIData_13.xml`. AI 31 is at line 2500, AI 32 at line 2613.
- "own skills" is the count of `Skill` rows in
  `<server_datasheet>\NpcSkillData_13.xml` carrying that template's
  `templateId`. This is the correct key: `NpcSkillData` skills are keyed by
  `(templateId, id)`, not by `id` alone. A skill id like `1101` exists once per template and
  means a completely different thing for a different template.
- `SkillList` on the `Template` element is a dead field for every one of these. In
  `NpcData_13.xml` it holds a lone backtick (for example line 508 to 510 for template 4). The
  real skill binding runs `Template.aiid` -> `Ai.Work.normalBehaviorId` /
  `angerBehaviorId` -> `NpcSkillData.Skill[@templateId][@id]`.

Two hazards this table exposes, both already documented in the NPC domain doc and both live here:

- Internal `name` is not unique. `오칸` is shared by 901 and 1002 (Orcan Guardian vs Acharak),
  `오칸미니미` by 902 and 1003 (Dwarf Guardian vs Acharak's Soldier). Never key anything off
  `name`.
- `13,902` is the only unreferenced camp Orcan and is the current v0 event boss, per
  `reforged\specs\patches\002\34-iod-guardian-legion-v0.yaml`.
  It is a level 7 `zarco` minion with 669 HP and 7 skills. It is not a boss in any sense other
  than being safe to spawn.

The Docile Terron precedent named in the brief holds up: `13,102` is a `creature` playStyle variant
of the Terron family sharing `shapeId` 300940 and a `parentId` with its combat siblings. The Orcan
family works the same way, with `901` and `902` carrying `parentId` 30065000 and 30071001
respectively while `4`, `5`, `1002`, `1003` carry none.

---

## 2. Corpus wide same model census

Full scan of all 424 `NpcData_*.xml` files in the v92 server datasheet for `shapeId` 300650 or
300710. 55 templates found across 19 hunting zones. Ranked by AI and skill infrastructure carried.

Ranking key: `works` = `Work` count on the referenced AI, `skills` = `NpcSkillData` rows keyed to
that template, `pat` = `Pattern` count, `stw` = `StWork` (short term target) count.

### shapeId 300650 (full size Orcan)

| rank | hz | tpl | NpcData line | aiid | AIData line | works | skills | pat | stw | playStyle | size | scale | elite | level | maxHp | zone role |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 453 | 20 | 70 | 102 | 477 | 23 | 26 | 2 | 2 | zarco | small | 0.21 | false | 60 | 6,044.99 | dungeon, Kezzel's Gorge |
| 2 | 87 | 2031 | 1156 | 108 | 1250 | 23 | 26 | 2 | 2 | basic | medium | 0.21 | false | 51 | 182,776 | channelingZone, Ashen Hope |
| 3 | 87 | 2053 | 1260 | 113 | - | 23 | 26 | 2 | 2 | basic | medium | 0.21 | false | 1 | 2,660 | channelingZone, Ashen Hope |
| 4 | 11 | 4001 | 444 | 29 | - | 20 | 24 | 2 | - | zarcoBoss | medium | 0.19 | false | 33 | 43,461 | field |
| 5 | 41 | 2004 | 148 | 6 | - | 20 | 24 | 1 | - | basic | medium | 0.24 | false | 46 | 104,415 | field |
| 6 | 41 | 2005 | 169 | 7 | - | 20 | 24 | 1 | - | basic | medium | 0.24 | false | 46 | 104,415 | field |
| 7 | 833 | 1078 | 1532 | 85 | - | 20 | 24 | 1 | - | basic | medium | 0.24 | false | 65 | 1,467,188 | dungeon |
| 8 | 1022 | 203 | 110 | 10 | - | 17 | 24 | 2 | - | basic | medium | 0.30 | **true** | 60 | 1,258,332 | black rift, `huntingStyle="raid"` |
| 9 | 13 | 5 | 515 | 31 | 2500 | 17 | 16 | 1 | - | zarcoBoss | medium | 0.17 | false | 7 | 5,949 | Island of Dawn |
| 9 | 13 | 1002 | 641 | 31 | 2500 | 17 | 16 | 1 | - | zarcoBoss | medium | 0.17 | false | 8 | 13,278 | Island of Dawn |
| 9 | 13 | 901 | 951 | 31 | 2500 | 17 | 16 | 1 | - | basic | medium | 0.17 | false | 7 | 8,094 | Island of Dawn |
| 12 | 437 | 5 | 595 | 31 | - | 17 | 16 | 1 | - | zarcoBoss | medium | 0.17 | false | 8 | 2,052 | IoD dungeon layer |
| 12 | 437 | 11 | 721 | 31 | - | 17 | 16 | 1 | - | zarcoBoss | medium | 0.17 | false | 7 | 124,300 | IoD dungeon layer |
| 14 | **620** | **1001** | **3** | **1** | **128** | **11** | **13** | 1 | **2** | (empty) | **large** | **0.31** | **true** | 68 | 10,080,000,000 | **Guardian Legion mission, Veritas District** |
| 14 | 620 | 1004 | 44 | 1 | 128 | 11 | 13 | 1 | 2 | (empty) | large | 0.35 | true | 68 | 10,080,000,000 | Guardian Legion mission |
| 14 | 620 | 1005 | 65 | 1 | 128 | 11 | 13 | 1 | 2 | (empty) | large | 0.41 | true | 68 | 10,080,000,000 | Guardian Legion mission |
| 17 | 795 | 205 | 411 | 19 | - | 9 | 14 | 1 | - | (empty) | medium | 0.6 | false | 68 | 40,000 | (all skills `totalAtk=0`) |
| 18 | 620 | 9001/9002/9003 | 320/341/362 | 10 | - | 3 | 0 | 2 | - | (empty) | large | 0.31/0.35/0.41 | false | 65 | 12,000,000,000 | AI 100 style stub, no skills |
| 19 | 87 | 1038, 1043 | 830, 931 | 100 | - | 3 | 0 | 2 | - | basic | medium | 0.21 | false | 53 | 52,658 | generic AI 100, no skills |
| 19 | 29 | 5002 | 1634 | 100 | - | 3 | 0 | 2 | - | (empty) | medium | 0.21 | false | 30 | 200 | generic AI 100, no skills |
| 19 | 241 | 1008, 1011, 1012, 1013, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1026 | 93 onward | 100 | - | 3 | 0 | 2 | - | (none) | medium | 0.125 | (none) | 40 | 10,000 | named villager style, no combat |

### shapeId 300710 (dwarf Orcan)

| rank | hz | tpl | NpcData line | aiid | works | skills | playStyle | size | scale | level | maxHp | zone role |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 42 | 100 | 70 | 100 | 11 | 8 | zarco | small | 0.6 | 47 | 9,918 | field |
| 2 | 41 | 2003 | 127 | 5 | 10 | 8 | zarco | small | 0.6 | 46 | 10,560 | field |
| 2 | 453 | 10 | 51 | 101 | 10 | 8 | zarco | small | 1.0 | 60 | 12,090 | dungeon |
| 2 | 833 | 1079 | 1553 | 86 | 10 | 8 | basic | small | 1.0 | 65 | 489,060 | dungeon |
| 2 | 87 | 2011 | 972 | 104 | 10 | 8 | zarco | small | 1.0 | 50 | 36,080 | channelingZone |
| 2 | 87 | 2016 | 1074 | 139 | 10 | 8 | zarco | small | 1.0 | 51 | 24,304 | channelingZone |
| 2 | 87 | 2021 | 1114 | 106 | 10 | 8 | zarco | small | 1.0 | 48 | 31,332 | channelingZone |
| 2 | 87 | 2083 | 1665 | 151 | 10 | 8 | basic | small | 1.0 | 53 | 25,892 | channelingZone |
| 9 | 13 | 4 | 494 | 32 | 12 | 7 | zarco | small | 0.5 | 7 | 669 | Island of Dawn |
| 9 | 13 | 1003 | 662 | 32 | 12 | 7 | zarco | small | 0.5 | 8 | 1,240 | Island of Dawn |
| 9 | 13 | 902 | 972 | 32 | 12 | 7 | zarco | small | 0.5 | 7 | 669 | Island of Dawn |
| 9 | 437 | 4, 12 | 574, 742 | 32 | 12 | 7 | zarco | small | 0.5 | 7 | 360 / 17,400 | IoD dungeon layer |
| 14 | 1022 | 303 | 410 | 26 | 8 | 7 | zarco | small | 0.9 | 60 | 13,432 | black rift, `huntingStyle="raid"` |
| 15 | 12 | 5, 10 | 63, 168 | 3, 8 | 7 | 5 | zarco | small | 0.6 | 31 | 6,195 / 2,880 | field |
| 15 | 830 | 1001000 | 949 | 100100 | 7 | 5 | basic | medium | 0.6 | 65 | 3,456,000 | dungeon |
| 17 | 112 | 4001 | 106 | 5 | 4 | 3 | basic | medium | 1.5 | 65 | 161,968 | field |
| 18 | 1023 | 30071000 | 171 | 100 | 3 | 0 | servant | small | 0.5 | 50 | 169 | base/parent template |
| 18 | 29 | 5001 | 1613 | 100 | 3 | 0 | (empty) | small | 1.5 | 39 | 537 | generic AI 100, no skills |

### What the richest ones actually carry

**hz 620, templates 1001 / 1004 / 1005, AI 1** at `<server_datasheet>\AIData_620.xml:128`.
This is the Guardian Legion mission Orcan for Veritas District, hunting zone 620, and it is the
only same model creature in the corpus that is both `elite="True"` and `size="large"` and carries
a purpose built field event mechanic. Mechanics, all cited from AIData_620.xml AI 1:

| Work | desc | skill (normal / anger) | cooldown | condition | chain |
|---|---|---|---|---|---|
| 101 | basic attack | 1101 / 1101 | 5,000 ms | always | - |
| 102 | telegraph windup before a heavy hit | 1203 / 2203 | 40,000 ms | `GetHpRatio() < 0.8` | -> Work 312 at prob 1 |
| 312 | the heavy hit the windup pays off | 1106 / 2106 | 30,000 ms | always | - |
| 104 | **field event bomb with an alarm telegraph** | 1303 / 1303 | 50,000 ms | always | - |
| 105 | basic attack 4 | 1105 / 1105 | 12,000 ms | always | - |
| 106 | ultra attack, double lariat spin | 1102 / 2102 | 30,000 ms | always | - |
| 201 | exhaustion pant at 50 percent | 1201 | 6,000 ms | `GetHpRatio() < 0.5 AND GetHpRatio() > 0.2` | - |
| 202 | exhaustion pant at 20 percent | 1202 | 6,000 ms | `GetHpRatio() < 0.2` | - |
| 204 | aggro change | 1204 / 2204 | 6,000 ms | always | - |
| 251 | approach `activeMove` 10 | activeMove | 6,000 ms | always | - |
| 313 | laugh social motion 26 | social | 1 ms | always | - |

Plus a `ShorttermTarget` block, which is the part that makes it read as a boss rather than a
punching bag:

- `StWork id="2"`: `NpcTargetByReaction(1,360,0,500,2)` fires the laugh at a player who has just
  been knocked down, with speech bubble message id `620013`.
- `StWork id="4"`: `GetCombatTime() > 10000 AND PcTargetByAreaRandom(180, 240, 0, 1000)` picks a
  random player in a 240 degree arc out to 1000 units and immediately fires Work 104, the
  telegraphed bomb, with message id `703`. This is a ranged harassment mechanic that ignores the
  aggro table.

Its skill 1303 is named `오칸_Atk04_(필드이벤트)알람있는 폭탄 투척`, "Orcan Atk04 (field event)
alarm bomb throw", at `<server_datasheet>\NpcSkillData_620.xml:11846`. It is
the only Orcan skill in the entire corpus authored specifically for a field event, and it is the
telegraphed ground AoE that a Guardian Legion boss wants.

Boss grade template attributes on `620,1001` (`NpcData_620.xml:3`):

- `elite="True"`, `size="large"`, `showAggroTarget="True"`, `showShorttermTarget="True"`,
  `isLightParty="True"`
- `Anger gaugeSize="252000000" time="36000" moveSpeedUpRate="1.3"` (line 16), a 36 second enrage
- `Reaction basicRes="9999900" miniRes="9999900" statRes="74999248" statStr="60"` (line 21),
  which is the CC immune profile the domain doc describes for dungeon bosses
- `Abnormality ... immuneCategory="3,10,11,12,14,20"` (line 4)
- `Critical str="80" res="234"`, `CriticalAdjust front=1 right=1.5 left=1.5 back=2` (lines 18, 19)
- `spawnScriptId="248009998" despawnScriptId="248009999"`
- `Stat maxHp="10080000000" atk="160000" def="8960" level="68" walkSpeed="200" runSpeed="200"`

And it is wired into a real Guardian Legion mission. `<server_datasheet>\FieldData_7015.xml`
declares `FieldEvent id="1"` at line 4 with `startTerritoryId="620,62000002"`, and its objective
tasks at lines 140, 143 and 146 are `target="@creature:620#1001"`, `#1004`, `#1005`. Continent 7015
owns hunting zone 620 as its `mission` layer (`lookup_hunting_zone 620`: area 7015/HEN_P,
role 수호자임무, siblings 30, 71, 230, 330, 371). This is the exact pattern the IoD event is
copying, one continent down.

**hz 453 template 20, AI 102** at `AIData_453.xml:477` and **hz 87 template 2031, AI 108** at
`AIData_87.xml:1250` are the two richest by raw count: 23 works, 26 skills, full normal plus anger
skill pairs for six attacks, two side walks, two jump evasions, a windup plus payoff chain, an
aggro change, and a four entry `Cooperation` WorkList that is genuinely interesting for a raider
tier:

| Coop Work | desc | condition |
|---|---|---|
| 1 | simultaneous attack when an ally is within 10 m, 10 percent of the time | `GetNpcCountInRange(250) > 1` |
| 2 | 10 second focused group attack on a player under 20 percent HP | `PcTargetByHp(1,360,0,300,0,0.2,0)` |
| 3 | split-to-the-flanks formation order when a player is casting a nuke | `PcTargetBySkillCategoryUsing(1,360,0,500,13) OR ...` |
| 4 | rally-to-the-leader formation order when focus fired | `GetDamagedCount(3) > 4` |

plus `StWork 1` flee below 20 percent HP and `StWork 2` move toward a downed ally. That is pack
behaviour, which is exactly what a mid tier raider wave wants.

The six Orcan attack skills (`1101` through `1106`) are identical in name and animation across all
the rich donors, so the difference between them is entirely which works are wired and at what
cooldown, not what animations exist:

| skill | name | what it is |
|---|---|---|
| 1101 / 2101 | `오칸_Atk01` | right hand basic |
| 1102 / 2102 | `오칸_Atk02` | double lariat spin |
| 1103 / 2103 | `오칸_Atk03` | back jump then ally attack power buff |
| 1104 / 2104 | `오칸_Atk04` | bomb throw, `category="9012"` (ranged), the only ranged one |
| 1105 / 2105 | `오칸_Atk05` | long forward lunge |
| 1106 / 2106 | `오칸_돌진공격_UltraAtk01` | charge |
| 1201 / 1202 | 50 / 20 percent exhaustion | HP threshold motions |
| 1203 / 2203 | pre-motion | telegraph windup |
| 1204 / 2204 | aggro change | taunt drop |
| 1207 / 1208 / 2207 / 2208 | side walk left / right | repositioning |
| 1209 / 1210 / 2209 / 2210 | jump evasion left / right | dodges |
| 1303 | `(필드이벤트)알람있는 폭탄 투척` | **zone 620 only**, telegraphed field event bomb |

The dwarf Orcan (300710) skill set is much thinner everywhere. The richest, 8 skills, is
`87,2011` AI 104: `1101` basic, `1103` two swing, `1104` charge, `1205` command-received motion
that chains into 101, `1206`/`1209` evasions, `1207`/`1208` side walks. IoD `13,4` has 7 of those
8, missing only `1205`. There is no rich dwarf Orcan anywhere in the corpus. The minion is a
minion by design.

---

## 3. Donor recommendations

### Tier 1, minion: copy `13,4` "Dwarf Orcan", add the missing command work from `87,2011`

Copy target: `<server_datasheet>\NpcData_13.xml:494` (template),
`AIData_13.xml:2613` (AI 32), and the 7 `NpcSkillData_13.xml` rows keyed `templateId="4"`
(ids 1101, 1103, 1104, 1206, 1207, 1208, 1209, at lines 3089, 3145, 3220, 3312, 3348, 3384, 3420).

Why this and not the higher ranked out of zone dwarfs: the corpus maximum for this model is 8
skills against IoD's 7, and the one extra is `1205`, a command-received motion. There is no
meaningful mechanical gain from importing `87,2011` or `453,10` wholesale, and staying in zone 13
means the skill rows are already tuned to level 7 scale and the animation set is already proven to
load in this zone. Cheap and swarm friendly is the requirement, and `13,4` already is that.

Deltas to apply:

- new `id` (see section 5), new `aiid` pointing at a new copy of AI 32
- `name`, plus a new `StrSheet_Creature` display name in `HuntingZone id="13"`
- `Anger gaugeSize="0" time="1"` stays as is: this is what makes it non enraging trash
- `Reaction statStr="5" statRes="28" basicRes="4"` stays: CC vulnerable
- `partyMember="8"` stays: this is the swarm flag
- `Stat maxHp` / `atk` / `exp` retuned to the event's level band
- optional: import `1205` plus AI Work 205 from `87,2011` / AI 104 if a "responds to the boss's
  order" beat is wanted in phase 1
- optional: raise `Aggro viewRadius` from 100 to 300 or 400 so a swarm actually swarms; the IoD
  value of 100 with `viewAngle="360"` is a very short leash

### Tier 2, raider: copy `87,2031` AI 108, retune to the IoD level band

Copy target: `<server_datasheet>\NpcData_87.xml:1156` (template),
`AIData_87.xml:1250` (AI 108), and the 26 `NpcSkillData_87.xml` rows keyed `templateId="2031"`
(lines 16440 through 17817).

Why `87,2031` over the equally rich `453,20`: they carry identical work and skill counts and the
same four Cooperation works, but `453,20` lives in a dungeon zone at `size="small"`, while
`87,2031` is `size="medium"` with the standard field mob profile and `playStyle="basic"`, which is
what a field event raider should be. `453,20` is also `playStyle="zarco"` on a full size model,
which is an odd pairing to inherit.

What you gain over IoD's own `13,5` (17 works / 16 skills): the two jump evasions
(1209/1210/2209/2210), the ultra charge attack (1106/2106), a full anger variant for every attack,
and above all the four Cooperation works listed in section 2. `13,5` has no `Cooperation` WorkList
at all, so a group of them fights as isolated individuals.

Deltas to apply:

- new `id`, new `aiid`, new `name`, new `StrSheet_Creature` entry
- `scale` 0.21 -> 0.17 to match the IoD Orcan silhouette, or keep 0.21 for a slightly bigger raider
- `Stat` fully retuned: `87,2031` is level 51 with 182,776 HP and the IoD band is level 7 to 8 with
  6,000 to 13,000 HP
- all 26 skill rows need `totalAtk` retuned; the zone 87 values are in the millions
- `playStyle` keep `basic`; `elite` keep `False`; `Anger gaugeSize` retune down from the zone 87
  value (the IoD raider `13,5` uses 2704.12 with `time="13608"`)
- keep the `Cooperation` block verbatim, including `FormationData` references. Note the formation
  ids referenced by Coop works 3 and 4 resolve against `FormationData_13.xml`, which exists and
  already has formations, so verify the ids you copy actually exist there or author them

### Tier 3, elite boss: copy `620,1005` AI 1, including skill 1303

Copy target: `<server_datasheet>\NpcData_620.xml:65` (template 1005, the
largest of the three at `scale="0.41"`), `AIData_620.xml:128` (AI 1), and the 13
`NpcSkillData_620.xml` rows keyed `templateId="1005"`, the equivalents of ids 1101, 1102, 1105,
1106, 1201, 1202, 1203, 1204, **1303**, 2102, 2106, 2203, 2204.

This is the recommendation with the most evidence behind it. It is the only same model creature in
the corpus that is simultaneously:

- `elite="True"` and `size="large"` (only the six zone 620 templates are)
- carrying a field event authored mechanic (skill 1303, unique to zone 620)
- carrying a `ShorttermTarget` block with an aggro independent ranged attack and a taunt reaction
- already proven wired as a Guardian Legion mission objective (`FieldData_7015.xml:146`)

Mechanics it brings, all listed in section 2: a telegraphed ground bomb on a 50 second cooldown
fired at a random player in a wide arc out to 1000 units, a windup plus heavy hit chain that only
unlocks below 80 percent HP, a charge, a spin, a 36 second enrage, HP threshold exhaustion beats
at 50 and 20 percent, and a mocking laugh when a party member gets knocked down.

Do not copy `620,9001/9002/9003`. They share the shape and the large size but run AI 10, which is a
three work stub with zero skills. They are decoration.

Deltas to apply:

- new `id`, new `aiid`, new `name`, new `StrSheet_Creature` entry (give it a `title`, the way
  `1002` carries "Dark Claw Warlord")
- `race`: zone 620 uses `race="Orcan"` while zone 13 uses `race="OrcanPirate"` for the same shape.
  Use `OrcanPirate` for consistency with the zone, or `Orcan`; both are attested for shape 300650.
  This is cosmetic metadata, not a model selector.
- `Stat`: `620,1005` is level 68 with 10.08 billion HP and 160,000 atk. Everything here is
  placeholder for a level 65 gated mission and must be fully retuned for the IoD band.
- `Reaction basicRes/miniRes 9999900, statRes 74999248` is total CC immunity. For a starter island
  boss that is almost certainly wrong: use something between the IoD raider profile
  (`statStr=40 statRes=50 basicRes=50`) and the zone 620 profile so the boss can still be
  staggered but not chain locked.
- `Anger gaugeSize="252000000" time="36000"` scales with HP; retune proportionally.
- `immuneCategory="3,10,11,12,14,20"` review against what the level band's abnormalities are.
- `spawnScriptId="248009998" despawnScriptId="248009999"` reference `S1ActionScripts`. Verify those
  ids resolve before copying them, or drop them; a dangling action script id is a boot risk.
- `scale`: see section 6. 0.41 is the largest attested elite value; 0.6 is the largest value
  attested anywhere for this shape (`795,205`).
- Skill 1303 has `category="0"` and `totalAtk="0"` on the zone 620 copy, so its damage is defined
  entirely by the copied `Effect` rows. Read those before retuning, do not just scale `totalAtk`.
- The `msg` ids on AI 1 (`620013`, `703`) resolve against the client only
  `StrSheet_MonsterBehavior` sheet. `620013` is a zone 620 specific line. Either author new lines
  or blank the `msg` attributes; leaving `620013` produces a Veritas District line on Island of
  Dawn.

---

## 4. Authoring checklist

Every family a new monster template touches, in dependency order. Traced against the real worked
example of `13,902` (a template with no quest and no achievement references, the current v0 event
boss) versus `620,1001` (a fully featured Guardian Legion boss). The delta between those two is the
checklist.

| # | Family | Server file | Key | Required for a new monster | `13,902` has it | `620,1001` has it | DSL entity |
|---|---|---|---|---|---|---|---|
| 1 | NPC template | `NpcData_13.xml` | `(huntingZoneId, id)` | yes, mandatory | yes, line 972 | yes, line 3 | `npcs` |
| 2 | AI definition | `AIData_13.xml` | `(huntingZoneId, Ai.id)` matched by `Template.aiid` | yes, mandatory. 100 percent referential integrity across 22,500 NPCs; a dangling `aiid` is a load failure | yes, aiid 32 shared with 4 and 1003 | yes, aiid 1, dedicated | `ai` |
| 3 | NPC skills | `NpcSkillData_13.xml` | `(huntingZoneId, templateId, id)` | yes, one row per distinct `normalBehaviorId` / `angerBehaviorId` where `behaviorType="skill"` | yes, 7 rows | yes, 13 rows | `npcSkills` |
| 4 | Display name, server | `StrSheet_Creature.xml`, `<HuntingZone id="13">` at line 660 | `(huntingZoneId, templateId)` | yes. Without it the template is treated as a parent-only base template and is never spawned directly | yes, "Dwarf Guardian" | (zone 620 block) | `creatureStrings` |
| 5 | Display name, client | `StrSheet_Creature\StrSheet_Creature-00000.xml` | same | yes, the client draws the nameplate | yes, byte identical to server | yes | **not covered by sync-config, see gap below** |
| 6 | Client NPC template | `NpcData\NpcData-00011.xml` (hz 13) | `(huntingZoneId, id)` | yes, for the display-side `Stat`, `NamePlate`, `Anger`, `Aggro`, `Reaction` subset | yes, all 57 server templates are mirrored | yes | `NpcData` in sync-config line 294 |
| 7 | Animation and collision | `NpcBasicAction.xml` | `basicActionId` | reuse 3006500 / 3007100, already exist | yes | yes | reuse only |
| 8 | Active moves | `ActiveMove_13.xml` | `(huntingZoneId, id)` | only if the AI has `behaviorType="activeMove"` works. Zone 13 has ids 1 to 23 plus 888 | AI 32 uses activeMove ids 1, 3, 16, all present | AI 1 uses activeMove id 10 | not documented as a DSL entity |
| 9 | Formations | `FormationData_13.xml` | `(huntingZoneId, Formation.id)` | only if the AI issues formation orders (the raider Cooperation works do) | no | no | not documented as a DSL entity |
| 10 | Spawn placement | `TerritoryData_13.xml` | `Npc.npcTemplateId` under a `Territory` | yes, unless spawned purely by field event `dynamicSpawn` | yes, territory 13017020 in group 1300062, `type="quest"` | zone 620 territories | `territories`, `territorySpawns` |
| 11 | Class branched loot | `CompensationData\CCompensation_0013.xml` | `Compensation.npcTemplateId` | optional | yes, line 1995, 16 bags | - | `cCompensations` |
| 12 | Environment loot | `CompensationData\ECompensation_13.xml` | `Compensation.npcTemplateId` | optional, this is the boss and gold-drop family | yes, line 812, GoldBag plus 6 ItemBags | zone 620 has no compensation file at all | `eCompensations` |
| 13 | Field event binding | `FieldData_13.xml` and `FieldEvent.xml` | `@creature:{hz}#{tpl}` in `Task.target`, `targetNpcId="{hz},{tpl}"` in `EventTask` | yes for an event mob | v0 spec binds it | `FieldData_7015.xml:140,143,146` | `Field`, `FieldEvent` in sync-config |
| 14 | AI speech lines | client `StrSheet_MonsterBehavior` | `msg` ids on AI `Work` and `StWork` | only if the AI sets `msg` | AI 32 has no msg | AI 1 uses 620013 and 703 | not covered by sync-config |
| 15 | Spawn / despawn choreography | `S1ActionScripts` | `spawnScriptId`, `despawnScriptId` | optional | no | yes, 248009998 / 248009999 | not documented as a DSL entity |
| 16 | Dynamic spawn | `DynamicSpawn_13.xml` | `(huntingZoneId, instanceId)` | only if the boss summons adds or the event uses `dynamicSpawn` tasks | no; `DynamicSpawn_13.xml` has zero `npcTemplateId` refs today | zone 620 has `DynamicSpawn_620.xml` | `taskDynamicSpawn` in the `fieldevent` package |

The minimum viable new monster is rows 1, 2, 3, 4, 5, 6, 10. Everything else is opt in.

### The `13,902` versus `620,1001` delta, stated plainly

`13,902` is wired as: template plus a shared AI plus 7 skills plus a name plus a client mirror plus
loot plus one quest-type territory. That is the full minimum and nothing more. It has no
`Cooperation`, no `ShorttermTarget`, no `Pattern` beyond the default, no action scripts, no
dynamic spawn, no speech, `Anger gaugeSize="0"` so it cannot enrage, and `Reaction basicRes="4"` so
it falls over to any crowd control.

`620,1001` adds, on top of that same minimum: a dedicated AI it does not share with anything, a
`ShorttermTarget` block with two `StWork` entries, a purpose built field event skill, a 36 second
enrage with a 252 million gauge, a CC immune `Reaction` profile, an `immuneCategory` list, spawn
and despawn action scripts, `showAggroTarget` / `showShorttermTarget` / `isLightParty` display
flags, and a `FieldData` objective binding. It notably does **not** have a compensation entry;
zone 620 has no `CCompensation` or `ECompensation` file at all, only
`QuestCompensationData_620.xml`. Guardian Legion missions pay out through the event reward system,
not through kill loot.

That last point matters for our design: if the IoD event's three mobs are meant to have their own
loot tables, we are diverging from how the shipped Guardian Legion missions pay out, and that is a
deliberate choice worth recording rather than an oversight.

### Two pipeline gaps found

1. **`StrSheet_Creature` is not in the sync config.** `reforged\config\sync-config.yaml`
   declares 40 synced entities including `NpcData`, `StrSheet_Npc`, `SkillData` and `TerritoryData`,
   but the string `StrSheet_Creature` does not appear anywhere in the file. Today the server and
   client copies are in perfect agreement for hunting zone 13 (170 entries each, zero differences
   in either direction), so nothing is broken now, but a newly authored creature name will land on
   the server only and the client nameplate will have nothing to render. Verify this before the
   first authored monster ships; it may warrant a `docs/dsl-requests` or a sync-config addition.
2. **`AIData` is not in the sync config either.** The client DataCenter does have an `AIData`
   folder. Whether the client copy is load bearing for anything visible is unverified here.

---

## 5. Proposed id allocation

**Recommendation: reserve `13,2001` through `13,2099` for authored Reforged NPCs in hunting zone 13,
and allocate `13,2001` (Dwarf Orcan minion), `13,2002` (Orcan Raider), `13,2003` (Orcan boss).**

### Proof the block is free

Every id-bearing family that scopes to hunting zone 13, across every era available on this machine:

| Source | File | ids in 1502..5000 | ids in 2001..2099 |
|---|---|---|---|
| v92 server NPC templates | `Datasheet\NpcData_13.xml` | none | none |
| v31 server NPC templates | `v31...\Datasheet\NpcData_13.xml` | none | none |
| v92 client NPC templates | `client-dc\...\NpcData\NpcData-00011.xml` | none | none |
| v31 client NPC templates | `client-dc_v31\...\NpcData\NpcData-00011.xml` | none | none |
| v17.11 client NPC templates | `tera-dc-17_11\...\NpcData\NpcData-00011.xml` | none | none |
| v92 server creature names | `Datasheet\StrSheet_Creature.xml` `<HuntingZone id="13">` line 660 | none | none |
| v31 server creature names | `v31...\StrSheet_Creature.xml` `<HuntingZone id="13">` line 549 | none | none |
| v92 client creature names | `StrSheet_Creature\StrSheet_Creature-00000.xml` | none | none |
| v31 / v17 client creature names | same path in each DC | none | none |
| v92 NPC skills | `Datasheet\NpcSkillData_13.xml` `Skill@templateId` | none | none |
| v31 NPC skills | `v31...\NpcSkillData_13.xml` `Skill@templateId` | none | none |
| v92 class loot | `CompensationData\CCompensation_0013.xml` | none | none |
| v92 environment loot | `CompensationData\ECompensation_13.xml` | none | none |
| v31 class loot | `v31...\CCompensation_0013.xml` | none | none |
| v31 environment loot | `v31...\ECompensation_13.xml` | none | none |
| v92 spawns | `Datasheet\TerritoryData_13.xml` `Npc@npcTemplateId` | none | none |
| v31 spawns | `v31...\TerritoryData_13.xml` `Npc@npcTemplateId` | none | none |
| v92 dynamic spawn | `Datasheet\DynamicSpawn_13.xml` | file has zero `npcTemplateId` refs | none |
| v92 work objects | `Datasheet\WorkObjectTerritory_13.xml` | only id 134 | none |
| v92 bonfire | `Datasheet\BonfireData_13.xml` | zero refs | none |
| v92 field data | `Datasheet\FieldData_13.xml` | only the literal 13 | none |

The complete union of NPC relevant ids ever used under hunting zone 13, across all five sources and
all three eras, below 400000:

```
1 2 3 4 5 6 7 8 9 101 102 111 134 301 302 303 304 555 556 557 558 601 888 901 902 999
1001 1002 1003 1004 1011 1271 1501
5001-5012 5101-5104 5201-5204 5301-5304
6001-6012 6017-6037 6040-6052
7001-7009
8001-8013 8015-8031
9001-9005 9009 9011 9020
300540-300542 300910 300911 300920 300921 300930-300933 300940-300945
300950-300953 300960 301190-301194
```

The gap `1502..5000` is 3,499 consecutive free ids and is the largest clean band below the
300000 shape-derived range. `1271` is "Vardung, Island of Dawn Mystery Merchant" and `1501` is
"Karascha's Lair Teleportal", both name-only entries in `StrSheet_Creature` with no template, which
is why the band starts at 1502.

### Ids to avoid, and why

- **`7001` to `7009` and `9001`.** These have live `Compensation` entries in
  `ECompensation_13.xml` and live name entries in `StrSheet_Creature` but **no template** in any
  `NpcData_13.xml`. Creating a template at one of those ids would silently inherit a pre-existing
  loot table and a pre-existing display name. This is the single most dangerous trap in the zone 13
  id space.
- **`5001` to `6052` and `8001` to `9020`.** Same shape of hazard: name entries exist in the v92
  `StrSheet_Creature` block with no matching template. `13,5008` is the Crystal Merchant the NPC
  domain doc cites as the zone 13 vendor pool example.
- **Anything at or above 300000.** That band mirrors `shapeId` values by convention in this zone
  (`300910`, `300941`, `301191` and so on) and should stay that way.
- **`902`.** Currently in use by the v0 event and carrying live loot in both compensation files.

### Free ids check via MCP

`mcp__datasheet-v92__find_free_ids` with `entityType: NpcTemplate` errored out on this build
(`An error occurred invoking 'find_free_ids'`), so the allocation above is proven by direct file
scan instead. Worth logging in `docs/mcp-requests/` if the tool is expected to accept
zone-partitioned entity types without a `huntingZoneId` argument.

### AI id allocation

Separate id space, same zone scoping. `AIData_13.xml` uses ids `1..39` and `103..108`. Both the
v92 and v31 copies are identical on this. Free and recommended: **`aiid` 201, 202, 203** for the
three new monsters, keeping them clearly out of the `1..39` classic band and the `103..108` band.

### NPC skill id allocation

No allocation needed. `NpcSkillData` rows are keyed `(templateId, id)`, so each new template gets
its own private `1101`, `1102`, ... namespace. Copy the donor's skill ids verbatim.

---

## 6. Scale and appearance values

`scale` on the `Template` element is the model size multiplier and is the attribute that makes a
creature visibly bigger. `size` (`small` / `medium` / `large`) is a separate categorical attribute
that does not scale the mesh; both should be set consistently but only `scale` changes what the
player sees. `NamePlate.nameplateHeight` must be raised alongside `scale` or the name tag will sit
inside the model.

### Observed values, shapeId 300650 (full size Orcan)

| scale | nameplateHeight | size | elite | example | zone role |
|---|---|---|---|---|---|
| 0.125 | (absent) | medium | (absent) | `241,1008` and 11 siblings | named non combat villagers |
| **0.17** | **18** | medium | False | `13,5`, `13,901`, `13,1002` | **Island of Dawn baseline** |
| 0.17 | 20, 21 | medium | false | `437,5`, `437,11` | IoD dungeon layer |
| 0.19 | 19 | medium | False | `11,4001` | field mob |
| 0.21 | (absent) | medium / small | False | `87,2031`, `87,2053`, `453,20`, `29,5002` | field and dungeon mobs |
| 0.24 | 20 | medium | False | `41,2004`, `41,2005`, `833,1078` | field and dungeon mobs |
| **0.30** | **30** | medium | **true** | `1022,203` | black rift, `huntingStyle="raid"` |
| **0.31** | (absent) | **large** | **True** | `620,1001`, `620,9001` | Guardian Legion mission |
| **0.35** | (absent) | **large** | **True** | `620,1004`, `620,9002` | Guardian Legion mission |
| **0.41** | (absent) | **large** | **True** | `620,1005`, `620,9003` | Guardian Legion mission |
| 0.6 | (absent) | medium | False | `795,205` | corpus maximum for this shape |

### Observed values, shapeId 300710 (dwarf Orcan)

| scale | nameplateHeight | size | example |
|---|---|---|---|
| **0.5** | **10, 11** | small | `13,4`, `13,902`, `13,1003`, `437,4`, `437,12`, `1023,30071000` |
| 0.6 | 0, 11, 14, 20 | small / medium | `12,5`, `12,10`, `41,2003`, `42,100`, `830,1001000` |
| 0.9 | (absent) | small | `1022,303` |
| 1.0 | (absent) | small | `453,10`, `833,1079`, `87,2011`, `87,2016`, `87,2021`, `87,2083` |
| 1.5 | (absent) | small / medium | `29,5001`, `112,4001` |

Note the two shapes use disjoint scale ranges. 300710 at `scale="1.0"` is still a small dwarf;
300650 at `scale="0.41"` is a large elite. Never carry a scale value across models.

### Recommendation for the three tiers

| tier | shapeId | scale | size | nameplateHeight | ratio vs IoD baseline |
|---|---|---|---|---|---|
| Dwarf Orcan minion | 300710 | 0.5 | small | 10 | 1.0x, matches `13,4` and `13,902` exactly |
| Orcan Raider | 300650 | 0.21 | medium | 20 | 1.24x the IoD Orcan, attested at `87,2031` |
| Orcan boss | 300650 | **0.41** | **large** | 40 to 45 | **2.41x the IoD Orcan**, the largest attested elite value, taken directly from `620,1005` |

0.41 is the strongest choice: it is the largest value the publisher itself shipped on an elite
Guardian Legion Orcan, it is 2.4 times the height of the Orcans standing next to it in the camp,
and it stays inside attested territory so there is no risk of clipping or animation stretching that
0.6 might introduce. If 0.41 reads as insufficiently imposing in game, 0.6 (`795,205`) is the only
larger attested value and is the ceiling.

`nameplateHeight` is not present on any zone 620 template, so it must be derived. The zone 13
Orcans are at 18 for `scale` 0.17, and `1022,203` is at 30 for `scale` 0.30, giving roughly
100 units of nameplate per unit of scale. 0.41 therefore wants somewhere near 41 to 45. Confirm
in game.

---

## 7. Loot attachment mechanism

A monster's drop table is attached externally, by composite key. Nothing on the `Template` element
points at loot.

```
NpcData_13.xml         Template@id = 902
                              ||
                              || (huntingZoneId, npcTemplateId)
                              ||
CCompensation_0013.xml   Compensation@npcTemplateId = 902     class branched drops
ECompensation_13.xml     Compensation@npcTemplateId = 902     gold, boss and elite drops
```

Both files are keyed on `(huntingZoneId, npcTemplateId)`. The `huntingZoneId` comes from the file
name and the root element attribute. Note the inconsistent file naming in this datasheet: the class
file is zero padded (`CCompensation_0013.xml`) and the environment file is not
(`ECompensation_13.xml`). There is no `ICompensation` or `FCompensation` for zone 13.

`npcName` on the `Compensation` element is informational. An empty string matches all NPCs with
that id; a specific name filters to a named boss. In practice the zone 13 files carry inconsistent
values: the class file uses Korean internal names (`미니 오칸B` for template 902) while the
environment file uses English display names (`Dwarf Guardian` for the same 902). Neither is used
for matching in the entries observed.

Zone 13 coverage today: 50 `Compensation` entries in `CCompensation_0013.xml`, 57 in
`ECompensation_13.xml`. All six IoD Orcan templates appear in both.

### Worked example, `13,902` "Dwarf Guardian", `ECompensation_13.xml:812`

```xml
<Compensation npcName="Dwarf Guardian" npcTemplateId="902">
  <GoldBag bagName="골드" probability="0.03" min="2" max="604" wValue="0.4"
           t="13;902;28.4034737986332;0.4;0.03"/>
  <ItemBag id="101" bagName="Alkahest" probability="0.04">
    <Item templateId="21351" name="Masterwork Alkahest" min="1" max="1" probability="1"/>
  </ItemBag>
  <ItemBag id="109" bagName="Feedstock" probability="0.04">
    <Item templateId="94101" name="Tier 1 Feedstock" min="2" max="2" probability="1"/>
  </ItemBag>
  <ItemBag id="102" bagName="CrystalBoxes" probability="0.02">
    <Item templateId="602176" name="Weapon Crystal Box (Rhomb)" min="1" max="1" probability="0.5"/>
    <Item templateId="602177" name="Armor Crystal Box (Rhomb)" min="1" max="1" probability="0.5"/>
  </ItemBag>
  <ItemBag id="103" bagName="DyadStructure" probability="0.01">
    <Item templateId="96108" name="Dyad Rhomb Structure" min="1" max="1" probability="1"/>
  </ItemBag>
  <ItemBag id="104" bagName="SmartDyadStructure" probability="0.001">
    <Item templateId="96114" name="Smart Dyad Rhomb Structure" min="1" max="1" probability="1"/>
  </ItemBag>
  <ItemBag id="105" bagName="InfusionBoxUncommon" probability="0.01">
    <Item templateId="602190" name="Infusion Weapon Box (Uncommon)" min="1" max="1" probability="0.25"/>
    <Item templateId="602193" name="Infusion Chest Box (Uncommon)" min="1" max="1" probability="0.25"/>
    <Item templateId="602196" name="Infusion Gloves Box (Uncommon)" min="1" max="1" probability="0.25"/>
    <Item templateId="602199" name="Infusion Boots Box (Uncommon)" min="1" max="1" probability="0.25"/>
  </ItemBag>
</Compensation>
```

That is the shape of a trash mob table: one `GoldBag` plus six independent `ItemBag` rolls, item
probabilities inside each bag summing to 1.0. Bags roll independently, so the numbers are per bag
trigger chances, not a partition.

The boss shape, `13,1002` "Acharak" at `ECompensation_13.xml:1593`, is the same structure with 11
bags: the same six Reforged bags at roughly 20x the probability and 2x the quantity, plus five
classic bags (`재료` materials, `제련석` refining stones, two guaranteed `악세서리_0` accessory
bags at `probability="1"` each dropping item 20001, and a movement speed orb bag). The two
`probability="1"` accessory bags are how a named boss guarantees a reward.

Note what is absent everywhere in zone 13: no `RewardBox`, no `JackpotRewardBox`. Damage gated and
grade gated distribution is not used on this island at all. If the event boss should pay out by
damage contribution rather than to everyone present, that is a new pattern for this zone and the
`RewardBox` `partyDamageMin` / `partyDamageMax` and `dropItemToPC` attributes are the mechanism.

Also note, as flagged in section 4: hunting zone 620, the shipped Guardian Legion mission zone,
has **no compensation file of any kind**. Its bosses pay out through the field event reward system.
Attaching kill loot to our event mobs is a deliberate divergence from the shipped pattern.

The DSL entities are `cCompensations` and `eCompensations`, both supporting
`create`, `update`, `delete`, `upsert`, and both registered for id list expansion on
`npcTemplateId` so one block can cover several templates.

---

## 8. Findings from XML comments

Every file relevant to this survey was parsed with comments preserved and cross checked against a
raw text pass.

| File | comments | content |
|---|---|---|
| `NpcData_13.xml` | 0 | nothing hidden. All 57 templates are live in v92, v31 and all three client DataCenters. |
| `AIData_13.xml` | 0 | none |
| `NpcSkillData_13.xml` | 0 | none |
| `CCompensation_0013.xml` | 0 | none |
| `NpcData_620.xml` | 2 | `이벤트_리리` and `리리 이벤트`, section markers for an event NPC, no disabled content |
| `AIData_620.xml`, `NpcSkillData_620.xml`, `NpcData_87.xml` | 0 | none |
| `ECompensation_13.xml` | **1, at line 3** | a large commented out block, roughly the whole pre-Reforged version of the file. It is the classic era loot for zone 13: `GoldBag` only entries for the Terrons, Dumpokans, Stone Crawlers, Black Marauder, plus the Orcan entries. It includes `<Compensation npcTemplateId="902" npcName="난쟁이 오칸 경계병">` with a single `GoldBag probability="0.03" min="2" max="604"`, which is exactly the `GoldBag` line that survives in the live entry at line 812. So the live file is the old file plus the six Reforged bags, and the comment is the pre-Reforged snapshot, not disabled content that was ever meant to come back. |
| `FieldData_7015.xml` | several | one relevant to mechanics: line 195 `<!-- <EventTask type="abnormality" abnormalityId="77771002" ... /> -->`, one rung of the Guardian scaling abnormality ladder switched off by commenting. This confirms the publisher does disable field event content this way, so any future `FieldData_13.xml` work must be read with comments preserved. |

`NpcData_13.xml` is byte identical in template inventory across v92 server, v31 server, v92 client,
v31 client and the v17.11 client: the same 57 ids in every one. There is no dormant Orcan hiding
anywhere in any era.

---

## Appendix: scan scripts

Written to the session scratchpad, not to the repo:

- `scan_orcan.py` full corpus scan of `NpcData_*.xml` for shapeId 300650 / 300710
- `scan_ai.py` first pass AI resolution (superseded)
- `scan_skills2.py` correct `(templateId, id)` keyed skill resolution, output `orcan_skills2.json`
- `summ_ai.py` per AI work and skill dump
- `dump_ai.py` raw AI element dump
- `ids13.py`, `ids_client.py`, `occupied13b.py` id occupancy across all sources and eras
