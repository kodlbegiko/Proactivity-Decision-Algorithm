#!/usr/bin/env python3
"""Validate an existing Candidate-v3 freeze manifest and source immutability."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

FREEZE = Path("gate_recovery_v3/freeze.json")
SOURCE = Path("src/proactivity/candidate_v3.py")
EXPECTED_STATUS = "RECOVERY DEVELOPMENT PASS — CANDIDATE V3 FROZEN"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not FREEZE.exists():
        print("CANDIDATE V3 FREEZE IMMUTABILITY = NOT YET APPLICABLE")
        return
    manifest = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert manifest["status"] == EXPECTED_STATUS
    assert manifest["candidate_identity"] == "V3A_factor_tree"
    assert manifest["gate_f_historical_status"] == "FAIL"
    assert manifest["gate_f_retired_protected_records_accessed_by_development"] == 0
    assert manifest["candidate_source_immutable_after_freeze"] is True
    assert SOURCE.exists()
    assert sha256(SOURCE) == manifest["candidate_source_sha256"]
    freeze_commit = manifest["candidate_source_freeze_commit"]
    subprocess.run(["git", "cat-file", "-e", f"{freeze_commit}^{{commit}}"], check=True)
    subprocess.run(["git", "diff", "--exit-code", freeze_commit, "HEAD", "--", str(SOURCE)], check=True)
    print(f"CANDIDATE V3 FREEZE IMMUTABILITY = PASS ({freeze_commit})")


if __name__ == "__main__":
    main()
