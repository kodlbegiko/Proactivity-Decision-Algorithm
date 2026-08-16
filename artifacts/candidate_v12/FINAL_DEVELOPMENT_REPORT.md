# Candidate-v12 Final Development Report

## 1. Executive decision
`D_compositional_semantic_frame_resolver` satisfies the preregistered Candidate-v12 development authorization floors on fresh controlled final-v2 holdout/stress data, passes mechanistic validation and development-safe repository regression, and is authorized for immutable freeze. No independent qualification was run.

## 2. Candidate-v11 scientific starting point
V11 ended with valid scientific FAIL. Declassified aggregates included Macro-F1≈0.303, exact state≈0.011, counterfactual exact-pair=0, invariance action consistency≈0.15, ACT precision=1.0 and ACT recall≈0.032.

## 3. Research hypotheses
H1–H7 were operationalized. Structured semantic state, explicit operators, calibrated missingness, counterfactual/invariance constraints, and deterministic policy are supported inside controlled development; external claims remain pending qualification.

## 4. Integrity boundaries
V11Q raw protected examples/labels/predictions/errors/realizations were not inspected. Candidate-v11 was not mutated. V12 source contains no protected test/generator imports.

## 5. Data-generation methodology
State-first generation created valid normative states before realization. Final-v2 uses fresh ambiguity-free realization pools after earlier harnesses exposed generator collisions. No protected score tuning occurred.

## 6. Architecture families explored
A canonical parser; B factor-specific evidence; C typed evidence resolver; D compositional semantic frames.

## 7. Architecture-selection criteria
Safety, semantic reconstruction, ACT-critical state accuracy, counterfactuals, invariance, UNKNOWN calibration, Macro-F1, ACT balance, then interpretability/complexity.

## 8. Selected architecture
D separates factor concepts from predicates, resolves semantic operators/temporal/entity/epistemic relations, forms a typed state, then invokes deterministic policy.

## 9. Semantic-state results
1,800-example pooled holdout: exact state=1.0, mean factor=1.0, Macro-F1=1.0.

## 10. Factor-level results
All 12 factor accuracies=1.0; ACT-critical factor accuracy=1.0.

## 11. Operator-level results
All 11 final operator/collision probes pass.

## 12. UNKNOWN calibration
Critical UNKNOWN=0.0; false UNKNOWN=0.0; legitimate UNKNOWN recall=1.0.

## 13. Counterfactual results
240 fresh pairs: exact pair=1.0, factor delta=1.0, action transition=1.0.

## 14. Invariance results
300 fresh groups: latent-state invariance=1.0, action invariance=1.0, correct consistency=1.0.

## 15. Action results
Macro-F1=1.0 with exactly 300 examples per action in pooled holdout.

## 16. ACT safety/capability results
ACT precision=1.0, ACT recall=1.0, forbidden ACT=0, invalid action=0.

## 17. Policy Oracle Gap
Ground-truth-state policy oracle Macro-F1=1.0; predicted-state policy Macro-F1=1.0; gap=0.0.

## 18. Robustness across seeds
Five fresh seeds all Macro-F1=1.0; worst seed=1.0; standard deviation=0.0.

## 19. Stress testing
720-example distractor stress set: Macro-F1=1.0, exact state=1.0, forbidden ACT=0.

## 20. Ablation findings
Temporal full=1.0 vs ablated=0.5667; contradiction safety full=1.0 vs ablated=0.0; frame composition exact-state=1.0 vs lexical C=0.0. State-to-action sufficiency: 5,000 states, zero equal-state conflicts.

## 21. Repository regression
Development-safe CI run 31932391905 passes on Python 3.10/3.11/3.12 after reproducing repository deterministic prerequisites. Protected qualification test is excluded by integrity rule; V7R collection failure is pre-existing and unchanged; superseded failed V12 harnesses are retained as history. All remaining repository tests pass.

## 22. Limitations
Perfect scores are on controlled synthetic development realizations. They do not prove open-domain, multilingual, unrestricted coreference, nested discourse, or real-user generalization. Earlier generator collisions demonstrate why independent qualification remains necessary.

## 23. Scientific interpretation
Within controlled development, the result supports the hypothesis that a compositional typed state layer can remove the policy bottleneck without obtaining ACT precision by suppressing ACT recall.

## 24. Freeze authorization decision
PASS. Source commit `e8ed2afa0171734450b4d56e04420b4cb1007423` is immutable-frozen by the Candidate-v12 freeze manifest.

## 25. Next scientifically authorized action
Design a separate, preregistered independent qualification lineage with fresh protected generation/seeds and no development access. Do not run qualification from this development agent.
