# W04 build/receipt closure audit independent review R3

Date: 2026-08-01  
Reviewer role: fresh independent W04 build/receipt R3 population reviewer  
Reviewed artifact: `reports/reviews/W04/wyscout-build-receipt-closure-audit-R3.md`  
Task: `W04-BUILD-RECEIPT-CLOSURE-AUDIT-REVIEW-01-R3`

## Verdict

`REWORK`

- P0: `0`
- P1: `1`
- P2: `0`

R3 closes R2's boundary-population omission: the exact guard-read Gold manifest is
now the sole population root, its accepted entry sequence has cardinality one, and
exact sequence/set equality forces exactly one matching boundary receipt before
`COMPLETE`. The parent-manifest graph, Gold-product readback, boundary readback and
clock ordering are otherwise coherent and acyclic.

One P1 executable binding remains open. The unchanged R20 five-key Gold layer
summary contains `semantic_sha256`, but the implemented `LayerManifest` has no
top-level layer semantic digest and R3 supplies no deterministic derivation from
its implemented fields. R3 guard-reads and reconciles the summary's path, physical
digest and size, then reconciles entry-level product semantic digests; it never
reproduces the summary's distinct layer-level `semantic_sha256`. A caller can
therefore replace that one summary value, recompute downstream summary-array
digests, and still satisfy every R3 manifest-population, product and boundary
predicate. Section 8 is not yet an exact sufficient authority question.

## 1. Fixed-byte admission

All packet-fixed bindings were reproduced before substantive analysis:

| Artifact | Reproduced SHA-256 | Result |
|---|---|---|
| R3 producer audit | `0cf86df75af1276b3703083d3137de9ef345e2125a08a4e819617bbfd6100435` | exact |
| R3 producer return | `14bb7cc5cdd9c146707d5ccdceb700170a5f5f761c3387f66b0304d548fddba0` | exact |
| R2 producer audit | `77cf8dcb79d202b960553dfd6da631af039e5ec0a382a0e7c30be770045d0491` | exact |
| R2 independent review | `b67e4f95e97567b60d93bab58e94bad877931b2259f219709b199d7325634658` | exact |
| R20 authority | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | exact |
| R21 authority | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | exact |
| accepted source-completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | exact |

No drift stop condition was triggered. The R3 source-manifest and England-member
digests were also reproduced exactly as
`8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`
and
`301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`.
Those exact values supersede the visibly mistyped abbreviated values in historical
R2 review prose, as R3 Section 2 expressly requires.

## 2. Independently reproduced passing R3 closure

### 2.1 Gold summary selection and manifest population

R3 begins with the exact R20 three-row `layer_manifests` array and selects its
third and only `layer=GOLD` row. The Gold path is deterministically derived from the
enclosing build ID; guard-reading that exact named path before entry inspection
prevents directory discovery, newest-file choice, alternate-path substitution and
symlink recovery. Physical SHA-256, byte size, closed manifest schema, layer,
build, source manifest, completion index, tenant, rights, source/authority clocks,
feature schema and dependency lineage are all required before population
derivation. The manifest has no `run_id`; R3 correctly does not invent one.

The implemented `LayerManifest` exposes the exact fields needed to derive
`expected_gold_paths`: `layer`, `build_id`, `manifest_path`, `entries`, entry
`path.path_role`, entry `path.relative_path`, entry completion and the closed
validator requiring unique lexically ordered paths all exist. The contract rejects
non-Gold entries in a Gold manifest. R3 then requires exactly one entry, one unique
path and exactly one boundary summary whose Gold-path tuple equals that one-item
manifest tuple. This makes the following population attacks fail before receipt
serialization:

| Attack | Failing R3 predicate |
|---|---|
| empty or omitted boundary array | `len(boundary_receipts)=1` and tuple equality |
| additional or cross-Gold row | exact one-item cardinality and manifest-path equality |
| duplicate row | exact cardinality plus unique one-item population |
| reordered population | exact sequence equality; no sort or repair is permitted |
| stale Gold manifest | summary physical digest/size and complete guard-read bytes |
| cross-layer entry | closed `LayerManifest` layer/role validation |
| cross-build product | manifest/build/path/partition equality |
| wrong product path | exact manifest-derived Gold path equality |

