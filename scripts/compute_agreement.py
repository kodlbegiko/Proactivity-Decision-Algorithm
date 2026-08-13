#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from proactivity.evaluation.agreement import cohen_kappa, raw_agreement


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute preferred-action agreement for two independent labelers")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--labeler-a", default="labeler_a")
    parser.add_argument("--labeler-b", default="labeler_b")
    args = parser.parse_args()

    a, b = [], []
    with args.csv_path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get(args.labeler_a) and row.get(args.labeler_b):
                a.append(row[args.labeler_a].strip())
                b.append(row[args.labeler_b].strip())
    if not a:
        raise SystemExit("No complete paired labels found")

    raw = raw_agreement(a, b)
    kappa = cohen_kappa(a, b)
    print(f"n={len(a)}")
    print(f"raw_agreement={raw:.6f}")
    print(f"cohen_kappa={kappa:.6f}")
    print(f"gate_raw={'PASS' if raw >= 0.80 else 'FAIL'}")
    print(f"gate_kappa={'PASS' if kappa >= 0.60 else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
