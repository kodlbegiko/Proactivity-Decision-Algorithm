from __future__ import annotations

import random
import statistics
from collections import Counter
from typing import Any

from .candidate_v12 import ACTIONS, ACT_CRITICAL, FIELD_ORDER, ArchitectureA, ArchitectureB, ArchitectureC, policy_action
from .candidate_v12_dev import macro_f1, state_for_action
from .candidate_v12_frames import ArchitectureD


# Independent realization grammar for the compositional phase. It deliberately
# combines factor concepts and predicates that Architecture C never saw as full
# phrases. Parser and generator share the public ontology, but not sentence
# templates or complete realization strings.
CONCEPTS: dict[str, tuple[str, ...]] = {
    "permission": ("authorization", "clearance", "approval"),
    "information": ("evidence", "record", "reports"),
    "urgency": ("priority", "timing", "deadline"),
    "need": ("requirement", "intervention", "handling"),
    "side_effect": ("operation", "write", "change"),
    "risk": ("exposure", "hazard", "risk"),
    "reversibility": ("rollback", "reversibility", "undo"),
    "deferral_available": ("postponement", "deferral", "delay"),
    "execution_possible": ("execution", "tooling", "operation"),
    "clarification_possible": ("inquiry", "clarification", "question"),
    "acknowledged": ("awareness", "notice", "acknowledgement"),
    "completed": ("status", "case", "work"),
}

CUES: dict[str, dict[Any, tuple[str, ...]]] = {
    "permission": {"granted": ("secured", "issued", "confirmed"), "missing": ("withheld", "revoked", "absent"), "not_required": ("exempt", "waived")},
    "information": {"sufficient": ("adequate", "settled", "complete"), "insufficient": ("lacking", "incomplete", "missing"), "contradictory": ("conflicting", "inconsistent", "contradictory")},
    "urgency": {"none": ("flexible", "routine", "nonurgent"), "normal": ("standard", "ordinary", "normal"), "high": ("immediate", "pressing", "time-sensitive"), "expired": ("closed", "overdue", "expired")},
    "need": {"none": ("unnecessary",), "optional": ("elective", "discretionary", "optional"), "material": ("mandatory", "necessary", "material")},
    "side_effect": {"none": ("read-only", "informational"), "local": ("internal", "local"), "external": ("cross-system", "external")},
    "risk": {"low": ("small", "minimal", "low"), "medium": ("moderate", "meaningful", "medium"), "high": ("substantial", "severe", "high")},
    "reversibility": {"reversible": ("available", "possible", "undoable"), "irreversible": ("unavailable", "impossible", "irreversible")},
    "deferral_available": {True: ("feasible", "available", "allowed"), False: ("prohibited", "unavailable", "blocked")},
    "execution_possible": {True: ("ready", "feasible", "available"), False: ("blocked", "infeasible", "unavailable")},
    "clarification_possible": {True: ("available", "allowed", "feasible"), False: ("blocked", "forbidden", "unavailable")},
    "acknowledged": {True: ("confirmed", "noted", "acknowledged"), False: ("unseen", "unnoticed", "unacknowledged")},
    "completed": {True: ("finished", "closed", "resolved"), False: ("open", "ongoing", "unfinished")},
}

TRAIN_TEMPLATES = (
    "The {concept} status is {cue}",
    "For {concept}, the current value is {cue}",
    "Current {concept}: {cue}",
)
HOLDOUT_TEMPLATES = (
    "Regarding {concept}, the status now reads {cue}",
    "Operationally, {concept} remains {cue}",
    "At present the {concept} condition is {cue}",
)
STRESS_TEMPLATES = (
    "After reviewing unrelated context, the only decision-relevant point about {concept} is that it is {cue}",
    "Despite the surrounding narrative, treat {concept} as {cue} for the current decision",
)
DISTRACTORS = (
    "The project codename is Meridian",
    "A dashboard refresh happened yesterday",
    "Maria moved a meeting to another room",
    "The attachment contains seven charts",
    "A historical note mentions a different workflow",
)


