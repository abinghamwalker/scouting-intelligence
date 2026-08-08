# W04 build-contract R2 frozen-authority audit return R1

## Task

- task_id: `W04-BUILD-CONTRACT-R2-AUTHORITY-AUDIT-01-R1`
- objective: independently determine the exact already-authorized R20/R4 contract
  needed to close the R2 v15 admission proof and three-manifest receipt composition,
  without inspecting, editing, or approving the producer candidate.
- verdict: **PASS_TO_IMPLEMENT**
- review boundary: this is a frozen-authority interpretation, not candidate review,
  implementation acceptance, or permission to publish product bytes.

## Files changed

- `reports/reviews/W04/returns/W04-BUILD-CONTRACT-R2-AUTHORITY-AUDIT-01-R1.md`

## Summary

The fixed R20, R4, accepted build/product authority, post-authority audits, and R2
producer packet unambiguously close the bounded correction. No architecture,
schema-root, product-population, dependency, provider, network, or local-only change
is required.

### 1. Exact v15 decoded stable manifest

The object decoded from
`result.canonical_manifest_bytes_b64u` is one closed canonical JSON object with
exactly 23 top-level fields and no wrapper around the component values:

```text
child_result_contract_digest
editable_root_digest
environment_digest
environment_values_digest
executable_census_digest
extracted_runtime_digest
installed_record_runtime_digest
interpreter_digest
local_launcher_control_digest
local_resource_digest
lock_inputs_digest
process_launch_contract_digest
pyc_policy_source_map_digest
repository_code_sha256
schema_version
selected_lock_closure_digest
selector
selector_bootstrap_digest
stdlib_digest
uv_physical_sha256
uv_version
venv_bootstrap_digest
wheel_declaration_digest
```

This top-level location follows directly from the combined accepted clauses:

1. R20 requires the decoded manifest's exact value at every `component_key` to be
   hashed for the corresponding proof;
2. it states that the fixed `COMPONENT_KEYS` are exactly the twenty keys of the
   decoded manifest environment-component object;
3. it separately requires decoded-manifest fields `schema_version`,
   `repository_code_sha256`, and `environment_digest`; and
4. the R2 packet closes the manifest environment component as exactly the twenty
   `COMPONENT_KEYS` values and rejects additional data.

Consequently, `environment_components`, `components`, or any other nested wrapper
would be an unauthorized 24th field and would also make `manifest[component_key]`
unavailable. The exact twenty-key environment-component object is an in-memory
projection of those twenty top-level values:

```text
C = {
  "selector": M["selector"],
  "selector_bootstrap_digest": M["selector_bootstrap_digest"],
  "lock_inputs_digest": M["lock_inputs_digest"],
  "editable_root_digest": M["editable_root_digest"],
  "venv_bootstrap_digest": M["venv_bootstrap_digest"],
  "selected_lock_closure_digest": M["selected_lock_closure_digest"],
  "wheel_declaration_digest": M["wheel_declaration_digest"],
  "extracted_runtime_digest": M["extracted_runtime_digest"],
  "installed_record_runtime_digest": M["installed_record_runtime_digest"],
  "executable_census_digest": M["executable_census_digest"],
  "pyc_policy_source_map_digest": M["pyc_policy_source_map_digest"],
  "uv_version": M["uv_version"],
  "uv_physical_sha256": M["uv_physical_sha256"],
  "local_launcher_control_digest": M["local_launcher_control_digest"],
  "process_launch_contract_digest": M["process_launch_contract_digest"],
  "child_result_contract_digest": M["child_result_contract_digest"],
  "interpreter_digest": M["interpreter_digest"],
  "stdlib_digest": M["stdlib_digest"],
  "local_resource_digest": M["local_resource_digest"],
  "environment_values_digest": M["environment_values_digest"]
}
```

`C` is encoded with the R20 canonical JSON algorithm, so serialized object-key
order is Unicode code-point order even though the authority formula presents the
fields in semantic construction order. `selector` is the exact frozen closed
selector object, `uv_version` is the exact canonical string, and the other eighteen
values are lowercase SHA-256 strings.

The admitted object may be represented by an internal/helper validation model. It
must not be exported as a ninth result role or a 24th schema-bundle root. The only
relevant accepted result roots remain `COMPONENT_PROOF_RESULT` and
`PRE_BUILD_ADMISSION_RESULT`; the stable manifest is the decoded value carried by
the latter. No `CODE_ENVIRONMENT_MANIFEST`, environment-component, aggregate, or
helper root is added to the fixed 23-root roster.

R20 is therefore unambiguous enough to implement the R2 correction without a new
architecture decision.

### 2. Exact executable admission equalities

Let:

- `B` be the strict base64url-decoded manifest bytes;
- `M` be the canonical parse of `B`;
- `K` be the following fixed proof order;
- `C` be the exact twenty-key projection above; and
- `N[k]` be an independently recounted stable-evidence row count for component
  `k`, supplied through a pure validation seam rather than copied from a proof.

The fixed proof order `K` is:

```text
child_result_contract_digest
editable_root_digest
environment_values_digest
executable_census_digest
extracted_runtime_digest
installed_record_runtime_digest
interpreter_digest
local_launcher_control_digest
local_resource_digest
lock_inputs_digest
process_launch_contract_digest
pyc_policy_source_map_digest
selected_lock_closure_digest
selector
selector_bootstrap_digest
stdlib_digest
uv_physical_sha256
uv_version
venv_bootstrap_digest
wheel_declaration_digest
```

Admission succeeds only if all of these equalities and predicates hold:

```text
B == R20_canonical_json(M)
set(M.keys()) == set(K) union {
  "schema_version", "repository_code_sha256", "environment_digest"
}
len(M) == 23

M["schema_version"]
  == result["manifest_schema_version"]
  == "w04-code-environment-admission-v15"

M["repository_code_sha256"]
  == result["repository_code_sha256"]
  == child_result["expected_repository_code_sha256"]

derived_environment_digest = SHA256(R20_canonical_json(C))
M["environment_digest"]
  == result["environment_digest"]
  == derived_environment_digest

result["canonical_manifest_sha256"] == SHA256(B)
```

The component-proof array must contain exactly twenty closed three-key rows, with
no omission, addition, duplication, null, or reordering. For every zero-based index
`i` and `k = K[i]`:

```text
proofs[i]["component_key"] == k
proofs[i]["value_json_sha256"]
  == SHA256(R20_canonical_json(M[k]))
proofs[i]["evidence_row_count"] == N[k]
1 <= N[k] <= 10_000_000
```

The independently supplied `N` seam itself must be closed to exactly the keys in
`K`, with each value a strict JSON/Python integer in the admitted range. It cannot
take a caller Boolean, reuse the row's claimed count, infer count from the component
digest, or treat exact component-value equality as evidence of source-row
cardinality. If the evidence producer naturally returns an ordered tuple, it must
be in `K` order; if it returns a mapping, the validator must project it into `K`
order only after rejecting missing or additional keys.

Finally:

```text
result["component_proofs_sha256"]
  == SHA256(R20_canonical_json(proofs))
```

Canonical byte reserialization rejects key reordering or noncanonical encoding.
The value hashes are independently recomputed from `M`, the environment hash from
`C`, the proof-array hash from the complete checked proof rows, and the evidence
counts from the separate recount seam. Rehashing a downstream result or child
envelope cannot cure any earlier mismatch.

### 3. Minimal pure all-three-manifest composition contract

The minimal side-effect-free receipt-closure input consists of:

1. the enclosing accepted build/invocation and frozen authority values;
2. the exact three closed five-key summary rows in order `BRONZE`, `SILVER`,
   `GOLD`;
3. for each layer, its complete physical manifest byte stream and the corresponding
   complete parsed object that has already passed the accepted closed v2
   `LAYER_MANIFEST` schema validator; and
4. the one boundary summary/receipt population submitted for final equality.

It need not implement a second LayerManifest schema. A strongly typed or explicitly
attested prevalidated object may establish only closed-schema shape, JSON types,
required/nullability rules, and nested structural validity. Composition must still
repeat every identity equality that binds that object to these bytes, this summary,
this build, and these authorities.

For each layer in exact `BRONZE`, `SILVER`, `GOLD` order, composition must:

1. require the summary to have exactly `layer`, `manifest_relative_path`,
   `manifest_sha256`, `manifest_size_bytes`, and `semantic_sha256`;
2. derive `data/manifests/wyscout/v5/<lower-layer>/<build_id>.manifest.json` and
   require exact equality with `manifest_relative_path`;
3. require the supplied bytes to be the complete guard-read bytes for that exact
   path, reproduce their SHA-256 and size, and compare both directly to the same
   summary row;
4. require physical encoding to be R20 canonical JSON plus exactly one terminal LF,
   parse it, and require byte-identical canonical reserialization plus LF;
5. require the parsed physical-byte value to equal the supplied prevalidated
   complete object exactly—every field, nested field, ordered array, and explicit
   null included;
6. repeat exact equalities for layer, build ID, manifest path, `complete`, source
   manifest ID/digest, source-completion-index digest, tenant context,
   classification/rights, source clocks, authority clocks, feature-schema hash,
   dependency-lineage hash/value, and every other enclosing frozen authority
   binding; and
7. derive, without using any supplied semantic digest, the sole R4 semantic value:

```text
semantic_preimage = {
  "layer_manifest": COMPLETE_EXACT_PARSED_OBJECT,
  "semantic_schema_version": "w04-wyscout-layer-manifest-semantic-v1"
}
derived_semantic_sha256 = SHA256(R20_canonical_json(semantic_preimage))
```

The semantic preimage has exactly those two keys, uses no terminal LF, and includes
the whole accepted manifest object. `derived_semantic_sha256` must equal that
layer's summary `semantic_sha256`. A physical manifest digest, an entry semantic
digest, another layer's digest, a partial projection, or a downstream rehash is not
equivalent.

Only after all three independent physical and semantic reproductions pass may the
parent chain be checked:

