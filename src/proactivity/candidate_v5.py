from __future__ import annotations
import hashlib, re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
import numpy as np
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer
from proactivity.specification.oracle import evaluate

ACTIONS=("ACT","ASK","IGNORE","NOTIFY","SUGGEST","WAIT")
FIELDS=("permission","information","urgency","need","side_effect","risk","reversibility","deferral_available","execution_possible","clarification_possible","acknowledged","completed")
VALUES={
"permission":("not_required","missing","granted"),
"information":("sufficient","insufficient","contradictory"),
"urgency":("none","normal","high","expired"),
"need":("none","optional","material"),
"side_effect":("none","local","external"),
"risk":("low","medium","high"),
"reversibility":("reversible","irreversible"),
"deferral_available":(False,True),"execution_possible":(False,True),
"clarification_possible":(False,True),"acknowledged":(False,True),"completed":(False,True)}
CRITICAL=("permission","information","risk","reversibility","execution_possible","need","side_effect")
UNKNOWN="__UNKNOWN__"; MODEL_ID="sentence-transformers/all-MiniLM-L6-v2"
DESC={
("permission","not_required"):"no additional authorization is needed because existing authority covers the operation",
("permission","missing"):"required authorization is still absent",
("permission","granted"):"the responsible authority has approved the operation",
("information","sufficient"):"the facts needed for the decision are complete and consistent",
("information","insufficient"):"important decision facts are still missing",
("information","contradictory"):"relevant sources conflict on a material fact",
("urgency","none"):"there is no meaningful time pressure",
("urgency","normal"):"timing matters on an ordinary non-urgent cadence",
("urgency","high"):"prompt attention is required because delay has material cost",
("urgency","expired"):"the relevant deadline or action window has already passed",
("need","none"):"no intervention is needed",
("need","optional"):"an intervention may help but is discretionary",
("need","material"):"a substantive intervention is required",
("side_effect","none"):"the response changes no local or external state",
("side_effect","local"):"the operation changes only local system state",
("side_effect","external"):"the operation affects a party or system outside the local boundary",
("risk","low"):"the plausible downside is small and bounded",
("risk","medium"):"the plausible downside is meaningful but moderate",
("risk","high"):"the plausible downside could be severe",
("reversibility","reversible"):"a reliable rollback can restore the prior state",
("reversibility","irreversible"):"there is no reliable way to restore the prior state",
("deferral_available",False):"no concrete future trigger exists for reconsideration",
("deferral_available",True):"a concrete future trigger or checkpoint exists",
("execution_possible",False):"the operation cannot currently be executed",
("execution_possible",True):"the operation can currently be executed",
("clarification_possible",False):"the uncertainty cannot currently be resolved by asking",
("clarification_possible",True):"an available source can resolve the uncertainty",
("acknowledged",False):"the relevant party has not confirmed awareness",
("acknowledged",True):"the relevant party has confirmed awareness",
("completed",False):"the underlying objective remains unfinished",
("completed",True):"the underlying objective is already complete",
}
def lab(v): return "__TRUE__" if v is True else "__FALSE__" if v is False else str(v)
def dec(v): return True if v=="__TRUE__" else False if v=="__FALSE__" else v
def split_props(text):
    p=re.split(r"(?:\n+|(?<=[.!?。！？])\s+|;\s*|；\s*|\s+(?:Meanwhile|Separately|In addition|At the same time),?\s+)",str(text))
    p=[x.strip(" \t\r\n-—:") for x in p if x and len(x.strip(" \t\r\n-—:"))>2]
    return p or [str(text)]
class SemanticEncoder:
    def __init__(self,model_id=MODEL_ID):
        self.model_id=model_id; self.model=SentenceTransformer(model_id,device="cpu"); self.cache={}
    def encode(self,texts):
        vals=[str(x) for x in texts]; h=hashlib.sha256("\0".join(vals).encode()).hexdigest()
        if h not in self.cache:
            self.cache[h]=np.asarray(self.model.encode(vals,batch_size=64,show_progress_bar=False,convert_to_numpy=True,normalize_embeddings=True),dtype=np.float64)
        return self.cache[h]
@dataclass(frozen=True)
class ParseResultV5:
    state:dict[str,Any]; confidence:dict[str,float]; source_clause:dict[str,str]
def project(state):
    d={"permission":"missing","information":"insufficient","urgency":"none","need":"optional","side_effect":"none","risk":"high","reversibility":"irreversible","deferral_available":False,"execution_possible":False,"clarification_possible":True,"acknowledged":False,"completed":False}
    out=dict(state); unknown=[]
    for f in FIELDS:
        if out.get(f,UNKNOWN)==UNKNOWN: unknown.append(f); out[f]=d[f]
    if out["side_effect"]=="none": out["permission"]="not_required"
    if out["side_effect"]=="external" and out["permission"]=="not_required": out["permission"]="missing"
    return out,tuple(unknown)
