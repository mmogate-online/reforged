# Quest Reward Ledger: Island of Dawn, Quest IDs 1371 to 1390

Source: datasheet-v92 (current server state), MCP tools `lookup_quest`, `lookup_quest_rewards`, `batch_lookup`/`lookup` (entityType Item), plus direct read of the underlying `.quest` XML files under `QuestData/` for the class gate detail (the `lookup_quest` tool summarizes a class gate as `class=적용` without naming the class).

## Section 1: Quest Summary

| id | title | category | level | storyGroup | enabled | classGate | giver | prerequisites | exp | gold | reward item count |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1371 | Warrior Training | Mission | min 2 | 1 | live | Warrior | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1372 | Lancer Training | Mission | min 2 | 1 | live | Lancer | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1373 | Slayer Training | Mission | min 2 | 1 | live | Slayer | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1374 | Berserker Training | Mission | min 2 | 1 | live | Berserker | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1375 | Archer Training | Mission | min 2 | 1 | live | Archer | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1376 | Sorcerer Training | Mission | min 2 | 1 | live | Sorcerer | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1377 | Priest Training | Mission | min 2 | 1 | live | Priest | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1378 | Mystic Training | Mission | min 2 | 1 | live | Elementalist (Mystic) | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1379 | Gunner Training | Mission | min 2 | 1 | live | Engineer (Gunner) | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1380 | Ninja Training | Mission | min 2 | 1 | live | Assassin (Ninja) | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1381 | Brawler Training | Mission | min 2 | 1 | live | Fighter (Brawler) | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1382 | Gathering Your Strength | Mission | min 5 | 1 | live | Warrior, Lancer, Slayer, Berserker, Archer, Engineer (Gunner), Assassin (Ninja), Fighter (Brawler), Glaiver (Valkyrie) (9 classes) | Milene (64,1049) | 1384 (Getting to Know the Garrison) | 100 | none | 0 |
| 1383 | Gathering Your Strength | Mission | min 5 | 1 | live | Sorcerer, Priest, Elementalist (Mystic) (3 classes) | Milene (64,1049) | 1384 (Getting to Know the Garrison) | 100 | none | 0 |
| 1384 | Getting to Know the Garrison | Mission | min 4 | 1 | live | none | Kiriya (64,1029) | 1329 (Going Above and Beyond) | 900 | 80 | 2 |
| 1385 | Always After Me Lucky Charms | Normal | min 3 | none | disabled (sentinel prerequisite 99,99) | none | Milene (64,1049) | 9999 (Unavailable Quest, sentinel) | 50 | none | 0 |
| 1386 | Bombs Away | Normal | min 4 | none | live | none | Jorhon (64,1006) | 1329 (Going Above and Beyond) | 300 | none | 1 |
| 1387 | Valkyrie Training | Mission | min 2 | 1 | live | Glaiver (Valkyrie) | Dulari (213,1017) | 1304 (Making the Rounds) | 2100 | 150 | 0 |
| 1388 | (no quest, see Section 4) | | | | | | | | | | |
| 1389 | Emptying Pandora's Box | Normal | min 5 | none | disabled (sentinel prerequisite 99,99) | none | Priscus (213,1020) | 9999 (Unavailable Quest, sentinel) | 200 | none | 0 |
| 1390 | Special Delivery | Normal | min 6, max 12 | none | live | none | Fili (213,1141) | none | 300 | none | 1 |

## Section 2: Per-Quest Detail

### 1371, Warrior Training

Class gate: Warrior (from `<클래스><Warrior>적용</Warrior></클래스>` in QuestData/001371.quest)

Ordered tasks:
1. Visit: Junia (213,1023)
2. Condition: acquire combat skill, skill id 180100
3. Visit: Junia (213,1023)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

### 1372, Lancer Training

Class gate: Lancer

Ordered tasks:
1. Visit: Junia (213,1023)
2. Condition: acquire combat skill, skill id 180100
3. Visit: Junia (213,1023)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

