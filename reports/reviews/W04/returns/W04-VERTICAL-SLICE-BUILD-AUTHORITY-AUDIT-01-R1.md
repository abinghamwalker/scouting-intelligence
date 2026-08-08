# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-BUILD-AUTHORITY-AUDIT-01`
- objective: Identify the smallest exact R20 build-ID and receipt-content closure
  required before the bounded vertical slice may publish.

## Files changed

- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-BUILD-AUTHORITY-AUDIT-01-R1.md`

## Summary

### Verdict

**BLOCKED_SCOPE for any final/staged product, manifest, or receipt publication.**
**PASS_TO_PACKET for an in-memory checked raw-to-Gold proof that writes no product
or control bytes.** This is a bounded missing-authority/implementation gap, not an
R20/R21 contradiction and not grounds for an architecture revision.

### Executable inventory

R20 fixes one and only one build algorithm: canonicalize the exact 25-key
`w04-wyscout-pre-build-projection-v1` object, hash it once with SHA-256, copy its
24 non-`schema_version` values unchanged, and insert only `build_id` to form the
25-key `w04-rebuild-invocation-v1`. The existing repository has the following
prerequisites:

| R20 projection prerequisite | Current executable authority |
|---|---|
| `authority_rows` | **EXISTS**: `WyscoutAuthorityReference` plus `accepted_authority_references()` return the exact FIELD-v2, POSSESSION-v2, SUPPORTED_FEATURE-v1, IDENTITY-v1 rows. |
| `source_manifest_id`, `source_manifest_sha256` | **EXISTS**: strict constants and the matching immutable source-manifest bytes at `data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json`. |
| `tenant_id`, `tenant_club_id` | **EXISTS**: exact tenant constant and validated null club context. |
| `feature_schema_hash` | **EXISTS**: accepted canonical feature digest `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`. |
| `product_contract_digest`, `schema_bundle_digest` | **EXISTS**: exact immutable preimage bytes and constants `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293` and `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`. |
| `role_context_id`, `role_context_state`, `role_context_version` | **EXISTS**: exact neutral context constants and Gold validation. |
| five `dependency_rows`, `dependency_watermark` | **PARTIAL**: `EvidenceDependency`, feature/source IDs, strict clocks, sorting and lineage validation exist; the fifth row cannot be finalized because no accepted identity-bundle bytes/digest exist. |
| `identity_bundle_id`, `identity_bundle_sha256` | **ABSENT**: the accepted ruleset exists, but `src/scouting/identity/` is empty and `data/working/wyscout/v5/identity/bundles/` does not exist. A ruleset digest is expressly not a bundle digest. |
| `window_definition_id`, `window_start_utc`, `window_end_utc`, `feature_cutoff_ts` | **ABSENT AS INVOCATION AUTHORITY**: row/temporal contracts validate supplied values, but only test fixtures supply them; there is no accepted executable pre-build input assembler. |
| `code_manifest_id`, `code_manifest_sha256`, `environment_digest`, `selected_lock_closure_digest`, `local_resource_digest` | **ABSENT**: no admitted code-manifest path/bytes and no R20 admission constructor. The R21 30-resource roster exists, but no accepted stable per-row resource digest has been built. |
| `schema_version` and exact projection/invocation conversion | **DESIGN ONLY**: no `WyscoutPreBuildProjection`, `WyscoutRebuildInvocation`, canonical one-hash calculator, inverse reconstruction, or closed-key negative tests exist. |

Reusable downstream authority already exists in
`src/scouting/sources/wyscout_completion_index.py`: exact full-population checking,
checked Silver/Gold/manifest builders, and `require_checked_product`. These do not
grant build identity. Existing `WyscoutProductPath` validates the two receipt path
roles and exact serializer owners only.

There is **no accepted or executable content schema** for either
`RebuildInvocationReceipt` or `TemporalBoundaryReceipt`. R20 fixes their paths,
owners, operational/non-semantic status, run/build/path equalities and result
summary rows, but does not close the JSON content keys. The R21 schema bundle
expressly labels both as
`CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`. Therefore a producer
must not infer receipt content from the path regex, the six-key child result, or a
free-form mapping.

### Exact conformant boundary

An in-memory proof remains conformant when it:

1. uses the authentic checked completion capability and checked builders;
2. labels any 64-hex build token as test-only/non-authoritative;
3. writes no staged/final Parquet, product manifest, code manifest, receipt, or
   build-scoped path; and
4. makes no publication, rebuild, or deterministic-build claim.

The first nonconformant action is treating an arbitrary or fixture build token as
authority: concretely, rendering/creating the R20 build-scoped staging tree or
writing any product, layer manifest, invocation receipt, or boundary receipt
before the immutable v15 code manifest has been written/read back by the sole
launcher and the exact projection has been hashed once. Writing either receipt
with an invented content mapping is independently nonconformant.

### Smallest serial packet sequence

All packets are serial at their shared boundaries; none may write product bytes
until packet 6 and the separate exact-Parquet/publication gate pass.

1. **`W04-BUILD-RECEIPT-CONTRACT-01-R1` — master/shared contract closure**
   - sole paths: `src/scouting/contracts/wyscout_build.py`, the required export in
     `src/scouting/contracts/__init__.py`, and
     `tests/contracts/test_w04_wyscout_build_authority.py`;
   - implement the closed 25-key projection, 25-key invocation, one-hash and exact
     inverse reconstruction; close both receipt-content models without changing
     R20 paths/owners/operational boundary; fail on every extra/missing/reordered
     authority/dependency row, cutoff equality, wrong aggregate, pre-hash
     operational value, alternate hash, or receipt key;
   - because receipt keys are not presently accepted, the master must make and
     retain this bounded content decision before code review. This is the exact
     scope blocker; a producer cannot choose it.

2. **`W04-BUILD-RECEIPT-CONTRACT-REVIEW-01-R1` — independent review**
   - sole paths: one fixed review and return under `reports/reviews/W04/`;
   - read-only review of R20/R21 equality, acyclicity, canonical bytes and negative
     tests; recommendation must be `PASS` before packet 3.

3. **`W04-IDENTITY-BUNDLE-RUNTIME-01-R1` — identity owner**
   - sole paths: `src/scouting/identity/wyscout.py`, focused tests, and only the
     R20 identity runtime families when invoked;
   - produce/reopen one exact content-addressed bundle and derive its UUIDv5
     dependency; do not substitute the ruleset candidate.

4. **`W04-RUNTIME-ADMISSION-01-R1` — admission owner**
   - sole paths: `scripts/admit_wyscout_v5_runtime.py` and focused tests;
   - construct/return, but never publish or hash into a build prematurely, exact
     `w04-code-environment-admission-v15` bytes including the R21 30-resource
     stable digest, selected lock closure and environment digest.

5. **`W04-LOCAL-CONTROL-LAUNCHER-01-R1` — sole launcher/build calculator**
   - sole paths: `scripts/launch_wyscout_v5.py` and focused tests;
   - publish/reopen the immutable code manifest, assemble all exact projection
     inputs including accepted window/cutoff values, perform the sole SHA-256,
     construct the post-hash invocation and only then render rebuild paths.

6. **`W04-REBUILD-RECEIPTS-01-R1` — rebuild/temporal owners after accepted
   serializers**
   - sole paths: `scripts/rebuild_wyscout_v5.py`,
     `src/scouting/data_products/rebuild.py`,
     `src/scouting/data_products/temporal_boundary.py`, and focused tests;
   - reconstruct/recheck the projection, invoke named serializers, and write only
     the two now-closed receipt contents at their exact paths. Product publication
     still additionally depends on the separate R20-exact Parquet and sidecar-free
     guarded publisher correction identified by the contract audit.

7. **`W04-BUILD-PUBLICATION-INDEPENDENT-REVIEW-01-R1` — independent reviewer**
   - sole paths: fixed review and return; reproduce both rebuilds, equal build ID,
     receipt/path bindings, exact manifest/product digests, and all fail-closed
     cases before master acceptance/full repository gate.

Packets 3 and the in-memory product proof can be implemented on path-disjoint
branches of work, but packets 1→2→4→5→6 are authority-serial. More agents cannot
safely parallelize that chain; they can independently review or build the
non-publishing row projection while it progresses.

## Tests run

- complete reads of every `read_first` path: exit `0`; R20/R21 and both preimages
  inspected, with focused line readback of the build, child-input/result, path,
  receipt, resource and publication clauses.
- locked/no-sync uv contract introspection:
  - command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <authority introspection>`
  - exit status: `0`
  - result: six checked builders exist; receipt/build/projection contract symbol
    lists are empty; exact accepted constants and four authority rows reproduced.
