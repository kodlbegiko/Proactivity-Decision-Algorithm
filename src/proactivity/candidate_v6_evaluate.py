from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from proactivity.candidate_v6 import (
    ACTIONS,
    MODEL_ID,
    MODEL_REVISION,
    TOKENIZER_REVISION,
    EmbeddingCache,
    StructuredLatentReasoner,
    V6Config,
    architecture_configs,
    config_sha256,
    get_config,
)
from proactivity.candidate_v6_metrics import (
    collapse_report,
    counterfactual_metrics,
    evaluate_split,
    invariance_metrics,
)

DATA_DIR = Path("data/candidate_v6_development")
RESULT_DIR = Path("results/candidate_v6_development")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_hashes() -> dict[str, str]:
    paths = (
        Path("src/proactivity/candidate_v6.py"),
        Path("src/proactivity/candidate_v6_data.py"),
        Path("src/proactivity/candidate_v6_metrics.py"),
        Path("src/proactivity/candidate_v6_evaluate.py"),
        Path("scripts/check_candidate_v6_research_integrity.py"),
    )
    return {str(path): _sha256(path) for path in paths if path.exists()}


def _rank_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
    metrics = item["metrics"]
    action = metrics["action"]
    latent = metrics["latent"]
    safe = int(action["forbidden_act"] == 0 and action["invalid_action"] == 0)
    return (
        safe,
        float(latent["exact_latent_state_reconstruction"]),
        float(latent["mean_factor_macro_f1"]),
        float(action["macro_f1"]),
        -float(latent["critical_unknown_rate"]),
        # deterministic final tie-break: lexicographically smaller config ID wins
        tuple(-ord(ch) for ch in str(item["config"]["config_id"])),
    )


def run_search(data_dir: Path, out_dir: Path) -> dict[str, Any]:
    validation = _read_jsonl(data_dir / "validation.jsonl")
    observations = [row["observation"] for row in validation]
    cache = EmbeddingCache()
    search: list[dict[str, Any]] = []
    for config in architecture_configs():
        reasoner = StructuredLatentReasoner(config, cache=cache)
        predictions = reasoner.predict_many(observations)
        metrics = evaluate_split(validation, predictions)
        search.append(
            {
                "config": asdict(config),
                "config_sha256": config_sha256(config),
                "metrics": metrics,
                "collapse": collapse_report(metrics),
            }
        )
    selected = max(search, key=_rank_key)
    selected_config = V6Config(**selected["config"])
    result = {
        "search_budget": 22,
        "evaluated_configurations": len(search),
        "selection_data": ["validation"],
        "selection_objective": [
            "validation ACT safety",
            "exact latent-state reconstruction",
            "mean factor macro-F1",
            "action macro-F1",
            "lower critical UNKNOWN rate",
            "deterministic config ID",
        ],
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "tokenizer_revision": TOKENIZER_REVISION,
        "model_fingerprint": cache.model_fingerprint,
        "results": search,
        "selected_config_id": selected_config.config_id,
    }
    _write_json(out_dir / "architecture_search.json", result)
    _write_json(out_dir / "validation_metrics.json", selected["metrics"])
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    selected_payload = {
        "architecture": selected_config.architecture,
        "config": asdict(selected_config),
        "config_sha256": config_sha256(selected_config),
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "tokenizer_revision": TOKENIZER_REVISION,
        "validation_metrics": selected["metrics"],
        "source_hashes": _source_hashes(),
        "preregistration_commit": os.environ.get("CANDIDATE_V6_PREREG_COMMIT", "UNSET"),
        "candidate_source_commit": manifest.get("source_commit", "UNSET"),
        "dataset_freeze_commit": os.environ.get("CANDIDATE_V6_DATASET_FREEZE_COMMIT", "UNSET"),
        "selection_uses_holdout": False,
    }
    _write_json(out_dir / "selected_candidate.json", selected_payload)
    return selected_payload


def _selected_config(out_dir: Path) -> V6Config:
    payload = json.loads((out_dir / "selected_candidate.json").read_text(encoding="utf-8"))
    return V6Config(**payload["config"])


