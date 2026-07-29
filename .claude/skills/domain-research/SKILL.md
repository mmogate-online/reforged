---
name: domain-research
description: >
  Routes any question about game data to the right source (domain docs, DSL docs, the two
  datasheet MCP servers, or the content framework) and catalogs what the datasheet MCP can
  answer: NPC profiles and name-vs-displayName divergence, spawn footprints, quest gates,
  dormant commented-out content, coordinate-to-section, and index freshness. Use when
  researching entities, ID ranges, item stats, loot tables or enchant chains; when deciding
  which MCP tool answers a question or whether one exists at all; when an MCP query returns
  nothing and you need to know whether that is real; when checking whether the MCP reflects
  edits you just applied, or whether the .mcp binary is stale; or when the question is about
  design intent, balance, currencies or seasons.
disable-model-invocation: false
user-invocable: true
argument-hint: [topic]
---

# Domain Research

This project has three research sources. Use the right one for the question.

## Source selection

| Question type | Source | How to access |
|---------------|--------|---------------|
| Game system concepts (how items/enchants/loot work) | Domain docs | Read markdown files |
| ID ranges, type codes, grade tiers, class data | Domain reference docs | Read markdown files |
| DSL syntax, operations, schema attributes | DSL docs | Read MDX files |
| DSL package/import/variable mechanics | DSL docs | Read MDX files |
| Current state of v92 server content | MCP `datasheet-v92` | Call `mcp__datasheet-v92__*` tools |
| How original v31 content worked | MCP `datasheet-v31` | Call `mcp__datasheet-v31__*` tools |
| Unused ID ranges for new content | MCP `datasheet-v92` | `mcp__datasheet-v92__find_free_ids` |
| Design intent, balance philosophy, reward budgets, currency rules, season scope, monetization | Content framework docs | Resolve `content_framework` from `.references`, read the numbered design doc for the system (00-overview through 10-social-architecture) |

## 1. Domain knowledge docs

**Path:** Resolve `domain_docs` from `.references` file.

**Structure:**
- `entities/`: System documentation (item, equipment, enchant, passivity, evolution, loot, NPC, quest, crystal, gacha, etc.)
- `reference/`: Lookup tables (ID ranges, type codes, class data, grade tiers, abnormality/passivity compatibility)

**Navigation:** Read the knowledge base index first: `D:\dev\github-vperim\datasheet-domain\.claude\CLAUDE.md` (the repo root of `domain_docs` from `.references`). It is a curated flat table mapping every documented topic to its exact file path. Use it to find the right file to read directly rather than globbing or navigating from `index.md`.

**Format:** Raw markdown (`.md`), readable directly.

**NPC dialog and quest editing:** `entities/villager-dialog-system.md` (ambient NPC lines: server per-zone aggregate vs client per-villager shards, SpeechCondition selectors), `entities/quest-system.md` (quest string row layout, task reward flag and wiring, QuestDialog per-quest files and markup tokens), `entities/villager-service-system.md` (menu bindings), `entities/quest-link-system.md` (journal links, NpcLoc registry incl. void-position spawns).

## 2. DSL tool docs

**Path:** Resolve `dsl_docs_enduser` from `.references` file.

**Structure:**
- `guides/`: Quickstart, definitions, packages, recipes (bulk-updates, equipment-sets, quest-chains)
- `reference/`: CLI, syntax, operations, filters, imports, variables, error codes, common pitfalls
- `schemas/`: Per-entity attribute reference (one file per entity type)

**Navigation:** For schema questions, go directly to `schemas/<category>/<entity>.mdx`. For syntax/feature questions, check `reference/`. For how-to questions, check `guides/` and `guides/recipes/`.

**Format:** MDX files, ignore JSX component tags, read the markdown content.

## 3. MCP datasheet tools

Two MCP servers are configured. Selecting the wrong one produces incorrect results.

### Server selection: mandatory rule

