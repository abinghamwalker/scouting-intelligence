# Subagent return

## Task

- task_id: `W04-SEASON-LINEUP-PRODUCT-BINDING-REVIEW-01-R1`
- objective: Independently attack the additive season/lineup product-binding
  authority, reproduce its frozen source and UUID evidence, and return `PASS` or
  bounded `REWORK` without editing candidate, test, product, data, or prior bytes.

## Files changed

- `reports/reviews/W04/authorities/wyscout-season-lineup-product-binding-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-SEASON-LINEUP-PRODUCT-BINDING-REVIEW-01-R1.md`

## Summary

- Verdict: `REWORK — AUTHORITY BYTES VALID; PROGRESSION TEST DEFECT`.
- Findings: `P0=0`, `P1=1`, `P2=0`.
- The candidate decision is canonical, all 11 packet-fixed bindings and all ten
  decision-bound inputs reproduce exactly, and no immutable authority defect was
  found.
- Independently reproduced the strict source manifest/member binding, 1,694,720
  bytes, 380 rows, ordinal 379, raw match digest, strict integer
  `seasonId=181150`, target bench/start/substitution counts `1/0/1`, and sole
  minute-82 `playerIn` evidence.
- Independently reproduced the source, season, match, team, player, and
  lineup-stint UUIDv5 chains from their authorized names. Alternate namespace,
  name, source ID, entity, and stint-ordinal attacks produced different IDs and
  were rejected.
- Proved the existing `authority_rows` member is the only integration route; the
  predecessor and candidate projection rosters are the same 25 unique keys; the
  post-hash invocation remains 25 keys; and the single R20 build hash remains
  unchanged.
- Confirmed no identity kind/root, schema root, supported feature, Gold row,
  wider population, runtime, aggregate, product, manifest, receipt, build, or data
  byte was introduced.
- P1 `UNCONDITIONAL_PRODUCT_ABSENCE_GATE`: the new authority test and the prior
  build-authority test both permanently assert that every intended downstream
  product root is absent. Because both tests are always collected, the complete
  repository gate must fail after any separately authorized Bronze, Silver,
  Gold, manifest, or rebuild implementation. This is bounded test/progression
  rework; the immutable decision bytes must remain unchanged.
- Emitted exactly one canonical machine-readable review record with independent
  reviewer UUID `3d9c3b46-afaa-50ad-a48d-48da4fac0bac`, truthful UTC clock,
  exact decision ID/hash, one P1 finding, and recommendation `REWORK`.

## Tests run

- command: `shasum -a 256` over all 11 packet-fixed artifacts
  - exit status: `0`
  - result: every authorization, decision, test, return, verification, prior
    authority, R20/R21, source-manifest, and completion-index hash matched.
- command: local `shasum`, `wc`, and `jq` source reconstruction
  - exit status: `0`
  - result: member SHA-256 `620725c2...fe29`, 1,694,720 bytes, 380 rows; ordinal
    379 match `2499719`; canonical raw-record SHA-256 `1cc084d5...4d86`;
    `seasonId=181150`; target bench/start/substitution counts `1/0/1`; minute 82.
- command: `uv run --locked --no-sync python -B -c <UUIDv5 reconstruction and alternate attacks>`
  - exit status: initial sandbox attempt `2`; exact approved-cache repeat `0`
  - result: all seven namespace/entity IDs and the lineup-stint ID reproduced;
    alternate season namespace/name/value and stint ordinal were rejected. The
    initial failure was only host uv-cache read permission and made no repository
    change.
- command: `uv run --locked --no-sync python -B -c <ten bound-input and projection reconstruction>`
  - exit status: `0`
  - result: `10/10` bound input hashes exact; 25 unique predecessor-equal keys;
    `authority_rows` sole integration; one hash; no 26th key.
- command: `uv run ruff format --check tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: one file already formatted, before and after review materialization.
- command: `uv run ruff check tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: all checks passed, before and after review materialization.
- command: `uv run mypy tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: no issues in one source file, before and after review materialization.
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `157 passed in 3.70s` before review and `157 passed in 3.74s` after
    the live lifecycle parser consumed the canonical `REWORK` review.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS` before and after review; 25 checks, zero remotes, `main`, active
    push guard, Python 3.12.12/root uv environment, and no cloud, hosted CI,
    deployment, container, or external-service definition.
- command: canonical embedded-record validation and artifact hash
  - exit status: `0`
  - result: exactly one machine fence; canonical record SHA-256
    `b1708640631732f304f6c07455ee1530ae0ef800a70276d29fd34b46fc484e3d`;
    review recommendation `REWORK` with counts `0/1/0`.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/authorities/wyscout-season-lineup-product-binding-independent-review-R1.md`
  - physical SHA-256:
    `431e0cfb98c6bbd94b6baf3cb6878c551028e894770fb02ada771be989fc31ba`
  - physical size: `8,046` bytes
  - embedded record SHA-256:
    `b1708640631732f304f6c07455ee1530ae0ef800a70276d29fd34b46fc484e3d`
- reviewed decision remains:
  `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e`
- reviewed authority test remains:
  `0b5b933575f22451b5474323188619acec659c7291262c2e457086319fe93e29`

## Risks

- If either unconditional absence assertion remains in the permanent repository
  suite, the later complete gate will fail as soon as an authorized product root
  exists, preventing valid W04 progression.
- Rework must not weaken pre-implementation absence evidence or mutate either
  immutable decision. It should make only test/progression behavior sensitive to
  the authorized lifecycle transition.

## Follow-up items

- Return a bounded correction packet for the two permanent product-absence tests,
  preserving all authority bytes and adding executable progression coverage.
- Obtain a fresh independent review after that correction before master
  acceptance or downstream product dispatch.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no dependency,
  environment, `pyproject.toml`, or `uv.lock` byte was edited.
- no edits outside `allowed_paths`: confirmed; exactly the two packet-owned paths
  were created.
- no delegation or self-approval: confirmed.
- no provider/network, cloud, container, hosted CI, endpoint, remote, deployment,
  publication, product, manifest, receipt, build, data, runtime, test, candidate,
  prior-authority, or orchestration write: confirmed.
