"""Dungeon reference integrity audit (read-only).

Validates that a dungeon continent's encounter wiring will actually work at
runtime by resolving every DungeonData reference against the PARSED content of
the per-HZ files, never against raw text. Born from the dungeon 9037 incident
(2026-07-21): all classic territory groups were wrapped in one XML comment, so
grep/text-diff reported the data as present while the server loaded nothing.

Checks per dungeon continent:
  1. Continent -> HuntingZone resolution (ContinentData) and DungeonConstraint
     registration.
  2. Every territoryId referenced by DungeonData event tasks resolves to a
     territory the server will LOAD (parsed XML). References that only exist
     inside comment blocks are flagged COMMENT-DISABLED; absent ones MISSING.
  3. Every "hz,templateId" NPC reference in DungeonData, and every
     npcTemplateId spawned by the active territories, exists as a parsed
     NpcData template (same comment-aware classification).
  4. Per-HZ file-set presence (NpcData, TerritoryData, AIData, NpcSkillData).
  5. Comment-disabled census per file (informational warning).

Exit code 1 if any COMMENT-DISABLED or MISSING reference is found.

Usage:
  python reforged/tools/dc-restore/dungeon_audit.py --dungeons 9037
  python reforged/tools/dc-restore/dungeon_audit.py --dungeons 9037,9039,9091
  python reforged/tools/dc-restore/dungeon_audit.py --dungeons 9037 --datasheet <path>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from dclib import (
    find_zone_file,
    iter_local,
    load_references,
    parse_pair,
    parse_root,
    read_text,
)

_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
_TERR_ID = re.compile(r'<Territory\s+id="(\d+)"')
_TPL_ID = re.compile(r'<Template\s+id="(\d+)"')
_TG_ID = re.compile(r'<TerritoryGroup\s+id="(\d+)"')
_INST_ID = re.compile(r'instanceId="(\d+)"')

# DungeonData attributes carrying "hz,id" entity references. The id half is
# polymorphic by event type: an NpcData templateId (talkNpc), a TerritoryData
# Npc instanceId (npcHp / npcDead targets), or a territoryId (enterTerritory).
_NPC_PAIR_ATTRS = ("targetNpcId", "npcId", "uniqueId")


def comment_bodies(text: str) -> str:
    return "\n".join(m.group(1) for m in _COMMENT.finditer(text))


def classify(ref: int, active: set[int], commented: set[int]) -> str:
    if ref in active:
        return "ok"
    if ref in commented:
        return "COMMENT-DISABLED"
    return "MISSING"


class ZoneFiles:
    """Parsed + comment-scanned per-HZ content for one hunting zone."""

    def __init__(self, datasheet: Path, hz: int):
        self.hz = hz
        self.missing_files: list[str] = []
        self.active_territories: set[int] = set()
        self.commented_territories: set[int] = set()
        self.commented_groups: set[int] = set()
        self.active_templates: set[int] = set()
        self.commented_templates: set[int] = set()
        self.active_instances: set[int] = set()     # Npc instanceId in active territories
        self.commented_instances: set[int] = set()
        self.territory_npc_refs: set[int] = set()  # npcTemplateId used by active territories

        terr = find_zone_file(datasheet, "TerritoryData", hz)
        if terr is None:
            self.missing_files.append(f"TerritoryData_{hz}.xml")
        else:
            text = read_text(terr)
            root = parse_root(text)
            for t in iter_local(root, "Territory"):
                tid = t.get("id")
                if tid and tid.isdigit():
                    self.active_territories.add(int(tid))
                for npc in iter_local(t, "Npc"):
                    tpl = npc.get("npcTemplateId")
                    if tpl and tpl.isdigit():
                        self.territory_npc_refs.add(int(tpl))
                    inst = npc.get("instanceId")
                    if inst and inst.isdigit():
                        self.active_instances.add(int(inst))
            dead = comment_bodies(text)
            self.commented_territories = {int(x) for x in _TERR_ID.findall(dead)}
            self.commented_groups = {int(x) for x in _TG_ID.findall(dead)}
            self.commented_instances = {int(x) for x in _INST_ID.findall(dead)}

        npc = find_zone_file(datasheet, "NpcData", hz)
        if npc is None:
            self.missing_files.append(f"NpcData_{hz}.xml")
        else:
            text = read_text(npc)
            root = parse_root(text)
            for tpl in iter_local(root, "Template"):
                tid = tpl.get("id")
                if tid and tid.isdigit():
                    self.active_templates.add(int(tid))
            self.commented_templates = {int(x) for x in _TPL_ID.findall(comment_bodies(text))}

        for family in ("AIData", "NpcSkillData"):
            if find_zone_file(datasheet, family, hz) is None:
                self.missing_files.append(f"{family}_{hz}.xml")


def continent_hzs(datasheet: Path, continent: int) -> list[int]:
    path = datasheet / "ContinentData.xml"
    if not path.is_file():
        return []
    root = parse_root(read_text(path))
    for cont in iter_local(root, "Continent"):
        if cont.get("id") == str(continent):
            return [int(hz.get("id")) for hz in iter_local(cont, "HuntingZone") if hz.get("id")]
    return []


def constraint_active(datasheet: Path, continent: int) -> str:
    path = datasheet / "DungeonConstraint.xml"
    if not path.is_file():
        return "file absent"
    root = parse_root(read_text(path))
    for el in root.iter():
        if el.get("continentId") == str(continent) or (
            el.tag.rsplit("}", 1)[-1] == "Dungeon" and el.get("id") == str(continent)
        ):
            return f"registered (isActive={el.get('isActive', '?')})"
    return "NOT REGISTERED"


def audit_dungeon(datasheet: Path, continent: int) -> list[str]:
    """Audit one dungeon continent. Returns list of failure strings."""
    failures: list[str] = []
    print(f"\n===== Dungeon continent {continent} =====")

    hzs = continent_hzs(datasheet, continent)
    if not hzs:
        failures.append(f"continent {continent} has no HuntingZone in ContinentData.xml")
        print(f"  FAIL: {failures[-1]}")
        return failures
    print(f"  HuntingZones: {hzs}")
    print(f"  DungeonConstraint: {constraint_active(datasheet, continent)}")

    dd_path = datasheet / f"DungeonData_{continent}.xml"
    if not dd_path.is_file():
        print(f"  note: no DungeonData_{continent}.xml (no scripted encounter)")
        dd_root = None
        dd_dead = ""
    else:
        dd_text = read_text(dd_path)
        dd_root = parse_root(dd_text)
        dd_dead = comment_bodies(dd_text)

    zones = {hz: ZoneFiles(datasheet, hz) for hz in hzs}
    default_hz = hzs[0]

    for hz, z in zones.items():
        for f in z.missing_files:
            print(f"  warn: missing file {f}")
        if z.commented_territories or z.commented_templates:
            print(
                f"  warn: HZ {hz} comment-disabled content: "
                f"{len(z.commented_groups)} territory group(s), "
                f"{len(z.commented_territories)} territorie(s), "
                f"{len(z.commented_templates)} npc template(s) "
                f"(not loaded by the server)"
            )

    # --- DungeonData reference resolution (active tree only) ---
    terr_refs: set[tuple[int, int]] = set()
    npc_refs: set[tuple[int, int]] = set()
    if dd_root is not None:
        for el in dd_root.iter():
            tid = el.get("territoryId")
            if tid and tid.isdigit():
                hz = int(el.get("huntingZoneId", default_hz))
                terr_refs.add((hz, int(tid)))
            for attr in _NPC_PAIR_ATTRS:
                pair = parse_pair(el.get(attr))
                if pair:
                    npc_refs.add(pair)

        dead_terr_refs = len(re.findall(r'territoryId="\d+"', dd_dead))
        if dead_terr_refs:
            print(
                f"  note: DungeonData has {dead_terr_refs} territoryId reference(s) inside "
                f"comment blocks (inert; not audited)"
            )

    for hz, tid in sorted(terr_refs):
        z = zones.get(hz)
        if z is None:
            failures.append(f"DungeonData references HZ {hz} not owned by continent {continent}")
            print(f"  FAIL: {failures[-1]}")
            continue
        verdict = classify(tid, z.active_territories, z.commented_territories)
        if verdict != "ok":
            failures.append(f"DungeonData -> territory {hz}/{tid}: {verdict}")
            print(f"  FAIL: {failures[-1]}")
    print(f"  DungeonData territory refs: {len(terr_refs)} checked")

    for hz, ref in sorted(npc_refs):
        z = zones.get(hz)
        if z is None:
            continue  # cross-continent NPC refs (e.g. exit NPCs) are out of scope
        active = z.active_templates | z.active_territories | z.active_instances
        commented = z.commented_templates | z.commented_territories | z.commented_instances
        verdict = classify(ref, active, commented)
        if verdict != "ok":
            failures.append(f"DungeonData -> entity ref {hz}/{ref}: {verdict}")
            print(f"  FAIL: {failures[-1]}")
    print(f"  DungeonData entity refs: {len(npc_refs)} checked")

    # --- Territory -> NpcData template resolution ---
    for hz, z in zones.items():
        for tpl in sorted(z.territory_npc_refs):
            verdict = classify(tpl, z.active_templates, z.commented_templates)
            if verdict != "ok":
                failures.append(f"territory spawn -> npc template {hz}/{tpl}: {verdict}")
                print(f"  FAIL: {failures[-1]}")
        print(f"  HZ {hz}: {len(z.active_territories)} active territorie(s), "
              f"{len(z.territory_npc_refs)} spawned template id(s) checked")

    if not failures:
        print("  PASS: every audited reference resolves to loaded content")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Dungeon reference integrity audit (read-only)")
    ap.add_argument("--dungeons", required=True,
                    help="comma-separated dungeon continent ids (e.g. 9037,9039)")
    ap.add_argument("--datasheet", default=None,
                    help="datasheet root override (default: server_datasheet from .references)")
    args = ap.parse_args()

    if args.datasheet:
        datasheet = Path(args.datasheet)
    else:
        datasheet = Path(load_references()["server_datasheet"])
    if not datasheet.is_dir():
        print(f"error: datasheet dir not found: {datasheet}", file=sys.stderr)
        return 2

    all_failures: list[str] = []
    for token in args.dungeons.split(","):
        all_failures.extend(audit_dungeon(datasheet, int(token.strip())))

    print(f"\n{'FAIL' if all_failures else 'PASS'}: {len(all_failures)} failure(s)")
    return 1 if all_failures else 0


if __name__ == "__main__":
    sys.exit(main())
