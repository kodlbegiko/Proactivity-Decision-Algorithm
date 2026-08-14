# Research Log — Protocol v2

## Preserved upstream history

Protocol v1 remains blocked by missing genuinely independent human annotation; its negative evidence is not rewritten. Protocol v2 Gate B passed its bounded formal-specification audit after preserving CI-only incidents `31788612273` and `31788931319`. Gate C preserved scientific failure `31791152951` (template dominance 38.69% > preregistered 34%) and infrastructure failure `31791651373` (`ModuleNotFoundError`) before its final PASS.

## 2026-08-14 — Gate D Baseline Integrity

- Repository: `kodlbegiko/Proactivity-Decision-Algorithm`
- Branch: `research/proactivity-baselines-v2`
- Base: Gate-C freeze HEAD `b26aa39866e5cc7aa99ba97d71862f7550a447fe`
- Issue: #9
- Draft PR: #10
- Initial preregistration commit: `2ff15cc095c168d16f6711b1c4aa131fb625595d`
- Amendment D-001 commit: `17920b1f86267727a2a7b4baf9672ec265267a1a`
- Formal implementation commit: `6377d31eaa57f162df68c4c3f89c7b6cb7e0206c`
- Formal CI: run `31801340084`, success across Python 3.10/3.11/3.12
- Frozen dependency: `scikit-learn==1.7.1`
- Criteria changes: **none**
- Spec/oracle/benchmark changes: **none**

### Amendment D-001

Before any formal baseline score was generated, the initial `scikit-learn==1.8.0` pin was found incompatible with the preregistered Python 3.10/3.11/3.12 matrix. It was replaced by 1.7.1. This was an infrastructure-compatibility correction before result observation, not a scientific threshold or model change.

### Formal baseline evidence

| Baseline | Accuracy | Macro-F1 | Forbidden ACT |
|---|---:|---:|---:|
| B0 majority | 0.3333 | 0.0833 | 0 |
| B1 prior-sampled random | 0.2424 | 0.1662 | 1 |
| B2 domain-only | 0.3030 | 0.1197 | 0 |
| B3 simple lexical | 0.1212 | 0.1071 | 5 |
| B4 strong classical | 0.3333 | 0.1562 | 0 |
| B5 transparent heuristic | 0.1818 | **0.2145** | 0 |

Strongest honest raw-context baseline: B5, macro-F1 `0.21452991452991452`.

Controls: domain-ablation macro-F1 `0.1602564103`; observation-shuffle `0.1336212807`; label-permutation `0.0939393939`; token-shuffle `0.1216931217`; row-order shuffle identical `true`.

All six prediction files and the canonical full Gate-D report were byte-identical across Python 3.10/3.11/3.12. Canonical CI report SHA-256: `af08e71950b28148a5f4d1a67a336d2ee8a43baf4ed7813600a54d6d25a80be9`.

### Gate-D verdict

`GATE D — PASS`.

This PASS establishes baseline integrity only. It does not establish candidate superiority, protected/OOD generalization, robustness, or human-preference alignment. Evidence-weighted Protocol-v2 completion advances from 48% to **63%**.
