# Subagent return

## Task

- task_id: `W04-IDENTITY-BUNDLE-RUNTIME-01-R1`
- objective: Implement, materialize, reopen, and recursively verify the exact source-complete initial W04 Wyscout identity review queue and identity bundle, under the original packet plus `W04-IDENTITY-BUNDLE-RUNTIME-01-R1-ADDENDUM-01`.
- producer disposition: `READY_FOR_INDEPENDENT_REVIEW`; this is not self-approval.

## Files changed

- `src/scouting/contracts/wyscout_identity.py`
- `src/scouting/contracts/__init__.py`
- `src/scouting/identity/wyscout.py`
- `src/scouting/identity/__init__.py`
- `tests/contracts/test_w04_wyscout_identity_bundle.py`
- `tests/unit/test_wyscout_identity.py`
- `data/working/wyscout/v5/identity/review-queues/e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51.identity-review-queue.json`
- `data/working/wyscout/v5/identity/bundles/4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80.identity-bundle.json`
- `reports/reviews/W04/returns/W04-IDENTITY-BUNDLE-RUNTIME-01-R1.md`

## Summary

- Added strict immutable contracts for initial crosswalk rows, the open review queue, effective-state index, and the sidecar-free identity bundle.
- Implemented exact no-newline UUIDv5 preimages for queue items and the addendum-frozen crosswalk namespace/preimage/trace chain. The fixed crosswalk namespace is `fd7bb3ae-10f7-5856-99fb-3854d794273d`.
- Implemented nofollow, stable-file, whole-member verification and streaming strict-JSON reads for the three master members, five match members, and five action members. Identity-bearing values accept JSON integers only; Booleans, floats, decimal objects, and string integers fail.
- Recomputed the full population from admitted source bytes: 5,594 current rows, comprising 7 resolved competitions, 142 resolved teams, 3,603 resolved players, 15 review-required players, one rejected player-zero row, and 1,826 resolved matches.
- Recomputed the 23 source occurrences aggregated into 15 open queue identities and all 226,041 unique player-zero source references. The six measured literal `"null"` substitution containers remain unmapped and contribute no identity; eight actual substitution-zero occurrences collapse to three exact parent match-row references in the rejected row and never enter the queue.
- Added exact authority-clock, same-kind source, canonical-decimal source ID, canonical UUID, reason-token, ordering, uniqueness, count, and recursive queue/bundle bindings.
- Materialized through immutable guarded writes, reopened through exact nofollow reads, compared bytes/digests/semantics, and repeated materialization byte-idempotently. Unequal existing bytes, partial inventory, extras, sidecars, unsafe modes, symlinks, wrong roots, stale bindings, and caller digest-only witnesses fail closed.
- Did not calculate a build ID and did not create Bronze, Silver, Gold, receipt, code-manifest, correction, or other product bytes.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check src/scouting/contracts/wyscout_identity.py src/scouting/contracts/__init__.py src/scouting/identity/wyscout.py src/scouting/identity/__init__.py tests/contracts/test_w04_wyscout_identity_bundle.py tests/unit/test_wyscout_identity.py`
  - exit status: `0`
  - result: 6 files already formatted.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check src/scouting/contracts/wyscout_identity.py src/scouting/contracts/__init__.py src/scouting/identity/wyscout.py src/scouting/identity/__init__.py tests/contracts/test_w04_wyscout_identity_bundle.py tests/unit/test_wyscout_identity.py`
  - exit status: `0`
  - result: all checks passed.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync mypy src/scouting/contracts/wyscout_identity.py src/scouting/identity/wyscout.py`
  - exit status: `0`
  - result: success, no issues in 2 source files.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 34 files and 60 dependencies analyzed; 3 contracts kept and 0 broken.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_wyscout_identity_bundle.py tests/unit/test_wyscout_identity.py tests/contracts/test_w04_identity_ruleset_authority.py`
  - exit status: `0`
  - result: 79 passed in 24.43 seconds.
- command: `uv run bandit -q -r src/scouting/contracts/wyscout_identity.py src/scouting/identity/wyscout.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: status `PASS`, failures `[]`; zero configured remotes, main branch, Python 3.12.12, one root uv environment, no hosted CI/deployment, containers, external service dependencies, or outside-root symlinks.
- command: in-memory `build_initial_identity_bundle(...)` through locked/no-sync uv
  - exit status: `0`
  - result: reproduced queue digest, bundle digest, derived dependency UUID, all 5,594 rows, all 15 queue items, and 91,420,676 canonical bundle bytes without writing product bytes.
- command: `shasum -a 256` over the two materialized artifacts and `find ... -type f | wc -l`
  - exit status: `0`
  - result: exact filename/digest equality and exactly two identity files.
- bounded rework evidence: the first full focused run produced 78 passes and one wrong-root exception-translation failure. The runtime was corrected to translate the bridge path exception into `WyscoutIdentityPathError`; the isolated regression passed, and the complete focused suite then passed 79/79.

## Artifacts/evidence

- queue SHA-256: `e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51`
- queue bytes/mode: `17,412`, `0600`
- identity bundle SHA-256: `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`
- identity bundle bytes/mode: `91,420,676`, `0600`
- R20-derived identity dependency UUID: `31638732-5b25-57db-9eb4-8e943a47a387`
- addendum physical SHA-256 reproduced as `d28e808a91864156b479aa02647859aea8e08ad55b36e9b726192cd9413c84dd`.
- fixed crosswalk test vector for `player:379199`: evidence digest `abc992ddc65429bd73c530a4103daf0567118856aa2b5f0a0771bea29c0595f9`, row UUID `45b2a06d-e200-5cb3-9c9d-8f429291ed31`, trace UUID `121e5662-35f6-5f12-8b3b-c458b30cc38a`.
- exact target canonical IDs, physical ordinals, and raw-record digests for competition 364, teams 1609/1631, player 285508, and match 2499719 are executable assertions in `tests/contracts/test_w04_wyscout_identity_bundle.py`.

## Risks

- The source-complete rejected-zero row intentionally makes the canonical bundle large (91,420,676 bytes); replacing its exact 226,041-member evidence with a count or witness would violate the packet.
- The producer gate is complete, but the packet still requires fresh independent review and master reproduction before downstream build authority consumes these bytes.
- No residual namespace, token, or preimage ambiguity was found after applying the additive crosswalk namespace binding.

## Follow-up items

- Fresh independent reviewer must bind and reproduce the original packet and `W04-IDENTITY-BUNDLE-RUNTIME-01-R1-ADDENDUM-01`, including both content addresses and population vectors.
- Master must independently rerun the complete W04 packet checks and its master-only repository checks before admitting this bundle downstream.

## Scope confirmation

- no Git operations: confirmed; no Git mutation, commit, tag, remote, fetch, push, or checkout was performed by this producer.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no delegation by this subagent: confirmed.
- no provider/network/cloud/container/hosted-CI/public-endpoint/deployment action: confirmed.
