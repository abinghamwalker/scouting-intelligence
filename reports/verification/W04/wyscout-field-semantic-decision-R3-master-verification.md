# W04 field-semantic decision R3 — master verification

## Decision

`ACCEPT` as the frozen candidate for fresh independent review. This acceptance is
the master task decision only; it is not the formal
`w04-wyscout-field-semantic-acceptance-v1` authority and does not authorize
Bronze or any downstream product work.

## Candidate

The accepted candidate remains:

```text
decision physical/canonical SHA-256:
e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999

registry physical SHA-256:
805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2

registry canonical SHA-256:
fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034

contract-test physical SHA-256:
d8616b4afd9b9b83fccc0fbd52e387713c08b6d3904a956d271ef0bfe3a5f7b3
```

The 119 rows remain exact, unique, roster ordered, source-shape bound, and
conservative. Counts are `10/11/26/47/18/4/3`; decisions are 27 TRANSFORM,
53 PRESERVE_UNMAPPED, and 39 FORBIDDEN.

The progression-safe contract strictly validates the future review and
acceptance when present and blocks all 13 downstream paths without a complete
valid acceptance. The master read all 1,869 test lines and found no remaining
implementation defect.

## R3 evidence closure

R3 wrote only its 149-line / 6,746-byte return, SHA-256:

```text
e51c9c4bf2342efebcf01154a70bc4053c1f3764ad04ffb21cd24f1fc28e4d3c
```

It transparently records why R2 evidence was rejected, does not relabel either
interrupted R2 attempt, and measures a new actual R3 preflight. Frozen artifacts
match, all 15 review/acceptance/downstream paths are absent, and every required
check passes:

- focused contract: 123 passed;
- Ruff formatting: pass;
- Ruff lint: pass;
- local-only verifier: 25/25.

R3 terminal inventory exactly equals its fresh preflight:

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

## Master reproduction

The master began with a fresh `uv sync --locked --all-groups` (83 resolved, 82
audited), established a new post-sync baseline, and independently reproduced the
same 123 focused tests, Ruff checks, 25 local-only controls, frozen digests,
absent future paths, and identical terminal inventory.

`git remote` prints nothing. No provider access, network activity, cloud
resource, hosted CI, public endpoint, container, deployment, or Git mutation was
created.

The next authorized step is fresh independent field-authority review with
read-only candidate ownership. Formal acceptance remains blocked until a PASS
review is independently verified by the master.
