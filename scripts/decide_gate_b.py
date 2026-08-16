from __future__ import annotations
import argparse
from proactivity.evaluation import decide_gate_b
p=argparse.ArgumentParser(); p.add_argument("--human-annotations-present",action="store_true"); p.add_argument("--raw-agreement",type=float); p.add_argument("--kappa",type=float); p.add_argument("--core-class-collapse",action="store_true"); p.add_argument("--label-leakage-acceptable",choices=["true","false"]); p.add_argument("--all-other-conditions-pass",action="store_true"); x=p.parse_args()
leakage=None if x.label_leakage_acceptable is None else x.label_leakage_acceptable=="true"
print(decide_gate_b(human_annotations_present=x.human_annotations_present,raw_agreement=x.raw_agreement,kappa=x.kappa,core_class_collapse=x.core_class_collapse,label_leakage_acceptable=leakage,all_other_conditions_pass=x.all_other_conditions_pass))
