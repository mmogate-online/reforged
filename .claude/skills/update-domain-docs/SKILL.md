---
name: update-domain-docs
description: >
  Use when a research session produces structural findings about any datasheet entity system
  that are not yet captured in the domain docs, when reverse-engineering server XML files
  reveals an undocumented schema, when an existing domain doc is found to be incomplete
  or missing attributes, or when MCP queries reveal behaviors, trigger types, or task types
  not listed in the documentation. Auto-invoke after any session where new entity system
  knowledge was acquired — including newly explored XML file types, undocumented attributes
  on known entities, or cross-system relationships not yet mapped. Do not invoke for content
  work that uses existing documented systems without discovering anything new.
disable-model-invocation: false
user-invocable: true
argument-hint: [system-name]
---

# Update Domain Documentation

Domain docs live at the path resolved by `domain_docs` in `.references`:
`D:\dev\github-vperim\datasheet-domain\src\content\docs\`

Five files must be kept in sync whenever docs change:

| File | Purpose | When to update |
|------|---------|----------------|
| `entities/<system>.md` or `reference/<topic>.md` | The doc itself | Always |
| `TRACKING.md` | Progress table + research checklist | Always |
| `astro.config.mjs` | Sidebar navigation | New files only |
| `.claude/CLAUDE.md` | Knowledge base index for agents | New files only |
| `.claude/skills/<system>/SKILL.md` | Auto-load skill that injects the doc | New files only |

---

## Step 1 — Identify what is new

State explicitly what knowledge was acquired this session that is not yet in the docs:

- **New system** — a file type or entity system with no doc at all
- **Missing attributes** — an existing doc lacks specific attributes found in the data
- **Missing types** — a trigger type, task type, or enum value not listed in an existing table
- **Incorrect coverage** — a claim in the docs contradicts what the data shows
- **New cross-system relationship** — a link between systems not captured in any integration table

If nothing new was discovered, stop here and do not invoke the rest of this skill.

---

## Step 2 — Check existing coverage

Before writing anything, read the relevant doc to confirm the gap is real.

1. Glob `{domain_docs}/entities/` and `{domain_docs}/reference/` to find candidate files
2. Read any file that might already cover the topic
3. Read `TRACKING.md` — check if the gap is already listed as an open research question

If the doc exists and the content is present, the gap does not exist — stop.

---

## Step 3 — Research and validate

**All claims in domain docs must be backed by data, not session memory.**

The research methodology depends on what is being documented:

### For a previously unseen XML file type

1. Glob the server datasheet for all files matching the pattern
2. Read 3–5 representative files — include the largest (most complex structure) and smallest (minimal structure)
3. Record every element name and attribute name encountered across all sampled files
4. For each attribute: note all observed values (not just one example)
5. For behavioral claims (e.g., "fires when HP reaches threshold"): verify by reading 2+ EventGroup entries that demonstrate the behavior

### For attributes missing from an existing doc

1. Use `mcp__datasheet-v92__describe_entity` on the entity type to get the attribute distribution
2. Use `mcp__datasheet-v92__count` or `mcp__datasheet-v92__search` to confirm frequency
3. Read 2–3 example entities that use the attribute to understand its semantics
4. Do not document an attribute whose purpose cannot be determined from the data alone — mark it as unknown

### For counts and frequency claims

- "X appears N times" claims require an actual count — use MCP `count` or grep the datasheet
- If an exact count is not feasible, use "N+ instances observed" with the sample size
- Never write frequency words like "common", "rare", or "frequently" without a count backing them

### Confidence tiers for documented attributes

Mark uncertain claims inline:

| Confidence | Condition | Notation |
|---|---|---|
| Confirmed | Seen in 3+ files with consistent semantics | No qualifier |
| Observed | Seen in 1–2 files; semantics inferred | *(observed, N files)* |
| Unknown | Attribute exists but behavior not determinable | *(semantics unknown)* |

---

## Step 4 — Write or update the doc

### Conventions (from domain CLAUDE.md)

- Frontmatter: `title` and `description` only — no other keys
- `##` for main sections, `###` for subsections — no `#` heading (title comes from frontmatter)
- Tables dominate — attribute listings, type catalogs, distributions
- Entity and attribute names in backticks: `progressTime`, `npcHp`
- Internal cross-references as links: `[Dungeon System](/entities/dungeon-system/)`
- **No raw XML blocks** — describe structure in prose and tables; pseudo-hierarchy blocks using box-drawing characters are acceptable
- No game IP references — use generic MMORPG terminology
- Technical, reference-oriented, concise — prose explains; tables enumerate

