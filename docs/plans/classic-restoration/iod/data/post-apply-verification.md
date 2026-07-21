# IoD Patch 001 Post-Apply Reconciliation (Phase 5 Gate)

Verified 2026-07-20 against raw XML. Sources:
server tree `D:\dev\mmogate\tera92\server\Datasheet`, v31 `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet`,
client `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR`. Read-only; no files modified.

## Status: ALL PASS (after spec 04 fix, then two user rulings)

First pass (12-spec batch): 7 PASS, 1 FAIL (check 5 rewards, class-scoped reward rows dropped).
Spec 04 was fixed (generator now emits one Item row per templateId with a merged semicolon-joined
class list), the server tree was reverted, and the full batch re-applied (12/12, 1568 ops, 0 warnings).
Re-run of check 5 (full) plus spot-re-run of checks 1, 6, 7 confirmed the fix landed with no drift.

Third pass (two user rulings, 13-spec batch, 1573 ops, server tree reverted first):
(1) shared stores now PORT to v31 game-wide (spec 03 grew to 9 ops: BuyLists
1001/1002/16064/1601/1602/2501/2502/2505 + Ashley binding); (2) new spec 12 removes the T-cat/Tikat
merchant via a single territories.delete of 64/6400001/6400024 (cascading his spawn 6400140), and
spec 07 dropped his dialog op. Targeted re-run below (amended spawn + shops expectations, villager
dialogs, no-drift spot). All items PASS. All eight gate checks remain PASS.

