# IoD Region Strings Diff (v31 vs clean v92)

Phase 3 artifact. Family: `StrSheet_Region.xml` (server, monolithic both eras). Scope: IoD id bands
13000-13999, 64000-64999, 9036000-9036999, plus continent name 202. Machine data:
`region-strings-diff.json`.

Sources (read-only):
- v31: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet\StrSheet_Region.xml`
- v92: `D:\dev\mmogate\tera92\server\Datasheet\StrSheet_Region.xml`

## Verdict counts

| Verdict | Count |
|---|---|
| MATCH | 41 |
| DECISION | 5 |
| PORT | 0 |

46 in-scope ids. **Every classic IoD region name already exists in v92 and matches v31 exactly.**
No region-string PORT or add is needed for any restored section - the restored sections reuse the
surviving, identical strings.

## DECISION rows (v92-only strings)

The only 5 non-MATCH rows are v92-only strings, and they are exactly the 5 v92-only sections:

| id | v92 string | Pairs with | Disposition (mirrors section verdict) |
|---|---|---|---|
| 13031 | North Dock | section 13031 (KEEP-flag) | KEEP if section kept |
| 13032 | Dulari's Camp | section 13032 (= v31 13017) | DECISION (renumber cluster) |
| 13033 | Southern Checkpoint | section 13033 (= v31 13020) | DECISION (renumber cluster) |
| 13034 | Tainted Gorge Outpost | section 13034 (= v31 13027) | DECISION (renumber cluster) |
| 13035 | Ruined Temple | section 13035 (REMOVE) | REMOVE with its section |

The 13032/13033/13034 strings are byte-identical to the classic 13017/13020/13027 strings (also
present and MATCH), which is the proof the v92 renumber preserved the names. See sections-diff.md
for the cluster decision.

## Key correction to prior (v17-era) art

- **13013 = "Airship Approach"** in v31 AND v92 (MATCH). The v31 section with nameId 13013 is
  Airship Approach, not "Terron Run". No 13036 allocation is warranted.
- **13015 = "Abandoned Camp"** in v31 AND v92 (MATCH). Not "Leander's Outpost" (that name is a
  different region, id 64003, present and MATCH both eras). No 13015 string revert is warranted.

The retired `gen_section_specs.py` REGION_UPSERTS (13036 Terron Run, 13015 Leander's Outpost) are
built on v17 data and are contradicted by the v31 source. Under v31-primary they should be dropped.

## Language check

All 46 in-scope rows are English in both eras (non-ASCII scan clean; apostrophes are ASCII). No
non-English StrSheet_Region rows found in the IoD bands. (Korean text exists only in AreaData/
NewWorldMapData `desc` dev-comment attributes, which are not player-facing.)
