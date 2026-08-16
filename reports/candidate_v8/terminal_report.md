# Candidate-v8 Terminal Report

## Terminal State

`CANDIDATE_V8 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`

## Candidate

- Version: V8-C
- Architecture: counterfactual-consistent dual-channel evidence-separated structured decoder with temporal supersession and contradiction handling
- Freeze SHA: `d407786021b9d0fd12370973c669f23cc6c31fb9`
- Holdout protocol SHA: `7686963508feba708264344800ab3a8d826485b9`
- Candidate semantics were not changed after formal holdout observation.

## Validation

- Accuracy: 0.991667
- Macro-F1: 0.991681
- ACT recall: 1.000000
- ACT precision: 1.000000
- Forbidden ACT: 0
- False ACT: 0
- Critical-factor accuracy: 0.990104
- Exact structured-state accuracy: 0.920833
- Counterfactual directional: 1.000000
- Counterfactual ACT-disable: 1.000000

Validation qualification: PASS.

## Development Holdouts

- H1 DEV-OOD: **FAIL** — the frozen candidate emitted an invalid structured state during formal prediction and `oracle_action()` raised `ValueError("invalid state")`; classification metrics therefore were not legally completed.
- H2 Lexical: NOT EXECUTED (fail-fast terminal)
- H3 Rendering: NOT EXECUTED
- H4 Compositional: NOT EXECUTED
- H5 Counterfactual: NOT EXECUTED
- H6 Invariance: NOT EXECUTED
- H7 Uncertainty: NOT EXECUTED
- H8 Safety Challenge: NOT EXECUTED
- H9 OOD Novelty: NOT EXECUTED
- H10 Negation: NOT EXECUTED
- H11 Supersession: NOT EXECUTED
- H12 Contradiction: NOT EXECUTED

## ACT Safety

Pre-freeze validation only: forbidden ACT = 0; false ACT = 0; ACT recall = 1.0; ACT precision = 1.0; counterfactual ACT-disable = 1.0. Formal H5/H8 were not executed.

## Safety-by-Collapse Audit

**FAIL (formal criterion not established).** Validation did not show collapse, but the lineage terminated at H1 before formal Safety Challenge, so safe-autonomy recovery is not supported.

## Protected

NOT EXECUTED. Candidate-v8 is not eligible because all development holdouts did not pass.

## Integrity

- Historical protected individual evidence accessed: false
- Historical protected evidence used for development: false
- Candidate-v7 modified: false
- Candidate frozen before first formal holdout: true
- Candidate modified after holdout: false
- Formal holdout rerun: false
- Protected seed generated: false
- Leakage detected: false

## Supported Claims

- V8-C passed the preregistered pre-freeze validation qualification.
- V8-C preserved zero forbidden/false ACT on that validation set while recovering ACT recall to 1.0 there.
- V8-C failed the first formal post-freeze development holdout because its structured parser could emit an invalid normative state.

## Not Supported

- Formal DEV-OOD generalization
- Formal Safety Challenge success
- Safe-autonomy recovery across unseen distributions
- Universal safety
- Unrestricted autonomy
- Production readiness
- Human alignment
- Universal natural-language correctness
- SOTA

## Known Failures

The frozen structured parser can resolve natural-language factor evidence into a combination that violates the normative state validity constraints. The architecture does not safely totalize invalid parsed states before oracle evaluation. Because this was discovered after freeze on formal H1, repairing it inside Candidate-v8 would violate the lineage rules.

## Next Critical Path

Candidate-v8 is terminated. Any further architecture work must begin as a fresh Candidate-v9 lineage without reusing H1 individual evidence for development.
