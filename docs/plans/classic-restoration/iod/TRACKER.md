# IoD Restoration Tracker (v31-primary redo)

Pilot zone under `../DOCTRINE.md`. Supersedes the retired `docs/plans/iod-alpha-content-loop/`
pilot (its TRACKER and data artifacts remain readable as reference; its doctrine does not apply).

> **Sub-plan: Guardian Legion field events moved to PATCH 003.** The authoring wave for the
> three-phase Orcan field event has its own folder, `guardian-legion/`, with `PLAN.md` (phases and
> acceptance gates), `BACKLOG.md` (every test, failure and decision) and `TRACKER.md` (current
> state). `/prime-classic-restoration iod` does not enumerate nested folders, so start there for
> any field event or new-monster work. It is BLOCKED until patch 002 is closed.

Last updated: 2026-07-31 (reward vector WAVE 1 CLOSED; wave 2 opened on the Valkyon Quartermaster, RV-02.
Patch 002 still OPEN, both datasheet repos still dirty by design.)

## Session handoff (2026-07-31, ninth session): wave 1 closed, wave 2 opened

Live testing confirmed the Valkyon Commendation and the feedstock flattening both landed. Three text
defects came out of it, all fixed in specs `002/37`, `002/39` and the new `002/43`: the token tooltip
was printing OUR BUILD ORDER at the player ("the quartermaster who accepts them has not yet set up"),
the retired feedstock tiers had been renamed on our own invention rather than using the publisher's
`[Not Usable]` convention, and item 21351 Masterwork Alkahest carried a `decompositionId` paying 336
Metamorphic Emblems, a level-65 v92 currency, off a material a level-3 player uses.

**The tooltip defect produced a binding rule and a gate.** `DOCTRINE.md` rule 10: player-facing text
describes the world, never our build order. Enforced by `tools/dc-restore/audit_player_text.py`, which
parses spec YAML and fails the patch on the phrase family. Proved by probe: restoring the original
sentence fails the gate on two independent patterns. Run it with the other pre-deploy gates.

**Wave 1 was closed without its live-validation pass**, by user ruling: the remaining deltas were
tooltip text. Its three planning documents (1,827 lines) were retired after a check found their content
duplicated at the point of use, in spec headers, `config/sync-config.yaml` and the audit gates. The
surviving document is `docs/plans/reward-vectors/IOD-BACKLOG.md`, which records where each piece went.
The wave-1 narrative about DSL gaps was stale: every gap it described has since been delivered.

**Specs `002/37`, `002/39` and `002/43` are authored, validated and NOT APPLIED.** They fold into
wave 2's first `migrate --patch 002` run rather than spending a deploy cycle on text alone.

## Session handoff (2026-07-30, eighth session): the dev box was missing patch 001 entirely

**The most important thing in this file.** Testers reported IoD zone quests missing in game (Kishale
offering nothing). It was not a spec fault: the dev box's datasheet clone sat at an APRIL commit
(`9c7163fe`) while the local repo was **8 commits ahead**, holding the whole patch-001 restoration
baseline. 127 of the 151 files those commits touch were stale or absent on the box, including 27 quest
files and all six Berlon chain quests.

Cause: `deploy_dev.py` pushes the **git-dirty set only**. While a patch is open its files are dirty and
ship every deploy; the moment the patch closes and they are committed they drop out of the payload and
reach the box only through the box's own clone. The box had been reset at some point, which discarded the
overlay carrying them. Nothing detected it: `--verify` reported 184 of 184 files hash-verified on every
run, because all 184 were exactly the dirty files it knew about.

Fixed by moving the 8 commits with a `git bundle` (the box has no git credentials in a non-interactive SSH
session), fast-forwarding its clone to `cdca4fb4`, then re-laying the overlay. All 151 files verified
content-identical afterwards, EOL-normalised: the box runs `core.autocrlf=true`, so a raw hash compare
shows 126 false mismatches. Lesson recorded in the `content-restoration` skill and
`tools/deploy-dev/README.md`.

**Still outstanding:** the box cannot fetch from GitLab on its own (no credential store over SSH; the fix
is a read-only deploy token plus GCM's `dpapi` store), and nothing in the deploy loop checks the box's HEAD
against origin.

### Token architecture wave, same session

Rulings R23 to R27 (`docs/plans/reward-vectors/IOD-BACKLOG.md`, which is now the only reward-vector
document; the separate implementation record was retired 2026-07-31). Story quests now pay the token, the flat rate
became an effort ladder (1,182 per character for a full island clear, against 35), tokens are no longer
bankable, and the item is renamed Valkyon Commendation. Deployed, client `0.1.0-dev.42`, all gates exit 0,
**not live-validated**. The content framework repo was brought in sync in the same session.

## Earlier state (2026-07-28) (Guardian Legion field event v0 LIVE-VALIDATED on Island of Dawn:
the first field event this project has ever authored, and the first outside the shipped
level-65 set. Quest log reward panel and recall network live-validated earlier; zone-quest
trimming and reward-cadence wave still awaiting live validation. Patch 002 still OPEN).

## Session handoff (2026-07-28, sixth session): Guardian Legion field events

First field event authored by this project. v0 was a deliberate lifecycle probe, not
content: one npc spawns, the progress bar is bound to its HP, killing it completes the
mission. It is LIVE-VALIDATED and the approach is proven.

### The blocker, and what it cost

The event was structurally perfect and did nothing for two restarts. Cause: a field event
will not run on a continent that is not declared `channelType="field"`. Continent 13 was
`channelingZone`.

This was documented in TWO places we already had, and both reads went around it:

1. `ContinentData.xml`'s own header comment defines the value as the attribute that must
   be set to use fieldEvent/fieldData, and says base behaviour is otherwise identical to
   `none`/`channelingZone`. Missed because every inspection used Python ElementTree,
   which DISCARDS comments; the file has 162 of them and the parse showed none.
2. The domain KB's own `field-event-system.md`, under "What Starts an Event", already
   listed the field channel type as a prerequisite. Missed because the search covered
   `zone-hierarchy-system.md` and the DSL schema page instead of the system's primary doc.

