---
name: server-load-diagnosis
description: >
  Diagnose a dev world server that fails to start after a datasheet deploy: silent
  access-violation crashes during startup validation, "Failed to Parse XML"
  rejections, and Korean loader lines that look fatal but are routine warnings.
  Covers the crash artifacts on the dev box (UTF-16LE console log, .crash and .dmp
  files), reading the symbolized call stack to name the failing validator, comparing
  a failing boot against a known-good boot, the file invariants the loader enforces,
  and how to bisect a bad datasheet across restart cycles. Use when the world server
  dies or hangs during startup after a deploy, when a deployed change never appears
  in game, when a log line must be classified as blocker or warning, or when a load
  failure must be narrowed to one file.
disable-model-invocation: false
user-invocable: true
---

# Diagnose a World Server Load Failure

The server loads datasheets at startup only, and when it dies during that load it
tells you very little. This is the forensic path from "it will not come up" to a
named file.

Restarts are the user's manual step. Every restart costs them minutes, so make each
one test exactly one thing.

## 1. The artifacts live on the dev box, not in this repo

Resolve `dev_server_ssh` and `dev_server_root` from `.references`. The local
`server/Log` folder in a datasheet checkout is unrelated and usually stale.

| Artifact | Path | Notes |
|---|---|---|
| Console log | `<dev_server_root>/Log/WorldServerConsole_<YYYY-MM-DD>_2800.log` | UTF-16LE, one file per day, appended per boot |
| Crash report | `<dev_server_root>/*.crash` | text, partially symbolized, written on access violation |
| Minidump | `<dev_server_root>/*_mini.dmp` | ~400 MB |
| Full dump | `<dev_server_root>/*_full.dmp` | multi-GB, rarely worth moving |

The console log is UTF-16LE: reading it as UTF-8 yields spaced-out garbage. Decode it
explicitly.

```python
raw = open(path, 'rb').read()
text = raw.decode('utf-16-le', errors='replace').replace('\ufeff', '')
```

Crash filenames contain parentheses, which breaks `scp` quoting. Copy to a simple
name on the remote first, then pull it:

```bash
ssh "$TARGET" 'Copy-Item -LiteralPath (Get-ChildItem <dev_server_root> -Filter *.crash | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Destination <dev_server_root>/latest.crash -Force'
```

Check the server clock (`ssh "$TARGET" 'Get-Date'`) before concluding a crash belongs
to your deploy: the dev box may not share your timezone.

## 2. Identify the failure shape

| Shape | Console signature | Meaning |
|---|---|---|
| Parse rejection | `Failed to Parse XML [...]: ... UTF8 파일인지 확인`, then `[<Sheet>] Loading Error!` and `Datasheets Loading Error!` | File level, and the log NAMES the files. Malformed XML or missing BOM |
| Validation crash | Log stops mid `Validation Check [...]` sequence; a `.crash` file appears | A cross-reference dereferenced null. No file named |
| Healthy boot | `...노드를 찾을 수 없습니다` warnings, then the `Validation Check` sequence completes | Not your blocker (see section 4) |

A parse rejection is the good case: fix the named file. A validation crash gives you
nothing but a fault address, and that is where the rest of this skill applies.

**A fourth shape is not a server failure at all: the world came up clean and the change
simply is not there.** Before diagnosing the game server, rule out the three cheaper
explanations in this order, because each is invisible from in game and none produces an error:

1. **The file never reached the box.** `deploy_dev.py` mirrors only files that differ from git
   HEAD, so a reverted file is silently left stale on the dev server. Treat the deploy summary's
   file COUNT as a checksum against the number of files you expect to have changed.
2. **The apply never wrote it.** An operation that decomposes to zero commands still counts
   toward the reported op total and only warns (W503). Reconcile counts, and check the working
   tree with `git status` rather than assuming.
3. **You are reading stale tooling, not stale data.** If a datasheet query disagrees with the
   file on disk, check `datasheet_freshness`; if a documented MCP tool or entity type appears
   to be missing outright, the `.mcp/` binary is a build behind, which fails silently from
   inside a session. Both are covered in `domain-research`.

## 3. Read the symbolized stack, not the raw one

Two traps in the `.crash` file:

