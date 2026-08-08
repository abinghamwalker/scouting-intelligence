# W04 build/receipt closure audit independent review R2

Date: 2026-08-01  
Reviewer role: fresh independent W04 build/receipt R2 authority reviewer  
Reviewed artifact: `reports/reviews/W04/wyscout-build-receipt-closure-audit-R2.md`  
Task: `W04-BUILD-RECEIPT-CLOSURE-AUDIT-REVIEW-01-R2`

## Verdict

`REWORK`

- P0: `0`
- P1: `1`
- P2: `0`

The corrected R2 decision surface closes the R1 window, temporal, schema-roster,
aggregate-preimage and receipt-clock findings. It does not yet close the exact
population of temporal-boundary receipts summarized by the rebuild invocation
receipt. Section 6.1 states fail-closed omission/addition/cross-Gold rules, but no
authoritative expected Gold population is read and compared with the submitted
`boundary_receipts` array. The empty array therefore passes every specified
per-receipt readback rule vacuously while `result_state=COMPLETE` remains possible.

The Section 10 authorization question is consequently not sufficient in its current
form and must not be presented as accepted authority. The defect is additive and
bounded to receipt-population closure; it does not require an R20/R21 rewrite, a new
projection key, a new feature, or a product/architecture change.

## 1. Fixed-byte admission

All packet-fixed hashes were reproduced before substantive analysis:

| Artifact | Reproduced SHA-256 | Result |
|---|---|---|
| R2 producer audit | `77cf8dcb79d202b960553dfd6da631af039e5ec0a382a0e7c30be770045d0491` | exact |
| R2 producer return | `71594f261beb772943b249b765144e3f929999789ef0fb6be5667fff08b24999` | exact |
| R1 independent review | `b3c6009cf3ad826bddabfbd6b722f89dcbffb11bf7755bbe60d4df68b67c9a09` | exact |
| R20 authority | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | exact |
| R21 authority | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | exact |
| accepted completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | exact |

No drift stop condition was triggered.

## 2. Independently reproduced accepted surfaces

### 2.1 Source, selected match and temporal boundary

The accepted source/completion evidence reproduces:

- source-manifest ID
  `4e16bdb5-afe7-5601-88ad-adc124cfce3b`;
- source-manifest digest
  `8fb6d539e3e2c9133d84efec5604672611d54df58c3bd06802681cc41cfd89bd`;
- source-completion manifest digest
  `69b8b357cc20b504cf7730b4efcb4a714ec57b6a6bde29cc18dfd0cfe30a3cb1`;
- England source member `archive-members/events_England.json`, digest
  `30159903f519eb8f7b439b91cd3149525191622c720bf917784026627b3defad`,
  row count `643150`;
- accepted aggregate source row count `3071395`;
- exactly one England match in
  `[2017-08-11T00:00:00Z, 2017-08-12T00:00:00Z)`: provider match `2499719`,
  start `2017-08-11T18:45:00Z`, competition `364`, season `181150`, teams
  `1609` and `1631`;
- authorized periods for match `2499719`: `1H` count `901`, membership digest
  `473174e3563098654b41cf580088e4347863643ae2965766f4bcaf3ab507b91b`,
  and `2H` count `867`, membership digest
  `b9b2ef12e43421f5e17236ef3a6cbfd12b3703b71fa7602e48d7e9c4fcf8c16`.

The selected-match snapshot is the retained R4/R5 maximum-selected-match-start
value `2017-08-11T18:45:00Z`, not the later acquisition clock. The retained
valid-from rule remains the maximum of snapshot and dependency watermark. The
source acquisition clock `2026-07-29T15:51:08.598589Z` and the latest currently
bound dependency/authority clock, identity acceptance
`2026-07-31T14:15:26Z`, are both strictly before the candidate cutoff
`2026-08-01T00:00:00Z`.

### 2.2 Five-key window identity

The exact no-terminal-LF canonical JSON bytes were independently reconstructed as:

