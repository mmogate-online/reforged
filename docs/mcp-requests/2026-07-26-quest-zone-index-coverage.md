# Datasheet MCP: the quest zone index misses givers and delivery targets (2026-07-26)

Filed from a live-diagnostics session that had to enumerate every Island of Dawn quest.
Companion to `2026-07-26-reward-and-loot-table-enumeration.md`, which covers the reward and
loot half of the same sweep; nothing here repeats an item from that file.

Probed against `datasheet-v92`, server datasheet tree `D:\dev\mmogate\tera92\server\Datasheet`
(working tree mid patch 002, `QuestData` newest write `2026-07-25T21:21:41Z`).

Note on the companion request: reading `datasheet-mcp` at `ee1fe2b`, every item in the
2026-07-26 reward and loot request already has a commit upstream (`6ca1c7e` continent loot
fan-out, `8677a4f` audit_zone_rewards plus inline item names, `8c02036` child attributes in
search and batch_lookup, `ff61b5a` child count grouped by parent, `6344a19` describe_entity
huntingZoneId, `ca67a5f` nested child rendering, `485f2e9` gold conversion and scan_zones
docs). Our binary is still the older build, so none of that is verified from this end yet.
This file is only about what those commits do not touch.

## 1. BUG (blocker): `search_quests(huntingZoneId)` omits ~10% of the corpus

The zone index is built from two element names only:

```csharp
// src/DatasheetMcp/Services/QuestDataService.cs:35
private static readonly string[] QuestZoneRefElements = ["NPCId", "몬스터Id"];
```

A quest is therefore indexed under a zone only if it has a visit or talk target (`NPCId`) or a
kill target (`몬스터Id`). Two other elements carry a `huntingZoneId,templateId` NPC reference
and are not read:

| Element | Meaning | Refs in corpus | Quests | Indexed |
|---|---|---|---|---|
| `NPCId` | visit / talk target | 3437 | 1757 | YES |
| `몬스터Id` | kill target | 4756 | 1898 | YES |
| **`NPC대화`** | **the giver, in `Header/발생조건`** | **1866** | **1866** | **no** |
| **`대상NPC지정`** | **task target NPC (Collect, DeliverItem, DeliverInjectedItem)** | **1821** | **1362** | **no** |

Consequence: a quest whose only NPC references are its giver and its delivery target is
indexed under no zone at all and cannot be found by any zone query.

**268 of 2710 quests (9.9%) are invisible to `search_quests(huntingZoneId)`.**

Reproducer on Island of Dawn, where exactly 10 live quests are affected:

```
search_quests(huntingZoneId=64)
  -> 19 quests. 1353 is absent.

lookup_quest(1353)
  -> Quest 1353: A Fiber of Their Being
     state: live
     [Trigger] npcDialog=Berlon (64,1011)
     [Tasks] 1, types: Collect x1   target: Berlon (64,1011)
```

Both references in 1353 point at zone 64, and the quest is still missing from the zone-64
result. The whole authored Berlon crafting chain (1353 to 1358) disappears this way, along
with 1334, 1336, 1341 and 1343.

Contrast, same zone, same NPCs: 1338 (`Visit x1`) and 1335 (`Visit x2`) are both returned.
Every quest present in a zone result has at least one Visit or Hunt-family task; every absent
one has none. Verified by scanning the corpus for which elements carry a `zone,template`
reference (script in the session temp folder, `scan_quest_refs.py` and `scan_invisible.py`).

Expected: the giver and the task target NPC both associate a quest with their zone. Actual:
neither does, silently. This is the same failure class the commit that added `몬스터Id`
already fixed once (`aa367fb`, "kill-target quest indexing"): the fix extended the element
list rather than deriving it, so the next reference element repeated the bug.

Suggested fix: add `NPC대화` and `대상NPC지정` to `QuestZoneRefElements`. Worth considering
whether the index should instead walk every descendant whose text matches
`^\d+,\d+$` and is not a known quest reference (`Quest번호`, `연결퀘스트`, `퀘스트Id`,
`진행퀘스트`), so a future task type does not silently drop out again. `목표지역` (524 refs,
196 quests), `테리토리진입` (26) and `분기목표지역` (8) are also unread and may belong,
though those are region rather than NPC references and we did not need them.

Impact beyond `search_quests`: `GetQuestsByZone` also backs `audit_quest_gates` and
`profile_npc`'s quest-link section, so a blocked delivery-only quest is invisible to the gate
audit too, and an NPC that only ever gives or receives quests shows no quest links.

## 2. GAP: `search_quests` omits the columns a zone roster actually needs

The row is `id, title, category, categoryKo, level, storyGroup, connectedTo, enabled,
taskTypes`. Missing, and needed for any quest table or reset plan:

- **giver** (`Header/발생조건/NPC대화`), already parsed and rendered by `lookup_quest`
- **prerequisites** (`선행퀘스트`), already indexed (`GetPrerequisites`)
- **minLevel / maxLevel** (`수행조건/최소레벨`, `최대레벨`)

`level` in the current output is `적정수행레벨` (recommendedLevel), which is not the gating
value and is not labelled as such. `maxLevel` matters disproportionately: a quest past its cap
is withheld with no marker and no greyed entry, which in game is indistinguishable from a
broken enable, and it appears in no bulk view at all.

Building a 74-row IoD table cost 7 `search_quests` calls plus ~15 `lookup_quest` calls purely
to recover giver, prerequisite and level-band columns. Adding them to the existing row would
make it one call per zone. This is the quest-side twin of the bulk-reward request in the
companion file, and `audit_zone_rewards` from `8677a4f` is the shape to copy.

## 3. `enabled` in `search_quests` means "carries no sentinel", not "reachable"

Quests 21302 to 21307 all report `enabled=Y`. They are unreachable: the chain head 21301
carries the sentinel and nothing else unlocks them. The footnote explains the sentinel rule
correctly but the column still reads as availability.

This bit during a scope check: the IoD divergence log records "21301-21307 sentinel-disabled
via chain head 21301", and the zone query appears to contradict it. It also hid a real finding
for a while, that 21311 and 21312 exist as a second chain (21311 disabled, 21312 live behind
21307) and were never accounted for in that log.

Request: either rename the column to something like `sentinel` / `notDisabled`, or add a
`reachable` column that walks the prerequisite chain to a root, since `GetPrerequisites` is
already indexed. A reachability walk would also answer "what does disabling this head actually
switch off", which is a routine question during a restoration.

## 4. GAP: no continent form on `search_quests` or `audit_quest_gates`

Island of Dawn is five layered hunting zones plus two dungeon zones. Both tools take
`huntingZoneId` only, so a regional answer is 7 calls and a manual union, with the
deduplication left to the caller (many quests legitimately appear in three of them).

`audit_zone_loot`, `audit_zone_gathering` and `audit_continent_merchants` already take
`continentId`. Request the same on these two. The zone-set-per-continent resolution already
exists for those tools.

## 5. Minor

- `lookup_quest` on a nonexistent id returns an exemplary message ("Quest ids are sparse; use
  find_free_ids with entityType Quest to see which ranges are unused"). No change wanted, noted
  as the pattern the tools in item 1 should follow when a zone query comes back thin.
- `search_quests` describes itself as "find all quests with NPCs in a given zone", which is
  precisely the promise item 1 breaks. Whatever the fix, the description should say which
  reference kinds are covered.
