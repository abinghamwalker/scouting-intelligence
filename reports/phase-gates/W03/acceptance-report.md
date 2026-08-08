# G-W03 acceptance report

Decision: **ACCEPT for local checkpoint**

The contract-first synthetic spine satisfies W03.1–W03.6 and the reviewed W03
contribution to blueprint gate G1.

## Work-item closure

- **W03.1 — strict foundation contracts:** canonical IDs, UTC-only instants, tenant,
  temporal evidence, source manifest, dependency lineage, audit, role-brief,
  retrieval, shortlist, workflow, and strict JSON boundaries are implemented and
  covered by contract and tamper tests.
- **W03.2 — guarded local persistence:** bounded roots, atomic writes, immutable
  manifests, content digests, JSON/JSONL/Parquet helpers, replay behavior, traversal
  rejection, and symlink escape denial pass.
- **W03.3 — database and first migration:** PostgreSQL/pgvector migration, constraints,
  application role, tenant-local RLS, append-only audit, migration replay, and
  application transaction identity pass against the approved loopback service.
- **W03.4 — deterministic synthetic domain:** development and master-only protected
  partitions are frozen separately. Late availability, cutoff-equality observation,
  missing temporal evidence, ambiguous identity, and prohibited future facts fail
  closed.
- **W03.5 — local vertical journey:** authenticated role brief → retrieval →
  explanation → shortlist entry → append-only audit runs through one serving and
  workflow path. Persisted-object conflicts admit only exact canonical replay;
  role-brief, retrieval, shortlist, and entry mismatches deny generically and roll
  back all material/audit effects.
- **W03.6 — independent boundary audit:** R1 reproduced a P1 same-tenant ownership
  collision and returned the work. R6 corrected every silent material conflict.
  Independent R2 then passed 17 original and additive adversarial checks and
  recommended acceptance.

## Gate result

The master independently reproduced:

- a fresh locked sync and lock check;
- 185 repository tests, including contracts, migration/RLS, authorization, storage,
  telemetry, E2E, and independent boundary checks;
- Ruff, strict mypy, Bandit, governance validation, and three import-linter contracts;
- exact master-only protected result and explanation digests with repeat stability;
- active local push guards, Python 3.12, one root uv project, and zero Git remotes;
- healthy loopback-only PostgreSQL/pgvector and Redis services;
- local secret, dependency-licence, and cached-container evidence.

No unresolved P0–P2 defect remains. The upstream TestClient deprecation warning is
disclosed and does not affect a W03 boundary.

## Boundary confirmation

`git remote` prints nothing. No cloud resource, hosted CI, remote repository, public
endpoint, external telemetry/model call, public image, or deployment was created. The
two controlling HTML files remain outside the project repository and unchanged.

## Checkpoint

- Commit: `phase(w03): accept contract first synthetic slice`
- Accepted annotated local tag: `checkpoint/w03-accepted`