What actually isolated it was a CONTROL TEST: running a shipped event (`/@startfe 7014 2`)
in the same session with the same commands. It started and teleported correctly while
`13/1` did nothing, which proved the subsystem worked on the box and localised the fault
to our continent in one step. Do this before changing any data next time.

Both lessons are now in the skills (`domain-research`, `content-restoration`).

### What is live and validated

- Event fires, mission UI renders, npc spawns, killing it drives the bar to 100.
- `channelType` flip is spec-driven on the server (spec `002/35`) and a HAND EDIT on the
  client, deliberately. See the DSL bug below.
- Field event families are fully plumbed: `Field`, `FieldEvent`, `StrSheet_Field`,
  `EventDialog`, `StrSheet_EventDialog` registered in `sync-config.yaml` and mapped in
  migrate's `ENTITY_SYNC_MAP`. `packages/fieldevent` installed (22 definitions).
- Adding a `FieldData` file inserts a shard into an IdSorted layout: continent 13 sorts
  FIRST (13 < 2000), so all 12 existing `Field` shards shift and the set goes to 13.
  That patch MUST sync with `--no-narrow` or it fails E680.

### Findings that contradicted our assumptions

- **A dedicated mission hunting zone is NOT required.** Every shipped event uses one
  (620-631 on ground continents). Ours runs its territories directly in live world HZ 13,
  with `startTerritoryId` also pointing at a world territory, and it works.
- **Event territories must be `type="quest"`.** All 647 HZ-13 territories are `normal` and
  spawn at world start; a `normal` event territory would leak its mobs into the live world
  permanently.
- **The world server emits NO runtime logging for field events.** The only line in any
  boot log is the template-loading line, so log silence proves nothing.

### Known defects found and contained this session

- **`ContinentData` client sync CORRUPTS the client.** The server writes
  `isSpecificSpace="TRUE"` uppercase; the client XSD types it `xsd:boolean`; the cast
  fails and the sync writes `false` for all 135 uppercase-TRUE continents, clearing the
  instanced-space flag on every dungeon and battlefield continent. Exit 0, no warning.
  `continentDatas` is mapped to `None` in `ENTITY_SYNC_MAP` as a QUARANTINE (not a
  server-only claim). Filed: `docs/dsl-requests/2026-07-28-continentdata-sync-boolean-case.md`.
  DSL team is working on it as of session end. When it lands: map the key, re-sync, and
  verify with an ATTRIBUTE-level diff that only continent 13 changed.
- **`IdSorted` silently plans 0 files without an explicit `server_path`.** Filed:
  `docs/dsl-requests/2026-07-27-idsorted-server-path-required.md`.
- **`AreaData` had never synced to the client**, its `source_mapping` key was missing the
  subdirectory prefix. FIXED. Zero client diff resulted, because the client `Area.xsd`
  declares neither `recallScrollPos` nor `recallRevivePos`, so spec `002/26`'s recall work
  genuinely was server-only after all.

### Reproducibility defect: FIXED

`migrate` applies with `--source-ref <server HEAD>`, so an UNTRACKED server datasheet does
not exist in the commit it reads and gets rewritten from scratch. This truncated
`StrSheet_Field.xml` from 214 rows to 8 on two separate runs. Resolved by committing both
imported baselines to the server datasheet repo (`7b5e4092`, canonical pre-change content:
214 and 159 rows). Replay now yields 222 rows with zero canonical rows lost.

Note this was a DELIBERATE exception to the never-commit-mid-patch rule, made by the user,
precisely to move the source-ref baseline.

### Next session: make the event engaging

v0 is deliberately not content. The user's stated goals:

1. **Dedicated event mobs.** Currently the boss is `13,902` Dwarf Guardian, chosen only
   because it is the sole Orcan-family template with ZERO references anywhere. Every other
   camp Orcan is load-bearing: `13,4`/`13,5` for quest 1349, `13,901` for 1311 and 1337,
   `13,1002`/`1003` for 1309. Author dedicated templates, slightly more powerful.
2. **Map markers and legibility.** Live feedback: there is no indicator of what belongs to
   the event, and its mobs are visually mixed with ambient spawns. The mechanism that
   fixes this is the world takeover shipped events use: despawn the underlying world
   territories in `initialize`, restore them at `beforeDeleteEvent` with
   `isEventNpc="false"`. v0 deliberately skipped it to keep blast radius small.
3. **Progress calibration.** One kill currently fills the bar, because `progressType` is
   bound to a single npc's HP. Move to kill-count or multi-stage progress.
4. **Rewards.** Measured: the shipped small-event `dealing` coefficient 1.45 yields about
   1 contribution point per 2 kills at level 8, against a participation bag requiring
   100000 points. Unreachable. Recalibrate before wiring any reward.
5. **Explore more field event features in practice**: waves on timers, `killCount` groups,
   multi-phase flag gates, `changePos` to move the staging point, `AutoEventBalance`
   (its abnormality ladder 77770001-77770030 is level-65 tuned and untested at level 8),
   and `ClearRewardPool`.

The endgoal remains the multi-phase moving event: start near Eria at `55608,-82162` and
advance to the Orcan Bivouac at `49991,-78114`, roughly 6,900 units WNW, via Ayrdoss at
`49870,-80830`. Donor architecture for that is the shipped escort mission, which uses
`enterTerritory` per leg plus `changePos` on both `start` and `revive`.

### Outstanding

- Live-test the zone-quest trimming wave (specs `002/27` to `002/33`), still unvalidated.
- Live-test Brawler and Valkyrie on the new-class spine, and the Dulari wrong-class case.
- Quests 1316 and 1317 still grant level-11 gear from story quests.
- **Patch 002 grew on 2026-07-28**: the reward-vector wave folds into it rather than a later patch.
  Its scope, rulings and measured corpus figures are in `docs/plans/reward-vectors/IOD-BACKLOG.md`
  and `docs/patch-002-scope.md`. That is forward design, not restoration, so nothing is duplicated
  here; prime from the backlog before touching feedstock, tokens or zone-quest rewards.
- Then close patch 002 with one commit per datasheet repo.

