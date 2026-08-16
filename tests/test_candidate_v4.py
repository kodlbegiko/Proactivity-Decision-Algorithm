from __future__ import annotations

import random

from proactivity.candidate_v4 import AtomStateMachineCandidate, split_clauses
from proactivity.recovery_v4_data import (
    ACTIONS,
    FIELDS,
    balanced_state_pool,
    build_counterfactual_pairs,
    build_splits,
    candidate_view,
    generation_manifest,
    render_state,
)


def _state_key(record: dict) -> tuple:
    return tuple(record["state"][field] for field in FIELDS)


def test_generation_is_deterministic_and_preregistered_sizes_hold():
    first = generation_manifest()
    second = generation_manifest()
    assert first == second
    assert first["split_sizes"] == {
        "train": 576,
        "validation": 36,
        "ood": 36,
        "lexical_holdout": 24,
        "rendering_holdout": 24,
        "compositional_holdout": 24,
    }
    assert first["counterfactual_pairs"] == 18
    assert first["invariance_pairs"] == 24


def test_qualification_state_configurations_are_disjoint():
    splits = build_splits()
    state_sets = {name: {_state_key(record) for record in records} for name, records in splits.items()}
    assert len(state_sets["train"]) == 144
    names = ["train", "validation", "ood", "lexical_holdout", "rendering_holdout", "compositional_holdout"]
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            assert state_sets[left].isdisjoint(state_sets[right]), (left, right)


def test_candidate_view_exposes_only_domain_and_observation():
    record = build_splits()["validation"][0]
    view = candidate_view(record)
    assert set(view) == {"domain", "observation"}
    assert "state" not in view
    assert "expected_action" not in view


def test_atom_candidate_has_all_six_actions_on_validation():
    candidate = AtomStateMachineCandidate(act_confidence_floor=0.55)
    validation = build_splits()["validation"]
    predicted = candidate.predict([candidate_view(record) for record in validation])
    assert set(predicted) == set(ACTIONS)
    assert predicted == [record["expected_action"] for record in validation]


def test_clause_permutation_is_prediction_invariant():
    candidate = AtomStateMachineCandidate(act_confidence_floor=0.55)
    pool = balanced_state_pool()
    rng = random.Random(7)
    for action in ACTIONS:
        state = pool[action][24]
        observation = render_state(state, family="canonical", mode="train", rng=rng)
        clauses = split_clauses(observation)
        reversed_observation = " | ".join(reversed(clauses))
        assert candidate.predict([{"domain": "x", "observation": observation}])[0] == action
        assert candidate.predict([{"domain": "x", "observation": reversed_observation}])[0] == action


def test_punctuation_family_change_preserves_semantics():
    candidate = AtomStateMachineCandidate(act_confidence_floor=0.55)
    pool = balanced_state_pool()
    rng = random.Random(11)
    for action in ACTIONS:
        state = pool[action][25]
        canonical = render_state(state, family="canonical", mode="train", rng=rng)
        telegraphic = " | ".join(split_clauses(canonical))
        assert candidate.predict([{"domain": "x", "observation": canonical}])[0] == action
        assert candidate.predict([{"domain": "x", "observation": telegraphic}])[0] == action


def test_act_counterfactuals_never_remain_act():
    candidate = AtomStateMachineCandidate(act_confidence_floor=0.55)
    for pair in build_counterfactual_pairs():
        before = pair["before"]
        after = pair["after"]
        assert candidate.predict([candidate_view(before)])[0] == "ACT"
        assert candidate.predict([candidate_view(after)])[0] == after["expected_action"]
        assert candidate.predict([candidate_view(after)])[0] != "ACT"


def test_completed_states_cannot_emit_intervention_actions():
    candidate = AtomStateMachineCandidate(act_confidence_floor=0.55)
    pool = balanced_state_pool()
    rng = random.Random(13)
    completed = [state for state in pool["IGNORE"] if state["completed"]][:8]
    assert completed
    for state in completed:
        observation = render_state(state, family="canonical", mode="train", rng=rng)
        prediction = candidate.predict([{"domain": "x", "observation": observation}])[0]
        assert prediction == "IGNORE"
        assert prediction not in {"ACT", "ASK", "NOTIFY", "SUGGEST"}


def test_full_record_hidden_fields_do_not_change_inference():
    candidate = AtomStateMachineCandidate(act_confidence_floor=0.55)
    record = build_splits()["validation"][0]
    view_prediction = candidate.predict([candidate_view(record)])[0]
    poisoned = dict(record)
    poisoned["state"] = {field: "malicious" for field in FIELDS}
    poisoned["expected_action"] = "ACT" if record["expected_action"] != "ACT" else "WAIT"
    full_prediction = candidate.predict([poisoned])[0]
    assert full_prediction == view_prediction
