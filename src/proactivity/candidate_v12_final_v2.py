from __future__ import annotations

import statistics

from .candidate_v12 import ArchitectureA, ArchitectureB, ArchitectureC
from .candidate_v12_frames import ArchitectureD
from . import candidate_v12_final_dev as base

# Methodological correction after the first final harness exposed a syntactic
# collision between `Current factor: value` and the parser's explicit
# `Entity: clause` binding syntax.  The failed harness is retained unchanged.
# This v2 harness uses ambiguity-free templates and entirely fresh seeds.
POOL_A = (
    "The {concept} is {cue}",
    "For {concept}, mark it {cue}",
    "The current reading for {concept} is {cue}",
)
POOL_B = (
    "Regarding {concept}, it now reads {cue}",
    "Operationally, {concept} remains {cue}",
    "At present, {concept} is {cue}",
)
POOL_C = (
    "For the current decision, {concept} should be treated as {cue}",
    "After unrelated context, the decision-relevant value for {concept} is {cue}",
    "Ignoring background details, {concept} is {cue}",
)

# The base functions intentionally read their module-global pools.  Replacing
# only the three realization pools keeps the metric implementation identical
# while changing the fresh realization family.
base.POOL_A = POOL_A
base.POOL_B = POOL_B
base.POOL_C = POOL_C


def final_v2_summary() -> dict:
    d = ArchitectureD()
    comparison_records = base.make_records(20501, 720, pool=POOL_A)
    comparison = [base.evaluate(a, comparison_records) for a in (ArchitectureA(), ArchitectureB(), ArchitectureC(), d)]

    seeds = (20511, 20512, 20513, 20514, 20515)
    runs = [base.evaluate(d, base.make_records(s, 360, pool=POOL_B)) for s in seeds]
    pooled = base.evaluate(d, sum((base.make_records(s, 360, pool=POOL_B) for s in seeds), []))
    stress = base.evaluate(d, base.make_records(20521, 720, pool=POOL_C, distractors=5))
    macro = [x["macro_f1"] for x in runs]

    return {
        "methodology_revision": "fresh templates remove Entity:clause ambiguity; no parser or policy threshold change",
        "architecture_comparison": comparison,
        "holdout": pooled,
        "robustness": {
            "seeds": list(seeds),
            "mean": statistics.mean(macro),
            "median": statistics.median(macro),
            "minimum": min(macro),
            "maximum": max(macro),
            "standard_deviation": statistics.pstdev(macro),
        },
        "stress": stress,
        "unknown": base.unknown_metrics(seed=20601, n=360),
        "counterfactual": base.counterfactual_metrics(seed=20602, n=240),
        "invariance": base.invariance_metrics(seed=20603, n=300),
        "operators": base.operator_suite(),
        "mechanistic": base.mechanistic_diagnostics(seed=20604, n=180),
        "state_to_action_sufficiency": base.state_to_action_sufficiency(seed=20605, n=5000),
        "collision_audit": base.collision_audit(seed=20600, repetitions=24),
    }
