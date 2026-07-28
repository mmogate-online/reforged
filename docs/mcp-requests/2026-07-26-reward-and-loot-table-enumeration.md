# Datasheet MCP: enumerating quest rewards and loot tables for a whole region (2026-07-26)

Context: building the IoD reward and loot balance tables (every quest with its tasks, sequence and
payout; every mob loot table in the region). Probed against `datasheet-v92`, server datasheet tree
`D:\dev\mmogate\tera92\server\Datasheet` (working tree mid patch 002).

Most of this works well. `audit_zone_loot` at zone scope in particular answers the loot half of the
question in a single call and needs no change. The items below are what blocked or slowed the sweep,
ordered by impact.

## 1. BUG (blocker): `audit_zone_loot(continentId=...)` finds no loot on any continent

The tool description advertises the continent form as a multi-HZ fan-out. It reports the correct
hunting zone count and then finds nothing.

Reproducer A (IoD, 5 layered HZs):

```
audit_zone_loot(continentId=13, npcTemplateIds="[1004]")
  -> continent 13: loot across 5 hunting zone(s)
     No loot tables found in any hunting zone of this continent.

audit_zone_loot(huntingZoneId=13, npcTemplateIds="[1004]")
  -> Zone 13 -- 57 NPCs, 1 with loot, 1 unique loot tables, filter=1 NPCs
     [LT-1] (1 NPC: Kugai) ... full table, 24 bags including gold, designs and Kugai token bags
```

Reproducer B (single-HZ continent, so layering is not the variable):

```
audit_zone_loot(continentId=9037, npcTemplateIds="[1001]")
  -> continent 9037: loot across 1 hunting zone(s)
     No loot tables found in any hunting zone of this continent.

audit_zone_loot(huntingZoneId=437)
  -> Zone 437 -- 59 NPCs, 31 with loot, 15 unique loot tables   (Sorcha 1001 = LT-1)
```

Both continents have loot that the zone form returns. Corroborating counts on continent 13:
`count(ECompensation, huntingZoneId=13)` = 57 and `count(CCompensation, huntingZoneId=13)` = 50.

