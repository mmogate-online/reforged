# MCP request: expose Achievement, WorkObject, Treasure, CollectionBook, and AreaData/Section families

Date: 2026-07-26
Context: reward-vector planning for IoD (`docs/plans/reward-vectors/IOD-BACKLOG.md`). A research wave over exploration and conditional-visibility mechanics had to fall back to raw XML for every question in these families, because neither datasheet MCP server exposes them.

## Missing entity families (both servers, v92 priority)

1. **AchievementList** (+ publisher overlays, AchievementCategoryInfo, AchievementGradeInfo, Passivity_Achievement): 1,734 achievements with condition triggers (`Condition type/templateId/value1..6`) and rewards (TitleReward/ItemReward/MoneyReward/AbilityReward). Wanted: lookup by id, search by condition templateId (e.g. all 4209 territory-discovery achievements), reverse lookup from a territory/quest/item to the achievements referencing it.
2. **WorkObjectData + WorkObjectTerritory_{hz}**: 310 object templates (quest windows `isForQuestId`/`firstTaskId`/`lastTaskId`, `keyItemId`, `Work` outcome lists) and their per-zone placements. Wanted: lookup, per-zone placement listing, reverse lookup from quest id to gated objects.
3. **Treasure (TreasurehuntData)**: single dormant prototype; low priority, but list/lookup would document it.
4. **CollectionBook**: card-collection milestones; low priority.
5. **AreaData sections**: `lookup_area` exists, but there is no way to query section-level attributes across zones (e.g. which sections carry a given attribute). Wanted: attribute-level section search, or inclusion of AreaData in `search_text` scope.

## Also observed

- `count` does not accept entity type `Quest` (the family is exposed via lookup_quest/search_quests, but not countable): error "Unknown entity type: Quest". Either alias it or document the supported key.

## Impact

Exploration backlog items (RV-16..22) and any achievement-driven content will query these families constantly; today every question costs a raw-XML scan agent.
