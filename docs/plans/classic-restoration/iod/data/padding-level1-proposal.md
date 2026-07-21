# IoD Padding Level 1: Consolidated Findings and Proposal

Orchestrator adjudication over the four workstream artifacts (2026-07-20):
`padding-quest-gates.md`, `padding-overlap-rewards.md`, `padding-habitat-gaps.md`,
`padding-dormant-systems.md`. Analysis phase only; no specs authored yet. All enable
candidates keep their v31 bodies; "enable" means replacing the 99,99 sentinel prerequisite
with the v17 parent (rewards were already ported by patch 001 spec 04).

## Corrections to workstream artifacts (main-agent verification)

1. REFUTED: the collections-axis blocker claimed for 1334/1336/1341 (quest-gates) and the
   "collection nodes must be placed" dependency (dormant-systems). Verified in raw XML:
   CollectionTerritory_13_ATW_P.xml in BOTH v31 and v92 places typeId 409 (supply crates,
   spawnNum 15), 410 (ancient relics, 15) and 411 (expedition remains, 25), and live quests
   1311/1313 already gather 409/411 on the validated server. Consequence: 1336 and 1341 are
   gate-clean RESTORE; 1334 lacks only its giver NPC spawn (Eria Elin 213,1021).
2. Correction: 1334 uses collection 410, not 404 (dormant-systems typo).
3. Confirmed by spot-check: all six dormant leads sentinel-disabled with comp rows present
   in the live v92 tree; Beres 213,1130 has a template in NpcData_213 but zero spawns in
   TerritoryData_213 in both eras (sample validation of the missing-NPC roster).

## Headline findings

- All 40 sentinel-disabled candidates have intact server data (bodies, dialogs, strings,
  non-stub rewards) in v31 AND v92. Gate (a) never fails; the differentiators are NPC
  spawns (gate b), mob habitats (gate c), and narrative/reward conflicts.
- No candidate is blocked on the never-built camps: every v17 band quest exists in v31
  (v31 is a superset; adds 1379/1383, both live). Doctrine rule 3 is moot for IoD padding.
- The entire mob-habitat gap is in HZ 13: 17 v17-only mob groups (217 territories) deleted
  before v31; zones 64/213 fully covered. The Mysterious Ruins interior today contains only
  9 exploding-keg props; v17 had a 9-group, 117-territory ecology there. All roster
  templates still exist in v92 NpcData_13.
- Narrative screen: 5 AWKWARD-DUPLICATE (1306/1307/1308/1310/1343, cut story subplots that
  retell or spoil the compressed live arc; 1310 also collides on the displayed title with
  live 1305). Reward screen: 3 flags (1310/1326/1330 duplicate live 1305's ilvl7 set
  pieces). All 102 candidate reward item ids resolve on v92.
- Dormant mechanisms all expressible with living v92 examples (repeatable header, collect
  task, guard/solo-instance task, condition task).

## Proposal

### Wave A: immediate quest enables (17 quests, no world edits)

Gate-clean, narrative-clean (CLEAN or OVERLAP-BENIGN), reward-clean. One prereq op per
quest; anchor = v17 parent (live quest or co-enabled candidate):

1302, 1312, 1318, 1321, 1322 (+dialog fix 300932 to 300931), 1323, 1325, 1328, 1339,
1340, 1341 (repeatable), 1345, 1346 (live-test checkpoint: solo instance 9037/437),
1351, 1352, 1386, 1390.

Chain integrity inside the wave: 1322 roots {1318, 1323}; 1329 (live) roots
{1351, 1352, 1386 to 1328}; 1345 roots 1346. The 1322 fix is a doctrine rule 1
internal-consistency fix, divergence-logged.

### Wave B: mob habitat restoration (doctrine rule 5, 17 groups, 217 territories)