With cardinality one, a nontrivial two-item reorder cannot occur in this POC, but
the specified sequence equality remains the correct fail-closed rule and does not
broaden the population.

### 2.2 Parent graph and product/boundary readback

The implemented parent surfaces support the R3 graph without an invented run ID or
absent parent field. `parent_layer_manifests` supplies layer, build, exact path and
physical digest. `ordered_parent_paths` supplies ordered unique product paths.
Guard-reading Gold's exact Silver parent and Silver's exact Bronze parent, then
requiring same-build layer/source/index/tenant/rights/authority/feature/lineage
equality and exact path resolution in the corresponding manifest entries closes
missing, duplicate, reordered, cross-layer and cross-build parent references.
Bronze's empty parent tuple terminates the graph.

For the sole Gold entry, R3 requires complete product guard-read and exact path,
role, build/partition, physical digest, size, accepted serializer/schema, row count,
entry-level semantic digest, parent paths, rights, window, snapshot, cutoff,
feature schema, completion index, lineage, applicability and temporal-proof
reconciliation. The boundary readback then binds its path hash, complete physical
bytes, schema, build/run, exact Gold manifest physical identity, Gold product
physical and semantic identities, row count, lineage, cutoff and temporal proof.
The retained
`started_at <= checked_at <= completed_at` predicate closes cross-receipt clock
order. Missing, stale, malformed, cross-run and caller-substituted product or
boundary evidence consequently fails.

### 2.3 Incorporated R2 authority and acyclicity

The incorporated R2 surface remains internally consistent:

- the half-open window is exactly
  `[2017-08-11T00:00:00Z, 2017-08-12T00:00:00Z)`;
- selected-match snapshot is exactly `2017-08-11T18:45:00Z`, cutoff is exactly
  `2026-08-01T00:00:00Z`, and valid-from remains the maximum of snapshot and
  dependency watermark;
- the five-key no-terminal-LF window object, SHA-256 name input and UUIDv5 rule
  remain unchanged;
- the accepted completion-index content address and exact `901`/`867` period
  populations remain bound;
- the implemented-schema roster contains exactly 23 ordered roots;
- the schema-bundle v2 preimage precedes the product-contract v2 preimage, both
  precede the unchanged 25-key projection, and neither contains its own digest;
- the exact nine-key invocation and 15-key boundary receipt surfaces remain
  unchanged; and
- R3 only adds backward readback predicates to
  `product -> manifest -> boundary -> invocation -> child`, so it introduces no
  content-address cycle or unauthorized feature/product rule.

## 3. P1 finding: layer-summary semantic digest is caller-substitutable

### 3.1 Exact implemented-field contradiction

The R20 five-key layer summary has:

```text
layer
manifest_relative_path
manifest_sha256
manifest_size_bytes
semantic_sha256
```

R3 Section 3 says the final value is the accepted Gold-layer semantic digest, but
the implemented `LayerManifest` fields are exactly:

```text
manifest_schema_version
construction_authority_state
layer
build_id
manifest_path
source_manifest_id
source_manifest_sha256
source_completion_index_sha256
tenant_context
classification
source_available_at
source_acquired_at
authority_clocks
feature_schema_hash
dependency_lineage_hash
dependency_lineage
entries
parent_layer_manifests
complete
```

There is no top-level `semantic_sha256`. Each `LayerManifestEntry` has an
entry-level `semantic_sha256`, but neither R20 nor R3 defines a canonical formula
that converts the complete ordered manifest/entry/parent semantics into the
distinct layer-summary value. An entry digest cannot silently be relabelled as a
layer digest, especially where non-Gold manifests may contain multiple entries.

### 3.2 Executable substitution

Starting from otherwise valid evidence:

1. keep the Gold summary's layer, exact manifest path, physical digest and physical
   size unchanged;
2. replace only its `semantic_sha256` with a different canonical 64-lowercase-hex
   value;
3. keep the complete Gold, Silver and Bronze manifests, every product and every
   boundary receipt byte unchanged; and
