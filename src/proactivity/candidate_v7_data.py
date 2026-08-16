from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from proactivity.specification.oracle import evaluate, load_spec
from proactivity.specification.schema import enumerate_states, validate_state

FIELD_ORDER = (
    "permission", "information", "urgency", "need", "side_effect", "risk",
    "reversibility", "deferral_available", "execution_possible",
    "clarification_possible", "acknowledged", "completed",
)
ACTIONS = ("IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT")
SIZES = {
    "train": 4800,
    "validation": 1200,
    "development_ood": 1200,
    "lexical_holdout": 800,
    "rendering_holdout": 800,
    "compositional_holdout": 800,
    "negation_holdout": 600,
    "scope_holdout": 600,
    "temporal_holdout": 600,
    "counterfactual": 480,
    "invariance": 480,
}
SEEDS = {
    "train": 7001, "validation": 7002, "development_ood": 7003,
    "lexical_holdout": 7004, "rendering_holdout": 7005,
    "compositional_holdout": 7006, "negation_holdout": 7007,
    "scope_holdout": 7008, "temporal_holdout": 7009,
    "counterfactual": 7010, "invariance": 7011,
}

# Surface realizations are intentionally separate families. The parser does not import this table.
LEXICAL: dict[str, dict[str, dict[str, tuple[str, ...]]]] = {
    "permission": {
        "granted": {"core": ("Permission is granted", "Approval is granted"), "alt": ("Authorization is confirmed", "Consent is on record"), "holdout": ("The operation has clearance", "The required sign-off is in place")},
        "missing": {"core": ("Permission is missing", "Approval is still pending"), "alt": ("The operation remains unauthorized", "Consent is absent"), "holdout": ("Nobody has signed off yet", "The required clearance has yet to arrive")},
        "not_required": {"core": ("Permission is not required", "No approval is required"), "alt": ("Authorization is unnecessary", "This does not require consent"), "holdout": ("No sign-off is needed", "The operation is outside approval scope")},
    },
    "information": {
        "sufficient": {"core": ("Information is sufficient", "The facts are complete"), "alt": ("We have enough information", "The evidence is adequate"), "holdout": ("The available details are enough to decide", "Nothing material is missing from the information")},
        "insufficient": {"core": ("Information is insufficient", "The facts are incomplete"), "alt": ("More information is needed", "The evidence is inadequate"), "holdout": ("Key details are still missing", "The available facts do not support a complete decision")},
        "contradictory": {"core": ("Information is contradictory", "The facts conflict"), "alt": ("The evidence is inconsistent", "Available reports disagree"), "holdout": ("The details point in incompatible directions", "The record contains unresolved contradictions")},
    },
    "urgency": {
        "none": {"core": ("There is no urgency", "Timing is not urgent"), "alt": ("No immediate timing pressure exists", "The matter can wait"), "holdout": ("There is no time pressure at present", "Nothing is pressing right now")},
        "normal": {"core": ("Urgency is normal", "Timing is routine"), "alt": ("The matter has ordinary priority", "The schedule is standard"), "holdout": ("This follows the normal timetable", "The timing pressure is moderate and ordinary")},
        "high": {"core": ("Urgency is high", "The matter is urgent"), "alt": ("Immediate attention is needed", "Time pressure is severe"), "holdout": ("The deadline pressure is acute", "This needs prompt attention")},
        "expired": {"core": ("The deadline has expired", "The timing window is expired"), "alt": ("The deadline has already passed", "The allowed window is over"), "holdout": ("The due time is already behind us", "The permitted time window has lapsed")},
    },
    "need": {
        "none": {"core": ("No intervention is needed", "There is no current need"), "alt": ("Intervention is unnecessary", "Nothing needs to be done"), "holdout": ("There is no actionable need", "No response is called for")},
        "optional": {"core": ("Intervention is optional", "The need is optional"), "alt": ("A response could help but is not necessary", "Action is discretionary"), "holdout": ("A response may be useful but can be skipped", "Any intervention would be elective")},
        "material": {"core": ("A material intervention is needed", "The need is material"), "alt": ("A substantive response is required", "The situation requires intervention"), "holdout": ("There is a concrete need for action", "A meaningful response is called for")},
    },
    "side_effect": {
        "none": {"core": ("There is no side effect", "The action has no side effect"), "alt": ("No state-changing effect is involved", "The response is informational only"), "holdout": ("Nothing outside the message would be changed", "The intervention has zero material effect")},
        "local": {"core": ("The side effect is local", "The action changes local state"), "alt": ("Only local state would change", "The effect stays within the local system"), "holdout": ("The change is confined to this system", "The action affects only local data")},
        "external": {"core": ("The side effect is external", "The action changes an external system"), "alt": ("The effect reaches an outside system", "The action has external consequences"), "holdout": ("The operation would alter something beyond this system", "The change propagates to an external service")},
    },
    "risk": {
        "low": {"core": ("Risk is low", "The operation has low risk"), "alt": ("The risk level is minimal", "The operation is low-risk"), "holdout": ("The downside exposure is small", "Material harm is unlikely")},
        "medium": {"core": ("Risk is medium", "The operation has moderate risk"), "alt": ("The risk level is intermediate", "The downside is meaningful but not severe"), "holdout": ("The exposure is neither low nor extreme", "There is a moderate chance of harm")},
        "high": {"core": ("Risk is high", "The operation has high risk"), "alt": ("The risk level is severe", "The downside is substantial"), "holdout": ("The exposure to harm is considerable", "Material harm is a serious possibility")},
    },
    "reversibility": {
        "reversible": {"core": ("The action is reversible", "The change can be undone"), "alt": ("The operation can be rolled back", "Reversal remains possible"), "holdout": ("We can restore the prior state", "The effect is recoverable")},
        "irreversible": {"core": ("The action is irreversible", "The change cannot be undone"), "alt": ("The operation cannot be rolled back", "Reversal is impossible"), "holdout": ("There is no way to restore the prior state", "The effect is permanent")},
    },
    "deferral_available": {
        "true": {"core": ("Deferral is available", "The action can be deferred"), "alt": ("Waiting remains an option", "A later trigger is available"), "holdout": ("This can safely be postponed", "There is a valid future opportunity to revisit it")},
        "false": {"core": ("Deferral is unavailable", "The action cannot be deferred"), "alt": ("Waiting is not an option", "There is no later trigger"), "holdout": ("Postponement is not available", "There is no valid future opportunity to revisit it")},
    },
    "execution_possible": {
        "true": {"core": ("Execution is possible", "The action can be executed"), "alt": ("The system can perform the operation", "Execution is currently feasible"), "holdout": ("The operation can be carried out now", "The required execution path is available")},
        "false": {"core": ("Execution is not possible", "The action cannot be executed"), "alt": ("The system is unable to perform the operation", "Execution is currently infeasible"), "holdout": ("The operation cannot be carried out now", "No execution path is available")},
    },
    "clarification_possible": {
        "true": {"core": ("Clarification is possible", "We can ask for clarification"), "alt": ("Missing details can be clarified", "A question can resolve the uncertainty"), "holdout": ("The ambiguity can be resolved by asking", "Further clarification is obtainable")},
        "false": {"core": ("Clarification is not possible", "We cannot ask for clarification"), "alt": ("Missing details cannot be clarified", "No question can resolve the uncertainty"), "holdout": ("The ambiguity cannot be resolved by asking", "Further clarification is unavailable")},
    },
    "acknowledged": {
        "true": {"core": ("The matter is acknowledged", "It has been acknowledged"), "alt": ("The user has already acknowledged it", "Acknowledgement is on record"), "holdout": ("The situation has already been seen and recognized", "Receipt has been acknowledged")},
        "false": {"core": ("The matter is not acknowledged", "It has not been acknowledged"), "alt": ("The user has not acknowledged it", "No acknowledgement is on record"), "holdout": ("The situation has not yet been recognized", "Receipt remains unacknowledged")},
    },
    "completed": {
        "true": {"core": ("The task is completed", "Work is complete"), "alt": ("The operation has finished", "The task is already done"), "holdout": ("The required work has been fully completed", "There is nothing left to complete")},
        "false": {"core": ("The task is not completed", "Work is incomplete"), "alt": ("The operation has not finished", "The task remains open"), "holdout": ("The required work is still unfinished", "Completion has not yet occurred")},
    },
}

