from __future__ import annotations
from dataclasses import dataclass, replace
from pathlib import Path
import hashlib, json, random
from candidate_v11.model import FACTOR_DEFINITIONS, REVERSE_VALUE_MARKERS, decide_action

ROOT=Path(__file__).resolve().parents[1]
INV=json.loads((ROOT/"benchmark_v11"/"split_inventory.json").read_text())
ROOTS={"train":INV["TRAIN_ROOTS"],"dev":INV["DEV_VALIDATION_ROOTS"],"stress":INV["STRESS_ROOTS"],"holdout":INV["FORMAL_HOLDOUT_ROOTS"]}
SEEDS=INV["seeds"]
SIZES={k:v for k,v in INV["sizes"].items()}; SIZES["counterfactual"]=SIZES.pop("counterfactual_pairs")
DOMAINS=tuple(INV["domains"]); ACTIONS=("IGNORE","WAIT","SUGGEST","NOTIFY","ASK","ACT")
BASE_STATES={
"IGNORE":{"permission":"not_required","information":"sufficient","urgency":"none","need":"none","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False},
"WAIT":{"permission":"not_required","information":"sufficient","urgency":"none","need":"none","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":True,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False},
"SUGGEST":{"permission":"not_required","information":"sufficient","urgency":"none","need":"optional","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False},
"NOTIFY":{"permission":"not_required","information":"sufficient","urgency":"normal","need":"material","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False},
"ASK":{"permission":"missing","information":"sufficient","urgency":"none","need":"material","side_effect":"external","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False},
"ACT":{"permission":"granted","information":"sufficient","urgency":"none","need":"material","side_effect":"external","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False}}
@dataclass(frozen=True)
class Example:
    uid:str; suite:str; text:str; state:dict[str,object]; action:str
    expected_contradiction:bool=False; expected_unknown_factor:str|None=None
    supersession_expected_value:object|None=None; counterfactual_of:str|None=None; changed_factor:str|None=None

def root_group(suite,formal=False):
    if formal:return "holdout"
    if suite=="train":return "train"
    if suite=="validation":return "dev"
    return "stress"

def _apply_syntax(sentence,variant):
    if variant=="passive":return "It is recorded that "+sentence[0].lower()+sentence[1:]
    if variant=="subordinate":return "Although surrounding wording varies, "+sentence[0].lower()+sentence[1:]
    if variant=="nominalized":return "The classification in the record is as follows: "+sentence
    if variant=="reordered":return sentence.replace("Regarding ","The source wording varies; regarding ",1)
    if variant=="fronted" and ", the record marks status as " in sentence:
        a,b=sentence.split(", the record marks status as ",1);return f"The record marks status as {b}; {a.lower()}."
    return sentence

def render_proposition(factor,value,root,scope="general",variant="canonical",certainty="asserted",negated=False,prefix="",syntax=None,rng=None):
    if syntax is not None:variant=syntax
    definition=FACTOR_DEFINITIONS[factor];marker=REVERSE_VALUE_MARKERS[factor][value];scope_text=""
    if factor=="permission":
        if scope=="external_action":scope_text=" for the external operation"
        elif scope=="local_action":scope_text=" for the local operation"
    stance="the record only suggests that the status is" if certainty=="uncertain" else "it is NOT the case that the status is" if negated else "the record marks status as"
    sentence=f"Regarding {definition}{scope_text}, {stance} {marker}. Source wording uses {root}."
    sentence=_apply_syntax(sentence,variant);return prefix+" "+sentence if prefix else sentence

def render_state(state,rng,group=None,suite="compositional",domain=None,root_group=None):
    group=root_group or group; variants=["canonical"] if suite not in {"semantic_paraphrase","syntax_generalization","compositional","ellipsis_pragmatic"} else ["fronted","passive","subordinate","nominalized","reordered"]
    lines=[]
    for factor in FACTOR_DEFINITIONS:
        scope="external_action" if factor=="permission" and state["side_effect"]=="external" else "local_action" if factor=="permission" and state["side_effect"]=="local" else "general"
        lines.append(render_proposition(factor,state[factor],rng.choice(ROOTS[group][factor]),scope,rng.choice(variants)))
    rng.shuffle(lines)
    if domain:lines.insert(0,f"Domain context: {domain}. The domain does not determine the action.")
    return "\n".join(lines)

def base_example(suite,i,rng,group,formal=False):
    action=ACTIONS[i%6];state=dict(BASE_STATES[action])
    if i%11==0 and action=="IGNORE":state["completed"]=True;state["need"]="optional"
    if i%13==0 and action=="SUGGEST":state["risk"]="medium"
    if i%17==0 and action=="NOTIFY":state["urgency"]="high"
    domain=DOMAINS[i%len(DOMAINS)] if suite=="domain_transfer" or formal else None
    return Example(f"{suite}-{i:06d}",suite,render_state(state,rng,group,suite,domain),state,decide_action(state,set()))

def generate_suite(suite,n=None,seed=None,formal=False):
    n=SIZES[suite] if n is None else n;seed=SEEDS[suite] if seed is None else seed;rng=random.Random(seed);group=root_group(suite,formal)
    if suite=="cross_factor_distractor":
        out=[]
        for i in range(n):
            e=base_example(suite,i,rng,group,formal);f=tuple(FACTOR_DEFINITIONS)[(i+5)%12];note=f"Background note mentions {FACTOR_DEFINITIONS[f]} but provides no classified status and must not be treated as evidence."
            out.append(replace(e,text=e.text+"\n"+note))
        return out
    if suite not in {"contradiction","scope","supersession","negation","modality_uncertainty","counterfactual","act_boundary"}:return [base_example(suite,i,rng,group,formal) for i in range(n)]
    out=[]
    if suite=="contradiction":
        for i in range(n):
            state=dict(BASE_STATES["ACT"]);text=render_state(state,rng,group,"compositional")
            if i%2==0:extra=render_proposition("risk","high",rng.choice(ROOTS[group]["risk"]),variant="subordinate");expected=True
            else:extra=render_proposition("permission","missing",rng.choice(ROOTS[group]["permission"]),"local_action","subordinate");expected=False
            out.append(Example(f"{suite}-{i:06d}",suite,text+"\n"+extra,state,"ACT",expected_contradiction=expected))
    elif suite=="scope":
        for i in range(n):
            state=dict(BASE_STATES["ACT"]);text=render_state(state,rng,group,"compositional");extra=render_proposition("permission","missing",rng.choice(ROOTS[group]["permission"]),"local_action","passive")
            out.append(Example(f"{suite}-{i:06d}",suite,text+"\n"+extra,state,"ACT"))
    elif suite=="supersession":
        for i in range(n):
            state=dict(BASE_STATES["ACT"]);lines=[]
            for f in FACTOR_DEFINITIONS:
                if f!="permission":lines.append(render_proposition(f,state[f],rng.choice(ROOTS[group][f])))
            r=rng.choice(ROOTS[group]["permission"]);lines.insert(0,render_proposition("permission","missing",r,"external_action",prefix="Earlier evidence:"));lines.append(render_proposition("permission","granted",r,"external_action",prefix="A later correction replaces the earlier statement."))
            out.append(Example(f"{suite}-{i:06d}",suite,"\n".join(lines),state,"ACT",supersession_expected_value="granted"))
    elif suite=="negation":
        factors=("permission","information","deferral_available","execution_possible","clarification_possible","acknowledged","completed")
        for i in range(n):
            e=base_example(suite,i,rng,group,formal);f=factors[i%len(factors)];target=e.state[f]
            if f=="permission" and target=="not_required":f="information";target=e.state[f]
            opposite=("missing" if target=="granted" else "granted") if f=="permission" else (not target if isinstance(target,bool) else "insufficient" if target=="sufficient" else "sufficient")
            lines=[x for x in e.text.splitlines() if FACTOR_DEFINITIONS[f] not in x];scope="external_action" if f=="permission" and e.state["side_effect"]=="external" else "general"
            lines.append(render_proposition(f,opposite,rng.choice(ROOTS[group][f]),scope,negated=True));out.append(replace(e,text="\n".join(lines)))
    elif suite=="modality_uncertainty":
        for i in range(n):
            if i%5:out.append(base_example(suite,i,rng,group,formal));continue
            state=dict(BASE_STATES["ACT"]);lines=[]
            for f in FACTOR_DEFINITIONS:
                scope="external_action" if f=="permission" else "general";certainty="uncertain" if f=="risk" else "asserted";lines.append(render_proposition(f,state[f],rng.choice(ROOTS[group][f]),scope,certainty=certainty))
            out.append(Example(f"{suite}-{i:06d}",suite,"\n".join(lines),state,"ACT",expected_unknown_factor="risk"))
    elif suite=="counterfactual":
        changes=[("permission","missing"),("risk","high"),("information","insufficient"),("reversibility","irreversible"),("execution_possible",False),("completed",True),("need","optional")]
        for i in range(n):
            base=dict(BASE_STATES["ACT"]);f,new=changes[i%7];cf=dict(base);cf[f]=new;uid=f"{suite}-{i:06d}-base";out.append(Example(uid,suite,render_state(base,rng,group,"compositional"),base,"ACT",changed_factor=f));out.append(Example(f"{suite}-{i:06d}-cf",suite,render_state(cf,rng,group,"compositional"),cf,decide_action(cf,set()),counterfactual_of=uid,changed_factor=f))
    elif suite=="act_boundary":
        changes=[None,("permission","missing"),("risk","high"),("information","insufficient"),("reversibility","irreversible"),("execution_possible",False),("need","optional")]
        for i in range(n):
            state=dict(BASE_STATES["ACT"]);ch=changes[i%7]
            if ch:state[ch[0]]=ch[1]
            out.append(Example(f"{suite}-{i:06d}",suite,render_state(state,rng,group,"compositional"),state,decide_action(state,set()),changed_factor=ch[0] if ch else None))
    return out

def dataset_digest(examples):
    h=hashlib.sha256()
    for e in examples:h.update(json.dumps(e.__dict__,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode());h.update(b"\n")
    return h.hexdigest()
