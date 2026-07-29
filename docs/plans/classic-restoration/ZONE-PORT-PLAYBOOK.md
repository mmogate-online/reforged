# Zone Port Playbook (v31-primary)

How to port a zone's v31 state onto the v92 server, exactly as validated end to end on Island of
Dawn (2026-07-20, single session, live-tested and committed). Prime any zone-migration session
with: this playbook, `DOCTRINE.md`, the zone's scope doc, and the skills listed per phase.

Orchestration model that worked: main agent orchestrates, reviews, and adjudicates; Opus
subagents execute (diffs, spec authoring, verification); every DECISION row comes back to the
orchestrator; user rules on policy (blast radius, content exclusions).

## Priming (before any phase)

- Read: `DOCTRINE.md` (rules + adaptation whitelist), the zone scope doc (`docs/patch-XXX-scope.md`
  convention: enumerate ALL layered hunting zones + hub layers + dungeons, never just the combat HZ),
  `packages/README.md` (archetypes), the prior zone's tracker for precedent rulings.
- Skills: `content-restoration`, `domain-research`, `new-spec`, `dsl-definitions`, `apply-spec`,
  `quest-live-test`. Domain docs routing for NPC dialog and quest editing is in `domain-research`.
- Paths from `.references`: `v31_datasheet`, `client_dc_v31`, `server_datasheet`,
  `client_datacenter`, `old_client_dc` (padding only), `dsl_cli`.

## Phases

| Phase | Work | Gate to next |
|-------|------|--------------|
| 0 | Zone folder (`classic-restoration/<zone>/`: TRACKER.md, data/, divergence-log.md) | Folder + tracker exist |
| 1 | Salvage pass over prior work for the zone (CARRY-OVER / REWORK / RETIRE per spec, verified against v31 data, not assumed) | Manifest adjudicated |
| 2 | Three-surface revert: server repo stash, client-dc repo stash, dev overlay `deploy_dev.py --revert --yes` (stash labels dated; recoverable, never hard delete) | All three clean |
| 3 | Per-family v31-vs-v92 diffs, parallel agents (see family list), every row dispositioned | All DECISION rows adjudicated |
| 4 | Spec authoring from diffs (parallel agents per family) + carry-over renumbering + patch README | All specs validate clean; op counts reconciled |
| 5 | Migrate batch apply + reconciliation gate + client legs + deploys | Gate all-PASS |
| 6 | User live validation, then baseline-lane commits, then `/log-progress`, then dependent-patch rebase | User confirms live |
| 7 | Padding (two levels per doctrine rule 4; separate brief) | n/a |

## Phase 3: diff families and the diff model

Agents (parallelizable): spawns/territories; quests (headers, sentinel set, task trees, rewards,
story groups, dialogs); shops (bindings AND store contents); sections + region strings + worldmap;
client-registry readiness. Verdicts per row: PORT / MATCH / KEEP (stated reason: patch-000, new
class, engine-spawned, salvage) / REMOVE / DECISION. Method rules learned the hard way:

- Query with the MCP first; parse raw XML only for what it cannot answer. The staleness
  hazard that once forced raw-first is fixed (2026-07-25): cached indexes rebuild when their
  files change, so a post-apply or post-revert read is current, and `datasheet_freshness`
  reports per-family `current` / `stale` / `not-yet-built` on demand. Check it after a revert
  instead of probing a known marker. Trust raw files on any disagreement, and treat a
  disagreement as a bug report worth filing.
- Run `audit_quest_gates --huntingZoneId <hz>` over every zone in scope before authoring.
  It names the quests whose contact NPCs or kill/collect targets nothing spawns, which is the
  "MATCH in the diff but unspawned in the world" miss that this phase exists to catch.
  Run `find_dormant_blocks` on the spawn families too: commented-out content is invisible to
  every other tool by design, and BHS ships whole territory groups that way.
- Expect the baseline to be closer to v31 than assumed: IoD TerritoryData was 100% identical
  (whole family became a no-op) and the quest spine matched fully except rewards. Diff first,
  never assume work exists.
