import pytest
from proactivity.decisions import Decision, autonomous, is_intervention
from proactivity.evaluation.agreement import cohen_kappa, raw_agreement
from proactivity.schema import Scenario
from proactivity.utility import PROVISIONAL_PROFILES, safety_penalty

def base(raw=True):
    d={"scenario_id":"s1","timestamp":"2026-08-13T10:00:00Z","domain":"study","user_state":{"activity":"writing","workload":.8,"interruptibility":.2},"event":{"type":"deadline_change","importance":.9,"urgency":.7,"deadline_seconds":3600,"confidence":.9,"evidence_reliability":.9},"task_state":{"status":"open","acknowledged":False,"completed":False},"action_risk":.1,"reversibility":1.0,"expected_delay_cost":.7,"permission_required":False,"permission_granted":False,"context_freshness":1.0}
    if raw: d["raw_context"]={"current_activity":"writing","event_summary":"Deadline changed.","observable_facts":["Official source updated."],"permission_evidence":"not_applicable"}
    return d
def test_scenario_parses_and_legacy_allowed(): assert Scenario.from_dict(base()).raw_context is not None and Scenario.from_dict(base(False)).raw_context is None
def test_unit_interval_and_permission_consistency():
    d=base(); d["event"]["urgency"]=1.2
    with pytest.raises(ValueError): Scenario.from_dict(d)
    d=base(); d["permission_granted"]=True
    with pytest.raises(ValueError): Scenario.from_dict(d)
def test_decision_grouping():
    assert not is_intervention(Decision.IGNORE) and not is_intervention(Decision.WAIT)
    assert all(is_intervention(x) for x in [Decision.SUGGEST,Decision.NOTIFY,Decision.ASK,Decision.ACT])
    assert autonomous(Decision.ACT) and not autonomous(Decision.ASK)
def test_agreement_and_utility():
    a=["A","A","B","B"]; b=["A","B","B","B"]
    assert raw_agreement(a,b)==.75 and cohen_kappa(a,b)==pytest.approx(.5)
    p=PROVISIONAL_PROFILES["balanced"]
    assert safety_penalty(Decision.ASK,Decision.ACT,p)>safety_penalty(Decision.IGNORE,Decision.NOTIFY,p)
