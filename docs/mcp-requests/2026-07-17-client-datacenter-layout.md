# Datasheet MCP: cannot mount unpacked client DataCenter layouts (2026-07-17)

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
