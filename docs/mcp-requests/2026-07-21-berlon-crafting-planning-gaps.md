# Datasheet MCP Improvement Requests: Berlon Crafting-Chain Planning (2026-07-21)

Gaps surfaced during the IoD Level 2 "Berlon crafting-intro chain" planning pass (validating items,
recipes, gathering nodes, quest rewards, and quest/dialog text across v31 and v92). Tool names given
without the `mcp__datasheet-vNN__` prefix; server noted per item. Several agents had to fall back to
reading raw datasheet XML because no MCP path exists.

## Blocking gaps (no MCP path to the data)

1. **No queryable entity for crafting recipes (`ItemProduceRecipe`).** Not in `list_entity_types`
   (v31 and v92). There is no way to ask "what recipe produces item X", "what does recipe R consume",
   or read the `obtainable` flag / craft skill / output count. Two agents had to open
   `Datasheet\ItemProduceRecipe.xml` directly (v92: 1552 recipes; v31 similarly) and parse by hand.
   This is core crafting data and is central to the crafting-restoration workstream just opened.
   Request: expose `ItemProduceRecipe` as an entity with product->recipe and recipe->ingredients
   lookups, or a `trace_item_dependencies` extension that includes recipes as producers (it already
   claims to cover recipes but returned nothing usable for these consumables).

2. **No `Skill`/`SkillData` entity exposed.** Restoring the "no longer usable" consumables
   (6000/6001/6016/6017/6197) requires checking the skill/effect their `linkSkillId` points at
   (60220100, 60220200, 60225200, ...) to confirm the item still FUNCTIONS, not just reads usable.
   Neither server exposes Skill in `list_entity_types`, so the mechanical gate behind the disabled
   tooltip could not be inspected via MCP; the item-usability conclusion had to carry an explicit
   "verify in-game or inspect the skill sheet outside MCP" caveat. Request: a read-only Skill/effect
   entity or at least a resolver that reports whether a `linkSkillId` resolves to a live skill.

3. **Quest bodies (`QuestData` / `.quest`) are not a queryable entity.** `find_free_ids` with
   `entityType: "QuestData"` and `"quest"` both return "Unknown entity type" (v92), so there is no
   MCP way to find free quest ids or read a quest's task structure/prerequisites/giver. Had to glob
   the server `QuestData\*.quest` files to allocate ids 1353-1358. (Continues the 2026-07-17 item 18
   "Quest is not in list_entity_types"; still unresolved.) Request: a `quest` entity (or `find_free_ids`
   support keyed off the QuestData directory) and a task-structure reader.

## Correctness / output-format friction

4. **`lookup_quest_dialogs` per-task dialog is a shared rotating pool, not the quest's own lines.**
   (v31.) The per-quest journal blurbs and start-popups resolve correctly, but the "NPC dialog" it
   prints for each task is the same ~10 recurring IoD NPCs' generic lines repeated across every quest,
   so it cannot be used to read a specific quest's authored task dialog. Forced treating the NPC
   quotes as representative zone voice rather than verified per-quest text during the lore study.
   (Related to 2026-07-17 item 14, which noted orphan dialog texts with no task association.) Request:
   bind per-task dialog to the quest's actual `QuestDialog_{id}.xml` `Text` nodes.

5. **Quest task-TYPE is not surfaced by reward/quest tools.** `lookup_quest_rewards` and
   `search_quests` expose id/level/reward but not whether a quest's objective is kill / collect /
   delivery. The reward-benchmark pass had to infer type from quest titles, which is unreliable
   (every IoD "collect" quest is actually loot-from-kills, a distinction that mattered for the
   XP calibration). Request: expose the task type(s) from the quest body in the quest/reward tools.

## Note

Items 1-3 all stem from the same root: crafting recipes, skills, and quest bodies are three
high-value datasheet families with NO entity coverage, so any crafting- or quest-authoring task
falls back to raw XML. Prioritizing recipe + quest-body entities would unblock the crafting-
restoration workstream and future authored quest chains.
