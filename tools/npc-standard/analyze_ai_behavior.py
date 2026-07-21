"""
Phases A-E: data-accurate combat-AI classification.

Structure vs parameter split: an AI's STRUCTURAL SKELETON (element nesting + bool/
string/enum attrs, with numeric leaf VALUES stripped) defines its behavior class;
the numeric leaves are PARAMETERS defaulted within the class. Classes are discovered
globally (across zones/ids), not imposed by flags.

A  extract per-AI skeleton (4 granularity levels) + params
B  concentration curve per level (the go/no-go gate)
C  define classes (skeleton groups >= MIN_CLASS) + cross-check vs flag-cluster / shared aiid
D  within-class param defaults (tau=0.90)
E  5-fold CV reconstruction (param accuracy; structure is exact within class)
"""
import glob, os, re, json, hashlib
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

DS = r"D:\dev\mmogate\tera92\server\Datasheet"
TAU, PI, FOLDS, MIN_CLASS = 0.90, 0.50, 5, 30
IGNORE = {'id', 'name', 'desc'}          # identity/label attrs excluded from skeleton & params
ZONE = re.compile(r'_(\d+)\.xml$', re.I)
def strip(t): return t.rsplit('}', 1)[-1]
def zone_of(p): m = ZONE.search(os.path.basename(p)); return m.group(1) if m else '?'
def files_for(p): return sorted({os.path.realpath(x) for x in glob.glob(os.path.join(DS, f"{p}*.xml"))})
def isnum(v):
    try: float(v); return True
    except (ValueError, TypeError): return False
def canon(v):
    s = (v or '').strip()
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

KEEP_L3 = {'enable', 'normalBehaviorType', 'angerBehaviorType', 'orderType', 'type', 'default'}

def skel(el, level):
    """Structural skeleton at a granularity level.
       L0 exact (numeric values kept) · L1 numeric->#  · L2 drop numeric attrs
       · L3 keep only whitelisted structural attrs."""
    tag = strip(el.tag); attrs = []
    for k in sorted(el.attrib):
        kk = strip(k)
        if kk in IGNORE: continue
        v = el.attrib[k]
        if isnum(v):
            if level == 0: attrs.append(f"{kk}={canon(v)}")
            elif level == 1: attrs.append(f"{kk}=#")
            # L2/L3: numeric attrs dropped
        else:
            if level >= 3 and kk not in KEEP_L3: continue
            attrs.append(f"{kk}={canon(v)}")
    kids = ','.join(skel(c, level) for c in el)
    body = ' '.join(attrs)
    return f"({tag} {body}[{kids}])" if kids else f"({tag} {body})"

def params(el, path=''):
    """Numeric leaves keyed by a stable structural path (sibling-indexed)."""
    out = {}; tag = strip(el.tag); here = f"{path}{tag}"
    for k in sorted(el.attrib):
        kk = strip(k)
        if kk in IGNORE: continue
        if isnum(el.attrib[k]): out[f"{here}@{kk}"] = canon(el.attrib[k])
    seen = Counter()
    for c in el:
        ct = strip(c.tag); out.update(params(c, f"{here}/{ct}{seen[ct]}/")); seen[ct] += 1
    return out

def h(s): return hashlib.sha1(s.encode()).hexdigest()[:12]

# ---- owning-NPC cluster per (zone, aiid) ----
ai_cluster = defaultdict(Counter)
for f in files_for("NpcData"):
    z = zone_of(f)
    for _, el in ET.iterparse(f, events=('end',)):
        if strip(el.tag) != 'Template': continue
        a = el.get('aiid')
        if a is not None: ai_cluster[(z, canon(a))][cluster_of(el.attrib)] += 1
        el.clear()

# ---- A: extract skeletons + params for referenced AIs ----
recs = []   # {skelL: {0..3}, params, cluster, shareKey}
for f in files_for("AIData"):
    z = zone_of(f)
    for _, el in ET.iterparse(f, events=('end',)):
        if strip(el.tag) != 'Ai': continue
        refs = ai_cluster.get((z, canon(el.get('id'))))
        if not refs: el.clear(); continue
        recs.append({
            'L': {lv: h(skel(el, lv)) for lv in (0, 1, 2, 3)},
            'p': params(el),
            'cl': refs.most_common(1)[0][0],
            'share': (z, canon(el.get('id'))),
        })
        el.clear()
N = len(recs)
print(f"[A] {N} referenced AIs extracted ({len({r['share'] for r in recs})} distinct zone/aiid)")

# combat-only view: the question this whole effort is about (villagers/objects mask it)
COMBAT = {'NormalMonster', 'EliteMonster', 'BossMonster'}
combat = [r for r in recs if r['cl'] in COMBAT]
print(f"\n[B-combat] {len(combat)} combat AIs (Normal/Elite/Boss) — concentration:")
print(f"{'level':<10}{'distinct':>9}{'top10':>8}{'top20':>8}{'top50':>8}{'>=30 cover':>12}")
for lv, lbl in [(1, 'L1 skel'), (2, 'L2 struct'), (3, 'L3 coarse')]:
    c = Counter(r['L'][lv] for r in combat); M = len(combat)
    cov = lambda k: 100 * sum(n for _, n in c.most_common(k)) / M
    big = sum(n for _, n in c.items() if n >= MIN_CLASS)
    print(f"{lbl:<10}{len(c):>9}{cov(10):>7.0f}%{cov(20):>7.0f}%{cov(50):>7.0f}%{100*big/M:>11.0f}%")

