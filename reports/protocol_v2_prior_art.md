# Protocol v2 Prior-Art Audit — 2026-08-14

## Verdict

**PARTIAL NOVELTY ONLY**

The primary-source record does not support a broad claim that Protocol v2 is the first work to constrain agent behavior with explicit specifications, decide when proactive agents should intervene, separate authorization from capability, or evaluate proactive intervention timing. The defensible research position is a narrower integration claim that remains provisional until later gates establish value beyond the frozen specification itself.

## Primary-source overlap

### Constrained and specification-enforced policy behavior

- Achiam et al., **Constrained Policy Optimization**, ICML 2017. The work explicitly treats behavior as reward optimization subject to separately specified constraints and provides constraint-satisfaction guarantees during policy learning. https://proceedings.mlr.press/v70/achiam17a.html
- Alshiekh et al., **Safe Reinforcement Learning via Shielding**, 2017/AAAI 2018. Temporal-logic specifications are compiled into a shield that restricts or corrects unsafe actions. https://arxiv.org/abs/1708.08611

These works substantially overlap the idea that allowed agent actions can be bounded by a machine-checkable specification. Protocol v2 must not claim that formal constraints or action filtering are novel in themselves.

### Proactive timing / intervention selection

- Chen et al., **LlamaPIE: Proactive In-Ear Conversation Assistants**, Findings ACL 2025. A dedicated model decides when to proactively respond, with emphasis on helpful, unobtrusive intervention. https://aclanthology.org/2025.findings-acl.710/
- Ding et al., **ProActor: Timing-Aware Reinforcement Learning for Proactive Task Scheduling Agents**, ACL 2026. The framework explicitly measures and optimizes proactive timing and reference-action alignment using automatically generated opportunity windows. https://aclanthology.org/2026.acl-long.832/
- Wu et al., **CoLabScience**, ACL 2026. PULI decides when and how to intervene in streaming scientific discussions. https://aclanthology.org/2026.acl-long.1671/
- Liu et al., **ProMediate**, Findings ACL 2026. A proactive mediator decides when and how to intervene, with intervention-latency and effectiveness metrics. https://aclanthology.org/2026.findings-acl.1479/
- Kaur et al., **PROPER Agents**, Findings ACL 2026. The paper explicitly identifies unnecessary or mistimed interventions and the trade-off between clarifying questions and context extrapolation. https://aclanthology.org/2026.findings-acl.2082/

These works reject any broad novelty claim over proactive timing, intervention decisions, or proactive-assistant evaluation.

### Authorization / capability / safe power

- Zheng et al., **Separating Capability from Permission: A Governance Framework for Agentic AI Autonomy Levels**, 2026. The framework explicitly separates allowed autonomy from technical capability and discusses risk, reversibility, and authorization. https://arxiv.org/abs/2607.23438
- Wang et al., **SafeMCP**, ACL 2026. The work constrains agent tool acquisition through risk-aware filtering and intervention. https://aclanthology.org/2026.acl-long.522/

These sources overlap Protocol v2's permission-sensitive autonomy and safe-action filtering motivation.

### Asking proactively for missing information/preferences

- Wu et al., **Ask Now, Use Later: Benchmarking the Proactivity Gap in Long-Lived LLM Agents**, 2026. ATRBench evaluates whether an agent proactively asks for reusable hidden preferences. https://arxiv.org/abs/2605.28108

This overlaps the broader ASK/proactivity construct and further rules out a first claim over proactive information acquisition.

## Narrow remaining research position

A possible contribution, subject to later evidence, is the **integration** of:

- a cross-domain intervention-control layer;
- six discrete modes (`IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`);
- explicit permission, information, risk, reversibility, timing, and side-effect state;
- a frozen deterministic oracle with rule/prohibition traces;
- asymmetric safety diagnostics around autonomous action;
- exhaustive finite-state specification checks;
- counterfactual and temporal policy-invariant testing;
- later protected/OOD evaluation of policies against that specification.

No individual item above is presumed novel. Protocol v2 should test whether the integrated formulation is useful, auditable, and empirically discriminative rather than presenting terminology as novelty.

## Claim boundary resulting from this audit

The research should use language such as **specification-grounded intervention control** and **policy compliance**. It should not claim first-in-field status for constrained agents, proactive timing, asking versus acting, permission-aware autonomy, or formal safety filtering.
