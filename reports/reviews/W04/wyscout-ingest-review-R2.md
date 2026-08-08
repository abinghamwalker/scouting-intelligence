# W04 Wyscout ingest review — R2

## Review decision

**Recommendation to master: REWORK.**

This is an independent-verifier recommendation, not task or phase approval. The master
retains gate authority.

One P2 redirect-validation defect was reproduced. A syntactically decimal
`X-Amz-Expires` value longer than Python's integer-string conversion limit escapes the
source boundary as raw `ValueError` instead of the required `WyscoutDownloadError`.
The packet stop condition therefore fired before the deferred archive, completion, and
replay matrix could receive complete independent R2 coverage.

## Scope and method

The review read the complete R2 packet, producer packet and return, R1 master review,
canonical source authority, redirect preflight, source implementation, CLI, producer
tests, retained R1 review tests and report, and return template.

All executed payloads, redirect URLs, access keys, response objects, and signatures
were fabricated in memory. An autouse socket denial makes any attempted real network
connection fail immediately. This reviewer did not access Figshare, S3, a provider
object, a real archive, a protected fixture, a data root, a container, or any external
service.

The source, configuration, CLI, producer tests, dependencies, storage, data,
orchestration, and all other non-reviewer paths were read only. Only the three
reviewer-owned R2 paths were changed.

## Ranked finding

### P2 — oversized decimal expiry escapes the domain-error boundary

The redirect validator checks canonical expiry with:

```text
str(int(expiry_text)) == expiry_text
```

Python 3.12 limits decimal-string conversion to 4,300 digits by default. A fabricated
5,000-digit ASCII decimal therefore raises:

```text
ValueError: Exceeds the limit (4300 digits) for integer string conversion
```

That exception is not translated by `_validate_signed_destination` and is not caught by
`_response_url_is_allowed`, which catches only `WyscoutDownloadError`. The malformed
provider-controlled redirect value consequently escapes `download_source_object` as an
unexpected builtin exception.

Independent retained evidence:

- `test_malformed_numeric_expiry_is_domain_error_before_body_read`
- forms `0`, `61`, `-1`, `+1`, `01`, `1.0`, `1_0`, and full-width `１２` correctly
  produce `WyscoutDownloadError`;
- the 5,000-digit decimal alone produces raw `ValueError`;
- before the final exception-type assertion fails, the test proves:
  - response body read count is zero;
  - the response is closed;
  - the temporary working directory is empty.

Impact:

- no invalid payload is read or admitted, so this is not an authority bypass;
- malformed provider-controlled input can escape the adapter's documented failure
  type, unexpectedly terminate callers, and bypass code that safely handles
  `WyscoutDownloadError`;
- the behavior violates the explicit R2 requirement that malformed numeric query
  values fail closed as `WyscoutDownloadError` before body read.

Required correction:

- reject expiry text by a small lexical bound before integer conversion—the only
  authorised values are canonical ASCII decimal `1..60`;
- or catch conversion failures and translate them to `WyscoutDownloadError`;
- retain zero body reads, response closure, and temporary cleanup;
- add producer coverage for an expiry exceeding the interpreter conversion limit;
- redispatch the complete independent ingest matrix after the producer suite is green.

## R1 regression evidence

The independent R1 regressions were adapted to canonical R2:

| R1 defect or boundary | R2 independent result |
| --- | --- |
| Canonical redirect authority loads | PASS |
| Runtime authority exposes exactly one hop and literal-slash encoding | PASS |
| Conforming fabricated one-hop target executes | PASS |
| Observed literal `/` credential separators execute | PASS |
| Redirect response body is read only after validation | PASS |
| Reviewed identity and rights cannot mutate while loading | PASS — all eight retained mutations reject |
| Percent-encoded credential separators | PASS — rejected before body read |
| Mixed literal/encoded separators | PASS — rejected before body read |
| Double-encoded separators | PASS — rejected before body read |
| Backslash separators | PASS — rejected before body read |
| Empty and extra credential segments | PASS — rejected before body read |
| 15-character access key | PASS — rejected before body read |
| 129-character access key | PASS — rejected before body read |
| Lowercase access key | PASS — rejected before body read |
| Non-302 statuses | PASS — 301, 303, 307 and 308 reject |
| Redirect origin binding | PASS — an unreviewed origin rejects |
| Second hop | PASS — exact first 302 succeeds, second 302 rejects |

Each invalid credential case also independently proves response closure and an empty
temporary working directory.

## Stop-condition boundary

The producer's 81-test unit suite remains green inside the combined run and includes
synthetic coverage for the wider status, target, query, signature, length/hash, retry,
cleanup, archive, completion, replay, import, temporal, and rights controls.

Those producer tests are supporting evidence, not a substitute for the packet's
required independent matrix. Once the P2 exception-boundary defect reproduced, this
review stopped rather than:

- editing the immutable producer candidate;
- weakening or marking the regression expected;
- accessing a provider or real payload;
- claiming independent archive/completion/replay coverage that was not completed.

The next review must execute the full deferred matrix, including encryption and
excluded-member non-read/non-persistence, completion-last ordering, every durable-byte
replay read, malformed/conflicting completion evidence, and honest temporal and frozen
rights fields.

## Verification

- `uv run pytest -q tests/unit/test_wyscout_source.py tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `1`
  - result: `1 failed, 102 passed in 0.88s`
  - sole failure: 5,000-digit expiry produces `ValueError`, not
    `WyscoutDownloadError`
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
  - result: status `PASS`, failures `[]`

## Residual risk

- The complete archive, completion, replay, temporal, and rights matrix remains
  independently unverified in R2 because the mandatory P2 stop condition fired.
- This reviewer did not execute the real endpoint. The master-owned header-only
  preflight remains the controlling observation for the literal-slash redirect shape.
- The producer return's requested real acquisition is outside this packet and no real
  acquisition was attempted.
- The master retains producer correction allocation, integration, acquisition, phase
  gate, and checkpoint authority.

## Recommendation

**REWORK.** The R1 redirect and configuration-freezing corrections make substantial
progress and all tested credential aliases fail before body read, but the oversized
numeric expiry violates the required domain-error boundary. This is a recommendation
to the master, not self-approval.

