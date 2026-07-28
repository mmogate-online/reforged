# QuestCompensationData client sync

Status: APPLIED 2026-07-26, scoped to zone 13. `config/sync-config.yaml` gained the entity
and `tools/migrate/migrate.py` maps `questCompensations` to it. Patch 002 replayed clean
(68 specs, 9149 ops, 0 failed, 0 warnings) and server/client reward parity for zone 13 is
now measured at 0 divergent quests. NOT yet live-validated: that is the user's step, and
it needs a client pack and install because the fix is client-side data.

The shipped `source_mapping` carries **one pair** (zone 13), not the full 153 below. Zone 13
is the only quest reward table this project has ever modified, so mapping only what we own
keeps a game-wide reward rewrite out of the patch. The full content-verified mapping is
retained below for when another zone's rewards come into scope.

## Why

The quest log shows gold and XP but no reward item, while the NPC accept dialog shows the
full reward and completion pays correctly. Root cause: `QuestCompensationData` is a
**client family as well as a server one**, and we have never synced it.

Evidence chain:

- `S_DIALOG` (accept window) carries a `questRewards` array including `items`, so that
  window is server-fed and always correct.
- `S_QUEST_INFO` (the quest log packet) carries **no** reward fields at all, so the log
  cannot be server-fed.
- The client `Quest` shard carries no reward data either. The only client-side source is
  `QuestCompensationData`, 153 shards, holding `gold`, `exp`, `itemBag` and per-class
  `<Item>` rows.
- `gold` and `exp` are attributes on `CompensationType` and are always present, so they
  always render. `<Item>` rows are class-filtered, so a class with no row in the stale
  client copy shows no item.

Measured divergence on zone 13 alone: 64 item rows exist server-side and not client-side
across 15 quests (all `assassin` / `fighter` / `glaiver`, plus one `engineer` row on 1310);
7 quests are absent from the client table entirely (1353 to 1358 and 1387); and 1380 and
1381 show a stale 5 gold / 50 XP against the server's 150 gold / 2100 XP.

The premise came from the domain KB, which states twice that all compensation entities are
server-only. That is true for CCompensation, ECompensation, FCompensation and ICompensation
(no client folders exist for them) and false for QuestCompensation, the one type with a
client UI panel to feed. Doc corrections are listed at the bottom.

## Strategy choice

`ZoneBased` is semantically correct (the family is zone-partitioned and the server root
carries `huntingZoneId`) but is blocked by two gaps filed as
`docs/dsl-requests/2026-07-26-zonebased-server-path.md`: it cannot read the
`CompensationData/` subdirectory, and auto sequence assignment misaligns because three
server zone files (620, 622, 628) have no client shard and sit mid-ordering.

`SourceMapped` with an explicit mapping avoids both, needs no DSL change, and is
deterministic. Verified bijection: **153 of 153 client shards mapped, 0 unmatched**, with
exactly those 3 server files omitted. Zone 13 maps to shard 00012, confirmed by content.

Only one mapped pair is not a set-identity match, and it is pre-existing content drift, not
a mapping error: server `_615` holds quest 61502 where client shard 00121 holds 61501, with
the other 6 ids identical.

## The entry

Below is the full-coverage form. **What actually shipped is this entry with the
`source_mapping` reduced to the single zone-13 pair**; see the status note at the top. The
rest of the entry (strategy, folders, id attribute, XSD) is identical to what is live in
`config/sync-config.yaml`. Default `merge` (replace) is correct: each server zone file is
authoritative for its shard.

