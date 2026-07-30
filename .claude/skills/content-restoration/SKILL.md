---
name: content-restoration
description: >
  Restore classic-era TERA content (quests, NPC spawns, mob habitats, rewards,
  dialogs) from historical DataCenters into the current v92 server, using the
  dc-restore toolkit. Covers the source doctrine (v31-primary baseline, v17.11
  as padding research index), the survey/audit/restore/spawn pipeline, the two-commit-lane
  discipline, and the client deploy pipeline. Use when restoring a map or zone
  to its classic state, re-enabling disabled quests, reconstructing deleted NPC
  or mob spawns, filling empty quest rewards, or diffing a zone across the
  old client / v31 / v92 sources.
disable-model-invocation: false
user-invocable: true
---

# Content Restoration

Restoring a classic map into v92. Tools live in `reforged/tools/dc-restore/`
(read `reforged/tools/dc-restore/README.md` for CLI detail). Deploy via
`reforged/tools/deploy-client/`.

**Zone port playbook (binding for new zones):** the full validated phase
pipeline (revert, diffs, authoring, gate, deploy, commit lanes), family map,
and hard-won traps live in `docs/plans/classic-restoration/ZONE-PORT-PLAYBOOK.md`.
Prime any zone-migration session with it plus `DOCTRINE.md`. Padding phases use
the zone's `PADDING-BRIEF.md`.

## Source doctrine (binding)

The binding doctrine is `docs/plans/classic-restoration/DOCTRINE.md`
(v31-primary, adopted 2026-07-20; it supersedes the earlier v17-north-star
posture). Summary: **v31** (`v31_datasheet` in `.references`) is the structural
and content baseline, ported 1:1 per zone (story spine, spawns, sections,
shops, pacing). The old client **v17.11** (`old_client_dc`) is a RESEARCH
INDEX only, used in a separate data-first padding phase to locate dormant
server-side content; it is never a data source for story quests or NPC
placement. The v31 client (`client_dc_v31`) cross-checks client-side families.
v31 wins on divergence with v92 except where v31 is internally inconsistent
(task vs dialog vs strings); every divergence is logged per zone.

Client DataCenters (v17.11 and current) carry no TerritoryData spawn
positions; only fences + group descs survive client-side, so spawn positions
come from v31 or must be authored. ONE exception: the client StrSheet_NpcLoc
holds a quest-marker world coordinate per (huntingZone, templateId) for every
quest-linked NPC of its era, and it survives for NPCs that were never spawned
server-side. See the StrSheet_NpcLoc lesson below.

## Pipeline

1. **Survey + audit** (read-only): `survey.py` for a 3-source gap report;
   `audit_quests.py` for the 12-flag deterministic quest diff (writes md+json).
   `dcq.py` for targeted cross-source lookups (`quest <id>`, `npc <hz> <id>`,
   `name <text>`, `collection <id>`). Diff against git HEAD baseline, not the
   working tree, so an uncommitted DSL overlay is not misread as content loss.
2. **Restore** (idempotent, dry-run by default, `--apply` to write):
   `quest_restore.py` (remove 99,99 sentinel, relink prereqs, register story
   groups), `comp_restore.py` (fill empty QuestCompensationData from v31),
   `spawn_restore.py` (reconstruct territories/mobs/villagers from client
   fences). Re-run the audit after apply to confirm flags cleared.
3. **Gate (dungeon content)**: any restore touching a dungeon continent
   (DungeonData, its TerritoryData/NpcData, DungeonConstraint) must pass
   `python reforged/tools/dc-restore/dungeon_audit.py --dungeons <contId>`
   before deploy. It resolves every DungeonData territory/entity reference
   against PARSED per-HZ content and fails on comment-disabled or missing
   targets (the dungeon 9037 failure class). Exit 0 required.
