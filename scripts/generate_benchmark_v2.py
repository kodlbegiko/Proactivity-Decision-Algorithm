from __future__ import annotations

import argparse
import json
from pathlib import Path

from proactivity.benchmark_v2 import ROOT, frozen_integrity, write_artifacts
from proactivity.benchmark_v2_template_balance import activate as activate_template_balance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "benchmark_v2")
    args = parser.parse_args()
    activate_template_balance()
    integrity = frozen_integrity()
    if not integrity["spec_match"] or not integrity["oracle_match"]:
        raise SystemExit("GATE C — BLOCKED_BY_UPSTREAM_HASH_MISMATCH: " + json.dumps(integrity, sort_keys=True))
    manifest = write_artifacts(args.output_dir)
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
