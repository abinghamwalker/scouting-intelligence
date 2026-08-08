# W04 Wyscout schema design R20 — master verification

## Decision

`ACCEPT` as the corrected master candidate for fresh independent review. R20
closes R12-P1-01 without changing the installed environment, dependencies, or
architecture. It truthfully binds the exact current per-row wrapper aliases and
updates the stable schemas affected by that canonical-preimage change.

No W04 field or product implementation is authorized by this master acceptance
alone.

## Artifact integrity and inspection

- R20 design: 4,516 lines, `245,957` bytes; SHA-256
  `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`.
- R20 return: 123 lines, `6,236` bytes; SHA-256
  `ff1c927aee260df324f27347be6671dc53b73f1123f34ab437ad476fbf8dff9f`.
- R19-to-R20 unified diff: 1,389 lines, `88,585` bytes; 247 insertions and
  88 deletions.
- The master read the return and every diff line. R19 had already been read
  completely as the standalone predecessor, so this covers every R20 change and
  every unchanged inherited clause.
- The producer authored exactly its design and return paths.

## Reproduced executable authority

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The master independently enumerated every immediate installed dist-info RECORD
row beginning `../../../bin/`, verified all complete file digests and sizes,
checked target kind/mode/link count, and reconstructed the deterministic wrapper
body from the exact entry-point target.

```text
B:                            35
E:                            33
P:                             1
W:                             1
owners:                       21
E selecting python:           29
P selecting python:            1
E selecting python3:           4
W non-wrapper Ruff binary:      1
```

The exact `python3` tuple set is:

```text
detect-secrets==1.5.0 / detect-secrets /
  console_scripts / detect_secrets.main:main
detect-secrets==1.5.0 / detect-secrets-hook /
  console_scripts / detect_secrets.pre_commit_hook:main
httpx==0.28.1 / httpx /
  console_scripts / httpx:main
pip-licenses==5.5.5 / pip-licenses /
  console_scripts / piplicenses:main
```

Each exceptional row has the exact R12/master owner, RECORD row, target, size,
SHA-256, URL-safe RECORD digest, regular/non-symlink/single-link/mode-`0755`
predicates, `python3` first line, and deterministic post-first-LF body. The other
30 text wrappers use exact `python`; Ruff remains the one Class-W Mach-O row.

R20 derives alias choice from the complete four-field tuple and rejects basename,
owner-only, target-only, `sys.executable`, realpath-only, fallback, repair, and
interchangeable-alias rules. It requires the exact contained
`python3 -> python -> physical interpreter` chain for the exceptional rows.

Stable normalization has two non-interchangeable role tokens:

```text
#!<W04_VENV_WRAPPER_PYTHON>
#!<W04_VENV_WRAPPER_PYTHON3>
```

This preserves the root-independent alias choice rather than collapsing it
because both paths resolve to the same physical bytes.

## Stable schema propagation

The changed executable component is exactly:

```text
w04-installed-executable-census-v3
```

Its enclosing stable manifest is exactly:

```text
w04-code-environment-admission-v15
```

There is no R20 occurrence of the prior v2 census or v14 manifest literal. V15 is
propagated through admission input/result, canonical manifest, component proof,
immutable readback/equality, health, tests, projection/final recheck, two-root
proof, gate, and ledger.

The following remain unchanged:

```text
w04-local-control-bootstrap-v4
w04-outer-environment-bootstrap-v2
w04-child-environment-input-v2
common/admission/rebuild/projection/component cardinalities:
16 / 8 / 10 / 25 / 25 / 20
projection/invocation same-named stable values: 24
```

The H1/H2 construction, exact child inputs/results, twenty component keys, single
build-ID SHA-256, and build/ownership chronology are unchanged.

## Preserved semantic and operational closure

The master reproduced:

- 119 unique field pairs with exact `10/11/26/47/18/4/3` decomposition;
- strict UUID `ActorId`;
- twelve possession predicate fields and all six decisions, including explicit
  `UNMAPPED`;
- only `tests/contracts/test_wyscout_field_registry_authority.py` as the field
  contract-test path;
- exact 17 local resources;
- absent launch/admission/rebuild scripts;
- source, rights, temporal, identity, supported-feature, product, coverage,
  quarantine, path, result-frame, two-root, ownership, gate, and ledger clauses
  unchanged outside the bounded executable/manifest updates; and
- the R19 operational pyc incident snapshot and future dynamic-preflight rule.

## No-write evidence

Every Python helper ran through root `uv run --locked --no-sync` with
`PYTHONDONTWRITEBYTECODE=1` and `python -B`; stdlib-only helpers used `-S -B`.
The complete shell inventories before sync/helpers and after all checks are
identical:

```text
site count:                 1,086
repository count:             58
site metadata SHA-256:
0424caf9281ece4665f090a4095454d29622d6eb748e65cbc0b21701f452a26c
site content SHA-256:
a58b6915d692b5871b2d4aa807ee88523277b46b7e5fd1b99e80a63c6d3c0f46
repository metadata SHA-256:
d948edffb4538de2936a188957cec504de1610bac06abf65eb1fea9a7a7946e3
repository content SHA-256:
0107d67c8a963e08893c52a3c4a60d2ae6f1df1c190de0e226618ce01b4337f5
```

No pyc or environment row was created, deleted, renamed, repaired, or mutated.

## Checks

- Fresh locked sync: PASS; 83 resolved, 82 audited.
- R20 return and complete R19-to-R20 delta readback: PASS.
- Exact 35-row executable/RECORD/template census: PASS.
- Exact 30/4/Ruff alias split and constructive selector: PASS.
- Stable dual-token normalization and contained alias chain: PASS.
- Census v3 and manifest v15 propagation: PASS.
- Zero stale census-v2/manifest-v14 literals: PASS.
- Field/ActorId/possession/cardinality/future-script invariants: PASS.
- Master pyc preflight/postflight: PASS; 1,086/58 and all hashes equal.
- Local-only verifier: PASS; 25/25.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition, product implementation, cloud resource, hosted CI,
public endpoint, Git remote, container, or deployment was created.
