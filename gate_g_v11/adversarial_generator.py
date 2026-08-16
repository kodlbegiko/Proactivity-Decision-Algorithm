from __future__ import annotations

# Kept separate so mixed-adversarial composition remains an independently reviewable layer.
COMPOSITE_DIFFICULTIES = (
    "lexical_novelty", "long_context", "negation", "scope",
    "uncertainty", "distractor", "domain_transfer", "temporal_update",
)


def choose_difficulties(index: int) -> tuple[str, ...]:
    width = 3 + (index % 3)
    start = index % len(COMPOSITE_DIFFICULTIES)
    return tuple(COMPOSITE_DIFFICULTIES[(start + j) % len(COMPOSITE_DIFFICULTIES)] for j in range(width))
