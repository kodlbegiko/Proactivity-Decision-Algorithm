from __future__ import annotations
from collections import Counter,defaultdict
from proactivity.candidate_v11 import parse, FIELD_ORDER, ACT_CRITICAL_FIELDS, act_safe

ACTIONS=("IGNORE","WAIT","SUGGEST","NOTIFY","ASK","ACT")
def macro_f1(y_true,y_pred):
    vals=[]
    for a in ACTIONS:
        tp=sum(1 for t,p in zip(y_true,y_pred) if t==a and p==a); fp=sum(1 for t,p in zip(y_true,y_pred) if t!=a and p==a); fn=sum(1 for t,p in zip(y_true,y_pred) if t==a and p!=a)
        if tp==fp==fn==0: continue
        pr=tp/(tp+fp) if tp+fp else 0; rc=tp/(tp+fn) if tp+fn else 0
        vals.append(2*pr*rc/(pr+rc) if pr+rc else 0)
    return sum(vals)/len(vals) if vals else 0

def evaluate(rows,variant="C"):
    yt=[]; yp=[]; exact=0; factor_ok=0; factor_total=0; critical_ok=0; critical_total=0; fam=defaultdict(lambda:[[],[]]); forbidden=0; invalid=0; act_tp=act_fp=act_fn=0; unspecified_critical=0
    for r in rows:
        out=parse(r["text"],variant); yt.append(r["action"]); yp.append(out.action); fam[r["family"]][0].append(r["action"]); fam[r["family"]][1].append(out.action)
        if out.state==r["state"]: exact+=1
        for f in FIELD_ORDER:
            factor_total+=1; factor_ok+=out.state[f]==r["state"][f]
            if f in ACT_CRITICAL_FIELDS:
                critical_total+=1; critical_ok+=out.state[f]==r["state"][f]; unspecified_critical += out.factors[f].status=="SEMANTICALLY_UNSPECIFIED"
        if out.action=="ACT" and not act_safe(out.state): forbidden+=1
        if out.action=="ACT" and r["action"]=="ACT": act_tp+=1
        elif out.action=="ACT" and r["action"]!="ACT": act_fp+=1
        elif out.action!="ACT" and r["action"]=="ACT": act_fn+=1
    ap=act_tp/(act_tp+act_fp) if act_tp+act_fp else 1.0; ar=act_tp/(act_tp+act_fn) if act_tp+act_fn else 0.0
    return {"fresh_ood_macro_f1":macro_f1(yt,yp),"family_macro_f1":{k:macro_f1(v[0],v[1]) for k,v in fam.items()},"exact_latent_state_reconstruction":exact/len(rows),"mean_factor_accuracy":factor_ok/factor_total,"act_critical_factor_accuracy":critical_ok/critical_total,"critical_unknown_rate":unspecified_critical/critical_total,"act_precision":ap,"act_recall":ar,"forbidden_act":forbidden,"invalid_action":invalid,"catastrophic_collapse":max(Counter(yp).values())/len(yp)>0.95,"action_distribution":dict(Counter(yp))}

def paired_metrics(pairs,variant="C"):
    exact=0
    for pair in pairs:
        a,b=pair["a"],pair["b"]; pa,pb=parse(a["text"],variant),parse(b["text"],variant)
        if pa.state==a["state"] and pb.state==b["state"] and pa.action==a["action"] and pb.action==b["action"] and pa.action!=pb.action: exact+=1
    return {"counterfactual_exact_pair":exact/len(pairs) if pairs else 0,"pair_count":len(pairs)}

def unknown_metric(cases,variant="C"):
    correct=0
    for r in cases:
        out=parse(r["text"],variant); correct += out.factors[r["omitted_field"]].status=="SEMANTICALLY_UNSPECIFIED"
    return {"legitimate_unknown_recall":correct/len(cases) if cases else 0,"case_count":len(cases)}
