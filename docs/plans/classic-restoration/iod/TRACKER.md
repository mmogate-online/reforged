# IoD Restoration Tracker (v31-primary redo)

Pilot zone under `../DOCTRINE.md`. Supersedes the retired `docs/plans/iod-alpha-content-loop/`
pilot (its TRACKER and data artifacts remain readable as reference; its doctrine does not apply).

Last updated: 2026-07-25 (Sorcha dungeon rebuilt as a five-player encounter and live-tuned over
three passes; Acharak spawn leak closed. Patch 002 still OPEN).

## Session handoff (2026-07-25, third session): Sorcha dungeon + Acharak

Specs repo COMMITTED (not pushed). Server and client-dc datasheet repos deliberately left
UNCOMMITTED: patch 002 is still open and closes with one commit per repo, per the patch
discipline. Working trees hold the full patch: server 68 dirty, client 4955 dirty.

### Shipped and live-validated this session

1. **Acharak no longer spawns in the Mysterious Ruins** (spec `002/21`). Quest 1309 is a kill-one
   on named boss 13,1002, but the patch-001 padding wave drew that template from the v17 roster
   `[5, 901, 1002]` into habitat group 1300038, putting 8 mobs that display as "Acharak" about
   19,400 units from the Tainted Gorge Garrison the journal names. Retargeted to generic template
   901 (same shapeId/basicActionId/aiid, so density and appearance hold). `gen_npcloc.py --prune`
   returned the map marker to the two v31 garrison waypoints. Client published `0.1.0-dev.36`.
2. **Sorcha dungeon 9037 opened to a party of five** (specs `002/22` and `002/23`). Two gates had
   to fall: DungeonData conditions (`solo` + `maxMemberCount 1` -> the v31 `party=1` +
   `maxMemberCount=5`, retiring a patch-001 divergence) and then, found live, the entrance portal
   itself (`partyCantWork="true"` on WorkObject 134, inherited from cloning the level-65 donor 125).
3. **Encounter rebuilt over three live-tuned passes** (spec `002/24` + generator, spec `002/25`,
   `balance/zone-0437`). Final state: waves at v31 x100 HP / x600 atk, effective population
   **834** across **50 spawn tasks**, stage 3 fully wired at 25 spawn points, Sorcha 1,082,344 hp,
   Guardians 311,719 each.

### Tuning history, so it is not rediscovered

| Pass | Change | Live verdict |
|---|---|---|
| 1 | island parity (v31 x10 HP / x60 atk), 308 defined | far too weak for geared characters |
| 2 | stats x10, population x2 (616 defined / 314 effective), rear groups 43700012+43700013 wired | cleared by TWO players, but the flanking spread was praised: "we had to split our forces" |
| 3 | population to 834 effective (stage 3 fully wired, 25 points), Sorcha -20% | good, but the mob increase plus the HP nerf together were too much |
| 3b | Sorcha nerf REVERTED to x93.75, population kept | current state |

Standing guidance: the population is the expressive lever, not the escort's HP. x75 on Sorcha was
tried and rejected; `startAggro` (70 flanking / 150 stage closers) and the cluster spacing in spec
25 are the untried knobs.

### Calibration caveat, recorded deliberately

These numbers are tuned for geared test characters, NOT for a level 8-10 player walking quest 1346
normally, for whom the dungeon is now unclearable. Quest 1346 is 최소레벨 8 and this is classic
level-8 content. If it should be hard for geared players and fair for levelling ones, the lever is
a difficulty mode or level scaling, not the base stat block. **Revisit before launch.**

### Structural findings worth keeping

- **Only 27 of 60 wave territories were ever wired.** The dungeon script spawns by territory and
  the EventTasks carry no count of their own, so density flows through, but 33 territories were
  activated by nothing. Our wiring matched v31 exactly, so this was BHS authoring more geometry
  than the script used, not a restoration gap. Specs 25 wired 23 of them (both stage-1/2 rear
  groups plus all of stage 3); the finale set piece 43700015 is deliberately still dark.
