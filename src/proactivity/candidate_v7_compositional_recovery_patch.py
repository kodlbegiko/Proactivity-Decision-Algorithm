"""Candidate-v7 infrastructure retry 003: feasible compositional partition.

The original deterministic hash bucket was discovered, before any evaluation
metric existed, to contain no ACT formal states. This repair defines the
compositional holdout using a generator-known conjunction of three independent
boolean primitives. Train/validation exclude this conjunction; the
compositional holdout contains it. No natural-language example, validation
score, or qualification score is consulted.
"""

from . import candidate_v7_data as _data


def _composition_signature_feasible(state):
    held_out_conjunction = (
        state["clarification_possible"] is True
        and state["acknowledged"] is True
        and state["deferral_available"] is True
    )
    if held_out_conjunction:
        return 0
    return 1 + (_data.stable_int(
        state["permission"], state["information"], state["risk"],
        state["need"], state["side_effect"], state["urgency"],
    ) % 6)


_data.composition_signature = _composition_signature_feasible
