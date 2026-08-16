from __future__ import annotations
import hashlib,json,random
from pathlib import Path
from benchmark_v8.evaluation import evaluate_rows,qualifies
from benchmark_v8.generator import inject_validation_stress,make_dataset,render_state,write_jsonl
from candidate_v8.model import predict
from candidate_v8.policy import oracle_action
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data"/"candidate_v8_development";REPORTS=ROOT/"reports"/"candidate_v8"
def sha256(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    DATA.mkdir(parents=True,exist_ok=True);REPORTS.mkdir(parents=True,exist_ok=True);train=make_dataset(4800,8001,"train");validation=make_dataset(1200,8002,"validation");inject_validation_stress(validation,8003);write_jsonl(DATA/"train.jsonl",train);write_jsonl(DATA/"validation.jsonl",validation);rng=random.Random(8004);acts=[r for r in validation if r["action"]=="ACT"][:120];pert=[("information","insufficient"),("risk","high"),("reversibility","irreversible"),("execution_possible",False),("need","optional"),("completed",True)];results={}
    for arch in ("V8-A","V8-B","V8-C"):
        m=evaluate_rows(validation,arch);total=correct=disable_total=disable_correct=0
        for row in acts:
            bp=predict(row["text"],arch).action
            for f,v in pert:
                s=dict(row["state"]);s[f]=v;p=predict(render_state(s,"validation",rng),arch).action;g=oracle_action(s);ec=g!="ACT";oc=p!="ACT";total+=1;correct+=int(ec==oc and bp=="ACT");disable_total+=int(ec);disable_correct+=int(ec and oc)
        m["counterfactual_directional_accuracy"]=correct/total;m["counterfactual_act_disable_accuracy"]=disable_correct/disable_total;q=qualifies(m) and m["counterfactual_directional_accuracy"]>=.95 and m["counterfactual_act_disable_accuracy"]==1.0;results[arch]={"metrics":m,"qualified":q}
    qs=[a for a,r in results.items() if r["qualified"]];selected=max(qs,key=lambda a:(results[a]["metrics"]["counterfactual_directional_accuracy"],results[a]["metrics"]["macro_f1"],results[a]["metrics"]["act_recall"])) if qs else None;payload={"architectures":results,"selected":selected,"data":{"train_n":len(train),"validation_n":len(validation),"train_sha256":sha256(DATA/"train.jsonl"),"validation_sha256":sha256(DATA/"validation.jsonl")},"thresholds_locked":True};(REPORTS/"validation_summary.json").write_text(json.dumps(payload,indent=2,sort_keys=True));(REPORTS/"architecture_search.json").write_text(json.dumps(payload,indent=2,sort_keys=True));print(json.dumps(payload,indent=2));return 0 if selected else 2
if __name__=="__main__":raise SystemExit(main())
