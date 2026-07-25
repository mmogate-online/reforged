"""Generate the Tainted Gorge Bridge (HZ 437) wave-density spec.

Sets every wave spawn row in dungeon 9037 to a multiple of its BASELINE
spawnCount, leaving the escort cast and the dormant level-65 groups alone.

WHY A GENERATOR: `spawnCount` is not a transform-capable field in the DSL (only
stat.maxHp, stat.atk, stat.level and critical.res accept NumericChange), so the
density factor cannot be expressed as `{multiply: N}`. Each of the 84 rows needs
an explicit absolute value, and this content is on its second tuning pass with
more expected.

BASELINE IS GIT HEAD, NOT THE WORKING TREE. The emitted ops are ABSOLUTE values.
Reading the working tree would read back a previously applied factor and square
it on the next regeneration. Reading the committed baseline makes the generator
idempotent: same factor in, same spec out, no matter how many times the patch has
been applied.

Stage 3 takes its own factor: it is the finale and is tuned harder than the
opening, and spec 25 wires ALL of its territories while stages 1 and 2 still run
a subset, so stage 3 reaches a higher mob count from a lower factor.

Usage:
    python gen_sorcha_wave_density.py --factor-stage12 4 --factor-stage3 3
    python gen_sorcha_wave_density.py --factor-stage12 4 --factor-stage3 3 --dry-run
"""

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REFS = Path(__file__).resolve().parents[2] / ".references"

HZ = 437
# Staged defence waves, with the density factor applied to each. Stages 1 and 2
# scale together; stage 3 carries its own factor because tuning pass 3 raised the
# finale harder than the opening (user decision 2026-07-25).
#
# 43700015 (the 막판 연출용 finale set piece) is deliberately ABSENT: it is
# dormant, no event spawns it, and scaling mobs nothing ever spawns just makes the
# file lie about its own population. Omitting it leaves those rows at their
# authored baseline.
#
# 43700001 is the escort cast (Sorcha, Guardians, exit portal); 43700016 holds the
# dormant level-65 Garden of Dawn set and 43700017 the invisible cinematic NPCs.
STAGE12_GROUPS = ["43700009", "43700012", "43700010", "43700013"]
STAGE3_GROUPS = ["43700011", "43700014"]
EXCLUDED_GROUPS = ["43700001", "43700015", "43700016", "43700017"]

OUT = Path(__file__).resolve().parents[2] / "specs" / "patches" / "002" / "24-sorcha-wave-density.yaml"


def read_refs():
    refs = {}
    for line in REFS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            refs[k.strip()] = v.strip()
    return refs


