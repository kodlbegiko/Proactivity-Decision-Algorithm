from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from proactivity.specification.oracle import evaluate, load_spec
from proactivity.specification.schema import validate_state

FIELD_ORDER = (
    "permission", "information", "urgency", "need", "side_effect", "risk",
    "reversibility", "deferral_available", "execution_possible",
    "clarification_possible", "acknowledged", "completed",
)
ACT_CRITICAL_FIELDS = {
    "permission", "information", "risk", "reversibility",
    "execution_possible", "side_effect", "need",
}


@dataclass(frozen=True)
class Proposition:
    text: str
    predicate: str
    field: str | None
    value: Any | None
    polarity: str
    modality: str
    certainty: float
    temporality: str
    scope: str


@dataclass(frozen=True)
class Evidence:
    field: str
    value: Any
    confidence: float
    proposition_index: int
    polarity: str
    temporality: str


@dataclass(frozen=True)
class CandidateConfig:
    id: str
    family: str
    token_threshold: float
    conflict_margin: float
    confidence_floor: float


CONFIGS: tuple[CandidateConfig, ...] = (
    CandidateConfig("V7A-01", "V7A", 0.44, 0.08, 0.52),
    CandidateConfig("V7A-02", "V7A", 0.48, 0.10, 0.56),
    CandidateConfig("V7A-03", "V7A", 0.52, 0.12, 0.60),
    CandidateConfig("V7A-04", "V7A", 0.56, 0.14, 0.64),
    CandidateConfig("V7B-01", "V7B", 0.38, 0.08, 0.48),
    CandidateConfig("V7B-02", "V7B", 0.42, 0.10, 0.52),
    CandidateConfig("V7B-03", "V7B", 0.46, 0.12, 0.56),
    CandidateConfig("V7B-04", "V7B", 0.50, 0.14, 0.60),
    CandidateConfig("V7C-01", "V7C", 0.40, 0.08, 0.50),
    CandidateConfig("V7C-02", "V7C", 0.44, 0.10, 0.54),
    CandidateConfig("V7C-03", "V7C", 0.48, 0.12, 0.58),
    CandidateConfig("V7C-04", "V7C", 0.52, 0.14, 0.62),
)
CONFIG_BY_ID = {config.id: config for config in CONFIGS}

