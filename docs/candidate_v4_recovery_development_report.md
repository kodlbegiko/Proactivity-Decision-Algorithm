# Candidate-v4 Independent Generalization Recovery — Development Terminal Report

## Terminal decision

**RECOVERY DEVELOPMENT PASS — CANDIDATE V4 FROZEN**

Selected candidate: `V4B_atom_state_machine_a65`.

This decision is limited to the preregistered Candidate-v4 recovery/development protocol. It does not execute or authorize Gate G, Gate H, or a new protected confirmatory evaluation.

## Research-integrity boundaries

Candidate v3 remains terminated after its fresh confirmatory failure. Historical Gate F remains FAIL. No Candidate-v3 confirmatory record was used for Candidate-v4 development; the only Candidate-v3 confirmatory information admitted into this lineage was the aggregate terminal fact set allowed by the mission.

The quarantined paths remained unchanged under CI enforcement. Candidate-v4 inference receives only `domain` and `observation`; development labels and latent states are removed before prediction.

## Preregistration and chronology

- Recovery base: `0fd05b6ac9e3f451ed710f2f37ee845dedad1df7`
- Candidate-v4 preregistration frozen before implementation: `c1942470cfea1fe3678e5143da0c1ba8f9ed1aa4`
- First implementation CI run: `31885246197` — FAIL during a development unit test because one negated deferral phrase was parsed as positive.
- The defect was a lexical negation collision: `lacks a concrete trigger` contained the positive tail `concrete trigger`.
- The parser was corrected by explicit negation precedence without changing the preregistration, search space, thresholds, protected-data boundary, or development split labels.
- Candidate source commit after that correction: `daf0def6bc06633f3e743a83b2792fc5c4a2d3a8`.
- Qualification/materialization execution commit: `dbd688cc2ec7856627ab732b9d357625269ea7f7`.
- Formal matrix qualification run: `31885502180` — PASS on Python 3.10, 3.11, and 3.12.

## Architecture

The selected architecture is not a sentence-level classifier. It performs:

```text
observation
-> clause segmentation
-> factor-anchor routing
-> value-cue reconstruction
-> latent public-specification state
-> Protocol-v2 deterministic decision state machine
-> conservative ACT safety gate
```

`V4B_atom_state_machine_a65` uses an ACT confidence floor of `0.65`. Unknown or weak critical evidence cannot authorize ACT.

## Development-safe datasets

The new Candidate-v4 dataset lineage was generated solely from the frozen public Protocol-v2 state schema and deterministic oracle.

Materialized CI payloads:

- training: 576 rendered examples
- validation: 36 examples
- development OOD: 36 examples
- lexical holdout: 24 examples
- rendering-family holdout: 24 examples
- compositional holdout: 24 examples
- counterfactual safety: 18 pairs
- invariance: 24 pairs

The state configurations for training and each qualification split are disjoint. The materialized JSONL files were byte-identical across Python 3.10/3.11/3.12. Exact payload and byte hashes are frozen in `data/candidate_v4_development/manifest.json`.

## Bounded candidate search

The preregistered search evaluated only the allowed V4A/V4B/V4C families and configurations. Four configurations satisfied all preregistered acceptance criteria:

1. `V4B_atom_state_machine_a65`
2. `V4B_atom_state_machine_a55`
3. `V4C_hybrid_guarded_c6_a55`
4. `V4C_hybrid_guarded_c4_a55`

The preregistered selection rule chose `V4B_atom_state_machine_a65`; V4B is preferred over more complex alternatives on ties, and the `a65` configuration sorts ahead among the fully qualified V4B configurations under the frozen ranking implementation.

The supervised V4A clause-linear family did not qualify. It retained zero ACT recall in validation and collapsed toward ASK under several holdouts, showing that factor-level supervision alone was insufficient under this development distribution.

## Selected-candidate qualification metrics

| Evaluation | n | Macro-F1 | Parser factor accuracy | Forbidden ACT | Collapse |
|---|---:|---:|---:|---:|---|
| Validation | 36 | 1.000000 | 0.986111 | 0 | No |
| Development OOD | 36 | 1.000000 | 1.000000 | 0 | No |
| Lexical holdout | 24 | 1.000000 | 1.000000 | 0 | No |
| Rendering-family holdout | 24 | 1.000000 | 0.975694 | 0 | No |
| Compositional holdout | 24 | 1.000000 | 1.000000 | 0 | No |

All six action recalls were `1.0` on every qualification split. Maximum prediction-class share was `1/6` on every split, so no single-class collapse occurred.

Additional tests:

- counterfactual exact-pair rate: `1.000000` on 18 pairs
- counterfactual forbidden ACT: `0`
- invariance prediction consistency: `1.000000` on 24 pairs
- invariance exact-both rate: `1.000000`
- invalid action count: `0`

## Reproducibility

The normalized qualification result, after removing only the Python runtime-version field, had SHA-256:

`594be2c6ecd2ed5f928d4c70d776358d7ae14e15814850ed7a274cce84db56f1`

This hash was identical on Python 3.10.20, 3.11.15, and 3.12.13. All materialized dataset files were also byte-identical across the matrix.

Candidate source SHA-256:

`66a5a899b7c1c5eea102e96f649db89cce2e9c8a38c8d755a25dddcf6abe492e`

## Interpretation and limitation

The recovery objective was to eliminate the brittle `unknown -> WAIT` failure mode on preregistered development-safe heterogeneous renderings. On these tests, Candidate v4 did so while retaining zero forbidden ACT.

However, the perfect action metrics must not be interpreted as broad natural-language generalization. The holdouts are still generated from the same public state ontology and a researcher-designed family of semantic phrase inventories. Candidate V4B also uses researcher-authored semantic anchors/cues aligned to that ontology. Therefore these tests provide strong evidence of **compositional/rendering robustness inside this synthetic development design**, but they are not statistically or semantically independent evidence of open-vocabulary human language understanding.

A fresh protected confirmatory evaluation, if separately authorized and preregistered after this freeze, remains necessary to test whether the architecture generalizes beyond the development language families. Candidate-v3 protected evidence remains quarantined and cannot be reused for that purpose.

## Final state

- Historical Gate F — **FAIL**
- Candidate-v3 Fresh Confirmatory — **FAIL**
- Candidate-v3 lineage — **TERMINATED**
- Candidate-v4 Recovery Development — **PASS**
- Candidate-v4 — **FROZEN** (`V4B_atom_state_machine_a65`)
- Gate G — **NOT EXECUTED**
- Gate H — **NOT EXECUTED**
- New protected confirmatory evaluation — **NOT AUTHORIZED / NOT EXECUTED**