- **`party` is a mode flag, not a headcount requirement** (5 corpus dungeons pair it with
  `maxMemberCount=1`); `notSolo` is the actual solo block. Domain KB corrected.
- **`partyCantWork` blocks the interaction outright**, it does not merely restrict outcome
  distribution. Domain KB corrected.
- **`NpcData.name` is an internal label, not the display name** (98.5% differ in kind). This is
  what caused the Acharak defect. Domain KB corrected, and `npc-system.md` had actively wrong text.

### Next

1. **Live-test the current tuning** if not already done: a party of 2 to 5 entering together, stage
   3 reading as pincers rather than a stream, and Sorcha's HP floor at the 7-minute mark.
2. Continue IoD polishing (the stated purpose of the next session). Open with
   `/prime-classic-restoration iod`.
3. Still outstanding from earlier sessions: live-test Brawler + Valkyrie and the wrong-class
   negative case on the new-class spine.
4. Then close patch 002 with one commit per datasheet repo.

## Session handoff (2026-07-24, second session): new-class spine LIVE

The story-spine soft-lock for Ninja/Brawler/Valkyrie is **fixed and live-validated**: a Ninja
advances Making the Rounds -> Ninja Training -> 1303. Brawler and Valkyrie are structurally
identical (same donor clone, only class and string ids differ) but were not walked in game;
the negative case (Dulari refusing a wrong-class offer) is also untested.

### Root cause of the three-day block

Not the DSL VisitTask completion-item gap (that message is a **warning**; it appears on every
healthy boot for quests 1353-1358). The real fault: DSL-created quests omit nodes present in
100% of the corpus for their task type, and `QuestTemplate::Validate` dereferences them, so the
world server dies with a bare `access violation ... Write to 0x0` during datasheet validation:
no message, no quest id, no file name. Missing nodes sat at several nesting depths
(`보상`, `진행조건` at body level; `연출Id` in `방문그룹/방문그룹`; `조우시대사`/`사망시대사`/
`이상상태조건` in `몬스터지정/몬스터지정`), so auditing one level at a time cost six
deploy/restart cycles.

**What worked:** rebuilding the quests as structural clones of files the server already loads
(001371 for header + `방문Task` bodies, 001303 for the `사냥Task` body) with only values
substituted. Clone known-good structure; do not synthesize and patch.

### Settled facts (do not re-litigate)

- Quest 1303 loads fine with **12** prerequisites (old corpus max was 9). There is no cap.
- Class gates for Assassin/Fighter/Glaiver are fine server- and client-side; existing v92
  quests 18353/118301/18352/118302 already ship them.
- The server rejects any datasheet without a UTF-8 BOM (`UTF8 파일인지 확인`). DSL writes it
  correctly; a repair script that drops it will hard-fail the load.
- `deploy_dev.py` mirrors only files that differ from git HEAD, so reverting a file leaves the
  stale copy on the dev box. Push reverted files explicitly.

### Current state

- Client `Quest/Quest.xsd` 3-class widening: **committed** (`09ea033f`, client repo). The
  `git checkout .` hazard is gone.
- **The DSL structural fix SHIPPED (2026-07-25) and the pause is over.** Verified against the
  released binary `1.0.0+5f90181c` on a scratch datasheet, from a create-only probe spec: all
  four proven entry children emit (`연출Id` on each visit target, `조우시대사` / `사망시대사` /
  `이상상태조건` on each monster target), plus the quest and task header skeletons, the
  VisitTask completion-item bags, the empty `<다음Task />` terminator, and the class gate. The
  in-place visit-target update keeps its sibling nodes. E427 now refuses an element name the
  client schema cannot carry.
