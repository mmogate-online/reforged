# Island of Dawn Alpha Content Loop: Restoration and Loop Plan

Status: READY FOR EXECUTION (feasibility gates passed 2026-07-17). This
document is self-contained for a fresh session; supporting data extracted from
the old client lives in `data/` next to it.

## Design intent (binding for all phases)

- **Nostalgia first, mechanics second.** We restore the pre-revamp island
  *content* (quests, story chain, flavor) but map rewards onto Reforged's own
  systems (Kugai token loop, enchant materials, infusion, crystals). Do NOT
  inherit old-patch progression mechanics wholesale.
- Patch 001 as it stands is a **viability check, not a final loop**; every
  number in it is tunable. Framework invariants are binding (content framework
  repo CLAUDE.md, resolve `content_framework` from `.references`): pure
  currency separation, gold sinks at every layer, no death penalty, per-content
  tokens, no system-printed catch-up.
- Alpha scope: Island of Dawn only (zones 13/64/213/313/364 + dungeon 436),
  server level cap 10. Exit is sealed by spec 22 (flight manager voided).

## Source assets

- Old client DataCenter (2011 era, pre-revamp island):
  `D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA` (unpacked XML; the
  datasheet MCP cannot mount it, use the Python scripts in `data/`).
- Extracted catalogs (in `data/`): `iod_catalog.json` (63-quest catalog with
  classification), `iod_report.txt` (per-quest tasks/rewards/dialogs),
  `iod_inventory.json` (raw), `gate1_out.txt` (schema-strip listing),
  scripts `inventory_iod.py`, `gate1_diff.py`, `gate3_comp.py`.
- Prior research context: `docs/mcp-requests/2026-07-17-iod-alpha-research.md`
  (tooling + content findings), domain doc `entities/loot-system.md`
  (QuestCompensation section), `docs/patch-001-scope.md`.

## Feasibility gate results (2026-07-17, all passed)

1. **Client-to-server conversion: GO.** Corpus diff (2,701 server .quest vs
   2,121 client shards): for talk/visit, kill-N, deliver, and gather tasks the
   client preserves all gameplay-defining fields (task types, NPC/monster ids,
   counts, collection ids, flag items, journal refs, minLevel, prereqs, story
   group). Mechanical generation policies: chain = ascending task id with
   StartTaskId=1 (linear quests only); archetype defaults for stripped header
   fields. **Hand-authored per quest:** kill-drop chances (수여확률), completion
   item grants/removals, dialog page index mapping, next-quest links
   (연결퀘스트), popup/button texts. Branch (분기) and escort task types are NOT
   mechanically restorable (none needed for the target batch).
2. **All referenced world objects exist on v92:** quest flag items 9010/9011/
   9012/9095/9100; reward items 17710/13/16 (Family Ties body armor lv5),
   15605/08/11 (Air Courier hands lv9), 8007, 7100; NPCs 437:1001 Sorcha,
   436:1002 Karascha; collections 409/410/411/492/496 configured on continent
   13 with spawn points (409: 20, 410: 24, 411: 30, 492: 1, 496: 5). The
   collections for the deleted quests are orphaned v92 residue, ready to use.
3. **Old rewards are machine-readable:** client `QuestCompensationData-00007.xml`
   carries all 11 target quests with English attributes
   (`CompensationType@gold/exp/itemBag`, `Item@templateId/quantity/class`).
   None of the 11 uses class-filtered items (only 1384 has items at all).

## Target quest batch

From `data/iod_catalog.json`: 52 of the old island's 63 quests survive in v92
unchanged (category i). The batch:

**Restore (deleted from v92 and v31, client-only source):**
| id | name | archetype | notes |
|----|------|-----------|-------|
| 1334 | Investigating the Relics | gather (coll. 410) x5 item 9011, REPEATABLE | daily-loop candidate |
| 1336 | Chione's Missing Cargo | gather (coll. 409) x4 item 9010 | |
| 1341 | Bequest of the Dead | gather (coll. 411) x5 item 9012, REPEATABLE | daily-loop candidate |
| 1343 | Answers Lead to More Questions | 3x deliver-given-item chain | main-chain link: old chain ran 1315 -> 1343 -> 1316; reinsert via prereq edits |

