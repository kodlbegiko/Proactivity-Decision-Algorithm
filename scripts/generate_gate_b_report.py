from __future__ import annotations
import argparse,json
from proactivity.evaluation import blocked_report
from proactivity.evaluation.annotations import load_annotations,load_metadata,load_packet_sources
from proactivity.evaluation.gate_b_analysis import counterfactual_report,reliability_report,temporal_report
p=argparse.ArgumentParser(); p.add_argument("--a"); p.add_argument("--b"); p.add_argument("--packet-a"); p.add_argument("--meta"); x=p.parse_args()
if not x.a or not x.b:
    report=blocked_report()
else:
    a=load_annotations(x.a); b=load_annotations(x.b); sources=load_packet_sources(x.packet_a) if x.packet_a else None; report=reliability_report(a,b,sources)
    if x.meta:
        meta=load_metadata(x.meta); report["counterfactual_reliability"]=counterfactual_report(a,b,meta); report["temporal_reliability"]=temporal_report(a,b,meta)
print(json.dumps(report,indent=2,sort_keys=True))
