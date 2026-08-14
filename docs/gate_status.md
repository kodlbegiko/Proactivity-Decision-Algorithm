# Gate Status — 2026-08-14 — Protocol v2

## Historical Protocol v1

Protocol v1 remains preserved as historical negative evidence:

- Gate A: `PASS (narrowed)`;
- Gate B: `BLOCKED_BY_INDEPENDENT_ANNOTATION`;
- evidence-weighted completion: **25%** under the v1 weighting;
- genuinely independent human annotation: **NOT EXECUTED**;
- raw agreement / Cohen's kappa / human-label-dependent leakage checks: **NOT EXECUTED**.

Protocol v2 does not retroactively convert those missing results into passes.

## Protocol v2

### Gate A — Scope / claim boundary / prior art: PASS (narrowed)

The primary target is specification-grounded intervention control. Novelty remains `PARTIAL NOVELTY ONLY`. Human preference alignment, universal correctness, user satisfaction, and unsupported ecological-validity claims remain outside the current evidence boundary.

### Gate B — Formal Specification Validity: PASS

Frozen upstream:

- branch `research/proactivity-specification-v2`;
- commit `89e00052d68b2862269daf2adc8b31ebb1ae592c`;
- policy `PDA-SPEC-v2`;
- schema `2.0.0`;
- spec SHA-256 `ea06eeb85ffa375740e778d273b57d79e7f4f96d0eb68eb74ed2ef9df6d827a4`;
- oracle source SHA-256 `11ec7557d4809b18e1c414d9a3b0eaf95ad93ac7f771da11ed0cf4c3043bed2f`.

Gate-B bounded-state evidence remains 62,208 raw combinations, 41,472 valid states, zero nondeterministic outputs, zero final-action conflicts, zero unexplained fallback selections, complete traces, zero mandatory-invariant violations, zero metadata/domain invariance violations, 140 counterfactual cases with zero violations, and the reference temporal transition `WAIT -> NOTIFY -> WAIT -> IGNORE` with zero violations.

Historical Gate-B CI incidents remain preserved: run `31788612273` exposed a workflow assertion problem; run `31788931319` showed the formal Gate-B PASS but failed on Unicode text matching. The typed assertion repair did not weaken any Gate-B rule or criterion. Final Gate-B run `31788997247` was green on Python 3.10/3.11/3.12.

### Gate C — Oracle and Benchmark Validity: PASS

Machine verdict:

```text
GATE C — PASS
READY FOR GATE D
DO NOT START GATE D
```

Gate-C branch/PR:

- branch `research/proactivity-benchmark-v2`;
- Draft PR #8, stacked on `research/proactivity-specification-v2`;
- Gate-B normative artifacts unchanged throughout Gate C.

Final benchmark freeze:

- version `benchmark_v2`;
- generator `2.0.1`;
- seed `20260814`;
- scenarios / unique IDs: **168 / 168**;
- action counts: ACT 16, ASK 50, IGNORE 15, NOTIFY 38, SUGGEST 16, WAIT 33;
- splits: development 91, validation 33, deterministic public holdout 44;
- candidate hash `7e9826fe4f0b59aa92556048bf45abc44e525644dc27fca3425c140350b1e587`;
- private hash `9d15c5a2f4454f049c7f60ee26f7247efc583b718c115e59293a8c95c3985ae8`;
- relations hash `8cf4d939378185accb4b5506620c626fa83d566114140ba692ffd085dbc8bd66`;
- splits hash `9b9ffdfad6ca0561d2142723053c3582a748e5fefc60b37e5e82762dd1544a27`;
- structured hash `a1533cd6289fd8a97b2c92c26d3f78172c32ebf4203cb47e0f9ccdad7e7f149e`.

Ground-truth / circularity evidence:

- 168/168 records oracle-derived;
- manual gold findings: 0;
- LLM gold findings: 0;
- oracle mismatches: 0;
- candidate/private forbidden-field overlap: 0;
- candidate direct answer-token findings: 0;
- future candidate forbidden-import/private-path guard implemented and tested.

Diversity / leakage evidence:

- exact candidate duplicates: 0;
- structural/source-state duplicate members: 0;
- template distribution: `41 / 38 / 39 / 50`;
- largest template share: **29.76%**, below preregistered 34%;
- domain distribution: communication 30, device 20, scheduling 30, study 28, travel 22, work 38;
- forbidden metadata findings: 0;
- high-purity forbidden lexical answer leaks: 0;
- split-family leakage: 0.

