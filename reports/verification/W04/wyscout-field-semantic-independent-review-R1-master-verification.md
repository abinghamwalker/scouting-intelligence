# W04 field-semantic independent review R1 — master verification

## Decision

`REWORK`. The independent semantic review itself recommends PASS with zero
findings, but its terminal bytecode inventory failed and the written return
incorrectly claims success. The review is not accepted and formal field
acceptance remains blocked.

No pyc is cleaned, deleted, repaired, or rewritten. R2 is evidence-only and must
start from the newly observed repository state.

## Review record

The review Markdown is 14 lines / 1,299 bytes with complete physical SHA-256:

```text
e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861
```

Its one exact `w04-authority-review-v1` record has canonical SHA-256:

```text
8beb747f71f43586c4a57125fae405e90db8af2bd8b6b408346b38b64d7e7fa0
```

It binds the exact frozen decision and registry physical/canonical digests, uses
independent actor `03a65770-02f6-5eb0-9bd2-e2ebb44b62bd`, records truthful
post-audit UTC `2026-07-30T15:18:11Z`, contains no findings, and recommends PASS.
It is not acceptance.

The reviewer independently reproduced 119 rows, exact
`10/11/26/47/18/4/3` record-kind counts, `27/53/39` decisions, expected transform
distribution, source shapes/support, taxonomy counts, candidate digests,
registry equality, zero unsafe projections/collisions, and the progression
validator's valid and invalid state matrix.

Post-review focused checks passed:

- field contract: 123 passed;
- Ruff format/lint: pass;
- local-only verifier: 25/25;
- frozen candidate/test digests: unchanged;
- acceptance and downstream paths: absent;
- Git remote: empty.

## Terminal environment failure

The R1 return says the terminal shell comparison exited 0 and all six inventory
projections were identical. The reviewer's later final disclosure corrects that
claim:

```text
actual terminal exit: 1
repository preflight entries: 58
repository terminal entries: 59
site entries: 1,086 -> 1,086, identical
```

The repository change is:

```text
NEW
tests/contracts/__pycache__/
  test_wyscout_field_registry_authority.cpython-312-pytest-9.1.1.pyc
size 95,026 / mode 0644 / links 1
SHA-256 cd5aaa7895728f9992008585841958377ad41cea0b78b8659c57b9677c06b217

CHANGED
scripts/__pycache__/verify_local_only.cpython-312.pyc
size 24,014 / mode 0644 / links 1
SHA-256 f2490301227b2a4ff82c4f0f606de53b146ded7f1eea14c3d34a8d169562125a
```

Both terminal pycs have integer mtime `1785424745`, so the drift is one
contemporaneous terminal event, not a relabelled old baseline. Candidate source,
registry, test source, and verifier source bytes remain unchanged.

This violates the packet's fail-closed inventory condition. Counts/content must
not be repaired into success. R2 must instead take a new real preflight
containing the 59 current repository entries, run the exact post-review checks,
and reproduce the same complete state at terminal.

No provider access, network activity, cloud resource, hosted CI, public endpoint,
container, deployment, Git remote, or Git mutation was created.
