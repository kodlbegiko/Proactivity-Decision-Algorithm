# Candidate-v12 Architecture Selection

Frozen lexicographic hierarchy: safety → exact state reconstruction → ACT-critical factor accuracy → counterfactual correctness → invariance → UNKNOWN calibration → action Macro-F1 → ACT precision/recall balance → interpretability/complexity.

On fresh final-v2 comparison seed 20501, A/B/C exact-state reconstruction were 0.0/0.0/0.0 and Macro-F1 were 0.047619/0.065208/0.080662. D achieved exact-state=1.0 and Macro-F1=1.0 with zero forbidden ACT and zero invalid actions.

Selected: `D_compositional_semantic_frame_resolver`. C's earlier controlled 1.0 did not qualify it for freeze because fresh compositional tests revealed lexical dependence; this reopening was methodological, not protected-score driven.