### 1373, Slayer Training

Class gate: Slayer

Ordered tasks:
1. Visit: Junia (213,1023)
2. Condition: acquire combat skill, skill id 120100
3. Visit: Junia (213,1023)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

### 1374, Berserker Training

Class gate: Berserker

Ordered tasks:
1. Visit: Junia (213,1023)
2. Condition: acquire combat skill, skill id 30100
3. Visit: Junia (213,1023)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

### 1375, Archer Training

Class gate: Archer

Ordered tasks:
1. Visit: Junia (213,1023)
2. Condition: acquire combat skill, skill id 30100
3. Visit: Junia (213,1023)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

Note: skill id 30100 is recorded identically for both Berserker Training (1374) and Archer Training (1375).

### 1376, Sorcerer Training

Class gate: Sorcerer

Ordered tasks:
1. Visit: Volis (213,1024)
2. Condition: acquire combat skill, skill id 70100
3. Visit: Volis (213,1024)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

### 1377, Priest Training

Class gate: Priest

Ordered tasks:
1. Visit: Volis (213,1024)
2. Condition: acquire combat skill, skill id 110100
3. Visit: Volis (213,1024)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

### 1378, Mystic Training

Class gate: Elementalist (internal identifier; game name Mystic)

Ordered tasks:
1. Visit: Volis (213,1024)
2. Condition: acquire combat skill, skill id 80100
3. Visit: Volis (213,1024)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

### 1379, Gunner Training

Class gate: Engineer (internal identifier; game name Gunner)

Ordered tasks:
1. Visit: Junia (213,1023)
2. Condition: acquire combat skill, skill id 70100
3. Visit: Junia (213,1023)
4. Visit: Dulari (213,1017)
5. HuntAndDeliver: monster 13,300921, deliver count 5, to NPC 213,1115 (Nivek)

Reward items: none (exp 2100, gold 150)

Note: skill id 70100 is recorded identically for both Sorcerer Training (1376) and Gunner Training (1379).

### 1380, Ninja Training

Class gate: Assassin (internal identifier; game name Ninja)

Ordered tasks:
1. Visit: Junia (213,1023)
2. Hunt: monster 13,300921, kill count 5
3. Visit: Nivek (213,1115)

Reward items: none (exp 2100, gold 150)

Note: this quest uses a 3-task Visit/Hunt/Visit structure, unlike the 5-task Visit/Condition/Visit/Visit/HuntAndDeliver structure used by 1371 to 1379. There is no skill-acquisition Condition task.

### 1381, Brawler Training

Class gate: Fighter (internal identifier; game name Brawler)

Ordered tasks:
1. Visit: Junia (213,1023)
2. Hunt: monster 13,300921, kill count 5
3. Visit: Nivek (213,1115)

Reward items: none (exp 2100, gold 150)

Note: same 3-task structure as 1380 and 1387.

### 1382, Gathering Your Strength (physical classes)

Class gate: Warrior, Lancer, Slayer, Berserker, Archer, Engineer (Gunner), Assassin (Ninja), Fighter (Brawler), Glaiver (Valkyrie), 9 classes (from QuestData/001382.quest)

Ordered tasks:
1. Visit: Gurney (64,1007)
2. Visit: Lilni (64,1048)
3. Collect: collection id 496, deliver item 9100, deliver count 2, to NPC 64,1048 (Lilni)

Reward items: none (exp 100, no gold)

### 1383, Gathering Your Strength (caster classes)

Class gate: Sorcerer, Priest, Elementalist (Mystic), 3 classes (from QuestData/001383.quest)

Ordered tasks:
1. Visit: Charise (64,1008)
2. Visit: Lilni (64,1048)
3. Collect: collection id 496, deliver item 9100, deliver count 2, to NPC 64,1048 (Lilni)

Reward items: none (exp 100, no gold)

