# Patch 003 Specs

Guardian Legion field events and targeted content customizations.

Develops against the **closed patch 002 baseline**, per the patch application discipline in
`CLAUDE.md`: each new patch layers on the previous patch's committed datasheet state. Do not
author or apply anything here until patch 002 is fully applied, synced, live-validated and closed
with one commit per datasheet repo.

Zone scope: `reforged/docs/patch-003-scope.md`.
Working plan, phases and acceptance gates: `reforged/docs/plans/classic-restoration/iod/guardian-legion/PLAN.md`.

## What is different about this patch

Patch 003 is the first patch in this project to author **new monster templates**. Nothing under
`reforged/specs/` has ever used the `npcs:`, `ai:` or `npcSkills:` DSL entities, so there is no
working example to copy and every one of them is exercised here for the first time. Treat the
first spec in each of those families as a capability probe, not as content.

The known authoring blockers are recorded in
`docs/plans/classic-restoration/iod/guardian-legion/BACKLOG.md`, seeded from the phase A research
under that plan's `data/` folder. Read the backlog before authoring, not after.

## Numbering Convention

Two-digit prefix controls apply order and groups related specs, matching patches 001 and 002.

| Prefix | Group |
|--------|-------|
| `00-09` | NPC authoring foundation: templates, AI, skills, creature strings, loot tables |
| `10-19` | Guardian Legion field event: territories, Field/FieldEvent, EventDialog, strings |
| `20-29` | Reward and economy wiring for events |
| `30+` | Other content customizations |

Subfolders are walked recursively and sorted by relative path, so a subfolder sorts inside its
prefix band the same way patch 002's `loot/` and `evolutions/` do.

## Binding rules for every spec in this patch

1. **Idempotent upserts only.** Never `create`. A `create` fails on replay, breaks manifest
   generation and silently omits files from server pushes.
2. **Provenance header per spec**: doctrine pointer, source, the research artifact it was derived
   from, and the backlog or decision id that authorized it.
3. **Apply as a whole patch**: `python reforged/tools/migrate/migrate.py --patch 003`. Never
   `dsl apply` a single spec; that replays source-ref and wipes sibling changes on shared files.
4. **New IdSorted client entities require `--no-narrow`.** This patch is expected to add rows to
   existing shards rather than insert new ones, because hunting zone 13 already exists in every
   client family. Re-check before the first sync if that changes.
5. **Two pre-deploy gates, exit 0 required**, per the zone port playbook: `dungeon_audit.py` for
   anything touching a dungeon continent, `audit_class_gates.py` for any restored or changed
   quests.
6. **KB delta before a phase closes.** Any new game-domain knowledge this patch produces goes into
   the `datasheet-domain` KB via `/update-domain-docs`. See doctrine rule 9.

## Spec index

| File | Group | Purpose | Status |
|------|-------|---------|--------|
| `10-iod-field-event-continent.yaml` | GL event | Flips continent 13 to `channelType="field"`. Hard prerequisite: a field event will not run on a continent that is not declared `field`. Must apply before `11` | Moved from patch 002 on 2026-07-28, not yet applied under 003 |
| `11-iod-guardian-legion-v0.yaml` | GL event | The v0 lifecycle probe: one npc, progress bar bound to its HP. Live-validated under patch 002. Superseded in phase 5 by the real three-phase event, kept as the working base | Moved from patch 002 on 2026-07-28, not yet applied under 003 |

Both were authored and live-validated as `002/34` and `002/35`, then moved here on 2026-07-28 so
patch 002 could close on a clean baseline. Patch 002 was reverted and replayed without them; the
server and client trees currently carry **no** Guardian Legion content.

**Known client-side gap carried with `10`.** The continent flip is spec-driven on the server but
was a HAND EDIT on the client, because `continentDatas` is quarantined to `None` in migrate's
`ENTITY_SYNC_MAP`. The DSL fix has since landed (`3976613a`); lifting the quarantine and proving
it with an attribute-level diff is register row `GL-P04`. Do that before re-applying `10`, or the
hand edit has to be repeated.
