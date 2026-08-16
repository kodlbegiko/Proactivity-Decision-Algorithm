from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auditor import (
    audit_runner_inputs, integrity_audit, leakage_audit,
    verify_candidate_immutable, verify_preregistration,
)
from .common import (
    ACTIONS, CANDIDATE_ID, COUNTERFACTUAL_PAIRS_PER_RUN,
    DEVELOPMENT_TERMINAL_COMMIT, EXAMPLES_PER_RUN, FAMILIES,
    INVARIANCE_GROUPS_PER_RUN, INVARIANCE_REALIZATIONS, PROTOCOL_VERSION,
    RUN_SEEDS, SOURCE_FREEZE_COMMIT, TECHNICAL_RETRY_REASONS, THRESHOLDS,
    sha256_bytes, sha256_file, write_json,
)
from .protected_builder import build_all
from .scorer import score_all

ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
EVAL_DIR = ROOT / "evaluation/v11q"
PREREG_DIR = EVAL_DIR / "preregistration"
ARTIFACTS = ROOT / "artifacts/candidate_v11_qualification"
IMMUTABLE_MANIFEST = EVAL_DIR / "CANDIDATE_IMMUTABLE_MANIFEST.json"


def _git_show(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def _git_blob(commit: str, path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"{commit}:{path}"], cwd=ROOT, text=True).strip()


def _hash_at_commit(commit: str, path: str) -> str:
    return hashlib.sha256(_git_show(commit, path)).hexdigest()


def _copy_prereg_to_artifacts() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PREREG_DIR / "V11Q_PREREGISTRATION.md", ARTIFACTS / "QUALIFICATION_PREREGISTRATION.md")
    shutil.copy2(PREREG_DIR / "V11Q_PREREGISTRATION.json", ARTIFACTS / "QUALIFICATION_PREREGISTRATION.json")
    shutil.copy2(PREREG_DIR / "V11Q_PREREGISTRATION.sha256", ARTIFACTS / "QUALIFICATION_PREREGISTRATION.sha256")
    shutil.copy2(IMMUTABLE_MANIFEST, ARTIFACTS / "CANDIDATE_IMMUTABLE_MANIFEST.json")