# Parser ontology. It is deliberately independent from candidate_v7_data.LEXICAL.
# Patterns describe factor semantics rather than split-specific example text.
PATTERNS: dict[str, tuple[tuple[Any, tuple[str, ...]], ...]] = {
    "permission": (
        ("not_required", (
            r"permission\s+is\s+not\s+required", r"no\s+approval\s+is\s+required",
            r"authorization\s+is\s+unnecessary", r"does\s+not\s+require\s+consent",
            r"no\s+sign[- ]off\s+is\s+needed", r"outside\s+approval\s+scope",
        )),
        ("missing", (
            r"permission\s+is\s+missing", r"approval\s+is\s+(?:still\s+)?pending",
            r"remains\s+unauthori[sz]ed", r"consent\s+is\s+absent",
            r"approval\s+has\s+not\s+been\s+granted", r"nobody\s+has\s+signed\s+off",
            r"sign[- ]off.*(?:not|yet)", r"clearance\s+has\s+yet\s+to\s+arrive",
            r"clearance.*(?:missing|pending)",
        )),
        ("granted", (
            r"permission\s+is\s+granted", r"approval\s+is\s+granted",
            r"authorization\s+is\s+confirmed", r"consent\s+is\s+on\s+record",
            r"operation\s+has\s+clearance", r"sign[- ]off\s+is\s+in\s+place",
            r"clearance\s+is\s+in\s+place", r"(?:properly\s+)?authori[sz]ed",
        )),
    ),
    "information": (
        ("contradictory", (
            r"information\s+is\s+contradictory", r"facts\s+conflict",
            r"evidence\s+is\s+inconsistent", r"reports\s+disagree",
            r"incompatible\s+directions", r"unresolved\s+contradictions",
        )),
        ("insufficient", (
            r"information\s+is\s+(?:not\s+)?sufficient", r"facts\s+are\s+incomplete",
            r"more\s+information\s+is\s+needed", r"evidence\s+is\s+inadequate",
            r"details\s+are\s+still\s+missing", r"do\s+not\s+support\s+a\s+complete\s+decision",
        )),
        ("sufficient", (
            r"information\s+is\s+sufficient", r"facts\s+are\s+complete",
            r"enough\s+information", r"evidence\s+is\s+adequate",
            r"details\s+are\s+enough", r"nothing\s+material\s+is\s+missing.*information",
        )),
    ),
    "urgency": (
        ("expired", (
            r"deadline\s+has\s+(?:already\s+)?expired", r"timing\s+window\s+is\s+expired",
            r"deadline\s+has\s+already\s+passed", r"allowed\s+window\s+is\s+over",
            r"due\s+time\s+is\s+already\s+behind", r"time\s+window\s+has\s+lapsed",
        )),
        ("none", (
            r"no\s+urgency", r"not\s+urgent", r"no\s+immediate\s+timing\s+pressure",
            r"matter\s+can\s+wait", r"no\s+time\s+pressure", r"nothing\s+is\s+pressing",
        )),
        ("high", (
            r"urgency\s+is\s+high", r"matter\s+is\s+urgent", r"immediate\s+attention\s+is\s+needed",
            r"time\s+pressure\s+is\s+severe", r"deadline\s+pressure\s+is\s+acute", r"needs\s+prompt\s+attention",
        )),
        ("normal", (
            r"urgency\s+is\s+normal", r"timing\s+is\s+routine", r"ordinary\s+priority",
            r"schedule\s+is\s+standard", r"normal\s+timetable", r"timing\s+pressure\s+is\s+moderate",
        )),
    ),
    "need": (
        ("none", (
            r"no\s+intervention\s+is\s+needed", r"no\s+current\s+need", r"intervention\s+is\s+unnecessary",
            r"nothing\s+needs\s+to\s+be\s+done", r"no\s+actionable\s+need", r"no\s+response\s+is\s+called\s+for",
        )),
        ("optional", (
            r"intervention\s+is\s+optional", r"need\s+is\s+optional", r"could\s+help\s+but\s+is\s+not\s+necessary",
            r"action\s+is\s+discretionary", r"may\s+be\s+useful\s+but\s+can\s+be\s+skipped", r"intervention\s+would\s+be\s+elective",
        )),
        ("material", (
            r"material\s+intervention\s+is\s+needed", r"need\s+is\s+material", r"substantive\s+response\s+is\s+required",
            r"requires\s+intervention", r"concrete\s+need\s+for\s+action", r"meaningful\s+response\s+is\s+called\s+for",
        )),
    ),
    "side_effect": (
        ("none", (
            r"no\s+side\s+effect", r"action\s+has\s+no\s+side\s+effect", r"no\s+state[- ]changing\s+effect",
            r"informational\s+only", r"nothing\s+outside\s+the\s+message\s+would\s+be\s+changed", r"zero\s+material\s+effect",
        )),
        ("local", (
            r"side\s+effect\s+is\s+local", r"changes\s+local\s+state", r"only\s+local\s+state\s+would\s+change",
            r"effect\s+stays\s+within\s+the\s+local\s+system", r"change\s+is\s+confined\s+to\s+this\s+system", r"affects\s+only\s+local\s+data",
        )),
        ("external", (
            r"side\s+effect\s+is\s+external", r"changes\s+an\s+external\s+system", r"effect\s+reaches\s+an\s+outside\s+system",
            r"external\s+consequences", r"alter\s+something\s+beyond\s+this\s+system", r"external\s+service",
        )),
    ),
    "risk": (
        ("low", (
            r"risk\s+is\s+low", r"has\s+low\s+risk", r"risk\s+level\s+is\s+minimal", r"low[- ]risk",
            r"downside\s+exposure\s+is\s+small", r"material\s+harm\s+is\s+unlikely", r"risk\s+is\s+not\s+medium\s+or\s+high",
        )),
        ("medium", (
            r"risk\s+is\s+medium", r"moderate\s+risk", r"risk\s+level\s+is\s+intermediate",
            r"meaningful\s+but\s+not\s+severe", r"neither\s+low\s+nor\s+extreme", r"moderate\s+chance\s+of\s+harm",
        )),
        ("high", (
            r"risk\s+is\s+high", r"has\s+high\s+risk", r"risk\s+level\s+is\s+severe",
            r"downside\s+is\s+substantial", r"exposure\s+to\s+harm\s+is\s+considerable", r"harm\s+is\s+a\s+serious\s+possibility",
        )),
    ),
    "reversibility": (
        ("irreversible", (
            r"action\s+is\s+irreversible", r"change\s+cannot\s+be\s+undone", r"cannot\s+be\s+rolled\s+back",
            r"reversal\s+is\s+impossible", r"no\s+way\s+to\s+restore\s+the\s+prior\s+state", r"effect\s+is\s+permanent",
            r"change\s+is\s+not\s+reversible",
        )),
        ("reversible", (
            r"action\s+is\s+reversible", r"change\s+can\s+be\s+undone", r"can\s+be\s+rolled\s+back",
            r"reversal\s+remains\s+possible", r"restore\s+the\s+prior\s+state", r"effect\s+is\s+recoverable",
        )),
    ),
    "deferral_available": (
        (False, (
            r"deferral\s+is\s+(?:not\s+available|unavailable)", r"cannot\s+be\s+deferred", r"waiting\s+is\s+not\s+an\s+option",
            r"no\s+later\s+trigger", r"postponement\s+is\s+not\s+available", r"no\s+valid\s+future\s+opportunity",
        )),
        (True, (
            r"deferral\s+is\s+available", r"can\s+be\s+deferred", r"waiting\s+remains\s+an\s+option",
            r"later\s+trigger\s+is\s+available", r"can\s+safely\s+be\s+postponed", r"valid\s+future\s+opportunity",
        )),
    ),
    "execution_possible": (
        (False, (
            r"execution\s+is\s+not\s+possible", r"action\s+cannot\s+be\s+executed", r"unable\s+to\s+perform\s+the\s+operation",
            r"execution\s+is\s+currently\s+infeasible", r"operation\s+cannot\s+be\s+carried\s+out", r"no\s+execution\s+path\s+is\s+available",
        )),
        (True, (
            r"execution\s+is\s+possible", r"action\s+can\s+be\s+executed", r"can\s+perform\s+the\s+operation",
            r"execution\s+is\s+currently\s+feasible", r"operation\s+can\s+be\s+carried\s+out", r"execution\s+path\s+is\s+available",
        )),
    ),
    "clarification_possible": (
        (False, (
            r"clarification\s+is\s+not\s+possible", r"cannot\s+ask\s+for\s+clarification", r"cannot\s+be\s+clarified",
            r"no\s+question\s+can\s+resolve", r"cannot\s+be\s+resolved\s+by\s+asking", r"clarification\s+is\s+unavailable",
        )),
        (True, (
            r"clarification\s+is\s+possible", r"can\s+ask\s+for\s+clarification", r"can\s+be\s+clarified",
            r"question\s+can\s+resolve", r"can\s+be\s+resolved\s+by\s+asking", r"clarification\s+is\s+obtainable",
        )),
    ),
    "acknowledged": (
        (False, (
            r"matter\s+is\s+not\s+acknowledged", r"has\s+not\s+been\s+acknowledged", r"has\s+not\s+acknowledged",
            r"no\s+acknowledgement\s+is\s+on\s+record", r"has\s+not\s+yet\s+been\s+recognized", r"remains\s+unacknowledged",
        )),
        (True, (
            r"matter\s+is\s+acknowledged", r"has\s+been\s+acknowledged", r"already\s+acknowledged",
            r"acknowledgement\s+is\s+on\s+record", r"already\s+been\s+seen\s+and\s+recognized", r"receipt\s+has\s+been\s+acknowledged",
        )),
    ),
    "completed": (
        (False, (
            r"task\s+is\s+not\s+completed", r"work\s+is\s+incomplete", r"has\s+not\s+finished",
            r"task\s+remains\s+open", r"work\s+is\s+still\s+unfinished", r"completion\s+has\s+not\s+yet\s+occurred",
            r"task\s+has\s+not\s+been\s+completed",
        )),
        (True, (
            r"task\s+is\s+completed", r"work\s+is\s+complete", r"has\s+finished",
            r"task\s+is\s+already\s+done", r"work\s+has\s+been\s+fully\s+completed", r"nothing\s+left\s+to\s+complete",
        )),
    ),
}

