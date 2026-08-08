# Subagent return

## Task

- task_id: W05-FEATURES-01
- objective: Close the R1 feature-boundary identity, authenticated W04 Gold, and research-only claim P1s.

## Files changed

- configs/features/w05-m0-feature-registry-v1.json
- src/scouting/features/registry.py
- tests/fixtures/w05/synthetic-development-features-v1.json
- tests/unit/test_w05_features.py
- reports/reviews/W05/returns/W05-FEATURES-01-R2.md

## Summary

- Added immutable independently coded W05 v1 pins at the public registry and fixture load boundaries: root, both families, all three schemas, and fixture ID/version/digest. Fully re-signed root, family cross-wire, descriptor, synthetic provider/evaluation-language, and fixture substitutions now reject.
- Changed both families to `production_evidence=false` and `protected_evaluation=false`. The W04 bridge claim is explicitly accepted-four-count, resemblance-only, and research-only.
- Replaced caller-labelled W04 admission with one exact supplied authenticated projection: the accepted build, manifest/product paths and SHA-256 identities, one row, research-only applicability, player/competition/season/window/snapshot/watermark/cutoff, exact vector `(2,2,1,2)`, and the complete ordered five-dependency envelope. The bridge only compares supplied evidence to these pins; it does not open W04 product or provider data.

## Tests run

- command: `UV_CACHE_DIR=/tmp/w05-features-01-r2-uv-cache uv run --no-sync ruff format --check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r2-uv-cache uv run --no-sync ruff check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r2-uv-cache uv run --no-sync mypy src/scouting/features`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r2-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: 0
  - result: 187 passed in 9.90s.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r2-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken; 42 files and 81 dependencies analyzed.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r2-uv-cache uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 checks passed.

## Artifacts/evidence

- registry digest: `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644`
- W04 family digest: `b3854c5fe1c120233475e3b8224c3f3592d06d656447dedd4f764fe45da36d9b`
- synthetic family digest: `8c0845ab46a71d5cd6542b3e80c568b6a678ab5a9dffbe543e894d6d78eca047`
- synthetic fixture digest: `7abd569366caa439cc28563a53c51a0c7ecdd1dfb622bee49d69957f444b9545`
- accepted W04 dependency lineage: `ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d`

## Risks

- No W04 bytes were opened or changed at materialization time; the bridge intentionally admits only a caller-supplied projection that exactly matches independently coded accepted identities.
- The shared uv cache was not used because it is known to deny access before command execution; every required check passed through the existing locked environment with the isolated `/tmp` cache.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
