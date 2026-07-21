import os, re, json, glob
import xml.etree.ElementTree as ET

DC = r"D:\dev\tera\tera-dc-17_11\DataCenter_Final_USA"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iod_inventory.json")
ISLAND_HZ = {13, 64, 213, 313, 364}

def ln(tag):
    return tag.split('}', 1)[1] if '}' in tag else tag

def leaves(el, path=""):
    """Yield (path, text) for all leaf elements."""
    p = path + "/" + ln(el.tag)
    kids = list(el)
    if not kids:
        txt = (el.text or "").strip()
        yield (p, txt, el.attrib)
    else:
        for k in kids:
            yield from leaves(k, p)

def parse_pair(s):
    m = re.fullmatch(r"(\d+)\s*,\s*(\d+)", s.strip())
    if m:
        return int(m.group(1)), int(m.group(2))
    return None

def find1(el, name):
    for e in el.iter():
        if ln(e.tag) == name:
            return e
    return None

def findall(el, name):
    return [e for e in el.iter() if ln(e.tag) == name]

quests = []
for f in sorted(glob.glob(os.path.join(DC, "Quest", "Quest-*.xml"))):
    try:
        root = ET.parse(f).getroot()
    except ET.ParseError as e:
        print("PARSE ERROR", f, e)
        continue
    q = {"file": os.path.basename(f), "docId": root.get("id")}
    header = None
    tasks_el = None
    for c in root:
        if ln(c.tag) == "Header":
            header = c
        elif ln(c.tag) == "Tasks":
            tasks_el = c

    def htext(name):
        e = find1(header, name) if header is not None else None
        return (e.text or "").strip() if e is not None and e.text else None

    q["questNo"] = htext("Quest번호")            # Quest번호
    q["titleRef"] = htext("Quest제목")           # Quest제목
    q["repeat"] = htext("반복퀘스트")  # 반복퀘스트
    q["minLevel"] = htext("최소레벨")     # 최소레벨
    q["maxLevel"] = htext("최대레벨")     # 최대레벨
    q["recLevel"] = htext("적정수행레벨")  # 적정수행레벨
    q["party"] = htext("적정수행인원")     # 적정수행인원
    q["storyGroup"] = htext("스토리그룹Id")   # 스토리그룹Id
    q["type"] = htext("퀘스트종류")           # 퀘스트종류
    # prerequisites: 선행퀘스트 -> 퀘스트Id
    prereqs = []
    if header is not None:
        pre = find1(header, "선행퀘스트")  # 선행퀘스트
        if pre is not None:
            for qid in findall(pre, "퀘스트Id"):    # 퀘스트Id
                if qid.text and qid.text.strip():
                    prereqs.append(qid.text.strip())
    q["prereqs"] = prereqs
    # start condition children
    start = []
    if header is not None:
        sc = find1(header, "발생조건")  # 발생조건
        if sc is not None:
            for p, txt, at in leaves(sc):
                start.append([p, txt, at] if at else [p, txt])
    q["startCond"] = start
    # class filter
    q["classFilter"] = htext("종족") or htext("클래스")

    # tasks
    tasks = []
    npc_refs = set()
    if tasks_el is not None:
        for t in tasks_el:
            if ln(t.tag) != "Task":
                continue
            tk = {"id": t.get("id")}
            nm = find1(t, "이름")  # 이름
            tk["name"] = (nm.text or "").strip() if nm is not None and nm.text else None
            details = []
            for p, txt, at in leaves(t):
                lp = p
                if txt or at:
                    details.append((lp, txt, at))
                pr = parse_pair(txt) if txt else None
                if pr and ("NPCId" in lp or "몹Id" in lp or "몹Id" in lp):
                    npc_refs.add(pr)
            tk["details"] = [[p, txt, at] if at else [p, txt] for p, txt, at in details]
            tasks.append(tk)
    q["tasks"] = tasks
    # collect ALL pair refs anywhere in doc that look like hz,id
    all_pairs = set()
    for p, txt, at in leaves(root):
        if txt:
            pr = parse_pair(txt)
            if pr and "NPCId" in p:
                all_pairs.add(pr)
    q["npcRefs"] = sorted(all_pairs)
    q["npcZones"] = sorted({a for a, b in all_pairs})
    quests.append(q)

