# W04 build/receipt closure audit R3

Date: 2026-08-01

Status: **bounded R2 receipt-population correction; fresh independent review required; not self-approved**

Verdict: **USER_CLARIFICATION_REQUIRED**

## 1. Exact scope and incorporation rule

This R3 corrects only the single P1 boundary-population defect returned by the R2
independent review. The complete R2 audit at
`reports/reviews/W04/wyscout-build-receipt-closure-audit-R2.md`, physical SHA-256
`77cf8dcb79d202b960553dfd6da631af039e5ec0a382a0e7c30be770045d0491`,
is incorporated unchanged and remains binding except that:

1. R2 Section 6.1 is augmented by the exact Gold-manifest-derived population and
   readback rules in Sections 3–6 below; and
2. R2 Section 10's candidate authorization question is replaced by R3 Section 8.

Every other sound R2 rule and byte is preserved. In particular, R3 does not change
the one-match window, selected-match snapshot, strict cutoff, five-key window UUID
preimage, accepted completion index, exact receipt key sets, 23-root implemented
schema closure, acyclic v2 aggregate materialization, direct Gold path hash, exact
25-key one-hash build, four-feature POC, serial review gates, rights, guarded-reader,
or local-only boundary.

This is a report correction only. It creates no authority, schema implementation,
product, manifest, receipt, build, or data byte.

## 2. Fixed-binding verification and exact source evidence

Every R3 packet binding was reproduced before analysis.

| Binding | Exact SHA-256 | Result |
| --- | --- | --- |
| R2 audit | `77cf8dcb79d202b960553dfd6da631af039e5ec0a382a0e7c30be770045d0491` | PASS |
| R2 independent review | `b67e4f95e97567b60d93bab58e94bad877931b2259f219709b199d7325634658` | PASS |
| R2 reviewer return | `9b85482e2edbc8c6011c65a63a53d4d302c481cf9529c657407fcdb6d1be0d35` | PASS |
| R20 | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | PASS |
| R21 | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | PASS |
| source-completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | PASS |
| source manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | PASS |
| England event member | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` | PASS |

Only these reproduced source/index values are authoritative. Abbreviated or mistyped
digest text in review prose is not incorporated. The retained exact bindings remain:

```text
source_manifest_id = 4e16bdb5-afe7-5601-88ad-adc124cfce3b
source_manifest_sha256 = 8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd
source_completion_index_sha256 = 46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df
england_member_path = archive-members/events_England.json
england_member_sha256 = 301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad
provider_match_id = 2499719
1H_count = 901
1H_membership_sha256 = 473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b
2H_count = 867
2H_membership_sha256 = b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16
```

## 3. Gold layer summary is the sole boundary-population root

The invocation writer may not begin with caller-supplied boundary rows. It first
validates the exact R20 `layer_manifests` array and selects its third and only
`layer="GOLD"` row. That row has exactly the existing five keys:

```text
layer
manifest_relative_path
manifest_sha256
manifest_size_bytes
semantic_sha256
```

The values must satisfy all unchanged R20 rules, including:

```text
layer = GOLD
manifest_relative_path =
  data/manifests/wyscout/v5/gold/<enclosing-build_id>.manifest.json
