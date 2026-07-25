# Datasheet MCP: no read support for the Field Event system (FieldData / FieldEvent) (2026-07-22)

## Resolution log (2026-07-25): CLOSED, all three requests implemented

datasheet-mcp commit `2135eaf`. 378 tests green; Release AOT publish validated over a direct stdio
harness against v92, v31 and a client DataCenter dump.

- **Request 1 (minimum useful): done.** Three new entity types in `entity_config.json`:
  - `FieldEvent` (`FieldData_{continentId}.xml`, zone-partitioned by continent). `FieldEvent.id`
    is unique only within its file, so the continent is the partition key: pass it as
    `huntingZoneId` to `lookup`/`search`, or as `continentId` to the dedicated tools.
  - `FieldActionScript` (`S1ActionScripts_Field.xml` **plus** `S1ActionScripts_Spawn.xml`; 8 of the
    17 `doActionScript` ids referenced by field events live in the Field sheet, the other 9 in the
    Spawn sheet, and the id ranges do not overlap).
  - `FieldEventClearReward` (the `FieldEvent.xml` clear-reward tiers, keyed by `ClearReward.id`).
  - New tool `list_field_events`: all 16 events across the 12 continent files, with EventGroup /
    EventTask / Guide-task counts and rotation schedule per event.
  - New tool `lookup_field_event(continentId, eventId, eventGroupType?, eventTaskType?, maxResults?)`:
    header, conditions, clear condition, progress, `AutoEventBalance` tiers with resolved
    abnormality names, scoring rules, guide objectives with resolved NPC display names, spawn areas,
    clear-reward pool, aero territories, and the full EventGroup/EventTask tree with type filters.
- **Request 2 (higher value): done.** New tool `audit_field_event_references(continentId, eventId)`.
  Reference semantics were established empirically over all 12 FieldData files rather than assumed:
  - `EventTask spawn/despawn` (`huntingZoneId` + `territoryId`) to `Territory`: 2,044 of 2,075
    resolve; the audit surfaces the 31 genuinely dangling ones (e.g. 7011/1 despawns `622,62200003`,
    which `TerritoryData_622.xml` does not define).
  - `EventTask.targetNpcId` and `Guide/Task.target` (`@creature:hz#id`) to `NpcTemplate`: 2,051/2,051.
  - `EventTask abnormality` and `BasicAbnormality.abnormalityId` to `Abnormality`: 211/211,
    including the reserved 77770001-77770030 scaling range.
  - `EventGroup.uniqueId` is **type-dependent**, not uniformly an NPC ref: the `npc*` triggers
    resolve 11/11 against `NpcTemplate`, `enterTerritory` / `userCountInTerritory` resolve 22/22
    against `TerritoryData`. Probing one table for both would have reported about two thirds of
    them as dangling.
  - Rotation `Event(continentId, eventId)` entries pointing at undefined events are flagged by
    `list_field_events`; per-event rotation membership is reported by the audit.
  - **Correction to the request:** `EventGroup.targetInstanceId` and
    `EventTask[dynamicSpawn].targetInstanceId` do **not** map to `NpcTemplate` (0 of 1,014 resolve).
    They are placed-instance handles (321/321 match `TerritoryData` `Npc.instanceId`) and runtime
    DynamicSpawn ids. They are reported in an explicit `[Unchecked]` section with the reason, rather
    than as false positives.
- **Request 3 (nice to have): done** via the `FieldActionScript` entity plus the
  `EventTask[doActionScript].actionScriptId` check in the audit.
- **Not exposed:** the `FieldEvent.xml` AFK (`FieldEventBanTime`), world-map UI, size, state and
  font-colour sections. They carry no integer key and are irrelevant to authoring correctness;
  the rotation, reward and clear-reward data they sit beside is covered above.
- **v31:** the whole family is absent there. All three tools return an explicit "field event system
  is v92-only" message instead of an empty result.

