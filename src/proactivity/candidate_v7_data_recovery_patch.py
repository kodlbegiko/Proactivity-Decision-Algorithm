"""Candidate-v7 infrastructure retry 002: deterministic formal-state reuse.

The preregistration fixes dataset sizes and generation direction but does not
require every record to use a unique formal Protocol-v2 state. The finite valid
ACT state pool is smaller than the balanced train quota. This repair preserves
the frozen action-balanced sampling plan, seeds, sizes, oracle, and realization
logic while deterministically cycling the ranked formal-state pool when a quota
exceeds the number of distinct valid states.
"""

from . import candidate_v7_data as _data


def _balanced_states_with_reuse(spec, count, seed, *, compositional_only=None):
    pools = {action: [] for action in _data.ACTIONS}
    for state in _data.enumerate_states(spec):
        if not _data.validate_state(spec, state).valid:
            continue
        sig = _data.composition_signature(state)
        if compositional_only is True and sig != 0:
            continue
        if compositional_only is False and sig == 0:
            continue
        result = _data.evaluate(state, spec=spec)
        if result.status == "VALID_DECISION" and result.action in pools:
            pools[result.action].append(dict(state))

    quotas = {action: count // len(_data.ACTIONS) for action in _data.ACTIONS}
    for action in _data.ACTIONS[: count % len(_data.ACTIONS)]:
        quotas[action] += 1

    selected = []
    for action in _data.ACTIONS:
        ranked = sorted(
            pools[action],
            key=lambda state: (
                _data.stable_int(seed, action, _data.canonical_json(state)),
                _data.canonical_json(state),
            ),
        )
        if not ranked:
            raise RuntimeError(f"no valid formal states for required action: {action}")
        selected.extend(dict(ranked[index % len(ranked)]) for index in range(quotas[action]))

    return sorted(
        selected,
        key=lambda state: (
            _data.stable_int(seed, _data.canonical_json(state)),
            _data.canonical_json(state),
        ),
    )


_data._balanced_states = _balanced_states_with_reuse