4. **Gate (any restored quests)**: run
   `python reforged/tools/dc-restore/audit_class_gates.py --zones <zones>`
   before deploy. Exit 0 required. It checks that every class on the CURRENT
   roster is offered some member of each class-gated variant group. A faithful
   restore reproduces the era's class list exactly, so classes added after that
   era match no variant and the content is offered to nobody; anything gated
   behind it is then unreachable. See the class-gate lesson below.
5. **Review (any restored or changed quests, ADVISORY)**: run
   `python reforged/tools/dc-restore/audit_quest_design.py --zones <zones> --since HEAD`.
   Always exits 0 and is not a gate: it reports design defects that are
   individually valid and wrong as a system (duplicate rewards, uncompletable
   gear sets, objectives the zone cannot supply, references into disabled
   quests). A NEW finding needs a fix or a waiver entry with a reason. See the
   `quest-design-review` skill.
6. **Deploy**: `deploy-dev/deploy_dev.py --verify` (server, SSH), then
   `deploy-client/deploy_client.py --all --note "..."` to pack, install, and
   dry-run the publish, and `--publish --note "..."` to commit the upload.
   The client DC is already synced by migrate; `deploy_client.py` does not
   sync. World-server restart is manual.

## Two commit lanes (binding)

Restored canonical content is the BASELINE lane: commit it separately once the
user validates it live, and commit it BEFORE the patch-001 DSL specs are
applied on top. DSL patch application is the TUNING lane, committed only by the
user. Never mix the lanes in one commit. See [[project-commit-lanes]]. If the
working tree already intermingles both (a mess to avoid), snapshot before any
destructive reconcile.

## Lessons

### A tool that writes the client DataCenter directly is a workaround; import the family instead
- **Date/source:** 2026-07-28: a full patch 002 revert-and-replay silently dropped the `StrSheet_NpcLoc` regeneration. The migrate run read 76 applied, 0 failed, 0 warnings, and the loss was invisible in it. Found only by diffing the stash against the working tree afterward.
- **Why:** `gen_npcloc.py` writes the CLIENT shard directly, so its output lives in the tree that is not reproducible from specs. A patch replay regenerates the server tree and syncs it; it cannot regenerate something that was never server-side. A stash of the client tree therefore discards the work and nothing reports it. The same shape applies to any bespoke tool or hand edit that targets the client.
- **Apply:** prefer `dsl import` (the documented inverse of `sync`) to bring a client-only family onto the server, then let normal sync propagate it. Four steps, in order, none skippable:
  1. Register the descriptor in `sync-config.yaml` FIRST, since import reads that same descriptor inverted. Set `composite_id_attributes` when the family's identity is a pair.
  2. `dsl import --dry-run` and **read the duplicate-collapse line**. It is what catches a wrong key: `StrSheet_NpcLoc` is keyed `(huntingZoneId, templateId)` and a `templateId`-only key collapsed 4101 rows to 1018 while reporting "imported 1018 record(s)", which reads as success. The ids it listed were all `1`, the giveaway.
  3. Import, then sync straight back and diff the client. Verify with a REAL sync, never a dry-run alone: a plan cannot show byte-stability, and registering a never-synced family can legitimately rewrite shipped client values on first sync (`StrSheet_Creature` merged 3 duplicate `<HuntingZone id="183">` wrappers and lowercased two `class="True"` values, all 17,755 rows preserved).
  4. Commit the imported canonical file to the server repo, scoped and alone. `migrate` applies with `--source-ref <server HEAD>`, so an UNTRACKED server datasheet does not exist in the commit it reads and gets rewritten from scratch.
