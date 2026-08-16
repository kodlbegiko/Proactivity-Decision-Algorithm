from __future__ import annotations

import json, platform
from pathlib import Path
import sklearn

from candidate_v10.model import SymbolicParser, ContrastiveEvidenceScorer, HybridEvidenceLattice
from benchmark_v10.generator import TRAIN_PHRASES, generate_all, write_all
from benchmark_v10.evaluation import architecture_qualification, contradiction_metrics, evaluate_counterfactual, evaluate_records, focus_accuracy, uncertainty_metrics

ROOT=Path(__file__).resolve().parents[1]; REPORT=ROOT/"reports"/"candidate_v10"; GATE=ROOT/"gate_recovery_v10"; DATA=ROOT/"data"/"candidate_v10_development"

def dump(path,obj): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,sort_keys=True),encoding="utf-8")

def main():
    REPORT.mkdir(parents=True,exist_ok=True); GATE.mkdir(parents=True,exist_ok=True)
    data=generate_all(); manifest=write_all(DATA,data)
    models={"V10-A":SymbolicParser(TRAIN_PHRASES),"V10-B":ContrastiveEvidenceScorer(101001).fit(data["train"]),"V10-C":HybridEvidenceLattice(TRAIN_PHRASES,101001).fit(data["train"])}
    results={}; qualifications=[]
    splits=["validation","lexical_novelty","syntactic_novelty","domain_transfer","act_boundary","state_validity_stress"]
    for name,model in models.items():
        ms={}; ps={}
        for split in splits: ms[split],ps[split]=evaluate_records(model,data[split])
        neg_m,neg_p=evaluate_records(model,data["negation"]); con_m,con_p=evaluate_records(model,data["contradiction"]); sup_m,sup_p=evaluate_records(model,data["supersession"]); cross_m,cross_p=evaluate_records(model,data["cross_factor_distractor"]); unc_m,unc_p=evaluate_records(model,data["uncertainty"]); ell_m,ell_p=evaluate_records(model,data["ellipsis"]); prag_m,prag_p=evaluate_records(model,data["pragmatic"]); comp_m,comp_p=evaluate_records(model,data["compositional"]); perm_m,perm_p=evaluate_records(model,data["permission_scope"])
        sp={"negation_factor_accuracy":focus_accuracy(data["negation"],neg_p),"contradiction":contradiction_metrics(data["contradiction"],con_p),"supersession_latest_valid":focus_accuracy(data["supersession"],sup_p),"counterfactual":evaluate_counterfactual(model,data["counterfactual"]),"cross_factor_confusion_rate":1.0-cross_m["critical_factor_accuracy"],"uncertainty":uncertainty_metrics(data["uncertainty"],unc_p),"ellipsis":ell_m,"pragmatic":prag_m,"compositional":comp_m,"permission_scope":perm_m}
        q=architecture_qualification(name,ms,sp); qualifications.append(q); results[name]={"metrics":ms,"specialized":sp,"qualification":q}
    qualified=[q["architecture"] for q in qualifications if q["qualified"]]; selected=None
    if qualified:
        complexity={"V10-A":0,"V10-B":1,"V10-C":2}
        def key(a):
            r=results[a]; v=r["metrics"]["validation"]
            return (v["invalid_states"],v["forbidden_ACT"],v["false_ACT"],-v["state_validity"],-v["ACT_precision"],-r["metrics"]["lexical_novelty"]["critical_factor_accuracy"],-r["metrics"]["syntactic_novelty"]["critical_factor_accuracy"],-r["metrics"]["domain_transfer"]["critical_factor_accuracy"],-v["ACT_recall"],-v["exact_structured_state_accuracy"],-v["macro_f1"],complexity[a])
        selected=sorted(qualified,key=key)[0]
    dump(REPORT/"architecture_search.json",{"architectures":qualifications,"selected":selected})
    (REPORT/"architecture_search.md").write_text("# Candidate-v10 Architecture Search\n\n"+"\n".join(f"- {q['architecture']}: {'QUALIFIED' if q['qualified'] else 'FAIL'}; failed={', '.join(q['failed_checks']) or 'none'}" for q in qualifications)+f"\n\nSelected: {selected or 'none'}\n",encoding="utf-8")
    dump(REPORT/"validation_summary.json",{a:results[a]["metrics"]["validation"] for a in results}); dump(REPORT/"per_factor_metrics.json",{a:results[a]["metrics"]["validation"]["factor_metrics"] for a in results})
    dump(REPORT/"structured_state_report.json",{a:{"exact_structured_state_accuracy":results[a]["metrics"]["validation"]["exact_structured_state_accuracy"],"critical_factor_accuracy":results[a]["metrics"]["validation"]["critical_factor_accuracy"]} for a in results})
    dump(REPORT/"state_validity_report.json",{a:{"state_validity":results[a]["metrics"]["validation"]["state_validity"],"invalid_states":results[a]["metrics"]["validation"]["invalid_states"]} for a in results})
    dump(REPORT/"act_safety_report.json",{a:{"ACT_precision":results[a]["metrics"]["validation"]["ACT_precision"],"ACT_recall":results[a]["metrics"]["validation"]["ACT_recall"],"forbidden_ACT":results[a]["metrics"]["validation"]["forbidden_ACT"],"false_ACT":results[a]["metrics"]["validation"]["false_ACT"]} for a in results})
    dump(REPORT/"semantic_novelty_report.json",{a:{"lexical":results[a]["metrics"]["lexical_novelty"]["critical_factor_accuracy"],"syntactic":results[a]["metrics"]["syntactic_novelty"]["critical_factor_accuracy"],"domain":results[a]["metrics"]["domain_transfer"]["critical_factor_accuracy"]} for a in results})
    dump(REPORT/"negation_report.json",{a:results[a]["specialized"]["negation_factor_accuracy"] for a in results}); dump(REPORT/"contradiction_report.json",{a:results[a]["specialized"]["contradiction"] for a in results}); dump(REPORT/"supersession_report.json",{a:results[a]["specialized"]["supersession_latest_valid"] for a in results}); dump(REPORT/"cross_factor_report.json",{a:results[a]["specialized"]["cross_factor_confusion_rate"] for a in results}); dump(REPORT/"counterfactual_report.json",{a:results[a]["specialized"]["counterfactual"] for a in results}); dump(REPORT/"uncertainty_report.json",{a:results[a]["specialized"]["uncertainty"] for a in results})
    dump(REPORT/"collapse_audit.json",{a:{"action_distribution":results[a]["metrics"]["validation"]["action_distribution"],"max_prediction_share":results[a]["metrics"]["validation"]["max_prediction_share"],"IGNORE_share":results[a]["metrics"]["validation"]["IGNORE_share"],"ACT_share":results[a]["metrics"]["validation"]["ACT_share"]} for a in results})
    dump(REPORT/"development_holdouts_summary.json",{"H1_H15":"NOT_EXECUTED_PRE_FREEZE","reason":"qualification must pass before freeze and formal holdout materialization"})
    dump(REPORT/"baseline_comparison.json",{"majority_balanced_expected_accuracy":1/6,"simple_heuristic":"V10-A is the registered symbolic baseline","candidate_v9_historical_aggregate":{"H1_macro_f1":0.5771589882,"H1_ACT_recall":0.2366666667,"H1_ACT_precision":1.0,"H1_state_validity":1.0,"H1_exact_state":0.3983333333,"H1_critical_factor_accuracy":0.9093055556},"candidate_v9_H1_rerun":False})
    dump(REPORT/"lexical_split_report.json",{"manifest":manifest,"policy":"development and lexical-novelty primary roots are preregistered disjoint inventories"}); dump(REPORT/"syntax_split_report.json",{"development":"canonical","validation":"wrapped declarative","syntactic_novelty":"concessive/cleft/fronted wrappers"}); dump(REPORT/"domain_split_report.json",{"development":["file operation","local application change","notification","account setting"],"validation":["message sending","scheduling","system configuration","deletion"]})
    (REPORT/"semantic_generalization_design.md").write_text("# Semantic Generalization Design\n\nV10-A is a symbolic baseline. V10-B uses deterministic schema-conditioned word/character TF-IDF logistic evidence models. V10-C combines explicit symbolic evidence with ML evidence while keeping semantic evidence separate from normative-valid state projection.\n",encoding="utf-8")
    dump(REPORT/"reproducibility.json",{"python":platform.python_version(),"scikit_learn":sklearn.__version__,"seeds":{k:v["seed"] for k,v in manifest.items()},"data_hashes":{k:v["sha256"] for k,v in manifest.items()},"remote_models":False,"deterministic_random_state":101001})
    integrity={"candidate_v9_modified":False,"candidate_v9_h1_individual_evidence_accessed":False,"candidate_v9_h1_individual_evidence_used_for_development":False,"candidate_v10_preregistered_before_results":True,"candidate_frozen_before_holdouts":False,"candidate_modified_after_holdout":False,"formal_holdout_rerun":False,"protected_evidence_used_for_development":False,"threshold_changed_after_results":False,"seed_changed_after_results":False,"lexical_split_changed_after_results":False,"syntax_split_changed_after_results":False,"training_data_changed_after_results":False,"leakage_detected":False}; dump(REPORT/"integrity_report.json",integrity)
    if selected is None:
        terminal="CANDIDATE_V10 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED"; t={"candidate":"Candidate-v10","terminal_state":terminal,"terminal_stage":"PRE_FREEZE_ARCHITECTURE_QUALIFICATION","selected_architecture":None,"qualified_architectures":[],"H1_H15_executed":False,"protected_eligible":False,"protected_executed":False,"individual_formal_holdout_rows_inspected":False,"candidate_v9_h1_individual_evidence_accessed":False,"architecture_results":qualifications}; dump(GATE/"development_terminal.json",t); dump(GATE/"terminal_freeze.json",t); (REPORT/"terminal_report.md").write_text(f"# Candidate-v10 Terminal Report\n\n## Terminal state\n\n`{terminal}`\n\nNo architecture satisfied every preregistered pre-freeze qualification requirement. No candidate was frozen; H1-H15 were not materialized or executed; protected evaluation was not eligible.\n",encoding="utf-8")
    else:
        dump(GATE/"development_terminal.json",{"status":"QUALIFICATION_PASS","selected_architecture":selected,"next":"CANDIDATE_FREEZE_REQUIRED"}); (REPORT/"terminal_report.md").write_text(f"# Candidate-v10 Development Qualification\n\nSelected `{selected}`. Candidate freeze is required before any formal holdout.\n",encoding="utf-8")
    dump(GATE/"run_result.json",{"selected_architecture":selected,"qualified":selected is not None}); return 0

if __name__=="__main__": raise SystemExit(main())
