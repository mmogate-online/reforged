# Enchant System Packages

The enchant system is built from four packages in a strict dependency chain. Each layer builds on the previous, and only the top two layers (`enchant-standard`, `enchant-categories`) are ever imported by specs directly.

```
enchant-passives          ← individual stat passivity templates (38 definitions)
      ↓ internal import
enchant-categories        ← groups passivities into roll pools per slot/role
      ↓ internal import          (19 category IDs + 19 category definitions)
enchant-standard          ← full enchant chain records + stat rates + IDs
      ↓ internal import          (38 variables + 21 definitions)
equipment-item-standard   ← item-level templates (enchantEnable + rareGrade + linkEnchantId)
                                 (14 variables + 14 definitions) — built, not yet used
```

Spec authors import from `enchant-standard` for the enchant chain, or from `enchant-categories` if they only need the category IDs.

---

## Layer 1: `enchant-passives`

Defines individual passivity stat templates — the atomic building blocks. Each definition sets the `type`, `method`, `condition`, and default strings for one stat bonus.

**Never import this directly.** It is an internal dependency of `enchant-categories`.

Pools defined:
- **Weapon DPS/Tank random** (8): enraged damage, back attack, all damage, cooldown reduction, most-aggro damage, attack speed, crit power, prone damage
- **Weapon Healer random** (3): MP recovery on skill, crit factor, healing performance
- **Chest random** (6): damage reduction variants + max HP
- **Gloves random** (5): attack speed, crit factor, power, endurance, healing performance
- **Boots random** (4): movement speed, endurance, MP regen, slow duration reduction
- **Fixed weapon DPS/Tank** (3): power (+7), monster damage (+8), all damage (+9-12)
- **Fixed weapon Healer** (3): MP recovery (+7), healing flat (+8), cooldown (+9-12)
- **Fixed armor** (3): endurance (+7), all damage (+8), max HP (+9)

---

## Layer 2: `enchant-categories`

Groups the passivity definitions into roll pool categories with actual values and passivity IDs. Each category definition contains an `enchantPassivityCategoryId` and its list of passivities.

**Import this** when you only need category IDs (e.g., to set `linkPassivityCategoryId` on items).

### Category ID Ranges

| Range | Purpose |
|-------|---------|
| `121001–121007` | Random pools (always active from enchant step 0) |
| `121011–121019` | Fixed bonus pools (unlock at specific enchant steps) |

### Random Pools (step 0, always active)

| Variable | ID | Slot / Roles |
|----------|----|-------------|
| `CATEGORY_WEAPON_DPS_TANK_RANDOM` | 121001 | Weapons — all DPS + tanks (shared pool) |
| `CATEGORY_WEAPON_HEALER_RANDOM` | 121002 | Weapons — Priest, Mystic |
| `CATEGORY_CHEST_RANDOM` | 121003 | Body armor — all classes |
| `CATEGORY_HAND_MAIL_RANDOM` | 121004 | Gloves — Lancer, Berserker, Gunner, Brawler |
| `CATEGORY_HAND_LEATHER_RANDOM` | 121005 | Gloves — Warrior, Slayer, Archer, Glaiver |
| `CATEGORY_HAND_ROBE_RANDOM` | 121006 | Gloves — Sorcerer, Priest, Mystic, Ninja |
| `CATEGORY_BOOTS_RANDOM` | 121007 | Feet — all classes |

> **Note:** Chest armor also has class-specific top-roll categories (122001–122013) from the `chest-toproll-categories` package. These override the generic `CATEGORY_CHEST_RANDOM` on specific items via `03-chest-toproll-items.yaml`.

### Fixed Bonus Pools (unlock at enchant steps)

| Variable | ID | Unlocks at | Slot |
|----------|----|-----------|------|
| `CATEGORY_WEAPON_DPS_TANK_FIXED_10` | 121011 | +10 | Weapons — DPS/Tank |
| `CATEGORY_WEAPON_DPS_TANK_FIXED_11` | 121012 | +11 | Weapons — DPS/Tank |
| `CATEGORY_WEAPON_DPS_TANK_FIXED_12` | 121013 | +12–15 | Weapons — DPS/Tank |
| `CATEGORY_WEAPON_HEALER_FIXED_10` | 121014 | +10 | Weapons — Healer |
| `CATEGORY_WEAPON_HEALER_FIXED_11` | 121015 | +11 | Weapons — Healer |
| `CATEGORY_WEAPON_HEALER_FIXED_12` | 121016 | +12–15 | Weapons — Healer |
| `CATEGORY_ARMOR_FIXED_7` | 121017 | +7 | All armor slots |
| `CATEGORY_ARMOR_FIXED_8` | 121018 | +8 | All armor slots |
| `CATEGORY_ARMOR_FIXED_9` | 121019 | +9 | All armor slots |

### Passivity ID Range