**Deferred to post-alpha (old variants of quests whose ids v92 reuses for
rewritten content):** old 1301/1305/1311/1331/1337/1382/1384. If restored,
they need NEW quest ids and titles disambiguated. Not part of the alpha
critical path.

**Quest ID allocation rule (binding whenever a new id is needed):** quest ids
are a composite key (huntingZoneId, questId) and the global id follows a
region-indexed pattern: the island band is 13xx (old client used 1301-1390
with gaps at 1314, 1320, 1342, 1353-1370, 1380-1381, 1383, 1387-1388; v92
took 1379 for Gunner training). New island quests must be allocated INSIDE
the 13xx band from those gaps, and each allocation must be verified three
ways before use: (1) `domain_docs` reference/id-registry.md conventions,
(2) `mcp__datasheet-v92__find_free_ids` / direct quest lookup on v92 to
confirm the id is free NOW, (3) the StrSheet constraint that quest string ids
derive as GlobalId x 1000 + index (quest-system domain doc), so the matching
string id block must be free too. Do not allocate outside the region band.

**Ambience (optional, cheap):** 124 old VillagerDialog files for zones 213/64.

## Live-test iteration plan (2026-07-17, supersedes the phase ordering below)

Working mode: technical restoration first, balance later. Each iteration is
the smallest testable unit: apply, deploy to dev, manual world restart, live
test against an expected-results checklist, feedback, next iteration.

- **Iteration 0 (DONE):** `tools/dc-restore/` survey toolkit + gap report
  (`iteration-0-gap-report.md` in this folder). Key results: NO NPC, skill,
  AI, or territory loss in any scoped zone; 75 empty QuestCompensationData_13
  rows restorable verbatim from v31; the "4 deleted quests" are actually
  soft-disabled in place (see the Phase 2 correction below).
- **DISCOVERY (2026-07-17): 40 island quests are sentinel-disabled**, not 4.
  Every one of the 40 has exactly one `퀘스트Id 99,99` prereq sentinel; the
  currently live island runs only the ~25 remaining quests (reduced spine +
  class training). The disabled set includes the old spine segment
  1306/1307/1308/1310/1312 that the live chain bypasses, so full re-enable
  must be chain-aware (restore prereqs from client reference in dependency
  order and rewire the live spine). Example cascade: 1336 needs 1335, which
  needs 1310.
- **Iteration 1 (APPLIED + DEPLOYED 2026-07-17, awaiting live test):**
  re-enabled 1334/1341 (fully testable, no prereqs) and 1336 (dormant: its
  prereq 1335 is still disabled; verifying it stays unoffered is part of the
  test) + v31 comp rows for all three. Server-only change; delta deployed
  and SHA-verified (56 files incl. the 52-file patch-001 overlay).
- **Iteration 1 addendum (2026-07-17): quest-giver spawns can be missing.**
  Eria (213,1021), giver and turn-in of 1334, had NO spawn entry anywhere:
  v92 and v31 despawned her along with the quest disable, and client
  TerritoryData carries only fence polygons (never NPC spawn lists), so no
  historical position exists. Authored a new spawn (instanceId 21300069,
  Black Rift vanguard camp next to Fili, pos 53330,-69640,-5659) in
  TerritoryData_213; server-only, deployed. CONSEQUENCE for Iteration 3: the
  batch re-enable must audit EVERY giver/turn-in NPC of the ~36 quests for a
  live spawn; despawned givers need authored placements (design decision per
  NPC, camp co-location as the default).
