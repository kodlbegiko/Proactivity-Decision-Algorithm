# Research Question and Scope

## Core decision problem

At time `t`, let `X_t` represent observable user/task/event context. A policy outputs one action:

`D_t ∈ {IGNORE, WAIT, SUGGEST, NOTIFY, ASK, ACT}`.

The objective is to maximize useful intervention while controlling false interruption, missed critical events, premature intervention, redundant notification, low-confidence intervention, and unsafe autonomy.

## Primary research question

Under what conditions should a personal AI proactively intervene, which intervention class should it choose, and can a lightweight/model-agnostic policy improve the usefulness–interruption trade-off over preregistered simple baselines under protected, cross-domain evaluation?

## Formal research questions

1. Can deterministic/lightweight policies outperform simple heuristics?
2. Which context variables contribute most to decision quality?
3. How should benefit, urgency, confidence, interruption cost, delay cost, and risk be traded off?
4. Does performance generalize across domains?
5. What is lost when individual signals are removed?
6. Can usefulness improve without materially increasing false interruptions?
7. Does added complexity provide practical benefit?
8. Is the policy calibrated under uncertainty/missing context?
9. When is `WAIT` preferable to immediate intervention?
10. When must `ACT` be prohibited even if expected benefit is high?

## In scope

Intervention necessity/timing, class selection, uncertainty/abstention, interruption/delay costs, permission/action risk, redundancy/acknowledgement/history, cross-domain and longitudinal evaluation.

## Out of scope

Full personal assistant implementation, generalized memory/PSE replacement, speech/vision/ambient sensing, production OS integration, production autonomous action execution, and online personalization in stage 1.

## Novelty constraint

The project must not claim novelty merely from the word “proactive.” Current work already contains proactive dialogue benchmarks, proactive personal-assistant benchmarks, timing-aware task-scheduling agents, real-user proactive-agent datasets, and active-user simulation. Any contribution must be demonstrated at the level of decision formulation, action taxonomy, cost-sensitive evaluation, protected methodology, or empirical findings.
