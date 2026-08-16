from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .protocol import FACTORS

DOMAINS = (
    "healthcare administration", "school administration", "travel logistics",
    "finance operations", "software deployment", "household coordination",
    "legal-document workflow", "event scheduling", "commerce order processing",
    "account security operations",
)

@dataclass(frozen=True)
class SemanticCase:
    case_id: str
    suite: str
    state: dict[str, Any]
    domain: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def serializable(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "suite": self.suite,
            "state": {k: self.state[k] for k in FACTORS},
            "domain": self.domain,
            "metadata": self.metadata,
        }


def state_for_action(action: str) -> dict[str, Any]:
    base = {
        "permission": "not_required",
        "information": "sufficient",
        "urgency": "none",
        "need": "none",
        "side_effect": "none",
        "risk": "low",
        "reversibility": "reversible",
        "deferral_available": False,
        "execution_possible": True,
        "clarification_possible": True,
        "acknowledged": False,
        "completed": False,
    }
    if action == "IGNORE":
        return base
    if action == "WAIT":
        base["deferral_available"] = True
        return base
    if action == "SUGGEST":
        base["need"] = "optional"
        base["urgency"] = "normal"
        return base
    if action == "NOTIFY":
        base["need"] = "material"
        base["urgency"] = "high"
        return base
    if action == "ASK":
        base.update({
            "permission": "missing", "side_effect": "external", "need": "material",
            "urgency": "normal", "information": "sufficient",
        })
        return base
    if action == "ACT":
        base.update({
            "permission": "granted", "side_effect": "external", "need": "material",
            "urgency": "normal", "information": "sufficient", "risk": "low",
            "reversibility": "reversible", "execution_possible": True,
        })
        return base
    raise ValueError(action)


def valid_state(state: dict[str, Any]) -> bool:
    if state["side_effect"] == "external" and state["permission"] == "not_required":
        return False
    if state["side_effect"] == "none" and state["permission"] != "not_required":
        return False
    return True
