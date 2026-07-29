# Datasheet MCP: `lookup`/`batch_lookup` on `Item` fail with an unexplained error (2026-07-28)

Context: surfaced during the feedstock flattening research for patch 002, while resolving
the four reward item ids on quest 272 (the only quest in v92 carrying two `Compensation`
groups). Probed against `datasheet-v92`.

## 1. BUG: bare `An error occurred invoking '<tool>'` with no reason string

Both tools fail identically for `entity: "Item"`:

```
mcp__datasheet-v92__lookup(entity="Item", id=219006)
  -> An error occurred invoking 'lookup'

mcp__datasheet-v92__batch_lookup(entity="Item", ids=[219006, 219013, 202144, 202150, 219007])
  -> An error occurred invoking 'batch_lookup'
```

Ids probed: **219006, 219013, 202144, 202150, 219007**. All five are real reward/trigger
item ids read verbatim out of `QuestCompensationData_2.xml` in the server datasheet tree
(resolve `server_datasheet` from `.references`):

```xml
<Quest questId="272">
    <Compensation compensationId="1">
      <CompensationType type="normal" itemBag="allpay">
        <Item templateId="219006" quantity="1" />
        <Item templateId="202144" quantity="1" />
```

`219007` is the item whose use triggers the quest, per `lookup_quest 272`.

**The server was up and the index was reachable in the same session.** `lookup_quest` on
the same server, same session, returned a full payload:

```
lookup_quest(272)
  -> Quest 272: Rise of the Dead
     state: live | recommendedLevel: 60 | repeatable | cancellable
     [Trigger] itemUse=NPC 219007
     [Requirements] minLevel=60
     [Tasks] 1, types: DeliverItem x1
```

So this is not a dead server and not a transport failure.

## 2. Why the opacity is the actual problem

The message names the tool and nothing else. From the caller's side, at least four
distinct conditions are indistinguishable:

| Possible cause | How the caller should react | Currently distinguishable? |
|---|---|---|
| The id does not exist in the item table | accept it, record "no such item" | no |
| `Item` is the wrong entity name for this server | retry with the right name | no |
| The index is stale or not built for this entity | rebuild / report staleness | no |
| The tool crashed (parse error, null deref) | file a bug, fall back | no |

Two of those are ordinary findings a caller must be able to act on; two are defects. With
one undifferentiated string there is no way to branch, and no way to know whether a retry
is even meaningful.

## 3. Caller impact

**The fallback is raw XML parsing, which is the thing the MCP exists to avoid.** Because
the error could not be classified, the research pass could not treat "no result" as a
finding and had to resolve those ids by walking the datasheet XML directly with a script.
Every such fallback reintroduces exactly the risks the MCP removes: hand-rolled path
assumptions, no comment stripping, no id-space awareness, and no client/server parity
check. This project has already been bitten by find-and-replace style id handling on this
same family (the `itemMixId` / `decompositionId` id spaces overlap the item id space
numerically), so pushing callers back onto raw parsing has a real cost here.

Secondary cost: `Item` is one of the most-called entities in this repo's research work. A
reward row, a loot bag row and a shop row all give a bare `templateId`, so item resolution
sits on the critical path of nearly every audit.

## 4. Request

1. **Structured error naming the cause.** Any failure should carry a reason string
   identifying which of the conditions in section 2 occurred: unknown entity type, entity
   not indexed, index stale, internal exception (with the exception class or a stable error
   code). Follow the precedent the `search` filter path already sets on this server, which
   is exemplary:

   ```
   search(QuestCompensation, huntingZoneId=13, filters={"exp": "1000..99999"})
     -> Filter 'exp' is not an attribute of <Quest>; it is an attribute of its child
        element <Compensation/CompensationType>. Filters match root attributes only.
        Use count with childElement=CompensationType groupBy=exp ...
   ```

   That message tells the caller exactly what to do next. The `Item` lookup failure tells
   the caller nothing.

2. **A distinct "not found" result that is not an error.** A missing id is a normal,
   expected outcome of a lookup and should return an empty/not-found result the caller can
   read as data, not an exception. For `batch_lookup` this matters more: one bad id in a
   list of five should not take down the other four. Expected shape is a per-id result set
   with found/not-found per entry, so a partial answer is still usable.

## Expected versus actual

**Expected:** `lookup`/`batch_lookup` on `Item` either return item records, or return a
not-found result per id, or fail with a message naming the cause.

**Actual:** a bare `An error occurred invoking '<tool>'` for all five ids, on a server that
answered `lookup_quest` correctly in the same session.

---

## Resolution (datasheet-mcp, 2026-07-28)

### Section 1 does not reproduce. The parameter is `entityType`, not `entity`.

All five ids resolve against `datasheet-v92`:

```
lookup(entityType="Item", id=219006)   -> Item 219006, name eventItem, combatItemType MIX_DISPOSAL
batch_lookup(entityType="Item", ids=[219006, 219013, 202144, 202150, 219007])
                                       -> Batch lookup: 5/5 found in Item
```

The calls in section 1 pass `entity=`. Every entity-scoped tool on this server takes `entityType`
(verified: all 13 of them, no exceptions), so the argument never bound and the tool body never ran.
`Item` was never the problem, and neither was the index.

### Section 4.2 was already implemented, with one real gap.

`lookup` on an absent id returns `Item 999999999 not found.`, and `batch_lookup` already kept the
good rows: a two-id call with one bad id returned `1/2 found` plus the found row. The gap was that it
reported a count and not *which* id was missing, so a partial answer still forced a re-probe.

### Section 4.1 is valid, and is now fixed for all 60 tools.

The cause of the opacity is not in any individual tool. The .NET MCP SDK appends a reason only when
the exception was an `McpException`; argument binding throws something else, so every binding failure
on every tool collapsed to the bare string. Two commits:

- `692e781` (refined by `959a478`) validates the supplied argument names against each tool's own
  published input schema before the call is dispatched. The reported call now answers:

  ```
  lookup: unknown parameter 'entity' (did you mean 'entityType'?); missing required parameter
  'entityType'. Accepted: entityType (required), id (required), huntingZoneId (optional).
  ```

  When the arguments *do* match the schema and the call still fails, the reply now says so
  explicitly and echoes the call, so "bad call" and "server defect" are distinguishable and a
  pointless retry is ruled out. That covers rows 2 and 4 of the section 2 table; row 1 was already
  covered by the not-found result, and row 3 by `list_entity_types` (`files` column) plus
  `datasheet_freshness`.

- `7951680` makes `batch_lookup` name the ids it did not find:

  ```
  Batch lookup: 1/3 found in Item
  name|displayName
  eventItem|Древний свиток
  notFound: 999999998,999999999
  ```

### Worth knowing: an unknown parameter used to be silently ignored.

The schema validation immediately caught a latent defect in this server's own test suite: a call
passing `filter` where the tool takes `nameFilter`. The SDK dropped the unknown argument and returned
the **unfiltered** result, which the assertion then passed on by coincidence. That failure mode is
strictly worse than the one reported here, because it returns plausible wrong data instead of an
error. It is now an error naming the parameter.

### Action for the caller

Re-probe with `entityType`. If `lookup` still fails after `.mcp/` is redeployed, the message will now
name the cause.
