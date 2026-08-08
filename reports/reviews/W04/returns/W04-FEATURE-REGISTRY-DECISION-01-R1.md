# Subagent return

## Task

- task_id: `W04-FEATURE-REGISTRY-DECISION-01-R1`
- objective: Materialize the frozen R21 conservative supported-feature decision, deterministic candidate, and progression-safe focused contract with exactly fifteen rows and exactly four supported count features.

## Files changed

- `reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json`
- `configs/features/wyscout-v5-supported-count-features-v1.yaml`
- `tests/contracts/test_w04_supported_feature_authority.py`
- `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-DECISION-01-R1.md`

## Summary

- Materialized the canonical eight-key `SUPPORTED_FEATURE` decision using actor `4efe5691-8903-5148-8275-30d2e7e8aed0` and truthful fresh decision clock `2026-07-31T08:37:00Z`, strictly after the accepted field-v2 and possession-v2 clocks.
- Bound the exact ten R21 inputs: accepted field-v2 and possession-v2 IDs/canonical candidate digests/acceptance digests plus both canonical sibling-control-preimage IDs and digests.
- Materialized exactly fifteen lexically ordered feature rows, each with exactly eight fields. Exactly `action_count`, `coordinate_known_action_count`, `match_count`, and `resolved_possession_action_count` are `SUPPORTED`; the remaining split is four `SUPPRESSED_UNSUPPORTED_DENOMINATOR` and seven `UNAVAILABLE`.
- Preserved the exact R21 row strings, scalar types, input-field order, state combinations, reasons, and ten-key policy object. `resolved_possession_action_count` has only its three canonical selector fields and its executable applicability check additionally requires exact accepted `possession_eligibility_state == ELIGIBLE_RESOLVED`.
- Materialized the exact seven-key deterministic YAML candidate as a semantic restatement of the decision and bound its decision physical digest.
- Added strict canonical JSON/YAML parsing, duplicate/unsafe-type rejection, fixed predecessor and preimage binding, accepted canonical/physical digest separation, exact roster/state/input validation, review/acceptance UUIDv5/digest/clock/progression validation, deferred feature-schema-hash enforcement, no-product progression enforcement, and mutation challenges for all packet-listed roster, input, state, preimage, review, and acceptance failure classes.

## Tests run

- command: shell-only recursive preflight `.pyc` / `__pycache__` inventory
  - exit status: `0`
  - result: `1,145` `.pyc`; `150` `__pycache__`; combined sorted-path SHA-256 `38de1f6ddc5e8086bba61d3c63dfb2acd71a7e00a1c3a7b0c17fbf492601c034`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `2` inside the managed sandbox before Python startup
  - result: existing external uv cache read was denied; no test executed and no repository/environment write occurred. The same mandated locked/no-sync command was rerun with read access to the existing cache.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `1`
  - result: `42 passed, 1 failed`; the failed synthetic fixture incorrectly expected a canonical-but-schema-incomplete JSON object to fail the canonical loader. The fixture was narrowed to genuinely noncanonical whitespace bytes; no authority artifact changed.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: final strengthened focused feature suite `64 passed in 5.05s`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: final complete packet-focused authority/preimage suite `290 passed in 26.61s`.
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
  - result: verified the Python controls before file-backed imports; decision `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`; candidate physical `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`; candidate parsed canonical `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`.
- command: shell-only recursive terminal `.pyc` / `__pycache__` inventory after this return
  - exit status: `0`
  - result: exact baseline equality: `1,145` `.pyc`; `150` `__pycache__`; combined sorted-path SHA-256 `38de1f6ddc5e8086bba61d3c63dfb2acd71a7e00a1c3a7b0c17fbf492601c034`.

## Artifacts/evidence

- decision: `reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json`
  - bytes: `5,322`
  - physical/canonical SHA-256: `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`
- candidate: `configs/features/wyscout-v5-supported-count-features-v1.yaml`
  - bytes: `5,202`
  - physical SHA-256: `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`
  - parsed canonical SHA-256: `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`
- focused contract: `tests/contracts/test_w04_supported_feature_authority.py`
  - bytes before return creation: `47,250`
  - physical SHA-256: `976eeea142ee96d8c4274bb22dd8637c7486c6a1b71aec591f69962117501411`
- accepted predecessor/preimage physical digests reproduced exactly:
  - field-v2 acceptance: `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436`
  - possession-v2 acceptance: `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1`
  - product-contract preimage: `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
  - schema-bundle preimage: `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`
- terminal bytecode inventory: exact equality with preflight; no creation, deletion, or mutation observed.

## Risks

- No unresolved authority, schema, progression, local-only, or scope risk was found in this bounded packet.
- Review, acceptance, cross-authority composition, `feature_schema_hash` use, and all product implementation remain separately owned and unavailable until their serial gates pass.

## Follow-up items

- Fresh independent `W04-FEATURE-REGISTRY-REVIEW-01-R1` review by an actor distinct from this producer.
- Master independently reads every changed byte and reproduces all evidence before accepting or returning this packet.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no sync, install, dependency, `pyproject.toml`, or `uv.lock` change occurred.
- no edits outside `allowed_paths`: confirmed; exactly the four packet-owned paths were created or edited.
- no delegation: confirmed.
- no self-approval: confirmed; this is a producer return only.
- no network/provider/product/cloud/container/endpoint/hosted-CI/deployment work: confirmed.
