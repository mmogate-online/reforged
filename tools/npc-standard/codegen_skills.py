"""Inject <Cluster>Skill archetypes (from derived_skills.json) into the already
-generated packages/npc-standard/index.yml. Run AFTER codegen.py.

Vocab-guarded to the DSL npcSkills schema (schemas/skills/skill-data + property-
blocks). Action/TargetingList (list-typed) and unmodeled fields are dropped and
reported as coverage-gap candidates."""
import json, os

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "derived_skills.json")
OUT = r"D:\dev\mmogate\github\reforged-server-content\reforged\packages\npc-standard\index.yml"
CLUSTERS = ['MerchantVillager', 'QuestVillager', 'NormalMonster',
            'EliteMonster', 'BossMonster', 'ObjectNpc']

# DSL npcSkills vocabulary (from the schema docs)
ROOT = {'abnormalityTargetIsOwner','adjAtkByNpcHp','adjAtkByTargetHp','aiRotateThreshold',
        'allDirectionDefence','applyAttackAnimRate','applyDistanceDamageRate','attackRange',
        'autoUse','canUseOnCombatMode','canUseOnRide','category','changeDirMethodOnSkillEnd',
        'changeDirOnSkillEnd','changeDirToCenter','changeDirection','ignoreAir','ignoreDefence',
        'ignoreLos','ignoreShield','isPlayArmorSound','name','needWeapon','nextSkill',
        'pushtarget','switchInfo','timeRate','totalAtk','type',
        # modeled in DSL 82e3424f (skill L4 reconcile):
        'adjustHeight','attackRangeMin','attackRangeMax','returnAnimName','totalAtkRate'}
BLOCKS = {
 'property': {'movingWithAbnormalId','reactionPendingType','skillPendingType','weaponStatus',
   'defence','adjustLoopRepeat','toCenterWhenNoMove','parentId','afterDefenceSuccess',
   'cancelPressPendingTime','counterIfZeroAtkAttack','deactivateSkillReaction','noCorrectLocation',
   'movingWithAbnormalIdStage','skillDangerLevel','useSkillWhileGravity','useSkillMoving',
   'useSkillWhileReaction','usableDuringActionStep','isItemSkill','category','effectCancelTime',
   'aiReactionStage','cinematicType','abnormalMultiHitAdjustId'},
 'direction': {'toCenterWhenNoMove'},
 'bullet': {'createTime','detachTime','flyingDuration','startSkill','shotSkill',
   'flyingBackDuration','projectileHit','beamEffect'},
 'defence': {'rootMotion','perfectDefenceForAllies','successAnimName','allDirection',
   'adjustCooltimeWhenBrokenByBreakInvincible','adjustCooltimeWhenBrokenByIgnoreDefence',
   'blockOnceBreakInvincibleAttack','breakShieldDistance','coolTime','duration','endAngle',
   'endTime','ignoreAttackSpeed','maxEnduranceBase','nextSkillId','reduceEnduranceRateOnBreak',
   'startAngle','startTime','successCoolTime','triggerSkillId','type',
   'damageReduceValue','successAnimSet'},
 'aggro': {'offensiveSkill','enemyTemplateId','aggroIncValue','aggroWhenStart'},
 'anger': {'attackUpRate','maxAngerPoint'},
 'resistance': {'startTime','endTime','stun','knockdown','pull','fear','sleep','stagger','addResD','value',
   'addResA','addResB','addResC','basicRes','basicIncRes','miniRes','damageRes'},
 'teleport': {'distRange','istrue','range','type'},
 'drain': {'backSkillId','drainGaugeExpireTime','maxDrainGauge'},
 'drainBack': {'backSkillId','gaugeToMpRate'},
 'precondition': {'coolTime','modeNo','coolTimeResetWhenSkillCancel','innerCool','minLevel',
   'noCostSkill','nocTanCount','coolTimeResetProb','successMp','itemId','isItemCountSkill',
   'itemConsumeCount','level','stackCount','pointNo','requiredPoint','questId','abnormalityId',
   'modeChangeMethod'},
 'projectile': {'destroyWhenHit','lifeTime','loopingTime','areaBoxSizeX','areaBoxSizeY',
   'areaBoxSizeZ','despawnDist','explosionDelay','hideFromEnemy','hitEffectOnTarget',
   'instanceShotHit','modelId','speed'},
 # restored — empty-string ref* crash fixed by DSL empty->null (9f13a78c)
 'balanceRef': {'ignoreAttr','isAngerSkill','needBalance','refItemLevel','refLeatherDmgRate',
   'refMailDmgRate','refRobeDmgRate','refTotalAtk','totalAtk','timeRate'},
}
dropped = set()

