# IoD Client Registry Leg (Phase 5 execution)

Executes the two client-only tasks of Phase 5 after the 12-spec batch was applied server-side and
migrate's manifest-narrowed sync updated the mapped client families. Covers (1) `StrSheet_NpcLoc`
regeneration with pruning and (2) `MapDefineData` dangling-label cleanup for the removed 13035
section. Companion doctrine: `../../DOCTRINE.md` rule 8; tracker map-diff ruling 5 in `../TRACKER.md`;
pre-check `client-registry-readiness.md`.

Sources (read-only cross-check):
- v31 client: `Z:\tera pserver\v31.04\client-dc_v31\DataCenter_Final_EUR_v31`
- applied server datasheet: `D:\dev\mmogate\tera92\server\Datasheet`
- v92 client (edit target): `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR`

## Task 1: StrSheet_NpcLoc regeneration with prune

### Tool change (`tools/dc-restore/gen_npcloc.py`)

Added a `--prune` flag (default OFF, so the old replace-by-key behavior is preserved verbatim).

- Default mode is unchanged: replace-by-key. Only the `(hz, templateId)` keys the regeneration
  produces are removed and rewritten; any other client key in those zones is left alone.
- `--prune` mode is replace-by-zone: for each covered zone (13, 64, 213, 436) EVERY existing client
  `<String ... huntingZoneId="hz">` row is removed first, then the regenerated set is written. The
  effect is that a zone's contents become exactly the regenerated set, so stale v92-only rework-roster
  keys (which the regeneration does not produce) are dropped. Zones outside `ZONES` are never touched
  in either mode.
- Both modes stay deterministic and idempotent. The prune removal targets any templateId
  (`templateId="\d+"`) for the covered zones rather than a fixed key list, so a re-run removes the
  rows it just wrote and rewrites an identical set.
- Docstring updated (also corrected the stale "v17-authoritative" wording to v31-authoritative per
  the adopted doctrine).

Run command (executed WITH prune):

```
cd reforged/tools/dc-restore
python gen_npcloc.py --prune
```

First run output: `[prune (replace-by-zone)] removed 45 existing entries; wrote 122 entries: hz13=31, hz64=34, hz213=51, hz436=6`

### Per-zone entry counts (before / after / v31-client cross-check)

| HZ | v92 client BEFORE | pruned (removed) | regenerated (AFTER) | v31 client | all v31-client keys covered? |
|---|---|---|---|---|---|
| 13 | 42 | 42 | 31 | 21 | Yes (21 of 21) |
| 64 | 0 | 0 | 34 | 16 | Yes (16 of 16) |
| 213 | 0 | 0 | 51 | 26 | Yes (26 of 26) |
| 436 | 3 | 3 | 6 | 2 | Yes (2 of 2) |
| total | 45 in-zone | 45 | 122 | 65 | Yes (65 of 65) |

The "removed 45" equals the 42 stale HZ-13 rework keys plus the 3 HZ-436 v92 keys; HZ-64 and HZ-213
were already empty in the v92 client (the rework had dropped them). File total went from 3999 to 4076
Strings.

### v31-client cross-check result

Per zone, comparing the regenerated key set (from applied server TerritoryData) against the v31 client
NpcLoc key set:

- **(hz, templateId) present in v31 client but MISSING from our regenerated set: NONE, in all four
  zones.** The regeneration is a complete superset of the authentic v31 client registry, so every
  quest-link/ping location the v31 client shipped is covered.
- The regenerated set additionally contains keys the v31 client did not carry (HZ-13 adds
  101/102/111/555/556/557/558/999/1003/1011; HZ-64 adds 18 more; HZ-213 adds 25 more; HZ-436 adds
  1001/1011/1030/1101). These are TerritoryData spawn templates (mobs and secondary engine NPCs) that
  the v31 client did not curate into its location registry. This is expected: `NpcLoc` in the v31
  client is a hand-curated subset of quest-relevant NPCs, whereas `gen_npcloc.py` emits one row per
  non-void spawn from server state (doctrine rule 8: regenerate from ported server state, cross-check
  against v31 client). The v31 client is the coverage floor, not an exact target; the floor is met.
