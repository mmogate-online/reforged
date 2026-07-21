# Padding NpcLoc Sweep: Island of Dawn (v17.11 client)

Generated 2026-07-20. Analysis only (no specs, no datasheet changes).

Full sweep of the v17.11 USA client `StrSheet_NpcLoc` for IoD hunting zones 13, 64, 213, 313, 364, 436, 437, 9036, 9037. Every v17 quest-marker entry is reconciled against v92 server `NpcData` existence, `TerritoryData` baseline spawn state, and the v17 / v31 / v92 name sources. Zones 313, 364, 9036, 9037 carry no NpcLoc entries.

## 1. Source and method notes

- v17 client TerritoryData holds only Fence polygons (no per-Npc spawn points); NpcLoc is the only v17 source of discrete world coordinates per template.
- NpcLoc coordinate system matches server coordinates (SPAWNED single-marker NPC median offset 145u), but encodes the v17-era layout: 17 of 44 spawned NPCs sit >300u from the current baseline spawn and some moved thousands of units (Leander 1008 ~13975u), so NpcLoc positions must be authored then tuned in-game.
- No DEAD entries: every scoped marker template still exists in v92 NpcData.
- English displayed-name line is stable v17->v31: only 4 utility-object renames, zero human-NPC renames.
- The v92 Korean server carries a wholesale re-identified NPC roster (Kamarnu=Rabram, Taleb=Albert, Clovis=Muriel, ...) diverging from the English client across essentially all ~54 IoD villagers; this is a NA/EU-English vs KR localization split, not a content rename over time.

Name sources used (three parallel layers):

- **v17 EN**: v17.11 USA `StrSheet_Creature` (English display name in the old client).
- **v31 EN**: v31.04 EUR `StrSheet_Creature` (English display name; equals the v92 baseline era).
- **v92 KR**: v92 server `NpcData_{hz}.xml` `name` attribute (Korean internal/display name; romanized here). The server `StrSheet_Creature.xml` English sheet is stale (it still reads Kamarnu for 1009 while the live KR server calls it Rabram), so it is not used as an authority.

## 2. Classification counts per hunting zone

| HZ | SPAWNED | PLANNED-NPC | PLANNED-MOB | NEW-CANDIDATE | DEAD | total |
|----|--------:|------------:|------------:|--------------:|-----:|------:|
| 13 | 21 | 0 | 13 | 4 | 0 | 38 |
| 64 | 15 | 0 | 0 | 0 | 0 | 15 |
| 213 | 28 | 9 | 0 | 2 | 0 | 39 |
| 436 | 1 | 0 | 0 | 0 | 0 | 1 |
| 437 | 1 | 0 | 0 | 0 | 0 | 1 |
| **all** | **66** | **9** | **13** | **6** | **0** | **94** |

Classification rules: DEAD = template absent from v92 NpcData; SPAWNED = has a v92 TerritoryData spawn; PLANNED-NPC = one of the six located quest-givers or the three story-bridge NPCs (213,1027 Pelaeni; 213,1036 Rian Kubel; 213,1020 Theon); PLANNED-MOB = template already covered by a planned habitat roster; NEW-CANDIDATE = marker plus v92 template, no baseline spawn, in no current plan.

## 3. NEW-CANDIDATE entries

Six markers point at templates that exist in v92 NpcData, have no baseline spawn, and are in no current plan.

| HZ | tid | v17 name / title | v92 KR (roman) | NPC / mob | markers | first pos (x,y,z) | referenced by |
|----|-----|------------------|----------------|-----------|--------:|-------------------|---------------|
| 13 | 302 | Terron Ringleader /  | Nature Spirit | mob | 10 | 66432, -83644, -3667 | q1348 (missing_mob: Nature Spirit) |
| 13 | 303 | Terron Thief /  | Nature Spirit | mob | 10 | 66432, -83644, -3667 | q1348 (missing_mob: Nature Spirit) |
| 13 | 300941 | Terron /  | Nature Spirit Theron B | mob | 17 | 79848, -83405, -4501 | q1319 (missing_mob: Nature Spirit Theron B) |
| 13 | 300944 | Terron Chief /  | Nature Spirit Theron Chief | mob | 17 | 79848, -83405, -4501 | q1319 (missing_mob: Nature Spirit Theron Chief) |
| 213 | 1018 | Riel / Prefect | Koren | NPC (villager) | 1 | 64416, -65444, -4220 | nothing in the 40 candidates |
| 213 | 1137 | Milun / Apprentice Priest | Remaniel | NPC (villager) | 1 | 64860, -65448, -4180 | nothing in the 40 candidates |

