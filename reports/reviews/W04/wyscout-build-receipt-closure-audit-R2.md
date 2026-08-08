# W04 build/receipt closure audit R2

Date: 2026-07-31

Status: **corrected bounded decision surface; fresh independent review required; not self-approved**

Verdict: **USER_CLARIFICATION_REQUIRED**

This R2 supersedes only the four recommendations returned by the R1 independent
review. It preserves the R1 audit, R1 review, R20, R21, the accepted source
completion index, and every other accepted byte. It proposes no architecture,
provider, rights, project-root, dependency, storage, local-only, cloud, container,
endpoint, hosted-CI, deployment, Git, product-feature, or source-scope change.

The clarification remains one bounded product/build authority decision. No product,
receipt, manifest, authority, implementation, or data byte is created by this audit.

## 1. Fixed-binding verification

Every packet binding was reproduced before analysis.

| Binding | Expected SHA-256 | Observed | Result |
| --- | --- | --- | --- |
| R1 closure audit/return | `2d0fd4c6a797c6f04879772075d068560ccbca23456cc559160eb259c5d7ef18` | same | PASS |
| R1 independent review | `b3c6009cf3ad826bddabfbd6b722f89dcbffb11bf7755bbe60d4df68b67c9a09` | same | PASS |
| R1 reviewer return | `79a829d7c147a39b05b25495e1ff8a68604d625afebb3ae9ee21e24974a9efce` | same | PASS |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | same | PASS |
| R21 correction | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | same | PASS |
| accepted source-completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | same | PASS |

The historical v1 product-contract and descriptor-only schema-bundle preimages
remain respectively:

```text
0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293
a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f
```

They are retained as immutable inputs. They are not relabelled as publication or
implemented-schema authority.

## 2. Exact four-finding correction

| R1 review finding | R2 correction |
| --- | --- |
| P1 snapshot used source acquisition | `snapshot_as_of_ts` is exactly the retained selected-match start `2017-08-11T18:45:00Z`; `valid_from_ts=max(snapshot_as_of_ts, dependency_watermark)` remains unchanged. |
| P1 schema aggregate was incomplete | Section 7 defines a closed, acyclic v2 materialization rule over every actually implemented R20 Bronze, Silver, Gold, layer-manifest, result, and receipt schema and retains the descriptor-only v1 digest. No absent schema is assigned a digest. |
| P1 cross-receipt clock order was open | The invocation writer must reopen every boundary receipt and prove exact path/hash/size plus `started_at <= checked_at <= completed_at` before it can serialize the invocation receipt. |
| P2 window UUID preimage was not byte-exact | Section 3 freezes the exact five keys, string values, key order, canonical JSON bytes, namespace, SHA-256 name input, and UUIDv5 formula. |

No other R1 conclusion is changed.

## 3. Exact one-match POC window authority

The window is the half-open UTC day:

```text
window_start_utc = 2017-08-11T00:00:00Z
window_end_utc = 2017-08-12T00:00:00Z
feature_cutoff_ts = 2026-08-01T00:00:00Z
snapshot_as_of_ts = 2017-08-11T18:45:00Z
valid_from_ts = max(snapshot_as_of_ts, dependency_watermark)
```

The window contains exactly the retained authentic England match: provider match
`2499719`, canonical match UUID
`bad97950-6fac-5cf0-a93c-094f91abbb9b`, start
`2017-08-11T18:45:00Z`. Snapshot is semantic selected-match time, not source
acquisition time. The cutoff is strict and is later than the source acquisition and
the latest currently bound authority acceptance; equality remains forbidden.

### 3.1 Exact five-key UUID object

The object has exactly five JSON string fields in increasing Unicode code-point
order and no other field:

1. `match_id` = `bad97950-6fac-5cf0-a93c-094f91abbb9b`
2. `source_manifest_id` = `4e16bdb5-afe7-5601-88ad-adc124cfce3b`
3. `window_end_utc` = `2017-08-12T00:00:00Z`
4. `window_schema_version` = `w04-single-match-poc-window-v1`
5. `window_start_utc` = `2017-08-11T00:00:00Z`

