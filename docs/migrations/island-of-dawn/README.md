# Island of Dawn Restoration

## Objective

Restore Island of Dawn as the new-character starting zone in v92, replacing Stepstone Isle. This restores the original TERA lore and progression experience using v31 server data as the reference source.

This migration must be completed **before** patch 001 is applied — the game should be fully functional with the original starting experience before custom content changes are layered on.

## Scope

- Replace all v92 endgame Island of Dawn content with v31 original content
- Restore the prologue dungeon (zone 416) and main open-world zone (zone 13) with sub-zones
- Redirect new character creation from Stepstone Isle (zone 827) to IoD prologue (zone 416)
- Migrate all zone-partitioned server datasheet files
- Selectively merge IoD-related entries from v31 monolithic files into v92
- Sync applicable changes to client datacenter

## Out of Scope

- Stepstone Isle removal (zone 827 files left in place, just unreferenced)
- Island of Dawn Coast (zone 415) — v92-only zone, decision deferred
- Endgame IoD content preservation — we are fully replacing, not merging
- Character creation entry point redirect (zone 827 → 416) — handled manually by project lead

## Key Paths

| Resource | Path |
|----------|------|
| v31 server datasheet | `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet` |
| v92 server datasheet | `D:\dev\mmogate\tera92\server\Datasheet` |
| v92 client datacenter | `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR` |
| DSL CLI | `D:\dev\mmogate\github\reforged-server-content\dsl.exe` |
| Sync config | `reforged\config\sync-config.yaml` |

## Data Sources

| Server | MCP Tool | Purpose |
|--------|----------|---------|
| v31 (`datasheet-v31`) | Read-only reference | How the original game worked |
| v92 (`datasheet-v92`) | Active server (modifiable) | Current state, validation target |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-14 | Full replacement, not merge | We want the original experience, not a hybrid |
| 2026-04-14 | DSL not viable for bulk migration | Zone infrastructure files (NPC, AI, spawn, territory) have no DSL schema. Direct file operations are the primary method |
| 2026-04-14 | DSL may be used for fine-tuning | Post-migration adjustments to loot, items, strings can use DSL where schemas exist |
| 2026-04-14 | Pre-patch-001 execution | Migration establishes the foundation; patch 001 builds on top |
| 2026-04-14 | DSL sync template has NpcData, TerritoryData, DungeonData, ContinentData | Adopt zone_mapping configs from `sync-config.template.yaml` — no DSL code changes needed |
| 2026-04-14 | Client DC migration uses direct v31 copy, not DSL sync | v31 client DC has exact data in correct format; DSL sync adopted post-migration for ongoing maintenance |
| 2026-04-14 | .quest files are XML with Korean tags, not binary | DSL has full quest schema support (quests, questStrings, questDialogs, questCompensations) |
| 2026-04-14 | DSL sync template missing entries for multiple entities | QuestData (IdSorted code exists), QuestDialog, AIData, DynamicGeoData, NpcShape, StrSheet_ZoneName — file as post-migration DSL requests |
| 2026-04-14 | v31 client DC available | `Z:\tera pserver\v31.04\client-dc_v31\DataCenter_Final_EUR_v31\` (408 files) |
| 2026-04-14 | v92-only zone files to be emptied, not deleted | DynamicSpawn/FormationData for sub-zones 64, 213, 313, 364 — keep valid XML skeleton |
| 2026-04-14 | Phase 0 uses git revert | Pending changes from patch 001 migration run; git checkout to clean state |
| 2026-04-14 | Character creation entry point out of scope | Project lead handles manually |
| 2026-04-14 | Quest data queryable via MCP | `search_quests`, `trace_quest_sequence`, `audit_quest_chain`, `lookup_quest_dialogs`, `lookup_quest_rewards` available on both v31 and v92 |
| 2026-04-14 | Noctenium arc excluded | Story group 18 (quests 15101–15103, level 60) out of scope — no high-level quest migration |
| 2026-04-14 | Zone 415 included for quests only | Zone files identical between v31/v92 (no zone file copy needed). 8 "Reach the Beach" prologue quests added to scope |
| 2026-04-14 | Quest 1339 included | Zoneless side quest, successor to 1313. All dialog NPCs in IoD zones 213/64 |
| 2026-04-14 | connectedTo 101 is chain terminal | Not a real quest — it's the null/terminal marker in the quest chain system |
| 2026-04-14 | Dangling chains accepted | IoD chains may not connect to v92 questline seamlessly. Smooth out post-migration with DSL |
| 2026-04-14 | 65 total quests in scope | 25 mission + 40 side (includes 16 prologue class variants + 1 zoneless) |

## Current Status

**Phase: Assessment (complete)**

See [assessment.md](assessment.md) for the full technical evaluation.
See [progress.md](progress.md) for phase-by-phase status tracking.

## Related Documents

- [assessment.md](assessment.md) — Technical evaluation: zones, files, gaps, approach
- [zones.md](zones.md) — Zone inventory with IDs, NPC counts, relationships
- [quests.md](quests.md) — Complete quest inventory (53 quests), chains, dependencies, reward items
- [file-manifest.md](file-manifest.md) — Exact file lists per phase (copy/merge/delete)
- [plan.md](plan.md) — Detailed execution plan with steps, commands, and dependencies
- [progress.md](progress.md) — Phase checklist with done/pending status