def freeze() -> int:
    if (PREREG_DIR / "V11Q_PREREGISTRATION.json").exists():
        raise RuntimeError("preregistration already exists; refusing to rewrite frozen protocol")
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    PREREG_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    candidate_path = "src/proactivity/candidate_v11.py"
    policy_path = "spec/proactivity_policy_v2.json"
    ontology_path = "src/proactivity/specification/schema.py"
    candidate_sha = _hash_at_commit(SOURCE_FREEZE_COMMIT, candidate_path)
    if sha256_file(ROOT / candidate_path) != candidate_sha:
        raise RuntimeError("candidate_v11.py differs from source freeze before qualification")
    policy_sha = _hash_at_commit(SOURCE_FREEZE_COMMIT, policy_path)
    ontology_sha = _hash_at_commit(SOURCE_FREEZE_COMMIT, ontology_path)
    if sha256_file(ROOT / policy_path) != policy_sha or sha256_file(ROOT / ontology_path) != ontology_sha:
        raise RuntimeError("policy/schema differs from source freeze before qualification")

    immutable = {
        "candidate_id": CANDIDATE_ID,
        "development_terminal_commit": DEVELOPMENT_TERMINAL_COMMIT,
        "candidate_source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "candidate_source_paths": [candidate_path],
        "candidate_blob_hashes": {
            candidate_path: {
                "git_blob": _git_blob(SOURCE_FREEZE_COMMIT, candidate_path),
                "sha256": candidate_sha,
            }
        },
        "policy_hash": policy_sha,
        "ontology_hash": ontology_sha,
        "evaluation_protocol_version": PROTOCOL_VERSION,
        "immutable": True,
    }
    write_json(IMMUTABLE_MANIFEST, immutable)

    implementation_hashes = {
        name: sha256_file(EVAL_DIR / name)
        for name in ("common.py", "protected_builder.py", "runner.py", "scorer.py", "auditor.py", "orchestrate.py")
    }
    prereg = {
        "protocol_version": PROTOCOL_VERSION,
        "candidate_id": CANDIDATE_ID,
        "candidate_hashes": immutable,
        "qualification_run_count": len(RUN_SEEDS),
        "run_ids": list(RUN_SEEDS),
        "seeds": RUN_SEEDS,
        "examples_per_run": EXAMPLES_PER_RUN,
        "total_examples": EXAMPLES_PER_RUN * len(RUN_SEEDS),
        "construction": {
            "core_examples_per_run": 300,
            "counterfactual_pairs_per_run": COUNTERFACTUAL_PAIRS_PER_RUN,
            "invariance_groups_per_run": INVARIANCE_GROUPS_PER_RUN,
            "invariance_realizations_per_group": INVARIANCE_REALIZATIONS,
            "families": list(FAMILIES),
            "primary_family_rule": "deterministic rotation across action-stratified core states; every primary family must have positive support in every run",
            "action_balancing_rule": "core contributes exactly 50 examples per action; invariance contributes exactly 6 per action; counterfactual source endpoints contribute exactly 7 per action; target endpoints are determined only by one-factor oracle-changing neighbors",
            "semantic_state_sampling_rule": "enumerate valid Protocol-v2 formal states, evaluate only with frozen Protocol-v2 oracle, bucket by oracle action, shuffle each bucket with the frozen run seed, then sample without score feedback",
            "realization_mechanisms": [
                "independent semantic phrase inventory authored from Protocol-v2 state meanings",
                "lexical paraphrase",
                "rendering variation",
                "multi-clause composition",
                "structural negation",
                "scope-focused wording",
                "past-to-current supersession",
                "mixed adversarial combinations of at least three linguistic phenomena",
            ],
            "generator_must_not_import": ["proactivity.candidate_v11", "benchmark_v11.generator"],
            "ground_truth_source": "formal state + frozen Protocol-v2 oracle only",
        },
        "counterfactual_design": "42 minimum pairs per run; pair members differ in exactly one formal state field and the oracle action must change; both exact state reconstruction and action must be correct for pair credit",
        "invariance_design": "12 groups per run, three independent realizations of one identical formal state; action consistency and correct consistency are reported",
        "unknown_design": "one tenth of core cases attempt omission of exactly one field only when at least two valid values for that field preserve the same oracle action; omitted fields are scored as SEMANTICALLY_UNSPECIFIED and excluded from concrete-value factor denominators",
        "acceptance_criteria": THRESHOLDS,
        "aggregation_rule": "report pooled aggregate plus Q1-Q5 complete metrics and mean/median/min/max/population-standard-deviation; no run may be excluded or replaced",
        "terminal_threshold_scope": "formal acceptance thresholds apply to pooled protected metrics exactly as listed; all preregistered runs remain in the pooled decision and are also reported individually",
        "scoring_implementation_hash": implementation_hashes["scorer.py"],
        "generation_implementation_hash": implementation_hashes["protected_builder.py"],
        "runner_implementation_hash": implementation_hashes["runner.py"],
        "auditor_implementation_hash": implementation_hashes["auditor.py"],
        "all_implementation_hashes": implementation_hashes,
        "overlap_policy": {
            "exact_text_overlap_required": 0,
            "normalized_exact_overlap_required": 0,
            "pre_prediction_rebuild_allowed": True,
            "max_construction_attempts": 3,
            "rebuild_rule": "same frozen seed plus deterministic construction-attempt salt; rebuild is allowed only before any candidate prediction and only for exact/normalized overlap, never for scores",
        },
        "retry_policy": {
            "allowed_reasons": sorted(TECHNICAL_RETRY_REASONS),
            "seed_must_remain_unchanged": True,
            "dataset_must_remain_unchanged_after_prediction_begins": True,
            "candidate_must_remain_unchanged": True,
            "scorer_must_remain_unchanged": True,
            "score_driven_retry": False,
        },
        "terminal_decision_rule": {
            "integrity_fail": "CANDIDATE_V11 QUALIFICATION INVALID — NO_ARCHITECTURE_CONCLUSION",
            "evidence_invalid": "CANDIDATE_V11 QUALIFICATION INVALID — NO_ARCHITECTURE_CONCLUSION",
            "all_scientific_criteria_pass": "CANDIDATE_V11 QUALIFICATION PASS — FRESH_CONFIRMATORY_AUTHORIZED",
            "otherwise": "CANDIDATE_V11 QUALIFICATION FAIL — LINEAGE_TERMINATED",
        },
        "protected_storage": "raw protected examples exist only in ephemeral CI workspace; repository receives manifests, hashes, aggregate reports, and terminal evidence only",
        "candidate_runner_input_keys": ["example_id", "text"],
        "v7r_boundary": "V11Q qualification job must not materialize or read V7R protected raw data; V7R runtime materialization is confined to a separate regression job",
        "frozen_before_realization": True,
    }
    prereg_json = PREREG_DIR / "V11Q_PREREGISTRATION.json"
    write_json(prereg_json, prereg)
    md = f"""# Candidate-v11B V11Q Preregistration\n\nProtocol: `{PROTOCOL_VERSION}`  \nCandidate: `{CANDIDATE_ID}`  \nSource freeze: `{SOURCE_FREEZE_COMMIT}`  \nDevelopment terminal: `{DEVELOPMENT_TERMINAL_COMMIT}`\n\n## Frozen execution\n\n- Runs: Q1-Q5\n- Seeds: `{json.dumps(RUN_SEEDS, sort_keys=True)}`\n- Examples per run: {EXAMPLES_PER_RUN}\n- Total protected examples: {EXAMPLES_PER_RUN * len(RUN_SEEDS)}\n- Raw protected data is never committed to repository history.\n- Candidate runner receives exactly `example_id` and `text`.\n- Protected generation uses only Protocol-v2 schema/oracle and the independent V11Q realization implementation.\n- `candidate_v11` and `benchmark_v11.generator` are forbidden dependencies of the protected builder.\n\n## Relations\n\n- {COUNTERFACTUAL_PAIRS_PER_RUN} counterfactual minimum pairs per run.\n- {INVARIANCE_GROUPS_PER_RUN} invariance groups per run × {INVARIANCE_REALIZATIONS} realizations.\n\n## Acceptance criteria\n\n```json\n{json.dumps(THRESHOLDS, indent=2, sort_keys=True)}\n```\n\n## Retry and contamination policy\n\nOnly infrastructure retries are permitted, with unchanged candidate, seeds, dataset, scorer, and scientific parameters. Score-driven reruns, best-run selection, seed replacement, post-score candidate changes, protected-label exposure to the runner, or V7R protected raw access by V11Q invalidate the qualification.\n\n## Terminal rule\n\nThere are exactly three scientific terminal states: PASS/FRESH_CONFIRMATORY_AUTHORIZED, FAIL/LINEAGE_TERMINATED, or INVALID/NO_ARCHITECTURE_CONCLUSION.\n"""
    prereg_md = PREREG_DIR / "V11Q_PREREGISTRATION.md"
    prereg_md.write_text(md, encoding="utf-8")
    sha_file = PREREG_DIR / "V11Q_PREREGISTRATION.sha256"
    sha_file.write_text(
        f"{sha256_file(prereg_json)}  V11Q_PREREGISTRATION.json\n{sha256_file(prereg_md)}  V11Q_PREREGISTRATION.md\n",
        encoding="utf-8",
    )

    lineage = {
        "lineage": "Candidate-v11B Independent Protected Qualification",
        "candidate": CANDIDATE_ID,
        "development_branch": "research/candidate-v11-post-v7r-semantic-generalization",
        "development_terminal_commit": DEVELOPMENT_TERMINAL_COMMIT,
        "candidate_source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "qualification_branch": "research/candidate-v11-independent-qualification",
        "qualification_executed": False,
        "research_integrity": "PENDING",
        "terminal_decision": "PENDING",
    }
    write_json(ARTIFACTS / "LINEAGE_MANIFEST.json", lineage)
    _copy_prereg_to_artifacts()
    print("V11Q preregistration frozen; no protected examples have been realized.")
    return 0


