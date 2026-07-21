# v92 Island-of-Dawn Section Reference Sweep

Read-only census of every v92 reference to seven contested IoD map-section region
ids. Two sources swept in full (32k XML, 3.6 GB):

- v92 client DC: `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR`
- v92 server datasheets: `D:\dev\mmogate\tera92\server\Datasheet`

Method: unrestricted ripgrep for each id across both trees (candidate files), then
integer-boundary re-match in Python with mechanism detection and XML-comment
detection. Every hit was classified as a real region reference, an id-space reuse
false positive (Abnormality / Item / Skill / Achievement share the same 5-digit
numbers), or a coordinate false positive. Region references use only these
mechanisms: `@rgn:ID` / `@Rgn:ID$$Name` tokens, `nameId="ID"` (Area/AreaData/
NewWorldMapData Section), `stringId`/`titleStringId="ID"` (Guard/MapDefine),
`<String id="ID">` (StrSheet_Region def), and `campId`/`menuId="ID"`
(TeleportMenuList camp-network node).

Cross-check: an exhaustive `@[Rr]gn:` scan of both entire sources returns exactly
five region-token hits (QuestGroupList@Rgn:64001 client+server, StrSheet_Teleport
@Rgn:13031 client, TeleportData@rgn:64001 client+server). No `region=`/`spawnZone=`/
`zoneId=` attribute anywhere targets these ids. Quest `목표지역` values in IoD
(`13,1300245`, `13,1300253`) are hunting-zone-13 regions (hz*100000+N), not section
nameIds; the "13002" substring in them is coincidental.

## Verdict table

| id | Name (v92) | v92 section state | Real inbound refs beyond definition | Verdict |
|----|-----------|-------------------|-------------------------------------|---------|
| 13031 | North Dock (v92 add) | live geometry (AreaData Section 57) | NewWorldMapData town, StrSheet_Teleport UI string, TeleportMenuList node, 4 minimap labels | HAS DEPENDENTS, not safe to remove |
| 13035 | Ruined Temple (v92 add) | live geometry (AreaData Section 61) | 2 client minimap labels only (UI) | SAFE to remove (only cosmetic labels dangle) |
| 64001 | Tower Base | section + worldmap COMMENTED-OUT | GuardData town, QuestGroupList HZ-64 name, TeleportData dest, minimap, all still live | DANGLING refs present |
| 64007 | Researcher Quarters | section COMMENTED-OUT | none (orphaned StrSheet_Region string only) | no dangling refs (nothing points at it) |
| 13002 | Pegasus Platform | absent (no section at all) | none (orphaned StrSheet_Region string only) | no dangling refs |
| 13013 | Airship Approach (reused) | no section; string + minimap | StrSheet_Region def + 3 client minimap labels | new meaning in use, restoration must migrate |
| 13015 | Abandoned Camp (reused) | no section; string only | StrSheet_Region def only | new meaning barely used, lowest risk |

## Per-id evidence

### 13031, North Dock (v92 addition): HAS DEPENDENTS
Definition pair (expected, not a dependent): Area-00013.xml:118 Section 57 nameId;
AreaData_13_ATW_Death_P.xml:119 Section 57 nameId (LIVE); StrSheet_Region(-00000).xml:317 String def (client+server).
Real inbound dependents:
- NewWorldMapData-00000.xml:79 (client) plus NewWorldMapData.xml:135 (server): `<Section id="8" type="town" nameId="13031" mapId="WMap_ATW_Death_Vill">`. It is a world-map **town**.
- StrSheet_Teleport-00000.xml:243 (client): `<String string="{@Rgn:13031}" stringId="13031"/>`, a teleport UI label.
- TeleportMenuList.xml (server): `<TeleportMenu menuId="13031">` (line 617, its own teleport menu) and `<Destination campId="13031"/>` reachable from menus 13032/13033/13034 (lines 623, 628, 633). This is a live node in the IoD camp teleport network.
- MapDefineData-00048.xml:12, -00049.xml:12, -00050.xml:2 (titleStringId), -00053.xml:4 (client): minimap labels.