All passivities defined in this system use the `1510000+` range (with a few legacy IDs like `1320600` and `1410110`).

---

## Layer 3: `enchant-standard`

The practical entry point. Assembles per-tier, per-slot enchant chain records — each one specifies stat rates and links to its passivity categories.

**Import this** when building the enchant chain (`materialEnchants`, `enchants`) or syncing `linkEnchantId` onto items.

### Exported Variables

**Enchant chain IDs** (`950001–950027` range) — used as `linkEnchantId` on equipment items:

| Variable group | Tiers covered |
|---------------|--------------|
| `ENCHANT_HIGH_TIER_*` | Mythic-grade weapons and armor (7 variables) |
| `ENCHANT_MID_TIER_*` | Superior-grade weapons and armor (7 variables) |
| `ENCHANT_LOW_TIER_*` | Uncommon/Rare weapons and armor (7 variables) |

Slot suffixes match `equipment-item-ids`: `_DPS_WEAPON`, `_HEALER_WEAPON`, `_CHEST`, `_HAND_MAIL`, `_HAND_LEATHER`, `_HAND_ROBE`, `_BOOTS`.

**Stat rate multipliers** — controls base stat scaling per enchant step:

| Variable | Applied to |
|----------|-----------|
| `WEAPON_ATTACK_RATE`, `WEAPON_IMPACT_RATE` | Weapons (normal enchant range) |
| `ARMOR_DEFENCE_RATE`, `ARMOR_BALANCE_RATE` | Armor (normal enchant range) |
| `WEAPON_ATTACK_RATE_13/14/15`, etc. | High-enchant step overrides |

**Category IDs** — re-exports all 19 variables from `enchant-categories`.

### Exported Definitions

21 enchant record definitions, one per tier/slot combination: `HighTierWeaponDPSTank`, `HighTierWeaponHealer`, `HighTierChest`, `HighTierHandMail`, `HighTierHandLeather`, `HighTierHandRobe`, `HighTierBoots`, and `Mid`/`Low` equivalents.

### Current Consumers

| Spec | What it imports |
|------|----------------|
| `patches/001/00-enchant-system.yaml` | All enchant IDs + all tier/slot definitions (creates the enchant chain) |
| `patches/001/07-gear-enchant-sync.yaml` | All 21 enchant ID variables (links items to their enchant chain) |

---

## Layer 4: `equipment-item-standard`

The practical entry point for specs that create gear items. Encodes the full standard attribute set for each tier and slot so specs only declare what is specific to their gear family.

### Hierarchy

```
_EquipmentBase          — universal: enchantEnable, storeSellable, unidentifiedItemGrade,
                          warehouseStorable, guildWarehouseStorable, dropType, dropIdentify,
                          masterpieceRate
      ↓
_WeaponBase / _ChestBase / _GlovesBase / _BootsBase
                        — combatItemType per slot; _WeaponBase also sets linkPassivityCategoryId
      ↓
_HighTier*Base / _MidTier*Base (one per slot)
                        — tier standards: boundType, dismantlable, tradable, combineOptionValue
      ↓
HighTier*/MidTier* items — rareGrade + linkEnchantId (one per tier/slot/role)
      ↓
Class-specific derivations — combatItemSubType, category, requiredClass (e.g. MidTierChainWeapon)
```

### Exported Definitions

**Tier/slot items** — 14 definitions, one per tier × slot × role combination:
`HighTierWeaponDPSTankItem`, `HighTierWeaponHealerItem`, `HighTierChestItem`, `HighTierHandMailItem`, `HighTierHandLeatherItem`, `HighTierHandRobeItem`, `HighTierBootsItem`, and `MidTier` equivalents.

**Class-specific weapon derivations** — extend the appropriate tier weapon definition and add subtype, category, and requiredClass:

| Definition | Class | Extends |
|---|---|---|
| `MidTierChainWeapon` | Soulless (Reaper) | `MidTierWeaponDPSTankItem` |
| `HighTierChainWeapon` | Soulless (Reaper) | `HighTierWeaponDPSTankItem` |
| `MidTierGauntletWeapon` | Fighter (Brawler) | `MidTierWeaponDPSTankItem` |
| `HighTierGauntletWeapon` | Fighter (Brawler) | `HighTierWeaponDPSTankItem` |

### Tier Standards

| Attribute | High Tier (Mythic) | Mid Tier (Superior) |
|---|---|---|
| `boundType` | `Loot` | `Equip` |
| `dismantlable` | `false` | `true` |
| `tradable` | `false` | `true` |
| `combineOptionValue` | `3` | `2` |

### Current Consumers

| Spec | What it imports |
|------|----------------|
| `patches/001/01-reaper-weapons.yaml` | `MidTierChainWeapon`, `HighTierChainWeapon` |
| `patches/001/06-brawler-weapons.yaml` | `MidTierGauntletWeapon`, `HighTierGauntletWeapon` |