```text
Bronze.parent_layer_manifests == []

Silver.parent_layer_manifests == [
  {
    "layer": Bronze_summary.layer,
    "build_id": enclosing_build_id,
    "relative_path": Bronze_summary.manifest_relative_path,
    "sha256": Bronze_summary.manifest_sha256
  }
]

Gold.parent_layer_manifests == [
  {
    "layer": Silver_summary.layer,
    "build_id": enclosing_build_id,
    "relative_path": Silver_summary.manifest_relative_path,
    "sha256": Silver_summary.manifest_sha256
  }
]
```

Each parent row has those four exact fields; no size or semantic field is invented.
The referenced parsed parent manifest must carry the same build ID. Missing,
additional, duplicate, reordered, cross-layer, cross-build, path-substituted, or
physical-digest-substituted parents fail before Gold population selection.

After that parent closure, the accepted Gold manifest must yield exactly one entry,
that entry must have role `GOLD_PLAYER_WINDOW`, and its relative path is the direct
one-element population sequence. No sorting, filtering-away of other entries,
deduplication, fallback, recovery, or caller population witness is accepted. The
one boundary summary and the receipt population must have exact sequence and set
equality with that Gold-manifest-derived path. Product and boundary guard-read
equalities then execute as frozen; only after they pass may the unchanged receipt
claim `result_state="COMPLETE"`.

Thus a previously closed-schema-validated manifest object avoids duplicating the
schema validator, but cannot replace physical byte/object equality, physical
digest/size equality, R4 semantic reproduction, enclosing-authority equality,
parent reconciliation, or Gold-derived boundary-population equality.

### 4. Exact competition identity and population boundary

The sole accepted Gold path is:

```text
data/working/wyscout/v5/gold/build_id=<build>/player-window/competition_id=cb5c5317-fa4a-571e-93dc-ef6ce482eab7/window_definition_id=a0af8d56-e41d-5467-b46e-82887c4861e0/window_start_utc=20170811T000000000000Z/window_end_utc=20170812T000000000000Z/feature_cutoff_ts=20260801T000000000000Z/part-00000.parquet
```

The competition UUID was independently reproduced from R20's accepted identity
algorithm:

```text
source_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
  = 89161938-1e8c-53ab-ab52-eba969681833

competition_namespace = UUIDv5(source_namespace, "competition")
  = 66349480-e00f-5748-a5b1-56b210366ae7

UUIDv5(competition_namespace, "figshare-v5:364")
  = cb5c5317-fa4a-571e-93dc-ef6ce482eab7
```

Accepting any other UUID—including a syntactically valid UUIDv5 or the former
`11111111-1111-5111-8111-111111111111` fixture—widens the exact one-product path
and product population and must fail.

## Tests run

- command: `shasum -a 256` over every packet-fixed binding
  - exit status: `0`
  - result: PASS
  - reproduced:
    - R2 packet: `8995671c7591b022c36f755e065c5f12b0bfd9138bf6e1a7d40633c3f678d368`
    - build authority decision: `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d`
    - R4 audit: `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222`
    - R20: `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
    - R21: `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; 25 checks passed, zero failures, zero configured Git remotes,
    and no hosted CI, deployment, container, external-service, or cloud boundary.
- command: bounded `uv run python -c` UUIDv5 reproduction using the frozen R20
  source identity formula and competition source ID `364`
  - exit status: `0`
  - result: PASS; reproduced
    `cb5c5317-fa4a-571e-93dc-ef6ce482eab7`.

## Artifacts/evidence

- `orchestration/task_packets/W04-BUILD-CONTRACT-R2-AUTHORITY-AUDIT-01-R1.yaml`
  (`1fe0f13ca039e7a54a56419ef6354c40e96c7c0b640782d44ffe68e8b1dcbf6c`)
- `orchestration/task_packets/W04-WYSCOUT-BUILD-CONTRACT-01-R2.yaml`
  (`8995671c7591b022c36f755e065c5f12b0bfd9138bf6e1a7d40633c3f678d368`)
- `reports/reviews/W04/wyscout-schema-design-R20.md`
  (`8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`)
- `reports/reviews/W04/wyscout-schema-design-R21.md`
  (`faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`)
- `reports/reviews/W04/wyscout-build-receipt-closure-audit-R4.md`
  (`a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222`)
- `reports/reviews/W04/authorities/wyscout-build-product-authority-decisions-v1.json`
  (`3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d`)

## Risks

- This return does not inspect, test, or approve the evolving R2 producer candidate.
- The separate evidence-count seam is mandatory because stable component values do
  not intrinsically prove their source-evidence cardinalities.
- Treating a prevalidated manifest object as proof of physical-byte identity or
  summary equality would reopen the R1 composition defect; those equalities must be
  repeated as specified above.
- No unresolved frozen-authority contradiction remains within this bounded audit.

## Follow-up items

- Dispatch or continue the existing bounded R2 producer packet using this exact
  contract; then obtain a fresh independent candidate review and master acceptance.
- Do not treat this authority audit as producer-byte approval.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no producer candidate inspection or modification: confirmed
- no product/control/data/run write, provider/network access, cloud, container,
  hosted CI, endpoint, deployment, or publication: confirmed
