from __future__ import annotations

import argparse
import json

from proactivity.specification import load_spec
from proactivity.specification.validation import audit_gate_b, gate_b_verdict


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence")
    parser.add_argument("--spec", default="spec/proactivity_policy_v2.json")
    args = parser.parse_args()
    if args.evidence:
        with open(args.evidence, encoding="utf-8") as handle:
            report = json.load(handle)
    else:
        report = audit_gate_b(load_spec(args.spec))
    verdict = gate_b_verdict(report)
    print(verdict)
    return 0 if verdict == "GATE B — PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