print("total quests parsed:", len(quests))

# island membership
def qno_hz(q):
    pr = parse_pair(q["questNo"] or "")
    return pr[0] if pr else None

island = []
for q in quests:
    hz = qno_hz(q)
    zones = set(q["npcZones"])
    if (hz in ISLAND_HZ) or (zones & ISLAND_HZ):
        q["qnoHz"] = hz
        island.append(q)

print("island quests:", len(island))
zone_dist = {}
for q in island:
    zone_dist[q["qnoHz"]] = zone_dist.get(q["qnoHz"], 0) + 1
print("by questNo hz:", zone_dist)

# StrSheet_Quest map (only ids we need: title refs) - build full map
strq = {}
for f in glob.glob(os.path.join(DC, "StrSheet_Quest", "StrSheet_Quest-*.xml")):
    try:
        root = ET.parse(f).getroot()
    except ET.ParseError:
        continue
    for s in root:
        sid = s.get("id")
        if sid:
            strq[int(sid)] = s.get("string") or (s.text or "").strip()

def resolve_title(q):
    ref = q.get("titleRef") or ""
    m = re.match(r"@quest:(\d+)", ref)
    if m:
        return strq.get(int(m.group(1)))
    return None

for q in island:
    q["title"] = resolve_title(q)

# Compensation map
comp = {}
for f in glob.glob(os.path.join(DC, "QuestCompensationData", "QuestCompensationData-*.xml")):
    try:
        root = ET.parse(f).getroot()
    except ET.ParseError:
        continue
    for qel in root:
        qid = qel.get("questId")
        if qid is None:
            continue
        entries = []
        for ct in qel.iter():
            if ln(ct.tag) == "CompensationType":
                e = dict(ct.attrib)
                items = []
                for it in ct:
                    if ln(it.tag) == "Item":
                        items.append(dict(it.attrib))
                e["items"] = items
                entries.append(e)
        comp[int(qid)] = entries

for q in island:
    did = q.get("docId")
    q["compensation"] = comp.get(int(did)) if did and did.isdigit() else None

# QuestDialog map: (id attr, huntingZoneId attr) per file
dlg = {}
for f in glob.glob(os.path.join(DC, "QuestDialog", "QuestDialog-*.xml")):
    # fast: read first 400 bytes
    with open(f, "r", encoding="utf-8", errors="replace") as fh:
        head = fh.read(500)
    m = re.search(r'<QuestDialog[^>]*\bid="(\d+)"[^>]*huntingZoneId="(\d+)"', head)
    if m:
        did, hz = int(m.group(1)), int(m.group(2))
        size = os.path.getsize(f)
        # count Text nodes cheaply
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        ntext = content.count("<Text ")
        npages = content.count("<Page")
        dlg[(hz, did)] = {"file": os.path.basename(f), "size": size, "texts": ntext, "pages": npages}

for q in island:
    pr = parse_pair(q["questNo"] or "")
    q["dialog"] = dlg.get(pr) if pr else None

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"island": island, "totalQuests": len(quests)}, f, ensure_ascii=False, indent=1)
print("wrote", OUT)

# quick table
island.sort(key=lambda q: (q["qnoHz"] or 0, int(q["docId"] or 0)))
for q in island:
    d = q["dialog"]
    print(f'{q["docId"]:>6} qno={q["questNo"]:<8} lv={q["minLevel"]}/{q["recLevel"]} type={q["type"]} sg={q["storyGroup"]} pre={q["prereqs"]} zones={q["npcZones"]} tasks={len(q["tasks"])} comp={"Y" if q["compensation"] else "-"} dlg={"%dt/%dp"%(d["texts"],d["pages"]) if d else "-"} | {q["title"]}')
