# Changelog

Covers all meaningful work across the reforged content project and correlated projects
(datasheetlang DSL, datasheet-domain, reforged-server ATP).
Newest entries first.

---

## 2026-07-28

### Content
- **First Guardian Legion field event authored and live-validated** (`specs/patches/002/34-iod-guardian-legion-v0.yaml`, 15 ops). New event `13/1` "Orcan Raiders" on Island of Dawn: `FieldData_13.xml`, territory group 1300062 with a mission boundary, staging pad and boss spawn (all `type="quest"`), one npc (`13,902` Dwarf Guardian), 8 `StrSheet_Field` strings, and a dedicated rotation group. v0 is a lifecycle probe, not shipped content: the progress bar is bound to the npc's HP so one kill completes the mission. Authored content under doctrine rule 4 Level 2, divergence-logged
- **Continent 13 redeclared `channelType="field"`** (`specs/patches/002/35-iod-field-event-continent.yaml`). A field event will not run on a continent without it. Server leg is spec-driven; the client leg is a documented hand edit pending the sync bug below. All 162 comments in `ContinentData.xml` survive the apply, 249 continents and every hunting zone list unchanged, exactly one attribute modified
- Field event families plumbed end to end: `Field`, `FieldEvent`, `StrSheet_Field`, `EventDialog` and `StrSheet_EventDialog` registered in `config/sync-config.yaml` and mapped in migrate's `ENTITY_SYNC_MAP`; `packages/fieldevent` installed with 22 task-type definitions and registered in `datasheetlang.yml`
- `AreaData` client sync fixed: its `source_mapping` key was missing the `AreaData/` prefix so the entity planned 0 files and the client `Area` leg had never synced. Zero client diff resulted, since the client `Area.xsd` declares neither `recallScrollPos` nor `recallRevivePos`
- Server datasheet repo commit `7b5e4092` adds the client-imported `StrSheet_Field.xml` (214 rows) and `EventDialog.xml` (159 rows) baselines, canonical pre-change content
- Patch 002 applied at 78 specs / 9211 ops / 0 failed / 0 warnings; both gates exit 0; `audit_field_event_references` on `13/1` reports 6 checked, 0 unresolved. Deployed to dev, 82 files hash-verified, client repacked and installed

### Infrastructure
- `datasheet-domain`: `entities/field-event-system.md` expanded 532 to 841 lines. Adds that a dedicated mission hunting zone is convention rather than a requirement, that event-owned territories must be `type="quest"`, the field channel type prerequisite with its source and live validation, operator/GM control, the absence of any runtime logging, npc-HP progress binding, low-level scoring calibration, and world takeover and restore. 14 corrections applied against measured counts
- Skills: `apply-spec` gained the `--source-ref` untracked-file hazard and the zero-source sync plan; its new-sync-entity lesson hardened to attribute-level diffs. `domain-research` gained the read-the-raw-comments rule. `content-restoration` gained the shipped-control-test method and installed-`.dat` verification

### Blockers resolved
- Patch 002 is reproducible again. `migrate` applies with `--source-ref <server HEAD>`, so untracked `StrSheet_Field.xml` did not exist in the commit it read and was rewritten from 214 rows to 8 on two runs. Committing the baselines fixes it: replay now yields 222 rows with zero canonical rows lost

### Blockers outstanding
- `docs/dsl-requests/2026-07-28-continentdata-sync-boolean-case.md`: the `ContinentData` client sync writes `false` for all 135 continents whose server value is uppercase `TRUE`, clearing `isSpecificSpace` on every dungeon and battlefield continent. `continentDatas` is mapped to `None` as a quarantine and the client leg is a hand edit until fixed. DSL team working on it
- `docs/dsl-requests/2026-07-27-idsorted-server-path-required.md`: `IdSorted` plans 0 files and exits 0 when `server_path` is omitted

## 2026-07-27

