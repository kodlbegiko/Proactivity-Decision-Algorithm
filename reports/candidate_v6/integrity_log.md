# Candidate-v6 Integrity Log

- clean-context assertion: PASS
- historical protected individual evidence accessed: NO
- GitHub historical operations: metadata + exact-file allow-list only
- branch created from required base SHA `370aac305c14c4ddc2fa2f782cbb3f0fdde4f630`
- Candidate-v5 PR #19 metadata verified without diff/patch
- development data generated from fresh structured states
- candidate search: V6-B / V6-C / V6-D only
- validation selection: V6-B
- validation forbidden ACT: 0
- development holdout observed: counterfactual forbidden ACT = 4
- counterfactual exact-pair: 0.9777777778
- counterfactual directional accuracy: 0.9777777778
- no post-holdout tuning: YES
- protected generator created: NO
- protected seed generated: NO
- protected scoring executed: NO
- formal protected rerun: NO
- historical protected error analysis: NO

## Integrity note
The formal freeze manifest was materialized after the local development holdout runner. Candidate semantics/configuration were not changed after holdout observation, but this chronology deviation is preserved rather than hidden. In all cases, protected progression is prohibited because the mandatory counterfactual safety criterion already failed.

## Terminal
`CANDIDATE_V6 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`