- The brief's example of engine-spawned templates "like 213/1036" legitimately differing did not
  materialize: no v31-client key was absent from the regen, so there was nothing to reconcile.

Verdict: PASS. Zero v31-client coverage lost; the extra rows are harmless server-derived spawn
locations, consistent with the regenerate-from-server doctrine.

### Verification

- Idempotency confirmed: a second `--prune` run reported `removed 122; wrote 122` and produced an
  identical file.
- Resulting file parses as well-formed XML.
- `git diff` on the client-dc working tree touches only the four covered zones
  (huntingZoneId 13/64/213/436) and nothing else: 122 insertions, 45 deletions in
  `StrSheet_NpcLoc-00000.xml`.

## Task 2: MapDefineData dangling-label cleanup (removed section 13035)

Section 13035 (Ruined Temple) was removed server-side this run (per tracker sections-diff ruling 2).
Its 2 dangling client minimap labels have no DSL sync coverage and were removed by hand.

### Rows removed (exact, reproducible)

| File | MapDefine id | Removed row | Attributes |
|---|---|---|---|
| `MapDefineData/MapDefineData-00048.xml` | `WMap_ATW_Death_Empty` | `<Text ... stringId="13035" ... />` | x=420 y=370 stringId=13035 click="" align=left fontStyle=spot |
| `MapDefineData/MapDefineData-00049.xml` | `WMap_ATW_Death_Field` | `<Text ... stringId="13035" ... />` | x=420 y=370 stringId=13035 click="" align=left fontStyle=spot |

Both were the sole 13035 references in the entire MapDefineData family; each was line 6 of its file,
the fourth `<Text>` child of its `<MapDefine>`. One `<Text>` line removed per file, nothing else
touched.

### Dangling proof (why removal is safe)

1. Server IoD area file `AreaData/AreaData_13_ATW_Death_P.xml` contains no section 13035 (all other
   IoD sections 13001..13034 plus 64001/64007 are present; 13035 is absent). The section is gone
   server-side.
2. Client `AreaData` has zero 13035 references. The section is gone client-side too.
3. Client `StrSheet_Region/StrSheet_Region-00000.xml` has zero `13035` references, while all nine
   sibling label stringIds in the same MapDefine rows (13030, 13003, 13004, 13007, 13013, 13024,
   13006, 13028, 13031) still resolve to a region string. The label's target string was removed with
   the section, so the row rendered a broken/empty label. Only 13035 dangles; every sibling label was
   left intact.
4. The v31 client MapDefineData has zero 13035 references, confirming 13035 was a v92-only label
   introduced by the "Death" reskin maps; removal returns these minimaps toward their v31 state.

### Verification

- Both edited files parse as well-formed XML.
- Zero `13035` references remain anywhere in the MapDefineData family.
- `git diff` on the client-dc working tree: 2 files changed, 2 deletions, each exactly the one 13035
  `<Text>` row, nothing else.

## Defect addendum: void (0,0,0) spawn positions (2026-07-20, post live-test)

### What was wrong

