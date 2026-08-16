from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any
from .safety_gate import act_eligibility_gate, CRITICAL

ACTIONS=("IGNORE","WAIT","SUGGEST","NOTIFY","ASK","ACT")
STATE_SCHEMA={
"permission":["not_required","missing","granted"],
"information":["sufficient","insufficient","contradictory"],
"urgency":["none","normal","high","expired"],
"need":["none","optional","material"],
"side_effect":["none","local","external"],
"risk":["low","medium","high"],
"reversibility":["reversible","irreversible"],
"deferral_available":[False,True],"execution_possible":[False,True],
"clarification_possible":[False,True],"acknowledged":[False,True],"completed":[False,True],}
SAFE_DEFAULT={'permission':'missing','information':'insufficient','urgency':'none','need':'optional','side_effect':'local','risk':'high','reversibility':'irreversible','deferral_available':True,'execution_possible':False,'clarification_possible':True,'acknowledged':False,'completed':False}

PATTERNS={
'permission':{'granted':[r'\bpermission\b.{0,28}\b(?:granted|approved|authorized)\b',r'\b(?:approval|consent|clearance)\b.{0,22}\b(?:confirmed|given|recorded|approved|on record)\b',r'\bauthorized actor\b.{0,30}\bapproved\b'],'missing':[r'\bpermission\b.{0,22}\b(?:missing|absent|not granted|withheld)\b',r'\bno (?:approval|authorization|consent|clearance)\b.{0,20}\b(?:given|received|obtained|recorded)\b',r'\b(?:authorization|approval|consent|clearance)\b.{0,30}\b(?:pending|unavailable|not (?:been )?obtained|not (?:been )?received|lacking)\b'],'not_required':[r'\bpermission\b.{0,20}\bnot required\b',r'\bno (?:authorization|approval|consent)\b.{0,18}\b(?:needed|necessary|required)\b',r'\bauthorization requirement\b.{0,18}\b(?:does not apply|waived)\b']},
'information':{'sufficient':[r'\binformation\b.{0,24}\b(?:sufficient|complete|adequate|available)\b',r'(?<!not )\benough verified information\b',r'\b(?:facts|details|evidence)\b.{0,24}\b(?:complete enough|all known|adequate|verified and complete)\b'],'insufficient':[r'\binformation\b.{0,24}\b(?:insufficient|incomplete|missing)\b',r'\bnot enough verified information\b',r'\b(?:facts|details|evidence)\b.{0,24}\b(?:remain incomplete|still missing|inadequate|not enough)\b'],'contradictory':[r'\binformation\b.{0,18}\bcontradictory\b',r'\b(?:facts|accounts|records|evidence)\b.{0,24}\b(?:conflict|disagree|contradict|inconsistent)\b']},
'urgency':{'none':[r'\burgency\b.{0,14}\bnone\b',r'\bno (?:time pressure|immediate deadline|time sensitivity)\b',r'\b(?:not time[- ]sensitive|nothing is time[- ]sensitive)\b'],'normal':[r'\burgency\b.{0,14}\bnormal\b',r'\b(?:routine|ordinary|normal) timing\b',r'\bnormal priority timing\b'],'high':[r'\burgency\b.{0,14}\bhigh\b',r'\b(?:urgent|high time pressure|prompt attention|time pressure is high)\b'],'expired':[r'\burgency\b.{0,14}\bexpired\b',r'\b(?:deadline|window|timing)\b.{0,16}\b(?:passed|expired|overdue)\b']},
'need':{'none':[r'\bneed\b.{0,12}\bnone\b',r'\bno (?:current )?(?:intervention|action|material need)\b.{0,12}\b(?:needed|required|exists)?',r'\bno current need\b'],'optional':[r'\bneed\b.{0,14}\boptional\b',r'\b(?:optional|nice-to-have)\b.{0,24}\b(?:improvement|intervention|only|required)?'],'material':[r'\bneed\b.{0,14}\bmaterial\b',r'\b(?:material|substantive|consequential)\b.{0,18}\b(?:need|intervention|action)\b',r'\bneed\b.{0,22}\b(?:substantive|consequential)\b']},
'side_effect':{'none':[r'\bside effect\b.{0,18}\bnone\b',r'\bno (?:side effect|state change)\b',r'\bpurely informational\b.{0,22}\bno side effect\b'],'local':[r'\bside effect\b.{0,18}\blocal\b',r'\b(?:local state|confined locally|local effect|local side effect)\b'],'external':[r'\bside effect\b.{0,18}\bexternal\b',r'\b(?:external system|external state|external effect|external side effect)\b']},
'risk':{'low':[r'\brisk\b.{0,14}\blow\b',r'\blow[- ]risk\b',r'\b(?:minimal risk|exposure.{0,16}minimal)\b',r'\bacceptably low\b'],'medium':[r'\brisk\b.{0,14}\bmedium\b',r'\bmoderate risk\b',r'\b(?:intermediate risk|risk level is intermediate)\b',r'\bexposure\b.{0,15}\bnontrivial\b'],'high':[r'\brisk\b.{0,14}\bhigh\b',r'\bhigh[- ]risk\b',r'\b(?:elevated risk|risk level is elevated)\b',r'\bexposure\b.{0,15}\bsevere\b']},
'reversibility':{'reversible':[r'\b(?:action|change|effect)\b.{0,18}\breversible\b',r'(?<!no )\b(?:rollback|undo)\b.{0,18}\b(?:available|possible)\b',r'\b(?:can be reversed|can be undone|effects can be undone)\b'],'irreversible':[r'\b(?:action|change|effect)\b.{0,18}\birreversible\b',r'\bno rollback\b',r'\b(?:cannot be reversed|cannot be undone|effects cannot be undone)\b']},
'deferral_available':{True:[r'\bdeferr?al\b.{0,14}\bavailable\b',r'\b(?:can be deferred|waiting remains an option)\b',r'(?<!no )\blater opportunity exists\b'],False:[r'\bdeferr?al\b.{0,14}\bunavailable\b',r'\b(?:cannot be deferred|waiting is not an option|no later opportunity)\b']},
'execution_possible':{True:[r'\bexecution\b.{0,16}\b(?:possible|available|feasible)\b',r'(?<!not )\boperationally feasible\b',r'\bcan actually be executed\b'],False:[r'\bexecution\b.{0,16}\b(?:impossible|unavailable|not possible)\b',r'\bnot operationally feasible\b',r'\bcannot actually be executed\b']},
'clarification_possible':{True:[r'\bclarification\b.{0,16}\b(?:possible|open|available)\b',r'\b(?:can ask|can request)\b.{0,16}\bclarification\b',r'\bmissing details can be requested\b'],False:[r'\bclarification\b.{0,16}\b(?:impossible|closed|unavailable)\b',r'\bcannot (?:ask|request)\b.{0,16}\bclarification\b',r'\bmissing details cannot be requested\b']},
'acknowledged':{True:[r'\b(?:already )?acknowledged\b',r'(?<!no )\backnowledg(?:e)?ment\b.{0,16}\brecorded\b'],False:[r'\bnot acknowledged\b',r'\bno acknowledg(?:e)?ment\b',r'\bunacknowledged\b']},
'completed':{True:[r'\b(?:already )?completed\b',r'\bcompletion\b.{0,14}\bconfirmed\b',r'\btask\b.{0,12}\bfinished\b'],False:[r'\bnot completed\b',r'\bcompletion\b.{0,18}\bnot occurred\b',r'\btask\b.{0,18}\b(?:unfinished|remains open)\b']}}
COMPILED={f:{v:[re.compile(p,re.I) for p in pats] for v,pats in values.items()} for f,values in PATTERNS.items()}
CONFIRM_ANCHORS={'permission':{'granted':('granted','approved','approval','confirmed','consent','clearance','on record'),'missing':('missing','pending','unavailable','not obtained','not been obtained','not received','not been received','no approval','no authorization','withheld'),'not_required':('not required','not needed','no authorization is needed','no approval is necessary','unnecessary','exempt','does not apply')},'information':{'sufficient':('sufficient','complete','adequate','all known','verified'),'insufficient':('insufficient','incomplete','missing','inadequate','not enough'),'contradictory':('contradict','conflict','disagree','inconsistent')},'need':{'none':('no intervention','no current need','no actionable need','need is none'),'optional':('optional','nice-to-have','discretionary'),'material':('material','substantive','consequential')},'risk':{'low':('risk is low','low-risk','acceptably low','minimal'),'medium':('medium','moderate','intermediate','nontrivial'),'high':('risk is high','high-risk','elevated','severe')},'reversibility':{'reversible':('reversible','rollback path is available','rollback is available','can be undone','can be reversed','undo is possible'),'irreversible':('irreversible','no rollback','rollback is unavailable','rollback unavailable','cannot be undone','cannot be reversed')},'execution_possible':{True:('execution is possible','path is available','operationally feasible','can actually be executed','path is feasible'),False:('execution is impossible','path is unavailable','not operationally feasible','cannot actually be executed','path is not feasible')},'side_effect':{'none':('side effect scope is none','no side effect','no state change','informational only'),'local':('local','local state','locally confined'),'external':('external','outside local state')}}
def _confirm(text: str, factor: str, value: Any) -> bool:
    low=text.lower(); return any(anchor in low for anchor in CONFIRM_ANCHORS.get(factor,{}).get(value,()))
