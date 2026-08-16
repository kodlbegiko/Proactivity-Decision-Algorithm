# Candidate-v7 Development Terminal Report

## Terminal State

`CANDIDATE V7 DEVELOPMENT INVALID — RESEARCH INTEGRITY OR EVALUATION FAILURE`

This terminal state is intentionally **INVALID**, not PASS and not scientific FAIL. The pre-qualification research-integrity gate failed after validation-only architecture selection had already produced scientific validation evidence. Under the frozen retry rule, the auditor cannot be repaired and the scientific pipeline rerun after that point. Qualification holdouts therefore remained locked and were not evaluated.

## Identity

- Branch: `research/candidate-v7-proposition-logic-reasoning`
- Preregistration commit: `520033a76a848262290dd1221f9fc79fcba08539`
- Frozen Candidate-v7 scientific source commit: `a23d14a9438870314d67d60ce2deda1ebf5b899e`
- Source freeze commit: `3441e89eb27f88363d91608791db39abced9a59f`
- Dataset freeze commit: `bf069274a32b639feeddffb55203befa51721ff6`
- Selected candidate commit: `fb4dc35e2447d28d8b2777aca6c6a901bc2aeaf1`
- Qualification commit: `NOT_EXECUTED`
- Terminal evidence commit: `7c7fd2f2afbcddfce30cb54431b9bc12183725df`
- GitHub Actions run: `31923232067`
- Selected architecture: `V7A — Proposition Semantic Graph`
- Selected config: `V7A-01`

## Research Integrity

Preregistration chronology, source freeze, dataset freeze, validation-only selection, search budget, and selected-candidate freeze all completed in the required order.

The pre-qualification auditor then returned `FAIL` and reported forbidden historical path references. Inspection of the audit output showed that every reported hit was the auditor scanning **its own `FORBIDDEN_REFERENCES` detector constants** inside `scripts/check_candidate_v7_research_integrity.py`. The reported hits were detector definitions such as `data/protected/` and Candidate-v4/v5/v6 paths, not evidence that Candidate-v7 source, generator, evaluator, architecture search, or prompt construction opened individual protected examples.

Accordingly:

- Auditor status: `FAIL`
- Actual protected-example access evidence observed: `NONE_OBSERVED`
- Auditor self-reference false positive: `YES`
- Source mutation after selected-candidate freeze: `NONE`
- Qualification execution count: `0`
- Qualification holdouts observed: `false`

Because validation evidence already existed when the auditor defect became visible, repairing the auditor and rerunning the scientific pipeline would violate the preregistered infrastructure-retry rule. The correct research-integrity action is therefore to terminate INVALID rather than reinterpret the failed gate as a pass.

## Reproducibility

Stage A completed on Python `3.10`, `3.11`, and `3.12`.

- Candidate-v7 source tests: passed on all three Python versions
- Full fresh dataset generation: passed on all three Python versions
- Cross-version manifest comparison: byte-identical
- Canonical Python: `3.11`
- Canonical manifest SHA-256: `951cf59df3f4664d4f271365ea69b36b7af78ef63304d95d6f5289482e1d6f10`

Three pre-validation infrastructure retries were recorded. All occurred before any validation or qualification metric existed: one regex implementation typo, one finite formal-state sampling issue, and one infeasible compositional partition. None changed the preregistered architecture search budget, qualification thresholds, dataset sizes, seeds, or used protected/qualification evidence for repair.

## Dataset Freeze

The canonical fresh Candidate-v7 dataset was frozen before architecture selection:

- train: `4,800`
- validation: `1,200`
- development OOD: `1,200`
- lexical holdout: `800`
- rendering holdout: `800`
- compositional holdout: `800`
- negation holdout: `600`
- scope holdout: `600`
- temporal holdout: `600`
- counterfactual: `480` records / `240` pairs
- invariance: `480` records / `240` pairs

Lexical isolation was recorded as true. The generation direction remained `formal state -> semantic plan -> typed propositions -> surface realization`.

## Selected Architecture

The preregistered validation-only search evaluated exactly 12 configurations across V7A, V7B, and V7C. No qualification holdout was loaded by the selection process.

Selected candidate:

- Architecture: `V7A`
- Config: `V7A-01`
- Selection source: `validation_only`

V7A and V7C configurations reached the same perfect action/latent validation metrics under this fresh validation generator. V7B was substantially weaker. The deterministic tie-break selected `V7A-01`.

## Validation

Frozen validation-only selection evidence for `V7A-01`:

- Accuracy: `1.000000`
- Macro-F1: `1.000000`
- Forbidden ACT: `0`
- Invalid action: `0`

These are **development validation metrics only**. They are not qualification or confirmatory evidence.

## Latent-State Recovery

Validation-only evidence:

- Exact latent-state reconstruction: `1.000000`
- Mean factor accuracy: `1.000000`
- ACT-critical factor accuracy: `1.000000`
- Critical UNKNOWN rate: `0.000000`

The perfect validation result shows that V7A can reconstruct the states generated by the validation realization family. It does **not** establish robustness under the locked OOD/lexical/rendering/negation/scope/temporal distributions.

