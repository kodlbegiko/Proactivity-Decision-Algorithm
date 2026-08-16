from proactivity.candidate_v7 import CONFIGS, predict


def full_status(permission="granted", information="sufficient", execution="possible"):
    return (
        f"Permission is {permission}. Information is {information}. Urgency is normal. "
        "A material intervention is needed. The side effect is external. Risk is low. "
        "The action is reversible. Deferral is unavailable. "
        f"Execution is {execution}. Clarification is possible. "
        "The matter is not acknowledged. The task is not completed."
    )


def test_search_budget_is_frozen_to_twelve_configs():
    assert len(CONFIGS) == 12
    assert {config.family for config in CONFIGS} == {"V7A", "V7B", "V7C"}


def test_full_proposition_pipeline_reconstructs_safe_act_state():
    result = predict(full_status(), "V7A-01")
    assert result["state"]["permission"] == "granted"
    assert result["state"]["information"] == "sufficient"
    assert result["state"]["risk"] == "low"
    assert result["state"]["execution_possible"] is True
    assert result["action"] == "ACT"
    assert result["forbidden_act"] is False
