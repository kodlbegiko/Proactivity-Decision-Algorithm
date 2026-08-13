# Systematic Novelty Audit — Gate B

Date: 2026-08-13

## Verdict

**PARTIAL NOVELTY ONLY**

## What broad claims were rejected

The evidence no longer supports any claim that this project uniquely introduces:

- deciding whether/when to intervene;
- silence as a proactive option;
- consent/confirmation before acting;
- ask-or-act control;
- non-intrusive assistance;
- long-horizon proactive personal assistance;
- intervention timing as a standalone research problem.

KnowU-Bench is the closest conceptual overlap because it explicitly evaluates intervention, consent negotiation, silence, and post-rejection restraint. ProActor directly optimizes intervention opportunity timing; PACT formalizes ask-or-act; NIABench jointly decides when to act and what to do while avoiding interruptions; π-Bench and Pare-Bench already cover long-horizon personal-assistant and stateful proactive-agent settings.

## Remaining testable contribution

The project may still contribute an **integrated intervention-control measurement formulation** with:

1. six ordered but semantically distinct actions: `IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`;
2. explicit `IGNORE != WAIT` and `ASK != ACT` distinctions;
3. acceptable-action sets for legitimate ambiguity;
4. cross-domain, model-agnostic context inputs;
5. asymmetric error definitions for false interruption, premature intervention, missed critical events, over/under-escalation, and unsafe autonomy;
6. counterfactual and temporal tests of acknowledgement, redundancy, staleness, permission, risk, confidence, and interruption state.

Whether these distinctions are actually reliable enough to form a benchmark remains **unproven** until independent annotation passes Gate B.
