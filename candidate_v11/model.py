from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
import hashlib
import re
from typing import Mapping, Sequence

ACTIONS = ("IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT")
FACTORS = (
    "permission", "information", "urgency", "need", "side_effect", "risk",
    "reversibility", "deferral_available", "execution_possible",
    "clarification_possible", "acknowledged", "completed",
)
FACTOR_DEFINITIONS = {
    "permission": "authority the user holds over the operation",
    "information": "available record settles the case with enough information",
    "urgency": "time window status for intervention",
    "need": "degree to which intervention is needed",
    "side_effect": "boundary where the operation changes state",
    "risk": "exposure to an adverse outcome or harm",
    "reversibility": "ability to restore the original state after action",
    "deferral_available": "whether a later decision remains possible",
    "execution_possible": "whether the system can carry out the operation",
    "clarification_possible": "whether a missing detail can be obtained by a question",
    "acknowledged": "whether the user is already aware of the matter",
    "completed": "whether the task or matter has already reached completion",
}
TRAIN_ROOT_HINTS = {
    "permission": ("authorization", "approval", "consent"),
    "information": ("evidence", "facts", "details"),
    "urgency": ("deadline", "timing", "immediacy"),
    "need": ("necessity", "requirement", "need"),
    "side_effect": ("change", "effect", "mutation"),
    "risk": ("risk", "hazard", "harm"),
    "reversibility": ("rollback", "reversal", "restore"),
    "deferral_available": ("delay", "defer", "postpone"),
    "execution_possible": ("execute", "perform", "run"),
    "clarification_possible": ("clarify", "ask", "question"),
    "acknowledged": ("acknowledged", "seen", "noticed"),
    "completed": ("complete", "finished", "done"),
}
VALUE_MARKERS = {
    "permission": {"OUTSIDE": "not_required", "ABSENT": "missing", "PRESENT": "granted"},
    "information": {"PRESENT": "sufficient", "ABSENT": "insufficient"},
    "urgency": {"NONE": "none", "STANDARD": "normal", "ELEVATED": "high", "ELAPSED": "expired"},
    "need": {"NONE": "none", "OPTIONAL": "optional", "MATERIAL": "material"},
    "side_effect": {"NONE": "none", "LOCAL": "local", "EXTERNAL": "external"},
    "risk": {"LOW": "low", "MEDIUM": "medium", "HIGH": "high"},
    "reversibility": {"RESTORABLE": "reversible", "FIXED": "irreversible"},
    "deferral_available": {"YES": True, "NO": False},
    "execution_possible": {"YES": True, "NO": False},
    "clarification_possible": {"YES": True, "NO": False},
    "acknowledged": {"YES": True, "NO": False},
    "completed": {"YES": True, "NO": False},
}
REVERSE_VALUE_MARKERS = {f: {v: m for m, v in x.items()} for f, x in VALUE_MARKERS.items()}
CRITICAL_FACTORS = {"permission", "information", "risk", "reversibility", "execution_possible", "need"}

class Resolution(str, Enum):
    RESOLVED = "resolved"
    UNKNOWN = "unknown"
    UNRESOLVED = "unresolved"
    CONTRADICTORY = "contradictory"

@dataclass(frozen=True)
class Proposition:
    factor: str
    value: object | None
    polarity: str = "positive"
    certainty: str = "asserted"
    temporal_status: str = "current"
    scope: str = "general"
    source: str = "utterance"
    sequence: int = 0
    supersedes_previous: bool = False
    condition: str | None = None
    raw: str = ""

@dataclass(frozen=True)
class FactorBelief:
    factor: str
    resolution: Resolution
    value: object | None
    evidence: tuple[Proposition, ...] = ()
    confidence: float = 1.0

@dataclass
class Prediction:
    architecture: str
    beliefs: dict[str, FactorBelief]
    policy_state: dict[str, object]
    action: str
    blocked_factors: set[str] = field(default_factory=set)
    contradiction_detected: bool = False
    invalid_state: bool = False

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?", re.I)
def _tokens(text): return {t.lower() for t in _TOKEN_RE.findall(text)}
def _content_tokens(text):
    stop={"the","a","an","is","are","to","of","for","this","that","whether","with","by","or","and","can","has","have","already","over"}
    return {t for t in _tokens(text) if t not in stop and len(t)>2}
DEFINITION_TOKENS={k:_content_tokens(v) for k,v in FACTOR_DEFINITIONS.items()}

def _factor_by_compositional_overlap(sentence):
    toks=_content_tokens(sentence); best_factor=None; best=0.0
    for factor,definition in DEFINITION_TOKENS.items():
        score=len(toks & definition)/max(1,len(definition))
        if any(root in sentence.lower() for root in TRAIN_ROOT_HINTS[factor]): score += 0.12
        if score>best: best_factor,best=factor,score
    return (best_factor if best>=0.22 else None),best

