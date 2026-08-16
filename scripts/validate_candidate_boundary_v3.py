#!/usr/bin/env python3
"""Machine-check Candidate-v3 inference source boundaries."""
from __future__ import annotations

import ast
from pathlib import Path

FILES = [Path("src/proactivity/recovery_candidates_v3.py"), Path("src/proactivity/candidate_v3.py")]
FORBIDDEN_IMPORTS = ("oracle", "specification", "gate_f")
FORBIDDEN_KEYS = {"state", "private_state", "gold_action", "expected_action", "scenario_id", "split_id", "template_id", "relation_id", "rule_id", "prohibition_id", "matched_rule", "prohibited_actions", "eligible_actions"}


def subscript_key(node: ast.Subscript):
    sl = node.slice
    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
        return sl.value
    return None


def main() -> None:
    findings = []
    for path in FILES:
        if not path.exists():
            if path.name == "recovery_candidates_v3.py": findings.append(f"{path}: required candidate-search source missing")
            continue
        source = path.read_text(encoding="utf-8"); tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(part in alias.name.lower() for part in FORBIDDEN_IMPORTS): findings.append(f"{path}: forbidden import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = (node.module or "").lower()
                if any(part in module for part in FORBIDDEN_IMPORTS): findings.append(f"{path}: forbidden import-from {module}")
            elif isinstance(node, ast.Subscript):
                key = subscript_key(node)
                if key in FORBIDDEN_KEYS: findings.append(f"{path}: forbidden inference key {key}")
    if findings:
        raise SystemExit("\n".join(findings))
    print("CANDIDATE V3 SOURCE BOUNDARY = PASS (candidate-visible domain + observation only)")


if __name__ == "__main__":
    main()
