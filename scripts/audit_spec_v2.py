from __future__ import annotations

import argparse
import json
from pathlib import Path

from proactivity.specification import load_spec, spec_sha256
from proactivity.specification.validation import audit_gate_b


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="spec/proactivity_policy_v2.json")
    parser.add_argument("--output")
    args = parser.parse_args()
    spec = load_spec(args.spec)
    report = audit_gate_b(spec)
    report = {
        "policy_id": spec["policy_id"],
        "schema_version": spec["schema_version"],
        "spec_sha256": spec_sha256(args.spec),
        **report,
    }
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["gate_verdict"] == "GATE B — PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
