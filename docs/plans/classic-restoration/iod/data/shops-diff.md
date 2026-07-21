# IoD Shops Diff (v31 vs v92)

Phase 3 diff artifact for the v31-primary Island of Dawn restoration. Source of truth is v31;
every v92-only row carries a disposition (PORT / KEEP / REMOVE / DECISION / MATCH).

Machine artifact: `shops-diff.json` (per-merchant, per-store, per-tab item lists and blast radius).

## Sources and model

- v31 server: `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet`
- v92 server: `D:\dev\mmogate\tera92\server\Datasheet` (clean baseline, patch state reverted today)
- Binding: `VillagerData/VillagerMenu.xml` `<Villager id="hz,tid"><Menu type= id=/>`; a store-type
  menu (Merchant / MedalStore / PointStore / BuyMenuMedal / guildStore / BattleFieldStore /
  FloatingCastlePartsStore) points its `id` at a `BuyMenuList.xml` store.
- Store: `BuyMenuList.xml` `<Menu id desc><ItemList id/>` (a store is a menu with tabs).
- Tab contents: `BuyList.xml` `<List id><Item priceRevision itemId/>`.
- Item validity: `ItemTemplate.xml` (`<ItemData><Item id=/>`) is the v92 id universe.
- Names: `StrSheet_Creature.xml` per (huntingZone, templateId).

Price note: BuyList carries `itemId` + `priceRevision` only; gold price is resolved server-side by
priceRevision and is not encoded, so price is out of scope for this diff.

Scope zones queried: 13, 64, 213, 313, 364, 436, 9036. No merchant NPC exists in 436 or 9036 on
either side; v31 has no villager merchant in combat zone 13 at all (v31 IoD merchants live only in
the safe-zone layers 64 / 213 / 313 / 364). All zone-13 merchants are a v92 addition.

## Verdict counts

Merchants in union roster: 18. MATCH 1, PORT 4, DECISION 4, KEEP 9 (all v92-only zone-13 hub layer).
Ailesa is PORT with a new-class KEEP exception (counted under PORT). Ashley is PORT at the binding
level (re-bind the NPC to the existing store 250); the store 250 *content* is a separate shared
DECISION (item 1 below) that also covers Ainah and Thagall.

## Real v31 IoD merchants (safe-zone layers)

| NPC (hz,tid) | Name / role | v31 store | v92 store | Shared non-IoD | Verdict | Disposition |
|--------------|-------------|-----------|-----------|----------------|---------|-------------|
| 64,1004 | Viator, Crystal Merchant | Merchant 100 | Merchant 100 | 1 | DECISION | store 100 content differs and is shared with 60,1002 |
| 64,1005 | Rutgar, general goods | Merchant 16064 | Merchant 16064 | 0 | PORT | store IoD-exclusive; v31 wins; 2 items skip |
| 64,1052 | Ailesa, weapons | Merchant 211 | Merchant 211 | 0 | PORT (KEEP exc.) | v31 subset of v92; 4 v92-only items are new-class weapons, KEEP |
| 64,1053 | Mahadam, armor | Merchant 210 | Merchant 210 | 0 | MATCH | v92 already equals v31 |
| 64,8000 | Ellonia, medal store | MedalStore 331 | BuyMenuMedal 1008 | 29 | DECISION | binding changed; v31 is a Halloween event vendor |
| 64,9000 | Tikat (T-cat Exchanger) | MedalStore 315 | MedalStore 315 (empty) | 24 | DECISION | v31 winter-event store; v92 store emptied; 33/37 items gone |
| 213,1054 | Sandom, general goods | Merchant 16090 | Merchant 16090 | 0 | PORT | store IoD-exclusive; identical shape to Rutgar; 2 items skip |
| 313,1002 | Ashley, Lord Immediate Merchant (Test) | Merchant 250 | (unbound) | 35 | PORT + DECISION | re-bind NPC to store 250 (PORT); store 250 content is shared DECISION |
| 364,1001 | Ainah, Specialty Store | Merchant 250 | Merchant 250 | 35 | DECISION | store 250 shared 35x; classic charm tab empty in v92 |

### PORT detail (clean, IoD-exclusive stores)

- **Rutgar 16064 / Sandom 16090** (same store shape, "supply base" / "garden field" general goods).
  v31 stocks the classic consumable set: Tier 3-6 Alkahest (94203-94206), bandages (125-128, 7154,
  7155), Ranger's Nostrum and Nostrum of Energy I-V (6283-6292), identification and enigmatic scrolls
  (91, 92, 93), campfire / firewood (98, 99). v92 had swapped in a newer set (139093, 206046, 206049,
  206600, 206610, 206620 in tab 1601; 6550-6562 and 200997-200999 in tab 1602). v31 wins: restore the
  classic lists. Two v31 ids do not exist in v92 ItemTemplate and become skip rows: **213307, 219000**
  (both tab 1601).
- **Ailesa 211** (low-level ceremonial weapons). v31 is a strict subset of v92. The 4 v92-only ids are
  new-class starter weapons and are KEPT under the adaptation whitelist (rule 2, new-class support):
  58312 / 58313 Ceremonial Shuriken (Ninja), 82208 / 82209 Ceremonial Powerfists (Brawler). Net: no
  removal; binding already matches, so this is effectively MATCH-plus-KEEP.

