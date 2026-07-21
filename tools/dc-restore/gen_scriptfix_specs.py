"""Spawn-script displacement fixes for IoD patch 001.

Pattern (proven via packet capture + S1ActionScripts analysis, 2026-07-19):
a spawn script that ENDS with a move action leaves the client-side visual
actor at the script endpoint while the server entity stays at the spawn
position. If the two diverge, C_NPC_CONTACT on the visual fails the server
range check silently (quest NPC un-interactable; first case: Ramun 213/1038,
script 10023, quest 1327).

Fix: move the server spawn position onto the script endpoint so the authored
choreography ends on the interactable entity.

Sweep scope: IoD zones, villager templates with a nonzero spawnScriptId whose
script ends in a move landing more than DISPLACEMENT_MIN units away from the
spawn position. Emits specs/patches/001/12-iod-spawn-script-fixes.yaml.
Deterministic: sorted iteration, no timestamps.
"""
import math
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DS = Path(r"D:\dev\mmogate\tera92\server\Datasheet")
SPEC = Path(r"D:\dev\mmogate\github\reforged-server-content\reforged\specs\patches\001\12-iod-spawn-script-fixes.yaml")
ZONES = [13, 64, 213, 313, 364, 436]
DISPLACEMENT_MIN = 100.0   # units (cm); ~1m
DISPLACEMENT_MAX = 2000.0  # beyond this the script endpoint is NOT this spawn's
                           # scene (e.g. 213/1124 shares script 10023 with 1038
                           # but lives 6.5km away at the garrison): flag, do not move


def read(p):
    return p.read_text(encoding="utf-8-sig", errors="replace")


def script_endpoints(text):
    """script id -> (x, y, z) of the LAST move action in the script, if any."""
    out = {}
    for m in re.finditer(r'<Script id="(\d+)"[^>]*>(.*?)</Script>', text, re.S):
        moves = re.findall(r'<Action[^>]*type="move"[^>]*pos="([^"]+)"', m.group(2))
        if moves:
            parts = [float(v) for v in moves[-1].replace(" ", "").split(",")[:3]]
            if len(parts) == 3:
                out[int(m.group(1))] = tuple(parts)
    return out


def main():
    endpoints = script_endpoints(read(DS / "S1ActionScripts_Spawn.xml"))

    rows = []
    for zone in ZONES:
        npc_path = DS / f"NpcData_{zone}.xml"
        td_path = DS / f"TerritoryData_{zone}.xml"
        if not npc_path.exists() or not td_path.exists():
            continue
        npcs = read(npc_path)
        scripts = {}
        for m in re.finditer(r'<Template id="(\d+)"[^>]*>', npcs):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
            sid = int(attrs.get("spawnScriptId", "0") or 0)
            if sid and attrs.get("villager") == "true":
                scripts[int(attrs["id"])] = sid

        td = read(td_path)
        group = terr = None
        for m in re.finditer(r"<(TerritoryGroup|Territory|Npc)\b[^>]*>", td):
            tag = m.group(1)
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
            if tag == "TerritoryGroup":
                group = int(attrs["id"])
            elif tag == "Territory":
                terr = int(attrs["id"])
            else:
                tid = int(attrs.get("npcTemplateId", "0") or 0)
                sid = scripts.get(tid)
                if not sid or sid not in endpoints:
                    continue
                pos = [float(v) for v in attrs["pos"].split(",")[:3]]
                end = endpoints[sid]
                dist = math.dist(pos[:2], end[:2])
                if dist > DISPLACEMENT_MIN:
                    row = {
                        "zone": zone, "group": group, "territory": terr,
                        "instance": int(attrs["instanceId"]), "template": tid,
                        "script": sid, "dist": dist, "end": end,
                        "desc": attrs.get("desc", ""),
                        "skip": dist > DISPLACEMENT_MAX,
                    }
                    rows.append(row)

    rows.sort(key=lambda r: (r["zone"], r["instance"]))
    print(f"sweep: {len(rows)} displaced script-ending villager spawn(s)")
    for r in rows:
        tag = "SKIP (beyond max: not this spawn's scene)" if r["skip"] else "FIX"
        print(f"  {tag}: hz {r['zone']} tid {r['template']} inst {r['instance']} "
              f"script {r['script']} displacement {r['dist']:.0f}u -> {r['end']} ({r['desc']})")
    rows = [r for r in rows if not r["skip"]]

    if not rows:
        if SPEC.exists():
            SPEC.unlink()
        print("no spec emitted")
        return

    lines = [
        'spec:',
        '  version: "1.0"',
        '  schema: v92',
        '',
        '# Spawn-script displacement fixes (see gen_scriptfix_specs.py header).',
        '# A spawn script ending in a move strands the client visual away from the',
        '# server entity; C_NPC_CONTACT then fails the server range check silently.',
        '# Fix: server spawn position moved onto the script endpoint so the entrance',
        '# choreography ends on the interactable entity. Packet-capture proven on',
        '# Ramun (213/1038, script 10023, quest 1327), 2026-07-19.',
        '# Server-only in effect: client TerritoryData carries no Npc entries.',
        '',
        'territorySpawns:',
        '  update:',
    ]
    for r in rows:
        x, y, z = r["end"]
        def fmt(v):
            return f"{v:.8f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))
        lines += [
            f'    - huntingZoneId: {r["zone"]}',
            f'      groupId: {r["group"]}',
            f'      territoryId: {r["territory"]}',
            f'      npcInstanceId: {r["instance"]}',
            f'      changes:',
            f'        pos: [{fmt(x)}, {fmt(y)}, {fmt(z)}]',
        ]
    SPEC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {SPEC.name} with {len(rows)} update op(s)")


if __name__ == "__main__":
    main()
