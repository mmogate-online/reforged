# Classification: NPC Stats / Behaviour (axis 4)

Target: **v31 stat blocks for all 218 v17-rostered templates**. Roster total: 218.

Verdict counts: MATCH=218

> Baseline stat VALUES were not byte-diffed against v31 for all 218; baseline is a v31 port so MATCH is expected. Spot-check via datasheet-v92 NpcTemplate confirmed an EXACT match on sampled templates (hz13/1 Pigling: maxHp 88.4572514565471, level 3, atk 20, def 46.656 identical in baseline and v31 artifact). Recommend a full per-template stat diff during spec authoring; any drift found (patch-000 or manual fixes) should be re-flagged RESTORE.

## Out-of-roster extras (informational; present v31+v92, absent v17)

| hz | templateId | name | classification |
|----|-----------|------|----------------|
| 64 | 8000 | Ellonia | EXTRA_V31+EXTRA_V92 |
| 213 | 1054 | Sandom | EXTRA_V31+EXTRA_V92 |
| 213 | 1150 | Todoro | EXTRA_V31+EXTRA_V92 |
| 213 | 1151 | 콰탕카 | EXTRA_V31+EXTRA_V92 |
| 213 | 1152 | Karlikan | EXTRA_V31+EXTRA_V92 |
| 213 | 1153 | Amekel | EXTRA_V31+EXTRA_V92 |
| 213 | 1501 | Kelsaik's Nest Teleportal | EXTRA_V31+EXTRA_V92 |

## Per-template verdicts (RESTORE rows only; MATCH summarised in counts)

_All 218 rostered templates classified MATCH (v31 port). No RESTORE rows._
