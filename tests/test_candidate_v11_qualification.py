from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from evaluation.v11q import protected_builder
from evaluation.v11q.auditor import (
    audit_source_boundaries, leakage_audit, verify_candidate_immutable,
    verify_preregistration,
)
from evaluation.v11q.common import (
    ACTIONS, EXAMPLES_PER_RUN, FAMILIES, FORBIDDEN_RETRY_REASONS,
    RUN_SEEDS, TECHNICAL_RETRY_REASONS, macro_f1, read_jsonl,
)
from evaluation.v11q.orchestrate import IMMUTABLE_MANIFEST, ROOT, _terminal_state
from evaluation.v11q.runner import validate_runner_record
from evaluation.v11q.scorer import _metrics_from_pairs, exact_reconstruction_ok, scientific_criteria


def test_preregistration_before_authorization_and_seed_freeze():
    result = verify_preregistration(ROOT)
    assert result["pass"]
    assert result["seeds_frozen"]
    assert result["chronology_pass"]


def test_candidate_immutable_hash():
    result = verify_candidate_immutable(ROOT, IMMUTABLE_MANIFEST)
    assert result["pass"]


def test_runner_input_isolation_contract():
    validate_runner_record({"example_id": "x", "text": "hello"})
    with pytest.raises(ValueError):
        validate_runner_record({"example_id": "x", "text": "hello", "label": "ACT"})


def test_ground_truth_and_generation_dependency_isolation():
    result = audit_source_boundaries(ROOT)
    assert result["pass"]
    assert not result["builder_imports_candidate_v11"]
    assert not result["builder_imports_benchmark_v11_generator"]
    assert result["runner_imports_candidate_v11"]


