# W04 build/receipt closure audit independent review R4

Date: 2026-08-01  
Reviewer role: fresh independent W04 build/receipt R4 semantic reviewer  
Reviewed artifact: `reports/reviews/W04/wyscout-build-receipt-closure-audit-R4.md`  
Task: `W04-BUILD-RECEIPT-CLOSURE-AUDIT-REVIEW-01-R4`

## Verdict

`PASS_TO_USER_QUESTION`

- P0: `0`
- P1: `0`
- P2: `0`

R4 supplies the one binding missing from R3. For each Bronze, Silver and Gold
summary, the writer must derive `semantic_sha256` from exactly one canonical
two-key wrapper around that summary's complete, guard-read, closed-schema
`LayerManifest`. The manifest contains no layer-level semantic digest or summary,
the wrapper contains neither its own digest nor a downstream value, and the
derivation therefore has no self-reference. Direct reproduction occurs before any
Gold population, boundary-receipt or invocation-receipt work, so isolated
substitution, entry/physical/other-layer copying, swaps and complete downstream
rehashing all fail at the first manifest-to-summary equality.

R4 also makes all three R20 summary rows mandatory, reconciles the Gold-to-Silver-
to-Bronze parent identities to those exact validated rows, and retains R3's exact
Gold-manifest-derived one-product/one-boundary population and complete product and
receipt readback. The incorporated R2 window, completion index, 23-root aggregate,
receipt schemas, clock checks and unchanged 25-key one-hash projection remain
exact and acyclic. Section 7 is an exact sufficient bounded user decision surface.

## 1. Fixed-byte admission

Every packet-fixed binding was reproduced before the merits review:

| Artifact | Reproduced SHA-256 | Result |
|---|---|---|
| R4 producer audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` | exact |
| R4 producer return | `a06fb74741f77f6a157418ce776a9a936ee037432866a81be1a142b45125c030` | exact |
| R3 producer audit | `0cf86df75af1276b3703083d3137de9ef345e2125a08a4e819617bbfd6100435` | exact |
| R3 independent review | `658cfeb2d504b4124467861391acfdc25643d0c5a1faf2afbf538eeb7c652074` | exact |
| R20 authority | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | exact |
| R21 authority | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | exact |
| accepted source-completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | exact physical file and content-addressed filename |

The incorporated R3 reviewer return was also reproduced as
`1456d6016606a8bec813c67a6ebd341204a72cf3efdf92365ef07c408f90fb19`.
No fixed-byte drift or stop condition was triggered.

## 2. Exact two-key complete-manifest derivation

### 2.1 One accepted JSON value and one preimage

The derivation input is not a caller projection, code object, serialized
placeholder or selected field set. It is the complete exact parsed JSON object
from the already guard-read manifest after all of these predicates pass:

1. the exact same-build path is derived from layer and enclosing `build_id`;
2. the complete physical bytes reproduce the summary SHA-256 and byte length;
3. physical bytes are strict R20 canonical JSON plus exactly one terminal LF;
4. parse and canonical reserialization are byte-identical;
5. the complete accepted closed `LAYER_MANIFEST` schema passes; and
6. unknown, duplicate, omitted, default-substituted, mistyped, reordered or
   noncanonical content has failed.

The current implemented `LayerManifest` value has the complete field set
`manifest_schema_version`, `construction_authority_state`, `layer`, `build_id`,
`manifest_path`, `source_manifest_id`, `source_manifest_sha256`,
`source_completion_index_sha256`, `tenant_context`, `classification`,
`source_available_at`, `source_acquired_at`, `authority_clocks`,
`feature_schema_hash`, `dependency_lineage_hash`, `dependency_lineage`, `entries`,
`parent_layer_manifests`, and `complete`. R4 requires all of those and every nested
field/ordered array/explicit null present in the accepted complete schema. A model
default cannot repair an omitted physical field.

For that accepted value `M`, the wrapper is exactly:

```json
{"layer_manifest":M,"semantic_schema_version":"w04-wyscout-layer-manifest-semantic-v1"}
```

Here `M` denotes the inserted JSON object, never a JSON string or the literal
letter `M`. The only two keys are in increasing Unicode code-point order because
`layer_manifest` precedes `semantic_schema_version`. R20 canonicalization sorts
every nested object key, retains every schema-ordered array, emits strict UTF-8
NFC strings, and emits no BOM, insignificant whitespace or terminal LF. Thus each
valid complete manifest value has one unambiguous canonical preimage byte string:

```text
layer_semantic_preimage_bytes = R20_canonical_json(wrapper)
layer_semantic_sha256 = SHA256(layer_semantic_preimage_bytes)
```

The manifest file's required terminal LF is intentionally physical encoding and
is not carried into the semantic wrapper. No alternative omission, second schema
version, second preimage or newline convention remains available.

### 2.2 Cycle proof

`LayerManifest` has no top-level `semantic_sha256`, no R20 summary row and no
layer-level semantic digest. Entry-level `semantic_sha256` values are earlier
product claims, not the digest of the enclosing manifest. The wrapper contains
only the complete manifest and the fixed version string; it contains no wrapper
digest, summary, receipt, child result or aggregate digest.

The retained dependency direction is therefore:

```text
immutable authorities + accepted aggregate schemas
  -> unchanged 25-key build ID
    -> product bytes
      -> complete layer manifest
        -> reproduced R20 layer summary
          -> boundary/invocation receipt
            -> child result
