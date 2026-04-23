# equipment-item-ids Package

Central registry of gear item IDs for the Reforged server. Consumed by the gear standardization specs in `specs/patches/001/` to apply server-required properties to all gear items in the progression pipeline.

## Purpose

This package exports named lists of item IDs grouped by tier and slot. Standardization specs import these lists to apply properties in bulk (enchant enable, passivity category, bound type, tradability, etc.) without hardcoding IDs in the spec files themselves.

Adding a new gear set to the pipeline means: add its IDs here, re-run the standardize specs.

## Tier Structure

| Tier | Grade | In-Game Term | Tradable |
|------|-------|--------------|----------|
| `HIGH_TIER` | 4 (Mythic) | Mythic-grade endgame gear | No |
| `MID_TIER` | 3 (Superior) | Mid-game progression gear | Yes |
| `LOW_TIER` | 1–2 (Uncommon/Rare) | Early-game starter gear | Yes |

**LOW_TIER sets (ordered by gear level):**
1. Kugai's (lv8) — obtained during early-game play
2. Starter 0 (lv11) — evolved from Kugai's
3. Starter 1 — next progression step
4. Bastion — final LOW_TIER step before MID_TIER

## Slot and Type Variables

Each tier exports variables per slot. Hands are split by armor type because they use different passivity roll pools:

| Variable suffix | Slot | Notes |
|-----------------|------|-------|
| `_HEALER_WEAPON_IDS` | Weapon (staff/rod) | Separate from DPS — different class set |
| `_DPS_WEAPON_IDS` | Weapon (all others) | All non-healer weapon types |
| `_BODY_IDS` | Body armor | Mail + leather + robe in one list |
| `_HAND_MAIL_IDS` | Hand armor (mail) | Mail classes only |
| `_HAND_LEATHER_IDS` | Hand armor (leather) | Leather classes only |
| `_HAND_ROBE_IDS` | Hand armor (robe) | Robe classes only |
| `_FEET_IDS` | Feet armor | Mail + leather + robe in one list |

**Why hands are split but body/feet are not:** hand armor has armor-type-specific passivity roll pools (`linkPassivityCategoryId`: mail=4150, leather=4152, robe=4151). Body and feet use the same pool regardless of type (body=120316, feet=4250), so they can be batched together.

## Class → Armor Type Mapping

This is game domain knowledge that isn't stored in the XML files:

| Armor Type | Classes |
|------------|---------|
| Mail | Lancer, Berserker, Engineer (Gunner), Fighter (Brawler) |
| Leather | Warrior, Slayer, Archer, Glaiver |
| Robe | Sorcerer, Priest, Elementalist (Mystic), Assassin (Ninja) |

Soulless (Reaper) starts at level 50 with unique gear and does not participate in the standard gear progression pipeline.

## How to Add a New Gear Tier

1. Identify the item IDs for each slot and weapon type (use `mcp__datasheet-v92__search` or `batch_lookup`).
2. Add them to the appropriate `_TIER_*` variable in `index.yml`, following the existing comment pattern (`# --- Set Name (PowerTierN) ---`).
3. Make sure the new IDs are added to all relevant slot variables (healer weapon, DPS weapon, body, hand mail/leather/robe, feet).
4. The standardize specs pick them up automatically on next `dsl apply` — no spec changes needed unless the new tier belongs in a different tradability group.

**Variable naming:** `{HIGH|MID|LOW}_TIER_{SLOT}_IDS`. All variables are listed in the `exports.variables` section at the bottom of `index.yml`.

## Consumers

| Spec | What it does |
|------|-------------|
| `specs/patches/001/01-weapon-standardize.yaml` | Applies weapon baseline properties to all tiers |
| `specs/patches/001/01-armor-standardize.yaml` | Applies armor baseline properties to all tiers |
| `specs/patches/001/03-flawless-standardize.yaml` | Additional properties for Flawless-grade items (HIGH_TIER subset) |

The standardize specs import only the specific variables they need via `use.variables` in their import block. Not all variables need to be imported by every consumer — DSL variables must be explicitly opted in.
