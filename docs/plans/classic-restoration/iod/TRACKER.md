# IoD Restoration Tracker (v31-primary redo)

Pilot zone under `../DOCTRINE.md`. Supersedes the retired `docs/plans/iod-alpha-content-loop/`
pilot (its TRACKER and data artifacts remain readable as reference; its doctrine does not apply).

Last updated: 2026-07-20 (kickoff).

## Mission

Port Island of Dawn's v31 state 1:1 onto the v92 server as the patch 001 baseline: region strings,
area sections, spawns (wipe-and-replace), shops, story quest spine, zone quest availability, and
map surfaces. Salvage carried over from the retired pilot: charm system (spine dependency), legacy
string fixes, Stepstone disable, plus fixes that survive the wipe. After live validation and
baseline commit, a separate v17 padding phase reintroduces dormant content per doctrine rules.

## Scope

Unchanged from `docs/patch-001-scope.md`: continent 13 as five layered HZs (13 combat, 64 hub,
213 social, 313 politics, 364 hub-politics) plus dungeon 436 / continent 9036. Out of scope:
prologue instances 415/9015, 416/9016; Stepstone Isle quests get disabled (policy divergence).

## Key inputs

- Old pilot data artifacts (read-only): `docs/plans/iod-alpha-content-loop/data/`
- Old patch 001 specs (reference only, moved out of the repo): `temp/patch-001-v17-reference/`
  under the project root (local, not in git)
- Prior lessons that remain binding: patch specs apply ONLY via migrate batch replay; single-spec
  `dsl apply` source-ref replay wipes sibling specs' changes on shared files. QuestGroupList has no
  client sync entity. StrSheet_NpcLoc is client-only, regenerated via `tools/dc-restore/gen_npcloc.py`.

## Phase log

