from __future__ import annotations

import hashlib, json, random
from pathlib import Path
from typing import Any, Dict, List

from candidate_v10.policy import ACTIONS, FACTOR_VALUES, is_valid_state, project_valid_state, select_action

SEEDS={"train":101001,"validation":101002,"lexical_novelty":101003,"syntactic_novelty":101004,"domain_transfer":101005,"state_validity_stress":101006,"act_boundary":101007,"negation":101008,"contradiction":101009,"supersession":101010,"ellipsis":101011,"pragmatic":101012,"cross_factor_distractor":101013,"uncertainty":101014,"compositional":101015,"counterfactual":101016,"permission_scope":101017}
SIZES={"train":12000,"validation":3000,"lexical_novelty":2000,"syntactic_novelty":2000,"domain_transfer":1500,"state_validity_stress":2500,"act_boundary":2000,"negation":1000,"contradiction":1000,"supersession":1000,"ellipsis":1000,"pragmatic":1000,"cross_factor_distractor":1500,"uncertainty":1000,"compositional":1500,"counterfactual":1500,"permission_scope":1000}

TRAIN_PHRASES: Dict[str, Dict[Any,List[str]]] = {
"permission":{"not_required":["authorization is not required","no approval is needed","permission is unnecessary"],"missing":["authorization is still missing","approval has not been granted","permission remains pending"],"granted":["authorization is granted","approval is in place","permission has been given"]},
"information":{"sufficient":["information is complete","the details are sufficient","all requirements are known"],"insufficient":["information is incomplete","key details are missing","some requirements are unknown"],"contradictory":["information is contradictory","the details conflict","requirements disagree with each other"]},
"urgency":{"none":["there is no urgency","no deadline pressure exists","timing is open"],"normal":["urgency is normal","the deadline is routine","timing is ordinary"],"high":["urgency is high","the deadline is close","timing is pressing"],"expired":["the deadline has expired","the timing window has passed","the due point is already past"]},
"need":{"none":["there is no need","the action is unnecessary","importance is absent"],"optional":["the need is optional","this would merely be helpful","importance is limited"],"material":["the need is material","this action is necessary","importance is substantial"]},
"side_effect":{"none":["there is no side effect","nothing will be changed","the impact is informational only"],"local":["the effect is local","the change stays on this device","impact is limited to the local workspace"],"external":["the effect is external","the change reaches a third party","impact leaves the local workspace"]},
"risk":{"low":["risk is low","exposure is minimal","the hazard is minor"],"medium":["risk is medium","exposure is meaningful","the hazard is moderate"],"high":["risk is high","exposure is severe","the hazard is substantial"]},
"reversibility":{"reversible":["the change is reversible","it can be undone","the prior state can be restored"],"irreversible":["the change is irreversible","it cannot be undone","the prior state cannot be restored"]},
"deferral_available":{False:["deferral is unavailable","it cannot be postponed","waiting until later is not an option"],True:["deferral is available","it can be postponed","waiting until later is possible"]},
"execution_possible":{False:["execution is impossible","the action cannot be performed","it cannot be carried out now"],True:["execution is possible","the action can be performed","it can be carried out now"]},
"clarification_possible":{False:["clarification is impossible","nobody can be asked to resolve this","the ambiguity cannot be resolved now"],True:["clarification is possible","someone can be asked to resolve this","the ambiguity can be resolved"]},
"acknowledged":{False:["the item is not acknowledged","it has not been seen","the notice has not been noted"],True:["the item is acknowledged","it has been seen","the notice has been noted"]},
"completed":{False:["the task is not completed","the work is unfinished","the job is not done"],True:["the task is completed","the work is finished","the job is done"]}}

LEXICAL_PHRASES: Dict[str, Dict[Any,List[str]]] = {
"permission":{"not_required":["this can proceed without consent"],"missing":["clearance is still absent"],"granted":["the go-ahead has arrived"]},
"information":{"sufficient":["we have enough facts"],"insufficient":["key facts remain unknown"],"contradictory":["the accounts point in opposing directions"]},
"urgency":{"none":["there is no time-pressure"],"normal":["the time window is routine"],"high":["the window is closing quickly"],"expired":["the opportunity is overdue"]},
"need":{"none":["no practical requirement remains"],"optional":["intervention is a nice-to-have"],"material":["outcome materially depends on action"]},
"side_effect":{"none":["there is no operational footprint"],"local":["the footprint stays inside the machine"],"external":["the footprint reaches beyond the machine"]},
"risk":{"low":["the downside is slight"],"medium":["the stakes are meaningful"],"high":["danger is substantial"]},
"reversibility":{"reversible":["a rollback remains available"],"irreversible":["the step is one-way"]},
"deferral_available":{False:["pausing is unavailable"],True:["this may be put on hold"]},
"execution_possible":{False:["the operation is blocked"],True:["the operation is feasible"]},
"clarification_possible":{False:["verification cannot be obtained"],True:["confirmation can be sought"]},
"acknowledged":{False:["receipt has not been registered"],True:["receipt is registered"]},
"completed":{False:["the matter remains open"],True:["the matter is settled"]}}

