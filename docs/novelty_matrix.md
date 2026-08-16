# Construct-Level Novelty Matrix — 2026-08-13

Status: systematic primary-source reconnaissance for Gate B. The verdict is **PARTIAL NOVELTY ONLY**.

Notation: `Explicit` = directly described in the reviewed primary source; `Partial` = related construct is present but not the same operationalization; `Not established` = the reviewed primary source did not establish the construct, so this is not a claim of absence.

| Work | Primary task | Silence / no intervention | Deferral / WAIT | Timing | Permission / ask | Direct action | Cost / interruption | Longitudinal / state | Relevance to our remaining gap |
|---|---|---|---|---|---|---|---|---|---|
| ProactiveEval (ACL 2026) | proactive dialogue target planning + dialogue guidance | Not established | Not established | Partial | Not established | dialogue-level | Partial | Partial | broad cross-domain proactive dialogue evaluation already exists |
| ProActor (ACL 2026) | proactive task scheduling | Partial | opportunity-window formulation | **Explicit** | Not established | **Explicit** software action alignment | timing-oriented | stage-aware | timing optimization is already a mature overlap |
| KnowU-Bench (arXiv 2604.08455) | personalized mobile agent | **Explicit remain silent** | post-rejection restraint; no six-class WAIT taxonomy established | **Explicit intervention calibration** | **Explicit consent / confirmation** | **Explicit execute** | Partial | behavioral logs + interaction | closest overlap; invalidates broad first-claim over intervene/ask/silent |
| PACT (arXiv 2605.24350) | continual human-robot assistance | ask-or-act setting | Not established | contextual sufficiency | **Explicit ASK** | **Explicit ACT** | clarification utility trades accuracy vs asking frequency | **cross-day history** | ask-vs-act is not novel by itself |
| NIABench (arXiv 2605.01368) | non-intrusive human-robot assistance | interruption avoidance is central | Partial via choosing when to act | **Explicit** | conventional negotiation contrasted, not core | **Explicit what to do** | **non-intrusiveness** | multi-step activities | non-interruption and timing/action joint decisions already studied |
| π-Bench (arXiv 2605.14678) | long-horizon personal assistant | Not established | Not established | proactive intent resolution over trajectories | Partial through hidden intent resolution | task completion | Not established | **Explicit cross-session continuity** | personal-assistant + long-horizon proactivity already benchmarked |
| Pare-Bench (arXiv 2604.00842) | stateful app proactive agent | Not established | Not established | **Explicit intervention timing** | Not established | multi-app orchestration | Not established | **stateful apps** | realistic active-user environment and timing already covered |
| ProAgentBench (arXiv 2602.04482) | real-user proactive working scenarios | Not established | Not established | **timing prediction** | Not established | assist content generation | Not established | 500+ hours / long-term context | real-world timing data is already a strong external benchmark axis |
| ProEvent (arXiv 2607.17701) | event-centric proactive agents | overacting/cancellation errors | Partial | **response timing** | Not established | proactive event assistance | overacting explicitly observed | ongoing chat/event updates | overaction and event cancellation are already explicit failure modes |
| ProMediate (Findings ACL 2026) | proactive multi-party mediation | mediator chooses whether/when via policy, but no six-action taxonomy established | Not established | **Explicit when** | Not established | intervention | latency/effectiveness | streaming negotiation | “when/how to intervene” is not itself novel |
| **This research (proposed)** | model-agnostic intervention control | `IGNORE` | **`WAIT` as separate operational class** | yes | `ASK` | `ACT` | **asymmetric false-interruption, premature, missed-critical, unsafe-autonomy costs** | acknowledgement/redundancy/staleness/temporal sequences | remaining claim is an integrated measurement/control formulation, not first proactive benchmark |

## Primary sources

- ProactiveEval: https://aclanthology.org/2026.acl-long.1906/
- ProActor: https://aclanthology.org/2026.acl-long.832/
- KnowU-Bench: https://arxiv.org/abs/2604.08455
- PACT: https://arxiv.org/abs/2605.24350
- NIABench: https://arxiv.org/abs/2605.01368
- π-Bench: https://arxiv.org/abs/2605.14678
- Pare: https://arxiv.org/abs/2604.00842
- ProAgentBench: https://arxiv.org/abs/2602.04482
- ProEvent: https://arxiv.org/abs/2607.17701
- ProMediate: https://aclanthology.org/2026.findings-acl.1479/

## Novelty decision

**PARTIAL NOVELTY ONLY**

The review does **not** support claims that this project is the first to study when agents intervene, remain silent, ask permission, avoid interruption, or act proactively. The defensible research target is narrower: whether a model-agnostic, cross-domain **six-level intervention-control taxonomy** (`IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`) plus explicit asymmetric failure costs can be reliably annotated and can expose trade-offs that timing/task-completion benchmarks do not capture jointly.

This remaining gap is still provisional until independent annotation shows the six-way distinctions are reliably measurable.
