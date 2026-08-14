from __future__ import annotations

import runpy
from pathlib import Path

from proactivity.benchmark_v2_template_balance import activate


def main() -> None:
    # Activate the documented non-normative template-distribution remediation
    # in this process, then execute the original audit entrypoint with argv
    # unchanged. run_path avoids relying on the repository root being importable
    # when this wrapper itself is invoked as scripts/run_gate_c_audit.py.
    activate()
    runpy.run_path(str(Path(__file__).with_name("audit_gate_c.py")), run_name="__main__")


if __name__ == "__main__":
    main()