| Query intent | Server |
|---|---|
| What does our active server currently have? | `datasheet-v92` |
| How did the original game work? (names, structure, rewards, mechanics) | `datasheet-v31` |
| Validate what we've already spec'd or applied | `datasheet-v92` |
| Find free IDs for new content | `datasheet-v92` |
| Original item names, NPC dialogs, quest chains, loot tables | `datasheet-v31` |
| Cross-entity link validation in live content | `datasheet-v92` |

**Hard rules:**
- **v31 is read-only reference.** Never use v31 output as direct input to a DSL spec. v31 data describes the old server; IDs, attributes, and structure may differ from v92 conventions.
- **v92 is the source of truth for current state.** All DSL specs apply to v92. Always verify restoration work against v92 after applying.
- **Never mix servers in a single chain of reasoning** without explicitly labeling which data came from which server.
- **The content framework defines locked invariants (listed in its CLAUDE.md).** Content specs must not violate them; if research reveals a conflict between a requested change and an invariant, surface it.
- **Framework answers why/how-much questions; MCP and domain docs answer what-exists/how-encoded questions.**

### Restoration research pattern (v31 → v92)

When restoring original content to the v92 server:
1. Use `datasheet-v31` tools to understand the original structure (items, quests, NPCs, loot, rewards, dialogs)
2. Use domain docs to understand how those systems are modeled in v92 schema
3. Use `datasheet-v92` tools to check what already exists and find appropriate ID ranges
4. Write DSL specs targeting v92 based on findings from steps 1 to 3

### Discovery pattern

When investigating an unfamiliar entity type:
1. `describe_entity`: discover XML structure, attribute names, value distributions
2. `search` or `search_text`: find entities matching criteria
3. `lookup` or `batch_lookup`: get specific entities by ID
4. `profile_item`: complete item profile (equipment stats, enchant chain, passivities, display name)

### Relationship tracing

| Tool | Answers |
|------|---------|
| `trace_item_dependencies` | What references this item? (evolution, recipes, sets, inheritance, decomposition) |
| `trace_evolution` | What are the evolution paths for this item? |
| `trace_enchant_chain` | Enchant → categories → passivities graph |
| `trace_passivity_proc` | Passivity proc chain → abnormality → effects |
| `check_references` | Are cross-entity links valid? Includes NpcTemplate to loot-table links (CCompensation/ECompensation, zone-scoped) |

### Zone and loot investigation

| Tool | Answers |
|------|---------|
| `list_zones` | What zones exist? Filter by name, channel type, NPC presence |
| `audit_zone_loot` | All NPCs + loot tables in a zone |
| `scan_zones` | Search NPCs/compensation across ALL zones |

### NPC, spawn, quest and position investigation

Delivered 2026-07-25 in response to this project's own requests. Each one replaces a
multi-call or hand-rolled-Python workflow, so reach for these BEFORE writing a script.

| Tool | Answers | Replaces |
|------|---------|----------|
| `profile_npc` | Everything about one template in one call: identity (with a WARNING when `NpcData.name` and `StrSheet_Creature` displayName diverge), spawn footprint by habitat group and territory, quests referencing it with kill counts and enabled state, and templates sharing its `shapeId` | Four separate lookups plus raw XML parsing |
| `audit_quest_gates` | Per quest in a zone, whether every contact NPC and every kill/collect target actually spawns. A blocked quest is authored correctly but silently uncompletable | The "MATCH but unspawned" class of audit miss |
| `find_dormant_blocks` | Content commented out in a datasheet, which the server never loads and every other tool correctly ignores. `wellFormed=N` flags a comment that swallowed a closing tag | Manually scanning for `<!--` before trusting that content "exists" |
| `resolve_position` | Which AreaData sections contain a world coordinate, nested broadest-first. The inverse of `resolve_region` | Hand-rolled point-in-polygon against section fences |
| `datasheet_freshness` | Per cached family: files on disk, newest write time, index build time, and `current` / `stale` / `not-yet-built` | Probing a known marker to guess whether the server went stale |
| `lookup_quest` | A quest body from QuestData: header, requirements, giver trigger, prerequisites, and every task with Korean type paired to its English name | Reading `.quest` files with Python |

Two upgrades to tools you already know:

