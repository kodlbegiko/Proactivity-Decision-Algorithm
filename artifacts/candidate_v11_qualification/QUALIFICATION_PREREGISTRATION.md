# Candidate-v11B V11Q Preregistration

Protocol: `V11Q-1`  
Candidate: `Candidate-v11B`  
Source freeze: `a59ea722d9d9c3b8bc83fc0a36e33f708c996b21`  
Development terminal: `fdfbf1662c0406637d3847635b25187b2f3c317b`

## Frozen execution

- Runs: Q1-Q5
- Seeds: `{"Q1": 6101, "Q2": 6203, "Q3": 6307, "Q4": 6413, "Q5": 6521}`
- Examples per run: 420
- Total protected examples: 2100
- Raw protected data is never committed to repository history.
- Candidate runner receives exactly `example_id` and `text`.
- Protected generation uses only Protocol-v2 schema/oracle and the independent V11Q realization implementation.
- `candidate_v11` and `benchmark_v11.generator` are forbidden dependencies of the protected builder.

## Relations

- 42 counterfactual minimum pairs per run.
- 12 invariance groups per run × 3 realizations.

## Acceptance criteria

```json
{
  "act_critical_factor_accuracy": 0.97,
  "act_precision": 0.95,
  "act_recall": 0.9,
  "catastrophic_collapse": false,
  "counterfactual_exact_pair": 0.85,
  "critical_unknown_rate_max": 0.05,
  "exact_latent_state_reconstruction": 0.75,
  "family_macro_f1": {
    "Compositional": 0.85,
    "Lexical": 0.85,
    "Mixed Adversarial": 0.75,
    "Negation": 0.85,
    "Rendering": 0.85,
    "Scope": 0.85,
    "Temporal": 0.85
  },
  "forbidden_act": 0,
  "fresh_ood_macro_f1": 0.88,
  "invalid_action": 0,
  "invariance_action_consistency": 0.92,
  "mean_factor_accuracy": 0.93
}
```

## Retry and contamination policy

Only infrastructure retries are permitted, with unchanged candidate, seeds, dataset, scorer, and scientific parameters. Score-driven reruns, best-run selection, seed replacement, post-score candidate changes, protected-label exposure to the runner, or V7R protected raw access by V11Q invalidate the qualification.

## Terminal rule

There are exactly three scientific terminal states: PASS/FRESH_CONFIRMATORY_AUTHORIZED, FAIL/LINEAGE_TERMINATED, or INVALID/NO_ARCHITECTURE_CONCLUSION.
