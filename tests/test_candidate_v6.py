from __future__ import annotations

from proactivity.candidate_v6 import ACTIONS, FIELDS, architecture_configs, get_config, segment
from proactivity.candidate_v6_data import FAMILIES, SPLIT_SIZES, PAIR_SIZES, TRANSITIONS
from proactivity.specification.oracle import load_spec


def test_search_budget_is_exactly_preregistered() -> None:
    configs = architecture_configs()
    assert len(configs) == 22
    assert sum(c.architecture == "V6A" for c in configs) == 8
    assert sum(c.architecture == "V6B" for c in configs) == 6
    assert sum(c.architecture == "V6C" for c in configs) == 8
    assert len({c.config_id for c in configs}) == 22
    for config in configs:
        assert get_config(config.config_id) == config


def test_protocol_fields_are_explicitly_reconstructed() -> None:
    spec = load_spec()
    assert tuple(spec["state_schema"].keys()) == FIELDS
    assert set(ACTIONS) == set(spec["actions"])


def test_dataset_sizes_and_pair_counts_match_preregistration() -> None:
    assert SPLIT_SIZES == {
        "train": 3600,
        "validation": 900,
        "development_ood": 900,
        "lexical_holdout": 600,
        "rendering_holdout": 600,
        "compositional_holdout": 600,
        "negation": 360,
    }
    assert PAIR_SIZES == {"counterfactual": 180, "invariance": 180}


def test_holdout_families_are_separated_from_train_validation() -> None:
    dev = set(FAMILIES["development_ood"])
    rendering = set(FAMILIES["rendering_holdout"])
    negation = set(FAMILIES["negation"])
    trainval = set(FAMILIES["train"]) | set(FAMILIES["validation"])
    assert not dev.intersection(trainval)
    assert not rendering.intersection(trainval)
    assert not negation.intersection(trainval)


def test_counterfactual_protocol_contains_required_transition_types() -> None:
    fields = {field for field, _before, _after in TRANSITIONS}
    assert {
        "permission",
        "information",
        "risk",
        "reversibility",
        "execution_possible",
        "need",
        "deferral_available",
        "acknowledged",
        "completed",
        "urgency",
    }.issubset(fields)
    assert len(TRANSITIONS) == 14


def test_segmentation_supports_dialogue_notes_and_prose() -> None:
    text = "First condition.\nSpeaker 2: Second condition | Third condition; Fourth condition."
    assert len(segment(text, "sentence_clause")) >= 3
    assert len(segment(text, "punctuation_clause")) >= 4
    assert segment(text, "whole_observation") == [text]