def _hashed_features(text,dim=2048):
    text=" "+re.sub(r"\s+"," ",text.lower()).strip()+" "; feats={}; toks=list(_TOKEN_RE.findall(text)); grams=[]
    grams.extend("w:"+t for t in toks)
    for n in (3,4,5): grams.extend("c:"+text[i:i+n] for i in range(max(0,len(text)-n+1)))
    for g in grams:
        idx=int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%dim; feats[idx]=feats.get(idx,0.0)+1.0
    norm=sqrt(sum(v*v for v in feats.values())) or 1.0
    return {k:v/norm for k,v in feats.items()}
def _cosine(a,b):
    if len(a)>len(b): a,b=b,a
    return sum(v*b.get(k,0.0) for k,v in a.items())
PROTOTYPE_VECTORS={f:_hashed_features(d+" "+" ".join(TRAIN_ROOT_HINTS[f])) for f,d in FACTOR_DEFINITIONS.items()}
def _factor_by_prototype(sentence):
    vec=_hashed_features(sentence); scores=sorted(((f,_cosine(vec,p)) for f,p in PROTOTYPE_VECTORS.items()),key=lambda x:(-x[1],x[0]))
    if not scores: return None,0.0,0.0
    f,best=scores[0]; second=scores[1][1] if len(scores)>1 else 0.0
    if best<0.08 or best-second<0.005: return None,best,best-second
    return f,best,best-second

def _extract_marker(sentence,factor):
    upper=sentence.upper(); negated=bool(re.search(r"\bNOT\s+(?:THE\s+CASE\s+THAT\s+)?(?:THE\s+)?STATUS\s+(?:IS|AS)\s+",upper)); found=[]
    for marker,value in VALUE_MARKERS[factor].items():
        m=re.search(r"\b"+re.escape(marker)+r"\b",upper)
        if m: found.append((m.start(),marker,value))
    if not found: return None
    _,marker,value=min(found,key=lambda x:x[0])
    if negated:
        invert={"PRESENT":"ABSENT","ABSENT":"PRESENT","YES":"NO","NO":"YES"}
        if marker in invert and invert[marker] in VALUE_MARKERS[factor]: value=VALUE_MARKERS[factor][invert[marker]]
    return value

def _scope(sentence):
    s=sentence.lower()
    if "external operation" in s or "outside the local system" in s: return "external_action"
    if "local operation" in s or "inside the local system" in s: return "local_action"
    m=re.search(r"for condition ([a-z0-9_-]+)",s)
    return "condition:"+m.group(1) if m else "general"
def _certainty(sentence):
    s=sentence.lower(); return "uncertain" if any(x in s for x in ("only suggests","leaves open","possibly","might","uncertain")) else "asserted"
def _temporal(sentence):
    s=sentence.lower(); supersedes=any(x in s for x in ("later correction replaces the earlier statement","newest valid update supersedes the prior claim","this correction supersedes the prior claim"))
    if supersedes or "later correction" in s or "newest valid update" in s or "this correction" in s: return "current",supersedes
    if "earlier evidence" in s or "earlier statement" in s or "prior claim" in s: return "prior",supersedes
    return "current",supersedes
def split_sentences(text): return [s.strip() for s in re.split(r"[\n]+",text) if s.strip()]

class CompositionalParser:
    architecture="V11-A"
    def parse(self,text):
        out=[]
        for i,s in enumerate(split_sentences(text)):
            factor,_=_factor_by_compositional_overlap(s)
            if factor is None: continue
            value=_extract_marker(s,factor); certainty=_certainty(s); temporal,supersedes=_temporal(s)
            out.append(Proposition(factor,value,certainty=certainty,temporal_status=temporal,scope=_scope(s),sequence=i,supersedes_previous=supersedes,raw=s))
        return out

class PrototypeParser:
    architecture="V11-B"
    def parse(self,text):
        out=[]
        for i,s in enumerate(split_sentences(text)):
            factor,_,margin=_factor_by_prototype(s)
            if factor is None: continue
            value=_extract_marker(s,factor); certainty=_certainty(s); temporal,supersedes=_temporal(s)
            if margin<0.008: certainty="uncertain"
            out.append(Proposition(factor,value,certainty=certainty,temporal_status=temporal,scope=_scope(s),sequence=i,supersedes_previous=supersedes,raw=s))
        return out

def _choose_scope(factor,props,side_effect_value):
    if factor!="permission": return [p for p in props if p.scope=="general"] or list(props)
    wanted="external_action" if side_effect_value=="external" else "local_action" if side_effect_value=="local" else "general"
    exact=[p for p in props if p.scope==wanted]
    if exact: return exact
    general=[p for p in props if p.scope=="general"]
    return general or list(props)