```

The product-contract v2 value contains the derivation rule and receipt schemas,
not a future manifest instance or its semantic digest. Its digest can enter the
build ID without pointing forward to a build output. Parent manifest references
point only Bronze-to-Silver-to-Gold: Silver contains Bronze's already closed
physical identity and Gold contains Silver's. No build, schema, manifest, summary,
receipt or aggregate edge points back to itself.

## 3. All-three-summary reproduction and parent reconciliation

The validated R20 array is exactly three five-key rows in order `BRONZE`,
`SILVER`, `GOLD`. For every row independently, R4 derives the path from layer and
build, guard-reads the exact complete file, reproduces physical hash and size,
validates canonical bytes and the complete closed schema, reconciles build/source/
index/tenant/rights/clocks/authorities/feature schema/lineage, derives the Section
2 semantic digest from the parsed manifest, and compares it directly to that
row's `semantic_sha256`. Gold cannot compensate for a failed Bronze or Silver
row, and population derivation cannot begin until all three pass.

The same already validated rows then close the parent chain:

- Bronze has no parent manifest;
- Silver has exactly one Bronze parent whose `layer`, enclosing/same `build_id`,
  `relative_path` and physical `sha256` equal the exact Bronze summary and parsed
  Bronze manifest; and
- Gold has exactly one Silver parent satisfying the identical equalities against
  the exact Silver summary and parsed Silver manifest.

`ParentLayerManifest` correctly contains no size or semantic field. None is
invented. Parent semantic identity is still unambiguous because the exact parent
path and physical digest select the same complete bytes whose corresponding R20
summary semantic value has already been independently reproduced. Missing,
additional, duplicate, reordered, cross-layer, cross-build, path-substituted or
physical-digest-substituted parents fail before R3 population evaluation.

## 4. Adversarial semantic substitution

Every required substitution fails before `COMPLETE`:

| Attack | Direct failing predicate |
|---|---|
| change only Bronze summary semantic value | derived Bronze whole-manifest digest != Bronze summary |
| change only Silver summary semantic value | derived Silver whole-manifest digest != Silver summary |
| change only Gold summary semantic value | derived Gold whole-manifest digest != Gold summary |
| copy an entry semantic digest | entry digest != independently derived complete-manifest digest |
| copy a physical manifest digest | physical and semantic derivations are separately reproduced |
| copy another layer's semantic digest | digest is re-derived from this row's exact path-bound manifest |
| swap layer semantic values | each row compares only with its own manifest-derived value |
| rehash summary set, final recheck, receipt and child wrapper | later hashes cannot alter the earlier guard-read manifest preimage/equality |

Changing a later wrapper never changes the complete manifest bytes selected by the
exact row path and physical identity. The former R3 counterexample is therefore no
longer executable.

## 5. Re-executed R3 population and readback closure

Only after all three summary and parent predicates pass does the exact validated
Gold manifest become the sole population root. It yields every and only
`GOLD_PLAYER_WINDOW` entry in validated manifest order, and this POC requires
exactly one entry/path and exactly one boundary summary. Sequence and set equality
must both hold; there is no sorting, filtering, deduplication or recovery.

The sole Gold product is then guard-read and reconciled to the manifest entry's
path/role/build/partition, physical hash/size, implemented schema/serializer, exact
one-row count, independently derived semantic digest, parents, restricted rights,
window/snapshot/cutoff, feature schema, completion index, lineage, applicability
and temporal proof. The matching boundary receipt is reopened and reconciled to
that same product and Gold manifest, its direct path hash, exact build/run, physical
and semantic digests, row count, lineage, cutoff, temporal-proof digest and
`STRICT_BEFORE_CUTOFF_PASS` state. Finally:

```text
invocation.started_at <= boundary.checked_at <= invocation.completed_at
```

is mandatory before the unchanged nine-key invocation receipt may state
`COMPLETE`.

The adversarial outcomes are closed:

| Attack | Failing predicate |
|---|---|
| empty or omitted boundary array | exact one-entry/one-summary cardinality and tuple equality |
| additional or cross-Gold row | exact manifest-derived path set/sequence equality |
| duplicate row | exact cardinality and unique population |
| reordered population | exact sequence equality; one-item POC still retains the general rule |
| stale/cross-build Gold manifest | summary path, complete physical hash/size and build/schema equality |
| missing/stale/wrong Gold product | manifest entry path/hash/size/semantic/row-count/readback equality |
| malformed/cross-run boundary | closed bytes, derived path, build/run and product/manifest equality |
| clock before start or after completion | exact inclusive invocation interval predicate |

No caller Boolean, count, witness, submitted-array digest, directory scan or newest
file can substitute for the exact guard-read manifest population.

## 6. Re-executed incorporated R2/R21 authority

The inherited authority remains exact:

- the half-open window is
  `[2017-08-11T00:00:00Z, 2017-08-12T00:00:00Z)`;
- selected-match snapshot is `2017-08-11T18:45:00Z`, strict cutoff is
  `2026-08-01T00:00:00Z`, and valid-from is the maximum of snapshot and the
  dependency watermark;
- the exact five-key, no-terminal-LF window object is 250 UTF-8 bytes, has SHA-256
  `3582348bc62d5624162078802a0495edd2a3206856cdf532322d1233bc33b327`,
  and derives window UUID `a0af8d56-e41d-5467-b46e-82887c4861e0` from the fixed
  namespace/name rule;
- the selected authentic match is provider `2499719`, canonical match
  `bad97950-6fac-5cf0-a93c-094f91abbb9b`;
- the accepted completion index is bound to source manifest
  `4e16bdb5-afe7-5601-88ad-adc124cfce3b`, England member digest
  `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`,
  and exact `1H=901`/`2H=867` populations with their retained ordered membership
  digests;
- the implemented schema-bundle v2 retains exactly 23 ordered roots, precedes the
  product-contract v2 value, and both precede the projection without placeholders
  or own-digest fields;
- the invocation and boundary receipt surfaces retain exactly nine and 15 keys;
- the projection retains exactly 25 keys and one canonical SHA-256, and the
  post-hash invocation copies the same 24 authority values and inserts only
  `build_id`; and
- the conservative R21 scope remains exactly four supported count features,
  integer-only event/subevent mapping, no Boolean-as-integer, and no coercion of
  strings or quarantined values.

The exact source-completion reader remains content-addressed and must re-establish
source binding, canonical order, uniqueness, whole-population equality and aggregate
row-count reconciliation. R4 adds no feature, provider access, dependency, schema
root, projection key, product field or external action.

## 7. Exact user decision surface

R20 requires a five-key layer summary but, before R4, no accepted bytes supplied a
deterministic layer-level semantic derivation. R21 is intentionally descriptor-only
and product-forbidden. R4 is therefore the smallest additive authority decision;
there is no accepted-byte-only implementation route around the user decision.

The exact sufficient question that may now be presented is R4 Section 7:

> Do you authorize the master to freeze and independently review the bounded additive
> W04 build/product authority in `wyscout-build-receipt-closure-audit-R4.md`: the exact
> one-match window `[2017-08-11T00:00:00Z, 2017-08-12T00:00:00Z)`, selected-match
> snapshot `2017-08-11T18:45:00Z`, strict cutoff `2026-08-01T00:00:00Z`, accepted
> completion-index and exact five-key UUID bindings; complete 23-root acyclic v2
> aggregates; unchanged receipt schemas and clocks; exact Gold-manifest-derived
> one-product/one-boundary population and product/boundary readback; and the sole
> two-key complete-`LayerManifest` semantic derivation reproduced for all Bronze/
> Silver/Gold R20 summaries with exact parent-summary reconciliation and
> substitution rejection—while preserving every R20/R21/v1/index/R2/R3 byte, the
> exact 25-key one-hash build, conservative four-feature POC scope, and local-only
> boundary?

An affirmative answer authorizes only the bounded master authority freeze and its
independent review chain. It does not itself authorize a product byte, second
semantic derivation, schema omission, manifest-field change, broader population,
provider action or publication before every downstream implementation and gate has
passed.

## 8. Verification and scope

- Read `AGENTS.md`, the R4 packet, and every packet `read_first` artifact
  completely: all 4,516 R20 lines, all 1,254 R21 lines, all 3,256 implemented
  contract lines, R3 audit/review/return, R4 producer return and the return
  template.
- Reproduced every packet-fixed SHA-256 and the exact physical completion-index
  content address with `shasum -a 256`.
- Read the incorporated R2 audit and independent review and re-executed its window,
  UUID, completion-index, 23-root, receipt, aggregate, clock and 25-key reasoning.
- Statically enumerated the complete implemented `LayerManifest`, entry and parent
  fields and traced every summary, product, manifest, boundary and child edge.
- Applied isolated/copy/swap/downstream-rehash summary attacks and omission,
  addition, duplication, reorder, stale, cross-scope and out-of-interval population
  attacks.
- Used no Python helper. A read-only shell preflight recorded 80 repository and
  1,086 site-package pyc files with aggregate inventory digest
  `49d001c3d26c3491761d0519cec5c34b89b22224142bce3b11867e618eed41ef`;
  a postflight equality check is recorded in the return.

No implementation, test mutation, data/authority/product/manifest/receipt write,
provider access, network, cloud, container, CI, remote, endpoint, deployment or Git
operation was performed. Only this review and its bounded return were created.

## 9. Final independent decision

`PASS_TO_USER_QUESTION — P0=0, P1=0, P2=0`

R4's exact complete-manifest semantic derivation, all-three-summary reproduction
and parent reconciliation close the R3 semantic-substitution defect without
creating a cycle or changing the accepted product boundary. Its Section 7 question
is exact and sufficient for the bounded user authority decision.
