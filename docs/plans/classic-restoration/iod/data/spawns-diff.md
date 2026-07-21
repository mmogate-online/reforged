# Island of Dawn - v31 vs v92 Spawn / Territory Diff

Phase 3 diff artifact for the classic-restoration (v31-primary) port. Family: TerritoryData (territory groups, territories with fence geometry, single Npc spawns, and Party pack spawns). Scope: hunting zones 13, 64, 213, 313, 364 and dungeon 436.

Sources (read-only): v31 server `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet`; v92 server (post-revert clean baseline) `D:\dev\mmogate\tera92\server\Datasheet`. Parsed from raw XML with python; MCP not used.

## Headline

- v92 IoD TerritoryData is SEMANTICALLY IDENTICAL to v31 across all six zones (13, 64, 213, 313, 364, 436). A recursive canonical comparison of the full XML tree (every attribute including instanceId, every child element, PatrolList/SocialSet, Territory Attribute, and Party envelope) is equal on all six.
- The Phase 2 revert already restored the exact v31 spawn/territory state. The wipe-and-replace port of the spawn family is therefore a NO-OP: there is nothing to port, keep, or remove. Verdict totals are 100% MATCH (641 spawns, 470 territories, 37 groups, 219 parties), 0 PORT, 0 DECISION.
- The only byte-level difference is line-ending style: v31 files are CRLF, v92 files are LF (e.g. HZ 13 differs by exactly 5825 bytes = 5825 lines of CR). HZ 436 is byte-identical. Line endings are cosmetic and irrelevant to the game server.
- Recommendation for Phase 4: skip spec authoring for the spawn/territory family and replace it with a verification checkpoint (re-run this diff after any dev deploy to confirm the baseline still matches v31). Spend the port effort on families that actually diverge.

## Per-HZ counts and verdict totals

| HZ | Groups v31/v92 | Territories v31/v92 | Parties v31/v92 | Spawns v31/v92 | MATCH | PORT | KEEP | REMOVE | DECISION |
|----|----------------|---------------------|-----------------|----------------|-------|------|------|--------|----------|
| 13 | 25/25 | 403/403 | 214/214 | 498/498 | 498 | 0 | 0 | 0 | 0 |
| 64 | 2/2 | 15/15 | 0/0 | 64/64 | 64 | 0 | 0 | 0 | 0 |
| 213 | 4/4 | 24/24 | 0/0 | 51/51 | 51 | 0 | 0 | 0 | 0 |
| 313 | 1/1 | 6/6 | 0/0 | 8/8 | 8 | 0 | 0 | 0 | 0 |
| 364 | 1/1 | 4/4 | 0/0 | 4/4 | 4 | 0 | 0 | 0 | 0 |
| 436 | 4/4 | 18/18 | 5/5 | 16/16 | 16 | 0 | 0 | 0 | 0 |
| **all** | | | | 641/641 | **641** | **0** | **0** | **0** | **0** |

Spawn count = single `<Npc>` spawns plus `<Party>` member spawns. A spawn row is MATCH when its template, position bucket, and every material attribute (all attributes except the per-row `instanceId`) are identical on both sides, and, for party members, the enclosing party envelope also matches.

## Dispositions for v92-only rows

There are **no** v92-only groups, territories, parties, or spawns in any zone. Every v92 row has an identical v31 counterpart, so no KEEP / REMOVE / DECISION disposition is required. DECISION count is 0.

## Flags

| HZ | conditionalSpawn=true | pos 0,0,0 (random-in-fence) | abnormality territories |
|----|-----------------------|----------------------------|-------------------------|
| 13 | 0 | 365 | 0 |
| 64 | 0 | 0 | 0 |
| 213 | 0 | 0 | 0 |
| 313 | 0 | 0 | 0 |
| 364 | 0 | 0 | 0 |
| 436 | 0 | 10 | 0 |

- **conditionalSpawn:** none. Every spawn (single and party member) across all six zones carries `conditionalSpawn="false"`. No conditional/traveling choreography is encoded in TerritoryData; consistent with the doctrine note that such choreography is not achievable from held sources.
- **pos 0,0,0 random-in-fence:** 375 spawns (365 in HZ 13, 10 in HZ 436). This is the authentic engine pattern (spawn placed randomly inside the territory fence), not an error. Every Party member spawn uses it (formation/flock packs), which is why the two party-bearing zones account for all of them.
- **abnormality territories:** none. Every Territory `<Attribute>` child is `achieveConditionId="0" abnormality="0"` on both sides.
- **engine/cinematic-spawned templates absent from TerritoryData:** HZ 213 template 1036 (Leander shrine variant) is confirmed **not present** in TerritoryData_213 on either side - it is engine-spawned, as expected, and correctly absent from the diff. No action.
- **v31 internal inconsistency:** none found. The v31 TerritoryData tree is structurally clean and identical to v92 down to every attribute.

## Package-fit recommendation

Because the port is a no-op, no spawn specs need to be authored right now. The recommendation below applies IF spawn specs are later authored for this or another zone (e.g. a zone whose v92 state does diverge from v31).

`ClassicTerritory`, `RestoreSpawnBase`, and `RestoreSpawnAggressive` fit the shape of SINGLE `<Npc>` spawns and normal territories (they were derived from the 217 restored single spawns of patch 001). Two gaps must be closed before they cover the full v31 IoD population:

1. **`msgBroadcastingChannel` is missing from `RestoreSpawnBase`.** Every v31 single Npc carries `msgBroadcastingChannel="false"` (share 100%), but the archetype does not list it, so a spec built purely from `$extends: RestoreSpawnBase` would omit the attribute. Add `msgBroadcastingChannel: false` to `RestoreSpawnBase`.

2. **Party pack spawns are entirely unmodeled.** 307 of the 641 IoD spawns (48%) live inside `<Party>` elements (302 in HZ 13, 5 in HZ 436), which the archetype library does not represent at all. A Party carries its own envelope (`partySpawn`, `partyRespawnTime`, `partyRespawnRandomTime`, `partyAutoRespawn`, `autoRespawn`, `flock`, `randomFormationSpawn`, `delaySpawnTimeWhenWorldStart`, `bossInstanceId`, `desc`) plus member Npcs that add `memberId` and always spawn at pos 0,0,0 with a leader `spawnCount`. If party spawns must be authored via DSL, a new `ClassicParty` archetype (party-envelope constants) plus a party-member spawn archetype is needed - confirm first that the DSL territorySpawns schema even supports the Party nesting, since the existing `gen_spawn_specs.py` was built only for single spawns.

Per-row fields correctly left out of any archetype (supplied literally per spawn): `instanceId`, `npcTemplateId`, `pos`, `desc`, `memberId`, `ai`, `spawnCount`, `aggroSendToPartyDistance`.

