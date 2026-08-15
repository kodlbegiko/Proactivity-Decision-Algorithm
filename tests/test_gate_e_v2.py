from proactivity.gate_e_v2 import BOOTSTRAP_SAMPLES, FROZEN_BASELINE_MACRO_F1, MIN_MACRO_DELTA


def test_gate_e_preregistered_constants_are_frozen():
    assert BOOTSTRAP_SAMPLES == 10_000
    assert FROZEN_BASELINE_MACRO_F1 == 0.21452991452991452
    assert MIN_MACRO_DELTA == 0.05
