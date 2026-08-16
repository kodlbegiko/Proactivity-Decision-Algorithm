from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from proactivity.specification.oracle import evaluate, load_spec

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
TOKENIZER_REVISION = MODEL_REVISION
ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
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
ACT_CRITICAL_FIELDS = (
    "permission",
    "information",
    "need",
    "side_effect",
    "risk",
    "reversibility",
    "execution_possible",
)

VALUE_HYPOTHESES: dict[str, dict[Any, tuple[str, ...]]] = {
    "permission": {
        "not_required": (
            "Authorization is not required for the operation.",
            "The operation is outside any permission requirement.",
        ),
        "missing": (
            "Required authorization has not been obtained.",
            "The necessary permission remains missing.",
        ),
        "granted": (
            "Required authorization has been granted.",
            "The necessary permission has already been obtained.",
        ),
    },
    "information": {
        "sufficient": (
            "The available information is sufficient for a decision.",
            "There is enough reliable information to decide.",
        ),
        "insufficient": (
            "Important information required for the decision is missing.",
            "The available evidence is insufficient to decide.",
        ),
        "contradictory": (
            "The available information contains unresolved contradictions.",
            "Decision-relevant evidence conflicts with itself.",
        ),
    },
    "urgency": {
        "none": ("There is no current time pressure.", "The matter is not time-sensitive."),
        "normal": ("The matter has ordinary time sensitivity.", "Timing is relevant but not urgent."),
        "high": ("The matter is time-critical.", "A prompt response is urgently required."),
        "expired": ("The relevant deadline has passed.", "The applicable response window has expired."),
    },
    "need": {
        "none": ("There is no present need for intervention.", "No intervention is currently called for."),
        "optional": ("Intervention is optional rather than necessary.", "Acting would be discretionary."),
        "material": ("A material intervention is presently needed.", "A consequential intervention is required now."),
    },
    "side_effect": {
        "none": ("The intervention creates no material side effect.", "Nothing material changes if the step is taken."),
        "local": ("Any material side effect remains local.", "The step changes only the local user or system state."),
        "external": ("The intervention creates an external side effect.", "The step materially affects an external target."),
    },
    "risk": {
        "low": ("The operational risk is low.", "Exposure to harm is minimal."),
        "medium": ("The operational risk is medium.", "Exposure to harm is moderate."),
        "high": ("The operational risk is high.", "Exposure to harm is substantial."),
    },
    "reversibility": {
        "reversible": ("The action can be reversed after execution.", "The step can later be undone."),
        "irreversible": ("The action cannot be reversed after execution.", "The step cannot later be undone."),
    },
    "deferral_available": {
        False: ("There is no defined opportunity to defer and revisit later.", "No later checkpoint is available."),
        True: ("A defined opportunity exists to defer and revisit later.", "A later checkpoint is available."),
    },
    "execution_possible": {
        False: ("The action cannot currently be executed.", "Execution is presently infeasible."),
        True: ("The action can currently be executed.", "Execution is presently feasible."),
    },
    "clarification_possible": {
        False: ("Clarification cannot currently be requested.", "There is no channel for obtaining clarification now."),
        True: ("Clarification can currently be requested.", "A channel exists for obtaining clarification now."),
    },
    "acknowledged": {
        False: ("The relevant information has not been acknowledged.", "Receipt has not been confirmed."),
        True: ("The relevant information has already been acknowledged.", "Receipt has already been confirmed."),
    },
    "completed": {
        False: ("The underlying task is not complete.", "The underlying work remains unfinished."),
        True: ("The underlying task has already been completed.", "The underlying work is finished."),
    },
}

DESCRIPTIVE_HYPOTHESES: dict[str, dict[Any, tuple[str, ...]]] = {
    field: {
        value: tuple(
            list(texts)
            + [
                f"For Protocol-v2 factor '{field}', the correct structured value is '{str(value).lower()}'.",
            ]
        )
        for value, texts in values.items()
    }
    for field, values in VALUE_HYPOTHESES.items()
}

FIELD_FALLBACKS: dict[str, Any] = {
    "permission": "missing",
    "information": "insufficient",
    "urgency": "normal",
    "need": "optional",
    "side_effect": "external",
    "risk": "medium",
    "reversibility": "irreversible",
    "deferral_available": False,
    "execution_possible": False,
    "clarification_possible": True,
    "acknowledged": False,
    "completed": False,
}


