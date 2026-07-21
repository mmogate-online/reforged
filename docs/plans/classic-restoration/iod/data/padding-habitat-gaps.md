# IoD Padding L1-W6: Mob Habitat Gap Analysis

Analysis only (no specs, no datasheet changes). Deliverable pair: this report plus `padding-habitat-gaps.json` (machine-readable, includes every v17 fence polygon for the spec-authoring phase).

**Scope:** Island of Dawn combat zone HZ 13 (primary), HZ 64 and HZ 213 (secondary). MOBS ONLY, per doctrine rule 5. NPC and villager territories are excluded.

**Method.** v17 fence polygons come from the v17.11 client TerritoryData; the client stores fences and a Korean TerritoryGroup description only, no per-territory roster. The mob family is read from the group description; the actual template ids and all spawn attributes (respawnTime, spawnCount, randomPos, ai, aggression) come from a comparable v31 donor group of the same mob family in the same zone. Baseline is v92 TerritoryData_13, which is byte-identical to v31 (641 spawns / 470 territories island-wide, 25 mob groups in HZ 13). Classification is by same-family baseline overlap: MISSING when the nearest baseline territory of the same mob family is more than 1500 units from the v17 group centroid (or the family is absent from the zone), PARTIAL when a same-family baseline territory is closer than that but roster or density differs. Every replicated territory is an approximation and is logged as such.

**Sources reused:** `iod-alpha-content-loop/data/` artifacts `v17-territories.json`, `v31-spawns.json`, `v31-npc-stats.json`, `classification-spawns.json`, `section-spatial.md`, `2026-07-17-ruins-archaeology.md`; live `AreaData_13_ATW_Death_P.xml` for section polygons.

## Coverage summary

| HZ | v17 mob groups | baseline mob groups | MISSING | PARTIAL | matched/covered | verdict |
|----|----------------|---------------------|---------|---------|-----------------|---------|
| 13 | 40 | 25 | 16 | 1 | 23 | 17 v17-only mob groups deleted pre-v31; all roster templates still exist in v92 NpcData_13; 2 population-donor blockers |
| 64 | 2 | 2 | 0 | 0 | 2 | Tower Base area, both groups match baseline; no mob habitat gap |
| 213 | 3 | 4 | 0 | 0 | 4 | baseline has 1 extra v31-only group (21300004, an alliance-quest territory, NPC/quest not mob); no mob habitat gap |

The entire habitat gap is in HZ 13. HZ 64 and HZ 213 have no missing mob habitat. The loss predates v31 (these groups exist in the v17.11 client but not in the v31 server baseline), so "restore from v31" cannot recover them; only v17 geometry plus v31 same-family donor attributes can.

## Gap table (prioritized)

Roster column lists the v31/v92 NpcData template ids proposed for the pocket (all verified present in NpcData_13). Donor is the v31 group whose population, respawn and flags are copied.

| P | v17 group | area (section) | mob family | class | v17 terr / verts | roster templates | donor group | blocker |
|---|-----------|----------------|------------|-------|------------------|------------------|-------------|---------|
| 1 | 1300031 | Mysterious Ruins (13003) | Decaying Argas | MISSING | 22 / 67 | 304, 300920, 300921 | 1300018 | |
| 1 | 1300032 | Mysterious Ruins (13003) | Polluted Earth Spirit | MISSING | 18 / 95 | 2, 3 | 1300026 | |
| 1 | 1300033 | Mysterious Ruins (13003) | Rockcrawler / Stone Crawler | MISSING | 14 / 74 | 300541, 300542, 300540 | none | population donor |
| 1 | 1300034 | Mysterious Ruins (13003) | Dying Cromos | MISSING | 27 / 109 | 300910, 300911 | 1300039 | |
| 1 | 1300036 | Mysterious Ruins camp outskirts (13003/13008) | Orcan Minimi | MISSING | 4 / 24 | 4, 902, 1003 | 1300035 | |
| 1 | 1300037 | Mysterious Ruins camp interior (13003/13008) | Dark Marauder | MISSING | 3 / 15 | 601, 300951, 300960 | 1300040 | |
| 1 | 1300038 | Mysterious Ruins Orcan patrol (13003) | Orcan Pirate | MISSING | 12 / 48 | 5, 901, 1002 | 1300035 | |
| 1 | 1300057 | Mysterious Ruins ambient (13003) | Spirit of Nature (env 102) | PARTIAL | 11 / 44 | 102 | 1300054 | |
| 1 | 1300058 | Mysterious Ruins (13003) | Stone Head (env 301) | MISSING | 6 / 30 | 301 | none | population donor |
| 2 | 1300022 | Near Base / Vanguard staging (13001) | Spirit of Nature (env 102) | MISSING | 10 / 50 | 102 | 1300056 | |
| 2 | 1300025 | Near Base / Vanguard staging (13001) | Decaying Argas | MISSING | 32 / 96 | 304, 300920, 300921 | 1300018 | |
| 2 | 1300028 | Near Base gorge edge (13001/13004) | Dark Marauder | MISSING | 3 / 12 | 601, 300951, 300960 | 1300040 | |
| 2 | 1300029 | Near Base gorge edge (13001/13004) | Fallen Spirit of Nature (Terron) | MISSING | 10 / 50 | 300942, 300943, 300945 | 1300140 | roster choice |
| 2 | 1300030 | Near Base Black Rift side (13001/13004) | Polluted Earth Spirit | MISSING | 6 / 30 | 2, 3 | 1300026 | |
| 3 | 1300019 | Timeless Woods mid (13030) | Spirit of Nature (env 102) | MISSING | 17 / 85 | 102 | 1300054 | |
| 3 | 1300020 | Timeless Woods late (13030) | Ghilliedhu | MISSING | 11 / 44 | 300930, 300931, 1001 | 1300016 | |
| 3 | 1300021 | Timeless Woods late aggressive (13030) | Ghilliedhu (aggressive) | MISSING | 11 / 66 | 300932, 300933 | 1300023 | |