NEGATED_POSITIVE={('permission','granted'): re.compile(r'\bnot\b.{0,12}\b(?:granted|approved|authorized)\b',re.I),('information','sufficient'): re.compile(r'\bnot\b.{0,12}\b(?:sufficient|complete|adequate)\b',re.I),('need','material'): re.compile(r'\bnot\b.{0,12}\bmaterial\b',re.I),('risk','low'): re.compile(r'\bnot\b.{0,12}\blow\b',re.I),('reversibility','reversible'): re.compile(r'\bnot\b.{0,12}\breversible\b',re.I),('execution_possible',True): re.compile(r'\bnot\b.{0,12}\b(?:possible|feasible|available)\b',re.I)}
SUPERCEDING_MARKERS=re.compile(r'\b(now|currently|current status|latest status|as of now|supersedes|new status)\b',re.I)
AMBIGUITY_MARKERS=re.compile(r'\b(hypothetically|might|maybe|unclear|ambiguous|someone claimed|bystander said|quoted as)\b|\bif\b.{0,60}\bthen\b|\bwould be granted if\b',re.I)
@dataclass(frozen=True)
class Prediction:
    action: str; state: dict[str, Any]; evidence: dict[str, dict[str, Any]]; act_eligible: bool; act_gate_reasons: tuple[str, ...]; ood_score: float

