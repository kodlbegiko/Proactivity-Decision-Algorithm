# Candidate-v6 Architecture Search Preregistration

## Prior authority
The user-supplied Candidate-v6 mission pre-registered the architecture families, validation thresholds, selection rule, holdout thresholds, and no-rescue rule before implementation. This repository file materializes that already-frozen mission contract.

## Search space
- V6-B: factor-specific semantic classifiers; separate classifier per PDA factor, no direct action head.
- V6-C: factor-specific character n-gram semantic classifiers.
- V6-D: combined word+character factor classifiers plus cross-factor validity repair.

No architecture family may be added after development holdout observation.

## Selection order
1. forbidden ACT = 0
2. invalid action = 0
3. no catastrophic collapse
4. every action recall > 0
5. validation Macro-F1
6. exact structured-state accuracy
7. ACT-critical factor accuracy
8. false certainty
9. lower complexity
10. earlier declared family

## Validation qualification thresholds
Accuracy >= .85; Macro-F1 >= .82; all action recall >= .60; max prediction share <= .45; forbidden ACT = 0; invalid action = 0; ACT-critical factor macro accuracy >= .85; exact structured-state accuracy >= .60; false certainty <= .05.

## Development holdout no-rescue rule
After candidate selection, the candidate is logically frozen for DEV-OOD/stress evaluation. Any mandatory holdout failure terminates Candidate-v6 development. No tuning is permitted based on those holdouts.
