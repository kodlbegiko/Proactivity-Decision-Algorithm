"""Protocol-v2 recovery candidate families.

Inference boundary: only candidate-visible ``domain`` and ``observation``.
No oracle/spec/private-state imports are permitted in this module.
"""
from __future__ import annotations

import re
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
SEED = 20260815
FACTORS = (
    "permission", "information", "urgency", "need", "side_effect", "risk",
    "reversibility", "deferral_available", "execution_possible",
    "clarification_possible", "acknowledged", "completed",
)


def _norm(text: str) -> str:
    text = text.lower().replace("’", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text)


def _has(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def extract_visible_semantic_factors(observation: str) -> dict[str, object]:
    """Parse independently designed natural-language factor evidence.

    The parser is clause-order independent, uses multiple lexical families, and
    gives explicit negation constructions precedence over generic matching.
    Unknown/ambiguous evidence fails closed to ``unknown`` rather than silently
    inheriting a positive value.
    """
    t = _norm(observation)

    if _has(t, r"not the case that (?:the )?authorization is unavailable", r"authorization is not unavailable"):
        permission = "granted"
    elif _has(t, r"no authorization (?:is )?(?:needed|required)", r"authorization (?:is )?unnecessary", r"may proceed without (?:seeking )?authorization", r"does not require authorization"):
        permission = "not_required"
    elif _has(t, r"authorization (?:has been |is )?(?:granted|approved|cleared|in place)", r"approval is already in place", r"permission is already secured"):
        permission = "granted"
    elif _has(t, r"authorization (?:is )?(?:missing|absent|pending|still needed|not yet granted|not yet approved)", r"approval has not arrived", r"permission is still outstanding"):
        permission = "missing"
    else:
        permission = "unknown"

    if _has(t, r"facts? (?:are |remain )?(?:in conflict|contradictory|inconsistent)", r"evidence conflicts", r"accounts do not agree", r"the record disagrees with itself"):
        information = "contradictory"
    elif _has(t, r"information (?:is )?(?:insufficient|incomplete)", r"key facts? (?:are )?missing", r"not enough evidence", r"necessary evidence has not arrived", r"cannot establish the needed facts"):
        information = "insufficient"
    elif _has(t, r"information (?:is )?(?:sufficient|complete enough)", r"enough evidence is available", r"necessary facts? (?:are )?(?:available|settled)", r"the record is complete enough"):
        information = "sufficient"
    else:
        information = "unknown"

    if _has(t, r"window (?:has )?(?:expired|closed|passed)", r"deadline (?:has )?(?:expired|passed)", r"already too late for the current window", r"relevant period is over"):
        urgency = "expired"
    elif _has(t, r"urgency (?:is )?(?:high|critical)", r"needs attention immediately", r"time pressure is severe", r"cannot safely wait"):
        urgency = "high"
    elif _has(t, r"urgency (?:is )?(?:normal|ordinary)", r"ordinary timing applies", r"timely but not urgent", r"normal time pressure"):
        urgency = "normal"
    elif _has(t, r"no current urgency", r"no time pressure", r"timing can wait", r"nothing is time-sensitive now"):
        urgency = "none"
    else:
        urgency = "unknown"

    if _has(t, r"no intervention is needed", r"no current need to intervene", r"nothing calls for intervention", r"intervention need is absent"):
        need = "none"
    elif _has(t, r"intervention is optional", r"an optional recommendation could help", r"intervention is discretionary", r"help would be nice but not necessary"):
        need = "optional"
    elif _has(t, r"material intervention is needed", r"substantive intervention is required", r"there is a material need to intervene", r"the situation calls for real intervention"):
        need = "material"
    else:
        need = "unknown"

    if _has(t, r"no side effect is expected", r"no material side effect", r"nothing outside the decision changes", r"effect scope is none"):
        side_effect = "none"
    elif _has(t, r"effect stays local", r"local system would change", r"impact is confined locally", r"side effect scope is local"):
        side_effect = "local"
    elif _has(t, r"effect reaches an external (?:system|party)", r"an outside system would change", r"impact extends beyond the local system", r"side effect scope is external"):
        side_effect = "external"
    else:
        side_effect = "unknown"

    if _has(t, r"risk (?:is |stays )?low", r"low-risk outcome", r"risk remains minimal"):
        risk = "low"
    elif _has(t, r"risk (?:is |stays )?(?:medium|moderate)", r"moderate-risk outcome", r"risk is neither low nor high"):
        risk = "medium"
    elif _has(t, r"risk (?:is |stays )?high", r"high-risk outcome", r"risk is substantial"):
        risk = "high"
    else:
        risk = "unknown"

    if _has(t, r"not irreversible", r"can be (?:reversed|undone|rolled back)", r"reversal remains possible", r"the change is reversible"):
        reversibility = "reversible"
    elif _has(t, r"cannot be (?:reversed|undone|rolled back)", r"reversal is impossible", r"the change is irreversible"):
        reversibility = "irreversible"
    else:
        reversibility = "unknown"

    if _has(t, r"a later trigger is defined", r"there is a scheduled follow-up trigger", r"a concrete future trigger exists", r"deferral has a defined trigger"):
        deferral_available = True
    elif _has(t, r"no later trigger is defined", r"there is no scheduled follow-up trigger", r"no concrete future trigger exists", r"deferral lacks a trigger"):
        deferral_available = False
    else:
        deferral_available = "unknown"

    if _has(t, r"execution is possible", r"the action can be carried out now", r"the capability is available", r"nothing blocks execution"):
        execution_possible = True
    elif _has(t, r"execution is not possible", r"the action cannot be carried out now", r"the capability is unavailable", r"execution is blocked"):
        execution_possible = False
    else:
        execution_possible = "unknown"

    if _has(t, r"clarification is possible", r"the missing point can be clarified", r"a clarification channel is available", r"we can ask for clarification"):
        clarification_possible = True
    elif _has(t, r"clarification is not possible", r"the missing point cannot be clarified", r"no clarification channel is available", r"we cannot obtain clarification"):
        clarification_possible = False
    else:
        clarification_possible = "unknown"

    if _has(t, r"acknowledgement is present", r"the user has acknowledged", r"receipt has been acknowledged", r"the notice was acknowledged"):
        acknowledged = True
    elif _has(t, r"acknowledgement is absent", r"the user has not acknowledged", r"receipt has not been acknowledged", r"the notice remains unacknowledged"):
        acknowledged = False
    else:
        acknowledged = "unknown"

    if _has(t, r"not incomplete", r"the task is complete", r"the objective has been resolved", r"work is already finished", r"completion is confirmed"):
        completed = True
    elif _has(t, r"the task is incomplete", r"the objective remains unresolved", r"work is still unfinished", r"completion has not happened"):
        completed = False
    else:
        completed = "unknown"

    return {
        "permission": permission,
        "information": information,
        "urgency": urgency,
        "need": need,
        "side_effect": side_effect,
        "risk": risk,
        "reversibility": reversibility,
        "deferral_available": deferral_available,
        "execution_possible": execution_possible,
        "clarification_possible": clarification_possible,
        "acknowledged": acknowledged,
        "completed": completed,
    }


class _ObservationSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X): return [row["observation"] for row in X]


