# Island of Dawn (continent 13) - Deleted v17.11 sections vs v92 layout

Spatial overlap of the 12 sections present in v17.11 `ATW_P` (Area-00004.xml) but absent from v92 `ATW_Death_P`, mapped onto the live v92 section layout.

## Coordinate representation

Section polygons are ordered <Fence pos='x,y,z'/> rings; x,y is the horizontal plane (world units, ~ -12000..96000 here), z is terrain height (ignored for footprint). Sections nest; each section's polygon is its DIRECT Fence children only. Overlap estimated by 60-unit uniform sample grid, point-in-polygon ray casting.

Tower Base (64001) and Researcher Quarters (64007) are one nested pair; in v92 they survive only as a **commented-out** `<Section>` block in the server file `AreaData_13_ATW_Death_P.xml` and are absent from the client Area file.

## Overall map coverage

- v17 main section 13001 footprint area: **1,021,377,335** sq units

- v92 main section 13001 footprint area: **1,021,377,336** sq units

- Main-section bounding box identical both eras: `[47267.7, -92060.1, 96230.0, -62774.2]` == `[47267.7, -92060.1, 96230.0, -62774.2]`

- All 10 vertices of the 13001 outer fence match to <0.001 units between eras: **the island outline / walkable footprint was NOT rebuilt.** The map is the same physical terrain; only the interior section subdivision changed.

- Every point of the v17 footprint still falls inside a v92 section (**100.0%**), because parent section 13001 blankets the whole island in both eras.

- But only **6.2%** of the island is covered by v92 *camp/sub-scale* sections; ~94% is generic region (13001/13003/13004/13030) plus the two new region-scale additions (13035 Ruined Temple, 13031 North Dock).

## Deleted section verdicts

`new-region overlap` = the deleted footprint now sits inside a v92 section that did NOT exist in v17 (newly built content). `kept-region only` = it sits inside regions retained from v17, i.e. genuinely empty ground with no new section drawn over it.

| v17 sec | name | area | centroid (x,y) | best v92 camp target | camp ov% | container overlaps | new content over it? |
|---|---|---|---|---|---|---|---|
| 13002 | Pegasus Platform | 1,871,124 | [70800.9, -69999.0] | NONE | 0 | 13001:100.0%, 13035:100.0% | 13035(Ruined Temple) 100.0% |
| 13005 | Northern Checkpoint | 3,464,320 | [87150.9, -85355.0] | NONE | 0 | 13001:100.0%, 13030:100.0% | no (kept-region only) |
| 13008 | Orcan Bivouac | 1,924,552 | [50003.0, -78098.3] | NONE | 0 | 13001:100.0%, 13003:100.0% | no (kept-region only) |
| 13013 | Terron Run | 1,149,315 | [65965.1, -70295.0] | NONE | 0 | 13001:100.0%, 13035:25.8% | 13035(Ruined Temple) 25.8% |
| 13015 | Leander's Outpost | 3,087,104 | [55495.6, -82321.9] | NONE | 0 | 13001:100.0%, 13003:100.0% | no (kept-region only) |
| 13017 | Dulari's Camp | 854,575 | [80795.7, -81058.2] | 13032 | 83.3 | 13001:100.0%, 13030:100.0% | no (kept-region only) |
| 13018 | Northern Overwatch | 4,709,706 | [74060.2, -82725.8] | NONE | 0 | 13001:100.0%, 13030:100.0% | no (kept-region only) |
| 13020 | Southern Checkpoint | 701,777 | [63760.4, -84045.2] | 13033 | 69.3 | 13001:100.0%, 13035:100.0% | 13035(Ruined Temple) 100.0% |
| 13022 | Tainted Gorge Garrison | 2,938,520 | [64690.0, -65510.9] | NONE | 0 | 13001:100.0% | no (kept-region only) |
| 13027 | Tainted Gorge Outpost | 1,609,580 | [52927.8, -69723.2] | 13034 | 80.8 | 13001:100.0%, 13004:100.0% | no (kept-region only) |
| 64001 | Tower Base | 33,625,444 | [68409.3, -78763.2] | NONE | 0 | 13001:100.0%, 13035:100.0% | 13035(Ruined Temple) 100.0% |
| 64007 | Researcher Quarters | 1,977,092 | [70230.2, -81703.6] | NONE | 0 | 13001:100.0%, 13035:100.0% | 13035(Ruined Temple) 100.0% |

## Renumbered camps (same name, new nameId, redrawn fence)

Quantifies drift so we know whether v17 hard-coded spawn coordinates still land inside the new v92 fence.

| old -> new | name | centroid shift | area old -> new | old footprint inside new fence | new inside old | IoU | old centroid in new fence |
|---|---|---|---|---|---|---|---|
| 13017->13032 | Dulari's Camp | 690 | 854,575 -> 2,536,333 | 83.3% | 27.6% | 26.2% | True |
| 13020->13033 | Southern Checkpoint | 474 | 701,777 -> 1,393,680 | 69.3% | 34.0% | 29.8% | True |
| 13027->13034 | Tainted Gorge Outpost | 74 | 1,609,580 -> 1,337,711 | 80.8% | 97.1% | 78.3% | True |

Reads: **13034 Tainted Gorge Outpost** barely moved (74 units, 78% IoU, old footprint 97% inside new) - old spawn coords are safe. **13032 Dulari's Camp** and **13033 Southern Checkpoint** were enlarged (2-3x) and shifted 470-690 units; old centroids stay inside the new fence, but 17% (13032) and 31% (13033) of the old footprint now lies OUTSIDE the new fence, so v17 spawn points near the old camp edges may fall out of bounds and need re-clamping to the new polygon.

## Restore-vs-remap read

**Terrain is intact.** The 13001 outline is byte-for-byte identical between eras, so a deleted section's fence ring can be re-inserted as pure data without any terrain conflict; the only question is whether it overlaps a v92 section that now owns that ground.

Three groups:

1. **Renumbered camps already present (remap, do not re-add):** 13017->13032, 13020->13033, 13027->13034. The camp still exists under a new nameId. Point v17 content at the new id; re-clamp edge spawns for 13032/13033.

2. **Clear ground - safe to restore as data polygons (no new section over them):** 13005 Northern Checkpoint, 13008 Orcan Bivouac, 13015 Leander's Outpost, 13018 Northern Overwatch, 13022 Tainted Gorge Garrison. Their footprints sit only inside retained v17 regions (13001/13003/13030); no *new* v92 section was drawn over that space, so restoring the original fence collides with nothing new. (13005/13018 are contained by the retained region 13030, which already spanned that ground in v17.)

3. **Space rebuilt with NEW v92 content (restoring the polygon collides):** 13002 Pegasus Platform and 64001 Tower Base + 64007 Researcher Quarters now sit 100% inside **13035 Ruined Temple** (a region-scale section new in v92); 13013 Terron Run overlaps it ~26%. The Ruined Temple was built directly over the old Tower Base / Pegasus Platform ground. Re-adding these fences would overlap a live v92 section, so they need remap onto 13035 (or deliberate layering), not blind restoration.