| Phase | Status | Notes |
|-------|--------|-------|
| 0: Framework setup | Done 2026-07-20 | Doctrine adopted; folders created; `client_dc_v31` wired in .references(+example); content-restoration skill rewritten; old pilot tracker marked RETIRED; old specs moved to temp/patch-001-v17-reference |
| 1: Salvage disposition pass | Done 2026-07-20 | data/salvage-manifest.md: 7 CARRY-OVER (08,10,11,14,15,16,18), 9 REWORK (00,01,04,05,06,07,09,12,13), 3 RETIRE (02,03,17). v31 1384 uses charm 7100 natively with the charm-use step absorbed; 1385 sentinel-disabled in v31; regenerated enable spec must NOT re-enable 1385 |
| 2: Three-surface revert | Done 2026-07-20 | Server repo stashed (235 files, stash "pre-v31-redo overlay snapshot 2026-07-20" on feature/iod at 9c7163fe); client-dc repo stashed (95 files, same label at 495fea2e); dev overlay reset via deploy_dev --revert (world server restart pending) |
| 3: v31-vs-v92 diff artifacts | Done 2026-07-20 | All four families diffed and adjudicated; see Diff artifacts section |
| 4: Spec authoring | Done 2026-07-20 | 12 specs, all validate clean, batch dry-run 1568 ops / 0 warnings. 00 sections (12), 01 region strings (1), 02 worldmap (1; sec9 delete deferred, DSL request filed), 03 shops (4), 04 quest rewards (65, generator gen_v31_reward_specs.py), 05-11 carry-overs (1080/1/92/150/98/62/2). NO spawn/enable/task/story-group specs needed. Migrate gained the missing newWorldMap -> NewWorldMapData sync mapping |
| 5: Apply + deploy + live validation | LIVE TEST IN PROGRESS 2026-07-20 (client dev.23) | LIVE-TEST FINDING 1 (fixed): quest links for random-in-fence spawns (party packs + pos-0,0,0 singles, e.g. Stonebeaks 301191/301193/301194 for Climbing Through the Ranks) had 13#0,0,0 marker positions; gen_npcloc.py copied void spawn pos verbatim. FIX: void pos now resolves to the containing territory's fence centroid; verified 0 void tokens, centroids within ~35 units of the v31 client's authored points (confirming BHS used the same derivation); published dev.23 (client-only, no server restart needed). LIVE-TEST FINDING 2 (expected behavior, not a bug): zero yellow zone quests in IoD; v31 itself sentinel-disables all 40 non-story quests (live set = story groups 1+2 = 25 exactly); Taras 1343/1344 disabled in v31, Jirash only carries class-gated training quests; padding-phase (7) deliverable per doctrine. | RULING UPDATE 2026-07-20: shared stores ported to v31 game-wide (spec 03 now 9 ops: +1601/1602/2501/2502/2505; side effects documented in spec header) and T-cat removed (spec 12 single cascade territory delete; spec 07 down to 91 ops; NpcLoc regen 121 entries). Batch replayed as 13 specs / 1573 ops / 0 warnings; targeted gate re-run ALL PASS (TerritoryData_64 = v31 minus exactly Tikat's territory; 8 BuyLists match v31 minus documented skips; no other drift). Server push 85 files hash-verified; client published 0.1.0-dev.22. PRIOR PASS | First apply hit a spec 04 keying defect (reward rows sharing a templateId across classes collapsed; 116 v31 rows lost on 11 quests); generator fixed to emit one row per templateId with merged semicolon-joined class lists; server tree reverted and full batch REPLAYED clean (12/12, 1568 ops, 0 warnings, 105 files). Reconciliation gate: ALL 8 CHECKS PASS (incl. deep reward compare: 0 v31 pairs missing; spawn no-drift re-confirmed). Client-registry leg done (NpcLoc regen+prune 122 entries, 100% v31-client coverage; 2 dangling 13035 MapDefine labels removed). DEPLOYED: server push 84 files hash-verified; client packed, installed, published 0.1.0-dev.21. World-server restart is manual (user). Note: 12 orphan comp entries (1342, 1388, 1361-1368, 1380, 1381) have no quest file in either era and correctly stay empty |
| 6: Baseline commit + patch 002 rebase | Commit DONE 2026-07-20 | Story spine live-validated end to end by the user (reached 1317 Ride Off into the Sunset at level 10; pacing confirmed). Baseline-lane commits: server c59c18ff "Restore IoD to the v31 baseline (patch 001)" (85 files), client 43bedc3a "Sync client for IoD v31 baseline (patch 001)" (15 files). Patch 002 rebase still pending. Alpha-boundary spec 13 (policy, revert at launch) being authored on top: quest 1317 ends at Leiyane with reward, task 4 removed, Pegasus menu deleted, alpha-closure texts (user-approved wording) |
| 7: v17 padding phase | LEVEL 1 + POLISH + REWARD FIX + DROP TABLE APPLIED 2026-07-21, LIVE VALIDATION CONTINUES NEXT SESSION | SESSION CLOSE (2026-07-21): spec 20 restores the v31 ECompensation_13 entry for Corrupted Theron Chief 300945 (First Expedition drop bags, v31 1:1, not class-scoped, no divergence); batch 21 specs / 2148 ops / 0 failed; hand edit re-applied; server push 44 files verified; client stays 0.1.0-dev.27 (spec 20 is server-only). Decisions 6 (level caps stay authentic) and 7 (drop table restored, 1310 stays OUT) recorded. NEXT SESSION: live-test checklist = armor payout (1305 or side quests 1322/1325/1326/1330/1347), First Expedition drops from 300945 at the gorge edge, Orcan density (1349 pace), 1348/1319 mob availability, Ramun click (1327), single politics NPCs, Sorcha auto-entry + defense + fail-eject (1346), repeatable cycle 1341 (level 8-12 char). PRIOR | REWARD FIX (2026-07-21): user live report (weapons paid, armor never) exposed that spec 04's semicolon-joined class rows (workaround for the DSL templateId-keying collapse) are not an engine format (0 occurrences in stock v92/v31); filed docs/dsl-requests/2026-07-21-compensation-class-row-collapse.md; DSL delivered d79aca90 (identity templateId+class+race, E207 rejects semicolons) + 363ed076 (EventTask npc field, E426); generator reverted to native per-class emission, spec 04 regenerated (65 ops; 1305 = 48 rows / 12 classes; 0 semicolons anywhere), spec 19 regained the npc="437,1001" attribution; batch replayed 20 specs / 2147 ops / 0 failed; RestoreTargetQuest hand edit re-applied (dsl-request issue 3 still open); NpcLoc 146; server push 43 files verified; client 0.1.0-dev.27. First Expedition armor (incl. Cuirass 15022) now actually pays from story 1305 and side quests 1322/1325/1326/1330/1347. PRIOR | POLISH WAVE (2026-07-21, from first live test): spec 15 regenerated 509 ops (density: Orcan camp 4x tpl-4 spawnCount 5, patrol spawnCount 2, bespoke 1300060/1300061 rebuilt one-territory-per-marker 10/17, stale hulls deleted), spec 18 (Ramun 1038 spawn-script reposition + 5 dual-state politics twin removals incl. Hyneu), spec 19 (dungeon 9037 reclaimed for Sorcha 1346: v31 config restored solo/lv8/quest-gated; level-65 line 21301-21307 sentinel-disabled at head; COMPANION HAND EDIT: RestoreTargetQuest 21307 removed by hand, re-apply after every replay, dsl-request issue 3). Research artifacts: padding-density-fixes, padding-sorcha-entrance, padding-ramun-dupes, padding-reward-audit, padding-first-expedition (user's First Expedition memory CONFIRMED: full set granted by story 1305 + disabled 1310; v31 ECompensation_13 drop table of the 9 armor pieces removed in v92 = open restoration option C). 1334 non-offer explained: authentic 6-10 level cap (1341 caps 12, 1390 caps 12). Batch 20 specs / 2147 ops / 0 failed; targeted verify PASS; NpcLoc 146 entries; server push 42 files verified; client 0.1.0-dev.26. OPEN USER CALLS: C gear option (ECompensation drop restore / 1310 reconsider / patch-002 design), 1334 level-cap raise. PRIOR | Level 1 analysis (4 agents) + adjudication: `data/padding-level1-proposal.md` (verdicts over the 40 disabled quests; corrections incl. the refuted collections blocker and the EN-vs-KR identity split). Specs 14-17 authored (26/461/13/11 ops), batch replayed 18 specs / 2091 ops / 15 expected warnings, reconciliation gate ALL 7 PASS. LATE FIX in same wave: v92 collect-quest bodies carried remapped collection ids with no IoD nodes (1334: 404, 1336: 403, 1341: 405); retargeted to the placed v31 ids 410/409/411 (tracker ruling 3 resolved), clean re-replay + targeted gate PASS. Enabled 34 quests (25 no-world-edit incl. courier re-anchor on 1309 and 1343/1344 gated behind 1316; 9 world-dependent); 19 habitat groups (217+4 spawns; Vekas excluded from 1300020); 6 giver NPCs at v17 NpcLoc markers. NpcLoc regen 147 entries (0 void). Server push 38 files verified; client 0.1.0-dev.25 published. StrSheet_NpcLoc technique + EN/KR identity census codified in playbook + content-restoration skill. World restart manual (user); live checkpoints: 1346 instance, fixed dialogs 1322/1327, repeatable cycle 1341, ruins density, restored-giver display names. NOT enabled: 1306/1307/1308/1310 (cut subplots, OUT), 1389 (deferred), 1385 (superseded). Level 2 (Berlon chain) not started |

