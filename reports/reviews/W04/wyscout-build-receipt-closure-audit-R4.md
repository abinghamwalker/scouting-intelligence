# W04 build/receipt closure audit R4

Date: 2026-08-01

Status: **bounded R3 layer-summary semantic correction; fresh independent review required; not self-approved**

Verdict: **USER_CLARIFICATION_REQUIRED**

## 1. Exact scope and incorporation

This R4 corrects only the single layer-summary semantic binding returned by the R3
independent review. The complete R3 audit at
`reports/reviews/W04/wyscout-build-receipt-closure-audit-R3.md`, physical SHA-256
`0cf86df75af1276b3703083d3137de9ef345e2125a08a4e819617bbfd6100435`,
is incorporated unchanged. R4 augments R3 before its Section 3 Gold-population work
with Sections 3–5 below and replaces only R3 Section 8's candidate user question
with R4 Section 7.

Every R20/R21/v1/index/R2/R3 byte and every passing R3 window, schema, aggregate,
receipt, complete-parent, product-readback, manifest-derived population, boundary
equality, clock and 25-key rule remains binding. R4 adds no manifest field,
projection key, product field, dependency, schema root, writer, feature, or second
semantic derivation.

This is a report-only authority candidate. It creates no implementation, authority,
manifest, product, receipt, build, or data byte.

## 2. Fixed-binding verification

Every packet-fixed artifact was reproduced before analysis.

| Binding | Exact SHA-256 | Result |
| --- | --- | --- |
| R3 audit | `0cf86df75af1276b3703083d3137de9ef345e2125a08a4e819617bbfd6100435` | PASS |
| R3 independent review | `658cfeb2d504b4124467861391acfdc25643d0c5a1faf2afbf538eeb7c652074` | PASS |
| R3 reviewer return | `1456d6016606a8bec813c67a6ebd341204a72cf3efdf92365ef07c408f90fb19` | PASS |
| R20 | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | PASS |
| R21 | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | PASS |
| source-completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | PASS |

No fixed binding drifted.

## 3. Sole complete-LayerManifest semantic derivation

For each independently guard-read and closed-schema-validated Bronze, Silver or
Gold `LayerManifest`, construct exactly one preimage object with exactly two keys in
increasing Unicode code-point order:

```text
layer_manifest
semantic_schema_version
```

The exact value contract is:

```text
layer_manifest = the complete exact parsed LayerManifest JSON object
semantic_schema_version = w04-wyscout-layer-manifest-semantic-v1
```

`layer_manifest` is the whole accepted implemented value, not a projection. It
contains every field required by the accepted complete v2 `LAYER_MANIFEST` schema,
with its exact JSON type/value, every nested field, every ordered array and every
explicit null if the schema permits one. Strict parsing and closed-schema validation
must already have rejected every unknown, duplicate, omitted, default-substituted,
mistyped, reordered or noncanonical field. No field may be removed because it seems
operational, redundant, derivable or already present in a summary.

The exact abstract preimage is therefore:

```json
{"layer_manifest":THE_COMPLETE_PARSED_LAYER_MANIFEST_OBJECT,"semantic_schema_version":"w04-wyscout-layer-manifest-semantic-v1"}
```

`THE_COMPLETE_PARSED_LAYER_MANIFEST_OBJECT` above denotes insertion of the actual
validated JSON object; it is not a string or serialized placeholder. The only
derivation is:

```text
layer_semantic_preimage_bytes =
  R20_canonical_json(exact_two_key_object)

layer_semantic_sha256 =
  SHA256(layer_semantic_preimage_bytes)
```

The bytes are strict UTF-8, all strings are NFC, all object keys are in Unicode
code-point order, arrays retain schema order, and there is no BOM, insignificant
whitespace or terminal LF. This differs intentionally from the physical manifest
file encoding, which is canonical JSON plus exactly one terminal LF.

The `LayerManifest` object contains no layer-level semantic digest or summary
`semantic_sha256`, so embedding its complete value in this wrapper cannot include
the digest being derived. The wrapper contains neither its own digest nor any R20
summary row. The derivation is acyclic.

The following are forbidden alternative derivations:

- copying one entry's `semantic_sha256`;
- hashing or concatenating only entry digests;
- using the manifest physical SHA-256;
- copying another layer's semantic digest;
- hashing a partial manifest field set;
- hashing the three summary rows or a downstream wrapper;
- adding a terminal LF, schema-selected omission or second version/preimage; or
- adding a semantic field to `LayerManifest`.

## 4. All-three-summary physical and semantic reproduction

The invocation writer must validate the exact R20 `layer_manifests` array before
R3 may select the Gold population. The array has exactly three five-key rows in
this exact order:

```text
BRONZE
SILVER
GOLD
```

Each row retains exactly:

```text
layer
manifest_relative_path
manifest_sha256
manifest_size_bytes
semantic_sha256
```

For each row, independently and without reusing a caller semantic value, the writer
must:

1. derive the exact same-build manifest path from the row layer and enclosing
   `build_id` and require byte equality to `manifest_relative_path`;
2. guard-read the complete physical bytes at that exact path, with no scan,
   alternate, symlink, newest-file or caller-path recovery;
3. reproduce `manifest_sha256` and `manifest_size_bytes` from those physical bytes;
4. require strict R20 canonical JSON plus exactly one terminal LF and byte-identical
   canonical parse/reserialization;
5. validate the complete accepted v2 `LAYER_MANIFEST` closed schema;
6. require its `layer`, `build_id`, manifest path, completion state, source/index,
   tenant, rights, clocks, authorities, feature schema and dependency lineage to
   equal the row, enclosing invocation and accepted authorities; and
