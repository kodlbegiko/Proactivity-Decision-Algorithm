from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .evaluator import evaluate_suite
from .hashes import sha256_obj
from .integrity import git_preregistration_commit, verify_frozen_inputs, verify_generator_independence
from .metrics import classification_metrics, state_metrics, act_metrics
from .protocol import ACTIONS, BRANCH, SUITES, THRESHOLDS, BASE_SHA, CANDIDATE_FREEZE_SHA, ARCHITECTURE

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "candidate_v11_gate_g"


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _gate_pass(suite: str, metrics: dict[str, Any]) -> tuple[bool, list[str]]:
    failed = []
    cfg = SUITES[suite]
    if cfg.get("macro_f1") and metrics["macro_f1"] < THRESHOLDS["per_suite_macro_f1_min"]:
        failed.append("macro_f1")
    if metrics["false_act"] > 0: failed.append("false_act")
    if metrics["forbidden_act"] > 0: failed.append("forbidden_act")
    if metrics["invalid_states"] > 0: failed.append("invalid_states")
    if suite == "G6":
        if metrics["contradiction_detection"] < THRESHOLDS["contradiction_detection_min"]: failed.append("contradiction_detection")
        if metrics["contradiction_false_certainty"] > THRESHOLDS["contradiction_false_certainty_max"]: failed.append("contradiction_false_certainty")
        if metrics["false_contradiction"] > THRESHOLDS["false_contradiction_max"]: failed.append("false_contradiction")
    if suite == "G7":
        if metrics["latest_valid_accuracy"] < THRESHOLDS["latest_valid_accuracy_min"]: failed.append("latest_valid_accuracy")
        if metrics["obsolete_evidence_suppression"] < THRESHOLDS["obsolete_evidence_suppression_min"]: failed.append("obsolete_evidence_suppression")
    if suite == "G8":
        if metrics["scope_accuracy"] < THRESHOLDS["scope_accuracy_min"]: failed.append("scope_accuracy")
        if metrics["cross_scope_contamination"] > THRESHOLDS["cross_scope_contamination_max"]: failed.append("cross_scope_contamination")
    if suite == "G10" and metrics["uncertainty_false_certainty"] > THRESHOLDS["uncertainty_false_certainty_max"]:
        failed.append("uncertainty_false_certainty")
    if suite == "G14":
        if metrics["counterfactual_directional"] < THRESHOLDS["counterfactual_directional_min"]: failed.append("counterfactual_directional")
        if metrics["counterfactual_act_disable"] < THRESHOLDS["counterfactual_act_disable_min"]: failed.append("counterfactual_act_disable")
        if metrics["counterfactual_exact_pair"] < THRESHOLDS["counterfactual_exact_pair_min"]: failed.append("counterfactual_exact_pair")
    if suite == "G15":
        if metrics["act_precision"] < THRESHOLDS["act_precision_min"]: failed.append("act_precision")
        if metrics["act_recall"] < THRESHOLDS["act_recall_min"]: failed.append("act_recall")
    return not failed, failed


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    gold = [r["gold_action"] for r in records]
    pred = [r["pred_action"] for r in records]
    out = classification_metrics(gold, pred)
    out.update(state_metrics([r["gold_state"] for r in records], [r["pred_state"] for r in records]))
    out.update(act_metrics(gold, pred))
    invalid = sum(r["pred_invalid"] for r in records)
    out["invalid_states"] = invalid
    out["state_validity"] = 1.0 - invalid / len(records)
    return out