# Fields the DSL skill schema types as string? (must be quoted, even when the
# value is numeric/bool — otherwise the AOT deserializer index-faults). This is
# the known string?-typing defect, now also affecting npcSkills.
STRING_FIELDS = {
 'adjAtkByTargetHp','changeDirMethodOnSkillEnd','ignoreDefence','name','nextSkill',
 'pushtarget','switchInfo','type','category','returnAnimName','totalAtkRate',
 'defence.successAnimSet',
 'property.reactionPendingType','property.skillPendingType','property.weaponStatus',
 'property.parentId','property.category','property.aiReactionStage','property.cinematicType',
 'bullet.shotSkill','defence.successAnimName','defence.nextSkillId','defence.type',
 'defence.reduceEnduranceRateOnBreak','defence.successCoolTime','defence.triggerSkillId',
 'teleport.distRange','teleport.istrue','teleport.range','teleport.type',
 'balanceRef.ignoreAttr','balanceRef.needBalance','balanceRef.refItemLevel',
 'balanceRef.refLeatherDmgRate','balanceRef.refMailDmgRate','balanceRef.refRobeDmgRate',
 'precondition.itemId','precondition.questId',
}

def fmt(v, force_str=False):
    if force_str: return f'"{v}"'
    if v == '': return '""'
    if v in ('true','false'): return v
    try: int(v); return v
    except ValueError: pass
    try: float(v); return v
    except ValueError: pass
    return f'"{v}"'
def bkey(b): return b[0].lower() + b[1:]

d = json.load(open(SRC)); S = d['standard']
def_lines, exp_lines = [], []
for cl in CLUSTERS:
    defs = S.get(cl, {})
    root, blocks = {}, {}
    for k, v in defs.items():
        if '.' in k:
            b, f = k.split('.', 1); bk = bkey(b)
            if bk not in BLOCKS or f not in BLOCKS[bk]:
                dropped.add(f"{bk}.{f}"); continue
            blocks.setdefault(bk, {})[f] = v
        else:
            if k not in ROOT:
                if k not in ('id', 'templateId', 'skillId'): dropped.add(k)
                continue
            root[k] = v
    name = f"{cl}Skill"
    def_lines.append(f'  {name}:')
    for k in sorted(root):
        v = root[k]; fs = k in STRING_FIELDS
        def_lines.append(f'    {k}: {fmt(v["value"], fs)}  # share={v["share"]:.0%} n={v["n"]}')
    for b in sorted(blocks):
        def_lines.append(f'    {b}:')
        for f in sorted(blocks[b]):
            v = blocks[b][f]; fs = f"{b}.{f}" in STRING_FIELDS
            def_lines.append(f'      {f}: {fmt(v["value"], fs)}  # share={v["share"]:.0%} n={v["n"]}')
    exp_lines.append(f'    - {name}')

# splice into index.yml: insert defs before `exports:`, append exports
txt = open(OUT, encoding='utf-8').read().splitlines()
ei = next(i for i, ln in enumerate(txt) if ln.rstrip() == 'exports:')
head = txt[:ei]
tail = txt[ei:]
head += ['  # ===== NpcSkill archetypes (data-derived, npcSkills section) ====='] + def_lines
out = head + tail + exp_lines
open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(f"injected {len(CLUSTERS)} skill archetypes into {OUT}")
print("dropped (derived but outside DSL npcSkills vocab):", ', '.join(sorted(dropped)) or '(none)')
