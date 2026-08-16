from proactivity.candidate_v12 import ArchitectureC
from proactivity.candidate_v12_advanced_dev import (
    advanced_development_summary,
    evaluate_architecture,
    make_compositional_records,
    operator_suite,
    state_to_action_sufficiency,
)
from proactivity.candidate_v12_frames import ArchitectureD


def test_compositional_holdout_meets_semantic_floors():
    r = evaluate_architecture(ArchitectureD(), make_compositional_records(18001, 480, split="holdout"))
    assert r["macro_f1"] >= 0.93
    assert r["exact_latent_state_reconstruction"] >= 0.85
    assert r["mean_factor_accuracy"] >= 0.97
    assert r["act_critical_factor_accuracy"] >= 0.985
    assert r["act_precision"] >= 0.97
    assert r["act_recall"] >= 0.95
    assert r["forbidden_act"] == 0
    assert r["invalid_action"] == 0


def test_compositional_architecture_materially_exceeds_lexical_predecessor():
    records = make_compositional_records(18002, 480, split="holdout")
    c = evaluate_architecture(ArchitectureC(), records)
    d = evaluate_architecture(ArchitectureD(), records)
    assert d["exact_latent_state_reconstruction"] - c["exact_latent_state_reconstruction"] >= 0.25
    assert d["mean_factor_accuracy"] - c["mean_factor_accuracy"] >= 0.10


def test_all_mandatory_operator_probes_pass():
    results = operator_suite()
    assert results
    assert all(results.values()), results


def test_state_to_action_sufficiency():
    r = state_to_action_sufficiency(seed=18003, n=5000)
    assert r["pass"]
    assert r["conflicting_equal_states"] == 0
    assert r["invalid_action"] == 0


def test_long_context_stress_meets_floor():
    r = evaluate_architecture(ArchitectureD(), make_compositional_records(18004, 480, split="stress", long_context=True))
    assert r["macro_f1"] >= 0.93
    assert r["exact_latent_state_reconstruction"] >= 0.85
    assert r["forbidden_act"] == 0
    assert r["invalid_action"] == 0


def test_five_seed_advanced_robustness():
    r = advanced_development_summary()
    assert r["robustness"]["minimum"] >= 0.93
    assert r["holdout"]["exact_latent_state_reconstruction"] >= 0.85
    assert r["stress"]["macro_f1"] >= 0.93
    assert all(r["operators"].values())
    assert r["state_to_action_sufficiency"]["pass"]
