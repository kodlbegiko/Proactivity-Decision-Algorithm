from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_candidate_boundary_v2 import validate_source

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "gate_c" / "representation_contract_v2.json").read_text(encoding="utf-8"))


def test_clean_candidate_source_passes_boundary_guard():
    source = "def decide(observation, domain):\n    return 'WAIT' if not observation else 'SUGGEST'\n"
    result = validate_source(source, CONTRACT)
    assert result == {"forbidden_imports": [], "forbidden_paths": [], "pass": True}


def test_candidate_importing_frozen_oracle_fails_boundary_guard():
    source = "from proactivity.specification import evaluate\n\ndef decide(state):\n    return evaluate(state).action\n"
    result = validate_source(source, CONTRACT)
    assert result["pass"] is False
    assert "proactivity.specification" in result["forbidden_imports"]


def test_candidate_reading_oracle_private_artifact_fails_boundary_guard():
    source = "from pathlib import Path\nDATA = Path('data/benchmark_v2/private.jsonl').read_text()\n"
    result = validate_source(source, CONTRACT)
    assert result["pass"] is False
    assert "data/benchmark_v2/private.jsonl" in result["forbidden_paths"]
