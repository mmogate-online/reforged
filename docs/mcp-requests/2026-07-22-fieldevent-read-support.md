# Datasheet MCP: no read support for the Field Event system (FieldData / FieldEvent) (2026-07-22)

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