PROTOTYPES: dict[str, dict[Any, tuple[str, ...]]] = {
    "permission": {
        "granted": ("permission approval authorization consent clearance granted confirmed authorized signoff",),
        "missing": ("permission approval authorization consent clearance missing pending absent unauthorized unsigned",),
        "not_required": ("permission approval authorization consent unnecessary exempt no requirement",),
    },
    "information": {
        "sufficient": ("information facts evidence details sufficient complete enough adequate",),
        "insufficient": ("information facts evidence details insufficient incomplete missing inadequate",),
        "contradictory": ("information facts evidence reports contradictory conflict inconsistent disagree",),
    },
    "urgency": {
        "none": ("urgency timing no pressure wait not urgent",),
        "normal": ("urgency timing routine normal ordinary standard",),
        "high": ("urgency timing urgent high immediate severe acute prompt",),
        "expired": ("deadline timing expired passed over lapsed",),
    },
    "need": {
        "none": ("need intervention response none unnecessary nothing",),
        "optional": ("need intervention response optional discretionary elective",),
        "material": ("need intervention response material substantive required concrete meaningful",),
    },
    "side_effect": {
        "none": ("side effect none informational zero material change",),
        "local": ("side effect local state system data internal",),
        "external": ("side effect external outside service consequences",),
    },
    "risk": {
        "low": ("risk low minimal small unlikely safe",),
        "medium": ("risk medium moderate intermediate meaningful",),
        "high": ("risk high severe substantial considerable serious harm",),
    },
    "reversibility": {
        "reversible": ("reversible undo rollback reversal restore recoverable",),
        "irreversible": ("irreversible cannot undo rollback impossible permanent",),
    },
    "deferral_available": {True: ("deferral defer waiting later postpone future available",), False: ("deferral defer waiting later postpone future unavailable cannot no",)},
    "execution_possible": {True: ("execution execute perform feasible carry out path available",), False: ("execution execute perform infeasible unable cannot no path",)},
    "clarification_possible": {True: ("clarification ask clarify question resolve obtainable possible",), False: ("clarification ask clarify question resolve unavailable impossible cannot",)},
    "acknowledged": {True: ("acknowledged acknowledgement recognized receipt seen",), False: ("unacknowledged no acknowledgement not recognized unseen",)},
    "completed": {True: ("completed complete finished done nothing left",), False: ("not completed incomplete unfinished open remains",)},
}