Removing 13031 breaks the camp teleport network (three other camps list it as a destination) and orphans the world-map town section.

### 13035, Ruined Temple (v92 addition): SAFE TO REMOVE
Definition pair: Area-00013.xml:159 Section 61 nameId; AreaData_13_ATW_Death_P.xml:160 Section 61 nameId (LIVE, worldMapSectionId="0"); StrSheet_Region(-00000).xml:321 String def (client+server).
Only inbound refs: MapDefineData-00048.xml:6 and -00049.xml:6 (client) minimap spot labels.
No worldmap town, no teleport, no TeleportMenuList node, no guard, no quest, no spawn. Removal only drops two cosmetic minimap labels.

### 64001, Tower Base: DANGLING
- AreaData_13_ATW_Death_P.xml:3 (server): Section id=30 nameId=64001, **COMMENTED-OUT** (geometry absent).
- NewWorldMapData.xml:113 (server): `<Section id="6" type="town" nameId="64001">`, **COMMENTED-OUT**.
- StrSheet_Region(-00000).xml:858 (client+server): String 64001 "Tower Base", LIVE (definition survives).
- GuardData-00000.xml:9 (client) plus GuardData.xml:14 (server): `<Town stringId="64001"/>`, LIVE.
- QuestGroupList-00000.xml:65 (client) plus QuestGroupList.xml:75 (server): HZ id=64 name `{@Rgn:64001$$...}`, LIVE.
- TeleportData-00000.xml:348 (client) plus TeleportData.xml:360 (server): `<Teleport uniqueId="4371002" stringId="@rgn:64001" pos="66615,-79814,-3003"/>`, LIVE.
- MapDefineData-00052.xml:3 (stringId) plus -00054.xml:2 (titleStringId) (client): minimap, LIVE.

The string-based refs (guard town, HZ-64 name, minimap, teleport label) still resolve because StrSheet_Region 64001 exists. What is DANGLING is the section polygon and the world-map town section (both commented out): the teleport keeps its explicit `pos` so it lands the player positionally, but there is no section-64001 region to resolve at that spot, and the HZ-64/guard town operate at hunting-zone level, not sub-section level.

### 64007, Researcher Quarters: NO DANGLING REFS
- AreaData_13_ATW_Death_P.xml:16 (server): Section id=40 nameId=64007, **COMMENTED-OUT**.
- StrSheet_Region(-00000).xml:864 (client+server): String 64007 "Researcher Quarters", LIVE, orphaned.
- No teleport, worldmap, guard, quest, spawn, or minimap reference anywhere.
(BGMList templateId=64007 exists but is BGM-template id-space, an ambient-sound key, not a region reference.)

### 13002, Pegasus Platform: NO DANGLING REFS
- StrSheet_Region(-00000).xml:288 (client+server): String 13002 "Pegasus Platform", LIVE, orphaned. No section present in AreaData at all (not even commented). No inbound region reference of any kind. (`목표지역 13,1300245/1300253` are hz-13 regions, coincidental substring.)

### 13013, Airship Approach (id reused in v92): NEW MEANING IN USE
- StrSheet_Region(-00000).xml:299 (client+server): String 13013 "Airship Approach", new-meaning definition.
- MapDefineData-00048.xml:8, -00049.xml:8, -00052.xml:8 (client): 3 minimap labels using the new meaning.
- No Area/AreaData section, no worldmap, no teleport. A restoration that reverts 13013 to its old meaning must update these 4 records.

### 13015, Abandoned Camp (id reused in v92): NEW MEANING BARELY USED
- StrSheet_Region(-00000).xml:301 (client+server): String 13015 "Abandoned Camp", new-meaning definition; the only live consumer.
- No minimap, section, worldmap, or teleport. Lowest-risk id to repurpose.
(BGMList templateId=13015 "쿠벨 야영지" is BGM-template id-space, not a region reference.)