## Salvage manifest

See `data/salvage-manifest.md`. Orchestrator rulings on its DECISION items (2026-07-20):

1. Spec 15's item 70033 op: KEEP (broad charm-family restore; low risk; belongs to adaptation
   whitelist entry 1). Logged as divergence (adaptation).
2. Spec 13 ops 2-3 (9034/9053 sync-compat E650 band-aids): carry CONDITIONALLY; verify during the
   Phase 5 client sync whether the clean baseline still fails E650 on 9034/9053, drop if not.
3. v31 1384 task 3 (rest-to-max-condition stamina mechanic): port the v31 body UNCHANGED and make
   it an explicit live-test checkpoint. Hypothesis: with the stamina system retired on v92 the
   condition reads as MAX and the task auto-completes (the v92 baseline carried this same task
   live). Only if it blocks in the live test does it become adaptation whitelist entry 3 work.

## Diff artifacts

Phase 3 outputs land in `data/`.

- `shops-diff.md/.json` (done 2026-07-20): 18-merchant union roster; MATCH 1, PORT 4, DECISION 4,
  KEEP 9. Orchestrator rulings on the DECISION items:
  1. Store 250 (shared by 35 merchants game-wide): Ashley 313,1002 re-bind to 250 PORTS
     (IoD-scoped); store 250 CONTENT is NOT touched by the 001 baseline (blast radius 35 exceeds
     the accepted precedent). Charm purchase availability stays an open knob; USER CALL surfaced
     in the Phase 5 report. Note: quest 1384 grants its own charm, so the spine does not depend
     on this.
  1b. AMENDMENT (2026-07-20, Phase 4 finding): Rutgar/Sandom's entire classic-consumables diff
     lives in shared BuyLists 1601 (31 menus) / 1602 (34 menus), NOT in their IoD-exclusive tabs;
     ruled option (a): leave 1601/1602 untouched, grouped with store 250 into the pending user
     call. One clean op the diff missed DOES port: Rutgar's exclusive tab 16064 regains Skycastle
     Teleport Scroll 98032 (v31 = [98032,133,160]). Sandom's exclusive tab verified MATCH.
     Shops spec = 4 ops total (Viator 2, Ashley 1, Rutgar 1).
  2. Store 315 (Tikat winter event, 33 of 37 item ids absent from v92): OMIT, unrecoverable
     seasonal content; logged divergence.
  3. Store 100 (Viator crystals, shared with exactly 1 non-IoD merchant 60,1002, all ids valid):
     PORT to v31; blast radius 1 accepted (matches the old tab-2501 precedent); logged.
  4. Ellonia 64,8000 (v31 binds Halloween store 331): KEEP the v92 binding, OMIT the event store;
     logged divergence.
  5. Zone-13 v92-only hub merchant layer (9 NPCs): AMENDED to KEEP-INERT after verification
     (2026-07-20): none of the 9 templates (1271, 5001, 5004, 5005, 5006, 5008, 5101, 5201, 5301)
     exists in NpcData_13 and none spawns via TerritoryData_13 on either side; the layer is dead
     wiring (VillagerMenu/store bindings to non-existent templates) with zero player impact.
     Baseline leaves it untouched (no churn in the shared VillagerMenu file); flagged as a
     padding-phase cleanup candidate. Logged in the divergence log.

