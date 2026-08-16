from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _eval(cond: dict[str, Any], state: dict[str, Any]) -> bool:
    if cond.get("always") is True:
        return True
    if "all" in cond:
        return all(_eval(c, state) for c in cond["all"])
    if "any" in cond:
        return any(_eval(c, state) for c in cond["any"])
    field = cond["field"]
    op = cond["op"]
    value = cond.get("value")
    actual = state[field]
    if op == "eq": return actual == value
    if op == "ne": return actual != value
    if op == "in": return actual in value
    if op == "not_in": return actual not in value
    raise ValueError(f"unsupported operator: {op}")


class NormativeOracle:
    def __init__(self, spec_path: str | Path = "spec/proactivity_policy_v2.json"):
        self.spec_path = Path(spec_path)
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        if self.spec.get("policy_id") != "PDA-SPEC-v2":
            raise ValueError("unexpected policy specification")

    def state_valid(self, state: dict[str, Any]) -> bool:
        return not any(_eval(rule["when"], state) for rule in self.spec["invalid_constraints"])

    def prohibited(self, action: str, state: dict[str, Any]) -> bool:
        for rule in self.spec["hard_prohibitions"]:
            if action in rule["actions"] and _eval(rule["when"], state):
                return True
        return False

    def decide(self, state: dict[str, Any]) -> str:
        if not self.state_valid(state):
            raise ValueError("oracle received invalid policy state")
        rules = sorted(self.spec["selection_rules"], key=lambda r: r["priority"], reverse=True)
        for rule in rules:
            if _eval(rule["when"], state) and not self.prohibited(rule["action"], state):
                return rule["action"]
        return "IGNORE"