- **Patch 002 re-applied from the baseline and the acceptance diff PASSED (2026-07-25).**
  `migrate --patch 002 --no-narrow`: 61 specs, 9071 ops, 0 failed, 0 warnings, reads pinned to
  server HEAD `789fec28`. The hand-repaired files are gone, replaced by generated output, which is
  the intended outcome: the datasheet trees are generated artifacts and the specs are authoritative.
  Acceptance against the off-repo oracle copies: **14 missing nodes, 0 extra, identical on all three
  quests**, exactly the documented exclusion set (`Header/위치` x3, `Body/보상`=0,
  `진행조건/제한시간`, `반복횟수`, `수행지역`, `추가보상`, `특수가이드`, `DesignersNote`, and the four
  XSD-invalid-if-empty body nodes). All four proven entry children present on every quest
  (`연출Id` x2, `조우시대사`, `사망시대사`, `이상상태조건`), and every task chain ends `('3','')`,
  the empty terminator. Client shards `Quest-00389/00390/00396` carry `Assassin` / `Fighter` /
  `Glaiver` = `적용` and the same empty terminator.
- **Deployed.** Server: 60 files to the dev box, all 60 hash-verified. Client: packed, installed,
  and published to R2 as `0.1.0-dev.34` (15 new chunks, 57.12 MiB, 19,446 reused, `committed=True`),
  so remote testers can pull it.
- **No spec changes are pending.** Every identity value lives in
  `specs/patches/002/18-iod-newclass-training.yaml`, and the structural nodes are scaffolded.
- One residual DSL item, not blocking: `docs/dsl-requests/2026-07-25-created-quest-element-order.md`
  (the create path writes three child sequences that occur zero times in the corpus). Normalizing
  order did not by itself stop the original crash, so this is unproven fatal, and the next boot is
  its test. Note the as-deployed 001303 that booted and passed the Ninja test on 2026-07-24 carried
  the old operator-before-list order, which is evidence against that site being fatal.

### Class-gate soft-lock (found live 2026-07-25, fixed, deployed, LIVE-VALIDATED)

A Ninja completed 1384 (Getting to Know the Garrison) and the spine dead-ended. Cause: the
spine continues `1384 -> 1382 OR 1383 "Gathering Your Strength" -> 1331 "Climbing through the
Ranks"`, and the 1382/1383 pair is class-split (1382 physical: Warrior Lancer Slayer Berserker
Archer Engineer; 1383 casters: Sorcerer Priest Elementalist). Assassin/Fighter/Glaiver are in
neither, so Milene offers nothing and 1331 never unlocks. A Berserker progresses via 1382.

**v31 carries the identical class lists**, so the restoration was faithful and no source diff
could catch it: the defect exists only against today's 13-class roster.

Fixed by `specs/patches/002/19-newclass-quest-gates.yaml` (applied, synced, and deployed
2026-07-25: server 63 files hash-verified, client published `0.1.0-dev.35`):
1382 and 1351 (IoD) and 6306 (Velika) gain the three classes on the physical variant only, so
each class still matches exactly one variant. The same sweep found `Engineer`/Gunner missing
from the 1351/1352 and 6302/6306 groups (vanilla added Gunner to 1382 but not its siblings), so
Engineer was added there too. Quests 6304/6307 look like the same pattern but are
sentinel-disabled in both eras and were deliberately left alone. Reaper/Soulless is out of
scope (starts elsewhere at a higher level).

Regression-checked: node-level diff against the committed baseline shows exactly the added class
children (3 or 4 per quest) and zero removed nodes on all four files; client shards carry the
widened gates; caster variants unchanged.

New permanent gate: `python reforged/tools/dc-restore/audit_class_gates.py --zones <zones>`,
exit 0 required before any deploy that touches restored quests. Both the IoD zone set and the
patch-002 zone set now PASS. It is wired into the `content-restoration` pipeline as step 4.

### Acharak spawn-clarity fix (2026-07-25, applied, deployed, LIVE-VALIDATED, published)

Quest 1309 "Acharak Attacks" is a kill-ONE task on named boss 13,1002 whose journal string
1309006 names one place: "Clear out Acharak and his minions from the Tainted Gorge Garrison."
The patch-001 padding wave (spec 001/15) replicated v17 habitat group 1300038
"태고의 유적지(오칸 순찰)" from the roster recorded in padding-habitat-gaps.md as [5, 901, 1002],
so 4 of its 12 fences drew template 1002 at spawnCount 2: EIGHT extra Acharaks in AreaData
section 31 (Mysterious Ruins), about 19,400 units from the garrison.

