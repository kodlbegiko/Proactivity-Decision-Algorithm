# Candidate-v11 Terminal Report

**Terminal State:** `FRESH CONFIRMATORY PASS — READY_FOR_GATE_G_AUTHORIZATION`

## Evidence

- Selected architecture: `V11-A`
- Candidate freeze: `2d87fbf19d4715bdfaa3eb56e817b64cbdb2239e`
- Development qualification: V11-A PASS; V11-B PASS; V11-C PASS; V11-D NOT IMPLEMENTED.
- H1-H16: ALL PASS.
- Protected seed: `113001`; n = 3,600.
- Protected dataset SHA256: `1ee9f1ddc6cc19a9f91a08abecf405d3005c477651671e594b88a0b62763aa6e`
- Protected Macro-F1: 1.000000
- Protected ACT precision / recall: 1.000000 / 1.000000
- Protected critical-factor accuracy: 0.979166666667
- Protected contradiction detection: 1.000000
- Protected counterfactual directional / ACT-disable: 1.000000 / 1.000000
- Protected forbidden ACT / false ACT: 0 / 0
- Protected state validity / invalid states: 1.000000 / 0
- Protected max action share: 0.333333333333
- Integrity: PASS; no Candidate-v10 failed individual evidence, failed formal-holdout rows, or protected individual rows were inspected.

## Supported claim

Within the preregistered deterministic synthetic evaluation family, frozen V11-A passed the development gates, all sixteen fresh formal holdouts, and the one-shot protected confirmatory evaluation while preserving the PDA-SPEC-v2 ACT safety invariants.

## Unsupported claims

This does **not** establish unrestricted natural-language understanding, human-preference ground truth, real-world deployment readiness, or Gate G completion. The generators deliberately preserve independently authored semantic-definition scaffolds while varying lexical roots, syntax, domains, discourse structure, contradiction, scope, supersession, uncertainty, and counterfactual factors.

## Known limitation

Development cross-factor critical-factor accuracy was `0.9860833333333333` (confusion `0.013916666666666688`) and protected critical-factor accuracy was `0.9791666666666666` rather than 1.0. The controlled generator family is substantially narrower than unconstrained human language.

## Next critical path

Candidate-v11 is eligible for an independently authorized Gate G process. Do not tune or reinterpret the frozen Candidate-v11 lineage before that authorization.