Its exact R20-canonical JSON text is:

```json
{"match_id":"bad97950-6fac-5cf0-a93c-094f91abbb9b","source_manifest_id":"4e16bdb5-afe7-5601-88ad-adc124cfce3b","window_end_utc":"2017-08-12T00:00:00Z","window_schema_version":"w04-single-match-poc-window-v1","window_start_utc":"2017-08-11T00:00:00Z"}
```

`window_identity_bytes` is strict UTF-8 of that NFC text, with no BOM, whitespace,
or terminal LF. The derivation is exactly:

```text
window_definition_namespace = UUIDv5(
  NAMESPACE_URL,
  "urn:scouting-intelligence:w04:wyscout:window-definition:v1")

window_identity_sha256 = SHA256(window_identity_bytes)

window_definition_id = UUIDv5(
  window_definition_namespace,
  "single-match-poc:" + window_identity_sha256)
```

The cutoff and snapshot do not enter this five-key object. They remain independently
bound product/projection values. No completion-index UUID or namespace is introduced.

## 4. Accepted source-completion binding

The existing content address remains the sole completion-index identity:

```text
path = data/manifests/wyscout/v5/source-completion/
       46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df
       .source-completion-index.json
sha256 = 46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df
source_manifest_id = 4e16bdb5-afe7-5601-88ad-adc124cfce3b
source_member_path = archive-members/events_England.json
source_member_sha256 = 301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad
source_member_row_count = 643150
provider_match_id = 2499719
canonical_match_id = bad97950-6fac-5cf0-a93c-094f91abbb9b
```

The exact retained period population is:

| Period | Rank | Action count | Ordered membership digest |
| --- | ---: | ---: | --- |
| `1H` | 1 | 901 | `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b` |
| `2H` | 2 | 867 | `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16` |

The accepted reader's source binding, canonical ordering, uniqueness, aggregate
row-count reconciliation, and exact supplied-period equality remain mandatory. A
Boolean, caller count, submitted-population witness, or digest derived only from the
submitted population is not a substitute. The authority remains limited to this
W04 one-match/four-feature POC and implies no wider source completeness.

## 5. Exact unchanged one-hash build surface

The R20 pre-build projection retains exactly these 25 keys in Unicode code-point
order:

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

`schema_version` is exactly `w04-wyscout-pre-build-projection-v1`. R20 canonical
JSON applies. The one and only build calculation remains:

```text
build_id = SHA256(canonical_json(exact_25_key_projection))
```

The post-hash invocation copies the other 24 values byte-semantically unchanged,
removes only projection `schema_version`, and inserts only `build_id`. It therefore
also has exactly 25 keys. Rebuild performs the inverse reconstruction and the same
single SHA-256. No index field, receipt, output, path, run ID, nonce, host value, or
clock is added as a 26th key. The accepted index and final schema closure are bound
through the corrected existing aggregate fields in Section 7.

## 6. Exact closed receipt contracts

### 6.1 Rebuild invocation receipt

The invocation receipt has exactly these nine keys in canonical object order:

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

Rules:

- `schema_version` is exactly
  `w04-wyscout-rebuild-invocation-receipt-v1`.
- `result_state` is exactly `COMPLETE`.
- `rebuild_invocation` is the exact R20 25-key post-hash invocation.
- `layer_manifests` is exactly the three R20 five-key rows in `BRONZE`, `SILVER`,
  `GOLD` order.
- `boundary_receipts` is sorted uniquely by strict Gold relative path. Every row
  has exactly `gold_relative_path`, `relative_path`, `sha256`, and `size_bytes`.
- `started_at` and `completed_at` are truthful canonical UTC operational clocks and
  satisfy `started_at <= completed_at`.
- Before serialization, the sole invocation writer reopens every summarized
  boundary `relative_path` through the guarded local reader, reads its complete
  physical bytes, and reproduces exact `sha256` and `size_bytes`.
- The reopened boundary content must reproduce the summary's
  `gold_relative_path`, enclosing `build_id`, and enclosing `run_id`, and must pass
  its own closed schema.
