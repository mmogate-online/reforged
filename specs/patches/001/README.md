# Patch 001 Specs

## Numbering Convention

Specs are prefixed with a two-digit number that controls apply order and groups related specs:

| Prefix | Group | Files |
|--------|-------|-------|
| `01-` | Gear standardization | `01-weapon-standardize.yaml`, `01-armor-standardize.yaml`, `03-flawless-standardize.yaml` |
| `02-` | Gear evolution paths | `evolutions/02-evo-*.yaml` |
| `03-` | Chest top-roll system | `02-chest-toproll-system.yaml`, `03-chest-toproll-items.yaml` |
| `04–09` | Enchant, infusion, crafting | Various |
| `10–15` | Crystals, dyad, dungeon tokens, infusion boxes | Various |
| `loot/` | Zone loot tables | Subfolder, per-zone files |

---

## Gear Standardization

**The most complex system in this patch.** Spans the `equipment-item-ids` package and two spec files.

### What It Does

Every gear item in the progression pipeline must have a set of server-required properties configured correctly. The game will not display enchanting, passivity rolls, or loot correctly without them. These properties are not set by default in the base datasheets.

**Properties applied to all gear:**

| Property | Value | Purpose |
|----------|-------|---------|
| `enchantEnable` | `true` | Allows enchanting at the enchant NPC |
| `boundType` | `Equip` | Item binds on equip |
| `warehouseStorable` | `true` | Can be stored in account warehouse |
| `guildWarehouseStorable` | `true` | Can be stored in guild warehouse |
| `unidentifiedItemGrade` | `1` | Required for identification/passivity roll system |
| `dropType` | `2` | Controls loot-bag behavior in group play |
| `tradable` | `true` / `false` | LOW/MID=true, HIGH=false (Mythic gear is bind-on-pickup) |

**Passivity category IDs by slot** (controls which roll pool the item draws from):

| Slot | `linkPassivityCategoryId` |
|------|--------------------------|
| Weapon (all types) | `120300` |
| Body armor (all types) | `120316` |
| Hand armor — mail | `4150` |
| Hand armor — leather | `4152` |
| Hand armor — robe | `4151` |
| Feet armor (all types) | `4250` |

> HIGH_TIER hand and feet pieces intentionally omit `linkPassivityCategoryId` — some sets (e.g. Visionmaker) have class-specific values already set and must not be overwritten.
>
> HIGH_TIER body pieces do get `120316` as a baseline, which is then overridden for class-specific chest pieces by `03-chest-toproll-items.yaml`.

### How It Works

```
packages/equipment-item-ids/index.yml
         (ID lists by tier + slot)
                   │
                   │  import (use.variables)
                   ▼
01-weapon-standardize.yaml  ←─ applies weapon properties
01-armor-standardize.yaml   ←─ applies armor properties (body/hand/feet)
03-flawless-standardize.yaml ←─ extra pass for Flawless-grade items
```

The `equipment-item-ids` package exports 21 named ID list variables. The standardize specs import only the ones they need via `use.variables` in the import block. This is a DSL requirement — variables must be explicitly opted in, they are not auto-imported.

### Adding Gear to the Pipeline

See `packages/equipment-item-ids/README.md` for how to add a new gear tier. Once IDs are in the package, re-running the two standardize specs covers them automatically.

---

## Gear Evolution (`evolutions/`)

The evolution system lets players upgrade gear by consuming Rune materials at the Evolution NPC. Each spec in the `evolutions/` subfolder defines one step in the gear progression chain.

**Current chain (LOW_TIER progression):**

```
Kugai's (lv8) → Starter 0 (lv11) → Starter 1 → Bastion → (MID_TIER chain continues...)
   evo-00-pre-starter    evo-00-starter-0    evo-01    evo-02
```

**Materials:**
- Weapons use Paverune of Shara (item 501)
- Armor uses Paverune of Arun (item 511)
- Higher-tier evolutions use Sil/Quoi/Arch/Keyrune variants

**How a spec works:**

Each `02-evo-NN-*.yaml` spec imports from `evolution-base` package and uses the `EvolutionItem` definition template. One `EvolutionItem` entry covers a single gear piece (SOURCE→TARGET) across 4 enchant steps: `+9→+0`, `+10→+3`, `+11→+6`, `+12→+9`. The `evolutionPaths: upsert` block lists one entry per gear piece (12 weapons + 9 armor = 21 entries for a full low-tier set).

The `evolution-base` package (`packages/evolution-base/index.yml`) defines all shared materials, cost, probability, and the `EvolutionItem` / rune path templates.

**All evolution specs use `upsert`** — they are idempotent and safe to re-apply.

---

## Other Systems (Brief Index)

| File(s) | System |
|---------|--------|
| `00-enchant-system.yaml` | Enchant probability and material configuration |
| `02-chest-toproll-system.yaml`, `03-chest-toproll-items.yaml` | Per-class passivity roll categories for HIGH_TIER chest pieces |
| `04-enchant-materials.yaml` | Enchant material item definitions |
| `05-enchant-item-links.yaml` | Links enchant materials to gear items |
| `06-brawler-weapons.yaml`, `06-gear-infusion-items.yaml` | Fighter (Brawler) weapon fixes; gear infusion item setup |
| `07-gear-enchant-sync.yaml`, `07-crafting-recipes.yaml` | Enchant data sync; crafting recipe definitions |
| `08-legacy-strings-restore.yaml` | Restores display strings overwritten by base patch |
| `09-frostfire-inheritance.yaml` | Frostfire gear set property inheritance |
| `10-crystal-boxes.yaml` | Crystal box item definitions |
| `11-dyad-*.yaml` | Full dyad crystal system (structures, abnormalities, passivities, crystal sets) |
| `11-potential-unlock-*.yaml` | Potential unlock scroll and gear configuration |
| `12-potential-unlock-gear.yaml` | Gear-side potential unlock properties |
| `13-potential-unlock-evolution.yaml` | Evolution paths for potential unlock gear |
| `14-dungeon-tokens.yaml` | Dungeon token items |
| `15-infusion-boxes.yaml` | Gear infusion box items |
| `loot/e-compensation/` | Zone-specific loot compensation tables, one file per zone |
