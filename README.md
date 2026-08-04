# Reforged Content

Content specifications for the TERA Reforged server, written in DataSheetLang.

Every gameplay change we ship is authored here as a spec, so this repository is
also a readable record of what changed and when.

If you just want to know what changed in the game, read [CHANGELOG.md](CHANGELOG.md). It is
written for players and needs no knowledge of the tooling below.

Layout:

- `CHANGELOG.md` what shipped, in plain language, one entry per patch
- `specs/` patch specifications, one folder per patch
- `packages/` reusable spec modules the patches build on

Specs carry their own explanation. Where a change is not obvious from the data, the reason is
a comment at the top of the file that produced it. There are no separate notes to keep in
sync, so what you read beside a spec is as current as the spec itself.

The DataSheetLang tool is documented at https://dsl.mmogate.online
