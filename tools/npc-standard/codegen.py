"""Regenerate the data-derived archetype packages from derived_standard_all.json:
  - packages/npc-standard/index.yml : NPC template + territory-spawn archetypes
  - packages/ai-standard/index.yml  : AI archetypes (split out per-schema)
Skills are injected into npc-standard separately by codegen_skills.py."""
import json, os, re

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "derived_standard_all.json")
LISTS = json.load(open(os.path.join(HERE, "derived_list_blocks.json")))
PKG = r"D:\dev\mmogate\github\reforged-server-content\reforged\packages"
OUT = os.path.join(PKG, "npc-standard", "index.yml")
AI_OUT = os.path.join(PKG, "ai-standard", "index.yml")
CLUSTERS = ['MerchantVillager', 'QuestVillager', 'NormalMonster',
            'EliteMonster', 'BossMonster', 'ObjectNpc']

d = json.load(open(SRC))
TAU = d['tau']; S = d['standard']

# DSL-supported vocabulary. Derived defaults outside these sets are dropped and
# reported as DSL coverage gaps.
NPC_ROOT = {'villager','questVillager','invincible','resourceType','resourceSize',
            'size','class','scale','race','gender','isObjectNpc','isWideBroadcaster',
            'collideOnMove','dontTurn','lifeTime','elite','unionElite','isFreeNamed',
            'huntingStyle','villagerVolumeOffset','villagerVolumeActiveRange',
            'villagerVolumeHalfHeight','villagerVolumeInteractionDist'}
NPC_BLOCKS = {'abnormality','aggro','anger','critical','criticalAdjust','namePlate',
              'npcOnly','reaction','stackPoint','stat','skillList',
              # unblocked by DSL fixes (996dda59 + empty->null 9f13a78c):
              'abnormalityResistanceOverride','objectNpcAiParam','balanceRef'}
TERR = {'memberId','dir','offsetZ','randomPos','escapeLocation','spawnCount',
        'respawnTime','respawnRandomTime','conditionalSpawn','isAggressiveMonster',
        'isReturn','returnDistance','moveInTerritory','viewRadius','viewAngle',
        'alertRadius','alertAngle','questPatrol','aggroShareGroupId',
        'aggroSendToPartyDistance','aggroSendToClanDistance','aggroIgnorePartyId',
        'aggroReceiveOnlyInSight','randomGroupId',
        # unblocked by DSL empty->null fix (9f13a78c) + confirmed modeled:
        'aggroSendToTerritory','aggroTargetIsUserOnly','battlefieldTeam',
        'cautionStateNoMoving','delaySpawnTimeWhenWorldStart','excludeAggroLimit',
        'isReturnMyTerritory','msgBroadcastingChannel','msgInterval','msgProb',
        'peaceStateNoMoving','popupMsg','voidSpawn'}
dropped = {'npc': set(), 'territory': set()}

def fmt(v):
    if v == '': return '""'
    if v in ('true', 'false'): return v
    try: int(v); return v
    except ValueError: pass
    try: float(v); return v
    except ValueError: pass
    return f'"{v}"'
def bkey(b): return b[0].lower() + b[1:]

def parse_aro(cluster):
    """Modal <Abnormality> list for a cluster (only if the whole block is a default)."""
    info = LISTS.get('abnormalityResistanceOverride', {}).get(cluster)
    if not info or info.get('modal_share', 0) < TAU: return None
    out = []
    for m in re.finditer(r'\(Abnormality ([^)]*)\)', info['modal_sig']):
        kv = dict(p.split('=') for p in m.group(1).split())
        if 'kind' in kv: out.append(kv)
    return out or None

def header(title):
    return ['spec:', '  version: "1.0"', '',
            f'# AUTO-GENERATED {title} from full-population statistical analysis of the live datasheet.',
            f'# tau={TAU} modal-share acceptance; each value annotated share=modal-share, n=sample.',
            '# Source: tools/npc-standard/ (analyze_all.py -> codegen.py). Do not hand-edit.', '',
            'definitions:']

def emit_blocked(out, name, defs, vocab_filter=False, aro_list=None):
    root, blocks = {}, {}
    for k, v in defs.items():
        if '.' in k:
            b, f = k.split('.', 1); bk = bkey(b)
            if vocab_filter and bk not in NPC_BLOCKS:
                dropped['npc'].add(f"{bk}.{f}"); continue
            blocks.setdefault(bk, {})[f] = v
        else:
            if vocab_filter and k not in NPC_ROOT:
                dropped['npc'].add(k); continue
            root[k] = v
    out.append(f'  {name}:')
    for k in sorted(root):
        v = root[k]; out.append(f'    {k}: {fmt(v["value"])}  # share={v["share"]:.0%} n={v["n"]}')
    for b in sorted(blocks):
        out.append(f'    {b}:')
        for f in sorted(blocks[b]):
            v = blocks[b][f]; out.append(f'      {f}: {fmt(v["value"])}  # share={v["share"]:.0%} n={v["n"]}')
        if b == 'abnormalityResistanceOverride' and aro_list:
            out.append('      abnormalities:')
            for a in aro_list:
                out.append(f'        - {{ kind: {a["kind"]}, initRes: {a["initRes"]}, incRes: {a["incRes"]} }}')

def emit_flat(out, name, defs):
    out.append(f'  {name}:')
    for k in sorted(defs):
        if k not in TERR:
            dropped['territory'].add(k); continue
        v = defs[k]   # empty-string now safe (DSL empty->null fix 9f13a78c)
        out.append(f'    {k}: {fmt(v["value"])}  # share={v["share"]:.0%} n={v["n"]}')

# ---- npc-standard: NPC template + territory spawn ----
L = header('NPC template + territory-spawn archetypes')
L.append('  # ===== NPC template archetypes =====')
for c in CLUSTERS: emit_blocked(L, c, S['NpcData'].get(c, {}), vocab_filter=True, aro_list=parse_aro(c))
L.append('  # ===== Territory spawn archetypes =====')
for c in CLUSTERS: emit_flat(L, f'{c}Spawn', S['TerritoryData'].get(c, {}))
L += ['', 'exports:', '  definitions:']
L += [f'    - {c}' for c in CLUSTERS] + [f'    - {c}Spawn' for c in CLUSTERS]
open(OUT, 'w').write('\n'.join(L) + '\n')
print(f"wrote {OUT}  ({len(L)} lines)")

# ---- ai-standard: AI archetypes (split out) ----
A = header('AI archetypes')
A.append('  # ===== AI archetypes =====')
for c in CLUSTERS: emit_blocked(A, f'{c}AI', S['AIData'].get(c, {}))
A += ['', 'exports:', '  definitions:'] + [f'    - {c}AI' for c in CLUSTERS]
open(AI_OUT, 'w').write('\n'.join(A) + '\n')
print(f"wrote {AI_OUT}  ({len(A)} lines)")

print("\nDropped (derived default but outside DSL vocab — coverage-gap candidates):")
print("  NPC:", ', '.join(sorted(dropped['npc'])) or '(none)')
print("  TERRITORY:", ', '.join(sorted(dropped['territory'])) or '(none)')
