# Proactivity Decision Algorithm

Research repository for a rigorous, reproducible study of **when a personal AI should proactively intervene, how strongly it should intervene, and when it should remain silent**.

The research target is the proactivity decision policy itself, not a full personal assistant product.

## Current research position

Gate A is narrowed after a 2026 primary-source audit: broad first claims over intervention timing, silence, consent, ask-or-act, and non-intrusive assistance are not supported. The remaining question is whether an integrated six-level intervention-control formulation (`IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`) with asymmetric error costs is independently measurable and useful.

Gate B is currently **BLOCKED_BY_INDEPENDENT_ANNOTATION**. `development_v1` has passed pre-annotation leakage checks, but human agreement and label-dependent controls are not executed.

## Research branch

Substantive research work is conducted on `research/proactivity-decision-v0` and merged only after evidence gates are satisfied.
