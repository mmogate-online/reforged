# NPC template-ID alignment (Island of Dawn)

Cross-source check of every v17 roster NPC `(huntingZoneId, templateId)` against v31 and v92 `NpcData_<hz>.xml`, plus reverse-direction server extras.

Name-resolution path: server Template `name` is Korean (compared v31 vs v92 as the sharp rename signal); the English `race` enum anchors the roster row to the server row across languages; the v17 English name (old client) is compared to the current v92 client StrSheet_Creature English name for the same key.

## Counts

| Classification | Count |
|---|---|
| ALIGNED | 218 |
| RENAMED | 0 |
| MISSING_IN_V31 | 0 |
| MISSING_IN_V92 | 0 |
| EXTRA_V31 | 7 |
| EXTRA_V92 | 7 |

Per-zone key counts (v17 / v31 / v92 template totals):

| Zone | v17 | v31 | v92 |
|---|---|---|---|
| 13 | 57 | 57 | 57 |
| 64 | 50 | 51 | 51 |
| 213 | 87 | 93 | 93 |
| 313 | 8 | 8 | 8 |
| 364 | 8 | 8 | 8 |
| 436 | 8 | 8 | 8 |

## RENAMED / MISSING v17 rows (id landmines)

RENAMED here means genuine id reuse: the same `(hz,tid)` carries a different canonical Korean server name in v31 vs v92. That is the signal that would break keying.

**None.** Every v17 roster NPC key is present in both v31 and v92, and its canonical Korean Template name is identical between the two servers, so no id was reused for a different creature.

## Informational drift (NOT id landmines)

These rows are ALIGNED: the `(hz,tid)` id is stable and the canonical Korean server name is identical v31 vs v92. Only the client English display name was revised across region/patch (`DISPLAY_EN_DRIFT`), or the `race` attribute is recorded differently between the v17 roster and the server (`RACE_REPR_DRIFT`, e.g. a corpse tagged `object` in the roster but the model race `Human` on the server). Listed for restoration awareness only.

| hz | tid | drift | v17 name | v92 client EN | v17 race | v92 race | v31 ko = v92 ko |
|---|---|---|---|---|---|---|---|
| 64 | 1006 | DISPLAY_EN_DRIFT | Jhon | Jorhon | Human | Human | yes |
| 64 | 1050 | DISPLAY_EN_DRIFT | Hermaiorni | Tainted Gorge Teleportal | Popori | Popori | yes |
| 64 | 2501 | DISPLAY_EN_DRIFT | Teleportal | Tainted Gorge Bridge Teleportal | object | object | yes |
| 64 | 9000 | DISPLAY_EN_DRIFT | T-cat Exchanger | Tikat | popori | popori | yes |
| 213 | 1015 | DISPLAY_EN_DRIFT | Teleportal | Karascha's Lair Teleportal | object | object | yes |
| 213 | 1020 | RACE_REPR_DRIFT | Priscus | Priscus | Castanic | Human | yes |
| 213 | 1033 | RACE_REPR_DRIFT | Roderic | Roderic | object | Human | yes |
| 213 | 1034 | RACE_REPR_DRIFT | Sybella | Sybella | object | Human | yes |
| 213 | 1035 | RACE_REPR_DRIFT | Eldred | Eldred | object | Human | yes |
| 213 | 1053 | DISPLAY_EN_DRIFT | Detector Stone | Obelisk | object | object | yes |
| 313 | 1004 | DISPLAY_EN_DRIFT | Slagger | Harger | human | human | yes |
| 313 | 1006 | DISPLAY_EN_DRIFT | Simons | Misrile | Highelf | Highelf | yes |
| 313 | 1007 | DISPLAY_EN_DRIFT | Teiger | Jilva | castanic | castanic | yes |
| 436 | 1501 | DISPLAY_EN_DRIFT | Teleportal | Exit Teleportal | object | object | yes |

## Reverse-direction extras (present in server, absent from v17)

Candidate REMOVE/ignore set: server NPCs the v17 roster does not list. All are present in both v31 and v92 unless a single-server tag says otherwise.

| hz | tid | tag | v92 ko name | v92 client EN | race | in v31 | in v92 |
|---|---|---|---|---|---|---|---|
| 64 | 8000 | EXTRA_V31+EXTRA_V92 | 꼬마 마녀 엘로니아 | Ellonia | monster | yes | yes |
| 213 | 1054 | EXTRA_V31+EXTRA_V92 | 출장 잡화 상인 | Sandom | popori | yes | yes |
| 213 | 1150 | EXTRA_V31+EXTRA_V92 | 토도롱 | Todoro | popori | yes | yes |
| 213 | 1151 | EXTRA_V31+EXTRA_V92 | 콰탕카 |  | monster | yes | yes |
| 213 | 1152 | EXTRA_V31+EXTRA_V92 | 칼링 투르칸 | Karlikan | Aman | yes | yes |
| 213 | 1153 | EXTRA_V31+EXTRA_V92 | 아메리아 쿠벨 | Amekel | Highelf | yes | yes |
| 213 | 1501 | EXTRA_V31+EXTRA_V92 | 차원의 마법석(이벤트던전) | Kelsaik's Nest Teleportal | object | yes | yes |
