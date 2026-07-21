# v17 -> v92 Structural Checks (Island of Dawn)

## (a) Fence-ring drift of the 8 surviving sections

v17 client `Area/Area-00004.xml` (continentId 13) vs v92 client `Area/Area-00013.xml` (continentId 13). Each section's own ring is its direct `<Fence>` children (sections nest inside the outer 13001 zone section). Note: the v17 file stores fence coordinates at 4 decimals while v92 stores 8, so an identical ring shows a residual deviation up to the rounding tolerance (0.001).

| Section | v17 verts | v92 verts | Vertex-identical | Max deviation | Verdict |
|---------|-----------|-----------|------------------|---------------|---------|
| 13001 | 10 | 10 | yes | 6.8e-05 | identical (rounding only) |
| 13003 | 11 | 11 | yes | 6.6e-05 | identical (rounding only) |
| 13004 | 18 | 18 | yes | 6.8e-05 | identical (rounding only) |
| 13006 | 7 | 7 | yes | 4.8e-05 | identical (rounding only) |
| 13007 | 4 | 4 | yes | 7.4e-05 | identical (rounding only) |
| 13024 | 8 | 8 | yes | 6.6e-05 | identical (rounding only) |
| 13028 | 10 | 10 | yes | 6.3e-05 | identical (rounding only) |
| 13030 | 13 | 12 | NO | 8405.575844 | drift (vertex count changed; ring reshaped) |

**Verdict:** 7 of 8 sections are vertex-identical (same vertex count; every position equal within decimal-rounding, i.e. the only numeric difference is v92's extra decimal digits).

- Section `13030` is genuinely drifted: vertex count 13 -> 12 and the ring was reshaped (the change is far larger than rounding; max nearest-vertex distance 8405.575844 units). This is a real boundary edit in v92, not a formatting artifact: the southern arc of the ring was relocated.

## (b) Free-id check for candidate region ids 13036-13039

Families scanned in BOTH v92 client and v92 server: `StrSheet_Region`, `AreaData`, `Area`, `NewWorldMapData`, `MapDefineData`, `TeleportData`, `GuardData`.

| Candidate | v92 client | v92 server | Free |
|-----------|-----------|-----------|------|
| 13036 | clear (1 coord. false-positive) | clear (1 coord. false-positive) | yes |
| 13037 | clear | clear | yes |
| 13038 | clear | clear | yes |
| 13039 | clear | clear | yes |

The only textual matches are coincidental coordinate fragments, not region-id usages:

- v92-client `Area` / Area-00018.xml: `13036` appears only as a coordinate fragment (`...313" /> <Fence pos="111121.13281250,-68893.80468750,13036.72753906" />...`), not a region id.
- v92-server `AreaData` / AreaData_2000_FDI_C_P.xml: `13036` appears only as a coordinate fragment (`...2.93945313"/> <Fence pos="111121.13281250,-68893.80468750,13036.72753906"/> <Fenc...`), not a region id.

**Verdict:** candidate region ids 13036-13039 are ALL FREE in both the v92 client and the v92 server across every family listed.

### Standard-conformance of 13036

Contiguous 13xxx region-name ids present in `StrSheet_Region`:

- v92 client: 13001..13035 (35 ids, contiguous)
- v92 server: 13001..13035 (35 ids, contiguous)

Both sides run 13001..13035 with no gaps, so 13036 is the next sequential id. The domain reference `datasheet-domain/.../reference/zone-id-conventions.md` documents the section nameId / StrSheet_Region encoding `XXYYY` (XX = base HZ 10-99, YYY = sub-region), e.g. `13004` = HZ 13 sub-region 004. Thus 13036 = HZ 13 sub-region 036 = 13*1000+36 follows the hz*1000+seq pattern and is standard-conforming as the next IoD region id.

