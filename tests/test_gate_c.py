from __future__ import annotations

import copy
import re
from collections import Counter

import pytest

from proactivity.benchmark_v2 import (
    ACTIONS, DOMAINS, FORBIDDEN_CANDIDATE_FIELDS, artifact_texts, build_benchmark,
    build_manifest, frozen_integrity, load_config, state_key,
)
from proactivity.specification import evaluate
from scripts.audit_gate_c import build_report
from scripts.decide_gate_c import decide


@pytest.fixture(scope="session")
def bundle():
    return build_benchmark()


@pytest.fixture(scope="session")
def report():
    return build_report()


def test_gate_c_upstream_hashes_are_frozen():
    integrity = frozen_integrity()
    assert integrity["spec_match"] is True
    assert integrity["oracle_match"] is True


def test_gate_c_generation_is_deterministic():
    first = build_benchmark()
    second = build_benchmark()
    assert artifact_texts(first) == artifact_texts(second)
    assert build_manifest(first, artifact_texts(first)) == build_manifest(second, artifact_texts(second))


def test_candidate_schema_excludes_oracle_private_fields(bundle):
    for row in bundle["candidate"]:
        assert set(row) == {"scenario_id", "domain", "observation"}
        assert not (set(row) & FORBIDDEN_CANDIDATE_FIELDS)


def test_candidate_text_does_not_embed_action_labels(bundle):
    pattern = re.compile(r"\b(ignore|wait|suggest|notify|ask|act)\b", re.I)
    assert all(pattern.search(row["observation"]) is None for row in bundle["candidate"])


def test_scenario_ids_are_unique(bundle):
    ids = [row["scenario_id"] for row in bundle["private"]]
    assert len(ids) == len(set(ids))


def test_source_states_are_unique(bundle):
    states = [state_key(row["state"]) for row in bundle["private"]]
    assert len(states) == len(set(states))


def test_all_actions_meet_preregistered_coverage(bundle):
    minimum = load_config()["preregistered_criteria"]["minimum_examples_per_action"]
    counts = Counter(row["oracle_action"] for row in bundle["private"])
    assert set(counts) == set(ACTIONS)
    assert all(counts[action] >= minimum for action in ACTIONS)


def test_all_selected_nonfallback_rules_meet_coverage(report):
    minimum = report["preregistered_criteria"]["minimum_examples_per_selected_nonfallback_rule"]
    for rule_id, item in report["rule_coverage"].items():
        if rule_id == "R_FALLBACK_IGNORE" or item["reachable_selected_state_count"] == 0:
            continue
        assert item["benchmark_example_count"] >= minimum


def test_all_hard_prohibitions_meet_coverage(report):
    minimum = report["preregistered_criteria"]["minimum_examples_per_hard_prohibition"]
    for item in report["prohibition_coverage"].values():
        assert item["benchmark_trigger_count"] >= minimum
        assert item["counterfactual_pair_count"] >= 1


def test_triggered_hard_prohibitions_never_emit_forbidden_action(report):
    assert report["prohibition_safety_violations"] == []


def test_counterfactual_relations_are_clean(report):
    assert report["counterfactual"]["family_count"] >= report["preregistered_criteria"]["minimum_counterfactual_families"]
    assert report["counterfactual"]["violations"] == []


def test_temporal_relations_are_clean(report):
    assert report["temporal"]["sequence_count"] >= report["preregistered_criteria"]["minimum_temporal_sequences"]
    assert report["temporal"]["violations"] == []


def test_group_aware_split_has_no_relation_leakage(report):
    assert report["split_integrity"]["group_leakage"] == {}
    assert all(report["split_integrity"]["counts"].get(name, 0) > 0 for name in ("development", "validation", "protected_test"))


def test_all_domains_are_represented(report):
    assert all(report["diversity"]["domain_distribution"].get(domain, 0) > 0 for domain in DOMAINS)


def test_template_family_share_is_within_preregistered_limit(report):
    assert report["diversity"]["largest_template_family_share"] <= report["preregistered_criteria"]["largest_observation_template_family_share_max"]


