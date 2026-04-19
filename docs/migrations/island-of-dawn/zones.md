# Island of Dawn — Zone Inventory

## Continent 13 — Island of Dawn (Channeling Zone)

All zones on continent 13 share the same physical map space. Continent type: `channelingZone`.

| Zone ID | Name | Type | v31 NPCs | v92 NPCs | Notes |
|---------|------|------|----------|----------|-------|
| 13 | Island of Dawn | channelingZone | 57 | 186 | Main hub. v92 has endgame BAMs added |
| 64 | Tower Base | channelingZone | 51 | 51 | Named sub-zone, Nexus tower area |
| 213 | (unnamed) | channelingZone | 93 | 93 | Substantial sub-zone, no player-facing name |
| 313 | (unnamed) | channelingZone | 8 | 8 | Small sub-zone |
| 364 | (unnamed) | channelingZone | 8 | 8 | Small sub-zone |

### Continent 13 Properties (v92)

- `cancelAbnormalityId`: 990070318–990070322
- `withAbnormalityId`: 488000009 (beginner buff/restriction system)

### Region Names (v92 string table)

| Region ID | Name |
|-----------|------|
| 13001 | Island of Dawn |
| 13019 | Western Island of Dawn |
| 13021 | Eastern Island of Dawn |
| 13023 | Southern Island of Dawn |

## Continent 9016 — Island of Dawn Prologue (Dungeon)

| Zone ID | Name | Type | v31 NPCs | v92 NPCs | Notes |
|---------|------|------|----------|----------|-------|
| 416 | Island of Dawn (Prologue) | dungeon | 58 | 58 | Instanced tutorial. DungeonName = "Island of Dawn Clifftops" |

Continent type: `dungeon`, `isSpecificSpace: TRUE`. Single-zone continent.

## Continent 9015 — Island of Dawn Coast (v92 only)

| Zone ID | Name | Type | v31 NPCs | v92 NPCs | Notes |
|---------|------|------|----------|----------|-------|
| 415 | Island of Dawn Coast | channelingZone | N/A | 65 | v92-only zone. Decision deferred |

Continent type: `channelingZone`, `isSpecificSpace: TRUE`. Single-zone continent. Does not exist in v31.

## Continent 9827 — Stepstone Isle (v92 only, being replaced)

| Zone ID | Name | Type | v31 NPCs | v92 NPCs | Notes |
|---------|------|------|----------|----------|-------|
| 827 | Stepstone Isle | dungeon | N/A | 83 | Current starting zone. No ZoneName entry; name from DungeonName |

Continent type: `dungeon`. Single-zone continent. Does not exist in v31. Files will be left in place but unreferenced after migration.

## Migration Target Zones

Zones requiring v31 → v92 file migration: **13, 64, 213, 313, 364, 416**
