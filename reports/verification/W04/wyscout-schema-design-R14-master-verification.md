# W04 Wyscout schema design R14 — master verification

## Decision

`REWORK`. The master read all 3,076 R14 design lines, the complete 100-line
return, and the full 800-line R13-to-R14 delta after a fresh locked all-groups
sync. R14 closes the three returned R13 design findings and its scope handback is
truthful. Two new P1 contradictions remain in the rebuild invocation contract,
and one P2 lineage statement incorrectly promotes the rejected R13 revision.
Independent review and implementation remain blocked.

## Integrity and scope

- R14 design: `169,853` bytes; SHA-256
  `4e1db637a92bd2e4208dc64541e23fbb506571f7d1057a904bcb420e86ae02ea`.
- R14 return: `5,222` bytes; SHA-256
  `9353a5860731a9997b16e91f7c500adda7823d6a319c113c6ada6e7ff34023ff`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Producer ownership remained limited to the two absolute R14 report paths.
- The mistaken parent-workspace `reports` hierarchy did not recur and is absent.
- The future launcher, admission entry point, and rebuild entry point remain absent.

## R13 findings now closed

The outer environment construction is acyclic: the exact normalized base map
excludes `W04_BOOTSTRAP_TUPLE_B64`, its digest enters the completed bootstrap
tuple, the tuple is encoded and inserted once, and a separate operational digest
covers the complete actual transport map. The master constructively reproduced
the asserted uv 0.9.21 transformation under the closed input map: recursion depth
became `1`, `UV` was the admitted physical path, and `PATH` gained exactly one
root-venv prefix without another environment mutation.

The child transport is now closed. Mechanical parsing confirmed exactly 16 common
input keys, 8 admission keys, 10 rebuild keys, and 25 rebuild-invocation keys.
`W04_CHILD_INPUT_B64` is the sole value-bearing channel, both eight-token child
argv remain unchanged, role/environment/envelope equalities are explicit, and the
manifest-readback/build-ID/rebuild-prefix sequence is chronological.

The R14 producer used exactly its two assigned paths. Its return distinguishes
prohibited Git-mutating operations from read-only Git checks made by the mandated
local-only verifier.

## P1 — build identity depends on an invocation containing itself

The closed `w04-rebuild-invocation-v1` object contains `build_id`, which must equal
the recomputed Section 9 digest. Section 9 then says canonical build input contains
the exact `w04-rebuild-invocation-v1` fields before defining:

```text
build_id = SHA256(canonical_json(all stable semantic build-input fields))
```

That makes `build_id` depend on an object containing `build_id`. It contradicts
the otherwise-correct chronology requiring the complete build ID before the
rebuild envelope is constructed. No deterministic construction can both include
the resulting digest as an input and avoid a placeholder/fixed-point search.

R15 must define an exact stable pre-build projection that excludes the computed
`build_id` and every operational run/path value. The launcher hashes that closed
projection once, then inserts the result into the runtime rebuild invocation.
Recomputation validates the projection after removing only the explicitly
computed field; the schema contract itself may be stable authority, but the
post-hash runtime instance must not be an input to its own digest.

## P1 — dependency rows contradict the accepted contract

The existing accepted `EvidenceDependency` fields are exactly:

```text
kind
dependency_id
digest
observed_at
available_at
```

R14 instead defines each supposedly complete dependency row as
`available_at`, `dependency_kind`, `manifest_id`, `manifest_sha256`, and
`observed_at`. Identity-evidence and feature-schema dependencies are not manifests,
and Section 5 itself sorts by `DependencyKind`, `dependency_id`, and `digest`.
The R14 row therefore cannot round-trip the accepted model or preserve the
declared canonical lineage.

R15 must use the exact five accepted field names and types, retain the exact
Section 5 cardinality/sort, and require byte-for-byte equality with the five
accepted `EvidenceDependency` records. Generic manifest aliases are forbidden.

## P2 — R13 was never accepted

R14 says it retains “accepted R13” and repeats that lineage at the end. The master
decision for R13 is `REWORK`. R14 may retain the passing R13 closures, but it
cannot label that revision accepted. R15 must state the exact master-returned
lineage while retaining the independently reproduced passing controls.

## Checks

- Fresh `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited.
- Full R14/return/delta readback: PASS.
- Exact closed uv transformation probe: PASS; 29 environment keys, depth `1`,
  admitted physical uv path, and one venv `PATH` prefix.
- Input table cardinalities: PASS; 16/8/10/25.
- Build-ID dependency graph: FAIL; rebuild invocation includes its resulting ID.
- Accepted `EvidenceDependency` model: PASS; exact five fields reproduced.
- R14 dependency row compatibility: FAIL; three field names disagree.
- Orchestration YAML: PASS; 129 documents, 23 registry tasks, zero duplicate
  registry task IDs.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider, network, cloud, hosted CI, public endpoint, remote, container, or
deployment was created.
