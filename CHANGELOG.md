# Changelog

Covers all meaningful work across the reforged content project and correlated projects
(datasheetlang DSL, datasheet-domain, reforged-server ATP).
Newest entries first.

---

## 2026-07-21 (session 3)

### Content
- IoD Level 2 Berlon crafting-intro chain live-validated end to end and PATCH 001 CLOSED (committed locally on server datasheet, client-dc, and specs repos, not pushed; client published 0.1.0-dev.28 through dev.33). Spec 21: 6 one-time linear quests 1353-1358 (gather Verdra Fibers/Sun Essence/Krymetal Ore then craft Healing Potion I/Mana Potion I/Crit Power Scroll via recipes 91213/91221/91282; Berlon 64,1011 giver; gated behind story 1301)
- Material give-back reward model: each gather turn-in returns the gathered material plus the kit plus the recipe design, so the craft step is pure crafting; the craft turn-in requires the full crafted batch and Berlon returns 2 potions (1 scroll) as the reward
- Recipe designs 91213/91221/91282 restored to v31 identity ("Recipe: <product>" name, "Use this design to learn the corresponding crafting skill." tooltip) from the v92 "Worn Recipe" deprecation (spec 22)
- Consumables 6000/6001/6016/6017/6197 tooltip restored to v31 functional text (spec 22); verified usable in-game
- Gather-node map markers authored: StrSheet_CollectionLoc waypoints added for tier-1 collections 1/101/301 (absent in both v31 and v92) so the gather-quest journal markers resolve

### Infrastructure
- reforged-server: `gen_collectionloc.py` added to dc-restore (projects `CollectionTerritory_13_*` nodes into `StrSheet_CollectionLoc` 13# waypoints; add-only, idempotent, writes server + client)
- reforged-server: Patch Application Discipline rule encoded in root `CLAUDE.md` (apply and sync a patch only as a whole; `--no-narrow` when a patch adds new IdSorted quests; never commit the server/client datasheet repos mid-patch)
- datasheet-domain: `quest-link-system` doc gained the `StrSheet_CollectionLoc` gather-node registry and corrected the `{@LinkNpc}` claim (0 in data; `{@LinkCreature}` is the universal NPC and monster token); `quest-task-reference` gained the DeliverItem `아이템지정` element inventory gate

### Blockers resolved
- `2026-07-21-quest-journalscript-field.md` delivered (datasheetlang `cd080461`: task `journalScript` field) and adopted natively; interim JournalScript fixup retired
- `2026-07-21-deliveritemtask-wrong-item-element.md` delivered (datasheetlang `30220450`: DeliverItemTask body element corrected to `아이템지정`) and adopted natively; interim element fixup retired

## 2026-07-21 (session 2)

### Content
- Sorcha's dungeon 9037 fixed and live-validated end to end (quest 1346 completed in-game): the 8 classic territory groups (63 territories: Sorcha's villager party, wave stages 1-3, rear-guard, finale) were comment-disabled in v92 `TerritoryData_437.xml`; uncommented and restored 1:1 to v31 (swallowed `</TerritoryGroup>` re-added, speculative `bossInstanceId` 0 edit reverted to 43700996). Baseline-lane commit `b2ae08fa`
- `padding-sorcha-dungeon-investigation.md` corrected (banner + section 12): the "territory topology below the datasheet layer" conclusion refuted; report now records the comment-disable root cause and live-validated resolution
- Established live: AreaData section containment does NOT gate territory spawning (42 restored wave territories outside the shrunken v92 section polygon spawn normally); the conditional AreaData polygon fix is unnecessary

### Infrastructure
- `dungeon_audit.py` added to dc-restore: read-only dungeon reference integrity gate resolving DungeonData territory/entity refs against parsed per-HZ content, flagging COMMENT-DISABLED vs MISSING; regression-verified against the pre-fix 9037 snapshot (27 refs flagged); wired into the `content-restoration` skill pipeline as a pre-deploy gate for dungeon restores
- datasheet-domain: territory-system doc gained the "Comment-Disabled Territory Blocks" section (14-file / 18-group / 173-territory v92 census, swallowed-close-tag trap, parse-vs-grep audit rule) plus the section-containment negative result; `content-restoration` skill gained the parse-before-trusting lesson

### Blockers resolved
- `2026-07-21-workobject-entity.md` delivered (datasheetlang `3db84f4f`) and adopted: spec 19 now authors the Sorcha portal server legs via `workObjects`/`workObjectTerritories` upserts (5-file hand edit retired server-side); `WorkObjectData` sync entity added to sync-config + migrate `ENTITY_SYNC_MAP`, sync verified (tpl 134 normalized, 299 rows byte-stable)
- `2026-07-21-dungeon-data-mapper.md` issue 3 delivered (datasheetlang `885dd4eb`: `restoreTargetQuests` full replace, `[]` clears) and adopted: spec 19 carries `restoreTargetQuests: []`, the replay-time hand-edit trap is RETIRED; all three issues in the request closed. Spec 19 re-applied + `dungeon_audit` gate PASS + deployed

## 2026-07-21

