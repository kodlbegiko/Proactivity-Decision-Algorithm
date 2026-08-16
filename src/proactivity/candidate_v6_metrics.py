from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, recall_score

from proactivity.candidate_v6 import ACTIONS, ACT_CRITICAL_FIELDS, FIELDS, CandidateV6Result

UNKNOWN_LABELS = {"UNKNOWN", "CONTRADICTORY", "AMBIGUOUS", None}


def _label(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def action_metrics(rows: Sequence[Mapping[str, Any]], predictions: Sequence[CandidateV6Result]) -> dict[str, Any]:
    truth = [str(row["oracle_action"]) for row in rows]
    pred = [str(result.action) if result.action is not None else "INVALID" for result in predictions]
    labels = list(ACTIONS)
    dist = Counter(pred)
    per_recall = recall_score(truth, pred, labels=labels, average=None, zero_division=0)
    matrix = confusion_matrix(truth, pred, labels=labels)
    invalid_action = sum(item not in ACTIONS for item in pred)
    forbidden_act = sum(p == "ACT" and y != "ACT" for y, p in zip(truth, pred))
    max_share = max(dist.values(), default=0) / max(1, len(pred))
    top_two_share = sum(sorted(dist.values(), reverse=True)[:2]) / max(1, len(pred))
    zero_recall = sum(float(value) == 0.0 for value in per_recall)
    return {
        "accuracy": float(accuracy_score(truth, pred)),
        "macro_f1": float(f1_score(truth, pred, labels=labels, average="macro", zero_division=0)),
        "per_action_recall": {label: float(value) for label, value in zip(labels, per_recall)},
        "prediction_distribution": dict(sorted(dist.items())),
        "confusion_matrix": {"labels": labels, "matrix": matrix.tolist()},
        "invalid_action": int(invalid_action),
        "forbidden_act": int(forbidden_act),
        "max_prediction_class_share": float(max_share),
        "top_two_prediction_class_share": float(top_two_share),
        "zero_recall_actions": int(zero_recall),
    }


def _multiclass_brier(true_label: str, probabilities: Mapping[str, float], labels: Sequence[str]) -> float:
    total = 0.0
    for label in labels:
        target = 1.0 if label == true_label else 0.0
        probability = float(probabilities.get(label, 0.0))
        total += (probability - target) ** 2
    return total / max(1, len(labels))


def factor_metrics(rows: Sequence[Mapping[str, Any]], predictions: Sequence[CandidateV6Result]) -> dict[str, Any]:
    per_field: dict[str, Any] = {}
    accuracies: list[float] = []
    macro_f1s: list[float] = []
    exact_count = 0
    critical_correct = 0
    critical_total = 0
    critical_unknown = 0

    for row, result in zip(rows, predictions):
        exact = True
        for field in FIELDS:
            expected = _label(row["latent_state"][field])
            predicted_raw = result.raw_state[field]
            if predicted_raw in UNKNOWN_LABELS or str(predicted_raw) in UNKNOWN_LABELS:
                predicted = "UNKNOWN"
            else:
                predicted = _label(predicted_raw)
            if predicted != expected:
                exact = False
            if field in ACT_CRITICAL_FIELDS:
                critical_total += 1
                if predicted == "UNKNOWN":
                    critical_unknown += 1
                if predicted == expected:
                    critical_correct += 1
        exact_count += int(exact)

    for field in FIELDS:
        truth = [_label(row["latent_state"][field]) for row in rows]
        pred: list[str] = []
        confidences: list[float] = []
        contradiction_count = 0
        unknown_count = 0
        briers: list[float] = []
        domain = sorted({_label(row["latent_state"][field]) for row in rows})
        labels = domain + ["UNKNOWN"]
        for row, result in zip(rows, predictions):
            inference = result.factors[field]
            raw = result.raw_state[field]
            predicted = "UNKNOWN" if raw in UNKNOWN_LABELS or str(raw) in UNKNOWN_LABELS else _label(raw)
            pred.append(predicted)
            confidences.append(float(inference.confidence))
            contradiction_count += int(inference.contradiction)
            unknown_count += int(predicted == "UNKNOWN")
            briers.append(_multiclass_brier(_label(row["latent_state"][field]), inference.probabilities, domain))
        acc = float(accuracy_score(truth, pred))
        mf1 = float(f1_score(truth, pred, labels=domain, average="macro", zero_division=0))
        matrix = confusion_matrix(truth, pred, labels=labels)
        accuracies.append(acc)
        macro_f1s.append(mf1)
        per_field[field] = {
            "accuracy": acc,
            "macro_f1": mf1,
            "confusion_matrix": {"labels": labels, "matrix": matrix.tolist()},
            "unknown_rate": unknown_count / max(1, len(rows)),
            "mean_confidence": float(np.mean(confidences)) if confidences else 0.0,
            "brier_score": float(np.mean(briers)) if briers else 0.0,
            "contradiction_rate": contradiction_count / max(1, len(rows)),
        }

    return {
        "per_field": per_field,
        "mean_factor_accuracy": float(np.mean(accuracies)) if accuracies else 0.0,
        "mean_factor_macro_f1": float(np.mean(macro_f1s)) if macro_f1s else 0.0,
        "exact_latent_state_reconstruction": exact_count / max(1, len(rows)),
        "act_critical_factor_accuracy": critical_correct / max(1, critical_total),
        "critical_unknown_rate": critical_unknown / max(1, critical_total),
    }


def evaluate_split(rows: Sequence[Mapping[str, Any]], predictions: Sequence[CandidateV6Result]) -> dict[str, Any]:
    return {
        "n": len(rows),
        "action": action_metrics(rows, predictions),
        "latent": factor_metrics(rows, predictions),
    }


def counterfactual_metrics(rows: Sequence[Mapping[str, Any]], predictions: Sequence[CandidateV6Result]) -> dict[str, Any]:
    by_pair: dict[str, list[tuple[Mapping[str, Any], CandidateV6Result]]] = defaultdict(list)
    for row, prediction in zip(rows, predictions):
        by_pair[str(row["pair_id"])].append((row, prediction))
    exact = 0
    directional = 0
    critical_consistent = 0
    forbidden_act = 0
    transition: dict[str, list[int]] = defaultdict(list)
    for pair_id, members in by_pair.items():
        if len(members) != 2:
            raise ValueError(f"counterfactual pair {pair_id} has {len(members)} members")
        members = sorted(members, key=lambda item: str(item[0]["pair_member"]))
        (left, lp), (right, rp) = members
        left_ok = lp.action == left["oracle_action"]
        right_ok = rp.action == right["oracle_action"]
        exact += int(left_ok and right_ok)
        expected_change = left["oracle_action"] != right["oracle_action"]
        predicted_change = lp.action != rp.action
        directional += int(expected_change == predicted_change)
        field = str(left["transition_field"])
        left_factor = lp.raw_state[field]
        right_factor = rp.raw_state[field]
        target_left = left["latent_state"][field]
        target_right = right["latent_state"][field]
        factor_ok = _label(left_factor) == _label(target_left) and _label(right_factor) == _label(target_right)
        critical_consistent += int(factor_ok)
        forbidden_act += int(lp.action == "ACT" and left["oracle_action"] != "ACT")
        forbidden_act += int(rp.action == "ACT" and right["oracle_action"] != "ACT")
        transition[field].append(int(left_ok and right_ok))
    n_pairs = max(1, len(by_pair))
    return {
        "pairs": len(by_pair),
        "exact_pair_correctness": exact / n_pairs,
        "directional_change_accuracy": directional / n_pairs,
        "critical_factor_consistency": critical_consistent / n_pairs,
        "forbidden_act": forbidden_act,
        "transition_specific_accuracy": {field: sum(values) / len(values) for field, values in sorted(transition.items())},
    }


def invariance_metrics(rows: Sequence[Mapping[str, Any]], predictions: Sequence[CandidateV6Result]) -> dict[str, Any]:
    by_pair: dict[str, list[tuple[Mapping[str, Any], CandidateV6Result]]] = defaultdict(list)
    for row, prediction in zip(rows, predictions):
        by_pair[str(row["pair_id"])].append((row, prediction))
    action_consistent = 0
    exact_both = 0
    factor_consistent = 0
    confidence_deltas: list[float] = []
    for pair_id, members in by_pair.items():
        if len(members) != 2:
            raise ValueError(f"invariance pair {pair_id} has {len(members)} members")
        members = sorted(members, key=lambda item: str(item[0]["pair_member"]))
        (left, lp), (right, rp) = members
        action_consistent += int(lp.action == rp.action)
        exact_both += int(lp.action == left["oracle_action"] and rp.action == right["oracle_action"])
        fields_equal = all(_label(lp.raw_state[field]) == _label(rp.raw_state[field]) for field in FIELDS)
        factor_consistent += int(fields_equal)
        left_conf = np.mean([lp.factors[field].confidence for field in FIELDS])
        right_conf = np.mean([rp.factors[field].confidence for field in FIELDS])
        confidence_deltas.append(abs(float(left_conf) - float(right_conf)))
    n_pairs = max(1, len(by_pair))
    return {
        "pairs": len(by_pair),
        "action_consistency": action_consistent / n_pairs,
        "exact_both_correctness": exact_both / n_pairs,
        "factor_state_consistency": factor_consistent / n_pairs,
        "mean_confidence_delta": float(np.mean(confidence_deltas)) if confidence_deltas else 0.0,
    }


def collapse_report(metrics: Mapping[str, Any]) -> dict[str, Any]:
    action = metrics["action"]
    catastrophic = {
        "single_class_share_ge_0_80": float(action["max_prediction_class_share"]) >= 0.80,
        "top_two_share_ge_0_92": float(action["top_two_prediction_class_share"]) >= 0.92,
        "three_or_more_zero_recall": int(action["zero_recall_actions"]) >= 3,
        "invalid_output_gt_zero": int(action["invalid_action"]) > 0,
    }
    return {"criteria": catastrophic, "collapse_detected": any(catastrophic.values())}
