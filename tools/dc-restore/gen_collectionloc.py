"""Generate a DSL spec adding missing StrSheet_CollectionLoc waypoints for IoD collections.

The gather-quest map marker reads the family StrSheet_CollectionLoc: one String per
collection (templateId = collection id) whose value is a pipe-joined list of
`continentId#x,y,z` node positions (the collection analog of StrSheet_NpcLoc).
Clicking a gather objective marks those points on the map.

The v92 (and v31) data shipped WITHOUT entries for the tier-1 IoD collections
(Verdra Plant 1, Krymetal Ore 101, Sun Essence 301), so their quest markers never
resolved. This tool projects the IoD node positions from the server
CollectionTerritory_13_* data into continent-13 waypoints and emits an upsert for
every continent-13 collection that does not already have a row.

ADD-ONLY, and that is load bearing. Collections that already carry an entry are left
alone, including multi-zone ones: `templateId 496` mixes continent 13 and mainland
waypoints, and the DSL's own docs call it the single row of the 177 shipped that spans
continents. Re-deriving it from continent-13 data alone would silently drop its
mainland half. Never widen this tool to upsert rows that already exist.

It EMITS A SPEC and writes no datasheet, neither server nor client.

That indirection is the point. This tool used to write the server file AND the client
shard directly. The client write bypassed the pipeline entirely, putting output in the
one tree that is not reproducible from specs, which is how the sibling registry
(StrSheet_NpcLoc) was silently lost by a patch revert-and-replay on 2026-07-28 with the
migrate run reporting 0 failed and 0 warnings. StrSheet_CollectionLoc is now a
registered sync family (`collectionLocStrings`), so the server file is the source of
truth and the normal server-to-client sync propagates it.

Derivation from node geometry stays here because it is a genuine batch operation;
authoring goes through the DSL.

Waypoints are emitted in the TYPED form (`continent` + `markers`) rather than a packed
`string`, so a change diffs one waypoint at a time.

Idempotent: once every IoD collection has a row, the tool reports that there is nothing
to add and writes no spec. Paths resolve from reforged/.references.

Usage:
    python gen_collectionloc.py --out reforged/specs/patches/NNN/NN-iod-collectionloc.yaml
"""

import argparse
import glob
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

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
    return str(int(round(float(v))))


def collect(server: Path):
    """{collectionId: [(x, y, z), ...]} from CollectionTerritory_13_* Spawn nodes.

    Deduped by formatted position (the two IoD area files overlap), spawn order kept.
    """
    out = {}
    for p in sorted(glob.glob(str(server / "CollectionData" / f"CollectionTerritory_{CONTINENT}_*.xml"))):
        root = ET.parse(p).getroot()
        for coll in root.iter("Collections"):
            tid = int(coll.get("typeId"))
            seen = out.setdefault(tid, [])
            seenset = set(seen)
            for sp in coll.iter("Spawn"):
                pos = sp.get("pos")
                if not pos:
                    continue
                x, y, z = pos.split(",")[:3]
                wp = (fmt(x), fmt(y), fmt(z))
                if wp not in seenset:
                    seen.append(wp)
                    seenset.add(wp)
    return {tid: wps for tid, wps in out.items() if wps}


def existing_ids(server: Path):
    """Collection ids that already have a row in the server registry."""
    p = server / "StrSheet_CollectionLoc.xml"
    if not p.exists():
        return set()
    ids = set()
    for el in ET.parse(p).getroot().iter():
        if el.tag.endswith("String") and el.get("templateId"):
            ids.add(int(el.get("templateId")))
    return ids


def render_spec(missing: dict) -> str:
    out = [
        "# StrSheet_CollectionLoc gather-node waypoints for Island of Dawn collections.",
        "#",
        "# GENERATED FILE. Do not hand-edit: regenerate with",
        "#   python reforged/tools/dc-restore/gen_collectionloc.py --out <this file>",
        "#",
        "# Node positions projected from the server CollectionTerritory_13_* data. The",
        "# tier-1 IoD collections shipped with no waypoints in either era, so their",
        "# gather-quest map markers never resolved. ADD-ONLY: collections that already",
        "# carry a row are never re-derived here, because templateId 496 spans continent",
        "# 13 and the mainland and rebuilding it from continent-13 data alone would drop",
        "# its mainland half.",
        "",
        'spec:',
        '  version: "1.0"',
        '  schema: v92',
        "",
        "collectionLocStrings:",
        "  upsert:",
    ]
    for tid, wps in sorted(missing.items()):
        out.append(f"    - templateId: {tid}")
        out.append(f"      continent: {CONTINENT}")
        out.append("      markers:")
        for x, y, z in wps:
            out.append(f"        - [{x}, {y}, {z}]")
    out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="path of the spec file to write")
    args = parser.parse_args()

    refs = read_refs()
    server = Path(refs["server_datasheet"])

    entries = collect(server)
    if not entries:
        raise SystemExit("ERROR: no CollectionTerritory_13_* collections found")

    present = existing_ids(server)
    missing = {tid: wps for tid, wps in entries.items() if tid not in present}

    if not missing:
        print(f"IoD collections={len(entries)}, all already present in the registry; "
              f"nothing to add, no spec written.")
        return

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_spec(missing), encoding="utf-8", newline="\n")
    print(f"wrote {out_path}: {len(missing)} upsert(s) "
          f"(IoD collections={len(entries)}, already-present={len(entries) - len(missing)}): "
          + ", ".join(str(t) for t in sorted(missing)))


if __name__ == "__main__":
    sys.exit(main())
