# Candidate-v12 Architecture

Four serious architectures were evaluated: A canonical structured parser, B factor-specific independent evidence extraction, C typed proposition/evidence resolver, and D compositional semantic-frame resolver.

C initially dominated the first controlled corpus, but was rejected as a final candidate because fresh compositional realizations exposed lexical dependence. Architecture search was reopened before freeze under the preregistered semantic-first selection rule. The selected architecture is `D_compositional_semantic_frame_resolver`.

D separates factor concepts from value predicates; applies clause-scoped negation, conditional suppression for non-actual propositions, temporal supersession, entity binding, uncertain-modality handling, dependency inference, cancellation/preference semantics, contradiction-safe aggregation, and ontology constraints; then sends the resulting 12-factor state into an unchanged deterministic policy.

The architecture remains deliberately inspectable. Perfect development scores are controlled synthetic evidence, not a claim of unrestricted natural-language understanding.