- **Deterministic backlog established (2026-07-17).** The quest audit
  (`iteration-2-quest-audit.md` + `.json`, generated by
  `tools/dc-restore/audit_quests.py`) and the ruins archaeology
  (`data/2026-07-17-ruins-archaeology.md`, plus the external location map
  `data/legacy-quest-locations.md`) supersede ad-hoc discovery. Key facts:
  65 quests audited; 37 sentinel-disabled; ~8 quest NPCs and ~17 quest
  kill-target mobs are UNSPAWNED since before v31 (spawn restoration cannot
  source from v31); Leander's Outpost was never built server-side and needs
  full TerritoryData authoring; Mysterious Ruins polygon itself is correct
  as-is; "Redeployment" = quest 1311 title drift, not a lost quest.
  Fixed en route: 1336 collection 403 -> 409 (v92-only regression caught by
  the audit; deployed).
- **Batch 1 (pilot): Kishale pair 1322/1323.** Sentinel removal + v31 comp
  (class-filtered boots / class weapons). Tests the class-itemBag comp path.
- **Batch 2: mechanical set.** The 8 COMP_EMPTY quests where client==v31
  agree + any remaining TASKREF regressions from the audit JSON.
- **Batch 3: spawn reconstruction (authored).** Leander's Outpost territory
  + roster (Ayrdoss 1126, Lorin 1128, Jehan 1130, Eria 1021 relocation) +
  its target mobs (Rockcrawlers, Cromos, Orcans); then the remaining
  unspawned givers/targets at their authentic camps per the archaeology
  anchor table. Positions are design decisions validated by the user's
  legacy videos.
- **Batch 4: chain re-enable.** The 19 chain-entangled quests including the
  bypassed spine segment (1306-1312), 1343 + 1316 relink + story group 2
  registration. Gated on Batch 3 for kill targets.
- **Batch 5 (decision queue).** Reward-era conflicts, 1304 task redesign
  judgment, level-band drifts.
- **User decisions (2026-07-17, binding):** reward era = v31 values,
  fallback to the 2011 client only where v31 has no data for the quest;
  quest 1311 keeps the server title "Redeployment"; Batch 1 and Batch 3
  approved. Iteration 1 quests validated live by the user (1334 and the
  collection-fixed 1336; Eria reachable at the provisional Tainted Gorge
  spot, relocation to her original post pending Batch 3).
- Each batch ships via deploy-dev + deploy-client (pack, install, publish)
  with a world restart and a user spot-test before the next.
- **Iteration 4:** villager ambience from old-client shards (zones
  64/213/313/364/436 have shards; zone 13 has none by design).
- **NPC/spawn restoration: dropped.** The survey found zero loss; there is
  nothing to restore in scope.
- Restored files are BASELINE-lane commits (see execution conventions).

## Phases

### Phase 0: Reconcile current island state (MOSTLY DONE 2026-07-17)

Completed in the planning session, in this order:
1. Dev server datasheet reverted to payload HEAD via `deploy_dev.py --revert`
   (it held a stale overlay from the previous test); verified clean; box HEAD
   == local HEAD (commit 9c7163fe, the IoD baseline, which already contains
   patch 000: verified via Training Bomb item 5002).
2. Full fresh apply of patch 001 onto the clean local baseline:
   `python reforged/tools/migrate/migrate.py --patch 001` (65 specs applied,
   0 failed, 10177 ops; includes IoD specs 16-22 and the balance multiply
   applied exactly ONCE: the earlier research saw an unpatched island because
   the local tree had been reset after the last test). Client sync completed
   (16 entities, 52 files, manifest-narrowed).
3. Delta deployed to the dev server via `deploy_dev.py --verify`: 52 files,
   all SHA256-verified. Kugai's Crest (95216) confirmed live in the local
   datasheet. Balance docs fixed to the real multipliers (spec comment +
   STATUS.md): maxHp x10 / atk x60, intentionally above gear-formula neutral;
   the `multiply` spec must never be re-applied to an already-patched tree.

