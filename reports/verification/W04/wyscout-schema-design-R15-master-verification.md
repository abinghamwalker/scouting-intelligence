# W04 Wyscout schema design R15 — master verification

## Decision

`ACCEPT` as the master candidate for independent review. The master read all
3,234 R15 design lines, the complete 110-line return, and the full 510-line
R14-to-R15 delta after a fresh locked all-groups sync. R15 closes all three
returned R14 findings without regressing the previously reproduced source,
rights, temporal, identity, product, environment, path, resource, gate,
ownership, two-root, and ledger controls. Implementation remains blocked pending
separate independent acceptance and master reproduction of that verdict.

## Integrity and scope

- R15 design: `179,095` bytes; SHA-256
  `bf448cfc8478515dab760d119f6b89509e576fc24cfc44e3de473202224ae73e`.
- R15 return: `5,733` bytes; SHA-256
  `c2bd432e57dbb4c84beb28b67b7af352175602e90291a406b0451a58354d0254`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Producer ownership remained limited to the two exact R15 report paths.
- The parent-workspace report hierarchy is absent.
- The future launcher, admission entry point, and rebuild entry point remain
  absent.

## Acyclic build identity

Mechanical parsing found exactly 25 unique keys in the stable pre-build
projection and exactly 25 unique keys in the post-hash rebuild invocation. The
sets share exactly 24 stable values. Their only differences are:

```text
projection only: schema_version
invocation only: build_id
```

Both lists are in Unicode code-point order. The launcher hashes only the closed
projection carrying
`schema_version="w04-wyscout-pre-build-projection-v1"`, then replaces that marker
with the resulting `build_id` when constructing the runtime invocation. The child
performs the inverse schema-bound reconstruction and compares the one recomputed
digest against every enclosing identity. Completed projection and invocation
instances are explicitly excluded from the stable process-contract component, so
the admitted code-manifest digest binds the algorithms without depending on its
own future instance. No placeholder, fixed point, runtime path, run ID, or second
build algorithm remains.

The chronology is now singular: admission result; immutable manifest
write/confirm; byte-for-byte readback; projection construction; one build-ID
SHA-256; post-hash invocation construction; run-bound path rendering; rebuild
prefix creation; envelope/environment construction; rebuild launch.

## Accepted dependency rows and lineage

The accepted `EvidenceDependency` model exposes exactly:

```text
kind
dependency_id
digest
observed_at
available_at
```

Canonical JSON validation reproduced those five wire fields, their canonical
serialized values, and `extra="forbid"` rejection of `manifest_id`. R15 uses the
same closed rows throughout, explicitly rejects `dependency_kind`,
`manifest_id`, and `manifest_sha256`, preserves one source-manifest row, one
identity-evidence row, three feature-schema rows, the declared canonical sort,
strict-before clocks, maximum watermark, and the lineage hash over the complete
ordered objects.

R15 truthfully identifies both R13 and R14 as master-returned `REWORK`
revisions. It retains only their passing, independently reproduced controls and
does not retroactively call either revision accepted.

## Retained closures

The full delta and complete document readback retain the exact 16 common, 8
admission, 10 rebuild, and 25 invocation input schemas; the acyclic outer and
child environment constructions; three exact locked/no-sync argv; descriptor,
race, frame, result-v2, diagnostic, and three-prefix ownership contracts; the
35-executable census; three interpreter aliases; three denied `.pth` classes;
the 58-pyc/19-cache repository observation with all three repository inert
orphans; the optional site-six predicate; 17 local resources; and the complete
two-root and two-local-commit gate.

## Checks

- Fresh `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited.
- Complete design/return/delta readback: PASS; 3,234/110/510 lines.
- Projection/invocation mapping: PASS; 25/25 unique keys, 24 common, exact
  `schema_version`/`build_id` substitution.
- Accepted dependency model in canonical JSON mode: PASS; exact five fields and
  forbidden extra alias.
- Child input table cardinalities: PASS; 16/8/10/25.
- Stale-cycle, alias, version, and lineage search: PASS; old or alias terms occur
  only in explicit retirement/forbidden tests.
- Orchestration YAML: PASS; 133 documents, 23 registry tasks, zero duplicate
  registry task IDs.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition, provider/network access, product implementation, cloud
resource, hosted CI, public endpoint, Git remote, container, or deployment was
created.