- **Then retarget the generator to emit a SPEC, not a datasheet.** `gen_npcloc.py` takes `--out <spec path>` and emits `npcLocStrings: upsert` rows plus `delete` rows for stale keys; it writes no datasheet. Derivation from spawn geometry stays in the tool because that is a real batch operation; authoring goes through the DSL. That is what makes the output survive a revert-and-replay.
- **Emit Loc waypoints as typed `continent` + `markers`, not a packed `string`.** Both forms work, but a packed payload runs to thousands of characters and hides which waypoint moved; typed markers diff one at a time. `markers` replaces the whole list and is sequence-exact, `addMarkers`/`removeMarkers` edit in place and are idempotent, removals apply before additions, and mixing `string` with the typed keys is E554 rather than a precedence rule.
- **Prove a form change is a no-op by hashing the applied file.** Switching the registry from raw to typed was verified byte-for-byte identical (same SHA256) against a snapshot taken before the change. For a generated artifact that is the cheapest possible regression proof, and it is stronger than re-reading the spec.
- **Map the new key in `ENTITY_SYNC_MAP`.** A key absent from `tools/migrate/migrate.py` syncs to nothing, silently, no matter how correct the spec and descriptor are.

### Prove the subsystem with a SHIPPED control before changing authored data; some subsystems log nothing at runtime
- **Date/source:** 2026-07-28: an authored field event would not start, and two world-server restarts were spent on data hypotheses first. Running a shipped event as a control (`/@startfe 7014 2`) isolated the fault in one step. Separately, the world server emits NO runtime field-event logging: the only field-event line in any boot log is the template-loading line, so the silent log had never been evidence either way.
- **Why:** "my authored content is wrong" and "the subsystem is not working on this box" look identical in game (nothing happens) and identical in the log (silence). Log silence is evidence only for a subsystem known to log; for one that logs nothing at runtime it is compatible with every hypothesis, including success.
- **Apply:** when authored content does not fire, run the nearest SHIPPED example as a control BEFORE changing any data or spending a restart. Establish whether the subsystem logs at all before reading its silence as a result. Field event GM kit: `/@startfe <contId> <eventId>` then `/@gotofe <contId> <eventId>` (BOTH arguments are required on both; a bare `gotofe` silently does nothing), supported by `/@showfeinfo on`, `/@showfeprogress`, `/@setfeprogress`, `/@endfe`, `/@ferotation on|off`.

### Verify a client deploy reached the INSTALLED .dat, not just the source XML
- **Date/source:** 2026-07-28: field-event deploy and test cycle. The chain is source XML, then packed `.dat`, then installed `.dat`, and only the last hop is what a tester loads.
- **Why:** pack and install are separate stages, so a skipped, failed, or partial run leaves the previous `.dat` in the game install with nothing in the output naming the discrepancy. The tester then validates old data and reports a spec failure that is really a deploy failure, at the cost of a manual restart and their time.
- **Apply:** before asking anyone to test a client-side change, confirm the packed `.dat` mtime is LATER than the edit to the source XML, and that the packed and installed `.dat` hash identical (`Get-FileHash`). Two commands, and they gate the most expensive verification in the project.

### A faithful restore inherits the era's class roster; audit gates against the CURRENT roster
- **Date/source:** 2026-07-25: a Ninja completed 1384 (Getting to Know the Garrison) and the story spine dead-ended. Quest 1382 "Gathering Your Strength" admits Warrior/Lancer/Slayer/Berserker/Archer/Engineer and its sibling 1383 admits Sorcerer/Priest/Elementalist, so Milene offered neither to a Ninja and 1331 "Climbing through the Ranks" never unlocked. A Berserker progressed normally. Fixed by `specs/patches/002/19-newclass-quest-gates.yaml`; the same sweep also found Gunner excluded from the 1351/1352 and 6302/6306 groups.
- **Why:** classic content gates class-split variants with `<수행조건><클래스>`, listing exactly the classes that existed then. **v31 carries the identical lists**, so the restoration was correct and no diff-against-source gate can ever catch this: both sides agree. The defect only exists relative to the current 13-class roster. It is also invisible in every single-class live test that happens to use a classic class, and invisible at load time (no warning, no crash): the quest simply is not offered, which reads as "nothing happened".
- **Apply:** after restoring or enabling any class-gated quest, run `audit_class_gates.py --zones <zones>` and require exit 0. It evaluates coverage per variant GROUP (grouped by zone + giver + story group, since one NPC hands each class its matching variant), so a caster-only quest is not flagged when its physical sibling covers the class. Fix a gap by adding the classes to the variant whose content fits them (physical vs caster), keeping the group mutually exclusive so every class matches exactly one member. Never widen a sentinel-disabled quest (prereq `99,99`): that is dead data. Reaper/Soulless is excluded by decision (starts elsewhere at a higher level), so it is not in the default roster.

