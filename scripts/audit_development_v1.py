from __future__ import annotations

import argparse,json,re
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from proactivity.evaluation.annotations import load_annotations,load_metadata,load_packet_sources
from proactivity.evaluation.gate_b_analysis import lexical_leakage_report,metadata_leakage_report

FORBIDDEN_INPUT_KEYS={"design_category","pair_id","pair_variant","changed_variable","intended_relation","sequence_id","sequence_stage","transition_type","expected_label","gold_action","correct_decision","design_intent"}
def load_jsonl(path): return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
def text_repr(r):
    rc=r["raw_context"]; return " ".join([rc["current_activity"],rc["event_summary"],*rc["observable_facts"],*rc.get("recent_history",[]),rc.get("permission_evidence","")]).lower()
def norm_text(s): return " ".join(re.findall(r"[a-z0-9]+",s.lower()))
def structural(r): return {"user_state":r["user_state"],"event":r["event"],"task_state":r["task_state"],"action_risk":r["action_risk"],"reversibility":r["reversibility"],"expected_delay_cost":r["expected_delay_cost"],"permission_required":r["permission_required"],"permission_granted":r["permission_granted"],"context_freshness":r["context_freshness"]}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("dataset"); ap.add_argument("metadata"); ap.add_argument("--json-out"); ap.add_argument("--annotations"); ap.add_argument("--packet"); ap.add_argument("--validated-human-annotations",action="store_true"); args=ap.parse_args()
    rows=load_jsonl(args.dataset); meta=load_jsonl(args.metadata); by_meta={x["scenario_id"]:x for x in meta}; ids=[r["scenario_id"] for r in rows]
    exact=Counter(json.dumps({k:v for k,v in r.items() if k not in {"scenario_id","timestamp"}},sort_keys=True) for r in rows); exact_dups=sum(n for n in exact.values() if n>1); structs=Counter(json.dumps(structural(r),sort_keys=True) for r in rows); structural_dups=sum(n for n in structs.values() if n>1)
    near_violations=[]; intentional_near=[]; texts=[norm_text(text_repr(r)) for r in rows]
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):
            ratio=SequenceMatcher(None,texts[i],texts[j]).ratio()
            if ratio<.90: continue
            mi,mj=by_meta[ids[i]],by_meta[ids[j]]; related=(mi.get("pair_id") and mi.get("pair_id")==mj.get("pair_id")) or (mi.get("sequence_id") and mi.get("sequence_id")==mj.get("sequence_id")); item=(ids[i],ids[j],round(ratio,3)); (intentional_near if related else near_violations).append(item)
    forbidden=[]
    for r in rows:
        hit=FORBIDDEN_INPUT_KEYS.intersection(r)
        if hit: forbidden.append((r["scenario_id"],sorted(hit)))
        if not re.fullmatch(r"dv1-[0-9a-f]{12}",r["scenario_id"]): forbidden.append((r["scenario_id"],["non_opaque_id"]))
        if any(d in r["scenario_id"] for d in {"study","work","scheduling","communication","device","travel"}): forbidden.append((r["scenario_id"],["domain_in_id"]))
    domains=Counter(r["domain"] for r in rows); longest=1; cur=1
    for a,b in zip(rows,rows[1:]):
        if a["domain"]==b["domain"]: cur+=1; longest=max(longest,cur)
        else: cur=1
    token_cat=defaultdict(Counter)
    for r in rows:
        cat=by_meta[r["scenario_id"]]["design_category"]
        for tok in set(norm_text(text_repr(r)).split()): token_cat[tok][cat]+=1
    shortcut=[]
    for tok,c in token_cat.items():
        total=sum(c.values()); cat,n=c.most_common(1)[0]
        if total>=5 and n/total>=.90: shortcut.append((tok,cat,total,round(n/total,3)))
    shortcut=sorted(shortcut,key=lambda x:(-x[3],-x[2],x[0]))[:30]; prelabel_pass=(len(rows)==144 and len(set(ids))==144 and set(domains.values())=={24} and exact_dups==0 and structural_dups==0 and not near_violations and not forbidden and longest<=3)
    report={"scenario_count":len(rows),"unique_ids":len(set(ids)),"domain_counts":dict(sorted(domains.items())),"exact_duplicate_members":exact_dups,"structural_duplicate_members":structural_dups,"unrelated_near_duplicate_pairs":len(near_violations),"intentional_related_near_pairs":len(intentional_near),"metadata_leakage_findings":forbidden,"longest_same_domain_run":longest,"design_category_shortcut_candidates":shortcut,"label_dependent_lexical_audit":"NOT_EXECUTED_NO_INDEPENDENT_LABELS","metadata_label_audit":"NOT_EXECUTED_NO_INDEPENDENT_LABELS","shuffled_feature_control":"FRAMEWORK_PENDING_LABELS","pre_annotation_leakage_gate":"PASS" if prelabel_pass else "FAIL"}
    if args.annotations or args.packet or args.validated_human_annotations:
        if not (args.annotations and args.packet and args.validated_human_annotations): raise SystemExit("post-label audit requires --annotations, --packet, and --validated-human-annotations")
        annotations=load_annotations(args.annotations); sources=load_packet_sources(args.packet); metadata=load_metadata(args.metadata); report["label_dependent_lexical_audit"]=lexical_leakage_report(annotations,sources); report["metadata_label_audit"]=metadata_leakage_report(annotations,sources,metadata)
    print(json.dumps(report,indent=2,sort_keys=True))
    if args.json_out: Path(args.json_out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    raise SystemExit(0 if prelabel_pass else 2)
if __name__=="__main__": main()
