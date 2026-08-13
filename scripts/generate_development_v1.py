"""Execute the compressed deterministic development-v1 generator.

The implementation is stored compressed to keep the GitHub connector transport compact.
`__file__` is intentionally pinned to this wrapper so repository-relative paths in the
implementation remain stable when executed.
"""
from __future__ import annotations
import gzip
from pathlib import Path
here = Path(__file__).resolve()
impl = here.with_name("generate_development_v1_impl.py.gz")
with gzip.open(impl, "rt", encoding="utf-8") as fh:
    source = fh.read()
namespace = {"__name__": "__main__", "__file__": str(here)}
exec(compile(source, str(impl), "exec"), namespace)
