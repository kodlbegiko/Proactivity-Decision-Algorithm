from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

BASE_COMMIT = "a4e73fb0f16694efbe75ace8c088075fe83c9303"
PREREG_COMMIT = "a077a6bf5e522e85c84820efbe3c9ae350d126bc"
BRANCH = "research/candidate-v6-structured-latent-reasoning"
PREREG_PATH = Path("preregistration/candidate_v6_structured_latent_reasoning.md")
INTEGRITY_SCRIPT = Path("scripts/check_candidate_v6_research_integrity.py")
SOURCE_PATHS = (
    Path("src/proactivity/candidate_v6.py"),
    Path("src/proactivity/candidate_v6_data.py"),
    Path("src/proactivity/candidate_v6_metrics.py"),
    Path("src/proactivity/candidate_v6_evaluate.py"),
    INTEGRITY_SCRIPT,
)
FORBIDDEN_IMPORT_PREFIXES = (
    "proactivity.candidate_v3",
    "proactivity.candidate_v4",
    "proactivity.candidate_v5",
    "proactivity.recovery_candidates_v3",
    "proactivity.recovery_v4_data",
)
FORBIDDEN_PATH_LITERALS = (
    "data/candidate_v4_fresh_confirmatory",
    "results/candidate_v4_fresh_confirmatory",
    "data/candidate_v5_development",
    "results/candidate_v5_development",
    "data/protected",
)
EXPECTED_COUNTS = {
    "train": 3600,
    "validation": 900,
    "development_ood": 900,
    "lexical_holdout": 600,
    "rendering_holdout": 600,
    "compositional_holdout": 600,
    "negation": 360,
    "counterfactual": 360,
    "invariance": 360,
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"CANDIDATE_V6_INTEGRITY_FAIL: {message}")


def check_chronology() -> dict[str, Any]:
    current_branch = git("branch", "--show-current")
    if current_branch != BRANCH:
        fail(f"unexpected branch {current_branch}")
    prereg_parent = git("show", "-s", "--format=%P", PREREG_COMMIT)
    if prereg_parent != BASE_COMMIT:
        fail(f"preregistration parent {prereg_parent} != required base {BASE_COMMIT}")
    prereg_path_at_commit = git("show", "--format=", "--name-only", PREREG_COMMIT)
    if str(PREREG_PATH) not in prereg_path_at_commit.splitlines():
        fail("preregistration commit does not create expected preregistration path")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", PREREG_COMMIT, "HEAD"])
    for path in SOURCE_PATHS:
        if not path.exists():
            fail(f"missing source artifact {path}")
        first_commit = git("log", "--reverse", "--format=%H", "--", str(path)).splitlines()[0]
        if first_commit == PREREG_COMMIT:
            fail(f"source artifact existed in preregistration commit: {path}")
        subprocess.check_call(["git", "merge-base", "--is-ancestor", PREREG_COMMIT, first_commit])
    return {
        "branch": current_branch,
        "base_commit": BASE_COMMIT,
        "preregistration_commit": PREREG_COMMIT,
        "chronology": "PASS",
    }


def check_source_quarantine() -> dict[str, Any]:
    import_violations: list[str] = []
    path_literal_violations: list[str] = []
    for path in SOURCE_PATHS:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.ImportFrom):
                module = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name.startswith(prefix) for prefix in FORBIDDEN_IMPORT_PREFIXES):
                        import_violations.append(f"{path}:{alias.name}")
            if module and any(module.startswith(prefix) for prefix in FORBIDDEN_IMPORT_PREFIXES):
                import_violations.append(f"{path}:{module}")
        # The audit script itself must name forbidden paths in order to enforce the boundary.
        # Treating those declarations as evidence access is a self-scan false positive; only
        # executable Candidate-v6 decision/data/evaluation source is checked for such literals.
        if path == INTEGRITY_SCRIPT:
            continue
        for literal in FORBIDDEN_PATH_LITERALS:
            if literal in source:
                path_literal_violations.append(f"{path}:{literal}")
    if import_violations:
        fail("forbidden imports: " + ", ".join(import_violations))
    if path_literal_violations:
        fail("forbidden individual-evidence path literals: " + ", ".join(path_literal_violations))
    return {
        "candidate_v3_protected_access": 0,
        "candidate_v4_protected_access": 0,
        "candidate_v5_holdout_reuse": False,
        "forbidden_import_violations": [],
        "forbidden_path_literal_violations": [],
        "quarantine": "PASS",
    }


def check_dataset(data_dir: Path) -> dict[str, Any]:
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.exists():
        fail("dataset manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("candidate_v3_protected_access") != 0:
        fail("candidate_v3_protected_access is nonzero")
    if manifest.get("candidate_v4_protected_access") != 0:
        fail("candidate_v4_protected_access is nonzero")
    if manifest.get("candidate_v5_holdout_reuse") is not False:
        fail("candidate_v5_holdout_reuse is not false")
    for split, expected in EXPECTED_COUNTS.items():
        actual = int(manifest.get("counts", {}).get(split, -1))
        if actual != expected:
            fail(f"count mismatch {split}: {actual} != {expected}")
        path = data_dir / f"{split}.jsonl"
        if not path.exists():
            fail(f"missing dataset split {path}")
        expected_hash = manifest.get("sha256", {}).get(path.name)
        actual_hash = sha256(path)
        if expected_hash != actual_hash:
            fail(f"dataset hash mismatch {path.name}")
    if not manifest.get("source_commit") or manifest.get("source_commit") == "UNSET":
        fail("manifest source_commit is unset")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", str(manifest["source_commit"]), "HEAD"])
    return {
        "dataset": "PASS",
        "dataset_source_commit": manifest["source_commit"],
        "dataset_hashes": manifest["sha256"],
    }


def check_selection(result_dir: Path) -> dict[str, Any]:
    selected_path = result_dir / "selected_candidate.json"
    search_path = result_dir / "architecture_search.json"
    if not selected_path.exists() or not search_path.exists():
        fail("selection artifacts missing")
    selected = json.loads(selected_path.read_text(encoding="utf-8"))
    search = json.loads(search_path.read_text(encoding="utf-8"))
    if selected.get("selection_uses_holdout") is not False:
        fail("selection_uses_holdout must be false")
    if search.get("selection_data") != ["validation"]:
        fail(f"invalid selection_data {search.get('selection_data')}")
    if int(search.get("evaluated_configurations", -1)) > 22:
        fail("architecture search budget exceeded")
    if int(search.get("evaluated_configurations", -1)) != 22:
        fail("architecture search did not execute exactly preregistered 22 configurations")
    if selected.get("model_revision") != "1110a243fdf4706b3f48f1d95db1a4f5529b4d41":
        fail("model revision drift")
    return {
        "selection": "PASS",
        "selected_config": selected["config"],
        "selection_data": search["selection_data"],
        "evaluated_configurations": search["evaluated_configurations"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("source", "dataset", "selection", "terminal"), required=True)
    parser.add_argument("--data", type=Path, default=Path("data/candidate_v6_development"))
    parser.add_argument("--results", type=Path, default=Path("results/candidate_v6_development"))
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report: dict[str, Any] = {}
    report.update(check_chronology())
    report.update(check_source_quarantine())
    if args.phase in {"dataset", "selection", "terminal"}:
        report.update(check_dataset(args.data))
    if args.phase in {"selection", "terminal"}:
        report.update(check_selection(args.results))
    report["phase"] = args.phase
    report["status"] = "PASS"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
