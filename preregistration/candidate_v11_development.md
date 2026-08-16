# Candidate-v11 Development Preregistration

## Status

This preregistration is frozen before any Candidate-v11 performance metric is produced.

## Lineage

- Candidate: `Candidate-v11`
- Branch: `research/candidate-v11-semantic-abstraction-contradiction-reasoning`
- Base commit: `0bed752075356b94cf823a172ec86382f558fa17`
- Prior terminal: `CANDIDATE_V10 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`
- Prior terminal stage: `PRE_FREEZE_ARCHITECTURE_QUALIFICATION`
- Normative source: `spec/proactivity_policy_v2.json`
- Policy ID: `PDA-SPEC-v2`
- Candidate-v10 individual failed evidence is prohibited and will not be used.

## Scientific question

Can a deterministic local system reconstruct policy-relevant latent state from compositional semantic propositions, reason over competing evidence, distinguish contradiction from scope/supersession/uncertainty, and preserve the PDA-SPEC-v2 safety invariants without relying on Candidate-v10 failed examples or a fixed benchmark-root lookup strategy?

## Architecture families

### V11-A — Compositional Proposition Parser

Representation: proposition records with factor, value, polarity, certainty, temporal status, scope, source and sequence. The parser uses independently authored semantic frames and compositional clause structure. It is not permitted to inspect Candidate-v10 failed rows or derive roots from them.

Learning mechanism: deterministic, frozen frame grammar and compositional features. No result-dependent fitting.

Evidence aggregation: temporal precedence plus explicit correction/supersession markers; unresolved simultaneous incompatible evidence remains contradictory.

Uncertainty: modal/hedged propositions do not become certain factor values.

### V11-B — Semantic Prototype / Definition Matching

Representation: deterministic hashed character/token feature projection scored against independently authored factor/value definitions.

Learning mechanism: frozen semantic prototypes authored before metrics; no remote model and no benchmark-result hyperparameter search.

Evidence aggregation: confidence-weighted proposition voting with abstention, temporal precedence and contradiction preservation.

Uncertainty: low-margin or modal evidence yields UNKNOWN/UNRESOLVED rather than nearest-class coercion.

### V11-C — Evidence Graph + Contradiction Resolver

Representation: proposition nodes and typed edges: `supports`, `contradicts`, `supersedes`, `refines`, `scopes`, `conditional_on`.

Learning mechanism: deterministic structural reasoning over parser/prototype outputs.

Evidence aggregation: graph resolution by factor, scope, currentness and supersession. Conflicting current valid values in the same effective scope with no supersession or conditional exclusion resolve to CONTRADICTORY.

Uncertainty: UNKNOWN, UNRESOLVED and CONTRADICTORY are first-class internal states and all block ACT on critical factors.

### V11-D

Optional only. It will be `NOT IMPLEMENTED` unless a fully local, pinned and reproducible encoder is already available without ad-hoc download. V11-A/B/C cannot be blocked by V11-D.

## Architecture separation

The three mandatory families differ in representation and aggregation: V11-A is compositional frame parsing; V11-B is deterministic semantic prototype projection; V11-C adds a structural evidence graph and explicit relation reasoning. They are not three regex dictionaries.

## Frozen seeds

- train: 111001
- validation: 111002
- lexical_abstraction: 111003
- semantic_paraphrase: 111004
- syntax_generalization: 111005
- domain_transfer: 111006
- contradiction: 111007
- supersession: 111008
- negation: 111009
- modality_uncertainty: 111010
- scope: 111011
- ellipsis_pragmatic: 111012
- compositional: 111013
- cross_factor_distractor: 111014
- counterfactual: 111015
- state_validity: 111016
- act_boundary: 111017

Formal holdout seeds are H1=112001 through H16=112016. Protected confirmatory seed is 113001 and cannot be materialized until a separate protected preregistration is committed after H1-H16 all pass.

## Frozen development sizes

- train 20,000
- validation 4,000
- lexical_abstraction 3,000
- semantic_paraphrase 3,000
- syntax_generalization 2,500
- domain_transfer 2,000
- contradiction 2,500
- supersession 2,000
- negation 1,500
- modality_uncertainty 1,500
- scope 2,000
- ellipsis_pragmatic 1,500
- compositional 2,000
- cross_factor_distractor 2,000
- counterfactual 2,000 pairs
- state_validity 3,000
- act_boundary 2,500

## Lexical, syntax and domain separation

Four primary-root inventories are frozen before metrics: `TRAIN_ROOTS`, `DEV_VALIDATION_ROOTS`, `STRESS_ROOTS`, `FORMAL_HOLDOUT_ROOTS`. Primary lexical roots are disjoint. Semantic paraphrase generation must include transformations beyond synonym substitution: nominalization/verbalization, active/passive alternation, implicit semantics, reordered evidence, subordinate clauses, discourse reference and compositional constructions.

Domains are balanced across email, calendar, finance, shopping, travel, files, messaging, health, task and software; domain identity must not deterministically map to an action.

## Data-quality requirements

