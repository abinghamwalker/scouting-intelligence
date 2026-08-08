# Subagent return

## Task

- task_id: W05-CONTRACTS-01
- objective: Close the R1 manifest/result substitution defects and accepted architecture-preflight gaps through additive, content-addressed W05 M0 contracts.

## Files changed

- src/scouting/contracts/m0.py
- src/scouting/contracts/__init__.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-01-R2.md

## Summary

- Added a self-verifying `M0ArtifactManifest` SHA-256 identity. Its documented canonical projection is compact JSON with sorted keys, defaults included, and `artifact_manifest_digest` excluded; construction and JSON reload reject mismatches.
- Bound registry ID/canonical digest/descriptor digest, evidence class, fitting-population manifest, candidate-universe manifest, safe numeric array descriptors, descriptor-bundle digest, and PCA policies into every artifact identity.
- Added closed real-versus-synthetic evidence classes. `W04_REAL_GOVERNED` admits only the four accepted W04 count features in their authoritative registry order; broader feature sets must be synthetic development.
- Added closed non-executable numeric-array descriptor, dtype, semantic-role, endianness, memory-order, and PCA/tie-policy contracts. Byte length must match the declared safe numeric layout.
- Pinned manifest digest, fit/candidate identities, resolved query digest, ordered exclusions, shared-core version, and canonical UUID tie policy in serving requests; matching revalidates the artifact’s own content digest first.
- Embedded the complete artifact manifest and pinned request in `M0RetrievalResult`, bound them into result bytes, and validated schema/model/index parity, contiguous limit-bounded ranks, exclusions, and request identity.
- Made data-confidence evidence authoritative (score, applicability, coverage, limitations, ordered reasons), forced exact legacy data-confidence projection, and added all-six dimension evidence states so non-measured dimensions cannot rank or carry non-sentinel legacy scores.
- Added adversarial tests for manifest, evidence-class, array/PCA, request/query/universe/tie, rank/exclusion, confidence, dimension-state, schema/model/index, digest, and JSON-reload substitution paths.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/m0.py src/scouting/contracts/__init__.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `uv run ruff check src/scouting/contracts/m0.py src/scouting/contracts/__init__.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/m0.py src/scouting/contracts/__init__.py`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py`
  - exit status: 0
  - result: 50 passed in 0.15s.
- command: `uv run lint-imports`
  - exit status: 0
  - result: 3 contract layers kept; 0 broken; 40 files and 78 dependencies analysed.

## Artifacts/evidence

- src/scouting/contracts/m0.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-01-R2.md
- `M0ArtifactManifest.artifact_manifest_digest` and `M0RetrievalResult.result_digest` are verified SHA-256 identities over their documented canonical wire projections.

## Risks

- W05 evidence remains explicitly synthetic-development or the narrow W04 real governed boundary. These contracts make no expert-relevance, quality, protected-test, calibration, transfer, value, forecast, learned-ranker, or W06 claim.
- Array descriptors seal safe metadata and identities; the later artifact loader must enforce the same descriptor/allowlisted-load checks against bytes before use.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