REMAINING for the implementing session:
- World server restarted and loaded live 2026-07-17; user began live testing.
- Complete the in-game smoke if not already done: BAM kill, Kugai's Crest
  drop, right-click Kugai Exchange, one enchant with T1 materials.
- MCP spot-audit: `audit_zone_loot` hz 13 (crest bags, crystal/infusion
  boxes live; dead bags marked [DEAD]).
- The local datasheet working tree now holds the 52 applied changes
  UNCOMMITTED. Commit + push to the payload repo only after in-game
  validation (the promotion step); until then the dev box overlay is
  intentionally ahead of payload HEAD.

### Phase 1: Fill the reward vacuum (biggest playability win)

All 77 `QuestCompensationData_13.xml` entries are empty stubs: the questline
grants nothing, and island mobs drop no gold. Steps:
1. Generate compensation rows for the ~61 classic quests from the old client
   values (gold/exp baseline in `data/iod_report.txt`), scaled to current
   balance; keep the nostalgia gear rewards (Family Ties / Air Courier pieces,
   they exist on v92) as quest-gear flavor beneath the Kugai token set.
2. Mechanism: no DSL entity for QuestCompensation exists (open request
   `docs/dsl-requests/2026-04-27-quest-compensation-data.md`); generate the
   XML with a script (extend `tools/iod-loot/` or new `tools/quest-rewards/`),
   idempotent by regeneration, and record it as a known manual-XML artifact.
3. Note: v92 CompensationType supports `itemBag` allpay/class/race/choice and
   internal class names (see domain doc loot-system.md, QuestCompensation
   section). The old client uses the same shape with 2011 class names; map
   `elementalist` etc. per the class-mapping reference.
4. DECIDED: island mobs get a small gold bag (difficulty-scaled, classic-TERA
   copper-range feel), alongside quest gold; gathering stays the premium
   income. Rationale: the framework's lane model expects solo combat to be a
   gold source (07 §9) and "all lanes mild" forbids forcing gathering as the
   only income; the evolution step needs 10000 money; and mobs dropping a few
   copper IS the nostalgia feel. Implement as an ECompensation gold bag in the
   `tools/iod-loot/` generator, tuned so evolution affordability arrives
   around the natural Kugai-farm point, not instantly.

### Phase 2: Restore the 4 deleted quests

**CORRECTED by Iteration 0 (2026-07-17): the premise "deleted from v92 and
v31, client-only source" is FALSE.** All four quests exist in v31 AND v92
with full content (tasks, `QuestDialog_13xx.xml` dialogs, StrSheet_Quest
titles), byte-identical between the two servers. They are soft-disabled in
place: prereq replaced with the unsatisfiable sentinel `퀘스트Id 99,99`;
1343's story group (2) stripped and 1316's prereq rewired from 13,43 to
13,15 (chain collapsed around the disabled quest); no QuestGroupList entries;
v92 QuestCompensationData_13 rows emptied to stubs while v31 rows remain
FILLED (1334: 800xp/80g, 1336: 600xp/60g, 1341: 1500xp + allpay itemBag,
1343: 800xp/80g). The old client (active era) confirms original wiring:
1334/1341 repeatable with no prereq, 1336 prereq 13,35, 1343 prereq 13,15 +
story group 2, 1316 prereq 13,43. Restoration is therefore a surgical header
re-enable + v31 comp-row merge + story-group insert, owned by
`tools/dc-restore/` (`quest_restore.py`, `comp_restore.py`). No client-shard
conversion is needed; the v92 client DC already contains all four quests.
The original phase text below is retained for reference only.

1. Build `tools/quest-restore/` (Python): client-shard to server-.quest
   converter implementing the Gate 1 policies. Input: `data/iod_inventory.json`
   or the raw client shards; output: `QuestData/00133X.quest` files plus
   strings and dialog artifacts.
2. Hand-author per quest: dialog page index mapping (dialog text survives in
   client QuestDialog shards; page indices must be reassigned), next-quest
   links, button texts. No kill-drop quests in this batch, so no drop-chance
   authoring needed.
