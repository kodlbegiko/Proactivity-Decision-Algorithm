from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import re, hashlib, json

FIELD_ORDER = (
    "permission","information","urgency","need","side_effect","risk",
    "reversibility","deferral_available","execution_possible",
    "clarification_possible","acknowledged","completed",
)
ACT_CRITICAL_FIELDS = {"permission","information","risk","reversibility","execution_possible","side_effect","need"}

DEFAULTS = {
    "permission":"missing","information":"insufficient","urgency":"none","need":"none",
    "side_effect":"none","risk":"high","reversibility":"irreversible",
    "deferral_available":False,"execution_possible":False,"clarification_possible":True,
    "acknowledged":False,"completed":False,
}
DOMAINS = {
    "permission":("not_required","missing","granted"),
    "information":("sufficient","insufficient","contradictory"),
    "urgency":("none","normal","high","expired"),
    "need":("none","optional","material"),
    "side_effect":("none","local","external"),
    "risk":("low","medium","high"),
    "reversibility":("reversible","irreversible"),
    "deferral_available":(False,True),"execution_possible":(False,True),
    "clarification_possible":(False,True),"acknowledged":(False,True),"completed":(False,True),
}

@dataclass(frozen=True)
class SemanticUnit:
    text: str
    clause_index: int
    tokens: tuple[str,...]

@dataclass(frozen=True)
class Proposition:
    field: str
    value: Any
    confidence: float
    clause_index: int
    source: str
    negated: bool = False
    modality: str = "asserted"
    temporal: str = "current"
    scope_depth: int = 0

@dataclass
class FactorHypothesis:
    value: Any
    confidence: float
    evidence: list[Proposition] = field(default_factory=list)
    counterevidence: list[Proposition] = field(default_factory=list)
    status: str = "KNOWN"

@dataclass
class ParseResult:
    state: dict[str,Any]
    factors: dict[str,FactorHypothesis]
    propositions: list[Proposition]
    graph: dict[str,Any]
    action: str

FIELD_HINTS = {
 "permission":{"approval","authorization","permission","consent","clearance","goahead","signoff","permissionless","outsideapprovalscope","notrequired","unauthorized","unauthorised"},
 "information":{"information","facts","evidence","details","reports","record"},
 "urgency":{"urgent","urgency","deadline","timing","priority","pressing","window","overdue","expired","immediate","acute","schedule","routine","nonurgent","unpressing"},
 "need":{"need","needed","required","necessary","optional","intervention","response","actionable","discretionary","elective"},
 "side_effect":{"effect","sideeffect","external","local","outside","system","informational","readonly","thirdparty","remote","internal","onsystem"},
 "risk":{"risk","harm","downside","exposure","danger","safe","dangerous","minimal","severe","substantial"},
 "reversibility":{"reversible","irreversible","undo","undoable","rollback","restore","permanent","recoverable","nonreversible","cannotundo","final"},
 "deferral_available":{"defer","deferral","wait","later","postpone","future","nodeferral","cannotdefer","nowait","postponement"},
 "execution_possible":{"execute","execution","perform","feasible","carryout","path","executable","infeasible","blocked","performable","canexecute","cannotexecute"},
 "clarification_possible":{"clarify","clarification","ask","question","resolve","askable","clarifiable","canask","cannotask","resolvable","unresolvable"},
 "acknowledged":{"acknowledged","noted","seen","aware","confirmed","unacknowledged","notnoted","unseen","unaware"},
 "completed":{"completed","done","finished","resolved","closed","incomplete","unfinished","ongoing"},
}