### Content
- **IoD recall network restored** (`specs/patches/002/26-iod-recall-points.yaml`, 12 ops). The Safe Haven Teleport Scroll (item 160, skill 60130100, type `MYSELF_VILLAGE`) carries no coordinate: its destination is the `recallScrollPos` of the AreaData section the player stands in, and death uses `recallRevivePos` the same way. v31 sends every continent-13 section's scroll to the Tower Base; v92 had repointed 12 of 21 to `93957,-89037,-4554` (North Dock), including the ROOT section 13001 that catches the whole island. All 21 sections now point at the Tower Base, and revive points are restored to their exact v31 mapping including v31's own northern exception (`87533.2031,-83932.6797,-4533.1616` on 13005/13030). Live-validated
- The 4 kept v92-only camp sections (13031 North Dock, 13032/13033/13034) were repointed too rather than left: their `vender`/`restBonus` flags advertise a service layer that does not exist, since `audit_continent_merchants` reports all 9 merchants filed under the HZ-13 camp layer as PHANTOM while the real cast stands at the Tower Base. Their revive points were derived from the v31 section whose fence contains each camp, not chosen. Divergence-logged as policy
- Item 133 (Tower Base Teleport Scroll, skill 60130101, `SER_POS`) was confirmed NOT at fault: byte-identical across the v31 server, v92 server and v92 client shard, resolving inside section 64001 in both eras. Patch 000's coordinate fix is intact
- Patch 002 applied at 69 specs / 9161 ops / 0 failed / 0 warnings; server diff exactly 12 insertions and 12 deletions on one file with every changed attribute a `recall*` value; both gates exit 0. Deployed to dev, 71 files hash-verified. Server-only: the client `Area` family did not change, so `0.1.0-dev.37` stayed current and no republish was needed

### Infrastructure
- `ZONE-PORT-PLAYBOOK.md` phase 3 gained the section-attribute trap: a MATCH verdict must state which fields were compared, since the IoD sections diff compared fences vertex-exact and never compared attributes, and partial "realign" upserts merge only the attributes they name. Also records that a destination-carrying attribute may live on the section rather than the item or skill that appears to own the behaviour

## 2026-07-26

### Content
- **Quest log reward panel now shows item rewards.** `QuestCompensationData` has a client leg (153 shards) that had never been synced, so every reward row written since the client DC was authored existed server-side only. `config/sync-config.yaml` gained a `QuestCompensationData` entity (`SourceMapped`, `id_attribute: questId`) and `migrate.py` maps `questCompensations` to it. Scoped to the single zone-13 pair, since zone 13 is the only quest reward table this project has ever modified; a new zone needs its pair added or the sync skips it silently. Zone 13 server-to-client reward parity went from 25 divergent quests to 0
- Client shard `QuestCompensationData-00012.xml` 77 -> 84 quests: 15 quests regained their `assassin`/`fighter`/`glaiver` rows (64 item rows, plus the `engineer` row on 1310), 1353-1358 and 1387 gained their reward blocks outright, and 1380/1381 corrected from a stale 5 gold / 50 XP to the server's 150 / 2100. Zero rows lost on any pre-existing quest. Live-validated
- Quests 1361-1368 lost their vestigial client-side 5 gold / 50 XP stubs, matching the server's empty stubs; none of the eight has a quest file in either era, so none can be accepted
- Patch 002 replayed at 68 specs / 9149 ops / 0 failed / 0 warnings; `dungeon_audit.py --dungeons 9037` and `audit_class_gates.py --zones 13,64,213,436` both exit 0
- Client published `0.1.0-dev.37` (16 new chunks / 57.16 MiB / 19,445 reused, merkle `7f58970177`). No server leg: the reward table was already correct and deployed, which is why the payout worked while the log did not
- New `docs/plans/questcomp-client-sync.md` carries the content-verified full 153-pair server-file-to-client-shard mapping for when another zone's rewards come into scope

### Infrastructure
- datasheet-domain: `loot-system.md` and `entity-map.md` corrected. The blanket "all compensation entities are server-only" claim holds for CCompensation/ECompensation/FCompensation/ICompensation but was false for QuestCompensation, and it is what put `questCompensations` at `None` in the sync map. New `QuestCompensation has a client leg` section documents the two-source split: the accept dialog is fed by `S_DIALOG.questRewards`, the quest log reads the client shard, and `S_QUEST_INFO` carries no reward fields at all
- `tools/migrate/README.md` sync table, `ZONE-PORT-PLAYBOOK.md` family map, both reward-spec generators (`gen_reward_specs.py`, `gen_v31_reward_specs.py`), and three spec headers corrected to drop the same claim

## 2026-07-25

