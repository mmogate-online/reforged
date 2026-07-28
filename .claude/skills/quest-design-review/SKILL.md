---
name: quest-design-review
description: >
  Review dimensions and deterministic checks to apply when authoring a new quest
  or changing an existing one: rewards, prerequisites, task sequence, objective
  targets and counts, level gates, quest enabling or retiring, or moving a reward
  between quests. Use when writing or editing a quest spec, when trimming or
  disabling quests, when changing what a quest grants or how much, when adding or
  removing an objective target, when changing spawn density for a quest
  objective, or when restoring classic quests, re-enabling sentinel-disabled
  quests, or filling empty quest rewards from v31.
disable-model-invocation: false
user-invocable: true
argument-hint: "[zone ids] [quest ids]"
---

# Quest Design Review

Quests fail review as a SYSTEM, not one at a time. Two quests can each be valid
and still grant the identical reward at the identical payout; a gear set can be
granted piece by piece and still be uncompletable; an objective can have a legal
target count and still demand more items than the zone can drop. None of that is
visible in a spec diff, and none of it is caught by `dsl validate`.

Most of it is computable. Run the tool, then spend your judgment on what the tool
cannot decide.

## 1. Run the tool

```bash
python reforged/tools/dc-restore/audit_quest_design.py --zones <zones> --quests <ids>
python reforged/tools/dc-restore/audit_quest_design.py --zones <zones> --since HEAD
python reforged/tools/dc-restore/audit_quest_design.py --zones <zones> --json      # for agents
python reforged/tools/dc-restore/audit_quest_design.py --list-checks               # current inventory
python reforged/tools/dc-restore/audit_quest_design.py --zones <zones> --report    # descriptive tables
```

`--zones` is the SUBJECT scope and is required. Always pass every layer of a
multi-zone map: Island of Dawn is 13, 64, 213, 313, 364 plus dungeon 436, never
just the combat hunting zone.

`--quests` (or `--since`) is the FINDINGS scope: it marks which findings are NEW.
Pass the quests you touched. Without it, every pre-existing condition in the zone
is reported as if you had just introduced it, and the real signal drowns.

Evidence is always corpus-wide and is not affected by `--zones`. That is
deliberate: set completeness must see every granting quest in the game, and no
trim can be proven safe against a zone-scoped view of inbound references.

**Do not restate the check list here or anywhere else.** `--list-checks` is the
inventory, in machine-readable form, and it is generated from the registry. A
copy in prose is wrong the first time a check is added.

## 2. The advisory contract

The tool always exits 0 and never prints the word PASS. Read the terminal line:

```
ADVISORY: 47 findings (2 new, 1 waived)
```

- **A clean run is not approval.** It means the deterministic checks found
  nothing, which is a much smaller claim than the change being good.
- **A NEW finding needs a decision, not a dismissal.** Either fix it, or add a
  waiver entry with a reason to `reforged/config/quest-design-waivers.yaml`.
- **A waiver without a reason is ignored by the loader** and the finding keeps
  reporting. That is intentional: a reasonless waiver is indistinguishable from
  nobody having looked.
- **Severity is confidence, not importance.** `high` means the signature marked a
  real defect every time it fired. `info` means the fact is legitimate about as
  often as not, and is reported so you can see it.

Pre-existing findings are not your problem unless you are the one changing that
content. There is no retrofit wave; the tool exists so that new work is reviewed
properly.

## 3. What the tool cannot decide

Spend your review here, because nothing else will:

- **Narrative and theme fit.** Whether this reward, giver, or objective belongs
  in this story beat.
- **Whether a duplication is deliberate.** The tool reports that two sources
  grant one item. Whether that is a copy-paste or a design choice is a ruling,
  and the waiver file is where rulings are recorded.
- **Tuning values.** The tool reports that a quest asks for 8 items from a
  population expected to yield 6.1. Whether the answer is a lower count, a wider
  accept list, or more spawns is design.
- **Whether distance is a flaw or the point.** A migration quest is supposed to
  be long. The set-placement report gives you the geometry, not the verdict.
- **Whether a quest should exist at all.**

## Worked examples

Every check exists because it caught something real. The incidents, how they were
found, what the fix was, and which check now covers each one:
[reference/case-studies.md](reference/case-studies.md).

## Related

- `/apply-spec` for validating and applying the spec itself.
- `/quest-live-test` for confirming the change in the running game afterwards.
- `/domain-research` for what exists and how it is encoded.
- The content framework (`content_framework` in `.references`) for why and how
  much: reward budgets, pacing, currency separation.
