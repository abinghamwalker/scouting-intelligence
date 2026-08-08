# Subagent return

## Task

- task_id: `W04-FEATURE-REGISTRY-DECISION-01-R2`
- objective: Correct only the focused feature-authority applicability proof so every supported row requires accepted canonical evidence values rather than mere key presence, while preserving every frozen R21 authority byte.

## Files changed

- `tests/contracts/test_w04_supported_feature_authority.py`
- `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-DECISION-01-R2.md`

## Summary

- Replaced presence-only supported-feature applicability evidence with fail-closed value predicates while leaving the exact frozen R21 roster, states, inputs, reasons, policies, hashes, progression routes, and product-absence boundary unchanged.
- `action_count` and `match_count` now require their declared source ID to be an exact positive Python `int`; missing, null, string, float, `Decimal`, Boolean, zero, and negative values are ineligible.
- `coordinate_known_action_count` now requires a list of exactly one or two mappings, each containing exactly `x` and `y`. Each axis must be a finite `int`, `float`, or `Decimal`, must not be a Boolean or string, and must lie within inclusive `0..100`.
- `resolved_possession_action_count` now requires exact `ELIGIBLE_RESOLVED`, exact integer event and subevent taxonomy IDs excluding Booleans, and an exact positive integer team source ID.
- Added positive and negative contract cases for all R1 reviewer challenges and the R2 expansion: missing/null/Boolean IDs, strings, floats, `Decimal` source IDs, zero/negative source IDs, missing/null/empty/oversized/malformed positions, missing/extra axes, nonnumeric/nonfinite/out-of-range axes, missing/mistyped possession selectors, and non-resolved eligibility states.

## Tests run

- command: shell-only recursive preflight `.pyc` / `__pycache__` inventory
  - exit status: `0`
  - result: exact retained baseline reproduced: `1,150` `.pyc`; sorted `.pyc` path-list SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`; `150` `__pycache__`; sorted cache-directory path-list SHA-256 `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `2` inside the managed sandbox before Python startup
  - result: the existing external uv cache was not readable inside the sandbox; no test ran and no repository/environment write occurred. The same locked/no-sync command was rerun with read access to the existing cache.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: complete packet-focused R21/R2 authority/preimage suite `352 passed in 26.61s`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; all `25` checks passed, failures empty, configured remotes zero.
- command: locked/no-sync, bytecode-disabled canonical digest helper
  - exit status: `0`
  - result: decision physical/canonical `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`; candidate physical `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`; candidate parsed canonical `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`.
- command: shell-only recursive terminal `.pyc` / `__pycache__` inventory after this return
  - exit status: `0`
  - result: exact retained baseline equality: `1,150` `.pyc`; sorted `.pyc` path-list SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`; `150` `__pycache__`; sorted cache-directory path-list SHA-256 `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.

## Artifacts/evidence

- corrected focused contract: `tests/contracts/test_w04_supported_feature_authority.py`
  - bytes before return creation: `53,412`
  - physical SHA-256: `2331bf0bdbc25457e29b9e9a72c6667cc4852711ee55bbcc5d63711b005eca03`
- frozen decision: `reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json`
  - physical/canonical SHA-256: `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`
- frozen candidate: `configs/features/wyscout-v5-supported-count-features-v1.yaml`
  - physical SHA-256: `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`
  - parsed canonical SHA-256: `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`
- frozen R1 independent review: `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
  - physical SHA-256: `3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47`
- terminal bytecode inventory: exact equality with the retained R2 baseline; no creation, deletion, or mutation observed.

## Risks

- No unresolved applicability, authority, progression, local-only, retained-inventory, or bounded-scope risk was found in this producer packet.
- This return is producer evidence only. Fresh independent review and master acceptance remain required before any cross-authority, identity, Bronze, Silver, Gold, or product implementation may proceed.

## Follow-up items

- Fresh independent R2 review by an actor distinct from this producer.
- Master independently reads every changed byte and reproduces the complete packet evidence before accepting or returning this correction.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no sync, install, dependency, `pyproject.toml`, or `uv.lock` change occurred.
- no edits outside `allowed_paths`: confirmed; exactly the two packet-owned paths were edited or created.
- no delegation: confirmed.
- no self-approval: confirmed; this is a producer return only.
- no network/provider/product/cross-authority/identity/Bronze/Silver/Gold/cloud/container/endpoint/hosted-CI/deployment work: confirmed.
