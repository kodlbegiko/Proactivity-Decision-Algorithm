from proactivity.candidate_v2 import CANDIDATE_FACTORIES, extract_visible_semantic_factors


def test_exact_six_preregistered_candidate_configs():
    assert list(CANDIDATE_FACTORIES) == [
        "C1_balanced_classical_c1",
        "C2_balanced_classical_c4",
        "C3_balanced_linear_margin",
        "C4_semantic_factor_tree",
        "C5_semantic_factor_linear",
        "C6_hybrid_semantic_safety",
    ]


def test_visible_semantic_normalization_examples():
    observation = (
        "Travel context. Authorization is required but absent; important information is missing; "
        "timing pressure is high; current intervention need is material; the modeled side effect is external; "
        "modeled risk is high; the modeled consequence cannot be reversed; a future trigger is defined; "
        "the relevant capability is unavailable; a clarification channel is available; acknowledgement is absent; "
        "completion has not occurred."
    )
    factors = extract_visible_semantic_factors(observation)
    assert factors == {
        "permission": "required_absent",
        "information": "missing",
        "timing": "high",
        "need": "material",
        "side_effect": "external",
        "risk": "high",
        "reversible": "no",
        "deferral": "yes",
        "execution": "no",
        "clarification": "yes",
        "acknowledged": "no",
        "completed": "no",
    }
