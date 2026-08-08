# Subagent return

## Task

- task_id: `W04-NESTED-PHYSICAL-PRIMARY-KEY-01`
- objective: Correct the bounded W04 Parquet encoder/physical-key mismatch with
  exact descriptor-owned nested struct primary-key paths, without changing any
  logical model, row population, Arrow field, digest meaning or serializer
  formula.
- producer state: `COMPLETE`; independent review and master acceptance remain
  separate gates.

## Files changed

- `src/scouting/contracts/wyscout_schema.py`
- `src/scouting/storage/formats.py`
- `tests/contracts/test_w04_wyscout_schema_closure.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-NESTED-PHYSICAL-PRIMARY-KEY-01-R1.md`

## Summary

- Added exported `w04_physical_primary_key_paths(root_role)` with one exact,
  immutable path roster for all twelve W04 serialized product roles.
- The three Bronze rosters retain complete source-row identity in exact order:
  `source_manifest_id`, `completion_relative_path`, and
  `source_record_ordinal`. Rejected-field then adds `json_path`.
- Competition, Team, Player, Match, Action, LineupStint and Possession use their
  exact non-null canonical identity field. PlayerMatchFact and Gold retain the
  complete accepted logical primary-key order, with
  `tenant_context.tenant_id` represented as the exact nested physical path.
- Added import-time fail-closed validation that every frozen path exists in its
  accepted descriptor, descends only through non-null `OBJECT_STRUCT` fields,
  and terminates at a non-null `IDENTITY` scalar whose canonical projected key
  value is exact `str` or `int`.
- Extended `encode_w04_wyscout_product_parquet` to parse canonical dotted paths,
  validate them independently against both the explicit descriptor and generated
  Arrow schema, resolve the same path in the projected canonical contract row,
  and compare exact type and value with the supplied key. Existing simple
  top-level field compatibility is retained.
- Preserved key arity, per-position type homogeneity, uniqueness, canonical row
  ordering, contract-row equality, physical controls, semantic framing and both
  digest formulas.
- Closed malformed, empty, double-dot, duplicate, missing, alias/fallback,
  nullable, list, positional-struct, non-scalar, Boolean, null, raw-timestamp,
  type-drift, duplicate-key and reordered-key cases. Added exact repeated
  rejected-field source-row/JSON-path ordering proof plus Fact and Gold nested
  tenant encode proofs.
- Reconciled the packet's exact `str`/`int` terminal requirement at the canonical
  projected key boundary. The accepted Gold key contains three fields physically
  stored as `TIMESTAMP_US_UTC`; the unchanged inverse projection converts each to
  canonical UTC text before comparison. Tests prove physical timestamp to exact
  canonical UTC `str` and reject a raw timestamp or drifted string as a supplied
  key. Omitting those fields or changing them to Arrow UTF-8 would have violated
  the accepted Gold logical key and frozen Arrow schema.

## Tests run

- command: `UV_CACHE_DIR=/tmp/w04-nested-primary-key-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check src/scouting/contracts/wyscout_schema.py src/scouting/storage/formats.py tests/contracts/test_w04_wyscout_schema_closure.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `4 files already formatted`
- command: `UV_CACHE_DIR=/tmp/w04-nested-primary-key-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check src/scouting/contracts/wyscout_schema.py src/scouting/storage/formats.py tests/contracts/test_w04_wyscout_schema_closure.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `UV_CACHE_DIR=/tmp/w04-nested-primary-key-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync mypy src/scouting/contracts/wyscout_schema.py src/scouting/storage/formats.py tests/contracts/test_w04_wyscout_schema_closure.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `Success: no issues found in 4 source files`
- command: `UV_CACHE_DIR=/tmp/w04-nested-primary-key-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_v2_aggregates.py`
  - exit status: `0`
  - result: `360 passed in 55.24s`
- command: `UV_CACHE_DIR=/tmp/w04-nested-primary-key-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync bandit -q -r src/scouting/contracts/wyscout_schema.py src/scouting/storage/formats.py`
  - exit status: `0`
  - result: no findings
- command: `UV_CACHE_DIR=/tmp/w04-nested-primary-key-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync lint-imports`
  - exit status: `0`
  - result: `3 kept, 0 broken`; 39 files and 74 dependencies analyzed
- command: `UV_CACHE_DIR=/tmp/w04-nested-primary-key-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 25 checks, zero failures, main branch and zero remotes
- command: `git diff --check`
  - exit status: `0`
  - result: no whitespace errors

## Artifacts/evidence

- Every fixed binding matched before the authorized edits:
  - `src/scouting/storage/formats.py`:
    `2dfdf3675a47f6c2b53478857de1af27aebecb85def8f0701e6ef86c65fafcc9`
  - `src/scouting/contracts/wyscout_schema.py`:
    `8ff15eb36e588806d3768e7a3769d7e5cad9a95ea994f676f5930bc63205d0f4`
  - `tests/unit/test_w04_wyscout_product_formats.py`:
    `ba38c5a66f41aee8ef2b998f4622c71ec30f3b8861d7ef07d8540d001b0bee89`
  - `tests/contracts/test_w04_wyscout_schema_closure.py`:
    `5daaa32082cc0f82ed9b8b0b61cc06fe9d2db633cb15ed9c9837e491f2b9a5b8`
  - product-contract v2 physical binding:
    `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af`
  - schema-bundle v2 physical binding:
    `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45`
- Fresh aggregate reproduction after implementation:
  - schema-bundle logical digest:
    `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be`
  - schema-bundle physical file: `12295` bytes,
    `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45`
  - product-contract logical digest:
    `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0`
  - product-contract physical file: `6386` bytes,
    `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af`
  - both generated canonical no-LF preimages plus exactly one terminal LF equal
    their accepted files byte-for-byte.
- Frozen final producer-owned implementation/test hashes:
  - `src/scouting/contracts/wyscout_schema.py`:
    `b76ff6d55f841594a337929c382137d27d841b37e49f0f40c1961b9af743bb54`
  - `src/scouting/storage/formats.py`:
    `d5e6690f4b2467baeb364e2f8339b2b091f18bc01f8e18a96e8d770da66af9b6`
  - `tests/contracts/test_w04_wyscout_schema_closure.py`:
    `e6d14e9fb8787990716796b1e9031013a7386fae4d7637ccc77b28d746bb9817`
  - `tests/unit/test_w04_wyscout_product_formats.py`:
    `8fe2d3b587541ee4fd80c6e5604e788b48ef78ba4bdc608a9245b64b30afd345`

## Risks

- No known bounded implementation defect remains. This is a producer return and
  does not self-approve; fresh independent review and master acceptance are still
  required.
- Generic top-level-key compatibility is intentionally retained by packet
  requirement. Product serializers must consume the exported role roster to bind
  the exact W04 physical paths.

## Follow-up items

- Dispatch fresh independent review against the frozen hashes above.

## Scope confirmation

- no Git operations: confirmed; no add, commit, checkout, reset, stash, clean or
  other Git mutation was performed.
- no unauthorised dependency or lockfile changes: confirmed; no dependency,
  provider, network, credential, external-service, cloud, container, deployment or
  publication action occurred. The temporary uv cache was isolated below `/tmp`.
- no edits outside `allowed_paths`: confirmed.
