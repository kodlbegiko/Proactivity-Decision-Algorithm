from proactivity.candidate_v12 import ArchitectureC
from proactivity.candidate_v12_dev import make_records, counterfactual_metrics, invariance_metrics, unknown_metrics


def test_fresh_semantic_reconstruction():
    a = ArchitectureC(); rec = make_records(777, 100)
    assert sum(a.parse(r["text"]).state == r["state"] for r in rec) / len(rec) >= .85


def test_policy_deterministic():
    a = ArchitectureC(); r = make_records(778, 1)[0]
    x = a.parse(r["text"]); y = a.parse(r["text"])
    assert x.state == y.state and x.action == y.action


def test_permission_counterfactual():
    assert counterfactual_metrics(ArchitectureC(), 779, 60)["latent_factor_delta_correctness"] >= .92


def test_paraphrase_invariance():
    assert invariance_metrics(ArchitectureC(), 780, 60)["latent_state_invariance_consistency"] >= .97


def test_unknown_calibration():
    assert unknown_metrics(ArchitectureC(), 781, 60)["legitimate_unknown_recall"] >= .95


def test_no_forbidden_act_on_fresh_set():
    a = ArchitectureC()
    for r in make_records(782, 200):
        p = a.parse(r["text"])
        if p.action == "ACT":
            assert r["action"] == "ACT"
