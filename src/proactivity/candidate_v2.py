"""Protocol v2 Gate-E raw-context PDA candidate families.

All candidate families consume only candidate-visible ``domain`` and
``observation`` fields supplied by the evaluator.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
SEED = 20260814


def _contains(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def extract_visible_semantic_factors(observation: str) -> dict[str, str]:
    """Normalize visible semantic statements without hidden transport fields."""
    text = observation.lower()

    if _contains(text, ("required but absent", "required authorization has not been granted", "still lacks required authorization", "needed authorization is still unavailable")):
        permission = "required_absent"
    elif _contains(text, ("required and present", "required authorization has been granted", "has required authorization", "needed authorization is already available")):
        permission = "required_present"
    elif _contains(text, ("no authorization is required", "authorization is outside the required scope", "authorization is not part of the modeled requirement", "does not need authorization")):
        permission = "not_required"
    else:
        permission = "unknown"

    if _contains(text, ("contains a contradiction", "available information conflicts", "includes conflicting facts", "internally inconsistent")):
        information = "contradictory"
    elif _contains(text, ("important information is missing", "lacks necessary facts", "some evidence needed for this modeled choice is unavailable", "evidence needed for this modeled choice is missing")):
        information = "missing"
    elif _contains(text, ("available information is sufficient", "context is sufficiently specified", "evidence needed for this modeled choice is available", "evidence is complete enough")):
        information = "sufficient"
    else:
        information = "unknown"

    if _contains(text, ("deadline state is expired", "relevant time window has already expired", "past its relevant window", "timing window has passed")):
        timing = "expired"
    elif _contains(text, ("highly time-sensitive", "strong time pressure", "timing pressure is high", "timing is urgent")):
        timing = "high"
    elif _contains(text, ("normal time sensitivity", "ordinary time pressure", "timing pressure is ordinary", "timing is currently relevant")):
        timing = "ordinary"
    elif _contains(text, ("not time-sensitive now", "no present time pressure", "no immediate timing pressure", "timing pressure is absent")):
        timing = "absent"
    else:
        timing = "unknown"

    if _contains(text, ("material intervention need", "material need for intervention", "substantive intervention requirement", "current intervention need is material")):
        need = "material"
    elif _contains(text, ("intervention would be discretionary", "potential intervention is optional", "current intervention need is optional", "only a discretionary intervention opportunity")):
        need = "optional"
    elif _contains(text, ("no current intervention requirement", "no material intervention need", "nothing material currently calls for intervention")):
        need = "none"
    else:
        need = "unknown"

    if _contains(text, ("modeled side effect is external", "external side effect", "effect beyond the local system", "affect an external system or party")):
        side_effect = "external"
    elif _contains(text, ("modeled side effect is local", "only a local side effect", "effect confined locally", "side effect would remain local")):
        side_effect = "local"
    elif _contains(text, ("there is no modeled side effect", "would not create a material side effect", "no material side effect", "no side effect")):
        side_effect = "none"
    else:
        side_effect = "unknown"

    if _contains(text, ("risk is high", "risk level is high", "consequence has high risk", "modeled risk is high")):
        risk = "high"
    elif _contains(text, ("risk is medium", "risk is moderate", "risk level is medium", "risk level is moderate", "consequence has medium risk", "consequence has moderate risk", "modeled risk is medium", "modeled risk is moderate")):
        risk = "medium"
    elif _contains(text, ("risk is low", "risk level is low", "consequence has low risk", "modeled risk is low")):
        risk = "low"
    else:
        risk = "unknown"

    if _contains(text, ("not reversible", "cannot be rolled back", "cannot be undone", "cannot be reversed")):
        reversible = "no"
    elif _contains(text, ("is reversible", "can be rolled back", "can be undone", "can be reversed")):
        reversible = "yes"
    else:
        reversible = "unknown"

    if _contains(text, ("defined deferred trigger is available", "specified later trigger", "later trigger has been defined", "future trigger is defined")):
        deferral = "yes"
    elif _contains(text, ("no specified later trigger", "no later trigger has been defined", "no defined deferred trigger", "no future trigger is defined")):
        deferral = "no"
    else:
        deferral = "unknown"

    if _contains(text, ("execution is not currently possible", "cannot presently be executed", "cannot currently carry out", "relevant capability is unavailable")):
        execution = "no"
    elif _contains(text, ("execution is currently possible", "can presently be executed", "can currently carry out", "relevant capability is available")):
        execution = "yes"
    else:
        execution = "unknown"

    if _contains(text, ("clarification cannot currently be obtained", "cannot presently be clarified", "cannot currently be clarified", "clarification channel is unavailable")):
        clarification = "no"
    elif _contains(text, ("clarification can currently be obtained", "can presently be clarified", "can currently be clarified", "clarification channel is available")):
        clarification = "yes"
    else:
        clarification = "unknown"

    if _contains(text, ("has not acknowledged", "no acknowledgement has been recorded", "has not been acknowledged", "acknowledgement is absent")):
        acknowledged = "no"
    elif _contains(text, ("user has acknowledged", "an acknowledgement has been recorded", "has been acknowledged", "acknowledgement is present")):
        acknowledged = "yes"
    else:
        acknowledged = "unknown"

    if _contains(text, ("underlying task is not completed", "modeled task remains incomplete", "objective remains unresolved", "completion has not occurred")):
        completed = "no"
    elif _contains(text, ("underlying task is already completed", "underlying task is completed", "modeled task has been completed", "objective has been resolved", "objective is resolved", "completion has occurred")):
        completed = "yes"
    else:
        completed = "unknown"

    return {"permission": permission, "information": information, "timing": timing, "need": need, "side_effect": side_effect, "risk": risk, "reversible": reversible, "deferral": deferral, "execution": execution, "clarification": clarification, "acknowledged": acknowledged, "completed": completed}


class _ObservationSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return [row["observation"] for row in X]


class _DomainSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return np.asarray([[row["domain"]] for row in X], dtype=object)


class _SemanticSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return [extract_visible_semantic_factors(row["observation"]) for row in X]


def _raw_features() -> FeatureUnion:
    return FeatureUnion([
        ("word", Pipeline([("select", _ObservationSelector()), ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, sublinear_tf=True))])),
        ("char", Pipeline([("select", _ObservationSelector()), ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), lowercase=True, sublinear_tf=True))])),
        ("domain", Pipeline([("select", _DomainSelector()), ("onehot", OneHotEncoder(handle_unknown="ignore"))])),
    ])


def _semantic_features() -> Pipeline:
    return Pipeline([("select", _SemanticSelector()), ("vectorize", DictVectorizer(sparse=True))])


class _PipelineCandidate:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        self.pipeline.fit(list(records), list(labels)); return self
    def predict(self, records: Sequence[dict]) -> list[str]:
        values = self.pipeline.predict(list(records)); return [str(value) for value in values.tolist()]


class BalancedClassicalLinear(_PipelineCandidate):
    def __init__(self, c: float):
        super().__init__(Pipeline([("features", _raw_features()), ("classifier", LogisticRegression(C=c, class_weight="balanced", max_iter=3000, random_state=SEED, solver="lbfgs"))]))


class BalancedLinearMargin(_PipelineCandidate):
    def __init__(self):
        super().__init__(Pipeline([("features", _raw_features()), ("classifier", LinearSVC(C=1.0, class_weight="balanced", random_state=SEED))]))


class SemanticFactorTree(_PipelineCandidate):
    def __init__(self):
        super().__init__(Pipeline([("features", _semantic_features()), ("classifier", DecisionTreeClassifier(max_depth=8, class_weight="balanced", random_state=SEED))]))


class SemanticFactorLinear(_PipelineCandidate):
    def __init__(self):
        super().__init__(Pipeline([("features", _semantic_features()), ("classifier", LogisticRegression(C=1.0, class_weight="balanced", max_iter=3000, random_state=SEED, solver="lbfgs"))]))


class HybridSemanticSafetyCandidate:
    def __init__(self):
        self.pipeline = Pipeline([
            ("features", FeatureUnion([("raw", _raw_features()), ("semantic", _semantic_features())])),
            ("classifier", LogisticRegression(C=1.0, class_weight="balanced", max_iter=3000, random_state=SEED, solver="lbfgs")),
        ])
    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        self.pipeline.fit(list(records), list(labels)); return self
    @staticmethod
    def _act_veto(record: dict) -> bool:
        factors = extract_visible_semantic_factors(record["observation"])
        return factors["permission"] == "required_absent" or factors["information"] in {"missing", "contradictory"} or factors["risk"] == "high" or factors["reversible"] == "no" or factors["execution"] == "no" or factors["completed"] == "yes"
    def predict(self, records: Sequence[dict]) -> list[str]:
        rows = list(records)
        probabilities = self.pipeline.predict_proba(rows)
        classes = [str(value) for value in self.pipeline.named_steps["classifier"].classes_.tolist()]
        output = []
        for row, scores in zip(rows, probabilities):
            order = np.argsort(-scores, kind="stable")
            best = classes[int(order[0])]
            if best == "ACT" and self._act_veto(row):
                best = next(classes[int(index)] for index in order if classes[int(index)] != "ACT")
            output.append(best)
        return output


CANDIDATE_FACTORIES = {
    "C1_balanced_classical_c1": lambda: BalancedClassicalLinear(1.0),
    "C2_balanced_classical_c4": lambda: BalancedClassicalLinear(4.0),
    "C3_balanced_linear_margin": BalancedLinearMargin,
    "C4_semantic_factor_tree": SemanticFactorTree,
    "C5_semantic_factor_linear": SemanticFactorLinear,
    "C6_hybrid_semantic_safety": HybridSemanticSafetyCandidate,
}


def make_candidate(name: str):
    try:
        return CANDIDATE_FACTORIES[name]()
    except KeyError as exc:
        raise ValueError(f"unknown candidate: {name}") from exc
