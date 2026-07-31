# dc-restore Toolkit

A persistent Python toolkit for restoring old TERA content (NPC spawns, quests, rewards, dialogs) into the current v92 server datasheet. This is the archaeology and diff layer: it compares three content sources and reports what is missing, what is easy to restore, and what is a deliberate patch overlay rather than loss.

## Overview

Restoration draws on three sources, each resolved from `reforged/.references`:

| Role | `.references` key | What it is |
|------|-------------------|------------|
| Hard-restore source | `old_client_dc` | 2011-era unpacked client DataCenter, Novadrop layout (folder per family, sharded `Family-NNNNN.xml`). Visual-oriented schema; used when nothing else has the content. |
| Easy-restore source | `v31_datasheet` | v31.04 server datasheet, flat per-zone files (`NpcData_13.xml`). Same server schema as v92, so restores are near copy-paste. Lives on a network drive (`Z:`). |
| Current truth | `server_datasheet` | v92 server datasheet, the restoration target and validation baseline. |

> **Standing rule (2026-07-28): no tool in this directory writes a datasheet, and none writes the
> client DataCenter at all.** Generators derive content and emit a DSL **spec**; `migrate` applies
> it and the normal server-to-client sync propagates it. A tool that writes the client directly
> puts its output in the one tree that is not reproducible from specs, so a patch revert-and-replay
> silently discards it: that is exactly how the `StrSheet_NpcLoc` registry was lost, with the
> migrate run reporting 0 failed and 0 warnings while it happened. `gen_npcloc.py` and
> `gen_collectionloc.py` were retargeted for this reason. Restore modules (`quest_restore.py`,
> `comp_restore.py`, `spawn_restore.py`) emit reviewable plans, not edits. If a new family needs a
> client leg, register it in `config/sync-config.yaml`, map its key in migrate's `ENTITY_SYNC_MAP`,
> and if it is client-only bring it over with `dsl import` first. See `ZONE-PORT-PLAYBOOK.md`,
> "Client-only families".

The modules are **survey.py** (per-zone gap report), **quest_restore.py** (restore quest header wiring from the client reference), **comp_restore.py** (restore quest compensation blocks from v31), **spawn_restore.py** (reconstruct deleted TerritoryData spawns from the client shard), **dcq.py** (cross-source content query CLI), **audit_quests.py** (deterministic quest-difference flagger), **dungeon_audit.py** (dungeon reference integrity gate), **audit_class_gates.py** (class-gate coverage gate), and **audit_quest_design.py** (quest design review, advisory). `dclib.py` is the shared library every module builds on, and `auditlib.py` carries the shared model for the design review.

### Read-only vs restore modules

`survey.py`, `dcq.py`, `audit_quests.py`, `dungeon_audit.py`, `audit_class_gates.py`, and `audit_quest_design.py` are **read-only analysis** tools: they never write to a datasheet. `quest_restore.py` and `comp_restore.py` are **restore** tools (dry-run by default, `--apply` writes). The analysis tools that judge current v92 state differ in which lane they read: `survey.py` diffs the clean git HEAD baseline (patch overlays are annotated, not counted as loss), while `dcq.py` and `audit_quests.py` read the **working tree** (so authored spawns and restored comp/prereq show up as the current truth), noting dirty files for context.

### Dry-run by default

Every restore module is dry-run by default: it prints a unified diff of exactly what it would change and writes nothing. Pass `--apply` to write. On `--apply`, each edited file is re-validated with `ET.fromstring` before it is written; a parse failure aborts the write.

### Baseline lane

Files produced by the restore modules are **canonical content baseline**, not patch tuning. They are committed on the baseline lane, separate from DSL patch overlays: a restore fills back content that was lost or disabled, whereas a patch spec deliberately tunes live content. Keep the two in separate commits so the survey's HEAD-baseline logic (see below) keeps reading restores as intact content and overlays as deliberate tuning.

## Quick Start

```bash
# Survey the Island of Dawn zone set, write markdown + JSON
python reforged/tools/dc-restore/survey.py \
  --zones 13,64,213,313,364,436 \
  --out reforged/docs/plans/iod-alpha-content-loop/iteration-0-gap-report.md \
  --json reforged/docs/plans/iod-alpha-content-loop/iteration-0-gap-report.json
```

## survey.py Parameters