Coverage / relation evidence:

- all six actions meet the preregistered minimum;
- every reachable selected non-fallback rule meets the preregistered minimum;
- all eight hard prohibitions meet trigger coverage and each has one action-changing counterfactual pair;
- generic counterfactual families: 8, violations 0;
- prohibition counterfactual families: 8, violations 0;
- temporal sequences: 8, violations 0;
- hard-prohibition safety violations: 0.

Reproducibility / CI:

- benchmark regenerated repeatedly with byte-identical hashes;
- final source commit before status documentation: `6653424a3e90b4b67c792bc9e0a15762d3d6966e`;
- GitHub Actions run `31791713759`: SUCCESS on Python 3.10, 3.11, 3.12;
- complete pytest suite: **73 passed per matrix job**;
- evidence artifacts uploaded for all three Python versions.

#### Preserved Gate-C incidents

1. **Scientific generator failure — run `31791152951`.** Initial three-template distribution `65/45/58` produced a 38.69% largest-family share, violating the preregistered 34% maximum. This was recorded as `TEMPLATE_DOMINANCE`. Remediation added a fourth non-normative paraphrase family. The normative spec, oracle, gold actions, and threshold were unchanged.
2. **Infrastructure failure — run `31791651373`.** Gate-C audit wrapper raised `ModuleNotFoundError: scripts` after benchmark regeneration. The wrapper path was repaired without changing the benchmark criterion, specification, oracle, or labels.

### Protected-test limitation

The Gate-C `protected_test` split is deterministic and publicly regenerable. It validates grouping/freeze mechanics only and does **not** count as Gate-F independent protected-validation evidence.

### Gate D — Baseline Integrity: PASS

Gate-D branch/PR/Issue:

- branch `research/proactivity-baselines-v2`;
- Draft PR #10 stacked on `research/proactivity-benchmark-v2`;
- Issue #9;
- base Gate-C freeze HEAD `b26aa39866e5cc7aa99ba97d71862f7550a447fe`.

Preregistration and implementation:

- initial preregistration commit `2ff15cc095c168d16f6711b1c4aa131fb625595d`;
- amendment D-001 commit `17920b1f86267727a2a7b4baf9672ec265267a1a`;
- formal implementation commit `6377d31eaa57f162df68c4c3f89c7b6cb7e0206c`;
- pinned dependency `scikit-learn==1.7.1`.

D-001 was made **before formal scoring** solely because the initially named scikit-learn 1.8.x line could not satisfy the preregistered Python 3.10/3.11/3.12 matrix. No benchmark, label, feature definition, baseline family, hyperparameter, metric, seed, PASS criterion, or scientific meaning changed.

Formal Gate-D CI run `31801340084` completed successfully on Python 3.10, 3.11, and 3.12. It re-ran Gate-B and Gate-C regressions, executed B0–B5 twice, passed source-boundary failure paths, prediction coverage, fixed-seed determinism, benchmark hashes, metric recomputation, row-order invariance, the complete regression/failure-path suite, Protocol-v1 negative-evidence checks, and uploaded three evidence artifacts.

The canonical full Gate-D report SHA-256 is `af08e71950b28148a5f4d1a67a336d2ee8a43baf4ed7813600a54d6d25a80be9`; report and all six prediction files were byte-identical across Python 3.10/3.11/3.12.

Strongest honest raw-context baseline by validation macro-F1 is `B5_transparent_heuristic` at **0.21452991452991452**. This is frozen as the Gate-E comparison baseline.

Negative baseline results are preserved: B1 made one forbidden-ACT prediction and B3 made five. Gate D is an integrity gate, so these are not hidden or misrepresented as candidate evidence.

#### Preserved Gate-D documentation incident

Freeze commit `3352fbe98da3f681cd34f81b6cf66a13b2b1cdd3` correctly froze the experiment artifacts but over-compressed existing documentation. Diff audit detected that this violated the documentation-preservation rule. The fix restored the Gate-C documents and applied only Gate-D additions/necessary status changes. Scientific artifacts, benchmark, oracle, criteria, scores, and source commit were unchanged.

