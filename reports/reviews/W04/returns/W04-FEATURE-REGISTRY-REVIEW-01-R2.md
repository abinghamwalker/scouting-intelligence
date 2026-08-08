# Subagent return

## Task

- task_id: `W04-FEATURE-REGISTRY-REVIEW-01-R2`
- objective: Perform a fresh independent adversarial review of the corrected
  R21 supported-feature applicability proof and recommend `PASS` only with zero
  P0-P2 findings and a stable retained inventory.

## Files changed

- `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-REVIEW-01-R2.md`

## Summary

- Reconstructed the frozen decision/candidate digests, exact closed schemas,
  ten bindings, fifteen ordered feature rows, `4/4/7` state split, exact four
  supported features, policy closure, candidate restatement, predecessor and
  preimage lineage, UUIDv5 actor/clock progression, and no-product boundary.
- Verified the archived failed R1 review is preserved at SHA-256
  `3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47`
  before replacing the fixed review route.
- Confirmed R2 closes the R1 key-presence defect for source identifiers,
  accepted positions, selector types, team identifiers, and the exact
  `ELIGIBLE_RESOLVED` state string.
- Returned `REWORK` with one bounded P2,
  `POSSESSION_SELECTOR_ACCEPTANCE_GAP`. The corrected helper still returns
  applicable for strict-integer selector pairs `(0,0)`, `(7,999)`,
  `(999999,999999)`, and accepted-but-`UNMAPPED` pair `(9,90)` when the
  context claims `ELIGIBLE_RESOLVED`; the accepted possession-v2 selector
  returns `PREDICATE_UNMAPPED` for every one.
- The frozen R21 decision, candidate, focused contract, predecessors,
  preimages, and archived review require no change. Rework remains bounded to
  the focused applicability helper and its negative cases.

## Tests run

- command: shell-only recursive preflight `.pyc` / `__pycache__` inventory
  - exit status: `0`
  - result: exact retained baseline reproduced: `1,150` `.pyc`; sorted path-list
    SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`;
    `150` `__pycache__`; sorted path-list SHA-256
    `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.
- command: shell SHA-256 verification of the archived failed review and initial
  fixed route
  - exit status: `0`
  - result: both reproduced the required pre-replacement SHA-256
    `3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47`.
- command: packet-focused authority/preimage `pytest` command
  - exit status: `2` before Python startup in the managed sandbox
  - result: the existing external uv-cache path was unreadable; no test
    executed and no repository or environment write occurred.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q
  tests/contracts/test_w04_supported_feature_authority.py
  tests/contracts/test_w04_possession_semantic_v2_authority.py
  tests/contracts/test_w04_field_semantic_v2_authority.py
  tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: `352 passed in 26.87s` before review replacement and
    `352 passed in 28.19s` after writing the fresh fixed-route `REWORK` review.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format
  --check tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check
  tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B
  scripts/verify_local_only.py`
  - exit status: `0`
  - result: `25/25 PASS`; configured remotes zero.
- command: locked/no-sync, bytecode-disabled authority reconstruction
  - exit status: `0`
  - result: decision physical/canonical
    `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`;
    candidate physical
    `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`;
    candidate canonical
    `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`;
    exact eight/seven top-level keys, ten inputs, fifteen unique sorted rows,
    `4/4/7` split, exact supported roster, and semantic restatement.
- command: locked/no-sync, bytecode-disabled R2 applicability challenge
  - exit status: `0`
  - result: valid source IDs/positions/resolved evidence passed; all packet
    missing/null/string/float/decimal/bool/zero/negative/nonfinite/malformed/
    out-of-range cases covered by R2 failed closed, except strict-integer
    impossible possession selector pairs remained applicable.
- command: locked/no-sync, bytecode-disabled accepted possession-selector to
  feature-applicability comparison
  - exit status: `0`
  - result: `(0,0)`, `(7,999)`, `(999999,999999)`, and `(9,90)` each returned
    `PREDICATE_UNMAPPED` from possession-v2 and `True` from feature
    applicability with a claimed `ELIGIBLE_RESOLVED` state.
- command: locked/no-sync review fence, digest, and progression validation
  - exit status: `0`
  - result: one canonical 12-key review record; state `REVIEW_REWORK`;
    physical SHA-256
    `31653ac8cc12333b91a82ea81e655a69ad71e7b8e20435e14d101c6b15ae62ac`;
    record SHA-256
    `57439c69bf347b1b38cc49d735795b81e0ba1ae016e961ef2141e05f17095891`;
    packet UUIDv5 actor and truthful fresh clock validated.
- command: shell-only terminal `.pyc` / `__pycache__` inventory after review and
  return creation
  - exit status: `0`
  - result: exact retained baseline equality: `1,150` `.pyc`; sorted path-list
    SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`;
    `150` `__pycache__`; sorted path-list SHA-256
    `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.

## Artifacts/evidence

- fresh review:
  `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
  - review ID:
    `w04-wyscout-supported-feature-registry-independent-review-R1`
  - reviewed by: `0cb1d025-bd15-5c06-9ebb-7b70e195192f`
  - reviewed at: `2026-07-31T09:20:28Z`
  - recommendation: `REWORK`
  - findings: `P0=0`, `P1=0`, `P2=1`
  - physical SHA-256:
    `31653ac8cc12333b91a82ea81e655a69ad71e7b8e20435e14d101c6b15ae62ac`
  - canonical review-record SHA-256:
    `57439c69bf347b1b38cc49d735795b81e0ba1ae016e961ef2141e05f17095891`
- preserved failed review:
  `reports/reviews/W04/archive/wyscout-supported-feature-registry-independent-review-R1-rework-3b5738da.md`
  - physical SHA-256:
    `3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47`
- frozen focused contract:
  `tests/contracts/test_w04_supported_feature_authority.py`
  - physical SHA-256:
    `2331bf0bdbc25457e29b9e9a72c6667cc4852711ee55bbcc5d63711b005eca03`

## Risks

- Feature acceptance would currently allow its focused proof to accept a
  selector context that cannot be produced by the accepted possession-v2
  selector. This leaves the R21 accepted-evidence composition incomplete.
- Feature acceptance, cross-authority composition, identity, Bronze, Silver,
  Gold, and all product implementation remain blocked.

## Follow-up items

- Bounded producer rework: preserve all frozen authority bytes; strengthen only
  `tests/contracts/test_w04_supported_feature_authority.py` so
  `resolved_possession_action_count` rejects selector pairs that the accepted
  possession-v2 selector cannot admit or resolve, without adding
  `possession_eligibility_state` or any other hidden fourth input to the
  feature row.
- Fresh independent review on the same fixed R21 route after master readback
  and bounded rework.

## Scope confirmation

- no Git operations: confirmed; no Git command was run by this reviewer.
- no unauthorised dependency or lockfile changes: confirmed; no sync, install,
  dependency, `pyproject.toml`, or `uv.lock` change occurred.
- no edits outside `allowed_paths`: confirmed; exactly the two reviewer-owned
  paths were edited or created.
- no delegation: confirmed.
- no self-approval: confirmed; this is an independent `REWORK`, not acceptance.
- no candidate, focused-test, predecessor, preimage, acceptance,
  cross-authority, identity, Bronze, Silver, Gold, build, model, product,
  network, cloud, container, endpoint, hosted-CI, deployment, or external
  service work: confirmed.
