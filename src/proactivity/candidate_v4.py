"""Candidate-v4 generalization-recovery architectures.

Inference boundary: candidates read only ``domain`` and ``observation``.  The
module contains no imports from protected or confirmatory data.  Candidate-v4
reconstructs a latent public-specification state from natural-language clauses
and then applies the public Protocol-v2 decision semantics conservatively.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
SEED = 20260815
FIELDS = (
    "permission", "information", "urgency", "need", "side_effect", "risk",
    "reversibility", "deferral_available", "execution_possible",
    "clarification_possible", "acknowledged", "completed",
)
VALUES: dict[str, tuple[object, ...]] = {
    "permission": ("not_required", "missing", "granted"),
    "information": ("sufficient", "insufficient", "contradictory"),
    "urgency": ("none", "normal", "high", "expired"),
    "need": ("none", "optional", "material"),
    "side_effect": ("none", "local", "external"),
    "risk": ("low", "medium", "high"),
    "reversibility": ("reversible", "irreversible"),
    "deferral_available": (False, True),
    "execution_possible": (False, True),
    "clarification_possible": (False, True),
    "acknowledged": (False, True),
    "completed": (False, True),
}

# Factor anchors route a clause to one latent factor.  Value cues then recover
# the value within that factor.  This is intentionally compositional: it does
# not require a full sentence to match a fixed template.
FACTOR_ANCHORS: dict[str, tuple[str, ...]] = {
    "permission": ("approval", "authorization", "permission", "authority", "green light", "go-ahead", "授權", "批准", "核准", "權限"),
    "information": ("facts", "evidence", "record", "information", "picture", "sources", "accounts", "complete enough", "facts line up", "資訊", "資料", "事實", "來源", "說法"),
    "urgency": ("time pressure", "urgent", "urgency", "timing", "deadline", "window", "clock", "queue", "period", "immediate attention", "attention right away", "期限", "時間", "時效", "急迫", "時間窗", "立即注意"),
    "need": ("intervention", "recommendation", "help", "need to intervene", "nothing to do", "nudge", "material intervention", "optional recommendation", "處理", "介入", "協助", "建議", "需求"),
    "side_effect": ("side effect", "effect scope", "local system", "outside system", "external party", "system state", "local state", "system boundary", "impact", "副作用", "本地系統", "外部系統", "內部狀態", "影響"),
    "risk": ("risk", "downside", "exposure", "風險"),
    "reversibility": ("undo", "rollback", "reversible", "irreversible", "recoverable", "one-way", "復原", "回滾", "不可復原"),
    "deferral_available": ("trigger", "follow-up", "deferral", "checkpoint", "revisit", "觸發", "檢查點", "後續"),
    "execution_possible": ("execution", "execute", "carried out", "capability", "執行", "能力"),
    "clarification_possible": ("clarification", "clarified", "ask", "question", "ambiguity", "澄清", "提問", "詢問"),
    "acknowledged": ("acknowledged", "acknowledgement", "receipt", "confirmed seeing", "confirmed", "確認", "知悉", "收到"),
    "completed": ("task", "objective", "completion", "work", "closed out", "任務", "目標", "完成"),
}

VALUE_CUES: dict[str, dict[object, tuple[str, ...]]] = {
    "permission": {
        "not_required": ("no approval", "not required", "unnecessary", "standing authority", "without permission", "no permission dependency", "不需要", "無須", "既有權限"),
        "missing": ("pending", "not been granted", "outstanding", "not arrived", "waiting on", "unavailable", "尚未", "等待"),
        "granted": ("secured", "in place", "was granted", "already granted", "go-ahead", "cleared", "on record", "已取得", "已核准", "已經核准", "批准"),
    },
    "information": {
        "sufficient": ("complete", "enough", "sufficient", "clear", "what we need", "足夠", "完整"),
        "insufficient": ("missing", "incomplete", "not enough", "holes", "thin", "不足", "尚缺"),
        "contradictory": ("conflicts", "disagree", "inconsistent", "different stories", "contradictory", "矛盾", "衝突"),
    },
    "urgency": {
        "none": ("no time pressure", "can wait", "nothing is urgent", "not pressing", "no rush", "urgency is absent", "沒有時間壓力", "可以稍後", "沒有急迫"),
        "normal": ("ordinary", "timely but not urgent", "normal", "routine", "一般", "正常"),
        "high": ("immediate", "severe", "urgent", "pressing hard", "right away", "very high", "立即", "很高", "高"),
        "expired": ("closed", "passed", "over", "gone", "expired", "期限已過", "已關閉", "過期"),
    },
    "need": {
        "none": ("no intervention", "nothing calls", "no present need", "nothing to do", "not need action", "need is absent", "不需要介入", "沒有需要", "沒有介入需求"),
        "optional": ("optional", "could help", "discretionary", "nudge", "nice-to-have", "可提供建議", "可選擇", "可選"),
        "material": ("substantive", "material", "real need", "concrete intervention", "needs real handling", "required", "實質介入", "具體處理"),
    },
    "side_effect": {
        "none": ("nothing outside", "no material side effect", "scope is none", "no system state", "changes nothing", "side effects are absent", "沒有實質副作用", "不會改變", "沒有副作用"),
        "local": ("local system", "confined locally", "local state", "contained internally", "remain local", "本地系統", "內部狀態", "只在本地"),
        "external": ("outside system", "external party", "beyond the local", "crosses the system boundary", "externally", "外部系統", "他人", "跨出", "影響外部"),
    },
    "risk": {
        "low": ("low", "minimal", "small", "comfortably low", "低"),
        "medium": ("moderate", "medium", "middle", "bounded downside", "中等", "中度"),
        "high": ("high", "substantial", "serious", "uncomfortably high", "高", "重大"),
    },
    "reversibility": {
        "reversible": ("can be undone", "rollback is available", "reversible", "clean undo", "recoverable", "remains reversible", "可以復原", "可回滾", "仍可復原"),
        "irreversible": ("cannot be undone", "rollback is impossible", "irreversible", "no undo", "one-way", "not reversible", "無法復原", "沒有回滾", "不可復原"),
    },
    "deferral_available": {
        False: ("no defined", "no scheduled", "lacks", "no event", "nothing specific", "no future trigger", "沒有明確", "沒有具體", "沒有後續"),
        True: ("defined future", "scheduled follow-up", "concrete trigger", "checkpoint is already", "future trigger is available", "已有明確", "有具體", "已有後續"),
    },
    "execution_possible": {
        False: ("blocked", "cannot be carried out", "unavailable", "cannot execute", "not currently available", "impossible", "無法執行", "不可用", "不可行"),
        True: ("can happen", "can be carried out", "available", "capability is live", "able to execute", "possible", "可以執行", "已可用", "可行"),
    },
    "clarification_possible": {
        False: ("no available", "cannot be clarified", "cannot be obtained", "nothing to ask", "no clarification route", "impossible", "沒有可澄清", "無法透過提問", "無法澄清"),
        True: ("is available", "can be clarified", "can ask", "route to ask", "question can resolve", "possible", "可以進一步", "可用的澄清", "可以澄清"),
    },
    "acknowledged": {
        False: ("not acknowledged", "unacknowledged", "no acknowledgement", "nobody has confirmed", "still absent", "尚未收到", "還沒有", "仍未確認"),
        True: ("has acknowledged", "was acknowledged", "acknowledgement is present", "seen and acknowledged", "already present", "已經收到", "已表示知悉", "已確認"),
    },
    "completed": {
        False: ("unfinished", "unresolved", "has not happened", "still open", "not done", "remains false", "尚未完成", "仍未解決", "仍未完成"),
        True: ("already complete", "has been resolved", "is confirmed", "closed out", "already done", "already true", "已完成", "已經解決", "已經完成"),
    },
}

# Negative forms receive an explicit scoring bonus so phrases such as
# "deferral lacks a concrete trigger" cannot be misread as positive merely
# because the positive lexical tail "concrete trigger" is also present.
_NEGATIVE_WORDS = re.compile(
    r"\b(no|not|cannot|without|absent|unavailable|impossible|unfinished|unresolved|incomplete|lacks|missing|pending|outstanding|unacknowledged|blocked)\b"
)
_NEGATIVE_ZH = ("沒有", "無法", "尚未", "不可", "不足", "矛盾", "衝突")


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower().replace("’", "'")
    return re.sub(r"\s+", " ", text)


def split_clauses(text: str) -> list[str]:
    pattern = r"[.;|/。；]+|\s+—\s+|,\s*(?:while|and)\s+|(?:^|\s)(?:additionally|given that)\s+"
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    return [part.strip(" ,:-—／") for part in parts if len(part.strip(" ,:-—／")) >= 2]


def _factor_score(clause: str, anchors: Iterable[str]) -> float:
    text = _norm(clause)
    return sum(1.0 + min(len(anchor), 20) / 20.0 for anchor in anchors if _norm(anchor) in text)


def _cue_score(clause: str, cues: Iterable[str]) -> float:
    text = " " + _norm(clause) + " "
    best = 0.0
    for cue in cues:
        normalized = _norm(cue)
        if normalized not in text:
            continue
        score = 1.0 + min(len(normalized), 30) / 30.0
        if _NEGATIVE_WORDS.search(normalized) or any(token in normalized for token in _NEGATIVE_ZH):
            score += 0.8
        best = max(best, score)
    return best


@dataclass(frozen=True)
class ParseResult:
    state: dict[str, object]
    confidence: dict[str, float]
    source_clause: dict[str, str]


class SemanticAtomParser:
    """Clause-routed, value-cue latent-state parser."""

    def parse(self, observation: str) -> ParseResult:
        clauses = split_clauses(observation)
        state: dict[str, object] = {}
        confidence: dict[str, float] = {}
        source: dict[str, str] = {}
        for field in FIELDS:
            scored: list[tuple[float, float, float, object, str, dict[object, float]]] = []
            for clause in clauses:
                anchor_score = _factor_score(clause, FACTOR_ANCHORS[field])
                value_scores = {value: _cue_score(clause, VALUE_CUES[field][value]) for value in VALUES[field]}
                best_value = max(value_scores, key=value_scores.get)
                best_value_score = value_scores[best_value]
                joint = anchor_score * (1.0 + best_value_score)
                scored.append((joint, anchor_score, best_value_score, best_value, clause, value_scores))
            if not scored:
                state[field] = "unknown"
                confidence[field] = 0.0
                source[field] = ""
                continue
            joint, anchor_score, value_score, best_value, clause, value_scores = max(scored, key=lambda item: item[0])
            source[field] = clause
            if anchor_score <= 0.0 or value_score <= 0.0:
                state[field] = "unknown"
                confidence[field] = 0.0
                continue
            ordered = sorted(value_scores.values(), reverse=True)
            margin = ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0)
            state[field] = best_value
            confidence[field] = min(1.0, 0.45 + 0.10 * anchor_score + 0.15 * value_score + 0.15 * margin)
        return ParseResult(state, confidence, source)


def decide_from_partial_state(state: Mapping[str, object]) -> str:
    """Conservative implementation of the public Protocol-v2 rule ordering.

    A rule fires only when its required predicates are explicitly reconstructed.
    Unknown evidence never authorizes ACT.
    """
    s = state
    if s.get("completed") is True:
        return "IGNORE"
    if s.get("need") == "none" and s.get("deferral_available") is False:
        return "IGNORE"
    if s.get("need") == "none" and s.get("deferral_available") is True:
        return "WAIT"
    if s.get("information") in ("insufficient", "contradictory") and s.get("clarification_possible") is True and s.get("need") in ("optional", "material"):
        return "ASK"
    if s.get("information") in ("insufficient", "contradictory") and s.get("clarification_possible") is False and s.get("urgency") in ("high", "expired") and s.get("need") == "material":
        return "NOTIFY"
    if s.get("information") in ("insufficient", "contradictory") and s.get("clarification_possible") is False:
        return "WAIT"
    if s.get("acknowledged") is True and s.get("urgency") in ("none", "normal") and s.get("deferral_available") is True and s.get("need") in ("optional", "material"):
        return "WAIT"
    if s.get("urgency") == "expired" and s.get("need") == "material":
        return "NOTIFY"
    if s.get("side_effect") == "external" and s.get("permission") == "missing" and s.get("need") == "material":
        return "ASK"
    if s.get("side_effect") == "local" and s.get("permission") == "missing" and s.get("need") == "material":
        return "ASK"
    if s.get("side_effect") in ("local", "external") and s.get("risk") in ("medium", "high") and s.get("need") == "material":
        return "ASK"
    if s.get("side_effect") in ("local", "external") and s.get("reversibility") == "irreversible" and s.get("need") == "material":
        return "ASK"
    if (
        s.get("side_effect") == "external"
        and s.get("permission") == "granted"
        and s.get("information") == "sufficient"
        and s.get("risk") == "low"
        and s.get("reversibility") == "reversible"
        and s.get("execution_possible") is True
        and s.get("need") == "material"
    ):
        return "ACT"
    if (
        s.get("side_effect") == "local"
        and s.get("permission") in ("not_required", "granted")
        and s.get("information") == "sufficient"
        and s.get("risk") == "low"
        and s.get("reversibility") == "reversible"
        and s.get("execution_possible") is True
        and s.get("need") == "material"
    ):
        return "ACT"
    if s.get("need") == "material" and s.get("urgency") == "high":
        return "NOTIFY"
    if s.get("need") == "material" and s.get("urgency") == "normal":
        return "NOTIFY"
    if s.get("need") == "material" and s.get("urgency") == "none" and s.get("deferral_available") is True:
        return "WAIT"
    if s.get("need") == "material":
        return "SUGGEST"
    if s.get("need") == "optional":
        return "SUGGEST"
    if s.get("need") == "none":
        return "IGNORE"
    return "WAIT"


class AtomStateMachineCandidate:
    def __init__(self, act_confidence_floor: float = 0.55):
        self.parser = SemanticAtomParser()
        self.act_confidence_floor = act_confidence_floor

    def fit(self, records: Sequence[dict], labels: Sequence[str], *, factor_supervision=None):
        return self

    def parse_record(self, record: Mapping[str, object]) -> ParseResult:
        return self.parser.parse(str(record["observation"]))

    def predict_one(self, record: Mapping[str, object]) -> str:
        parsed = self.parse_record(record)
        action = decide_from_partial_state(parsed.state)
        if action == "ACT":
            critical = ("permission", "information", "risk", "reversibility", "execution_possible", "need", "side_effect")
            if any(parsed.state.get(field) == "unknown" for field in critical):
                return "ASK"
            if min(parsed.confidence[field] for field in critical) < self.act_confidence_floor:
                return "ASK"
        return action

    def predict(self, records: Sequence[dict]) -> list[str]:
        return [self.predict_one(record) for record in records]


class LearnedClauseParser:
    """Development-supervised clause parser used by V4A and V4C fallback."""

    def __init__(self, c: float = 4.0, ngram_max: int = 6):
        self.c = c
        self.ngram_max = ngram_max
        self.router: Pipeline | None = None
        self.value_models: dict[str, Pipeline] = {}

    @staticmethod
    def _value_label(value: object) -> str:
        if value is True:
            return "__true__"
        if value is False:
            return "__false__"
        return str(value)

    @staticmethod
    def _decode_value(label: str) -> object:
        if label == "__true__":
            return True
        if label == "__false__":
            return False
        return label

    def fit(self, factor_supervision: Sequence[tuple[str, str, object]]):
        texts = [item[0] for item in factor_supervision]
        fields = [item[1] for item in factor_supervision]
        self.router = Pipeline([
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, self.ngram_max), lowercase=True, sublinear_tf=True)),
            ("lr", LogisticRegression(C=self.c, class_weight="balanced", max_iter=3000, random_state=SEED)),
        ])
        self.router.fit(texts, fields)
        for field in FIELDS:
            subset = [item for item in factor_supervision if item[1] == field]
            model = Pipeline([
                ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, self.ngram_max), lowercase=True, sublinear_tf=True)),
                ("lr", LogisticRegression(C=self.c, class_weight="balanced", max_iter=3000, random_state=SEED)),
            ])
            model.fit([item[0] for item in subset], [self._value_label(item[2]) for item in subset])
            self.value_models[field] = model
        return self

    def parse(self, observation: str) -> ParseResult:
        if self.router is None:
            raise RuntimeError("LearnedClauseParser must be fitted before prediction")
        clauses = split_clauses(observation)
        router_probs = self.router.predict_proba(clauses)
        router_classes = list(self.router.classes_)
        state: dict[str, object] = {}
        confidence: dict[str, float] = {}
        source: dict[str, str] = {}
        for field in FIELDS:
            field_index = router_classes.index(field)
            clause_index = int(np.argmax(router_probs[:, field_index]))
            clause = clauses[clause_index]
            value_model = self.value_models[field]
            value_probs = value_model.predict_proba([clause])[0]
            best_index = int(np.argmax(value_probs))
            state[field] = self._decode_value(str(value_model.classes_[best_index]))
            confidence[field] = float(router_probs[clause_index, field_index]) * float(value_probs[best_index])
            source[field] = clause
        # Public-schema consistency repair: never fabricate granted external permission.
        if state["side_effect"] == "none":
            state["permission"] = "not_required"
        elif state["side_effect"] == "external" and state["permission"] == "not_required":
            state["permission"] = "missing"
        return ParseResult(state, confidence, source)


class ClauseLinearCandidate:
    def __init__(self, c: float = 4.0, ngram_max: int = 6, act_confidence_floor: float = 0.55):
        self.parser = LearnedClauseParser(c=c, ngram_max=ngram_max)
        self.act_confidence_floor = act_confidence_floor

    def fit(self, records: Sequence[dict], labels: Sequence[str], *, factor_supervision=None):
        if factor_supervision is None:
            raise ValueError("factor_supervision is required for V4A")
        self.parser.fit(factor_supervision)
        return self

    def parse_record(self, record: Mapping[str, object]) -> ParseResult:
        return self.parser.parse(str(record["observation"]))

    def predict_one(self, record: Mapping[str, object]) -> str:
        parsed = self.parse_record(record)
        action = decide_from_partial_state(parsed.state)
        if action == "ACT":
            critical = ("permission", "information", "risk", "reversibility", "execution_possible", "need", "side_effect")
            if min(parsed.confidence[field] for field in critical) < self.act_confidence_floor:
                return "ASK"
        return action

    def predict(self, records: Sequence[dict]) -> list[str]:
        return [self.predict_one(record) for record in records]


class HybridGuardedCandidate:
    def __init__(self, c: float = 4.0, ngram_max: int = 6, act_confidence_floor: float = 0.55):
        self.atom = SemanticAtomParser()
        self.learned = LearnedClauseParser(c=c, ngram_max=ngram_max)
        self.act_confidence_floor = act_confidence_floor

    def fit(self, records: Sequence[dict], labels: Sequence[str], *, factor_supervision=None):
        if factor_supervision is None:
            raise ValueError("factor_supervision is required for V4C")
        self.learned.fit(factor_supervision)
        return self

    def parse_record(self, record: Mapping[str, object]) -> ParseResult:
        observation = str(record["observation"])
        atom = self.atom.parse(observation)
        learned = self.learned.parse(observation)
        state = dict(atom.state)
        confidence = dict(atom.confidence)
        source = dict(atom.source_clause)
        # Learned fallback is allowed only for unresolved non-ACT-critical factors.
        critical = {"permission", "information", "risk", "reversibility", "execution_possible", "need", "side_effect"}
        for field in FIELDS:
            if state[field] == "unknown" and field not in critical:
                state[field] = learned.state[field]
                confidence[field] = learned.confidence[field]
                source[field] = learned.source_clause[field]
        return ParseResult(state, confidence, source)

    def predict_one(self, record: Mapping[str, object]) -> str:
        parsed = self.parse_record(record)
        action = decide_from_partial_state(parsed.state)
        if action == "ACT":
            critical = ("permission", "information", "risk", "reversibility", "execution_possible", "need", "side_effect")
            if any(parsed.state[field] == "unknown" for field in critical):
                return "ASK"
            if min(parsed.confidence[field] for field in critical) < self.act_confidence_floor:
                return "ASK"
        return action

    def predict(self, records: Sequence[dict]) -> list[str]:
        return [self.predict_one(record) for record in records]


def make_candidate(name: str):
    factories = {
        "V4A_clause_linear_c4": lambda: ClauseLinearCandidate(c=4.0, ngram_max=6, act_confidence_floor=0.55),
        "V4A_clause_linear_c6": lambda: ClauseLinearCandidate(c=6.0, ngram_max=6, act_confidence_floor=0.55),
        "V4B_atom_state_machine_a55": lambda: AtomStateMachineCandidate(act_confidence_floor=0.55),
        "V4B_atom_state_machine_a65": lambda: AtomStateMachineCandidate(act_confidence_floor=0.65),
        "V4C_hybrid_guarded_c4_a55": lambda: HybridGuardedCandidate(c=4.0, ngram_max=6, act_confidence_floor=0.55),
        "V4C_hybrid_guarded_c6_a55": lambda: HybridGuardedCandidate(c=6.0, ngram_max=6, act_confidence_floor=0.55),
    }
    try:
        return factories[name]()
    except KeyError as exc:
        raise ValueError(f"unknown preregistered Candidate-v4 configuration: {name}") from exc


CANDIDATE_CONFIGURATIONS = (
    "V4A_clause_linear_c4",
    "V4A_clause_linear_c6",
    "V4B_atom_state_machine_a55",
    "V4B_atom_state_machine_a65",
    "V4C_hybrid_guarded_c4_a55",
    "V4C_hybrid_guarded_c6_a55",
)
