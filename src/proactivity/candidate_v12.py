from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Iterable
import re

ACTIONS=("IGNORE","WAIT","SUGGEST","NOTIFY","ASK","ACT")
FIELD_ORDER=("permission","information","urgency","need","side_effect","risk","reversibility","deferral_available","execution_possible","clarification_possible","acknowledged","completed")
ACT_CRITICAL={"permission","information","risk","reversibility","execution_possible","side_effect","need"}
DOMAINS={
"permission":("not_required","missing","granted"),"information":("sufficient","insufficient","contradictory"),
"urgency":("none","normal","high","expired"),"need":("none","optional","material"),"side_effect":("none","local","external"),
"risk":("low","medium","high"),"reversibility":("reversible","irreversible"),"deferral_available":(False,True),
"execution_possible":(False,True),"clarification_possible":(False,True),"acknowledged":(False,True),"completed":(False,True)}
DEFAULTS={"permission":"missing","information":"insufficient","urgency":"none","need":"none","side_effect":"local","risk":"high","reversibility":"irreversible","deferral_available":False,"execution_possible":False,"clarification_possible":True,"acknowledged":False,"completed":False}

@dataclass(frozen=True)
class Evidence:
    factor:str; value:Any; span:str; confidence:float=1.0; polarity:str="positive"; temporal_rank:int=1; explicit:bool=True

@dataclass
class FactorResult:
    value:Any; epistemic_status:str; confidence:float; evidence:list[Evidence]=field(default_factory=list)

@dataclass
class ParseResult:
    state:dict[str,Any]; factors:dict[str,FactorResult]; evidence:list[Evidence]; action:str; architecture:str
    def trace(self)->dict[str,Any]: return {"architecture":self.architecture,"evidence":[asdict(e) for e in self.evidence],"factors":{k:asdict(v) for k,v in self.factors.items()},"state":self.state,"action":self.action}

def valid_state(s:dict[str,Any])->bool:
    if set(s)!=set(FIELD_ORDER): return False
    if s["side_effect"]=="external" and s["permission"]=="not_required": return False
    if s["side_effect"]=="none" and s["permission"]!="not_required": return False
    return all(s[k] in DOMAINS[k] for k in FIELD_ORDER)

def policy_action(s:dict[str,Any])->str:
    if not valid_state(s): return "INVALID"
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
    ext=s["side_effect"]=="external" and s["permission"]=="granted"
    loc=s["side_effect"]=="local" and s["permission"] in ("not_required","granted")
    if (ext or loc) and s["information"]=="sufficient" and s["risk"]=="low" and s["reversibility"]=="reversible" and s["execution_possible"] and s["need"]=="material": return "ACT"
    if s["need"]=="material" and s["urgency"]=="high": return "NOTIFY"
    if s["need"]=="material" and s["urgency"]=="normal": return "NOTIFY"
    if s["need"]=="material" and s["urgency"]=="none" and s["deferral_available"]: return "WAIT"
    if s["need"]=="material": return "SUGGEST"
    if s["need"]=="optional": return "SUGGEST"
    return "IGNORE"

# Development vocabulary is intentionally semantic/factor based rather than sentence-ID based.
# Holdout/stress generators choose phrases independently from these normalized concepts.
LEXICON={
"permission":{"granted":r"\b(approved|authorized|authorised|approval (?:is )?granted|permission granted|green light|go[ -]?ahead(?: is in)?|sign[ -]?off|clearance received)\b","missing":r"\b(approval pending|permission missing|not authorized|not authorised|awaiting approval|no clearance|authorization unresolved)\b","not_required":r"\b(no permission required|approval exempt|permissionless|outside approval scope)\b"},
"information":{"sufficient":r"\b(information (?:is )?(?:sufficient|complete)|facts (?:are )?(?:complete|settled)|(?<!not )enough information|evidence is adequate|record is complete)\b","insufficient":r"\b(information (?:is )?(?:insufficient|incomplete)|facts are missing|information gaps|not enough information|record is incomplete)\b","contradictory":r"\b(contradictory information|conflicting evidence|facts conflict|records disagree|inconsistent reports)\b"},
"urgency":{"none":r"\b(no urgency|not urgent|can wait(?! until later)|timing is flexible|routine timing)\b","normal":r"\b(normal urgency|ordinary priority|standard timing|moderate priority)\b","high":r"\b(high urgency|(?<!not )urgent|needs prompt attention|time sensitive|pressing)\b","expired":r"\b(expired|overdue|deadline passed|window has closed|past due)\b"},
"need":{"none":r"\b(no action needed|nothing is needed|no intervention required|need is none)\b","optional":r"\b(optional action|nice to have|discretionary|may help|elective)\b","material":r"\b(material action needed|action is required|substantive need|must be handled|material need)\b"},
"side_effect":{"none":r"\b(no side effect|read[ -]?only|informational only|no material side effect)\b","local":r"\b(local side effect|on[ -]?system change|internal change|local write)\b","external":r"\b(external side effect|third[ -]?party change|outside system action|external write)\b"},
"risk":{"low":r"\b(low risk|minimal risk|safe operation|small downside)\b","medium":r"\b(medium risk|moderate risk|meaningful downside)\b","high":r"\b(high risk|severe risk|dangerous|substantial downside)\b"},
"reversibility":{"reversible":r"\b(reversible|can be undone|rollback is possible|recoverable change|can be rolled back)\b","irreversible":r"\b(irreversible|cannot be undone|permanent change|no rollback|final change)\b"},
"deferral_available":{True:r"\b(can defer|deferral available|can wait until later|postponement is possible)\b",False:r"\b(cannot defer|no deferral|must decide now|postponement unavailable)\b"},
"execution_possible":{True:r"\b(execution possible|can execute|feasible to perform|tooling is available)\b",False:r"\b(execution impossible|cannot execute|blocked from execution|tooling unavailable)\b"},
"clarification_possible":{True:r"\b(can ask|clarification possible|question can resolve it|clarification available)\b",False:r"\b(cannot ask|clarification impossible|no clarification channel|question cannot be asked)\b"},
"acknowledged":{True:r"\b(already acknowledged|user has seen it|already noted|awareness confirmed)\b",False:r"\b(not acknowledged|user has not seen it|not yet noted|unseen by user)\b"},
"completed":{True:r"\b((?<!not )completed|already done|task is finished|case is closed|resolved already)\b",False:r"\b(not completed|still open|work remains|task is ongoing|unfinished)\b"},
}

