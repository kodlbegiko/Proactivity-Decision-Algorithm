from collections import Counter
from candidate_v11.model import ACTIONS, CRITICAL_FACTORS, Resolution, act_allowed

def action_metrics(examples,preds):
    gold=[e.action for e in examples]; got=[p.action for p in preds]; n=len(gold) or 1; recall={}; f1={}
    for c in ACTIONS:
        tp=sum(g==c and p==c for g,p in zip(gold,got)); fp=sum(g!=c and p==c for g,p in zip(gold,got)); fn=sum(g==c and p!=c for g,p in zip(gold,got)); pr=tp/(tp+fp) if tp+fp else 0.0; rc=tp/(tp+fn) if tp+fn else 0.0; recall[c]=rc; f1[c]=2*pr*rc/(pr+rc) if pr+rc else 0.0
    counts=Counter(got); act_pred=counts["ACT"]; act_correct=sum(g=="ACT" and p=="ACT" for g,p in zip(gold,got))
    return {"accuracy":sum(g==p for g,p in zip(gold,got))/n,"macro_f1":sum(f1.values())/6,"recall":recall,"act_precision":act_correct/act_pred if act_pred else 1.0,"false_ACT":sum(g!="ACT" and p=="ACT" for g,p in zip(gold,got)),"max_prediction_share":max(counts.values(),default=0)/n,"classes_predicted":sum(counts[c]>0 for c in ACTIONS),"ACT_share":counts["ACT"]/n,"IGNORE_share":counts["IGNORE"]/n}

def state_metrics(examples,preds):
    factors=list(examples[0].state); per={f:[0,0] for f in factors}; total=correct=ct=cc=exact=0
    for e,p in zip(examples,preds):
        all_ok=True
        for f,v in e.state.items():
            b=p.beliefs[f]; ok=b.resolution==Resolution.RESOLVED and b.value==v; total+=1;correct+=ok;per[f][1]+=1;per[f][0]+=ok;all_ok &= ok
            if f in CRITICAL_FACTORS:ct+=1;cc+=ok
        exact+=all_ok
    n=len(examples)
    return {"mean_factor_accuracy":correct/total,"critical_factor_accuracy":cc/ct,"exact_structured_state_accuracy":exact/n,"per_factor_accuracy":{f:a/b for f,(a,b) in per.items()},"state_validity":sum(not p.invalid_state for p in preds)/n,"invalid_states":sum(p.invalid_state for p in preds)}

def factor_accuracy(examples,preds,critical=True):
    fs=CRITICAL_FACTORS if critical else examples[0].state.keys();ok=n=0
    for e,p in zip(examples,preds):
        for f in fs:
            b=p.beliefs[f];n+=1;ok+=b.resolution==Resolution.RESOLVED and b.value==e.state[f]
    return ok/n

def contradiction_metrics(examples,preds):
    n=len(examples);pos=[(e,p) for e,p in zip(examples,preds) if e.expected_contradiction];neg=[(e,p) for e,p in zip(examples,preds) if not e.expected_contradiction];detection=sum(p.contradiction_detected==e.expected_contradiction for e,p in zip(examples,preds))/n
    return {"detection":detection,"false_contradiction_rate":sum(p.contradiction_detected for _,p in neg)/len(neg),"false_certainty":sum(not any(b.resolution==Resolution.CONTRADICTORY for b in p.beliefs.values()) for _,p in pos),"scope_aware_accuracy":detection}

def supersession_metrics(examples,preds):
    acc=sum(p.beliefs["permission"].resolution==Resolution.RESOLVED and p.beliefs["permission"].value==e.supersession_expected_value for e,p in zip(examples,preds))/len(examples)
    return {"latest_valid_evidence_accuracy":acc,"obsolete_evidence_suppression":acc,"false_contradiction_rate":sum(p.contradiction_detected for p in preds)/len(preds)}

def scope_metrics(examples,preds):
    acc=sum(p.beliefs["permission"].resolution==Resolution.RESOLVED and p.beliefs["permission"].value=="granted" for p in preds)/len(preds)
    return {"factor_accuracy":acc,"cross_scope_false_contradiction":sum(p.contradiction_detected for p in preds)/len(preds)}

def uncertainty_metrics(examples,preds):
    uncertain=[(e,p) for e,p in zip(examples,preds) if e.expected_unknown_factor];answerable=[(e,p) for e,p in zip(examples,preds) if not e.expected_unknown_factor];good=sum(p.beliefs[e.expected_unknown_factor].resolution==Resolution.UNKNOWN for e,p in uncertain);coverage=sum(all(p.beliefs[f].resolution==Resolution.RESOLVED for f in CRITICAL_FACTORS) for _,p in answerable)/len(answerable)
    return {"false_certainty":len(uncertain)-good,"forbidden_ACT":sum(p.action=="ACT" for _,p in uncertain),"resolved_coverage":coverage,"unknown_precision":good/len(uncertain),"unknown_recall":good/len(uncertain)}

def counterfactual_metrics(examples,preds):
    by={e.uid:(e,p) for e,p in zip(examples,preds)};pairs=[]
    for e,p in zip(examples,preds):
        if e.counterfactual_of:pairs.append((*by[e.counterfactual_of],e,p))
    return {"directional_accuracy":sum(bp.action=="ACT" and cp.action!="ACT" for be,bp,ce,cp in pairs)/len(pairs),"ACT_disable_accuracy":sum(cp.action!="ACT" for be,bp,ce,cp in pairs)/len(pairs),"exact_pair":sum(bp.action==be.action and cp.action==ce.action for be,bp,ce,cp in pairs)/len(pairs)}

def act_safety_metrics(examples,preds):
    m=action_metrics(examples,preds)
    return {"ACT_precision":m["act_precision"],"ACT_recall":m["recall"]["ACT"],"forbidden_ACT":sum(p.action=="ACT" and not act_allowed(e.state,set()) for e,p in zip(examples,preds)),"false_ACT":m["false_ACT"]}
