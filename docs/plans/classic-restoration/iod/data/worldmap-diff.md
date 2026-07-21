# IoD Worldmap Diff (v31 vs clean v92)

Phase 3 artifact. Family: `WorldMap/NewWorldMapData.xml` (server). Machine data: `worldmap-diff.json`.

Sources (read-only):
- v31: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet\WorldMap\NewWorldMapData.xml`
- v92: `D:\dev\mmogate\tera92\server\Datasheet\WorldMap\NewWorldMapData.xml`

IoD worldmap content lives in two hierarchy locations, both diffed here:
1. **World 1 / Guard 2** (Valkyon Protectorate, nameId 202) - the overworld map sections.
2. **World 9999 / Guard 2** ("여명의 정원" = Island of Dawn) - instance sections (dungeon 9036,
   Tainted Gorge entrance).

Sections keyed by section `id`. Verdicts as in sections-diff.

## Verdict counts

| Verdict | Count |
|---|---|
| MATCH | 2 |
| PORT | 2 |
| DECISION | 2 |

## Rows

| sec id | nameId | type | v31 mapId | v92 mapId | Verdict | Note |
|---|---|---|---|---|---|---|
| 6 | 64001 | town | WMap_ATW_Vill_01 | WMap_ATW_Vill_01 **(COMMENTED)** | PORT | Tower Base town; live in v31, commented-out in v92. Re-enable (matches AreaData 64001 re-enable). |
| 7 | 13001 | (field) | WMap_ATW_Field_01 | WMap_ATW_Death_Field | PORT | IoD field map reskinned "Death" in v92. Revert mapId to WMap_ATW_Field_01 (v31 wins). |
| 8 | 13031 | town | - | WMap_ATW_Death_Vill | DECISION | v92-only North Dock town. Keep/remove with the 13031 section + teleport-network cluster (sections-diff). |
| 9 | 13001 | (field) | - | WMap_ATW_Death_Empty | DECISION | v92-only duplicate 13001 section, `visibleInMap="false"`. Recommend REMOVE with the Death-reskin revert (cosmetic, hidden). |
| 9036 | 9036001 | (instance) | WMap_SJ_03 | WMap_SJ_03 | MATCH | Karascha's Lair summon marker, identical. |
| 9037 | 13009 | (instance) | WMap_ATW_Empty_02 | WMap_ATW_Empty_02 | MATCH | Tainted Gorge entrance marker, identical. |

## Verified priors from the brief

- **Tower Base town (World 1 / Guard 2, nameId 64001, MapDefine WMap_ATW_Vill_01):** CONFIRMED
  commented-out server-side in v92 (`<!--<Section id="6" type="town" ... nameId="64001" ...`), and
  LIVE in v31. Verdict PORT (re-enable).
- **Section 9053 Kezzel's Gorge:** OUT OF IOD SCOPE. It is a Giant's Forest dungeon section
  (`WMap_EX_HEC_B_SD`, nameId 9053001), under World 9999 / Guard 14 - not continent 13/9036. State
  now: v31 has it **commented-out** (dormant); clean v92 has a **well-formed live row**
  (`id="9053" desc="Kezzel's Gorge (5-Person)" mapId="WMap_DG_EX_HEC_B_SD_02_P" nameId="9053001"`).
  The bad hand-edited server row referenced in the brief is gone after today's revert; the current
  clean-v92 row is legitimate. No IoD action.

## MapDefine / mapId asset readiness (v92 client)

Every mapId referenced by a v31 IoD row still exists in the v92 client DC (checked
`NewWorldMapData` + `MapDefineData` under `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR\`):

| mapId | v92 client files referencing it | Restore relevance |
|---|---|---|
| WMap_ATW_Vill_01 | 2 (MapDefineData-00052, -00054) + ResourceSummary-00000 | **Tower Base town re-enable is asset-safe** |
| WMap_ATW_Field_01 | 3 | field-map mapId revert target exists |
| WMap_ATW_Empty_02 | 2 | Tainted Gorge entrance marker |
| WMap_SJ_03 | 2 | Karascha's Lair marker |
| WMap_ATW_Death_Field / Death_Vill / Death_Empty | 3-5 each | v92-only maps (removal only) |

`WMap_ATW_Vill_01` appears in `ResourceSummary-00000.xml` (the packaged-asset manifest), confirming
the underlying map asset ships in the v92 client. Re-enabling the 64001 town section will render.

## Sync note

`NewWorldMapData` syncs monolithic **merge-by-id** (keys `id`, `nameId`; sync-config lines 386-395),
so re-enabling the server-side 64001 town adds it as a server-only record while preserving the
client's curated markers. Removing a v92-only section server-side does NOT remove client-only minimap
labels - those live in `MapDefineData`, which has no sync coverage (see readiness note).
