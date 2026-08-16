from __future__ import annotations

from dataclasses import dataclass
import random
import statistics
from collections import Counter
from typing import Any

from .candidate_v12 import (
    ACTIONS,
    ACT_CRITICAL,
    FIELD_ORDER,
    ArchitectureA,
    ArchitectureB,
    ArchitectureC,
    Evidence,
    ParseResult,
    policy_action,
    resolve_state,
)
from .candidate_v12_dev import macro_f1, state_for_action
from .candidate_v12_frames import (
    ArchitectureD,
    ArchitectureDNoOperators,
    _apply_contradiction_safety,
    _apply_dependency_semantics,
    extract_frame_evidence,
)

# Fresh, collision-audited realization vocabulary.  Factor concepts are unique
# across factors; predicates may repeat because they are interpreted only under
# an explicitly bound factor concept.
CONCEPTS: dict[str, tuple[str, ...]] = {
    "permission": ("authorization", "clearance", "approval"),
    "information": ("evidence", "record", "reports"),
    "urgency": ("priority", "timing", "deadline"),
    "need": ("requirement", "intervention", "handling"),
    "side_effect": ("side effect", "write", "effect"),
    "risk": ("exposure", "hazard", "risk"),
    "reversibility": ("rollback", "reversibility", "undo"),
    "deferral_available": ("postponement", "deferral", "delay"),
    "execution_possible": ("execution", "tooling", "perform"),
    "clarification_possible": ("inquiry", "clarification", "question"),
    "acknowledged": ("awareness", "notice", "acknowledgement"),
    "completed": ("status", "case", "work"),
}

CUES: dict[str, dict[Any, tuple[str, ...]]] = {
    "permission": {
        "granted": ("secured", "issued", "confirmed"),
        "missing": ("withheld", "revoked", "absent"),
        "not_required": ("exempt", "waived"),
    },
    "information": {
        "sufficient": ("adequate", "settled", "complete"),
        "insufficient": ("lacking", "incomplete", "missing"),
        "contradictory": ("conflicting", "inconsistent", "contradictory"),
    },
    "urgency": {
        "none": ("flexible", "routine", "nonurgent"),
        "normal": ("standard", "ordinary", "normal"),
        "high": ("immediate", "pressing", "time-sensitive"),
        "expired": ("closed", "overdue", "expired"),
    },
    "need": {
        "none": ("unnecessary",),
        "optional": ("elective", "discretionary", "optional"),
        "material": ("mandatory", "necessary", "material"),
    },
    "side_effect": {
        "none": ("read-only", "informational"),
        "local": ("internal", "local"),
        "external": ("cross-system", "external"),
    },
    "risk": {
        "low": ("small", "minimal", "low"),
        "medium": ("moderate", "meaningful", "medium"),
        "high": ("substantial", "severe", "high"),
    },
    "reversibility": {
        "reversible": ("available", "possible", "undoable"),
        "irreversible": ("unavailable", "impossible", "irreversible"),
    },
    "deferral_available": {
        True: ("feasible", "available", "allowed"),
        False: ("prohibited", "unavailable", "blocked"),
    },
    "execution_possible": {
        True: ("ready", "feasible", "available"),
        False: ("blocked", "infeasible", "unavailable"),
    },
    "clarification_possible": {
        True: ("available", "allowed", "feasible"),
        False: ("blocked", "forbidden", "unavailable"),
    },
    "acknowledged": {
        True: ("confirmed", "noted", "acknowledged"),
        False: ("unseen", "unnoticed", "unacknowledged"),
    },
    "completed": {
        True: ("finished", "closed", "resolved"),
        False: ("open", "ongoing", "unfinished"),
    },
}

