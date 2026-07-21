#!/usr/bin/env python
"""Generate the IoD patch 001 villager-dialog gap-fill spec (speechConditions).

Sources
-------
* Roster / scope: docs/plans/iod-alpha-content-loop/data/v31-dialogs.json - a
  v31 survey of every IoD villager that carried a .condition (SpeechCondition)
  file. Each zone's "present" array is the gap-fill target and supplies the
  routing hunting zone, template id, and the free-text Villager note.
* Param attributes: the original v31 .condition files themselves (V31_SRC). The
  survey artifact dropped the optional <Param value=...> threshold, so Param
  type and value are read straight from the source XML per villager. Verified:
  v31 source notes and Text slot ids match the artifact exactly, and no slot
  carries any Param attribute beyond type/value.

The generated spec upserts one speechConditions entry per gap villager, which
DSL writes to VillagerData/{HHHH}0000{TTTTTT}.condition. Upsert keeps the batch
idempotent (re-running produces byte-identical files).

Encoded decisions (mirrored in the emitted header block)
--------------------------------------------------------
* Zone 364 malformed Param: the eight zone-364 v31 files nest a malformed
  <Text type="random"/> where every other villager uses <Param type="random"/>.
  We read the first child element of each Text slot regardless of its tag name,
  so these restore as paramType: random (matching every other single-slot IoD
  villager) rather than an empty slot.
* friendly value: the three friendly slots (64/1001 #2=200, #3=800;
  64/1002 #2=100) carry their reputation thresholds, read from the v31 source.
* Excluded villagers: settled IoD-removal decisions. Only intersecting keys are
  skipped; the rest were never in the survey's dialog set.
"""
import json
import os
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ARTIFACT = os.path.join(
    ROOT, 'docs', 'plans', 'iod-alpha-content-loop', 'data', 'v31-dialogs.json')
OUT = os.path.join(ROOT, 'specs', 'patches', '001', '11-iod-villager-dialogs.yaml')

# Original v31 server .condition files: the authority for Param attributes.
V31_SRC = r'Z:\tera pserver\v31.04\TERAServer\Executable\Bin\Datasheet\VillagerData'

# Villagers removed from IoD by settled decisions; never restore their dialog.
SETTLED_REMOVALS = {
    (64, 9000),    # T-cat Exchanger
    (64, 8000),    # Ellonia
    (213, 1054),   # Sandom cluster
    (213, 1150),
    (213, 1152),
    (213, 1153),
    (213, 1501),
}


def yaml_quote(text):
    """Double-quote a note for YAML. Notes are free of quotes/backslashes and
    long dashes (verified against the source); Korean text is safe verbatim."""
    return '"' + text + '"'


def read_v31_slots(hz, tid):
    """Read the ordered Normal slots (id, paramType, paramValue) for one villager
    straight from its v31 .condition file. The Param element is the first child
    of each <Text> slot; some zone-364 files mislabel it <Text type=...> instead
    of <Param type=...>, so match by position, not tag name."""
    path = os.path.join(V31_SRC, '%04d0000%06d.condition' % (hz, tid))
    root = ET.parse(path).getroot()
    slots = []
    normal = root.find('Normal')
    if normal is not None:
        for text_el in normal.findall('Text'):
            sid = int(text_el.get('id'))
            children = list(text_el)
            inner = children[0] if children else None
            ptype = inner.get('type') if inner is not None else None
            pvalue = inner.get('value') if inner is not None else None
            slots.append((sid, ptype, pvalue))
    return slots


def build_entries(data):
    entries = []
    excluded = []
    for zone_key in sorted(data['zones'], key=int):
        zd = data['zones'][zone_key]
        for v in sorted(zd['present'], key=lambda e: e['templateId']):
            hz = int(v['detail']['villager']['huntingZoneId'])
            tid = v['templateId']
            if (hz, tid) in SETTLED_REMOVALS:
                excluded.append((hz, tid))
                continue
            note = v['detail']['villager']['note']
            slots = read_v31_slots(hz, tid)
            entries.append({'hz': hz, 'tid': tid, 'note': note, 'normal': slots})
    return entries, excluded


HEADER = '''spec:
  version: "1.0"
  schema: v92

# IoD patch 001 Stage 3: villager dialog gap-fill (speechConditions).
#
# Roster/scope: docs/plans/iod-alpha-content-loop/data/v31-dialogs.json
#   ("present" arrays = every IoD villager that carried a v31 SpeechCondition).
# Param attributes (type + value) read straight from the original v31 .condition
#   source files. Generator: tools/dc-restore/gen_speech_specs.py (deterministic).
#
# Each upsert restores one villager's classic .condition file
# (VillagerData/{HHHH}0000{TTTTTT}.condition): its Villager note plus the
# ordered Normal Text slots with their Param type and value. Popup is empty
# throughout (no gap villager carries a Popup slot). Upsert keeps it idempotent.
#
# Encoded decisions:
#   * Zone 364 (8 villagers): the v31 files nest a malformed <Text type="random"/>
#     instead of <Param type="random"/>. Read by position, they restore as
#     paramType: random, matching every other single-slot IoD villager.
#   * friendly slots carry their reputation thresholds from the v31 source:
#     64/1001 #2=200 #3=800, 64/1002 #2=100.
#   * Excluded (settled IoD removals, dialog skipped): 64/9000 T-cat Exchanger.
#     Other settled removals (64/8000, 213/1054,1150,1152,1153,1501) were never
#     in the survey's dialog set.

speechConditions:
  upsert:
'''


def render_slot(sid, ptype, pvalue):
    body = 'id: %d, paramType: %s' % (sid, ptype)
    if pvalue is not None:
        body += ', paramValue: %s' % yaml_quote(pvalue)
    return '        - { %s }' % body


def render(entries):
    lines = [HEADER.rstrip('\n')]
    current_zone = None
    for e in entries:
        if e['hz'] != current_zone:
            current_zone = e['hz']
            lines.append('    # hunting zone %d' % current_zone)
        lines.append('    - huntingZoneId: %d' % e['hz'])
        lines.append('      templateId: %d' % e['tid'])
        lines.append('      note: %s' % yaml_quote(e['note']))
        lines.append('      normal:')
        for sid, ptype, pvalue in e['normal']:
            lines.append(render_slot(sid, ptype, pvalue))
        lines.append('      popup: []')
    return '\n'.join(lines) + '\n'


def main():
    with open(ARTIFACT, encoding='utf-8') as f:
        data = json.load(f)
    entries, excluded = build_entries(data)
    text = render(entries)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

    per_zone = {}
    value_slots = 0
    for e in entries:
        per_zone[e['hz']] = per_zone.get(e['hz'], 0) + 1
        value_slots += sum(1 for s in e['normal'] if s[2] is not None)
    total_present = sum(len(z['present']) for z in data['zones'].values())
    print('wrote', OUT)
    print('emitted per zone:', dict(sorted(per_zone.items())))
    print('emitted total:', len(entries))
    print('slots carrying paramValue:', value_slots)
    print('excluded (present & settled-removal):', sorted(excluded))
    print('artifact gap count (total present):', total_present)
    print('reconcile emitted + excluded == gap:',
          len(entries) + len(excluded), '==', total_present,
          len(entries) + len(excluded) == total_present)


if __name__ == '__main__':
    main()