### Content
- Patch 002 re-applied in full from the committed baseline `789fec28` (61 specs / 9071 ops / 0 failed / 0 warnings) with the fixed DSL, then full client sync (`--no-narrow`, 20 entities). The hand-repaired `QuestData/001303|001380|001381|001387.quest` are retired: those files are now generated output, and specs are again the sole authority over both datasheet trees
- Acceptance diff of regenerated 1380/1381/1387 against the hand-repaired oracle: 14 missing nodes, 0 extra, identical on all three quests, every one a documented exclusion (`Header/위치` x3, `Body/보상`=0, `진행조건/제한시간`, `반복횟수`, `수행지역`, `추가보상`, `특수가이드`, `DesignersNote`, and the four body nodes that are XSD-invalid if scaffolded empty). All four loader-dereferenced entry children present on every quest; every task chain ends with the empty `<다음Task />`
- Ninja live-validated on the generated files (offer, briefing, hunt, turn-in, 1303 unlock), so the DSL structural fix is closed end to end. Brawler, Valkyrie, and the wrong-class negative case remain unwalked
- Deployed: server 60 files hash-verified to the dev box; client packed, installed, and published to R2 as `0.1.0-dev.34` (15 new chunks / 57.12 MiB / 19,446 reused, merkle `44d3373129`), the first dev release aimed at remote testers
- Element order on created quests proven NOT fatal: the regenerated quests carry three child sequences absent from the whole corpus and the loader accepts them (`docs/dsl-requests/2026-07-25-created-quest-element-order.md`, downgraded to cosmetic)
- Spec `002/18-iod-newclass-training.yaml` header corrected: the `BLOCKED ON DSL` banner removed, and the false claim that ConditionTask `learnSkill` ids cannot be authored replaced with the actual reason the 5-task v31 beat is dropped
- **Second story-spine soft-lock found live and closed:** a Ninja cleared 1384 (Getting to Know the Garrison) and the spine still dead-ended at the class-split pair 1382/1383 "Gathering Your Strength" (both from Milene, gating 1331 "Climbing through the Ranks"), which admits only the classic nine classes. New spec `002/19-newclass-quest-gates.yaml` opens the physical variant of each affected group: 1382 and 1351 (IoD) and 6306 (Velika). Ninja live-validated end to end
- Gunner (`Engineer`) was missing from the same groups and is added with them: vanilla itself put Engineer in 1382 but never in its sibling pair 1351/1352 nor in the Velika pair. Quests 6304/6307 match the pattern but are sentinel-disabled in both eras and were deliberately left untouched; Reaper (`Soulless`) is out of scope (starts elsewhere at a higher level)
- Established: this class of defect **cannot** be caught by diffing against the restoration source. v31 carries byte-identical class lists, so the restore is faithful while still excluding every class added after that era; it emits no load warning, and it hides from any live test that uses a class of the original era
- Deployed and published: server 63 files hash-verified; client `0.1.0-dev.35` (14 new chunks / 55.66 MiB / 19,448 reused, merkle `5e0ab434c0`)
- **Acharak no longer spawns outside the Tainted Gorge Garrison.** New spec `002/21-iod-acharak-ruins-cleanup.yaml` retargets 4 spawns in habitat group 1300038 (Mysterious Ruins) from named-boss template 1002 to generic 901, so quest 1309's kill-one target exists only where its journal string 1309006 says. The padding wave had drawn 1002 from the v17 roster `[5, 901, 1002]`, putting 8 mobs that display as "Acharak" some 19,400 units from the garrison. The named-unique roster (1001 / 1002 / 1003 / 1004) now matches v31 exactly; the four spawns keep their positions, density, model, AI and aggro attributes (901 shares shapeId 300650 / basicActionId 3006500 / aiid 31) and lose only the level-8 boss profile. Client `StrSheet_NpcLoc` 13/1002 regenerated from 6 waypoints back to the v31 client's 2. Live-validated
- Client `TerritoryData` family fully synced for the first time, a side effect of patch 002's first territory-touching spec: 409 shards rewritten, of which 368 are attribute reordering only and 41 carry real content (+2031 net lines), led by HZ 1022 (+889), HZ 437 (+550), HZ 152 (+439), HZ 84 (+313). This closes standing server-to-client gaps, notably the 8 groups / 63 territories of dungeon 437 (Sorcha) that patch 001 uncommented server-side by hand and that had never reached the client. Packs clean, no W602, `dungeon_audit.py --dungeons 9037` PASS
- Deployed and published: server 64 files hash-verified; client `0.1.0-dev.36` (14 new chunks / 57.16 MiB / 19,446 reused, merkle `468a2435e3`)
- **Sorcha dungeon 9037 (Tainted Gorge Bridge) is a five-player encounter.** `002/22` restores the v31 entry conditions (`party=1` + `maxMemberCount=5`, replacing the patch-001 `solo` + `maxMemberCount=1` narrowing, retiring that divergence row); `002/23` clears `partyCantWork="true"` from entrance WorkObject 134, which had been inherited from cloning the level-65 donor template 125 and blocked grouped players outright
- **Wave encounter rebuilt across three live-tuned passes.** Final state: 19 wave templates at v31 x100 HP / x600 atk (`balance/zone-0437-tainted_gorge_bridge.yaml`), effective population 314 -> 834 across 50 spawn tasks, Sorcha 1,082,344 hp and Guardians 311,719. Pass 3 cut Sorcha 20% and pass 3b reverted it after live play; the population increase was kept
- **23 dormant wave territories wired into the dungeon script** (`002/25`): both stage-rear groups (43700012, 43700013) and all 15 remaining stage-3 territories, taking stage 3 from 10 spawn points to 25. Every insert splits an existing `next: time` delay so stage totals hold; the stage-3 window uses 60s of the slack before the 420s guard, so the chain ends at 400s. Authored content, not restoration: our wiring matched v31 exactly (3 EventGroups / 27 spawn tasks / identical territory ids) before this, so the 33 dormant territories were BHS authoring more geometry than the script used
- New generator `tools/dc-restore/gen_sorcha_wave_density.py` emits the per-row spawn-count spec (`002/24`) with per-stage factors, reading baselines from git HEAD so re-running never compounds. New package file `packages/npc-ids/zone-437-tainted-gorge-bridge.yml` (`TGB` prefix, registered in `index.yml` and the README zone table)
- Both dungeon 9037 gates pass at every step: `dungeon_audit.py --dungeons 9037` exit 0, and territory references resolved 27 -> 50 as the wiring grew. All of this work is server-only (`balanceProfiles`, `territorySpawns`, `dungeonDatas`, `workObjects` carry no client-visible fields here), so no client build was republished after `0.1.0-dev.36`

