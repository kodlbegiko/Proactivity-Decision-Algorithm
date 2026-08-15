# Gate F Terminal Report — Protocol v2

## Decision

**FAIL**

The frozen `C5_semantic_factor_linear` candidate did not satisfy the preregistered Level-C process-isolated protected/OOD confirmatory criteria. No candidate tuning or protected-set regeneration is authorized from this result.

## Chronology and isolation

- Gate-E candidate source freeze: `554da731c962cdbf2ebd63cb65149f393e05b617`
- Gate-F preregistration: `7c445c4928dcb09c7b3864fec0ada0aef4570d1c` — before protected generation
- Protected generation run: `31880132838` — Python 3.10/3.11/3.12 success and byte-identical outputs
- Protected-data freeze: `7132bb17978310ad8003e834c8f012253e445b04`
- Formal scientific scoring SHA: `23d183086368d0921c9af2f6c326d4c97214f267`
- Formal scoring run: `31880421048` — Python 3.10/3.11/3.12 success
- Leakage audit before scoring: `NONE`
- Candidate source immutable: `YES`
- Protected set immutable: `YES`
- Independence classification: **Level C**, process-isolated candidate-blind generation; not external/human-independent

## Protected set

- n = 120
- ACT / ASK / IGNORE / NOTIFY / SUGGEST / WAIT = 20 each
- 24 disjoint single-field action-changing counterfactual pairs
- 6 domains = 20 each
- 4 protected rendering families = 30 each

## Formal result

| Metric | C5 | B5 |
|---|---:|---:|
| Accuracy | 0.166667 | 0.191667 |
| Macro-F1 | 0.047619 | 0.094180 |
| Weighted-F1 | 0.047619 | 0.094180 |
| Valid-action rate | 100.0% | 100.0% |
| Forbidden ACT | 0 | 0 |

Macro-F1 delta C5−B5: `-0.04656084656084657`.

Paired bootstrap, 10,000 resamples, seed `2026081501`: 95% interval `[-0.08583374363752445, -0.006802939152846802]`; fraction delta > 0 = `0.0104`.

## Preregistered criteria

Failed:

- protected macro-F1 >= 0.50 — observed `0.047619047619047616`
- delta vs B5 >= +0.20 — observed `-0.04656084656084657`
- paired-bootstrap lower 95% bound > 0 — observed `-0.08583374363752445`
- non-zero recall for all six actions — observed `false`

Passed:

- valid-action rate = 1.00
- invalid-action count = 0
- forbidden ACT count = 0
- protected hashes match
- candidate source hash matches the Gate-E freeze

## Negative evidence

C5 predicted `IGNORE` on all 120 protected examples. Its action-distribution collapse produced recall 1.0 only for IGNORE and zero recall for ACT, ASK, NOTIFY, SUGGEST, and WAIT. It solved 0/24 protected action-changing counterfactual pairs exactly. B5 also performed poorly, but still exceeded C5 on protected macro-F1.

This is a substantive generalization failure under the preregistered Level-C protected distribution, not a CI failure.

## Claim boundary

Gate F does **not** support protected/OOD confirmation for this frozen candidate. It does not establish anything broader about human preference, real-world autonomy, deployment safety, unrestricted language understanding, or arbitrary-distribution generalization.

## Research-integrity consequence

The Gate-F protected set is retired as confirmatory evidence for this candidate lineage. It must not be used to tune C5 and then reused to claim a Gate-F pass. Any future recovery requires a new development/candidate lineage and, before any new confirmatory claim, a fresh protected evaluation not used for development. Gate G is not started from this failed Gate-F lineage.