### Not generating a row does not delete a row: a neutered generator leaves the baseline's rows untouched
- **Date/source:** 2026-07-30: a wave stopped its loot generators emitting feedstock, and the plan reasoned that the rows "exist only in the dirty tree" so a replay would simply never write them. A post-apply value check found 192 feedstock rows still live, all inside the eleven zones the patch owns, while all 1,595 rows in the 85 zones it does not own were gone. The framework rule was being enforced everywhere except where we were working.
- **Why:** a generator controls what a spec WRITES; the baseline holds whatever was committed. Removing an emitter is sufficient only for rows that emitter created. Rows that predate the patch survive every replay untouched, and nothing reports them: no op count, no warning, no validate result, because no spec ever names them. The reasoning error is seductive because it is half true, and the half that is true is the half you tested.
- **Apply:** when a change is expressed as "the generator no longer emits X", ask whether X also exists in the committed baseline and MEASURE it (`git show HEAD:<path>` and count), rather than reasoning from the dirty tree. If it does, the baseline rows need explicit deletes on top of the generator change. Verify by VALUE after the apply, never by reading the spec diff. See the mirror case in the next lesson, where a removed op leaves behind a file it already wrote.

### Removing an op from a spec does not revert the file it already wrote
- **Date/source:** 2026-07-25: spec 19 first widened quest 6307's class gate, then the op was dropped after 6307 turned out to be sentinel-disabled. The next full apply left 6307 still carrying the widened gate: no spec touched the file, so nothing rewrote it, and the stale value stayed in the working tree and synced to the client.
- **Why:** an apply only writes files its ops target. The datasheet trees are generated output, but "generated" means "written when a spec touches it", not "reconciled to what the specs currently say". A removed or narrowed op therefore leaves drift that no later apply cleans up.
- **Apply:** when you delete or narrow an op, `git checkout --` the files it used to write, then re-run the full apply and sync so both trees are re-derived. Verify with `git status` that only files the current specs produce are dirty. This is the same failure shape as `deploy_dev.py` mirroring only git-dirty files, which leaves a reverted file stale on the dev box.

### Gather-node map markers come from StrSheet_CollectionLoc; regenerate it with gen_collectionloc.py
- **Date/source:** 2026-07-21: an IoD gather quest tracked correctly but clicking its journal objective marked nothing on the map; `lookup_gathering_spawns 301` reported 90 world spawns yet `StrSheet_CollectionLoc waypoints (templateId=301): (none)`. The tier-1 IoD collections (Verdra Plant 1, Krymetal Ore 101, Sun Essence 301) had no entry in v31 OR v92.
- **Why:** the map marker for a CollectTask reads `StrSheet_CollectionLoc`, the collection analog of `StrSheet_NpcLoc`: one String per collection (templateId = collection id) whose value is `continentId#x,y,z|...` node waypoints. Base tier-1 collections shipped without waypoints in both eras (a gap, not a regression).
- **Apply:** run `python reforged/tools/dc-restore/gen_collectionloc.py --out <spec path>` after any IoD collection/spawn change. It projects `CollectionTerritory_13_*` node positions into continent-13 waypoints and emits a `collectionLocStrings` spec for collections that lack a row. **It writes no datasheet, server or client** (corrected 2026-07-28: it used to write both, and the client write was a pipeline bypass). The family is now a registered sync entity, so the server file is the source of truth and normal sync propagates it. Idempotent: once every IoD collection has a row it writes no spec at all.
- **ADD-ONLY is load bearing here.** Never widen the tool to re-derive rows that already exist. `templateId 496` spans continent 13 AND the mainland, the only such row of the 177 shipped, so rebuilding it from continent-13 data alone would silently drop its mainland half. The `13#` prefix is the continentId, confirmed against a working mainland collection (304 = continent 7001).

