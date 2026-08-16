from __future__ import annotations

from collections import Counter
from typing import Any

from .protocol import ACTIONS, CRITICAL_FACTORS, FACTORS


def _safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def classification_metrics(gold: list[str], pred: list[str]) -> dict[str, Any]:
    per = {}
    f1s = []
    for cls in ACTIONS:
        tp = sum(g == cls and p == cls for g, p in zip(gold, pred))
        fp = sum(g != cls and p == cls for g, p in zip(gold, pred))
        fn = sum(g == cls and p != cls for g, p in zip(gold, pred))
        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * precision * recall, precision + recall)
        per[cls] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(g == cls for g in gold)}
        f1s.append(f1)
    dist = Counter(pred)
    return {
        "accuracy": _safe_div(sum(g == p for g, p in zip(gold, pred)), len(gold)),
        "macro_f1": sum(f1s) / len(f1s),
        "per_class": per,
        "predicted_action_distribution": {a: dist.get(a, 0) for a in ACTIONS},
        "max_action_share": _safe_div(max(dist.values(), default=0), len(pred)),
    }


def state_metrics(gold_states: list[dict], pred_states: list[dict]) -> dict[str, Any]:
    per_factor = {f: _safe_div(sum(g.get(f) == p.get(f) for g, p in zip(gold_states, pred_states)), len(gold_states)) for f in FACTORS}
    exact = _safe_div(sum(all(g.get(f) == p.get(f) for f in FACTORS) for g, p in zip(gold_states, pred_states)), len(gold_states))
    return {
        "exact_structured_state_accuracy": exact,
        "mean_factor_accuracy": sum(per_factor.values()) / len(per_factor),
        "critical_factor_accuracy": sum(per_factor[f] for f in CRITICAL_FACTORS) / len(CRITICAL_FACTORS),
        "per_factor_accuracy": per_factor,
    }


def act_metrics(gold: list[str], pred: list[str]) -> dict[str, Any]:
    tp = sum(g == "ACT" and p == "ACT" for g, p in zip(gold, pred))
    fp = sum(g != "ACT" and p == "ACT" for g, p in zip(gold, pred))
    fn = sum(g == "ACT" and p != "ACT" for g, p in zip(gold, pred))
    return {
        "act_precision": _safe_div(tp, tp + fp) if tp + fp else 1.0,
        "act_recall": _safe_div(tp, tp + fn),
        "false_act": fp,
        "forbidden_act": fp,
    }