@dataclass(frozen=True)
class V6Config:
    config_id: str
    architecture: str
    segmentation: str
    aggregation: str
    contradiction_mode: str
    confidence_floor: float
    ambiguity_margin: float
    hypothesis_bank: str = "compact"
    solver: str = "none"


@dataclass(frozen=True)
class FactorInference:
    field: str
    value: Any | None
    resolved_value: Any
    confidence: float
    margin: float
    evidence: tuple[str, ...]
    contradiction: bool
    ambiguous: bool
    unknown: bool
    probabilities: dict[str, float]
    raw_scores: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateV6Result:
    action: str | None
    raw_state: dict[str, Any]
    resolved_state: dict[str, Any]
    factors: dict[str, FactorInference]
    oracle_status: str
    oracle_rule: str | None
    prohibited_actions: tuple[str, ...]
    candidate_source: str
    config: V6Config

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["factors"] = {field: inference.to_dict() for field, inference in self.factors.items()}
        return payload


def architecture_configs() -> tuple[V6Config, ...]:
    configs: list[V6Config] = []
    # V6A — factor-specific proposition entailment surrogate using semantic hypotheses.
    aid = 1
    for segmentation in ("sentence_clause", "punctuation_clause"):
        for aggregation in ("max_support", "evidence_pool"):
            for floor in (0.50, 0.60):
                configs.append(
                    V6Config(
                        f"V6A-{aid:02d}",
                        "V6A",
                        segmentation,
                        aggregation,
                        "posterior_margin" if aid % 2 else "strict",
                        floor,
                        0.03,
                        "compact",
                        "none",
                    )
                )
                aid += 1

    # V6B — schema-guided whole-observation parser. Six preregistered configs.
    bid = 1
    for bank, floor, contradiction in (
        ("compact", 0.50, "posterior_margin"),
        ("compact", 0.60, "posterior_margin"),
        ("descriptive", 0.50, "posterior_margin"),
        ("descriptive", 0.60, "posterior_margin"),
        ("descriptive", 0.50, "strict"),
        ("descriptive", 0.60, "strict"),
    ):
        configs.append(
            V6Config(
                f"V6B-{bid:02d}",
                "V6B",
                "whole_observation",
                "schema_global",
                contradiction,
                floor,
                0.03,
                bank,
                "schema_validation",
            )
        )
        bid += 1

    # V6C — neuro-symbolic: proposition representation + factor scorer + consistency solver.
    cid = 1
    for segmentation, aggregation, solver, floor in (
        ("sentence_clause", "max_support", "strict", 0.50),
        ("sentence_clause", "max_support", "strict", 0.60),
        ("sentence_clause", "evidence_pool", "graded", 0.50),
        ("sentence_clause", "evidence_pool", "graded", 0.60),
        ("punctuation_clause", "max_support", "graded", 0.50),
        ("punctuation_clause", "max_support", "graded", 0.60),
        ("whole_observation", "schema_global", "strict", 0.50),
        ("whole_observation", "schema_global", "strict", 0.60),
    ):
        configs.append(
            V6Config(
                f"V6C-{cid:02d}",
                "V6C",
                segmentation,
                aggregation,
                "strict" if solver == "strict" else "posterior_margin",
                floor,
                0.03,
                "descriptive",
                solver,
            )
        )
        cid += 1
    if len(configs) != 22:
        raise AssertionError(len(configs))
    return tuple(configs)


def get_config(config_id: str) -> V6Config:
    for config in architecture_configs():
        if config.config_id == config_id:
            return config
    raise KeyError(config_id)


def _softmax(values: Sequence[float], *, temperature: float = 0.08) -> list[float]:
    if not values:
        return []
    a = np.asarray(values, dtype=np.float64) / temperature
    a -= np.max(a)
    exp = np.exp(a)
    return [float(x) for x in exp / exp.sum()]


def _normalize_label(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+|\n+|\s+[|]\s+|\s*[•]\s*", text.strip())
    return [chunk.strip(" -\t") for chunk in chunks if chunk.strip(" -\t")]


def _split_punctuation(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?;:])\s+|\n+|\s*[|]\s*|\s*[•]\s*", text.strip())
    return [chunk.strip(" -\t") for chunk in chunks if chunk.strip(" -\t")]


