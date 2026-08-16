from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any

CRITICAL = ("permission", "information", "need", "risk", "reversibility", "execution_possible", "side_effect")

@dataclass(frozen=True)
class ActGateResult:
    eligible: bool
    reasons: tuple[str, ...]


def act_eligibility_gate(state: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]], *, ood_score: float, ood_threshold: float = 0.15) -> ActGateResult:
    """ACT is opt-in by positive evidence; absence of a veto is never sufficient."""
    reasons: list[str] = []
    for factor in CRITICAL:
        item = evidence.get(factor, {})
        if item.get("status") != "SUPPORTED" or not item.get("positive_evidence"):
            reasons.append(f"{factor}:not_positively_supported")
        if item.get("contradiction_score", 0.0) > 0:
            reasons.append(f"{factor}:contradiction")
    if ood_score > ood_threshold:
        reasons.append("ood_unsafe")
    if state.get("information") != "sufficient": reasons.append("information_not_sufficient")
    if state.get("need") != "material": reasons.append("need_not_material")
    if state.get("risk") != "low": reasons.append("risk_not_low")
    if state.get("reversibility") != "reversible": reasons.append("not_reversible")
    if state.get("execution_possible") is not True: reasons.append("execution_not_possible")
    if state.get("completed") is True: reasons.append("already_completed")
    side = state.get("side_effect")
    perm = state.get("permission")
    if side == "external" and perm != "granted": reasons.append("external_permission_not_granted")
    if side == "local" and perm not in ("not_required", "granted"): reasons.append("local_permission_missing")
    if side == "none": reasons.append("no_material_side_effect")
    return ActGateResult(not reasons, tuple(sorted(set(reasons))))