- `audit_zone_spawns` takes `npcTemplateIds` and `territoryGroupIds`. Always filter: an
  unfiltered zone call can exceed the token ceiling (zone 13 returns 742 rows), while the
  same question filtered to one template returns tens. Output also gained a
  `territoryGroupId` column and a `posSource` column reading `authored` or `fenceCentroid`,
  the latter meaning the datasheet holds 0,0,0 and the engine picks a random point in the
  fence.
- `find_free_ids` allocates quest ids.

### ID allocation

Use `find_free_ids` on `datasheet-v92` to find unused ID gaps. Always check `domain_docs` reference/id-registry.md first for documented ID range conventions before allocating.

## Research workflow

1. **Identify the question type** using the source selection table above
2. **Select the correct MCP server**: v31 for original game knowledge, v92 for current server state
3. **Check domain docs first** for conceptual understanding, and do not't jump to MCP queries without context
4. **Use MCP tools for specific data**: entity lookups, ID searches, relationship tracing
5. **Check DSL docs for implementation**: how to express findings as YAML specs
6. **Cross-reference**: domain docs explain the "what", v31 shows the "original state", v92 shows the "current state", DSL docs show the "how to change"

## Lessons

### An MCP miss is evidence only once you know the mechanism that would have produced a hit
- **Date/source:** 2026-07-28: `reverse_lookup_shop_npcs` returned no NPCs for token shop menus 9999008, 9999004 and 9999006, and that was written up as "all three patch-002 token shops are unreachable", a defect claim that reached three documents before it was caught. The shops are fine. They are item-opened `MEDAL_USEABLE` right-click shops, where `VillagerMenuItem` binds the ITEM to the menu and no NPC is ever bound. The KB already said so: `entities/merchant-system.md` maps `MEDAL_USEABLE` to "Right-click opens shop UI from inventory" with the exact `VillagerMenuItem + BuyMenuList + BuyList` chain, and `packages/dungeon-tokens/index.yml` repeats it in its header.
- **Why:** a query that returns nothing answers the question you asked, not the question you meant. `reverse_lookup_shop_npcs` asks "which NPC opens this menu", and for a shop type where the answer is legitimately "none", the miss is the CORRECT result. An absence looks identical whether the wiring is broken, the wiring is a different shape, or the query was the wrong one, and unlike a hand-written parser's empty result there is no bug to find, so nothing prompts a second look.
- **Apply:** before turning any negative result into a defect claim, state the mechanism that would have produced a positive one and confirm the subject uses it. For shops specifically: read `combatItemType` on the item first. `MEDAL_USEABLE` plus `itemUseCount` means the item opens the shop and no NPC binding exists or should. Check the KB's primary doc for the system before filing, which is the same discipline as the entry below, and check git log for the commit that established the wiring (here, `a57c65b`, which built that chain deliberately).

### Classify id hits attribute-level before sizing a migration; adjacent id bands are usually different families
- **Date/source:** 2026-07-28: a raw-count pass reported `QuestCompensationData` carrying 3,053 feedstock references across 70 files, which would have made it the second largest surface in a corpus-wide flattening. An attribute-level pass found the real number is ZERO. All 3,053 hits were ids 94113 to 94118, Relic Fragment and Relic Shard, a `generalMaterial` bound family that merely sits next to feedstock (94101 to 94112) in the id space. The same pass also found 216 references to 94119 to 94122, which are not items at all.
- **Why:** a bare integer in XML carries no type. The same digits appear as an item id, a quantity, a coordinate, an unrelated entity id and a string id, and a family boundary inside a contiguous id run is invisible to grep. Sizing work from raw counts inflates scope in one direction and hides the real surface in the other, and the error survives review because the number is genuinely present in the file.
- **Apply:** for any census that will size work, parse with ElementTree and emit the (file family, element, attribute) triple for every hit, then classify each triple as an item reference or a false positive BEFORE totalling. Confirm family boundaries with `batch_lookup` or `profile_item` on the edge ids rather than assuming a contiguous range is one family. Report per-id counts, never a single total: it is the per-id breakdown that exposes a foreign family.