```yaml
  # ===========================================================================
  # QUEST COMPENSATION (REWARD TABLES)
  # ===========================================================================
  # Quest reward tables. NOT server-only, despite the domain KB's blanket claim
  # about compensation families: the client ships 153 QuestCompensationData
  # shards and the QUEST LOG reward panel reads them. The NPC accept dialog is
  # server-fed via S_DIALOG.questRewards, which is why the two disagreed while
  # this family went unsynced. See docs/plans/questcomp-client-sync.md.
  #
  # SourceMapped rather than ZoneBased because ZoneBased cannot reach the
  # CompensationData/ subdirectory (server_path is IdSorted-only) and its auto
  # sequence assignment misaligns: 156 server zone files against 153 client
  # shards, with zones 620/622/628 having no client shard and sitting
  # mid-ordering. Explicit pairs are derived from a content-verified bijection.
  # See docs/dsl-requests/2026-07-26-zonebased-server-path.md.
  QuestCompensationData:
    strategy: SourceMapped
    client_folder: "QuestCompensationData"
    root_element: "QuestCompensationData"
    id_attribute: "questId"
    xsd_file: "QuestCompensationData/QuestCompensationData.xsd"
    source_mapping:
      "CompensationData/QuestCompensationData_1.xml": "QuestCompensationData-00000.xml"
      "CompensationData/QuestCompensationData_10.xml": "QuestCompensationData-00001.xml"
      "CompensationData/QuestCompensationData_100.xml": "QuestCompensationData-00002.xml"
      "CompensationData/QuestCompensationData_101.xml": "QuestCompensationData-00003.xml"
      "CompensationData/QuestCompensationData_1022.xml": "QuestCompensationData-00004.xml"
      "CompensationData/QuestCompensationData_1023.xml": "QuestCompensationData-00005.xml"
      "CompensationData/QuestCompensationData_11.xml": "QuestCompensationData-00006.xml"
      "CompensationData/QuestCompensationData_1183.xml": "QuestCompensationData-00007.xml"
      "CompensationData/QuestCompensationData_12.xml": "QuestCompensationData-00008.xml"
      "CompensationData/QuestCompensationData_121.xml": "QuestCompensationData-00009.xml"
      "CompensationData/QuestCompensationData_122.xml": "QuestCompensationData-00010.xml"
      "CompensationData/QuestCompensationData_123.xml": "QuestCompensationData-00011.xml"
      "CompensationData/QuestCompensationData_13.xml": "QuestCompensationData-00012.xml"
      "CompensationData/QuestCompensationData_15.xml": "QuestCompensationData-00013.xml"
      "CompensationData/QuestCompensationData_151.xml": "QuestCompensationData-00014.xml"
      "CompensationData/QuestCompensationData_16.xml": "QuestCompensationData-00015.xml"
      "CompensationData/QuestCompensationData_17.xml": "QuestCompensationData-00016.xml"
      "CompensationData/QuestCompensationData_172.xml": "QuestCompensationData-00017.xml"
      "CompensationData/QuestCompensationData_18.xml": "QuestCompensationData-00018.xml"
      "CompensationData/QuestCompensationData_181.xml": "QuestCompensationData-00019.xml"
      "CompensationData/QuestCompensationData_182.xml": "QuestCompensationData-00020.xml"
      "CompensationData/QuestCompensationData_183.xml": "QuestCompensationData-00021.xml"
      "CompensationData/QuestCompensationData_19.xml": "QuestCompensationData-00022.xml"
      "CompensationData/QuestCompensationData_191.xml": "QuestCompensationData-00023.xml"
      "CompensationData/QuestCompensationData_2.xml": "QuestCompensationData-00024.xml"
      "CompensationData/QuestCompensationData_20.xml": "QuestCompensationData-00025.xml"
      "CompensationData/QuestCompensationData_2000.xml": "QuestCompensationData-00026.xml"
      "CompensationData/QuestCompensationData_2001.xml": "QuestCompensationData-00027.xml"
      "CompensationData/QuestCompensationData_2002.xml": "QuestCompensationData-00028.xml"
      "CompensationData/QuestCompensationData_2003.xml": "QuestCompensationData-00029.xml"
      "CompensationData/QuestCompensationData_21.xml": "QuestCompensationData-00030.xml"
      "CompensationData/QuestCompensationData_213.xml": "QuestCompensationData-00031.xml"
      "CompensationData/QuestCompensationData_22.xml": "QuestCompensationData-00032.xml"
      "CompensationData/QuestCompensationData_23.xml": "QuestCompensationData-00033.xml"
      "CompensationData/QuestCompensationData_24.xml": "QuestCompensationData-00034.xml"
      "CompensationData/QuestCompensationData_25.xml": "QuestCompensationData-00035.xml"
      "CompensationData/QuestCompensationData_26.xml": "QuestCompensationData-00036.xml"
      "CompensationData/QuestCompensationData_27.xml": "QuestCompensationData-00037.xml"
      "CompensationData/QuestCompensationData_28.xml": "QuestCompensationData-00038.xml"
      "CompensationData/QuestCompensationData_29.xml": "QuestCompensationData-00039.xml"
      "CompensationData/QuestCompensationData_3.xml": "QuestCompensationData-00040.xml"
      "CompensationData/QuestCompensationData_30.xml": "QuestCompensationData-00041.xml"
      "CompensationData/QuestCompensationData_3023.xml": "QuestCompensationData-00042.xml"
      "CompensationData/QuestCompensationData_3024.xml": "QuestCompensationData-00043.xml"
      "CompensationData/QuestCompensationData_3025.xml": "QuestCompensationData-00044.xml"
      "CompensationData/QuestCompensationData_3027.xml": "QuestCompensationData-00045.xml"
      "CompensationData/QuestCompensationData_31.xml": "QuestCompensationData-00046.xml"
      "CompensationData/QuestCompensationData_3101.xml": "QuestCompensationData-00047.xml"
      "CompensationData/QuestCompensationData_32.xml": "QuestCompensationData-00048.xml"
      "CompensationData/QuestCompensationData_33.xml": "QuestCompensationData-00049.xml"
      "CompensationData/QuestCompensationData_34.xml": "QuestCompensationData-00050.xml"
      "CompensationData/QuestCompensationData_35.xml": "QuestCompensationData-00051.xml"
      "CompensationData/QuestCompensationData_36.xml": "QuestCompensationData-00052.xml"
      "CompensationData/QuestCompensationData_37.xml": "QuestCompensationData-00053.xml"
      "CompensationData/QuestCompensationData_38.xml": "QuestCompensationData-00054.xml"
      "CompensationData/QuestCompensationData_39.xml": "QuestCompensationData-00055.xml"
      "CompensationData/QuestCompensationData_4.xml": "QuestCompensationData-00056.xml"
      "CompensationData/QuestCompensationData_40.xml": "QuestCompensationData-00057.xml"
      "CompensationData/QuestCompensationData_41.xml": "QuestCompensationData-00058.xml"
      "CompensationData/QuestCompensationData_411.xml": "QuestCompensationData-00059.xml"
      "CompensationData/QuestCompensationData_415.xml": "QuestCompensationData-00060.xml"
      "CompensationData/QuestCompensationData_42.xml": "QuestCompensationData-00061.xml"
      "CompensationData/QuestCompensationData_424.xml": "QuestCompensationData-00062.xml"
      "CompensationData/QuestCompensationData_425.xml": "QuestCompensationData-00063.xml"
      "CompensationData/QuestCompensationData_426.xml": "QuestCompensationData-00064.xml"
      "CompensationData/QuestCompensationData_43.xml": "QuestCompensationData-00065.xml"
      "CompensationData/QuestCompensationData_431.xml": "QuestCompensationData-00066.xml"
      "CompensationData/QuestCompensationData_432.xml": "QuestCompensationData-00067.xml"
      "CompensationData/QuestCompensationData_433.xml": "QuestCompensationData-00068.xml"
      "CompensationData/QuestCompensationData_44.xml": "QuestCompensationData-00069.xml"
      "CompensationData/QuestCompensationData_45.xml": "QuestCompensationData-00070.xml"
      "CompensationData/QuestCompensationData_453.xml": "QuestCompensationData-00071.xml"
      "CompensationData/QuestCompensationData_46.xml": "QuestCompensationData-00072.xml"
      "CompensationData/QuestCompensationData_469.xml": "QuestCompensationData-00073.xml"
      "CompensationData/QuestCompensationData_47.xml": "QuestCompensationData-00074.xml"
      "CompensationData/QuestCompensationData_471.xml": "QuestCompensationData-00075.xml"
      "CompensationData/QuestCompensationData_472.xml": "QuestCompensationData-00076.xml"
      "CompensationData/QuestCompensationData_473.xml": "QuestCompensationData-00077.xml"
      "CompensationData/QuestCompensationData_476.xml": "QuestCompensationData-00078.xml"
      "CompensationData/QuestCompensationData_478.xml": "QuestCompensationData-00079.xml"
      "CompensationData/QuestCompensationData_479.xml": "QuestCompensationData-00080.xml"
      "CompensationData/QuestCompensationData_48.xml": "QuestCompensationData-00081.xml"
      "CompensationData/QuestCompensationData_480.xml": "QuestCompensationData-00082.xml"
      "CompensationData/QuestCompensationData_481.xml": "QuestCompensationData-00083.xml"
      "CompensationData/QuestCompensationData_482.xml": "QuestCompensationData-00084.xml"
      "CompensationData/QuestCompensationData_487.xml": "QuestCompensationData-00085.xml"
      "CompensationData/QuestCompensationData_488.xml": "QuestCompensationData-00086.xml"
      "CompensationData/QuestCompensationData_489.xml": "QuestCompensationData-00087.xml"
      "CompensationData/QuestCompensationData_49.xml": "QuestCompensationData-00088.xml"
      "CompensationData/QuestCompensationData_493.xml": "QuestCompensationData-00089.xml"
      "CompensationData/QuestCompensationData_494.xml": "QuestCompensationData-00090.xml"
      "CompensationData/QuestCompensationData_5.xml": "QuestCompensationData-00091.xml"
      "CompensationData/QuestCompensationData_50.xml": "QuestCompensationData-00092.xml"
      "CompensationData/QuestCompensationData_505.xml": "QuestCompensationData-00093.xml"
      "CompensationData/QuestCompensationData_506.xml": "QuestCompensationData-00094.xml"
      "CompensationData/QuestCompensationData_51.xml": "QuestCompensationData-00095.xml"
      "CompensationData/QuestCompensationData_510.xml": "QuestCompensationData-00096.xml"
      "CompensationData/QuestCompensationData_52.xml": "QuestCompensationData-00097.xml"
      "CompensationData/QuestCompensationData_528.xml": "QuestCompensationData-00098.xml"
      "CompensationData/QuestCompensationData_53.xml": "QuestCompensationData-00099.xml"
      "CompensationData/QuestCompensationData_54.xml": "QuestCompensationData-00100.xml"
      "CompensationData/QuestCompensationData_55.xml": "QuestCompensationData-00101.xml"
      "CompensationData/QuestCompensationData_550.xml": "QuestCompensationData-00102.xml"
      "CompensationData/QuestCompensationData_56.xml": "QuestCompensationData-00103.xml"
      "CompensationData/QuestCompensationData_57.xml": "QuestCompensationData-00104.xml"
      "CompensationData/QuestCompensationData_599.xml": "QuestCompensationData-00105.xml"
      "CompensationData/QuestCompensationData_6.xml": "QuestCompensationData-00106.xml"
      "CompensationData/QuestCompensationData_60.xml": "QuestCompensationData-00107.xml"
      "CompensationData/QuestCompensationData_601.xml": "QuestCompensationData-00108.xml"
      "CompensationData/QuestCompensationData_602.xml": "QuestCompensationData-00109.xml"
      "CompensationData/QuestCompensationData_603.xml": "QuestCompensationData-00110.xml"
      "CompensationData/QuestCompensationData_604.xml": "QuestCompensationData-00111.xml"
      "CompensationData/QuestCompensationData_605.xml": "QuestCompensationData-00112.xml"
      "CompensationData/QuestCompensationData_606.xml": "QuestCompensationData-00113.xml"
      "CompensationData/QuestCompensationData_607.xml": "QuestCompensationData-00114.xml"
      "CompensationData/QuestCompensationData_608.xml": "QuestCompensationData-00115.xml"
      "CompensationData/QuestCompensationData_609.xml": "QuestCompensationData-00116.xml"
      "CompensationData/QuestCompensationData_61.xml": "QuestCompensationData-00117.xml"
      "CompensationData/QuestCompensationData_612.xml": "QuestCompensationData-00118.xml"
      "CompensationData/QuestCompensationData_613.xml": "QuestCompensationData-00119.xml"
      "CompensationData/QuestCompensationData_614.xml": "QuestCompensationData-00120.xml"
      "CompensationData/QuestCompensationData_615.xml": "QuestCompensationData-00121.xml"
      "CompensationData/QuestCompensationData_616.xml": "QuestCompensationData-00122.xml"
      "CompensationData/QuestCompensationData_617.xml": "QuestCompensationData-00123.xml"
      "CompensationData/QuestCompensationData_618.xml": "QuestCompensationData-00124.xml"
      "CompensationData/QuestCompensationData_619.xml": "QuestCompensationData-00125.xml"
      "CompensationData/QuestCompensationData_63.xml": "QuestCompensationData-00126.xml"
      "CompensationData/QuestCompensationData_64.xml": "QuestCompensationData-00127.xml"
      "CompensationData/QuestCompensationData_7.xml": "QuestCompensationData-00128.xml"
      "CompensationData/QuestCompensationData_701.xml": "QuestCompensationData-00129.xml"
      "CompensationData/QuestCompensationData_702.xml": "QuestCompensationData-00130.xml"
      "CompensationData/QuestCompensationData_711.xml": "QuestCompensationData-00131.xml"
      "CompensationData/QuestCompensationData_72.xml": "QuestCompensationData-00132.xml"
      "CompensationData/QuestCompensationData_743.xml": "QuestCompensationData-00133.xml"
      "CompensationData/QuestCompensationData_750.xml": "QuestCompensationData-00134.xml"
      "CompensationData/QuestCompensationData_766.xml": "QuestCompensationData-00135.xml"
      "CompensationData/QuestCompensationData_780.xml": "QuestCompensationData-00136.xml"
      "CompensationData/QuestCompensationData_8.xml": "QuestCompensationData-00137.xml"
      "CompensationData/QuestCompensationData_801.xml": "QuestCompensationData-00138.xml"
      "CompensationData/QuestCompensationData_808.xml": "QuestCompensationData-00139.xml"
      "CompensationData/QuestCompensationData_809.xml": "QuestCompensationData-00140.xml"
      "CompensationData/QuestCompensationData_810.xml": "QuestCompensationData-00141.xml"
      "CompensationData/QuestCompensationData_811.xml": "QuestCompensationData-00142.xml"
      "CompensationData/QuestCompensationData_813.xml": "QuestCompensationData-00143.xml"
      "CompensationData/QuestCompensationData_814.xml": "QuestCompensationData-00144.xml"
      "CompensationData/QuestCompensationData_822.xml": "QuestCompensationData-00145.xml"
      "CompensationData/QuestCompensationData_84.xml": "QuestCompensationData-00146.xml"
      "CompensationData/QuestCompensationData_87.xml": "QuestCompensationData-00147.xml"
      "CompensationData/QuestCompensationData_9.xml": "QuestCompensationData-00148.xml"
      "CompensationData/QuestCompensationData_901.xml": "QuestCompensationData-00149.xml"
      "CompensationData/QuestCompensationData_950.xml": "QuestCompensationData-00150.xml"
      "CompensationData/QuestCompensationData_99.xml": "QuestCompensationData-00151.xml"
      "CompensationData/QuestCompensationData_999.xml": "QuestCompensationData-00152.xml"
```

