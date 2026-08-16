# Candidate-v8 Development Preregistration

- Base SHA: `83e41d91d264dd7074ea31d61571f14eaa6b09e3`
- Historical Candidate-v7 frozen SHA: `545af659abd420843e7b5313f4daf0de4d3ac95a`
- Fresh lineage: Candidate-v8 only; Candidate-v7 is immutable.
- Development inputs: frozen PDA-SPEC-v2, public/spec-derived logic, newly generated Candidate-v8 train/validation data, Candidate-v7 aggregate failure families only.
- Historical individual holdout/protected records are prohibited development inputs.
- Train target: 4,800; validation target: 1,200; six actions balanced.
- Candidate families: V8-A evidence-separated decoder; V8-B dual-channel eligibility/prohibition; V8-C adds temporal supersession and contradiction-aware resolution.
- Selection is multi-objective. Thresholds are fixed before validation execution and are not reducible after results.
- Validation thresholds: Macro-F1 >= .90; accuracy >= .90; each action recall >= .80; ACT recall >= .85; ACT precision >= .95; forbidden ACT = 0; false ACT = 0; critical-factor accuracy >= .95; exact-state accuracy >= .90; critical false-positive rate = 0; false certainty = 0; max prediction share <= .35.
- Structured qualification additionally requires counterfactual directional accuracy >= .95 and ACT-disable accuracy = 1.0.
- Development holdouts may only be materialized after the selected candidate is committed and remote freeze SHA verified.
- Any mandatory post-freeze holdout failure terminates Candidate-v8. No tuning or retry is allowed.
