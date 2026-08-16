from __future__ import annotations
import random, statistics
from collections import Counter
from .candidate_v12 import *

P={
"permission":{"granted":["approval is granted","we got the green light"],"missing":["approval pending","authorization unresolved"],"not_required":["no permission required","outside approval scope"]},
"information":{"sufficient":["information is sufficient","record is complete"],"insufficient":["information is incomplete","facts are missing"],"contradictory":["contradictory information","records disagree"]},
"urgency":{"none":["no urgency","timing is flexible"],"normal":["normal urgency","ordinary priority"],"high":["high urgency","time sensitive"],"expired":["expired","deadline passed"]},
"need":{"none":["no action needed","no intervention required"],"optional":["optional action","discretionary"],"material":["material action needed","substantive need"]},
"side_effect":{"none":["no side effect","read-only"],"local":["local side effect","internal change"],"external":["external side effect","third-party change"]},
"risk":{"low":["low risk","minimal risk"],"medium":["medium risk","moderate risk"],"high":["high risk","severe risk"]},
"reversibility":{"reversible":["reversible","can be undone"],"irreversible":["irreversible","cannot be undone"]},
"deferral_available":{True:["can defer","deferral available"],False:["cannot defer","no deferral"]},
"execution_possible":{True:["execution possible","can execute"],False:["execution impossible","cannot execute"]},
"clarification_possible":{True:["can ask","clarification possible"],False:["cannot ask","clarification impossible"]},
"acknowledged":{True:["already acknowledged","user has seen it"],False:["not acknowledged","unseen by user"]},
"completed":{True:["completed","task is finished"],False:["not completed","work remains"]},
}
SP={
"permission":{"granted":"clearance received","missing":"not yet approved","not_required":"approval exempt"},
"information":{"sufficient":"evidence is adequate","insufficient":"information gaps remain","contradictory":"facts conflict"},
"urgency":{"none":"not urgent","normal":"standard timing","high":"pressing","expired":"past due"},
"need":{"none":"action is not required","optional":"may help","material":"material need"},
"side_effect":{"none":"informational only","local":"local write","external":"external write"},
"risk":{"low":"small downside","medium":"meaningful downside","high":"substantial downside"},
"reversibility":{"reversible":"can be rolled back","irreversible":"final change"},
"deferral_available":{True:"postponement is possible",False:"postponement unavailable"},
"execution_possible":{True:"tooling is available",False:"execution is not possible"},
"clarification_possible":{True:"clarification available",False:"question cannot be asked"},
"acknowledged":{True:"awareness confirmed",False:"not yet noted"},
"completed":{True:"resolved already",False:"unfinished"},
}
FAMILIES=("Lexical","Rendering","Compositional","Negation","Scope","Temporal","Mixed Adversarial")

def sample_state(r):
    s={k:r.choice(DOMAINS[k]) for k in FIELD_ORDER}
    s["permission"]="not_required" if s["side_effect"]=="none" else (r.choice(("missing","granted")) if s["permission"]=="not_required" else s["permission"])
    return s

