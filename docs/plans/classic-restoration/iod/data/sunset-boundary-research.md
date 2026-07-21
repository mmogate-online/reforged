# Ride Off into the Sunset: Boundary Research

Read-only data capture for the IoD alpha-boundary design. Nothing was modified.

Note on long dash: one verbatim quest string (Leiyane, text 5) contains a literal long-dash character in the source. To satisfy the no-long-dash writing rule, it is rendered here as the HTML numeric entity `&#8212;`. That entity stands for a real long-dash glyph present byte-for-byte in the source XML.

Sources:
- v92 server datasheet (applied working tree): `D:\dev\mmogate\tera92\server\Datasheet`
- v92 client DC: `D:\dev\mmogate\tera92\client-dc\DataCenter_Final_EUR`
- v31 server (reference): `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet`

---

## 1. Quest identity

- Quest global id: **1317** (Quest번호 `13,17` = story group display 13, index 17; global id 13*100+17)
- Story group: **2** (스토리그룹Id), category 미션 (Mission), min level 10
- Title: "Ride Off into the Sunset"
- English title string found via client shard: `StrSheet_Quest/StrSheet_Quest-00341.xml`, row `id="1317001"`
- Server monolithic strings: `StrSheet_Quest.xml` rows 1317001..1317011 (v92 line 2781; v31 line 3369)
- Server quest file: `QuestData/001317.quest`
- Server quest dialog file: `QuestDialog/QuestDialog_1317.xml` (element `QuestDialog id="17" huntingZoneId="13"`)
- v31 quest dialog file (different naming scheme): `QuestDialog/QuestDialog_13_17.xml`

---

## 2. Quest file: server task tree (`QuestData/001317.quest`)

Header:
- Quest번호 `13,17`; 스토리그룹Id `2`; 제목 `@quest:1317001`
- 반복퀘스트 `1회성` (one-time, non-repeatable)
- 연결퀘스트 `1,1` (connectedTo global 101 = end-of-chain sentinel; this is the last quest in its forward chain)
- 수행조건 / 최소레벨 `10`
- 선행퀘스트 (prerequisite): quest `13,16` = quest **1316 "Dark Revelations"**
- 발생조건 / NPC대화 (giver / trigger NPC): `64,1001` = **Adria** in HZ 64 (Exploration Corps Supply Base, hub layer)
- 취소가능여부 `불가능` (not cancelable)
- 시작Task번호 `1`; 요약정보 `100`
- 시작시팝업대사 `@quest:1317002`; 종료시팝업대사 `@quest:1317003`
- 시작아이템 (start items): none; 추가보상 (extra reward): none; 퀘스트버프: none
- autoAccept: not set (accepted by talking to Adria 64,1001)

Tasks (all four are 방문Task, meaning "Visit/Talk" tasks):

| Task | Type | Target NPC (hz,villagerId) | NPC name | dialog (대사작성) | JournalScript | journal blurb | complete button | 다음Task | reward flag (보상) |
|------|------|----------------------------|----------|-------------------|---------------|---------------|-----------------|----------|---------------------|
| 1 | 방문Task | 64,1009 | Councilor Teil | 3 | 2 | @quest:1317005 | @quest:1317004 | 2 | 0 |
| 2 | 방문Task | 213,1001 | Taleb | 4 | 3 | @quest:1317007 | @quest:1317006 | 3 | 0 |
| 3 | 방문Task | 213,1016 | Flight Manager Leiyane | 5 | 4 | @quest:1317009 | @quest:1317008 | 4 | 0 |
| 4 | 방문Task | 63,1107 | Legate Troius | 6 | 5 | @quest:1317011 | @quest:1317010 | (none / final) | 1 |

