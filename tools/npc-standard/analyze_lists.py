"""
Nested-list-block extension to the standard-library analysis.

Whole-attribute analysis (analyze_all.py) can only default scalar attributes. This
captures designated nested SUBTREES (a block + its repeated children) as a single
canonical signature per entry, then measures the modal-signature share per cluster
-- i.e. "is there a standard <AbnormalityResistanceOverride> list / a standard
combat-AI tree for this archetype, or does it vary per NPC?"

Targets:
  NpcData   Template > AbnormalityResistanceOverride (resetTime + Abnormality[])
  AIData    Ai > PeaceState > RandomMove (Social[])
  AIData    Ai > CombatState (full combat tree)
"""
import glob, os, re, json, hashlib
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

DS = r"D:\dev\mmogate\tera92\server\Datasheet"
ZONE = re.compile(r'_(\d+)\.xml$', re.I)
def strip(t): return t.rsplit('}', 1)[-1]
def zone_of(p): m = ZONE.search(os.path.basename(p)); return m.group(1) if m else '?'
def files_for(p): return sorted({os.path.realpath(x) for x in glob.glob(os.path.join(DS, f"{p}*.xml"))})
def canon(v):
    if v is None: return None
    s = v.strip()
    try:
        f = float(s); return str(int(f)) if f == int(f) else repr(f)
    except ValueError: return s
def cluster_of(t):
    if t.get('isObjectNpc') == 'true': return 'ObjectNpc'
    if t.get('villager') == 'true':
        return 'QuestVillager' if t.get('questVillager') == 'true' else 'MerchantVillager'
    if canon(t.get('huntingStyle')) == 'raid': return 'BossMonster'
    if t.get('elite') == 'true': return 'EliteMonster'
    return 'NormalMonster'

def sig(el):
    """Canonical signature of a full subtree (tag + sorted canon attrs + children)."""
    parts = [strip(el.tag)] + [f"{strip(k)}={canon(v)}" for k, v in sorted(el.attrib.items())]
    kids = [sig(c) for c in el]
    return f"({' '.join(parts)}{('[' + ','.join(kids) + ']') if kids else ''})"

def modal_report(title, by_cluster_sigs):
    print(f"\n=== {title}: modal-subtree share per cluster ===")
    print(f"{'cluster':<18}{'N':>7}{'present%':>9}{'distinct':>9}{'modal_share':>12}")
    out = {}
    for cl, sigs in sorted(by_cluster_sigs.items(), key=lambda kv: -len(kv[1])):
        present = [s for s in sigs if s is not None]
        if not present: continue
        c = Counter(present); mv, mc = c.most_common(1)[0]
        out[cl] = {'n': len(sigs), 'present': len(present), 'distinct': len(c),
                   'modal_share': mc / len(present), 'modal_sig': mv}
        print(f"{cl:<18}{len(sigs):>7}{100*len(present)/len(sigs):>8.0f}%"
              f"{len(c):>9}{mc/len(present):>11.0%}")
    return out

# ---- NpcData: AbnormalityResistanceOverride subtree, clustered ----
npc_by = defaultdict(list); ai_ref = defaultdict(Counter)
for f in files_for("NpcData"):
    z = zone_of(f)
    for _, el in ET.iterparse(f, events=('end',)):
        if strip(el.tag) != 'Template': continue
        rec = {strip(k): v for k, v in el.attrib.items()}; cl = cluster_of(rec)
        block = el.find('AbnormalityResistanceOverride')
        npc_by[cl].append(sig(block) if block is not None else None)
        if 'aiid' in rec: ai_ref[(z, canon(rec['aiid']))][cl] += 1
        el.clear()
aro = modal_report("NpcData AbnormalityResistanceOverride", npc_by)

# ---- AIData: PeaceState/RandomMove socials + CombatState, clustered by owning NPC ----
peace_by = defaultdict(list); combat_by = defaultdict(list)
for f in files_for("AIData"):
    z = zone_of(f)
    for _, el in ET.iterparse(f, events=('end',)):
        if strip(el.tag) != 'Ai': continue
        refs = ai_ref.get((z, canon(el.get('id'))))
        if not refs: el.clear(); continue
        cl = refs.most_common(1)[0][0]
        ps = el.find('PeaceState')
        rm = ps.find('RandomMove') if ps is not None else None
        peace_by[cl].append(sig(rm) if rm is not None else None)
        cs = el.find('CombatState')
        combat_by[cl].append(sig(cs) if cs is not None else None)
        el.clear()
soc = modal_report("AIData PeaceState/RandomMove (socials)", peace_by)
com = modal_report("AIData CombatState (full combat tree)", combat_by)

# show the modal AbnormalityResistanceOverride list for merchants (the filed gap)
mv = aro.get('MerchantVillager', {})
if mv:
    print("\nMerchantVillager modal AbnormalityResistanceOverride subtree:")
    print(" ", (mv['modal_sig'][:300] + ('...' if len(mv['modal_sig']) > 300 else '')))

# persist signatures (hashed for compactness) for future codegen once DSL supports them
def pack(d):
    return {cl: {**{k: v for k, v in m.items() if k != 'modal_sig'},
                 'modal_sig_sha': hashlib.sha1(m['modal_sig'].encode()).hexdigest()[:12],
                 'modal_sig': m['modal_sig'][:1000]}
            for cl, m in d.items()}
json.dump({'abnormalityResistanceOverride': pack(aro), 'randomMoveSocials': pack(soc),
           'combatState': pack(com)},
          open("derived_list_blocks.json", "w"), indent=2)
print("\nWrote derived_list_blocks.json")
