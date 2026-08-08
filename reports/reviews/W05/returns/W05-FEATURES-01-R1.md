# Subagent return

## Task

- task_id: W05-FEATURES-01
- objective: Implement the additive versioned W05 feature registry, exact W04 bridge, and cryptographically separate synthetic-development materializer and fixture.

## Files changed

- configs/features/w05-m0-feature-registry-v1.json
- src/scouting/features/__init__.py
- src/scouting/features/registry.py
- tests/fixtures/w05/synthetic-development-features-v1.json
- tests/unit/test_w05_features.py
- reports/reviews/W05/returns/W05-FEATURES-01-R1.md

## Summary

- Added a compact-JSON, self-verifying two-family registry. Its root digest excludes only `registry_digest`; each family and ordered schema has a separate canonical SHA-256 identity. The loader rejects unknown fields, reordered or non-contiguous positions, duplicate identities, digest drift, and non-canonical bytes.
- Bound the W04 real bridge exclusively to the accepted candidate digest `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`, decision digest `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`, descriptor digest `fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e`, and exact ordered four-count schema. W04 admission requires accepted-Gold status, exact authority identity, exact lineage, and strictly pre-cutoff observations/availability.
- Added a provider-free synthetic-development family with the exact six resemblance features and a separate three-field `control_only=true` metadata schema. Decimal arithmetic occurs before the one finite float conversion; zero, missing, suppressed, and unavailable remain distinct `FeatureValue` states with no imputation.
- Added a self-verifying 22-row synthetic fixture: 18 complete rows across three constructed development peer groups plus explicit missing, suppressed, unavailable, and observed-zero edge rows. The fixture states that peer groups are not recruitment outcomes, expert labels, or W06 protected evidence.

## Tests run

- command: `uv run ruff format --check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 1
  - result: the pre-existing shared uv cache denied access to `/Users/adrian/.cache/uv/sdists-v9/.git` before Ruff started.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-uv-cache uv run --no-sync ruff format src/scouting/features tests/unit/test_w05_features.py && UV_CACHE_DIR=/tmp/w05-features-01-uv-cache uv run --no-sync ruff format --check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 0
  - result: formatter applied the final source layout; then 3 files were already formatted.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-uv-cache uv run --no-sync ruff check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-uv-cache uv run --no-sync mypy src/scouting/features`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: 0
  - result: 183 passed in 9.48s.
- command: `uv run lint-imports`
  - exit status: 1
  - result: the same pre-existing unreadable shared uv cache denied access before import analysis.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken; 42 files and 81 dependencies analyzed.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 1
  - result: the same pre-existing unreadable shared uv cache denied access before verifier execution.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-uv-cache uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 local-only checks passed.

## Artifacts/evidence

- registry digest: `5cf2864f763d4670a2baa882c1db32c88cf194f3da0b573b148be50641edd946`
- W04 exact-four schema hash: `cf8847f2b1f70ebf293ce90e48817e80a4e47b78316079bd88e8c2a80bc08127`
- synthetic resemblance schema hash: `1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f`
- synthetic control schema hash: `eae69d45d076f4fc07127d3fd08f45d5ae3d4a7c99ae203d7f63e8a56c88abdb`
- fixture digest: `cd5de08b648a94b0c8d3f2c8e5e84d330887381621492641a5e1514bbf8fc8a7`

## Risks

- The exact shared-cache invocations are blocked before tool execution by the pre-existing unreadable uv cache path. Isolated `--no-sync` executions used the existing locked environment and passed every requested verification.
- No W04 authority, Gold data, provider access, model/serving behavior, dependency state, or shared contract was changed.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