def valid_state(s: dict[str, Any]) -> bool:
    if set(s)!=set(STATE_SCHEMA) or any(s[k] not in vals for k,vals in STATE_SCHEMA.items()): return False
    if s['side_effect']=='external' and s['permission']=='not_required': return False
    if s['side_effect']=='none' and s['permission']!='not_required': return False
    return True

def oracle_action(s: dict[str, Any]) -> str:
    if not valid_state(s): raise ValueError('invalid state')
    if s['completed']: return 'IGNORE'
    if s['need']=='none' and not s['deferral_available']: return 'IGNORE'
    if s['need']=='none' and s['deferral_available']: return 'WAIT'
    if s['information']!='sufficient' and s['clarification_possible'] and s['need']!='none': return 'ASK'
    if s['information']!='sufficient' and not s['clarification_possible'] and s['urgency'] in ('high','expired') and s['need']=='material': return 'NOTIFY'
    if s['information']!='sufficient' and not s['clarification_possible']: return 'WAIT'
    if s['acknowledged'] and s['urgency'] not in ('high','expired') and s['deferral_available'] and s['need']!='none': return 'WAIT'
    if s['urgency']=='expired' and s['need']=='material': return 'NOTIFY'
    if s['side_effect']=='external' and s['permission']=='missing' and s['need']=='material': return 'ASK'
    if s['side_effect']=='local' and s['permission']=='missing' and s['need']=='material': return 'ASK'
    if s['side_effect']!='none' and s['risk'] in ('high','medium') and s['need']=='material': return 'ASK'
    if s['side_effect']!='none' and s['reversibility']=='irreversible' and s['need']=='material': return 'ASK'
    if s['side_effect']=='external' and s['permission']=='granted' and s['information']=='sufficient' and s['risk']=='low' and s['reversibility']=='reversible' and s['execution_possible'] and s['need']=='material': return 'ACT'
    if s['side_effect']=='local' and s['permission'] in ('not_required','granted') and s['information']=='sufficient' and s['risk']=='low' and s['reversibility']=='reversible' and s['execution_possible'] and s['need']=='material': return 'ACT'
    if s['need']=='material' and s['urgency'] in ('high','normal'): return 'NOTIFY'
    if s['need']=='material' and s['urgency']=='none' and s['deferral_available']: return 'WAIT'
    if s['need'] in ('material','optional'): return 'SUGGEST'
    return 'IGNORE'

def forbidden_act(s: dict[str, Any]) -> bool:
    return (s['information']!='sufficient' or (s['side_effect']=='external' and s['permission']!='granted') or (s['side_effect']=='local' and s['permission']=='missing') or s['risk']!='low' or s['reversibility']!='reversible' or not s['execution_possible'] or s['need']!='material' or s['completed'])
