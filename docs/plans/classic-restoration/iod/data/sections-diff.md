# IoD AreaData Section Diff (v31 vs clean v92)

Phase 3 artifact. Scope: continent 13 (`AreaData_13_ATW_P` v31 / `AreaData_13_ATW_Death_P` v92)
and dungeon continent 9036 (`AreaData_9036_ATW_A_SD_P` both). Machine data: `sections-diff.json`.

Sources (read-only):
- v31 server: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet\AreaData\`
- v92 server (clean baseline, reverted today): `D:\dev\mmogate\tera92\server\Datasheet\AreaData\`

Method: live sections parsed with ElementTree (comments stripped); commented-out `<Section>` blocks
parsed separately by regex and merged. Fence rings compared vertex-exact (rounded to 0.01u). Verdicts:
MATCH (identical live both sides), PORT (v31 wins: restore or re-enable), KEEP (dormant both), REMOVE
(v92-only, drop), DECISION (v92-only live, disposition required).

## Continent 13 - verdict counts

| Verdict | Count | nameIds |
|---|---|---|
| MATCH | 5 | 13001, 13003, 13006, 13024, 13028 |
| PORT | 15 | 13002, 13004, 13005, 13007, 13008, 13013, 13015, 13017, 13018, 13020, 13022, 13027, 13030, 64001, 64007 |
| DECISION | 5 | 13031, 13032, 13033, 13034, 13035 |

Total 25 sections. Dungeon 9036: 1 section, MATCH (9036001, id 1, 12 verts, identical).

## PORT rows detail

Three classes of PORT:

**A. Absent in v92, live in v31 (re-add) - 8 sections:** 13002 Pegasus Platform (id 6, 4v),
13005 Northern Checkpoint (id 9, 6v), 13008 Orcan Bivouac (id 56, 4v), 13013 Airship Approach
(id 47, 5v), 13015 Abandoned Camp (id 36, 8v), 13018 Northern Overwatch (id 43, 9v),
13022 Tainted Gorge Garrison (id 34, 6v). Also 13017/13020/13027 (see class C).

> Correction to prior (v17-era) art: in v31 the section with nameId **13013 is already
> "Airship Approach"** and **13015 is already "Abandoned Camp"** (see region-strings-diff). The
> retired v17 plan's "Terron Run -> new id 13036" and "revert 13015 to Leander's Outpost" do NOT
> hold under v31-primary. These sections restore under their existing, already-matching nameIds;
> no new region string and no 13036 allocation are needed.

**B. Live both, diverged attrs/fence (v31 wins) - 3 sections:**

| nameId | Name | Divergence | Disposition |
|---|---|---|---|
| 13004 | Tainted Gorge | `addMaxZ` 1000.0 (v31) vs 4096.0 (v92); fence exact | PORT attr |
| 13007 | Mathar Spire | `priority` 0 (v31) vs 5 (v92); fence exact | PORT attr |
| 13030 | Timeless Woods | `priority` 1 vs 2; **fence 13 verts (v31) vs 12 (v92)** | PORT ring+attr |

13030 is the Timeless Woods boundary redraw the v92 rework applied; the v31 13-vertex ring reverts
with the rest per doctrine (v31 wins on divergence).

**C. Commented-out in v92, live in v31 (re-enable) + renumber pairs:**
- **64001 Tower Base** (id 30, 12v) and **64007 Researcher Quarters** (id 40, 5v, nested child):
  COMMENTED-OUT in v92, live in v31, fences vertex-exact between eras. Straight re-enable (the v92
  comment block is a ready template; ids 30/40 match v31). This heals the dangling GuardData town,
  QuestGroupList HZ-64 name, and TeleportData `@rgn:64001` refs that are still live in v92.
- **13017 Dulari's Camp (id 42, 6v), 13020 Southern Checkpoint (id 45, 6v), 13027 Tainted Gorge
  Outpost (id 51, 8v):** live in v31 under these classic nameIds. v92 renumbered the same three
  camps to 13032/13033/13034 (names confirmed identical via region strings). See DECISION rows.

## DECISION rows (v92-only live sections)

All five have no v31 counterpart. They split into two clusters:

| nameId | v92 id / verts | v92 name | Recommended | Why |
|---|---|---|---|---|
| 13031 | 57 / 8v | North Dock | KEEP (flag) | v92-only camp-teleport hub; live `TeleportMenuList`/`TeleportList` node (menuId 13031, campId referenced by 13032/13033/13034) and world-map town. Removal breaks the live teleport graph. |
| 13032 | 58 / 9v | Dulari's Camp | DECISION | v92 renumber of v31 13017 (same name). Keeping it plus PORTing 13017 yields two overlapping same-named camps; removing it breaks TeleportMenuList campId 13032. |
| 13033 | 59 / 8v | Southern Checkpoint | DECISION | v92 renumber of v31 13020; same conflict as 13032 (campId 13033). |
| 13034 | 60 / 8v | Tainted Gorge Outpost | DECISION | v92 renumber of v31 13027; same conflict (campId 13034). |
| 13035 | 61 / 16v | Ruined Temple | REMOVE | v92-only; only cosmetic client minimap labels (MapDefineData-00048/-00049) dangle. No teleport, worldmap-town, guard, quest, or spawn dependency. |

**Cluster note for team lead:** 13031/13032/13033/13034 plus their world-map town (13031) and the
`TeleportMenuList`/`TeleportList` camp network are a single v92-only subsystem. v31 has **no IoD camp
teleport network at all** (v31 `TeleportMenuList` carries none of these camp menus). The clean choice
is a unit decision:
- **Option KEEP-network:** keep 13031-13034 (+ teleport network) as engine-dependency KEEPs; do
  NOT re-add classic 13017/13020/13027 (avoid duplicate camps). Classic camp *names* already live
  under the renumbered ids.
- **Option v31-pure:** PORT 13017/13020/13027 under classic nameIds and REMOVE 13031-13034, which
  requires reverting the whole camp teleport network (out of this diff's family scope).

This diff reports both classic sections (13017/13020/13027 as PORT) and their v92 twins
(13032/13033/13034 as DECISION); resolving the overlap is a cross-family (teleport) call.

## Root `<Area>` element divergences (continent 13)

| Attr | v31 | v92 | Note |
|---|---|---|---|
| `recallRevivePos` / `recallScrollPos` | 66600.87,-79855.52,-2993.16 (Tower Base) | 93957,-89037,-4554 (North Dock area) | v92 moved the continent recall point off Tower Base after removing it. Reverts with 64001 restore. |
| `vender` | true | false | v31 continent allows vendors. |

`worldMapWorldId=1`, `worldMapGuardId=2`, `nameId=202` identical both eras. Dungeon 9036 root differs
only on recall pos (cosmetic, dungeon-internal).

## Language note

AreaData `desc` attributes are Korean dev comments in BOTH eras (e.g. `64001 원정대 보급기지`) - not
player-facing and era-consistent, so not a divergence. Player-facing names live in StrSheet_Region
(all English; see region-strings-diff).
