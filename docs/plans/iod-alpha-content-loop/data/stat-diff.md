# IoD NPC Stat VALUE Diff (v31 source vs v92 baseline)

Full-Template value comparison for every v17-rostered NPC template: all template-level attributes plus every attribute on the <Stat> child. Numeric formatting differences ("100.000000" vs "100", trailing spaces) are treated as equal; only genuine value differences are flagged.

- v31 source: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet`
- v92 baseline: `D:\dev\mmogate\tera92\server\Datasheet` (git HEAD baseline (dirty files) / disk (clean files))
- Roster: 218 templates (IDENTICAL=218, DRIFT=0, MISSING=0)
- **Verdict: ALL-MATCH**

## Per-zone summary

| HZ | Roster | IDENTICAL | DRIFT | MISSING |
|----|-------:|----------:|------:|--------:|
| 13 | 57 | 57 | 0 | 0 |
| 64 | 50 | 50 | 0 | 0 |
| 213 | 87 | 87 | 0 | 0 |
| 313 | 8 | 8 | 0 | 0 |
| 364 | 8 | 8 | 0 | 0 |
| 436 | 8 | 8 | 0 | 0 |

## Drift detail

No drift and no missing templates. Every rostered template carries an identical stat block in v92 versus v31. No restore spec is needed on the NPC-stats axis.