**Departure / pegasus mechanism (spelled out):**
- The quest does NOT complete by clicking Leiyane's flight menu. Task 3 is only a *talk* task to Leiyane (213,1016) that explains how the pegasus UI works.
- Task 3's 다음Task is 4. Task 4 is a talk task to **Legate Troius (63,1107)** in **Velika (HZ 63)**.
- The player flies the pegasus manually (Leiyane's `Menu type="Pegasus" id="13"` binding, destination Velika), arrives in Velika HZ 63, walks to Troius, and talking to Troius completes task 4 (which carries 보상=1, the reward flag).
- So "arrival in Velika" is realized as a **talk-to-NPC task at the destination**, not an arrival trigger, item use, or the flight action itself. The flight is player-driven travel between task 3 and task 4; nothing in the quest forces or detects the flight except that Troius only exists in HZ 63.

**v31 comparison:** `Z:\...\v31.04\...\QuestData\001317.quest` is byte-for-byte identical to the v92 file (header, all four tasks, NPC ids, dialog refs, prereq, reward flag). Confirmed identical.

---

## 3. Quest strings, verbatim (server `StrSheet_Quest.xml`; identical in client shard `StrSheet_Quest-00341.xml` and in v31)

1. `1317001` = `Ride Off into the Sunset`
2. `1317002` (start popup) = `You've done all you can here. It's time to move on.`
3. `1317003` (end popup) = `Welcome to the city of Velika!`
4. `1317004` (task 1 complete btn) = `"I understand."`
5. `1317005` (task 1 journal) = `Speak to Councilor Teil.`
6. `1317006` (task 2 complete btn) = `"Leiyane. Got it."`
7. `1317007` (task 2 journal) = `Speak to Taleb.`
8. `1317008` (task 3 complete btn) = `"Thanks."`
9. `1317009` (task 3 journal) = `Speak to Flight Manager Leiyane.`
10. `1317010` (task 4 complete btn) = `"I did my duty. Nothing more."`
11. `1317011` (task 4 journal) = `Take the pegasus to Velika, then speak with Legate Troius.`

(Server v92 `StrSheet_Quest.xml` line 2781; v31 line 3369; client shard `StrSheet_Quest-00341.xml` line 2. All three copies match exactly.)

---

## 4. Quest dialogs, verbatim (`QuestDialog/QuestDialog_1317.xml`; identical to v31 `QuestDialog_13_17.xml`)

Wrapper: `QuestDialog id="17" huntingZoneId="13" voiceTypeId="0"`. Each Text = one NPC dialog window; `<BR>` = line break (stored escaped as `&lt;BR&gt;`).

**Text 1** [hz 0, villager 0]: empty placeholder (no page).

**Text 100 (summary)** [Adria, hz 64 villager 1001], social 0:
> Adria and Teil thanked you for your valorous service, but said your skills are needed elsewhere.<BR><BR>They directed you to the flight master, who put you on a pegasus and sent you on a dizzying flight to Velika, where Legate Troius personally welcomed you!

**Text 2 (intro / accept dialog)** [Adria, hz 64 villager 1001], social 4:
> Word is spreading about everything you've done for us here, <PCNAME>. And it's reaching some very well-connected ears.<BR><BR>Report to <b>Councilor Teil</b>, he's eager to talk to you.

**Text 3** [Councilor Teil, hz 64 villager 1009], prevId 2, 2 pages, social 4:
- Page 1: `In the name of the Valkyon Federation, I'd like to extend our thanks for everything you've done. Adria, Sersine, and Leander speak quite highly of you.<BR><BR>The federation needs good soldiers elsewhere, however. With Karascha's death, we can make do here. It's time for you to go to Velika!<BR><NEXTPAGEBUTTON>"Yes, sir!"</NEXTPAGEBUTTON>`
- Page 2: `{@linkcreature:213#1001#Taleb} will help you arrange your return to Arun.<BR><BR>He's just on the other side of this pavilion.`

**Text 4** [Taleb, hz 213 villager 1001], prevId 3, social 4:
> I've been expecting you, <PCNAME>.<BR><BR>We've adjusted your orders so that you remain on detached duty. This should let you search for Elleon without too much interference, but you're still expected to complete any orders you're given.<BR><BR>And on a personal note, I hope you enjoy the pegasus flight to Velika. There's some really impressive scenery around the city.<BR><BR>Flight Manager Leiyane will get you saddled up.

**Text 5** [Leiyane, hz 213 villager 1016], prevId 4, social 4:
> Pegasus travel is for long journeys&#8212;like back to the mainland and the capital, Velika.<BR><BR>Just click the <font color='#660000'>Take a Flight</font> button and choose your destination. It's that easy!<BR><BR>For your first trip, select <B>Velika</B> as your destination.<BR><BR>Oh, and please turn off any magical devices until you've reached your cruising altitude.

(The `&#8212;` after "journeys" is a literal long dash in the source XML.)

**Text 6** [Legate Troius, hz 63 villager 1107], prevId 5, social 4:
> <PCNAME>! I have been waiting for you.<BR>My name is Troius, and let me be the first to welcome you to Velika the City of Glory!<BR><BR>I must admit, I haven't seen orders like yours before, but they're all filed and registered. Even Commander Seir was impressed, and sent me here to wait for your arrival.

Token note: text 3 page 2 contains `{@linkcreature:213#1001#Taleb}` (a clickable creature link to Taleb, hz 213 villager 1001).

---

## 5. Leiyane (flight master)

**Identity (client `StrSheet_Creature/StrSheet_Creature-00000.xml` line 7171):**
```
<String name="Leiyane" templateId="1016" gender="female" race="Highelf" title="Flight Manager" class="" />
```
- Client display name: **Leiyane**, title "Flight Manager", female Highelf.
- Server internal/Korean name (NpcData_213 Template id 1016): `레니아`; spawn desc `이동관리인 레니아` ("Flight Manager Leiyane").

**Location:** She is villager **templateId 1016 in HZ 213** (the *social* layer of Island of Dawn, 여명의 정원; base HZ 13, continent 13, area 13/ATW_Death_P). She is referenced by the quest at `213,1016`. She is NOT in HZ 64 or HZ 13; she lives on the 213 social layer.

**Spawn (server `TerritoryData_213.xml`, present and active):**
```
<Npc instanceId="1305602" desc="이동관리인 레니아" npcTemplateId="1016" ai="100"
     randomPos="false" spawnCount="1"
     pos="70920.50000000,-69947.79687500,-3336.96484375" offsetZ="0" dir="277"
     respawnTime="10000" ... />
```
- She has Patrol nodes (e.g. `65968.23,-70448.13,-3666.05` and `74112.07,-82462.05,-3554.80`).
- Template (`NpcData_213.xml` Template id 1016): `villager="true" shapeId="500142" basicActionId="5001400" race="Highelf" gender="female" aiid="103" invincible="true" questVillager="false"`.

**VillagerMenu binding (server `VillagerData/VillagerMenu.xml` line 5283):**
```
<Villager id="213,1016" guideEffectId="106">
    <Menu type="Pegasus" id="13" />
</Villager>
```
- Single menu entry: **`Menu type="Pegasus" id="13"`**. This IS the pegasus/travel function (the "Take a Flight" button; flight table id 13). No other menu entries.

**SpeechCondition (.condition file):** NONE for Leiyane. There is no `VillagerData\...001016.condition` for HZ 213 (checked `002130000001016.condition`, which does not exist). The file `VillagerData\00630000001317.condition` matched only by filename coincidence: it belongs to villager id **1317** in HZ 63 (Ghislain Rionas / 기슬란 리오나스 in Velika), unrelated to this quest.

**Villager speech text (client-side family):**
- Family/folder: **`VillagerDialog`** (element root `VillagerDialog`, Novadrop DC). Leiyane's lines live in `VillagerDialog/VillagerDialog-03804.xml` (`id="1016" huntingZoneId="213" voiceTypeId="49"`).
- Server counterpart: `VillagerDialog/VillagerDialog_213.xml`.
- Her current lines verbatim:
  - Text 1 (social 4, endSocial 14): `Your orders, please.<BR><BR>(If you're level 10 or higher, you can take the pegasus to Velika.)`
  - Text 99 (social 4, endSocial 14): empty page (placeholder).

---

## 6. Reward: `CompensationData/QuestCompensationData_13.xml` (questId 1317, what was ported)

```
<Quest questId="1317">
  <Compensation compensationId="1">
    <CompensationType type="normal" exp="2000" gold="200" itemBag="class">
      <Item templateId="15667" quantity="1" class="lancer;berserker;engineer;fighter" />
      <Item templateId="15670" quantity="1" class="warrior;slayer;archer;glaiver" />
      <Item templateId="15673" quantity="1" class="sorcerer;priest;elementalist;assassin" />
    </CompensationType>
  </Compensation>
</Quest>
```
- exp 2000, gold 200, itemBag `class` (class-gated single pick).
- Reward items are level-11 body armor (one per armor weight):
  - 15667 "Outrider's Chestpiece" (plate/bodyMail): lancer;berserker;engineer;fighter
  - 15670 "Sentry's Jerkin" (leather/bodyLeather): warrior;slayer;archer;glaiver
  - 15673 "Outrider's Robes" (robe/bodyRobe): sorcerer;priest;elementalist;assassin
- Reward is granted on completion of task 4 (task 4 has 보상=1).

---

## 7. Downstream references (inbound)

- Story position: **last quest in its forward chain** (연결퀘스트 `1,1` points to global 101 end-of-chain sentinel; trace confirms `1317 -> 101` with no backward chain). Its own prerequisite is 1316 "Dark Revelations".
- **Inbound prerequisite reference found:** quest **6359** (Quest번호 `63,59`, story group 4, title `@quest:6359001`) lists quest 1317 (`13,17`) as one of its 선행퀘스트 prerequisites (alongside `599,11`). File: `QuestData/006359.quest` lines 19-25.
  - Meaning: completing "Ride Off into the Sunset" (reaching Velika) is a gate for a later Velika/mainland quest (6359). Removing or breaking 1317 would block 6359's availability.
- No other quest references quest id 1317 (grep of `QuestData` for `13,17` returns only `001317.quest` itself and `006359.quest`).

---

## Summary of the departure mechanic (design-relevant)

The IoD-to-Velika hand-off is a soft, player-driven boundary. Adria (64,1001) gives the quest, Teil (64,1009) authorizes departure, Taleb (213,1001) processes orders, Leiyane (213,1016) explains the pegasus (`Menu type="Pegasus" id="13"`), the player flies to Velika (HZ 63) at will, and the quest only *closes* when the player talks to Troius (63,1107) on the far side. There is no arrival trigger, no forced teleport, and no item consumption; the flight itself is optional travel and the quest completion is a destination talk-task. Leiyane's pegasus menu is level-gated at 10 both by her ambient line and by the quest's own min level 10.
