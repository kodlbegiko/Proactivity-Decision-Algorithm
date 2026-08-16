from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from proactivity.decisions import Decision
from .schema import condition_matches, validate_state

DEFAULT_SPEC_PATH = Path(__file__).resolve().parents[3] / "spec" / "proactivity_policy_v2.json"


@dataclass(frozen=True)
class OracleResult:
    status: str
    action: str | None
    matched_rule: str | None
    matched_rules: tuple[str, ...]
    prohibited_actions: tuple[str, ...]
    prohibition_rules: tuple[str, ...]
    eligible_actions: tuple[str, ...]
    violations: tuple[str, ...]
    spec_version: str
    spec_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_spec(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else DEFAULT_SPEC_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def spec_sha256(path: str | Path | None = None) -> str:
    target = Path(path) if path is not None else DEFAULT_SPEC_PATH
    return hashlib.sha256(target.read_bytes()).hexdigest()


def _prohibitions(spec: Mapping[str, Any], state: Mapping[str, Any]) -> tuple[set[str], list[str]]:
    prohibited: set[str] = set()
    rules: list[str] = []
    for rule in spec.get("hard_prohibitions", []):
        if condition_matches(rule["when"], state):
            prohibited.update(rule["actions"])
            rules.append(rule["id"])
    return prohibited, rules


def evaluate_record(record: Mapping[str, Any], *, spec: Mapping[str, Any] | None = None, spec_path: str | Path | None = None) -> OracleResult:
    """Evaluate only record['state']; metadata such as scenario_id/domain is deliberately ignored."""
    if "state" not in record:
        raise ValueError("record must contain state")
    return evaluate(record["state"], spec=spec, spec_path=spec_path)


def evaluate(state: Mapping[str, Any], *, spec: Mapping[str, Any] | None = None, spec_path: str | Path | None = None) -> OracleResult:
    policy = dict(spec) if spec is not None else load_spec(spec_path)
    version = str(policy.get("schema_version", "UNKNOWN"))
    sha = spec_sha256(spec_path) if spec is None else hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    validation = validate_state(policy, state)
    if not validation.valid:
        return OracleResult("INVALID_STATE", None, None, tuple(), tuple(), tuple(), tuple(), validation.errors, version, sha)
    prohibited, prohibition_rules = _prohibitions(policy, state)
    matching = [rule for rule in policy["selection_rules"] if condition_matches(rule["when"], state)]
    if not matching:
        return OracleResult("INVALID_SPEC", None, None, tuple(), tuple(sorted(prohibited)), tuple(prohibition_rules), tuple(), ("no_matching_rule",), version, sha)
    top_priority = max(rule["priority"] for rule in matching)
    top = [rule for rule in matching if rule["priority"] == top_priority]
    actions = {rule["action"] for rule in top}
    if len(actions) != 1:
        return OracleResult("INVALID_SPEC", None, None, tuple(rule["id"] for rule in top), tuple(sorted(prohibited)), tuple(prohibition_rules), tuple(), ("equal_priority_action_conflict",), version, sha)
    selected = top[0]
    action = selected["action"]
    eligible = tuple(item.value for item in Decision if item.value not in prohibited)
    if action in prohibited:
        return OracleResult("INVALID_SPEC", action, selected["id"], tuple(rule["id"] for rule in matching), tuple(sorted(prohibited)), tuple(prohibition_rules), eligible, ("selected_action_prohibited",), version, sha)
    return OracleResult("VALID_DECISION", action, selected["id"], tuple(rule["id"] for rule in matching), tuple(sorted(prohibited)), tuple(prohibition_rules), eligible, tuple(), version, sha)
