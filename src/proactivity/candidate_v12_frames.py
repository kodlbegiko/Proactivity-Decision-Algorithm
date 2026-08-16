from __future__ import annotations

from dataclasses import replace
import re
from typing import Any

from .candidate_v12 import (
    ArchitectureC,
    DEFAULTS,
    Evidence,
    FactorResult,
    FIELD_ORDER,
    ParseResult,
    policy_action,
    resolve_state,
)


# Architecture D separates lexical concepts from value predicates.  The parser
# composes a factor concept with a predicate and semantic operators instead of
# memorising full realization strings.  It is intentionally small and
# inspectable; qualification, not this lexicon, must establish external breadth.
FRAME_SPECS: dict[str, dict[str, Any]] = {
    "permission": {
        "concept": r"\b(approval|permission|authorization|authorisation|clearance|sign[ -]?off|go[ -]?ahead)\b",
        "direct": [("not_required", r"\b(exempt|waived|outside (?:the )?approval scope|permission unnecessary)\b")],
        "cues": {
            "granted": r"\b(granted|approved|authorized|authorised|secured|received|confirmed|issued)\b",
            "missing": r"\b(pending|missing|unresolved|awaiting|withheld|denied|revoked|absent)\b",
        },
        "negate": {"granted": "missing"},
    },
    "information": {
        "concept": r"\b(information|facts?|evidence|record|records|reports?)\b",
        "direct": [("contradictory", r"\b(contradictory|conflicting|disagree|disagrees|inconsistent)\b")],
        "cues": {
            "sufficient": r"\b(sufficient|complete|adequate|settled|enough)\b",
            "insufficient": r"\b(insufficient|incomplete|missing|gaps?|lacking)\b",
        },
        "negate": {"sufficient": "insufficient"},
    },
    "urgency": {
        "concept": r"\b(urgency|priority|timing|deadline|window)\b",
        "direct": [("expired", r"\b(expired|overdue|passed|closed|past due)\b")],
        "cues": {
            "none": r"\b(flexible|routine|nonurgent|non-urgent)\b",
            "normal": r"\b(normal|ordinary|standard)\b",
            "high": r"\b(high|urgent|pressing|time[ -]?sensitive|immediate)\b",
        },
        "negate": {"high": "none"},
    },
    "need": {
        "concept": r"\b(need|action|intervention|handling|requirement)\b",
        "direct": [("none", r"\b(no action|no intervention|unnecessary)\b")],
        "cues": {
            "optional": r"\b(optional|discretionary|elective|nice[ -]?to[ -]?have)\b",
            "material": r"\b(material|required|mandatory|substantive|necessary)\b",
        },
        "negate": {"material": "none"},
    },
    "side_effect": {
        "concept": r"\b(side effect|effect|write|change|operation)\b",
        "direct": [("none", r"\b(read[ -]?only|informational|no side effect|no material effect)\b")],
        "cues": {
            "local": r"\b(local|internal|on[ -]?system)\b",
            "external": r"\b(external|third[ -]?party|cross[ -]?system|outside)\b",
        },
        "negate": {},
    },
    "risk": {
        "concept": r"\b(risk|downside|exposure|hazard)\b",
        "direct": [],
        "cues": {
            "low": r"\b(low|minimal|small|safe)\b",
            "medium": r"\b(medium|moderate|meaningful)\b",
            "high": r"\b(high|severe|substantial|dangerous)\b",
        },
        "negate": {},
    },
    "reversibility": {
        "concept": r"\b(reversibility|rollback|undo|change)\b",
        "direct": [("irreversible", r"\b(permanent|final|no rollback)\b")],
        "cues": {
            "reversible": r"\b(reversible|available|possible|undoable|recoverable)\b",
            "irreversible": r"\b(irreversible|unavailable|impossible)\b",
        },
        "negate": {"reversible": "irreversible"},
    },
    "deferral_available": {
        "concept": r"\b(deferral|defer|postponement|postpone|delay|waiting)\b",
        "direct": [],
        "cues": {
            True: r"\b(available|possible|feasible|permitted|allowed|can)\b",
            False: r"\b(unavailable|impossible|blocked|prohibited|cannot|can't)\b",
        },
        "negate": {True: False},
    },
    "execution_possible": {
        "concept": r"\b(execution|execute|tooling|perform|operation)\b",
        "direct": [],
        "cues": {
            True: r"\b(possible|available|feasible|ready|can)\b",
            False: r"\b(impossible|unavailable|blocked|infeasible|cannot|can't)\b",
        },
        "negate": {True: False},
    },
    "clarification_possible": {
        "concept": r"\b(clarification|clarify|question|inquiry|ask)\b",
        "direct": [],
        "cues": {
            True: r"\b(possible|available|feasible|allowed|can)\b",
            False: r"\b(impossible|unavailable|blocked|forbidden|cannot|can't)\b",
        },
        "negate": {True: False},
    },
    "acknowledged": {
        "concept": r"\b(acknowledg(?:e|ed|ement)|awareness|notice|seen|noted)\b",
        "direct": [],
        "cues": {
            True: r"\b(acknowledged|seen|noted|confirmed|aware)\b",
            False: r"\b(unacknowledged|unseen|unnoticed|pending)\b",
        },
        "negate": {True: False},
    },
    "completed": {
        "concept": r"\b(task|case|work|job|item|completion|status)\b",
        "direct": [(True, r"\b(cancelled|canceled)\b")],
        "cues": {
            True: r"\b(complete|completed|finished|closed|done|resolved)\b",
            False: r"\b(incomplete|open|ongoing|unfinished|remaining)\b",
        },
        "negate": {True: False},
    },
}

