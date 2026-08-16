from __future__ import annotations

import re
from typing import Any

SAFE_DEFAULT: dict[str, Any] = {
    "permission": "missing",
    "information": "insufficient",
    "urgency": "none",
    "need": "optional",
    "side_effect": "local",
    "risk": "high",
    "reversibility": "irreversible",
    "deferral_available": True,
    "execution_possible": False,
    "clarification_possible": True,
    "acknowledged": False,
    "completed": False,
}

# Candidate-v9 lexicon is newly authored from PDA-SPEC-v2 factor semantics. It does
# not depend on Candidate-v8 formal holdout rows.
PATTERNS: dict[str, dict[Any, tuple[str, ...]]] = {
    "permission": {
        "granted": (
            r"\b(?:authorization|approval|permission|consent|clearance)\b.{0,35}\b(?:confirmed|granted|recorded|valid|secured|obtained|given|available|in force)\b",
            r"\b(?:authorized|cleared)\s+(?:for|to)\b",
            r"\b(?:go ahead|green light)\b.{0,20}\b(?:recorded|confirmed|given)\b",
        ),
        "missing": (
            r"\b(?:authorization|approval|permission|consent|clearance)\b.{0,35}\b(?:absent|missing|pending|revoked|withheld|unavailable|not granted|not approved|not obtained|withdrawn)\b",
            r"\bwithout\s+(?:authorization|approval|permission|consent|clearance)\b",
            r"\bno\s+(?:authorization|approval|permission|consent|clearance)\s+(?:has been|was|is)\s+(?:granted|obtained|recorded)\b",
        ),
        "not_required": (
            r"\b(?:authorization|approval|permission|consent|clearance)\b.{0,35}\b(?:waived|exempt|unnecessary|not required|not needed|does not apply|isn't required|is not necessary)\b",
            r"\bno\s+(?:authorization|approval|permission|consent|clearance)\s+(?:is\s+)?(?:needed|required|necessary)\b",
            r"\bapproval[- ]free\b",
        ),
    },
    "information": {
        "sufficient": (
            r"\b(?:information|facts|details|evidence|record|inputs?)\b.{0,35}\b(?:complete|verified|adequate|sufficient|settled|ready)\b",
            r"\b(?:information|facts|details|evidence|record|inputs?)\b.{0,35}\bcomplete enough\b",
            r"\b(?:we|system)\s+(?:have|has)\s+enough\s+(?:information|evidence|detail|facts?)\b",
            r"\bnothing material (?:is|remains) missing\b",
        ),
        "insufficient": (
            r"\b(?:information|facts|details|evidence|record|inputs?)\b.{0,35}\b(?:incomplete|insufficient|missing|inadequate|not enough|has gaps|contain gaps|unknown)\b",
            r"\b(?:we|system)\s+(?:do not|does not|don't|doesn't)\s+have\s+enough\b",
            r"\bmaterial (?:detail|information|fact)s? (?:is|are) missing\b",
        ),
        "contradictory": (
            r"\b(?:information|facts|details|evidence|record|accounts?)\b.{0,35}\b(?:conflicting|inconsistent|contradictory|disagree|in conflict)\b",
        ),
    },
    "urgency": {
        "none": (
            r"\b(?:urgency|time pressure|time sensitivity|deadline pressure)\b.{0,30}\b(?:none|absent|low|not present)\b",
            r"\bnot time[- ]sensitive\b",
            r"\bno (?:immediate )?deadline\b",
        ),
        "normal": (
            r"\b(?:urgency|timing|priority|schedule)\b.{0,30}\b(?:normal|routine|ordinary|standard)\b",
            r"\broutine timing\b",
        ),
        "high": (
            r"\b(?:urgency|time pressure|priority|deadline pressure)\b.{0,30}\b(?:high|urgent|elevated|immediate|critical)\b",
            r"\btime[- ]critical\b",
            r"\bimmediate attention\b",
        ),
        "expired": (
            r"\b(?:urgency|deadline|window|timing|time window)\b.{0,30}\b(?:expired|passed|overdue|closed|elapsed)\b",
            r"\bdeadline (?:has )?(?:passed|elapsed)\b",
        ),
    },
    "need": {
        "none": (
            r"\b(?:need|intervention|action|task)\b.{0,30}\b(?:none|not needed|unnecessary|absent)\b",
            r"\bno current need\b",
            r"\bnothing (?:needs|requires) (?:doing|action|intervention)\b",
            r"\bno (?:intervention|action) is needed\b",
        ),
        "optional": (
            r"\b(?:need|intervention|action|improvement|task)\b.{0,35}\b(?:optional|nice[- ]to[- ]have|discretionary|nonessential)\b",
            r"\boptional improvement\b",
            r"\b(?:nice[- ]to[- ]have|nonessential|discretionary)\b",
        ),
        "material": (
            r"\b(?:need|intervention|action|task|requirement)\b.{0,35}\b(?:material|substantive|consequential|important|necessary|required)\b",
            r"\bmaterial need\b",
            r"\bsubstantive intervention\b",
        ),
    },
    "side_effect": {
        "none": (
            r"\b(?:side effect|state change|effect scope|operation)\b.{0,35}\b(?:none|absent|no state change|read[- ]only|informational only)\b",
            r"\bpurely informational\b",
            r"\bread[- ]only\b",
            r"\bno side effect\b",
        ),
        "local": (
            r"\b(?:side effect|effect|state change|scope|operation)\b.{0,35}\b(?:local|locally confined|on[- ]device|internal)\b",
            r"\blocal state\b",
            r"\bon[- ]device (?:change|write|update)\b",
        ),
        "external": (
            r"\b(?:side effect|effect|state change|scope|operation|write)\b.{0,35}\b(?:external|remote|third[- ]party|outside the local system)\b",
            r"\bexternal system\b",
            r"\bthird[- ]party (?:write|change|update|effect)\b",
        ),
    },
    "risk": {
        "low": (
            r"\b(?:risk|exposure)\b.{0,30}\b(?:low|minimal|negligible|acceptably low|minor)\b",
            r"\blow[- ]risk\b",
        ),
        "medium": (
            r"\b(?:risk|exposure)\b.{0,30}\b(?:medium|moderate|intermediate|nontrivial)\b",
            r"\bnontrivial risk\b",
        ),
        "high": (
            r"\b(?:risk|exposure)\b.{0,30}\b(?:high|elevated|severe|substantial|major)\b",
            r"\bhigh[- ]risk\b",
        ),
    },
    "reversibility": {
        "reversible": (
            r"\b(?:action|change|effect|operation)\b.{0,35}\b(?:reversible|undoable|rollbackable|can be undone|can be reversed)\b",
            r"(?<!no )\b(?:rollback|undo)\b.{0,25}\b(?:available|possible|supported)\b",
            r"\bnot irreversible\b",
            r"\bnot permanent\b",
        ),
        "irreversible": (
            r"\b(?:action|change|effect|operation)\b.{0,35}\b(?<!not )\b(?:irreversible|permanent|nonreversible)\b",
            r"\bno (?:rollback|undo)\b",
            r"\bcannot be (?:reversed|undone|rolled back)\b",
        ),
    },
    "deferral_available": {
        True: (
            r"\b(?:deferral|waiting)\b.{0,30}\b(?:available|possible|allowed|open)\b",
            r"(?<!no )\b(?:later option|later opportunity)\b.{0,20}\b(?:available|exists|open)\b",
            r"\bcan (?:wait|defer|be deferred)\b",
        ),
        False: (
            r"\b(?:deferral|waiting|later option|later opportunity)\b.{0,30}\b(?:unavailable|impossible|not allowed|closed|does not exist|absent)\b",
            r"\bcannot (?:wait|defer|be deferred)\b",
            r"\bno later (?:option|opportunity)\b",
        ),
    },
    "execution_possible": {
        True: (
            r"\b(?:execution|operation|run)\b.{0,25}\b(?:is |remains )?(?!not |un)(?:possible|available|feasible|ready|executable)\b",
            r"\bpath\b.{0,25}\b(?:is |remains )?(?!not )(?:operationally feasible|available|ready)\b",
            r"\bcan (?:execute|run|be executed)\b",
            r"(?<!not )\boperationally feasible\b",
        ),
        False: (
            r"\b(?:execution|operation|path|run)\b.{0,30}\b(?:impossible|unavailable|infeasible|blocked|not possible|cannot proceed)\b",
            r"\bcannot (?:execute|run|be executed)\b",
            r"\bnot operationally feasible\b",
        ),
    },
    "clarification_possible": {
        True: (
            r"\b(?:clarification|question)\b.{0,25}\b(?:is |remains )?(?!not )(?:possible|available|open|allowed)\b",
            r"\bfollow[- ]up\b.{0,25}\b(?:is |remains )?(?!not |un)(?:possible|available|open|allowed)\b",
            r"\bcan (?:ask|request)(?: for)? (?:a )?(?:clarification|follow[- ]up)\b",
        ),
        False: (
            r"\b(?:clarification|follow[- ]up|asking|question)\b.{0,30}\b(?:impossible|unavailable|closed|not possible|not allowed)\b",
            r"\bcannot (?:ask|request)(?: for)? (?:a )?(?:clarification|follow[- ]up)\b",
        ),
    },
    "acknowledged": {
        True: (
            r"(?<!not )(?<!un)\backnowledged\b",
            r"(?<!no )\backnowledg(?:e)?ment\b.{0,25}\b(?:recorded|confirmed|received)\b",
        ),
        False: (
            r"\bnot acknowledged\b",
            r"\bunacknowledged\b",
            r"\bno acknowledg(?:e)?ment\b",
            r"\backnowledg(?:e)?ment\b.{0,20}\bnot present\b",
        ),
    },
    "completed": {
        True: (
            r"\b(?:task|work|item|operation)\b.{0,25}(?<!not )\b(?:completed|finished|done|resolved)\b",
            r"\bcompletion\b.{0,25}\b(?:confirmed|recorded|occurred)\b",
        ),
        False: (
            r"\b(?:task|work|item|operation)\b.{0,25}\b(?:not completed|unfinished|remains open|still open)\b",
            r"\bcompletion\b.{0,25}\b(?:pending|not occurred)\b",
        ),
    },
}

COMPILED = {
    field: {value: tuple(re.compile(pattern, re.I) for pattern in patterns) for value, patterns in values.items()}
    for field, values in PATTERNS.items()
}

CRITICAL = {
    "permission",
    "information",
    "need",
    "side_effect",
    "risk",
    "reversibility",
    "execution_possible",
    "completed",
}
EARLIER = re.compile(r"\b(?:earlier|previously|initially|before that|formerly|at first)\b", re.I)
CURRENT = re.compile(r"\b(?:now|currently|at present|latest|final status|as of now|after review|final reading)\b", re.I)
AMBIGUOUS = re.compile(r"\b(?:maybe|possibly|perhaps|unclear|uncertain|rumou?r|reportedly|might|could be|if it were|hypothetically)\b", re.I)