| Flag | Required | Description |
|------|----------|-------------|
| `--zones` | Yes | Comma-separated hunting zone ids (e.g. `13,64,213`) |
| `--out` | Yes | Output markdown report path (parent dirs created) |
| `--json` | No | Optional machine-readable JSON dump of every zone's raw findings |

The survey is read-only: it writes only `--out` and `--json` and never touches any datasheet, `.references`, or config file.

## What the survey compares (per zone)

Every comparison is v31 vs the **v92 git HEAD baseline** (see below), with the old client as an existence signal or hard-restore source.

1. **NPC templates** - `Template id`+`name` sets from `NpcData_<zone>.xml`; reports ids missing from v92 and counts the client shard templates.
2. **NPC skills** - `Skill templateId` set diff from `NpcSkillData_<zone>.xml` (root tag is `<SkillData>` despite the filename).
3. **AI** - `Ai id` set diff from `AIData_<zone>.xml`.
4. **Territory / spawns** - `TerritoryGroup id`+`desc` diff from `TerritoryData_<zone>.xml`, plus per-group spawn-entry (`<Npc>`) count shrink for groups present in both.
5. **Quests** - zone quest-id set from the authoritative `Quest번호` hz header (not the filename band), classified `in-v92` / `v31-only` (easy) / `client-only` (hard). QuestGroupList registration counts are reported as a secondary signal.
6. **Quest compensations** - per `questId` filled vs empty-stub (`<Quest questId=".."/>`) in v31 vs v92 HEAD; a filled v31 reward that is a stub or absent in v92 is a restorable loss.
7. **Loot compensations** - `npcTemplateId` presence in `C`/`E` Compensation files, v31 vs v92 HEAD, plus a working-tree-vs-HEAD overlay annotation and a "gap after overlay" line when the working tree already restores entries.
8. **Dialogs** - QuestDialog coverage (client shards by `huntingZoneId`, v31 files by `questId` prefix, v92 files in the `zone*100 .. zone*100+99` band) and a VillagerDialog signal.
9. **Commented-out markup** - comment blocks containing `<` markup in the zone's server files (v31 and v92 HEAD).

The report ends with a per-zone summary table and a restoration worklist split into easy path (v31 source), hard path (client-only), and overlay (patch tuning, out of restoration scope).

## quest_restore.py

Restores quest header wiring that was soft-disabled in v92, using the old client Quest shard as the source of truth. Format-preserving surgery only: the `.quest` file is edited by regex slice, never round-tripped through ElementTree, so tasks, dialogs, and body stay byte-identical.

```bash
# Restore prerequisites for three quests (dry-run diff)
python reforged/tools/dc-restore/quest_restore.py --quests 1334,1336,1341

# Restore quest 1343 (prereq + story group + QuestGroupList) and relink 1316's prereq
python reforged/tools/dc-restore/quest_restore.py --quests 1343 --relink 1316=13,43

# Write the changes
python reforged/tools/dc-restore/quest_restore.py --quests 1334,1336,1341 --apply
```

| Flag | Required | Description |
|------|----------|-------------|
| `--quests` | one of these | Comma-separated global quest ids to restore from the client reference |
| `--relink` | one of these | `A=x,y` : set quest A's existing single prerequisite to `x,y` (repeatable). Refuses to act unless A currently has exactly one prerequisite |
| `--apply` | No | Write changes (default: dry-run diff) |

Per requested quest it touches only two fields, both taken from the client shard:

1. **Prerequisite.** If the client quest has no prerequisite, the v92 `99,99` sentinel block is dropped to the canonical no-prereq form. If the client has a prerequisite, the sentinel value is replaced with it. A v92 prerequisite that is not the `99,99` sentinel is never overwritten (reported as a divergence; use `--relink` to change it deliberately).
2. **Story group.** If the client records a story-group id and v92 has an empty `<스토리그룹Id />`, the value is restored and the quest is registered in `QuestGroupList.xml` under that `StoryGroup`, inserted after the same predecessor quest it follows in the client group (appended at the end of the group if that predecessor is absent). An already-present registration is skipped with a note.

A quest with no sentinel and no story-group gap is reported as "nothing to do" (not an error).

### The 99,99 soft-disable sentinel and the canonical no-prereq form

The four Island quests (1334, 1336, 1341, 1343) were disabled in v92 by writing a sentinel prerequisite into the header:

```xml
<선행퀘스트>
  <선행퀘스트>
    <퀘스트Id>99,99</퀘스트Id>
  </선행퀘스트>
</선행퀘스트>
```

