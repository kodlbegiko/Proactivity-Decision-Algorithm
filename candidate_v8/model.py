from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any
from .policy import STATE_SCHEMA, oracle_action

SAFE_DEFAULT={"permission":"missing","information":"insufficient","urgency":"none","need":"optional","side_effect":"local","risk":"high","reversibility":"irreversible","deferral_available":True,"execution_possible":False,"clarification_possible":True,"acknowledged":False,"completed":False}
PATTERNS={
"permission":{"granted":(r"\b(?:permission|approval|authorization|consent|clearance)\b.{0,40}\b(?:granted|approved|confirmed|given|recorded|secured|obtained|valid|in place|on record)\b",r"\b(?:authorized|cleared)\s+to\s+proceed\b",r"\bgreen light\b",r"\bgo-ahead\b"),"missing":(r"\b(?:permission|approval|authorization|consent|clearance)\b.{0,40}\b(?:missing|absent|pending|withheld|revoked|withdrawn|unavailable|not granted|not approved|not obtained)\b",r"\bwithout\s+(?:permission|approval|authorization|consent|clearance)\b",r"\bno\s+(?:permission|approval|authorization|consent|clearance)\b",r"\black(?:s|ing)?\s+(?:permission|approval|authorization|consent|clearance)\b"),"not_required":(r"\b(?:permission|approval|authorization|consent)\b.{0,35}\b(?:not required|not needed|unnecessary|waived|does not apply|isn't required|is not necessary)\b",r"\bno\s+(?:permission|approval|authorization|consent)\s+(?:is\s+)?(?:needed|required|necessary)\b")},
"information":{"sufficient":(r"\b(?:information|facts|details|evidence|record)\b.{0,40}\b(?:sufficient|complete|adequate|verified|enough|complete enough|ready)\b",r"\b(?:we|the system)\s+(?:have|has|know)\s+enough\b",r"\bnothing material is missing\b",r"\bno missing information\b"),"insufficient":(r"\b(?:information|facts|details|evidence|record)\b.{0,40}\b(?:insufficient|incomplete|missing|inadequate|not enough|has gaps|contains gaps)\b",r"\b(?:we|the system)\s+(?:do not|does not|don't|doesn't)\s+(?:have|know)\s+enough\b"),"contradictory":(r"\b(?:information|facts|records|evidence|accounts)\b.{0,40}\b(?:contradictory|conflicting|inconsistent|disagree|conflict)\b",)},
"urgency":{"none":(r"\b(?:urgency|time pressure|time sensitivity)\b.{0,30}\b(?:none|absent|low|not present)\b",r"\bnot time[- ]sensitive\b",r"\bno immediate deadline\b"),"normal":(r"\b(?:urgency|timing|priority)\b.{0,30}\b(?:normal|routine|ordinary|standard)\b",r"\broutine timing\b"),"high":(r"\b(?:urgency|time pressure|priority)\b.{0,30}\b(?:high|urgent|elevated|immediate)\b",r"\btime[- ]critical\b",r"\bprompt attention\b"),"expired":(r"\b(?:urgency|deadline|window|timing)\b.{0,30}\b(?:expired|passed|overdue|closed)\b",r"\bdeadline has passed\b")},
"need":{"none":(r"\b(?:need|intervention|action)\b.{0,30}\b(?:none|not needed|unnecessary|absent)\b",r"\bno current need\b",r"\bnothing needs doing\b"),"optional":(r"\b(?:need|intervention|action|improvement)\b.{0,35}\b(?:optional|nice-to-have|discretionary|nonessential)\b",r"\boptional improvement\b"),"material":(r"\b(?:need|intervention|action)\b.{0,35}\b(?:material|substantive|consequential|important)\b",r"\bmaterial need\b",r"\bsubstantive intervention\b")},
"side_effect":{"none":(r"\b(?:side effect|state change|effect scope)\b.{0,30}\b(?:none|absent|no state change)\b",r"\bpurely informational\b",r"\bno side effect\b"),"local":(r"\b(?:side effect|effect|state change|scope)\b.{0,30}\b(?:local|locally confined|on-device|internal)\b",r"\blocal state\b"),"external":(r"\b(?:side effect|effect|state change|scope)\b.{0,30}\b(?:external|remote|outside the local system|third-party)\b",r"\bexternal system\b")},
"risk":{"low":(r"\b(?:risk|exposure)\b.{0,30}\b(?:low|minimal|negligible|acceptably low|safe)\b",r"\blow[- ]risk\b",r"\bnot unsafe\b"),"medium":(r"\b(?:risk|exposure)\b.{0,30}\b(?:medium|moderate|intermediate|nontrivial)\b",),"high":(r"\b(?:risk|exposure)\b.{0,30}\b(?:high|elevated|severe|substantial)\b",r"\bhigh[- ]risk\b")},
"reversibility":{"reversible":(r"\b(?:action|change|effect|operation)\b.{0,35}\b(?:reversible|undoable|rollbackable)\b",r"\b(?:rollback|undo)\b.{0,25}\b(?:available|possible|supported)\b",r"\bcan be (?:reversed|undone|rolled back)\b",r"\bnot irreversible\b"),"irreversible":(r"\b(?:action|change|effect|operation)\b.{0,35}\b(?:irreversible|permanent|nonreversible)\b",r"\bno (?:rollback|undo)\b",r"\bcannot be (?:reversed|undone|rolled back)\b")},
"deferral_available":{True:(r"\b(?:deferral|waiting)\b.{0,30}\b(?:available|possible|allowed|remains an option)\b",r"(?<!no )\blater opportunity\b.{0,20}\bexists\b",r"\bcan be deferred\b"),False:(r"\b(?:deferral|waiting|later opportunity)\b.{0,30}\b(?:unavailable|impossible|not allowed|not an option|does not exist)\b",r"\bcannot be deferred\b",r"\bno later opportunity\b")},
"execution_possible":{True:(r"\b(?:execution|operation|path)\b.{0,30}\b(?:possible|available|feasible|ready|can proceed)\b",r"\boperationally feasible\b",r"\bcan actually (?:execute|be executed|run)\b"),False:(r"\b(?:execution|operation|path)\b.{0,30}\b(?:impossible|unavailable|infeasible|blocked|not possible|cannot proceed)\b",r"\bnot operationally feasible\b",r"\bcannot actually (?:execute|be executed|run)\b")},
"clarification_possible":{True:(r"\b(?:clarification|asking|follow-up)\b.{0,30}\b(?:possible|available|open|allowed)\b",r"\bcan (?:ask|request) clarification\b"),False:(r"\b(?:clarification|asking|follow-up)\b.{0,30}\b(?:impossible|unavailable|closed|not possible)\b",r"\bcannot (?:ask|request) clarification\b")},
"acknowledged":{True:(r"(?<!not )(?<!un)\backnowledged\b",r"\backnowledg(?:e)?ment\b.{0,25}\b(?:recorded|confirmed|received)\b"),False:(r"\bnot acknowledged\b",r"\bunacknowledged\b",r"\bno acknowledg(?:e)?ment\b")},
"completed":{True:(r"(?<!not )\b(?:completed|finished|done)\b",r"\bcompletion\b.{0,25}\b(?:confirmed|recorded)\b",r"\bcompletion\b.{0,25}(?<!not )\boccurred\b"),False:(r"\bnot completed\b",r"\bunfinished\b",r"\bremains open\b",r"\bcompletion\b.{0,25}\b(?:not occurred|pending)\b")}}
COMPILED={f:{v:tuple(re.compile(p,re.I) for p in pats) for v,pats in vm.items()} for f,vm in PATTERNS.items()}
CRITICAL={"permission","information","risk","reversibility","execution_possible","need","side_effect","completed"}
AMBIGUITY=re.compile(r"\b(?:maybe|might|possibly|unclear|uncertain|rumor|someone claims|hypothetically|if it were|if .* then)\b",re.I)
EARLIER=re.compile(r"\b(?:earlier|previously|initially|before|formerly|used to|at first)\b",re.I)
CURRENT=re.compile(r"\b(?:now|currently|latest|as of now|at present|today|since then|has now|new status)\b",re.I)
@dataclass(frozen=True)
class EvidenceEvent:
    factor:str; value:Any; text:str; start:int; rank:int; ambiguous:bool