The trap: `desc` is an internal comment, and NpcData_13 calls template 1002 "오칸" (Orcan). The
player-visible name comes from StrSheet_Creature keyed by (hz, templateId), where 13/1002 is
"Acharak". So all 8 ruins mobs displayed as Acharak AND satisfied the kill-1 task, and the
client NpcLoc marker set had grown from the v31 client's 2 waypoints to 6.

**Fix (spec `002/21-iod-acharak-ruins-cleanup.yaml`, user decision option B):** retarget the four
spawns from 1002 to generic template 901 rather than deleting the territories, preserving the
live-tuned patrol density from the spec 001/15 regen. 901 is the same creature generically:
shapeId 300650, basicActionId 3006500, aiid 31, internal name 오칸, differing only in
playStyle (basic vs zarcoBoss) and level (7 vs 8, which also removes a level outlier from an
otherwise level-7 patrol). Bounded side effect: 901 goes 33 -> 37 territories; its only quest
reference is 1311 ("Thin the orcan ranks", location-neutral).

Verified: server diff is exactly 4 lines (`npcTemplateId` only, every other attribute
byte-identical); the named-unique roster (1001/1002/1003/1004) now matches v31 exactly;
`gen_npcloc.py --prune` brought 13/1002 back to exactly the 2 v31 garrison waypoints. Batch
`migrate --patch 002 --no-narrow` = 63 specs / 9078 ops / 0 failed / 0 warnings. Both gates
exit 0 (`dungeon_audit.py --dungeons 9037`, `audit_class_gates.py --zones 13,64,213,436`).

A sweep of every HZ-13 quest-target template confirmed 1002 was the ONLY named unique whose
footprint diverged from v31. Eight other templates gained padding groups but are generic
kill-5-to-48 targets with location-neutral journal text, which is what the density restore was for.

**Client-side collateral, accepted by user decision:** this was the first patch-002 spec to touch
a territory entity, so it triggered the first full sync of the `TerritoryData` family. 409 client
shards were rewritten: 368 are pure attribute reordering (net 0 lines, proving DSL had never
written them), and 41 carry real content (+2031 net), led by HZ 1022 (+889), HZ 437 (+550),
HZ 152 (+439), HZ 84 (+313). These are pre-existing server-to-client divergences the full sync is
now closing, NOT anything spec 21 caused; HZ 437's 8 groups / 63 territories are exactly the block
patch 001 uncommented by hand server-side, which never reached the client. Shipped rather than
hand-reverted, per the rule that the datasheet trees are generated output. Packs clean, no W602.

Deployed 2026-07-25: server 64 files hash-verified; client packed and installed. **LIVE-VALIDATED
by the user**, then published to R2 as `0.1.0-dev.36` (14 new chunks, 57.16 MiB, 19,446 reused,
`committed=True`), so remote testers can pull it. Note the fix needs BOTH legs: the spawn retarget
is server-authoritative and rides the world restart, but the NpcLoc marker correction is
client-only data and lands only with the new `.dat`.

### Next

1. Live-test Brawler + Valkyrie and the wrong-class negative case (Dulari refusing a wrong-class
   training quest). Cheap, and the negative case is the only untested code path. Everything else
   on the new-class spine is validated: a Ninja now walks 1304 -> class training -> 1303 and
   1384 -> 1382 -> 1331 end to end.
2. Spot-check dungeon 437 (Sorcha, quest 1346). Its client shard gained 8 groups / 63 territories
   in the 2026-07-25 full TerritoryData sync, content that had only ever existed server-side. It
   passes `dungeon_audit.py --dungeons 9037` and packs clean, but it has never been walked with
   matching client data.
2. Then close patch 002 in one commit per repo, per the patch discipline.
3. Continue quest polishing in a fresh session: open it with `/prime-classic-restoration iod`,
   which loads the doctrine, this tracker, the divergence log, and the current state of the three
   working trees, then hands off to `content-restoration`.

### Proven by controlled experiment (2026-07-24), do not retest