- `sections-diff / region-strings-diff / worldmap-diff / client-registry-readiness` (done
  2026-07-20): sections MATCH 5 / PORT 15 / DECISION 5; strings 41 MATCH, 5 v92-only; worldmap
  MATCH 2 / PORT 2 / DECISION 2. v31 CORRECTION adopted: 13013 is already "Airship Approach" and
  13015 already "Abandoned Camp" in v31 (both MATCH v92); the retired Terron-Run-13036 and
  Leander's-Outpost-rename plans are DROPPED. Orchestrator rulings:
  1. Camp-teleport cluster (sections 13031 North Dock + 13032/13033/13034, worldmap sec8 town,
     TeleportMenuList/TeleportList campIds): KEEP the v92 cluster; do NOT re-add classic
     13017/13020/13027 (13032-34 are v92 renumbers of the same camps, same names; re-adding
     duplicates them). Reason: live functional traversal subsystem, and the renumber precedent
     (old decision 3 REMAP) treats these as the same camps. Logged divergence; revisit only if a
     classic teleport network restoration is ever undertaken. Sections PORT list drops to 12
     (7 re-adds + 3 diverged realigns + Tower Base 64001/64007 re-enable).
  2. Section 13035 Ruined Temple: REMOVE (v92-only, cosmetic labels only), including its region
     string; the 2 dangling client MapDefineData minimap labels have NO sync coverage and go on
     the Phase 5 manual client checklist.
  3. Worldmap sec9 (13001 duplicate hidden field): REMOVE. Sec7 mapId reskin reverts to
     WMap_ATW_Field_01; sec6 Tower Base town re-enables (asset-safe, MapDefine ships in client).
     AMENDED (Phase 4): sec9 removal DEFERRED; newWorldMap has no section-level delete op in the
     DSL (request filed: docs/dsl-requests/2026-07-20-newworldmap-section-delete.md). Sec9 is
     visibleInMap=false, cosmetically inert; the delete op ships when the DSL capability lands.
     Phase 4 also adopted v31 exactness over retired-pilot values: Tower Base ring is the v31
     12-vertex set (not the pilot's 10), section-6 marker roster is the v31 6-NPC set (not the
     pilot's 8), and sec7's re-supplied marker roster keeps the KEPT camp-cluster markers.
  4. Region strings for 13031-13034: KEEP (cluster); 13035 string removed with its section. No
     other string ops needed (all classic names already present and identical).
  5. NpcLoc regen at Phase 5: extend gen_npcloc.py with an IoD-zone PRUNE (replace-by-zone for
     HZ 13/64/213/436) so the ~21 stale v92-only HZ-13 keys drop out; 313/364 have zero entries
     both eras, acceptable.

- `quests-diff.md/.json` (done 2026-07-20): 65/65 existence MATCH; sentinel-disabled set
  IDENTICAL (40/40, so NO enable spec is needed and 1385 stays disabled naturally); headers,
  story groups, prerequisites all MATCH (prior 1382-prereq-drop claim REFUTED: both sources
  retain 13,84 on 1382 AND 1383). Rewards: v92 QuestCompensationData_13 is ALL empty stubs;
  PORT all 65 rows from v31. Orchestrator rulings:
  1. Quest 1384 body: KEEP the v92 patch-000 body (charm 70033, rest-stamina task replaced by
     use-item-98, rewired flow). SUPERSEDES the earlier salvage ruling 3 (port v31 body
     unchanged): patch-000 already adapts BOTH dead-mechanic tasks and v31's 7100 flow would
     depend on a mid-chain item flip. Spec 15's 70033 op is therefore LOAD-BEARING, not
     extraneous. Whitelist entries 1 and 3; logged divergence.
  2. Training quests 1371/1373/1374/1375/1379 skill-learn ids: KEEP v92 values (v92 skill-table
     numbering; v31 ids would dangle). Whitelist 3; logged; each gets a live-test checkpoint.
  3. Dormant collection-id PORTs (1334/1336/1341, disabled in BOTH sources): DEFERRED to the
     padding phase together with the collections-axis reconciliation they depend on. Zero player
     impact now.
  4. New-class reward rows (15 class-scoped quests): append fighter/assassin/glaiver rows
     mirroring v31's per-class analog items, reusing the pilot's data-verified progression picks
     (retired spec 05 + gen_reward_specs.py tables) re-derived against v31 bag content. soulless
     omitted. engineer already has v31 rows.
  5. Class-gate widening for 1382/1351 (admit new melee classes): DEFERRED to patch 002 (forward
     design, not a v31 correction). Baseline keeps the v31=v92 gates.
  6. Internal inconsistencies 1322 and 1327 (task target vs dialog link): DORMANT (disabled in
     both); fix-to-consistency happens only if the padding phase enables them; noted there.

- `spawns-diff.md/.json` (done 2026-07-20): v92 IoD TerritoryData is SEMANTICALLY IDENTICAL to
  v31 across all six zones (641/641 spawns, 470 territories, 37 groups, 219 parties all MATCH;
  0 conditionalSpawn on either side; 375 pos-0,0,0 random-in-fence rows are the authentic engine
  pattern). The Phase 2 revert already restored exact v31 spawn state. Phase 4 authors NO spawn
  spec; the family becomes a verification checkpoint (re-run the diff after deploys). Package
  notes for FUTURE zones only: RestoreSpawnBase lacks msgBroadcastingChannel; Party pack spawns
  (48% of IoD spawns) are unmodeled in DSL archetypes.

## Divergence log

See `divergence-log.md`.

## Decisions

1. Charms stay in patch 001 (user decision 2026-07-20): the spine depends on usable charms.
2. No v17 story quest porting, including IoD (user decision 2026-07-20): never-built camps
   (Leander's Outpost roster, Kamarnu/Riel/Kirash/Clovis/Milun) stay unbuilt; quests referencing
   them stay disabled in the baseline.
3. Pacing is defined by v31 content.
4. T-cat/Tikat 64,9000 EXCLUDED from the baseline (user decision 2026-07-20): spawn deleted
   (spec 12), dialog op dropped from spec 07, dead menu wiring left in place. Supersedes the
   earlier keep-standing ruling.
5. In-game stores match v31 even where game-wide shared (user decision 2026-07-20): store 250
   content and BuyLists 1601/1602 ported to v31; side effects accepted and documented in the
   spec 03 header and divergence log. Supersedes the option-(a) deferrals and the store-250
   pending call.
6. Padding quest level caps stay v31-authentic (user decision 2026-07-21): 1334 (6-10),
   1341 (8-12), 1390 (6-12) keep their max-level conditions; overleveled characters simply
   age out of them. No divergence.
7. First Expedition acquisition (user decision 2026-07-21): restore the v31 ECompensation_13
   mob-drop table (spec 20); 1310 stays OUT; no authored side-quest gear in patch 001
   (patch-002 design space if wanted).