```json
{"match_id":"bad97950-6fac-5cf0-a93c-094f91abbb9b","source_manifest_id":"4e16bdb5-afe7-5601-88ad-adc124cfce3b","window_end_utc":"2017-08-12T00:00:00Z","window_schema_version":"w04-single-match-poc-window-v1","window_start_utc":"2017-08-11T00:00:00Z"}
```

The preimage is exactly `250` UTF-8 bytes. Its SHA-256 is
`3582348bc62d5624162078802a0495edd2a3206856cdf532322d1233bc33b327`.
The UUIDv5 input is exactly:

```text
namespace = 94552497-0365-5758-a7b5-4d11f1b88e1e
name = single-match-poc:3582348bc62d5624162078802a0495edd2a3206856cdf532322d1233bc33b327
```

It derives window ID `a0af8d56-e41d-5467-b46e-82887c4861e0`. No alternate
encoding, extra field, terminal LF, or invented completion-index identity is needed.

### 2.3 Closed schema roster and dependency order

The R2 `required_root_roles` array contains exactly `23` roots:

- 3 Bronze roots;
- 8 Silver roots;
- 1 Gold root;
- 1 layer-manifest root;
- 2 receipt roots; and
- 8 R20 result/nested-result roots.

The eight result roles are `ENTRYPOINT_SOURCE_RESULT`, `COMPONENT_PROOF_RESULT`,
`PRE_BUILD_ADMISSION_RESULT`, `REBUILD_RECEIPT_SUMMARY`,
`LAYER_MANIFEST_SUMMARY`, `FINAL_RECHECK_RESULT`,
`POST_BUILD_ID_REBUILD_RESULT`, and `CHILD_RESULT_ENVELOPE`. This is exact coverage
of the externally serialized R20 product, layer-manifest, result and receipt roots
within the stated aggregate boundary. The receipt boundary precedes the invocation
receipt that consumes it; nested result roots precede the enclosing result envelope.
Requiring complete transitive canonical schema content prevents a descriptor-only
row from substituting for absent implemented schema bytes.

### 2.4 Aggregate and projection acyclicity

The schema-bundle v2 preimage contains exactly its stated eight keys. It excludes
its own digest, later product identity, projection/build/output values and receipt
instances. The product-contract v2 preimage contains exactly its stated ten keys,
binds the accepted completion index and completed schema-bundle preimage, and also
excludes its own digest. Neither preimage uses a placeholder as an accepted digest.

The resulting direction is acyclic:

```text
R20/R21 + v1 descriptor authority
  -> implemented schema bundle v2
  -> product contract v2
  -> unchanged R20 projection/invocation
  -> products and layer manifests
  -> boundary receipt(s)
  -> invocation receipt
  -> child result
```

The unchanged R20 projection remains exactly `25` keys and uses one SHA-256 over
its canonical preimage. The accepted index and schema closure are bound through
existing aggregate fields. R2 does not add a 26th key.

## 3. P1 finding: invocation receipt has no authoritative boundary population

### 3.1 Executable counterexample

Section 6.1 defines `boundary_receipts` as a sorted unique array whose rows each
contain exactly four keys. It then requires the writer to reopen and verify every
summarized boundary receipt. Those requirements quantify only over rows supplied in
the array; they do not define an exact required cardinality or derive the expected
set from an authoritative Gold manifest/product population.

Consequently this submitted value satisfies all array-shape, sorting, uniqueness
and per-row readback rules as written:

```json
"boundary_receipts": []
```

There is no summarized row to reopen, no row whose Gold path can mismatch, and no
`checked_at` value to test against `started_at <= checked_at <= completed_at`.
`result_state` can still be `COMPLETE`; `layer_manifests` can still name the Gold
layer manifest. At least the required one-row Gold product can therefore have its
boundary receipt omitted without a specified predicate failing.

The same missing expected-set comparison prevents the prose claims for
`additional` and `cross-Gold` boundary rows from being executed reliably: every
submitted row can be internally well-formed, correctly hashed and within the clock
interval, yet not be a member of the exact accepted Gold product set for this
invocation. The boundary contract's fixed `row_count=1` constrains an individual
receipt; it does not establish equality between invocation summaries and the Gold
manifest population.

