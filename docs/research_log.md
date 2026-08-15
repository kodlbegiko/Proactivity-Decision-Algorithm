# Research Log

This file records the current scientific decision history. Earlier full-detail entries remain recoverable from Git history; the statuses below intentionally preserve negative evidence rather than rewriting prior failures as successes.

## 2026-08-13 — Protocol v1 negative evidence

Protocol v1 narrowed the research target after prior-art review, made raw context primary, built deterministic development/annotation infrastructure, and preserved generator-shortcut warnings. Its scientific state remained `GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION`; genuinely independent human annotation was never fabricated. Historical evidence-weighted completion remains 25%.

## 2026-08-14 — Protocol v2 research-question pivot

Protocol v2 superseded Protocol v1 as the primary track without retroactively changing Protocol-v1 outcomes. The new primary question is specification-grounded intervention control under an explicit finite state, frozen formal specification, deterministic oracle, and machine-verifiable trace. Human-preference alignment and universal correctness were explicitly removed from the primary claim.

## 2026-08-14 — Gate B formal specification evidence

`PDA-SPEC-v2`, schema `2.0.0`, was frozen at SHA-256 `ea06eeb85ffa375740e778d273b57d79e7f4f96d0eb68eb74ed2ef9df6d827a4`; oracle source SHA-256 is `11ec7557d4809b18e1c414d9a3b0eaf95ad93ac7f771da11ed0cf4c3043bed2f`.

The bounded state audit covered 62,208 raw combinations / 41,472 valid states, with zero nondeterminism, conflicts, mandatory-invariant violations, trace gaps, counterfactual violations, temporal violations, or metadata/domain invariance violations. The 144 Protocol-v1 scenarios were not subjectively relabeled into v2 gold. Final Gate-B CI run `31788997247` was green across Python 3.10/3.11/3.12. Gate B verdict: `GATE B — PASS`.

Preserved Gate-B CI incidents: `31788612273` exposed a workflow assertion problem; `31788931319` exposed Unicode text-matching fragility after the formal audit itself had passed. Fixes changed CI parsing, not scientific criteria.

## 2026-08-14 — Gate C authorization and isolation

Created `research/proactivity-benchmark-v2` from exact Gate-B PASS commit `89e00052d68b2862269daf2adc8b31ebb1ae592c` and Draft PR #8 stacked on `research/proactivity-specification-v2`. Gate-C criteria were preregistered before formal benchmark statistics. The frozen specification/oracle were treated as upstream dependencies and were not modified for benchmark convenience.

## 2026-08-14 — Gate C representation and anti-circularity contract

Defined two tracks: Track A for mechanistic structured-state diagnostics and Track B for deterministic synthetic semantic observations. Candidate-visible transport is separated from oracle-private state/action/rule/prohibition/relation metadata. Future candidate source is forbidden from importing the reference oracle/benchmark implementation or reading private benchmark evidence at runtime; machine-checkable guards and failure-path tests enforce this boundary.

The deterministic public holdout is explicitly not treated as independent Gate-F protected evidence.

## 2026-08-14 — Gate C initial scientific failure preserved

Run `31791152951` passed frozen-upstream and deterministic-regeneration checks but the formal Gate-C audit returned:

```text
GATE C — FAIL: BENCHMARK_VALIDITY_CRITERIA_NOT_MET
reason: TEMPLATE_DOMINANCE
```

Initial three-template allocation was `65/45/58` over 168 records; largest share 38.69% exceeded the preregistered 34% maximum. No threshold was relaxed. No specification, oracle, state, gold action, or relation criterion changed. Remediation added a fourth genuinely distinct **non-normative observation paraphrase family**, producing final `41/38/39/50` distribution and 29.76% maximum share. Generator version advanced to `2.0.1`.

## 2026-08-14 — Gate C infrastructure incident preserved

Run `31791651373` exposed `ModuleNotFoundError: scripts` in the Gate-C audit wrapper after remediated benchmark regeneration had succeeded. This was classified as infrastructure, not a scientific benchmark failure. The wrapper was made path-independent; no benchmark threshold, normative spec, oracle, or gold label changed.

## 2026-08-14 — Final Gate C benchmark evidence

Final benchmark `benchmark_v2` contains 168 unique source states / opaque IDs. Action distribution is ACT 16, ASK 50, IGNORE 15, NOTIFY 38, SUGGEST 16, WAIT 33. Natural exhaustive distribution remains separately reported and was not represented as natural benchmark prevalence.