Recommendations:

- **13,302 / 13,303** and **13,300941 / 13,300944** are the quest-target mobs of quests 1348 and 1319 (both ADAPT). They have NpcLoc markers but no planned habitat group, so their markers are the bespoke placement source (see section 4). Recommend authoring quest-mob territories from these markers when 1348 and 1319 are adapted.
- **213,1018 Riel (Prefect)** and **213,1137 Milun (Apprentice Priest)** are unspawned villagers with a single v17 marker each, near the northern hub / garden area (y approximately -65,444). No candidate quest references them. Low priority: likely ambient / flavor NPCs. Restore only if a hub-population pass wants them; a single-point NpcLoc position is available if so.

## 4. Mob-position reconstruction assessment

**Does NpcLoc add positional information beyond the v17 fences already held?**

For planned-habitat mobs: mostly no, it is a cross-validation surface. The v17 client TerritoryData supplies Fence polygons (regions), and the NpcLoc point markers for those same templates fall tight against those fences. Median nearest-fence-vertex distance per template is roughly 100 to 350u:

| tid | v17 name | markers | groups | median marker-to-fence dist | max |
|-----|----------|--------:|-------:|----------------------------:|----:|
| 3 | Ponderous Sporewalker | 18 | 2 | 192 | 192 |
| 4 | Dwarf Orcan | 12 | 1 | 2060 | 2960 |
| 5 | Orcan Raider | 12 | 1 | 182 | 183 |
| 304 | Sickly Noruk | 32 | 2 | 200 | 201 |
| 601 | Dark Marauder | 6 | 2 | 106 | 138 |
| 300541 | Rockcrawler | 14 | 1 | 241 | 242 |
| 300542 | Rockcrawler Cleaver | 14 | 1 | 241 | 242 |
| 300911 | Cromos | 27 | 1 | 258 | 259 |
| 300920 | Shaggy Noruk | 22 | 2 | 245 | 245 |
| 300930 | Elder Ghilliedhu | 11 | 1 | 341 | 341 |
| 300933 | Hardened Ghilliedhu | 11 | 1 | 118 | 1601 |
| 300943 | Terron Saboteur | 10 | 1 | 242 | 242 |
| 300945 | Terron Lama | 10 | 1 | 242 | 242 |

Two templates show a larger spread (Dwarf Orcan 4 median roughly 2060u; Hardened Ghilliedhu 300933 max roughly 1601u) because their markers extend past the single habitat group mapped for them, a minor hint that those families ranged slightly wider in v17 than the one planned group captures. Otherwise the markers add no placement precision the fences do not already give.

**Where NpcLoc is the ONLY v17 positional source: the quest-target mobs with no habitat group.**

These four templates have zero v17 habitat fences (no TerritoryGroup) and zero v92 baseline spawn, so their NpcLoc markers are the sole data-derived positions for bespoke placement. Within each quest pair the two templates carry an identical marker set.

| tid | v17 name | quest | markers | cluster centroid (x,y) | x range | y range |
|-----|----------|-------|--------:|------------------------|---------|---------|
| 302 | Terron Ringleader | 1348 Ferocious Flowering Felons | 10 | (65842, -84146) | 63443..67621 | -85049..-83528 |
| 303 | Terron Thief | 1348 Ferocious Flowering Felons | 10 | (65842, -84146) | 63443..67621 | -85049..-83528 |
| 300941 | Terron | 1319 Dwellers of the Island | 17 | (79568, -84880) | 77901..80973 | -87410..-82567 |
| 300944 | Terron Chief | 1319 Dwellers of the Island | 17 | (79568, -84880) | 77901..80973 | -87410..-82567 |