manifest_sha256 = SHA256(complete physical Gold manifest bytes)
manifest_size_bytes = exact positive physical byte length
semantic_sha256 = exact accepted Gold-layer semantic digest
```

Before inspecting an entry, the invocation writer must guard-read that exact
`manifest_relative_path`; directory discovery, newest-file selection, caller
substitution, alternate path, symlink, or unguarded reopen is forbidden. It reads
the complete physical bytes and requires exact equality to the summary's SHA-256 and
size. Strict parse, canonical reserialization, and the accepted complete v2
`LAYER_MANIFEST` schema must pass.

The parsed manifest must be `layer=GOLD`, `complete=true`, and bind exactly the
enclosing invocation `build_id`, exact Gold manifest path, source manifest ID/digest,
source-completion-index digest, tenant, restricted rights, source clocks, accepted
authority clocks, feature schema, dependency lineage and lineage hash. Its path and
content carry no `run_id`; none is invented. Run identity is instead established by
the enclosing invocation `run_id`, invocation receipt path, boundary receipt paths,
and their exact cross-run equality rules.

### 3.1 Complete parent-manifest and parent-product chain

The Gold manifest cannot authorize a product row until its complete same-build
parent chain is guard-read and reconciled:

1. Gold has exactly one `parent_layer_manifests` row for `SILVER`, with the exact
   same-build Silver manifest path and physical SHA-256.
2. The writer guard-reads that exact Silver manifest, reproduces its complete
   physical digest, validates its closed schema, requires `layer=SILVER`, the same
   `build_id`, complete/source/index/tenant/rights/authority/feature/lineage equality,
   and exactly one same-build `BRONZE` parent row.
3. The writer guard-reads that exact Bronze manifest, reproduces its complete
   physical digest, validates its closed schema, requires `layer=BRONZE`, the same
   `build_id`, complete/source/index/tenant/rights/authority/feature/lineage equality,
   and an empty parent-manifest tuple.
4. Every Gold entry `ordered_parent_paths` value is sorted and unique and resolves
   exactly once to a Silver manifest entry of the same build. Every referenced
   Silver entry's ordered parent path resolves exactly once to a Bronze manifest
   entry of the same build. Missing, additional, duplicated, reordered,
   cross-layer, or cross-build parent references fail.

This is readback validation of already named immutable manifests. It adds no
manifest field, product field, projection key, dependency, or writer.

## 4. Exact manifest-derived Gold and boundary population

Only after Section 3 passes does the invocation writer derive:

```text
expected_gold_entries =
  every and only Gold-manifest entry whose path.path_role is GOLD_PLAYER_WINDOW,
  in the manifest's already validated strict relative-path order

expected_gold_paths =
  tuple(entry.path.relative_path for entry in expected_gold_entries)
```

The accepted closed Gold manifest already forbids a non-Gold entry and requires
unique ordered entry paths. R3 additionally requires, for this bounded POC:

```text
len(expected_gold_entries) = 1
len(expected_gold_paths) = 1
len(set(expected_gold_paths)) = 1
len(boundary_receipts) = 1

tuple(row.gold_relative_path for row in boundary_receipts)
  == expected_gold_paths
```

`boundary_receipts` remains an array of the exact R2 four-key summary objects:

```text
gold_relative_path
relative_path
sha256
size_bytes
```

It must already be in the same canonical Gold-path order. Equality is sequence and
set equality together: no sorting, deduplication, filtering, or recovery may repair
a submitted array. The empty array, a missing expected path, an extra path, a
duplicate, or the right set in the wrong order fails before receipt serialization.

The authoritative population therefore comes from the exact guard-read accepted
Gold manifest, not a caller Boolean, count, witness, boundary array, directory scan,
or digest derived only from submitted boundary rows.

## 5. Guard-read every expected Gold product

For the sole `expected_gold_entries[0]`, the invocation writer guard-reads the exact
manifest-named product path before accepting a corresponding boundary receipt. It
must re-establish all of the following from the physical product bytes and accepted
schema/serializer rules:

1. the exact NFC relative path and `GOLD_PLAYER_WINDOW` role;
2. same enclosing `build_id` and the exact path partition values;
3. physical SHA-256 and positive size equal the manifest entry;
4. serializer owner/version and accepted v2 canonical Gold schema identity;
5. parsed row count equal the manifest entry and exactly `1` for this POC;
6. semantic SHA-256 recomputed from the accepted schema, canonical ordered row,
   complete parent/authority/schema lineage and serializer rules, equal to the
   manifest entry;
7. manifest entry `complete=true`, exact restricted classification, exact sorted
   partition values, and exact validated Silver parent paths;
8. the Gold row's source manifest, source-completion index, tenant, role context,
   window definition/start/end, selected-match snapshot, cutoff, feature schema,
   dependency lineage/hash and applicability equal the accepted invocation and
   manifest authorities; and
9. the sole row's complete `W04SemanticTemporalProof` passes its closed schema and
   strict-before rules, and its exact R20-canonical object digest is reproduced as
   the expected `temporal_proof_sha256`.

An unreadable, empty, additional-row, stale, malformed, cross-build, cross-window,
cross-cutoff, path-, physical-digest-, size-, semantic-digest-, row-count-, parent-,
lineage-, or temporal-proof-mismatched product fails before any invocation receipt
can claim `COMPLETE`.

## 6. Exact boundary readback against manifest and product

For the one path in `expected_gold_paths`, exactly one boundary summary and exactly
one boundary receipt must exist. All R2 receipt rules remain binding, augmented by
these equalities:

1. `summary.gold_relative_path` equals the exact expected Gold path.
2. `summary.relative_path` equals the unchanged R20 boundary path formula under the
   enclosing `build_id` and `run_id`; its filename digest is direct SHA-256 of the
   strict UTF-8 NFC Gold path bytes with no BOM or terminal LF.
3. The writer guard-reads the complete boundary bytes and reproduces summary
   `sha256` and `size_bytes`; the accepted 15-key boundary schema and canonical JSON
   plus one-terminal-LF encoding pass.
4. Boundary `build_id` and `run_id` equal the enclosing invocation and path.
5. Boundary `gold_manifest_relative_path` and `gold_manifest_sha256` equal the exact
   guard-read Gold manifest and R20 Gold summary.
6. Boundary `gold_product_relative_path`, physical SHA-256, semantic SHA-256 and
   `row_count` equal the exact guard-read Gold product and manifest entry.
7. Boundary `dependency_lineage_hash`, `feature_cutoff_ts`, and
   `temporal_proof_sha256` equal the guard-read Gold row/proof.
8. Boundary `verification_state` is exactly `STRICT_BEFORE_CUTOFF_PASS`.
9. The retained cross-receipt predicate holds:
   `invocation.started_at <= boundary.checked_at <= invocation.completed_at`.

Only after the Gold summary, complete parent chain, exact one-entry population,
Gold product, boundary summary, boundary receipt and cross-clock checks all pass may
the writer set `result_state="COMPLETE"` and serialize the unchanged nine-key
invocation receipt.

The writer must explicitly reject, before serialization: empty, missing,
additional, duplicate, reordered, stale, cross-build, cross-run, cross-Gold,
cross-layer, path-mismatched, hash-mismatched, size-mismatched,
semantic-mismatched, row-count-mismatched, lineage-mismatched,
temporal-proof-mismatched, malformed, noncanonical, or out-of-interval manifest,
product, boundary-summary, or boundary-receipt evidence. Per-row validation alone is
insufficient; exact manifest-derived population equality is mandatory.

## 7. Acyclicity and aggregate incorporation remain unchanged

R3 adds only readback predicates over already closed earlier nodes. The publication
graph remains:

```text
product Parquet -> layer manifest -> temporal-boundary receipt
  -> rebuild invocation receipt -> child result summary
