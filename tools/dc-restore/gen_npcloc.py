"""Regenerate client StrSheet_NpcLoc entries for the IoD hunting zones.

The client family StrSheet_NpcLoc is the location registry behind the quest
link/ping/spawn-dot UI: one String per (huntingZoneId, templateId) whose
string value is a pipe-joined list of continentId#x,y,z spawn positions.
The v92 rework regenerated the file for its own IoD roster (HZ 13 mission
NPCs only) and dropped HZ 64/213 entirely, so links in the restored classic
quests resolve to nothing.

This tool rebuilds the entries for the IoD zones from the CURRENT server
TerritoryData (post patch-001 state, which is v31-authoritative under the
classic-restoration doctrine), and merges them into the client file. Two
merge modes:

  Default (replace-by-key): for every (hz, templateId) with at least one
  non-void spawn, emit one String with all spawn positions (continent 13);
  an existing client entry with the SAME key is replaced in place; entries
  for other zones and stale rework-roster keys are left alone.

  Position resolution: a spawn with a real position contributes it directly. A
  spawn stored as the 0,0,0 random-in-fence sentinel (party members and random
  singles) instead contributes the fence centroid of its containing territory,
  matching the representative point the v31 client authored for those spawns.
  No '13#0,0,0' dead link target is ever emitted.

  --prune (replace-by-zone): for the covered IoD zones, EVERY existing client
  key in those zones that the regeneration did not produce is removed as well,
  so the zone contents become exactly the regenerated set. This drops the
  stale v92-only rework-roster keys (per TRACKER map-diff ruling 5). Zones
  outside ZONES are never touched in either mode.

Deterministic and idempotent in both modes: re-running against the same
inputs produces the same client file. Paths resolve from reforged/.references.
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ZONES = [13, 64, 213, 436]
CONTINENT = 13

REFS = Path(__file__).resolve().parents[2] / ".references"


def read_refs():
    refs = {}
    for line in REFS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            refs[k.strip()] = v.strip()
    return refs


def fmt(v) -> str:
    """Format one coordinate like the vendor entries: strip trailing zeros."""
    f = float(v)
    i = int(round(f))
    return str(i) if abs(f - i) < 0.5 else f"{f:.4f}".rstrip("0").rstrip(".")


def is_void_pos(pos: str) -> bool:
    """True when the spawn position is the 0,0,0 random-in-fence sentinel.

    Party members and random-in-fence singles store pos 0,0,0; the engine picks
    a real point inside the containing territory's fence at spawn time. Copying
    0,0,0 verbatim into NpcLoc yields a dead '13#0,0,0' link target.
    """
    try:
        return all(abs(float(v)) < 1e-6 for v in pos.split(","))
    except (ValueError, AttributeError):
        return False


def fence_centroid(territory):
    """Average of the territory's Fence vertices, or None if it has no fence.

    This is the representative point the v31 client authored for random-in-fence
    spawns: one point per territory, shared by every template that spawns there.
    """
    sx = sy = sz = 0.0
    n = 0
    for f in territory.iter("Fence"):
        x, y, z = (float(v) for v in f.get("pos").split(","))
        sx += x
        sy += y
        sz += z
        n += 1
    if n == 0:
        return None
    return sx / n, sy / n, sz / n


def collect(server: Path):
    """(hz, templateId) -> list of 'CONT#x,y,z' strings, spawn order.

    A non-void spawn contributes its own position. A void (0,0,0) spawn instead
    contributes the fence centroid of its containing territory, so a template
    spawning in N territories emits N distinct real points.
    """
    out = {}
    for hz in ZONES:
        p = server / f"TerritoryData_{hz}.xml"
        if not p.exists():
            continue
        root = ET.parse(p).getroot()
        for terr in root.iter("Territory"):
            centroid = None  # resolved lazily; every Npc here shares one territory
            for npc in terr.iter("Npc"):
                if npc.get("voidSpawn") == "true":
                    continue
                pos = npc.get("pos", "")
                if is_void_pos(pos):
                    if centroid is None:
                        centroid = fence_centroid(terr)
                    if centroid is None:
                        continue  # no fence to resolve; drop the dead sentinel
                    x, y, z = centroid
                else:
                    x, y, z = pos.split(",")
                key = (hz, int(npc.get("npcTemplateId")))
                out.setdefault(key, []).append(
                    f"{CONTINENT}#{fmt(x)},{fmt(y)},{fmt(z)}"
                )
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prune",
        action="store_true",
        help="replace-by-zone: also delete existing client keys in the "
             "covered IoD zones that the regeneration did not produce "
             "(drops stale v92-only rework keys). Default OFF (replace-by-key).",
    )
    args = parser.parse_args()

    refs = read_refs()
    server = Path(refs["server_datasheet"])
    client_file = (
        Path(refs["client_datacenter"]) / "StrSheet_NpcLoc" / "StrSheet_NpcLoc-00000.xml"
    )

    entries = collect(server)

    # Guard: no void (0,0,0) sentinel may survive into the emitted registry.
    void_tokens = sum(
        1 for pos in entries.values() for tok in pos
        if is_void_pos(tok.split("#", 1)[1])
    )
    if void_tokens:
        raise SystemExit(f"ERROR: {void_tokens} unresolved 0,0,0 position tokens")

    text = client_file.read_text(encoding="utf-8")

    removed = 0
    if args.prune:
        # Replace-by-zone: drop EVERY existing key in the covered zones, so the
        # zone contents become exactly the regenerated set (stale v92-only keys
        # that the regeneration did not produce are dropped too).
        for hz in ZONES:
            pat = rf'[ \t]*<String string="[^"]*" templateId="\d+" huntingZoneId="{hz}" />\r?\n'
            text, n = re.subn(pat, "", text)
            removed += n
    else:
        # Replace-by-key: drop only the entries for keys we regenerate.
        for (hz, tmpl) in entries:
            pat = rf'[ \t]*<String string="[^"]*" templateId="{tmpl}" huntingZoneId="{hz}" />\r?\n'
            text, n = re.subn(pat, "", text)
            removed += n

    lines = "".join(
        f'    <String string="{"|".join(pos)}" templateId="{tmpl}" huntingZoneId="{hz}" />\n'
        for (hz, tmpl), pos in sorted(entries.items())
    )
    text = text.replace("</StrSheet_NpcLoc>", lines + "</StrSheet_NpcLoc>")

    client_file.write_text(text, encoding="utf-8")
    per_hz = {}
    for (hz, _t) in entries:
        per_hz[hz] = per_hz.get(hz, 0) + 1
    mode = "prune (replace-by-zone)" if args.prune else "replace-by-key"
    print(f"[{mode}] removed {removed} existing entries; wrote {len(entries)} entries "
          f"(0 void 0,0,0 tokens): "
          + ", ".join(f"hz{hz}={n}" for hz, n in sorted(per_hz.items())))


if __name__ == "__main__":
    sys.exit(main())