4. recompute only later operational containers that hash the submitted
   `layer_manifests` array, such as `layer_manifest_set_sha256` and the physical
   invocation-receipt digest.

R3's guard read still selects and validates the same manifest. The same one Gold
path is derived. Product readback still equals the manifest entry's semantic
digest. Boundary readback still equals that product and the Gold manifest's
physical digest. No R3 predicate compares the altered layer-summary semantic value
with a value reproduced from manifest bytes. `result_state="COMPLETE"` therefore
remains reachable with a false R20 summary claim.

This is P1 because the invocation receipt's complete three-layer summary surface
can contain caller-substituted semantic authority while all population and
readback gates report success.

### 3.3 Bounded R4 correction required

Preserve every R20/R21/v1/index/R2/R3 byte and every passing R3 population rule.
Add only one executable layer-summary semantic binding:

1. define a byte-exact acyclic `layer_semantic_sha256` derivation over explicitly
   named existing implemented `LayerManifest` semantic fields, with exact object
   keys, inclusion/exclusion rules, array order, R20 canonical encoding and no
   self-digest; **or** separately authorize an additive closed manifest field and
   its schema change;
2. require the writer to recompute that value independently from each complete
   guard-read Bronze, Silver and Gold manifest and compare it to the corresponding
   exact R20 summary row before population derivation;
3. require the Gold and Silver parent-manifest path/physical identity to reconcile
   to the corresponding Silver and Bronze R20 summary rows, so all three summary
   rows and the parent chain name one identical manifest population; and
4. add adversarial tests that alter only each summary `semantic_sha256`, including a
   value copied from an entry or another layer, while recomputing every downstream
   wrapper digest; all must fail before `COMPLETE`.

The smallest correction can use existing manifest fields and does not inherently
require a new projection key, feature, product path, dependency, provider, rights,
architecture or local-only change. A fresh independent review must adjudicate its
exact byte formula; this reviewer does not choose product authority.

## 4. Decision surface

No accepted-byte-only route supplies the missing layer-semantic derivation: R20
requires the five-key summary but does not materialize the value in the implemented
manifest, and R21 deliberately remains descriptor-only/product-forbidden. The
current R3 Section 8 question would authorize a `COMPLETE` receipt with the
substitution above. Therefore:

- `PASS_TO_USER_QUESTION` is unavailable;
- R3 Section 8 must not be dispatched as accepted authority;
- only the bounded layer-summary semantic correction in Section 3.3 should be
  returned; and
- product/build/receipt implementation remains blocked pending fresh review.

## 5. Verification performed

- Read AGENTS, the R3 packet and every `read_first` artifact completely, including
  all 4,516 R20 lines, all 1,254 R21 lines and all 3,256 implemented contract lines.
- Reproduced every packet-fixed SHA-256 and the exact source-manifest/member
  digests with `shasum -a 256`.
- Statically enumerated the exact implemented `LayerManifest`,
  `LayerManifestEntry`, `ParentLayerManifest`, Gold product and temporal-proof
  fields and validators.
- Traced the exact R20 three-row/five-key summaries, parent-manifest references,
  product parents, manifest population, Gold product and receipt equality edges.
- Applied empty, missing, additional, duplicate, reordered, stale, cross-layer,
  cross-build/run/Gold, wrong-product, product-digest/size/semantic/row-count,
  boundary path/hash/size/schema/clock, and layer-summary-semantic substitution
  attacks.
- Rechecked the incorporated R2 window, UUID, index, roster, aggregate, receipt and
  unchanged 25-key one-hash surfaces for direction and cycle closure.

No Python helper, product test, repository gate, implementation, data write,
authority write, product/manifest/receipt creation, provider access, network,
cloud, container, CI, remote, endpoint, deployment or Git operation was performed.
Only this review and its bounded return were created.

## 6. Final independent decision

`REWORK — P0=0, P1=1, P2=0`

R3 successfully closes exact manifest-derived one-product/one-boundary population
equality and preserves the complete acyclic R2 authority surface. It does not yet
bind the R20 layer summary's `semantic_sha256` to any reproducible value in the
guard-read implemented manifest. Apply only the bounded correction above and
obtain a fresh independent review before asking for user authority.
