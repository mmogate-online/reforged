"""Extract kill requirements from IoD quest XML files."""
import os
import sys
from xml.etree import ElementTree as ET

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUEST_DIR = r"D:\dev\mmogate\tera92\server\Datasheet\QuestData"

IOD_QUESTS = [
    # Story Group 1
    1301, 1303, 1304, 1305, 1329, 1331,
    1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379,
    1382, 1383, 1384,
    # Story Group 2
    1309, 1311, 1313, 1315, 1316, 1317, 1350,
]

HUNT_DELIVER = "사냥전달Task"   # 사냥전달Task
HUNT_ONLY    = "사냥Task"               # 사냥Task
GROUP_HUNT   = "그룹사냥Task"   # 그룹사냥Task

ITEM_MAKE        = "아이템작성"   # 아이템작성
DELIVERY_QTY     = "전달수량"          # 전달수량
MONSTER_ID       = "몬스터Id"           # 몬스터Id

HUNT_GROUP       = "사냥그룹"          # 사냥그룹
QTY_TAG          = "수량"                       # 수량
COND_TAG         = "진행조건"           # 진행조건
MONSTER_SPEC     = "몬스터지정"     # 몬스터지정

for qid in sorted(IOD_QUESTS):
    path = os.path.join(QUEST_DIR, f"{qid:06d}.quest")
    if not os.path.exists(path):
        print(f"Q{qid}: NOT FOUND")
        continue

    tree = ET.parse(path)
    root = tree.getroot()
    q_kills = []

    for task in root.findall(".//Task"):
        name_el = task.find("Header/이름")   # 이름
        if name_el is None:
            continue
        task_type = (name_el.text or "").strip()

        if task_type == HUNT_DELIVER:
            # Structure: <아이템작성><아이템작성><전달수량>N</전달수량><몬스터지정><몬스터Id>z,id</몬스터Id>
            outer = task.find(".//" + ITEM_MAKE)
            if outer is None:
                continue
            for inner in outer.findall(ITEM_MAKE):
                qty_el = inner.find(DELIVERY_QTY)
                qty = int(qty_el.text.strip()) if qty_el is not None and qty_el.text else 0
                mob_ids = [m.text for m in inner.findall(".//" + MONSTER_ID)]
                q_kills.append(("DELIVER", mob_ids, qty))

        elif task_type in (HUNT_ONLY, GROUP_HUNT):
            # Try <사냥그룹><수량> and <몬스터Id>
            for hg in task.findall(".//" + HUNT_GROUP):
                qty_el = hg.find(QTY_TAG)
                mob_el = hg.find(".//" + MONSTER_ID)
                qty    = int(qty_el.text.strip()) if qty_el is not None and qty_el.text else 0
                mob_id = mob_el.text if mob_el is not None else "?"
                q_kills.append(("HUNT", [mob_id], qty))
            # Fallback: <몬스터지정> list with <수량>
            if not q_kills or q_kills[-1][0] != "HUNT":
                qty_el = task.find(".//" + QTY_TAG)
                qty    = int(qty_el.text.strip()) if qty_el is not None and qty_el.text else 0
                mob_ids = [m.text for m in task.findall(".//" + MONSTER_ID)]
                if mob_ids and qty:
                    q_kills.append(("HUNT", mob_ids, qty))

    if q_kills:
        total = sum(q[2] for q in q_kills if isinstance(q[2], int))
        print(f"Q{qid} (total kills={total}):")
        for (ttype, mobs, qty) in q_kills:
            print(f"  [{ttype}] x{qty}  mobs={mobs}")
    else:
        names = [t.findtext("Header/이름", "?") for t in root.findall(".//Task")]
        hunt_names = [n for n in names if any(h in n for h in ["Task", "task"])]
        # Only print if no kill tasks at all
        print(f"Q{qid}: no kill tasks  (task types: {names})")
