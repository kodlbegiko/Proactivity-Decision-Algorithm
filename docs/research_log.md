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