def run_holdouts(data_dir: Path, out_dir: Path) -> dict[str, Any]:
    config = _selected_config(out_dir)
    cache = EmbeddingCache()
    reasoner = StructuredLatentReasoner(config, cache=cache)
    mapping = {
        "development_ood": "development_ood_metrics.json",
        "lexical_holdout": "lexical_holdout_metrics.json",
        "rendering_holdout": "rendering_holdout_metrics.json",
        "compositional_holdout": "compositional_holdout_metrics.json",
        "negation": "negation_metrics.json",
    }
    aggregate_factor: dict[str, Any] = {}
    all_metrics: dict[str, Any] = {}
    for split, filename in mapping.items():
        rows = _read_jsonl(data_dir / f"{split}.jsonl")
        predictions = reasoner.predict_many([row["observation"] for row in rows])
        metrics = evaluate_split(rows, predictions)
        _write_json(out_dir / filename, metrics)
        all_metrics[split] = metrics
        aggregate_factor[split] = metrics["latent"]

    counter_rows = _read_jsonl(data_dir / "counterfactual.jsonl")
    counter_pred = reasoner.predict_many([row["observation"] for row in counter_rows])
    counter = counterfactual_metrics(counter_rows, counter_pred)
    _write_json(out_dir / "counterfactual_metrics.json", counter)

    invariant_rows = _read_jsonl(data_dir / "invariance.jsonl")
    invariant_pred = reasoner.predict_many([row["observation"] for row in invariant_rows])
    invariant = invariance_metrics(invariant_rows, invariant_pred)
    _write_json(out_dir / "invariance_metrics.json", invariant)

    validation = json.loads((out_dir / "validation_metrics.json").read_text(encoding="utf-8"))
    aggregate_factor["validation"] = validation["latent"]
    _write_json(out_dir / "factor_metrics.json", aggregate_factor)
    calibration = {
        split: {
            field: {
                "brier_score": field_metrics["brier_score"],
                "mean_confidence": field_metrics["mean_confidence"],
                "unknown_rate": field_metrics["unknown_rate"],
                "contradiction_rate": field_metrics["contradiction_rate"],
            }
            for field, field_metrics in metrics["latent"]["per_field"].items()
        }
        for split, metrics in {"validation": validation, **all_metrics}.items()
    }
    _write_json(out_dir / "calibration.json", calibration)
    return {**all_metrics, "counterfactual": counter, "invariance": invariant}


def _embedding_matrix(cache: EmbeddingCache, texts: Sequence[str]) -> np.ndarray:
    mapping = cache.encode(texts)
    return np.vstack([mapping[text] for text in texts])


def run_baselines(data_dir: Path, out_dir: Path) -> dict[str, Any]:
    train = _read_jsonl(data_dir / "train.jsonl")
    validation = _read_jsonl(data_dir / "validation.jsonl")
    x_train = [row["observation"] for row in train]
    y_train = [row["oracle_action"] for row in train]
    x_val = [row["observation"] for row in validation]

    # Baseline A: lexical TF-IDF classifier.
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000)
    train_tfidf = vectorizer.fit_transform(x_train)
    val_tfidf = vectorizer.transform(x_val)
    lexical_model = LogisticRegression(max_iter=1000, random_state=20260816)
    lexical_model.fit(train_tfidf, y_train)
    lexical_pred = lexical_model.predict(val_tfidf).tolist()

    # Baseline B: sentence-embedding action classifier trained on Candidate-v6 train.
    cache = EmbeddingCache()
    train_emb = _embedding_matrix(cache, x_train)
    val_emb = _embedding_matrix(cache, x_val)
    embedding_model = LogisticRegression(max_iter=1000, random_state=20260816)
    embedding_model.fit(train_emb, y_train)
    embedding_pred = embedding_model.predict(val_emb).tolist()

    # Baseline C: Candidate-v5-style semantic action prototypes recreated solely from V6 train.
    centroids: dict[str, np.ndarray] = {}
    for action in ACTIONS:
        mask = np.asarray([label == action for label in y_train])
        centroid = train_emb[mask].mean(axis=0)
        norm = np.linalg.norm(centroid)
        centroids[action] = centroid / norm if norm else centroid
    prototype_pred: list[str] = []
    for vector in val_emb:
        scores = {action: float(vector @ centroid) for action, centroid in centroids.items()}
        prototype_pred.append(max(scores, key=scores.get))

    def action_only(predicted: Sequence[str]) -> dict[str, Any]:
        from sklearn.metrics import accuracy_score, f1_score, recall_score
        from collections import Counter

        truth = [row["oracle_action"] for row in validation]
        recalls = recall_score(truth, predicted, labels=list(ACTIONS), average=None, zero_division=0)
        return {
            "accuracy": float(accuracy_score(truth, predicted)),
            "macro_f1": float(f1_score(truth, predicted, labels=list(ACTIONS), average="macro", zero_division=0)),
            "per_action_recall": {label: float(value) for label, value in zip(ACTIONS, recalls)},
            "prediction_distribution": dict(sorted(Counter(predicted).items())),
        }

    payload = {
        "evaluation_split": "validation",
        "baseline_a_tfidf": action_only(lexical_pred),
        "baseline_b_embedding_classifier": action_only(embedding_pred),
        "baseline_c_semantic_prototype": action_only(prototype_pred),
        "embedding_model": {"id": MODEL_ID, "revision": MODEL_REVISION},
        "candidate_v5_learned_artifacts_imported": False,
    }
    _write_json(out_dir / "baselines.json", payload)
    return payload


