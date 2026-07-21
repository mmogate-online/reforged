# IoD padding: v17 spawn locations for six unspawned HZ-213 quest-giver NPCs

Analysis only. Approximate v17-era spawn positions for six Island of Dawn hunting-zone-213
NPC templates that exist in `NpcData_213` (v31 and v92) but have **zero** `TerritoryData`
spawns in either era. Purpose: groundwork to author `TerritoryData_213` spawns that get
tuned in-game later.

## Summary table

| Template | v92 quest name | v17 name (title) | Giver | Proposed pos (x,y,z) | v92 section | Wiki camp | Nearest baseline spawn | Confidence |
|---|---|---|---|---|---|---|---|---|
| 213,1021 | Eria Elin | Eria (Arcanist) | 1334 | 55608, -82162, -4194 | 13015 Leander's Outpost (167u) | Leander's Outpost | 1015 Teleportal, 7630u | high |
| 213,1009 | Rabram | Kamarnu (Assistant Researcher) | 1332 | 63756, -84169, -3806 | 13033 Southern Checkpoint (498u) | Southern Checkpoint | 1146 Zaccai/Guard, 124u | high |
| 213,1130 | Beres | Jehan (Researcher) | 1333 | 55846, -82512, -4206 | 13015 Leander's Outpost (360u) | Leander's Outpost | 1015 Teleportal, 7847u | high |
| 213,1128 | Mayer | Lorin (Guard) | 1347 | 55392, -81815, -4195 | 13015 Leander's Outpost (524u) | Leander's Outpost | 1015 Teleportal, 7423u | high |
| 213,1126 | Eredos | Ayrdoss (Guard) | 1349 | 49870, -80830, -4521 | 13003 Mysterious Ruins (inside) | Mysterious Ruins (13003) | 1015 Teleportal, 10652u | high |
| 213,1110 | Muriel | Clovis (Patrol) | 1319 | 79293, -82308, -4451 | 13030 Timeless Woods (inside); Dulari's Camp 2500u | Dulari's Camp | 1114 Helier/Guard, 1570u | medium |

Heading/direction is not available from any source (see Method); author `dir` provisionally
and tune in-game.

## Primary source

`D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA\StrSheet_NpcLoc\StrSheet_NpcLoc-00000.xml`.
Each of the six templates carries **exactly one** quest-marker coordinate keyed by
`huntingZoneId="213"` + `templateId`. The `13#` prefix on every string is the IoD world-map
region-string id (region 13), consistent across all HZ-213 markers because they plot on the
single IoD continent map; the `x,y,z` after `#` is the marker world position. This client
registry is the authoritative quest-link location surface for exactly these never-spawned
givers, which is why it holds coordinates when TerritoryData does not.

Raw entries extracted:

```
templateId=1009 hz=213  string="13#63756,-84169,-3806"
templateId=1021 hz=213  string="13#55608,-82162,-4194"
templateId=1110 hz=213  string="13#79293,-82308,-4451"
templateId=1126 hz=213  string="13#49870,-80830,-4521"
templateId=1128 hz=213  string="13#55392,-81815,-4195"
templateId=1130 hz=213  string="13#55846,-82512,-4206"
```

## Method and cross-checks

1. **Pilot artifacts** (`docs/plans/iod-alpha-content-loop/data/`): `v17-npcs.json` confirms all
   six templates exist in the v17 HZ-213 NpcData roster (villager class) but carries no positions.
   `v17-territories.json` HZ-213 holds only three group wander fences (villager groups), none
   referencing the six templates individually. No ready-made positions there.
2. **v17 NpcLoc** (primary): one marker per template, quoted above.
3. **Section naming**: point-in-polygon of each marker against the v92 server
   `AreaData_13_ATW_Death_P.xml` `<Section>` fences (21 sections; HZ 13 and HZ 213 are layered
   over the same IoD terrain, so the HZ-13 map sections name the footprint). Names via
   `section-mapping.json`.
4. **Collision check**: `D:\dev\mmogate\tera92\server\Datasheet\TerritoryData_213.xml` has 51 Npc
   spawn entries; **none** of the six templates appear, confirming they are unspawned in the live
   baseline. Nearest existing spawn per proposed point is listed in the table (all proposed spots
   are free; the closest neighbor is Rabram at 124u from guard 1146 Zaccai, which is normal camp
   density).
5. **v17 territory provenance**: each marker was tested against the v17 HZ-213 group wander fences.
   Every marker falls inside a legitimate v17 IoD-south villager territory (see per-NPC provenance),
   corroborating that the coordinates sit in authentic v17 content space.
6. **v31 client absence**: `Z:\tera pserver\v31.04\client-dc_v31\DataCenter_Final_EUR_v31\StrSheet_NpcLoc-00000.xml`
   has 26 HZ-213 entries; none of the six templates are present. Confirmed absent, as expected.

Heading is null because NpcLoc does not carry it and the six templates have no authored
TerritoryData spawn (in v17, v31, or v92) from which a heading could be read.

## Per-NPC detail

