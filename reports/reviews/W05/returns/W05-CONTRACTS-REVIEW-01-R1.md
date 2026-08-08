# Subagent return

## Task

- task_id: W05-CONTRACTS-REVIEW-01
- objective: Independently review and adversarially challenge the current additive W05 M0 contracts after R2 without changing candidate source or tests.

## Files changed

- reports/reviews/W05/w05-m0-contracts-independent-review-R1.md
- reports/reviews/W05/returns/W05-CONTRACTS-REVIEW-01-R1.md

## Summary

- Verdict: **REWORK** (`P0: 0; P1: 6; P2: 0`).
- R2 closes the narrow same-artifact-ID manifest substitution and embedded artifact
  schema/model/index parity defects, but direct probes reproduce signed-zero drift,
  non-executable tie policy, request/result brief and trace drift, global rather than
  candidate-specific evidence state, W04 unsupported measured role compatibility,
  arbitrary explanation substitution, PCA manifests without PCA arrays, same-ID taxonomy
  content substitution, and incomplete/misnamed W04 descriptor authority.
- Every finding is mapped to the six exact W05 blocker tests in the review report;
  host/cache metadata is separated as W10-only.

## Tests run

- command: `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py`
  - exit status: 0
  - result: 50 passed in 0.14s.
- command: `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/m0.py`
  - exit status: 0
  - result: success; no issues in 1 source file.
- command: `uv run lint-imports`
  - exit status: 2
  - result: managed sandbox denied reading `/Users/adrian/.cache/uv/sdists-v9/.git`.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-review-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken; 40 files and 78 dependencies analysed.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: status PASS with no failures.
- command: four bounded `uv run python -B - <<'PY' ... PY` adversarial probe invocations
  - exit statuses: 1, 1, 0, 0.
  - result: the first printed both signed-zero acceptances before a strict-enum harness
    error; the second reached explanation construction before a strict Python/JSON-mode
    harness error; the third reproduced explanation, ZERO-state and taxonomy
    substitutions; the fourth reproduced tie/rank, request/result identity, PCA-array and
    W04 authority/state substitutions. Harness errors did not alter repository bytes and
    are retained here truthfully.

## Artifacts/evidence

- reports/reviews/W05/w05-m0-contracts-independent-review-R1.md
- reports/reviews/W05/returns/W05-CONTRACTS-REVIEW-01-R1.md
- Exact probe outputs and smallest bounded corrections are embedded in the review.

## Risks

- Current contracts can authenticate internally consistent but false ranking,
  explanation, taxonomy, role-fit and request/result bytes.
- W05 synthetic-development evidence remains incapable of W06 expert/protected/transfer,
  validation, reliability or product-utility claims.
- The initial uv-cache sandbox denial is W10/host-state only; the isolated-cache import
  check passed and no W05 executable-admission path was reproduced.

## Follow-up items

- Issue bounded R3 contract/test rework for the six P1 findings, then obtain a fresh
  independent review before downstream W05 contract consumers are accepted.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed; only the two exact report paths above.
- no source/test/config/orchestration/data/run/provider/network/external-service access or mutation beyond packet-authorised local reads and checks: confirmed.
- no delegation or self-approval: confirmed.
