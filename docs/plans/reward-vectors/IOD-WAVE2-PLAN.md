# IoD Reward Vector Wave 2: the token sink

_Opened 2026-07-31. Design rulings live in `IOD-BACKLOG.md`; this file holds the build order, the
spikes, the acceptance gates and the open decisions. It is deliberately short. Wave 1's planning
documents ran to 1,827 lines and were retired because their content was duplicated at the point of
use; this one records only what a spec header, a config comment or a gate cannot._

Scope: backlog items **RV-02** (the Valkyon Quartermaster), **RV-05a** (Kugai's Crest converted off
its right-click shop) and **RV-13** (Sorcha re-entry). Folds into the OPEN patch 002.

## Goal

When this is done, the Valkyon Commendation can be spent. A physical quartermaster NPC stands at
Tower Base, authored by this project from scratch, and sells a token-priced catalogue. The Kugai's
Crest shop moves off its inventory right-click onto a physical NPC, which removes the last
`MEDAL_USEABLE` shop on the island and satisfies ruling R11. A player who has completed Sorcha can
walk back in. Framework reward parity (`03 §3b-i`), unsatisfied since the token shipped with no
sink, holds again.

## Out of scope

- **RV-04**, the Sorcha and Karasha dungeon tokens. A second and third token item triples the vendor
  work in one wave. They come after this wave proves the pattern live.
- **RV-14**, Sorcha's promotion to Tower Base with her own shop. Depends on RV-04.
- **RV-09 to RV-12**, reputation and dailies. Blocked on PROBE-1 and PROBE-2 and large enough to own
  a wave.
- **RV-26's remaining legs**, MWA off trash and the dyad structure cap. Real framework debt, no
  player-visible payoff next to a working vendor.
- **The leveling-scroll conversion.** Deferred until level sync exists (`02 §5`).
- **Re-pricing the token ladder.** The 150-ceiling effort ladder stays as shipped. Tuning it against
  a sink is the wave AFTER this one, once accumulation data exists.

## Files and interfaces

| File | Role |
|---|---|
| `specs/patches/002/44-valkyon-quartermaster.yaml` | NEW. The NPC template, its spawn, strings, menu and catalogue |
| `specs/patches/002/20-kugai-token-shop.yaml` | AMEND. Swap `villagerMenuItems` for `villagerMenus`, add the host NPC |
| `specs/patches/002/45-sorcha-reentry.yaml` | NEW. `DungeonData_9037` condition plus WorkObject 134 |
| `packages/progression-tokens/index.yml` | Add the quartermaster's menu and BuyList ids |
| `packages/iod-tokens/index.yml` | Kugai keeps its ids; the host NPC id joins them |
| `tools/dc-restore/gen_npcloc.py` | Re-run with `--prune` if the spawn set changes |

Entities this wave uses: `npcs`, `territoryGroups` / `territorySpawns`, `creatureStrings`,
`villagerMenus`, `buyMenuLists`, `buyLists`, `exchanges`, `villagerDialogs`, `dungeonDatas`,
`workObjects`.

**The canon shape is fully measured and needs no rediscovery.** NPC `59,1955` "Major Milestone" is
the base game's own NPC-attached token shop:

```
VillagerMenu.xml   <Villager id="59,1955"><Menu type="MedalStore" id="280" /></Villager>
BuyMenuList.xml    <Menu id="280" desc="..." stringId="280"><ItemList id="2801" stringed="2801" /></Menu>
BuyList.xml        <List id="2801" NeedMedalItemId="72"><Item priceRevision="1" itemId="4672" /> ...
ItemMedalExchange  one row per (itemId, medalItemId, buyPriceMedal)
```

Our Kugai shop already authors three of those four blocks. **The only structural difference between
a right-click shop and an NPC shop is which block binds the menu**: `villagerMenuItems` binds an
ITEM to it, `villagerMenus` binds an NPC. That is what makes RV-05a cheap.