def verify() -> int:
    immutable = verify_candidate_immutable(ROOT, IMMUTABLE_MANIFEST)
    prereg = verify_preregistration(ROOT)
    if not immutable["pass"] or not prereg["pass"]:
        print(json.dumps({"immutable": immutable, "preregistration": prereg}, indent=2))
        return 2
    print(json.dumps({"immutable": "PASS", "preregistration": "PASS"}, sort_keys=True))
    return 0


def _run_predictions(workspace: Path) -> dict[str, Any]:
    truth_paths = sorted((workspace / "truth").glob("Q*.jsonl"))
    for path in truth_paths:
        path.chmod(0)
    freeze: dict[str, Any] = {"runs": {}, "ground_truth_permissions_during_candidate_execution": "000"}
    try:
        for run_id in RUN_SEEDS:
            inp = workspace / "runner" / f"{run_id}.jsonl"
            out = workspace / "predictions" / f"{run_id}.jsonl"
            out.parent.mkdir(parents=True, exist_ok=True)
            cmd = [sys.executable, "-m", "evaluation.v11q.runner", str(inp), str(out)]
            env = dict(os.environ)
            env["PYTHONPATH"] = f"{ROOT / 'src'}:{ROOT}"
            try:
                subprocess.check_call(cmd, cwd=ROOT, env=env)
            except subprocess.CalledProcessError as exc:
                incident_dir = workspace / "incidents"
                incident_dir.mkdir(parents=True, exist_ok=True)
                incident = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "run_id": run_id,
                    "failure_reason": "runner_crash",
                    "evidence": f"exit_code={exc.returncode}",
                    "labels_exposed": False,
                    "candidate_changed": False,
                    "seed_changed": False,
                    "dataset_changed": False,
                    "authorized_retry": True,
                    "retry_result": "PENDING",
                }
                incident_path = incident_dir / f"INFRASTRUCTURE_RETRY_{run_id}.json"
                write_json(incident_path, incident)
                subprocess.check_call(cmd, cwd=ROOT, env=env)
                incident["retry_result"] = "PASS"
                write_json(incident_path, incident)
            freeze["runs"][run_id] = {
                "runner_input_sha256": sha256_file(inp),
                "prediction_sha256": sha256_file(out),
                "predictions_frozen_before_ground_truth_unlock": True,
            }
    finally:
        for path in truth_paths:
            path.chmod(0o600)
    write_json(workspace / "PREDICTION_FREEZE_MANIFEST.json", freeze)
    return freeze


