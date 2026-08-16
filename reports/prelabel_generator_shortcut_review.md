# Pre-label Generator Shortcut Review

Status: **PRE-HUMAN / DEVELOPMENT ONLY**

This review records construction-family language visible before independent human labels exist. It is not a label-dependent leakage result and it does not authorize changing the frozen `development_v1` after seeing future disagreements.

## Evidence already observed

The deterministic pre-annotation audit reports:

- 144 scenarios / 144 unique IDs;
- 0 exact duplicate members;
- 0 structural duplicate members;
- 0 unrelated near-duplicate pairs at the frozen threshold;
- no hidden-metadata findings in policy-visible records;
- construction-family token associations remain visible.

## Interpretation classes

### KNOWN_CONSTRUCTION_ARTIFACT

Words that disproportionately reveal a generator family (for example counterfactual or temporal-sequence phrasing) are recorded as benchmark-construction warnings. They are not automatically treated as decision-label leakage because no independent human labels exist yet.

### LEGITIMATE_CONTEXT_SIGNAL

Permission, acknowledgement, completion, timing, contradiction, freshness, and similar language may be causally relevant to intervention decisions. Correlation with future labels will not by itself justify removing these signals.

### UNCERTAIN_PENDING_HUMAN_LABELS

Tokens that could be either legitimate context or generator shorthand remain unresolved until immutable independent labels permit label-conditional analysis.

## Frozen handling rule

Do not rewrite `development_v1` merely because a token predicts design family. After human labels exist, run unigram/bigram label association and metadata-label checks, then distinguish legitimate causal signal from generation shortcut. Any dataset revision must be versioned rather than silently replacing the annotated data.
