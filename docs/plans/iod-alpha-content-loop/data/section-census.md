# Island of Dawn Deleted-Section Reference Census

Scope: 12 v17.11 sections deleted or renumbered in v92 (continent 13, ATW_P to
ATW_Death_P) plus the 3 v92 renumber targets. Read-only census over v17.11 client
DataCenter and v31 server datasheet. Goal: inform the restore-vs-remap decision.

Sources:
- v17.11 client: `D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA`
- v31 server: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet`

## 1. How content references a section

A section is defined by two paired records, keyed by the same **section nameId**:

| Record | File family | Meaning |
|---|---|---|
| `<Section nameId="ID" ...>` + `<Fence pos=.../>` | `Area` (client `Area-*.xml`) / `AreaData` (server `AreaData_13_*.xml`) | Polygon geometry, hunting-zone binding, pk/rest flags, worldMapSectionId |
| `<String id="ID" string="Name"/>` | `StrSheet_Region` | Display name shown on entry / minimap |

Content that points *at* a section does so **by that region-string id**, through
one of these mechanisms (all discovered in the data, not assumed):

| Mechanism | Where | Example |
|---|---|---|
| `@rgn:ID` teleport destination | `TeleportData` | `<Teleport uniqueId="4371002" stringId="@rgn:64001"/>` |
| `@Rgn:ID$$Name` inline token | `QuestGroupList` HuntingZone name, `QuestDialog` body text | `<HuntingZone id="64" name="{@Rgn:64001$$Elleon's Outpost}"/>` |
| `nameId="ID"` world-map section | `NewWorldMapData` | `<Section id="6" type="town" nameId="64001" .../>` |
| `stringId="ID"` town/HZ label | `GuardData` | `<Town stringId="64001"/>` |
| `stringId`/`titleStringId="ID"` | `MapDefineData` | `<Text stringId="13013" .../>` (minimap label) |

**Quest tasks do NOT use the section nameId.** Quest region targeting uses a
separate scheme:
- `<목표지역>hz,region</목표지역>` where `region = hz*100000 + N` (e.g. `213,21300011`)
- `<지역명>@quest:STRID</지역명>` (a quest string, not a region string)
- `<수행조건>`/`수행지역` header pursue-region

None of these resolve to any of the 12 deleted sub-section nameIds. The only IoD
quest `목표지역` values point at hunting-zone 213 regions (`21300011`, `21300020`),
which are unaffected.

Collisions excluded from all counts (confirmed by context inspection): pegasus
path `rot="0,13008,-1116"` / `loc` floats, `StrSheet_NpcLoc` coordinate blobs
(`7012#13008,-93873,69`), and `ItemData`/`AchievementList`/`Skill*` id-space reuse
of the same 5-digit numbers.

## 2. Census: dependency edges per section

"Dependency edges" = genuine references *from other content* (excludes the
section's own StrSheet_Region + Area definition, which every section has once).

| nameId | Name | v92 status | v17 dep edges | v31 dep edges | Edge types |
|---|---|---|---|---|---|
| 13002 | Pegasus Platform | deleted | 0 | 0 | none |
| 13005 | Northern Checkpoint | deleted | 0 | 0 | none |
| 13008 | Orcan Bivouac | deleted | 0 | 0 | none |
| 13013 | Terron Run | deleted (id reused) | 1 | 0 | mapdefine label |
| 13015 | Leander's Outpost | deleted (id reused) | 0 | 0 | none |
| 13017 | Dulari's Camp | renamed to 13032 | 0 | 0 | none |
| 13018 | Northern Overwatch | deleted | 0 | 0 | none |
| 13020 | Southern Checkpoint | renamed to 13033 | 0 | 0 | none |
| 13022 | Tainted Gorge Garrison | deleted | 0 | 0 | none |
| 13027 | Tainted Gorge Outpost | renamed to 13034 | 0 | 0 | none |
| 64001 | Tower Base | deleted | 7 | 4 | teleport, HZ name, worldmap, guard town, mapdefine |
| 64007 | Researcher Quarters | deleted | 0 | 0 | none |
| 13032 | Dulari's Camp (target) | present v92 | 0 | 0 | none |
| 13033 | Southern Checkpoint (target) | present v92 | 0 | 0 | none |
| 13034 | Tainted Gorge Outpost (target) | present v92 | 0 | 0 | none |

Survivor baseline (8 surviving IoD-13 sections): each carries its definition pair
plus exactly **1** dependency edge (a single MapDefineData minimap label), except
13001 (the continent/hunting-zone-13 name "Island of Dawn") which carries 6 edges
(worldmap, guard, questgroup HZ name, a QuestDialog `@Rgn` token, mapdefine).

**Conclusion on affected content:** 11 of the 12 deleted sections are pure
map-geography records with zero or one (UI-only) inbound edge. No quests, quest
dialogs, quest rewards, NPC spawns, or teleports depend on them. `64001` is the
sole exception and its edges are hunting-zone/town-level, not sub-section-level.

## 3. Per-section classification

| nameId | Content hanging off it | Reference key | Remap-safe? |
|---|---|---|---|
| 13002, 13005, 13015, 13018, 13022, 64007 | strings only (name + geometry) | nameId | trivial (name+geometry only) |
| 13008, 13017, 13020, 13027 | strings + geometry; renum targets already exist for 3 | nameId | table-remappable |
| 13013 | strings + 1 client minimap label | nameId (stringId) | table-remappable; id reused in v92 as "Airship Approach" |
| 64001 | teleport dest + HZ-64 display name + worldmap section + guard town + minimap | region-string id (`@rgn:64001`) | remappable by string-id table, but see geometry note |

## 4. Feasibility of Option B (remap table)

**A remap table is highly mechanical.** Because content references sections by a
single integer (the region-string id) and quests bypass sections entirely, a
remap is a flat `old_nameId -> new_nameId` substitution across five well-defined
files: `StrSheet_Region`, `Area/AreaData`, `TeleportData`, `QuestGroupList`,
`NewWorldMapData`, `GuardData`, `MapDefineData`. The total edge count to rewrite
outside the definitions is **8 in the client and 4 in v31** across all 12
sections combined; 11 of 12 sections need only their definition pair touched.

v92 already demonstrates the remap pattern: 13017/13020/13027 were renumbered to
13032/13033/13034 keeping their names, and 13013/13015 were freed and reused for
new places ("Airship Approach", "Abandoned Camp").

**What a remap cannot recover: geometry.** A remap only preserves *names and
references*. The deleted sections' gameplay value is their **Fence polygon
geometry** (the physical camp/checkpoint footprints and their pk/rest/vendor/
huntingZone flags). If the intent is to bring back the *places* (safe camps,
checkpoints, the Tower Base town with its teleport and vendor), the polygons must
be restored from the v17 `Area-00004.xml` into the v92 `AreaData_13_ATW_Death_P`
geometry; a nameId remap alone yields a label with no on-map region. For 64001
specifically, its teleport destination coordinates and worldMapSection live in
`TeleportData`/`NewWorldMapData` and would need the section polygon to exist for
the teleport to land inside a valid region.

**Net:** remap is nearly free mechanically (12 label edges) but only meaningful if
paired with geometry restoration; the reference graph itself imposes almost no
constraint because the deleted sections are near-leaf nodes.
