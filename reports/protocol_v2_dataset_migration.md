# Protocol v2 Dataset Migration Audit

Date: 2026-08-14

## Decision

`development_v1` is preserved as Protocol-v1 evidence but is **not silently relabeled** into Protocol-v2 normative ground truth.

The 144 v1 scenarios contain useful raw-context, continuous scalar controls, six domains, counterfactual pairs, and temporal sequences. However, they do not encode the complete Protocol-v2 finite semantic state as explicit generator-known fields. In particular, Protocol v2 requires distinctions such as information status, intervention need, side-effect scope, clarification feasibility, and explicit finite risk/reversibility semantics. Inferring those missing fields from prose after the fact would introduce subjective hand-labeling under another name.

## Classification of the 144 existing scenarios

| Migration category | Count | Treatment |
|---|---:|---|
| A — directly reusable as v2 formal evidence | 0 | none |
| B — reusable after deterministic schema migration with complete source state | 0 | none demonstrated |
| C — ambiguous under the complete v2 formal state | 144 | preserve as v1; do not assign v2 oracle gold |
| D — intrinsically incompatible with v2 | 0 | none established |
| **Total** | **144** | |

Category C does not mean the scenarios are scientifically worthless. It means their full v2 normative state cannot be recovered without adding judgments that were not frozen in the original generator.

## What is reused

The following **design infrastructure**, rather than v1 labels, remains reusable:

- six-domain organization;
- deterministic generation and SHA-verification pattern;
- counterfactual testing concept;
- temporal-sequence testing concept;
- raw-context rendering as a future secondary track;
- leakage/metadata-separation lessons;
- fail-closed validation conventions;
- CI and reproducibility infrastructure.

## Protocol-v2 development benchmark

`scripts/generate_development_v2.py` creates a new machine-grounded development set from explicit finite states. Each expected action is computed by the frozen reference oracle. The generator never maintains a separately handwritten action lookup.

The v2 development artifact is intentionally a **development/reachability set**, not Gate-C candidate evidence. Its purposes at this stage are to verify deterministic generation, ensure all six action modes are reachable, bind rows to the specification hash, and exercise the oracle/validator transport path.

Formal benchmark validity remains a Gate-C question and is not claimed by the Gate-B migration.
