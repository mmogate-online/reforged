# Island of Dawn — NPC Template IDs (v31)

Source: v31 MCP `audit_zone_spawns` with `excludeVoidSpawn=false`

## Summary

| Zone | Territories | Spawns | Unique NPCs |
|------|-------------|--------|-------------|
| 13 | 403 | 498 | 31 |
| 64 | 15 | 64 | 34 |
| 213 | 24 | 51 | 51 |
| 313 | 6 | 8 | 8 |
| 364 | 4 | 4 | 4 |
| 416 | 70 | 168 | 45 |
| **Total** | **522** | **793** | **137** |

> **Note on template ID reuse:** Template IDs in the low ranges (1001-1153) are zone-local. The same numeric ID is reused across multiple zones for entirely different NPCs. These must always be referenced as `huntingZoneId:templateId` pairs.

## Master NPC Template Table

| templateId | name | zones | hasName |
|------------|------|-------|---------|
| 1 | Pigling | 13 | Y |
| 2 | Sporewalker | 13 | Y |
| 6 | Kariagon | 13 | Y |
| 7 | Disc Reaper | 13 | Y |
| 8 | Runekeeper | 13 | Y |
| 9 | Destroyer | 13 | Y |
| 101 | (no name) | 13 | N |
| 102 | Docile Terron | 13 | Y |
| 111 | Gentle Pigling | 13 | Y |
| 555 | Scion Scout | 13 | Y |
| 556 | Scion Scout | 13 | Y |
| 557 | Scion Scout | 13 | Y |
| 558 | Scion Scout | 13 | Y |
| 888 | Training Dummy | 13 | Y |
| 901 | Orcan Guardian | 13 | Y |
| 999 | (no name) | 13 | N |
| 1000 | Demonic Zombie | 416 | Y |
| 1001 | (zone-local) | 13=Vekas, 64=Adria, 213=Taleb, 313=Ashley, 364=Ainah | Y |
| 1002 | (zone-local) | 13=Acharak, 313=Ashley, 364=Ainah, 416=Disc Reaper | Y |
| 1003 | (zone-local) | 13=Acharak's Soldier, 64=Kerson, 213=Kishale, 313=Harger, 416=Orcan Brute | Y |
| 1004 | (zone-local) | 13=Kugai, 213=Neziir, 313=Harger | Y |
| 1005 | (zone-local) | 64=Rutgar, 213=Phaedra, 313=Jilva | Y |
| 1006 | (zone-local) | 64=Jorhon, 313=Misrile | Y |
| 1007 | (zone-local) | 64=Gurney, 213=Chione, 313=Jilva | Y |
| 1008 | (zone-local) | 64=Charise, 213=Leander, 313=Misrile | Y |
| 1009 | Teil | 64 | Y |
| 1011 | (zone-local) | 13=Terron Saboteur, 64=Berlon | Y |
| 1012 | Disc Reaper | 416 | Y |
| 1013 | Orcan Brute | 416 | Y |
| 1014 | Lam | 213 | Y |
| 1015 | Karascha's Lair Teleportal | 213 | Y |
| 1016 | Leiyane | 213 | Y |
| 1017 | Dulari | 213 | Y |
| 1021 | Telrayne | 64 | Y |
| 1022 | Abadir | 64, 416 | Y |
| 1023 | (zone-local) | 64=Jirash, 213=Junia, 416=Orcan Brute | Y |
| 1024 | (zone-local) | 64=Gyebrik, 213=Volis | Y |
| 1025 | (zone-local) | 64=Riordan, 213=Sersine | Y |
| 1026 | (zone-local) | 64=Verele, 213=Verus | Y |
| 1027 | Bree | 64 | Y |
| 1028 | (zone-local) | 64=Taras, 213=Gregor | Y |
| 1029 | Kiriya | 64 | Y |
| 1030 | Annukha | 64 | Y |
| 1031 | Teague | 64 | Y |
| 1032 | Orin | 64, 416=(no name) | Y |
| 1033 | Bipi | 64, 416=(no name) | Y |
| 1034 | Rehiya | 64 | Y |
| 1037 | Leander | 213 | Y |
| 1038 | Ramun | 213 | Y |
| 1042 | Jairus | 64, 416=(no name) | Y |
| 1043 | (no name) | 416 | N |
| 1045 | Mardon | 64 | Y |
| 1046 | Peron | 64 | Y |
| 1047 | Rheta | 64 | Y |
| 1048 | Lilni | 64 | Y |
| 1049 | Milene | 64 | Y |
| 1050 | Teleportal | 64 | Y |
| 1052 | (no name) | 416 | N |
| 1053 | Obelisk | 213, 416=(no name) | Y |
| 1054 | Sandom | 213 | Y |
| 1062 | (no name) | 416 | N |
| 1063 | (no name) | 416 | N |
| 1072 | (no name) | 416 | N |
| 1073 | (no name) | 416 | N |
| 1101 | (zone-local) | 213=Rivem, 364=Hyneu | Y |
| 1102 | (zone-local) | 213=Banzon, 364=Hyneu | Y |
| 1103 | Merrick | 213 | Y |
| 1104 | Rania | 213 | Y |
| 1105 | Axelle | 213 | Y |
| 1106 | Barsabba | 213 | Y |
| 1107 | Talia | 213 | Y |
| 1108 | Jamila | 213 | Y |
| 1111 | Adrastus | 213 | Y |
| 1112 | Neely | 213 | Y |
| 1114 | Helier | 213 | Y |
| 1115 | Nivek | 213 | Y |
| 1117 | Joram | 213 | Y |
| 1118 | Kaeden | 213 | Y |
| 1119 | Ashak | 213 | Y |
| 1120 | Cassia | 213 | Y |
| 1121 | Leolin | 213 | Y |
| 1122 | Islene | 213 | Y |
| 1123 | Braeless | 213 | Y |
| 1124 | Ramun | 213 | Y |
| 1134 | Edan | 213 | Y |
| 1139 | Darius | 213 | Y |
| 1141 | Fili | 213 | Y |
| 1142 | Palesk | 213 | Y |
| 1143 | Perrin | 213 | Y |
| 1145 | Wystan | 213 | Y |
| 1146 | Zaccai | 213 | Y |
| 1147 | Tanli | 213 | Y |
| 1150 | Todoro | 213 | Y |
| 1152 | Karlikan | 213 | Y |
| 1153 | Amekel | 213 | Y |
| 1501 | Kelsaik's Nest Teleportal | 213 | Y |
| 1601 | Vene | 64 | Y |
| 2010 | Priest | 416 | Y |
| 2011 | Slayer | 416 | Y |
| 2012 | Sorcerer | 416 | Y |
| 2013 | Archer | 416 | Y |
| 2014 | Berserker | 416 | Y |
| 3000 | Kumas Demon | 416 | Y |
| 3001 | Karascha the Dark Wing | 416 | Y |
| 3002 | Kumas Demon | 416 | Y |
| 3003 | Kumas Demon | 416 | Y |
| 3004 | Kumas Demon | 416 | Y |
| 3005 | Kumas Demon | 416 | Y |
| 3006 | Kumas Demon | 416 | Y |
| 3007 | Kumas Demon | 416 | Y |
| 3008 | Kumas Demon | 416 | Y |
| 5001 | Yisron | 416 | Y |
| 5002 | Stegram | 416 | Y |
| 5004 | Rajiel | 416 | Y |
| 5005 | Hinsan | 416 | Y |
| 5006 | Tantus | 416 | Y |
| 5007 | Halec | 416 | Y |
| 5010 | Elleon | 416 | Y |
| 7001 | (no name) | 416 | N |
| 7002 | (no name) | 416 | N |
| 8000 | (no name) | 416 | N |
| 8001 | (no name) | 416 | N |
| 9000 | Tikat | 64 | Y |
| 9001 | (no name) | 64 | N |
| 9002 | (no name) | 64, 416 | N |
| 9003 | (no name) | 64, 416 | N |
| 9004 | (no name) | 416 | N |
| 300910 | Prowling Cromos | 13 | Y |
| 300921 | Noruk | 13 | Y |
| 300931 | Ghilliedhu | 13 | Y |
| 300932 | Horned Ghilliedhu | 13 | Y |
| 300942 | Terron Thrall | 13 | Y |
| 300951 | Dark Raider | 13 | Y |
| 300960 | Devoted Ebon Imp | 13 | Y |
| 301191 | Stonebeak Raider | 13 | Y |
| 301193 | Stonebeak Brigand | 13 | Y |
| 301194 | Stonebeak Highcrest | 13 | Y |

## Key Observations

- 16 template IDs are zone-local reuse (1001-1008, 1011, 1023-1026, 1028, 1101, 1102)
- Zone 13 has the world mobs (300xxx range) plus named bosses
- Zone 416 has prologue dungeon content (Karascha, Kumas Demons, Elleon)
- Zone 213 has the largest named NPC population (quest givers, villagers)
- Zones 313/364 are small transition zones with 8/4 NPCs respectively
