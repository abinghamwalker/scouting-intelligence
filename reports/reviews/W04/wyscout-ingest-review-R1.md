# W04 Wyscout ingest review — R1

## Review decision

**Recommendation to master: REWORK.**

This is an independent-verifier recommendation, not phase approval. The master retains
gate authority.

Two P1 defects were reproduced. The first prevents the reviewed canonical source
configuration from loading or acquiring any object. The second permits reviewed
identity and rights evidence to change while the pre-redirect producer parser still
loads successfully. The packet stop condition therefore fired before the remaining
archive and replay challenge matrix could be completed.

The executable results below were captured against the R1 producer snapshot. The master
subsequently began separate R2 producer rework while this report was being written.
Those later producer edits were deliberately not assessed and do not change the R1
decision.

## Scope and method

The review read the frozen W04 authority, implementation, CLI, producer tests, producer
return, and return template. It added only reviewer-owned tests and reports.

All executed review payloads and transport responses were fabricated locally. A global
socket denial makes an accidental real connection fail immediately. This reviewer did
not access Figshare, S3, a provider object, a real archive, a protected fixture, or any
network service.

The master separately supplied the read-only endpoint-preflight fact used to assess
operational impact: each exact authorised Figshare `ndownloader` URL responds with HTTP
302 to a short-lived signed HTTPS URL under
`s3-eu-west-1.amazonaws.com/pfigshare-u-files/<file_id>/<filename>`. This reviewer did
not repeat that network request.

## Ranked findings

### 1. P1 — canonical redirect authority is rejected and cannot be executed

The reviewed configuration now declares an exact one-hop redirect authority:

- status 302;
- maximum one hop;
- HTTPS only;
- exact S3 host and path template;
- exact signed-query key set, credential scope, algorithm, signed headers, and
  60-second maximum expiry.

At the R1 snapshot, the producer loader still required the prior exact `acquisition`
key set and raised:

```text
WyscoutConfigError: acquisition keys must be exact;
missing=[], unknown=['redirect_authority']
```

Consequences:

- the canonical configuration cannot load;
- 21 producer tests error during fixture setup;
- no source object can reach download, hash verification, archive admission,
  persistence, completion, or replay;
- the R1 default transport still denies every redirect, while the master-supplied
  endpoint preflight establishes that the exact authorised endpoint requires one.

Independent retained tests:

- `test_canonical_redirect_authority_is_loaded_as_runtime_authority`
- `test_fabricated_reviewed_one_hop_redirect_is_accepted`

The second test uses only a fabricated payload and a fabricated signed S3 final URL
matching the reviewed host, path, query-key, credential-scope, algorithm, signed-header,
and expiry constraints.

Required correction:

- parse and freeze the complete redirect authority in the source model;
- implement exactly one manually validated 302 hop;
- validate the destination before opening it;
- reject URL aliases, any second hop, any other status/scheme/host/path/query shape,
  malformed or duplicate query keys, excess expiry, fragments, userinfo, and authority
  ambiguity;
- preserve the existing exact source URL, size, MD5, SHA-256, retry, and temporary-file
  controls.

### 2. P1 — eight reviewed identity and rights fields remain mutable

To isolate the parser that produced the implementation under review, the independent
test removes only the newly added redirect-authority key from a temporary copy. That
baseline loads. Eight one-at-a-time mutations then also load:

1. `identity.dataset_title`
2. `identity.dataset_authors`
3. `identity.data_paper_doi`
4. `rights.licence_name`
5. `rights.licence_url`
6. `rights.evidence`
7. `rights.attribution.text`
8. `rights.attribution.change_notice`

This violates the packet requirement that exact reviewed identity and rights evidence
cannot change while configuration still loads. It can also produce completion evidence
whose licence name, licence URL, attribution, or change notice differs from the reviewed
authority. Freezing only `licence_id` does not make the surrounding rights evidence
truthful.

Independent retained test:

- `test_reviewed_identity_and_rights_cannot_change_while_loading`

Required correction:

- freeze every reviewed identity, licence, evidence, attribution, and change-notice
  value, including ordered evidence URLs;
- add producer mutation tests for every frozen field;
- ensure completion/replay compare the exact frozen rights and attribution evidence,
  rather than trusting a successfully parsed but altered configuration.

## Positive observations not sufficient for acceptance

Static inspection found deliberate fail-closed controls for exact object identity,
bounded attempts and timeouts, temporary cleanup, size/MD5/SHA-256 verification, ZIP
member-set equality, traversal/link/encryption/expansion rejection, exclusion without
payload opening, completion written after durable inputs, canonical completion parsing,
durable-byte reverification, and no-network replay.

Those controls cannot establish an acceptable integrated source seam while the
canonical configuration is unloadable. In accordance with the packet stop condition,
the reviewer did not broaden work into forbidden producer/configuration edits or claim
unexecuted archive/replay coverage.

## Verification

Packet checks captured at the R1 stop condition, before later R2 producer edits:

- `uv run pytest -q tests/unit/test_wyscout_source.py tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: 1
  - result: `4 failed, 4 passed, 21 errors in 0.73s`
  - retained failures: canonical redirect authority rejected, conforming fabricated
    redirect unavailable, and eight identity/rights mutations accepted
- `uv run ruff format --check tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: 0
  - result: `1 file already formatted`
- `uv run ruff check tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: 0
  - result: `All checks passed!`
- `uv run mypy tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: 0
  - result: `Success: no issues found in 1 source file`

## Required R2 evidence

An independent R2 review should begin only after the producer and canonical authority
load together. It must then run the complete packet matrix for exact redirect
validation, aliases, statuses, lengths, hashes, retries, temporary cleanup, import-time
network denial, ZIP duplicate/traversal/link/encryption/expansion/member-set/exclusion
controls, completion-last ordering, no-network replay, durable-byte reverification,
malformed/conflicting manifests, and honest temporal evidence.
