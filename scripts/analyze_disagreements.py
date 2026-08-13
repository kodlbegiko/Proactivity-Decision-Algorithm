from __future__ import annotations
import argparse,json
from proactivity.evaluation.annotations import load_annotations
from proactivity.evaluation.gate_b_analysis import disagreement_report
p=argparse.ArgumentParser(); p.add_argument("a"); p.add_argument("b"); args=p.parse_args()
print(json.dumps(disagreement_report(load_annotations(args.a),load_annotations(args.b)),indent=2,sort_keys=True))
