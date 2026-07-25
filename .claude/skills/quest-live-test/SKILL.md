---
name: quest-live-test
description: >
  Verify an applied quest change in the running game using QA slash commands,
  by deriving checkpoints from the spec diff instead of just replaying the
  quest. Covers the reset protocol, which GM shortcut silently skips which
  change, and the preconditions that produce false passes. Use after deploying
  any quest spec (tasks, prerequisites, rewards, start items, journal strings)
  when it needs live confirmation, when a quest must be re-run on a character
  that already completed it, or when a live test reports a quest behaving
  unexpectedly and it must be narrowed to a specific spec op.
disable-model-invocation: false
user-invocable: true
argument-hint: "[questId]"
---

# Quest Live Test

Protocol for confirming a deployed quest change in game. The command surface
itself is documented in the domain knowledge base at
`server-setup/gm-commands.md` (resolve `domain_docs` from `.references`); read
it for the full QA command list. This skill covers how to USE those commands so
the test actually proves something.

## Binding method: derive checkpoints from the spec, not from the quest

Never test by "playing the quest and seeing if it works". Open the spec that was
applied, and for every operation in it produce a row:

| Spec op | In-game observable | What failure means |
|---------|-------------------|--------------------|

Each row must name a DISTINCT observable. If two ops collapse to the same
observable, the test cannot tell them apart and one is unverified.

Worked example (`17-iod-charm-quest-dedup.yaml`, 2026-07-20):

| Spec op | Observable | Failure means |
|---------|-----------|---------------|
| 1384 task 2 `nextTaskId: 6` | Quest goes straight to wrap-up | Rewiring did not take |
| 1384 task 2 `completionItems` = campfire only | NPC hands campfire, no charm | List-replace did not take |
| 1384 compensation `7103 x2` | Reward is Onslaught Charm IV x2 | QuestCompensationData not live |
| 1385 `header.startItems` `7103` | Charm IV count +1 **on accept** | startItems did not land |
| 1385 task 1 `conditionItemId: 7103` | Using a Charm IV completes the task | Task body not live |
| questStrings 1385002/1385004 | Journal reads the new text | Client sync did not reach the client |

## Shortcuts skip the thing you changed

This is the trap that produces confident false passes. Every fast path forfeits
a checkpoint:

| Command | Skips | Do not use it to verify |
|---------|-------|-------------------------|
| `/@start_quest [id]` | Giver trigger, prerequisites, level band | `giverNpc`, `prerequisites`, `minLevel`, `autoAccept` changes |
| `/@jump_task [id] [taskId]` | Quest accept, and everything before that task | `startItems`, earlier task wiring, `nextTaskId` chains |
| `/@complete_all_quest` | Essentially all logic | Anything |
| `/@task_goal` | The task's own completion condition | The condition you edited |

Rule: **accept from the NPC and walk the chain** whenever the change touches
accept-time or chain wiring. Reserve shortcuts for re-hitting a single
mid-chain step you have already validated end to end once.

Real case: `/@jump_task 1385 1` completed cleanly and proved nothing about that
quest's start item, because the item is granted at accept, which the jump
skipped. Caught only because the spec diff listed a start-item op with no
matching observable.

## Reset protocol

```
/@clear_quest [questId]        one id at a time
```

Clear the whole affected chain, deepest dependant first, then re-accept from
the giver NPC. Clearing order is not load-bearing; re-accept order is, since a
prerequisite must be complete before its dependant is offered.

Pass only the single-id form. The command is documented as
`/@clear_quest [questId] [all]` and the `all` variant's scope is unspecified.

## Preconditions that cause false results

- **Server restart.** Datasheets load at world-server startup only. Verify the
  restart happened before trusting any result. Restarts are the user's manual
  step. The `/@reload_*` command family exists in the vanilla reference but is
  UNVERIFIED on this build; do not assume it applies changes. If the restart did
  not bring the world up at all, switch to the `server-load-diagnosis` skill: a
  deployed datasheet can crash the loader silently.
- **Inventory baseline.** Before testing an item grant, zero out the item on the
  character. Leftovers from earlier attempts make a grant unobservable, and a
  wrong-item grant (Charm I vs Charm IV) indistinguishable from a right one.
- **Class gates.** A quest with a `<클래스>` block only appears for those
  classes. Check the requirement block before concluding a chain is broken. IoD
  1383 "Gathering Your Strength" is Sorcerer/Priest/Elementalist only, so it
  will never appear on a Slayer, and that is correct behavior.
- **GM invisibility.** A GM-flagged character is invisible and cannot damage
  monsters. Run `/@set_go off` (Arbiter in QA mode) before any kill task.
- **Client-side changes need the client shipped.** Journal text, popups, and
  task strings live in the client DataCenter. If a string still reads the old
  value, suspect the client build before suspecting the spec: confirm the
  packed `.dat` was installed and the published release is the one running.

## Reporting

A result is only useful if it names which checkpoint passed. "The quest worked"
does not distinguish a real pass from a shortcut that skipped the change. Report
per-row, and treat any row with no observation as still unverified.

## Lessons

### A quest that is not offered may be level-capped, not broken; check 최대레벨 first
- **Date/source:** 2026-07-21: user reported the enabled repeatable 1334 "did not land" from its giver; the enable, giver spawn, and collect nodes were all verified correct, and the actual cause was the body's `<최대레벨>10</최대레벨>` with a level 11+ test character.
- **Why:** quests with a max-level condition show NO marker and no greyed entry; the offer is silently withheld, which is indistinguishable in-game from a broken enable.
- **Apply:** before diagnosing a missing quest offer, read the live quest header's 최소레벨/최대레벨 band and compare with the test character's level; test age-capped quests on a character inside the band (or state the cap in the checklist so the tester picks the right character).

- 2026-07-20: `/@jump_task` past a quest accept silently skips `startItems`
  verification. The jump succeeded and the quest completed; the start item was
  still the old id. Derive checkpoints from the spec diff so a skipped op has a
  visibly empty result rather than an implied pass.
- 2026-07-20: an unchanged reward on the quest under test proves nothing about
  whether `QuestCompensationData` is live. Pick the quest whose reward actually
  changed as the discriminator (1384's `7100 -> 7103`, not 1385's unchanged
  50xp/5g).
