# IoD Padding Level 2 - Berlon Crafting-Intro Chain (proposal)

Design-first, AUTHORED content per DOCTRINE rule 4 (Level 2) and PADDING-BRIEF approved design
seed 1 (user, 2026-07-20). This doc captures the pre-authoring validation (brief-mandated), the
resolved design decisions, and the proposed chain structure.

Divergence-log category for the chain itself: **authored**. Its item-usability dependency is a
restoration (see "Crafting-restoration dependency").

## Resolved decisions (user, 2026-07-21)

1. **One-time linear chain** (6 quests, each completed once). Compliant with the framework
   anti-faucet invariant (`01-seasons.md §4d`); no repeatable EXP loop.
2. **Base-tier products, one-step recipes.** Craft Healing Potion I (6000) / Mana Potion I (6016)
   / Crit Power Scroll (6197) via the v31-faithful RAW recipes (91213/91221/91282) - gather then
   craft in one step. The Major tier was rejected: on v31 Major potions were not player-craftable
   and have no raw one-step recipe (would force a processing step and a v92 divergence). Base
   potions can still ALSO be merchant-sold; nothing in the data enforces exclusivity.
3. **Mana raw material = Sun Essence (1003).** The Mana Potion I recipe uses Sun Essence, gatherable
   in IoD (collection 301, Energy skill).
4. **No teaching step.** Players already hold the baseline crafting/gathering requirements; Berlon's
   "intro" is narrative only. Quest 1353 grants no skill.
5. **Crafted turn-ins are being un-deprecated.** The products currently read "no longer usable"; the
   crafting-restoration dependency below restores them to usable, so the chain's rewards are real.

## Validation results (v92, all GO)

### Items

| role | id | exact v92 name | notes |
|------|----|----|-------|
| raw: healing | 1001 | Verdra Fibers | plural; singular does not exist. |
| raw: mana | 1003 | Sun Essence | mana recipe input; IoD-gatherable. |
| raw: scroll | 1002 | Krymetal Ore | mining ore; IoD-gatherable. |
| product: healing | 6000 | Healing Potion I | usable in v31; v92 tooltip disabled (restore, see below). |
| product: mana | 6016 | Mana Potion I | same. |
| product: scroll | 6197 | Onslaught Scroll: Crit Power I | same. |
| kit: alchemy | 1616 | Apprentice Alchemical Kit | consumed by potion recipes. |
| kit: scroll | 1611 | Apprentice Scroll Kit | consumed by the scroll recipe. |

### Recipes used (base tier, v31-faithful, obtainable in both eras)

| recipe | produces | consumes | craft skill (v92) |
|--------|----------|----------|-------------------|
| 91213 | 6000 Healing Potion I x5 (crit 10) | Verdra Fibers 1001 x10 + kit 1616 x2 | Alchemy (26), Apprentice |
| 91221 | 6016 Mana Potion I x5 (crit 10) | Sun Essence 1003 x8 + kit 1616 x2 | Alchemy (26), Apprentice |
| 91282 | 6197 Crit Power Scroll x2 (crit 6) | Krymetal Ore 1002 x20 + Scroll Kit 1611 x1 | Alchemy (26), Apprentice |

(Skill id note: v31 used needSkillId 6, v92 remapped to 26 - a schema remap, not a break. The Major
recipes 26759/26775 and processed variants are intentionally unused.)

### Gathering nodes in IoD (area `13_ATW_Death_P`, all present)

- Verdra Fibers (1001): Collection 1 "Verdra Plant", Herb, ~46 live nodes.
- Krymetal Ore (1002): Collection 101 "Krymetal Ore", Mine, ~66 live nodes.
- Sun Essence (1003): Collection 301, Energy.

### Giver NPC

- Berlon = NPC template **1011**, HZ **64**, spawns at TerritoryData 6400015
  (x 70120.75, y -81504.60, z -3078.59), next to Annukha (1030). No new NPC authoring required.

## Proposed chain structure (one-time linear, 6 quests, ids 1353-1358)

| id | title (working) | task | reward |
|----|-----------------|------|--------|
| 1353 | Alchemy: First Gather | gather Verdra Fibers 1001 x10 | Healing Potion I 6000 x1, Apprentice Alchemical Kit 1616 x2, exp |
| 1354 | Alchemy: First Brew | craft + return Healing Potion I 6000 x5 (recipe 91213) | Apprentice Alchemical Kit 1616 pack, exp |
| 1355 | Mana Gather | gather Sun Essence 1003 x8 | Apprentice Alchemical Kit 1616 x2, exp |
| 1356 | Mana Brew | craft + return Mana Potion I 6016 x5 (recipe 91221) | Apprentice Alchemical Kit 1616 pack, exp |
| 1357 | Scrollwork Gather | gather Krymetal Ore 1002 x20 | Apprentice Scroll Kit 1611 x1, exp |
| 1358 | Scrollwork Craft | craft + return Crit Power Scroll 6197 x2 (recipe 91282) | Apprentice Scroll Kit 1611 pack, exp |

