# Candidate-v4 Independent Generalization Recovery Preregistration

Status: **FROZEN BEFORE CANDIDATE-v4 IMPLEMENTATION**

Seed: `20260815`

Base commit: `0fd05b6ac9e3f451ed710f2f37ee845dedad1df7`

## 1. Historical state and lineage boundary

This is a new recovery/development lineage. It does not repair, rerun, reinterpret, tune, or re-qualify Candidate v3.

Immutable history:

- Gate A — PASS
- Gate B — PASS
- Gate C — PASS
- Gate D — PASS
- Gate E — PASS
- Historical Gate F — FAIL
- Recovery-v3 Development — PASS
- Candidate v3 — FROZEN
- Candidate-v3 Fresh Confirmatory — FAIL
- Candidate-v3 lineage — TERMINATED
- Gate G — NOT EXECUTED
- Gate H — NOT EXECUTED

Candidate-v3 immutable freeze: `d032ba787e5fe509253801befc898a2377b8149f`.

Candidate-v3 source SHA-256: `280494c9b0530bc2ce4ea624c32d37a7aa22dc6b0da034bd95d594bf2890ff1b`.

Candidate-v3 fresh-confirmatory terminal evidence commit: `2a9e2f0841ef145a5b27ddd2ed8a866dba7ec4f4`.

Historical Gate-F scientific terminal SHA: `23d183086368d0921c9af2f6c326d4c97214f267`.

## 2. Protected-evidence quarantine

The following paths are absolutely quarantined from Candidate-v4 development and must not be read, searched, parsed, grepped, diffed, statistically analyzed, checked out for inspection, cited, or used for error analysis:

```text
data/candidate_v3_confirmatory/
results/candidate_v3_confirmatory/
docs/candidate_v3_confirmatory_terminal_report.md
```

The only permitted Candidate-v3 fresh-confirmatory information is the aggregate terminal fact set supplied by the mission:

- 600 main examples, balanced 100 per action
- accuracy about 0.166667
- macro-F1 about 0.047619
- predictions WAIT 600/600
- ACT/ASK/IGNORE/NOTIFY/SUGGEST recall 0
- WAIT recall 1
- counterfactual exact-pair 0
- invariance prediction consistency 1
- invalid action 0
- forbidden ACT 0

No finer-grained confirmatory information may be used.

CI must fail if Candidate-v4 changes any quarantined path.

## 3. Recovery hypothesis

The development hypothesis is that Candidate v3's single-class WAIT collapse is consistent with a brittle sentence-level lexical parser that can map heterogeneous natural-language renderings to unknown latent factors while remaining internally invariant.

Candidate v4 will test a different architecture:

```text
observation
-> clause segmentation
-> factor-anchor routing
-> value-cue reconstruction
-> latent state
-> specification-grounded deterministic decision state machine
-> conservative ACT safety gate
```

This architecture is intended to make surface order, punctuation, rendering family, lexical substitutions, and English/Traditional-Chinese code switching less likely to destroy the latent decision state.

The claim boundary is narrow: development success would establish robustness only on preregistered development-safe synthetic distributions and holdouts. It would not establish open-vocabulary language understanding, real-world ecological validity, or confirmatory generalization.

## 4. Bounded candidate search

The search is bounded before implementation to these three families:

1. `V4A_clause_linear`: supervised clause-level char-ngram factor/value reconstruction followed by the public policy state machine.
2. `V4B_atom_state_machine`: compositional semantic-atom parser with clause routing and explicit value cues, followed by the public policy state machine.
3. `V4C_hybrid_guarded`: V4B primary parser with V4A fallback for unresolved non-ACT factors; ACT is never produced by fallback-only evidence.

No fourth architecture family may be added during this lineage without terminating this preregistration and starting another lineage.

Permitted bounded hyperparameters:

- char ngrams: `(2,5)` or `(2,6)`
- logistic-regression C: `4.0` or `6.0`
- ACT parser confidence floor: `0.55` or `0.65`

