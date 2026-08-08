# W04 Wyscout ingest review — R3

## Review decision

**Recommendation to master: ACCEPT.**

This is an independent-verifier recommendation, not task or phase approval. The master
retains gate authority.

The R2 P2 defect is closed. A fabricated 5,000-digit ASCII-decimal
`X-Amz-Expires` value now raises `WyscoutDownloadError` before any body read; the
response is closed and the temporary working directory is empty. The retained shorter
invalid expiry forms have the same fail-closed behavior.

The complete deferred independent redirect, transport, archive, completion, replay,
temporal, rights, import-safety, and local-only matrix passed. No P0-P2 defect was
reproduced.

## Scope and method

The review treated the R3 producer implementation, configuration, CLI, producer tests,
storage implementation, dependencies, orchestration, and data paths as immutable. Only
the three reviewer-owned R3 paths were changed.

All executed source bytes, ZIP files, response objects, signed targets, signatures, and
access keys were fabricated in memory. The review suite has an autouse socket denial,
and replay uses an opener that raises on any call. This reviewer did not contact
Figshare, S3, Wyscout, or any external service and did not access a real payload,
protected fixture, repository data root, run root, or container path.

The final independent suite contains 98 passing cases. Together with the producer's 82
cases, the packet acceptance run contains 180 passing tests.

## R2 stop-condition closure

The retained
`test_malformed_numeric_expiry_is_domain_error_before_body_read` challenges:

- boundary values `0` and `61`;
- signed, padded, floating, and underscore forms `-1`, `+1`, `01`, `1.0`, and `1_0`;
- non-ASCII full-width digits `１２`;
- a 5,000-digit ASCII decimal.

Every case now produces `WyscoutDownloadError`, makes zero response-body reads, closes
the response, and leaves no temporary file. The bounded lexical check therefore
prevents Python's integer-string conversion limit from escaping the source-domain
exception boundary.

## Independent matrix results

### Redirect and transport

- A fabricated exact one-hop signed target with literal `/` credential separators is
  accepted.
- Reviewed status, source origin, one-hop limit, scheme, host, implicit port, userinfo,
  fragment, bucket, file ID, filename, and path encoding are exact.
- Query key presence, cardinality, encoding, algorithm, credential date/region/service,
  date form and validity, expiry, signed headers, and 64-character lower-case
  hexadecimal signature are exact.
- Encoded, mixed, double-encoded, backslash, empty, extra, short, long, and lowercase
  credential variants reject.
- Every challenged invalid final redirect rejects as `WyscoutDownloadError` before a
  body read, closes the response, and removes temporary bytes.
- Non-retryable `400`, `401`, `404`, and `429` responses are not retried and are not
  read. Retryable `500`, `502`, and `503` responses exhaust exactly the configured
  three attempts, with closure and cleanup on every attempt.
- A timeout is retried only within the configured bound.
- Malformed, oversized, zero, negative, and reviewed-size-conflicting
  `Content-Length` values reject before body read. A missing header is allowed only
  when the streamed byte count and digest verify.
- Short, long, and MD5-conflicting bodies reject after bounded reads, with response
  closure and temporary cleanup.
- Importing the acquisition CLI under a non-main module name performs no transport,
  storage construction, or persistence.

### Archive admission

- Both fabricated archives contain exactly the five reviewed admitted members and two
  reviewed scope-excluded members.
- A `ZipFile.open` spy proves that only the five admitted payloads in each archive are
  opened; the two excluded entries are verified only from central-directory metadata.
- Unknown, missing, duplicate, absolute, parent-traversing, backslash, symlink,
  special-file, encrypted, and excessive-compression-ratio variants reject as
  `WyscoutArchiveError`.
- Acquisition persists all ten admitted members and no excluded member payload.
- Completion evidence records the four excluded entries with the expected
  directory-only disposition.

### Completion and replay

- A write-order spy proves that all seven objects and all ten admitted members are
  written before `completion-manifest.json`; completion is the last application-level
  write.
- The completion document is canonical JSON with exact complete state, source
  identity, frozen collection, licence, attribution, source-availability, and actual
  acquisition-time evidence.
- No signed redirect query material is persisted in completion evidence.
- Existing completion causes exact no-network replay. A read spy proves replay reads
  the completion document, every one of the seven durable objects, and every one of
  the ten durable admitted-member payloads.
- Replay re-admits both persisted archives and compares admitted bytes with each
  separately persisted member.
- Independent corruption of an ordinary object, an archive object, and an admitted
  member is rejected without network.
- Malformed, non-canonical, missing-key, rights-conflicting, temporally impossible, and
  object-digest-conflicting completion documents are rejected without network.

### Temporal, rights, and local-only controls

- Acquisition before source availability rejects before transport or destination
  creation.
- Naive and non-UTC acquisition datetimes reject before transport or persistence.
- Honest completion evidence distinguishes actual `acquired_at` from frozen
  `source_available_at` and retains its reviewed basis.
- All eight retained identity/licence/attribution configuration mutations reject.
- Completion replay rejects conflicting frozen licence evidence.
- The repository local-only validator passes every check with `failures: []`.

## Verification

- `uv run pytest -q tests/unit/test_wyscout_source.py tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `0`
  - result: `180 passed in 1.48s`
- `uv run ruff format --check tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `0`
  - result: `1 file already formatted`
- `uv run ruff check tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `0`
  - result: `All checks passed!`
- `uv run mypy tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: status `PASS`; failures `[]`

## Residual risk

- This review deliberately did not execute a real endpoint or payload. Provider
  availability and the live redirect's current header/query shape remain outside this
  packet's no-provider boundary.
- Synthetic ZIPs establish control behavior but do not make claims about the semantic
  quality of real provider records.
- The master retains integration, real-acquisition authorization, phase-gate, and
  checkpoint authority.

## Recommendation

**ACCEPT.** The R2 expiry-domain defect is corrected, every required independent
challenge passed, and no P0-P2 acquisition, redirect, rights, archive, completion,
replay, temporal, or local-only defect was reproduced. This is a recommendation to the
master, not self-approval.
