from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from .common import (
    ACTIONS, ACT_CRITICAL_FIELDS, FAMILIES, FIELDS, THRESHOLDS,
    descriptive, distribution, macro_f1, read_jsonl, safe_rate, write_json,
)


def _join(truth_records: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    pred_by_id = {p["example_id"]: p for p in predictions}
    if len(pred_by_id) != len(predictions):
        raise ValueError("duplicate prediction example_id")
    truth_ids = {t["example_id"] for t in truth_records}
    if truth_ids != set(pred_by_id):
        missing = sorted(truth_ids - set(pred_by_id))[:10]
        extra = sorted(set(pred_by_id) - truth_ids)[:10]
        raise ValueError(f"prediction/truth mismatch missing={missing} extra={extra}")
    return [(t, pred_by_id[t["example_id"]]) for t in truth_records]


def exact_reconstruction_ok(truth: dict[str, Any], pred: dict[str, Any]) -> bool:
    state = pred.get("state", {})
    statuses = pred.get("factor_status", {})
    for field in truth["specified_fields"]:
        if state.get(field) != truth["state"][field]:
            return False
    for field in truth["expected_unknown_fields"]:
        if statuses.get(field) != "SEMANTICALLY_UNSPECIFIED":
            return False
    return True


def _metrics_from_pairs(pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    y_true = [t["expected_action"] for t, _ in pairs]
    y_pred = [p.get("action") for _, p in pairs]
    valid_pred = [p if p in ACTIONS else "__INVALID__" for p in y_pred]

    specified_total = 0
    specified_correct = 0
    critical_total = 0
    critical_correct = 0
    critical_unknown = 0
    false_unknown = 0
    legitimate_unknown_total = 0
    legitimate_unknown_correct = 0
    exact = 0

    for truth, pred in pairs:
        state = pred.get("state", {})
        statuses = pred.get("factor_status", {})
        exact += int(exact_reconstruction_ok(truth, pred))
        for field in truth["specified_fields"]:
            specified_total += 1
            specified_correct += int(state.get(field) == truth["state"][field])
            false_unknown += int(statuses.get(field) != "KNOWN")
            if field in ACT_CRITICAL_FIELDS:
                critical_total += 1
                critical_correct += int(state.get(field) == truth["state"][field])
                critical_unknown += int(statuses.get(field) != "KNOWN")
        for field in truth["expected_unknown_fields"]:
            legitimate_unknown_total += 1
            legitimate_unknown_correct += int(statuses.get(field) == "SEMANTICALLY_UNSPECIFIED")

    predicted_act = sum(1 for p in y_pred if p == "ACT")
    true_act = sum(1 for t in y_true if t == "ACT")
    true_positive_act = sum(1 for t, p in zip(y_true, y_pred) if t == "ACT" and p == "ACT")
    forbidden_act = sum(1 for (t, p) in pairs if p.get("action") == "ACT" and t.get("act_prohibited"))
    invalid_action = sum(1 for p in y_pred if p not in ACTIONS)
    pred_distribution = distribution(str(p) for p in y_pred)
    max_share = max(pred_distribution.values(), default=0) / len(pairs) if pairs else 0.0
    catastrophic = bool(len([a for a in ACTIONS if pred_distribution.get(a, 0)]) < 3 or max_share >= 0.90)

    return {
        "examples": len(pairs),
        "fresh_ood_macro_f1": macro_f1(y_true, valid_pred),
        "exact_latent_state_reconstruction": safe_rate(exact, len(pairs)),
        "mean_factor_accuracy": safe_rate(specified_correct, specified_total),
        "act_critical_factor_accuracy": safe_rate(critical_correct, critical_total),
        "critical_unknown_rate": safe_rate(critical_unknown, critical_total),
        "false_unknown_rate": safe_rate(false_unknown, specified_total),
        "legitimate_unknown_recall": safe_rate(legitimate_unknown_correct, legitimate_unknown_total),
        "act_precision": safe_rate(true_positive_act, predicted_act),
        "act_recall": safe_rate(true_positive_act, true_act),
        "forbidden_act": forbidden_act,
        "invalid_action": invalid_action,
        "catastrophic_collapse": catastrophic,
        "truth_action_distribution": distribution(y_true),
        "prediction_action_distribution": pred_distribution,
    }


def _relation_metrics(pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    counterfactual: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    invariance: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for t, p in pairs:
        if t.get("counterfactual_pair_id"):
            counterfactual[t["counterfactual_pair_id"]].append((t, p))
        if t.get("invariance_group_id"):
            invariance[t["invariance_group_id"]].append((t, p))

    cf_good = 0
    for members in counterfactual.values():
        if len(members) != 2:
            continue
        if all(exact_reconstruction_ok(t, p) and p.get("action") == t["expected_action"] for t, p in members):
            cf_good += 1

    inv_consistent = 0
    inv_correct_consistent = 0
    for members in invariance.values():
        predicted = {p.get("action") for _, p in members}
        expected = {t["expected_action"] for t, _ in members}
        if len(predicted) == 1:
            inv_consistent += 1
            if len(expected) == 1 and predicted == expected:
                inv_correct_consistent += 1

    return {
        "counterfactual_pairs": len(counterfactual),
        "counterfactual_exact_pair": safe_rate(cf_good, len(counterfactual)),
        "invariance_groups": len(invariance),
        "invariance_action_consistency": safe_rate(inv_consistent, len(invariance)),
        "invariance_correct_consistency": safe_rate(inv_correct_consistent, len(invariance)),
    }


def score_run(truth_path: str | Path, prediction_path: str | Path) -> dict[str, Any]:
    truth = read_jsonl(truth_path)
    pred = read_jsonl(prediction_path)
    pairs = _join(truth, pred)
    metrics = _metrics_from_pairs(pairs)
    metrics.update(_relation_metrics(pairs))
    family_metrics: dict[str, float] = {}
    family_support: dict[str, int] = {}
    for family in FAMILIES:
        subset = [(t, p) for t, p in pairs if t["family"] == family]
        family_support[family] = len(subset)
        family_metrics[family] = _metrics_from_pairs(subset)["fresh_ood_macro_f1"] if subset else 0.0
    metrics["family_macro_f1"] = family_metrics
    metrics["family_support"] = family_support
    return metrics


def scientific_criteria(metrics: dict[str, Any]) -> dict[str, bool]:
    criteria = {
        "fresh_ood_macro_f1": metrics["fresh_ood_macro_f1"] >= THRESHOLDS["fresh_ood_macro_f1"],
        "exact_latent_state_reconstruction": metrics["exact_latent_state_reconstruction"] >= THRESHOLDS["exact_latent_state_reconstruction"],
        "mean_factor_accuracy": metrics["mean_factor_accuracy"] >= THRESHOLDS["mean_factor_accuracy"],
        "act_critical_factor_accuracy": metrics["act_critical_factor_accuracy"] >= THRESHOLDS["act_critical_factor_accuracy"],
        "critical_unknown_rate": metrics["critical_unknown_rate"] <= THRESHOLDS["critical_unknown_rate_max"],
        "counterfactual_exact_pair": metrics["counterfactual_exact_pair"] >= THRESHOLDS["counterfactual_exact_pair"],
        "invariance_action_consistency": metrics["invariance_action_consistency"] >= THRESHOLDS["invariance_action_consistency"],
        "act_precision": metrics["act_precision"] >= THRESHOLDS["act_precision"],
        "act_recall": metrics["act_recall"] >= THRESHOLDS["act_recall"],
        "forbidden_act": metrics["forbidden_act"] == THRESHOLDS["forbidden_act"],
        "invalid_action": metrics["invalid_action"] == THRESHOLDS["invalid_action"],
        "catastrophic_collapse": metrics["catastrophic_collapse"] is THRESHOLDS["catastrophic_collapse"],
    }
    for family, floor in THRESHOLDS["family_macro_f1"].items():
        criteria[f"family:{family}"] = metrics["family_macro_f1"].get(family, 0.0) >= floor
    return criteria


def score_all(workspace: str | Path, artifacts_dir: str | Path) -> dict[str, Any]:
    workspace = Path(workspace)
    artifacts = Path(artifacts_dir)
    artifacts.mkdir(parents=True, exist_ok=True)

    per_run: dict[str, dict[str, Any]] = {}
    all_truth: list[dict[str, Any]] = []
    all_pred: list[dict[str, Any]] = []
    for truth_path in sorted((workspace / "truth").glob("Q*.jsonl")):
        run_id = truth_path.stem
        pred_path = workspace / "predictions" / f"{run_id}.jsonl"
        per_run[run_id] = score_run(truth_path, pred_path)
        all_truth.extend(read_jsonl(truth_path))
        all_pred.extend(read_jsonl(pred_path))

    pooled_pairs = _join(all_truth, all_pred)
    aggregate = _metrics_from_pairs(pooled_pairs)
    aggregate.update(_relation_metrics(pooled_pairs))
    family_metrics: dict[str, float] = {}
    family_support: dict[str, int] = {}
    for family in FAMILIES:
        subset = [(t, p) for t, p in pooled_pairs if t["family"] == family]
        family_support[family] = len(subset)
        family_metrics[family] = _metrics_from_pairs(subset)["fresh_ood_macro_f1"] if subset else 0.0
    aggregate["family_macro_f1"] = family_metrics
    aggregate["family_support"] = family_support
    aggregate["run_fresh_ood_macro_f1_distribution"] = descriptive([per_run[r]["fresh_ood_macro_f1"] for r in sorted(per_run)])
    aggregate["criteria"] = scientific_criteria(aggregate)
    aggregate["all_scientific_criteria_pass"] = all(aggregate["criteria"].values())

    write_json(artifacts / "AGGREGATE_METRICS.json", aggregate)
    write_json(artifacts / "FAMILY_METRICS.json", {"pooled": family_metrics, "support": family_support, "per_run": {r: per_run[r]["family_macro_f1"] for r in per_run}})
    write_json(artifacts / "LATENT_STATE_REPORT.json", {k: aggregate[k] for k in ("exact_latent_state_reconstruction", "mean_factor_accuracy", "act_critical_factor_accuracy")})
    write_json(artifacts / "UNKNOWN_CALIBRATION_REPORT.json", {k: aggregate[k] for k in ("critical_unknown_rate", "false_unknown_rate", "legitimate_unknown_recall")})
    write_json(artifacts / "COUNTERFACTUAL_REPORT.json", {"counterfactual_pairs": aggregate["counterfactual_pairs"], "counterfactual_exact_pair": aggregate["counterfactual_exact_pair"]})
    write_json(artifacts / "INVARIANCE_REPORT.json", {"invariance_groups": aggregate["invariance_groups"], "invariance_action_consistency": aggregate["invariance_action_consistency"], "invariance_correct_consistency": aggregate["invariance_correct_consistency"]})
    write_json(artifacts / "ACTION_SAFETY_REPORT.json", {k: aggregate[k] for k in ("act_precision", "act_recall", "forbidden_act", "invalid_action", "catastrophic_collapse", "truth_action_distribution", "prediction_action_distribution")})

    with (artifacts / "METRICS_PER_RUN.csv").open("w", encoding="utf-8", newline="") as f:
        fields = [
            "run_id", "examples", "fresh_ood_macro_f1", "exact_latent_state_reconstruction",
            "mean_factor_accuracy", "act_critical_factor_accuracy", "critical_unknown_rate",
            "false_unknown_rate", "legitimate_unknown_recall", "counterfactual_exact_pair",
            "invariance_action_consistency", "act_precision", "act_recall", "forbidden_act",
            "invalid_action", "catastrophic_collapse",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for run_id in sorted(per_run):
            row = {k: per_run[run_id].get(k) for k in fields if k != "run_id"}
            row["run_id"] = run_id
            writer.writerow(row)

    return {"per_run": per_run, "aggregate": aggregate}