def state_for_action(r,t):
    if t=="ACT":
        s={"permission":"granted","information":"sufficient","urgency":r.choice(("none","normal","high")),"need":"material","side_effect":r.choice(("local","external")),"risk":"low","reversibility":"reversible","deferral_available":r.choice((False,True)),"execution_possible":True,"clarification_possible":r.choice((False,True)),"acknowledged":False,"completed":False}
    elif t=="ASK":
        s={"permission":"missing","information":r.choice(("insufficient","contradictory")),"urgency":r.choice(("none","normal","high")),"need":"material","side_effect":r.choice(("local","external")),"risk":r.choice(("low","medium","high")),"reversibility":r.choice(("reversible","irreversible")),"deferral_available":r.choice((False,True)),"execution_possible":r.choice((False,True)),"clarification_possible":True,"acknowledged":False,"completed":False}
    elif t=="NOTIFY":
        side=r.choice(("none","local","external")); s={"permission":"not_required" if side=="none" else r.choice(("missing","granted")),"information":"insufficient","urgency":r.choice(("high","expired")),"need":"material","side_effect":side,"risk":r.choice(("low","medium","high")),"reversibility":r.choice(("reversible","irreversible")),"deferral_available":r.choice((False,True)),"execution_possible":r.choice((False,True)),"clarification_possible":False,"acknowledged":False,"completed":False}
    elif t=="WAIT":
        side=r.choice(("none","local","external")); s={"permission":"not_required" if side=="none" else r.choice(("missing","granted")),"information":"insufficient","urgency":r.choice(("none","normal")),"need":r.choice(("optional","material")),"side_effect":side,"risk":r.choice(("low","medium","high")),"reversibility":r.choice(("reversible","irreversible")),"deferral_available":True,"execution_possible":r.choice((False,True)),"clarification_possible":False,"acknowledged":r.choice((False,True)),"completed":False}
    elif t=="SUGGEST":
        s={"permission":"not_required","information":"sufficient","urgency":"none","need":"optional","side_effect":"none","risk":r.choice(("low","medium")),"reversibility":r.choice(("reversible","irreversible")),"deferral_available":False,"execution_possible":r.choice((False,True)),"clarification_possible":r.choice((False,True)),"acknowledged":False,"completed":False}
    else:
        side=r.choice(("none","local","external")); s={"permission":"not_required" if side=="none" else r.choice(("missing","granted")),"information":r.choice(("sufficient","insufficient")),"urgency":r.choice(("none","normal")),"need":"none","side_effect":side,"risk":r.choice(("low","medium","high")),"reversibility":r.choice(("reversible","irreversible")),"deferral_available":False,"execution_possible":r.choice((False,True)),"clarification_possible":r.choice((False,True)),"acknowledged":r.choice((False,True)),"completed":r.choice((False,True))}
    assert valid_state(s) and policy_action(s)==t
    return s

def realize(s,r,family="Lexical",stress=False):
    q=[SP[f][s[f]] if stress else r.choice(P[f][s[f]]) for f in FIELD_ORDER]; r.shuffle(q)
    if family in ("Compositional","Scope","Mixed Adversarial"): q.insert(r.randrange(len(q)+1),r.choice(("The project name is Orion","Maria is travelling today","A dashboard was refreshed")))
    sep="; " if family=="Rendering" else (", meanwhile, " if family=="Mixed Adversarial" else ". ")
    return ("Context: " if family=="Mixed Adversarial" else "")+sep.join(q)+"."

def make_records(seed,n,stress=False):
    r=random.Random(seed); targets=list(ACTIONS); r.shuffle(targets); out=[]
    for i in range(n):
        if i and i%6==0:r.shuffle(targets)
        t=targets[i%6]; s=state_for_action(r,t); fam=r.choice(FAMILIES); text=realize(s,r,fam,stress)
        out.append({"id":f"v12-{seed}-{i}","family":fam,"state":s,"action":t,"text":text,"semantic_seed":seed,"realization_seed":seed*100000+i})
    return out

def macro_f1(y,p):
    z=[]
    for c in ACTIONS:
        tp=sum(a==c==b for a,b in zip(y,p)); fp=sum(a!=c and b==c for a,b in zip(y,p)); fn=sum(a==c and b!=c for a,b in zip(y,p)); pr=tp/(tp+fp) if tp+fp else 0; rc=tp/(tp+fn) if tp+fn else 0; z.append(2*pr*rc/(pr+rc) if pr+rc else 0)
    return sum(z)/6

