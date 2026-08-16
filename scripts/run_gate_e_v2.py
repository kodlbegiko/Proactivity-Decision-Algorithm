from __future__ import annotations

import argparse
import json
from pathlib import Path

from proactivity.gate_d_v2 import stable_json_bytes
from proactivity.gate_e_v2 import run_gate_e


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-root", type=Path, default=Path("data/benchmark_v2"))
    parser.add_argument("--candidate-source", type=Path, default=Path("src/proactivity/candidate_v2.py"))
    parser.add_argument("--frozen-baseline", type=Path, default=Path("gate_d/predictions/B5_transparent_heuristic.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/gate_e_report.json"))
    parser.add_argument("--prediction-dir", type=Path, default=Path("gate_e/predictions"))
    args = parser.parse_args()

    report = run_gate_e(args.benchmark_root, args.candidate_source, args.frozen_baseline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.prediction_dir.mkdir(parents=True, exist_ok=True)
    for name, result in report["candidates"].items():
        (args.prediction_dir / f"{name}.json").write_bytes(stable_json_bytes(result["predictions"]))
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["gate_verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
