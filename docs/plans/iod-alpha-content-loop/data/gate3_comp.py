import glob, sys, itertools
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")

def sn(t): return t.split('}', 1)[1] if '}' in t else t

files = sorted(glob.glob(r"D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA\QuestCompensationData\QuestCompensationData-*.xml"))
print("files:", len(files))

paths = Counter()
attrs = Counter()
targets = {1301, 1305, 1311, 1331, 1334, 1336, 1337, 1341, 1343, 1382, 1384}
found = {}          # questId -> (file, element)
samples_left = 3

def walk(e, path):
    tag = sn(e.tag)
    p = path + '/' + tag if path else tag
    paths[p] += 1
    for a in e.attrib:
        if not a.startswith('{'):
            attrs[p + '@' + a] += 1
    for c in e:
        walk(c, p)

def dump(e, d=0):
    a = {k: v for k, v in e.attrib.items() if not k.startswith('{')}
    txt = (e.text or '').strip()
    print('    ' * d + '<' + sn(e.tag) + '> ' + str(a) + ((' text=' + txt[:60]) if txt else ''))
    for c in e:
        dump(c, d + 1)

for f in files:
    root = ET.parse(f).getroot()
    walk(root, '')
    for entry in root:
        at = {k: v for k, v in entry.attrib.items() if not k.startswith('{')}
        # find quest id attribute heuristically
        qid = None
        for k, v in at.items():
            if 'id' in k.lower() or 'quest' in k.lower() or '퀘스트' in k:
                try:
                    qid = int(v.split(',')[-1]) if ',' in v else int(v)
                except ValueError:
                    pass
        # also check child elements for quest number
        if qid is None:
            for c in entry.iter():
                t = sn(c.tag)
                if 'Quest' in t or '퀘스트' in t:
                    txt = (c.text or '').strip()
                    if txt:
                        try:
                            qid = int(txt.split(',')[-1])
                        except ValueError:
                            pass
                        break
        if qid in targets and qid not in found:
            found[qid] = f.split('\\')[-1]
            global_dump = False
            if samples_left > 0:
                print(f"\n=== SAMPLE entry for quest {qid} (in {found[qid]}) ===")
                dump(entry)
                samples_left -= 1

print("\n=== all element paths (corpus-wide) ===")
for p, c in sorted(paths.items()):
    print(f"  {p}: {c}")
print("\n=== attributes ===")
for p, c in sorted(attrs.items()):
    print(f"  {p}: {c}")
print("\n=== target quest presence ===")
for q in sorted(targets):
    print(f"  {q}: {'FOUND in ' + found[q] if q in found else 'MISSING'}")
