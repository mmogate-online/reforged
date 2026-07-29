# Orcans of the Island of Dawn: lore source dossier

Research date: 2026-07-28. Read-only survey.

Sources consulted:

| tag | source | how queried |
|---|---|---|
| v17 | `<old_client_dc>` (Novadrop unpacked, English USA) | direct XML parse |
| v31c | `<client_dc_v31>` (English EUR) | direct XML parse |
| v31s | `<v31_datasheet>` | `datasheet-v31` MCP + direct XML parse |
| v92s | `<server_datasheet>` | `datasheet-v92` MCP + direct XML parse |
| v92c | `<client_datacenter>` | direct XML parse |

**Quoting convention.** Several source lines contain U+2014. Repo style forbids that glyph, so it is rendered
below as a colon or a comma. Everything else in the quoted blocks is verbatim, including `<BR>` markup and
`{@LinkCreature:...}` tokens. Pull the cited id from the cited file to see the original punctuation.

**Matching rule applied.** Creatures were matched across eras by `(huntingZone, templateId)`. English display
names were taken from the v17 and v31 CLIENT `StrSheet_Creature`, never from the v92 server StrSheet, which is
known stale on this project.

---

## 1. Lore summary

The Orcans are a tribal raider people, not a monster swarm. They are organised, they hold a named camp, they
post patrols, they trade loot among themselves, they carry a tribal talisman, and they take orders from a
warlord. The federation garrison on the Island of Dawn treats them as a military problem, not vermin: the
in-fiction language is "thin their ranks", "break their morale", "the proper military response is to remove
them by force". Nobody in the sources hates them personally. They are described with weary professional
respect and a little contempt, the tone of soldiers talking about an enemy who keeps showing up.

The island band belongs to the **Black Claw tribe** (KR 검은 발톱). The English localisation of the Island of
Dawn quests calls them the **Dark Claw** tribe; the same Korean tribe name is localised as **Black Claw** on
the mainland, in Feral Valley (hunting zone 41) and its quest band 4124 to 4193. So the island Orcans are a
detachment of a large mainland tribe, not an endemic island species. Their warlord on the island is
**Acharak**, whose spawn is labelled 검은 발톱 아카락, "Black Claw Acharak". The tribe's talisman is a plain
black feather.

Their motive is the crux, and the sources deliberately leave it half-answered. In the v31 story the Orcans
bring down a federation supply airship, then camp on the wreck and barter the crates among themselves. That
reads like ordinary banditry until Chione, the downed pilot, notices they are not looting her, only watching
her, and says "these orcans are not what they appear". The missing crate turns out to hold **relic stones**
attuned to the island's guardians, and the garrison concludes the Orcan Guardians were on the airship
specifically to get them, "but why?". Acharak's feather, recovered from his corpse, "hurts just to hold" and
was imbued with power by someone else: "Someone else wants this island very badly." So the Orcans are a
proxy. Somebody with real magical weight is aiming them at the island's guardian relics, and the garrison
never learns who before the arc moves on to the demon Karascha.

The second thread is their allies. Orcans have "some magic, but nothing of the level we're encountering".
Working inside the Orcan camp are **mekonari dark marauders** (13,601), bird-headed magical mercenaries who
"sell their magical prowess to nearly anyone". The scout Kirash watches the camp and reports that the
interesting thing there is not the Orcans at all. Killing a marauder yields a scroll in demonic script that
points at the Tainted Gorge. That is how the Orcan plot hands off into the Karascha and Lok plot: the Orcans
are the visible layer, the mekonaris are the paid middlemen, and the demon lord Karascha is at the bottom.

The Kugai thread is adjacent, not Orcan. **Kugai the Mighty** (13,1004) is race `SlaveManager`, spawn label
어둠의 인도자 쿠가이, "Kugai, Guide of Darkness". He is not an Orcan and shares no model with them. His codex,
translated by Leander in quest 1343, names Karascha and a god long thought dead, **Lok**. The only bridge
between Kugai's thread and the Orcan thread is that Sersine notes his scroll "bears similar markings to the
tokens you collected earlier", which is the Acharak feather chain. Treat Orcan-to-Lok as *implied but never
stated*.

Voice, for an author: the Orcans themselves never speak in any source. Every line about them is a garrison
line. Ayrdoss the scout is dry and enjoys the work ("Watching orcans run and hide is quite enjoyable"). Kirash
is proverbial and ominous. Chione is calm and unnerved. Bipi is clipped and impatient. Edan is warm.
Leander and Sersine are scholars who keep finding that the answer is worse than the question.

---

## 2. Creature census