## Phase 0: de-risk

Three unknowns, and the first is load-bearing enough that nothing else should start before it
resolves. All three are cheap.

### SPIKE-1: can this project author a new NPC template at all?

**Question.** No spec in `specs/patches/` has ever used the `npcs` entity. Patch 003's own scope doc
calls itself "the first patch to author new monster templates, so it is the first use anywhere in
this repo of the `npcs:`, `ai:` and `npcSkills:` DSL entities". This wave needs one villager, which
is simpler than a monster (no AI, no skills), but the entity is still unexercised here.

**Experiment.** Author a minimal villager template in `NpcData_64.xml` cloned from an existing Tower
Base villager, spawn it beside Jirash, apply, deploy, restart, and look at it.

**Data.** Server boot log clean; the NPC visible in game; talkable.

**Threshold.** GO only if the NPC renders and is clickable. A template that loads but does not
render means the client leg is missing, which SPIKE-2 covers.

### SPIKE-2: is `npcs` mapped to the wrong sync target?

**Question.** `tools/migrate/migrate.py:98` maps `"npcs"` to `None`, on a comment claiming `NpcData`
is server-only. **The client DataCenter holds 426 `NpcData` shards, and `config/sync-config.yaml:392`
carries a full `NpcData` ZoneBased descriptor.** Those two facts contradict the comment. If the
client genuinely needs the template row, a new NPC will never render and the log will say nothing.

This is the exact failure class this project has already paid for twice: `QuestCompensationData` was
mapped to `None` on a blanket "compensation families are server-only" claim and the quest log lied
for months; `AreaData` had a descriptor whose `source_mapping` omitted a prefix and never synced at
all. **Do not resolve this by reasoning. Measure it.**

**Experiment.** Diff a client `NpcData` shard against its server file for an existing zone and see
whether the client carries template rows for villagers, or only a subset. Then, with SPIKE-1's NPC
authored, sync with the key mapped and confirm the row reaches the client shard.

**Data.** Whether client `NpcData-000NN.xml` contains a `<Template id="1023">` row for Jirash.

**Threshold.** If the client carries villager templates, map the key and correct the comment. If it
does not, leave `None` and record WHY, with the evidence, so the next reader does not reopen it.

### SPIKE-3: does an NPC-attached MedalStore work for a token we authored?

**Question.** Backlog §4.2 records NPC-attached token shops as canon-proven (`59,1955` with vanilla
item 72) but never authored by this project. Our three existing token shops are all right-click.

**Experiment.** Bind a one-item `MedalStore` menu to SPIKE-1's NPC, priced in 95217. Buy the item.

**Data.** The shop window opens at the NPC; the purchase debits the correct token count.

**Threshold.** GO. On failure, the fallback is a `Merchant` menu, and the wave narrows to what that
supports.

Phase 0 ends with an explicit GO or NO-GO recorded in this file, backed by what was observed in
game. On NO-GO for SPIKE-1, the wave does not proceed with a right-click shop instead: that would
contradict R11 while pretending to satisfy it.

## Phase 1: the quartermaster exists

**Goal.** A named Valkyon quartermaster stands at Tower Base and can be talked to.

**Changes.** `specs/patches/002/44-valkyon-quartermaster.yaml`:

- `npcs: upsert` a villager template in hunting zone 64. Free ids: **1012 to 1020, 1035 to 1040, or
  1057 upward** (HZ 64 currently holds 1001 to 1011, 1021 to 1034 and 1041 to 1056).
- `territoryGroups` / `territorySpawns` placing it in group **6400002** (Supply Base North), which
  already holds Jirash `64,1023` at `67089,-81620,-3255` and Taras `64,1028` at
  `67294,-81783,-3255`. Tower Base's recall point is `66600.87,-79855.52`, so this cluster is where
  a returning player arrives.
- `creatureStrings` for the name, `villagerDialogs` for one greeting line.

