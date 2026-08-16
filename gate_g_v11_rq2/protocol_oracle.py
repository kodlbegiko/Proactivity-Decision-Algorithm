from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "spec" / "proactivity_policy_v2.json"

FACTOR_NAMES = (
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


@dataclass(frozen=True)
class OracleDecision:
    action: str
    state: dict[str, object]
    invalid: bool
    invalid_constraints: tuple[str, ...]
    act_prohibitions: tuple[str, ...]
    matched_rule: str | None


@lru_cache(maxsize=1)
def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text())


def _condition(expr: Mapping[str, Any], state: Mapping[str, object]) -> bool:
    if expr.get("always") is True:
        return True
    if "all" in expr:
        return all(_condition(item, state) for item in expr["all"])
    if "any" in expr:
        return any(_condition(item, state) for item in expr["any"])
    field = expr["field"]
    op = expr["op"]
    expected = expr.get("value")
    actual = state.get(field)
    if op == "eq":
        return actual == expected
    if op == "ne":
        return actual != expected
    if op == "in":
        return actual in expected
    if op == "not_in":
        return actual not in expected
    raise ValueError(f"Unsupported PDA-SPEC operator: {op}")


def validate_state(state: Mapping[str, object]) -> tuple[bool, tuple[str, ...]]:
    spec = load_spec()
    schema = spec["state_schema"]
    if set(state) != set(FACTOR_NAMES):
        return False, ("SCHEMA_FIELDS",)

    problems: list[str] = []
    for name in FACTOR_NAMES:
        rule = schema[name]
        value = state[name]
        if rule["type"] == "enum":
            if value not in rule["values"]:
                problems.append(f"SCHEMA_VALUE:{name}")
        elif rule["type"] == "boolean":
            if type(value) is not bool:
                problems.append(f"SCHEMA_VALUE:{name}")
        else:
            problems.append(f"SCHEMA_TYPE:{name}")

    for constraint in spec["invalid_constraints"]:
        if _condition(constraint["when"], state):
            problems.append(constraint["id"])
    return not problems, tuple(problems)


def act_prohibitions(state: Mapping[str, object]) -> tuple[str, ...]:
    spec = load_spec()
    blocked: list[str] = []
    for prohibition in spec["hard_prohibitions"]:
        if "ACT" in prohibition["actions"] and _condition(prohibition["when"], state):
            blocked.append(prohibition["id"])
    return tuple(blocked)


def decide(state: Mapping[str, object]) -> OracleDecision:
    normalized = dict(state)
    valid, invalid_constraints = validate_state(normalized)
    if not valid:
        return OracleDecision(
            action="INVALID",
            state=normalized,
            invalid=True,
            invalid_constraints=invalid_constraints,
            act_prohibitions=act_prohibitions(normalized),
            matched_rule=None,
        )

    spec = load_spec()
    rules = sorted(spec["selection_rules"], key=lambda item: int(item["priority"]), reverse=True)
    for rule in rules:
        if _condition(rule["when"], normalized):
            action = rule["action"]
            prohibitions = act_prohibitions(normalized)
            if action == "ACT" and prohibitions:
                raise RuntimeError(
                    f"PDA-SPEC-v2 internal inconsistency: rule {rule['id']} selects ACT while {prohibitions} prohibit it"
                )
            return OracleDecision(
                action=action,
                state=normalized,
                invalid=False,
                invalid_constraints=(),
                act_prohibitions=prohibitions,
                matched_rule=rule["id"],
            )
    raise RuntimeError("PDA-SPEC-v2 contains no matching selection rule")
