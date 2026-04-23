# Changelog

Covers all meaningful work across the reforged content project and correlated projects
(datasheetlang DSL, datasheet-domain, reforged-server ATP).
Newest entries first.

---

## 2026-04-23

### Content
- `01-reaper-weapons.yaml` migrated from `weapons` package to `equipment-item-standard` — spec reduced from 3 local definitions to 2, 20+ attributes removed from spec scope
- `06-brawler-weapons.yaml` migrated from `weapons` package to `equipment-item-standard`
- `packages/weapons/` removed; `datasheetlang.yml` `defaultImports` cleared — no specs depend on it
- `packages/equipment-item-standard` restructured: universal standard attrs added to `_EquipmentBase`; 8 tier intermediary bases introduced per slot; `linkPassivityCategoryId: 120300` added to `_WeaponBase`; `MidTierChainWeapon`, `HighTierChainWeapon`, `MidTierGauntletWeapon`, `HighTierGauntletWeapon` added as class-specific derivations
- Package and patch 001 READMEs updated to reflect new hierarchy and consumers

### Infrastructure
- datasheetlang: Fixed package-internal variable scope — definitions exported from a package no longer require consumers to re-import the variables used internally

### Blockers resolved
- `2026-04-23-package-variable-scope-not-resolved-at-export.md` — resolved ✅

---

## 2026-04-22

### Content
- Island of Dawn migration declared complete — all phases 0–4 done, in-game validated
- Patch 000 all 8 specs applied, synced, and validated in-game:
  - `00-iod-training-bomb.yaml` — item 5002 itemUseCount restored to unlimited
  - `01-iod-garrison-quest.yaml` — quest 1384 task chain redesigned for v92 compatibility
  - `02-iod-skill-quest-strings.yaml` — skill name strings corrected for 5 classes
  - `03-iod-skill-quest-conditions.yaml` — skill ID conditions corrected for 5 classes
  - `04-iod-garrison-dialog.yaml` — quest 1384 garrison dialog revamped
  - `05-iod-gathering-nodes.yaml` — pickSkillType fixes + territory id=1/5 restored
  - `06-iod-teleport-scroll-coordinates.yaml` — teleport scroll coordinates confirmed in-game ✅
  - `07-iod-teleport-scroll-strings.yaml` — item 133 name/tooltip restored from v31 ✅
- Client DC synced for all patch 000 entities (Collections, ItemData, SkillData, QuestDialog, StrSheet_Item)
- Server share updated with patch 000 changes

### Infrastructure
- datasheetlang: Fixed float precision expansion — `dsl apply` now caps floats to 8 decimal places (92fa465) ✅
- datasheetlang: Reverted server XSD attribute-order source generation (ab41f20) — one-time reformat diff expected on first sync per entity; subsequent syncs stable
- datasheetlang: Fixed ClientElementPreserver attribute equality check (e65b390)

### Blockers resolved
- `2026-04-22-float-precision.md` — resolved by 92fa465 ✅
- `2026-04-22-skilldata-sync-attribute-reorder.md` — resolved by reverting XSD attribute-order feature (ab41f20); one-time reformat on first sync is expected behavior

---

## 2026-04-21