- SECTION-ATTRIBUTE TRAP: a MATCH verdict must state WHICH fields were compared. The IoD
  sections diff compared fences vertex-exact and dispositioned same-id sections MATCH, but
  never compared their attributes, so `recallScrollPos` / `recallRevivePos` silently kept
  v92 values on 12 of 21 sections. v31 sent every section's recall scroll to the Tower Base;
  v92 sent 12 of them to North Dock, including the ROOT section that catches the whole
  island, so the zone's teleport scroll and death-revive both landed players in the wrong
  place for a year of sessions (found live 2026-07-26, fixed by spec 002/26). Geometry
  equality is not section equality. Diff the attribute set explicitly, and give any
  behaviour-bearing attribute (`recall*`, `campId`, `vender`, `restBonus`, `priority`,
  `disableItemId`) its own row. The same caution applies to partial "realign" upserts: they
  merge ONLY the attributes listed, so a realigned section keeps every v92 value you did not
  name. Note the destination-carrying attribute may live on the SECTION rather than the item
  or skill that appears to own the behaviour: `MYSELF_VILLAGE` recall skills carry no
  coordinate at all.
- SHOPS TRAP: diff a merchant's EXCLUSIVE tabs and its SHARED lists separately. Shared lists
  (game-wide BuyLists) have blast radius: measure the consumer count and make it a DECISION.
  IoD precedent: user ruled shared stores port to v31 game-wide WITH documented side effects
  (enumerate per-list what non-zone merchants gain AND lose in the spec header + divergence log).
- REWARD SHEET: check for empty-stub compensation rows (v92 wiped whole zones); new-class
  adaptation rows append per whitelist entry 2 (internal names; soulless omitted).
- Dead wiring (menus/dialogs bound to templates that never spawn) = KEEP-INERT, zero churn.
- Cross-check quest task targets against their own dialog LinkCreature tokens (internal
  inconsistency scan); dormant contradictions are fixed only when enabled.

## Phase 7 padding: era-client research surfaces

- **StrSheet_NpcLoc as a position and identity source.** The era client's StrSheet_NpcLoc
  holds one quest-marker world coordinate per (huntingZone, templateId) for every
  quest-linked template of that era, and the marker SURVIVES for NPCs the server never
  spawned. Use it to: (1) recover approximate spawn positions for never-spawned quest
  givers (author at the marker, point-in-polygon against AreaData fences to name the camp,
  nearest-neighbor check against live TerritoryData, tune heading and spot in-game; NpcLoc
  carries no heading); (2) track identity divergence: the same (hz, templateId) carries a
  DIFFERENT name in the English clients vs the KR-based v92 server for most villagers (a
  NA/EU vs KR localization split, stable over eras; the server's English StrSheet_Creature
  is stale). Always match cross-era NPCs by (hz, templateId), never by display name, and
  keep a per-zone EN/KR identity census (IoD example: iod/data/padding-npcloc-sweep.md).
- Mob habitat geometry still comes from era-client TerritoryData fences (doctrine rule 5);
  NpcLoc markers cross-validate fence centroids and can place quest-target mobs whose v17
  territories are missing.

## Phase 4: authoring rules

The general spec-authoring and regression-diff discipline is NOT restated here: read the
entity's capabilities before choosing an operation (`new-spec`, "Read the entity's
capabilities before choosing the operation") and prove the applied footprint afterwards
(`apply-spec`, "Prove the change is exactly what you intended"). Those apply to every spec in
the project, restoration or not. What follows is only what is specific to a zone port.

- Generators first (deterministic, re-runnable, live in `tools/dc-restore/`); definitions
  packages (`$extends`) where a repeated shape exists; rewards are known unfactorable.
- Idempotent upserts + explicit deletes only; never create-ops. Provenance header per spec
  (doctrine pointer, source, diff artifact, ruling numbers).
- VALIDATE HAZARD: `dsl validate` is green on ops that decompose to zero commands, and a spec can
  document an op in its header while missing the op body. Always reconcile REPORTED op counts
  against the adjudicated op list, and grep the spec for each ruled key.
- Check EVERY top-level YAML key against migrate's `ENTITY_SYNC_MAP` before applying (the
  `newWorldMap` key was silently unmapped and would have skipped client sync).
- Parent-delete CASCADE is real (territory delete removes child spawns): prefer one cascade
  delete over ordered child+parent deletes.
- Quest work gets a DESIGN review as well as a correctness one:
  `python tools/dc-restore/audit_quest_design.py --zones <zones> --since HEAD` (advisory,
  always exit 0). Duplicate rewards, gear sets nothing completes, objectives the zone cannot
  supply, and references into disabled quests are all invisible in a spec diff. See the
  `quest-design-review` skill.

## Phase 5: apply, verify, deploy

1. `python tools/migrate/migrate.py --patch <NNN>` (batch ONLY; single-spec `dsl apply` replays
   source-ref and wipes sibling changes on shared files). Re-apply after a spec fix: revert the
   server tree first, replay the whole batch.
