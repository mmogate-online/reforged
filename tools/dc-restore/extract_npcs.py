"""Phase 1 north-star extraction: v17.11 client NPC roster and territory geometry.

Extracts, for the Island of Dawn hunting zones (13, 64, 213, 313, 364, 436),
every NPC template and every territory group/territory from the 2011-era
(v17.11) unpacked client DataCenter. The client DataCenter carries NPC
definitions (id, name, level, race/gender/size flags, villager classification)
and territory geometry (group id + Korean desc + fence vertex rings) only. It
holds no spawn entries linking an NPC to a territory, so the sole territory ->
NPC hint is the Korean group desc, which is captured verbatim.

Sources (read-only), resolved as fixed client subfamilies:
  - NpcData/           per-zone Template roster (huntingZoneId on the root)
  - StrSheet_Creature/ English names/titles keyed by (HuntingZone id, templateId)
  - TerritoryData/     per-zone TerritoryGroup geometry (huntingZoneId on the root)

Output (deterministic, sorted, no timestamps) under
docs/plans/iod-alpha-content-loop/data/:
  - v17-npcs.json / v17-npcs.md
  - v17-territories.json / v17-territories.md

Reuses dclib.py for references loading, namespace-agnostic XML parsing, the
client shard indexer, and the StrSheet_Creature name index. Stdlib only.
Invoke as: python reforged/tools/dc-restore/extract_npcs.py
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dclib  # noqa: E402

ZONES = [13, 64, 213, 313, 364, 436]
OUT_DIR = dclib.reforged_dir() / "docs" / "plans" / "iod-alpha-content-loop" / "data"

# Subject extractor: prefer the last parenthetical, else the last _-delimited part.
_PAREN = re.compile(r"\(([^()]*)\)")


def _client_root() -> Path:
    refs = dclib.load_references()
    return Path(refs["old_client_dc"])


def _to_float(value: str):
    """Parse a numeric attribute to int or float, or None when absent/blank."""
    if value is None or value == "":
        return None
    try:
        f = float(value)
    except ValueError:
        return value
    return int(f) if f.is_integer() else f


def _bool(value: str) -> bool:
    return value == "true"


def _classify(tmpl) -> str:
    if _bool(tmpl.get("isObjectNpc")):
        return "object"
    if _bool(tmpl.get("villager")):
        return "villager"
    return "monster"


def _subject(desc: str) -> str:
    """The Korean subject a group desc names (last parenthetical, else last _ part)."""
    if not desc:
        return ""
    parens = _PAREN.findall(desc)
    if parens:
        return parens[-1].strip()
    if "_" in desc:
        return desc.rsplit("_", 1)[1].strip()
    return desc.strip()


def _extract_npcs(client: Path):
    """Per-zone NPC roster joined with StrSheet_Creature names. Returns dict."""
    npc_shards = dclib.index_client_shards(
        client / "NpcData", dclib.zone_from_hz_attr, set(ZONES)
    )
    name_rows = dclib.index_creature_names(client / "StrSheet_Creature")
    names = {}
    for r in name_rows:
        if r["hz"] is not None and r["templateId"] is not None:
            names[(r["hz"], r["templateId"])] = r

    zones_out = {}
    for zone in ZONES:
        shards = npc_shards.get(zone, [])
        npcs = []
        shard_name = shards[0].name if shards else None
        if shards:
            root = dclib.parse_root(dclib.read_text(shards[0]))
            for tmpl in dclib.iter_local(root, "Template"):
                tid_raw = tmpl.get("id")
                tid = int(tid_raw) if tid_raw and tid_raw.isdigit() else tid_raw
                stat = None
                for ch in tmpl:
                    if dclib.strip_ns(ch.tag) == "Stat":
                        stat = ch
                        break
                level = _to_float(stat.get("level")) if stat is not None else None
                name_row = names.get((zone, tid), {})
                classification = _classify(tmpl)
                npcs.append({
                    "templateId": tid,
                    "name": name_row.get("name", ""),
                    "title": name_row.get("title", ""),
                    "role_class": name_row.get("class", ""),
                    "level": level,
                    "race": tmpl.get("race", ""),
                    "gender": tmpl.get("gender", ""),
                    "size": tmpl.get("size", ""),
                    "scale": _to_float(tmpl.get("scale")),
                    "elite": _bool(tmpl.get("elite")),
                    "villager": _bool(tmpl.get("villager")),
                    "isObjectNpc": _bool(tmpl.get("isObjectNpc")),
                    "classification": classification,
                    "parentId": _to_float(tmpl.get("parentId")),
                    "template_class": tmpl.get("class", ""),
                    "has_name": (zone, tid) in names,
                })
        npcs.sort(key=lambda n: (n["templateId"] if isinstance(n["templateId"], int) else 1 << 62))
        counts = {
            "total": len(npcs),
            "villager": sum(1 for n in npcs if n["classification"] == "villager"),
            "monster": sum(1 for n in npcs if n["classification"] == "monster"),
            "object": sum(1 for n in npcs if n["classification"] == "object"),
            "named": sum(1 for n in npcs if n["has_name"]),
            "unnamed": sum(1 for n in npcs if not n["has_name"]),
        }
        zones_out[str(zone)] = {
            "huntingZoneId": zone,
            "npc_shard": shard_name,
            "counts": counts,
            "npcs": npcs,
        }
    return zones_out


def _extract_territories(client: Path, npc_zones: dict):
    """Per-zone territory groups with fence rings and desc-based NPC hints."""
    terr_shards = dclib.index_client_shards(
        client / "TerritoryData", dclib.zone_from_hz_attr, set(ZONES)
    )
    zones_out = {}
    for zone in ZONES:
        shards = terr_shards.get(zone, [])
        shard_name = shards[0].name if shards else None
        # English names in this zone, for literal desc matching (best-effort).
        zone_names = [
            n["name"] for n in npc_zones.get(str(zone), {}).get("npcs", []) if n["name"]
        ]
        groups = []
        terr_total = 0
        if shards:
            root = dclib.parse_root(dclib.read_text(shards[0]))
            for grp in dclib.iter_local(root, "TerritoryGroup"):
                desc = grp.get("desc", "")
                territories = []
                for idx, terr in enumerate(dclib.iter_local(grp, "Territory")):
                    ring = [f.get("pos", "") for f in dclib.iter_local(terr, "Fence")]
                    territories.append({"index": idx, "vertex_count": len(ring), "fence": ring})
                terr_total += len(territories)
                desc_lower = desc.lower()
                matches = sorted({nm for nm in zone_names if nm and nm.lower() in desc_lower})
                groups.append({
                    "id": grp.get("id", ""),
                    "desc": desc,
                    "subject": _subject(desc),
                    "npc_name_matches": matches,
                    "territory_count": len(territories),
                    "vertex_count": sum(t["vertex_count"] for t in territories),
                    "territories": territories,
                })
        groups.sort(key=lambda g: (g["id"].isdigit() is False, int(g["id"]) if g["id"].isdigit() else 0, g["id"]))
        zones_out[str(zone)] = {
            "huntingZoneId": zone,
            "territory_shard": shard_name,
            "group_count": len(groups),
            "territory_count": terr_total,
            "groups": groups,
        }
    return zones_out


def _write_json(path: Path, data: dict):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def _write_npcs_md(path: Path, data: dict):
    lines = ["# v17.11 Island of Dawn NPC Roster", ""]
    lines.append(
        "Source: unpacked v17.11 client DataCenter (`NpcData`, names from "
        "`StrSheet_Creature`). The client carries NPC definitions and level only; "
        "combat stats (HP, attack) are server-side and absent here. Classification "
        "uses the client `villager` / `isObjectNpc` template flags (object takes "
        "precedence over villager)."
    )
    lines.append("")
    lines.append("| Zone | Total | Villager | Monster | Object | Named | Unnamed |")
    lines.append("|------|-------|----------|---------|--------|-------|---------|")
    for zone in ZONES:
        z = data["zones"][str(zone)]
        c = z["counts"]
        lines.append(
            f"| {zone} | {c['total']} | {c['villager']} | {c['monster']} | "
            f"{c['object']} | {c['named']} | {c['unnamed']} |"
        )
    lines.append("")
    for zone in ZONES:
        z = data["zones"][str(zone)]
        lines.append(f"## Zone {zone} ({z['npc_shard']})")
        lines.append("")
        lines.append("| tid | name | title | class(job) | lvl | race | gender | size | elite | classification |")
        lines.append("|-----|------|-------|-----------|-----|------|--------|------|-------|----------------|")
        for n in z["npcs"]:
            lines.append(
                f"| {n['templateId']} | {n['name'] or '-'} | {n['title'] or '-'} | "
                f"{n['role_class'] or '-'} | {n['level'] if n['level'] is not None else '-'} | "
                f"{n['race'] or '-'} | {n['gender'] or '-'} | {n['size'] or '-'} | "
                f"{'yes' if n['elite'] else '-'} | {n['classification']} |"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_territories_md(path: Path, data: dict):
    lines = ["# v17.11 Island of Dawn Territory Geometry", ""]
    lines.append(
        "Source: unpacked v17.11 client DataCenter (`TerritoryData`). Each zone shard "
        "holds `TerritoryGroup`s (id + Korean desc) containing `Territory` fence "
        "polygons. The client carries no spawn entries, so the only territory -> NPC "
        "hint is the group desc; `subject` is the Korean label the desc names "
        "(last parenthetical, else the trailing `_` segment), kept verbatim. English "
        "`npc_name_matches` are literal desc substrings only (the descs are Korean, so "
        "this is near-always empty and downstream translation is required to map a "
        "Korean subject to an English template)."
    )
    lines.append("")
    lines.append("| Zone | Groups | Territories | Vertices |")
    lines.append("|------|--------|-------------|----------|")
    for zone in ZONES:
        z = data["zones"][str(zone)]
        v = sum(g["vertex_count"] for g in z["groups"])
        lines.append(f"| {zone} | {z['group_count']} | {z['territory_count']} | {v} |")
    lines.append("")
    for zone in ZONES:
        z = data["zones"][str(zone)]
        lines.append(f"## Zone {zone} ({z['territory_shard']})")
        lines.append("")
        for g in z["groups"]:
            match_note = f" | matches: {', '.join(g['npc_name_matches'])}" if g["npc_name_matches"] else ""
            lines.append(
                f"### Group {g['id']} - {g['desc'] or '(no desc)'}"
            )
            lines.append("")
            lines.append(
                f"subject: `{g['subject'] or '-'}` | territories: {g['territory_count']} | "
                f"vertices: {g['vertex_count']}{match_note}"
            )
            lines.append("")
            for t in g["territories"]:
                ring = " ".join(f"({p})" for p in t["fence"])
                lines.append(f"- T{t['index']} ({t['vertex_count']} verts): {ring}")
            lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    client = _client_root()
    if not client.is_dir():
        print(f"client DataCenter not found: {client}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    npc_zones = _extract_npcs(client)
    npcs_doc = {"zones": npc_zones}
    terr_zones = _extract_territories(client, npc_zones)
    terr_doc = {"zones": terr_zones}

    _write_json(OUT_DIR / "v17-npcs.json", npcs_doc)
    _write_npcs_md(OUT_DIR / "v17-npcs.md", npcs_doc)
    _write_json(OUT_DIR / "v17-territories.json", terr_doc)
    _write_territories_md(OUT_DIR / "v17-territories.md", terr_doc)

    for zone in ZONES:
        c = npc_zones[str(zone)]["counts"]
        t = terr_zones[str(zone)]
        print(
            f"zone {zone}: npcs total={c['total']} "
            f"(villager={c['villager']} monster={c['monster']} object={c['object']}), "
            f"groups={t['group_count']} territories={t['territory_count']}"
        )
    print(f"wrote 4 artifacts to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
