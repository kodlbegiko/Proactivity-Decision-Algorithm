from __future__ import annotations
import argparse, json
from proactivity.evaluation.agreement import cohen_kappa, raw_agreement
from proactivity.evaluation.annotations import load_annotations
p=argparse.ArgumentParser(); p.add_argument("a"); p.add_argument("b"); args=p.parse_args()
a={x.scenario_id:x for x in load_annotations(args.a)}; b={x.scenario_id:x for x in load_annotations(args.b)}
if set(a)!=set(b): raise SystemExit("annotation scenario sets differ")
ids=sorted(a); la=[a[i].preferred_action.value for i in ids]; lb=[b[i].preferred_action.value for i in ids]
amb=sum(a[i].ambiguity_flag or b[i].ambiguity_flag for i in ids)/len(ids)
print(json.dumps({"n":len(ids),"raw_agreement":raw_agreement(la,lb),"cohen_kappa":cohen_kappa(la,lb),"either_annotator_ambiguity_rate":amb},indent=2))