3. Server-side integration:
   - `.quest` files: direct file drop (IoD migration precedent), DSL
     `questStrings` for StrSheet_Quest entries (supported and proven).
   - `QuestGroupList.xml`: manual Python merge (no DSL entity; IoD precedent
     `docs/migrations/island-of-dawn/data/phase2-log.md`).
   - Compensation rows: same generator as Phase 1.
   - Re-link 1343: DSL quest partial-update to set 1316's prerequisite to
     1343 and 1343's to 1315 (watch open requests: destructive task update,
     silent no-op; touch ONLY header prereq fields, verify by re-read).
4. Client-side: full `-e Quest` DSL sync (manifest-narrowed sync silently
   no-ops for IdSorted: `docs/dsl-requests/2026-04-21-...md`); manual
   QuestDialog + StrSheet_Quest shard copies remapped by content (no sync
   config exists for either); repack DataCenter via the established pipeline.
5. Known DSL friction on this path (workarounds exist, files in
   `docs/dsl-requests/`): 2026-04-15 destructive/silent task updates,
   2026-04-16 NPCId qualification + E650 XSD abort, 2026-04-18 dialog path
   bug + nextTaskId, 2026-04-27 compensation entity. Log any new issue there;
   MCP gaps go to `docs/mcp-requests/`.

### Phase 3: Close the loop (framework exercise layer)

