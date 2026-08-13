from __future__ import annotations
import argparse,json
from proactivity.evaluation.annotations import load_annotations,load_packet_sources
from proactivity.evaluation.gate_b_analysis import reliability_report
p=argparse.ArgumentParser(); p.add_argument("a"); p.add_argument("b"); p.add_argument("--packet-a"); args=p.parse_args()
sources=load_packet_sources(args.packet_a) if args.packet_a else None
print(json.dumps(reliability_report(load_annotations(args.a),load_annotations(args.b),sources),indent=2,sort_keys=True))
