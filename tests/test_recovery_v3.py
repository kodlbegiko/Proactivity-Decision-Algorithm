import json
from pathlib import Path

from proactivity.recovery_candidates_v3 import CANDIDATE_FACTORIES, extract_visible_semantic_factors, make_candidate


def test_candidate_budget_exactly_eight():
    assert len(CANDIDATE_FACTORIES) == 8


def test_parser_handles_negation_and_synonyms():
    text = (
        "Authorization is not unavailable. Enough evidence is available. There is no current urgency. "
        "Material intervention is needed. The effect stays local. Risk remains minimal. "
        "The change is not irreversible. No later trigger is defined. Execution is possible. "
        "Clarification is possible. Acknowledgement is absent. The task is incomplete."
    )
    f = extract_visible_semantic_factors(text)
    assert f["permission"] == "granted"
    assert f["information"] == "sufficient"
    assert f["reversibility"] == "reversible"
    assert f["completed"] is False


def test_selected_tree_is_constructible():
    assert make_candidate("V3A_factor_tree") is not None


def test_generated_summary_when_present_is_development_only_and_balanced():
    path = Path("data/recovery_v3_dev_ood/generation_summary.json")
    if not path.exists():
        return
    summary = json.loads(path.read_text())
    assert summary["development_status"] == "DEVELOPMENT_ONLY"
    assert summary["gate_f_records_accessed"] == 0
    for counts in summary["action_distribution"].values():
        assert len(counts) == 6
        assert len(set(counts.values())) == 1
