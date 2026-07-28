# Quest Reward Ledger: Quest IDs 1353 to 1370

Scope: quest ids 1353 through 1370 inclusive (18 ids checked against datasheet-v92). 6 quests found (1353 to 1358, the Berlon crafting-intro chain). 12 ids (1359 to 1370) do not exist in the current server datasheet.

## Section 1: Quest Summary Table

| id | title | category | level | storyGroup | enabled | giver | prerequisites | exp | gold | reward item count |
|---|---|---|---|---|---|---|---|---|---|---|
| 1353 | A Fiber of Their Being | Normal | 3 | none | live | Berlon (huntingZone 64, templateId 1011) | 1301 (Dawn's Twilight) | 2300 | 230 | 3 |
| 1354 | An Ounce of Prevention | Normal | 3 | none | live | Berlon (huntingZone 64, templateId 1011) | 1353 (A Fiber of Their Being) | 2300 | 230 | 2 |
| 1355 | Essence of the Matter | Normal | 5 | none | live | Berlon (huntingZone 64, templateId 1011) | 1354 (An Ounce of Prevention) | 3100 | 310 | 3 |
| 1356 | Mana from Heaven | Normal | 5 | none | live | Berlon (huntingZone 64, templateId 1011) | 1355 (Essence of the Matter) | 3100 | 310 | 2 |
| 1357 | The Ore the Merrier | Normal | 7 | none | live | Berlon (huntingZone 64, templateId 1011) | 1356 (Mana from Heaven) | 4000 | 400 | 3 |
| 1358 | Scroll With It | Normal | 7 | none | live | Berlon (huntingZone 64, templateId 1011) | 1357 (The Ore the Merrier) | 4000 | 400 | 2 |

Notes on the table:
- "level" is the recommendedLevel value reported by lookup_quest (no separate min/max fields were present for these quests).
- "storyGroup" is reported as "none" because lookup_quest did not return a storyGroupId value for any of these 6 quests.
- "enabled" reflects the quest's "state" field, which reads "live" for all 6.

## Section 2: Per-Quest Detail

### 1353: A Fiber of Their Being

- category: Normal, recommendedLevel: 3, recommendedPartySize: 1, repeatable: 1-time (1회성), cancellable: yes (가능)
- Trigger: npcDialog with Berlon (huntingZone 64, templateId 1011)
- Requirements: minLevel=3
- Prerequisite quests: 1301 (Dawn's Twilight)
- connectedQuest (chain link to next quest): 1354

Ordered task list:
1. Collect, target: Collection 1 (delivered to Berlon, huntingZone 64, templateId 1011), count: 10x item 1001 (Verdra Fibers)

Reward items:

| templateId | name | qty | class |
|---|---|---|---|
| 91213 | Recipe: Healing Potion I | 1 | (none, root-scoped) |
| 1001 | Verdra Fibers | 10 | (none, root-scoped) |
| 1616 | Apprentice Alchemical Kit | 2 | (none, root-scoped) |

Reward totals: exp 2300, gold 230, itemBag: allpay

### 1354: An Ounce of Prevention

- category: Normal, recommendedLevel: 3, recommendedPartySize: 1, repeatable: 1-time (1회성), cancellable: yes (가능)
- Trigger: npcDialog with Berlon (huntingZone 64, templateId 1011)
- Requirements: minLevel=3
- Prerequisite quests: 1353 (A Fiber of Their Being)
- connectedQuest (chain link to next quest): 1355

Ordered task list:
1. DeliverItem, target: item 6000 (Healing Potion I), delivered to Berlon (huntingZone 64, templateId 1011), count: 5x

Reward items:

| templateId | name | qty | class |
|---|---|---|---|
| 6000 | Healing Potion I | 2 | (none, root-scoped) |
| 1616 | Apprentice Alchemical Kit | 5 | (none, root-scoped) |

Reward totals: exp 2300, gold 230, itemBag: allpay

### 1355: Essence of the Matter

- category: Normal, recommendedLevel: 5, recommendedPartySize: 1, repeatable: 1-time (1회성), cancellable: yes (가능)
- Trigger: npcDialog with Berlon (huntingZone 64, templateId 1011)
- Requirements: minLevel=5
- Prerequisite quests: 1354 (An Ounce of Prevention)
- connectedQuest (chain link to next quest): 1356

Ordered task list:
1. Collect, target: Collection 301 (delivered to Berlon, huntingZone 64, templateId 1011), count: 8x item 1003 (Sun Essence)

Reward items:

| templateId | name | qty | class |
|---|---|---|---|
| 91221 | Recipe: Mana Potion I | 1 | (none, root-scoped) |
| 1003 | Sun Essence | 8 | (none, root-scoped) |
| 1616 | Apprentice Alchemical Kit | 2 | (none, root-scoped) |

Reward totals: exp 3100, gold 310, itemBag: allpay

### 1356: Mana from Heaven

- category: Normal, recommendedLevel: 5, recommendedPartySize: 1, repeatable: 1-time (1회성), cancellable: yes (가능)
- Trigger: npcDialog with Berlon (huntingZone 64, templateId 1011)
- Requirements: minLevel=5
- Prerequisite quests: 1355 (Essence of the Matter)
- connectedQuest (chain link to next quest): 1357

Ordered task list:
1. DeliverItem, target: item 6016 (Mana Potion I), delivered to Berlon (huntingZone 64, templateId 1011), count: 5x

Reward items:

| templateId | name | qty | class |
|---|---|---|---|
| 6016 | Mana Potion I | 2 | (none, root-scoped) |
| 1616 | Apprentice Alchemical Kit | 5 | (none, root-scoped) |

Reward totals: exp 3100, gold 310, itemBag: allpay

### 1357: The Ore the Merrier

- category: Normal, recommendedLevel: 7, recommendedPartySize: 1, repeatable: 1-time (1회성), cancellable: yes (가능)
- Trigger: npcDialog with Berlon (huntingZone 64, templateId 1011)
- Requirements: minLevel=7
- Prerequisite quests: 1356 (Mana from Heaven)
- connectedQuest (chain link to next quest): 1358

Ordered task list:
1. Collect, target: Collection 101 (delivered to Berlon, huntingZone 64, templateId 1011), count: 20x item 1002 (Krymetal Ore)

Reward items:

| templateId | name | qty | class |
|---|---|---|---|
| 91282 | Recipe: Onslaught Scroll: Crit Power I | 1 | (none, root-scoped) |
| 1002 | Krymetal Ore | 20 | (none, root-scoped) |
| 1611 | Apprentice Scroll Kit | 1 | (none, root-scoped) |

Reward totals: exp 4000, gold 400, itemBag: allpay

### 1358: Scroll With It

- category: Normal, recommendedLevel: 7, recommendedPartySize: 1, repeatable: 1-time (1회성), cancellable: yes (가능)
- Trigger: npcDialog with Berlon (huntingZone 64, templateId 1011)
- Requirements: minLevel=7
- Prerequisite quests: 1357 (The Ore the Merrier)
- connectedQuest: none (chain ends here)

Ordered task list:
1. DeliverItem, target: item 6197 (Onslaught Scroll: Crit Power I), delivered to Berlon (huntingZone 64, templateId 1011), count: 2x

Reward items:

| templateId | name | qty | class |
|---|---|---|---|
| 6197 | Onslaught Scroll: Crit Power I | 1 | (none, root-scoped) |
| 1611 | Apprentice Scroll Kit | 5 | (none, root-scoped) |

Reward totals: exp 4000, gold 400, itemBag: allpay

## Section 3: Item Name Lookup Table

All templateIds resolved via batch_lookup (entityType Item).

| templateId | name | level | grade/rarity | type |
|---|---|---|---|---|
| 91213 | Recipe: Healing Potion I | 1 | rareGrade 0 | RECIPE / combatRecipe (category: recipe) |
| 91221 | Recipe: Mana Potion I | 1 | rareGrade 0 | RECIPE / combatRecipe (category: recipe) |
| 91282 | Recipe: Onslaught Scroll: Crit Power I | 1 | rareGrade 0 | RECIPE / combatRecipe (category: recipe) |
| 1001 | Verdra Fibers | 15 | rareGrade 0 | NO_COMBAT / fiber (category: fiber, gathered material) |
| 1002 | Krymetal Ore | 15 | rareGrade 0 | NO_COMBAT / metal (category: metal, gathered material) |
| 1003 | Sun Essence | 15 | rareGrade 0 | NO_COMBAT / alchemy (category: alchemy, gathered material) |
| 1611 | Apprentice Scroll Kit | 1 | rareGrade 0 | NO_COMBAT / generalMaterial (category: generalMaterial, crafting kit) |
| 1616 | Apprentice Alchemical Kit | 1 | rareGrade 0 | NO_COMBAT / generalMaterial (category: generalMaterial, crafting kit) |
| 6000 | Healing Potion I | 1 | rareGrade 0 | DISPOSAL / combat (category: combat, consumable) |
| 6016 | Mana Potion I | 1 | rareGrade 0 | DISPOSAL / combat (category: combat, consumable) |
| 6197 | Onslaught Scroll: Crit Power I | 1 | rareGrade 0 | DISPOSAL / combat (category: combat, consumable) |

## Section 4: Missing Ids

The following ids in the 1353 to 1370 range have no quest in datasheet-v92 (lookup_quest returned "not found"):

1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370