### Gate E — PDA Candidate Evidence: FORMAL-SOURCE PASS / TERMINAL FREEZE CI PENDING

Gate-E branch/PR/Issue:

- branch `research/proactivity-candidate-v2`;
- Draft PR #12 stacked on `research/proactivity-baselines-v2`;
- Issue #11;
- exact Gate-D terminal base `cbb73cde89ac74f194c19d52e14379223ddc8c8a`.

Preregistration / chronology:

- preregistration commit `da6f205f4c1aff001b9f24b4782a44a94e885acd`;
- candidate source freeze commit `554da731c962cdbf2ebd63cb65149f393e05b617`;
- candidate source SHA-256 `78d4cbdf6190cd8d87927d4efbce63ef29e3dacb902c44c1b3d5004a290aae5b`;
- evaluator added after source freeze at `c3c814c6020d0fb9b47a0bf71b6d80b67202c1d9`;
- protected-payload isolation fix before formal scoring at `8ad2411b5db48cfe180bb500c996a7557abbda9b`;
- formal CI enable commit `fc030269e347142d5a9ad730499d189647ccded7`.

The pre-scoring isolation audit found that the initial Gate-E evaluator would parse the complete private JSONL before subsetting. Before any formal validation score was produced, the loader was replaced with split-first isolation that recognizes protected rows only by scenario ID and skips their candidate/private payloads without JSON parsing. Candidate source, search budget, thresholds, baseline comparator, and scientific criteria were unchanged.

Formal Gate-E run `31804595710` succeeded on Python 3.10, 3.11, and 3.12. Every matrix job re-ran upstream Gates B–D, complete 79-test regression, Protocol-v1 negative-evidence validators, candidate-source immutability, two formal Gate-E evaluations, terminal criteria, and evidence upload. The full Gate-E report SHA-256 was byte-identical across environments: `d3bdb01ea4e37f763ae8c973b86ee6600cf1c774bc62bf82e22aff746f86702f`.

Selected candidate: `C5_semantic_factor_linear`.

- validation accuracy: **0.6666666667**;
- validation macro-F1: **0.6936507937**;
- validation weighted F1: **0.6779220779**;
- frozen B5 macro-F1: **0.2145299145**;
- macro-F1 delta: **+0.4791208791**;
- valid-action rate: **100%**;
- forbidden ACT: **0**;
- all six actions non-zero recall: **true**;
- validation prediction SHA-256: `2b31c30d417c86c8c3e346d3b35579668b5852a289ffb9c6e15bf9fbec5c556d`.

Paired bootstrap, 10,000 samples, seed `20260814`: mean delta `0.4721225669`, 95% interval `[0.2691404957, 0.6969364244]`, fraction delta > 0 = `1.0`.

Negative candidate evidence is retained: C1–C3 each produced five forbidden ACT predictions and failed the all-six-action-recall eligibility rule; C4 and C6 were eligible but scored below C5. Protected candidate/private payload rows parsed in Gate E = 0. Gate-F protected/OOD data remains **NOT GENERATED**.

The experiment evidence is frozen in `gate_e/freeze_v2.json`. Gate E must not be marked terminal PASS, Issue #11 must not close, and Gate F must not start until the current evidence/documentation freeze HEAD itself passes the full Python 3.10/3.11/3.12 regression CI.

## Gates F–H

**NOT EXECUTED.**

No independent protected/OOD result, robustness claim, ablation result, independent clean reproduction result, merge, or release has been executed yet.

## Protocol-v2 evidence-weighted completion

| Evidence area | Weight | Supported after terminal Gate-E freeze CI |
|---|---:|---:|
| Research scope / claim definition | 10% | 10% |
| Formal specification validity | 20% | 20% |
| Oracle / benchmark validity | 15% | 15% |
| Baseline integrity | 15% | 15% |
| Candidate evidence | 15% | 15% |
| Protected validation | 10% | 0% |
| Robustness | 5% | 0% |
| Ablation | 5% | 0% |
| Reproducibility / independent reproduction | 5% | 3% |
| **Total** | **100%** | **78%** |

The remaining 2/5 reproducibility credit is withheld because independent clean-environment reproduction/audit has not been performed.

## Exact next scientifically valid action

`Gate F — Protected / OOD Validation`, but only after the Gate-E terminal freeze HEAD passes full regression CI.