class _DomainSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X): return np.asarray([[row["domain"]] for row in X], dtype=object)


class _SemanticSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X): return [extract_visible_semantic_factors(row["observation"]) for row in X]


def _text_features() -> FeatureUnion:
    return FeatureUnion([
        ("word", Pipeline([("select", _ObservationSelector()), ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, sublinear_tf=True, min_df=1))])),
        ("char", Pipeline([("select", _ObservationSelector()), ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), lowercase=True, sublinear_tf=True, min_df=1))])),
        ("domain", Pipeline([("select", _DomainSelector()), ("onehot", OneHotEncoder(handle_unknown="ignore"))])),
    ])


def _factor_features() -> Pipeline:
    return Pipeline([("select", _SemanticSelector()), ("vectorize", DictVectorizer(sparse=True))])


class _PipelineCandidate:
    def __init__(self, pipeline: Pipeline): self.pipeline = pipeline
    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        self.pipeline.fit(list(records), list(labels)); return self
    def predict(self, records: Sequence[dict]) -> list[str]:
        return [str(x) for x in self.pipeline.predict(list(records)).tolist()]
    def predict_proba(self, records: Sequence[dict]):
        if not hasattr(self.pipeline, "predict_proba"):
            return None
        return self.pipeline.predict_proba(list(records))


class FactorLinear(_PipelineCandidate):
    def __init__(self, c: float):
        super().__init__(Pipeline([
            ("features", _factor_features()),
            ("classifier", LogisticRegression(C=c, class_weight="balanced", max_iter=4000, random_state=SEED, solver="lbfgs")),
        ]))


class FactorTree(_PipelineCandidate):
    def __init__(self):
        super().__init__(Pipeline([
            ("features", _factor_features()),
            ("classifier", DecisionTreeClassifier(max_depth=14, class_weight="balanced", random_state=SEED, min_samples_leaf=1)),
        ]))


class TextLR(_PipelineCandidate):
    def __init__(self, c: float):
        super().__init__(Pipeline([
            ("features", _text_features()),
            ("classifier", LogisticRegression(C=c, class_weight="balanced", max_iter=4000, random_state=SEED, solver="lbfgs")),
        ]))


class TextSVC(_PipelineCandidate):
    def __init__(self):
        super().__init__(Pipeline([
            ("features", _text_features()),
            ("classifier", LinearSVC(C=1.0, class_weight="balanced", random_state=SEED)),
        ]))


class HybridLR(_PipelineCandidate):
    def __init__(self, c: float):
        super().__init__(Pipeline([
            ("features", FeatureUnion([("semantic", _factor_features()), ("text", _text_features())])),
            ("classifier", LogisticRegression(C=c, class_weight="balanced", max_iter=4000, random_state=SEED, solver="lbfgs")),
        ]))


CANDIDATE_FACTORIES = {
    "V3A_factor_linear_c1": lambda: FactorLinear(1.0),
    "V3A_factor_linear_c4": lambda: FactorLinear(4.0),
    "V3A_factor_tree": FactorTree,
    "V3C_text_lr_c1": lambda: TextLR(1.0),
    "V3C_text_lr_c4": lambda: TextLR(4.0),
    "V3C_text_svc": TextSVC,
    "V3D_hybrid_c1": lambda: HybridLR(1.0),
    "V3D_hybrid_c4": lambda: HybridLR(4.0),
}


def make_candidate(name: str):
    try:
        return CANDIDATE_FACTORIES[name]()
    except KeyError as exc:
        raise ValueError(f"unknown preregistered candidate: {name}") from exc


SELECTED_CONFIGURATION = "V3A_factor_tree"

def make_selected_candidate():
    return FactorTree()