def _factor_sentence(factor: str, value: Any, r: random.Random, templates: tuple[str, ...]) -> str:
    return r.choice(templates).format(concept=r.choice(CONCEPTS[factor]), cue=r.choice(CUES[factor][value]))


def realize_compositional(state: dict[str, Any], r: random.Random, *, split: str = "holdout", long_context: bool = False) -> str:
    templates = TRAIN_TEMPLATES if split == "train" else HOLDOUT_TEMPLATES if split == "holdout" else STRESS_TEMPLATES
    clauses = [_factor_sentence(f, state[f], r, templates) for f in FIELD_ORDER]
    r.shuffle(clauses)
    if long_context:
        for _ in range(5):
            clauses.insert(r.randrange(len(clauses) + 1), r.choice(DISTRACTORS))
    return ". ".join(clauses) + "."


def make_compositional_records(seed: int, n: int, *, split: str = "holdout", long_context: bool = False) -> list[dict[str, Any]]:
    r = random.Random(seed)
    targets = list(ACTIONS)
    r.shuffle(targets)
    out = []
    for i in range(n):
        if i and i % 6 == 0:
            r.shuffle(targets)
        action = targets[i % 6]
        state = state_for_action(r, action)
        out.append({
            "id": f"v12-advanced-{split}-{seed}-{i}",
            "state": state,
            "action": action,
            "text": realize_compositional(state, r, split=split, long_context=long_context),
            "semantic_seed": seed,
            "realization_seed": seed * 100000 + i,
        })
    return out


