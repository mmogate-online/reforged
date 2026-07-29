# Patch 002 (Reforged Customizations) Zone Scope

This document defines the complete set of zones in scope for patch 002 content development (custom progression, loot economies, balance tuning).
Research, loot table work, merchant audits, and NPC queries for patch 002 must include **all zones listed here**, not just hunting zones.

## Island of Dawn

Patch 002 layers custom loot/balance on top of the patch 001 baseline. See `patch-001-scope.md` for the full five-layer zone breakdown.

| Zone ID | Name | Type |
|---------|------|------|
| 13 | Island of Dawn | channelingZone |
| 436 | Karascha's Lair | dungeon |

## Hunting Zones (Open World)

| Zone ID | Name |
|---------|------|
| 2 | Fey Forest |
| 3 | Oblivion Woods |
| 5 | Tuwangi Mire |
| 6 | Valley of Titans |
| 7 | Celestial Hills |
| 15 | Cliffs of Insanity |
| 16 | Vale of the Fang |
| 17 | Paraanon Ravine |

## Hub Cities

| Zone ID | Name |
|---------|------|
| 59 | Crescentia |
| 60 | Lumbertown |
| 63 | Velika |

## Dungeons

| Zone ID | Name |
|---------|------|
| 487 | Bastion of Lok |
| 488 | Sinestral Manor |

## Scope expansion: reward-vector wave (added 2026-07-28)

Patch 002 now also carries the reward-vector wave scoped in `docs/plans/reward-vectors/`. The wave was originally planned for a later patch lane; it folds into patch 002 instead because every affected row exists only in the dirty working tree, so a replay simply never writes them and no delete op is needed (backlog ruling R16).

**This part of the scope is not zone-bounded.** The feedstock flattening (backlog R15/R18/R19, work item RV-28) is a corpus-wide change:

- 4,620 feedstock references across **117 files**, decomposing to 1,991 record-level ops, of which 1,469 are `ECompensation` mob loot tables spread over 96 hunting zones.
- Roughly **8,439 items carry a feedstock-consuming enchant link**, of which only **1,342 fall inside the Island of Dawn band**.

So a research pass, an audit or a regression diff for this part of patch 002 must be run over the whole corpus, not over the zone tables above. The zone tables still bound the rest of patch 002 (custom progression, loot economies, balance tuning).

Authority for the design decisions, the per-family migrate-versus-delete calls and the measured corpus figures: `docs/plans/reward-vectors/IOD-BACKLOG.md` (rulings in section 1, work items in sections 3 and 5, measured facts in section 4.10). Do not restate them here.
