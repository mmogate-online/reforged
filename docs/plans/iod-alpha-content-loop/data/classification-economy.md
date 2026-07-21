# Classification: Economy (axes 5-8: shops, loot, gathering, dialogs, furniture)

Combined verdict counts: DECISION=2, GAPFILL=143, MATCH=62, REMOVE=1, RESTORE=5

## Shops (axis 5)

Target: 7 real v31 stores for v17-registry NPCs, diffed per store against the v92 baseline BuyMenuList/BuyList; 2 out-of-registry stores held as DECISION extras

Registry stores: 7, out-of-registry extras: 2, service-only NPCs: 29

| store | store_id | npc | menu | n_items | verdict | note |
|-------|----------|-----|------|---------|---------|------|
| 64/1004 | 100 | Viator | Merchant | 18 | RESTORE | list 1001: v31 10 items vs v92 20; list 1002: v31 8 ite |
| 64/1005 | 16064 | Rutgar | Merchant | 31 | RESTORE | list 1601: v31 12 items vs v92 7; list 1602: v31 16 ite |
| 64/1052 | 211 | Ailesa | Merchant | 18 | RESTORE | list 2111: v31 8 items vs v92 10; list 2112: v31 10 ite |
| 64/1053 | 210 | Mahadam | Merchant | 18 | MATCH | v92 BuyMenuList/BuyList already equals v31 store 210 |
| 64/9000 | 315 | T-cat Exchanger | MedalStore | 37 | GAPFILL | store menu 315 absent from v92 BuyMenuList; wire 37 v31 |
| 313/1002 | 250 | Ashley | Merchant | 62 | RESTORE | tab set v31=['2501', '2502', '2505'] vs v92=['2501', '2 |
| 364/1001 | 250 | Ainah | Merchant | 62 | RESTORE | tab set v31=['2501', '2502', '2505'] vs v92=['2501', '2 |
| 213/1054 | 16090 | Sandom | Merchant | 29 | DECISION | Sandom (merchant, out of v17 registry): real store but  |
| 64/8000 | 331 | Ellonia | MedalStore | 15 | DECISION | Ellonia medal store (out of v17 registry): real store b |

## Loot (axis 6)

Target: v31 zone-13 loot filtered to v17 roster (50 mobs)
baseline CCompensation templates: 50

| templateId | name | verdict | note |
|-----------|------|---------|------|
| 1 | Pigling | MATCH | baseline CCompensation has loot for 1 (10 bags); v31 po |
| 2 | Sporewalker | MATCH | baseline CCompensation has loot for 2 (10 bags); v31 po |
| 3 | Ponderous Sporewalke | MATCH | baseline CCompensation has loot for 3 (10 bags); v31 po |
| 4 | Dwarf Orcan | MATCH | baseline CCompensation has loot for 4 (10 bags); v31 po |
| 5 | Orcan Raider | MATCH | baseline CCompensation has loot for 5 (10 bags); v31 po |
| 6 | Kariagon | MATCH | baseline CCompensation has loot for 6 (10 bags); v31 po |
| 7 | Disc Reaper | MATCH | baseline CCompensation has loot for 7 (10 bags); v31 po |
| 8 | Runekeeper | MATCH | baseline CCompensation has loot for 8 (10 bags); v31 po |
| 9 | Destroyer | MATCH | baseline CCompensation has loot for 9 (10 bags); v31 po |
| 101 |  | MATCH | baseline CCompensation has loot for 101 (7 bags); v31 p |
| 102 | Docile Terron | MATCH | baseline CCompensation has loot for 102 (7 bags); v31 p |
| 111 | Gentle Pigling | MATCH | baseline CCompensation has loot for 111 (10 bags); v31  |
| 301 | Rockcrawler Tumbler | MATCH | baseline CCompensation has loot for 301 (7 bags); v31 p |
| 302 | Terron Ringleader | MATCH | baseline CCompensation has loot for 302 (10 bags); v31  |
| 303 | Terron Thief | MATCH | baseline CCompensation has loot for 303 (10 bags); v31  |
| 304 | Sickly Noruk | MATCH | baseline CCompensation has loot for 304 (10 bags); v31  |
| 555 | Scion Scout | MATCH | baseline CCompensation has loot for 555 (10 bags); v31  |
| 556 | Scion Scout | MATCH | baseline CCompensation has loot for 556 (10 bags); v31  |
| 557 | Scion Scout | MATCH | baseline CCompensation has loot for 557 (10 bags); v31  |
| 558 | Scion Scout | MATCH | baseline CCompensation has loot for 558 (10 bags); v31  |
| 601 | Dark Marauder | MATCH | baseline CCompensation has loot for 601 (10 bags); v31  |
| 888 | Training Dummy | MATCH | baseline CCompensation has loot for 888 (10 bags); v31  |
| 901 | Orcan Guardian | MATCH | baseline CCompensation has loot for 901 (10 bags); v31  |
| 902 | Dwarf Guardian | MATCH | baseline CCompensation has loot for 902 (10 bags); v31  |
| 999 |  | MATCH | baseline CCompensation has loot for 999 (10 bags); v31  |
| 1001 | Vekas | MATCH | baseline CCompensation has loot for 1001 (10 bags); v31 |
| 1002 | Acharak | MATCH | baseline CCompensation has loot for 1002 (10 bags); v31 |
| 1003 | Acharak's Soldier | MATCH | baseline CCompensation has loot for 1003 (10 bags); v31 |
| 1004 | Kugai | MATCH | baseline CCompensation has loot for 1004 (10 bags); v31 |
| 1011 | Terron Saboteur | MATCH | baseline CCompensation has loot for 1011 (7 bags); v31  |
| 300541 | Rockcrawler | MATCH | baseline CCompensation has loot for 300541 (10 bags); v |
| 300542 | Rockcrawler Cleaver | MATCH | baseline CCompensation has loot for 300542 (10 bags); v |
| 300910 | Prowling Cromos | MATCH | baseline CCompensation has loot for 300910 (10 bags); v |
| 300911 | Cromos | MATCH | baseline CCompensation has loot for 300911 (10 bags); v |
| 300920 | Shaggy Noruk | MATCH | baseline CCompensation has loot for 300920 (10 bags); v |
| 300921 | Noruk | MATCH | baseline CCompensation has loot for 300921 (10 bags); v |
| 300930 | Elder Ghilliedhu | MATCH | baseline CCompensation has loot for 300930 (10 bags); v |
| 300931 | Ghilliedhu | MATCH | baseline CCompensation has loot for 300931 (10 bags); v |
| 300932 | Horned Ghilliedhu | MATCH | baseline CCompensation has loot for 300932 (10 bags); v |
| 300933 | Hardened Ghilliedhu | MATCH | baseline CCompensation has loot for 300933 (10 bags); v |
| 300941 | Terron | MATCH | baseline CCompensation has loot for 300941 (10 bags); v |
| 300942 | Terron Thrall | MATCH | baseline CCompensation has loot for 300942 (10 bags); v |
| 300943 | Terron Saboteur | MATCH | baseline CCompensation has loot for 300943 (10 bags); v |
| 300944 | Terron Chief | MATCH | baseline CCompensation has loot for 300944 (10 bags); v |
| 300945 | Terron Lama | MATCH | baseline CCompensation has loot for 300945 (10 bags); v |
| 300951 | Dark Raider | MATCH | baseline CCompensation has loot for 300951 (10 bags); v |
| 300960 | Devoted Ebon Imp | MATCH | baseline CCompensation has loot for 300960 (10 bags); v |
| 301191 | Stonebeak Raider | MATCH | baseline CCompensation has loot for 301191 (10 bags); v |
| 301193 | Stonebeak Brigand | MATCH | baseline CCompensation has loot for 301193 (10 bags); v |
| 301194 | Stonebeak Highcrest | MATCH | baseline CCompensation has loot for 301194 (10 bags); v |

## Gathering (axis 7)

Target: v31 gathering placement landed in LIVE CollectionTerritory_13_ATW_Death_P.xml
> Account for patch-000 gathering fixes in the LIVE file; do not remove them blindly. Any LIVE spawn count exceeding the v31 target may be a patch-000 fix -> flag, don't overwrite.

| territory | collection | typeId | verdict | target_spawns | live_spawns | note |
|-----------|-----------|--------|---------|---------------|-------------|------|
| 1 | 1 | 1 | MATCH | 46 | 46 | LIVE _ATW_Death_P already has 46 spawns for ( |
| 1 | 2 | 101 | MATCH | 66 | 66 | LIVE _ATW_Death_P already has 66 spawns for ( |
| 1 | 3 | 301 | MATCH | 45 | 45 | LIVE _ATW_Death_P already has 45 spawns for ( |
| 5 | 4 | 409 | MATCH | 20 | 20 | LIVE _ATW_Death_P already has 20 spawns for ( |
| 5 | 5 | 410 | MATCH | 24 | 24 | LIVE _ATW_Death_P already has 24 spawns for ( |
| 5 | 6 | 411 | MATCH | 30 | 30 | LIVE _ATW_Death_P already has 30 spawns for ( |
| 5 | 7 | 492 | MATCH | 1 | 1 | LIVE _ATW_Death_P already has 1 spawns for (5 |
| 5 | 8 | 496 | MATCH | 5 | 5 | LIVE _ATW_Death_P already has 5 spawns for (5 |
| * | * | None | REMOVE | None | None | inert baseline file CollectionTerritory_13_AT |

## Dialogs (axis 8a)

Target: v31 .condition dialogs for rostered villagers; coverage gaps = GAPFILL-missing
coverage gaps (GAPFILL-missing): 16

| hz | with_dialog | missing | verdict | note |
|----|-------------|---------|---------|------|
| 64 | 45 | 5 | GAPFILL | restore v31 .condition dialogs for 45 rostere |
| 213 | 78 | 9 | GAPFILL | restore v31 .condition dialogs for 78 rostere |
| 313 | 8 | 0 | GAPFILL | restore v31 .condition dialogs for 8 rostered |
| 364 | 8 | 0 | GAPFILL | restore v31 .condition dialogs for 8 rostered |
| 436 | 3 | 2 | GAPFILL | restore v31 .condition dialogs for 3 rostered |

## Furniture (axis 8b)

Target: 3 zone-13 campfires (v31 BonfireData)
baseline bonfires: 3, v31: 3

| id | desc | verdict | note |
|----|------|---------|------|
| 4 | 검은 틈 수비대 캠프 | MATCH | campfire at 53308.2422,-69770.0625,-5579.3008 alre |
| 4 | 북부 경계 초소 | MATCH | campfire at 87055.3359,-84622.1406,-4528.3013 alre |
| 4 | 쿠벨 야영지 | MATCH | campfire at 55418.7578,-82242.0156,-4127.3003 alre |
