from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from .integrity import git_preregistration_commit, verify_frozen_inputs, verify_generator_independence
    from .protocol import SUITES, THRESHOLDS, BASE_SHA, CANDIDATE_FREEZE_SHA
except ImportError:
    from gate_g_v11.integrity import git_preregistration_commit, verify_frozen_inputs, verify_generator_independence
    from gate_g_v11.protocol import SUITES, THRESHOLDS, BASE_SHA, CANDIDATE_FREEZE_SHA

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "candidate_v11_gate_g"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def audit() -> dict[str, Any]:
    findings = []
    frozen = verify_frozen_inputs(ROOT)
    independent = verify_generator_independence(ROOT)
    if not frozen["pass"]: findings.append("candidate_or_spec_hash_mismatch")
    if not independent["pass"]: findings.append("benchmark_generator_dependency")
    prereg_commit = git_preregistration_commit(ROOT)
    if not prereg_commit: findings.append("preregistration_commit_unresolved")
    prereg = _load(ROOT / "gate_g_v11" / "preregistration.json")
    if prereg.get("candidate_sha") != BASE_SHA: findings.append("wrong_candidate_sha")
    if prereg.get("candidate_freeze_sha") != CANDIDATE_FREEZE_SHA: findings.append("wrong_candidate_freeze_sha")
    if prereg.get("thresholds") != THRESHOLDS: findings.append("threshold_drift")

    terminal_path = REPORT_DIR / "terminal.json"
    if terminal_path.exists():
        terminal = _load(terminal_path)
        if terminal.get("candidate_modified") is not False: findings.append("terminal_candidate_modified_flag")
        if terminal.get("protected_rows_inspected") is not False: findings.append("protected_rows_inspected")
        if terminal.get("individual_gate_g_failed_rows_inspected") is not False: findings.append("failed_rows_inspected")

    reports = {s: _load(REPORT_DIR / f"{s}.json") for s in SUITES if (REPORT_DIR / f"{s}.json").exists()}
    if not reports: findings.append("no_suite_reports")
    repro_path = ROOT / "gate_g_v11" / "reproducibility_report.json"
    if not repro_path.exists(): findings.append("missing_reproducibility_report")
    elif _load(repro_path).get("status") != "PASS": findings.append("nonreproducible")

    chronology = {"preregistration_commit": prereg_commit, "checked": False, "pass": None}
    try:
        cp = subprocess.run(["git", "log", "--format=%H", "--", "reports/candidate_v11_gate_g/terminal.json"], cwd=ROOT, text=True, capture_output=True, check=True)
        terminal_commits = [x for x in cp.stdout.splitlines() if x]
        if prereg_commit and terminal_commits:
            first_terminal = terminal_commits[-1]
            anc = subprocess.run(["git", "merge-base", "--is-ancestor", prereg_commit, first_terminal], cwd=ROOT).returncode == 0
            chronology = {"preregistration_commit": prereg_commit, "first_terminal_commit": first_terminal, "checked": True, "pass": anc}
            if not anc: findings.append("preregistration_after_metrics")
        elif prereg_commit and terminal_path.exists():
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
            anc = subprocess.run(["git", "merge-base", "--is-ancestor", prereg_commit, head], cwd=ROOT).returncode == 0
            chronology = {"preregistration_commit": prereg_commit, "evaluation_head": head, "terminal_uncommitted": True, "checked": True, "pass": anc}
            if not anc: findings.append("preregistration_after_metrics")
    except Exception:
        chronology["error"] = "git chronology unavailable"

    result = {
        "status": "PASS" if not findings else "FAIL", "findings": findings,
        "frozen_inputs": frozen, "independent_generator": independent,
        "chronology": chronology, "suite_reports_present": sorted(reports),
        "terminal_state_recomputed": _load(terminal_path).get("terminal_state") if terminal_path.exists() else None,
    }
    (ROOT / "gate_g_v11" / "audit_report.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    r = audit()
    print(json.dumps(r, indent=2, sort_keys=True))
    raise SystemExit(0 if r["status"] == "PASS" else 1)