### Content
- IoD padding Level 1 applied and deployed (patch 001 specs 14-20; batch 21 specs / 2148 ops / 0 failed; server push 44 files hash-verified; client dev.24 through dev.27): 34 of the 40 sentinel-disabled band quests enabled on recovered v17 wiring (25 no-world-edit incl. courier branch re-anchored on 1309 and 1343/1344 gated behind 1316; 9 world-dependent), 19 mob habitat groups restored (217 v17-fence territories + 2 bespoke NpcLoc-marker territories; Mysterious Ruins ecology back), 6 never-spawned quest givers placed at v17 NpcLoc markers (Eria Elin, Rabram, Beres, Mayer, Eredos, Muriel). NOT enabled: 1306/1307/1308/1310 (cut story subplots), 1389 (deferred), 1385 (superseded)
- Level 1 analysis artifacts in `docs/plans/classic-restoration/iod/data/` (padding-quest-gates, padding-overlap-rewards, padding-habitat-gaps, padding-dormant-systems, padding-npc-locations, padding-npcloc-sweep, padding-level1-proposal): per-quest gate verdicts, narrative/reward screens, habitat gap map, EN/KR identity census
- Dormant collect quests fixed on enable: v92 bodies pointed at unplaced collection ids (1334: 404, 1336: 403, 1341: 405); retargeted to the placed v31 ids 410/409/411 (tracker ruling 3 resolved)
- Dialog internal-inconsistency fixes on enable (doctrine rule 1): 1322 LinkCreature 300932 -> 300931; 1327 13#304 -> 13#300921 in both carrier texts
- Polish wave from first live test (spec 15 regen 509 ops, spec 18): Orcan camp rebuilt as Mini Orcan farm (2 -> 20 concurrent for the 48-kill quest 1349), bespoke 1348/1319 groups rebuilt one-territory-per-marker (1 -> 10 and 1 -> 17 concurrent), Herald Ramun 1038 moved onto his spawn-script endpoint (quest 1327 clickable), 5 inert dual-state politics NPC twins removed (Ashley/Jilva/Misrile 313, Ainah/Hyneu 364)
- Sorcha's Reckless Challenge unlocked (spec 19): continent 9037 reclaimed with the v31 dungeon config (solo, level 8+, quest-1346-gated auto-entry, wave defense, fail-eject); non-classic level-65 Garden of Dawn line 21301-21307 sentinel-disabled; dungeon 437 added to the patch-001 scope doc; companion hand edit removes the un-modeled RestoreTargetQuest row (re-apply after every replay)
- Quest reward class rows re-encoded to native per-class format (spec 04 regenerated, `gen_v31_reward_specs.py` semicolon workaround removed): the merged class lists were not an engine format and paid nothing; First Expedition armor (incl. Cuirass 15022) now actually pays from 1305 and the gear side quests
- First Expedition open-world drop path restored (spec 20): v31 ECompensation_13 entry for Corrupted Theron Chief 300945 (9 armor + 9 weapon drop bags) reinstated 1:1
- `migrate.py` maps `dungeonDatas` (server-only); `gen_habitat_specs.py` added (deterministic habitat-spec generator with QUEST_DENSITY overrides and same-family overlap guard)
- ZONE-PORT-PLAYBOOK gained the "Phase 7 padding: era-client research surfaces" section (StrSheet_NpcLoc position recovery, EN-client vs KR-server identity census); `content-restoration` skill updated to match (its "clients never contain NPC positions" claim corrected)

### Infrastructure
- datasheetlang: questCompensation item identity now templateId+class+race so per-class rows survive apply, semicolon class lists rejected with E207 (d79aca90); DungeonData EventTask `npc` attribution field + invalid enums surfaced as E426 (363ed076)

### Blockers resolved
- `2026-07-21-compensation-class-row-collapse.md` delivered (d79aca90) and adopted; `2026-07-21-dungeon-data-mapper.md` issues 1-2 delivered (363ed076), issue 3 (RestoreTargetQuest modeling) still open with a documented hand edit

## 2026-07-20 (session 3)

### Content
- v31-primary doctrine adopted (`docs/plans/classic-restoration/DOCTRINE.md`): v31 is the structural and content baseline ported 1:1 per zone; v17.11 demoted to padding-phase research index. Old pilot `docs/plans/iod-alpha-content-loop/` retired (data kept read-only); `content-restoration` skill rewritten; `client_dc_v31` added to `.references`
- Patch 001 rebuilt from scratch under the new doctrine: 13 specs / 1573 ops (was 19 / 2178), applied via migrate batch, 8-check reconciliation gate PASS, story spine live-validated end to end (new character to level 10, quest 1317 reached with balanced pacing). Baseline-lane commits: server `c59c18ff`, client `43bedc3a`. Deployed: server push hash-verified, client dev.21 through dev.23
- IoD reward sheet restored: v92 `QuestCompensationData_13` was 100% empty stubs; all 65 band rows ported from v31 plus fighter/assassin/glaiver adaptation rows on 15 class-scoped quests (`gen_v31_reward_specs.py`, one Item row per templateId with merged class lists)
- Sections/worldmap to v31: Tower Base 64001/64007 re-enabled, 7 classic sections re-added, 3 realigned, 13035 Ruined Temple removed (+2 dangling client MapDefine labels hand-cleaned), 13001 field map reskin reverted; v92 camp-teleport cluster (13031-13034) kept as ruled divergence
- Shared stores ported to v31 game-wide (user decision): store 250 incl. classic charm tab 2502 (33 charms), BuyLists 1601/1602 classic consumables; side effects enumerated in spec 03 header + divergence log. T-cat/Tikat 64,9000 removed from the baseline (spec 12 cascade territory delete)
- `gen_npcloc.py` gained `--prune` (replace-by-zone) and fence-centroid positions for pos-0,0,0 spawns, fixing dead quest-link markers for party-pack mobs (Stonebeaks et al.); regenerated client NpcLoc covers 100% of the v31 client registry
- `migrate.py` maps `newWorldMap` -> NewWorldMapData sync (was silently unsynced)
- Retired patch 001 v17-era specs preserved read-only at `temp/patch-001-v17-reference/` (local)