- For every reopened boundary, the writer enforces the cross-receipt predicate
  `started_at <= boundary.checked_at <= completed_at`.
- Missing, additional, duplicate, reordered, stale, cross-run, cross-build,
  cross-Gold, path-mismatched, hash-mismatched, size-mismatched, malformed, or
  out-of-interval boundary bytes fail before an invocation receipt is written.
- The physical file is R20-canonical JSON plus exactly one terminal LF. Its own
  path, digest, and size are absent from its content and are supplied only by the
  enclosing build/run path and later child-result summary.

The readback clocks are operational and remain excluded from build/product identity.

### 6.2 Temporal-boundary receipt

The boundary receipt has exactly these 15 keys in canonical object order:

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

Rules:

- `schema_version` is exactly
  `w04-wyscout-temporal-boundary-receipt-v1`.
- `verification_state` is exactly `STRICT_BEFORE_CUTOFF_PASS`.
- `row_count` is exactly `1` for this bounded POC.
- Every build/run/path/digest equals the accepted Gold product and Gold manifest.
- `gold_relative_path_sha256` is direct SHA-256 of strict UTF-8 NFC bytes of the
  exact Gold relative-path string, with no BOM or terminal LF. It equals the digest
  token in the boundary filename.
- `temporal_proof_sha256` covers the exact R20-canonical temporal-proof object.
- `checked_at` is a truthful canonical UTC operational clock. It is later checked
  against its invocation interval under Section 6.1.
- The physical file is R20-canonical JSON plus exactly one terminal LF and contains
  neither its own path nor its own physical digest.

## 7. Acyclic product-authorized v2 aggregate materialization

The user decision authorizes the following exact materialization rules; it does not
assert that future absent schema bytes or aggregate digests already exist.

### 7.1 Complete v2 schema-bundle preimage

The schema-bundle preimage ID is exactly
`w04-wyscout-schema-bundle-preimage-v2`. Its R20-canonical top-level object has
exactly these eight keys in code-point order:

```text
implemented_schema_rows
preimage_schema_version
r20_design_sha256
r21_design_sha256
required_root_roles
schema_bundle_preimage_id
schema_bundle_preimage_v1_sha256
surface_closure_policy
```

Fixed scalar values are:

```text
preimage_schema_version = w04-wyscout-schema-bundle-preimage-v2
r20_design_sha256 = 8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047
r21_design_sha256 = faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020
schema_bundle_preimage_id = w04-wyscout-schema-bundle-preimage-v2
schema_bundle_preimage_v1_sha256 = a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f
surface_closure_policy = EXACT_TRANSITIVE_CANONICAL_IMPLEMENTED_SCHEMA_CLOSURE
```

`required_root_roles` is exactly this closed ordered array:

```text
BRONZE_KNOWN_RECORD
BRONZE_REJECTED_RECORD
BRONZE_REJECTED_FIELD
SILVER_COMPETITION
SILVER_TEAM
SILVER_PLAYER
SILVER_MATCH
SILVER_ACTION
SILVER_LINEUP_STINT
SILVER_POSSESSION
SILVER_PLAYER_MATCH_FACT
GOLD_PLAYER_WINDOW
LAYER_MANIFEST
TEMPORAL_BOUNDARY_RECEIPT
REBUILD_INVOCATION_RECEIPT
ENTRYPOINT_SOURCE_RESULT
COMPONENT_PROOF_RESULT
PRE_BUILD_ADMISSION_RESULT
REBUILD_RECEIPT_SUMMARY
LAYER_MANIFEST_SUMMARY
FINAL_RECHECK_RESULT
POST_BUILD_ID_REBUILD_RESULT
CHILD_RESULT_ENVELOPE
```

This roster covers all R20 product layers, the layer-manifest surface, the complete
R20 child-result envelope and each separately validated nested result surface, and
both receipts. This is the v2 schema dependency order: the boundary schema precedes
the invocation schema it is summarized by, and nested result schemas precede the
child-result envelope that contains them. It does not rewrite the historical R21
descriptor order. The closed schema for each root must contain its complete transitive
named/anonymous definition closure, unions, enums, nullability, cardinality,
ordering, and cross-field constraints; a code symbol name or serializer digest is
not schema content.