@dataclass(frozen=True)
class Prediction:
    action:str; state:dict[str,Any]; positive_evidence:dict[str,list[str]]; negative_evidence:dict[str,list[str]]; unresolved_fields:tuple[str,...]; act_eligible:bool; prohibited:bool; certain:bool; architecture:str

def _sentences(text):
    out=[]; pos=0
    for piece in re.split(r"(?<=[.!?;])\s+|\n+",text):
        piece=piece.strip()
        if not piece: continue
        idx=text.find(piece,pos); out.append((idx,piece)); pos=max(idx+len(piece),pos)
    return out

def _events(text,factor):
    out=[]
    for base,sentence in _sentences(text):
        rank=3 if CURRENT.search(sentence) else (1 if EARLIER.search(sentence) else 2); ambiguous=bool(AMBIGUITY.search(sentence))
        for value,pats in COMPILED[factor].items():
            for pat in pats:
                for m in pat.finditer(sentence): out.append(EvidenceEvent(factor,value,m.group(0),base+m.start(),rank,ambiguous))
    return out

def _resolve(text,factor,temporal,contradiction):
    events=_events(text,factor); definite=[e for e in events if not e.ambiguous]
    if not definite: return SAFE_DEFAULT[factor],events,False
    best=[e for e in definite if e.rank==max(x.rank for x in definite)] if temporal else definite
    if contradiction and len({e.value for e in best})>1: return SAFE_DEFAULT[factor],events,False
    chosen=max(best,key=lambda e:e.start); return chosen.value,events,True