Removing only the four repeated-container entry children from 001380, with 001381/001387 left
intact as controls, crashes the loader at the same address and site; restoring them boots. So
children of `방문그룹/방문그룹` and `몬스터지정/몬스터지정` are hard dereferences, while
body-level bags only warn. Corpus frequency does not classify a node: two nodes at exactly 100%
presence behave differently by read site. The DSL request that carried the full write-up was
closed and deleted on 2026-07-25 once the fix shipped; the finding survives here, in the
`new-spec` skill lesson "Clone a donor record the server already loads", and in the DSL repo's
derived contract (`schemas/Quest.structure-contract.json`).

## Session handoff (2026-07-24 close, SUPERSEDED by the entry above)

Fixes the story-spine soft-lock for Ninja/Brawler/Valkyrie. Those classes had no v31 IoD
training quest, so they stalled right after 1304 (Making the Rounds): quest 1303 gates
behind an OR of the nine class training quests 1371-1379, and the new classes matched none.
Gunner is already covered (1379 = `Engineer`); Reaper (`Soulless`) excluded by doctrine.
Full state also in memory `project_iod_newclass_spine_deploy_held`.

### Spec (patch 002)
- `specs/patches/002/18-iod-newclass-training.yaml`: three new class-gated training quests
  1380 Ninja (`Assassin`), 1381 Brawler (`Fighter`), 1387 Valkyrie (`Glaiver`); 3-task
  Visit -> Hunt -> Visit reusing the live cast Dulari 213,1017 / Junia 213,1023 / Nivek
  213,1115 (no new spawns); extends 1303's OR-prereq to 12 quests; strings + dialogs
  (`<PCCLASS:lcase>` token) + rewards (2100 xp / 150 gold) + StoryGroup-1 registration.
  The v31 5-task "learn a skill" beat is dropped (DSL cannot author ConditionTask
  learnSkill ids). Validates clean (37 ops); full patch-002 batch clean (61 specs / 0
  failed / 0 warnings).

### Status: DEPLOYED but the dev WORLD SERVER FAILS TO LOAD
- `migrate --patch 002 --no-narrow` applied to both working trees; server pushed to dev
  (60 files verified); client packed + installed. NOT committed (mid-patch-002; `--publish`
  to R2 NOT run).

### Three DSL gaps hit in sequence (all filed in docs/dsl-requests/)
1. Class-gate APPLY field: DELIVERED (DSL commit 1c31ff16, `requirements.classes`).
2. Class-gate CLIENT-SYNC (`2026-07-23-quest-class-gate.md` Issue 3): the XSD pre-filter
   dropped the class children client-side. RESOLVED by adding Assassin/Fighter/Glaiver to
   the client `Quest/Quest.xsd` complexType (it was only 10 classes wide). DSL also shipped
   W602 (warn on XSD-dropped data, commit 8bd7aaba). *** The Quest.xsd edit is UNCOMMITTED
   and a `git checkout .` reverts it: RE-APPLY after any revert, and COMMIT it as the first
   action once live-validated (user directive). ***
3. VisitTask completion-item nodes (`2026-07-24-visittask-completion-item-nodes.md`):
   CURRENT BLOCKER. The DSL `TaskDecomposer` only writes `<완료시삽입아이템/>` /
   `<완료시삭제아이템/>` when the item list Count>0, so a created `방문Task` omits them; the
   SERVER loader requires them present even when empty (`조건Task` / `사냥Task` do not need
   them). Server error: "Quest[1387]: ...완료시삽입아이템...노드를 찾을 수 없습니다". User
   chose to WAIT for the DSL fix (no temp patch, no revert), so the dev server stays down
   until it lands.

### Next session (when the DSL VisitTask fix ships)
1. `git checkout .` both repos, then RE-APPLY the `Quest.xsd` 3-class edit (checkout
   reverts it).
2. `migrate --patch 002 --no-narrow`; verify server `방문Task` bodies now carry the empty
   completion-item nodes AND the client class gates stay populated.
3. Deploy server + client; user restarts the dev world server.
4. Live-test one Ninja + Brawler + Valkyrie: Making the Rounds -> Dulari offers the class
   training quest (and NOT to wrong classes) -> complete -> 1303 unlocks -> 1329.
