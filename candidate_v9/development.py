from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from benchmark_v9.evaluation import (
    evaluate_contradiction,
    evaluate_counterfactual_pairs,
    evaluate_joint_resolution,
    evaluate_negation,
    evaluate_rows,
    evaluate_supersession,
    qualifies_validation,
)
from benchmark_v9.generator import (
    make_act_boundary,
    make_contradiction,
    make_counterfactual_pairs,
    make_dataset,
    make_joint_constraint,
    make_negation,
    make_state_validity_stress,
    make_supersession,
    make_uncertainty,
    write_jsonl,
)

ARCHITECTURES = ("V9-A", "V9-B", "V9-C")
SEEDS = {
    "train": 91001,
    "validation": 91002,
    "state_validity_stress": 91003,
    "act_boundary": 91004,
    "contradiction": 91005,
    "negation": 91006,
    "supersession": 91007,
    "uncertainty": 91008,
    "permission_scope": 91009,
    "compositional": 91010,
    "rendering": 91011,
    "lexical": 91012,
}
SIZES = {
    "train": 9000,
    "validation": 2400,
    "state_validity_stress": 2400,
    "act_boundary": 1500,
    "contradiction": 600,
    "negation": 600,
    "supersession": 600,
    "uncertainty": 600,
    "permission_scope": 600,
    "compositional": 600,
    "rendering": 600,
    "lexical": 600,
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def materialize_development_data(root: str | Path = ".") -> dict[str, str]:
    root = Path(root)
    data = root / "data" / "candidate_v9_development"
    data.mkdir(parents=True, exist_ok=True)
    datasets: dict[str, list[dict[str, Any]]] = {
        "train.jsonl": make_dataset(SIZES["train"], SEEDS["train"], "train", "train"),
        "validation.jsonl": make_dataset(SIZES["validation"], SEEDS["validation"], "validation", "validation"),
        "state_validity_stress.jsonl": make_state_validity_stress(SIZES["state_validity_stress"], SEEDS["state_validity_stress"]),
        "act_boundary.jsonl": make_act_boundary(SIZES["act_boundary"], SEEDS["act_boundary"]),
        "contradiction.jsonl": make_contradiction(SIZES["contradiction"], SEEDS["contradiction"]),
        "negation.jsonl": make_negation(SIZES["negation"], SEEDS["negation"]),
        "supersession.jsonl": make_supersession(SIZES["supersession"], SEEDS["supersession"]),
        "uncertainty.jsonl": make_uncertainty(SIZES["uncertainty"], SEEDS["uncertainty"]),
        "permission_scope.jsonl": make_joint_constraint(SIZES["permission_scope"], SEEDS["permission_scope"]),
        "compositional.jsonl": make_dataset(SIZES["compositional"], SEEDS["compositional"], "validation", "compositional", narrative=True),
        "rendering.jsonl": make_dataset(SIZES["rendering"], SEEDS["rendering"], "rendering", "rendering", narrative=True),
        "lexical.jsonl": make_dataset(SIZES["lexical"], SEEDS["lexical"], "lexical", "lexical"),
    }
    hashes: dict[str, str] = {}
    for filename, rows in datasets.items():
        path = data / filename
        write_jsonl(path, rows)
        hashes[filename] = _sha256(path)
    (data / "manifest.json").write_text(
        json.dumps({"seeds": SEEDS, "sizes": SIZES, "sha256": hashes}, indent=2, sort_keys=True), encoding="utf-8"
    )
    return hashes


def run_architecture_search(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    validation = make_dataset(SIZES["validation"], SEEDS["validation"], "validation", "validation")
    counterfactual = make_counterfactual_pairs(1000, SEEDS["act_boundary"] + 5000, "validation")
    invalid_attack = make_state_validity_stress(SIZES["state_validity_stress"], SEEDS["state_validity_stress"])
    act_boundary = make_act_boundary(SIZES["act_boundary"], SEEDS["act_boundary"])
    contradiction = make_contradiction(SIZES["contradiction"], SEEDS["contradiction"])
    supersession = make_supersession(SIZES["supersession"], SEEDS["supersession"])
    negation = make_negation(SIZES["negation"], SEEDS["negation"])
    joint = make_joint_constraint(1200, SEEDS["permission_scope"])

    results: dict[str, Any] = {}
    for architecture in ARCHITECTURES:
        metrics = evaluate_rows(validation, architecture)
        cf = evaluate_counterfactual_pairs(counterfactual, architecture)
        invalid_metrics = evaluate_joint_resolution(invalid_attack, architecture)
        act_metrics = evaluate_rows(act_boundary, architecture)
        contradiction_metrics = evaluate_contradiction(contradiction, architecture)
        supersession_metrics = evaluate_supersession(supersession, architecture)
        negation_metrics = evaluate_negation(negation, architecture)
        joint_metrics = evaluate_joint_resolution(joint, architecture)
        adversarial_pass = (
            invalid_metrics["invalid_predicted_states"] == 0
            and act_metrics["forbidden_act"] == 0
            and act_metrics["false_act"] == 0
            and act_metrics["act_recall"] >= 0.85
            and contradiction_metrics["contradiction_detection"] >= 0.95
            and contradiction_metrics["false_certainty"] == 0
            and contradiction_metrics["invalid_predicted_states"] == 0
            and supersession_metrics["factor_behavior"] >= 0.95
            and negation_metrics["factor_accuracy"] >= 0.95
            and joint_metrics["invalid_predicted_states"] == 0
            and joint_metrics["joint_valid_state_resolution_accuracy"] >= 0.95
        )
        # V9-A is explicitly a post-hoc projection baseline. It is evaluated but
        # cannot become the final candidate because the mission requires a
        # valid-by-construction / constrained-decoding architecture.
        structural_eligible = architecture in {"V9-B", "V9-C"}
        qualified = qualifies_validation(metrics, cf) and adversarial_pass and structural_eligible
        results[architecture] = {
            "validation": metrics,
            "counterfactual": cf,
            "invalid_state_attack": invalid_metrics,
            "act_boundary": act_metrics,
            "contradiction": contradiction_metrics,
            "supersession": supersession_metrics,
            "negation": negation_metrics,
            "joint_state_constraint": joint_metrics,
            "structural_eligible": structural_eligible,
            "qualified": qualified,
        }

    qualified = [name for name in ARCHITECTURES if results[name]["qualified"]]
    selected = None
    if qualified:
        # Earlier criteria are hard qualifications for all surviving candidates;
        # apply the preregistered remaining ranking criteria.
        complexity = {"V9-B": 2, "V9-C": 3}
        qualified.sort(
            key=lambda name: (
                -results[name]["validation"]["act_precision"],
                -results[name]["validation"]["act_recall"],
                -results[name]["validation"]["exact_state_accuracy"],
                -results[name]["validation"]["macro_f1"],
                complexity[name],
            )
        )
        selected = qualified[0]

    report = {
        "architectures": results,
        "selected_candidate": selected,
        "qualification_pass": selected is not None,
        "selection_rule": [
            "zero invalid predicted states",
            "forbidden ACT",
            "false ACT",
            "counterfactual ACT-disable",
            "ACT precision",
            "ACT recall",
            "exact structured-state accuracy",
            "Macro-F1",
            "lower complexity",
        ],
    }
    report_dir = root / "reports" / "candidate_v9"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "architecture_search.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


if __name__ == "__main__":
    materialize_development_data(".")
    result = run_architecture_search(".")
    print(json.dumps({"selected_candidate": result["selected_candidate"], "qualification_pass": result["qualification_pass"]}, indent=2))