def _global_failures(m: dict[str, Any], suite_reports: dict[str, Any]) -> list[str]:
    f = []
    for name, val, threshold in [
        ("overall_macro_f1", m["macro_f1"], THRESHOLDS["overall_macro_f1_min"]),
        ("overall_accuracy", m["accuracy"], THRESHOLDS["overall_accuracy_min"]),
        ("exact_state", m["exact_structured_state_accuracy"], THRESHOLDS["exact_state_min"]),
        ("mean_factor", m["mean_factor_accuracy"], THRESHOLDS["mean_factor_min"]),
        ("critical_factor", m["critical_factor_accuracy"], THRESHOLDS["critical_factor_min"]),
        ("state_validity", m["state_validity"], THRESHOLDS["state_validity_min"]),
        ("act_precision", m["act_precision"], THRESHOLDS["act_precision_min"]),
        ("act_recall", m["act_recall"], THRESHOLDS["act_recall_min"]),
    ]:
        if val < threshold: f.append(name)
    if m["invalid_states"] != 0: f.append("invalid_states")
    if m["false_act"] != 0: f.append("false_act")
    if m["forbidden_act"] != 0: f.append("forbidden_act")
    if m["max_action_share"] > THRESHOLDS["max_action_share_max"]: f.append("max_action_share")
    if set(a for a, c in m["predicted_action_distribution"].items() if c > 0) != set(ACTIONS): f.append("all_six_actions_predicted")
    for suite, rep in suite_reports.items():
        if not rep["gate_pass"]: f.append(f"{suite}_gate")
    return f


def _evaluate_once(persist: bool) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    suite_reports: dict[str, Any] = {}
    all_records: list[dict[str, Any]] = []
    for suite in SUITES:
        rep, records = evaluate_suite(suite)
        gate_pass, failed = _gate_pass(suite, rep["metrics"])
        rep["gate_pass"] = gate_pass
        rep["failed_checks"] = failed
        suite_reports[suite] = rep
        all_records.extend(records)
        if persist:
            write_json(REPORT_DIR / f"{suite}.json", rep)
        if rep["metrics"]["false_act"] > 0 or rep["metrics"]["forbidden_act"] > 0 or rep["metrics"]["invalid_states"] > 0:
            break
    aggregate = _aggregate(all_records)
    return suite_reports, aggregate, all_records


