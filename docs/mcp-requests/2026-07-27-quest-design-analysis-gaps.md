# Datasheet MCP: quest-design analysis gaps (2026-07-27)

Filed after a full session of Island of Dawn quest trimming and reward redistribution
(patch 002 specs 27 to 31, all live-validated). Every item below is a question the session
actually had to answer, and had to answer with a hand-written Python sweep because no MCP tool
covers it. Grouped by theme; the first item is the only outright bug.

Probed against `datasheet-v92` and `datasheet-v31`, server tree
`D:\dev\mmogate\tera92\server\Datasheet` (working tree mid patch 002).

Companion to `2026-07-26-quest-zone-index-coverage.md` and
`2026-07-26-reward-and-loot-table-enumeration.md`. Nothing here repeats an item from either.

---

## 1. BUG: the in-progress gate `진행퀘스트` is invisible to every quest tool

`수행조건/진행퀘스트` gates a quest behind another quest being **actively in progress**. It is
reported by nothing:

| Tool | Quest 1326, which carries `<진행퀘스트>1305,1</진행퀘스트>` |
|---|---|
| `search_quests(huntingZoneId=64)` | `prerequisites` column empty |
| `audit_quest_chain(1326)` | no prerequisite line, no gate line at all |
| `search_quests` `reachable` | `Y` |

Reproduction: `audit_quest_chain(1326)` and `audit_quest_chain(1330)`, then compare against the
raw header of `QuestData/001326.quest`.

**Why it matters.** These two quests carry two pieces of a four-piece armour set. Because the
gate only opens while story quest 1305 is active, a player who completes 1305 first can never
obtain them, and the set stops being completable. The session found this only by parsing raw
headers; every MCP surface said the quests were freely available. 37 quests corpus-wide carry
the element, so this is small but load-bearing.

Asks:
- Surface the gate in `audit_quest_chain` and as a column in `search_quests`.
- Fold it into `reachable`: a quest whose in-progress gate references an unreachable or
  already-completable-and-gone quest is not reachable in the ordinary sense. At minimum flag it
  as a distinct state, e.g. `reachable=WINDOW`, because "obtainable only during another quest"
  is a different player-facing fact from "obtainable".

---

## 2. GAP: there is no reverse-reference query

`trace_quest_sequence` walks one quest's prerequisite tree backward. There is no way to ask
**"what would break if this quest went away"**, which is the central question of any trimming
pass.

The session needed inbound edges of five distinct kinds, and only the first is covered at all:

| Reference class | Where it lives | Covered? |
|---|---|---|
| `선행퀘스트` prerequisite | quest header | partially, via trace_quest_sequence |
| `진행퀘스트` in-progress gate | quest header | no, see item 1 |
| `연결퀘스트` successor auto-offer | quest header | shown outbound only, never inbound |
| Dungeon entry conditions | `DungeonData_*` `progressQuest` / `completeQuest` | no |
| WorkObject window | `WorkObjectData` `isForQuestId` | no |
| NPC appear/hide gate | `NpcData` `appearQuestId` / `hideQuestId` | no |
| Area access gate | `AreaData` `requireQuestId` | no |
| Achievement completion check | `AchievementList` | no |

A further trap: the two encodings differ. Quest headers use the **pair form** `13,46`, while
every non-quest family uses the **global id** `1346`. Any sweep must match both, which is easy
to get wrong by hand.

Ask: `quest_references(questId)` returning inbound edges across all of the above, with the
encoding handled internally.

---

## 3. GAP: `audit_quest_gates` passes objectives that are not realistically completable

The tool answers "does at least one spawn of each target exist". It does not answer "are there
enough of them".

Quest 1348 requires **8** collected items. At its spot there are **10** valid targets: six of
template 302 at a 90% grant rate and four of template 303 at **17%**. Expected yield for a full
clear of every mob in the area is about 6.1 items against a requirement of 8, on a 20-second
respawn. `audit_quest_gates` reports it `OK`. Live testers reported it as the worst quest in the
zone, which it was.

Ask: extend the gate to compare the objective's **required count** against the **available
credit population**, using per-entry `수여확률` and `사냥마리수` and the spawn counts already in
`audit_zone_spawns`. A column of expected-yield-per-clear versus required would have caught this
without anyone playing the quest.

---

## 4. GAP: no reward comparison, so duplicate rewards are invisible

Three separate duplications, each found by eye across multiple `lookup_quest_rewards` calls:

- **1304 and 1323** granted the *identical* 12-row class weapon bag at the identical
  800 exp / 80 gold. The second copy was always vendor fodder. (Authentic v31 data, confirmed
  against `datasheet-v31`.)
- **1305** granted the entire level-7 First Expedition set, and **1326** and **1330** then
  granted duplicates of its feet and hands.
- **1315** granted the 12 Kugai weapons plus the level-8 chest, which is the whole weapons tab
  and chest row of the Kugai token shop, purchasable with a token that drops from the same
  boss the quest is about.

