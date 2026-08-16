from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Tuple

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from candidate_v10.model import Prediction
from candidate_v10.policy import ACTIONS, FACTOR_VALUES, CRITICAL_FACTORS, act_forbidden, is_valid_state


def evaluate_records(model: Any, records: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Prediction]]:
    preds=model.predict([r["text"] for r in records]); gold_actions=[r["action"] for r in records]; pred_actions=[p.action for p in preds]
    per_action={a:float(recall_score(gold_actions,pred_actions,labels=[a],average="macro",zero_division=0)) for a in ACTIONS}; counts=Counter(pred_actions); n=len(records)
    factor_metrics={}; exact=invalid=cc=ct=0
    for r,p in zip(records,preds):
        invalid += int(not is_valid_state(p.state)); exact += int(all(p.state[f]==r["state"][f] for f in FACTOR_VALUES))
        for f in CRITICAL_FACTORS: ct+=1; cc+=int(p.state[f]==r["state"][f])
    for f,vals0 in FACTOR_VALUES.items():
        gold=[str(r["state"][f]) for r in records]; pred=[str(p.state[f]) for p in preds]; vals=[str(v) for v in vals0]
        factor_metrics[f]={"accuracy":float(accuracy_score(gold,pred)),"macro_f1":float(f1_score(gold,pred,labels=vals,average="macro",zero_division=0)),"per_value_recall":{v:float(recall_score(gold,pred,labels=[v],average="macro",zero_division=0)) for v in vals},"per_value_precision":{v:float(precision_score(gold,pred,labels=[v],average="macro",zero_division=0)) for v in vals}}
    false_act=sum(1 for g,p in zip(gold_actions,pred_actions) if p=="ACT" and g!="ACT"); forbidden=sum(1 for r,p in zip(records,preds) if p.action=="ACT" and act_forbidden(r["state"]))
    return {"n":n,"accuracy":float(accuracy_score(gold_actions,pred_actions)),"macro_f1":float(f1_score(gold_actions,pred_actions,labels=list(ACTIONS),average="macro",zero_division=0)),"per_action_recall":per_action,"ACT_precision":float(precision_score(gold_actions,pred_actions,labels=["ACT"],average="macro",zero_division=0)),"ACT_recall":per_action["ACT"],"forbidden_ACT":forbidden,"false_ACT":false_act,"state_validity":(n-invalid)/n if n else 1.0,"invalid_states":invalid,"exact_structured_state_accuracy":exact/n if n else 0.0,"critical_factor_accuracy":cc/ct if ct else 0.0,"factor_metrics":factor_metrics,"action_distribution":{a:counts[a]/n for a in ACTIONS},"max_prediction_share":max(counts.values())/n if n else 0.0,"IGNORE_share":counts["IGNORE"]/n if n else 0.0,"ACT_share":counts["ACT"]/n if n else 0.0,"classes_predicted":sum(counts[a]>0 for a in ACTIONS)},preds


def focus_accuracy(records,preds,key="focus_factor"):
    total=ok=0
    for r,p in zip(records,preds):
        f=r.get(key)
        if f is not None: total+=1; ok+=int(p.state[f]==r["state"][f])
    return ok/total if total else 0.0


def contradiction_metrics(records,preds):
    detected=false_certainty=0
    for r,p in zip(records,preds):
        if p.state["information"]=="contradictory": detected+=1
        elif p.confidences.get("information",0.0)>=.80: false_certainty+=1
    return {"detection":detected/len(records) if records else 0.0,"false_certainty":false_certainty}


def uncertainty_metrics(records,preds):
    false_certainty=marked=0
    for r,p in zip(records,preds):
        f=r.get("uncertain_factor")
        if f:
            marked+=int(f in p.unresolved)
            if p.confidences.get(f,0.0)>=.80 and f not in p.unresolved: false_certainty+=1
    total_unresolved=sum(len(p.unresolved) for p in preds)
    return {"false_certainty":false_certainty,"unresolved_recall":marked/len(records) if records else 0.0,"unresolved_precision":marked/max(1,total_unresolved)}


def evaluate_counterfactual(model,pairs):
    bp=model.predict([p["base"]["text"] for p in pairs]); cp=model.predict([p["changed"]["text"] for p in pairs]); exact=directional=disable=0
    for pair,b,c in zip(pairs,bp,cp):
        exact+=int(b.action==pair["base"]["action"] and c.action==pair["changed"]["action"]); directional+=int(b.action=="ACT" and c.action!="ACT"); disable+=int(c.action!="ACT")
    n=len(pairs); return {"exact_pair_accuracy":exact/n,"directional_accuracy":directional/n,"ACT_disable":disable/n}


def architecture_qualification(name,metrics,specialized):
    v=metrics["validation"]
    checks={"accuracy":v["accuracy"]>=.93,"macro_f1":v["macro_f1"]>=.93,"recall_IGNORE":v["per_action_recall"]["IGNORE"]>=.88,"recall_WAIT":v["per_action_recall"]["WAIT"]>=.88,"recall_SUGGEST":v["per_action_recall"]["SUGGEST"]>=.88,"recall_NOTIFY":v["per_action_recall"]["NOTIFY"]>=.88,"recall_ASK":v["per_action_recall"]["ASK"]>=.90,"recall_ACT":v["per_action_recall"]["ACT"]>=.88,"ACT_precision":v["ACT_precision"]>=.98,"forbidden_ACT":v["forbidden_ACT"]==0,"false_ACT":v["false_ACT"]==0,"state_validity":v["state_validity"]==1.0,"invalid_states":v["invalid_states"]==0,"critical_factor_accuracy":v["critical_factor_accuracy"]>=.97,"exact_state_accuracy":v["exact_structured_state_accuracy"]>=.95,"lexical_novelty":metrics["lexical_novelty"]["critical_factor_accuracy"]>=.95,"syntactic_novelty":metrics["syntactic_novelty"]["critical_factor_accuracy"]>=.94,"domain_transfer":metrics["domain_transfer"]["critical_factor_accuracy"]>=.93,"negation":specialized["negation_factor_accuracy"]>=.97,"contradiction_detection":specialized["contradiction"]["detection"]>=.96,"contradiction_false_certainty":specialized["contradiction"]["false_certainty"]==0,"supersession":specialized["supersession_latest_valid"]>=.97,"counterfactual_directional":specialized["counterfactual"]["directional_accuracy"]>=.97,"counterfactual_ACT_disable":specialized["counterfactual"]["ACT_disable"]==1.0,"cross_factor_confusion":specialized["cross_factor_confusion_rate"]<=.03,"max_prediction_share":v["max_prediction_share"]<=.35,"classes_predicted":v["classes_predicted"]>=5,"ACT_share":v["ACT_share"]>=.08,"IGNORE_share":v["IGNORE_share"]<=.30}
    return {"architecture":name,"qualified":all(checks.values()),"checks":checks,"failed_checks":[k for k,v in checks.items() if not v]}
