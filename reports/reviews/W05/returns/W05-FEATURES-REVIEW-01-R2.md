# Subagent return

## Task

- task_id: W05-FEATURES-REVIEW-01-R2
- objective: Independently replay every R1 fully re-signed identity, fabricated W04 Gold and false-claim attack after R2 while confirming accepted feature positives remain exact.

## Files changed

- reports/reviews/W05/w05-feature-registry-independent-review-R2.md
- reports/reviews/W05/returns/W05-FEATURES-REVIEW-01-R2.md

## Summary

- Verdict: **REWORK — P0: 0; P1: 1; P2: 0**.
- R2 closes the three R1 defect classes for the originally demonstrated attacks: fully re-signed W05 identity/semantic replacements reject, the exact accepted W04 product/vector/five-dependency lineage is pinned, and both production/protected flags are false.
- One strict identity blocker remains: JSON `true` and `1.0` both compare equal to the accepted integer `gold_row_count=1`, so both substitute values cross the public W04 admission boundary.
- All other product, manifest, player, count-vector, clock, applicability, authority and re-hashed dependency substitutions independently replayed here reject.

## Tests run

- command: `uv run pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: 0
  - result: 187 passed in 10.01s.
- command: `uv run ruff check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/features`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `uv run lint-imports`
  - exit status: 2
  - result: shared uv cache denied `/Users/adrian/.cache/uv/sdists-v9/.git` before import analysis.
- command: `UV_CACHE_DIR=/tmp/w05-features-review-01-r2-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken; 42 files and 81 dependencies analyzed.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 checks passed.
- command: `UV_CACHE_DIR=/tmp/w05-features-review-01-r2-uv-cache uv run --no-sync python /tmp/w05_features_review_r2_adversarial.py`
  - exit status: 0
  - result: all R1 and expanded R2 attacks rejected except `gold_row_count=true` and `gold_row_count=1.0`, which admitted.

## Artifacts/evidence

- reports/reviews/W05/w05-feature-registry-independent-review-R2.md
- registry digest: `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644`
- W04 family digest: `b3854c5fe1c120233475e3b8224c3f3592d06d656447dedd4f764fe45da36d9b`
- synthetic family digest: `8c0845ab46a71d5cd6542b3e80c568b6a678ab5a9dffbe543e894d6d78eca047`
- fixture digest: `7abd569366caa439cc28563a53c51a0c7ecdd1dfb622bee49d69957f444b9545`
- accepted W04 Gold manifest SHA-256: `08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068`
- accepted W04 lineage: `ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d`
- accepted public result: player `be8da881-2b15-513f-978f-6bb3865bc8e2`, values `(2.0, 2.0, 1.0, 2.0)`.
- failing attack markers: `ACCEPTED_ATTACK w04_row_count_bool`; `ACCEPTED_ATTACK w04_row_count_float`.

## Risks

- Until `gold_row_count` receives strict integer validation, a caller can substitute a different JSON type while satisfying the accepted projection comparison, weakening the exact accepted-Gold identity guarantee.
- The shared-cache import-lint failure is environmental; the packet-authorized isolated `--no-sync` rerun passed.

## Follow-up items

- Add a non-boolean strict-integer `gold_row_count == 1` boundary check and direct boolean/float rejection tests, then obtain fresh independent review.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