VALUE_WORDS = {
 "permission":{
   "granted":{"granted","approved","authorized","authorised","cleared","clearance","goahead","consented","signedoff","recorded"},
   "missing":{"missing","pending","unauthorized","unauthorised","absent","awaiting","lacking","uncleared"},
   "not_required":{"unnecessary","notrequired","exempt","outsideapprovalscope","permissionless"},
 },
 "information":{
   "sufficient":{"sufficient","complete","adequate","enough","settled","clear"},
   "insufficient":{"insufficient","incomplete","inadequate","missing","unclear","gaps"},
   "contradictory":{"contradictory","conflicting","inconsistent","disagree","incompatible"},
 },
 "urgency":{
   "none":{"none","nonurgent","routine","canwait","unpressing"},
   "normal":{"normal","ordinary","standard","moderate"},
   "high":{"high","urgent","immediate","acute","pressing","soon"},
   "expired":{"expired","overdue","lapsed","passed","over"},
 },
 "need":{
   "none":{"none","unnecessary","nothing","noaction","notneeded"},
   "optional":{"optional","discretionary","elective","mayhelp","nice"},
   "material":{"material","required","needed","necessary","substantive","must"},
 },
 "side_effect":{
   "none":{"none","informational","read_only","readonly","zero"},
   "local":{"local","onsystem","internal"},
   "external":{"external","outside","thirdparty","remote"},
 },
 "risk":{
   "low":{"low","minimal","small","unlikely","safe"},
   "medium":{"medium","moderate","intermediate","meaningful"},
   "high":{"high","severe","substantial","considerable","dangerous"},
 },
 "reversibility":{
   "reversible":{"reversible","undoable","rollback","restore","recoverable","temporary"},
   "irreversible":{"irreversible","permanent","nonreversible","cannotundo","final"},
 },
 "deferral_available":{True:{"available","defer","later","postpone","wait"},False:{"unavailable","nodeferral","cannotdefer","nowait"}},
 "execution_possible":{True:{"possible","executable","feasible","canexecute","performable"},False:{"impossible","infeasible","cannotexecute","blocked"}},
 "clarification_possible":{True:{"possible","askable","clarifiable","canask","resolvable"},False:{"impossible","unavailable","cannotask","unresolvable"}},
 "acknowledged":{True:{"acknowledged","noted","seen","aware"},False:{"unacknowledged","unseen","notnoted","unaware"}},
 "completed":{True:{"completed","done","finished","resolved","closed"},False:{"incomplete","pending","open","unfinished","ongoing"}},
}

OPPOSITE = {
 ("permission","missing"):"granted", ("permission","granted"):"missing",
 ("information","insufficient"):"sufficient", ("information","sufficient"):"insufficient",
 ("urgency","high"):"none", ("urgency","none"):"high",
 ("need","material"):"none", ("need","none"):"material",
 ("risk","high"):"low", ("risk","low"):"high",
 ("reversibility","irreversible"):"reversible", ("reversibility","reversible"):"irreversible",
 ("deferral_available",True):False, ("deferral_available",False):True,
 ("execution_possible",True):False, ("execution_possible",False):True,
 ("clarification_possible",True):False, ("clarification_possible",False):True,
 ("acknowledged",True):False, ("acknowledged",False):True,
 ("completed",True):False, ("completed",False):True,
}

def _norm(text:str)->str:
    text=text.lower().replace("go-ahead","goahead").replace("sign-off","signoff").replace("side effect","sideeffect")
    text=text.replace("read-only","readonly").replace("carry out","carryout")
    return re.sub(r"[^a-z0-9]+"," ",text).strip()

def _tokens(text:str)->tuple[str,...]:
    return tuple(_norm(text).split())

def split_units(text:str)->list[SemanticUnit]:
    prepared=re.sub(r"\b(?:but|however|although|yet|instead)\b", ";", text, flags=re.I)
    parts=[p.strip() for p in re.split(r"[;.!?\n]+",prepared) if p.strip()]
    return [SemanticUnit(p,i,_tokens(p)) for i,p in enumerate(parts)]