Note: 1382 and 1383 are the same title ("Gathering Your Strength") and the same task shape (Visit, Visit, Collect of the same collection id 9100/496), differing only in the giver dialog NPC (Gurney vs Charise), the class gate, and (per task instructions) confirmed identical exp/gold (100/none).

### 1384, Getting to Know the Garrison

Class gate: none

Ordered tasks (as returned, id/next chain forms two branches into task 5):
1. Visit: Rutgar (64,1005), next task 2
2. Visit: Milene (64,1049), inserts item 98 x1 and item 70033 x1 on completion, next task 5
5. Condition: use item 70033, count 1, next task 6
6. Visit: Milene (64,1049), completes quest
3. Condition: use item 98, count 1, next task 4
4. Visit: Milene (64,1049), inserts item 70033 x1 on completion, next task 5

Reward items:
- 6048, qty 3, class none
- 7100, qty 2, class none

itemBag: allpay (root-scoped). exp 900, gold 80.

### 1385, Always After Me Lucky Charms

State: disabled (sentinel prerequisite 99,99); prerequisite quest 9999 (Unavailable Quest)

Class gate: none

Start items: item 7100, qty 1

Ordered tasks:
1. Condition: use item 7100, count 1
2. Visit: Milene (64,1049)

Reward items: none (exp 50, no gold)

### 1386, Bombs Away

Class gate: none

Ordered tasks:
1. Visit: Kiriya (64,1029), inserts item 5002 x1 on completion
2. Hunt: monster 13,888, kill count 3
3. Visit: Kiriya (64,1029), removes item 5002 x1 on completion
4. Visit: Jorhon (64,1006)

Reward items:
- 7200, qty 10, class none

itemBag: allpay (root-scoped). exp 300, no gold.

### 1387, Valkyrie Training

Class gate: Glaiver (internal identifier; game name Valkyrie)

Ordered tasks:
1. Visit: Junia (213,1023)
2. Hunt: monster 13,300921, kill count 5
3. Visit: Nivek (213,1115)

Reward items: none (exp 2100, gold 150)

Note: same 3-task structure as 1380 and 1381.

### 1388

No quest header exists (`lookup_quest` returns not found; no `QuestData/001388.quest` file on disk). See Section 4.

### 1389, Emptying Pandora's Box

State: disabled (sentinel prerequisite 99,99); prerequisite quest 9999 (Unavailable Quest)

Class gate: none

Start items: item 100, qty 1

Ordered tasks:
1. Visit: Priscus (213,1020), inserts item 1002 x1 on completion
2. Condition: no completion-condition child element recorded in the task body (journal text and success message only)
3. Visit: Priscus (213,1020)

Reward items: none (exp 200, no gold)

### 1390, Special Delivery

Class gate: none

Start items: item 160, qty 1

Ordered tasks:
1. Condition: use item 160, count 1
2. Visit: Tainted Gorge Teleportal (64,1050)
3. DeliverInjectedItem: deliver count 10, to NPC 213,1141 (Fili)

Reward items:
- 160, qty 2, class none

itemBag: allpay (root-scoped). exp 300, no gold.

## Section 3: Item Name Lookup

| templateId | name | level | grade/rarity | type |
|---|---|---|---|---|
| 160 | Safe Haven Teleport Scroll | 1 | rareGrade 0 | magical (combatItemType DISPOSAL) |
| 6048 | Healing Elixir I | 1 | rareGrade 0 | combat (combatItemType DISPOSAL) |
| 7100 | Onslaught Charm I | 1 | rareGrade 0 | charm (combatItemType DISPOSAL) |
| 7200 | Bomb I | 1 | rareGrade 0 | combat (combatItemType DISPOSAL) |

## Section 4: Missing IDs

- 1388: no quest header found in the range. `lookup_quest(questId=1388)` returns not found, and there is no `QuestData/001388.quest` file in the server datasheet tree. `lookup_quest_rewards(questId=1388)` reports the quest "is registered but defines no compensation (empty reward stub)", meaning a QuestCompensation entry exists at id 1388 with no header and no reward children.