Confirm at dry-run time whether `SourceMapped` also requires a `server_files` list. The
Entity Properties table lists it for SourceMapped, but our existing `StrSheet_Quest` entry
omits it, so it appears optional when `source_mapping` is explicit.

## The migrate change

`tools/migrate/migrate.py`, `ENTITY_SYNC_MAP`:

```python
-    "questCompensations": None, # QuestCompensationData: server-only
+    "questCompensations": "QuestCompensationData",
```

## XSD surface (checked, no action needed)

The client XSD declares a superset of what the server writes:

| Element | Server attributes used | Client XSD declares |
|---|---|---|
| `CompensationType` | `type`, `exp`, `gold`, `itemBag` | those plus `reputationExp`, `reputationPoint`, `npcGuildId`, `skillPolishingExp`, `memo`, `policyPoint` |
| `Item` | `templateId`, `class`, `quantity` | those plus `race` |

`class` is `xsd:string` with no enumeration, so the class-width trap that forced the
`Quest.xsd` widening does not apply: `assassin`, `fighter` and `glaiver` pass the filter.

The only dropped attribute is `Compensation/@compensationId`, undeclared client-side and
never present in the client shards, so an expected `W602` on it is correct behavior and
matches the client's existing shape.

## Rollout

1. Apply the two changes above.
2. Dry run: `dsl sync --config reforged/config/sync-config.yaml -e QuestCompensationData -d -v`.
   Expect writes confined to shards whose server file changed, and `W602` only on
   `compensationId`.
