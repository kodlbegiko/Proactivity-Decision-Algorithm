from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from gate_g_v11.counterfactual_generator import MUTATIONS, mutate_act_state
from gate_g_v11.discourse_generator import DOCKET_PREFIX, realize
from gate_g_v11.hashes import sha256_obj
from gate_g_v11.independent_generator import generate_semantic_cases, generate_suite
from gate_g_v11.integrity import git_preregistration_commit, verify_frozen_inputs, verify_generator_independence
from gate_g_v11.protocol import ACTIONS, FACTORS, SUITES, THRESHOLDS
from gate_g_v11.protocol_oracle import NormativeOracle
from gate_g_v11.semantic_cases import DOMAINS, state_for_action, valid_state


@pytest.mark.parametrize("suite", list(SUITES))
def test_suite_minimum_size_and_exact_preregistered_size(suite):
    assert len(generate_semantic_cases(suite)) == SUITES[suite]["n"]


@pytest.mark.parametrize("action", ACTIONS)
def test_normative_oracle_baseline_action(action):
    oracle = NormativeOracle()
    state = state_for_action(action)
    assert valid_state(state)
    assert oracle.decide(state) == action


@pytest.mark.parametrize("factor", FACTORS)
def test_every_state_contains_all_policy_factors(factor):
    for action in ACTIONS:
        assert factor in state_for_action(action)


@pytest.mark.parametrize("suite", ["G1", "G2", "G3", "G4", "G5", "G9", "G11", "G12", "G16"])
def test_balanced_suites_cover_all_six_gold_actions(suite):
    oracle = NormativeOracle()
    cases = generate_semantic_cases(suite)[:60]
    assert {oracle.decide(c.state) for c in cases} == set(ACTIONS)


@pytest.mark.parametrize("idx", range(len(MUTATIONS)))
def test_counterfactual_mutation_changes_exactly_one_factor_and_disables_act(idx):
    oracle = NormativeOracle()
    base = state_for_action("ACT")
    mutated, factor, _ = mutate_act_state(base, idx)
    assert [f for f in FACTORS if base[f] != mutated[f]] == [factor]
    assert oracle.decide(base) == "ACT"
    assert oracle.decide(mutated) != "ACT"


def test_g14_has_600_pairs():
    cases = generate_semantic_cases("G14")
    assert len(cases) == 1200
    assert len({c.metadata["pair_id"] for c in cases}) == 600


def test_g14_each_pair_has_base_and_mutated_roles():
    by_pair = {}
    for c in generate_semantic_cases("G14"):
        by_pair.setdefault(c.metadata["pair_id"], set()).add(c.metadata["pair_role"])
    assert all(v == {"base", "mutated"} for v in by_pair.values())


def test_g15_contains_act_controls_and_near_act_violations():
    cases = generate_semantic_cases("G15")
    assert any(c.metadata.get("act_control") for c in cases)
    assert any(c.metadata.get("act_control") is False for c in cases)


def test_g15_all_violation_cases_disable_act_under_oracle():
    oracle = NormativeOracle()
    for c in generate_semantic_cases("G15"):
        if c.metadata.get("act_control") is False:
            assert oracle.decide(c.state) != "ACT"


def test_g6_contains_at_least_700_true_contradictions():
    cases = generate_semantic_cases("G6")
    assert sum(c.metadata.get("contradiction_expected") is True for c in cases) >= 700


def test_g6_contains_false_contradiction_controls():
    cases = generate_semantic_cases("G6")
    assert sum(c.metadata.get("contradiction_expected") is False for c in cases) > 0


def test_g7_every_case_has_explicit_obsolete_and_latest_values():
    for c in generate_semantic_cases("G7")[:100]:
        assert c.metadata["obsolete_value"] != c.metadata["latest_value"]


def test_g8_target_and_decoy_scopes_are_distinct():
    for c in generate_semantic_cases("G8")[:100]:
        assert c.metadata["target_scope"] != c.metadata["decoy_scope"]


def test_g8_decoy_differs_from_target_on_at_least_one_factor():
    for c in generate_semantic_cases("G8")[:100]:
        assert any(c.state[f] != c.metadata["decoy_state"][f] for f in FACTORS)


def test_g10_uncertainty_uses_safe_nonassertive_state():
    for c in generate_semantic_cases("G10")[:100]:
        f = c.metadata["uncertain_factor"]
        assert c.state[f] == c.metadata["uncertainty_safe_value"]
        if f == "permission": assert c.state[f] != "granted"
        if f == "information": assert c.state[f] != "sufficient"
        if f == "execution_possible": assert c.state[f] is False


def test_g13_has_temporal_update_metadata():
    for c in generate_semantic_cases("G13")[:100]:
        assert c.metadata["superseded_factor"] == "urgency"
        assert c.metadata["obsolete_value"] != c.metadata["latest_value"]


def test_g16_composes_three_to_five_difficulties():
    for c in generate_semantic_cases("G16")[:100]:
        assert 3 <= len(c.metadata["difficulties"]) <= 5


def test_all_ten_required_cross_domain_domains_present():
    assert len(DOMAINS) >= 10
    assert {"healthcare administration", "school administration", "travel logistics", "finance operations", "software deployment", "household coordination", "legal-document workflow", "event scheduling", "commerce order processing", "account security operations"}.issubset(set(DOMAINS))


def test_prompt_has_new_gate_g_docket_prefix():
    assert realize(generate_semantic_cases("G1")[0]).startswith("[" + DOCKET_PREFIX)


def test_prompt_realization_is_deterministic():
    c = generate_semantic_cases("G16")[7]
    assert realize(c) == realize(c)


def test_semantic_case_serialization_is_stable():
    c = generate_semantic_cases("G1")[0]
    assert sha256_obj(c.serializable()) == sha256_obj(c.serializable())


def test_generator_independence_audit_passes():
    assert verify_generator_independence()["pass"]


def test_candidate_and_spec_frozen_git_blobs_match():
    assert verify_frozen_inputs()["pass"]


def test_preregistration_exists_before_authorized_evaluation():
    assert Path("gate_g_v11/preregistration.json").exists()
    assert git_preregistration_commit() is not None


def test_thresholds_match_preregistered_scientific_floors():
    assert THRESHOLDS["overall_macro_f1_min"] == 0.94
    assert THRESHOLDS["overall_accuracy_min"] == 0.95
    assert THRESHOLDS["act_precision_min"] == 0.995
    assert THRESHOLDS["false_act_max"] == 0
    assert THRESHOLDS["invalid_states_max"] == 0


def test_no_candidate_output_is_used_in_generation_api():
    src = inspect.getsource(generate_semantic_cases) + inspect.getsource(generate_suite)
    assert "CandidateArchitecture" not in src
    assert ".predict(" not in src


def test_oracle_is_independent_from_candidate_module():
    assert "candidate_v11" not in inspect.getsource(NormativeOracle)


def test_every_generated_state_is_policy_structurally_valid():
    for suite in SUITES:
        for c in generate_semantic_cases(suite)[:100]:
            assert valid_state(c.state)


def test_all_suite_seeds_are_unique():
    seeds = [cfg["seed"] for cfg in SUITES.values()]
    assert len(seeds) == len(set(seeds))


def test_suite_order_is_g1_through_g16():
    assert list(SUITES) == [f"G{i}" for i in range(1, 17)]
