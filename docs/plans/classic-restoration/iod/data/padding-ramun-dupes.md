# IoD Padding Wave Regressions: Ramun (quest 1327) and Politics NPC Duplication

Analysis only. No datasheet modifications made. Live v92 dev server, TerritoryData parsed from
`D:\dev\mmogate\tera92\server\Datasheet`. Repo root for git is `D:\dev\mmogate\tera92\server`.

## ISSUE 1: Ramun / quest 1327 "Garrison in Distress"

### Quest structure (001327.quest + QuestDialog_1327.xml)
- Giver trigger: talk to NPC `213,1017` (Researcher Kaimon), at Kaimon's encampment.
- Task 1 (visit): `213,1038` Ramun, dialog id 3 ("Attend! You there! Have you seen anyone named..."),
  choreography 연출Id 10024, completes the herald handoff.
- Task 2 (visit): `213,1004` (Centurion Neziir), at Garrison North Camp.
- Task 3 (hunt/deliver): kill `13,300921` sickly noruk x5, deliver to `213,1119` (Prefect Ashak),
  Garrison North Camp.

The template the player MUST talk to for Task 1 is **1038**. It sits at Kaimon's encampment
(territory 1300467), right beside the giver 1017. There IS a second "Ramun":

| template | name / title  | layer | territory | position (x,y,z) | role |
|----------|---------------|-------|-----------|------------------|------|
| 1038 | Ramun / Herald | 213 | 1300467 Kaimon's encampment | 80798, -80691, -4433 | Task 1 target (inst 21300005) |
| 1124 | Ramun / Herald | 213 | 1300464 Garrison North Camp | 74138, -82048, -3462 | decorative twin near Neziir/Ashak (inst 1305643) |

Both are genuine v31 spawns (v31-spawns: group 1300005 territory 1300467 carries 1038; territory
1300464 carries 1124). The twin 1124 is ~6800u away at the NORTH camp. Task 1 happens at Kaimon's
encampment, where only 1038 exists, so **1124 is not the cause of the Task 1 failure**.

### Root cause
Template 1038 (NpcData_213) carries `spawnScriptId="10023"`. That entrance spawn-script ends in a
move: the server keeps the interactable entity at the spawn coordinate while the client visual walks
to the script endpoint. The player clicks where they SEE Ramun, `C_NPC_CONTACT` fails the server
range check silently, and the visit task never completes. This is the exact bug the retired pilot
diagnosed and packet-capture proved.

### Old fix (retired pilot)
`temp/patch-001-v17-reference/12-iod-spawn-script-fixes.yaml` (2026-07-19). NOT a retarget, rename,
or twin-spawn. It moves the server spawn onto the script's move endpoint so server and client agree:

```yaml
territorySpawns:
  update:
    - huntingZoneId: 213
      groupId: 1300005
      territoryId: 1300467
      npcInstanceId: 21300005
      changes:
        pos: [80672, -81177, -4409]
```

### Current state and re-applicability
- The 1038 spawn (inst 21300005) is BASELINE: present in HEAD at position 80798, -80691, -4433 (the
  un-fixed coordinate). The padding wave did NOT add or move it (the wave added group 1300006 with
  templates 1009/1021/1110/1126/1128/1130 only). The bug is a baseline condition; the pilot reposition
  lived in discarded specs and was never applied to the current baseline, so it resurfaced.
- Re-applying is clean under v31-primary: it is an internal server/client position-consistency fix,
  not a v31 divergence. Re-author the same `territorySpawns.update` into the current patch (optionally
  re-verify the endpoint 80672,-81177,-4409 with a fresh packet capture; the pilot already proved it).

## ISSUE 2: Politics NPC duplication (Hyneu and peers)

### Hyneu root cause
Hyneu = huntingZone 364, two templates both displayed as "Hyneu", stacked ~14u apart in layer 364
(Tower Base, hub-politics):
- 1101 "Cleric of Restoration" (inst 36400007, 67830,-80534)
- 1102 "Noble Cleric of Restoration" (inst 36400008, 67840,-80524)

These are dual-state (vanarch / political) NPC pairs from classic TERA. The classic policy system
toggled which variant spawned per policy state (ON/OFF). This server runs no policy gating and both
rows have `conditionalSpawn="false"`, so BOTH always spawn and overlap. Note: template ids are
namespaced per huntingZone, so this is a WITHIN-layer duplicate (two templates, one name), not a
cross-layer overlap. No cross-layer same-name overlaps exist across HZ 13/64/213/313/364.

### Pre-dates the padding wave
Confirmed via git: TerritoryData_313 and _364 last changed in the baseline commits `de8138ea`
("Island of Dawn restoration") and `518827e2` ("Commit inicial"); untouched by this session's padding
wave (which modified only 213 group 1300006 and TerritoryData_13). This is a v31-port baseline
condition, not introduced by padding.

### Full duplicate set (same display name, overlap <500u, within one layer; service NPCs)

Layer 313 (garden politics, group 31300002):
| name | templates | keep | remove (instanceId / territory) | dist |
|------|-----------|------|----------------------------------|------|
| Ashley | 1001 + 1002 | 1002 working Merchant (store 250) | 1001 inst 31300014 / t31300005 (menu-less "Specialty Store" retitle) | 126 |
| Harger | 1003 + 1004 | BOTH (not a true dupe) | none | 108 |
| Jilva | 1005 + 1007 | 1007 working Tactics Instructor (SkillLearn) | 1005 inst 31300018 / t31300009 (Off-Duty, menu-less) | 136 |
| Misrile | 1006 + 1008 | 1008 working Magic Instructor (SkillLearn) | 1006 inst 31300019 / t31300009 (Off-Duty, menu-less) | 132 |

Layer 364 (Tower Base hub-politics, group 36400001):
| name | templates | keep | remove (instanceId / territory) | dist |
|------|-----------|------|----------------------------------|------|
| Ainah | 1001 + 1002 | 1001 working Merchant (store 250) | 1002 inst 36400002 / t36400002 ("Vacationing Shopowner" placeholder) | 17 |
| Hyneu | 1101 + 1102 | 1102 Noble (working restore menus) | 1101 inst 36400007 / t36400005 (policy cleric, inert) | 14 |

Harger (1003/1004) is retained: v31 has these as two distinct services (1003 BuffStore, 1004
ConditionRestore) whose names v92 collapsed; not a real duplicate.

Excluded (not the reported "politics NPC" issue): L13 Ghilliedhu (mob pair) and L13 Training Dummy
(training props).

Note the keep/remove choice is NOT a blanket template rule: the working merchant is template 1002 in
layer 313 but template 1001 in layer 364, so removals must use the exact instanceIds above.

### Old fix (retired pilot)
`temp/patch-001-v17-reference/03-iod-spawn-removals.yaml` items 5 and 6, settled "decision 24"
(2026-07-19). Same resolution: remove the menu-less OFF/placeholder variant, keep the working one,
keep the Harger pair. `territorySpawns.delete` on the 5 instanceIds:
31300014, 31300018, 31300019 (HZ 313); 36400002, 36400007 (HZ 364). NpcData template rows left in
place as dormant templates.

### Proposed fix and policy call
Re-author the 5 `territorySpawns.delete` rows above into the current patch. **This needs a user policy
call.** v31 itself carries these dual-state NPCs (valid v31 data toggled by a policy system this build
does not run), so removing them is a deliberate divergence from v31 under the v31-primary doctrine and
requires user approval plus a divergence-log entry. It was approved once as decision 24 in the
discarded pilot; it needs re-confirmation before applying.
