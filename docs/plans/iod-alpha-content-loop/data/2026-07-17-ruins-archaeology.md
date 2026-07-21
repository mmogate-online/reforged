# Ruins / Leander's Outpost archaeology findings (2026-07-17)

Condensed from the archaeology agent run; full detail lives in the session log.
Companion to iteration-2-quest-audit.md and legacy-quest-locations.md.

## Verdicts
1. NO template deletion or name-stubbing anywhere in zones 13/213: client, v31
   and v92 template id sets and names are identical. Suspects resolved:
   13,301 Rockcrawler Tumbler (ambient), 13,888 Training Dummy (prop, quest
   1386 target), 13,999 exploding powder keg (object NPC, no English string,
   renders unnamed in English tooling).
2. Mysterious Ruins polygon (section 13003, "Airship Crash Site (Orcan)") is
   CORRECT as-is: 7x Orcan Guardian 901 + 9x keg 999 in both servers. It was
   never a manned camp. Nothing to restore inside it.
3. Leander's Outpost (the multi-quest camp beside the ruins, per the legacy
   wiki) was NEVER built server-side: no territory, no NPC spawns, in v31 OR
   v92. Full authoring required. All templates + names exist in NpcData_213.
4. All spawn losses predate v31. "Restore from v31" does not work for spawns.
5. "Redeployment" mystery RESOLVED: it is quest 1311 under its old English
   title. Server StrSheet (v31+v92) has 1311001 = "Redeployment"; the 2011
   client has "Clearing the Gorge". Title drift only; ids 1314/1320/1342 have
   no data anywhere.

## Unspawned quest NPCs (templates exist, no TerritoryData entry in v31/v92)
| hz213 tpl | name [title] | breaks quests | authentic post |
|---|---|---|---|
| 1009 | Kamarnu [Assistant Researcher] | 1305, 1332 | Kaimon's Camp |
| 1018 | Riel [Prefect] | 1311, 1313 | Supply Base / gorge |
| 1027 | Kirash [Outrider] | 1307 | Supply Base |
| 1110 | Clovis [Patrol] | 1319 | Garrison North Camp |
| 1126 | Ayrdoss [Guard] | 1349 | Leander's Outpost |
| 1128 | Lorin [Guard] | 1347 | Leander's Outpost |
| 1130 | Jehan [Researcher] | 1310, 1332, 1333, 1390 | Leander's Outpost |
| 1137 | Milun [Apprentice Priest] | 1338 | Chione / Dock cluster |
Do NOT world-place: 1036 Leander (cinematic dup), 1020 Priscus (event guide).
Eria 1021: relocate from the vanguard camp to the authored Leander's Outpost.

## Unspawned quest kill-target mobs (~17 templates, pre-v31 gap)
1349: Dwarf Orcan 4, Orcan Raider 5 | 1347: Rockcrawler 300541, Cleaver
300542 | 1333: Cromos 300911 | 1308: Ponderous Sporewalker 3 | 1348: Terron
Ringleader 302, Terron Thief 303 | 1327: Sickly Noruk 304 | 1307: Dark
Marauder 601 | 1332: Shaggy Noruk 300920 | 1324: Elder Ghilliedhu 300930,
Hardened Ghilliedhu 300933 | 1319: Terron 300941, Terron Chief 300944 |
1337: Terron Saboteur 300943, Terron Lama 300945.
Note: 365 of 498 zone-13 spawns use randomPos=true with pos 0,0,0 inside a
fence; that is NORMAL (fence-random), not missing.

## Placement anchors for Leander's Outpost (authored)
- Ruins section centroid (50700,-78500); wiki: outpost adjacent to ruins.
- Corridor bracket toward the vanguard camp: x 50000-52000, y -74000..-76000
  (friendly anchors: Terron Thrall 49875,-71408; Kariagon 50189,-71651).
- Alternate southern anchor: empty territory 21300020 (51854,-85755).
- Other NPC anchors: Dulari 1017 at Kaimon's Camp (80900,-81300); Leander
  1008 at Supply Base (69014,-79276); Garrison North Camp (74100,-82680).
