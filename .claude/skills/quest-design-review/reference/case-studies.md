# Case studies

Every check in `audit_quest_design.py` exists because it caught something real.
Abstract checklists get skimmed; worked examples stick. Each entry names the
defect, how it was found, the fix, and the check that now covers it.

Unless stated otherwise, these come from the Island of Dawn restoration and the
patch-002 trimming and redistribution wave (specs `002/27` through `002/33`,
live-validated 2026-07-27).

---

## Rewards

### Two quests, one bag, identical payout
**Check: `duplication`.** Quests 1304 and 1323 granted the identical 12-row class
weapon bag at the identical 800 exp and 80 gold. This is authentic v31 data, so
no diff against the historical source could ever have flagged it: both quests
were faithfully restored and both were correct in isolation. Found by comparing
reward payloads across the zone. Fixed by redistributing one bag.

The signature that made it detectable is narrow on purpose: same item AND same
exp AND same gold. Two quests granting one item at different payouts is ordinary
design, and widening the signature is how the check starts crying wolf.

### A quest handing over a shop's whole tab
**Check: `duplication`.** Quest 1315 granted the Kugai token shop's entire
weapons tab and chest row for free, 24 items, while the same items were
purchasable with a token that drops from the boss the quest is about. Only
visible with shops in evidence scope, which is why the source universe spans
about twenty file families rather than just the compensation tables.

Note for anyone rebuilding this oracle: the overlap does not exist in either
committed snapshot. At `789fec28` quest 1315 grants the 24 items but the Kugai
Weapons list does not exist yet; in the current working tree the shop exists and
1315 grants nothing. The defect was real in a transient state. The structure is
pinned by a hermetic test instead.

### A class stuck on the same weapon for a whole zone
**Check: `class-matrix`.** Brawler and Ninja received the same level-2 weapon
from all three weapon quests in the zone and never a mid-tier upgrade. Root
cause: two reward generators (`gen_reward_specs.py`, `gen_v31_reward_specs.py`)
each carried a PRIVATE per-class weapon pool that skipped levels 3 to 6. It
survived every gate and was only caught by live testing.

That is why the item model lives in `dclib` and why folding those two generators
onto it is a tracked follow-up: three independent item models is what produced
the defect. Until that lands, the audit and the generators can disagree, and the
audit is the one to trust.

### A gear tier nobody could complete
**Check: `set-completeness`.** No gear set below level 7 was completable: 6 of 9
level-4 pieces and all 3 level-3 body pieces were granted by no quest anywhere in
the corpus. Sets group by VISUAL TIER, decoded from `linkLookInfoId`, not by
level and not by `itemLevelId` (the latter is the wrong axis and returns sets
spanning levels 1 to 60).

Tier is not level: tier 005 is a level-4 item, tier 007 a level-7 one, tier 116 a
level-58 one. Never infer one from the other.

### A farmable unique
**Check: `repeatable-rewards`.** Repeatables 1334 and 1390 had to be manually
excluded as set carriers: a repeatable quest granting unique gear is farmable.
The equipment test is an allow-list, because `combatItemType.startswith("EQUIP")`
also matches roughly 4,100 cosmetic, underwear and inheritance items and would
fire on every costume repeatable in the game. A bare `최대레벨` is not a trigger
either; only the conjunction with an equipment grant is.

### A class silently left out of a reward row
**Check: `reward-class-coverage`.** Quest 1322's leather rows list four classes
while item 17409's own `requiredClass` admits five. The fifth omission is a
doctrine ruling, which is exactly what the waiver file is for. Compare
case-insensitively: `ItemTemplate` uses UPPERCASE (`WARRIOR;SLAYER;...`) and
compensation rows use lowercase internal names (`class="lancer"`).

### The quest log advertising rewards the server does not pay
**Check: `client-parity`.** `QuestCompensationData` was not client-synced, so the
quest log showed stale rewards while the payouts were correct. This recurs per
zone by design: `sync-config.yaml` needs a pair per zone or the sync skips
silently. The most impactful single defect of the session that produced this
tool.

---

## Graph