POOL_A = (
    "The {concept} is {cue}",
    "For {concept}, mark it {cue}",
    "Current {concept}: {cue}",
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
DISTRACTORS = (
    "The project codename is Meridian",
    "A dashboard refresh happened yesterday",
    "Maria moved a meeting to another room",
    "The attachment contains seven charts",
    "A historical note mentions a different workflow",
    "The meeting room has twelve seats",
)


def _sentence(factor: str, value: Any, r: random.Random, pool: tuple[str, ...]) -> str:
    return r.choice(pool).format(concept=r.choice(CONCEPTS[factor]), cue=r.choice(CUES[factor][value]))


def collision_audit(seed: int = 19000, repetitions: int = 24) -> dict[str, Any]:
    r = random.Random(seed)
    failures: list[dict[str, Any]] = []
    for pool_name, pool in (("A", POOL_A), ("B", POOL_B), ("C", POOL_C)):
        for factor in FIELD_ORDER:
            for value in CUES[factor]:
                for _ in range(repetitions):
                    text = _sentence(factor, value, r, pool)
                    evidence = extract_frame_evidence(text)
                    factors = {e.factor for e in evidence}
                    values = {e.value for e in evidence if e.factor == factor}
                    if factors - {factor} or value not in values:
                        failures.append({"pool": pool_name, "factor": factor, "value": value, "factors": sorted(factors)})
                        if len(failures) >= 20:
                            return {"pass": False, "failures": failures}
    return {"pass": not failures, "failures": failures}


def realize(
    state: dict[str, Any],
    r: random.Random,
    *,
    pool: tuple[str, ...] = POOL_B,
    omit: str | None = None,
    distractors: int = 0,
) -> str:
    clauses = [_sentence(f, state[f], r, pool) for f in FIELD_ORDER if f != omit]
    r.shuffle(clauses)
    for _ in range(distractors):
        clauses.insert(r.randrange(len(clauses) + 1), r.choice(DISTRACTORS))
    return ". ".join(clauses) + "."


def make_records(seed: int, n: int, *, pool: tuple[str, ...] = POOL_B, distractors: int = 0) -> list[dict[str, Any]]:
    r = random.Random(seed)
    actions = list(ACTIONS)
    r.shuffle(actions)
    out: list[dict[str, Any]] = []
    for i in range(n):
        if i and i % len(ACTIONS) == 0:
            r.shuffle(actions)
        action = actions[i % len(ACTIONS)]
        state = state_for_action(r, action)
        out.append({
            "id": f"v12-final-{seed}-{i}",
            "state": state,
            "action": action,
            "text": realize(state, r, pool=pool, distractors=distractors),
            "semantic_seed": seed,
            "realization_seed": seed * 100000 + i,
        })
    return out


def evaluate(architecture: Any, records: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = [architecture.parse(x["text"]) for x in records]
    truth = [x["action"] for x in records]
    pred = [x.action for x in parsed]
    oracle = [policy_action(x["state"]) for x in records]
    n = len(records)
    fa = {f: sum(p.state[f] == x["state"][f] for p, x in zip(parsed, records)) / n for f in FIELD_ORDER}
    tp = sum(a == p == "ACT" for a, p in zip(truth, pred))
    fp = sum(a != "ACT" and p == "ACT" for a, p in zip(truth, pred))
    fn = sum(a == "ACT" and p != "ACT" for a, p in zip(truth, pred))
    pred_macro = macro_f1(truth, pred)
    oracle_macro = macro_f1(truth, oracle)
    unknown_all = sum(p.factors[f].epistemic_status == "UNKNOWN" for p in parsed for f in FIELD_ORDER)
    unknown_critical = sum(p.factors[f].epistemic_status == "UNKNOWN" for p in parsed for f in ACT_CRITICAL)
    return {
        "architecture": architecture.name,
        "examples": n,
        "macro_f1": pred_macro,
        "exact_latent_state_reconstruction": sum(p.state == x["state"] for p, x in zip(parsed, records)) / n,
        "mean_factor_accuracy": sum(fa.values()) / len(FIELD_ORDER),
        "factor_accuracy": fa,
        "act_critical_factor_accuracy": sum(fa[f] for f in ACT_CRITICAL) / len(ACT_CRITICAL),
        "critical_unknown_rate": unknown_critical / (n * len(ACT_CRITICAL)),
        "false_unknown_rate": unknown_all / (n * len(FIELD_ORDER)),
        "act_precision": tp / (tp + fp) if tp + fp else 0.0,
        "act_recall": tp / (tp + fn) if tp + fn else 0.0,
        "forbidden_act": fp,
        "invalid_action": sum(p.action not in ACTIONS for p in parsed),
        "action_distribution": dict(Counter(pred)),
        "policy_oracle_macro_f1": oracle_macro,
        "policy_oracle_gap": oracle_macro - pred_macro,
    }


def unknown_metrics(seed: int = 19601, n: int = 360) -> dict[str, Any]:
    r = random.Random(seed)
    d = ArchitectureD()
    legitimate = 0
    complete_unknown = 0
    complete_critical_unknown = 0
    total_complete = 0
    fields = list(FIELD_ORDER)
    for i in range(n):
        action = r.choice(ACTIONS)
        state = state_for_action(r, action)
        omit = fields[i % len(fields)]
        if omit == "permission" and state["side_effect"] == "none":
            state["side_effect"] = "local"
            state["permission"] = r.choice(("missing", "granted"))
        p = d.parse(realize(state, r, pool=POOL_C, omit=omit))
        legitimate += p.factors[omit].epistemic_status == "UNKNOWN"

        full = d.parse(realize(state, r, pool=POOL_B))
        complete_unknown += sum(full.factors[f].epistemic_status == "UNKNOWN" for f in FIELD_ORDER)
        complete_critical_unknown += sum(full.factors[f].epistemic_status == "UNKNOWN" for f in ACT_CRITICAL)
        total_complete += 1
    return {
        "legitimate_unknown_recall": legitimate / n,
        "false_unknown_rate": complete_unknown / (total_complete * len(FIELD_ORDER)),
        "critical_unknown_rate": complete_critical_unknown / (total_complete * len(ACT_CRITICAL)),
    }


def counterfactual_metrics(seed: int = 19602, n: int = 240) -> dict[str, Any]:
    r = random.Random(seed)
    d = ArchitectureD()
    exact = delta = transition = 0
    for _ in range(n):
        x = state_for_action(r, "ACT")
        x["side_effect"] = "external"
        x["permission"] = "granted"
        y = dict(x)
        y["permission"] = "missing"
        px = d.parse(realize(x, r, pool=POOL_B))
        py = d.parse(realize(y, r, pool=POOL_C))
        exact += px.state == x and py.state == y
        delta += (
            px.state["permission"] == "granted"
            and py.state["permission"] == "missing"
            and sum(px.state[f] != py.state[f] for f in FIELD_ORDER) == 1
        )
        transition += px.action == policy_action(x) and py.action == policy_action(y)
    return {
        "exact_pair_correctness": exact / n,
        "latent_factor_delta_correctness": delta / n,
        "action_transition_correctness": transition / n,
    }


def invariance_metrics(seed: int = 19603, n: int = 300) -> dict[str, Any]:
    r = random.Random(seed)
    d = ArchitectureD()
    state_same = action_same = correct = 0
    for _ in range(n):
        action = r.choice(ACTIONS)
        state = state_for_action(r, action)
        a = d.parse(realize(state, random.Random(r.randrange(10**9)), pool=POOL_A))
        b = d.parse(realize(state, random.Random(r.randrange(10**9)), pool=POOL_B))
        c = d.parse(realize(state, random.Random(r.randrange(10**9)), pool=POOL_C, distractors=3))
        state_same += a.state == b.state == c.state
        action_same += a.action == b.action == c.action
        correct += a.state == b.state == c.state == state and a.action == b.action == c.action == policy_action(state)
    return {
        "latent_state_invariance_consistency": state_same / n,
        "action_invariance_consistency": action_same / n,
        "correct_consistency": correct / n,
    }


def operator_suite() -> dict[str, bool]:
    d = ArchitectureD()
    conditional = d.parse("If authorization is secured, the requirement becomes mandatory. Authorization is withheld. Requirement is elective.")
    double_neg = d.parse("Approval is not not granted. Evidence is not not adequate. Requirement is not not mandatory.")
    temporal = d.parse("Previously, exposure was substantial. Currently, exposure is small. Earlier, authorization was withheld. At present, authorization is secured.")
    contradiction = d.parse("Exposure is small. Risk is substantial. Authorization is secured. Approval is withheld.")
    entity = d.parse("Atlas: authorization is secured. Boreal: authorization is withheld. Atlas: exposure is small. Boreal: exposure is substantial.", target="Atlas")
    cancellation = d.parse("The case is canceled. The handling requirement is mandatory.")
    preference = d.parse("The user prefers no intervention. The handling requirement is mandatory.")
    missing = d.parse("Exposure is small. The timing is standard.")
    modality = d.parse("Authorization may be secured. Evidence might be adequate. Exposure is small.")
    dependency = d.parse("Execution depends on authorization. Authorization is withheld. Requirement is mandatory.")
    return {
        "conditional": conditional.state["permission"] == "missing" and conditional.state["need"] == "optional",
        "double_negation": double_neg.state["permission"] == "granted" and double_neg.state["information"] == "sufficient" and double_neg.state["need"] == "material",
        "temporal_supersession": temporal.state["risk"] == "low" and temporal.state["permission"] == "granted",
        "contradiction": contradiction.factors["risk"].epistemic_status == "CONTRADICTED" and contradiction.state["risk"] == "high" and contradiction.state["permission"] == "missing" and contradiction.action != "ACT",
        "entity_binding": entity.state["permission"] == "granted" and entity.state["risk"] == "low",
        "cancellation": cancellation.state["completed"] is True and cancellation.state["need"] == "none" and cancellation.action == "IGNORE",
        "user_preference": preference.state["need"] == "none",
        "explicit_missingness": missing.factors["permission"].epistemic_status == "UNKNOWN" and missing.factors["information"].epistemic_status == "UNKNOWN",
        "uncertain_modality": modality.factors["permission"].epistemic_status == "UNKNOWN" and modality.factors["information"].epistemic_status == "UNKNOWN" and modality.state["risk"] == "low",
        "dependency": dependency.state["permission"] == "missing" and dependency.state["execution_possible"] is False and dependency.factors["execution_possible"].epistemic_status == "INFERRED",
        "generator_no_cross_factor_collision": collision_audit()["pass"],
    }


class _DNoTemporal(ArchitectureD):
    name = "D_ablation_no_temporal"
    def parse(self, text: str, target: str | None = None) -> ParseResult:
        ev = extract_frame_evidence(text, target=target)
        flat = [Evidence(e.factor, e.value, e.span, e.confidence, e.polarity, 10, e.explicit) for e in ev]
        state, factors = resolve_state(flat, joint_constraints=True, temporal=True)
        _apply_dependency_semantics(text, state, factors)
        _apply_contradiction_safety(state, factors)
        return ParseResult(state, factors, flat, policy_action(state), self.name)


class _DNoContradictionSafety(ArchitectureD):
    name = "D_ablation_no_contradiction_safety"
    def parse(self, text: str, target: str | None = None) -> ParseResult:
        ev = extract_frame_evidence(text, target=target)
        state, factors = resolve_state(ev, joint_constraints=True, temporal=True)
        _apply_dependency_semantics(text, state, factors)
        return ParseResult(state, factors, ev, policy_action(state), self.name)


def mechanistic_diagnostics(seed: int = 19604, n: int = 180) -> dict[str, Any]:
    r = random.Random(seed)
    full = ArchitectureD()
    no_temporal = _DNoTemporal()
    no_safe = _DNoContradictionSafety()

    temporal_full = temporal_ablated = 0
    contradiction_full = contradiction_ablated = 0
    for _ in range(n):
        latest = r.choice(("low", "high"))
        earlier = "high" if latest == "low" else "low"
        text = f"Previously, exposure was {'substantial' if earlier == 'high' else 'small'}. Currently, exposure is {'substantial' if latest == 'high' else 'small'}."
        temporal_full += full.parse(text).state["risk"] == latest
        temporal_ablated += no_temporal.parse(text).state["risk"] == latest

        text2 = "Exposure is small. Risk is substantial. Authorization is secured. Approval is withheld."
        f = full.parse(text2)
        a = no_safe.parse(text2)
        contradiction_full += f.state["risk"] == "high" and f.state["permission"] == "missing" and f.action != "ACT"
        contradiction_ablated += a.state["risk"] == "high" and a.state["permission"] == "missing" and a.action != "ACT"

    comp_records = make_records(seed + 1, 480, pool=POOL_C)
    d_exact = evaluate(full, comp_records)["exact_latent_state_reconstruction"]
    c_exact = evaluate(ArchitectureC(), comp_records)["exact_latent_state_reconstruction"]
    poor = ArchitectureDNoOperators()
    poor_exact = evaluate(poor, comp_records)["exact_latent_state_reconstruction"]
    return {
        "temporal": {"full": temporal_full / n, "ablated": temporal_ablated / n, "delta": (temporal_full - temporal_ablated) / n},
        "contradiction_safety": {"full": contradiction_full / n, "ablated": contradiction_ablated / n, "delta": (contradiction_full - contradiction_ablated) / n},
        "frame_composition": {"full_exact_state": d_exact, "lexical_c_exact_state": c_exact, "no_operator_exact_state": poor_exact, "delta_vs_c": d_exact - c_exact},
    }


def state_to_action_sufficiency(seed: int = 19605, n: int = 5000) -> dict[str, Any]:
    r = random.Random(seed)
    seen: dict[tuple[Any, ...], str] = {}
    conflicts = invalid = 0
    for _ in range(n):
        state = state_for_action(r, r.choice(ACTIONS))
        key = tuple(state[f] for f in FIELD_ORDER)
        action = policy_action(state)
        invalid += action not in ACTIONS
        if key in seen and seen[key] != action:
            conflicts += 1
        seen[key] = action
    return {"states_checked": n, "unique_states": len(seen), "conflicting_equal_states": conflicts, "invalid_action": invalid, "pass": conflicts == 0 and invalid == 0}


def final_development_summary() -> dict[str, Any]:
    d = ArchitectureD()
    comparison_records = make_records(19501, 720, pool=POOL_A)
    comparison = [evaluate(a, comparison_records) for a in (ArchitectureA(), ArchitectureB(), ArchitectureC(), d)]

    seeds = (19511, 19512, 19513, 19514, 19515)
    runs = [evaluate(d, make_records(s, 360, pool=POOL_B)) for s in seeds]
    pooled = evaluate(d, sum((make_records(s, 360, pool=POOL_B) for s in seeds), []))
    stress = evaluate(d, make_records(19521, 720, pool=POOL_C, distractors=5))
    macro = [x["macro_f1"] for x in runs]
    return {
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
        "unknown": unknown_metrics(),
        "counterfactual": counterfactual_metrics(),
        "invariance": invariance_metrics(),
        "operators": operator_suite(),
        "mechanistic": mechanistic_diagnostics(),
        "state_to_action_sufficiency": state_to_action_sufficiency(),
        "collision_audit": collision_audit(),
    }
