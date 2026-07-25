# Datasheet MCP Improvement Requests: Berlon Crafting-Chain Planning (2026-07-21)

## Resolution log (2026-07-25): CLOSED

datasheet-mcp commits `e9af2bd` (skills) and `8d8c6de` (quest bodies). 391 tests green; Release AOT
publish validated over a direct stdio harness against v92 and v31.

**Root cause of item 1 (and part of the general "nothing is exposed" impression): a stale deployed
binary.** `.mcp/datasheet-mcp.exe` was a May 8 build and `.mcp/entity_config.json` an April 25 copy,
while the repo had moved on. That staleness is invisible from inside a session, because tools answer
from the old binary. A `deploy-mcp.ps1` script and a `files` column on `list_entity_types` now make
it detectable and one command to fix.

- **Item 1 (ItemProduceRecipe): rejected, already working.** `ItemProduceRecipe` has been a
  configured entity since April, is listed by `list_entity_types`, and carries `obtainable`,
  `needSkillId`, `needGrade` plus `Materials` and `Result` child sections. Both reverse directions
  already work through `trace_item_dependencies`: item 200999 reports "Craft Recipes as result:
  Recipe 1466", item 206817 reports 8 recipes "as material". The consumables in the report
  (6000/6001/6016/6017/6197) genuinely have no recipe, which is why the trace looked empty.
- **Item 2 (Skill / linkSkillId): done.** New `Skill` entity over the Common skill family
  (`UserSkillData_Common.xml` plus `_Guild`, `_Vehicle`, `_EventSeed`), and a new `linkSkillId`
  reference on `Item` so `check_references` validates it. `check_references Item 6000` now reports
  `linkSkillId = 60220100 -> Skill FOUND`, and `lookup Skill 60220100` returns
  `Item_HP_Recovery_LV_1` with its `Precondition` cooldown block. 2,940 of the 2,957 items carrying
  a `linkSkillId` resolve; the 17 that do not point at region-specific vehicle skills.
  The 119 per-class `UserSkillData_{Class}_{Race}_{Gender}` shards are deliberately excluded: they
  total ~375 MB and `Skill.id` is unique only per `templateId`, so a flat index would collide.
  Class-skill browsing needs a dedicated indexed reader, which no request has asked for yet.
- **Item 3 (quest bodies): done.** New `lookup_quest(questId, includeTaskBodies?)` renders the
  header (category, story group, connected quest, repeatability), the `발생조건` giver trigger with
  the NPC name resolved, the `수행조건` acceptance gates (level, class, race, reputation, guild),
  prerequisite quests with their titles, start items, the task table, and a generic per-task body
  dump that walks the tree rather than hard-coding element paths, so no authored value is hidden.
  `find_free_ids` now accepts `entityType: "Quest"` and scans the `QuestData` id space
  (`Quest` is not an entity_config table, so the tool routes internally).
- **Item 4 (per-task dialog pool): done, it was a real binding bug.** Commit `8cd4eea`. v31 stores
  one dialog file per quest as `QuestDialog_{huntingZoneId}_{questIndex}.xml`, where both halves come
  from the quest header `Quest번호 = "{zone},{index}"`. The resolver was passing the *text-id
  reference* as the chain id, so quest 1301 (`Quest번호 13,1`) read its intro from
  `QuestDialog_13_2.xml` and its task dialog from `QuestDialog_13_3.xml`. Because every quest uses
  small ref numbers, they all landed in the same handful of files, which is exactly the "same ~10
  recurring IoD NPCs repeated across every quest" symptom. It also explains the "text 100
  (not found)" sentinel from the 2026-07-17 report item 14: there is no `QuestDialog_13_100.xml`.
  Now fixed to open the quest's own file and index Text nodes inside it. Quest 1301 intro is Axelle's
  text 2 and its task dialog is Lam's text 3; quest 1303's five tasks bind to Nivek, Neziir and Adria
  in their authored order instead of a shared pool. v92 (one file per quest) is unaffected.
- **Item 5 (task types): done.** Task types are now surfaced in three places, each pairing the
  Korean element value with an English name (all 34 v92 types mapped, covering the 25 in v31):
  `lookup_quest` per task (`id|type|typeKo|target|nextTask|failReturnTask|isRewardTask`),
  `search_quests` as a per-quest `taskTypes` summary column, and `lookup_quest_rewards` as a
  `taskTypes:` line so reward values can be calibrated against the actual objective. Quest category
  is now translated too. Example: quest 1313 reads
  `Collect x1, GroupHunt x1, Hunt x1, MoveToPC x1, Visit x1` instead of requiring a title guess.

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