### Before calling a setting undocumented, grep the raw file for `<!--` and read the system's PRIMARY doc end to end
- **Date/source:** 2026-07-28: a two-restart investigation into why a field event would not start was already answered in two places. `ContinentData.xml` documents in a comment block at the top of the file (the very file being edited) that its `field` channel type is the attribute that must be set to use the field event system, and the domain KB's field event doc says the same thing in its "What Starts an Event" section. Every inspection of the file went through Python `ElementTree`, which DISCARDS comments: 162 comments in that file, zero in the parse. The doc search read the zone-hierarchy doc and the DSL schema page instead of the field event doc itself.
- **Why:** the datasheet corpus carries its own inline documentation, and every structural reader (ElementTree, the MCP, the server loader) drops it, so a file can look undocumented while explaining itself in plain text a few lines above the row you are editing. Reading AROUND a system has the same shape: adjacent docs describe the entity, not what triggers it, so they read as complete while omitting the answer.
- **Apply:** when reasoning about an unfamiliar attribute, grep the raw file for `<!--` BEFORE parsing it structurally (or parse with `ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))`). Before declaring anything undocumented, open the primary doc for that system from the KB index and read it end to end rather than sampling neighbours. Note this is the OTHER comment problem: `find_dormant_blocks` finds content commented OUT, and never surfaces explanatory comments.
- **Also strip comments before any count that sizes work or claims content exists** (2026-07-28): a feedstock census read 35 references in `LimitedDrop.xml` and 0 after stripping, because the entire file body is commented out and the system caps nothing; `EventMatching.xml` went 217 to 164 the same way. A raw count silently mixes live rows with retired ones, so "this content exists" and "this content is reachable" become the same number when they are not.

### A stale `.mcp/` is invisible from inside a session, and a half-updated one is fatal
- **Date/source:** 2026-07-25: the datasheet-mcp team shipped 18 commits including 9 new tools, and documented in their own CLAUDE.md that the deployment step had previously "left the servers a build behind". Two distinct failure modes are recorded there.
- **Why:** `.mcp.json` points both server instances at `reforged/.mcp/datasheet-mcp.exe`, and the exe reads `entity_config.json` from its own directory. (1) If only one of the pair is copied, `EntityConfigLoader.Validate` throws at startup before the stdio transport opens, so EVERY tool call fails rather than degrading. A config using a feature the deployed exe predates is fatal, not merely inconsistent. (2) If both are simply old, nothing errors at all: tools answer from the previous build, so delivered fixes look unshipped and new entity types look missing, and no amount of querying from inside the session reveals it.
- **Apply:** when a documented MCP capability appears absent, suspect the deployment before the tool. Check `list_entity_types` (it reports a `files` column) and `datasheet_freshness`; the startup log line `Mounted N of M configured entity types` is the other tell. Deploy with the MCP repo's `deploy-mcp.ps1`, which publishes and copies BOTH artifacts, and run it with no Claude Code session open because the running servers hold a lock on the exe. Never hand-copy one file.

### Set PYTHONIOENCODING=utf-8 before any Python that prints datasheet text
- **Date/source:** 2026-07-25: a script scanning `TerritoryData_13.xml` for Acharak spawns died with `'charmap' codec can't encode characters in position 22-24` the instant it printed a territory `desc`. Two calls lost re-running it.
- **Why:** every datasheet carries Korean in `desc` and `name` attributes, and the default console codepage on this box cannot encode them. The failure happens at PRINT time, not parse time, so a script can do all its work correctly and still die on its first output line, which reads like a data problem rather than a console problem.
- **Apply:** invoke datasheet-parsing scripts as `PYTHONIOENCODING=utf-8 python <script>`. Read files with `encoding="utf-8-sig"` (the loader requires a BOM and it must not reach the parser). Write the script to a file rather than a bash heredoc: backslash and quote escaping through the heredoc layer is a second, independent source of syntax errors.