### Blockers resolved
- None; 2 new low-priority requests filed (`2026-07-20-newworldmap-section-delete.md`, VillagerDialog client sync)

## 2026-07-20 (session 2)

### Content
- Charm tutorial de-duplication live-confirmed (patch 001 spec `17-iod-charm-quest-dedup.yaml`, 5 ops; batch now 19 specs / 2178 ops, 0 warnings; server pushed + client dev.20): quest 1384 "Getting to Know the Garrison" task 2 rewired `2 -> 6` and stripped of its charm grant, reward bumped to Onslaught Charm IV x2; quest 1385 "Always After Me Lucky Charms" retargeted to Onslaught Charm IV (start item + task condition) with its obsolete Stamina journal text replaced. 1384 and 1385 each carried a use-a-charm step; no source version has two (v17 keeps the step in 1385, v31 moved it into 1384 and sentinel-disabled 1385), so the duplicate was an artifact of re-enabling 1385 to its v17 wiring on top of a v31-lineage 1384
- Quest string edits now reach the client: sync-config gained a `StrSheet_Quest` entity (`merge: shard-routed`) and migrate maps `questStrings` to it; the previously server-only path had been silently swallowing edits since patch 000 (six stale 1384 strings shipped in this batch)
- `deploy_client.py` `--sync` stage removed (637 -> 479 lines): it mapped one family (`QuestData/*.quest`) and reported every other dirty family as unmappable, which went stale as sync-config grew. Syncing is migrate's alone; deploy-client README, migrate README, `content-restoration` skill, CLAUDE.md, and STATUS.md updated to match. Tool's `.references` surface reduced from 7 keys to 3
- `quest-live-test` skill added: derive live-test checkpoints from the spec diff, plus which QA shortcut skips which change (`/@jump_task` past an accept skips `startItems`; `/@start_quest` skips giver/prereq/level gating)

### Infrastructure
- datasheetlang: 10 previously declared-but-unconsumed quest header elements wired incl. `header.startItems` (84d5ded8); `merge: shard-routed` client-sync mode routing each record to the shard that already owns it (8a3d89ab). Also aligns `shareable`/`autoShare` to integer flags and retypes `questDialogue` to int, matching the on-disk format

### Blockers resolved
- `2026-07-20-quest-start-items.md` and `2026-07-20-strsheet-quest-shard-routing.md` both delivered, apply-verified, and closed (files deleted); the interim quest-string sync tool was deleted with the delivery rather than retained

## 2026-07-20

### Content
- Charm system restored and live-validated (patch 001 specs 14/15/16, 2173-op batch, 0 warnings; server pushed + client dev.18/dev.19): 50 buff abnormalities (488000010-488000059) on the 1:1 deterministic model (buff name/icon match the granting item; named charms at classic tier-3 values, greater at tier-4; Onslaught/Ethereal/Sanguine I-IV as kind-scoped bundles at half the classic tier bonus; trios at classic full values); 57 charm items usable again (41 NO_COMBAT flips) with real tooltips; all 50 charm skills cast to user + nearby allies (BHS food-buff area pattern); classic burn-burst visuals via per-kind appearEffectId; 30-min duration, persist through death; spike abnormalities 488000003-488000006 and their hand-edited skill injections removed
- `tools/dc-restore/gen_charm_specs.py` added: deterministic generator for the three charm specs + `docs/plans/charm-restoration/charm-design-map.md`; spec 16 definitions-factored (2781 to 321 lines, dsl-expand-proven equivalent)
- Sync coverage extended: sync-config gained `AbnormalityIconData` and `StrSheet_Abnormality` (shard-aware) entities; migrate map covers abnormalityIconData/abnormalityStrings + inline abnormality strings
- Stale `/deploy-patch` command removed (described the discontinued manual `.dat` distribution and hardcoded the DC encryption key); migrate and deploy-dev READMEs now document the real pipeline (migrate, then deploy-dev, then deploy-client pack/install/publish)

### Infrastructure
- datasheetlang: skill Area `type`/`maxCount`/`rangeAngle`/heights + Targeting header attrs modeled (a7cf8d11); XSD-required attribute fill on client sync, skill Effect `atk` modeled, shard-aware SourceMapped merge (42c8d67a). SkillData client sync of DSL-created elements now passes and StrSheet_Abnormality shard 0 stays duplicate-free

### Blockers resolved
- `2026-07-19-skill-area-type-attribute.md` and `2026-07-19-skilldata-sync-e650-and-strsheet-mirror.md` both delivered and closed (files deleted); charm skill authoring and full client sync unblocked

## 2026-07-19 (session 2)

