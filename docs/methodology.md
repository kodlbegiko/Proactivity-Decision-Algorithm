# Methodology v2 — Specification-Grounded Intervention Control

Protocol v2 studies specification compliance for intervention control, not general assistant task completion or human-preference prediction. The six discrete actions are `IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, and `ACT`; no universal scalar action ordering is assumed.

## Frozen upstream

The normative chain remains frozen at Gate-B commit `89e00052d68b2862269daf2adc8b31ebb1ae592c`, policy SHA-256 `ea06eeb85ffa375740e778d273b57d79e7f4f96d0eb68eb74ed2ef9df6d827a4`, and oracle source SHA-256 `11ec7557d4809b18e1c414d9a3b0eaf95ad93ac7f771da11ed0cf4c3043bed2f`. Gate C froze a 168-scenario oracle-derived benchmark with development/validation/public-holdout counts 91/33/44. The public holdout is not independent Gate-F evidence.

## Gate B — Formal Specification Validity

Gate B exhaustively validated 62,208 raw Cartesian combinations, 41,472 valid states, deterministic output, rule coverage, traces, invariants, counterfactual checks, temporal behavior, metadata/domain invariance, and Python 3.10/3.11/3.12 CI.

## Gate C — Oracle and Benchmark Validity

Gate C validated oracle-derived ground-truth provenance, candidate/private separation, coverage, structural diversity, leakage controls, counterfactual/temporal integrity, group-aware splits, and deterministic regeneration. Synthetic observation text is a controlled representation and does not establish ecological validity or unrestricted natural-language understanding.

Preserved Gate-C failures: run `31791152951` violated the preregistered template-family cap; run `31791651373` exposed an audit-wrapper import-path failure. Both were repaired without changing normative policy, oracle, gold labels, or thresholds.

## Gate D — Baseline Integrity

Gate D preregistered and evaluated six raw-context comparison baselines using only development labels for fitting and validation labels only in the evaluator. Baseline source is prohibited from importing the oracle/spec implementation, reading private/structured evidence, or using scenario/split/template/family metadata as predictive features.

Required baselines are majority action, prior-sampled random, domain-only, unigram Naive Bayes, word+character TF-IDF logistic regression with domain one-hot, and a fixed transparent surface heuristic. Fixed seed is `20260814`; `scikit-learn==1.7.1` is pinned for Python 3.10/3.11/3.12 compatibility.

Formal metrics include accuracy, macro/weighted F1, per-action precision/recall/F1, confusion matrix, prediction distribution, valid-action rate, ACT count, forbidden-ACT count, and relational diagnostics. Controls include benchmark hash verification, source-boundary failure paths, repeated deterministic runs, row-order shuffle, domain ablation, observation shuffle, label permutation, token shuffle, and independent metric recomputation.

Gate-D PASS is an integrity decision, not a requirement that baselines be safe or strong. Weak-baseline forbidden ACT predictions are preserved. Formal run `31801340084` passed all matrix jobs and produced byte-identical report/prediction content across Python 3.10/3.11/3.12.

The strongest honest validation baseline by macro-F1 is B5 at `0.21452991452991452`; Gate E must compare against that fixed result.

## Next methodology gate

Gate E will preregister candidate families, bounded search budget, model-selection rule, paired uncertainty method, safety thresholds, and the no-protected-test rule before formal candidate evaluation. Gate F data must not be generated or accessed until the Gate-E candidate is frozen.
