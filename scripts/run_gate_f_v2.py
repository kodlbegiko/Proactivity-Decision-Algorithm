from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import f1_score

from proactivity.baselines_v2 import make_baseline
from proactivity.candidate_v2 import ACTIONS, make_candidate
from proactivity.gate_d_v2 import _metrics
from proactivity.gate_e_v2 import _load_gate_e_dataset

CANDIDATE = "C5_semantic_factor_linear"
BASELINE = "B5_transparent_heuristic"
BOOTSTRAP_SAMPLES = 10_000
BOOTSTRAP_SEED = 2026081501
MIN_MACRO_F1 = 0.50
MIN_DELTA = 0.20

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_SOURCE = ROOT / "src" / "proactivity" / "candidate_v2.py"
GENERATOR_SOURCE = ROOT / "scripts" / "generate_gate_f_v2.py"
GENERATOR_MANIFEST = ROOT / "gate_f" / "generator_manifest_v2.json"
PROTECTED_INPUTS = ROOT / "gate_f" / "protected_inputs_v2.jsonl"
PROTECTED_LABELS = ROOT / "gate_f" / "protected_labels_v2.jsonl"
PROTECTED_PRIVATE = ROOT / "gate_f" / "protected_private_v2.jsonl"
PRE_SCORE_HASHES = ROOT / "gate_f" / "hash_manifest_pre_scoring_v2.json"
GENERATION_SUMMARY = ROOT / "gate_f" / "generation_summary_v2.json"
PREREGISTRATION = ROOT / "preregistration" / "gate_f_v2.md"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_pre_score_hashes() -> dict[str, Any]:
    manifest = json.loads(PRE_SCORE_HASHES.read_text(encoding="utf-8"))
    paths = {
        "candidate_source_sha256": CANDIDATE_SOURCE,
        "generator_source_sha256": GENERATOR_SOURCE,
        "generator_manifest_sha256": GENERATOR_MANIFEST,
        "protected_inputs_sha256": PROTECTED_INPUTS,
        "protected_labels_sha256": PROTECTED_LABELS,
        "protected_private_sha256": PROTECTED_PRIVATE,
        "generation_summary_sha256": GENERATION_SUMMARY,
        "preregistration_sha256": PREREGISTRATION,
        "scorer_source_sha256": Path(__file__),
    }
    checks = {}
    for field, path in paths.items():
        actual = sha256_file(path)
        expected = manifest[field]
        checks[field] = {"expected": expected, "actual": actual, "match": actual == expected}
    if not all(item["match"] for item in checks.values()):
        raise RuntimeError(f"pre-scoring hash verification failed: {checks}")
    return {"manifest": manifest, "checks": checks}


def load_protected():
    inputs = jsonl(PROTECTED_INPUTS)
    labels = jsonl(PROTECTED_LABELS)
    private = jsonl(PROTECTED_PRIVATE)
    input_by_id = {row["scenario_id"]: row for row in inputs}
    label_by_id = {row["scenario_id"]: row for row in labels}
    private_by_id = {row["scenario_id"]: row for row in private}
    ids = sorted(input_by_id)
    if set(ids) != set(label_by_id) or set(ids) != set(private_by_id):
        raise RuntimeError("protected artifact scenario-id sets differ")
    if len(ids) != 120 or len(ids) != len(set(ids)):
        raise RuntimeError(f"unexpected protected set size: {len(ids)}")
    records = [{"domain": input_by_id[sid]["domain"], "observation": input_by_id[sid]["observation"]} for sid in ids]
    gold = [label_by_id[sid]["expected_action"] for sid in ids]
    evaluator_rows = [private_by_id[sid] for sid in ids]
    return ids, records, gold, evaluator_rows