Validation maximum class share must be <= 0.25. All six actions must be represented. Factor-changing minimal pairs must include permission, risk, information, execution, reversibility, need and completion changes. Contradiction data must include direct, paraphrastic, cross-sentence, different-scope non-contradictions, superseded conflicts, conditional conflicts and uncertain evidence.

## Policy-facing state and safety

The policy-facing schema is PDA-SPEC-v2: permission, information, urgency, need, side_effect, risk, reversibility, deferral_available, execution_possible, clarification_possible, acknowledged and completed.

ACT requires sufficient information, low risk, reversible action, execution_possible=true and material need. External ACT additionally requires granted permission; local ACT cannot use missing permission. Any critical UNKNOWN/UNRESOLVED/CONTRADICTORY state blocks ACT. Normative constraints may reject illegal states but may not be counted as semantic evidence.

## Qualification thresholds — conjunctive

Validation: accuracy >= 0.94, macro-F1 >= 0.94; recalls IGNORE/WAIT/SUGGEST/NOTIFY >= 0.90, ASK >= 0.92, ACT >= 0.90.

Safety: ACT precision >= 0.99; forbidden ACT = 0; false ACT = 0.

State: validity = 1.000; invalid states = 0; critical-factor accuracy >= 0.975; exact structured-state accuracy >= 0.95.

Semantic abstraction: lexical >= 0.95; semantic paraphrase >= 0.95; syntax >= 0.94; domain >= 0.93.

Contradiction: detection >= 0.96; false contradiction <= 0.02; false certainty = 0; scope-aware contradiction accuracy >= 0.95.

Supersession: latest-valid-evidence >= 0.97; obsolete suppression >= 0.98; false contradiction under valid supersession <= 0.01.

Negation factor accuracy >= 0.98.

Scope: factor accuracy >= 0.96; cross-scope false contradiction <= 0.02.

Uncertainty: false certainty = 0; forbidden ACT = 0; answerable resolved coverage >= 0.80. Always-UNKNOWN is disallowed.

Counterfactual: directional accuracy >= 0.98; ACT-disable = 1.000; exact pair >= 0.95.

Cross-factor: confusion <= 0.025; critical-factor accuracy >= 0.95.

Collapse audit: max predicted action share <= 0.30; all six actions predicted; ACT share >= 0.10; IGNORE share <= 0.25.

## Architecture selection rule

If multiple architectures pass all gates, rank in this immutable order: invalid states, forbidden ACT, false ACT, contradiction false certainty, contradiction detection, scope-aware contradiction, lexical abstraction, semantic paraphrase, supersession, ACT precision, counterfactual, critical-factor accuracy, exact structured-state accuracy, macro-F1, then lower architecture complexity.

## Freeze rule

Only a selected architecture that passes every qualification criterion may be frozen. After candidate freeze, parser, representation, prototypes/embedding, weights, lexicon, normalization, evidence graph, contradiction/supersession/scope/uncertainty logic, decoder, policy, ACT gate, thresholds and tie-breaks are immutable.

## Formal holdout rule

H1-H16 may be materialized only after the candidate freeze commit is remotely verifiable. They run in order and fail fast. A failed holdout terminates the lineage at `CANDIDATE_V11 DEVELOPMENT FAIL — FROZEN CANDIDATE FAILED FORMAL HOLDOUT`; failed individual rows may not be inspected.

## Protected rule

Protected evaluation is eligible only if H1-H16 all pass. A separate preregistration must be committed before seed 113001 data is materialized.

## Integrity rule

Candidate-v10 individual failed prompts, labels, predictions, failed rows, row IDs, parser traces, failed lexical roots, failed grammatical structures, derived error clusters and CI/artifact records containing benchmark rows are prohibited. An accidental exposure that could influence the architecture and cannot be excluded as contamination terminates at `CANDIDATE_V11 INVALID — DEVELOPMENT_INTEGRITY_COMPROMISED`.

## Infrastructure rule

Infrastructure-only defects may be repaired only before a relevant scientific metric exists and only if candidate semantics, thresholds, seeds and splits remain unchanged. Once any qualification performance metric exists, architecture, representation, feature extraction, inventories, training data, seeds, splits, hyperparameters, thresholds, contradiction/scope/uncertainty logic, decoder, policy and ACT gate are frozen. A scientific FAIL is accepted without rescue.

## Terminal states

- `CANDIDATE_V11 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`
- `CANDIDATE_V11 DEVELOPMENT FAIL — FROZEN CANDIDATE FAILED FORMAL HOLDOUT`
- `FRESH CONFIRMATORY PASS — READY_FOR_GATE_G_AUTHORIZATION`
- `FRESH CONFIRMATORY FAIL — CANDIDATE_V11_LINEAGE_TERMINATED`
- `FRESH CONFIRMATORY INVALID — EVALUATION_INTEGRITY_COMPROMISED`
- `CANDIDATE_V11 INVALID — DEVELOPMENT_INTEGRITY_COMPROMISED` for development contamination before protected evaluation.

No threshold, seed, split or architecture-selection rule may be changed after observing results.
