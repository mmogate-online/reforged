# Datasheet MCP: no NPC profile tool, no spawn-footprint filter, no coordinate-to-section lookup (2026-07-25)

Filed from a real content defect that the MCP could have caught in one call and instead took an
afternoon of hand-rolled Python. The bug is described first because every request below is scored
against whether it would have surfaced it.

## The defect

Quest 1309 "Acharak Attacks" (Island of Dawn) is a kill-ONE task on named boss `13,1002`, and its
journal string names one place: "Clear out Acharak and his minions from the Tainted Gorge Garrison."

The patch-001 padding wave replicated v17 mob habitat group 1300038 from a roster of
`[5, 901, 1002]`, so four of its twelve fences drew template 1002 at `spawnCount 2`: eight extra
Acharaks in the Mysterious Ruins, about 19,400 units from the garrison, all of them satisfying the
kill-one task.

The trap is an identity split inside one template:

| Source | Value for `13,1002` |
|---|---|
| `NpcData_13.xml` `name` | `오칸` (Orcan) |
| `StrSheet_Creature` `displayName` | `Acharak` |
| `TerritoryData_13.xml` spawn `desc` | `오칸` |

Two of the three say "generic Orcan". The one the player reads says "Acharak". A generator that
places by roster and writes `desc` from `NpcData.name` produces data that looks correct in every
field an author would inspect, and wrong in the only field a player sees.

Fixed by `specs/patches/002/21-iod-acharak-ruins-cleanup.yaml`, retargeting the four spawns to
template 901, which shares `shapeId 300650` / `basicActionId 3006500` / `aiid 31` with 1002 and is
already in the same group.

## What the investigation actually cost

Roughly 11 of ~40 tool calls were overhead. The MCP-attributable part:

1. **`audit_zone_spawns(huntingZoneIds="[13]")` overflowed.** 742 spawn entries, 97,483 characters
   across 797 lines, over the token ceiling, spilled to a file that then had to be grepped. The
   question being asked was "where does template 1002 spawn", which is 8 rows.
2. **No way to ask what a template is.** Establishing the `name` vs `displayName` split needed a
   raw regex over `NpcData_13.xml` plus a `lookup` call, and establishing that 901 was a safe
   substitute needed a second pass comparing `shapeId` / `basicActionId` / `aiid` across five
   templates.
3. **No coordinate-to-section resolution.** Proving the four spawns are in "Mysterious Ruins" and
   the two v31 ones are in "Tainted Gorge Garrison" required hand-rolled point-in-polygon against
   the `Section` fences in `AreaData_13_ATW_Death_P.xml`, joined to `StrSheet_Region` for the
   English names. `resolve_region` was checked first and takes names or ids, not positions.

## Request 1 (minimum useful): `npcTemplateId` filter on `audit_zone_spawns`

Add an optional `npcTemplateId` parameter. With it, the whole of item 1 above becomes one call
returning 8 rows instead of 742.

The reverse-lookup pattern already exists in this server's vocabulary (`reverse_lookup_shop_npcs`),
so this is consistent rather than novel. A `groupId` filter would be a cheap companion, since
habitat work is almost always group-scoped.

## Request 2 (highest value): a `profile_npc` tool

`profile_item(itemId)` exists and is described as combining multiple lookups into one response.
There is no NPC equivalent, and NPC questions are the bulk of restoration work.

Proposed: `profile_npc(huntingZoneId, templateId)` returning

- **Identity**, with `name` and `displayName` shown together and **explicitly flagged when they
  diverge in kind** (not merely a translation of each other). This single line is the defect above.
- **Spawn footprint**: every group and territory the template spawns in, with group `desc`, spawn
  counts, and the AreaData section each territory falls in. This is the "10 mobs across 2 sections,
  one of which is not where the quest points" line.
- **Quest links**: every quest referencing the template as a `사냥Task` monster, `방문Task` NPC, or
  collect target, with kill counts and enabled / sentinel-disabled state. This is the
  "kill count 1, and it is live" line.
- **Sibling templates sharing `shapeId`**, with their `playStyle`, `level` and `parentId`. This is
  the fix, handed over instead of derived: template 901 is the same creature without the boss
  profile.

Every one of those four sections was reconstructed by hand this session. Together they are the
entire diagnosis.

Two secondary uses worth designing for:

- **Named-unique audit.** "Which templates with a boss-ish `playStyle` spawn outside their named
  group" is the generalised form of this bug. A footprint section makes it answerable.
- **Substitute selection.** Any spawn edit that swaps a template needs a same-model candidate. The
  `shapeId` sibling list is that query.

## Request 3 (nice to have): `resolve_position`

`resolve_position(continentId, x, y)` returning the containing `Section` id, `nameId`, English
name from `StrSheet_Region`, and the parent Area.

Needed by anything that places, audits, or explains a spawn position. `resolve_region` covers the
name-to-zone direction; this is the missing inverse. The `z` coordinate can be ignored (the section
fences are 2D polygons with `addMaxZ` / `subtractMinZ` bands).

## Noted, but probably not MCP's job

- **Cross-era spawn diffing.** "Template X's footprint in v31 versus v92" is the core operation of
  the classic-restoration doctrine, and it was hand-rolled twice this session (once for the named
  roster, once as a sweep over all 27 HZ-13 quest-target templates). `compare` is same-server,
  two ids, one entity type, so it does not reach this. Since the MCP servers are deliberately
  per-era and read-only, a cross-server diff sits awkwardly in that architecture; this is probably
  a `tools/dc-restore/` script instead. Recording it here so the boundary is a decision rather
  than an oversight.
- **Client DataCenter families.** The fix was only coherent because `StrSheet_NpcLoc` was
  regenerated: the quest map marker for `13/1002` had grown from the v31 client's 2 waypoints to 6,
  four of them pointing into the ruins. No MCP server can see client data at all, so that half of
  the diagnosis was invisible to tooling. The restoration doctrine makes client-only families
  (`StrSheet_NpcLoc`, `StrSheet_CollectionLoc`, `MapDefineData`) first-class pipeline members, so
  this is structurally the largest gap. Flagged rather than requested, pending a scope decision.

## Scoring

Would `profile_npc(13, 1002)` alone have caught this? Yes, at the moment the padding spec was
authored, and again at review time. The identity flag and the two-section footprint are each
independently sufficient to see it.
