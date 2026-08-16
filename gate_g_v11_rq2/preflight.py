from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from .candidate_adapter import CandidateV11Adapter, EXPECTED_FACTORS, EXPECTED_PUBLIC_FIELDS

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BLOBS = {
    "candidate_v11/model.py": "77553f7821113b48a2ffcd368ca23195853f8fb0",
    "candidate_v11/evidence.py": "9f5338e0317bdababc8fbd6c2ebf3e499ac4ce42",
    "spec/proactivity_policy_v2.json": "e34345bf76179d2c989d9da2effaa013792925fe",
}
SENTINELS = (
    "Interface sentinel alpha: a schema-only probe with no scientific label.",
    "Interface sentinel beta: inspect only runtime field names and serializable types.",
)


def git_blob(path: str) -> str:
    proc = subprocess.run(
        ["git", "hash-object", path],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout.strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_candidate_freeze() -> dict[str, dict[str, str]]:
    observed: dict[str, dict[str, str]] = {}
    for rel, expected_blob in EXPECTED_BLOBS.items():
        path = ROOT / rel
        if not path.exists():
            raise RuntimeError(f"Frozen Candidate-critical file missing: {rel}")
        actual_blob = git_blob(rel)
        if actual_blob != expected_blob:
            raise RuntimeError(
                f"Frozen Candidate-critical blob changed: {rel}: {actual_blob} != {expected_blob}"
            )
        observed[rel] = {
            "git_blob": actual_blob,
            "sha256": sha256_file(path),
        }
    return observed


def run_interface_sentinel() -> dict[str, object]:
    adapter = CandidateV11Adapter()
    hashes: list[str] = []
    for prompt in SENTINELS:
        canonical = adapter.predict(prompt)
        if canonical.action not in {"IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT"}:
            raise RuntimeError("Sentinel returned an invalid action representation")
        if tuple(canonical.factors) != EXPECTED_FACTORS:
            raise RuntimeError("Canonical factor ordering/shape changed")
        if canonical.public_field_names != EXPECTED_PUBLIC_FIELDS:
            raise RuntimeError("Candidate public interface contract changed")
        hashes.append(hashlib.sha256(prompt.encode("utf-8")).hexdigest())
    return {
        "sentinel_sha256": hashes,
        "performance_scoring_performed": False,
        "gold_labels_present": False,
    }


def main() -> None:
    result = {
        "candidate_freeze": verify_candidate_freeze(),
        "interface": run_interface_sentinel(),
        "historical_protected_rows_inspected": False,
        "historical_development_rows_inspected": False,
        "previous_gate_g_rows_inspected": False,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
