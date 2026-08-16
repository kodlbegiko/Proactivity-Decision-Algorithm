#!/usr/bin/env python3
"""Materialize the preregistered Candidate-v4 development-safe datasets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from proactivity.recovery_v4_data import (
    build_counterfactual_pairs,
    build_invariance_pairs,
    build_splits,
    generation_manifest,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/candidate_v4_development")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    splits = build_splits()
    for split, records in splits.items():
        _write_jsonl(output_dir / f"{split}.jsonl", records)
    _write_jsonl(output_dir / "counterfactual_pairs.jsonl", build_counterfactual_pairs())
    _write_jsonl(output_dir / "invariance_pairs.jsonl", build_invariance_pairs())
    (output_dir / "manifest.json").write_text(
        json.dumps(generation_manifest(), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(generation_manifest(), ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