### Run find_dormant_blocks before trusting that content "exists"; BHS disables legacy content by commenting it out
- **Date/source:** 2026-07-21: dungeon 9037 (Sorcha, quest 1346) investigation. A prior
  session verified TerritoryData_437 as "byte-identical v31/v92" via grep/text-diff and
  concluded territory spawning was broken below the datasheet layer; an XML parse showed
  all 8 classic territory groups (63 territories) were wrapped in one `<!--` `-->` comment
  and never loaded. The session had even edited `bossInstanceId` inside the comment with no
  effect. Uncommenting fixed the data layer (the comment had swallowed one closing
  `</TerritoryGroup>`, re-added by hand).
- **Why:** grep, diff, and text comparison all "see" commented-out XML that the server never
  parses. Disable-by-comment is a standard BHS practice when repurposing zones: a sweep found
  14 v92 TerritoryData files with comment-disabled groups (HZ 26: 76 territories, HZ 437: 63,
  also 473, 358, 243, 871, 872, 767, 980, 2050, 2052, 2054, 236, 58).
- **Apply:** call `find_dormant_blocks(entityType, huntingZoneId)` (delivered 2026-07-25 for
  exactly this failure). It reports commented-out elements with their ids and descs, and its
  `wellFormed=N` flag marks a block whose comment swallowed a closing tag, which is the 9037
  case and the thing that makes a naive uncomment produce an unparseable file. Every OTHER
  tool correctly ignores dormant content, so its absence from a normal query proves nothing.
  Run it on the spawn families of any zone before concluding content was deleted, and use it
  to enumerate re-enable candidates during a padding phase. Diagnostic signature in game:
  `/@spawnnpc <hz> <tpl> 1` works but load, event, and `initialize` territory spawns all
  fail = the territory data is not loaded; check for comment markers first, not topology.
  When uncommenting, verify tag balance.
- **Date/source:** 2026-07-18 duplication incident first led to v17-primary;
  the 2026-07-20 strategy review (`docs/plans/restoration-source-strategy.md`)
  reversed it: v17 is a client holding zero spawn positions, the 3-source
  reconciliation caused systematic audit misses (Eria MATCH-but-unspawned,
  Priscus wrong-format grep), and conditional-spawn choreography survives in
  no source we hold.
- **Why:** layering sources without a single authority double-counts content;
  making the only complete server dataset (v31) the authority removes the
  reconciliation error surface instead of asking audits to be more careful
  inside it.
- **Apply:** follow `docs/plans/classic-restoration/DOCTRINE.md`: port v31 1:1
  per zone, wipe-and-replace driven by per-row diff dispositions, v17 used
  only as a padding-phase research index gated on intact server data plus
  standing spawns.

### Convert mid-chain auto-accept quests to NPC-accept during staged re-enable
- **Date/source:** 2026-07-18: quest 1311 (즉시수주 auto-accept) never granted
  to a character that completed prereq 1310 while 1311 was still sentinel-
  disabled; talking to the NPC and relog both failed; only `/@start_quest`
  worked.
- **Why:** auto-accept quests grant only on the prereq-completion EVENT and
  have no clickable accept dialog; a staged re-enable makes the grant fire into
  a disabled quest and be lost permanently for that character.
- **Apply:** when re-enabling a mid-chain `즉시수주` quest that carries an
  NPC대화 reference, drop the `즉시수주` line so the NPC offers it clickably.
  Flag every `즉시수주`-behind-a-prereq quest before play. `/@start_quest <id>`
  unblocks an already-stuck character (character-DB state, not fixable by data).

### jumpto keys on templateId; beware twin-name NPCs
- **Date/source:** 2026-07-18: "Ramun" (herald) and other names exist as TWO
  templates in different island sub-zones (e.g. 213,1038 vs 213,1124); a quest
  targets one specific template while the player clicks the other.