def _field_candidates(unit:SemanticUnit)->list[str]:
    bag=set(unit.tokens)
    out=[]
    for f,hints in FIELD_HINTS.items():
        if bag & hints:
            out.append(f)
    if ({"task","case","work","item"} & bag) and ({"pending","open"} & bag) and "completed" not in out:
        out.append("completed")
    return out

def _value_score(field:str, value:Any, unit:SemanticUnit)->float:
    bag=set(unit.tokens)
    joined="".join(unit.tokens)
    words=VALUE_WORDS[field][value]
    score=0.0
    for w in words:
        if w in bag: score=max(score,1.0)
        elif w in joined: score=max(score,0.92)
    return score

def _negation_near(unit:SemanticUnit, field:str, value:Any)->bool:
    toks=list(unit.tokens)
    neg={"not","no","never","without","lacks","lacking","isnt","isn","neither"}
    valwords=VALUE_WORDS[field][value]
    idxs=[i for i,t in enumerate(toks) if t in valwords]
    if not idxs:
        return False
    for i in idxs:
        if any(toks[j] in neg for j in range(max(0,i-3),i)):
            return True
    return False

def extract_propositions(text:str, variant:str="C")->list[Proposition]:
    units=split_units(text)
    props=[]
    for u in units:
        fields=_field_candidates(u)
        for f in fields:
            if f=="side_effect" and "no" in u.tokens and ("external" in u.tokens or "local" in u.tokens or "effect" in u.tokens):
                props.append(Proposition(f,"none",0.97,u.clause_index,u.text,True,"asserted","current",0)); continue
            if f=="need" and ("nothing" in u.tokens or "noaction" in u.tokens or "notneeded" in u.tokens):
                props.append(Proposition(f,"none",0.97,u.clause_index,u.text,True,"asserted","current",0)); continue
            if f=="urgency" and ("nothing" in u.tokens or "nonurgent" in u.tokens or "unpressing" in u.tokens or "canwait" in u.tokens):
                props.append(Proposition(f,"none",0.97,u.clause_index,u.text,True,"asserted","current",0)); continue
            if f=="clarification_possible" and "no" in u.tokens and "question" in u.tokens:
                props.append(Proposition(f,False,0.98,u.clause_index,u.text,True,"asserted","current",0)); continue
            best=None
            for v in DOMAINS[f]:
                s=_value_score(f,v,u)
                if s and (best is None or s>best[0]):
                    best=(s,v)
            if best is None:
                continue
            s,v=best
            neg=_negation_near(u,f,v)
            if variant=="A":
                neg=False
            if neg and (f,v) in OPPOSITE:
                v=OPPOSITE[(f,v)]; s*=0.96
            discourse_bonus=0.02*u.clause_index if variant=="C" else 0.0
            modality="conditional" if any(x in u.tokens for x in ("if","unless","when")) else "asserted"
            temporal="past" if any(x in u.tokens for x in ("was","were","previously","already")) else ("future" if any(x in u.tokens for x in ("will","later","tomorrow")) else "current")
            if modality=="conditional" and variant!="C":
                s*=0.82
            props.append(Proposition(f,v,min(1.0,s+discourse_bonus),u.clause_index,u.text,neg,modality,temporal,1 if modality=="conditional" else 0))
    return props

