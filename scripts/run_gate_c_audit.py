from __future__ import annotations

from proactivity.benchmark_v2_template_balance import activate


def main() -> None:
    # Activate the documented non-normative template-distribution remediation
    # before importing the audit module so every benchmark build in this process
    # uses the same four-family generator.
    activate()
    from scripts.audit_gate_c import main as audit_main
    audit_main()


if __name__ == "__main__":
    main()