### Infrastructure
- `tools/dc-restore/audit_class_gates.py` added: class-gate coverage gate, read-only, exit 1 on any gap. Judges coverage per variant GROUP (keyed on zone + giver + story group, since one NPC hands each class its matching variant), so caster-only quests are not flagged when their physical sibling covers the class; per-class training quests report `SINGLE` and sentinel-disabled groups report `DISABLED`. Wired into the `content-restoration` pipeline as step 4, exit 0 required before any deploy touching restored quests. Both the IoD and patch-002 zone sets PASS
- `content-restoration` skill gained two lessons: the era-roster class-gate hazard, and that removing an op from a spec does not revert the file it already wrote (a narrowed spec leaves stale values that no later apply reconciles; `git checkout --` the affected files and re-derive)
- datasheet-domain: `quest-system.md` gained a Class Gating section (allowlist `클래스` block, 13 PascalCase identifiers, variant-group pattern, era-roster hazard); `quest-task-reference.md` gained journal icon resolution (body-level `아이콘지정` is DeliverInjectedItem-only at 204/204 valued, every other task type derives the icon from the item template) and corrected the `스킬습득` trigger from "unused in dataset" to 11 task bodies in live use
- datasheetlang: quest creation structural completeness shipped and adopted (`fd3f1d27` entry-child scaffolding on all 22 repeated-entry containers, `a59caf4e` mechanically derived structure contract + W504, `01823e2f` quest/task header skeletons, `2c306261` empty chain terminator, `2ab73e85` E427 apply-time element-name validation against the client schema, `b5372490` HuntAndCollect entry fields, `12e35c04` in-place prerequisite replace). Binary in use: `1.0.0+5f90181c`
- Patch Application Discipline gained binding rule 4 in `reforged/CLAUDE.md`: the datasheet trees are generated output, hand-edits there are temporary probes that an apply is expected to destroy, and no apply/sync/deploy may be held back to protect them. `tools/migrate/README.md` restated accordingly (`git checkout .` is always safe before a re-apply)

- datasheet-domain: three attribute descriptions corrected where the docs stated inferred intent rather than observed behaviour, each caught by data or live play contradicting the text. `npc-system.md`: `name` is an internal label, NOT the display name (98.5% of 15,630 templates differ in kind; 1,600 name/zone groups are shared by 2+ templates, 733 of them rendering as different creatures), plus a new Template Identity section covering variant families sharing a `shapeId` and a completed `playStyle` enum (`zarcoBoss`, `creature`, `servant` were missing). `dungeon-system.md`: `party` is a mode flag, not a headcount requirement (5 dungeons pair it with `maxMemberCount=1`), and `notSolo` is the actual solo block. `work-object-system.md`: `partyCantWork` blocks the interaction outright rather than restricting outcome distribution

