# Proactivity Decision Algorithm

Research repository for a rigorous, reproducible study of **when an AI system should remain silent, defer, suggest, notify, ask, or act under an explicit intervention-control specification**. The target is the proactivity decision layer, not a full personal-assistant product.

## Protocol v2 status

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
READY FOR GATE E
DO NOT MERGE OR RELEASE
```

Gate D is frozen on `research/proactivity-baselines-v2` / Draft PR #10. Formal source commit `6377d31eaa57f162df68c4c3f89c7b6cb7e0206c` passed GitHub Actions run `31801340084` on Python 3.10, 3.11, and 3.12. All three evidence artifacts contained byte-identical Gate-D reports and predictions. The strongest honest raw-context baseline is B5 transparent heuristic with validation macro-F1 `0.21452991452991452`.

Gate-D PASS establishes **comparison-baseline integrity only**. It does not establish candidate performance, OOD/protected generalization, robustness, production readiness, human-preference alignment, or universal correctness.

The frozen action vocabulary is `IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`; these are discrete intervention-control modes, not a universally valid scalar ordering.

## Claim boundary

Protocol v2 studies specification compliance. The oracle is an executable research policy, not universal human truth. The raw-context benchmark is synthetic and deterministically rendered from generator-known structured state. Passing Gates B–D does not establish unrestricted natural-language understanding or ecological validity.

## Historical Protocol v1

Protocol v1 remains preserved as negative/historical evidence: `GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION`, 25% v1 evidence-weighted completion. Missing human annotation is not retroactively converted into a pass.

## Gate sequence

- Gate A — scope, claim boundary, prior art
- Gate B — formal specification validity
- Gate C — oracle and benchmark validity
- Gate D — baseline integrity
- Gate E — PDA candidate evidence
- Gate F — protected / OOD validation
- Gate G — robustness / adversarial / invariant stress testing
- Gate H — ablation / reproducibility / independent reproduction / final claim audit

See `docs/gate_status.md`, `docs/research_log.md`, `docs/methodology.md`, `docs/claim_boundaries.md`, `gate_c/freeze_v2.json`, and `gate_d/freeze_v2.json`.