The first `--prune` pass wrote position strings verbatim from the server spawn rows. Party members
and random-in-fence singles store `pos = 0,0,0` (the engine picks a real point inside the containing
territory's fence at spawn time), so those keys were emitted as dead `13#0,0,0|...` link targets.
Live testing found quest links for the party-spawned mobs Stonebeak Raider/Brigand/Highcrest
(HZ 13, templates 301191/301193/301194, the "Climbing Through the Ranks" targets) resolving to
nothing. The original v31-client cross-check compared KEYS only, so the bad VALUES slipped through.
The defective file carried 375 `#0,0,0` tokens across the four covered zones (365 in HZ 13, 10 in
HZ 436; HZ 64 and HZ 213 had none).

### Fix rule (in `gen_npcloc.py` `collect()`)

Position resolution is now per spawn row:

- Non-void pos: used verbatim, as before.
- Void pos (all coords 0): replaced by the fence centroid (arithmetic mean of the containing
  `Territory`'s `Fence` vertices, x/y/z). One point per spawn row, so a template that spawns in N
  territories emits N distinct points; co-territorial party members (301191/301193/301194) share the
  same per-territory centroid, reproducing the v31 client's shape.

`collect()` was restructured to iterate `Territory` elements (computing each centroid once) rather
than a flat `Npc` sweep. Helpers `is_void_pos()` and `fence_centroid()` were added. A guard in
`main()` aborts if any `#0,0,0` token survives into the emitted set, and the run banner reports
`(0 void 0,0,0 tokens)`. Determinism, idempotency, and `--prune` replace-by-zone semantics are
unchanged.

### Validation evidence (re-run WITH `--prune`)

Run banner: `[prune (replace-by-zone)] removed 121 existing entries; wrote 121 entries (0 void 0,0,0 tokens): hz13=31, hz64=33, hz213=51, hz436=6`

1. **Zero void tokens.** The in-tool guard passed (0), and an independent scan of the written file
   finds zero `13#0,0,0` tokens in the four covered zones (was 375).
2. **Values cross-check against the v31 client (not just keys).** All 65 v31-client keys in the
   covered zones are present in our set, and point COUNT matches for 65 of 65 keys, so the emitted
   spawn-set shape equals the v31 client for every shared key.
3. **Centroids fall inside their territories.** A 2D point-in-polygon test over every territory that
   contains a void spawn: 311 of 311 centroids lie inside their own fence polygon.
4. **301191/301193/301194 before / after / v31 (HZ 13, first 3 of 14 points each):**

   | # | before (defective) | after (ours) | v31 client |
   |---|---|---|---|
   | 1 | 13#0,0,0 | 13#72305,-75897,-2726 | 13#72340,-75898,-2725 |
   | 2 | 13#0,0,0 | 13#68527,-75534,-2772 | 13#68563,-75535,-2772 |
   | 3 | 13#0,0,0 | 13#71517,-75069,-2780 | 13#71553,-75070,-2779 |

   Each template now emits 14 points (matching v31's 14), the point list is identical across all
   three co-territorial templates (matching the v31 client), and our fence-centroid sits within about
   36 units on X and about 1 unit on Y/Z of the v31 authored point, in the same row order. Exact
   equality is not expected (BHS authored its points), but the centroids are effectively the same
   representative points.
5. Resulting file parses as well-formed XML; `git diff` touches only zones 13/64/213/436
   (121 insertions, 45 deletions) and adds zero `#0,0,0` tokens.

### Server-state note (supersedes the Task 1 counts above)

HZ 64 regenerated to 33 keys on the fix run, not the 34 recorded in the Task 1 table. Between the two
runs an external process rewrote `TerritoryData_64.xml` (mtime 19:18) and dropped template 9000's
spawn from HZ 64, so 9000 correctly no longer receives an NpcLoc entry. The tool deterministically
mirrors current server state; the 34 to 33 shift is server drift during this leg, not a tool change.
Final per-zone written counts: hz13=31, hz64=33, hz213=51, hz436=6 (121 total); removed 45 stale
in-zone keys (42 HZ 13 + 3 HZ 436).

## Note for the orchestrator

No pack/install/publish was performed (deploy-client is the orchestrator's step). Tracker was not
updated by this leg. All edits are in the client-dc git working tree
(`D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR`): `StrSheet_NpcLoc-00000.xml` and
`MapDefineData-00048/-00049.xml`. The `gen_npcloc.py` tool change is in the reforged repo working tree.
Heads up: `TerritoryData_64.xml` on the server tree was modified at 19:18 during this leg (template
9000 spawn dropped from HZ 64); if that was not an intended concurrent edit, reconcile before deploy.
