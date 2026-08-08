# W04 possession semantic v2 acceptance R1 — master verification

## Decision

`ACCEPT`. The master-owned canonical acceptance binds the corrected
possession-v2 decision/candidate, fresh independent PASS review, exact
possession-v1 supersession, UUIDv5 actors, and ordered clocks.

This acceptance lifts only the possession prerequisite for the serial
supported-feature authority. It does not authorize cross-authority composition,
Bronze, Silver, Gold, build, model, or product implementation.

## Canonical acceptance

```text
acceptance ID:
w04-wyscout-possession-semantic-acceptance-v2
schema:
w04-authority-acceptance-v1
accepted_at:
2026-07-31T08:28:40Z
accepted_by:
4efe5691-8903-5148-8275-30d2e7e8aed0
supersedes:
w04-wyscout-possession-semantic-acceptance-v1
bytes:
1,046
SHA-256:
2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1
```

The acceptance is strict compact canonical JSON with lexically sorted keys and
one terminal LF. It has exactly fifteen keys.

## Bound authority

```text
decision physical/canonical SHA-256:
8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425
candidate physical SHA-256:
24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187
candidate canonical SHA-256:
3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881
review physical SHA-256:
c1e249c377d11258415cea84e83f0d3742436ebcb7aa640b885c44d245cb1e97
review record SHA-256:
0b4c02b6caa0457ec181bb1949dfaf920b71a4173157506d477ed4038d5ec553
review recommendation:
PASS
review findings:
[]
```

Clock order is:

```text
decision 2026-07-30T22:14:21Z
<= review 2026-07-31T08:24:02Z
<= acceptance 2026-07-31T08:28:40Z
```

The reviewer is distinct from the master and both actors are canonical
UUIDv5. The exact accepted possession-v1 predecessor is named by
`supersedes_acceptance_id`.

## Master verification

```text
uv sync --locked --all-groups
PASS: 83 resolved, 82 audited

strict acceptance canonical/digest/progression reconstruction
PASS: ACCEPTED

focused field/possession authority suite
PASS: 332 passed

local-only verifier
PASS: 25/25

orchestration YAML parse
PASS

git diff --check
PASS

git remote
PASS: empty
```

The retained environment still contains 1,145 `.pyc` files and 150
`__pycache__` directories. No provider access, dependency/lock change, remote,
cloud resource, hosted CI, public endpoint, container, deployment, or product
path was created.

## Gate

The next permitted serial task is the R21 supported-feature decision/candidate
authority. Cross-authority testing and every product implementation remain
blocked until that authority is independently reviewed and accepted and the
complete R21 gate passes.