2. RECONCILIATION GATE (dedicated agent): per family, deep VALUE-level compare of applied state
   vs v31 targets plus a no-drift check on untouched families. Key-level checks are not enough:
   the gate caught a class-row collapse (rows sharing a templateId across classes) that key
   coverage missed. Re-run the gate after every replay.
3. Client legs: migrate syncs mapped families; then `gen_npcloc.py --prune` (fence-centroid
   positions for pos-0,0,0 spawns; VALUE-check against the v31 client registry, not just keys);
   families with no sync entity (MapDefineData, client VillagerDialog shards) are documented
   hand edits with dangling-proofs.
4. Deploy: `deploy_dev.py --verify` (server; world restart is manual, user does it), then
   `deploy_client.py --pack --install --note`, then `--publish --note` (game client must be
   CLOSED for publish). Warnings on replay against an already-applied HEAD are expected
   absent-delete warnings; anything else investigate.

## Phase 6: validation and commits

- Live test per `quest-live-test`: derive checkpoints from the spec diff; do not jump past the
  accept step. Divergence-log rows each get a checkpoint (adaptation rows especially).
- Commits are baseline-lane, single-line messages, both repos (server + client-dc), only after
  the user confirms live. Then `/log-progress`, then rebase dependent patches.

## Family map (where things live)

Measured at server datasheet `789fec28` over all 2,707 quests present there: 1,969 carry the
`보상` flag on exactly the last task, 729 carry it on several tasks, and 9 carry exactly one
that is NOT the last. Treating "reward on the final task" as a rule is wrong for 738 quests.

| Family | Server | Client | Sync |
|--------|--------|--------|------|
| Quest bodies | `QuestData/00NNNN.quest` (sentinel disable = prereq `99,99` OR `99,9999`; the `보상` reward flag is NOT an invariant) | per-quest shards | Quest entity |
| Quest strings | monolithic `StrSheet_Quest.xml` (rows NNNN001+) | 2879 opaque shards | shard-routed |
| Quest dialogs | `QuestDialog/QuestDialog_<gid>.xml` (one PER QUEST) | shards | QuestDialog entity |
| Rewards | `CompensationData/QuestCompensationData_<hz>.xml` | `QuestCompensationData` shards (153) | QuestCompensationData entity; **zone 13 only** is mapped, add a pair per new zone or the sync skips it silently (`docs/plans/questcomp-client-sync.md`) |
| Spawns | `TerritoryData_<hz>.xml` (groups > territories > Npc/Party; pos 0,0,0 = random-in-fence) | none | TerritoryData |
| Villager menus | `VillagerData/VillagerMenu.xml` (`hz,tpl` -> Menu entries) | synced | VillagerMenu |
| Ambient NPC lines | `VillagerDialog/VillagerDialog_<hz>.xml` | per-villager shards | NONE (hand edits; DSL entity broken, request filed) |
| Speech selectors | `VillagerData/<hz><id>.condition` | n/a | speechConditions (server-only) |
| Sections | `AreaData/AreaData_*` (commented-out blocks are re-enable candidates) | synced | AreaData |
| Worldmap | `WorldMap/NewWorldMapData.xml` | monolithic client file | merge-by-id; NO section-level delete (request filed) |
| Creature names | `StrSheet_Creature.xml` | `StrSheet_Creature` shard | **StrSheet_Creature** (entity `creatureStrings`) |
| Quest-link registry | `StrSheet_NpcLoc.xml` (imported 2026-07-28, committed `cdca4fb4`) | `StrSheet_NpcLoc` shard | **StrSheet_NpcLoc** (entity `npcLocStrings`, keyed on the PAIR `(huntingZoneId, templateId)`). `gen_npcloc.py --out <spec> --prune` emits a SPEC; it no longer writes any datasheet |
| Gather-node registry | `StrSheet_CollectionLoc.xml` | `StrSheet_CollectionLoc` shard | **StrSheet_CollectionLoc** (entity `collectionLocStrings`) |
| Minimap labels | none | `MapDefineData/*` | none; hand edits with dangling proof |
| Shops | `BuyMenuList.xml` + `BuyList.xml` (shared tabs game-wide) | MenuList | buyMenuLists synced; buyLists server-only |

## Client-only families: use `dsl import`, not a hand-written client edit (2026-07-28)

The server datasheet is the source of truth and `sync` propagates it. A family that ships ONLY
in the client used to be unauthorable, so this project wrote it directly into the client
DataCenter with a bespoke tool. That is a workaround and it is now being retired.

