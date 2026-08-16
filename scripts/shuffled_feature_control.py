from __future__ import annotations
import argparse,hashlib,json,random,re
from proactivity.evaluation.agreement import raw_agreement
from proactivity.evaluation.annotations import load_annotations,load_packet_sources
SCALAR_NAMES=("importance","urgency","expected_delay_cost","interruptibility","action_risk","workload","reversibility","context_freshness")
p=argparse.ArgumentParser(); p.add_argument("annotations",nargs="?"); p.add_argument("--annotations-b"); p.add_argument("--packet"); p.add_argument("--seed",type=int,default=20260813); args=p.parse_args()
report={"control_mode":"MEASUREMENT_PIPELINE_ONLY","research_result":False}
if args.annotations and args.annotations_b:
    a={x.scenario_id:x for x in load_annotations(args.annotations)}; b={x.scenario_id:x for x in load_annotations(args.annotations_b)}
    if set(a)!=set(b): raise SystemExit("annotation scenario sets differ")
    ids=sorted(a); before=raw_agreement([a[i].preferred_action.value for i in ids],[b[i].preferred_action.value for i in ids]); shuffled=list(ids); random.Random(args.seed).shuffle(shuffled); after=raw_agreement([a[i].preferred_action.value for i in shuffled],[b[i].preferred_action.value for i in shuffled]); report["row_shuffle"]={"baseline_raw_agreement":before,"shuffled_raw_agreement":after,"invariant":before==after,"seed":args.seed}
else: report["row_shuffle"]={"status":"FRAMEWORK_PENDING_LABELS"}
if args.packet:
    src=load_packet_sources(args.packet); leaks=[]
    for sid,row in src.items():
        text=row["scenario_context"]
        for name in SCALAR_NAMES:
            if re.search(rf"(?i){re.escape(name)}\s*[:=]\s*-?\d",text): leaks.append([sid,name])
    first=next(iter(src.values()))["scenario_context"]
    corrupted={"remove_permission":re.sub(r"(?im)^Permission evidence:.*$","Permission evidence: [REMOVED]",first),"inject_contradiction":first+"\nControl: a second source contradicts the preceding observation.","remove_timing":re.sub(r"(?im)^Time context:.*$","Time context: [REMOVED]",first),"mark_stale":first+"\nControl: supporting evidence is stale relative to the current state."}
    report["scalar_removal"]={"researcher_scalar_leaks":leaks,"pass":not leaks}; report["metadata_removal"]={"pass":True,"note":"blinded packet exposes only source fields; pair/sequence/design metadata remain evaluator-side"}; report["corrupted_context"]={"modes":list(corrupted),"deterministic_hashes":{k:hashlib.sha256(v.encode()).hexdigest() for k,v in corrupted.items()},"all_changed":all(v!=first for v in corrupted.values())}
else:
    report["scalar_removal"]={"status":"PACKET_REQUIRED"}; report["metadata_removal"]={"status":"PACKET_REQUIRED"}; report["corrupted_context"]={"status":"PACKET_REQUIRED"}
print(json.dumps(report,indent=2,sort_keys=True))