SAFE_DEFAULTS: dict[str, Any] = {
    "permission": "missing",
    "information": "insufficient",
    "urgency": "normal",
    "need": "optional",
    "side_effect": "local",
    "risk": "high",
    "reversibility": "irreversible",
    "deferral_available": False,
    "execution_possible": False,
    "clarification_possible": True,
    "acknowledged": False,
    "completed": False,
}


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


def segment_propositions(text: str, *, enabled: bool = True, scope_enabled: bool = True) -> list[str]:
    normalized_lines: list[str] = []
    for line in text.replace("\r", "\n").split("\n"):
        line = re.sub(r"^\s*[-*•]\s*", "", line.strip())
        if line:
            normalized_lines.append(line)
    normalized = ". ".join(normalized_lines)
    if not enabled:
        return [normalized]
    chunks = [chunk.strip(" .") for chunk in re.split(r"[.;]+\s*", normalized) if chunk.strip(" .")]
    output: list[str] = []
    for chunk in chunks:
        chunk = re.sub(r"^status\s+update\s*:\s*", "", chunk, flags=re.I)
        chunk = re.sub(r"^also\s*,?\s*", "", chunk, flags=re.I)
        chunk = re.sub(r"^for\s+context\s*\((.*)\)$", r"\1", chunk, flags=re.I)
        if scope_enabled:
            pieces = [p.strip(" ,") for p in re.split(r"\s+(?:but|whereas|while)\s+", chunk, flags=re.I) if p.strip(" ,")]
            output.extend(pieces)
        else:
            output.append(chunk)
    return output


def _temporal_scope(clause: str) -> tuple[str, str]:
    lower = clause.lower().strip()
    if re.match(r"^(previously|formerly|earlier|in the past)\b", lower):
        return "past", re.sub(r"^(previously|formerly|earlier|in the past)\s*,?\s*", "", clause, flags=re.I)
    if re.match(r"^(as of now|currently|now|at present)\b", lower):
        return "current", re.sub(r"^(as of now|currently|now|at present)\s*,?\s*", "", clause, flags=re.I)
    if re.search(r"\b(?:will|later|in the future)\b", lower):
        return "future", clause
    return "current", clause


