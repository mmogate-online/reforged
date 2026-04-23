---
name: log-progress
description: >
  Log completed work to CHANGELOG.md and update STATUS.md. Auto-invoke when a
  migration phase transitions to Done, a patch batch is applied and validated,
  or an infrastructure milestone (DSL fix, new MCP capability) is noted during
  content work. Also invoke proactively at session end when meaningful progress
  was made.
disable-model-invocation: false
user-invocable: true
---

# Log Progress

Use this skill to record completed work in `reforged/CHANGELOG.md` and update
`reforged/STATUS.md`. Both files live at the root of the git repo.

## When to invoke

**Invoke immediately** (no need to ask):
- A migration phase entry in any `docs/migrations/*/progress.md` changes to Done
- A batch of patch specs is applied **and** validated (both steps complete)
- Phase 4 validation confirms a migration is correct

**Prompt the user first** ("Should I log this progress?"):
- Session is wrapping up and meaningful work was done but no clear phase boundary was crossed
- Infrastructure milestone noted (DSL fix, new MCP tool) that unblocked content work
- Unsure whether the change is significant enough

**Skip** (do not log):
- Exploratory research, reading files, or querying MCP with no outcome
- A spec was written but not yet applied or validated
- A DSL bug was discovered and filed but not resolved

---

## Step 1 — Identify what changed

Summarize in your head:
1. **Content** — what migration phase, spec, or validation was completed
2. **Infrastructure** — any DSL commits, MCP tool additions, or build changes that enabled the work (get commit hash from `git -C <dsl_source> log --oneline -3` if relevant)
3. **Blockers resolved** — any DSL requests that are now fixed

---

## Step 2 — Append to CHANGELOG.md

File: `D:\dev\mmogate\github\reforged-server-content\reforged\CHANGELOG.md`

Read the file first to see the last entry date. Then prepend a new entry at the
top of the log section (below the header). Use today's date from `currentDate`
in memory context.

### Entry format

```markdown
## YYYY-MM-DD

### Content
- <one line per completed item: migration phase, spec applied, validation done>

### Infrastructure
- <datasheetlang: short description (commit hash)>
- <other correlated project changes that unblocked content work>

### Blockers resolved
- <DSL request filename or short description — omit section if none>
```

Rules:
- Omit **Infrastructure** and **Blockers resolved** sections if nothing to report
- One line per item — no multi-sentence prose
- Infrastructure entries: prefix with `datasheetlang:`, `datasheet-domain:`, or `reforged-server:` as appropriate
- Only include infrastructure items that directly enabled the content work done this session

---

## Step 3 — Update STATUS.md

File: `D:\dev\mmogate\github\reforged-server-content\reforged\STATUS.md`

Read the file, identify the section(s) affected by what changed, and update them in place.

Rules:
- Change status emoji: 🔄 In Progress → ✅ Complete, or add a new 🔄 item
- Update the "Last updated" line at the top
- If a new patch or system starts, add a new section following the existing structure
- Do **not** rewrite unaffected sections

---

## Step 4 — Confirm

After writing both files, state in one sentence what was logged.
Do not commit — the user decides when to commit.
