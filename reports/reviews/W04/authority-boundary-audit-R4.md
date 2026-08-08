# W04 independent source-authority boundary audit — R4

- Task: `W04-AUTHORITY-REVIEW-01-R4`
- Reviewer role: independent verifier
- Review date: 2026-07-29
- Recommendation: **ACCEPT**
- Defects: no reproduced `P0`, `P1`, or `P2`
- Data-access status: no protected fixture, archive, provider payload, external service,
  or network resource was accessed

## Executive result

The bounded redirect correction authorises only delivery of one of the seven exact
Figshare source objects through one HTTP 302 to its corresponding short-lived signed
S3 delivery URL. It does not establish a general S3, cloud-storage, credential,
external-transfer, hosted-service, or additional-source exception.

The independent R4 suite treats the declaration as a source-adapter consumer would.
One conforming synthetic URL per exact source object passes. Mutations to the status,
hop count, destination scheme/authority/path, query-key set, AWS algorithm, credential
scope and date, signed headers, signature shape, expiry, source identity, port,
userinfo, or fragment all fail closed.

All R1–R3 URL, authority-path alias, rights, archive, temporal, claim, and
cross-artifact challenges remain retained. The complete producer-plus-independent
authority suite reports **89 passed**. Formatting, lint, typing, and the repository
local-only verifier also pass.

The reviewer recommends **ACCEPT** for this bounded authority correction. This is an
independent recommendation only; the master retains task and phase authority.
Acceptance here does not approve the source-adapter implementation or supersede the
separate R1 ingest-review REWORK decision.

## Scope and reviewed evidence

The reviewer read every R4 packet-required artifact:

- `AGENTS.md`
- `orchestration/task_packets/W04-AUTHORITY-REVIEW-01-R3.yaml`
- `orchestration/reviews/REVIEW-W04-AUTHORITY-REVIEW-01-R3.yaml`
- `configs/sources/w04-provider.yaml`
- `configs/policies/data-rights.yaml`
- `docs/dataset-cards/w04-source.md`
- `reports/phase-gates/W04/provider-rights-decision-required.md`
- `reports/phase-gates/W04/download-redirect-preflight.md`
- `tests/governance/test_w04_source_authority.py`
- `tests/security/test_w04_source_authority_boundary.py`
- `orchestration/templates/subagent_return.md`

The prior R3 audit and return were also read to preserve the established evidence
boundary. All normative, policy, producer, documentation, preflight, and orchestration
paths were read only. Reviewer writes were limited to the three packet-owned paths.

The master-owned preflight is treated only as recorded evidence. The reviewer did not
repeat its request, resolve a provider hostname, fetch headers or content, open an
archive, or access any real provider object.

## Exact redirect authority

The normative declaration is an exact conjunction:

| Dimension | Required value |
| --- | --- |
| Starting object | One of seven exact allowlisted `ndownloader.figshare.com/files/{file_id}` objects |
| Redirect status | HTTP 302 |
| Hop count | Exactly one |
| Destination scheme | `https` |
| Destination authority | Literal `s3-eu-west-1.amazonaws.com`, without userinfo or port |
| Destination path | `/pfigshare-u-files/{file_id}/{name}` for the same starting object |
| Query keys | Exactly the six declared AWS v4 fields, with no missing, extra, or duplicate key |
| Algorithm | `AWS4-HMAC-SHA256` |
| Credential scope | Dated access-key component ending in `eu-west-1/s3/aws4_request` |
| Signed headers | `host` only |
| Signed date | Valid compact UTC AWS timestamp whose date matches the credential date |
| Expiry | Canonical positive integer no greater than 60 seconds |
| Signature | Exactly 64 lowercase hexadecimal characters |
| Continuation | No second redirect |

The recorded preflight observed a 10-second expiry, within the declared 60-second
ceiling, and deliberately retained no transient signed query value.

## Independent executable evidence

