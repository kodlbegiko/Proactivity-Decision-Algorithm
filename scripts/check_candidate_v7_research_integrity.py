from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

FORBIDDEN_REFERENCES = (
    "data/protected/",
    "data/candidate_v4_fresh_confirmatory/",
    "data/candidate_v5_development/",
    "data/candidate_v6_development/",
    "results/candidate_v4_fresh_confirmatory/",
    "results/candidate_v5_development/",
    "results/candidate_v6_development/",
)
CANDIDATE_PATHS = (
    "src/proactivity/candidate_v7.py",
    "src/proactivity/candidate_v7_data.py",
    "src/proactivity/candidate_v7_metrics.py",
    "src/proactivity/candidate_v7_evaluate.py",
    "scripts/run_candidate_v7.py",
    "scripts/check_candidate_v7_research_integrity.py",
    ".github/workflows/candidate_v7_development.yml",
)


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def ancestor(older: str, newer: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", older, newer]).returncode == 0


def source_references() -> list[str]:
    hits: list[str] = []
    for path in CANDIDATE_PATHS:
        target = Path(path)
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_REFERENCES:
            if forbidden in text:
                hits.append(f"{path}:{forbidden}")
    return hits


def source_changed_since(source_commit: str) -> list[str]:
    changed = git("diff", "--name-only", f"{source_commit}..HEAD").splitlines()
    return sorted(path for path in changed if path in CANDIDATE_PATHS and path != "scripts/check_candidate_v7_research_integrity.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("prequalification", "terminal"), required=True)
    parser.add_argument("--prereg-commit", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-freeze-commit", required=True)
    parser.add_argument("--dataset-commit", required=True)
    parser.add_argument("--selected-commit", required=True)
    parser.add_argument("--qualification-commit")
    parser.add_argument("--results", default="results/candidate_v7_development")
    args = parser.parse_args()

    errors: list[str] = []
    chronology = [
        (args.prereg_commit, args.source_commit, "prereg_before_source"),
        (args.source_commit, args.source_freeze_commit, "source_before_source_freeze"),
        (args.source_freeze_commit, args.dataset_commit, "source_freeze_before_dataset"),
        (args.dataset_commit, args.selected_commit, "dataset_before_selection"),
    ]
    if args.phase == "terminal" and args.qualification_commit:
        chronology.append((args.selected_commit, args.qualification_commit, "selection_before_qualification"))
    for older, newer, label in chronology:
        if not ancestor(older, newer):
            errors.append(f"chronology:{label}")

    manifest_path = Path("data/candidate_v7_development/manifest.json")
    if not manifest_path.exists():
        errors.append("dataset_manifest_missing")
        manifest: dict[str, Any] = {}
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_counts = {"train":4800,"validation":1200,"development_ood":1200,"lexical_holdout":800,"rendering_holdout":800,"compositional_holdout":800,"negation_holdout":600,"scope_holdout":600,"temporal_holdout":600,"counterfactual":480,"invariance":480}
        if manifest.get("counts") != expected_counts:
            errors.append("dataset_counts_not_preregistered")
        if manifest.get("lexical_isolation") is not True:
            errors.append("lexical_isolation_failed")

    search_path = Path(args.results) / "architecture_search.json"
    selected_path = Path(args.results) / "selected_candidate.json"
    if not search_path.exists() or not selected_path.exists():
        errors.append("selection_artifacts_missing")
        search: dict[str, Any] = {}
    else:
        search = json.loads(search_path.read_text(encoding="utf-8"))
        if search.get("selection_source") != "validation_only" or search.get("holdouts_loaded") is not False:
            errors.append("validation_only_selection_failed")
        if search.get("configurations_evaluated", 999) > 12:
            errors.append("architecture_search_budget_exceeded")

    forbidden_hits = source_references()
    if forbidden_hits:
        errors.extend("forbidden_reference:" + hit for hit in forbidden_hits)
    changed_source = source_changed_since(args.source_commit)
    if changed_source:
        errors.extend("source_mutated_after_freeze:" + path for path in changed_source)

    marker = Path("gate_recovery_v7/qualification_execution.json")
    if args.phase == "prequalification":
        if marker.exists():
            data = json.loads(marker.read_text(encoding="utf-8"))
            if data.get("scientific_metrics_observed") is True or int(data.get("qualification_run_count", 0)) > 0:
                errors.append("qualification_already_executed")
        q_count = 0
    else:
        if not marker.exists():
            errors.append("qualification_marker_missing")
            q_count = 0
        else:
            data = json.loads(marker.read_text(encoding="utf-8"))
            q_count = int(data.get("qualification_run_count", 0))
            if q_count != 1:
                errors.append("qualification_execution_count_not_one")
            if data.get("scientific_metrics_observed") is not True:
                errors.append("qualification_completion_not_recorded")

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": args.phase,
        "chronology": "PASS" if not any(error.startswith("chronology:") for error in errors) else "FAIL",
        "protected_leakage": "NONE_DETECTED" if not forbidden_hits else "DETECTED",
        "forbidden_historical_path_references": forbidden_hits,
        "source_mutation_after_freeze": changed_source,
        "architecture_search_budget": search.get("configurations_evaluated"),
        "validation_only_selection": search.get("selection_source") == "validation_only" and search.get("holdouts_loaded") is False,
        "qualification_execution_count": q_count,
        "dataset_manifest_present": manifest_path.exists(),
        "errors": errors,
    }
    output = Path(args.results) / "research_integrity.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, sort_keys=True))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