def evaluate(a,rec):
    ps=[a.parse(x["text"]) for x in rec]; y=[x["action"] for x in rec]; p=[x.action for x in ps]; n=len(rec)
    fa={f:sum(z.state[f]==x["state"][f] for z,x in zip(ps,rec))/n for f in FIELD_ORDER}; tp=sum(x==z=="ACT" for x,z in zip(y,p)); fp=sum(x!="ACT" and z=="ACT" for x,z in zip(y,p)); fn=sum(x=="ACT" and z!="ACT" for x,z in zip(y,p))
    return {"macro_f1":macro_f1(y,p),"exact_latent_state_reconstruction":sum(z.state==x["state"] for z,x in zip(ps,rec))/n,"mean_factor_accuracy":sum(fa.values())/12,"factor_accuracy":fa,"act_critical_factor_accuracy":sum(fa[f] for f in ACT_CRITICAL)/len(ACT_CRITICAL),"false_unknown_rate":sum(z.factors[f].epistemic_status=="UNKNOWN" for z in ps for f in FIELD_ORDER)/(12*n),"act_precision":tp/(tp+fp) if tp+fp else 0,"act_recall":tp/(tp+fn) if tp+fn else 0,"forbidden_act":fp,"invalid_action":sum(z.action not in ACTIONS for z in ps),"action_distribution":dict(Counter(p))}

def unknown_metrics(a,seed=991,n=240):
    r=random.Random(seed); ok=false=0
    for _ in range(n):
        s=sample_state(r); omit=r.choice(FIELD_ORDER); q=[r.choice(P[f][s[f]]) for f in FIELD_ORDER if f!=omit]; r.shuffle(q); z=a.parse(". ".join(q)+"."); ok+=z.factors[omit].epistemic_status=="UNKNOWN"
    for x in make_records(seed+1,n): false+=sum(a.parse(x["text"]).factors[f].epistemic_status=="UNKNOWN" for f in ACT_CRITICAL)
    return {"legitimate_unknown_recall":ok/n,"critical_unknown_rate":false/(n*len(ACT_CRITICAL)),"false_unknown_rate":false/(n*len(ACT_CRITICAL))}

def counterfactual_metrics(a,seed=992,n=220):
    r=random.Random(seed); exact=delta=trans=0
    for _ in range(n):
        s=state_for_action(r,"ACT"); s["side_effect"]="external"; s["permission"]="granted"; x=dict(s); y=dict(s); y["permission"]="missing"; px=a.parse(realize(x,r)); py=a.parse(realize(y,r)); exact+=px.state==x and py.state==y; delta+=px.state["permission"]=="granted" and py.state["permission"]=="missing" and sum(px.state[f]!=py.state[f] for f in FIELD_ORDER)==1; trans+=px.action==policy_action(x) and py.action==policy_action(y)
    return {"exact_pair_correctness":exact/n,"latent_factor_delta_correctness":delta/n,"action_transition_correctness":trans/n}

def invariance_metrics(a,seed=993,n=220):
    r=random.Random(seed); st=ac=cc=0
    for _ in range(n):
        s=sample_state(r); x=a.parse(realize(s,random.Random(r.randrange(10**9)),"Lexical")); y=a.parse(realize(s,random.Random(r.randrange(10**9)),"Rendering")); st+=x.state==y.state; ac+=x.action==y.action; cc+=x.state==s and y.state==s and x.action==policy_action(s)==y.action
    return {"latent_state_invariance_consistency":st/n,"action_invariance_consistency":ac/n,"correct_consistency":cc/n}

def development_summary():
    arches=[ArchitectureA(),ArchitectureB(),ArchitectureC()]; selection=[{"architecture":a.name,**evaluate(a,make_records(12001,600))} for a in arches]; w=ArchitectureC(); runs=[evaluate(w,make_records(s,320)) for s in (13001,13002,13003,13004,13005)]; pooled=evaluate(w,sum((make_records(s,320) for s in (13001,13002,13003,13004,13005)),[])); stress=evaluate(w,make_records(14001,600,True)); f=[x["macro_f1"] for x in runs]
    return {"selection":selection,"pooled":pooled,"unknown":unknown_metrics(w),"counterfactual":counterfactual_metrics(w),"invariance":invariance_metrics(w),"stress":stress,"robustness":{"mean":statistics.mean(f),"median":statistics.median(f),"minimum":min(f),"maximum":max(f),"standard_deviation":statistics.pstdev(f)}}
