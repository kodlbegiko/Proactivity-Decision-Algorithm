from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from candidate_v11.model import CandidateArchitecture

EXPECTED_PUBLIC_FIELDS = (
    "architecture",
    "beliefs",
    "policy_state",
    "action",
    "blocked_factors",
    "contradiction_detected",
    "invalid_state",
)

EXPECTED_FACTORS = (
    "permission",
    "information",
    "urgency",
    "need",
    "side_effect",
    "risk",
    "reversibility",
    "deferral_available",
    "execution_possible",
    "clarification_possible",
    "acknowledged",
    "completed",
)

VALID_ACTIONS = {"IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT"}


@dataclass(frozen=True)
class CanonicalPrediction:
    action: str
    factors: dict[str, object]
    belief_resolution: dict[str, str]
    contradiction_detected: bool
    invalid_state: bool
    public_field_names: tuple[str, ...]


def _resolution_name(value: Any) -> str:
    resolution = getattr(value, "resolution", None)
    raw = getattr(resolution, "value", resolution)
    return str(raw) if raw is not None else "unknown"


def adapt_prediction(prediction: Any) -> CanonicalPrediction:
    missing = [name for name in EXPECTED_PUBLIC_FIELDS if not hasattr(prediction, name)]
    if missing:
        raise TypeError(f"Candidate public prediction is missing fields: {missing}")

    action = str(prediction.action)
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid candidate action: {action}")

    state = prediction.policy_state
    if not isinstance(state, Mapping):
        raise TypeError("prediction.policy_state must be a mapping")
    factors = {factor: state.get(factor) for factor in EXPECTED_FACTORS}

    beliefs = prediction.beliefs
    if not isinstance(beliefs, Mapping):
        raise TypeError("prediction.beliefs must be a mapping")
    belief_resolution = {
        factor: _resolution_name(beliefs.get(factor)) for factor in EXPECTED_FACTORS
    }

    return CanonicalPrediction(
        action=action,
        factors=factors,
        belief_resolution=belief_resolution,
        contradiction_detected=bool(prediction.contradiction_detected),
        invalid_state=bool(prediction.invalid_state),
        public_field_names=tuple(EXPECTED_PUBLIC_FIELDS),
    )


class CandidateV11Adapter:
    """Evaluator-side compatibility adapter only; it does not alter Candidate semantics."""

    def __init__(self) -> None:
        self._candidate = CandidateArchitecture("V11-A")

    def predict(self, text: str) -> CanonicalPrediction:
        if not isinstance(text, str):
            raise TypeError("Candidate-v11 input must be text")
        return adapt_prediction(self._candidate.predict(text))