### Standard section order for entity docs

```
## Overview
## File Structure
## [Root Element] Attributes
## [Child Elements] (one ## per major structural tier)
## [Trigger/Type Catalog] (tables with count + attributes + description)
## Common Patterns (2–5 named patterns with concrete descriptions)
## Cross-System Integration (table: source → link → target)
```

Adapt the structure to the system being documented. Reference `dungeon-system.md` as the canonical style example.

### Updating an existing doc

- Add missing attributes to the existing table — do not reorganize the whole doc
- Add missing enum values as new rows — preserve existing rows
- If adding a new major subsystem, append a new `##` section at the bottom before the integration table
- Update the `description` frontmatter if scope has expanded

### Creating a new doc

Choose the path:
- New entity system → `entities/<system-name>.md`
- New reference table → `reference/<topic>.md`

File name: lowercase, hyphenated, matches the system name used in TRACKING.md and the sidebar.

---

## Step 5 — Update TRACKING.md

File: `D:\dev\github-vperim\datasheet-domain\TRACKING.md`

### Progress table (bottom of file)

For new docs — add a row:
```
| <System Name> | New | <YYYY-MM-DD> |
```

For updated docs — change the status:
```
| <System Name> | Updated | <YYYY-MM-DD> |
```

### Research checklist (middle of file)

For new docs — add a `### <System Name>` section with:
- `[x]` for every item documented this session
- `[ ]` for every open question identified during research (unknown attributes, unsampled file variants, unexplored sub-systems)

For updated docs — check off the items now resolved; add new `[ ]` items if gaps were found.

---

## Step 6 — Update astro.config.mjs (new docs only)

File: `D:\dev\github-vperim\datasheet-domain\astro.config.mjs`

Add a sidebar entry in the appropriate group (`Entities` or `Reference`). Place it logically near related systems — not necessarily alphabetically.

```js
{ label: '<Human-Readable Name>', slug: 'entities/<system-name>' },
```

---

## Step 7 — Update .claude/CLAUDE.md (new docs only)

File: `D:\dev\github-vperim\datasheet-domain\.claude\CLAUDE.md`

Add a row to the appropriate table (`## Entity Systems` or `## Reference Tables`):

```markdown
| <System Name> | <keywords comma-separated — what agents would search for> | `src/content/docs/entities/<system>.md` |
```

Keywords should include: the XML file name pattern, all major element and attribute names agents might search for, and any system aliases or colloquial names.

---

## Step 8 — Create the auto-load skill (new docs only)

File: `D:\dev\github-vperim\datasheet-domain\.claude\skills\<system-name>\SKILL.md`

Every doc in the knowledge base has a corresponding skill that lazily injects the full doc content using the Skills 2.0 dynamic context injection syntax. Create the skill directory and write `SKILL.md`:

```
---
name: <system-name>
description: Load when working with <xml file pattern>, <primary element names>,
  <key attribute names>, or <system aliases and colloquial names>.
user-invocable: false
---

![backtick]cat "D:/dev/github-vperim/datasheet-domain/src/content/docs/<path-to-doc>.md"[/backtick]
```

Replace `[backtick]` / `[/backtick]` with a literal backtick character. The pattern is: exclamation mark immediately followed by a backtick-wrapped shell command on the first non-frontmatter line of the file.

The `description` must contain the trigger keywords an agent would naturally use when the system is relevant — XML file name patterns, element names, attribute names, and any aliases the system is known by.

`user-invocable: false` is mandatory — these skills are Claude-only, not user-invocable commands.

---

## Step 9 — Confirm

State in two sentences:
1. What was added or updated (doc name, scope of changes)
2. Which of the four supporting files were touched

Do not commit — the user decides when to commit.
