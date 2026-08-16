from __future__ import annotations

# Gate-C's initial deterministic three-template hash allocation violated the
# preregistered 34% maximum template-family share. Enable the documented
# four-family non-normative generator remediation before test modules import
# and build Gate-C artifacts. This does not alter the frozen specification,
# oracle, labels, or thresholds.
from proactivity.benchmark_v2_template_balance import activate

activate()
