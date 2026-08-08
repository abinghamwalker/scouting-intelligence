# Subagent return

## Task

- task_id: W04-R21-CROSS-AUTHORITY-TEST-01-R4
- objective: Remove only the unsupported interpreter-global bytecode assertion, retain normal pytest bytecode, and bind fresh review lineage to this final R4 handback.

## Files changed

- tests/contracts/test_w04_r21_cross_authority_composability.py
- reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R4.md

## Summary

- Removed the fixture assertion that required `sys.dont_write_bytecode` and removed the now-unused `sys` import; the contract no longer depends on a caller-supplied interpreter global.
- Changed the fixed review-bound return to `reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R4.md`, whose complete bytes are read dynamically without embedding a return digest.
- Preserved every Section 13 semantic, lifecycle, authority, review, gate, product, and resource assertion unchanged.
- Preserved R1-R3 returns and the superseded independent-review archive byte-for-byte.

## Tests run

- command: `uv run --locked --no-sync pytest -q tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: exact unsuppressed command passed; 107 passed in 4.32s
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_supported_feature_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: 0
  - result: 478 passed in 40.38s
- command: `uv run --locked --no-sync ruff format --check tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: 1 file already formatted
- command: `uv run --locked --no-sync ruff check tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: All checks passed
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; zero remotes, active branch `main`, local guards and one-root Python 3.12 uv boundary verified, with no hosted CI, deployment, container, or external-service configuration
- command: retained bytecode/cache inventory checks using sorted `find` path lists
  - exit status: 0
  - result: retained 1,151 pyc files at `d9c0a14033a78398072b597944de104470cb69aa3df97ee47ecdde3f182d9a48`; retained 150 cache directories at `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`

## Artifacts/evidence

- tests/contracts/test_w04_r21_cross_authority_composability.py
- final test physical SHA-256: `fffb71d4d382816f3572b575cbcd9e951309f92239ca540327cdb02304c4f9b0`
- reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R4.md

## Risks

- Fresh independent review remains required because the prior PASS review did not reproduce the mandatory unsuppressed pytest environment and is preserved only as superseded archive evidence.

## Follow-up items

- Dispatch fresh independent review only after master reproduction of the exact unsuppressed cross-test command and the complete focused suite.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
