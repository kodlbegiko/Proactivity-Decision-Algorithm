# Benchmark v1 Gate-B Preregistration — HISTORICAL PROTOCOL v1

Status: **HISTORICAL / SUPERSEDED AS PRIMARY TRACK**. This document preserves the methodology preregistered before independent human labels under Protocol v1. It is intentionally not rewritten as if that evidence occurred.

Protocol-v1 historical verdict remains `GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION`. Protocol v2 uses a different primary research question, ground truth, and gate architecture; see `docs/protocol_v2.md`.

## Dataset

- 144 development scenarios.
- six domains, 24 each.
- 24 counterfactual pairs (48 members).
- six 4-stage temporal sequences (24 members).
- no gold/preferred action stored with scenario generation.

## Primary track under Protocol v1

Raw-context projection was primary. Researcher-derived normalized scalar state was a secondary mechanistic/control track.

## Pre-annotation leakage requirements

- exact duplicate members: 0;
- normalized structural duplicate members: 0, excluding intentionally defined pair relations only if the structure changes on the preregistered changed variable;
- unrelated near-duplicate pairs at similarity >= 0.90: 0;
- forbidden hidden metadata in policy input: 0;
- opaque scenario IDs, no domain/category/label semantics;
- domain ordering must not create long homogeneous blocks (current gate <= 3 consecutive same-domain records).

## Post-annotation leakage requirements — NOT EXECUTED

Protocol v1 required, before its Gate B could pass:

- label-conditional lexical shortcut audit;
- shuffled/corrupted-feature controls;
- suspicious token/metadata correlation review;
- preservation of raw outputs.

These label-dependent checks were not executed because independent human labels were not collected. Protocol v2 does not retroactively mark them PASS.

## Annotation reliability — NOT EXECUTED

Protocol v1 required immutable first-pass independent human labels with:

- raw preferred-action agreement >= 0.80;
- Cohen's kappa >= 0.60;
- original labels hashed before adjudication.

No such human reliability result exists.

## Historical Gate-B rule

Under Protocol v1, Gate B could pass only after the novelty/overlap position was documented, development-v1 was valid, independent agreement passed, label-dependent leakage checks passed, and metric definitions were frozen sufficiently for baseline evaluation.

That rule remains historically true for Protocol v1 but is not the current Protocol-v2 Gate-B definition.