## v92-only zone-13 hub merchant layer (KEEP, pending policy)

v31 combat zone 13 has no villager merchants. v92 added a full merchant layer directly in zone 13.
All are v92-only and default to KEEP with reason "v92 IoD redesign hub merchant, not present in v31".
Whether the restoration keeps this hub or removes it to match v31's merchant-free combat layer is a
doctrine-owner policy DECISION. All of them bind to game-wide shared stores (see blast radius below).

| NPC (hz,tid) | Name | Store bound (type,id) |
|--------------|------|-----------------------|
| 13,1271 | Vardung | Merchant 10050 |
| 13,5001 | Marpa | Merchant 16091 |
| 13,5004 | Thagall | Merchant 250 |
| 13,5005 | Rendall | PointStore 6090 |
| 13,5006 | Conifi | PointStore 609 |
| 13,5008 | Gardeng | Merchant 110 |
| 13,5101 | Tienna | Merchant 16092 |
| 13,5201 | Cynapelle | Merchant 16092 |
| 13,5301 | Kenritt | Merchant 16092 |

## DECISION list (shared stores, blast radius)

Under v31-primary the default is v31-wins for IoD-scoped stores, but a store referenced by non-IoD
merchants cannot be ported without changing those merchants. Each of these needs an explicit call.

1. **Store 250 "luxury/charm store"** - blast radius **35 non-IoD v92 merchants** (36 refs total incl.
   Ainah, Thagall; Ashley is unbound in v92). This store holds the classic charm vendor tab **2502**
   (Power/Keen/Speed/... charms 178-193 plus Greater charms 70019-70034 plus Tier 6 Alkahest 94206,
   33 items) which is **empty in v92**. All 33 charm ids exist in v92 ItemTemplate (valid). tab 2501:
   v31 has bandages 171-177 and Combat Panacea/Rapid Resurrection; v92 swapped in newer nostrums
   (6550-6562, 200997-200999, 1189, 21355, 202015). tab 2505: v31 21 teleport scrolls, v92 expanded
   to 47. Porting v31 store 250 content would add charms to all 35 non-IoD merchants game-wide. Note
   the adaptation whitelist (rule 1) already schedules charms as patch 001 content, so the charm
   restoration may be better delivered through a dedicated IoD-scoped charm store rather than by
   overwriting shared store 250.
2. **Store 315 "T-cat winter-event exchanger"** - blast radius **24 non-IoD v92 merchants**. v31 has
   37 medal items across tabs 3000/3001/3002; v92 emptied store 315 game-wide. 33 of the 37 v31 ids do
   not exist in v92 ItemTemplate (see missing-item list). Recommendation: OMIT (seasonal event content,
   items removed from the item table); porting is not achievable without re-adding 33 event items.
3. **Store 100 "low-level crystal shop"** - blast radius **1 non-IoD merchant (60,1002)**. tab 1001:
   v31 10 crystals are a subset of v92's 20 (v92 added 8142/8143/8156/8157/8242/8243/8314/8315/8530/
   8531). tab 1002: v31 8 crystals are a superset of v92's 2 (v92 dropped 8494/8495/8506/8507/8518/
   8519). v31-wins would trim tab 1001 and re-add tab 1002 crystals, also affecting merchant 60,1002.
   All ids valid. Small blast radius but not zero.
4. **Ellonia rebinding 331 -> 1008** - v31 binds Ellonia to MedalStore 331 "Halloween Festival
   Merchant" (event vendor, IoD-exclusive store, tabs 9149/9150/9151); v92 rebinds her to the generic
   BuyMenuMedal store 1008 (shared by 29 merchants, lives in the newer BuyMenuData family). This is a
   seasonal event vendor. Recommendation: OMIT the event binding (do not restore Halloween store 331),
   or explicitly decide to keep the v92 generic medal binding.
5. **Zone-13 v92-only hub merchant layer (9 NPCs above)** - policy DECISION: keep the v92 IoD hub
   redesign, or remove it to match v31's merchant-free combat zone 13. Their shared stores: 250
   (35 non-IoD), 110 (34 non-IoD), 6090 (3), 609 (4), 16091 (Marpa only), 16092 (the three brokers,
   IoD-internal), 10050 (Vardung).

## Missing item list (v31 ids absent from v92 ItemTemplate)

52 v31 store items do not exist in the v92 item table. If their store is ported they become
adaptation-or-skip rows. Breakdown by store:

- **Store 315 (Tikat, T-cat winter event)** - 47 of its ids missing. tab 3000: 210888, 213876, 213877,
  214630. tab 3001: 210555, 210557, 210643, 210647, 210770, 211699. tab 3002: 210535, 210536, 210892-
  210897, 213036, 213039, 213042, 213839-213847, 214023-214025, 214209-214211, 214561. (Confirms the
  OMIT recommendation.)
- **Store 609 tab 6093 (Conifi PointStore, v92-only merchant)** - 213363-213370, 213815-213818, 214459.
  These are v92-only anyway (KEEP layer), listed only because the tab id collides in reverse.
- **Stores 16064 / 16090 (Rutgar / Sandom)** - 213307, 219000 (both tab 1601). Only these two block the
  otherwise-clean PORT; skip them.

All charm ids (178-193, 70019-70034) and Tier 6 Alkahest (94206) referenced by store 250 exist in v92
ItemTemplate and are valid to port.
