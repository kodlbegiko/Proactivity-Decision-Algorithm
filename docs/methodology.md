# Methodology v2 — Specification-Grounded Intervention Control

## Research design

Protocol v2 studies **specification compliance for intervention control**, not general assistant task completion and not human-preference prediction.

Primary evidence path:

```text
explicit structured state
-> frozen versioned specification
-> deterministic reference oracle
-> oracle action + rule/prohibition trace
-> leakage-controlled benchmark representation
-> reproducible evaluation evidence
```

## Frozen structured state and action semantics

The formal state contains permission, information sufficiency/contradiction, urgency, intervention need, side-effect scope, risk, reversibility, deferral availability, execution possibility, clarification possibility, acknowledgement, and completion. Invalid combinations fail closed.

The six actions are `IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, and `ACT`. No universal scalar ordering is assumed.

## Formal specification and oracle

`spec/proactivity_policy_v2.json` is the transparent machine-readable policy. `src/proactivity/specification/` implements the deterministic reference oracle and validation logic. The oracle has no network/LLM dependency, reads only formal state for normative decisions, rejects invalid states, computes hard prohibitions, fails closed on conflicts, and returns a trace.

Gate-C normative dependency is frozen at:

- policy `PDA-SPEC-v2`;
- schema `2.0.0`;
- spec SHA-256 `ea06eeb85ffa375740e778d273b57d79e7f4f96d0eb68eb74ed2ef9df6d827a4`;
- oracle source SHA-256 `11ec7557d4809b18e1c414d9a3b0eaf95ad93ac7f771da11ed0cf4c3043bed2f`;
- Gate-B commit `89e00052d68b2862269daf2adc8b31ebb1ae592c`.

Gate C is prohibited from changing these normative artifacts for benchmark convenience.

## Gate B — Formal Specification Validity

Gate B exhaustively validated 62,208 raw Cartesian combinations, 41,472 valid states, deterministic output, rule coverage, traces, invariants, counterfactual checks, temporal behavior, metadata/domain invariance, and Python 3.10/3.11/3.12 CI. Its machine verdict remains `GATE B — PASS`.

## Gate C — Oracle and Benchmark Validity

Gate C asks whether the frozen oracle-derived benchmark is a valid measurement instrument for later evaluation. It does **not** test a PDA candidate.

### Ground-truth provenance

The only accepted label chain is:

```text
generator-known structured state
-> frozen validator
-> frozen specification
-> deterministic oracle
-> oracle action + trace
```

Manual gold actions, LLM-authored gold actions, post-hoc label overrides, or candidate-derived answers are forbidden. The final Gate-C benchmark contains 168/168 oracle-derived records, with zero manual gold, zero LLM gold dependency, and zero oracle mismatch.

### Representation tracks

**Track A — mechanistic structured-state track:** candidate transport may contain `scenario_id`, `domain`, `state`; the evaluated model/policy input excludes the transport identifier. This track supports mechanistic rule-compliance diagnostics only.

**Track B — synthetic observation/context track:** candidate transport contains `scenario_id`, `domain`, `observation`; evaluated input excludes the transport identifier. Observation text is deterministically rendered from source-state semantics and excludes oracle action, rule/prohibition trace, relation IDs, template ID, split, and other answer-bearing metadata.

Track B is synthetic. It cannot alone support broad real-world contextual-proactivity or ecological-validity claims.

### Anti-circularity

`gate_c/representation_contract_v2.json` separates candidate-visible transport from oracle-private evidence. `scripts/validate_candidate_boundary_v2.py` rejects future candidate source that imports the frozen oracle/benchmark implementation or directly reads private evidence artifacts at runtime; machine-checkable guards and failure-path tests enforce this boundary.

### Coverage and relational design

Gate-C criteria were frozen before formal statistics. Final benchmark evidence includes:

- all six actions, each with at least 12 examples;
- every reachable selected non-fallback decision rule with at least 6 examples;
- every hard prohibition with at least 6 trigger examples and one single-variable action-changing prohibition counterfactual;
- 8 generic counterfactual families;
- 8 prohibition-counterfactual families;
- 8 temporal sequences;
- zero relation violations.

The natural exhaustive action distribution is reported separately from the intentionally coverage-efficient benchmark sampling distribution.

### Diversity and leakage

The final benchmark has 168 unique IDs, zero exact candidate-record duplicates, zero structural/source-state duplicate members, four observation template families (`41/38/39/50`), and a largest template-family share of 29.76%, below the preregistered 34% maximum.

Candidate-visible records contain no forbidden answer metadata and no direct action-label tokens. Diagnostic ID-prefix, row-bucket, domain-only, template-only, and lexical analyses are leakage diagnostics, not formal Gate-D baselines. Group-aware splitting prevents counterfactual/temporal/state-family siblings from crossing development/validation/public-holdout sets.

### Split and protected-set boundary

Final deterministic split counts are development 91, validation 33, and `protected_test` 44. The Gate-C `protected_test` split is publicly regenerable and therefore validates freeze/split mechanics only. It is **not** independent Gate-F protected evidence. A future confirmatory protected set must use the isolation protocol in `gate_c/protected_test_protocol_v2.json`.

### Reproducibility

Gate-C CI regenerates the benchmark twice and requires byte-identical artifacts, re-runs Gate-B regression, executes the Gate-C audit and fail-closed decision engine, runs the full regression/failure-path suite, and preserves Protocol-v1 negative evidence.

Passing run `31791713759` completed successfully on Python 3.10, 3.11, and 3.12. Each matrix job ran 73 pytest tests successfully. Frozen benchmark hashes are recorded in `gate_c/freeze_v2.json`.

## Preserved Gate-C failures

1. Run `31791152951` produced a real Gate-C scientific benchmark-generator failure: the first three-template allocation was `65/45/58`, giving a 38.69% largest-family share and violating the preregistered 34% cap. The fix added a fourth non-normative paraphrase family. No specification, oracle, gold action, or threshold changed.
2. Run `31791651373` exposed an infrastructure-only audit-wrapper import-path failure (`ModuleNotFoundError: scripts`) after benchmark regeneration succeeded. The wrapper was made path-independent; no scientific criterion changed.

Negative results remain part of the evidence chain.

## Gate D — Baseline Integrity

Gate D evaluates whether later candidate work has an honest, deterministic comparison suite. It does not require baselines themselves to be strong or safe.

The preregistered raw-context baselines are B0 majority action, B1 development-prior sampled random, B2 domain-only, B3 unigram Multinomial Naive Bayes, B4 word/character TF-IDF plus domain one-hot logistic regression, and B5 fixed transparent heuristic. Models receive only preregistered candidate-visible fields; private/oracle state and answer-bearing transport metadata are evaluator-only.

Source guards reject oracle/spec imports, private/structured benchmark reads, relation files, matched-rule/prohibition traces, family/split metadata, hard-coded scenario-ID lookup, and direct gold tables. Formal controls include frozen benchmark hashes, repeated fixed-seed runs, row-order shuffle, domain ablation, observation shuffle, label permutation, token shuffle, prediction coverage, valid-action coverage, and independent metric recomputation.

Formal Gate-D implementation commit `6377d31eaa57f162df68c4c3f89c7b6cb7e0206c` passed run `31801340084` on Python 3.10, 3.11, and 3.12. The full report and six prediction files were byte-identical across the three environments. Strongest honest raw-context baseline by macro-F1 is B5 at `0.21452991452991452`; Gate E must compare against that frozen value.

Preregistration amendment D-001 changed only the scikit-learn version pin to `1.7.1` before formal scoring so the predeclared Python 3.10/3.11/3.12 matrix remained executable. Scientific criteria and model definitions did not change.

## Gate E — Candidate Evidence

Gate E uses development for training, validation for bounded preregistered selection, and excludes Gate-C `protected_test` payloads from fitting, feature engineering, scoring, selection, and debugging. Gate-F protected/OOD data remains ungenerated until the selected candidate is frozen.

The search budget was frozen at six configurations before formal evaluation. The selected raw-context candidate is `C5_semantic_factor_linear`: candidate-visible observation text is mapped by an independently implemented extractor into 12 visible semantic factors—permission, information, timing, intervention need, side-effect scope, risk, reversibility, deferral, execution possibility, clarification possibility, acknowledgement, and completion—then encoded with `DictVectorizer` and classified by balanced logistic regression (`C=1.0`, `max_iter=3000`, `random_state=20260814`). It does not import/call the reference oracle or read hidden structured state/private benchmark data at runtime.

Chronology is machine-auditable: preregistration `da6f205f4c1aff001b9f24b4782a44a94e885acd` -> candidate-source freeze `554da731c962cdbf2ebd63cb65149f393e05b617` -> evaluator addition `c3c814c6020d0fb9b47a0bf71b6d80b67202c1d9` -> protected-payload isolation fix `8ad2411b5db48cfe180bb500c996a7557abbda9b` before scoring -> formal CI enable `fc030269e347142d5a9ad730499d189647ccded7`. CI verifies `candidate_v2.py` remains unchanged from the source-freeze commit.

Formal run `31804595710` succeeded across Python 3.10/3.11/3.12 with byte-identical reports and predictions. Selected validation macro-F1 is `0.6936507936507935`, versus frozen B5 `0.21452991452991452`, for delta `+0.479120879120879`. Valid-action rate is 100%, forbidden ACT is 0, and all six actions have non-zero recall. The preregistered 10,000-sample paired bootstrap produced a delta 95% interval `[0.269140495727183, 0.6969364243570899]` and fraction delta > 0 of `1.0`.

These are **validation** results under the controlled synthetic representation. They do not establish independent protected/OOD generalization. Gate F must generate a new chronological/process-isolated confirmatory set only after the selected candidate source/config is frozen and evaluate it once under preregistered criteria.

## Historical Protocol v1

Protocol v1 remains `GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION`; its 25% historical completion and missing human-label evidence are not rewritten by Protocol v2.

## Gate order

Gate A: scope / claim boundary / prior art.  
Gate B: formal specification validity.  
Gate C: oracle and benchmark validity.  
Gate D: baseline integrity.  
Gate E: candidate evidence.  
Gate F: protected/OOD validation.  
Gate G: robustness/adversarial/invariant stress testing.  
Gate H: ablation/reproducibility/independent reproduction/final claim audit.

Gate E has passed at the formal-source evidence level. The next scientifically valid gate is Gate F only after the Gate-E terminal freeze HEAD itself completes regression CI.
