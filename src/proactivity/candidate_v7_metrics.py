from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

from proactivity.candidate_v7 import ACT_CRITICAL_FIELDS, FIELD_ORDER

ACTIONS = ("IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT")


def _safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else num / den


def classification_metrics(y_true: Sequence[Any], y_pred: Sequence[Any], labels: Sequence[Any]) -> dict[str, Any]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true/y_pred length mismatch")
    total = len(y_true)
    confusion = {str(t): {str(p): 0 for p in labels} for t in labels}
    invalid = 0
    for truth, pred in zip(y_true, y_pred):
        if pred not in labels:
            invalid += 1
            continue
        if truth in labels:
            confusion[str(truth)][str(pred)] += 1
    per_label: dict[str, dict[str, float | int]] = {}
    f1s: list[float] = []
    recalls: dict[str, float] = {}
    for label in labels:
        key = str(label)
        tp = confusion[key][key]
        fp = sum(confusion[str(other)][key] for other in labels if other != label)
        fn = sum(confusion[key][str(other)] for other in labels if other != label) + sum(
            1 for truth, pred in zip(y_true, y_pred) if truth == label and pred not in labels
        )
        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * precision * recall, precision + recall)
        per_label[key] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(1 for value in y_true if value == label)}
        recalls[key] = recall
        f1s.append(f1)
    correct = sum(1 for truth, pred in zip(y_true, y_pred) if truth == pred)
    pred_counts = Counter(str(pred) for pred in y_pred if pred in labels)
    shares = {str(label): _safe_div(pred_counts[str(label)], total) for label in labels}
    sorted_shares = sorted(shares.values(), reverse=True)
    return {
        "accuracy": _safe_div(correct, total),
        "macro_f1": _safe_div(sum(f1s), len(f1s)),
        "per_label": per_label,
        "per_action_recall": recalls,
        "confusion_matrix": confusion,
        "prediction_distribution": {str(label): pred_counts[str(label)] for label in labels},
        "prediction_share": shares,
        "zero_recall_actions": [str(label) for label in labels if recalls[str(label)] == 0.0],
        "invalid_action": invalid,
        "max_class_share": max(shares.values()) if shares else 0.0,
        "top_two_class_share": sum(sorted_shares[:2]),
        "n": total,
    }