Quantities align to the recipe batch sizes (91213/91221 yield 5, 91282 yields 2). Prerequisites:
1353 gated behind an appropriate early story checkpoint (TBD at authoring); each later quest gated
on the prior.

## Reward calibration - XP + gold (the anti-punishment model)

Design problem (user, 2026-07-21): a mob-kill quest pays TWICE - incidental per-kill XP + loot-gold
earned while doing the objective, PLUS the turn-in. A gather+craft quest earns NOTHING incidental
(gathering gives gathering-skill points, not character XP; mats are consumed). If the turn-ins only
matched a combat quest's stated turn-in, the craft path would feel punished.

Benchmark (v31 source of truth):
- v31 GOLD = 10% of quest XP, a near-universal invariant. Follow it; it auto-restores loot-gold.
- IoD mob per-kill character XP ~= **85 + 27 x level** (L3~166, L5~220, L7~274). A typical kill quest
  (~10 mobs) hands out ~10x that incidentally - as much as or MORE than its own turn-in, so a combat
  quest's true payout is roughly **2x its stated turn-in**.
- Every v31 IoD "collect" quest was actually loot-from-kills (still combat), so v31 never had a pure
  gather+craft quest to compensate. Ours is the first; the incidental deficit is entirely ours to close.

Rule: **each Berlon quest XP = same-level combat base turn-in + (10 x per-kill XP at that level);
gold = 10% of XP.** This reaches per-quest parity with a combat quest's TOTAL payout. Because
gather+craft takes longer per quest than killing 10 mobs, the effective XP/hour still lands around the
framework 0.8x side weighting (`02-progression-lanes.md`) - not below (not punished), not above story.

Provisional levels + values (levels pinned to prereq gates at authoring; base turn-in from the v31
non-story band):

| id | quest | lvl | per-kill | +10 kills | base | proposed XP | gold |
|----|-------|-----|----------|-----------|------|-------------|------|
| 1353 | First Gather | 3 | 166 | 1660 | 600 | ~2300 | 230 |
| 1354 | First Brew | 3 | 166 | 1660 | 600 | ~2300 | 230 |
| 1355 | Mana Gather | 5 | 220 | 2200 | 900 | ~3100 | 310 |
| 1356 | Mana Brew | 5 | 220 | 2200 | 900 | ~3100 | 310 |
| 1357 | Scrollwork Gather | 7 | 274 | 2740 | 1200 | ~4000 | 400 |
| 1358 | Scrollwork Craft | 7 | 274 | 2740 | 1200 | ~4000 | 400 |

Chain total ~= 18,800 XP / 1,880 gold across L3-L7. Sanity vs budget: story quest 1316 alone pays
14,600 XP, and the ~25-quest story spine dwarfs this; the chain cannot outpace story and dungeons
(1.5x) stay the fastest path. Trim lever if it feels too rich: the three GATHER quests
(1353/1355/1357) are the lighter step and can drop to base + 0.5x incidental without touching the
craft quests. On top of XP/gold, every quest also grants the crafting-kit rewards in the table above.

## Crafting-restoration dependency (in-scope, decided 2026-07-21)

The three crafted products currently read "This item is no longer usable" on v92. Restoring them to
usable is a classic restoration and a prerequisite for the chain's rewards to be meaningful.

Finding (v31 vs v92): the disable is **only the ItemString tooltip**. All mechanical attributes
(`linkSkillId` 60220100/60220200/60225200, `combatItemType`, cooldowns, `requiredLevel`) are already
byte-identical to v31 on v92. So the restore is a tooltip revert to the v31 functional text.

CAVEAT - must verify function, not just text: because the use-binding is already intact yet the item
still reads disabled, the real mechanical gate may live in the linked SkillData sheet (not exposed by
MCP). After the tooltip restore, verify in-game that the item actually fires its effect; if it does
not, the linked skill/effect (60220100 etc.) also needs restoring.

Scope for THIS work: restore 6000, 6001, 6016, 6017, 6197 to usable (tooltip + function check).
(6001/6017 included for completeness even though the chain crafts base tier.) Economy fields
(buy/sell prices, v92-retuned higher) are left at v92 values unless a separate call reverts them.

The broader "import all old recipes / un-deprecate the full v31 consumable set" is a separate global
workstream - see `../../crafting-restoration/` (to be opened).

## Text authoring surface - DSL vs hand-edit (researched 2026-07-21)

