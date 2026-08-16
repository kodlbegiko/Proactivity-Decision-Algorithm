from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from proactivity.gate_d_v2 import run_gate_d, stable_json_bytes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-root", type=Path, default=Path("data/benchmark_v2"))
    parser.add_argument("--output", type=Path, default=Path("reports/gate_d_report.json"))
    parser.add_argument("--prediction-dir", type=Path, default=Path("gate_d/predictions"))
    args = parser.parse_args()
    report = run_gate_d(args.benchmark_root, Path("src/proactivity/baselines_v2.py"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.prediction_dir.mkdir(parents=True, exist_ok=True)
    if "baselines" in report:
        prediction_hashes = {}
        for name, result in report["baselines"].items():
            payload = stable_json_bytes(result["predictions"])
            path = args.prediction_dir / f"{name}.json"
            path.write_bytes(payload)
            prediction_hashes[name] = hashlib.sha256(payload).hexdigest()
        report["prediction_sha256"] = prediction_hashes
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["gate_verdict"])
    return 0 if report["gate_verdict"] == "GATE D — PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