def _terminal_state(integrity: dict[str, Any], evidence_valid: bool, aggregate: dict[str, Any]) -> str:
    if integrity.get("research_integrity") != "PASS":
        return "CANDIDATE_V11 QUALIFICATION INVALID — NO_ARCHITECTURE_CONCLUSION"
    if not evidence_valid:
        return "CANDIDATE_V11 QUALIFICATION INVALID — NO_ARCHITECTURE_CONCLUSION"
    if aggregate.get("all_scientific_criteria_pass") is True:
        return "CANDIDATE_V11 QUALIFICATION PASS — FRESH_CONFIRMATORY_AUTHORIZED"
    return "CANDIDATE_V11 QUALIFICATION FAIL — LINEAGE_TERMINATED"


def _next_action(terminal: str) -> str:
    if "PASS" in terminal:
        return "Create a separate Candidate-v11 Fresh Confirmatory Evaluation Mission without reusing V11Q protected examples."
    if "FAIL" in terminal:
        return "Terminate Candidate-v11 and start a new Candidate-v12 architecture-development lineage using only declassified aggregate/family-level findings."
    return "Repair or replace the invalid qualification infrastructure without drawing an architecture conclusion, then establish a new preregistered independent qualification execution."


def _write_final_report(scores: dict[str, Any], integrity: dict[str, Any], evidence_valid: bool, terminal: str, protected_examples: int, regression_status: str, test_status: str) -> None:
    aggregate = scores["aggregate"]
    per_run = scores["per_run"]
    prereg_audit = integrity["preregistration"]
    terminal_record = {
        "candidate": CANDIDATE_ID,
        "candidate_source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "qualification_branch": "research/candidate-v11-independent-qualification",
        "preregistration_commit": prereg_audit.get("preregistration_commit"),
        "preregistration_hash": sha256_file(PREREG_DIR / "V11Q_PREREGISTRATION.json"),
        "protected_raw_example_access_by_candidate_runner": "NONE",
        "v7r_protected_raw_example_access": integrity["v7r_protected_raw_example_access_by_v11q"],
        "candidate_v11_development_example_access_during_protected_generation": integrity["candidate_v11_development_example_access_during_generation"],
        "candidate_mutation": not integrity["candidate_immutable"]["pass"],
        "qualification_runs": len(per_run),
        "protected_examples": protected_examples,
        "existing_repository_regression": regression_status,
        "qualification_infrastructure_tests": test_status,
        "research_integrity": integrity["research_integrity"],
        "qualification_evidence_valid": evidence_valid,
        "terminal_state": terminal,
        "next_scientifically_authorized_action": _next_action(terminal),
    }
    write_json(ARTIFACTS / "TERMINAL_DECISION.json", terminal_record)

    lines = [
        "# Candidate-v11B Independent Protected Qualification — Final Report", "",
        f"Terminal state: **{terminal}**", "",
        f"Protected examples: {protected_examples}",
        f"Research integrity: {integrity['research_integrity']}",
        f"Qualification evidence valid: {evidence_valid}",
        f"Repository regression: {regression_status}",
        f"Qualification infrastructure tests: {test_status}", "",
        "## Q1–Q5 Fresh OOD Macro-F1", "",
    ]
    for run_id in sorted(per_run):
        lines.append(f"- {run_id}: {per_run[run_id]['fresh_ood_macro_f1']:.10f}")
    lines += [
        "", "## Pooled qualification metrics", "",
        f"- Fresh OOD Macro-F1: {aggregate['fresh_ood_macro_f1']:.10f}",
        f"- Exact latent-state reconstruction: {aggregate['exact_latent_state_reconstruction']:.10f}",
        f"- Mean factor accuracy: {aggregate['mean_factor_accuracy']:.10f}",
        f"- ACT-critical factor accuracy: {aggregate['act_critical_factor_accuracy']:.10f}",
        f"- Critical UNKNOWN rate: {aggregate['critical_unknown_rate']:.10f}",
        f"- False UNKNOWN rate: {aggregate['false_unknown_rate']:.10f}",
        f"- Legitimate UNKNOWN recall: {aggregate['legitimate_unknown_recall']:.10f}",
        f"- Counterfactual exact-pair: {aggregate['counterfactual_exact_pair']:.10f}",
        f"- Invariance action consistency: {aggregate['invariance_action_consistency']:.10f}",
        f"- ACT precision: {aggregate['act_precision']:.10f}",
        f"- ACT recall: {aggregate['act_recall']:.10f}",
        f"- Forbidden ACT: {aggregate['forbidden_act']}",
        f"- Invalid action: {aggregate['invalid_action']}",
        f"- Catastrophic collapse: {aggregate['catastrophic_collapse']}", "",
        "## Family Macro-F1", "",
    ]
    for family in FAMILIES:
        lines.append(f"- {family}: {aggregate['family_macro_f1'][family]:.10f}")
    lines += ["", "## Scientific criteria", ""]
    for criterion, passed in aggregate["criteria"].items():
        lines.append(f"- {criterion}: {'PASS' if passed else 'FAIL'}")
    lines += ["", "## Next scientifically authorized action", "", _next_action(terminal), ""]
    (ARTIFACTS / "FINAL_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def execute() -> int:
    if (ARTIFACTS / "TERMINAL_DECISION.json").exists():
        print("Terminal qualification evidence already exists; score-driven rerun is forbidden.")
        return 0
    if verify() != 0:
        return 2
    if not (EVAL_DIR / "AUTHORIZED").exists():
        raise RuntimeError("qualification execution is not authorized")

    workspace = Path(os.environ.get("V11Q_WORKSPACE", "/tmp/v11q-protected"))
    selected_attempt: int | None = None
    leakage: dict[str, Any] | None = None
    manifest: dict[str, Any] | None = None
    for attempt in range(3):
        manifest = build_all(workspace, construction_attempt=attempt)
        leakage = leakage_audit(ROOT, workspace)
        if leakage["pass"]:
            selected_attempt = attempt
            break
    if selected_attempt is None or manifest is None or leakage is None:
        raise RuntimeError("unable to construct zero-overlap protected set before prediction; no candidate prediction executed")

    runner_audit = audit_runner_inputs(workspace)
    if not runner_audit["pass"]:
        raise RuntimeError("runner input isolation violation before prediction")
    prediction_freeze = _run_predictions(workspace)
    scores = score_all(workspace, ARTIFACTS)

    shutil.copy2(workspace / "PROTECTED_DATA_MANIFEST.json", ARTIFACTS / "PROTECTED_DATA_MANIFEST.json")
    shutil.copy2(workspace / "LEAKAGE_AUDIT.json", ARTIFACTS / "LEAKAGE_AUDIT.json")
    write_json(ARTIFACTS / "RUNNER_ISOLATION_AUDIT.json", runner_audit)

    integrity = integrity_audit(ROOT, workspace, IMMUTABLE_MANIFEST)
    write_json(ARTIFACTS / "INTEGRITY_AUDIT.json", integrity)
    regression_status = os.environ.get("V11Q_REGRESSION_STATUS", "UNKNOWN")
    test_status = os.environ.get("V11Q_TEST_STATUS", "UNKNOWN")
    protected_examples = int(manifest["total_examples"])
    evidence_valid = bool(
        integrity["pass"]
        and regression_status == "PASS"
        and test_status == "PASS"
        and protected_examples >= 1750
        and len(prediction_freeze["runs"]) == 5
        and leakage["exact_text_overlap"] == 0
        and leakage["normalized_exact_overlap"] == 0
    )
    terminal = _terminal_state(integrity, evidence_valid, scores["aggregate"])

    incidents = []
    incident_src = workspace / "incidents"
    incident_dst = ARTIFACTS / "incidents"
    if incident_src.exists():
        incident_dst.mkdir(parents=True, exist_ok=True)
        for path in sorted(incident_src.glob("*.json")):
            shutil.copy2(path, incident_dst / path.name)
            incidents.append(path.name)

    reproducibility = {
        "protocol": PROTOCOL_VERSION,
        "candidate_source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "seeds": RUN_SEEDS,
        "construction_attempt": selected_attempt,
        "protected_manifest_sha256": sha256_file(workspace / "PROTECTED_DATA_MANIFEST.json"),
        "prediction_freeze": prediction_freeze,
        "preregistration_json_sha256": sha256_file(PREREG_DIR / "V11Q_PREREGISTRATION.json"),
        "scorer_sha256": sha256_file(EVAL_DIR / "scorer.py"),
        "builder_sha256": sha256_file(EVAL_DIR / "protected_builder.py"),
        "runner_sha256": sha256_file(EVAL_DIR / "runner.py"),
        "incidents": incidents,
        "raw_protected_data_committed": False,
    }
    write_json(ARTIFACTS / "REPRODUCIBILITY_REPORT.json", reproducibility)
    _write_final_report(scores, integrity, evidence_valid, terminal, protected_examples, regression_status, test_status)

    lineage = json.loads((ARTIFACTS / "LINEAGE_MANIFEST.json").read_text(encoding="utf-8"))
    lineage.update({"qualification_executed": True, "research_integrity": integrity["research_integrity"], "terminal_decision": terminal})
    write_json(ARTIFACTS / "LINEAGE_MANIFEST.json", lineage)

    print(json.dumps({"terminal_state": terminal, "evidence_valid": evidence_valid, "protected_examples": protected_examples}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("freeze", "verify", "execute"))
    args = parser.parse_args()
    if args.command == "freeze":
        return freeze()
    if args.command == "verify":
        return verify()
    return execute()


if __name__ == "__main__":
    raise SystemExit(main())
