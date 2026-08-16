from proactivity.decisions import Decision
from proactivity.utility import PROVISIONAL_PROFILES, safety_penalty


def test_unsafe_act_is_more_severe_than_false_interruption():
    p = PROVISIONAL_PROFILES["balanced"]
    unsafe = safety_penalty(Decision.ASK, Decision.ACT, p)
    nuisance = safety_penalty(Decision.IGNORE, Decision.NOTIFY, p)
    assert unsafe > nuisance


def test_wait_to_notify_counts_as_premature():
    p = PROVISIONAL_PROFILES["balanced"]
    assert safety_penalty(Decision.WAIT, Decision.NOTIFY, p) == p.premature