Full marker coordinates for these four are in `padding-npcloc-sweep.json` (records for hz13 tids 302, 303, 300941, 300944). Quest 1319 giver is 213,1110 (Muriel/Clovis, a planned NPC) and its target cluster sits at x approximately 78k to 81k, y approximately -82k to -87k, consistent with that NPC marker at (79293, -82308). Quest 1348 targets cluster near the Near-Base staging band at x approximately 63k to 68k, y approximately -83k to -85k.

## 5. Rename census

### 5a. English displayed-name changes (v17 EN vs v31 EN)

The English line is stable across the roster. Only four templates changed English name between the v17 USA client and the v31 EUR client (which equals the v92 baseline era), and all four are utility objects, not story NPCs:

| HZ | tid | v17 EN | v31 EN (v92 baseline) | v92 KR (roman) |
|----|-----|--------|-----------------------|----------------|
| 64 | 1006 | Jhon | Jorhon | Ian |
| 64 | 1050 | Hermaiorni | Teleportal | Teleport Stone (Hermaione Elin) |
| 213 | 1015 | Teleportal | Karascha's Lair Teleportal | Demon Magic Stone |
| 213 | 1053 | Detector Stone | Obelisk | Detection Magic Stone |

### 5b. English-client vs Korean-server identity divergence (the real rename surface)

Almost every IoD human villager has a v92 Korean server identity that is a different name from its English client identity (Kamarnu to Rabram, Taleb to Albert, Clovis to Muriel, and so on). This is a NA/EU-English versus KR localization split, not a rename over time (v17 EN and v31 EN agree). It is the rename-tracking table the restoration must maintain: quest dialogs, journals and NPC references on the KR-based v92 server key off the Korean identity, while an English client shipped from v17/v31 shows the English identity. The spawned column shows baseline spawn count.

