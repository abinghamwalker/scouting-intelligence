# Subagent return

## Task

- task_id: `W04-FEATURE-REGISTRY-REVIEW-01-R3`
- objective: Independently review the complete R3 feature-authority proof, both archived REWORK controls, and accepted possession-pair/applicability composition without changing any frozen authority byte.

## Files changed

- `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-REVIEW-01-R3.md`

## Summary

- Recommendation: `REWORK` with one bounded `P2` and no `P0` or `P1` finding.
- Reproduced both archived failed-review hashes before writing the fixed route: R1 `3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47`; R2 `31653ac8cc12333b91a82ea81e655a69ad71e7b8e20435e14d101c6b15ae62ac`.
- Reproduced the frozen decision physical/canonical hash `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`, candidate physical hash `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`, and candidate canonical hash `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`.
- Confirmed the exact ten bound inputs, fifteen sorted eight-field rows, `4/4/7` state split, exact four supported features, candidate restatement, policies, actor/clock progression, and pre-acceptance no-product boundary.
- Independently derived all 36 unique accepted possession pairs and the exact four `UNMAPPED` pairs. R3's `32/4` partition is a decision partition, not a valid sequence-resolution-capability partition.
- Directly composed the feature helper with the accepted possession-v2 same-period resolver. For `(2,23)` and `(5,51)` (`DEAD_BALL` with `UNASSIGNED`) and `(2,24)` and `(2,26)` (`NON_CONTROL_ADMIN`), the feature helper returned applicable while the accepted resolver returned `INELIGIBLE_UNMAPPED`. Those four predicates can never attach to or open a resolved possession. The actual capability split is 28 potentially resolvable and eight structurally ineligible, including the four `UNMAPPED` pairs.
- Preserved every decision, candidate, test, predecessor, preimage, archive, and acceptance byte; the bounded correction belongs only in a successor focused-contract/evidence packet.

## Tests run

- command: shell-only recursive preflight `.pyc` / `__pycache__` inventory
  - exit status: `0`
  - result: exact packet baseline: `1,150` `.pyc`; sorted path-list SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`; `150` `__pycache__`; sorted path-list SHA-256 `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.
- command: packet-bound SHA-256 verification of both archived REWORK reviews and all R3 frozen artifacts
  - exit status: `0`
  - result: every expected hash reproduced; no protected byte drift.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: complete packet-focused suite passed all `370` collected cases before and after fixed-route review creation; no failure output.
- command: bytecode-disabled locked/no-sync direct accepted-feature plus accepted-possession helper composition
  - exit status: `0`
  - result: exact mismatch reproduced for `(2,23)`, `(2,24)`, `(2,26)`, and `(5,51)`: feature applicable `true`; sequence result `INELIGIBLE_UNMAPPED`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: all `25` checks passed; failures empty; configured remotes zero.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py::test_actual_progression_and_no_product_boundary`
  - exit status: `0`
  - result: `1 passed`; the canonical fixed-route `REWORK` record validates and still blocks acceptance/progression.
- command: shell-only recursive terminal `.pyc` / `__pycache__` inventory after both allowed files
  - exit status: `0`
  - result: exact equality with preflight: `1,150` / `150` and both expected path-list SHA-256 values.

## Artifacts/evidence

- fixed review path: `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
- fixed review physical SHA-256: `acb43cec3597debd8feda0387a8c0720a8353bed7420b6b4083c3b3a6df51677`
- canonical fenced review-record SHA-256: `6aae590291c7a30ca4d6d3d7f3c67bd7d2d2e6ed509c1b3be9cf5fa9f552e50a`
- independent reviewer ActorId: `c37f72f6-508b-5eaf-bf70-65d727287f7b`
- reviewed clock: `2026-07-31T09:42:35Z`
- finding code: `POSSESSION_SEQUENCE_RESOLUTION_CAPABILITY_GAP`

## Risks

- Acceptance must remain blocked because four structurally unassignable accepted predicates can currently satisfy the focused feature-applicability helper under an inconsistent eligibility label.
- No architecture or product change is required. The smallest correction is to derive capability from the accepted sequence attachment/opening semantics, exercise the exact four additional ineligible pairs, and update the bounded successor packet/master evidence.

## Follow-up items

- Return only the focused R3 contract/evidence to a bounded successor producer; preserve all frozen decision/candidate/predecessor/preimage/archive/acceptance bytes.
- Obtain another fresh independent review after master reproduction of the correction.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no sync, install, dependency, `pyproject.toml`, or `uv.lock` change occurred.
- no edits outside `allowed_paths`: confirmed; exactly the two packet-owned paths were created.
- no delegation: confirmed.
- no self-approval: confirmed; this is an independent `REWORK` review, not acceptance.
- no authority/candidate/test/predecessor/preimage/archive/acceptance/product edit: confirmed.
- no formal cross-authority packet, identity, Bronze, Silver, Gold, build, model, product, network, cloud, container, endpoint, hosted-CI, deployment, or Git work: confirmed.
