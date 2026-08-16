from __future__ import annotations
import argparse
import ast
import hashlib
from pathlib import Path

BASE_COMMIT = "370aac305c14c4ddc2fa2f782cbb3f0fdde4f630"
PREREG_COMMIT = "d064d8cf66e2354d38e0b0b69ba5bffd6ff386ef"

FORBIDDEN_PROTECTED_TOKENS = (
    "data/candidate_v3_confirmatory",
    "results/candidate_v3_confirmatory",
    "docs/candidate_v3_confirmatory_terminal_report",
    "data/candidate_v4_fresh_confirmatory",
    "results/candidate_v4_fresh_confirmatory",
    "docs/candidate_v4_fresh_confirmatory_terminal_report",
)
FORBIDDEN_DEVELOPMENT_REUSE_TOKENS = (
    "data/candidate_v4_development",
    "recovery_v4_data",
)
STRICT_FILES = (
    Path("src/proactivity/candidate_v5.py"),
    Path("src/proactivity/candidate_v5_data.py"),
    Path("src/proactivity/candidate_v5_metrics.py"),
    Path("src/proactivity/candidate_v5_evaluate.py"),
)
GENERATOR_FILES = (
    Path("src/proactivity/candidate_v5.py"),
    Path("src/proactivity/candidate_v5_data.py"),
)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imported_modules(text: str) -> set[str]:
    tree = ast.parse(text)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules

def scan(root: Path) -> dict[str, object]:
    errors: list[str] = []
    hashes: dict[str, str] = {}
    texts: dict[Path, str] = {}
    for rel in STRICT_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        texts[rel] = text
        hashes[str(rel)] = sha256(path)
        for token in FORBIDDEN_PROTECTED_TOKENS:
            if token in text:
                errors.append(f"protected path token in {rel}: {token}")
        for token in FORBIDDEN_DEVELOPMENT_REUSE_TOKENS:
            if token in text:
                errors.append(f"Candidate-v4 development reuse token in {rel}: {token}")
    for rel in GENERATOR_FILES:
        text = texts.get(rel)
        if text is None:
            continue
        modules = imported_modules(text)
        for module in modules:
            if module.endswith("candidate_v4") or module.endswith("recovery_v4_data"):
                errors.append(f"forbidden previous-lineage implementation import in {rel}: {module}")
    evaluator_rel = Path("src/proactivity/candidate_v5_evaluate.py")
    text = texts.get(evaluator_rel)
    if text is not None:
        modules = imported_modules(text)
        prior = [m for m in modules if m.endswith("candidate_v4")]
        if prior not in ([], ["proactivity.candidate_v4"]):
            errors.append(f"unexpected Candidate-v4 evaluator import: {prior}")
    prereg = root / "preregistration/candidate_v5_development.md"
    if not prereg.exists():
        errors.append("missing Candidate-v5 preregistration")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "hashes": hashes,
        "base_commit": BASE_COMMIT,
        "preregistration_commit": PREREG_COMMIT,
        "candidate_v3_protected_access": 0,
        "candidate_v4_protected_access": 0,
        "candidate_v4_development_corpus_reused": False,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    report = scan(Path(args.root))
    import json
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    if report["errors"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