`dsl import` is the inverse of `sync`: it merges a client family's shards into one server-format
file and drops the novadrop namespace. It reads the SAME `sync-config.yaml` descriptor that sync
reads, inverted, so the two directions cannot drift. **A family must be registered in
`sync-config.yaml` before it can be imported.** Per-family workflow: add the descriptor, run
`dsl import --dry-run`, import, then **sync straight back and confirm the client tree is
unchanged**. That round-trip is the only check that proves the import did not mangle the family.

Why this matters beyond tidiness: a tool that writes the client directly puts its output in the
tree that is NOT reproducible from specs. A patch replay cannot regenerate it, and a stash of the
client tree silently discards it. That is exactly what happened on 2026-07-28, when a full patch
002 revert-and-replay dropped the `StrSheet_NpcLoc` regeneration and the loss was invisible in
the migrate output, which read 0 failed and 0 warnings.

**Verify with an actual sync and a client diff, not a dry-run.** A dry-run reports the plan, not
byte-stability. Registering `StrSheet_Creature` planned clean and then rewrote the client on the
first real sync: three duplicate `<HuntingZone id="183">` wrappers merged (428 blocks to 426,
all 17,755 rows preserved) and two `class="True"` values normalized to lowercase by the boolean
fix in `3976613a`. Both correct, neither predictable from the plan. Expect a first-adoption
rewrite when registering a family that was never synced, check it explicitly, and confirm a
second sync writes 0 files.

**Adopted, all three**: `StrSheet_Creature`, `StrSheet_CollectionLoc`, `StrSheet_NpcLoc`.

NpcLoc was briefly blocked because it is keyed on the pair `(huntingZoneId, templateId)` and
`composite_id_attributes` was silently ignored on `monolithic`, collapsing 4101 rows to 1018. The
DSL team delivered the fix the same day (`48fefbae`, which also refuses a mass-collapse import,
plus `530f0038` onboarding the `npcLocStrings` and `collectionLocStrings` entities). Imported at
4101 of 4101 rows, round-tripped byte-stable, committed as `cdca4fb4`.

**Read the dry-run's duplicate-collapse line every time.** It is what caught the wrong key, and
it named the ids (all `1`, the giveaway). Without it, "imported 1018 record(s)" reads as success.

**A generated registry belongs in a SPEC, not written into a datasheet.** `gen_npcloc.py` now
takes `--out <spec path>` and emits `npcLocStrings: upsert` rows plus `delete` rows for stale
keys in the covered zones; it writes no datasheet at all. Derivation from spawn geometry stays in
the tool because that is a genuine batch operation; authoring goes through the DSL. This is what
makes the registry survive a revert-and-replay, which is the failure that started all of this.

**Author Loc waypoints in the TYPED form**, `continent` plus `markers` (bare `[x, y, z]` flow
sequences, the same shape `fences` uses), not the packed `string`. Both are supported and the DSL
docs call raw "what a generator emits", but a packed payload runs to thousands of characters, so a
spawn change lands as one enormous changed line and a reviewer cannot see which waypoint moved.
Typed markers diff one waypoint at a time. Adopting it on `gen_npcloc.py` was verified to be a
pure no-op: the applied `StrSheet_NpcLoc.xml` came out byte-for-byte identical to the raw-string
result, same SHA256. Semantics worth knowing: `markers` replaces the whole list and is
sequence-exact (275 shipped rows repeat a waypoint, one of them 32 times), `addMarkers` appends
and is idempotent, `removeMarkers` removes EVERY occurrence, removals apply before additions, and
`continent` is required alongside any of them. Mixing `string` with the typed keys is E554, not a
precedence rule. There is deliberately no index-addressed form, because these rows are regenerated
from spawn geometry and any written-down position would go stale.

**Do not forget `ENTITY_SYNC_MAP`.** A new entity key that is not mapped in
`tools/migrate/migrate.py` syncs to nothing, silently. All three of `creatureStrings`,
`npcLocStrings` and `collectionLocStrings` had to be added there as well as to `sync-config.yaml`.

## Standing constraints

- No git branches, no co-authored commits, single-line commit subjects, no conventional-commit
  prefixes. No em/en dashes in any authored file (machine hook enforces).
- Public repo: no hostnames/paths/credentials in tracked docs; environment goes in `.references`.
- DSL/MCP bugs: file requests in `docs/dsl-requests/` / `docs/mcp-requests/`, never fix locally;
  interim hand edits must be documented in the spec header that owns the change.
