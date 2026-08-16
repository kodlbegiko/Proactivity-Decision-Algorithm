from proactivity.candidate_v12_final_v2 import final_v2_summary


def test_final_v2_authorization_floors():
    r = final_v2_summary()
    h = r["holdout"]
    u = r["unknown"]
    c = r["counterfactual"]
    i = r["invariance"]
    s = r["stress"]
    m = r["mechanistic"]

    assert r["collision_audit"]["pass"], r["collision_audit"]
    assert h["macro_f1"] >= 0.93
    assert h["exact_latent_state_reconstruction"] >= 0.85
    assert h["mean_factor_accuracy"] >= 0.97
    assert h["act_critical_factor_accuracy"] >= 0.985
    assert h["critical_unknown_rate"] <= 0.03
    assert h["false_unknown_rate"] <= 0.03
    assert u["critical_unknown_rate"] <= 0.03
    assert u["false_unknown_rate"] <= 0.03
    assert u["legitimate_unknown_recall"] >= 0.95
    assert c["exact_pair_correctness"] >= 0.92
    assert i["latent_state_invariance_consistency"] >= 0.97
    assert i["action_invariance_consistency"] >= 0.97
    assert h["act_precision"] >= 0.97
    assert h["act_recall"] >= 0.95
    assert h["forbidden_act"] == 0
    assert h["invalid_action"] == 0
    assert r["robustness"]["minimum"] >= 0.93
    assert s["macro_f1"] >= 0.93
    assert s["exact_latent_state_reconstruction"] >= 0.85
    assert s["forbidden_act"] == 0
    assert s["invalid_action"] == 0
    assert all(r["operators"].values()), r["operators"]
    assert r["state_to_action_sufficiency"]["pass"]
    assert m["temporal"]["full"] >= 0.95
    assert m["temporal"]["delta"] >= 0.20
    assert m["contradiction_safety"]["full"] >= 0.95
    assert m["contradiction_safety"]["delta"] >= 0.20
    assert m["frame_composition"]["delta_vs_c"] >= 0.25


def test_final_v2_has_four_serious_architectures_and_selects_d():
    r = final_v2_summary()
    comparison = r["architecture_comparison"]
    assert len(comparison) == 4
    d = comparison[-1]
    c = comparison[2]
    assert d["architecture"] == "D_compositional_semantic_frame_resolver"
    assert d["exact_latent_state_reconstruction"] >= 0.85
    assert d["exact_latent_state_reconstruction"] - c["exact_latent_state_reconstruction"] >= 0.25


def test_final_v2_policy_oracle_gap():
    h = final_v2_summary()["holdout"]
    assert h["policy_oracle_macro_f1"] == 1.0
    assert 0.0 <= h["policy_oracle_gap"] <= 0.07