## Deployment status (2026-07-27, SUPERSEDED: current client is `0.1.0-dev.42`, see the 2026-07-30 handoff above)

Specs `002/27` through `002/30` (with `29` amended) are applied, both gates exit 0, and both legs
are on dev:

- **Server**: `deploy_dev.py --verify`, 80 files copied, 80 hash-verified (redeployed
  2026-07-27 after specs 32 and 33). **The world server restart is manual**; datasheets load at
  startup only.
- **Client**: packed and installed to the local game client (repacked 2026-07-27 after the
  NpcLoc regeneration), then **PUBLISHED to R2 as `0.1.0-dev.39`** (15 new chunks, 55.69 MiB,
  19,448 reused, verified 19,463, `committed=True`), so remote testers can pull the wave.
  (`dev.38` carried specs 27 to 31; `dev.39` adds trims 6 and 7.) The client leg is load-bearing for this wave, not
  optional: `QuestCompensationData` for zone 13 is client-synced, so without it the quest log
  reward panel advertises the OLD rewards while the payout is correct.

Live-test checkpoints are in the wave sections below. The one checkpoint that must wait for the
DSL fix is the 1326/1330 negative case (complete 1305, then confirm both are still offered);
everything else is testable now by accepting 1305 and leaving it open.

## Session handoff (2026-07-27, fifth session): zone-quest trimming wave

Internal live testing reported the IoD zone quests as excessively repetitive and low value.
This session opens a trimming wave against that feedback. It is policy work on our own
padding, not restoration: v31 ships every one of the 34 quests our Level 1 wave enabled with
the 99,99 sentinel, so each trim REMOVES scope from the padding enable set rather than adding
a divergence.

### Priming artifact: the reference model for trimming

Before touching anything, the removal-hazard surface was measured over the whole server
datasheet and client DC, matching BOTH reference encodings (pair form `13,23` in quest
headers, global form `1323` everywhere else). Seven classes exist; the IoD footprint is:

| Class | IoD footprint |
|---|---|
| `선행퀘스트` prerequisite | 31 edges inside the band |
| `진행퀘스트` in-progress gate | 2 (quests 1326 and 1330 gate on story 1305 being ACTIVE at task 1) |
| `연결퀘스트` successor auto-offer | 1321->1322, 1313->1339, 1345->1346, Berlon chain |
| Dungeon entry conditions | `DungeonData_9036` on 1316, `DungeonData_9037` on 1346 |
| WorkObject window | template 134 on 1346 (both legs) |
| NPC appear/hide, Area access gate | ZERO |
| Achievement completion check | Six 13xx quests referenced: 1301, 1303, 1309, 1316, 1329, 1317, all live story quests; none trimmed or re-anchored (CORRECTED 2026-07-27, see note below) |

**CORRECTION 2026-07-27 (quest-design-review planning session).** The achievement row
originally read "ZERO of the 100 quest-completion achievements name a 13xx quest", measured
against `Condition templateId="1020"`. That is the WRONG condition type: all 100 of 1020's
`value2` ids are ITEM templates (quest materials, fishing, collection), so it is an
item-possession condition. The real quest-completion condition is `templateId="4012"` with the
quest global id in `value1` (286 conditions corpus-wide; 244 resolve to current quest files and
the remainder are legacy ids of removed quests). Measured correctly, six IoD quests ARE
achievement-referenced: 1301, 1303, 1309, 1316, 1329 and 1317. All six are live story quests;
no trimmed quest (1323, 1318, 1386, 1343, 1344) and no re-anchored quest (1324, 1328) appears
among them, so every trim in this wave remains safe. The safety model was wrong, the outcome
unaffected. Any future trim must check `4012` (and never `1020`) for achievement references.