- exact absent-surface scan:
  - command: bounded `test`/`find` checks plus `rg` for the four required models
    and two build functions
  - exit status: `0` for the scan; symbol search exit `1` (no matches, expected)
  - result: all three fixed scripts, code-manifest directory, identity-bundle
    directory and receipt/build symbols are absent.
- immutable-byte digest check:
  - command: `shasum -a 256` over source manifest and product/schema preimages
  - exit status: `0`
  - result: exact digests `8fb6...9bd`, `0003...293`, and `a37b...16f` match
    executable constants.

## Artifacts/evidence

- audit: `reports/reviews/W04/returns/W04-VERTICAL-SLICE-BUILD-AUTHORITY-AUDIT-01-R1.md`
- controlling build algorithm: `reports/reviews/W04/wyscout-schema-design-R20.md:3839`
- receipt path-only implementation: `src/scouting/contracts/wyscout_data.py:2842`
- descriptor-only proof: `configs/schema/wyscout-v5-schema-bundle-preimage-v1.json`

## Risks

- P1: any fixture/arbitrary build ID permits false deterministic-publication claims.
- P1: inventing either receipt mapping creates bytes with no accepted content
  authority.
- P1: ruleset digest substitution for the absent identity bundle breaks the fifth
  dependency and build preimage.
- P1: current generic Parquet and guarded sidecar behavior remains separately
  incompatible with R20 final publication.

## Follow-up items

- Master must issue packet 1 with an explicit bounded receipt-content decision;
  until independent review passes, continue only the non-publishing in-memory
  proof and identity-bundle work.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
