from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping

ACTIONS = ("IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT")
SPEC_PATH = Path(__file__).resolve().parents[1] / "spec" / "proactivity_policy_v2.json"


def load_spec(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else SPEC_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def _condition_matches(condition: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
    if condition.get("always") is True:
        return True
    if "all" in condition:
        return all(_condition_matches(item, state) for item in condition["all"])
    if "any" in condition:
        return any(_condition_matches(item, state) for item in condition["any"])
    if "not" in condition:
        return not _condition_matches(condition["not"], state)
    field = condition["field"]
    op = condition["op"]
    actual = state[field]
    expected = condition.get("value")
    if op == "eq":
        return actual == expected
    if op == "ne":
        return actual != expected
    if op == "in":
        return actual in expected
    if op == "not_in":
        return actual not in expected
    raise ValueError(f"unsupported condition operator: {op}")


def state_errors(state: Mapping[str, Any], spec: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    policy = dict(spec) if spec is not None else load_spec()
    schema = policy["state_schema"]
    errors: list[str] = []
    missing = sorted(set(schema) - set(state))
    unknown = sorted(set(state) - set(schema))
    if missing:
        errors.append("missing_fields:" + ",".join(missing))
    if unknown:
        errors.append("unknown_fields:" + ",".join(unknown))
    if missing or unknown:
        return tuple(errors)
    for field, definition in schema.items():
        value = state[field]
        if definition["type"] == "boolean":
            if type(value) is not bool:
                errors.append(f"invalid_boolean:{field}")
        elif definition["type"] == "enum":
            if value not in definition["values"]:
                errors.append(f"invalid_enum:{field}:{value}")
        else:
            errors.append(f"unsupported_schema_type:{field}")
    if errors:
        return tuple(errors)
    for constraint in policy.get("invalid_constraints", []):
        if _condition_matches(constraint["when"], state):
            errors.append("invalid_combination:" + constraint["id"])
    return tuple(errors)


def valid_state(state: Mapping[str, Any], spec: Mapping[str, Any] | None = None) -> bool:
    return not state_errors(state, spec)


def oracle_action(state: Mapping[str, Any], spec: Mapping[str, Any] | None = None) -> str:
    policy = dict(spec) if spec is not None else load_spec()
    errors = state_errors(state, policy)
    if errors:
        raise ValueError("invalid state: " + ";".join(errors))
    prohibited: set[str] = set()
    for rule in policy.get("hard_prohibitions", []):
        if _condition_matches(rule["when"], state):
            prohibited.update(rule["actions"])
    matching = [rule for rule in policy["selection_rules"] if _condition_matches(rule["when"], state)]
    top_priority = max(rule["priority"] for rule in matching)
    top = [rule for rule in matching if rule["priority"] == top_priority]
    actions = {rule["action"] for rule in top}
    if len(actions) != 1:
        raise ValueError("invalid specification: equal-priority action conflict")
    action = top[0]["action"]
    if action in prohibited:
        raise ValueError("invalid specification: selected prohibited action")
    return action


def forbidden_act(state: Mapping[str, Any], spec: Mapping[str, Any] | None = None) -> bool:
    policy = dict(spec) if spec is not None else load_spec()
    if not valid_state(state, policy):
        return True
    for rule in policy.get("hard_prohibitions", []):
        if "ACT" in rule["actions"] and _condition_matches(rule["when"], state):
            return True
    return False


def state_schema(spec: Mapping[str, Any] | None = None) -> dict[str, tuple[Any, ...]]:
    policy = dict(spec) if spec is not None else load_spec()
    out: dict[str, tuple[Any, ...]] = {}
    for field, definition in policy["state_schema"].items():
        out[field] = tuple(definition["values"]) if definition["type"] == "enum" else (False, True)
    return out


def enumerate_states(spec: Mapping[str, Any] | None = None, *, valid_only: bool = False) -> Iterable[dict[str, Any]]:
    policy = dict(spec) if spec is not None else load_spec()
    schema = state_schema(policy)
    names = list(schema)
    for values in product(*(schema[name] for name in names)):
        state = dict(zip(names, values))
        if not valid_only or valid_state(state, policy):
            yield state


def valid_permission_side_pairs() -> tuple[tuple[str, str], ...]:
    # (permission, side_effect), exactly the normative-valid domain induced by PDA-SPEC-v2.
    return (
        ("not_required", "none"),
        ("not_required", "local"),
        ("missing", "local"),
        ("granted", "local"),
        ("missing", "external"),
        ("granted", "external"),
    )
