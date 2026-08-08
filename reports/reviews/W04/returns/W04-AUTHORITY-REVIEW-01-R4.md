# Subagent return

## Task

- task_id: `W04-AUTHORITY-REVIEW-01-R4`
- objective: Independently review the bounded one-hop Figshare delivery redirect
  authority, proving it enables only the exact observed transport shape without
  broadening source, storage, credential, transfer, or external-service authority.

## Files changed

- `tests/security/test_w04_source_authority_boundary.py`
- `reports/reviews/W04/authority-boundary-audit-R4.md`
- `reports/reviews/W04/returns/W04-AUTHORITY-REVIEW-01-R4.md`

## Summary

- Retained every R1–R3 exact-URL, path-alias, rights, archive, temporal, claim, and
  cross-artifact challenge.
- Added a consumer-side fail-closed proof for exactly one HTTP 302 from each of the
  seven exact source objects to its literal reviewed scheme, authority, and
  file-ID/name path.
- Proved exact AWS query-key equality and algorithm, credential-scope/date,
  signed-header, compact-date, expiry, and lowercase-hex signature semantics.
- Added adversarial status, hop, scheme, host, port, userinfo, path, fragment, query,
  credential, date, expiry, signed-header, signature, and new-object mutations.
- Proved transient S3 destinations do not enter the configured URL exception and
  cannot grant cloud storage, credentials, accounts, a second hop, an eighth source,
  post-acquisition transfer, public/external services, or deployment.
- Added an automatic socket denial; no reviewer test can access a real network.
- No `P0`–`P2` local-only, rights, or redirect-authority defect was reproduced.
- Recommendation: **ACCEPT**. This is a bounded reviewer recommendation only, not
  self-approval, ingest implementation approval, or a phase decision.

## Tests run

- command:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - baseline result before R4 additions: `44 passed in 0.30s`
- command:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - initial expanded exit status: `1`
  - initial expanded result: `83 passed, 1 failed`; reviewer-only cross-document
    wording assumption, not an authority defect
- command:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - final exit status: `0`
  - final result: `89 passed in 0.47s`
- command:
  `uv run ruff format --check tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command:
  `uv run ruff check tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: `All checks passed!`
- command:
  `uv run mypy tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: validator status `PASS`; failures `[]`

## Artifacts/evidence

- `tests/security/test_w04_source_authority_boundary.py`
  - `_redirect_is_authorised`
  - `test_redirect_authority_is_exact_and_matches_recorded_preflight`
  - `test_redirect_declaration_cannot_be_broadened`
  - `test_each_exact_source_object_has_one_conforming_synthetic_delivery_url`
  - `test_redirect_variants_fail_closed`
  - `test_redirect_cannot_authorise_a_new_source_object_or_url_exception`
  - `test_delivery_hop_grants_no_credentials_storage_or_external_transfer`
- `reports/reviews/W04/authority-boundary-audit-R4.md`
- Final combined result: `89 passed in 0.47s`
- Local-only validator: `PASS`

## Risks

- This is an authority review, not approval of the source-adapter redirect
  implementation or its downloaded bytes.
- Runtime code must validate the destination fully before opening it and deny every
  second redirect; that remains subject to separate producer and independent review.
- Any future provider transport-shape change requires new explicit authority.
- The separate R1 ingest-review REWORK decision is not superseded by this bounded
  authority recommendation.

## Follow-up items

- Master to inspect the three reviewer-owned changes, reproduce the packet checks, and
  decide the R4 authority gate.
- Runtime redirect behavior to remain under the separate producer/reviewer ingest
  correction cycle.

## Scope confirmation

- no Git operations: confirmed; no Git command was run by the reviewer.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no producer, source, configuration, policy, documentation, orchestration, migration,
  script, data, run-artifact, or protected-fixture edits: confirmed.
- no provider, archive, real payload, network, external service, credential, public
  bind, cloud, or deployment access: confirmed.
- no delegation: confirmed.
- no self-approval: confirmed; **ACCEPT** is a recommendation to the master.