Reuse what patch 001 already authored (Kugai's Crest token + 3-tab MedalStore
+ Kugai lv8 gear evolving to Starter 0; T1 enchant materials; Rhomb crystal +
dyad structure boxes; Uncommon infusion boxes). Add the missing closures:
1. **Rune source DECIDED: a 4th tab on the Kugai MedalStore selling Paverune
   501/511 for Kugai's Crests.** Rationale: the first evolution step is
   mandatory progression and should be deterministic, not RNG-gated; crests
   are guaranteed BAM drops, so the token shop is the pity-path best practice;
   token-buys-item respects currency-separation invariant #4; the 10000-money
   evolution cost stays as the gold sink (invariant #7), fed by the Phase 1
   gold decision. A small rune drop from named elites may be added later as
   flavor, not as the primary source.
2. **Daily loop DECIDED: convert restored repeatables 1334/1341 into island
   dailies** (DailyQuest entity, DSL-supported), preserving their original
   text and repeat framing. Rationale: at a hard level-10 cap an unlimited
   repeatable gold/XP quest is an open faucet (economy exploit); a daily cap
   preserves the nostalgic repeatable feel while bounding the faucet, matches
   the framework's NPC-daily lane (02 §5, 03 §2), and generates the exact
   playtest data its open questions ask for (daily cadence, first-of-day
   bonus, XP calibration).
3. Optional identity rewards per framework (05 §6): island chain title,
   an emote/footstep on the token shop. Cosmetic-only, wipe-exempt framing.
3b. **Villager ambience (alpha scope per decision 6):** restore the old
   client's 124 VillagerDialog files for zones 213/64. Note: the VillagerDialog
   entity is NOT DSL-supported (`docs/dsl-requests/2026-06-02-villager-dialog-
   entity-not-supported.md`); this is manual server-XML merge plus client
   shard copy, following the IoD migration precedent.
4. Dungeon token drop wiring for 487/488 (95214/95215 have shops but no drop
   bags in the zone e-comp specs) is OUT of alpha scope but flagged; confirm
   server-side state before beta.

### Phase 4: Validate, deploy, log

1. MCP audits: `audit_quest_chain` for the re-linked story spine,
   `lookup_quest_rewards` for filled compensations (the tool distinguishes
   empty stubs from missing since the 2026-07-17 MCP build), `audit_zone_loot`
   for the final drop picture, `check_references` for NPC loot links.
2. `/deploy-dev` + manual world restart + in-game run-through of the full
   1-10 chain including 1343 and both repeatables.
3. `/log-progress` on completion of each phase; spec work follows the
   idempotent-upsert rule; all new specs registered per patch conventions.

## Decisions (settled 2026-07-17)

1. **Balance multipliers: keep as applied** (maxHp x10 / atk x60); fix spec
   comments and STATUS.md to match reality; never re-apply the multiply spec.
   (User decision.)
2. **Island gold: restore a small difficulty-scaled mob gold bag** plus quest
   gold; gathering remains premium income. (Recommended; rationale in
   Phase 1.4.)
3. **Evolution closure: Paverune tab on the Kugai MedalStore**; gold cost
   stays as the sink. (Recommended; rationale in Phase 3.1.)
4. **Restored repeatables become island dailies.** (Recommended; rationale in
   Phase 3.2.)
5. **Quest gear (Family Ties / Air Courier): standardize stats via
   `equipment-item-standard`, positioned strictly below the Kugai token set;
   keep original names and looks.** (Recommended.) Rationale: the island
   balance multipliers were calibrated against standardized gear formulas, so
   off-formula vanilla stats would distort difficulty; nostalgia lives in the
   names/appearance, not 2011 stat lines; and this answers the framework's
   open question on basic-gear stat shape (07): quest gear sits above vendor
   common gear, below token gear.
6. **Villager ambience dialogs: alpha scope** (cheap, zero balance impact,
   pure nostalgia). **Old-variant story quests under new ids: post-alpha**
   (needs the ID-allocation rule above, dialog remapping, and disambiguated
   titles; alpha time is better spent on Phases 0-3). (Recommended.)

## Open tuning tensions (recorded 2026-07-17, resolve via LIVE TESTING)

Deliberate decision: do NOT resolve these on paper. They are tuned through
live dev-server iterations (deploy, restart, play, feedback), not intuition.

1. **Karascha's Lair (436) is a dead reward lane.** It has a balance profile
   (normal x8/x70, boss x10/x120) but NO loot spec exists in patch 001. With
   the island exit sealed it is the only reachable dungeon; it currently
   rewards nothing. Decide via play: wire minimal loot (crest bonus or own
   token per invariant 9) or accept a dead dungeon for alpha.
2. **Gold budget vs evolution sink sizing.** Classic quest gold totals 4,695
   plus dailies 180/day at classic values, far below the evolution sink
   (10,000 money per piece; 40,000 for weapon + 3 armor). Phase 1 scaling
   factor and mob copper rate must be derived from a live-tested target, not
   preset.
3. **Paverune tab price undecided.** At 2 runes per piece, 4 evolutions need
   8 runes; the price sets total crest demand beyond the 90-crest gear cost
   and therefore the loop length. Tune live.
4. **XP pacing unverifiable on paper.** No XP spec exists; classic questline
   totals 68,150 XP. Whether that lands players at L10 by the finale depends
   on the v92 XP curve. Playtest calibration item.
5. **Dungeon tokens 95214/95215 are intent-only** (defined and shop-wired,
   dropped by nothing; confirmed by spec grep). Out of alpha scope; recheck
   before beta.

## Execution conventions for the implementing session

- **Two commit lanes (binding).** Restored canonical old content (quests,
  spawns, NPCs, compensations recovered from the old client / v31) is the
  permanent BASELINE lane: commit it separately once live testing gives a
  strong stability signal. DSL-applied patch changes are the TUNING lane:
  expected to keep changing and committed ONLY by the user (patch 001 is
  still uncommitted for this reason). Never mix the two lanes in one commit.
- Research routing: `/domain-research` (v92 = current truth, v31 = reference,
  old client = archaeology via `data/` scripts only).
- Specs idempotent (`upsert`), validate before apply (`/apply-spec`), deploy
  with `/deploy-dev`, world restart is manual, promotion = commit + push of
  the datasheet repo to the payload repo.
- This repo is public: no hostnames/credentials in any file; environment via
  `.references` keys.
- Never revert client DC files on schema errors: investigate, DSL sync, or
  stop and report.
