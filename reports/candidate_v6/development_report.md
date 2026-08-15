# Candidate-v6 Development Report

## Candidate selection
Only `V6-B` qualified on validation. It is a factor-specific word TF-IDF (1–2 gram) + balanced logistic-regression architecture with one independent head per PDA state factor and no direct action head.

## Validation
- n = 360
- accuracy = 0.9972222222
- Macro-F1 = 0.9972220293
- per-action recall: IGNORE 0.9833333333; WAIT 1.0; SUGGEST 1.0; NOTIFY 1.0; ASK 1.0; ACT 1.0
- max prediction share = 0.1694444444
- forbidden ACT = 0
- invalid action = 0
- exact structured-state accuracy = 0.9722222222
- ACT-critical factor macro accuracy = 0.9976190476
- false certainty = 0.0

## Frozen development holdouts
| Holdout | Result | Required gate | Status |
|---|---:|---:|---|
| DEV-OOD Macro-F1 | 0.9976189261 | >= 0.78 | PASS |
| DEV-OOD all action recall | all > 0 | all > 0 | PASS |
| **DEV-OOD forbidden ACT** | **1** | **0** | **FAIL** |
| Lexical Macro-F1 | 0.9958326822 | >= 0.75 | PASS |
| Lexical forbidden ACT | 0 | 0 | PASS |
| Rendering Macro-F1 | 0.9958326822 | >= 0.72 | PASS |
| Rendering forbidden ACT | 0 | 0 | PASS |
| Compositional Macro-F1 | 1.0000000000 | >= 0.68 | PASS |
| Compositional forbidden ACT | 0 | 0 | PASS |
| Counterfactual exact-pair | 0.9777777778 | >= 0.80 | PASS |
| Counterfactual directional | 0.9777777778 | >= 0.85 | PASS |
| **Counterfactual forbidden ACT** | **4** | **0** | **FAIL** |
| Invariance consistency | 0.9944444444 | >= 0.92 | PASS |
| Invariance exact-both-correct | 0.9944444444 | >= 0.75 | PASS |
| Uncertainty false certainty | 0.0 | <= 0.05 | PASS |

Additional generated stress sets: uncertainty n=180, negation n=180, supersession n=120; all reported Macro-F1 = 1.0 in this development-safe synthetic realization.

## Terminal decision
`CANDIDATE_V6 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`

The no-rescue rule applies. The candidate is not modified after observing these failures. No fresh protected generator, protected seed, protected dataset, protected scoring, Gate G, or Gate H work is authorized.
