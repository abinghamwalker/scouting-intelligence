# W04 field-semantic acceptance R1 — master verification

## Decision

`REWORK`. The first master-owned acceptance rendering failed its own strict
contract before any downstream work.

All IDs, digests, actors, and clock ordering were correct, but the physical JSON
was not canonical: `review_record_sha256` appeared before
`review_recommendation`. Lexicographic canonical order requires
`review_recommendation` first.

The focused suite failed exactly one actual-state test:

```text
1 failed, 122 passed
ValueError: noncanonical JSON
```

The invalid R1 physical bytes were 980 bytes with SHA-256:

```text
22530f7afdf964902b085eb4befd384ab566e6b8fab87e0a125b4c38cc61dae5
```

No return was created and no downstream path exists. R2 resamples the master
clock, changes only the acceptance bytes and its new return, and must pass the
full acceptance-present suite from an identical bytecode baseline.

No provider access, network activity, cloud resource, hosted CI, public endpoint,
container, deployment, Git remote, or Git mutation was created.
