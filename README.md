# Proactivity Decision Algorithm

Research repository for a rigorous, reproducible study of **when an AI system should remain silent, defer, suggest, notify, ask, or act under an explicit intervention-control specification**.

The research target is the proactivity decision layer itself, not a full personal-assistant product.

## Current primary track — Protocol v2

Protocol v2 is **specification-grounded**. Its primary evidence chain is:

```text
structured state
-> frozen formal specification
-> deterministic oracle
-> expected intervention mode
-> rule/prohibition trace
-> machine-verifiable evaluation
```

The current research question is whether a deterministic, auditable decision layer can map explicit permission, information, timing, intervention need, side-effect, risk, reversibility, and execution state to one of:

`IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`

while satisfying frozen invariants and counterfactual/temporal consistency checks.

These are discrete intervention-control modes, not a universally valid scalar intensity ordering.

## Claim boundary

Protocol v2 studies **specification compliance**. It does not establish human preference alignment, universal correctness, social acceptability, user satisfaction, or ecological validity outside the modeled conditions. The oracle is the executable reference implementation of a research policy, not universal human truth.

Novelty remains conservatively **PARTIAL NOVELTY ONLY** after comparison with constrained-policy/shielding work and recent proactive-agent research.

## Historical Protocol v1

Protocol v1 used independent human annotation as its primary validity path. Its historical result remains:

```text
GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION
Evidence-weighted completion: 25%
```

The annotation packets, validators, archival helpers, agreement/kappa tooling, historical leakage evidence, and CI incidents remain preserved. Human annotation is now optional future external-validity evidence rather than a blocker for the primary Protocol-v2 sequence.

## Gate sequence

- Gate A — scope, claim boundary, prior art
- Gate B — formal specification validity
- Gate C — oracle and benchmark validity
- Gate D — baseline integrity
- Gate E — PDA candidate evidence
- Gate F — protected / OOD validation
- Gate G — robustness / adversarial / invariant stress testing
- Gate H — ablation / reproducibility / independent reproduction / final claim audit

See `docs/protocol_v2.md`, `docs/methodology.md`, and `docs/gate_status.md` for the authoritative protocol and current verdict.

## Research branch

Protocol-v2 work is conducted on `research/proactivity-specification-v2`. Gate C must not start merely because Gate-B infrastructure exists; it requires an explicit Gate-B PASS and a separate authorization/task.