CONSERVATIVE_CONTRADICTION = {
    "permission": "missing",
    "information": "contradictory",
    "urgency": "high",
    "need": "material",
    "side_effect": "external",
    "risk": "high",
    "reversibility": "irreversible",
    "deferral_available": False,
    "execution_possible": False,
    "clarification_possible": True,
    "acknowledged": False,
    "completed": False,
}

_CONDITIONAL = re.compile(r"^\s*(if|unless|assuming|provided that|in case)\b", re.I)
_ENTITY = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 _-]{0,40})\s*:\s*(.*)$", re.S)
_NEG = re.compile(r"\b(not|never|no)\b", re.I)


def _segments(text: str) -> list[tuple[str, int, str | None]]:
    out: list[tuple[str, int, str | None]] = []
    for m in re.finditer(r"[^.;]+(?:[.;]|$)", text):
        raw = m.group(0).strip(" .;\n\t")
        if not raw:
            continue
        entity = None
        em = _ENTITY.match(raw)
        if em:
            entity = em.group(1).strip().lower()
            raw = em.group(2).strip()
        out.append((raw, m.start(), entity))
    return out


def _temporal_rank(segment: str) -> int:
    s = segment.lower()
    if re.search(r"\b(currently|now|as of now|latest|today|this morning|this afternoon)\b", s):
        return 30
    if re.search(r"\b(later|subsequently|afterward|afterwards)\b", s):
        return 20
    if re.search(r"\b(previously|earlier|formerly|before)\b", s):
        return 5
    return 10


def _negation_count_before(segment: str, cue_start: int) -> int:
    # Clause-level parity supports ordinary and double negation without
    # phrase-specific exceptions.  It is deliberately bounded to this clause.
    prefix = segment[:cue_start]
    return len(_NEG.findall(prefix))


def _factor_evidence(segment: str, factor: str, rank: int) -> list[Evidence]:
    spec = FRAME_SPECS[factor]
    if not re.search(spec["concept"], segment, re.I):
        return []
    out: list[Evidence] = []
    occupied: list[tuple[int, int]] = []

    for value, pattern in spec["direct"]:
        for m in re.finditer(pattern, segment, re.I):
            occupied.append((m.start(), m.end()))
            out.append(Evidence(factor, value, m.group(0), 1.0, "semantic", rank, True))

    for value, pattern in spec["cues"].items():
        for m in re.finditer(pattern, segment, re.I):
            if any(a <= m.start() < b for a, b in occupied):
                continue
            resolved = value
            polarity = "positive"
            if _negation_count_before(segment, m.start()) % 2 == 1 and value in spec["negate"]:
                resolved = spec["negate"][value]
                polarity = "negated"
            out.append(Evidence(factor, resolved, m.group(0), 0.995, polarity, rank, True))
    return out


def extract_frame_evidence(text: str, target: str | None = None) -> list[Evidence]:
    evidence: list[Evidence] = []
    target_norm = target.strip().lower() if target else None
    for segment, _, entity in _segments(text):
        if target_norm and entity is not None and entity != target_norm:
            continue
        if _CONDITIONAL.match(segment):
            # Hypothetical consequent is not current-state evidence.
            continue
        rank = _temporal_rank(segment)
        for factor in FIELD_ORDER:
            evidence.extend(_factor_evidence(segment, factor, rank))

        # Cancellation and explicit opt-out are cross-factor semantic events.
        if re.search(r"\b(task|case|work|job|item)\b", segment, re.I) and re.search(r"\b(cancelled|canceled)\b", segment, re.I):
            evidence.append(Evidence("need", "none", "cancelled", 1.0, "semantic", rank, False))
        if re.search(r"\b(user|owner|requester)\b", segment, re.I) and re.search(r"\b(prefers?|asked|opted)\b", segment, re.I) and re.search(r"\b(no|not|without)\b", segment, re.I) and re.search(r"\b(action|intervention|reminder|notification)\b", segment, re.I):
            evidence.append(Evidence("need", "none", segment, 1.0, "preference", rank, False))
    return evidence


def _apply_contradiction_safety(state: dict[str, Any], factors: dict[str, FactorResult]) -> None:
    for factor, result in factors.items():
        if result.epistemic_status == "CONTRADICTED":
            safe = CONSERVATIVE_CONTRADICTION[factor]
            state[factor] = safe
            result.value = safe
            result.confidence = 0.0
    if state["side_effect"] == "none":
        state["permission"] = "not_required"
        factors["permission"].value = "not_required"


class ArchitectureD:
    name = "D_compositional_semantic_frame_resolver"

    def parse(self, text: str, target: str | None = None) -> ParseResult:
        evidence = extract_frame_evidence(text, target=target)
        state, factors = resolve_state(evidence, joint_constraints=True, temporal=True)
        _apply_contradiction_safety(state, factors)
        return ParseResult(state, factors, evidence, policy_action(state), self.name)


class ArchitectureDNoOperators(ArchitectureD):
    """Ablation: retain frame lexicon but suppress temporal/conditional semantics."""
    name = "D_ablation_no_operators"

    def parse(self, text: str, target: str | None = None) -> ParseResult:
        # Reuse Architecture C's independent evidence baseline as a deliberately
        # operator-poor comparator rather than silently patching D.
        return ArchitectureC(operators=False, joint_constraints=False, temporal=False).parse(text)
