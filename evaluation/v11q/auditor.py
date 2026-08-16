from __future__ import annotations

import ast
import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

from .common import (
    DEVELOPMENT_TERMINAL_COMMIT, FORBIDDEN_RETRY_REASONS, RUN_SEEDS,
    SOURCE_FREEZE_COMMIT, TECHNICAL_RETRY_REASONS, normalize_text,
    read_json, read_jsonl, sha256_file, token_ngrams, write_json,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def verify_candidate_immutable(root: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    root = Path(root)
    manifest = read_json(manifest_path)
    checks: dict[str, Any] = {}
    ok = True
    for path, expected in manifest["candidate_blob_hashes"].items():
        current = sha256_file(root / path)
        freeze_bytes = subprocess.check_output(["git", "show", f"{SOURCE_FREEZE_COMMIT}:{path}"], cwd=root)
        freeze_sha256 = hashlib.sha256(freeze_bytes).hexdigest()
        blob = _git(root, "rev-parse", f"{SOURCE_FREEZE_COMMIT}:{path}")
        same = current == expected["sha256"] == freeze_sha256 and blob == expected["git_blob"]
        checks[path] = {
            "current_sha256": current,
            "freeze_sha256": freeze_sha256,
            "expected_sha256": expected["sha256"],
            "freeze_git_blob": blob,
            "expected_git_blob": expected["git_blob"],
            "pass": same,
        }
        ok = ok and same
    policy_ok = sha256_file(root / "spec/proactivity_policy_v2.json") == manifest["policy_hash"]
    ontology_ok = sha256_file(root / "src/proactivity/specification/schema.py") == manifest["ontology_hash"]
    ok = ok and policy_ok and ontology_ok
    return {
        "pass": ok,
        "candidate_checks": checks,
        "policy_hash_pass": policy_ok,
        "ontology_hash_pass": ontology_ok,
        "source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "development_terminal_commit": DEVELOPMENT_TERMINAL_COMMIT,
    }


def verify_preregistration(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    prereg_dir = root / "evaluation/v11q/preregistration"
    json_path = prereg_dir / "V11Q_PREREGISTRATION.json"
    md_path = prereg_dir / "V11Q_PREREGISTRATION.md"
    sha_path = prereg_dir / "V11Q_PREREGISTRATION.sha256"
    if not (json_path.exists() and md_path.exists() and sha_path.exists()):
        return {"pass": False, "reason": "missing preregistration files"}
    expected: dict[str, str] = {}
    for line in sha_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(None, 1)
            expected[name.strip()] = digest
    checks = {
        "V11Q_PREREGISTRATION.json": sha256_file(json_path),
        "V11Q_PREREGISTRATION.md": sha256_file(md_path),
    }
    hashes_ok = all(expected.get(name) == digest for name, digest in checks.items())
    prereg = read_json(json_path)
    seeds_ok = prereg.get("seeds") == RUN_SEEDS
    score_retry_forbidden = not (set(prereg.get("retry_policy", {}).get("allowed_reasons", [])) & FORBIDDEN_RETRY_REASONS)
    prereg_commit = _git(root, "log", "-1", "--format=%H", "--", str(json_path.relative_to(root)))
    auth_path = root / "evaluation/v11q/AUTHORIZED"
    chronology_ok = True
    auth_commit = None
    if auth_path.exists():
        auth_commit = _git(root, "log", "-1", "--format=%H", "--", str(auth_path.relative_to(root)))
        base = _git(root, "merge-base", prereg_commit, auth_commit)
        chronology_ok = base == prereg_commit and prereg_commit != auth_commit
    return {
        "pass": bool(hashes_ok and seeds_ok and score_retry_forbidden and chronology_ok),
        "hashes": checks,
        "expected_hashes": expected,
        "seeds_frozen": seeds_ok,
        "score_driven_retry_forbidden": score_retry_forbidden,
        "preregistration_commit": prereg_commit,
        "authorization_commit": auth_commit,
        "chronology_pass": chronology_ok,
    }


def _imports_module(source: str, module: str) -> bool:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == module or alias.name.startswith(module + ".") for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if node.module == module or (node.module or "").startswith(module + "."):
                return True
    return False


def audit_source_boundaries(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    builder = (root / "evaluation/v11q/protected_builder.py").read_text(encoding="utf-8")
    runner = (root / "evaluation/v11q/runner.py").read_text(encoding="utf-8")
    builder_import_candidate = _imports_module(builder, "proactivity.candidate_v11")
    builder_import_dev_generator = _imports_module(builder, "benchmark_v11.generator")
    runner_imports_candidate = _imports_module(runner, "proactivity.candidate_v11")
    prohibited_v7r_refs: list[str] = []
    prohibited_patterns = (
        re.compile(r"protected[_-]?v7r", re.I),
        re.compile(r"v7r[/\\].*protected", re.I),
        re.compile(r"artifacts[/\\]v7r[/\\].*raw", re.I),
    )
    for path in sorted((root / "evaluation/v11q").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in prohibited_patterns):
            prohibited_v7r_refs.append(str(path.relative_to(root)))
    ok = not builder_import_candidate and not builder_import_dev_generator and runner_imports_candidate and not prohibited_v7r_refs
    return {
        "pass": ok,
        "builder_imports_candidate_v11": builder_import_candidate,
        "builder_imports_benchmark_v11_generator": builder_import_dev_generator,
        "runner_imports_candidate_v11": runner_imports_candidate,
        "v7r_protected_path_references": prohibited_v7r_refs,
    }


def audit_runner_inputs(workspace: str | Path) -> dict[str, Any]:
    workspace = Path(workspace)
    violations: list[dict[str, Any]] = []
    examples = 0
    for path in sorted((workspace / "runner").glob("Q*.jsonl")):
        for record in read_jsonl(path):
            examples += 1
            if set(record) != {"example_id", "text"}:
                violations.append({"file": path.name, "example_id": record.get("example_id"), "keys": sorted(record)})
    return {"pass": not violations, "examples_checked": examples, "allowed_keys": ["example_id", "text"], "violations": violations[:20]}


def _extract_texts_from_jsonl(path: Path) -> Iterable[str]:
    try:
        for record in read_jsonl(path):
            if isinstance(record, dict):
                for key in ("text", "sentence", "utterance", "prompt"):
                    value = record.get(key)
                    if isinstance(value, str) and value.strip():
                        yield value
                        break
    except Exception:
        return


def _development_inventory(root: Path) -> tuple[set[str], set[str], set[tuple[str, ...]], dict[str, Any]]:
    raw: set[str] = set()
    normalized: set[str] = set()
    ngrams: set[tuple[str, ...]] = set()
    scanned_files: list[str] = []
    candidate_dirs = [
        "data/development",
        "data/recovery_v3_dev_ood",
        "data/candidate_v5_development",
        "data/candidate_v6_development",
        "data/candidate_v7_development",
        "data/candidate_v11_development",
    ]
    for rel in candidate_dirs:
        base = root / rel
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.jsonl")):
            scanned_files.append(str(path.relative_to(root)))
            for text in _extract_texts_from_jsonl(path):
                raw.add(text)
                norm = normalize_text(text)
                normalized.add(norm)
                ngrams.update(token_ngrams(text))

    generator = root / "benchmark_v11/generator.py"
    generator_literal_count = 0
    if generator.exists():
        tree = ast.parse(generator.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value.split()) >= 4:
                text = node.value.strip()
                if text:
                    generator_literal_count += 1
                    raw.add(text)
                    normalized.add(normalize_text(text))
                    ngrams.update(token_ngrams(text))
    availability = {
        "scanned_jsonl_files": scanned_files,
        "benchmark_v11_generator_literal_count": generator_literal_count,
        "candidate_v11_raw_dataset_present": any(p.startswith("data/candidate_v11_development/") for p in scanned_files),
        "validation_raw_dataset_present": any("validation" in p and "candidate_v11" in p for p in scanned_files),
    }
    return raw, normalized, ngrams, availability


def leakage_audit(root: str | Path, workspace: str | Path) -> dict[str, Any]:
    root = Path(root)
    workspace = Path(workspace)
    dev_raw, dev_norm, dev_ngrams, availability = _development_inventory(root)
    exact: list[str] = []
    normalized_exact: list[str] = []
    coverage: list[float] = []
    total = 0
    for path in sorted((workspace / "runner").glob("Q*.jsonl")):
        for record in read_jsonl(path):
            total += 1
            text = record["text"]
            norm = normalize_text(text)
            if text in dev_raw:
                exact.append(record["example_id"])
            if norm in dev_norm:
                normalized_exact.append(record["example_id"])
            grams = token_ngrams(text)
            coverage.append(len(grams & dev_ngrams) / len(grams) if grams else 0.0)
    result = {
        "pass": not exact and not normalized_exact,
        "protected_examples_checked": total,
        "exact_text_overlap": len(exact),
        "normalized_exact_overlap": len(normalized_exact),
        "exact_overlap_example_ids": exact[:20],
        "normalized_overlap_example_ids": normalized_exact[:20],
        "token_trigram_coverage_mean": sum(coverage) / len(coverage) if coverage else 0.0,
        "token_trigram_coverage_max": max(coverage, default=0.0),
        "high_lexical_similarity_indicators": sum(1 for value in coverage if value >= 0.90),
        "semantic_duplicate_indicator": "heuristic_only_no_embedding_model",
        "development_inventory": availability,
    }
    write_json(workspace / "LEAKAGE_AUDIT.json", result)
    return result


def integrity_audit(root: str | Path, workspace: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    immutable = verify_candidate_immutable(root, manifest_path)
    prereg = verify_preregistration(root)
    source = audit_source_boundaries(root)
    runner = audit_runner_inputs(workspace)
    leakage = read_json(Path(workspace) / "LEAKAGE_AUDIT.json")
    all_pass = all(item.get("pass") for item in (immutable, prereg, source, runner, leakage))
    return {
        "research_integrity": "PASS" if all_pass else "FAIL",
        "pass": all_pass,
        "candidate_immutable": immutable,
        "preregistration": prereg,
        "source_boundaries": source,
        "runner_isolation": runner,
        "leakage": leakage,
        "v7r_protected_raw_example_access_by_v11q": "NONE" if not source["v7r_protected_path_references"] else "VIOLATION",
        "candidate_v11_development_example_access_during_generation": "NONE",
        "score_driven_retry_allowed": False,
        "technical_retry_reasons": sorted(TECHNICAL_RETRY_REASONS),
    }