### In a hand-written parser, an empty result is a bug hypothesis, not a finding
- **Date/source:** 2026-07-25: a Python spawn scan returned zero hits from the correct files because it filtered on `templateId`; the attribute is `npcTemplateId`. The empty output initially read as a finding ("no Acharak spawns here") rather than as a bug.
- **Why:** a wrong attribute name yields an EMPTY result, never an error, which is indistinguishable from a true negative and silently confirms whatever you hoped to prove. The MCP side of this was fixed the same day (it now explains why a child-attribute filter cannot match, and distinguishes an attribute that is unset in the searched scope from one that does not exist), so the trap now lives almost entirely in hand-written parsers.
- **Apply:** prefer the MCP over a parser precisely because it explains its empty results. When you must parse raw XML, call `describe_entity(entityType)` first for attribute names and value distributions, then sanity-check the scan by asserting that a row you KNOW is present shows up. Known trap pairs: territory spawns use `npcTemplateId` (not `templateId`); `StrSheet_NpcLoc` rows key on `templateId` plus `huntingZoneId`, with no `id`; `NpcData` `Template` carries `name` (internal) while the player-visible name lives in `StrSheet_Creature`.

### Filter every spawn audit; an unfiltered zone call still overflows
- **Date/source:** 2026-07-25: `audit_zone_spawns(huntingZoneIds="[13]")` returned 742 entries across 97,483 characters, over the token ceiling and spilled to disk, to answer a question whose real answer was 8 rows. The `npcTemplateIds` / `territoryGroupIds` filters shipped the same day; the same call filtered to two templates returns 39 rows.
- **Why:** the zone is the wrong unit for almost every real question. Scope creep in the query, not the tool, is what overflows: zone 13 alone exceeds the limit and larger zones are worse.
- **Apply:** pass `npcTemplateIds` or `territoryGroupIds` whenever the question is about specific templates or one habitat group. For a single template prefer `profile_npc`, which returns the footprint already joined to quest links and shape siblings. Reserve the unfiltered call for genuine whole-zone inventory, and expect a spill file when you do it.

### Distinguish authored, applied, committed, and deployed before concluding content is missing
- **Date/source:** 2026-07-17: IoD alpha research concluded specs 16-22 were unapplied; the local datasheet tree had been deliberately reset after a test
- **Why:** MCP queries read the local datasheet working tree. Specs can exist in `specs/` (authored) without being applied; applied output can be uncommitted; the dev server can hold an overlay from a previous state. Each is a different state, and the working tree is routinely reset between test cycles.
- **Apply:** Before reporting content as missing, check `git -C <server_datasheet> status/log` and `deploy_dev.py --status` to establish which state you are looking at; phrase findings as "not in the current working tree" rather than "does not exist".

### Query every sibling layer of a multi-layer area when enumerating zone content
- **Date/source:** 2026-07-17: IoD alpha research; `search_quests` hz 13 missed the classic questline
- **Why:** Area 13 spans hunting zones 13 (combat), 64/364 (hub), 213 (social), 313 (politics); quests and merchants register under hub/social layers. Kill-target indexing (2026-07-17 MCP build) widened hz-13 quest results from 14 to 96, but sibling-layer expansion is still manual.
- **Apply:** For any multi-layer area, run zone-filtered queries against all sibling HZ ids, not just the combat layer; discover layers via `lookup_area`/`list_zones` first.

### "Empty reward stub" from lookup_quest_rewards is a content gap, not missing data
- **Date/source:** 2026-07-17: MCP fix batch; IoD quests 1301/1316/1317
- **Why:** v92 QuestCompensation entries can exist with no children; the tool distinguishes "registered but defines no compensation (empty reward stub)" from "not found". The IoD continent-13 entries are empty pending patch 001 content.
- **Apply:** Treat the stub message as "quest grants nothing as configured" and flag it to content work; do not re-investigate it as a tool failure.

### batch_lookup takes JSON-encoded strings for ids and attributes
- **Date/source:** 2026-07-17: stdio validation of the rebuilt MCP
- **Why:** Passing native JSON arrays yields an opaque "An error occurred invoking 'batch_lookup'"; the schema declares string parameters (e.g. `"[1002]"`). Since the 2026-07-17 build it resolves nested Stat attributes (level/maxHp) and Item display names.
- **Apply:** Encode `ids` and `attributes` as JSON strings; on an opaque batch_lookup error, check parameter typing before suspecting data.
