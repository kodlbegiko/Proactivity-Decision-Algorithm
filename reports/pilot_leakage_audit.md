# Pilot Structural Leakage Audit — 2026-08-13

## Scope

Audit `data/development/pilot_v0.jsonl` for exact structural template duplication after removing identifiers that should not define scenario substance: `scenario_id`, `timestamp`, and `domain`.

## Executed command

```bash
python scripts/audit_structural_leakage.py data/development/pilot_v0.jsonl
```

## Raw summary

```text
scenario_count=24
unique_structural_fingerprints=4
duplicate_groups=4
duplicate_members=24
duplicate_member_rate=1.000000
duplicate_group_sizes=6,6,6,6
structural_leakage_gate=FAIL
```

Exit code: `2` (expected failure on threshold breach).

## Interpretation

All 24 pilot scenarios belong to an exact duplicated structural template group once domain/id/timestamp are removed. The pilot is therefore **not suitable for formal model comparison, baseline ranking, or benchmark-performance claims**.

This does not invalidate its intended use as an executable schema, taxonomy, annotation-workflow, and CI pipeline pilot.

## Research decision

- Preserve the pilot as development infrastructure.
- Do not label it a validated benchmark.
- Do not tune candidate policies against it.
- Build the next development batch with greater structural diversity and controlled anti-leakage generation before attempting Gate B.

## Residual audits still required

This exact-structure test does not replace lexical, label-frequency, metadata, ordering, near-duplicate, or shuffled-feature controls. Those remain Gate B requirements.
