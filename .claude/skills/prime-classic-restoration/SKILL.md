---
name: prime-classic-restoration
description: >
  Session bootstrap for classic-restoration work on any plan folder under
  docs/plans/classic-restoration/ (a zone like iod, or a theme like
  crafting-restoration). Loads the doctrine and zone-port playbook, the target's
  tracker and divergence log, and a live snapshot of the three working trees,
  then restates the session protocol: whole-patch applies, the binding pre-deploy
  gates, generated-tree discipline, commit lanes, and user-owned live validation.
  Use when starting or resuming restoration, padding, or quest-polish work on a
  zone or theme, when the user invokes /prime-classic-restoration, or before
  authoring specs against a restoration plan folder.
argument-hint: "[plan folder, e.g. iod]"
disable-model-invocation: true
user-invocable: true
---

# Prime: Classic Restoration Session

Open a restoration session with the doctrine, the target's state, and the working
agreements already in context. This skill primes and choreographs only. The method
lives in [content-restoration](../content-restoration/SKILL.md); the rules live in
`docs/plans/classic-restoration/DOCTRINE.md`. Nothing here restates either: if a
rule appears in both places, the doctrine wins and this file is the bug.

## Current state (injected at load)

```!
bash "${CLAUDE_SKILL_DIR}/state.sh"
```

## 1. Select the target

Target requested: `$1`

If empty, ask which plan folder to work in, listing the ones above with their
tracker status. Change nothing until the user names one. Everything below is
relative to `docs/plans/classic-restoration/<target>/`.

A target is a zone (`iod`) or a cross-zone theme (`crafting-restoration`). Both
follow the same doctrine; only a zone target has per-zone `data/` diff artifacts.

## 2. Read the shared layer

- `docs/plans/classic-restoration/DOCTRINE.md`: source hierarchy, the rules, the
  mechanical-adaptation whitelist, the per-zone pipeline phases, the divergence
  log convention.
- `docs/plans/classic-restoration/ZONE-PORT-PLAYBOOK.md`: the repeatable port
  procedure.

## 3. Read the target layer

- `<target>/TRACKER.md`: read the Current state and Next sections first. The phase
  log at the bottom is long history; read it only when the current work needs it.
- `<target>/divergence-log.md`: every deliberate deviation from the source and its
  category. A change that adds one belongs here before it is called done.
- `<target>/data/`: list it, do not read it wholesale. These are generated diff and
  audit artifacts; open the one the task needs.

## 4. Load the method and its neighbours

Invoke `content-restoration` and follow its pipeline. Route to the other skills
rather than reimplementing them:

| Need | Skill |
|---|---|
| Restore pipeline, dc-restore tools, commit lanes, deploy | `content-restoration` |
| Where does this game knowledge live | `domain-research` |
| Author a spec | `new-spec`; `spec-standardization` for repeated blocks or hardcoded ids |
| Validate and apply a spec | `apply-spec` |
| Verify a quest change in game | `quest-live-test` |
| World server dies or hangs after a deploy | `server-load-diagnosis` |
| Record finished, validated work | `log-progress` |
| Capture a trap so it is not rediscovered | `learn` |

## 5. Hold the session protocol (non-negotiable)

- **Apply whole patches only.** `python reforged/tools/migrate/migrate.py --patch NNN`,
  never a hand-picked subset. Add `--no-narrow` whenever the patch adds a new
  `IdSorted` client entity (`Quest`, `QuestDialog`), because the narrowed sync
  cannot place a new shard (E680).
- **Two pre-deploy gates, exit 0 required.** `dungeon_audit.py --dungeons <contId>`
  for anything touching a dungeon continent; `audit_class_gates.py --zones <zones>`
  for any restored or re-enabled quests. The second exists because a faithful
  restore inherits the source era's class roster, so classes added later match no
  variant and the content is offered to nobody, silently, with both sources
  agreeing.
- **The datasheet trees are generated output.** Everything dirty in them must be
  reproducible by applying the patch. A hand-edit there is a temporary probe for
  proving a DSL gap; never pause an apply or deploy to protect one, and never
  treat one as an oracle beyond the single comparison it was made for. Removing an
  op does not revert the file it already wrote: `git checkout --` those files and
  re-derive.
- **Commit lanes.** Restored canonical content is the baseline lane, committed only
  after the user validates it live. DSL patch commits are the user's. Never commit
  the datasheet repos mid-patch.
- **Live validation belongs to the user.** The world server loads datasheets at
  startup only and the restart is manual. An agent can prove a file is correct and
  deployed; only the user can prove the content works. Do not report content as
  working on the strength of a clean apply.
- **DSL gaps are requests, not fixes.** File in `docs/dsl-requests/` as
  `YYYY-MM-DD-<topic>.md` and design around the gap.
- **Resolve every external path from `.references`.** Never write a machine path
  into a spec, doc, tool, or command: this repository is public.

## 6. Handshake before editing

Summarize, in a few lines: the target, where its tracker says the work stands, what
is uncommitted, and what you believe the next unit of work is.

Then:
- If the invocation named a task, present a scoped proposal (what you will read or
  audit first, what you expect to change, which gates you will run, what the live
  test would be). Change nothing until the user approves.
- If it did not, ask what to pick up, offering the tracker's Next items.
