# W04 Wyscout schema design independent review R9 — master verification

## Decision

`REWORK`. The master read the complete 726-line independent review and its
131-line return, began reproduction with a fresh
`uv sync --locked --all-groups`, and confirmed the one P1 finding. R15 cannot
start implementation because its closed outer and child maps require a physical
`UV` spelling that normal resolution of the mandated literal `uv` token does not
produce.

The correction is bounded to standalone R16. It requires no architecture,
provider, rights, dependency, lock, storage-root, network, container, Git,
deployment, or local-only change.

## Integrity and scope

- Independent review: `30,087` bytes; SHA-256
  `b288aee09612e7a7e1c793a319914db05f83a6bb1daa5dbaf15a685c16f49dc5`.
- Final return: `6,828` bytes; SHA-256
  `21d09611877b82cc1b4c26315f9c80638655394c61d4a57f6f33f2fd8fbc5b4a`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Reviewer ownership remained limited to the independent R9 review and return.
- The three future launcher/admission/rebuild scripts remain absent.
- No parent-workspace report hierarchy exists.

## P1 reproduced — normal uv resolution uses the logical launch path

The master constructed a read-only closed minimal uv input map with the exact
design `PATH`, recursion depth `0`, project `VIRTUAL_ENV`, offline cache, and
physical Cellar path supplied as the input `UV`. Normal command resolution of:

```text
uv run --locked --no-sync python -S -B -c <environment observation>
```

produced:

```json
{
  "PATH": "<project-root>/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
  "UV": "/opt/homebrew/bin/uv",
  "UV_RUN_RECURSION_DEPTH": "1",
  "VIRTUAL_ENV": "<project-root>/.venv"
}
```

Depth, venv prefix insertion, and the other values pass. The `UV` value does not:
R15 expects `/opt/homebrew/Cellar/uv/0.9.21/bin/uv`. Because the exact actual
map is compared and hashed, the mismatch blocks the outer verifier, bootstrap
tuple, both child maps, their envelopes, and transport equality before admission
can establish authority.

A separate low-level control kept visible `argv[0]="uv"` but selected the Cellar
binary as the operating-system executable target. That child received the
physical Cellar value. The result proves the distinction is controlled by launch
resolution and cannot be normalized away after the fact.

The current logical authority is exact:

```text
/opt/homebrew/bin/uv
  symlink mode: lrwxr-xr-x
  raw target: ../Cellar/uv/0.9.21/bin/uv
  raw target length: 26

/opt/homebrew/Cellar/uv/0.9.21/bin/uv
  regular mode: 0o555
  size: 41,617,552
  SHA-256: 4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f
  version: uv 0.9.21 (Homebrew 2025-12-30)
```

## Bounded R16 disposition

R16 must preserve normal PATH resolution and the exact visible argv. The outer
and both child maps will use actual `UV=/opt/homebrew/bin/uv` and a truthfully
named logical-launch token. Stable authority will separately bind the exact
logical symlink lstat/raw-link/one-hop resolution to the existing physical uv
mode, size, digest, and version. Direct physical execution, another logical path,
link drift, an extra hop, cycle, non-symlink, target escape, physical byte drift,
or accepting either spelling must fail.

The corrected actual value, normalized token, base digests, bootstrap tuple,
child envelopes, first/final comparisons, environment component, negative tests,
and two-root proof must change together. The acyclic construction and all other
R15 controls remain unchanged.

## Retained passing review evidence

The master read back the independent reproduction of all other required
challenges. R9 found no other P0-P2 defect in:

- the exact 25/25 projection/invocation schemas with 24 common fields and the
  schema-marker/build-ID substitution;
- the accepted five-field `EvidenceDependency` rows, enum order, strict clocks,
  watermark, and lineage;
- the 16/8/10/25 child schemas, descriptor and result-frame authority, unique
  chronology, and sole writers;
- locked all-groups `L == I`, Packaging bootstrap, three denied `.pth` classes,
  editable metadata, 35 executables/21 owners with 33/1/1 classes, three
  interpreter aliases, encoding sources, and source-complete pyc authority;
- 1,075 site pycs, 58 repository pycs in 19 caches, and all four optional orphan
  predicates;
- the 18 source evidence paths, 17 local resources, rights, strict envelope
  dispatch, exact Bronze/Silver/Gold paths and keys, separate six-dimensional
  source/Gold coverage, temporal and unknown handling, two-root proof, full gate,
  and two-local-commit ledger.

## Master checks

- Fresh locked sync: PASS; 83 packages resolved, 82 audited.
- Complete R9 review/return readback: PASS; 726/131 lines.
- Normal closed-map uv probe: reproduced logical `/opt/homebrew/bin/uv`.
- Physical-exec-target control: reproduced physical Cellar `UV`.
- Logical symlink and physical uv identity: PASS; exact link, mode, size, digest,
  and version.
- R9 packet artifact sizes: PASS; 30,087/6,828 bytes.
- Orchestration YAML after R16 issuance: PASS; 135 files, 23 task IDs, zero
  duplicates.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.
- Parent scope: PASS; no stray parent report hierarchy.

No provider access, cloud resource, hosted CI, public endpoint, remote,
container, or deployment was created.
