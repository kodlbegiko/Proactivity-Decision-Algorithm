# Data

## `development/pilot_v0.jsonl`

**INFRASTRUCTURE PILOT ONLY — NOT FOR FORMAL POLICY COMPARISON.**

The 24-scenario pilot failed the structural template audit: all 24 members collapsed into four repeated structural templates of six members each (`duplicate_member_rate = 1.0`). The file is retained as negative evidence and for legacy schema/pipeline regression tests.

See `development/pilot_v0.metadata.json` and `reports/pilot_leakage_audit.md`.

## Development v1

The canonical Gate-B development artifact is generated deterministically with:

```bash
python scripts/generate_development_v1.py
sha256sum -c data/development/development_v1.sha256
```

This produces:

- `data/development/development_v1.jsonl` — 144 scenarios;
- `data/development/development_v1.meta.jsonl` — hidden generation metadata;
- `annotation/packet_a.csv` / `packet_b.csv` — blinded annotation packets.

The expected hashes are versioned in `development_v1.sha256`. Hidden pair/sequence/design metadata must never be supplied to annotators or policies.

Scenario records contain no gold action. Formal policy evaluation must use the **raw-context projection** as the primary validity track; researcher-derived scalar state remains a mechanistic/control track only.

Current state: **pre-annotation leakage gate PASS; full label-dependent leakage and independent agreement NOT EXECUTED.** Therefore this dataset is not yet cleared for formal baseline ranking.