def evaluate_architecture(architecture: Any, records: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = [architecture.parse(x["text"]) for x in records]
    truth_actions = [x["action"] for x in records]
    pred_actions = [x.action for x in parsed]
    n = len(records)
    factor_accuracy = {f: sum(p.state[f] == x["state"][f] for p, x in zip(parsed, records)) / n for f in FIELD_ORDER}
    tp = sum(a == p == "ACT" for a, p in zip(truth_actions, pred_actions))
    fp = sum(a != "ACT" and p == "ACT" for a, p in zip(truth_actions, pred_actions))
    fn = sum(a == "ACT" and p != "ACT" for a, p in zip(truth_actions, pred_actions))
    return {
        "architecture": architecture.name,
        "macro_f1": macro_f1(truth_actions, pred_actions),
        "exact_latent_state_reconstruction": sum(p.state == x["state"] for p, x in zip(parsed, records)) / n,
        "mean_factor_accuracy": sum(factor_accuracy.values()) / len(FIELD_ORDER),
        "act_critical_factor_accuracy": sum(factor_accuracy[f] for f in ACT_CRITICAL) / len(ACT_CRITICAL),
        "factor_accuracy": factor_accuracy,
        "act_precision": tp / (tp + fp) if tp + fp else 0.0,
        "act_recall": tp / (tp + fn) if tp + fn else 0.0,
        "forbidden_act": fp,
        "invalid_action": sum(p.action not in ACTIONS for p in parsed),
        "action_distribution": dict(Counter(pred_actions)),
    }


def conditional_probe() -> bool:
    text = "If authorization is secured, the requirement becomes mandatory. Authorization is withheld. Requirement is elective. Operation is internal."
    p = ArchitectureD().parse(text)
    return p.state["permission"] == "missing" and p.state["need"] == "optional"


def double_negation_probe() -> bool:
    p = ArchitectureD().parse("Approval is not not granted. Evidence is not not adequate. Requirement is not not mandatory.")
    return p.state["permission"] == "granted" and p.state["information"] == "sufficient" and p.state["need"] == "material"


def temporal_probe() -> bool:
    text = "Previously, exposure was substantial. Currently, exposure is small. Earlier, authorization was withheld. At present, authorization is secured."
    p = ArchitectureD().parse(text)
    return p.state["risk"] == "low" and p.state["permission"] == "granted"


def contradiction_probe() -> bool:
    p = ArchitectureD().parse("Exposure is small. Risk is substantial. Authorization is secured. Approval is withheld.")
    return p.factors["risk"].epistemic_status == "CONTRADICTED" and p.state["risk"] == "high" and p.factors["permission"].epistemic_status == "CONTRADICTED" and p.state["permission"] == "missing" and p.action != "ACT"


def entity_binding_probe() -> bool:
    text = "Atlas: authorization is secured. Boreal: authorization is withheld. Atlas: exposure is small. Boreal: exposure is substantial."
    p = ArchitectureD().parse(text, target="Atlas")
    return p.state["permission"] == "granted" and p.state["risk"] == "low"


def cancellation_probe() -> bool:
    p = ArchitectureD().parse("The case is canceled. The handling requirement is mandatory.")
    return p.state["completed"] is True and p.state["need"] == "none" and p.action == "IGNORE"


def preference_probe() -> bool:
    p = ArchitectureD().parse("The user prefers no intervention. The handling requirement is mandatory.")
    return p.state["need"] == "none"


def missingness_probe() -> bool:
    p = ArchitectureD().parse("Exposure is small. The timing is standard.")
    return p.factors["permission"].epistemic_status == "UNKNOWN" and p.factors["information"].epistemic_status == "UNKNOWN"


def modality_probe() -> bool:
    p = ArchitectureD().parse("Authorization may be secured. Evidence might be adequate. Exposure is small.")
    return p.factors["permission"].epistemic_status == "UNKNOWN" and p.factors["information"].epistemic_status == "UNKNOWN" and p.state["risk"] == "low"


def dependency_probe() -> bool:
    p = ArchitectureD().parse("Execution depends on authorization. Authorization is withheld. Requirement is mandatory.")
    return p.state["permission"] == "missing" and p.state["execution_possible"] is False and p.factors["execution_possible"].epistemic_status == "INFERRED"


def state_to_action_sufficiency(seed: int = 17001, n: int = 4000) -> dict[str, Any]:
    r = random.Random(seed)
    observed: dict[tuple[Any, ...], str] = {}
    conflicts = 0
    invalid = 0
    for _ in range(n):
        action = r.choice(ACTIONS)
        state = state_for_action(r, action)
        key = tuple(state[f] for f in FIELD_ORDER)
        current = policy_action(state)
        invalid += current not in ACTIONS
        if key in observed and observed[key] != current:
            conflicts += 1
        observed[key] = current
    return {"states_checked": n, "unique_states": len(observed), "conflicting_equal_states": conflicts, "invalid_action": invalid, "pass": conflicts == 0 and invalid == 0}


def operator_suite() -> dict[str, bool]:
    return {
        "conditional": conditional_probe(),
        "double_negation": double_negation_probe(),
        "temporal_supersession": temporal_probe(),
        "contradiction": contradiction_probe(),
        "entity_binding": entity_binding_probe(),
        "cancellation": cancellation_probe(),
        "user_preference": preference_probe(),
        "explicit_missingness": missingness_probe(),
        "uncertain_modality": modality_probe(),
        "dependency": dependency_probe(),
    }


def advanced_development_summary() -> dict[str, Any]:
    architectures = [ArchitectureA(), ArchitectureB(), ArchitectureC(), ArchitectureD()]
    comparison_records = make_compositional_records(17101, 720, split="train")
    comparison = [evaluate_architecture(a, comparison_records) for a in architectures]
    d = ArchitectureD()
    holdout_seeds = (17201, 17202, 17203, 17204, 17205)
    runs = [evaluate_architecture(d, make_compositional_records(s, 360, split="holdout")) for s in holdout_seeds]
    pooled_records = sum((make_compositional_records(s, 360, split="holdout") for s in holdout_seeds), [])
    pooled = evaluate_architecture(d, pooled_records)
    stress = evaluate_architecture(d, make_compositional_records(17301, 720, split="stress", long_context=True))
    mf1 = [x["macro_f1"] for x in runs]
    return {
        "comparison": comparison,
        "holdout": pooled,
        "robustness": {"seeds": list(holdout_seeds), "mean": statistics.mean(mf1), "median": statistics.median(mf1), "minimum": min(mf1), "maximum": max(mf1), "standard_deviation": statistics.pstdev(mf1)},
        "stress": stress,
        "operators": operator_suite(),
        "state_to_action_sufficiency": state_to_action_sufficiency(),
    }
