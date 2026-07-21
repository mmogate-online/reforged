# v31-vs-v92 Quest Axis Diff - Island of Dawn (Phase 3)

Axis: story quest spine, zone-quest availability, rewards, story groups, and dialog
consistency, diffing the **v31 server baseline** (source of truth, port 1:1) against the
**v92 clean baseline** (port target, patch state reverted; patch-000 edits are committed into
it and surface here as differences). Band: global quest ids 1300-1399 (all keyed `Quest번호` hz=13).

Method: raw XML parsed with python; whole-tree whitespace-insensitive canonical diff per quest
file, plus per-family comparison of `QuestCompensationData_13`, `QuestGroupList`, and
`QuestDialog`. Machine-readable rows with exact ops: `quests-diff.json` (and the extractor dump
`quests-diff.raw.json`).

## Headline

The spine matches v31 almost exactly. **Existence, sentinel-disabled set, all quest Headers
(givers, prerequisites, levels, story groups, class restrictions, start items, auto-accept), and
story-group membership+order are all identical** between v31 and v92. Only 9 of 65 quest files
differ, all in task bodies, and every one is either a v31-wins port of a dormant field or a
sanctioned v92 adaptation. The one systemic divergence is **rewards**: v92's entire IoD reward
sheet has been gutted to empty stubs and must be ported wholesale from v31.

## Verdict counts

| Axis | Verdict | Count / detail |
|------|---------|----------------|
| Existence | MATCH | 65/65 band quest files present in both |
| Sentinel-disabled set | MATCH | 40 disabled in v31 = 40 disabled in v92 (identical ids) |
| Quest Headers (spine wiring) | MATCH | 65/65 - no giver/prereq/level/storygroup/class/start-item/auto-accept drift |
| Story groups | MATCH | group 1 (18 quests) + group 2 (7 quests), identical membership and order |
| Quest task bodies | MATCH 56 / PORT 3 / KEEP 6 | see below |
| Rewards (`QuestCompensationData_13`) | PORT ALL 65 | v92 rows are empty stubs; port every row from v31 |

Live set: 25 quests are live in v31 (65 minus 40 sentinel-disabled); the same 25 are live in v92.

## Rewards - the one systemic divergence (PORT ALL)

**v92 `QuestCompensationData_13.xml` is entirely empty self-closed stubs**
(`<Quest questId="1384"/>` and so on) for every band questId: 0 `CompensationType`, 0 `Item`, 0
class rows across the whole file. v31 carries the full reward data (211 item rows, exp/gold,
class-scoped). The band questId set in the comp file is identical (both include 1384). So the
diff is not per-quest noise; it is a wholesale wipe of the v92 reward sheet.

Op: **port every band reward row from v31 `QuestCompensationData_13.xml` 1:1.** No v31 band row
is an empty stub (all 65 have at least exp/gold), so there is no v92-only reward to keep.

### New-class reward gap (adaptation, whitelist item 2)

15 quests carry class-scoped reward items in v31, each defining rows for the 9 v31-era classes
(warrior, lancer, slayer, berserker, archer, sorcerer, priest, elementalist=Mystic,
engineer=Gunner):

`1303, 1304, 1305, 1310, 1315, 1316, 1317, 1319, 1322, 1323, 1325, 1326, 1330, 1331, 1347`

When ported, append adaptation rows for the classes absent from v31-era data: **Fighter
(Brawler), Assassin (Ninja), Glaiver (Valkyrie)**. **Soulless (Reaper) stays omitted** (no
base-game low-level gear; patch 002 covers it). Engineer (Gunner) already has rows in v31, so it
needs nothing. Namespace trap: `QuestCompensationData` uses INTERNAL class names; the client
`CCompensation` uses CLIENT names - never cross them.

## Quest task-body diffs (9 files)

### PORT (3) - collection-id drift, dormant

