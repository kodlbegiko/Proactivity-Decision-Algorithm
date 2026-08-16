from __future__ import annotations

"""Gate-C generator remediation for preregistered observation-template dominance.

This module deliberately changes only the non-normative observation paraphrase
surface. It does not alter source states, the frozen specification, the oracle,
selection rules, gold actions, relation families, or preregistered thresholds.

The initial three-family deterministic hash allocation produced a 65/45/58
split over 168 records (largest share 38.69%), violating the preregistered
34% maximum. A fourth genuinely distinct paraphrase family changes the same
hash allocation to four-way sampling while preserving relation-family template
consistency. Gate-C CI must re-audit the resulting distribution; this module
does not waive or modify the criterion.
"""

from proactivity import benchmark_v2 as base

_EXTRA_PHRASE_FAMILY = {
    "permission": {
        "not_required": "Authorization is not part of the modeled requirement",
        "missing": "The needed authorization is still unavailable",
        "granted": "The needed authorization is already available",
    },
    "information": {
        "sufficient": "the evidence needed for this modeled choice is available",
        "insufficient": "some evidence needed for this modeled choice is unavailable",
        "contradictory": "the evidence needed for this modeled choice is internally inconsistent",
    },
    "urgency": {
        "none": "no present time pressure is modeled",
        "normal": "ordinary time pressure is modeled",
        "high": "strong time pressure is modeled",
        "expired": "the modeled timing window has passed",
    },
    "need": {
        "none": "no current intervention requirement is modeled",
        "optional": "only a discretionary intervention opportunity is modeled",
        "material": "a substantive intervention requirement is modeled",
    },
    "side_effect": {
        "none": "the modeled operation has no material side effect",
        "local": "the modeled operation has a material effect confined locally",
        "external": "the modeled operation has a material effect beyond the local system",
    },
    "risk": {
        "low": "the modeled risk level is low",
        "medium": "the modeled risk level is moderate",
        "high": "the modeled risk level is high",
    },
    "reversibility": {
        "reversible": "the modeled outcome can be rolled back",
        "irreversible": "the modeled outcome cannot be rolled back",
    },
    "deferral_available": {
        False: "there is no specified later trigger",
        True: "there is a specified later trigger",
    },
    "execution_possible": {
        False: "the modeled operation cannot presently be executed",
        True: "the modeled operation can presently be executed",
    },
    "clarification_possible": {
        False: "the unresolved context cannot presently be clarified",
        True: "the unresolved context can presently be clarified",
    },
    "acknowledged": {
        False: "no acknowledgement has been recorded",
        True: "an acknowledgement has been recorded",
    },
    "completed": {
        False: "the modeled task remains incomplete",
        True: "the modeled task has been completed",
    },
}


def activate() -> None:
    """Idempotently enable four-family observation sampling for Gate C."""
    if len(base.PHRASES) == 3:
        base.PHRASES = base.PHRASES + (_EXTRA_PHRASE_FAMILY,)
        return
    if len(base.PHRASES) == 4 and base.PHRASES[-1] == _EXTRA_PHRASE_FAMILY:
        return
    raise RuntimeError(f"unexpected benchmark_v2 PHRASES state: {len(base.PHRASES)} families")
