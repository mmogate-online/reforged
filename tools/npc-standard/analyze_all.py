"""
Combined Phase A-C pipeline for NpcData + AIData + TerritoryData.

- NPCs clustered by declared flags (6 semantic clusters).
- AIs clustered by the modal cluster of NPCs that reference them (zone, aiid).
- Territory Npc spawns clustered by their npcTemplateId's NPC cluster.

Outputs: tau-sensitivity curve (NPC), 5-fold CV reconstruction accuracy per
family/cluster, and a combined derived-standard JSON with provenance.
"""
import glob, os, re, json
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

DS = r"D:\dev\mmogate\tera92\server\Datasheet"
PI = 0.50
FOLDS = 5
ZONE = re.compile(r'_(\d+)\.xml$', re.I)

def strip(t): return t.rsplit('}', 1)[-1]
def zone_of(path): m = ZONE.search(os.path.basename(path)); return m.group(1) if m else '?'
def files_for(prefix):
    return sorted({os.path.realpath(p) for p in glob.glob(os.path.join(DS, f"{prefix}*.xml"))})

def canon(v):
    if v is None: return None
    s = v.strip()
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else repr(f)
    except ValueError:
        return s

def cluster_of(t):
    if t.get('isObjectNpc') == 'true':         return 'ObjectNpc'
    if t.get('villager') == 'true':
        return 'QuestVillager' if t.get('questVillager') == 'true' else 'MerchantVillager'
    if canon(t.get('huntingStyle')) == 'raid': return 'BossMonster'
    if t.get('elite') == 'true':               return 'EliteMonster'
    return 'NormalMonster'

# ---------- loaders ----------
def load_npcs():
    rows = []; npc_cluster = {}; ai_ref = defaultdict(Counter)
    for f in files_for("NpcData"):
        z = zone_of(f)
        for _, el in ET.iterparse(f, events=('end',)):
            if strip(el.tag) != 'Template': continue
            rec = {strip(k): v for k, v in el.attrib.items()}
            cl = cluster_of(rec)
            flat = dict(rec)
            for child in el:
                bt = strip(child.tag)
                for k, v in child.attrib.items():
                    flat[f"{bt}.{strip(k)}"] = v
            flat['__cluster__'] = cl
            rows.append(flat)
            if 'id' in rec: npc_cluster[(z, canon(rec['id']))] = cl
            if 'aiid' in rec: ai_ref[(z, canon(rec['aiid']))][cl] += 1
            el.clear()
    return rows, npc_cluster, ai_ref

def load_ais(ai_ref):
    rows = []
    for f in files_for("AIData"):
        z = zone_of(f)
        for _, el in ET.iterparse(f, events=('end',)):
            if strip(el.tag) != 'Ai': continue
            rec = {strip(k): v for k, v in el.attrib.items()}
            refs = ai_ref.get((z, canon(rec.get('id'))))
            if not refs:
                el.clear(); continue            # AI referenced by no NPC -> skip
            flat = dict(rec)
            for child in el:
                bt = strip(child.tag)
                for k, v in child.attrib.items():
                    flat[f"{bt}.{strip(k)}"] = v
            flat['__cluster__'] = refs.most_common(1)[0][0]
            rows.append(flat); el.clear()
    return rows

def load_territory(npc_cluster):
    rows = []
    for f in files_for("TerritoryData"):
        z = zone_of(f)
        for _, el in ET.iterparse(f, events=('end',)):
            if strip(el.tag) != 'Npc': continue
            rec = {strip(k): v for k, v in el.attrib.items()}
            tid = canon(rec.get('npcTemplateId'))
            cl = npc_cluster.get((z, tid))
            if not cl:
                el.clear(); continue
            rec['__cluster__'] = cl
            rows.append(rec); el.clear()
    return rows

# ---------- stats / acceptance ----------
def raw_stats(rows):
    n = len(rows); pres = Counter(); vals = defaultdict(Counter)
    for r in rows:
        for k, v in r.items():
            if k == '__cluster__': continue
            pres[k] += 1; vals[k][canon(v)] += 1
    out = {}
    for k, p in pres.items():
        mv, mc = vals[k].most_common(1)[0]
        out[k] = {'present': p, 'n': n, 'modal': mv, 'mc': mc,
                  'share': mc / p, 'presence': p / n, 'distinct': len(vals[k])}
    return out

