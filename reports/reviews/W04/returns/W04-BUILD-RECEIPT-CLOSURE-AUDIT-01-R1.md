# Subagent return

## Task

- task_id: `W04-BUILD-RECEIPT-CLOSURE-AUDIT-01`
- objective: Audit the exact remaining R20 build-identity, code/environment,
  invocation, temporal-boundary, and rebuild-receipt gaps and return the shortest
  safe serial closure chain without implementing or writing data.

## Files changed

- `reports/reviews/W04/returns/W04-BUILD-RECEIPT-CLOSURE-AUDIT-01-R1.md`

## Summary

### Verdict

**USER_CLARIFICATION_REQUIRED.** The clarification is a bounded product/build
authority decision. It is **not** an architecture, provider, rights, project-root,
dependency, storage, local-only, cloud, container, endpoint, hosted-CI, deployment,
or Git decision.

R20 already fixes the exact acyclic 25-key pre-build projection, the exact 25-key
post-hash invocation, and the one-SHA-256 build algorithm. Those surfaces are
ready for a normal implementation packet. The stop is narrower and evidenced:

1. R21 explicitly fixes both receipt entries as
   `CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`. There is no accepted
   receipt-content key set, nullability, ordering, clock schema, path-hash
   preimage, or canonical file encoding.
2. The accepted R21 product-contract preimage is expressly `control_plane_only`,
   has `product_bytes_forbidden=true`, and says it is not permission to create
   output bytes. The accepted schema-bundle preimage expressly does not bind
   implemented receipt schemas. R20 nevertheless requires
   `product_contract_digest` and `schema_bundle_digest` in the build projection to
   bind the exact receipts and every implemented receipt schema. Treating the v1
   preimages as that authority would contradict their bytes.
3. No accepted exact POC window authority exists. R20 specifies only the field
   types. It does not fix the UUID namespace/preimage, window start/end, cutoff,
   or semantic `snapshot_as_of_ts` derivation. The only concrete repository
   values are test fixtures. Their 2018 window excludes the authentic selected
   match, whose start is `2017-08-11T18:45:00Z`.