NEGATION_RULES=[
(r"\bapproval was not granted\b",("permission","missing")),
(r"\bnot yet approved\b",("permission","missing")),
(r"\binformation is not sufficient\b",("information","insufficient")),
(r"\baction is not required\b",("need","none")),
(r"\bchange is not reversible\b",("reversibility","irreversible")),
(r"\bexecution is not possible\b",("execution_possible",False)),
]

def _latest_clause_rank(text:str, start:int)->int:
    prefix=text[:start].lower()
    rank=1+prefix.count("but now")*10+prefix.count("however now")*10+prefix.count("as of now")*10+prefix.count("later")*3
    return rank

def extract_evidence(text:str, *, vocabulary_fraction:float=1.0, operators:bool=True)->list[Evidence]:
    low=" ".join(text.lower().replace("’","'").split())
    out=[]
    for field, values in LEXICON.items():
        items=list(values.items())
        if vocabulary_fraction<1.0: items=items[:max(1,int(len(items)*vocabulary_fraction+0.5))]
        for value,pat in items:
            for m in re.finditer(pat,low,re.I):
                out.append(Evidence(field,value,text[m.start():m.end()],0.98,"positive",_latest_clause_rank(low,m.start()),True))
    if operators:
        for pat,(field,value) in NEGATION_RULES:
            for m in re.finditer(pat,low,re.I): out.append(Evidence(field,value,text[m.start():m.end()],0.99,"negative",_latest_clause_rank(low,m.start()),True))
    return out

def resolve_state(evidence:Iterable[Evidence], *, joint_constraints:bool=True, temporal:bool=True)->tuple[dict[str,Any],dict[str,FactorResult]]:
    ev=list(evidence); state=dict(DEFAULTS); factors={}
    for f in FIELD_ORDER:
        xs=[e for e in ev if e.factor==f]
        if not xs:
            factors[f]=FactorResult(state[f],"UNKNOWN",0.0,[]); continue
        if temporal:
            best_rank=max(e.temporal_rank for e in xs); current=[e for e in xs if e.temporal_rank==best_rank]
        else: current=xs
        by={}
        for e in current: by[e.value]=by.get(e.value,0.0)+e.confidence
        ranked=sorted(by.items(),key=lambda x:(x[1],str(x[0])),reverse=True)
        v,score=ranked[0]
        status="KNOWN" if len(ranked)==1 else ("CONTRADICTED" if ranked[0][1]-ranked[1][1]<0.15 else "KNOWN")
        state[f]=v; factors[f]=FactorResult(v,status,min(1.0,score/max(1,len(current))),current)
    if joint_constraints:
        # Hard ontology constraint: permission scope follows side-effect type.
        if factors["side_effect"].epistemic_status!="UNKNOWN" and state["side_effect"]=="none":
            state["permission"]="not_required"
            if factors["permission"].epistemic_status=="UNKNOWN": factors["permission"]=FactorResult("not_required","INFERRED",0.90,[])
        # Contradictory information is itself a valid information state.
        if factors["information"].epistemic_status=="CONTRADICTED": state["information"]="contradictory"
    return state,factors

class ArchitectureA:
    name="A_canonical_structured_parser"
    def parse(self,text:str)->ParseResult:
        # Canonical parser: intentionally narrow benchmark baseline.
        evidence=[]
        for f in FIELD_ORDER:
            for v in DOMAINS[f]:
                token=str(v).lower().replace("_"," ")
                pat=rf"\b{re.escape(f.replace('_',' '))}\s*(?:is|=)\s*{re.escape(token)}\b"
                m=re.search(pat,text.lower())
                if m: evidence.append(Evidence(f,v,m.group(0),0.95))
        s,fac=resolve_state(evidence,joint_constraints=False,temporal=False)
        return ParseResult(s,fac,evidence,policy_action(s),self.name)

class ArchitectureB:
    name="B_factor_specific_evidence"
    def parse(self,text:str)->ParseResult:
        e=extract_evidence(text,vocabulary_fraction=0.72,operators=False)
        s,f=resolve_state(e,joint_constraints=False,temporal=False)
        return ParseResult(s,f,e,policy_action(s),self.name)

class ArchitectureC:
    name="C_typed_proposition_constraint_resolver"
    def __init__(self,*,operators:bool=True,joint_constraints:bool=True,temporal:bool=True): self.operators=operators; self.joint_constraints=joint_constraints; self.temporal=temporal
    def parse(self,text:str)->ParseResult:
        e=extract_evidence(text,vocabulary_fraction=1.0,operators=self.operators)
        s,f=resolve_state(e,joint_constraints=self.joint_constraints,temporal=self.temporal)
        return ParseResult(s,f,e,policy_action(s),self.name)
