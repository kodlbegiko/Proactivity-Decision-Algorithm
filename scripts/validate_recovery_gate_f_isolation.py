#!/usr/bin/env python3
"""Fail-closed static guard against retired Gate-F development access."""
from __future__ import annotations

import ast
from pathlib import Path

ROOTS = [Path("src/proactivity/recovery_candidates_v3.py"), Path("src/proactivity/candidate_v3.py")]
ROOTS += sorted(Path("scripts").glob("*recovery*v3*.py"))
ROOTS += sorted(Path("tests").glob("*recovery*v3*.py"))
FORBIDDEN_IMPORT_FRAGMENTS = ("gate_f", "generate_gate_f", "run_gate_f")
FORBIDDEN_PATH_FRAGMENTS = ("gate_f/protected_inputs", "gate_f/protected_labels", "gate_f/protected_private", "gate_f/predictions", "gate_f/baseline_predictions")


def main() -> None:
    findings = []
    for path in ROOTS:
        if not path.exists():
            continue
        source = path.read_text(encoding="utf-8"); tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(fragment in alias.name.lower() for fragment in FORBIDDEN_IMPORT_FRAGMENTS): findings.append(f"{path}: forbidden import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = (node.module or "").lower()
                if any(fragment in module for fragment in FORBIDDEN_IMPORT_FRAGMENTS): findings.append(f"{path}: forbidden import-from {module}")
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value.lower().replace("\\", "/")
                if any(fragment in value for fragment in FORBIDDEN_PATH_FRAGMENTS): findings.append(f"{path}: forbidden protected path literal")
    if findings:
        raise SystemExit("\n".join(findings))
    print("GATE-F RETIRED PROTECTED RECORDS ACCESSED BY DEVELOPMENT = 0")


if __name__ == "__main__":
    main()