This violates the review requirement to reject stale, omitted, extra and cross-Gold
bytes. It is P1 because a `COMPLETE` invocation receipt can attest to a publication
whose mandatory temporal-boundary evidence is incomplete.

### 3.2 Bounded R3 correction required

Preserve every R20/R21/v1/index byte and every accepted R2 rule not implicated by
this finding. Add one fail-closed population-closure rule to the receipt authority:

1. The invocation writer must guard-read the complete physical bytes of the exact
   accepted `GOLD` layer manifest named by the exact R20 Gold layer-manifest summary.
2. It must reproduce the manifest physical digest and size and validate the closed
   schema, enclosing build/run/layer/parent chain before using its product entries.
3. It must derive the authoritative expected set of Gold product relative paths
   from that guarded manifest. For this bounded POC the expected set has exactly one
   Gold product.
4. It must require exact set equality between that expected set and
   `boundary_receipts[*].gold_relative_path`, in canonical path order, before any
   invocation receipt is written.
5. Each expected Gold product must be guard-read and checked against the manifest's
   path, physical digest and size, semantic digest, row count and temporal proof
   before its boundary receipt is accepted. If this check remains the boundary
   writer's responsibility, the invocation writer must still re-establish exact
   manifest-population equality and perform the already specified complete boundary
   readback.
6. Missing, additional, duplicate, reordered, cross-Gold, stale, path-mismatched,
   hash-mismatched or size-mismatched population bytes must fail before serialization.
   Retain `started_at <= boundary.checked_at <= completed_at` for every member of the
   now-closed expected set.

This makes the stated failures executable without adding a receipt self-hash, a
projection key, a new aggregate field, a product feature, a dependency or an
external action. A fresh independent review must reproduce the corrected predicate.

## 4. Decision surface

No narrower accepted-byte-only route exists because R20/R21 deliberately do not
freeze these concrete future receipt contents. A bounded user authorization remains
genuinely necessary. However, an affirmative answer to R2 Section 10 would currently
authorize a receipt contract with the P1 omission counterexample above. Therefore:

- `PASS_TO_USER_QUESTION` is not available;
- the current Section 10 question must not be dispatched as accepted authority;
- return only the receipt-population closure defect for bounded R3 correction; and
- after correction, obtain fresh independent review before user dispatch or any
  authoritative build/receipt implementation.

## 5. Verification performed

- Read every packet `read_first` artifact completely, including all `4516` R20
  lines, all `1254` R21 lines and all `3256` contract-source lines.
- Reproduced every packet-fixed SHA-256 with `shasum -a 256`.
- Extracted and cross-checked the accepted completion-index source/member/match/
  period bindings and aggregate row count.
- Recomputed the half-open match selection from the frozen raw source and confirmed
  exact cardinality one.
- Reproduced the retained R4/R5 snapshot/cutoff comparison against the current
  source, dependency and accepted-authority clocks.
- Reconstructed the five-key canonical bytes, byte length, SHA-256 name input and
  UUIDv5 result in a bytecode-disabled, locked/no-sync Python 3.12 process.
- Enumerated every R20 externally serialized product/manifest/result/receipt root
  against R2's exact `23`-role roster and checked dependency-before-consumer order.
- Traced both aggregate preimages and the post-hash projection for self, sibling,
  forward and 26th-key cycles.
- Applied omission, addition, cross-Gold and clock-order adversarial reasoning to
  both receipt contracts.

No product test, repository gate, implementation, data write, authority write,
product/manifest/receipt creation, provider access, network, cloud, container, CI,
remote, endpoint, deployment or Git operation was performed. Review outputs are the
only changed files.

## 6. Final independent decision

`REWORK — P0=0, P1=1, P2=0`

R2 is exact and acyclic on the selected-match/window identity, completion-index
binding, 23-root schema closure, v2 aggregate dependency graph, unchanged 25-key
build identity and receipt clocks. It fails one critical completeness property:
the invocation receipt does not prove exact equality between the accepted Gold
manifest population and its summarized temporal-boundary receipts. Apply only the
bounded Section 3.2 correction and return it for fresh review.
