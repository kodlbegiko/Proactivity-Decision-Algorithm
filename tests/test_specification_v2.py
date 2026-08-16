from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

from proactivity.specification import evaluate, evaluate_record, load_spec
from proactivity.specification.validation import (
    audit_gate_b,
    detect_precedence_cycles,
    gate_b_verdict,
    validate_spec_structure,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec/proactivity_policy_v2.json"
POLICY = load_spec(SPEC)
AUDIT = audit_gate_b(POLICY)


def base(**patch):
    state = {
        "permission": "granted",
        "information": "sufficient",
        "urgency": "none",
        "need": "material",
        "side_effect": "external",
        "risk": "low",
        "reversibility": "reversible",
        "deferral_available": False,
        "execution_possible": True,
        "clarification_possible": True,
        "acknowledged": False,
        "completed": False,
    }
    state.update(patch)
    return state


def test_gate_b_full_exhaustive_passes():
    report = AUDIT
    assert report["gate_verdict"] == "GATE B — PASS"
    assert report["valid_state_combinations"] == 41472
    assert set(report["action_distribution"]) == {"IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT"}


def test_missing_permission_never_acts():
    assert evaluate(base(permission="missing"), spec_path=SPEC).action != "ACT"


def test_contradictory_information_never_acts():
    assert evaluate(base(information="contradictory"), spec_path=SPEC).action != "ACT"


def test_high_risk_never_acts():
    assert evaluate(base(risk="high"), spec_path=SPEC).action != "ACT"


def test_irreversible_never_acts():
    assert evaluate(base(reversibility="irreversible"), spec_path=SPEC).action != "ACT"


def test_invalid_enum_fails_closed():
    assert evaluate(base(risk="extreme"), spec_path=SPEC).status == "INVALID_STATE"


def test_missing_field_fails_closed():
    state = base()
    del state["risk"]
    assert evaluate(state, spec_path=SPEC).status == "INVALID_STATE"


def test_external_not_required_permission_is_invalid():
    assert evaluate(base(permission="not_required"), spec_path=SPEC).status == "INVALID_STATE"


def test_completed_state_is_silent():
    assert evaluate(base(completed=True), spec_path=SPEC).action == "IGNORE"


def test_metadata_and_domain_are_not_oracle_inputs():
    state = base()
    left = evaluate_record({"scenario_id": "A", "domain": "study", "state": state}, spec_path=SPEC)
    right = evaluate_record({"scenario_id": "B", "domain": "travel", "state": state}, spec_path=SPEC)
    assert left.action == right.action == "ACT"


def test_row_order_independence():
    states = [base(), base(permission="missing"), base(risk="high")]
    forward = {json.dumps(state, sort_keys=True): evaluate(state, spec_path=SPEC).action for state in states}
    reverse = {json.dumps(state, sort_keys=True): evaluate(state, spec_path=SPEC).action for state in reversed(states)}
    assert forward == reverse


def test_equal_priority_conflict_fails_closed():
    spec = deepcopy(load_spec(SPEC))
    spec["selection_rules"].append({
        "id": "SYNTHETIC_TEST_ONLY_CONFLICT",
        "priority": 740,
        "action": "ASK",
        "when": {"all": [
            {"field": "side_effect", "op": "eq", "value": "external"},
            {"field": "permission", "op": "eq", "value": "granted"},
            {"field": "information", "op": "eq", "value": "sufficient"},
            {"field": "risk", "op": "eq", "value": "low"},
            {"field": "reversibility", "op": "eq", "value": "reversible"},
            {"field": "execution_possible", "op": "eq", "value": True},
            {"field": "need", "op": "eq", "value": "material"},
        ]},
    })
    assert evaluate(base(), spec=spec).status == "INVALID_SPEC"


def test_precedence_cycle_detected():
    assert detect_precedence_cycles([("A", "B"), ("B", "A")])


def test_precedence_cycle_is_schema_failure():
    spec = deepcopy(load_spec(SPEC))
    spec["precedence_edges"] = [["A", "B"], ["B", "A"]]
    assert "precedence_cycle" in validate_spec_structure(spec)


def test_unreachable_rule_causes_coverage_failure():
    report = deepcopy(AUDIT)
    report["coverage"]["unreachable_matching_rules"] = ["SYNTHETIC_TEST_ONLY"]
    assert gate_b_verdict(report) == "GATE B — FAIL_COVERAGE"


def test_nondeterminism_evidence_fails_gate():
    report = deepcopy(AUDIT)
    report["determinism"]["pass"] = False
    assert gate_b_verdict(report) == "GATE B — FAIL_NONDETERMINISM"


def test_missing_trace_evidence_fails_gate():
    report = deepcopy(AUDIT)
    report["traceability"]["pass"] = False
    assert gate_b_verdict(report) == "GATE B — FAIL_TRACEABILITY"


def test_invalid_state_cannot_silently_act():
    assert evaluate(base(side_effect="none", permission="granted"), spec_path=SPEC).status == "INVALID_STATE"