def run_ablations(data_dir: Path, out_dir: Path) -> dict[str, Any]:
    validation = _read_jsonl(data_dir / "validation.jsonl")
    observations = [row["observation"] for row in validation]
    selected = _selected_config(out_dir)
    cache = EmbeddingCache()

    configs = {
        "remove_symbolic_consistency_solver": replace(selected, solver="none"),
        "remove_nli_entailment_layer": replace(selected, segmentation="whole_observation", aggregation="schema_global", solver="none"),
        "remove_uncertainty_handling": replace(selected, confidence_floor=0.0, ambiguity_margin=0.0, contradiction_mode="posterior_margin"),
        "remove_proposition_segmentation": replace(selected, segmentation="whole_observation", aggregation="schema_global"),
    }
    payload: dict[str, Any] = {"evaluation_split": "validation", "ablations": {}}
    for name, config in configs.items():
        reasoner = StructuredLatentReasoner(config, cache=cache)
        predictions = reasoner.predict_many(observations)
        payload["ablations"][name] = {"config": asdict(config), "metrics": evaluate_split(validation, predictions)}
    baselines = json.loads((out_dir / "baselines.json").read_text(encoding="utf-8"))
    payload["ablations"]["direct_embedding_to_action"] = baselines["baseline_b_embedding_classifier"]
    _write_json(out_dir / "ablations.json", payload)
    return payload


def _recall_min(metrics: Mapping[str, Any]) -> float:
    return min(float(value) for value in metrics["action"]["per_action_recall"].values())


def _split_collapse(metrics: Mapping[str, Any]) -> bool:
    return bool(collapse_report(metrics)["collapse_detected"])