Quest `99,99` does not exist, so the requirement can never be met and the quest never offers. The canonical "no prerequisite" form is **the entire `<선행퀘스트>` block absent** (not an empty element): active no-prereq quests such as `001301.quest` carry only `<최소레벨>`, `<영주길드 />`, `<길드레벨 />` under `<수행조건>` and no `<선행퀘스트>` at all. quest_restore mirrors that exactly by removing the sentinel block, including its leading newline, so no blank line is left behind. (Note: `001318.quest` is itself still sentinel-disabled, so it is not a valid no-prereq template despite having no real prerequisite.)

## comp_restore.py

Restores quest reward payloads from v31 into the v92 `QuestCompensationData_<zone>.xml`, which carries empty self-closing quest stubs (`<Quest questId="1334"/>`) where the reward was stripped.

```bash
# Restore four specific quests (dry-run diff)
python reforged/tools/dc-restore/comp_restore.py --zone 13 --quests 1334,1336,1341,1343

# Restore every empty stub that has a filled v31 source
python reforged/tools/dc-restore/comp_restore.py --zone 13 --all-empty

# Write the changes
python reforged/tools/dc-restore/comp_restore.py --zone 13 --all-empty --apply
```

| Flag | Required | Description |
|------|----------|-------------|
| `--zone` | Yes | Hunting zone id (selects `QuestCompensationData_<zone>.xml`) |
| `--quests` | one of these | Comma-separated questIds to restore |
| `--all-empty` | one of these | Restore every empty v92 stub that has a filled v31 source |
| `--apply` | No | Write changes (default: dry-run diff) |

Each v31 filled block (its `exp`/`gold`, plus any `itemBag` and per-class `<Item>` children) is spliced in place of the v92 stub, re-indented to the v92 file's indentation. Only an empty stub (self-closing or childless) is ever replaced; a non-empty v92 entry is never overwritten (skipped with a warning). A quest whose v31 entry is missing or itself empty has no source and is left as a stub. The report lists restored / skipped-non-empty / no-v31-source / (requested-but-absent) counts.

For zone 13 the full `--all-empty` scope is 75 restorable of 77 stubs; the two with no source (`1342`, `1388`) are empty in v31 as well.

## spawn_restore.py

Reconstructs deleted `TerritoryData` spawns from the old client shard. Island spawn losses predate v31 (v31 and v92 hold the same reduced set), so the client DataCenter shard is the only surviving record of the full spawn topology. The module diffs the client shard against the v92 server file and produces a reviewable reconstruction plan (markdown + JSON); it never edits a datasheet on a dry run.

```bash
# Build the full zone 13 + 213 reconstruction plan (dry-run; writes plan files only)
python reforged/tools/dc-restore/spawn_restore.py --zones 13,213
```

| Flag | Required | Description |
|------|----------|-------------|
| `--zones` | No | Comma-separated zones (default `13,213`) |
| `--plan-out` | No | Plan markdown path (default `docs/plans/iod-alpha-content-loop/batch-3-spawn-plan.md`) |
| `--json` | No | Plan JSON path (defaults beside `--plan-out`) |
| `--audit` | No | Audit JSON joined for the flag-closure section |
| `--apply` | No | Write server files (default: dry-run plan only) |

Two spawn losses are handled with two idioms, both verified against the v92 files:

- **Zone 13 group deletion.** 17 whole `TerritoryGroup`s (ruins / late-forest mob camps that feed the kill-quests) exist only in the client. Each is rebuilt group + territories (client fence polygons copied verbatim) + area-mob `<Npc>` entries (`randomPos="true"`, `pos="0,0,0"`, sized `spawnCount`). `npcTemplateId` is resolved from the Korean group desc via a curated authoritative table (parent `페어런츠용` stubs and `환경` ambient templates excluded unless the desc says `환경`), cross-checked against the ruins-archaeology kill-target roster; each group carries a confidence tag. Combat attrs are cloned from a real same-zone v92 donor spawn (self-template preferred, else same-family, else a flagged generic).
- **Zone 213 territory deletion.** No client-only groups; deleted southern villager territories hide inside the shared group 21300003, found by fence-polygon similarity (mean nearest-vertex distance). The recovered polygon beside the ruins is authored as Leander's Outpost; the unspawned quest villagers are placed at their authentic camps with the fixed idiom (`randomPos="false"`, explicit pos + dir), and Eria (1021) is relocated from the vanguard camp by a `pos` replacement on her instance.

