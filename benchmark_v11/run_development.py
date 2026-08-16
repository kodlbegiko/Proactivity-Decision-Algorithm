from __future__ import annotations
import argparse, json
from benchmark_v11 import generator as g, evaluation as e
from proactivity import candidate_v11 as c

SELECTED="B"
def false_unknown_rate(rows, variant=SELECTED):
    total=unknown=0
    for r in rows:
        out=c.parse(r["text"],variant)
        for f in c.FIELD_ORDER: total+=1; unknown += out.factors[f].status=="SEMANTICALLY_UNSPECIFIED"
    return unknown/total if total else 0.0

def invariance(rows, variant=SELECTED):
    good=state_good=0; subset=rows[:350]
    for i,r in enumerate(subset):
        outs=[c.parse(t,variant) for t in g.invariance_texts(r["state"],9000+i)]
        good += len({o.action for o in outs})==1; state_good += all(o.state==outs[0].state for o in outs[1:])
    return {"action_consistency":good/len(subset),"latent_consistency":state_good/len(subset),"groups":len(subset)}

def main(check=False):
    development=(g.make_dataset(1400,1101,0)+g.make_dataset(1400,2207,2)+g.make_dataset(1750,3301,4)+g.make_action_balanced_dataset(250,4409,4))
    search={v:e.evaluate(development,v) for v in ("A","B","C")}
    fresh=g.make_action_balanced_dataset(250,5501,1); metrics=e.evaluate(fresh,SELECTED)
    cf=e.paired_metrics(g.counterfactual_pairs(280,7229,1),SELECTED); unk=e.unknown_metric(g.unknown_cases(280,8231,1),SELECTED); inv=invariance(fresh,SELECTED)
    out={"selected_variant":SELECTED,"development_count":len(development),"fresh_validation_count":len(fresh),"architecture_search":search,"fresh_validation":metrics,"false_unknown_rate":false_unknown_rate(fresh),"counterfactual":cf,"unknown_calibration":unk,"invariance":inv}
    if check:
        fm=metrics["family_macro_f1"]
        assert metrics["fresh_ood_macro_f1"]>=0.88
        assert all(fm[x]>=0.88 for x in ("Lexical","Rendering","Compositional","Negation","Scope","Temporal")); assert fm["Mixed Adversarial"]>=0.82
        assert metrics["exact_latent_state_reconstruction"]>=0.80; assert metrics["mean_factor_accuracy"]>=0.95; assert metrics["act_critical_factor_accuracy"]>=0.97
        assert metrics["critical_unknown_rate"]<=0.05; assert out["false_unknown_rate"]<=0.08; assert unk["legitimate_unknown_recall"]>=0.95
        assert cf["counterfactual_exact_pair"]>=0.88; assert inv["action_consistency"]>=0.95
        assert metrics["act_precision"]>=0.95 and metrics["act_recall"]>=0.85; assert metrics["forbidden_act"]==0 and metrics["invalid_action"]==0; assert not metrics["catastrophic_collapse"]
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--check",action="store_true"); args=ap.parse_args(); main(args.check)
