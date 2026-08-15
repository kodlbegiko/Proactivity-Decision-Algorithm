# Candidate-v4 Fresh Independent Protected Confirmatory Evaluation — Terminal Report

## Terminal State

`FRESH CONFIRMATORY FAIL — CANDIDATE V4 LINEAGE TERMINATED`

## Frozen identity

- Candidate: `V4B_atom_state_machine_a65`
- Candidate source SHA-256: `66a5a899b7c1c5eea102e96f649db89cce2e9c8a38c8d755a25dddcf6abe492e`
- Preregistration commit: `f8a085808fa21cb852c068f0d10a890ce7dd81a3`
- Protected manifest preregistration commit: `f8a085808fa21cb852c068f0d10a890ce7dd81a3`

## Main protected set

- Accuracy: `0.173333`
- Macro-F1: `0.084594`
- Prediction distribution: `{"ACT": 0, "ASK": 0, "IGNORE": 0, "NOTIFY": 0, "SUGGEST": 56, "WAIT": 544}`
- Maximum class share: `0.906667`
- Per-action recall: `{"ACT": 0.0, "ASK": 0.0, "IGNORE": 0.0, "NOTIFY": 0.0, "SUGGEST": 0.19, "WAIT": 0.85}`
- Invalid actions: `0`

## Counterfactual

- Exact-pair correctness: `0.000000`
- Directionally correct behavior: `0.266667`
- Forbidden ACT: `0`

## Invariance

- Prediction consistency: `0.816667`
- Exact-both correctness: `0.100000`

## Stress tracks

- Lexical stress macro-F1: `0.113399`
- Compositional stress macro-F1: `0.080729`

## ACT safety

- Main ACT precision: `0.000000`
- Main ACT recall: `0.000000`
- Main forbidden ACT: `0`
- Main unsafe ACT rate: `0.000000`
- Main missed-safe-ACT rate: `1.000000`

## Collapse audit

```json
{
  "action_disappearance": [
    "ACT",
    "ASK",
    "IGNORE",
    "NOTIFY"
  ],
  "catastrophic_max_share_collapse": true,
  "catastrophic_three_or_more_zero_recall": true,
  "collapse_detected": true,
  "single_class_collapse": false,
  "two_class_collapse": true,
  "zero_recall_action_count": 4
}
```

## Preregistered criteria

```json
{
  "compositional_each_recall_nonzero": false,
  "compositional_forbidden_act": true,
  "compositional_macro_f1": false,
  "counterfactual_exact_pair": false,
  "counterfactual_forbidden_act": true,
  "fewer_than_three_zero_recall": false,
  "forbidden_act_main": true,
  "invalid_action": true,
  "invariance_consistency": false,
  "invariance_exact_both": false,
  "lexical_each_recall_nonzero": false,
  "lexical_forbidden_act": true,
  "lexical_macro_f1": false,
  "main_accuracy": false,
  "main_each_recall": false,
  "main_macro_f1": false,
  "main_max_share": false,
  "no_catastrophic_max_share": false,
  "no_single_class_collapse": true
}
```

## Integrity

- Integrity errors: `[]`
- Candidate-v3 protected records accessed by confirmatory generator/evaluator: `0 by design and path guard`
- Candidate-v4 development payload imported by confirmatory generator/evaluator: `no`
- Protected generator imports Candidate-v4: `no`

## Gate boundary

Gate G: `NOT EXECUTED`  
Gate H: `NOT EXECUTED`

This result is limited to the preregistered Protocol-v2 specification-grounded research setting. It does not establish production readiness, universal proactivity correctness, human-preference alignment, ecological validity across arbitrary domains, SOTA status, Gate G PASS, or Gate H PASS.
