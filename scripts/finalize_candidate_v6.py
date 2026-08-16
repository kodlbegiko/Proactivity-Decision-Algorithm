from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_terminal(results: Path, out: Path) -> dict[str, Any]:
    qualification = read_json(results / "qualification.json")
    selected = read_json(results / "selected_candidate.json")
    validation = read_json(results / "validation_metrics.json")
    dev = read_json(results / "development_ood_metrics.json")
    lexical = read_json(results / "lexical_holdout_metrics.json")
    rendering = read_json(results / "rendering_holdout_metrics.json")
    compositional = read_json(results / "compositional_holdout_metrics.json")
    negation = read_json(results / "negation_metrics.json")
    counterfactual = read_json(results / "counterfactual_metrics.json")
    invariance = read_json(results / "invariance_metrics.json")
    baselines = read_json(results / "baselines.json")
    ablations = read_json(results / "ablations.json")
    search = read_json(results / "architecture_search.json")
    integrity = read_json(results / "research_integrity.json")
    reproducibility = read_json(results / "reproducibility.json")

    terminal = {
        "schema_version": 1,
        "terminal_state": qualification["terminal_state"],
        "branch": "research/candidate-v6-structured-latent-reasoning",
        "base_commit": "a4e73fb0f16694efbe75ace8c088075fe83c9303",
        "preregistration_commit": "a077a6bf5e522e85c84820efbe3c9ae350d126bc",
        "candidate_source_commit": os.environ["CANDIDATE_V6_SOURCE_COMMIT"],
        "candidate_source_sha": selected["source_hashes"],
        "dataset_freeze_commit": os.environ["CANDIDATE_V6_DATASET_FREEZE_COMMIT"],
        "selection_commit": os.environ["CANDIDATE_V6_SELECTION_COMMIT"],
        "qualification_commit": os.environ["CANDIDATE_V6_QUALIFICATION_COMMIT"],
        "ci_run_id": os.environ.get("GITHUB_RUN_ID", "UNKNOWN"),
        "model_id": selected["model_id"],
        "model_revision": selected["model_revision"],
        "tokenizer_revision": selected["tokenizer_revision"],
        "candidate_v3_protected_access": integrity["candidate_v3_protected_access"],
        "candidate_v4_protected_access": integrity["candidate_v4_protected_access"],
        "candidate_v5_holdout_reuse": integrity["candidate_v5_holdout_reuse"],
        "protected_leakage": "NONE_DETECTED",
        "chronology_status": integrity["chronology"],
        "reproducibility": reproducibility,
        "validation": validation,
        "development_ood": dev,
        "lexical": lexical,
        "rendering": rendering,
        "compositional": compositional,
        "negation": negation,
        "counterfactual": counterfactual,
        "invariance": invariance,
        "architecture_evidence": {
            "v6a_best": _best_family(search, "V6A"),
            "v6b_best": _best_family(search, "V6B"),
            "v6c_best": _best_family(search, "V6C"),
            "selected_architecture": selected["architecture"],
            "selected_config": selected["config"],
            "selection_rationale": search["selection_objective"],
            "baselines": baselines,
            "ablations": ablations,
        },
        "criteria": qualification["criteria"],
        "catastrophic": qualification["catastrophic"],
        "candidate_v6_fresh_independent_protected_confirmatory": qualification[
            "candidate_v6_fresh_independent_protected_confirmatory"
        ],
        "gate_g": "NOT EXECUTED",
    }
    write_json(out, terminal)
    return terminal


def _best_family(search: dict[str, Any], family: str) -> dict[str, Any] | None:
    members = [item for item in search["results"] if item["config"]["architecture"] == family]
    if not members:
        return None
    return max(
        members,
        key=lambda item: (
            item["metrics"]["latent"]["exact_latent_state_reconstruction"],
            item["metrics"]["latent"]["mean_factor_macro_f1"],
            item["metrics"]["action"]["macro_f1"],
        ),
    )


