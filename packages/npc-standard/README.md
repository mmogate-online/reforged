# npc-standard

NPC authoring **standard library**. Supplies default scaffolding so specs declare
only identity/wiring fields instead of re-authoring boilerplate per NPC.

This is the *authoring* counterpart to [`npc-ids`](../npc-ids/README.md) (which
only *targets* existing NPCs).

## Data-derived

`index.yml` is **auto-generated**, not hand-written. Defaults come from a
full-population statistical analysis of the live datasheet (all 22,358 NPCs /
11,750 AIs / 95,806 spawns / 174,272 skills), segmented into 6 semantic archetypes,
accepting a value as a default only when its modal share within the cluster is
**≥ τ (0.90)**. Every value in `index.yml` is annotated with its `share` and
sample size `n`.

- Methodology, validation, pipeline, resume steps: **`tools/npc-standard/README.md`**
- Pipeline: `tools/npc-standard/analyze_all.py` + `analyze_skills.py`
- Codegen: `tools/npc-standard/codegen.py` then `codegen_skills.py` (writes `index.yml`)
- **Do not hand-edit `index.yml`** — re-run the pipeline + codegen to regenerate.

Cross-validated reconstruction accuracy (5-fold): 95–99% NPC/AI/territory,
**98.7–99.3% skills**.

## Exported definitions

Per archetype × section: `<Cluster>` (npcs), `<Cluster>Spawn` (territorySpawns),
`<Cluster>Skill` (npcSkills). **AI archetypes live in the separate
[`ai-standard`](../ai-standard/) package** (import it alongside this one). Clusters:

| Archetype | Selector |
|---|---|
| `MerchantVillager` | `villager=true`, not `questVillager` |
| `QuestVillager` | `villager=true`, `questVillager=true` |
| `NormalMonster` | combat, not elite/boss/object |
| `EliteMonster` | `elite=true` |
| `BossMonster` | `huntingStyle=raid` |
| `ObjectNpc` | `isObjectNpc=true` |

## Usage

```yaml
imports:
  - from: npc-standard
  - from: ai-standard      # AI archetypes split into their own package

npcs:
  upsert:
    - $extends: MerchantVillager
      huntingZoneId: 213
      id: 9001
      name: "my_merchant"
      shapeId: 53072008
      basicActionId: 5002600
      aiid: 9001
      scale: 1.0          # required, varies per NPC (not defaultable)
      race: popori
      gender: male
ai:
  upsert:
    - $extends: MerchantVillagerAI
      huntingZoneId: 213
      id: 9001
      name: "my_merchant_ai"
territorySpawns:
  upsert:
    - $extends: MerchantVillagerSpawn
      huntingZoneId: 213
      groupId: 21300003
      territoryId: 21300023
      npcInstanceId: 21399001
      npcTemplateId: 9001
      ai: 9001
      pos: [60000.0, -75000.0, -5000.0]
      respawnTime: 90000   # required, varies per spawn (not defaultable)
```

Worked example: `temp/specs/merchant-9001-derived.yaml` (validates + applies, 9 ops).

### From-scratch territory (optional)

`VillagerSpawn` above reuses an existing territory polygon. To author a **new**
territory instead (now that the AOT fence fix has landed), add a `territories` block
and point the spawn's `territoryId`/`groupId` at it — `fences` is a list of bare
coordinate triples:

```yaml
territories:
  upsert:
    - huntingZoneId: 213
      groupId: 21300003
      territoryId: 21399001
      type: normal
      addMaxZ: 100
      subtractMinZ: 100
      desc: "my territory"
      fences:
        - [52362.0, -69251.0, -5637.0]
        - [52233.0, -70033.0, -5727.0]
        - [53486.0, -70300.0, -5660.0]
```

(Some published schema examples show a stale `fences: - pos: [...]` form. The shape above is
the one the tool actually accepts.)

## DSL coverage

Now modelled and round-tripping idempotently: `abnormalityResistanceOverride` with its nested
`abnormalities` list, `objectNpcAiParam` and `balanceRef` on npcs, all 14 `territorySpawns`
fields including an empty `aggroIgnorePartyId`, and `balanceRef` on npcSkills. The npcSkills
field gaps are closed and re-added to the `<Cluster>Skill` archetypes.

**Not modelled yet**, so an archetype cannot carry them:

- npcSkills `defence.damageApplyRate` (present on 99% of skills), `parentId` (98%),
  `returnAnimSet` (95%), `ignoreDefenceRate` (59%).
- npcSkills `actions` and `targetingLists`, both list-typed.
