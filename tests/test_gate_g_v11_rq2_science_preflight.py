from __future__ import annotations
import inspect
from collections import Counter
from gate_g_v11_rq2 import generator as generator_module
from gate_g_v11_rq2 import protocol_oracle as oracle_module
from gate_g_v11_rq2.audit_gate_g_v2 import audit_evaluation
from gate_g_v11_rq2.candidate_adapter import CanonicalPrediction,EXPECTED_PUBLIC_FIELDS
from gate_g_v11_rq2.generator import SUITE_CONFIG,TOTAL_CASES,dataset_sha256,generate_all,generate_suite
from gate_g_v11_rq2.metrics import ACTIONS,THRESHOLDS,compute_metrics
from gate_g_v11_rq2.protocol_oracle import FACTOR_NAMES,decide

def test_fresh_generator_is_deterministic_and_total_is_exact():
    first=generate_all();second=generate_all();assert len(first)==TOTAL_CASES==13540;assert dataset_sha256(first)==dataset_sha256(second);assert [c.prompt for c in first]==[c.prompt for c in second]
def test_suite_counts_and_seeds_are_frozen():
    expected={"G1":(1200,82101),"G2":(800,82102),"G3":(800,82103),"G4":(1000,82104),"G5":(800,82105),"G6":(840,82106),"G7":(600,82107),"G8":(700,82108),"G9":(700,82109),"G10":(700,82110),"G11":(600,82111),"G12":(700,82112),"G13":(500,82113),"G14":(1200,82114),"G15":(1200,82115),"G16":(1200,82116)};assert {k:(v["count"],v["seed"]) for k,v in SUITE_CONFIG.items()}==expected
def test_g6_has_required_contradiction_and_control_composition():
    cases=generate_suite("G6");assert sum(c.metadata["contradiction_case"] is True for c in cases)==700;assert sum(c.metadata["contradiction_case"] is False for c in cases)==140
def test_g14_has_600_pairs_and_each_pair_changes_one_gold_factor():
    cases=generate_suite("G14");by_pair={}
    for c in cases:by_pair.setdefault(c.metadata["pair_id"],{})[c.metadata["pair_member"]]=c
    assert len(by_pair)==600
    for pair in by_pair.values():
        b=pair["baseline"];cf=pair["counterfactual"];diffs=[f for f in FACTOR_NAMES if b.gold_state[f]!=cf.gold_state[f]];assert diffs==[b.metadata["changed_factor"]];assert b.gold_action=="ACT";assert cf.gold_action!="ACT"
def test_g16_is_exactly_action_balanced():assert Counter(c.gold_action for c in generate_suite("G16"))==Counter({a:200 for a in ACTIONS})
def test_gold_oracle_and_generator_are_candidate_independent_by_import_boundary():
    gs=inspect.getsource(generator_module).lower();osrc=inspect.getsource(oracle_module).lower();assert "from candidate_v11" not in gs;assert "import candidate_v11" not in gs;assert "benchmark_v11.generator" not in gs;assert "from candidate_v11" not in osrc;assert "import candidate_v11" not in osrc
def test_acceptance_thresholds_are_exactly_frozen():
    expected={"overall_macro_f1":(">=",0.94),"overall_accuracy":(">=",0.95),"exact_structured_state_accuracy":(">=",0.90),"mean_factor_accuracy":(">=",0.97),"critical_factor_accuracy":(">=",0.95),"state_validity":(">=",0.999),"invalid_states":("==",0),"act_precision":(">=",0.995),"act_recall":(">=",0.95),"forbidden_act":("==",0),"false_act":("==",0),"contradiction_detection":(">=",0.95),"contradiction_false_certainty":("<=",0.01),"false_contradiction":("<=",0.02),"latest_valid_evidence_accuracy":(">=",0.95),"obsolete_evidence_suppression":(">=",0.95),"scope_accuracy":(">=",0.95),"cross_scope_contamination":("<=",0.02),"uncertainty_false_certainty":("<=",0.01),"counterfactual_directional":(">=",0.97),"counterfactual_act_disable":(">=",0.99),"counterfactual_exact_pair":(">=",0.94),"max_action_share":("<=",0.35),"per_suite_macro_f1":(">=",0.90)};assert THRESHOLDS==expected
def _perfect_prediction(case):return CanonicalPrediction(action=case.gold_action,factors=dict(case.gold_state),belief_resolution={f:"supported" for f in FACTOR_NAMES},contradiction_detected=(case.gold_state["information"]=="contradictory"),invalid_state=False,public_field_names=EXPECTED_PUBLIC_FIELDS)
def test_mock_perfect_predictions_exercise_evaluator_and_independent_auditor():
    cases=generate_all();pred=[_perfect_prediction(c) for c in cases];metrics=compute_metrics(cases,pred);assert metrics["all_mandatory_thresholds_pass"] is True;assert audit_evaluation(cases,pred,pred,metrics,dataset_sha256(cases))["pass"] is True
def test_oracle_returns_valid_action_for_every_generated_gold_state():
    for suite in SUITE_CONFIG:
        for c in generate_suite(suite):
            o=decide(c.gold_state);assert o.invalid is False;assert o.action==c.gold_action
