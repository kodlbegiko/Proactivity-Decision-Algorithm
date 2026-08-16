from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .policy import FACTOR_VALUES, CRITICAL_FACTORS, project_valid_state, select_action


def norm(text: str) -> str:
    text = text.lower().replace("‑", "-").replace("—", "-")
    text = re.sub(r"[^a-z0-9_\-\s.;']+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass
class Prediction:
    state: Dict[str, Any]
    action: str
    confidences: Dict[str, float]
    unresolved: List[str]


class SymbolicParser:
    """High-precision development-root baseline; intentionally no holdout lexicon."""
    def __init__(self, phrase_index: Dict[str, Dict[Any, List[str]]]):
        self.index = {f: {v: [norm(x) for x in ps] for v, ps in byv.items()} for f, byv in phrase_index.items()}
        self.defaults = {
            "permission": "not_required", "information": "insufficient", "urgency": "none",
            "need": "none", "side_effect": "none", "risk": "medium",
            "reversibility": "irreversible", "deferral_available": False,
            "execution_possible": False, "clarification_possible": True,
            "acknowledged": False, "completed": False,
        }

    def predict_one(self, text: str) -> Prediction:
        t = norm(text)
        state, conf, unresolved = {}, {}, []
        for f, byv in self.index.items():
            hits: List[Tuple[int, Any, str]] = []
            for v, phrases in byv.items():
                for p in phrases:
                    pos = t.rfind(p)
                    if pos >= 0: hits.append((pos, v, p))
            if hits:
                hits.sort(key=lambda x: x[0])
                state[f] = hits[-1][1]
                conf[f] = 1.0
                if len({h[1] for h in hits}) > 1 and "after review" not in t and "now" not in t:
                    unresolved.append(f)
            else:
                state[f] = self.defaults[f]
                conf[f] = 0.0
                unresolved.append(f)
        state = project_valid_state(state)
        return Prediction(state, select_action(state), conf, unresolved)

    def predict(self, texts: Iterable[str]) -> List[Prediction]:
        return [self.predict_one(t) for t in texts]


class ContrastiveEvidenceScorer:
    def __init__(self, random_state: int = 101001):
        self.random_state = random_state
        self.word = TfidfVectorizer(ngram_range=(1, 2), lowercase=True, min_df=2, max_features=8000, sublinear_tf=True)
        self.char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True, min_df=2, max_features=12000, sublinear_tf=True)
        self.models: Dict[str, LogisticRegression] = {}

    def fit(self, records: List[Dict[str, Any]]) -> "ContrastiveEvidenceScorer":
        texts = [r["text"] for r in records]
        X = hstack([self.word.fit_transform(texts), self.char.fit_transform(texts)], format="csr")
        for f in FACTOR_VALUES:
            y = [str(r["state"][f]) for r in records]
            m = LogisticRegression(max_iter=500, C=4.0, solver="liblinear", random_state=self.random_state)
            m.fit(X, y)
            self.models[f] = m
        return self

    def _X(self, texts: List[str]):
        return hstack([self.word.transform(texts), self.char.transform(texts)], format="csr")

    @staticmethod
    def _decode_label(f: str, label: str) -> Any:
        if f in {"deferral_available", "execution_possible", "clarification_possible", "acknowledged", "completed"}:
            return label == "True"
        return label

    def predict(self, texts: Iterable[str]) -> List[Prediction]:
        texts = list(texts)
        X = self._X(texts)
        rows = [({}, {}, []) for _ in texts]
        for f, m in self.models.items():
            probs = m.predict_proba(X); classes = m.classes_; idx = probs.argmax(axis=1)
            for i in range(len(texts)):
                label = classes[idx[i]]; p = float(probs[i, idx[i]])
                rows[i][0][f] = self._decode_label(f, label); rows[i][1][f] = p
                if p < 0.55: rows[i][2].append(f)
        out = []
        for state, conf, unresolved in rows:
            state = project_valid_state(state)
            out.append(Prediction(state, select_action(state), conf, unresolved))
        return out


class HybridEvidenceLattice:
    def __init__(self, phrase_index: Dict[str, Dict[Any, List[str]]], random_state: int = 101001):
        self.symbolic = SymbolicParser(phrase_index)
        self.ml = ContrastiveEvidenceScorer(random_state=random_state)

    def fit(self, records: List[Dict[str, Any]]) -> "HybridEvidenceLattice":
        self.ml.fit(records)
        return self

    def predict(self, texts: Iterable[str]) -> List[Prediction]:
        texts = list(texts); sp = self.symbolic.predict(texts); mp = self.ml.predict(texts); out: List[Prediction] = []
        for s, m in zip(sp, mp):
            state = dict(m.state); conf = dict(m.confidences); unresolved = set(m.unresolved)
            for f in FACTOR_VALUES:
                if s.confidences.get(f, 0.0) == 1.0:
                    state[f] = s.state[f]; conf[f] = 1.0; unresolved.discard(f)
            state = project_valid_state(state); action = select_action(state)
            if action == "ACT" and any(conf.get(f, 0.0) < 0.72 or f in unresolved for f in CRITICAL_FACTORS):
                gated = dict(state); gated["information"] = "insufficient"; gated["clarification_possible"] = True
                state = project_valid_state(gated); action = select_action(state)
            out.append(Prediction(state, action, conf, sorted(unresolved)))
        return out