All Island of Dawn Orcan-family templates. Display names are identical across v17, v31 and v92 clients for
every row below, so a single "English name" column is accurate.

| HZ,tpl | English name (v17 / v31 / v92 clients) | Server name (NpcData) | Race | Lvl | playStyle / role | shapeId | Spawned where |
|---|---|---|---|---|---|---|---|
| 13,4 | Dwarf Orcan | 미니 오칸 | OrcanMinimi | 7 | `zarco`, small minion | 300710 | v17: group 1300036, camp outskirts. v31: **template only, zero spawns**. v92: 4 territories x5 in 1300036 (patch 001 restoration) |
| 13,5 | Orcan Raider | 오칸 습격자 | OrcanPirate | 7 | `zarcoBoss`, regular | 300650 | v17: group 1300035, inside camp. v31: **template only, zero spawns**. v92: 4 territories x2 in 1300038 (patch 001 restoration) |
| 13,901 | Orcan Guardian | 오칸 | OrcanPirate | 7 | `basic`, regular; `parentId` 30065000 | 300650 | v31: 29 party spawns in group 1300035 "비행선 추락지(오칸)", the airship crash site. v92: those 29 plus 8 more in 1300038 |
| 13,902 | Dwarf Guardian | 오칸미니미 | OrcanMinimi | 7 | `zarco`, small minion; `parentId` 30071001 | 300710 | **zero spawns in every era.** Pure template |
| 13,1002 | Acharak | 오칸 | OrcanPirate | 8 | `zarcoBoss`, named boss | 300650 | v31 and v92: 2 spawns in group 1300047 "네임드", spawn label 검은 발톱 아카락 |
| 13,1003 | Acharak's Soldier | 오칸미니미 | OrcanMinimi | 8 | `zarco`, boss add | 300710 | v31 and v92: 8 spawns (4 per territory) alongside Acharak in 1300047, label 아카락의 부하 |
| 437,4 | Orcan Minion | (dungeon variant) | OrcanMinimi | | minion | | Karascha's Lair / Sorcha instance, hunting zone 437 |
| 437,5 | Orcan Raider | | OrcanPirate | | regular | | hunting zone 437 |
| 437,11 | Orcan Brute | | | | elite | | hunting zone 437 |
| 437,12 | Dwarf Orcan | | OrcanMinimi | | minion | | hunting zone 437 |

Adjacent, non-Orcan but part of the same story block:

| HZ,tpl | English name | Server name | Race | Lvl | Note |
|---|---|---|---|---|---|
| 13,601 | Dark Marauder | | mekonari | | Magical mercenaries embedded in the Orcan camp. v17 group 1300037 is literally "야영지 내부 어둠의 약탈자", dark marauders inside the camp |
| 13,1004 | Kugai | 노예 관리인 | SlaveManager | 10 | NOT an Orcan. Shares shapeId 300110 with 13,9 Destroyer. Spawn label 어둠의 인도자 쿠가이 |

### Name warnings worth carrying forward

- `13,901` and `13,1002` share the server name `오칸`. A spawn desc written from `NpcData.name` cannot tell
  Orcan Guardian from Acharak.
- `13,902` and `13,1003` share the server name `오칸미니미`, same problem.
- The v31 crash-site party spawns place template **901** but carry the spawn desc `오칸 습격자`, which is the
  name of template **5**. Do not infer the template from the spawn desc in group 1300035.

### Wider-world Orcans (they are not island-only)

Sweeping all `StrSheet_Creature` zones for "Orcan" returns 23 hits in v17, 39 in v31 and 56 in v92. The
species is pan-continental and grows across eras. Named tribes and locales, from the v31 client:

