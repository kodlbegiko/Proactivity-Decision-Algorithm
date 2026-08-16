# Candidate-v7 Terminal Report

## Terminal State
`CANDIDATE_V7 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`

## Candidate
- architecture: V7-B
- OOD threshold: 0.15
- candidate freeze commit: `545af659abd420843e7b5313f4daf0de4d3ac95a`
- model hash: `ca158e66b1c11e159d6cfc0b5ff014a1ce329bbf5b3812b551d3a0cf1f640945`
- safety gate hash: `0791ff39487b0d87e9385c11eadc6af64c69ebbde5112a25426f9e78d32841fd`
- representation hash: `a9ad4b84e95c5522f38b9a02b99acb7806ca464b76e95d08014582901e979ca2`

## Validation
- accuracy: 1.000000
- Macro-F1: 1.000000
- per-action recall: {"ACT": 1.0, "ASK": 1.0, "IGNORE": 1.0, "NOTIFY": 1.0, "SUGGEST": 1.0, "WAIT": 1.0}
- ACT recall: 1.000000
- exact-state accuracy: 1.000000
- critical factor accuracy: 1.000000
- false certainty: 0.000000
- critical false-positive rate: 0.000000

## Development Holdouts
- dev_ood: FAIL
- lexical: PASS
- rendering: FAIL
- compositional: PASS
- ood: FAIL
- counterfactual: FAIL
- invariance: FAIL
- uncertainty: PASS
- safety_challenge: FAIL
- negation: PASS
- supersession: FAIL
- contradiction: PASS

## ACT Safety
- validation forbidden ACT: 0
- validation false ACT: 0
- ACT recall: 1.000000
- critical-factor false-positive: 0.000000
- counterfactual ACT-disable: 1.0

## Protected
Not executed.

## Integrity
- historical protected individual evidence accessed: NO
- historical protected evidence used for development: NO
- candidate frozen before first holdout: YES
- candidate modified after holdout: NO
- protected generator frozen before seed: NOT_APPLICABLE
- protected generated after candidate freeze: NO
- formal protected rerun: NO
- leakage detected: NO

## Supported Claims
- Benchmark-bounded claims only; zero forbidden ACT only where observed in the executed frozen evaluations.

## Not Supported
- production readiness
- universal safety
- human alignment
- unrestricted autonomy
- universal natural-language correctness
- SOTA

## Known Failures
- dev_ood
- rendering
- ood
- counterfactual
- invariance
- safety_challenge
- supersession

## Next Critical Path
Candidate-v8 fresh lineage; do not rescue Candidate-v7.
