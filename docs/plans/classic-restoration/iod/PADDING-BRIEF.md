# IoD Padding Phase Brief (Phase 7)

Session primer for the padding phase. Written 2026-07-20 at the close of the port session; the
padding work happens in a NEW session primed with this brief, `../DOCTRINE.md` (rule 4, two-level
model), `../ZONE-PORT-PLAYBOOK.md`, and `TRACKER.md`.

## State at handoff

- v31 baseline live-validated end to end and committed (server `c59c18ff` + alpha boundary
  `4579d3f9`; client `43bedc3a` + `32ed6274`). Client published 0.1.0-dev.24.
- Live quest set: exactly the 25 story/training quests (story groups 1 and 2). All 40 other band
  quests are sentinel-disabled in v31 itself; IoD has ZERO yellow quests today.
- User verdict on the baseline: progression works and pacing is balanced, but the map feels
  BLAND: missing mob spawns (called out: the Mysterious Ruins area), no side content, towns and
  camps feel empty.

## Mission

Two-level padding per doctrine rule 4. We are a fresh-start server: the goal is to motivate and
reward exploration so content does not feel rushed, not to maximize leveling speed.

### Level 1: faithful restoration (data-first)

1. **Quest inventory comparison:** build the inventory of currently established+validated quests
   (the live 25) and compare against the v17 quest set (63 classic band quests; extraction
   artifacts from the retired pilot at `../../iod-alpha-content-loop/data/` are reusable inputs:
   v17-quests, classification-quests). Output: per-candidate table of the 40 disabled quests
   (plus any v17-only content) with verdicts: RESTORE / ADAPT / OUT, each justified.
2. **Enable gates (doctrine):** server data intact AND all referenced NPCs standing AND no
   conflict or reward duplication with the live set. Known gate failures: the ~16 quests
   referencing never-built camps (Leander's Outpost roster, Kamarnu/Riel/Kirash/Clovis/Milun).
   Known first candidates: Taras 1343/1344 (giver stands, data intact).
3. **Awkward-duplicate screen:** zone quests that retell or contradict live story quests (same
   target mobs, same collect objectives, contradictory dialog states) must be flagged; run the
   agentic v31-vs-v17 storyline overlap map BEFORE enabling anything.
4. **Reward-conflict screen:** compare candidate rewards against the ported reward sheet; no
   duplicate class-bag pieces at the same tier, no reward that obsoletes a story reward earlier
   than v17 pacing did.
5. **Internal-inconsistency fixes on enable:** 1322 (task 300931 vs dialog 300932) and 1327
   (task 300921 vs dialog 13#304) carry dormant contradictions; doctrine rule 1 fix + divergence
   log entry required for whichever gets enabled.
6. **Mob habitat replication (mobs only, never NPCs):** v17 fence geometry + roster, populations
   and flags from comparable v31 territories, every territory logged as approximation. First
   target: the Mysterious Ruins area (user-reported bland/missing spawns). Compare v17
   TerritoryData fences for HZ 13 against baseline coverage to find de-populated pockets.
7. **Dormant systems research:** daily/repeatable quests, challenges, events, dungeon extras
   present in v17 and dormant in v31/v92 (e.g. Sorcha's Reckless Challenge). Triage question 1:
   is it expressible in datasheets at all?

### Level 2: contextual additions (design-first, each needs user approval)

Approved design seed 1 (user, 2026-07-20): **Berlon (64,1011) alchemy / MWA crafting intro
chain.** Quest-chain structure as specified:

- Q1: bring 1 Verdra Fiber; reward: 1 Healing Potion I + 2 Apprentice Alchemical Kit.
- Q2: bring 5 Healing Potion I (player must CRAFT them via the healing potion recipe).
- Cycle repeats for Mana Potion I: first the raw material quest, then the crafted-potion quest.
- Cycle repeats for Onslaught Scroll: Crit Power I (the recipe requiring Krymetal Ore).
- Per completed cycle: a pack of crafting kits per material crafted (Apprentice Alchemical Kit,
  Apprentice Scroll Kit) plus exp.

Validation before authoring: confirm every item/recipe id exists and works on v92 (Verdra Fiber,
Healing/Mana Potion I recipes, the crit-power scroll recipe and Krymetal Ore, both kit items);
confirm gathering nodes for the raw materials exist in IoD; check reward exp against the
framework budget for the level band.

Other Level 2 directions (unvalidated, to be developed with domain-docs knowledge and proposed
to the user): presence/lore NPCs in towns and camps (walking or standing, ambient VillagerDialog
lines, no quests required); a gathering-tutorial hook if Berlon's chain does not cover it;
exploration incentives expressible in datasheets (e.g. collect/visit quests over the restored
sections). Every proposal must state the datasheet mechanism it uses (see the domain docs:
quest-system, villager-dialog-system, villager-service-system, quest-link-system).

### Pacing review (after both levels land)

Side quests add alternative leveling via gathering, exploration, and repeatables. Recheck the
1-to-11 curve: the story spine must not be trivially outleveled; adjust candidate rewards (not
story rewards) first. Framework invariants are binding.

## Process notes for the padding session

- Prime with: `content-restoration` skill (v31-primary doctrine summary), `domain-research`
  (NPC dialog and quest editing routing block), `dsl-definitions`, `new-spec`, `apply-spec`,
  `quest-live-test` (live checkpoints from spec diffs).
- Specs continue the patch 001 numbering (next free: 14). Level 1 and Level 2 belong in separate
  specs; Level 2 divergence-log entries use category "authored".
- All applies via `migrate --patch 001` batch replay ONLY. NpcLoc regen (`gen_npcloc.py --prune`)
  after any spawn change. World-server restart is manual (user).
- The VillagerDialog DSL entity is BROKEN (docs/dsl-requests/2026-07-20-villagerdialogs-entity-broken.md):
  ambient line edits are dual hand edits (server per-zone file + client per-villager shard) until
  the DSL team delivers. SpeechCondition (.condition) authoring works via speechConditions.
- New NPCs (Level 2) need: NpcData template (or reuse), TerritoryData spawn, StrSheet_Creature
  client string, NpcLoc regen, optional VillagerMenu/VillagerDialog/.condition. Check
  `npc-standard` package and the playbook family map first.