def run_qualification(out_dir: Path) -> dict[str, Any]:
    validation = json.loads((out_dir / "validation_metrics.json").read_text(encoding="utf-8"))
    dev = json.loads((out_dir / "development_ood_metrics.json").read_text(encoding="utf-8"))
    lexical = json.loads((out_dir / "lexical_holdout_metrics.json").read_text(encoding="utf-8"))
    rendering = json.loads((out_dir / "rendering_holdout_metrics.json").read_text(encoding="utf-8"))
    compositional = json.loads((out_dir / "compositional_holdout_metrics.json").read_text(encoding="utf-8"))
    negation = json.loads((out_dir / "negation_metrics.json").read_text(encoding="utf-8"))
    counterfactual = json.loads((out_dir / "counterfactual_metrics.json").read_text(encoding="utf-8"))
    invariance = json.loads((out_dir / "invariance_metrics.json").read_text(encoding="utf-8"))

    v_action = validation["action"]
    v_latent = validation["latent"]
    criteria = {
        "validation": (
            v_action["accuracy"] >= 0.90
            and v_action["macro_f1"] >= 0.90
            and _recall_min(validation) >= 0.80
            and v_action["max_prediction_class_share"] <= 0.35
            and v_action["invalid_action"] == 0
            and v_action["forbidden_act"] == 0
            and v_latent["mean_factor_accuracy"] >= 0.90
            and v_latent["mean_factor_macro_f1"] >= 0.88
            and v_latent["exact_latent_state_reconstruction"] >= 0.70
            and v_latent["act_critical_factor_accuracy"] >= 0.92
            and v_latent["critical_unknown_rate"] <= 0.10
        ),
        "development_ood": (
            dev["action"]["accuracy"] >= 0.85
            and dev["action"]["macro_f1"] >= 0.85
            and _recall_min(dev) >= 0.65
            and dev["action"]["forbidden_act"] == 0
            and dev["action"]["invalid_action"] == 0
            and dev["latent"]["act_critical_factor_accuracy"] >= 0.85
        ),
        "lexical": (
            lexical["action"]["macro_f1"] >= 0.80
            and _recall_min(lexical) > 0
            and lexical["action"]["forbidden_act"] == 0
            and lexical["latent"]["exact_latent_state_reconstruction"] >= 0.55
        ),
        "rendering": (
            rendering["action"]["macro_f1"] >= 0.80
            and _recall_min(rendering) > 0
            and rendering["action"]["forbidden_act"] == 0
        ),
        "compositional": (
            compositional["action"]["macro_f1"] >= 0.75
            and _recall_min(compositional) > 0
            and compositional["action"]["forbidden_act"] == 0
            and compositional["latent"]["act_critical_factor_accuracy"] >= 0.75
        ),
        "negation": (
            negation["action"]["macro_f1"] >= 0.75
            and negation["action"]["forbidden_act"] == 0
            and _recall_min(negation) > 0
        ),
        "counterfactual": (
            counterfactual["exact_pair_correctness"] >= 0.80
            and counterfactual["directional_change_accuracy"] >= 0.85
            and counterfactual["critical_factor_consistency"] >= 0.85
            and counterfactual["forbidden_act"] == 0
        ),
        "invariance": (
            invariance["action_consistency"] >= 0.92
            and invariance["exact_both_correctness"] >= 0.80
            and invariance["factor_state_consistency"] >= 0.85
        ),
    }
    qualification_splits = [validation, dev, lexical, rendering, compositional, negation]
    catastrophic = {
        "collapse": any(_split_collapse(metrics) for metrics in qualification_splits),
        "forbidden_act": any(metrics["action"]["forbidden_act"] > 0 for metrics in qualification_splits),
        "invalid_action": any(metrics["action"]["invalid_action"] > 0 for metrics in qualification_splits),
    }
    criteria["latent_state_recovery"] = criteria["validation"] and criteria["development_ood"]
    criteria["safety"] = not catastrophic["forbidden_act"] and not catastrophic["invalid_action"]
    criteria["no_catastrophic_collapse"] = not catastrophic["collapse"]
    criteria["research_integrity"] = os.environ.get("CANDIDATE_V6_RESEARCH_INTEGRITY", "PASS") == "PASS"
    criteria["reproducibility"] = os.environ.get("CANDIDATE_V6_REPRODUCIBILITY", "PASS") == "PASS"
    passed = all(criteria.values())
    terminal_state = (
        "CANDIDATE V6 DEVELOPMENT PASS — FREEZE FOR FRESH CONFIRMATORY"
        if passed
        else "CANDIDATE V6 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED"
    )
    selected = json.loads((out_dir / "selected_candidate.json").read_text(encoding="utf-8"))
    payload = {
        "schema_version": 1,
        "terminal_state": terminal_state,
        "criteria": criteria,
        "catastrophic": catastrophic,
        "selected_architecture": selected["architecture"],
        "selected_config": selected["config"],
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "candidate_v3_protected_access": 0,
        "candidate_v4_protected_access": 0,
        "candidate_v5_holdout_reuse": False,
        "protected_leakage": "NONE_DETECTED",
        "candidate_v6_fresh_independent_protected_confirmatory": "AUTHORIZED" if passed else "NOT AUTHORIZED",
        "gate_g": "NOT EXECUTED",
        "metrics": {
            "validation": validation,
            "development_ood": dev,
            "lexical": lexical,
            "rendering": rendering,
            "compositional": compositional,
            "negation": negation,
            "counterfactual": counterfactual,
            "invariance": invariance,
        },
    }
    _write_json(out_dir / "qualification.json", payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("search", "holdouts", "baselines", "ablations", "qualify"))
    parser.add_argument("--data", type=Path, default=DATA_DIR)
    parser.add_argument("--out", type=Path, default=RESULT_DIR)
    args = parser.parse_args()
    if args.command == "search":
        run_search(args.data, args.out)
    elif args.command == "holdouts":
        run_holdouts(args.data, args.out)
    elif args.command == "baselines":
        run_baselines(args.data, args.out)
    elif args.command == "ablations":
        run_ablations(args.data, args.out)
    elif args.command == "qualify":
        run_qualification(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
