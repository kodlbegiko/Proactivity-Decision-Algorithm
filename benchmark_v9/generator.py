from __future__ import annotations

import json
import random
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

from candidate_v9.policy import ACTIONS, enumerate_states, oracle_action, valid_state
from .render_inventory import FAMILY_INDEXES, NEGATION_OVERRIDES, PHRASES

def _choice_for_family(field: str, value: Any, family: str, rng: random.Random) -> str:
    pool = PHRASES[field][value]
    indexes = FAMILY_INDEXES.get(family, FAMILY_INDEXES["validation"])
    return pool[rng.choice(indexes)]


@lru_cache(maxsize=1)
def valid_states_by_action() -> dict[str, tuple[dict[str, Any], ...]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for state in enumerate_states(valid_only=True):
        grouped[oracle_action(state)].append(state)
    return {action: tuple(grouped[action]) for action in ACTIONS}


def balanced_states(n: int, seed: int) -> list[dict[str, Any]]:
    if n % len(ACTIONS):
        raise ValueError("balanced dataset size must be divisible by six")
    rng = random.Random(seed)
    grouped = valid_states_by_action()
    rows: list[dict[str, Any]] = []
    each = n // len(ACTIONS)
    for action in ACTIONS:
        source = grouped[action]
        for _ in range(each):
            rows.append(dict(rng.choice(source)))
    rng.shuffle(rows)
    return rows


def render_state(
    state: dict[str, Any],
    family: str,
    rng: random.Random,
    *,
    shuffle: bool = True,
    narrative: bool = False,
    omit: set[str] | None = None,
    negation_mode: bool = False,
) -> str:
    omit = omit or set()
    clauses: list[str] = []
    for field, value in state.items():
        if field in omit:
            continue
        if negation_mode and (field, value) in NEGATION_OVERRIDES:
            phrase = NEGATION_OVERRIDES[(field, value)]
        else:
            phrase = _choice_for_family(field, value, family, rng)
        clauses.append(phrase)
    if shuffle:
        rng.shuffle(clauses)
    if narrative:
        connectors = ("In context, ", "Separately, ", "Operationally, ", "For the current decision, ")
        clauses = [connectors[i % len(connectors)] + clause[0].lower() + clause[1:] for i, clause in enumerate(clauses)]
    return " ".join(clauses)


def make_dataset(n: int, seed: int, family: str, prefix: str, *, narrative: bool = False) -> list[dict[str, Any]]:
    rng = random.Random(seed + 37)
    rows = []
    for i, state in enumerate(balanced_states(n, seed)):
        rows.append({
            "id": f"{prefix}-{i:05d}",
            "text": render_state(state, family, rng, shuffle=True, narrative=narrative),
            "state": state,
            "action": oracle_action(state),
        })
    return rows


def _wrong_value(field: str, current: Any, rng: random.Random) -> Any:
    values = list(PHRASES[field])
    return rng.choice([value for value in values if value != current])


def make_supersession(n: int, seed: int, family: str = "validation") -> list[dict[str, Any]]:
    base = make_dataset(n, seed, family, "supersession")
    rng = random.Random(seed + 71)
    fields = list(PHRASES)
    for row in base:
        chosen = rng.sample(fields, k=3)
        earlier = []
        for field in chosen:
            wrong = _wrong_value(field, row["state"][field], rng)
            phrase = _choice_for_family(field, wrong, family, rng)
            earlier.append("Earlier, " + phrase[0].lower() + phrase[1:])
        row["text"] = " ".join(earlier) + " " + row["text"]
        row["superseded_fields"] = chosen
    return base


def make_state_validity_stress(n: int, seed: int, family: str = "validation") -> list[dict[str, Any]]:
    base = make_dataset(n if n % 6 == 0 else n + (6 - n % 6), seed, family, "state-validity")[:n]
    rng = random.Random(seed + 83)
    for row in base:
        target = row["state"]
        if target["side_effect"] == "none":
            bad_p, bad_s = "granted", "none"
        else:
            bad_p, bad_s = "not_required", "external"
        p = _choice_for_family("permission", bad_p, family, rng)
        s = _choice_for_family("side_effect", bad_s, family, rng)
        row["text"] = f"Earlier, {p[0].lower()+p[1:]} Earlier, {s[0].lower()+s[1:]} " + row["text"]
        row["attack_pair"] = {"permission": bad_p, "side_effect": bad_s}
    return base


def make_joint_constraint(n: int, seed: int, family: str = "validation") -> list[dict[str, Any]]:
    # Same attack class as validity stress but with explicit latest target pair.
    base = make_state_validity_stress(n, seed, family)
    rng = random.Random(seed + 97)
    for row in base:
        target = row["state"]
        p = _choice_for_family("permission", target["permission"], family, rng)
        s = _choice_for_family("side_effect", target["side_effect"], family, rng)
        row["text"] += f" Final status: {p[0].lower()+p[1:]} {s}"
    return base


def make_act_boundary(n: int, seed: int, family: str = "validation") -> list[dict[str, Any]]:
    rng = random.Random(seed)
    act_states = valid_states_by_action()["ACT"]
    rows: list[dict[str, Any]] = []
    mutations = ("information", "permission", "risk", "reversibility", "execution_possible", "need", "completed")
    for i in range(n):
        state = dict(rng.choice(act_states))
        legitimate = i % 2 == 0
        mutated_field = None
        if not legitimate:
            mutated_field = mutations[(i // 2) % len(mutations)]
            if mutated_field == "information": state[mutated_field] = "insufficient"
            elif mutated_field == "permission":
                if state["side_effect"] == "external": state[mutated_field] = "missing"
                else: state[mutated_field] = "missing"
            elif mutated_field == "risk": state[mutated_field] = "high"
            elif mutated_field == "reversibility": state[mutated_field] = "irreversible"
            elif mutated_field == "execution_possible": state[mutated_field] = False
            elif mutated_field == "need": state[mutated_field] = "optional"
            elif mutated_field == "completed": state[mutated_field] = True
            assert valid_state(state)
        rows.append({
            "id": f"act-boundary-{i:05d}",
            "text": render_state(state, family, rng),
            "state": state,
            "action": oracle_action(state),
            "legitimate_act": legitimate,
            "mutated_field": mutated_field,
        })
    rng.shuffle(rows)
    return rows


def make_contradiction(n: int, seed: int, family: str = "validation") -> list[dict[str, Any]]:
    base = make_dataset(n if n % 6 == 0 else n + (6 - n % 6), seed, family, "contradiction")[:n]
    rng = random.Random(seed + 111)
    candidate_fields = ["permission", "information", "risk", "reversibility", "execution_possible", "need", "side_effect", "completed"]
    for row in base:
        field = rng.choice(candidate_fields)
        wrong = _wrong_value(field, row["state"][field], rng)
        phrase = _choice_for_family(field, wrong, family, rng)
        # Same temporal rank as the base text => explicit unresolved contradiction.
        row["text"] += " " + phrase
        row["contradicted_field"] = field
    return base


def make_uncertainty(n: int, seed: int, family: str = "validation") -> list[dict[str, Any]]:
    base = make_dataset(n if n % 6 == 0 else n + (6 - n % 6), seed, family, "uncertainty")[:n]
    rng = random.Random(seed + 127)
    critical = ["permission", "information", "risk", "reversibility", "execution_possible", "need", "side_effect", "completed"]
    for row in base:
        field = rng.choice(critical)
        # Re-render while omitting one critical factor, then add ambiguous evidence.
        text = render_state(row["state"], family, rng, omit={field})
        phrase = _choice_for_family(field, row["state"][field], family, rng)
        row["text"] = text + " Maybe " + phrase[0].lower() + phrase[1:]
        row["uncertain_field"] = field
    return base


def make_negation(n: int, seed: int, family: str = "lexical") -> list[dict[str, Any]]:
    base = make_dataset(n if n % 6 == 0 else n + (6 - n % 6), seed, family, "negation")[:n]
    rng = random.Random(seed + 139)
    for row in base:
        row["text"] = render_state(row["state"], family, rng, negation_mode=True)
    return base


def make_invariance_pairs(n_pairs: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    # balanced base can be larger than needed, then slice
    n = ((n_pairs + 5) // 6) * 6
    states = balanced_states(n, seed)[:n_pairs]
    rows = []
    for i, state in enumerate(states):
        rows.append({
            "id": f"invariance-{i:05d}",
            "state": state,
            "action": oracle_action(state),
            "text_a": render_state(state, "lexical", rng, shuffle=True),
            "text_b": render_state(state, "rendering", rng, shuffle=True, narrative=True),
        })
    return rows


def make_counterfactual_pairs(n_pairs: int, seed: int, family: str = "validation") -> list[dict[str, Any]]:
    rng = random.Random(seed)
    act_states = valid_states_by_action()["ACT"]
    rows = []
    fields = ("information", "permission", "risk", "reversibility", "execution_possible", "need", "completed")
    for i in range(n_pairs):
        before = dict(rng.choice(act_states))
        after = dict(before)
        field = fields[i % len(fields)]
        if field == "information": after[field] = "insufficient"
        elif field == "permission": after[field] = "missing"
        elif field == "risk": after[field] = "high"
        elif field == "reversibility": after[field] = "irreversible"
        elif field == "execution_possible": after[field] = False
        elif field == "need": after[field] = "optional"
        elif field == "completed": after[field] = True
        assert valid_state(after)
        rows.append({
            "id": f"counterfactual-{i:05d}",
            "field": field,
            "before_state": before,
            "after_state": after,
            "before_action": oracle_action(before),
            "after_action": oracle_action(after),
            "before_text": render_state(before, family, rng),
            "after_text": render_state(after, family, rng),
        })
    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
