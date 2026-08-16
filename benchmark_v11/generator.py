from __future__ import annotations
import random, json
from proactivity.candidate_v11 import DOMAINS, FIELD_ORDER, policy_action

PHRASES = {
"permission":{
 "granted":["approval is granted","authorization is approved","consent is recorded","we have clearance","the goahead is signedoff"],
 "missing":["approval is missing","authorization is pending","consent is absent","clearance is awaiting","the request is unauthorized"],
 "not_required":["permission is unnecessary","approval is notrequired","this is exempt from approval","the task is outsideapprovalscope","the operation is permissionless"],
},
"information":{
 "sufficient":["information is sufficient","the facts are complete","evidence is adequate","details are enough","the record is clear"],
 "insufficient":["information is insufficient","the facts are incomplete","evidence is inadequate","details have gaps","the record is unclear"],
 "contradictory":["information is contradictory","the facts are conflicting","evidence is inconsistent","reports disagree","details are incompatible"],
},
"urgency":{
 "none":["urgency is none","the matter is nonurgent","timing is routine and canwait","nothing is pressing","priority is unpressing"],
 "normal":["urgency is normal","priority is ordinary","timing is standard","the schedule is moderate","deadline pressure is normal"],
 "high":["urgency is high","the matter is urgent","attention is immediate","deadline pressure is acute","the issue is pressing"],
 "expired":["the deadline is expired","the item is overdue","the timing window has lapsed","the deadline has passed","the window is over"],
},
"need":{
 "none":["need is none","intervention is unnecessary","nothing is needed","there is noaction need","a response is notneeded"],
 "optional":["need is optional","intervention is discretionary","action is elective","a response mayhelp","this is a nice optional step"],
 "material":["need is material","intervention is required","action is needed","a response is necessary","a substantive response must happen"],
},
"side_effect":{
 "none":["sideeffect is none","the operation is informational","this is readonly","effect is zero","no external or local effect exists"],
 "local":["sideeffect is local","the effect is internal","the change stays local","the operation changes the onsystem state","only local data changes"],
 "external":["sideeffect is external","the effect reaches outside","a thirdparty system changes","the operation is remote","an external service changes"],
},
"risk":{
 "low":["risk is low","harm is minimal","downside is small","harm is unlikely","the operation is safe"],
 "medium":["risk is medium","harm is moderate","downside is intermediate","exposure is meaningful","risk is moderate"],
 "high":["risk is high","harm is severe","downside is substantial","exposure is considerable","the operation is dangerous"],
},
"reversibility":{
 "reversible":["the action is reversible","the change is undoable","rollback is available","we can restore the prior state","the effect is recoverable"],
 "irreversible":["the action is irreversible","the change is permanent","this is nonreversible","we cannotundo the effect","the result is final"],
},
"deferral_available":{
 True:["deferral is available","we can defer","waiting until later is available","we can postpone","a future wait point exists"],
 False:["deferral is unavailable","there is nodeferral","we cannotdefer","nowait option exists","postponement is unavailable"],
},
"execution_possible":{
 True:["execution is possible","the action is executable","execution is feasible","we canexecute it","the task is performable"],
 False:["execution is impossible","the action is infeasible","we cannotexecute it","execution is blocked","no feasible execution path exists"],
},
"clarification_possible":{
 True:["clarification is possible","the issue is askable","the point is clarifiable","we canask","a question is resolvable"],
 False:["clarification is impossible","clarification is unavailable","we cannotask","the issue is unresolvable","no question can resolve it"],
},
"acknowledged":{
 True:["the issue is acknowledged","the item is noted","the user has seen it","they are aware","the alert was acknowledged"],
 False:["the issue is unacknowledged","the item is unseen","it is notnoted","they are unaware","the alert remains unacknowledged"],
},
"completed":{
 True:["the work is completed","the task is done","the case is finished","the issue is resolved","the item is closed"],
 False:["the work is incomplete","the task is pending","the case is open","the issue is unfinished","the item is ongoing"],
},
}

FAMILIES=("Lexical","Rendering","Compositional","Negation","Scope","Temporal","Mixed Adversarial")

def valid_state(rng:random.Random):
    while True:
        s={f:rng.choice(DOMAINS[f]) for f in FIELD_ORDER}
        if s["side_effect"]=="external" and s["permission"]=="not_required": continue
        if s["side_effect"]=="none" and s["permission"]!="not_required": continue
        return s

def render_value(field,value,idx):
    return PHRASES[field][value][idx % len(PHRASES[field][value])]

