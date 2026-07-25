---
name: skill-authoring
description: >
  Standard for writing and reviewing project skills in .claude/skills/. Use when
  creating a new skill, editing an existing skill, encoding a lesson learned into
  the skill library, or reviewing a skill for compliance. Defines the frontmatter
  contract, description writing rules, progressive disclosure structure, and the
  lesson-entry template.
disable-model-invocation: false
user-invocable: true
---

# Skill Authoring Standard

Authoritative rules for every skill in this repository. Derived from the official
Claude Code docs (code.claude.com/docs/en/skills and the Agent Skills best
practices page); the full frontmatter field reference lives in
[reference.md](reference.md).

## Layout

- One skill = one directory: `.claude/skills/<skill-name>/SKILL.md`.
- The directory name is the command name (`/apply-spec` comes from `apply-spec/`).
  Lowercase letters, numbers, hyphens; prefer noun-phrase or gerund names
  (`domain-research`, `apply-spec`); never vague (`helper`, `utils`).
- Supporting depth goes in sibling files (`reference.md`, `examples.md`), linked
  from SKILL.md one level deep only. No chained references: deep chains get
  partially read and silently truncated.
- Use forward slashes in all paths inside skill content.

## Frontmatter contract

Required for every skill in this project (per CLAUDE.md conventions):

```yaml
---
name: <directory-name>
description: >
  <what it does AND when to use it, third person, specific trigger terms>
disable-model-invocation: false
user-invocable: true
---
```

- `description` is the trigger: it is pre-loaded into every session; the body is
  lazy-loaded only when relevant. Write it in third person, lead with the key use
  case, and include the words an agent would think of ("loot table", "upsert",
  "sync", "free IDs"). End with an explicit "Use when ..." clause listing 2 to 4
  concrete trigger situations. Max 1024 chars; vague descriptions ("helps with X")
  are rejected.
- Add `argument-hint` when the skill accepts parameters.
- Do not use `context: fork` in this project: skills here are reference and
  guidance, not orchestration tasks.
- Other opt-in fields (`allowed-tools`, `paths`, `model`, `effort`) only when
  genuinely needed; semantics in [reference.md](reference.md).

## Body rules

1. Under 500 lines, ideally far less. Claude is already smart: only write what it
   does not know, meaning this project's constraints, paths, conventions, and traps.
2. Standing instructions, not narration. Body content stays in context for the
   rest of the session; every sentence must earn that.
3. One default approach with an escape hatch, never a menu of alternatives.
4. Resolve external paths through `.references` keys, never hardcoded machine
   paths. Server datasheet paths use the `<server_datasheet>` placeholder.
5. No time-sensitive facts without provenance (see lesson template); no
   unexplained constants: justify or parametrize.
6. Examples as input and expected output pairs where format matters.
7. For fragile multi-step operations, include a copyable checklist and a
   validate-fix-revalidate feedback loop.
8. Never write the em-dash family anywhere (a PreToolUse hook blocks it); use
   colons, commas, or parentheses.

## Priming skills (`prime-*`)

A priming skill opens a session on a workstream: it loads the reference set, injects
current state, restates the working agreements, and hands off. It is orientation,
never method. Current members: `prime-spec-standardization`, `prime-classic-restoration`.

Rules specific to them:

- **`disable-model-invocation: true`.** This is the one sanctioned exception to the
  frontmatter contract above. Priming is an explicit user act; auto-firing it
  mid-conversation dumps a large orientation payload nobody asked for.
- **Point, never copy.** A priming skill must not restate doctrine, method, or
  reference content that lives in a doc or another skill. It names the file and says
  read it. If a rule ends up in two places, the source of truth wins and the priming
  copy is a bug. The only prose it owns is the session protocol, meaning how to work
  in this area, which lives nowhere else.
- **Delegate the method.** Invoke the owning skill (`content-restoration`,
  `spec-standardization`) rather than summarizing it, and include a routing table
  for the neighbouring skills so the agent does not reimplement one.
- **Be target-agnostic.** Never hardcode a zone, folder, or spec family name. Take
  the target as `argument-hint` plus `$1`, discover the valid targets at load time,
  and ask when the argument is missing.
- **Inject state, do not describe it.** Prefer a dynamic-context command over prose
  about where things stand: which patch is open, what is dirty, what shipped last.
  Put anything needing quoting or path resolution in a sibling script
  (`state.sh`) invoked as `` !`bash "${CLAUDE_SKILL_DIR}/state.sh"` ``, so escaping
  happens once in a file instead of through nested shell layers. Keep it read-only
  and fast, and resolve external paths from `.references` inside the script.
- **End with a handshake.** Summarize the understanding, present a scoped proposal,
  change nothing until the user approves.

## Lesson-entry template

Lessons captured into any skill (via `/learn` or manually) use this exact shape,
appended under the target skill's `## Lessons` section, newest first:

```markdown
### <one-line rule, imperative>
- **Date/source:** <YYYY-MM-DD>: <failing command | validation error | audit finding | user correction>
- **Why:** <the failure or observation that proved it>
- **Apply:** <what an agent should do differently, concretely>
```

A lesson that generalizes beyond its skill belongs in a new skill: create it per
this standard.

## Compliance check (run before finishing any skill change)

- [ ] Directory name = intended command, kebab-case
- [ ] `description` third person, "Use when" triggers present, under 1024 chars
- [ ] `disable-model-invocation: false` and `user-invocable: true` present (a `prime-*` skill sets `disable-model-invocation: true`; see Priming skills)
- [ ] Body under 500 lines, references one level deep, forward-slash paths
- [ ] External paths resolved via `.references`, no hardcoded machine paths
- [ ] No em-dash family characters anywhere in the file
- [ ] Lessons carry date + source + why + apply
