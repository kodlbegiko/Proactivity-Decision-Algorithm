from pathlib import Path

from proactivity.candidate_v7 import CONFIGS
from proactivity.candidate_v7_data import SIZES, SEEDS


def test_preregistered_sizes_and_seeds_are_fixed():
    assert SIZES == {"train":4800,"validation":1200,"development_ood":1200,"lexical_holdout":800,"rendering_holdout":800,"compositional_holdout":800,"negation_holdout":600,"scope_holdout":600,"temporal_holdout":600,"counterfactual":480,"invariance":480}
    assert SEEDS["train"] == 7001 and SEEDS["invariance"] == 7011
    assert len(CONFIGS) == 12


def test_candidate_v7_reasoner_does_not_import_candidate_v6_source():
    text = Path("src/proactivity/candidate_v7.py").read_text(encoding="utf-8")
    assert "candidate_v6" not in text
    assert "data/candidate_v6_development" not in text
