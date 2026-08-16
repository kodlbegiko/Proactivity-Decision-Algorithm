"""Protocol v2 Gate-D raw-context comparison baselines.

This module is intentionally isolated from evaluator-only data. Every baseline
receives only records containing the candidate-visible fields needed by that
baseline and, at fit time, development labels supplied by the evaluator.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import OneHotEncoder

ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
SEED = 20260814


def _majority(labels: Sequence[str]) -> str:
    counts = Counter(labels)
    if not counts:
        raise ValueError("development labels must not be empty")
    best = max(counts.values())
    return sorted(label for label, count in counts.items() if count == best)[0]


class MajorityAction:
    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        self.action_ = _majority(labels)
        return self

    def predict(self, records: Sequence[dict]) -> list[str]:
        return [self.action_] * len(records)


class PriorSampledRandom:
    def __init__(self, seed: int = SEED):
        self.seed = seed

    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        counts = Counter(labels)
        self.actions_ = sorted(counts)
        total = sum(counts.values())
        self.probabilities_ = np.array([counts[a] / total for a in self.actions_], dtype=float)
        return self

    def predict(self, records: Sequence[dict]) -> list[str]:
        rng = np.random.default_rng(self.seed)
        values = rng.choice(self.actions_, size=len(records), p=self.probabilities_)
        return [str(v) for v in values.tolist()]


class DomainOnly:
    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        grouped: dict[str, list[str]] = defaultdict(list)
        for record, label in zip(records, labels):
            grouped[record["domain"]].append(label)
        self.global_action_ = _majority(labels)
        self.domain_action_ = {domain: _majority(values) for domain, values in grouped.items()}
        return self

    def predict(self, records: Sequence[dict]) -> list[str]:
        return [self.domain_action_.get(record["domain"], self.global_action_) for record in records]


class SimpleLexical:
    def __init__(self):
        self.pipeline = Pipeline([
            ("vectorizer", CountVectorizer(ngram_range=(1, 1), lowercase=True)),
            ("classifier", MultinomialNB(alpha=1.0)),
        ])

    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        self.pipeline.fit([r["observation"] for r in records], labels)
        return self

    def predict(self, records: Sequence[dict]) -> list[str]:
        return [str(x) for x in self.pipeline.predict([r["observation"] for r in records]).tolist()]


class _ObservationSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [r["observation"] for r in X]


class _DomainSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.asarray([[r["domain"]] for r in X], dtype=object)


class StrongClassicalText:
    def __init__(self, seed: int = SEED):
        features = FeatureUnion([
            ("word", Pipeline([
                ("select", _ObservationSelector()),
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, sublinear_tf=True)),
            ])),
            ("char", Pipeline([
                ("select", _ObservationSelector()),
                ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), lowercase=True, sublinear_tf=True)),
            ])),
            ("domain", Pipeline([
                ("select", _DomainSelector()),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ])),
        ])
        self.pipeline = Pipeline([
            ("features", features),
            ("classifier", LogisticRegression(C=1.0, max_iter=2000, random_state=seed, solver="lbfgs")),
        ])

    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        self.pipeline.fit(list(records), labels)
        return self

    def predict(self, records: Sequence[dict]) -> list[str]:
        return [str(x) for x in self.pipeline.predict(list(records)).tolist()]


@dataclass(frozen=True)
class TransparentHeuristic:
    """Fixed, deliberately simple surface-keyword comparison baseline."""

    def fit(self, records: Sequence[dict], labels: Sequence[str]):
        return self

    @staticmethod
    def _one(record: dict) -> str:
        text = f"{record['domain']} {record['observation']}".lower()
        if "underlying task is completed" in text or "completion has occurred" in text or "objective is resolved" in text:
            return "IGNORE"
        if "contradiction" in text or "insufficient" in text or "lacks necessary facts" in text:
            return "ASK"
        if "execution is not currently possible" in text or "capability is unavailable" in text:
            return "WAIT"
        if "side effect is external" in text or "external side effect" in text:
            return "NOTIFY"
        if (
            ("authorization is required and present" in text or "authorization is not required" in text or "no authorization is required" in text)
            and ("can be reversed" in text or "reversible" in text)
            and ("can currently carry out" in text or "capability is available" in text or "execution is currently possible" in text)
            and "risk is low" in text
        ):
            return "ACT"
        return "SUGGEST"

    def predict(self, records: Sequence[dict]) -> list[str]:
        return [self._one(record) for record in records]


BASELINE_FACTORIES = {
    "B0_majority": MajorityAction,
    "B1_prior_sampled_random": PriorSampledRandom,
    "B2_domain_only": DomainOnly,
    "B3_simple_lexical": SimpleLexical,
    "B4_strong_classical_text": StrongClassicalText,
    "B5_transparent_heuristic": TransparentHeuristic,
}


def make_baseline(name: str):
    try:
        return BASELINE_FACTORIES[name]()
    except KeyError as exc:
        raise ValueError(f"unknown baseline: {name}") from exc
