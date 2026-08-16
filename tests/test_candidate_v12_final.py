from proactivity.candidate_v12_final_dev import final_development_summary


def test_final_development_authorization_floors():
    r = final_development_summary()
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
    assert m["frame_composition"]["full_exact_state"] - m["frame_composition"]["lexical_c_exact_state"] >= 0.25


def test_final_architecture_comparison_has_four_serious_candidates():
    r = final_development_summary()
    comparison = r["architecture_comparison"]
    assert len(comparison) == 4
    assert comparison[-1]["architecture"] == "D_compositional_semantic_frame_resolver"
    assert comparison[-1]["exact_latent_state_reconstruction"] >= 0.85
    assert comparison[-1]["exact_latent_state_reconstruction"] - comparison[2]["exact_latent_state_reconstruction"] >= 0.25


def test_policy_oracle_gap_is_attributable():
    r = final_development_summary()
    h = r["holdout"]
    assert h["policy_oracle_macro_f1"] >= h["macro_f1"]
    assert h["policy_oracle_macro_f1"] == 1.0
    assert h["policy_oracle_gap"] <= 0.07
