"""Add missing StrSheet_CollectionLoc waypoints for IoD (continent 13) collections.

The gather-quest map marker reads the family StrSheet_CollectionLoc: one String per
collection (templateId = collection id) whose value is a pipe-joined list of
`continentId#x,y,z` node positions (the collection analog of StrSheet_NpcLoc).
Clicking a gather objective marks those points on the map.

The v92 (and v31) data shipped WITHOUT entries for the tier-1 IoD collections
(Verdra Plant 1, Krymetal Ore 101, Sun Essence 301), so their quest markers never
resolved. This tool projects the IoD node positions from the server
CollectionTerritory_13_* data into `13#x,y,z` waypoints and ADDS an entry for every
continent-13 collection that does not already have one. Collections that already
carry an entry (409/410/411/492/496, live-validated) are LEFT UNTOUCHED, including
multi-zone ones (496 also spawns on the mainland).

Add-only + idempotent: re-running adds nothing once every IoD collection has an entry.
Not in the migrate sync-config, so this is a tool-managed registry like NpcLoc. Writes
both the server copy and the client shard so they stay consistent. The two files use
slightly different self-closing styles, so presence is detected by substring, and new
rows are inserted with each file's own indent. Paths resolve from reforged/.references.
"""

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
    """{collectionId: '13#x,y,z|...'} from CollectionTerritory_13_* Spawn nodes,
    deduped by formatted position (the two IoD area files overlap), spawn order kept."""
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
                wp = f"{CONTINENT}#{fmt(x)},{fmt(y)},{fmt(z)}"
                if wp not in seenset:
                    seen.append(wp)
                    seenset.add(wp)
    return {tid: "|".join(wps) for tid, wps in out.items() if wps}


def add_missing(text: str, entries: dict, indent: str) -> tuple[str, int, int]:
    added = skipped = 0
    for tid, wps in sorted(entries.items()):
        if f'templateId="{tid}"' in text:  # already has an entry (any style) -> leave it
            skipped += 1
            continue
        row = f'{indent}<String string="{wps}" templateId="{tid}" />\n'
        text = text.replace("</StrSheet_CollectionLoc>", row + "</StrSheet_CollectionLoc>")
        added += 1
    return text, added, skipped


def main():
    refs = read_refs()
    server = Path(refs["server_datasheet"])
    entries = collect(server)
    if not entries:
        raise SystemExit("ERROR: no CollectionTerritory_13_* collections found")

    for label, path, indent in [
        ("server", server / "StrSheet_CollectionLoc.xml", "  "),
        ("client", Path(refs["client_datacenter"]) / "StrSheet_CollectionLoc" /
         "StrSheet_CollectionLoc-00000.xml", "    "),
    ]:
        text = path.read_text(encoding="utf-8")
        text, added, skipped = add_missing(text, entries, indent)
        path.write_text(text, encoding="utf-8")
        print(f"[{label}] IoD collections={len(entries)} added={added} "
              f"already-present={skipped}")


if __name__ == "__main__":
    sys.exit(main())