4. The later accepted completion-index digest
   `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
   is now mandatory in row, temporal, dependency-lineage, manifest, and Gold
   provenance. It occurs in executable contracts but in neither accepted R21
   preimage and in no explicit field of R20's fixed 25-key projection. The current
   `dependency_lineage_hash` is also not a projection field. A build using the v1
   aggregate digests therefore would not explicitly commit the post-R21
   completion-index authority.

These are executable contradictions at the publication boundary, not a reason to
change architecture. The minimal resolution is an additive, reviewed build/product
authority that preserves every R20/R21 byte, keeps the 25-key projection unchanged,
and supplies replacement aggregate values for the existing
`product_contract_digest` and `schema_bundle_digest` fields. A producer or master
cannot claim those product choices were already accepted.

### Exact R20 build and invocation reconciliation

The projection has exactly these keys in Unicode code-point order:

```text
authority_rows
code_manifest_id
code_manifest_sha256
dependency_rows
dependency_watermark
environment_digest
feature_cutoff_ts
feature_schema_hash
identity_bundle_id
identity_bundle_sha256
local_resource_digest
product_contract_digest
role_context_id
role_context_state
role_context_version
schema_bundle_digest
schema_version
selected_lock_closure_digest
source_manifest_id
source_manifest_sha256
tenant_club_id
tenant_id
window_definition_id
window_end_utc
window_start_utc
```

The projection-only field is
`schema_version="w04-wyscout-pre-build-projection-v1"`. Canonical bytes use
R20 Section 8.0.6: strict UTF-8, NFC strings, code-point-sorted object keys,
declared array order, no insignificant whitespace, strict integer grammar, and no
unknown/duplicate key. The sole build calculation is:

```text
build_id = SHA256(canonical_json(exact_projection))
```

The post-hash invocation copies the other 24 values without normalization,
removes only projection `schema_version`, and inserts only `build_id`. Rebuild
performs the inverse operation and the same single SHA-256. Run IDs, receipt and
layer paths, descriptors, nonces, output hashes, host values, transport hashes,
and clocks are post-hash operational values and cannot enter the projection.

| Projection value | Exact present authority | Executable state | Classification |
|---|---|---|---|
| `authority_rows` | Four accepted rows in exact `FIELD, POSSESSION, SUPPORTED_FEATURE, IDENTITY` order; `accepted_authority_references()` enforces all IDs/digests | present | already fixed and implementable |
| source ID/digest | `4e16bdb5-afe7-5601-88ad-adc124cfce3b` / `8fb6eb54...fd89bd`; immutable file digest reproduced | present | already fixed and implementable |
| tenant | `65a43912-d412-5ff9-a364-7f84d1ad6c5d`, club `null` | present | already fixed and implementable |
| feature schema | `49065bcf...ea10f` | present | already fixed and implementable |
| role context | UUIDv5 constant, `neutral_unscoped`, `w04-neutral-role-context-v1` | present | already fixed and implementable |
| product/schema v1 digests | `0003daf8...c6293` / `a37b426e...d916f`; bytes reproduced | present but descriptor-only/no-product | genuine bounded product decision before publication |
| identity bundle | exact source-complete builder/reader code now exists; no accepted materialized bundle bytes or bundle path exists | implementation in flight | bounded implementation plus fresh review |
| five dependencies | source and three feature rows executable; identity row becomes exact only after accepted bundle digest | partial | already specified; serially implementable after identity |
| dependency watermark | strict maximum of the five `available_at` clocks; all decision/review/acceptance clocks strictly before cutoff | derivable after identity and cutoff | implementable after product time decision |
| window/cutoff | only strict types and inequalities are fixed; concrete repository values are test fixtures | absent authority | genuine bounded product decision |
| code manifest ID/path | UUIDv5 of dependency namespace and `post_integration_code_environment_manifest:<sha>`; content-addressed path fixed | no accepted bytes | implementable after admission |
| environment/lock/resource digests | v15 20-component environment object, all-groups `L`, and R21 30-resource roster specified | no constructor/accepted bytes | bounded serialization and implementation |

### Exact missing executable surfaces

The following are absent:

- `src/scouting/contracts/wyscout_build.py` and any projection, invocation, or
  receipt content models;
- `scripts/launch_wyscout_v5.py`;
- `scripts/admit_wyscout_v5_runtime.py`;
- `scripts/rebuild_wyscout_v5.py`;
- `src/scouting/data_products/rebuild.py`;
- `src/scouting/data_products/temporal_boundary.py`;
- `data/manifests/wyscout/v5/code/`;
- `data/working/wyscout/v5/identity/bundles/`; and
- `runs/w04/wyscout-rebuild/`.

The R20 rebuild result is nevertheless already closed. Its six keys are
`build_id`, `final_recheck`, `layer_manifests`,
`rebuild_prefix_relative_path`, `rebuild_receipt`, and `run_id`.
`rebuild_receipt` is only a three-key **summary** (`relative_path`, `sha256`,
`size_bytes`); it is not the receipt content schema. The three layer rows and the
17-key final recheck are likewise result-channel schemas, not receipt authority.

The v15 code/environment design fixes the exact 20 environment-component keys and
component-proof order. It does not provide an executable constructor. Two remaining
byte-level decisions are safe for the master to freeze in implementation packets,
without user product input:

- the closed top-level code-manifest wrapper around `schema_version`,
  `repository_code_sha256`, `environment_digest`, and the exact 20-key component
  object; and
- the exact repository-code allowlist/row encoding used to calculate
  `repository_code_sha256` after the master declares code freeze.

Those decisions attest implementation bytes; they do not change product meaning.

### Named but underived product tokens

The following cannot be selected from R20/R21 without a retained product decision:

- the `window_definition_id` UUID namespace and UUIDv5 name/preimage;
- exact `window_start_utc`, `window_end_utc`, and `feature_cutoff_ts`;
- exact `snapshot_as_of_ts` and therefore the deterministic temporal-proof input
  (only `valid_from_ts=max(snapshot_as_of_ts,dependency_watermark)` is fixed);
- receipt schema IDs/versions and complete key sets;
- receipt operational clock names and ordering predicates;
- the direct byte preimage for
  `<sha256-of-exact-gold-relative-path>`;
- whether and how boundary-receipt summaries are committed by the invocation
  receipt; and
- aggregate contract bytes that bind the accepted completion-index digest and
  actual receipt schemas while superseding, not rewriting, the descriptor-only v1
  aggregates.

### Smallest recommended product decision

The smallest user decision is to authorize the master to freeze this bounded
additive POC authority (or to provide different product values):

1. **One-match window**

   ```text
   window_schema_version = w04-single-match-poc-window-v1
   window_start_utc = 2017-08-11T00:00:00Z
   window_end_utc = 2017-08-12T00:00:00Z
   feature_cutoff_ts = 2026-08-01T00:00:00Z
   snapshot_as_of_ts = SOURCE_ACQUIRED_AT
   valid_from_ts = max(snapshot_as_of_ts, dependency_watermark)
   ```

   The fixed namespace would be
   `UUIDv5(NAMESPACE_URL,
   "urn:scouting-intelligence:w04:wyscout:window-definition:v1")`.
   The UUIDv5 name would be `"single-match-poc:" + SHA256(R20-canonical JSON)` of
   the closed object containing `window_schema_version`, accepted source-manifest
   ID, canonical match ID `bad97950-6fac-5cf0-a93c-094f91abbb9b`, and the two
   window bounds. The cutoff remains a separate projection field.

2. **Completion-index binding**

   The additive product aggregate must contain the exact accepted index digest,
   source-manifest ID, source-member digest, match `2499719`, exact period counts
   `901/867`, and the accepted content-addressed index ID/digest. No Boolean,
   caller count, or population-only witness substitutes for it.

3. **Acyclic receipt publication order**

   ```text
   product Parquet -> layer manifest -> temporal-boundary receipt(s)
     -> rebuild invocation receipt -> child result summary
   ```

   No receipt contains its own digest. The child result hashes the already closed
   invocation receipt. Products/manifests do not reference a later receipt.

4. **Minimal invocation-receipt content**

   Exact keys, in canonical object order:

   ```text
   boundary_receipts
   build_id
   completed_at
   layer_manifests
   rebuild_invocation
   result_state
   run_id
   schema_version
   started_at
   ```

   `schema_version` is
   `w04-wyscout-rebuild-invocation-receipt-v1`; `result_state` is exactly
   `COMPLETE`; the invocation is the exact 25-key post-hash object; layer rows are
   the exact R20 three ordered five-key summaries; boundary summaries are sorted
   uniquely by Gold relative path and contain exactly `gold_relative_path`,
   `relative_path`, `sha256`, and `size_bytes`; clocks are canonical UTC and
   `started_at <= completed_at`. The file is R20-canonical JSON plus one terminal
   LF. Its own path/digest/size are excluded from its content and supplied only by
   the enclosing build/run path and later child-result summary.

5. **Minimal temporal-boundary receipt content for this one-row POC**

   Exact keys, in canonical object order:

   ```text
   build_id
   checked_at
   dependency_lineage_hash
   feature_cutoff_ts
   gold_manifest_relative_path
   gold_manifest_sha256
   gold_product_physical_sha256
   gold_product_relative_path
   gold_product_semantic_sha256
   gold_relative_path_sha256
   row_count
   run_id
   schema_version
   temporal_proof_sha256
   verification_state
   ```

   `schema_version` is `w04-wyscout-temporal-boundary-receipt-v1`;
   `verification_state` is `STRICT_BEFORE_CUTOFF_PASS`; `row_count` is exactly
   `1`; every build/run/path/digest equals the accepted Gold product and manifest;
   `gold_relative_path_sha256` is direct SHA-256 of the strict UTF-8 NFC Gold
   relative-path bytes and equals the boundary filename; `temporal_proof_sha256`
   covers the exact canonical temporal-proof object; `checked_at` is operational
   and is excluded from build/product semantics. The file is R20-canonical JSON
   plus one terminal LF and excludes its own digest/path.

6. **Superseding aggregates without changing the 25-key shape**

   Preserve both existing preimages and constants as historical inputs. Create
   reviewed v2 aggregate values in the build-contract implementation that bind the
   v1 digests, the accepted completion index, the exact POC window/snapshot rule,
   the two exact receipt schemas, and the post-gate product-authorized state. Use
   those v2 aggregate digests in the existing
   `product_contract_digest`/`schema_bundle_digest` projection fields. Do not add a
   26th key and do not relabel the descriptor-only v1 bytes as implemented schema
   authority.

The recommended values are conservative and limited to the already selected
one-match/one-player/four-feature proof. Authorizing them would not broaden source
coverage or product scope.

### Shortest serial packet chain after clarification

1. **`W04-BUILD-PRODUCT-AUTHORITY-01-R1` — master decision**
   - Sole ownership: one new fixed authority report/return and exact packet/test
     declarations; no runtime/product bytes.
   - Freeze the window/snapshot, v2 aggregate preimages, index binding, both
     receipt schemas, path-hash preimage, and acyclic publication order above.
   - Preserve all R20/R21/v1/index bytes.

2. **`W04-BUILD-PRODUCT-AUTHORITY-REVIEW-01-R1` — independent review**
   - Sole ownership: one fixed review and return.
   - Reproduce aggregate digests and reject self/sibling cycles, missing index,
     descriptor substitution, fixture window, receipt self-hash, cutoff equality,
     or a 26th projection key.

3. **`W04-BUILD-CONTRACTS-01-R1` — shared-contract producer**
   - Sole code paths: `src/scouting/contracts/wyscout_build.py`, named exports,
     and `tests/contracts/test_w04_wyscout_build_authority.py`.
   - Implement exact projection/invocation inverse, one-hash calculator, both
     receipt models, window authority, and v2 aggregate calculators. Do not write
     runtime/product bytes.

4. **`W04-BUILD-CONTRACTS-REVIEW-01-R1` — independent review**
   - Review only; prove closed keys, strict types, exact row order, index binding,
     canonical bytes, acyclicity, and adversarial rejection.

5. **`W04-IDENTITY-BUNDLE-RUNTIME-01-R1` acceptance completion**
   - Finish fresh independent review and master acceptance of the already in-flight
     source-complete bundle. This can proceed before steps 3–4, but build assembly
     waits for its accepted digest.

6. **`W04-RUNTIME-ADMISSION-01-R1` — admission producer**
   - Sole paths: `scripts/admit_wyscout_v5_runtime.py`, dedicated admission module
     if packeted, and focused tests.
   - Construct/return the exact v15 canonical code manifest and 20 component
     proofs; write no manifest and calculate no build ID.

7. **`W04-LOCAL-CONTROL-LAUNCHER-01-R1` — sole launcher/calculator**
   - Sole paths: `scripts/launch_wyscout_v5.py` and focused tests.
   - Write/reopen the immutable code manifest, assemble accepted invocation
     values, perform the sole build hash, and only then render rebuild paths.

8. **`W04-REBUILD-AND-BOUNDARY-RECEIPTS-01-R1` — named receipt owners**
   - Disjoint serial ownership for `rebuild.py` and `temporal_boundary.py` modules,
     `scripts/rebuild_wyscout_v5.py`, and focused tests.
   - Execute only after the exact product serializers, sidecar-free publisher, and
     layer manifests are independently accepted.

9. **`W04-BUILD-PUBLICATION-INDEPENDENT-REVIEW-01-R1` then master gate**
   - Reproduce two local rebuilds, equal build/projection/product semantics and
     physical bytes, permitted operational receipt differences, all fail-closed
     cases, complete repository gate, empty remote, and local-only proof.

Packets 1–4 are the critical serial authority chain. More producer agents cannot
safely bypass it. Identity and non-publishing row/encoder work may proceed in
parallel because their path scopes and authority do not choose receipt/window
semantics.

## Tests run

- command: complete `sed` reads of `AGENTS.md`, the packet, both predecessor
  audits, all 4,516 R20 lines, all 1,254 R21 lines, all 3,256
  `wyscout_data.py` lines, all 391 `guarded.py` lines, all 619 `formats.py`
  lines, and the return template
  - exit status: `0`
  - result: every `read_first` path read completely; no Python helper/import used.
- command: `shasum -a 256` over R20, R21, both v1 preimages, and the immutable
  source manifest
  - exit status: `0`
  - result: exact digests `8cb2...78047`, `faff...7020`, `0003...c6293`,
    `a37b...d916f`, and `8fb6...fd89bd` reproduced.
- command: bounded `rg` scan for projection/invocation/receipt classes and build
  calculators in `src`, `scripts`, and `tests`
  - exit status: `1` for absent required symbols, expected
  - result: only `ArtifactReceipt` exists; there is no W04 build/receipt content
    model or calculator.
- command: bounded path existence scan for the three runtime scripts, build
  contract/product modules, code-manifest root, identity-bundle root, and rebuild
  receipt root
  - exit status: `0`
  - result: all listed runtime/build/receipt surfaces and generated roots are
    absent; the in-flight identity implementation module exists but no bundle
    bytes do.
- command: exact scans for `window_definition_id`, window/cutoff values, authentic
  match start, and completion-index digest binding
  - exit status: `0`
  - result: concrete window values occur only as test fixtures; the fixture window
    is 2018 while the authentic match start is 2017-08-11; the accepted index
    digest occurs in executable contracts but not either v1 aggregate preimage.

## Artifacts/evidence

- this audit:
  `reports/reviews/W04/returns/W04-BUILD-RECEIPT-CLOSURE-AUDIT-01-R1.md`
- exact one-hash build authority:
  `reports/reviews/W04/wyscout-schema-design-R20.md:3839`
- exact 25-key invocation:
  `reports/reviews/W04/wyscout-schema-design-R20.md:2524`
- result summary versus missing receipt content:
  `reports/reviews/W04/wyscout-schema-design-R20.md:2734`
- descriptor-only schema evidence:
  `reports/reviews/W04/wyscout-schema-design-R21.md:692`
- control-only/no-product preimage evidence:
  `reports/reviews/W04/wyscout-schema-design-R21.md:674`
- path-only executable receipt authority:
  `src/scouting/contracts/wyscout_data.py:2924`
- completion-index executable binding:
  `src/scouting/contracts/wyscout_data.py:35`
- test-only window values:
  `tests/contracts/test_wyscout_data_contracts.py:114`
- authentic match/window evidence:
  `reports/reviews/W04/returns/W04-VERTICAL-SLICE-IDENTITY-BUNDLE-AUDIT-01-R1.md:90`

## Risks

- P1: using the descriptor-only v1 schema digest as if it bound receipt keys would
  create authoritative-looking bytes without accepted content authority.
- P1: using the v1 product digest after product publication would contradict its
  `product_bytes_forbidden=true` control-only bytes.
- P1: omitting the accepted completion-index digest from the build aggregate
  permits identical build identity across different completeness authorities.
- P1: fixture or arbitrary window/cutoff/snapshot values permit semantically
  different Gold bytes under the same claimed build contract.
- P1: a receipt containing its own digest, or a manifest/product referencing a
  later receipt, introduces a content-address cycle.
- P1: proceeding with a fixture/arbitrary build ID remains forbidden.

## Follow-up items

- Ask the user to authorize the exact bounded product/build authority above, or
  supply different window/receipt choices. Do not dispatch authoritative receipt,
  launcher, or final-publication implementation before that decision and its
  independent review.
- Continue only already-authorized non-publishing source, identity, encoder, and
  in-memory proof work while clarification is pending.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no build ID calculated: confirmed
- no receipt, product, manifest, control, data, provider, network, cloud,
  container, CI, endpoint, remote, or deployment action: confirmed
