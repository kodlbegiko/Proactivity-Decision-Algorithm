# Candidate-v6 Frontier Review

## Scope
This review was completed without historical protected individual evidence. It informs architecture only; it is not protected evidence.

## 2025–2026 primary-source findings

| Work | Relevance | Candidate-v6 tag |
|---|---|---|
| Xu, Yang & Wang, **MC²** (Findings of EMNLP 2025), DOI 10.18653/v1/2025.findings-emnlp.406 | Semantic parsing compositional generalization remains brittle under limited primitive coverage; motivates explicit primitive/factor coverage and compositional holdouts. | ARCHITECTURE_INSPIRATION |
| Calanzone, Teso & Vergari, **Logically Consistent Language Models via Neuro-Symbolic Integration** (ICLR 2025) | External facts/rules plus a neural model can improve logical consistency; supports separation of semantic reconstruction from frozen symbolic policy. | ARCHITECTURE_INSPIRATION |
| Banerjee et al., **CRANE: Reasoning with constrained LLM generation** (ICML 2025) | Hard output constraints can improve validity but overly restrictive grammars can harm reasoning; motivates constraints after semantic extraction rather than action-class shortcuts. | ARCHITECTURE_INSPIRATION |
| Huang et al., **Selective Abstention Learning** (ACL 2025) | Explicit rejection/abstention objectives can reduce unsupported confident outputs; motivates UNKNOWN and false-certainty measurement. | ARCHITECTURE_INSPIRATION |
| Tayebati et al., **CAP: Conformalized Abstention Policies** (ACML/PMLR 2025) | Context-adaptive abstention formalizes the coverage/risk tradeoff; motivates fail-closed handling of uncertain ACT-critical factors. | ARCHITECTURE_INSPIRATION |
| Sakai et al., **Ordered CommonGen** (ACL 2025) | Models can follow surface instructions while still showing compositional/order bias; motivates rendering and compositional stress sets. | ARCHITECTURE_INSPIRATION |

## Architecture decision
Candidate-v6 keeps the authoritative PDA policy symbolic and frozen. Learned components reconstruct each decision factor independently from natural language. Direct action prediction is baseline-only. The selected development candidate was a factor-specific word n-gram classifier (V6-B), with an ACT veto when critical factors are insufficiently supported.

## Runtime constraints
No paid API, proprietary inference service, GPU, or human annotation was introduced. A local semantic embedding baseline was not available as a pinned runtime dependency and was therefore reported as unavailable rather than substituted with an online service.
