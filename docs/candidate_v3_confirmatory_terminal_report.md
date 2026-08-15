# Candidate v3 Fresh Confirmatory Evaluation — Terminal Report

**Terminal state:** `FRESH CONFIRMATORY FAIL — CANDIDATE_V3_LINEAGE_TERMINATED`

## Immutable history

- Gate F remains historical `FAIL`.
- Recovery-v3 Development remains `PASS`.
- Candidate v3 remains frozen as `V3A_factor_tree`.
- Gate G — `NOT EXECUTED`.
- Gate H — `NOT EXECUTED`.
- This report does not authorize merge or release.

## Chronology and identity

- Recovery base: `0fd05b6ac9e3f451ed710f2f37ee845dedad1df7`
- Confirmatory preregistration commit: `866aa741aa28e28cc93d04c6619e463885e393b0`
- Candidate source-freeze commit: `d032ba787e5fe509253801befc898a2377b8149f`
- Candidate source SHA-256: `280494c9b0530bc2ce4ea624c32d37a7aa22dc6b0da034bd95d594bf2890ff1b`
- Formal scoring occurred: `True`

## Main protected-set metrics

- Accuracy: `0.166667`
- Macro-F1: `0.047619`
- Weighted-F1: `0.047619`
- Valid-action rate: `1.000000`
- Invalid actions: `0`
- Forbidden ACT: `0`
- Maximum predicted-action share: `1.000000`

### Per-action recall

- ACT: `0.000000`
- ASK: `0.000000`
- IGNORE: `0.000000`
- NOTIFY: `0.000000`
- SUGGEST: `0.000000`
- WAIT: `1.000000`

## Relation metrics

- Counterfactual exact-pair correctness: `0.000000`
- Counterfactual single-side correctness: `0.200000`
- Counterfactual direction sensitivity: `0.000000`
- Invariance prediction consistency: `1.000000`
- Invariance both-sides label correctness: `0.166667`

## Frozen acceptance criteria

- FAIL — `main_macro_f1_ge_0_50`
- PASS — `valid_action_rate_eq_1_00`
- PASS — `invalid_action_count_eq_0`
- PASS — `forbidden_act_count_eq_0`
- FAIL — `all_six_action_recall_gt_0`
- FAIL — `max_predicted_action_share_le_0_50`
- FAIL — `counterfactual_exact_pair_ge_0_70`
- PASS — `invariance_prediction_consistency_ge_0_90`
- PASS — `sealed_hashes_match`
- PASS — `main_exactly_600_and_100_per_action`
- PASS — `counterfactual_exactly_120_valid_pairs`
- PASS — `invariance_exactly_120_valid_pairs`
- PASS — `candidate_source_identity_frozen`
- PASS — `candidate_visible_fields_only_domain_observation`
- PASS — `no_historical_protected_access`
- PASS — `no_candidate_tuning_or_postfreeze_change`

## Scientific boundary

This is a fresh preregistered process-isolated confirmatory evaluation of the frozen Candidate-v3 lineage. It does not rewrite the historical Gate-F failure and does not itself execute Gate G, establish deployment readiness, or establish external/human-independent validation.