# ---- B: concentration curve per granularity level ----
print("\n[B] concentration (distinct skeletons / cumulative coverage by top-K)")
print(f"{'level':<8}{'distinct':>9}{'top5':>8}{'top10':>8}{'top20':>8}{'top50':>8}")
def cover(c, k): return 100 * sum(n for _, n in c.most_common(k)) / N
for lv, label in [(0, 'L0 exact'), (1, 'L1 skel'), (2, 'L2 struct'), (3, 'L3 coarse')]:
    c = Counter(r['L'][lv] for r in recs)
    print(f"{label:<8}{len(c):>9}{cover(c,5):>7.0f}%{cover(c,10):>7.0f}%{cover(c,20):>7.0f}%{cover(c,50):>7.0f}%")

# ---- C+D+E at two candidate levels (skeleton L1, structure L2) ----
def accept(rows):
    n = len(rows); pres = Counter(); vals = defaultdict(Counter)
    for r in rows:
        for k, v in r['p'].items(): pres[k] += 1; vals[k][v] += 1
    out = {}
    for k, pcnt in pres.items():
        if pcnt / n < PI: continue
        mv, mc = vals[k].most_common(1)[0]
        if mc / pcnt >= TAU: out[k] = {'value': mv, 'share': mc / pcnt, 'presence': pcnt / n, 'n': pcnt}
    return out

def run_level(lv):
    groups = defaultdict(list)
    for r in recs: groups[r['L'][lv]].append(r)
    classes = {g: rows for g, rows in groups.items() if len(rows) >= MIN_CLASS}
    covered = sum(len(v) for v in classes.values())
    # CV (param accuracy) over class members
    cor = tot = 0; exact = etot = 0
    for g, rows in classes.items():
        folds = [rows[i::FOLDS] for i in range(FOLDS)]
        for i in range(FOLDS):
            test = folds[i]; train = [r for j in range(FOLDS) if j != i for r in folds[j]]
            if not train: continue
            defs = accept(train)
            for r in test:
                etot += 1; ok = True; hit = False
                for k, d in defs.items():
                    hit = True; tot += 1
                    if r['p'].get(k) == d['value']: cor += 1
                    else: ok = False
                if hit and ok: exact += 1
    return {'lv': lv, 'classes': len(classes), 'covered': covered,
            'coverage': covered / N, 'param_acc': cor / max(tot, 1),
            'entry_exact': exact / max(etot, 1),
            'avg_defaults': (sum(len(accept(v)) for v in classes.values()) / max(len(classes), 1)),
            'groups': classes}

print(f"\n[C-E] classes (>= {MIN_CLASS} AIs) + within-class param CV")
print(f"{'level':<8}{'#classes':>9}{'pop_cov':>9}{'param_acc':>11}{'entry_exact':>13}{'avg_dflt':>9}")
results = {}
for lv in (1, 2):
    R = run_level(lv); results[lv] = R
    print(f"L{lv:<7}{R['classes']:>9}{R['coverage']:>8.0%}{R['param_acc']:>10.1%}{R['entry_exact']:>12.1%}{R['avg_defaults']:>9.1f}")

# pick the level with best coverage*accuracy among the two
best = max(results.values(), key=lambda R: R['coverage'] * R['param_acc'])
lv = best['lv']; classes = best['groups']
print(f"\nselected level L{lv}: {best['classes']} classes cover {best['coverage']:.0%} of AIs "
      f"at {best['param_acc']:.1%} param accuracy")

# cross-check: top classes vs flag-cluster + AI sharing
print("\ntop behavior classes (size · dominant flag-cluster · distinct shared-AI count):")
top = sorted(classes.items(), key=lambda kv: -len(kv[1]))[:12]
catalog = {}
for gid, rows in top:
    flag = Counter(r['cl'] for r in rows).most_common(1)[0]
    shares = len({r['share'] for r in rows})
    defs = accept(rows)
    catalog[gid] = {'size': len(rows), 'dominant_cluster': flag[0],
                    'dominant_share': flag[1] / len(rows), 'distinct_ais': shares,
                    'param_defaults': len(defs)}
    print(f"  {gid}  n={len(rows):<5} {flag[0]:<16} ({flag[1]/len(rows):.0%})  "
          f"sharedAIs={shares:<4} params={len(defs)}")

tail = N - best['covered']
print(f"\nbespoke tail: {tail} AIs ({tail/N:.0%}) below MIN_CLASS={MIN_CLASS} — stay hand-authored")

out = {'tau': TAU, 'level': lv, 'min_class': MIN_CLASS, 'n_ais': N,
       'concentration': {f'L{lv2}': dict(Counter(r['L'][lv2] for r in recs).most_common(50)) for lv2 in (0,1,2,3)},
       'selected': {k: v for k, v in best.items() if k != 'groups'},
       'classes': {gid: {**catalog.get(gid, {}),
                         'params': {k: {'value': d['value'], 'share': round(d['share'],3),
                                        'presence': round(d['presence'],3), 'n': d['n']}
                                    for k, d in accept(rows).items()}}
                   for gid, rows in classes.items()}}
json.dump(out, open(os.path.join(os.path.dirname(__file__), "derived_ai_behavior.json"), "w"), indent=2)
print("\nWrote derived_ai_behavior.json")