def action_metrics(records: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    metrics = classification_metrics(
        [record["action"] for record in records],
        [prediction.get("action") for prediction in predictions],
        ACTIONS,
    )
    metrics["forbidden_act"] = sum(1 for prediction in predictions if prediction.get("forbidden_act"))
    return metrics


def latent_state_metrics(records: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    n = len(records)
    exact = 0
    per_factor: dict[str, dict[str, Any]] = {}
    all_correct = 0
    all_total = 0
    critical_correct = 0
    critical_total = 0
    unknown_total = 0
    critical_unknown_total = 0
    contradiction_records = 0
    for field in FIELD_ORDER:
        truth = [record["state"][field] for record in records]
        pred = [prediction["state"].get(field) for prediction in predictions]
        labels = []
        for value in truth:
            if value not in labels:
                labels.append(value)
        for value in pred:
            if value not in labels:
                labels.append(value)
        fm = classification_metrics(truth, pred, labels)
        per_factor[field] = {"accuracy": fm["accuracy"], "macro_f1": fm["macro_f1"], "n": fm["n"]}
        correct = sum(1 for t, p in zip(truth, pred) if t == p)
        all_correct += correct
        all_total += n
        if field in ACT_CRITICAL_FIELDS:
            critical_correct += correct
            critical_total += n
    for record, prediction in zip(records, predictions):
        if all(prediction["state"].get(field) == record["state"][field] for field in FIELD_ORDER):
            exact += 1
        unknown_total += len(prediction.get("unknown_fields", []))
        critical_unknown_total += len(prediction.get("critical_unknown_fields", []))
        contradiction_records += int(bool(prediction.get("contradictions")))
    mean_factor_macro_f1 = sum(per_factor[field]["macro_f1"] for field in FIELD_ORDER) / len(FIELD_ORDER)
    return {
        "exact_latent_state_reconstruction": _safe_div(exact, n),
        "mean_factor_accuracy": _safe_div(all_correct, all_total),
        "mean_factor_macro_f1": mean_factor_macro_f1,
        "per_factor": per_factor,
        "act_critical_factor_accuracy": _safe_div(critical_correct, critical_total),
        "unknown_rate": _safe_div(unknown_total, n * len(FIELD_ORDER)),
        "critical_unknown_rate": _safe_div(critical_unknown_total, n * len(ACT_CRITICAL_FIELDS)),
        "contradiction_rate": _safe_div(contradiction_records, n),
        "n": n,
    }


def semantic_operator_metrics(records: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    polarity_correct = polarity_total = 0
    modality_correct = modality_total = 0
    temporal_correct = temporal_total = 0
    attribution_correct = attribution_total = 0
    scope_correct = scope_total = 0
    for record, prediction in zip(records, predictions):
        predicted_props = prediction.get("propositions", [])
        by_field_value: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
        for prop in predicted_props:
            if prop.get("field") is None:
                continue
            key = (str(prop.get("field")), repr(prop.get("value")))
            by_field_value.setdefault(key, []).append(prop)
        for gold in record.get("propositions", []):
            field = gold.get("field")
            value = gold.get("value")
            if field is None:
                continue
            attribution_total += 1
            candidates = by_field_value.get((str(field), repr(value)), [])
            if candidates:
                attribution_correct += 1
                best = candidates[0]
                polarity_total += 1
                modality_total += 1
                temporal_total += 1
                scope_total += 1
                polarity_correct += int(best.get("polarity") == gold.get("polarity"))
                modality_correct += int(best.get("modality") == gold.get("modality"))
                temporal_correct += int(best.get("temporality") == gold.get("temporality"))
                scope_correct += int(best.get("scope") == gold.get("scope"))
            else:
                polarity_total += 1
                modality_total += 1
                temporal_total += 1
                scope_total += 1
    return {
        "proposition_polarity_accuracy": _safe_div(polarity_correct, polarity_total),
        "modal_interpretation_accuracy": _safe_div(modality_correct, modality_total),
        "temporal_interpretation_accuracy": _safe_div(temporal_correct, temporal_total),
        "negation_scope_accuracy": _safe_div(scope_correct, scope_total),
        "factor_evidence_attribution_accuracy": _safe_div(attribution_correct, attribution_total),
        "gold_propositions": attribution_total,
    }


def evaluate_metrics(records: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "action": action_metrics(records, predictions),
        "latent": latent_state_metrics(records, predictions),
        "semantic": semantic_operator_metrics(records, predictions),
    }


def counterfactual_pair_metrics(records: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[tuple[Mapping[str, Any], Mapping[str, Any]]]] = {}
    for record, prediction in zip(records, predictions):
        groups.setdefault(str(record["pair_id"]), []).append((record, prediction))
    exact = action_transition = factor_transition = critical_consistency = 0
    valid_pairs = 0
    for pairs in groups.values():
        if len(pairs) != 2:
            continue
        pairs = sorted(pairs, key=lambda item: str(item[0].get("pair_member")))
        valid_pairs += 1
        both_state = all(all(pred["state"].get(field) == rec["state"][field] for field in FIELD_ORDER) for rec, pred in pairs)
        both_action = all(pred.get("action") == rec.get("action") for rec, pred in pairs)
        exact += int(both_state and both_action)
        true_action_changed = pairs[0][0]["action"] != pairs[1][0]["action"]
        pred_action_changed = pairs[0][1].get("action") != pairs[1][1].get("action")
        action_transition += int(true_action_changed == pred_action_changed and both_action)
        true_changed = {field for field in FIELD_ORDER if pairs[0][0]["state"][field] != pairs[1][0]["state"][field]}
        pred_changed = {field for field in FIELD_ORDER if pairs[0][1]["state"].get(field) != pairs[1][1]["state"].get(field)}
        factor_transition += int(true_changed == pred_changed and both_state)
        critical_consistency += int((true_changed & ACT_CRITICAL_FIELDS) == (pred_changed & ACT_CRITICAL_FIELDS) and both_state)
    return {
        "exact_pair": _safe_div(exact, valid_pairs),
        "action_transition_correctness": _safe_div(action_transition, valid_pairs),
        "factor_transition_correctness": _safe_div(factor_transition, valid_pairs),
        "critical_factor_consistency": _safe_div(critical_consistency, valid_pairs),
        "pairs": valid_pairs,
    }


def invariance_pair_metrics(records: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[tuple[Mapping[str, Any], Mapping[str, Any]]]] = {}
    for record, prediction in zip(records, predictions):
        groups.setdefault(str(record["pair_id"]), []).append((record, prediction))
    action_consistent = state_consistent = exact = 0
    valid_pairs = 0
    for pairs in groups.values():
        if len(pairs) != 2:
            continue
        valid_pairs += 1
        first, second = pairs
        ac = first[1].get("action") == second[1].get("action")
        sc = all(first[1]["state"].get(field) == second[1]["state"].get(field) for field in FIELD_ORDER)
        gold_correct = all(
            pred["state"].get(field) == rec["state"][field]
            for rec, pred in pairs for field in FIELD_ORDER
        ) and all(pred.get("action") == rec.get("action") for rec, pred in pairs)
        action_consistent += int(ac)
        state_consistent += int(sc)
        exact += int(ac and sc and gold_correct)
    return {
        "action_consistency": _safe_div(action_consistent, valid_pairs),
        "latent_state_consistency": _safe_div(state_consistent, valid_pairs),
        "exact_pair": _safe_div(exact, valid_pairs),
        "pairs": valid_pairs,
    }
