# W04 independent source-authority boundary audit

- Task: `W04-AUTHORITY-REVIEW-01-R1`
- Reviewer role: independent verifier
- Review date: 2026-07-29
- Recommendation: **REWORK**
- Defects: one `P2`; no reproduced `P0` or `P1`
- Data-access status: no protected fixture, real provider payload, external service, or
  network resource was accessed

## Executive result

The frozen Wyscout Figshare v5 authority is internally consistent across the source
configuration, data-rights policy, dataset card, and recorded user decision. Exact URL
variants are denied. The upstream CC BY grant does not weaken the project's raw-export,
network-transfer, hosted-display, external-model, remote-storage, or public-demo
denials. The archive authority admits exactly the five 2017/18 domestic partitions and
freezes all three safety switches. Availability remains fixed to the collection release,
and current/live/population/prospective claims remain forbidden.

One packet requirement does not pass. The local-only URL exception is bound to
`config_path.resolve()` rather than the literal reviewed path. Consequently, both a
path containing `../sources/` and a symlink alias are treated as the normative
`configs/sources/w04-provider.yaml` authority and receive its network URL exception.
The two input paths are not equal to the reviewed path, but
`is_allowed_config_url(...)` returns `True` for both.

The combined authority suite reports **25 passed, 1 failed**. The failure violates the
definition-of-done requirement that unreviewed path variants reject, so the reviewer
recommends **REWORK**. This is an independent recommendation only; the master retains
acceptance and phase authority.

## Controlling and reviewed artifacts

The reviewer read every packet-required artifact completely:

- `AGENTS.md`
- `orchestration/task_packets/W04-AUTHORITY-REVIEW-01-R1.yaml`
- `configs/sources/w04-provider.yaml`
- `configs/policies/data-rights.yaml`
- `docs/dataset-cards/w04-source.md`
- `reports/phase-gates/W04/provider-rights-decision-required.md`
- `scripts/verify_local_only.py`
- `tests/governance/test_w04_source_authority.py`
- `orchestration/templates/subagent_return.md`

Only the reviewer-owned security test, this report, and the mandatory return were
written. No implementation, authority configuration, policy, documentation,
orchestration, dependency, fixture, data, or run artifact was changed.

## Independent executable evidence

The review uses configuration readback and in-memory adversarial mutations. It does
not acquire provider data or call any URL.

| Boundary challenge | Result | Evidence |
| --- | --- | --- |
| Literal reviewed URLs | PASS | The canonical source path admits the exact ten licence, evidence, and file URLs |
| Equivalent URL spellings | PASS | HTTP, host-case, explicit-port, trailing/double-slash, percent-encoded, query, fragment, user-info, and whitespace variants all reject |
| Non-literal authority filesystem paths | **FAIL** | Both a `..` alias and a symlink alias receive the reviewed URL exception |
| Upstream CC BY versus stricter project rights | PASS | Four mutations attempting raw export, network transfer, external sharing, or policy raw export fail the frozen invariant |
| Derivative rights inheritance | PASS | Manifest, licence, attribution, change notice, and frozen historical claim boundary are mandatory |
| Five domestic partitions | PASS | England, France, Germany, Italy, and Spain are the exact match/event archive members |
| Tournament, unknown, and unsafe members | PASS | Euro/World Cup-like, Portugal, and parent-traversal mutations all fail |
| Archive safety switches | PASS | Unknown-member, link, and absolute/parent-path rejection flags cannot be disabled |
| Temporal availability floor | PASS | One-second-early availability, acquisition-time basis, and pre-release replay mutations all fail |
| Frozen claim boundary | PASS | Each of the six current/live/women-youth/prospective/equivalence claims fails if moved into the allowed set |
| Cross-artifact identity | PASS | DOI, release, licence, project restrictions, current-claim denial, and source-config identity agree across normative artifacts |
| Producer governance suite | PASS | All seven existing W04 source-authority tests pass |

## Ranked defect

### P2 — URL exception follows non-literal aliases of the authority config

Requirement:

- Packet definition of done: unreviewed URL and path variants are rejected.
- `scripts/verify_local_only.py` docstring for `is_allowed_config_url`: only the exact
  reviewed W04 evidence and acquisition URLs are allowed.