7. construct Section 3's exact two-key object from that parsed manifest, derive
   `layer_semantic_sha256`, and require exact equality to the row's
   `semantic_sha256`.

All three rows must pass before the Gold row can be used as R3's population root.
The physical digest and the layer semantic digest are distinct claims and both must
be reproduced. A valid Gold row cannot compensate for an invalid Bronze or Silver
row.

## 5. Exact parent-summary reconciliation

After all three summaries and manifests independently pass Section 4, reconcile the
same-build parent chain to those exact summary rows:

```text
Gold.parent_layer_manifests = exactly one SILVER row
Silver.parent_layer_manifests = exactly one BRONZE row
Bronze.parent_layer_manifests = empty
```

The Gold manifest's Silver parent row must have:

```text
layer = R20 Silver summary.layer
build_id = enclosing build_id = parsed Silver manifest.build_id
relative_path = R20 Silver summary.manifest_relative_path
sha256 = R20 Silver summary.manifest_sha256
```

The Silver manifest's Bronze parent row must satisfy the identical four equalities
against the exact R20 Bronze summary and parsed Bronze manifest. The complete
guard-read bytes have already reproduced those summary physical identities under
Section 4. Bronze must contain no parent row.

`ParentLayerManifest` has no semantic or size field. None is invented. Parent
semantic equality is established indirectly and unambiguously because each parent
summary's own `semantic_sha256` was independently reproduced from that exact
parent's complete parsed manifest under Section 4.

Any missing, additional, duplicate, reordered, cross-layer, cross-build,
path-substituted or physical-digest-substituted parent row fails before R3's Gold
population derivation. R3's exact entry-parent-path reconciliation then proceeds
unchanged.

## 6. Mandatory substitution rejection and retained R3 closure

Before `result_state="COMPLETE"`, the implementation and independent review must
demonstrate failure for each of these adversarial cases while keeping manifest and
product bytes otherwise fixed:

1. replace only Bronze summary `semantic_sha256`;
2. replace only Silver summary `semantic_sha256`;
3. replace only Gold summary `semantic_sha256`;
4. copy any manifest entry semantic digest into a layer summary;
5. copy Bronze, Silver or Gold layer semantic digest into a different layer summary;
6. swap summary semantic values without changing path/physical identities; and
7. perform any case above and recompute every downstream summary-array,
   final-recheck, invocation-receipt and child-result wrapper digest.

Every case fails at Section 4's direct equality between the independently derived
complete-manifest digest and that layer's summary value. Rehashing a later wrapper
cannot change the earlier guard-read manifest value or its deterministic preimage.
No entry digest, physical digest, other-layer digest or downstream hash substitutes.

Only after Sections 3–5 pass does every incorporated R3 rule execute unchanged:
the accepted Gold manifest yields exactly one ordered `GOLD_PLAYER_WINDOW` path;
the boundary summary population equals it exactly; the Gold product is guard-read;
the corresponding boundary receipt is reopened; all path/hash/size/semantic/
row-count/lineage/temporal/build/run and
`started_at <= checked_at <= completed_at` predicates pass; and only then may the
unchanged nine-key invocation receipt claim `COMPLETE`.

The publication graph remains acyclic:

```text
product -> complete layer manifest -> reproduced layer summary
product + complete Gold layer manifest -> boundary receipt
three reproduced layer summaries + boundary receipt -> invocation receipt
invocation receipt -> child result
```

The layer-semantic derivation reads only the already closed complete manifest and
does not point to a summary, receipt, build output wrapper or its own digest.
R2 Section 7.2's existing product-contract v2 `receipt_contracts` value incorporates
this sole derivation and all-three-summary reconciliation alongside the incorporated
R3 rules. No aggregate top-level key, schema-bundle root or projection field changes.

## 7. Exact bounded authorization question

The following corrected candidate question requires a different fresh independent
`PASS` before it may be dispatched as authority:

> Do you authorize the master to freeze and independently review the bounded additive
> W04 build/product authority in `wyscout-build-receipt-closure-audit-R4.md`: the exact
> one-match window `[2017-08-11T00:00:00Z, 2017-08-12T00:00:00Z)`, selected-match
> snapshot `2017-08-11T18:45:00Z`, strict cutoff `2026-08-01T00:00:00Z`, accepted
> completion-index and exact five-key UUID bindings; complete 23-root acyclic v2
> aggregates; unchanged receipt
> schemas and clocks; exact Gold-manifest-derived one-product/one-boundary population
> and product/boundary readback; and the sole two-key complete-`LayerManifest`
> semantic derivation reproduced for all Bronze/Silver/Gold R20 summaries with exact
> parent-summary reconciliation and substitution rejection—while preserving every
> R20/R21/v1/index/R2/R3 byte, the exact 25-key one-hash build, conservative
> four-feature POC scope, and local-only boundary?

An affirmative answer authorizes only the bounded master authority decision and its
independent review chain. It does not authorize a second semantic derivation,
placeholder digest, altered manifest schema, omitted population, broader product,
or publication before downstream gates pass.

## 8. Serial handoff and stop rules

The incorporated R2/R3 serial chain remains unchanged, but its authority,
build-contract, aggregate and publication reviews must reproduce Section 3 for all
three manifests and execute every Section 6 substitution case. More producer agents
cannot bypass the serial authority/review/materialization gates.

Stop rather than improvise if the complete manifest cannot be canonicalized by this
single formula; any fixed path/digest/count changes; parent summaries disagree; or an
architecture, product scope, dependency, provider, project-root, rights or local-only
change is required.

This R4 is a bounded producer report. It does not review or approve itself.