class Base:
    def fit(self,records): return self
    def parse_records(self,records): return [self.parse_record(r) for r in records]
    @staticmethod
    def action(parsed):
        s,u=project(parsed.state); r=evaluate(s)
        if r.status!="VALID_DECISION" or r.action not in ACTIONS: return "WAIT"
        return "ASK" if r.action=="ACT" and any(f in u for f in CRITICAL) else str(r.action)
    def predict(self,records): return [self.action(p) for p in self.parse_records(records)]
class V5A(Base):
    def __init__(self,encoder,similarity_floor,ambiguity_margin):
        self.e=encoder; self.floor=similarity_floor; self.margin=ambiguity_margin; self.h={}
        for f in FIELDS:
            for v in VALUES[f]:
                z=self.e.encode([f"The {f} condition means {DESC[(f,v)]}."])[0]; self.h[(f,v)]=z
    def parse_record(self,r): return self.parse_records([r])[0]
    def parse_records(self,records):
        lists=[split_props(r["observation"]) for r in records]; flat=[x for xs in lists for x in xs]; emb=self.e.encode(flat); out=[]; off=0
        for xs in lists:
            x=emb[off:off+len(xs)]; off+=len(xs); s={}; c={}; src={}
            for f in FIELDS:
                sc=[]
                for v in VALUES[f]:
                    sims=x@self.h[(f,v)]; i=int(np.argmax(sims)); sc.append((float(sims[i]),v,i))
                sc.sort(reverse=True,key=lambda q:q[0]); a,b=sc[0],sc[1]; c[f]=(a[0]+1)/2; src[f]=xs[a[2]]
                s[f]=UNKNOWN if a[0]<self.floor or a[0]-b[0]<self.margin else a[1]
            out.append(ParseResultV5(s,c,src))
        return out
class V5B(Base):
    def __init__(self,encoder,c,abstention_floor): self.e=encoder; self.c=c; self.floor=abstention_floor; self.models={}
    def fit(self,records):
        x=self.e.encode([r["observation"] for r in records])
        for f in FIELDS:
            m=LogisticRegression(C=self.c,class_weight="balanced",max_iter=3000,random_state=20260815)
            m.fit(x,[lab(r["latent_state"][f]) for r in records]); self.models[f]=m
        return self
    def parse_record(self,r): return self.parse_records([r])[0]
    def parse_records(self,records):
        obs=[r["observation"] for r in records]; x=self.e.encode(obs); S=[{} for _ in records]; C=[{} for _ in records]; Q=[{} for _ in records]
        for f,m in self.models.items():
            P=m.predict_proba(x)
            for j,row in enumerate(P):
                i=int(np.argmax(row)); p=float(row[i]); C[j][f]=p; Q[j][f]=obs[j]; S[j][f]=dec(str(m.classes_[i])) if p>=self.floor else UNKNOWN
        return [ParseResultV5(S[i],C[i],Q[i]) for i in range(len(records))]
class V5C(Base):
    def __init__(self,encoder,similarity_floor,ambiguity_margin,hypothesis_weight=.25):
        self.e=encoder; self.floor=similarity_floor; self.margin=ambiguity_margin; self.w=hypothesis_weight; self.cent={}; self.h={}
        for f in FIELDS:
            for v in VALUES[f]: self.h[(f,v)]=self.e.encode([f"The {f} condition means {DESC[(f,v)]}."])[0]
    def fit(self,records):
        b={(f,v):[] for f in FIELDS for v in VALUES[f]}
        for r in records:
            for f in FIELDS: b[(f,r["latent_state"][f])].append(r["factor_clauses"][f])
        for k,t in b.items():
            z=self.e.encode(t).mean(axis=0); self.cent[k]=z/max(float(np.linalg.norm(z)),1e-12)
        return self
    def parse_record(self,r): return self.parse_records([r])[0]
    def parse_records(self,records):
        lists=[split_props(r["observation"]) for r in records]; flat=[x for xs in lists for x in xs]; emb=self.e.encode(flat); out=[]; off=0
        for xs in lists:
            x=emb[off:off+len(xs)]; off+=len(xs); s={}; c={}; src={}
            for f in FIELDS:
                sc=[]
                for v in VALUES[f]:
                    z=(1-self.w)*(x@self.cent[(f,v)])+self.w*(x@self.h[(f,v)]); i=int(np.argmax(z)); sc.append((float(z[i]),v,i))
                sc.sort(reverse=True,key=lambda q:q[0]); a,b=sc[0],sc[1]; c[f]=(a[0]+1)/2; src[f]=xs[a[2]]
                s[f]=UNKNOWN if a[0]<self.floor or a[0]-b[0]<self.margin else a[1]
            out.append(ParseResultV5(s,c,src))
        return out
def make_candidate(name,config,encoder):
    if name=="V5A": return V5A(encoder,float(config["similarity_floor"]),float(config["ambiguity_margin"]))
    if name=="V5B": return V5B(encoder,float(config["c"]),float(config["abstention_floor"]))
    if name=="V5C": return V5C(encoder,float(config["similarity_floor"]),float(config["ambiguity_margin"]),float(config.get("hypothesis_weight",.25)))
    raise ValueError(name)
