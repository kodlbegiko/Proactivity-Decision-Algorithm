from __future__ import annotations

from collections import defaultdict
from typing import Any

from candidate_v11.model import CandidateArchitecture

from .hashes import sha256_obj
from .independent_generator import generate_suite
from .metrics import classification_metrics, state_metrics, act_metrics
from .protocol import ARCHITECTURE, FACTORS, SUITES
from .protocol_oracle import NormativeOracle


def _resolution_name(x: Any) -> str:
    return getattr(x, "value", str(x))


def evaluate_suite(suite: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    oracle = NormativeOracle()
    candidate = CandidateArchitecture(ARCHITECTURE)
    rows = generate_suite(suite, oracle)
    records: list[dict[str, Any]] = []
    prediction_fingerprint = []
    dataset_fingerprint = []

    for row in rows:
        case = row["case"]
        pred = candidate.predict(row["prompt"])
        pred_state = {f: pred.state.get(f) for f in FACTORS}
        belief_resolutions = {f: _resolution_name(pred.beliefs[f].resolution) if f in pred.beliefs else "absent" for f in FACTORS}
        record = {
            "case_id": case.case_id,
            "suite": suite,
            "gold_action": row["gold_action"],
            "pred_action": pred.action,
            "gold_state": case.state,
            "pred_state": pred_state,
            "pred_invalid": bool(pred.invalid),
            "pred_contradiction": bool(pred.contradiction),
            "belief_resolutions": belief_resolutions,
            "metadata": case.metadata,
        }
        records.append(record)
        dataset_fingerprint.append({"case": case.serializable(), "prompt": row["prompt"], "gold_action": row["gold_action"]})
        prediction_fingerprint.append({
            "case_id": case.case_id, "action": pred.action, "state": pred_state,
            "invalid": bool(pred.invalid), "contradiction": bool(pred.contradiction),
            "belief_resolutions": belief_resolutions,
        })

    gold = [r["gold_action"] for r in records]
    predicted = [r["pred_action"] for r in records]
    m = classification_metrics(gold, predicted)
    m.update(state_metrics([r["gold_state"] for r in records], [r["pred_state"] for r in records]))
    m.update(act_metrics(gold, predicted))
    invalid = sum(r["pred_invalid"] for r in records)
    m["invalid_states"] = invalid
    m["state_validity"] = 1.0 - (invalid / len(records) if records else 0.0)

    if suite == "G6":
        contrad = [r for r in records if r["metadata"].get("contradiction_expected")]
        controls = [r for r in records if not r["metadata"].get("contradiction_expected")]
        m["contradiction_positive_n"] = len(contrad)
        m["contradiction_control_n"] = len(controls)
        m["contradiction_detection"] = sum(r["pred_contradiction"] for r in contrad) / len(contrad)
        m["contradiction_false_certainty"] = sum((not r["pred_contradiction"]) and r["pred_state"].get("information") == "sufficient" for r in contrad) / len(contrad)
        m["false_contradiction"] = sum(r["pred_contradiction"] for r in controls) / len(controls) if controls else 0.0

    if suite == "G7":
        latest, obsolete_suppressed = [], []
        for r in records:
            f = r["metadata"]["superseded_factor"]
            latest.append(r["pred_state"].get(f) == r["metadata"]["latest_value"])
            obsolete_suppressed.append(r["pred_state"].get(f) != r["metadata"]["obsolete_value"])
        m["latest_valid_accuracy"] = sum(latest) / len(latest)
        m["obsolete_evidence_suppression"] = sum(obsolete_suppressed) / len(obsolete_suppressed)
        m["false_contradiction_under_supersession"] = sum(r["pred_contradiction"] for r in records) / len(records)

    if suite == "G8":
        factor_hits, contam = [], []
        for r in records:
            decoy = r["metadata"]["decoy_state"]
            for f in FACTORS:
                factor_hits.append(r["pred_state"].get(f) == r["gold_state"].get(f))
                if decoy.get(f) != r["gold_state"].get(f):
                    contam.append(r["pred_state"].get(f) == decoy.get(f) and r["pred_state"].get(f) != r["gold_state"].get(f))
        m["scope_accuracy"] = sum(factor_hits) / len(factor_hits)
        m["cross_scope_contamination"] = sum(contam) / len(contam) if contam else 0.0
        m["false_contradiction_from_cross_scope"] = sum(r["pred_contradiction"] for r in records) / len(records)

    if suite == "G10":
        false_certainty = []
        for r in records:
            f = r["metadata"]["uncertain_factor"]
            risky = {"permission": "granted", "information": "sufficient", "execution_possible": True}[f]
            false_certainty.append(r["pred_state"].get(f) == risky)
        m["uncertainty_false_certainty"] = sum(false_certainty) / len(false_certainty)

    if suite == "G14":
        by_pair = defaultdict(dict)
        for r in records:
            by_pair[r["metadata"]["pair_id"]][r["metadata"]["pair_role"]] = r
        exact, directional, disable = [], [], []
        for pair in by_pair.values():
            a, b = pair["base"], pair["mutated"]
            exact.append(a["pred_action"] == a["gold_action"] and b["pred_action"] == b["gold_action"])
            directional.append(a["pred_action"] == "ACT" and b["pred_action"] != "ACT")
            disable.append(b["pred_action"] != "ACT")
        m["counterfactual_exact_pair"] = sum(exact) / len(exact)
        m["counterfactual_directional"] = sum(directional) / len(directional)
        m["counterfactual_act_disable"] = sum(disable) / len(disable)

    report = {
        "suite": suite,
        "name": SUITES[suite]["name"],
        "n": len(records),
        "seed": SUITES[suite]["seed"],
        "dataset_sha256": sha256_obj(dataset_fingerprint),
        "prediction_sha256": sha256_obj(prediction_fingerprint),
        "metrics": m,
    }
    return report, records