Audit results:

- manual gold: 0;
- LLM gold: 0;
- oracle mismatch: 0;
- exact candidate duplicates: 0;
- structural/source-state duplicates: 0;
- forbidden candidate metadata: 0;
- direct action-label token leakage: 0;
- candidate/private forbidden overlap: 0;
- split-family leakage: 0;
- all six actions covered;
- every reachable selected non-fallback rule covered;
- every hard prohibition covered with trigger evidence and one action-changing counterfactual;
- generic counterfactual families 8 / violations 0;
- prohibition counterfactual families 8 / violations 0;
- temporal sequences 8 / violations 0;
- hard-prohibition safety violations 0;
- deterministic regeneration PASS.

Split counts: development 91, validation 33, public deterministic holdout 44. The holdout is not Gate-F independent evidence.

Artifact hashes are frozen in `gate_c/freeze_v2.json`.

## 2026-08-14 — Final Gate C CI and verdict

Passing source commit before final documentation: `6653424a3e90b4b67c792bc9e0a15762d3d6966e`.

GitHub Actions run `31791713759` completed successfully on Python 3.10, 3.11, and 3.12. Each matrix job passed the formal Gate-C audit/decision, Gate-B regression, Protocol-v1 negative-evidence preservation, deterministic double regeneration, and the complete **73-test** pytest suite.

Final machine verdict:

```text
GATE C — PASS
READY FOR GATE D
DO NOT START GATE D
```

Protocol-v2 evidence-weighted completion is now **48%**: 10% scope + 20% formal specification + 15% oracle/benchmark validity + 3% reproducibility. Independent reproduction remains incomplete; Gates D–H remain unexecuted.

## 2026-08-14 — Gate D preregistration and compatibility amendment

Created `research/proactivity-baselines-v2` from exact Gate-C freeze HEAD `b26aa39866e5cc7aa99ba97d71862f7550a447fe`, Issue #9, and Draft PR #10. Gate-D criteria were preregistered before formal baseline scoring.

The initial preregistration named `scikit-learn==1.8.0`. Before any formal score existed, compatibility checking showed that the required Python 3.10/3.11/3.12 matrix could not be satisfied by that line. Amendment D-001 at `17920b1f86267727a2a7b4baf9672ec265267a1a` pinned `scikit-learn==1.7.1`. No benchmark, label, baseline family, feature definition, hyperparameter, metric, seed, PASS criterion, or scientific meaning changed.

## 2026-08-14 — Gate D formal baseline evidence

Formal source commit: `6377d31eaa57f162df68c4c3f89c7b6cb7e0206c`. GitHub Actions run `31801340084` succeeded on Python 3.10, 3.11, and 3.12.

Validation results:

| Baseline | Accuracy | Macro-F1 | Forbidden ACT |
|---|---:|---:|---:|
| B0 majority | 0.3333 | 0.0833 | 0 |
| B1 prior-sampled random | 0.2424 | 0.1662 | 1 |
| B2 domain-only | 0.3030 | 0.1197 | 0 |
| B3 simple lexical | 0.1212 | 0.1071 | 5 |
| B4 strong classical | 0.3333 | 0.1562 | 0 |
| B5 transparent heuristic | 0.1818 | **0.2145** | 0 |

All required baseline implementations, candidate/private boundary checks, frozen benchmark hashes, failure-path tests, prediction coverage, valid-action coverage, metric recomputation, row-order invariance, and deterministic repeat checks passed. Controls produced domain-ablation macro-F1 `0.1602564103`, observation-shuffle `0.1336212807`, label-permutation `0.0939393939`, and token-shuffle `0.1216931217`.

The full report and all six prediction files were byte-identical across the three Python versions. Canonical full report SHA-256: `af08e71950b28148a5f4d1a67a336d2ee8a43baf4ed7813600a54d6d25a80be9`.

Strongest honest raw-context baseline is B5 with macro-F1 `0.21452991452991452`. This result is frozen for Gate-E comparison. B1's one forbidden ACT and B3's five forbidden ACT predictions are preserved as negative baseline evidence rather than hidden.

Gate-D machine verdict: `GATE D — PASS`. Protocol-v2 evidence-weighted completion advances to **63%**.

## 2026-08-14 — Gate D documentation-integrity incident preserved

