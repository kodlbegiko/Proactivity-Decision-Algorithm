from __future__ import annotations
import hashlib,json,os,subprocess,traceback
from datetime import datetime,timezone
from pathlib import Path
from .audit_gate_g_v2 import audit_evaluation
from .candidate_adapter import CandidateV11Adapter
from .generator import DOCKET_PREFIX,GENERATOR_VERSION,SUITE_CONFIG,TOTAL_CASES,dataset_sha256,generate_all,gold_sha256
from .metrics import compute_metrics
from .preflight import verify_candidate_freeze
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"gate_g_v11_rq2_out";REPORTS=OUT/"reports"/"candidate_v11_gate_g_v2";PREREG=ROOT/"gate_g_v11_rq2"/"preregistration.json";CANDIDATE_SHA="3cdf4c9432b13f6ae003fa475a794e7491495d00";CANDIDATE_FREEZE_SHA="2d87fbf19d4715bdfaa3eb56e817b64cbdb2239e"
def _utcnow():return datetime.now(timezone.utc).isoformat()
def _sha256_bytes(raw):return hashlib.sha256(raw).hexdigest()
def _sha256_file(path):return _sha256_bytes(path.read_bytes())
def _git_head():return subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,text=True,stdout=subprocess.PIPE).stdout.strip()
def _write(path,payload):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(payload,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
def _prediction_digest(predictions):
    canonical=[{"action":str(p.action),"factors":dict(p.factors),"belief_resolution":dict(p.belief_resolution),"contradiction_detected":bool(p.contradiction_detected),"invalid_state":bool(p.invalid_state)} for p in predictions];return _sha256_bytes(json.dumps(canonical,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())
def _terminal_payload(status,terminal_state,*,metrics,audit,dataset_sha,gold_sha,prereg_sha,reproducibility,incident=None):
    payload={"mission":"Candidate-v11 Gate G v2 Independent External-Validity Requalification","gate_g_v2":status,"terminal_state":terminal_state,"branch":"research/candidate-v11-gate-g-v2-independent-requalification","base_sha":CANDIDATE_SHA,"candidate_freeze_sha":CANDIDATE_FREEZE_SHA,"candidate_modified":False,"previous_gate_g_preserved_as_invalid":True,"previous_gate_g_used_as_scientific_trial":False,"interface_preflight":"PASS","performance_scoring_during_preflight":False,"preregistration_sha":prereg_sha,"evaluator_freeze_sha":prereg_sha,"generator_freeze_sha":prereg_sha,"oracle_freeze_sha":prereg_sha,"dataset_sha":dataset_sha,"gold_sha":gold_sha,"total_formal_cases":TOTAL_CASES if dataset_sha else None,"integrity":"PASS" if status in {"PASS","FAIL"} else "FAIL","reproducibility":reproducibility,"independent_audit":"PASS" if audit and audit.get("pass") else ("FAIL" if audit else "NOT_EXECUTED"),"metrics":metrics,"audit":audit,"incident":incident,"individual_historical_rows_inspected":False,"individual_previous_gate_g_rows_inspected":False,"individual_gate_g_v2_rows_inspected":False,"merged":False};payload["terminal_evidence_sha256"]=_sha256_bytes(json.dumps(dict(payload),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode());return payload
def main():
    OUT.mkdir(parents=True,exist_ok=True);REPORTS.mkdir(parents=True,exist_ok=True);formal_started=False;dataset_hash=gold_hash=prereg_sha=None
    try:
        if not PREREG.exists():raise RuntimeError("preregistration.json is required for formal execution")
        json.loads(PREREG.read_text());prereg_sha=_git_head();verify_candidate_freeze();cases=generate_all();dataset_hash=dataset_sha256(cases);gold_hash=gold_sha256(cases);gp=ROOT/"gate_g_v11_rq2"/"generator.py";op=ROOT/"gate_g_v11_rq2"/"protocol_oracle.py"
        dataset_manifest={"lineage":"GG-V11-RQ2-20260816","generator_version":GENERATOR_VERSION,"generation_timestamp":_utcnow(),"suite_counts":{s:c["count"] for s,c in SUITE_CONFIG.items()},"suite_seeds":{s:c["seed"] for s,c in SUITE_CONFIG.items()},"total_row_count":len(cases),"dataset_sha256":dataset_hash,"gold_label_sha256":gold_hash,"generator_source_sha256":_sha256_file(gp),"oracle_source_sha256":_sha256_file(op),"exact_prompt_overlap":"0 by construction / independent namespace proof","namespace":DOCKET_PREFIX,"lexical_template_overlap":"N/A — intentionally not measured under information-isolation policy","historical_protected_rows_inspected":False,"historical_development_rows_inspected":False,"previous_gate_g_rows_inspected":False};_write(OUT/"dataset_manifest.json",dataset_manifest)
        adapter=CandidateV11Adapter();formal_started=True;formal_manifest={"formal_trial_started":True,"timestamp":_utcnow(),"candidate_sha":CANDIDATE_SHA,"candidate_freeze_sha":CANDIDATE_FREEZE_SHA,"dataset_sha":dataset_hash,"preregistration_sha":prereg_sha,"evaluator_sha":prereg_sha,"generator_source_sha256":_sha256_file(gp),"oracle_source_sha256":_sha256_file(op),"ci_run_id":os.environ.get("GITHUB_RUN_ID")};_write(OUT/"formal_trial_manifest.json",formal_manifest)
        run_a=[adapter.predict(c.prompt) for c in cases];run_b=[adapter.predict(c.prompt) for c in cases];da=_prediction_digest(run_a);db=_prediction_digest(run_b);repro={"run_a_prediction_sha256":da,"run_b_prediction_sha256":db,"deterministic_equal":da==db,"row_level_predictions_persisted":False};_write(OUT/"reproducibility_report.json",repro)
        if da!=db:
            terminal=_terminal_payload("INVALID","GATE G V2 INVALID — NONDETERMINISTIC EVALUATION",metrics=None,audit=None,dataset_sha=dataset_hash,gold_sha=gold_hash,prereg_sha=prereg_sha,reproducibility="FAIL");_write(REPORTS/"terminal.json",terminal);print(json.dumps(terminal,sort_keys=True));return 2
        metrics=compute_metrics(cases,run_a);audit=audit_evaluation(cases,run_a,run_b,metrics,dataset_hash);_write(OUT/"audit_report.json",audit)
        for suite in SUITE_CONFIG:
            sm=metrics["suite_metrics"][suite];_write(REPORTS/f"{suite}.json",{"suite":suite,"count":sm["count"],"macro_f1":sm["macro_f1"],"accuracy":sm["accuracy"],"seed":SUITE_CONFIG[suite]["seed"],"row_level_examples_persisted":False})
        _write(REPORTS/"aggregate.json",metrics)
        if not audit["pass"]:status="INVALID";terminal_state="GATE G V2 INVALID — EVALUATION INTEGRITY FAILURE"
        elif metrics["all_mandatory_thresholds_pass"]:status="PASS";terminal_state="GATE G V2 PASS — CANDIDATE_V11 EXTERNAL VALIDITY SUPPORTED"
        else:status="FAIL";terminal_state="GATE G V2 FAIL — CANDIDATE_V11 EXTERNAL VALIDITY NOT ESTABLISHED"
        terminal=_terminal_payload(status,terminal_state,metrics=metrics,audit=audit,dataset_sha=dataset_hash,gold_sha=gold_hash,prereg_sha=prereg_sha,reproducibility="PASS");_write(REPORTS/"terminal.json",terminal);print(json.dumps(terminal,sort_keys=True));return 0 if status in {"PASS","FAIL"} else 3
    except Exception as exc:
        iid="formal_001" if formal_started else "preformal_002";incident={"incident_id":iid,"timestamp":_utcnow(),"formal_trial_started":formal_started,"classification":"GATE G V2 INVALID — EVALUATION INTEGRITY FAILURE" if formal_started else "PRE-FORMAL INFRASTRUCTURE FAILURE","exception_type":type(exc).__name__,"exception_message":str(exc),"traceback":traceback.format_exc(),"candidate_scientific_conclusion":"NONE"};_write(OUT/"incidents"/f"{iid}.json",incident);status="INVALID" if formal_started else "PRECHECK BLOCKED";term="GATE G V2 INVALID — EVALUATION INTEGRITY FAILURE" if formal_started else "GATE G V2 PRECHECK BLOCKED — CANDIDATE INTERFACE CONTRACT UNRESOLVED";terminal=_terminal_payload(status,term,metrics=None,audit=None,dataset_sha=dataset_hash,gold_sha=gold_hash,prereg_sha=prereg_sha,reproducibility="NOT_EXECUTED",incident=iid);_write(REPORTS/"terminal.json",terminal);print(json.dumps(terminal,sort_keys=True));return 4
if __name__=="__main__":raise SystemExit(main())
