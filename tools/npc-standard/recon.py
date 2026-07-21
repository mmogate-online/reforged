"""
Streaming structural recon of the NPC-related datasheet schemas.
Population-complete (no sampling), memory-bounded via iterparse + element clear
and capped per-attribute value tracking.

For each file family it reports, for the primary entry element and its nested
blocks: entry count, per-attribute presence%, distinct-value cardinality (capped),
and modal value share. This is the raw material for deciding which attributes are
"defaults" (low cardinality + high modal share) vs "identity/varies" (high
cardinality), and whether archetype clustering is warranted.
"""
import sys, glob, time, os
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

DS = r"D:\dev\mmogate\tera92\server\Datasheet"
CAP = 256  # max distinct values tracked per attribute before flagging high-cardinality

def strip(tag):
    return tag.rsplit('}', 1)[-1]

class AttrStat:
    __slots__ = ('present', 'counter', 'capped')
    def __init__(self):
        self.present = 0
        self.counter = Counter()
        self.capped = False
    def add(self, v):
        self.present += 1
        if self.capped:
            return
        self.counter[v] += 1
        if len(self.counter) > CAP:
            self.capped = True
            self.counter.clear()

def analyze(family, primary_tag, files, value_dist=True):
    """primary_tag: the depth-1 repeating element to profile. If None, auto-detect."""
    t0 = time.time()
    entry_count = 0
    # attr stats keyed by (element_tag, attr_name); element_tag '' == primary, else nested block
    attr = defaultdict(AttrStat)
    block_present = Counter()      # nested block tag -> # primary entries containing it
    primary_seen = Counter()       # depth-1 tag frequency (to confirm primary)
    total_bytes = sum(os.path.getsize(f) for f in files)

    for fi, fpath in enumerate(files):
        context = ET.iterparse(fpath, events=('start', 'end'))
        _, root = next(context)
        depth = 0
        cur_primary = None
        cur_blocks = set()
        for event, el in context:
            tag = strip(el.tag)
            if event == 'start':
                depth += 1
                if depth == 1:
                    primary_seen[tag] += 1
                    if primary_tag is None or tag == primary_tag:
                        cur_primary = el
                        cur_blocks = set()
            else:  # end
                if depth == 1 and (primary_tag is None or tag == primary_tag) and el is cur_primary:
                    entry_count += 1
                    for k, v in el.attrib.items():
                        s = attr[('', strip(k))]
                        s.add(v) if value_dist else s.add(None)
                    cur_primary = None
                    root.clear()  # free processed subtree
                elif depth == 2 and cur_primary is not None:
                    # nested block directly under the primary entry
                    if tag not in cur_blocks:
                        block_present[tag] += 1
                        cur_blocks.add(tag)
                    for k, v in el.attrib.items():
                        s = attr[(tag, strip(k))]
                        s.add(v) if value_dist else s.add(None)
                depth -= 1

    dt = time.time() - t0
    print(f"\n{'='*78}\n{family}: {len(files)} files, {total_bytes/1048576:.1f} MB, "
          f"{entry_count} '{primary_tag or 'auto'}' entries  ({dt:.1f}s)")
    print(f"  depth-1 tags: {dict(primary_seen.most_common(6))}")
    if not entry_count:
        return
    # nested blocks
    if block_present:
        print(f"  nested blocks (presence% of {entry_count} entries):")
        for tag, c in block_present.most_common():
            print(f"    {tag:<28} {100*c/entry_count:5.1f}%")
    # primary attributes
    def report(scope_label, scope_key):
        rows = sorted([(k[1], v) for k, v in attr.items() if k[0] == scope_key],
                      key=lambda kv: -kv[1].present)
        if not rows:
            return
        print(f"  [{scope_label}] attr  presence%  distinct  modal(share%)")
        for name, s in rows:
            pres = 100*s.present/entry_count
            if s.capped:
                dist = f">{CAP}"
                modal = "-- (high-card)"
            else:
                dist = str(len(s.counter))
                mv, mc = s.counter.most_common(1)[0] if s.counter else ('', 0)
                mvs = (mv[:18] + '..') if len(mv) > 20 else mv
                modal = f"{mvs!r} ({100*mc/s.present:.0f}%)"
            print(f"    {name:<26} {pres:5.1f}    {dist:>5}   {modal}")
    report("primary", '')
    # nested block attrs (only the biggest blocks to keep output readable)
    for tag, _ in block_present.most_common(12):
        report(f"block:{tag}", tag)

def files_for(prefix):
    seen = dict.fromkeys(
        os.path.realpath(p) for p in
        glob.glob(os.path.join(DS, f"{prefix}*.xml")) +
        glob.glob(os.path.join(DS, "**", f"{prefix}*.xml"), recursive=True))
    return sorted(seen)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    plan = {
        "npc":       ("NpcData",       "Template", True),
        "ai":        ("AIData",        "Ai",       True),
        "territory": ("TerritoryData", None,       True),
        "skill":     ("NpcSkillData",  None,       False),  # 954MB: structure/count only
    }
    for key, (prefix, tag, vdist) in plan.items():
        if which not in ("all", key):
            continue
        analyze(prefix, tag, files_for(prefix), value_dist=vdist)
