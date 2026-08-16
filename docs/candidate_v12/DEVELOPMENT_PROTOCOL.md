# Candidate-v12 Development Protocol

Data are generated state-first: valid PDA-SPEC-v2 state → deterministic oracle action → fresh controlled realization. Architecture comparison uses seed 12001. Internal holdout uses seeds 13001–13005 (320 examples each). Stress uses seed 14001 (600 examples) and a separate stress realization pool. Mechanistic diagnostics use independent seed family 16001+.

All six action classes are deliberately covered to prevent rare-ACT sampling from inflating safety metrics. Internal synthetic PASS is not independent qualification PASS.
