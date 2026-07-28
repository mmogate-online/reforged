# dc-restore test suite

```powershell
python -m pip install -r reforged/requirements-dev.txt   # once
python -m pytest                                          # from reforged/
python -m pytest -m "not corpus"                          # hermetic tier only
python -m pytest -rs                                      # show why anything skipped
```

`pytest.ini` at `reforged/` sets `rootdir`, points `testpaths` at this folder and puts
`tools/dc-restore` on `pythonpath`, so `import dclib` works without any install step.

## Two tiers

| Tier | Marker | Source | Answers |
|---|---|---|---|
| hermetic | none | committed fixtures under `fixtures/`, or trees built by the `corpus_dir` factory | do the parsers and checks handle the byte shapes and edge cases correctly |
| corpus | `corpus` | the real v92 server datasheet at the pinned commit `789fec28` | does the check actually fire on the real historical defect it was written for |

The corpus tier skips with a stated reason when `.references` or the private datasheet
repo is unavailable, so a clean clone runs the hermetic tier and reports the rest as
skipped rather than failing.

## Why the baseline commit is pinned

`BASELINE_REF` in `conftest.py` is `789fec28`, the datasheet state before the patch-002
Island of Dawn trimming and redistribution wave (specs 002/27 to 002/33). Every audit
check owes its existence to a defect that lives in that state. HEAD advances each time a
patch closes, so an oracle written against HEAD silently turns from "fires on the defect"
into "asserts nothing about anything" on that day.

Because the ref is pinned, exact corpus counts ARE legitimate assertions here: the data
cannot move underneath them. The audit tool itself must still regenerate every census at
runtime rather than carrying baked-in numbers.

## Conventions

- A check ships with a positive oracle (fires on the known defect) and a negative oracle
  (stays silent on the known-legitimate lookalike). The negative half is what keeps a
  noisy check from being declared working.
- `test_harness.py` holds self-tests for the machinery, including a strict xfail proving a
  false assertion is reported as a failure.
- A strict xfail marked `P<n>:` is a ratchet on unfinished work: it turns into a failure
  the moment the fix lands, which is the signal to promote it to a plain assertion.
