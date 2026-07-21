#!/usr/bin/env python
"""Generate the IoD patch 001 story-group registration spec (Stage 4A).

Membership + in-group ORDER target (authoritative): the v17.11 client
QuestGroupList StoryGroupList section. Journal display order equals document
order within a group, so ordering is part of the target. The v17 order is read
directly from the client shard and cross-checked against the extracted artifact
(docs/plans/iod-alpha-content-loop/data/v17-quests.json).

Two v92-keeps are preserved (settled decision 11): quests 1379 (Gunner/Engineer
Training) and 1383 (Gathering Your Strength). They are absent from v17 but exist
in v92; each is kept in its current v92 story group, inserted at its current v92
relative position (anchored between the retained v17 members that surround it).

Server-era registrations that are absent from v17 (and are not keeps) are dropped
by v17 authority: the group-level `quests:` list on upsert is REPLACE-ALL, so
listing exactly the target membership drops everything else. This is only valid
because every current member of the affected groups is inside the patch scope
(the 63 v17 quests plus the 2 keeps); the generator asserts this and hard-fails
if a future out-of-scope member appears, which would force a fallback to
membership ops.

The `dec` (journal short description) and group `name` are inert server-side
annotations: they do not drive any game logic, only display/authoring. They are
normalized to ENGLISH here so the spec reads cleanly and is self-documenting.
Each quest's dec is its English title (the v17 client title for the 63 v17
quests; the v92 client English title for the two keeps 1379/1383). Each group's
name is its v17 client English name. Membership and ORDER are unchanged by this
normalization.

The sibling questHuntingZones entity co-tenants QuestGroupList.xml. Zone 13's
HuntingZone row is checked against the v17 registration; a row is emitted ONLY if
step/kind drifted. In current data step=1/kind=solo match v17, so none is emitted.

Output: specs/patches/001/07-iod-story-groups.yaml (upsert, idempotent).
QuestGroupList.xml is server-authored and client-synced.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path("D:/dev/mmogate/github/reforged-server-content/reforged")
V17_JSON = REPO / "docs/plans/iod-alpha-content-loop/data/v17-quests.json"
ALIGN_JSON = REPO / "docs/plans/iod-alpha-content-loop/data/id-alignment-quests.json"
V17_CLIENT = Path(
    "D:/dev/tera/tera-dc-17_11/DataCenter_Final_USA/QuestGroupList/QuestGroupList-00000.xml"
)
V92_FILE = Path("D:/dev/mmogate/tera92/server/Datasheet/QuestGroupList.xml")
OUT = REPO / "specs/patches/001/07-iod-story-groups.yaml"

# Settled decision 11: keep these two v92 quests at their current v92 registration.
KEEP_IDS = [1379, 1383]

# Groups this spec owns (the IoD story groups). Only these are rewritten.
TARGET_GROUPS = [1, 2]

ZONE13 = 13


def parse_storygroups(path):
    """Return {group_id: {'name': str, 'quests': [(id, dec), ...]}} in doc order."""
    data = path.read_text(encoding="utf-8")
    m = re.search(r"<StoryGroupList>(.*?)</StoryGroupList>", data, re.S)
    if not m:
        sys.exit(f"HARD FAIL: no StoryGroupList section in {path}")
    section = m.group(1)
    groups = {}
    for gm in re.finditer(
        r'<StoryGroup\b([^>]*)>(.*?)</StoryGroup>', section, re.S
    ):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', gm.group(1)))
        gid = int(attrs["id"])
        quests = []
        for qm in re.finditer(r'<Quest\b([^>]*)/>', gm.group(2)):
            qa = dict(re.findall(r'(\w+)="([^"]*)"', qm.group(1)))
            quests.append((int(qa["id"]), qa.get("dec", "")))
        groups[gid] = {"name": attrs.get("name", ""), "quests": quests}
    return groups


def parse_client_order(path):
    """Return {group_id: {'name': str, 'order': [quest_id, ...]}} from the v17 client shard."""
    data = path.read_text(encoding="utf-8")
    groups = {}
    for gm in re.finditer(r'<StoryGroup\b([^>]*)>(.*?)</StoryGroup>', data, re.S):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', gm.group(1)))
        gid = int(attrs["id"])
        ids = [int(x) for x in re.findall(r'<Quest\s+id="(\d+)"', gm.group(2))]
        groups[gid] = {"name": attrs.get("name", ""), "order": ids}
    return groups


def yaml_str(s):
    """Double-quoted YAML scalar, escaping backslash and quote."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    v17 = json.load(open(V17_JSON, encoding="utf-8"))
    v17_quests = {q["id"]: q for q in v17["quests"]}
    scope_ids = set(v17_quests) | set(KEEP_IDS)

    v92_groups = parse_storygroups(V92_FILE)
    client_groups = parse_client_order(V17_CLIENT)

    # v17 authoritative per-group order (client shard), cross-checked vs artifact.
    for gid in TARGET_GROUPS:
        art = next(
            (g["island_order"] for g in v17["story_groups"] if int(g["group_id"]) == gid),
            None,
        )
        if art is None:
            sys.exit(f"HARD FAIL: artifact has no story_groups entry for group {gid}")
        client_ids = client_groups.get(gid, {}).get("order")
        if client_ids != art:
            sys.exit(
                f"HARD FAIL: group {gid} order drift client={client_ids} artifact={art}"
            )

    # Map each keep to its current v92 group.
    keep_group = {}
    for kid in KEEP_IDS:
        for gid, g in v92_groups.items():
            if any(q[0] == kid for q in g["quests"]):
                keep_group[kid] = gid
                break
        else:
            sys.exit(f"HARD FAIL: keep {kid} not found in any v92 story group")

    # dec source (normalized to English): v17 client title for the 63 v17 quests;
    # v92 client English title (from the alignment artifact) for the two keeps.
    align = json.load(open(ALIGN_JSON, encoding="utf-8"))
    keep_title = {
        r["questId"]: r.get("v92_client_title", "")
        for r in align["non_aligned"]
    }

    def dec_for(qid):
        if qid in v17_quests:
            title = v17_quests[qid].get("title", "")
        else:
            title = keep_title.get(qid, "")
        if not title:
            sys.exit(f"HARD FAIL: no English title for quest {qid}")
        return title

    report = {}
    lines = [
        "spec:",
        '  version: "1.0"',
        "  schema: v92",
        "",
        "# IoD patch 001 story-group registration (Stage 4A restoration).",
        "# Membership + in-group ORDER TARGET (authoritative): the v17.11 client",
        "#   QuestGroupList StoryGroupList section (order verified directly from the",
        "#   client shard, cross-checked vs v17-quests.json island_order).",
        "# Journal display order = document order within a group, so order is the target.",
        "#",
        "# Decision 6: v17.11 is the north star; v31 gap-fill only.",
        "# Decision 11: quests 1379 and 1383 are v92-keeps (absent from v17, kept at their",
        "#   current v92 story group and relative position).",
        "#",
        "# The group-level quests: list on upsert is REPLACE-ALL. Every current member of",
        "#   groups 1 and 2 is inside patch scope (63 v17 quests + 2 keeps), so replace-all",
        "#   yields exact v17 order and drops server-era registrations absent from v17.",
        "# dec and group name are inert server-side annotations (no game logic); they are",
        "#   normalized to ENGLISH for self-documentation: each dec is the quest's English",
        "#   title (v17 client title for the 63; v92 client title for keeps 1379/1383), and",
        "#   each group name is its v17 client English name. Membership/order are unchanged.",
        "#",
        "# QuestGroupList.xml is server-authored and client-synced.",
        "# Generated by tools/dc-restore/gen_storygroup_specs.py",
        "",
        "questStoryGroups:",
        "  upsert:",
    ]

    for gid in TARGET_GROUPS:
        v17_ids = client_groups[gid]["order"]
        current = [q[0] for q in v92_groups[gid]["quests"]]

        # Scope guard: replace-all is only safe if every current member is in scope.
        out_of_scope = [q for q in current if q not in scope_ids]
        if out_of_scope:
            sys.exit(
                f"HARD FAIL: group {gid} has out-of-scope members {out_of_scope}; "
                "replace-all would touch them. Fall back to membership ops."
            )

        # Keeps that live in this group, anchored to their preceding retained member.
        keeps_here = [k for k in KEEP_IDS if keep_group[k] == gid]
        attach = {a: [] for a in v17_ids}  # anchor id -> [keep ids after it]
        front = []
        for k in keeps_here:
            pos = current.index(k)
            anchor = None
            for j in range(pos - 1, -1, -1):
                if current[j] in v17_ids:
                    anchor = current[j]
                    break
            if anchor is None:
                front.append(k)
            else:
                attach[anchor].append(k)

        target = list(front)
        for a in v17_ids:
            target.append(a)
            target.extend(attach[a])

        dropped = [q for q in current if q not in target]

        lines.append(f"    - id: {gid}")
        lines.append(f"      name: {yaml_str(client_groups[gid]['name'])}")
        lines.append("      quests:")
        for qid in target:
            lines.append(f"        - id: {qid}")
            lines.append(f"          dec: {yaml_str(dec_for(qid))}")

        report[gid] = {
            "target": target,
            "size": len(target),
            "keeps": {k: target.index(k) for k in keeps_here},
            "dropped": dropped,
            "added": [q for q in target if q not in current],
        }

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- zone 13 HuntingZone drift check (emit only if step/kind drift) ---
    def zone_row(path, zid):
        d = path.read_text(encoding="utf-8")
        m = re.search(r'<HuntingZone\b[^>]*\bid="%d"[^>]*/>' % zid, d)
        if not m:
            return None
        return dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    z92 = zone_row(V92_FILE, ZONE13)
    z17 = zone_row(V17_CLIENT, ZONE13)
    zone_drift = z92 is None or z17 is None or (
        z92.get("step") != z17.get("step") or z92.get("kind") != z17.get("kind")
    )

    # --- report to stderr (not part of the spec) ---
    print(f"Wrote {OUT}", file=sys.stderr)
    for gid in TARGET_GROUPS:
        r = report[gid]
        print(
            f"group {gid}: size={r['size']} target={r['target']}",
            file=sys.stderr,
        )
        print(f"  keeps@index={r['keeps']}", file=sys.stderr)
        print(f"  added={r['added']} dropped={r['dropped']}", file=sys.stderr)
    print(
        f"zone {ZONE13} HuntingZone: v92 step/kind="
        f"{(z92 or {}).get('step')}/{(z92 or {}).get('kind')} "
        f"v17 step/kind={(z17 or {}).get('step')}/{(z17 or {}).get('kind')} "
        f"-> drift={zone_drift} (no row emitted)" if not zone_drift else
        f"zone {ZONE13} DRIFT -> manual review",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