## Result table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Spawn no-drift | PASS | All 6 TerritoryData zones (13/64/213/313/364/436) canonically (order-insensitive) identical to v31; 470 territories total (403/15/24/6/4/18). Git porcelain shows no TerritoryData file in the modified set. |
| 2 | Sections | PASS | 7 re-adds (13002/13005/13008/13013/13015/13018/13022) live with v31 fence geometry (numeric match). 3 realigns at v31 values: 13004 addMaxZ=1000, 13007 priority=0, 13030 priority=1 plus 13-vertex ring. Tower Base 64001 and 64007 live (uncommented). 13035 absent. KEEPs 13031/13032/13033/13034 present. Classic camps 13017/13020/13027 correctly absent. |
| 3 | Region strings | PASS | 13035 "Ruined Temple" removed; 13031-13034 intact (North Dock / Dulari's Camp / Southern Checkpoint / Tainted Gorge Outpost). Classic names match v31, including 13013 "Airship Approach" and 13015 "Abandoned Camp". |
| 4 | Worldmap NewWorldMapData (server) | PASS | Semantic diff HEAD vs working tree: only sec6 added and sec7 mapId changed. Sec6 Tower Base town (nameId 64001) live with the v31 6-marker roster (99,32/11/6/9/7/10). Sec7 mapId reverted WMap_ATW_Death_Field -> WMap_ATW_Field_01, 5 markers retained. Sec8 (North Dock 13031) UNCHANGED. Sec9 present, visibleInMap=false (deferred delete). |
| 5 | Rewards | PASS (re-run) | All 65 real quests populated (0 unpopulated). Deep-compare over all 65 real quests: 0 v31 (templateId,class) reward pairs missing. The 11 previously-broken quests (1303/1305/1310/1315/1317/1322/1325/1326/1330/1331/1347) now retain every v31 core-class row with its classes intact and carry the appended fighter/glaiver/assassin classes on the shared templateId. Quest 1310 has its engineer 15019 row. New schema: one Item per templateId with a semicolon-joined class list (e.g. 1322 17703 class="lancer;berserker;engineer;fighter"). First-pass FAIL (116 dropped rows) is resolved. |
| 6 | Shops | PASS | BuyList 1001 (10 items), 1002 (8 items), 16064 ([98032,133,160]) all set-match v31. Only lists 1001/1002/16064 have changed Item lines; 1601/1602 untouched. VillagerMenu semantic diff: the sole change is a new Villager 313,1002 bound to Menu type Merchant id 250; no existing menu altered. No BuyList outside the three changed, so store 250 content unchanged. |
| 7 | Quest files | PASS | Only 059901.quest modified (Stepstone sentinel disable: prerequisite quest 99,99 added, plus whitespace reserialization). 001384.quest clean (KEEP). No 13xx quest file modified. |
| 8 | Client sync landed | PASS | Client Area-00013 section nameId set exactly matches the server (all 7 re-adds + 64001/64007 + KEEPs 13031-34, no 13035). Client StrSheet_Region dropped 13035 only. Client NewWorldMapData gained sec6 Tower Base town (6 markers); sec7/8/9 marker counts unchanged (5/9/5) with zero client-only markers dropped by the merge-by-id. |

## Ruling-driven re-run (third pass)

Targeted re-run after the two user rulings and the 13-spec replay. All items PASS.

| Item | Result | Evidence |
|------|--------|----------|
| 1. Spawn (amended) | PASS | Only TerritoryData_64 is in the modified set. server_64 is canonically equal to v31_64 with exactly Territory 6400024 removed and nothing else. The removed territory's containing TerritoryList (inside TerritoryGroup 6400001) retains its other 9 territories (6400001/2/3/8/12/13/21/22/23). The Tikat merchant spawn cascaded out: v31 Territory 6400024 held Npc instanceId 6400140 (Tcat, npcTemplateId 9000), now absent server-side. Zones 13/213/313/364/436 remain canon-identical to v31. No other TerritoryData drift. |
| 2. Shops (amended) | PASS | Semantic diff vs HEAD: exactly the 8 spec-03 lists changed (1001/1002/16064/1601/1602/2501/2502/2505), no others. Content vs v31: 1001(10)/1002(8)/16064(3)/1602(16)/2501(8)/2505(21) match v31 exactly; 1601 matches v31 minus the documented skips 213307+219000 (srv 10 = v31 12 - 2, neither skipped id present); 2502 carries the 33 classic charms and matches v31. |
| 3. Villager dialogs | PASS | 00640000009000.condition (T-cat) is NOT in the modified set: it is tracked at HEAD, unchanged on disk, so the dropped T-cat op left it untouched. 71 villager .condition files modified (was 72 on the first pass; the T-cat file dropped out), consistent with the reduced 91-op spec 07. |
| 4. No-drift spot | PASS | Rewards: quest 1310 retains all 17 v31 (templateId,class) rows plus new-class fighter/glaiver/assassin (24 total), engineer 15019 present. Quest files: only 059901.quest modified. |

## Check 5 re-run resolution

After the spec 04 generator fix and full re-apply, the deep-compare passes:

- 65 real quests populated; 0 unpopulated.
- 0 v31 (templateId,class) pairs missing across all 65 real quests.
- 11 previously-broken quests all retain every v31 row and carry the new classes:

| Quest | v31 pairs | srv pairs | v31 survives | new classes present |
|-------|-----------|-----------|--------------|---------------------|
| 1303 | 18 | 24 | yes | fighter/glaiver/assassin |
| 1305 | 36 | 48 | yes | fighter/glaiver/assassin |
| 1310 | 17 | 24 | yes | fighter/glaiver/assassin (engineer 15019 present) |
| 1315 | 18 | 24 | yes | fighter/glaiver/assassin |
| 1317 | 9 | 12 | yes | fighter/glaiver/assassin |
| 1322 | 9 | 12 | yes | fighter/glaiver/assassin |
| 1325 | 9 | 12 | yes | fighter/glaiver/assassin |
| 1326 | 9 | 12 | yes | fighter/glaiver/assassin |
| 1330 | 9 | 12 | yes | fighter/glaiver/assassin |
| 1331 | 9 | 12 | yes | fighter/glaiver/assassin |
| 1347 | 9 | 12 | yes | fighter/glaiver/assassin |

The fixed schema emits one Item per templateId with a semicolon-joined class list, so the shared-id
collision that dropped rows on the first pass no longer occurs (e.g. quest 1322 now has
17703 class="lancer;berserker;engineer;fighter"). Spot-re-run of checks 1, 6, 7 after the
revert+replay: no drift (470 territories canon-identical to v31; only BuyList 1001/1002/16064 changed;
only 059901.quest modified, 001384.quest clean).

## Check 5 history (first-pass FAIL, resolved)

Two-part check. Population count passed; deep-compare failed on the first pass.

### Defect: v31 core-class reward rows dropped (data loss)

QuestCompensationData_13: 11 class-scoped quests lost their v31 core-class Item rows,
replaced by only the appended new-class (fighter/glaiver/assassin) rows. 116 rows dropped total.

| Quest | Enabled? | v31 core rows dropped | new-class rows added |
|-------|----------|-----------------------|----------------------|
| 1303 | ENABLED | 9 (all 8 core + engineer) | 6 |
| 1305 | ENABLED | 27 (all core armor tiers + engineer) | 12 |
| 1310 | disabled (sentinel) | 8 core armor | 6 |
| 1315 | ENABLED | 9 | 6 |
| 1317 | ENABLED | 9 | 3 |
| 1322 | disabled | 9 | 3 |
| 1325 | disabled | 9 | 3 |
| 1326 | disabled | 9 | 3 |
| 1330 | disabled | 9 | 3 |
| 1331 | ENABLED | 9 | 3 |
| 1347 | disabled | 9 | 3 |

Enabled status is heuristic (presence of a 99,99 sentinel prerequisite in the quest file).

Live impact: 5 of the 11 quests are ENABLED (1303, 1305, 1315, 1317, 1331). On those, the 9 core
classes (warrior/lancer/slayer/berserker/sorcerer/archer/priest/elementalist/engineer) lose their
v31 armor reward rows and receive nothing in that itemBag slot; only fighter/glaiver/assassin get rewards.

Two sub-findings that directly contradict the documented rulings:
- Divergence-log entry 21 requires quest 1310 to carry a restored 15019 engineer armor row. Server 1310
  has NO engineer armor row at all (weapon engineer row 55007 survives; armor engineer row is gone).
- Divergence-log entry 20 says new-class rows are APPENDED, engineer rows kept. Server state is a
  REPLACE, not an append.

### Mechanism

The break correlates exactly with shared templateIds. Quests done correctly (1304, 1316, 1319, 1323)
give each class a UNIQUE templateId; the new classes get their own new unique ids, so no collision.
The 11 broken quests reuse one templateId across several classes (e.g. v31 17703 -> lancer+berserker+engineer,
15019 -> lancer+berserker+engineer). The new-class analog reuses that same templateId (17703 -> fighter,
15019 -> fighter). The reward write appears keyed on templateId only, so all rows sharing a templateId
collapsed to the single new-class row, dropping the core-class rows. This is a keying / list-replace
defect in the reward spec (spec 04) or its DSL operation, not a formatting artifact.
