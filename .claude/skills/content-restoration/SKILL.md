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
4. **Deploy**: `deploy-dev/deploy_dev.py --verify` (server, SSH), then
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

### Gather-node map markers come from StrSheet_CollectionLoc; regenerate it with gen_collectionloc.py
- **Date/source:** 2026-07-21: an IoD gather quest tracked correctly but clicking its journal objective marked nothing on the map; `lookup_gathering_spawns 301` reported 90 world spawns yet `StrSheet_CollectionLoc waypoints (templateId=301): (none)`. The tier-1 IoD collections (Verdra Plant 1, Krymetal Ore 101, Sun Essence 301) had no entry in v31 OR v92.
- **Why:** the map marker for a CollectTask reads the client family `StrSheet_CollectionLoc`, the collection analog of `StrSheet_NpcLoc`: one String per collection (templateId = collection id) whose value is `continentId#x,y,z|...` node waypoints. It is not in the migrate sync-config, so it is tool-managed. Base tier-1 collections shipped without waypoints in both eras (a gap, not a regression).
- **Apply:** run `python reforged/tools/dc-restore/gen_collectionloc.py` after any IoD collection/spawn change. It projects `CollectionTerritory_13_*` node positions into `13#x,y,z` waypoints and ADDS entries only for continent-13 collections that lack one, leaving live-validated existing entries and multi-zone `7001#` waypoints untouched; writes both the server copy and client shard; idempotent. The prefix is the continentId (IoD = 13), confirmed against a working mainland collection (304 = continent 7001). This is the collection sibling of the `gen_npcloc.py --prune` client-registry step.

### Parse the XML before trusting that spawn data "exists"; BHS disables legacy content by commenting it out
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
- **Apply:** when auditing whether spawn/territory content exists in an era, load the file
  with an XML parser (or check for `<!--` markers spanning the block) before concluding
  anything from grep hits. Diagnostic signature: `/@spawnnpc <hz> <tpl> 1` works but load,
  event, and `initialize` territory spawns all fail = the territory data is not loaded;
  check for comment markers first, not topology. When uncommenting, verify tag balance:
  the `-->` often swallows a closing tag.
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
