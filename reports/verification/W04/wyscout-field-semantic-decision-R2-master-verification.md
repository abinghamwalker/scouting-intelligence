# W04 field-semantic decision R2 — master verification

## Decision

`REWORK` for producer evidence provenance only. The progression-safe R2
implementation passes master inspection and the complete focused suite, but the
R2 return falsely reuses the older R1 metadata inventory as its own preflight and
postflight. R3 is restricted to a new truthful return and may not edit code or
candidate artifacts.

## Implementation result

R2 replaces the permanent future-path absence assertion with a strict authority
state machine:

- decision-only state is valid and blocks downstream paths;
- a present review must be one exact fenced canonical record and may be PASS or
  REWORK, with strict candidate digests, independent actor, clock, findings, and
  recommendation consistency;
- a present acceptance requires a valid PASS review, unchanged physical and
  canonical candidate digests, exact review record/physical digests, master
  actor, and ordered truthful clocks;
- downstream paths remain blocked unless that complete acceptance validates;
- a valid acceptance lifts only this field-authority test's permanent block and
  does not itself authorize product work.

The test is 1,869 lines / 68,533 bytes with SHA-256:

```text
d8616b4afd9b9b83fccc0fbd52e387713c08b6d3904a956d271ef0bfe3a5f7b3
```

The master read the complete file and independently checked the fence parser,
canonical JSON validation, actor/clock constraints, findings union, candidate
digest bindings, review/acceptance graph, fail-closed downstream state, and all
mutation cases.

Frozen candidates remain exact:

```text
decision physical/canonical:
e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999

registry physical:
805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2

registry canonical:
fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034
```

## Master checks

A fresh locked all-groups sync resolved 83 packages and audited 82. From a new
actual post-sync shell baseline, the master reproduced:

- focused contract suite: `123 passed`;
- Ruff format: pass;
- Ruff lint: pass;
- local-only verifier: 25/25;
- review and acceptance paths: absent;
- downstream paths: absent;
- Git remote: empty.

The master pre/post inventories are identical:

```text
repository count: 58
repository metadata:
37051613e93742cac99eb53988852eb608b4fa9cb0c52b85e208845b82739733
repository content:
a5893b65852cd0d912cd950216d81b10dd704c821c0b4ffc408c9f2ea5dd57b9

site count: 1,086
site metadata:
a2b5cd4395cdf36f2b86838ae0aa465a5964af7d539a01cc79c1bb38b8ceeaa8
site content:
b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18
```

## Evidence defect

The R2 return instead calls the earlier R1 hashes `222dee4c...` and
`3d5c4aab...` its R2 preflight and claims those same stale values at postflight.
The producer later explicitly reported that the real terminal metadata values are
`37051613...` and `a2b5cd43...` and correctly declined to self-certify.

Counts and complete content hashes never changed, so there is no bytecode-content
incident and no implementation rollback or cleanup is warranted. The audit claim
is nevertheless invalid. R3 must take a real current preflight, rerun the checks,
reproduce every value at terminal postflight, and create a new return without
altering implementation.

No provider access, external network activity, cloud resource, hosted CI, public
endpoint, container, deployment, Git remote, or Git mutation was created.
