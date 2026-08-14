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
-> honest baselines
-> frozen candidate validation
-> protected/OOD confirmation
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
Gate E — FORMAL-SOURCE PASS; TERMINAL FREEZE CI PENDING
Gate F — NOT EXECUTED
Gate G — NOT EXECUTED
Gate H — NOT EXECUTED
EVIDENCE-WEIGHTED COMPLETION: 78% AFTER TERMINAL GATE-E FREEZE CI
DO NOT START GATE F BEFORE TERMINAL FREEZE CI
DO NOT MERGE OR RELEASE
```

Gate C is isolated on `research/proactivity-benchmark-v2` and Draft PR #8. It froze `benchmark_v2` at 168 oracle-derived scenarios and validated deterministic regeneration, provenance, candidate/private schema separation, rule/action/prohibition coverage, structural diversity, leakage controls, counterfactual/temporal relations, and group-aware split integrity across Python 3.10/3.11/3.12 CI.

Gate D is isolated on `research/proactivity-baselines-v2` and Draft PR #10. Formal implementation commit `6377d31eaa57f162df68c4c3f89c7b6cb7e0206c` passed GitHub Actions run `31801340084` on Python 3.10, 3.11, and 3.12. Terminal freeze HEAD `cbb73cde89ac74f194c19d52e14379223ddc8c8a` also passed full matrix regression. The strongest honest raw-context baseline is B5 transparent heuristic with validation macro-F1 `0.21452991452991452`.

Gate E is isolated on `research/proactivity-candidate-v2` and Draft PR #12. Preregistration was frozen at `da6f205f4c1aff001b9f24b4782a44a94e885acd`; candidate source was frozen before formal validation at `554da731c962cdbf2ebd63cb65149f393e05b617` with SHA-256 `78d4cbdf6190cd8d87927d4efbce63ef29e3dacb902c44c1b3d5004a290aae5b`. Formal run `31804595710` passed on Python 3.10, 3.11, and 3.12 with byte-identical reports/predictions. Selected `C5_semantic_factor_linear` achieved validation macro-F1 `0.6936507936507935` versus B5 `0.21452991452991452` (delta `+0.479120879120879`), zero forbidden ACT and non-zero recall across all six actions. Paired-bootstrap delta 95% interval: `[0.269140495727183, 0.6969364243570899]`.

Gate-E protected candidate/private payload rows parsed = 0; Gate-F protected/OOD data is not generated yet. Gate-E formal-source PASS is a **validation** result under a controlled synthetic representation. It is not OOD/real-world proof, and Gate F must not start until the Gate-E evidence/documentation freeze HEAD itself passes full regression CI.

The Gate-C candidate-facing context track is synthetic and deterministically rendered from generator-known structured state. Passing Gates C–E establishes measurement/comparison/validation evidence **within this modeled benchmark design**; it does not establish real-world contextual understanding.

## Claim boundary

Protocol v2 studies specification compliance. Current evidence does **not** establish human preference alignment, universal correctness, social acceptability, user satisfaction, ecological validity beyond supported modeled/synthetic conditions, robustness, independent protected/OOD generalization, production readiness, SOTA status, or general assistant superiority.

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

See `docs/protocol_v2.md`, `docs/methodology.md`, `docs/gate_status.md`, `docs/claim_boundaries.md`, `gate_c/freeze_v2.json`, `gate_d/freeze_v2.json`, and `gate_e/freeze_v2.json`.