Spawn counts are sized from the donor density (one Npc per client polygon), raised toward 1.5x an explicit client kill count where one exists (capped at 12/territory, shortfalls flagged). The plan closes with an audit join: which `GIVER_UNSPAWNED` / `TARGET_UNSPAWNED` flags clear (via villager placements) versus remain (cinematic/event NPCs deliberately not placed, and out-of-scope zones), plus the kill-target availability the zone-13 groups restore (a ruins-archaeology gap the audit does not itself spawn-check). The full proposed XML is emitted in a fenced appendix; `--apply` inserts it and re-validates every edited file before writing.

## dcq.py (cross-source query)

Focused lookups across the three sources, side by side. Read-only; parses on demand (no cache layer). v92 is read from the working tree.

```bash
python reforged/tools/dc-restore/dcq.py quest 1322      # header/tasks/comp/dialog, 3-source, DIFFs marked
python reforged/tools/dc-restore/dcq.py npc 213 1003    # name + spawns + quest references for NPC (hz,tid)
python reforged/tools/dc-restore/dcq.py name Kishale    # creature name/title substring search
python reforged/tools/dc-restore/dcq.py collection 410  # collection attrs + island spawns + quest references
```

| Subcommand | Shows |
|------------|-------|
| `quest <gid>` | Header wiring (type, repeat, story group, prereq, giver, min/max level), per-task gameplay fields, compensation summary per source, English title, and dialog-file presence, as CLIENT / V31 / V92 columns with differing values marked `<<< DIFF`. |
| `npc <hz> <tid>` | Template name in v31/v92 `NpcData_<hz>` and the client `StrSheet_Creature`; spawn entries in `TerritoryData_<hz>` (the ref's own zone) for both servers; and island-band quests that reference the NPC as giver or task target. Note: `npcTemplateId` is unique only within a hunting zone, so the same local id in another island zone is reported as a distinct NPC, never conflated. |
| `name <substring>` | Case-insensitive search of client creature names and titles; each hit prints name, templateId, hz, and whether v92/v31 `NpcData_<hz>` define that template. |
| `collection <cid>` | `Collections.xml` attributes, island `CollectionTerritory` spawn counts (via `<Collections typeId=cid>` groups), and island-band quests whose tasks reference the collection. |

## audit_quests.py (deterministic quest-difference flagger)

Compares every Island quest (global-id band 1300-1399, unioned across sources) CLIENT vs V31 vs V92 and emits deterministic flags. Read-only; writes only the report and JSON. V92 is the working tree.

```bash
python reforged/tools/dc-restore/audit_quests.py \
  --zones 13,64,213,313,364,436 \
  --out reforged/docs/plans/iod-alpha-content-loop/iteration-2-quest-audit.md \
  --json reforged/docs/plans/iod-alpha-content-loop/iteration-2-quest-audit.json
```

| Flag | Meaning |
|------|---------|
| `SENTINEL_DISABLED` | v92 prereq is the single `99,99` disable sentinel. |
| `PREREQ_DRIFT` | prereq differs client vs v92 (non-sentinel); v31's value is recorded so a v92 regression is distinguishable from a genuine conflict. |
| `TYPE_DRIFT` / `REPEAT_DRIFT` / `STORYGROUP_DRIFT` / `LEVELBAND_DRIFT` | header field differs client vs v92 (informational). |
| `TASKREF_DRIFT` | a gameplay task field differs client vs v92, compared structurally per task id. Each entry is classed `ref` (reference-identity: collection/item/NPC id) or `count` (kill count, quantity), and carries v31's value plus whether v31 agrees with the client. |
| `COMP_EMPTY` | v92 compensation is a stub/absent while the client or v31 has a reward. |
| `COMP_DRIFT` | the client-era and v31 rewards disagree (exp/gold/itemBag/items); no winner is picked. |
| `GIVER_UNSPAWNED` / `TARGET_UNSPAWNED` | a giver (`발생조건`) or task target (`대상NPC지정` / visit `NPCId`) has no `TerritoryData_<hz>` spawn in v92; v31 spawn state is noted. |
| `GROUPLIST_UNREGISTERED` | the quest has a story group but no `StoryGroup` entry in v92 `QuestGroupList`. |
| `DIALOG_MISSING` / `STRINGS_MISSING` | v92 lacks the `QuestDialog` file / `StrSheet_Quest` title string the client has. |
| `CLEAN` | none of the above. |

Severity ranks blocking (sentinel, reference-identity taskref, unspawned NPC, empty comp on an active quest) above drift (prereq, comp drift, grouplist/dialog/strings) above info (level band, type, story-group, count-only taskref).

The report opens with a **reference-identity regressions** table (the highest-signal mechanical fixes: a task reference where the client and v31 agree and only v92 diverges, the `콜렉션Id`-style bug class). It then splits the actionable quests into a worklist:

- **Group A** mechanically fixable now (isolated sentinel re-enable, or a fix the v31 source resolves toward the client), giver spawned.
- **Group B** needs spawn authoring (giver or task target unspawned in v92).
- **Group C** chain-entangled: a disabled quest wired into the client-era prereq chain, so it re-enables as part of the story spine (predecessor/successor links are shown).
- **Group D** conflicts needing a human decision (comp restore with divergent sources, or prereq/taskref where v31 sides against the client).

`COMP_DRIFT` on a quest whose v92 comp is already filled, and header drifts (level/type/story group), are recorded as flags but do not by themselves put a quest in the worklist. The JSON mirrors every field, flag, signal, and the prereq chain graph for a future `--from-audit` consumer.

## dungeon_audit.py (dungeon reference integrity gate)

Validates that a dungeon continent's encounter wiring will actually work at runtime by resolving every DungeonData reference against the **parsed** content of the per-HZ files, never raw text. Read-only; reads the working tree; exit code 1 on any failure. Born from the dungeon 9037 incident (2026-07-21): all classic territory groups were wrapped in one XML comment, so grep and text diff reported the data as present while the server loaded nothing, and the failure was misdiagnosed as an engine-level topology limit.

```bash
# Gate a dungeon restore before deploying (run after apply, before deploy-dev)
python reforged/tools/dc-restore/dungeon_audit.py --dungeons 9037

# Audit several dungeons; point at another datasheet root (e.g. a snapshot or v31)
python reforged/tools/dc-restore/dungeon_audit.py --dungeons 9037,9039,9091 --datasheet <path>
```

Checks per dungeon continent:

1. Continent resolves to its HuntingZone(s) in `ContinentData.xml`; `DungeonConstraint` registration + `isActive` reported.
2. Every `territoryId` referenced by active DungeonData event tasks resolves to a territory the server will load. Failures are classed `COMMENT-DISABLED` (exists only inside a comment block; uncommenting restores it) or `MISSING`.
3. Every `"hz,id"` entity reference (`targetNpcId` / `npcId` / `uniqueId`) resolves. The id half is polymorphic by event type: NpcData `templateId`, TerritoryData `Npc instanceId`, or `territoryId`; a reference passes if any of the three resolves in parsed content.
4. Every `npcTemplateId` spawned by the active territories exists as a parsed NpcData template.
5. Per-HZ file-set presence (`NpcData`, `TerritoryData`, `AIData`, `NpcSkillData`) and a comment-disabled census per file (warning): commented groups/territories/templates counted, plus inert commented DungeonData refs noted.

Regression-verified: run with `--datasheet` against a pre-fix snapshot of the 9037 files, it reports exactly the 27 wave-spawn references as `COMMENT-DISABLED`.

## audit_class_gates.py (class-gate coverage gate)

Checks that every class on the **current** roster is offered some member of each class-gated quest group. Read-only; reads the working tree; exit code 1 if any offerable group excludes an audited class. Born from the 2026-07-25 incident: a Ninja completed 1384 and the story spine dead-ended, because 1382 admits Warrior/Lancer/Slayer/Berserker/Archer/Engineer and its sibling 1383 admits Sorcerer/Priest/Elementalist, so Milene offered neither and 1331 never unlocked.

```bash
# Gate any quest restore before deploying (run after apply, before deploy-dev)
python reforged/tools/dc-restore/audit_class_gates.py --zones 13,64,213,313,364

# Whole corpus, or a zone set with Reaper included
python reforged/tools/dc-restore/audit_class_gates.py --all-zones
python reforged/tools/dc-restore/audit_class_gates.py --zones 63 --classes Assassin,Fighter,Glaiver,Soulless
```


Why a source diff cannot replace this: classic content lists exactly the classes that existed when it shipped, and **v31 carries the identical lists**, so a faithful restore agrees with its source while still excluding every later class. The defect exists only relative to today's roster, produces no load warning and no crash, and hides from any live test that happens to use a classic class.

How it judges coverage:

1. Quests carrying `<수행조건><클래스>` are grouped by (zone, giver, story group), because the giver is the real grouping mechanism: one NPC hands each player the variant matching their class. Known groups this resolves correctly: 1351/1352 (Kiriya), 1382/1383 (Milene), 6302/6306 (63,1007), and the twelve per-class training quests 1371-1379 + 1380/1381/1387 (Dulari).
2. A group passes when the union of its members' gates covers the audited roster, so a caster-only quest is never flagged while its physical sibling covers the class.
3. Groups whose members are all sentinel-disabled (prereq `99,99`) are reported `DISABLED`, not failed: widening an unofferable quest is dead data. A single quest gated to exactly one class is reported `SINGLE` (per-class training quests are meant to be one per class).
4. A group whose members disagree on prerequisites is tagged `MIXED`, the one case where the giver key can over-merge unrelated chains and hide a gap. Per-member prerequisites are always printed.

Default roster is the full 13 classes minus `Soulless`: Reaper starts in a different zone at a higher level and never walks these chains (decision 2026-07-25). Override with `--classes`.

## audit_player_text.py (player-facing text gate)

Enforces `DOCTRINE.md` rule 10: player-facing text describes the world, never our build order. Read-only; scans **spec YAML**, not the datasheet; exit code 1 on any hit. Born from the 2026-07-31 incident: item 95217 "Valkyon Commendation" shipped the tooltip line *"The quartermaster who accepts them has not yet set up"*, and it passed `dsl validate`, `migrate` with 0 warnings, a clean client sync, all three standing gates, a client publish and a world-server boot. A human reading it in game was the only thing that caught it.

```bash
# Gate a patch before deploying (run alongside dungeon_audit and audit_class_gates)
python reforged/tools/dc-restore/audit_player_text.py --patch 002

# Everything, or one file
python reforged/tools/dc-restore/audit_player_text.py
python reforged/tools/dc-restore/audit_player_text.py --specs path/to/spec.yaml
```

Why specs and not the datasheet: authoring time is the cheap place to fail, and a datasheet scan cannot separate our text from the publisher's 112,000 shipped strings, several of which legitimately say "no longer usable" or name a discontinued event. This gate owns only what our specs write.

Comments are invisible to it by construction (the file is parsed as YAML), so spec headers may discuss wave order in as much detail as they like. What it scans is every string under a string-table entity (`itemStrings`, `questStrings`, `questDialogs`, ...) plus any `toolTip` anywhere. `name` is deliberately not scanned globally: under `items:` it is the internal datasheet name, not player-facing.

*No longer usable*, *formerly* and *obsolete* are deliberately **not** banned. They describe a stable state of the world, and the publisher's own retirement convention uses them (item 447, and the baseline strings for 94111/94112).

## audit_quest_design.py (quest design review, ADVISORY)

Deterministic checks over quest rewards, graph wiring and objective tuning. Read-only, **always exits 0**, and never prints the word PASS: a clean run means the deterministic checks found nothing, which is a much smaller claim than approval. Born from the 2026-07-27 Island of Dawn trimming and redistribution wave, which surfaced defects that are individually valid and wrong as a system: quests 1304 and 1323 granting the identical 12-row class weapon bag at the identical 800 exp and 80 gold (authentic v31 data, so no source diff could find it), no gear set below level 7 completable anywhere in the corpus, and quest 1348 asking for 8 items from a population expected to yield about 6.1.

```bash
# Review the quests a change touched (the usual form)
python reforged/tools/dc-restore/audit_quest_design.py --zones 13,64,213,313,364 --since HEAD

# Explicit findings scope, machine-readable output, current check inventory
python reforged/tools/dc-restore/audit_quest_design.py --zones 13 --quests 1323,1324
python reforged/tools/dc-restore/audit_quest_design.py --zones 13 --json
python reforged/tools/dc-restore/audit_quest_design.py --list-checks

# Descriptive tables (set placement, giver load, effort versus reward)
python reforged/tools/dc-restore/audit_quest_design.py --zones 13 --report
```

Three scopes, never conflated. `--zones` is the SUBJECT scope (which quests findings are reported about) and is required. Evidence is ALWAYS corpus-wide regardless of `--zones`: set completeness must see every granting quest in the game, and no trim can be proven safe against a zone-scoped view of inbound references. `--quests` or `--since` is the FINDINGS scope, marking which findings are NEW; without it every pre-existing condition in the zone is reported as though you had just introduced it.

Severity is CONFIDENCE that a finding is a defect, not importance. `high` means the signature marked a real defect every time it fired. Accepted findings go in `reforged/config/quest-design-waivers.yaml`, keyed by the stable finding key, and a waiver without a `reason` is ignored by the loader (a reasonless waiver is indistinguishable from nobody having looked).

Unlike every other module here, this one reads the **working tree** by default, because the subject of a design review is the content you just changed. `--baseline-ref <sha>` opts into a historical read; the regression fixtures use it to pin `789fec28`.

Run `--list-checks` for the current inventory rather than trusting any prose list, including this one. The registry is the single source of truth, and the `quest-design-review` skill defers to it for exactly that reason.

## Tests

The toolkit has a pytest suite under `tools/dc-restore/tests/` in two tiers: hermetic (synthetic fixtures, runs on any clone) and corpus (the real datasheet at the pinned commit `789fec28`, skipped with a stated reason when the private repo is absent). See `tests/README.md`.

```bash
python -m pip install -r reforged/requirements-dev.txt   # once
python -m pytest                                          # from reforged/
python -m pytest -m "not corpus"                          # hermetic tier only
```

## Notes and gotchas

### The v92 HEAD baseline (most important)

The v92 datasheet folder sits inside a git repo (`server_datasheet`'s parent) whose working tree currently holds uncommitted patch-001 changes. Those changes are a deliberate tuning overlay, **not lost content**. Every content comparison therefore diffs against the clean git HEAD, not the working tree: `V92Baseline` reads any file that is dirty per `git status --porcelain` from `git show HEAD:Datasheet/<relpath>`, and reads clean files straight from disk.

The canonical example is `CompensationData/CCompensation_0013.xml`: 238 KB and 50 npc loot tables at HEAD, but an 82-byte empty stub in the working tree because patch-001 spec 21 deliberately stripped it. The survey reports the HEAD content as intact and annotates the working-tree stub as a patch-001 overlay, so it never shows up as content loss.

Where a dirty overlay instead *adds* entries (e.g. `ECompensation_13.xml`: 10 npcs at HEAD, 47 in the working tree), the survey reports the baseline gap vs HEAD and a separate "gap after overlay" count so the worklist reflects the realistic remaining work.

### Format-preserving surgery (restore modules)

The restore modules must leave every byte they do not intend to change untouched. `dclib.TextFile` handles this: it reads raw bytes, records the UTF-8 BOM and the file's newline style (CRLF for `.quest` and `QuestGroupList.xml`, LF for `QuestCompensationData_*.xml`), normalizes the in-memory text to LF so regex never has to reason about `\r`, and restores the original newline and BOM on write. An unedited round-trip reproduces the source bytes exactly. When comp_restore splices a v31 block (CRLF) into a v92 file (LF), the block is carried in normalized LF form so the target file's newline style is preserved. All edited XML is validated with `dclib.validate_xml` (which encodes to bytes to avoid the ElementTree "encoding declaration in str" error) before any write.

### Korean tags in source

The quest header tags are Korean (`선행퀘스트`, `퀘스트Id`, `스토리그룹Id`). Passing Korean literals through a shell (inline `python -c`) mangles them; write a script file with the Write tool and force UTF-8 stdout (`PYTHONIOENCODING=utf-8`, or `sys.stdout.reconfigure`) instead. The modules embed the tag names verified against the actual files.

### Case trap

The zone-64 AI file is lowercase `AiData_64.xml` in both servers while every other zone uses `AIData_<zone>.xml`. All server-file matching is case-insensitive (`find_zone_file` / `find_file_ci`).

### Quest zone linkage

Quests are id-filed, not zone-filed. The authoritative zone for a quest is the first value of the `Quest번호` (hz,localId) header inside the `.quest` file (and the client `Quest` shard). The numeric filename band (`13xx` for zone 13) holds for the Island band but not for every zone, so the survey scans headers rather than trusting the band. QuestGroupList's `QuestHuntingZoneList` lists zones but not their quest membership; its `StoryGroupList` registers only story quests, so it is a partial signal, not the full zone quest set.

### Novadrop client layout

Client families are one folder per family with sequential shards `Family-NNNNN.xml` (the index is not the zone). Zone-scoped families carry `huntingZoneId` on the root element; `Quest` shards carry the id on the root and the zone in the `Quest번호` header. XML is namespaced (`https://vezel.dev/novadrop/dc/<Family>`); parsing is namespace-agnostic (`strip_ns`). Shard indexing reads only the first ~800 bytes of each file for speed.

### VillagerDialog

v31 has no VillagerDialog directory (absent by design). Client and v92 villager dialogs are keyed globally (`huntingZoneId="0"`), not per zone, so true per-zone attribution needs a join through the zone's villager NPCs. The survey reports a corpus-level signal now and defers per-zone attribution to the villager-restore module.

## Files

| File | Purpose |
|------|---------|
| `dclib.py` | Shared library: references + source resolution, namespace-agnostic XML helpers, case-insensitive server-file finder, Novadrop shard indexer (by zone and by root quest id), `V92Baseline` git-HEAD reader, `TextFile` format-preserving reader/writer, `validate_xml`, comment scanner, and the quest model / compensation / StrSheet / territory-spawn / collection / dialog parsers and the island quest-scope loader shared by `dcq.py` and `audit_quests.py`. |
| `survey.py` | Gap-report CLI. |
| `quest_restore.py` | Restore quest header wiring (prerequisite, story group, QuestGroupList registration) from the client reference. |
| `comp_restore.py` | Restore quest compensation blocks from v31. |
| `spawn_restore.py` | Reconstruct deleted `TerritoryData` spawns (zone-13 mob groups, zone-213 villager placements + Eria relocation) from the client shard; emits a plan (markdown + JSON). |
| `gen_npcloc.py` | Derive the `StrSheet_NpcLoc` quest-marker registry from server `TerritoryData` and **emit a spec** (`npcLocStrings`). `--out <spec path>` required; `--prune` also emits deletes for stale keys in the covered zones. Writes no datasheet. |
| `gen_collectionloc.py` | Derive `StrSheet_CollectionLoc` gather-node waypoints from `CollectionTerritory_13_*` and **emit a spec** (`collectionLocStrings`). `--out <spec path>` required. ADD-ONLY. Writes no datasheet. |
| `dcq.py` | Cross-source content query CLI (`quest` / `npc` / `name` / `collection`). |
| `audit_quests.py` | Deterministic Island quest-difference flagger (markdown + JSON worklist). |
| `dungeon_audit.py` | Dungeon reference integrity gate: DungeonData refs vs parsed per-HZ content; flags comment-disabled data. |
| `audit_item_references.py` | Item-id referential integrity gate, plus the `ItemTemplate` loader invariants, the token restriction policy, and the sum-to-1 probability bags. |
| `audit_player_text.py` | Player-facing text gate (DOCTRINE.md rule 10): fails the patch when a spec-authored string describes our build order rather than the world. |
| `audit_quest_design.py` | Quest design review (ADVISORY, always exit 0): reward duplication, gear-set completeness, class coverage, reference integrity, objective feasibility. |
| `auditlib.py` | Shared model for the design review: findings, the three scopes, waivers, corpus evidence. |
| `tests/` | pytest suite: hermetic fixtures plus corpus regressions pinned to `789fec28`. |
| `README.md` | This file. |

## Roadmap (planned modules)

All future modules import `dclib.py` and honor the HEAD-baseline rule.

- **npc-restore** - restore missing `NpcData` templates and `NpcSkillData` from v31.
- **loot-comp-restore** - restore `C`/`E` loot compensation npc tables from v31, respecting patch overlays.

Shipped:

- **quest_restore.py** - restore quest header wiring (prerequisite, story group, QuestGroupList registration) from the client reference.
- **comp_restore.py** - restore quest compensation reward blocks from v31.
- **spawn_restore.py** - reconstruct deleted `TerritoryData` spawns (client-only zone-13 mob groups + zone-213 villager placements and Eria relocation) from the client shard, as a reviewable plan.
- **dcq.py** - cross-source content query CLI (quest / npc / name / collection).
- **audit_quests.py** - deterministic Island quest-difference flagger with a worklist and JSON mirror.
- **dungeon_audit.py** - dungeon reference integrity gate (parsed-XML resolution of DungeonData territory/entity refs, comment-disabled detection).
- **audit_class_gates.py** - class-gate coverage gate against the current roster.
- **audit_quest_design.py** - quest design review (advisory): reward duplication, gear-set completeness, class matrix, reference integrity, objective feasibility, plus descriptive placement and effort reports.
