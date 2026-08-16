import pytest

from proactivity.schema import Scenario


def base():
    return {
        "scenario_id": "s1",
        "timestamp": "2026-08-13T10:00:00Z",
        "domain": "study",
        "user_state": {"activity": "writing", "workload": 0.8, "interruptibility": 0.2},
        "event": {"type": "deadline_change", "importance": 0.9, "urgency": 0.7, "deadline_seconds": 3600, "confidence": 0.9, "evidence_reliability": 0.9},
        "task_state": {"status": "open", "acknowledged": False, "completed": False},
        "action_risk": 0.1,
        "reversibility": 1.0,
        "expected_delay_cost": 0.7,
        "permission_required": False,
        "permission_granted": False,
        "context_freshness": 1.0,
    }


def test_scenario_parses():
    s = Scenario.from_dict(base())
    s.validate_safety_consistency()
    assert s.scenario_id == "s1"
    assert s.event.urgency == 0.7


def test_unit_interval_enforced():
    data = base()
    data["event"]["urgency"] = 1.2
    with pytest.raises(ValueError):
        Scenario.from_dict(data)


def test_permission_consistency():
    data = base()
    data["permission_granted"] = True
    s = Scenario.from_dict(data)
    with pytest.raises(ValueError):
        s.validate_safety_consistency()