`implemented_schema_rows` has exactly one row for every root role and no other row.
Rows occur in the `required_root_roles` order. Each row has exactly these six keys in
code-point order:

```text
canonical_schema_content_sha256
canonical_schema_id
canonical_schema_version
closure_dependencies
root_role
surface_kind
```

Rules for every row:

- `root_role` equals its array position's required role.
- `surface_kind` is exactly `IMPLEMENTED_CLOSED_SCHEMA`.
- `canonical_schema_id` and `canonical_schema_version` are non-empty NFC strings
  frozen by the owning implementation contract and unique as a pair.
- `canonical_schema_content_sha256` is SHA-256 of the fully closed canonical schema
  bytes for that exact ID/version, not code bytes, a descriptor, a placeholder, or
  a serializer claim.
- `closure_dependencies` is the ordered unique array of earlier
  `canonical_schema_id` values referenced by this schema. Forward, missing,
  duplicate, or cyclic dependencies fail.
- Canonical schema bytes contain no own content digest, schema-bundle digest,
  product-contract digest, projection/build/run/output identity, host path, or
  operational clock.

Materialization is unavailable until every root schema is actually implemented,
the canonical schema exporter has reproduced its exact bytes, and a fresh
independent review has accepted the complete roster and content digests. No null,
placeholder, anticipated digest, descriptor-only row, omitted nested constraint, or
extra implemented publication surface is permitted. If implementation creates an
additional externally serialized R20 product/manifest/result/receipt root, the
closed roster authority must be returned before publication; it cannot be silently
omitted or appended.

Only after exact set equality and review pass is:

```text
schema_bundle_digest = SHA256(
  R20_canonical_json(complete_v2_schema_bundle_preimage))
```

materialized for the existing projection field.

### 7.2 Product-authorized v2 preimage

The product-contract preimage ID is exactly
`w04-wyscout-product-contract-preimage-v2`. Its R20-canonical top-level object has
exactly these ten keys in code-point order:

```text
completion_index_binding
feature_cutoff_ts
preimage_schema_version
product_authorization_state
product_contract_preimage_id
product_contract_preimage_v1_sha256
publication_order
receipt_contracts
schema_bundle_preimage_v2_sha256
window_authority
```

Fixed values and objects are exactly those in Sections 3, 4, 6, and 7.1, including
the accepted completion-index path/digest/source/member/match/period bindings; the
exact cutoff, snapshot, valid-from rule, five-key window object and UUID formula;
the two complete receipt schemas/readback rules; and this exact ordered publication
array:

```text
PRODUCT_PARQUET
LAYER_MANIFEST
TEMPORAL_BOUNDARY_RECEIPT
REBUILD_INVOCATION_RECEIPT
CHILD_RESULT_SUMMARY
```

The remaining fixed scalars are:

```text
preimage_schema_version = w04-wyscout-product-contract-preimage-v2
product_authorization_state = W04_SINGLE_MATCH_FOUR_FEATURE_POC_PUBLICATION_AUTHORIZED
product_contract_preimage_id = w04-wyscout-product-contract-preimage-v2
product_contract_preimage_v1_sha256 = 0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293
schema_bundle_preimage_v2_sha256 = the actual accepted digest materialized by Section 7.1
```

The explanatory phrase on the final line above is not a serialized value. No future
digest token or placeholder may be serialized. The v2 product preimage is
materialized only after the complete v2 schema bundle exists and passes independent
review. Then:

```text
product_contract_digest = SHA256(
  R20_canonical_json(complete_v2_product_contract_preimage))
```

is used in the existing projection field.

The dependency graph is strictly one-way:

```text
immutable R20/R21 + descriptor-only schema v1
  -> complete implemented schema bundle v2
  -> product-authorized contract v2
  -> unchanged 25-key projection
  -> build/product/layer-manifest instances
  -> boundary receipt(s)
  -> invocation receipt
  -> child result summary
```

