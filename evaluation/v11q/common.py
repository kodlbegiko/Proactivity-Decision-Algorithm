from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Iterable

PROTOCOL_VERSION = "V11Q-1"
SOURCE_FREEZE_COMMIT = "a59ea722d9d9c3b8bc83fc0a36e33f708c996b21"
DEVELOPMENT_TERMINAL_COMMIT = "fdfbf1662c0406637d3847635b25187b2f3c317b"
CANDIDATE_ID = "Candidate-v11B"
VARIANT = "B"

RUN_SEEDS = {"Q1": 6101, "Q2": 6203, "Q3": 6307, "Q4": 6413, "Q5": 6521}
ACTIONS = ("IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT")
FAMILIES = ("Lexical", "Rendering", "Compositional", "Negation", "Scope", "Temporal", "Mixed Adversarial")
FIELDS = (
    "permission", "information", "urgency", "need", "side_effect", "risk",
    "reversibility", "deferral_available", "execution_possible",
    "clarification_possible", "acknowledged", "completed",
)
ACT_CRITICAL_FIELDS = {
    "permission", "information", "risk", "reversibility",
    "execution_possible", "side_effect", "need",
}

CORE_PER_RUN = 300
INVARIANCE_GROUPS_PER_RUN = 12
INVARIANCE_REALIZATIONS = 3
COUNTERFACTUAL_PAIRS_PER_RUN = 42
EXAMPLES_PER_RUN = CORE_PER_RUN + INVARIANCE_GROUPS_PER_RUN * INVARIANCE_REALIZATIONS + COUNTERFACTUAL_PAIRS_PER_RUN * 2
assert EXAMPLES_PER_RUN == 420

THRESHOLDS = {
    "fresh_ood_macro_f1": 0.88,
    "family_macro_f1": {
        "Lexical": 0.85,
        "Rendering": 0.85,
        "Compositional": 0.85,
        "Negation": 0.85,
        "Scope": 0.85,
        "Temporal": 0.85,
        "Mixed Adversarial": 0.75,
    },
    "exact_latent_state_reconstruction": 0.75,
    "mean_factor_accuracy": 0.93,
    "act_critical_factor_accuracy": 0.97,
    "critical_unknown_rate_max": 0.05,
    "counterfactual_exact_pair": 0.85,
    "invariance_action_consistency": 0.92,
    "act_precision": 0.95,
    "act_recall": 0.90,
    "forbidden_act": 0,
    "invalid_action": 0,
    "catastrophic_collapse": False,
}

TECHNICAL_RETRY_REASONS = {
    "runner_crash", "dependency_failure", "machine_interruption",
    "corrupted_artifact", "deterministic_serialization_bug", "unavailable_infrastructure",
}
FORBIDDEN_RETRY_REASONS = {
    "low_macro_f1", "scope_fail", "act_recall_fail", "unknown_too_high",
    "bad_seed", "mixed_adversarial_fail", "score_driven_rerun",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def write_json(path: str | Path, value: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_jsonl(path: str | Path, records: Iterable[dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        for record in records:
            f.write(canonical_json(record) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()


def token_ngrams(text: str, n: int = 3) -> set[tuple[str, ...]]:
    toks = normalize_text(text).split()
    if len(toks) < n:
        return {tuple(toks)} if toks else set()
    return {tuple(toks[i:i+n]) for i in range(len(toks) - n + 1)}


def macro_f1(y_true: list[str], y_pred: list[str], labels: Iterable[str] = ACTIONS) -> float:
    scores: list[float] = []
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def distribution(values: Iterable[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items()))


def descriptive(values: list[float]) -> dict[str, float]:
    if not values:
        return {k: 0.0 for k in ("mean", "median", "minimum", "maximum", "standard_deviation")}
    return {
        "mean": mean(values),
        "median": median(values),
        "minimum": min(values),
        "maximum": max(values),
        "standard_deviation": pstdev(values) if len(values) > 1 else 0.0,
    }


def safe_rate(numerator: int | float, denominator: int | float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def stable_index(seed: int, key: str, modulo: int) -> int:
    digest = hashlib.sha256(f"{seed}:{key}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % modulo
