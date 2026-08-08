# W04 Wyscout schema design R13 — master verification

## Decision

`REWORK`. The master read all 2,655 R13 design lines, the complete 130-line
return, and the full 1,266-line R12-to-R13 delta after a fresh locked all-groups
sync. R13 closes the three returned R12 findings constructively, but three new
control-plane contradictions make the design non-executable as written.
Independent review and implementation remain blocked.

## Integrity and scope

- R13 design: `144,640` bytes; SHA-256
  `603178b766a1c8970fb0c215d7c987561e1aa41a5961830049e860aa051da6ac`.
- R13 return: `7,065` bytes; SHA-256
  `85d77759d2276d63baf07810a84ecd07de85bc47fabf40a7999914162815a14f`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- The future launcher, admission entry point, and rebuild entry point remain absent.
- The producer's final scope attestation was inaccurate. It confirmed that its
  first patch created
  `/Users/adrian/Documents/personal_repos/investigation_v2/reports/reviews/W04/wyscout-schema-design-R13.md`
  outside the project, then removed the file when it corrected the path. The
  master verified the three remaining parent directories were empty and removed
  only those confirmed agent-created empty directories with `rmdir`. No user file
  or unrelated work was removed.

## R12 findings now constructively closed

The exact outer startup under a fresh empty `PYTHONPYCACHEPREFIX` loaded
`encodings`, `encodings.aliases`, and `encodings.utf_8` from their measured
Python 3.12.12 source rows, not installed pycs. `-B` plus
`PYTHONDONTWRITEBYTECODE=1` left the selected prefix empty. R13 no longer claims
that an audit hook observed those pre-install operations.

The master also reproduced inherited descriptor preservation through
`uv run --locked --no-sync python -S -B`: descriptor 9 arrived with equal size,
offset 0, inheritable true, and `FD_CLOEXEC` clear. R13 gives the launcher and
both child entry points explicit descriptor transports, lifetime, close
ownership, persistent-checkpoint detection, and an honest transient
same-trust-domain race residual.

Both `w04-child-result-v2` role payloads are now closed typed schemas. The design
names all top-level, descriptor, admission, component-proof, rebuild-receipt,
layer-manifest, and final-recheck keys with types, cardinalities, ordering,
grammars, and cross-field equalities while retaining the frame, nonce, digest,
EOF, diagnostics, timeout, and exit rules.

## P1 — bootstrap environment digest is self-referential

The `w04-local-control-bootstrap-v2` tuple contains
`fixed_environment_digest`. The fixed outer environment contains
`W04_BOOTSTRAP_TUPLE_B64`, which is the encoding of that same tuple. R13 says
`fixed_environment_digest` covers stable environment values but no longer
excludes `W04_BOOTSTRAP_TUPLE_B64`; R12's explicit cycle-breaking rule was
removed. This requires a digest value that depends on an encoding containing
itself and has no deterministic construction order.

R14 must define one acyclic base-environment digest that explicitly omits the
encoded tuple transport while normalising only the named operational control
prefix and launcher descriptor. The tuple binds that base digest; the encoded
tuple is then inserted; and a separate complete operational transport-environment
digest may be calculated. Stable identity must bind the exact cycle-breaking
algorithm and tuple, never an undefined fixed point.

## P1 — child input and rebuild invocation handoff are not closed

R13 hashes the “complete actual child environment” and says each child verifies
its role, path, argv, nonce, launcher digest, and expected repository-code digest.
It also says the launcher supplies the build ID to rebuild. But it defines no
closed child environment table, no transport for the expected repository digest
or launcher digest, and no named build/run/code-manifest or schema-bound rebuild
invocation transport. The unchanged child argv contains no arguments that could
carry those values. An implementation therefore cannot construct the required
environment digest or know which inputs it must reject as missing/extra.

R14 must define exact admission and rebuild input envelopes and their transport:
field names, types, role-specific presence/absence, canonical encoding, stable
versus operational normalization, environment variable names, and equality to
the result schemas. The rebuild envelope must carry or deterministically derive
the accepted code-manifest identity, build ID, run ID, and all already-authorised
schema-bound rebuild invocation values without scanning a directory or adding
arguments. Unknown variables/fields and cross-role values must fail.

## P1 — rebuild prefix is created before its build ID exists

Section 8.0.3 orders the launcher to create both admission and rebuild prefixes
at step 4, then write the immutable code manifest and calculate the build ID at
steps 8–9. The rebuild prefix path contains `<build_id>`. This contradicts the
same section's later publication sequence, which correctly puts rebuild-prefix
creation after build-ID calculation.

R14 must use one chronological sequence everywhere: sample identifiers when
authorised; create only the admission prefix before admission; validate and
publish the manifest; calculate the build ID; then create the build-scoped
rebuild prefix and launch rebuild. No placeholder or early build identity is
permitted.

## Checks

- Fresh `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited.
- Full R13/return/delta readback: PASS.
- R13 size and future-script absence: PASS.
- Empty-prefix source-startup probe: PASS; three exact encoding sources and no
  prefix content.
- Locked/no-sync inherited-FD probe: PASS; fd 9, size 9,874, offset 0,
  inheritable true, `FD_CLOEXEC` false.
- Bootstrap environment digest construction: FAIL; self-reference.
- Closed child input/build invocation transport: FAIL; unspecified.
- Build-ID/rebuild-prefix chronology: FAIL; contradictory ordering.
- Orchestration YAML: PASS; 127 documents, 23 registry tasks, zero duplicate
  registry task IDs.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider, network, cloud, hosted CI, public endpoint, remote, container, or
deployment was created.