5. FIRST commit the client `Quest.xsd`.

## Session handoff (2026-07-22 close): IoD loot fix + patch-002 loot merge

Live test of the patch-002 merged loot is POSTPONED to the next session. Current state below.

### Done + committed (patch 001 drop fix)

- **IoD drop bug CLOSED, live-validated by the user.** Root cause: v92 commented out the entire v31
  ECompensation_13 natural table, and IoD's CCompensation bags are root ItemBags with no
  ClassItemBag wrapper (they drop to no one, per loot-system rule 4); only ECompensation actually
  drops. Old spec 20 had restored only 300945, so every other IoD mob dropped nothing in live tests.
- **Fix:** new `tools/dc-restore/gen_ecomp_restore.py` regenerated
  `specs/patches/001/20-iod-ecomp-drops.yaml` as the FULL v31 ECompensation_13 table (43 mobs = 49
  minus 6 empty stubs; gold + mats + paverunes + designs + First Expedition, verbatim wValue/t; no
  divergence). Confirmed working live via `/@drop_all_items`.
- **Commits (LOCAL ONLY, not pushed):** server datasheet `789fec28`; specs `277f94a` (generator +
  spec 20 + tracker) and `ff698da` (spec 22 removal).

### Done, NOT committed (patch 002 loot merge, applied + deployed to dev for testing)

- **Merged loot:** `specs/patches/002/17-iod-loot.yaml` regenerated as the UNION of v31 (gold as
  priority + classic mats/paverunes/designs/First Expedition, native bag ids <= 20) and the reforged
  item drops (Alkahest/Feedstock/crystal/dyad/infusion boxes, Kugai tokens; reforged bag ids offset
  by +100 to avoid id collision). User design call: keep BOTH economies.
  `tools/iod-loot/generate_iod_loot.py` now reads the v31 ECompensation_13 as a second source.
- **Deleted patch-002 specs (audit outcomes):** `22-iod-disable-flight-manager` (voidSpawn on
  Leiyane broke quest 1317 turn-in; flight already grounded by patch-001 spec 13), plus
  `19-iod-strip-legacy-ecomp` and `21-iod-strip-ccomp` (disposed with the merge: stripping
  CCompensation would remove the one working class-gated Mote drop, and the 7001-7009 / 9001 stubs
  are harmless).
- **Applied + deployed:** `migrate --patch 002` = 60 specs / 9034 ops / 0 failed / 0 warnings.
  Server pushed to dev (50 files, hash-verified). Client repacked + installed to the local game
  client. Verified applied: 300945 carries all 14 bags (v31 First Expedition + reforged); reforged
  items (602176 / 96108 / 602190 / 95216) now exist in ItemTemplate.
- **Working tree is UNCOMMITTED** (throwaway TEST deployment; per patch discipline patch 002 commits
  only on close). `server_datasheet` + `client_datacenter` hold the full patch-002 diff; the specs
  repo has the 19/21 deletions staged plus the spec 17 + generator edits.

### Next session

1. **Restart the dev world server** (manual; datasheets load at startup only).
2. **Live-test the merged loot:** QA `/@drop_all_items on`, kill IoD mobs, confirm both economies drop:
   - Terron Lama 300945: v31 First Expedition set + Wonder Ring + mats AND reforged
     Alkahest/Feedstock/crystal/dyad/infusion, plus gold.
   - Regular mobs (Pigling / Dwarf Orcan / Kariagon): v31 gold + classic mats AND reforged boxes.
   - Kugai 1004: v31 gold/mats/designs + reforged + Kugai's Crest tokens.
   - IoD mobs are balance-multiplied (x10 HP / x60 atk), so they are tankier; pair with GM damage.
