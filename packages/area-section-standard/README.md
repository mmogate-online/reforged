# area-section-standard Package

Reusable DSL archetype for classic area-section restoration. Factors the attribute
envelope that every restored `areaSections` entry repeats, so the dc-restore
generator emits `$extends` plus per-row deviations instead of a full attribute dump.

## Type

System / template package. Exports one definition, no variables.

## Definitions

| Definition | Purpose | Fields |
|------------|---------|--------|
| `ClassicSection` | Shared shape of a classic town/camp/outpost section | 14 |

The seven booleans (`huntingZoneId=-1`, `floor=1`, `desTex=false`, `protect=false`,
`guildWar=true`, `ride=true`, `trade=true`) are constant across the sample. The
remaining fields (`duel`, `vender`, `pcMoveCylinder`, `campId`, `worldMapSectionId`,
`subtractMinZ`, `pk`) hold the dominant classic default and are overridden per row
where a specific section differs. Each field is annotated with its modal share in
`index.yml`.

## What is NOT in the archetype

Zone-agnostic reuse means identity, geometry, and continent-specific fields are
supplied per row and never inherited:

- Identity / geometry: `continentId`, `areaName`, `parentSectionId`, `sectionId`,
  `nameId`, `desc`, `priority`, `addMaxZ`, `fences`.
- Continent-specific recall block: `recallReviveContinentId`, `recallRevivePos`,
  `recallScrollContinentId`, `recallScrollPos`.
- Occasional fields not present in every section (e.g. `restBonus`, `enableItemId`,
  `disableItemId`).

A ring-only revert (a section whose attributes must not change, only its fence ring)
must NOT extend `ClassicSection`, or it would gain section attributes it should not
carry. The generator emits those rows literally.

## Usage

```yaml
imports:
  - from: area-section-standard

areaSections:
  upsert:
    - continentId: 13
      areaName: "ATW_Death_P"
      parentSectionId: 4
      sectionId: 6
      $extends: area-section-standard.ClassicSection
      nameId: 13002
      desc: "Pegasus Platform"
      priority: 4
      addMaxZ: 1000.000000
      recallReviveContinentId: 13
      recallRevivePos: "66600.8,-79855.5,-2993.1"
      recallScrollContinentId: 13
      recallScrollPos: "66600.8,-79855.5,-2993.1"
      fences:
        - [70152.3, -70773.4, -3485.0]
```

Definitions auto-import from the package (no `use:` clause needed). Any field a row
sets after `$extends` overrides the inherited value (deep merge, child-wins).

## Consumers

- `tools/dc-restore/gen_section_specs.py` (patch 001 spec `01-iod-area-sections.yaml`).

Future area/section restorations (other IoD layers, hub cities) reuse the archetype.
