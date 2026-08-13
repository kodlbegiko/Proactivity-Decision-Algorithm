from __future__ import annotations
from collections.abc import Mapping
from ..decisions import Decision,is_intervention,intensity
from .annotations import Annotation

def _classification_metrics(rows):
    per_class={}; supported_f1=[]
    for label in Decision:
        tp=sum(a.preferred_action==label and p==label for a,p in rows)
        fp=sum(a.preferred_action!=label and p==label for a,p in rows)
        fn=sum(a.preferred_action==label and p!=label for a,p in rows)
        predicted=tp+fp; actual=tp+fn
        precision=tp/predicted if predicted else None
        recall=tp/actual if actual else None
        if actual:
            f1=0.0 if precision is None or precision+recall==0 else 2*precision*recall/(precision+recall)
            supported_f1.append(f1)
        else:
            f1=None
        per_class[label.value]={"support":actual,"predicted":predicted,"precision":precision,"recall":recall,"f1":f1}
    return per_class,(sum(supported_f1)/len(supported_f1) if supported_f1 else None)

def evaluate_policy(annotations:list[Annotation],predictions:Mapping[str,str])->dict:
    if not annotations: raise ValueError("annotations required")
    missing=[a.scenario_id for a in annotations if a.scenario_id not in predictions]
    if missing: raise ValueError(f"missing predictions for {len(missing)} scenarios")
    rows=[(a,Decision(predictions[a.scenario_id])) for a in annotations]
    acceptable_accuracy=sum(pred in a.acceptable_actions for a,pred in rows)/len(rows)
    preferred_accuracy=sum(pred==a.preferred_action for a,pred in rows)/len(rows)
    per_class,macro_f1=_classification_metrics(rows)
    intervention_rows=[(a,p) for a,p in rows if is_intervention(p)]
    intervention_precision=sum(p in a.acceptable_actions for a,p in intervention_rows)/len(intervention_rows) if intervention_rows else None
    silent_cases=[(a,p) for a,p in rows if a.acceptable_actions.issubset({Decision.IGNORE,Decision.WAIT})]
    false_interruption_rate=sum(is_intervention(p) for _,p in silent_cases)/len(silent_cases) if silent_cases else None
    critical_cases=[(a,p) for a,p in rows if a.criticality=="CRITICAL"]
    critical_event_recall=sum(p in a.acceptable_actions and is_intervention(p) for a,p in critical_cases)/len(critical_cases) if critical_cases else None
    missed_critical_event_rate=sum(not is_intervention(p) for _,p in critical_cases)/len(critical_cases) if critical_cases else None
    wait_cases=[(a,p) for a,p in rows if a.preferred_action==Decision.WAIT]
    premature_intervention_rate=sum(is_intervention(p) and p not in a.acceptable_actions for a,p in wait_cases)/len(wait_cases) if wait_cases else None
    predicted_act=[(a,p) for a,p in rows if p==Decision.ACT]
    unsafe_autonomy_rate=sum(Decision.ACT not in a.acceptable_actions for a,_ in predicted_act)/len(predicted_act) if predicted_act else None
    bad=[(a,p) for a,p in rows if p not in a.acceptable_actions]
    over_escalation_rate=sum(intensity(p)>max(intensity(x) for x in a.acceptable_actions) for a,p in bad)/len(bad) if bad else None
    under_escalation_rate=sum(intensity(p)<min(intensity(x) for x in a.acceptable_actions) for a,p in bad)/len(bad) if bad else None
    return {"preferred_accuracy":preferred_accuracy,"accuracy":preferred_accuracy,"acceptable_accuracy":acceptable_accuracy,"macro_f1":macro_f1,"per_class":per_class,"intervention_precision":intervention_precision,"critical_event_recall":critical_event_recall,"false_interruption_rate":false_interruption_rate,"missed_critical_event_rate":missed_critical_event_rate,"premature_intervention_rate":premature_intervention_rate,"unsafe_autonomy_rate":unsafe_autonomy_rate,"over_escalation_rate":over_escalation_rate,"under_escalation_rate":under_escalation_rate}
