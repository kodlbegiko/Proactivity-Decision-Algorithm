# Literature / Benchmark Reconnaissance

Status: **INITIAL RECONNAISSANCE — NOT A SYSTEMATIC REVIEW**  
Cutoff: 2026-08-13

## Key sources

| Work | Year | Problem / input-output | Evaluation focus | Relevance / limitation for this mission |
|---|---:|---|---|---|
| Horvitz, Jacobs & Hovel, *Attention-Sensitive Alerting* | 1999 | Context-sensitive alert mediation | interruption cost vs delayed awareness | Foundational evidence that proactivity should be utility/cost-sensitive, not urgency-only. |
| Horvitz & Apacible, *Learning and Reasoning About Interruption* | 2003 | Infer interruption cost from activity/context | interruption-cost prediction | Supports explicit interruptibility/context variables. |
| Horvitz, Koch & Apacible, *BusyBody* | 2004 | Personalized interruption-cost models | notification mediation | Supports personalized/context-conditioned interruption cost. |
| Achlioptas & Horvitz, *Principles of Bounded Deferral* | 2005 | Defer alerts for bounded time | optimized deferral | Direct precedent for `WAIT` as a first-class decision. |
| Wu et al., *InSCIt* (TACL) | 2023 | Mixed-initiative information seeking | answer / clarify / relevant-info generation | Initiative-aware multi-action dialogue, but not general personal-assistant intervention control. |
| Chen et al., *Need Help? Designing Proactive AI Assistants for Programming* | 2024 | Proactive programming assistance | productivity / user experience | Strong domain-specific HCI evidence; not a cross-domain decision benchmark. |
| Srinivas et al., *Substance over Style* (ACL) | 2025 | Proactive conversational coaching | user study and evaluator comparison | Demonstrates evaluator misalignment; supports human validation of labels/judges. |
| Liu et al., *ProactiveEval* (ACL) | 2026 | target planning + dialogue guidance; 328 environments / 6 domains | proactive dialogue capability | Important overlap; not the same six-action intervention-control formulation. |
| Ding et al., *ProActor* (ACL) | 2026 | task scheduling with opportunity windows | timing quality + reference action alignment; RL | Very close on timing; this mission must not duplicate scheduling-only optimization. |
| Zhang et al., *π-Bench* | 2026 | long-horizon personal-assistant tasks with hidden intents | proactivity + task completion | Very close on personal assistants; this mission must isolate decision quality rather than repackage task completion. |
| Nathani et al., *Pare / Pare-Bench* | 2026 | active-user simulation in stateful apps | observation, goal inference, intervention timing, orchestration | Directly covers intervention timing; major novelty comparator. |
| Tang et al., *ProAgentBench* | 2026 | real work sessions; timing prediction + assist content | timing/content under long-term context | Challenges realism claims from synthetic-only data. |
| Zhang et al., *NIABench* | 2026 | non-intrusive assistance during multi-step activities | when/what to assist | Supports non-intrusiveness as an explicit objective. |

## Primary-source URLs

- https://www.microsoft.com/en-us/research/publication/attention-sensitive-alerting/
- https://www.microsoft.com/en-us/research/publication/learning-and-reasoning-about-interruption/
- https://www.microsoft.com/en-us/research/?p=316172
- https://www.microsoft.com/en-us/research/?p=152855
- https://aclanthology.org/2023.tacl-1.27/
- https://arxiv.org/abs/2410.04596
- https://aclanthology.org/2025.acl-long.1017/
- https://aclanthology.org/2026.acl-long.1906/
- https://aclanthology.org/2026.acl-long.832/
- https://arxiv.org/abs/2605.14678
- https://arxiv.org/abs/2604.00842
- https://arxiv.org/abs/2602.04482
- https://arxiv.org/abs/2605.01368

## Current gap statement

**Rejected broad claim:** “There is no benchmark for proactive agents.” This is false by 2026.

**Narrow research gap to test:** Existing systems distribute the problem across dialogue planning, hidden-intent/task-completion benchmarks, task-scheduling windows, active-user simulation, real-session timing prediction, and non-intrusive assistance. A potentially distinct contribution is a **model-agnostic cross-domain intervention-controller benchmark** whose central output is one of `IGNORE/WAIT/SUGGEST/NOTIFY/ASK/ACT`, with asymmetric evaluation of interruption, delay, permission, uncertainty, and unsafe-autonomy errors.

This is not yet a proven novelty claim. Before publication-level claims, a systematic related-work pass must verify whether another benchmark already uses an equivalent action taxonomy and cost structure.

## Design consequences

1. `WAIT` must be first-class; bounded deferral is prior art.
2. Interruption cost cannot be an afterthought.
3. Timing-only accuracy is insufficient; permission/risk errors require separate metrics.
4. Synthetic data is useful for controlled-variable experiments but weak evidence of realism.
5. Human annotation agreement is mandatory because proactive usefulness is subjective and evaluator disagreement is documented.
6. The benchmark must compare against current proactive benchmarks rather than position itself as the first proactive-agent evaluation.
