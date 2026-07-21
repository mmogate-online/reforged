# IoD Padding Wave B: spawn-density diagnosis and fix proposal

Scope: spawn density of the three live-test problem areas from patch 001 spec
`15-iod-mob-habitats.yaml` (HZ 13). Analysis only; no specs or datasheets changed.

Sources parsed: v92 `TerritoryData_13.xml` (applied state), v31
`TerritoryData_13.xml` + `QuestData/001349|001348|001319.quest` (kill counts and
donor populations), v17.11 client `TerritoryData-00005.xml` (classic geometry),
`v17-quests.json` (classic quest objectives), `padding-habitat-gaps.json` and
`padding-npcloc-sweep.json` (generator inputs).

## Confirmed kill / collect requirements

Quest bodies are byte-for-byte the same objective in v31 and v17 (hypothesis B
check below):

| Quest | Title | Task | Objective | Count |
|-------|-------|------|-----------|-------|
| 1349 | Gotta Kill 'Em All | hunt | tpl 4 (미니 오칸 / Mini Orcan) | 48 |
| 1349 | | hunt | tpl 5 (오칸 습격자 / Orcan Raider) | 6 |
| 1348 | Ferocious Flowering Felons | hunt-deliver | item from tpl 302 (90%) / 303 (17%) | 8 items |
| 1319 | Dwellers of the Island | hunt-deliver | item from tpl 300944 (85%) / 300941 (12%) | 5 items |

User's memory is correct: quest 1349 requires 48 kills of template 4.

## Which templates count (and which do not)

Only the templates listed above give quest credit. The family neighbors that
share the same habitat and look near-identical do NOT count:

- Orcan camp: tpl 902 and tpl 1003 are both `오칸미니미` (race OrcanMinimi),
  visually the same as the credit mob tpl 4 `미니 오칸`. They give no 1349 credit.
- Orcan patrol: tpl 901 and tpl 1002 are both `오칸` (race OrcanPirate), siblings
  of the credit mob tpl 5 `오칸 습격자`. They give no 1349 credit.

This is the source of the "crowded area, no quest credit" effect (user
hypothesis B). It is authentic classic behavior, not a bug (see below).

## Root-cause diagnosis per area

### Area 1 - Quest 1349 (Orcan camp), too sparse

Two independent density faults stack:

1. Round-robin template dilution. The generator assigns roster templates
   round-robin, one per territory (`gen_habitat_specs.py` line ~588,
   `tpl = roster[i % len(roster)]`).
   - Group 1300036 (camp outskirts), roster `[4, 902, 1003]` over 4 territories
     -> tpl 4 lands on only territories 0 and 3 = **2 spawns of the 48-kill
     target**. tpl 902 and 1003 take the other 2.
   - Group 1300038 (patrol), roster `[5, 901, 1002]` over 12 territories -> tpl 5
     lands on 4 territories = 4 spawns.
2. spawnCount 1 everywhere. Every restored territory carries the base
   archetype's single mob. Classic Orcan minions were dense pack farms.

Result: 2 concurrent tpl 4 for a 48-kill quest. With respawnTime 20000 (+2000
random), a solo player clears 2, waits ~22 s, repeats. 48 kills / 2 = 24 cycles
= roughly 9 minutes of pure respawn waiting. This matches the report exactly.

tpl 5 at 4 concurrent for a 6-kill objective is borderline acceptable solo but
thin for 2-3 concurrent players.

### Area 2 - Quest 1348 (Terron Ringleader/Thief 302/303), too low

Bespoke group 1300060 has 2 territories (one for tpl 302, one for tpl 303),
spawnCount 1. The generator built these from a 10-marker NpcLoc cluster but
collapsed all 10 markers into a single convex hull and emitted one territory per
template (`gen_habitat_specs.py` lines ~613-642, `hull = convex_hull(pts)` then
one territory per roster entry).

So NpcLoc actually supplied 10 spawn points and the generator discarded 9 of
them. Result: 1 concurrent tpl 302 for a quest needing ~9 kills of it (8 items at
90% drop). Solo ~3.3 minutes of waiting; multiplayer competes for a single mob.

### Area 3 - Quest 1319 (Terron 300941/300944), too low

Same generator fault as area 2. Bespoke group 1300061 = 2 territories from a
17-marker cluster collapsed to one hull. 1 concurrent tpl 300944 for a quest
needing ~6 kills of it (5 items at 85% drop). 16 of 17 markers discarded.

## Hypothesis verdicts

- Hypothesis A (NpcLoc under-represents clustered mobs): half true. The NpcLoc
  data was fine (10 and 17 distinct markers, roughly one per classic spawn
  point). The under-representation was introduced by the generator collapsing
  the marker set into a single hull, not by NpcLoc.
- Hypothesis B (family neighbors should count / quest widening): NOT warranted
  for fidelity. `v17-quests.json` and the v31 quest bodies list the identical
  narrow template set for all three quests. The neighbor mobs never counted in
  classic. The correct fix is spawn-side dominance, not quest widening. A
  quest-widening variant is possible as a deliberate non-classic UX change and
  is flagged for approval at the end.