def test_protected_generation_reproducibility_family_action_and_relations(tmp_path: Path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    m1 = protected_builder.build_run("Q1", RUN_SEEDS["Q1"], first)
    m2 = protected_builder.build_run("Q1", RUN_SEEDS["Q1"], second)
    assert m1["runner_sha256"] == m2["runner_sha256"]
    assert m1["truth_sha256"] == m2["truth_sha256"]
    assert m1["examples"] == EXAMPLES_PER_RUN
    assert all(m1["action_distribution"].get(action, 0) >= 60 for action in ACTIONS)
    assert all(m1["family_distribution"].get(family, 0) > 0 for family in FAMILIES)
    assert m1["counterfactual_pairs"] == 42
    assert m1["invariance_groups"] == 12

    truth = read_jsonl(first / "truth/Q1.jsonl")
    by_pair: dict[str, list[dict]] = {}
    by_group: dict[str, list[dict]] = {}
    for record in truth:
        if record["counterfactual_pair_id"]:
            by_pair.setdefault(record["counterfactual_pair_id"], []).append(record)
        if record["invariance_group_id"]:
            by_group.setdefault(record["invariance_group_id"], []).append(record)
    assert len(by_pair) == 42
    for members in by_pair.values():
        assert len(members) == 2
        diffs = [field for field in members[0]["state"] if members[0]["state"][field] != members[1]["state"][field]]
        assert len(diffs) == 1
        assert members[0]["expected_action"] != members[1]["expected_action"]
    assert len(by_group) == 12
    for members in by_group.values():
        assert len(members) == 3
        assert len({json.dumps(m["state"], sort_keys=True) for m in members}) == 1
        assert len({m["expected_action"] for m in members}) == 1


def test_exact_overlap_and_normalized_overlap_detection(tmp_path: Path):
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    (root / "data/development").mkdir(parents=True)
    (root / "benchmark_v11").mkdir(parents=True)
    (workspace / "runner").mkdir(parents=True)
    (root / "data/development/example.jsonl").write_text('{"text":"A distinctive development sentence lives here."}\n', encoding="utf-8")
    (root / "benchmark_v11/generator.py").write_text('X = "another independent development realization phrase"\n', encoding="utf-8")
    (workspace / "runner/Q1.jsonl").write_text('{"example_id":"q","text":"A distinctive development sentence lives here."}\n', encoding="utf-8")
    result = leakage_audit(root, workspace)
    assert not result["pass"]
    assert result["exact_text_overlap"] == 1
    assert result["normalized_exact_overlap"] == 1


def test_unknown_scoring_and_exact_reconstruction():
    truth = {
        "example_id": "u",
        "state": {"permission": "missing", "information": "insufficient"},
        "specified_fields": ["information"],
        "expected_unknown_fields": ["permission"],
        "expected_action": "ASK",
        "act_prohibited": True,
    }
    pred = {
        "example_id": "u",
        "action": "ASK",
        "state": {"permission": "missing", "information": "insufficient"},
        "factor_status": {"permission": "SEMANTICALLY_UNSPECIFIED", "information": "KNOWN"},
    }
    assert exact_reconstruction_ok(truth, pred)
    metrics = _metrics_from_pairs([(truth, pred)])
    assert metrics["legitimate_unknown_recall"] == 1.0
    assert metrics["false_unknown_rate"] == 0.0


def test_macro_f1_scorer():
    assert macro_f1(list(ACTIONS), list(ACTIONS)) == 1.0
    assert macro_f1(list(ACTIONS), ["IGNORE"] * len(ACTIONS)) < 0.5


def test_act_precision_recall_forbidden_and_invalid_action():
    base_state = {field: None for field in ("permission", "information", "urgency", "need", "side_effect", "risk", "reversibility", "deferral_available", "execution_possible", "clarification_possible", "acknowledged", "completed")}
    truth1 = {"example_id": "1", "state": base_state, "specified_fields": [], "expected_unknown_fields": [], "expected_action": "ACT", "act_prohibited": False}
    truth2 = {"example_id": "2", "state": base_state, "specified_fields": [], "expected_unknown_fields": [], "expected_action": "ASK", "act_prohibited": True}
    pred1 = {"example_id": "1", "action": "ACT", "state": {}, "factor_status": {}}
    pred2 = {"example_id": "2", "action": "ACT", "state": {}, "factor_status": {}}
    metrics = _metrics_from_pairs([(truth1, pred1), (truth2, pred2)])
    assert metrics["act_recall"] == 1.0
    assert metrics["act_precision"] == 0.5
    assert metrics["forbidden_act"] == 1
    pred2["action"] = "BOGUS"
    metrics = _metrics_from_pairs([(truth1, pred1), (truth2, pred2)])
    assert metrics["invalid_action"] == 1


def test_retry_policy_and_score_driven_rerun_prohibition():
    assert "runner_crash" in TECHNICAL_RETRY_REASONS
    assert "score_driven_rerun" in FORBIDDEN_RETRY_REASONS
    assert not (TECHNICAL_RETRY_REASONS & FORBIDDEN_RETRY_REASONS)


def test_terminal_decision_logic():
    passed = {"research_integrity": "PASS"}
    failed_integrity = {"research_integrity": "FAIL"}
    assert "INVALID" in _terminal_state(failed_integrity, True, {"all_scientific_criteria_pass": True})
    assert "INVALID" in _terminal_state(passed, False, {"all_scientific_criteria_pass": True})
    assert "FRESH_CONFIRMATORY_AUTHORIZED" in _terminal_state(passed, True, {"all_scientific_criteria_pass": True})
    assert "LINEAGE_TERMINATED" in _terminal_state(passed, True, {"all_scientific_criteria_pass": False})


def test_no_protected_raw_data_tracked_in_qualification_tree():
    tracked = subprocess.check_output(["git", "ls-files", "evaluation/v11q", "artifacts/candidate_v11_qualification"], cwd=ROOT, text=True).splitlines()
    forbidden = [p for p in tracked if "/truth/" in p or "/runner/" in p or "/predictions/" in p or p.endswith(".jsonl")]
    assert forbidden == []
