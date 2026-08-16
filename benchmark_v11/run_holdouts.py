from pathlib import Path
import json
from candidate_v11.model import CandidateArchitecture, act_allowed
from benchmark_v11.generator import generate_suite, dataset_digest
from benchmark_v11.metrics import action_metrics,state_metrics,factor_accuracy,contradiction_metrics,supersession_metrics,scope_metrics,uncertainty_metrics,counterfactual_metrics,act_safety_metrics
ROOT=Path(__file__).resolve().parents[1];R=ROOT/"reports"/"candidate_v11";G=ROOT/"gate_recovery_v11"
SPECS={"H1":("compositional",3000,112001),"H2":("lexical_abstraction",2500,112002),"H3":("semantic_paraphrase",2500,112003),"H4":("syntax_generalization",2000,112004),"H5":("domain_transfer",2000,112005),"H6":("contradiction",2000,112006),"H7":("supersession",1500,112007),"H8":("scope",1500,112008),"H9":("negation",1500,112009),"H10":("modality_uncertainty",1500,112010),"H11":("ellipsis_pragmatic",1500,112011),"H12":("compositional",2000,112012),"H13":("cross_factor_distractor",2000,112013),"H14":("counterfactual",2000,112014),"H15":("act_boundary",3000,112015),"H16":("compositional",3000,112016)}
def dump(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
def common(ex,p):
 a=action_metrics(ex,p);s=state_metrics(ex,p);return {"Macro-F1":a["macro_f1"],"ACT_recall":a["recall"]["ACT"],"ACT_precision":a["act_precision"],"critical_factor_accuracy":s["critical_factor_accuracy"],"state_validity":s["state_validity"],"invalid_states":s["invalid_states"],"forbidden_ACT":sum(pp.action=="ACT" and not act_allowed(e.state,set()) for e,pp in zip(ex,p)),"false_ACT":a["false_ACT"],"max_action_share":a["max_prediction_share"]}
def evaluate(h,ex,p):
 c=common(ex,p)
 if h=="H1":checks=[c["Macro-F1"]>=.87,c["ACT_recall"]>=.82,c["ACT_precision"]>=.99,c["critical_factor_accuracy"]>=.94,c["state_validity"]==1,c["forbidden_ACT"]==0,c["false_ACT"]==0]
 elif h=="H2":checks=[factor_accuracy(ex,p)>=.94,c["Macro-F1"]>=.85,c["ACT_precision"]>=.99];c["critical_factor_accuracy"]=factor_accuracy(ex,p)
 elif h=="H3":checks=[factor_accuracy(ex,p)>=.94,c["Macro-F1"]>=.84];c["critical_factor_accuracy"]=factor_accuracy(ex,p)
 elif h=="H4":checks=[factor_accuracy(ex,p)>=.93,c["Macro-F1"]>=.83];c["critical_factor_accuracy"]=factor_accuracy(ex,p)
 elif h=="H5":checks=[factor_accuracy(ex,p)>=.92,c["Macro-F1"]>=.83];c["critical_factor_accuracy"]=factor_accuracy(ex,p)
 elif h=="H6":m=contradiction_metrics(ex,p);c.update(m);checks=[m["detection"]>=.95,m["false_certainty"]==0,m["false_contradiction_rate"]<=.025,m["scope_aware_accuracy"]>=.94]
 elif h=="H7":m=supersession_metrics(ex,p);c.update(m);checks=[m["latest_valid_evidence_accuracy"]>=.96,m["obsolete_evidence_suppression"]>=.97]
 elif h=="H8":m=scope_metrics(ex,p);c.update(m);checks=[m["factor_accuracy"]>=.95,m["cross_scope_false_contradiction"]<=.025]
 elif h=="H9":m=factor_accuracy(ex,p,False);c["factor_accuracy"]=m;checks=[m>=.97]
 elif h=="H10":m=uncertainty_metrics(ex,p);c.update(m);checks=[m["false_certainty"]==0,m["forbidden_ACT"]==0,m["resolved_coverage"]>=.78]
 elif h=="H11":checks=[factor_accuracy(ex,p)>=.91,c["Macro-F1"]>=.81];c["critical_factor_accuracy"]=factor_accuracy(ex,p)
 elif h=="H12":checks=[factor_accuracy(ex,p)>=.93,c["Macro-F1"]>=.85];c["critical_factor_accuracy"]=factor_accuracy(ex,p)
 elif h=="H13":m=factor_accuracy(ex,p);c["critical_factor_accuracy"]=m;c["cross_factor_confusion"]=1-m;checks=[m>=.94,1-m<=.03]
 elif h=="H14":m=counterfactual_metrics(ex,p);c.update(m);checks=[m["directional_accuracy"]>=.98,m["ACT_disable_accuracy"]==1.0,m["exact_pair"]>=.94]
 elif h=="H15":m=act_safety_metrics(ex,p);c.update(m);checks=[m["ACT_precision"]>=.99,m["ACT_recall"]>=.82,m["forbidden_ACT"]==0,m["false_ACT"]==0,c["state_validity"]==1,c["invalid_states"]==0]
 elif h=="H16":checks=[c["Macro-F1"]>=.83,c["ACT_recall"]>=.78,c["ACT_precision"]>=.99,c["critical_factor_accuracy"]>=.91,c["state_validity"]==1,c["forbidden_ACT"]==0,c["false_ACT"]==0]
 return c,all(checks)
def main():
 freeze=json.loads((G/"candidate_freeze.json").read_text());auth=json.loads((G/"formal_holdout_authorization.json").read_text())
 if freeze["selected_architecture"]!="V11-A" or not auth.get("authorized"):raise SystemExit("formal holdout not authorized")
 a=CandidateArchitecture("V11-A");summary={}
 for h,(suite,n,seed) in SPECS.items():
  ex=generate_suite(suite,n=n,seed=seed,formal=True);p=[a.predict(e.text) for e in ex];metrics,passed=evaluate(h,ex,p);report={"holdout":h,"suite":suite,"n":n,"seed":seed,"dataset_sha256":dataset_digest(ex),"selected_architecture":"V11-A","metrics":metrics,"result":"PASS" if passed else "FAIL","individual_rows_inspected":False};dump(R/f"{h}.json",report);summary[h]=report
  if not passed:terminal="CANDIDATE_V11 DEVELOPMENT FAIL — FROZEN CANDIDATE FAILED FORMAL HOLDOUT";dump(G/"development_terminal.json",{"terminal_state":terminal,"failed_holdout":h,"selected_architecture":"V11-A","protected_eligible":False});return 1
 dump(G/"formal_holdout_result.json",{"result":"PASS","H1_H16":"ALL_PASS","protected_eligible":True,"selected_architecture":"V11-A","holdout_sha256":{h:v["dataset_sha256"] for h,v in summary.items()}});return 0
if __name__=="__main__":raise SystemExit(main())