The schema bundle never references the product aggregate, projection, build, output,
or receipt instance. Neither aggregate contains its own digest. Products/manifests
never reference a later receipt, and no receipt contains its own path/content digest.
The graph is therefore acyclic.

## 8. Conservative product boundary retained

The decision remains limited to the already selected one-day, one authentic match,
one-player, four-supported-feature proof. It adds no feature, minute, per-90,
outcome, provider-native possession, role-inferred, model, current-data, wider
competition, or external publication claim. All R21 feature restrictions,
integer-only action-subevent mapping, string quarantine/unmapped behavior, equal-clock
rules, rights, guarded-reader, and local-only constraints remain unchanged.

## 9. Shortest safe serial packet chain after authorization

1. **Build/product authority decision — master.** Freeze only the exact R2 rules,
   authority paths, and tests; preserve R20/R21/v1/index bytes. Do not create product
   or future schema digests.
2. **Authority independent review.** Reproduce the window bytes/UUID rule, index
   binding, receipt contracts, acyclic aggregate schemas, and unchanged 25 keys.
3. **Build-contract implementation.** Implement the projection/invocation inverse,
   one-hash calculator, window authority, receipt models/readers, and canonical
   schema exporters; write no publication product.
4. **Build-contract independent review.** Challenge closed keys/types/order,
   canonical bytes, readback clocks, path hash, cycles, and adversarial rejection.
5. **Implemented-schema closure.** Complete and independently accept the exact
   Bronze/Silver/Gold/manifest/result/receipt root schemas. Disjoint product owners
   may work in parallel only where their packets permit, but final closure is a
   serial equality gate.
6. **V2 aggregate materialization and independent review — master serial gate.** Once
   all required schema bytes exist, reproduce every content digest, materialize the
   schema v2 digest then product v2 digest, and accept neither on placeholders.
7. **Identity/runtime admission and sole launcher.** Build assembly waits for the
   accepted identity bundle, code/environment/resource admission, and both accepted
   aggregate digests; the launcher performs the sole build hash.
8. **Rebuild and named receipt writers.** Publish only through accepted serializers,
   layer writers, boundary writer, invocation writer, and child-result summary in
   the acyclic order above.
9. **Independent publication review and master repository gate.** Reproduce two
   local builds, build/projection/product equality, permitted operational receipt
   differences, fail-closed cases, empty remote, local-only state, and the complete
   repository gate before master acceptance.

Steps 1–4 and the final materialization in step 6 are irreducibly serial authority
and review gates. Already-authorized path-disjoint nonpublishing implementation can
proceed in parallel but cannot bypass them.

## 10. Exact bounded authorization question

The following is the candidate question for the user. It must receive fresh
independent `PASS` review before dispatch as authority:

> Do you authorize the master to freeze and independently review the bounded additive
> W04 build/product authority in `wyscout-build-receipt-closure-audit-R2.md`: the exact
> one-match window `[2017-08-11T00:00:00Z, 2017-08-12T00:00:00Z)`, selected-match
> snapshot `2017-08-11T18:45:00Z`, strict cutoff `2026-08-01T00:00:00Z`, accepted
> completion-index binding, exact five-key window UUID preimage, complete acyclic
> implemented-schema/product v2 aggregate rules, and exact boundary/invocation
> receipt schemas and readback clocks—while preserving every R20/R21/v1/index byte,
> the unchanged 25-key one-hash build, the four-feature POC scope, and the local-only
> boundary?

An affirmative answer authorizes only the master decision and its independent review
chain. It is not authority to fabricate absent schema digests, bypass review, broaden
the product, or publish before every downstream gate passes.

## 11. Stop rules

Stop rather than improvise if any fixed digest/path/count changes; a different
window, cutoff, feature, source, provider, rights, dependency, project root,
architecture, local-only boundary, or aggregate key shape is required; a schema
digest is requested before its bytes exist; a 26th projection key is proposed; a
receipt cannot satisfy readback and clock order; or any product/receipt/data byte
would need to be written before authority and review pass.

This report is a corrected producer artifact. It does not approve itself.