3. **After the test:** if good, decide on committing/closing patch 002 (still mid-audit for its other
   systems); if not, `git checkout .` in `server_datasheet` + `client_datacenter` reverts the dev
   test state back to the committed patch-001 baseline.

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
| 7: v17 padding phase | LEVEL 1 + POLISH + REWARD FIX + DROP TABLE APPLIED 2026-07-21; FULL ECOMP RESTORE DEPLOYED 2026-07-22 (live test pending) | FULL LOOT RESTORE + PATCH-002 AUDIT (2026-07-22): audited the patch-002 IoD specs against the committed patch-001 baseline. Deleted `specs/patches/002/22-iod-disable-flight-manager.yaml` (voidSpawn on Leiyane 213,1016 would break quest 1317's VisitTask turn-in; flight is already grounded by patch-001 spec 13, so it was redundant AND harmful). Root-caused why patch-001 mob loot never dropped in live tests: v92 commented out the entire v31 ECompensation_13 natural table, and the visible CCompensation bags are ROOT ItemBags (no ClassItemBag wrapper) which the engine gives to no one (loot-system rule 4); only 300945 dropped because old spec 20 gave it an ECompensation. FIX: new generator `tools/dc-restore/gen_ecomp_restore.py` regenerates spec 20 as the FULL v31 ECompensation_13 table (43 mobs = 49 minus 6 empty stubs; gold + materials + designs + First Expedition, verbatim wValue/`t`; no divergence, pure v31-primary completion). `migrate --patch 001` clean (23 specs, 0 failed, 15 idempotent-delete warnings); working-tree delta = `ECompensation_13.xml` only (+519 lines) after reverting 3 cosmetic element-reorder artifacts (TerritoryData_13/_213, WorkObjectData) to committed HEAD; client 0 drift (ECompensation server-only). Deployed to dev + hash-verified (1 file); client NOT republished (server-only, DC byte-identical). Confirmed via DSL schema that `eCompensations.upsert` = full-entry replace, so patch-002 spec 17's upsert on 300945 WILL wipe First Expedition drops. The patch-002 reforged loot must MERGE into these restored v31 bags, not overwrite. NEXT: user restarts dev world server, live-test regular IoD mobs (Pigling/Dwarf Orcan/Kariagon/Kugai/Terrons) now drop gold + materials; then this restored table is the "vanilla" base for the patch-002 reforged-merge. PRIOR | SESSION CLOSE (2026-07-21): spec 20 restores the v31 ECompensation_13 entry for Corrupted Theron Chief 300945 (First Expedition drop bags, v31 1:1, not class-scoped, no divergence); batch 21 specs / 2148 ops / 0 failed; hand edit re-applied; server push 44 files verified; client stays 0.1.0-dev.27 (spec 20 is server-only). Decisions 6 (level caps stay authentic) and 7 (drop table restored, 1310 stays OUT) recorded. NEXT SESSION: live-test checklist = armor payout (1305 or side quests 1322/1325/1326/1330/1347), First Expedition drops from 300945 at the gorge edge, Orcan density (1349 pace), 1348/1319 mob availability, Ramun click (1327), single politics NPCs, Sorcha auto-entry + defense + fail-eject (1346), repeatable cycle 1341 (level 8-12 char). PRIOR | REWARD FIX (2026-07-21): user live report (weapons paid, armor never) exposed that spec 04's semicolon-joined class rows (workaround for the DSL templateId-keying collapse) are not an engine format (0 occurrences in stock v92/v31); filed docs/dsl-requests/2026-07-21-compensation-class-row-collapse.md; DSL delivered d79aca90 (identity templateId+class+race, E207 rejects semicolons) + 363ed076 (EventTask npc field, E426); generator reverted to native per-class emission, spec 04 regenerated (65 ops; 1305 = 48 rows / 12 classes; 0 semicolons anywhere), spec 19 regained the npc="437,1001" attribution; batch replayed 20 specs / 2147 ops / 0 failed; RestoreTargetQuest hand edit re-applied (dsl-request issue 3 still open); NpcLoc 146; server push 43 files verified; client 0.1.0-dev.27. First Expedition armor (incl. Cuirass 15022) now actually pays from story 1305 and side quests 1322/1325/1326/1330/1347. PRIOR | POLISH WAVE (2026-07-21, from first live test): spec 15 regenerated 509 ops (density: Orcan camp 4x tpl-4 spawnCount 5, patrol spawnCount 2, bespoke 1300060/1300061 rebuilt one-territory-per-marker 10/17, stale hulls deleted), spec 18 (Ramun 1038 spawn-script reposition + 5 dual-state politics twin removals incl. Hyneu), spec 19 (dungeon 9037 reclaimed for Sorcha 1346: v31 config restored solo/lv8/quest-gated; level-65 line 21301-21307 sentinel-disabled at head; COMPANION HAND EDIT: RestoreTargetQuest 21307 removed by hand, re-apply after every replay, dsl-request issue 3). Research artifacts: padding-density-fixes, padding-sorcha-entrance, padding-ramun-dupes, padding-reward-audit, padding-first-expedition (user's First Expedition memory CONFIRMED: full set granted by story 1305 + disabled 1310; v31 ECompensation_13 drop table of the 9 armor pieces removed in v92 = open restoration option C). 1334 non-offer explained: authentic 6-10 level cap (1341 caps 12, 1390 caps 12). Batch 20 specs / 2147 ops / 0 failed; targeted verify PASS; NpcLoc 146 entries; server push 42 files verified; client 0.1.0-dev.26. OPEN USER CALLS: C gear option (ECompensation drop restore / 1310 reconsider / patch-002 design), 1334 level-cap raise. PRIOR | Level 1 analysis (4 agents) + adjudication: `data/padding-level1-proposal.md` (verdicts over the 40 disabled quests; corrections incl. the refuted collections blocker and the EN-vs-KR identity split). Specs 14-17 authored (26/461/13/11 ops), batch replayed 18 specs / 2091 ops / 15 expected warnings, reconciliation gate ALL 7 PASS. LATE FIX in same wave: v92 collect-quest bodies carried remapped collection ids with no IoD nodes (1334: 404, 1336: 403, 1341: 405); retargeted to the placed v31 ids 410/409/411 (tracker ruling 3 resolved), clean re-replay + targeted gate PASS. Enabled 34 quests (25 no-world-edit incl. courier re-anchor on 1309 and 1343/1344 gated behind 1316; 9 world-dependent); 19 habitat groups (217+4 spawns; Vekas excluded from 1300020); 6 giver NPCs at v17 NpcLoc markers. NpcLoc regen 147 entries (0 void). Server push 38 files verified; client 0.1.0-dev.25 published. StrSheet_NpcLoc technique + EN/KR identity census codified in playbook + content-restoration skill. World restart manual (user); live checkpoints: 1346 instance, fixed dialogs 1322/1327, repeatable cycle 1341, ruins density, restored-giver display names. NOT enabled: 1306/1307/1308/1310 (cut subplots, OUT), 1389 (deferred), 1385 (superseded). LEVEL 2 DONE + PATCH 001 CLOSED (2026-07-21): Berlon crafting-intro chain (quests 1353-1358, specs 21/22) LIVE-VALIDATED END TO END by the user (chain progression, crafting via recipes 91213/91221/91282, restored recipe designs + usable consumables, reward give-back keep-2, gather-node map markers). Client published through 0.1.0-dev.33. Fixes this wave: material give-back so craft is pure crafting; recipe designs 91213/91221/91282 restored to v31 identity (spec 22); consumables 6000/6001/6016/6017/6197 tooltip restored (spec 22); StrSheet_CollectionLoc waypoints authored for tier-1 collections 1/101/301 via new gen_collectionloc.py so gather markers resolve. All DSL requests from this work DELIVERED and adopted NATIVELY (journalScript cd080461, restoreTargetQuests 885dd4eb, DeliverItemTask element 30220450); pipeline is fixup-free. Patch application discipline encoded in root CLAUDE.md (full-patch apply/sync; --no-narrow when adding IdSorted quests; no mid-patch repo commits). Patch 001 committed locally on all three repos (server datasheet, client-dc, specs), NOT pushed. NEXT (LEVEL2-ROADMAP.md): bump patch 002 -> 003, open patch 002 for follow-up Level 2 contextual additions, pacing review of the new XP sources. |

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
