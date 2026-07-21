"""
NpcSkillData standard-library analysis (the 954 MB family).

Skills are clustered by their owning NPC's archetype (zone + templateId), then
the same accept-on-modal-share methodology is applied. Because the corpus is
~180k skills / 954 MB, this uses a streaming TWO-PASS design (no rows held in
RAM): pass 1 accumulates per-(fold,cluster,attr) value counters (distinct-capped);
pass 2 re-streams to score 5-fold hold-out reconstruction.

Defaultable fields are the structural/flag attributes (type, pushtarget, needWeapon,
changeDir*, ...). Per-skill damage (totalAtk, attackRange, timeRate, category) is
high-cardinality and correctly stays below tau (= required/identity).
"""
import glob, os, re, json
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

DS = r"D:\dev\mmogate\tera92\server\Datasheet"
TAU, PI, FOLDS, CAP = 0.90, 0.50, 5, 128
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

# ---- owning-NPC cluster map: (zone, templateId) -> cluster ----
npc_cluster = {}
for f in files_for("NpcData"):
    z = zone_of(f)
    for _, el in ET.iterparse(f, events=('end',)):
        if strip(el.tag) != 'Template': continue
        i = el.get('id')
        if i is not None: npc_cluster[(z, canon(i))] = cluster_of(el.attrib)
        el.clear()
print(f"npc_cluster map: {len(npc_cluster)} (zone,templateId) keys")

def flat(el):
    d = {strip(k): v for k, v in el.attrib.items()}
    for c in el:
        bt = strip(c.tag)
        for k, v in c.attrib.items():
            d[f"{bt}.{strip(k)}"] = v
    return d

# ---- PASS 1: per-(fold,cluster,attr) capped value counters ----
foldcnt = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))   # f->c->a->Counter
foldpres = defaultdict(lambda: defaultdict(Counter))                       # f->c->a->present
foldN = defaultdict(Counter)                                              # f->c->N
capped = defaultdict(set)                                                 # (c,a) flagged high-card
idx = 0; skipped = 0
for f in files_for("NpcSkillData"):
    z = zone_of(f)
    for _, el in ET.iterparse(f, events=('end',)):
        if strip(el.tag) != 'Skill': continue
        cl = npc_cluster.get((z, canon(el.get('templateId'))))
        if cl is None: skipped += 1; el.clear(); continue
        fold = idx % FOLDS; idx += 1
        foldN[fold][cl] += 1
        for k, v in flat(el).items():
            foldpres[fold][cl][k] += 1
            cv = canon(v); ctr = foldcnt[fold][cl][k]
            if (cl, k) in capped: continue
            ctr[cv] += 1
            if len(ctr) > CAP:
                capped[(cl, k)].add(True); ctr.clear()
        el.clear()
print(f"pass1: {idx} skills clustered, {skipped} skipped (owner not found)")
clusters = sorted({c for f in foldN for c in foldN[f]}, key=lambda c: -sum(foldN[f][c] for f in foldN))
print("cluster sizes:", {c: sum(foldN[f][c] for f in foldN) for c in clusters})

def derive(folds_used, cl):
    """Accept defaults from the summed counters of the given folds for one cluster."""
    pres = Counter(); vals = defaultdict(Counter); N = sum(foldN[g][cl] for g in folds_used)
    high = set()
    for g in folds_used:
        for a, c in foldpres[g][cl].items(): pres[a] += c
        for a, ctr in foldcnt[g][cl].items():
            if (cl, a) in capped: high.add(a)
            else: vals[a].update(ctr)
    out = {}
    for a, p in pres.items():
        if a in high or p / N < PI or not vals[a]: continue
        mv, mc = vals[a].most_common(1)[0]
        if mc / p >= TAU:
            out[a] = {'value': mv, 'share': mc / p, 'presence': p / N, 'n': p, 'distinct': len(vals[a])}
    return out, N

# ---- PASS 2: 5-fold scoring ----
trained = {f: {c: derive([g for g in range(FOLDS) if g != f], c)[0] for c in clusters} for f in range(FOLDS)}
cor = defaultdict(Counter); tot = defaultdict(Counter); ee = Counter(); et = Counter()
cn = Counter(); cd = Counter()
idx = 0
for f in files_for("NpcSkillData"):
    z = zone_of(f)
    for _, el in ET.iterparse(f, events=('end',)):
        if strip(el.tag) != 'Skill': continue
        cl = npc_cluster.get((z, canon(el.get('templateId'))))
        if cl is None: el.clear(); continue
        fold = idx % FOLDS; idx += 1
        defs = trained[fold][cl]; rec = flat(el)
        et[cl] += 1; ok = True; hit = False
        cd[cl] += len(rec)
        for k, v in rec.items():
            if k in defs:
                hit = True; cn[cl] += 1; tot[cl][k] += 1
                if defs[k]['value'] == canon(v): cor[cl][k] += 1
                else: ok = False
        if hit and ok: ee[cl] += 1
        el.clear()

print(f"\n=== NpcSkillData 5-fold CV (tau={TAU}) ===")
print(f"{'cluster':<18}{'N':>9}{'#dflt':>7}{'attr_acc':>10}{'coverage':>10}{'entry_exact':>13}")
for c in clusters:
    N = sum(foldN[f][c] for f in foldN)
    acc = sum(cor[c].values()) / max(sum(tot[c].values()), 1)
    print(f"{c:<18}{N:>9}{len(tot[c]):>7}{acc:>9.1%}{cn[c]/max(cd[c],1):>10.1%}{ee[c]/max(et[c],1):>12.1%}")

# ---- full-data standard ----
standard = {}
for c in clusters:
    defs, N = derive(list(range(FOLDS)), c)
    standard[c] = {k: {'value': d['value'], 'share': round(d['share'], 3),
                       'presence': round(d['presence'], 3), 'n': d['n'], 'distinct': d['distinct']}
                   for k, d in defs.items()}
json.dump({'tau': TAU, 'pi': PI, 'family': 'NpcSkillData', 'standard': standard},
          open(os.path.join(os.path.dirname(__file__), "derived_skills.json"), "w"), indent=2)
print("\nNormalMonster sample defaults:")
for k, d in sorted(standard.get('NormalMonster', {}).items())[:20]:
    print(f"  {k:<28} = {d['value']!r:<14} share={d['share']:.0%} n={d['n']}")
print(f"  ... ({len(standard.get('NormalMonster', {}))} defaults total)")
print("\nWrote derived_skills.json")