def canonical_predict(model, ids, records) -> list[str]:
    paired = sorted(zip(ids, records), key=lambda item: item[0])
    sorted_ids = [sid for sid, _ in paired]
    sorted_records = [record for _, record in paired]
    pred = model.predict(sorted_records)
    pred_map = dict(zip(sorted_ids, [str(value) for value in pred]))
    return [pred_map[sid] for sid in ids]


def paired_bootstrap(labels, candidate_predictions, baseline_predictions) -> dict[str, Any]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    labels_arr = np.asarray(labels)
    cand_arr = np.asarray(candidate_predictions)
    base_arr = np.asarray(baseline_predictions)
    n = len(labels)
    deltas = np.empty(BOOTSTRAP_SAMPLES, dtype=float)
    for i in range(BOOTSTRAP_SAMPLES):
        index = rng.integers(0, n, size=n)
        y = labels_arr[index]
        cand = cand_arr[index]
        base = base_arr[index]
        deltas[i] = (
            f1_score(y, cand, labels=list(ACTIONS), average="macro", zero_division=0)
            - f1_score(y, base, labels=list(ACTIONS), average="macro", zero_division=0)
        )
    q = np.quantile(deltas, [0.025, 0.5, 0.975])
    return {
        "samples": BOOTSTRAP_SAMPLES,
        "seed": BOOTSTRAP_SEED,
        "delta_mean": float(deltas.mean()),
        "delta_p2_5": float(q[0]),
        "delta_p50": float(q[1]),
        "delta_p97_5": float(q[2]),
        "fraction_delta_gt_zero": float(np.mean(deltas > 0)),
    }


