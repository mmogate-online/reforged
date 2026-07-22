# IoD Level 2 Roadmap (padding phase, post-Berlon)

Forward plan agreed with the user 2026-07-21. Read alongside `PADDING-BRIEF.md`
(Level 2 section), `../DOCTRINE.md` (rule 4), and `TRACKER.md`. This captures the
sequencing so a new session can continue without re-deriving it.

## Current state (2026-07-21)

- **PATCH 001 CLOSED.** The Berlon crafting-intro chain (Level 2 first slice) is
  LIVE-VALIDATED END TO END and committed locally on all three repos (server
  datasheet, client-dc, specs), NOT pushed. Client published through 0.1.0-dev.33.
  All DSL requests delivered and adopted natively (pipeline is fixup-free). Later
  refinements landed on the first cut: material give-back so the craft step is pure
  crafting; recipe designs 91213/91221/91282 restored to v31 identity (spec 22);
  gather-node map markers authored via the new `gen_collectionloc.py`
  (StrSheet_CollectionLoc for tier-1 collections 1/101/301). **Steps 2-4 below are
  the next session's work.**
- Original first-slice notes (superseded by the above, kept for reference):
- **Berlon crafting-intro chain (Level 2, first slice).**
  - Spec `specs/patches/001/21-iod-berlon-crafting-chain.yaml`: 6 one-time linear
    quests 1353-1358 (gather/craft: Verdra Fibers -> Healing Potion I, Sun Essence
    -> Mana Potion I, Krymetal Ore -> Crit Power Scroll), Berlon giver (64,1011),
    XP/gold + Apprentice kit rewards. Ungrouped (like all IoD side quests; user
    decision, story group left off because QuestGroupList is server-only).
  - Spec `specs/patches/001/22-iod-consumable-usability-restore.yaml`: reverted the
    "no longer usable" tooltip on 6000/6001/6016/6017/6197 to v31 functional text.
  - DSL `journalScript` field (datasheetlang `cd080461`) is used natively; the
    interim fixup script is retired. Full pipeline is clean and idempotent.
  - Deployed: server delta pushed to dev (15 files, hash-verified); client `.dat`
    packed + installed to the local game client. NOT published to CF. NOT committed.
  - Live-test checkpoints: see the task brief / `quest-live-test`. The single
    riskiest one: confirm 6000/6016/6197 actually FIRE in-game (tooltip-only
    restore may not unlock a skill-gated item; if not, the linked SkillData needs
    restoring too, out of spec 22 scope).

## Sequence from here

1. **Close patch 001 (only after Berlon is fully live-validated).**
   - Land one "close patch 001" baseline commit per repo (server `server_datasheet`,
     client `client_datacenter`) plus the specs repo. First mid-patch commit was
     premature; going forward follow the Patch Application Discipline in the root
     `CLAUDE.md` (apply/sync the whole patch, commit only on close).
   - Update `TRACKER.md`, `divergence-log.md` (6 AUTHORED quest rows + 1 restoration
     row for the tooltip restore), `CHANGELOG.md`/`STATUS.md` via `/log-progress`,
     and `/learn` any new traps (link-token `{@LinkCreature}` not `{@LinkNpc}`;
     IdSorted new-quest renumber needs `--no-narrow`).

2. **Bump patch 002 -> 003.** The current patch 002 ("Reforged customizations",
   ~40 specs + `balance/`, `evolutions/`, `loot/`, `docs/patch-002-scope.md`)
   becomes patch 003. Rename the spec folder, the scope doc, and every reference
   (grep for `patch.?002` / `patches/002` across `docs/`, `CLAUDE.md`,
   `CHANGELOG.md`, `STATUS.md`, tracker/plan docs). This is a deliberate doctrine
   change: Level 2 authored additions move OUT of patch 001 into their own layer.
   Update `DOCTRINE.md` rule 4 and `PADDING-BRIEF.md` to reflect that Level 2
   contextual additions are patch 002, applied on the closed patch-001 baseline.

3. **Patch 002 = Level 2 contextual additions (design-first authored content).**
   We are NOT done with Berlon. Continue the Level 2 directions from
   `PADDING-BRIEF.md` (Level 2 section), each needing user approval and a stated
   datasheet mechanism:
   - Further Berlon / crafting content beyond the first 6-quest slice.
   - Presence / lore NPCs in towns and camps (ambient VillagerDialog, no quests).
   - A gathering-tutorial hook if Berlon's chain does not cover it.
   - Exploration incentives expressible in datasheets (collect/visit over the
     restored sections).

4. **Pacing review (framework-gated).** The Berlon chain adds a large new XP
   source (~18,800 XP across L3-L7, plus loot-gold parity). With Level 1 padding
   and Level 2 both live, recheck the 1-to-11 curve against the content framework
   (`02-progression-lanes.md`, `01-seasons.md` anti-faucet invariant): the story
   spine must not be trivially outleveled, and side content must stay on the
   framework's side-weighting. Adjust CANDIDATE rewards first (the three gather
   quests 1353/1355/1357 are the lightest lever), never story rewards. Consult the
   `content_framework` repo before changing any reward budget.