### Content
- IoD Phase 4 validation complete: 65/65 quests, 72/72 reward items, all NPC templates confirmed zero-diff vs v31
- Zone 436 (Karascha's Lair) validated: 8 NPCs, correct loot (ECompensation), quest 1316 task chain intact
- Story groups 1 (18q) and 2 (7q IoD) confirmed; prologue zones 415/416 (8+8q) confirmed
- Patch 000 spec `06-iod-teleport-scroll-coordinates.yaml` applied — skill 60130101 correct on server + client
- Patch 000 spec `05-iod-gathering-nodes.yaml` applied — collection types and territory id=1/5 restored
- IoD zones 13 and 436 added to patch 001 zone scope
- CollectionData and SkillData entities added to migrate.py entity map
- Migrate tool upgraded: manifest-narrowed apply→sync with preflight `nul` file checks

### Infrastructure
- datasheetlang: Fixed `--from-manifest` narrowing for ZoneBased + IdSorted strategies (7d64e6a)
- datasheetlang: Fixed `--from-manifest` narrowing for Monolithic + SourceMapped (0a10f78)
- datasheetlang: Made `Create{Targeting,Area,Effect}EntryCommand` idempotent — eliminates empty placeholder appends on re-apply (fc6e3b0)
- datasheetlang: Mapped TeleportType string to typed enum across schema, commands, mapper (53b8850)
- datasheetlang: Fixed CRLF line endings and indentation preservation in `dsl apply` (e86a42d) — validated ✅
- datasheetlang: Fixed SkillData sync float normalization and preserve-unchanged verbatim (8db859c) — validated ✅
- datasheetlang: Fixed UTF-8 BOM preservation in `dsl apply` (5427ba1) — validated ✅
- datasheetlang: Fixed SkillData NPC shard oscillation via composite key (id+templateId) (29137ed) — validated ✅ (536/536 unchanged on second sync)

### Blockers resolved
- `2026-04-21-commonskills-apply-appends-empty-placeholder-elements.md` — resolved by fc6e3b0
- `2026-04-21-manifest-narrowing-broken-for-zonebased-and-idsorted.md` — resolved by 7d64e6a
- `2026-04-21-xml-writer-crlf-line-endings.md` — resolved by e86a42d ✅
- `2026-04-21-apply-indentation-normalization.md` — resolved by e86a42d ✅
- `2026-04-21-skilldata-sync-attribute-order-float-format.md` — float normalization resolved by 8db859c ✅; attribute ordering still open
- `2026-04-21-apply-strips-utf8-bom.md` — resolved by 5427ba1 ✅
- `2026-04-21-skilldata-sync-npc-non-unique-id-non-idempotent.md` — resolved by 29137ed ✅

---

## 2026-04-20

### Content
- Teleport scroll coordinates applied to server (skill 60130101, recallContinent=13)
- Malformed XML placeholders in UserSkillData_Common.xml cleaned up (two-step hand-fix)

### Infrastructure
- datasheetlang: Apply manifest (`--manifest-out` / `--from-manifest`) implemented — targeted client sync without broad shard rewrite (90a62d9)
- datasheetlang: Fixed class-filter regex swallowing `.xml` on base files (UserSkillData_Common.xml now matches class=Common) (5dc68a2)
- datasheetlang: Orphan deletion correctly gated behind `--filter`/`--segment` flags (b4a51bf)

---

## 2026-04-18

### Content
- Zone 436 (Karascha's Lair) added to migration scope
- 8 zone-partitioned files + 3 VillagerData conditions copied from v31 → v92
- DungeonData_9036.xml restored to v31 conditions (levelOver=9, progressQuest=1316)
- Client DC zone 436: NpcData-00212 and TerritoryData-00218 generated via DSL sync
- IoD migration documentation added: assessment, zones, quests, file-manifest, plan, progress

### Infrastructure
- datasheetlang: SkillData segmented sync added — XSD-driven class filter, orphan deletion, 536-shard coverage (6bce01f)
- datasheetlang: Effect-level Teleport (`recallPos`, `recallContinent`, `type`) added to commonSkills/npcSkills/userSkills (c5d7874, e5911f7)
- datasheetlang: Area resolution via Descendants — AreaList-wrapped Areas now correctly targeted (b52b2bf)
- datasheetlang: CategoryVariants update/delete now respects category target (8e17ee5)

---

## 2026-04-14 to 2026-04-17

### Content
- Island of Dawn full migration executed (phases 0–3):
  - Phase 0: v92 server + client DC repos reverted to clean state
  - Phase 1: 34 v31 zone files copied; 8 v92-only files emptied; CollectionTerritory patched
  - Phase 2: 65 .quest files, QuestDialog files, StrSheet_Quest (1009 strings), QuestGroupList merged
  - Phase 3: 245+ client DC quest shards copied; zone NpcData/TerritoryData generated via DSL sync

### Infrastructure
- datasheetlang: QuestDialog subdirectory path resolution fixed (e12908c)
- datasheetlang: Nested Collections partial-update and delete-by-id (8a8dec3)
- datasheetlang: AreaId composite value type; NpcId element type (08d6f20)
- datasheetlang: Multiple quest task fixes (visit, condition, journal, nextTask) across 8 DSL requests filed

---

## 2026-04-05 to 2026-04-06

### Content
- Dyad crystal system: 1182 crystals across 6 tiers, per-type passivity configs, fusion structures, zone loot integration
- Infusion box system: gear-infusion-boxes package, zone loot tables across all patch 001 zones
- Crystal system, dungeon tokens, zone loot overhaul with unified eCompensation model
- Dungeon token shop chain fixed: ItemMedalExchange → VillagerMenuItem → BuyMenuList → BuyList

---

## 2026-02-22 to 2026-02-26

### Content
- Flawless gear added to progression pipeline with dedicated ID package
- Masterwork system replaced with potential unlock scroll (63 items, 6 tiers, 1:1 enchant evolution)
- Starter 0 gear added; weapon/armor attributes standardized across all tiers
- Missing enchant rolls added: weapon crit factor, prone damage, chest prone damage reduction

---

## 2026-01-30 to 2026-02-10

### Content
- Gear infusion: passivities, items generated from CSV source data
- Evolution specs refactored with `$with/$params` — monolithic file split into per-set parameterized specs
- EquipmentInheritanceData config added
- Zone loot specs added across all patch 001 zones
- Patch migration tool (`migrate.py`) introduced — automates apply→sync pipeline per patch
- Spec paths updated to patch-aware structure (`specs/patches/{NNN}/`)
- Enchant tiers split: +12 cap grades 0–3, +15 cap mythic (grade 4)
- Frostfire gear upgrade path added
