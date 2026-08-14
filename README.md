# Proactivity Decision Algorithm

Research repository for a rigorous, reproducible study of **when an AI system should remain silent, defer, suggest, notify, ask, or act under an explicit intervention-control specification**.

The research target is the proactivity decision layer itself, not a full personal-assistant product.

## Current primary track — Protocol v2

Protocol v2 is specification-grounded:

```text
structured state
-> frozen formal specification
-> deterministic oracle
-> expected intervention mode + trace
-> reproducible benchmark
-> later baseline/candidate evaluation
```

The action vocabulary is:

`IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`

These are discrete intervention-control modes, not a universally valid scalar ordering.

## Current gate status

```text
Gate A — PASS (narrowed)
Gate B — PASS
Gate C — PASS
Gate D — PASS
Gate E — NOT EXECUTED
Gate F — NOT EXECUTED
Gate G — NOT EXECUTED
Gate H — NOT EXECUTED
EVIDENCE-WEIGHTED COMPLETION: 63%
READY FOR GATE E AFTER TERMINAL FREEZE CI
DO NOT MERGE OR RELEASE
```

Gate C is isolated on `research/proactivity-benchmark-v2` and Draft PR #8. It froze `benchmark_v2` at 168 oracle-derived scenarios and validated deterministic regeneration, provenance, candidate/private schema separation, rule/action/prohibition coverage, structural diversity, leakage controls, counterfactual/temporal relations, and group-aware split integrity across Python 3.10/3.11/3.12 CI.

Gate D is isolated on `research/proactivity-baselines-v2` and Draft PR #10. Formal implementation commit `6377d31eaa57f162df68c4c3f89c7b6cb7e0206c` passed GitHub Actions run `31801340084` on Python 3.10, 3.11, and 3.12. All three evidence artifacts contained byte-identical Gate-D reports and predictions. The strongest honest raw-context baseline is B5 transparent heuristic with validation macro-F1 `0.21452991452991452`.

Gate-D PASS establishes comparison-baseline integrity only. It does not establish candidate performance, OOD/protected generalization, robustness, production readiness, human-preference alignment, or universal correctness.

The Gate-C candidate-facing context track is synthetic and deterministically rendered from generator-known structured state. Passing Gates C–D establishes measurement/comparison integrity **within this modeled benchmark design**; it does not establish real-world contextual understanding.

## Claim boundary

Protocol v2 studies specification compliance. It does **not** establish human preference alignment, universal correctness, social acceptability, user satisfaction, ecological validity beyond supported modeled/synthetic conditions, robustness, OOD generalization, or candidate quality unless the corresponding later evidence exists.

The oracle is an executable research policy, not universal human truth. Novelty remains conservatively `PARTIAL NOVELTY ONLY`.

## Historical Protocol v1

Protocol v1 remains preserved as negative/historical evidence:

```text
GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION
Evidence-weighted completion: 25%
```

Protocol v2 does not retroactively convert missing human annotation into a pass.

## Gate sequence

- Gate A — scope, claim boundary, prior art
- Gate B — formal specification validity
- Gate C — oracle and benchmark validity
- Gate D — baseline integrity
- Gate E — PDA candidate evidence
- Gate F — protected / OOD validation
- Gate G — robustness / adversarial / invariant stress testing
- Gate H — ablation / reproducibility / independent reproduction / final claim audit

See `docs/protocol_v2.md`, `docs/methodology.md`, `docs/gate_status.md`, `docs/claim_boundaries.md`, `gate_c/freeze_v2.json`, and `gate_d/freeze_v2.json`.