Asks:
- `compare_quest_rewards(questIdA, questIdB)`.
- Better: a zone-scoped duplicate detector, "which reward items are granted by more than one
  source in this zone", where source includes **shops** (`BuyList` / `ItemMedalExchange`), not
  just quests. The 1315 case is only visible if shops are in scope.

---

## 5. GAP: no "who grants this item" lookup

To decide where a set piece could be placed, the session had to know whether it was already
granted anywhere. That meant a Python sweep of all 156 `QuestCompensationData` files. The answer
mattered: six of the nine level-4 set pieces and all three level-3 body pieces were granted by
**no quest in the entire corpus**, which is what made them free to use.

Ask: `item_sources(itemId)` returning quest compensations, ECompensation drop tables, shop
lists and medal exchanges that grant or sell it.

---

## 6. GAP: no gear-set or visual-tier awareness

"Can a player complete a full set look at this tier" is a first-class design question here, and
answering it required deriving the encoding by hand. For the record, since it is stable and
useful:

`linkLookInfoId` decodes as `{armourType}{slot}{tier}` where armour type is 3 = mail,
2 = leather, 4 = robe, and slot is 11 = body, 12 = hands, 13 = feet. So the level-3 set is look
tier `003`, the level-4 set `005`, Family Ties/Rockhound/Nivek's `006`, First Expedition `007`.

`find_similar_items` matches on `itemLevelId`, which is the wrong axis: for item 17703 it
returned 77 items spanning levels 1 to 60, all "ilvl17 feet" across unrelated sets, not the
eight siblings of its actual set.

Asks:
- `gear_set(itemId)` returning the slot x armour-type grid for that visual tier, with each
  cell's grant source (which pairs with item 5).
- Expose `linkLookInfoId` as a `matchBy` axis on `find_similar_items`.

---

## 7. GAP: no per-class reward ladder

The single most damaging defect of the session: Brawler and Ninja received the **same level-2
weapon from all three weapon quests in the zone** (1304, 1319, 1303) and never a mid-tier
upgrade, while Valkyrie received the same level-3 glaive twice. The cause was a generator pool
that skipped levels 3 to 6 because those classes' mid-tier weapons live in separate id ranges
(`823xx`, `583xx`/`585xx`, `593xx`) instead of continuing the base line. The same defect also
sat on quests 1315 and 1316.

Every reward tool presents rewards **per quest**. Nothing presents them **per class across
quests**, which is the view in which "this class gets the same item three times" is obvious at a
glance.

Ask: `class_reward_ladder(huntingZoneId | continentId)` returning, per class, the ordered list
of equipment granted across the zone's quests with each item's level, so a flat or regressing
ladder is visible immediately. This is the check that would have caught a defect that shipped,
survived a source diff, and needed live testing to notice.

---

## 8. GAP: no spatial reasoning between quest elements

Reward placement was ultimately decided on travel distance, and every number had to be computed
by hand from `audit_zone_spawns` coordinates plus a Tower Base reference point taken out of an
`AreaData` recall attribute:

- giver to objective, objective to turn-in, and turn-in back to the hub;
- and the fact that two quests **chain** (one ends where the next begins), which turned a
  46,380-unit pair of round trips into a single 27,018-unit run.

`resolve_position` and `audit_zone_spawns` provide the raw material, so this is composition
rather than new data.

Asks:
- `quest_geometry(questId)`: per task, the giver position, the objective centroid and nearest
  member, the turn-in position, and the distances between them, plus the containing AreaData
  section names for each.
- Optionally a zone-scoped variant so quests can be ranked by travel cost, which is exactly how
  this session chose carriers.

---

## 9. Smaller items

- **Environment-mob classification is not surfaced.** Template 13,102 is
  `(환경몬스터)자연의 정령`, `playStyle=creature`, `aiid=108`, an ambient variant of the same
  model as the combat templates. Deciding whether it was a legitimate kill target needed a
  corpus sweep (result: 3 of 3,785 hunt-target references are `playStyle=creature`). A flag on
  `profile_npc`, plus the ability to filter `audit_zone_spawns` by `playStyle`, would make this
  a query.
- **`audit_quest_chain` does not show the reward flag or the turn-in NPC per task.** Both are in
  the task body and both matter for sequencing (`보상=1` says which task pays; `대상NPC지정`
  says where the player ends up, which is not the giver).
- **No spawn-level AI override in `audit_zone_spawns`.** The `ai` attribute on a spawn overrides
  the template's `aiid`, and a retarget that leaves it stale makes one template behave two ways
  at adjacent points. The session hit exactly this and had to read raw XML to catch it.

---

## What already works well, for calibration

Worth saying, because these carried most of the session:

- `search_quests` `reachable` versus `enabled` is exactly the right distinction and made the
  trim verification a one-call check.
- `audit_zone_spawns` `posSource=fenceCentroid` is honest about derived coordinates.
- `profile_npc` flagging name-versus-displayName divergence, and listing shape siblings, is what
  made the ambient-versus-combat template split visible at all.
- `resolve_position` returning nested sections broadest-first answered every "where is this"
  question instantly.