def _polarity(text: str) -> str:
    lower = text.lower()
    if re.search(r"\b(?:not|no|never|neither|without|unable|cannot|unavailable|unauthorized|incomplete|irreversible|unacknowledged)\b", lower) or "n't" in lower:
        return "negative"
    return "positive"


def _modality(text: str) -> str:
    lower = text.lower()
    if re.search(r"\b(?:must|required|need(?:ed)?)\b", lower):
        return "required"
    if re.search(r"\b(?:cannot|prohibited|forbidden|must not)\b", lower):
        return "prohibited"
    if re.search(r"\b(?:may|might|could|possible)\b", lower):
        return "possible"
    if re.search(r"\b(?:if|unless)\b", lower):
        return "conditional"
    return "asserted"


def _regex_match(clause: str, *, negation_enabled: bool) -> list[tuple[str, Any, float]]:
    lower = clause.lower()
    neg = _polarity(lower) == "negative"
    matches: list[tuple[str, Any, float]] = []
    for field, values in PATTERNS.items():
        for value, patterns in values:
            for pattern in patterns:
                if re.search(pattern, lower):
                    if not negation_enabled and neg:
                        continue
                    specificity = min(0.995, 0.88 + 0.005 * len(_tokens(pattern)))
                    matches.append((field, value, specificity))
                    break
    return matches


def _prototype_match(clause: str, threshold: float, *, negation_enabled: bool) -> list[tuple[str, Any, float]]:
    words = _tokens(clause)
    if not words:
        return []
    neg = _polarity(clause) == "negative"
    if neg and not negation_enabled:
        return []
    scores: list[tuple[str, Any, float]] = []
    for field, by_value in PROTOTYPES.items():
        best_for_field: tuple[Any, float] | None = None
        for value, prototypes in by_value.items():
            score = 0.0
            for prototype in prototypes:
                p = _tokens(prototype)
                if not p:
                    continue
                overlap = len(words & p)
                candidate = overlap / math.sqrt(max(1, len(p)) * max(1, len(words)))
                score = max(score, candidate)
            if best_for_field is None or score > best_for_field[1]:
                best_for_field = (value, score)
        if best_for_field and best_for_field[1] >= threshold:
            scores.append((field, best_for_field[0], min(0.86, 0.45 + best_for_field[1] * 0.50)))
    return scores


def parse_text(
    text: str,
    config: CandidateConfig,
    *,
    segmentation_enabled: bool = True,
    negation_enabled: bool = True,
    scope_enabled: bool = True,
    temporal_enabled: bool = True,
) -> list[Proposition]:
    clauses = segment_propositions(text, enabled=segmentation_enabled, scope_enabled=scope_enabled)
    propositions: list[Proposition] = []
    for clause in clauses:
        temporality, semantic_clause = _temporal_scope(clause) if temporal_enabled else ("current", clause)
        candidates: list[tuple[str, Any, float]] = []
        if config.family in {"V7A", "V7C"}:
            candidates.extend(_regex_match(semantic_clause, negation_enabled=negation_enabled))
        if (not candidates and config.family == "V7C") or config.family == "V7B":
            candidates.extend(_prototype_match(semantic_clause, config.token_threshold, negation_enabled=negation_enabled))
        if not candidates:
            propositions.append(Proposition(
                text=clause, predicate="unknown", field=None, value=None,
                polarity=_polarity(semantic_clause), modality=_modality(semantic_clause),
                certainty=0.40, temporality=temporality, scope="clause",
            ))
            continue
        # A clause should normally encode one factor. Retain multiple matches if they are genuinely distinct fields.
        best_by_field: dict[str, tuple[Any, float]] = {}
        for field, value, confidence in candidates:
            current = best_by_field.get(field)
            if current is None or confidence > current[1]:
                best_by_field[field] = (value, confidence)
        for field, (value, confidence) in best_by_field.items():
            propositions.append(Proposition(
                text=clause, predicate=field, field=field, value=value,
                polarity=_polarity(semantic_clause), modality=_modality(semantic_clause),
                certainty=confidence, temporality=temporality, scope="clause",
            ))
    return propositions


