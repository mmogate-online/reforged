# v17.11 Client Merchant / Shop Extraction (Island of Dawn)

Scope zones: 13, 64, 213, 313, 364, 436.

## Headline finding: no merchant sell lists in the client

**Does the v17.11 client carry merchant SELL lists (store inventories, i.e. what merchants sell to players)? NO.**

All 258 client families enumerated; the only shop/menu family is VillagerMenu, a bare <Villager id="hz,tid"/> registry with no child inventory (child tags: none). No StoreData / StoreSellList / MenuList / price / goods family exists. ReputationItem is a reputation-vendor placeholder, TradeBroker* is auction-house UI. Gold-merchant store inventories are server-side, so v31 is the source for shop sell lists.

Consequence: v31 (server datasheet) is the source of truth for IoD merchant shop inventories; the client cannot supply them.

## Shop-related client families (name scan)

Of 258 client families, the name-based shop/menu/price scan surfaces only:

- `GambeItemData`
- `GambleBoxData`
- `ReputationItem`
- `TradeBrokerCategory`
- `TradeBrokerSetting`
- `VillagerMenu`

Assessment of each:

- `VillagerMenu` - bare registry of menu-bearing NPCs; **no inventory** (see below).
- `ReputationItem` - reputation-vendor SellItem list, npcGuild-keyed, placeholder/dummy rows; not IoD gold merchants.
- `TradeBrokerCategory` / `TradeBrokerSetting` - auction-house (trade broker) UI category tree and settings, not merchant stores.
- `GambleBoxData` / `GambeItemData` - loot-box tables, not stores.

## VillagerMenu (the client NPC linkage)

Shard `VillagerMenu-00000.xml` holds 1136 `<Villager id="hz,tid"/>` entries. Every entry is self-closing; the only child tags present are: none. There is no sell list, buy menu, price, or menu-type content.

VillagerMenu id="hz,tid" registers a client interaction menu for NpcData Template id=tid inside the huntingZoneId=hz shard (which carries villager="true"); the display name resolves from StrSheet_Creature by (HuntingZone id, templateId). The client marks an NPC as a menu-bearing villager but does not encode what it sells.

### Scope-zone villager-menu NPCs

Per-zone counts of VillagerMenu entries in scope:

| Zone | Villager-menu NPCs |
|------|--------------------|
| 13 | 0 |
| 64 | 18 |
| 213 | 7 |
| 313 | 5 |
| 364 | 5 |
| 436 | 1 |

Full list (name/title from StrSheet_Creature; blank = template not named in the client creature strings):

| hz | templateId | Name | Title | Race |
|----|-----------|------|-------|------|
| 64 | 1002 | Poron | Banker | Popori |
| 64 | 1003 | Kerson | Banker | popori |
| 64 | 1004 | Viator | Crystal Merchant | Castanic |
| 64 | 1005 | Rutgar | Merchant | Human |
| 64 | 1007 | Gurney | Tactics Instructor | Human |
| 64 | 1008 | Charise | Magic Instructor | Highelf |
| 64 | 1010 | Donush | Cleric of Blessing | Human |
| 64 | 1050 | Hermaiorni | Teleport Master | Popori |
| 64 | 1052 | Ailesa | Weapon Merchant | Highelf |
| 64 | 1053 | Mahadam | Armor Merchant | Aman |
| 64 | 1054 | Ellis | Election Registrar | Human |
| 64 | 1055 | Morel | Guild Manager (Test) | Human |
| 64 | 1056 | Lailah | Policy and Tax Rate Aide (Test) | Human |
| 64 | 1601 | Vene | Aide | Human |
| 64 | 1602 | Mission Board | Valkyon Forum | Object |
| 64 | 1603 | Sripi | Guild Quest Rewards | Human |
| 64 | 2501 | Teleportal |  | Object |
| 64 | 9000 | T-cat Exchanger |  | popori |
| 213 | 1015 | Teleportal |  | Object |
| 213 | 1016 | Leiyane | Flight Master | Highelf |
| 213 | 1023 | Junia | Tactics Instructor | Castanic |
| 213 | 1024 | Volis | Magic Instructor | Highelf |
| 213 | 1030 | Ferya | Cleric of Blessing | popori |
| 213 | 1051 | Elinnia | Cleric of Blessing | popori |
| 213 | 1129 | Lucrece | Cleric of Blessing | Highelf |
| 313 | 1002 | Ashley | Lord Immediate Merchant (Test) | Human |
| 313 | 1003 | Harger | Lord Immediate Cleric of Recovery (Test) | Human |
| 313 | 1004 | Slagger | Lord Immediate Superior Cleric of Recovery (Test) | Human |
| 313 | 1007 | Teiger | Lord Immediate Tactics Instructor (Test) | Castanic |
| 313 | 1008 | Misrile | Lord Immediate Magic Instructor (Test) | Highelf |
| 364 | 1001 | Ainah | Specialty Store | Highelf |
| 364 | 1101 | Hyneu | Cleric of Restoration | Popori |
| 364 | 1102 | Hyneu | Noble Cleric of Restoration | Popori |
| 364 | 1201 | Huria | Tactics Instructor | Highelf |
| 364 | 1301 | Lowing | Magic Instructor | Popori |
| 436 | 1501 | Teleportal |  | Object |

## ReputationItem (reputation vendor, not a gold merchant)

Shard `ReputationItem-00000.xml` has 143 SellItem rows, keyed by npcGuildId + reputationPoint (reputation vendor). placeholder/dummy rows, not IoD gold-merchant inventory; keyed by npcGuild not NPC template. Sample rows:

| Id | name | grade | npcGuildId | reputationPoint |
|----|------|-------|-----------|-----------------|
| 123 | 열라 좋은 무기1 | 4 | 11 | 500 |
| 124 | 열라 좋은 무기2 | 2 | 22 | 600 |
| 125 | 열라 좋은 무기3 | 3 | 33 | 700 |
| 126 | 열라 좋은 무기4 | 4 | 44 | 800 |
| 127 | 열라 좋은 무기5 | 5 | 55 | 900 |
| 128 | 열라 좋은 무기6 | 6 | 66 | 1000 |
| 129 | 열라 좋은 무기7 | 7 | 77 | 1100 |
| 130 | 열라 좋은 무기8 | 8 | 88 | 1200 |