def render_state(state, family, seed, bank_offset=0):
    rng=random.Random(seed)
    order=list(FIELD_ORDER)
    if family in ("Compositional","Scope","Mixed Adversarial"):
        rng.shuffle(order)
    clauses=[]
    for j,f in enumerate(order):
        idx=(seed+j+bank_offset) % 5
        c=render_value(f,state[f],idx)
        if family=="Rendering":
            c=("FYI: "+c.upper()) if j%2==0 else ("(" + c + ")")
        elif family=="Temporal" and f in ("urgency","completed","acknowledged"):
            c=("currently, "+c) if j%2 else ("as of now, "+c)
        clauses.append(c)
    if family=="Negation":
        repl={
          ("risk","low"):"risk is not high", ("risk","high"):"risk is not low",
          ("reversibility","reversible"):"the action is not irreversible",
          ("reversibility","irreversible"):"the action is not reversible",
          ("execution_possible",True):"execution is not impossible",
          ("execution_possible",False):"execution is not possible",
          ("clarification_possible",True):"clarification is not impossible",
          ("clarification_possible",False):"clarification is not possible",
          ("completed",True):"the work is not incomplete", ("completed",False):"the work is not completed",
        }
        clauses=[repl.get((f,state[f]),c) for f,c in zip(order,clauses)]
    if family=="Scope":
        d=[]
        for f,c in zip(order,clauses):
            if f=="risk":
                distract="risk is high" if state[f]!="high" else "risk is low"
                d.append("previously "+distract); d.append("however "+c)
            else: d.append(c)
        clauses=d
    if family=="Mixed Adversarial":
        wrappers=["for context","despite earlier discussion","operationally","at this point"]
        clauses=[f"{wrappers[i%len(wrappers)]}, {c}" for i,c in enumerate(clauses)]
    sep="; " if family!="Rendering" else ".\n"
    return sep.join(clauses)+"."

def make_dataset(n, seed, bank_offset=0):
    rng=random.Random(seed); rows=[]
    for i in range(n):
        s=valid_state(rng); fam=FAMILIES[i%len(FAMILIES)]
        text=render_state(s,fam,seed*10000+i,bank_offset)
        rows.append({"id":f"{seed}-{i:05d}","family":fam,"text":text,"state":s,"action":policy_action(s)})
    return rows

def write_jsonl(path,rows):
    with open(path,"w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,sort_keys=True)+"\n")

def render_state_subset(state, family, seed, omit=(), bank_offset=0):
    rng=random.Random(seed); order=[f for f in FIELD_ORDER if f not in set(omit)]
    if family in ("Compositional","Scope","Mixed Adversarial"): rng.shuffle(order)
    clauses=[render_value(f,state[f],(seed+j+bank_offset)%5) for j,f in enumerate(order)]
    return "; ".join(clauses)+"."

def counterfactual_pairs(n=240,seed=3119,bank_offset=1):
    pairs=[]
    base={"permission":"granted","information":"sufficient","urgency":"normal","need":"material","side_effect":"external","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False}
    changes=[("permission","missing"),("information","insufficient"),("risk","high"),("reversibility","irreversible"),("execution_possible",False),("completed",True)]
    fams=list(FAMILIES); i=0
    while len(pairs)<n:
        s1=dict(base)
        if i%2: s1["side_effect"]="local"; s1["permission"]="not_required"
        f,v=changes[i%len(changes)]; s2=dict(s1); s2[f]=v
        if s2["side_effect"]=="external" and s2["permission"]=="not_required": s2["permission"]="missing"
        fam=fams[i%len(fams)]
        t1=render_state(s1,fam,seed*1000+i,bank_offset); t2=render_state(s2,fam,seed*1000+i+100000,bank_offset)
        if policy_action(s1)!=policy_action(s2):
            pairs.append({"id":f"cf-{i:04d}","factor":f,"a":{"text":t1,"state":s1,"action":policy_action(s1)},"b":{"text":t2,"state":s2,"action":policy_action(s2)}})
        i+=1
    return pairs

def unknown_cases(n=240,seed=4111,bank_offset=3):
    rng=random.Random(seed); out=[]; critical=["permission","information","risk","reversibility","execution_possible","side_effect","need"]
    for i in range(n):
        s=valid_state(rng); f=critical[i%len(critical)]
        text=render_state_subset(s,"Compositional",seed*1000+i,omit=(f,),bank_offset=bank_offset)
        out.append({"id":f"u-{i:04d}","omitted_field":f,"text":text,"state":s})
    return out

def invariance_texts(state, seed):
    rng=random.Random(seed); clauses=[PHRASES[f][state[f]][0] for f in FIELD_ORDER]
    a="; ".join(clauses)+"."; b=". ".join(reversed(clauses))+"."
    shuffled=list(clauses); rng.shuffle(shuffled); c="For context, " + "; ".join(shuffled)+"."
    d=(" | ".join(clauses)).replace(" | ","; ").upper()+"."; e="Operationally: " + "; ".join(clauses)+"."
    return [a,b,c,d,e]

def make_action_balanced_dataset(per_action, seed, bank_offset=0):
    rng=random.Random(seed); targets=("IGNORE","WAIT","SUGGEST","NOTIFY","ASK","ACT"); buckets={a:[] for a in targets}; attempts=0
    while any(len(v)<per_action for v in buckets.values()):
        attempts+=1
        if attempts>2_000_000: raise RuntimeError("unable to balance actions")
        s=valid_state(rng); a=policy_action(s)
        if len(buckets[a])>=per_action: continue
        idx=sum(len(v) for v in buckets.values()); fam=FAMILIES[(idx + seed) % len(FAMILIES)]
        text=render_state(s,fam,seed*100000+attempts,bank_offset)
        buckets[a].append({"id":f"bal-{seed}-{a}-{len(buckets[a]):04d}","family":fam,"text":text,"state":s,"action":a})
    rows=[]
    for a in targets: rows.extend(buckets[a])
    rng.shuffle(rows); return rows
