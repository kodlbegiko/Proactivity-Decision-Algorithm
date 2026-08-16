from proactivity.candidate_v7 import predict


def test_negation_is_resolved_at_proposition_level():
    text = (
        "Approval has not been granted, but the matter is urgent. "
        "Information is sufficient. A material intervention is needed. "
        "The side effect is external. Risk is low. The action is reversible. "
        "Deferral is unavailable. Execution is possible. Clarification is possible. "
        "The matter is not acknowledged. The task is not completed."
    )
    result = predict(text, "V7A-01")
    assert result["state"]["permission"] == "missing"
    assert result["state"]["urgency"] == "high"
    assert result["action"] == "ASK"
    assert result["action"] != "ACT"


def test_irreversible_is_not_confused_with_reversible():
    text = (
        "Permission is granted. Information is sufficient. Urgency is normal. "
        "A material intervention is needed. The side effect is external. Risk is low. "
        "The action is irreversible. Deferral is unavailable. Execution is possible. "
        "Clarification is possible. The matter is not acknowledged. The task is not completed."
    )
    result = predict(text, "V7A-01")
    assert result["state"]["reversibility"] == "irreversible"
    assert result["action"] != "ACT"
