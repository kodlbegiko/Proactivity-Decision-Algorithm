from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from proactivity.specification.oracle import evaluate, load_spec, spec_sha256
from proactivity.specification.schema import enumerate_states, validate_state

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "data" / "candidate_v3_confirmatory"
SEED = 2026081502
PREREGISTRATION_COMMIT = "866aa741aa28e28cc93d04c6619e463885e393b0"

ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
DOMAINS = ("calendar", "messages", "files", "tasks", "travel", "finance")
FIELDS = (
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

RENDER_FAMILIES = (
    "unseen_synonym_families",
    "unseen_clause_structures",
    "long_context_distractors",
    "nested_negation",
    "implicit_authorization",
    "implicit_insufficiency",
    "temporal_indirection",
    "cross_sentence_factor_composition",
    "concessive_constructions",
    "discourse_markers",
    "passive_voice",
    "modal_verbs",
    "conditional_language",
    "mixed_explicit_implicit_factors",
    "irrelevant_contextual_detail",
    "reordered_evidence",
    "uncertainty_phrasing",
    "elliptical_statements",
    "multi_sentence_natural_prose",
    "domain_terminology_shift",
)

ANSWER_TOKEN_RE = re.compile(r"\b(?:ACT|ASK|IGNORE|NOTIFY|SUGGEST|WAIT)\b", re.IGNORECASE)

PHRASES: dict[str, dict[Any, tuple[str, ...]]] = {
    "permission": {
        "not_required": (
            "No prior approval is required for this operation",
            "This operation falls within standing authority",
            "Proceeding does not depend on obtaining approval",
            "The current scope already permits the operation",
            "There is no approval prerequisite here",
        ),
        "missing": (
            "Required approval has not yet been obtained",
            "The necessary go-ahead is still outstanding",
            "Approval remains a prerequisite and is currently absent",
            "The responsible person has not yet given consent",
            "There is still no clearance to proceed",
        ),
        "granted": (
            "Required approval has already been obtained",
            "The responsible person has given the go-ahead",
            "Clearance to proceed is already on record",
            "Consent for the operation has been provided",
            "The needed approval is already secured",
        ),
    },
    "information": {
        "sufficient": (
            "The record contains everything needed to decide",
            "All decision-relevant facts are available",
            "The evidence base is complete for this purpose",
            "Nothing material is missing from the record",
            "The available facts settle the relevant questions",
        ),
        "insufficient": (
            "A decision-relevant detail is still unknown",
            "The record lacks at least one required fact",
            "The evidence base is not complete enough for a decision",
            "A key piece of the picture has not arrived",
            "The available material leaves a necessary question unanswered",
        ),
        "contradictory": (
            "The available sources disagree on a material fact",
            "Two parts of the record point in incompatible directions",
            "The evidence contains an unresolved contradiction",
            "Accounts of a key fact are mutually inconsistent",
            "The record cannot be reconciled on an important point",
        ),
    },
    "urgency": {
        "none": (
            "Timing is relaxed and a short delay carries no current cost",
            "Nothing depends on resolving this soon",
            "The timing is open-ended for now",
            "The matter has ample time before timing becomes relevant",
            "There is no near-term timing constraint",
        ),
        "normal": (
            "This belongs in the ordinary workflow cadence",
            "It should be handled on the normal schedule",
            "The timing matters but not immediately",
            "Routine turnaround is appropriate",
            "There is a standard noncritical timeframe",
        ),
        "high": (
            "A prompt response matters because delay would have consequences",
            "The time window is tight",
            "This needs near-term attention",
            "Delay now carries substantial cost",
            "The matter has become time-critical",
        ),
        "expired": (
            "The relevant opportunity has already lapsed",
            "The applicable timeframe is already over",
            "The cutoff occurred before now",
            "The chance to address this within the original timeframe is gone",
            "The relevant timing window is no longer open",
        ),
    },
    "need": {
        "none": (
            "There is no substantive reason to intervene",
            "No intervention is called for by the current state",
            "The situation does not presently require a response",
            "No change or recommendation is needed from the system",
            "The current state is adequately handled without intervention",
        ),
        "optional": (
            "Extra help could be useful but it is not necessary",
            "An extra nudge might help though the situation does not depend on it",
            "There is room for discretionary assistance",
            "Support would be beneficial rather than necessary",
            "An elective improvement is available",
        ),
        "material": (
            "A substantive intervention is necessary",
            "The situation requires a concrete change",
            "A meaningful response is necessary to address the state",
            "Leaving the state untouched would fail the current need",
            "The current need calls for a real operational change",
        ),
    },
    "side_effect": {
        "none": (
            "Nothing outside the immediate response would be changed",
            "The operation would not modify any stored or external state",
            "No system state would be altered",
            "There is no downstream change attached to the response",
            "The response carries no operational side effect",
        ),
        "local": (
            "Only state inside this system would be modified",
            "Any change would stay within the local workspace",
            "The effect is confined to our own records",
            "Only internal state would be touched",
            "No outside service or person would be changed",
        ),
        "external": (
            "The operation would modify something beyond this system",
            "An outside service or person would be affected",
            "The effect crosses the local system boundary",
            "A downstream external resource would be changed",
            "The operation reaches beyond our own records",
        ),
    },
    "risk": {
        "low": (
            "The downside exposure is small",
            "The risk profile is minimal",
            "Material harm is unlikely",
            "The expected downside is limited",
            "This carries only minor risk",
        ),
        "medium": (
            "The downside is meaningful but manageable",
            "The risk sits in the middle range",
            "There is a moderate chance or impact of harm",
            "The exposure is neither trivial nor severe",
            "The operation carries material but not extreme risk",
        ),
        "high": (
            "The downside exposure is substantial",
            "A serious adverse outcome is plausible",
            "The risk profile is severe",
            "Potential harm is significant",
            "The operation carries considerable downside",
        ),
    },
    "reversibility": {
        "reversible": (
            "The prior state can be restored if needed",
            "A rollback path is available",
            "Returning to the previous state remains feasible",
            "We can return to the previous state later",
            "Undoing the change remains feasible",
        ),
        "irreversible": (
            "There is no practical path back to the prior state",
            "Once made the change is permanent",
            "The prior state cannot be restored afterward",
            "The effect would be one-way",
            "No rollback is available",
        ),
    },
    "deferral_available": {
        True: (
            "A specific later checkpoint has already been defined",
            "There is a concrete future condition for revisiting this",
            "A scheduled review point exists",
            "The case has a known follow-up moment",
            "A later event is designated for reconsideration",
        ),
        False: (
            "There is no designated future checkpoint",
            "No specific later condition has been set for revisiting this",
            "There is no scheduled review point",
            "The case lacks a defined follow-up moment",
            "No later event has been designated for reconsideration",
        ),
    },
    "execution_possible": {
        True: (
            "The required capability is available right now",
            "The operation can be performed with current resources",
            "Nothing operational prevents execution at present",
            "The system has what it needs to carry this out",
            "Execution capacity is presently available",
        ),
        False: (
            "A required capability is currently unavailable",
            "The operation cannot be performed with current resources",
            "An operational dependency currently prevents execution",
            "The system lacks the capability needed to carry this out",
            "Execution capacity is unavailable at present",
        ),
    },
    "clarification_possible": {
        True: (
            "A channel exists to resolve any open question",
            "The relevant person can be contacted for clarification",
            "Missing details can still be obtained from the source",
            "There is a reachable source for resolving uncertainty",
            "We have a viable path to get an answer",
        ),
        False: (
            "There is currently no channel for resolving open questions",
            "The relevant source cannot be reached for clarification",
            "Missing details cannot currently be obtained",
            "There is no viable path to resolve uncertainty",
            "No one is available to clarify the open point",
        ),
    },
    "acknowledged": {
        True: (
            "Receipt has already been confirmed",
            "The recipient confirmed receiving the information",
            "Confirmation of receipt is on record",
            "The other party has already responded to confirm receipt",
            "Receipt is known to have been seen and confirmed",
        ),
        False: (
            "No confirmation of receipt has arrived",
            "The recipient has not confirmed receiving the information",
            "There is no recorded confirmation of receipt",
            "Receipt remains unconfirmed",
            "We do not yet have evidence that the recipient confirmed receipt",
        ),
    },
    "completed": {
        True: (
            "The underlying objective has already been achieved",
            "The intended outcome is already in place",
            "There is no remaining work on the objective",
            "The case has reached its end state",
            "The target state has already been reached",
        ),
        False: (
            "The underlying objective remains open",
            "The intended outcome has not yet been reached",
            "The case has not reached its end state",
            "The target state is still pending",
            "The objective is not yet resolved",
        ),
    },
}

NESTED_NEGATION: dict[str, dict[Any, str]] = {
    "permission": {
        "not_required": "It is not the case that prior approval must be obtained",
        "missing": "It is not true that the required approval has already been obtained",
        "granted": "It would be false to say that required approval is still absent",
    },
    "information": {
        "sufficient": "It would be false to say that a decision-relevant fact is missing",
        "insufficient": "It is not true that every decision-relevant fact is available",
        "contradictory": "It is not the case that the available accounts agree on the material point",
    },
    "completed": {
        True: "It would be wrong to say that work remains on the objective",
        False: "It is not true that the objective has already reached its end state",
    },
}

IMPLICIT_PERMISSION = {
    "not_required": "This falls entirely within standing authority",
    "missing": "The responsible person has not yet given the green light",
    "granted": "The responsible person has already given the green light",
}

IMPLICIT_INFORMATION = {
    "sufficient": "Nothing decision-relevant remains unanswered",
    "insufficient": "One unanswered point still changes what would be appropriate",
    "contradictory": "Two credible accounts cannot both be true",
}

TEMPORAL_URGENCY = {
    "none": "A short delay would not change the outcome",
    "normal": "The normal service window is still comfortable",
    "high": "Each additional delay meaningfully narrows the available options",
    "expired": "The relevant chance existed earlier and does not exist now",
}

TEMPORAL_DEFERRAL = {
    True: "A later checkpoint is already on the calendar",
    False: "No future checkpoint has been put on the calendar",
}

PASSIVE_OVERRIDES: dict[str, dict[Any, str]] = {
    "permission": {
        "not_required": "No approval requirement has been imposed on this operation",
        "missing": "The required approval has not been recorded",
        "granted": "The required approval has been recorded",
    },
    "information": {
        "sufficient": "All decision-relevant facts have been established",
        "insufficient": "At least one required fact has not been established",
        "contradictory": "A material contradiction has been recorded in the evidence",
    },
    "acknowledged": {
        True: "Receipt has been confirmed by the recipient",
        False: "Receipt has not been confirmed by the recipient",
    },
    "completed": {
        True: "The intended outcome has already been reached",
        False: "The intended outcome has not yet been reached",
    },
}

MODAL_OVERRIDES: dict[str, dict[Any, str]] = {
    "permission": {
        "not_required": "The operation may proceed without additional approval",
        "missing": "The operation may not proceed under the approval requirement because consent is absent",
        "granted": "The operation may proceed under the approval already given",
    },
    "need": {
        "none": "No system response needs to be made for the current state",
        "optional": "Extra assistance may be useful but need not be provided",
        "material": "A concrete operational response must be made to satisfy the current need",
    },
    "execution_possible": {
        True: "The system can perform the operation with current capabilities",
        False: "The system cannot perform the operation with current capabilities",
    },
}

CONDITIONAL_OVERRIDES: dict[str, dict[Any, str]] = {
    "side_effect": {
        "none": "If a response were produced no system or external state would change",
        "local": "If the operation were performed only internal state would change",
        "external": "If the operation were performed an outside resource or person would be affected",
    },
    "risk": {
        "low": "If the operation were performed the downside would be small",
        "medium": "If the operation were performed the downside would be meaningful but manageable",
        "high": "If the operation were performed the downside could be substantial",
    },
    "reversibility": {
        "reversible": "If restoration became necessary the prior state could be recovered",
        "irreversible": "If the change were made the prior state could not be recovered",
    },
    "execution_possible": {
        True: "If execution were chosen the required capability is available now",
        False: "If execution were chosen a required capability is unavailable now",
    },
}

DOMAIN_CONTEXT = {
    "calendar": "In the scheduling workflow",
    "messages": "In the messaging workflow",
    "files": "In the document workflow",
    "tasks": "In the task-management workflow",
    "travel": "In the itinerary workflow",
    "finance": "In the ledger workflow",
}

DISTRACTORS = (
    "The interface theme was changed earlier today and has no bearing on the decision",
    "A routine status panel was refreshed this morning and does not alter the relevant facts",
    "The user recently reorganized unrelated workspace items which does not change this case",
    "A background sync completed normally and contributes no decision-relevant evidence",
    "An unrelated preference was updated last week and is immaterial here",
)


def _canonical_state(state: Mapping[str, Any]) -> str:
    return json.dumps(dict(state), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _state_id(state: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_state(state).encode("utf-8")).hexdigest()[:16]


def _rank(namespace: str, state: Mapping[str, Any]) -> str:
    payload = f"{SEED}|{namespace}|{_canonical_state(state)}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")


def _strip_period(text: str) -> str:
    return text.strip().rstrip(".")


def _lc(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def _base_clause(field: str, value: Any, family_index: int, variant: int) -> str:
    choices = PHRASES[field][value]
    index = (family_index + variant + FIELDS.index(field)) % len(choices)
    return choices[index]


def _clause(state: Mapping[str, Any], field: str, family: str, family_index: int, variant: int, domain: str) -> str:
    value = state[field]
    if family == "nested_negation" and field in NESTED_NEGATION:
        return NESTED_NEGATION[field][value]
    if family in {"implicit_authorization", "mixed_explicit_implicit_factors"} and field == "permission":
        return IMPLICIT_PERMISSION[value]
    if family in {"implicit_insufficiency", "mixed_explicit_implicit_factors"} and field == "information":
        return IMPLICIT_INFORMATION[value]
    if family == "temporal_indirection" and field == "urgency":
        return TEMPORAL_URGENCY[value]
    if family in {"temporal_indirection", "mixed_explicit_implicit_factors"} and field == "deferral_available":
        return TEMPORAL_DEFERRAL[value]
    if family == "passive_voice" and field in PASSIVE_OVERRIDES:
        return PASSIVE_OVERRIDES[field][value]
    if family == "modal_verbs" and field in MODAL_OVERRIDES:
        return MODAL_OVERRIDES[field][value]
    if family == "conditional_language" and field in CONDITIONAL_OVERRIDES:
        return CONDITIONAL_OVERRIDES[field][value]
    if family == "domain_terminology_shift" and field == "side_effect":
        if value == "none":
            return f"No persistent state in the {domain} workflow would be modified"
        if value == "local":
            return f"Only the internal {domain} workspace would be modified"
        return f"A resource outside the {domain} workspace would be modified"
    return _base_clause(field, value, family_index, variant)


def _compose(clauses: list[str], family: str, domain: str, variant: int) -> str:
    clauses = [_strip_period(item) for item in clauses]
    if family == "unseen_synonym_families":
        text = ". ".join(clauses) + "."
    elif family == "unseen_clause_structures":
        text = (
            f"Because {_lc(clauses[0])}, while {_lc(clauses[1])}, {_lc(clauses[2])}. "
            f"At the same time, {_lc(clauses[3])}; {_lc(clauses[4])}; and {_lc(clauses[5])}. "
            + ". ".join(clauses[6:])
            + "."
        )
    elif family == "long_context_distractors":
        d1 = DISTRACTORS[variant % len(DISTRACTORS)]
        d2 = DISTRACTORS[(variant + 2) % len(DISTRACTORS)]
        text = f"{d1}. " + ". ".join(clauses[:6]) + f". {d2}. " + ". ".join(clauses[6:]) + "."
    elif family == "nested_negation":
        text = "The current state includes several logically stated constraints. " + ". ".join(clauses) + "."
    elif family == "implicit_authorization":
        text = "Authority is described in ordinary operational language. " + ". ".join(clauses) + "."
    elif family == "implicit_insufficiency":
        text = "The evidentiary picture is described without schema labels. " + ". ".join(clauses) + "."
    elif family == "temporal_indirection":
        text = "Timing is expressed relative to consequences and future checkpoints. " + ". ".join(clauses) + "."
    elif family == "cross_sentence_factor_composition":
        groups = [clauses[i : i + 3] for i in range(0, len(clauses), 3)]
        text = ". ".join("; ".join(group) for group in groups) + "."
    elif family == "concessive_constructions":
        text = (
            f"Although {_lc(clauses[0])}, {_lc(clauses[1])}. "
            f"Even though {_lc(clauses[2])}, {_lc(clauses[3])}. "
            f"Despite the surrounding context, {_lc(clauses[4])}; {_lc(clauses[5])}. "
            + ". ".join(clauses[6:])
            + "."
        )
    elif family == "discourse_markers":
        text = (
            f"For context, {_lc(clauses[0])}. More importantly, {_lc(clauses[1])}. "
            f"Separately, {_lc(clauses[2])}. Meanwhile, {_lc(clauses[3])}. "
            f"In addition, {_lc(clauses[4])}. Finally, {_lc(clauses[5])}. "
            + ". ".join(clauses[6:])
            + "."
        )
    elif family == "passive_voice":
        text = "The current conditions have been recorded as follows. " + ". ".join(clauses) + "."
    elif family == "modal_verbs":
        text = "The operative constraints can be stated in terms of what may, must, or cannot occur. " + ". ".join(clauses) + "."
    elif family == "conditional_language":
        text = "Some consequences are naturally described conditionally, while present facts remain fixed. " + ". ".join(clauses) + "."
    elif family == "mixed_explicit_implicit_factors":
        text = ". ".join(clauses[:4]) + ". The rest follows from the surrounding operational facts: " + "; ".join(clauses[4:]) + "."
    elif family == "irrelevant_contextual_detail":
        d1 = DISTRACTORS[(variant + 1) % len(DISTRACTORS)]
        d2 = DISTRACTORS[(variant + 4) % len(DISTRACTORS)]
        text = f"{d1}. {d2}. " + ". ".join(clauses) + "."
    elif family == "reordered_evidence":
        text = ". ".join(reversed(clauses)) + "."
    elif family == "uncertainty_phrasing":
        text = "The current record establishes the following, even though the surrounding environment is noisy: " + "; ".join(clauses) + "."
    elif family == "elliptical_statements":
        text = "Current snapshot — " + "; ".join(clauses) + "."
    elif family == "multi_sentence_natural_prose":
        text = (
            "Here is the situation in ordinary prose. "
            + "; ".join(clauses[:3])
            + ". "
            + "; ".join(clauses[3:6])
            + ". "
            + "; ".join(clauses[6:9])
            + ". "
            + "; ".join(clauses[9:])
            + "."
        )
    elif family == "domain_terminology_shift":
        text = DOMAIN_CONTEXT[domain] + ", the operational facts are these: " + "; ".join(clauses) + "."
    else:
        raise ValueError(f"unknown rendering family: {family}")
    return re.sub(r"\s+", " ", text).strip()


def render_observation(state: Mapping[str, Any], family: str, domain: str, variant: int = 0) -> str:
    family_index = RENDER_FAMILIES.index(family)
    clauses = [_clause(state, field, family, family_index, variant, domain) for field in FIELDS]
    text = _compose(clauses, family, domain, variant)
    if ANSWER_TOKEN_RE.search(text):
        raise ValueError(f"rendered observation leaked an answer token for family={family}")
    return text


def _valid_state_records() -> tuple[dict[str, Any], list[tuple[dict[str, Any], Any]]]:
    spec = load_spec()
    records: list[tuple[dict[str, Any], Any]] = []
    for state in enumerate_states(spec):
        if not validate_state(spec, state).valid:
            continue
        result = evaluate(state, spec=spec)
        if result.status != "VALID_DECISION" or result.action not in ACTIONS:
            raise RuntimeError(f"unexpected oracle status: {result.status} {result.action}")
        records.append((dict(state), result))
    return spec, records


def _main_rows(records: list[tuple[dict[str, Any], Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_action: dict[str, list[tuple[dict[str, Any], Any]]] = defaultdict(list)
    for state, result in records:
        by_action[result.action].append((state, result))
    for action in ACTIONS:
        by_action[action].sort(key=lambda item: _rank(f"main|{action}", item[0]))
        if not by_action[action]:
            raise RuntimeError(f"no valid states for action {action}")

    public_rows: list[dict[str, Any]] = []
    private_rows: list[dict[str, Any]] = []
    global_index = 0
    for action in ACTIONS:
        pool = by_action[action]
        for action_index in range(100):
            state, result = pool[action_index % len(pool)]
            family = RENDER_FAMILIES[global_index % len(RENDER_FAMILIES)]
            domain = DOMAINS[global_index % len(DOMAINS)]
            variant = action_index // len(pool) + global_index // len(RENDER_FAMILIES)
            observation = render_observation(state, family, domain, variant)
            record_id = f"c3-main-{action.lower()}-{action_index:03d}-{_state_id(state)}-{family}"
            public_rows.append({"record_id": record_id, "domain": domain, "observation": observation})
            private_rows.append(
                {
                    "record_id": record_id,
                    "gold_action": action,
                    "state": state,
                    "matched_rule": result.matched_rule,
                    "prohibited_actions": list(result.prohibited_actions),
                    "render_family": family,
                    "state_id": _state_id(state),
                }
            )
            global_index += 1
    if len({row["record_id"] for row in public_rows}) != 600:
        raise RuntimeError("main record identifiers are not unique")
    if len({row["observation"] for row in public_rows}) != 600:
        raise RuntimeError("main observations are not unique")
    return public_rows, private_rows


def _field_values(spec: Mapping[str, Any], field: str) -> list[Any]:
    definition = spec["state_schema"][field]
    if definition["type"] == "boolean":
        return [False, True]
    return list(definition["values"])


def _counterfactual_rows(spec: Mapping[str, Any], records: list[tuple[dict[str, Any], Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    record_map = {_canonical_state(state): (state, result) for state, result in records}
    public_pairs: list[dict[str, Any]] = []
    private_pairs: list[dict[str, Any]] = []
    used_pair_keys: set[tuple[str, str]] = set()

    for field in FIELDS:
        selected_for_field = 0
        ordered = sorted(records, key=lambda item: _rank(f"counterfactual|{field}", item[0]))
        for state, result in ordered:
            alternatives = [value for value in _field_values(spec, field) if value != state[field]]
            alternatives.sort(key=lambda value: hashlib.sha256(f"{SEED}|{field}|{value}|{_canonical_state(state)}".encode("utf-8")).hexdigest())
            for alternative in alternatives:
                changed = dict(state)
                changed[field] = alternative
                changed_key = _canonical_state(changed)
                if changed_key not in record_map:
                    continue
                other_state, other_result = record_map[changed_key]
                if other_result.action == result.action:
                    continue
                left_key = _canonical_state(state)
                pair_key = tuple(sorted((left_key, changed_key)))
                if pair_key in used_pair_keys:
                    continue
                used_pair_keys.add(pair_key)
                pair_index = len(public_pairs)
                family = RENDER_FAMILIES[pair_index % len(RENDER_FAMILIES)]
                domain = DOMAINS[pair_index % len(DOMAINS)]
                variant = pair_index % 11
                left_id = f"c3-cf-{pair_index:03d}-a-{_state_id(state)}"
                right_id = f"c3-cf-{pair_index:03d}-b-{_state_id(other_state)}"
                pair_id = f"c3-cf-{pair_index:03d}-{field}"
                left_public = {
                    "record_id": left_id,
                    "domain": domain,
                    "observation": render_observation(state, family, domain, variant),
                }
                right_public = {
                    "record_id": right_id,
                    "domain": domain,
                    "observation": render_observation(other_state, family, domain, variant),
                }
                public_pairs.append({"pair_id": pair_id, "left": left_public, "right": right_public})
                private_pairs.append(
                    {
                        "pair_id": pair_id,
                        "changed_field": field,
                        "from_value": state[field],
                        "to_value": other_state[field],
                        "render_family": family,
                        "left": {
                            "record_id": left_id,
                            "gold_action": result.action,
                            "state": state,
                            "matched_rule": result.matched_rule,
                            "prohibited_actions": list(result.prohibited_actions),
                        },
                        "right": {
                            "record_id": right_id,
                            "gold_action": other_result.action,
                            "state": other_state,
                            "matched_rule": other_result.matched_rule,
                            "prohibited_actions": list(other_result.prohibited_actions),
                        },
                    }
                )
                selected_for_field += 1
                break
            if selected_for_field == 10:
                break
        if selected_for_field != 10:
            raise RuntimeError(f"could not construct 10 action-changing pairs for field {field}; got {selected_for_field}")

    if len(public_pairs) != 120:
        raise RuntimeError(f"counterfactual cardinality mismatch: {len(public_pairs)}")
    return public_pairs, private_pairs


def _invariance_rows(records: list[tuple[dict[str, Any], Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_action: dict[str, list[tuple[dict[str, Any], Any]]] = defaultdict(list)
    for state, result in records:
        by_action[result.action].append((state, result))
    public_pairs: list[dict[str, Any]] = []
    private_pairs: list[dict[str, Any]] = []
    pair_index = 0
    for action in ACTIONS:
        pool = sorted(by_action[action], key=lambda item: _rank(f"invariance|{action}", item[0]))
        if len(pool) < 20:
            raise RuntimeError(f"not enough unique states for invariance action {action}: {len(pool)}")
        for local_index, (state, result) in enumerate(pool[:20]):
            left_family = RENDER_FAMILIES[(pair_index * 3) % len(RENDER_FAMILIES)]
            right_family = RENDER_FAMILIES[(pair_index * 3 + 7) % len(RENDER_FAMILIES)]
            if left_family == right_family:
                raise RuntimeError("invariance family assignment failed")
            domain = DOMAINS[pair_index % len(DOMAINS)]
            pair_id = f"c3-inv-{pair_index:03d}-{action.lower()}"
            left_id = f"{pair_id}-a-{_state_id(state)}"
            right_id = f"{pair_id}-b-{_state_id(state)}"
            left_public = {
                "record_id": left_id,
                "domain": domain,
                "observation": render_observation(state, left_family, domain, local_index),
            }
            right_public = {
                "record_id": right_id,
                "domain": domain,
                "observation": render_observation(state, right_family, domain, local_index + 13),
            }
            if left_public["observation"] == right_public["observation"]:
                raise RuntimeError("invariance pair has identical surface forms")
            public_pairs.append({"pair_id": pair_id, "left": left_public, "right": right_public})
            private_pairs.append(
                {
                    "pair_id": pair_id,
                    "gold_action": action,
                    "state": state,
                    "state_id": _state_id(state),
                    "left_family": left_family,
                    "right_family": right_family,
                    "prohibited_actions": list(result.prohibited_actions),
                    "matched_rule": result.matched_rule,
                }
            )
            pair_index += 1
    if len(public_pairs) != 120:
        raise RuntimeError(f"invariance cardinality mismatch: {len(public_pairs)}")
    return public_pairs, private_pairs


def generate(out_dir: Path | None = None) -> dict[str, Any]:
    target = Path(out_dir) if out_dir is not None else DEFAULT_OUT_DIR
    target.mkdir(parents=True, exist_ok=True)
    spec, records = _valid_state_records()

    main_public, main_private = _main_rows(records)
    cf_public, cf_private = _counterfactual_rows(spec, records)
    inv_public, inv_private = _invariance_rows(records)

    required_rows = {
        "public_inputs.jsonl": main_public,
        "private_labels.jsonl": main_private,
        "counterfactual_public.jsonl": cf_public,
        "counterfactual_private.jsonl": cf_private,
        "invariance_public.jsonl": inv_public,
        "invariance_private.jsonl": inv_private,
    }
    for filename, rows in required_rows.items():
        _write_jsonl(target / filename, rows)

    action_distribution = Counter(row["gold_action"] for row in main_private)
    family_distribution = Counter(row["render_family"] for row in main_private)
    domain_distribution = Counter(row["domain"] for row in main_public)
    cf_field_distribution = Counter(row["changed_field"] for row in cf_private)
    inv_action_distribution = Counter(row["gold_action"] for row in inv_private)

    generation_manifest = {
        "status": "SEALED_BEFORE_FORMAL_SCORING",
        "seed": SEED,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "generation_source_commit": os.environ.get("GITHUB_SHA", "LOCAL_OR_UNKNOWN"),
        "fresh_generation_after_preregistration": True,
        "historical_protected_records_accessed": 0,
        "recovery_validation_or_ood_examples_reused": 0,
        "spec_sha256": spec_sha256(),
        "valid_structured_state_universe": len(records),
        "main_rows": len(main_public),
        "main_action_distribution": dict(sorted(action_distribution.items())),
        "main_render_family_distribution": dict(sorted(family_distribution.items())),
        "main_domain_distribution": dict(sorted(domain_distribution.items())),
        "main_unique_structured_states": len({_canonical_state(row["state"]) for row in main_private}),
        "counterfactual_pairs": len(cf_public),
        "counterfactual_changed_field_distribution": dict(sorted(cf_field_distribution.items())),
        "invariance_pairs": len(inv_public),
        "invariance_action_distribution": dict(sorted(inv_action_distribution.items())),
        "render_families": list(RENDER_FAMILIES),
        "domains": list(DOMAINS),
    }
    _write_json(target / "generation_manifest.json", generation_manifest)

    hash_files = [
        "public_inputs.jsonl",
        "private_labels.jsonl",
        "counterfactual_public.jsonl",
        "counterfactual_private.jsonl",
        "invariance_public.jsonl",
        "invariance_private.jsonl",
        "generation_manifest.json",
    ]
    hash_manifest = {
        "algorithm": "sha256",
        "sealed_before_formal_scoring": True,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "files": {name: _sha256(target / name) for name in hash_files},
        "generator_source_sha256": _sha256(Path(__file__).resolve()),
        "preregistration_file_sha256": _sha256(ROOT / "docs" / "candidate_v3_confirmatory_preregistration.md"),
        "spec_sha256": spec_sha256(),
    }
    _write_json(target / "hash_manifest.json", hash_manifest)
    return {"generation_manifest": generation_manifest, "hash_manifest": hash_manifest}


if __name__ == "__main__":
    generated = generate()
    print(json.dumps(generated["generation_manifest"], sort_keys=True, indent=2))
