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

- Parse RAW XML with python. MCP servers may be stale right after a revert: verify freshness
  against a known marker before trusting, and trust raw files on any disagreement.
- Expect the baseline to be closer to v31 than assumed: IoD TerritoryData was 100% identical
  (whole family became a no-op) and the quest spine matched fully except rewards. Diff first,
  never assume work exists.
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

| Family | Server | Client | Sync |
|--------|--------|--------|------|
| Quest bodies | `QuestData/00NNNN.quest` (sentinel disable = prereq `99,99`; reward flag on final task) | per-quest shards | Quest entity |
| Quest strings | monolithic `StrSheet_Quest.xml` (rows NNNN001+) | 2879 opaque shards | shard-routed |
| Quest dialogs | `QuestDialog/QuestDialog_<gid>.xml` (one PER QUEST) | shards | QuestDialog entity |
| Rewards | `CompensationData/QuestCompensationData_<hz>.xml` | none | server-only |
| Spawns | `TerritoryData_<hz>.xml` (groups > territories > Npc/Party; pos 0,0,0 = random-in-fence) | none | TerritoryData |
| Villager menus | `VillagerData/VillagerMenu.xml` (`hz,tpl` -> Menu entries) | synced | VillagerMenu |
| Ambient NPC lines | `VillagerDialog/VillagerDialog_<hz>.xml` | per-villager shards | NONE (hand edits; DSL entity broken, request filed) |
| Speech selectors | `VillagerData/<hz><id>.condition` | n/a | speechConditions (server-only) |
| Sections | `AreaData/AreaData_*` (commented-out blocks are re-enable candidates) | synced | AreaData |
| Worldmap | `WorldMap/NewWorldMapData.xml` | monolithic client file | merge-by-id; NO section-level delete (request filed) |
| Quest-link registry | none | `StrSheet_NpcLoc` | tool-managed: `gen_npcloc.py --prune` |
| Minimap labels | none | `MapDefineData/*` | none; hand edits with dangling proof |
| Shops | `BuyMenuList.xml` + `BuyList.xml` (shared tabs game-wide) | MenuList | buyMenuLists synced; buyLists server-only |

## Standing constraints

- No git branches, no co-authored commits, single-line commit subjects, no conventional-commit
  prefixes. No em/en dashes in any authored file (machine hook enforces).
- Public repo: no hostnames/paths/credentials in tracked docs; environment goes in `.references`.
- DSL/MCP bugs: file requests in `docs/dsl-requests/` / `docs/mcp-requests/`, never fix locally;
  interim hand edits must be documented in the spec header that owns the change.