- The authority decision identifies
  `configs/sources/w04-provider.yaml` as the normative machine-readable authority.

Reproduction:

1. Select an exact reviewed URL:
   `https://ndownloader.figshare.com/files/15073685`.
2. Confirm the literal normative path is allowed.
3. Construct a lexically different path:
   `configs/sources/../sources/w04-provider.yaml`.
4. Construct a second, unrelated path as a symlink to the normative config.
5. Confirm both paths are unequal to the literal authority path.
6. Expected: both aliases return `False`.
7. Observed: both aliases return `True`.

Executable reproduction:

```text
uv run pytest -q \
  tests/governance/test_w04_source_authority.py \
  tests/security/test_w04_source_authority_boundary.py
```

Result: `25 passed, 1 failed`. The retained failure is
`test_url_exception_rejects_nonliteral_authority_path_variants`.

Root cause:

- `scripts/verify_local_only.py:206` calls `config_path.resolve()` before comparing the
  relative path at line 209.
- Resolution removes the parent-path segment and follows the symlink, collapsing both
  unreviewed inputs to the reviewed target.

Impact:

- The URL destination remains one of the exact reviewed endpoints, so this review did
  not reproduce arbitrary-network access.
- The authority-location guarantee is nevertheless weaker than declared: a different
  configuration path can inherit an exception reserved for one normative artifact.
  That breaks the packet's exact path boundary and can allow consumers or future
  configuration scanning to treat an alias as independently authorised.

Bounded correction:

1. In `is_allowed_config_url`, require `config_path` to equal the literal absolute
   `ROOT / W04_SOURCE_CONFIG` path before granting the exception.
2. Do not normalize parent segments or follow symlinks for the authority-path identity
   comparison.
3. Retain exact string membership in `ALLOWED_W04_SOURCE_URLS`.
4. Add producer-owned regressions for both the `..` alias and a symlink alias.
5. Rerun this independent packet after the master accepts the correction.

The correction belongs to `scripts/verify_local_only.py` and producer governance tests,
which are outside this packet. The reviewer made no implementation change.

## Authority-to-evidence mapping

| Authority boundary | Independent evidence | Assessment |
| --- | --- | --- |
| Exact Wyscout Figshare v5 identity | DOI, collection version, release time, licence, source path, card, and user-decision report agree. | PASS |
| Local-only URL exception | Exact URL string variants reject, but non-literal filesystem aliases inherit the exception after path resolution. | **REWORK — P2** |
| Rights inheritance | CC BY permissions remain upstream facts while raw export, network transfer, public/hosted display, remote storage, external model calls, and public demo remain denied by the stricter project boundary. | PASS |
| Archive/five-competition scope | Only five domestic match and event members are admitted; tournament, unknown, traversal, and disabled-safeguard mutations fail. | PASS |
| Temporal availability | Collection release is the exact availability floor; acquisition/generation time is not evidence and pre-release replay remains forbidden. | PASS |
| Claim restrictions | Only frozen historical engineering/retrieval evidence is allowed; all six current, live, population, prospective, and equivalence claims remain forbidden. | PASS |

## Command results

- Baseline producer suite:
  `uv run pytest -q tests/governance/test_w04_source_authority.py`
  - exit `0`
  - `7 passed`
- Final combined review:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit `1`
  - `25 passed, 1 failed`
  - sole failure:
    `test_url_exception_rejects_nonliteral_authority_path_variants`
- `uv run ruff format --check tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - one file already formatted
- `uv run ruff check tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - all checks passed
- `uv run mypy tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - no issues found in one source file

## Residual boundary

- This static authority review does not claim acquired-file digest, size, archive
  extraction, five-partition record-count, provider schema, data-quality, model, or
  serving evidence.
- No network request, provider payload, real-person record, protected fixture, or
  external service was accessed.
- CC BY interpretation and the dataset card are implementation controls, not legal
  advice.
- The master retains correction allocation, independent rerun, phase-gate, and every
  Git/checkpoint action.

## Recommendation

**REWORK.** Preserve the passing URL, rights, archive, temporal, and claim controls,
but bind the URL exception to the literal normative authority path and independently
rerun this packet before W04 authority acceptance.
