# W08 evidence-export import-boundary correction

Status: **MASTER REPRODUCTION AND FRESH INDEPENDENT REVIEW PASS**

The final import-contract gate found that the evidence exporter lived in
`scouting.operations` while importing peer-layer `scouting.policy`. The contract was
not weakened. The application service was relocated to
`scouting.workflow.evidence_export`, which is the permitted layer for composition of
policy, audit, storage and contracts. `scouting.operations` is telemetry-only again.

## Exact implementation preservation

- pre-move implementation commit:
  `8d6a7b1b202b83486618d018c7cb1d408fa11e48`
- pre-move Git blob, `src/scouting/operations/evidence_export.py`:
  `1c75b99449b9fe1f77e1e4f237283c55fa3492c5`
- current Git hash-object, `src/scouting/workflow/evidence_export.py`:
  `1c75b99449b9fe1f77e1e4f237283c55fa3492c5`
- result: exact byte identity; no exporter implementation line changed

The web composition and direct exporter tests now import the workflow package. No
compatibility re-export or upward/peer dependency was added.

## Master reproduction

- Ruff format/check: PASS.
- mypy on the relocated exporter and W08 web composition: PASS, 2 files.
- import-linter: PASS, 63 files, 144 dependencies, 3 contracts kept and 0 broken.
- export/security/web/browser focused pytest: PASS, 37 tests; one existing third-party
  Starlette TestClient deprecation warning.
- Bandit on the relocated exporter and web composition: PASS, zero findings.

Fresh independent 05F review reproduced the current Git blob-format SHA-1 without
using Git, kept all 3 import contracts, passed the complete 72-test W08 focused
surface and Bandit, and returned PASS with P0/P1/P2/P3 all zero.

This is a dependency-routing correction only. It does not add model, participant,
external-service or protected-output evidence and does not alter the fixed W06 claim
boundary.