Investigating feasibility of authoring new Guardian Legion (open-world field) events. The
server datasheet carries the full system, but the MCP cannot see any of it.

- `list_entity_types` (both `datasheet-v92` and `datasheet-v31`) does **not** include
  `FieldData` or `FieldEvent`. There is no lookup, search, reference-check, or audit tool
  that reaches them.
- The files are present and non-trivial in the server datasheet (`server_datasheet` in
  `.references`):
  - `FieldData_{continentId}.xml`: 12 files (continents 7001, 7003, 7005, 7011, 7012, 7013,
    7014, 7015, 7021, 7022, 7031, 2000). Sizes 2 KB (dummy transport) to 360 KB (7021 flying).
  - `FieldEvent.xml`: single global rotation/reward/AFK/UI file.
  - `S1ActionScripts_Field.xml`: client-effect scripts referenced by `doActionScript` tasks.
- Effect: any correctness check while authoring a new event (does this `abnormalityId` exist,
  does this `territoryId` / `huntingZoneId` resolve, is this `targetInstanceId` a real NPC
  template, does the `RotationGroup.Event(continentId, eventId)` reference a real
  `FieldEvent.id`) has to be done by hand in Python. There is no validation target after an
  apply, unlike every other entity we edit.

## Context we already have (would inform the tooling)

- The system is documented and verified at
  `datasheet-domain/src/content/docs/entities/field-event-system.md`: 17 EventGroup trigger
  types, 21 EventTask types, the `FieldData` element tree, the `FieldEvent.xml` rotation model,
  the reserved 77770001 to 77770030 scaling-abnormality range, and the cross-system ID links.
- Confirmed `FieldData` element tree (from `FieldData_7003.xml`):
  `Field(continentId) > FieldEvent(id,...) > {Condition, ClearCondition, Progress,
  AutoEventBalance>Balance, EventPoint>Point, Guide>Task, EventGroup>Event>EventTaskGroup>EventTask,
  ClearRewardPool>ClearReward, SpawnAreaList>SpawnArea, FieldEventCloud>AeroList>Aero, AeroTerritory}`.
- Cross-references that a reference-check tool could validate against entities the MCP
  **already** exposes:
  - `EventTask type="spawn"/"despawn"` maps to `Territory` (`huntingZoneId` + `territoryId`)
  - `EventTask type="abnormality"` / `BasicAbnormality.abnormalityId` maps to `Abnormality`
  - `EventGroup.uniqueId` / `targetInstanceId` maps to `NpcTemplate` (`continentId,templateId`)
  - `FieldEvent.xml RotationGroup.Event` maps to `FieldData` `FieldEvent.id`
  - `Guide.Task.target` (`@creature:zone#templateId`) maps to `NpcTemplate` display name
- The client DataCenter mirrors the system with XSDs (`Field/`, `FieldEvent/`, `StrSheet_Field/`),
  so string IDs in `Guide.titleString`/`description` resolve against `StrSheet_Field`.

## Requests

1. **Minimum useful:** expose `FieldData` and `FieldEvent` as queryable entity types
   (`lookup` / `search` by `continentId` + event `id`, and dump of an event's EventGroup /
   EventTask tree). This alone turns "hand-parse 12 XML files" into a normal MCP query and
   gives an authoring reference surface.
2. **Higher value:** a `check_references`-style validator for field events that resolves the
   cross-references listed above against the existing NPC / Territory / Abnormality tools, and
   flags rotation `Event(continentId, eventId)` entries that point at a non-existent
   `FieldEvent.id`. This is the validation target we lack after an apply.
3. **Nice to have:** surface `S1ActionScripts_Field.xml` script IDs so `doActionScript`
   task references can be validated too.

## Related

- Paired DSL write request: `docs/dsl-requests/2026-07-22-fieldevent-entity.md`. Read support
  here is the validation half; DSL support is the authoring half. Both are currently absent.
