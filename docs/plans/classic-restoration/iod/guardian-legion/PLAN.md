# Guardian Legion: Plan

The contract for the Guardian Legion authoring wave. Stable document: objectives, phases and
acceptance gates. It should change rarely.

- **Where we are now**: `TRACKER.md` (volatile, rewritten every session)
- **Every test, failure and attempt**: `BACKLOG.md` (the register)
- **Frozen research evidence**: `data/` (dated, cited, do not edit)
- **Patch**: 003. Scope `docs/patch-003-scope.md`, specs `specs/patches/003/`

## Objective

Ship a three-phase Guardian Legion field event on Island of Dawn, fought against three purpose
built Orcan monsters, with lore grounding, working sequencing, and a reward that is actually
reachable at the zone's level band.

This is **AUTHORED content**, doctrine rule 4 Level 2 (contextual additions, design-first). Field
events do not exist before v92 in any source we hold, so there is no classic event to restore, no
precedent for tuning, and no era-authentic reward table. Every design decision needs explicit user
approval and a row in `../divergence-log.md` labelled AUTHORED.

## The organising constraint

**The unit of cost is the world restart, not the probe.** Restarts are manual, they belong to the
user, and they serialize everything. The register currently holds 26 open items. Run one per boot
that is 26 restarts; batched properly it is two or three.

Two rules follow, and they shape every phase below:

1. **Drain everything answerable without a restart first.** Roughly half the register needs no
   server at all: scratch-datasheet applies, sync dry-runs, reference integrity checks.
2. **Probe in descending order of blast radius.** The monster-authoring probes gate every spec we
   would write. The field event mechanic probes gate none of the monster work. They are
   independent tracks and must not be sequenced behind each other.

## Phases and acceptance gates

A gate is binary and checkable. If it can be argued about, it is not a gate.

### Phase 0: scaffold

**Objective.** Patch 003 exists as an addressable unit with its scope, plan, register and
conventions written down, so a cold session can resume without reconstructing context.

**Gate.**
- `specs/patches/003/README.md` and `docs/patch-003-scope.md` exist
- `PLAN.md`, `BACKLOG.md`, `TRACKER.md` exist under this folder
- The register is seeded with every known unknown from phase A research
- `iod/TRACKER.md` points at this plan, so priming on `iod` surfaces it
- Nothing applied, nothing deployed

### Phase 1: deskbound de-risking

**Objective.** Resolve every unknown that does not need a running server, so the first restart is
spent on questions that genuinely require one.

**Work.** Register batch 0: `GL-P01` to `GL-P10`. The `npcSkills:` scratch probe, the sync
dry-runs including the new `W604` and `W605` sweep, the ContinentData attribute diff, and the
three reference integrity checks on the donor's script, formation and message ids.

**Gate.**
- Every batch 0 row is `PASS`, `FAIL` with a recorded cause, or `FILED` as a DSL or MCP request
- `GL-P01` has produced a decision: author skills natively, or clone a donor set, with the reason
- The `NpcData` / `AIData` / `StrSheet_Creature` client sync question has a decided path, not an
  open question
- No spec applied to the server datasheet

**Why this gate matters.** `GL-P01` decides whether the boss can have a bespoke skill set at all.
`npcSkills:` cannot express `parentId`, which sits on 98.0 percent of the 179,580 skill rows in
the corpus. If the emitted skill is unusable without it, the whole tier 3 design changes shape.

### Phase 2: monster capability proof

**Objective.** Prove the project can author a working monster end to end, using one throwaway
template, before committing to three.

**Work.** First spec in `specs/patches/003/`, restart batch 1: `GL-P11` to `GL-P14`.

**Gate.** The user's own stated criteria, verbatim, on a single authored template:
- It spawns via `/@spawnnpc`
- It renders at the intended `scale`
- It draws a correct nameplate with the intended display name
- It fights, and uses at least one skill from **its own** skill rows
- It drops loot from **its own** compensation entry
- Both audit gates exit 0
- The KB delta for anything learned is written