def accept(raw, tau, pi=PI):
    return {k: s for k, s in raw.items() if s['presence'] >= pi and s['share'] >= tau}

def cv(rows_by_cluster, tau):
    rep = {}
    for cl, rows in rows_by_cluster.items():
        if len(rows) < FOLDS: continue
        folds = [rows[i::FOLDS] for i in range(FOLDS)]
        cor = Counter(); tot = Counter(); ee = 0; et = 0; cn = 0; cd = 0
        for i in range(FOLDS):
            test = folds[i]; train = [r for j in range(FOLDS) if j != i for r in folds[j]]
            defs = accept(raw_stats(train), tau)
            for r in test:
                et += 1; ok = True
                present = [k for k in r if k != '__cluster__']; cd += len(present)
                hit = False
                for k in present:
                    if k in defs:
                        hit = True; cn += 1; tot[k] += 1
                        if defs[k]['modal'] == canon(r[k]): cor[k] += 1
                        else: ok = False
                if hit and ok: ee += 1
        rep[cl] = {'n': len(rows), 'defaulted': len(tot),
                   'acc': sum(cor.values()) / max(sum(tot.values()), 1),
                   'cov': cn / max(cd, 1), 'exact': ee / max(et, 1)}
    return rep

def print_cv(name, rep):
    print(f"\n=== {name}: 5-fold CV ===")
    print(f"{'cluster':<18}{'N':>7}{'#dflt':>7}{'attr_acc':>10}{'coverage':>10}{'entry_exact':>13}")
    for cl, m in sorted(rep.items(), key=lambda kv: -kv[1]['n']):
        print(f"{cl:<18}{m['n']:>7}{m['defaulted']:>7}{m['acc']:>9.1%}{m['cov']:>10.1%}{m['exact']:>12.1%}")

if __name__ == "__main__":
    npc_rows, npc_cluster, ai_ref = load_npcs()
    ai_rows = load_ais(ai_ref)
    terr_rows = load_territory(npc_cluster)
    fams = {'NpcData': npc_rows, 'AIData': ai_rows, 'TerritoryData': terr_rows}
    for name, rows in fams.items():
        bc = Counter(r['__cluster__'] for r in rows)
        print(f"{name}: {len(rows)} entries  " + "  ".join(f"{c}={n}" for c, n in bc.most_common()))

    # ---- tau-sensitivity curve on NPCs ----
    npc_by = defaultdict(list)
    for r in npc_rows: npc_by[r['__cluster__']].append(r)
    print("\n=== tau-sensitivity curve (NpcData, weighted across clusters) ===")
    print(f"{'tau':>6}{'tot_defaults':>14}{'weighted_acc':>14}{'weighted_cov':>14}")
    for tau in (0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 0.99):
        rep = cv(npc_by, tau)
        N = sum(m['n'] for m in rep.values())
        wacc = sum(m['acc'] * m['n'] for m in rep.values()) / N
        wcov = sum(m['cov'] * m['n'] for m in rep.values()) / N
        tot = sum(m['defaulted'] for m in rep.values())
        print(f"{tau:>6.2f}{tot:>14}{wacc:>13.1%}{wcov:>13.1%}")

    # ---- per-family CV at chosen tau ----
    TAU = 0.90
    by_fam = {}
    for name, rows in fams.items():
        bc = defaultdict(list)
        for r in rows: bc[r['__cluster__']].append(r)
        by_fam[name] = bc
        print_cv(name, cv(bc, TAU))

    # ---- combined derived standard ----
    standard = {}
    for name, bc in by_fam.items():
        standard[name] = {cl: {k: {'value': s['modal'], 'share': round(s['share'], 3),
                                   'presence': round(s['presence'], 3), 'n': s['present'],
                                   'distinct': s['distinct']}
                               for k, s in accept(raw_stats(rs), TAU).items()}
                          for cl, rs in bc.items()}
    with open("derived_standard_all.json", "w") as fh:
        json.dump({'tau': TAU, 'pi': PI, 'standard': standard}, fh, indent=2)
    print("\nWrote derived_standard_all.json")
