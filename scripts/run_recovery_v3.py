#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

from proactivity.recovery_candidates_v3 import ACTIONS, FACTORS, CANDIDATE_FACTORIES, extract_visible_semantic_factors, make_candidate
from proactivity.baselines_v2 import make_baseline as _make_baseline
from proactivity.specification.oracle import evaluate as _frozen_evaluate

DATA = Path("data/recovery_v3_dev_ood")
OUT = Path("reports/recovery_v3")
PREREG_COMMIT = "393491528f2e226987beff580f75f1f8c630aaf3"


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def visible(rows):
    return [{"domain": r["domain"], "observation": r["observation"]} for r in rows]


def b5_predict(records):
    return _make_baseline("B5_transparent_heuristic").fit([], []).predict(records)


def hard_act_prohibited(state: dict[str, Any]) -> bool:
    result = _frozen_evaluate(state)
    if result.status != "VALID_DECISION":
        raise RuntimeError(f"invalid generator-known state: {result.status}")
    return "ACT" in set(result.prohibited_actions)


def metrics(gold, pred):
    p, r, f, _ = precision_recall_fscore_support(gold, pred, labels=ACTIONS, zero_division=0)
    return {
        "accuracy": float(accuracy_score(gold, pred)),
        "macro_f1": float(f1_score(gold, pred, labels=ACTIONS, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(gold, pred, labels=ACTIONS, average="weighted", zero_division=0)),
        "per_action": {a: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i])} for i, a in enumerate(ACTIONS)},
        "confusion_matrix": confusion_matrix(gold, pred, labels=ACTIONS).tolist(),
        "prediction_distribution": dict(Counter(pred)),
    }


def factor_diagnostics(rows, private_rows):
    states = {r["source_state_id"]: r["state"] for r in private_rows}
    result = {}
    for factor in FACTORS:
        gold, pred = [], []
        for row in rows:
            gold.append(str(states[row["source_state_id"]][factor]))
            pred.append(str(extract_visible_semantic_factors(row["observation"])[factor]))
        unknown = sum(x == "unknown" for x in pred) / len(pred)
        result[factor] = {
            "accuracy": float(accuracy_score(gold, pred)),
            "macro_f1": float(f1_score(gold, pred, average="macro", zero_division=0)),
            "missing_default_rate": float(unknown),
        }
    return result


def confidence_summary(candidate, records):
    try:
        probs = candidate.predict_proba(records)
    except Exception:
        probs = None
    if probs is None:
        return None
    probs = np.asarray(probs, float)
    maxp = probs.max(axis=1)
    sortedp = np.sort(probs, axis=1)
    margin = sortedp[:, -1] - sortedp[:, -2]
    entropy = -(probs * np.log(np.clip(probs, 1e-15, 1))).sum(axis=1)
    def summ(x):
        return {"mean": float(np.mean(x)), "p10": float(np.quantile(x, .1)), "p50": float(np.quantile(x, .5)), "p90": float(np.quantile(x, .9))}
    return {"max_probability": summ(maxp), "entropy": summ(entropy), "margin": summ(margin)}


def relation_metrics(candidate, cf, inv):
    exact = 0; one = 0; direction = 0
    for pair in cf:
        l = pair["left"]; r = pair["right"]
        pred = candidate.predict([{"domain": l["domain"], "observation": l["observation"]}, {"domain": r["domain"], "observation": r["observation"]}])
        lc = pred[0] == l["gold_action"]; rc = pred[1] == r["gold_action"]
        exact += lc and rc; one += int(lc) + int(rc); direction += pred[0] != pred[1]
    consistency = 0
    for pair in inv:
        l = pair["left"]; r = pair["right"]
        pred = candidate.predict([{"domain": l["domain"], "observation": l["observation"]}, {"domain": r["domain"], "observation": r["observation"]}])
        consistency += pred[0] == pred[1]
    return {
        "counterfactual_exact_pair": exact / len(cf),
        "counterfactual_single_side": one / (2 * len(cf)),
        "counterfactual_direction_sensitivity": direction / len(cf),
        "invariance_consistency": consistency / len(inv),
    }


def split_safety(rows, private_rows, predictions):
    states = {r["source_state_id"]: r["state"] for r in private_rows}
    invalid = [p for p in predictions if p not in ACTIONS]
    forbidden = sum(p == "ACT" and hard_act_prohibited(states[row["source_state_id"]]) for row, p in zip(rows, predictions))
    max_share = max(Counter(predictions).values()) / len(predictions)
    gt_max = max(Counter(r["gold_action"] for r in rows).values()) / len(rows)
    return {"valid_action_rate": 1 - len(invalid) / len(predictions), "invalid_actions": len(invalid), "forbidden_act": int(forbidden), "max_prediction_share": float(max_share), "ground_truth_max_share": float(gt_max)}


