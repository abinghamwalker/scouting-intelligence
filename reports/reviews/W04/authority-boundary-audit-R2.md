# W04 independent source-authority boundary audit — R2

- Task: `W04-AUTHORITY-REVIEW-01-R2`
- Reviewer role: independent verifier
- Review date: 2026-07-29
- Recommendation: **ACCEPT**
- Defects: no reproduced `P0`, `P1`, or `P2`
- Data-access status: no protected fixture, real provider payload, external service, or
  network resource was accessed

## Executive result

The master’s verifier-only correction closes the R1 authority-path alias defect.
`is_allowed_config_url` now grants the W04 exception only when the supplied path is
literally equal to the absolute normative path
`ROOT / "configs/sources/w04-provider.yaml"` and the URL string is an exact member of
the frozen allowlist.

The literal canonical path remains allowed. The independent parent-segment and symlink
aliases now both reject, and the producer independently covers the same cases. Every
unchanged R1 challenge also passes: equivalent URL spellings deny, the stricter
project boundary overrides permissive upstream CC BY uses, only five domestic
partitions are admitted, archive safety flags remain mandatory, collection release is
the availability floor, and current/live/population/prospective claims remain
forbidden.

The complete producer-plus-independent suite reports **26 passed**. Ruff formatting,
Ruff lint, and mypy also pass. The reviewer therefore recommends **ACCEPT**. This is an
independent recommendation only; the master retains task, phase, and checkpoint
authority.

## Controlling and reviewed artifacts

The reviewer read every R2 packet-required artifact completely:

- `AGENTS.md`
- `orchestration/task_packets/W04-AUTHORITY-REVIEW-01-R2.yaml`
- `orchestration/task_packets/W04-AUTHORITY-REVIEW-01-R1.yaml`
- `orchestration/reviews/REVIEW-W04-AUTHORITY-REVIEW-01-R1.yaml`
- `scripts/verify_local_only.py`
- `tests/governance/test_w04_source_authority.py`
- `tests/security/test_w04_source_authority_boundary.py`
- `reports/reviews/W04/authority-boundary-audit-R1.md`
- `orchestration/templates/subagent_return.md`

The implementation, producer test, and complete independent R1 matrix were inspected
read-only. The R2 reviewer made no test, implementation, authority, configuration,
policy, documentation, orchestration, dependency, fixture, data, or run-artifact
change. Only this R2 audit and its mandatory return were written.

## R1 defect closure

R1 reproduced one `P2`: `config_path.resolve()` collapsed both a lexical
parent-segment alias and a symlink alias to the normative source configuration, so
both inherited its reviewed URL exception.

R2 readback confirms the correction:

1. `is_allowed_config_url` constructs the literal authority path as
   `ROOT / W04_SOURCE_CONFIG`.
2. It compares the supplied `config_path` directly with that path.
3. It does not call `resolve`, remove parent segments, or follow symlinks for the
   authority identity check.
4. It independently requires exact membership in `ALLOWED_W04_SOURCE_URLS`.
5. The canonical absolute path returns allowed for reviewed URLs.
6. The lexically different `configs/sources/../sources/w04-provider.yaml` path returns
   denied.
7. A temporary symlink to the normative path returns denied.

The correction does not broaden the URL allowlist or alter source authority, rights,
coverage, temporal, or claim declarations.

## Independent executable evidence

The complete R1 reviewer test remains unchanged and creates no provider/network
activity.

| Boundary challenge | R2 result | Evidence |
| --- | --- | --- |
| Literal normative authority path | PASS | Exact reviewed URL remains allowed only at the absolute canonical source-config path |
| Parent-segment alias | PASS | Lexically distinct `../sources/` path is denied |
| Symlink alias | PASS | Temporary alias pointing to the normative config is denied |
| Equivalent URL spellings | PASS | HTTP, host-case, explicit-port, trailing/double-slash, percent-encoded, query, fragment, user-info, and whitespace variants reject |
| Upstream CC BY versus stricter project rights | PASS | Raw export, network transfer, external sharing, remote storage, hosted display, public demo, and external model use remain denied |
| Derivative rights inheritance | PASS | Manifest, licence, attribution, change notice, and frozen historical claim boundary remain mandatory |
| Five domestic partitions | PASS | England, France, Germany, Italy, and Spain remain the exact match/event archive members |
| Tournament, unknown, and unsafe members | PASS | Euro/World Cup-like, Portugal, and parent-traversal mutations reject |
| Archive safety switches | PASS | Unknown-member, link, and absolute/parent-path rejection flags cannot be disabled |
| Temporal availability floor | PASS | One-second-early availability, acquisition-time basis, and pre-release replay mutations reject |
| Frozen claim boundary | PASS | All six current/live/women-youth/prospective/equivalence claim mutations reject |
| Cross-artifact authority identity | PASS | DOI, release, licence, restrictions, and source-config identity remain consistent |
| Producer governance suite | PASS | All producer source-authority cases, including both alias regressions, pass |

## Authority-to-evidence mapping

| Authority boundary | Independent R2 evidence | Assessment |
| --- | --- | --- |
| Exact Wyscout Figshare v5 identity | DOI, version, release, licence, normative source path, card, and recorded decision remain mutually consistent. | PASS |
| Local-only URL exception | Canonical path plus exact URL is allowed; all challenged URL spellings, alternate config paths, parent aliases, and symlink aliases deny. | PASS |
| Rights inheritance | Permissive upstream licence facts remain subordinate to raw-export, network, sharing, hosting, remote-storage, external-model, and public-demo project denials. | PASS |
| Archive/five-competition scope | Only five domestic match/event partitions are admitted; tournament, unknown, traversal, and disabled-safeguard mutations reject. | PASS |
| Temporal availability | Collection release remains the exact availability floor; acquisition/generation time is not evidence and pre-release replay is forbidden. | PASS |
| Claim restrictions | Only frozen historical engineering/retrieval evidence is allowed; current, live, population, prospective, and provider-equivalence claims remain forbidden. | PASS |

## Command results

- `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - `26 passed`
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

- This is a static source-authority review. It does not claim downloaded-file size or
  digest verification, archive extraction, admitted record counts, provider schema,
  data quality, modeling, or serving evidence.
- No network request, provider payload, real-person record, protected fixture,
  external service, credential, or hosted resource was accessed.
- CC BY interpretation and the dataset card remain implementation controls rather
  than legal advice.
- The master retains phase-gate, fresh integration, local-only verification, and every
  Git/checkpoint action.

## Recommendation

**ACCEPT.** The literal-path correction closes the R1 `P2` without weakening any
reviewed URL, rights, archive, temporal, or claim boundary, and the complete
producer-plus-independent authority suite passes. This is a recommendation to the
master and not self-approval or a phase-gate decision.