def aggregate(props:list[Proposition], variant:str="C")->tuple[dict[str,Any],dict[str,FactorHypothesis]]:
    by={f:[] for f in FIELD_ORDER}
    for p in props: by[p.field].append(p)
    state={}; factors={}
    for f in FIELD_ORDER:
        ps=by[f]
        if not ps:
            state[f]=DEFAULTS[f]
            factors[f]=FactorHypothesis(DEFAULTS[f],0.0,[],[],"SEMANTICALLY_UNSPECIFIED")
            continue
        scores={}
        for p in ps:
            weight=p.confidence
            if variant=="B": weight*=1.0+0.02*p.clause_index
            elif variant=="C":
                weight*=1.0+0.08*p.clause_index
                if p.temporal=="past": weight*=0.75
                if p.modality=="conditional": weight*=0.70
            scores[p.value]=scores.get(p.value,0.0)+weight
        ranked=sorted(scores.items(),key=lambda kv:(kv[1],str(kv[0])),reverse=True)
        topv,tops=ranked[0]; runner=ranked[1][1] if len(ranked)>1 else 0.0
        margin=(tops-runner)/(tops+1e-9)
        status="KNOWN"
        if len(ranked)>1 and margin<0.12: status="CONTRADICTORY_EVIDENCE"
        elif tops<0.50: status="EXTRACTION_UNCERTAIN"
        ev=[p for p in ps if p.value==topv]; ce=[p for p in ps if p.value!=topv]
        state[f]=topv
        factors[f]=FactorHypothesis(topv,min(1.0,tops/(tops+runner+1e-9)),ev,ce,status)
    return state,factors

def policy_action(s:dict[str,Any])->str:
    if s["completed"]: return "IGNORE"
    if s["need"]=="none": return "WAIT" if s["deferral_available"] else "IGNORE"
    if s["information"]!="sufficient" and s["clarification_possible"]: return "ASK"
    if s["information"]!="sufficient" and not s["clarification_possible"] and s["urgency"] in ("high","expired") and s["need"]=="material": return "NOTIFY"
    if s["information"]!="sufficient" and not s["clarification_possible"]: return "WAIT"
    if s["acknowledged"] and s["urgency"] not in ("high","expired") and s["deferral_available"] and s["need"]!="none": return "WAIT"
    if s["urgency"]=="expired" and s["need"]=="material": return "NOTIFY"
    if s["side_effect"]=="external" and s["permission"]=="missing" and s["need"]=="material": return "ASK"
    if s["side_effect"]=="local" and s["permission"]=="missing" and s["need"]=="material": return "ASK"
    if s["side_effect"]!="none" and s["risk"] in ("high","medium") and s["need"]=="material": return "ASK"
    if s["side_effect"]!="none" and s["reversibility"]=="irreversible" and s["need"]=="material": return "ASK"
    ext_act=(s["side_effect"]=="external" and s["permission"]=="granted")
    loc_act=(s["side_effect"]=="local" and s["permission"] in ("not_required","granted"))
    if (ext_act or loc_act) and s["information"]=="sufficient" and s["risk"]=="low" and s["reversibility"]=="reversible" and s["execution_possible"] and s["need"]=="material": return "ACT"
    if s["need"]=="material" and s["urgency"]=="high": return "NOTIFY"
    if s["need"]=="material" and s["urgency"]=="normal": return "NOTIFY"
    if s["need"]=="material" and s["urgency"]=="none" and s["deferral_available"]: return "WAIT"
    if s["need"]=="material": return "SUGGEST"
    if s["need"]=="optional": return "SUGGEST"
    return "IGNORE"

def parse(text:str, variant:str="C")->ParseResult:
    props=extract_propositions(text,variant)
    state,factors=aggregate(props,variant)
    graph={"nodes":[{"id":i,"type":"TypedProposition",**asdict(p)} for i,p in enumerate(props)],"edges":[{"type":"supports","from":i,"to":p.field} for i,p in enumerate(props)]}
    return ParseResult(state,factors,props,graph,policy_action(state))

def act_safe(state:dict[str,Any])->bool:
    return (state["need"]=="material" and state["information"]=="sufficient" and state["risk"]=="low" and state["reversibility"]=="reversible" and state["execution_possible"] and ((state["side_effect"]=="external" and state["permission"]=="granted") or (state["side_effect"]=="local" and state["permission"] in ("granted","not_required"))))

def fingerprint()->str:
    payload=json.dumps({"fields":FIELD_ORDER,"domains":{k:list(v) for k,v in DOMAINS.items()}},sort_keys=True,default=str)
    return hashlib.sha256(payload.encode()).hexdigest()
