from proactivity.decisions import Decision, autonomous, is_intervention


def test_intervention_grouping():
    assert not is_intervention(Decision.IGNORE)
    assert not is_intervention(Decision.WAIT)
    assert is_intervention(Decision.SUGGEST)
    assert is_intervention(Decision.NOTIFY)
    assert is_intervention(Decision.ASK)
    assert is_intervention(Decision.ACT)


def test_only_act_is_autonomous():
    assert autonomous(Decision.ACT)
    assert not autonomous(Decision.ASK)