## Cluster model reference (how classic / v31 model packs)

- v17 client `TerritoryData` carries geometry only (fence rings, no Npc, no
  Party). It cannot tell us pack size; it gave 4 rings for 1300036 and 12 for
  1300038. The v17 SERVER spawn data is not available.
- v31 donor group 1300035 (`비행선 추락지(오칸)`): 29 territories, each a single
  `<Party flock="true" partyRespawnTime="20000">` wrapping ONE `<Npc
  spawnCount="1">` (tpl 901). So v31 models this family as many single-mob
  flocking parties, not multi-member packs.
- Live v92 HZ 13 idiom: spawnCount distribution across all groups is
  1:504, 3:132, 6:53, 4:16, 2:14, plus 214 Party tags. spawnCount 3-6 and pack
  Parties are both normal and idiomatic. Raising spawnCount is the least
  invasive faithful lever; it needs no Party schema and rides the existing
  spawn-restore-standard archetype.

## Proposed fixes (before / after in-world concurrent counts)

Density target assumptions: solo player should not wait more than ~1 respawn
cycle (~22 s) for the next credit mob; 2-3 concurrent players should not fully
deplete the credit population. Rule of thumb used: concurrent credit mobs >=
required_count / 3, and >= 6 for hunt-deliver single-drop mobs.

| Area | Group | Fix | Before | After |
|------|-------|-----|--------|-------|
| 1349 tpl 4 | 1300036 | all 4 territories -> tpl 4; spawnCount 5 | 2 | 20 |
| 1349 tpl 5 | 1300038 | keep round-robin; spawnCount 2 (tpl5 on its 4 terrs) | 4 | 8 |
| 1348 tpl 302 | 1300060 | one territory per marker; weight 302 6 / 303 4 | 1 | 6 |
| 1348 tpl 303 | 1300060 | (same) | 1 | 4 |
| 1319 tpl 300944 | 1300061 | one territory per marker; weight 300944 10 / 300941 7 | 1 | 10 |
| 1319 tpl 300941 | 1300061 | (same) | 1 | 7 |

Expected clear times after fix:
- 1349: 48 tpl 4 / 20 concurrent = ~2.4 cycles ~50 s wait solo; sustains 2-3
  players. 6 tpl 5 / 8 concurrent = no wait.
- 1348: 8 items / 6 concurrent tpl 302 = ~2 cycles solo; 10 mobs remove
  single-mob contention.
- 1319: 5 items / 10 concurrent tpl 300944 = under 1 cycle; 17 mobs, no
  contention.

### Concrete generator changes (`tools/dc-restore/gen_habitat_specs.py`)

1. Bespoke quest groups (per-marker instead of hull-per-template). In the
   bespoke block (lines ~613-642), replace the single convex hull with one small
   territory per marker: iterate the marker list, emit a small square fence
   (e.g. +/-150 units around the marker), one spawn per territory, assigning
   templates by a weighted split (302:303 = 6:4 over 10 markers; 300944:300941 =
   10:7 over 17 markers, weighting the high-drop template). spawnCount stays 1.
   This uses every NpcLoc marker instead of discarding all but one.

2. Quest-served v17 groups (density override). Add a small table, e.g.
   `QUEST_DENSITY = {1300036: {"force_roster": [4], "spawnCount": 5},
   1300038: {"spawnCount": 2}}`, and apply it in the v17-group loop: when a
   group id is present, override the roster (so the credit template dominates)
   and merge `spawnCount` into the per-spawn overrides (same mechanism as
   `GENERIC_COMBAT_OVERRIDE`). Group 1300036 becomes 4 territories of tpl 4 at
   spawnCount 5; 1300038 keeps its roster but doubles spawnCount.

   Fidelity note: forcing 1300036 to all tpl 4 drops flavor mobs 902/1003 from
   that camp. This is defensible: the camp IS the Mini Orcan farm for the
   48-kill quest, and 902/1003 remain available elsewhere. Alternative if 902/
   1003 must be preserved: keep 1 territory each for 902/1003 and put tpl 4 on
   the other 2 territories at spawnCount 8 (= 16 concurrent tpl 4).

All changes stay within the spawn-restore-standard archetype (spawnCount is a
plain override field), so no package edits are required.

## User-approval item (optional, NON-CLASSIC)

Quest widening for 1349 (hypothesis B, UX variant). If the "crowded but no
credit" confusion should be removed at the quest level rather than the spawn
level, quest 001349 task 1 could be widened to also count the sibling templates:
add `13,902` and `13,1003` to the tpl 4 objective and `13,901` and `13,1002` to
the tpl 5 objective (with recalculated counts). This changes quest behavior and
diverges from classic (both v17 and v31 count only 13,4 and 13,5), so it is
flagged for explicit approval and is NOT part of the recommended spawn-side fix.
The spawn-side fix above resolves the density and the confusion without touching
quest behavior, and is the recommended path.
