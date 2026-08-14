# Research Question and Scope — Protocol v2

## Core decision problem

Let `S_t` be an explicit validated structured state at time `t`. A frozen specification and deterministic oracle map `S_t` to one discrete intervention-control mode:

`D_t ∈ {IGNORE, WAIT, SUGGEST, NOTIFY, ASK, ACT}`.

The six modes are not assumed to form a universal scalar order.

## Primary research question

Can a deterministic, auditable proactivity decision layer map explicitly represented state concerning permission, timing, information sufficiency, intervention need, risk, reversibility, action side effects, and execution conditions to a policy-compliant intervention mode while satisfying a frozen formal specification and remaining consistent under counterfactual and temporal changes?

## Gate-oriented research questions

1. Can the finite specification be made deterministic, exhaustive, contradiction-free, traceable, and fail-closed? — Gate B.
2. Can a machine-grounded benchmark derived only from frozen state + specification + oracle be validated without hidden answer leakage or circular evaluation? — Gate C.
3. How do simple preregistered baselines perform against the frozen policy? — Gate D.
4. Does a PDA candidate improve exact compliance and asymmetric safety metrics over those baselines? — Gate E.
5. Does the improvement survive a protected/OOD evaluation? — Gate F.
6. Does behavior remain safe under adversarial, missing, contradictory, counterfactual, temporal, and distribution shifts? — Gate G.
7. Which state dimensions and mechanisms are causally useful, and can the full result be independently reproduced without claim inflation? — Gate H.

## In scope

- explicit intervention-control state;
- silence versus deferred intervention;
- notification versus authorization/information requests;
- permission-sensitive autonomous action;
- risk, reversibility, information sufficiency, side-effect scope, and timing;
- deterministic oracle and rule traces;
- counterfactual and temporal specification tests;
- machine-grounded development/protected benchmarks;
- later cross-domain and OOD policy evaluation.

## Out of scope for the primary Protocol-v2 claim

- human preference alignment;
- universal correctness or desirability of the specification;
- user satisfaction/trust/comfort;
- psychological or social validity;
- full personal-assistant implementation;
- production autonomous execution;
- speech/vision/ambient sensing;
- generalized memory/PSE replacement;
- online personalization in the current stage.

## Novelty constraint

The project must not claim novelty merely from the terms “proactive,” “permission,” “constraints,” or “formal specification.” Prior work already covers constrained policy optimization, shielding/action filtering, proactive intervention timing, ask-versus-context-extrapolation trade-offs, and permission/capability separation. The current position remains `PARTIAL NOVELTY ONLY`; any contribution must be supported at the level of the integrated decision formulation, evaluation design, evidence, and empirical findings.