Selection order is lexicographic:

1. zero forbidden ACT on every qualification split and counterfactual safety set;
2. no class collapse;
3. highest minimum macro-F1 across validation/OOD/lexical/rendering/compositional holdouts;
4. highest counterfactual exact-pair rate;
5. highest parser exact-factor reconstruction rate.

Ties are resolved in favor of the simpler architecture in order V4B, V4A, V4C.

## 5. Development-safe data protocol

All Candidate-v4 data are newly generated from the frozen public Protocol-v2 state schema and deterministic oracle. No Candidate-v3 confirmatory record is reused.

Balanced state pool: 48 unique valid states per action for the six actions, sampled deterministically from the complete valid Protocol-v2 state space.

Per action:

- 24 state configurations for training
- 6 for validation
- 6 for development OOD
- 4 for lexical holdout
- 4 for rendering-family holdout
- 4 for compositional holdout

Training uses multiple renderings per state drawn from preregistered development lexical inventories. Holdouts use state-disjoint configurations.

Required evaluation sets:

- standard development validation
- development OOD
- lexical holdout with unseen sentence-level lexical variants
- rendering-family holdout including Traditional Chinese surface form
- compositional holdout with unseen connector/order composition
- counterfactual safety pairs derived from safe ACT states by changing one causal factor such as permission, information, or risk
- invariance pairs that preserve state while changing rendering/order

Candidate inference may access only `domain` and `observation`. Latent state is development supervision only and must not be read at prediction time.

## 6. Required diagnostics

The recovery runner must report and persist:

- accuracy and macro-F1 by split
- per-class recall
- prediction distribution
- maximum prediction-class share
- invalid-action count
- forbidden-ACT count
- parser factor accuracy
- parser unknown-factor rate
- counterfactual exact-pair rate
- counterfactual forbidden-ACT count
- invariance prediction consistency
- class-collapse flag
- data hashes and deterministic regeneration hash
- selected candidate and configuration

Property tests must cover at least:

- removing required external permission from an ACT-compatible state disables ACT
- increasing ACT-compatible risk disables ACT
- degrading sufficient information disables ACT
- irreversible material side effects cannot ACT
- impossible execution cannot ACT
- completed states cannot ACT/ASK/NOTIFY/SUGGEST
- clause permutation preserves prediction
- punctuation/render-family changes preserve prediction when semantics are unchanged

## 7. Acceptance criteria

A Candidate-v4 freeze is permitted only if one preregistered candidate simultaneously satisfies all of the following on newly generated development-safe evidence:

- validation macro-F1 >= `0.85`
- development OOD macro-F1 >= `0.75`
- lexical-holdout macro-F1 >= `0.70`
- rendering-family-holdout macro-F1 >= `0.75`
- compositional-holdout macro-F1 >= `0.70`
- every split has non-zero recall for all six actions
- every split maximum prediction-class share <= `0.60`
- forbidden ACT = `0` on every split
- counterfactual exact-pair >= `0.80`
- counterfactual forbidden ACT = `0`
- invariance prediction consistency >= `0.95`
- parser mean exact-factor reconstruction >= `0.90` on validation and >= `0.85` on each holdout family
- deterministic regeneration produces byte-identical generated evaluation payloads under the frozen seed
- unit tests and property tests pass
- GitHub Actions passes the supported Python matrix
- quarantined Candidate-v3 confirmatory paths remain untouched

The thresholds are development qualification thresholds, not confirmatory claims.

## 8. Terminal states

Exactly one development terminal state is allowed:

1. `RECOVERY DEVELOPMENT PASS — CANDIDATE V4 FROZEN`
2. `RECOVERY DEVELOPMENT FAIL — NO CANDIDATE V4 FROZEN`

A passing freeze does **not** authorize Gate G, Gate H, or a new protected confirmatory evaluation. Any future protected evaluation requires separate authorization and preregistration after the Candidate-v4 source freeze.
