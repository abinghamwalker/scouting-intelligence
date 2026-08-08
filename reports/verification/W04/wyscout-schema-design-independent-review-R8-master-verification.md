# W04 Wyscout schema design independent review R8 — master verification

## Decision

`REWORK`. The master read the complete 498-line independent review and 97-line
return, began reproduction with a fresh `uv sync --locked --all-groups`, and
confirmed both P1 findings. R11 remains blocked from implementation. The required
R12 is a bounded report-only correction; it needs no architecture, dependency,
provider, rights, network, storage-root, cleanup, Git, or local-only change.

## Integrity

- Independent review: `24,850` bytes; SHA-256
  `94d5a6c56bdc27b8a0c752b8867465d3f47b26af2af54187768ae14d3214583d`.
- Final return: `4,749` bytes; SHA-256
  `136a03fc3c673115c6d8a150901bfef05d15dc1c832422bb1fb15b62f1626efd`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Reviewer ownership remained limited to the independent review and return.
- The two inner future entry points and any launcher implementation remain absent.

## P1-01 reproduced — omitted migration bytecode orphans

Whole-repository traversal excluding `.venv` yields 58 pycs in 19
`__pycache__` directories, not R11's claimed 56/17. There are 38 normal-name
files and 20 pytest-rewrite files. Only 35 normal-name files map to present
`.py` sources. The exact three source-absent files are:

| Path | Mode | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `migrations/__pycache__/env.cpython-312.pyc` | `0o644` | 2,795 | `6d93fd4b51bfcfaed59e59358f6694fef65bf04be088e7ff8377340389990ff2` |
| `migrations/versions/__pycache__/0001_foundation.cpython-312.pyc` | `0o644` | 25,415 | `b10987536a062b17702b1fdb5dbb94ca0b2293f8c6d91e43a9fd4042dfeea84d` |
| `src/scouting/storage/__pycache__/postgres.cpython-312.pyc` | `0o644` | 4,230 | `ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac` |

All have current magic `cb0d0d0a`; all three sibling `.py` sources are absent.
R11 admits only the PostgreSQL predicate. Its exhaustive whole-repository rule
therefore rejects the other two while cleanup is forbidden. R12 must add exact
non-authoritative optional denial predicates for the migration files and update
the operational census, health, required tests, and two-root rule. A broad
arbitrary-orphan class is not accepted.

## P1-02 reproduced — undefined external launcher authority

R11 assigns an unnamed “external admitted launcher” authority to measure the
runtime, create both prefixes, set the pre-interpreter environment, classify
bytecode, launch both children, receive code-manifest bytes, publish the immutable
manifest, cross the build-ID boundary, and perform final checks. The design names
no launcher implementation or exact invocation and defines no bootstrap trust
tuple, repository path/bytes, result-channel framing, diagnostics separation,
writer ownership, stable manifest row, or entry-point replacement/TOCTOU rule.

The two named child scripts cannot implement operations required before their
interpreters exist. Repository script enumeration confirms no launcher exists,
and the ownership sequence contains only the two inner future scripts. R12 must
name the exact future local launcher/control entry point, define its locked/no-sync
no-site invocation and reviewed bootstrap trust, bind its path/bytes and role,
specify a bounded authenticated child-result protocol, assign all transition and
publication owners, and require pre/post identity/digest checks. It must retain
the two existing exact inner argv and cannot introduce site startup, dependency
sync, network, generated wrappers, or another product serializer.

## Retained passing controls

The independent review and master readback found no regression in source rights,
the strict completion envelope, temporal equality rejection, player-match/Gold
keys, source/Gold coverage, exact paths, all-groups closure, Packaging bootstrap,
three denied `.pth` classes, editable-root normalization, 35 installed
executables, three interpreter aliases, site bytecode predicates, 17 resources,
product sole writers, health/card/gate structure, two-root stable identity, or
the two-local-commit ledger.

## Master checks

- Fresh locked sync: PASS; 83 packages resolved, 82 audited.
- Repository bytecode census and source mapping: reproduced both omitted files.
- Exact orphan path/hash/size/mode/magic and source absence: PASS.
- Launcher path/authority/channel/ownership search: reproduced the absence.
- Local-only verification: PASS; 25 checks, zero failures.
- Orchestration YAML before R12 issuance: PASS; 123 files, 23 task IDs, zero
  duplicates.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.
- Parent scope: PASS; no stray `../reports`.

No cloud resource, hosted CI, public endpoint, remote, container, or deployment
was created.