- **Why:** the client shows the same display name for both; only the templateId
  disambiguates. StrSheet_Creature templateIds are zone-scoped (resolve the
  enclosing `<HuntingZone id=>`), so a name can map to several ids.
- **Apply:** use `dcq name <text>` (it joins against per-zone NpcData) to find
  the right (hz, templateId); `/@jumpto <hz> <templateId>` targets the exact
  one. When a quest NPC "cannot be talked to", check for a same-name twin first.

### An unclickable quest NPC may be a spawn-script position mismatch
- **Date/source:** 2026-07-21: quest 1327 task 1 (talk to Herald Ramun 213,1038) failed live; template carries spawnScriptId 10023 whose entrance script ends in a move, so the client visual walks away from the server-side interactable position and C_NPC_CONTACT fails the range check silently. Packet-capture-proven by the retired pilot; fix re-applied as patch 001 spec 18.
- **Why:** the server keeps the entity at the TerritoryData spawn coordinate; the player clicks where they SEE the NPC (the script endpoint), and nothing happens with no error.
- **Apply:** when a visit/talk task fails on an NPC that visibly stands there, check the template for a spawnScriptId; if present, move the server spawn pos onto the script's endpoint so server and client agree. Distinct from the twin-name trap (also in these lessons): check both.

### StrSheet_NpcLoc recovers lost NPC positions and tracks renames
- **Date/source:** 2026-07-20 IoD padding phase: six quest-giver NPCs with v31
  templates but zero TerritoryData spawns in any era were placed using the
  v17.11 client StrSheet_NpcLoc quest markers (`13#x,y,z` strings keyed by
  huntingZone + templateId), then collision-checked against baseline spawns.
- **Why:** the quest-link registry outlives the spawn: an era's client keeps
  one marker per quest-linked template even when the server never spawned it.
  Name-based cross-era matching is unsafe for a second reason: the KR-based
  v92 server carries a wholly different villager identity per template than
  the English clients (EN Kamarnu = KR Rabram, Jehan = Beres, Clovis = Muriel,
  spanning nearly all IoD villagers). This is a NA/EU vs KR localization
  split, stable across v17/v31 EN, NOT a rename over time; the v92 server's
  English StrSheet_Creature is stale and not an authority. Full census:
  classic-restoration/iod/data/padding-npcloc-sweep.md section 5.
- **Apply:** when restoring an NPC with no spawn in any server source, pull its
  marker from the era client's StrSheet_NpcLoc, point-in-polygon it against
  AreaData section fences to name the camp, nearest-neighbor check against the
  live TerritoryData, author at the marker, tune heading and exact spot
  in-game (NpcLoc has no heading). Always match cross-era NPCs by
  (huntingZone, templateId), never by display name.
- **Marker density (2026-07-21 amendment):** a quest-linked MOB template carries
  roughly ONE marker PER CLASSIC SPAWN POINT, not one per cluster. When authoring
  territories from a marker set, emit one small territory per marker; collapsing
  the set into a single convex hull discarded 9 of 10 and 16 of 17 spawn points
  in the IoD padding wave and produced unplayably sparse quest mobs (fixed by
  spec 15 regen). Check the quest's kill/collect counts against the resulting
  concurrent mob count before shipping.
- **Date/source:** 2026-07-18: the patcher build failed 3x with "Scanning" /
  cannot access `Binaries/TERA_d3d9.log` because the running game client locks
  that log while the publisher chunks the whole game dir.
- **Why:** the publish stage chunks the entire install directory; an open
  client holds runtime files open.
- **Apply:** close the game client before `deploy_client.py --publish`. The
  sync/pack/install stages are unaffected; only publish needs the client shut.

### Never leave sidecar/backup files in the game install
- **Date/source:** 2026-07-17: user rule; the patcher chunks the whole gameDir.
- **Why:** any stray file (.bak, copies) gets chunked and shipped to players.
- **Apply:** copy the .dat in place with no backup file; stage any backup
  outside `game_client_install`. See [[no-backups-in-game-install]].
