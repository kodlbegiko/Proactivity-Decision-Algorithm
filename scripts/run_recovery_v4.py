#!/usr/bin/env python3
"""Run the preregistered Candidate-v4 development recovery search/qualification."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import sklearn
from sklearn.metrics import accuracy_score, f1_score, recall_score

from proactivity.candidate_v4 import ACTIONS, CANDIDATE_CONFIGURATIONS, FIELDS, make_candidate
from proactivity.recovery_v4_data import (
    build_counterfactual_pairs,
    build_invariance_pairs,
    build_splits,
    candidate_view,
    factor_supervision,
    generation_manifest,
    sha256_json,
)

PREREGISTRATION_COMMIT = "c1942470cfea1fe3678e5143da0c1ba8f9ed1aa4"
RECOVERY_BASE_COMMIT = "0fd05b6ac9e3f451ed710f2f37ee845dedad1df7"
QUALIFICATION_SPLITS = ("validation", "ood", "lexical_holdout", "rendering_holdout", "compositional_holdout")
THRESHOLDS = {
    "validation": 0.85,
    "ood": 0.75,
    "lexical_holdout": 0.70,
    "rendering_holdout": 0.75,
    "compositional_holdout": 0.70,
}
PARSER_THRESHOLDS = {
    "validation": 0.90,
    "ood": 0.85,
    "lexical_holdout": 0.85,
    "rendering_holdout": 0.85,
    "compositional_holdout": 0.85,
}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _split_metrics(candidate, records: list[dict]) -> dict[str, object]:
    views = [candidate_view(record) for record in records]
    expected = [str(record["expected_action"]) for record in records]
    predicted = candidate.predict(views)
    recalls = recall_score(expected, predicted, labels=list(ACTIONS), average=None, zero_division=0)
    distribution = Counter(predicted)
    factor_correct = 0
    factor_total = 0
    unknown = 0
    for view, record in zip(views, records):
        parsed = candidate.parse_record(view)
        state = record["state"]
        for field in FIELDS:
            factor_total += 1
            factor_correct += int(parsed.state.get(field) == state[field])
            unknown += int(parsed.state.get(field) == "unknown")
    invalid = sum(item not in ACTIONS for item in predicted)
    forbidden_act = sum(pred == "ACT" and truth != "ACT" for pred, truth in zip(predicted, expected))
    max_share = max(distribution.values(), default=0) / max(len(predicted), 1)
    return {
        "n": len(records),
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(f1_score(expected, predicted, labels=list(ACTIONS), average="macro", zero_division=0)),
        "per_class_recall": {action: float(value) for action, value in zip(ACTIONS, recalls)},
        "prediction_distribution": {action: int(distribution.get(action, 0)) for action in ACTIONS},
        "max_prediction_class_share": float(max_share),
        "invalid_action": int(invalid),
        "forbidden_act": int(forbidden_act),
        "parser_exact_factor_accuracy": float(factor_correct / factor_total),
        "parser_unknown_factor_rate": float(unknown / factor_total),
        "collapse": bool(max_share > 0.60 or any(value == 0.0 for value in recalls)),
    }


def _counterfactual_metrics(candidate) -> dict[str, object]:
    pairs = build_counterfactual_pairs()
    exact = 0
    forbidden_act = 0
    rows = []
    for pair in pairs:
        before = pair["before"]
        after = pair["after"]
        before_pred = candidate.predict([candidate_view(before)])[0]
        after_pred = candidate.predict([candidate_view(after)])[0]
        before_ok = before_pred == before["expected_action"]
        after_ok = after_pred == after["expected_action"]
        exact += int(before_ok and after_ok)
        forbidden_act += int(after_pred == "ACT")
        rows.append({
            "mutation": pair["mutation"],
            "before_expected": before["expected_action"],
            "before_predicted": before_pred,
            "after_expected": after["expected_action"],
            "after_predicted": after_pred,
        })
    return {
        "pairs": len(pairs),
        "exact_pair_rate": float(exact / len(pairs)),
        "forbidden_act": int(forbidden_act),
        "rows_sha256": sha256_json(rows),
    }


def _invariance_metrics(candidate) -> dict[str, object]:
    pairs = build_invariance_pairs()
    consistent = 0
    exact_both = 0
    rows = []
    for pair in pairs:
        left = pair["left"]
        right = pair["right"]
        left_pred = candidate.predict([candidate_view(left)])[0]
        right_pred = candidate.predict([candidate_view(right)])[0]
        consistent += int(left_pred == right_pred)
        exact_both += int(left_pred == left["expected_action"] and right_pred == right["expected_action"])
        rows.append({
            "expected": left["expected_action"],
            "left": left_pred,
            "right": right_pred,
            "left_family": left["rendering_family"],
            "right_family": right["rendering_family"],
        })
    return {
        "pairs": len(pairs),
        "prediction_consistency": float(consistent / len(pairs)),
        "exact_both_rate": float(exact_both / len(pairs)),
        "rows_sha256": sha256_json(rows),
    }


def _passes_preregistration(evaluation: dict[str, object]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    split_metrics = evaluation["splits"]
    for split in QUALIFICATION_SPLITS:
        metrics = split_metrics[split]
        if metrics["macro_f1"] < THRESHOLDS[split]:
            failures.append(f"{split}.macro_f1<{THRESHOLDS[split]}")
        if metrics["parser_exact_factor_accuracy"] < PARSER_THRESHOLDS[split]:
            failures.append(f"{split}.parser_exact_factor_accuracy<{PARSER_THRESHOLDS[split]}")
        if metrics["forbidden_act"] != 0:
            failures.append(f"{split}.forbidden_act!=0")
        if metrics["invalid_action"] != 0:
            failures.append(f"{split}.invalid_action!=0")
        if metrics["max_prediction_class_share"] > 0.60:
            failures.append(f"{split}.max_prediction_class_share>0.60")
        if metrics["collapse"]:
            failures.append(f"{split}.collapse")
        if any(value <= 0.0 for value in metrics["per_class_recall"].values()):
            failures.append(f"{split}.zero_class_recall")
    if evaluation["counterfactual"]["exact_pair_rate"] < 0.80:
        failures.append("counterfactual.exact_pair_rate<0.80")
    if evaluation["counterfactual"]["forbidden_act"] != 0:
        failures.append("counterfactual.forbidden_act!=0")
    if evaluation["invariance"]["prediction_consistency"] < 0.95:
        failures.append("invariance.prediction_consistency<0.95")
    return (not failures, failures)


def _simplicity_rank(name: str) -> int:
    if name.startswith("V4B_"):
        return 3
    if name.startswith("V4A_"):
        return 2
    return 1


def run() -> dict[str, object]:
    manifest_a = generation_manifest()
    manifest_b = generation_manifest()
    deterministic_regeneration = manifest_a == manifest_b
    splits = build_splits()
    supervision = factor_supervision()
    training = splits["train"]
    training_views = [candidate_view(record) for record in training]
    training_labels = [str(record["expected_action"]) for record in training]

    candidate_results: dict[str, object] = {}
    for name in CANDIDATE_CONFIGURATIONS:
        candidate = make_candidate(name)
        candidate.fit(training_views, training_labels, factor_supervision=supervision)
        evaluation: dict[str, object] = {
            "splits": {split: _split_metrics(candidate, splits[split]) for split in QUALIFICATION_SPLITS},
            "counterfactual": _counterfactual_metrics(candidate),
            "invariance": _invariance_metrics(candidate),
        }
        passed, failures = _passes_preregistration(evaluation)
        evaluation["passes_preregistration"] = passed
        evaluation["failures"] = failures
        evaluation["minimum_holdout_macro_f1"] = min(evaluation["splits"][split]["macro_f1"] for split in QUALIFICATION_SPLITS)
        evaluation["minimum_parser_factor_accuracy"] = min(evaluation["splits"][split]["parser_exact_factor_accuracy"] for split in QUALIFICATION_SPLITS)
        candidate_results[name] = evaluation

    eligible = [name for name, result in candidate_results.items() if result["passes_preregistration"]]
    eligible.sort(
        key=lambda name: (
            candidate_results[name]["minimum_holdout_macro_f1"],
            candidate_results[name]["counterfactual"]["exact_pair_rate"],
            candidate_results[name]["minimum_parser_factor_accuracy"],
            _simplicity_rank(name),
            name,
        ),
        reverse=True,
    )
    selected = eligible[0] if eligible else None
    terminal = "RECOVERY DEVELOPMENT PASS — CANDIDATE V4 FROZEN" if selected else "RECOVERY DEVELOPMENT FAIL — NO CANDIDATE V4 FROZEN"

    root = Path(__file__).resolve().parents[1]
    result = {
        "schema_version": 1,
        "mission": "Candidate-v4 Independent Generalization Recovery",
        "base_commit": RECOVERY_BASE_COMMIT,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "seed": 20260815,
        "historical_gate_f": "FAIL",
        "candidate_v3_lineage": "TERMINATED",
        "candidate_v3_confirmatory_records_accessed": 0,
        "gate_g": "NOT EXECUTED",
        "gate_h": "NOT EXECUTED",
        "python": sys.version.split()[0],
        "scikit_learn": sklearn.__version__,
        "deterministic_regeneration": deterministic_regeneration,
        "generation_manifest": manifest_a,
        "source_sha256": {
            "candidate_v4.py": _sha256_file(root / "src" / "proactivity" / "candidate_v4.py"),
            "recovery_v4_data.py": _sha256_file(root / "src" / "proactivity" / "recovery_v4_data.py"),
            "run_recovery_v4.py": _sha256_file(Path(__file__).resolve()),
        },
        "candidate_results": candidate_results,
        "eligible_candidates": eligible,
        "selected_candidate": selected,
        "terminal_state": terminal,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="results/candidate_v4_recovery")
    parser.add_argument("--assert-pass", action="store_true")
    args = parser.parse_args()
    result = run()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    (output_dir / "development_results.json").write_text(payload, encoding="utf-8")
    summary = [
        "# Candidate-v4 Development Recovery Result",
        "",
        f"Terminal state: **{result['terminal_state']}**",
        "",
        f"Selected candidate: `{result['selected_candidate']}`",
        "",
        "This is development qualification only. Gate G and Gate H remain NOT EXECUTED.",
        "",
    ]
    if result["selected_candidate"]:
        selected = result["candidate_results"][result["selected_candidate"]]
        summary.append("## Selected metrics")
        summary.append("")
        for split in QUALIFICATION_SPLITS:
            metrics = selected["splits"][split]
            summary.append(f"- {split}: macro-F1={metrics['macro_f1']:.6f}, parser-factor-accuracy={metrics['parser_exact_factor_accuracy']:.6f}, forbidden-ACT={metrics['forbidden_act']}")
        summary.append(f"- counterfactual exact-pair={selected['counterfactual']['exact_pair_rate']:.6f}")
        summary.append(f"- invariance consistency={selected['invariance']['prediction_consistency']:.6f}")
    (output_dir / "development_report.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(payload)
    if args.assert_pass and result["terminal_state"] != "RECOVERY DEVELOPMENT PASS — CANDIDATE V4 FROZEN":
        return 1
    if not result["deterministic_regeneration"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