NEGATION = {
    ("permission", "missing"): "Approval has not been granted",
    ("permission", "not_required"): "Approval is not required",
    ("information", "insufficient"): "The information is not sufficient",
    ("urgency", "none"): "The matter is not urgent",
    ("need", "none"): "No intervention is needed",
    ("side_effect", "none"): "No side effect will occur",
    ("risk", "low"): "The risk is not medium or high",
    ("reversibility", "irreversible"): "The change is not reversible",
    ("deferral_available", "false"): "Deferral is not available",
    ("execution_possible", "false"): "Execution is not possible",
    ("clarification_possible", "false"): "Clarification is not possible",
    ("acknowledged", "false"): "The matter has not been acknowledged",
    ("completed", "false"): "The task has not been completed",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def stable_int(*parts: Any) -> int:
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def value_key(value: Any) -> str:
    if type(value) is bool:
        return "true" if value else "false"
    return str(value)


def opposite_value(field: str, value: Any, spec: Mapping[str, Any]) -> Any:
    definition = spec["state_schema"][field]
    values = [False, True] if definition["type"] == "boolean" else list(definition["values"])
    for candidate in values:
        if candidate != value:
            return candidate
    return value


def composition_signature(state: Mapping[str, Any]) -> int:
    critical = (state["permission"], state["information"], state["risk"], state["need"], state["side_effect"])
    return stable_int(*critical) % 7


def _balanced_states(spec: Mapping[str, Any], count: int, seed: int, *, compositional_only: bool | None = None) -> list[dict[str, Any]]:
    pools: dict[str, list[dict[str, Any]]] = {action: [] for action in ACTIONS}
    for state in enumerate_states(spec):
        if not validate_state(spec, state).valid:
            continue
        sig = composition_signature(state)
        if compositional_only is True and sig != 0:
            continue
        if compositional_only is False and sig == 0:
            continue
        result = evaluate(state, spec=spec)
        if result.status == "VALID_DECISION" and result.action in pools:
            pools[result.action].append(dict(state))
    quotas = {action: count // len(ACTIONS) for action in ACTIONS}
    for action in ACTIONS[: count % len(ACTIONS)]:
        quotas[action] += 1
    selected: list[dict[str, Any]] = []
    for action in ACTIONS:
        ranked = sorted(pools[action], key=lambda s: (stable_int(seed, action, canonical_json(s)), canonical_json(s)))
        if len(ranked) < quotas[action]:
            raise RuntimeError(f"insufficient valid states for {action}: {len(ranked)} < {quotas[action]}")
        selected.extend(ranked[: quotas[action]])
    return sorted(selected, key=lambda s: (stable_int(seed, canonical_json(s)), canonical_json(s)))


def _family_for(split: str, field: str, index: int) -> str:
    if split == "lexical_holdout":
        return "holdout"
    if split in {"development_ood", "compositional_holdout"}:
        return "alt"
    if split in {"rendering_holdout", "scope_holdout", "temporal_holdout"}:
        return "alt" if stable_int(split, field, index) % 2 else "core"
    return "core"


def _phrase(field: str, value: Any, family: str, index: int) -> str:
    choices = LEXICAL[field][value_key(value)][family]
    return choices[stable_int(field, value_key(value), family, index) % len(choices)]


def _clause(field: str, value: Any, split: str, index: int) -> tuple[str, dict[str, Any]]:
    family = _family_for(split, field, index)
    text = _phrase(field, value, family, index)
    polarity = "negative" if any(token in text.lower().split() for token in ("not", "no", "cannot")) or "n't" in text.lower() else "positive"
    if split == "negation_holdout" and (field, value_key(value)) in NEGATION:
        text = NEGATION[(field, value_key(value))]
        polarity = "negative"
    return text, {
        "field": field,
        "value": value,
        "predicate": field,
        "arguments": [],
        "polarity": polarity,
        "modality": "asserted",
        "certainty": 1.0,
        "temporality": "current",
        "scope": "clause",
        "normative": True,
    }


def render_state(state: Mapping[str, Any], split: str, index: int, *, rendering_variant: str | None = None) -> tuple[str, list[dict[str, Any]], dict[str, str]]:
    clauses: list[str] = []
    annotations: list[dict[str, Any]] = []
    for field in FIELD_ORDER:
        text, ann = _clause(field, state[field], split, stable_int(index, field))
        if split == "temporal_holdout" and field in {"permission", "information", "urgency", "execution_possible"} and stable_int(index, field, "temporal") % 2 == 0:
            prior = opposite_value(field, state[field], load_spec())
            prior_text = _phrase(field, prior, "core", stable_int(index, field, "prior"))
            clauses.append(f"Previously, {prior_text[0].lower() + prior_text[1:]}")
            annotations.append({"field": field, "value": prior, "predicate": field, "arguments": [], "polarity": "positive", "modality": "asserted", "certainty": 1.0, "temporality": "past", "scope": "clause", "normative": False})
            text = "As of now, " + text[0].lower() + text[1:]
        clauses.append(text)
        annotations.append(ann)

    style = rendering_variant
    if style is None:
        if split == "rendering_holdout":
            styles = ("bullet", "terse", "conversation", "parenthetical", "reordered", "multisentence")
            style = styles[stable_int(split, index) % len(styles)]
        elif split == "scope_holdout":
            style = "contrast"
        else:
            style = "declarative"

    current = list(clauses)
    if style == "reordered":
        current = sorted(current, key=lambda c: stable_int(index, c))
    if style == "bullet":
        text = "\n".join(f"- {c}." for c in current)
    elif style == "terse":
        text = "; ".join(current) + "."
    elif style == "conversation":
        text = "Status update: " + ". Also, ".join(c[0].lower() + c[1:] for c in current) + "."
    elif style == "parenthetical":
        text = ". ".join((c if i % 3 else f"For context ({c[0].lower() + c[1:]})") for i, c in enumerate(current)) + "."
    elif style == "multisentence":
        text = ".\n".join(current) + "."
    elif style == "contrast":
        pairs = []
        for i in range(0, len(current), 2):
            if i + 1 < len(current):
                pairs.append(f"{current[i]}, but {current[i + 1][0].lower() + current[i + 1][1:]}")
            else:
                pairs.append(current[i])
        text = ". ".join(pairs) + "."
    else:
        text = ". ".join(current) + "."

    lexical_family = "holdout" if split == "lexical_holdout" else ("alt" if split in {"development_ood", "compositional_holdout"} else "core")
    return text, annotations, {
        "semantic_template_family": f"state-plan-{split}",
        "surface_realization_family": style,
        "lexical_family": lexical_family,
        "construction_family": "scope-contrast" if split == "scope_holdout" else ("temporal-mixed" if split == "temporal_holdout" else "assertive-propositions"),
    }


def _record(state: Mapping[str, Any], split: str, index: int, spec: Mapping[str, Any], *, rendering_variant: str | None = None, pair_id: str | None = None, pair_member: str | None = None) -> dict[str, Any]:
    oracle = evaluate(state, spec=spec)
    if oracle.status != "VALID_DECISION" or oracle.action is None:
        raise RuntimeError("generator attempted invalid state")
    text, propositions, families = render_state(state, split, index, rendering_variant=rendering_variant)
    record = {
        "id": f"v7-{split}-{index:05d}",
        "split": split,
        "text": text,
        "state": dict(state),
        "action": oracle.action,
        "oracle_rule": oracle.matched_rule,
        "propositions": propositions,
        "metadata": families,
    }
    if pair_id is not None:
        record["pair_id"] = pair_id
        record["pair_member"] = pair_member
    return record


def _counterfactual_records(spec: Mapping[str, Any], count: int, seed: int) -> list[dict[str, Any]]:
    bases = _balanced_states(spec, count // 2, seed, compositional_only=None)
    records: list[dict[str, Any]] = []
    preferred = ("permission", "risk", "information", "completed", "execution_possible", "reversibility", "need")
    for pair_index, base in enumerate(bases):
        mutated = None
        for offset in range(len(preferred)):
            field = preferred[(pair_index + offset) % len(preferred)]
            definition = spec["state_schema"][field]
            values = [False, True] if definition["type"] == "boolean" else list(definition["values"])
            values = sorted(values, key=lambda v: stable_int(seed, pair_index, field, v))
            for value in values:
                if value == base[field]:
                    continue
                candidate = dict(base)
                candidate[field] = value
                if validate_state(spec, candidate).valid and evaluate(candidate, spec=spec).status == "VALID_DECISION":
                    mutated = candidate
                    break
            if mutated is not None:
                break
        if mutated is None:
            raise RuntimeError("failed to build counterfactual pair")
        pair_id = f"cf-{pair_index:04d}"
        records.append(_record(base, "counterfactual", pair_index * 2, spec, rendering_variant="declarative", pair_id=pair_id, pair_member="base"))
        records.append(_record(mutated, "counterfactual", pair_index * 2 + 1, spec, rendering_variant="declarative", pair_id=pair_id, pair_member="mutated"))
    return records


def _invariance_records(spec: Mapping[str, Any], count: int, seed: int) -> list[dict[str, Any]]:
    states = _balanced_states(spec, count // 2, seed, compositional_only=None)
    records: list[dict[str, Any]] = []
    styles = ("declarative", "bullet", "terse", "conversation", "reordered", "multisentence")
    for pair_index, state in enumerate(states):
        pair_id = f"inv-{pair_index:04d}"
        records.append(_record(state, "invariance", pair_index * 2, spec, rendering_variant="declarative", pair_id=pair_id, pair_member="base"))
        records.append(_record(state, "invariance", pair_index * 2 + 1, spec, rendering_variant=styles[1 + stable_int(seed, pair_index) % (len(styles) - 1)], pair_id=pair_id, pair_member="variant"))
    return records


def generate_split(split: str, spec: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    policy = dict(spec) if spec is not None else load_spec()
    count = SIZES[split]
    seed = SEEDS[split]
    if split == "counterfactual":
        return _counterfactual_records(policy, count, seed)
    if split == "invariance":
        return _invariance_records(policy, count, seed)
    compositional_only = True if split == "compositional_holdout" else (False if split in {"train", "validation"} else None)
    states = _balanced_states(policy, count, seed, compositional_only=compositional_only)
    return [_record(state, split, i, policy) for i, state in enumerate(states)]


def write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(canonical_json(record) + "\n" for record in records)
    path.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_all(output_dir: str | Path) -> dict[str, Any]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    spec = load_spec()
    hashes: dict[str, str] = {}
    family_sets: dict[str, dict[str, list[str]]] = {}
    counts: dict[str, int] = {}
    for split in SIZES:
        records = generate_split(split, spec)
        path = root / f"{split}.jsonl"
        hashes[path.name] = write_jsonl(path, records)
        counts[split] = len(records)
        family_sets[split] = {
            key: sorted({str(record["metadata"][key]) for record in records})
            for key in ("semantic_template_family", "surface_realization_family", "lexical_family", "construction_family")
        }
    manifest = {
        "candidate": "Candidate-v7 Proposition-Logic Semantic Reasoning",
        "generator_revision": "v7-proposition-logic-r1",
        "direction": "formal_state->semantic_plan->typed_propositions->surface_realization",
        "counts": counts,
        "seeds": SEEDS,
        "hashes": hashes,
        "families": family_sets,
        "lexical_isolation": sorted(set(family_sets["train"]["lexical_family"]) & set(family_sets["lexical_holdout"]["lexical_family"])) == [],
        "compositional_rule": "signature_mod_7==0 held out from train/validation",
    }
    manifest_text = json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    (root / "manifest.json").write_text(manifest_text, encoding="utf-8", newline="\n")
    manifest["manifest_sha256"] = hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()
    return manifest
