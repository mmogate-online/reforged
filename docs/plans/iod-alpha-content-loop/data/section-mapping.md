# IoD Section Mapping Table (v17.11 -> v92)

The authoritative translation layer for the patch 001 structural restoration. Every v17 content reference (spawns, teleports, labels) must be translated through this table. Derived from three verified analyses (2026-07-18): `section-spatial.md` (geometry), `section-census.md` (v17/v31 references), `v92-section-refs.md` (v92 references).

Established facts: island terrain is identical between eras (13001 outer fence vertex-exact); sections are pure data (fence ring + flags + StrSheet_Region string); deleted sections are near-leaf (only Tower Base has inbound wiring); quests never reference section nameIds.

## Dispositions

KEEP = v92 already correct. REMAP = point v17 refs at the v92 id. RESTORE = re-add v17 fence + flags under the original nameId. RESTORE_NEW_ID = re-add v17 geometry under a freshly allocated nameId. REMOVE = delete v92-only section.

| v17 id | Name (v17) | Disposition | v92 id | Notes |
|--------|------------|-------------|--------|-------|
| 13001 | Island of Dawn | KEEP | 13001 | Main section, fence vertex-identical |
| 13003 | Mysterious Ruins | KEEP | 13003 | Survivor; vertex-identical (Phase 1 drift check) |
| 13004 | Tainted Gorge | KEEP | 13004 | Survivor; vertex-identical (Phase 1 drift check) |
| 13006 | Shrine of the Demon God | KEEP | 13006 | Survivor; vertex-identical (Phase 1 drift check) |
| 13007 | Mathar Spire | KEEP | 13007 | Survivor; vertex-identical (Phase 1 drift check) |
| 13024 | Shrine of Yurian | KEEP | 13024 | Survivor; vertex-identical (Phase 1 drift check) |
| 13028 | Arun Heights | KEEP | 13028 | Survivor; vertex-identical (Phase 1 drift check) |
| 13030 | Timeless Woods | RESTORE (v17 ring) | 13030 | DECIDED 2026-07-18: restore the v17 boundary ring. v92 had redrawn it (13 to 12 vertices, southern arc moved ~8400u); the redraw reverts with the rest of the rework |
| 13017 | Dulari's Camp | REMAP | 13032 | v92 fence enlarged 3x, shifted 690u; 17% of old footprint outside new fence: re-clamp edge spawns |
| 13020 | Southern Checkpoint | REMAP | 13033 | v92 fence enlarged 2x, shifted 474u; 31% outside: re-clamp edge spawns |
| 13027 | Tainted Gorge Outpost | REMAP | 13034 | 74u shift, 78% IoU: old coords safe as-is |
| 13005 | Northern Checkpoint | RESTORE | 13005 | Clear ground; original string survives in v92 |
| 13008 | Orcan Bivouac | RESTORE | 13008 | Clear ground; original string survives |
| 13018 | Northern Overwatch | RESTORE | 13018 | Clear ground; original string survives |
| 13022 | Tainted Gorge Garrison | RESTORE | 13022 | Clear ground; original string survives |
| 13002 | Pegasus Platform | RESTORE | 13002 | Ground now under 13035 (being removed); original string survives, zero inbound refs |
| 64001 | Tower Base | RESTORE | 64001 | Section AND worldmap town are commented out in v92 server files (ready templates). v92 still LIVE-references it: GuardData town, QuestGroupList HZ-64 name, TeleportData @rgn:64001 (pos 66615,-79814,-3003), MapDefineData. Restoring the section heals these dangling refs |
| 64007 | Researcher Quarters | RESTORE | 64007 | Nested inside 64001; commented-out template available; orphaned string survives |
| 13015 | Leander's Outpost | RESTORE (revert id) | 13015 | DECIDED 2026-07-18: revert string text to "Leander's Outpost" and restore the section under the original id. "Abandoned Camp" retires (zero inbound refs) |
| 13013 | Terron Run | RESTORE_NEW_ID | 13036 | v92 reuses id as "Airship Approach" (3 live minimap labels): keep it. New id 13036 VERIFIED free in both v92 client and server across all region-referencing families, contiguous next in the 13001..13035 sequence, and conforming to the XXYYY (hz*1000+seq) convention per domain docs |

## v92-only sections

| v92 id | Name | Disposition | Notes |
|--------|------|-------------|-------|
| 13031 | North Dock | KEEP (for now) | Live world-map town + node in the v92 camp teleport network (menus 13032/13033/13034 list campId 13031; own teleport menu; StrSheet_Teleport ref). Removal would break the live teleport graph. Revisit when the classic teleport network (Tower Base landing) is restored in a later phase |
| 13035 | Ruined Temple | REMOVE | Only dependents are 2 client minimap labels (MapDefineData-00048/-00049), which must be cleaned with it. Occupies the ground of 13002/64001/64007 (and 100% of old 13020) |

## Consequences for spec authoring

1. Section restore/remove specs require the pending DSL `areaSections` + `regionStrings` schemas (dsl-requests/2026-07-18-area-section-and-region-string-schemas.md).
2. Restoring 64001 also requires un-commenting the NewWorldMapData town (DSL has a `newWorldMap` section; verify coverage) and cleaning MapDefineData labels for 13035 (MapDefineData has NO DSL schema; assess when reached).
3. Order: section restoration precedes spawn/quest specs (restored spawn areas and the Tower Base teleport landing key on sections).
4. String work: revert 13015 text, add new string for Terron Run's new id; all other restored sections reuse surviving original strings.
