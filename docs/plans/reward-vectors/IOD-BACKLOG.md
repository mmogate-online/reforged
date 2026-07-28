# IoD Reward-Vector Backlog

_Status: adopted 2026-07-26 (planning session). Forward design (patch 003+ lane), not classic restoration: implementation starts only after patch 002 closes, and applies via migrate batches per the patch discipline. The classic-restoration doctrine still governs anything that touches restored content; deliberate deviations land in the IoD divergence log (`docs/plans/classic-restoration/iod/divergence-log.md`)._

Goal: make the Island of Dawn region (HZ 13/64/213/313/364, dungeons 436/continent 9036 and 437/continent 9037) compliant with the content-framework reward vision before first release.

**This document is self-contained.** It records the session's rulings (section 1), the vector design contract (section 2), the work items (sections 3 and 5), and a mechanism dossier (section 4) holding what a research wave over the canonical server data established, including the gaps. An implementing agent should not need the originating session; where a fact below feels thin, section 0 says where to dig deeper.

## 0. Sources for further research

- **Design authority:** the content-framework repo (resolve `content_framework` in `.references`). Citations below use its `NN §x` convention. Session-relevant sections: `11-region-progression.md` (whole doc), `03 §3d` (reputation architecture), `03 §3b-i` (early-prog token), `03 §3a/§3c` (per-content tokens, power-spend registry), `02 §2/§5` (XP weighting, token sources), `08 §4` (unlock-mechanism distinction), `10 §1b/§5` (loneliness economy, reputation flywheel), plus locked invariants in its CLAUDE.md.
- **Game-data documentation:** the datasheet-domain knowledge base (navigate via its curated index, per this repo's CLAUDE.md "Domain Knowledge"). Docs cited below by name live under `entities/` (e.g. `quest-system.md`).
- **Live data queries:** the `datasheet-v92` MCP (current state / validation target) and `datasheet-v31` MCP (historical reference); route questions per the `domain-research` skill. Known MCP gap: no Achievement, WorkObject, Treasure, CollectionBook, or AreaData-section families (`docs/mcp-requests/2026-07-26-achievement-workobject-families.md`); those need raw-XML reads under `server_datasheet` / `client_datacenter` from `.references` until delivered.
- **Era archaeology sources:** `v31_datasheet` (v31 server), `client_dc_v31` (v31 client DC), `old_client_dc` (v17.11 client DC), all in `.references`. Findings already extracted are in §4.7; re-derive only if contradicted.
- **Project background:** `docs/plans/classic-restoration/iod/TRACKER.md` (current IoD state, patch 002), `docs/plans/classic-restoration/iod/data/padding-sorcha-dungeon-investigation.md` (dungeon 9037 event scripting, tile-sharing proof).

## 1. Session rulings (2026-07-26, all user-confirmed)

| # | Ruling |
|---|--------|
| R1 | The early-progression token (`03 §3b-i`, `02 §5`) is IoD's cross-vector reward spine: every vector pays some of it |
| R2 | Karasha NM and HM share ONE dungeon token; HM pays a higher quantity (`03 §3a`: difficulty modifies quantity, not type) |
| R3 | Sorcha: entry is never limited; rewards are shaped (uncapped base token drops + daily bonus quest). No EventMatching anywhere: dailies use the classic faction daily-pool system (now specced as `03 §3d`) |
| R4 | Repeatables keep hard level caps (v31-authentic); the cap is an effective-level placeholder for the future level-sync feature (`02 §7`) |
| R5 | Region-unlock challenge: authored into the framework (`11-region-progression.md`, DONE) before balancing content against it; season-1 unlock is an ops-managed flip; the persistent world flag is a future server feature |
| R6 | Reputation vector: adopt the classic faction-daily architecture at the IoD level band by repurposing a dormant faction id (610-617); reputation and dailies are one system |
| R7 | Karasha HM is a new dungeon continent (9536 / HZ 536), probe-first epic |
| R8 | Exploration is a three-layer loop: landmark achievements + one-time cache quests + key-item treasure chests; the cache quest journal entry is a deliberate breadcrumb (waypoint on the chest via StrSheet_WorkObjectLoc) |
| R9 | Backend infrastructure raised by content design (one-time quest latch persistence, world flags) is owned by the Mystel Proxy team; this repo ships content only |
| R10 | Zone quest completion XP is capped at 25% or less of the equivalent story quest's XP (strawman ratio; framework `02 §2` zone-quest XP note). Story XP is NOT nerfed: the spine stays self-sufficient to the bracket top (level 10, live-validated). Repeatables share the cap; faction dailies grant zero or near-zero XP per classic. The removed XP value is compensated in non-XP rewards (reward parity, `03 §3b-i`): story = "level faster", zone content = "get stronger" |
| R11 | Token shops are PHYSICAL NPC VENDORS, never inventory right-click (MEDAL_USEABLE) shops: players must navigate the map, which keeps the region feeling busy. Aligns with framework `03 §5` ("token shop at a vendor NPC"). Sorcha's shop is Sorcha herself at Tower Base flanked by her guards; the Karasha shop's NPC model and placement are a lore call inside RV-05; the existing Kugai's Crest right-click shop converts to an NPC vendor. NPC-attached token shops are canon-proven but not yet exercised end to end by this project (first exercise = RV-02) |
| R12 | The mystery merchant system is adopted for IoD as a REPLAYABILITY vector: revive the dangling v92 "Vardung, Island of Dawn Mystery Merchant" wiring as a wandering merchant with a randomized, GOLD-priced, per-appearance-rerolled catalog (not the Mystery Market Coin economy). Framework home: `07 §4`. See D §4.8 and RV-25 |
| R13 | Content-drop discipline: direct feedstock drops are REMOVED (fodder dismantling is the sole feedstock source, `04 §4e/§5e`); MWA concentrates on named uniques/elites, dungeon clears, and faction dailies, not trash mobs (`04 §5a` source ranking); dyad drops cap at RARE structures (superior structures stay race-tier + GL only per `04 §3b`; finished dyads never drop); infusion fodder keeps its all-grades spread (`04 §4d`); the classic v31 drop layer stays untouched |
| R14 | Overlevel drop decay adopted: drop rates decay toward zero as the player overlevels the content, keyed on EFFECTIVE level (a level-synced vet earns full rates per `03 §3b-i` no-rate-disparity rule; the decay pushes capped players into sync instead of killing the vet-return loop). Applies to the reforged material layer and gold. Implementation is server-side (no data hook exists), Mystel Proxy handoff per R9 |
| R15 | Feedstock is FLATTENED to a single untiered item (the framework already treats it as one commodity, and `08 §3` locks "MWA + feedstock same across all patches"). Grade (and optionally content-tier) scales dismantle QUANTITY, never item identity; enchant-side throttling comes from consumption scaling (`04 §2c`). Chase-tier differentiation, if ever needed, arrives as a separate named material (capstone-alkahest precedent, framework `99 #04`), never as feedstock tiers |

## 2. Vector roles (the design contract)

| Vector | Role | Framework |
|---|---|---|
| Story quests | High XP pacing, story progression, minimal power | `02 §3a` Lane A baseline |
| Zone quests | Minimal XP (25% or less of story per-quest, R10), more gold, small power items, early-prog tokens | `02 §2` zone-quest XP note + R1/R10 |
| Repeatables | Level-capped, XP under the R10 cap, resources + gold + tokens, zone-band economy | `02 §7`, `03 §3b-i`, R4/R10 |
| Dailies | NPC-given faction daily pool, zero/near-zero XP, thin direct rewards, reputation + tokens | `03 §3d`, R3/R6/R10 |
| Reputation | Grade-gated progressive store access; economy/cosmetic/utility goods, recipes; no BoP power | `03 §3d`, `03 §3c`, R6 |
| Instanced PvE | Per-content token + token shop; exclusive cosmetics + materials | invariant #9, `03 §3a/3b-iii`, R2/R3 |
| Exploration | One-time discovery highs + recurring ambient chest loop + completionist meta | `02 §2` exploration note, `03 §3b-i`, R8 |
| Region challenge | Community-progression gate to the next region, once per season | `11-region-progression.md`, R5 |
| Content drops (mob loot) | Classic v31 baseline + reforged material layer (fodder, MWA on elites, rare structures, tokens); guarded by effective-level decay | `04 §4d/§5a`, R13/R14/R15 |

## 3. Work items

IDs: RV-nn. Legend: PROBE-n (section 6), DSLR (dsl-request to file at item start), MCPR (mcp-request), MP (Mystel Proxy handoff), FW (framework repo authoring), D §4.x (dossier subsection with the mechanism facts).

### A. Token spine

- **RV-01 Early-progression token item.** Allocate item id (find_free_ids), author ItemTemplate on the currency-token archetype (D §4.2): `boundType=Loot`, `tradable=false`, NO_COMBAT, high maxStack; name/tooltip strings both legs. Gate: item exists, drops, stacks, cannot trade.
- **RV-02 Early-prog vendor at Tower Base.** A PHYSICAL villager NPC (R11; this is the project's first end-to-end authored NPC token shop, canon baseline: NPC 59,1955 "Major Milestone" MedalStore, D §4.2) carrying a Merchant/MedalStore menu whose BuyList tab is item-priced in RV-01 (`NeedMedalItemId`, D §4.2) plus matching ItemMedalExchange rows. Phase-1 catalog per `03 §3b-i`, sized by the reward-parity rule: enchant material bundles, uncommon crystals, consumables, a first cosmetic. Leveling-scroll conversion deferred (needs the level-sync era). Gate: purchase works live at correct prices.
- **RV-03 Token threading.** Add RV-01 payouts to: zone quest compensations, repeatables (1341/1390/1334 band), daily pool quests (RV-11), Sorcha/Karasha clears (small), exploration caches (RV-20), treasure chests (RV-22). Tokens are granted as ordinary `Item` rows in QuestCompensation and as ECompensation drops; quest rewards cannot grant currencies directly (D §4.1). Gate: every vector demonstrably pays tokens in a live pass.
- **RV-04 Sorcha dungeon token + Karasha dungeon token.** Two per-content token items (R2) + boss ECompensation drops at base rate (uncapped by design, `03 §4`; there is no data-level completion-reward mechanism in dungeons, D §4.4). Gate: tokens drop per clear.
- **RV-05 Dungeon token shops.** All NPC-attached per R11. Sorcha's shop rides on the Sorcha NPC (RV-14). The Karasha shop needs a design call inside this item: which NPC model and where, chosen from lore (a survivor of the 1316 chain, a garrison quartermaster near the dungeon entrance, or a new placement at Tower Base); document the choice in this folder. Also converts the existing Kugai's Crest MEDAL_USEABLE right-click shop (patch 002) to an NPC vendor, reusing its ItemMedalExchange rows. Catalogs: dungeon-exclusive cosmetics + tradeable materials only, per `03 §3c`. Gate: every token catalog purchasable live at a physical NPC; no MEDAL_USEABLE shops remain in IoD.

### B. Story / zone / repeatable tuning

- **RV-06 Story reward audit.** Verify the restored v31 story spine matches its role (high XP, transitional gear) AND assert self-sufficiency: the spine alone must reach level 10 (validated live in patch 001; the assertion protects it against future reward changes). Audit-only, changes only on contract violations. Gate: audit note in this folder including the level-10 assertion.
- **RV-07 Zone quest XP + reward pass.** Apply R10: audit every IoD zone quest's current (v31-restored) completion XP against its bracket's story quests; reduce any above the 25% cap _(strawman ratio; framework `99 #02` tuning entry)_. Compensate the removed XP value with non-XP rewards per `03 §3b-i` parity: gold up modestly, RV-01 tokens (RV-03), small power items. Every changed v31 value is divergence-logged (category: policy, R10). Gate: regression diff shows exactly the intended compensation deltas; no zone quest exceeds the cap.
- **RV-08 Repeatable pass.** Keep v31 level caps (R4; encoded as `최소레벨`/`최대레벨`, e.g. quest 1341 = 8 to 12, D §4.1). Apply the R10 XP cap; add token + resource payouts sized to the zone economy; one repeatable may pay treasure-hunt keys (RV-22). Gate: live re-accept loop works, caps hold.

### C. Reputation + dailies (one system; spec is `03 §3d`, mechanisms D §4.3)

- **RV-09 Faction bring-up.** After PROBE-1/2: repurpose a dormant faction id (610-617 have empty RealmLists in v92), rename via string sheets to an IoD identity, set RealmList to the IoD realm(s), AppearCondition = level + intro-quest gate, tune maxPoint/weekly caps to classic pacing (D §4.3; leveling-band numbers are open in framework `99 #03-currencies`). Gate: faction visible in the client reputation UI at the right moment.
- **RV-10 Intro chain.** Short quest chain gating the daily pool (classic pattern: v31 quest 60118 shape); candidate anchor: the Berlon crafting hub. Gate: completing the chain opens the pool.
- **RV-11 Daily pool.** New `DailyQuest` ReputationQuest pool: giveCount by grade, 07:00 reset, weighted variety (Hunt / Collect / Deliver / ObjectAction bodies with Branch variants, classic shapes; concrete v31 examples in D §4.3). Rewards THIN per classic: gold + reputationExp + reputationPoint, plus a small RV-01 bundle (Reforged addition; divergence-logged); zero or near-zero XP (R10, classic-faithful: v31 reputation dailies granted no XP at all). Includes the Sorcha daily and a Karasha daily. Gate: pool rotates at reset on dev, caps respected.
- **RV-12 PointStore + grade catalog.** Reputation vendor at Tower Base (or revive the dormant 13,5005/5006 PointStore wiring, D §4.3): PointStore menu + ReputationItem catalog with per-item grade gating: consumables and crystals early, crafting recipes and materials mid, cosmetics and a mount high. No BoP power (`03 §3c`). Gate: per-grade unlock proves out live.

### D. Instanced content

- **RV-13 Sorcha re-entry (R3).** DungeonData_9037: add a `completeQuest 1346` entry condition alongside the existing gate (dungeon 9036 already ships the progressQuest-OR-completeQuest pattern, D §4.4); rework portal WorkObject 134 to ungated, because a WorkObject quest window only expresses an ACTIVE task bracket, never completion (D §4.4/§4.6); keep the patch-002 party rules. Gate: a character with 1346 complete re-enters freely, a fresh character still enters via the quest path.
- **RV-14 Sorcha promotion.** Sorcha NPC spawned permanently in Tower Base gated by `appearQuestId=1346` (server-side only, no client leg needed, D §4.6), carrying her token shop directly (R11) and dialog, with her guard NPCs spawned beside her (same appear gate; cosmetic escort, template picks from the 9037 cast). Gate: Sorcha and guards appear only after first completion; shop purchasable at the NPC.
- **RV-15 Karasha HM unlock quest.** On completing 1316, auto-offer the HM follow-up (`연결퀘스트` successor or NPC-accept with prereq 1316, D §4.1), scoped as an optional zone quest; it gates HM entry (RV-30 epic) and carries the HM reward multiplier on the shared token (R2). Gate: quest offers exactly once, at the right moment, to all classes (audit_class_gates exit 0).

### E. Exploration (R8; mechanisms D §4.6)

- **RV-16 Landmark layer.** Restore trigger territories 1300199-1300204 (`achieveConditionId="4209"` fence polygons in TerritoryData_13) so the dangling IoD achievements 1425-1431 (incl. the found-all-six meta 1431) fire again; sync client AchievementList/StrSheet_Achievement. Deps: PROBE-3, MCPR-1 (raw XML until delivered). Gate: one achievement fires live.
- **RV-17 Cache generator.** New dc-restore-family tool (gen_cache_quests) stamping per cache: `questStart` trigger territory, one-time micro-quest (ObjectAction task + virtual `9999,9999` turn-in carrying the reward flag, cancellable; the exact canon-safe quest shape is D §4.6), WorkObject chest template + placement, `Work type="item"` chest payout, compensation row (tokens/XP/gold), strings, StrSheet_WorkObjectLoc waypoint. Deps: PROBE-4. Gate: one end-to-end cache proven live before batch generation.
- **RV-18 WorkObjectLoc registry step.** Extend the client-registry leg (gen_npcloc/gen_collectionloc family) to author StrSheet_WorkObjectLoc waypoints for cache quests; check migrate sync-config coverage for the family (extend or document as tool-managed). Gate: journal link resolves to a map marker on the chest.
- **RV-20 Cache placement wave.** 8 to 12 curated caches across the five IoD zones (positions chosen editorially). Reward: meaningful one-time payouts (tokens + materials + occasional cosmetic). Quest-count capacity is a non-issue (D §4.1: ~2,710 corpus quests in a ~1,000,000-id space); the scarce resource is the player's journal (D §4.6). Gate: live sweep opens every cache once per character and never twice.
- **RV-21 Treasure-map meta-quest (optional).** One "find all the caches" meta reward, pending PROBE-5. Gate: pays once after all caches.
- **RV-22 Treasure-hunt layer.** Key item (rare drop from IoD mobs/gathering/repeatables) + `keyItemId` chest WorkObject placed with `type="random"` candidates and respawn (canon precedents and the dormant vanilla chest template are D §4.6). Economy throttled by key drop rate. Gate: key-and-chest loop live, drop rate tuned against the reward-parity rule.

### F. Guardian Legion / region challenge

- **RV-23 (FW) Author the region-unlock challenge into the framework. DONE 2026-07-26.** Authored as framework doc `11-region-progression.md` (four structural calls user-confirmed: own doc; natural starvation while locked, no hard level cap; challenge persists as repeatable token content after unlock; server-first prestige for the completing group), with propagation to 01/02/03/08/10, README, CLAUDE.md, and 99. The same round shipped `03 §3d` and the expanded early-prog token source list (`03 §3b-i`, `02 §5`). RV-24 is unblocked.
- **RV-25 Vardung, the IoD wandering merchant (R12; mechanisms D §4.8).** Revive the dangling v92 wiring as a gold-priced randomized merchant: author NpcData_13 template 1271 (villager, BlackMarketer, invincible, 30-min lifeTime) and territory 1300270 with `RandomSpawn` candidate points at editorially chosen spots across the IoD layers; keep or extend WorldSpawn 10050 (cadence, weighted spots, guard-scope arrival announcements); replace the coin shop with a new gold-priced BuyMenu (`resetType=instanceNpc`, probability menu variants, account limits) bound via VillagerMenu `type="BuyMenu"`; reuse the existing "Vardung" and "Island of Dawn Mystery Market" strings; client legs per D §4.8. Catalog: randomized consumables/dyes/cosmetics at varied prices, tradeable power commodities (fodder, dust, basic materials) at a premium over broker norms with account limits (the `07 §4b` guardrail, ruled Option A 2026-07-26), plus one rare high-priced cosmetic sink item. Deps: PROBE-7/8, DSLR (BuyMenuData, WorldSpawnData, StrSheet_BuyMenu coverage). Gate: merchant appears on schedule at varied spots, announces, sells a rerolled gold catalog per appearance, despawns after 30 minutes.

- **RV-24 IoD challenge design brief.** Per `11 §2/§8`: the level-10 gate content (candidate vehicle: an authored FieldEvent, GL-style shared-progress group event, or a group boss; FieldEvent capabilities and limits are D §4.5), the closed gate (Pegasus platform), and the prepared unlock patch for the ops flip. First release ships the gate closed + the challenge; the flip is an ops runbook item (`framework 99 #11`). Gate: design brief approved; content items spun out afterwards.

### G. Content drops (R13/R14/R15; mechanisms D §4.9)

- **RV-26 Loot table correction pass (R13).** Audit the patch-002 merged IoD table (specs 001/20 + 002/17): remove all direct feedstock drops; move MWA off trash mobs onto named uniques/elites, dungeon clears, and the faction dailies; cap dyad drops at rare structures (remove any superior structures or finished dyads); keep the infusion-fodder grade spread and the entire classic v31 layer byte-untouched. Document the per-drop-class framework mapping in the spec header. Gate: regression diff shows exactly the intended ECompensation deltas; classic layer proven unchanged.
- **RV-27 Overlevel drop decay (R14).** Content-side deliverables only (implementation is server code): PROBE-9 confirms no data-side hook exists; author the decay contract for the Mystel Proxy handoff (which drop classes decay: the reforged material layer + gold, classic vendor-trash optional; effective-level keying with the level-sync dependency stated; a strawman curve: full rate through the bracket, decaying to zero within a few levels past it); ensure the loot specs keep the classic layer and the reforged layer cleanly separable so a global rule can target one and not the other. Gate: handoff doc accepted by Mystel Proxy; decay live-validated once shipped (full rate in-bracket, zero when far overleveled, full rate again when synced).
- **RV-28 Feedstock flattening (R15).** Research first: how v92 enchant data encodes per-tier feedstock requirements (which family, how gear references it): this is the one genuine unknown. Then: pick the surviving feedstock item id, repoint enchant tables across ALL gear tiers, repoint dismantle outputs to grade-scaled quantities of the single item, retire tier items from every loot/shop/reward reference (the current IoD table drops "Tier 1 Feedstock" 94101), fix strings/tooltips. This diverges from the v92 ITEM system (not from v31 content): record it as a systems divergence in the spec header. Gate: enchanting works at a leveling tier and an endgame tier with the single item; zero dangling tier-item references corpus-wide.

## 4. Mechanism dossier (canonical-data findings, 2026-07-26 research wave)

Facts below were established by reading the v92/v31 server datasheets, both client DCs, and the domain KB. Each subsection lists the reference docs, the established facts (with ids), and the gaps. Trust these over intuition; re-verify only where marked unproven.

### 4.1 Quest system

Docs: domain KB `entities/quest-system.md`, `entities/quest-task-reference.md`; framework `02`, `03`.

Established:
- Repeatability: header `반복퀘스트` = `반복` means unlimited immediate re-accept (36 quests; IoD 1341 is one). `반복횟수` (finite repeat count) is empty in ALL 2,710 quest files: treat as unusable.
- **No per-quest daily flag exists.** Daily cadence lives only in: `DailyQuest.xml` faction pools (resetHour=7, account-wide limitAccomplishCount, per-grade giveCount), `DailyPlayGuideQuest.xml` (Vanguard band, rejected by decision), `EventMatching.xml` (rejected by decision, see §4.7).
- Level gates: `수행조건/최소레벨` + `최대레벨` (777 quests use a max; 1341 = 8..12); level-capped repeatables are native.
- Accept triggers (`발생조건`): `NPC대화` (NPC dialog), `즉시수주` (auto-accept), `아이템사용` (item use, 143 quests), `테리토리진입` (enter territory `zoneId,territoryId`, 26 quests), `던전입장` (dungeon entry, 1 quest).
- Prerequisites: `선행퀘스트` pairs default OR, `선행퀘스트논리식` switches to AND; `평판` = `factionId, minGrade` reputation prereq (166 quests); `진행퀘스트` requires another quest active; sentinel prereq `99,99` = soft-disabled.
- Tasks: 34 types. Relevant: `방문Task` (visit NPC), `사냥Task` (hunt), MoveToPC (ENTER a territory region), Collect (gather via `콜렉션Id`), ObjectAction (`오브젝트동작Task`, interact with a WorkObject; 135 tasks in 89 quests), UseItem/Condition, Branch, `반복Task` (infinite loop inside a one-time quest).
- Rewards (QuestCompensationData_{hz}, keyed by GlobalId): fixed `exp`/`gold`/`reputationExp`/`reputationPoint`/`extendInven` + `Item` rows; `itemBag` modes allpay / class (internal class names) / race / choice. GlobalId = group*100 + index (index 0..99); corpus 2,710 quests; id space ~1,000,000.
- Successor offering: `연결퀘스트` auto-offers a follow-up on completion (`1,1` = none).

Gaps / unproven / not supported:
- No daily/weekly reset on a plain quest; no finite repeat counts; no level-scaled or probabilistic rewards; no token/currency grants (tokens must be items); no choice+class combined bag; allowlist-only class/race gates; no hidden/journal-invisible quest category (auto-granted quests always popup + journal); linear dialogs (branching only via Branch tasks).
- The per-character accepted-quest journal cap is a client/server constant of unverified value: live-check before shipping many auto-granted quests.

### 4.2 Shops, tokens, item-currency

Docs: domain KB `entities/merchant-system.md`, `entities/villager-service-system.md`; framework `03`.

Established:
- BuyList tabs are single-currency: gold by default, or `NeedMedalItemId="<itemId>"` for item-priced (392 of 597 v92 BuyLists are item-priced). `ItemMedalExchange.xml` rows validate each (item, price, medal) transaction and must match the BuyList `priceRevision`.
- `BuyMenuData.xml` (rotating shops) supports `resetType=day`, tab `probability`, and `limitType`/`limitCount`, but the only limitType ever used is `account`.
- NPC binding: `VillagerData/VillagerMenu.xml` `<Villager id="hz,tpl">` with multiple `<Menu type=...>` children (Merchant, MedalStore, BuyMenu, PointStore...). Menus are gated by `<Param>` types incl. `questCompleted` (12 vanilla uses) and `questProgress` (33), multiple Params AND. Vanilla uses quest Params only on Teleport menus: shop-menu use is structurally identical but unproven (PROBE-6).
- Token archetypes: currency token = item 72 "Challenge Receipt" (`combatItemType=NO_COMBAT`, `tradable=false`, maxStack 1000); right-click shop opener = item 95216 "Kugai's Crest" (`MEDAL_USEABLE`, `itemUseCount=1`). Bind-on-pickup = `boundType=Loot` + `tradable=false`.
- Kugai's Crest already drops in patch-002 IoD loot and has 23 ItemMedalExchange rows: the working in-repo example of an item-priced shop. It is currently a MEDAL_USEABLE right-click shop, which R11 rejects: RV-05 rebinds it to a physical NPC. NPC-attached token shops are canon-proven (NPC 59,1955 "Major Milestone": `MedalStore` menu 280, BuyList 2801, `NeedMedalItemId=72`) but not yet authored from scratch by this project.

Gaps / not supported: no per-item quest/level/class gating inside a shop (granularity is the Menu, or the reputation grade per §4.3); no purchase limits on standard BuyLists; no mixed gold+token pricing; no dynamic pricing; no `reputation` Param on menus; no item-possession gate on menus.

### 4.3 Reputation and dailies (the classic architecture)

Docs: domain KB `entities/reputation-system.md`; framework `03 §3d` (the adopted spec); era evidence §4.7.

Established (v92 data):
- `ReputationSystem.xml`: 17 factions (NPCGuild 601-617, 901, 903), shared 9-grade ladder, `startGrade`, `maxPoint`, weekly `gainPointLimit` + reset day, kill-based `TargetList`, `AppearCondition` (RequiredLevel, Quest, Region, UnionMember).
- `DailyQuest.xml`: root `limitAccomplishCount` + `resetHour="7"`; per-faction `ReputationQuest` pools with per-grade `<Quest grade giveCount id="questId,weight;...">`.
- `ReputationItem.xml`: per-item `grade` (min reputation grade) + `reputationPoint` price: native per-item progressive store unlock. Store side: `PointStore` VillagerMenu type + BuyList `NeedPointNpcGuildId`.
- IoD carries dormant v92-era wiring: villagers 13,5005 and 13,5006 hold PointStore menus for faction 609 (BuyLists 6091-6098): part of the shops-diff KEEP-INERT layer, reusable for RV-12.
- Dormant faction ids 610-617 have empty RealmLists: the low-risk repurpose targets (new faction ids are unproven server-side).
- Classic pacing reference (v31): dailies pay gold + repExp 600-800 + points 20-30, no XP, no items; grade thresholds 9000-25000 repExp (2 to 4 weeks per band); store prices 75-8300 points; maxPoint 3000-9000 forces spending. Daily giver villagers are dedicated town NPCs; one intro chain gates each faction's pool.
- Classic daily quest bodies to imitate: v31 60101 (2x ObjectAction + Visit), 60301 (Branch into Hunt then Visit), 60501 (Branch 50/50 into DeliverItem then Visit).

Gaps / unproven: a NEW ReputationQuest pool on v92 (PROBE-2); renamed dormant faction acceptance (PROBE-1); `RequiredReputation` as a faction unlock condition is commented out in all vanilla data (untested); no reputation gating of menu VISIBILITY (grades gate purchases, not the menu button).

### 4.4 Dungeons, entry gating, difficulty variants

Docs: domain KB `entities/dungeon-system.md`, `entities/topology-system.md`, `entities/zone-hierarchy-system.md`; project artifact `classic-restoration/iod/data/padding-sorcha-dungeon-investigation.md`.

Established:
- DungeonData_{continent} conditions (ANDed; multiple `progressQuest` rows are OR): `levelOver`, `party`/`solo` (mode flags; `notSolo` is the real solo-block), `maxMemberCount`, `progressQuest` (+taskId), `completeQuest`, `minItemLevel`, `raid`, `flag`. Root attrs `enterLimitCount`/`coolTime` exist, but the reset clock is server code, not data. Omitting them = unlimited entry (9036 has neither).
- **9036 already ships the re-entry pattern RV-13 needs:** `progressQuest 1316 taskId 3` OR `completeQuest 1316`.
- `RestoreTargetQuest` restores an IN-PROGRESS quest to the dungeon task on re-entry; it can never re-grant a completed quest.
- WorkObject portals: quest gating is `isForQuestId` + `firstTaskId`/`lastTaskId`, an ACTIVE-task window only; no completion-based gate exists; `keyItemId` is the questless alternative; `partyCantWork` blocks grouped use. The Sorcha portal 134 is currently windowed on 1346 and goes inert after completion.
- There is NO reward-granting element in dungeon event scripts. Per-clear reward options: boss ECompensation drops; quest rewards; a `workObjectSpawn`-on-`complete` chest with `Work type="item"` + `extendPartyMember` (end-of-run chest pattern).
- Hard modes are separate continent + HZ pairs sharing one map: Abscess trio 9511/9711/9811 = HZ 511/711/811, same `startPos`, same area `RNW_DarkCave_P`, divergent DungeonData conditions/scripts, NpcData stats, ECompensation. Modern id convention: continent = 9000 + HZ. Proposed for Karasha HM: **9536 / HZ 536** (verified free).
- Topology binding lives ONLY in `AreaList.xml` (continent -> area name -> tiles); cooked geometry is keyed by area name, never continent id; two continents sharing tiles is proven (9037 runs on continent 13's `ATW_Death_P`). The "topology cooking gap" applies only to NEW geometry; 9036's map `ATW_A_SD_P` is already cooked, so a clone has zero topology risk.
- Server files per variant: ContinentData, HuntingZoneAreaList, AreaList, AreaData_{cont}_{area}, DungeonData_{cont}, DungeonConstraint, DungeonMatching, per-HZ NpcData/TerritoryData/AIData/NpcSkillData/etc., StrSheet_Dungeon, StrSheet_Region, NewWorldMapData section, TeleportData. Client mirrors ~10 families (ContinentData, AreaList, HuntingZoneAreaList, Area, Dungeon, DungeonMatching, NewWorldMapData, StrSheet_Dungeon/_Region, TeleportData); MapDefineData can reuse an existing mapId.
- DSL coverage holes (hand edits + dsl-requests): AreaList, HuntingZoneAreaList, DungeonConstraint, DungeonMatching, StrSheet_Dungeon, TeleportData, ShieldTerritory. Sync-config holes client-side: ContinentData, AreaList, HZAL, Dungeon, DungeonMatching, StrSheet_Dungeon, TeleportData.

Gaps / unproven: creating a brand-new continent id has never been done in this project (hence RV-30 probe-first); which client families are load-bearing for a server-known continent is unknown; camp/resurrection registration (`campId` on the Area section) location unresolved; whether DSL can create new per-HZ shard files vs file-copy is unproven.

### 4.5 Field events (Guardian Legion class) 

Docs: domain KB `entities/field-event-system.md`, `entities/dark-rift-system.md`.

Established: GL fully exists in v92: 16 events in `FieldData_{continent}.xml` scheduled by `FieldEvent.xml` rotations. Capabilities: entry conditions, timed clear conditions, shared progress bar with milestone triggers, wave spawns, player-count difficulty scaling (`AutoEventBalance`), contribution scoring (`EventPoint` per class), level-bracketed rewards (`FieldEventReward`, `FieldEventClearReward`), `worldAnnounce`, cross-channel shared progress. Dark Rift is a second timetable-driven wave-defense system.

Gaps: no player-triggered or one-shot event starts (rotation/timetable only); no persistent world state (progress resets per event instance): a permanent "region unlocked" outcome cannot be recorded by the event (hence the `11 §8` ops-flip ladder); rewards are per-participant, never zone-wide state.

### 4.6 Exploration, achievements, conditional visibility

Docs: domain KB `entities/work-object-system.md`, `entities/quest-system.md` (NPC appear/hide section); MCPR-1 applies (raw XML needed today).

Established:
- Achievements: `AchievementList.xml` (server) + client `AchievementList`/`StrSheet_Achievement` (both legs required). Condition `templateId=4209` fires on entering a territory carrying `<Attribute achieveConditionId="4209"/>`. **IoD precedent: achievements 1425-1431 (Mathar Spire, crashed courier ship, obelisk, graveyard, +meta) exist but dangle: their trigger territories 1300199-1300204 were deleted from TerritoryData_13.** Rewards: TitleReward (titles exist ONLY via achievements), ItemReward, MoneyReward, AbilityReward, inventory expansion.
- AreaData sections carry NO reward/XP fields; classic discovery XP is hardcoded server behavior. The data-driven substitutes: 4209 achievements and MoveToPC/`테리토리진입` quests.
- NPC visibility: NpcData `appearQuestId`+`appearQuestTaskId` / `hideQuestId`+`hideQuestTaskId` (1,104 meaningful templates). **Server-side only: the client DC has no such fields; the server just withholds the spawn.** Used in canon for staged scenery, discovery props, quest-window camps.
- WorkObject windows (`isForQuestId`, `firstTaskId`, `lastTaskId`) ARE mirrored into the client DC (required attributes), so chest work needs both legs. `keyItemId`/`keyItemAmount` gates interaction questlessly. Placements support `type="random"` candidate positions and world-scoped respawn (`respawnTimeMin/Max`; 0 = one-shot per world).
- The canon-safe cache-quest shape (every link corpus-verified): `questStart` trigger territory (silent volume; BHS desc precedent "entry territory for the folktale quest") -> auto-granted one-time quest -> WorkObject window opens -> ObjectAction task on interaction -> **trailing `방문Task` to virtual NPC `9999,9999`** (UI turn-in, 512 canon quests) carrying the reward flag `보상=1` -> QuestCompensation pays. ObjectAction is NEVER terminal or reward-flagged in canon (0 of 135): do not make it the paying task. One-time latch = the quest's `1회성` completion record.
- Canon discovery precedents: "Dusty Tome"/"Old Book" walk-up quests (018353/118301); Velika Banquet lucky box (key item -> coins, questless, template 50502); "더미 보물찾기" treasure-hunt prototype (template 202001, key + one-shot box + NPC spawn); dormant "보물상자!" chest template 10 (drops item 9093, 180s enableTime, placed nowhere: adoptable asset).
- Client marker registry for object objectives: `StrSheet_WorkObjectLoc` (sibling of StrSheet_NpcLoc/CollectionLoc): cache quests can carry a real map waypoint (the journal-breadcrumb ruling R8).
- Gathering bonus drops are native and tunable: `CollectionData/CollectionGiftTable.xml` bags already roll rare extras for IoD collections 1/101/301.

Gaps / not supported: no per-character cooldown or "opened by me" state on WorkObjects (world-scoped only; one-time-per-character exists ONLY via the quest latch); visibility can key ONLY on quest progress (never achievements, reputation, items owned, or level); one-time and repeatable are mutually exclusive at the quest level; journal noise is unavoidable (design uses it as the breadcrumb); whether a windowed chest is invisible vs visible-but-inert outside its window is undecidable from data (PROBE-4).

### 4.7 Era archaeology (why the reputation/daily decisions look the way they do)

Sources: `v31_datasheet`, `old_client_dc` (v17.11), `client_dc_v31`, datasheet-v31 MCP.

- Reputation was BORN at v17.11 as an endgame-only system (6 factions, 86 dailies all level 58-60, placeholder store rows) and EXPANDED through v31 (12 factions, 367 dailies, 4x store catalog). Nothing was removed between eras.
- **No era ever put reputation, dailies, or repeatables on Island of Dawn or any 1-20 zone.** Early-zone repeatable content in both eras was the ~125 generic `반복` grind quests in mainland hubs. The IoD faction is therefore authored Reforged content following the classic architecture (the `03 §3d` zone-band deviation).
- Faction 609 is the Vanguard Initiative meta-faction: in v31 it has NO DailyQuest pool because `EventMatching.xml` (fully present in v31, bound to `npcGuildId="609"`, beginLevel 13) feeds it. The v92 IoD PointStore wiring of 609 is the level-65 IoD rework reusing that meta-faction.
- EventMatching / Vanguard Requests were rejected by decision (R3, framework `03 §2` note): menu-driven accept, auto-complete, reward-from-panel, teleport-to-objective; historically the system that displaced the classic repeatables when extended to levels 1-59. Do not route any Reforged content through it.

### 4.8 Mystery merchant (wandering-merchant system)

Docs: domain KB `entities/world-spawn-system.md`, `entities/merchant-system.md`, `entities/villager-service-system.md`; framework `07 §4` (design home: random-spawn, random-catalog luxury gold sink). Player-facing reference: the retail feature shipped patch 85 (2019): occasional unannounced appearances at a pool of spots, ~30-minute stays, random limited stock, account purchase limits, arrival announcements.

Established (v92 data; the system is FULLY data-driven except the scheduler engine itself):
- NPCs: template 1271 "wandering merchant" replicated per field HZ (~40 zones; villager, race BlackMarketer, invincible, `lifeTime=1800000` = 30 min, despawn-warning system message); 1276 "city secret merchant" (hub cities, also the gold-priced coin seller); 1278 city-territory wanderer.
- **IoD's merchant exists and dangles:** StrSheet_Creature HZ 13 names template 1271 "Vardung, Island of Dawn Mystery Merchant"; VillagerMenu binds `13,1271` to `BuyMenuMedal` menu 10050; client StrSheet_BuyMenu string 100500 = "Island of Dawn Mystery Market"; WorldSpawnData entry 10050 schedules `hz 13, territory 1300270`. But the v92 IoD rework deleted template 1271 from NpcData_13 AND territory 1300270 from TerritoryData_13: NPC + territory must be authored (the mystery merchant postdates v31, so there is no classic restore source; this is adopted v92-era wiring, not restoration).
- Spawn scheduling: `WorldSpawnData.xml`: `WorldSpawn` -> `SpawnTerritoryGroup` (weight, `nextTime` +/- `nextRandomTime`) -> `SpawnTerritory` (hz, territoryId, lifeTime, `notifySpawn/notifyDespawn` scope guard/world, notify template). All listed territories start despawned; the scheduler cycles them (`randomOrder` weighted). Data controls positions, zones, cadence, stay length, and announcement scope. Territory pattern: merchant Npc with `randomPos`, `spawnCount=1`, `persistentChannelSpawn`, multiple `RandomSpawn fixedPos` candidate points (one picked per appearance).
- Shop: `BuyMenuData.xml`: `BuyMenu(resetType none|day|instanceNpc)` -> `Menu(probability, [needMedalItemId])` -> `Item(buyPrice, count, limitType, limitCount)`. **A gold-priced, probability-rotated, per-spawn-resetting catalog is vanilla-proven** (BuyMenu 1019: gold + resetType=day + 10 menus at 0.1; BuyMenu 10004: gold + resetType=instanceNpc + account limits). `probability` rolls WHICH menu variant is live at reset; `instanceNpc` rerolls per NPC appearance. The retail coin economy (Mystery Market Coin 204069) sits at Menu level and is simply omitted for a gold variant. For the record, retail coin sources were: gold purchase at 10,000,000g from city NPC 1276 (account limit 3, per-appearance restock: the whale sink), Vanguard Request rewards and small Ghillieglade drops (both server-code side, no compensation-table rows), and a gacha coin chest (204070). R12 drops the coin because: `07 §4` defines our mystery merchant as a direct GOLD sink; the coin has no per-content identity (`03 §3a`); its earn stream was Vanguard (rejected, R3); and every coin role maps to a native mechanism (account limits + instanceNpc resets for throttling, spawn cadence + probability catalogs for scarcity, price bands + one expensive sink item for the whale sink).
- Client legs: BuyMenuData is a header-only client mirror (id, stringId, resetType); StrSheet_BuyMenu is CLIENT-ONLY (shop title + tab strings); plus the normal NpcData/TerritoryData/VillagerMenu/StrSheet_Creature syncs.

Gaps / unproven (PROBE-7/8): scheduler behavior with layered-HZ territories (13 vs 64/213/313/364) and guard-scope announcements there; `probability` semantics when menu weights do not sum to 1; whether account limits reset per instanceNpc appearance; whether `type="BuyMenu"` works on a world-spawned NPC exactly like the permanently-placed 10004 precedent; DSL apply coverage for BuyMenuData / WorldSpawnData and sync-config coverage for BuyMenuData / StrSheet_BuyMenu (none mapped today).
- Framework catalog rule (`07 §4b/§4d` inconsistency RESOLVED 2026-07-26, Option A): tradeable power commodities are allowed in the catalog at a premium over broker norms (strawman 1.5 to 2x) with account limits: the merchant is a scarcity-relief valve and gold sink, never a primary supplier. BoP power and power exclusives never appear; the headline chase item stays cosmetic.

### 4.9 Mob drop layer (the content-drop vector)

Docs: domain KB `entities/loot-system.md`; framework `04 §3b/§4d/§4e/§5a/§5e`, `08 §3`; project background: IoD tracker 2026-07-22 session (loot merge design).

Established:
- The current IoD table is a two-layer merge: spec `001/20` restores the FULL v31 ECompensation_13 natural table (43 mobs: gold, classic materials, paverunes, designs, First Expedition set on the named boss), and spec `002/17` unions the reforged layer on top (MWA, Tier 1 Feedstock 94101, crystal boxes, dyad structures, infusion gear boxes, Kugai's Crest 95216; reforged bag ids offset +100). Both economies coexist by design (user call, 2026-07-22).
- Framework verdicts per drop class (R13): infusion fodder all-grades everywhere = correct (`04 §4d` "the game shouldn't start only at the endgame"); direct feedstock drops = CONTRADICTION (`04 §4e/§5e`: feedstock is exclusively downstream of fodder dismantling; the fodder supply being the single limiter on infusion AND enchanting is load-bearing); MWA on trash = too broad (`04 §5a` ranks GL > dungeons > dailies > BAMs; trash is unlisted); superior structures = race-tier + GL only (`04 §3b`); finished dyads never drop (they exist only as structure conversions).
- ECompensation rows carry NO player-level-conditional terms: an overlevel drop-rate decay cannot be expressed in data and is a server-side feature (R14, Mystel Proxy). The decay must key on EFFECTIVE level or it violates the `03 §3b-i` same-rate rule for synced vets and kills the vet-return loop; until level sync ships, the decay alone is the anti-exploit story.
- v92 ships TIERED feedstock items (per gear band); the framework treats feedstock as a single commodity everywhere it appears, and `08 §3` locks enchant materials as patch-stable. R15 flattens to one item; the quantity axis (dismantle yield by grade, consumption by band per `04 §2c`) replaces tier gating as the throttle.

Gaps / unproven: how v92 enchant data references feedstock tiers per gear band (RV-28's first research step); whether any engine surface exists for level-conditional drops (PROBE-9 expected to confirm absence); the decay curve itself is tuning (framework `99 #07-economy`).

## 5. Epic: Karasha Hard Mode (R7; mechanisms D §4.4)

- **RV-30 Probe milestone (blocks the rest).** Boot a skeleton continent 9536 / HZ 536 on dev: ContinentData row, HuntingZoneAreaList + AreaList blocks cloned from 9036 (same area name `ATW_A_SD_P`), AreaData clone with renumbered nameIds, minimal DungeonData_9536; `/@enter_dungeon` probe; establish which client families are load-bearing. Deps: `server-load-diagnosis` skill on standby; DSLR for the §4.4 coverage holes; sync-config extension requests. Gate: server boots, character stands in 9536.
- **RV-31 Clone wave.** Per-HZ files 436 to 536 verbatim (territory ids renumbered 436xxxxx to 536xxxxx), DungeonData script clone with HZ rewrite and stale RestoreTargetQuest sweep. Gate: NM-identical dungeon playable end to end in 9536.
- **RV-32 Divergence wave.** The three divergence surfaces: NpcData_536 stat blocks (HM tuning; Sorcha lesson: population is the expressive lever, not flat HP), DungeonData_9536 conditions (entry via the RV-15 quest) + new mechanics, ECompensation_536 + clear rewards (shared Karasha token at HM rate, R2). Gate: `dungeon_audit.py --dungeons 9536` exit 0 + live group clear.
- **RV-33 Registration + client mirror.** DungeonConstraint, optional DungeonMatching, entrance portal/teleport, StrSheet_Dungeon/Region, worldmap section, client rows across the affected families, pack + deploy. Gate: full loop from unlock quest to HM clear to token spend, live.

## 6. Probes (front-load; each is a small dev-server experiment)

| # | Question | Blocks |
|---|---|---|
| PROBE-1 | Does a renamed dormant faction (610-617) with a new RealmList surface correctly in client UI and accept points? | RV-09..12 |
| PROBE-2 | Does a NEW DailyQuest ReputationQuest pool function on v92 (grant at 07:00 reset, giveCount, limitAccomplishCount)? | RV-11 |
| PROBE-3 | Do restored `achieveConditionId=4209` territories fire their achievements on our server + client build? | RV-16 |
| PROBE-4 | Chest WorkObject outside its quest window: invisible or visible-but-inert? (Client mirrors the window fields.) | RV-17/20 |
| PROBE-5 | Does one ObjectAction task accept multiple object targets? | RV-21 |
| PROBE-6 | Does a `questCompleted`/`questProgress` Param gate a Merchant/MedalStore menu (vanilla uses them only on Teleport menus)? | fallback for RV-12 if reputation grades prove insufficient |
| PROBE-7 | Does the WorldSpawnData scheduler handle IoD's layered HZs (spawns and guard-scope announcements on 13/64/213), and does a world-spawned NPC serve a `type="BuyMenu"` gold shop like a placed one? | RV-25 |
| PROBE-8 | BuyMenuData semantics: menu `probability` when weights do not sum to 1, and whether account purchase limits reset per `instanceNpc` appearance? | RV-25 catalog design |
| PROBE-9 | Confirm no data-side hook exists for player-level-conditional drop rates (expected: none; then the decay is a pure Mystel Proxy feature) | RV-27 |

Also live-check early: the per-character accepted-quest journal cap value (D §4.1 gap).

## 7. Standing dependencies and handoffs

- **MCPR-1 (filed 2026-07-26):** expose Achievement, WorkObject/WorkObjectTerritory, Treasure, CollectionBook, and AreaData/Section families: `docs/mcp-requests/2026-07-26-achievement-workobject-families.md`. Until delivered, those questions need raw-XML reads.
- **DSLR (file at item start):** the §4.4 DSL coverage holes for RV-30/33; DailyQuest / ReputationSystem / ReputationItem / AchievementList entity coverage for C and E items; BuyMenuData / WorldSpawnData / StrSheet_BuyMenu coverage for RV-25; sync-config additions (client Dungeon family, StrSheet_WorkObjectLoc, BuyMenuData header, StrSheet_BuyMenu if unmapped).
- **MP (Mystel Proxy):** persistent world flag for region unlock (`11 §8` successor); the overlevel drop-decay feature (RV-27 contract: effective-level keying, targeted drop classes); completed-quest persistence at scale (informational per R9); journal-cap tuning if the client constant needs raising.
- **FW:** none open. RV-23 and the framework instantiation notes shipped 2026-07-26 (framework commit 3a32bff).

## 8. Sequencing toward first release

1. **Wave 1, token spine + loot correction:** RV-01..05 + RV-06..08 + RV-26 (small specs, immediate player-visible value; every vector starts paying and the drop layer becomes framework-clean). RV-28's enchant-data research and the RV-27 handoff doc can start here too (no content dependency).
2. **Wave 2, reputation + dailies:** PROBE-1/2 then RV-09..12; Sorcha items RV-13/14 land here too (small, independent).
3. **Wave 3, exploration + replayability:** PROBE-3/4 then RV-16..22; PROBE-7/8 then RV-25.
4. **Wave 4, Karasha HM epic:** RV-15 + RV-30..33 (longest pole; the probe milestone can start as early as Wave 2 in parallel).
5. **Wave 5, region challenge:** RV-24 design brief per `11-region-progression.md`; content follows the framework doc.

Every wave ends with the standing project gates: full-patch migrate apply, dungeon_audit + audit_class_gates exit 0 where applicable, deploy, USER live validation, then the patch-close commit discipline. Nothing in this file is "done" on a clean apply alone.
