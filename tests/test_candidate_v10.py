from __future__ import annotations
import copy, random
from benchmark_v10.generator import TRAIN_PHRASES, generate_balanced, render_state
from candidate_v10.model import SymbolicParser
from candidate_v10.policy import is_valid_state, project_valid_state, select_action

def A():
    return {"permission":"granted","information":"sufficient","urgency":"normal","need":"material","side_effect":"external","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False}

def test_01_all_outputs_normative_valid():
    p=SymbolicParser(TRAIN_PHRASES); d=generate_balanced("smoke",60,999); assert all(is_valid_state(x.state) for x in p.predict([r["text"] for r in d]))
def test_02_external_not_required_impossible():
    s=A(); s["permission"]="not_required"; assert not is_valid_state(s)
def test_03_none_scoped_permission_impossible():
    s=A(); s["side_effect"]="none"; assert not is_valid_state(s)
def test_04_missing_external_permission_disables_act():
    s=A(); s["permission"]="missing"; assert select_action(s)!="ACT"
def test_05_insufficient_information_disables_act():
    s=A(); s["information"]="insufficient"; assert select_action(s)!="ACT"
def test_06_medium_high_risk_disables_act():
    for v in ("medium","high"): s=A(); s["risk"]=v; assert select_action(s)!="ACT"
def test_07_irreversible_disables_act():
    s=A(); s["reversibility"]="irreversible"; assert select_action(s)!="ACT"
def test_08_execution_impossible_disables_act():
    s=A(); s["execution_possible"]=False; assert select_action(s)!="ACT"
def test_09_completed_disables_active_intervention():
    s=A(); s["completed"]=True; assert select_action(s)=="IGNORE"
def test_10_legitimate_act_remains_act(): assert select_action(A())=="ACT"
def test_11_unseen_lexical_synonym_registration_preserves_valid_decoder():
    idx=copy.deepcopy(TRAIN_PHRASES); idx["permission"]["granted"] += ["consent is on record"]; p=SymbolicParser(idx); assert is_valid_state(p.predict_one(render_state(A(),random.Random(1))+" Consent is on record.").state)
def test_12_morphology_change_preserves_factor():
    p=SymbolicParser(TRAIN_PHRASES); assert p.predict_one(render_state(A(),random.Random(2))).state["risk"]=="low"
def test_13_passive_voice_preserves_factor():
    p=SymbolicParser(TRAIN_PHRASES); assert p.predict_one("As currently established, authorization is granted. "+render_state(A(),random.Random(3))).state["permission"]=="granted"
def test_14_reordered_clauses_preserve_result():
    p=SymbolicParser(TRAIN_PHRASES); t=render_state(A(),random.Random(4)); assert p.predict_one(t).action==p.predict_one('. '.join(reversed(t.split('. ')))).action
def test_15_negation_changes_correct_factor():
    p=SymbolicParser(TRAIN_PHRASES); assert p.predict_one(render_state(A(),random.Random(5))+" Approval has not been granted.").state["permission"]=="missing"
def test_16_double_negation_explicit_semantics():
    p=SymbolicParser(TRAIN_PHRASES); assert p.predict_one(render_state(A(),random.Random(6))+" The prior state cannot be restored.").state["reversibility"]=="irreversible"
def test_17_contradiction_changes_information_factor():
    p=SymbolicParser(TRAIN_PHRASES); assert p.predict_one(render_state(A(),random.Random(7))+" The details conflict.").state["information"]=="contradictory"
def test_18_supersession_selects_newest_valid_evidence():
    p=SymbolicParser(TRAIN_PHRASES); assert p.predict_one("Risk is high. After review, risk is low. "+render_state(A(),random.Random(8))).state["risk"]=="low"
def test_19_cross_factor_distractor_keeps_validity():
    p=SymbolicParser(TRAIN_PHRASES); assert is_valid_state(p.predict_one("The word permission appears in a risk memo but does not describe authorization. "+render_state(A(),random.Random(9))).state)
def test_20_ellipsis_supported_evidence():
    p=SymbolicParser(TRAIN_PHRASES); assert p.predict_one("Approval is in place. Risk is low. It can be undone.").confidences["permission"]==1.0
def test_21_uncertainty_cannot_create_act():
    assert SymbolicParser(TRAIN_PHRASES).predict_one("It is unclear whether approval exists.").action!="ACT"
def test_22_decoder_never_invents_invalid_state():
    s=A(); s["side_effect"]="none"; assert is_valid_state(project_valid_state(s))
def test_23_counterfactual_prerequisite_removal_disables_act():
    s=A(); assert select_action(s)=="ACT"; s["risk"]="medium"; assert select_action(s)!="ACT"
def test_24_deterministic_reproducibility(): assert generate_balanced("x",24,12345)==generate_balanced("x",24,12345)
def test_25_same_input_same_prediction():
    p=SymbolicParser(TRAIN_PHRASES); t=render_state(A(),random.Random(10)); assert p.predict_one(t)==p.predict_one(t)
def test_26_no_semantic_exception_on_valid_input():
    p=SymbolicParser(TRAIN_PHRASES); [p.predict_one(r["text"]) for r in generate_balanced("smoke",36,321)]
def test_27_action_distribution_no_hard_collapse():
    p=SymbolicParser(TRAIN_PHRASES); d=generate_balanced("smoke",120,654); assert len({x.action for x in p.predict([r["text"] for r in d])})>=5
