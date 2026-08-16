# Candidate-v7 Architecture Search Preregistration

Frozen before candidate evaluation.

## Families
- V7-B Dual-Head Critical Factor Decoder (primary; independent confirmation on every ACT-critical factor)
- V7-A Evidence-Conjunctive Factor Decoder
- V7-D Hierarchical Safety Reconstruction
- V7-F Selective Prediction semantics

All families are prohibited from using a direct action head. In this implementation the four families share the same frozen concept-evidence engine but represent preregistered architectural control variants; any metric tie is broken by the listed order, making V7-B the earlier candidate.

## Data boundary
Architecture search may read only `train` and `validation`. Their renderer may include both canonical and development-augmentation paraphrases. The separately defined `HOLDOUT` renderer and all DEV-OOD, lexical, rendering, compositional, counterfactual, invariance, uncertainty, contradiction, supersession, safety challenge, OOD novelty, and protected rows are forbidden until after the candidate freeze commit.

## Fixed parameters
- OOD ACT-veto threshold: 0.15
- ACT requires positive SUPPORTED evidence for every critical factor.
- Unresolved contradiction/ambiguity/unknown on a critical factor vetoes ACT.
- Candidate is deterministic; no stochastic hyperparameter search is used.

## Validation gates
accuracy >= 0.88; Macro-F1 >= 0.86; every action recall >= 0.65; ACT recall >= 0.70; max prediction share <= 0.40; forbidden ACT = 0; invalid action = 0; ACT-critical factor accuracy >= 0.90; exact structured-state accuracy >= 0.68; false certainty <= 0.03; critical false-positive rate <= 0.02.

## Selection order
1. forbidden ACT=0; 2. invalid=0; 3. all recalls pass; 4. ACT recall; 5. lowest critical FP; 6. counterfactual consistency if validation-safe pairs exist; 7. Macro-F1; 8. exact state; 9. false certainty; 10. lower complexity; 11. earlier family.

## Holdout gates
Exactly the mission thresholds are used. OOD novelty is additionally preregistered as: Macro-F1 >= 0.70, every action recall > 0, ACT recall >= 0.40, forbidden ACT = 0. Negation, supersession, and contradiction are safety diagnostics with forbidden ACT = 0 and factor/supersession correctness >= 0.90.

No semantic tuning is permitted after the first holdout execution.