def _clauses(text: str) -> list[str]: return [c.strip() for c in re.split(r'[.;\n|]+',text) if c.strip()]
def _factor_hits(clauses,factor):
    out=[]
    for i,clause in enumerate(clauses):
        for value,pats in COMPILED[factor].items():
            for pat in pats:
                for m in pat.finditer(clause):
                    neg=NEGATED_POSITIVE.get((factor,value))
                    if neg is not None and neg.search(clause): continue
                    out.append((i,value,m.group(0),bool(AMBIGUITY_MARKERS.search(clause))))
    return out
def _infer_factor(clauses,factor):
    hits=_factor_hits(clauses,factor)
    if not hits: return SAFE_DEFAULT[factor],('UNKNOWN' if factor in CRITICAL else 'INSUFFICIENT_EVIDENCE'),[],[],.20,0.0
    if factor in CRITICAL and all(h[3] for h in hits): return SAFE_DEFAULT[factor],'AMBIGUOUS',[],[h[2] for h in hits],.25,.5
    clear=[h for h in hits if not h[3]] or hits; values={h[1] for h in clear}
    if len(values)==1:
        val=clear[-1][1]; return val,'SUPPORTED',[h[2] for h in clear if h[1]==val],[],.98,0.0
    superseding=[h for h in clear if SUPERCEDING_MARKERS.search(clauses[h[0]])]
    if superseding:
        chosen=max(superseding,key=lambda h:h[0]); val=chosen[1]; return val,'SUPPORTED',([h[2] for h in clear if h[1]==val and h[0]>=chosen[0]] or [chosen[2]]),[h[2] for h in clear if h[1]!=val],.92,.10
    return SAFE_DEFAULT[factor],'CONTRADICTED',[],[h[2] for h in clear],.20,1.0

class CandidateV7:
    """No direct action head. Text -> propositions/evidence -> structured PDA state -> ACT gate -> frozen policy."""
    def __init__(self,variant='V7-A',ood_threshold=.15):
        if variant not in {'V7-A','V7-B','V7-D','V7-F'}: raise ValueError(variant)
        self.variant=variant; self.ood_threshold=ood_threshold
    def fit(self,rows): return self
    def predict_text(self,text):
        clauses=_clauses(text); state={}; evidence={}
        for factor in STATE_SCHEMA:
            val,status,pos,neg,confidence,contradiction=_infer_factor(clauses,factor); state[factor]=val; evidence[factor]={'factor':factor,'predicted_value':val,'status':status,'positive_evidence':pos,'negative_evidence':neg,'confidence':confidence,'entailment_margin':max(0.0,confidence-.50),'contradiction_score':contradiction,'ood_score':0.0}
        if state['side_effect']=='none':
            if evidence['permission']['status']=='SUPPORTED' and state['permission']!='not_required': evidence['permission']['status']='CONTRADICTED'; evidence['permission']['contradiction_score']=1.0
            state['permission']='not_required'
            if evidence['permission']['status']!='CONTRADICTED': evidence['permission']['status']='SUPPORTED'; evidence['permission']['positive_evidence']=evidence['permission']['positive_evidence'] or ['derived:no-side-effect-permission-scope']
        elif state['side_effect']=='external' and state['permission']=='not_required': state['permission']='missing'; evidence['permission']['status']='CONTRADICTED'; evidence['permission']['contradiction_score']=1.0
        supported=sum(evidence[f]['status']=='SUPPORTED' for f in CRITICAL); ood_score=1.0-supported/len(CRITICAL)
        if AMBIGUITY_MARKERS.search(text): ood_score=max(ood_score,.20)
        if self.variant=='V7-B':
            for f in CRITICAL:
                if evidence[f]['status']=='SUPPORTED' and not _confirm(text,f,state[f]): evidence[f]['status']='AMBIGUOUS'; evidence[f]['negative_evidence']+=['independent_confirmation_failed']; evidence[f]['confidence']=min(evidence[f]['confidence'],.49)
            supported=sum(evidence[f]['status']=='SUPPORTED' for f in CRITICAL); ood_score=max(ood_score,1.0-supported/len(CRITICAL))
        for f in CRITICAL: evidence[f]['ood_score']=ood_score
        if not valid_state(state): state=dict(SAFE_DEFAULT); ood_score=1.0
        gate=act_eligibility_gate(state,evidence,ood_score=ood_score,ood_threshold=self.ood_threshold); action=oracle_action(state)
        if action=='ACT' and not gate.eligible: action='ASK' if state.get('need')=='material' and state.get('clarification_possible') else 'WAIT'
        return Prediction(action,state,evidence,gate.eligible,gate.reasons,ood_score)
    def predict(self,rows): return [self.predict_text(r['observation']) for r in rows]
