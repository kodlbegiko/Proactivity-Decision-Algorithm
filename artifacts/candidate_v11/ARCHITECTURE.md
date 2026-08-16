# Candidate-v11 Architecture

## Research question
Infer a decision-relevant structured state from heterogeneous natural language without making surface phrase matching the decision policy.

## Pipeline
`text -> semantic units -> typed propositions -> polarity/scope/temporal attributes -> evidence graph -> factor hypotheses -> uncertainty status -> Protocol-v2 latent state -> frozen action policy`

The lexical layer is only a grounding interface. Policy selection is not mapped from phrases. Evidence is first assigned to typed factors, contradiction/counterevidence is retained, and Protocol-v2-equivalent action semantics are evaluated only after state reconstruction.

## Variants
- **A — flat propositions:** typed proposition extraction without structural negation.
- **B — weighted evidence graph:** structural negation + typed propositions + evidence aggregation. **Selected.**
- **C — scope/temporal weighted graph:** B plus additional temporal/modal discounting.

B and C tied on development metrics. B is selected by the preregistered parsimony tie-break: equal scientific performance -> lower inference complexity.

## UNKNOWN states
Factor hypotheses distinguish `SEMANTICALLY_UNSPECIFIED`, `EXTRACTION_UNCERTAIN`, `CONTRADICTORY_EVIDENCE`, and `KNOWN`.

## Safety
ACT is selected only after reconstruction and Protocol-v2-equivalent safety constraints. There is no universal-ASK fallback.