- **The top frame is often not the fault.** If a frame sits ABOVE
  `KiUserExceptionDispatcher` in the backtrace, that is the crash reporter faulting
  while handling the original exception. The real fault is the frame BELOW the
  dispatcher.
- **The useful part is far down the file.** Search for `Call Stack Trace Begin`. A
  later section carries demangled C++ names even though the raw backtrace shows only
  addresses.

Worked example (2026-07-24): a bare `access violation ... Write to 0x0` with no file
name resolved to

```
void __cdecl QuestTemplate::Validate(void) const
bool __cdecl QuestDataSheet::Validate(void)
bool __cdecl DatasheetManager::Validate(void)
```

which localized the fault to quest validation immediately. Get this before forming
any hypothesis: it is the difference between bisecting an entity family and bisecting
the whole patch.

## 4. Classify log lines against a known-good boot

Do not assume a Korean error-looking line is the blocker. Keep a known-good boot log
(any earlier day's file on the box) and compare the phase sequence: the failing boot's
last phase, and whether the suspicious line also appears in the good one.

`Task에서 [완료시삽입아이템.[count]]노드를 찾을 수 없습니다` and its
`노드를 찾을 수 없습니다` siblings are **warnings**. Quests 1353-1358 emit them on every
healthy boot, and the server continues to `Validation Check [QuestData]` and finishes.
Reading one as fatal on 2026-07-23 cost a day of waiting and a DSL request filed on a
wrong premise.

Also note: quest iteration order is not id order (the warning block runs 1356, 1358,
1357, 1355, 1354, 1353), so "it crashed before quest N" proves nothing about which
record is at fault. Nor does the NUMBER of warnings that made it to disk: the log
writer runs on its own thread (`LogFileWriterManager::WriteLogLoop` appears in every
crash report), so a crash truncates the buffered tail. Two runs that died at the same
place printed 0 and 3 warnings respectively. Treat a short warning list as a flushing
artifact, never as a position signal.

The warning stream is still useful for one thing: it enumerates the loader's SOFT read
sites. A node that warns when missing is read defensively; a node whose absence crashes
is dereferenced. Corpus frequency does not predict which is which (two nodes at exactly
100% presence behave differently), but container kind does: children of repeated entry
containers were proven by controlled experiment to be hard dereferences, while
body-level bags warn.

## 5. Loader invariants

- **UTF-8 BOM is mandatory** on every server datasheet file. Without it the loader
  rejects the file outright (`UTF8 파일인지 확인`). `dsl apply` writes it correctly; the
  live risk is an ad-hoc repair script, since Python's `ElementTree.write` emits no
  BOM. Any script that rewrites datasheet XML must write `b'\xef\xbb\xbf'` first, and
  the check belongs in its verification step.
- **Element order is not free.** The loader is a hand-rolled sequential reader, so a
  setting written before the container it configures can be applied to a pointer that
  does not exist yet. Match the ordering the shipping corpus uses.
- **Missing structural nodes are dereferenced, not defaulted.** See the
  clone-do-not-synthesize lesson in the `new-spec` skill.

## 6. Bisect protocol

When the stack names a subsystem but not a file:

1. Scope the surface: `git status` in `<server_datasheet>` limited to that entity
   family. That is your candidate set, and it is usually small.
2. Change ONE variable per boot. Combining a revert with a fix wastes the restart,
   because a green boot no longer tells you which one mattered.
3. **`deploy_dev.py` mirrors only files that differ from git HEAD.** Reverting a file
   with `git checkout` removes it from the delta, so the STALE copy stays on the dev
   box and your "revert" never reached the server. Push reverted files explicitly with
   `scp` and verify remotely.
4. Verify the remote file state before asking for the restart: hash or parse the
   deployed file over SSH rather than trusting the deploy summary line.

## 7. When to stop bisecting

Two boots that fail to isolate the fault mean the method is wrong, not that the next
hypothesis will land. Prefer replacing the suspect record with a clone of a
known-good one over further guessing.

Dump analysis is the escape hatch, but `cdb.exe` is not installed by default on the
dev workstation (the Windows Kit ships `dbghelp.dll` and friends without the
debuggers). Installing it is a deliberate step worth taking only when structural
comparison has genuinely run out.

## Lessons