def segment(text: str, mode: str) -> list[str]:
    if mode == "whole_observation":
        return [text.strip()]
    if mode == "sentence_clause":
        return _split_sentences(text)
    if mode == "punctuation_clause":
        return _split_punctuation(text)
    raise ValueError(f"unknown segmentation mode: {mode}")


class EmbeddingCache:
    def __init__(self) -> None:
        self._model = None
        self._cache: dict[str, np.ndarray] = {}
        self._model_fingerprint: str | None = None

    @property
    def model_fingerprint(self) -> str | None:
        return self._model_fingerprint

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(MODEL_ID, revision=MODEL_REVISION, device="cpu")
            self._model_fingerprint = hashlib.sha256(f"{MODEL_ID}@{MODEL_REVISION}".encode()).hexdigest()
        return self._model

    def encode(self, texts: Iterable[str]) -> dict[str, np.ndarray]:
        ordered = list(dict.fromkeys(str(text).strip() for text in texts if str(text).strip()))
        missing = [text for text in ordered if text not in self._cache]
        if missing:
            model = self._load()
            vectors = model.encode(
                missing,
                batch_size=128,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            for text, vector in zip(missing, vectors):
                self._cache[text] = np.asarray(vector, dtype=np.float32)
        return {text: self._cache[text] for text in ordered}


class StructuredLatentReasoner:
    def __init__(self, config: V6Config, *, cache: EmbeddingCache | None = None) -> None:
        self.config = config
        self.cache = cache or EmbeddingCache()
        self.spec = load_spec()
        bank = VALUE_HYPOTHESES if config.hypothesis_bank == "compact" else DESCRIPTIVE_HYPOTHESES
        self.hypotheses = bank
        all_hypotheses = [text for values in bank.values() for texts in values.values() for text in texts]
        self.cache.encode(all_hypotheses)

    def _value_score(self, propositions: list[str], hypotheses: tuple[str, ...]) -> tuple[float, tuple[str, ...]]:
        vectors = self.cache.encode(propositions + list(hypotheses))
        p = np.vstack([vectors[item] for item in propositions])
        h = np.vstack([vectors[item] for item in hypotheses])
        similarities = p @ h.T
        if self.config.aggregation in {"max_support", "schema_global"}:
            flat_index = int(np.argmax(similarities))
            pi, _hi = np.unravel_index(flat_index, similarities.shape)
            score = float(similarities.flat[flat_index])
            evidence = (propositions[int(pi)],)
        elif self.config.aggregation == "evidence_pool":
            best_per_prop = similarities.max(axis=1)
            k = min(2, len(best_per_prop))
            indices = np.argsort(best_per_prop)[-k:][::-1]
            score = float(best_per_prop[indices].mean())
            evidence = tuple(propositions[int(i)] for i in indices)
        else:
            raise ValueError(self.config.aggregation)
        return score, evidence

    def _infer_factor(self, field: str, observation: str) -> FactorInference:
        propositions = segment(observation, self.config.segmentation)
        if not propositions:
            propositions = [observation]
        values = list(self.hypotheses[field])
        scores: list[float] = []
        evidences: list[tuple[str, ...]] = []
        for value in values:
            score, evidence = self._value_score(propositions, self.hypotheses[field][value])
            scores.append(score)
            evidences.append(evidence)
        probabilities = _softmax(scores)
        order = list(np.argsort(np.asarray(scores)))[::-1]
        top_i = int(order[0])
        second_i = int(order[1]) if len(order) > 1 else top_i
        top_score = float(scores[top_i])
        second_score = float(scores[second_i])
        # Cosine similarity is mapped into [0, 1] for the preregistered confidence floor.
        confidence = max(0.0, min(1.0, (top_score + 1.0) / 2.0))
        margin = top_score - second_score
        strict_margin = self.config.ambiguity_margin * (1.5 if self.config.contradiction_mode == "strict" else 1.0)
        ambiguous = margin < strict_margin
        contradiction = margin < (strict_margin / 2.0)
        unknown = confidence < self.config.confidence_floor or ambiguous
        selected = None if unknown else values[top_i]
        resolved = selected if selected is not None else FIELD_FALLBACKS[field]
        return FactorInference(
            field=field,
            value=selected,
            resolved_value=resolved,
            confidence=confidence,
            margin=margin,
            evidence=evidences[top_i],
            contradiction=contradiction,
            ambiguous=ambiguous,
            unknown=unknown,
            probabilities={_normalize_label(value): probability for value, probability in zip(values, probabilities)},
            raw_scores={_normalize_label(value): float(score) for value, score in zip(values, scores)},
        )

    def _solve_consistency(self, factors: dict[str, FactorInference]) -> dict[str, FactorInference]:
        if self.config.solver == "none" or self.config.solver == "schema_validation":
            return factors
        resolved = {field: factors[field].resolved_value for field in FIELDS}

        # Protocol-v2 schema constraints are used only to resolve inconsistent uncertain states.
        # Confident semantic predictions are never silently overwritten.
        side = factors["side_effect"]
        perm = factors["permission"]
        if side.resolved_value == "none" and perm.resolved_value != "not_required" and perm.unknown:
            factors["permission"] = _with_resolution(perm, "not_required")
        elif side.resolved_value == "external" and perm.resolved_value == "not_required" and perm.unknown:
            factors["permission"] = _with_resolution(perm, "missing")

        if self.config.solver == "graded":
            # Completed states are explicitly represented but do not force other factor labels;
            # the policy layer handles the intervention consequence.
            return factors

        # Strict solver: if the resolved schema is invalid solely because an uncertain permission
        # fallback conflicts with side-effect scope, repair only that uncertain fallback.
        resolved = {field: factors[field].resolved_value for field in FIELDS}
        validation = __import__("proactivity.specification.schema", fromlist=["validate_state"]).validate_state(self.spec, resolved)
        if not validation.valid and factors["permission"].unknown:
            side_effect = resolved["side_effect"]
            replacement = "not_required" if side_effect == "none" else "missing"
            factors["permission"] = _with_resolution(factors["permission"], replacement)
        return factors

    def predict(self, observation: str) -> CandidateV6Result:
        factors = {field: self._infer_factor(field, observation) for field in FIELDS}
        factors = self._solve_consistency(factors)
        raw_state = {field: factors[field].value if factors[field].value is not None else "UNKNOWN" for field in FIELDS}
        resolved_state = {field: factors[field].resolved_value for field in FIELDS}

        # ACT safety gate is implemented as structured-state fail-closed semantics, not a direct
        # action override. Any unresolved critical factor remains conservatively resolved so the
        # public Protocol-v2 oracle cannot select ACT.
        unresolved_critical = [
            field
            for field in ACT_CRITICAL_FIELDS
            if factors[field].unknown or factors[field].contradiction or factors[field].confidence < self.config.confidence_floor
        ]
        if unresolved_critical:
            for field in unresolved_critical:
                resolved_state[field] = FIELD_FALLBACKS[field]
            # Preserve schema validity of permission relative to side-effect scope.
            if resolved_state["side_effect"] == "none":
                resolved_state["permission"] = "not_required"
            elif resolved_state["permission"] == "not_required":
                resolved_state["permission"] = "missing"

        oracle = evaluate(resolved_state, spec=self.spec)
        return CandidateV6Result(
            action=oracle.action,
            raw_state=raw_state,
            resolved_state=resolved_state,
            factors=factors,
            oracle_status=oracle.status,
            oracle_rule=oracle.matched_rule,
            prohibited_actions=oracle.prohibited_actions,
            candidate_source=f"{MODEL_ID}@{MODEL_REVISION}",
            config=self.config,
        )

    def predict_many(self, observations: Sequence[str]) -> list[CandidateV6Result]:
        # Warm the cache in one deterministic batch to avoid repeated model calls.
        texts: list[str] = []
        for observation in observations:
            texts.extend(segment(observation, self.config.segmentation))
        self.cache.encode(texts)
        return [self.predict(observation) for observation in observations]


def _with_resolution(inference: FactorInference, value: Any) -> FactorInference:
    return FactorInference(
        field=inference.field,
        value=inference.value,
        resolved_value=value,
        confidence=inference.confidence,
        margin=inference.margin,
        evidence=inference.evidence,
        contradiction=inference.contradiction,
        ambiguous=inference.ambiguous,
        unknown=inference.unknown,
        probabilities=inference.probabilities,
        raw_scores=inference.raw_scores,
    )


def config_sha256(config: V6Config) -> str:
    return hashlib.sha256(json.dumps(asdict(config), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
