from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score,f1_score,precision_recall_fscore_support,confusion_matrix
from proactivity.candidate_v5 import ACTIONS,FIELDS,VALUES,CRITICAL,UNKNOWN,lab
from proactivity.specification.oracle import evaluate

def load_jsonl(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
def load_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def write_json(path,obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
def action_metrics(records,pred):
    y=[r["oracle_action"] for r in records]
    pr,rc,f1,sup=precision_recall_fscore_support(y,pred,labels=ACTIONS,zero_division=0)
    dist=Counter(pred); n=max(len(pred),1); mx=max(dist.values(),default=0)/n
    forbidden=0
    for r,p in zip(records,pred):
        if p=="ACT" and "ACT" in evaluate(r["latent_state"]).prohibited_actions: forbidden+=1
    pa={a:{"precision":float(pr[i]),"recall":float(rc[i]),"f1":float(f1[i]),"support":int(sup[i])} for i,a in enumerate(ACTIONS)}
    zero=[a for a in ACTIONS if pa[a]["recall"]==0.0]; used=[a for a in ACTIONS if dist.get(a,0)]
    return {"accuracy":float(accuracy_score(y,pred)),"macro_f1":float(f1_score(y,pred,labels=ACTIONS,average="macro",zero_division=0)),
      "per_action":pa,"prediction_distribution":{a:int(dist.get(a,0)) for a in ACTIONS},"max_prediction_class_share":float(mx),
      "invalid_action":sum(p not in ACTIONS for p in pred),"forbidden_act":forbidden,"action_disappearance":zero,
      "single_class_collapse":len(used)<=1,"two_class_collapse":len(used)<=2,"catastrophic_collapse":bool(mx>=.80 or len(zero)>=3)}
def factor_metrics(records,parses):
    pf={}; exact=0
    for r,p in zip(records,parses): exact+=int(all(p.state.get(f)==r["latent_state"][f] for f in FIELDS))
    for f in FIELDS:
        legal=[lab(v) for v in VALUES[f]]; truth=[lab(r["latent_state"][f]) for r in records]
        pred=[UNKNOWN if p.state.get(f)==UNKNOWN else lab(p.state.get(f)) for p in parses]
        conf=np.asarray([float(p.confidence.get(f,0)) for p in parses]); good=np.asarray([a==b for a,b in zip(truth,pred)],dtype=float)
        labels=legal+[UNKNOWN]
        pf[f]={"accuracy":float(good.mean()),"macro_f1":float(f1_score(truth,pred,labels=legal,average="macro",zero_division=0)),
          "unknown_rate":float(sum(x==UNKNOWN for x in pred)/max(len(pred),1)),"mean_confidence":float(conf.mean()),
          "confidence_brier":float(np.mean((conf-good)**2)),"confusion_labels":labels,"confusion_matrix":confusion_matrix(truth,pred,labels=labels).tolist()}
    return {"per_field":pf,"exact_latent_state_reconstruction":exact/max(len(records),1),
      "act_critical_factor_macro_accuracy":float(np.mean([pf[f]["accuracy"] for f in CRITICAL])),
      "critical_factor_unknown_rate":float(np.mean([pf[f]["unknown_rate"] for f in CRITICAL]))}
def eval_candidate(candidate,records):
    parses=candidate.parse_records(records); pred=[candidate.action(p) for p in parses]
    return {"action":action_metrics(records,pred),"factor":factor_metrics(records,parses)},parses,pred
def pair_metrics(candidate,records,invariance=False):
    m,parses,pred=eval_candidate(candidate,records); g=defaultdict(list)
    for i,r in enumerate(records): g[r["pair_id"]].append(i)
    exact=consistent=directional=latent=0; cc=[]; trans=defaultdict(list)
    for pid,ix in g.items():
        a,b=ix; both=pred[a]==records[a]["oracle_action"] and pred[b]==records[b]["oracle_action"]; exact+=both
        consistent+=pred[a]==pred[b]; directional+=(records[a]["oracle_action"]!=records[b]["oracle_action"])==(pred[a]!=pred[b])
        latent+=parses[a].state==parses[b].state
        cc.append(sum(parses[a].state.get(f)==parses[b].state.get(f) for f in CRITICAL)/len(CRITICAL))
        if not invariance: trans[records[a].get("transition","unknown")].append(float(both))
    n=max(len(g),1); out={"pairs":len(g),"exact_pair_correctness":exact/n,"prediction_consistency":consistent/n,
      "directional_change_accuracy":directional/n,"critical_factor_consistency":float(np.mean(cc)),"forbidden_act":m["action"]["forbidden_act"]}
    if invariance: out.update({"action_consistency":consistent/n,"exact_both_correctness":exact/n,"latent_state_consistency":latent/n})
    else: out["transition_specific_exact_pair"]={k:float(np.mean(v)) for k,v in sorted(trans.items())}
    return out
