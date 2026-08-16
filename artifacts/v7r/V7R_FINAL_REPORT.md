# V7R Final Report

## Terminal state

`V7R REQUALIFICATION FAIL — CANDIDATE_V7_QUALIFICATION_LINEAGE_TERMINATED`

## Frozen candidate

- Candidate: `V7A-01`
- Source commit: `a23d14a9438870314d67d60ce2deda1ebf5b899e`
- Candidate SHA256: `d332d2ccd806b5ea6382a18e11b2ba92a91f3916fdd84dba1b9d2d617853a7fe`
- Research integrity: `PASS`
- Qualification evidence valid: `True`

## Qualification exposure

- Runs: 5
- Fresh protected examples: 1750
- Actual protected-example access: `NONE`
- Legacy exact-text overlap: 0

## Primary metrics

- Fresh OOD Macro-F1: 0.615642
- Worst-run Fresh OOD Macro-F1: 0.585701
- Exact latent-state reconstruction: 0.353799
- Mean factor accuracy: 0.782771
- ACT-critical factor accuracy: 0.754400
- Critical UNKNOWN rate: 0.640571
- False UNKNOWN rate: 0.397272
- Counterfactual exact-pair: 0.291429
- Invariance action consistency: 0.885714
- ACT precision: 1.000000
- ACT recall: 0.380000
- Forbidden ACT: 0
- Invalid action: 0
- Catastrophic collapse in any run: False

## Family Macro-F1

- Lexical: 0.082051
- Rendering: 1.000000
- Compositional: 1.000000
- Negation: 0.388118
- Scope: 0.060109
- Temporal: 0.808653
- Mixed Adversarial: 0.477904

## Decision basis

Scientific acceptance failures: `['Q1:Lexical_macro_f1', 'Q1:Mixed Adversarial_macro_f1', 'Q1:Negation_macro_f1', 'Q1:Scope_macro_f1', 'Q1:Temporal_macro_f1', 'Q1:act_critical_factor_accuracy', 'Q1:act_recall', 'Q1:counterfactual_exact_pair', 'Q1:critical_unknown_rate', 'Q1:exact_latent_state_reconstruction', 'Q1:fresh_ood_macro_f1', 'Q1:invariance_action_consistency', 'Q1:mean_factor_accuracy', 'Q2:Lexical_macro_f1', 'Q2:Mixed Adversarial_macro_f1', 'Q2:Negation_macro_f1', 'Q2:Scope_macro_f1', 'Q2:Temporal_macro_f1', 'Q2:act_critical_factor_accuracy', 'Q2:act_recall', 'Q2:counterfactual_exact_pair', 'Q2:critical_unknown_rate', 'Q2:exact_latent_state_reconstruction', 'Q2:fresh_ood_macro_f1', 'Q2:invariance_action_consistency', 'Q2:mean_factor_accuracy', 'Q3:Lexical_macro_f1', 'Q3:Mixed Adversarial_macro_f1', 'Q3:Negation_macro_f1', 'Q3:Scope_macro_f1', 'Q3:Temporal_macro_f1', 'Q3:act_critical_factor_accuracy', 'Q3:act_recall', 'Q3:counterfactual_exact_pair', 'Q3:critical_unknown_rate', 'Q3:exact_latent_state_reconstruction', 'Q3:fresh_ood_macro_f1', 'Q3:invariance_action_consistency', 'Q3:mean_factor_accuracy', 'Q4:Lexical_macro_f1', 'Q4:Mixed Adversarial_macro_f1', 'Q4:Negation_macro_f1', 'Q4:Scope_macro_f1', 'Q4:Temporal_macro_f1', 'Q4:act_critical_factor_accuracy', 'Q4:act_recall', 'Q4:counterfactual_exact_pair', 'Q4:critical_unknown_rate', 'Q4:exact_latent_state_reconstruction', 'Q4:fresh_ood_macro_f1', 'Q4:invariance_action_consistency', 'Q4:mean_factor_accuracy', 'Q5:Lexical_macro_f1', 'Q5:Mixed Adversarial_macro_f1', 'Q5:Negation_macro_f1', 'Q5:Scope_macro_f1', 'Q5:Temporal_macro_f1', 'Q5:act_critical_factor_accuracy', 'Q5:act_recall', 'Q5:counterfactual_exact_pair', 'Q5:critical_unknown_rate', 'Q5:exact_latent_state_reconstruction', 'Q5:fresh_ood_macro_f1', 'Q5:invariance_action_consistency', 'Q5:mean_factor_accuracy', 'aggregate:Lexical_macro_f1', 'aggregate:Mixed Adversarial_macro_f1', 'aggregate:Negation_macro_f1', 'aggregate:Scope_macro_f1', 'aggregate:Temporal_macro_f1', 'aggregate:act_critical_factor_accuracy', 'aggregate:act_recall', 'aggregate:counterfactual_exact_pair', 'aggregate:critical_unknown_rate', 'aggregate:exact_latent_state_reconstruction', 'aggregate:fresh_ood_macro_f1', 'aggregate:invariance_action_consistency', 'aggregate:mean_factor_accuracy']`

Integrity failures: `[]`

Frozen V7A-01 failed one or more preregistered criteria under a valid fresh independent multi-run qualification. This is scientific qualification failure, not infrastructure invalidity.

## Authorization boundary

- Fresh Confirmatory: `NOT_AUTHORIZED`
- Candidate-v8 development: `SCIENTIFICALLY_JUSTIFIED`
- Gate G: `NOT_EXECUTED`

## Next scientifically authorized action

Open Candidate-v8 development as a completely new scientific lineage.
