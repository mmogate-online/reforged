# Datasheet MCP: cannot mount unpacked client DataCenter layouts (2026-07-17)

## Resolution log (2026-07-25): request 1 done, request 2 declined for now

datasheet-mcp commit `4ee5b2c`. 355 tests green at that commit; verified by running the published
exe against `D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA`.

- **Request 1 (silent empties): done.** A new `IDatasheetMountProbe` reports, per entity type, how
  many backing files actually exist under `--path`.
  - Startup, on the client dump, now logs to stderr: *"No configured entity file was found under
    '...\DataCenter_Final_USA' (53 entity types probed). Every data tool will return empty results.
    Expected a server datasheet directory containing flat XML files (ItemTemplate.xml,
    ContinentData.xml, NpcData_*.xml) plus CompensationData/ and QuestData/ subdirectories.
    Unpacked client DataCenter layouts are a different structure and are not supported."*
    A healthy mount logs `Mounted 53 of 53 configured entity types` (v92) or `36 of 53` (v31).
  - `list_entity_types` gained a `files` column, so "is this type mounted at all" is one call.
  - `lookup` / `search` / `compare` misses now distinguish the two causes. On the client dump,
    `lookup Skill 60220100` returns *"...not found. No backing file for Skill is present under the
    mounted datasheet path (expected '...\UserSkillData_Common.xml'), so this entity type holds no
    data here. Run list_entity_types to see which types are mounted."* A genuine id miss on a
    mounted type is unchanged, so ordinary misses do not grow a misleading "wrong path" tail.
  - This also closes the 2026-07-17 IoD item 19 ("index-empty vs data-absent signal") for the
    entity-table case.
- **Request 2 (client DataCenter mount mode): declined for now.** It is not a path-handling change:
  the client sharded layout needs a second organization mode (one entity spread over N files), a
  separate entity config because the client element and attribute names differ from the server
  sheets, and its own validation corpus. That is a project rather than a feature, and the two uses
  so far (IoD pre-revamp questline recovery) were served acceptably by direct Python parsing. Worth
  reopening if client-dump archaeology becomes recurring rather than occasional; the mount probe
  above at least makes the unsupported layout fail loudly instead of silently.

Attempted to point the MCP at a recovered old-client unpacked DataCenter
(`datasheet-mcp.exe --path "D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA"`,
259 element folders of sharded XML: `Quest\Quest-NNNNN.xml`,
`StrSheet_Quest\`, `QuestCompensationData\`, `ContinentData\`, etc.).

- Expected: at least partial querying (quests, strings, zones) for content
  archaeology against historical client dumps.
- Actual: server starts cleanly and `list_entity_types` returns the static
  config table, but every data tool returns empty ("No zones found", "Quest
  data not available"). No error, no hint that the path layout is unsupported.
- Workaround used: direct Python parsing of the shards (worked fine).

Requests:
1. Low cost: when a `--path` mounts zero entities, emit a startup warning and
   a distinct tool message ("path layout not recognized: expected server
   datasheet structure") instead of silent empties.
2. Larger feature (optional, valuable for archaeology): a client-DataCenter
   mount mode that maps sharded client folders (`Quest-NNNNN.xml`,
   `StrSheet_*`, `QuestCompensationData`, `VillagerDialog`) onto the existing
   quest/string/reward tools. Old client dumps are the only source for
   content trimmed from both v31 and v92; first real use case was the Island
   of Dawn pre-revamp questline recovery.