**Acceptance criteria.**
- `dsl validate` reports 0 errors on the new spec.
- After `migrate --patch 002`, the server dirty set grows by exactly `NpcData_64.xml`,
  `TerritoryData_64.xml`, `StrSheet_Creature.xml` and `VillagerDialog_64.xml`, and nothing else.
- `audit_item_references.py`, `audit_player_text.py`, `dungeon_audit.py --dungeons 9037` and
  `audit_class_gates.py --zones 13,64,213,436` all exit 0.
- `gen_npcloc.py --prune` runs clean if the spawn set moved.
- Live: the NPC is visible, named correctly, and talkable.

## Phase 2: the shop opens and sells

**Goal.** The quartermaster sells a token-priced catalogue.

**Changes.** Same spec, four blocks in the shape measured above:

- `villagerMenus`: a `MedalStore` menu bound to the new NPC.
- `buyMenuLists`: the menu with its tabs.
- `buyLists`: `needMedalItemId: $EARLY_PROGRESSION_TOKEN` plus the items.
- `exchanges`: one row per item, matching each BuyList `priceRevision` exactly. A mismatch here is
  what makes a purchase silently fail.
- `packages/progression-tokens/index.yml`: menu and list ids from the project's reserved 9999xxx
  band. **Taken: 9999001, 9999004, 9999006, 9999008 (menus); 9999005, 9999007, 9999009, 9999010,
  9999011 (lists).** Next free pair is **9999012 / 9999013**.

**Catalogue, strawman, needs approval before authoring.** Income is **1,182 tokens per character for
a full island clear** (framework `99 #02-progression-lanes`), and it is per character, so these
prices are set against one character-run.

| Tab | Item | Price | Reasoning |
|---|---|---|---|
| Materials | Feedstock x50 | 20 | The routine sink. A full clear buys plenty, which is the point: the token is meant to relieve the enchant grind, not gate it |
| Materials | Masterwork Alkahest x10 | 25 | Pairs with feedstock on every enchant attempt |
| Supplies | HP / MP potion x10 | 10 | Cheap, always useful, keeps low-value token stacks spendable |
| Supplies | Campfire x5 | 15 | Utility, no power |
| Crystals | one uncommon crystal | 40 | `03 §3c` permits crystals as a power spend; uncommon caps it |
| Cosmetic | one dye or hat | 300 | The chase sink. About a quarter of a full clear, so it is a decision rather than an afterthought |

Total for one of everything is 410, so a full clear funds the cosmetic plus a solid material stock
and still leaves a surplus. That surplus is deliberate: this is the first sink, and a catalogue that
absorbs every token leaves nothing to measure.

**Acceptance criteria.**
- Every `buyLists` `priceRevision` has a matching `exchanges` row at the same price. Check by parsing
  both after apply, not by reading the spec.
- All four gates exit 0.
- Live: the shop window opens at the NPC, each tab renders, and one purchase from each tab debits
  the stated number of tokens.

## Phase 3: Kugai's Crest moves to an NPC

**Goal.** No `MEDAL_USEABLE` right-click shop remains on the Island of Dawn (R11).

**Changes.** Amend `specs/patches/002/20-kugai-token-shop.yaml`:

- Replace the `villagerMenuItems` block with a `villagerMenus` block binding menu `9999008` to a host
  NPC. **The three `buyMenuLists`, `buyLists` and `exchanges` blocks are unchanged**, which is the
  whole reason this phase is cheap.
- Item 95216 drops `combatItemType: MEDAL_USEABLE` for `NO_COMBAT` and `itemUseCount: 1` for `0`, so
  the dead right-click affordance does not linger.
- Author the host NPC, or bind to an existing one. **Open decision, below.**

**Acceptance criteria.**
- A corpus sweep finds zero `VillagerMenuItem` rows referencing any Island of Dawn token.
- `audit_item_references.py` exits 0 (item 95216 still resolves everywhere it is referenced).
- Live: right-clicking Kugai's Crest does nothing; the shop opens at the NPC and still sells its
  level-8 set at the shipped prices.

