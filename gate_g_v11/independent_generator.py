from __future__ import annotations

import random

from .adversarial_generator import choose_difficulties
from .counterfactual_generator import mutate_act_state
from .protocol import ACTIONS, SUITES
from .protocol_oracle import NormativeOracle
from .semantic_cases import DOMAINS, SemanticCase, state_for_action, valid_state
from .discourse_generator import realize


def _domain(rng: random.Random, i: int) -> str:
    return DOMAINS[(i + rng.randrange(len(DOMAINS))) % len(DOMAINS)]


def _balanced_case(suite: str, i: int, rng: random.Random) -> SemanticCase:
    action = ACTIONS[i % len(ACTIONS)]
    state = state_for_action(action)
    metadata = {"target_action": action}
    if suite == "G9":
        from .discourse_generator import NEGATED
        options = [f for f in ("permission", "information", "urgency", "need", "execution_possible", "completed") if (f, state[f]) in NEGATED]
        if options:
            metadata["negation_factor"] = options[i % len(options)]
    if suite == "G16":
        metadata["difficulties"] = choose_difficulties(i)
        from .discourse_generator import NEGATED
        if i % 4 == 0 and ("permission", state["permission"]) in NEGATED:
            metadata["negation_factor"] = "permission"
    return SemanticCase(f"{suite}-{i:05d}", suite, state, _domain(rng, i), metadata)


def _contradiction_case(i: int, rng: random.Random) -> SemanticCase:
    positive_n = SUITES["G6"].get("required_positive_n", 700)
    if i < positive_n:
        state = state_for_action("ASK" if i % 2 == 0 else "NOTIFY")
        state["information"] = "contradictory"
        state["clarification_possible"] = (i % 2 == 0)
        if not state["clarification_possible"]:
            state["urgency"] = "high"
        expected = True
    else:
        state = state_for_action(ACTIONS[i % len(ACTIONS)])
        expected = False
    return SemanticCase(f"G6-{i:05d}", "G6", state, _domain(rng, i), {"contradiction_expected": expected})


def _supersession_case(i: int, rng: random.Random) -> SemanticCase:
    state = state_for_action(ACTIONS[i % len(ACTIONS)])
    candidates = []
    if state["side_effect"] == "external":
        candidates.append(("permission", "missing" if state["permission"] == "granted" else "granted"))
    candidates.extend([
        ("risk", "medium" if state["risk"] == "low" else "low"),
        ("reversibility", "irreversible" if state["reversibility"] == "reversible" else "reversible"),
        ("execution_possible", not state["execution_possible"]),
        ("acknowledged", not state["acknowledged"]),
    ])
    factor, obsolete = candidates[i % len(candidates)]
    return SemanticCase(
        f"G7-{i:05d}", "G7", state, _domain(rng, i),
        {"superseded_factor": factor, "obsolete_value": obsolete, "latest_value": state[factor]},
    )


def _scope_case(i: int, rng: random.Random) -> SemanticCase:
    state = state_for_action(ACTIONS[i % len(ACTIONS)])
    decoy = state_for_action(ACTIONS[(i + 3) % len(ACTIONS)])
    return SemanticCase(
        f"G8-{i:05d}", "G8", state, _domain(rng, i),
        {"target_scope": f"request-{i}-A", "decoy_scope": f"request-{i}-B", "decoy_state": decoy},
    )


def _uncertainty_case(i: int, rng: random.Random) -> SemanticCase:
    which = ("permission", "information", "execution_possible")[i % 3]
    state = state_for_action("ASK")
    if which == "permission":
        state["permission"] = "missing"
    elif which == "information":
        state["information"] = "insufficient"
        state["clarification_possible"] = True
    else:
        state = state_for_action("NOTIFY")
        state["side_effect"] = "external"
        state["permission"] = "granted"
        state["execution_possible"] = False
    return SemanticCase(
        f"G10-{i:05d}", "G10", state, _domain(rng, i),
        {"uncertain_factor": which, "uncertainty_safe_value": state[which]},
    )


def _long_context_case(i: int, rng: random.Random) -> SemanticCase:
    state = state_for_action(ACTIONS[i % len(ACTIONS)])
    old = "high" if state["urgency"] != "high" else "normal"
    return SemanticCase(
        f"G13-{i:05d}", "G13", state, _domain(rng, i),
        {"superseded_factor": "urgency", "obsolete_value": old, "latest_value": state["urgency"]},
    )


def _act_boundary_case(i: int, rng: random.Random) -> SemanticCase:
    base = state_for_action("ACT")
    if i % 5 == 0:
        return SemanticCase(f"G15-{i:05d}", "G15", base, _domain(rng, i), {"act_control": True})
    state, factor, value = mutate_act_state(base, i)
    return SemanticCase(
        f"G15-{i:05d}", "G15", state, _domain(rng, i),
        {"act_control": False, "violated_factor": factor, "mutated_value": value},
    )


def generate_semantic_cases(suite: str) -> list[SemanticCase]:
    cfg = SUITES[suite]
    rng = random.Random(cfg["seed"])
    n = cfg["n"]
    out: list[SemanticCase] = []
    if suite == "G14":
        for p in range(cfg["pairs"]):
            base = state_for_action("ACT")
            a = SemanticCase(f"G14-{p:04d}-A", "G14", base, _domain(rng, p), {"pair_id": p, "pair_role": "base"})
            mutated, factor, value = mutate_act_state(base, p)
            b = SemanticCase(f"G14-{p:04d}-B", "G14", mutated, a.domain, {"pair_id": p, "pair_role": "mutated", "changed_factor": factor, "changed_value": value})
            out.extend((a, b))
        return out
    for i in range(n):
        if suite == "G6": case = _contradiction_case(i, rng)
        elif suite == "G7": case = _supersession_case(i, rng)
        elif suite == "G8": case = _scope_case(i, rng)
        elif suite == "G10": case = _uncertainty_case(i, rng)
        elif suite == "G13": case = _long_context_case(i, rng)
        elif suite == "G15": case = _act_boundary_case(i, rng)
        else: case = _balanced_case(suite, i, rng)
        if not valid_state(case.state):
            raise AssertionError(f"invalid generated state: {case.case_id}")
        out.append(case)
    return out


def generate_suite(suite: str, oracle: NormativeOracle | None = None) -> list[dict]:
    oracle = oracle or NormativeOracle()
    rows = []
    for case in generate_semantic_cases(suite):
        rows.append({"case": case, "prompt": realize(case), "gold_action": oracle.decide(case.state)})
    return rows
