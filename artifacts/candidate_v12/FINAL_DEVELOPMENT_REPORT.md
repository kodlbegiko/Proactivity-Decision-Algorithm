# Candidate-v12 Final Development Report

## Executive decision
Architecture C passed controlled internal synthetic holdout, balanced-action stress testing, UNKNOWN probes, counterfactual/invariance probes, and targeted mechanistic diagnostics. It is not frozen in this snapshot because full repository regression is pending GitHub CI. No independent protected qualification was run.

## Starting point and integrity
Candidate-v11 ended `CANDIDATE_V11 QUALIFICATION FAIL — LINEAGE_TERMINATED` with declassified Macro-F1 0.302606, exact latent-state reconstruction 0.011429, counterfactual exact-pair 0, invariance action consistency 0.15, ACT precision 1.0 and ACT recall 0.031746. Candidate-v12 accessed no V11Q raw protected examples, labels, per-example predictions, or protected generators and did not mutate Candidate-v11.

## Architectures
A canonical parser; B factor-specific evidence; C typed propositions/evidence + semantic operators + temporal/ontology resolution + deterministic policy. Frozen lexicographic development criteria selected C.

## Internal results
Internal holdout (5 seeds, 1600 examples): Macro-F1 1.0; exact state 1.0; mean factor 1.0; ACT-critical 1.0; ACT precision 1.0; ACT recall 1.0; forbidden ACT 0; invalid action 0. UNKNOWN: critical 0, false 0, legitimate recall 0.9875. Counterfactual exact pair 1.0. Latent-state and action invariance 1.0. Worst-seed Macro-F1 1.0. Stress Macro-F1 1.0.

Policy Oracle Macro-F1 is 1.0 and Policy Oracle Gap is 0.0 on this controlled development set.

## Mechanistic validation
Targeted fresh diagnostics: negation full 1.0 vs no-operator 0.7833; temporal full 1.0 vs no-temporal 0.4889; ontology full 1.0 vs no-joint-constraint 0.0. These diagnostics establish causal contribution inside the controlled generator regime.

## Limitations
The perfect internal scores are not natural-language generalization evidence. Development and stress realizations are synthetic and ontology-controlled. Unrestricted coreference, nested conditionals, long discourse, unseen idioms, multilingual language, and genuinely independent realizations remain unqualified. An independent protected qualification is mandatory after freeze.

## Freeze decision
NOT AUTHORIZED until GitHub Actions confirms complete repository regression on the V12 branch. If CI passes without integrity violation, create the immutable freeze manifest and stop before independent qualification.