### Blockers resolved
- MCP request delivered and adopted: `profile_npc`, `resolve_position`, `audit_quest_gates`, `find_dormant_blocks` and `datasheet_freshness` are live on both datasheet servers, filed as `docs/mcp-requests/2026-07-25-npc-profile-and-spawn-filters.md` after the Acharak investigation cost ~11 of 40 tool calls in avoidable overhead
- DSL request `2026-07-25-dungeon-condition-order-and-update.md` delivered and CLOSED: `d5250b5b` rejects create-only fields under `update.changes` with E209 (the silently-inert case), `334f10fd` keeps a replaced nested collection at its original document position (retiring the all-conditions-last shape that occurred in 0 of 203 corpus dungeons). Full dry runs on the new binary `1.0.0+334f10fd` are clean on both patches, and no spec needed changing
- DSL request filed, open: `2026-07-25-territoryspawn-party-key-silent-noop.md`. A `territorySpawns.update` whose composite key omits `partyId` for a party-nested spawn matches nothing, reports as applied with zero warnings, and passes op-count reconciliation; caught only by a post-apply mob-count gate (609 instead of 616)
- 7 quest DSL requests closed and deleted after verification against the shipped binary: `2026-07-24-created-quest-structural-completeness.md` (the world-server crash blocker), `2026-07-24-visittask-completion-item-nodes.md`, `2026-07-23-quest-class-gate.md` (all 3 issues), `2026-04-16-conditiontask-learnskill-skillid.md`, `2026-04-17-visit-task-completion-button-text.md`, `2026-04-16-quest-task-visit-and-condition-body-issues.md`, `2026-04-17-visit-task-npcid-written-to-outer-container.md`
- `2026-07-25-created-quest-element-order.md` filed as the one carry-forward from that set, then downgraded to cosmetic by the live boot

## 2026-07-24

### Content
- IoD new-class story-spine soft-lock fixed and live-validated on a Ninja (Making the Rounds -> class training -> 1303): spec `002/18-iod-newclass-training.yaml` adds class-gated training quests 1380 (Assassin), 1381 (Fighter), 1387 (Glaiver) as 3-task Visit/Hunt/Visit chains on the live cast (Dulari 213,1017 / Junia 213,1023 / Nivek 213,1115; 2100 xp / 150 gold; StoryGroup 1), and extends quest 1303's OR-prerequisite from 9 to 12 entries. Brawler and Valkyrie untested in game
- Client `Quest/Quest.xsd` widened from 10 to all 13 classes (`Quest_Header_수행조건_클래스` gained Assassin/Fighter/Glaiver element decls + type defs); committed client `09ea033f`
- Server `QuestData/001303|001380|001381|001387.quest` are hand-repaired working-tree state (structural clones of 001371 and 001303, values substituted): patch 002 cannot be re-applied until the DSL structural-completeness fix lands, or the world server crashes on next restart
- Established: quest 1303 loads with 12 prerequisites (previous corpus maximum was 9, held by 1303 in v31); no prerequisite cap exists

### Infrastructure
- `server-load-diagnosis` skill added: dev-box crash artifacts (UTF-16LE console log, `.crash`, dumps), reading the symbolized call stack past the crash reporter's own secondary fault, classifying loader lines against a known-good boot, the UTF-8 BOM invariant, and the one-variable-per-boot bisect protocol
- `new-spec` skill gained the clone-a-donor-record rule for created records; `apply-spec` gained the `deploy_dev.py` git-dirty-delta revert trap; `learn` routing table gained a world-server-boot row; `quest-live-test` cross-references the new skill from its restart precondition
- `.references` and `.references.example`: `dev_server_root` key added (console logs and crash dumps on the dev game server)
- datasheetlang: `b437a532` (quest task body required-container scaffold) and `1c31ff16` (`requirements.classes` class-gate field) adopted; both in use by spec 18

### Blockers resolved
- `2026-07-24-visittask-completion-item-nodes.md` delivered (datasheetlang `b437a532`) and adopted; the request itself carries a correction: the `노드를 찾을 수 없습니다` lines it cited are warnings emitted on every healthy boot, not the load blocker
- `2026-07-23-quest-class-gate.md` Issue 3 (client sync dropping `<클래스>` children) worked around permanently by the committed client Quest.xsd widening

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