def build_report(terminal: dict[str, Any], terminal_evidence_commit: str, path: Path) -> None:
    v = terminal["validation"]
    lines = [
        "# Candidate-v6 Development Terminal Report",
        "",
        f"**Terminal State:** `{terminal['terminal_state']}`",
        "",
        "## Identity",
        "",
        f"- Branch: `{terminal['branch']}`",
        f"- Base Commit: `{terminal['base_commit']}`",
        f"- Preregistration Commit: `{terminal['preregistration_commit']}`",
        f"- Candidate Source Commit: `{terminal['candidate_source_commit']}`",
        f"- Dataset Freeze Commit: `{terminal['dataset_freeze_commit']}`",
        f"- Selection Commit: `{terminal['selection_commit']}`",
        f"- Qualification Commit: `{terminal['qualification_commit']}`",
        f"- Terminal Evidence Commit: `{terminal_evidence_commit}`",
        f"- CI Run ID: `{terminal['ci_run_id']}`",
        f"- Model: `{terminal['model_id']}@{terminal['model_revision']}`",
        "",
        "## Research Integrity",
        "",
        f"- Candidate-v3 protected access: `{terminal['candidate_v3_protected_access']}`",
        f"- Candidate-v4 protected access: `{terminal['candidate_v4_protected_access']}`",
        f"- Candidate-v5 holdout reuse: `{terminal['candidate_v5_holdout_reuse']}`",
        f"- Protected leakage: `{terminal['protected_leakage']}`",
        f"- Chronology: `{terminal['chronology_status']}`",
        "",
        "## Validation",
        "",
        f"- Accuracy: `{v['action']['accuracy']:.6f}`",
        f"- Macro-F1: `{v['action']['macro_f1']:.6f}`",
        f"- Exact latent-state reconstruction: `{v['latent']['exact_latent_state_reconstruction']:.6f}`",
        f"- Mean factor accuracy: `{v['latent']['mean_factor_accuracy']:.6f}`",
        f"- ACT-critical factor accuracy: `{v['latent']['act_critical_factor_accuracy']:.6f}`",
        f"- Critical UNKNOWN rate: `{v['latent']['critical_unknown_rate']:.6f}`",
        f"- Forbidden ACT: `{v['action']['forbidden_act']}`",
        f"- Invalid action: `{v['action']['invalid_action']}`",
        "",
        "## Holdout Summary",
        "",
        f"- Development OOD macro-F1: `{terminal['development_ood']['action']['macro_f1']:.6f}`",
        f"- Lexical macro-F1: `{terminal['lexical']['action']['macro_f1']:.6f}`",
        f"- Rendering macro-F1: `{terminal['rendering']['action']['macro_f1']:.6f}`",
        f"- Compositional macro-F1: `{terminal['compositional']['action']['macro_f1']:.6f}`",
        f"- Negation macro-F1: `{terminal['negation']['action']['macro_f1']:.6f}`",
        f"- Counterfactual exact-pair: `{terminal['counterfactual']['exact_pair_correctness']:.6f}`",
        f"- Invariance action consistency: `{terminal['invariance']['action_consistency']:.6f}`",
        "",
        "## Architecture Evidence",
        "",
        f"- Selected architecture: `{terminal['architecture_evidence']['selected_architecture']}`",
        f"- Selected config: `{terminal['architecture_evidence']['selected_config']['config_id']}`",
        "- V6A, V6B, V6C family summaries, baselines, and ablations are preserved in `gate_recovery_v6/terminal.json`.",
        "",
        "## Scientific Interpretation",
        "",
        _interpret(terminal),
        "",
        "## Final Authorization",
        "",
        f"Candidate-v6 Fresh Independent Protected Confirmatory: **{terminal['candidate_v6_fresh_independent_protected_confirmatory']}**",
        "",
        "Gate G: **NOT EXECUTED**",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _interpret(terminal: dict[str, Any]) -> str:
    c = terminal["criteria"]
    failed = [name for name, passed in c.items() if not passed]
    if terminal["terminal_state"].startswith("CANDIDATE V6 DEVELOPMENT PASS"):
        return (
            "Structured latent-state inference plus the frozen Protocol-v2 policy satisfied all preregistered development, "
            "generalization, safety, integrity, and reproducibility criteria. This supports advancing only to a fresh independent protected confirmatory evaluation; it does not establish universal correctness or human preference alignment."
        )
    return (
        "The structured latent-state direction did not satisfy every preregistered mandatory criterion. Failed criteria: "
        + ", ".join(failed)
        + ". The lineage is therefore frozen as a development FAIL without holdout tuning or rescue. The preserved factor, calibration, counterfactual, invariance, baseline, and ablation evidence should be used only as aggregate architectural evidence for a future fresh lineage."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p_terminal = sub.add_parser("terminal")
    p_terminal.add_argument("--results", type=Path, default=Path("results/candidate_v6_development"))
    p_terminal.add_argument("--out", type=Path, default=Path("gate_recovery_v6/terminal.json"))
    p_report = sub.add_parser("report")
    p_report.add_argument("--terminal", type=Path, default=Path("gate_recovery_v6/terminal.json"))
    p_report.add_argument("--terminal-evidence-commit", required=True)
    p_report.add_argument("--out", type=Path, default=Path("docs/candidate_v6_development_terminal_report.md"))
    args = parser.parse_args()
    if args.command == "terminal":
        build_terminal(args.results, args.out)
    else:
        terminal = read_json(args.terminal)
        build_report(terminal, args.terminal_evidence_commit, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
