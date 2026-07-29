"""Generate a DSL spec that rebuilds the StrSheet_NpcLoc entries for the IoD zones.

StrSheet_NpcLoc is the location registry behind the quest link/ping/spawn-dot
UI: one String per (huntingZoneId, templateId) whose string value is a
pipe-joined list of continentId#x,y,z spawn positions. The v92 rework
regenerated the file for its own IoD roster (HZ 13 mission NPCs only) and
dropped HZ 64/213 entirely, so links in the restored classic quests resolve
to nothing.

This tool derives the correct entries from the CURRENT server TerritoryData
(v31-authoritative under the classic-restoration doctrine) and EMITS A SPEC.
It does not write any datasheet itself.

That indirection is the point. Until 2026-07-28 this tool wrote the CLIENT
shard directly, which put its output in the one tree that is not reproducible
from specs: a patch revert-and-replay regenerated the server tree and synced
it, but could not regenerate something that had never been server-side. A full
patch 002 replay silently dropped this registry, and the migrate run reported
0 failed and 0 warnings while it happened. Emitting a spec puts the registry
back inside the pipeline, where `migrate --patch NNN` reproduces it and the
normal server-to-client sync propagates it.

Derivation stays here because it is a genuine batch operation over spawn
geometry; authoring goes through the DSL. Entity: `npcLocStrings`, keyed on
the PAIR (huntingZoneId, templateId).

Two merge modes:

  Default (replace-by-key): for every (hz, templateId) with at least one
  non-void spawn, emit one upsert with all spawn positions (continent 13).
  Rows for other zones and stale rework-roster keys are left alone.

  Position resolution: a spawn with a real position contributes it directly. A
  spawn stored as the 0,0,0 random-in-fence sentinel (party members and random
  singles) instead contributes the fence centroid of its containing territory,
  matching the representative point the v31 client authored for those spawns.
  No '13#0,0,0' dead link target is ever emitted.

  --prune (replace-by-zone): for the covered IoD zones, EVERY existing key in
  those zones that the regeneration did not produce also gets a delete op, so
  the zone contents become exactly the regenerated set. This drops the stale
  v92-only rework-roster keys (per TRACKER map-diff ruling 5). Zones outside
  ZONES are never touched in either mode. Prune reads the CURRENT server
  StrSheet_NpcLoc.xml to learn which keys exist.

Deterministic and idempotent in both modes: re-running against the same inputs
produces the same spec, and the spec is upsert-based so applying it repeatedly
is a no-op. Paths resolve from reforged/.references.

Usage:
    python gen_npcloc.py --out reforged/specs/patches/003/NN-iod-npcloc-registry.yaml --prune
"""

import argparse
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
    """(hz, templateId) -> list of (x, y, z) formatted coordinate triples, spawn order.

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
                out.setdefault(key, []).append((fmt(x), fmt(y), fmt(z)))
    return out


def existing_keys(server: Path):
    """(hz, templateId) pairs already present in the server registry, ZONES only."""
    p = server / "StrSheet_NpcLoc.xml"
    if not p.exists():
        return set()
    root = ET.parse(p).getroot()
    keys = set()
    for s in root.iter("String"):
        hz = s.get("huntingZoneId")
        tmpl = s.get("templateId")
        if hz is None or tmpl is None:
            continue
        if int(hz) in ZONES:
            keys.add((int(hz), int(tmpl)))
    return keys


def render_spec(entries, deletes, mode: str) -> str:
    """Emit the npcLocStrings spec. Upserts first, then deletes."""
    out = [
        "# StrSheet_NpcLoc quest-marker registry for the Island of Dawn zones.",
        "#",
        "# GENERATED FILE. Do not hand-edit: regenerate with",
        "#   python reforged/tools/dc-restore/gen_npcloc.py --out <this file>"
        + (" --prune" if mode.startswith("prune") else ""),
        "#",
        "# Derived from the CURRENT server TerritoryData, which is v31-authoritative",
        "# under the classic-restoration doctrine. One row per (huntingZoneId,",
        "# templateId); the value is the pipe-joined list of that template's spawn",
        "# positions on continent 13. A spawn stored as the 0,0,0 random-in-fence",
        "# sentinel contributes its territory's fence centroid instead, so no dead",
        f"# '13#0,0,0' link target is ever emitted. Mode: {mode}.",
        "#",
        "# Waypoints use the TYPED form (`continent` + `markers`) rather than a packed",
        "# `string`. Both are supported and the raw form is what the DSL docs call the",
        "# generator default, but a packed payload runs to thousands of characters, so a",
        "# spawn change shows up as one enormous changed line. Typed markers diff one",
        "# waypoint at a time, which is what this project's regression-diff discipline",
        "# needs. `markers` replaces the whole list and is sequence-exact, so repeated",
        "# waypoints are preserved as written.",
        "",
        'spec:',
        '  version: "1.0"',
        '  schema: v92',
        "",
        "npcLocStrings:",
        "  upsert:",
    ]
    for (hz, tmpl), pos in sorted(entries.items()):
        out.append(f"    - huntingZoneId: {hz}")
        out.append(f"      templateId: {tmpl}")
        out.append(f"      continent: {CONTINENT}")
        out.append("      markers:")
        for x, y, z in pos:
            out.append(f"        - [{x}, {y}, {z}]")
    if deletes:
        out.append("")
        out.append("  # Stale keys in the covered zones that the regeneration did not")
        out.append("  # produce (v92-only rework-roster leftovers).")
        out.append("  delete:")
        for hz, tmpl in sorted(deletes):
            out.append(f"    - huntingZoneId: {hz}")
            out.append(f"      templateId: {tmpl}")
    out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        required=True,
        help="path of the spec file to write",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="replace-by-zone: also emit delete ops for existing keys in the "
             "covered IoD zones that the regeneration did not produce "
             "(drops stale v92-only rework keys). Default OFF (replace-by-key).",
    )
    args = parser.parse_args()

    refs = read_refs()
    server = Path(refs["server_datasheet"])

    entries = collect(server)

    # Guard: no void (0,0,0) sentinel may survive into the emitted registry.
    void_tokens = sum(
        1 for pos in entries.values() for tok in pos
        if is_void_pos(",".join(tok))
    )
    if void_tokens:
        raise SystemExit(f"ERROR: {void_tokens} unresolved 0,0,0 position tokens")

    deletes = (existing_keys(server) - set(entries)) if args.prune else set()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "prune (replace-by-zone)" if args.prune else "replace-by-key"
    out_path.write_text(render_spec(entries, deletes, mode), encoding="utf-8", newline="\n")

    per_hz = {}
    for (hz, _t) in entries:
        per_hz[hz] = per_hz.get(hz, 0) + 1
    print(f"[{mode}] wrote {out_path}: {len(entries)} upsert(s), {len(deletes)} delete(s) "
          f"(0 void 0,0,0 tokens): "
          + ", ".join(f"hz{hz}={n}" for hz, n in sorted(per_hz.items())))


if __name__ == "__main__":
    sys.exit(main())
