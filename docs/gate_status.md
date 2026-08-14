# Gate Status — 2026-08-14 — Protocol v2

## Historical evidence preserved

Protocol v1 remains `GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION` with 25% v1 evidence-weighted completion. Missing independent human annotations, agreement, kappa, and human-label-dependent checks remain missing; Protocol v2 does not retroactively turn them into passes.

Gate-B historical CI incidents remain preserved: run `31788612273` exposed a workflow assertion problem and run `31788931319` exposed a Unicode text-matching CI failure; neither changed the normative Gate-B criteria. Final Gate-B run `31788997247` was green on Python 3.10/3.11/3.12.

Gate-C historical failures remain preserved: run `31791152951` failed the preregistered template-dominance criterion (38.69% > 34%) and was repaired by adding a fourth non-normative paraphrase family; run `31791651373` exposed an import-path infrastructure failure. Neither fix changed the frozen specification, oracle, gold labels, or thresholds.

## Protocol v2 terminal status

- Gate A — **PASS (narrowed)**
- Gate B — **PASS**
- Gate C — **PASS**
- Gate D — **PASS**
- Gate E — **NOT EXECUTED**
- Gate F — **NOT EXECUTED**
- Gate G — **NOT EXECUTED**
- Gate H — **NOT EXECUTED**

### Gate D — Baseline Integrity: PASS

Branch: `research/proactivity-baselines-v2`  
Draft PR: #10  
Issue: #9  
Frozen Gate-C base: `b26aa39866e5cc7aa99ba97d71862f7550a447fe`  
Formal source commit: `6377d31eaa57f162df68c4c3f89c7b6cb7e0206c`  
Formal CI: `31801340084` — SUCCESS on Python 3.10 / 3.11 / 3.12.

All B0–B5 baselines were implemented. Frozen benchmark hashes matched, candidate/private/source-boundary violations were zero, all failure-path tests passed, validation coverage and valid-action rates were 100%, metric recomputation matched, row-order shuffle was invariant, and fixed-seed outputs were deterministic. The three Python matrix evidence artifacts contained byte-identical Gate-D reports and prediction files.

Strongest honest raw-context baseline by macro-F1: `B5_transparent_heuristic`, macro-F1 **0.2145299145**. This value is the Gate-E comparison baseline and must not be weakened post hoc.

Negative baseline behavior is preserved rather than hidden: B1 produced one forbidden ACT and B3 produced five forbidden ACT predictions. Gate D is an integrity gate, so these weak-baseline safety errors are reported evidence rather than grounds to claim candidate success.

Preregistration amendment D-001 changed the scikit-learn pin from 1.8.0 to 1.7.1 **before formal scoring** because the required Python 3.10 matrix is incompatible with 1.8.x. No benchmark, label, model family, hyperparameter, metric, seed, PASS criterion, or scientific meaning changed.

## Evidence-weighted completion

| Evidence area | Weight | Supported now |
|---|---:|---:|
| Research scope / claim definition | 10% | 10% |
| Formal specification validity | 20% | 20% |
| Oracle / benchmark validity | 15% | 15% |
| Baseline integrity | 15% | 15% |
| Candidate evidence | 15% | 0% |
| Protected validation | 10% | 0% |
| Robustness | 5% | 0% |
| Ablation | 5% | 0% |
| Reproducibility / independent reproduction | 5% | 3% |
| **Total** | **100%** | **63%** |

The remaining 2/5 reproducibility credit is withheld until Gate H clean-environment reproduction passes.

## Exact next scientifically valid action

`Gate E — PDA Candidate Evidence`.

Gate-C public `protected_test` remains ineligible as Gate-F protected evidence. No candidate, OOD, robustness, ablation, merge, or release claim exists yet.
