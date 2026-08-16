from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .hashes import git_blob_sha
from .protocol import CANDIDATE_EVIDENCE_GIT_BLOB, CANDIDATE_MODEL_GIT_BLOB, SPEC_GIT_BLOB


def verify_frozen_inputs(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    checks = {
        "candidate_v11/model.py": (CANDIDATE_MODEL_GIT_BLOB, git_blob_sha(root / "candidate_v11/model.py")),
        "candidate_v11/evidence.py": (CANDIDATE_EVIDENCE_GIT_BLOB, git_blob_sha(root / "candidate_v11/evidence.py")),
        "spec/proactivity_policy_v2.json": (SPEC_GIT_BLOB, git_blob_sha(root / "spec/proactivity_policy_v2.json")),
    }
    mismatch = {p: {"expected": e, "actual": a} for p, (e, a) in checks.items() if e != a}
    return {"pass": not mismatch, "checks": checks, "mismatch": mismatch}


def verify_generator_independence(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    files = list((root / "gate_g_v11").glob("*.py"))
    violations = []
    prohibited_import = "benchmark" + "_v11"
    for path in files:
        text = path.read_text(encoding="utf-8")
        if prohibited_import in text:
            violations.append(str(path))
    return {"pass": not violations, "prohibited_dependency_files": violations}


def git_preregistration_commit(root: str | Path = ".") -> str | None:
    try:
        cp = subprocess.run(
            ["git", "log", "-n", "1", "--format=%H", "--", "gate_g_v11/preregistration.json"],
            cwd=root, text=True, capture_output=True, check=True,
        )
        return cp.stdout.strip() or None
    except Exception:
        return None
