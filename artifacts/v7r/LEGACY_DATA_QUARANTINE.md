# V7R Legacy Protected Data Quarantine

All individual example content from every historical development, validation, holdout, qualification, protected, confirmatory, Gate, failed and invalid lineage is classified as `LEGACY_PROTECTED` for V7R.

Quarantined namespaces include, without limitation:

- `data/candidate_v4_*`
- `data/candidate_v5_development/*`
- `data/candidate_v6_development/*`
- `data/candidate_v7_development/*`
- `data/protected/*`
- historical recovery/protected/confirmatory example stores
- historical prediction/example-level diagnostic artifacts where raw example content may be recoverable

V7R generator, candidate runner and scorer development must not read, search, sample, embed, paraphrase, transform or retrieve these individual examples. Only frozen public task specification/schema/oracle, metric definitions and aggregate historical terminal evidence are authorized.

The isolated integrity auditor may scan quarantined files solely to calculate non-content overlap/leakage statistics. It must not emit legacy raw text and must never provide legacy content to the generator or candidate runner.