3. Full patch replay per the patch discipline, not a standalone sync:
   `python reforged/tools/migrate/migrate.py --patch 002 --no-narrow`.
4. Verify zone 13 specifically: client shard `QuestCompensationData-00012.xml` should gain
   the 64 missing item rows, the 7 absent quests (1353 to 1358, 1387), and corrected
   gold and exp on 1380 and 1381.
5. Regression check the rest: no client shard outside the mapped set should change, and no
   mapped shard should lose records (the sync replaces per zone file, and 152 of 153 pairs
   already agree on their record sets).
6. Pack, install, deploy. This is a client-only fix for the display defect, but the server
   leg rides the same patch.
7. Live confirmation belongs to the user. Discriminating checks: a Warrior on 1325 already
   sees the item today (the client has a warrior row); a Ninja, Brawler or Valkyrie does
   not; and any class on 1353 sees no rewards at all, because that quest is missing from
   the client table entirely.

## Documentation corrections this produces

1. `datasheet-domain` `entities/loot-system.md`: the "Server-only" note and rule 6 both
   claim all compensation entities are never synced to the client. Correct for C, E, F and
   I; wrong for QuestCompensation. Route via `/learn` to `update-domain-docs`.
2. `docs/plans/classic-restoration/ZONE-PORT-PLAYBOOK.md` family map: the Rewards row reads
   `server-only` with no client column entry.
3. `tools/migrate/migrate.py`: the inline comment repeats the same claim.
