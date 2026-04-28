# npc-ids Package

Central registry of NPC template IDs per zone. Consumed by balancing specs to target
NPC cohorts without hardcoding template IDs in the spec files themselves.

## Purpose

Exports per-NPC scalar variables (one per template) and per-zone category group lists.
Balancing specs import only the variables they need via `use.variables`.

Typical usage in a `balanceProfiles` spec:

```yaml
imports:
  - from: npc-ids
    use:
      variables:
        - IOD_NORMAL_MONSTERS
        - IOD_KUGAI

balanceProfiles:
  - name: IoDTrashBuff
    npcFilter:
      huntingZoneId: 13
      id: $IOD_NORMAL_MONSTERS
    npc:
      stat:
        maxHp: { multiply: 5 }
        atk:   { multiply: 10 }

  - name: KugaiFieldBoss
    npcFilter:
      huntingZoneId: 13
      id: $IOD_KUGAI
    npc:
      stat:
        maxHp: { multiply: 20 }
        atk:   { multiply: 15 }
```

## File Structure

```
packages/npc-ids/
├── index.yml               # Re-exports all zone variables
├── README.md               # This file
└── zone-{ZZZ}-{name}.yml   # One file per zone
```

Zone files are named `zone-{3-digit-id}-{kebab-name}.yml`. Example:
`zone-013-iod.yml`, `zone-002-fey-forest.yml`.

## Zone Abbreviations

Used as the prefix for every variable in a zone file.

| Zone ID | Zone Name | Abbreviation |
|---------|-----------|--------------|
| 13 | Island of Dawn | `IOD` |
| 436 | Karascha's Lair | `KL` |
| 2 | Fey Forest | `FF` |
| 3 | Oblivion Woods | `OW` |
| 5 | Tuwangi Mire | `TM` |
| 6 | Valley of Titans | `VT` |
| 7 | Celestial Hills | `CH` |
| 15 | Cliffs of Insanity | `COI` |
| 16 | Vale of the Fang | `VF` |
| 17 | Paraanon Ravine | `PR` |
| 59 | Crescentia | `CR` |
| 60 | Lumbertown | `LT` |
| 63 | Velika | `VLK` |
| 487 | Bastion of Lok | `BOL` |
| 488 | Sinestral Manor | `SM` |

## Categorization Rules

NPCs are assigned to exactly one category, evaluated in this order. The first matching
rule wins.

| Category | Rule | Data source |
|----------|------|-------------|
| **Friendly NPCs** | `villager=true` | `audit_zone_spawns.villager` |
| **Objects** | `isObjectNpc=true` | `audit_zone_spawns.isObjectNpc` |
| **Boss Monsters** | `showAggroTarget=true` | `audit_zone_spawns.showAggroTarget` |
| **Elite Monsters** | `elite=true` | `audit_zone_spawns.elite` |
| **World Bosses** | Manual selection (fixed position, respawn > 2h) | Human judgment |
| **Normal Monsters** | Everything else | Catch-all |

### Exclusions

Two kinds of NPC templates are **not** included in the package:

- **Parent-only formation templates**: Templates marked `(페어런츠용 몬스터)` in the
  Korean internal name. These exist in `NpcData_{zone}.xml` but are never placed in
  `TerritoryData` and never spawn. They define party composition for formation spawns,
  not playable NPCs. Excluding them keeps the package focused on real game entities.

- **Environmental triggers with no display name and `hasName=false`**: These appear in
  spawn data but are not meaningful targets — the category system does not cover them.

### Category caveats

- `playStyle=creature` NPCs (near-zero HP, scripted behaviour) are classified as
  Normal Monsters by the catch-all rule. Balance specs should filter them out when
  they are not intended targets.

- When a single display name maps to multiple template IDs (e.g., 4 "Scion Scout"
  variants in IoD), each variant gets its own scalar with a numeric suffix
  (`IOD_SCION_SCOUT_1`, `IOD_SCION_SCOUT_2`, …) to preserve the one-scalar-per-template
  rule.

## Variable Naming

### Individual NPC variables

Pattern: `{ZONE_ABBR}_{ENGLISH_DISPLAY_NAME_UPPER_SNAKE}`. Special characters
(apostrophes) are dropped: `Acharak's Soldier` → `IOD_ACHARAKS_SOLDIER`.

When the same display name maps to multiple template IDs, disambiguate with a suffix:
`IOD_TERRON_SABOTEUR` (combat variant, 300943) vs `IOD_TERRON_SABOTEUR_ENV`
(environmental variant, 1011).

### Category group variables

Pattern: `{ZONE_ABBR}_{CATEGORY}` where category is one of:
`FRIENDLY_NPCS`, `NORMAL_MONSTERS`, `ELITE_MONSTERS`, `BOSS_MONSTERS`,
`WORLD_BOSSES`, `OBJECTS`. Each is a list of template IDs.

Group lists reference the individual scalar variables (`$IOD_PIGLING`, etc.) so each
ID lives in a single place. DSL resolves these references at declaration time.

## How to Add a New Zone

1. Create `zone-{ZZZ}-{kebab-name}.yml` following the IoD file as a template.
2. Populate NPC IDs using `mcp__datasheet-v92__audit_zone_spawns` to read flags.
3. Assign each NPC to a category per the rules above.
4. List every exported variable in the file's `exports.variables` section.
5. Add an import block for the new file in `index.yml`.
6. Re-export the same variables from `index.yml`.
7. Add the zone abbreviation to the table in this README.

## Consumers

_None yet — this package is the foundation for upcoming NPC balance specs._
