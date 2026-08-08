# Subagent return

## Task

- task_id: W04-R21-CROSS-AUTHORITY-TEST-01-R2
- objective: Correct only the cross-authority contract's serial lifecycle handling so it remains valid before review, after exact review, after the complete master gate, and after later gate-authorized product presence.

## Files changed

- tests/contracts/test_w04_r21_cross_authority_composability.py
- reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R2.md

## Summary

- Preserved all R1 semantic, composability, mutation, authority, resource-roster, and preimage assertions while replacing only permanent-absence assumptions with an explicit serial lifecycle validator.
- Added executable coverage for all four required states: `AWAITING_REVIEW`, `REVIEW_PASS`, `GATE_PASS`, and `GATE_PASS_PRODUCT_PRESENT`.
- An absent review is now a valid pre-review state only when the gate and product paths are also absent; supplying gate or product evidence before review fails closed.
- The fixed review is parsed from exactly one `w04-r21-cross-authority-review-v1` Markdown fence. Its canonical JSON record is closed to `recommendation`, `review_id`, `review_path`, `reviewed_by`, `test_artifact_physical_sha256`, and `test_return_physical_sha256`; it must be `PASS`, use the fixed ID/path, bind the complete current test bytes and preserved R1 return bytes, and use a distinct canonical UUID reviewer.
- The machine gate record is parsed as exact canonical JSON with one terminal LF and is closed to `decision`, `gate_path`, `review_path`, `review_physical_sha256`, and `review_recommendation`. It must bind the complete fixed review Markdown bytes and its `PASS` recommendation.
- Gate completion requires all three fixed control-evidence paths: master verification, canonical machine gate record, and gate return. Partial gate evidence fails closed.
- Gate evidence paths are structurally disjoint from the governed product paths and are never classified as product artifacts.
- Product, serializer, build, Bronze, Silver, Gold, manifest, and receipt paths remain forbidden before the complete gate, but simulated later presence of each is accepted after an exact complete gate.
- The actual-state test now conditionally validates any future fixed review/gate bytes and permits actual governed product presence only after that complete gate; it has no permanent review, gate, or product absence assertion.
- Preserved the R1 producer return byte-for-byte at SHA-256 `24a92563e9f2eae23a66f1da70e7ac1b7647f23a2be4e791024a033be7f60e95`.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: 107 passed in 4.36s
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_supported_feature_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: 0
  - result: 478 passed in 36.42s
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: 1 file already formatted
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: All checks passed
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; zero configured remotes, active branch `main`, local guards and one-root Python 3.12 uv boundary verified, with no hosted CI, deployment, container, or external-service configuration
- command: `find . -type f -name '*.pyc' -print | wc -l` and sorted path-list SHA-256
  - exit status: 0
  - result: retained 1,150 files; path-list SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`
- command: `find . -type d -name __pycache__ -print | wc -l` and sorted path-list SHA-256
  - exit status: 0
  - result: retained 150 directories; path-list SHA-256 `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`

## Artifacts/evidence

- tests/contracts/test_w04_r21_cross_authority_composability.py
- corrected test physical SHA-256: `7eb2640c640ae8fe8d410ded62f9a5a555a600c20ac3228d283b0e7ab6208416`
- preserved R1 producer return: reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R1.md
- preserved R1 producer return physical SHA-256: `24a92563e9f2eae23a66f1da70e7ac1b7647f23a2be4e791024a033be7f60e95`
- reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R2.md

## Risks

- The actual independent review, gate verification, gate record, gate return, and product paths remain intentionally absent; exact later-state behavior is proven with in-memory bytes and paths.
- A future review must use the exact machine fence and six-field closed record described above or the contract will fail closed.
- A future master gate is complete only when all three fixed gate evidence paths exist and the canonical gate record exactly binds the fixed review's complete physical bytes.

## Follow-up items

- Independently review the corrected physical test bytes and preserved R1 return bytes, then materialize only the fixed review artifact/return before master-gate dispatch.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