DOMAINS=["message sending","scheduling","system configuration","deletion"]

def base_state():
    return {"permission":"not_required","information":"sufficient","urgency":"none","need":"optional","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False}

def _prototype(action:str,rng:random.Random):
    s=base_state()
    if action=="IGNORE":
        if rng.random()<.5: s["completed"]=True; s["need"]=rng.choice(["none","optional","material"])
        else: s["need"]="none"; s["deferral_available"]=False
    elif action=="WAIT":
        m=rng.randrange(3)
        if m==0: s["need"]="none"; s["deferral_available"]=True
        elif m==1: s["need"]=rng.choice(["optional","material"]); s["information"]="insufficient"; s["clarification_possible"]=False; s["urgency"]=rng.choice(["none","normal"])
        else: s["need"]=rng.choice(["optional","material"]); s["acknowledged"]=True; s["deferral_available"]=True; s["urgency"]=rng.choice(["none","normal"])
    elif action=="SUGGEST":
        if rng.random()<.65: s["need"]="optional"
        else: s["need"]="material"; s["urgency"]="none"; s["deferral_available"]=False; s["side_effect"]="none"; s["permission"]="not_required"
    elif action=="NOTIFY": s["need"]="material"; s["side_effect"]="none"; s["permission"]="not_required"; s["urgency"]=rng.choice(["normal","high","expired"])
    elif action=="ASK":
        m=rng.randrange(4); s["need"]="material"
        if m==0: s["information"]=rng.choice(["insufficient","contradictory"]); s["clarification_possible"]=True
        elif m==1: s["side_effect"]="external"; s["permission"]="missing"
        elif m==2: s["side_effect"]="local"; s["permission"]="not_required"; s["risk"]=rng.choice(["medium","high"])
        else: s["side_effect"]="local"; s["permission"]="not_required"; s["reversibility"]="irreversible"
    elif action=="ACT":
        s.update({"need":"material","information":"sufficient","risk":"low","reversibility":"reversible","execution_possible":True,"completed":False,"acknowledged":False,"deferral_available":False,"urgency":rng.choice(["none","normal","high"])})
        if rng.random()<.5: s["side_effect"]="local"; s["permission"]=rng.choice(["not_required","granted"])
        else: s["side_effect"]="external"; s["permission"]="granted"
    for f in ("risk","reversibility","execution_possible","clarification_possible"):
        if action in ("IGNORE","WAIT","SUGGEST","NOTIFY") and rng.random()<.25: s[f]=rng.choice(list(FACTOR_VALUES[f]))
    return project_valid_state(s)

def make_state(action:str,rng:random.Random):
    for _ in range(500):
        s=_prototype(action,rng)
        if is_valid_state(s) and select_action(s)==action: return s
    raise RuntimeError(action)

def _wrap(c:str,style:str,i:int):
    if style=="canonical": return c.capitalize()+"."
    if style=="validation": return ["As currently established, {}.","Operationally, {}.","For this case, {}.","The record indicates that {}.","At present, {}."][i%5].format(c)
    if style=="syntactic": return ["Although other conditions may vary, {}.","What the record shows is that {}.","After the surrounding context is considered, {}.","{}; this remains the operative fact.","The condition that matters here is this: {}."][i%5].format(c)
    return c.capitalize()+"."

def render_state(state:Dict[str,Any],rng:random.Random,bank="train",style="canonical",domain=None):
    phrases=TRAIN_PHRASES if bank=="train" else LEXICAL_PHRASES; fs=list(FACTOR_VALUES); rng.shuffle(fs); parts=[]
    if domain: parts.append(f"Scenario domain: {domain}.")
    for i,f in enumerate(fs): parts.append(_wrap(rng.choice(phrases[f][state[f]]),style,i))
    return " ".join(parts)

def generate_balanced(name,n,seed,bank="train",style="canonical",domain=False):
    rng=random.Random(seed); out=[]
    for i in range(n):
        a=ACTIONS[i%6]; s=make_state(a,rng); d=rng.choice(DOMAINS) if domain else None
        out.append({"id":f"v10-{name}-{i:06d}","split":name,"text":render_state(s,rng,bank,style,d),"state":s,"action":a})
    rng.shuffle(out); return out

def generate_negation(n,seed):
    out=generate_balanced("negation",n,seed,style="validation"); fs=["permission","information","reversibility","execution_possible","completed"]
    for i,r in enumerate(out): r["focus_factor"]=fs[i%len(fs)]
    return out

def generate_supersession(n,seed):
    rng=random.Random(seed); out=generate_balanced("supersession",n,seed); fs=["risk","information","permission","reversibility","completed"]
    for i,r in enumerate(out):
        f=fs[i%len(fs)]; vals=[v for v in FACTOR_VALUES[f] if v!=r["state"][f]]; old=rng.choice(vals)
        r["text"]=f"Earlier, {rng.choice(TRAIN_PHRASES[f][old])}. After review, {rng.choice(TRAIN_PHRASES[f][r['state'][f]])}. "+r["text"]; r["focus_factor"]=f
    return out

def generate_contradiction(n,seed):
    out=generate_balanced("contradiction",n,seed)
    for r in out:
        r["state"]["information"]="contradictory"; r["text"]="The information first appears complete. However, the details conflict. "+r["text"]; r["action"]=select_action(project_valid_state(r["state"])); r["focus_factor"]="information"; r["contradiction_present"]=True
    return out

def generate_cross_factor(n,seed):
    out=generate_balanced("cross_factor_distractor",n,seed,style="validation"); ds=["The word permission appears in a risk memo but does not describe authorization.","A deadline label is present in a filename but says nothing about urgency.","The word reversible occurs in metadata, not as a statement about this action.","A local folder is mentioned, but that mention does not describe side effects."]
    for i,r in enumerate(out): r["text"]=ds[i%4]+" "+r["text"]
    return out

def generate_uncertainty(n,seed):
    out=generate_balanced("uncertainty",n,seed,style="validation"); fs=["permission","risk","execution_possible","information"]
    for i,r in enumerate(out): f=fs[i%4]; r["text"]=f"It is unclear whether the {f.replace('_',' ')} statement is reliable. "+r["text"]; r["uncertain_factor"]=f
    return out

def generate_counterfactual(n,seed):
    rng=random.Random(seed); changes=[("permission","missing"),("information","insufficient"),("risk","medium"),("reversibility","irreversible"),("execution_possible",False),("completed",True)]; out=[]
    for i in range(n):
        base=make_state("ACT",rng); f,v=changes[i%len(changes)]; changed=dict(base)
        if f=="permission" and changed["side_effect"]!="external": changed["side_effect"]="external"; changed["permission"]="granted"
        changed[f]=v; changed=project_valid_state(changed)
        out.append({"id":f"v10-counterfactual-{i:06d}","split":"counterfactual","base":{"text":render_state(base,rng),"state":base,"action":select_action(base)},"changed":{"text":render_state(changed,rng),"state":changed,"action":select_action(changed)},"changed_factor":f})
    return out

def generate_all():
    d={}; d["train"]=generate_balanced("train",SIZES["train"],SEEDS["train"]); d["validation"]=generate_balanced("validation",SIZES["validation"],SEEDS["validation"],style="validation"); d["lexical_novelty"]=generate_balanced("lexical_novelty",SIZES["lexical_novelty"],SEEDS["lexical_novelty"],bank="lexical",style="validation"); d["syntactic_novelty"]=generate_balanced("syntactic_novelty",SIZES["syntactic_novelty"],SEEDS["syntactic_novelty"],style="syntactic"); d["domain_transfer"]=generate_balanced("domain_transfer",SIZES["domain_transfer"],SEEDS["domain_transfer"],style="validation",domain=True); d["state_validity_stress"]=generate_balanced("state_validity_stress",SIZES["state_validity_stress"],SEEDS["state_validity_stress"],style="syntactic"); d["act_boundary"]=generate_balanced("act_boundary",SIZES["act_boundary"],SEEDS["act_boundary"],style="validation"); d["negation"]=generate_negation(SIZES["negation"],SEEDS["negation"]); d["contradiction"]=generate_contradiction(SIZES["contradiction"],SEEDS["contradiction"]); d["supersession"]=generate_supersession(SIZES["supersession"],SEEDS["supersession"]); d["ellipsis"]=generate_balanced("ellipsis",SIZES["ellipsis"],SEEDS["ellipsis"],bank="lexical"); d["pragmatic"]=generate_balanced("pragmatic",SIZES["pragmatic"],SEEDS["pragmatic"],bank="lexical",style="validation"); d["cross_factor_distractor"]=generate_cross_factor(SIZES["cross_factor_distractor"],SEEDS["cross_factor_distractor"]); d["uncertainty"]=generate_uncertainty(SIZES["uncertainty"],SEEDS["uncertainty"]); d["compositional"]=generate_balanced("compositional",SIZES["compositional"],SEEDS["compositional"],bank="lexical",style="syntactic",domain=True); d["permission_scope"]=generate_balanced("permission_scope",SIZES["permission_scope"],SEEDS["permission_scope"],style="validation"); d["counterfactual"]=generate_counterfactual(SIZES["counterfactual"],SEEDS["counterfactual"]); return d

def write_all(root,data):
    root=Path(root); root.mkdir(parents=True,exist_ok=True); manifest={}; names=["train","validation","lexical_novelty","syntactic_novelty","domain_transfer","negation","contradiction","supersession","ellipsis","pragmatic","cross_factor_distractor","uncertainty","permission_scope","act_boundary","state_validity_stress","compositional","counterfactual"]
    for k in names:
        p=root/f"{k}.jsonl"; h=hashlib.sha256()
        with p.open("w",encoding="utf-8") as f:
            for r in data[k]: line=json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"; f.write(line); h.update(line.encode())
        manifest[k]={"file":p.name,"n":len(data[k]),"seed":SEEDS[k],"sha256":h.hexdigest()}
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding="utf-8"); return manifest

if __name__=="__main__": write_all("data/candidate_v10_development",generate_all())
