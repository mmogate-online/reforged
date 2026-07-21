---
name: learn
description: >
  Captures a lesson learned into the project skill library and curates it. Use
  after resolving a pipeline trap (apply, sync, pack, deploy), a DSL authoring
  mistake, an MCP query pattern worth reusing, or a tooling quirk, when the user
  corrects the same behavior twice, or at session end when knowledge was gained
  that future agents would otherwise rediscover the hard way. Routes domain
  knowledge to update-domain-docs and DSL bugs to docs/dsl-requests instead.
  Invoke with "curate" to sweep the skill library for stale or duplicate entries.
argument-hint: "[one-line lesson, or 'curate']"
disable-model-invocation: false
user-invocable: true
---

# Capture a Lesson

Encode the following lesson so no future agent repeats the mistake:

> $ARGUMENTS

If the argument is `curate` (or empty at session end with no single lesson), skip
to the Curate section below. Otherwise copy this checklist and work through it:

```
- [ ] 1. Establish provenance
- [ ] 2. Read the authoring standard
- [ ] 3. Route the lesson
- [ ] 4. Write the entry (or new skill)
- [ ] 5. Compliance check + report
```

**Step 1: Establish provenance.** A lesson without evidence is an opinion.
Identify the concrete source: failing command output, validation error, audit
finding, MCP query result, or user correction. If the conversation does not
contain it, find it before writing anything.

**Step 2: Read the authoring standard.** Read
`.claude/skills/skill-authoring/SKILL.md`; the lesson-entry template and
compliance checklist there are binding.

**Step 3: Route the lesson.** Not everything belongs in the skill library. Check
these destinations in order:

| Lesson is about | Destination |
|---|---|
| Game entity systems, schemas, attributes, ID ranges, datasheet structure | Invoke `update-domain-docs`; domain docs are the source of truth, not skills |
| DSL bug or missing feature | Log in `docs/dsl-requests/YYYY-MM-DD-<topic>.md` per CLAUDE.md; do not encode workarounds as permanent rules without noting the pending request |
| Design intent, balance, economy, framework invariants | The content framework repo owns it; use that repo's own authoring skills, do not duplicate design decisions here |
| Spec YAML structure, operations, imports, idempotency | `new-spec` |
| Validate, apply, sync, pack, deploy pipeline behavior | `apply-spec` (or the deploy workflow doc the lesson concerns) |
| Package structure, exports, registration | `create-package` |
| Research routing, source selection, MCP tool usage patterns | `domain-research` |
| Progress logging thresholds and format | `log-progress` |
| Writing skills themselves | `skill-authoring` |

Only when no existing scope fits and the lesson describes a repeatable workflow
or a durable body of project knowledge: create a new skill per the standard.
One-off trivia does not earn a skill.

**Step 4: Write the entry.** First check the target skill's `## Lessons` section
for an entry covering the same ground: update it (refine the rule, add the new
source) rather than appending a near-duplicate. If the lesson contradicts the
skill's body guidance, fix the body; do not append a contradicting lesson below
stale advice. Otherwise append under `## Lessons` (create the section if the
skill lacks one), newest first, using the exact template from the authoring
standard (rule / date+source / why / apply). Keep the rule imperative and the
apply line actionable by an agent that has read nothing else.

**Step 5: Compliance + report.** Run the authoring-standard compliance checklist.
Report back: target skill (or destination), the entry as written, and whether it
updated, created, or rerouted.

## Curate

Sweep the library and tighten it. For each skill in `.claude/skills/`:

1. **Duplicates:** merge `## Lessons` entries that state the same rule; keep the
   strongest source.
2. **Contradictions:** where a lesson and the body disagree, the newer evidence
   wins; rewrite the body and delete the superseded entry.
3. **Promotion:** a lesson that has held up and shapes routine work moves into
   the body as a rule; delete the entry after folding it in.
4. **Staleness:** verify lessons that reference files, tools, commands, or paths
   still match reality (resolve via `.references`, check the file exists); delete
   or rewrite entries that no longer apply.
5. **Descriptions:** confirm each skill's `description` still matches its body
   and carries the trigger keywords an agent would think of; sharpen if drifted.
6. **Overlap between skills:** if two skills now cover the same ground, merge
   into the better-named one and delete the other.

Run the compliance check on every file touched. Report a summary: entries merged,
promoted, deleted, and skills changed. Deleting a skill or large sections is
destructive: list what would be removed and confirm with the user first.
