---
name: apply-spec
description: >
  Validate, apply and sync a DSL spec against the server datasheets, then prove the result.
  Resolves paths from .references, runs validate-before-apply, reconciles reported op counts
  against intended ops, and covers the regression-diff discipline: snapshotting the dirty set
  to catch unintended footprint, node-level diffs against committed HEAD, value compares
  against an oracle, and probing unproven or destructive DSL semantics on a scratch datasheet.
  Use when validating or applying a spec, when syncing or packing the client, when checking
  whether an apply changed exactly what it should and nothing else, when an apply seems to
  have done nothing, or when a verification gate fails and it is unclear whether the gate or
  the change is wrong.
disable-model-invocation: false
user-invocable: true
argument-hint: [spec-path]
---

# Apply a DSL Spec

Follow these steps when validating or applying a spec. Do not skip validation.

**CRITICAL: never raw-apply a single patch spec.** When a `--source-ref` is
configured (this project pins it to the server repo baseline HEAD), `dsl apply`
REPLAYS the target files from that ref and applies only the specs given on the
command line. A single-spec apply therefore RESETS every file it touches to
baseline and silently wipes the changes every sibling spec made to those files
(2026-07-19 incident: applying `03-iod-spawn-removals.yaml` alone reset
`TerritoryData_13.xml` to HEAD and erased spec 02's 451 restored spawn ops; the
regressed file was deployed three times before detection). For any spec that
lives under `specs/patches/<patch>/`, apply THE WHOLE PATCH with the migrate
tool: `python reforged/tools/migrate/migrate.py --patch <patch> [--skip-sync]`.
Raw single-spec `dsl apply` is safe only for a spec whose target files no other
spec touches, or against a scratch path with no shared-file siblings.

## 1. Resolve paths

Read `.references` in the project root (`reforged/.references`). Parse as `key=value` lines. You need:

| Key | Purpose |
|-----|---------|
| `project_root` | Where `dsl.exe` lives |
| `server_datasheet` | Target datasheet XML directory |

The DSL binary is at `<project_root>/dsl.exe`. Always use the full absolute path — never `./dsl` or relative paths.

## 2. Determine the spec path

If the user provides a spec path, use it directly. If they mention a spec by name or number, find it under `specs/`. Spec files live in:

```
specs/patches/<patch>/          — patch-specific specs (numbered for execution order)
specs/patches/<patch>/loot/     — loot table specs (zone files)
specs/patches/<patch>/evolutions/ — evolution path specs
specs/backlog/                  — pending/future specs
```

## 3. Validate first

Always validate before applying:

```bash
"<project_root>/dsl.exe" validate <spec-path> --path "<server_datasheet>"
```