- HZ 7 Red Fang Orcan (Casidhe's Stand, quest band 7xx)
- HZ 12 Mistmoor Orcan Fighter, Mistmoor Orcan Scrapper
- HZ 24 Horned Orcan Berserker (Aurum Road)
- HZ 41 Black Claw Orcan (Feral Valley)
- HZ 45 / 426 / 478 / 726 Argonomorph Orcan variants (argon-corrupted)
- HZ 51 Cyasma-Riddled Orcan
- HZ 55 Bloodgulper Orcan (Ceravin Point, "the orcans are working with the unseelie!")
- HZ 87 an entire Orcan settlement: region string 87004 is **Orcan Hold**, with Orcan Tamer, Orcan Summoner,
  Orcan Deserter, Orcan Marauder, Brutal Orcan Soldier, Elite Orcan Combatant, Awkward Orcan
- HZ 112 Vindictive Orcan Mauler, HZ 416 / 437 Orcan Brute, HZ 1022 Nexus Orcan Thrasher
- v92 adds allied or neutral Orcans: HZ 739 Orcan Guard and Orcan Follower, HZ 833 **Orcan Chief** and Orcan
  Follower, HZ 939 Elite Orcan Guard, HZ 783 / 983 / 3018 Orcan Guard

The HZ 87 Orcan Hold cluster and the v92 Orcan Chief and Orcan Guard sets are the strongest evidence that
Orcans are a civilisation with ranks, tamers, summoners and deserters, not a mob family. There is also an item
`StrSheet_Item` 45444 **Orcan Soldier's Signet**, "A soldier's signet with the Orcan leader Rahto's emblem
imprinted on it", naming a second Orcan leader, **Rahto**, and item 5089, a flute "used to call upon the orcan
cooperators", implying Orcan factions that will work with players.

---

## 3. Quoted source text

### 3.1 v31 main line: the airship, the crash site, the raid

**Quest 1311, task 1, Bipi (64,1033).** MCP: `datasheet-v31 lookup_quest_dialogs 1311`. Client: v31c
`QuestDialog\QuestDialog-00440.xml`, `QuestDialog[id=11 huntingZoneId=13] > Text[id=3 huntingZoneId=64]`.

> I greet you, `<PCCLASS:lcase>`, with the worst of news. Our supply airship has crashed, and we've lost
> contact with its pilot.
>
> {@linkcreature:213#1007$$Chione} is smart and resourceful, but no soldier. A relief team is forming, but you
> are here now. Head east along this road and thin the ranks of the Dark Claw orcans, and recover any supplies
> you can while looking for Chione.
>
> Why are you still here?

**Quest 1311, Chione (213,1007), two lines.** Same query, texts 4 and 5.

> At last, a friendly face.
>
> It was a routine flight, until the explosion. After the crash, Terrons sprang from the wreckage, but they
> were definitely not on the manifest.
>
> I will wait here with the supplies you've recovered. The orcans seem content merely to watch me...for now.

> Be careful, `<PCCLASS:lcase>`. These orcans are not what they appear.
>
> Help me gather these supplies, and we can talk more.

**Quest 1311 summary, text 100.**

> Councillor Teil told you of Elleon's suspicions about the Tainted Gorge, and sent you to investigate. Along
> the way, you helped secure supplies from a crashed airship, and rescued its pilot from Orcans.

**Quest 1336, Chione (213,1007).** MCP: `lookup_quest_dialogs 1336`. Client: v31c `QuestDialog-00463.xml`.

> All around you is the result of an unavoidable situation. Orcans attempting to steal supplies caused the
> airship's crash, and even now trade our crates among themselves.
>
> It is imperative that those crates are recovered. If you would help, collect at least four and bring them
> here.

Turn-in, text 3:

> There was hope that one particular crate would be among those you found, one containing artifacts requested
> by **Sersine**. Your efforts are appreciated, of course.

### 3.2 The relic stones: the clearest statement of Orcan motive

**Quest 1337, Chione (213,1007).** MCP: `lookup_quest_dialogs 1337`. Client: v31c `QuestDialog-00464.xml`,
`QuestDialog[id=37 huntingZoneId=13] > Text[id=2 huntingZoneId=213]`. Journal blurb `@quest:1337005` is
"Fight through orcans and take back our supplies."

> The missing crate contains relic stones. Eria, child of Elinu, claims the stones are specially attuned to
> this island's guardians and will allow the soldiers of the Tainted Gorge more freedom of movement. They must
> be what the {@LinkCreature:13#901#orcan guardians} were seeking on the airship, but why?
>
> Recovering these objects is of great importance. Do not hesitate to use deadly force on the orcans, they
> have much to answer for.

Incomplete nag, text 4:

> Every hour that passes increases the risk that {@LinkCreature:13#901#orcan guardians} will damage the
> `<font color='#660000'>`relic stones`</font>` and endanger those who serve in the Tainted Gorge. Please do
> not tarry in their recovery.

### 3.3 Acharak, the Dark Claw warlord

**Quest 1309, v31 text, Chione (213,1007).** MCP: `datasheet-v31 lookup_quest_dialogs 1309`. Client: v31c
`QuestDialog-00438.xml`. Journal blurb `@quest:1309006` is "Clear out Acharak and his minions from the
Tainted Gorge Garrison."

> If orcans are to blame for the crash, then it was {@linkcreature:13#1002#Acharak} who ordered it.
>
> We have tracked his movements for weeks, but never have so many orcans gathered in one place.
>
> He must have overrun the Tainted Gorge Garrison, but a decisive blow will break their morale.
>
> Kill Acharak and take the Dark Claw tribe's talisman, a black feather. If Centurion Edan still lives, he will
> know what to do with it.

**Quest 1309, v31 turn-in, Edan (213,1134).**

> This token is so small, so simple, yet to the orcans it is a powerful talisman.
>
> For a courier, Chione has a surprising grasp of tactics. I'm impressed! You did a good job too, `<PCNAME>`.
> Thank you.

**Quest 1309, v17 text: DIFFERENT.** Client: v17 `QuestDialog\QuestDialog-00398.xml`,
`QuestDialog[id=9 huntingZoneId=13]`. In v17 the same quest slot places Acharak on **Arun Heights**, not the
Tainted Gorge Garrison, and the turn-in reading of the feather is stronger.

> This scroll mentions someone called Acharak. Sounds orcish, but it might well be the demon's name.
>
> We know where to look. Head to Arun Heights and locate {@linkcreature:13#1002#Acharak}.
>
> Kill him and bring back anything unusual or obviously magical.
>
> We're getting closer, `<PCNAME>`! We will have justice for Elleon!

v17 turn-in:

> This token is so small, so simple, yet it hurts just to hold it. Such power!
>
> This is no orcan talisman. Someone imbued this with a tremendous amount of magic. Someone else wants this
> island very badly.
>
> Well done, `<PCNAME>`. That fight couldn't have been easy.

v17 summary, text 100:

> Leander felt that whomever resisted Eria's probes was atop Arun Heights. You went there to confront this
> Acharak and encountered an orcan warlord.
>
> You fought Acharak and his minions and recovered a simple-looking feather that practically burned with
> arcane energy.

### 3.4 The mekonari alliance: quest 1307, identical in v17 and v31

MCP: `datasheet-v31 lookup_quest_dialogs 1307`. Client: v17 `QuestDialog-00396.xml`, v31c
`QuestDialog-00436.xml`.

Leander (213,1008), text 2:

> Orcans have some magic, but nothing of the level we're encountering. There's something else we're missing
> here.
>
> `<NEXTPAGEBUTTON>`"Perhaps the orcans have allies."`</NEXTPAGEBUTTON>`
>
> Exactly. Not just any ally, but someone more than magically adept. Kirash is keeping watch on the orcan
> bivouacs. Speak with him and find out if he knows anything about this.

Kirash (213,1027), text 3:

> Oh, we're watching the orcans, but they're not what's interesting. Look out there, see those bird-headed
> creatures with the large staves?
>
> `<NEXTPAGEBUTTON>`"Bird heads?"`</NEXTPAGEBUTTON>`
>
> Those are mekonaris and most of them are magical adepts. Who knows why these
> {@LinkCreature:13#601#dark marauders} are working with the orcans, but it won't be to our benefit.
>
> We must remain at our post, but sneak closer and capture or kill one of the marauders. Perhaps there are
> clues to be found.

Kirash, text 5:

> We remember tales of the mekonaris. While their god sleeps in a great golden egg, they sell their magical
> prowess to nearly anyone.
>
> Mercenaries of the worst kind. Pah!
>
> It's not surprising they'd work with these orcans. See what you can learn from one of them!

Task 2 journal blurb `@quest:1307007`, v17 `StrSheet_Quest-00384.xml`, v31c `StrSheet_Quest-00437.xml`:

> That's not an orcan! Kill it before it sounds an alarm!

Summary, text 100:

> Though Leander didn't believe the orcans capable of the magical feats necessary to corrupt Demonbane, he
> wasn't willing to make assumptions.
>
> He dispatched you to the south, where you spoke with Kirash, who explained about the presence of mekonari
> marauders, magical mercenaries.
>
> You crept into the bivouac, killed a dark marauder, and escaped with a scroll of demonic script. Leander
> translated part of it and learned the location of the mastermind, in the Tainted Gorge.

### 3.5 The garrison view: quest 1349, the "they keep reinforcing" line

MCP: `datasheet-v31 lookup_quest_dialogs 1349`. Client: v17 `QuestDialog-00435.xml`, v31c
`QuestDialog-00475.xml`. Giver Ayrdoss (213,1126). Identical text in v17, v31 and v92.

> Orcans in the camp below are continuously reinforcing from somewhere. It is only a matter of time before
> they build to a strength capable of seriously threatening the federation presence on the island. The proper
> military response is to remove them by force, but the scouts here are all those assigned to the problem.
>
> An excellent start would be to thin the ranks of {@LinkCreature:13#5#Orcan Raiders} patrolling the edge of
> their encampment.

Turn-in, text 3:

> Watching orcans run and hide is quite enjoyable. Come back and kill with us any time.

Journal blurb `@quest:1349004`, "Kill orcan raiders and dwarf orcans." Start popup `@quest:1349002`,
"Try not to die. Filling out reports is...unpleasant." Kill counts: 48 x `13,4`, 6 x `13,5`.

### 3.6 Other quests that touch the Orcans

**Quest 1306, Leander (213,1008).** v17 `QuestDialog-00395.xml`, v31c `QuestDialog-00435.xml`.

> Interesting. A dark energy, eh?
>
> Our scouts are watching an orcan force to the south, but it's inconceivable that they're responsible for
> this.
>
> `<NEXTPAGEBUTTON>`"What's the next step?"`</NEXTPAGEBUTTON>`
>
> Isn't it obvious? We must investigate the {@LinkCreature:213#1036#Shrine of Yurian}. We'll meet up at the
> shrine itself.
>
> Don't let any orcans follow us up, however. We're there to study, not fight.

**Quest 1343, Gregor (213,1028).** MCP: `lookup_quest_dialogs 1343`. The only line linking Orcans to the
codex leg.

> Nice to see a face that isn't attached to a blade or twisted by magic.
>
> The demons seem content to control the gorge, but be careful of orcan patrols at the summit.

### 3.7 Ambient villager dialog

All from v31c `VillagerDialog`, cross-checked against v17.

**Chione (213,1007)**, `VillagerDialog[id=1007 huntingZoneId=213] > Text[id=1]`. v31 only, absent in v17.

> This has not been the best of days.
>
> First the explosion, and now orcans. Hazard pay is definitely in order.

**Kirash (213,1027)**, `VillagerDialog-03014.xml`. Present in both v17 and v31.

> Noise means death here. The noisy and reckless will hear the laughter of Kirash, child of Karas,
> accompanying the clubs and claws of orcans.
>
> A true scout learns all there is to know before ever engaging the enemy face to face.

**Edan (213,1134)**, `VillagerDialog-03056.xml`. v31 only.

> When Acharak attacked, I managed to relocate most of our people to a temporary camp in the Tainted Gorge.
> It's not ideal, but it's good enough for now.
>
> I wish Elleon was here. He'd show those orcans a thing or two!

A full sweep of `VillagerDialog` in both clients returns **no other** Island of Dawn line mentioning Orcans.
Nothing in hunting zone 64 (the supply base), nothing in 13, 313, 364 or 436.

### 3.8 The Kugai / Karascha / Lok thread, and how weakly it connects

**Quest 1315, Sersine (213,1025).** MCP: `lookup_quest_dialogs 1315`.

> With what we have learned today, I cannot recommend that our forces withdraw from the island. But suspicions
> are not facts, and you hold in your hand the means to confirm them.
>
> {@linkcreature:13#1004#Kugai the Mighty} walks unmolested through demon infested lands, when so many of our
> comrades lie savaged at his feet.
>
> Search his corpse for clues.

Turn-in, two pages, and the **only** textual bridge to the Orcan chain:

> Kugai has fallen by your hand, but instead of answers you bring me more questions. This scroll bears similar
> markings to the tokens you collected earlier, an ancient language few understand. Few besides myself, anyway.
>
> (Sersine reads the scroll.)
>
> I fear a ritual is underway, meant to summon a darkness that will spread across the world.
>
> Conducted by a demon lord and servant of Lok thought defeated long ago.
>
> Karascha.

**Quest 1343, Leander (213,1008).** The codex translation. No Orcan appears in it.

> A codex? This could be the breakthrough we've hoped for! Hand it over!
>
> No mention of him. Alas.
>
> Indeed. However, the codex speaks of Karascha gathering power for some nefarious purpose. Wait, this can't be
> right. Impossible. Lok's dead.
>
> Take this to Sersine. Whatever his delusions, Karascha must be stopped, slain would be better.
>
> Most demons are very mercenary, they'll work for nearly anyone. Whoever bound Karascha to their will is very
> dangerous. This codex must be wrong, but Karascha must be stopped whether it is or not.
>
> Besides, Karascha's responsible for Elleon's...fate.

### 3.9 Mainland tribe confirmation (Black Claw = Dark Claw)

v31c `StrSheet_Quest-01293.xml` id 4124002, and `StrSheet_Quest-01303.xml` id 4134009:

> Take the fight to the Black Claw tribe.

> Kill Black Claw tribe fighters and take their warrior tokens.

v31c `StrSheet_Quest-01298.xml` id 4129006 (v17 wording, richer):

> Eliminate the Black Claw Warlords who have instilled fear in the Orcans, including Black Claw Berserkers,
> Black Claw Slaughterers and Black Claw Blood Fighters, and bring back their deranged eyeballs

The Korean-side link is the Acharak spawn desc in `TerritoryData_13.xml`, territory 1300995: `검은 발톱 아카락`,
literally "Black Claw Acharak". Same tribe name, two English localisations.

### 3.10 Items and flavour

| sheet | id | text |
|---|---|---|
| `StrSheet_Item` | 9000 | Orcan Rations |
| `StrSheet_Item` | 9287 | Orcan Jerky, "Dried meat; orcan style." |
| `StrSheet_Item` | 9288 | tooltip "An edible flower prized by orcans." |
| `StrSheet_Item` | 45444 | Orcan Soldier's Signet, "A soldier's signet with the Orcan leader Rahto's emblem imprinted on it." |
| `StrSheet_Item` | 5089 | tooltip "Small flute used to call upon the orcan cooperators. Only use at the secret meeting location." |
| `StrSheet_Item` | 50072 / 131466 | Dwarf Orcan Mask, "You're as dedicated to the slaughter as an orcan." |
| `StrSheet_Item` | 10573, 30345 | Orcan Oculus |
| `StrSheet_Region` | 13008 | **Orcan Bivouac** (Island of Dawn) |
| `StrSheet_Region` | 7008 | Orcan Bivouac (Casidhe's Stand, different continent, same string) |
| `StrSheet_Region` | 87004 | Orcan Hold (v31 and later only) |
| `StrSheet_Achievement` | 165001 | title "Dances with Orcans". Achievement 165 condition is `check templateId 4012 value1 4101`, a Feral Valley quest gate, so this title is mainland, not island |
| `StrSheet_Abnormality` | 47621200 | **Orcan Loyalty**, "Self-destruct. Orcan Loyalty cannot be removed." Also Orcan Might, Orcan Guile, Orcan Sloth I to VII. None of these are attached to any Island of Dawn Orcan template; they belong to the hunting zone 87 Orcan Hold set |
| `StrSheet_Dungeon` | 9019004 | "Red Fang orcans! Gods help us!" (Casidhe's Stand instance) |

**No book, codex or lore object anywhere in either client names the Orcans.** The only readable in-world
documents in the island arc are the demonic-script scroll (quest 1307), Kugai's scroll (1315) and Kugai's codex
(1343), and none of the three mentions Orcans in its translated text.

---

## 4. Geography

Island of Dawn is continent 13, area 7, area file `ATW_P`. Area recall point `66600.8672,-79855.5234,-2993.1643`.

### 4.1 Named sections in and around Orcan territory

From `AreaData\AreaData_13_ATW_P.xml` (v31 server). `nameId` resolves through `StrSheet_Region`.

| section id | nameId | Korean desc | English (StrSheet_Region) | polygon extent (x, y) |
|---|---|---|---|---|
| 56 | 13008 | 오칸 야영지 | **Orcan Bivouac** | x 49028 to 51017, y -77082 to -79127, z about -4700 |
| 52 | 13028 | 아룬의 언덕 | Arun Heights | x 50010 to 53696, y -73750 to -76965 |
| 31 | 13003 | 태고의 유적지 | Ancient Ruins | (the wider ruin field the bivouac sits in) |
| 47 | 13013 | 키오네 추락지 | Chione's Crash Site | x 65232 to 66587, y -69567 to -70826 |
| 34 | 13022 | 검은 틈 수비대 캠프 | Tainted Gorge Garrison Camp | x 63664 to 65536, y -64577 to -66608 |
| 54 | 13006 | 로크 추종자 기지 | Scions of Lok Base | x 57117 to 60654, y -72166 to -77995 |
| 43 | 13018 | 수비대 북부 캠프 | Garrison North Camp | x 72461 to 75596, y -81604 to -83680 |

**Orcan Bivouac polygon, exact**, section 56:

```
49859.4883,-79127.0391,-4713.7271
51016.5039,-77576.3125,-4732.8457
50058.0547,-77081.6875,-4661.1465
49028.2188,-78672.3594,-4715.5747
```

Centroid approximately `49990,-78114,-4706`, which is the "around 49991,-78114" figure in the brief. Confirmed.

### 4.2 The critical era divergence: the Orcans MOVED

The habitat group id **1300035** exists in both eras with completely different meaning and position.

| era | group 1300035 desc | English | territories | position |
|---|---|---|---|---|
| v17.11 | 태고의 유적지(야영지 내부 오칸) | Ancient Ruins, inside camp, Orcans | 14 | x 48858 to 52363, y -77060 to -80023, z about -4700 |
| v31 / v92 | 비행선 추락지(오칸) | **Airship crash site, Orcans** | 29 | x 63530 to 67009, y -66698 to -73000, z about -3400 to -4200 |

So in v17 the Orcan camp physically sat **inside the Orcan Bivouac section (13008) in the far southwest**, in
the Ancient Ruins, next door to Arun Heights where Acharak stood. In v31 NCSoft rewrote the arc around the
airship crash and relocated the whole Orcan population roughly 14000 units northeast, into and around
Chione's Crash Site and the Tainted Gorge Garrison. **The Orcan Bivouac region name was left behind, still
present in `StrSheet_Region` and still a live section polygon, but with no Orcan in it in stock v31.**

The v17 layout was a four-group camp:

| v17 group | Korean desc | English | territories | extent |
|---|---|---|---|---|
| 1300035 | 태고의 유적지(야영지 내부 오칸) | inside camp, Orcans | 14 | x 48858 to 52363, y -77060 to -80023 |
| 1300036 | 태고의 유적지(야영지 외곽 오칸 미니미) | camp outskirts, Dwarf Orcans | 4 | x 49709 to 50989, y -77346 to -79485 |
| 1300037 | 태고의 유적지(야영지 내부 어둠의 약탈자) | inside camp, Dark Marauders | 3 | x 49543 to 50638, y -77485 to -78850 |
| 1300038 | 태고의 유적지(오칸 순찰) | Orcan patrol | 7+ | x 50460 to 53039, y -77817 to -80970 |

That layout is exactly what quest 1307 describes: Orcans holding a camp, Dwarf Orcan minions on the perimeter,
mekonari dark marauders **inside** the camp, and patrols ranging out from it, with Kirash watching from
outside.

### 4.3 Current v92 state (important: partly this project's own work)

The v92 server has group **1300038 "태고의 유적지(오칸 순찰)"** live with 12 territories at
x 50325 to 53378, y -77817 to -82072, spawning templates `5` and `901` two at a time, and group **1300036**
with 4 territories spawning template `4` five at a time. These do **not** come from v31. They were authored by
this project in `specs/patches/001/15-iod-mob-habitats.yaml` (patch 001 IoD padding Wave B), which recovered
v17 fence geometry from the v17.11 client `TerritoryData` and repopulated it with v31 same-family donor
attributes. The spec header states plainly that "every group is an APPROXIMATION" and is divergence-logged.

Practical consequence: in stock v31, quest 1349 ("Kill orcan raiders and dwarf orcans", 48 x tpl 4, 6 x tpl 5)
was **unsatisfiable and shipped disabled**, because templates 4 and 5 had zero spawns anywhere. In current v92
it is live and satisfiable only because of the patch 001 restoration.

### 4.4 Named boss positions

From `TerritoryData_13.xml`, group 1300047 `네임드` ("named"):

| territory | label | English | position |
|---|---|---|---|
| 1300995 | 검은 발톱 아카락 | Black Claw Acharak | fence centre approximately `64636,-65570,-4213`; inside section 13022, the Tainted Gorge Garrison Camp |
| 1301440 | 사본 - 검은 발톱 아카락 | copy of the above | second layer instance |
| 1300996 | 어둠의 인도자 쿠가이 | Kugai, Guide of Darkness | same named group |
| 1300994 | 뾰족나무 베카스 | Vekas | npc spawn at `75488.83,-80699.18,-4145.54` |

Acharak's four fence points:

```
64862.32421875,-65467.88671875,-4180.92578125
64433.78515625,-65452.60156250,-4218.92578125
64473.76171875,-65671.82812500,-4241.84375000
64775.60546875,-65687.71875000,-4209.39062500
```

### 4.5 Airship crash site Orcan cluster (v31 stock, group 1300035)

Representative territory centres, all party spawns of template 901 labelled `오칸 습격자`:

```
1300903  approx 66897,-72515   1301341  approx 65607,-67096
1300904  approx 63870,-69386   1301342  approx 64305,-68209
1300905  approx 64105,-70641   1301343  approx 65299,-68603
1300906  approx 64504,-67594   1301344  approx 63919,-70201
1301011  approx 66792,-71690   1301345  approx 65773,-72823
1301368  approx 64766,-71126   1301346  approx 65264,-66877
1301369  approx 65426,-72447
```

The cluster runs as a corridor from the Tainted Gorge Garrison in the north (y about -66000) down past
Chione's Crash Site (y about -70000) to y about -73000, which matches Bipi's "head east along this road".

---

## 5. Gaps: what the sources do NOT say

Everything in this section is territory an authored event must invent. This project logs authored content as
AUTHORED, never as restoration, so these are the explicit boundaries.

### 5.1 Never stated anywhere

1. **Why the Orcans want the relic stones.** Chione asks the question in quest 1337 and the arc never answers
   it. No later quest, item or dialog returns to it.
2. **Who armed and directed them.** Quest 1309's v17 turn-in says only "Someone else wants this island very
   badly." That someone is never named. It is *not* explicitly Karascha, and it is *not* explicitly Lok.
3. **Whether the Orcans serve Karascha or Lok at all.** The chain runs Orcans, then mekonari mercenaries, then
   a scroll pointing at the Tainted Gorge, then Karascha. But the mekonaris are described as mercenaries who
   "sell their magical prowess to nearly anyone", which is a deliberate hedge. No line makes the Orcans
   worshippers, vassals or cultists of anything. **Do not write them as Lok cultists as if restoring; that is
   invention.**
4. **How the Orcans reached the island, or where the reinforcements come from.** Ayrdoss says they are
   "continuously reinforcing from somewhere" and nobody ever finds out where. This is the single largest
   deliberately open hook in the whole set, and the best hanging plot thread for an authored event.
5. **What Acharak wanted personally**, whether he had a superior, and whether the tribe survived his death.
   His death is a "decisive blow will break their morale" beat and the story simply moves on.
6. **Any Orcan speech.** Not one Orcan says a word in any era, on the island or the mainland. There is no
   Orcan voice, no Orcan name for themselves, no Orcan greeting, no shout line, no `popupMsg` on any island
   Orcan spawn. An authored event that gives them dialogue is inventing their voice from scratch.
7. **Orcan culture beyond three food items.** Rations, jerky, a prized edible flower. That is the entire
   material culture record for the island Orcans.
8. **Any relationship between the island Orcans and the Dwarf Orcans as a people.** `OrcanMinimi` versus
   `OrcanPirate` are race codes on the templates; no text ever explains whether Dwarf Orcans are a caste, a
   subspecies, children, or slaves.
9. **Whether the Orcans and the Scions of Lok (section 13006) are connected.** They occupy adjacent parts of
   the same map and no source ever puts them in the same sentence.

### 5.2 Ambiguous, so state your assumption

10. **The tribe name.** Korean says 검은 발톱 in both places. English says "Dark Claw" on the island and "Black
    Claw" on the mainland. Pick one and say why; do not present either as unambiguously canonical.
11. **Orcan Guardian (13,901) versus Orcan Raider (13,5).** The v31 crash-site spawns place template 901 but
    label the spawn 오칸 습격자, the raider's name. Whether "Guardian" is a rank, a role, or a localisation
    accident is not recoverable from the data.
12. **Dwarf Guardian (13,902).** Zero spawns in every era, no quest reference, no dialog mention. It exists
    only as a template and a name. Anything you do with it is entirely new.

### 5.3 Restoration boundary warnings

13. **The Orcan Bivouac (region 13008) is empty in stock v31.** Placing Orcans in the region that bears their
    name is a **v17 restoration** claim, not a v31 one. If the event is scoped v31-primary, populating the
    bivouac is authored content justified by a v17 precedent, and should be logged that way.
14. **The current v92 Orcan patrols in the Ancient Ruins (groups 1300036 and 1300038) are already this
    project's authored approximation**, from `specs/patches/001/15-iod-mob-habitats.yaml`. Do not cite them as
    a source of truth for where Orcans "belong". They are v17 fence geometry with v31 donor stats and
    round-robin template placement, and the spec says so.
15. **Field events do not exist before v92.** `datasheet-v31 list_field_events` reports the FieldData system is
    v92-only and absent from classic datasheets. Therefore **any** Guardian Legion field event featuring the
    Orcans is 100 percent authored. There is no classic Orcan field event to restore, no precedent for how one
    would have been tuned, and no era-authentic reward table to copy.
16. **Kugai is not an Orcan.** Race `SlaveManager`, model shared with the Destroyer, level 10 rather than 7 or
    8. Writing him as an Orcan leader would be a factual error, not a creative choice.
17. **Acharak's post-v17 relocation.** If the event stages a confrontation at Arun Heights, that is v17
    geography. If it stages one at the Tainted Gorge Garrison, that is v31 geography. They are mutually
    exclusive versions of the same quest slot and both are attested; pick one and note the era.
