# Zone 436 — Karascha's Lair Dungeon Migration

## Context

Zone 436 (continent 9036) is the Karascha's Lair dungeon, reached at the climax of the Island of Dawn story arc via the "Dark Revelations" quest (id=1316). In v92 the dungeon was repurposed for lv65 endgame content, breaking IoD quest progression. This document covers the full migration back to v31 state.

Zone 436 was not part of the original IoD migration scope — it was added after Phase 1–3 were completed for zones 13, 64, 213, 313, 364, and 416.

---

## Constraints

1. **No DSL sync.** All migration steps must be full file replacement or surgical XML edits. DSL sync is prohibited for this dungeon migration.
2. **Both v31 paths are required.** Do not begin any migration step without confirming both `v31_server_datasheet` and `v31_client_datacenter` are accessible.
3. **Validate after each phase.** Compare migrated content against v31 source using file diffs or MCP tools before moving to the next phase.

---

## Prerequisites

Confirm the following paths are accessible before starting. These are documented in `assessment.md` and should be added to `.references` as `v31_server_datasheet` and `v31_client_datacenter` if not already present.

| Key | Path |
|-----|------|
| `v31_server_datasheet` | `Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet` |
| `v31_client_datacenter` | `Z:\tera pserver\v31.04\client-dc_v31\DataCenter_Final_EUR_v31` |
| `server_datasheet` (v92) | from `.references` |
| `client_datacenter` (v92) | from `.references` |

**Gate check — run before proceeding:**

```bash
ls "Z:/tera pserver/v31.04/TERAServer/Executable/Bin/Datasheet/DungeonData_9036.xml"
ls "Z:/tera pserver/v31.04/client-dc_v31/DataCenter_Final_EUR_v31/NpcData/NpcData-00209.xml"
```

Both files must exist. If either is missing, stop and restore v31 access before continuing.

---

## Phase 1 — Server Migration

**Status: PENDING**

### Files copied from v31 → v92 (full file replacement)

Source: `<v31_server_datasheet>/`
Target: `<server_datasheet>/`

| Source File | Target File | Notes |
|-------------|-------------|-------|
| `AIData_436.xml` | `AIData_436.xml` | |
| `ActiveMove_436.xml` | `ActiveMove_436.xml` | |
| `DungeonData_9036.xml` | `DungeonData_9036.xml` | **Critical** — v92 had `levelOver="65"`; v31 has `levelOver="9"` with IoD quest conditions |
| `DynamicSpawn_436.xml` | `DynamicSpawn_436.xml` | |
| `FormationData_436.xml` | `FormationData_436.xml` | |
| `NpcData_436.xml` | `NpcData_436.xml` | |
| `NpcSkillData_436.xml` | `NpcSkillData_436.xml` | |
| `TerritoryData_436.xml` | `TerritoryData_436.xml` | |
| `VillagerData/04360000001010.condition` | `VillagerData/04360000001010.condition` | |
| `VillagerData/04360000001030.condition` | `VillagerData/04360000001030.condition` | |
| `VillagerData/04360000001501.condition` | `VillagerData/04360000001501.condition` | |

### v92-only server files — kept as-is

These files have no v31 equivalent and must not be removed or overwritten.

| File | Reason |
|------|--------|
| `VillagerData/04360000001502.condition` | NPC 1502 "Dimensional Magic Stone" — v92 teleportal addition |
| `VillagerData/04360000008001.condition` | NPC 8001 "Joel" — v92 story scene NPC |
| `VillagerData/04360000008002.condition` | NPC 8002 "Jowyn Rionas" — v92 story scene NPC |
| `VillagerDialog/VillagerDialog_436.xml` | v92-only server dialog file; covers all zone 436 NPCs including v92 additions |

### Phase 1 Validation

```bash
# 1. Confirm DungeonData level requirement is correct
grep "levelOver" "D:/dev/mmogate/tera92/server/Datasheet/DungeonData_9036.xml"
# Expected: value="9"

# 2. Confirm v31 quest conditions are present
grep -E "progressQuest|completeQuest" "D:/dev/mmogate/tera92/server/Datasheet/DungeonData_9036.xml"
# Expected: progressQuest value="1316" and/or completeQuest value="1316"

# 3. Diff each copied file against v31 source to confirm clean copy
diff "Z:/tera pserver/v31.04/TERAServer/Executable/Bin/Datasheet/NpcData_436.xml" \
     "D:/dev/mmogate/tera92/server/Datasheet/NpcData_436.xml"
# Expected: no diff (or only whitespace)
```

