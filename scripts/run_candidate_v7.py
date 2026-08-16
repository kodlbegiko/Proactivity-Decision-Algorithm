from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from proactivity.candidate_v7_data import generate_all
from proactivity.candidate_v7_evaluate import make_decision, qualify, run_ablations, run_baselines, search_architectures


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def cmd_generate(args: argparse.Namespace) -> None:
    manifest = generate_all(args.output)
    print(json.dumps(manifest, sort_keys=True))


def cmd_search(args: argparse.Namespace) -> None:
    result = search_architectures(Path(args.data) / "validation.jsonl", args.results)
    print(json.dumps({"selected_config": result["selected_config"], "selected_family": result["selected_family"]}, sort_keys=True))


def cmd_qualify(args: argparse.Namespace) -> None:
    result = qualify(args.data, Path(args.results) / "selected_candidate.json", args.results)
    print(json.dumps(result, sort_keys=True))


def cmd_baselines(args: argparse.Namespace) -> None:
    root = Path(args.data)
    run_baselines(root / "train.jsonl", root / "validation.jsonl", Path(args.results) / "baseline_results.json")


def cmd_ablations(args: argparse.Namespace) -> None:
    run_ablations(args.data, Path(args.results) / "selected_candidate.json", Path(args.results) / "ablation_results.json")


def cmd_decision(args: argparse.Namespace) -> None:
    decision = make_decision(args.results, Path(args.results) / "qualification_decision.json")
    print(decision["terminal_state"])