Total gap: 217 v17 mob territories across 17 groups, 9 of them concentrated in the Mysterious Ruins (117 territories).

**Donor spawn profile (for reference, uniform across the pure combat donors).** Groups 1300016/1300018/1300023/1300026/1300039 each spawn one mob per territory with `spawnCount=1`, `respawnTime=20000`, `randomPos=true`, `isAggressiveMonster=false` (aggression is driven by the template AI, not this flag). Environment donors 1300054/1300056/1300059/1300140 use `spawnCount=3`. The Orcan camp donor 1300035 mixes `randomPos` true/false (fixed patrol posts) and the Dark Marauder donor 1300040 uses `spawnCount=6` for the pack template 300960. Copy the matching profile per family.

## Mysterious Ruins deep-dive (priority 1)

The user's called-out "bland, de-populated" example. Section 13003 in the live server is literally named 태고의 유적지 (Ancient Ruins); its polygon (11 vertices, centroid 54124,-81241, x 46899..63050, y 90776..71958) blankets the whole southern ruins band, including the nested Orcan Bivouac section 13008 (오칸 야영지, centroid 49991,-78114) and the Leander's/Kubel Outpost section 13015.

**What v17.11 had here:** nine mob territory groups, 117 fenced territories, spanning six mob families:
- Decaying Argas (1300031, 22 terr)
- Polluted / Tainted Earth Spirit (1300032, 18 terr)
- Rockcrawler / Stone Crawler (1300033, 14 terr)
- Dying Cromos (1300034, 27 terr)
- Orcan Minimi at the camp outskirts (1300036, 4 terr) and Orcan patrol (1300038, 12 terr)
- Dark Marauder inside the camp (1300037, 3 terr)
- Spirit of Nature ambient (1300057, 11 terr) and Stone Head ambient (1300058, 6 terr)

This reads as a full ruins ecology: earth and nature elementals among the stones, roving rockcrawlers, dying cromos, and an occupied Orcan camp (patrol plus minions plus a marauder core) tucked into the Orcan Bivouac.

**What the baseline has now:** inside section 13003 the only mob-side content is group 1300048, nine exploding powder kegs (template 999, props, not creatures). Group 1300035 Orcan (template 901) that the earlier ruins-archaeology note associated with this section is in fact entirely in the northern gorge (x 63871..68268, y 73712..65998), zero territories within 3000 units of the ruins camp. The shrine-ambient environment groups 1300140 (Nature Spirit 102) and 1300141 (Honeybee 101) only clip the ruins edge from 2265 units out. So the ruins interior is genuinely empty of habitat mobs: kegs and a little edge ambient, nothing to fight. That is the blandness.

**Replication recipe for the ruins:** re-add the nine v17 fence groups under HZ 13, roster each from its family template set above, copy population and respawn from the listed v31 donor. Seven of the nine have a clean same-family donor. Two are blocked on the population donor (see below). This single pocket restores the largest share of the lost density and is the highest-value target.

## Blocked candidates

Both blockers are population-donor blockers, not roster blockers. The roster templates exist in NpcData_13 and can be spawned; what is missing is a v31 territory of the same family to copy density and attributes from, so each needs a small DECISION.

- **1300033 Rockcrawler / Stone Crawler (Mysterious Ruins).** Templates 300540/300541/300542 exist but are quest-target only (quest 1347); zero v31 territories spawn them. Proposed substitute: copy the generic combat-mob profile (spawnCount 1, respawn 20000, randomPos true) used by every pure donor group. DECISION: confirm the substitute density and whether all three tiers or only the common 300541 should populate.
- **1300058 Stone Head env (Mysterious Ruins).** Env template 301 (Stone Head) has zero v31 spawns anywhere in the zone. Proposed substitute: copy the environment profile (spawnCount 3, respawn 20000, randomPos true) from env donor 1300054 or 1300059. DECISION: confirm the ambient density.

One soft item (not a hard blocker): **1300029 Fallen Spirit of Nature (Terron), Near Base gorge edge.** The same-named baseline group 1300140 spawns only the environment template 102. Fightable corrupted-Terron templates 300942/300943/300945 do exist. DECISION: if this pocket is meant to be a combat pocket, take the fightable roster and copy density from Black Rift group 1300041; if ambient, use env 102. Default assumption: combat, matching the v17 family name.

## Prioritized candidate list

1. **Mysterious Ruins (priority 1), 9 groups, 117 territories.** The user's target and the biggest single density restore. Seven groups ready (1300031, 1300032, 1300034, 1300036, 1300037, 1300038, 1300057); two need a substitute-donor DECISION (1300033, 1300058). Restores the ruins ecology: earth/nature elementals, rockcrawlers, cromos, and the occupied Orcan camp.
2. **Near Base ring (priority 2), 5 groups, 61 territories.** The early-leveling hub around the Vanguard staging area and the Black Rift edge: Nature Spirit and Argas at the staging ground (1300022, 1300025), Dark Marauder, corrupted Terron and Polluted Earth Spirit along the gorge edge (1300028, 1300029, 1300030). High player traffic; second priority after the ruins. 1300029 carries the roster-choice DECISION.
3. **Timeless Woods east arc (priority 3), 3 groups, 39 territories.** The eastern woods leveling stretch: ambient Nature Spirit (1300019) and the Ghilliedhu late-woods pair, passive and aggressive (1300020, 1300021). All three have clean donors; lowest urgency because the adjacent baseline woods groups 1300016/1300018 already give the area some population.
