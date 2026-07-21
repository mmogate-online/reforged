import glob, re, sys, json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")

SERVER = r"D:\dev\mmogate\tera92\server\Datasheet\QuestData"
CLIENT = r"D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA\Quest"

def strip_ns(tag):
    return tag.split('}', 1)[1] if '}' in tag else tag

def walk(e, path, paths, task_body, cur_task):
    tag = strip_ns(e.tag)
    p = path + '/' + tag if path else tag
    for a in e.attrib:
        if a.startswith('{'):
            continue
        paths[p + '@' + a] += 1
    paths[p] += 1
    if tag == 'Task':
        # find task name in Header/이름
        name = None
        for h in e:
            if strip_ns(h.tag) == 'Header':
                for c in h:
                    if strip_ns(c.tag) == '이름':
                        name = (c.text or '').strip()
        cur_task = name or '?'
    if cur_task and tag not in ('Task',):
        rel = p.split('Task/', 1)[-1] if 'Task/' in p else None
        if rel and (rel.startswith('Body') or rel.startswith('Header')):
            task_body[cur_task][rel] += 1
    for c in e:
        walk(c, p, paths, task_body, cur_task)

def scan(files):
    paths = Counter()
    task_body = defaultdict(Counter)
    nfiles = 0
    for f in files:
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as ex:
            print('PARSE FAIL', f, ex)
            continue
        nfiles += 1
        walk(root, '', paths, task_body, None)
    return paths, task_body, nfiles

sfiles = glob.glob(SERVER + r"\*.quest")
cfiles = glob.glob(CLIENT + r"\Quest-*.xml")
spaths, stasks, sn = scan(sfiles)
cpaths, ctasks, cn = scan(cfiles)
print(f"server files: {sn}, client files: {cn}")
print(f"server distinct paths: {len(spaths)}, client distinct paths: {len(cpaths)}")
print()
sonly = sorted(set(spaths) - set(cpaths))
conly = sorted(set(cpaths) - set(spaths))
print("=== PATHS PRESENT IN SERVER CORPUS BUT NEVER IN ANY CLIENT SHARD (schema-stripped) ===")
for p in sonly:
    print(f"  {p}   (server count: {spaths[p]})")
print()
print("=== PATHS PRESENT IN CLIENT BUT NOT SERVER ===")
for p in conly:
    print(f"  {p}   (client count: {cpaths[p]})")
print()
print("=== PER TASK TYPE: body/header fields, server vs client presence ===")
for tname in sorted(set(stasks) | set(ctasks)):
    sset = set(stasks.get(tname, {}))
    cset = set(ctasks.get(tname, {}))
    print(f"-- Task type: {tname}  (server occurrences of type: {'Y' if tname in stasks else 'N'}, client: {'Y' if tname in ctasks else 'N'})")
    for rel in sorted(sset | cset):
        mark = 'BOTH' if rel in sset and rel in cset else ('SERVER-ONLY' if rel in sset else 'CLIENT-ONLY')
        if mark != 'BOTH':
            print(f"    {mark}: {rel}  s={stasks.get(tname,{}).get(rel,0)} c={ctasks.get(tname,{}).get(rel,0)}")