Run this from the `reforged/` directory. Check for:
- **Valid**: proceed to apply
- **Errors (E###)**: fix before applying, do not apply broken specs

## 4. Apply

Only after validation passes:

```bash
"<project_root>/dsl.exe" apply <spec-path> --path "<server_datasheet>"
```

Report the number of operations applied. Reconcile that count against the ops you intended:
`validate` reports success on operations that decompose to zero commands, so a matching count
is the only cheap proof the edit actually landed.

### Prove the change is exactly what you intended, and nothing else

An apply writes files its ops target. It does NOT reconcile the tree to what the specs
currently say, so the risk is always in two directions: the change you meant may be smaller
than you think, and the footprint may be larger. Four techniques, cheapest first. The zone-port
pipeline layers a per-family reconciliation gate on top of these; see
`docs/plans/classic-restoration/ZONE-PORT-PLAYBOOK.md` phase 5.

1. **Snapshot the dirty set, then diff it.** Before applying, `git status --porcelain > before.txt`
   in the datasheet repo; after, capture `after.txt` and `diff` them. This is the only check that
   shows files ENTERING the dirty set, which is where unintended footprint hides: a 4-op spec once
   pulled 409 client shards into the patch because it was the first spec to touch that entity
   family and triggered a full sync of it. Per-file diffs cannot catch this, because you have no
   reason to look at files you did not touch.
2. **Node-level diff against committed HEAD.** `git diff -U0 -- <file>` on each file the spec
   targets, and account for EVERY changed line. Unexplained lines are the finding. Expect one
   legitimate extra: DSL adds an XML declaration the first time it writes a file that lacked one,
   while preserving the BOM the loader requires.
3. **Value-level compare against an external oracle** when one exists (the v31 tree, a spec's own
   stated targets, a pre-change copy). Key-level coverage is not enough: it once missed a
   compensation class-row collapse that a value compare caught.
4. **Probe unproven semantics on a scratch datasheet, never on the real tree.** Copy the target
   file into a scratch directory, apply a throwaway probe spec against that path, and diff. Use
   this whenever a doc leaves a destructive question open. It confirmed that `dungeonDatas.upsert`
   naming only one nested collection preserves its siblings (41 EventTasks of scripting) and every
   root attribute, which the docs' "nested collections are fully replaced" wording did not settle.

**When a gate fails, first ask whether the gate or the change is wrong.** A verification that
asserts something never true of the working precedent produces a false alarm: a post-apply check
once failed on a client shard that is server-only by design, and the correct fix was to the gate.

### Verifying the result with the MCP

The MCP reads the same working tree you just wrote, so it is the fastest post-apply check, with
two caveats worth one call each. See `domain-research` for the full tool catalog.

- **Confirm you are reading post-apply state.** `datasheet_freshness` reports per family whether
  the held index matches the files on disk. Indexes rebuild on file change, so this is normally
  a formality, but it is the one call that distinguishes "the spec did nothing" from "I am
  looking at pre-apply data". If a documented tool or entity seems missing entirely, suspect a
  stale `.mcp/` binary instead (lesson in `domain-research`).
- **Gate zones whose quests changed.** `audit_quest_gates --huntingZoneId <hz>` names any quest
  whose contact NPCs or kill/collect targets nothing spawns. Those quests are authored correctly
  and silently uncompletable, which no validate or apply step can catch.

## 5. Sync to client (if requested)

If the user asks to sync or deploy, run the entity sync:

```bash
"<project_root>/dsl.exe" sync --config "reforged/config/sync-config.yaml" -e <Entity1> -e <Entity2>
```

Common entity names: `ItemData`, `EquipmentData`, `EnchantData`, `MaterialEnchantData`, `PassivityData`, `QuestData`.

Choose entities based on what the spec modifies. If unsure, ask the user which entities to sync.

## 6. Pack client (if requested)

Client packing requires PowerShell. Resolve `client_pack_dir` from `.references`:

```bash
powershell -Command "Set-Location '<client_pack_dir>'; & '.\novadrop-dc_92.04\novadrop-dc' pack --encryption-key 7533835567F31B7C8BF9321CF7C67A07 --encryption-iv 1A2DE14F51A8AD426FEAEB4AC3CB705C DataCenter_Final_EUR DataCenter_Final_EUR.dat"
```

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| E535 | Exported variable not found | Package sub-file missing `exports: variables:` or index.yml missing `use: variables:` |
| E536 | Imported variable not exported by source | Variable name not in source package's exports list |
| E520 | Unknown variable reference | `$VAR_NAME` used but not imported — add to `use: variables:` in imports |
| E103 | Invalid property | Check the DSL schema docs for the entity type (see note below) |
| E200 | Missing required field | Check required attributes in the entity schema (see note below) |

**Schema docs location:** resolve `dsl_docs_enduser` from `.references`, then read `schemas/<category>/<entity>.mdx` for the entity type.

## Lessons

### The `.references` datasheet paths are not the git repo roots, so a pathspec'd git command silently returns empty
- **Date/source:** 2026-07-25: `git diff --stat -- Datasheet/TerritoryData_13.xml`, run from `<server_datasheet>` immediately after an apply that reported 4 ops against that file, printed NOTHING. The same happened on the client repo. Four calls lost, and worse, the empty output first read as "the apply changed nothing".
- **Why:** `server_datasheet` resolves to the `Datasheet` subfolder while the repo root is its PARENT; `client_datacenter` resolves to `DataCenter_Final_EUR` while the root is one level up. `git status` prints paths relative to the repo ROOT, so copying a path out of `git status` output and passing it straight back as a pathspec from inside the subfolder resolves to `Datasheet/Datasheet/...` and matches nothing. Git raises no error for a `diff` pathspec that matches nothing, so the failure is silent and reads as a clean file.
- **Apply:** run `git rev-parse --show-toplevel` once per repo before any pathspec'd git command, and give pathspecs relative to that root (or run from the root). Treat an empty `git diff` after an apply that reported ops as a pathspec bug until proven otherwise: re-check with a bare `git status --porcelain` (no pathspec) before concluding the apply was a no-op. Snapshot `git status --porcelain` before an apply and diff it after, so files ENTERING the dirty set are visible even when a pathspec is wrong.

### `git checkout` does not un-deploy: deploy_dev mirrors only git-dirty files, so push reverted files explicitly
- **Date/source:** 2026-07-24: while bisecting a world-server load crash, `git checkout -- Datasheet/QuestData/001303.quest` followed by `deploy_dev.py --verify` reported "59 copied, Verify OK" instead of the expected 60. The reverted file was never pushed, so the dev box still ran the modified copy and the isolation boot would have tested nothing.
- **Why:** `deploy_dev.py` computes its delta from `git status` in the datasheet repo. A reverted file is no longer dirty, so it drops out of the delta entirely; the tool has no notion of "the remote has something the local no longer does". The overlay on the dev box is working-tree state, not a mirror.
- **Apply:** when a test depends on a file being reverted, push it explicitly (`scp` to `<dev_server_datasheet>`) and verify remotely (hash it, or parse the value you reverted) before asking for the restart. Treat the deploy summary's file COUNT as a checksum: if it does not match the number of files you expect to have changed, find out why before restarting. Same trap applies to any revert-and-retest cycle, and it compounds with the fact that restarts are the user's manual step.

### New quests (any new IdSorted client entity) need a full quest sync, not migrate's narrowed default
- **Date/source:** 2026-07-21: `migrate --patch 001` on the IoD Berlon chain (6 new quests 1353-1358) failed the client sync with `[E680] Position conflict ... expected quest 1358 but found quest 1376` on `Quest-0037x`, plus `[W600] 36 StrSheet_Quest records owned by no shard appended to fallback primary 00000`.
- **Why:** `Quest`/`QuestDialog` use the `IdSorted` client strategy (shard N = the Nth server file by sorted id). Inserting a new low-id quest shifts every later quest's shard position, which the manifest-narrowed sync cannot do: it rewrites only the changed files, so it writes the new quest onto a shard that still holds another quest. New `StrSheet_Quest` strings have no owning shard and land in the fallback primary shard (harmless).
- **Apply:** for a patch that ADDS quests, run a full sync, not the narrowed default: `dsl sync --config reforged/config/sync-config.yaml -e Quest -e QuestDialog -e StrSheet_Quest -e StrSheet_Item` (or `migrate --patch NNN --no-narrow`). It renumbers all downstream shards (content-safe, thousands of files). VERIFY nothing was lost: parse the server `.quest` id set and the client `Quest-*` id set and assert they are equal with zero duplicates before deploying. Once the new quests are in the committed baseline, later modify-only replays sync fine narrowed.

### A family mapped to `None` in ENTITY_SYNC_MAP is an assertion, not a fact: verify it against the client DC folder listing
- **Date/source:** 2026-07-26: a live report that accepted quests showed gold and XP but no item reward in the QUEST LOG, while the NPC accept dialog showed the full reward and completion paid the item correctly. `questCompensations` had been mapped to `None, # QuestCompensationData: server-only` since the map was written, inherited from the domain KB's blanket claim that all compensation families are server-only. The client ships 153 `QuestCompensationData` shards and the quest log reads them, so 64 reward rows across 15 IoD quests, 7 whole quests, and 2 stale gold/exp pairs had never reached the client.
- **Why:** "server-only" is true for CCompensation / ECompensation / FCompensation / ICompensation, which have no client folder at all, and the KB generalized it to the fifth type. Nothing in the pipeline contradicts a wrong `None`: the apply succeeds, the sync reports no entity, every server-side gate and MCP query passes (both MCP servers read SERVER datasheets, so a server-to-client divergence is invisible to them by construction), and the game mostly works because the server stays authoritative for behavior. Only a client-RENDERED value exposes it.
- **Apply:** before trusting any `None` in `ENTITY_SYNC_MAP`, `ls` the client DataCenter root for a folder of that family's name. It takes one command and is the whole proof. Then decide from the client XSD, not from intuition, whether the family is renderable. Diagnostic signature to recognize in a bug report: **a value the client DISPLAYS disagrees with the server while the server's own behavior is correct** (reward shown vs reward paid, tooltip vs effect, marker vs spawn). That shape means a client copy exists and is stale, not that the server data is wrong. Two windows can also read two different sources for the same fact: here the accept dialog is server-fed (`S_DIALOG.questRewards`) while the log is client-fed (`S_QUEST_INFO` carries no reward fields at all), so "one screen is right and the other is wrong" is itself the tell. When wiring the newly discovered entity, prefer explicit `source_mapping` pairs over any positionally derived strategy, and scope the mapping to the zones the project actually owns so the fix does not become a game-wide rewrite.

### Semantic-diff a NEW sync entity's output against client HEAD before accepting it
- **Date/source:** 2026-07-19: `dsl sync -e NewWorldMapData` (entity newly added to sync-config for the Tower Base minimap fix); a Python semantic diff of the projection vs the client-dc git HEAD showed 37 curated client-only markers deleted game-wide (guild boards, dungeon entrances, brokers), on top of the intended addition.
- **Why:** monolithic sync is a full-file replace of the client file with the XSD-filtered server projection. "Server is source of truth" does not hold at file granularity for families where the publisher curated the client copy (extra markers, patched attributes); the sync silently deletes that curation. A single XSD-invalid server row also aborts the whole entity sync with E650 (server section 9034 lacked height/left/top; fixed by a spec backfill op using the client's own values).
- **Apply:** when adding a sync-config entity for a family never synced before, run the sync, then diff the written client file against git HEAD semantically (parse both, compare by id hierarchy), not just by eyeballing the textual diff. If client-only content would be deleted, set `merge: merge-by-id` (Monolithic strategy only) with `merge_key_attributes` on the entity: it preserves client-only siblings while server records win on match (delivered 2026-07-19; see tools/client-sync.mdx "Merge modes" in the end-user docs; NewWorldMapData is the live example in sync-config). Even with merge-by-id, review the "changed" entries of the semantic diff: server-wins overwrites can surface bad hand-edited server rows (e.g. section 9053 pointed at a MapDefine absent from the client; fixed by realigning the SERVER row to the client-proven values via a spec op, precedent in spec 13).
