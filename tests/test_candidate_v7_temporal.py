from proactivity.candidate_v7 import predict


def test_past_permission_does_not_override_current_permission():
    text = (
        "Previously, permission is granted. As of now, approval is still pending. "
        "Information is sufficient. Urgency is normal. A material intervention is needed. "
        "The side effect is external. Risk is low. The action is reversible. "
        "Deferral is unavailable. Execution is possible. Clarification is possible. "
        "The matter is not acknowledged. The task is not completed."
    )
    result = predict(text, "V7A-01")
    assert result["state"]["permission"] == "missing"
    assert result["action"] == "ASK"


def test_prediction_is_deterministic():
    text = (
        "No approval is required. Information is sufficient. There is no urgency. "
        "No intervention is needed. There is no side effect. Risk is low. "
        "The action is reversible. Deferral is unavailable. Execution is possible. "
        "Clarification is possible. The matter is not acknowledged. The task is not completed."
    )
    assert predict(text, "V7A-01") == predict(text, "V7A-01")
