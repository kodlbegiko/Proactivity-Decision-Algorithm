# Candidate-v12 Development Protocol

Development is state-first: valid PDA-SPEC-v2 state → deterministic oracle action → fresh controlled realization. Four architectures were compared.

Final-v2 uses ambiguity-free realization pools and entirely fresh seeds after earlier development harnesses exposed generator collisions. Final comparison seed=20501. Internal holdout seeds=20511–20515, 360 examples each (1,800 pooled). Stress seed=20521, 720 examples with distractors. UNKNOWN=20601, counterfactual=20602, invariance=20603, mechanistic=20604, state-to-action sufficiency=20605, collision audit=20600.

Earlier failed `advanced_dev` and `final_dev` harnesses are retained as research history. Their failures were generator/evaluation collisions; final-v2 changed realization methodology and seeds, not policy thresholds or protected-data access.

All six actions are deliberately supported. Independent qualification is NOT_RUN and must be a separate lineage.