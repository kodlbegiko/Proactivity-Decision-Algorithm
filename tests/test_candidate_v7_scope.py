from proactivity.candidate_v7 import predict


def test_contrast_scope_keeps_permission_and_execution_separate():
    text = (
        "Permission is granted, but execution is not possible. "
        "Information is sufficient. Urgency is normal. A material intervention is needed. "
        "The side effect is external. Risk is low. The action is reversible. "
        "Deferral is unavailable. Clarification is possible. "
        "The matter is not acknowledged. The task is not completed."
    )
    result = predict(text, "V7A-01")
    assert result["state"]["permission"] == "granted"
    assert result["state"]["execution_possible"] is False
    assert result["action"] != "ACT"


def test_opposite_contrast_reconstructs_different_state():
    text = (
        "Permission is missing, but execution is possible. "
        "Information is sufficient. Urgency is normal. A material intervention is needed. "
        "The side effect is external. Risk is low. The action is reversible. "
        "Deferral is unavailable. Clarification is possible. "
        "The matter is not acknowledged. The task is not completed."
    )
    result = predict(text, "V7A-01")
    assert result["state"]["permission"] == "missing"
    assert result["state"]["execution_possible"] is True
    assert result["action"] == "ASK"