Expected: the continent form returns the union of its hunting zones, deduplicated the same way the
zone form is. Actual: an empty result with no error, which reads as a finding ("this region drops
nothing") rather than as a failure. Note continent 9037 maps to hunting zone 437, so the fan-out may
be resolving continent id to hunting zone id incorrectly rather than failing to read the files.

## 2. GAP: no bulk quest reward retrieval

`lookup_quest_rewards(questId)` and `lookup(QuestCompensation, huntingZoneId, questId)` both return a
complete payload (exp, gold, itemBag mode, per-item rows with class/gender/race), but one quest at a
time. Continent 13 has 84 quest compensation entries, so a regional reward table costs 84 calls plus
the name joins in item 5 below. This is the single largest cost in the sweep and is why the ledgers
in `docs/plans/classic-restoration/iod/data/quest-ledger-*.md` had to be built by hand.

Request, cheapest useful form first:

1. `lookup_quest_rewards` accepts a list of quest ids (mirroring `batch_lookup`), or
2. a zone-scoped `audit_zone_rewards(huntingZoneId)` shaped like `audit_zone_loot`: one row per
   quest with exp, gold, itemBag mode and item rows, deduplicating identical reward blocks (the 12
   class training quests 1371 to 1381 and 1387 all pay 2100/150, so dedup would be effective).

Either form should resolve item display names, per item 5.

## 3. `search` silently returns blank columns for child attributes, while `filters` errors helpfully

The filter path is exemplary:

```
search(QuestCompensation, huntingZoneId=13, filters={"exp": "1000..99999"})
  -> Filter 'exp' is not an attribute of <Quest>; it is an attribute of its child element
     <Compensation/CompensationType>. Filters match root attributes only.
     Use count with childElement=CompensationType groupBy=exp to query child attributes.
```

The projection path for the same attributes does not:

```
search(QuestCompensation, huntingZoneId=13, filters={"questId": "1301..1310"},
       attributes=["questId","exp","gold","itemBag","type"])
  -> questId|exp|gold|itemBag|type
     1301||||
     1302||||     (10 rows, every requested child column empty)
```

Request: apply the same diagnostic to `attributes` as to `filters`. An empty column is
indistinguishable from a real empty value, so this silently produces a reward table full of blanks.

## 4. `count` with `childElement` cannot group by the parent key

```
count(QuestCompensation, huntingZoneId=13, childElement="Item", groupBy="questId")
  -> Total: 283
     Count by questId:
       (none): 283
```

The total is right and useful (283 reward item rows in the zone), but every row falls into `(none)`,
so reward item counts cannot be attributed to quests. Grouping by an attribute of the parent entity
while aggregating a child element would turn this into a usable per-quest histogram.

Working counterexample, for contrast: `groupBy` on an attribute of the child element itself is
correct and was the one bulk numeric view available for balance work.

```
count(QuestCompensation, huntingZoneId=13, childElement="CompensationType", groupBy="exp")
  -> Total: 74;  2100: 12,  800: 9,  500: 5,  900: 5, ... 14600: 1
```

## 5. Quest reward items carry no display name, and `batch_lookup(Item)` returns internal names

Quest reward rows give `templateId` only. `batch_lookup(Item, ...)` resolves to the internal name,
not the player-visible one, so a third call is needed:

```
batch_lookup(Item, ids=[15019,10017,82007,95216], attributes=["name","level","rareGrade"])
  -> mail17_body | dual_01 | gauntlet_01 | token
batch_lookup(ItemString, ids=[15019,10017,82007,95216])
  -> Hauberk of the First Expedition | Twin Swords of the First Expedition
     | Powerfists of the First Expedition | Kugai's Crest
```

`audit_zone_loot` already resolves display names inline, which is exactly the right behaviour.
Request: do the same in the quest reward tools, or at least document that `Item.name` is the
internal label and `ItemString.string` is the display name (this is the item-side twin of the
`NpcData.name` versus `StrSheet_Creature` divergence that `profile_npc` now warns about).

## 6. `describe_entity` cannot describe any zone-partitioned entity

```
describe_entity(entityType="ECompensation")
  -> totalEntities: 0
     sampleSize: 0
     sampledZoneId: 1 (zone-partitioned - pass huntingZoneId to describe_entity for a specific zone)
     Attributes (presence% | distinct | range/values):
     (empty)
```

The output instructs the caller to pass `huntingZoneId`, but the tool schema declares no such
parameter, so there is no way to comply. Same for `QuestCompensation`, `CCompensation` and every
other `zoneRequired=Yes` type. The result is that structure discovery, the documented first step of
the discovery pattern, is unavailable for exactly the entities this work needed. Request: add the
`huntingZoneId` parameter the message already refers to, and default to the first zone that has data
rather than zone 1 when it is omitted.

## 7. Output format: generic `lookup` flattens repeated child groups, losing the association

```
lookup(CCompensation, huntingZoneId=13, id=1004)
  [ClassItemBag]  class: Warrior / Lancer / Slayer / Berserker / Sorcerer / Archer
  [ClassBag]      probability: 0.1144  (x6)
  [ClassItem]     templateId: 8000 ... 8005 ...  (12 rows)
```

The XML nests bag inside class and item inside bag, but the render is three flat lists, so which
class gets which bag and which items is not recoverable from the output. With uniform values it is
merely awkward; with per-class differences it would be wrong. `audit_zone_loot` renders the same data
correctly (`Class/only: Warrior,Lancer,... bag=0.1144` followed by its items), so this is a
generic-lookup rendering issue only. Prefer the audit tool for loot; the request is that `lookup`
preserve nesting for repeated child groups.

## 8. Minor

- `scan_zones` works on `ECompensation` (14 zones returned for `npcTemplateId=1004`, with npcName
  resolved), but its description names only `NpcTemplate` and `CCompensation`. Documentation fix.
- The gold bag conversion annotation renders unresolved:
  `Everyone/gold "골드" prob=0.7 min=16 max=171.2 (=16c..?)` in `audit_zone_loot(huntingZoneId=13)`.
  The legend promises `(=Ng Ms Nc)`.

## Not a request, recorded because it was found during this sweep

`audit_zone_gathering(continentId=13)` works at continent scope, is rich, and flagged real content
drift: an `ORPHAN_FILE` (`13_ATW_P`) duplicating all five IoD quest collections, and `SPAWN_DRIFT`
on collections 409, 410 and 411 (declared spawn counts 15/15/25 against actual 20/24/30). That is
content work for this project, not an MCP defect.
