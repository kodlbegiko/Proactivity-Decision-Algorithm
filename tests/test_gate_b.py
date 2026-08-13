import csv, json, subprocess, sys
from pathlib import Path
import pytest
from proactivity.evaluation.annotations import PACKET_FIELDS, archive_raw_annotations, parse_annotation_row, validate_completed_annotations
from proactivity.evaluation.metrics import evaluate_policy
from proactivity.projections import DERIVED_FIELDS, raw_context_projection, structured_state_projection
from proactivity.schema import Scenario
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data/development/development_v1.jsonl"; META=ROOT/"data/development/development_v1.meta.jsonl"
def rows(): return [json.loads(x) for x in DATA.read_text().splitlines() if x.strip()]
def test_development_v1_invariants():
    rs=rows(); assert len(rs)==144 and len({x["scenario_id"] for x in rs})==144
    counts={d:sum(x["domain"]==d for x in rs) for d in {x["domain"] for x in rs}}; assert set(counts.values())=={24}; assert all("raw_context" in x for x in rs); assert all(not any(k in x for k in ["expected_label","gold_action","correct_decision","design_intent","pair_id","sequence_id"]) for x in rs)
def test_counterfactual_and_sequence_metadata_are_separate():
    ms=[json.loads(x) for x in META.read_text().splitlines() if x.strip()]; pair_ids={x["pair_id"] for x in ms if x.get("pair_id")}; seq_ids={x["sequence_id"] for x in ms if x.get("sequence_id")}; assert len(pair_ids)==24 and len(seq_ids)==6; assert sum(bool(x.get("pair_id")) for x in ms)==48; assert sum(bool(x.get("sequence_id")) for x in ms)==24
def test_raw_projection_hides_researcher_derived_scores():
    s=Scenario.from_dict(rows()[0]); raw=raw_context_projection(s); structured=structured_state_projection(s); text=json.dumps(raw); assert not any(f'"{k}"' in text for k in DERIVED_FIELDS); assert "event" in structured and "expected_delay_cost" in structured
def test_annotation_parser_rejects_impossible_set():
    good={"scenario_id":"s","preferred_action":"WAIT","acceptable_actions":"WAIT|SUGGEST","confidence":"4","ambiguity_flag":"true","reason_code":"timing","criticality":"NONE"}; assert parse_annotation_row(good).preferred_action.value=="WAIT"; bad=dict(good); bad["acceptable_actions"]="SUGGEST"
    with pytest.raises(ValueError): parse_annotation_row(bad)
def test_metric_operationalization_on_toy_annotations():
    a1=parse_annotation_row({"scenario_id":"a","preferred_action":"WAIT","acceptable_actions":"WAIT","confidence":"5","ambiguity_flag":"false","reason_code":"timing","criticality":"NONE"}); a2=parse_annotation_row({"scenario_id":"b","preferred_action":"ASK","acceptable_actions":"ASK","confidence":"5","ambiguity_flag":"false","reason_code":"permission","criticality":"CRITICAL"}); m=evaluate_policy([a1,a2],{"a":"NOTIFY","b":"ACT"}); assert m["false_interruption_rate"]==1.0; assert m["premature_intervention_rate"]==1.0; assert m["unsafe_autonomy_rate"]==1.0
def test_leakage_audit_executes_and_passes_preannotation():
    cp=subprocess.run([sys.executable,str(ROOT/"scripts/audit_development_v1.py"),str(DATA),str(META)],capture_output=True,text=True); assert cp.returncode==0,cp.stdout+cp.stderr; report=json.loads(cp.stdout); assert report["pre_annotation_leakage_gate"]=="PASS"; assert report["label_dependent_lexical_audit"]=="NOT_EXECUTED_NO_INDEPENDENT_LABELS"
def _write_packet(path, completed=False, mutate=False):
    source_rows=[]
    for i in range(2):
        source_rows.append({"scenario_id":f"synthetic-{i}","domain":"study","timestamp":f"2026-08-13T0{i}:00:00Z","scenario_context":f"SYNTHETIC_TEST_ONLY context {i}","preferred_action":"WAIT" if completed else "","acceptable_actions":"WAIT" if completed else "","confidence":"5" if completed else "","ambiguity_flag":"false" if completed else "","reason_code":"timing" if completed else "","criticality":"NONE" if completed else "","rationale":"SYNTHETIC_TEST_ONLY" if completed else ""})
    if mutate: source_rows[0]["scenario_context"]+=" MUTATED"
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=PACKET_FIELDS); w.writeheader(); w.writerows(source_rows)
def test_completed_annotation_validation_fails_closed_on_source_mutation(tmp_path):
    blank=tmp_path/"blank.csv"; done=tmp_path/"done.csv"; bad=tmp_path/"bad.csv"; _write_packet(blank); _write_packet(done,completed=True); _write_packet(bad,completed=True,mutate=True)
    assert validate_completed_annotations(done,blank,expected_count=2)["validation"]=="PASS"
    with pytest.raises(ValueError,match="SOURCE_CONTEXT_MODIFIED"): validate_completed_annotations(bad,blank,expected_count=2)
def test_raw_archive_is_immutable(tmp_path):
    pa=tmp_path/"pa.csv"; pb=tmp_path/"pb.csv"; a=tmp_path/"a.csv"; b=tmp_path/"b.csv"; _write_packet(pa); _write_packet(pb); _write_packet(a,completed=True); _write_packet(b,completed=True); out=tmp_path/"raw"
    manifest=archive_raw_annotations(a,b,pa,pb,out); assert manifest["annotator_a"]["scenario_count"]==2; assert (out/"SHA256SUMS").exists()
    with pytest.raises(FileExistsError): archive_raw_annotations(a,b,pa,pb,out)