def _eligibility(state,resolved):
    side=state["side_effect"]
    permission_ok=(side=="external" and state["permission"]=="granted") or (side=="local" and state["permission"] in ("not_required","granted"))
    positive=(side in ("local","external") and permission_ok and state["information"]=="sufficient" and state["risk"]=="low" and state["reversibility"]=="reversible" and state["execution_possible"] is True and state["need"]=="material" and state["completed"] is False)
    all_resolved=all(resolved.get(k,False) for k in CRITICAL)
    prohibited=(state["information"]!="sufficient" or (side=="external" and state["permission"]!="granted") or (side=="local" and state["permission"]=="missing") or state["risk"]!="low" or state["reversibility"]!="reversible" or not state["execution_possible"] or state["need"]!="material" or state["completed"])
    return positive and all_resolved and not prohibited,prohibited

def predict(text,architecture="V8-C"):
    temporal=architecture=="V8-C"; state={}; resolved={}; positive={}; negative={}
    for factor in STATE_SCHEMA:
        value,events,ok=_resolve(text,factor,temporal,True); state[factor]=value; resolved[factor]=ok
        positive[factor]=[e.text for e in events if not e.ambiguous and e.value==value]; negative[factor]=[e.text for e in events if e.ambiguous or e.value!=value]
    eligible,prohibited=_eligibility(state,resolved); action=oracle_action(state); unresolved=tuple(sorted(k for k,v in resolved.items() if not v))
    if action=="ACT" and not eligible:
        action="ASK" if state["clarification_possible"] and state["need"]!="none" else ("NOTIFY" if state["urgency"] in ("high","expired") and state["need"]=="material" else "WAIT")
    return Prediction(action,state,positive,negative,unresolved,eligible,prohibited,len(unresolved)==0,architecture)
