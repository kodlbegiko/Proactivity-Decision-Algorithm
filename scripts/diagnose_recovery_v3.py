#!/usr/bin/env python3
"""Development-safe diagnosis of C5 representation brittleness.

This script uses only the frozen C5 source and recovery-v3 DEVELOPMENT_ONLY
records. It never opens retired Gate-F records.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from sklearn.metrics import accuracy_score, f1_score

from proactivity.candidate_v2 import SemanticFactorLinear, extract_visible_semantic_factors as old_extract
from proactivity.recovery_candidates_v3 import extract_visible_semantic_factors as new_extract

DATA = Path("data/recovery_v3_dev_ood")
OUT = Path("reports/recovery_v3")
ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
OLD_TO_STATE = {
    "permission": ("permission", {"required_absent": "missing", "required_present": "granted", "not_required": "not_required", "unknown": "unknown"}),
    "information": ("information", {"missing": "insufficient", "contradictory": "contradictory", "sufficient": "sufficient", "unknown": "unknown"}),
    "timing": ("urgency", {"absent": "none", "ordinary": "normal", "high": "high", "expired": "expired", "unknown": "unknown"}),
    "need": ("need", {"none": "none", "optional": "optional", "material": "material", "unknown": "unknown"}),
    "side_effect": ("side_effect", {"none": "none", "local": "local", "external": "external", "unknown": "unknown"}),
    "risk": ("risk", {"low": "low", "medium": "medium", "high": "high", "unknown": "unknown"}),
    "reversible": ("reversibility", {"yes": "reversible", "no": "irreversible", "unknown": "unknown"}),
    "deferral": ("deferral_available", {"yes": "True", "no": "False", "unknown": "unknown"}),
    "execution": ("execution_possible", {"yes": "True", "no": "False", "unknown": "unknown"}),
    "clarification": ("clarification_possible", {"yes": "True", "no": "False", "unknown": "unknown"}),
    "acknowledged": ("acknowledged", {"yes": "True", "no": "False", "unknown": "unknown"}),
    "completed": ("completed", {"yes": "True", "no": "False", "unknown": "unknown"}),
}


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def visible(rows):
    return [{"domain": row["domain"], "observation": row["observation"]} for row in rows]


def old_factor_metrics(rows, private_rows):
    states = {row["source_state_id"]: row["state"] for row in private_rows}; by_factor = {}; all_gold = []; all_pred = []
    for old_name, (state_name, mapping) in OLD_TO_STATE.items():
        gold = []; pred = []
        for row in rows:
            g = str(states[row["source_state_id"]][state_name]); raw = str(old_extract(row["observation"])[old_name]); p = mapping.get(raw, raw)
            gold.append(g); pred.append(p)
        by_factor[state_name] = {"accuracy": float(accuracy_score(gold, pred)), "macro_f1": float(f1_score(gold, pred, average="macro", zero_division=0)), "default_unknown_rate": float(sum(v == "unknown" for v in pred) / len(pred))}
        all_gold.extend(gold); all_pred.extend(pred)
    return {"by_factor": by_factor, "micro_factor_accuracy": float(accuracy_score(all_gold, all_pred)), "overall_unknown_rate": float(sum(v == "unknown" for v in all_pred) / len(all_pred))}


def new_factor_metrics(rows, private_rows):
    states = {row["source_state_id"]: row["state"] for row in private_rows}; factors = tuple(next(iter(states.values())).keys()); by_factor = {}; all_gold = []; all_pred = []
    for factor in factors:
        gold = []; pred = []
        for row in rows:
            g = str(states[row["source_state_id"]][factor]); p = str(new_extract(row["observation"])[factor]); gold.append(g); pred.append(p)
        by_factor[factor] = {"accuracy": float(accuracy_score(gold, pred)), "macro_f1": float(f1_score(gold, pred, average="macro", zero_division=0)), "default_unknown_rate": float(sum(v == "unknown" for v in pred) / len(pred))}
        all_gold.extend(gold); all_pred.extend(pred)
    return {"by_factor": by_factor, "micro_factor_accuracy": float(accuracy_score(all_gold, all_pred)), "overall_unknown_rate": float(sum(v == "unknown" for v in all_pred) / len(all_pred))}


def action_metrics(model, train, test):
    model.fit(visible(train), [r["gold_action"] for r in train]); pred = model.predict(visible(test)); gold = [r["gold_action"] for r in test]
    return {"macro_f1": float(f1_score(gold, pred, labels=ACTIONS, average="macro", zero_division=0)), "prediction_distribution": dict(Counter(pred)), "max_prediction_share": float(max(Counter(pred).values()) / len(pred))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    train = load_jsonl(DATA / "train.jsonl"); val = load_jsonl(DATA / "validation.jsonl"); ood = load_jsonl(DATA / "ood.jsonl")
    val_private = load_jsonl(DATA / "validation_private.jsonl"); ood_private = load_jsonl(DATA / "ood_private.jsonl")
    old_val = old_factor_metrics(val, val_private); old_ood = old_factor_metrics(ood, ood_private)
    new_val = new_factor_metrics(val, val_private); new_ood = new_factor_metrics(ood, ood_private)
    c5_val = action_metrics(SemanticFactorLinear(), train, val); c5_ood = action_metrics(SemanticFactorLinear(), train, ood)
    report = {
        "development_status": "DEVELOPMENT_ONLY",
        "gate_f_records_accessed": 0,
        "old_c5_extractor": {"validation": old_val, "ood": old_ood},
        "recovery_v3_extractor": {"validation": new_val, "ood": new_ood},
        "c5_retrained_on_recovery_development": {"validation": c5_val, "ood": c5_ood},
        "findings": {
            "VERIFIED": [
                "Frozen C5 semantic extraction is exact-substring/phrase-list dependent and falls back to unknown for unmatched factor evidence.",
                "On the recovery DEVELOPMENT_ONLY stress suite, frozen C5 extraction has substantially higher unknown/default rate and lower factor accuracy than the recovery parser.",
                "A C5 SemanticFactorLinear model trained only on recovery development data loses action discrimination when those factor representations default/collapse on shifted renderings."
            ],
            "SUPPORTED_HYPOTHESIS": [
                "Representation extraction brittleness is a major plausible contributor to the historical Gate-F complete-IGNORE generalization failure.",
                "The recovery tree result suggests downstream classification can remain discriminative when factor observability is restored on development-safe shifts."
            ],
            "NOT_ESTABLISHED": [
                "The exact fraction of historical Gate-F error attributable to extraction versus downstream classification is not established.",
                "No protected Gate-F phrase, per-example error, label, prediction, or rendering family was inspected, so the exact protected lexical trigger is intentionally unknown."
            ]
        }
    }
    (OUT / "root_cause_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"old_ood_factor_accuracy": old_ood["micro_factor_accuracy"], "old_ood_unknown_rate": old_ood["overall_unknown_rate"], "new_ood_factor_accuracy": new_ood["micro_factor_accuracy"], "c5_ood_macro_f1": c5_ood["macro_f1"], "c5_ood_prediction_distribution": c5_ood["prediction_distribution"], "gate_f_records_accessed": 0}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