Freeze commit `3352fbe98da3f681cd34f81b6cf66a13b2b1cdd3` correctly added Gate-D evidence artifacts but over-compressed the pre-existing research documentation. A diff audit caught the excessive deletion before Gate D was closed. The corrective commit restored the Gate-C document bodies and limited edits to Gate-D additions/status changes. This is classified as a documentation/infrastructure integrity defect; no scientific evidence, benchmark, specification, oracle, score, or criterion changed.

## 2026-08-14 — Gate E preregistration and source freeze

Created `research/proactivity-candidate-v2` from exact Gate-D terminal HEAD `cbb73cde89ac74f194c19d52e14379223ddc8c8a`. Gate-E preregistration commit `da6f205f4c1aff001b9f24b4782a44a94e885acd` froze the six-configuration search budget, Gate-D B5 comparator, eligibility rules, paired-bootstrap procedure, and no-protected-test rule before formal candidate evaluation.

Development-only engineering produced an independently implemented raw-observation semantic-factor extractor. Candidate source was frozen at `554da731c962cdbf2ebd63cb65149f393e05b617` before formal validation. Subsequent CI explicitly checks `src/proactivity/candidate_v2.py` is unchanged from that commit.

## 2026-08-14 — Gate E protected-isolation pre-scoring fix

After the evaluator was added at `c3c814c6020d0fb9b47a0bf71b6d80b67202c1d9`, audit found that the initial loader would parse the entire private JSONL before subsetting. No formal Gate-E validation result had yet been generated. Commit `8ad2411b5db48cfe180bb500c996a7557abbda9b` replaced it with split-first isolation: protected candidate/private lines are recognized only by scenario ID and skipped without JSON parsing their payload. Candidate source and scientific criteria were unchanged.

## 2026-08-14 — Gate E formal candidate evidence

Formal CI enable commit `fc030269e347142d5a9ad730499d189647ccded7`; run `31804595710` succeeded on Python 3.10, 3.11, and 3.12. Every matrix job re-ran upstream Gates B–D, the complete 79-test regression suite, Protocol-v1 negative-evidence validators, candidate-source immutability, two Gate-E evaluations, terminal criteria, and evidence upload.

The three formal reports and all six candidate prediction files were byte-identical across Python versions. Canonical full report SHA-256: `d3bdb01ea4e37f763ae8c973b86ee6600cf1c774bc62bf82e22aff746f86702f`.

Selected candidate: `C5_semantic_factor_linear`. Validation macro-F1 `0.6936507936507935`, accuracy `0.6666666666666666`, weighted F1 `0.677922077922078`, valid-action rate 100%, forbidden ACT 0, six-action recall all non-zero. Frozen B5 delta: `+0.479120879120879`. 10,000 paired bootstrap resamples gave mean delta `0.4721225669070198`, 95% interval `[0.269140495727183, 0.6969364243570899]`, and fraction delta > 0 `1.0`.

C1–C3 each produced five forbidden ACT predictions and failed all-six-action-recall eligibility; C4 and C6 passed eligibility but scored below C5. Protected candidate/private payload rows parsed by Gate E: zero. Gate-F protected data remains not generated.

Gate-E formal-source verdict: `GATE E — PASS`. Evidence-weighted Protocol-v2 completion is **78%** once the terminal freeze HEAD itself completes regression CI.

## 2026-08-15 — Gate E terminal closeout

The previously pending terminal-freeze condition was rechecked against live GitHub state rather than README status text. Candidate branch verification HEAD `2f19671371e2bd81ee14ecd6819a2945155f0e86` completed GitHub Actions run `31806809694` successfully on Python 3.10, 3.11, and 3.12. All required jobs executed Gate-E chronology and candidate-source immutability checks, repeated formal Gate-E evaluation, terminal criteria, upstream regressions, Protocol-v1 negative-evidence preservation, and evidence upload.

The scientific Gate-E result remains anchored to `fc030269e347142d5a9ad730499d189647ccded7` / run `31804595710`; the later verification and documentation commits are administrative/reproducibility evidence and are not relabeled as the scientific scoring commit.

Diff audit from candidate-source freeze `554da731c962cdbf2ebd63cb65149f393e05b617` through verification HEAD showed no modification to `src/proactivity/candidate_v2.py`. `SCIENTIFIC_SOURCE_IMMUTABLE = YES`.

Formal CI artifacts were downloaded and byte-compared across Python 3.10/3.11/3.12. Identical hashes were confirmed for:

- Gate-E report: `d3bdb01ea4e37f763ae8c973b86ee6600cf1c774bc62bf82e22aff746f86702f`;
- C5 prediction: `2b31c30d417c86c8c3e346d3b35579668b5852a289ffb9c6e15bf9fbec5c556d`;
- Gate-E preregistration: `75d2864b82cb48d1c77a9d3992c30de792e99c0b4167ef5fb5daf143ffaf5b84`;
- candidate source: `78d4cbdf6190cd8d87927d4efbce63ef29e3dacb902c44c1b3d5004a290aae5b`.

Gate-E protected candidate/private payload rows parsed remained zero and Gate-F protected data had not been generated at the time of this decision. Protocol-v1 BLOCKED evidence and Gate-C/Gate-D/Gate-E negative results remain preserved.

Decision: `GATE E — PASS`. Evidence-weighted Protocol-v2 completion remains **78%**. This supports only the bounded validation claim under the controlled synthetic representation; it does not support protected/OOD generalization, robustness, human preference alignment, deployment safety, or real-world autonomy claims.

Exact next gate: Gate F protected/OOD confirmatory evaluation, beginning with preregistration on a new branch from the final Gate-E administrative closeout state. The frozen Candidate must not be modified.

## 2026-08-15 — Gate F preregistration, protected generation, and terminal FAIL

Gate F started from final Gate-E HEAD `a9ca08024e42a6a926a4cb015af7f745880f894d`. The first Gate-F commit was preregistration `7c445c4928dcb09c7b3864fec0ada0aef4570d1c`; no protected examples or labels existed before that commit. The frozen candidate remained `C5_semantic_factor_linear` with source SHA-256 `78d4cbdf6190cd8d87927d4efbce63ef29e3dacb902c44c1b3d5004a290aae5b`. Independence was honestly classified Level C: process-isolated candidate-blind generation within the same research orchestration lineage, not external/human independent.

Generator source `eeb509ef4d8cbd24d4a9ab6c228634ca0b9a98fa` and manifest `21e729e93888716f71be67f9253cc191066343d8` were frozen before generation. Run `31880132838` succeeded on Python 3.10/3.11/3.12 and produced byte-identical 120-case protected artifacts: inputs `8817cef5026a2e118d3f850653cd400a06316584510922c89c94fed79a16b971`, labels `21f6b4ba7843f3d90f269944a3a675ba7428edf1baece5ac6472e2196133c332`, private evidence `fb9f819dd9020951ec4145efafa5e78088cadee1ad3c07b4c734a88dd6b7c9a5`. The generated bytes were committed without regeneration at `7132bb17978310ad8003e834c8f012253e445b04`.

Before scoring, leakage audit = NONE; candidate source, generator source/manifest, protected artifacts, and scorer hashes were frozen. Formal one-shot scoring occurred at `23d183086368d0921c9af2f6c326d4c97214f267`, run `31880421048`. Python 3.10/3.11/3.12 all completed successfully, and report, candidate predictions, baseline predictions, bootstrap output, and formal marker were byte-identical. Canonical report SHA-256 is `d49cbdab7d43a190b9e278657906d95a2bd29d5b0db4dbd9e39b1031ba8c0b3f`; candidate prediction SHA-256 is `5785a180a4c5c2d01b7a94ee7c511263894f89267f910faf69090e4e560940d9`.

C5 protected accuracy `0.16666666666666666`, macro-F1 `0.047619047619047616`, weighted-F1 `0.04761904761904761`. B5 protected macro-F1 `0.09417989417989418`; delta `-0.04656084656084657`. Paired bootstrap 95% interval `[-0.08583374363752445, -0.006802939152846802]`, fraction delta > 0 = `0.0104`. C5 predicted IGNORE on all 120 cases and solved 0/24 action-changing counterfactual pairs exactly.

Safety/hash criteria passed: valid-action rate 1.0, invalid actions 0, forbidden ACT 0, protected hashes matched, candidate hash matched. Performance criteria failed: macro-F1 threshold, +0.20 baseline delta, positive bootstrap lower bound, and all-six-action recall. Therefore the formal decision is `GATE F — FAIL`. This negative evidence is retained and the protected set is retired for confirmatory use in the C5 lineage. No C5 tuning/retest on this set is permitted. Evidence-weighted completion remains 78%; Gates G/H remain unexecuted.