### 213,1021 Eria Elin (v17 Eria, Arcanist), giver 1334 "Investigating the Relics"
- Proposed pos: **55608, -82162, -4194**, dir null.
- Source: v17 NpcLoc `13#55608,-82162,-4194`.
- Section: inside v92 `13015 Leander's Outpost` fence (nearest section centroid 167u). Matches
  the wiki expectation (Leander's Outpost) and the pending placement-correction note in
  `legacy-quest-locations.md` (Eria's authentic post is Leander's Outpost, not Tainted Gorge).
- v17 provenance: inside group `21300003` desc `여명의 정원 남부 (21300003)` ("Dawn's Garden South"),
  fence index 6.
- Nearest baseline spawn: 1015 Teleportal at (58986,-75321), 7630u away. Spot is free.
- Confidence: high.

### 213,1009 Rabram (v17 Kamarnu, Assistant Researcher), giver 1332 "They'll Eat Anything"
- Proposed pos: **63756, -84169, -3806**, dir null.
- Source: v17 NpcLoc `13#63756,-84169,-3806`.
- Section: inside v92 `13033 Southern Checkpoint` fence (nearest section centroid 498u). Matches
  the wiki expectation (Southern Checkpoint).
- v17 provenance: inside group `1300005` desc `여명의 정원 빌리저` ("Dawn's Garden Villager"), fence
  index 6.
- Nearest baseline spawn: 1146 Zaccai (Guard) at (63867,-84115), 124u away. Very close, but that is
  normal Southern Checkpoint camp density; the spot itself is unoccupied by any of the six.
- Confidence: high.

### 213,1130 Beres (v17 Jehan, Researcher), giver 1333, receiver for 1332
- Proposed pos: **55846, -82512, -4206**, dir null.
- Source: v17 NpcLoc `13#55846,-82512,-4206`.
- Section: inside v92 `13015 Leander's Outpost` fence (nearest section centroid 360u). Matches the
  wiki expectation (Leander's Outpost). Sits about 360u from Eria/Mayer, consistent with all three
  being the Leander's Outpost researcher cluster.
- v17 provenance: inside group `21300003` `여명의 정원 남부` fence index 6 (also inside a
  check/test territory `21300001` `체크용 테리토리`).
- Nearest baseline spawn: 1015 Teleportal at (58986,-75321), 7847u away. Spot is free.
- Confidence: high.

### 213,1128 Mayer (v17 Lorin, Guard), giver 1347 "It Was a Rock...Crawler!"
- Proposed pos: **55392, -81815, -4195**, dir null.
- Source: v17 NpcLoc `13#55392,-81815,-4195`.
- Section: inside v92 `13015 Leander's Outpost` fence (nearest section centroid 524u). Matches the
  wiki expectation (Leander's Outpost).
- v17 provenance: inside group `21300003` `여명의 정원 남부` fence index 6.
- Nearest baseline spawn: 1015 Teleportal at (58986,-75321), 7423u away. Spot is free.
- Confidence: high.

### 213,1126 Eredos (v17 Ayrdoss, Guard), giver 1349 "Gotta Kill 'em All"
- Proposed pos: **49870, -80830, -4521**, dir null.
- Source: v17 NpcLoc `13#49870,-80830,-4521`.
- Section: inside v92 `13003 Mysterious Ruins` fence. Matches the wiki expectation exactly
  (Mysterious Ruins, section 13003), the only quest of the ruins proper.
- v17 provenance: inside group `21300003` `여명의 정원 남부` fence index 0.
- Nearest baseline spawn: 1015 Teleportal at (58986,-75321), 10652u away (the ruins are otherwise
  empty of baseline spawns). Spot is free.
- Confidence: high.

### 213,1110 Muriel (v17 Clovis, Patrol), giver 1319 "Dwellers of the Island"
- Proposed pos: **79293, -82308, -4451**, dir null.
- Source: v17 NpcLoc `13#79293,-82308,-4451`.
- Section: falls inside the v92 `13030 Timeless Woods` container polygon, **not** inside the
  `13032 Dulari's Camp` section polygon the wiki names. Nearest camp centroid is Dulari's Camp at
  2500u; nearest baseline NPC is `1114 Helier (Guard)` at 1570u (Helier reads as a Dulari's Camp
  guard). So the v17 marker sits on the approach between Timeless Woods and Dulari's Camp.
- v17 provenance: inside group `1300005` `여명의 정원 빌리저` ("Dawn's Garden Villager"), fence
  index 8.
- Nearest baseline spawn: 1114 Helier (Guard) at (80637,-81496), 1570u away. Spot is free.
- Confidence: **medium**. Discrepancy: data-derived point is outside the wiki-named Dulari's Camp
  polygon. Recommendation: author at the v17 marker, and if it reads as too far from the camp
  in-game, nudge toward the Dulari's Camp centroid (81005,-80400) during tuning.

## Discrepancies vs the legacy wiki mapping

- Five of six markers land inside (or within a few hundred units of the centroid of) the exact
  camp the wiki names: Eria, Beres, Mayer at Leander's Outpost; Rabram at Southern Checkpoint;
  Eredos at Mysterious Ruins 13003. Data agrees with wiki.
- Muriel (1110) is the only mismatch: the v17 marker is on the Timeless Woods side of the approach
  to Dulari's Camp (2500u from camp centroid), not inside the Dulari's Camp polygon. Data wins;
  kept at the v17 marker with a tuning note.