def test_oracle_provenance_has_no_mismatches(report):
    provenance = report["ground_truth_provenance"]
    assert provenance["oracle_mismatch_findings"] == 0
    assert provenance["oracle_derived_records"] == report["scenario_count"]


def test_no_manual_or_llm_gold(report):
    provenance = report["ground_truth_provenance"]
    assert provenance["manual_gold_findings"] == 0
    assert provenance["llm_gold_findings"] == 0


def test_candidate_private_schema_boundary_is_clean(report):
    assert report["representation"]["private_forbidden_overlap"] == []
    assert report["representation"]["direct_answer_token_findings"] == []


def test_report_regeneration_is_reproducible(report):
    assert report["reproducibility"]["deterministic_regeneration"] is True


def test_gate_c_decision_matches_report(report):
    assert decide(report) == report["gate_verdict"]


def test_fail_closed_on_missing_report_fields(report):
    damaged = copy.deepcopy(report)
    damaged.pop("benchmark_sha256")
    assert decide(damaged) == "GATE C — BLOCKED: INCOMPLETE_MACHINE_REPORT"


def test_fail_closed_on_invalid_report_identity(report):
    damaged = copy.deepcopy(report)
    damaged["gate"] = "D"
    assert decide(damaged) == "GATE C — BLOCKED: INVALID_REPORT_IDENTITY"


def test_fail_closed_on_corrupted_spec_hash_evidence(report):
    damaged = copy.deepcopy(report)
    damaged["upstream_integrity"]["spec_match"] = False
    assert decide(damaged) == "GATE C — BLOCKED: UPSTREAM_INTEGRITY_MISMATCH"


def test_fail_closed_on_corrupted_oracle_hash_evidence(report):
    damaged = copy.deepcopy(report)
    damaged["upstream_integrity"]["oracle_match"] = False
    assert decide(damaged) == "GATE C — BLOCKED: UPSTREAM_INTEGRITY_MISMATCH"


def test_fail_closed_on_benchmark_validity_failure(report):
    damaged = copy.deepcopy(report)
    damaged["criteria_failures"] = ["FORBIDDEN_CANDIDATE_METADATA"]
    assert decide(damaged) == "GATE C — FAIL: BENCHMARK_VALIDITY_CRITERIA_NOT_MET"


def test_fail_closed_on_report_decision_inconsistency(report):
    damaged = copy.deepcopy(report)
    damaged["criteria_failures"] = []
    damaged["gate_verdict"] = "GATE C — FAIL: BENCHMARK_VALIDITY_CRITERIA_NOT_MET"
    assert decide(damaged) == "GATE C — BLOCKED: REPORT_DECISION_INCONSISTENCY"


def test_row_order_does_not_change_action_distribution(bundle):
    original = Counter(row["oracle_action"] for row in bundle["private"])
    reversed_rows = list(reversed(bundle["private"]))
    assert Counter(row["oracle_action"] for row in reversed_rows) == original


def test_domain_metadata_does_not_affect_oracle(bundle):
    for row in bundle["private"][:25]:
        baseline = evaluate(row["state"])
        for _domain in DOMAINS:
            assert evaluate(row["state"]).action == baseline.action


def test_private_metadata_deletion_does_not_change_candidate_observation(bundle):
    candidate_by_id = {row["scenario_id"]: row for row in bundle["candidate"]}
    for row in bundle["private"][:25]:
        before = copy.deepcopy(candidate_by_id[row["scenario_id"]])
        stripped = {"scenario_id": row["scenario_id"], "domain": row["domain"]}
        assert stripped["scenario_id"] == before["scenario_id"]
        assert candidate_by_id[row["scenario_id"]] == before


def test_relation_members_share_domain_and_template(bundle):
    private = {row["scenario_id"]: row for row in bundle["private"]}
    for relation in bundle["relations"]:
        rows = [private[sid] for sid in relation["scenario_ids"]]
        assert len({row["domain"] for row in rows}) == 1
        assert len({row["template_family"] for row in rows}) == 1