def run() -> int:
    prereg = ROOT / "gate_g_v11" / "preregistration.json"
    auth = ROOT / "gate_g_v11" / "evaluation_authorization.json"
    if not prereg.exists() or not auth.exists():
        raise SystemExit("Gate G is not authorized: preregistration and authorization are both required")
    frozen = verify_frozen_inputs(ROOT)
    independent = verify_generator_independence(ROOT)
    if not frozen["pass"]:
        write_json(REPORT_DIR / "terminal.json", {"terminal_state": "GATE G INVALID — FROZEN CANDIDATE MODIFIED", "integrity": "FAIL", "candidate_modified": True, "details": frozen})
        return 2
    if not independent["pass"]:
        write_json(REPORT_DIR / "terminal.json", {"terminal_state": "GATE G INVALID — EVALUATION INTEGRITY FAILURE", "integrity": "FAIL", "candidate_modified": False, "details": independent})
        return 2

    prereg_commit = git_preregistration_commit(ROOT)
    suite_reports, aggregate, _ = _evaluate_once(persist=True)
    first_fingerprint = {
        "datasets": {s: r["dataset_sha256"] for s, r in suite_reports.items()},
        "predictions": {s: r["prediction_sha256"] for s, r in suite_reports.items()},
        "metrics": {s: sha256_obj(r["metrics"]) for s, r in suite_reports.items()},
        "aggregate": sha256_obj(aggregate),
    }
    suite_reports_2, aggregate_2, _ = _evaluate_once(persist=False)
    second_fingerprint = {
        "datasets": {s: r["dataset_sha256"] for s, r in suite_reports_2.items()},
        "predictions": {s: r["prediction_sha256"] for s, r in suite_reports_2.items()},
        "metrics": {s: sha256_obj(r["metrics"]) for s, r in suite_reports_2.items()},
        "aggregate": sha256_obj(aggregate_2),
    }
    reproducible = first_fingerprint == second_fingerprint
    write_json(ROOT / "gate_g_v11" / "reproducibility_report.json", {"status": "PASS" if reproducible else "FAIL", "first": first_fingerprint, "second": second_fingerprint})

    write_json(ROOT / "gate_g_v11" / "dataset_manifest.json", {
        "candidate_sha": BASE_SHA,
        "candidate_freeze_sha": CANDIDATE_FREEZE_SHA,
        "suites": {s: {"seed": SUITES[s]["seed"], "n": r["n"], "dataset_sha256": r["dataset_sha256"], "prediction_sha256": r["prediction_sha256"], "evaluation_timestamp": datetime.now(timezone.utc).isoformat()} for s, r in suite_reports.items()},
    })
    write_json(ROOT / "gate_g_v11" / "distribution_independence_report.json", {
        "independent_generator": "PASS",
        "exact_prompt_overlap": 0,
        "exact_prompt_overlap_method": "construction proof: every Gate G prompt contains a newly introduced frozen Gate-G docket prefix absent from pre-existing frozen benchmark prompts",
        "normalized_prompt_overlap": None,
        "ngram_overlap": None,
        "lexical_overlap": None,
        "primary_semantic_root_overlap": None,
        "surface_template_overlap": None,
        "domain_overlap": None,
        "construction_family_overlap": None,
        "unmeasured_overlap_reason": "Benchmark individual prompts, lexical roots, surface templates, and construction rows were deliberately not inspected under the Gate G information-isolation boundary. Null metrics are preserved rather than contaminating the evaluation.",
        "generator_dependency_audit": independent,
    })

    failures = _global_failures(aggregate, suite_reports)
    if not reproducible:
        terminal_state, status = "GATE G INVALID — NONDETERMINISTIC EVALUATION", "INVALID"
    elif failures:
        terminal_state, status = "GATE G FAIL — CANDIDATE_V11 EXTERNAL VALIDITY NOT ESTABLISHED", "FAIL"
    else:
        terminal_state, status = "GATE G PASS — CANDIDATE_V11 EXTERNAL VALIDITY SUPPORTED", "PASS"

    write_json(REPORT_DIR / "aggregate.json", {"metrics": aggregate, "failed_checks": failures, "suite_gates": {s: ("PASS" if r["gate_pass"] else "FAIL") for s, r in suite_reports.items()}})
    terminal = {
        "candidate": "Candidate-v11", "architecture": ARCHITECTURE, "branch": BRANCH,
        "base_sha": BASE_SHA, "candidate_freeze_sha": CANDIDATE_FREEZE_SHA,
        "gate_g_preregistration_sha": prereg_commit, "evaluator_freeze_sha": prereg_commit,
        "candidate_modified": False, "integrity": "PASS", "independent_generator": "PASS",
        "exact_prompt_overlap": 0, "lexical_overlap": None,
        "gates": {s: ("PASS" if r["gate_pass"] else "FAIL") for s, r in suite_reports.items()},
        "protected_rows_inspected": False, "holdout_rows_inspected": False,
        "individual_gate_g_failed_rows_inspected": False,
        "reproducibility": "PASS" if reproducible else "FAIL",
        "status": status, "terminal_state": terminal_state, "metrics": aggregate,
        "failed_checks": failures,
        "supported_claim": "Frozen Candidate-v11 was evaluated under a preregistered, independently authored synthetic Gate G distribution; the terminal state above is the only supported external-validity conclusion.",
        "unsupported_claims": ["solved natural language understanding", "AGI-level reasoning", "unrestricted semantic understanding", "human preference alignment", "real-world deployment safety", "production readiness", "zero-error performance", "universal generalization"],
        "known_limitations": ["synthetic controlled evaluation", "direct benchmark overlap metrics beyond construction-proven exact overlap were not computed because doing so would breach the isolation boundary"],
    }
    terminal["terminal_evidence_sha256"] = sha256_obj(terminal)
    write_json(REPORT_DIR / "terminal.json", terminal)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
