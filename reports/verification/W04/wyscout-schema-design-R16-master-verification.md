# W04 Wyscout schema design R16 — master verification

## Decision

`ACCEPT` as the corrected master candidate for independent review. The master
read all 3,322 R16 design lines, the complete 132-line return, and the full
537-line R15-to-R16 delta after a fresh locked all-groups sync. R16 truthfully
corrects the sole independent R9 P1: normal `PATH` resolution records
`UV=/opt/homebrew/bin/uv`, while an exact one-hop symlink proof binds that logical
launch spelling to the already admitted physical uv bytes. Implementation
remains blocked pending separate independent acceptance and master reproduction
of that verdict.

## Integrity and scope

- R16 design: `185,625` bytes; SHA-256
  `c36eaca5ed2d803ae495e26d24413f6a86baf60e7732f24770a2e9f59787386d`.
- R16 return: `6,844` bytes; SHA-256
  `a944a15338def800aa67aef22648f7aa2f78d35f4f1468ab13b98f15e57fdd16`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Producer ownership remained limited to the two exact R16 report paths.
- The parent-workspace report hierarchy is absent.
- The future launcher, admission entry point, and rebuild entry point remain
  absent.

## Logical launch and physical byte authority

The master independently reproduced all current-environment facts:

```text
normal command-v selection: /opt/homebrew/bin/uv
logical lstat type: symbolic link
raw target: ../Cellar/uv/0.9.21/bin/uv
raw target length: 26 bytes
one-hop target: /opt/homebrew/Cellar/uv/0.9.21/bin/uv
physical type/mode/size: regular file / 0o555 / 41,617,552
physical SHA-256:
4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f
version: uv 0.9.21 (Homebrew 2025-12-30)
```

The stable launch authority now binds the exact logical entry, raw relative
link, one contained hop, and exact final physical identity. Operational
device/inode/link-count/clock observations remain outside stable identity.
Normal execution must select the logical entry only. A missing or non-symlink
entry, raw-link drift, extra hop, escape, cycle, alternate logical path, direct
physical exec target, either-spelling policy, realpath-normalized `UV`, or final
byte/version/mode/size drift fails.

## Closed environment transforms

The master executed the visible literal `uv` under exact `env -i` input maps.
For the outer role, uv 0.9.21 produced exactly 29 names; for the admission-child
role it produced exactly 32. Both transforms:

- retained `UV=/opt/homebrew/bin/uv`;
- changed `UV_RUN_RECURSION_DEPTH` from `0` to `1`;
- prepended exactly one root `.venv/bin` component to `PATH`; and
- introduced, removed, or changed no other name or value.

The document consistently uses the sole normalized stable token
`<W04_UV_LOGICAL_LAUNCH_PATH>` across the outer and two child maps. The old
physical-path token is absent. The acyclic algorithm identifiers are exactly:

```text
w04-local-control-bootstrap-v3
w04-outer-environment-bootstrap-v2
w04-child-environment-input-v2
w04-code-environment-admission-v13
```

Their predecessor identifiers are absent.

## Retained exact schemas and identity

Mechanical parsing reproduced exact unique cardinalities:

```text
common child input: 16
admission inputs: 8
rebuild inputs: 10
rebuild invocation: 25
stable pre-build projection: 25
component proofs: 20
```

The projection and invocation remain code-point sorted, share exactly 24 stable
values, and differ only by projection `schema_version` versus invocation
`build_id`. The completed invocation does not enter its own preimage. The
five-field `EvidenceDependency` closure, five-row chronology, exact three argv
and roles, descriptor/result framing, independent `L == I`, 35 executables,
three aliases, three denied `.pth` classes, source-complete pyc rules, 17
resources, source/rights/temporal/identity/product authority, two-root proof,
gate, and two-commit ledger remain unchanged by the R16 delta.

## Checks

- Fresh `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited.
- Complete design/return/delta readback: PASS; 3,322/132/537 lines.
- Logical-to-physical uv proof: PASS; exact symlink, raw target, one hop, final
  mode/size/digest/version.
- Closed environment transforms: PASS; outer 29, child 32, exact logical `UV`,
  depth 1, one venv prefix, zero unknown names.
- Schema cardinalities: PASS; 16/8/10/25/25/20, with the projection/invocation
  24-key intersection and exact one-key substitution.
- Version/token consistency: PASS; only v3/v2/v2/v13 and the logical launch
  token remain.
- Orchestration/config YAML: PASS; 135 plus 5 documents, 23 registry tasks, zero
  duplicate registry task IDs.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition, provider/network access, product implementation, cloud
resource, hosted CI, public endpoint, Git remote, container, or deployment was
created.
