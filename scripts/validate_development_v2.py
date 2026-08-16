from __future__ import annotations

import json
from pathlib import Path

from proactivity.specification import evaluate, load_spec, spec_sha256

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec/proactivity_policy_v2.json"
DATA = ROOT / "data/development/development_v2.jsonl"


def main() -> None:
    spec = load_spec(SPEC)
    sha = spec_sha256(SPEC)
    rows = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids: set[str] = set()
    for row in rows:
        if row["scenario_id"] in ids:
            raise SystemExit("duplicate scenario_id")
        ids.add(row["scenario_id"])
        if row["spec_sha256"] != sha or row["spec_version"] != spec["schema_version"]:
            raise SystemExit("spec version/hash mismatch")
        result = evaluate(row["state"], spec_path=SPEC)
        if result.status != "VALID_DECISION" or result.action != row["oracle_action"] or result.matched_rule != row["matched_rule"]:
            raise SystemExit("oracle mismatch")
    expected = {"IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT"}
    if {row["oracle_action"] for row in rows} != expected:
        raise SystemExit("all six actions must be represented in development_v2 reachability coverage")
    print(f"validated={len(rows)} unique_ids={len(ids)}")


if __name__ == "__main__":
    main()