def baseline_xml(server_datasheet: Path) -> str:
    """TerritoryData_437.xml as committed at HEAD, not as it sits in the tree."""
    root = subprocess.run(
        ["git", "-C", str(server_datasheet), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True).stdout.strip()
    rel = server_datasheet.resolve().relative_to(Path(root).resolve())
    target = (rel / "TerritoryData_437.xml").as_posix()
    out = subprocess.run(["git", "-C", root, "show", "HEAD:" + target],
                         capture_output=True, check=True).stdout
    return out.decode("utf-8-sig")


def collect(xml_text):
    """-> [(groupId, territoryId, npcInstanceId, partyId|None, templateId, baseCount)]

    PARTY NESTING IS PART OF THE KEY. A spawn may sit directly under <Territory>
    or under a <Party> inside it, and for the party-nested case `partyId` joins
    (huntingZoneId, groupId, territoryId, npcInstanceId) in the composite key.
    Omitting it does NOT error: the op matches nothing, applies cleanly, and is
    reported as applied with no warning. Two rows were silently skipped that way
    before this was handled (territory 43700363, party 43700001), which the
    post-apply mob-count gate caught as 609 mobs instead of 616.
    """
    active = re.sub(r"<!--.*?-->", "", xml_text, flags=re.S)
    root = ET.fromstring(active.encode("utf-8"))
    rows = []
    for grp in root.iter("TerritoryGroup"):
        gid = grp.get("id")
        if gid not in STAGE12_GROUPS + STAGE3_GROUPS:
            continue
        for terr in grp.iter("Territory"):
            tid = terr.get("id")
            for child in terr:
                if child.tag == "Npc":
                    rows.append((gid, tid, child.get("instanceId"), None,
                                 child.get("npcTemplateId"), int(child.get("spawnCount") or 1)))
                elif child.tag == "Party":
                    pid = child.get("id")
                    for npc in child.iter("Npc"):
                        rows.append((gid, tid, npc.get("instanceId"), pid,
                                     npc.get("npcTemplateId"), int(npc.get("spawnCount") or 1)))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--factor-stage12", type=int, required=True,
                    help="density factor for stage 1 and 2 groups (front and rear)")
    ap.add_argument("--factor-stage3", type=int, required=True,
                    help="density factor for stage 3 groups (front and rear)")
    ap.add_argument("--dry-run", action="store_true", help="print the summary, write nothing")
    args = ap.parse_args()

    if args.factor_stage12 < 1 or args.factor_stage3 < 1:
        sys.exit("factors must be >= 1")

    def factor_for(gid):
        return args.factor_stage3 if gid in STAGE3_GROUPS else args.factor_stage12

    refs = read_refs()
    ds = Path(refs["server_datasheet"])
    rows = collect(baseline_xml(ds))
    if not rows:
        sys.exit("no wave spawn rows found; check the group id list")

    base_total = sum(r[5] for r in rows)
    new_total = sum(r[5] * factor_for(r[0]) for r in rows)
    party_rows = sum(1 for r in rows if r[3])
    s12 = sum(r[5] for r in rows if r[0] in STAGE12_GROUPS)
    s3 = sum(r[5] for r in rows if r[0] in STAGE3_GROUPS)

    lines = [
        "# Spec: 24 - Tainted Gorge Bridge (HZ 437) wave density",
        "#",
        "# GENERATED by tools/dc-restore/gen_sorcha_wave_density.py",
        "#   --factor-stage12 %d --factor-stage3 %d" % (args.factor_stage12, args.factor_stage3),
        "# Do not hand-edit: regenerate instead.",
        "#",
        "# Sets every staged-wave spawn row in dungeon 9037 to a multiple of its BASELINE",
        "# count. Stage 3 carries its own factor because tuning pass 3 raised the finale",
        "# harder than the opening (user decision 2026-07-25, after clearing the pass-2",
        "# encounter with two players).",
        "#",
        "#   stages 1+2 (front and rear)  x%d   %d baseline mobs -> %d" % (
            args.factor_stage12, s12, s12 * args.factor_stage12),
        "#   stage 3    (front and rear)  x%d   %d baseline mobs -> %d" % (
            args.factor_stage3, s3, s3 * args.factor_stage3),
        "#   TOTAL                             %d baseline mobs -> %d" % (base_total, new_total),
        "#",
        "# Pairs with balance/zone-0437-tainted_gorge_bridge.yaml (stat side) and",
        "# 25-sorcha-rear-waves.yaml (which territories the wave script actually spawns).",
        "# Density alone does nothing for a territory no event references, so those two",
        "# specs must move together; spec 25 wires all of stage 3, which is why stage 3",
        "# needs a LOWER factor than stages 1 and 2 to reach a HIGHER mob count.",
        "#",
        "# Counts are ABSOLUTE and are derived from the COMMITTED baseline, never from the",
        "# working tree, so regenerating after an apply reproduces this file byte for byte.",
        "#",
        "# Groups covered: %s (stages 1+2), %s (stage 3)" % (
            ", ".join(STAGE12_GROUPS), ", ".join(STAGE3_GROUPS)),
        "# Groups deliberately excluded: %s" % ", ".join(EXCLUDED_GROUPS),
        "#   43700001 escort cast (Sorcha, Guardians, exit portal); 43700015 the dormant",
        "#   finale set piece, left at baseline since nothing spawns it; 43700016 dormant",
        "#   level-65 Garden of Dawn set; 43700017 cinematic invisibles.",
        "#",
        "# Rows: %d, of which %d are party-nested and carry partyId in the key." % (len(rows), party_rows),
        "# Idempotent: absolute values, applied via the migrate --patch 002 batch.",
        "",
        'spec:',
        '  version: "1.0"',
        '  schema: v92',
        "",
        "territorySpawns:",
        "  update:",
    ]

    for gid, tid, iid, pid, tpl, base in rows:
        f = factor_for(gid)
        lines += [
            "    - huntingZoneId: %d" % HZ,
            "      groupId: %s" % gid,
            "      territoryId: %s" % tid,
            "      npcInstanceId: %s" % iid,
        ]
        if pid:
            lines.append("      partyId: %s        # party-nested: part of the composite key" % pid)
        lines += [
            "      changes:",
            "        spawnCount: %d      # tpl %s, baseline %d, x%d" % (base * f, tpl, base, f),
        ]

    text = "\n".join(lines) + "\n"

    print("wave spawn rows      : %d" % len(rows))
    print("baseline mobs        : %d" % base_total)
    print("factor stages 1+2    : x%d" % args.factor_stage12)
    print("factor stage 3       : x%d" % args.factor_stage3)
    print("resulting mobs       : %d" % new_total)
    print("groups covered       : %s | %s" % (", ".join(STAGE12_GROUPS), ", ".join(STAGE3_GROUPS)))
    print("groups excluded      : %s" % ", ".join(EXCLUDED_GROUPS))
    if args.dry_run:
        print("(dry run, nothing written)")
        return
    OUT.write_text(text, encoding="utf-8")
    print("wrote                : %s" % OUT)


if __name__ == "__main__":
    main()
