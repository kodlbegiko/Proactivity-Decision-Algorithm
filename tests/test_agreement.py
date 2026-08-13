import pytest

from proactivity.evaluation.agreement import cohen_kappa, cohen_kappa_diagnostic, raw_agreement


def test_perfect_agreement():
    a = ["IGNORE", "WAIT", "ASK"]
    assert raw_agreement(a, a) == 1.0
    assert cohen_kappa(a, a) == 1.0
    assert cohen_kappa_diagnostic(a, a) == (1.0, None)


def test_known_kappa():
    a = ["A", "A", "B", "B"]
    b = ["A", "B", "B", "B"]
    assert raw_agreement(a, b) == 0.75
    assert cohen_kappa(a, b) == pytest.approx(0.5)


def test_constant_class_kappa_is_flagged_as_degenerate():
    value, warning = cohen_kappa_diagnostic(["WAIT"] * 12, ["WAIT"] * 12)
    assert value is None
    assert warning == "DEGENERATE_EXPECTED_AGREEMENT_1_SINGLE_CLASS"
