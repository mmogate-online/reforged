# Classification: Spawns / Territories (axis 3)

Target: **v31 spawn entries mapped through identity (exact + near-group) territory matches**

Verdict counts: DECISION=3, MATCH=35, RESTORE=17

> Cross-group near matches are spatial coincidences (losses), not restorable correspondences. MATCH groups (baseline == v31 port) are summarised in hz_summary, not emitted per-row.

## Per-HZ summary

| hz | v17 grps | v31 grps | base grps | deleted-v17-only (RESTORE) | matched (MATCH) | v31-only (DECISION) | exact terr | near terr | near x-grp |
|----|----------|----------|-----------|----------------------------|-----------------|---------------------|------------|-----------|-----------|
| 13 | 40 | 25 | 25 | 17 | 23 | 2 | 200 | 127 | 91 |
| 64 | 2 | 2 | 2 | 0 | 2 | 0 | 13 | 1 | 0 |
| 213 | 3 | 4 | 4 | 0 | 4 | 1 | 11 | 3 | 0 |
| 313 | 1 | 1 | 1 | 0 | 1 | 0 | 6 | 0 | 0 |
| 364 | 1 | 1 | 1 | 0 | 1 | 0 | 3 | 1 | 0 |
| 436 | 4 | 4 | 4 | 0 | 4 | 0 | 17 | 0 | 0 |

## Actionable rows (RESTORE / DECISION)

| hz | group_id | desc | verdict | provenance | note |
|----|----------|------|---------|------------|------|
| 13 | 1300019 | 태고의 숲_중반(자연의 정령) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300020 | 태고의 숲_후반(길리두) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300021 | 태고의 숲_후반(선공 길리두) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300022 | 기지 인근(자연의 정령) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300025 | 기지 인근(아르가스) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300028 | 기지 인근(어둠의 약탈자) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300029 | 기지 인근(타락한 자연의 정령) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300030 | 기지 인근(검은틈쪽 오염된 흙의 정령) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300031 | 태고의 유적지(아르가스) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300032 | 태고의 유적지(타락한 흙의 정령) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300033 | 태고의 유적지(스톤 크라울러) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300034 | 태고의 유적지(죽어가는 크로모스) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300036 | 태고의 유적지(야영지 외곽 오칸 미니미)  | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300037 | 태고의 유적지(야영지 내부 어둠의 약탈자) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300038 | 태고의 유적지(오칸 순찰) | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300057 | 태고의 유적지_환경_자연의 정령 | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300058 | 태고의 유적지_스톤 헤드 | RESTORE | v17 | geometry from v17 territory fences; population from correlat |
| 13 | 1300140 | 사원 인근_환경_테론 | DECISION | v31-gapfill | v31-only territory group, absent from v17 roster |
| 13 | 1300141 | 사원 인근_환경_꿀벌 | DECISION | v31-gapfill | v31-only territory group, absent from v17 roster |
| 213 | 21300004 | 연맹 퀘스트 | DECISION | v31-gapfill | v31-only territory group, absent from v17 roster |