**Why a throwaway first.** Three monsters authored against an unproven pipeline means a failure
cannot be localised. One monster is one variable.

### Phase 3: the three monsters

**Objective.** Author the minion, raider and boss from their donors, each validated individually
before any event wiring.

**Donors, from `data/orcan-npc-donor-survey.md`:**

| Tier | Template | Donor | Scale |
|---|---|---|---|
| Minion | `13,2001` | `13,4` Dwarf Orcan, in zone, already level 7 tuned | 0.5 |
| Raider | `13,2002` | `87,2031`, the only same-model Orcan with a `Cooperation` work list | 0.21 |
| Boss | `13,2003` | `620,1005`, elite, large, carries field event skill `1303` | 0.41 |

**Gate.**
- Each of the three passes the phase 2 criteria individually
- The boss visibly reads as elite beside the zone's existing Orcans
- No dangling reference: every `aiid`, `activeMove` id, formation id, script id and `msg` id
  referenced by a copied donor resolves in zone 13, or was deliberately dropped
- Both audit gates exit 0
- KB delta written

**Why individually.** Stated user instruction, and it is right: the world server emits no runtime
logging for field events, so a mob debugged inside an event is debugged blind.

### Phase 4: field event mechanics probe

**Objective.** Answer the twelve open mechanic questions with a throwaway probe event, so the real
event is authored against measured behaviour rather than inference.

**Work.** Register batch 2: `GL-P15` to `GL-P26`. A disposable `FieldData` event whose only job is
to answer questions, driven by the GM kit.

**Gate.**
- Every batch 2 row is `PASS`, `FAIL` with cause, or `DEFERRED` with a stated reason
- The progress ladder is confirmed: `killCount` fires once per integer in its range
- `dividerPercent` is confirmed cosmetic or not
- KB delta written

**Why a probe event.** Twelve questions inferred from shipped data, several from arithmetic rather
than observation. One disposable event answers most of them in one boot.

### Phase 5: the three-phase event

**Objective.** Author the real event: swarm near the camp, raider wave further out, boss at the
Orcan Bivouac, staging point advancing each phase.

**Recipe.** `data/fieldevent-multiphase-reference.md` section 4: 18 trigger groups, a 20/30/50
progress budget, the `13017xxx` territory band, and the world takeover despawn and restore
ordering.

**Gate.**
- Applies clean in a full patch run, op counts reconciled against the intended op list
- Both audit gates exit 0
- A player runs all three phases end to end live, and each phase advances the staging point
- The world takeover restores every despawned world territory at teardown, verified by count
- KB delta written

### Phase 6: reward calibration

**Objective.** Make the participation bag reachable.

**The problem.** A global `EventPoint defaultRate="0.001"` multiplies every event. Our 1.45
coefficient becomes 0.00145 points per damage, so a 100000-point bag needs 69 million damage,
about 200,000 level 8 kills. The live measurement and the arithmetic agree exactly.

**Gate.**
- Measured points per kill matches prediction within a stated tolerance
- One participation bag is reachable in a stated number of runs, and that number is the user's
  ruling, not an assumption
- `FieldEvent.xml` `defaultRate` is untouched, because it is global to all 16 shipped events
- KB delta written

### Phase 7: close

**Gate.**
- Every AUTHORED design decision has a row in `../divergence-log.md`
- The KB carries everything this wave learned about field events
- `/log-progress` run
- One commit per datasheet repo, only after the user confirms live

## Standing rules

Inherited, not restated: `../DOCTRINE.md` for the source hierarchy and the AUTHORED boundary,
`../../ZONE-PORT-PLAYBOOK.md` for pipeline traps, `specs/patches/003/README.md` for spec
conventions, and `CLAUDE.md` for the patch application discipline and the public-repo rule.

Two that bite this wave specifically:

- **Live validation belongs to the user.** An agent can prove a file is correct and deployed. Only
  the user can prove the content works. A clean apply is never a report that content works.
- **The datasheet trees are generated output.** A hand edit there is a temporary probe for proving
  a gap, never an artifact to defend.