## Semantic Operators

Validation-only evidence:

- Factor evidence attribution accuracy: `1.000000`
- Proposition polarity accuracy: `0.915000`
- Negation scope accuracy: `1.000000`
- Modal interpretation accuracy: `0.734861`
- Temporal interpretation accuracy: `1.000000`

The non-perfect polarity and modality scores are important: action/state validation perfection does not imply complete proposition-level semantic correctness.

## Development OOD

`NOT_EXECUTED` — pre-qualification research-integrity gate failed before holdout unlock.

## Lexical

`NOT_EXECUTED` — no legal lexical robustness conclusion is available.

## Rendering

`NOT_EXECUTED` — no legal rendering robustness conclusion is available.

## Compositional

`NOT_EXECUTED` — no legal compositional qualification conclusion is available.

## Negation

`NOT_EXECUTED` — the synthetic unit tests passed before freeze, but the preregistered negation qualification holdout was never evaluated. Unit-test success is not a qualification result.

## Scope

`NOT_EXECUTED` — the preregistered scope holdout was never evaluated.

## Temporal

`NOT_EXECUTED` — the preregistered temporal holdout was never evaluated.

## Counterfactual

`NOT_EXECUTED` — counterfactual exact-pair performance is unavailable.

## Invariance

`NOT_EXECUTED` — invariance action consistency is unavailable.

## Safety

Validation-only evidence:

- Forbidden ACT: `0`
- Invalid action: `0`

Qualification safety metrics: `NOT_EVALUATED`.

It would be incorrect to claim Candidate-v7 safety qualification from validation alone.

## Baselines

`NOT_EXECUTED` after the integrity gate failure. The frozen execution order placed baselines after qualification; qualification was never authorized.

## Ablations

`NOT_EXECUTED` after the integrity gate failure. No component-level causal performance claim is authorized from this lineage.

## Catastrophic Collapse

Qualification collapse analysis: `NOT_EVALUATED`.

The selected validation candidate had no invalid action and no forbidden ACT, but a full qualification collapse conclusion requires the locked split metrics and distributions, which were not executed.

## Failure Analysis

The terminal invalidation was not caused by a Candidate-v7 holdout score. It was caused by a defect in the pre-qualification research-integrity auditor:

1. The auditor correctly attempted to detect forbidden historical path references.
2. Its source scanner included `scripts/check_candidate_v7_research_integrity.py` itself.
3. That file necessarily contained the forbidden path strings as detector constants.
4. The scanner therefore self-matched those constants and reported protected leakage.
5. The defect was discovered only after validation-only architecture selection had already executed.
6. The preregistered retry rule permits infrastructure repair only before scientific evaluation evidence is observed.
7. Therefore no auditor patch, no qualification unlock, and no scientific rerun is legal within this Candidate-v7 lineage.

## Scientific Interpretation

1. **Did Candidate-v7 improve joint latent-state reconstruction?** Validation evidence is strong (`1.0` exact), but qualification evidence is absent. Improvement under distribution shift is not established.
2. **Did explicit proposition representation improve lexical robustness?** Not evaluable; lexical holdout was not run.
3. **Did the negation engine solve negation collapse?** Not evaluable at qualification level; unit tests alone are insufficient.
4. **Was scope parsing effective?** Not evaluable on the scope holdout.
5. **Was temporal normalization effective?** Not evaluable on the temporal holdout.
6. **Was the symbolic state solver better than independent factor argmax?** Not evaluable because mandatory ablations were not run.
7. **Is V7 improvement genuine semantic reasoning or a dataset shortcut?** Unresolved. Perfect validation plus shared formal ontology makes shortcut/template-family overfit a material alternative explanation until independent shifts are evaluated.
8. **Which ablations are most important?** Unresolved; ablations were not legally reached.
9. **Does single-class/two-class collapse remain?** Qualification-level answer unavailable.
10. **Was safety obtained by excessive conservatism?** Cannot be determined from validation alone.
11. **Is ACT safe while retaining reasonable recall?** Validation shows zero forbidden ACT, but qualification recall/safety trade-off is unavailable.
12. **What is the next architecture bottleneck?** This lineage cannot answer that scientifically because the qualification gate was never reached. The immediate bottleneck is evaluation-integrity infrastructure, not evidence that V7 semantics passed or failed generalization.

## Authorization

- Development PASS: `NO`
- Development scientific FAIL: `NO` — qualification was not executed
- Development INVALID: `YES`
- Fresh independent confirmatory: `NOT_AUTHORIZED`
- Gate G: `NOT_EXECUTED`

No future confirmatory or Gate G work may cite this Candidate-v7 lineage as a development PASS.

## Primary Scientific Conclusion

Candidate-v7 produced unusually strong validation-only evidence for proposition-level state reconstruction, but the lineage cannot legally answer the intended generalization question. The pre-qualification research-integrity gate failed because its detector self-matched its own forbidden-path constants, and that defect was discovered only after validation evidence existed. Under the preregistered no-post-evaluation-repair rule, the correct terminal result is **INVALID**, with all qualification holdouts left untouched and no rescue attempt.
