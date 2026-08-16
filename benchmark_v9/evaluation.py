from __future__ import annotations

from collections import Counter
from math import log
from typing import Any, Iterable

from candidate_v9.model import CRITICAL, predict
from candidate_v9.policy import ACTIONS, forbidden_act, valid_state


def _f1(tp: int, fp: int, fn: int) -> float:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def evaluate_rows(rows: Iterable[dict[str, Any]], architecture: str = "V9-C") -> dict[str, Any]:
    rows = list(rows)
    predictions = [predict(row["text"], architecture) for row in rows]
    y_true = [row["action"] for row in rows]
    y_pred = [prediction.action for prediction in predictions]
    n = len(rows)
    per_action_recall: dict[str, float] = {}
    per_action_precision: dict[str, float] = {}
    f1_values: list[float] = []
    for action in ACTIONS:
        tp = sum(t == action and p == action for t, p in zip(y_true, y_pred))
        fp = sum(t != action and p == action for t, p in zip(y_true, y_pred))
        fn = sum(t == action and p != action for t, p in zip(y_true, y_pred))
        per_action_recall[action] = tp / (tp + fn) if tp + fn else 0.0
        per_action_precision[action] = tp / (tp + fp) if tp + fp else 0.0
        f1_values.append(_f1(tp, fp, fn))

    dist = Counter(y_pred)
    act_tp = sum(t == "ACT" and p == "ACT" for t, p in zip(y_true, y_pred))
    act_fp = sum(t != "ACT" and p == "ACT" for t, p in zip(y_true, y_pred))
    act_fn = sum(t == "ACT" and p != "ACT" for t, p in zip(y_true, y_pred))
    critical_total = n * len(CRITICAL)
    critical_correct = sum(
        prediction.state[field] == row["state"][field]
        for prediction, row in zip(predictions, rows)
        for field in CRITICAL
    )
    exact = sum(prediction.state == row["state"] for prediction, row in zip(predictions, rows))
    invalid_predicted_states = sum(not valid_state(prediction.state) for prediction in predictions)
    forbidden = sum(
        pred == "ACT" and forbidden_act(row["state"])
        for pred, row in zip(y_pred, rows)
    )
    false_certainty = 0
    for prediction, row in zip(predictions, rows):
        should_be_uncertain = bool(row.get("uncertain_field") or row.get("contradicted_field"))
        if should_be_uncertain and prediction.certain:
            false_certainty += 1
    entropy = -sum((count / n) * log(count / n) for count in dist.values()) if n else 0.0
    return {
        "n": n,
        "accuracy": sum(t == p for t, p in zip(y_true, y_pred)) / n if n else 0.0,
        "macro_f1": sum(f1_values) / len(ACTIONS) if n else 0.0,
        "per_action_recall": per_action_recall,
        "per_action_precision": per_action_precision,
        "act_recall": act_tp / (act_tp + act_fn) if act_tp + act_fn else 0.0,
        "act_precision": act_tp / (act_tp + act_fp) if act_tp + act_fp else 0.0,
        "forbidden_act": forbidden,
        "false_act": act_fp,
        "critical_factor_accuracy": critical_correct / critical_total if critical_total else 0.0,
        "exact_state_accuracy": exact / n if n else 0.0,
        "normative_state_validity_rate": (n - invalid_predicted_states) / n if n else 1.0,
        "invalid_predicted_states": invalid_predicted_states,
        "false_certainty": false_certainty,
        "prediction_distribution": dict(dist),
        "max_prediction_share": max(dist.values()) / n if n else 0.0,
        "active_action_classes": sum(1 for action in ACTIONS if dist.get(action, 0) > 0),
        "act_prediction_share": dist.get("ACT", 0) / n if n else 0.0,
        "action_entropy": entropy,
    }


def evaluate_counterfactual_pairs(pairs: Iterable[dict[str, Any]], architecture: str = "V9-C") -> dict[str, Any]:
    pairs = list(pairs)
    exact = 0
    directional = 0
    act_disable = 0
    for pair in pairs:
        before = predict(pair["before_text"], architecture)
        after = predict(pair["after_text"], architecture)
        before_ok = before.action == pair["before_action"]
        after_ok = after.action == pair["after_action"]
        exact += int(before_ok and after_ok)
        directional += int(before.action == "ACT" and after.action != "ACT")
        act_disable += int(after.action != "ACT")
    n = len(pairs)
    return {
        "n_pairs": n,
        "exact_pair_accuracy": exact / n if n else 0.0,
        "directional_accuracy": directional / n if n else 0.0,
        "act_disable_accuracy": act_disable / n if n else 0.0,
    }


