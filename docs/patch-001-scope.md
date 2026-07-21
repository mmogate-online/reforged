# Patch 001 (Baseline) Zone Scope

Patch 001 is the classic-restoration baseline: Island of Dawn restored from old client v17.11 (primary source) with v31 gap-fill. This document defines exactly which zones that covers.

Island of Dawn is one physical map (continent 13, area `ATW_Death_P` in v92) carrying five layered hunting zones. Research, audits, and restoration specs must enumerate ALL five layers, not just the combat zone. Each layer has its own per-zone file families (NpcData, TerritoryData, compensation tables, etc.).

## Continent 13 (Island of Dawn)

| HZ | Layer | Content |
|----|-------|---------|
| 13 | combat | field mobs, bosses, combat content |
| 64 | hub | Tower Base camp (merchants, camp NPCs) |
| 213 | social | main villager population |
| 313 | politics | politics-layer NPCs |
| 364 | hub (politics layer) | camp politics NPCs |

## Associated Dungeon

| Zone ID | Name | Continent |
|---------|------|-----------|
| 436 | Karascha's Lair | 9036 (separate dungeon continent; scope explicitly, do not fold into continent 13) |
| 437 | Tainted Gorge Bridge | 9037 (Sorcha's Reckless Challenge solo instance, quest 1346; reclaimed for classic by patch 001 spec 19, displacing the non-classic level-65 line 21301-21307) |

## Out of Scope (decided 2026-07-18)

- HZ 415 / continent 9015 (Island of Dawn Coast, tutorial) and HZ 416 / continent 9016 (Island of Dawn Prologue, tutorial dungeon): excluded from the baseline.
- Stepstone Isle (continents 5/9827/9828/9829, v92-only starter isle): not restored; its quests are DISABLED by a baseline spec (classic-authentic, the zone did not exist in the classic era).

## Porting Notes (v17.11 to v92)

The zone/continent skeleton is identical across eras, but continent 13's section layout was rebuilt (`ATW_P` 20 sections to `ATW_Death_P` 13 sections): 12 sections deleted, 3 renumbered (13017 to 13032, 13020 to 13033, 13027 to 13034), and region string ids 13013/13015 REUSED for different places in v92. All v17 content references must be translated through the section mapping table (Phase 1 artifact) before spec authoring. See `docs/plans/iod-alpha-content-loop/`.

## Patch 002 Scope

The Reforged customization zones (hunting zones, hub cities, dungeons) formerly listed here are now defined in `patch-002-scope.md`.
