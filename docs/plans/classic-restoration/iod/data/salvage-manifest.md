# IoD Patch 001 Salvage Manifest (v31-primary redo)

Phase 1 disposition pass over the 19 retired patch-001 spec YAMLs in
`temp/patch-001-v17-reference/`. Doctrine: `docs/plans/classic-restoration/DOCTRINE.md`
(v31-primary, adopted 2026-07-20). Verdict definitions:

- **CARRY-OVER**: still valid verbatim; may need renumbering only.
- **REWORK**: the concern survives but content must be regenerated from v31-vs-v92 diffs.
- **RETIRE**: v17-flavored, superseded by the v31 port.

## Verdict counts

| Verdict | Count | Specs |
|---------|-------|-------|
| CARRY-OVER | 7 | 08, 10, 11, 14, 15, 16, 18 |
| REWORK | 9 | 00, 01, 04, 05, 06, 07, 09, 12, 13 |
| RETIRE | 3 | 02, 03, 17 |

## Disposition table

| Spec | Verdict | Reason (short) |
|------|---------|----------------|
| 00-iod-region-strings | REWORK | 13036 is a v17/v92 id-reconciliation artifact (NEW id because v31's row = nameId 13013). Port full continent-13 region strings from v31; re-derive the id remap from the diff. |
| 01-iod-area-sections | REWORK | Header rule "v17 client geometry WINS on disagreement" violates v31-primary. Regenerate with v31-only geometry. Generator + `area-section-standard` package survive. |
| 02-iod-spawn-restore | RETIRE | Restores 17 v17-ONLY groups (HZ 13, absent from v31) with v17 fences. These are phase-7 padding candidates per doctrine rule 4, not v31 baseline. Generator survives for the v31 spawn port. |
| 03-iod-spawn-removals | RETIRE | Removals driven by "absent from v17 roster" (deletes v31 groups v31-primary must KEEP) and v92 live-state dedup. The v31 wipe-and-replace generates its own delete set from the diff. |
| 04-iod-shops | REWORK | Content is a v17-registry-SCOPED v31 dump. Port the full v31 IoD shop set; re-evaluate decisions 20/21/22 + T-cat against the v31 diff. Generator survives. |
| 05-iod-quest-rewards | REWORK | Header: "v31 rewards are NOT the value source" (only 10/63 match); values are v17 verbatim. v31-primary requires v31 reward values. New-class bag extension survives as adaptation-whitelist #2. |
| 06-iod-quest-tasks | REWORK | Task target is v17.11 client shards. Port v31 .quest task trees 1:1. Watch 1384 task 3 (stamina mechanic) for adaptation. Generator survives. |
| 07-iod-story-groups | REWORK | Membership/order are v17.11-authoritative REPLACE-ALL. Port v31 QuestGroupList membership/order (v31 group 1 differs). Generator survives. |
| 08-legacy-strings-restore | CARRY-OVER | Global item-economy string repair (207 mats + 873 designs), not IoD-scoped. Verified still needed (v92 item 501 still "no longer usable"). Already v31-sourced. |
| 09-iod-quest-enable | REWORK | v17-driven prereq clears / autoAccept / NPC-accept overrides. Regenerate enable-state from v31 headers. **Must NOT re-enable 1385** (that re-enable created the spec-17 problem). Generator survives. |
| 10-iod-stepstone-disable | CARRY-OVER | Policy divergence. Quest 59901 verified v92-ONLY (absent from v31). Deliberate REMOVE of a v92-only row; log in divergence log (category: policy). |
| 11-iod-villager-dialogs | CARRY-OVER | speechConditions read straight from v31 `.condition` files (deterministic). Per-op: re-derive the exclusion list from the v31 spawn set. Generator survives. |
| 12-iod-spawn-script-fixes | REWORK | Ramun pos [80672,-81177,-4409] is a packet-capture value, NOT v31 (v31 = [80798.73,-80691.16,-4433.67]). Port v31 position; the displacement fix re-derives only if it reproduces live. |
| 13-iod-worldmap-town | REWORK | Op 1 (Tower Base town section) is COVERED by v31 (NewWorldMapData line 96, section 6 live). Ops 2-3 (9034/9053 sync-compat) survive as salvaged E650 fixes if v92 still fails. |
| 14-charm-abnormalities | CARRY-OVER | Adaptation-whitelist #1 (charm support). Required by the v31 1384 lineage. User decision: charms stay in patch 001. |
| 15-charm-items | CARRY-OVER | Flips 7100 (Onslaught Charm I) to usable - REQUIRED by v31 1384 (grants/uses 7100). Per-op: review the extraneous 70033 op (v31 uses 7100, not patch-000's 70033). |
| 16-charm-skills | CARRY-OVER | Injects the buff TargetingList into charm skill 60240200 (item 7100's linkSkillId). Completes the charm item->skill->abnormality chain. |
| 17-iod-charm-quest-dedup | RETIRE | The double-teach was pilot-created (re-enabling 1385 while keeping v31/v92 1384). Under v31 port, 1384 owns the step and 1385 stays disabled. No dedup needed. See finding below. |
| 18-iod-item-string-fixes | CARRY-OVER | Campfire (98) + Masterwork Alkahest (21351). Verified still needed (v92 baseline still broken). Item 98 also supports the charm quest (1384 task 2 grants it). |

## Charm quest finding (1384 / 1385) - spelled out

**Question:** under strict v31 port, does quest 1384 work as-is once charm salvage lands, and does spec 17 fully retire?

**Answer: YES to both.** Read directly from the v31 server quest files
(`QuestData/001384.quest`, `QuestData/001385.quest`):

### v31 quest 1384 "Getting to Know the Garrison" (mission, story group 1, min lvl 4, prereq 13,29)
Giver NPC 64,1029. 6 tasks:
1. Visit 64,1005
2. Visit 64,1049 -> grants item **98 (Campfire)**
3. Condition: rest-to-max-condition (`휴식후컨디션MAX`) - the stamina mechanic; may need a mechanical adaptation on v92 (whitelist #3)
4. Visit 64,1049 -> grants item **7100 (Onslaught Charm I)**
5. Condition: **USE ITEM 7100 x1** - THE CHARM-USE STEP
6. Visit 64,1049 -> reward=1

**(a) 1384 absorbed the charm-use step: CONFIRMED** (task 5).
**(b) charm item it grants/uses: 7100** (Onslaught Charm I) in both task 4 (grant) and task 5 (use). v17 used 7100; patch-000 on v92 swapped 1384's charm to 70033; **v31 uses 7100 natively.** Under v31 port, revert the 70033 swap back to 7100.

### v31 quest 1385 "Always After Me Lucky Charms" (normal, no story group, min lvl 3, prereq 99,99)
Start item 7100 x1. 2 tasks: (1) use item 7100 x1; (2) visit 64,1049 reward=1.

**(c) 1385 sentinel-disabled in v31: CONFIRMED** (prereq `99,99`, never-satisfiable).

### Does the v31 charm item exist in v92 baseline?
**YES.** Clean v92 `Item 7100`: exists, `combatItemType: NO_COMBAT`, tooltip "This item is no longer usable.", `linkSkillId 60240200`. It is present but **disabled**. v31 has it as `DISPOSAL` (usable). Charm spec **15** flips 7100 back to `DISPOSAL` and restores the tooltip; spec **16** injects the skill buff (60240200); spec **14** supplies the abnormality.

### Conclusion
Under strict v31 port:
- **1384** ported 1:1 keeps its charm-use step and works **once the charm salvage (14/15/16) makes item 7100 usable.** (One caveat: task 3's rest-to-max-condition may need a stamina adaptation, tracked with the quest-tasks family, not the charm chain.)
- **1385** ported 1:1 stays sentinel-disabled - players never see it.
- **No double-teach** exists. The retired pilot only had one because its `09-iod-quest-enable` re-enabled 1385 (to v17 wiring prereq 13,84) on top of the v31/v92 1384 that already teaches the step.
- **Spec 17 fully retires.** Its 7103/Onslaught-Charm-IV escalation was a v17-flavored layer on the dedup and retires with it (v31 1384/1385 both use 7100).

**Load-bearing constraint for the redo:** when regenerating `09-iod-quest-enable` from v31 (REWORK), do **not** re-enable 1385. Keep v31's `99,99` sentinel. Re-enabling it is exactly what re-creates the double-teach.

## Generators in tools/dc-restore useful for the redo

Every `gen_*.py` that encoded v17-north-star logic survives but must be **re-pointed at v31 sources**. The `extract_v31_*.py` extractors are directly useful.

| Generator | Feeds spec(s) | Status for redo |
|-----------|---------------|-----------------|
| gen_section_specs.py | 00, 01 | Re-point to v31 geometry/strings |
| gen_spawn_specs.py | 02 | Reused for v31 wipe-and-replace (not the v17 groups) |
| gen_shop_specs.py | 04 | Re-point to full v31 shop set |
| gen_reward_specs.py | 05 | Re-point to v31 QuestCompensationData |
| gen_task_specs.py | 06 | Re-point to v31 .quest trees |
| gen_storygroup_specs.py | 07 | Re-point to v31 QuestGroupList |
| gen_enable_specs.py | 09, 10 | Re-point to v31 headers; keep 1385 disabled |
| gen_speech_specs.py | 11 | Already v31-sourced; reconfirm roster |
| gen_charm_specs.py | 14, 15, 16 | Charm salvage carries over as-is |
| gen_scriptfix_specs.py | 12 | Conditional - only if displacement reproduces post-port |
| gen_npcloc.py | (client) | Regenerate client NpcLoc from ported server state (doctrine rule 8) |

**v31 extraction core (directly useful):** `extract_v31_econ.py`, `extract_v31_quests.py`, `extract_v31_spawns.py`.
**Diff / disposition tooling:** `classify.py`, `stat_diff.py`, `align_ids.py`, `survey.py`, `audit_quests.py`.
**Libraries:** `dclib.py`, `dcq.py`.
**v92 extraction for the diff side:** `extract_quests.py`, `extract_npcs.py`, `extract_shops.py`.
**Legacy restore engines (partial reuse):** `comp_restore.py`, `quest_restore.py`, `spawn_restore.py`.

## DECISION items for the orchestrator

1. **Spec 15 item 70033 op.** v31 1384 uses 7100, not patch-000's 70033. The 70033 charm-item op in spec 15 is extraneous under v31-primary (harmless, but not needed). Keep it usable (broad charm restore) or drop it (strict v31 scope)? Recommend keep - low risk, keeps the item family consistent.
2. **Spec 13 worldmap ops 2-3 (9034/9053 sync-compat).** These are E650 XSD band-aids, not IoD content. Confirm whether the freshly reverted v92 baseline still fails the client-sync projection on 9034/9053; carry them only if it does. Not blocking IoD.
3. **v31 1384 task 3 (rest-to-max-condition / stamina).** The v31 quest body carries the retired stamina mechanic. Needs a mechanical-adaptation decision (whitelist #3) during the quest-tasks REWORK - which functioning v92 equivalent, or drop the task. Flagged here so it is not lost between the salvage pass and spec authoring.
