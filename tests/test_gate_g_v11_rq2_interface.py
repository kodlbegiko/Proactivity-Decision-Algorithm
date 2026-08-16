from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from candidate_v11.model import CandidateArchitecture, Prediction
from gate_g_v11_rq2.candidate_adapter import (
    CanonicalPrediction,
    EXPECTED_FACTORS,
    EXPECTED_PUBLIC_FIELDS,
    adapt_prediction,
)
from gate_g_v11_rq2.preflight import run_interface_sentinel, verify_candidate_freeze

ROOT = Path(__file__).resolve().parents[1]


def test_frozen_prediction_contract_declares_actual_public_fields():
    field_names = tuple(field.name for field in dataclasses.fields(Prediction))
    assert field_names == EXPECTED_PUBLIC_FIELDS
    assert "state" not in field_names
    assert "policy_state" in field_names


def test_candidate_initializes_and_adapter_accepts_runtime_output_without_scoring():
    candidate = CandidateArchitecture("V11-A")
    raw = candidate.predict("Interface-only schema probe; no gold label exists for this text.")
    canonical = adapt_prediction(raw)
    assert isinstance(canonical, CanonicalPrediction)
    assert canonical.action in {"IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT"}
    assert tuple(canonical.factors) == EXPECTED_FACTORS


def test_interface_sentinel_is_unscored_and_gold_free():
    result = run_interface_sentinel()
    assert result["performance_scoring_performed"] is False
    assert result["gold_labels_present"] is False
    assert len(result["sentinel_sha256"]) == 2


def test_candidate_freeze_blobs_are_exact():
    observed = verify_candidate_freeze()
    assert observed["candidate_v11/model.py"]["git_blob"] == "77553f7821113b48a2ffcd368ca23195853f8fb0"
    assert observed["candidate_v11/evidence.py"]["git_blob"] == "9f5338e0317bdababc8fbd6c2ebf3e499ac4ce42"
    assert observed["spec/proactivity_policy_v2.json"]["git_blob"] == "e34345bf76179d2c989d9da2effaa013792925fe"


def test_interface_contract_forbids_scoring_and_row_inspection():
    contract = json.loads((ROOT / "gate_g_v11_rq2/interface_contract.json").read_text())
    assert contract["performance_scoring_performed"] is False
    assert contract["historical_protected_rows_inspected"] is False
    assert contract["historical_development_rows_inspected"] is False
    assert contract["previous_gate_g_rows_inspected"] is False
    assert contract["structured_state_source"] == "policy_state"
