from pathlib import Path

from proactivity.gate_d_v2 import failure_path_cases, scan_baseline_source, verify_hashes


def test_frozen_benchmark_hashes():
    results = verify_hashes(Path("data/benchmark_v2"))
    assert all(v["match"] for v in results.values())


def test_real_baseline_source_is_clean():
    source = Path("src/proactivity/baselines_v2.py").read_text()
    assert scan_baseline_source(source) == []


def test_boundary_failure_paths():
    assert all(failure_path_cases().values())