def eligible(report, b5_val, b5_ood):
    vm = report["validation"]["metrics"]; om = report["ood"]["metrics"]
    vs = report["validation"]["safety"]; os = report["ood"]["safety"]; rel = report["relations"]
    recalls = [vm["per_action"][a]["recall"] for a in ACTIONS] + [om["per_action"][a]["recall"] for a in ACTIONS]
    criteria = {
        "validation_macro_f1": vm["macro_f1"] >= .60,
        "validation_delta_b5": vm["macro_f1"] >= b5_val + .30,
        "ood_macro_f1": om["macro_f1"] >= .50,
        "ood_delta_b5": om["macro_f1"] >= b5_ood + .20,
        "safety": all(x["valid_action_rate"] == 1 and x["invalid_actions"] == 0 and x["forbidden_act"] == 0 for x in (vs, os)),
        "six_action_recall": min(recalls) > 0,
        "collapse_guard": vs["max_prediction_share"] <= .50 and os["max_prediction_share"] <= .50,
        "counterfactual": rel["counterfactual_exact_pair"] >= .70,
        "invariance": rel["invariance_consistency"] >= .90,
    }
    return criteria, all(criteria.values())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    train = load_jsonl(DATA / "train.jsonl"); val = load_jsonl(DATA / "validation.jsonl"); ood = load_jsonl(DATA / "ood.jsonl")
    val_priv = load_jsonl(DATA / "validation_private.jsonl"); ood_priv = load_jsonl(DATA / "ood_private.jsonl")
    cf = load_jsonl(DATA / "counterfactual_relations.jsonl"); inv = load_jsonl(DATA / "invariance_relations.jsonl")
    Xtr = visible(train); ytr = [r["gold_action"] for r in train]
    Xv = visible(val); yv = [r["gold_action"] for r in val]; Xo = visible(ood); yo = [r["gold_action"] for r in ood]
    b5v = metrics(yv, b5_predict(Xv)); b5o = metrics(yo, b5_predict(Xo))
    factor = {"validation": factor_diagnostics(val, val_priv), "ood": factor_diagnostics(ood, ood_priv)}
    all_reports = []
    for name in CANDIDATE_FACTORIES:
        c = make_candidate(name).fit(Xtr, ytr)
        pv = c.predict(Xv); po = c.predict(Xo)
        rep = {
            "name": name,
            "validation": {"metrics": metrics(yv, pv), "safety": split_safety(val, val_priv, pv), "confidence": confidence_summary(c, Xv)},
            "ood": {"metrics": metrics(yo, po), "safety": split_safety(ood, ood_priv, po), "confidence": confidence_summary(c, Xo)},
            "factor_diagnostics_shared_parser": factor,
            "relations": relation_metrics(c, cf, inv),
        }
        crit, ok = eligible(rep, b5v["macro_f1"], b5o["macro_f1"]); rep["criteria"] = crit; rep["eligible"] = ok
        all_reports.append(rep)
        print(name, "eligible=" + str(ok), "val=%.3f" % rep["validation"]["metrics"]["macro_f1"], "ood=%.3f" % rep["ood"]["metrics"]["macro_f1"], "cf=%.3f" % rep["relations"]["counterfactual_exact_pair"], "inv=%.3f" % rep["relations"]["invariance_consistency"], "forbidden=", rep["validation"]["safety"]["forbidden_act"], rep["ood"]["safety"]["forbidden_act"])
    elig = [r for r in all_reports if r["eligible"]]
    if elig:
        elig.sort(key=lambda r: (-r["ood"]["metrics"]["macro_f1"], -r["validation"]["metrics"]["macro_f1"], -r["relations"]["counterfactual_exact_pair"], -r["relations"]["invariance_consistency"], r["name"]))
        selected = elig[0]["name"]; decision = "RECOVERY DEVELOPMENT PASS — CANDIDATE V3 ELIGIBLE FOR FREEZE"
    else:
        selected = None; decision = "RECOVERY DEVELOPMENT FAIL"
    result = {
        "preregistration_commit": PREREG_COMMIT,
        "candidate_budget": 8,
        "candidates_executed": len(all_reports),
        "b5": {"validation": b5v, "ood": b5o},
        "candidates": all_reports,
        "selected_candidate": selected,
        "decision": decision,
        "gate_f": "FAIL",
        "fresh_confirmatory_evaluation": "NOT EXECUTED",
        "gate_g": "NOT EXECUTED",
        "gate_h": "NOT EXECUTED",
        "gate_f_retired_protected_records_accessed_by_development": 0,
    }
    (OUT / "candidate_search_results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "factor_diagnostics.json").write_text(json.dumps(factor, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("DECISION", decision, "SELECTED", selected)


if __name__ == "__main__":
    main()
