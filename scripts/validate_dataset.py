#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from proactivity.schema import Scenario


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    seen: set[str] = set()
    count = 0
    for lineno, line in enumerate(args.path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            scenario = Scenario.from_dict(json.loads(line))
            scenario.validate_safety_consistency()
        except Exception as exc:
            raise SystemExit(f"{args.path}:{lineno}: {exc}") from exc
        if scenario.scenario_id in seen:
            raise SystemExit(f"{args.path}:{lineno}: duplicate scenario_id={scenario.scenario_id}")
        seen.add(scenario.scenario_id)
        count += 1
    print(f"VALID: {count} scenarios; unique_ids={len(seen)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