MCP check (once server share is updated):
- `mcp__datasheet-v92__audit_zone_spawns` for zone 436 — NPC count and template IDs should match v31

---

## Phase 2 — Client DC Migration

**Status: PENDING**

### Rules for this phase

- **Full file replacement** is used when the v92 shard contains exclusively zone 436 data. The v31 shard is copied and renamed to the v92 shard filename.
- **Surgical XML merge** is used when the v92 shard contains multiple zones or mixed content. Only zone 436 entries are extracted from v31 and written into the v92 shard.

### Step 2a — NpcData (no action required)

**Status: COMPLETE — no changes needed.**

Investigation (2026-04-19): The v92 client DC shard NpcData-00212 already contains the exact same 22 NPC template IDs referenced by the v31 server NpcData_436.xml. The NPC templates for this dungeon were not changed in v92. The v92 shard is in v92-compliant format; the v31 shard uses an older schema (missing attributes required by v92 XSD) and cannot be used as a direct replacement.

Validation check performed:
```bash
# Template IDs in v92 NpcData-00212 and v31 server NpcData_436.xml both resolve to:
# ['1001','1002','1010','1011','1012','1030','1101','1501','1502',
#  '4000','4001','4002','8001','8002','8003','8004','8005','8006',
#  '8007','8008','8009','8010']
```

### Step 2b — TerritoryData (no action required)

**Status: COMPLETE — no changes needed.**

Investigation (2026-04-19): The v92 TerritoryData-00218 contains a single zone 436 territory entry (`id=43600010`) in v92-compliant format. The v31 shard uses an older schema (`desc`-based structure with `TerritoryList` children) that the v92 packer rejects. The territory definition represents the same physical zone and requires no content change.

### Step 2c — VillagerDialog (no action required)

**Status: COMPLETE — no changes needed.**

Investigation (2026-04-19) found:
- v92 shard 06090 already contains `villagerId=1010 huntingZoneId=436` — byte-for-byte identical to v31 shard 05218
- v92 shard 06091 already contains `villagerId=1030 huntingZoneId=436` — byte-for-byte identical to v31 shard 05219
- v92 shards 06092–06095 contain empty stubs (`id=1, endSocial` only) with no zone identifier, matching the same stub pattern in v31 shard 05220
- NPC 1501 does not have a separate VillagerDialog entry in either version; it is covered by the condition file only
- NPCs 1502, 8001, 8002 are v92-only additions and are not referenced in VillagerDialog shards (they use the VillagerData condition files instead)

No merge required.

---

## Phase 3 — Pack and Push

After Phase 2 is validated, pack the client DC and push the server datasheet:

```bash
# Pack client DC
/deploy-patch   # (no patch number — packs and pushes current state)
```

Or manually via the deploy pipeline documented in `tools/migrate/README.md`.

---

## Phase 4 — Functional Validation

### Server-side checks (MCP)

- `mcp__datasheet-v92__audit_zone_spawns` zone 436: verify NPC population
- `mcp__datasheet-v92__lookup` DungeonData continent 9036: confirm `levelOver="9"`, `progressQuest value="1316"`
- Cross-reference NPC template IDs in server NpcData_436.xml against client DC NpcData-00212.xml — all server template IDs must have a client template record

### In-game functional checks

- Character with quest 1316 "Dark Revelations" active can enter the dungeon (no level gate, no wrong-quest block)
- Zone 436 NPCs are visible with correct models
- Story sequence inside dungeon triggers correctly
- Dungeon exit / return to IoD world works

### Diff-based sanity checks

```bash
# Server DungeonData — confirm v31 match
diff "Z:/tera pserver/v31.04/TERAServer/Executable/Bin/Datasheet/DungeonData_9036.xml" \
     "D:/dev/mmogate/tera92/server/Datasheet/DungeonData_9036.xml"

# Client NpcData shard — confirm v31 match
diff "Z:/tera pserver/v31.04/client-dc_v31/DataCenter_Final_EUR_v31/NpcData/NpcData-00209.xml" \
     "D:/dev/mmogate/tera92/client-dc/DataCenter_Final_EUR/NpcData/NpcData-00212.xml"
```