def build_evidence_graph(propositions: Iterable[Proposition]) -> dict[str, list[Evidence]]:
    graph: dict[str, list[Evidence]] = {field: [] for field in FIELD_ORDER}
    for index, proposition in enumerate(propositions):
        if proposition.field is None or proposition.value is None:
            continue
        if proposition.temporality != "current":
            continue
        graph[proposition.field].append(Evidence(
            field=proposition.field, value=proposition.value,
            confidence=proposition.certainty, proposition_index=index,
            polarity=proposition.polarity, temporality=proposition.temporality,
        ))
    return graph


def _solve_field(field: str, evidence: list[Evidence], config: CandidateConfig, *, uncertainty_enabled: bool) -> tuple[Any, bool, bool]:
    if not evidence:
        return SAFE_DEFAULTS[field], True, False
    by_value: dict[Any, float] = defaultdict(float)
    for item in evidence:
        by_value[item.value] += item.confidence
    ranked = sorted(by_value.items(), key=lambda item: (-item[1], str(item[0])))
    best_value, best_score = ranked[0]
    contradiction = len(ranked) > 1 and ranked[1][1] >= best_score - config.conflict_margin
    uncertain = best_score < config.confidence_floor or contradiction
    if uncertain and uncertainty_enabled:
        return SAFE_DEFAULTS[field], True, contradiction
    return best_value, False, contradiction


def _repair_schema_consistency(state: dict[str, Any], unknown_fields: set[str]) -> dict[str, Any]:
    # This is schema repair only; it never inspects or optimizes the target action.
    repaired = dict(state)
    if repaired["side_effect"] == "none":
        repaired["permission"] = "not_required"
        if "permission" in unknown_fields:
            unknown_fields.add("permission")
    elif repaired["side_effect"] == "external" and repaired["permission"] == "not_required":
        repaired["permission"] = "missing"
        unknown_fields.add("permission")
    return repaired


def reconstruct_state(
    propositions: Iterable[Proposition],
    config: CandidateConfig,
    *, solver_enabled: bool = True,
    uncertainty_enabled: bool = True,
) -> tuple[dict[str, Any], set[str], set[str], dict[str, list[Evidence]]]:
    graph = build_evidence_graph(propositions)
    state: dict[str, Any] = {}
    unknown_fields: set[str] = set()
    contradictions: set[str] = set()
    for field in FIELD_ORDER:
        value, unknown, contradiction = _solve_field(field, graph[field], config, uncertainty_enabled=uncertainty_enabled)
        state[field] = value
        if unknown:
            unknown_fields.add(field)
        if contradiction:
            contradictions.add(field)
    if solver_enabled:
        state = _repair_schema_consistency(state, unknown_fields)
    return state, unknown_fields, contradictions, graph


def predict(
    text: str,
    config_id: str,
    *,
    segmentation_enabled: bool = True,
    negation_enabled: bool = True,
    scope_enabled: bool = True,
    temporal_enabled: bool = True,
    solver_enabled: bool = True,
    uncertainty_enabled: bool = True,
) -> dict[str, Any]:
    config = CONFIG_BY_ID[config_id]
    propositions = parse_text(
        text, config,
        segmentation_enabled=segmentation_enabled,
        negation_enabled=negation_enabled,
        scope_enabled=scope_enabled,
        temporal_enabled=temporal_enabled,
    )
    state, unknown_fields, contradictions, graph = reconstruct_state(
        propositions, config,
        solver_enabled=solver_enabled,
        uncertainty_enabled=uncertainty_enabled,
    )
    spec = load_spec()
    validation = validate_state(spec, state)
    if validation.valid:
        oracle = evaluate(state, spec=spec)
        action = oracle.action if oracle.status == "VALID_DECISION" else None
        status = oracle.status
        forbidden_act = bool(action == "ACT" and "ACT" in oracle.prohibited_actions)
    else:
        action = None
        status = "INVALID_STATE"
        forbidden_act = False
    return {
        "state": state,
        "action": action,
        "status": status,
        "unknown_fields": sorted(unknown_fields),
        "contradictions": sorted(contradictions),
        "critical_unknown_fields": sorted(ACT_CRITICAL_FIELDS & unknown_fields),
        "forbidden_act": forbidden_act,
        "propositions": [asdict(item) for item in propositions],
        "evidence_counts": {field: len(items) for field, items in graph.items()},
    }


def get_config(config_id: str) -> CandidateConfig:
    return CONFIG_BY_ID[config_id]


def config_manifest() -> list[dict[str, Any]]:
    return [asdict(config) for config in CONFIGS]
