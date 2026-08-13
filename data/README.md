# Data

## `development/pilot_v0.jsonl`

**INFRASTRUCTURE PILOT ONLY — NOT FOR FORMAL POLICY COMPARISON.**

The 24-scenario pilot failed the structural template audit: all 24 members collapsed into four repeated structural templates of six members each (`duplicate_member_rate = 1.0`). The file is retained as negative evidence and for legacy schema/pipeline regression tests.

See `development/pilot_v0.metadata.json` and `reports/pilot_leakage_audit.md`.

## `development/development_v1.jsonl.gz`

A compressed, canonical Gate-B development artifact containing 144 diversified scenarios. Materialize it with:

```bash
gzip -dk data/development/development_v1.jsonl.gz
```

`development_v1.meta.jsonl.gz` contains hidden generation metadata, counterfactual IDs, sequence IDs, and design categories. It must never be supplied to annotators or policies. The SHA-256 manifest in `development_v1.sha256` covers the uncompressed canonical artifacts.

Scenario records contain no gold action. Formal policy evaluation must use the **raw-context projection** as the primary validity track; researcher-derived scalar state remains a mechanistic/control track only.

Current state: **pre-annotation leakage gate PASS; full label-dependent leakage and independent agreement NOT EXECUTED.** Therefore this dataset is not yet cleared for formal baseline ranking.
