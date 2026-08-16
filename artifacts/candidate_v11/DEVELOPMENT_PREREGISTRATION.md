# Candidate-v11 Development Preregistration

## Boundary
No V7R protected raw examples may be read or used.

## Architecture search
Compare variants A/B/C on fresh formal-state -> semantic-plan -> realization development data.

Selection dimensions: OOD Macro-F1, latent reconstruction, lexical/scope/negation robustness, UNKNOWN calibration, counterfactual exact-pair, invariance, ACT precision/recall, forbidden ACT, collapse.

Tie-break: if scientific metrics are effectively tied, choose the lower-complexity architecture.

## Gates
- Exact latent reconstruction >= 0.80
- Mean factor accuracy >= 0.95
- ACT-critical factor accuracy >= 0.97
- Lexical/Negation/Scope/Temporal/Compositional >= 0.88
- Mixed Adversarial >= 0.82
- Counterfactual exact-pair >= 0.88
- Invariance action consistency >= 0.95
- Critical UNKNOWN <= 0.05
- False UNKNOWN <= 0.08
- Legitimate UNKNOWN recall >= 0.95
- ACT precision >= 0.95
- ACT recall >= 0.85
- Forbidden ACT = 0
- Invalid action = 0
- catastrophic collapse = false

## Validation
Any validation set inspected before final freeze is downgraded to development evidence. Fresh validation uses a new seed and realization bank. Action-stratified sampling is used so ACT recall is estimable rather than undefined because of zero ACT support.