Two structural facts make trimming cheap: **no story-spine quest depends on any zone quest**
(the spine's prerequisites are all Missions), and **QuestGroupList registers only the Missions**
(group 1 = 21, group 2 = 7), so no zone-quest trim touches story-group data.

Mechanism for every trim: `requirements.prerequisites: [9999]` (the 99,99 sentinel), the
publisher's own retire-in-place pattern, which keeps tasks, dialogs, strings and the
compensation row intact and is trivially reversible. Never delete the quest file.

Verification oracle: re-run `search_quests --continentId 13` after each trim. Its `reachable`
column walks the prerequisite chain, so an orphaned quest shows up as `enabled=Y reachable=N`.
A clean trim leaves every unreachable row reading `sentinel`, never `upstream blocked`.

### Trim 1: quest 1323 "Getting Some Answers" (spec 002/27, applied, gated, DEPLOYED to dev, awaiting live validation)

Three quests target mob 13,300931 Ghilliedhu: story 1304 (mandatory), 1322 (Kishale, plain
kill 5), and 1323. Task 1 of 1323 is field-for-field identical to task 2 of 1304: same monster,
same count 5, same 100% grant rate, same flag icon 87, same delivery NPC Dulari 213,1017. Both
pay 800 exp / 80 gold AND the same 12-row class weapon bag, so 1323's copy of the weapon is
always vendor fodder. Checked against v31 before concluding: the duplication is authentic BHS
data, not a spec 001/04 generator artifact.

The reference sweep found quest 1324's prerequisite to be the ONLY inbound reference to 1323 in
either tree. User ruled option A: sentinel 1323, re-anchor 1324 to 1322, so the chain becomes
1322 -> {1318, 1324 -> 1327} and the branch shape of the opening survives.

Applied in the full patch (70 specs / 9163 ops / 0 failed / 0 warnings). Footprint proven
exact: the server dirty SET grew by exactly the two intended files, each a one-line change
(`13,22`->`99,99` on 1323, `13,23`->`13,22` on 1324), and the client legs are the same single
line on shards `Quest-00345` / `Quest-00346`. No `선행퀘스트논리식` operator was introduced.
Both gates exit 0 (`audit_class_gates --zones 13,64,213,436` PASS 0 gaps;
`dungeon_audit --dungeons 9037` PASS 0 failures). Post-trim `search_quests` on HZ 213: 1323
reads `enabled=N reachable=N (sentinel)`, and all 6 unreachable rows are sentinels with zero
`upstream blocked`, proving nothing was orphaned.

Cosmetic residue accepted deliberately: Kishale's 1322 completion line ("...but it also spawns
questions...") was the tease for 1323 and now dangles as flavor. Closing it is a one-string
edit, separable from the structural change.

### Trim 2 + reward cadence: quest 1318 and the level-4 set (spec 002/28, applied, gated, DEPLOYED to dev, awaiting live validation)

**Trim.** Quest 1318 "Hunting the Beasts" retired by sentinel. Its collect-5-Noruk objective
repeats task 3 of 1327 (same giver Dulari, same mob 13,300921, same count, different turn-in
NPC); 1327 is the richer quest so 1318 is the one retired. Zero inbound references, so no
re-anchor was needed. v31 shipped it disabled.

**Reward cadence.** User design principle, recorded because it governs all future reward work:
**zone quests own POWER progression, story quests own LORE progression**, and the player must be
able to complete a full SET LOOK at each progression step, even when pieces are split across
quests.

The audit that drove it: gear grants across the whole zone follow a broken pattern where body
pieces sit on story quests and the matching hands/feet are mostly unassigned, so no set below
level 7 was completable.

| Look tier | Level | body | hands | feet |
|---|---|---|---|---|
| 003 | 3 | nobody | 1325 | 1322 |
| 005 | 4 | 1303 story | nobody | nobody |
| 006 | 5/6 | 1331 story | 1347 | nobody |
| 007 | 7 | 1305 story | 1305 + 1330 DUPLICATE | 1305 + 1326 DUPLICATE |
| 009 | 8 | 1315 story | nobody | nobody |

`linkLookInfoId` decodes as `{armourType}{slot}{tier}` (3=mail, 2=leather, 4=robe; 11=body,
12=hands, 13=feet), which is how a visual set is identified. Use it for any future set work.

Applied distribution: the level-4 set (17404-17412, complete 3x3, all requiredLevel 4, all one
visual tier 005, six of nine pieces previously granted by no quest in the corpus) moved onto zone
quests: **1322 feet, 1324 body, 1325 hands, 1319 the level-4 weapon**. Story quests **1303 and
1304 stripped to exp and gold**. The level-3 set is no longer granted at all.

**New-class weapon defect fixed, root cause in our tooling.** Brawler and Ninja were receiving the
SAME level-2 weapon from all three IoD weapon quests (1304, 1319, 1303) and never a mid-tier
upgrade; Valkyrie got the same level-3 glaive twice. Cause: the per-class weapon pools in
`gen_v31_reward_specs.py` and `gen_reward_specs.py` skipped levels 3 to 6 entirely, because those
classes' mid-tier weapons live in separate id ranges (`823xx`, `583xx`/`585xx`, `593xx`) instead
of continuing the base line, so nearest-requiredLevel fell back to the level-2 item. Both pools
now span the full band with per-id level comments. The same defect still exists OUTSIDE this
bracket: **quest 1315 (level 9, should pay the level-8 Kugai weapons) still hands the new classes
the level-7 First Expedition weapons.**

Applied in the full patch (71 specs / 9170 ops / 0 failed / 0 warnings). Verification: exactly one
new dirty server file (`001318.quest`, one line); a per-quest semantic diff of
`QuestCompensationData_13` against committed HEAD shows exactly the 6 intended quests changed
(plus 1380/1381/1387, which are spec 002/18's own patch-002 additions); and a completability check
confirms **all 12 classes assemble 3 slots at one visual tier plus a level-4 weapon**. Both gates
exit 0.

Accepted consequences, both live-test checkpoints: pieces are earned before they can be equipped
(carriers are minLevel 1-3, items require level 4), and a story-only player now wears starter gear
until 1305 at level 5 on mobs balance-multiplied x10 HP / x60 atk.

### Trim 3: the level 5-7 band, First Expedition set (spec 002/29, applied, gated, DEPLOYED to dev, awaiting live validation)

The pass scoped in the previous section, now done. Story quest 1305 granted the ENTIRE level-7
First Expedition set in one payout (48 rows, every one equipment: 3 armour pieces plus a weapon
per class), and zone quests 1326 and 1330 then granted duplicates of its feet and hands.

**Placement was chosen on measured travel distance**, using the Tower Base recall point
`66600.87,-79855.52` as the origin and a round trip of base -> giver -> nearest objective ->
turn-in -> base:

| Quest | Lv | Giver | Round trip | Piece |
|---|---|---|---|---|
| 1326 | 5 | Jirash 64,1023 (Tower Base) | 5,236 | feet (already granted, now unique) |
| 1330 | 5 | Taras 64,1028 (Tower Base) | 6,452 | hands (already granted, now unique) |
| 1332 | 6 | Kamarnu 213,1009 (Southern Checkpoint) | 29,513 solo | **body** (revised 2026-07-27) |
| 1333 | 6 | Jehan 213,1130 (Mysterious Ruins) | 24,776 solo | **weapon** (revised 2026-07-27) |
| 1348 | 5 | Tanli 213,1147 (mid-island) | 11,141 | none (was body until 2026-07-27) |
| 1349 | 7 | Ayrdoss 213,1126 (far west) | 35,240 | none (was weapon until 2026-07-27) |
| 1347 | 6 | Lorin 213,1128 | 26,927 | none |

**REVISED 2026-07-27 after live testing, carrot and stick.** The body and weapon were first
placed on 1348 and 1349 purely on distance. Live feedback: Ayrdoss stands **6,208 units past**
the Jehan/Lorin camp, still inside Mysterious Ruins but well beyond the NPC cluster, so the
weapon was out of sight and players skipped the quest. Moved to the **1332 -> 1333** pair
because 1332 already carries Kamarnu's power gauges WEST and hands them to Jehan, and Jehan's
existing turn-in dialog already sets up the follow-up: *"you will find no shortage of work here
in this camp. Perhaps it is best that you stay nearby. There are other tasks needing
attention."* The chest is therefore paid exactly where the next reward is visible, and 1333 is
Jehan's own tight loop (Cromos are 1,315 units away).

Travel: the old pair cost 11,141 + 35,240 = **46,380** as two separate round trips; the new pair
CHAINS (base to Kamarnu to noruks to Jehan 13,320, Jehan loop 2,620, Jehan to base 11,078) =
**27,018** for both pieces. The solo round-trip column above understates the new pair because
they are never done separately.

**The level 5-7 zone inventory is geographically lopsided**: only three quests sit inside an 11k
round trip and everything else is 25k to 35k, so a four-piece spread cannot be placed entirely
near the base. Hence armour near the base (the LOOK is never gated behind a trek) and the weapon
on the far quest, whose minLevel 7 matches the equip level exactly. **1332 is a trap worth
remembering**: its giver is 5k from base but its turn-in is Jehan 11k west, making it the second
longest round trip on the list. It is really the quest that migrates the player west.

Same pass corrected the rest of the stale new-class weapons: 1315 (was paying the level-7 First
Expedition weapons where others got level-8 Kugai, i.e. the exact weapons 1305 had already given
those classes) and 1316 (was paying level-12 where others got level-11).

Applied in the full patch (72 specs / 9175 ops / 0 failed / 0 warnings). Both gates exit 0. All
12 classes assemble 3 slots at one visual tier (007) plus a level-7 weapon.

### RESOLVED 2026-07-27: the 1326/1330 in-progress gate is gone

The DSL request below was filed and DELIVERED the same day, in commit `94707de7` "Make the quest
in-progress gate a clearable questId/taskId pair" (verified against binary `1.0.0+12a24535`).
`inProgress: []` now removes the element, matching the `prerequisites: []` precedent, and the
field became a `[questId, taskId]` pair so the task half is authorable, with a lone id rejected
by the new E211. Both issues in the request were delivered.

Adopted natively in spec 002/29: quests 1326 and 1330 carry `inProgress: []`. Verified as exactly
one deleted line per quest file, with a corpus sweep confirming no `0,0` and no empty
`<진행퀘스트 />` anywhere. No hand edit, no post-apply fixup, so the pipeline stays fixup-free.
**Server-only**: the client Quest XSD carries no `진행퀘스트` element, so the client shards for
these two never held the gate and no repack was needed for this leg.

The level-7 set is now completable without qualification, and the negative case (finish 1305,
then confirm Jirash and Taras still offer their quests) becomes a live-test checkpoint rather
than a known hole.

### The original blocker, kept for the record

Quests 1326 and 1330 carry `수행조건/진행퀘스트` = `1305,1`, so they are only offerable while
story quest 1305 is ACTIVE. They now carry the level-7 feet and hands, so a player who completes
1305 without visiting Jirash and Taras loses those pieces permanently and the set stops being
completable. The gate should have been removed in spec 002/29 and could not be:

| Attempt | Result |
|---|---|
| `inProgress: 0` | writes `<진행퀘스트>0,0</진행퀘스트>`, **zero occurrences** in the 2,710-file corpus |
| `inProgress: null` | W503, produced no commands, element untouched |

The canonical no-gate form is the element being ABSENT (2,673 of 2,710 files). `0,0` plausibly
reads as "quest 0,0 must be in progress", which would make both quests permanently unofferable,
the same failure as the `99,99` prerequisite sentinel. Not shipped, per the project's own hard
lesson about shapes with zero corpus occurrences. Both probes were run against the working tree
and reverted. Filed as `docs/dsl-requests/2026-07-27-quest-inprogress-clear.md`.

Practical exposure is limited because Jirash and Taras stand AT Tower Base, where 1305's own
giver Adria stands and where several of 1305's visit tasks return, but it is real and it is the
one open hole in the level 5-7 set.

### Verification-method correction, worth not repeating

The per-quest reward regression diff was first run with a regex block extractor
(`<Quest questId="N">.*?(?:</Quest>|/>)`, non-greedy). That stops at the first `<Item ... />`
inside the block, so it compared only each quest's CompensationType header and silently reported
1315 and 1316 as unchanged when their rows had in fact changed. Redone with ElementTree, which
gave the true answer: 14 quests differ from committed HEAD, being the 11 touched by specs 002/28
and 002/29 plus 1380/1381/1387 from spec 002/18. **Compare compensation blocks with a parser, not
a regex**: the block contains self-closing children, so any lazy terminator match truncates it.

### Trim 4: the level 5/6 gear step removed (spec 002/30, applied, gated, DEPLOYED to dev, awaiting live validation)

User ruling 2026-07-27: no set between the level-4 and level-7 steps. A sweep of the whole
zone-13 reward table for equipment at level 5 or 6 returned exactly two quests, both stripped:
**1331** (story, level-5 Family Ties body) and **1347** (zone, level-6 Rockhound hands). Both
keep their exp and gold; every row on both was equipment. Re-swept after apply: **zero** residual
level 5/6 equipment grants in zone 13.

The tier-006 look was never completable anyway (its feet 17712/17715/17718 are granted by no
quest in the corpus), so this removed a partial set rather than a working one.

### THE GEAR LADDER, as it now stands

| Band | Set | Source |
|---|---|---|
| levels 1-4 | level-4 set, look tier 005 | zone quests 1322 feet / 1324 body / 1325 hands / 1319 weapon |
| levels 5-7 | level-7 First Expedition, tier 007 | zone quests 1326 feet / 1330 hands / 1332 body / 1333 weapon (body and weapon revised 2026-07-27, were 1348 / 1349) |
| level 8 | Kugai set | Kugai's Crest token shop (spec 002/20), tokens drop from Kugai 13,1004 |
| in between | nothing | by design |

Story quests 1303, 1304, 1305, 1331 now grant exp and gold only.

### Trim 5: quest 1315 stripped, the Kugai set belongs to the token shop (spec 002/29 amended)

The Kugai token shop (spec 002/20) sells the COMPLETE level-8 set: all 12 weapons
(12137-12144, 55272, 58523, 59320, 82272) at 30 tokens, chest 17413/17416/17419 at 30, gloves
17414/17417/17420 at 15, boots 17415/17418/17421 at 15, with Kugai's Crest dropping 10 per kill
from Kugai 13,1004.

Story quest 1315 "Putting the Pieces Together" was granting the 12 Kugai weapons plus the 3
chest pieces outright: the shop's entire weapons tab and its chest row, for free. Stripped to
exp 4500 / gold 450 (user ruling 2026-07-27). The three new-class weapon rows spec 002/29 had
just corrected on 1315 are moot as a result; the token shop already sells the correct level-8
items for those classes, so nobody is left short. 1316's correction stands.

Implemented by AMENDING spec 002/29 rather than layering a spec 31 over it, so each quest keeps
one authoritative statement in the patch. Legitimate because patch 002 is still open and specs
are replayed wholesale from the committed baseline every run.

### Trim 6: quest 1386 "Bombs Away" (spec 002/32, applied, gated, DEPLOYED to dev)

Retired by sentinel. It is a near-exact duplicate of the story quest that gates it: 1386's
prerequisite IS 1329 "Going Above and Beyond", and it repeats 1329 task for task (same giver
Jorhon, same Visit to Kiriya on the same dialog granting the same injected item 5002, same Hunt
of 3x training dummy 13,888, same Visit back deleting 5002), differing only by a trailing
"report to Jorhon" step. The reward duplicates as well: 1329 pays 10x Bomb I and so does 1386.
The player was doing bomb training twice in a row from the same NPC.

1328 "Academic Theft" was the only inbound reference anywhere and is re-anchored to **1329**,
which preserves its gate position exactly rather than loosening it, since 1386 was itself gated
on 1329. Chain goes `1303 -> 1329 -> 1386 -> 1328` to `1303 -> 1329 -> 1328`.

Nothing orphaned, checked explicitly: monster 13,888, item 5002 and NPC Kiriya 64,1029 are all
still used by 1329, and Kiriya also gives 1384. Server diff is exactly two lines, one per quest
file. Post-trim `search_quests` on HZ 64: all three unreachable rows read `sentinel`, zero
`upstream blocked`. Both gates exit 0.

### Trim 7: the post-arc pair 1343 and 1344 (spec 002/33, applied, gated, DEPLOYED to dev)

Both retired by sentinel. They sit behind story climax 1316 at minLevel 9, offered only once
the player has finished essentially everything else, and the user ruled they add no value there.

Retiring BOTH together needed **no re-anchor**: 1343's only inbound reference is 1344's
prerequisite, and 1344 has no inbound reference at all, so the pair is a closed tail off 1316.
After the trim the only live quest still gated on 1316 is the story finale 1317.

Shared assets checked per NPC and per mob rather than assumed, all survive: Sersine keeps 6 live
quests, Leander keeps 1305, Perrin keeps 1340, destroyer mob 13,9 keeps 1309/1316/1335.

**Gregor 213,1028 is the one consequence.** He is referenced by no other quest in either state,
so he becomes the zone's only quest-less NPC. He is not orphaned: he keeps his spawn and his
`VillagerDialog_213` entry and carries no `VillagerMenu`, so he stays a talkable flavour NPC at
the gorge outpost with no dangling service wiring, he simply loses his quest marker. Re-enabling
either quest restores his role.

**Content lost, recorded so it is not rediscovered as a bug.** 1343 carries the island's ONLY
Karascha reveal: Leander translates Kugai's codex, names Karascha as the power behind the
corruption, raises Lok (a god thought dead since the Divine War) and ties Karascha to Elleon's
fate, with cutscene 121310081 on the delivery. That lore exists nowhere else in the zone. 1344
carries no unique lore, but its 3000 exp was the second largest zone-quest payout after 1346, so
the level 9 band loses a noticeable chunk; the spine's self-sufficiency to level 10 is unaffected
since it never depended on either.

Also worth knowing: 1343 was `cancellable=불가능`, so a player who accepted it could never
abandon it and it would sit in the journal permanently once the arc ended.

Server diff is exactly two lines, one per quest file. Post-trim `search_quests` on HZ 213: all
nine unreachable rows read `sentinel`, zero `upstream blocked`. Both gates exit 0.

### Standing note on retired quests: compensation rows are left populated

1323, 1318 and 1386 all keep their populated `QuestCompensationData` rows. The publisher's own
soft-disable pattern also reduces the row to an empty stub, so if the full pattern is wanted
these three should be normalised together in one op rather than diverging per quest. Populated
rows on unreachable quests are inert (they can never pay out) and the zone already carries 12
such orphan entries from quests with no file in either era.

### FULL GEAR AUDIT of zone 13 after this wave

Every remaining equipment grant in the zone-13 reward table:

| Quest | Live? | Grants |
|---|---|---|
| 1322 / 1324 / 1325 / 1319 | yes | the level-4 set: feet / body / hands / weapon |
| 1326 / 1330 / 1332 / 1333 | yes | the level-7 First Expedition set: feet / hands / body / weapon (body and weapon revised 2026-07-27, were 1348 / 1349) |
| 1316 | yes | level-11 weapons (STORY quest, still granting gear) |
| 1317 | yes | level-11 body (STORY quest, still granting gear) |
| 1310 | NO, sentinel | a full level-7 set plus weapons, inert (cut subplot, disabled in both eras) |
| 1323 | NO, sentinel | the level-2 weapons, inert (retired by spec 002/27) |

Story quests 1303, 1304, 1305, 1315 and 1331 now grant exp and gold only.

### RESOLVED: quest-objective starvation on 1319 and 1348 (spec 002/31, applied + gated)

Fixed by converting a share of the co-located ambient terrons into their combat variants
(alternative A, user ruling 2026-07-27), NOT by widening the quest accept list.

| | 1348 | 1319 |
|---|---|---|
| Converted | 4 of 10 territories in group 1300022 (2 to 302, 2 to 303) | 6 of 17 in group 1300019 (3 to 300944, 3 to 300941) |
| Credit mobs | 10 to 22 | 17 to 35 |
| Expected items per full clear | 6.1 to **12.5** (needs 8) | 9.3 to **18.1** (needs 5) |
| Ambient left | 30 to 18 | 51 to 33 |

Two details worth carrying forward:

- **AI alignment matters on a retarget.** The ambient spawns carried a spawn-level `ai="108"`
  (environment behaviour) while every existing credit mob in 1300060/1300061 carries `ai="6"`.
  Retargeting the template alone would have left the SAME template running two different AIs
  about 11 units apart, so a converted Terron Ringleader would behave differently from its
  twin. Each op sets `ai: 6` as well. Check this on any future spawn retarget.
- **`desc` is deliberately stale** on converted spawns, still reading "(환경몬스터)자연의 정령".
  It is an internal authoring comment; the player-visible name comes from StrSheet_Creature
  keyed by (hz, templateId). Same lesson as the Acharak fix.

Client leg done: `gen_npcloc.py --prune` regenerated 146 entries, 0 void. Marker sets moved
302 6 to 8, 303 4 to 6, 300944 10 to 13, 300941 7 to 10, and 102 83 to 73.

Note the DSL request filed for the quest-side approach was DELIVERED the same day (commit
`2a41fa95`, "Author hunt task monster lists with per-entry grant rate and kill count"), so
`targets` lists with per-entry `grantRate` and kill count are now authorable if a future pass
wants to widen an accept list rather than move spawns.

### The original analysis, kept for the record

Live testing surfaced that both terron collect quests are starved of credit mobs, and the cause
is ours: spec `001/15`'s padding authored the bespoke groups 1300060/1300061 by placing the
quest-target terrons at **the exact coordinates of pre-existing ambient Docile Terron
territories** (offset about 11 units). Every point holds one mob that counts and three that
do not.

| | 1319 | 1348 |
|---|---|---|
| Needs | 5 terronite | 8 petals |
| Targets | 300944 @85%, 300941 @12% | 302 @90%, 303 @17% |
| Credit mobs at the spot | 17 | **10** |
| Ambient mobs at the same points | 51 (group 1300019) | 30 (group 1300022) |

1348 is the bad one: 8 items from 10 mobs on a 20-second respawn with the secondary at 17%.

The only other terron at either spot is `13,102 Docile Terron`, an environment mob
(`(환경몬스터)자연의 정령`, aiid 108, playStyle creature). It IS a real killable NPC, not a prop:
same shapeId 300940, same parentId, same Abnormality/Aggro/Reaction blocks as the combat
variants, differing only in AI and tuning. Corpus check: only 3 of 3,785 hunt-target references
are playStyle=creature and just 2 are true environment mobs, so it is rare but not invented.
Journal text on both quests is generic ("the terrons", "petals from terrons near the Southern
Checkpoint"), so widening needs no string change.

**BLOCKED as asked**: the DSL models `HuntAndDeliverTask` targets as a single `targetId` int with
no list form and no `수여확률` property, so a third monster entry cannot be authored. Filed as
`docs/dsl-requests/2026-07-27-hunt-task-multi-target-and-grant-rate.md` (corpus evidence: 611 of
1,853 hunt tasks carry 2+ entries, up to 28; 582 carry explicit grant rates).

Two TerritoryData-only alternatives reach the same outcome today, both awaiting a user decision:
- **Alt A (recommended)**: retarget a share of the ambient spawns to the combat variants at the
  same points (e.g. 4 of 10 group-1300022 entries 102 -> 303; 6 of 17 group-1300019 entries
  102 -> 300941). Precedent: spec `002/21`. Also thins the non-credit clutter.
- **Alt B**: raise `spawnCount` on our authored groups 1300060/1300061 from 1 to 2 or 3.
  Precedent: the 2026-07-21 density pass.

### Remaining gear work, not yet done

- ~~The 1326/1330 in-progress gate~~ RESOLVED 2026-07-27, see above. The level-7 set is
  completable without qualification.
- **Quests 1316 and 1317 still grant level-11 gear from story quests**, which is the same shape
  the rest of this wave removed, one tier above the Kugai step. The level 8+ zone quest inventory
  has not been surveyed for carriers, and there is no token economy above Kugai yet, so this is a
  design question rather than a mechanical trim.

### Observations parked for the trimming wave

- ~~Noruk 13,300921 is doubled~~ RESOLVED by spec 002/28 (1318 retired).
- ~~The Dulari arc pays no gear at all~~ RESOLVED by spec 002/28 (1324 now carries the level-4
  body piece). 1327 still pays an empty item bag, as do 1302, 1321, 1328 and 1348.
- 20 of the 34 restored zone quests are a single Hunt or HuntAndDeliver task, which is very
  likely the shape the testers reacted to.
- The level-3 set (17701-17709) is now granted by nothing. Its pieces stay in the data and are
  available if a future pass wants a pre-level-4 step.

### MCP deficiencies catalogued this session (file as one detailed request once the wave ends)

1. `진행퀘스트` in-progress gates are invisible to BOTH `search_quests` and `audit_quest_chain`.
   Quests 1326 and 1330 gate on story 1305 being active and both tools report no prerequisite
   whatsoever. Found only by parsing raw headers.
2. `search_quests` `reachable` does not account for those in-progress gates, so such a quest
   always reads reachable even when its gate quest is unobtainable.
3. No inbound/reverse reference query exists. `trace_quest_sequence` walks one quest's
   prerequisite tree backward, but there is no "what depends on this quest" view, and nothing
   covers the non-quest binding families (DungeonData conditions, WorkObjectData windows).
   Had to write a scratch script for it; that script is the spec for the request.
4. No reward-set comparison, so an exact duplicate like 1304 vs 1323 must be eyeballed across
   two calls.

## Session handoff (2026-07-26, fourth session): quest log reward panel

Opened as a zone-quest audit of 1325 "The Perfect Cut" (Leolin 213,1121) and turned into a
root-cause hunt when the user reported that accepted quests lose their item reward in the quest
log while the accept dialog and the payout stay correct.

### Root cause (fixed, deployed, LIVE-VALIDATED)

`QuestCompensationData` is **not server-only**. The client DataCenter ships 153
`QuestCompensationData` shards and the quest log reward panel reads them. We had
`questCompensations` mapped to `None` in migrate's `ENTITY_SYNC_MAP`, inherited from the domain
KB's blanket claim that all compensation families are server-only (true for C/E/F/I, false for
this one), so every reward row we ever wrote stayed server-side.

Proven from the protocol definitions rather than inferred: `S_DIALOG` carries a `questRewards`
array including `items`, so the accept window is server-fed and always right; `S_QUEST_INFO`, the
only journal packet, carries **no reward fields at all**, so the log cannot be server-fed; and the
client `Quest` shard holds no reward data either. `gold` and `exp` are attributes on
`CompensationType` so they always render, while `Item` rows are class-filtered, which is why the
defect presented as "gold and XP fine, item missing" and only for the three new classes.

Measured on zone 13 before the fix: 64 item rows server-only across 15 quests (all
assassin/fighter/glaiver plus one engineer row on 1310), 7 quests absent from the client table
entirely (1353-1358 Berlon chain, 1387), and 1380/1381 showing a stale 5 gold / 50 XP against the
server's 150 / 2100.

### Fix

`config/sync-config.yaml` gained a `QuestCompensationData` entity (`SourceMapped`, `id_attribute:
questId`) and `migrate.py` maps `questCompensations` to it. **Scoped to one pair (zone 13)**
deliberately: zone 13 is the only quest reward table this project has ever modified, and mapping
only what we own keeps a game-wide reward rewrite out of the patch. Add a pair per new zone or the
sync skips it silently; the content-verified full 153-pair mapping is in
`docs/plans/questcomp-client-sync.md`.

`SourceMapped` rather than the semantically correct `ZoneBased` because two DSL gaps block the
latter, both filed: `server_path` is IdSorted-only so ZoneBased cannot reach `CompensationData/`,
and ZoneBased auto sequence assignment misaligns (156 server zone files vs 153 client shards, with
zones 620/622/628 having no client shard and sitting mid-ordering).

Patch 002 replayed clean (68 specs, 9149 ops, 0 failed, 0 warnings). Semantic diff of shard 00012
against committed HEAD: 77 to 84 quests, **zero rows lost**, 15 quests gained class rows,
additions only. Both gates exit 0. Client published `0.1.0-dev.37` (16 new chunks, committed=True).
No server restart needed: the server table was always correct, which is exactly why the payout
worked while the log lied.

### Side effect, recorded

Quests 1361-1368 lost their vestigial client-side 5 gold / 50 XP stubs to match the server's empty
stubs. None of the eight has a quest file in either era, so they cannot be accepted. Not a
divergence from v31, just server-authoritative alignment.

### Audit finding on 1325 itself (no defect)

The quest is a faithful restore: body, dialogs and strings are byte-equal to v31, the only deltas
being the doctrine-sanctioned enable and the three new-class reward rows, which correctly mirror
each item's own `requiredClass`. One doc correction fell out: the doctrine's stated reason for
omitting soulless ("no base-game low-level gear") is wrong for the ilvl17 family, since
`leather17_hand` explicitly admits SOULLESS. The operative reason is that Reaper never plays IoD.

### Recall network restored (spec 002/26, 2026-07-27, deployed, LIVE-VALIDATED)

Second regression found in the same session, from a user report that the teleport scroll sent
players to North Dock instead of the Tower Base.

The scroll item is not at fault. Item 133 (Tower Base Teleport Scroll, skill 60130101, `SER_POS`)
carries an explicit destination that is byte-identical across the v31 server, the v92 server and
the v92 client shard, and resolves inside section 64001 Tower Base in both eras. Patch 000's fix is
intact. The scroll players actually carry is **item 160** (Safe Haven Teleport Scroll, skill
60130100, type **`MYSELF_VILLAGE`**), which carries no coordinate: the destination is read from the
AreaData section the player stands in, via `recallScrollPos`. Death works the same way through
`recallRevivePos`.

v31 sets `recallScrollPos` to the Tower Base on all 20 continent-13 sections, uniformly. v92 had
repointed 12 of its 21 to `93957,-89037,-4554`, which `resolve_position` places in North Dock. The
decisive one is the ROOT section 4 (13001), the catch-all covering the whole island.

**Why patch 001 missed it:** spec 001/00 wrote these attributes correctly on every section it
authored in full (hence the 9 already-correct sections), but the root section was not in the port
list, 13004/13007/13030 were partial realign upserts whose attribute list omitted them, and
13003/13006/13024/13028 existed in both eras so the diff dispositioned them MATCH on identity and
fence geometry **without comparing section attributes**. That is the reusable lesson: a MATCH
verdict on a section means the fence matched, not that the section matched.

Ruling (user): restore all three parts. The 8 classic sections take exact v31 values; the 4 kept
v92-only camp sections are repointed too (their `vender`/`restBonus` flags advertise a service layer
that does not exist, since all 9 merchants filed under the HZ-13 camp layer are PHANTOM while the
real cast stands at the Tower Base); and `recallRevivePos` is restored, noting v31 is NOT uniform
there and deliberately localizes three northern sections to `87533.2031,-83932.6797,-4533.1616`.
Camp revive points were derived from the v31 section whose fence contains each camp, not invented.

Applied in the full patch (69 specs / 9161 ops / 0 failed / 0 warnings). Server diff is exactly 12
insertions and 12 deletions on one file, every changed attribute a `recall*` value. Both gates exit
0. **Server-only:** the client `Area` family did not change, so client `0.1.0-dev.37` stayed
current and no republish was needed. Deployed to dev (71 files, all hash-verified).

**LIVE-VALIDATED 2026-07-27** by the user: both the Safe Haven scroll and death resurrection land
correctly. The methodological lesson (a MATCH verdict states which fields were compared, and
geometry equality is not section equality) is recorded in `../ZONE-PORT-PLAYBOOK.md` phase 3.

### Next

1. Still outstanding from earlier sessions: live-test Brawler + Valkyrie on the new-class spine and
   the wrong-class negative case (Dulari refusing).
2. Spot-check dungeon 437 (Sorcha, quest 1346) with matching client data.
3. Then close patch 002 with one commit per datasheet repo.

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
