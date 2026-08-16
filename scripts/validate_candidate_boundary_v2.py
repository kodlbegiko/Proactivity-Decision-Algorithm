from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Iterable

from proactivity.benchmark_v2 import ROOT

CONTRACT = ROOT / "gate_c" / "representation_contract_v2.json"


def forbidden_imports(source: str, forbidden_prefixes: Iterable[str]) -> list[str]:
    prefixes = tuple(forbidden_prefixes)
    tree = ast.parse(source)
    findings: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(prefixes):
                    findings.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith(prefixes):
                findings.append(module)
    return sorted(set(findings))


def forbidden_path_references(source: str, forbidden_paths: Iterable[str]) -> list[str]:
    return sorted(path for path in forbidden_paths if path in source)


def validate_source(source: str, contract: dict) -> dict:
    imports = forbidden_imports(source, contract["forbidden_candidate_import_prefixes"])
    paths = forbidden_path_references(source, contract["forbidden_candidate_paths"])
    return {"forbidden_imports": imports, "forbidden_paths": paths, "pass": not imports and not paths}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path, nargs="?")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if args.candidate is None:
        print(json.dumps({"contract_version":contract["version"],"status":"READY_FOR_FUTURE_CANDIDATE_VALIDATION"}, sort_keys=True))
        return
    source = args.candidate.read_text(encoding="utf-8")
    result = validate_source(source, contract)
    print(json.dumps(result, sort_keys=True))
    if not result["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