All three are sentinel-disabled in **both** v31 and v92, so the difference is dormant (revisited
only in the padding phase). v31 wins on divergence.

| gid | title | op |
|-----|-------|----|
| 1334 | Investigating the Relics | task-1 `콜렉션Id` 404 -> **410** (v31) |
| 1336 | Chione's Missing Cargo | task-1 `콜렉션Id` 403 -> **409** (v31) |
| 1341 | Bequest of the Dead | task-1 `콜렉션Id` 405 -> **411** (v31) |

Wipe-and-replace ports the v31 quest file wholesale, which brings the v31 collection id
automatically. Cross-family dependency: the collections/CollectionData port must use the v31
scheme too, or these ids would dangle. Coordinate with the spawns/collections diff owner. (Note:
the ids are `콜렉션Id` gather references, not `collectionId` attributes in `CollectionData_13`;
resolving their keyspace is a collections-axis task, out of scope here.)

### KEEP (6) - sanctioned v92 adaptations

**1384 Recharge It (the charm quest)** - patch-000, committed into the v92 baseline. Three kept
changes, all on the adaptation whitelist:
- Charm item **7100 -> 70033** (task-4 grant, task-5 use-condition). v31's charm 7100 **exists in
  v92 ItemTemplate but is `NO_COMBAT`** there, so it cannot satisfy the item-use condition; 70033
  is `charm`/`DISPOSAL`/usable and exists in both. (whitelist item 1: charm system support)
- Task-3 condition **`휴식후컨디션MAX` (rest-to-full-stamina) -> `아이템사용` 98**; the
  full-stamina mechanic does not function on v92. (whitelist item 3: changed mechanics)
- Task-2 rewired: `다음Task` 3 -> 5 plus an extra grant of 70033, so the v92 flow is
  `1 -> 2(grant 98+70033) -> 5(use 70033) -> 6`. v31 flow is
  `1 -> 2(grant 98) -> 3(rest) -> 4(grant 7100) -> 5(use 7100) -> 6`.

**1371 / 1373 / 1374 / 1375 / 1379 - training-quest skill-learn condition** (all live). Each
task-2 `완료조건/스킬습득/스킬Id` (learn-your-first-skill) uses a different id in v92:

| gid | class | v31 스킬Id | v92 스킬Id (KEEP) |
|-----|-------|-----------|-------------------|
| 1371 | Warrior | 40100 | 180100 |
| 1373 | Slayer | 30100 | 120100 |
| 1374 | Berserker | 100100 | 30100 |
| 1375 | Archer | 20100 | 30100 |
| 1379 | Engineer/Gunner | 30100 | 70100 |

These are class-scoped skill ids (v31 itself reuses 30100 for both Slayer and Engineer, so the
1374/1375 sharing of 30100 in v92 is not a collision - each quest is single-class-gated by its
header `클래스`). v92 uses its own skill-table numbering; porting the v31 id would point the
condition at the wrong/absent skill on v92 (whitelist item 3). KEEP the v92 ids. Recommended: a
live-test checkpoint per quest that the v92 id resolves to that class's first skill on the running
v92 `SkillData`.

## Story-group diff

MATCH. Both sources register the identical band membership in the identical order:

- **StoryGroup 1** (18 band quests): `1301, 1304, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378,
  1379, 1303, 1329, 1384, 1382, 1383, 1331, 1305`
- **StoryGroup 2** (7 band quests): `1311, 1309, 1313, 1350, 1315, 1316, 1317`

(Only the `name`/`dec` display attributes differ by locale - v31 server ships Russian display
strings - which is not a spine difference.) Note 1379 (Gunner) and 1383 (Gathering Your Strength)
are fully built and story-registered in **both** sources; neither is v92-only content.

## Internal-inconsistency findings (doctrine rule 1)

Two v31 quests contradict themselves (task kill target vs dialog `LinkCreature`), carried
identically into v92. **Both are sentinel-disabled in both sources, so the inconsistency is
dormant.** Per doctrine rule 1, fix to internal consistency and log **when the padding phase makes
them live**, not now.

