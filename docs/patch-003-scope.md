# Patch 003 (Guardian Legion and Content Customizations) Zone Scope

Defines the complete set of zones in scope for patch 003. Research, loot work, merchant audits,
spawn queries and NPC queries scoped to patch 003 must include **all zones listed here**, not just
the combat hunting zone.

Patch 003 develops against the closed patch 002 baseline.

## Island of Dawn (continent 13)

The Guardian Legion event runs in the **live world hunting zone 13**, not in a dedicated mission
hunting zone. That is a proven departure from all 12 shipped field events, which use dedicated
mission zones 620 to 631. Consequence: event territories share a zone with ambient world content,
so every event territory must be `type="quest"` and the world takeover despawn and restore list is
load bearing.

| Zone ID | Name | Type |
|---------|------|------|
| 13 | Island of Dawn | continent, `channelType="field"` since spec 002/35 |
| 13 | Island of Dawn | combat hunting zone |
| 64 | Island of Dawn | Tower Base hub layer |
| 213 | Island of Dawn | mid-island and western layer |
| 313 | Island of Dawn | layer |
| 364 | Island of Dawn | layer |
| 436 | Karascha's Lair | dungeon continent |
| 437 | Karascha's Lair | dungeon hunting zone |

Always enumerate all five layered hunting zones plus the dungeon. Never query hunting zone 13 in
isolation. This is the same rule as patch 001; see `patch-001-scope.md`.

### Event geography

Three staging points, all inside continent 13, confirmed against `AreaData`:

| Phase | Position | Containing section |
|---|---|---|
| 1, minion swarm | `51930, -81192, -4534` | 13003 Mysterious Ruins |
| 2, raider wave | `51290, -78824, -4733` | 13003 Mysterious Ruins |
| 3, boss | `50107, -77786, -4742` | 13008 **Orcan Bivouac** |

Leg 1 to 2 is about 2,450 units, leg 2 to 3 about 1,570 units.

## Donor zones (read-only reference, never an apply target)

These zones are read during authoring because they hold the donor templates, AI and skills being
copied. Nothing in patch 003 writes to them.

| Zone ID | Name | Why |
|---------|------|-----|
| 620 | Veritas District Guardian Legion mission zone | Elite boss donor `620,1005`, the only Orcan in the corpus carrying a field event authored skill |
| 87 | Orcan Hold | Raider donor `87,2031`, the only same-model Orcan with a `Cooperation` work list |
| 7015 | Continent owning hunting zone 620 | Reference `FieldData` for a shipped Guardian Legion mission |

## Reserved id block

`13,2001` through `13,2099` is reserved for authored Reforged NPC templates in hunting zone 13.
Proven free across the v92, v31 and v17.11 clients and the v92 and v31 servers, in every
id-bearing family. Allocation and the proof table are in
`docs/plans/classic-restoration/iod/guardian-legion/data/orcan-npc-donor-survey.md` section 5.

**Id hazard:** `13,7001` to `13,7009` and `13,9001` carry live loot tables and live display names
with no template in any era. Creating a template at one of those ids silently inherits both. Do
not allocate outside the reserved block without re-running the proof.
