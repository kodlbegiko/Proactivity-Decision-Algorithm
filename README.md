# Proactivity Decision Algorithm

A rigorous research repository for the decision problem:

> Given current context, uncertainty, urgency, benefit, interruption cost, delay cost, permission state, and action risk, should a personal AI intervene now, how strongly should it intervene, or should it remain silent?

## Scope

This repository studies the **proactivity decision policy**. It does not attempt to build a full personal assistant, GUI, voice agent, memory system, or autonomous action engine.

Decision taxonomy (v0):

`IGNORE | WAIT | SUGGEST | NOTIFY | ASK | ACT`

## Current evidence status — 2026-08-13

- Repository bootstrap: complete.
- Research landscape reconnaissance: initial pass complete; not yet a systematic review.
- Formal problem definition: drafted.
- Decision taxonomy: operational definitions drafted.
- Benchmark schema: drafted and executable validation added locally.
- Annotation protocol: drafted.
- Multi-annotator agreement: **NOT EXECUTED**.
- Protected set: **NOT CREATED / NOT FROZEN**.
- Formal baselines: **NOT EXECUTED**.
- Candidate algorithm: **NOT STARTED** by design.
- Protected validation: **NOT EXECUTED**.

The project is intentionally stopped before candidate development until Benchmark Validity (Gate B) is supported by independent annotation evidence.

## Research gap under test

Recent work already evaluates proactive dialogue, proactive task scheduling, long-horizon proactive personal assistants, active-user simulation, and timing prediction. This repository therefore does **not** claim that proactive-agent benchmarks are absent. The narrower hypothesis is that there remains value in a model-agnostic, cross-domain benchmark that isolates the intervention-control decision itself, explicitly represents silence/deferral, and evaluates permission/risk/interruption trade-offs with protected, cost-sensitive evaluation.

That gap is a research claim to validate, not an assumption.

## Reproducibility

```bash
python -m pytest -q
PYTHONPATH=src python scripts/validate_dataset.py data/development/pilot_v0.jsonl
```

Agreement tooling is prepared for two independent labelers.

## Branch discipline

Substantive work is performed on `research/proactivity-decision-v0`. `main` remains a stable entry point until research gates are satisfied.
