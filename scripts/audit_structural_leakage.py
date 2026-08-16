#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

IGNORE_FOR_STRUCTURE = {"scenario_id", "timestamp", "domain"}


def structural_fingerprint(row: dict) -> str:
    reduced = {k: v for k, v in row.items() if k not in IGNORE_FOR_STRUCTURE}
    encoded = json.dumps(reduced, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit exact template duplication across benchmark scenarios")
    parser.add_argument("path", type=Path)
    parser.add_argument("--max-duplicate-member-rate", type=float, default=0.20)
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise SystemExit("No scenarios found")

    counts = Counter(structural_fingerprint(row) for row in rows)
    duplicate_members = sum(count for count in counts.values() if count > 1)
    duplicate_member_rate = duplicate_members / len(rows)

    print(f"scenario_count={len(rows)}")
    print(f"unique_structural_fingerprints={len(counts)}")
    print(f"duplicate_groups={sum(count > 1 for count in counts.values())}")
    print(f"duplicate_members={duplicate_members}")
    print(f"duplicate_member_rate={duplicate_member_rate:.6f}")
    print("duplicate_group_sizes=" + ",".join(map(str, sorted((x for x in counts.values() if x > 1), reverse=True))))
    passed = duplicate_member_rate <= args.max_duplicate_member_rate
    print(f"structural_leakage_gate={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