v17 fences + rosters, v31 same-family donor populations, every group divergence-logged as
approximation. Priority order:
1. Mysterious Ruins, 9 groups, 117 territories (the user's called-out bland pocket).
2. Near Base ring, 5 groups, 61 territories (high traffic early-leveling band).
3. Timeless Woods east arc, 3 groups, 39 territories.

Quest effect: unblocks gate (c) for 1324 (which then unblocks 1327 RESTORE+FIX, its own
dialog fix 304 to 300921), and clears the mob side of 1307/1308/1332/1333/1347/1349.

Embedded DECISIONs (small): rockcrawler group 1300033 and stone-head group 1300058 have no
v31 donor anywhere (proposed: generic combat / environment profiles); group 1300029
roster choice (fightable corrupted-Terron vs ambient spirit; default fightable).

### Decisions for the user

D1. NPC spawn additions (9 NPCs, templates intact in v31 NpcData, zero spawns in either
    era; positions would come from v17 client data). Doctrine rule 5 is mobs-only, so this
    needs explicit approval as a logged adaptation. Unlocks: 1334 (relics repeatable),
    1332+1333 (Leander research pair), 1347, 1349 (the ONLY quest of the Mysterious Ruins
    proper), 1319, plus the D2 story-bridge quests. Recommendation: approve for the 7
    NPCs behind non-story quests (Eria Elin, Rabram, Beres, Muriel, Eredos, Mayer,
    Theon optional); hold Pelaeni/Rian Kubel for D2.
    UPDATE 2026-07-20: user directed restoration of the six non-story givers provided
    their quests are collision-free (they are: all CLEAN or OVERLAP-BENIGN, reward-clean).
    Approximate positions recovered from the v17 client StrSheet_NpcLoc quest markers,
    collision-checked against the live baseline: see padding-npc-locations.md/.json.
    Five HIGH confidence, Muriel MEDIUM (marker sits on the Timeless Woods approach,
    2500u from Dulari's Camp; author at marker, nudge in tuning if needed). Identity
    note (corrected by the NpcLoc sweep): the EN-client vs KR-server name differences
    (EN Kamarnu = KR Rabram, Jehan = Beres, Lorin = Mayer, Ayrdoss = Eredos,
    Clovis = Muriel) are a NA/EU vs KR localization split spanning nearly all IoD
    villagers, stable across v17/v31 EN, not a rename over time; match by
    (hz, templateId) only. Headings are not recoverable; set provisionally and tune
    in-game.
D2. Story-bridge quartet 1306/1307/1308/1310 (+1343/1344): AWKWARD-DUPLICATE cut subplots.
    Options: (a) OUT, keep the compressed arc clean; (b) enable gated behind live 1317
    completion as post-story side content; (c) enable on their v17 anchors and accept the
    retold beats. 1310 additionally needs a title disambiguation and carries a reward flag.
    Recommendation: (a) for 1306/1307/1308/1310; for 1343/1344 (gate-clean, no stranding,
    strong content) either (b) or accept the lore-reveal overlap consciously.
D3. Reward-flagged 1326/1330 (gate-clean otherwise): enable with v31 rewards as-is
    (duplicate ilvl7 piece vs live 1305 set) or swap the gear piece for a consumable
    (logged adaptation). Recommendation: enable as-is; duplication is mild (vendor trash
    value) and faithful.
D4. Courier branch 1335/1337/1338/1336: gate-clean but stranded behind 1310 (D2). Option:
    re-anchor 1335 onto live 1309 (v17 grandparent) and enable all four without 1310.
    Recommendation: re-anchor, logged as adaptation.
D5. 1389 Pandora box tutorial: expressible but Korean-only strings, teaches a double-loot
    consumable (economy fit question). Recommendation: DEFER.
D6. RESOLVED by the NpcLoc sweep (padding-npcloc-sweep.md section 4): the 1348 targets
    (302/303) and 1319 targets (300941/300944) have zero v17 fences but carry NpcLoc
    marker clusters (10 and 17 markers respectively), the only data-derived positions.
    1348's cluster sits in the Near Base staging band (x 63k-68k, y -83k..-85k); 1319's
    sits beside Muriel's own marker (x 78k-81k, y -82k..-87k). Recommendation: author
    bespoke quest-mob territories from these marker clusters (fence = cluster hull,
    donor population profile), logged as approximations; both quests join the restore.
D7. Optional ambient villagers surfaced by the sweep: 213,1018 (EN Riel / KR Koren,
    Prefect) and 213,1137 (EN Milun / KR Remaniel, Apprentice Priest), unspawned in
    both eras, single v17 markers near the northern hub garden, referenced by no quest.
    Pure presence/flavor; restore only if the user wants a hub-population pass
    (positions available).

### Out

1385 (superseded by patch-000 1384 charm flow; prior ruling stands).

### Sequencing and process

- Spec numbering: Wave A = spec 14 (quest enables + 2 dialog fixes), Wave B = spec 15
  (habitat groups, generator-driven from padding-habitat-gaps.json). Decision-dependent
  waves get 16+ after rulings.
- Apply via migrate batch replay only; NpcLoc regen with prune after any spawn change;
  world restart manual (user).
- Live-test checkpoints: 1346 instance entry/completion, 1322/1327 fixed dialogs, one
  repeatable cycle on 1341, ruins density walkthrough.
- After Waves A+B land: pacing review of the 1-to-11 curve per the framework (17+ side
  quests and repeatables add alternative leveling).
