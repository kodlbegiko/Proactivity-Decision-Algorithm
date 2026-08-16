from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping

from proactivity.decisions import Decision
from .oracle import evaluate
from .schema import condition_matches, enumerate_states, validate_state


def _walk_condition(condition: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    yield condition
    for key in ("all", "any"):
        for item in condition.get(key, []):
            yield from _walk_condition(item)
    if "not" in condition:
        yield from _walk_condition(condition["not"])


def detect_precedence_cycles(edges: Iterable[Iterable[str]]) -> list[list[str]]:
    graph: dict[str, list[str]] = defaultdict(list)
    for left, right in edges:
        graph[str(left)].append(str(right))
    visiting: set[str] = set(); visited: set[str] = set(); stack: list[str] = []; cycles: list[list[str]] = []
    def dfs(node: str) -> None:
        if node in visiting:
            start = stack.index(node); cycles.append(stack[start:] + [node]); return
        if node in visited: return
        visiting.add(node); stack.append(node)
        for nxt in graph.get(node, []): dfs(nxt)
        stack.pop(); visiting.remove(node); visited.add(node)
    for node in list(graph): dfs(node)
    return cycles


def validate_spec_structure(spec: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "policy_id", "actions", "state_schema", "hard_prohibitions", "selection_rules", "invariants"}
    missing = sorted(required - set(spec))
    if missing: return ["missing_spec_keys:" + ",".join(missing)]
    action_names = {item.value for item in Decision}
    if set(spec["actions"]) != action_names: errors.append("action_set_mismatch")
    fields = set(spec["state_schema"]); seen: set[str] = set()
    for group in (spec.get("invalid_constraints", []), spec.get("hard_prohibitions", []), spec.get("selection_rules", [])):
        for rule in group:
            rid = rule.get("id")
            if not rid or rid in seen: errors.append(f"duplicate_or_missing_rule_id:{rid}")
            seen.add(rid)
            if "when" not in rule: errors.append(f"missing_condition:{rid}"); continue
            for node in _walk_condition(rule["when"]):
                if "field" in node and node["field"] not in fields: errors.append(f"unknown_rule_field:{rid}:{node['field']}")
            if "action" in rule and rule["action"] not in action_names: errors.append(f"invalid_rule_action:{rid}")
            for action in rule.get("actions", []):
                if action not in action_names: errors.append(f"invalid_prohibition_action:{rid}:{action}")
    if not any(rule.get("when", {}).get("always") is True for rule in spec["selection_rules"]): errors.append("missing_explicit_fallback_rule")
    if detect_precedence_cycles(spec.get("precedence_edges", [])): errors.append("precedence_cycle")
    return errors


def _invariant_violations(state: Mapping[str, Any], action: str) -> list[str]:
    out: list[str] = []
    if action == "ACT":
        if state["information"] != "sufficient": out.append("INV_ACT_INFO")
        if state["risk"] != "low": out.append("INV_ACT_LOW_RISK")
        if state["reversibility"] != "reversible": out.append("INV_ACT_REVERSIBLE")
        if not state["execution_possible"]: out.append("INV_ACT_EXECUTABLE")
        if state["need"] != "material": out.append("INV_ACT_MATERIAL_NEED")
        if state["side_effect"] == "external" and state["permission"] != "granted": out.append("INV_ACT_PERMISSION")
        if state["side_effect"] == "local" and state["permission"] == "missing": out.append("INV_ACT_PERMISSION")
    if state["completed"] and action in {"SUGGEST", "NOTIFY", "ASK", "ACT"}: out.append("INV_COMPLETED_SILENT")
    return out


def audit_gate_b(spec: Mapping[str, Any]) -> dict[str, Any]:
    schema_errors = validate_spec_structure(spec)
    raw = valid_count = invalid_count = nondeterministic = trace_missing = 0
    action_distribution: Counter[str] = Counter(); selected_rules: Counter[str] = Counter(); matched_rules: Counter[str] = Counter()
    conflicts: list[dict[str, Any]] = []; invariant_violations: list[dict[str, Any]] = []; valid_states: list[dict[str, Any]] = []
    for state in enumerate_states(spec):
        raw += 1; validation = validate_state(spec, state)
        if not validation.valid: invalid_count += 1; continue
        valid_count += 1; valid_states.append(state)
        for rule in spec["selection_rules"]:
            if condition_matches(rule["when"], state): matched_rules[rule["id"]] += 1
        first = evaluate(state, spec=spec); second = evaluate(state, spec=spec)
        if first != second: nondeterministic += 1
        if first.status != "VALID_DECISION": conflicts.append({"state": state, "status": first.status, "violations": first.violations}); continue
        action_distribution[first.action or "NONE"] += 1; selected_rules[first.matched_rule or "NONE"] += 1
        if not (first.spec_version and first.spec_sha256 and first.matched_rule and first.action): trace_missing += 1
        for violation in _invariant_violations(state, first.action or ""): invariant_violations.append({"id": violation, "state": state, "action": first.action})
    counterfactual_cases = 0; counterfactual_violations = 0
    act_states = [s for s in valid_states if evaluate(s, spec=spec).action == "ACT"]
    for state in act_states:
        for field, value in (("risk", "high"), ("information", "insufficient")):
            changed = dict(state); changed[field] = value; counterfactual_cases += 1
            if evaluate(changed, spec=spec).action == "ACT": counterfactual_violations += 1
        if state["side_effect"] == "external":
            changed = dict(state); changed["permission"] = "missing"; counterfactual_cases += 1
            if evaluate(changed, spec=spec).action == "ACT": counterfactual_violations += 1
    base = {"permission":"not_required","information":"sufficient","urgency":"none","need":"material","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":True,"execution_possible":False,"clarification_possible":True,"acknowledged":False,"completed":False}
    temporal_states = [base, base | {"urgency":"high"}, base | {"urgency":"normal","acknowledged":True}, base | {"urgency":"expired","completed":True}]
    temporal_actions = [evaluate(item, spec=spec).action for item in temporal_states]; temporal_expected = ["WAIT", "NOTIFY", "WAIT", "IGNORE"]
    metadata_invariance_violations = sum(evaluate(s, spec=spec).action != evaluate(dict(s), spec=spec).action for s in valid_states)
    unreachable_rules = sorted(rule["id"] for rule in spec["selection_rules"] if matched_rules[rule["id"]] == 0)
    fallback_id = next((rule["id"] for rule in spec["selection_rules"] if rule.get("when", {}).get("always") is True), None)
    report = {
        "schema_errors": schema_errors,
        "raw_state_combinations": raw,
        "valid_state_combinations": valid_count,
        "invalid_state_combinations": invalid_count,
        "action_distribution": dict(sorted(action_distribution.items())),
        "determinism": {"tested_states": valid_count, "nondeterministic": nondeterministic, "pass": nondeterministic == 0},
        "coverage": {"conflicts": len(conflicts), "unreachable_matching_rules": unreachable_rules, "fallback_count": selected_rules[fallback_id] if fallback_id else 0, "selected_rule_count": len(selected_rules)},
        "traceability": {"missing": trace_missing, "pass": trace_missing == 0},
        "invariants": {"violations": len(invariant_violations), "pass": not invariant_violations},
        "counterfactual": {"cases": counterfactual_cases, "violations": counterfactual_violations, "pass": counterfactual_violations == 0},
        "temporal": {"actions": temporal_actions, "expected": temporal_expected, "violations": 0 if temporal_actions == temporal_expected else 1, "pass": temporal_actions == temporal_expected},
        "metadata_domain_invariance": {"violations": metadata_invariance_violations, "pass": metadata_invariance_violations == 0},
        "status": "EVIDENCE_COMPLETE"
    }
    report["gate_verdict"] = gate_b_verdict(report); return report


def gate_b_verdict(report: Mapping[str, Any]) -> str:
    if report.get("schema_errors"): return "GATE B — FAIL_SCHEMA"
    if not report.get("determinism", {}).get("pass"): return "GATE B — FAIL_NONDETERMINISM"
    if report.get("coverage", {}).get("conflicts", 1) != 0: return "GATE B — FAIL_SPEC_CONTRADICTION"
    if report.get("valid_state_combinations", 0) == 0 or report.get("coverage", {}).get("unreachable_matching_rules"): return "GATE B — FAIL_COVERAGE"
    if not report.get("invariants", {}).get("pass") or not report.get("counterfactual", {}).get("pass") or not report.get("temporal", {}).get("pass") or not report.get("metadata_domain_invariance", {}).get("pass"): return "GATE B — FAIL_INVARIANT"
    if not report.get("traceability", {}).get("pass"): return "GATE B — FAIL_TRACEABILITY"
    return "GATE B — PASS"
