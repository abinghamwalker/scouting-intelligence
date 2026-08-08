# Subagent return

## Task

- task_id: W04-R21-CROSS-AUTHORITY-TEST-01-R1
- objective: Implement only the frozen R21 cross-authority composability contract test and its mandatory return, without creating a product path.

## Files changed

- tests/contracts/test_w04_r21_cross_authority_composability.py
- reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R1.md

## Summary

- Added an executable positive and negative proof for every R21 Section 13.1 and 13.2 composability case.
- Directly loaded the accepted field-v2, possession-v2, supported-feature, and control-preimage contract helpers with `runpy`; no production semantics were copied into `src/`.
- Proved strict integer-only action-subevent mapping, explicit language-level boolean exclusion, exact preservation/quarantine of the measured 7,821 string values, and rejection of numeric-looking strings without coercion.
- Proved that all 36 admitted integer taxonomy pairs emit canonical subevents, the accepted possession-v2 predicates remain canonical-equal to v1, and a canonical field-v2 action composes through the possession resolver to only `resolved_possession_action_count`.
- Proved the exact ordered 15-row feature roster has exactly four supported features: `action_count`, `coordinate_known_action_count`, `match_count`, and `resolved_possession_action_count`.
- Proved the sibling control preimages are canonical, terminal-LF, descriptor-only inputs in the exact acyclic authority graph, with no feature hash, runtime descendant, output observation, or implementation claim admitted.
- Encoded and validated the exact ordered 30-resource roster, its 17-path v1 prefix, its fixed canonical path-list SHA-256 `0a5a174f05114dc1d260720174f7459526fbbceba3f549200ad6510c243938c6`, and exclusion of returns, product data, generated evidence, and directory shorthand.
- Proved the field-v2 and possession-v2 supersession/digest chain composes into the accepted feature authority and a deterministic five-dependency authority plan while v1/v2 hybrids fail closed.
- Added fail-closed assertions for the intentionally absent independent review and master gate, plus exact synthetic physical-byte binding checks for their future creation by distinct roles.
- Exercised all mutations in memory; no authority, product, manifest, receipt, serializer, build, Bronze, Silver, or Gold path was created.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: 105 passed in 2.97s
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_supported_feature_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: 0
  - result: 476 passed in 35.62s
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: 1 file already formatted
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: 0
  - result: All checks passed
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; zero configured remotes, active branch `main`, local guards and one-root Python 3.12 uv boundary verified, and no hosted CI, deployment, container, or external-service configuration found
- command: `find . -type f -name '*.pyc' -print | wc -l` and sorted path-list SHA-256
  - exit status: 0
  - result: retained 1,150 files; path-list SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`
- command: `find . -type d -name __pycache__ -print | wc -l` and sorted path-list SHA-256
  - exit status: 0
  - result: retained 150 directories; path-list SHA-256 `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`

## Artifacts/evidence

- tests/contracts/test_w04_r21_cross_authority_composability.py
- test artifact physical SHA-256: `9db63adc6494d77b0d8f33ef3cddb657d5ca91b925ba23c83827ad0dfe1ef7c2`
- reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R1.md

## Risks

- The future identity authority artifacts remain intentionally absent and are used only as exact resource-roster path values; no identity acceptance is claimed.
- The independent cross-authority review and master gate remain intentionally absent. The contract fails closed until separately authored artifacts bind the final physical test and return bytes.
- No product-path evidence exists because this packet expressly forbids product implementation.

## Follow-up items

- Dispatch the separately owned independent cross-authority review only after binding this test and return's final physical bytes; dispatch the master gate only after a fixed passing review exists.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
