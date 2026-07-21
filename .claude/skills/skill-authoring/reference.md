# SKILL.md Frontmatter Reference

Complete field list per the official Claude Code docs
(code.claude.com/docs/en/skills, verified 2026-06-11). The `/command` name always
comes from the skill directory name; the `name` field is a display label only.

## Fields

| Field | Type / values | Semantics |
|---|---|---|
| `name` | string, max 64 chars, `[a-z0-9-]` | Display name. Defaults to directory name. Must not contain "anthropic"/"claude". |
| `description` | string, max 1024 chars | What the skill does + when to use it. Pre-loaded into the system prompt at startup; drives model auto-invocation. Third person. |
| `when_to_use` | string | Extra trigger context appended to `description` in the skill listing (combined cap 1536 chars). |
| `argument-hint` | string, e.g. `"[file] [format]"` | Autocomplete hint for expected arguments. |
| `arguments` | space-separated string or YAML list | Named positional arguments; each becomes `$name` in the body. |
| `disable-model-invocation` | bool, default `false` | `true` = manual `/invoke` only; description removed from model context. Use for side-effect workflows. |
| `user-invocable` | bool, default `true` | `false` = hidden from `/` menu; model-only background knowledge. |
| `allowed-tools` | string or list, e.g. `Bash(git add *)` | Tools usable without permission prompts while the skill is active (grants, not restrictions). |
| `disallowed-tools` | string or list | Tools removed from the pool while active; clears on next user message. |
| `model` | model id or `inherit` | Model override for the rest of the current turn. |
| `effort` | `low` to `max` | Effort override for this skill. |
| `context` | only `fork` | Run in an isolated forked subagent context; SKILL.md body becomes the subagent prompt. Not used in this project. |
| `agent` | `Explore`, `Plan`, `general-purpose`, or custom agent name | Execution environment when `context: fork`. `Explore` skips CLAUDE.md/git status. |
| `hooks` | hook map (`PreToolUse:` ...) | Hooks scoped to this skill's lifecycle. |
| `paths` | comma-separated globs or list | Auto-activate only when working with matching files. |
| `shell` | `bash` (default) or `powershell` | Shell for dynamic-context commands in the body. |

## Body substitutions

| Placeholder | Expands to |
|---|---|
| `$ARGUMENTS` | All invocation arguments (appended as `ARGUMENTS: <value>` if absent from body). |
| `$ARGUMENTS[N]` / `$N` | 0-based positional argument. |
| `$<name>` | Named argument from `arguments`. |
| `${CLAUDE_SKILL_DIR}` | Absolute directory of this SKILL.md (cwd-independent). |
| `${CLAUDE_SESSION_ID}` | Current session id. |
| `${CLAUDE_EFFORT}` | Current effort level. |
| `` !`cmd` `` or a ```` ```! ```` block | Shell command executed before the body reaches the model; output replaces the placeholder. |
| `\$` | Literal dollar sign before digits/ARGUMENTS/argument names. |

## Loading model (token budgeting)

- Startup: every skill's `name` + `description` enter the system prompt.
- Invocation (model- or user-triggered): full SKILL.md body loads and stays in
  context for the rest of the session.
- Sibling files: zero cost until the model reads them; this is the progressive
  disclosure mechanism. Give them descriptive names and a table of contents when
  over 100 lines.
- Live reload: edits under `.claude/skills/` take effect within the current
  session, no restart (a brand-new top-level `.claude/skills/` dir requires one).

## Precedence and conflicts

Enterprise, then Personal (`~/.claude/skills/`), then Project (`.claude/skills/`).
Plugin skills are namespaced (`plugin:skill`) and cannot conflict.