### Content
- Tower Base minimap restored and live-confirmed: `13-iod-worldmap-town.yaml` re-adds the NewWorldMapData town section 64001 (full v17 marker roster) + sync-compat fixes on sections 9034 (E650 geometry backfill) and 9053 (Kezzel's Gorge realigned to the client-proven MapDefine); client counterpart synced via the new merge-by-id mode; published dev.16
- Quest link/ping/spawn-dot UI restored and live-confirmed: client `StrSheet_NpcLoc` regenerated for HZ 13/64/213/436 (134 entries from current server TerritoryData; the v92 rework had dropped HZ 64/213 wholesale); published dev.17
- Politics dual-state NPC duplicates removed (decision 24, IoD-wide audit complete: policy territories exist only in HZ 313/364): spec 03 now deletes the OFF/vacationing variants at Tower Base (Ainah 1002, policy cleric 1101) and the garden (Ashley 1001, off-duty Jilva/Misrile); Harger pair left pending decision (two distinct classic services, both menu-less in v92)
- Quest 1327 serum collection live-confirmed (closes the previous session's monster-target fix)
- Incident recovered: single-spec `dsl apply` source-ref replay had wiped spec 02's 451 spawn ops from TerritoryData_13 (locally and on dev); full `migrate --patch 001` batch replay (15 specs / 1863 ops) restored the complete state, redeployed and live-validated; patch specs are now migrate-batch-only (rule encoded in the apply-spec skill)

### Infrastructure
- datasheetlang: merge-by-id client sync mode preserving client-only records (4b1c61b7); `NewWorldMapData` sync entity enabled in sync-config with `merge_key_attributes: [id, nameId]`, verified lossless + idempotent against the live EUR client
- `tools/dc-restore/gen_npcloc.py` added: deterministic StrSheet_NpcLoc regeneration (replace-by-key merge; rerun whenever IoD spawns change; the family has no DSL schema)
- datasheet-domain: new `world-map-system.md` (NewWorldMapData/MapDefineData/WorldMapMarkerStyle chain, blank-map diagnosis) and `quest-link-system.md` (link tokens, the three location registries, rework registry-loss failure mode) with index/sidebar/skill wiring
- apply-spec skill: migrate-batch-only rule for patch specs + semantic-diff-before-enabling lesson for new sync entities

### Blockers resolved
- `2026-07-19-newworldmapdata-sync-lossy.md` filed and closed same day (merge-by-id delivery); NewWorldMapData client edits no longer manual

## 2026-07-19

### Content
- Patch 001 fully applied and deployed: 14 specs / 1856 ops (server dev VM SHA256-verified; client published 0.1.0-dev.12 through dev.14). Live in-game validation covered the story spine and zone chains through Garrison in Distress with v17 rewards paying out
- Live-test fixes shipped same-day: `12-iod-spawn-script-fixes.yaml` (Ramun spawn moved to his spawn-script endpoint; packet-capture-proven displacement pattern), 1303 gated on 1304 (v92 prereq clear had orphaned the logic operator, quest unofferable; interim gate matches journal order, decision 23), gather quests 1334/1336/1341 repaired to active collection nodes 409/410/411
- `06-iod-quest-tasks.yaml` regenerated on the delivered DSL task surface: 13 verified reconstructions (class-training trims 1303/1371-1378, gather fixes, 1390 deliver target); fabricated-body classes staged behind ALLOW_FABRICATED pending a live-load canary (1382)
- Client Area section topology now syncs (AreaData E650 fixed): restored camp sections reach the client from dev.14
- Session decisions 20-23 settled: T-cat exchanger removed from IoD; shared shop lists scoped; Ashley binding restored; 1303 keeps the 1304 gate

### Infrastructure
- `tools/dc-restore/` gained gen_section/spawn/shop/reward/storygroup/enable/speech/scriptfix/task spec generators (all deterministic, baseline-pinned) + packages `spawn-restore-standard` and `area-section-standard` ($extends refactor: spec 02 12543 to 4992 lines, dsl-expand-proven equivalent)
- Skills added: `dsl-definitions`, `spec-standardization`; packages README gained the archetype/curated maintenance classification
- datasheet-domain: new `action-script-system.md` (S1ActionScripts family, spawnType wire contract, displacement trap) + quest-system empty-operator trap section
- 9 DSL requests filed and 8 closed same-session after apply-level verification (SpeechCondition entity, quest header/requirements/triggers, faithful task rebuild + task-type/delete/hasReward/deliveryItems, AreaData sync XSD filtering, QuestGroupList entities, questCompensations docs, BOM headers); remaining open: 2 cosmetic clear-to-empty items

### Blockers resolved
- Quest re-enable, task reconstruction, villager speech, and client area sync all unblocked by DSL deliveries 52b57b8f / 2918a5c4 / 735abf92 (verified at apply level before adoption)

## 2026-07-18 (session 2)

### Content
- Patch renumbered: 66 custom specs moved `specs/patches/001/` -> `specs/patches/002/` (git mv); 001 repurposed as the classic-restoration baseline (retains `08-legacy-strings-restore`, `18-iod-item-string-fixes`); scope docs split (`patch-001-scope.md` rewritten as five-layer IoD + 436, `patch-002-scope.md` added; CLAUDE.md zone-scope section updated)
- Clean slate executed: server datasheet repo (113 tracked files), client-dc repo (47 files + 3 `nul` artifacts), and dev-server overlay all reverted to clean baselines
- IoD restoration north star + classification shipped under `docs/plans/iod-alpha-content-loop/data/`: v17.11 inventories (218 NPCs, 63 quests, shops/gathering/territories), v31 gap-fill extractions (spawns, stats, shops, loot, dialogs, quest server data), 3-source ID alignment (zero id reuse), section mapping table (incl. Terron Run new id 13036, Ruined Temple 13035 removal), per-key MATCH/RESTORE/REMOVE/GAPFILL verdict tables
- Decision queue closed: 19 settled decisions recorded in TRACKER.md (deep v17 task restoration for all 27 drifted quests with per-quest v31/v92 fallback; 1311 stays NPC-accept; 1379/1383 kept; soulless omitted from 001 reward bags; Sandom cluster, Ellonia store, and 3 v31-only spawn groups removed; 13030 v17 ring; 13015 reverts to Leander's Outpost; North Dock kept pending teleport-network phase)
- `TRACKER.md` added as the living consolidation doc for the restoration (supersedes PLAN.md batch model)

### Infrastructure
- `tools/dc-restore/` gained 9 deterministic extraction/analysis tools: `extract_npcs/quests/shops.py`, `extract_v31_spawns/econ/quests.py`, `align_ids.py`, `classify.py` (all artifacts regenerable byte-identical)
- `tools/migrate/` ENTITY_SYNC_MAP extended with quest/territory keys (`quests`->Quest, `questDialogs`->QuestDialog, `territory*`->TerritoryData; `questStrings`/`questCompensations`/`villagerDialogs` server-only)
- 4 DSL requests filed: questStoryGroups (QuestGroupList), areaSections + regionStrings, quest requirements/trigger gaps (+4 repro specs; prereq silent no-op, minLevel E500, accept/giver unexposed), questCompensations docs page

## 2026-07-18

### Content
- IoD story spine + side quests re-enabled end to end: Batch 2+4 re-enabled 33 quests with classic chain wiring (spine relinks 1305/1309/1311/1313/1316, story-group registrations), full v31 compensation fill (75 reward rows); Kishale pair 1322/1323 shipped with class-filtered rewards
- Batch 3 spawn reconstruction applied: TerritoryData_13 gained 17 mob territory groups (client fences), TerritoryData_213 gained Leander's Outpost (territory 21300037) + 8 villager NPCs; Eria relocated to the authentic outpost spot (55422,-82484)
- Quest 1311 "Redeployment" converted from auto-accept to NPC-accept (staged-restore robustness); Stepstone starter chain head 59901 "To Help by Gathering" disabled via 99,99 sentinel
- Collection-ref regressions fixed: 1334/1341 (404/405 to 410/411), 1336 (403 to 409)
- Duplicate service-less NPC twins disabled (voidSpawn): Harger 313,1004 / Ainah 364,1002 / Hyneu 364,1102
- Client launcher dev channel published through 0.1.0-dev.11
- **PIVOT (decided, not yet executed): IoD baseline restoration to be redone with old client v17.11 as north star, v31 gap-fill only, to remove content duplication; baseline must commit before patch 001. Handoff: docs/plans/iod-alpha-content-loop/RESUME-2026-07-18.md**

### Infrastructure
- `tools/dc-restore/` gained `dcq.py` (cross-source query), `audit_quests.py` (12-flag deterministic auditor), `spawn_restore.py` (territory/mob/villager reconstruction from client fences)
- `content-restoration` skill added (restoration pipeline, v17.11 source precedence, staged-restore traps, two-commit-lane discipline)
- datasheet-domain: territory-system.md gained "Client-Side TerritoryData Variant" section (client carries fences+descs only, never NPC spawns; archaeology source)

## 2026-07-17 (session 2)

### Content
- IoD soft-disabled quests re-enabled (99,99 sentinel removal + wiring restored from client reference): 1334 + 1341 live-validated in-game (stale collection refs fixed 404/405 -> 410/411), 1336 re-enabled dormant (prereq 1335 still disabled; collection 403 -> 409 fixed), Kishale pair 1322/1323 re-enabled with v31 class-filtered rewards (boots/weapons), deployed, live validation pending
- QuestCompensationData_13: v31 reward rows restored for 1334, 1336, 1341, 1322, 1323 (previously empty stubs)
- Eria (213,1021) spawn authored in TerritoryData_213 (no historical spawn source exists); provisional Tainted Gorge camp placement, relocation to Leander's Outpost planned in Batch 3
- Client DC synced (5 quest shards), DataCenter repacked, teratest install updated; dev channel published 0.1.0-dev.7 / dev.8 / dev.9 via patcher CLI (release records auto-appended from dev.9 on)
- PLAN.md restructured to live-test iteration + batch model; user decisions recorded (v31 reward era with client fallback, 1311 keeps "Redeployment", Batches 1+3 approved); tension points, iteration-0 gap report, 65-quest audit, ruins archaeology, and legacy wiki location map added under docs/plans/iod-alpha-content-loop/

### Infrastructure
- `tools/dc-restore/` toolkit added (client-DC / v31 / v92 restoration): survey + gap report, quest_restore (sentinel re-enable, prereq relink, story-group registration), comp_restore (v31 comp merge), dcq cross-source query CLI, audit_quests deterministic 12-flag quest auditor; registered in CLAUDE.md workflows
- `tools/deploy-client/` added: one-command client pipeline (DSL sync of dirty quest shards, novadrop pack, game-install update, CF patcher build/sign/dry-run/publish with version bump + rporigin/deployment-log recording); registered in CLAUDE.md workflows
- `.references` keys added: `old_client_dc`, `v31_datasheet`, `game_client_install`, `patcher_origin` (+ example placeholders)
- datasheet-domain: quest-system.md gained "Soft-Disable Sentinel (99,99)" section (84 quests corpus-wide, retire-in-place pattern); TRACKING updated

---

## 2026-07-17

### Content
- Dev server datasheet reverted from stale test overlay to payload HEAD; patch 001 re-applied fresh onto the clean baseline (65 specs, 0 failed, 10177 ops, includes IoD specs 16-22 and the one-shot balance multiply); client sync 16 entities / 52 files; delta deployed to dev server (52 files, SHA256-verified); world server restarted and loaded live
- Balance docs corrected to actual IoD multipliers (maxHp x10 / atk x60, intentional): spec comment + STATUS.md
- IoD alpha content loop plan authored: `docs/plans/iod-alpha-content-loop/PLAN.md` (old-client quest archaeology, feasibility gates passed, decisions settled, phased handoff)

### Infrastructure
- `tools/deploy-dev/` added: SSH delta deploy to the dev game server (sftp batch; `--dry-run`/`--verify`/`--status`/`--revert`); `/deploy-dev` command added; `/deploy-patch` step 3 switched to it
- Server-share push retired: `server_share` key removed from `.references`; replaced by `deploy_repo`, `dev_server_ssh`, `dev_server_datasheet`; share instructions removed from migrate README, GENERAL_WORKFLOW, PROJECT_STRUCTURE
- reforged-deploy: dev game VM sshd service restarted; `git` now resolves in non-interactive SSH sessions (stale service PATH)
- Content framework wired in: `content_framework` key added; CLAUDE.md gained Content Framework, Dev Game Server, and public-repo credential-rule sections plus two-server MCP docs; `domain-research` routes design/balance questions to framework docs; framework repo back-points to this project
- Skills: `skill-authoring` standard (+ frontmatter reference) and `/learn` lesson-capture/curation skill added
- `docs/mcp-requests/` convention added; `2026-07-17-iod-alpha-research.md` filed (20 datasheet-mcp issues from IoD alpha research; fixes in progress)
- Doc drift cleanup: hardcoded server datasheet paths replaced with `.references` placeholders (ENCHANT_MATERIALS, gear-infusion, infusion-loot READMEs), deprecated `dsl client-sync` corrected to `dsl sync -e`, `.references.example` gained missing `domain_data` key
- datasheet-domain: QuestCompensation documented in `loot-system.md` (156-file scan; itemBag modes, class-gear encoding); TRACKING, index, and loot-system skill synced

### Blockers resolved
- `2026-07-17-iod-alpha-research.md`: 11 of 20 datasheet-mcp items fixed same day (v31 profile_item/gathering crashes, PointStore/BuffStore resolvers, NpcTemplate check_references, kill-target quest indexing, sentinel rendering, nested-block batch_lookup, Item display names, dead-bag markers); rebuilt exe validated 15/15 via stdio harness; deployment pending session restart

---

## 2026-04-25 (session 2)

### Infrastructure
- `migrate.py`: switched from per-spec sequential apply back to single batch `dsl apply`; DSL's shared in-memory cache now correct; adds `--source-ref HEAD` for idempotent balance specs; adds `--no-source-ref` escape hatch

### Blockers resolved
- `2026-04-25-multi-spec-upsert-updatewhere-e422.md` — fixed in DSL commit `2278066c` (write-aware ElementIndex in EntityLocator) ✅
- `2026-04-25-multi-spec-apply-progress-not-streamed.md` — fixed in DSL commit `e66cda21` (per-spec lines streamed immediately on completion) ✅

---

## 2026-04-25

### Content
- `packages/npc-ids` package added — IoD (zone 13) NPC template IDs: 47 individual variables + 6 category groups (Friendly/Normal/Elite/Boss/World Boss/Objects); registered in `datasheetlang.yml`
- `specs/patches/001/balance/zone-0013-island_of_dawn.yaml` — IoD normal monster rebalance: maxHp ×5, atk ×10 (calibrated to gear formula multipliers from standard-issue starter gear)
- `01-reaper-weapons.yaml` renamed → `02-reaper-weapons.yaml`; `01-brawler-weapons.yaml` renamed → `02-brawler-weapons.yaml` (execution order fix)
- Patch 001: all 57 specs applied via per-spec sequential migrate; sync narrowed to 47 modified server files

### Infrastructure
- `migrate.py`: replaced batch `dsl apply` with per-spec sequential apply — each spec flushes to disk before the next reads; cwd set to project root (no implicit sourceRef)
- `tools/spec-check/` added — single-spec validate/apply tool; passes `--source-ref HEAD` of the datasheet repo for deterministic baseline on non-idempotent specs

### Blockers resolved
- `2026-04-25-multi-spec-upsert-updatewhere-e422.md` — worked around via per-spec apply; DSL bug filed

---

## 2026-04-23 (session 2)

### Content
- `equipment-item-standard` package extended to own every gear baseline: LOW tier intermediaries, `LowTierChainWeapon`/`LowTierGauntletWeapon`, 26 per-class chest definitions (`{High,Mid}TierChest{Class}Item` × 13 classes), per-material armor `linkPassivityCategoryId` on exported items (120316/4150/4152/4151/4250), `_WeaponBase.linkPassivityCategoryId` scalarized, `dropType:0` override dropped from class-restricted weapon derivations
- `01-armor-standardize.yaml` rewritten to sweep via `$extends: {Tier}{Slot}Item` for tier baseline + `$extends: {Tier}Chest{Class}Item` for per-class chest overrides (zero hardcoded attributes)
- `01-weapon-standardize.yaml` rewritten to sweep via `$extends: {Tier}Weapon{Role}Item` for tier × role baseline + per-subtype overrides for chain/gauntlet weapons
- `equipment-item-ids`: added 26 per-class chest partitions (`{HIGH,MID}_TIER_CHEST_{CLASS}_IDS`) and 5 per-subtype weapon partitions (`{HIGH,MID}_TIER_CHAIN_WEAPON_IDS`, `{HIGH,MID,LOW}_TIER_GAUNTLET_WEAPON_IDS`)
- `enchant-standard`: `ENCHANT_LOW_TIER_*` values aliased to `ENCHANT_MID_TIER_*` (950011-950017) per shared-enchant-pool decision
- Retired as redundant: `03-flawless-standardize.yaml`, `03-chest-toproll-items.yaml`, `07-gear-enchant-sync.yaml`
- `06-brawler-weapons.yaml` renamed → `01-brawler-weapons.yaml` so authoring specs precede standardize sweeps alphabetically
- `tools/gear-enchant-sync/` generator disabled with updated README (scripts preserved)
- `tools/potential-unlock/generate_potential_unlock.py` refactored to emit `$extends`-based specs (added `TIER_BY_GRADE` + `resolve_tier_def()`, `COPY_ATTRS` trimmed 55 → 17, emits `imports:` block + `$extends` per item); regenerated `12-potential-unlock-gear.yaml` (5333 → 2788 lines)
- Fixed server load crash: Token 90 (Bastion Masterwork) had 15 `linkEnchantId` mismatches between source LOW Bastion items and result Unlocked items; resolved by regenerated `12-potential-unlock-gear.yaml` flowing `linkEnchantId` from package `$extends` (0 mismatches across all 582 pairs / 53 tokens)

---

## 2026-04-23

### Content
- `01-reaper-weapons.yaml` migrated from `weapons` package to `equipment-item-standard` — spec reduced from 3 local definitions to 2, 20+ attributes removed from spec scope
- `06-brawler-weapons.yaml` migrated from `weapons` package to `equipment-item-standard`
- `packages/weapons/` removed; `datasheetlang.yml` `defaultImports` cleared — no specs depend on it
- `packages/equipment-item-standard` restructured: universal standard attrs added to `_EquipmentBase`; 8 tier intermediary bases introduced per slot; `linkPassivityCategoryId: 120300` added to `_WeaponBase`; `MidTierChainWeapon`, `HighTierChainWeapon`, `MidTierGauntletWeapon`, `HighTierGauntletWeapon` added as class-specific derivations
- Package and patch 001 READMEs updated to reflect new hierarchy and consumers

### Infrastructure
- datasheetlang: Fixed package-internal variable scope — definitions exported from a package no longer require consumers to re-import the variables used internally

### Blockers resolved
- `2026-04-23-package-variable-scope-not-resolved-at-export.md` — resolved ✅

---

## 2026-04-22

### Content
- Island of Dawn migration declared complete — all phases 0–4 done, in-game validated
- Patch 000 all 8 specs applied, synced, and validated in-game:
  - `00-iod-training-bomb.yaml` — item 5002 itemUseCount restored to unlimited
  - `01-iod-garrison-quest.yaml` — quest 1384 task chain redesigned for v92 compatibility
  - `02-iod-skill-quest-strings.yaml` — skill name strings corrected for 5 classes
  - `03-iod-skill-quest-conditions.yaml` — skill ID conditions corrected for 5 classes
  - `04-iod-garrison-dialog.yaml` — quest 1384 garrison dialog revamped
  - `05-iod-gathering-nodes.yaml` — pickSkillType fixes + territory id=1/5 restored
  - `06-iod-teleport-scroll-coordinates.yaml` — teleport scroll coordinates confirmed in-game ✅
  - `07-iod-teleport-scroll-strings.yaml` — item 133 name/tooltip restored from v31 ✅
- Client DC synced for all patch 000 entities (Collections, ItemData, SkillData, QuestDialog, StrSheet_Item)
- Server share updated with patch 000 changes

### Infrastructure
- datasheetlang: Fixed float precision expansion — `dsl apply` now caps floats to 8 decimal places (92fa465) ✅
- datasheetlang: Reverted server XSD attribute-order source generation (ab41f20) — one-time reformat diff expected on first sync per entity; subsequent syncs stable
- datasheetlang: Fixed ClientElementPreserver attribute equality check (e65b390)

### Blockers resolved
- `2026-04-22-float-precision.md` — resolved by 92fa465 ✅
- `2026-04-22-skilldata-sync-attribute-reorder.md` — resolved by reverting XSD attribute-order feature (ab41f20); one-time reformat on first sync is expected behavior

---

## 2026-04-21

### Content
- IoD Phase 4 validation complete: 65/65 quests, 72/72 reward items, all NPC templates confirmed zero-diff vs v31
- Zone 436 (Karascha's Lair) validated: 8 NPCs, correct loot (ECompensation), quest 1316 task chain intact
- Story groups 1 (18q) and 2 (7q IoD) confirmed; prologue zones 415/416 (8+8q) confirmed
- Patch 000 spec `06-iod-teleport-scroll-coordinates.yaml` applied — skill 60130101 correct on server + client
- Patch 000 spec `05-iod-gathering-nodes.yaml` applied — collection types and territory id=1/5 restored
- IoD zones 13 and 436 added to patch 001 zone scope
- CollectionData and SkillData entities added to migrate.py entity map
- Migrate tool upgraded: manifest-narrowed apply→sync with preflight `nul` file checks

### Infrastructure
- datasheetlang: Fixed `--from-manifest` narrowing for ZoneBased + IdSorted strategies (7d64e6a)
- datasheetlang: Fixed `--from-manifest` narrowing for Monolithic + SourceMapped (0a10f78)
- datasheetlang: Made `Create{Targeting,Area,Effect}EntryCommand` idempotent — eliminates empty placeholder appends on re-apply (fc6e3b0)
- datasheetlang: Mapped TeleportType string to typed enum across schema, commands, mapper (53b8850)
- datasheetlang: Fixed CRLF line endings and indentation preservation in `dsl apply` (e86a42d) — validated ✅
- datasheetlang: Fixed SkillData sync float normalization and preserve-unchanged verbatim (8db859c) — validated ✅
- datasheetlang: Fixed UTF-8 BOM preservation in `dsl apply` (5427ba1) — validated ✅
- datasheetlang: Fixed SkillData NPC shard oscillation via composite key (id+templateId) (29137ed) — validated ✅ (536/536 unchanged on second sync)

### Blockers resolved
- `2026-04-21-commonskills-apply-appends-empty-placeholder-elements.md` — resolved by fc6e3b0
- `2026-04-21-manifest-narrowing-broken-for-zonebased-and-idsorted.md` — resolved by 7d64e6a
- `2026-04-21-xml-writer-crlf-line-endings.md` — resolved by e86a42d ✅
- `2026-04-21-apply-indentation-normalization.md` — resolved by e86a42d ✅
- `2026-04-21-skilldata-sync-attribute-order-float-format.md` — float normalization resolved by 8db859c ✅; attribute ordering still open
- `2026-04-21-apply-strips-utf8-bom.md` — resolved by 5427ba1 ✅
- `2026-04-21-skilldata-sync-npc-non-unique-id-non-idempotent.md` — resolved by 29137ed ✅

---

## 2026-04-20

### Content
- Teleport scroll coordinates applied to server (skill 60130101, recallContinent=13)
- Malformed XML placeholders in UserSkillData_Common.xml cleaned up (two-step hand-fix)

### Infrastructure
- datasheetlang: Apply manifest (`--manifest-out` / `--from-manifest`) implemented — targeted client sync without broad shard rewrite (90a62d9)
- datasheetlang: Fixed class-filter regex swallowing `.xml` on base files (UserSkillData_Common.xml now matches class=Common) (5dc68a2)
- datasheetlang: Orphan deletion correctly gated behind `--filter`/`--segment` flags (b4a51bf)

---

## 2026-04-18

### Content
- Zone 436 (Karascha's Lair) added to migration scope
- 8 zone-partitioned files + 3 VillagerData conditions copied from v31 → v92
- DungeonData_9036.xml restored to v31 conditions (levelOver=9, progressQuest=1316)
- Client DC zone 436: NpcData-00212 and TerritoryData-00218 generated via DSL sync
- IoD migration documentation added: assessment, zones, quests, file-manifest, plan, progress

### Infrastructure
- datasheetlang: SkillData segmented sync added — XSD-driven class filter, orphan deletion, 536-shard coverage (6bce01f)
- datasheetlang: Effect-level Teleport (`recallPos`, `recallContinent`, `type`) added to commonSkills/npcSkills/userSkills (c5d7874, e5911f7)
- datasheetlang: Area resolution via Descendants — AreaList-wrapped Areas now correctly targeted (b52b2bf)
- datasheetlang: CategoryVariants update/delete now respects category target (8e17ee5)

---

## 2026-04-14 to 2026-04-17

### Content
- Island of Dawn full migration executed (phases 0–3):
  - Phase 0: v92 server + client DC repos reverted to clean state
  - Phase 1: 34 v31 zone files copied; 8 v92-only files emptied; CollectionTerritory patched
  - Phase 2: 65 .quest files, QuestDialog files, StrSheet_Quest (1009 strings), QuestGroupList merged
  - Phase 3: 245+ client DC quest shards copied; zone NpcData/TerritoryData generated via DSL sync

### Infrastructure
- datasheetlang: QuestDialog subdirectory path resolution fixed (e12908c)
- datasheetlang: Nested Collections partial-update and delete-by-id (8a8dec3)
- datasheetlang: AreaId composite value type; NpcId element type (08d6f20)
- datasheetlang: Multiple quest task fixes (visit, condition, journal, nextTask) across 8 DSL requests filed

---

## 2026-04-05 to 2026-04-06

### Content
- Dyad crystal system: 1182 crystals across 6 tiers, per-type passivity configs, fusion structures, zone loot integration
- Infusion box system: gear-infusion-boxes package, zone loot tables across all patch 001 zones
- Crystal system, dungeon tokens, zone loot overhaul with unified eCompensation model
- Dungeon token shop chain fixed: ItemMedalExchange → VillagerMenuItem → BuyMenuList → BuyList

---

## 2026-02-22 to 2026-02-26

### Content
- Flawless gear added to progression pipeline with dedicated ID package
- Masterwork system replaced with potential unlock scroll (63 items, 6 tiers, 1:1 enchant evolution)
- Starter 0 gear added; weapon/armor attributes standardized across all tiers
- Missing enchant rolls added: weapon crit factor, prone damage, chest prone damage reduction

---

## 2026-01-30 to 2026-02-10

### Content
- Gear infusion: passivities, items generated from CSV source data
- Evolution specs refactored with `$with/$params` — monolithic file split into per-set parameterized specs
- EquipmentInheritanceData config added
- Zone loot specs added across all patch 001 zones
- Patch migration tool (`migrate.py`) introduced — automates apply→sync pipeline per patch
- Spec paths updated to patch-aware structure (`specs/patches/{NNN}/`)
- Enchant tiers split: +12 cap grades 0–3, +15 cap mythic (grade 4)
- Frostfire gear upgrade path added
