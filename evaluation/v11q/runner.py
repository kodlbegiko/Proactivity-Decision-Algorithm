from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from proactivity.candidate_v11 import parse

from .common import ACTIONS, VARIANT, canonical_json, read_jsonl, sha256_file, write_jsonl

ALLOWED_INPUT_KEYS = {"example_id", "text"}


def validate_runner_record(record: dict[str, Any]) -> None:
    if set(record) != ALLOWED_INPUT_KEYS:
        raise ValueError(f"runner input keys must equal {sorted(ALLOWED_INPUT_KEYS)}; got {sorted(record)}")
    if not isinstance(record["example_id"], str) or not isinstance(record["text"], str):
        raise TypeError("runner input example_id and text must be strings")


def predict_record(record: dict[str, Any]) -> dict[str, Any]:
    validate_runner_record(record)
    result = parse(record["text"], variant=VARIANT)
    factor_status = {field: hypothesis.status for field, hypothesis in result.factors.items()}
    return {
        "example_id": record["example_id"],
        "action": result.action,
        "state": result.state,
        "factor_status": factor_status,
    }


def run_file(input_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    input_path = Path(input_path)
    output_path = Path(output_path)
    records = read_jsonl(input_path)
    for record in records:
        validate_runner_record(record)
    predictions = [predict_record(record) for record in records]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_path, predictions)
    return {
        "examples": len(predictions),
        "input_sha256": sha256_file(input_path),
        "prediction_sha256": sha256_file(output_path),
        "allowed_input_keys": sorted(ALLOWED_INPUT_KEYS),
        "variant": VARIANT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    meta = run_file(args.input, args.output)
    print(canonical_json(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