## Phase 4: Sorcha re-entry

**Goal.** A character who has completed quest 1346 can re-enter Sorcha.

**Changes.** `specs/patches/002/45-sorcha-reentry.yaml`:

- `dungeonDatas`: add a `completeQuest 1346` entry condition to `DungeonData_9037` beside the
  existing gate. Dungeon 9036 already ships this exact `progressQuest`-OR-`completeQuest` pattern,
  so it is a copy, not an invention.
- `workObjects`: ungate portal template 134. A WorkObject quest window (`isForQuestId` plus
  `firstTaskId` / `lastTaskId`) expresses an ACTIVE task bracket only; there is no completion-based
  form, so the window has to come off rather than be widened.
- Patch-002 party rules stay exactly as they are.

**Acceptance criteria.**
- `dungeon_audit.py --dungeons 9037` exits 0.
- The client leg matters here: `workObjects` maps to `WorkObjectData`, which IS client-synced, so
  this phase needs a repack. `dungeonDatas` is server-only.
- Live: a character with 1346 complete re-enters; a fresh character still enters through the quest
  path.

## Phase 5: apply, gate, deploy

**Goal.** The wave is on dev and testable.

**Changes.** One `python tools/migrate/migrate.py --patch 002`, whole patch, never a subset. This run
also picks up **specs `002/37`, `002/39` and `002/43`**, which were authored on 2026-07-31 and
deliberately left unapplied rather than spending a deploy cycle on tooltip text.

**Acceptance criteria.**
- Migrate reports 0 failed and 0 warnings, client sync clean.
- All four gates exit 0: `dungeon_audit`, `audit_class_gates`, `audit_item_references --retired`,
  `audit_player_text --patch 002`.
- `deploy_dev.py --verify`, all files hash-verified.
- Client packed, installed and published; the installed `.dat` hashes identical to the packed one.
- **Live validation is the user's**, and this wave earns it: it is content, not text.

## Open decisions

Two, both wanted before Phase 2 starts.

**1. Does the tooltip's promise need a second quartermaster?** Item 95217 now reads "Exchange with
Valkyon quartermasters in major towns and outposts." This wave places exactly one, at Tower Base.
Velika (HZ 63) is already inside patch 002's scope, and the token is band-wide by R25, so a second
quartermaster there would make the plural true for the two hubs a sub-60 player actually uses. It
costs one more NPC and one more `villagerMenus` row; the menu, lists and exchanges are shared. My
recommendation is to add it, in Phase 2, sharing the catalogue.

**2. Does Kugai's Crest get its own NPC or ride the quartermaster?** One NPC with two `MedalStore`
menus is fewer moving parts, and `VillagerMenu` does allow multiple `Menu` children. But Kugai's
Crest is a boss trophy and the quartermaster is a Valkyon institution, so sharing muddles both. My
recommendation is a separate NPC near the Tower Base cluster, which also keeps the two shops
independently testable. Whether two `MedalStore` menus on one villager even works is unproven and
would become a fourth spike if we went that way.

## Risks

| Risk | Mitigation |
|---|---|
| `npcs` has never been used in this repo | SPIKE-1, before anything else |
| A new NPC template may need a client leg that migrate does not send | SPIKE-2, measured against an existing villager rather than reasoned about |
| `BuyList`, `ItemMedalExchange` and `VillagerDialog` have no sync-config descriptor | Their DSL keys are mapped to `None` deliberately, so no E603. Confirm during Phase 2 that the shop works with the server leg alone |
| `priceRevision` and `exchanges` drifting apart | Checked by parsing both after apply, in Phase 2's criteria |
| The wave lands on top of three unapplied text specs | Phase 5 states them explicitly so their footprint is expected, not a surprise in the dirty set |
