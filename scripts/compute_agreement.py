from __future__ import annotations
import argparse,json
from proactivity.evaluation.annotations import load_annotations,load_metadata,load_packet_sources
from proactivity.evaluation.gate_b_analysis import counterfactual_report,reliability_report,temporal_report
p=argparse.ArgumentParser(); p.add_argument("a"); p.add_argument("b"); p.add_argument("--packet-a"); p.add_argument("--meta"); args=p.parse_args()
a=load_annotations(args.a); b=load_annotations(args.b); sources=load_packet_sources(args.packet_a) if args.packet_a else None
report=reliability_report(a,b,sources)
if args.meta:
    meta=load_metadata(args.meta); report["counterfactual_reliability"]=counterfactual_report(a,b,meta); report["temporal_reliability"]=temporal_report(a,b,meta)
print(json.dumps(report,indent=2,sort_keys=True))