def evaluate_invariance_pairs(pairs: Iterable[dict[str, Any]], architecture: str = "V9-C") -> dict[str, Any]:
    pairs = list(pairs)
    consistent = 0
    both_correct = 0
    valid = 0
    for pair in pairs:
        a = predict(pair["text_a"], architecture)
        b = predict(pair["text_b"], architecture)
        consistent += int(a.action == b.action)
        both_correct += int(a.action == pair["action"] and b.action == pair["action"])
        valid += int(valid_state(a.state) and valid_state(b.state))
    n = len(pairs)
    return {
        "n_pairs": n,
        "prediction_consistency": consistent / n if n else 0.0,
        "both_correct": both_correct / n if n else 0.0,
        "state_validity_rate": valid / n if n else 1.0,
    }


def evaluate_contradiction(rows: Iterable[dict[str, Any]], architecture: str = "V9-C") -> dict[str, Any]:
    rows = list(rows)
    detected = 0
    false_certainty = 0
    invalid = 0
    for row in rows:
        prediction = predict(row["text"], architecture)
        field = row["contradicted_field"]
        detected += int(field in prediction.contradicted_fields)
        false_certainty += int(prediction.certain)
        invalid += int(not valid_state(prediction.state))
    n = len(rows)
    return {
        "n": n,
        "contradiction_detection": detected / n if n else 0.0,
        "false_certainty": false_certainty,
        "invalid_predicted_states": invalid,
        "state_validity_rate": (n - invalid) / n if n else 1.0,
    }


def evaluate_supersession(rows: Iterable[dict[str, Any]], architecture: str = "V9-C") -> dict[str, Any]:
    rows = list(rows)
    total = 0
    correct = 0
    invalid = 0
    for row in rows:
        prediction = predict(row["text"], architecture)
        invalid += int(not valid_state(prediction.state))
        for field in row["superseded_fields"]:
            total += 1
            correct += int(prediction.state[field] == row["state"][field])
    return {
        "n": len(rows),
        "factor_behavior": correct / total if total else 0.0,
        "invalid_predicted_states": invalid,
        "state_validity_rate": (len(rows) - invalid) / len(rows) if rows else 1.0,
    }


def evaluate_negation(rows: Iterable[dict[str, Any]], architecture: str = "V9-C") -> dict[str, Any]:
    rows = list(rows)
    total = len(rows) * len(CRITICAL)
    correct = 0
    invalid = 0
    for row in rows:
        prediction = predict(row["text"], architecture)
        invalid += int(not valid_state(prediction.state))
        for field in CRITICAL:
            correct += int(prediction.state[field] == row["state"][field])
    return {
        "n": len(rows),
        "factor_accuracy": correct / total if total else 0.0,
        "invalid_predicted_states": invalid,
        "state_validity_rate": (len(rows) - invalid) / len(rows) if rows else 1.0,
    }


def evaluate_joint_resolution(rows: Iterable[dict[str, Any]], architecture: str = "V9-C") -> dict[str, Any]:
    rows = list(rows)
    correct = 0
    invalid = 0
    forbidden = 0
    false_act = 0
    for row in rows:
        prediction = predict(row["text"], architecture)
        invalid += int(not valid_state(prediction.state))
        correct += int(
            prediction.state["permission"] == row["state"]["permission"]
            and prediction.state["side_effect"] == row["state"]["side_effect"]
        )
        forbidden += int(prediction.action == "ACT" and forbidden_act(row["state"]))
        false_act += int(prediction.action == "ACT" and row["action"] != "ACT")
    n = len(rows)
    return {
        "n": n,
        "joint_valid_state_resolution_accuracy": correct / n if n else 0.0,
        "invalid_predicted_states": invalid,
        "state_validity_rate": (n - invalid) / n if n else 1.0,
        "forbidden_act": forbidden,
        "false_act": false_act,
    }


def qualifies_validation(metrics: dict[str, Any], counterfactual: dict[str, Any]) -> bool:
    minimum_recall = {
        "IGNORE": 0.85,
        "WAIT": 0.85,
        "SUGGEST": 0.85,
        "NOTIFY": 0.85,
        "ASK": 0.90,
        "ACT": 0.85,
    }
    return (
        metrics["accuracy"] >= 0.92
        and metrics["macro_f1"] >= 0.92
        and all(metrics["per_action_recall"][action] >= threshold for action, threshold in minimum_recall.items())
        and metrics["act_precision"] >= 0.97
        and metrics["forbidden_act"] == 0
        and metrics["false_act"] == 0
        and metrics["critical_factor_accuracy"] >= 0.96
        and metrics["exact_state_accuracy"] >= 0.93
        and metrics["normative_state_validity_rate"] == 1.0
        and metrics["invalid_predicted_states"] == 0
        and counterfactual["directional_accuracy"] >= 0.97
        and counterfactual["act_disable_accuracy"] == 1.0
        and metrics["false_certainty"] == 0
        and metrics["max_prediction_share"] <= 0.35
        and metrics["active_action_classes"] >= 5
        and metrics["act_prediction_share"] > 0.0
    )