Id convention: quest 135N -> group 13, index N; string ids `135N00X` (001 title, 002 start popup,
003 end popup, then per-task journal/button rows at 003+2N); files `00135N.quest`,
`QuestDialog_135N.xml`.

**DSL-authorable, all in spec 21 (`dsl apply` + `dsl sync` cover server + client):**
- `quests` - the 6 `.quest` bodies (headers with `giverNpc: "64,1011"`, task chains, reward flag,
  journalText wiring).
- `questStrings` - titles + per-task journal/objective/button rows + start/end popups. Author the
  per-task rows as standalone entries with computed ids (the inline `strings:` block only sets the
  title). `StrSheet_Quest` DOES sync to client (shard-routed).
- `questDialogs` - briefing (node 2) + journal summary (node 100) + per-task dialog nodes, with the
  quest-link markup embedded in the text. `QuestDialog` syncs to client (IdSorted).
- Quest-link MARKUP - `{@LinkNpc:64#1011#Berlon}` / `{@LinkCreature:hz#tmpl#Name}` tokens, embedded
  in the dialog/strings above.
- QuestGroupList registration (`questStoryGroups`/`questHuntingZones`) to file 1353-1358 in the IoD
  group - server-side DSL op; QuestGroupList has NO client sync entity (server-only, fine).
- `villagerMenus` - NOT needed. A quest offer is driven by the quest header `giverNpc`, not a menu.
  Only add a menu if Berlon should ALSO sell or run a crafting service (open decision).

**Hand-edit (cannot go in the spec):**
- `StrSheet_NpcLoc` link registry (client-only, no DSL schema): regen via `gen_npcloc.py` from the
  restored server `TerritoryData` so the `{@LinkNpc/LinkCreature}` tokens resolve (Berlon 64#1011 +
  every gather/target ping). Markup without a registry entry = silent dead link. Standard post-wiring
  step.
- Berlon's ambient text bubbles (`VillagerDialog`) - dual hand-edit (server `VillagerDialog_64.xml`
  + client per-villager shard); DSL entity broken + no sync. OPTIONAL: only if we change what he says
  idly. For iteration 1 his existing scholar lines can stay (open decision).

## Voice & lore fit (researched 2026-07-21)

- **Berlon = Baraka scholar** at the Tower Base research hub; measured, mission-first register, invokes
  the god Oriyn, frames small tasks against big stakes (garrison survival, getting the federation
  home). Classically a flavor NPC with no quest role - a clean slate to attach a giver to. Real lines
  recovered (e.g. "Our efforts here must succeed... we cannot be certain this island is permanent").
- **Annukha (1030, Aman warrior)** stands beside him as a comic foil - bored at the post, wants to
  "sink this blade into some demons over in the gorge." Use her as the field-test volunteer on the
  scroll cycle.
- **IoD already has the vocabulary:** node-gathering taught via Mock Rocks + [F] (quests 1382/1384),
  and a garrison-logistics frame ("resupply from what the island provides"). MATERIAL NAMING
  CORRECTION: the chain's text must name the ACTUAL recipe inputs the player gathers - Verdra Fibers
  (1001), Sun Essence (1003), Krymetal Ore (1002) - not the mob-drop essences (heartwood essence /
  mana crystals) the research agent first suggested; those are different items. The narrative FRAME
  (self-sufficiency, Berlon the scholar, Annukha field-test) still holds around the real materials.
- **Premise:** the garrison bleeds through field supplies faster than the federation can ship them;
  Berlon argues the island can supply itself and recruits the player to gather + brew on-site.
  Per-cycle hook: heal draughts (Verdra Fibers) -> mana potions (Sun Essence) -> battle-focus scrolls
  (Krymetal Ore, tied to Annukha's gorge push).
- **Style rules:** measured Baraka voice; address player by `<PCCLASS:lcase>`/`<PCNAME>`/"recruit";
  one-sentence imperative journal blurbs; short (2-4 sentence) giver dialog split with `<BR><BR>`
  ending by naming the next stop; one light pun per title, plain objective line; completion button
  "For the federation!".

## Non-text authoring surface

- QuestCompensationData_13 reward rows (INTERNAL class names; namespace trap per doctrine whitelist 2).
- ItemString tooltip restore for the 5 consumables (+ in-game function verify).
- Spec files: patch 001 next free = **21** (`21-iod-berlon-crafting-chain.yaml`); item-usability
  restore as its own spec (`22-consumable-usability-restore.yaml`) or folded into the crafting-
  restoration workstream. Applied via migrate batch replay only. NpcLoc regen after wiring.
- divergence-log.md: one AUTHORED entry per new quest; the item restore is a restoration entry.