def cmd_report(args: argparse.Namespace) -> None:
    root = Path(args.results)
    selected = _read(root / "selected_candidate.json")
    decision = _read(root / "qualification_decision.json")
    val = _read(root / "validation_metrics.json")
    ood = _read(root / "ood_metrics.json")
    lex = _read(root / "lexical_metrics.json")
    rend = _read(root / "rendering_metrics.json")
    comp = _read(root / "compositional_metrics.json")
    neg = _read(root / "negation_metrics.json")
    scope = _read(root / "scope_metrics.json")
    temporal = _read(root / "temporal_metrics.json")
    cf = _read(root / "counterfactual_metrics.json")
    inv = _read(root / "invariance_metrics.json")
    safety = _read(root / "safety_report.json")
    collapse = _read(root / "collapse_report.json")
    integrity = _read(root / "research_integrity.json")
    baselines = _read(root / "baseline_results.json")
    ablations = _read(root / "ablation_results.json")

    def f(value: float) -> str:
        return f"{value:.6f}"

    failed = decision.get("failed_criteria", [])
    lines = [
        "# Candidate-v7 Development Terminal Report", "",
        f"**Terminal State:** `{decision['terminal_state']}`", "",
        "## Identity", "",
        f"- Branch: `{args.branch}`",
        f"- Preregistration Commit: `{args.prereg_commit}`",
        f"- Candidate Source Commit: `{args.source_commit}`",
        f"- Source Freeze Commit: `{args.source_freeze_commit}`",
        f"- Dataset Freeze Commit: `{args.dataset_commit}`",
        f"- Selected Candidate Commit: `{args.selected_commit}`",
        f"- Qualification Commit: `{args.qualification_commit}`",
        f"- Terminal Evidence Commit: `{args.terminal_commit}`",
        f"- GitHub Actions Run ID: `{args.run_id}`", "",
        "## Research Integrity", "",
        f"- Status: `{integrity.get('status')}`",
        f"- Protected leakage: `{integrity.get('protected_leakage')}`",
        f"- Chronology: `{integrity.get('chronology')}`",
        f"- Validation-only selection: `{integrity.get('validation_only_selection')}`",
        f"- Qualification execution count: `{integrity.get('qualification_execution_count')}`", "",
        "## Selected Architecture", "",
        f"- Family: `{selected['architecture']}`",
        f"- Configuration: `{selected['config']}`",
        "- Pipeline: raw text -> proposition segmentation -> semantic operators -> factor evidence graph -> constrained state reconstruction -> frozen Protocol-v2 oracle.", "",
        "## Validation", "",
        f"- Accuracy: `{f(val['action']['accuracy'])}`",
        f"- Macro-F1: `{f(val['action']['macro_f1'])}`", "",
        "## Latent-State Recovery", "",
        f"- Exact latent-state reconstruction: `{f(val['latent']['exact_latent_state_reconstruction'])}`",
        f"- Mean factor accuracy: `{f(val['latent']['mean_factor_accuracy'])}`",
        f"- Mean factor macro-F1: `{f(val['latent']['mean_factor_macro_f1'])}`",
        f"- ACT-critical factor accuracy: `{f(val['latent']['act_critical_factor_accuracy'])}`",
        f"- Critical UNKNOWN rate: `{f(val['latent']['critical_unknown_rate'])}`", "",
        "## Distribution Shifts", "",
        f"- Development OOD Macro-F1: `{f(ood['action']['macro_f1'])}`",
        f"- Lexical Macro-F1: `{f(lex['action']['macro_f1'])}`",
        f"- Rendering Macro-F1: `{f(rend['action']['macro_f1'])}`",
        f"- Compositional Macro-F1: `{f(comp['action']['macro_f1'])}`",
        f"- Negation Macro-F1: `{f(neg['action']['macro_f1'])}`",
        f"- Scope Macro-F1: `{f(scope['action']['macro_f1'])}`",
        f"- Temporal Macro-F1: `{f(temporal['action']['macro_f1'])}`", "",
        "## Counterfactual and Invariance", "",
        f"- Counterfactual exact-pair: `{f(cf['pair']['exact_pair'])}`",
        f"- Counterfactual factor-transition correctness: `{f(cf['pair']['factor_transition_correctness'])}`",
        f"- Invariance action consistency: `{f(inv['pair']['action_consistency'])}`",
        f"- Invariance latent-state consistency: `{f(inv['pair']['latent_state_consistency'])}`", "",
        "## Safety", "",
        f"- Forbidden ACT: `{safety['forbidden_act']}`",
        f"- Invalid action: `{safety['invalid_action']}`",
        f"- Catastrophic collapse: `{collapse['catastrophic_collapse']}`", "",
        "## Baselines", "",
        "Baselines include majority action, direct token classifier, deterministic feature-hash embedding -> action, a fresh V6-style factor-matcher reconstruction, no-logic proposition model, and no-negation-awareness model.", "",
        f"- B0 validation Macro-F1: `{f(baselines['B0_majority_action']['macro_f1'])}`",
        f"- B1 validation Macro-F1: `{f(baselines['B1_direct_token_nb_action']['macro_f1'])}`",
        f"- B2 validation Macro-F1: `{f(baselines['B2_direct_feature_hash_embedding_action']['macro_f1'])}`", "",
        "## Ablations", "",
        "The full candidate and all mandatory ablations were executed after qualification. See `results/candidate_v7_development/ablation_results.json` for the frozen aggregate evidence.", "",
        "## Failure Analysis", "",
        ("- No mandatory qualification criterion failed." if not failed else "- Failed mandatory criteria: " + ", ".join(f"`{item}`" for item in failed)), "",
        "## Scientific Interpretation", "",
        "Candidate-v7 tests whether explicit proposition structure, polarity/scope/temporal interpretation and constrained state reconstruction materially improve raw-language recovery of the formal Protocol-v2 state. The development result must be interpreted only within the fresh synthetic generator and preregistered shifts; it does not establish human preference alignment or ecological validity.", "",
        "A PASS means the frozen Candidate-v7 met every preregistered development criterion. A FAIL means the architecture did not meet at least one mandatory criterion and is not rescued or retuned from qualification evidence. CI success alone is not scientific PASS.", "",
        "## Authorization", "",
        f"- Fresh independent confirmatory: **{decision['fresh_confirmatory']}**",
        "- Gate G: **NOT EXECUTED**", "",
        "If development PASSed, the next scientific step is a separately preregistered fresh independent confirmatory evaluation with a new generator, seeds, realization families and protected dataset. Candidate-v7 qualification holdouts are not authorized as confirmatory evidence.", "",
    ]
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("\n".join(lines), encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("generate"); p.add_argument("--output", required=True); p.set_defaults(func=cmd_generate)
    p = sub.add_parser("search"); p.add_argument("--data", required=True); p.add_argument("--results", required=True); p.set_defaults(func=cmd_search)
    p = sub.add_parser("qualify"); p.add_argument("--data", required=True); p.add_argument("--results", required=True); p.set_defaults(func=cmd_qualify)
    p = sub.add_parser("baselines"); p.add_argument("--data", required=True); p.add_argument("--results", required=True); p.set_defaults(func=cmd_baselines)
    p = sub.add_parser("ablations"); p.add_argument("--data", required=True); p.add_argument("--results", required=True); p.set_defaults(func=cmd_ablations)
    p = sub.add_parser("decision"); p.add_argument("--results", required=True); p.set_defaults(func=cmd_decision)
    p = sub.add_parser("report")
    p.add_argument("--results", required=True); p.add_argument("--output", required=True); p.add_argument("--branch", required=True)
    for name in ("prereg_commit","source_commit","source_freeze_commit","dataset_commit","selected_commit","qualification_commit","terminal_commit","run_id"):
        p.add_argument("--" + name.replace("_", "-"), dest=name, required=True)
    p.set_defaults(func=cmd_report)
    return parser


def main() -> None:
    args = build_parser().parse_args(); args.func(args)


if __name__ == "__main__":
    main()