| gid | title | task kills | dialog LinkCreature | status |
|-----|-------|-----------|---------------------|--------|
| 1322 | Unrest in the Forest | 13,300931 | 13#300932 | dormant (disabled both) - off-by-one target |
| 1327 | Garrison in Distress | 13,300921 | 13#304 | dormant (disabled both) - Noruk B vs Sickly Noruk |

Scope note: the scan flags quests that have both hunt tasks and dialog `LinkCreature` tokens whose
creature-id sets are disjoint. No **live** quest is flagged.

## DECISION items (need a policy/design call)

1. **New-class reward item selection.** The whitelist authorizes appending Fighter/Assassin/Glaiver
   rows to the 15 class-scoped reward quests, but v31 only defines items for the 9 old classes, so
   the specific low-level item ids to grant each new class must be chosen during spec authoring.
   Soulless omitted.
2. **New-class quest availability (header `클래스` restrictions).** The class-split and
   training quests gate by class and exclude the new classes - identical in v31 and v92 (so MATCH
   on this axis), but the port inherits the exclusion:
   - `1382` (melee gathering: Warrior/Lancer/Slayer/Berserker/Archer/Engineer) and `1351`
     (melee) - do we widen to admit Fighter/Assassin/Glaiver (melee-family)?
   - `1383`/`1352` (casters: Sorcerer/Priest/Elementalist) - unaffected by the three melee
     new classes.
   - `1371-1379` are single-class training quests; the new classes would need their own training
     quests, which do not exist in either source (out of band / deferred).
   This is a forward new-class-support call, not a v31-vs-v92 correction.

## Specific checks (from the task brief)

1. **1384 charm** - v31 charm item is **7100** (`combat_item_31`, charm/DISPOSAL). Task structure:
   `1 visit -> 2 grant item 98 -> 3 rest-condition -> 4 grant charm 7100 -> 5 use charm 7100 ->
   6 reward`. v92 patch-000 swapped it to 70033. **7100 exists in v92 but is NO_COMBAT** (so it
   cannot be used by the quest); 70033 exists in both as charm/DISPOSAL. Verdict KEEP v92. See the
   KEEP section.
2. **~40 sentinel-disabled** - **CONFIRMED IDENTICAL.** 40 disabled in v31, the same 40 in v92,
   same ids. No quest is disabled in one and live in the other. MATCH.
3. **Internal-inconsistency scan** - 1322 and 1327 flagged; both dormant (disabled in both). 1327
   is exactly the known Garrison-in-Distress case (task 300921 vs dialog 13#304). See the
   internal-inconsistency section.
4. **1382 / 1383 prerequisites** - **prior claim REFUTED.** Both v31 and v92 retain
   `<퀘스트Id>13,84</퀘스트Id>` for **both** 1382 and 1383 (headers byte-identical). v92 did **not**
   drop 1382's prereq. No PORT op needed. MATCH.
5. **Story groups** - identical membership and order (see the story-group section). MATCH.
6. **New-class rewards** - the new-era INTERNAL classes fighter/assassin/glaiver have **no** rows
   in v31 (engineer does). 15 class-scoped reward quests need appended adaptation rows; soulless
   omitted. See the new-class reward gap section.

## KEEP list (reasons)

| gid | what is kept over v31 | reason |
|-----|----------------------|--------|
| 1384 | charm 70033 + item-use condition + task rewiring | patch-000; v31's 7100 is NO_COMBAT on v92 and the rest-stamina mechanic is dead (whitelist 1, 3) |
| 1371, 1373, 1374, 1375, 1379 | v92 skill-learn `스킬Id` | v92 skill-table numbering; v31 id would reference the wrong/absent skill (whitelist 3) |

No quest file is KEEP-because-v92-only: every band quest exists in v31 as well.
