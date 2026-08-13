import pytest

from proactivity.evaluation.agreement import cohen_kappa, raw_agreement


def test_perfect_agreement():
    a = ["IGNORE", "WAIT", "ASK"]
    assert raw_agreement(a, a) == 1.0
    assert cohen_kappa(a, a) == 1.0


def test_known_kappa():
    a = ["A", "A", "B", "B"]
    b = ["A", "B", "B", "B"]
    assert raw_agreement(a, b) == 0.75
    assert cohen_kappa(a, b) == pytest.approx(0.5)
