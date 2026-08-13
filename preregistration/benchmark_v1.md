# Benchmark v1 Gate-B Preregistration

Status: development methodology preregistered before independent labels.

## Dataset

- 144 development scenarios.
- six domains, 24 each.
- 24 counterfactual pairs (48 members).
- six 4-stage temporal sequences (24 members).
- no gold/preferred action stored with scenario generation.

## Primary track

Raw-context projection is primary. Researcher-derived normalized scalar state is a secondary mechanistic/control track.

## Pre-annotation leakage requirements

- exact duplicate members: 0;
- normalized structural duplicate members: 0, excluding intentionally defined pair relations only if the structure changes on the preregistered changed variable;
- unrelated near-duplicate pairs at similarity >= 0.90: 0;
- forbidden hidden metadata in policy input: 0;
- opaque scenario IDs, no domain/category/label semantics;
- domain ordering must not create long homogeneous blocks (current gate <= 3 consecutive same-domain records).

## Post-annotation leakage requirements

Before Gate B pass:

- run label-conditional lexical shortcut audit;
- run shuffled/corrupted-feature controls;
- document any suspicious token/metadata correlations and remediation;
- preserve raw outputs.

No exact numerical threshold for shuffled-control performance is invented before labels. The control must be interpreted against the strongest trivial/majority behavior once class distribution exists.

## Annotation reliability

Required on immutable first-pass independent human labels:

- raw preferred-action agreement >= 0.80;
- Cohen's kappa >= 0.60 (for two annotators);
- original labels hashed before adjudication.

If the threshold fails, the six-class benchmark is not frozen; diagnose taxonomy/guideline/scenario ambiguity first.

## Gate B rule

Gate B can pass only after the novelty/overlap position is documented, development-v1 is valid, independent agreement passes, label-dependent leakage checks pass, and metric definitions are frozen sufficiently for baseline evaluation.