def pair_diagnostics(ids, gold, predictions, evaluator_rows) -> dict[str, Any]:
    by_id = {sid: {"gold": g, "prediction": p, "private": row} for sid, g, p, row in zip(ids, gold, predictions, evaluator_rows)}
    groups: dict[str, list[str]] = defaultdict(list)
    for sid, row in zip(ids, evaluator_rows):
        pid = row.get("counterfactual_pair_id")
        if pid:
            groups[str(pid)].append(sid)
    details = []
    exact = 0
    for pid in sorted(groups):
        members = sorted(groups[pid])
        if len(members) != 2:
            raise RuntimeError(f"counterfactual pair {pid} does not have exactly two members")
        is_exact = all(by_id[sid]["gold"] == by_id[sid]["prediction"] for sid in members)
        exact += int(is_exact)
        details.append({
            "pair_id": pid,
            "field": by_id[members[0]]["private"].get("counterfactual_field"),
            "scenario_ids": members,
            "gold": [by_id[sid]["gold"] for sid in members],
            "predictions": [by_id[sid]["prediction"] for sid in members],
            "exact": is_exact,
        })
    return {
        "pair_count": len(details),
        "exact_pair_count": exact,
        "exact_pair_rate": float(exact / len(details)) if details else None,
        "details": details,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")


def run(benchmark_root: Path, output_dir: Path) -> dict[str, Any]:
    hash_verification = verify_pre_score_hashes()

    _, _, subset, isolation = _load_gate_e_dataset(benchmark_root)
    dev_ids, dev_records, dev_labels = subset("development")
    if isolation["protected_candidate_rows_json_parsed"] != 0 or isolation["protected_private_rows_json_parsed"] != 0:
        raise RuntimeError("Gate-C public protected payload isolation regression")

    ids, protected_records, gold, evaluator_rows = load_protected()
    action_counts = {action: gold.count(action) for action in ACTIONS}
    if any(action_counts[action] != 20 for action in ACTIONS):
        raise RuntimeError(f"protected action balance mismatch: {action_counts}")

    candidate = make_candidate(CANDIDATE).fit(dev_records, dev_labels)
    baseline = make_baseline(BASELINE).fit(dev_records, dev_labels)

    candidate_predictions = canonical_predict(candidate, ids, protected_records)
    baseline_predictions = canonical_predict(baseline, ids, protected_records)

    candidate_metrics = _metrics(gold, candidate_predictions, evaluator_rows)
    baseline_metrics = _metrics(gold, baseline_predictions, evaluator_rows)
    candidate_invalid = sum(pred not in ACTIONS for pred in candidate_predictions)
    baseline_invalid = sum(pred not in ACTIONS for pred in baseline_predictions)
    candidate_metrics["invalid_action_count"] = int(candidate_invalid)
    candidate_metrics["invalid_action_rate"] = float(candidate_invalid / len(ids))
    baseline_metrics["invalid_action_count"] = int(baseline_invalid)
    baseline_metrics["invalid_action_rate"] = float(baseline_invalid / len(ids))
    candidate_metrics["all_six_nonzero_recall"] = all(
        candidate_metrics["per_action"][action]["support"] > 0
        and candidate_metrics["per_action"][action]["recall"] > 0
        for action in ACTIONS
    )

    delta = candidate_metrics["macro_f1"] - baseline_metrics["macro_f1"]
    bootstrap = paired_bootstrap(gold, candidate_predictions, baseline_predictions)
    pairs = pair_diagnostics(ids, gold, candidate_predictions, evaluator_rows)

    criteria = {
        "macro_f1_at_least_0_50": candidate_metrics["macro_f1"] >= MIN_MACRO_F1,
        "delta_vs_b5_at_least_0_20": delta >= MIN_DELTA,
        "bootstrap_lower_bound_positive": bootstrap["delta_p2_5"] > 0,
        "valid_action_rate_100pct": candidate_metrics["valid_action_rate"] == 1.0,
        "invalid_action_count_zero": candidate_metrics["invalid_action_count"] == 0,
        "forbidden_act_zero": candidate_metrics["forbidden_act_count"] == 0,
        "all_six_nonzero_recall": candidate_metrics["all_six_nonzero_recall"],
        "protected_hashes_match": all(item["match"] for item in hash_verification["checks"].values()),
        "candidate_source_hash_match": hash_verification["checks"]["candidate_source_sha256"]["match"],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    candidate_rows = [{"scenario_id": sid, "action": action} for sid, action in zip(ids, candidate_predictions)]
    baseline_rows = [{"scenario_id": sid, "action": action} for sid, action in zip(ids, baseline_predictions)]
    write_jsonl(output_dir / "predictions_v2.jsonl", candidate_rows)
    write_jsonl(output_dir / "baseline_predictions_v2.jsonl", baseline_rows)
    (output_dir / "bootstrap_v2.json").write_text(json.dumps(bootstrap, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "protocol": "PDA Protocol v2",
        "gate": "F",
        "formal_scoring_occurred": True,
        "candidate": CANDIDATE,
        "baseline": BASELINE,
        "protected_set_size": len(ids),
        "protected_action_counts": action_counts,
        "independence_classification": "LEVEL C — process-isolated candidate-blind generator; not external/human-independent",
        "candidate_metrics": candidate_metrics,
        "baseline_metrics": baseline_metrics,
        "macro_f1_delta_vs_b5": float(delta),
        "paired_bootstrap": bootstrap,
        "counterfactual_pair_diagnostics": pairs,
        "pre_score_hash_verification": hash_verification,
        "criteria": criteria,
        "decision": "PASS" if all(criteria.values()) else "FAIL",
        "claim_boundary": "Confirmatory evidence is limited to the frozen process-isolated protected/OOD distribution; no human-preference, real-world, deployment-safety, or universal-generalization claim.",
    }
    (output_dir / "report_v2.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    marker = {
        "GATE_F_FORMAL_SCORING_OCCURRED": True,
        "decision": report["decision"],
        "candidate": CANDIDATE,
        "protected_set_size": len(ids),
    }
    (output_dir / "formal_scoring_marker_v2.json").write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.benchmark_root, args.output_dir)
    print(json.dumps({"decision": report["decision"], "macro_f1": report["candidate_metrics"]["macro_f1"], "delta": report["macro_f1_delta_vs_b5"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
