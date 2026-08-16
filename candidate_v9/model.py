from __future__ import annotations

import re
from functools import lru_cache
from dataclasses import dataclass
from typing import Any, Iterable

from .lexicon import AMBIGUOUS, COMPILED, CRITICAL, CURRENT, EARLIER, PATTERNS, SAFE_DEFAULT
from .policy import forbidden_act, oracle_action, valid_permission_side_pairs, valid_state

@dataclass(frozen=True)
class EvidenceEvent:
    factor: str
    value: Any
    text: str
    start: int
    rank: int
    ambiguous: bool


@dataclass(frozen=True)
class Prediction:
    action: str
    state: dict[str, Any]
    raw_state: dict[str, Any] | None
    positive_evidence: dict[str, list[str]]
    negative_evidence: dict[str, list[str]]
    unresolved_fields: tuple[str, ...]
    contradicted_fields: tuple[str, ...]
    act_eligible: bool
    prohibited: bool
    certain: bool
    architecture: str
    projection_log: tuple[str, ...]
    valid_by_construction: bool


def _sentences(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    pos = 0
    for piece in re.split(r"(?<=[.!?;])\s+|\n+", text):
        piece = piece.strip()
        if not piece:
            continue
        idx = text.find(piece, pos)
        if idx < 0:
            idx = pos
        out.append((idx, piece))
        pos = idx + len(piece)
    return out


@lru_cache(maxsize=8192)
def _sentence_matches(sentence: str, factor: str) -> tuple[tuple[Any, str, int, int, bool], ...]:
    rank = 4 if CURRENT.search(sentence) else (1 if EARLIER.search(sentence) else 2)
    ambiguous = bool(AMBIGUOUS.search(sentence))
    lowered = sentence.lower()
    found: list[tuple[Any, str, int, int, bool]] = []
    for value, patterns in COMPILED[factor].items():
        for pattern in patterns:
            for match in pattern.finditer(sentence):
                # Sentence-level negation guards prevent a positive lexical cue
                # embedded inside an explicit negative statement from voting twice.
                if factor == "permission" and value == "granted" and re.search(r"\bno (?:authorization|approval|permission|consent|clearance).{0,25}(?:granted|obtained|recorded)\b|\bnot (?:granted|approved|obtained)\b", lowered):
                    continue
                if factor == "clarification_possible" and value is True and re.search(r"\b(?:not possible|unavailable|cannot ask|not allowed|closed)\b", lowered):
                    continue
                if factor == "execution_possible" and value is True and re.search(r"\b(?:not operationally feasible|impossible|unavailable|infeasible|blocked|cannot execute|cannot proceed)\b", lowered):
                    continue
                if factor == "deferral_available" and value is True and re.search(r"\b(?:no later|cannot be deferred|cannot defer|unavailable|not allowed)\b", lowered):
                    continue
                if factor == "acknowledged" and value is True and re.search(r"\b(?:not acknowledged|unacknowledged|no acknowledgement|acknowledgement is not present)\b", lowered):
                    continue
                if factor == "reversibility" and value == "reversible" and re.search(r"\b(?:no rollback|cannot be undone|cannot be reversed|permanent|nonreversible)\b|(?<!not )\birreversible\b", lowered):
                    continue
                found.append((value, match.group(0), match.start(), rank, ambiguous))
    unique: dict[tuple[Any, int, str], tuple[Any, str, int, int, bool]] = {}
    for item in found:
        value, text, offset, item_rank, item_ambiguous = item
        unique[(value, offset, text.lower())] = item
    return tuple(sorted(unique.values(), key=lambda item: (item[3], item[2])))


def _events(text: str, factor: str) -> list[EvidenceEvent]:
    out: list[EvidenceEvent] = []
    for base, sentence in _sentences(text):
        for value, matched, offset, rank, ambiguous in _sentence_matches(sentence, factor):
            out.append(EvidenceEvent(factor, value, matched, base + offset, rank, ambiguous))
    return sorted(out, key=lambda e: (e.rank, e.start))


def _definite_frontier(events: Iterable[EvidenceEvent]) -> list[EvidenceEvent]:
    definite = [event for event in events if not event.ambiguous]
    if not definite:
        return []
    rank = max(event.rank for event in definite)
    return [event for event in definite if event.rank == rank]


def _resolve_independent(events: list[EvidenceEvent], factor: str, *, contradiction_last_wins: bool) -> tuple[Any, bool, bool]:
    frontier = _definite_frontier(events)
    if not frontier:
        return SAFE_DEFAULT[factor], False, False
    values = {event.value for event in frontier}
    contradicted = len(values) > 1
    if contradicted and not contradiction_last_wins:
        return SAFE_DEFAULT[factor], False, True
    chosen = max(frontier, key=lambda event: event.start)
    return chosen.value, True, contradicted


def _value_score(events: list[EvidenceEvent], value: Any, *, factor: str) -> float:
    frontier = _definite_frontier(events)
    if not frontier:
        return 0.0
    matching = [event for event in frontier if event.value == value]
    if not matching:
        return 0.0
    # Side-effect scope is slightly heavier than permission scope. If explicit
    # evidence is jointly invalid, preserve the effect scope and choose the
    # conservative permission compatible with that scope.
    factor_weight = 1.10 if factor == "side_effect" else 1.0
    return factor_weight * (100.0 * len(matching) + max(event.start for event in matching) / 1_000_000.0)


def _joint_permission_side(
    permission_events: list[EvidenceEvent],
    side_events: list[EvidenceEvent],
    *,
    contradiction_last_wins: bool,
) -> tuple[str, str, bool, bool, bool, bool]:
    # Returns permission, side_effect, permission_resolved, side_resolved,
    # permission_contradicted, side_contradicted.
    p_frontier = _definite_frontier(permission_events)
    s_frontier = _definite_frontier(side_events)
    p_values = {event.value for event in p_frontier}
    s_values = {event.value for event in s_frontier}
    p_contra = len(p_values) > 1
    s_contra = len(s_values) > 1

    if contradiction_last_wins:
        # V9-B keeps a last-event preference inside the valid joint domain.
        p_last = max(p_frontier, key=lambda e: e.start).value if p_frontier else None
        s_last = max(s_frontier, key=lambda e: e.start).value if s_frontier else None
    else:
        p_last = None if p_contra else (next(iter(p_values)) if p_values else None)
        s_last = None if s_contra else (next(iter(s_values)) if s_values else None)

    pair_priority = {
        ("not_required", "none"): 6,
        ("missing", "external"): 5,
        ("missing", "local"): 4,
        ("not_required", "local"): 3,
        ("granted", "external"): 2,
        ("granted", "local"): 1,
    }
    scored: list[tuple[float, int, str, str]] = []
    for permission, side in valid_permission_side_pairs():
        score = _value_score(permission_events, permission, factor="permission") + _value_score(side_events, side, factor="side_effect")
        if p_last is not None and permission == p_last:
            score += 0.01
        if s_last is not None and side == s_last:
            score += 0.011
        # Safe prior only matters when evidence is missing or exactly tied.
        if not p_frontier and permission == "missing" and side != "none":
            score += 0.001
        if not s_frontier and side == "local":
            score += 0.001
        scored.append((score, pair_priority[(permission, side)], permission, side))
    _, _, permission, side = max(scored)
    p_resolved = bool(p_frontier) and (contradiction_last_wins or not p_contra)
    s_resolved = bool(s_frontier) and (contradiction_last_wins or not s_contra)
    return permission, side, p_resolved, s_resolved, p_contra, s_contra


def _project_valid(raw: dict[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]:
    state = dict(raw)
    log: list[str] = []
    if state["side_effect"] == "none" and state["permission"] != "not_required":
        log.append(f"permission:{state['permission']}->not_required because side_effect=none")
        state["permission"] = "not_required"
    elif state["side_effect"] == "external" and state["permission"] == "not_required":
        log.append("permission:not_required->missing because side_effect=external")
        state["permission"] = "missing"
    return state, tuple(log)


def _fallback_action(state: dict[str, Any]) -> str:
    if state["need"] == "none":
        return "WAIT" if state["deferral_available"] else "IGNORE"
    if state["clarification_possible"]:
        return "ASK"
    if state["need"] == "material" and state["urgency"] in ("high", "expired"):
        return "NOTIFY"
    if state["deferral_available"]:
        return "WAIT"
    return "SUGGEST"


def predict(text: str, architecture: str = "V9-C") -> Prediction:
    if architecture not in {"V9-A", "V9-B", "V9-C"}:
        raise ValueError(f"unknown architecture: {architecture}")

    events = {factor: _events(text, factor) for factor in PATTERNS}
    state: dict[str, Any] = {}
    resolved: dict[str, bool] = {}
    contradicted: dict[str, bool] = {}
    raw_state: dict[str, Any] | None = None
    projection_log: tuple[str, ...] = tuple()

    contradiction_last_wins = architecture in {"V9-A", "V9-B"}

    if architecture == "V9-A":
        raw_state = {}
        for factor in PATTERNS:
            value, ok, contra = _resolve_independent(events[factor], factor, contradiction_last_wins=True)
            raw_state[factor] = value
            resolved[factor] = ok
            contradicted[factor] = contra
        state, projection_log = _project_valid(raw_state)
    else:
        p, side, p_ok, s_ok, p_contra, s_contra = _joint_permission_side(
            events["permission"], events["side_effect"], contradiction_last_wins=contradiction_last_wins
        )
        state["permission"] = p
        state["side_effect"] = side
        resolved["permission"] = p_ok
        resolved["side_effect"] = s_ok
        contradicted["permission"] = p_contra
        contradicted["side_effect"] = s_contra
        for factor in PATTERNS:
            if factor in {"permission", "side_effect"}:
                continue
            value, ok, contra = _resolve_independent(
                events[factor], factor, contradiction_last_wins=contradiction_last_wins
            )
            state[factor] = value
            resolved[factor] = ok
            contradicted[factor] = contra

    if not valid_state(state):
        # This is a defensive assertion, not a semantic rescue. Reaching it is
        # a Candidate-v9 defect because output validity is an architecture invariant.
        raise AssertionError(f"Candidate-v9 emitted invalid state: {state}")

    unresolved_fields = tuple(sorted(field for field, ok in resolved.items() if not ok))
    contradicted_fields = tuple(sorted(field for field, flag in contradicted.items() if flag))
    base_action = oracle_action(state)
    prohibited = forbidden_act(state)
    critical_resolved = all(resolved.get(field, False) for field in CRITICAL)
    no_critical_contradiction = all(not contradicted.get(field, False) for field in CRITICAL)
    act_eligible = base_action == "ACT" and critical_resolved and no_critical_contradiction and not prohibited
    action = base_action
    if base_action == "ACT" and not act_eligible:
        action = _fallback_action(state)

    positive: dict[str, list[str]] = {}
    negative: dict[str, list[str]] = {}
    for factor, factor_events in events.items():
        positive[factor] = [event.text for event in factor_events if not event.ambiguous and event.value == state[factor]]
        negative[factor] = [event.text for event in factor_events if event.ambiguous or event.value != state[factor]]

    certain = not unresolved_fields and not contradicted_fields and not any(event.ambiguous for values in events.values() for event in values)
    return Prediction(
        action=action,
        state=state,
        raw_state=raw_state,
        positive_evidence=positive,
        negative_evidence=negative,
        unresolved_fields=unresolved_fields,
        contradicted_fields=contradicted_fields,
        act_eligible=act_eligible,
        prohibited=prohibited,
        certain=certain,
        architecture=architecture,
        projection_log=projection_log,
        valid_by_construction=True,
    )