| Challenge | Result |
| --- | --- |
| Exact declaration | PASS — every redirect field equals the reviewed authority |
| Recorded evidence consistency | PASS — config, card, decision, and preflight agree on one bounded Figshare delivery hop and the 60-second ceiling |
| All source identities | PASS — one conforming fabricated signed destination validates for each of the seven exact objects |
| Status and hop count | PASS — 301, 307, hop zero, and hop two reject |
| Scheme and authority | PASS — HTTP, other host, explicit port, and userinfo reject |
| Object path binding | PASS — wrong bucket, file ID, or file name rejects |
| Query-key equality | PASS — missing, additional, duplicate, or declaration-reordered keys reject |
| AWS algorithm and scope | PASS — alternate algorithm, region, or credential date rejects |
| Date semantics | PASS — non-AWS formatting and an impossible calendar date reject |
| Expiry semantics | PASS — zero, non-canonical, non-numeric, and values over 60 reject |
| Signed-header semantics | PASS — any header set other than `host` rejects |
| Signature semantics | PASS — uppercase, short, and non-hex signatures reject |
| URL ambiguity | PASS — fragments, ports, userinfo, and nonliteral destinations reject |
| New source authority | PASS — a fabricated eighth file ID/name is not a source object and cannot use the hop |
| Local-only URL exception | PASS — neither reviewed nor unreviewed transient S3 URLs enter the static configured-URL exception |
| Credentials/accounts | PASS — both remain explicitly unnecessary; the signed query is recorded as transient delivery authorization, not a project credential |
| Storage and later transfer | PASS — cloud/remote storage, post-acquisition transfer, raw export, and external sharing remain denied |
| Public/external services | PASS — hosted display, public demo, external model calls, endpoints, and deployment remain denied |
| Retained R1–R3 boundaries | PASS — exact original URLs, config-path aliases, rights inheritance, archive admission/exclusion, temporal availability, and frozen claims remain green |

The tests install a process-local socket denial so an accidental network attempt would
fail immediately. All redirect URLs are constructed from synthetic access keys,
timestamps, signatures, and object-independent test values; none is a provider URL
obtained by the reviewer.

## Local-only interpretation

The destination hostname describes the provider-controlled delivery location for the
same exact Figshare object. It is not added to the static configured-URL allowlist.
The authority supplies no ability to:

- create or retain an S3 object;
- choose a bucket, host, region, path, file ID, or name;
- acquire an eighth source object;
- provide or store a project credential or account;
- follow a second redirect;
- transfer data after the bounded acquisition;
- enable external sharing, cloud storage, public display, telemetry, hosted services,
  external model calls, or deployment.

The source and policy continue to apply the stricter local project boundary even where
the upstream CC BY licence could permit broader use.

## Verification

- Baseline before R4 additions:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - `44 passed in 0.30s`
- Initial expanded run:
  - `83 passed, 1 failed`
  - the failure was a reviewer-only wording assumption: the decision delegates the
    literal S3 hostname to the normative config while describing the destination as
    Figshare's S3 backend
  - the assertion was corrected without weakening the exact-host check, which remains
    required in the normative config, dataset card, and redirect preflight
- Final combined authority suite:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - `89 passed in 0.47s`
- `uv run ruff format --check tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - `1 file already formatted`
- `uv run ruff check tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - `All checks passed!`
- `uv run mypy tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - `Success: no issues found in 1 source file`
- `uv run python scripts/verify_local_only.py`
  - exit `0`
  - status `PASS`, with no failures across all reported checks

## Residual boundary

- This packet verifies the authority declaration, policy inheritance, and recorded
  preflight only. It does not approve a redirect-following implementation, acquired
  bytes, hashes, archives, ingestion, replay, modeling, serving, or a phase gate.
- Runtime code must independently implement these exact checks before opening the
  destination and must reject every second redirect. That implementation remains
  subject to a separate producer and independent ingest review.
- A provider change to status, host, region, path, query semantics, expiry, or source
  identity requires new explicit authority and remains denied until reviewed.
- The master retains integration, acquisition, phase-gate, and checkpoint authority.

## Recommendation

**ACCEPT.** The declaration is narrow enough for a source adapter to fail closed and
enables only the exact observed one-hop delivery shape. No P0–P2 local-only, rights, or
redirect-authority defect was reproduced. This is a recommendation to the master, not
self-approval or a phase-gate decision.

