from __future__ import annotations

import json
from pathlib import Path

from evaluation.v7r import auditor
from evaluation.v7r.common import (
    FAMILIES, RUN_EXAMPLE_COUNT, SEEDS, THRESHOLDS, macro_f1, read_json, write_json, write_jsonl,
)
from evaluation.v7r.runner import ALLOWED_INPUT_KEYS
from evaluation.v7r.scorer import relation_metrics

def test_machine_preregistration_matches_runtime():
    machine = json.loads(Path("evaluation/v7r/preregistration/V7R_PREREGISTRATION.json").read_text())
    assert machine["run_count"] == len(SEEDS)
    assert machine["seeds"] == SEEDS
    assert machine["families"] == list(FAMILIES)
    assert machine["examples_per_run"] == RUN_EXAMPLE_COUNT
    assert machine["thresholds"] == THRESHOLDS

def test_runner_label_isolation_contract():
    assert ALLOWED_INPUT_KEYS == {"example_id", "text"}

def test_scorer_macro_f1_perfect():
    labels = ["IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT"]
    assert macro_f1(labels, labels) == 1.0

def _state(**changes):
    state = {
        "permission": "granted", "information": "sufficient", "urgency": "normal",
        "need": "material", "side_effect": "external", "risk": "low",
        "reversibility": "reversible", "deferral_available": False,
        "execution_possible": True, "clarification_possible": True,
        "acknowledged": False, "completed": False,
    }
    state.update(changes)
    return state

def test_counterfactual_and_invariance_scorer_correctness():
    s1 = _state()
    s2 = _state(risk="high")
    pairs = [
        ({
            "example_id": "a", "ground_truth_state": s1, "specified_fields": list(s1),
            "fully_specified": True, "expected_unknown_fields": [], "expected_action": "ACT",
            "family": "Lexical", "counterfactual_pair_id": "cf", "invariance_group_id": None,
        }, {"state": s1, "action": "ACT", "unknown_fields": []}),
        ({
            "example_id": "b", "ground_truth_state": s2, "specified_fields": list(s2),
            "fully_specified": True, "expected_unknown_fields": [], "expected_action": "ASK",
            "family": "Lexical", "counterfactual_pair_id": "cf", "invariance_group_id": None,
        }, {"state": s2, "action": "ASK", "unknown_fields": []}),
        ({
            "example_id": "c", "ground_truth_state": s1, "specified_fields": list(s1),
            "fully_specified": True, "expected_unknown_fields": [], "expected_action": "ACT",
            "family": "Lexical", "counterfactual_pair_id": None, "invariance_group_id": "inv",
        }, {"state": s1, "action": "ACT", "unknown_fields": []}),
        ({
            "example_id": "d", "ground_truth_state": s1, "specified_fields": list(s1),
            "fully_specified": True, "expected_unknown_fields": [], "expected_action": "ACT",
            "family": "Lexical", "counterfactual_pair_id": None, "invariance_group_id": "inv",
        }, {"state": s1, "action": "ACT", "unknown_fields": []}),
    ]
    m = relation_metrics(pairs)
    assert m["counterfactual_exact_pair"] == 1.0
    assert m["invariance_action_consistency"] == 1.0
    assert m["invariance_correct_consistency"] == 1.0

def test_dataset_seed_mismatch_detection(tmp_path: Path):
    art = tmp_path / "artifacts/v7r"
    art.mkdir(parents=True)
    write_json(art / "PROTECTED_DATA_MANIFEST.json", {
        "run_count": len(SEEDS), "total_example_count": RUN_EXAMPLE_COUNT * len(SEEDS),
        "realizations": [
            {"run_id": run_id, "seed": (seed + 1 if run_id == "Q1" else seed),
             "example_count": RUN_EXAMPLE_COUNT,
             "family_distribution": {f: 50 for f in FAMILIES}}
            for run_id, seed in SEEDS.items()
        ],
    })
    problems = auditor.validate_dataset(tmp_path)
    assert "Q1:seed_mismatch" in problems

def test_incomplete_run_detection(tmp_path: Path):
    problems = auditor.validate_predictions(tmp_path)
    assert "predictions_complete_marker_missing" in problems
    assert any(p.endswith(":prediction_missing") for p in problems)

def test_hash_mismatch_detection_primitive():
    assert auditor.sha256_bytes(b"candidate-a") != auditor.sha256_bytes(b"candidate-b")

def test_forbidden_rerun_probe_semantics():
    assert auditor.terminal_probe_is_forbidden(0) is True
    assert auditor.terminal_probe_is_forbidden(1) is False

def test_leakage_exact_overlap_detection(tmp_path: Path):
    repo = tmp_path / "repo"
    work = tmp_path / "work"
    (repo / "data").mkdir(parents=True)
    write_jsonl(repo / "data/legacy.jsonl", [{"text": "A uniquely repeated protected sentence."}])
    for run_id in SEEDS:
        p = work / "protected" / run_id
        p.mkdir(parents=True)
        write_jsonl(p / "ground_truth.jsonl", [{
            "example_id": f"{run_id}-x",
            "text": "A uniquely repeated protected sentence." if run_id == "Q1" else f"Fresh sentence {run_id}.",
        }])
    result = auditor.leakage_audit(repo, work)
    assert result["exact_text_overlap_count"] == 1
    assert result["actual_protected_example_access"] == "NONE"