### A trim that would have orphaned its successor
**Check: `references`.** Retiring 1323 would have orphaned 1324; retiring 1318
had zero inbound edges and was safe. Answering that question needed a sweep of
every reference class in both id encodings, including the DungeonData
`Event questId` surface that two earlier reviews of the plan both missed, which
is what wires dungeon 9037 to quest 1346.

### A permanently missable set
**Check: `hidden-gates`.** Quests 1326 and 1330 carried `진행퀘스트 = 1305,1`
and each granted a piece of a four-piece set. Finishing 1305 first stranded the
set permanently. Invisible to every MCP tool. Native clearing now exists in the
DSL (`inProgress: []`, commit `94707de7`).

---

## Tuning

### An objective that could not be completed by clearing the zone
**Check: `feasibility`.** Quest 1348 required 8 items from 10 credit mobs, an
expected yield of about 6.1. `audit_quest_gates` reported it as OK; testers
called it the worst quest in the zone. Report the numbers, not just a verdict,
and name both remedies: widen the accept list (now authorable per DSL commit
`2a41fa95`) or change the spawns.

### Gear arriving before or after its band
**Check: `level-coherence`.** Level-4 gear granted by quests at `최소레벨` 1 to 3,
and the Chione chain (`최소레벨` 7) sitting behind quest 1335 (`최소레벨` 8).

### Story quests carrying the power curve
**Check: `lane`.** Zone quests own power progression; story quests own lore. Test
story membership with a non-empty `스토리그룹Id`, never with
`퀘스트종류 = 미션` alone, which misses every `중요미션` quest.

---

## Placement

### A reward nobody walked to
**Report: `set-placement`.** The level-7 weapon sat on Ayrdoss, 6,208 units
past the camp cluster, and testers skipped it. Rechaining 1332 to 1333 cut the
two-piece round trip from 46,380 to 27,018 units. The ideal placement is a chain:
one quest's turn-in NPC is the next quest's giver.

### "The zone feels repetitive"
**Report: `giver-load`.** 20 of the 34 restored zone quests are a single Hunt or
HuntAndDeliver task. That is what testers meant, and it is measurable rather than
a matter of taste.

### Deciding whether a payout matches the work
**Report: `effort-reward`.** Kill and collect counts and task counts against exp,
gold and item payout, sorted raw and deliberately unflagged. Thresholds are
judgment; a table is deterministic. The tool lays the two columns side by side
and stops there, because every attempt to automate "is this worth it" encodes one
zone's pacing as if it were a law.

---

## Method lessons

These are not about quests. They are about how the analysis itself goes wrong.

### Prove a condition's semantics from data, never from its name
The trimming wave's achievement-safety claim was measured against
`templateId=1020`, which turned out to be an ITEM-POSSESSION condition: all of
its `value2` values are item ids. The real quest-completion condition is
`templateId=4012`, with the quest global id in `value1`, and it references six
Island of Dawn quests. The trims survived by luck, not by check. If another
`templateId` is ever needed, prove it the way 4012 was proven: show that its
values resolve into the quest id space, and explain the misses.

### Parse structurally, never grep
A raw substring search for the `99,9999` prerequisite sentinel returns 563 files.
The real answer is 17. The other 546 are `NPCId` values that merely contain those
digits. There are also TWO sentinel encodings (`99,99` and `99,9999`), and a
checker that knows only the first reports 17 disabled quests as live.

### Measure the baseline, not the working tree
Several numbers in the original plan were measured against a dirty patch working
tree and are wrong for the committed baseline: the `99,99` sentinel is on 55
files at `789fec28`, not 60, and `ItemTemplate.xml` itself is dirty, so the base
shard holds 34,276 items at the baseline versus 36,528 in the tree. Regression
fixtures pin the commit for exactly this reason; HEAD moves every time a patch
closes.

### The regional-variant rule is not universal
Skipping `_NAEU` and friends is correct for `BuyList` and every shop family,
where the variants duplicate the base list. It is WRONG for `ItemTemplate`, whose
shards are disjoint id spaces: 171 of the 925 item ids quest rewards reference
(19%) live only in a non-base shard, and a base-only read loses their level and
class data entirely.