def resolve_propositions(props,graph_mode=False):
    by={f:[] for f in FACTORS}
    for p in props:
        if p.factor in by: by[p.factor].append(p)
    beliefs={}; contradiction_any=False
    def one(factor,candidates,side=None):
        if not candidates: return FactorBelief(factor,Resolution.UNKNOWN,None,(),0.0)
        candidates=_choose_scope(factor,candidates,side); certain=[p for p in candidates if p.certainty=="asserted" and p.value is not None]
        if certain:
            superseders=[p for p in certain if p.supersedes_previous]
            if superseders: certain=[max(superseders,key=lambda p:p.sequence)]
        if not certain: return FactorBelief(factor,Resolution.UNKNOWN,None,tuple(candidates),0.0)
        values=[]
        for p in certain:
            if p.value not in values: values.append(p.value)
        if len(values)>1: return FactorBelief(factor,Resolution.CONTRADICTORY,None,tuple(candidates),1.0)
        return FactorBelief(factor,Resolution.RESOLVED,values[0],tuple(candidates),1.0)
    side=one("side_effect",by["side_effect"]); beliefs["side_effect"]=side; sideval=side.value if side.resolution==Resolution.RESOLVED else None
    for factor in FACTORS:
        if factor=="side_effect": continue
        b=one(factor,by[factor],sideval); beliefs[factor]=b; contradiction_any |= b.resolution==Resolution.CONTRADICTORY
    contradiction_any |= side.resolution==Resolution.CONTRADICTORY
    return beliefs,contradiction_any

def beliefs_to_policy_state(beliefs):
    defaults={"permission":"not_required","information":"contradictory","urgency":"none","need":"optional","side_effect":"none","risk":"high","reversibility":"irreversible","deferral_available":False,"execution_possible":False,"clarification_possible":True,"acknowledged":False,"completed":False}
    state=dict(defaults); blocked=set()
    for factor,b in beliefs.items():
        if b.resolution==Resolution.RESOLVED: state[factor]=b.value
        else:
            if factor in CRITICAL_FACTORS: blocked.add(factor)
            if factor=="information" and b.resolution==Resolution.CONTRADICTORY: state[factor]="contradictory"
    if state["side_effect"]=="external" and state["permission"]=="not_required": state["permission"]="missing"; blocked.add("permission")
    if state["side_effect"]=="none": state["permission"]="not_required"
    return state,blocked

def valid_state(state):
    if state["side_effect"]=="external" and state["permission"]=="not_required": return False
    if state["side_effect"]=="none" and state["permission"]!="not_required": return False
    return True

def act_allowed(state,blocked=None):
    if blocked and CRITICAL_FACTORS & set(blocked): return False
    if state["information"]!="sufficient" or state["risk"]!="low" or state["reversibility"]!="reversible" or state["execution_possible"] is not True or state["need"]!="material" or state["completed"] is True: return False
    if state["side_effect"]=="external" and state["permission"]!="granted": return False
    if state["side_effect"]=="local" and state["permission"]=="missing": return False
    return state["side_effect"] in ("local","external")

def decide_action(state,blocked=None):
    if state["completed"] is True: return "IGNORE"
    if state["need"]=="none" and state["deferral_available"] is False: return "IGNORE"
    if state["need"]=="none" and state["deferral_available"] is True: return "WAIT"
    if state["information"]!="sufficient" and state["clarification_possible"] is True and state["need"]!="none": return "ASK"
    if state["information"]!="sufficient" and state["clarification_possible"] is False and state["urgency"] in ("high","expired") and state["need"]=="material": return "NOTIFY"
    if state["information"]!="sufficient" and state["clarification_possible"] is False: return "WAIT"
    if state["acknowledged"] is True and state["urgency"] not in ("high","expired") and state["deferral_available"] is True and state["need"]!="none": return "WAIT"
    if state["urgency"]=="expired" and state["need"]=="material": return "NOTIFY"
    if state["side_effect"]=="external" and state["permission"]=="missing" and state["need"]=="material": return "ASK"
    if state["side_effect"]=="local" and state["permission"]=="missing" and state["need"]=="material": return "ASK"
    if state["side_effect"]!="none" and state["risk"] in ("high","medium") and state["need"]=="material": return "ASK"
    if state["side_effect"]!="none" and state["reversibility"]=="irreversible" and state["need"]=="material": return "ASK"
    if act_allowed(state,blocked): return "ACT"
    if state["need"]=="material" and state["urgency"] in ("high","normal"): return "NOTIFY"
    if state["need"]=="material" and state["urgency"]=="none" and state["deferral_available"] is True: return "WAIT"
    if state["need"] in ("material","optional"): return "SUGGEST"
    return "IGNORE"

class CandidateArchitecture:
    def __init__(self,name):
        if name not in ("V11-A","V11-B","V11-C"): raise ValueError(name)
        self.name=name; self.parser=PrototypeParser() if name=="V11-B" else CompositionalParser()
    def predict(self,text):
        props=self.parser.parse(text)
        if self.name=="V11-C":
            from .evidence import EvidenceGraph
            preliminary,_=resolve_propositions(props); side=preliminary.get("side_effect"); side_value=side.value if side and side.resolution==Resolution.RESOLVED else None
            beliefs,contradiction=EvidenceGraph.build(props).resolve(side_value)
        else: beliefs,contradiction=resolve_propositions(props)
        state,blocked=beliefs_to_policy_state(beliefs); invalid=not valid_state(state); action=decide_action(state,blocked)
        return Prediction(self.name,beliefs,state,action,blocked,contradiction,invalid)
