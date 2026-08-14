from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Mapping


class SpecificationError(ValueError):
    pass


@dataclass(frozen=True)
class StateValidation:
    valid: bool
    errors: tuple[str, ...]


def condition_matches(condition: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
    if condition.get("always") is True:
        return True
    if "all" in condition:
        return all(condition_matches(item, state) for item in condition["all"])
    if "any" in condition:
        return any(condition_matches(item, state) for item in condition["any"])
    if "not" in condition:
        return not condition_matches(condition["not"], state)
    field = condition.get("field")
    op = condition.get("op")
    if field not in state:
        raise SpecificationError(f"unknown/missing condition field: {field}")
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
    raise SpecificationError(f"unsupported condition operator: {op}")


def validate_state(spec: Mapping[str, Any], state: Mapping[str, Any]) -> StateValidation:
    schema = spec["state_schema"]
    errors: list[str] = []
    missing = sorted(set(schema) - set(state))
    unknown = sorted(set(state) - set(schema))
    if missing:
        errors.append("missing_fields:" + ",".join(missing))
    if unknown:
        errors.append("unknown_fields:" + ",".join(unknown))
    if missing or unknown:
        return StateValidation(False, tuple(errors))
    for field, definition in schema.items():
        value = state[field]
        if definition["type"] == "boolean":
            if type(value) is not bool:
                errors.append(f"invalid_boolean:{field}")
        elif definition["type"] == "enum":
            if value not in definition["values"]:
                errors.append(f"invalid_enum:{field}:{value}")
        else:
            errors.append(f"unsupported_schema_type:{field}:{definition['type']}")
    if errors:
        return StateValidation(False, tuple(errors))
    for constraint in spec.get("invalid_constraints", []):
        if condition_matches(constraint["when"], state):
            errors.append("invalid_combination:" + constraint["id"])
    return StateValidation(not errors, tuple(errors))


def enumerate_states(spec: Mapping[str, Any]) -> Iterable[dict[str, Any]]:
    names = list(spec["state_schema"])
    domains: list[list[Any]] = []
    for name in names:
        definition = spec["state_schema"][name]
        domains.append(list(definition["values"]) if definition["type"] == "enum" else [False, True])
    for values in product(*domains):
        yield dict(zip(names, values))
