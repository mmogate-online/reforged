# Datasheet MCP Improvement Requests: Island of Dawn Alpha Research (2026-07-17)

Findings from a four-agent research pass over zones 13 (Island of Dawn) and 436
(Karascha's Lair) on both servers. Grouped by severity. Tool names are given
without the `mcp__datasheet-vNN__` prefix; server noted per item.

## Deployment follow-up (2026-07-25)

The 2026-07-17 fixes below were committed but **never deployed**: `.mcp/datasheet-mcp.exe` was still
the May 8 build and `.mcp/entity_config.json` the April 25 copy, so every "Fixed" item was still
broken in practice for a week (v31 `profile_item` still errored; `search_quests` for hz 13 still
returned 14 quests instead of 99). That failure mode is invisible from inside a session because the
tools answer from the old binary.

Addressed at the root: `deploy-mcp.ps1` now publishes and copies **both** the exe and
`entity_config.json` into `.mcp/` in one command, `list_entity_types` gained a `files` column, and
startup logs `Mounted N of M configured entity types`. See the 2026-07-17 client-DataCenter request
for the full mount-diagnostics change.

Also closed in this pass:

- **Item 18 (no raw escape hatch for quest data): done.** New `lookup_quest` tool plus
  `find_free_ids` support for `entityType: "Quest"`. See the 2026-07-21 Berlon request, item 3.
- **Item 19 (index-empty vs data-absent): done for entity tables.** Empty results now say whether
  the backing file exists and where it was looked for.
- **Item 14, in part: done.** The v31 "orphan dialog texts with no task association" and the
  "text 100 (not found)" sentinel were one bug: the dialog resolver used the text-id reference as
  the dialog file's chain id, so every quest read other quests' files. See the 2026-07-21 Berlon
  request, item 4. The `lookup_story_arc_dialogs` payload size and member filtering are still open.
- Items 11, 13, 15, 16, 20 and the `batch_lookup` typed-error nit remain deferred.

## Resolution log (2026-07-17)

Triaged and implemented in datasheet-mcp the same day; dotnet test green (342),
Release AOT publish validated 15/15 via a direct stdio harness against both
datasheet paths. Deployment of the new exe to `.mcp/` pending (binary locked by
running session servers; swap on session restart).

- **Fixed:** 2, 3, 4, 5, 6, 7 (kill-target indexing; sibling-layer expansion
  deferred), 8, 9, 10; 12 partial ([DEAD] markers, gold units).
- **Rejected (already working):** 1 (QuestCompensation was fully supported; the
  IoD continent-13 entries are genuinely EMPTY reward stubs, now reported as
  "registered but defines no compensation" instead of "no data"; this is a
  patch 001 content gap, not an MCP gap), 17 (`search {}` already enumerates).
- **Deferred (design):** 11, 13, 14, 15, 16, 18, 19 (partial messaging
  improvements shipped), 20.
- **New minor issues found during validation:** `batch_lookup` declares `ids`
  and `attributes` as JSON-encoded strings; native arrays produce an opaque
  "An error occurred" (should reject with a typed message). Gold unit
  conversion renders `?` for fractional max values (cosmetic).

## Blocking gaps (no MCP path to the data)

1. **v92 QuestCompensation is unsupported.** On v92, quest rewards live in
   `CompensationData/QuestCompensationData_{continent}.xml` (entity
   `QuestCompensation`, keyed by `questId`; 77 entries exist for continent 13).
   `lookup_quest_rewards` only reads the legacy v31-style layout and returns
   "No compensation data" for every classic leveling quest (tested 1301, 1316,
   1317, and more). `lookup`/`lookup_enriched` on QuestCompensation drop the
   child elements (`CompensationType`/`Item`), returning only `questId`. Net
   effect: v92 quest reward values (XP, gold, class gear) are completely
   invisible to the MCP, and this file is actively modified by patch 001.
   Highest-priority fix.
2. **v31 `profile_item` errors on every call** (tested 12121, 10017, 17404):
   generic "An error occurred invoking 'profile_item'" with no diagnostics.
   Fallback `batch_lookup` loses display names, stats, and passivity resolution.
3. **v31 gathering tools broken for continent 13**: `audit_zone_gathering`
   and `lookup_gathering_spawns` both return an opaque "An error occurred"
   (v92 counterparts work on the same continent). Original-game gathering
   comparison is impossible without manual XML parsing.
4. **No PointStore/BuffStore resolvers.** `audit_zone_merchants` (v92, hz 13)
   looks up PointStore menus 6090/609 and BuffStore 1 as BuyMenuData and
   reports "not found"; MedalStore 315 fails with "VillagerMenuItem not found".
   Cannot distinguish data corruption from missing tool capability.
5. **`check_references` has no rules for NpcTemplate** ("NpcTemplate has no
   configured references"), so NPC to compensation-table links cannot be
   validated; that is the natural integrity check for loot audits.

## Correctness / consistency issues

6. **v31 `lookup_hunting_zone` mount inconsistency**: hz 13 and 436 return
   "not found -- not mounted under any Area" while `list_zones`,
   `resolve_region`, and `audit_zone_spawns` on the same server resolve them
   fine. Nearly produced a false "IoD absent from v31" conclusion. Should fall
   back to ZoneName/ContinentData when area mounting is absent.
7. **`search_quests` zone index systematically undercounts.** Filtering by
   huntingZoneId 13 misses the entire classic questline: the index only covers
   villager/visit references, so kill-task-only quests (e.g. 1313 targets
   monster 13,300910) and quests registered under sibling layers (64, 213) of
   the same area are invisible. Needs kill-target indexing and/or an
   area/continent-expansion mode.
8. **Sentinel values rendered as broken references.** Successor "Quest 101"
   (end-of-chain) prints as "101 (not found)" on virtually every quest, and
   prerequisite "Quest 99999 (Unavailable Quest)" renders like a real dangling
   link. `audit_quest_chain` prints "(unknown)" ambiguously for both
   unresolved-name and nonexistent-quest; a dependency audit should
   distinguish them and annotate known sentinels.
9. **`batch_lookup` cannot reach nested blocks**: requesting `level`/`maxHp`
   on NpcTemplate returns empty columns because they live in the `[Stat]`
   child (single `lookup` resolves them). Forces one lookup per NPC.
10. **Item name resolution**: `batch_lookup`/`search` on Item return internal
    names (`dual_01`, `mail17_body`); no displayName option, forcing a
    `profile_item` round-trip per item. NpcTemplate `search` already emits
    display names; Item should too.

## Output-format friction

11. **`audit_zone_spawns`**: multi-zone calls dump 84k chars of raw
    per-territory rows to a file; needs a summary/group-by-template mode
    (name, level, spawn total). Many rows report 0,0,0 coordinates
    (party-sourced territories), degrading spatial analysis, notably in
    dungeon 436.
12. **`audit_zone_loot`**: highly repetitive across near-identical tables; a
    "diff vs common skeleton" or summary mode would cut output ~80%. Dead
    bags (probability 0) print identically to live ones; mark them. Synthetic
    LT-N ids are per-invocation, preventing cross-server table diffs; expose
    the real compensation id per NPC. Money ranges lack units.
13. **Currency formatting**: `gold:10000000` and `buyPrice: 140` are raw
    copper with no unit label anywhere; `audit_zone_merchants` shows only
    `itemId|priceRevision` with no resolved price or price formula.
14. **Dialog tools**: `lookup_story_arc_dialogs` returned a 52 KB escaped-JSON
    payload via file indirection with no member filtering or pagination;
    `lookup_quest_dialogs` on v31-format quests appends orphan dialog texts
    with no task association and prints "text 100 (not found)" sentinels;
    letter-triggered quests render speakers as "[npc 0,0]".
15. **Medal shop rotation blocks unlabeled** (shop 10050): four repeated item
    blocks with different prices and no section headers or rotation labels.

## Capability wishlist

16. **Villager dialog enumeration per zone** (list which villager IDs have
    ambient dialogs); currently requires guessing IDs.
17. **Empty-filter scans**: `search` requires a dummy `{"id":"1..9999999"}`
    filter to enumerate a zone; support an explicit all-in-zone mode.
18. **Raw fallback for quest data**: `Quest` is not in `list_entity_types`,
    so when the dedicated quest tools hit a gap there is no raw escape hatch.
19. **Index-empty vs data-absent signal**: empty results (v31 merchants,
    v31 quests for hz 13) cannot be distinguished from an index keyed off a
    different HZ; a "what does this index cover" introspection would help.
20. **Section resolution for zone 13**: `lookup_area` returns one unnamed
    section although named sub-regions exist (e.g. StrSheet_Region 13004
    "Tainted Gorge"), making `lookup_section_npcs` unusable there.

## Domain doc candidate (not an MCP change)

The v92 QuestCompensation structure discovered here
(`QuestCompensationData_{continent}.xml`, keyed by questId, children carry
exp/gold/item rewards) should be captured in the datasheet-domain docs if not
already documented.
