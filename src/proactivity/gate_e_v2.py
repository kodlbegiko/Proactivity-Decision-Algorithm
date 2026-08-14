"""Protocol v2 Gate-E candidate evaluator and preregistered selection logic."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

from .candidate_v2 import ACTIONS, CANDIDATE_FACTORIES, SEED, extract_visible_semantic_factors, make_candidate
from .gate_d_v2 import _metrics, _relation_diagnostics, scan_baseline_source, stable_json_bytes

FROZEN_BASELINE_NAME = "B5_transparent_heuristic"
FROZEN_BASELINE_MACRO_F1 = 0.21452991452991452
MIN_MACRO_DELTA = 0.05
BOOTSTRAP_SAMPLES = 10_000
_SCENARIO_ID = re.compile(r'"scenario_id"\s*:\s*"([^"]+)"')


def _scenario_id_without_parsing_payload(line: str) -> str:
    match = _SCENARIO_ID.search(line)
    if not match:
        raise ValueError("benchmark JSONL row has no scenario_id")
    return match.group(1)


def _load_gate_e_dataset(root: Path):
    split_rows = [json.loads(line) for line in (root / "splits.jsonl").read_text().splitlines() if line.strip()]
    split_by_id = {row["scenario_id"]: row["split"] for row in split_rows}
    allowed_ids = {sid for sid, split in split_by_id.items() if split in {"development", "validation"}}
    protected_ids = {sid for sid, split in split_by_id.items() if split == "protected_test"}

    candidate_by_id = {}
    skipped_candidate_protected = 0
    for line in (root / "candidate.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        sid = _scenario_id_without_parsing_payload(line)
        if sid in protected_ids:
            skipped_candidate_protected += 1
            continue
        if sid in allowed_ids:
            candidate_by_id[sid] = json.loads(line)

    evaluator_by_id = {}
    skipped_private_protected = 0
    for line in (root / "private.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        sid = _scenario_id_without_parsing_payload(line)
        if sid in protected_ids:
            skipped_private_protected += 1
            continue
        if sid in allowed_ids:
            evaluator_by_id[sid] = json.loads(line)

    if set(candidate_by_id) != allowed_ids or set(evaluator_by_id) != allowed_ids:
        raise ValueError("Gate-E development/validation row sets are incomplete")

    relations_all = json.loads((root / "relations.json").read_text())["relations"]
    relations = [relation for relation in relations_all if set(relation["scenario_ids"]).issubset(allowed_ids)]

    def subset(name: str):
        ids = sorted(sid for sid, split in split_by_id.items() if split == name)
        records = [{"domain": candidate_by_id[sid]["domain"], "observation": candidate_by_id[sid]["observation"]} for sid in ids]
        labels = [evaluator_by_id[sid]["oracle_action"] for sid in ids]
        return ids, records, labels

    isolation = {
        "protected_split_count": len(protected_ids),
        "protected_candidate_rows_json_parsed": 0,
        "protected_private_rows_json_parsed": 0,
        "protected_candidate_rows_skipped_by_id": skipped_candidate_protected,
        "protected_private_rows_skipped_by_id": skipped_private_protected,
    }
    return evaluator_by_id, relations, subset, isolation


def _canonical_predict(model, ids, records):
    paired = sorted(zip(ids, records), key=lambda pair: pair[0])
    ordered_ids = [pair[0] for pair in paired]
    ordered_records = [pair[1] for pair in paired]
    return dict(zip(ordered_ids, model.predict(ordered_records)))


def _evaluate(model, ids, records, labels, evaluator_by_id, relations):
    pred_map = _canonical_predict(model, ids, records)
    predictions = [pred_map[sid] for sid in ids]
    evaluator_rows = [evaluator_by_id[sid] for sid in ids]
    labels_by_id = dict(zip(ids, labels))
    metrics = _metrics(labels, predictions, evaluator_rows)
    metrics["counterfactual"] = _relation_diagnostics(ids, labels_by_id, pred_map, relations, {"counterfactual", "prohibition_counterfactual"})
    metrics["temporal"] = _relation_diagnostics(ids, labels_by_id, pred_map, relations, {"temporal"})
    metrics["predictions"] = [{"scenario_id": sid, "action": pred_map[sid]} for sid in ids]
    metrics["all_six_nonzero_recall"] = all(metrics["per_action"][action]["support"] > 0 and metrics["per_action"][action]["recall"] > 0 for action in ACTIONS)
    return metrics


def _bootstrap(labels, candidate_predictions, baseline_predictions):
    rng = np.random.default_rng(SEED)
    n = len(labels)
    deltas = np.empty(BOOTSTRAP_SAMPLES, dtype=float)
    labels_arr = np.asarray(labels)
    cand_arr = np.asarray(candidate_predictions)
    base_arr = np.asarray(baseline_predictions)
    for i in range(BOOTSTRAP_SAMPLES):
        index = rng.integers(0, n, size=n)
        y = labels_arr[index]
        cand = cand_arr[index]
        base = base_arr[index]
        cand_f1 = f1_score(y, cand, labels=list(ACTIONS), average="macro", zero_division=0)
        base_f1 = f1_score(y, base, labels=list(ACTIONS), average="macro", zero_division=0)
        deltas[i] = cand_f1 - base_f1
    q = np.quantile(deltas, [0.025, 0.5, 0.975])
    return {"samples": BOOTSTRAP_SAMPLES, "seed": SEED, "delta_mean": float(deltas.mean()), "delta_p2_5": float(q[0]), "delta_p50": float(q[1]), "delta_p97_5": float(q[2]), "fraction_delta_gt_zero": float(np.mean(deltas > 0))}


def _load_frozen_baseline(path: Path, validation_ids):
    rows = json.loads(path.read_text())
    pred_by_id = {row["scenario_id"]: row["action"] for row in rows}
    if set(pred_by_id) != set(validation_ids):
        raise ValueError("frozen Gate-D baseline prediction IDs do not match validation IDs")
    return [pred_by_id[sid] for sid in validation_ids]


def _source_sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_gate_e(benchmark_root: Path, candidate_source: Path, frozen_baseline_path: Path) -> dict:
    evaluator_by_id, relations, subset, isolation = _load_gate_e_dataset(benchmark_root)
    dev_ids, dev_records, dev_labels = subset("development")
    val_ids, val_records, val_labels = subset("validation")
    baseline_predictions = _load_frozen_baseline(frozen_baseline_path, val_ids)

    source_violations = scan_baseline_source(candidate_source.read_text())
    semantic_unknown = {key: 0 for key in ("permission", "information", "timing", "need", "side_effect", "risk", "reversible", "deferral", "execution", "clarification", "acknowledged", "completed")}
    for record in val_records:
        factors = extract_visible_semantic_factors(record["observation"])
        for key, value in factors.items():
            semantic_unknown[key] += int(value == "unknown")

    results = {}
    deterministic = {}
    eligibility = {}
    for name in CANDIDATE_FACTORIES:
        first_model = make_candidate(name).fit(dev_records, dev_labels)
        second_model = make_candidate(name).fit(dev_records, dev_labels)
        first = _evaluate(first_model, val_ids, val_records, val_labels, evaluator_by_id, relations)
        second = _evaluate(second_model, val_ids, val_records, val_labels, evaluator_by_id, relations)
        first_hash = hashlib.sha256(stable_json_bytes(first["predictions"])).hexdigest()
        second_hash = hashlib.sha256(stable_json_bytes(second["predictions"])).hexdigest()
        deterministic[name] = first_hash == second_hash
        first["prediction_sha256"] = first_hash
        results[name] = first
        eligibility[name] = first["valid_action_rate"] == 1.0 and len(source_violations) == 0 and first["forbidden_act_count"] == 0 and first["all_six_nonzero_recall"] and deterministic[name]

    eligible = [name for name in CANDIDATE_FACTORIES if eligibility[name]]
    selected = None
    if eligible:
        selected = sorted(eligible, key=lambda name: (-results[name]["macro_f1"], results[name]["forbidden_act_count"], -min(results[name]["per_action"][action]["recall"] for action in ACTIONS), list(CANDIDATE_FACTORIES).index(name)))[0]

    bootstrap = None
    selected_delta = None
    selected_pass = False
    if selected is not None:
        selected_pred = [row["action"] for row in results[selected]["predictions"]]
        selected_delta = results[selected]["macro_f1"] - FROZEN_BASELINE_MACRO_F1
        bootstrap = _bootstrap(val_labels, selected_pred, baseline_predictions)
        selected_pass = selected_delta >= MIN_MACRO_DELTA and results[selected]["valid_action_rate"] == 1.0 and results[selected]["forbidden_act_count"] == 0 and results[selected]["all_six_nonzero_recall"] and deterministic[selected] and len(source_violations) == 0

    return {
        "protocol": "PDA Protocol v2",
        "gate": "E",
        "seed": SEED,
        "search_budget": 6,
        "candidate_source_sha256": _source_sha(candidate_source),
        "candidate_source_boundary_violations": source_violations,
        "split_counts": {"development": len(dev_ids), "validation": len(val_ids)},
        "protected_test_isolation": isolation,
        "gate_f_protected_data": "NOT_GENERATED",
        "frozen_baseline": {"name": FROZEN_BASELINE_NAME, "macro_f1": FROZEN_BASELINE_MACRO_F1, "prediction_sha256": hashlib.sha256(stable_json_bytes([{"scenario_id": sid, "action": action} for sid, action in zip(val_ids, baseline_predictions)])).hexdigest()},
        "semantic_factor_unknown_counts_on_validation": semantic_unknown,
        "candidates": results,
        "deterministic_prediction_match": deterministic,
        "eligibility": eligibility,
        "selected_candidate": selected,
        "selected_macro_f1_delta_vs_b5": selected_delta,
        "paired_bootstrap": bootstrap,
        "criteria": {
            "exact_preregistered_search_budget": len(results) == 6,
            "candidate_source_boundary_violations_zero": len(source_violations) == 0,
            "protected_rows_not_parsed": isolation["protected_candidate_rows_json_parsed"] == 0 and isolation["protected_private_rows_json_parsed"] == 0,
            "selected_candidate_exists": selected is not None,
            "selected_macro_f1_delta_at_least_0_05": selected_delta is not None and selected_delta >= MIN_MACRO_DELTA,
            "paired_bootstrap_completed": bootstrap is not None and bootstrap["samples"] == BOOTSTRAP_SAMPLES,
            "selected_forbidden_act_zero": selected is not None and results[selected]["forbidden_act_count"] == 0,
            "selected_all_six_nonzero_recall": selected is not None and results[selected]["all_six_nonzero_recall"],
            "selected_deterministic": selected is not None and deterministic[selected],
            "selected_valid_action_rate_100pct": selected is not None and results[selected]["valid_action_rate"] == 1.0,
        },
        "gate_verdict": "GATE E — PASS" if selected_pass and isolation["protected_candidate_rows_json_parsed"] == 0 and isolation["protected_private_rows_json_parsed"] == 0 else "GATE E — FAIL",
    }
