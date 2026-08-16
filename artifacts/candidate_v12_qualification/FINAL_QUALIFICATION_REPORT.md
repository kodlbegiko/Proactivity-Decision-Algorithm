# Candidate-v12 Independent Qualification — Final Report

## A. Candidate identity

Frozen commit `7fe5c915c8139888bc4925282d11b42a223cbf25` exists, but the five preregistered values described as frozen blob identities do not resolve as Git blob objects. The files at the frozen commit have different actual Git blob SHAs. Candidate identity gate therefore fails before protected evaluation.

Hard-stop decision: **`QUALIFICATION INVALID — FROZEN CANDIDATE IDENTITY MISMATCH`**.

## B. Qualification design

Preregistration was committed as `c7b8e3ef57e28c09a3d4f0d74e58e767cf39cebd` before protected generation. It froze five runs, 1,200 examples/run, eight major families, action balancing, factor coverage, 500+ counterfactual pairs, 500+ invariance groups, bootstrap CIs, acceptance gates Q-A through Q-J, no-peeking, and a protected seed commitment.

## C. Core results

Not evaluated. Qualification runs: **0**. Protected examples generated: **0**. No Macro-F1, latent-state, UNKNOWN, counterfactual, invariance, ACT, or policy-oracle metric is scientifically defined for this invalid lineage.

## D. Per-family results

Not evaluated because identity verification failed before dataset generation.

## E. Robustness

Not evaluated because no qualification run was executed.

## F. Integrity

- Candidate mutation: false.
- Protected raw leakage: false.
- Protected seed leakage: false.
- Post-hoc tuning: false.
- Protected examples generated: 0.
- Identity mismatch: **true (5/5 declared blob identities)**.
- Evaluation contamination by outcomes: false; no outcomes were produced.

The freeze manifest repeats the five declared 40-hex values, but direct Git blob lookup returns Not Found for each and no alternative hash algorithm is specified there. Therefore the frozen candidate identity asserted by the qualification prompt is not reproducible as a Git blob identity.

## G. Terminal decision

**INVALID**

Canonical terminal state:

`CANDIDATE_V12 QUALIFICATION INVALID — EVALUATION_INTEGRITY_FAILURE`

Specific hard-stop reason:

`QUALIFICATION INVALID — FROZEN CANDIDATE IDENTITY MISMATCH`

### Next scientifically authorized action

Do not modify Candidate-v12. Create an integrity-only repair that defines and records reproducible file identities from the frozen commit (prefer actual Git blob SHAs), independently verify them, then begin a new qualification lineage with fresh preregistration and fresh protected seed commitment. No Candidate-v12 performance claim may be made from this invalid lineage.
