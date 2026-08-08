# W04 Wyscout source-ingest master verification — R3

Verified at: `2026-07-29T15:44:19Z`

## Decision

`W04-SOURCE-INGEST-01` and `W04-SOURCE-INGEST-REVIEW-01` are accepted at R3.
This is task-level acceptance only; W04 remains open because other W04 lanes are
outside this review.

The independent R2 review correctly returned one P2 domain-error defect. The master
reproduced that failure, issued the bounded R3 packet, inspected the returned lexical
expiry bound and producer regression, and redispatched the immutable candidate. The
independent R3 review completed the previously stopped matrix and recommended ACCEPT.

## Corrected authority behavior

- The reviewed `credential_separator_encoding: literal_slash` value is strictly
  parsed and frozen.
- The exact observed literal `/` separators are accepted.
- Percent-encoded, mixed, double-encoded, backslash, empty-segment, and extra-segment
  credential aliases reject before body read.
- Access-key material is limited to 16–128 uppercase ASCII letters or digits.
- A signed expiry must be canonical ASCII decimal in the exact `1..60` range.
- Oversized decimal expiry text is rejected lexically before integer conversion and
  raises `WyscoutDownloadError`.

## Independent evidence

The 98-case independent suite covers:

- redirect status, hop, origin, scheme, host, port, userinfo, path, query, algorithm,
  date, scope, expiry, signed-header, and signature boundaries;
- response status, content length, body length, digest, retry, cleanup, and import
  safety;
- ZIP equality, duplicate, traversal, link/special, encryption, expansion, and
  excluded-member non-read/non-persistence;
- completion-last ordering, canonical evidence, exact no-network replay, every durable
  object/member read, durable-byte corruption, malformed/conflicting manifests,
  temporal honesty, frozen rights, and local-only enforcement.

All payloads, redirect URLs, response objects, credentials, and archives were
fabricated locally. Socket creation was denied in the reviewer suite.

## Master rerun

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- Combined producer and independent pytest: PASS; `180 passed in 1.50s`.
- Ruff format check across producer, CLI, unit, and independent tests: PASS.
- Ruff lint across the same paths: PASS.
- Mypy across source, CLI, and independent tests: PASS.
- Bandit across source and CLI: PASS; no findings.
- `scripts/verify_local_only.py`: PASS; 25 checks, no failures.
- Structured W04 packet/review/registry YAML parse: PASS.
- `git diff --check`: PASS.
- `git remote`: PASS; empty output.

## Scope and acquisition boundary

No real provider request, real payload, data-root write, hosted CI, cloud resource,
public endpoint, container, or deployment was created or used. The container-free
storage decision and unrelated user-owned changes were preserved.

Real provider acquisition was deliberately not run in this correction/review cycle.
It is now eligible for a separately controlled master-owned acquisition step because
the redirect correction and independent review have passed.

