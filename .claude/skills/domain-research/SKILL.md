---
name: domain-research
description: Use when researching game entities, datasheets, ID ranges, item stats, loot tables, enchant chains, or any TERA game system knowledge. Routes to the correct source.
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

## 1. Domain knowledge docs

**Path:** Resolve `domain_docs` from `.references` file.

**Structure:**
- `entities/` — System documentation (item, equipment, enchant, passivity, evolution, loot, NPC, quest, crystal, gacha, etc.)
- `reference/` — Lookup tables (ID ranges, type codes, class data, grade tiers, abnormality/passivity compatibility)

**Navigation:** Start from `index.md` for an overview. Glob the directory to discover available files.

**Format:** Raw markdown (`.md`), readable directly.

## 2. DSL tool docs

**Path:** Resolve `dsl_docs_enduser` from `.references` file.

**Structure:**
- `guides/` — Quickstart, definitions, packages, recipes (bulk-updates, equipment-sets, quest-chains)
- `reference/` — CLI, syntax, operations, filters, imports, variables, error codes, common pitfalls
- `schemas/` — Per-entity attribute reference (one file per entity type)

**Navigation:** For schema questions, go directly to `schemas/<category>/<entity>.mdx`. For syntax/feature questions, check `reference/`. For how-to questions, check `guides/` and `guides/recipes/`.

**Format:** MDX files — ignore JSX component tags, read the markdown content.

## 3. MCP datasheet tools

Two MCP servers are configured. Selecting the wrong one produces incorrect results.

### Server selection — mandatory rule

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

### Restoration research pattern (v31 → v92)

When restoring original content to the v92 server:
1. Use `datasheet-v31` tools to understand the original structure (items, quests, NPCs, loot, rewards, dialogs)
2. Use domain docs to understand how those systems are modeled in v92 schema
3. Use `datasheet-v92` tools to check what already exists and find appropriate ID ranges
4. Write DSL specs targeting v92 based on findings from steps 1–3

### Discovery pattern

When investigating an unfamiliar entity type:
1. `describe_entity` — discover XML structure, attribute names, value distributions
2. `search` or `search_text` — find entities matching criteria
3. `lookup` or `batch_lookup` — get specific entities by ID
4. `profile_item` — complete item profile (equipment stats, enchant chain, passivities, display name)

### Relationship tracing

| Tool | Answers |
|------|---------|
| `trace_item_dependencies` | What references this item? (evolution, recipes, sets, inheritance, decomposition) |
| `trace_evolution` | What are the evolution paths for this item? |
| `trace_enchant_chain` | Enchant → categories → passivities graph |
| `trace_passivity_proc` | Passivity proc chain → abnormality → effects |
| `check_references` | Are cross-entity links valid? |

### Zone and loot investigation

| Tool | Answers |
|------|---------|
| `list_zones` | What zones exist? Filter by name, channel type, NPC presence |
| `audit_zone_loot` | All NPCs + loot tables in a zone |
| `scan_zones` | Search NPCs/compensation across ALL zones |

### ID allocation

Use `find_free_ids` on `datasheet-v92` to find unused ID gaps. Always check `domain_docs` reference/id-registry.md first for documented ID range conventions before allocating.

## Research workflow

1. **Identify the question type** using the source selection table above
2. **Select the correct MCP server** — v31 for original game knowledge, v92 for current server state
3. **Check domain docs first** for conceptual understanding — don't jump to MCP queries without context
4. **Use MCP tools for specific data** — entity lookups, ID searches, relationship tracing
5. **Check DSL docs for implementation** — how to express findings as YAML specs
6. **Cross-reference** — domain docs explain the "what", v31 shows the "original state", v92 shows the "current state", DSL docs show the "how to change"
