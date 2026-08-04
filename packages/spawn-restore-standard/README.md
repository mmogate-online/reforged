# spawn-restore-standard Package

Reusable DSL archetypes for classic-zone spawn restoration. Factors the boilerplate
that every restored `territorySpawns` and `territories` entry repeats, so the
dc-restore generator emits `$extends` plus per-row deviations instead of a full
attribute dump.

## Type

System / template package. Exports three definitions, no variables.

## Definitions

| Definition | Purpose | Fields |
|------------|---------|--------|
| `RestoreSpawnBase` | Environmental defaults shared by every restored world spawn | 31 (tau>=0.9) |
| `RestoreSpawnAggressive` | Aggressive sub-archetype (`$extends RestoreSpawnBase`, `isAggressiveMonster: true`) | +1 |
| `ClassicTerritory` | Constant territory-shape defaults | 6 |

Values were derived statistically from the 217 restored HZ 13 spawns and 217
territories in patch 001, using a tau=0.9 modal-share acceptance threshold (the same
rule `npc-standard` uses). Every folded value is annotated in `index.yml` with its
share across the restoration sample.

## What is NOT in the archetypes

Zone-agnostic reuse means identity and genuinely per-mob fields are always supplied
per row and never inherited:

- Identity: `huntingZoneId`, `groupId`, `territoryId`, `npcInstanceId`, `npcTemplateId`.
- Per-row literals: `desc`, `pos` (spawns); `desc`, `fences` (territories).
- Below-tau per-mob fields (spawns): `ai` (37% modal), `spawnCount` (73%), `memberId`
  (82%), `aggroSendToPartyDistance` (53%). These are emitted per row.

`isReturn` is held at its non-aggressive default (`false`) in the base. It is not
correlated with aggression: the 17 aggressive rows keep `isReturn=false`, and a
disjoint set of 17 rows carry `isReturn=true`, which the generator emits per row.

## Usage

```yaml
imports:
  - from: spawn-restore-standard

territories:
  upsert:
    - huntingZoneId: 13
      groupId: 1300019
      territoryId: 13014260
      $extends: spawn-restore-standard.ClassicTerritory
      desc: "restored territory"
      fences:
        - [79705.3, -83665.1, -4522.1]

territorySpawns:
  upsert:
    - huntingZoneId: 13
      groupId: 1300019
      territoryId: 13014260
      $extends: spawn-restore-standard.RestoreSpawnBase
      npcInstanceId: 13472950
      npcTemplateId: 302
      desc: "Nature Spirit"
      pos: [79851.2, -83394.5, -4501.4]
      ai: 11
      spawnCount: 6
      memberId: 0
      aggroSendToPartyDistance: 500
```

Definitions auto-import from the package (no `use:` clause needed). Any field a row
sets after `$extends` overrides the inherited value (deep merge, child-wins).

## Consumers

- `tools/dc-restore/gen_spawn_specs.py` (patch 001 spec `02-iod-spawn-restore.yaml`).

Future classic-zone restorations (other IoD layers, hub cities, dungeons) reuse the
same archetypes.
