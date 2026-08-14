from __future__ import annotations

import argparse
import json
from pathlib import Path

from proactivity.benchmark_v2 import ROOT


def decide(report: dict) -> str:
    required = {
        "protocol", "gate", "spec_sha256", "oracle_hash", "benchmark_version",
        "benchmark_sha256", "scenario_count", "unique_ids", "upstream_integrity",
        "ground_truth_provenance", "representation", "diversity", "action_coverage",
        "rule_coverage", "prohibition_coverage", "counterfactual", "temporal",
        "split_integrity", "leakage", "reproducibility", "preregistered_criteria",
        "criteria_failures", "gate_verdict",
    }
    missing = sorted(required - set(report))
    if missing:
        return "GATE C — BLOCKED: INCOMPLETE_MACHINE_REPORT"
    if report.get("protocol") != "PDA Protocol v2" or report.get("gate") != "C":
        return "GATE C — BLOCKED: INVALID_REPORT_IDENTITY"
    upstream = report["upstream_integrity"]
    if not upstream.get("spec_match") or not upstream.get("oracle_match"):
        return "GATE C — BLOCKED: UPSTREAM_INTEGRITY_MISMATCH"
    if report["criteria_failures"]:
        return "GATE C — FAIL: BENCHMARK_VALIDITY_CRITERIA_NOT_MET"
    if report["gate_verdict"] != "GATE C — PASS":
        return "GATE C — BLOCKED: REPORT_DECISION_INCONSISTENCY"
    return "GATE C — PASS"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=ROOT / "reports" / "gate_c_report.json")
    args = parser.parse_args()
    if not args.evidence.exists():
        print("GATE C — BLOCKED: MISSING_EVIDENCE_REPORT")
        return
    try:
        report = json.loads(args.evidence.read_text(encoding="utf-8"))
    except Exception:
        print("GATE C — BLOCKED: UNREADABLE_EVIDENCE_REPORT")
        return
    print(decide(report))


if __name__ == "__main__":
    main()