```

The invocation reader reads backward along that graph. No product or manifest points
forward to a receipt; no receipt contains its own digest; no projection contains a
receipt instance; and the child result hashes only the already closed invocation
receipt. R3 introduces no content-address cycle.

R2 Section 7.2's `receipt_contracts` value incorporates the complete R2 receipt
schemas together with R3 Sections 3–6. The v2 schema/product aggregate shapes,
materialization order and no-placeholder rule do not otherwise change. The existing
projection fields `schema_bundle_digest` and `product_contract_digest` bind the
accepted materialized values; the projection remains exactly 25 keys and one hash.

## 8. Exact bounded authorization question

The following is the corrected candidate question. It requires a fresh independent
`PASS` before it may be dispatched as authority:

> Do you authorize the master to freeze and independently review the bounded additive
> W04 build/product authority in `wyscout-build-receipt-closure-audit-R3.md`: the exact
> one-match window `[2017-08-11T00:00:00Z, 2017-08-12T00:00:00Z)`, selected-match
> snapshot `2017-08-11T18:45:00Z`, strict cutoff `2026-08-01T00:00:00Z`, accepted
> completion-index and exact five-key window UUID bindings, complete 23-root acyclic
> v2 aggregate rules, exact receipt schemas/readback clocks, and the guard-read Gold
> manifest-derived exact one-product/one-boundary population equality with complete
> parent-manifest, Gold-product and boundary-receipt readback—while preserving every
> R20/R21/v1/index/R2 byte, the unchanged 25-key one-hash build, conservative
> four-feature POC scope, and local-only boundary?

An affirmative answer authorizes only the bounded master decision and independent
review chain. It does not authorize a placeholder digest, omitted population,
unreviewed implementation, broader product, or publication before all downstream
gates pass.

## 9. Shortest serial handoff and stop rules

The R2 Section 9 chain remains unchanged except that its authority, build-contract,
aggregate-materialization and publication reviews must test Sections 3–6 above,
including empty-array and wrong-population adversarial cases. More producer agents
cannot bypass the serial authority/review/materialization gates.

Stop rather than improvise if a fixed digest/path/count changes; the Gold manifest
does not yield exactly one product; a complete same-build parent chain cannot be
proved; product/boundary readback disagrees; or any architecture, product scope,
dependency, provider, project-root, rights, or local-only change is required.

This R3 is a bounded producer report. It does not review or approve itself.