| HZ | tid | v17/v31 EN | v92 KR (roman) | title | spawned | class |
|----|-----|-----------|----------------|-------|--------:|-------|
| 64 | 1001 | Adria | Yulia | Tribune | 1 | SPAWNED |
| 64 | 1003 | Kerson | Kerong | Banker | 1 | SPAWNED |
| 64 | 1005 | Rutgar | Kohen | Merchant | 1 | SPAWNED |
| 64 | 1006 | Jhon to Jorhon | Ian | Adjutant | 1 | SPAWNED |
| 64 | 1007 | Gurney | Alios Renders | Tactics Instructor | 1 | SPAWNED |
| 64 | 1008 | Charise | Eiyerin Pilus | Magic Instructor | 1 | SPAWNED |
| 64 | 1009 | Teil | Franz Teil | Councilor | 1 | SPAWNED |
| 64 | 1023 | Jirash | Michael | Guard | 1 | SPAWNED |
| 64 | 1028 | Taras | Jaki | Guard | 1 | SPAWNED |
| 64 | 1029 | Kiriya | Rikia | Guard | 1 | SPAWNED |
| 64 | 1033 | Bipi | Cherne | Guard | 1 | SPAWNED |
| 64 | 1042 | Jairus | Jeremia | Researcher | 1 | SPAWNED |
| 64 | 1048 | Lilni | Lilina | Gathering Guide | 1 | SPAWNED |
| 64 | 1049 | Milene | Artemis | Rest Guide | 1 | SPAWNED |
| 64 | 1050 | Hermaiorni to Teleportal | Teleport Stone (Hermaione Elin) | Teleport Master | 1 | SPAWNED |
| 213 | 1001 | Taleb | Albert | Legate | 1 | SPAWNED |
| 213 | 1003 | Kishale | Keisha | Centurion | 1 | SPAWNED |
| 213 | 1004 | Neziir | Jokan | Centurion | 1 | SPAWNED |
| 213 | 1005 | Phaedra | Tiares | Outrider | 1 | SPAWNED |
| 213 | 1007 | Chione | Kione | Courier | 1 | SPAWNED |
| 213 | 1008 | Leander | Rian Kubel | Magister | 1 | SPAWNED |
| 213 | 1009 | Kamarnu | Rabram | Assistant Researcher | 0 | PLANNED-NPC |
| 213 | 1014 | Lam | Lambert | Legate | 1 | SPAWNED |
| 213 | 1015 | Teleportal to Karascha's Lair Teleportal | Demon Magic Stone |  | 1 | SPAWNED |
| 213 | 1016 | Leiyane | Lenia | Flight Master | 1 | SPAWNED |
| 213 | 1017 | Dulari | Kaimon | Researcher | 1 | SPAWNED |
| 213 | 1018 | Riel | Koren | Prefect | 0 | NEW-CANDIDATE |
| 213 | 1020 | Priscus | Theon | Engine of Mischief Guide | 0 | PLANNED-NPC |
| 213 | 1021 | Eria | Eria Elin | Arcanist | 0 | PLANNED-NPC |
| 213 | 1023 | Junia | Jas Fanes | Tactics Instructor | 1 | SPAWNED |
| 213 | 1024 | Volis | Darius | Magic Instructor | 1 | SPAWNED |
| 213 | 1025 | Sersine | Kiana | Arcanist | 1 | SPAWNED |
| 213 | 1026 | Verus | Lester | Lancer | 1 | SPAWNED |
| 213 | 1027 | Kirash | Pelaeni | Outrider | 0 | PLANNED-NPC |
| 213 | 1028 | Gregor | Keren | Outrider | 1 | SPAWNED |
| 213 | 1036 | Leander | Rian Kubel | Magister | 0 | PLANNED-NPC |
| 213 | 1037 | Leander | Rian Kubel | Magister | 1 | SPAWNED |
| 213 | 1038 | Ramun | Raimong | Herald | 1 | SPAWNED |
| 213 | 1053 | Detector Stone to Obelisk | Detection Magic Stone |  | 1 | SPAWNED |
| 213 | 1105 | Axelle | Elika | Dock Manager | 1 | SPAWNED |
| 213 | 1106 | Barsabba | Labros | Centurion | 1 | SPAWNED |
| 213 | 1110 | Clovis | Muriel | Patrol | 0 | PLANNED-NPC |
| 213 | 1114 | Helier | Karios | Guard | 1 | SPAWNED |
| 213 | 1115 | Nivek | Mati | Centurion | 1 | SPAWNED |
| 213 | 1119 | Ashak | Bagos | Prefect | 1 | SPAWNED |
| 213 | 1121 | Leolin | Ryan | Guard | 1 | SPAWNED |
| 213 | 1126 | Ayrdoss | Eredos | Guard | 0 | PLANNED-NPC |
| 213 | 1128 | Lorin | Mayer | Guard | 0 | PLANNED-NPC |
| 213 | 1130 | Jehan | Beres | Researcher | 0 | PLANNED-NPC |
| 213 | 1134 | Edan | Rodrik | Centurion | 1 | SPAWNED |
| 213 | 1137 | Milun | Remaniel | Apprentice Priest | 0 | NEW-CANDIDATE |
| 213 | 1141 | Fili | Rasana | Outrider | 1 | SPAWNED |
| 213 | 1143 | Perrin | Jukon | Lancer | 1 | SPAWNED |
| 213 | 1147 | Tanli | Riya | Centurion | 1 | SPAWNED |
| 437 | 1001 | Sorcha | Apprentice Witch | Researcher | 1 | SPAWNED |

Note: 213 templates 1008, 1036 and 1037 all read Leander in EN and all map to the single KR identity Rian Kubel; the story-bridge NPC is 1036. The six planned quest-givers (1009 Rabram, 1021 Eria Elin, 1130 Beres, 1128 Mayer, 1126 Eredos, 1110 Muriel) and the three story-bridge NPCs (1027 Pelaeni, 1036 Rian Kubel, 1020 Theon) all sit in this divergence table with spawned = 0, consistent with the prior padding artifacts.

## 6. SPAWNED position agreement (validation datum)

NpcLoc marker vs current v92 baseline spawn, single-marker spawned NPCs: coordinate systems match (median offset 145u, 27 of 44 within 300u). But 17 NPCs sit farther, several relocated by thousands of units between v17 and v92 (for example 213,1008 Leander roughly 13975u, 213,1001 Taleb roughly 5905u, 64,1048 Lilni roughly 5076u, 213,1028 Gregor roughly 3836u). Takeaway: NpcLoc coordinates are directly usable as world positions but encode the v17 layout, so author from the marker then tune in-game, exactly as the six-NPC location plan already prescribes.
