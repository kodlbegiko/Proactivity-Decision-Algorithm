from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

from proactivity.specification import evaluate, load_spec
from proactivity.specification.schema import enumerate_states, validate_state

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "spec" / "proactivity_policy_v2.json"
ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
DOMAINS = ("study", "work", "scheduling", "communication", "travel", "device")
TARGET_PER_ACTION = 20
PAIR_TARGET = 24
SEED = 20260815

FIELD_ORDER = (
    "permission", "information", "urgency", "need", "side_effect", "risk",
    "reversibility", "deferral_available", "execution_possible",
    "clarification_possible", "acknowledged", "completed",
)

FORBIDDEN_ACTION_TOKENS = {"act", "ask", "ignore", "notify", "suggest", "wait"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def state_key(state: Mapping[str, Any]) -> str:
    return canonical_json(dict(state))


def stable_rank(*parts: str) -> str:
    return digest_text("|".join((str(SEED),) + tuple(parts)))


def schema_values(spec: Mapping[str, Any], field: str) -> list[Any]:
    definition = spec["state_schema"][field]
    if definition["type"] == "enum":
        return list(definition["values"])
    if definition["type"] == "boolean":
        return [False, True]
    raise RuntimeError(f"unsupported schema type for {field}")


def stress_tags(state: Mapping[str, Any]) -> tuple[str, ...]:
    tags: list[str] = []
    if state["permission"] == "missing":
        tags.append("permission_missing")
    elif state["permission"] == "granted" and state["side_effect"] != "none":
        tags.append("permission_granted_side_effect")
    if state["information"] != "sufficient":
        tags.append("information_boundary")
    if state["urgency"] in {"high", "expired"}:
        tags.append("urgency_boundary")
    if state["side_effect"] in {"local", "external"}:
        tags.append("material_side_effect")
    if state["risk"] in {"medium", "high"}:
        tags.append("risk_boundary")
    if state["reversibility"] == "irreversible":
        tags.append("irreversible")
    if state["deferral_available"]:
        tags.append("deferral_available")
    if not state["execution_possible"]:
        tags.append("execution_blocked")
    if not state["clarification_possible"]:
        tags.append("clarification_unavailable")
    if state["acknowledged"]:
        tags.append("acknowledged")
    if state["completed"]:
        tags.append("completed")
    if len(tags) >= 4:
        tags.append("composed_boundary")
    return tuple(tags)


def _value_text(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value).replace("_", " ")


def render_observation(state: Mapping[str, Any], domain: str, family: int) -> str:
    pairs = [(field, _value_text(state[field])) for field in FIELD_ORDER]
    if family == 0:
        body = "; ".join(f"{field.replace('_', ' ')} is {value}" for field, value in pairs)
        text = f"In this {domain} case, {body}."
    elif family == 1:
        first = pairs[:6]
        second = pairs[6:]
        s1 = ", ".join(f"{field.replace('_', ' ')}: {value}" for field, value in first)
        s2 = ", ".join(f"{field.replace('_', ' ')}: {value}" for field, value in second)
        text = f"A {domain} situation has these conditions. {s1}. The remaining conditions are {s2}."
    elif family == 2:
        reordered = pairs[2:6] + pairs[:2] + pairs[8:] + pairs[6:8]
        body = ". ".join(f"The {field.replace('_', ' ')} value is {value}" for field, value in reordered)
        text = f"Case note for {domain}. {body}."
    elif family == 3:
        reordered = list(reversed(pairs))
        body = "; ".join(f"{field.replace('_', ' ')}={value}" for field, value in reordered)
        text = f"For a {domain} decision context, the recorded situation is: {body}."
    else:
        raise ValueError(f"unknown rendering family: {family}")
    words = {word.strip(".,;:=()").lower() for word in text.split()}
    leaked = sorted(words & FORBIDDEN_ACTION_TOKENS)
    if leaked:
        raise RuntimeError(f"action-token leakage in observation: {leaked}")
    return text


def build_rows() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    spec = load_spec(SPEC_PATH)
    rows: dict[str, dict[str, Any]] = {}
    for state in enumerate_states(spec):
        if not validate_state(spec, state).valid:
            continue
        result = evaluate(state, spec=spec)
        if result.status != "VALID_DECISION" or result.action not in ACTIONS:
            raise RuntimeError(f"invalid oracle result: {result}")
        key = state_key(state)
        rows[key] = {
            "state": dict(state),
            "action": str(result.action),
            "matched_rule": str(result.matched_rule),
            "prohibited_actions": list(result.prohibited_actions),
            "prohibition_rules": list(result.prohibition_rules),
            "stress_tags": list(stress_tags(state)),
        }
    if len(rows) != 41472:
        raise RuntimeError(f"unexpected valid state count: {len(rows)}")
    return spec, rows


def build_pair_candidates(spec: Mapping[str, Any], rows: Mapping[str, dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    pairs: list[dict[str, Any]] = []
    for key, row in rows.items():
        state = row["state"]
        for field in FIELD_ORDER:
            for alternative in schema_values(spec, field):
                if alternative == state[field]:
                    continue
                changed = dict(state)
                changed[field] = alternative
                other_key = state_key(changed)
                other = rows.get(other_key)
                if other is None or other["action"] == row["action"]:
                    continue
                edge = tuple(sorted((key, other_key)))
                if edge in seen:
                    continue
                seen.add(edge)
                pairs.append({
                    "left": edge[0],
                    "right": edge[1],
                    "field": field,
                    "rank": stable_rank(field, edge[0], edge[1]),
                })
    return sorted(pairs, key=lambda item: (item["rank"], item["field"], item["left"], item["right"]))


def select_states(spec: Mapping[str, Any], rows: Mapping[str, dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    pairs = build_pair_candidates(spec, rows)
    selected: set[str] = set()
    counts: Counter[str] = Counter()
    selected_pairs: list[dict[str, Any]] = []
    covered_fields: set[str] = set()

    # First obtain broad single-field counterfactual coverage.
    for field in FIELD_ORDER:
        for pair in pairs:
            if pair["field"] != field:
                continue
            if pair["left"] in selected or pair["right"] in selected:
                continue
            a = rows[pair["left"]]["action"]
            b = rows[pair["right"]]["action"]
            if counts[a] >= TARGET_PER_ACTION or counts[b] >= TARGET_PER_ACTION:
                continue
            selected.update((pair["left"], pair["right"]))
            counts[a] += 1
            counts[b] += 1
            selected_pairs.append(pair)
            covered_fields.add(field)
            break

    # Then fill the preregistered disjoint-pair quota deterministically.
    for pair in pairs:
        if len(selected_pairs) >= PAIR_TARGET:
            break
        if pair["left"] in selected or pair["right"] in selected:
            continue
        a = rows[pair["left"]]["action"]
        b = rows[pair["right"]]["action"]
        if counts[a] >= TARGET_PER_ACTION or counts[b] >= TARGET_PER_ACTION:
            continue
        selected.update((pair["left"], pair["right"]))
        counts[a] += 1
        counts[b] += 1
        selected_pairs.append(pair)
        covered_fields.add(pair["field"])

    if len(selected_pairs) != PAIR_TARGET:
        raise RuntimeError(f"could not select {PAIR_TARGET} disjoint action-changing pairs")
    if len(covered_fields) < 8:
        raise RuntimeError(f"insufficient counterfactual field coverage: {sorted(covered_fields)}")

    # Fill each oracle-action stratum to exactly 20 with boundary-rich compositions.
    by_action: dict[str, list[str]] = defaultdict(list)
    for key, row in rows.items():
        by_action[row["action"]].append(key)
    for action in ACTIONS:
        candidates = sorted(
            (key for key in by_action[action] if key not in selected),
            key=lambda key: (-len(rows[key]["stress_tags"]), stable_rank(action, key)),
        )
        needed = TARGET_PER_ACTION - counts[action]
        if needed < 0:
            raise RuntimeError(f"pair selection exceeded action quota for {action}")
        chosen = candidates[:needed]
        if len(chosen) != needed:
            raise RuntimeError(f"insufficient rows for action {action}")
        selected.update(chosen)
        counts[action] += len(chosen)

    if any(counts[action] != TARGET_PER_ACTION for action in ACTIONS):
        raise RuntimeError(f"action quota failure: {dict(counts)}")
    if len(selected) != TARGET_PER_ACTION * len(ACTIONS):
        raise RuntimeError(f"unexpected selected state count: {len(selected)}")

    return sorted(selected, key=lambda key: stable_rank("final", key)), selected_pairs


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")


def generate(output_dir: Path) -> dict[str, Any]:
    spec, rows = build_rows()
    selected_keys, selected_pairs = select_states(spec, rows)
    output_dir.mkdir(parents=True, exist_ok=True)

    pair_by_state: dict[str, tuple[str, str]] = {}
    for index, pair in enumerate(selected_pairs, start=1):
        pair_id = f"GFPAIR-{index:02d}"
        pair_by_state[pair["left"]] = (pair_id, pair["field"])
        pair_by_state[pair["right"]] = (pair_id, pair["field"])

    inputs: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    private: list[dict[str, Any]] = []
    template_counts: Counter[int] = Counter()
    domain_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    stress_counts: Counter[str] = Counter()

    for index, key in enumerate(selected_keys):
        row = rows[key]
        domain = DOMAINS[index % len(DOMAINS)]
        family = index % 4
        scenario_id = "gf2_" + digest_text(f"{SEED}|{key}")[:16]
        observation = render_observation(row["state"], domain, family)
        inputs.append({"scenario_id": scenario_id, "domain": domain, "observation": observation})
        labels.append({"scenario_id": scenario_id, "expected_action": row["action"]})
        pair_meta = pair_by_state.get(key)
        private.append({
            "scenario_id": scenario_id,
            "state": row["state"],
            "oracle_action": row["action"],
            "matched_rule": row["matched_rule"],
            "prohibited_actions": row["prohibited_actions"],
            "prohibition_rules": row["prohibition_rules"],
            "stress_tags": row["stress_tags"],
            "counterfactual_pair_id": pair_meta[0] if pair_meta else None,
            "counterfactual_field": pair_meta[1] if pair_meta else None,
            "state_sha256": digest_text(key),
            "rendering_family": family,
        })
        template_counts[family] += 1
        domain_counts[domain] += 1
        action_counts[row["action"]] += 1
        stress_counts.update(row["stress_tags"])

    # Keep aligned artifacts in deterministic scenario-id order.
    ordering = sorted(range(len(inputs)), key=lambda i: inputs[i]["scenario_id"])
    inputs = [inputs[i] for i in ordering]
    labels = [labels[i] for i in ordering]
    private = [private[i] for i in ordering]

    write_jsonl(output_dir / "protected_inputs_v2.jsonl", inputs)
    write_jsonl(output_dir / "protected_labels_v2.jsonl", labels)
    write_jsonl(output_dir / "protected_private_v2.jsonl", private)

    summary = {
        "protocol": "PDA Protocol v2 Gate F",
        "generator_version": "1.0.0",
        "seed": SEED,
        "total": len(inputs),
        "action_counts": dict(sorted(action_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "rendering_family_counts": {str(k): template_counts[k] for k in sorted(template_counts)},
        "counterfactual_pair_count": len(selected_pairs),
        "counterfactual_fields": sorted({pair["field"] for pair in selected_pairs}),
        "stress_tag_counts": dict(sorted(stress_counts.items())),
        "valid_state_universe": len(rows),
        "candidate_runtime_access": False,
        "candidate_source_used_for_generation": False,
        "labels_source": "frozen PDA-SPEC-v2 deterministic oracle",
    }
    (output_dir / "generation_summary_v2.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = generate(args.output_dir)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
