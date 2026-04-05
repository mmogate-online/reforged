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
| Live entity data (lookup by ID, search by attributes) | MCP tools | Call datasheet MCP tools |
| Relationships (what references an item, evolution paths) | MCP tools | Call trace/audit MCP tools |
| Unused ID ranges for new content | MCP tools | Call `find_free_ids` |

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

Use MCP tools for live data queries. Do not write Python XML-parsing scripts when MCP tools can answer the question.

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

Use `find_free_ids` to find unused ID gaps. Always check `domain_docs` reference/id-registry.md first for documented ID range conventions before allocating.

## Research workflow

1. **Identify the question type** using the source selection table above
2. **Check domain docs first** for conceptual understanding — don't jump to MCP queries without context
3. **Use MCP tools for specific data** — entity lookups, ID searches, relationship tracing
4. **Check DSL docs for implementation** — how to express findings as YAML specs
5. **Cross-reference** — domain docs explain the "what", MCP tools show the "current state", DSL docs show the "how to change"
